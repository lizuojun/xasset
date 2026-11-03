# xasset/pipeline/stages/accessory/stage.py
"""accessory 层 Stage —— 细节阶段：点缀物散布（house/urban/wild 共享）。

契约见 xasset/pipeline/schemas/accessory.py。
小饰品 / 路灯标识牌 / 碎石灌木待按 Artist 范式重做。
"""
from __future__ import annotations

from xasset.pipeline.schemas import AccessoryOutput
from xasset.pipeline.stage import StageInputs


class AccessoryStage:
    name = "accessory"
    layer = "accessory"
    scene_types = ["house", "urban", "wild"]
    requires = ["understand", "layout"]
    output_type = AccessoryOutput

    def __init__(self, orchestrator=None) -> None:
        self._orchestrator = orchestrator

    def run(self, inputs: StageInputs) -> AccessoryOutput:
        # 算法重做过渡期：返回空产物（契约不变）。
        return AccessoryOutput(scene_type=inputs.pipeline_input.scene_type)
