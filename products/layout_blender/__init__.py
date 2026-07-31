# products/layout-blender
#
# Blender-centric house layout product.
#
# Components:
#   agent.py         — layout_house(scene_vector) → dict     (no blender dependency)
#   adapter.py       — dict → bpy objects                    (requires blender)
#   blender_addon.py — bpy operator + panel                  (requires blender)
