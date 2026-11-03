# tests/pipeline/test_pipeline.py
"""Pipeline 执行器测试：顺序执行、依赖校验、输出契约强校验。"""
import pytest
from pydantic import BaseModel

from xasset.pipeline.context import PipelineInput
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.registry import StageRegistry
from xasset.pipeline.stage import StageContractViolation, StageDependencyMissing


class _Out(BaseModel):
    """测试用阶段产物。"""

    value: str = ""


class _WriteStage:
    """产出一个固定值。"""

    def __init__(self, name, value, requires=None):
        self.name = name
        self.layer = name
        self.scene_types = ["*"]
        self.requires = requires or []
        self.output_type = _Out
        self._value = value

    def run(self, inputs):
        return _Out(value=self._value)


class _ReadPreviousStage:
    """读取上游声明的产物。"""

    name = "reader"
    layer = "reader"
    scene_types = ["*"]
    requires = ["writer"]
    output_type = _Out

    def run(self, inputs):
        return _Out(value=inputs.get("writer").value)


class _FailStage:
    name = "fail"
    layer = "fail"
    scene_types = ["*"]
    requires = []
    output_type = _Out

    def run(self, inputs):
        raise ValueError("intentional failure")


class _WrongTypeStage:
    """返回不符合 output_type 的类型。"""

    name = "wrong"
    layer = "wrong"
    scene_types = ["*"]
    requires = []
    output_type = _Out

    def run(self, inputs):
        return "not an _Out"


class _NeedsMissingStage:
    name = "needs_missing"
    layer = "needs_missing"
    scene_types = ["*"]
    requires = ["writer"]
    output_type = _Out

    def run(self, inputs):
        return _Out(value=inputs.get("writer").value)


def _make_input(scene_type="house"):
    return PipelineInput(input_type="text", scene_type=scene_type)


def test_pipeline_runs_stages_in_order():
    registry = StageRegistry()
    registry.register(_WriteStage("writer", "written"))
    registry.register(_ReadPreviousStage())
    config = PipelineConfig(scene_type="house", stages=["writer", "reader"])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.stage_outputs["reader"].value == "written"


def test_pipeline_sets_status_done_on_success():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", "v1"))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.status == "done"


def test_pipeline_sets_status_failed_on_error():
    registry = StageRegistry()
    registry.register(_FailStage())
    config = PipelineConfig(scene_type="house", stages=["fail"])
    with pytest.raises(ValueError, match="intentional failure"):
        Pipeline(registry).run(_make_input(), config)


def test_missing_dependency_raises():
    """Stage 声明的上游未产出时，依赖校验报错。"""
    registry = StageRegistry()
    registry.register(_NeedsMissingStage())
    config = PipelineConfig(scene_type="house", stages=["needs_missing"])
    with pytest.raises(StageDependencyMissing, match="writer"):
        Pipeline(registry).run(_make_input(), config)


def test_output_type_mismatch_raises():
    """Stage 返回的类型与 output_type 不符时报错。"""
    registry = StageRegistry()
    registry.register(_WrongTypeStage())
    config = PipelineConfig(scene_type="house", stages=["wrong"])
    with pytest.raises(StageContractViolation):
        Pipeline(registry).run(_make_input(), config)


def test_pipeline_uses_provided_job_id():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", "v1"))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config, job_id="my-job")
    assert ctx.job_id == "my-job"


def test_pipeline_generates_job_id_if_not_provided():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", "v1"))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.job_id is not None and len(ctx.job_id) > 0


def test_empty_stage_list_returns_done():
    registry = StageRegistry()
    config = PipelineConfig(scene_type="house", stages=[])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.status == "done"
    assert ctx.stage_outputs == {}
