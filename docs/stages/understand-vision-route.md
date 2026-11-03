# understand 视觉路线设计

> 定位：**设计决策文档**。定义 `understand` 阶段如何从图片得到轮廓线。
> 状态：设计定稿 + 第 ③ 步已实现；①②④ 为抽象接口，待选型
> 更新：2026-09
> 关联：`docs/iteration-convergence.md`、`research/foundation-models-multimodal/README.md`

---

## 0. 一句话结论

> **图片不交给大模型直接吐多边形。**
> 轮廓走「分割模型出 mask → 确定性几何算法拟合多边形」，语义走「多模态模型或分类器」。
> **两者分工，而不是一个模型全包。**

---

## 0.1 业务约束：输入几乎总是图片

**这是决定整个设计的前提。**

| 约束 | 说明 |
|------|------|
| **绝大多数输入是图片** | 用户给的就是图，不是矢量文件 |
| **即使原始是矢量，到手也是栅格图** | 截图、导出、转存等环节把矢量变成了图片 |
| **因此不追矢量来源** | 一律按图片处理，不为"矢量来源"做特殊分支 |

**这个决定做了三件事**：

1. **简化了系统**——只有一条输入路径，不用维护双轨
2. **抬高了第 ③ 层的价值**——几何后处理是唯一出口，所有输入都靠它
3. **明确了外部数据的定位**——OSM / 国标等是"校验与补全"的**辅助知识**，不是主输入

### 图片细分为两类（由用户选择）

| 类型 | 特点 | 几何后处理 |
|------|------|-----------|
| **图纸 / 平面图** | 信息完整、无遮挡、直角结构 | **正交化 ON** |
| **实景照片** | 有遮挡、深度歧义、墙角未必垂直 | **正交化 OFF** |

> **由用户选择而非自动判定**——两个入口（"传图纸" / "传实景照片"）。
> 理由：判定错误会让后续整条链路用错策略（正交化开关），代价远大于让用户点一下。

**当前范围：单图。** 多图（一个房间多张 / 图纸+实景混合）后续支持。

---

## 1. 为什么这么设计

依据见 `research/foundation-models-multimodal/README.md` 第 2.2 节，核心事实：

| 事实 | 来源 | 影响 |
|------|------|------|
| 多模态模型把图切成 32×32 patch | OpenAI 官方文档 | 1024 图上一个 patch ≈ 31cm（10m 房间），**坐标精度受此限制** |
| 官方承认"struggles with precise spatial localization" | 同上 Limitations | 精确空间定位是明确弱项 |
| 官方承认"may give approximate counts" | 同上 | 连数房间都不保证准 |

**结论**：让多模态模型直接输出房间多边形，是在用它最不擅长的能力。

---

## 2. 四层架构

```
用户输入：图片 + 类型选择（图纸 / 实景）
    │
    ├─ ① 输入类型 ─────────── ✅ 用户选择（不自动判定）
    │     图纸 → 正交化 ON
    │     实景 → 正交化 OFF
    │     ⚠️ 判错会让整条链路用错策略，所以交给用户
    │
    ├─ ② 分割 ─────────────── 抽象接口（可 SAM / 专用模型 / API）
    │     输出：每个区域的像素 mask
    │
    ├─ ③ 几何后处理 ───────── ✅ 已实现（tools/geometry/contour.py）
    │     mask → 轮廓跟踪 → 尺度换算 → 简化 → 正交化 → CCW
    │     **完全确定性，不依赖任何外部模型**
    │
    └─ ④ 语义标注 ─────────── 抽象接口（可 LLM / 分类器）
          给每个多边形打 region_type 标签
```

**① ② ④ 是"理解侧"（可换技术）；③ 是"约束侧"（确定性）。**

这正好体现 Artist 范式：理解侧技术按场景选型，约束侧必须确定。

---

## 3. 第 ③ 步：几何后处理（已实现）

### 3.1 处理链

```
mask（布尔矩阵）
  ↓ trace_contour()        Moore 邻域跟踪，提最外层轮廓
像素轮廓点
  ↓ pixels_to_polygon()    尺度换算，Y 翻转为 Z
米制多边形（可能很密）
  ↓ simplify_polygon()     Douglas-Peucker 简化
  ↓ orthogonalize()        正交化（**仅图纸场景**）
  ↓ ensure_ccw()           绕向统一
Polygon 契约
```

### 3.2 关键决策：正交化只在图纸场景用

| 场景 | 是否正交化 | 理由 |
|------|-----------|------|
| **图纸 / 户型图** | ✅ 是 | 这类图的墙本来就都是直角，正交化能修复分割模型的轻微倾斜 |
| **实景照片** | ❌ **否** | 真实墙角未必垂直（透视、施工误差），强行正交化会失真 |

`mask_to_polygon(..., orthogonalize_result=?)` 参数控制。**用户选择的输入类型决定这个开关。**

### 3.3 尺度推断：两条路

这是**最容易出错的一步**——图片是像素坐标，我们要米制。

| 方式 | 函数 | 可靠性 | 何时用 |
|------|------|--------|--------|
| **参照物反推** | `infer_scale_from_reference()` | ⭐⭐⭐⭐ 高 | 能识别出标准门宽（0.9m）时首选 |
| **面积先验反推** | `infer_scale_from_area()` | ⭐⭐ 低 | 无参照物时兜底，误差可能数倍 |

```python
# 首选：用识别出的门宽反推
scale = infer_scale_from_reference(px_length=90, real_length_m=0.9)  # 100 px/m

# 兜底：用房间类型典型面积反推
scale = infer_scale_from_area(px_area=10000, expected_area_m2=(8.0, 25.0))
```

> **风险提示**：面积先验法假设"这是个典型大小的房间"，若实际偏大偏小，整个场景尺度都会错。
> 建议在产物里标记尺度来源的置信度。

---

## 4. 第 ①②④ 步：抽象接口（待选型）

这三步**不绑定具体技术**，按 Artist 范式应做成可替换接口。

### 4.1 建议的接口形态

```python
class RegionSegmenter(Protocol):
    """② 分割：图片 → 每个区域的 mask。"""
    def segment(self, image: Any, hints: dict) -> list[RegionMask]: ...

class RegionLabeler(Protocol):
    """④ 语义标注：多边形 + 图片 → region_type。"""
    def label(self, image: Any, regions: list) -> list[str]: ...
```

> ① 不需要接口——它是用户选择的枚举值（`"drawing"` / `"photo"`），直接传参。

**为什么先抽象**：具体用 SAM、专有模型还是云 API，取决于成本/许可/精度实测，现在定死会限制后续。

### 4.2 候选技术（供后续选型）

| 步骤 | 候选 | 备注 |
|------|------|------|
| ② 分割 | SAM 系列 / 专用户型图模型 / 云 API | 需实测精度与成本 |
| ④ 语义标注 | 多模态 LLM | 语义是 LLM 强项，适合 |

> **④ 可以直接用多模态 LLM**——语义任务正是它的强项。
> 只有 ②（需要精确 mask）必须用专用视觉模型。

---

## 5. 与现有代码的关系

| 模块 | 作用 |
|------|------|
| `tools/geometry/contour.py` | **本设计第 ③ 步的实现**（约束侧，确定性） |
| `pipeline/stages/understand/interfaces.py` | ②④ 的 Protocol + 空实现（理解侧，可替换） |
| `pipeline/stages/understand/scene_understand.py` | Stage 编排（Artist 形状） |
| `tools/geometry/normalize.py` | SceneVector 的规整（结构化输入路线） |
| `tools/constraint/` | 硬约束，产出后立刻校验 |

### 5.1 实现形态：按 Artist 形状，不是流水线

**这一点很关键。** `understand` 的 `run()` 不是平铺直叙的四步流水线，而是 Artist 的迭代形状：

```python
def run(self, inputs):
    if scene_vector:  return self._from_scene_vector(inp)   # 结构化路线
    if image:         return self._from_image(inp)          # 视觉路线

def _from_image(self, inp):
    idea = self.produce_idea(image, inp)          # 理解侧：②分割 + ④语义
    for i in range(self.max_fix_iterations):      # ← 迭代入口（现为 1）
        output = self.realize(idea, inp)          # 约束侧：③几何后处理
        result = self._hard_constraints.validate(None, output)   # 校验门
        if result.ok:
            break
        if i + 1 < self.max_fix_iterations:
            idea = self.refine_idea(idea, result, inp)           # ← 回拉
    return output
```

**为什么这样写（而不是流水线）**：

| 写法 | 符合 Artist 吗 |
|------|--------------|
| 平铺流水线 `分割 → 几何 → 标注` | ❌ 是单向处理，不是迭代收敛 |
| **本实现的「想法 → 落地 → 校验 → 回拉」** | ✅ 结构是 Artist 的，参数保守 |

**当前 `max_fix_iterations = 1` 的含义**：单次求解 + 强制校验，不启用回拉。这符合 `docs/iteration-convergence.md` 第 8 节"先不要做迭代"的建议。

**将来改迭代只需一个参数**：把 `max_fix_iterations` 从 1 调到 3，并在 `refine_idea()` 里填真实逻辑（如"开口悬空 → 让分割器重出 mask"），**不需要重写 `run()`**。

### 5.2 「想法」与「产物」是分开的

```python
class _Idea:
    mask: RegionMask          # 像素 mask（还没落地）
    region_type: str          # 语义标签
    confidence: float
    scale: ScaleInfo | None   # 尺度（来自参照物时优先）
```

**为什么分开**：
- **想法**是理解侧的产物，还没有米制几何
- **产物**（`SceneRegion`）是约束侧落地后的结果，有 `Polygon` 和面积
- 回拉时改的是**想法**，不是已落地的产物——这样才符合"重新出想法"的语义

---

## 6. 尚未解决

| 问题 | 影响 | 优先级 |
|------|------|--------|
| ①②④ 的具体技术选型 | 阻塞 `understand` 完整实现 | P0 |
| 尺度推断的置信度如何表达 | 影响下游对结果的信任度 | P1 |
| 多区域重叠时轮廓如何分离 | 分割模型可能给出粘连 mask | P1 |
| 实景照片的深度/遮挡怎么处理 | 比图纸难得多 | P2 |

---

## 7. 一句话记住

> **精确的几何交给确定性算法，语义判断才交给 LLM。**
>
> 图片 → mask（专用模型）→ 多边形（我们的几何算法）→ 语义标签（LLM）→ 契约。
