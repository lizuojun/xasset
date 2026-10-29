# xasset/debug/renderers/house/region_2d.py
"""2D region plan renderer: SceneUnderstandOutput -> PNG via matplotlib."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandOutput
from xasset.debug.renderers.house.draw_utils import (
    draw_window_symbol, draw_door_jambs, draw_door_swing, draw_sliding_door, draw_main_door,
    FLOOR_COLOR, WALL_COLOR, STRUCT_COLOR, DOOR_COLOR, WINDOW_COLOR, REGION_COLORS,
)

FLOOR_COLOR  = FLOOR_COLOR
WALL_COLOR   = WALL_COLOR
STRUCT_COLOR = STRUCT_COLOR
DOOR_COLOR   = DOOR_COLOR
WINDOW_COLOR = WINDOW_COLOR

# 按 region_type 定制填充色；当前 house 统一色，将来室外/城市可按需扩充
REGION_COLORS: dict[str, str] = REGION_COLORS

# ── helpers ──────────────────────────────────────────────────────────────────

def _proj_t(p0, p1, pt):
    """Project pt onto segment p0→p1, return parameter t (may be outside [0,1])."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    len2 = dx * dx + dz * dz
    if len2 < 1e-12:
        return None
    return ((pt[0] - p0[0]) * dx + (pt[1] - p0[1]) * dz) / len2


def _find_edge(boundary, seg_start, seg_end):
    """Return (edge_idx, t0, t1) for the boundary edge that contains this opening."""
    n = len(boundary)
    best = None
    best_perp = float("inf")
    for i in range(n):
        p0, p1 = boundary[i], boundary[(i + 1) % n]
        t0 = _proj_t(p0, p1, seg_start)
        t1 = _proj_t(p0, p1, seg_end)
        if t0 is None:
            continue
        if not (-0.05 <= t0 <= 1.05 and -0.05 <= t1 <= 1.05):
            continue
        dx, dz = p1[0] - p0[0], p1[1] - p0[1]
        length = math.hypot(dx, dz)
        if length < 1e-9:
            continue
        perp = abs((seg_start[0] - p0[0]) * dz - (seg_start[1] - p0[1]) * dx) / length
        if perp < best_perp:
            best_perp = perp
            best = (i, min(t0, t1), max(t0, t1))
    return best


def _lerp(p0, p1, t):
    return (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))


# ── main renderer ─────────────────────────────────────────────────────────────

def render_region_2d(output: SceneUnderstandOutput, path: str) -> None:
    """Render all regions (boundary + doors + windows) to a PNG file."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect("equal")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")

    # Track drawn door symbols by position to avoid drawing shared doors twice.
    # Key: frozenset of rounded (x, z) endpoint pairs — identical for both sides of a shared door.
    for region in output.regions:
        bnd = region.boundary
        n = len(bnd)

        # Fill floor polygon
        xs = [p[0] for p in bnd] + [bnd[0][0]]
        zs = [p[1] for p in bnd] + [bnd[0][1]]
        color = REGION_COLORS.get(region.region_type, FLOOR_COLOR)
        ax.fill(xs, zs, color=color, alpha=1.0, zorder=1)

        # Map each opening to its boundary edge
        structural = set(region.structural_edges)
        edge_opens: dict = {}  # edge_idx -> [(t0, t1, type, obj)]

        for door in region.doors:
            if door.seg_start and door.seg_end:
                r = _find_edge(bnd, door.seg_start, door.seg_end)
                if r:
                    ei, t0, t1 = r
                    edge_opens.setdefault(ei, []).append((t0, t1, "door", door))

        for win in region.windows:
            if win.seg_start and win.seg_end:
                r = _find_edge(bnd, win.seg_start, win.seg_end)
                if r:
                    ei, t0, t1 = r
                    edge_opens.setdefault(ei, []).append((t0, t1, "win", win))

        # Draw each boundary edge with gaps at openings
        for i in range(n):
            p0, p1 = bnd[i], bnd[(i + 1) % n]
            is_struct = i in structural
            wc = STRUCT_COLOR if is_struct else WALL_COLOR
            lw = 5.0 if is_struct else 2.0

            # Interior normal (left normal of CCW polygon edge)
            dx, dz = p1[0] - p0[0], p1[1] - p0[1]
            elen = math.hypot(dx, dz)
            int_nx = -dz / elen if elen > 1e-9 else 0.0
            int_nz =  dx / elen if elen > 1e-9 else 0.0

            opens = sorted(edge_opens.get(i, []), key=lambda o: o[0])

            if not opens:
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                        color=wc, linewidth=lw, zorder=2)
                continue

            cur = 0.0
            for t0, t1, otype, obj in opens:
                # Wall segment before this opening
                if t0 > cur + 1e-6:
                    pa, pb = _lerp(p0, p1, cur), _lerp(p0, p1, t0)
                    ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
                            color=wc, linewidth=lw, zorder=2)

                # Opening symbol
                oa, ob = _lerp(p0, p1, t0), _lerp(p0, p1, t1)
                if otype == "door":
                    opens_into = obj.opens_into
                    door_type  = obj.door_type
                    if opens_into is None:
                        draw_main_door(ax, oa, ob, int_nx, int_nz, bnd)
                    elif door_type == "sliding":
                        if opens_into == region.region_id:
                            draw_door_jambs(ax, oa, ob, int_nx, int_nz)
                            draw_sliding_door(ax, oa, ob, int_nx, int_nz)
                    elif opens_into == region.region_id:
                        draw_door_jambs(ax, oa, ob, int_nx, int_nz)
                        draw_door_swing(ax, oa, ob, int_nx, int_nz, bnd)
                    # else: shared swing door owned by the other room — gap only, no symbol
                    else:
                        pass
                else:  # window
                    draw_window_symbol(ax, oa, ob, int_nx, int_nz)

                cur = t1

            # Remaining wall after last opening
            if cur < 1.0 - 1e-6:
                pa = _lerp(p0, p1, cur)
                ax.plot([pa[0], p1[0]], [pa[1], p1[1]],
                        color=wc, linewidth=lw, zorder=2)

        # Region label
        cx = sum(p[0] for p in bnd) / n
        cz = sum(p[1] for p in bnd) / n
        ax.text(cx, cz, f"{region.region_type}\n{region.area:.1f}m2",
                ha="center", va="center", fontsize=7, color="#555555", zorder=3)

    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)
