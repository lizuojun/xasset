# Scene Generation Pipeline Design

**Goal:** 定义一套通用的场景生成分层协议，并以室内（house）场景作为首个完整实现。

**Architecture:** 六层协议顺序固定，每层职责单一、可独立运行，算法实现按 scene_type 注册。

> **Current State (2026-06-15):** 管线框架已落地，六层全部可跑通（缺层以桩 Stage 填补）。
> 目录结构按 `stages/<layer>/<scene>/` 组织，详下。

---

## Current Implementation — 目录结构 & 管线全景

```
xasset/
├── pipeline/
│   ├── context.py                # PipelineInput / PipelineContext / VariationInput
│   ├── stage.py                  # Stage Protocol（name / layer / scene_types / run）
│   ├── registry.py               # StageRegistry（按 layer + scene_type 分发）
│   ├── pipeline.py               # Pipeline 执行器 + PipelineConfig
│   ├── utils/                    # 跨层共享工具
│   │   ├── mesh_utils.py         #   Ear-cut 三角剖分
│   │   ├── uv_utils.py           #   UV 坐标映射
│   │   └── vector_normalize.py   #   多边形去噪/归一化
│   └── stages/                   # Stage 实现（按 layer/scene 组织）
│       ├── understand/
│       │   └── scene_understand.py    # SceneUnderstandStage [*]
│       ├── geometry/
│       │   └── house/
│       │       └── mesh_build.py      # MeshBuildStage [house]
│       ├── surface/
│       │   └── stage.py               # SurfaceStage 桩 [*]
│       ├── layout/
│       │   └── house/
│       │       ├── compose.py         # HouseLayoutComposeStage [house]
│       │       └── room_decompose.py  # 墙体分段分析（同层内部模块）
│       ├── accessory/
│       │   └── stage.py               # AccessoryStage 桩 [*]
│       └── stylize/
│           └── stylize.py             # StylizeStage 桩 [*]
│
├── config/  services/  debug/  storage/  jobs/
├── tests/
├── docs/pipeline-map.md              # ← 管线全景图（最权威参考）
└── debug_run.py                       # 手动调试入口
```

### 六层管线状态

| # | Layer | house | urban | wild | output |
|---|-------|-------|-------|------|--------|
| 1 | understand | ✅ `SceneUnderstandStage` `[*]` | 同左 | 同左 | `SceneUnderstandOutput` |
| 2 | geometry | ✅ `MeshBuildStage` | ❌ 缺 | ❌ 缺 | `MeshBuildOutput` |
| 3 | surface | 桩 `SurfaceStage` `[*]` | 同左 | 同左 | `SurfaceOutput` |
| 4 | layout | ✅ `HouseLayoutComposeStage` | ❌ 缺 | ❌ 缺 | `LayoutOutput` |
| 5 | accessory | 桩 `AccessoryStage` `[*]` | 同左 | 同左 | `AccessoryOutput` |
| 6 | stylize | 桩 `StylizeStage` `[*]` | 同左 | 同左 | `StylizeOutput` |

> `[*]` = 三个场景共享实现。桩 = 返回空 output，管线可跑通，待后续填充。

### 扩展规则

新增场景（如 `scifi`）：逐层判断复用 `[*]` 实现 or 在 `stages/<layer>/<scene>/` 下新建 Stage，注册到 Registry 即可。六层定义不变。

**目录命名规则：** 有 `scene/` 子目录 = 场景专属，无 = 共享或桩。

```
97 tests passed (2026-06-15)
```

---

## 0. 通用场景生成协议

### 0.1 六层协议

场景生成的核心步骤与具体场景类型无关，仅算法不同：

| Layer | 通用名称 | 职责 |
|-------|---------|------|
| 1 | **UnderstandStage** 理解层 | 解析输入数据，输出场景结构 |
| 2 | **GeometryStage** 几何层 | 构建基础几何（纯算法，无方案库） |
| 3 | **SurfaceStage** 表面层 | 固定铺层：墙纸/地板/地貌覆盖 |
| 4 | **LayoutStage** 布局层 | 主体对象摆放 |
| 5 | **AccessoryStage** 配饰层 | 细节点缀 |
| 6 | **StylizeStage** 表现层 | 材质/灯光/相机 |

**协议约定：**
- 执行顺序固定（1→2→3→4→5→6），每层可单独跳过或独立运行
- 每层输出写入 `PipelineContext.stage_outputs`，供后续层读取
- 各层实现通过 `StageRegistry` 按 `(layer, scene_type)` 注册和分发

### 0.2 各场景类型的实现映射

```
Layer           house                    outdoor                  urban
─────────────────────────────────────────────────────────────────────────────
UnderstandStage SceneUnderstandStage     TerrainUnderstandStage   CityUnderstandStage
GeometryStage   MeshBuildStage           TerrainBuildStage        CityMeshStage
surface       SurfaceStage            RoadSurfaceStage         TerrainCoverageStage
LayoutStage     HouseLayoutComposeStage  OutdoorFeatureLayoutStage BuildingLayoutStage
AccessoryStage  AccessoryStage           ScatterStage             StreetFurnitureStage
StylizeStage    StylizeStage             StylizeStage             StylizeStage
```

> AccessoryStage / StylizeStage 跨场景复用，差异仅在方案库和参数。

### 0.3 各场景类型的未来实现映射

```
Layer         house                    urban                    wild
───────────────────────────────────────────────────────────────────────────
understand    SceneUnderstandStage [*] 同左                     同左
geometry      MeshBuildStage          CityMeshStage            TerrainBuildStage
surface       SurfaceStage            RoadSurfaceStage         TerrainCoverageStage
layout        HouseLayoutComposeStage  BuildingLayoutStage      FeatureScatterStage
accessory     AccessoryStage           StreetFurnitureStage     DetailScatterStage
stylize       StylizeStage [*]        同左                     同左
```

> `[*]` = 可跨场景复用。暂时未实现的以桩 Stage 占位。

### 0.4 关键设计原则

1. **管线层固定，实现按 scene_type 分发** — PipelineConfig 只管 6 个 layer key
2. **同层产出格式统一** — 不同 scene_type 的同一层必须产出一致的 output 类型
3. **桩 Stage 保证管线完整可跑** — 缺层不阻塞，返回标识性空 output（`status: "stub"`）
4. **目录规则** — `stages/<layer>/<scene>/` = 场景专属，无 scene 子目录 = 共享/桩

---

## 1. 原始输入 → 矢量 Pipeline

Pipeline 消费矢量数据（SceneVector JSON）。原始输入（图片/文字）由独立的 RecognitionService 转换，不进 Stage 链。

```
图片/文字 → RecognitionService → SceneVector JSON → Pipeline Stage 1
```

现阶段可跳过 RecognitionService，直接用矢量数据输入。

---

## 2. Stage Output 协议

各层 output 类型定义于对应 Stage 文件中：

| Layer | Output 类型 | 文件 |
|-------|------------|------|
| understand | `SceneUnderstandOutput` | `stages/understand/scene_understand.py` |
| geometry | `MeshBuildOutput` | `stages/geometry/house/mesh_build.py` |
| surface | `SurfaceOutput` | `stages/surface/stage.py` |
| layout | `LayoutOutput` | `stages/layout/house/compose.py` |
| accessory | `AccessoryOutput` | `stages/accessory/stage.py` |
| stylize | `StylizeOutput` | `stages/stylize/stylize.py` |

---

## 3. 参考

完整目录结构和缺项统计见 `docs/pipeline-map.md`（最权威参考）。

