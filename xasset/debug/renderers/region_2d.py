# xasset/debug/renderers/region_2d.py
"""2D region plan renderer: SceneUnderstandOutput -> PNG via matplotlib."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from xasset.pipeline.stages.scene_understand import SceneUnderstandOutput

FLOOR_COLOR  = "#F0EDE8"   # 地板填充（默认）
WALL_COLOR   = "#555555"   # 普通隔墙
STRUCT_COLOR = "#1A1A1A"   # 承重墙
DOOR_COLOR   = "#C0392B"   # 门
WINDOW_COLOR = "#2980B9"   # 窗

# 按 region_type 定制填充色；当前 house 统一色，将来室外/城市可按需扩充
REGION_COLORS: dict[str, str] = {
    "living_room":  FLOOR_COLOR,
    "bedroom":      FLOOR_COLOR,
    "dining_room":  FLOOR_COLOR,
    "kitchen":      FLOOR_COLOR,
    "bathroom":     FLOOR_COLOR,
    "balcony":      FLOOR_COLOR,
    # outdoor（占位）
    # "forest":     "#D4EDDA",
    # "road":       "#D6D3C4",
}

# 窗符号的半宽偏移（模拟墙体厚度，三线间距）
_WIN_HALF = 0.06   # m


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


def _draw_door(ax, p_hinge, p_free, int_nx, int_nz):
    """Draw door panel line + 90° arc sweeping into the room interior."""
    ax.plot([p_hinge[0], p_free[0]], [p_hinge[1], p_free[1]],
            color=DOOR_COLOR, linewidth=2.0, zorder=4)

    door_len = math.hypot(p_free[0] - p_hinge[0], p_free[1] - p_hinge[1])
    if door_len < 1e-6:
        return

    # Direction from hinge to free end
    tx = (p_free[0] - p_hinge[0]) / door_len
    tz = (p_free[1] - p_hinge[1]) / door_len
    theta_free = math.degrees(math.atan2(tz, tx))

    # cross(tangent, interior_normal) > 0 → normal is CCW from tangent → sweep CCW
    cross = tx * int_nz - tz * int_nx
    if cross > 0:
        t1, t2 = theta_free, theta_free + 90
    else:
        t1, t2 = theta_free - 90, theta_free

    arc = mpatches.Arc(
        (p_hinge[0], p_hinge[1]), door_len * 2, door_len * 2,
        angle=0, theta1=t1, theta2=t2,
        color=DOOR_COLOR, linewidth=1.2, linestyle="--", zorder=4,
    )
    ax.add_patch(arc)

    # Second radius: hinge → open position (completes the sector)
    open_rad = math.radians(t2 if cross > 0 else t1)
    open_x = p_hinge[0] + door_len * math.cos(open_rad)
    open_z = p_hinge[1] + door_len * math.sin(open_rad)
    ax.plot([p_hinge[0], open_x], [p_hinge[1], open_z],
            color=DOOR_COLOR, linewidth=2.0, zorder=4)


def _draw_sliding_door(ax, p0, p1, int_nx, int_nz):
    """Draw sliding door symbol: two overlapping panel lines with slight depth offset."""
    dx = p1[0] - p0[0]
    dz = p1[1] - p0[1]
    length = math.hypot(dx, dz)
    if length < 1e-6:
        return

    tx, tz = dx / length, dz / length  # tangent along door opening
    # Two panel lines: each covers ~60% of opening, offset toward each end
    panel = length * 0.55
    depth = 0.05  # perpendicular offset to show panel thickness

    # Panel A: starts at p0, shifts inward along tangent slightly
    a0 = (p0[0], p0[1])
    a1 = (p0[0] + tx * panel, p0[1] + tz * panel)
    ao = (int_nx * depth, int_nz * depth)  # interior offset

    # Panel B: starts at p1, shifts inward along tangent
    b0 = (p1[0], p1[1])
    b1 = (p1[0] - tx * panel, p1[1] - tz * panel)

    for q0, q1, off in [(a0, a1, ao), (b0, b1, (-ao[0], -ao[1]))]:
        ax.plot([q0[0], q1[0]], [q0[1], q1[1]],
                color=DOOR_COLOR, linewidth=2.0, zorder=4)
        # small depth line at one end to suggest panel
        ax.plot([q1[0], q1[0] + off[0]], [q1[1], q1[1] + off[1]],
                color=DOOR_COLOR, linewidth=1.2, zorder=4)



def _draw_window(ax, p0, p1, edge_int_nx, edge_int_nz):
    """Draw 3-line window symbol: two frame lines + center glass line."""
    dx = p1[0] - p0[0]
    dz = p1[1] - p0[1]
    length = math.hypot(dx, dz)
    if length < 1e-9:
        return

    # Use the edge interior normal to orient lines symmetrically across wall
    nx, nz = edge_int_nx, edge_int_nz

    for t, lw in ((-1, 1.2), (0, 2.5), (1, 1.2)):
        ox = t * _WIN_HALF * nx
        oz = t * _WIN_HALF * nz
        ax.plot([p0[0] + ox, p1[0] + ox], [p0[1] + oz, p1[1] + oz],
                color=WINDOW_COLOR, linewidth=lw, zorder=4)


# ── main renderer ─────────────────────────────────────────────────────────────

def render_region_2d(output: SceneUnderstandOutput, path: str) -> None:
    """Render all regions (boundary + doors + windows) to a PNG file."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect("equal")
    ax.set_title(f"Region Plan — {output.scene_type}", fontsize=12)
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
                    if door_type == "sliding":
                        # Sliding door: draw on whichever room first encounters it (or exterior)
                        if opens_into is None or opens_into == region.region_id:
                            _draw_sliding_door(ax, oa, ob, int_nx, int_nz)
                    elif opens_into is None:
                        # Exterior swing door — panel line only, no arc
                        ax.plot([oa[0], ob[0]], [oa[1], ob[1]],
                                color=DOOR_COLOR, linewidth=2.0, zorder=4)
                    elif opens_into == region.region_id:
                        # This region owns the swing symbol — draw full sector
                        da = min(math.hypot(oa[0] - v[0], oa[1] - v[1]) for v in bnd)
                        db = min(math.hypot(ob[0] - v[0], ob[1] - v[1]) for v in bnd)
                        if da >= db:
                            _draw_door(ax, oa, ob, int_nx, int_nz)
                        else:
                            _draw_door(ax, ob, oa, int_nx, int_nz)
                    # else: shared swing door owned by the other room — wall gap only
                else:  # window
                    _draw_window(ax, oa, ob, int_nx, int_nz)

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
