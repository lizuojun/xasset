# xasset/pipeline/stages/layout_compose.py
from dataclasses import dataclass, field
from pathlib import Path

from xasset.pipeline.context import PipelineContext
from xasset.pipeline.stages.scene_understand import SceneUnderstandOutput, SceneRegion
from xasset.config.loader import load_group_configs, get_group_by_code, get_region_groups
from xasset.config.schemas import GroupDefinition

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

        region_groups = get_region_groups("house")
        regions = scene_out.regions if scene_out else []
        for region in regions:
            entries = sorted(
                region_groups.get(region.region_type, []),
                key=lambda e: e.priority,
            )
            for entry in entries:
                group_def = get_group_by_code("house", entry.code)
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
