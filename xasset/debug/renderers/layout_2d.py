# xasset/debug/renderers/layout_2d.py
"""Layout 2D renderer: LayoutOutput + SceneUnderstandOutput -> PNG via matplotlib."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
import numpy as np

from xasset.pipeline.stages.layout_compose import LayoutOutput
from xasset.pipeline.stages.scene_understand import SceneUnderstandOutput
from xasset.debug.renderers.region_2d import FLOOR_COLOR, WALL_COLOR, REGION_COLORS

# Approximate footprint size for a placed group (meters)
GROUP_HALF_W = 0.4
GROUP_HALF_D = 0.4


def render_layout_2d(
    layout: LayoutOutput,
    understand: SceneUnderstandOutput,
    path: str,
) -> None:
    """Render room outlines and placed group footprints to a PNG file."""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_aspect("equal")
    ax.set_title(f"Layout Plan — {layout.scene_type}", fontsize=12)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")

    # Draw room outlines
    for region in understand.regions:
        bnd = region.boundary
        xs = [p[0] for p in bnd] + [bnd[0][0]]
        zs = [p[1] for p in bnd] + [bnd[0][1]]
        color = REGION_COLORS.get(region.region_type, FLOOR_COLOR)
        ax.fill(xs, zs, color=color, alpha=1.0, zorder=1)
        ax.plot(xs, zs, color=WALL_COLOR, linewidth=2.0, zorder=2)

        cx = sum(p[0] for p in bnd) / len(bnd)
        cz = sum(p[1] for p in bnd) / len(bnd)
        ax.text(cx, cz, region.region_type, ha="center", va="center",
                fontsize=7, color="#555555", zorder=3)

    # Draw placed groups as rotated rectangles + direction arrow + label
    for pg in layout.placed_groups:
        # position is [x, y, z] in cm -> convert to meters for xz plane
        px = pg.position[0] / 100.0
        pz = pg.position[2] / 100.0
        rot_deg = pg.rotation  # Y-axis rotation in degrees

        # Draw rotated rectangle
        rect = mpatches.Rectangle(
            (-GROUP_HALF_W, -GROUP_HALF_D),
            GROUP_HALF_W * 2, GROUP_HALF_D * 2,
            linewidth=1.5, edgecolor="#333333", facecolor="#FFD580", alpha=0.7,
            zorder=5,
        )
        transform = (
            mtransforms.Affine2D()
            .rotate_deg(-rot_deg)   # matplotlib Y-up, negate for XZ plane
            .translate(px, pz)
            + ax.transData
        )
        rect.set_transform(transform)
        ax.add_patch(rect)

        # Direction arrow (points along +Z before rotation, i.e. "front")
        rad = math.radians(-rot_deg)
        arrow_len = GROUP_HALF_D * 0.8
        dx = math.sin(rad) * arrow_len
        dz = math.cos(rad) * arrow_len
        ax.annotate(
            "", xy=(px + dx, pz + dz), xytext=(px, pz),
            arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.5),
            zorder=6,
        )

        # Label: group_code
        ax.text(px, pz, str(pg.group_code),
                ha="center", va="center", fontsize=6, color="#222222",
                fontweight="bold", zorder=7)

    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)
