# xasset/pipeline/registry.py
from xasset.pipeline.stage import Stage


class StageNotFound(Exception):
    pass


class StageRegistry:
    def __init__(self) -> None:
        # layer → { scene_type → Stage }
        self._stages: dict[str, dict[str, Stage]] = {}

    def register(self, stage: Stage) -> "StageRegistry":
        if stage.layer not in self._stages:
            self._stages[stage.layer] = {}
        for scene_type in stage.scene_types:
            self._stages[stage.layer][scene_type] = stage
        return self

    def get(self, layer: str, scene_type: str) -> Stage:
        if layer not in self._stages:
            raise StageNotFound(f"Stage layer '{layer}' not registered")
        bucket = self._stages[layer]
        if scene_type in bucket:
            return bucket[scene_type]
        if "*" in bucket:
            return bucket["*"]
        raise StageNotFound(
            f"Stage layer '{layer}' has no implementation for scene_type='{scene_type}'"
        )

    def pipeline_for(self, config: "PipelineConfig") -> list[Stage]:  # type: ignore[name-defined]
        from xasset.pipeline.pipeline import PipelineConfig  # avoid circular import
        return [self.get(layer, config.scene_type) for layer in config.stages]
