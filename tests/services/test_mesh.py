# tests/services/test_mesh.py
import types
from xasset.services.mesh import MeshService, PlacementZones, PlacementSlot


def _make_asset(object_type="house/room/furniture/sofa", computed_features=None, raw_data=None):
    asset = types.SimpleNamespace()
    asset.object_type = object_type
    asset.computed_features = computed_features
    asset.raw_data = raw_data or {}
    return asset


def test_no_geometry_returns_empty_zones():
    service = MeshService()
    asset = _make_asset(raw_data={})
    zones = service.get_placement_zones(asset)
    assert zones.top == []
    assert zones.back == []
    assert zones.front == []


def test_cache_hit_returns_cached_zones():
    service = MeshService()
    cached = {
        "top": [{"surface_type": "top", "center": [0, 80, 0], "size": [60, 0, 40], "height": 80.0}],
        "back": [],
        "front": [],
    }
    asset = _make_asset(computed_features={"placement_zones": cached})
    zones = service.get_placement_zones(asset)
    assert len(zones.top) == 1
    assert zones.top[0].surface_type == "top"
    assert zones.top[0].height == 80.0


def test_force_recompute_bypasses_cache():
    service = MeshService()
    cached = {
        "top": [{"surface_type": "top", "center": [0, 80, 0], "size": [60, 0, 40], "height": 80.0}],
        "back": [],
        "front": [],
    }
    asset = _make_asset(computed_features={"placement_zones": cached})
    # force_recompute=True skips cache; no geometry → empty zones
    zones = service.get_placement_zones(asset, force_recompute=True)
    assert zones.top == []


def test_result_written_to_computed_features():
    service = MeshService()
    asset = _make_asset()
    service.get_placement_zones(asset)
    assert "placement_zones" in asset.computed_features


def test_placement_slot_fields():
    slot = PlacementSlot(surface_type="top", center=[0, 80, 0], size=[60, 0, 40], height=80.0)
    assert slot.surface_type == "top"
    assert slot.height == 80.0
