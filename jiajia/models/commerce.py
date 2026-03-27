# jiajia/models/commerce.py
# Stub - full implementation in Task 4
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from jiajia.db.base import Base

if TYPE_CHECKING:
    from jiajia.models.asset import AssetDefinition


class CommerceMetadata(Base):
    __tablename__ = "commerce_metadata"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_definition.id"),
        nullable=False,
        unique=True,
    )

    asset: Mapped["AssetDefinition"] = relationship(
        "AssetDefinition",
        back_populates="commerce",
    )
