# xasset/tools/geometry/__init__.py
"""几何工具：三角剖分、UV 映射、多边形归一化。

从旧 pipeline/utils 迁入的独立确定性算法，算法重做后作为 LLM 编排
主干的工具被调用。这些实现本身是正确且通用的，不需要随旧算法一起清理。
"""
from xasset.tools.geometry.mesh import (
    ear_cut_triangulation,
    check_poly_clock,
    build_polygon_mesh,
    polygon_area,
)
from xasset.tools.geometry.uv import (
    compute_wall_uv,
    map_uv_planar,
)
from xasset.tools.geometry.normalize import (
    normalize_polygon,
    normalize_scene_vector,
    NormalizeResult,
)

__all__ = [
    "ear_cut_triangulation",
    "check_poly_clock",
    "build_polygon_mesh",
    "polygon_area",
    "compute_wall_uv",
    "map_uv_planar",
    "normalize_polygon",
    "normalize_scene_vector",
    "NormalizeResult",
]
