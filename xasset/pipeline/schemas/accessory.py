# xasset/pipeline/schemas/accessory.py
"""accessory 层契约 —— 细节阶段产物：点缀物散布。

**跨场景统一**：一切场景都是"在区域内散布小尺度点缀物"。

| 场景 | accessory_type 示例 |
|------|-------------------|
| 室内 | vase / picture_frame / book |
| 城市 | lamp_post / signboard / trash_bin |
| 海洋 | buoy / seaweed_patch |
| 沙漠 | pebble / dry_shrub |
| 乡村 | haystack / fence_post |
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from xasset.pipeline.schemas.common import Vec3


class AccessoryElement(BaseModel):
    """一个点缀元素。"""

    element_id: str
    region_id: str
    accessory_type: str            # 开放字符串，按 scene 定义
    asset_id: str | None = None
    position: Vec3
    rotation: float = 0.0
    scale: Vec3 = (1.0, 1.0, 1.0)
    attrs: dict = Field(default_factory=dict)


class AccessoryOutput(BaseModel):
    """accessory 阶段的阶段产物。"""

    scene_type: str
    elements: list[AccessoryElement] = Field(default_factory=list)
    attrs: dict = Field(default_factory=dict)
