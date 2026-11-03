# xasset/tools/io/image.py
"""图片读取与基础处理。

定位：**I/O 工具**，不属于算法，所以放 tools/io/ 而非 tools/geometry/。

依赖：pillow（已在环境中，12.2.0）
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoadedImage:
    """已加载的图片。"""

    width: int
    height: int
    rgb: list[list[tuple[int, int, int]]]   # [row][col] -> (r,g,b)

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)


def load_image(path: str | Path) -> LoadedImage:
    """读取图片为纯 Python 结构。

    为什么不用 numpy 直接返回：
    - 保持与项目其它模块一致（多为纯 Python 结构）
    - 便于测试与序列化
    - 需要性能时可在调用处转 numpy
    """
    from PIL import Image

    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        px = im.load()
        rgb = [[px[c, r] for c in range(w)] for r in range(h)]
    return LoadedImage(width=w, height=h, rgb=rgb)


def load_grayscale(path: str | Path) -> list[list[int]]:
    """读取为灰度矩阵（0~255）。"""
    from PIL import Image

    with Image.open(path) as im:
        im = im.convert("L")
        w, h = im.size
        px = im.load()
        return [[px[c, r] for c in range(w)] for r in range(h)]


def image_to_mask(
    path: str | Path,
    *,
    threshold: int = 128,
    invert: bool = False,
) -> list[list[bool]]:
    """按灰度阈值二值化，得到 mask。

    用途：**最简单的分割**——对已经二值化的图纸（黑线白底或白线黑底）
    直接阈值化就能拿到"非背景"区域。

    对复杂图片（实景照片）不适用，需要真实分割模型。
    """
    gray = load_grayscale(path)
    mask = []
    for row in gray:
        if invert:
            mask.append([v < threshold for v in row])
        else:
            mask.append([v >= threshold for v in row])
    return mask


def mask_stats(mask: list[list[bool]]) -> dict:
    """mask 的统计信息（调试用）。"""
    h = len(mask)
    w = len(mask[0]) if h else 0
    total = h * w
    on = sum(1 for row in mask for v in row if v)
    return {
        "width": w,
        "height": h,
        "pixels_on": on,
        "total": total,
        "ratio": (on / total) if total else 0.0,
    }
