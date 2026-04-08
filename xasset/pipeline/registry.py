# xasset/pipeline/registry.py
from xasset.pipeline.stage import Stage


class StageNotFound(Exception):
    pass


class StageRegistry:
    def __init__(self) -> None:
        # name → { scene_type → Stage }
        self._stages: dict[str, dict[str, Stage]] = {}

    def register(self, stage: Stage) -> "StageRegistry":
        if stage.name not in self._stages:
            self._stages[stage.name] = {}
        for scene_type in stage.scene_types:
            self._stages[stage.name][scene_type] = stage
        return self

    def get(self, name: str, scene_type: str) -> Stage:
        if name not in self._stages:
            raise StageNotFound(f"Stage '{name}' not registered")
        bucket = self._stages[name]
        if scene_type in bucket:
            return bucket[scene_type]
        if "*" in bucket:
            return bucket["*"]
        raise StageNotFound(
            f"Stage '{name}' has no implementation for scene_type='{scene_type}'"
        )

    def pipeline_for(self, config: "PipelineConfig") -> list[Stage]:  # type: ignore[name-defined]
        from xasset.pipeline.pipeline import PipelineConfig  # avoid circular import
        return [self.get(name, config.scene_type) for name in config.stages]
