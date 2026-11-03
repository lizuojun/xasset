# xasset/pipeline/stages/geometry/house/mesh_build.py
"""geometry 层 Stage —— 轮廓阶段：把 2D 轮廓线拉成 3D 几何（house）。

契约见 xasset/pipeline/schemas/geometry.py。

规则式网格构建算法（地板/天花板/墙/开洞的几何拉伸）已在算法重做中清理，
待按 Artist 范式重做（理解侧可为几何/视觉重建算法，约束侧为多边形合法性
与开洞规则）。底层工具 —— ear-cut 三角剖分、UV 映射 —— 在 tools/geometry。
"""
from __future__ import annotations

from xasset.pipeline.schemas import GeometryOutput, SceneMesh
from xasset.pipeline.stage import StageInputs


class MeshBuildStage:
    name = "mesh_build"
    layer = "geometry"
    scene_types = ["house"]
    requires = ["understand"]
    output_type = GeometryOutput

    def __init__(self, wall_thickness: float = 0.2, orchestrator=None) -> None:
        self._wall_thickness = wall_thickness
        self._orchestrator = orchestrator

    def run(self, inputs: StageInputs) -> GeometryOutput:
        understand = inputs.understand

        # 算法重做过渡期：返回空的 SceneMesh，契约保持不变。
        # 轮廓 → 3D 几何的重建算法待重做（tools/geometry 的三角剖分/UV 可用）。
        return GeometryOutput(
            scene_type=understand.scene_type,
            scene_mesh=SceneMesh(),
            wall_thickness=self._wall_thickness,
        )
