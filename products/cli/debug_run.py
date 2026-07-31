"""
debug_run.py - debug visualization entry script

Usage:
    uv run python -m products.cli.debug_run

Output:
    products/cli/debug/<case>/scene_understand.png
    products/cli/debug/<case>/room_decompose.png
    products/cli/debug/<case>/geometry_mesh.obj
"""
import os
import sys
import uuid

from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage
from xasset.pipeline.stages.geometry.house.mesh_build import MeshBuildStage
from xasset.pipeline.stages.layout.house.room_decompose import RoomDecomposer
from xasset.pipeline.stages.layout.house.compose import HouseLayoutComposeStage
from xasset.debug import debug_dump
from xasset.debug.renderers.house.decompose_2d import render_decompose_2d

# =============================================================================
# Case 1: two-bedroom apartment, ~88m (original)
# =============================================================================

SCENE_VECTOR = {
    "meta": {"coordinate": "xzy", "unit": "m", "version": "1.0"},
    "rooms": [
        {
            "id": "r-living",
            "type": "living_room",
            "height": 2.8,
            "floor": [[0,0],[7,0],[7,5],[0,5]],
            "doors": [
                {"id": "d-entry",
                 "pts": [[2,0],[3.5,0],[3.5,0.1],[2,0.1]],
                 "height": 2.1, "to_room": None},
                {"id": "d-liv-master",
                 "pts": [[7,3.5],[7,4.5],[6.9,4.5],[6.9,3.5]],
                 "height": 2.0, "to_room": "r-master"},
                {"id": "d-liv-bed2",
                 "pts": [[1.5,5],[2.5,5],[2.5,4.9],[1.5,4.9]],
                 "height": 2.0, "to_room": "r-bed2"},
                {"id": "d-liv-kitchen",
                 "pts": [[7,1],[7,2],[6.9,2],[6.9,1]],
                 "height": 2.0, "to_room": "r-kitchen"},
            ],
            "windows": [
                {"id": "w-liv-west",
                 "window_type": "normal",
                 "pts": [[0,1.5],[0,3.5],[0.1,3.5],[0.1,1.5]],
                 "sill_height": 0.9, "height": 1.5},
            ],
        },
        {
            "id": "r-master",
            "type": "bedroom",
            "height": 2.8,
            "floor": [[7,3],[11,3],[11,8],[7,8]],
            "doors": [
                {"id": "d-liv-master",
                 "pts": [[7,3.5],[7,4.5],[7.1,4.5],[7.1,3.5]],
                 "height": 2.0, "to_room": "r-living"},
                {"id": "d-master-bath",
                 "pts": [[7,5.5],[7,6.5],[7.1,6.5],[7.1,5.5]],
                 "height": 2.0, "to_room": "r-bath"},
            ],
            "windows": [
                {"id": "w-master-east",
                 "window_type": "normal",
                 "pts": [[11,4.5],[11,7],[10.9,7],[10.9,4.5]],
                 "sill_height": 0.9, "height": 1.5},
                {"id": "w-master-north",
                 "window_type": "normal",
                 "pts": [[8,8],[10,8],[10,7.9],[8,7.9]],
                 "sill_height": 0.9, "height": 1.5},
            ],
        },
        {
            "id": "r-bed2",
            "type": "bedroom",
            "height": 2.8,
            "floor": [[0,5],[5,5],[5,8],[0,8]],
            "doors": [
                {"id": "d-liv-bed2",
                 "pts": [[1.5,5],[2.5,5],[2.5,5.1],[1.5,5.1]],
                 "height": 2.0, "to_room": "r-living"},
                {"id": "d-bed2-bath",
                 "pts": [[5,6],[5,7],[4.9,7],[4.9,6]],
                 "height": 2.0, "to_room": "r-bath"},
            ],
            "windows": [
                {"id": "w-bed2-west",
                 "window_type": "normal",
                 "pts": [[0,6],[0,7.5],[0.1,7.5],[0.1,6]],
                 "sill_height": 0.9, "height": 1.5},
                {"id": "w-bed2-bay",
                 "window_type": "bay",
                 "pts": [[1,8],[4,8],[4,7.9],[1,7.9]],
                 "sill_height": 0.45, "height": 1.5, "depth": 0.6},
            ],
        },
        {
            "id": "r-kitchen",
            "type": "kitchen",
            "height": 2.6,
            "floor": [[7,0],[11,0],[11,3],[7,3]],
            "doors": [
                {"id": "d-liv-kitchen",
                 "pts": [[7,1],[7,2],[7.1,2],[7.1,1]],
                 "height": 2.0, "to_room": "r-living"},
            ],
            "windows": [
                {"id": "w-kitchen-south",
                 "window_type": "normal",
                 "pts": [[7.5,0],[10,0],[10,0.1],[7.5,0.1]],
                 "sill_height": 0.9, "height": 1.2},
                {"id": "w-kitchen-east",
                 "window_type": "normal",
                 "pts": [[11,0.5],[11,2],[10.9,2],[10.9,0.5]],
                 "sill_height": 0.9, "height": 1.2},
            ],
        },
        {
            "id": "r-bath",
            "type": "bathroom",
            "height": 2.5,
            "floor": [[5,5],[7,5],[7,8],[5,8]],
            "doors": [
                {"id": "d-bed2-bath",
                 "pts": [[5,6],[5,7],[5.1,7],[5.1,6]],
                 "height": 2.0, "to_room": "r-bed2"},
                {"id": "d-master-bath",
                 "pts": [[7,5.5],[7,6.5],[6.9,6.5],[6.9,5.5]],
                 "height": 2.0, "to_room": "r-master"},
            ],
            "windows": [
                {"id": "w-bath-north",
                 "window_type": "normal",
                 "pts": [[5.3,8],[6.7,8],[6.7,7.9],[5.3,7.9]],
                 "sill_height": 1.5, "height": 0.6},
            ],
        },
    ],
}

# =============================================================================
# Case 2: simple 2-bedroom flat (all rectangles, no overlap)
# =============================================================================

SCENE_VECTOR_CASE2 = {
    "meta": {"coordinate": "xzy", "unit": "m", "version": "1.0"},
    "rooms": [
        {
            "id": "r-living",
            "type": "living_room",
            "height": 2.8,
            "floor": [[0,0],[10,0],[10,4],[0,4]],
            "doors": [
                {"id":"d-entry2","pts":[[4,0],[5,0],[5,0.1],[4,0.1]],"height":2.1,"to_room":None},
                {"id":"d-liv-bed2","pts":[[1,4],[2,4],[2,4.1],[1,4.1]],"height":2.0,"to_room":"r-bed2"},
                {"id":"d-liv-master","pts":[[7,4],[8,4],[8,4.1],[7,4.1]],"height":2.0,"to_room":"r-master"},
            ],
            "windows": [
                {"id":"w-liv-south","window_type":"normal","pts":[[6,0],[8,0],[8,0.1],[6,0.1]],"sill_height":0.6,"height":1.8},
                {"id":"w-liv-west","window_type":"normal","pts":[[0,1.5],[0,3],[0.1,3],[0.1,1.5]],"sill_height":0.9,"height":1.5},
            ],
        },
        {
            "id": "r-bed2",
            "type": "bedroom",
            "height": 2.8,
            "floor": [[0,4],[5,4],[5,8],[0,8]],
            "doors": [
                {"id":"d-liv-bed2","pts":[[1,4],[2,4],[2,3.9],[1,3.9]],"height":2.0,"to_room":"r-living"},
            ],
            "windows": [
                {"id":"w-bed2-west","window_type":"normal","pts":[[0,5.5],[0,7],[0.1,7],[0.1,5.5]],"sill_height":0.9,"height":1.5},
            ],
        },
        {
            "id": "r-master",
            "type": "bedroom",
            "height": 2.8,
            "floor": [[5,4],[10,4],[10,8],[5,8]],
            "doors": [
                {"id":"d-liv-master","pts":[[7,4],[8,4],[8,3.9],[7,3.9]],"height":2.0,"to_room":"r-living"},
            ],
            "windows": [
                {"id":"w-master-east","window_type":"normal","pts":[[10,5],[10,7],[9.9,7],[9.9,5]],"sill_height":0.9,"height":1.5},
                {"id":"w-master-north","window_type":"normal","pts":[[7,8],[9,8],[9,7.9],[7,7.9]],"sill_height":0.9,"height":1.5},
            ],
        },
    ],
}

# =============================================================================
# Main
# =============================================================================

CASE = 1  # default case1; set to 2 to switch

if CASE == 2:
    SCENE_VECTOR_FINAL = SCENE_VECTOR_CASE2
    CASE_TAG = "case2"
else:
    SCENE_VECTOR_FINAL = SCENE_VECTOR
    CASE_TAG = "case1"

OUT_DIR = os.path.join(os.path.dirname(__file__), "debug")
out_dir_case = os.path.join(OUT_DIR, CASE_TAG)
os.makedirs(out_dir_case, exist_ok=True)

print(f"\n=== Case: {CASE_TAG} ===")

ctx = PipelineContext(
    job_id=str(uuid.uuid4()),
    input=PipelineInput(input_type="vector", scene_type="house", scene_vector=SCENE_VECTOR_FINAL),
)
SceneUnderstandStage().run(ctx)
MeshBuildStage().run(ctx)
HouseLayoutComposeStage().run(ctx)

print("[ output files ]")
files_final = debug_dump(ctx, output_dir=out_dir_case)
for f in files_final:
    print(f"  {f}")

print("[ RoomDecomposer ]")
understand_out = ctx.stage_outputs["understand"]
decomposer = RoomDecomposer()
segs_by_region = {}
curtains_by_region = {}
for region in understand_out.regions:
    segs, curtains = decomposer.decompose(region)
    segs_by_region[region.region_id] = segs
    curtains_by_region[region.region_id] = curtains
    n_wall = sum(1 for s in segs if s.seg_type in ("wall", "window"))
    n_door = sum(1 for s in segs if s.seg_type == "door")
    print(f"  {region.region_id}: {len(segs)} segs "
          f"({n_wall} wall+window, {n_door} door)"
          f" + {len(curtains)} curtains")

decompose_path = os.path.join(out_dir_case, "room_decompose.png")
render_decompose_2d(segs_by_region, curtains_by_region, understand_out, decompose_path)
print(f"  -> {decompose_path}")
files_final.append(decompose_path)

if sys.platform == "win32":
    for f in files_final:
        if f.endswith(".png"):
            os.startfile(f)

print("Done.")
