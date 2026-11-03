# tests/datasource/test_manager.py
"""数据源管理测试。"""
import json

import pytest

from xasset.datasource import (
    STATUS_NOT_APPLIED,
    STATUS_UNREACHABLE,
    load_catalog,
)


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


# ── 加载 ────────────────────────────────────────────────────────────────

def test_catalog_loads(catalog):
    assert len(catalog.all_sources()) > 0


def test_known_sources_present(catalog):
    names = {s.name for s in catalog.all_sources()}
    for expected in ("cubicasa5k", "rplan", "structured3d", "osm"):
        assert expected in names


def test_unknown_source_raises_actionable_error(catalog):
    with pytest.raises(KeyError) as ei:
        catalog.get("nonexistent_dataset")
    assert "sources.json" in str(ei.value)


# ── 状态与可操作性 ──────────────────────────────────────────────────────

def test_rplan_needs_approval(catalog):
    rplan = catalog.get("rplan")
    assert rplan.requires_approval is True
    assert rplan.status == STATUS_NOT_APPLIED
    assert rplan.needs_user_action is True
    assert rplan.approval_url is not None


def test_cubicasa_fetchable_without_approval(catalog):
    c = catalog.get("cubicasa5k")
    assert c.requires_approval is False
    assert c.status != STATUS_UNREACHABLE


def test_osm_has_mirrors(catalog):
    osm = catalog.get("osm")
    assert osm.primary_url is not None
    assert len(osm.mirrors) > 0
    # urls() 应把主源放前面
    urls = osm.urls()
    assert urls[0] == osm.primary_url


# ── 分组查询 ────────────────────────────────────────────────────────────

def test_by_scene(catalog):
    house = catalog.by_scene("house")
    assert len(house) >= 2
    assert all(s.scene == "house" for s in house)


def test_need_user_action_lists_rplan(catalog):
    need = catalog.need_user_action()
    names = {s.name for s in need}
    assert "rplan" in names or "structured3d" in names


def test_fetchable_now_excludes_approval_sources(catalog):
    fetchable = catalog.fetchable_now()
    for s in fetchable:
        assert s.requires_approval is False
        assert s.status != STATUS_UNREACHABLE


# ── 失败经验被记录 ──────────────────────────────────────────────────────

def test_wikipedia_failure_is_recorded(catalog):
    """维基的失败教训必须被记下来——下次不用重试。"""
    imgs = catalog.test_images()
    wp = imgs.get("wikipedia_floorplans")
    assert wp is not None
    assert wp["status"] == STATUS_UNREACHABLE
    assert "400" in wp["failure_notes"]
    assert "root_cause" in wp          # 不只记现象，还要记原因


def test_successful_fetch_is_recorded(catalog):
    """成功经验也要记——包含可复现的步骤。"""
    imgs = catalog.test_images()
    ok = imgs.get("wikipedia_sample_floorplan")
    assert ok is not None
    assert ok["status"] == "fetched"
    assert ok["local_path"].endswith(".jpg")
    # 关键：记录"怎么复现"，而不只是"我下到了"
    assert "how_to_reproduce" in ok
    assert len(ok["how_to_reproduce"]) >= 3
    assert any("User-Agent" in s for s in ok["how_to_reproduce"])


def test_failure_records_root_cause_not_just_symptom(catalog):
    """失败记录必须包含根因，否则下次还是会踩同一个坑。"""
    imgs = catalog.test_images()
    wp = imgs.get("wikipedia_floorplans")
    assert "root_cause" in wp
    assert "hash" in wp["root_cause"].lower() or "哈希" in wp["root_cause"]


def test_status_report_is_readable(catalog):
    report = catalog.status_report()
    assert "数据源状态" in report
    assert "cubicasa5k" in report


def test_status_report_is_ascii_only(catalog):
    """状态报告必须能打印到 GBK 终端（Windows 默认）。"""
    report = catalog.status_report()
    report.encode("gbk")   # 编码失败会抛异常
