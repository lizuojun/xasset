# xasset/repositories/asset.py
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from xasset.models.asset import AssetDefinition, AssetInstance

class AssetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> AssetDefinition:
        asset = AssetDefinition(**kwargs)
        self.session.add(asset)
        await self.session.commit()
        await self.session.refresh(asset)
        return asset

    async def get(self, asset_id: uuid.UUID) -> Optional[AssetDefinition]:
        result = await self.session.execute(
            select(AssetDefinition).where(AssetDefinition.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def list_by_scene_type(
        self, scene_type: str, asset_level: Optional[str] = None
    ) -> list[AssetDefinition]:
        query = select(AssetDefinition).where(
            AssetDefinition.scene_type == scene_type
        )
        if asset_level:
            query = query.where(AssetDefinition.asset_level == asset_level)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def publish(
        self, asset_id: uuid.UUID, usd_url: str, gltf_url: str
    ) -> AssetDefinition:
        asset = await self.get(asset_id)
        asset.state = "published"
        asset.packaged_data = {"usd_url": usd_url, "gltf_url": gltf_url}
        await self.session.commit()
        await self.session.refresh(asset)
        return asset

    async def deprecate(self, asset_id: uuid.UUID) -> AssetDefinition:
        asset = await self.get(asset_id)
        asset.state = "deprecated"
        await self.session.commit()
        return asset

    async def create_instance(
        self,
        definition_id: uuid.UUID,
        scene_id: Optional[uuid.UUID],
        **kwargs,
    ) -> AssetInstance:
        definition = await self.get(definition_id)
        if definition and definition.state == "deprecated":
            raise ValueError(
                f"Cannot create instance of deprecated asset {definition_id}"
            )
        instance = AssetInstance(
            definition_id=definition_id, scene_id=scene_id, **kwargs
        )
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
