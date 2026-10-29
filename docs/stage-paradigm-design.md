# Stage 范式化设计：Artist × 产品形态

> 状态：设计草案 v5（术语统一版），待评审确认后实施
> 日期：2026-09
> 关联：
> - `docs/algorithm-rebuild-plan.md` —— 算法全面重做总纲
> - `research/unified-scene-pipeline/README.md` —— 术语表 + 约束校验原则
> - `docs/pipeline-map.md` —— 六层管线现状

---

## 术语表（本文档权威写法）

| 权威写法 | 含义 | 废弃写法 |
|---------|------|---------|
| **Stage** | 工作阶段（六层） | stage |
| **Artist** | 每个 Stage 内部「LLM × 边界约束」迭代收敛的工作方式 | 画家模型、画家/雕塑家模型 |
| **LLM** | Stage 内部负责理解与想法的一侧 | 大模型 |
| **边界约束** | Stage 内部负责把想法落地成合法数据的确定性规则与求解器 | 约束、现实的约束 |
| **迭代收敛** | LLM 与边界约束在一个 Stage 内部的反复协作直至定型 | 拉扯、双向拉扯 |
| **想法** | LLM 产出的语义理解与意图选择 | 理解、意图 |
| **阶段产物** | 每个 Stage 的定型结果（= 该 Stage 的输出契约） | 定型结果、数据结果、输出 |
| **求解器** | 边界约束侧把想法落地成合法数据的确定性工具 | 落地器、确定性求解器 |
| **校验门** | 边界约束侧对求解结果的最终合法性护栏 | — |
| **产品形态** | 每个 Stage 对外交付的形态（插件 / 软件 / 页面） | 形态、宿主包装 |
| **输入输出契约** | 每个 Stage 的输入与输出的唯一权威 schema 定义 | IO 契约、产物 schema |

> 代码标识符（`LLMProvider`、`output_type`、`solve`、`schemas/` 等）保持英文原样，不作中文转译。`pydantic` 全小写；类名（`BaseModel`）按 Python 惯例。

---

## 0. 一句话目标

**六层 Stage 保持划分、顺序重排为「轮廓 → 主体 → 细节」。每个 Stage 是（a）一个独立产品单元——有独立输入输出契约、可用「插件 / 软件 / 页面」三种产品形态包装；（b）其内部实现统一走「LLM（想法）× 边界约束（求解器）」的迭代收敛范式。先把每个 Stage 独立成型（插件 / 软件 / 页面），再组合成整体服务。**

---

## 1. 两个正交的维度

理解这个系统，要同时看两条轴：

### 轴一：实现方式（Stage 内部算法）

每个 Stage 内部都是「LLM + 边界约束」两套机制协同，通过迭代收敛完成本阶段工作（Artist，见第 2 节）。

### 轴二：产品形态（Stage 对外交付）

每个 Stage 都是**独立产品单元**：

- **独立输入**：消费明确的输入契约（原始输入或上游 Stage 的阶段产物）。
- **独立输出**：产出明确的输出契约（本阶段的阶段产物 schema）。
- **独立产品形态**：可用三种产品形态对外交付——**插件 / 软件 / 页面**。

> 关键：**两轴正交**。「LLM × 边界约束」是每个 Stage **怎么做**；「插件 / 软件 / 页面」是每个 Stage **怎么交付给用户**。同一个 Stage 的同一份实现，可以同时封装成三种产品形态。

---

## 2. 实现方式：Artist（Stage 内部）

Artist 创作时，天然分阶段（轮廓 → 主体 → 细节），每一笔都是「大脑理解与想法」与「现实约束」的迭代收敛。

| Artist 概念 | 系统对应 |
|-----------|---------|
| 工作阶段 | **Stage**（六层） |
| 大脑的理解与想法 | **LLM** |
| 现实的约束 | **边界约束（确定性规则 / 求解器）** |
| 每一笔的迭代收敛 | Stage 内部「想法 → 求解 → 校验 → 回拉新想法」 |
| 一幅完成的作品 | 场景生成（数据结果） |

三点基石：

1. LLM 与边界约束**不分工到不同 Stage**——每个 Stage 内部**同时存在**两套机制。
2. 两套机制通过**迭代收敛**协作，不是线性「先 LLM 后边界约束」。
3. 边界约束是**确定性规则与求解器**，不是软约束、不是又一个 LLM。

---

## 3. 产品形态：插件 / 软件 / 页面

每个 Stage 的同一份「LLM × 边界约束」实现，通过**统一的输入输出契约**对外提供三种产品形态：

| 产品形态 | 含义 | 典型宿主 | 示例 |
|---------|------|---------|------|
| **插件** | 嵌入宿主应用的功能模块 | Blender / 浏览器 / 编辑器 | `layout` Stage 作为 Blender 布局插件；`understand` 作为图片理解插件 |
| **软件** | 独立运行的桌面 / 命令行应用 | 独立进程 | 完整场景生成的独立 CLI / 桌面软件 |
| **页面** | Web / 交互 UI | 浏览器 | `stylize` 的实时风格化预览页面；整个 pipeline 的 Web 控制台 |

### 3.1 输入输出契约统一，产品形态是包装层

- 每个 Stage 的**输入输出契约（schema）是唯一的权威定义**（见第 4 节 `schemas/`）。
- 插件 / 软件 / 页面只是对这个契约的**三种产品形态包装**——同一份输入 schema、同一份输出 schema，三套不同的交互外壳。
- 因此「先插件后整体服务」= 先把每个 Stage 以最合适的产品形态独立包装出来，再通过统一的契约把它们串成整体服务。

### 3.2 与现有 products/ 的关系

现有 `products/layout_blender`、`products/layout_omniverse`、`products/cli` 就是「产品形态」的雏形，但目前：

- 它们直接 import Stage 内部类、手工拼 Stage，**没有通过统一输入输出契约**；
- `layout_blender` 的 `agent.py` 引用了已不存在的 `scene_mesh.vertices` 字段（已坏）。

本设计要把 products/ 重构成「契约之上的产品形态包装层」：每个 products 只认识「输入契约 + 输出契约」，不 import Stage 内部实现。

---

## 4. 六层 Stage：顺序重排 + 每层两轴

顺序：`understand → geometry → layout → surface → accessory → stylize`（轮廓 → 主体 → 细节，点缀在风格前）。

| 阶段 | layer | 工作内容 | 实现方式（LLM × 边界约束） | 产品形态示例 |
|------|-------|---------|--------------------------|-------------|
| 轮廓 | `understand` | 语义理解：场景 / 区域 / 类型 | 想法「这是客厅」× 边界约束「词表合法、区域不空」 | 页面（上传图 / 文 → 理解结果） |
| 轮廓 | `geometry` | 边界 / 骨架：2D → 3D 几何 | 想法「大致矩形」× 边界约束「多边形闭合、不自交、开洞落边」 | 插件（Blender 几何重建） |
| 主体 | `layout` | 主体造型：组合布局 | 想法「沙发靠墙」× 边界约束「不越界、不碰撞、留净宽」 | 插件（Blender 布局） |
| 主体 | `surface` | 表面覆盖：铺贴 | 想法「白墙木地板」× 边界约束「覆盖完整、归属合法」 | 页面（材质选择） |
| 细节 | `accessory` | 点缀：小件散布 | 想法「书桌放本书」× 边界约束「在区域内、不挡通道」 | 插件（点缀散布） |
| 细节 | `stylize` | 风格化：材质 / 灯光 / 相机 | 想法「暖色调」× 边界约束「参数在界内、风格词表合法」 | 页面（实时风格化预览） |

---

## 5. Stage 接口改造

### 5.1 Stage Protocol

```python
# xasset/pipeline/stage.py
from typing import Protocol, Generic, TypeVar, runtime_checkable

T = TypeVar("T")

@runtime_checkable
class Stage(Protocol, Generic[T]):
    name: str
    layer: str
    scene_types: list[str]

    @property
    def input_type(self) -> type:
        """本 Stage 的输入契约类型。"""

    @property
    def output_type(self) -> type:
        """本 Stage 的输出契约类型（框架强校验）。"""

    def run(self, ctx: PipelineContext) -> T:
        """执行本 Stage：内部「LLM × 边界约束」迭代收敛，返回阶段产物。"""
```

### 5.2 Stage 内部两套机制（Stage 自持）

```python
self._llm: LLMProvider           # LLM 侧（框架 / 构造注入）
self._solvers: list[Solver]      # 边界约束侧：求解器（落地合法数据）
self._constraints: ConstraintSet # 边界约束侧：校验门（求解结果护栏）
```

`run()` 内部是本 Stage 独有的迭代循环（想法 → 求解 → 校验 → 回拉新想法），迭代过程不外露，只在 Stage 内收敛。

### 5.3 框架职责（收敛到最小）

1. 按 `config.stages` 顺序执行，注入 `LLMProvider`。
2. `run()` 返回后强校验 `output_type`，写入 `ctx.stage_outputs[self.layer]`。
3. 失败即中断（迭代不收敛 / 校验不过 → `StageRejected`）。

---

## 6. 输入输出契约：统一 schema 层

```
xasset/pipeline/schemas/
├── understand.py     # SceneUnderstanding（理解阶段产物）
├── geometry.py       # MeshBuildOutput / SceneMesh / ...
├── layout.py         # LayoutOutput / PlacedGroup / ...
├── surface.py        # SurfaceOutput
├── accessory.py      # AccessoryOutput
└── stylize.py        # StylizeOutput
```

- 每个 Stage 的 `input_type` / `output_type` 都来自这里——这是**产品和实现共享的唯一输入输出契约**。
- 倾向 pydantic：LLM 结构化输出用 `model_validate` 严格解析，跨产品形态（插件 / 软件 / 页面）的边界也用它做序列化契约。

---

## 7. 边界约束 = 求解器（工具），校验门 = 护栏

- **求解器**：确定性几何 / 布局算法，是"把想法落地成合法数据"的主力，复用并扩展 `tools/geometry`，新增布局与约束求解器。
- **校验门**：求解结果的最终合法性护栏，非"落地"主力。
- 边界约束都是确定性的，不是 LLM。

---

## 8. 迁移影响面

| 文件 | 改动 |
|------|------|
| `pipeline/stage.py` | `Stage[Generic[T]]` + `input_type` / `output_type` + `run() -> T` |
| `pipeline/pipeline.py` | 注入 LLMProvider；顺序执行 + output_type 强校验 + 失败中断 |
| `pipeline/context.py` | `stage_outputs` 类型强校验 |
| `pipeline/schemas/*` | 新增统一输入输出契约层 |
| 6 个 Stage 文件 | 各自实现 input_type / output_type + 内部「LLM × 边界约束」迭代（过渡期占位） |
| `products/*` | 重构成「契约之上的产品形态包装层」：插件 / 软件 / 页面只靠输入输出契约，不 import Stage 内部 |
| `llm/` | `LLMProvider` 保留；编排逻辑下沉到各 Stage 内部 |
| `tools/` | `geometry` 保留；新增求解器 |
| `services/generation.py` | 默认顺序改为重排后；variation 映射改基于 layer 语义 |

---

## 9. 待确认问题

- [ ] schema 全面 pydantic 化（`BaseModel`），还是 dataclass + 手动 validate？（倾向 pydantic）
- [ ] 「插件 / 软件 / 页面」三种产品形态，是否每种都要有明确的打包 / 隔离机制（各自 pyproject / optional-dependencies），还只是现阶段目录约定？
- [ ] 每个 Stage 的「产品形态」是否要现在就选型并落地，还是先定义输入输出契约、产品形态包装后续逐个补？
- [ ] Stage 内部迭代收敛的策略：统一框架级策略（最大迭代 N 次），还是各 Stage 自由？
- [ ] `understand` 的「想法」是否覆盖所有下游选择（Group / 风格），还是下游 Stage 各自也有次级「想法」（内嵌 LLM）？
