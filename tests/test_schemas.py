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
