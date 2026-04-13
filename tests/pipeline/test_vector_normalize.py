# tests/pipeline/test_vector_normalize.py
import math
import pytest
from xasset.pipeline.stages.vector_normalize import normalize_polygon, normalize_scene_vector, NormalizeResult


def test_clean_polygon_unchanged():
    """正常矩形，无需规整，原样返回。"""
    pts = [[0, 0], [4, 0], [4, 3], [0, 3]]
    result = normalize_polygon(pts)
    assert result is not None
    assert len(result) == 4


def test_short_segment_removed():
    """相邻两点距离 < 5cm，后一个顶点应被删除。"""
    pts = [[0, 0], [0.02, 0], [4, 0], [4, 3], [0, 3]]
    result = normalize_polygon(pts)
    assert result is not None
    assert len(result) == 4


def test_collinear_vertex_removed_by_deviation():
    """中间顶点偏离共线 < 5cm，应被删除。"""
    pts = [[0, 0], [2, 0.01], [4, 0], [4, 3], [0, 3]]
    result = normalize_polygon(pts)
    assert result is not None
    assert len(result) == 4


def test_collinear_vertex_removed_by_angle():
    """相邻两段夹角 < 5°，中间顶点应被删除。"""
    angle_rad = math.radians(2)
    mid = [2 + 0.5 * math.sin(angle_rad), 0.5 * (1 - math.cos(angle_rad))]
    pts = [[0, 0], mid, [4, 0], [4, 3], [0, 3]]
    result = normalize_polygon(pts)
    assert result is not None
    assert len(result) == 4


def test_degenerate_polygon_returns_none():
    """规整后顶点 < 3，返回 None。"""
    pts = [[0, 0], [0.01, 0], [0.02, 0]]
    result = normalize_polygon(pts)
    assert result is None


def test_cw_polygon_converted_to_ccw():
    """顺时针输入，输出应翻转为逆时针。"""
    from xasset.pipeline.stages.mesh_utils import check_poly_clock
    pts_cw = [[0, 0], [0, 3], [4, 3], [4, 0]]
    assert check_poly_clock(pts_cw) == True
    result = normalize_polygon(pts_cw)
    assert result is not None
    assert check_poly_clock(result) == False


def test_normalize_scene_vector_basic():
    """正常 scene_vector 规整后区域数不变。"""
    rv = {
        "rooms": [{
            "id": "r1",
            "type": "living_room",
            "floor": [[0, 0], [4, 0], [4, 3], [0, 3]],
            "doors": [],
            "windows": [],
        }]
    }
    result = normalize_scene_vector(rv)
    assert isinstance(result, NormalizeResult)
    assert len(result.scene_vector["rooms"]) == 1
    assert result.excluded_room_ids == []


def test_normalize_scene_vector_excludes_degenerate_room():
    """退化房间被排除，excluded_room_ids 中有该房间 id。"""
    rv = {
        "rooms": [
            {
                "id": "bad_room",
                "type": "living_room",
                "floor": [[0, 0], [0.01, 0], [0.02, 0]],
                "doors": [],
                "windows": [],
            },
            {
                "id": "good_room",
                "type": "bedroom",
                "floor": [[0, 0], [3, 0], [3, 3], [0, 3]],
                "doors": [],
                "windows": [],
            },
        ]
    }
    result = normalize_scene_vector(rv)
    assert len(result.scene_vector["rooms"]) == 1
    assert result.scene_vector["rooms"][0]["id"] == "good_room"
    assert "bad_room" in result.excluded_room_ids


def test_normalize_scene_vector_excludes_degenerate_door():
    """退化门被排除，excluded_opening_ids 中有该门 id。"""
    rv = {
        "rooms": [{
            "id": "r1",
            "type": "living_room",
            "floor": [[0, 0], [4, 0], [4, 3], [0, 3]],
            "doors": [
                {"id": "d_bad", "pts": [[1, 0], [1.01, 0], [1.02, 0]]},
                {"id": "d_good", "pts": [[2, 0], [3, 0], [3, 0.1], [2, 0.1]]},
            ],
            "windows": [],
        }]
    }
    result = normalize_scene_vector(rv)
    doors = result.scene_vector["rooms"][0]["doors"]
    assert len(doors) == 1
    assert doors[0]["id"] == "d_good"
    assert "d_bad" in result.excluded_opening_ids
