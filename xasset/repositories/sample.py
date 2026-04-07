# xasset/repositories/sample.py
import math
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from xasset.models.sample import Sample


def _cosine_distance(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1.0 - dot / (norm_a * norm_b)


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
            .where(Sample.style_vector.is_not(None))
        )
        rows = list(result.scalars().all())
        rows.sort(key=lambda s: _cosine_distance(query_vector, s.style_vector))
        return rows[:limit]

    async def search_by_partition(
        self,
        query_vector: list[float],
        scene_type: str,
        limit: int = 10,
    ) -> list[Sample]:
        result = await self.session.execute(
            select(Sample)
            .where(Sample.scene_type == scene_type)
            .where(Sample.partition_vector.is_not(None))
        )
        rows = list(result.scalars().all())
        rows.sort(key=lambda s: _cosine_distance(query_vector, s.partition_vector))
        return rows[:limit]
