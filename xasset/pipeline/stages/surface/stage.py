# xasset/pipeline/stages/surface/stage.py
"""surface 层 Stage —— 主体阶段：表面覆盖（house/urban/wild 共享）。

契约见 xasset/pipeline/schemas/surface.py。
硬装铺贴 / 道路基础面 / 地貌基底待按 Artist 范式重做。
"""
from __future__ import annotations

from xasset.pipeline.schemas import SurfaceOutput
from xasset.pipeline.stage import StageInputs


class SurfaceStage:
    name = "surface"
    layer = "surface"
    scene_types = ["house", "urban", "wild"]
    requires = ["understand", "geometry"]
    output_type = SurfaceOutput

    def __init__(self, orchestrator=None) -> None:
        self._orchestrator = orchestrator

    def run(self, inputs: StageInputs) -> SurfaceOutput:
        # 算法重做过渡期：返回空产物（契约不变）。
        return SurfaceOutput(scene_type=inputs.pipeline_input.scene_type)
