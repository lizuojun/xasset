# Artist 方案：LLM × 边界约束的统一场景生成方法

**日期**: 2026-08-31（持续更新，见第 5 节进展记录）
**状态**: 方案统一推进中（living doc，逐步记录讨论结论，不是一次性调研）
**关联**:
- [scene-recognition-from-raw-input](../scene-recognition-from-raw-input/README.md) —— 原始输入识别路线的技术选型调研 + 相关工作综述；架构性结论已内化到本文档（见第 2.1/4 节），不重复
- [learned-layout-with-hard-constraints](../learned-layout-with-hard-constraints/README.md) —— 组合布局的数据驱动打分/生成技术方案参考
- [polygon-encoder-baseline](../polygon-encoder-baseline/README.md) —— 为组合布局提供底层 encoder 方案参考
- [geometry-neural-paradigm](../geometry-neural-paradigm/README.md) —— 更底层的几何神经网络范式综述

> **命名演进说明（2026-09）**：本方案早期以「四阶段」（场景理解 → 边界特征 → 组合布局 → 场景生成）描述，现正式命名为 **Artist**，内部按「轮廓 → 主体 → 细节」的三个工作阶段组织，每个 Stage 内部统一走「LLM（想法）× 边界约束（求解器）」的迭代收敛范式。旧的「四阶段」「边界特征」「组合布局」「表面覆盖」「边界重建」等叫法已废弃，全文以本文术语表为准。

---

## 术语表（2026-09 确立）

### Artist 之名

**Artist** 是本方案「用 LLM 与边界约束共同创作 3D 场景」这一方法论的名称——取自艺术家工作的类比：艺术家分阶段创作（先轮廓、再主体、最后细节），每一笔都在「大脑的想法」与「现实的约束」之间迭代收敛。

| 权威写法 | 含义 | 废弃写法 |
|---------|------|---------|
| **Artist** | 本方案整体名称（LLM × 边界约束生成场景的方法） | 四阶段、画家模型 |
| **Stage** | 工作阶段（六层） | — |
| **LLM** | Stage 内部负责理解与想法的一侧 | 大模型 |
| **边界约束** | Stage 内部负责把想法落地成合法数据的确定性规则与求解器 | 约束、现实的约束 |
| **迭代收敛** | LLM 与边界约束在一个 Stage 内部的反复协作直至定型 | 拉扯、双向拉扯 |
| **想法** | LLM 产出的语义理解与意图选择 | 理解、意图 |
| **阶段产物** | 每个 Stage 的定型结果（= 该 Stage 的输出契约） | 定型结果、数据结果、输出 |
| **求解器** | 边界约束侧把想法落地成合法数据的确定性工具 | 落地器、确定性求解器 |
| **校验门** | 边界约束侧对求解结果的最终合法性护栏 | — |
| **产品形态** | 每个 Stage 对外交付的形态（插件 / 软件 / 页面） | 形态、宿主包装 |
| **输入输出契约** | 每个 Stage 的输入与输出的唯一权威 schema 定义 | IO 契约、产物 schema |

### 六层 Stage 与「轮廓 / 主体 / 细节」的映射

| 阶段 | Layer | 工作内容 |
|------|-------|---------|
| **轮廓** | `understand` | 语义理解：场景 / 区域 / 类型 |
| **轮廓** | `geometry` | 边界 / 骨架：2D → 3D 几何 |
| **主体** | `layout` | 主体造型：组合布局 |
| **主体** | `surface` | 表面覆盖：铺贴 |
| **细节** | `accessory` | 点缀：小件散布 |
| **细节** | `stylize` | 风格化：材质 / 灯光 / 相机 |

### 三个轮廓语义术语

下列三个概念描述**区域轮廓上的语义**，用**场景中性**术语统一（house 的"门/窗"在 urban/wild 没有对应物，沿用会让跨场景讨论失焦）：

| 统一术语 | 定义 | 承载字段 | 不再使用 |
|---------|------|---------|---------|
| **轮廓语义** | 挂在区域轮廓上的语义信息的总称，分**开口**与**固定边**两类（见下表） | `doors` / `windows` / `structural_edges`（及提案的 `boundary_features`） | "边界特征"、"墙体特征"、"门窗字段" |
| **开口** | 轮廓上可开洞、可通行的位置 | house：门 / 窗；urban：路网出入口 / 交叉口；wild：水岸线交叉 / 地形过渡带 | "边界特征"（旧伞形统称） |
| **固定边** | 轮廓上不可位移、不可编辑的边 | house：承重墙；urban：用地红线 / 道路红线；wild：硬性地形边界 | "固定边"沿用（无更优区分） |

> 「轮廓语义」是**数据概念**（区域轮廓上的门/窗/固定边等），与 Artist 机制里的「边界约束」（LLM 之外的确定性规则 + 求解器）是**两个完全不同的概念**，不要混淆。字段保持独立（`doors`/`windows` 与 `structural_edges` 分开存储），各自按 scene_type 填词表。

---

## 0. 目标与背景

目前 xasset pipeline 是「6 层 × 3 scene_type」矩阵（understand/geometry/layout/surface/accessory/stylize，house/urban/wild），同一层不同 scene_type 各自实现算法。层与层之间、场景与场景之间目前只统一了 Stage 接口，没有统一的算法骨架。

现在要推进的收敛，是在这个基础上再提一层抽象：把一个 3D 场景的生成，组织成一条 **Artist** 方法论——不论 house/urban/wild，也不论 region_type 具体是"客厅"还是"街区绿地"还是"山坡草甸"，都遵循同一套「LLM × 边界约束」的创作方式，只是每个 Stage 内部的专用算法（想法产生方式、约束规则集）按 region_type / scene_type 热插拔替换。

这套方法有两条贯穿性的设计要求，共同构成本文档要记录、推进、逐步达成一致的"统一方案"：

1. **LLM 与边界约束分工**——每个 Stage 都用「LLM 出想法 → 边界约束求解落地 → 校验门护航」这同一个动作；LLM 承担语义理解与选择（强项），边界约束承担精确几何 / 数值的合法化（弱项由约束补上）
2. **贯穿全流程的「约束校验 + 自然语言迭代编辑」能力**——任何要呈现给用户或送入下游的结果都必须先过校验（4.1 节，无例外），且任何一阶段的结果都能被后续提示词继续编辑

**这不是推翻现有六层设计**，而是在「六层」这个渲染管线式的分层之上，重新组织出一条统一的方法论骨架。

**文档边界说明**：本文档是架构决策的唯一权威来源（living doc）。[scene-recognition-from-raw-input](../scene-recognition-from-raw-input/README.md) 早先探索 understand 层识别时提出的产品形态设计已内化、泛化到本文档（见第 4 节），该文档现在只保留三大类输入路线的技术选型调研和相关工作文献综述这类"纯研究"内容。

---

## 1. Artist：一条统一的方法论

```
[原始输入]        LLM 侧（想法）              边界约束侧（求解 + 校验）
   │                ┌──────────┐              ┌──────────────────┐
   ▼                │  理解     │  迭代收敛    │  求解器 → 合法几何 │
 Stage 1 understand │  选择     │ ◄──────────► │  校验门 → 合法性护栏 │
   │                └──────────┘              └──────────────────┘
   ▼                 （每个 Stage 内部重复同一个「想法 × 约束」循环）
 Stage 2 geometry
   ▼
 Stage 3 layout  ... 其余 Stage 同构
   │
   ▼
  场景生成（数据结果）= 可渲染场景
```

每个 Stage 内部都是同一个模式：

```
想法（LLM 产出语义/意图选择）
   ↓  求解器（边界约束把想法落地成合法数据）
   ↓  校验门（合法护栏）
   ↓  未过 → 回拉新想法 → 再求解……迭代收敛
   ↓  通过 → 本阶段定型，进入下一 Stage
```

**Stage 之间的递进**是「轮廓 → 主体 → 细节」：

- **轮廓**（understand → geometry）：先把"是什么、大致长什么样"定下来——语义理解 + 边界骨架
- **主体**（layout → surface）：把主要内容/形体填充出来——组合布局 + 表面覆盖
- **细节**（accessory → stylize）：最后打磨——点缀 + 风格化

**前几层产出的是数据，最后把数据变成场景。**

### 1.1 各 Stage 的 LLM 任务形态

| Stage | LLM 任务类型 | LLM 做什么 | 边界约束做什么 | 阶段产物 |
|-------|-------------|-----------|--------------|---------|
| `understand` | 语义理解 / 分类（LLM 强项） | 判定 scene_type、划分区域、判定 region_type、推断区域关系 | 词表闭集校验、依赖归一化 | 区域列表 + 语义标注 |
| `geometry` | 结构化抽取 + 几何生成（LLM 中等，坐标是短板） | 给出边界大致形状、开口大致位置 | 多边形闭合 / 去噪 / 简化、几何合法化 | SceneRegion 的边界骨架 + 3D 网格 |
| `layout` | 离散候选选择 + 关系推理（LLM 中等） | 选"摆哪个组、摆哪、朝哪" | 碰撞 / 净宽 / 越界校验、合法候选空间构造 | PlacedGroup 列表 |
| `surface` / `accessory` / `stylize` | 资产语义匹配 + 风格选择（LLM 强项） | 给 role 选资产、定风格、内部搭配 | 尺寸 / 覆盖 / 归属校验、网格构建 | 表面覆盖 / 点缀 / 风格化结果 |

**为什么这样分工契合 LLM 能力**：LLM 的任务类型从"强的语义任务"逐步过渡到"弱的精确几何 / 数值任务"，而边界约束恰好补上后者——语义阶段约束起闭集 / 边界兜底，几何阶段约束集最厚（把 LLM 的粗略结构拉回合法范围）。

---

## 2. SceneRegion schema 泛化（现只覆盖 house）

### 2.1 逐字段对照

| 字段 | 是否可泛化到 urban/wild | 说明 |
|------|----------------------|------|
| `boundary` / `area` | ✅ | 任意区域都有边界多边形和面积 |
| `region_type` | ❌ | 词表硬编码 house 房间类型，urban/wild 无对应词表 |
| `height` | ❌ | 默认值绑定 house 层高常量；urban 是建筑高度、wild 是地形海拔，语义不同 |
| `doors` / `windows` | ❌ | house 专属的开口概念；urban 是路网出入口、wild 是地形过渡带 |
| `structural_edges` | ❌ | "承重墙"是建筑概念，urban/wild 无对应物 |

**结论：现在的 `SceneRegion` 是 house 的 schema 被暂时挂在通用命名之下。** 字段级语义并未真正打通，RecognitionService 的输出契约现在也只能对齐 house。

### 2.2 具体设计提案（尚未编码验证）

**2.2.1 region_type 词表提案**

| scene_type | region_type 候选词表 |
|-----------|---------------------|
| urban | `road` / `building_footprint` / `green_space` / `plaza` / `parking_lot` |
| wild | `mountain` / `water_body` / `grassland` / `forest` / `rock_formation` / `bare_ground` |

**2.2.2 `doors` / `windows` → 通用 `BoundaryFeature`（轮廓语义）**

```python
@dataclass
class BoundaryFeature:
    id: str
    feature_type: str                    # house: "door"|"window"；urban: "road_entrance"|"intersection"|"building_entrance"；wild: "terrain_transition"|"waterline_crossing"
    pts: list[list[float]]               # 沿边界的几何
    width: float
    seg_start: list[float] | None = None
    seg_end: list[float] | None = None
    to_region: str | None = None
    to_region_type: str | None = None
    attrs: dict = field(default_factory=dict)  # 类型特定附加信息
```

**迁移策略：只新增，不破坏 house 现有实现**——`door/window` 消费方现存多处，全部改名成本高。方案：`SceneRegion` 新增 `boundary_features`，urban/wild 直接用；house 保持 `doors`/`windows` 不变，两套并存。渲染器分支成本可接受，先落地 urban/wild。

**2.2.3 `structural_edges` → 语义泛化（固定边）**

| scene_type | 固定边含义 |
|-----------|-----------|
| house | 承重墙 |
| urban | 用地权属边界 / 道路红线 |
| wild | 硬性地形边界（悬崖边缘、水岸线） |

字段名不强制改，只需补规则："固定边标记的边界段，编辑操作不能使其位移或删除"。

**2.2.4 `height` 语义按 region_type 区分，取消统一默认值**

`height: float | None = None`，语义按 scene_type + region_type 解释。

---

## 3. 热插拔模块边界

每个 Stage 内部，不同 region_type 对应不同的"专用算法"，但对外接口（输入输出契约）一致——模块可独立替换，不影响上下游。

### 3.1 六层 Stage 的实现现状

| Stage | house | urban | wild |
|-------|-------|-------|------|
| `understand` | `SceneUnderstandStage`（语义 + 结构解析 + `vector_normalize.py`；通用 `BoundaryFeature` 未落地） | 同 house（同一份代码，词表见 2.2） | 同 house |
| `geometry` | `MeshBuildStage`（已落地） | ❌ 缺 | ❌ 缺 |
| `layout` | `HouseLayoutComposeStage`（`placed_groups` 恒空，算法待 Artist 重做） | ❌ 缺 | ❌ 缺 |
| `surface` / `accessory` / `stylize` | 三场景共享（空桩 / 待实现） | 同左 | 同左 |

**关键事实**：

- `understand` 在三个 scene_type 之间是同一份代码（都是 `SceneUnderstandStage`），差异只在数据（schema 词表 / 字段语义）
- `layout` 只有 house 有 Stage 类骨架（且是 stub），urban/wild 连代码文件都不存在
- `geometry` 是唯一有实际落地内容的一段（`MeshBuildStage`），但规则式网格算法已在算法重做中清理，待 Artist 范式重做

### 3.2 横向 + 纵向两个热插拔维度

- **横向**：同一 Stage 换到不同 scene_type（接口相同、实现替换）
- **纵向**：同一 scene_type 下，实现方法按技术成熟度 / 数据可用性切换（如 layout 的规则模板 vs 数据驱动打分，见 [learned-layout-with-hard-constraints](../learned-layout-with-hard-constraints/README.md)）

### 3.3 LLM × 边界约束的原生接口

每个 Stage 都要能被表述成同一个动作：

```
该 Stage 的输入 + 用户提示词 + 该 Stage 的边界约束集
                    ↓  LLM（想法）
         阶段产物（schema 固定、语义明确）
                    ↓  校验门（4.1 节，强制执行）
      通过 → 呈现给用户 / 进下一 Stage
      不通过 → 拒绝并反馈（要求改提示词 / 给可行范围）
```

**「想法」与「边界约束」的双重关系**：

1. **边界约束进 prompt 引导**——把规则显式告诉 LLM，降低它产出非法结果的概率
2. **边界约束由校验门强制检验**——不因为"prompt 里已经说过"就跳过校验

两者是同一套规则集的两种用法：prompt 引导提高一次通过率，校验门保证最终不放过。

---

## 4. 约束校验与自然语言编辑：跨 Stage 的统一能力

### 4.0 核心判断：不追求单次高还原，先画"速写轮廓"

每个 Stage 的专用算法单次产出都不可能完全贴合用户意图。**把"提升单次准确率"当作唯一目标是不现实的**，更贴切的类比是艺术家的速写：先画大致轮廓，细节留给后续阶段填充和用户反复调整。

也就是说，每个 Stage 的产出都不是"最终答案"，而是一份**可编辑的初稿**——算法只需把语义搭对（区域数量类型对、边界大致形状对、该有的 Group 都摆上、资产类型风格基本对），精修交给约束校验和用户自然语言调整。这个思路把"生成准确率"压力从算法侧一部分转移到"约束校验 + 人工可控二次调整"上。

### 4.1 统一原则：约束校验是强制默认项，没有例外

无论候选结果来自专用算法还是自然语言编辑，**任何要呈现给用户或送入下游的结果，必须先经过约束校验**。这条对所有 Stage、所有专用算法实现，都不允许有例外。

- **自身可靠的专用算法**（如 layout 的几何合法候选构造）：输出常直接通过，但校验门**依然执行**，只是"跑一遍确认"
- **识别 / 生成 / 编辑**（LLM 输出不确定）：校验门是真正会拦截、会拒绝的一道关卡

**结论**：不区分"要不要校验"，只区分"大概率通过 or 大概率拦截"——但校验动作本身，全部路径都不可省略。

### 4.2 各 Stage 的约束 / 编辑内容对照

| Stage | 约束示例 | 编辑操作示例 |
|-------|---------|-------------|
| `understand` | 区域数量合理 / region_type 在词表内 / 关系自洽 / priority 合法 | rename_region_type / merge_regions / split_region / set_priority |
| `geometry` | 闭合 / 不自交 / 面积区间 / 开口落边界 / 区域不重叠 / 最小净宽 / 固定边不可位移 | resize_region / move_opening / merge_region / split_region |
| `layout` | Group 不越界 / 不碰撞 / 留净宽 / 必需 Group 齐备 | move_group / resize_group / replace_group / add_group / remove_group |
| `surface` / `accessory` / `stylize` | 资产尺寸在界内 / 不碰撞 / 开洞不越界 / 材质覆盖完整 | replace_role_asset / adjust_sub_position / change_style |

> `understand` 的约束是最薄的一层——语义正确性靠"词表内 + 关系自洽"这类弱校验兜底，不像 `geometry` 有硬几何约束。这是已知不对称，后续若语义错误频繁需拦截再补强。

`geometry` 约束展开（现有 `tools/geometry/normalize.py` 只做了去噪和 CCW 绕向，缺以下校验）：

| 约束项 | 现状 | 需新增 |
|--------|------|--------|
| 闭合性 | ✅ | 无 |
| 去噪 / 共线简化 | ✅ | 无 |
| 绕向统一 (CCW) | ✅ | 无 |
| 自相交检测 | ❌ | 简单多边形校验（shapely `is_simple`） |
| 面积合理区间 | ❌ | 按 region_type 定区间 |
| 开口落在边界上 | ❌ | 开口必须落在某条边界段上 |
| 区域间不重叠 | ❌ | 多 Region 边界互不重叠 |
| 最小可通行宽度 | ❌ | 门宽 / 走廊净宽阈值 |
| 固定边不可位移 | ❌ | structural_edges 标记的边不可位移 / 删除 |

**通用校验 / 编辑引擎的工程决策**：值得把「候选产出 → 校验门 → 通过呈现 / 不通过拒绝」这个闭环抽成跨 Stage 复用的引擎（输入 = 当前数据结构 + 该 Stage 的约束规则集 + 编辑操作集），各 Stage 只需提供自己的规则集和操作集——专用算法是否"自带合法性"只影响闸门拦截率，不影响闸门存在。

编辑指令解析闭环（跨 Stage 通用）：

```
自然语言指令
  → LLM 解析成结构化编辑操作
  → 在当前数据结构上应用（纯几何/数据变换）
  → 重新跑校验门
  → 失败 → 返回自然语言解释（如"放大后与客厅重叠"）
  → 通过 → 更新数据结构，刷新对照展示
```

### 4.3 结果核验：可视化对照

用户需要直观确认"生成结果对不对"，各 Stage 都适用同一机制：把当前结果渲染成简笔画 / 线框图，与原始输入或前一 Stage 结果并排 / 叠加对照：

- `understand`：结构化摘要（"识别为：3室2厅，客厅26㎡朝南"）
- `geometry`：边界线框图叠加原图
- `layout`：区域线框图上叠加 Group 位置框
- `surface` / `accessory` / `stylize`：叠加资产缩略图 / 风格标签，几何重建后给三维预览

### 4.4 技术选型标准的连带调整

因为每个 Stage 都有 4.1 强制校验兜底 + 4.0 "速写轮廓"预期 + 自然语言编辑闭环收尾，专用算法的选型标准都发生同一种偏移：**不选精度最高的，选"能快速产出语义正确初稿"的**。

- `understand`：可先规则 / 词表兜底，语义错误易靠一次编辑修正
- `geometry`：优先推理成本低、语义理解强的方案（多模态 LLM 给粗略结构，坐标不准靠约束收敛）
- `layout`：不必一次摆到位，只要必需 Group 齐、大致不冲突
- `surface` / `accessory` / `stylize`：资产不必风格 100% 匹配，用编辑操作直接换

---

## 5. 当前进展 / 待推进事项（持续更新）

> **命名演进说明**：本文档早期以"四阶段"（场景理解 → 边界特征 → 组合布局 → 场景生成）描述，2026-09 正式命名为 Artist（轮廓 → 主体 → 细节 + LLM × 边界约束）。历史记录保留原措辞，新增记录一律用 Artist 术语。

- [x] 2026-08-31：确立统一流程框架（当时为三段划分）
- [x] 2026-08-31：确立"约束校验强制默认、无例外"原则
- [x] 2026-08-31：内化并泛化 [scene-recognition](../scene-recognition-from-raw-input/README.md) 的产品形态结论（速写轮廓、约束校验清单、编辑闭环、可视化对照、技术选型标准）
- [x] 2026-08-31：完成 urban/wild schema 提案（region_type 词表、`BoundaryFeature` 通用化、`structural_edges` 语义泛化、`height` 取消默认值）
- [x] 2026-09-22：确立场景中性术语（边界重建 / 边界特征 / 组合布局）——注：这些旧术语已于 2026-09 被 Artist 术语表取代，仅作历史记录
- [x] 2026-09：骨架由三段 / 四阶段正式命名为 **Artist**（轮廓 → 主体 → 细节，LLM × 边界约束迭代收敛）；废弃「四阶段」「边界特征」等旧叫法
- [ ] 各 Stage 的阶段产物 schema 需细化到字段级（understand 的"区域间关系"尚无具体字段设计）
- [ ] `understand` 内部语义 + 结构是否拆成两个 Stage，还是类内分方法，待决策
- [ ] urban/wild schema 提案的开放问题（region_type 词表扩充、`BoundaryFeature` 是否补 house 适配器）
- [ ] layout 的 urban/wild Group 库完全空白（group 定义暂无对应）
- [ ] layout 约束满足式算法未实现（`HouseLayoutComposeStage` 是 stub，house 也缺）
- [ ] surface/accessory/stylize 的 Group 内容填充"生成 vs 检索"选型未定；三层在三个 scene_type 下全是空桩
- [ ] 跨 Stage 复用的约束校验 / 自然语言编辑引擎待细化验证

---

## 6. 与其他调研文档的分工

- **[scene-recognition-from-raw-input](../scene-recognition-from-raw-input/README.md)**：专注原始输入识别路线的技术选型调研（结构化图纸 / 自然语言 / 通用图片）+ 文献综述
- **[learned-layout-with-hard-constraints](../learned-layout-with-hard-constraints/README.md)**：专注组合布局的数据驱动打分 / 生成模型方案
- **[polygon-encoder-baseline](../polygon-encoder-baseline/README.md)**：为组合布局提供底层 encoder 方案参考
- **[geometry-neural-paradigm](../geometry-neural-paradigm/README.md)**：更底层的几何神经网络范式综述
- **本文档**：唯一的架构决策权威来源，记录"哪些是通用能力（只实现一次）、哪些是按 region_type 热插拔的专用模块"，持续追踪整体推进状态。
