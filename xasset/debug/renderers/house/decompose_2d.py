# xasset/debug/renderers/house/decompose_2d.py
"""
RoomDecompose 2D renderer: WallSegment + CurtainZone -> PNG via matplotlib.

Visual legend
--------------
  Wall segment line   : gray (#555555)
  w=X.X d=X.X q=X.XX  : width / depth / quality label
  Depth bars          : filled rectangles, log1p(depth)*scale height inward
  Curtain zone        : dashed outline rectangle along window edges
  Door symbol         : jambs + swing arc (shared doors drawn once)
  Window symbol       : 3-line symbol
"""
from __future__ import annotations

import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandOutput
from xasset.pipeline.stages.layout.house.room_decompose import WallSegment, CurtainZone

from xasset.debug.renderers.house.draw_utils import (
    draw_door_jambs, draw_door_swing, draw_window_symbol, draw_curtain_zone, draw_main_door,
    CURTAIN_COLOR, CURTAIN_ALPHA, WALL_COLOR, DOOR_COLOR, WINDOW_COLOR, FLOOR_COLOR,
)

_FLOOR_FILL       = FLOOR_COLOR
_GRID_ALPHA       = 0.25
_DEPTH_BAR_COLOR  = "#4B9DCA"
_LOG_DEPTH_SCALE  = 0.80


def _bar_h(depth: float) -> float:
    return math.log1p(depth) * _LOG_DEPTH_SCALE


def _lerp(p0, p1, t):
    return (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))


def _prev_same_edge(segs: list, i: int):
    if i <= 0:
        return None
    prev = segs[i - 1]
    cur = segs[i]
    if prev.seg_type in ("wall", "window") and prev.edge_idx == cur.edge_idx:
        return prev
    return None


def _render_rooms(ax, segs_by_region, curtains_by_region, understand_out, orientation):
    """Draw room floors, walls, doors; depth analysis filtered by orientation."""
    id_to_region = {r.region_id: r for r in understand_out.regions}

    for region_id, segs in segs_by_region.items():
        region = id_to_region.get(region_id)
        if region is None:
            continue

        bnd = region.boundary
        n = len(bnd)

        xs = [p[0] for p in bnd] + [bnd[0][0]]
        zs = [p[1] for p in bnd] + [bnd[0][1]]
        ax.fill(xs, zs, color=_FLOOR_FILL, alpha=1.0, zorder=1)

        cx = sum(p[0] for p in bnd) / n
        cz = sum(p[1] for p in bnd) / n
        ax.text(cx, cz, region.region_type, ha="center", va="center",
                fontsize=6, color="#AAAAAA", zorder=2)

        for i_seg, seg in enumerate(segs):
            p0, p1 = seg.p0, seg.p1
            nx, nz = seg.inward_normal

            is_h = abs(nz) > abs(nx)
            show_depth = orientation is None or (orientation == "h" and is_h) or (orientation == "v" and not is_h)

            if seg.seg_type in ("wall", "window"):
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                        color=WALL_COLOR, linewidth=2.0, zorder=3)

                if show_depth:
                    mid_x = (p0[0] + p1[0]) / 2.0
                    mid_z = (p0[1] + p1[1]) / 2.0
                    for ds in seg.depth_profile:
                        base_s = _lerp(p0, p1, ds.t0)
                        base_e = _lerp(p0, p1, ds.t1)
                        h = _bar_h(ds.depth)
                        top_s = (base_s[0] + nx * h, base_s[1] + nz * h)
                        top_e = (base_e[0] + nx * h, base_e[1] + nz * h)
                        poly_x = [base_s[0], base_e[0], top_e[0], top_s[0]]
                        poly_z = [base_s[1], base_e[1], top_e[1], top_s[1]]
                        ax.fill(poly_x, poly_z, color=_DEPTH_BAR_COLOR, alpha=0.35, zorder=4)
                        ax.plot(poly_x + [poly_x[0]], poly_z + [poly_z[0]],
                                color=_DEPTH_BAR_COLOR, linewidth=0.5, alpha=0.55, zorder=4)

                    # Connect to previous same-edge segment
                    prev_seg = _prev_same_edge(segs, i_seg)
                    if prev_seg is not None and prev_seg.depth_profile:
                        p_is_h = abs(prev_seg.inward_normal[1]) > abs(prev_seg.inward_normal[0])
                        p_match = (orientation == "h" and p_is_h) or (orientation == "v" and not p_is_h)
                        if p_match:
                            ds_prev = prev_seg.depth_profile[-1]
                            h_prev = _bar_h(ds_prev.depth)
                            base_prev = _lerp(prev_seg.p0, prev_seg.p1, ds_prev.t1)
                            top_prev = (base_prev[0] + prev_seg.inward_normal[0]*h_prev,
                                        base_prev[1] + prev_seg.inward_normal[1]*h_prev)
                            ds_cur = seg.depth_profile[0]
                            h_cur = _bar_h(ds_cur.depth)
                            base_cur = _lerp(p0, p1, ds_cur.t0)
                            top_cur = (base_cur[0] + nx*h_cur, base_cur[1] + nz*h_cur)
                            conn_x = [base_cur[0], top_cur[0], top_prev[0], base_prev[0]]
                            conn_z = [base_cur[1], top_cur[1], top_prev[1], base_prev[1]]
                            ax.fill(conn_x, conn_z, color=_DEPTH_BAR_COLOR, alpha=0.35, zorder=4)
                            ax.plot(conn_x + [conn_x[0]], conn_z + [conn_z[0]],
                                    color=_DEPTH_BAR_COLOR, linewidth=0.5, alpha=0.55, zorder=4)

                    if seg.depth_profile:
                        max_h = max(_bar_h(ds.depth) for ds in seg.depth_profile)
                    else:
                        max_h = 0.0
                    depth_val = seg.depth_profile[0].depth if seg.depth_profile else 0.0
                    lbl_x = mid_x + nx * (max_h + 0.10)
                    lbl_z = mid_z + nz * (max_h + 0.10)
                    ax.text(lbl_x, lbl_z,
                            f"w={seg.length:.1f}  d={depth_val:.1f}  q={seg.wall_quality:.2f}",
                            fontsize=3.8, ha="center", va="center",
                            color="#333333", zorder=6)

                if seg.seg_type == "window":
                    draw_window_symbol(ax, p0, p1, nx, nz)

            elif seg.seg_type == "door":
                opens_into = seg.opens_into
                if opens_into is None:
                    draw_main_door(ax, p0, p1, nx, nz, bnd)
                elif opens_into == region_id:
                    draw_door_jambs(ax, p0, p1, nx, nz)
                    draw_door_swing(ax, p0, p1, nx, nz, bnd)

        curtains = curtains_by_region.get(region_id, [])
        for cz in curtains:
            draw_curtain_zone(ax, cz)


def render_decompose_2d(
    segs_by_region: dict,
    curtains_by_region: dict,
    understand_out: SceneUnderstandOutput,
    path: str,
    orientation: str | None = None,
) -> None:
    if orientation is None:
        fig, (ax_h, ax_v) = plt.subplots(1, 2, figsize=(24, 10))
    else:
        fig, ax = plt.subplots(figsize=(14, 11))
        ax.set_aspect("equal")
        _render_rooms(ax, segs_by_region, curtains_by_region, understand_out, orientation)
        orient_title = {"h": "Horizontal", "v": "Vertical"}.get(orientation, "")
        ax.set_title(f"Room Decompose - {orient_title} Walls")
        _finalize(fig, ax, path)
        return

    ax_h.set_aspect("equal")
    ax_v.set_aspect("equal")
    ax_h.set_title("Horizontal Walls")
    ax_v.set_title("Vertical Walls")
    ax_h.set_xlabel("X (m)")
    ax_v.set_xlabel("X (m)")
    ax_h.set_ylabel("Z (m)")

    _render_rooms(ax_h, segs_by_region, curtains_by_region, understand_out, "h")
    _render_rooms(ax_v, segs_by_region, curtains_by_region, understand_out, "v")

    # Shared legend
    legend_elements = [
        mpatches.Patch(facecolor=WALL_COLOR, label="Wall"),
        mpatches.Patch(facecolor=CURTAIN_COLOR, alpha=CURTAIN_ALPHA, label="Curtain zone"),
        mpatches.Patch(facecolor=_DEPTH_BAR_COLOR, alpha=0.5,
                       label=f"Depth (log1p x{_LOG_DEPTH_SCALE})"),
        mpatches.Patch(facecolor=DOOR_COLOR, label="Door"),
        mpatches.Patch(facecolor=WINDOW_COLOR, label="Window"),
    ]
    ax_v.legend(handles=legend_elements, loc="upper right", fontsize=7, framealpha=0.85)

    for a in (ax_h, ax_v):
        a.grid(True, linestyle="--", alpha=_GRID_ALPHA)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)


def _finalize(fig, ax, path):
    legend_elements = [
        mpatches.Patch(facecolor=WALL_COLOR, label="Wall"),
        mpatches.Patch(facecolor=CURTAIN_COLOR, alpha=CURTAIN_ALPHA, label="Curtain zone"),
        mpatches.Patch(facecolor=_DEPTH_BAR_COLOR, alpha=0.5,
                       label=f"Depth (log1p x{_LOG_DEPTH_SCALE})"),
        mpatches.Patch(facecolor=DOOR_COLOR, label="Door"),
        mpatches.Patch(facecolor=WINDOW_COLOR, label="Window"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=7, framealpha=0.85)
    ax.grid(True, linestyle="--", alpha=_GRID_ALPHA)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)
