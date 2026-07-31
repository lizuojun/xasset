# products/layout-omniverse
#
# Omniverse-centric house layout product.
#
# Components:
#   agent.py          — layout_house(scene_vector) → dict    (no omniverse dependency)
#   adapter.py        — dict → USD stage                     (requires pxr)
#   omniverse_ext.py  — Omni extension UI + lifecycle        (requires omni.*)
