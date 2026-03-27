# jiajia/models/composition.py
import uuid
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from jiajia.db.base import Base


class GroupInstance(Base):
    __tablename__ = "group_instance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # GroupDefinition 存于 JSON 配置，用 code（int）作引用键
    definition_code: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_definition.id")
    )
    position: Mapped[Optional[list]] = mapped_column(JSONB)
    rotation: Mapped[Optional[list]] = mapped_column(JSONB)
    scale: Mapped[Optional[list]] = mapped_column(JSONB)
    role_assignments: Mapped[Optional[list]] = mapped_column(JSONB)


class Region(Base):
    __tablename__ = "region"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scene_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_definition.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(128), nullable=False)
    boundary: Mapped[Optional[list]] = mapped_column(JSONB)
    groups: Mapped[Optional[list]] = mapped_column(JSONB)
    partition_vector: Mapped[Optional[list]] = mapped_column(JSONB)
    distribution_vector: Mapped[Optional[dict]] = mapped_column(JSONB)
