# xasset/services/generation.py
import uuid
from datetime import datetime, timezone

from xasset.pipeline.context import PipelineInput, VariationInput
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.jobs.job import Job, JobResult, JobStatus
from xasset.jobs.store import InMemoryJobStore


_DEFAULT_HOUSE_STAGES = ["scene_understand", "layout_compose", "stylize"]


class GenerationService:
    """Main entry point for asset generation.

    submit() is synchronous internally but exposes async-compatible semantics
    (submit → job_id → get_status → get_result).
    """

    def __init__(self, pipeline: Pipeline, job_store: InMemoryJobStore) -> None:
        self._pipeline = pipeline
        self._job_store = job_store

    def submit(
        self,
        input: PipelineInput,
        config: PipelineConfig | None = None,
    ) -> str:
        """Run the pipeline synchronously and store the result. Returns job_id."""
        job = Job()
        job.status = "running"
        self._job_store.create(job)

        if config is None:
            stages = _DEFAULT_HOUSE_STAGES if input.scene_type == "house" else []
            config = PipelineConfig(scene_type=input.scene_type, stages=stages)

        try:
            ctx = self._pipeline.run(input, config, job_id=job.id)
            job.status = "done"
            job.finished_at = datetime.now(timezone.utc)
            job.result = JobResult(
                job_id=job.id,
                asset_id=None,
                stage_outputs=ctx.stage_outputs,
            )
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            job.finished_at = datetime.now(timezone.utc)

        self._job_store.update(job)
        return job.id

    def submit_variation(
        self,
        source_asset_id: uuid.UUID,
        variation: VariationInput,
        scene_type: str = "house",
    ) -> str:
        """Run a partial pipeline to produce a variation of an existing asset.

        Which stages run is determined by the variation flags.
        Whether the result is saved as a new AssetDefinition is the caller's decision.

        Args:
            source_asset_id: The asset being varied.
            variation: Flags controlling which pipeline stages run.
            scene_type: Scene type of the source asset. Defaults to "house";
                callers must pass the correct value for urban/wild assets.
        """
        stages: list[str] = []
        if variation.replace_models or variation.replace_accessories:
            stages.append("layout_compose")
        if variation.replace_materials or variation.replace_lights:
            stages.append("stylize")
        if not stages:
            stages = ["stylize"]

        inp = PipelineInput(
            input_type="text",
            scene_type=scene_type,
            constraints={"source_asset_id": str(source_asset_id)},
            style=variation.style,
        )
        config = PipelineConfig(scene_type=scene_type, stages=stages)
        return self.submit(inp, config=config)

    def get_status(self, job_id: str) -> JobStatus:
        job = self._job_store.get(job_id)
        if job is None:
            raise KeyError(f"Job '{job_id}' not found")
        return JobStatus(
            job_id=job.id,
            status=job.status,
            progress=1.0 if job.status in ("done", "failed") else 0.5,
            message=job.error,
        )

    def get_result(self, job_id: str) -> JobResult:
        job = self._job_store.get(job_id)
        if job is None:
            raise KeyError(f"Job '{job_id}' not found")
        if job.result is None:
            return JobResult(
                job_id=job.id,
                asset_id=None,
                stage_outputs={},
                error=job.error,
            )
        return job.result

    def cancel(self, job_id: str) -> None:
        """No-op for synchronous execution. Reserved for future async queue."""
        pass
