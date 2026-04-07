# xasset/models/asset.py
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Enum, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from xasset.db.base import Base

def _now() -> datetime:
    return datetime.now(timezone.utc)

class AssetDefinition(Base):
    __tablename__ = "asset_definition"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    asset_level: Mapped[str] = mapped_column(
        Enum("object", "group", "zone", "scene", name="asset_level_enum"),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        Enum("draft", "published", "deprecated", name="asset_state_enum"),
        default="draft", nullable=False,
    )
    scene_type: Mapped[Optional[str]] = mapped_column(String(64))
    object_type: Mapped[Optional[str]] = mapped_column(String(256))
    role_hints: Mapped[Optional[list]] = mapped_column(JSON)
    style: Mapped[Optional[str]] = mapped_column(String(128))
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    source: Mapped[Optional[dict]] = mapped_column(JSON)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON)
    packaged_data: Mapped[Optional[dict]] = mapped_column(JSON)
    layout: Mapped[Optional[dict]] = mapped_column(JSON)
    light: Mapped[Optional[dict]] = mapped_column(JSON)
    computed_features: Mapped[Optional[dict]] = mapped_column(JSON)
    metadata_extra: Mapped[Optional[dict]] = mapped_column(JSON)  # 预留扩展

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))

    # canonical_children: scene_id=None 的实例，代表默认排列模板
    canonical_children: Mapped[list["AssetInstance"]] = relationship(
        "AssetInstance",
        primaryjoin="and_(AssetInstance.definition_id==AssetDefinition.id, "
                    "AssetInstance.scene_id==None)",
        foreign_keys="AssetInstance.definition_id",
        viewonly=True,
    )

    # commerce: 一对一关系
    commerce: Mapped[Optional["CommerceMetadata"]] = relationship(
        "CommerceMetadata",
        back_populates="asset",
        uselist=False,
        lazy="selectin",
    )


class AssetInstance(Base):
    __tablename__ = "asset_instance"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    definition_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("asset_definition.id"),
        nullable=False,
    )
    # scene_id=None → canonical_children（模板）
    # scene_id 有值 → 场景中的实际实例，始终指向根场景 AssetDefinition.id
    scene_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("asset_definition.id"),
        nullable=True,
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("asset_instance.id"),
        nullable=True,
    )
    position: Mapped[Optional[list]] = mapped_column(JSON)   # [x, y, z]，Y-up
    rotation: Mapped[Optional[list]] = mapped_column(JSON)   # [qx, qy, qz, qw]
    scale: Mapped[Optional[list]] = mapped_column(JSON)      # [sx, sy, sz]
    group_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    role: Mapped[Optional[str]] = mapped_column(String(128))
    overrides: Mapped[Optional[dict]] = mapped_column(JSON)

    definition: Mapped["AssetDefinition"] = relationship(
        "AssetDefinition",
        foreign_keys=[definition_id],
        overlaps="canonical_children",
    )


# 延迟导入避免循环引用
from xasset.models.commerce import CommerceMetadata  # noqa: E402
