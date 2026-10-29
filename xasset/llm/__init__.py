# xasset/llm/__init__.py
"""LLM 编排层——算法全面重做后的 Stage 主干。

每个 Stage 的算法不再手写规则逻辑，而是走统一的 LLM 原生阶段接口
（research/unified-scene-pipeline/README.md 3.4 节）。本层提供：

- LLMProvider         抽象底座（可替换，不绑定具体模型/平台）
- LLMStageOrchestrator 阶段编排执行器（输入+提示词+约束 → LLM → 校验闸门）
- StageLLMSpec         阶段编排说明（prompt/schema/约束规则集的注入点）

底座未定，当前以 Stub 占位，保证骨架可跑通。
"""
from xasset.llm.provider import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    StubLLMProvider,
)
from xasset.llm.orchestrate import (
    LLMStageOrchestrator,
    StageLLMSpec,
    StubStageOrchestrator,
    ValidationResult,
)

__all__ = [
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "StubLLMProvider",
    "LLMStageOrchestrator",
    "StageLLMSpec",
    "StubStageOrchestrator",
    "ValidationResult",
]
