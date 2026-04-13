# tests/debug/test_debug_dump.py
import os
import math
import uuid
import pytest

from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.scene_understand import (
    SceneUnderstandOutput, SceneRegion, DoorInfo, WindowInfo, SceneUnderstandStage,
)
from xasset.pipeline.stages.mesh_build import MeshBuildStage
from xasset.debug.renderers.region_2d import render_region_2d
from xasset.debug.renderers.mesh_obj import export_mesh_obj


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


def _make_understand():
    return SceneUnderstandOutput(
        scene_type="house",
        regions=[SceneRegion(
            region_type="living_room",
            boundary=[[0, 0], [4, 0], [4, 3], [0, 3]],
            area=12.0, height=2.8,
            doors=[DoorInfo(
                id="d1", pts=[[1, 0], [2, 0], [2, 0.1], [1, 0.1]],
                normal=[0, 1], center=[1.5, 0], width=1.0, height=2.1,
                to_room=None,
            )],
            windows=[WindowInfo(
                id="w1", window_type="normal",
                pts=[[2.5, 3], [3.5, 3], [3.5, 3.1], [2.5, 3.1]],
                sill_height=0.9, height=1.5, width=1.0,
                depth=None, seg_start=[2.5, 3], seg_end=[3.5, 3],
            )],
        )],
    )


def _make_mesh_output():
    ctx = PipelineContext(
        job_id=str(uuid.uuid4()),
        input=PipelineInput(input_type="text", scene_type="house"),
    )
    SceneUnderstandStage().run(ctx)
    MeshBuildStage().run(ctx)
    return ctx.stage_outputs["geometry"]


# ---- region_2d tests ----

def test_render_region_2d_creates_png(tmp_dir):
    out = _make_understand()
    path = os.path.join(tmp_dir, "floor_plan.png")
    render_region_2d(out, path)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 1000


def test_render_region_2d_multi_region(tmp_dir):
    out = SceneUnderstandOutput(
        scene_type="house",
        regions=[
            SceneRegion(region_type="living_room", boundary=[[0, 0], [4, 0], [4, 3], [0, 3]], area=12.0, height=2.8),
            SceneRegion(region_type="bedroom", boundary=[[4, 0], [7, 0], [7, 3], [4, 3]], area=9.0, height=2.8),
        ],
    )
    path = os.path.join(tmp_dir, "multi.png")
    render_region_2d(out, path)
    assert os.path.exists(path)


# ---- mesh_obj tests ----

def test_export_mesh_obj_creates_files(tmp_dir):
    mesh_out = _make_mesh_output()
    obj_path = os.path.join(tmp_dir, "mesh.obj")
    export_mesh_obj(mesh_out, obj_path)
    assert os.path.exists(obj_path)
    assert os.path.exists(obj_path.replace(".obj", ".mtl"))


def test_export_mesh_obj_content(tmp_dir):
    mesh_out = _make_mesh_output()
    obj_path = os.path.join(tmp_dir, "mesh.obj")
    export_mesh_obj(mesh_out, obj_path)
    content = open(obj_path).read()
    assert "v " in content
    assert "f " in content
    assert "usemtl" in content


from xasset.debug.renderers.layout_2d import render_layout_2d
from xasset.debug import debug_dump
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.registry import StageRegistry
from xasset.pipeline.stages.layout_compose import HouseLayoutComposeStage
from xasset.pipeline.stages.stylize import StylizeStage
from xasset.services.generation import GenerationService
from xasset.services.sample_search import SampleSearchService
from xasset.jobs.store import InMemoryJobStore


def _make_layout_output():
    from xasset.pipeline.stages.layout_compose import LayoutOutput, PlacedGroup
    # PlacedGroup fields: group_code, region_type, position ([x,y,z] cm), rotation, role_assets
    return LayoutOutput(
        scene_type="house",
        placed_groups=[
            PlacedGroup(
                group_code=1001,
                region_type="living_room",
                position=[200.0, 0.0, 150.0],  # cm
                rotation=0.0,
                role_assets={"sofa": None, "table": None},
            ),
            PlacedGroup(
                group_code=1002,
                region_type="living_room",
                position=[300.0, 0.0, 250.0],  # cm
                rotation=45.0,
                role_assets={"chair": None},
            ),
        ],
    )


def test_render_layout_2d_creates_png(tmp_dir):
    understand = _make_understand()
    layout = _make_layout_output()
    path = os.path.join(tmp_dir, "layout.png")
    render_layout_2d(layout, understand, path)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 1000


def test_debug_dump_creates_expected_files(tmp_dir):
    registry = StageRegistry()
    registry.register(SceneUnderstandStage())
    registry.register(MeshBuildStage())
    registry.register(HouseLayoutComposeStage(sample_search=SampleSearchService([])))
    registry.register(StylizeStage())
    svc = GenerationService(pipeline=Pipeline(registry), job_store=InMemoryJobStore())
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = svc.submit(inp)
    result = svc.get_result(job_id)

    class FakeCtx:
        stage_outputs = result.stage_outputs

    files = debug_dump(FakeCtx(), output_dir=tmp_dir)
    assert len(files) >= 2
    assert any("understand" in f for f in files)
    assert any("geometry" in f and f.endswith(".obj") for f in files)
    for f in files:
        assert os.path.exists(f)
