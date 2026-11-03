# tests/tools/test_contour.py
"""轮廓处理测试 —— mask → 多边形 → 正交化 → 尺度推断。

这是 understand 视觉路线的第 ③ 步，完全确定性，必须严格测试。
"""
import math

import pytest

from xasset.tools.geometry.contour import (
    ScaleInfo,
    ensure_ccw,
    infer_scale_from_area,
    infer_scale_from_reference,
    mask_to_polygon,
    orthogonalize,
    pixels_to_polygon,
    simplify_polygon,
    trace_contour,
)


# ── 轮廓跟踪 ────────────────────────────────────────────────────────────

def test_trace_contour_empty_mask():
    assert trace_contour([]) == []
    assert trace_contour([[False, False], [False, False]]) == []


def test_trace_contour_single_pixel():
    mask = [[False, False], [False, True]]
    c = trace_contour(mask)
    assert len(c) >= 1
    assert (1, 1) in c


def test_trace_contour_rectangle():
    """实心矩形应能追踪出轮廓。"""
    mask = [
        [False, False, False, False],
        [False, True,  True,  False],
        [False, True,  True,  False],
        [False, False, False, False],
    ]
    c = trace_contour(mask)
    assert len(c) >= 4
    # 所有点都应落在前景像素上
    for r, col in c:
        assert mask[r][col]


def test_trace_contour_l_shape():
    """L 形应能正确追踪（验证不是简单的凸包）。"""
    mask = [
        [True,  True,  False],
        [True,  True,  False],
        [True,  True,  True],
    ]
    c = trace_contour(mask)
    assert len(c) >= 6


# ── 尺度推断 ────────────────────────────────────────────────────────────

def test_infer_scale_from_reference():
    """用已知参照物（如门宽 0.9m）反推尺度。"""
    # 图上量得 90 像素 = 0.9 米 → 100 像素/米
    s = infer_scale_from_reference(px_length=90, real_length_m=0.9)
    assert s.pixels_per_meter == pytest.approx(100.0)
    assert s.source == "explicit"


def test_infer_scale_from_reference_rejects_invalid():
    with pytest.raises(ValueError):
        infer_scale_from_reference(0, 1.0)
    with pytest.raises(ValueError):
        infer_scale_from_reference(10, 0)


def test_infer_scale_from_area():
    """按典型面积反推尺度。"""
    # 10000 像素面积，典型 10m² → 1000 px/m² → sqrt ≈ 31.6 px/m
    s = infer_scale_from_area(px_area=10000, expected_area_m2=(10.0, 10.0))
    assert s.pixels_per_meter == pytest.approx(math.sqrt(1000), rel=1e-6)
    assert s.source == "area_prior"


def test_pixels_to_polygon_converts_correctly():
    """像素坐标应正确换算为米（且 Y 翻转为 Z）。"""
    s = ScaleInfo(pixels_per_meter=100.0, source="test")
    # origin=(0,0)，点(0,100) → 向右 100px = 1m
    pts = pixels_to_polygon([(0, 0), (0, 100)], s, origin=(0, 0))
    assert pts[0] == pytest.approx((0.0, 0.0))
    assert pts[1] == pytest.approx((1.0, 0.0))


# ── 简化 ────────────────────────────────────────────────────────────────

def test_simplify_removes_collinear_points():
    """共线点应被移除。"""
    pts = [(0, 0), (1, 0), (2, 0), (2, 2), (0, 2)]
    out = simplify_polygon(pts, tolerance_m=0.01)
    assert len(out) < len(pts)
    assert len(out) >= 3


def test_simplify_keeps_corners():
    """明显的拐角不能被简化掉。"""
    pts = [(0, 0), (5, 0), (5, 5), (0, 5)]
    out = simplify_polygon(pts, tolerance_m=0.05)
    assert len(out) == 4


def test_simplify_short_input_unchanged():
    pts = [(0, 0), (1, 0), (1, 1)]
    assert simplify_polygon(pts) == pts


# ── 正交化 ──────────────────────────────────────────────────────────────

def test_orthogonalize_snaps_near_horizontal():
    """接近水平的边应被吸附为水平。"""
    # 第二条边几乎水平（略斜 5 度）
    pts = [(0.0, 0.0), (5.0, 0.44), (5.0, 5.0), (0.0, 5.0)]
    out = orthogonalize(pts, angle_tolerance_deg=15.0)
    # 第二条边应变成水平：终点 z 与起点 z 相同
    assert out[1][1] == pytest.approx(out[0][1])


def test_orthogonalize_snaps_near_vertical():
    """接近垂直的边应被吸附为垂直。"""
    pts = [(0.0, 0.0), (5.0, 0.0), (5.44, 5.0), (0.0, 5.0)]
    out = orthogonalize(pts, angle_tolerance_deg=15.0)
    # 第三条边应变成垂直：终点 x 与起点 x 相同
    assert out[2][0] == pytest.approx(out[1][0])


def test_orthogonalize_leaves_diagonal_alone():
    """明显倾斜的边（45度）不应被动。"""
    pts = [(0.0, 0.0), (5.0, 5.0), (0.0, 10.0)]
    out = orthogonalize(pts, angle_tolerance_deg=15.0)
    assert out == pts


# ── 绕向 ────────────────────────────────────────────────────────────────

def test_ensure_ccw_reverses_clockwise():
    cw = [(0, 0), (0, 5), (5, 5), (5, 0)]
    ccw = ensure_ccw(cw)
    # 计算有符号面积，应为正（CCW）
    n = len(ccw)
    area2 = sum(ccw[i][0] * ccw[(i + 1) % n][1] - ccw[(i + 1) % n][0] * ccw[i][1]
                for i in range(n))
    assert area2 > 0


def test_ensure_ccw_keeps_ccw():
    ccw = [(0, 0), (5, 0), (5, 5), (0, 5)]
    out = ensure_ccw(ccw)
    n = len(out)
    area2 = sum(out[i][0] * out[(i + 1) % n][1] - out[(i + 1) % n][0] * out[i][1]
                for i in range(n))
    assert area2 > 0


# ── 完整链路 ────────────────────────────────────────────────────────────

def test_mask_to_polygon_rectangle_area():
    """10x10 像素矩形，100px/m → 0.1m x 0.1m = 0.01m²。"""
    mask = [[True] * 10 for _ in range(10)]
    scale = ScaleInfo(pixels_per_meter=100.0, source="test")
    result = mask_to_polygon(mask, scale, simplify_tolerance_m=0.001)

    assert len(result.polygon) >= 3
    # 容许一定误差（轮廓跟踪是像素级）
    assert 0.005 < result.area_m2 < 0.02


def test_mask_to_polygon_empty():
    result = mask_to_polygon([], ScaleInfo(100.0, "test"))
    assert result.polygon == []
    assert result.area_m2 == 0.0


def test_mask_to_polygon_with_orthogonalize():
    """正交化后应保持矩形形状。"""
    mask = [[True] * 20 for _ in range(10)]
    scale = ScaleInfo(pixels_per_meter=10.0, source="test")
    result = mask_to_polygon(
        mask, scale, simplify_tolerance_m=0.5, orthogonalize_result=True
    )
    assert result.orthogonalized
    assert len(result.polygon) >= 4
    # 2m x 1m 大约 2㎡
    assert 1.0 < result.area_m2 < 3.0


def test_mask_to_polygon_is_ccw():
    """输出多边形应是 CCW。"""
    mask = [[True] * 10 for _ in range(10)]
    result = mask_to_polygon(mask, ScaleInfo(100.0, "test"))
    pts = result.polygon
    n = len(pts)
    area2 = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
                for i in range(n))
    assert area2 > 0
