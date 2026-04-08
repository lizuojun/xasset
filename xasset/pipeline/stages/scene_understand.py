# xasset/pipeline/stages/scene_understand.py
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext


@dataclass
class SceneRegion:
    region_type: str             # "living_room" | "bedroom" | "dining_room" | etc.
    boundary: list[list[float]]  # polygon vertices, XZ plane, Y-up, unit cm
    area: float                  # m²


@dataclass
class SceneUnderstandOutput:
    scene_type: str
    regions: list[SceneRegion]
    style: str | None = None
    constraints: dict = field(default_factory=dict)


class SceneUnderstandStage:
    name = "scene_understand"
    scene_types = ["*"]

    def run(self, ctx: PipelineContext) -> None:
        """Stub: returns a fixed living room region for any house input."""
        ctx.stage_outputs["scene_understand"] = SceneUnderstandOutput(
            scene_type=ctx.input.scene_type,
            style=ctx.input.style,
            regions=[
                SceneRegion(
                    region_type="living_room",
                    boundary=[[0, 0, 0], [500, 0, 0], [500, 0, 400], [0, 0, 400]],
                    area=20.0,
                )
            ],
        )
