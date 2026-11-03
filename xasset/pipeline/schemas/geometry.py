# xasset/pipeline/schemas/geometry.py
"""geometry 层契约 —— 轮廓阶段产物：把 2D 轮廓拉成 3D 几何。

**跨场景统一**：一切场景都是"平面轮廓 + 垂直范围 → 三角网格"。

| 场景 | 网格 role 示例 |
|------|---------------|
| 室内 | floor / ceiling / wall_inner / wall_outer |
| 城市 | road_surface / building_face / ground |
| 海洋 | water_plane / seabed |
| 沙漠 | sand_plane / dune_face |
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from xasset.pipeline.schemas.common import Vec2, Vec3


class SubMesh(BaseModel):
    """一个可渲染的子网格。"""

    role: str                              # 开放字符串，按 scene 定义
    region_id: str
    vertices: list[Vec3] = Field(default_factory=list)
    normals: list[Vec3] = Field(default_factory=list)
    uvs: list[Vec2] = Field(default_factory=list)
    faces: list[tuple[int, int, int]] = Field(default_factory=list)


class WallSegmentMesh(BaseModel):
    """沿轮廓某条边的网格（室内=墙段，城市=路缘，海洋=岸线）。"""

    edge_index: int
    submeshes: list[SubMesh] = Field(default_factory=list)


class RegionGeometry(BaseModel):
    """一个区域的完整几何。"""

    region_id: str
    floor: SubMesh | None = None
    ceiling: SubMesh | None = None
    walls: list[WallSegmentMesh] = Field(default_factory=list)


class SceneMesh(BaseModel):
    """整个场景的几何集合。"""

    regions: list[RegionGeometry] = Field(default_factory=list)
    floor_offset: float = 0.0


class GeometryOutput(BaseModel):
    """geometry 阶段的阶段产物。"""

    scene_type: str
    scene_mesh: SceneMesh = Field(default_factory=SceneMesh)
    wall_thickness: float = Field(default=0.2, gt=0)
    attrs: dict = Field(default_factory=dict)
