"""
debug_run.py — 调试可视化入口脚本

用法：
    uv run python debug_run.py

输出：
    debug/understand_regions.png  — 理解层平面图（自动用 Windows 图片查看器打开）
    debug/layout_plan.png         — 布局层平面图（自动用 Windows 图片查看器打开）
    debug/geometry_mesh.obj       — 几何层白模（自动用系统默认 3D 查看器打开）
"""
import os
import sys
import uuid

from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.scene_understand import SceneUnderstandStage
from xasset.pipeline.stages.mesh_build import MeshBuildStage
from xasset.pipeline.stages.layout_compose import HouseLayoutComposeStage
from xasset.services.sample_search import SampleSearchService
from xasset.debug import debug_dump

# ── 测试场景：两居室（客厅 + 卧室 + 卫生间）──────────────────────────────────
SCENE_VECTOR = {
    "meta": {"coordinate": "xzy", "unit": "m", "version": "1.0"},
    "rooms": [
        {
            "id": "r-living",
            "type": "living_room",
            "height": 2.8,
            "floor": [[0, 0], [5, 0], [5, 4], [0, 4]],
            "doors": [
                # 入户门（外门）
                {"id": "d-entry", "pts": [[0, 1], [0, 2], [0.1, 2], [0.1, 1]],
                 "height": 2.1, "to_room": None},
                # 连卧室内门
                {"id": "d-liv-bed", "pts": [[5, 1.5], [5, 2.5], [4.9, 2.5], [4.9, 1.5]],
                 "height": 2.0, "to_room": "r-bed"},
                # 连卫生间内门
                {"id": "d-liv-bath", "pts": [[2, 0], [3, 0], [3, 0.1], [2, 0.1]],
                 "height": 2.0, "to_room": "r-bath"},
            ],
            "windows": [
                {"id": "w-liv1", "window_type": "normal",
                 "pts": [[1, 4], [3, 4], [3, 4.1], [1, 4.1]],
                 "sill_height": 0.9, "height": 1.5},
            ],
        },
        {
            "id": "r-bed",
            "type": "bedroom",
            "height": 2.8,
            "floor": [[5, 0], [8, 0], [8, 4], [5, 4]],
            "doors": [
                {"id": "d-liv-bed", "pts": [[5, 1.5], [5, 2.5], [5.1, 2.5], [5.1, 1.5]],
                 "height": 2.0, "to_room": "r-living"},
            ],
            "windows": [
                {"id": "w-bed1", "window_type": "normal",
                 "pts": [[5.5, 4], [7.5, 4], [7.5, 4.1], [5.5, 4.1]],
                 "sill_height": 0.9, "height": 1.5},
                {"id": "w-bed2", "window_type": "bay",
                 "pts": [[5, 0.5], [5, 1.5], [4.9, 1.5], [4.9, 0.5]],
                 "sill_height": 0.45, "height": 1.5, "depth": 0.6},
            ],
        },
        {
            "id": "r-bath",
            "type": "bathroom",
            "height": 2.5,
            "floor": [[1, -2], [4, -2], [4, 0], [1, 0]],
            "doors": [
                {"id": "d-liv-bath", "pts": [[2, 0], [3, 0], [3, -0.1], [2, -0.1]],
                 "height": 2.0, "to_room": "r-living"},
            ],
            "windows": [
                {"id": "w-bath1", "window_type": "normal",
                 "pts": [[1.5, -2], [2.5, -2], [2.5, -2.1], [1.5, -2.1]],
                 "sill_height": 1.5, "height": 0.6},
            ],
        },
    ],
}

OUT_DIR = os.path.join(os.path.dirname(__file__), "debug")
os.makedirs(OUT_DIR, exist_ok=True)

print("[ 理解层 ]")
ctx = PipelineContext(
    job_id=str(uuid.uuid4()),
    input=PipelineInput(input_type="vector", scene_type="house", scene_vector=SCENE_VECTOR),
)
SceneUnderstandStage().run(ctx)

print("[ 几何层 ]")
MeshBuildStage().run(ctx)

print("[ 布局层 ]")
HouseLayoutComposeStage(sample_search=SampleSearchService([])).run(ctx)

print("[ 输出文件 ]")
files = debug_dump(ctx, output_dir=OUT_DIR)
for f in files:
    print(f"  {f}")

# ── 自动打开查看器（仅 Windows）────────────────────────────────────────────────
if sys.platform == "win32":
    for f in files:
        print("  open:", f)
        os.startfile(f)

print("完成。")
