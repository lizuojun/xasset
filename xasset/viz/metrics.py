# xasset/viz/metrics.py
"""轮廓精度量化指标 —— 光看"像不像"不够，要有数值。

用途：验证 understand 的识别精度。有 ground truth 时算 IoU。

为什么放在 viz/：
- 它是"核验"的一部分，与可视化同属"看看结果对不对"
- 不是主链路算法（不参与生成）

未来若 CPU 密集度上升，可考虑移到 tools/metrics/。
"""
from __future__ import annotations


def compute_polygon_iou(
    poly_a: list[tuple[float, float]],
    poly_b: list[tuple[float, float]],
) -> float:
    """两个多边形的 IoU（交并比）。

    **当前实现是轴对齐包围盒（AABB）近似**，不是精确多边形求交。

    为什么先用近似：
    - 精确多边形布尔运算需要 shapely 依赖，与"零外部依赖"原则冲突
    - 对"形状大致对不对"的判断，AABB IoU 已经够用
    - 后续若需要精确值，可引入 shapely 作为可选依赖

    Returns
    -------
    float
        0.0 ~ 1.0。0 = 完全不重叠，1 = 完全一致。
    """
    if len(poly_a) < 3 or len(poly_b) < 3:
        return 0.0

    def aabb(pts):
        xs = [p[0] for p in pts]
        zs = [p[1] for p in pts]
        return min(xs), min(zs), max(xs), max(zs)

    ax0, az0, ax1, az1 = aabb(poly_a)
    bx0, bz0, bx1, bz1 = aabb(poly_b)

    ix0, iz0 = max(ax0, bx0), max(az0, bz0)
    ix1, iz1 = min(ax1, bx1), min(az1, bz1)

    inter = max(0.0, ix1 - ix0) * max(0.0, iz1 - iz0)
    area_a = (ax1 - ax0) * (az1 - az0)
    area_b = (bx1 - bx0) * (bz1 - bz0)
    union = area_a + area_b - inter

    if union <= 0:
        return 0.0
    return inter / union


def compute_iou(
    predicted: list,
    ground_truth: list,
    *,
    match_by: str = "region_id",
) -> dict[str, float]:
    """批量计算区域 IoU。

    Parameters
    ----------
    predicted : SceneRegion 列表（识别结果）
    ground_truth : SceneRegion 列表（真值）
    match_by : 匹配依据，"region_id" 或 "region_type"

    Returns
    -------
    dict
        {区域标识: IoU 值}。未匹配到的记为 0.0。
    """
    def key(r):
        return getattr(r, match_by, None) or getattr(r, "region_id", "")

    gt_map = {key(r): r for r in ground_truth}
    result: dict[str, float] = {}

    for pred in predicted:
        k = key(pred)
        gt = gt_map.get(k)
        if gt is None:
            result[k] = 0.0
            continue
        result[k] = compute_polygon_iou(
            list(pred.boundary.points),
            list(gt.boundary.points),
        )

    return result


def mean_iou(iou_dict: dict[str, float]) -> float:
    """平均 IoU。"""
    if not iou_dict:
        return 0.0
    return sum(iou_dict.values()) / len(iou_dict)
