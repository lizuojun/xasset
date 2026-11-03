# products/layout-blender/adapter.py
"""
Adapter: converts pipeline LayoutOutput dict → Blender objects.

Requires Blender runtime (bpy available). Imported only when running
inside Blender, never in agent-only contexts.

Usage:
    from products.layout_blender.adapter import place_layout

    result = layout_house(scene_vector)
    place_layout(result)   # creates bpy Empty + Text placeholders
"""

import bpy     # type: ignore


def place_layout(layout_result: dict) -> list[bpy.types.Object]:
    """Create Blender objects for each placed group in the layout output.

    Each placed group becomes an Empty at the computed position,
    with a child Text object showing the group label.

    Returns list of root Empty objects created.
    """
    groups = layout_result.get("placed_groups", [])
    created: list[bpy.types.Object] = []

    collection = _ensure_collection("XAsset_Layout")

    for pg in groups:
        name = f"Group_{pg['group_code']}"
        pos = pg["position"]

        empty = bpy.data.objects.new(name, None)
        empty.location = (pos[0], pos[1], pos[2])
        empty.rotation_euler = (0.0, 0.0, 0.0)
        empty.empty_display_type = "PLAIN_AXES"
        empty.empty_display_size = 0.3

        empty["xasset_group_code"] = pg["group_code"]
        empty["xasset_region_type"] = pg["region_type"]
        empty["xasset_rotation"] = pg["rotation"]

        collection.objects.link(empty)
        created.append(empty)

        _add_label_child(empty, pg, collection)

    return created


def _ensure_collection(name: str) -> bpy.types.Collection:
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def _add_label_child(
    parent: bpy.types.Object,
    pg: dict,
    collection: bpy.types.Collection,
) -> None:
    text_data = bpy.data.curves.new(
        f"label_{pg['group_code']}", type="FONT"
    )
    text_data.body = (
        f"{pg['region_type']} (code={pg['group_code']})\n"
        + "\n".join(
            f"  [{role}]" for role in (pg.get("role_assets") or {}).keys()
        )
    )
    text_obj = bpy.data.objects.new(f"Label_{pg['group_code']}", text_data)
    text_obj.location = (0, 0, 0.5)
    text_obj.parent = parent
    collection.objects.link(text_obj)
