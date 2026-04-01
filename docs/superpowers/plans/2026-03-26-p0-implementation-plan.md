# P0 资产数据模型 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 JiaJia 平台的核心数据模型基础设施，包括资产定义/实例、商业化元数据、Spatial Composition 配置体系、Sample 向量搜索库。

**Architecture:** Python + PostgreSQL + pgvector 的异步架构。核心资产元数据存 PostgreSQL，向量特征（style/partition）存 pgvector，GroupDefinition/Template 等静态规则以 JSON 配置文件管理并在启动时加载入内存，Sample 库存 PostgreSQL + pgvector 支持相似度检索。ORM 层用 SQLAlchemy 2.0 async，Schema 验证用 Pydantic v2，数据库迁移用 Alembic。

**Tech Stack:** Python 3.11+, PostgreSQL 16 + pgvector, SQLAlchemy 2.0 async, Pydantic v2 + pydantic-settings, Alembic, pytest + pytest-asyncio (asyncio_mode=auto), uv

---

## 文件结构

```
jiajia/
  __init__.py
  db/
    __init__.py
    connection.py         DB engine / session factory（async）
    base.py               SQLAlchemy declarative Base
  models/                 SQLAlchemy ORM 模型（数据库表）
    __init__.py
    asset.py              AssetDefinition, AssetInstance
    commerce.py           CommerceMetadata, Listing, PlatformConfig
    sample.py             Sample（含 pgvector 列）
    composition.py        GroupInstance, Region
  schemas/                Pydantic v2 schemas（API 验证 + 序列化）
    __init__.py
    asset.py
    commerce.py
    composition.py
  repositories/           数据库操作封装（CRUD + 查询）
    __init__.py
    asset.py              AssetRepository
    commerce.py           ListingRepository, CommerceRepository
    sample.py             SampleRepository（含向量相似搜索）
  config/
    __init__.py
    loader.py             JSON 配置加载器 + 验证
    schemas.py            GroupDefinition/RoleDefinition/Template 的 Pydantic schema
  data/
    groups/
      house.json          House 场景的 GroupDefinition + Template
      urban.json          （占位）
      wild.json           （占位）
  migrations/
    env.py
    versions/
      001_initial.py
  tests/
    __init__.py
    conftest.py           测试 DB 连接、fixture
    test_asset.py         AssetDefinition/Instance CRUD
    test_commerce.py      Commerce / Listing 操作
    test_sample.py        Sample 写入 + 向量搜索
    test_composition.py   GroupInstance / Region 操作
    test_config.py        JSON 配置加载验证
    test_schemas.py       Pydantic schema 验证
    test_integration.py   端到端生命周期验证
pyproject.toml
alembic.ini
.env.example
```

---

## Task 1：项目初始化

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: 所有 `__init__.py`

- [ ] **Step 1: 初始化 uv 项目**

```bash
cd D:/Projects/JiaJia
uv init --python 3.11 --package
```

- [ ] **Step 2: 安装依赖**

```bash
uv add sqlalchemy[asyncio] asyncpg pydantic pydantic-settings alembic pgvector python-dotenv
uv add --dev pytest pytest-asyncio pytest-cov
```

- [ ] **Step 3: 配置 pytest asyncio_mode（在 pyproject.toml 追加）**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] **Step 4: 创建所有子包 `__init__.py`**

```bash
mkdir -p jiajia/db jiajia/models jiajia/schemas jiajia/repositories jiajia/config jiajia/data/groups tests
touch jiajia/__init__.py
touch jiajia/db/__init__.py
touch jiajia/models/__init__.py
touch jiajia/schemas/__init__.py
touch jiajia/repositories/__init__.py
touch jiajia/config/__init__.py
touch tests/__init__.py
```

- [ ] **Step 5: 创建 .env.example**

```ini
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/jiajia
DATABASE_URL_SYNC=postgresql://postgres:password@localhost:5432/jiajia
```

- [ ] **Step 6: 复制为 .env 并填写本地数据库地址**

```bash
cp .env.example .env
# 编辑 .env，填入实际的数据库用户名和密码
```

- [ ] **Step 7: 确认 PostgreSQL 已安装 pgvector 扩展**

```sql
-- 在 psql 中执行
CREATE DATABASE jiajia;
CREATE DATABASE jiajia_test;
\c jiajia
CREATE EXTENSION IF NOT EXISTS vector;
\c jiajia_test
CREATE EXTENSION IF NOT EXISTS vector;
-- 各执行后预期：CREATE EXTENSION
```

- [ ] **Step 8: Commit**

```bash
git init
git add .
git commit -m "chore: init project structure"
```

---

## Task 2：数据库连接层

**Files:**
- Create: `jiajia/db/base.py`
- Create: `jiajia/db/connection.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: 写 base.py**

```python
# jiajia/db/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

- [ ] **Step 2: 写 connection.py**

```python
# jiajia/db/connection.py
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str

settings = Settings()

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

- [ ] **Step 3: 写 tests/conftest.py**

```python
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
```

- [ ] **Step 4: 写连接冒烟测试**

```python
# tests/test_connection.py
from jiajia.db.connection import engine

async def test_db_connection():
    async with engine.connect() as conn:
        result = await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        assert result.scalar() == 1
```

- [ ] **Step 5: 运行测试**

```bash
uv run pytest tests/test_connection.py -v
# 预期：1 passed
```

- [ ] **Step 6: Commit**

```bash
git add jiajia/db/ tests/conftest.py tests/test_connection.py
git commit -m "feat: add async db connection layer"
```

---

## Task 3：核心资产 ORM 模型

**Files:**
- Create: `jiajia/models/asset.py`
- Create: `tests/test_asset.py`

- [ ] **Step 1: 写 tests/test_asset.py（先写测试）**

```python
# tests/test_asset.py
import pytest
from sqlalchemy import select
from jiajia.models.asset import AssetDefinition, AssetInstance

async def test_create_asset_definition(session):
    asset = AssetDefinition(
        name="明式圈椅",
        asset_level="object",
        state="draft",
        scene_type="house",
        object_type="house/room/furniture/chair",
        style="中式古典",
        tags=["椅子", "明式", "木质"],
    )
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    assert asset.id is not None
    assert asset.asset_level == "object"
    assert asset.state == "draft"

async def test_canonical_children(session):
    """canonical_children 的 scene_id 应为 None（模板实例）"""
    parent = AssetDefinition(
        name="会客组",
        asset_level="group",
        state="draft",
        scene_type="house",
        object_type="house/room/group/meeting",
    )
    session.add(parent)
    await session.flush()

    child = AssetInstance(
        definition_id=parent.id,
        position=[0.0, 0.0, 0.0],
        rotation=[0.0, 0.0, 0.0, 1.0],
        scale=[1.0, 1.0, 1.0],
        scene_id=None,  # canonical_children
    )
    session.add(child)
    await session.commit()

    result = await session.execute(
        select(AssetInstance).where(
            AssetInstance.definition_id == parent.id,
            AssetInstance.scene_id.is_(None),
        )
    )
    canonical = result.scalars().all()
    assert len(canonical) == 1

async def test_placed_instance_has_scene_id(session):
    """放入场景的实例 scene_id 不为 None"""
    scene = AssetDefinition(
        name="测试场景", asset_level="scene", state="draft",
        scene_type="house", object_type="house",
    )
    asset = AssetDefinition(
        name="沙发", asset_level="object", state="draft",
        scene_type="house", object_type="house/room/furniture/sofa",
    )
    session.add_all([scene, asset])
    await session.flush()

    instance = AssetInstance(
        definition_id=asset.id,
        scene_id=scene.id,
        position=[1.0, 0.0, 2.0],
        rotation=[0.0, 0.0, 0.0, 1.0],
        scale=[1.0, 1.0, 1.0],
    )
    session.add(instance)
    await session.commit()
    assert instance.scene_id == scene.id
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_asset.py -v
# 预期：FAIL - ImportError: cannot import name 'AssetDefinition'
```

- [ ] **Step 3: 实现 jiajia/models/asset.py**

```python
# jiajia/models/asset.py
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from jiajia.db.base import Base

def _now() -> datetime:
    return datetime.now(timezone.utc)

class AssetDefinition(Base):
    __tablename__ = "asset_definition"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    asset_level: Mapped[str] = mapped_column(
        Enum("object", "group", "zone", "scene", name="asset_level_enum"),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        Enum("draft", "published", "deprecated", name="asset_state_enum"),
        default="draft", nullable=False,
    )
    scene_type: Mapped[Optional[str]] = mapped_column(String(64))
    object_type: Mapped[Optional[str]] = mapped_column(String(256))
    role_hints: Mapped[Optional[list]] = mapped_column(JSONB)
    style: Mapped[Optional[str]] = mapped_column(String(128))
    tags: Mapped[Optional[list]] = mapped_column(JSONB)
    source: Mapped[Optional[dict]] = mapped_column(JSONB)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    packaged_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    layout: Mapped[Optional[dict]] = mapped_column(JSONB)
    light: Mapped[Optional[dict]] = mapped_column(JSONB)
    computed_features: Mapped[Optional[dict]] = mapped_column(JSONB)
    metadata_extra: Mapped[Optional[dict]] = mapped_column(JSONB)  # 预留扩展

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    # canonical_children: scene_id=None 的实例，代表默认排列模板
    canonical_children: Mapped[list["AssetInstance"]] = relationship(
        "AssetInstance",
        primaryjoin="and_(AssetInstance.definition_id==AssetDefinition.id, "
                    "AssetInstance.scene_id==None)",
        foreign_keys="AssetInstance.definition_id",
        viewonly=True,
    )

    # commerce: 一对一关系
    commerce: Mapped[Optional["CommerceMetadata"]] = relationship(
        "CommerceMetadata",
        back_populates="asset",
        uselist=False,
    )


class AssetInstance(Base):
    __tablename__ = "asset_instance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_definition.id"),
        nullable=False,
    )
    # scene_id=None → canonical_children（模板）
    # scene_id 有值 → 场景中的实际实例，始终指向根场景 AssetDefinition.id
    scene_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_definition.id"),
        nullable=True,
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_instance.id"),
        nullable=True,
    )
    position: Mapped[Optional[list]] = mapped_column(JSONB)   # [x, y, z]，Y-up
    rotation: Mapped[Optional[list]] = mapped_column(JSONB)   # [qx, qy, qz, qw]
    scale: Mapped[Optional[list]] = mapped_column(JSONB)      # [sx, sy, sz]
    group_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    role: Mapped[Optional[str]] = mapped_column(String(128))
    overrides: Mapped[Optional[dict]] = mapped_column(JSONB)

    definition: Mapped["AssetDefinition"] = relationship(
        "AssetDefinition",
        foreign_keys=[definition_id],
        overlaps="canonical_children",
    )


# 延迟导入避免循环引用
from jiajia.models.commerce import CommerceMetadata  # noqa: E402
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_asset.py -v
# 预期：3 passed
```

- [ ] **Step 5: Commit**

```bash
git add jiajia/models/asset.py tests/test_asset.py
git commit -m "feat: add AssetDefinition and AssetInstance ORM models"
```

---

## Task 4：商业化 ORM 模型

**Files:**
- Create: `jiajia/models/commerce.py`
- Create: `tests/test_commerce.py`

- [ ] **Step 1: 写 tests/test_commerce.py（先写测试）**

```python
# tests/test_commerce.py
import pytest
from sqlalchemy import select
from jiajia.models.asset import AssetDefinition
from jiajia.models.commerce import CommerceMetadata, Listing, PlatformConfig

async def test_create_commerce_metadata(session):
    asset = AssetDefinition(
        name="测试资产", asset_level="object", state="draft",
        scene_type="house", object_type="house/room/furniture/chair",
    )
    session.add(asset)
    await session.flush()

    commerce = CommerceMetadata(
        asset_id=asset.id,
        owner_id=asset.id,
        version="1.0.0",
        license_tradeable=False,
        license_partial=False,
        license_transferable=False,
        credit_total=0,
        credit_final=0,
    )
    session.add(commerce)
    await session.commit()
    assert commerce.id is not None

async def test_asset_commerce_relationship(session):
    """通过 asset.commerce 可直接访问商业化元数据"""
    asset = AssetDefinition(
        name="关系测试", asset_level="object", state="draft",
        scene_type="house", object_type="house/room/furniture/sofa",
    )
    session.add(asset)
    await session.flush()

    commerce = CommerceMetadata(
        asset_id=asset.id, owner_id=asset.id, version="1.0.0",
        license_tradeable=True, license_partial=False,
        license_transferable=False, credit_total=100, credit_final=100,
    )
    session.add(commerce)
    await session.commit()
    await session.refresh(asset)

    assert asset.commerce is not None
    assert asset.commerce.credit_final == 100

async def test_platform_config(session):
    config = PlatformConfig(exchange_rate=100, revenue_share=0.20, currency="CNY")
    session.add(config)
    await session.commit()
    assert config.id is not None

async def test_create_listing(session):
    asset = AssetDefinition(
        name="上架资产", asset_level="object", state="published",
        scene_type="house", object_type="house/room/furniture/sofa",
    )
    session.add(asset)
    await session.flush()

    listing = Listing(
        title="现代布艺沙发",
        type="asset",
        targets=[{"asset_id": str(asset.id), "asset_level": "object"}],
        credit_price=50,
        license_type="non_exclusive",
        transferable=False,
        listed=True,
    )
    session.add(listing)
    await session.commit()
    assert listing.id is not None
    assert listing.listed is True
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_commerce.py -v
# 预期：FAIL - ImportError
```

- [ ] **Step 3: 实现 jiajia/models/commerce.py**

```python
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
    targets: Mapped[Optional[list]] = mapped_column(JSONB)    # [{asset_id, asset_level}]
    ip_bundle: Mapped[Optional[dict]] = mapped_column(JSONB)  # {name, cover_id, asset_ids}
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
    # 历史版本链：[AssetDefinition.id, ...] 存 JSONB，P0 阶段不单独建版本历史表
    version_history: Mapped[Optional[list]] = mapped_column(JSONB)

    watermark_id: Mapped[Optional[str]] = mapped_column(String(256))
    watermark_method: Mapped[Optional[str]] = mapped_column(String(32))
    watermark_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    license_tradeable: Mapped[bool] = mapped_column(Boolean, default=False)
    license_partial: Mapped[bool] = mapped_column(Boolean, default=False)
    license_transferable: Mapped[bool] = mapped_column(Boolean, default=False)

    # Credit 中间维度（算法写入，JSONB）
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_commerce.py -v
# 预期：4 passed
```

- [ ] **Step 5: Commit**

```bash
git add jiajia/models/commerce.py tests/test_commerce.py
git commit -m "feat: add CommerceMetadata, Listing, PlatformConfig models"
```

---

## Task 5：Sample 模型（pgvector）

**Files:**
- Create: `jiajia/models/sample.py`
- Create: `tests/test_sample.py`

- [ ] **Step 1: 写 tests/test_sample.py（先写测试）**

```python
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_sample.py -v
# 预期：FAIL - ImportError
```

- [ ] **Step 3: 实现 jiajia/models/sample.py**

```python
# jiajia/models/sample.py
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from jiajia.db.base import Base

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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_sample.py -v
# 预期：2 passed
```

- [ ] **Step 5: Commit**

```bash
git add jiajia/models/sample.py tests/test_sample.py
git commit -m "feat: add Sample model with pgvector columns"
```

---

## Task 6：Composition ORM 模型

**Files:**
- Create: `jiajia/models/composition.py`
- Create: `tests/test_composition.py`

- [ ] **Step 1: 写 tests/test_composition.py（先写测试）**

```python
# tests/test_composition.py
from jiajia.models.asset import AssetDefinition
from jiajia.models.composition import GroupInstance, Region

async def test_create_group_instance(session):
    scene = AssetDefinition(
        name="测试场景", asset_level="scene", state="draft",
        scene_type="house", object_type="house",
    )
    session.add(scene)
    await session.flush()

    gi = GroupInstance(
        definition_code=100001,
        scene_id=scene.id,
        position=[0.0, 0.0, 0.0],
        rotation=[0.0, 0.0, 0.0, 1.0],
        scale=[1.0, 1.0, 1.0],
        role_assignments=[],
    )
    session.add(gi)
    await session.commit()
    assert gi.id is not None
    assert gi.definition_code == 100001

async def test_create_region(session):
    scene = AssetDefinition(
        name="测试场景2", asset_level="scene", state="draft",
        scene_type="house", object_type="house",
    )
    session.add(scene)
    await session.flush()

    region = Region(
        scene_id=scene.id,
        type="会客区",
        boundary=[[0, 0, 0], [3, 0, 0], [3, 0, 3], [0, 0, 3]],
        groups=[],
    )
    session.add(region)
    await session.commit()
    assert region.id is not None
    assert region.type == "会客区"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_composition.py -v
# 预期：FAIL - ImportError
```

- [ ] **Step 3: 实现 jiajia/models/composition.py**

```python
# jiajia/models/composition.py
import uuid
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from jiajia.db.base import Base

class GroupInstance(Base):
    __tablename__ = "group_instance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # GroupDefinition 存于 JSON 配置，用 code（int）作引用键
    definition_code: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_definition.id")
    )
    position: Mapped[Optional[list]] = mapped_column(JSONB)
    rotation: Mapped[Optional[list]] = mapped_column(JSONB)
    scale: Mapped[Optional[list]] = mapped_column(JSONB)
    role_assignments: Mapped[Optional[list]] = mapped_column(JSONB)


class Region(Base):
    __tablename__ = "region"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scene_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_definition.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(128), nullable=False)
    boundary: Mapped[Optional[list]] = mapped_column(JSONB)
    groups: Mapped[Optional[list]] = mapped_column(JSONB)
    partition_vector: Mapped[Optional[list]] = mapped_column(JSONB)
    distribution_vector: Mapped[Optional[dict]] = mapped_column(JSONB)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_composition.py -v
# 预期：2 passed
```

- [ ] **Step 5: Commit**

```bash
git add jiajia/models/composition.py tests/test_composition.py
git commit -m "feat: add GroupInstance and Region models"
```

---

## Task 7：Alembic 迁移

**Files:**
- Create: `migrations/env.py`
- Create: `alembic.ini`

- [ ] **Step 1: 初始化 Alembic**

```bash
uv run alembic init migrations
```

- [ ] **Step 2: 配置 migrations/env.py（关键部分替换）**

```python
# migrations/env.py 顶部添加
import os
from dotenv import load_dotenv
from jiajia.db.base import Base
from jiajia.models import asset, commerce, sample, composition  # noqa: F401

load_dotenv()
target_metadata = Base.metadata

def get_url():
    return os.getenv("DATABASE_URL_SYNC", "")
```

在 `run_migrations_offline` 和 `run_migrations_online` 中用 `get_url()` 替换默认的 `config.get_main_option("sqlalchemy.url")`。

- [ ] **Step 3: 生成初始迁移**

```bash
uv run alembic revision --autogenerate -m "initial"
# 预期：生成 migrations/versions/xxxx_initial.py，包含所有表
```

- [ ] **Step 4: 执行迁移**

```bash
uv run alembic upgrade head
# 预期：所有表创建成功，无报错
```

- [ ] **Step 5: 确认表已创建**

```bash
psql jiajia -c "\dt"
# 预期：asset_definition, asset_instance, commerce_metadata,
#       listing, platform_config, sample, group_instance, region
```

- [ ] **Step 6: 为向量列创建索引**

```sql
-- psql jiajia 中执行
CREATE INDEX sample_style_vector_idx
  ON sample USING ivfflat (style_vector vector_l2_ops)
  WITH (lists = 100);
CREATE INDEX sample_partition_vector_idx
  ON sample USING ivfflat (partition_vector vector_l2_ops)
  WITH (lists = 100);
```

- [ ] **Step 7: Commit**

```bash
git add migrations/ alembic.ini
git commit -m "feat: add alembic migrations for full schema"
```

---

## Task 8：Repository 层

**Files:**
- Create: `jiajia/repositories/asset.py`
- Create: `jiajia/repositories/commerce.py`
- Create: `jiajia/repositories/sample.py`

- [ ] **Step 1: 为 AssetRepository 写测试（先写）**

```python
# tests/test_asset.py 末尾追加
from jiajia.repositories.asset import AssetRepository

async def test_asset_repo_create_and_get(session):
    repo = AssetRepository(session)
    asset = await repo.create(
        name="布艺沙发", asset_level="object", state="draft",
        scene_type="house", object_type="house/room/furniture/sofa",
    )
    fetched = await repo.get(asset.id)
    assert fetched.name == "布艺沙发"

async def test_asset_repo_publish(session):
    repo = AssetRepository(session)
    asset = await repo.create(
        name="木椅", asset_level="object", state="draft",
        scene_type="house", object_type="house/room/furniture/chair",
    )
    published = await repo.publish(
        asset.id,
        usd_url="oss://packaged/chair.usda",
        gltf_url="oss://packaged/chair.gltf",
    )
    assert published.state == "published"
    assert published.packaged_data["usd_url"] == "oss://packaged/chair.usda"

async def test_asset_repo_deprecate_blocks_new_instance(session):
    """废弃资产后，repository 拒绝为其创建新实例"""
    repo = AssetRepository(session)
    asset = await repo.create(
        name="废弃资产", asset_level="object", state="draft",
        scene_type="house", object_type="house/room/furniture/rug",
    )
    await repo.publish(asset.id, usd_url="oss://x.usda", gltf_url="oss://x.gltf")
    await repo.deprecate(asset.id)

    import pytest
    with pytest.raises(ValueError, match="deprecated"):
        await repo.create_instance(asset.id, scene_id=asset.id)

async def test_asset_repo_list_by_scene_type(session):
    repo = AssetRepository(session)
    await repo.create(name="A", asset_level="object", state="draft",
                      scene_type="urban", object_type="urban/build")
    await repo.create(name="B", asset_level="object", state="draft",
                      scene_type="urban", object_type="urban/road")
    results = await repo.list_by_scene_type("urban")
    assert len(results) >= 2
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_asset.py::test_asset_repo_create_and_get -v
# 预期：FAIL - ImportError
```

- [ ] **Step 3: 实现 repositories/asset.py**

```python
# jiajia/repositories/asset.py
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jiajia.models.asset import AssetDefinition, AssetInstance

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
```

- [ ] **Step 4: 为 SampleRepository 写测试（先写）**

```python
# tests/test_sample.py 末尾追加
from jiajia.repositories.sample import SampleRepository
from jiajia.models.sample import STYLE_VECTOR_DIM, PARTITION_VECTOR_DIM

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
```

- [ ] **Step 5: 实现 repositories/sample.py**

```python
# jiajia/repositories/sample.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jiajia.models.sample import Sample

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
```

- [ ] **Step 6: 为 CommerceRepository 写测试（先写）**

```python
# tests/test_commerce.py 末尾追加
from jiajia.repositories.commerce import CommerceRepository, ListingRepository

async def test_commerce_repo_create(session):
    asset = AssetDefinition(
        name="仓库测试", asset_level="object", state="draft",
        scene_type="house", object_type="house/room/furniture/bed",
    )
    session.add(asset)
    await session.flush()

    repo = CommerceRepository(session)
    commerce = await repo.create(
        asset_id=asset.id, owner_id=asset.id,
        license_tradeable=True, license_partial=False,
        license_transferable=False, credit_total=200, credit_final=200,
    )
    assert commerce.credit_final == 200

async def test_listing_repo_create_and_list(session):
    repo = ListingRepository(session)
    listing = await repo.create(
        title="测试上架", type="asset", credit_price=30,
        license_type="non_exclusive", transferable=False, listed=True,
    )
    listed = await repo.list_active()
    assert any(l.id == listing.id for l in listed)
```

- [ ] **Step 7: 实现 repositories/commerce.py**

```python
# jiajia/repositories/commerce.py
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jiajia.models.commerce import CommerceMetadata, Listing

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
```

- [ ] **Step 8: 运行所有测试确认通过**

```bash
uv run pytest tests/ -v
# 预期：全部通过
```

- [ ] **Step 9: Commit**

```bash
git add jiajia/repositories/ tests/
git commit -m "feat: add repository layer with CRUD, vector search, and deprecation guard"
```

---

## Task 9：Pydantic Schemas（验证层）

**Files:**
- Create: `jiajia/schemas/asset.py`
- Create: `jiajia/schemas/commerce.py`
- Create: `jiajia/schemas/composition.py`
- Create: `tests/test_schemas.py`

- [ ] **Step 1: 写 tests/test_schemas.py（先写测试）**

```python
# tests/test_schemas.py
import uuid
import pytest
from pydantic import ValidationError
from jiajia.schemas.asset import AssetDefinitionCreate, AssetInstanceCreate
from jiajia.schemas.commerce import CommerceMetadataRead, ListingCreate

def test_asset_definition_create_valid():
    data = AssetDefinitionCreate(
        name="测试资产",
        asset_level="object",
        scene_type="house",
        object_type="house/room/furniture/sofa",
        style="现代简约",
        tags=["沙发", "布艺"],
    )
    assert data.asset_level == "object"

def test_asset_definition_create_invalid_level():
    with pytest.raises(ValidationError):
        AssetDefinitionCreate(
            name="测试", asset_level="invalid_level",
            scene_type="house", object_type="house/room",
        )

def test_asset_instance_scene_id_nullable():
    instance = AssetInstanceCreate(
        definition_id=uuid.uuid4(),
        position=[0.0, 0.0, 0.0],
        rotation=[0.0, 0.0, 0.0, 1.0],
        scale=[1.0, 1.0, 1.0],
        scene_id=None,
    )
    assert instance.scene_id is None

def test_listing_create_valid():
    listing = ListingCreate(
        title="现代沙发",
        type="asset",
        credit_price=50,
        license_type="non_exclusive",
        transferable=False,
    )
    assert listing.credit_price == 50

def test_listing_create_negative_price():
    with pytest.raises(ValidationError):
        ListingCreate(
            title="错误定价", type="asset",
            credit_price=-10,
            license_type="non_exclusive", transferable=False,
        )
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_schemas.py -v
# 预期：FAIL - ImportError
```

- [ ] **Step 3: 实现 schemas/asset.py**

```python
# jiajia/schemas/asset.py
import uuid
from typing import Literal, Optional
from pydantic import BaseModel

AssetLevel = Literal["object", "group", "zone", "scene"]
AssetState = Literal["draft", "published", "deprecated"]

class AssetDefinitionCreate(BaseModel):
    name: str
    asset_level: AssetLevel
    scene_type: Optional[str] = None
    object_type: Optional[str] = None
    role_hints: Optional[list[str]] = None
    style: Optional[str] = None
    tags: Optional[list[str]] = None
    source: Optional[dict] = None

class AssetDefinitionRead(AssetDefinitionCreate):
    id: uuid.UUID
    state: AssetState
    model_config = {"from_attributes": True}

class AssetInstanceCreate(BaseModel):
    definition_id: uuid.UUID
    position: Optional[list[float]] = None
    rotation: Optional[list[float]] = None
    scale: Optional[list[float]] = None
    scene_id: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = None
    role: Optional[str] = None
    overrides: Optional[dict] = None
```

- [ ] **Step 4: 实现 schemas/commerce.py**

```python
# jiajia/schemas/commerce.py
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
```

- [ ] **Step 5: 实现 schemas/composition.py**

```python
# jiajia/schemas/composition.py
import uuid
from typing import Optional
from pydantic import BaseModel

class GroupInstanceCreate(BaseModel):
    definition_code: int
    scene_id: Optional[uuid.UUID] = None
    position: Optional[list[float]] = None
    rotation: Optional[list[float]] = None
    scale: Optional[list[float]] = None
    role_assignments: Optional[list[dict]] = None

class RegionCreate(BaseModel):
    scene_id: uuid.UUID
    type: str
    boundary: Optional[list[list[float]]] = None
    groups: Optional[list[uuid.UUID]] = None
```

- [ ] **Step 6: 运行测试确认通过**

```bash
uv run pytest tests/test_schemas.py -v
# 预期：5 passed
```

- [ ] **Step 7: Commit**

```bash
git add jiajia/schemas/ tests/test_schemas.py
git commit -m "feat: add Pydantic v2 schemas for validation layer"
```

---

## Task 10：Spatial Composition JSON 配置体系

**Files:**
- Create: `jiajia/config/schemas.py`
- Create: `jiajia/config/loader.py`
- Create: `jiajia/data/groups/house.json`
- Create: `tests/test_config.py`

- [ ] **Step 1: 写 tests/test_config.py（先写测试）**

```python
# tests/test_config.py
import pytest
from pathlib import Path
from jiajia.config.loader import load_group_configs, get_groups_for_scene, get_group_by_code

DATA_DIR = Path(__file__).parent.parent / "jiajia" / "data" / "groups"

def test_load_house_groups():
    configs = load_group_configs(DATA_DIR)
    assert "house" in configs
    assert len(configs["house"]) > 0

def test_get_meeting_group():
    load_group_configs(DATA_DIR)
    group = get_group_by_code("house", 100001)
    assert group is not None
    assert group.name == "会客组"
    assert group.anchor_role == "sofa"

def test_role_tiers():
    load_group_configs(DATA_DIR)
    group = get_group_by_code("house", 100001)
    roles = {r.name: r for r in group.roles}
    assert roles["sofa"].tier == "anchor"
    assert roles["sofa"].optional is False
    assert roles["coffee_table"].optional is True

def test_cache_is_populated_after_load():
    """加载后缓存应已填充，不需要传 data_dir 也能查到"""
    group = get_group_by_code("house", 100001)
    assert group is not None
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_config.py -v
# 预期：FAIL - ImportError
```

- [ ] **Step 3: 实现 config/schemas.py**

```python
# jiajia/config/schemas.py
from typing import Optional
from pydantic import BaseModel

class SizeRange(BaseModel):
    w: list[float]
    h: list[float]
    d: list[float]

class RoleDefinition(BaseModel):
    name: str
    tier: str
    asset_types: list[str]
    count: list[int]
    size_range: Optional[SizeRange] = None
    optional: bool = False

class Placement(BaseModel):
    role: str
    position: dict
    rotation: dict
    count: list[int]

class Template(BaseModel):
    id: str
    name: str
    placement_mode: str
    sequence: list[str]
    placements: list[Placement]
    total_count: int  # 所有角色 count.max 之和的上限，用于资源预算

class GroupDefinition(BaseModel):
    id: str
    name: str
    code: int
    scene_types: list[str]
    anchor_role: str
    roles: list[RoleDefinition]
    templates: list[Template]

class GroupConfigFile(BaseModel):
    scene_type: str
    groups: list[GroupDefinition]
```

- [ ] **Step 4: 实现 config/loader.py**

```python
# jiajia/config/loader.py
import json
from pathlib import Path
from jiajia.config.schemas import GroupConfigFile, GroupDefinition

_DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data" / "groups"
_group_cache: dict[str, list[GroupDefinition]] = {}

def load_group_configs(
    data_dir: Path = _DEFAULT_DATA_DIR,
    force_reload: bool = False,
) -> dict[str, list[GroupDefinition]]:
    global _group_cache
    if _group_cache and not force_reload:
        return _group_cache

    _group_cache.clear()
    for json_file in data_dir.glob("*.json"):
        raw = json.loads(json_file.read_text(encoding="utf-8"))
        config = GroupConfigFile(**raw)
        _group_cache[config.scene_type] = config.groups

    return _group_cache

def get_groups_for_scene(scene_type: str) -> list[GroupDefinition]:
    cache = _group_cache if _group_cache else load_group_configs()
    return cache.get(scene_type, [])

def get_group_by_code(scene_type: str, code: int) -> GroupDefinition | None:
    for group in get_groups_for_scene(scene_type):
        if group.code == code:
            return group
    return None
```

- [ ] **Step 5: 创建 house.json**

```json
{
  "scene_type": "house",
  "groups": [
    {
      "id": "house-meeting",
      "name": "会客组",
      "code": 100001,
      "scene_types": ["house"],
      "anchor_role": "sofa",
      "roles": [
        {
          "name": "sofa",
          "tier": "anchor",
          "asset_types": ["house/room/furniture/sofa"],
          "count": [1, 1],
          "size_range": {"w": [0.8, 8.0], "h": [0.4, 5.0], "d": [0.0, 5.0]},
          "optional": false
        },
        {
          "name": "coffee_table",
          "tier": "support",
          "asset_types": ["house/room/furniture/table/coffee"],
          "count": [0, 2],
          "size_range": {"w": [0.4, 5.0], "h": [0.4, 5.0], "d": [0.0, 1.5]},
          "optional": true
        },
        {
          "name": "rug",
          "tier": "fill",
          "asset_types": ["house/room/furniture/rug"],
          "count": [0, 1],
          "optional": true
        },
        {
          "name": "accessory",
          "tier": "accent",
          "asset_types": ["house/room/furniture/accessory"],
          "count": [0, 4],
          "optional": true
        }
      ],
      "templates": [
        {
          "id": "house-meeting-standard",
          "name": "标准会客",
          "placement_mode": "deterministic",
          "sequence": ["sofa", "coffee_table", "rug", "accessory"],
          "placements": [
            {
              "role": "coffee_table",
              "position": {"relative": [0.0, 0.0, 1.5], "range": [[-0.5, 0.5], [0.0, 0.0], [0.8, 2.0]]},
              "rotation": {"fixed": 0.0},
              "count": [0, 1]
            },
            {
              "role": "rug",
              "position": {"relative": [0.0, 0.0, 0.8], "range": [[-0.5, 0.5], [0.0, 0.0], [-0.5, 1.5]]},
              "rotation": {"fixed": 0.0},
              "count": [0, 1]
            }
          ],
          "total_count": 6
        }
      ]
    }
  ]
}
```

- [ ] **Step 6: 运行测试确认通过**

```bash
uv run pytest tests/test_config.py -v
# 预期：4 passed
```

- [ ] **Step 7: Commit**

```bash
git add jiajia/config/ jiajia/data/ tests/test_config.py
git commit -m "feat: add Spatial Composition JSON config system"
```

---

## Task 11：端到端集成验证

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: 写 tests/test_integration.py**

```python
# tests/test_integration.py
"""
端到端验证：沙发资产从创建 → 发布 → 商业化 → Sample 入库 → 向量搜索
"""
from jiajia.repositories.asset import AssetRepository
from jiajia.repositories.commerce import CommerceRepository, ListingRepository
from jiajia.repositories.sample import SampleRepository
from jiajia.config.loader import get_group_by_code
from jiajia.models.sample import STYLE_VECTOR_DIM, PARTITION_VECTOR_DIM
import pytest

async def test_full_asset_lifecycle(session):
    asset_repo = AssetRepository(session)
    commerce_repo = CommerceRepository(session)
    listing_repo = ListingRepository(session)
    sample_repo = SampleRepository(session)

    # 1. 创建草稿资产
    asset = await asset_repo.create(
        name="现代布艺沙发",
        asset_level="object",
        state="draft",
        scene_type="house",
        object_type="house/room/furniture/sofa",
        style="现代简约",
        tags=["沙发", "布艺"],
        source={"type": "manual", "ref": "设计师手工建模"},
        raw_data={"geometry_url": "oss://raw/sofa_001.obj"},
    )
    assert asset.state == "draft"

    # 2. 发布
    published = await asset_repo.publish(
        asset.id,
        usd_url="oss://packaged/sofa_001.usda",
        gltf_url="oss://packaged/sofa_001.gltf",
    )
    assert published.state == "published"

    # 3. 创建商业化元数据
    commerce = await commerce_repo.create(
        asset_id=asset.id,
        owner_id=asset.id,
        version="1.0.0",
        license_tradeable=True,
        license_partial=True,
        license_transferable=False,
        credit_total=120,
        credit_final=120,
    )
    assert commerce.credit_final == 120

    # 4. 创建 Listing 并上架
    listing = await listing_repo.create(
        title="现代布艺沙发",
        type="asset",
        targets=[{"asset_id": str(asset.id), "asset_level": "object"}],
        credit_price=50,
        license_type="non_exclusive",
        transferable=False,
        listed=True,
    )
    active = await listing_repo.list_active()
    assert any(l.id == listing.id for l in active)

    # 5. 废弃后无法创建新实例
    await asset_repo.deprecate(asset.id)
    with pytest.raises(ValueError, match="deprecated"):
        await asset_repo.create_instance(asset.id, scene_id=None)

    # 6. Sample 入库 + 向量相似搜索
    await sample_repo.create(
        scene_type="house", sample_level="zone", style="现代简约",
        score=88,
        style_vector=[0.9] + [0.0] * (STYLE_VECTOR_DIM - 1),
        partition_vector=[0.5] * PARTITION_VECTOR_DIM,
    )
    results = await sample_repo.search_by_style(
        query_vector=[0.9] + [0.0] * (STYLE_VECTOR_DIM - 1),
        scene_type="house", sample_level="zone",
    )
    assert len(results) > 0
    assert results[0].style == "现代简约"

    # 7. JSON 配置可用
    group = get_group_by_code("house", 100001)
    assert group.anchor_role == "sofa"
```

- [ ] **Step 2: 运行完整测试套件**

```bash
uv run pytest tests/ -v --cov=jiajia --cov-report=term-missing
# 预期：全部通过，覆盖率 > 75%
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration test for P0 lifecycle"
```

---

## 验证清单

P0 实施完成后，以下全部满足：

- [ ] `uv run pytest tests/ -v` 全部通过
- [ ] `uv run alembic upgrade head` 无报错，8 张表存在
- [ ] `get_group_by_code("house", 100001)` 返回会客组配置
- [ ] draft → published → deprecated 状态流转正确
- [ ] deprecated 资产无法创建新 Instance（ValueError）
- [ ] Sample 向量搜索返回最相似结果（L2 距离）
- [ ] Pydantic schema 拒绝非法 asset_level 和负数 credit_price
- [ ] `asset.commerce` 关系可直接访问商业化元数据
- [ ] `asset.canonical_children` 只返回 scene_id=None 的实例
