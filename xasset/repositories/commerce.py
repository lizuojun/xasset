# xasset/repositories/commerce.py
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from xasset.models.commerce import CommerceMetadata, Listing

class CommerceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> CommerceMetadata:
        commerce = CommerceMetadata(**kwargs)
        self.session.add(commerce)
        await self.session.commit()
        await self.session.refresh(commerce)
        return commerce

    async def get_by_asset(self, asset_id: uuid.UUID) -> Optional[CommerceMetadata]:
        result = await self.session.execute(
            select(CommerceMetadata).where(CommerceMetadata.asset_id == asset_id)
        )
        return result.scalar_one_or_none()


class ListingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Listing:
        listing = Listing(**kwargs)
        self.session.add(listing)
        await self.session.commit()
        await self.session.refresh(listing)
        return listing

    async def list_active(self) -> list[Listing]:
        result = await self.session.execute(
            select(Listing).where(Listing.listed.is_(True))
        )
        return list(result.scalars().all())
