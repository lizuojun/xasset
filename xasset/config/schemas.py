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
    scene_types: list[str]
    anchor_role: str
    roles: list[RoleDefinition]
    templates: list[Template]

class GroupConfigFile(BaseModel):
    scene_type: str
    groups: list[GroupDefinition]
