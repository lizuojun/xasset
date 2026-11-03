# xasset/pipeline/context.py
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineInput:
    input_type: str               # "text" | "image" | "concept_art"
    scene_type: str               # "house" | "urban" | "wild"
    text_description: str | None = None
    image_url: str | None = None
    style: str | None = None
    constraints: dict = field(default_factory=dict)
    scene_vector: dict | None = None   # SceneVector JSON（单区域，来自矢量输入）
    region_type: str | None = None     # 覆盖 scene_vector 内的 type 字段


@dataclass
class RoleTarget:
    """Identifies a role slot within a placed group for model replacement."""
    group_instance_id: uuid.UUID
    role: str                     # e.g. "sofa", "coffee_table"


@dataclass
class AssetTarget:
    """Identifies a specific asset instance for material/light replacement."""
    asset_instance_id: uuid.UUID


@dataclass
class VariationInput:
    replace_models: list[RoleTarget] | None = None
    replace_materials: list[AssetTarget] | None = None
    replace_lights: bool = False
    replace_accessories: bool = False
    style: str | None = None


@dataclass
class PipelineContext:
    job_id: str
    input: PipelineInput
    stage_outputs: dict[str, Any] = field(default_factory=dict)
    status: str = "running"       # "running" | "done" | "failed"
    error: str | None = None
