# tests/tools/test_constraint_gate.py
"""测试硬约束校验闸门（tools/constraint）。

硬约束 = 绝对不合法，不可让步。规则返回 RuleViolation 或 None。
"""
from xasset.pipeline.schemas import (
    ContourSemantics,
    Polygon,
    SceneRegion,
    UnderstandOutput,
)
from xasset.tools.constraint import (
    ConstraintSet,
    RuleViolation,
    ValidationResult,
    understand_hard_constraints,
)


def test_empty_constraint_set_passes():
    s = ConstraintSet("test", rules=[])
    assert s.validate(None, None).ok


def test_rule_pass_and_fail():
    def ok_rule(ctx, out):
        return None

    def bad_rule(ctx, out):
        return RuleViolation(rule="r1", message="value too small")

    s = ConstraintSet("test", rules=[ok_rule, bad_rule])
    result = s.validate(None, {"x": 1})
    assert not result.ok
    assert "value too small" in result.error_message


def test_fail_fast_stops_at_first_failure():
    calls = []

    def a(ctx, out):
        calls.append("a")
        return RuleViolation(rule="a", message="a failed")

    def b(ctx, out):
        calls.append("b")
        return RuleViolation(rule="b", message="b failed")

    s_fast = ConstraintSet("test", rules=[a, b], fail_fast=True)
    r = s_fast.validate(None, None)
    assert calls == ["a"]
    assert len(r.violations) == 1

    calls.clear()
    s_collect = ConstraintSet("test", rules=[a, b], fail_fast=False)
    r = s_collect.validate(None, None)
    assert calls == ["a", "b"]
    assert len(r.violations) == 2


def test_validation_result_helpers():
    assert ValidationResult.pass_().ok
    f = ValidationResult.fail(
        RuleViolation(rule="x", message="x"),
        RuleViolation(rule="y", message="y"),
    )
    assert not f.ok
    assert len(f.reasons) == 2


def test_fixable_separates_fixable_violations():
    """fixable 只挑出带修复建议的违规（求解器能直接处理的部分）。"""
    def with_fix(ctx, out):
        return RuleViolation(rule="a", message="a", fix={"op": "snap"})

    def without_fix(ctx, out):
        return RuleViolation(rule="b", message="b", fix=None)

    s = ConstraintSet("test", rules=[with_fix, without_fix])
    r = s.validate(None, None)
    assert len(r.violations) == 2
    assert len(r.fixable) == 1
    assert r.fixable[0].rule == "a"


# ── 真实硬约束规则测试 ──────────────────────────────────────────────────

def _region(region_id, pts, openings=None, area=None):
    pts = [tuple(p) for p in pts]
    if area is None:
        xs = [p[0] for p in pts]
        zs = [p[1] for p in pts]
        area = (max(xs) - min(xs)) * (max(zs) - min(zs))
    from xasset.pipeline.schemas import BoundaryFeature

    feats = [
        BoundaryFeature(
            feature_id=fid,
            kind="opening",
            feature_type="door",
            pts=[pts[0], pts[1]],
            seg_start=pts[0],
            seg_end=pts[1],
            width=w,
        )
        for w, fid in (openings or [])
    ]
    return SceneRegion(
        region_id=region_id,
        region_type="bedroom",
        boundary=Polygon(points=pts),
        area=area,
        semantics=ContourSemantics(features=feats),
    )


def test_valid_region_passes_hard_constraints():
    region = _region("r1", [(0, 0), (4, 0), (4, 4), (0, 4)], openings=[(0.9, "d1")])
    out = UnderstandOutput(scene_type="house", regions=[region])
    result = understand_hard_constraints().validate(None, out)
    assert result.ok, result.error_message


def test_self_intersecting_polygon_rejected():
    """自相交多边形是硬性非法。"""
    # 蝴蝶结形状：对角线交叉
    region = _region("bow", [(0, 0), (4, 4), (4, 0), (0, 4)])
    out = UnderstandOutput(scene_type="house", regions=[region])
    result = understand_hard_constraints().validate(None, out)
    assert not result.ok
    assert any(v.rule == "polygon_simple" for v in result.violations)


def test_opening_off_boundary_rejected_with_fix():
    """开口悬空应被拒，并给出可执行的修复建议。"""
    from xasset.pipeline.schemas import BoundaryFeature

    region = _region("r1", [(0, 0), (10, 0), (10, 10), (0, 10)])
    # 手工构造一个远离边界的开口（中心在房间中央）
    region.semantics.features.append(
        BoundaryFeature(
            feature_id="floating_door",
            kind="opening",
            feature_type="door",
            pts=[(5, 5), (5.5, 5.5)],
            width=0.9,
        )
    )
    out = UnderstandOutput(scene_type="house", regions=[region])
    result = understand_hard_constraints().validate(None, out)

    assert not result.ok
    v = next(v for v in result.violations if v.rule == "opening_on_boundary")
    assert v.fix is not None
    assert v.fix["op"] == "snap_feature_to_edge"
    assert v.target_id == "floating_door"


def test_zero_area_rejected():
    region = _region("zero", [(0, 0), (1, 0), (1, 1)], area=0.0)
    out = UnderstandOutput(scene_type="house", regions=[region])
    result = understand_hard_constraints().validate(None, out)
    assert not result.ok
    assert any(v.rule == "region_area_positive" for v in result.violations)


# ── 国标合规约束测试 ────────────────────────────────────────────────────

def test_standards_constants_have_expected_values():
    """规范常数与文档记录的数值一致。"""
    from xasset.tools.constraint import standards as STD

    assert STD.DOOR_WIDTH_BEDROOM_MIN_M == 0.90   # H-02
    assert STD.DOOR_WIDTH_KITCHEN_MIN_M == 0.80    # H-03
    assert STD.DOOR_WIDTH_BATHROOM_MIN_M == 0.70   # H-04
    assert STD.AREA_KITCHEN_MIN_M2 == 4.0          # H-12
    assert STD.AREA_BATHROOM_MIN_M2 == 2.5         # H-13


def test_bedroom_door_too_narrow_rejected():
    """卧室门宽 0.8m 低于国标 0.9m，应被拒。"""
    from xasset.pipeline.schemas import BoundaryFeature

    region = _region("bed", [(0, 0), (4, 0), (4, 4), (0, 4)], area=16.0)
    region.region_type = "bedroom"
    region.semantics.features.append(
        BoundaryFeature(
            feature_id="door_1",
            kind="opening",
            feature_type="door",
            pts=[(0, 0), (0.8, 0)],
            width=0.8,          # 低于卧室门规范 0.9
        )
    )
    out = UnderstandOutput(scene_type="house", regions=[region])
    result = understand_hard_constraints().validate(None, out)

    assert not result.ok
    v = next(v for v in result.violations if v.rule == "door_width_per_region_type")
    assert "0.90" in v.message


def test_bathroom_door_at_standard_passes():
    """卫生间门宽 0.7m 正好达国标，应通过该条检查。"""
    from xasset.pipeline.schemas import BoundaryFeature

    region = _region("bath", [(0, 0), (2, 0), (2, 2), (0, 2)], area=4.0)
    region.region_type = "bathroom"
    region.semantics.features.append(
        BoundaryFeature(
            feature_id="door_1",
            kind="opening",
            feature_type="door",
            pts=[(0, 0), (0.7, 0)],
            width=0.7,
        )
    )
    out = UnderstandOutput(scene_type="house", regions=[region])
    result = understand_hard_constraints().validate(None, out)

    rules_hit = {v.rule for v in result.violations}
    assert "door_width_per_region_type" not in rules_hit


def test_kitchen_area_below_standard_rejected():
    """厨房面积 3m² 低于国标 4m²，应被拒。"""
    region = _region("kit", [(0, 0), (2, 0), (2, 1.5), (0, 1.5)], area=3.0,
                     openings=[(0.9, "d1")])
    region.region_type = "kitchen"
    out = UnderstandOutput(scene_type="house", regions=[region])
    result = understand_hard_constraints().validate(None, out)

    assert not result.ok
    v = next(v for v in result.violations if v.rule == "region_area_meets_standard")
    assert "4.0" in v.message


def test_window_not_checked_for_door_width():
    """窗不是门，不适用门宽规范。"""
    from xasset.pipeline.schemas import BoundaryFeature

    region = _region("r", [(0, 0), (4, 0), (4, 4), (0, 4)], area=16.0)
    region.region_type = "bedroom"
    region.semantics.features.append(
        BoundaryFeature(
            feature_id="win_1",
            kind="opening",
            feature_type="window",
            pts=[(0, 0), (0.5, 0)],
            width=0.5,          # 窗窄不影响门宽规则
        )
    )
    out = UnderstandOutput(scene_type="house", regions=[region])
    result = understand_hard_constraints().validate(None, out)

    rules_hit = {v.rule for v in result.violations}
    assert "door_width_per_region_type" not in rules_hit
