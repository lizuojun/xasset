# tests/scene/test_scene_config.py
"""场景配置测试 —— 验证"少做重复、可扩展"。

关键验证点：
- 场景知识只有一处（scene.json），代码里不硬编码
- 新增场景只需加配置文件，代码零改动
"""
import json
from pathlib import Path

import pytest

from xasset.scene import (
    RegionTypeSpec,
    SceneConfig,
    available_scenes,
    load_scene_config,
)


@pytest.fixture(scope="module")
def house():
    return load_scene_config("house")


# ── 加载 ────────────────────────────────────────────────────────────────

def test_load_house_config(house):
    assert house.scene == "house"
    assert house.display_name == "室内"
    assert len(house.region_types) > 0


def test_house_has_expected_region_types(house):
    for rt in ("bedroom", "kitchen", "bathroom", "living_room",
               "balcony", "hallway"):
        assert house.has_region_type(rt), f"缺少区域类型 {rt}"


def test_region_type_display_name(house):
    assert house.display_name_of("bedroom") == "卧室"
    assert house.display_name_of("kitchen") == "厨房"


def test_unknown_region_type_display_falls_back_to_key(house):
    assert house.display_name_of("nonexistent") == "nonexistent"


# ── 面积先验（重构的核心：只有一处来源）──────────────────────────────

def test_typical_area_from_config(house):
    assert house.typical_area("bedroom") == (8.0, 25.0)
    assert house.typical_area("kitchen") == (4.0, 15.0)
    assert house.typical_area("bathroom") == (2.0, 8.0)


def test_typical_area_unknown_uses_fallback(house):
    """未知区域类型不抛异常，用 fallback（识别出未知类型是常见情况）。"""
    assert house.typical_area("weird_room") == house.fallback_typical_area_m2


def test_area_prior_is_not_hardcoded_in_stage():
    """Stage 代码里不应再有硬编码的面积表。"""
    stage_file = (
        Path(__file__).resolve().parents[2]
        / "xasset" / "pipeline" / "stages" / "understand" / "scene_understand.py"
    )
    src = stage_file.read_text(encoding="utf-8")
    # 关键：不应出现硬编码面积字典的特征
    assert "_TYPICAL_AREA" not in src
    assert "living_room\": (18.0" not in src


# ── 可用场景 ────────────────────────────────────────────────────────────

def test_available_scenes_lists_house():
    scenes = available_scenes()
    assert "house" in scenes


# ── 可扩展性：新增场景只需配置 ──────────────────────────────────────────

def test_new_scene_needs_only_config_file(tmp_path):
    """模拟新增一个场景：只写 scene.json，不碰代码。"""
    scene_dir = tmp_path / "scifi"
    scene_dir.mkdir()
    (scene_dir / "scene.json").write_text(json.dumps({
        "scene": "scifi",
        "display_name": "科幻",
        "region_types": {
            "hangar": {
                "display_name": "机库",
                "typical_area_m2": [200.0, 2000.0],
            },
            "bridge": {
                "display_name": "舰桥",
                "typical_area_m2": [30.0, 80.0],
            },
        },
        "fallback_typical_area_m2": [50.0, 100.0],
    }), encoding="utf-8")

    cfg = load_scene_config("scifi", data_root=tmp_path)

    assert cfg.scene == "scifi"
    assert cfg.display_name == "科幻"
    assert cfg.has_region_type("hangar")
    assert cfg.typical_area("hangar") == (200.0, 2000.0)
    assert cfg.typical_area("bridge") == (30.0, 80.0)
    assert cfg.typical_area("unknown") == (50.0, 100.0)


def test_missing_scene_reports_actionable_error(tmp_path):
    """缺配置时给出可操作的错误信息（告诉用户该怎么建）。"""
    with pytest.raises(FileNotFoundError) as ei:
        load_scene_config("nonexistent", data_root=tmp_path)
    msg = str(ei.value)
    assert "scene.json" in msg
    assert "参考" in msg


# ── 与 rules.json 的一致性 ──────────────────────────────────────────────

def test_typical_area_matches_rules_json(house):
    """scene.json 与 rules.json 的面积区间必须一致（防止又出现两份不同步的数据）。"""
    rules_path = house.rules_path()
    assert rules_path is not None and rules_path.exists()

    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    for rt, block in (rules.get("region_rules") or {}).items():
        area = block.get("typical_area_m2")
        if not area:
            continue
        assert house.typical_area(rt) == (float(area[0]), float(area[1])), (
            f"区域 {rt} 的面积区间在 scene.json 与 rules.json 中不一致"
        )
