# xasset/pipeline/stages/accessory/stage.py
"""accessory 层 Stage —— 装饰点缀（house/urban/wild 共享）。

产物 schema 保持不变（AccessoryOutput）。旧桩实现已替换为 LLM 编排入口：
装饰点缀（小饰品 / 路灯标识牌 / 碎石灌木）将由 LLM 编排重做。
"""
from dataclasses import dataclass, field

from xasset.pipeline.context import PipelineContext


@dataclass
class AccessoryOutput:
    scene_type: str
    elements: list = field(default_factory=list)
    status: str = "stub"


class AccessoryStage:
    name = "accessory"
    layer = "accessory"
    scene_types = ["house", "urban", "wild"]

    def __init__(self, orchestrator=None) -> None:
        self._orchestrator = orchestrator

    def run(self, ctx: PipelineContext) -> None:
        # 算法重做过渡期：返回空产物（schema 契约不变），装饰点缀待 LLM 重做。
        ctx.stage_outputs["accessory"] = AccessoryOutput(
            scene_type=ctx.input.scene_type,
        )
