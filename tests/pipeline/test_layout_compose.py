# tests/pipeline/test_layout_compose.py
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.understand.scene_understand import (
    SceneUnderstandOutput, SceneRegion,
)
from xasset.pipeline.stages.layout.house.compose import (
    HouseLayoutComposeStage, LayoutOutput,
)
from xasset.services.sample_search import SampleSearchService


def _ctx_with_scene(region_type="living_room", style=None):
    inp = PipelineInput(input_type="text", scene_type="house", style=style)
    ctx = PipelineContext(job_id="j1", input=inp)
    ctx.stage_outputs["understand"] = SceneUnderstandOutput(
        scene_type="house",
        style=style,
        regions=[
            SceneRegion(
                region_type=region_type,
                boundary=[[0, 0], [5, 0], [5, 4], [0, 4]],
                area=20.0,
                region_id="test_room",
            )
        ],
    )
    return ctx


def _make_stage():
    return HouseLayoutComposeStage()


def test_stage_name_and_scene_types():
    assert HouseLayoutComposeStage.name == "layout_compose"
    assert HouseLayoutComposeStage.layer == "layout"
    assert "house" in HouseLayoutComposeStage.scene_types


def test_returns_layout_output():
    stage = _make_stage()
    ctx = _ctx_with_scene()
    stage.run(ctx)
    out = ctx.stage_outputs["layout"]
    assert isinstance(out, LayoutOutput)
    assert out.scene_type == "house"


def test_living_room_placed_groups_is_stub_empty():
    """Furniture group placement (zone planning) is not yet implemented — stub returns no groups."""
    stage = _make_stage()
    ctx = _ctx_with_scene(region_type="living_room")
    stage.run(ctx)
    out: LayoutOutput = ctx.stage_outputs["layout"]
    assert out.placed_groups == []


def test_region_type_corrected_to_living_dining_room():
    stage = _make_stage()
    ctx = _ctx_with_scene(region_type="living_room")
    stage.run(ctx)
    understand = ctx.stage_outputs["understand"]
    assert understand.regions[0].region_type == "living_dining_room"


def test_unknown_region_type_produces_no_groups():
    stage = _make_stage()
    ctx = _ctx_with_scene(region_type="storage_room")
    stage.run(ctx)
    out: LayoutOutput = ctx.stage_outputs["layout"]
    assert out.placed_groups == []
