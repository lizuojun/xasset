# xasset/pipeline/stages/layout_compose.py
from dataclasses import dataclass, field
from pathlib import Path

from xasset.pipeline.context import PipelineContext
from xasset.pipeline.stages.scene_understand import SceneUnderstandOutput, SceneRegion
from xasset.config.loader import load_group_configs, get_group_by_code
from xasset.config.schemas import GroupDefinition

# Region type → GroupDefinition code 映射
# 每个区域类型对应一个主 Group（furniture 大类）
# Surface 组（墙/顶/地/窗）由 StylizeStage 处理，不在此映射
_REGION_TO_GROUP: dict[str, int] = {
    "living_room":        100001,   # 客厅会客组
    "living_dining_room": 100002,   # 客餐厅会客组
    "dining_room":        100101,   # 餐厅餐桌组
    "master_bedroom":     100201,   # 主卧床组
    "bedroom":            100202,   # 次卧床组
    "kids_room":          100203,   # 儿童房床组
    "library":            100301,   # 书房工作组
    "study":              100301,   # 书房工作组（别名）
    "balcony":            100401,   # 阳台休闲组
    "hallway":            100502,   # 玄关柜
    "bathroom":           100601,   # 卫生间马桶组
    "master_bathroom":    100602,   # 主卫马桶组
    "kitchen":            100801,   # 厨房电器组
}

# GroupDefinition config directory
_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "groups"


@dataclass
class PlacedGroup:
    group_code: int
    region_type: str
    position: list[float]          # [x, y, z] group anchor, unit cm
    rotation: float                # Y-axis rotation in degrees
    role_assets: dict[str, str | None] = field(default_factory=dict)
    # role_name → asset_id string or None if not yet assigned


@dataclass
class LayoutOutput:
    scene_type: str
    placed_groups: list[PlacedGroup] = field(default_factory=list)


class HouseLayoutComposeStage:
    name = "layout_compose"
    scene_types = ["house"]

    def __init__(self, mesh_service, sample_search) -> None:
        self._mesh = mesh_service
        self._sample_search = sample_search
        load_group_configs(_DATA_DIR)

    def run(self, ctx: PipelineContext) -> None:
        scene_out: SceneUnderstandOutput | None = ctx.stage_outputs.get("scene_understand")
        placed_groups: list[PlacedGroup] = []

        regions = scene_out.regions if scene_out else []
        for region in regions:
            group_code = _REGION_TO_GROUP.get(region.region_type)
            if group_code is None:
                continue
            group_def = get_group_by_code("house", group_code)
            if group_def is None:
                continue
            placed = self._place_group(group_def, region)
            placed_groups.append(placed)

        ctx.stage_outputs["layout_compose"] = LayoutOutput(
            scene_type=ctx.input.scene_type,
            placed_groups=placed_groups,
        )

    def _place_group(self, group_def: GroupDefinition, region: SceneRegion) -> PlacedGroup:
        # Compute anchor position: center of region boundary at floor level
        xs = [v[0] for v in region.boundary]
        zs = [v[2] for v in region.boundary]
        cx = (min(xs) + max(xs)) / 2
        cz = (min(zs) + max(zs)) / 2

        role_assets: dict[str, str | None] = {
            role.name: None for role in group_def.roles
        }

        return PlacedGroup(
            group_code=group_def.code,
            region_type=region.region_type,
            position=[cx, 0.0, cz],
            rotation=0.0,
            role_assets=role_assets,
        )
