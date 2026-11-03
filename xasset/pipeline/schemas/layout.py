# xasset/pipeline/schemas/layout.py
"""layout 层契约 —— 主体阶段产物：把内容摆进区域。

**跨场景统一**：一切场景的"主体内容摆放"都归结为两类：
1. **PlacedElement** —— 摆进区域内的内容主体（室内=家具组，城市=建筑/设施，
   海洋=船只/礁石，沙漠=植被/岩石，乡村=农舍/作物）
2. **PlacedFeature** —— 轮廓上语义要素的落地实例（室内=门窗实体，
   城市=路口标记，海洋=航道标识，沙漠=风口标记）

house 的"家具 Group / 门窗 / 窗帘"只是 PlacedElement + PlacedFeature 的
一种填法，不单独占字段。
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from xasset.pipeline.schemas.common import Vec3


class PlacedElement(BaseModel):
    """摆进区域的内容主体 —— 跨场景通用。

    | 场景 | element_type 示例 | parts 的含义 |
    |------|------------------|-------------|
    | 室内 | sofa_group / dining_group | 各 role 的具体资产 |
    | 城市 | building / street_furniture | 建筑构件 / 设施部件 |
    | 海洋 | vessel / reef_cluster | 船体部件 / 礁石簇 |
    | 沙漠 | dune_vegetation / rock_cluster | 植株 / 岩块 |
    | 乡村 | farmhouse / crop_row | 建筑构件 / 作物行 |
    """

    element_id: str
    element_type: str                        # 开放字符串，按 scene 定义
    region_id: str                           # 摆在哪个区域
    position: Vec3
    rotation: float = 0.0                    # 绕 Y 轴，度
    scale: Vec3 = (1.0, 1.0, 1.0)
    parts: dict[str, str | None] = Field(default_factory=dict)   # 部件 → 资产 id
    part_positions: dict[str, Vec3] = Field(default_factory=dict)  # 部件相对位置
    attrs: dict = Field(default_factory=dict)


class PlacedFeature(BaseModel):
    """轮廓要素的落地实例 —— 跨场景通用。

    | 场景 | feature_type 示例 |
    |------|-----------------|
    | 室内 | door / window / curtain |
    | 城市 | road_gate / crosswalk |
    | 海洋 | channel_marker |
    | 沙漠 | wind_gap_marker |
    """

    feature_id: str                          # 对应 ContourSemantics 里的 feature_id
    feature_type: str
    region_id: str
    position: Vec3
    rotation: float = 0.0
    width: float | None = None
    attrs: dict = Field(default_factory=dict)


class LayoutOutput(BaseModel):
    """layout 阶段的阶段产物。"""

    scene_type: str
    placed_elements: list[PlacedElement] = Field(default_factory=list)
    placed_features: list[PlacedFeature] = Field(default_factory=list)
    attrs: dict = Field(default_factory=dict)
