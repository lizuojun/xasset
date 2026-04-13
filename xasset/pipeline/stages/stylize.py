# xasset/pipeline/stages/stylize.py
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext


@dataclass
class StylizeOutput:
    material_assignments: list[dict] = field(default_factory=list)
    light_config: dict | None = None
    camera_hints: list[dict] = field(default_factory=list)


class StylizeStage:
    name = "stylize"
    layer = "stylize"
    scene_types = ["*"]

    def run(self, ctx: PipelineContext) -> None:
        """Stub: returns empty stylize output."""
        ctx.stage_outputs["stylize"] = StylizeOutput()
