# xasset/pipeline/stages/layout/house/compose.py
"""layout 层 Stage —— 主体阶段：组合摆放（house）。

契约见 xasset/pipeline/schemas/layout.py。

组合摆放算法（Group 摆放、门窗落位）已在算法重做中清理，待按 Artist
范式重做：理解侧选候选（LLM 或打分模型），约束侧做碰撞/净宽/越界求解。
旧的 RoomDecomposer / groups.json 规则式约束基础设施一并清理。
"""
from __future__ import annotations

from xasset.pipeline.schemas import LayoutOutput
from xasset.pipeline.stage import StageInputs


class HouseLayoutComposeStage:
    name = "layout_compose"
    layer = "layout"
    scene_types = ["house"]
    requires = ["understand"]
    output_type = LayoutOutput

    def __init__(self, orchestrator=None) -> None:
        self._orchestrator = orchestrator

    def run(self, inputs: StageInputs) -> LayoutOutput:
        # 算法重做过渡期：返回空的 LayoutOutput（契约不变）。
        return LayoutOutput(scene_type=inputs.pipeline_input.scene_type)
