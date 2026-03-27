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
