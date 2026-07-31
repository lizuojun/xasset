# xasset/pipeline/stages/layout/house/compose.py
"""House layout stage — furniture group placement (zone planning TODO, currently a stub)."""
from dataclasses import dataclass, field
import math

from xasset.pipeline.context import PipelineContext
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandOutput
from xasset.pipeline.stages.layout.house.room_decompose import RoomDecomposer


@dataclass
class PlacedGroup:
    group_code: int
    region_type: str
    position: list[float]          # [x, y, z] unit m
    rotation: float                # Y-axis rotation in degrees
    role_assets: dict[str, str | None] = field(default_factory=dict)
    sub_positions: dict[str, list[float]] = field(default_factory=dict)


@dataclass
class OpeningPlacement:
    opening_id: str
    opening_type: str           # "door" | "window"
    position: list[float]       # [x, y, z] unit m
    rotation: float             # Y-axis rotation in degrees
    width: float                # m


@dataclass
class CurtainPlacement:
    window_id: str
    position: list[float]       # [x, y, z] unit m
    rotation: float
    width: float                # m


@dataclass
class LayoutOutput:
    scene_type: str
    placed_groups: list[PlacedGroup] = field(default_factory=list)
    doors: list[OpeningPlacement] = field(default_factory=list)
    windows: list[OpeningPlacement] = field(default_factory=list)
    curtains: list[CurtainPlacement] = field(default_factory=list)


def _correct_region_types(regions: list) -> list:
    """Adjust region types based on house-level context (mirrors old import_house logic)."""
    type_counts: dict[str, int] = {}
    for r in regions:
        t = r.region_type
        type_counts[t] = type_counts.get(t, 0) + 1

    for r in regions:
        rt = r.region_type
        if rt == "living_room":
            if type_counts.get("dining_room", 0) == 0 and r.area >= 20:
                r.region_type = "living_dining_room"
    return regions


class HouseLayoutComposeStage:
    """Furniture group placement (zone planning) — TODO: not yet implemented.

    Door/window/curtain placement below is derived from RoomDecomposer and is
    considered correct; placed_groups is intentionally left empty pending a
    redesigned zone-planning algorithm.
    """
    name = "layout_compose"
    layer = "layout"
    scene_types = ["house"]

    def __init__(self, sample_search=None) -> None:
        self._sample_search = sample_search
        self._decomposer = RoomDecomposer()

    def run(self, ctx: PipelineContext) -> None:
        scene_out: SceneUnderstandOutput | None = ctx.stage_outputs.get("understand")
        placed_groups: list[PlacedGroup] = []

        if scene_out is None:
            ctx.stage_outputs["layout"] = LayoutOutput(
                scene_type=ctx.input.scene_type,
                placed_groups=placed_groups,
            )
            return

        _correct_region_types(scene_out.regions)

        ctx._layout_debug = {}  # for debug renderer

        doors: list[OpeningPlacement] = []
        windows: list[OpeningPlacement] = []
        out_curtains: list[CurtainPlacement] = []

        for region in scene_out.regions:
            walls, curtains = self._decomposer.decompose(region)
            ctx._layout_debug.setdefault("walls", {})[region.region_id] = walls
            ctx._layout_debug.setdefault("curtains", {})[region.region_id] = curtains

            for door in region.doors:
                if door.seg_start and door.seg_end:
                    pos = [(door.seg_start[0] + door.seg_end[0]) / 2, 0.0,
                           (door.seg_start[1] + door.seg_end[1]) / 2]
                    dx = door.seg_end[0] - door.seg_start[0]
                    dz = door.seg_end[1] - door.seg_start[1]
                    rot = math.degrees(math.atan2(dz, dx))
                    doors.append(OpeningPlacement(
                        opening_id=door.id, opening_type="door",
                        position=[round(v, 3) for v in pos],
                        rotation=round(rot, 1),
                        width=round(door.width, 3),
                    ))
            for win in region.windows:
                if win.seg_start and win.seg_end:
                    pos = [(win.seg_start[0] + win.seg_end[0]) / 2, win.sill_height,
                           (win.seg_start[1] + win.seg_end[1]) / 2]
                    dx = win.seg_end[0] - win.seg_start[0]
                    dz = win.seg_end[1] - win.seg_start[1]
                    rot = math.degrees(math.atan2(dz, dx))
                    windows.append(OpeningPlacement(
                        opening_id=win.id, opening_type="window",
                        position=[round(v, 3) for v in pos],
                        rotation=round(rot, 1),
                        width=round(win.width, 3),
                    ))
            for cz in curtains:
                pos = [(cz.p0[0] + cz.p1[0]) / 2, 0.0, (cz.p0[1] + cz.p1[1]) / 2]
                dx = cz.p1[0] - cz.p0[0]
                dz = cz.p1[1] - cz.p0[1]
                rot = math.degrees(math.atan2(dz, dx))
                out_curtains.append(CurtainPlacement(
                    window_id=cz.window_id,
                    position=[round(v, 3) for v in pos],
                    rotation=round(rot, 1),
                    width=round(cz.width, 3),
                ))

        ctx.stage_outputs["layout"] = LayoutOutput(
            scene_type=ctx.input.scene_type,
            placed_groups=placed_groups,
            doors=doors,
            windows=windows,
            curtains=out_curtains,
        )
