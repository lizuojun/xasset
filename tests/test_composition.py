# tests/test_composition.py
from xasset.models.asset import AssetDefinition
from xasset.models.composition import GroupInstance, Region

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
