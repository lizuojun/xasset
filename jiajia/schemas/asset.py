# jiajia/schemas/asset.py
import uuid
from typing import Literal, Optional
from pydantic import BaseModel

AssetLevel = Literal["object", "group", "zone", "scene"]
AssetState = Literal["draft", "published", "deprecated"]

class AssetDefinitionCreate(BaseModel):
    name: str
    asset_level: AssetLevel
    scene_type: Optional[str] = None
    object_type: Optional[str] = None
    role_hints: Optional[list[str]] = None
    style: Optional[str] = None
    tags: Optional[list[str]] = None
    source: Optional[dict] = None

class AssetDefinitionRead(AssetDefinitionCreate):
    id: uuid.UUID
    state: AssetState
    model_config = {"from_attributes": True}

class AssetInstanceCreate(BaseModel):
    definition_id: uuid.UUID
    position: Optional[list[float]] = None
    rotation: Optional[list[float]] = None
    scale: Optional[list[float]] = None
    scene_id: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = None
    role: Optional[str] = None
    overrides: Optional[dict] = None
