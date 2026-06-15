# tests/services/test_placement_zone.py
import math
import pytest
from xasset.services.placement_zone import PlacementZoneService, PlacementZone, PlacementZoneResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_box_mesh(w=2.0, h=1.0, d=2.0):
    """Unit box: 6 quads, each split into 2 triangles → 12 faces total.
    Y-up convention.  Bottom face at y=0, top face at y=h.
    """
    # 8 vertices
    verts = [
        [0, 0, 0],  # 0
        [w, 0, 0],  # 1
        [w, 0, d],  # 2
        [0, 0, d],  # 3
        [0, h, 0],  # 4
        [w, h, 0],  # 5
        [w, h, d],  # 6
        [0, h, d],  # 7
    ]
    # 6 faces × 2 triangles each (CCW winding, outward normals)
    faces = [
        # top (y=h, normal +Y)   e1=+Z, e2=+X → cross = +Y
        [4, 7, 6], [4, 6, 5],
        # bottom (y=0, normal -Y) e1=+X, e2=+Z → cross = -Y
        [0, 1, 2], [0, 2, 3],
        # front (z=d, normal +Z)  e1=+X, e2=+Y → cross = +Z
        [2, 6, 7], [2, 7, 3],
        # back (z=0, normal -Z)   e1=+Y, e2=+X → cross = -Z
        [0, 4, 5], [0, 5, 1],
        # right (x=w, normal +X)  e1=+Y, e2=+Z → cross = +X
        [1, 5, 6], [1, 6, 2],
        # left (x=0, normal -X)   e1=+Z, e2=+Y → cross = -X
        [0, 3, 7], [0, 7, 4],
    ]
    return {"vertices": verts, "faces": faces}


def _make_tiny_face_mesh():
    """One big triangle + one tiny triangle (area ~1e-7)."""
    verts = [
        [0, 0, 0],
        [2, 0, 0],
        [0, 0, 2],
        # tiny triangle above
        [0, 1, 0],
        [0.001, 1, 0],
        [0, 1.001, 0],
    ]
    faces = [
        [0, 1, 2],  # big horizontal face, area = 2
        [3, 4, 5],  # tiny face
    ]
    return {"vertices": verts, "faces": faces}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_analyze_simple_box():
    """Box mesh should produce at least one stable_top and stable_side zones."""
    service = PlacementZoneService()
    mesh = _make_box_mesh()
    result = service.analyze("box-001", mesh)

    assert isinstance(result, PlacementZoneResult)
    assert result.asset_id == "box-001"
    assert len(result.zones) > 0

    types_found = {z.zone_type for z in result.zones}
    assert "stable_top" in types_found, f"Expected stable_top but got {types_found}"
    assert "stable_side" in types_found, f"Expected stable_side but got {types_found}"


def test_analyze_returns_cached_result():
    """Second call with same asset_id should return cached result without recomputing."""
    call_count = 0

    class CountingService(PlacementZoneService):
        def _compute_zones(self, mesh_data):
            nonlocal call_count
            call_count += 1
            return super()._compute_zones(mesh_data)

    store = {}
    service = CountingService(asset_store=store)
    mesh = _make_box_mesh()

    result1 = service.analyze("box-001", mesh)
    result2 = service.analyze("box-001", mesh)

    assert call_count == 1, "Should compute only once; second call should use cache"
    assert result1.asset_id == result2.asset_id
    assert len(result1.zones) == len(result2.zones)


def test_stable_top_score_is_highest_for_horizontal_face():
    """A perfectly horizontal face (normal = [0,1,0]) should have stability_score >= 0.9."""
    service = PlacementZoneService()
    mesh = _make_box_mesh()
    result = service.analyze("box-002", mesh)

    top_zones = [z for z in result.zones if z.zone_type == "stable_top"]
    assert top_zones, "No stable_top zones found"

    # Top of the box is a horizontal face — its score should be close to 1.0
    max_score = max(z.stability_score for z in top_zones)
    assert max_score >= 0.9, f"Expected score >= 0.9, got {max_score}"


def test_empty_mesh_returns_empty_zones():
    """Empty mesh (no vertices/faces) should not raise and return empty zones list."""
    service = PlacementZoneService()
    result = service.analyze("empty-001", {"vertices": [], "faces": []})
    assert isinstance(result, PlacementZoneResult)
    assert result.zones == []


def test_analyze_filters_tiny_faces():
    """Faces with area < 0.01 should be excluded from results."""
    service = PlacementZoneService()
    mesh = _make_tiny_face_mesh()
    result = service.analyze("tiny-001", mesh)

    for z in result.zones:
        assert z.area >= 0.01, f"Zone with area {z.area} should have been filtered out"


def test_zone_normal_is_normalized():
    """Every zone's normal vector must have unit length (within 1e-6)."""
    service = PlacementZoneService()
    mesh = _make_box_mesh()
    result = service.analyze("box-003", mesh)

    assert result.zones, "Expected at least one zone"
    for z in result.zones:
        length = math.sqrt(sum(n * n for n in z.normal))
        assert abs(length - 1.0) <= 1e-6, (
            f"Zone {z.zone_type} normal {z.normal} has length {length}, expected 1.0"
        )
