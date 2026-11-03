# Stage 输入输出契约规范

> 状态：设计草案 v1，待评审确认后实施
> 日期：2026-09
> 定位：**契约先定，算法后补**。本规范定义六个 Stage 的输入输出契约（Stage 之间唯一的数据协议），Stage 内部用什么算法、什么流程，是实现阶段的事。
> 关联：
> - `docs/architecture.md` —— 架构总览
> - `docs/architecture.md` —— Artist 范式（理解侧 × 约束侧）

---

## 0. 一句话目标

**六个 Stage 之间的数据交换，只通过本规范定义的 pydantic 契约进行。每个 Stage 声明"我需要哪些上游产物"（`requires`）和"我产出什么"（`output_type`），框架负责按声明注入输入、校验输出。Stage 内部实现（LLM / 视觉算法 / 求解器的具体组合）不进入契约。**

### 0.1 压倒性的设计目标：一套契约描述六类场景

本契约**不是为室内设计的**。目标是用**同一套 schema** 统一描述：

| # | 场景 | 典型区域 | 垂直维度语义 | 轮廓上的开口 | 轮廓上的固定边 |
|---|------|---------|-------------|-------------|--------------|
| 1 | **室内** | 客厅 / 卧室 / 厨房 / 卫生间 | 层高（2.6–3.2 m） | 门 / 窗 / 拱门 | 承重墙 |
| 2 | **城市** | 街道 / 广场 / 建筑基底 / 绿地 | 建筑高度（数米–数百米） | 路口 / 出入口 / 大门 | 用地红线 / 道路红线 |
| 3 | **乡村** | 农田 / 果园 / 村舍街区 / 打谷场 | 地形起伏（数十厘米–数米） | 田埂口 / 小路口 / 场院门 | 地界 / 水渠 |
| 4 | **山林** | 山脊 / 林块 / 草坡 / 溪谷 | **海拔跨度**（可达数百米） | 山口 / 林间通道 / 溪流口 | 悬崖缘 / 陡坡线 |
| 5 | **海洋** | 深海 / 浅滩 / 礁盘 / 航道 | **水深**（水下为负，可达千余米） | 岸线交叉 / 航道 / 海峡 | 岸线 / 等深线 |
| 6 | **沙漠** | 沙丘 / 砾漠 / 绿洲 / 干河床 | 沙丘起伏高度（数米–百余米） | 风口 / 沙丘通道 | 硬岩缘 / 干河谷 |

**室内只是这六类中的一个填法**，它的 `door`/`window`/`structural_edges` 不是契约的默认形状，而是 `feature_type` 的一个取值。

### 0.2 统一抽象的手段

一切场景都归结为**三个通用维度 + 一个开放容器**：

| 维度 | 通用表示 | 说明 |
|------|---------|------|
| **平面轮廓** | `Polygon`（XZ 平面，≥3 点） | 房间 / 街区 / 海域 / 沙丘范围都是平面轮廓 |
| **区域类别** | `region_type: str`（**开放字符串**） | 不枚举场景，词表由各 scene 自行定义 |
| **垂直范围** | `ElevationRange(low, high)` | 中性字段：层高 / 建筑高 / 水深（负）/ 海拔 / 沙丘高 |
| **轮廓语义** | `ContourSemantics.features[]`，每项 `kind ∈ {opening, fixed_edge}` + 开放 `feature_type` | 门/路口/山口/航道都是 opening；承重墙/用地红线/岸线/悬崖缘都是 fixed_edge |
| **场景特有信息** | `attrs: dict` | 一律进 attrs，**不新增字段** |

**这样做的收益**：同一个 Stage 实现可以跨场景复用；同一份可视化 / 校验 / 编辑器可以处理所有场景；新增场景（如"太空站"、"地下洞穴"）不需要改契约。

**这样做的代价**（必须承认）：`attrs` 是弱类型的，运行时无法强校验场景特有内容。缓解办法是把高频属性提升为正式字段，低频的留在 `attrs`——这条边界由本规范第 5 节的演进规则控制。

---

## 1. 三条设计原则

### 1.1 契约是 Stage 之间唯一的数据协议

- Stage 之间**不共享中间变量**、不读对方的内部状态、不互相 import 实现类
- 一个 Stage 只能拿到它 `requires` 里声明的上游**阶段产物**（只读）
- 所有契约集中在 `xasset/pipeline/schemas/`，是**唯一权威定义处**

### 1.2 契约表达"数据形状"，不表达"怎么算出来的"

契约里不出现"用 LLM 生成""用求解器计算"这类实现描述。同一个契约可以由不同实现产出（house / urban / wild 各自实现，输出同一契约）。

### 1.3 契约必须能被序列化与校验

- 全部用 **pydantic v2 `BaseModel`**：可 `model_validate` 校验（LLM 输出直接喂进来）、可 `model_dump_json` 序列化
- 跨产品形态（插件 / 软件 / 页面）传输时，JSON 即协议
- 契约字段带明确类型与约束（`ge`/`gt`/`min_length` 等），**非法数据在进入下游前就被拒绝**

---

## 2. 多上游依赖的表达：`requires` + 具名输入

### 2.1 问题

六层的真实依赖不是单线的：

| Stage | 实际需要读的上游 |
|-------|----------------|
| `understand` | 无（只读 `PipelineInput`） |
| `geometry` | `understand` |
| `layout` | `understand` |
| `surface` | `understand` + `geometry` |
| `accessory` | `understand` + `layout` |
| `stylize` | `understand` + `geometry` + `layout` + `surface` + `accessory` |

单个 `input_type` 表达不了。用 `dict[str, Any]` 又失去类型安全。

### 2.2 方案：`requires` 声明 + `StageInputs` 具名访问

```python
class Stage(Protocol, Generic[TOut]):
    name: str
    layer: str
    scene_types: list[str]

    requires: list[str]          # 依赖的上游 layer 列表，如 ["understand", "geometry"]
    output_type: type[TOut]      # 产出的阶段产物类型

    def run(self, inputs: "StageInputs") -> TOut:
        """inputs 按 requires 声明注入，只含声明的上游产物。"""
```

```python
class StageInputs:
    """按 requires 注入的上游阶段产物（只读）。

    访问未在 requires 中声明的 layer 会抛 KeyError——依赖必须显式声明。
    """

    def __init__(self, pipeline_input: PipelineInput, outputs: dict[str, BaseModel]):
        self._pipeline_input = pipeline_input
        self._outputs = outputs

    @property
    def pipeline_input(self) -> PipelineInput:
        """原始输入（所有 Stage 都可读）。"""
        return self._pipeline_input

    def get(self, layer: str) -> BaseModel:
        if layer not in self._outputs:
            raise KeyError(f"Stage 未声明依赖 '{layer}'，或该上游尚未执行")
        return self._outputs[layer]

    # 具名便捷访问（类型标注让 IDE / 类型检查生效）
    @property
    def understand(self) -> "UnderstandOutput": return self.get("understand")
    @property
    def geometry(self) -> "GeometryOutput":     return self.get("geometry")
    @property
    def layout(self) -> "LayoutOutput":         return self.get("layout")
    @property
    def surface(self) -> "SurfaceOutput":       return self.get("surface")
    @property
    def accessory(self) -> "AccessoryOutput":   return self.get("accessory")
```

### 2.3 框架按 `requires` 注入

```
Pipeline.run:
    for layer in config.stages:
        stage = registry.get(layer, scene_type)
        # 校验依赖已就绪
        for dep in stage.requires:
            if dep not in ctx.stage_outputs:
                raise StageDependencyMissing(f"{stage.name} 依赖 '{dep}' 尚未产出")
        inputs = StageInputs(ctx.input, {d: ctx.stage_outputs[d] for d in stage.requires})
        output = stage.run(inputs)
        # 强校验输出类型
        if not isinstance(output, stage.output_type):
            raise TypeError(...)
        ctx.stage_outputs[layer] = output
```

**好处**：
- 依赖**显式可查**（看类定义就知道这个 Stage 要什么）
- 依赖**顺序自动校验**（漏了上游立刻报错，而不是 `None` 崩在深处）
- 类型**能校验**（具名属性带类型标注）

---

## 3. 六个 Stage 的契约定义

契约文件布局：

```
xasset/pipeline/schemas/
├── __init__.py       # 统一导出
├── common.py         # 共享基础类型（Vec2 / Vec3 / Polygon / ContourSemantics）
├── understand.py     # UnderstandOutput / SceneRegion
├── geometry.py       # GeometryOutput / SceneMesh / RegionGeometry / SubMesh
├── layout.py         # LayoutOutput / PlacedGroup / OpeningPlacement / CurtainPlacement
├── surface.py        # SurfaceOutput / SurfaceElement
├── accessory.py      # AccessoryOutput / AccessoryElement
└── stylize.py        # StylizeOutput / MaterialAssignment / LightConfig / CameraHint
```

### 3.1 共享基础类型（`common.py`）

```python
Vec2 = tuple[float, float]            # [x, z] 平面坐标，单位 m
Vec3 = tuple[float, float, float]     # [x, y, z] 三维坐标，单位 m

class Polygon(BaseModel):
    """平面轮廓（XZ 平面，≥3 个互不相同的点）。"""
    points: list[Vec2] = Field(min_length=3)

class ElevationRange(BaseModel):
    """垂直范围 —— 中性字段，统一各场景的"高度"概念。"""
    low: float = 0.0
    high: float | None = None      # None = 无明确上界（如开阔水域）

class BoundaryFeature(BaseModel):
    """轮廓上的语义要素 —— 通用抽象。"""
    feature_id: str
    kind: str                      # "opening" | "fixed_edge"
    feature_type: str              # 开放字符串：door/window/road_entrance/strait/dune_pass...
    pts: list[Vec2] = []
    seg_start: Vec2 | None = None
    seg_end: Vec2 | None = None
    width: float | None = None
    connects_to: str | None = None # 连通到的区域
    attrs: dict = {}

class ContourSemantics(BaseModel):
    """轮廓语义集合（数据概念，与 Artist 的"约束侧"机制无关）。"""
    features: list[BoundaryFeature] = []

    @property
    def openings(self): return [f for f in self.features if f.kind == "opening"]
    @property
    def fixed_edges(self): return [f for f in self.features if f.kind == "fixed_edge"]
```

### 3.2 `understand` —— 轮廓 + 语义

**输入**：`PipelineInput`（原始输入：图片 / 文字 / 场景矢量）
**输出**：`UnderstandOutput`

```python
class SceneRegion(BaseModel):
    """一个区域 —— 跨场景通用抽象。"""
    region_id: str
    region_type: str = ""                   # 开放字符串，词表按 scene 定义
    boundary: Polygon                       # ★ 轮廓线
    area: float = Field(ge=0)               # m²
    elevation: ElevationRange               # ★ 垂直范围（层高/建筑高/水深/海拔/沙丘高）
    semantics: ContourSemantics             # ★ 轮廓语义（开口 / 固定边）
    priority: int = 0
    attrs: dict = {}                        # 场景特有信息一律进这里

class UnderstandOutput(BaseModel):
    scene_type: str                         # house/urban/rural/mountain/ocean/desert/...
    regions: list[SceneRegion] = []
    style: str | None = None
    constraints: dict = {}
    attrs: dict = {}
```

> **关键**：`understand` 直接产出**轮廓线**（`SceneRegion.boundary`）+ 语义 + 轮廓语义。这正是"第一步通过图片或描述得到轮廓线结果"的契约落点。
>
> `elevation` 的六个场景填法见 0.1 节表格。

### 3.3 `geometry` —— 轮廓 → 3D 几何

**输入**：`requires = ["understand"]`
**输出**：`GeometryOutput`

```python
class SubMesh(BaseModel):
    role: str                     # 开放字符串：floor/ceiling/wall_inner/road_surface/seabed/dune_face...
    region_id: str
    vertices: list[Vec3]
    normals: list[Vec3]
    uvs: list[Vec2]
    faces: list[tuple[int, int, int]]

class WallSegmentMesh(BaseModel):
    edge_index: int               # 沿轮廓第几条边的网格（室内=墙段，海洋=岸线）
    submeshes: list[SubMesh] = []

class RegionGeometry(BaseModel):
    region_id: str
    floor: SubMesh | None = None
    ceiling: SubMesh | None = None
    walls: list[WallSegmentMesh] = []

class SceneMesh(BaseModel):
    regions: list[RegionGeometry] = []
    floor_offset: float = 0.0

class GeometryOutput(BaseModel):
    scene_type: str
    scene_mesh: SceneMesh = SceneMesh()
    wall_thickness: float = Field(default=0.2, gt=0)
    attrs: dict = {}
```

### 3.4 `layout` —— 主体内容摆放

**输入**：`requires = ["understand"]`
**输出**：`LayoutOutput`

跨场景统一为两类：**PlacedElement**（摆进区域的内容主体）+ **PlacedFeature**（轮廓要素的落地实例）。

```python
class PlacedElement(BaseModel):
    """摆进区域的内容主体。室内=家具组，城市=建筑/设施，海洋=船只/礁石。"""
    element_id: str
    element_type: str             # 开放字符串：sofa_group / building / vessel / crop_row ...
    region_id: str
    position: Vec3
    rotation: float = 0.0
    scale: Vec3 = (1.0, 1.0, 1.0)
    parts: dict[str, str | None] = {}          # 部件 → 资产 id
    part_positions: dict[str, Vec3] = {}
    attrs: dict = {}

class PlacedFeature(BaseModel):
    """轮廓要素的落地实例。室内=门窗实体，城市=路口标记，海洋=航道标识。"""
    feature_id: str               # 对应 ContourSemantics 里的 feature_id
    feature_type: str
    region_id: str
    position: Vec3
    rotation: float = 0.0
    width: float | None = None
    attrs: dict = {}

class LayoutOutput(BaseModel):
    scene_type: str
    placed_elements: list[PlacedElement] = []
    placed_features: list[PlacedFeature] = []
    attrs: dict = {}
```

> house 的"家具 Group / 门窗 / 窗帘"只是 `PlacedElement` + `PlacedFeature` 的一种填法，不单独占字段。

### 3.5 `surface` —— 表面覆盖

**输入**：`requires = ["understand", "geometry"]`
**输出**：`SurfaceOutput`

```python
class SurfaceElement(BaseModel):
    element_id: str
    region_id: str
    surface_role: str            # "wall" | "floor" | "ceiling" | "road_base" | "terrain_base"
    material_id: str | None = None
    uv_scale: Vec2 | None = None
    attrs: dict = {}

class SurfaceOutput(BaseModel):
    scene_type: str
    elements: list[SurfaceElement] = []
```

### 3.6 `accessory` —— 点缀

**输入**：`requires = ["understand", "layout"]`
**输出**：`AccessoryOutput`

```python
class AccessoryElement(BaseModel):
    element_id: str
    region_id: str
    accessory_type: str          # "vase" | "lamp_post" | "shrub" ...
    asset_id: str | None = None
    position: Vec3
    rotation: float = 0.0
    scale: Vec3 = (1.0, 1.0, 1.0)

class AccessoryOutput(BaseModel):
    scene_type: str
    elements: list[AccessoryElement] = []
```

### 3.7 `stylize` —— 风格化

**输入**：`requires = ["understand", "geometry", "layout", "surface", "accessory"]`
**输出**：`StylizeOutput`

```python
class MaterialAssignment(BaseModel):
    target_id: str               # 对应 SurfaceElement.element_id 或资产实例
    material_id: str
    params: dict = {}

class LightConfig(BaseModel):
    light_type: str              # "directional" | "point" | "ambient"
    position: Vec3 | None = None
    rotation: float | None = None
    intensity: float = Field(ge=0)
    color: str | None = None

class CameraHint(BaseModel):
    position: Vec3
    target: Vec3
    fov: float | None = None

class StylizeOutput(BaseModel):
    style: str | None = None
    material_assignments: list[MaterialAssignment] = []
    light_config: list[LightConfig] = []
    camera_hints: list[CameraHint] = []
```

> 注：现有 `StylizeOutput.light_config` 是 `dict | None`，本规范改为 `list[LightConfig]`（支持多光源）。这是契约变更点，需确认。

---

## 4. 依赖图与执行顺序

```
PipelineInput
     │
     ▼
 understand ──────┬──────────────┬─────────────┐
     │            │              │             │
     ▼            │              │             │
 geometry         │              │             │
     │            │              │             │
     ├────────────┤              │             │
     ▼            ▼              ▼             │
  surface      layout        accessory         │
     │            │              │             │
     └────────────┴──────────────┴─────────────┘
                  │
                  ▼
               stylize
```

当前默认顺序 `understand → geometry → layout → surface → accessory → stylize` 与依赖图**相容**（拓扑序之一）。

> `layout` 与 `geometry` 之间无依赖，可以并行（未来优化点）。

---

## 5. 契约的演进规则

1. **新增字段必须有默认值**——保证旧数据 / 旧实现仍能构造
2. **删除或改名字段属于破坏性变更**——必须同步所有实现与测试
3. **契约不承载"实现细节"**——某个 Stage 内部用 LLM 还是视觉算法，不出现在契约里
4. **跨 scene_type 共用同一契约**——house/urban/wild 的差异体现在字段的**取值**与 `attrs`，不体现在类型不同

---

## 6. 与现有代码的差异（迁移清单）

| 项 | 现状 | 迁移后 |
|----|------|--------|
| schema 定义位置 | 散落在各 Stage 文件内 | 统一到 `pipeline/schemas/` |
| schema 技术 | `dataclass` | `pydantic.BaseModel` |
| `run()` 签名 | `run(ctx) -> None` | `run(inputs) -> TOut` |
| 依赖声明 | 隐式（`ctx.stage_outputs.get(...)`） | 显式 `requires = [...]` |
| 输出校验 | 无 | 框架 `isinstance` 强校验 |
| `SceneRegion.boundary` | `list[list[float]]` | `Polygon` |
| `SceneRegion` 语义字段 | `doors` / `windows` / `structural_edges` 分开 | 收敛到 `semantics: ContourSemantics` |
| `StylizeOutput.light_config` | `dict \| None` | `list[LightConfig]` |
| `PlacedGroup` | 无 `region_id` | 新增 `region_id` |

---

## 7. 待确认问题

- [ ] `SceneRegion` 的 `doors`/`windows`/`structural_edges` 收敛到 `semantics` 是**破坏性变更**，现有 `scene_understand.py` 的输入解析路径要改，是否接受？
- [ ] `StylizeOutput.light_config` 从 `dict | None` 改为 `list[LightConfig]` 是否接受？
- [ ] `PlacedGroup.region_id` 新增是否合理（摆件需要知道属于哪个区域）？
- [ ] 阶段产物是否需要统一带一个 `meta` 字段（记录产出时间、实现版本、置信度等）？
- [ ] `understand` 的输入是否需要独立的 `UnderstandInput` 契约（而非直接读 `PipelineInput`）？
