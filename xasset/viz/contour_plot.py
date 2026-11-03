# xasset/viz/contour_plot.py
"""纯轮廓绘制 —— 不需要原图，直接把阶段产物画成线框图。

用途：
- 调试时快速看轮廓形状
- 没有原图时（如纯 SceneVector 输入）也能出图

与 overlay.py 的区别：
- overlay：叠在原图上，用于"识别得对不对"的对比
- contour_plot：从零画，用于"轮廓本身长什么样"
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

from xasset.pipeline.schemas import SceneRegion
from xasset.viz._font import configure_chinese_font

configure_chinese_font()

# 按区域类型区分的配色（未知类型用灰色）
REGION_COLORS: dict[str, str] = {
    "living_room": "#f5e6d3",
    "living_dining_room": "#f5e6d3",
    "bedroom": "#d3e6f5",
    "kids_room": "#e6d3f5",
    "kitchen": "#f5d3d3",
    "bathroom": "#d3f5f0",
    "balcony": "#e8f5d3",
    "dining_room": "#f5f0d3",
    "library": "#d3d9f5",
    "hallway": "#eeeeee",
    "unknown": "#dddddd",
}
DEFAULT_COLOR = "#dddddd"


def plot_regions(
    regions: list[SceneRegion],
    out_path: str | Path,
    *,
    show_labels: bool = True,
    show_openings: bool = True,
    dpi: int = 120,
    title: str | None = None,
) -> None:
    """把区域轮廓画成 2D 平面图。"""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")

    for region in regions:
        pts = list(region.boundary.points)
        if len(pts) < 3:
            continue

        color = REGION_COLORS.get(region.region_type, DEFAULT_COLOR)
        ax.add_patch(MplPolygon(
            pts, closed=True, fill=True, facecolor=color,
            edgecolor="#333333", linewidth=1.5,
        ))

        # 画开口（在轮廓边上的短线）
        if show_openings:
            for feat in region.semantics.openings:
                if len(feat.pts) >= 2:
                    xs = [p[0] for p in feat.pts]
                    zs = [p[1] for p in feat.pts]
                    ax.plot(xs, zs, color="#e74c3c", linewidth=3.0, solid_capstyle="butt")

        if show_labels:
            cx = sum(p[0] for p in pts) / len(pts)
            cz = sum(p[1] for p in pts) / len(pts)
            ax.text(cx, cz, f"{region.region_type}\n{region.area:.1f}m²",
                    ha="center", va="center", fontsize=8, color="#333333")

    if title:
        ax.set_title(title)

    ax.autoscale_view()
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    fig.savefig(str(out_path), dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_polygon_points(
    polygons: list[list[tuple[float, float]]],
    out_path: str | Path,
    *,
    dpi: int = 120,
) -> None:
    """最简绘制：只给多边形顶点列表（不需要 SceneRegion）。"""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")

    for pts in polygons:
        if len(pts) < 3:
            continue
        ax.add_patch(MplPolygon(
            list(pts), closed=True, fill=False,
            edgecolor="#2980b9", linewidth=2.0,
        ))

    ax.autoscale_view()
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    fig.savefig(str(out_path), dpi=dpi, bbox_inches="tight")
    plt.close(fig)
