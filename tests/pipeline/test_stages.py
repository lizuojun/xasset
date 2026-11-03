# tests/pipeline/test_stages.py
"""Stage 契约测试：requires / output_type / run(inputs)。"""
import pytest

from xasset.pipeline.context import PipelineInput
from xasset.pipeline.schemas import (
    AccessoryOutput,
    GeometryOutput,
    LayoutOutput,
    StylizeOutput,
    SurfaceOutput,
    UnderstandOutput,
)
from xasset.pipeline.stage import StageInputs
from xasset.pipeline.stages.accessory.stage import AccessoryStage
from xasset.pipeline.stages.geometry.house.mesh_build import MeshBuildStage
from xasset.pipeline.stages.layout.house.compose import HouseLayoutComposeStage
from xasset.pipeline.stages.stylize.stylize import StylizeStage
from xasset.pipeline.stages.surface.stage import SurfaceStage
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage


def _inputs(scene_type="house", style=None, **upstream):
    inp = PipelineInput(input_type="text", scene_type=scene_type, style=style)
    return StageInputs(inp, upstream)


def test_understand_returns_typed_output():
    stage = SceneUnderstandStage()
    out = stage.run(_inputs(style="现代简约"))
    assert isinstance(out, UnderstandOutput)
    assert out.scene_type == "house"
    assert out.style == "现代简约"


def test_understand_stub_returns_empty_regions():
    out = SceneUnderstandStage().run(_inputs())
    assert out.regions == []


def test_geometry_requires_understand():
    assert MeshBuildStage.requires == ["understand"]
    assert MeshBuildStage.output_type is GeometryOutput


def test_layout_requires_understand_only():
    assert HouseLayoutComposeStage.requires == ["understand"]
    assert HouseLayoutComposeStage.output_type is LayoutOutput


def test_surface_requires_understand_and_geometry():
    assert SurfaceStage.requires == ["understand", "geometry"]
    assert SurfaceStage.output_type is SurfaceOutput


def test_accessory_requires_understand_and_layout():
    assert AccessoryStage.requires == ["understand", "layout"]
    assert AccessoryStage.output_type is AccessoryOutput


def test_stylize_requires_all_upstreams():
    assert set(StylizeStage.requires) == {
        "understand", "geometry", "layout", "surface", "accessory",
    }
    assert StylizeStage.output_type is StylizeOutput


def test_accessing_undeclared_upstream_raises():
    """未在 requires 中声明的上游不可访问。"""
    stage = SurfaceStage()
    inputs = _inputs(understand=UnderstandOutput(scene_type="house"))
    # geometry 未注入
    with pytest.raises(KeyError):
        inputs.geometry


def test_stage_name_and_scene_types():
    assert SceneUnderstandStage.name == "scene_understand"
    assert SceneUnderstandStage.layer == "understand"
    assert "*" in SceneUnderstandStage.scene_types
    assert StylizeStage.name == "stylize"
    assert StylizeStage.layer == "stylize"
    assert "*" in StylizeStage.scene_types
