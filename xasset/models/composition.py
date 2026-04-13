# xasset/models/composition.py
import uuid
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column
from xasset.db.base import Base


class GroupInstance(Base):
    __tablename__ = "group_instance"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # GroupDefinition 存于 JSON 配置，用 code（int）作引用键
    definition_code: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset_definition.id")
    )
    position: Mapped[Optional[list]] = mapped_column(JSON)
    rotation: Mapped[Optional[list]] = mapped_column(JSON)
    scale: Mapped[Optional[list]] = mapped_column(JSON)
    role_assignments: Mapped[Optional[list]] = mapped_column(JSON)


class Region(Base):
    __tablename__ = "region"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scene_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset_definition.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(128), nullable=False)
    boundary: Mapped[Optional[list]] = mapped_column(JSON)
    groups: Mapped[Optional[list]] = mapped_column(JSON)
    partition_vector: Mapped[Optional[list]] = mapped_column(JSON)
    distribution_vector: Mapped[Optional[dict]] = mapped_column(JSON)
    doors: Mapped[Optional[list]] = mapped_column(JSON)
    # [{"pts": [[x,z]*4], "normal": [nx,nz], "center": [x,z], "width": float}, ...]
    windows: Mapped[Optional[list]] = mapped_column(JSON)
    # [{"pts": [[x,z]*4], "sill_height": float, "height": float, "center": [x,z], "width": float}, ...]
