"""
debug_run.py - debug visualization entry script

Usage:
    uv run python -m products.cli.debug_run

Output:
    products/cli/debug/<case>/scene_understand.png
    products/cli/debug/<case>/geometry_mesh.obj
    products/cli/debug/<case>/layout_plan.png

说明：算法全面重做后（见 docs/algorithm-rebuild-plan.md），本脚本只保留
框架跑通路径（六层 Stage 骨架 + 可视化 dump），旧的 RoomDecomposer /
MeshBuilderService 规则式算法已清理。
"""
import os
import sys
import uuid

from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage
from xasset.pipeline.stages.geometry.house.mesh_build import MeshBuildStage
from xasset.pipeline.stages.layout.house.compose import HouseLayoutComposeStage
from xasset.debug import debug_dump


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
            "floor": [[0, 0], [7, 0], [7, 5], [0, 5]],
            "doors": [],
            "windows": [],
        },
        {
            "id": "r-master",
            "type": "bedroom",
            "height": 2.8,
            "floor": [[7, 3], [11, 3], [11, 8], [7, 8]],
            "doors": [],
            "windows": [],
        },
    ],
}


def main() -> None:
    out_dir_case = os.path.join(os.path.dirname(__file__), "debug", "case1")
    os.makedirs(out_dir_case, exist_ok=True)

    print("\n=== Case: case1 ===")

    ctx = PipelineContext(
        job_id=str(uuid.uuid4()),
        input=PipelineInput(input_type="vector", scene_type="house", scene_vector=SCENE_VECTOR),
    )
    SceneUnderstandStage().run(ctx)
    MeshBuildStage().run(ctx)
    HouseLayoutComposeStage().run(ctx)

    print("[ output files ]")
    files_final = debug_dump(ctx, output_dir=out_dir_case)
    for f in files_final:
        print(f"  {f}")

    print("Done.")


if __name__ == "__main__":
    main()
