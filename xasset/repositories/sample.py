# xasset/repositories/sample.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from xasset.models.sample import Sample

class SampleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Sample:
        sample = Sample(**kwargs)
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def search_by_style(
        self,
        query_vector: list[float],
        scene_type: str,
        sample_level: str,
        limit: int = 10,
    ) -> list[Sample]:
        result = await self.session.execute(
            select(Sample)
            .where(Sample.scene_type == scene_type)
            .where(Sample.sample_level == sample_level)
            .order_by(Sample.style_vector.op("<->")(query_vector))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_partition(
        self,
        query_vector: list[float],
        scene_type: str,
        limit: int = 10,
    ) -> list[Sample]:
        result = await self.session.execute(
            select(Sample)
            .where(Sample.scene_type == scene_type)
            .order_by(Sample.partition_vector.op("<->")(query_vector))
            .limit(limit)
        )
        return list(result.scalars().all())
