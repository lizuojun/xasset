# xasset/pipeline/pipeline.py
"""Pipeline 执行器 —— 按需注入上游产物、强校验阶段产物类型。

契约规范见 docs/stage-io-contract-spec.md。
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from xasset.pipeline.context import PipelineContext, PipelineInput
from xasset.pipeline.registry import StageRegistry
from xasset.pipeline.stage import (
    StageContractViolation,
    StageDependencyMissing,
    StageInputs,
)


@dataclass
class PipelineConfig:
    scene_type: str
    stages: list[str]
    stage_configs: dict[str, dict] = field(default_factory=dict)


class Pipeline:
    def __init__(self, registry: StageRegistry) -> None:
        self._registry = registry

    def run(
        self,
        input: PipelineInput,
        config: PipelineConfig,
        job_id: str | None = None,
    ) -> PipelineContext:
        """按顺序执行所有 Stage，返回 PipelineContext。

        每个 Stage 执行前校验其 requires 声明的上游已产出；执行后强校验
        返回类型与 output_type 一致。任一环节失败即中断并标记 failed。
        """
        ctx = PipelineContext(
            job_id=job_id or str(uuid.uuid4()),
            input=input,
        )
        try:
            for layer in config.stages:
                stage = self._registry.get(layer, config.scene_type)

                # 1) 依赖校验：requires 声明的上游必须已产出
                for dep in getattr(stage, "requires", []):
                    if dep not in ctx.stage_outputs:
                        raise StageDependencyMissing(
                            f"Stage '{stage.name}' 依赖上游 '{dep}'，"
                            f"但该层尚未产出（当前已有: "
                            f"{sorted(ctx.stage_outputs)}）"
                        )

                # 2) 注入：只给声明的上游产物
                declared = getattr(stage, "requires", [])
                inputs = StageInputs(
                    input,
                    {d: ctx.stage_outputs[d] for d in declared},
                )

                # 3) 执行
                output = stage.run(inputs)

                # 4) 输出契约强校验
                expected = getattr(stage, "output_type", None)
                if expected is not None and not isinstance(output, expected):
                    raise StageContractViolation(
                        f"Stage '{stage.name}' 产出类型 {type(output).__name__} "
                        f"与声明的 output_type {expected.__name__} 不符"
                    )

                # 5) 写入
                ctx.stage_outputs[layer] = output

            ctx.status = "done"
        except Exception as exc:
            ctx.status = "failed"
            ctx.error = str(exc)
            raise
        return ctx
