# xasset/debug/renderers/house/layout_2d.py
"""Layout 2D renderer: LayoutOutput + SceneUnderstandOutput + WallSegments -> PNG via matplotlib.
Reuses shared door/window/curtain symbols from draw_utils, then overlays placed groups."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms

from xasset.pipeline.stages.layout.house.compose import LayoutOutput
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandOutput
from xasset.debug.renderers.house.draw_utils import (
    draw_door_jambs, draw_door_swing, draw_window_symbol, draw_curtain_zone, draw_main_door,
    FLOOR_COLOR, WALL_COLOR, REGION_COLORS,
)

GROUP_HALF_W = 0.4
GROUP_HALF_D = 0.4


def render_layout_2d(
    layout: LayoutOutput,
    understand: SceneUnderstandOutput,
    path: str,
    walls_by_region: dict | None = None,
    curtains_by_region: dict | None = None,
) -> None:
    walls_by_region = walls_by_region or {}
    curtains_by_region = curtains_by_region or {}

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_aspect("equal")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")

    id_to_region = {r.region_id: r for r in understand.regions}

    # Draw rooms: floor + walls + doors + windows + curtains
    for region in understand.regions:
        bnd = region.boundary
        xs = [p[0] for p in bnd] + [bnd[0][0]]
        zs = [p[1] for p in bnd] + [bnd[0][1]]
        color = REGION_COLORS.get(region.region_type, FLOOR_COLOR)
        ax.fill(xs, zs, color=color, alpha=1.0, zorder=1)
        ax.plot(xs, zs, color=WALL_COLOR, linewidth=2.0, zorder=2)

        cx = sum(p[0] for p in bnd) / len(bnd)
        cz = sum(p[1] for p in bnd) / len(bnd)
        ax.text(cx, cz, f"{region.region_type}\n{region.area:.1f}m2",
                ha="center", va="center", fontsize=7, color="#555555", zorder=3)

        segs = walls_by_region.get(region.region_id, [])
        for seg in segs:
            p0, p1 = seg.p0, seg.p1
            nx, nz = seg.inward_normal
            if seg.seg_type == "door":
                opens_into = seg.opens_into
                if opens_into is None:
                    draw_main_door(ax, p0, p1, nx, nz, bnd)
                elif opens_into == region.region_id:
                    draw_door_jambs(ax, p0, p1, nx, nz)
                    draw_door_swing(ax, p0, p1, nx, nz, bnd)
            elif seg.seg_type == "window":
                draw_window_symbol(ax, p0, p1, nx, nz)

        for cz in curtains_by_region.get(region.region_id, []):
            draw_curtain_zone(ax, cz)

    # Draw placed groups as rotated rectangles + direction arrow + label
    for pg in layout.placed_groups:
        px = pg.position[0]
        pz = pg.position[2]
        rot_deg = pg.rotation

        rect = mpatches.Rectangle(
            (-GROUP_HALF_W, -GROUP_HALF_D),
            GROUP_HALF_W * 2, GROUP_HALF_D * 2,
            linewidth=1.5, edgecolor="#333333", facecolor="#FFD580", alpha=0.7,
            zorder=5,
        )
        transform = (
            mtransforms.Affine2D()
            .rotate_deg(-rot_deg)
            .translate(px, pz)
            + ax.transData
        )
        rect.set_transform(transform)
        ax.add_patch(rect)

        rad = math.radians(-rot_deg)
        arrow_len = GROUP_HALF_D * 0.8
        dx = math.sin(rad) * arrow_len
        dz = math.cos(rad) * arrow_len
        ax.annotate(
            "", xy=(px + dx, pz + dz), xytext=(px, pz),
            arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.5),
            zorder=6,
        )

        ax.text(px, pz, str(pg.group_code),
                ha="center", va="center", fontsize=6, color="#222222",
                fontweight="bold", zorder=7)

    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)
