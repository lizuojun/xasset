# xasset/pipeline/schemas/stylize.py
"""stylize 层契约 —— 细节阶段产物：风格化（材质 / 灯光 / 相机）。

**跨场景统一**：一切场景都是"给实体分配材质 + 配置光照 + 给出机位"。
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from xasset.pipeline.schemas.common import Vec3


class MaterialAssignment(BaseModel):
    """材质分配。"""

    target_id: str                 # 对应 SurfaceElement.element_id 或资产实例 id
    material_id: str
    params: dict = Field(default_factory=dict)


class LightConfig(BaseModel):
    """一盏灯。"""

    light_id: str = ""
    light_type: str                # "directional" | "point" | "ambient" | "spot"
    position: Vec3 | None = None
    rotation: float | None = None
    intensity: float = Field(default=1.0, ge=0)
    color: str | None = None
    attrs: dict = Field(default_factory=dict)


class CameraHint(BaseModel):
    """相机建议机位。"""

    position: Vec3
    target: Vec3
    fov: float | None = None


class StylizeOutput(BaseModel):
    """stylize 阶段的阶段产物。"""

    scene_type: str | None = None
    style: str | None = None
    material_assignments: list[MaterialAssignment] = Field(default_factory=list)
    light_config: list[LightConfig] = Field(default_factory=list)
    camera_hints: list[CameraHint] = Field(default_factory=list)
    attrs: dict = Field(default_factory=dict)
