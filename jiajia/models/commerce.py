# jiajia/models/commerce.py
import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from jiajia.db.base import Base

if TYPE_CHECKING:
    from jiajia.models.asset import AssetDefinition

def _now() -> datetime:
    return datetime.now(timezone.utc)

class Listing(Base):
    __tablename__ = "listing"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    type: Mapped[str] = mapped_column(
        Enum("asset", "ip_bundle", name="listing_type_enum"), nullable=False
    )
    targets: Mapped[Optional[list]] = mapped_column(JSONB)
    ip_bundle: Mapped[Optional[dict]] = mapped_column(JSONB)
    credit_price: Mapped[int] = mapped_column(Integer, default=0)
    license_type: Mapped[str] = mapped_column(
        Enum("exclusive", "non_exclusive", "personal", "commercial",
             name="license_type_enum"),
        default="non_exclusive",
    )
    transferable: Mapped[bool] = mapped_column(Boolean, default=False)
    listed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class CommerceMetadata(Base):
    __tablename__ = "commerce_metadata"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_definition.id"),
        unique=True,
        nullable=False,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    origin_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    changelog: Mapped[Optional[str]] = mapped_column(String(1024))
    version_history: Mapped[Optional[list]] = mapped_column(JSONB)

    watermark_id: Mapped[Optional[str]] = mapped_column(String(256))
    watermark_method: Mapped[Optional[str]] = mapped_column(String(32))
    watermark_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    license_tradeable: Mapped[bool] = mapped_column(Boolean, default=False)
    license_partial: Mapped[bool] = mapped_column(Boolean, default=False)
    license_transferable: Mapped[bool] = mapped_column(Boolean, default=False)

    credit_dimensions: Mapped[Optional[dict]] = mapped_column(JSONB)
    credit_total: Mapped[int] = mapped_column(Integer, default=0)
    credit_manual_adjust: Mapped[int] = mapped_column(Integer, default=0)
    credit_final: Mapped[int] = mapped_column(Integer, default=0)

    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listing.id"), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    asset: Mapped["AssetDefinition"] = relationship(
        "AssetDefinition", back_populates="commerce"
    )


class PlatformConfig(Base):
    __tablename__ = "platform_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exchange_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue_share: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="CNY")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
