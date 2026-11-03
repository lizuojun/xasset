# xasset/pipeline/schemas/understand.py
"""understand 层契约 —— 轮廓阶段产物：轮廓线 + 语义标签 + 轮廓语义。

**一套契约统一描述一切场景**：房间、街区、海域、沙丘都是"带垂直范围的
平面轮廓 + 区域类别 + 轮廓语义"。house 只是其中一个填法。

| 场景 | region_type 示例 | elevation 语义 |
|------|-----------------|---------------|
| 室内 | living_room / bedroom / kitchen | 层高 |
| 城市 | road / building_footprint / plaza / green_space | 建筑高度 |
| 乡村 | farmland / orchard / village_block | 地形起伏 |
| 海洋 | deep_water / shallow_water / reef | 水深（负值） |
| 沙漠 | dune / gravel_plain / oasis | 沙丘高度 |
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from xasset.pipeline.schemas.common import ContourSemantics, ElevationRange, Polygon


class SceneRegion(BaseModel):
    """一个区域 —— 跨场景的通用抽象。

    一切场景都归结为：
      - 一个平面轮廓（boundary）
      - 一个区域类别（region_type，开放字符串）
      - 一个垂直范围（elevation）
      - 轮廓上的语义（semantics：开口 / 固定边）
      - 场景特有的其它信息（attrs）
    """

    region_id: str
    region_type: str = ""                  # 开放字符串，词表按 scene 定义
    boundary: Polygon                      # ★ 轮廓线
    area: float = Field(ge=0)              # m²（由轮廓计算，冗余存储便于校验）
    elevation: ElevationRange = Field(default_factory=ElevationRange)  # ★ 垂直范围
    semantics: ContourSemantics = Field(default_factory=ContourSemantics)  # ★ 轮廓语义
    priority: int = 0                      # 同类型主次：0=无，1=主，2+=次
    attrs: dict = Field(default_factory=dict)   # 场景特有信息一律进这里


class UnderstandOutput(BaseModel):
    """understand 阶段的阶段产物。"""

    scene_type: str                        # house / urban / rural / ocean / desert / ...
    regions: list[SceneRegion] = Field(default_factory=list)
    style: str | None = None
    constraints: dict = Field(default_factory=dict)
    attrs: dict = Field(default_factory=dict)   # 场景级特有信息
