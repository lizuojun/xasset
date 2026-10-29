# xasset/debug/renderers/house/draw_utils.py
"""Shared door / window / curtain drawing symbols and color constants used by all house renderers."""
from __future__ import annotations

import math
import matplotlib.patches as mpatches

FLOOR_COLOR  = "#F0EDE8"
WALL_COLOR   = "#555555"
STRUCT_COLOR = "#1A1A1A"
DOOR_COLOR   = "#C0392B"
WINDOW_COLOR = "#2980B9"

REGION_COLORS: dict[str, str] = {
    "living_room":  FLOOR_COLOR,
    "bedroom":      FLOOR_COLOR,
    "dining_room":  FLOOR_COLOR,
    "kitchen":      FLOOR_COLOR,
    "bathroom":     FLOOR_COLOR,
    "balcony":      FLOOR_COLOR,
}

_JAMB_DEPTH   = 0.08
_WIN_HALF     = 0.06
CURTAIN_COLOR = "#C0392B"
CURTAIN_ALPHA = 0.18
CURTAIN_DEPTH = 0.15


def draw_door_jambs(ax, p0, p1, nx, nz):
    for pt in (p0, p1):
        ax.plot(
            [pt[0], pt[0] + nx * _JAMB_DEPTH],
            [pt[1], pt[1] + nz * _JAMB_DEPTH],
            color=DOOR_COLOR, linewidth=1.8, zorder=5,
        )


def draw_main_door(ax, p0, p1, nx, nz, bnd):
    """Prominent symbol for the main/entry door (exterior, opens_into=None):
    jambs + thick leaf + open swing arc, heavier-weight than interior doors
    so it reads clearly against the wall line."""
    draw_door_jambs(ax, p0, p1, nx, nz)

    da = min(math.hypot(p0[0] - v[0], p0[1] - v[1]) for v in bnd)
    db = min(math.hypot(p1[0] - v[0], p1[1] - v[1]) for v in bnd)
    p_hinge = p0 if da <= db else p1
    p_free  = p1 if da <= db else p0

    door_len = math.hypot(p_free[0] - p_hinge[0], p_free[1] - p_hinge[1])
    if door_len < 1e-6:
        return

    ax.plot([p_hinge[0], p_free[0]], [p_hinge[1], p_free[1]],
            color=DOOR_COLOR, linewidth=3.2, zorder=6)

    tx = (p_free[0] - p_hinge[0]) / door_len
    tz = (p_free[1] - p_hinge[1]) / door_len
    theta_free = math.degrees(math.atan2(tz, tx))

    cross = tx * nz - tz * nx
    if cross > 0:
        t1, t2 = theta_free, theta_free + 90
    else:
        t1, t2 = theta_free - 90, theta_free

    arc = mpatches.Arc(
        (p_hinge[0], p_hinge[1]), door_len * 2, door_len * 2,
        angle=0, theta1=t1, theta2=t2,
        color=DOOR_COLOR, linewidth=1.8, linestyle="--", zorder=6,
    )
    ax.add_patch(arc)

    open_rad = math.radians(t2 if cross > 0 else t1)
    open_x = p_hinge[0] + door_len * math.cos(open_rad)
    open_z = p_hinge[1] + door_len * math.sin(open_rad)
    ax.plot([p_hinge[0], open_x], [p_hinge[1], open_z],
            color=DOOR_COLOR, linewidth=3.2, zorder=6)


def draw_door_swing(ax, p0, p1, nx, nz, bnd):
    da = min(math.hypot(p0[0] - v[0], p0[1] - v[1]) for v in bnd)
    db = min(math.hypot(p1[0] - v[0], p1[1] - v[1]) for v in bnd)
    p_hinge = p0 if da <= db else p1
    p_free  = p1 if da <= db else p0

    door_len = math.hypot(p_free[0] - p_hinge[0], p_free[1] - p_hinge[1])
    if door_len < 1e-6:
        return

    ax.plot([p_hinge[0], p_free[0]], [p_hinge[1], p_free[1]],
            color=DOOR_COLOR, linewidth=2.0, zorder=5)

    tx = (p_free[0] - p_hinge[0]) / door_len
    tz = (p_free[1] - p_hinge[1]) / door_len
    theta_free = math.degrees(math.atan2(tz, tx))

    cross = tx * nz - tz * nx
    if cross > 0:
        t1, t2 = theta_free, theta_free + 90
    else:
        t1, t2 = theta_free - 90, theta_free

    arc = mpatches.Arc(
        (p_hinge[0], p_hinge[1]), door_len * 2, door_len * 2,
        angle=0, theta1=t1, theta2=t2,
        color=DOOR_COLOR, linewidth=1.2, linestyle="--", zorder=5,
    )
    ax.add_patch(arc)

    open_rad = math.radians(t2 if cross > 0 else t1)
    open_x = p_hinge[0] + door_len * math.cos(open_rad)
    open_z = p_hinge[1] + door_len * math.sin(open_rad)
    ax.plot([p_hinge[0], open_x], [p_hinge[1], open_z],
            color=DOOR_COLOR, linewidth=2.0, zorder=5)


def draw_window_symbol(ax, p0, p1, nx, nz):
    for t, lw in ((-1, 1.2), (0, 2.5), (1, 1.2)):
        ox = t * _WIN_HALF * nx
        oz = t * _WIN_HALF * nz
        ax.plot([p0[0] + ox, p1[0] + ox], [p0[1] + oz, p1[1] + oz],
                color=WINDOW_COLOR, linewidth=lw, zorder=5)


def draw_curtain_zone(ax, curtain):
    nx, nz = curtain.inward_normal
    d = CURTAIN_DEPTH
    poly_x = [curtain.p0[0], curtain.p1[0], curtain.p1[0] + nx*d, curtain.p0[0] + nx*d, curtain.p0[0]]
    poly_z = [curtain.p0[1], curtain.p1[1], curtain.p1[1] + nz*d, curtain.p0[1] + nz*d, curtain.p0[1]]
    ax.fill(poly_x, poly_z, color=CURTAIN_COLOR, alpha=CURTAIN_ALPHA, zorder=2)
    ax.plot(poly_x, poly_z, color=CURTAIN_COLOR, linewidth=0.6, linestyle="--", alpha=0.5, zorder=2)


def draw_sliding_door(ax, p0, p1, int_nx, int_nz):
    dx = p1[0] - p0[0]
    dz = p1[1] - p0[1]
    length = math.hypot(dx, dz)
    if length < 1e-6:
        return
    tx, tz = dx / length, dz / length
    panel = length * 0.55
    depth = 0.05
    a1 = (p0[0] + tx * panel, p0[1] + tz * panel)
    b1 = (p1[0] - tx * panel, p1[1] - tz * panel)
    ao = (int_nx * depth, int_nz * depth)
    ax.plot([p0[0], a1[0]], [p0[1], a1[1]], color=DOOR_COLOR, linewidth=2.0, zorder=4)
    ax.plot([a1[0], a1[0] + ao[0]], [a1[1], a1[1] + ao[1]], color=DOOR_COLOR, linewidth=1.2, zorder=4)
    ax.plot([p1[0], b1[0]], [p1[1], b1[1]], color=DOOR_COLOR, linewidth=2.0, zorder=4)
    ax.plot([b1[0], b1[0] - ao[0]], [b1[1], b1[1] - ao[1]], color=DOOR_COLOR, linewidth=1.2, zorder=4)
