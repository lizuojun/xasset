# xasset/tools/constraint/__init__.py
"""约束校验闸门——跨四阶段复用的通用校验能力。

依据 research/unified-scene-pipeline/README.md 4.1 节原则：无论候选结果
来自 LLM 还是自然语言编辑，任何要呈现给用户或送下游的结果，必须先过约束
校验，无例外。

- ValidationResult  校验结果（通过/拒绝 + 原因列表）
- ConstraintRule    单条约束规则（可组合）
- ConstraintSet     某阶段的约束规则集（pass_all / collect_all_reasons）
"""
from xasset.tools.constraint.gate import (
    ValidationResult,
    ConstraintRule,
    ConstraintSet,
)

__all__ = [
    "ValidationResult",
    "ConstraintRule",
    "ConstraintSet",
]
