# tests/test_sample.py
from jiajia.models.sample import Sample, STYLE_VECTOR_DIM, PARTITION_VECTOR_DIM

async def test_create_sample(session):
    sample = Sample(
        scene_type="house",
        sample_level="zone",
        style="现代简约",
        score=85,
        scale_range=[10.0, 30.0],
        style_vector=[0.1] * STYLE_VECTOR_DIM,
        partition_vector=[0.2] * PARTITION_VECTOR_DIM,
    )
    session.add(sample)
    await session.commit()
    assert sample.id is not None
    assert sample.score == 85

async def test_vector_similarity_search(session):
    from sqlalchemy import select
    s1 = Sample(
        scene_type="house", sample_level="zone", style="现代",
        score=80, style_vector=[1.0] + [0.0] * (STYLE_VECTOR_DIM - 1),
    )
    s2 = Sample(
        scene_type="house", sample_level="zone", style="古典",
        score=75, style_vector=[0.0] * STYLE_VECTOR_DIM,
    )
    session.add_all([s1, s2])
    await session.commit()

    query = [1.0] + [0.0] * (STYLE_VECTOR_DIM - 1)
    result = await session.execute(
        select(Sample)
        .where(Sample.scene_type == "house")
        .order_by(Sample.style_vector.op("<->")(query))
        .limit(1)
    )
    closest = result.scalar_one()
    assert closest.id == s1.id


# 追加到 tests/test_sample.py 末尾
from jiajia.repositories.sample import SampleRepository

async def test_sample_repo_search_by_style(session):
    repo = SampleRepository(session)
    await repo.create(scene_type="house", sample_level="zone", style="现代",
                      score=80, style_vector=[1.0] + [0.0] * (STYLE_VECTOR_DIM - 1))
    await repo.create(scene_type="house", sample_level="zone", style="古典",
                      score=75, style_vector=[0.0] * STYLE_VECTOR_DIM)

    results = await repo.search_by_style(
        query_vector=[1.0] + [0.0] * (STYLE_VECTOR_DIM - 1),
        scene_type="house", sample_level="zone", limit=1,
    )
    assert results[0].style == "现代"
