# xasset/llm/provider.py
"""LLMProvider 抽象接口。

算法全面重做后，每个 Stage 内部的算法不再手写规则逻辑，而是走统一的
LLM 编排接口（见 research/unified-scene-pipeline/README.md 3.4 节）：

    该阶段输入数据 + 用户提示词 + 硬约束集
              ↓  LLM
      阶段输出（schema 固定、语义明确）
              ↓  约束校验闸门（强制）

本文件只定义 LLM 的抽象能力边界，不绑定任何具体模型 / 平台（底座未定，
先留可替换的 Provider 抽象）。具体实现（内部模型 / 混元 / 补天等）后续
各自继承本接口。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMRequest:
    """一次 LLM 编排调用的输入。

    Parameters
    ----------
    stage_key:
        阶段标识（对应四阶段主线：scene_understand / boundary_features /
        group_layout / scene_generation）。
    prompt:
        已经拼接好的提示词（含阶段硬约束集的引导性描述）。
    constraints:
        该阶段的硬约束集结构（用于函数调用/结构化输出时约束 schema，
        也用于校验闸门重放）。具体字段语义由各阶段自行定义。
    schema:
        期望 LLM 返回的结构化输出 schema 描述（JSON Schema 或等价物），
        保证输出"语义明确、可编程"。
    context:
        补充上下文（上游阶段产物、资产候选库摘要等）。
    """

    stage_key: str
    prompt: str
    constraints: dict = field(default_factory=dict)
    schema: dict | None = None
    context: dict = field(default_factory=dict)


@dataclass
class LLMResponse:
    """一次 LLM 编排调用的结构化输出。

    content:
        结构化产物（已按 schema 约束解析为 dict / 对象）。
        若 LLM 返回非法结构，content 为 None 并由 error 携带原因。
    rejected:
        结构校验（schema 层）是否拒绝。
    error:
        拒绝 / 失败原因。
    """

    content: Any | None = None
    rejected: bool = False
    error: str | None = None


class LLMProvider(ABC):
    """LLM 底座抽象。可替换，不绑定具体模型 / 平台。"""

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """执行一次 LLM 编排调用，返回结构化输出。

        实现方负责：拼接 prompt、执行 model 调用、约束结构化输出（JSON
        schema / function calling / constrained decoding）、返回解析后的
        结构化产物。不负责校验闸门（校验是跨阶段的通用能力，见 tools/
        constraint）；但必须保证返回的 content 在 schema 层合法。
        """
        ...


class StubLLMProvider(LLMProvider):
    """占位 LLM Provider：返回标识性空产物，保证管线骨架可跑通。

    算法重做过程中，各 Stage 尚未接入真实 LLM 前的过渡实现。
    """

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content={"stage_key": request.stage_key, "status": "stub"},
            rejected=False,
        )
