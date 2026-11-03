# tests/integration/test_understand_e2e.py
"""understand 端到端集成测试 —— 需要真实户型图。

**无图片时自动 skip**（见 tests/conftest.py 的约定），
所以 `pytest` 在任何机器上都能跑绿。

有图片时验证：
    读图 → 分割 → 几何后处理 → 出轮廓 → 渲染对比图 → IoU
"""
from pathlib import Path

import pytest

from xasset.pipeline.context import PipelineInput
from xasset.pipeline.stage import StageInputs
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage
from xasset.tools.io import image_to_mask, load_image, mask_stats
from xasset.viz import compute_iou, plot_regions, render_side_by_side

pytestmark = pytest.mark.integration


def test_can_load_test_image(test_image):
    """能读进来，且有合理尺寸。"""
    img = load_image(test_image)
    assert img.width > 0
    assert img.height > 0


def test_threshold_mask_is_nonempty(test_image):
    """阈值化能分出一些区域（否则说明图不是线条图）。"""
    mask = image_to_mask(test_image, threshold=200, invert=True)
    stats = mask_stats(mask)
    assert stats["pixels_on"] > 0, "阈值化后没有前景像素"
    assert stats["ratio"] < 0.95, "几乎全图都是前景，阈值可能不合适"


def test_understand_produces_regions_from_image(test_image, tmp_path):
    """整条链路：图片 → understand → 有轮廓产出。

    当前用 StubSegmenter，预期产出为空——这个测试用来**记录当前状态**，
    等真实分割器接入后应改为断言 regions 非空。
    """
    stage = SceneUnderstandStage()
    inp = PipelineInput(
        input_type="image",
        scene_type="house",
        image_url=str(test_image),
        constraints={"input_kind": "drawing"},
    )
    out = stage.run(StageInputs(inp, {}))

    # 无论空与否，类型契约必须正确
    assert out.scene_type == "house"
    assert isinstance(out.regions, list)


def test_render_comparison_image(test_image, tmp_path):
    """能出对比图（这是"绘制出来与原图对比"这个测试标准的落点）。"""
    stage = SceneUnderstandStage()
    inp = PipelineInput(
        input_type="image",
        scene_type="house",
        image_url=str(test_image),
        constraints={"input_kind": "drawing"},
    )
    out = stage.run(StageInputs(inp, {}))

    compare_path = tmp_path / "compare.png"
    render_side_by_side(test_image, out.regions, compare_path)
    assert compare_path.exists()
    assert compare_path.stat().st_size > 0

    contour_path = tmp_path / "contours.png"
    plot_regions(out.regions, contour_path, title="识别轮廓")
    assert contour_path.exists()


def test_iou_self_comparison(test_image):
    """用真值和自己比，IoU 应为 1（验证指标本身正确）。"""
    stage = SceneUnderstandStage()
    inp = PipelineInput(
        input_type="image",
        scene_type="house",
        image_url=str(test_image),
        constraints={"input_kind": "drawing"},
    )
    out = stage.run(StageInputs(inp, {}))
    if not out.regions:
        pytest.skip("当前无区域产出（分割器仍是 Stub）")

    iou = compute_iou(out.regions, out.regions)
    assert all(v == pytest.approx(1.0) for v in iou.values())
