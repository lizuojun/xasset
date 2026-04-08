# xasset/pipeline/pipeline.py
import uuid
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.registry import StageRegistry


@dataclass
class PipelineConfig:
    scene_type: str
    stages: list[str]
    stage_configs: dict[str, dict] = field(default_factory=dict)


class Pipeline:
    def __init__(self, registry: StageRegistry) -> None:
        self._registry = registry

    def run(
        self,
        input: PipelineInput,
        config: PipelineConfig,
        job_id: str | None = None,
    ) -> PipelineContext:
        """Execute all stages in order. Returns PipelineContext.
        Raises the stage exception on failure (after setting ctx.status='failed')."""
        ctx = PipelineContext(
            job_id=job_id or str(uuid.uuid4()),
            input=input,
        )
        try:
            for stage_name in config.stages:
                stage = self._registry.get(stage_name, config.scene_type)
                stage.run(ctx)
            ctx.status = "done"
        except Exception as exc:
            ctx.status = "failed"
            ctx.error = str(exc)
            raise
        return ctx
