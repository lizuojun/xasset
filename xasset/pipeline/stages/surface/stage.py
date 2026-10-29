# xasset/pipeline/stages/surface/stage.py
"""surface 层 Stage —— 表面覆盖（house/urban/wild 共享）。

产物 schema 保持不变（SurfaceOutput）。旧桩实现已替换为 LLM 编排入口：
表面覆盖（硬装铺贴 / 道路基础面 / 地貌基底）将由 LLM 编排重做。
"""
from dataclasses import dataclass, field

from xasset.pipeline.context import PipelineContext


@dataclass
class SurfaceOutput:
    scene_type: str
    elements: list = field(default_factory=list)
    status: str = "stub"


class SurfaceStage:
    name = "surface"
    layer = "surface"
    scene_types = ["house", "urban", "wild"]

    def __init__(self, orchestrator=None) -> None:
        self._orchestrator = orchestrator

    def run(self, ctx: PipelineContext) -> None:
        # 算法重做过渡期：返回空产物（schema 契约不变），表面覆盖待 LLM 重做。
        ctx.stage_outputs["surface"] = SurfaceOutput(
            scene_type=ctx.input.scene_type,
        )
