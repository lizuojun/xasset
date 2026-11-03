# xasset/tools/constraint/builtin.py
"""硬约束的几何实现 —— A 类"非法"的确定性检查。

每条规则返回 RuleViolation（含 fix 建议）或 None。
这些检查的对象是"绝对不合法"：几何自相交、开口悬空、越界等。
偏好的检查（面积典型性、长宽比）在 tools/quality 里，不要放这里。
"""
from __future__ import annotations

import math
from typing import Any

from xasset.tools.constraint import standards as STD
from xasset.tools.constraint.gate import (
    ConstraintSet,
    RuleViolation,
)


# ── 几何辅助 ────────────────────────────────────────────────────────────

def _segments_intersect(p1, p2, p3, p4) -> bool:
    """两条线段是否真正相交（不含共享端点）。"""
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False


def _dist_point_to_segment(p, a, b) -> float:
    px, pz = p
    ax, az = a
    bx, bz = b
    dx, dz = bx - ax, bz - az
    seg2 = dx * dx + dz * dz
    if seg2 < 1e-12:
        return math.hypot(px - ax, pz - az)
    t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / seg2))
    return math.hypot(px - (ax + t * dx), pz - (az + t * dz))


def _nearest_edge(center, pts) -> tuple[int, float, tuple]:
    """返回 (边索引, 距离, 最近的边中点)。"""
    n = len(pts)
    best_i, best_d = 0, float("inf")
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        d = _dist_point_to_segment(center, a, b)
        if d < best_d:
            best_d, best_i = d, i
    a, b = pts[best_i], pts[(best_i + 1) % n]
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return best_i, best_d, mid


def _context_regions(ctx) -> list:
    """从 ctx 里取出区域列表（兼容 Attribute / dict 两种 ctx）。"""
    out = getattr(ctx, "output", None) or getattr(ctx, "regions", None)
    if out is None and isinstance(ctx, dict):
        out = ctx.get("regions")
    if out is not None:
        return list(getattr(out, "regions", out) or [])
    return list(getattr(ctx, "all_regions", []) or [])


# ── 硬约束规则 ──────────────────────────────────────────────────────────

def polygon_simple(ctx, output):
    """区域轮廓必须是简单多边形（不能自相交）。

    自交是最严重的非法：它会让面积、内外判断全部失效。
    fix = None：自交没有通用的确定性修法，必须回到理解侧重出轮廓。
    """
    for region in getattr(output, "regions", []):
        pts = list(region.boundary.points)
        n = len(pts)
        for i in range(n):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                if _segments_intersect(pts[i], pts[(i + 1) % n],
                                       pts[j], pts[(j + 1) % n]):
                    return RuleViolation(
                        rule="polygon_simple",
                        target_id=region.region_id,
                        message=(
                            f"区域轮廓第 {i} 条边与第 {j} 条边自相交，"
                            f"该多边形不是简单多边形"
                        ),
                        fix=None,   # 无确定性修法，需重出轮廓
                    )
    return None


def opening_on_boundary(ctx, output):
    """每个开口必须落在所属区域轮廓的某条边上。

    fix：把开口吸附到最近的边上（确定性可执行）。
    容差 0.1m 是工程容差（非规范数值），用于吸收浮点误差与绘图误差。
    """
    tol = 0.1
    for region in getattr(output, "regions", []):
        pts = list(region.boundary.points)
        for feat in region.semantics.openings:
            if not feat.pts:
                continue
            center = (
                sum(p[0] for p in feat.pts) / len(feat.pts),
                sum(p[1] for p in feat.pts) / len(feat.pts),
            )
            idx, dist, mid = _nearest_edge(center, pts)
            if dist > tol:
                return RuleViolation(
                    rule="opening_on_boundary",
                    target_id=feat.feature_id,
                    message=(
                        f"开口 {feat.feature_id} 距最近轮廓边 {dist:.2f}m，"
                        f"超出容差 {tol}m（悬空）"
                    ),
                    fix={
                        "op": "snap_feature_to_edge",
                        "feature_id": feat.feature_id,
                        "edge_index": idx,
                        "target_point": list(mid),
                    },
                )
    return None


def door_width_per_region_type(ctx, output):
    """门洞宽度必须达到该区域类型对应的规范下限。

    数值依据见 standards.py 的 H-01~H-04：
    - 户门 / 卧室门 ≥ 0.90m
    - 厨房门 ≥ 0.80m
    - 卫生间门 ≥ 0.70m

    **这是硬约束**：门太窄就是不合格，不是"不够舒服"。
    fix = None：改门宽不是几何微调，需要重新决策开口位置与尺寸。
    """
    for region in getattr(output, "regions", []):
        required = STD.DOOR_WIDTH_BY_REGION_TYPE.get(
            region.region_type, STD.DOOR_WIDTH_FALLBACK_MIN_M
        )
        for feat in region.semantics.openings:
            # 只检查门类开口（窗/路口等不适用门宽规范）
            if feat.feature_type not in ("door",):
                continue
            if feat.width is None:
                continue
            if feat.width < required:
                return RuleViolation(
                    rule="door_width_per_region_type",
                    target_id=feat.feature_id,
                    message=(
                        f"区域 {region.region_id}({region.region_type}) 的门 "
                        f"{feat.feature_id} 宽 {feat.width:.2f}m，"
                        f"低于规范下限 {required:.2f}m"
                    ),
                    fix=None,   # 需重新决策开口，非几何微调
                )
    return None


def opening_width_positive(ctx, output):
    """开口宽度必须为正（零宽/负宽是数据错误）。"""
    for region in getattr(output, "regions", []):
        for feat in region.semantics.openings:
            if feat.width is not None and feat.width <= 0:
                return RuleViolation(
                    rule="opening_width_positive",
                    target_id=feat.feature_id,
                    message=f"开口 {feat.feature_id} 宽度 {feat.width} 必须为正",
                    fix=None,
                )
    return None


def region_area_positive(ctx, output):
    """区域面积必须为正。"""
    for region in getattr(output, "regions", []):
        if region.area <= 0:
            return RuleViolation(
                rule="region_area_positive",
                target_id=region.region_id,
                message=f"区域 {region.region_id} 面积 {region.area} 必须为正",
                fix=None,
            )
    return None


# 区域类型 → 规范规定的最小使用面积（依据 standards.py 的 H-10~H-14）
_MIN_AREA_BY_REGION_TYPE: dict[str, float] = {
    "living_room": STD.AREA_LIVING_MIN_M2,
    "living_dining_room": STD.AREA_LIVING_MIN_M2,
    "bedroom": STD.AREA_BEDROOM_SINGLE_MIN_M2,
    "kitchen": STD.AREA_KITCHEN_MIN_M2,
    "bathroom": STD.AREA_BATHROOM_MIN_M2,
}


def region_area_meets_standard(ctx, output):
    """区域面积必须达到规范最小使用面积。

    依据：GB 50096-2011 §5.6.2~5.6.5（见 standards.py H-10~H-14）。
    这是硬约束——低于规范下限的房间不合格。
    """
    for region in getattr(output, "regions", []):
        required = _MIN_AREA_BY_REGION_TYPE.get(region.region_type)
        if required is None:
            continue
        if region.area < required:
            return RuleViolation(
                rule="region_area_meets_standard",
                target_id=region.region_id,
                message=(
                    f"区域 {region.region_id}({region.region_type}) 面积 "
                    f"{region.area:.1f}m²，低于规范下限 {required:.1f}m²"
                ),
                fix=None,
            )
    return None


def region_inside_bounds(ctx, output):
    """所有区域必须落在地界范围内（若提供了 bounds）。"""
    bounds = getattr(ctx, "scene_bounds", None)
    if bounds is None and isinstance(ctx, dict):
        bounds = ctx.get("scene_bounds")
    if bounds is None:
        return None

    x0, z0, x1, z1 = bounds
    for region in getattr(output, "regions", []):
        for px, pz in region.boundary.points:
            if px < x0 - 0.01 or px > x1 + 0.01 or pz < z0 - 0.01 or pz > z1 + 0.01:
                return RuleViolation(
                    rule="region_inside_bounds",
                    target_id=region.region_id,
                    message=(
                        f"区域 {region.region_id} 的顶点 ({px:.2f},{pz:.2f}) "
                        f"超出场景边界 [{x0},{z0},{x1},{z1}]"
                    ),
                    fix=None,
                )
    return None


def element_inside_region(ctx, output):
    """摆放内容必须落在其所属区域内。

    fix：把元素沿最近方向推回区域内（确定性可执行）。
    """
    regions = {r.region_id: r for r in _context_regions(ctx)}
    if not regions:
        return None

    for el in getattr(output, "placed_elements", []):
        region = regions.get(el.region_id)
        if region is None:
            return RuleViolation(
                rule="element_inside_region",
                target_id=el.element_id,
                message=f"内容 {el.element_id} 指向不存在的区域 {el.region_id}",
                fix=None,
            )
        pts = list(region.boundary.points)
        idx, dist, mid = _nearest_edge((el.position[0], el.position[2]), pts)

        x0 = min(p[0] for p in pts); x1 = max(p[0] for p in pts)
        z0 = min(p[1] for p in pts); z1 = max(p[1] for p in pts)
        px, pz = el.position[0], el.position[2]
        if not (x0 <= px <= x1 and z0 <= pz <= z1):
            return RuleViolation(
                rule="element_inside_region",
                target_id=el.element_id,
                message=(
                    f"内容 {el.element_id} 位于 ({px:.2f},{pz:.2f})，"
                    f"超出区域 {el.region_id} 的范围"
                ),
                fix={
                    "op": "move_element_into_region",
                    "element_id": el.element_id,
                    "target_point": [mid[0], el.position[1], mid[1]],
                },
            )
    return None


# ── 组装 ────────────────────────────────────────────────────────────────

def understand_hard_constraints() -> ConstraintSet:
    """understand 阶段的硬约束集。

    覆盖：几何合法性（自交、悬空、越界）+ 规范合规（门宽、面积）。
    """
    return ConstraintSet(
        "understand",
        [
            # 几何合法性
            polygon_simple,
            opening_on_boundary,
            opening_width_positive,
            region_area_positive,
            region_inside_bounds,
            # 规范合规（依据国标，见 standards.py）
            door_width_per_region_type,
            region_area_meets_standard,
        ],
    )


def layout_hard_constraints() -> ConstraintSet:
    """layout 阶段的硬约束集。"""
    return ConstraintSet(
        "layout",
        [
            element_inside_region,
        ],
    )
