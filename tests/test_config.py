# tests/test_config.py
import pytest
from pathlib import Path
from xasset.config.loader import load_group_configs, get_groups_for_scene, get_group_by_code

DATA_DIR = Path(__file__).parent.parent / "xasset" / "data" / "groups"

def test_load_house_groups():
    configs = load_group_configs(DATA_DIR)
    assert "house" in configs
    assert len(configs["house"]) > 0

def test_get_meeting_group():
    load_group_configs(DATA_DIR)
    group = get_group_by_code("house", 100001)
    assert group is not None
    assert group.name == "客厅会客组"
    assert group.anchor_role == "sofa"

def test_role_tiers():
    load_group_configs(DATA_DIR)
    group = get_group_by_code("house", 100001)
    roles = {r.name: r for r in group.roles}
    assert roles["sofa"].tier == "anchor"
    assert roles["sofa"].optional is False
    assert roles["coffee_table"].optional is True

def test_cache_is_populated_after_load():
    """加载后缓存应已填充，不需要传 data_dir 也能查到"""
    group = get_group_by_code("house", 100001)
    assert group is not None
