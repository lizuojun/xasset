# xasset/pipeline/stages/understand/interfaces.py
"""understand 阶段的两侧接口 —— 理解侧的可替换实现。

按 Artist 范式，**理解侧技术按场景选型**。这里只定义协议，不绑定具体模型。

- `RegionSegmenter`：图片 → 区域 mask（② 分割）
- `RegionLabeler`：多边形 + 图片 → 区域类型（④ 语义标注）

③ 几何后处理不是接口——它是**约束侧**，必须是确定性的，
实现固定在 `tools/geometry/contour.py`。

设计依据见 docs/understand-vision-route.md。
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from xasset.pipeline.schemas import Polygon


@runtime_checkable
class RegionSegmenter(Protocol):
    """② 分割：从图片提取每个区域的像素 mask。

    这是**理解侧**——具体用 SAM、专用户型图模型还是云 API，由实现决定。
    Artist 只要求：换个实现不影响上下游。
    """

    def segment(
        self,
        image: Any,
        *,
        input_kind: str = "drawing",
    ) -> list["RegionMask"]:
        """返回每个区域的 mask。

        Parameters
        ----------
        image : 图片数据（格式由实现定义，如 numpy array / PIL Image / 路径）
        input_kind : "drawing" | "photo"
            用户选择的输入类型。图纸和实景的分割策略可能不同。
        """
        ...


@runtime_checkable
class RegionLabeler(Protocol):
    """④ 语义标注：给多边形打 region_type 标签。

    这是**理解侧**——语义判断是 LLM 的强项，也可是专用分类器。
    """

    def label(
        self,
        image: Any,
        polygons: list[Polygon],
        *,
        scene_type: str = "house",
    ) -> list["RegionLabelResult"]:
        """给每个多边形返回区域类型与置信度。"""
        ...


class RegionMask:
    """一个区域的像素 mask。

    刻意保持简单：只有 mask 本身 + 位置 + 可选提示。
    """

    def __init__(
        self,
        mask: list[list[bool]],
        *,
        origin_px: tuple[int, int] = (0, 0),
        hint_region_type: str | None = None,
        hint_confidence: float | None = None,
    ) -> None:
        self.mask = mask
        # **重要**：本 mask 左上角在原图中的像素位置。
        # 分割器如果裁过包围盒，必须填这个值，否则多个区域
        # 落地后会全部叠到 (0,0)，无法还原相对位置。
        self.origin_px = origin_px
        self.hint_region_type = hint_region_type
        self.hint_confidence = hint_confidence

    def __repr__(self) -> str:
        h = len(self.mask)
        w = len(self.mask[0]) if h else 0
        return (
            f"RegionMask({h}x{w}, origin={self.origin_px}, "
            f"hint={self.hint_region_type!r})"
        )


class RegionLabelResult:
    """一个区域的语义标注结果。"""

    def __init__(
        self,
        region_type: str,
        *,
        confidence: float = 1.0,
        rationale: str = "",
    ) -> None:
        self.region_type = region_type
        self.confidence = confidence
        self.rationale = rationale

    def __repr__(self) -> str:
        return f"RegionLabelResult({self.region_type!r}, conf={self.confidence:.2f})"


# ── 空实现（占位，让链路能跑通）────────────────────────────────────────

class StubSegmenter:
    """占位分割器：返回空结果。

    用途：在 ② 的选型确定前，让 understand 的骨架能端到端跑通。
    """

    def segment(self, image: Any, *, input_kind: str = "drawing") -> list[RegionMask]:
        return []


class StubLabeler:
    """占位标注器：一律返回 unknown。"""

    def label(
        self,
        image: Any,
        polygons: list[Polygon],
        *,
        scene_type: str = "house",
    ) -> list[RegionLabelResult]:
        return [RegionLabelResult("unknown", confidence=0.0) for _ in polygons]
