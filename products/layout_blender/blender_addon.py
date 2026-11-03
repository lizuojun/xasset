# products/layout-blender/blender_addon.py
"""
XAsset House Layout — Blender Addon

Install: copy this directory into Blender's addons folder, enable
    "XAsset: House Layout Generator" in Edit → Preferences → Add-ons.

Provides one operator "Generate House Layout" in the 3D View sidebar
(XAsset tab) or via F3 search.
"""

import bpy     # type: ignore

bl_info = {
    "name": "XAsset: House Layout Generator",
    "author": "xasset",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > XAsset",
    "description": "Generate interior layout from room polygons",
    "category": "3D View",
}


class XASSET_PT_LayoutPanel(bpy.types.Panel):
    bl_idname = "XASSET_PT_layout_panel"
    bl_label = "House Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "XAsset"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "xasset_sample_json", text="Sample JSON(not required)")

        op = layout.operator("xasset.generate_layout", text="Generate House Layout")
        op.sample_json = ""

        if scene.xasset_layout_message:
            box = layout.box()
            for line in scene.xasset_layout_message.splitlines():
                box.label(text=line)


class XASSET_OT_GenerateLayout(bpy.types.Operator):
    bl_idname = "xasset.generate_layout"
    bl_label = "Generate House Layout"
    bl_description = "Run understand → geometry → layout pipeline"

    sample_json: bpy.props.StringProperty()

    def execute(self, context):
        try:
            from products.layout_blender.agent import layout_house
            from products.layout_blender.adapter import place_layout

            if not self.sample_json:
                raise RuntimeError("No sample_json path provided.")

            import json
            import os

            # it will need to be passed by omniverse or user input
            if not os.path.isfile(self.sample_json):
                raise RuntimeError(f"File not found: {self.sample_json}")

            with open(self.sample_json, "r", encoding="utf-8") as f:
                scene_vector = json.load(f)

            result = layout_house(scene_vector)
            objects = place_layout(result)

            msg_lines = [f"Done — {len(objects)} groups placed"]
            for pg in result.get("placed_groups", []):
                msg_lines.append(
                    f"  {pg['region_type']}: code={pg['group_code']} "
                    f"@ ({pg['position'][0]:.1f}, {pg['position'][2]:.1f})"
                )
            context.scene.xasset_layout_message = "\n".join(msg_lines)
            self.report({"INFO"}, f"Placed {len(objects)} groups")

        except Exception as exc:
            context.scene.xasset_layout_message = f"ERROR: {exc}"
            self.report({"ERROR"}, str(exc))

        return {"FINISHED"}


_CLASSES = [
    XASSET_PT_LayoutPanel,
    XASSET_OT_GenerateLayout,
]


def register():
    bpy.types.Scene.xasset_layout_message = bpy.props.StringProperty(
        name="Message", default=""
    )
    bpy.types.Scene.xasset_sample_json = bpy.props.StringProperty(
        name="Sample Scene Path",
        description="JSON file path",
        subtype="FILE_PATH",
        default="",
    )
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    del bpy.types.Scene.xasset_layout_message
    del bpy.types.Scene.xasset_sample_json
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
