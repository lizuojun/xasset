# xasset/pipeline/stages/understand/segmenters.py
"""分割器实现 —— 理解侧的具体技术（可替换）。

本文件目前提供一个**零依赖**的实现：`ThresholdRegionSegmenter`。

## 为什么先做阈值分割

1. **零成本**：不需要下载模型、不需要 torch
2. **对户型图有效**：这类图是"黑线墙 + 白底空间"，阈值分割天然适用
3. **把分割隔离成唯一变量**：将来换 SAM 时对照清晰

## 核心思路（关键）

**不要对黑色线条做连通域** —— 那是墙体，不是房间。
**要对白色空间做连通域** —— 每一块被墙围起来的白色区域就是一个房间。

```
原始图 → 灰度 → 二值化（黑线=前景）
                        ↓
              取反（白空间=前景）
                        ↓
              连通域标记（4/8 邻域）
                        ↓
              过滤掉太小的区域（噪点/文字）
                        ↓
              每个连通域 = 一个 RegionMask
```
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path

from xasset.pipeline.stages.understand.interfaces import RegionMask


@dataclass
class SegmenterConfig:
    """阈值分割器参数。"""

    # 灰度阈值：低于此值视为"墙/线"（深色），高于视为"空间"（浅色）
    dark_threshold: int = 200

    # 最小区域面积（像素）。低于此值视为噪点/文字，丢弃。
    # 户型图里文字标注会形成小块，需要过滤。
    min_area_px: int = 2000

    # 最大区域占比。超过此值视为"图外空白背景"，丢弃。
    #
    # 为什么必须过滤：户型图外围通常是大片白色空白，
    # 它会被当成一个巨大的连通域。实测 842x569 的图上，
    # 这块空白占 30%+，必须排除才能只留下真正的房间。
    max_area_ratio: float = 0.25

    # 是否丢弃"贴着图像边缘"的连通域。
    #
    # 这是比面积占比更稳健的判据：
    # - 图外空白背景一定贴着四条边
    # - 房间是被墙围住的，通常不贴边
    #
    # 默认开启。若某些图里房间确实贴边被误删，可关闭并改用面积占比过滤。
    drop_edge_touching: bool = True

    # 连通域邻域：4 或 8
    connectivity: int = 4

    # 是否从文件读取（否则从传入的 image 读）
    image_path_hint: str | None = None


class ThresholdRegionSegmenter:
    """基于阈值 + 连通域的分割器 —— 适用于线条型户型图。

    这是 `RegionSegmenter` 协议的一个**具体实现**。
    换成 SAM 或其它模型时，只需实现同样接口，Stage 代码不用改。
    """

    def __init__(self, config: SegmenterConfig | None = None) -> None:
        self._config = config or SegmenterConfig()

    def segment(
        self,
        image,
        *,
        input_kind: str = "drawing",
    ) -> list[RegionMask]:
        """对图片做阈值分割，返回每块封闭空间为一个 RegionMask。"""
        gray = self._load_gray(image)
        if not gray:
            return []

        h = len(gray)
        w = len(gray[0])
        total = h * w
        cfg = self._config

        # 1. 二值化：浅色 = 空间（True）
        is_space = [
            [gray[r][c] > cfg.dark_threshold for c in range(w)]
            for r in range(h)
        ]

        # 2. 连通域标记
        visited = [[False] * w for _ in range(h)]
        regions: list[RegionMask] = []

        for r0 in range(h):
            for c0 in range(w):
                if visited[r0][c0] or not is_space[r0][c0]:
                    continue
                comp = self._flood_fill(is_space, visited, r0, c0, w, h)
                area = len(comp)

                # 3. 过滤噪点
                if area < cfg.min_area_px:
                    continue
                # 4. 过滤整图背景（面积占比）
                if area > total * cfg.max_area_ratio:
                    continue
                # 5. 过滤贴边连通域（图外空白背景）
                if cfg.drop_edge_touching and _touches_edge(comp, w, h):
                    continue

                # 6. 生成紧凑的 mask（只保留该连通域的包围盒，省内存）
                #    同时记录包围盒在原图中的位置 —— 否则多个区域落地后
                #    会全部叠到 (0,0)，无法还原相对位置。
                bbox_mask, bbox_origin = self._to_bbox_mask(comp)
                regions.append(RegionMask(bbox_mask, origin_px=bbox_origin))

        # 6. 按面积从大到小排（大区域通常是主要房间）
        regions.sort(key=lambda m: -_count_true(m.mask))
        return regions

    # ── 内部 ────────────────────────────────────────────────

    def _load_gray(self, image) -> list[list[int]]:
        """取得灰度矩阵。image 可以是路径字符串。"""
        path = None
        if isinstance(image, (str, Path)):
            path = str(image)
        elif self._config.image_path_hint:
            path = self._config.image_path_hint

        if path is None:
            # 没有路径，说明 image 本身可能是灰度矩阵
            if isinstance(image, list) and image and isinstance(image[0], list):
                return image
            return []

        from xasset.tools.io import load_grayscale
        return load_grayscale(path)

    def _flood_fill(
        self,
        is_space: list[list[bool]],
        visited: list[list[bool]],
        r0: int,
        c0: int,
        w: int,
        h: int,
    ) -> list[tuple[int, int]]:
        """BFS 连通域标记，返回该连通域的所有像素。"""
        cfg = self._config
        if cfg.connectivity == 8:
            steps = [(0, 1), (1, 0), (0, -1), (-1, 0),
                     (1, 1), (1, -1), (-1, 1), (-1, -1)]
        else:
            steps = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        comp: list[tuple[int, int]] = []
        q = deque([(r0, c0)])
        visited[r0][c0] = True

        while q:
            r, c = q.popleft()
            comp.append((r, c))
            for dr, dc in steps:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    if not visited[nr][nc] and is_space[nr][nc]:
                        visited[nr][nc] = True
                        q.append((nr, nc))
        return comp

    @staticmethod
    def _to_bbox_mask(
        comp: list[tuple[int, int]],
    ) -> tuple[list[list[bool]], tuple[int, int]]:
        """把连通域裁到包围盒，生成紧凑 mask。

        为什么裁包围盒：整图大小的 mask 会浪费几十倍内存，
        而且轮廓提取只需要包围盒范围内的信息。

        Returns
        -------
        (mask, origin_px)
            origin_px 是包围盒左上角在**原图**中的坐标 (row0, col0)。
            调用方必须把它传下去，否则区域位置信息会丢失。
        """
        rs = [p[0] for p in comp]
        cs = [p[1] for p in comp]
        r0, r1 = min(rs), max(rs)
        c0, c1 = min(cs), max(cs)

        hh = r1 - r0 + 1
        ww = c1 - c0 + 1
        mask = [[False] * ww for _ in range(hh)]
        for r, c in comp:
            mask[r - r0][c - c0] = True
        return mask, (r0, c0)


def _count_true(mask: list[list[bool]]) -> int:
    return sum(1 for row in mask for v in row if v)


def _touches_edge(comp: list[tuple[int, int]], w: int, h: int, margin: int = 1) -> bool:
    """连通域是否贴着图像边缘。

    判据：只要有任一像素落在外圈 margin 像素内，就算贴边。

    为什么用这个判据过滤背景：
    - 图外空白必然贴边
    - 房间被墙围住，墙本身占了边界，所以房间不贴边
    """
    for r, c in comp:
        if r < margin or c < margin or r >= h - margin or c >= w - margin:
            return True
    return False
