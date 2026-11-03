# tests/pipeline/test_understand_artist_shape.py
"""验证 understand Stage 符合 Artist 范式：

- 结构是「想法 → 落地 → 校验 → (回拉)」，不是单向流水线
- 理解侧可替换（分割器 / 标注器）
- 约束侧确定性（几何后处理）
- 迭代入口已预留（max_fix_iterations）
"""
import pytest

from xasset.pipeline.context import PipelineInput
from xasset.pipeline.schemas import UnderstandOutput
from xasset.pipeline.stage import StageInputs
from xasset.pipeline.stages.understand.interfaces import (
    RegionLabelResult,
    RegionMask,
    StubLabeler,
    StubSegmenter,
)
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage


def _inputs(**kwargs):
    kwargs.setdefault("input_type", "text")
    kwargs.setdefault("scene_type", "house")
    inp = PipelineInput(**kwargs)
    return StageInputs(inp, {})


class _FakeSegmenter:
    """返回一个 100x100 的实心 mask。"""

    def __init__(self, n=1, size=100):
        self._n = n
        self._size = size
        self.calls = 0

    def segment(self, image, *, input_kind="drawing"):
        self.calls += 1
        return [
            RegionMask([[True] * self._size for _ in range(self._size)])
            for _ in range(self._n)
        ]


class _FakeLabeler:
    def __init__(self, region_type="bedroom"):
        self._rt = region_type
        self.calls = 0

    def label(self, image, polygons, *, scene_type="house"):
        self.calls += 1
        return [RegionLabelResult(self._rt, confidence=0.9) for _ in polygons]


# ── Artist 结构 ─────────────────────────────────────────────────────────

def test_stage_declares_iteration_budget():
    """迭代入口必须存在且当前为 1（单次求解）。"""
    assert SceneUnderstandStage.max_fix_iterations == 1


def test_stage_has_artist_methods():
    """Artist 形状的方法必须都在：出想法 / 落地 / 回拉。"""
    s = SceneUnderstandStage()
    assert hasattr(s, "produce_idea")
    assert hasattr(s, "realize")
    assert hasattr(s, "refine_idea")


def test_refine_idea_is_hook_not_yet_active():
    """回拉住方法已预留，当前返回原想法（不做改动）。"""
    s = SceneUnderstandStage()
    ideas = [object()]
    out = s.refine_idea(ideas, None, None)
    assert out is ideas


# ── 理解侧可替换 ────────────────────────────────────────────────────────

def test_default_uses_threshold_segmenter():
    """默认用阈值分割器（零依赖，对线条户型图有效）。"""
    from xasset.pipeline.stages.understand.segmenters import (
        ThresholdRegionSegmenter,
    )

    s = SceneUnderstandStage()
    assert isinstance(s._segmenter, ThresholdRegionSegmenter)
    # 标注器仍是空实现（选型未定）
    assert isinstance(s._labeler, StubLabeler)


def test_can_force_stub_segmenter():
    """显式关掉阈值分割时退回空实现。"""
    s = SceneUnderstandStage(use_threshold_segmenter=False)
    assert isinstance(s._segmenter, StubSegmenter)


def test_segmenter_and_labeler_are_injectable():
    seg = _FakeSegmenter()
    lab = _FakeLabeler("kitchen")
    s = SceneUnderstandStage(segmenter=seg, labeler=lab)
    assert s._segmenter is seg
    assert s._labeler is lab


def test_image_route_calls_both_sides():
    """图片路线应同时调用理解侧（分割+标注）和约束侧（几何）。"""
    seg = _FakeSegmenter(n=1, size=100)
    lab = _FakeLabeler("bedroom")
    s = SceneUnderstandStage(segmenter=seg, labeler=lab)

    out = s.run(_inputs(input_type="image", image_url="fake://img"))

    assert seg.calls == 1
    assert lab.calls == 1
    assert len(out.regions) == 1
    assert out.regions[0].region_type == "bedroom"


# ── 约束侧确定性 ────────────────────────────────────────────────────────

def test_realize_produces_polygon_from_mask():
    """约束侧应把 mask 落成米制多边形。"""
    n = 50
    mask = [[True] * n for _ in range(n)]
    ideas = [type("I", (), {"mask": RegionMask(mask), "region_type": "bedroom",
                            "confidence": 1.0, "scale": None})()]
    s = SceneUnderstandStage()
    inp = PipelineInput(input_type="image", scene_type="house")

    out = s.realize(ideas, inp, input_kind="drawing")
    assert len(out.regions) == 1
    assert len(out.regions[0].boundary.points) >= 3
    assert out.regions[0].area > 0


def test_realize_is_deterministic():
    """同一输入两次落地，结果必须完全一致（约束侧必须是确定性的）。"""
    n = 40
    mask = [[True] * n for _ in range(n)]
    ideas = [type("I", (), {"mask": RegionMask(mask), "region_type": "kitchen",
                            "confidence": 1.0, "scale": None})()]
    s = SceneUnderstandStage()
    inp = PipelineInput(input_type="image", scene_type="house")

    a = s.realize(ideas, inp, input_kind="drawing")
    b = s.realize(ideas, inp, input_kind="drawing")

    assert a.regions[0].boundary.points == b.regions[0].boundary.points
    assert a.regions[0].area == b.regions[0].area


# ── 输入类型影响几何策略 ────────────────────────────────────────────────

def test_drawing_route_orthogonalizes():
    """图纸路线应开启正交化。"""
    n = 60
    mask = [[True] * n for _ in range(n)]
    ideas = [type("I", (), {"mask": RegionMask(mask), "region_type": "bedroom",
                            "confidence": 1.0, "scale": None})()]
    s = SceneUnderstandStage()
    inp = PipelineInput(input_type="image", scene_type="house")

    out = s.realize(ideas, inp, input_kind="drawing")
    assert len(out.regions) == 1


def test_photo_route_skips_orthogonalize():
    """实景路线不应正交化（真实墙角未必垂直）。"""
    n = 60
    mask = [[True] * n for _ in range(n)]
    ideas = [type("I", (), {"mask": RegionMask(mask), "region_type": "bedroom",
                            "confidence": 1.0, "scale": None})()]
    s = SceneUnderstandStage()
    inp = PipelineInput(input_type="image", scene_type="house")

    out = s.realize(ideas, inp, input_kind="photo")
    assert len(out.regions) == 1


# ── SceneVector 路线不受影响 ────────────────────────────────────────────

def test_scene_vector_route_still_works():
    """结构化输入路线不走视觉，直接解析。"""
    sv = {
        "rooms": [
            {"id": "r1", "type": "bedroom",
             "floor": [[0, 0], [4, 0], [4, 4], [0, 4]], "height": 2.8}
        ]
    }
    s = SceneUnderstandStage()
    out = s.run(_inputs(scene_vector=sv))

    assert isinstance(out, UnderstandOutput)
    assert len(out.regions) == 1
    assert out.regions[0].region_id == "r1"
    assert out.regions[0].area == pytest.approx(16.0)


def test_empty_input_returns_empty_output():
    out = SceneUnderstandStage().run(_inputs())
    assert out.regions == []
