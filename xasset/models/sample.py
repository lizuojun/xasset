# xasset/models/sample.py
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from xasset.db.base import Base

STYLE_VECTOR_DIM = 128
PARTITION_VECTOR_DIM = 64

def _now() -> datetime:
    return datetime.now(timezone.utc)

class Sample(Base):
    __tablename__ = "sample"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scene_type: Mapped[str] = mapped_column(String(64), nullable=False)
    sample_level: Mapped[str] = mapped_column(String(32), nullable=False)
    style: Mapped[Optional[str]] = mapped_column(String(128))
    score: Mapped[int] = mapped_column(Integer, default=0)
    scale_range: Mapped[Optional[list]] = mapped_column(JSONB)
    groups: Mapped[Optional[dict]] = mapped_column(JSONB)
    material: Mapped[Optional[dict]] = mapped_column(JSONB)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    style_vector: Mapped[Optional[list]] = mapped_column(Vector(STYLE_VECTOR_DIM))
    partition_vector: Mapped[Optional[list]] = mapped_column(Vector(PARTITION_VECTOR_DIM))
    distribution_vector: Mapped[Optional[dict]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
