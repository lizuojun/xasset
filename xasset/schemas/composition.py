# xasset/schemas/composition.py
import uuid
from typing import Optional
from pydantic import BaseModel

class GroupInstanceCreate(BaseModel):
    definition_code: int
    scene_id: Optional[uuid.UUID] = None
    position: Optional[list[float]] = None
    rotation: Optional[list[float]] = None
    scale: Optional[list[float]] = None
    role_assignments: Optional[list[dict]] = None

class RegionCreate(BaseModel):
    scene_id: uuid.UUID
    type: str
    boundary: Optional[list[list[float]]] = None
    groups: Optional[list[uuid.UUID]] = None
