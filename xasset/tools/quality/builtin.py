# xasset/tools/quality/builtin.py
"""软规则的几何实现 —— B 类"不够好"的确定性评估。

**边界**：这里只实现"偏好类"规则（违反了不非法，只是不够好）。
绝对不合法的检查在 xasset/tools/constraint/builtin.py，不要放这里。

判断标准：如果违反了结果就是"用不了"，那是硬约束；
          如果只是"用得不够舒服"，才是软规则。
"""
from __future__ import annotations

from xasset.tools.quality.rules import RuleRegistry


# ── 几何辅助 ────────────────────────────────────────────────────────────

def _bbox(points: list) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    zs = [p[1] for p in points]
    return min(xs), min(zs), max(xs), max(zs)


def _aspect_ratio(region) -> float:
    pts = list(region.boundary.points)
    x0, z0, x1, z1 = _bbox(pts)
    w, h = x1 - x0, z1 - z0
    if w <= 1e-9 or h <= 1e-9:
        return float("inf")
    return max(w, h) / min(w, h)


# ── 场景通用软规则 ──────────────────────────────────────────────────────

def _area_within_typical(region, ctx) -> "str | None":
    typical = ctx.get("typical_area")
    if not typical:
        return None
    lo, hi = typical
    area = region.area
    if area < lo:
        return f"面积 {area:.1f}m² 小于典型下限 {lo:.1f}m²"
    if area > hi:
        return f"面积 {area:.1f}m² 大于典型上限 {hi:.1f}m²"
    return None


def _aspect_ratio_comfortable(region, ctx) -> "str | None":
    params = ctx["params"]
    ratio = _aspect_ratio(region)
    hard_max = params.get("hard_max_ratio", 4.0)
    max_ratio = params.get("max_ratio", 2.5)
    if ratio > hard_max:
        return f"长宽比 {ratio:.2f} 明显偏大（建议 ≤ {max_ratio}）"
    if ratio > max_ratio:
        return f"长宽比 {ratio:.2f} 偏狭长（建议 ≤ {max_ratio}）"
    return None


def _passage_width_comfortable(region, ctx) -> "str | None":
    comfort = ctx["params"].get("comfort_width_m", 0.8)
    for feat in region.semantics.openings:
        if feat.width is not None and feat.width < comfort:
            return (
                f"开口 {feat.feature_id} 宽度 {feat.width:.2f}m "
                f"低于舒适值 {comfort}m（仍可使用）"
            )
    return None


# ── 区域专属软规则（当前数据不足以判定的先返回 None）────────────────────
# 说明：以下规则依赖 layout 层产物（已摆放内容），在 layout 未实现前
# 无法真正评估。保留函数占位，让配置可以先行声明。

def _needs_layout_products(region, ctx) -> "str | None":
    """占位：依赖 layout 产物的规则，暂时不评估。"""
    return None


def build_default_registry() -> RuleRegistry:
    """注册所有已实现的软规则。

    多数按区域细分的规则（床不对门、厨房三角动线等）需要 layout 层
    的摆放结果才能判断，当前注册为占位实现，等 layout 产出后补全。
    """
    reg = RuleRegistry()

    # 场景通用（已实现，基于 understand 产物即可判断）
    reg.register("area_within_typical", _area_within_typical)
    reg.register("aspect_ratio_comfortable", _aspect_ratio_comfortable)
    reg.register("passage_width_comfortable", _passage_width_comfortable)

    # 区域专属（依赖 layout 产物，暂占位）
    for rid in (
        "living_media_faces_seating",
        "living_seating_has_wall_backing",
        "ldr_dining_not_in_passage",
        "bed_not_facing_door",
        "bed_has_side_clearance",
        "bed_not_under_window",
        "kitchen_work_triangle",
        "bathroom_door_clearance",
        "dining_chair_clearance",
        "library_desk_natural_light",
        "kids_play_area",
        "hallway_not_cluttered",
    ):
        reg.register(rid, _needs_layout_products)

    return reg
