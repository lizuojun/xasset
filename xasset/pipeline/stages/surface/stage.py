from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext


@dataclass
class SurfaceOutput:
    scene_type: str
    elements: list = field(default_factory=list)
    status: str = "stub"


class SurfaceStage:
    name = "surface"
    layer = "surface"
    scene_types = ["house", "urban", "wild"]

    def __init__(self) -> None:
        pass

    def run(self, ctx: PipelineContext) -> None:
        ctx.stage_outputs["surface"] = SurfaceOutput(
            scene_type=ctx.input.scene_type,
        )
