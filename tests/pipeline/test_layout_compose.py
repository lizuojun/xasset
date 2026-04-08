# tests/pipeline/test_layout_compose.py
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.scene_understand import (
    SceneUnderstandOutput, SceneRegion,
)
from xasset.pipeline.stages.layout_compose import (
    HouseLayoutComposeStage, LayoutOutput, PlacedGroup,
)
from xasset.services.mesh import MeshService
from xasset.services.sample_search import SampleSearchService


def _ctx_with_scene(region_type="living_room", style=None):
    inp = PipelineInput(input_type="text", scene_type="house", style=style)
    ctx = PipelineContext(job_id="j1", input=inp)
    ctx.stage_outputs["scene_understand"] = SceneUnderstandOutput(
        scene_type="house",
        style=style,
        regions=[
            SceneRegion(
                region_type=region_type,
                boundary=[[0, 0, 0], [500, 0, 0], [500, 0, 400], [0, 0, 400]],
                area=20.0,
            )
        ],
    )
    return ctx


def _make_stage():
    mesh_svc = MeshService()
    sample_svc = SampleSearchService([])
    return HouseLayoutComposeStage(mesh_service=mesh_svc, sample_search=sample_svc)


def test_stage_name_and_scene_types():
    assert HouseLayoutComposeStage.name == "layout_compose"
    assert "house" in HouseLayoutComposeStage.scene_types


def test_returns_layout_output():
    stage = _make_stage()
    ctx = _ctx_with_scene()
    stage.run(ctx)
    out = ctx.stage_outputs["layout_compose"]
    assert isinstance(out, LayoutOutput)
    assert out.scene_type == "house"


def test_living_room_gets_meeting_group():
    stage = _make_stage()
    ctx = _ctx_with_scene(region_type="living_room")
    stage.run(ctx)
    out: LayoutOutput = ctx.stage_outputs["layout_compose"]
    assert len(out.placed_groups) > 0
    group = out.placed_groups[0]
    assert isinstance(group, PlacedGroup)
    assert group.group_code == 100001   # house-meeting group code
    assert group.region_type == "living_room"


def test_placed_group_has_position():
    stage = _make_stage()
    ctx = _ctx_with_scene()
    stage.run(ctx)
    out: LayoutOutput = ctx.stage_outputs["layout_compose"]
    group = out.placed_groups[0]
    assert len(group.position) == 3


def test_unknown_region_type_produces_no_groups():
    stage = _make_stage()
    ctx = _ctx_with_scene(region_type="storage_room")
    stage.run(ctx)
    out: LayoutOutput = ctx.stage_outputs["layout_compose"]
    assert out.placed_groups == []
