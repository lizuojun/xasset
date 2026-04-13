# xasset/debug/renderers/region_2d.py
"""2D region plan renderer: SceneUnderstandOutput -> PNG via matplotlib."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from xasset.pipeline.stages.scene_understand import SceneUnderstandOutput

REGION_COLORS = {
    "living_room": "#E8F4E8",
    "bedroom":     "#E8E8F4",
    "dining_room": "#F4F0E8",
    "kitchen":     "#F4E8E8",
    "bathroom":    "#E8F4F4",
    "balcony":     "#F0F4E8",
}
DEFAULT_REGION_COLOR = "#F5F5F5"


def render_region_2d(output: SceneUnderstandOutput, path: str) -> None:
    """Render all regions (boundary + doors + windows) to a PNG file."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect("equal")
    ax.set_title(f"Region Plan — {output.scene_type}", fontsize=12)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")

    for region in output.regions:
        bnd = region.boundary
        xs = [p[0] for p in bnd] + [bnd[0][0]]
        zs = [p[1] for p in bnd] + [bnd[0][1]]
        color = REGION_COLORS.get(region.region_type, DEFAULT_REGION_COLOR)
        ax.fill(xs, zs, color=color, alpha=0.6, zorder=1)
        ax.plot(xs, zs, color="#666666", linewidth=1.5, zorder=2)

        cx = sum(p[0] for p in bnd) / len(bnd)
        cz = sum(p[1] for p in bnd) / len(bnd)
        ax.text(cx, cz, f"{region.region_type}\n{region.area:.1f}m²",
                ha="center", va="center", fontsize=7, color="#333333", zorder=3)

        for door in region.doors:
            cx_d, cz_d = door.center
            nx, nz = door.normal
            hw = door.width / 2
            tx, tz = -nz, nx
            x0, z0 = cx_d - tx * hw, cz_d - tz * hw
            x1, z1 = cx_d + tx * hw, cz_d + tz * hw
            ax.plot([x0, x1], [z0, z1], color="red", linewidth=2, zorder=4)
            theta0 = math.degrees(math.atan2(tz, tx))
            arc = mpatches.Arc(
                (x0, z0), door.width, door.width,
                angle=0, theta1=theta0, theta2=theta0 + 90,
                color="red", linewidth=1, linestyle="--", zorder=4,
            )
            ax.add_patch(arc)

        for win in region.windows:
            if win.seg_start and win.seg_end:
                ax.plot(
                    [win.seg_start[0], win.seg_end[0]],
                    [win.seg_start[1], win.seg_end[1]],
                    color="steelblue", linewidth=3, zorder=4,
                )

    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)
