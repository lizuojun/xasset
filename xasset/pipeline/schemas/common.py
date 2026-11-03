# xasset/pipeline/schemas/common.py
"""共享基础类型 —— 六个 Stage 契约共用的几何与语义基元。

设计目标：**一套契约统一描述室内 / 室外 / 城市 / 乡村 / 海洋 / 沙漠**。
house 只是这套抽象的一个填法，不是设计基准。

统一手段：
- 几何：一切都是"带高度的平面轮廓"（Polygon + ElevationRange）
- 垂直维度：统一用中性的 elevation（室内=层高，城市=建筑高，海洋=水深用负值）
- 轮廓语义：统一用"开口（可通行/可穿越）+ 固定边（不可位移）"两个抽象，
  具体内涵由开放的 feature_type / edge_type 字符串承载
- 场景特有信息：一律进 attrs，不新增字段

单位统一为米（m）：
- Vec2: [x, z] 平面坐标（XZ 平面，Y 向上）
- Vec3: [x, y, z] 三维坐标
"""
from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

Vec2 = tuple[float, float]
Vec3 = tuple[float, float, float]


class Polygon(BaseModel):
    """平面轮廓（XZ 平面，单位 m）。

    一切场景的区域基础：房间、街区、海域、沙丘范围都是平面轮廓。
    契约只保证"至少 3 个互不相同的点"；几何合法性（闭合、不自交、
    面积合理）由各 Stage 的约束侧校验门负责。
    """

    points: list[Vec2] = Field(min_length=3)

    @model_validator(mode="after")
    def _check_distinct(self) -> "Polygon":
        if len(set(self.points)) < 3:
            raise ValueError("轮廓至少需要 3 个互不相同的顶点")
        return self


class ElevationRange(BaseModel):
    """垂直维度（单位 m，Y 向上）。

    用中性字段统一各场景的"高度"概念：

    | 场景 | low | high | 语义 |
    |------|-----|------|------|
    | 室内 house  | 0     | 2.8   | 层高 |
    | 城市 urban  | 0     | 45.0  | 建筑高度 |
    | 海洋 ocean  | -120  | 0     | 水深（水下为负） |
    | 沙漠 desert | 0     | 12    | 沙丘起伏高度 |
    | 乡村 rural  | 0     | 6     | 地形起伏 |
    """

    low: float = 0.0
    high: float | None = None      # None 表示该区域无明确上界（如开阔水域）

    @model_validator(mode="after")
    def _check_order(self) -> "ElevationRange":
        if self.high is not None and self.high < self.low:
            raise ValueError(f"elevation.high({self.high}) 不能小于 low({self.low})")
        return self


class BoundaryFeature(BaseModel):
    """轮廓上的语义要素 —— 通用抽象。

    两类共同语义：
    - **开口**（kind="opening"）：可通行 / 可穿越 / 可开洞的位置
    - **固定边**（kind="fixed_edge"）：不可位移、不可编辑的边界段

    具体内涵由开放的 feature_type 承载，不枚举场景：
    - 室内：door / window / archway
    - 城市：road_entrance / intersection / building_entrance / gate
    - 海洋：shoreline_crossing / channel / strait
    - 沙漠：dune_pass / wind_gap
    - 乡村：field_gate / path_crossing
    """

    feature_id: str
    kind: str                      # "opening" | "fixed_edge"
    feature_type: str              # 开放字符串，按 scene 自由定义
    pts: list[Vec2] = Field(default_factory=list)   # 开口的几何位置（固定边可为空）
    seg_start: Vec2 | None = None  # 所在的轮廓段
    seg_end: Vec2 | None = None
    width: float | None = None     # m；固定边可无宽度
    connects_to: str | None = None # 连通到的其它区域 region_id
    attrs: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check_kind(self) -> "BoundaryFeature":
        if self.kind not in ("opening", "fixed_edge"):
            raise ValueError(f"boundary feature kind 必须是 opening 或 fixed_edge，得到 {self.kind}")
        return self


class ContourSemantics(BaseModel):
    """轮廓语义：挂在区域轮廓上的全部语义要素。

    **注意区分**：这是数据概念（轮廓上有什么），与 Artist 范式里
    "约束侧"这个机制概念无关。
    """

    features: list[BoundaryFeature] = Field(default_factory=list)

    # ---- 便捷筛选 ----
    @property
    def openings(self) -> list[BoundaryFeature]:
        return [f for f in self.features if f.kind == "opening"]

    @property
    def fixed_edges(self) -> list[BoundaryFeature]:
        return [f for f in self.features if f.kind == "fixed_edge"]
