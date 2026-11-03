# tests/tools/test_image_io.py
"""图片 I/O 测试。"""
import pytest

from xasset.tools.io import (
    image_to_mask,
    load_grayscale,
    load_image,
    mask_stats,
)


@pytest.fixture
def sample_image(tmp_path):
    from PIL import Image, ImageDraw

    p = tmp_path / "img.png"
    im = Image.new("RGB", (100, 80), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([20, 20, 60, 60], fill="black")
    im.save(p)
    return p


def test_load_image_dimensions(sample_image):
    img = load_image(sample_image)
    assert img.width == 100
    assert img.height == 80
    assert img.size == (100, 80)


def test_load_image_rgb_values(sample_image):
    img = load_image(sample_image)
    # 左上角是白色
    assert img.rgb[0][0] == (255, 255, 255)
    # 中心是黑色
    assert img.rgb[40][40] == (0, 0, 0)


def test_load_grayscale(sample_image):
    g = load_grayscale(sample_image)
    assert len(g) == 80
    assert len(g[0]) == 100
    assert g[0][0] == 255      # 白
    assert g[40][40] == 0      # 黑


def test_image_to_mask_finds_dark_area(sample_image):
    """阈值化：暗区（黑方块）应被识别为 mask。"""
    mask = image_to_mask(sample_image, threshold=128, invert=True)
    assert mask[40][40] is True      # 方块内部
    assert mask[0][0] is False       # 白色背景


def test_image_to_mask_invert_false(sample_image):
    """不反转时，白色区域为 True。"""
    mask = image_to_mask(sample_image, threshold=128, invert=False)
    assert mask[0][0] is True
    assert mask[40][40] is False


def test_mask_stats(sample_image):
    mask = image_to_mask(sample_image, threshold=128, invert=True)
    s = mask_stats(mask)
    assert s["width"] == 100
    assert s["height"] == 80
    assert s["pixels_on"] > 0
    assert 0.0 < s["ratio"] < 1.0
