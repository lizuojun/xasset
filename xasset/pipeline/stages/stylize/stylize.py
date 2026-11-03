# xasset/pipeline/stages/stylize/stylize.py
"""stylize 层 Stage —— 细节阶段：风格化（三场景共享）。

契约见 xasset/pipeline/schemas/stylize.py。
材质分配 + 灯光 + 相机待按 Artist 范式重做。
"""
from __future__ import annotations

from xasset.pipeline.schemas import StylizeOutput
from xasset.pipeline.stage import StageInputs


class StylizeStage:
    name = "stylize"
    layer = "stylize"
    scene_types = ["*"]
    requires = ["understand", "geometry", "layout", "surface", "accessory"]
    output_type = StylizeOutput

    def __init__(self, orchestrator=None) -> None:
        self._orchestrator = orchestrator

    def run(self, inputs: StageInputs) -> StylizeOutput:
        # 算法重做过渡期：返回空产物（契约不变）。
        return StylizeOutput(style=inputs.pipeline_input.style)
