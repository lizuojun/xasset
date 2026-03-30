# tests/test_commerce.py
import pytest
from sqlalchemy import select
from xasset.models.asset import AssetDefinition
from xasset.models.commerce import CommerceMetadata, Listing, PlatformConfig

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


# 追加到 tests/test_commerce.py 末尾
from xasset.repositories.commerce import CommerceRepository, ListingRepository

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
