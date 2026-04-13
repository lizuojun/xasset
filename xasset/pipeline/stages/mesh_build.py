# xasset/pipeline/stages/mesh_build.py
"""MeshBuildStage: converts SceneUnderstandOutput into renderable scene mesh."""
from __future__ import annotations
from dataclasses import dataclass, field
import math

from xasset.pipeline.context import PipelineContext
from xasset.pipeline.stages.scene_understand import (
    SceneUnderstandOutput, SceneRegion, DoorInfo, WindowInfo
)
from xasset.pipeline.stages.mesh_utils import ear_cut_triangulation, check_poly_clock
from xasset.pipeline.stages.uv_utils import map_uv_planar, compute_wall_uv

WALL_THICKNESS_DEFAULT = 0.2  # meters


@dataclass
class Opening:
    opening_type: str          # "door" | "window"
    u_start: float             # 沿墙边的水平起始偏移（米）
    u_end: float               # 沿墙边的水平结束偏移（米）
    bottom_y: float            # 洞口底部 Y（绝对，含 floor_offset）
    top_y: float               # 洞口顶部 Y（绝对）
    opening_id: str            # DoorInfo.id 或 WindowInfo.id


@dataclass
class SubMesh:
    role: str                  # "floor"|"ceiling"|"wall_inner"|"wall_outer"|"wall_top"
    region_id: str
    vertices: list[list[float]]   # [[x,y,z], ...]
    normals: list[list[float]]    # [[nx,ny,nz], ...]
    uvs: list[list[float]]        # [[u,v], ...]
    faces: list[list[int]]        # [[i,j,k], ...]


@dataclass
class WallSegmentMesh:
    edge_index: int
    submeshes: list[SubMesh] = field(default_factory=list)


@dataclass
class RegionGeometry:
    region_id: str
    floor: SubMesh | None = None
    ceiling: SubMesh | None = None
    walls: list[WallSegmentMesh] = field(default_factory=list)


@dataclass
class SceneMesh:
    regions: list[RegionGeometry] = field(default_factory=list)
    floor_offset: float = 0.0


@dataclass
class MeshBuildOutput:
    scene_type: str
    scene_mesh: SceneMesh
    wall_thickness: float


class MeshBuilderService:
    """Stateless service: converts SceneRegion list to SceneMesh."""

    def build_scene(
        self,
        regions: list[SceneRegion],
        wall_thickness: float = WALL_THICKNESS_DEFAULT,
        floor_offset: float = 0.0,
    ) -> SceneMesh:
        mesh = SceneMesh(floor_offset=floor_offset)
        for idx, region in enumerate(regions):
            region_id = f"r{idx}"
            geom = self._build_region_geometry(region, region_id, wall_thickness, floor_offset)
            mesh.regions.append(geom)
        return mesh

    def _build_region_geometry(
        self,
        region: SceneRegion,
        region_id: str,
        wall_thickness: float,
        floor_offset: float,
    ) -> RegionGeometry:
        geom = RegionGeometry(region_id=region_id)
        boundary = region.boundary  # [[x,z], ...]
        height = region.height

        # Floor (Y = floor_offset)
        floor_verts = [[p[0], floor_offset, p[1]] for p in boundary]
        floor_2d = [[p[0], p[1]] for p in boundary]
        floor_faces = ear_cut_triangulation(floor_2d)
        floor_normals = [[0, 1, 0]] * len(floor_verts)
        floor_uvs = map_uv_planar(floor_verts, [0, 1, 0])
        geom.floor = SubMesh(
            role="floor", region_id=region_id,
            vertices=floor_verts, normals=floor_normals,
            uvs=floor_uvs, faces=floor_faces,
        )

        # Ceiling (Y = floor_offset + height), reversed winding
        ceil_y = floor_offset + height
        ceil_verts = [[p[0], ceil_y, p[1]] for p in boundary]
        ceil_2d = [[p[0], p[1]] for p in boundary]
        ceil_faces_raw = ear_cut_triangulation(ceil_2d)
        ceil_faces = [[f[2], f[1], f[0]] for f in ceil_faces_raw]  # flip winding
        ceil_normals = [[0, -1, 0]] * len(ceil_verts)
        ceil_uvs = map_uv_planar(ceil_verts, [0, -1, 0])
        geom.ceiling = SubMesh(
            role="ceiling", region_id=region_id,
            vertices=ceil_verts, normals=ceil_normals,
            uvs=ceil_uvs, faces=ceil_faces,
        )

        # Walls
        geom.walls = self._build_walls(region, region_id, wall_thickness, floor_offset)
        return geom

    def _compute_outward_normal(
        self,
        p0: list[float],
        p1: list[float],
        centroid: list[float],
    ) -> list[float]:
        """XZ 平面内朝外（背向 centroid）的单位法线。"""
        dx = p1[0] - p0[0]
        dz = p1[1] - p0[1]
        length = math.sqrt(dx * dx + dz * dz) or 1.0
        n0 = [-dz / length, dx / length]
        mid = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2]
        dot = n0[0] * (mid[0] - centroid[0]) + n0[1] * (mid[1] - centroid[1])
        if dot < 0:
            n0 = [dz / length, -dx / length]
        return n0

    def _match_openings_to_edge(
        self,
        p0: list[float],
        p1: list[float],
        doors: list,
        windows: list,
        floor_offset: float,
    ) -> list[Opening]:
        """将当前墙边上的门窗投影成 Opening 列表（u 坐标沿边）。"""
        dx = p1[0] - p0[0]
        dz = p1[1] - p0[1]
        edge_len = math.sqrt(dx * dx + dz * dz) or 1.0
        tx, tz = dx / edge_len, dz / edge_len

        openings: list[Opening] = []
        THRESHOLD = 0.15

        for d in doors:
            cx, cz = d.center[0], d.center[1]
            perp = abs((cx - p0[0]) * tz - (cz - p0[1]) * tx)
            if perp > THRESHOLD:
                continue
            u_center = (cx - p0[0]) * tx + (cz - p0[1]) * tz
            half_w = d.width / 2
            openings.append(Opening(
                opening_type="door",
                u_start=u_center - half_w,
                u_end=u_center + half_w,
                bottom_y=floor_offset,
                top_y=floor_offset + d.height,
                opening_id=d.id,
            ))

        for w in windows:
            if len(w.pts) < 2:
                continue
            cx = (w.pts[0][0] + w.pts[1][0]) / 2
            cz = (w.pts[0][1] + w.pts[1][1]) / 2
            perp = abs((cx - p0[0]) * tz - (cz - p0[1]) * tx)
            if perp > THRESHOLD:
                continue
            u_center = (cx - p0[0]) * tx + (cz - p0[1]) * tz
            half_w = w.width / 2
            openings.append(Opening(
                opening_type="window",
                u_start=u_center - half_w,
                u_end=u_center + half_w,
                bottom_y=floor_offset + w.sill_height,
                top_y=floor_offset + w.sill_height + w.height,
                opening_id=w.id,
            ))

        return sorted(openings, key=lambda o: o.u_start)

    def _build_wall_inner_poly(
        self,
        p0: list[float],
        p1: list[float],
        height: float,
        floor_offset: float,
        openings: list[Opening],
    ) -> list[list[float]]:
        """
        构造墙段内面凹多边形（含门窗缺口）。
        顶点为 [x, y, z]，Y=高度，XZ 沿墙边方向行进。
        门：底部 notch（从 y_bot 到 door_top）
        窗：中间矩形缺口（从 sill_height 到 window_top）
        """
        dx = p1[0] - p0[0]
        dz = p1[1] - p0[1]
        edge_len = math.sqrt(dx * dx + dz * dz) or 1.0
        tx, tz = dx / edge_len, dz / edge_len

        def pt_at_u(u, y):
            return [p0[0] + tx * u, y, p0[1] + tz * u]

        y_bot = floor_offset
        y_top = floor_offset + height

        poly: list[list[float]] = [pt_at_u(0.0, y_bot)]  # 左下起点

        for op in openings:
            u0 = max(0.0, min(edge_len, op.u_start))
            u1 = max(0.0, min(edge_len, op.u_end))
            if op.opening_type == "door":
                # 门：从底部开 notch
                poly.append(pt_at_u(u0, y_bot))
                poly.append(pt_at_u(u0, op.top_y))
                poly.append(pt_at_u(u1, op.top_y))
                poly.append(pt_at_u(u1, y_bot))
            else:
                # 窗：中间矩形缺口（sill_height ~ top_y）
                poly.append(pt_at_u(u0, y_bot))
                poly.append(pt_at_u(u0, op.bottom_y))
                poly.append(pt_at_u(u0, op.top_y))
                poly.append(pt_at_u(u1, op.top_y))
                poly.append(pt_at_u(u1, op.bottom_y))
                poly.append(pt_at_u(u1, y_bot))

        poly.append(pt_at_u(edge_len, y_bot))   # 右下
        poly.append(pt_at_u(edge_len, y_top))   # 右上
        poly.append(pt_at_u(0.0, y_top))        # 左上（闭合）
        return poly

    def _build_wall_segment(
        self,
        p0: list[float],
        p1: list[float],
        height: float,
        floor_offset: float,
        wall_thickness: float,
        outward: list[float],   # [nx, nz]
        openings: list[Opening],
        region_id: str,
    ) -> list[SubMesh]:
        submeshes = []
        nx, nz = outward
        dx = p1[0] - p0[0]
        dz = p1[1] - p0[1]
        el = math.sqrt(dx * dx + dz * dz) or 1.0

        # Inner face
        inner_poly = self._build_wall_inner_poly(p0, p1, height, floor_offset, openings)
        inner_2d = [[v[0], v[1]] for v in inner_poly]
        inner_faces = ear_cut_triangulation(inner_2d)
        inner_normal = [-nx, 0.0, -nz]
        inner_normals = [inner_normal] * len(inner_poly)
        inner_uvs = compute_wall_uv(inner_poly, u_axis=[dx / el, 0, dz / el], v_axis=[0, 1, 0])
        submeshes.append(SubMesh(
            role="wall_inner", region_id=region_id,
            vertices=inner_poly, normals=inner_normals,
            uvs=inner_uvs, faces=inner_faces,
        ))

        # Outer face: offset inward poly outward
        outer_poly = [
            [v[0] + nx * wall_thickness, v[1], v[2] + nz * wall_thickness]
            for v in inner_poly
        ]
        outer_2d = [[v[0], v[1]] for v in outer_poly]
        outer_faces_raw = ear_cut_triangulation(outer_2d)
        outer_faces = [[f[2], f[1], f[0]] for f in outer_faces_raw]  # flip winding
        outer_normal = [nx, 0.0, nz]
        outer_normals = [outer_normal] * len(outer_poly)
        outer_uvs = compute_wall_uv(outer_poly, u_axis=[dx / el, 0, dz / el], v_axis=[0, 1, 0])
        submeshes.append(SubMesh(
            role="wall_outer", region_id=region_id,
            vertices=outer_poly, normals=outer_normals,
            uvs=outer_uvs, faces=outer_faces,
        ))

        # Top cap
        y_top = floor_offset + height
        cap_verts = [
            [p0[0],                          y_top, p0[1]],
            [p1[0],                          y_top, p1[1]],
            [p1[0] + nx * wall_thickness,    y_top, p1[1] + nz * wall_thickness],
            [p0[0] + nx * wall_thickness,    y_top, p0[1] + nz * wall_thickness],
        ]
        cap_faces = [[0, 1, 2], [0, 2, 3]]
        cap_normals = [[0, 1, 0]] * 4
        cap_uvs = map_uv_planar(cap_verts, [0, 1, 0])
        submeshes.append(SubMesh(
            role="wall_top", region_id=region_id,
            vertices=cap_verts, normals=cap_normals,
            uvs=cap_uvs, faces=cap_faces,
        ))

        return submeshes

    def _build_walls(
        self,
        region: SceneRegion,
        region_id: str,
        wall_thickness: float,
        floor_offset: float,
    ) -> list[WallSegmentMesh]:
        boundary = region.boundary
        n = len(boundary)
        centroid = [
            sum(p[0] for p in boundary) / n,
            sum(p[1] for p in boundary) / n,
        ]
        walls = []
        for i in range(n):
            p0 = boundary[i]
            p1 = boundary[(i + 1) % n]
            outward = self._compute_outward_normal(p0, p1, centroid)
            openings = self._match_openings_to_edge(
                p0, p1, region.doors, region.windows, floor_offset
            )
            wsm = WallSegmentMesh(edge_index=i)
            wsm.submeshes = self._build_wall_segment(
                p0, p1, region.height, floor_offset,
                wall_thickness, outward, openings, region_id,
            )
            walls.append(wsm)
        return walls


class MeshBuildStage:
    name = "mesh_build"
    layer = "geometry"
    scene_types = ["house"]

    def __init__(self, wall_thickness: float = WALL_THICKNESS_DEFAULT):
        self._svc = MeshBuilderService()
        self._wall_thickness = wall_thickness

    def run(self, ctx: PipelineContext) -> None:
        understand: SceneUnderstandOutput = ctx.stage_outputs.get("understand")
        if understand is None:
            raise RuntimeError("MeshBuildStage requires 'understand' stage output")
        scene_mesh = self._svc.build_scene(
            regions=understand.regions,
            wall_thickness=self._wall_thickness,
            floor_offset=0.0,
        )
        ctx.stage_outputs["geometry"] = MeshBuildOutput(
            scene_type=understand.scene_type,
            scene_mesh=scene_mesh,
            wall_thickness=self._wall_thickness,
        )
