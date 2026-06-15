# xasset/config/schemas.py
from typing import Optional
from pydantic import BaseModel

class SizeRange(BaseModel):
    w: list[float]
    h: list[float]
    d: list[float]

class RoleDefinition(BaseModel):
    name: str
    tier: str
    asset_types: list[str]
    count: list[int]
    size_range: Optional[SizeRange] = None
    optional: bool = False

class Placement(BaseModel):
    role: str
    position: dict
    rotation: dict
    count: list[int]

class Template(BaseModel):
    id: str
    name: str
    placement_mode: str
    sequence: list[str]
    placements: list[Placement]
    total_count: int  # 所有角色 count.max 之和的上限，用于资源预算

class GroupDefinition(BaseModel):
    id: str
    name: str
    code: int
    category: str = "furniture"      # "furniture" | "surface"
    anchor_surface: Optional[str] = None  # surface groups: "wall"|"ceiling"|"floor"|"window"
    scene_types: list[str]
    anchor_role: str
    roles: list[RoleDefinition]
    templates: list[Template]
    # Layout placement fields (furniture groups only; null for surface groups)
    footprint_range: Optional[list[list[float]]] = None  # [[w_min,w_max],[d_min,d_max]] in metres
    wall_offset_ratio: float = 0.0   # 0.0=against wall, 0.5=island centre, 1.0=180° flip
    facing_group: Optional[str] = None  # code of group this one should face (soft constraint)

class RegionGroupEntry(BaseModel):
    code: int
    required: bool = True
    priority: int = 1


class GroupConfigFile(BaseModel):
    scene_type: str
    region_groups: dict[str, list[RegionGroupEntry]] = {}
    groups: list[GroupDefinition]
