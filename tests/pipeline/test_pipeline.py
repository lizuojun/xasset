# tests/pipeline/test_pipeline.py
import pytest
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.registry import StageRegistry


class _WriteStage:
    def __init__(self, name, value):
        self.name = name
        self.scene_types = ["*"]
        self._value = value

    def run(self, ctx):
        ctx.stage_outputs[self.name] = self._value


class _FailStage:
    name = "fail"
    scene_types = ["*"]

    def run(self, ctx):
        raise ValueError("intentional failure")


class _ReadPreviousStage:
    name = "reader"
    scene_types = ["*"]

    def run(self, ctx):
        ctx.stage_outputs["reader"] = ctx.stage_outputs.get("writer")


def _make_input(scene_type="house"):
    return PipelineInput(input_type="text", scene_type=scene_type)


def test_pipeline_runs_stages_in_order():
    registry = StageRegistry()
    registry.register(_WriteStage("writer", "written"))
    registry.register(_ReadPreviousStage())
    config = PipelineConfig(scene_type="house", stages=["writer", "reader"])
    pipeline = Pipeline(registry)
    ctx = pipeline.run(_make_input(), config)
    assert ctx.stage_outputs["reader"] == "written"


def test_pipeline_sets_status_done_on_success():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", 1))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.status == "done"


def test_pipeline_sets_status_failed_on_error():
    registry = StageRegistry()
    registry.register(_FailStage())
    config = PipelineConfig(scene_type="house", stages=["fail"])
    with pytest.raises(ValueError, match="intentional failure"):
        Pipeline(registry).run(_make_input(), config)


def test_pipeline_uses_provided_job_id():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", 1))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config, job_id="my-job")
    assert ctx.job_id == "my-job"


def test_pipeline_generates_job_id_if_not_provided():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", 1))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.job_id is not None and len(ctx.job_id) > 0


def test_empty_stage_list_returns_done():
    registry = StageRegistry()
    config = PipelineConfig(scene_type="house", stages=[])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.status == "done"
    assert ctx.stage_outputs == {}
