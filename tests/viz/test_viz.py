# tests/viz/test_viz.py
"""可视化与指标测试。

用代码合成图片，不依赖外部资源，保证测试可重复。
"""
from pathlib import Path

import pytest

from xasset.pipeline.schemas import (
    ContourSemantics,
    Polygon,
    SceneRegion,
)
from xasset.viz import (
    compute_iou,
    compute_polygon_iou,
    plot_polygon_points,
    plot_regions,
    render_overlay,
    render_side_by_side,
)


@pytest.fixture
def sample_image(tmp_path):
    """合成一张 200x200 的白色图片，中间一个灰色方块。"""
    from PIL import Image, ImageDraw

    p = tmp_path / "sample.png"
    im = Image.new("RGB", (200, 200), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([50, 50, 150, 150], fill=(200, 200, 200))
    im.save(p)
    return p


@pytest.fixture
def sample_regions():
    return [
        SceneRegion(
            region_id="r1",
            region_type="bedroom",
            boundary=Polygon(points=[(50.0, 50.0), (150.0, 50.0),
                                     (150.0, 150.0), (50.0, 150.0)]),
            area=16.0,
            semantics=ContourSemantics(),
        ),
        SceneRegion(
            region_id="r2",
            region_type="kitchen",
            boundary=Polygon(points=[(10.0, 10.0), (40.0, 10.0),
                                     (40.0, 40.0), (10.0, 40.0)]),
            area=4.0,
            semantics=ContourSemantics(),
        ),
    ]


# ── 绘制 ────────────────────────────────────────────────────────────────

def test_render_overlay_creates_file(sample_image, sample_regions, tmp_path):
    out = tmp_path / "overlay.png"
    render_overlay(sample_image, sample_regions, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_render_side_by_side_creates_file(sample_image, sample_regions, tmp_path):
    out = tmp_path / "compare.png"
    render_side_by_side(sample_image, sample_regions, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_regions_creates_file(sample_regions, tmp_path):
    out = tmp_path / "contours.png"
    plot_regions(sample_regions, out, title="测试轮廓")
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_polygon_points_creates_file(tmp_path):
    out = tmp_path / "poly.png"
    plot_polygon_points(
        [[(0.0, 0.0), (5.0, 0.0), (5.0, 5.0), (0.0, 5.0)]],
        out,
    )
    assert out.exists()


def test_render_overlay_with_scale(sample_image, tmp_path):
    """给了像素/米比例时，米制坐标应被映射回像素。"""
    regions = [
        SceneRegion(
            region_id="r1",
            region_type="bedroom",
            boundary=Polygon(points=[(0.0, 0.0), (2.0, 0.0),
                                     (2.0, 2.0), (0.0, 2.0)]),
            area=4.0,
            semantics=ContourSemantics(),
        )
    ]
    out = tmp_path / "scaled.png"
    render_overlay(sample_image, regions, out, pixel_per_meter=50.0)
    assert out.exists()


def test_render_overlay_empty_regions(sample_image, tmp_path):
    """没有区域时也应能出图（不崩）。"""
    out = tmp_path / "empty.png"
    render_overlay(sample_image, [], out)
    assert out.exists()


# ── 指标 ────────────────────────────────────────────────────────────────

def test_iou_identical_polygons():
    p = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert compute_polygon_iou(p, p) == pytest.approx(1.0)


def test_iou_disjoint_polygons():
    a = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    b = [(10.0, 10.0), (11.0, 10.0), (11.0, 11.0), (10.0, 11.0)]
    assert compute_polygon_iou(a, b) == pytest.approx(0.0)


def test_iou_half_overlap():
    """两个 2x2 方块，重叠 1x2 = 2，并集 4+4-2 = 6 → IoU = 1/3。"""
    a = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
    b = [(1.0, 0.0), (3.0, 0.0), (3.0, 2.0), (1.0, 2.0)]
    assert compute_polygon_iou(a, b) == pytest.approx(2.0 / 6.0)


def test_iou_invalid_polygon():
    assert compute_polygon_iou([], [(0, 0), (1, 0), (1, 1)]) == 0.0


def test_compute_iou_batch(sample_regions):
    """批量 IoU：自己和自己比应为 1。"""
    result = compute_iou(sample_regions, sample_regions)
    assert result["r1"] == pytest.approx(1.0)
    assert result["r2"] == pytest.approx(1.0)


def test_compute_iou_missing_match(sample_regions):
    """预测里有但真值里没有的，记为 0。"""
    result = compute_iou(sample_regions, [])
    assert all(v == 0.0 for v in result.values())
