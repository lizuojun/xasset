# xasset/debug/renderers/house/region_2d.py
"""2D region plan renderer: UnderstandOutput -> PNG via matplotlib.

适配新的 UnderstandOutput 契约（SceneRegion.boundary 为 Polygon，
轮廓语义收敛为 semantics.features：开口 / 固定边）。
"""
from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from xasset.pipeline.schemas import UnderstandOutput
from xasset.debug.renderers.house.draw_utils import (
    draw_door_jambs,
    draw_door_swing,
    draw_main_door,
    draw_sliding_door,
    draw_window_symbol,
)

REGION_COLORS = {
    "living_room": "#f5e6d3",
    "bedroom": "#d3e6f5",
    "kitchen": "#f5d3d3",
    "bathroom": "#d3f5f0",
}
FLOOR_COLOR = "#f0f0f0"
WALL_COLOR = "#333333"
STRUCT_COLOR = "#c0392b"


def _find_edge(bnd, seg_start, seg_end):
    """找到 seg_start-seg_end 对应的边界边索引与参数区间。"""
    n = len(bnd)
    for i in range(n):
        p0, p1 = bnd[i], bnd[(i + 1) % n]
        if (abs(p0[0] - seg_start[0]) < 1e-6 and abs(p0[1] - seg_start[1]) < 1e-6
                and abs(p1[0] - seg_end[0]) < 1e-6 and abs(p1[1] - seg_end[1]) < 1e-6):
            return i, 0.0, 1.0
    return None


def _lerp(p0, p1, t):
    return (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)


def render_region_2d(output: UnderstandOutput, path: str) -> None:
    """Render all regions (boundary + openings + fixed edges) to a PNG file."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect("equal")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")

    for region in output.regions:
        bnd = list(region.boundary.points)
        n = len(bnd)

        xs = [p[0] for p in bnd] + [bnd[0][0]]
        zs = [p[1] for p in bnd] + [bnd[0][1]]
        color = REGION_COLORS.get(region.region_type, FLOOR_COLOR)
        ax.fill(xs, zs, color=color, alpha=1.0, zorder=1)

        # 统计每条轮廓边上的开口
        edge_opens: dict = {}       # edge_idx -> [(t0, t1, feature)]
        struct_edges: set = set()   # 固定边所在的边索引

        for feat in region.semantics.features:
            if feat.seg_start is None or feat.seg_end is None:
                continue
            r = _find_edge(bnd, feat.seg_start, feat.seg_end)
            if not r:
                continue
            ei, t0, t1 = r
            if feat.kind == "opening":
                edge_opens.setdefault(ei, []).append((t0, t1, feat))
            elif feat.kind == "fixed_edge":
                struct_edges.add(ei)

        for i in range(n):
            p0, p1 = bnd[i], bnd[(i + 1) % n]
            is_struct = i in struct_edges
            wc = STRUCT_COLOR if is_struct else WALL_COLOR
            lw = 5.0 if is_struct else 2.0

            dx, dz = p1[0] - p0[0], p1[1] - p0[1]
            elen = math.hypot(dx, dz)
            int_nx = -dz / elen if elen > 1e-9 else 0.0
            int_nz = dx / elen if elen > 1e-9 else 0.0

            opens = sorted(edge_opens.get(i, []), key=lambda o: o[0])

            if not opens:
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                        color=wc, linewidth=lw, zorder=2)
                continue

            cur = 0.0
            for t0, t1, feat in opens:
                if t0 > cur + 1e-6:
                    pa, pb = _lerp(p0, p1, cur), _lerp(p0, p1, t0)
                    ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
                            color=wc, linewidth=lw, zorder=2)

                oa, ob = _lerp(p0, p1, t0), _lerp(p0, p1, t1)

                # 按 feature_type 决定画什么符号（开放字符串，未知则留空）
                ftype = feat.feature_type
                opens_into = feat.connects_to
                attrs = feat.attrs or {}

                if ftype == "door":
                    if opens_into is None:
                        draw_main_door(ax, oa, ob, int_nx, int_nz, bnd)
                    elif attrs.get("door_type") == "sliding":
                        if opens_into == region.region_id:
                            draw_door_jambs(ax, oa, ob, int_nx, int_nz)
                            draw_sliding_door(ax, oa, ob, int_nx, int_nz)
                    elif opens_into == region.region_id:
                        draw_door_jambs(ax, oa, ob, int_nx, int_nz)
                        draw_door_swing(ax, oa, ob, int_nx, int_nz, bnd)
                elif ftype == "window":
                    draw_window_symbol(ax, oa, ob, int_nx, int_nz)
                # 其它 feature_type（城市路口 / 岸线等）暂不画符号

                cur = t1

            if cur < 1.0 - 1e-6:
                pa = _lerp(p0, p1, cur)
                ax.plot([pa[0], p1[0]], [pa[1], p1[1]],
                        color=wc, linewidth=lw, zorder=2)

        cx = sum(p[0] for p in bnd) / n
        cz = sum(p[1] for p in bnd) / n
        ax.text(cx, cz, f"{region.region_type}\n{region.area:.1f}m2",
                ha="center", va="center", fontsize=7, color="#555555", zorder=3)

    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
