# tests/pipeline/test_registry.py
import pytest
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stage import Stage
from xasset.pipeline.registry import StageRegistry, StageNotFound


class _EchoStage:
    name = "echo"
    scene_types = ["house"]

    def run(self, ctx: PipelineContext) -> None:
        ctx.stage_outputs["echo"] = {"scene_type": ctx.input.scene_type}


class _WildcardStage:
    name = "wildcard"
    scene_types = ["*"]

    def run(self, ctx: PipelineContext) -> None:
        ctx.stage_outputs["wildcard"] = True


def _make_ctx(scene_type="house"):
    inp = PipelineInput(input_type="text", scene_type=scene_type)
    return PipelineContext(job_id="j1", input=inp)


def test_register_and_get():
    registry = StageRegistry()
    registry.register(_EchoStage())
    stage = registry.get("echo", "house")
    assert stage.name == "echo"


def test_get_missing_stage_raises():
    registry = StageRegistry()
    with pytest.raises(StageNotFound):
        registry.get("nonexistent", "house")


def test_get_wrong_scene_type_raises():
    registry = StageRegistry()
    registry.register(_EchoStage())
    with pytest.raises(StageNotFound):
        registry.get("echo", "urban")


def test_wildcard_scene_type_matches_any():
    registry = StageRegistry()
    registry.register(_WildcardStage())
    assert registry.get("wildcard", "house").name == "wildcard"
    assert registry.get("wildcard", "urban").name == "wildcard"
    assert registry.get("wildcard", "wild").name == "wildcard"


def test_specific_overrides_wildcard():
    """Scene-specific impl takes priority over wildcard."""
    class _HouseSpecific:
        name = "wildcard"
        scene_types = ["house"]
        def run(self, ctx): pass

    registry = StageRegistry()
    registry.register(_WildcardStage())
    registry.register(_HouseSpecific())
    assert registry.get("wildcard", "house").scene_types == ["house"]
    assert registry.get("wildcard", "urban").scene_types == ["*"]


def test_pipeline_for_returns_ordered_stages():
    from xasset.pipeline.pipeline import PipelineConfig
    registry = StageRegistry()
    registry.register(_EchoStage())
    registry.register(_WildcardStage())
    config = PipelineConfig(scene_type="house", stages=["wildcard", "echo"])
    stages = registry.pipeline_for(config)
    assert [s.name for s in stages] == ["wildcard", "echo"]
