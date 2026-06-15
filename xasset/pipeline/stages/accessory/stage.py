from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext


@dataclass
class AccessoryOutput:
    scene_type: str
    elements: list = field(default_factory=list)
    status: str = "stub"


class AccessoryStage:
    name = "accessory"
    layer = "accessory"
    scene_types = ["house", "urban", "wild"]

    def __init__(self) -> None:
        pass

    def run(self, ctx: PipelineContext) -> None:
        ctx.stage_outputs["accessory"] = AccessoryOutput(
            scene_type=ctx.input.scene_type,
        )
