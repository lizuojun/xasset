# xasset/config/loader.py
import json
from pathlib import Path
from xasset.config.schemas import GroupConfigFile, GroupDefinition, RegionGroupEntry

_DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data" / "groups"
_group_cache: dict[str, list[GroupDefinition]] = {}
_region_group_cache: dict[str, dict[str, list[RegionGroupEntry]]] = {}

def load_group_configs(
    data_dir: Path = _DEFAULT_DATA_DIR,
    force_reload: bool = False,
) -> dict[str, list[GroupDefinition]]:
    global _group_cache, _region_group_cache
    if _group_cache and not force_reload:
        return _group_cache

    _group_cache.clear()
    _region_group_cache.clear()
    for json_file in data_dir.glob("*.json"):
        raw = json.loads(json_file.read_text(encoding="utf-8"))
        config = GroupConfigFile(**raw)
        _group_cache[config.scene_type] = config.groups
        _region_group_cache[config.scene_type] = config.region_groups

    return _group_cache

def get_groups_for_scene(scene_type: str) -> list[GroupDefinition]:
    cache = _group_cache if _group_cache else load_group_configs()
    return cache.get(scene_type, [])

def get_group_by_code(scene_type: str, code: int) -> GroupDefinition | None:
    for group in get_groups_for_scene(scene_type):
        if group.code == code:
            return group
    return None

def get_region_groups(scene_type: str) -> dict[str, list[RegionGroupEntry]]:
    """Return region_groups mapping for the given scene type.
    Keys are region_type strings; values are lists of RegionGroupEntry sorted by priority."""
    if not _region_group_cache:
        load_group_configs()
    return _region_group_cache.get(scene_type, {})
