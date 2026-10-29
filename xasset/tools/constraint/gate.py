# xasset/tools/constraint/gate.py
"""约束校验闸门基础类型。

校验闸门与"工具"的边界（docs/algorithm-rebuild-plan.md 4.2）：
- 闸门只做"通过/不通过 + 原因"的校验，不产生新数据
- 每个阶段提供自己的规则集（阶段 2 最厚：闭合/自交/面积/开口落边界等，
  见 research/unified-scene-pipeline/README.md 4.2 节）

校验是强制的、无例外的：即使某算法的"生成过程自带合法性保证"，闸门
依然执行（通常直接通过），不为"捷径"所跳过。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ValidationResult:
    """约束校验闸门的输出。"""

    ok: bool
    reasons: list[str] = field(default_factory=list)

    @classmethod
    def pass_(cls) -> "ValidationResult":
        return cls(ok=True)

    @classmethod
    def fail(cls, *reasons: str) -> "ValidationResult":
        return cls(ok=False, reasons=list(reasons))

    @property
    def error_message(self) -> str:
        return "; ".join(self.reasons)


# 一条约束规则：给定阶段上下文 + 产物，返回 (是否通过, 不通过原因)。
ConstraintRule = Callable[[Any, Any], tuple[bool, str]]


class ConstraintSet:
    """某阶段的约束规则集。

    Parameters
    ----------
    stage_key:
        阶段标识（scene_understand / boundary_features / group_layout /
        scene_generation）。
    rules:
        有序规则列表。首条失败即短路（fail_fast=True），或收集全部原因
        （fail_fast=False）。
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
        reasons: list[str] = []
        for rule in self.rules:
            ok, reason = rule(ctx, output)
            if not ok:
                reasons.append(reason)
                if self.fail_fast:
                    break
        if reasons:
            return ValidationResult.fail(*reasons)
        return ValidationResult.pass_()
