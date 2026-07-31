# products/layout-blender/agent.py
"""
House layout generation agent API.

Usage (from any tool/agent/CLI):
    from products.layout_blender.agent import layout_house
    result = layout_house(scene_vector)
    print(result["placed_groups"])

This is the single entry point. Blender addon and external callers
both use this function — no platform coupling.
"""

from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.pipeline import PipelineConfig
from xasset.pipeline.registry import create_registry, StageRegistry

_HOUSE_STAGES = ["understand", "geometry", "layout"]
_SCENE_TYPE = "house"

_registry: StageRegistry | None = None


def _get_registry() -> StageRegistry:
    global _registry
    if _registry is None:
        _registry = create_registry(house=True, urban=False, wild=False)
    return _registry


def layout_house(scene_vector: dict) -> dict:
    """Run understand → geometry → layout stages and return LayoutOutput as dict.

    Args:
        scene_vector: SceneVector JSON as defined in pipeline docs.
                      Contains rooms with polygon floors, doors, windows.

    Returns:
        dict with keys:
            scene_type: str            # "house"
            placed_groups: list[dict]  # each has group_code, region_type,
                                       #   position[x,y,z], rotation, role_assets
            geometry: dict            # optional, mesh data
    """
    registry = _get_registry()
    ctx = PipelineContext(
        job_id="layout-blender",
        input=PipelineInput(
            input_type="vector",
            scene_type=_SCENE_TYPE,
            scene_vector=scene_vector,
        ),
    )

    for layer in _HOUSE_STAGES:
        stage = registry.get(layer, _SCENE_TYPE)
        stage.run(ctx)

    layout_output = ctx.stage_outputs.get("layout")
    result = {
        "scene_type": _SCENE_TYPE,
        "placed_groups": _placed_groups_as_dicts(layout_output),
    }

    geo_output = ctx.stage_outputs.get("geometry")
    if geo_output is not None and hasattr(geo_output, "scene_mesh"):
        result["geometry"] = {
            "vertices": geo_output.scene_mesh.vertices,
            "faces": geo_output.scene_mesh.faces,
        }

    return result


def _placed_groups_as_dicts(layout_output) -> list[dict]:
    if layout_output is None:
        return []
    return [
        {
            "group_code": pg.group_code,
            "region_type": pg.region_type,
            "position": list(pg.position),
            "rotation": pg.rotation,
            "role_assets": dict(pg.role_assets),
        }
        for pg in layout_output.placed_groups
    ]
