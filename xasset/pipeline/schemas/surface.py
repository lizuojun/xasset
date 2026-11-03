# xasset/pipeline/schemas/surface.py
"""surface 层契约 —— 主体阶段产物：表面覆盖。

**跨场景统一**：一切场景都是"给区域的某类表面铺上材质"。

| 场景 | surface_role 示例 | material 示例 |
|------|------------------|--------------|
| 室内 | wall / floor / ceiling | 墙纸 / 木地板 / 吊顶 |
| 城市 | road_base / green_base / plaza_base | 沥青 / 草地 / 石板 |
| 海洋 | water_surface / seabed | 水面 / 海床 |
| 沙漠 | sand_surface / rock_face | 沙粒 / 岩面 |
| 乡村 | field_soil / path_surface | 土 / 碎石路 |
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from xasset.pipeline.schemas.common import Vec2


class SurfaceElement(BaseModel):
    """一个待覆盖的表面构件。"""

    element_id: str
    region_id: str
    surface_role: str              # 开放字符串，按 scene 定义
    material_id: str | None = None
    uv_scale: Vec2 | None = None
    attrs: dict = Field(default_factory=dict)


class SurfaceOutput(BaseModel):
    """surface 阶段的阶段产物。"""

    scene_type: str
    elements: list[SurfaceElement] = Field(default_factory=list)
    attrs: dict = Field(default_factory=dict)
