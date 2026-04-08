# xasset/pipeline/stages/layout_compose.py
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext


@dataclass
class PlacedGroup:
    group_code: int              # references GroupDefinition.code
    region_type: str
    position: list[float]        # [x, y, z] group anchor, unit cm
    rotation: float              # Y-axis rotation in degrees
    role_assets: dict[str, str | None] = field(default_factory=dict)
    # role_name → asset_id string (None if unassigned)


@dataclass
class LayoutOutput:
    scene_type: str
    placed_groups: list[PlacedGroup] = field(default_factory=list)


class HouseLayoutComposeStage:
    name = "layout_compose"
    scene_types = ["house"]

    def run(self, ctx: PipelineContext) -> None:
        """Stub: returns empty layout. Full implementation in Task 9."""
        ctx.stage_outputs["layout_compose"] = LayoutOutput(
            scene_type=ctx.input.scene_type,
        )
