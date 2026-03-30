# xasset/config/loader.py
import json
from pathlib import Path
from xasset.config.schemas import GroupConfigFile, GroupDefinition

_DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data" / "groups"
_group_cache: dict[str, list[GroupDefinition]] = {}

def load_group_configs(
    data_dir: Path = _DEFAULT_DATA_DIR,
    force_reload: bool = False,
) -> dict[str, list[GroupDefinition]]:
    global _group_cache
    if _group_cache and not force_reload:
        return _group_cache

    _group_cache.clear()
    for json_file in data_dir.glob("*.json"):
        raw = json.loads(json_file.read_text(encoding="utf-8"))
        config = GroupConfigFile(**raw)
        _group_cache[config.scene_type] = config.groups

    return _group_cache

def get_groups_for_scene(scene_type: str) -> list[GroupDefinition]:
    cache = _group_cache if _group_cache else load_group_configs()
    return cache.get(scene_type, [])

def get_group_by_code(scene_type: str, code: int) -> GroupDefinition | None:
    for group in get_groups_for_scene(scene_type):
        if group.code == code:
            return group
    return None
