# tests/services/test_generation.py
import pytest
from xasset.pipeline.context import PipelineInput, VariationInput
from xasset.services.generation import GenerationService
from xasset.services.mesh import MeshService
from xasset.services.sample_search import SampleSearchService
from xasset.jobs.store import InMemoryJobStore
from xasset.pipeline.registry import StageRegistry
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.stages.scene_understand import SceneUnderstandStage
from xasset.pipeline.stages.layout_compose import HouseLayoutComposeStage
from xasset.pipeline.stages.stylize import StylizeStage


def _make_service():
    registry = StageRegistry()
    registry.register(SceneUnderstandStage())
    registry.register(HouseLayoutComposeStage(
        mesh_service=MeshService(),
        sample_search=SampleSearchService([]),
    ))
    registry.register(StylizeStage())
    pipeline = Pipeline(registry)
    job_store = InMemoryJobStore()
    return GenerationService(pipeline=pipeline, job_store=job_store)


def test_submit_returns_job_id():
    service = _make_service()
    inp = PipelineInput(input_type="text", scene_type="house", text_description="客厅")
    job_id = service.submit(inp)
    assert isinstance(job_id, str)
    assert len(job_id) > 0


def test_get_status_done_after_sync_submit():
    service = _make_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = service.submit(inp)
    status = service.get_status(job_id)
    assert status.status == "done"
    assert status.job_id == job_id


def test_get_result_has_stage_outputs():
    service = _make_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = service.submit(inp)
    result = service.get_result(job_id)
    assert result.job_id == job_id
    assert "layout_compose" in result.stage_outputs


def test_get_status_unknown_job_raises():
    service = _make_service()
    with pytest.raises(KeyError):
        service.get_status("nonexistent-job-id")


def test_submit_with_custom_config():
    service = _make_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    config = PipelineConfig(scene_type="house", stages=["scene_understand"])
    job_id = service.submit(inp, config=config)
    result = service.get_result(job_id)
    assert "scene_understand" in result.stage_outputs
    assert "layout_compose" not in result.stage_outputs


def test_submit_variation_returns_job_id():
    import uuid
    service = _make_service()
    variation = VariationInput(replace_accessories=True)
    job_id = service.submit_variation(
        source_asset_id=uuid.uuid4(),
        variation=variation,
    )
    assert isinstance(job_id, str)
