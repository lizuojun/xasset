# tests/pipeline/test_scene_understand.py
import pytest
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.scene_understand import (
    SceneUnderstandStage, SceneUnderstandOutput, SceneRegion,
)


def test_parse_scene_vector_basic():
    """有 scene_vector 时正确解析 region"""
    scene_vector = {
        "meta": {"coordinate": "xzy", "unit": "m"},
        "rooms": [{
            "id": "r1", "type": "living_room", "height": 2.8,
            "floor": [[0, 0], [4, 0], [4, 5], [0, 5]],
            "doors": [], "windows": [], "holes": []
        }]
    }
    inp = PipelineInput(input_type="vector", scene_type="house", scene_vector=scene_vector)
    ctx = PipelineContext(job_id="j1", input=inp)
    SceneUnderstandStage().run(ctx)
    out: SceneUnderstandOutput = ctx.stage_outputs["understand"]
    assert len(out.regions) == 1
    region = out.regions[0]
    assert region.region_type == "living_room"
    assert abs(region.area - 20.0) < 0.01   # 4*5=20 m²
    assert region.height == 2.8


def test_parse_door_geometry():
    """门的 normal/center/width 由 pts 正确计算"""
    scene_vector = {
        "meta": {"coordinate": "xzy", "unit": "m"},
        "rooms": [{
            "id": "r1", "type": "living_room", "height": 2.8,
            "floor": [[0, 0], [4, 0], [4, 5], [0, 5]],
            "doors": [{
                "id": "d1",
                "pts": [[1, 0], [2, 0], [2, 0], [1, 0]],   # 1m 宽，沿 x 轴
                "height": 2.1, "to_room": None
            }],
            "windows": [], "holes": []
        }]
    }
    inp = PipelineInput(input_type="vector", scene_type="house", scene_vector=scene_vector)
    ctx = PipelineContext(job_id="j1", input=inp)
    SceneUnderstandStage().run(ctx)
    region = ctx.stage_outputs["understand"].regions[0]
    assert len(region.doors) == 1
    door = region.doors[0]
    assert abs(door.width - 1.0) < 0.01
    assert abs(door.center[0] - 1.5) < 0.01
    assert door.height == 2.1


def test_parse_window_defaults():
    """缺少 sill_height 时使用 HOUSE_DEFAULTS"""
    scene_vector = {
        "meta": {"coordinate": "xzy", "unit": "m"},
        "rooms": [{
            "id": "r1", "type": "bedroom", "height": 2.8,
            "floor": [[0, 0], [3, 0], [3, 4], [0, 4]],
            "doors": [],
            "windows": [{
                "id": "w1", "window_type": "normal",
                "pts": [[0.5, 0], [1.5, 0], [1.5, 0], [0.5, 0]],
                # 不提供 sill_height / height
            }],
            "holes": []
        }]
    }
    inp = PipelineInput(input_type="vector", scene_type="house", scene_vector=scene_vector)
    ctx = PipelineContext(job_id="j1", input=inp)
    SceneUnderstandStage().run(ctx)
    region = ctx.stage_outputs["understand"].regions[0]
    win = region.windows[0]
    assert win.sill_height == 0.9    # HOUSE_DEFAULTS["window_sill_height"]
    assert win.height == 1.5         # HOUSE_DEFAULTS["window_height"]


def test_constraints_override_defaults():
    """constraints 可覆盖 HOUSE_DEFAULTS"""
    scene_vector = {
        "meta": {"coordinate": "xzy", "unit": "m"},
        "rooms": [{
            "id": "r1", "type": "living_room", "height": None,
            "floor": [[0, 0], [5, 0], [5, 6], [0, 6]],
            "doors": [], "windows": [], "holes": []
        }]
    }
    inp = PipelineInput(
        input_type="vector", scene_type="house",
        scene_vector=scene_vector,
        constraints={"room_height": 3.2}
    )
    ctx = PipelineContext(job_id="j1", input=inp)
    SceneUnderstandStage().run(ctx)
    region = ctx.stage_outputs["understand"].regions[0]
    assert region.height == 3.2


def test_bay_window_has_depth():
    """飘窗解析出 depth 字段"""
    scene_vector = {
        "meta": {"coordinate": "xzy", "unit": "m"},
        "rooms": [{
            "id": "r1", "type": "bedroom", "height": 2.8,
            "floor": [[0, 0], [4, 0], [4, 5], [0, 5]],
            "doors": [],
            "windows": [{
                "id": "bw1", "window_type": "bay",
                "pts": [[1, 0], [3, 0], [3, 0], [1, 0], [1, -0.6], [3, -0.6]],
                "sill_height": 0.45, "height": 1.5, "depth": 0.6
            }],
            "holes": []
        }]
    }
    inp = PipelineInput(input_type="vector", scene_type="house", scene_vector=scene_vector)
    ctx = PipelineContext(job_id="j1", input=inp)
    SceneUnderstandStage().run(ctx)
    win = ctx.stage_outputs["understand"].regions[0].windows[0]
    assert win.window_type == "bay"
    assert win.depth == 0.6
