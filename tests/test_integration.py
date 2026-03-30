# tests/test_integration.py
"""
端到端验证：沙发资产从创建 → 发布 → 商业化 → Sample 入库 → 向量搜索
"""
from jiajia.repositories.asset import AssetRepository
from jiajia.repositories.commerce import CommerceRepository, ListingRepository
from jiajia.repositories.sample import SampleRepository
from jiajia.config.loader import get_group_by_code, load_group_configs
from jiajia.models.sample import STYLE_VECTOR_DIM, PARTITION_VECTOR_DIM
from pathlib import Path
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
    data_dir = Path(__file__).parent.parent / "jiajia" / "data" / "groups"
    load_group_configs(data_dir)
    group = get_group_by_code("house", 100001)
    assert group.anchor_role == "sofa"
