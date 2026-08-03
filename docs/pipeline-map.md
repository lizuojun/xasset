# Pipeline Map — 管线阶段与模块全景

> 最后更新: 2026-06-15
> 
> **本次 (2026-06-15) 完成:**
> - 移除 DB 层，管线纯内存运行（3 依赖：pydantic/numpy/matplotlib）
> - 按 `stages/<layer>/<scene>/` 重组目录，`utils/` 放共享工具
> - 新增 surface/accessory 桩 Stage，六层全可跑通
> - 新增 `products/cli/` 产品目录，引擎与产品分离
> - 每个 stage 下放 `output_sample.json` 作为格式契约
> - 重置仓库为干净起点，master / xasset-urban / xasset-outdoor 三分支并行
> 
> **下一步:**
> - `xasset-urban` 分支：urban geometry/layout Stage 实现
> - `xasset-outdoor` 分支：wild geometry/layout Stage 实现
> - 各层 Stage output 协议化（同层不同场景产出统一格式）

---

## 六层管线总览

| # | Layer | house (室内) | urban (城市) | wild (野外) | output 格式 |
|---|-------|-------------|-------------|------------|-------------|
| 1 | **understand** | `SceneUnderstandStage` `[*]` | 同 left | 同 left | `SceneUnderstandOutput` |
| 2 | **geometry** | `MeshBuildStage` | ❌ 缺 | ❌ 缺 | `MeshBuildOutput` |
| 3 | **surface** | `SurfaceStage` (桩) `[*]` | 同 left | 同 left | `SurfaceOutput` |
| 4 | **layout** | `HouseLayoutComposeStage` | ❌ 缺 | ❌ 缺 | `LayoutOutput` |
| 5 | **accessory** | `AccessoryStage` (桩) | 同 left | 同 left | `AccessoryOutput` |
| 6 | **stylize** | `StylizeStage` (桩) `[*]` | 同 left | 同 left | `StylizeOutput` |

```
✅ = 已实现    ❌ 缺 = 未实现    桩 = 空桩代码（返回标识性空 output，管线可跑通）
```

---

## 各层详情

### 1. understand — 场景理解 ([*] 三个场景共享)

| 模块 | 职责 |
|------|------|
| `pipeline/stages/understand/scene_understand.py` | SceneVector JSON → 标注化的 SceneRegion 列表 |
| `pipeline/utils/vector_normalize.py` | 多边形去噪/简化/归一化 |

**output** `SceneUnderstandOutput`: `scene_type` + `regions[SceneRegion]`

### 2. geometry — 几何构建 ([house] 仅室内)

| 模块 | 职责 |
|------|------|
| `pipeline/stages/geometry/house/mesh_build.py` | SceneRegion → SceneMesh (地板/天花板/墙体开洞/UV) |
| `pipeline/utils/mesh_utils.py` | Ear-cut 三角剖分算法 |
| `pipeline/utils/uv_utils.py` | UV 坐标映射 |

**output** `MeshBuildOutput`: `scene_type` + `scene_mesh` (含 regions[RegionGeometry])

**待补**: urban 建筑/道路网格、wild 地形网格

### 3. surface — 表面覆盖层 (桩 Stage，三层共享)

| scene_type | 语义 |
|-----------|------|
| house | 硬装铺贴：墙纸、地板、吊顶 |
| urban | 道路基础面、绿化带 |
| wild | 地貌基底：草地、水体、沙漠 |

### 4. layout — 物体布局 ([house] 仅室内)

| 模块 | 职责 |
|------|------|
| `pipeline/stages/layout/house/compose.py` | 配置驱动的区域→Group映射+放置 (Step 1) |
| `pipeline/stages/layout/house/room_decompose.py` | 墙体分段+深度分析+墙面质量 (Step 2) |
| `config/loader.py` | 加载 GroupDefinition JSON（glob 匹配 `groups*.json`） |
| `config/schemas.py` | GroupDefinition / RoleDefinition / Template |
| `pipeline/stages/layout/house/groups.json` | 29组 × 11区域类型的室内布局配置 |

**output** `LayoutOutput`: `scene_type` + `placed_groups[PlacedGroup]`

**待补**: urban 建筑排列、wild 特征物散布

### 5. accessory — 装饰点缀 (桩 Stage，三层共享)

| scene_type | 语义 |
|-----------|------|
| house | 小饰品：花瓶、相框、书籍 |
| urban | 路灯、标识牌、垃圾箱 |
| wild | 碎石、灌木、散落草木 |

### 6. stylize — 风格化 ([*] 桩代码)

| 模块 | 职责 |
|------|------|
| `pipeline/stages/stylize/stylize.py` | 材质分配 + 灯光 + 相机（目前返回空） |

**output** `StylizeOutput`: `material_assignments` + `light_config` + `camera_hints`

---

## 管线框架 (跨层共享)

| 文件 | 职责 |
|------|------|
| `pipeline/context.py` | `PipelineInput` / `PipelineContext` / `VariationInput` |
| `pipeline/stage.py` | Stage Protocol (`name` + `layer` + `scene_types` + `run`) |
| `pipeline/registry.py` | 按 `(layer, scene_type)` 分发 Stage |
| `pipeline/pipeline.py` | Pipeline 顺序执行器 + `PipelineConfig` |

---

## 管线外服务

| 文件 | 职责 |
|------|------|
| `services/generation.py` | 生成入口 (submit / variation / status / result) |
| `services/sample_search.py` | 向量相似搜索 (内存 + LRU缓存) |
| `services/placement_zone.py` | 3D网格放置区域分析 |
| `storage/local.py` | 本地文件存储 |
| `jobs/store.py` | 内存任务管理 |
| `debug/` | 可视化调试 (按场景子目录) |

---

## 缺项统计

| 优先级 | 缺口 | 分支 | 说明 |
|--------|------|------|------|
| P0 | geometry: urban + wild | xasset-urban / xasset-outdoor | 建筑/道路网格、地形网格 |
| P0 | layout: urban + wild | xasset-urban / xasset-outdoor | 建筑排列、特征物散布 |
| P1 | surface: 完善实现 | master | 三场景桩→实际逻辑 |
| P1 | accessory: 完善实现 | master | 三场景桩→实际逻辑 |
| P1 | stylize: 完善实现 | master | 从空桩→实际材质/灯光逻辑 |
| P1 | 各层 Stage output 协议化 | master | 同层不同实现产出格式需统一 |

---

## 扩展新场景

新增一个场景类型（如 `"scifi"`、`"medieval"`）的步骤：

1. **定义语义**：确定 scene_type 字符串（如 `"scifi"`）
2. **逐层判断**：对 6 层分别决定——复用已有 `[*]` 实现、还是新建 Stage

| Layer | 可复用 | 需新建 |
|-------|--------|--------|
| understand | `SceneUnderstandStage` `[*]` | — |
| stylize | `StylizeStage` `[*]` | — |
| geometry | — | `SciFiMeshBuildStage` → 注册 `["scifi"]` |
| surface | — | 自定义 Stage |
| layout | — | 自定义 Stage + `groups.json`（放在 `stages/layout/<scene>/` 下） |
| accessory | — | 自定义 Stage |

3. **新增文件**：`pipeline/stages/scifi_mesh_build.py` 等，实现 Stage Protocol
4. **注册**：`registry.register(ScifiMeshBuildStage())`
5. **配置文件**：`stages/layout/<scene>/groups.json`（区域→组映射）
6. **更新本文档**：在总览表加一列

管线 6 层定义不变，`PipelineConfig.stages` 不变，只是 Registry 按 `scene_type` 分发到了新实现。

---

## 引擎 vs 产品

```
xasset/
├── xasset/                      # ═══ 引擎库（可 pip install） ═══
│   ├── pipeline/                #   六层管线 + 工具
│   ├── config/                  #   GroupDefinition loader
│   ├── services/                #   搜索 / 放置分析
│   ├── debug/                   #   可视化（供产品调用）
│   ├── storage/  jobs/          #   存储 / 任务
│
└── products/                    # ═══ 产品（组合引擎模块，可独立发布） ═══
    ├── cli/                     #   CLI 调试工具（debug_run.py）
    └── blender/                 #   Blender 插件（future）
```

- 引擎层不独立运行，被产品 import
- 产品层按需组合 pipeline stages + services，有自己的入口和部署方式
- 后续每个产品可独立打包（pip 包 / Blender addon zip / Docker image）


