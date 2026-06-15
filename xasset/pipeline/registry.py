# xasset/pipeline/registry.py
from xasset.pipeline.stage import Stage


class StageNotFound(Exception):
    pass


class StageRegistry:
    def __init__(self) -> None:
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

    def pipeline_for(self, config: "PipelineConfig") -> list[Stage]:
        from xasset.pipeline.pipeline import PipelineConfig
        return [self.get(layer, config.scene_type) for layer in config.stages]


def create_registry(house: bool = True, urban: bool = False, wild: bool = False) -> StageRegistry:
    """Create and populate StageRegistry with available stages.

    Callers only need to import this function — not individual stages.
    """
    from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage
    from xasset.pipeline.stages.surface.stage import SurfaceStage
    from xasset.pipeline.stages.accessory.stage import AccessoryStage
    from xasset.pipeline.stages.stylize.stylize import StylizeStage

    registry = StageRegistry()
    registry.register(SceneUnderstandStage())
    registry.register(SurfaceStage())
    registry.register(AccessoryStage())
    registry.register(StylizeStage())

    if house:
        from xasset.pipeline.stages.geometry.house.mesh_build import MeshBuildStage
        from xasset.pipeline.stages.layout.house.compose import HouseLayoutComposeStage
        from xasset.services.sample_search import SampleSearchService
        registry.register(MeshBuildStage())
        registry.register(HouseLayoutComposeStage(sample_search=SampleSearchService([])))

    return registry
