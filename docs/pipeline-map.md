# Pipeline Map — 管线阶段与模块全景

> 最后更新: 2026-09
>
> **本次更新完成:**
> - 算法全面重做：Stage 内部实现统一为 **Artist** 范式（LLM × 边界约束 迭代收敛），见 `docs/stage-paradigm-design.md`
> - 六层顺序重排为「轮廓 → 主体 → 细节」：`understand → geometry → layout → surface → accessory → stylize`
> - 规则式算法清理：`room_decompose.py` / `groups.json` / `sample_search.py` / `placement_zone.py` / `config/loader.py` 等已删除；独立几何工具迁入 `tools/geometry/`；新增 `llm/` 编排骨架
> - 每个 Stage 都是一个独立产品单元，可用「插件 / 软件 / 页面」三种产品形态包装
>
> **术语表（本文档权威写法）**：定义见 `docs/stage-paradigm-design.md` 术语表。核心词：**Stage** / **Artist** / **LLM** / **边界约束** / **迭代收敛** / **阶段产物** / **求解器** / **校验门** / **产品形态** / **输入输出契约**。

---

## 六层管线总览（顺序已重排为 轮廓 → 主体 → 细节）

| # | 阶段 | Layer | house (室内) | urban (城市) | wild (野外) | 阶段产物 |
|---|------|-------|-------------|-------------|------------|---------|
| 1 | 轮廓 | **understand** | `SceneUnderstandStage` `[*]` | 同左 | 同左 | `SceneUnderstandOutput` |
| 2 | 轮廓 | **geometry** | `MeshBuildStage` | ❌ 缺 | ❌ 缺 | `MeshBuildOutput` |
| 3 | 主体 | **layout** | `HouseLayoutComposeStage` | ❌ 缺 | ❌ 缺 | `LayoutOutput` |
| 4 | 主体 | **surface** | `SurfaceStage` (待实现) `[*]` | 同左 | 同左 | `SurfaceOutput` |
| 5 | 细节 | **accessory** | `AccessoryStage` (待实现) `[*]` | 同左 | 同左 | `AccessoryOutput` |
| 6 | 细节 | **stylize** | `StylizeStage` (待实现) `[*]` | 同左 | 同左 | `StylizeOutput` |

```
✅ = 已实现    ❌ 缺 = 未实现    待实现 = 骨架在、算法待 Artist 范式重做（当前返回空阶段产物，管线可跑通）
```

> 算法重做过渡期：六层 Stage 骨架与阶段产物 schema 均保留（契约不变），但规则式算法已清理，待按 Artist 范式逐一接入 LLM 与边界约束求解器。

---

## 各层详情

### 1. understand — 场景理解（轮廓，`[*]` 三场景共享）

| 模块 | 职责 |
|------|------|
| `pipeline/stages/understand/scene_understand.py` | `SceneUnderstandStage`：语义理解（场景 / 区域 / 类型），Artist 范式中的「理解」侧重层 |
| `tools/geometry/normalize.py` | 多边形去噪 / 简化 / 归一化（确定性工具，边界约束侧） |

**阶段产物** `SceneUnderstandOutput`: `scene_type` + `regions[SceneRegion]`

`SceneRegion` 上的轮廓语义（`doors` / `windows` / `structural_edges`）当前只有 house 填满；urban/wild 的 `region_type` 词表与固定边语义仍是空白，见 `research/unified-scene-pipeline/README.md` 第 2.1 / 2.2 节。

### 2. geometry — 边界重建（轮廓，`house` 仅室内）

| 模块 | 职责 |
|------|------|
| `pipeline/stages/geometry/house/mesh_build.py` | `MeshBuildStage`：SceneRegion → SceneMesh（地板 / 天花板 / 开洞 / UV），规则式网格算法已清理，待 Artist 范式重做 |
| `tools/geometry/mesh.py` | Ear-cut 三角剖分 + 多边形面积（确定性工具） |
| `tools/geometry/uv.py` | UV 坐标映射（确定性工具） |

**阶段产物** `MeshBuildOutput`: `scene_type` + `scene_mesh` (含 `regions[RegionGeometry]`)

**待补**: urban 建筑 / 道路网格、wild 地形网格

### 3. layout — 组合布局（主体，`house` 仅室内）

| 模块 | 职责 |
|------|------|
| `pipeline/stages/layout/house/compose.py` | `HouseLayoutComposeStage`：组合布局，`placed_groups` 当前恒为空（组合算法待 Artist 范式重做） |

**阶段产物** `LayoutOutput`: `scene_type` + `placed_groups[PlacedGroup]`（另有 `doors` / `windows` / `curtains` 字段）

**待补**: 组合布局的约束求解器（不越界 / 不碰撞 / 留净宽）、urban 建筑排列、wild 特征物散布

### 4. surface — 表面覆盖（主体，`[*]` 三场景共享）

| scene_type | 语义 |
|-----------|------|
| house | 硬装铺贴：墙纸、地板、吊顶 |
| urban | 道路基础面、绿化带 |
| wild | 地貌基底：草地、水体、沙漠 |

### 5. accessory — 装饰点缀（细节，`[*]` 三场景共享）

| scene_type | 语义 |
|-----------|------|
| house | 小饰品：花瓶、相框、书籍 |
| urban | 路灯、标识牌、垃圾箱 |
| wild | 碎石、灌木、散落草木 |

### 6. stylize — 风格化（细节，`[*]` 三场景共享）

**阶段产物** `StylizeOutput`: `material_assignments` + `light_config` + `camera_hints`

---

## 管线框架（跨层共享）

| 文件 | 职责 |
|------|------|
| `pipeline/context.py` | `PipelineInput` / `PipelineContext` / `VariationInput` |
| `pipeline/stage.py` | Stage Protocol（`name` + `layer` + `scene_types` + `run`） |
| `pipeline/registry.py` | 按 `(layer, scene_type)` 分发 Stage |
| `pipeline/pipeline.py` | Pipeline 顺序执行器 + `PipelineConfig` |

> Stage Protocol 将按 `docs/stage-paradigm-design.md` 第 5 节改造：新增 `input_type` / `output_type`，`run()` 返回阶段产物。当前实现见 `pipeline/stage.py`。

---

## 跨层模块

| 目录 | 职责 |
|------|------|
| `llm/` | LLM 侧抽象：`LLMProvider` + 编排骨架（Artist 范式的「想法」侧） |
| `tools/geometry/` | 边界约束侧确定性工具：三角剖分 / UV / 多边形归一化 |
| `tools/constraint/` | 边界约束侧校验门：`ConstraintSet` / `ConstraintRule` / `ValidationResult` |
| `services/generation.py` | 生成入口（submit / variation / status / result） |
| `storage/local.py` | 本地文件存储 |
| `jobs/store.py` | 内存任务管理 |
| `debug/` | 可视化调试 |

---

## 引擎 vs 产品

```
xasset/
├── xasset/                      # ═══ 引擎库（可 pip install） ═══
│   ├── pipeline/                #   六层管线 + 阶段产物 schema
│   ├── llm/                     #   LLM 侧抽象（Artist 范式的想法侧）
│   ├── tools/                   #   边界约束侧：几何工具 + 约束校验门
│   ├── services/                #   生成入口
│   ├── debug/                   #   可视化（供产品调用）
│   ├── storage/  jobs/          #   存储 / 任务
│
└── products/                    # ═══ 产品（组合引擎模块，可独立发布） ═══
    ├── cli/                     #   CLI 调试工具（debug_run.py）
    ├── layout_blender/          #   Blender 插件
    └── layout_omniverse/        #   Omniverse 扩展
```

- 引擎层不独立运行，被产品 import
- 产品层按需组合 pipeline stages + services，有自己的入口和部署方式
- 每个 Stage 都是独立产品单元，可用「插件 / 软件 / 页面」三种产品形态包装（见 `docs/stage-paradigm-design.md` 第 3 节）
- 后续每个产品可独立打包（pip 包 / Blender addon zip / Omniverse ext / Docker image）

---

## 缺项统计

| 优先级 | 缺口 | 分支 | 说明 |
|--------|------|------|------|
| P0 | 六层 Stage 按 Artist 范式重做 | master | 规则式算法已清，待接入 LLM + 边界约束求解器 |
| P0 | geometry: urban + wild | xasset-urban / xasset-outdoor | 建筑 / 道路网格、地形网格 |
| P0 | layout: urban + wild | xasset-urban / xasset-outdoor | 建筑排列、特征物散布 |
| P1 | 各层 Stage 阶段产物协议化 | master | 同层不同实现产出格式需统一（stage-paradigm 第 5 节） |

---

## 扩展新场景

新增一个场景类型（如 `"scifi"`、`"medieval"`）的步骤：

1. **定义语义**：确定 scene_type 字符串（如 `"scifi"`）
2. **逐层判断**：对 6 层分别决定——复用已有 `[*]` 实现、还是新建 Stage

| Layer | 可复用 | 需新建 |
|-------|--------|--------|
| understand | `SceneUnderstandStage` `[*]` | — |
| stylize | `StylizeStage` `[*]` | — |
| surface | `SurfaceStage` `[*]` | — |
| accessory | `AccessoryStage` `[*]` | — |
| geometry | — | `SciFiMeshBuildStage` → 注册 `["scifi"]` |
| layout | — | `SciFiLayoutComposeStage` → 注册 `["scifi"]` |

3. **新增文件**：`pipeline/stages/geometry/scifi/...` 等，实现 Stage Protocol
4. **注册**：`registry.register(SciFiMeshBuildStage())`
5. **更新本文档**：在总览表加一列

管线 6 层定义不变，`PipelineConfig.stages` 不变，只是 Registry 按 `scene_type` 分发到了新实现。
