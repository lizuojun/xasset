# tests/test_pipeline_integration.py
"""
端到端验证：文字描述 → Pipeline → house 布局结果
"""
from xasset.pipeline.context import PipelineInput, VariationInput
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.registry import StageRegistry
from xasset.pipeline.stages.scene_understand import SceneUnderstandStage, SceneUnderstandOutput
from xasset.pipeline.stages.layout_compose import HouseLayoutComposeStage, LayoutOutput
from xasset.pipeline.stages.stylize import StylizeStage, StylizeOutput
from xasset.services.generation import GenerationService
from xasset.services.mesh import MeshService
from xasset.services.sample_search import SampleSearchService
from xasset.jobs.store import InMemoryJobStore
import uuid


def _make_full_service():
    registry = StageRegistry()
    registry.register(SceneUnderstandStage())
    registry.register(HouseLayoutComposeStage(
        mesh_service=MeshService(),
        sample_search=SampleSearchService([]),
    ))
    registry.register(StylizeStage())
    return GenerationService(
        pipeline=Pipeline(registry),
        job_store=InMemoryJobStore(),
    )


def test_full_house_pipeline_end_to_end():
    """文字描述 → 完整 Pipeline → 三个 Stage 都产生输出"""
    service = _make_full_service()
    inp = PipelineInput(
        input_type="text",
        scene_type="house",
        text_description="一个现代简约风格的客厅，约20平方米",
        style="现代简约",
    )
    job_id = service.submit(inp)

    status = service.get_status(job_id)
    assert status.status == "done"

    result = service.get_result(job_id)
    assert "scene_understand" in result.stage_outputs
    assert "layout_compose" in result.stage_outputs
    assert "stylize" in result.stage_outputs


def test_scene_understand_output_structure():
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house", style="北欧")
    job_id = service.submit(inp)
    result = service.get_result(job_id)

    out: SceneUnderstandOutput = result.stage_outputs["scene_understand"]
    assert out.scene_type == "house"
    assert out.style == "北欧"
    assert len(out.regions) > 0


def test_layout_output_has_placed_groups():
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = service.submit(inp)
    result = service.get_result(job_id)

    out: LayoutOutput = result.stage_outputs["layout_compose"]
    assert isinstance(out, LayoutOutput)
    assert len(out.placed_groups) > 0
    group = out.placed_groups[0]
    assert group.group_code == 100001
    assert group.region_type == "living_room"
    assert len(group.position) == 3


def test_layout_group_has_all_roles():
    """会客组 (100001) 应包含 sofa, coffee_table, rug, accessory 四个角色"""
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = service.submit(inp)
    result = service.get_result(job_id)

    out: LayoutOutput = result.stage_outputs["layout_compose"]
    group = out.placed_groups[0]
    assert "sofa" in group.role_assets
    assert "coffee_table" in group.role_assets


def test_variation_pipeline_skips_scene_understand():
    """变体生成不执行 scene_understand Stage"""
    service = _make_full_service()
    variation = VariationInput(replace_accessories=True)
    job_id = service.submit_variation(
        source_asset_id=uuid.uuid4(),
        variation=variation,
    )
    result = service.get_result(job_id)
    assert "scene_understand" not in result.stage_outputs
    assert "layout_compose" in result.stage_outputs


def test_partial_pipeline_config():
    """只跑 scene_understand，layout_compose 不执行"""
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    config = PipelineConfig(scene_type="house", stages=["scene_understand"])
    job_id = service.submit(inp, config=config)
    result = service.get_result(job_id)
    assert "scene_understand" in result.stage_outputs
    assert "layout_compose" not in result.stage_outputs
