# P0：资产数据模型 & Schema 设计

**日期：** 2026-03-26
**状态：** 已确认
**依赖：** 无
**被依赖：** P1 / P2 / P3 / P4 / P5

---

## 一、核心概念

### 状态机

Asset Definition 有三种状态：

```
draft → published → deprecated
```

- `draft`：AI 可操作的原始状态，使用 `raw_data`
- `published`：对外交付状态，`packaged_data` 已填充，`Listing` 可上架
- `deprecated`：不再维护的历史版本，触发条件：创作者主动废弃或被新版本替代

**deprecated 规则：**
- 已有的 `AssetInstance` 引用仍然有效，不强制失效
- 关联的 `Listing` 自动下架（`listed` 置为 false）
- 不可再创建新的 `AssetInstance` 引用该 Definition

### 四种粒度

Asset Definition 是统一结构，粒度由 `asset_level` 区分：

```
object   单体模型        一把椅子、一棵树、一块石头
group    功能组合        会客组、街道组、林地组
zone     区域/房间       客厅、商业街区、林地区域
scene    完整场景        一栋房子、一片野外、一座城市
```

每一层都是 `AssetDefinition`，都有 `canonical_children`，支持递归嵌套、引用和交易。

### Definition vs Instance

```
AssetDefinition     描述"资产是什么"，全局唯一，可被多个场景引用
AssetInstance       描述"资产在某个上下文里怎么用"，记录空间变换和上下文
```

类比 USD 的 Reference + Override，或游戏引擎的 Prefab + Instance。

`AssetDefinition.canonical_children` 是该 Definition 的**默认典型排列**（模板实例），其中 `scene_id` 为 null。当 Definition 被放入具体场景时，会创建新的 `AssetInstance`，赋予实际的 `scene_id`。

---

## 二、Asset Definition

```yaml
AssetDefinition:
  # 标识
  id:             UUID
  name:           string
  asset_level:    object | group | zone | scene
  state:          draft | published | deprecated

  # 分类
  scene_type:     urban | wild | house | ...    # 可扩展注册
  object_type:    string                         # 类型路径，如 house/room/furniture/sofa
  role_hints:     [string]                       # 可担任的角色列表（object 级）

  # 描述
  style:          string                         # 风格标签，如 "东方古典"
  tags:           [string]                       # 自由标签，用于检索
  source:
    type:         image | text | manual
    ref:          string                         # 原图 URL 或文字描述

  # 数据
  raw_data:
    geometry_url:   string
    metadata_url:   string
    thumbnail_url:  string
  packaged_data:                                 # 发布后填充
    usd_url:        string
    gltf_url:       string                       # GLTF 导出（供非 Omniverse 工具使用）
    watermark_id:   string
    checksum:       string

  # 默认典型子资产排列（group / zone / scene 级，scene_id 为 null）
  canonical_children: [AssetInstance]

  # 布局与光照（zone / scene 级）
  layout:
    regions:      [Region]
    groups:       [GroupInstance]
  light:                                         # 创作者输入：期望的光照设定
    params:       object
    natural:      object                         # 自然光偏好（朝向、色温等）

  # 派生特征（算法计算输出）
  computed_features:
    vectors:
      style:        [float]                      # 风格特征向量
      partition:    [float]                      # 场景/区域功能划分向量（zone/scene 级）
      distribution: object                       # 功能组内角色尺寸分布向量（group 级）
    affinity:       [UUID]                       # 常见搭配资产（AssetDefinition.id 列表）
    geometry:
      bounds:       object                       # AABB/OBB 包围盒
      parts:        [object]                     # 部件划分（object 级）
      surfaces:     [object]                     # 承载面（object 级）
      interactions: [object]                     # 交互点（object 级）
      semantics:    [object]                     # 语义标签（zone/scene 级）
      density:      [object]                     # 密度分布（zone/scene 级）
    physics:
      collision:    object                       # 碰撞体（object 级）
      material:     string                       # 物理材质类型（object 级）
    navigation:
      navmesh:      object                       # 导航网格（zone/scene 级）
      flow:         object                       # 动线热力图（zone/scene 级）
    lighting:                                    # 算法计算输出：分析结果
      params:       object                       # 最佳打光参数
      natural:      object                       # 自然光分析结果（zone/scene 级）
    rendering:
      lod:          [string]                     # LOD 层级引用
      uv:           object                       # UV 特征
      occlusion:    object                       # 遮挡剔除

  # 商业化
  commerce:       CommerceMetadata

  # 时间戳
  created_at:     datetime
  updated_at:     datetime
  created_by:     UUID
```

> **`light` vs `computed_features.lighting` 区别：**
> - `light`：创作者输入，表达期望的光照意图（如"需要暖色自然光"）
> - `computed_features.lighting`：算法分析输出（如自动计算的最佳灯光参数）

---

## 三、Asset Instance

```yaml
AssetInstance:
  id:             UUID
  definition_id:  UUID                           # 引用的 AssetDefinition.id

  # 空间变换
  # 坐标系：Y-up 右手坐标系，与 USD / Omniverse 默认一致，单位：米
  position:       [x, y, z]                      # Y 为高度轴
  rotation:       [qx, qy, qz, qw]              # 四元数
  scale:          [sx, sy, sz]

  # 上下文
  # scene_id：始终指向根场景 AssetDefinition.id（整个层级共享同一 scene_id）
  # parent_id：直接父 AssetInstance.id，null 表示根节点
  scene_id:       UUID | null                    # canonical_children 中为 null
  parent_id:      UUID | null

  # 组合信息
  group_id:       UUID | null                    # 所属 GroupInstance.id
  role:           string | null                  # 在 Group 中的角色名

  # 覆盖（类似 USD Override）
  overrides:      object
```

---

## 四、场景类型体系

```yaml
SceneTypeRegistry:
  urban:
    sub_types: [ road, park, build, yard ]
  wild:
    sub_types: [ terrain, stone, plant, water, sky, underwater ]
  house:
    sub_types: [ room, yard, stair ]
  # 可扩展注册：dungeon / vehicle / ...

# object_type 用路径表示层次，例如：
#   house/room/furniture/sofa
#   house/room/furniture/table/dining
#   urban/build/layer
#   wild/plant/tree/conifer

# layout 与 light 是跨类型通用描述层，挂在 zone / scene 级 Asset 上
```

---

## 五、Spatial Composition System

### Sample（参考方案库）

```yaml
Sample:
  id:             UUID
  scene_type:     string
  sample_level:   group | zone | scene           # 方案对应的粒度级别
  style:          string
  score:          int
  scale_range:    [min, max]                     # 适用尺度范围（米）
  vectors:
    style:        [float]
    partition:    [float]
    distribution: object
  groups:         [GroupInstance]
  material:       object
  source_id:      UUID | null                    # 溯源，引用原始 AssetDefinition.id
```

### GroupDefinition（功能组定义）

```yaml
GroupDefinition:
  id:             UUID
  name:           string
  code:           int                            # 唯一编码
  scene_types:    [string]                       # 适用场景类型列表
  anchor_role:    string
  roles:          [RoleDefinition]
  templates:      [Template]
```

### RoleDefinition（角色定义）

```yaml
RoleDefinition:
  name:           string
  tier:           anchor | support | fill | accent
  asset_types:    [string]                       # 可担任此角色的 object_type 路径列表
  count:          [min, max]
  size_range:     { w: [min,max], h: [min,max], d: [min,max] }
  optional:       bool
```

### Template（布局模板）

```yaml
Template:
  id:             UUID
  name:           string
  placement_mode: deterministic | rule_based | procedural
  sequence:       [role_name]                    # 放置顺序（先 anchor，再依次其他角色）
  placements:
    - role:       string
      position:   object                         # 三种 mode 共用，内容按 mode 解释
      rotation:   object
      count:      [min, max]
  total_count:    int                            # 所有角色 count.max 之和的上限，用于资源预算
```

**placement_mode 说明：**
- `deterministic`：固定相对坐标，室内家具布局使用
- `rule_based`：沿线/沿面约束，urban 场景使用
- `procedural`：密度场 + 分布函数，wild 场景使用

对外接口统一，算法实现按 mode 注册，内部可独立迭代。

### Region（功能分区）

```yaml
Region:
  id:             UUID
  type:           string                         # 会客区|就餐区|商业区|林地区 ...
  boundary:       [point]                        # 多边形边界
  groups:         [GroupInstance]
  vectors:
    partition:    [float]
    distribution: object
```

### GroupInstance（组的实例引用）

```yaml
GroupInstance:
  id:             UUID                           # GroupInstance 自身标识，可被引用
  definition_id:  UUID                           # 引用 GroupDefinition.id
  position:       [x, y, z]
  rotation:       [qx, qy, qz, qw]
  scale:          [sx, sy, sz]
  role_assignments:
    - role:       string
      instance_id: UUID                          # 对应的 AssetInstance.id
```

---

## 六、商业化元数据

### 整体分层

```
Asset Definition
  └── CommerceMetadata      内部：权利、版本、水印、Credit 价值、Listing 引用

Listing                     外部：市场标的、授权、定价（独立实体）

PlatformConfig              平台级配置：Credit ↔ 货币汇率、平台抽成比例
```

### CommerceMetadata

```yaml
CommerceMetadata:
  # 所有权与溯源
  owner_id:         UUID
  origin_id:        UUID | null                  # 衍生自哪个 AssetDefinition.id

  # 版本
  version:          string                       # 语义版本，如 1.0.0
  changelog:        string
  version_history:  [UUID]                       # 历史版本 AssetDefinition.id 列表

  # 水印
  watermark:
    id:             string
    method:         geometry | texture | metadata
    verified:       bool

  # 交易许可
  license:
    tradeable:      bool                         # 是否可上架
    partial:        bool                         # 子资产是否可拆分交易
    transferable:   bool                         # 购买后是否可转售

  # 内在价值（Credit，整数）
  credit:
    # 中间计算维度（浮点，算法内部使用）
    geometry_quality:
      polygon_count:        int
      texture_resolution:   int
      uv_quality:           float
    feature_completeness:
      basic:      float
      physics:    float
      navigation: float
      rendering:  float
    level_weight:     float                      # object=1x, group=Nx, zone=Mx, scene=Lx
    iteration_count:  int                        # AI 精修次数
    originality:      float                      # 1.0=原创，<1.0=衍生
    # 最终值（整数，对外暴露）
    total:            int                        # 算法合成后取整
    manual_adjust:    int                        # 人工校正量
    final:            int                        # total + manual_adjust

  # Listing 引用（上架后填充）
  listing_id:       UUID | null                  # 引用 Listing.id，null 表示未上架
```

### Listing（市场交易标的）

```yaml
Listing:
  id:           UUID
  title:        string
  type:         asset | ip_bundle

  # 交易标的
  targets:
    - asset_id:     UUID                         # AssetDefinition.id
      asset_level:  object | group | zone | scene

  # IP Bundle 专有
  ip:
    name:       string
    cover_id:   UUID
    asset_ids:  [UUID]                           # AssetDefinition.id 列表

  # 定价
  credit_price:     int                          # 售价（Credit 单位）
  license_type:     exclusive | non_exclusive | personal | commercial
  transferable:     bool
```

### PlatformConfig（平台级配置，独立管理）

```yaml
PlatformConfig:
  exchange_rate:    int                          # 1 Credit = N 分（最小货币单位）
  revenue_share:    float                        # 平台抽成比例，如 0.20 = 20%
  currency:         string                       # CNY | USD
```

### 交易流程

```
创作者发布 Asset
  → credit.total 自动计算 → 人工校正 → credit.final 确定
  → 创作者创建 Listing，设定 credit_price 和 license_type
  → CommerceMetadata.listing_id 指向该 Listing
  → 平台审核 → Listing 上架

买家购买
  → 支付 credit_price 个 Credit
    （或按 PlatformConfig.exchange_rate 换算为货币，整数，最小货币单位）
  → 平台按 PlatformConfig.revenue_share 抽成
  → 买家获得 license，按 license_type 使用资产
```

---

## 七、物理承载形式

### 各阶段数据形式

```
输入（图像 / 文字描述）
    │
    ▼
AI Pipeline JSON（OSS 临时暂存）
  stage1_scene.json      场景类型、划分、语义标签
  stage1_terrain.obj     地形几何
  stage2_layout.json     Region / Group / Instance 空间排列
  stage2_models.json     Instance 对应的模型来源
  stage3_style.json      风格化参数、材质映射
  stage3_lighting.json   光照参数
    │ 汇总写入
    ▼
平台数据库（元数据 + 关系）
+ 向量数据库（computed_features.vectors）
+ OSS（几何文件 / 贴图 / 缩略图）
    │ 发布打包
    ▼
OSS packaged/（USD + GLTF）
    │ 导入
    ▼
Omniverse / 外部工具
```

### 数据库表结构

```
asset_definition        主表
asset_instance          实例表
asset_commerce          商业化表
asset_version_history   版本链表
group_instance          组实例表
listing                 市场标的表
platform_config         平台配置表（汇率、抽成比例）
sample                  参考方案表（PostgreSQL + pgvector）
```

### Spatial Composition System 存储方案

| 实体 | 形式 | 原因 |
|------|------|------|
| GroupDefinition / RoleDefinition / Template | **JSON 配置文件**（git 管理，启动时加载内存） | 相对静态的规则配置，与代码一起版本控制，字段结构按 DB schema 设计，后续迁移零成本 |
| Sample 库 | **PostgreSQL + pgvector** | 持续增长、需要向量相似度检索、运行时频繁写入 |

### OSS 目录结构

```
raw/          原始几何（OBJ / PLY / 点云）、贴图（PNG / EXR）
packaged/     USD 文件（含自定义元数据和水印）、GLTF 文件
thumbnails/   预览图
pipeline/     AI Pipeline 各阶段临时 JSON 文件
```

### USD 元数据嵌入（对接 Omniverse）

P0 商业化元数据嵌入 USD 自定义 metadata 层：

```
USD CustomData:
  xasset:asset_id
  xasset:owner_id
  xasset:version
  xasset:watermark_id
  xasset:license_type
```

USD Prim 层次结构对应 `canonical_children` 嵌套关系，Instance 对应 USD Reference + Override。

---

## 附录：字段适用级别速查

| 字段 | object | group | zone | scene |
|------|--------|-------|------|-------|
| role_hints | ✓ | | | |
| canonical_children | | ✓ | ✓ | ✓ |
| layout / light | | | ✓ | ✓ |
| vectors.partition | | | ✓ | ✓ |
| vectors.distribution | | ✓ | | |
| geometry.parts / surfaces / interactions | ✓ | | | |
| geometry.semantics / density | | | ✓ | ✓ |
| physics.collision / material | ✓ | | | |
| navigation.navmesh / flow | | | ✓ | ✓ |
| computed_features.lighting.natural | | | ✓ | ✓ |
