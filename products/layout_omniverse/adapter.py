# products/layout-omniverse/adapter.py
"""
Adapter: converts pipeline LayoutOutput dict → USD stage.

Requires pxr (USD Python bindings). Omniverse ships with pxr built-in;
no additional installation needed when running inside Omniverse.

Usage:
    from products.layout_omniverse.agent import layout_house
    from products.layout_omniverse.adapter import write_layout_to_usd

    result = layout_house(scene_vector)
    write_layout_to_usd(result, "output.usda")

Produces a USD file with:
    /Layout                (Xform root)
      /Layout/{group_id}   (Xform at computed position, with custom metadata)
"""

from pxr import Usd, UsdGeom, Sdf     # type: ignore


def write_layout_to_usd(layout_result: dict, usd_path: str) -> Usd.Stage:
    """Write placed groups to a USD stage file.

    Args:
        layout_result: dict from layout_house()
        usd_path: output .usda/.usdc path

    Returns:
        Usd.Stage (also saved to disk)
    """
    stage = Usd.Stage.CreateNew(usd_path)

    scene_type = layout_result.get("scene_type", "house")

    root_path = f"/Layout_{scene_type}"
    root = UsdGeom.Xform.Define(stage, root_path)

    root.GetPrim().SetMetadata(
        "customData", {"xasset:scene_type": scene_type}
    )

    groups = layout_result.get("placed_groups", [])
    for pg in groups:
        _add_group_xform(stage, root_path, pg)

    stage.Save()
    return stage


def _add_group_xform(stage: Usd.Stage, parent_path: str, pg: dict) -> None:
    pos = pg["position"]
    group_path = f"{parent_path}/Group_{pg['group_code']}"

    xform = UsdGeom.Xform.Define(stage, group_path)
    xform.AddTranslateOp().Set((pos[0], pos[1], pos[2]))

    prim = xform.GetPrim()
    prim.SetMetadata("customData", {
        "xasset:group_code": pg["group_code"],
        "xasset:region_type": pg["region_type"],
        "xasset:rotation": pg["rotation"],
    })

    for role_name in (pg.get("role_assets") or {}).keys():
        _add_role_prim(stage, group_path, role_name)


def _add_role_prim(stage: Usd.Stage, parent_path: str, role_name: str) -> None:
    role_path = f"{parent_path}/{role_name}"
    prim = stage.DefinePrim(role_path, "Xform")
    prim.SetMetadata("customData", {"xasset:role": role_name})


def scene_json_to_usd(stage: Usd.Stage, scene_vector: dict) -> None:
    """Embed the input SceneVector into USD customData for traceability.

    Called by Omniverse extension before running layout generation,
    so origin data travels with the USD file.
    """
    root = stage.GetPseudoRoot()
    existing = root.GetMetadata("customData") or {}
    existing["xasset:scene_vector"] = scene_vector
    root.SetMetadata("customData", existing)
