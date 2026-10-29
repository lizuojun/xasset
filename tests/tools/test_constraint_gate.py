# tests/tools/test_constraint_gate.py
"""测试约束校验闸门（tools/constraint）的基础能力。"""
from xasset.tools.constraint import (
    ValidationResult,
    ConstraintSet,
)


def test_empty_constraint_set_passes():
    s = ConstraintSet("test", rules=[])
    assert s.validate(None, None).ok


def test_rule_pass_and_fail():
    def ok_rule(ctx, out):
        return True, ""

    def bad_rule(ctx, out):
        return False, "value too small"

    s = ConstraintSet("test", rules=[ok_rule, bad_rule])
    result = s.validate(None, {"x": 1})
    assert not result.ok
    assert "value too small" in result.reasons


def test_fail_fast_stops_at_first_failure():
    calls = []

    def a(ctx, out):
        calls.append("a")
        return False, "a failed"

    def b(ctx, out):
        calls.append("b")
        return False, "b failed"

    s_fast = ConstraintSet("test", rules=[a, b], fail_fast=True)
    r = s_fast.validate(None, None)
    assert calls == ["a"]
    assert r.reasons == ["a failed"]

    # fail_fast=False 收集全部原因
    calls.clear()
    s_collect = ConstraintSet("test", rules=[a, b], fail_fast=False)
    r = s_collect.validate(None, None)
    assert calls == ["a", "b"]
    assert r.reasons == ["a failed", "b failed"]


def test_validation_result_helpers():
    assert ValidationResult.pass_().ok
    f = ValidationResult.fail("x", "y")
    assert not f.ok
    assert f.reasons == ["x", "y"]
    assert f.error_message == "x; y"
