# tests/llm/test_orchestrate.py
"""测试 LLM 编排骨架（llm/orchestrate）—— StubProvider 跑通。"""
from xasset.llm import (
    StubLLMProvider,
    StubStageOrchestrator,
    LLMRequest,
    LLMResponse,
)


def test_stub_provider_returns_stub_content():
    p = StubLLMProvider()
    resp = p.generate(LLMRequest(stage_key="test", prompt="hi"))
    assert isinstance(resp, LLMResponse)
    assert resp.content == {"stage_key": "test", "status": "stub"}


def test_stub_orchestrator_runs():
    orch = StubStageOrchestrator("scene_understand")
    output, validation = orch.run(ctx=None, user_hint="三室两厅")
    assert output is not None
    assert validation.ok


def test_orchestrator_rejects_on_rejected_response():
    from xasset.llm.orchestrate import LLMStageOrchestrator, StageLLMSpec
    from xasset.llm.provider import LLMProvider, LLMRequest, LLMResponse

    class RejectingProvider(LLMProvider):
        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(content=None, rejected=True, error="schema violation")

    def build_request(ctx, hint):
        return LLMRequest(stage_key="x", prompt=hint or "")

    def validate(ctx, content):
        from xasset.tools.constraint import ValidationResult
        return ValidationResult.pass_()

    spec = StageLLMSpec("x", build_request, validate)
    orch = LLMStageOrchestrator(RejectingProvider(), spec)
    output, validation = orch.run(None, None)
    assert output is None
    assert not validation.ok
    assert "schema violation" in validation.reasons
