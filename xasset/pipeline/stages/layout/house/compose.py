# xasset/pipeline/stages/layout/house/compose.py
"""layout 层 Stage —— 组合布局（house）。

产物 schema 保持不变（LayoutOutput / PlacedGroup / OpeningPlacement /
CurtainPlacement），但组合布局算法（Group 摆放、门窗落位规则）已被清理，
待 LLM 编排重做。旧的 RoomDecomposer / groups.json 规则式约束基础设施
一并清理，由 LLM 候选生成 + 约束校验闸门（tools/constraint）取代。
"""
from dataclasses import dataclass, field

from xasset.pipeline.context import PipelineContext
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandOutput


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


class HouseLayoutComposeStage:
    """组合布局（house）—— 算法待 LLM 编排重做。

    门窗/窗帘落位与 Group 摆放原本依赖 RoomDecomposer 的规则式几何分析，
    现已清理。过渡期返回空的 LayoutOutput（schema 契约不变）。
    """

    name = "layout_compose"
    layer = "layout"
    scene_types = ["house"]

    def __init__(self, sample_search=None, orchestrator=None) -> None:
        self._sample_search = sample_search
        self._orchestrator = orchestrator

    def run(self, ctx: PipelineContext) -> None:
        scene_out: SceneUnderstandOutput | None = ctx.stage_outputs.get("understand")
        scene_type = ctx.input.scene_type

        ctx.stage_outputs["layout"] = LayoutOutput(
            scene_type=scene_type,
            placed_groups=[],
            doors=[],
            windows=[],
            curtains=[],
        )
