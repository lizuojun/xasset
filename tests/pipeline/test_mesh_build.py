# tests/pipeline/test_mesh_build.py
import pytest
from xasset.pipeline.stages.mesh_utils import check_poly_clock, ear_cut_triangulation, build_polygon_mesh


def test_check_poly_clock_ccw():
    poly = [[0, 0], [1, 0], [1, 1], [0, 1]]
    assert check_poly_clock(poly) == False  # CCW


def test_check_poly_clock_cw():
    poly = [[0, 0], [0, 1], [1, 1], [1, 0]]
    assert check_poly_clock(poly) == True  # CW


def test_ear_cut_square():
    poly = [[0, 0], [1, 0], [1, 1], [0, 1]]
    tris = ear_cut_triangulation(poly)
    assert len(tris) == 2
    for tri in tris:
        assert len(tri) == 3


def test_ear_cut_triangle():
    poly = [[0, 0], [1, 0], [0.5, 1]]
    tris = ear_cut_triangulation(poly)
    assert len(tris) == 1
    assert len(tris[0]) == 3


def test_build_polygon_mesh_square():
    poly_3d = [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]]
    normal = [0, 1, 0]
    verts, faces = build_polygon_mesh(poly_3d, normal)
    assert len(verts) == 4
    assert len(faces) == 2


from xasset.pipeline.stages.uv_utils import compute_wall_uv, map_uv_planar


def test_compute_wall_uv_simple():
    verts = [[0, 0, 0], [2, 0, 0], [2, 3, 0], [0, 3, 0]]
    uvs = compute_wall_uv(verts, u_axis=[1, 0, 0], v_axis=[0, 1, 0])
    assert len(uvs) == 4
    assert uvs[0] == pytest.approx([0.0, 0.0], abs=1e-5)
    assert uvs[1] == pytest.approx([2.0, 0.0], abs=1e-5)
    assert uvs[3] == pytest.approx([0.0, 3.0], abs=1e-5)


def test_map_uv_planar_floor():
    verts = [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]]
    uvs = map_uv_planar(verts, normal=[0, 1, 0])
    assert len(uvs) == 4
    # floor: U=X, V=Z
    assert uvs[0] == pytest.approx([0.0, 0.0], abs=1e-5)
    assert uvs[2] == pytest.approx([1.0, 1.0], abs=1e-5)


def test_map_uv_planar_wall_z():
    verts = [[0, 0, 2], [1, 0, 2], [1, 2, 2], [0, 2, 2]]
    uvs = map_uv_planar(verts, normal=[0, 0, 1])
    assert len(uvs) == 4
    # wall facing Z: U=X, V=Y
    assert uvs[0] == pytest.approx([0.0, 0.0], abs=1e-5)
    assert uvs[2] == pytest.approx([1.0, 2.0], abs=1e-5)


from xasset.pipeline.stages.mesh_build import (
    Opening, SubMesh, WallSegmentMesh, RegionGeometry, SceneMesh,
    MeshBuildOutput, MeshBuilderService, WALL_THICKNESS_DEFAULT,
)
from xasset.pipeline.stages.scene_understand import SceneRegion, DoorInfo


# ---- 数据结构测试 ----

def test_opening_fields():
    o = Opening(opening_type="door", u_start=0.5, u_end=1.5,
                bottom_y=0.0, top_y=2.1, opening_id="d1")
    assert o.opening_type == "door"
    assert o.u_end == 1.5


def test_submesh_fields():
    sm = SubMesh(role="floor", region_id="r0",
                 vertices=[], normals=[], uvs=[], faces=[])
    assert sm.role == "floor"


def test_scene_mesh_fields():
    sm = SceneMesh(regions=[], floor_offset=0.0)
    assert sm.floor_offset == 0.0


# ---- MeshBuilderService 测试 ----

def _make_square_region():
    return SceneRegion(
        region_type="living_room",
        boundary=[[0, 0], [4, 0], [4, 3], [0, 3]],
        area=12.0,
        height=2.8,
    )


def test_floor_mesh_generated():
    svc = MeshBuilderService()
    region = _make_square_region()
    geom = svc._build_region_geometry(region, region_id="r0",
                                    wall_thickness=WALL_THICKNESS_DEFAULT,
                                    floor_offset=0.0)
    assert geom.floor is not None
    assert geom.floor.role == "floor"
    assert len(geom.floor.vertices) >= 3
    assert len(geom.floor.faces) >= 1


def test_ceiling_mesh_generated():
    svc = MeshBuilderService()
    region = _make_square_region()
    geom = svc._build_region_geometry(region, region_id="r0",
                                    wall_thickness=WALL_THICKNESS_DEFAULT,
                                    floor_offset=0.0)
    assert geom.ceiling is not None
    ceil_ys = [v[1] for v in geom.ceiling.vertices]
    assert all(abs(y - 2.8) < 1e-5 for y in ceil_ys)


def test_walls_generated():
    svc = MeshBuilderService()
    region = _make_square_region()
    geom = svc._build_region_geometry(region, region_id="r0",
                                    wall_thickness=WALL_THICKNESS_DEFAULT,
                                    floor_offset=0.0)
    assert len(geom.walls) == 4
    roles = {sm.role for w in geom.walls for sm in w.submeshes}
    assert "wall_inner" in roles
    assert "wall_outer" in roles


def test_door_creates_notch():
    """有门的墙段，inner face 顶点数应多于无门墙段。"""
    region = SceneRegion(
        region_type="living_room",
        boundary=[[0, 0], [4, 0], [4, 3], [0, 3]],
        area=12.0, height=2.8,
        doors=[DoorInfo(
            id="d1",
            pts=[[1, 0], [2, 0], [2, 0], [1, 0]],
            normal=[0, 1], center=[1.5, 0], width=1.0, height=2.1,
            to_room=None,
        )],
    )
    svc = MeshBuilderService()
    geom = svc._build_region_geometry(region, "r0", WALL_THICKNESS_DEFAULT, 0.0)
    wall_0 = geom.walls[0]  # edge [0,0]->[4,0]，有门
    wall_1 = geom.walls[1]  # edge [4,0]->[4,3]，无门
    inner_0 = next(s for s in wall_0.submeshes if s.role == "wall_inner")
    inner_1 = next(s for s in wall_1.submeshes if s.role == "wall_inner")
    assert len(inner_0.vertices) > len(inner_1.vertices)


from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.mesh_build import MeshBuildStage, MeshBuildOutput
from xasset.pipeline.stages.scene_understand import SceneUnderstandStage


def test_mesh_build_stage_runs():
    import uuid
    ctx = PipelineContext(
        job_id=str(uuid.uuid4()),
        input=PipelineInput(input_type="text", scene_type="house"),
    )
    SceneUnderstandStage().run(ctx)
    MeshBuildStage().run(ctx)
    assert "geometry" in ctx.stage_outputs
    out = ctx.stage_outputs["geometry"]
    assert isinstance(out, MeshBuildOutput)
    assert out.scene_type == "house"
    assert len(out.scene_mesh.regions) > 0


def test_mesh_build_output_has_floor_and_walls():
    import uuid
    ctx = PipelineContext(
        job_id=str(uuid.uuid4()),
        input=PipelineInput(input_type="text", scene_type="house"),
    )
    SceneUnderstandStage().run(ctx)
    MeshBuildStage().run(ctx)
    region = ctx.stage_outputs["geometry"].scene_mesh.regions[0]
    assert region.floor is not None
    assert region.ceiling is not None
    assert len(region.walls) > 0
