import os, sys, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage
from xasset.pipeline.stages.geometry.house.mesh_build import MeshBuildStage
from xasset.pipeline.stages.layout.house.compose import HouseLayoutComposeStage
from xasset.debug import debug_dump
from products.cli.debug_run import SCENE_VECTOR

ctx = PipelineContext(str(uuid.uuid4()), PipelineInput(input_type="vector", scene_type="house", scene_vector=SCENE_VECTOR))
SceneUnderstandStage().run(ctx)
MeshBuildStage().run(ctx)
HouseLayoutComposeStage().run(ctx)

out = ctx.stage_outputs["layout"]

print(f"\n=== Furniture ({len(out.placed_groups)}) ===")
for pg in out.placed_groups:
    print(f"  {pg.group_code:6d} {pg.region_type:15s} pos=({pg.position[0]:6.2f},{pg.position[2]:6.2f}) rot={pg.rotation:6.1f}")

print(f"\n=== Doors ({len(out.doors)}) ===")
for d in out.doors:
    print(f"  {d.opening_id:15s} pos=({d.position[0]:6.2f},{d.position[2]:6.2f}) w={d.width:.2f}m")

print(f"\n=== Windows ({len(out.windows)}) ===")
for w in out.windows:
    print(f"  {w.opening_id:15s} pos=({w.position[0]:6.2f},{w.position[2]:6.2f}) w={w.width:.2f}m")

print(f"\n=== Curtains ({len(out.curtains)}) ===")
for c in out.curtains:
    print(f"  {c.window_id:15s} pos=({c.position[0]:6.2f},{c.position[2]:6.2f}) w={c.width:.2f}m")

debug_dir = os.path.join(os.path.dirname(__file__), "debug", "case1")
files = debug_dump(ctx, debug_dir)
print(f"\n=== Files ===")
for f in files:
    print(f"  {f}")
