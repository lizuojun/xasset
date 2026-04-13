# Scene Generation Pipeline Design

**Goal:** 定义一套通用的场景生成分层协议，并以室内（house）场景作为首个完整实现。

**Architecture:** 六层协议顺序固定，每层职责单一、可独立运行，算法实现按 scene_type 注册；方案库统一采用"特征提取 → 方案库匹配 → 算法放置/调整"模式。

**Tech Stack:** Python 3.12, Pydantic v2, SQLAlchemy 2.0 async, SQLite/aiosqlite, NumPy（几何计算）, existing xasset pipeline infrastructure

---

## 0. 通用场景生成协议

### 0.1 六层协议

场景生成的核心步骤与具体场景类型无关，仅算法不同：

| Layer | 通用名称 | 职责 |
|-------|---------|------|
| 1 | **UnderstandStage** 理解层 | 解析输入数据，输出场景结构 |
| 2 | **GeometryStage** 几何层 | 构建基础几何（纯算法，无方案库） |
| 3 | **BaseLayerStage** 基础层 | 固定铺层（特征 + 方案库 + 放置） |
| 4 | **LayoutStage** 布局层 | 主体对象摆放（特征 + 方案库 + 布局） |
| 5 | **AccessoryStage** 配饰层 | 细节点缀，可选（特征 + 方案库 + 放置） |
| 6 | **StylizeStage** 表现层 | 资产替换 + 微调 + 渲染配置 |

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
BaseLayerStage  HardDecorationStage      LandscapeCoverageStage   RoadInfraStage
LayoutStage     HouseLayoutComposeStage  OutdoorFeatureLayoutStage BuildingLayoutStage
AccessoryStage  AccessoryStage           ScatterStage             StreetFurnitureStage
StylizeStage    StylizeStage             StylizeStage             StylizeStage
```

> AccessoryStage / StylizeStage 跨场景复用，差异仅在方案库和参数。

### 0.3 命名规范

**Stage 类命名：两级命名，不冲突**

每个具体 Stage 类保留语义名，同时通过 `layer` 属性声明所属通用层：

```python
class HardDecorationStage:
    name = "hard_decoration"     # stage 唯一标识
    layer = "base_layer"         # 对应通用协议层
    scene_types = ["house"]

class MeshBuildStage:
    name = "mesh_build"
    layer = "geometry"
    scene_types = ["house"]
```

通用层名（`layer` 值）规范：

| 通用层 | layer 值 |
|--------|---------|
| 理解层 | `understand` |
| 几何层 | `geometry` |
| 基础层 | `base_layer` |
| 布局层 | `layout` |
| 配饰层 | `accessory` |
| 表现层 | `stylize` |

**方案库 domain 命名：与通用层对齐**

`SampleSearchService` 的 domain key 使用通用层名，而非语义名：

| 通用层 | domain key | 对应方案库 |
|--------|-----------|----------|
| `base_layer` | `base_layer` | 硬装方案库 / 地貌方案库 |
| `layout` | `layout` | 软装 Group 方案库 / 地标方案库 |
| `accessory` | `accessory` | 配饰方案库 / 散布物方案库 |
| `stylize` | `stylize` | 布光+材质方案库 |

> 接口：`search(domain: str, feature_vec: list[float], top_k: int) -> list[SchemeMatch]`

**文档术语约定：**
- 第 0 节使用通用层名
- 第 3 节及之后使用具体实现名
- 两者通过 0.2 映射表关联，不混用

### 0.4 方案库通用模式

后四层（base_layer / layout / accessory / stylize）均遵循同一模式：

```
特征提取（输入数据 → 特征向量）
    ↓
方案库检索（domain + 特征向量 → top-K 候选方案）
    ↓
算法放置/调整（候选方案 → 最终输出）
```

---

## 1. 输入层设计

### 1.1 两层输入处理

Pipeline 永远只消费矢量数据。原始输入（图片/文字）由独立的 **RecognitionService** 在 Pipeline 之外完成转换：

```
原始输入
├── 户型图片 ──┐
├── 室内实拍 ──┤ RecognitionService → HouseInfo 矢量
├── 文字描述 ──┘
│
▼
PipelineInput.room_vector（统一矢量入口）
│
▼
Pipeline Stage 1: SceneUnderstandStage（只处理矢量）
```

**RecognitionService 定位：**
- 独立服务，不进入 Pipeline Stage 链
- 可独立迭代升级（换更好的识别模型）而不影响 Pipeline
- 现阶段可跳过（直接用矢量数据输入）

outdoor 场景同理：
```
地图图片 / 实拍图片 → RecognitionService → TerrainInfo 矢量 → Pipeline
```

---

### 1.2 房间矢量数据格式（RoomVector）

**设计原则：**
- 坐标系：`xzy`（x/z 水平，y 垂直），单位 m
- `area` 不存储，由 Pipeline 内 Shoelace 公式从 `floor` 计算
- `pts` 使用结构化点列表（非 flat array）
- 飘窗（bay window）是窗的子类型，用 `window_type` 区分，参与相同的布局约束，在 AccessoryStage 可按类型分流处理

```json
{
  "meta": {
    "coordinate": "xzy",
    "unit": "m",
    "version": "1.0"
  },
  "rooms": [
    {
      "id": "room-uuid",
      "type": "living_room",
      "height": 2.8,
      "floor": [[x,z], [x,z], ...],
      "doors": [
        {
          "id": "door-uuid",
          "pts": [[x,z],[x,z],[x,z],[x,z]],
          "height": 2.1,
          "to_room": "room-uuid-or-null"
        }
      ],
      "windows": [
        {
          "id": "window-uuid",
          "window_type": "normal",
          "pts": [[x,z],[x,z],[x,z],[x,z]],
          "sill_height": 0.9,
          "height": 1.5
        },
        {
          "id": "baywindow-uuid",
          "window_type": "bay",
          "pts": [[x,z],[x,z],[x,z],[x,z],[x,z],[x,z]],
          "sill_height": 0.45,
          "height": 1.5,
          "depth": 0.6
        }
      ],
      "holes": [
        {
          "pts": [[x,z],[x,z],[x,z],[x,z]],
          "height": 2.8
        }
      ]
    }
  ]
}
```

### 1.3 多房间并发处理

Pipeline 以**单房间**为单位执行，多房间由调用方并发提交多个 Job：

```
GenerationService.submit_batch(rooms: list[RoomVector])
    → 为每个房间并发提交独立 Job
    → 返回 list[job_id]
```

房间间关联（如门的 `to_room`）在布局阶段用于约束分析，不影响并发执行。

### 1.4 PipelineInput

```python
@dataclass
class PipelineInput:
    input_type: str          # "vector" | "image" | "text"
    scene_type: str          # "house" | "outdoor" | "urban"
    room_vector: dict        # RoomVector 格式（单房间）
    room_type: str           # "living_room" | "bedroom" | ...
    style: str = ""
    constraints: dict = field(default_factory=dict)
```

> `input_type` 保留用于记录来源，到达 Pipeline 时已全部为矢量数据。

---

## 2. Pipeline Stage 总览（house 场景实现）

| Layer | house 实现 | 职责 |
|-------|-----------|------|
| UnderstandStage | `SceneUnderstandStage` | 解析矢量，输出房间结构 |
| GeometryStage | `MeshBuildStage` | 白模 Mesh 重建 |
| BaseLayerStage | `HardDecorationStage` | 硬装方案匹配 + 模型放置 |
| LayoutStage | `HouseLayoutComposeStage` | 软装方案匹配 + Group 布局 |
| AccessoryStage | `AccessoryStage` | 配饰方案匹配 + 放置（可选） |
| StylizeStage | `StylizeStage` | 资产替换 + 微调 + 渲染布光配置 |

各 Stage 均实现 `Stage` Protocol，可独立运行，通过 `PipelineContext.stage_outputs` 传递数据。

---

## 3. Stage 详细设计（house 场景）

### 3.1 SceneUnderstandStage

**输入：** `PipelineInput.room_vector`

**职责：**
- 解析 `floor` 坐标列表为多边形顶点
- 用 Shoelace 公式计算多边形面积（不信任输入的 area 字段）
- 解析 doors / windows 为结构化对象，缺失字段填入默认值
- 由 pts 计算门的 normal、center、width
- 输出 `SceneUnderstandOutput`

**行业规范默认值：**

```python
HOUSE_DEFAULTS = {
    "room_height":            2.8,   # m，普通住宅层高
    "door_height":            2.1,   # m，室内门
    "window_sill_height":     0.9,   # m，普通窗（住宅规范下限）
    "window_height":          1.5,   # m，普通窗
    "bay_window_sill_height": 0.45,  # m，飘窗台高
    "bay_window_height":      1.5,   # m，飘窗窗高
}
```

默认值优先级：`PipelineInput.constraints` 覆盖 > `room_vector` 字段值 > `HOUSE_DEFAULTS`

示例（别墅项目覆盖层高）：
```python
PipelineInput(
    room_vector={...},
    constraints={"room_height": 3.2, "door_height": 2.4}
)
```

**输出数据结构：**
```python
@dataclass
class DoorInfo:
    id: str
    pts: list[list[float]]      # 四角坐标 [[x,z]*4]
    normal: list[float]         # [nx, nz]（由 pts 计算）
    center: list[float]         # 中心点 [x,z]（由 pts 计算）
    width: float                # 宽度 m（由 pts 计算）
    height: float               # 高度 m（输入值或默认值）
    to_room: str | None         # 连通房间 ID

@dataclass
class WindowInfo:
    id: str
    window_type: str            # "normal" | "bay"
    pts: list[list[float]]
    sill_height: float          # m（输入值或默认值）
    height: float               # m（输入值或默认值）
    width: float                # m（由 pts 计算）
    depth: float | None         # m，仅 bay window 有值

@dataclass
class SceneRegion:
    region_type: str            # "living_room" | "bedroom" | ...
    boundary: list[list[float]] # [[x,z], ...] 地板轮廓
    area: float                 # m²（Shoelace 计算）
    height: float               # m（输入值或默认值）
    doors: list[DoorInfo]
    windows: list[WindowInfo]

@dataclass
class SceneUnderstandOutput:
    scene_type: str
    regions: list[SceneRegion]
```

---

### 3.2 MeshBuildStage

**输入：** `SceneUnderstandOutput`

**职责：**
- 纯几何算法，无方案库
- 根据内墙多边形 + 门洞 + 窗洞重建白模 Mesh（无材质）
- 输出供后续 Stage 使用的几何结构

**算法流程：**
1. 内墙轮廓 → 地板面（Polygon mesh）
2. 内墙轮廓 → 墙体（沿 y 轴 extrude，默认层高 280cm）
3. 门洞：在对应墙段开洞（Boolean subtract）
4. 窗洞：按 sill_height + height 在墙段开洞
5. 顶面：平顶 Polygon（不含吊顶装饰，由 HardDecoration 负责）

**输出数据结构：**
```python
@dataclass
class RoomMesh:
    vertices: list[list[float]]   # [[x,y,z], ...]
    faces: list[list[int]]        # [[v0,v1,v2], ...]
    floor_polygon: list[list[float]]  # 地板轮廓 [[x,z], ...]
    wall_height: float            # cm
    door_openings: list[DoorInfo]
    window_openings: list[WindowInfo]

@dataclass
class MeshBuildOutput:
    scene_type: str
    room_mesh: RoomMesh
```

**服务依赖：** `MeshBuilderService`（被 Stage 调用，可单独测试）

---

### 3.3 HardDecorationStage

**输入：** `SceneUnderstandOutput` + `MeshBuildOutput`

**职责：** 硬装方案匹配 + 模型放置

**特征提取（用于方案匹配）：**
- 房间面积、长宽比
- 门数量 / 窗数量
- 房间类型

**方案库：** `hard_decoration_schemes`（待设计）
- 门窗套系（门套/窗套/飘窗组件）
- 吊顶方案（平顶+灯带 为默认）
- 地板/墙纸方案
- 踢脚线方案

**输出数据结构：**
```python
@dataclass
class PlacedAsset:
    asset_id: str | None
    position: list[float]     # [x, y, z] cm
    rotation: float           # Y 轴角度
    role: str                 # "door_frame" | "ceiling" | "floor" | ...

@dataclass
class HardDecorationOutput:
    scene_type: str
    placed_assets: list[PlacedAsset]
    ceiling_height: float     # 实际吊顶高度 cm
    scheme_id: str | None     # 使用的硬装方案 ID
```

**可独立运行：** 是（只需 SceneUnderstand + MeshBuild 输出）

---

### 3.4 HouseLayoutComposeStage

**输入：** `SceneUnderstandOutput` + `MeshBuildOutput` + `HardDecorationOutput`（用于获取吊顶高度/障碍物）

**职责：** 软装 Group 方案匹配 + 布局

**特征提取（两级过滤）：**
- 一级（快速过滤）：面积区间、门数量、窗数量
- 二级（几何相似）：Fourier Descriptor + 结构特征 + Polygon IOU

**方案库：** `group_sample_data_roles.json`（已有）+ `furniture_info`
- 特征向量维度：待确定（当前 9D 待改进）

**布局约束：**
- Group 不得遮挡门洞（通行宽度 ≥ 90cm）
- Group 不得遮挡窗户（落地窗留空）
- Group 锚点在房间内墙 boundary 内

**输出：** 沿用现有 `LayoutOutput` + `PlacedGroup`

**可独立运行：** 是

---

### 3.5 AccessoryStage（可选）

**输入：** `LayoutOutput`（已放置的 placed_groups）

**职责：** 为每个 PlacedGroup 匹配并放置配饰

**特征提取：**
- Group 内已放置软装的局部 Mesh 特征（相对位置 / 尺寸）
- 风格参数

**方案库：** 每个 Group code 独立一套配饰方案库
- 按 Group code 索引
- 方案包含：配饰角色列表 + 相对锚点的位置偏移

**识别依据：** `RoleDefinition.tier == "accessory"` 或 `optional == True`

**可独立运行：** 是（传入已有 placed_groups，跳过布局阶段）

**输出：**
```python
@dataclass
class AccessoryOutput:
    placed_groups: list[PlacedGroup]   # role_assets 已填充配饰 asset_id
```

---

### 3.6 StylizeStage

**输入：** 所有前序 Stage 输出（或独立传入已有布局）

**两种运行模式：**

#### skin_swap（换肤）
- 严格同结构，zero delta
- 纯资产 ID 替换，位置/旋转不变
- 适用：快速换色/换材质预览

#### stylize（风格化）
- 资产替换 + 局部微调
- 位置微调：单 role 级别，不超出 Group 边界
- 布光微调：根据材质/氛围从方案库取参数或自动计算

**替换范围：**
- 硬装资产：墙纸/地板/吊顶方案换一套
- 软装资产：role_assets 中的家具 asset_id
- 配饰资产：配饰 role_assets
- 材质变体：对已有资产应用材质包

**渲染布光配置输出：**
```python
@dataclass
class LightingConfig:
    sun_azimuth: float         # 方位角（度）
    sun_elevation: float       # 仰角（度）
    sun_color_temp: float      # 色温 K
    virtual_lights: list[dict] # 虚拟光源列表（位置/色温/强度/衰减）
    exposure: float
    tone_mapping: str

@dataclass
class StylizeOutput:
    mode: str                  # "skin_swap" | "stylize"
    asset_replacements: dict   # {old_asset_id: new_asset_id}
    position_deltas: dict      # {role_key: [dx,dy,dz,d_rot]}（stylize 模式）
    lighting_config: LightingConfig
    scheme_id: str | None
```

**方案库：** 布光方案库（按房间类型/风格/时段索引）

**可独立运行：** 是

---

## 4. 配套服务层

### 4.1 MeshBuilderService

- 被 MeshBuildStage 调用
- 纯几何算法，无外部依赖
- 接口：`build(region: SceneRegion) -> RoomMesh`

### 4.3 PlacementZoneService

**职责：** 通用模型放置点分析服务。分析任意 3D 模型的 Mesh，识别可用于放置或挂载其他物品的区域，结果持久化到 DB。

**适用范围（跨场景）：**
- 室内：沙发、柜子、搁板、床
- 城市：建筑外墙、货柜、货架
- 野外：树木、山体、石头

**Zone 类型定义：**

| 类型 | 说明 | 典型示例 |
|------|------|---------|
| `stable_top` | 稳定顶面，法向量接近向上，面积 ≥ 阈值 | 桌面、岩石平台、货架层板 |
| `stable_side` | 稳定侧面，垂直/近垂直，有足够面积 | 墙面、柜侧、建筑外墙 |
| `attach_point` | 挂接点，法向量向外的突出点/边缘 | 树枝、栏杆、挑檐 |
| `cavity` | 凹陷区，被其他面包围的内凹区域 | 壁龛、货架格、山洞口 |

**算法流程（通用，不依赖场景类型）：**
1. Mesh 面聚类（按法向量相似度 + 空间邻近）
2. 对每个面簇：计算朝向、面积、是否有上方遮挡（决定可达性）
3. 评分排序，过滤面积过小或不可达的区域
4. 输出结构化 PlacementZone 列表

**数据结构：**
```python
@dataclass
class PlacementZone:
    zone_type: str              # "stable_top" | "stable_side" | "attach_point" | "cavity"
    center: list[float]         # [x, y, z] 区域中心点
    normal: list[float]         # [nx, ny, nz] 法向量（已归一化）
    area: float                 # 面积 cm²
    bounds: list[list[float]]   # 包围框顶点 [[x,y,z], ...]
    stability_score: float      # 0.0~1.0，稳定性/可达性评分

@dataclass
class PlacementZoneResult:
    asset_id: str
    zones: list[PlacementZone]
```

**接口：**
```python
class PlacementZoneService:
    def analyze(self, asset_id: str, mesh_data: dict) -> PlacementZoneResult:
        """先查缓存，命中则直接返回，否则计算后写入 DB。"""
        ...
```

**缓存策略（先查→再算）：**
- 查 `AssetDefinition.computed_features["placement_zones"]`
- 命中 → 反序列化返回
- 未命中 → 运行分析算法 → 写入 `computed_features["placement_zones"]` → 返回

**落库位置：** `AssetDefinition.computed_features` JSON 字段：
```json
{
  "glm": { ... },
  "placement_zones": {
    "zones": [
      {"zone_type": "stable_top", "center": [x,y,z], "normal": [0,1,0],
       "area": 2400.0, "bounds": [...], "stability_score": 0.92}
    ]
  }
}
```

**被调用方：** `AccessoryStage` — 对每个已放置软装 Group 的 role_assets，调用此服务获取可用放置区，结合配饰方案库计算配饰的最终放置坐标。

---


多 domain 方案库检索，domain key 与通用层名对齐：

| domain | 特征向量 | 方案库 |
|--------|---------|--------|
| `base_layer` | 面积/门窗数/长宽比 | 硬装方案库 |
| `layout` | Fourier+结构特征 | group_sample_data_roles |
| `accessory` | Group 局部 Mesh 特征 | 配饰方案库（per group code）|
| `stylize` | 房间类型/风格/时段 | 布光+材质方案库 |

接口：`search(domain: str, feature_vec: list[float], top_k: int) -> list[SchemeMatch]`

---

## 5. 方案库总览

| 方案库 | 当前状态 | 特征维度 |
|--------|---------|---------|
| 硬装方案库 | 待建 | 面积/门窗/房型 |
| 软装方案库 | 已有（group_sample_data_roles.json，9D 待改进） | 房间空间特征 |
| 配饰方案库 | 待建 | Group 局部 Mesh 特征 |
| 布光方案库 | 待建 | 房型/风格/时段 |

---

## 6. 数据流总览

```
PipelineInput (room_vector)
    │
    ▼
SceneUnderstandOutput (regions, doors, windows, area)
    │
    ▼
MeshBuildOutput (RoomMesh)
    │
    ▼
HardDecorationOutput (placed_assets, ceiling_height, scheme_id)
    │
    ▼
LayoutOutput (placed_groups, role_assets filled for main roles)
    │
    ▼ [可选]
AccessoryOutput (placed_groups, role_assets filled for accessory roles)
    │
    ▼
StylizeOutput (asset_replacements, position_deltas, LightingConfig)
```

---

## 7. 数据模型补充与落库策略

### 7.1 Region 补充门窗字段

现有 `Region` 表缺少门窗数据，需新增两个 JSON 字段：

```python
class Region(Base):
    __tablename__ = "region"
    # ... 现有字段 ...
    doors: Mapped[Optional[list]] = mapped_column(JSON)
    # 存储格式：[{"pts": [[x,z]*4], "normal": [nx,nz], "center": [x,z], "width": float}, ...]
    windows: Mapped[Optional[list]] = mapped_column(JSON)
    # 存储格式：[{"pts": [[x,z]*4], "sill_height": float, "height": float, "center": [x,z], "width": float}, ...]
```

> 需配套 Alembic migration。

---

### 7.2 方案库存储策略：JSON 文件，不入库

**决策：方案库以 JSON 配置文件形式存储，不建 DB 表。**

理由：
- 与现有 `house.json`（GroupDefinition）模式一致
- 方案库内容由人工/离线工具维护，不需要在线写入
- 避免过早引入 DB 复杂性

各方案库文件规划：

| domain | 文件路径 | 状态 |
|--------|---------|------|
| `base_layer` | `xasset/data/schemes/hard_decoration.json` | 待建 |
| `layout` | `xasset/data/schemes/` 或复用 `group_sample_data_roles.json` | 已有原始数据，待整理 |
| `accessory` | `xasset/data/schemes/accessory_{group_code}.json` | 待建 |
| `stylize` | `xasset/data/schemes/lighting.json` | 待建 |

`SampleSearchService` 启动时加载所有方案库文件到内存，按 domain 分索引检索。

> `Sample` DB 表保留，用途调整为存储**已生成资产的特征向量**（用于相似资产检索），而非方案库条目。`sample_level` 字段语义不变（object/group/zone/scene），与方案库 domain 无关联。

---

### 7.3 Pipeline 输出落库策略

**原则：Pipeline 只返回计算结果，落库由 Service 层决定（Stage 不写 DB）。**

各 Stage 输出与 DB 的对应关系：

| Stage 输出 | 落库位置 | 说明 |
|-----------|---------|------|
| `SceneUnderstandOutput.regions` | `Region` 表（含新增 doors/windows 字段） | Scene 入库时同步写 |
| `MeshBuildOutput.room_mesh` | `AssetDefinition.raw_data` JSON 字段 | 白模作为 asset_level="zone" 资产存储 |
| `HardDecorationOutput.placed_assets` | `AssetInstance` 表（role 字段区分硬装角色） | scheme_id 存入 `AssetDefinition.metadata_extra` |
| `HardDecorationOutput.ceiling_height` | `AssetDefinition.metadata_extra` JSON | 供后续 Stage 读取 |
| `LayoutOutput.placed_groups` | `GroupInstance` 表（已有，role_assignments 对应 role_assets） | ✅ 无需变更 |
| `AccessoryOutput.placed_groups` | 同上，更新 role_assignments 中配饰字段 | ✅ 无需变更 |
| `StylizeOutput.asset_replacements` | `AssetInstance.overrides` JSON 字段 | 替换记录存为覆盖而非修改原始 |
| `StylizeOutput.lighting_config` | `AssetDefinition.light` JSON 字段 | 已有字段，结构对齐 LightingConfig |

---

### 7.4 Sample 表用途澄清

`Sample` 表定位为**已生成资产的特征向量索引**，用于"相似资产检索"场景，与方案库分离：

```
Sample 表职责：
  scene_type + sample_level → 定位资产类型
  style_vector              → 风格相似度检索
  partition_vector          → 空间分区特征检索
  distribution_vector       → 分布特征检索
  groups / material         → 资产内容摘要

方案库文件职责：
  feature_vec + scheme_data → 输入特征 → 推荐方案
```

---

## 8. 实施优先级建议

| 优先级 | 模块 | 理由 |
|--------|------|------|
| P1 | SceneUnderstandStage（完整实现） | 所有 Stage 的输入基础 |
| P1 | MeshBuildStage + MeshBuilderService | 几何基础，依赖少 |
| P1 | Region 模型补充 doors/windows + migration | SceneUnderstand 落库需要 |
| P2 | HardDecorationStage | 视觉效果最直接 |
| P2 | HouseLayoutComposeStage（完整实现） | 核心功能，当前为 stub |
| P2 | SampleSearchService 多 domain 扩展 | Layout/HardDecoration 依赖 |
| P3 | AccessoryStage | 可选，依赖软装完成 |
| P3 | StylizeStage（完整实现） | 当前为 stub，依赖前序完成 |
| 持续 | 方案库 JSON 文件建设 | 与 Stage 实现并行 |
