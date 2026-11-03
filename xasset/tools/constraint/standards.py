# xasset/tools/constraint/standards.py
"""硬约束的规范常数 —— 每个数字都能追溯到规范条款。

出处详见 docs/constraint-standard-references.md。
编号（H-01 等）与该文档的表格一一对应。

**重要**：这些条款号是依据记忆整理的，使用前务必核对规范原文。
"""
from __future__ import annotations

# ── 门洞与通行宽度 ──────────────────────────────────────────────────────

# H-01: 户（套）门洞口宽度 ≥ 0.90m（《住宅设计规范》GB 50096-2011 §5.8.7）
DOOR_WIDTH_ENTRANCE_MIN_M = 0.90

# H-02: 卧室门洞口宽度 ≥ 0.90m（GB 50096-2011 §5.8.7）
DOOR_WIDTH_BEDROOM_MIN_M = 0.90

# H-03: 厨房门洞口宽度 ≥ 0.80m（GB 50096-2011 §5.8.7）
DOOR_WIDTH_KITCHEN_MIN_M = 0.80

# H-04: 卫生间门洞口宽度 ≥ 0.70m（GB 50096-2011 §5.8.7）
DOOR_WIDTH_BATHROOM_MIN_M = 0.70

# H-05: 无障碍通行净宽 ≥ 0.80m（《无障碍设计规范》GB 50763-2012 §3.5.1）
PASSAGE_WIDTH_ACCESSIBLE_MIN_M = 0.80

# H-06: 轮椅回转空间直径 ≥ 1.50m（GB 50763-2012 §3.5.2）
WHEELCHAIR_TURNING_DIAMETER_M = 1.50


# ── 走廊与通道 ──────────────────────────────────────────────────────────

# H-07: 通往卧室/起居室的过道净宽 ≥ 1.00m（GB 50096-2011 §5.8.1）
CORRIDOR_WIDTH_TO_BEDROOM_MIN_M = 1.00

# H-08: 通往厨房/卫生间的过道净宽 ≥ 0.90m（GB 50096-2011 §5.8.1）
CORRIDOR_WIDTH_TO_SERVICE_MIN_M = 0.90

# H-09: 入户过道净宽 ≥ 1.20m（GB 50096-2011 §5.8.1）
CORRIDOR_WIDTH_ENTRANCE_MIN_M = 1.20


# ── 房间最小面积与尺寸 ──────────────────────────────────────────────────

# H-10: 双人卧室最小使用面积 ≥ 9.0m²（GB 50096-2011 §5.6.3）
AREA_BEDROOM_DOUBLE_MIN_M2 = 9.0

# H-11: 单人卧室最小使用面积 ≥ 5.0m²（GB 50096-2011 §5.6.3）
AREA_BEDROOM_SINGLE_MIN_M2 = 5.0

# H-12: 厨房最小使用面积 ≥ 4.0m²（GB 50096-2011 §5.6.4）
AREA_KITCHEN_MIN_M2 = 4.0

# H-13: 卫生间最小使用面积 ≥ 2.5m²（GB 50096-2011 §5.6.5）
AREA_BATHROOM_MIN_M2 = 2.5

# H-14: 起居室（厅）最小使用面积 ≥ 10.0m²（GB 50096-2011 §5.6.2）
AREA_LIVING_MIN_M2 = 10.0

# H-15: 起居室/卧室最小短边净尺寸 ≥ 2.10m（GB 50096-2011 §5.6.2）
ROOM_MIN_SHORT_SIDE_M = 2.10

# H-16: 层高 ≥ 2.80m（GB 50096-2011 §5.5.1）
STOREY_HEIGHT_MIN_M = 2.80

# H-17: 室内净高（局部）≥ 2.40m（GB 50096-2011 §5.5.2）
CLEAR_HEIGHT_MIN_M = 2.40


# ── 楼梯 ────────────────────────────────────────────────────────────────

# H-18: 户内楼梯梯段净宽 ≥ 0.90m（GB 50096-2011 §6.3.1）
STAIR_FLIGHT_WIDTH_MIN_M = 0.90

# H-19: 踏步宽度 ≥ 0.26m（GB 50096-2011 §6.3.1）
STAIR_TREAD_DEPTH_MIN_M = 0.26

# H-20: 踏步高度 ≤ 0.175m（GB 50096-2011 §6.3.1）
STAIR_RISER_HEIGHT_MAX_M = 0.175


# ── 采光 ────────────────────────────────────────────────────────────────

# H-21: 卧室/起居室/厨房窗地面积比 ≥ 1/7（GB 50096-2011 §7.1.5）
WINDOW_FLOOR_RATIO_MIN = 1.0 / 7.0


# ── 按区域类型的门宽要求 ────────────────────────────────────────────────

# 区域类型 → 该类型门洞的最小宽度（依据上表 H-01~H-04）
DOOR_WIDTH_BY_REGION_TYPE: dict[str, float] = {
    "entrance": DOOR_WIDTH_ENTRANCE_MIN_M,
    "living_room": DOOR_WIDTH_ENTRANCE_MIN_M,
    "living_dining_room": DOOR_WIDTH_ENTRANCE_MIN_M,
    "dining_room": DOOR_WIDTH_KITCHEN_MIN_M,
    "bedroom": DOOR_WIDTH_BEDROOM_MIN_M,
    "kids_room": DOOR_WIDTH_BEDROOM_MIN_M,
    "library": DOOR_WIDTH_BEDROOM_MIN_M,
    "kitchen": DOOR_WIDTH_KITCHEN_MIN_M,
    "bathroom": DOOR_WIDTH_BATHROOM_MIN_M,
    "balcony": DOOR_WIDTH_KITCHEN_MIN_M,
    "hallway": DOOR_WIDTH_KITCHEN_MIN_M,
}

# 未在表中的区域类型使用的保守下限
DOOR_WIDTH_FALLBACK_MIN_M = 0.70
