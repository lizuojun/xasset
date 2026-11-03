# tests/test_pipeline_integration.py
"""端到端验证：Pipeline 按契约注入上游产物、强校验阶段产物类型。"""
import uuid

import pytest

from xasset.jobs.store import InMemoryJobStore
from xasset.pipeline.context import PipelineInput, VariationInput
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.registry import create_registry
from xasset.pipeline.schemas import (
    AccessoryOutput,
    GeometryOutput,
    LayoutOutput,
    StylizeOutput,
    SurfaceOutput,
    UnderstandOutput,
)
from xasset.pipeline.stage import StageDependencyMissing
from xasset.services.generation import GenerationService


def _make_full_service():
    return GenerationService(
        pipeline=Pipeline(create_registry()),
        job_store=InMemoryJobStore(),
    )


def test_full_house_pipeline_end_to_end():
    """完整管线跑通，六层都产出阶段产物。"""
    service = _make_full_service()
    inp = PipelineInput(
        input_type="text",
        scene_type="house",
        text_description="一个现代简约风格的客厅，约20平方米",
        style="现代简约",
    )
    job_id = service.submit(inp)

    assert service.get_status(job_id).status == "done"

    result = service.get_result(job_id)
    for layer in ("understand", "geometry", "layout", "surface", "accessory", "stylize"):
        assert layer in result.stage_outputs


def test_each_stage_produces_declared_type():
    """每个 Stage 的阶段产物符合其 output_type 契约。"""
    service = _make_full_service()
    job_id = service.submit(PipelineInput(input_type="text", scene_type="house", style="北欧"))
    out = service.get_result(job_id).stage_outputs

    assert isinstance(out["understand"], UnderstandOutput)
    assert isinstance(out["geometry"], GeometryOutput)
    assert isinstance(out["layout"], LayoutOutput)
    assert isinstance(out["surface"], SurfaceOutput)
    assert isinstance(out["accessory"], AccessoryOutput)
    assert isinstance(out["stylize"], StylizeOutput)


def test_understand_preserves_style():
    service = _make_full_service()
    job_id = service.submit(PipelineInput(input_type="text", scene_type="house", style="北欧"))
    out: UnderstandOutput = service.get_result(job_id).stage_outputs["understand"]
    assert out.scene_type == "house"
    assert out.style == "北欧"


def test_layout_stub_has_no_groups():
    service = _make_full_service()
    job_id = service.submit(PipelineInput(input_type="text", scene_type="house"))
    out: LayoutOutput = service.get_result(job_id).stage_outputs["layout"]
    assert out.placed_elements == []
    assert out.placed_features == []


def test_missing_dependency_raises():
    """只跑 layout 而不跑 understand 时，依赖校验应报错。"""
    pipeline = Pipeline(create_registry())
    inp = PipelineInput(input_type="text", scene_type="house")
    config = PipelineConfig(scene_type="house", stages=["layout"])

    with pytest.raises(StageDependencyMissing):
        pipeline.run(inp, config)


def test_partial_pipeline_understand_only():
    """只跑 understand（无上游依赖）可以成功。"""
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    config = PipelineConfig(scene_type="house", stages=["understand"])
    result = service.get_result(service.submit(inp, config=config))

    assert "understand" in result.stage_outputs
    assert "layout" not in result.stage_outputs


def test_variation_runs_full_pipeline_for_dependencies():
    """变体生成过渡期跑完整管线，以满足各 Stage 的 requires 依赖。"""
    service = _make_full_service()
    job_id = service.submit_variation(
        source_asset_id=uuid.uuid4(),
        variation=VariationInput(replace_accessories=True),
    )
    result = service.get_result(job_id)
    assert service.get_status(job_id).status == "done"
    assert "understand" in result.stage_outputs
    assert "layout" in result.stage_outputs
