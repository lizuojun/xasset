# xasset/pipeline/stages/geometry/house/mesh_build.py
"""geometry 层 Stage —— 边界重建（house）。

产物 schema 保持不变（MeshBuildOutput / SceneMesh / RegionGeometry / SubMesh），
但规则式网格构建算法（地板/天花板/墙/开洞的几何拉伸出）已被清理，
待 LLM 编排 + 几何工具（tools/geometry）重做。

边界重建的底层工具 —— ear-cut 三角剖分、UV 映射 —— 已迁入 tools/geometry，
算法重做时由 LLM 编排调用，本 Stage 只保留 schema 契约与占位入口。
"""
from dataclasses import dataclass, field

from xasset.pipeline.context import PipelineContext
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandOutput


@dataclass
class Opening:
    opening_type: str          # "door" | "window"
    u_start: float             # 沿墙边的水平起始偏移（米）
    u_end: float               # 沿墙边的水平结束偏移（米）
    bottom_y: float            # 洞口底部 Y（绝对，含 floor_offset）
    top_y: float               # 洞口顶部 Y（绝对）
    opening_id: str


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


class MeshBuildStage:
    name = "mesh_build"
    layer = "geometry"
    scene_types = ["house"]

    def __init__(self, wall_thickness: float = 0.2, orchestrator=None) -> None:
        self._wall_thickness = wall_thickness
        self._orchestrator = orchestrator

    def run(self, ctx: PipelineContext) -> None:
        understand: SceneUnderstandOutput = ctx.stage_outputs.get("understand")
        if understand is None:
            raise RuntimeError("MeshBuildStage requires 'understand' stage output")

        # 算法重做过渡期：返回空的 SceneMesh，schema 契约保持不变。
        # 边界重建算法将由 LLM 编排 + tools/geometry 的三角剖分/UV 工具重做。
        scene_mesh = SceneMesh()
        ctx.stage_outputs["geometry"] = MeshBuildOutput(
            scene_type=understand.scene_type,
            scene_mesh=scene_mesh,
            wall_thickness=self._wall_thickness,
        )
