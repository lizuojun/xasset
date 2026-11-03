# tests/tools/test_quality_rules.py
"""软规则评估测试。

验证：
1. 配置能正确加载（data/house/rules.json）
2. 规则实现能对真实户型数据给出评估
3. required / preferred 分级生效
"""
import json
from pathlib import Path

import pytest

from xasset.pipeline.schemas import (
    BoundaryFeature,
    ContourSemantics,
    Polygon,
    SceneRegion,
)
from xasset.tools.quality import (
    QualityConfig,
    RuleLevel,
    build_default_registry,
)

RULES_PATH = Path(__file__).resolve().parents[2] / "data" / "house" / "rules.json"


@pytest.fixture(scope="module")
def config():
    return QualityConfig.load(RULES_PATH, build_default_registry())


def _region(region_id, region_type, pts, area=None, openings=None):
    pts = [tuple(p) for p in pts]
    if area is None:
        # 简化：用包围盒面积近似（测试够用）
        xs = [p[0] for p in pts]
        zs = [p[1] for p in pts]
        area = (max(xs) - min(xs)) * (max(zs) - min(zs))
    feats = []
    for i, (w, fid) in enumerate(openings or []):
        feats.append(
            BoundaryFeature(
                feature_id=fid,
                kind="opening",
                feature_type="door",
                pts=[pts[0], pts[1]],
                seg_start=pts[0],
                seg_end=pts[1],
                width=w,
            )
        )
    return SceneRegion(
        region_id=region_id,
        region_type=region_type,
        boundary=Polygon(points=pts),
        area=area,
        semantics=ContourSemantics(features=feats),
    )


def test_config_loads(config):
    assert config.scene == "house"
    assert config.typical_area("bedroom") == (8.0, 25.0)
    assert config.typical_area("bathroom") == (2.0, 8.0)


def test_rules_merge_scene_and_region(config):
    """区域规则 = 场景通用规则 + 区域专属规则。"""
    ids = {r.rule_id for r in config.rules_for("bedroom")}
    assert "area_within_typical" in ids         # 通用
    assert "bed_not_facing_door" in ids         # bedroom 专属
    assert "kitchen_work_triangle" not in ids   # 别的区域的不该有


def test_no_required_rules_in_quality_config(config):
    """软规则配置里不应有 required 级规则（那是硬约束的职责）。"""
    all_rules = []
    for rt in ("bedroom", "kitchen", "living_room", "bathroom"):
        all_rules.extend(config.rules_for(rt))
    assert all(r.level is RuleLevel.PREFERRED for r in all_rules)


def test_unimplemented_rule_skipped(config):
    """配置里声明但代码未实现的规则被跳过，不报错。"""
    r = _region("r1", "bedroom", [(0, 0), (4, 0), (4, 4), (0, 4)],
                openings=[(0.9, "d1")])
    report = config.evaluate([r])
    # bedroom_needs_bed 有实现吗？没有 → 跳过；不应抛异常
    assert isinstance(report.violations, list)


def test_area_out_of_range_flagged(config):
    """面积超典型区间的区域应被标出。"""
    # bedroom 典型 8~25m²，这里给 4m²
    r = _region("small", "bedroom", [(0, 0), (2, 0), (2, 2), (0, 2)],
                area=4.0, openings=[(0.9, "d1")])
    report = config.evaluate([r])
    ids = {v.rule_id for v in report.violations}
    assert "area_within_typical" in ids


def test_aspect_ratio_flagged(config):
    """过长的区域应被标出。"""
    # 12m x 1m，长宽比 12
    r = _region("long", "hallway", [(0, 0), (12, 0), (12, 1), (0, 1)],
                area=12.0, openings=[(0.9, "d1")])
    report = config.evaluate([r])
    ids = {v.rule_id for v in report.violations}
    assert "aspect_ratio_comfortable" in ids


def test_narrow_opening_flagged_preferred(config):
    """门宽低于舒适值应产生 preferred 级违规（但不算非法）。"""
    r = _region("r1", "living_room", [(0, 0), (6, 0), (6, 5), (0, 5)],
                area=30.0, openings=[(0.4, "narrow_door")])
    report = config.evaluate([r])
    pref_ids = {v.rule_id for v in report.preferred_violations}
    assert "passage_width_comfortable" in pref_ids
    # 软规则里没有 required，所以 ok 仍为 True
    assert report.ok


def test_ok_when_no_required_violations(config):
    """只有 preferred 违规时 ok 仍为 True。"""
    # 面积略小（preferred 违规），但门宽合格、连通、比例如常
    r = _region("r1", "living_room", [(0, 0), (6, 0), (6, 5), (0, 5)],
                area=30.0, openings=[(1.0, "d1")])
    report = config.evaluate([r])
    # 该区域没有 required 类违规
    assert report.ok


def test_score_decreases_with_violations(config):
    good = _region("g", "bathroom", [(0, 0), (2, 0), (2, 2), (0, 2)],
                   area=4.0, openings=[(0.8, "d1")])
    bad = _region("b", "bathroom", [(0, 0), (1, 0), (1, 1), (0, 1)],
                  area=1.0, openings=[(0.3, "d1")])
    good_score = config.evaluate([good]).score
    bad_score = config.evaluate([bad]).score
    assert bad_score < good_score


def test_rule_levels_parsed(config):
    """level 字段被正确解析（软规则一律 preferred）。"""
    scene_rules = {r.rule_id: r for r in config.rules_for("bedroom")}
    assert scene_rules["area_within_typical"].level is RuleLevel.PREFERRED
    assert scene_rules["aspect_ratio_comfortable"].level is RuleLevel.PREFERRED


def test_rules_json_is_valid():
    """配置文件本身是合法 JSON 且含必要字段。"""
    with open(RULES_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["scene"] == "house"
    assert "scene_rules" in data
    assert "region_rules" in data
    for r in data["scene_rules"]:
        assert "id" in r and "level" in r
