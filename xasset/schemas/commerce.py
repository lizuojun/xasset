# xasset/schemas/commerce.py
import uuid
from typing import Literal, Optional
from pydantic import BaseModel, field_validator

LicenseType = Literal["exclusive", "non_exclusive", "personal", "commercial"]

class ListingCreate(BaseModel):
    title: str
    type: Literal["asset", "ip_bundle"]
    targets: Optional[list[dict]] = None
    credit_price: int
    license_type: LicenseType
    transferable: bool = False

    @field_validator("credit_price")
    @classmethod
    def price_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("credit_price must be >= 0")
        return v

class CommerceMetadataRead(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    owner_id: uuid.UUID
    version: str
    credit_final: int
    license_tradeable: bool
    model_config = {"from_attributes": True}
