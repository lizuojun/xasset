# xasset/tools/constraint/__init__.py
"""硬约束校验闸门 —— A 类"非法"的确定性检查。

**硬约束 vs 软规则**（两个不同模块，边界清晰）：

| | 硬约束（本模块） | 软规则（tools/quality） |
|---|----------------|----------------------|
| 性质 | 绝对不合法，不可让步 | 偏好，可让步 |
| 例子 | 多边形自交、开口悬空 | 面积略小于典型、长宽比偏大 |
| 失败 | 必须修，修不好则失败 | 继续优化，优化不了也可接受 |
| fix | ✅ 需要（供求解器直接修） | ❌ 不需要 |

设计依据见 docs/iteration-convergence.md 第 3 节。

导出：
- ValidationResult  校验结果（违规列表 + ok + fixable）
- RuleViolation     单条违规（含 target_id / fix / message）
- ConstraintRule    规则签名 (ctx, output) -> RuleViolation | None
- ConstraintSet     某阶段的硬约束规则集
- understand_hard_constraints / layout_hard_constraints  已组装的规则集
"""
from xasset.tools.constraint.gate import (
    ConstraintRule,
    ConstraintSet,
    RuleViolation,
    ValidationResult,
)
from xasset.tools.constraint.builtin import (
    layout_hard_constraints,
    understand_hard_constraints,
)
from xasset.tools.constraint import standards

__all__ = [
    "ConstraintRule",
    "ConstraintSet",
    "RuleViolation",
    "ValidationResult",
    "understand_hard_constraints",
    "layout_hard_constraints",
    "standards",
]
