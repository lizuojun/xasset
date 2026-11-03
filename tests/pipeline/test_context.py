# tests/pipeline/test_context.py
import uuid
from xasset.pipeline.context import (
    PipelineInput, PipelineContext, VariationInput, RoleTarget, AssetTarget,
)


def test_pipeline_input_defaults():
    inp = PipelineInput(input_type="text", scene_type="house")
    assert inp.text_description is None
    assert inp.image_url is None
    assert inp.style is None
    assert inp.constraints == {}


def test_pipeline_context_stage_outputs_default_empty():
    inp = PipelineInput(input_type="text", scene_type="house")
    ctx = PipelineContext(job_id="j1", input=inp)
    assert ctx.stage_outputs == {}
    assert ctx.status == "running"
    assert ctx.error is None


def test_pipeline_context_stage_outputs_writable():
    inp = PipelineInput(input_type="text", scene_type="house")
    ctx = PipelineContext(job_id="j1", input=inp)
    ctx.stage_outputs["my_stage"] = {"result": 42}
    assert ctx.stage_outputs["my_stage"]["result"] == 42


def test_variation_input_defaults():
    v = VariationInput()
    assert v.replace_models is None
    assert v.replace_materials is None
    assert v.replace_lights is False
    assert v.replace_accessories is False


def test_role_target_fields():
    gid = uuid.uuid4()
    t = RoleTarget(group_instance_id=gid, role="sofa")
    assert t.role == "sofa"


def test_asset_target_fields():
    aid = uuid.uuid4()
    t = AssetTarget(asset_instance_id=aid)
    assert t.asset_instance_id == aid
