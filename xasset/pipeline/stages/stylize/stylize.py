# xasset/pipeline/stages/stylize/stylize.py
"""stylize 层 Stage —— 风格化（三场景共享）。

产物 schema 保持不变（StylizeOutput）。旧空桩实现已替换为 LLM 编排入口：
材质分配 + 灯光 + 相机（风格选择）将由 LLM 编排重做。
"""
from dataclasses import dataclass, field

from xasset.pipeline.context import PipelineContext


@dataclass
class StylizeOutput:
    material_assignments: list[dict] = field(default_factory=list)
    light_config: dict | None = None
    camera_hints: list[dict] = field(default_factory=list)


class StylizeStage:
    name = "stylize"
    layer = "stylize"
    scene_types = ["*"]

    def __init__(self, orchestrator=None) -> None:
        self._orchestrator = orchestrator

    def run(self, ctx: PipelineContext) -> None:
        # 算法重做过渡期：返回空产物（schema 契约不变），风格化待 LLM 重做。
        ctx.stage_outputs["stylize"] = StylizeOutput()
