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
from xasset.debug import debug_dump

# ── 测试场景：两室一厅一厨一卫，约 88m²  ─────────────────────────────────────
#
#  建筑范围 x[0,11] × z[0,8]，所有房间共墙相邻，无悬空/重叠
#
#      0    5    7   11
#  8   +----+----+----+
#      | 次卧 | 卫 | 主卧 |
#  5   +    +----+    |
#      |    |    |    |
#      | 客厅 |    | 主卧 |
#  3   |    +----+    |
#      |    | 厨房|    |
#  0   +----+----+----+
#
#  房间尺寸：
#    客厅  x[0,7]  z[0,5]  = 7×5  = 35m²
#    主卧  x[7,11] z[3,8]  = 4×5  = 20m²
#    次卧  x[0,5]  z[5,8]  = 5×3  = 15m²
#    厨房  x[7,11] z[0,3]  = 4×3  = 12m²
#    卫生间 x[5,7]  z[5,8]  = 2×3  =  6m²
#
SCENE_VECTOR = {
    "meta": {"coordinate": "xzy", "unit": "m", "version": "1.0"},
    "rooms": [
        {
            "id": "r-living",
            "type": "living_room",
            "height": 2.8,
            "floor": [[0,0],[7,0],[7,5],[0,5]],
            "doors": [
                # 入户门：南墙（z=0）外门
                {"id": "d-entry",
                 "pts": [[2,0],[3.5,0],[3.5,0.1],[2,0.1]],
                 "height": 2.1, "to_room": None},
                # 客厅→主卧：东墙（x=7）z[3,5] 段
                {"id": "d-liv-master",
                 "pts": [[7,3.5],[7,4.5],[6.9,4.5],[6.9,3.5]],
                 "height": 2.0, "to_room": "r-master"},
                # 客厅→次卧：北墙（z=5）x[0,5] 段
                {"id": "d-liv-bed2",
                 "pts": [[1.5,5],[2.5,5],[2.5,4.9],[1.5,4.9]],
                 "height": 2.0, "to_room": "r-bed2"},
                # 客厅→厨房：东墙（x=7）z[0,3] 段
                {"id": "d-liv-kitchen",
                 "pts": [[7,1],[7,2],[6.9,2],[6.9,1]],
                 "height": 2.0, "to_room": "r-kitchen"},
            ],
            "windows": [
                # 西墙（x=0）朝外大窗
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
                # 主卧→客厅
                {"id": "d-liv-master",
                 "pts": [[7,3.5],[7,4.5],[7.1,4.5],[7.1,3.5]],
                 "height": 2.0, "to_room": "r-living"},
                # 主卧→卫生间：西墙（x=7）z[5,8] 段
                {"id": "d-master-bath",
                 "pts": [[7,5.5],[7,6.5],[7.1,6.5],[7.1,5.5]],
                 "height": 2.0, "to_room": "r-bath"},
            ],
            "windows": [
                # 东墙（x=11）朝外窗
                {"id": "w-master-east",
                 "window_type": "normal",
                 "pts": [[11,4.5],[11,7],[10.9,7],[10.9,4.5]],
                 "sill_height": 0.9, "height": 1.5},
                # 北墙（z=8）朝外窗
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
                # 次卧→客厅
                {"id": "d-liv-bed2",
                 "pts": [[1.5,5],[2.5,5],[2.5,5.1],[1.5,5.1]],
                 "height": 2.0, "to_room": "r-living"},
                # 次卧→卫生间：东墙（x=5）z[5,8] 段
                {"id": "d-bed2-bath",
                 "pts": [[5,6],[5,7],[4.9,7],[4.9,6]],
                 "height": 2.0, "to_room": "r-bath"},
            ],
            "windows": [
                # 西墙（x=0）朝外窗
                {"id": "w-bed2-west",
                 "window_type": "normal",
                 "pts": [[0,6],[0,7.5],[0.1,7.5],[0.1,6]],
                 "sill_height": 0.9, "height": 1.5},
                # 北墙（z=8）朝外飘窗
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
                # 厨房→客厅
                {"id": "d-liv-kitchen",
                 "pts": [[7,1],[7,2],[7.1,2],[7.1,1]],
                 "height": 2.0, "to_room": "r-living"},
            ],
            "windows": [
                # 南墙（z=0）朝外窗
                {"id": "w-kitchen-south",
                 "window_type": "normal",
                 "pts": [[7.5,0],[10,0],[10,0.1],[7.5,0.1]],
                 "sill_height": 0.9, "height": 1.2},
                # 东墙（x=11）侧窗
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
                # 卫生间→次卧
                {"id": "d-bed2-bath",
                 "pts": [[5,6],[5,7],[5.1,7],[5.1,6]],
                 "height": 2.0, "to_room": "r-bed2"},
                # 卫生间→主卧
                {"id": "d-master-bath",
                 "pts": [[7,5.5],[7,6.5],[6.9,6.5],[6.9,5.5]],
                 "height": 2.0, "to_room": "r-master"},
            ],
            "windows": [
                # 北墙（z=8）高窗
                {"id": "w-bath-north",
                 "window_type": "normal",
                 "pts": [[5.3,8],[6.7,8],[6.7,7.9],[5.3,7.9]],
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
