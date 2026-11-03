# xasset/viz/overlay.py
"""在原图上叠加轮廓 —— 用于「结果对比」（产品与调试共用）。

设计依据见 docs/iteration-convergence.md 4.3 节「结果核验：可视化对照」：
用户需要能直观确认"生成结果对不对"。

为什么放在 viz/ 而不是 tools/：
- tools/ 是主链路算法（几何/约束/软规则），参与数据生成
- viz/ 是可视化，不参与生成，但**属于产品**（用户要看对照图）
- debug/ 是纯开发期调试，不进产品
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

from xasset.pipeline.schemas import SceneRegion
from xasset.viz._font import configure_chinese_font

configure_chinese_font()


@dataclass
class OverlayStyle:
    """叠加样式（便于统一外观）。"""

    edge_color: str = "#e74c3c"
    fill_alpha: float = 0.25
    line_width: float = 2.0
    show_labels: bool = True
    label_fontsize: int = 7
    dpi: int = 120


def render_overlay(
    image_path: str | Path,
    regions: list[SceneRegion],
    out_path: str | Path,
    *,
    style: OverlayStyle | None = None,
    pixel_per_meter: float | None = None,
    origin_px: tuple[float, float] = (0.0, 0.0),
    flip_y: bool = False,
) -> None:
    """把区域轮廓画在原图上（半透明覆盖），保存为图片。

    Parameters
    ----------
    image_path : 原始图片路径
    regions : understand 阶段产物
    out_path : 输出图片路径
    style : 样式
    pixel_per_meter : 像素/米比例。给了才能把米制多边形映射回像素。
    origin_px : 米制原点在图片上的像素位置。
    flip_y : True 时按 px_row = H - z*ppm 映射（场景 Z 向上、图片 Y 向下）。
    """
    style = style or OverlayStyle()

    img = plt.imread(str(image_path))
    h_px = img.shape[0]
    fig, ax = plt.subplots(figsize=(10, 10 * img.shape[0] / img.shape[1]))
    ax.imshow(img)

    for region in regions:
        pts = _to_pixel(region.boundary.points, pixel_per_meter, origin_px,
                        image_height_px=h_px, flip_y=flip_y)
        if len(pts) < 3:
            continue

        ax.add_patch(MplPolygon(
            pts,
            closed=True,
            fill=True,
            facecolor=style.edge_color,
            alpha=style.fill_alpha,
            edgecolor=style.edge_color,
            linewidth=style.line_width,
        ))

        if style.show_labels:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            label = f"{region.region_type}\n{region.area:.1f}m²"
            ax.text(cx, cy, label, ha="center", va="center",
                    fontsize=style.label_fontsize, color="#222222",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7))

    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(str(out_path), dpi=style.dpi, bbox_inches="tight")
    plt.close(fig)


def _to_pixel(
    points: list[tuple[float, float]],
    ppm: float | None,
    origin: tuple[float, float],
    image_height_px: int | None = None,
    flip_y: bool = False,
) -> list[tuple[float, float]]:
    """米制坐标 → 像素坐标。

    flip_y=True 时按 px_row = H - z*ppm 映射（因为场景 Z 向上、图片 Y 向下）。
    """
    if ppm is None:
        return list(points)
    if flip_y and image_height_px is not None:
        return [
            (origin[0] + x * ppm, image_height_px - z * ppm)
            for x, z in points
        ]
    return [(origin[0] + x * ppm, origin[1] + z * ppm) for x, z in points]


def render_side_by_side(
    image_path: str | Path,
    regions: list[SceneRegion],
    out_path: str | Path,
    *,
    style: OverlayStyle | None = None,
    pixel_per_meter: float | None = None,
    origin_px: tuple[float, float] = (0.0, 0.0),
    flip_y: bool = False,
) -> None:
    """并排对比：左=原图，右=叠加轮廓。"""
    style = style or OverlayStyle()

    img = plt.imread(str(image_path))
    h_px = img.shape[0]
    fig, axes = plt.subplots(1, 2, figsize=(18, 9 * img.shape[0] / img.shape[1]))

    axes[0].imshow(img)
    axes[0].set_title("原图")
    axes[0].set_axis_off()

    axes[1].imshow(img)
    for region in regions:
        pts = _to_pixel(region.boundary.points, pixel_per_meter, origin_px,
                        image_height_px=h_px, flip_y=flip_y)
        if len(pts) < 3:
            continue
        axes[1].add_patch(MplPolygon(
            pts, closed=True, fill=True,
            facecolor=style.edge_color, alpha=style.fill_alpha,
            edgecolor=style.edge_color, linewidth=style.line_width,
        ))
        if style.show_labels:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            axes[1].text(cx, cy, f"{region.region_type}\n{region.area:.1f}m²",
                         ha="center", va="center", fontsize=style.label_fontsize,
                         bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7))
    axes[1].set_title(f"识别轮廓（{len(regions)} 个区域）")
    axes[1].set_axis_off()

    plt.tight_layout()
    fig.savefig(str(out_path), dpi=style.dpi, bbox_inches="tight")
    plt.close(fig)
