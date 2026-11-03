# xasset/tools/geometry/contour.py
"""轮廓处理 —— 从 mask 提取并规整出多边形轮廓。

定位：**understand 视觉路线的第 ③ 步（几何后处理）**。
这一步完全确定性、不依赖任何外部模型，是整条视觉路线里唯一现在就能交付的部分。

设计依据见 docs/understand-vision-route.md。

处理链：
    mask（像素布尔矩阵）
      ↓ 轮廓跟踪（Moore 邻域）
    像素级轮廓点
      ↓ 尺度换算（像素 → 米）
    米制多边形
      ↓ 多边形简化（Douglas-Peucker）
      ↓ 正交化（可选，图纸场景墙都是直角）
      ↓ CCW 绕向统一
    Polygon 契约

与 tools/geometry/normalize.py 的关系：
- normalize 处理的是"已有 SceneVector"的规整
- 本模块处理的是"从像素 mask 生成轮廓"，是更上游的一步
- 复用其中的简化与绕向逻辑思路
"""
from __future__ import annotations

import math
from dataclasses import dataclass

Vec2 = tuple[float, float]


# ── 1. 轮廓跟踪 ─────────────────────────────────────────────────────────

def trace_contour(mask: list[list[bool]]) -> list[tuple[int, int]]:
    """从二值 mask 提取最外层轮廓（Moore 邻域跟踪）。

    Parameters
    ----------
    mask : list[list[bool]]
        二维布尔矩阵，True 表示属于该区域。

    Returns
    -------
    list[tuple[int, int]]
        像素坐标轮廓点序列（(row, col)），按逆时针或顺时针排列。
        若 mask 为空，返回空列表。
    """
    h = len(mask)
    if h == 0:
        return []
    w = len(mask[0])

    # 找到第一个前景像素作为起点（自上而下、自左而右扫描）
    start = None
    for r in range(h):
        for c in range(w):
            if mask[r][c]:
                start = (r, c)
                break
        if start:
            break
    if start is None:
        return []

    # Moore 邻域顺序：从正上方开始顺时针
    neighbors = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

    def get(r, c):
        if 0 <= r < h and 0 <= c < w:
            return mask[r][c]
        return False

    contour = [start]
    current = start
    # 起始回溯方向：从左侧进入
    prev_dir = 6   # (0,-1)

    for _ in range(h * w * 4):   # 防死循环上限
        found = False
        # 从回溯方向的下一个方向开始找
        for i in range(8):
            d = (prev_dir + 1 + i) % 8
            dr, dc = neighbors[d]
            nr, nc = current[0] + dr, current[1] + dc
            if get(nr, nc):
                contour.append((nr, nc))
                prev_dir = (d + 4) % 8    # 回溯方向设为来的反方向
                current = (nr, nc)
                found = True
                break
        if not found:
            break
        if current == start and len(contour) > 2:
            contour.pop()    # 去掉重复的起点
            break

    # 去掉相邻重复点
    dedup: list[tuple[int, int]] = []
    for p in contour:
        if not dedup or dedup[-1] != p:
            dedup.append(p)
    return dedup


# ── 2. 尺度换算 ─────────────────────────────────────────────────────────

@dataclass
class ScaleInfo:
    """像素 → 米的换算关系。"""

    pixels_per_meter: float
    source: str          # 换算依据："door_width" | "area_prior" | "explicit"

    def to_meters(self, px: tuple[float, float], origin: tuple[float, float]) -> Vec2:
        """像素坐标 → 米制坐标。

        索引约定：
            px / origin 都是 (row, col)，row 向下增长、col 向右增长。

        转换规则：
            X = (col - col0) / ppm     ← 水平轴，方向不变
            Z = (row0 - row) / ppm     ← **Y 必须翻转**

        为什么 Z 要翻转：
            图像坐标里 row 向下增长，而场景坐标里 Z 向上增长。
            不翻转的话所有 Z 都是负数，轮廓会跑到图片下方外面去。
        """
        return (
            (px[1] - origin[1]) / self.pixels_per_meter,
            (origin[0] - px[0]) / self.pixels_per_meter,
        )


def infer_scale_from_area(
    px_area: float,
    expected_area_m2: tuple[float, float],
) -> ScaleInfo:
    """按房间类型的典型面积反推尺度。

    用途：当图片没有任何尺寸参照时的兜底手段。

    Parameters
    ----------
    px_area : float
        该区域在图片上的像素面积。
    expected_area_m2 : tuple[float, float]
        该 region_type 的典型面积区间（见 data/house/rules.json）。

    Returns
    -------
    ScaleInfo
        以典型面积区间中位数反推的像素/米比例。

    Notes
    -----
    这是**粗略估计**，误差可能很大（同一类型房间面积差异可达数倍）。
    仅在没有更好的尺度来源时使用。
    """
    if px_area <= 0:
        raise ValueError("像素面积必须为正")
    lo, hi = expected_area_m2
    mid_area = (lo + hi) / 2.0
    ppm = math.sqrt(px_area / mid_area)
    return ScaleInfo(pixels_per_meter=ppm, source="area_prior")


def infer_scale_from_reference(
    px_length: float,
    real_length_m: float,
    source: str = "explicit",
) -> ScaleInfo:
    """按已知参照物（如标准门宽）反推尺度。

    这是**更可靠**的方式：找一个已知实际尺寸的要素（门宽 0.9m、地砖 0.6m 等）。

    Parameters
    ----------
    px_length : float
        该参照物在图片上的像素长度。
    real_length_m : float
        该参照物的真实长度（米）。
    """
    if px_length <= 0 or real_length_m <= 0:
        raise ValueError("像素长度与真实长度都必须为正")
    return ScaleInfo(pixels_per_meter=px_length / real_length_m, source=source)


def pixels_to_polygon(
    contour: list[tuple[int, int]],
    scale: ScaleInfo,
    origin: tuple[float, float] | None = None,
) -> list[Vec2]:
    """把像素轮廓转换成米制多边形（以左上角为原点，Y 向下转 Z 向上）。"""
    if not contour:
        return []
    if origin is None:
        origin = contour[0]
    return [scale.to_meters(p, origin) for p in contour]


# ── 3. 多边形简化 ───────────────────────────────────────────────────────

def simplify_polygon(points: list[Vec2], tolerance_m: float = 0.05) -> list[Vec2]:
    """Douglas-Peucker 简化（闭合多边形版本）。

    去掉几乎共线的点，保留形状特征。
    """
    if len(points) <= 3:
        return list(points)

    # 闭合多边形：先找距起点最远的点，分成两段分别简化
    p0 = points[0]
    far_idx = max(range(1, len(points)),
                  key=lambda i: math.dist(points[i], p0))

    seg1 = _douglas_peucker(points[:far_idx + 1], tolerance_m)
    seg2 = _douglas_peucker(points[far_idx:] + [p0], tolerance_m)

    result = seg1[:-1] + seg2[:-1]
    return result if len(result) >= 3 else list(points)


def _douglas_peucker(points: list[Vec2], tol: float) -> list[Vec2]:
    """标准 Douglas-Peucker（开放折线）。"""
    if len(points) <= 2:
        return list(points)

    def perp_dist(p, a, b):
        ax, az = a
        bx, bz = b
        px, pz = p
        dx, dz = bx - ax, bz - az
        seg = math.hypot(dx, dz)
        if seg < 1e-12:
            return math.dist(p, a)
        return abs(dx * (az - pz) - dz * (ax - px)) / seg

    dmax, idx = 0.0, 0
    for i in range(1, len(points) - 1):
        d = perp_dist(points[i], points[0], points[-1])
        if d > dmax:
            dmax, idx = d, i

    if dmax > tol:
        left = _douglas_peucker(points[:idx + 1], tol)
        right = _douglas_peucker(points[idx:], tol)
        return left[:-1] + right
    return [points[0], points[-1]]


# ── 4. 正交化 ───────────────────────────────────────────────────────────

def orthogonalize(
    points: list[Vec2],
    angle_tolerance_deg: float = 15.0,
    axis: str = "auto",
) -> list[Vec2]:
    """把接近水平/垂直的边吸附到正轴向。

    用途：**图纸/户型图场景**。这类图的墙基本是直角，分割模型给出的
    边界有轻微倾斜时，正交化能显著改善质量。

    Parameters
    ----------
    points : 输入多边形
    angle_tolerance_deg : 与轴向夹角在这个范围内的边会被吸附
    axis : "auto" 用最小外接矩形的方向对齐；"x" 直接对齐坐标轴

    Returns
    -------
    正交化后的多边形。

    Notes
    -----
    **实景照片场景不应调用本函数**——真实墙角未必垂直，强行正交化会失真。
    """
    if len(points) < 3:
        return list(points)

    n = len(points)
    result = list(points)

    for i in range(n):
        a = result[i]
        b = result[(i + 1) % n]
        dx = b[0] - a[0]
        dz = b[1] - a[1]
        length = math.hypot(dx, dz)
        if length < 1e-9:
            continue

        angle = math.degrees(math.atan2(dz, dx)) % 180.0

        # 判断接近水平（0°/180°）还是垂直（90°）
        if angle < angle_tolerance_deg or angle > 180 - angle_tolerance_deg:
            # 吸附为水平：保持 z 不变
            result[(i + 1) % n] = (b[0], a[1])
        elif abs(angle - 90) < angle_tolerance_deg:
            # 吸附为垂直：保持 x 不变
            result[(i + 1) % n] = (a[0], b[1])

    return result


# ── 5. 绕向统一 ─────────────────────────────────────────────────────────

def ensure_ccw(points: list[Vec2]) -> list[Vec2]:
    """确保多边形为逆时针（CCW）。"""
    if len(points) < 3:
        return list(points)
    area2 = 0.0
    n = len(points)
    for i in range(n):
        x1, z1 = points[i]
        x2, z2 = points[(i + 1) % n]
        area2 += x1 * z2 - x2 * z1
    return list(points) if area2 > 0 else list(reversed(points))


# ── 6. 完整处理链 ───────────────────────────────────────────────────────

@dataclass
class ContourResult:
    """一次轮廓提取的结果。"""

    polygon: list[Vec2]
    scale: ScaleInfo | None = None
    simplified_count: int = 0
    orthogonalized: bool = False

    @property
    def area_m2(self) -> float:
        """多边形面积（m²）。"""
        n = len(self.polygon)
        if n < 3:
            return 0.0
        s = 0.0
        for i in range(n):
            x1, z1 = self.polygon[i]
            x2, z2 = self.polygon[(i + 1) % n]
            s += x1 * z2 - x2 * z1
        return abs(s) / 2.0


def mask_to_polygon(
    mask: list[list[bool]],
    scale: ScaleInfo,
    *,
    simplify_tolerance_m: float = 0.05,
    orthogonalize_result: bool = False,
    angle_tolerance_deg: float = 15.0,
    origin_px: tuple[float, float] | None = None,
    mask_offset_px: tuple[int, int] = (0, 0),
) -> ContourResult:
    """完整处理链：mask → 米制多边形。

    Parameters
    ----------
    mask : 二值 mask（可能只是原图中某区域裁出来的包围盒）
    scale : 像素→米换算
    simplify_tolerance_m : 简化容差（米）
    orthogonalize_result : 是否正交化（**图纸场景 True，实景照片 False**）
    origin_px : 米制坐标系原点（原图像素坐标）。

        多个区域要落在同一坐标系里时，必须传**同一个** origin
        （通常是整图左下角，即 (image_height, 0)）。

        传 None 表示以 mask 自身第一个轮廓点为原点 —— 只适合单区域。
    mask_offset_px : mask 左上角在原图中的像素偏移 (row0, col0)。

        若 mask 是裁剪过的包围盒，必须传这个值，否则区域位置会错。
    """
    contour = trace_contour(mask)
    if not contour:
        return ContourResult(polygon=[])

    # 把裁剪偏移加回去，还原成原图坐标
    if mask_offset_px != (0, 0):
        dr, dc = mask_offset_px
        contour = [(r + dr, c + dc) for r, c in contour]

    raw = pixels_to_polygon(contour, scale, origin=origin_px)
    simplified = simplify_polygon(raw, simplify_tolerance_m)

    did_ortho = False
    if orthogonalize_result:
        simplified = orthogonalize(simplified, angle_tolerance_deg)
        simplified = simplify_polygon(simplified, simplify_tolerance_m)
        did_ortho = True

    final = ensure_ccw(simplified)

    return ContourResult(
        polygon=final,
        scale=scale,
        simplified_count=len(raw) - len(final),
        orthogonalized=did_ortho,
    )
