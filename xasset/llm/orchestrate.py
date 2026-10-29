# xasset/llm/orchestrate.py
"""四阶段统一的 LLM 编排执行器。

把 research/unified-scene-pipeline/README.md 3.4 节的"LLM 原生阶段接口"
落成一个可复用的执行器骨架：

    输入数据 + 用户提示词 + 硬约束集
        ↓  build_request（各阶段提供 prompt + schema + constraints）
        ↓  provider.generate
        ↓  阶段输出（schema 固定、语义明确）
        ↓  constraint 校验闸门（强制，来自 tools/constraint）

本文件只提供骨架；每个阶段通过 Stage 提供自己的 prompt / schema / 约束
规则集 / 校验函数，作为参数注入。校验闸门失败时返回拒绝，不把非法产物
送入下游或呈现给用户。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from xasset.llm.provider import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    StubLLMProvider,
)


@dataclass
class StageLLMSpec:
    """一个 Stage 阶段的 LLM 编排说明。

    stage_key:
        阶段标识，对应四阶段主线。
    build_request:
        (ctx, 用户提示词) -> LLMRequest。由阶段实现，负责拼接 prompt、
        填 constraints 与 schema。
    validate:
        校验闸门：(ctx, LLM 结构化产物) -> ValidationResult。
        来自 tools/constraint，是强制的、无例外的。
    """

    stage_key: str
    build_request: Callable[[Any, str | None], LLMRequest]
    validate: Callable[[Any, Any], "ValidationResult"]


@dataclass
class ValidationResult:
    """约束校验闸门的输出。"""

    ok: bool
    reasons: list[str] = field(default_factory=list)

    @property
    def error_message(self) -> str:
        return "; ".join(self.reasons)


class LLMStageOrchestrator:
    """把 Stage 的 LLM 编排 spec 与一个 LLMProvider 绑定执行。"""

    def __init__(self, provider: LLMProvider, spec: StageLLMSpec) -> None:
        self._provider = provider
        self._spec = spec

    def run(self, ctx: Any, user_hint: str | None = None) -> tuple[Any | None, ValidationResult]:
        """执行一次阶段编排：LLM 生成 → 强制校验闸门。

        Returns
        -------
        (output, validation)
            output 为 None 当且仅当 LLM 生成失败（schema 层拒绝）或校验闸门
            拒绝。调用方应据此决定是否把产物写入 ctx.stage_outputs。
        """
        request = self._spec.build_request(ctx, user_hint)
        response: LLMResponse = self._provider.generate(request)

        if response.rejected or response.content is None:
            return None, ValidationResult(
                ok=False,
                reasons=[response.error or "LLM 结构化输出被拒绝"],
            )

        validation = self._spec.validate(ctx, response.content)
        if not validation.ok:
            return None, validation

        return response.content, validation


class StubStageOrchestrator(LLMStageOrchestrator):
    """占位编排器：返回阶段标识性空产物。

    用于算法重做过渡期，让六层 Stage 骨架在无真实 LLM 时仍可跑通。
    """

    def __init__(self, stage_key: str) -> None:
        super().__init__(StubLLMProvider(), self._build_stub_spec(stage_key))

    @staticmethod
    def _build_stub_spec(stage_key: str) -> StageLLMSpec:
        def _build_request(ctx: Any, user_hint: str | None) -> LLMRequest:
            return LLMRequest(stage_key=stage_key, prompt=user_hint or "")

        def _validate(ctx: Any, content: Any) -> ValidationResult:
            return ValidationResult(ok=True)

        return StageLLMSpec(
            stage_key=stage_key,
            build_request=_build_request,
            validate=_validate,
        )
