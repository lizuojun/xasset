# xasset/pipeline/stage.py
"""Stage 接口契约 —— 每个 Stage 的输入输出规范。

契约规范见 docs/stage-io-contract-spec.md。

核心变化（相对旧接口）：
- 旧：run(ctx) -> None，产物靠 ctx.stage_outputs[layer] = ... 隐式写入
- 新：run(inputs) -> T，产物类型由 output_type 声明，框架强校验

依赖通过 requires 显式声明，框架按声明注入 StageInputs（只含声明的上游
阶段产物），未声明的依赖访问会直接报错而不是静默拿到 None。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from pydantic import BaseModel

    from xasset.pipeline.context import PipelineInput

TOut = TypeVar("TOut", bound="BaseModel")


@runtime_checkable
class Stage(Protocol, Generic[TOut]):
    """一个工作阶段的接口契约。

    实现者需要提供的属性/方法：

    name
        Stage 的唯一标识（如 "scene_understand"）。
    layer
        所属层，六层之一：understand / geometry / layout / surface /
        accessory / stylize。框架按 (layer, scene_type) 分发。
    scene_types
        支持的场景类型列表，如 ["house"] 或 ["*"]。
    requires
        **依赖的上游 layer 列表**。框架按此注入 StageInputs，只包含声明的
        上游阶段产物。空列表表示只依赖 PipelineInput（如 understand）。
    output_type
        本 Stage 阶段产物的类型（pydantic BaseModel 子类）。框架在 run()
        返回后强校验，不匹配即报错。
    run(inputs)
        执行本阶段，返回 output_type 的实例。

        Stage 内部怎么实现（LLM / 视觉算法 / 求解器的组合、是否迭代）
        不属于契约的一部分——那是各 Stage 按业务场景自由决定的事。
    """

    name: str
    layer: str
    scene_types: list[str]
    requires: list[str]
    output_type: type

    def run(self, inputs: "StageInputs") -> TOut: ...


class StageInputs:
    """按 requires 注入的上游阶段产物（只读）。

    只包含 Stage 显式声明的上游产物；访问未声明或未产出的 layer 会抛
    KeyError —— 依赖必须显式声明，不能靠"碰巧 ctx 里有"。
    """

    def __init__(
        self,
        pipeline_input: "PipelineInput",
        outputs: dict[str, "BaseModel"],
    ) -> None:
        self._pipeline_input = pipeline_input
        self._outputs = dict(outputs)

    @property
    def pipeline_input(self) -> "PipelineInput":
        """原始输入（所有 Stage 都可读）。"""
        return self._pipeline_input

    def get(self, layer: str) -> "BaseModel":
        if layer not in self._outputs:
            raise KeyError(
                f"Stage 未声明依赖 '{layer}'（或该上游尚未产出）；"
                f"可用上游: {sorted(self._outputs)}"
            )
        return self._outputs[layer]

    def has(self, layer: str) -> bool:
        return layer in self._outputs

    # ---- 具名便捷访问（让类型标注生效，避免字符串拼写错误） ----
    @property
    def understand(self):
        from xasset.pipeline.schemas import UnderstandOutput

        out = self.get("understand")
        assert isinstance(out, UnderstandOutput)
        return out

    @property
    def geometry(self):
        from xasset.pipeline.schemas import GeometryOutput

        out = self.get("geometry")
        assert isinstance(out, GeometryOutput)
        return out

    @property
    def layout(self):
        from xasset.pipeline.schemas import LayoutOutput

        out = self.get("layout")
        assert isinstance(out, LayoutOutput)
        return out

    @property
    def surface(self):
        from xasset.pipeline.schemas import SurfaceOutput

        out = self.get("surface")
        assert isinstance(out, SurfaceOutput)
        return out

    @property
    def accessory(self):
        from xasset.pipeline.schemas import AccessoryOutput

        out = self.get("accessory")
        assert isinstance(out, AccessoryOutput)
        return out

    @property
    def stylize(self):
        from xasset.pipeline.schemas import StylizeOutput

        out = self.get("stylize")
        assert isinstance(out, StylizeOutput)
        return out


class StageDependencyMissing(Exception):
    """Stage 声明的上游依赖尚未产出。"""


class StageContractViolation(Exception):
    """Stage 产出的类型与其 output_type 声明不符。"""
