# xasset 架构与理念

> **本文档是思路对齐的入口**。想快速理解系统设计意图，只看这一份就够。
> 更新：2026-09

---

## 一、核心理念：Artist

用**艺术家创作**的类比，组织整个 3D 场景生成：

> 艺术家分阶段创作（先轮廓、再主体、最后细节），每一笔都在「大脑的想法」和「现实的约束」之间反复权衡，直到成型。

落到系统里，每个 Stage 内部都有两股力量协作：

| Artist 概念 | 系统对应 |
|------------|---------|
| 大脑的理解与想法 | **理解侧**（LLM / 视觉算法 / 打分模型…） |
| 现实的约束 | **约束侧**（几何求解器 / 确定性规则 / 统计边界） |
| 反复权衡 | **迭代收敛**：想法 → 落地 → 校验 → 回拉新想法 |
| 完成的作品 | 场景生成（可渲染数据） |

> **最关键的一点：Artist 统一的是「结构」，不是「技术」。**
>
> 它只规定"每个 Stage 都由理解侧与约束侧协作、都要迭代收敛、都要过校验门"。
> 至于某一侧具体用 LLM、视觉算法还是几何求解器——**按业务场景自由选型，是实现的决策，不是架构的约束**。
>
> 例如：`understand` 的语义判断适合 LLM，`geometry` 的精确重建更适合几何/视觉算法。
> 如果硬把它们都塞成"LLM"，反而是错的。

### 1.1 为什么这样分工（有依据）

| 能力 | 大模型 | 专用模型/算法 |
|------|--------|--------------|
| 精确 mask / 坐标 | ❌ 受 patch 量化限制（32×32 一格 ≈ 31cm） | ✅ 像素级 |
| 语义判断 | ✅ 强项 | ❌ 不懂语义 |
| 几何合法性 | ❌ | ✅ 确定性可保证 |

> OpenAI 官方文档明确承认多模态模型 "struggles with precise spatial localization"。
> 详见 `research/foundation-models-multimodal/`。

---

## 二、六层 Stage：轮廓 → 主体 → 细节

| 阶段 | Layer | 干什么 | 依赖（requires） |
|------|-------|--------|-----------------|
| **轮廓** | `understand` | 产出轮廓线 + 语义 + 轮廓语义 | — |
| **轮廓** | `geometry` | 2D 轮廓线 → 3D 几何 | understand |
| **主体** | `layout` | 主体内容摆放 | understand |
| **主体** | `surface` | 表面覆盖 | understand, geometry |
| **细节** | `accessory` | 点缀散布 | understand, layout |
| **细节** | `stylize` | 风格化（材质 / 灯光 / 相机） | 全部上游 |

---

## 三、两轴正交

| 轴 | 含义 | 内容 |
|----|------|------|
| **轴一 · 实现方式** | Stage 内部怎么做 | 理解侧 × 约束侧迭代收敛 |
| **轴二 · 产品形态** | Stage 怎么交付 | 插件 / 软件 / 页面 |

**同一份实现，可以同时封装成三种产品形态**——两轴互不绑定。

演进路径：**先插件后整体服务**——先让每个 Stage 独立成型，再用统一契约串成整体服务。

---

## 四、契约：一套 schema 描述六类场景

这是整个设计最核心的突破——**契约不是为室内设计的**。

| 场景 | region_type 示例 | elevation 语义 | opening 示例 | fixed_edge 示例 |
|------|-----------------|---------------|-------------|----------------|
| 室内 | living_room / bedroom | 层高 [0, 2.8] | door / window | load_bearing |
| 城市 | road / building_footprint | 建筑高 [0, 45] | road_entrance | property_line |
| 乡村 | farmland / village_block | 地形起伏 [0, 1.5] | field_gate | irrigation_ditch |
| 山林 | ridge / forest_patch | 海拔 [800, 1450] | mountain_pass | cliff_edge |
| 海洋 | deep_water / reef | 水深 [-1200, 0] | strait / channel | shoreline |
| 沙漠 | dune / oasis | 沙丘高 [0, 85] | dune_pass | rock_edge |

### 统一的四个手段

1. **平面轮廓**（`Polygon`）—— 房间、街区、海域、沙丘都是轮廓
2. **中性垂直字段**（`ElevationRange`）—— 层高 / 建筑高 / 水深（负值）/ 海拔 / 沙丘高
3. **开口 + 固定边两抽象** —— door/路口/山口/航道都是 opening；承重墙/红线/岸线都是 fixed_edge
4. **attrs 开放容器** —— 场景特有信息一律进这里，**不新增字段**

> **室内只是这套抽象的一个填法**，`door` / `window` 不是契约的默认形状。
> 已实测验证六类场景都能用同一套 `SceneRegion` 描述成功。

**详细字段定义** → `docs/stage-io-contract-spec.md`

---

## 五、Stage 接口

```python
class Stage(Protocol, Generic[TOut]):
    name: str
    layer: str
    scene_types: list[str]
    requires: list[str]        # 显式声明依赖哪些上游
    output_type: type[TOut]    # 声明产出什么

    def run(self, inputs: StageInputs) -> TOut: ...
```

### 三个关键设计

| 设计 | 解决的问题 |
|------|-----------|
| **`requires` 显式依赖** | 旧做法从 ctx "碰巧取到"，漏了上游不报错 |
| **`output_type` 强校验** | 旧做法契约靠自觉，框架不检查 |
| **`run(inputs) -> T`** | 旧做法隐式写字典，无类型 |

**框架职责收敛到最小**：只做依赖校验、注入、类型校验、失败中断——
**不干预 Stage 内部用什么技术、怎么迭代**。

### 5.1 迭代入口（Artist 形状）

Stage 内部不是流水线，而是「想法 → 落地 → 校验 → 回拉」：

```python
def run(self, inputs):
    idea = self.produce_idea(...)              # 理解侧
    for _ in range(self.max_fix_iterations):   # ← 迭代入口
        output = self.realize(idea, ...)       # 约束侧
        errors = self.constraints.validate(output)
        if errors.ok: break
        idea = self.refine_idea(idea, errors)  # ← 回拉
    return output
```

**当前 `max_fix_iterations=1`**（单次求解），将来调到 3 就是迭代，结构不用改。

> 为什么先不做迭代：见 `docs/iteration-convergence.md` 第 8 节。

---

## 六、五条贯穿性设计原则

### 6.1 约束校验是强制默认项，没有例外

任何要呈现给用户或送入下游的结果，**必须先经过校验门**——不因为"这个算法看似可靠"就跳过。

不区分"要不要校验"，只区分"大概率通过 or 大概率拦截"——但校验动作本身，全部路径都不可省略。

### 6.2 速写轮廓 + 自然语言迭代编辑

**不追求单次生成的高还原度，先画"速写轮廓"。**

每个 Stage 的产出都不是"最终答案"，而是一份**可编辑的初稿**——算法只需把语义搭对，精修交给约束校验和用户调整。

**这把"生成准确率"的压力，从算法侧一部分转移到"约束校验 + 人工可控的二次调整"上。**

### 6.3 自然语言编辑闭环

```
自然语言指令
  → 理解侧解析成结构化编辑操作
  → 在当前数据上应用
  → 重新过校验门
  → 失败 → 返回自然语言解释
  → 通过 → 更新数据，刷新展示
```

**编辑结果同样必须过校验门**——与首次生成共用同一道闸门。

### 6.4 结果核验：可视化对照

各 Stage 通用：把结果渲染成线框图，与原始输入对照。

- `understand`：轮廓叠原图
- `geometry`：3D 预览
- `layout`：轮廓上叠加已摆放内容的框
- `surface` / `accessory` / `stylize`：叠加资产缩略图 / 风格标签

这是让用户"低成本纠错"的关键。

### 6.5 技术选型标准

因为有强制校验兜底 + 速写轮廓预期 + 编辑闭环，选型标准统一偏移：**不选精度最高的，选"能快速产出语义正确初稿"的**。

---

## 七、一句话总括

> **xasset = Artist 方法论（理解侧 × 约束侧迭代收敛）
> + 六层 Stage（轮廓 → 主体 → 细节）
> + 两轴正交（实现方式 × 产品形态）
> + 一套契约统一六类场景。**

**设计哲学**：把"该由谁做"（理解 or 约束）和"用什么做"（LLM / 算法 / 求解器）彻底分开——
**前者是架构，后者是实现**。这样架构可以稳定，而每一层都能选最适合的技术。

---

## 八、当前实现状态

| 层 | 状态 | 说明 |
|----|------|------|
| `understand` | 🟡 **已跑通真实户型图** | 分割 7 区域，轮廓准确；语义标注待接 |
| `geometry` | ⬜ | 返回空 mesh |
| `layout` | ⬜ | 返回空 |
| `surface` | ⬜ | 返回空 |
| `accessory` | ⬜ | 返回空 |
| `stylize` | ⬜ | 返回空 |

**详细进度** → `docs/task-progress.md`
