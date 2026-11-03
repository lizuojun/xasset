# 迭代与收敛设计

> 定位：**设计决策文档**。回答"每个 Stage 内部的迭代怎么才能真正收敛"。
> 状态：设计草案 v1，待评审
> 更新：2026-09
> 关联：
> - `docs/architecture.md` —— Artist 方法论（理解侧 × 约束侧）
> - `docs/architecture.md` —— Stage 接口与范式
> - `docs/stage-io-contract-spec.md` —— 阶段产物契约
> - `research/foundation-models-multimodal/README.md` —— 大模型能力边界的调研依据

---

## 0. 一句话结论

> **迭代不能只有一种。按"不满意"的性质分成三类，分别用三种不同的闭环策略——其中绝大多数是确定性的，只有最少的部分需要重新问 LLM，而"理解错了"这一类必须交给人，不做自动闭环。**

---

## 1. 问题的来源

Artist 范式说"每个 Stage 内部是理解侧 × 约束侧的迭代收敛"。但这句话留了一个关键缺口：**迭代什么时候停？**

如果只用"校验门通过"当判据，会有两个失败模式：

- **要么一次就过**（校验门只管合法性，很多"合法但很差"的结果能通过）→ 迭代形同虚设
- **要么永远不收敛**（"不满意"没有边界）→ 跑到最大次数硬停

所以必须先把"不满意"这件事拆清楚。

---

## 2. 三类"不满意"，三种闭环

| 类型 | 具体表现 | 谁能判断 | 能否确定性判定 | 闭环策略 |
|------|---------|---------|--------------|---------|
| **A. 非法** | 多边形自交、开口悬空、内容越界 | 几何算法 | ✅ 完全 | **确定性修正**（不调 LLM） |
| **B. 不够好** | 通行净宽不足、动线穿越、比例失衡 | 几何/统计规则 | ✅ 大部分可 | **确定性优化**（不调 LLM） |
| **C. 理解错了** | 把卧室认成书房、房间数错 | 需要外部真值 | ❌ 很难自动 | **交给人，不做自动闭环** |

**这个分类是整个设计的地基**。混在一起谈"迭代"，必然写出一个失控的循环。

### 2.1 已落地：硬约束与软规则分成两个模块

三类划分对应到代码，是两个边界清晰的模块：

| | **硬约束**（A 类） | **软规则**（B 类） |
|---|------------------|------------------|
| 模块 | `xasset/tools/constraint/` | `xasset/tools/quality/` |
| 规则承载 | **Python 代码**（几何算法） | **JSON 配置**（`data/<scene>/rules.json`） |
| 谁维护 | 开发者 | **领域专家可直接改** |
| 性质 | 绝对不合法，**不可让步** | 偏好，**可让步** |
| 例子 | 多边形自交、开口悬空、内容越界 | 面积略小于典型、长宽比偏大 |
| 返回值 | `RuleViolation`（含 **fix 修复建议**） | `str`（违规说明） |
| 失败后果 | 必须修，修不好则 Stage 失败 | 继续优化，优化不了也可接受 |

**判断标准（一句话）**：

> 违反了结果就**用不了** → 硬约束；
> 只是**用得不够舒服** → 软规则。

**为什么硬约束不用配置**：它的判定逻辑本身就是几何算法（如线段相交检测），没法用"阈值"表达，必须写代码。

**为什么软规则用配置**：它的结构就是"检查什么 + 阈值多少"，领域专家不需要读代码就能维护。

---

## 3. 类型 A：非法 —— 确定性修正

### 3.1 性质

**单调收敛**：每次修正严格减少非法项的数量，不会引入新的非法。

因为修复动作（裁剪、吸附、沿边平移）都是确定性的几何操作。

### 3.2 闭环形态

```
想法 → 求解器落地 → 校验门
                        ↓ 报错（附结构化修复信息）
                        ↓
              求解器直接执行修复（不调 LLM）
                        ↓
                   再校验 → 直到 0 错误
```

### 3.3 关键要求：回喂结构化错误，不是自然语言

**错误**：

```python
"门的位置不对"
```

**正确**：

```python
{
    "rule": "opening_on_boundary",
    "target_id": "door_3",
    "violation": "开口中心距轮廓边 0.42m，超出容差 0.1m",
    "fix": {"op": "move_along_normal", "delta": -0.42},
    "alternative": {"op": "snap_to", "seg": "seg_7", "t": 0.35},
}
```

**有了 `fix` 字段，求解器可以直接执行修复，根本不需要调用 LLM。** 这是"确定性迭代"。

> 契约影响：`ConstraintRule` 的返回值目前是 `(bool, str)`，需要扩展为携带修复建议的结构。

### 3.4 迭代上限

`max_legal_fix`，通常 **3~5 次**。超过说明求解器本身有问题，不是迭代能救的。

---

## 4. 类型 B：不够好 —— 把"质量"降解为可计算的几何规则

### 4.1 关键洞察

**不要试图定义一个综合审美评分函数**（"这户型好不好"根本没法算）。

但在这个领域里，**所谓"质量"大部分可以降解为具体的、可计算的几何/统计规则**：

| 软规则 | 判定方式 | 可算 |
|--------|---------|------|
| 通行净宽 ≥ 0.6m | 几何计算 | ✅ |
| 主要通道不被阻挡 | 几何可达性 | ✅ |
| 房间面积在合理区间 | 与统计先验比对 | ✅ |
| 长宽比不过分狭长 | 几何计算 | ✅ |
| 门不正对床/沙发 | 几何计算 | ✅ |
| 必需功能组齐备 | 集合比对 | ✅ |
| 主要动线不穿越功能区中心 | 几何计算 | ✅ |

**结论：类型 B 也是确定性的，只是规则"更软"（允许让步）。你不需要主观审美模型。**

### 4.1.1 已落地：软规则配置 + 评估器

这套机制已经实现，分三层：

| 层 | 位置 | 谁维护 |
|----|------|--------|
| **规则清单（业务知识）** | `data/<scene>/rules.json` | **领域专家**，直接改 JSON |
| **规则实现（几何计算）** | `xasset/tools/quality/builtin.py` | 开发者 |
| **评估框架** | `xasset/tools/quality/rules.py` | 开发者 |

**为什么用 JSON 而不是 YAML**：项目坚持"零外部服务依赖，git clone 后直接跑"，JSON 是 Python 内置，不引入 PyYAML。代价是不能写注释，用 `_comment` 字段替代。

**配置结构**（以 house 为例）：

```json
{
  "scene": "house",
  "scene_rules": [
    {"id": "min_passage_width", "level": "required",
     "params": {"min_width_m": 0.6}}
  ],
  "region_rules": {
    "bedroom": {
      "typical_area_m2": [8.0, 25.0],
      "rules": [
        {"id": "bedroom_needs_bed", "level": "required",
         "params": {"any_of_element_types": ["bed_group"]}}
      ]
    }
  }
}
```

**两级规则**：`scene_rules`（全场景通用）+ `region_rules[region_type]`（区域专属），评估时合并。

**阈值有数据依据**：`data/house/rules.json` 的面积区间来自 99 个真实户型的实测统计，不是拍脑袋：

| region_type | 面积区间 (m²) | 长宽比中位 / 最大 |
|-------------|-------------|-----------------|
| bathroom | 1.6 – 6.0 | 1.33 / 2.10 |
| bedroom | 3.9 – 22.2 | 1.48 / 2.19 |
| kitchen | 3.8 – 10.8 | 2.19 / 2.76 |
| living_dining_room | 18.8 – 39.3 | 1.70 / 2.53 |
| balcony | 2.1 – 6.6 | **3.12 / 4.54**（阳台天然狭长） |

> 注意 balcony 的长宽比明显大于其它房间——这条数据直接说明**不能用一个全局的长宽比阈值**，必须按 region_type 分别定。

**使用方式**：

```python
from xasset.tools.quality import QualityConfig, build_default_registry

config = QualityConfig.load("data/house/rules.json", build_default_registry())
report = config.evaluate(regions)

if not report.ok:                       # 有 required 级违规
    ...                                  # 继续迭代
score = report.score                     # 仅用于比较优化前后的好坏
```

**配置与实现解耦的好处**：配置里声明了但代码未实现的规则会被**跳过而不是报错**，所以可以"配置先行"——领域专家先把规则写全，开发者按需逐步实现。

### 4.2 软规则的三个设计要点

**要点 1：每条规则独立，不做加权求和**

加权求和会让"一条严重违规"被"很多小优点"抵消，这在质量判断上是错的。

**要点 2：规则有优先级，分"必须"和"尽力"**

```python
QUALITY_RULES = [
    # 必须满足（不满足则必须继续迭代）
    Rule("min_passage_width", required=True, threshold=0.6),
    Rule("no_blocking_passage", required=True),

    # 尽力而为（满足到一定程度即可停）
    Rule("area_within_typical", required=False, weight=2),
    Rule("aspect_ratio_comfortable", required=False, weight=1),
]
```

**要点 3：允许"无法同时满足"的冲突**

真实场景里，净宽和面宽可能冲突。需要有明确的**冲突消解策略**（按优先级放弃低优先级的），否则迭代会卡死。

### 4.3 收敛判据

```
不再有"必须"级违规
    且
（分数不再提升  或  达到 max_quality_iter）
```

`max_quality_iter` 通常 **2~3 次**。

---

## 5. 类型 C：理解错了 —— 必须不做自动闭环

### 5.1 为什么

- 系统内部**没有任何判据**能知道"把卧室认成了书房"
- 强行让 LLM 自我批评，它会**编造理由**，越改越差
- 自评的可靠性在有客观真值时很低

### 5.2 正确做法：外部校验

| 外部手段 | 说明 |
|---------|------|
| **用户确认** | 可视化对照后让用户判断（"这是书房不是卧室"） |
| **交叉验证** | 多个输入源（图片 + 文字）互相印证，不一致就标记 |
| **先验报警** | "15㎡被识别成卫生间"——面积先验不合理，主动标记 |

### 5.3 对设计的含义

**这正好对应你架构里的"自然语言迭代编辑"——编辑是给人用的，不是给系统自动重试的。**

`understand` 这类语义阶段，产出应该**明确标记置信度**，并把低置信的部分暴露给人确认，而不是内部自我迭代。

---

## 6. 综合流程

```python
def run(self, inputs) -> StageOutput:
    # 1. 理解侧出想法
    idea = self._understanding.generate(inputs)

    # 2. 类型 A：非法 → 确定性修正
    output = self._solve(idea)
    for _ in range(self.max_legal_fix):
        errors = self._hard_constraints.check(output)
        if not errors:
            break
        fixes = [e.fix for e in errors if e.fix]
        if not fixes:
            break                        # 无法自动修复
        idea = self._apply_fixes(idea, fixes)
        output = self._solve(idea)

    # 3. 修不好 → 极少次回问 LLM（不是重生成，是带着错误信息修正想法）
    if errors:
        idea = self._understanding.refine(idea, errors)
        output = self._solve(idea)
        errors = self._hard_constraints.check(output)
        if errors:
            raise StageRejected(errors)  # 明确失败，不无限重试

    # 4. 类型 B：质量 → 确定性优化
    for _ in range(self.max_quality_iter):
        report = self._quality_rules.evaluate(output)
        if report.ok:
            break
        output = self._solver.improve(output, report)
        # 分数不再提升就提前停
        if not report.improved_since_last:
            break

    # 5. 类型 C：不做自动迭代
    #    输出带置信度 + 可视化对照，交给人

    return output
```

**三条明确的设计约束**：

1. **绝大多数迭代是确定性的**（求解器自己修），只有极少数需要问 LLM
2. **每次迭代必须有明确的"这次改了什么"**，不能是黑盒重试
3. **终止条件是"不再改进"或"达到上限"**，不是"跑到某次数"

---

## 7. 需要写进契约的东西

### 7.1 Stage 接口扩展

```python
class Stage(Protocol):
    ...
    max_legal_fix: int = 5          # 合法性修正上限
    max_quality_iter: int = 3       # 质量优化上限
    quality_rules: ConstraintSet    # 软规则集（区别于硬约束）
```

### 7.2 迭代 trace（调试与评估用）

```python
class IterationTrace(BaseModel):
    """一次迭代的记录——不暴露给用户，用于调试和评估收敛设计是否合理。"""
    iteration: int
    kind: Literal["legal_fix", "quality", "llm_refine"]
    violations_before: list[str]
    violations_after: list[str]
    changed: bool
```

**为什么必须有 trace**：不然永远回答不了"这个 Stage 到底迭代了几次、每次为什么迭代"，也就无法判断收敛设计对不对。

### 7.3 ConstraintRule 返回值扩展

当前是 `(bool, str)`，需要携带修复建议：

```python
@dataclass
class RuleViolation:
    rule: str
    message: str
    fix: dict | None = None        # 结构化修复指令，供求解器直接执行
```

---

## 8. 开发顺序建议（反直觉但重要）

### 先不要做迭代。

**理由**：如果单次求解 + 校验门就能达到 90% 通过率，迭代机制的收益很低，却引入复杂度、延迟和不可预测性。

**正确顺序**：

| 步骤 | 做什么 | 判断标准 |
|------|--------|---------|
| 1 | 先做**单次求解** + 校验门 | 测通过率 |
| 2 | 通过率低 → **优先改进单次求解** | 而不是加迭代 |
| 3 | 单次求解到瓶颈了 → **再加迭代** | 作为兜底 |

> **迭代是兜底手段，不是质量来源。**
>
> 很多人一开始就设计复杂迭代，结果迭代在补救一个本来就不该那么差的一次性生成。

---

## 9. 待决定的三个问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| 1 | 哪些 Stage 必须迭代，哪些一次过？ | ⬜ 待定 | 直接影响端到端延迟。`layout` 必须，`surface`/`stylize` 大概率一次过 |
| 2 | 软规则的清单和优先级 | 🟡 house 已完成 | `data/house/rules.json` 已落地（场景通用 7 条 + 9 个区域类型专属规则）。其余场景待补 |
| 3 | 置信度怎么产出、怎么呈现 | ⬜ 待定 | 决定类型 C 的"交给人"能否落地 |

### 9.1 各场景软规则清单进度

| 场景 | 状态 | 文件 |
|------|------|------|
| 室内 house | ✅ 初版（数据驱动） | `data/house/rules.json` |
| 城市 urban | ⬜ 待建 | — |
| 乡村 rural | ⬜ 待建 | — |
| 山林 mountain | ⬜ 待建 | — |
| 海洋 ocean | ⬜ 待建 | — |
| 沙漠 desert | ⬜ 待建 | — |

> **每一类业务场景都需要自己的软规则清单**——这是领域知识，不能靠 LLM 通用推理或某个专有算法替代。
> house 是第一个样板，其余场景照同样的结构（`scene_rules` + `region_rules`）填即可。

---

## 10. 一句话记住

> **能算的确定性修，不能算的交给人。**
>
> 迭代的价值不在"多试几次"，而在"每次都知道为什么没通过、该怎么修"。
