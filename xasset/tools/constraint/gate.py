# xasset/tools/constraint/gate.py
"""硬约束校验闸门 —— Artist 范式下 A 类"非法"的检查。

设计依据见 docs/iteration-convergence.md 第 3 节。

**硬约束 vs 软规则的边界**（两者在不同模块，不要混）：

| | 硬约束（本模块） | 软规则（tools/quality） |
|---|----------------|----------------------|
| 性质 | 绝对不合法，**不可让步** | 偏好，**可让步** |
| 例子 | 多边形自交、开口悬空、门宽 0.3m | 面积略小于典型、长宽比偏大 |
| 失败后果 | 必须修，修不好则 Stage 失败 | 继续优化，优化不了也可接受 |
| 是否需要 fix | ✅ **需要**，供求解器直接执行 | ❌ 不需要 |

校验是强制的、无例外的：即使某算法的"生成过程自带合法性保证"，
闸门依然执行（通常直接通过），不为"捷径"所跳过。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class RuleViolation:
    """一条硬约束被违反。

    fix 字段是关键：它让求解器可以**直接执行确定性修复**，而不必回问 LLM。
    这是"确定性迭代"能成立的前提（见 iteration-convergence.md 3.3 节）。
    """

    rule: str
    message: str
    target_id: str | None = None       # 违规的对象 id（区域 / 开口 / 内容）
    fix: dict | None = None            # 结构化修复指令，如 {"op":"move","delta":-0.42}
    severity: str = "error"            # 预留给未来分级，当前一律 error


@dataclass
class ValidationResult:
    """硬约束校验结果。"""

    violations: list[RuleViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations

    @property
    def reasons(self) -> list[str]:
        return [f"[{v.rule}] {v.message}" for v in self.violations]

    @property
    def error_message(self) -> str:
        return "; ".join(self.reasons)

    @property
    def fixable(self) -> list[RuleViolation]:
        """带修复建议的违规（求解器可直接处理的部分）。"""
        return [v for v in self.violations if v.fix is not None]

    @classmethod
    def pass_(cls) -> "ValidationResult":
        return cls()

    @classmethod
    def fail(cls, *violations: RuleViolation) -> "ValidationResult":
        return cls(violations=list(violations))


# 一条硬约束规则：(ctx, output) -> RuleViolation | None
# 返回 None 表示通过。
ConstraintRule = Callable[[Any, Any], "RuleViolation | None"]


class ConstraintSet:
    """某阶段的硬约束规则集。

    Parameters
    ----------
    stage_key:
        阶段标识（对应六层 Stage：understand / geometry / layout /
        surface / accessory / stylize）。
    rules:
        有序规则列表。fail_fast=True 时首个违规即短路。
    """

    def __init__(
        self,
        stage_key: str,
        rules: list[ConstraintRule],
        fail_fast: bool = False,
    ) -> None:
        self.stage_key = stage_key
        self.rules = rules
        self.fail_fast = fail_fast

    def validate(self, ctx: Any, output: Any) -> ValidationResult:
        violations: list[RuleViolation] = []
        for rule in self.rules:
            v = rule(ctx, output)
            if v is not None:
                violations.append(v)
                if self.fail_fast:
                    break
        return ValidationResult(violations=violations) if violations else ValidationResult.pass_()
