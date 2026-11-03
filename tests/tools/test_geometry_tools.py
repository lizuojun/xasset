# tests/tools/test_geometry_tools.py
"""测试迁入 tools/geometry 的独立几何工具（算法重做后保留的工具）。"""
import math

import pytest

from xasset.tools.geometry import (
    check_poly_clock,
    ear_cut_triangulation,
    build_polygon_mesh,
    polygon_area,
    compute_wall_uv,
    map_uv_planar,
    normalize_polygon,
    normalize_scene_vector,
    NormalizeResult,
)


# ---- 三角剖分 / 绕向 ----

def test_check_poly_clock_ccw():
    poly = [[0, 0], [1, 0], [1, 1], [0, 1]]
    assert check_poly_clock(poly) == False  # CCW


def test_check_poly_clock_cw():
    poly = [[0, 0], [0, 1], [1, 1], [1, 0]]
    assert check_poly_clock(poly) == True  # CW


def test_polygon_area_square():
    poly = [[0, 0], [4, 0], [4, 5], [0, 5]]
    assert abs(polygon_area(poly) - 20.0) < 1e-9


def test_ear_cut_square():
    poly = [[0, 0], [1, 0], [1, 1], [0, 1]]
    tris = ear_cut_triangulation(poly)
    assert len(tris) == 2
    for tri in tris:
        assert len(tri) == 3


def test_ear_cut_triangle():
    poly = [[0, 0], [1, 0], [0.5, 1]]
    tris = ear_cut_triangulation(poly)
    assert len(tris) == 1
    assert len(tris[0]) == 3


def test_build_polygon_mesh_square():
    poly_3d = [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]]
    normal = [0, 1, 0]
    verts, faces = build_polygon_mesh(poly_3d, normal)
    assert len(verts) == 4
    assert len(faces) == 2


# ---- UV ----

def test_compute_wall_uv_simple():
    verts = [[0, 0, 0], [2, 0, 0], [2, 3, 0], [0, 3, 0]]
    uvs = compute_wall_uv(verts, u_axis=[1, 0, 0], v_axis=[0, 1, 0])
    assert len(uvs) == 4
    assert uvs[0] == pytest.approx([0.0, 0.0], abs=1e-5)
    assert uvs[1] == pytest.approx([2.0, 0.0], abs=1e-5)
    assert uvs[3] == pytest.approx([0.0, 3.0], abs=1e-5)


def test_map_uv_planar_floor():
    verts = [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]]
    uvs = map_uv_planar(verts, normal=[0, 1, 0])
    assert len(uvs) == 4
    assert uvs[0] == pytest.approx([0.0, 0.0], abs=1e-5)
    assert uvs[2] == pytest.approx([1.0, 1.0], abs=1e-5)


def test_map_uv_planar_wall_z():
    verts = [[0, 0, 2], [1, 0, 2], [1, 2, 2], [0, 2, 2]]
    uvs = map_uv_planar(verts, normal=[0, 0, 1])
    assert len(uvs) == 4
    assert uvs[0] == pytest.approx([0.0, 0.0], abs=1e-5)
    assert uvs[2] == pytest.approx([1.0, 2.0], abs=1e-5)


# ---- 多边形归一化 ----

def test_normalize_clean_polygon_unchanged():
    pts = [[0, 0], [4, 0], [4, 3], [0, 3]]
    result = normalize_polygon(pts)
    assert result is not None
    assert len(result) == 4


def test_normalize_short_segment_removed():
    pts = [[0, 0], [0.02, 0], [4, 0], [4, 3], [0, 3]]
    result = normalize_polygon(pts)
    assert result is not None
    assert len(result) == 4


def test_normalize_collinear_vertex_removed_by_deviation():
    pts = [[0, 0], [2, 0.01], [4, 0], [4, 3], [0, 3]]
    result = normalize_polygon(pts)
    assert result is not None
    assert len(result) == 4


def test_normalize_collinear_vertex_removed_by_angle():
    angle_rad = math.radians(2)
    mid = [2 + 0.5 * math.sin(angle_rad), 0.5 * (1 - math.cos(angle_rad))]
    pts = [[0, 0], mid, [4, 0], [4, 3], [0, 3]]
    result = normalize_polygon(pts)
    assert result is not None
    assert len(result) == 4


def test_normalize_degenerate_polygon_returns_none():
    pts = [[0, 0], [0.01, 0], [0.02, 0]]
    result = normalize_polygon(pts)
    assert result is None


def test_normalize_cw_polygon_converted_to_ccw():
    pts_cw = [[0, 0], [0, 3], [4, 3], [4, 0]]
    assert check_poly_clock(pts_cw) == True
    result = normalize_polygon(pts_cw)
    assert result is not None
    assert check_poly_clock(result) == False


def test_normalize_scene_vector_basic():
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
