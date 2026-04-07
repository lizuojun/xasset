# P1+P2：AI 生成 Pipeline & 基础设施设计

**日期：** 2026-04-07
**状态：** 已确认
**依赖：** P0（资产数据模型）

---

## 产品目标

构建可扩展的 AI 资产生成 Pipeline 框架，支持从文字/图片/概念原画生成 3D 场景资产。

**当前阶段目标：**
1. 搭建 Pipeline 骨架和基础设施（P2）
2. 以 house 场景布局逻辑填充 Stage 2，端到端跑通验证（P1）
3. 支持变体生成（替换模型/材质/配饰/打光）

**设计约束：**
- 接口以最终产品目标为准，ref/ 代码仅作填充验证，不倒逼接口设计
- 所有算法计算结果持久化，后续从 DB/内存取，不重复计算
- Pipeline 只负责计算，不做业务判断（是否创建新资产由 Service 层决定）
- 零外部服务依赖，可在任意机器 `git clone` 后直接运行

---

## 整体分层

```
┌─────────────────────────────────────┐
│  P3 (未来) REST API / Web App       │
├─────────────────────────────────────┤
│  P2  Service 层                     │
│       GenerationService             │  主入口：提交/查询/取结果
│       MeshService                   │  Mesh 空间分析（GLM 封装）
│       SampleSearchService           │  向量相似 Sample 检索
├─────────────────────────────────────┤
│  P2  Storage 抽象层                 │
│       LocalFileStorage（当前）      │
│       OSSStorage（stub，未来）      │
├─────────────────────────────────────┤
│  P1  Pipeline 层                    │
│       Stage Protocol                │
│       StageRegistry                 │
│       Pipeline / PipelineContext    │
│       stages/                       │
│         SceneUnderstandStage (stub) │
│         HouseLayoutComposeStage     │  ← 接 ref/ 布局逻辑
│         StylizeStage (stub)         │
├─────────────────────────────────────┤
│  P2  Job 层                         │
│       Job / JobStatus / JobResult   │  接口为异步语义，内部暂同步
│       InMemoryJobStore              │
├─────────────────────────────────────┤
│  P0  Domain 层（已完成）            │
│       xasset/models / repositories  │
│       xasset/config (GroupDef)      │
└─────────────────────────────────────┘
```

---

## 目录结构

```
xasset/
  pipeline/
    __init__.py
    context.py         # PipelineInput, PipelineContext, VariationInput
    stage.py           # Stage Protocol
    registry.py        # StageRegistry
    pipeline.py        # Pipeline 编排器, PipelineConfig
    stages/
      __init__.py
      scene_understand.py    # stub
      layout_compose.py      # HouseLayoutComposeStage
      stylize.py             # stub
  services/
    __init__.py
    generation.py      # GenerationService
    mesh.py            # MeshService（封装 GLM）
    sample_search.py   # SampleSearchService
  jobs/
    __init__.py
    job.py             # Job, JobStatus, JobResult
    store.py           # InMemoryJobStore
  storage/
    __init__.py
    base.py            # StorageBackend Protocol
    local.py           # LocalFileStorage
```

`ref/` 代码不迁入 `xasset/`，通过内部 adapter 调用，保持可替换性。

---

## 核心数据类型

```python
@dataclass
class PipelineInput:
    input_type: str              # "text" | "image" | "concept_art"
    scene_type: str              # "house" | "urban" | "wild"
    text_description: str | None
    image_url: str | None
    style: str | None
    constraints: dict            # 尺寸、房间类型等约束

@dataclass
class VariationInput:
    replace_models: list[RoleTarget] | None     # 指定替换哪些 role 的模型
    replace_materials: list[AssetTarget] | None
    replace_lights: bool = False
    replace_accessories: bool = False
    style: str | None = None

@dataclass
class PipelineContext:
    job_id: str
    input: PipelineInput
    stage_outputs: dict[str, Any]   # stage_name → output
    status: str                     # "running" | "done" | "failed"
    error: str | None = None

@dataclass
class Job:
    id: str
    status: str                  # "pending" | "running" | "done" | "failed"
    created_at: datetime
    finished_at: datetime | None
    result: dict | None
    error: str | None
```

---

## Pipeline 层

### Stage Protocol

```python
class Stage(Protocol):
    name: str                    # 唯一标识，如 "layout_compose"
    scene_types: list[str]       # 支持的场景类型；["*"] 表示通用

    def run(self, ctx: PipelineContext) -> None:
        """就地写入 ctx.stage_outputs[self.name]，抛出异常表示失败"""
```

### StageRegistry

```python
class StageRegistry:
    def register(self, stage: Stage) -> None: ...
    def get(self, name: str, scene_type: str) -> Stage: ...
    def pipeline_for(self, config: PipelineConfig) -> list[Stage]: ...
```

同一 Stage 名可注册多个实现，按 `scene_type` 分发：

```python
registry.register(HouseLayoutComposeStage())   # scene_types=["house"]
registry.register(UrbanLayoutComposeStage())   # scene_types=["urban"]，未来实现
```

### Pipeline 编排器

```python
@dataclass
class PipelineConfig:
    scene_type: str
    stages: list[str]                          # 要执行的 stage 名，按顺序
    stage_configs: dict[str, dict] = field(default_factory=dict)

class Pipeline:
    def run(self, input: PipelineInput, config: PipelineConfig) -> PipelineContext:
        """顺序执行各 Stage，ctx 在 Stage 间流转；不写 DB，只返回结果"""
```

**Pipeline 不写 DB**，只返回 `PipelineContext`，持久化由 Service 层完成。

### Stage 实现说明

| Stage 名 | 当前实现 | 未来 |
|---|---|---|
| `scene_understand` | stub（返回固定 region 描述） | 接多模态理解模型 |
| `layout_compose` | `HouseLayoutComposeStage`（接 ref/）| 注册 Urban/Wild 实现 |
| `stylize` | stub | 接材质风格化 + 光照生成模型 |

Stage 3（`stylize`）覆盖：材质/风格替换、光照生成、相机视角生成。当前阶段 stub，等资产库完善后填充。

---

## Service 层

### GenerationService

```python
class GenerationService:
    def submit(
        self,
        input: PipelineInput,
        config: PipelineConfig | None = None,
    ) -> str:                              # 返回 job_id，接口为异步语义
        ...

    def submit_variation(
        self,
        source_asset_id: uuid.UUID,
        variation: VariationInput,
    ) -> str:
        """
        精简 Pipeline（只执行受影响的 Stage）生成变体。
        是否创建新 AssetDefinition 由调用方决定，Service 不强制。
        """

    def get_status(self, job_id: str) -> JobStatus: ...
    def get_result(self, job_id: str) -> JobResult: ...
    def cancel(self, job_id: str) -> None: ...
```

当前 `submit()` 内部同步执行完整 Pipeline；接口语义为异步，后续换任务队列只改内部实现。

### MeshService

```python
class MeshService:
    def get_placement_zones(
        self,
        asset_id: uuid.UUID,
        force_recompute: bool = False,
    ) -> PlacementZones:
        """
        查 AssetDefinition.computed_features["placement_zones"]
        命中直接返回；未命中则调用 GLM 算法计算，写入 DB 后返回。
        """
```

`PlacementZones` 包含 top/back/front 三类区域及尺寸约束。GLM 作为实现细节封装在 adapter 内，接口不暴露任何 GLM 概念。

### SampleSearchService

```python
class SampleSearchService:
    def find_by_style(
        self,
        scene_type: str,
        sample_level: str,
        style_vector: list[float],
        limit: int = 10,
    ) -> list[Sample]:
        """内存 LRU 缓存；未命中走 SampleRepository"""

    def find_by_partition(
        self,
        scene_type: str,
        partition_vector: list[float],
        limit: int = 10,
    ) -> list[Sample]:
        ...
```

### Service 层调用关系

```
GenerationService
  └─ Pipeline.run()
       └─ HouseLayoutComposeStage.run()
            ├─ MeshService.get_placement_zones()
            ├─ SampleSearchService.find_by_style()
            └─ GroupDefinition config（xasset/data/groups/）
```

---

## 缓存策略

统一模式：**先查 → 有则返回 → 无则计算 → 写入 → 返回**

| 数据 | 存储位置 | 触发重算条件 |
|---|---|---|
| Mesh PlacementZones | `AssetDefinition.computed_features["placement_zones"]` | `force_recompute=True` |
| 风格/空间向量 | `Sample.style_vector / partition_vector` | 资产更新 |
| 布局结果 | `GroupInstance / Region` 表 | 显式重新生成 |
| 向量检索结果 | 内存 LRU（按 query_key） | 进程重启后失效 |

---

## Storage 抽象层

```python
class StorageBackend(Protocol):
    def put(self, key: str, data: bytes) -> str: ...   # 返回 URL
    def get(self, url: str) -> bytes: ...
    def exists(self, url: str) -> bool: ...
    def delete(self, url: str) -> None: ...
```

- **LocalFileStorage**：写 `xasset/data/storage/`，URL 格式 `local://path`
- **OSSStorage**（stub）：URL 格式 `oss://bucket/path`，替换时上层零改动

Storage URL 写入 `AssetDefinition.raw_data` / `packaged_data`，与 P0 数据模型对接。

---

## Job 层

```python
@dataclass
class JobStatus:
    job_id: str
    status: str      # "pending" | "running" | "done" | "failed"
    progress: float  # 0.0 ~ 1.0
    message: str | None

@dataclass
class JobResult:
    job_id: str
    asset_id: uuid.UUID | None
    stage_outputs: dict[str, Any]
    error: str | None
```

`InMemoryJobStore` 当前实现；后续迁移到 SQLite/Redis 时接口不变。

---

## 扩展性说明

**新增场景类型（urban/wild）：**
只需实现对应 Stage 并注册，Pipeline、Service、Job 层不改动：
```python
registry.register(UrbanLayoutComposeStage())
registry.register(WildLayoutComposeStage())
```

**接入外部 AI 模型：**
替换对应 Stage 实现即可，其他 Stage 和 Service 不受影响。

**切换任务队列（Celery/RQ）：**
只改 `GenerationService.submit()` 内部实现，接口不变。

**切换 OSS：**
实现 `StorageBackend` Protocol，替换 `LocalFileStorage`，上层零改动。

---

## 当前阶段不包含

- HTTP REST API（P3）
- OSS 实际实现（用 LocalFileStorage 替代）
- Stage 1 真实场景理解模型（stub）
- Stage 3 真实材质/光照算法（stub）
- 认证、计费（P4）
