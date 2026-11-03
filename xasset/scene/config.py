# xasset/scene/config.py
"""场景定义加载 —— 场景知识的唯一入口。

**这是"少做重复、可扩展"的关键模块。**

问题（重构前）：
    面积先验在两处硬编码——`scene_understand.py` 里一份字典，
    `data/house/rules.json` 里一份。改一处不同步；加 urban 要再复制一份。

解决：
    所有场景知识（区域词表、面积先验、显示名）统一放 `data/<scene>/scene.json`，
    **代码里不出现任何具体数值或区域名**。加新场景只需加一份配置文件。

设计原则见 docs/scene-config.md。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

# 默认场景数据目录（可被测试覆盖）
_DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


@dataclass
class RegionTypeSpec:
    """一个区域类型的定义。"""

    region_type: str
    display_name: str = ""
    typical_area_m2: tuple[float, float] | None = None

    def __repr__(self) -> str:
        return f"RegionTypeSpec({self.region_type!r}, area={self.typical_area_m2})"


@dataclass
class SceneConfig:
    """一个场景的完整定义。"""

    scene: str
    display_name: str = ""
    version: int = 1
    region_types: dict[str, RegionTypeSpec] = field(default_factory=dict)
    fallback_typical_area_m2: tuple[float, float] = (8.0, 25.0)
    rules_file: str | None = None
    data_dir: Path | None = None

    # ── 区域类型查询 ────────────────────────────────────────

    def has_region_type(self, region_type: str) -> bool:
        return region_type in self.region_types

    def get_region_type(self, region_type: str) -> RegionTypeSpec | None:
        return self.region_types.get(region_type)

    def region_type_names(self) -> list[str]:
        return list(self.region_types)

    def display_name_of(self, region_type: str) -> str:
        spec = self.region_types.get(region_type)
        return spec.display_name if spec and spec.display_name else region_type

    # ── 面积先验（原来在两处硬编码，现在唯一来源）────────────

    def typical_area(self, region_type: str) -> tuple[float, float]:
        """该区域类型的典型面积区间。

        未知类型返回 fallback，**不会抛异常**——因为识别出未知类型是常见情况
        （如老房子里的"储藏间"），不应该让整个流程失败。
        """
        spec = self.region_types.get(region_type)
        if spec and spec.typical_area_m2:
            return spec.typical_area_m2
        return self.fallback_typical_area_m2

    # ── 规则文件路径 ────────────────────────────────────────

    def rules_path(self) -> Path | None:
        if not self.rules_file or self.data_dir is None:
            return None
        p = self.data_dir / self.rules_file
        return p if p.exists() else None


# ── 加载 ────────────────────────────────────────────────────────────────

@lru_cache(maxsize=16)
def _load_scene_config(scene: str, data_root_str: str) -> SceneConfig:
    """带缓存的加载（同一场景不重复读盘）。"""
    root = Path(data_root_str)
    path = root / scene / "scene.json"
    if not path.exists():
        raise FileNotFoundError(
            f"场景 '{scene}' 的配置文件不存在: {path}\n"
            f"新增场景需要先创建 data/{scene}/scene.json（结构可参考 data/house/scene.json）"
        )

    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)

    region_types: dict[str, RegionTypeSpec] = {}
    for rt_name, rt_def in (raw.get("region_types") or {}).items():
        area = rt_def.get("typical_area_m2")
        region_types[rt_name] = RegionTypeSpec(
            region_type=rt_name,
            display_name=rt_def.get("display_name", ""),
            typical_area_m2=(float(area[0]), float(area[1])) if area else None,
        )

    fb = raw.get("fallback_typical_area_m2") or [8.0, 25.0]

    return SceneConfig(
        scene=raw.get("scene", scene),
        display_name=raw.get("display_name", ""),
        version=int(raw.get("version", 1)),
        region_types=region_types,
        fallback_typical_area_m2=(float(fb[0]), float(fb[1])),
        rules_file=raw.get("rules_file"),
        data_dir=root / scene,
    )


def load_scene_config(
    scene: str,
    data_root: str | Path | None = None,
) -> SceneConfig:
    """加载场景定义。

    Parameters
    ----------
    scene : 场景标识（"house" / "urban" / ...）
    data_root : 数据根目录，默认项目根的 data/
    """
    root = Path(data_root) if data_root else _DEFAULT_DATA_ROOT
    return _load_scene_config(scene, str(root))


def available_scenes(data_root: str | Path | None = None) -> list[str]:
    """列出所有已定义的场景（有 scene.json 的目录）。"""
    root = Path(data_root) if data_root else _DEFAULT_DATA_ROOT
    if not root.exists():
        return []
    return sorted(
        p.parent.name for p in root.glob("*/scene.json")
    )
