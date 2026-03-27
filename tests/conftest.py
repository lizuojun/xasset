# tests/conftest.py
import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from jiajia.db.base import Base
# 导入所有 ORM 模型，确保 Base.metadata 包含所有表
import jiajia.models.asset        # noqa: F401
import jiajia.models.commerce     # noqa: F401
import jiajia.models.sample       # noqa: F401
import jiajia.models.composition  # noqa: F401

TEST_DB_URL = os.getenv(
    "TEST_DB_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/jiajia_test",
)


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DB_URL)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
        await s.rollback()
