# tests/pipeline/test_stages.py
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.scene_understand import (
    SceneUnderstandStage, SceneUnderstandOutput, SceneRegion,
)
from xasset.pipeline.stages.stylize import StylizeStage, StylizeOutput


def _ctx(scene_type="house", style=None):
    inp = PipelineInput(input_type="text", scene_type=scene_type, style=style)
    return PipelineContext(job_id="j1", input=inp)


def test_scene_understand_stub_returns_output():
    stage = SceneUnderstandStage()
    ctx = _ctx(scene_type="house", style="现代简约")
    stage.run(ctx)
    out: SceneUnderstandOutput = ctx.stage_outputs["understand"]
    assert isinstance(out, SceneUnderstandOutput)
    assert out.scene_type == "house"
    assert len(out.regions) > 0


def test_scene_understand_stub_region_fields():
    stage = SceneUnderstandStage()
    ctx = _ctx()
    stage.run(ctx)
    out: SceneUnderstandOutput = ctx.stage_outputs["understand"]
    region: SceneRegion = out.regions[0]
    assert region.region_type in ("living_room", "bedroom", "dining_room")
    assert region.area > 0
    assert len(region.boundary) >= 3


def test_scene_understand_preserves_style():
    stage = SceneUnderstandStage()
    ctx = _ctx(style="北欧")
    stage.run(ctx)
    out: SceneUnderstandOutput = ctx.stage_outputs["understand"]
    assert out.style == "北欧"


def test_stylize_stub_returns_output():
    stage = StylizeStage()
    ctx = _ctx()
    stage.run(ctx)
    out: StylizeOutput = ctx.stage_outputs["stylize"]
    assert isinstance(out, StylizeOutput)


def test_stage_name_and_scene_types():
    assert SceneUnderstandStage.name == "scene_understand"
    assert SceneUnderstandStage.layer == "understand"
    assert "*" in SceneUnderstandStage.scene_types
    assert StylizeStage.name == "stylize"
    assert StylizeStage.layer == "stylize"
    assert "*" in StylizeStage.scene_types
