# xasset/pipeline/stage.py
from typing import Protocol, runtime_checkable
from xasset.pipeline.context import PipelineContext


@runtime_checkable
class Stage(Protocol):
    name: str
    scene_types: list[str]       # ["house"] or ["*"] for all scene types

    def run(self, ctx: PipelineContext) -> None:
        """Execute stage logic. Write output to ctx.stage_outputs[self.name].
        Raise an exception to signal failure."""
        ...
