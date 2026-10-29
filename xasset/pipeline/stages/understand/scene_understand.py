# xasset/pipeline/stages/understand/scene_understand.py
"""understand 层 Stage —— 场景理解（四阶段主线：阶段 1 + 阶段 2）。

产物 schema 保持不变（SceneRegion / SceneUnderstandOutput），但算法实现
已从"手写规则式解析"全面切换到 LLM 编排（见 docs/algorithm-rebuild-plan.md）。

当前处于算法重做过渡期：Stage 骨架 + 产物 schema + 归一化工具调用保留，
具体的规则式解析逻辑（词表归一化、门连通规则、手写字段映射）已清理，
待接入 LLMProvider 编排后重做。
"""
from dataclasses import dataclass, field

from xasset.pipeline.context import PipelineContext
from xasset.tools.geometry.normalize import normalize_scene_vector
from xasset.tools.geometry.mesh import polygon_area


@dataclass
class DoorInfo:
    id: str
    pts: list[list[float]]      # 四角坐标 [[x,z]*4]，单位 m
    normal: list[float]         # [nx, nz]，由 pts 计算
    center: list[float]         # [x, z]，由 pts 计算
    width: float                # 宽度 m，由 pts 计算
    height: float               # 高度 m（输入值或默认值）
    to_room: "str | None"
    to_room_type: "str | None" = None  # 连通房间类型
    thickness: "float | None" = None   # 门框厚度 m（可选）
    seg_start: "list[float] | None" = None  # 沿墙线段起点 [x, z]
    seg_end: "list[float] | None" = None    # 沿墙线段终点 [x, z]
    opens_into: "str | None" = None
    door_type: str = "swing"    # "swing" | "sliding"


@dataclass
class WindowInfo:
    id: str
    window_type: str            # "normal" | "bay"
    pts: list[list[float]]
    sill_height: float          # m
    height: float               # m
    width: float                # m，由 pts 计算
    depth: "float | None"       # m，仅 bay window 有值
    thickness: "float | None" = None
    seg_start: "list[float] | None" = None
    seg_end: "list[float] | None" = None


@dataclass
class SceneRegion:
    region_type: str             # 纯功能类别，不含主/次语义
    boundary: list[list[float]]  # polygon vertices, XZ plane
    area: float                  # m²
    height: float = 2.8
    doors: list = field(default_factory=list)
    windows: list = field(default_factory=list)
    structural_edges: list = field(default_factory=list)  # 固定边（承重墙等）
    region_id: str = ""
    priority: int = 0            # 同类型区域的主次排序：0=无主次，1=主，2+=次


@dataclass
class SceneUnderstandOutput:
    scene_type: str
    regions: list[SceneRegion]
    style: str | None = None
    constraints: dict = field(default_factory=dict)


class SceneUnderstandStage:
    name = "scene_understand"
    layer = "understand"
    scene_types = ["*"]

    def __init__(self, orchestrator=None) -> None:
        # 算法重做过渡期：orchestrator 为 None 时走占位路径。
        # 接入 LLM 后，由 LLMStageOrchestrator 驱动"输入+提示词+约束 → LLM → 产物"。
        self._orchestrator = orchestrator

    def run(self, ctx: PipelineContext) -> None:
        if ctx.input.scene_vector:
            output = self._from_scene_vector(ctx.input)
        else:
            output = self._stub_output(ctx.input)
        ctx.stage_outputs["understand"] = output

    def _stub_output(self, inp) -> SceneUnderstandOutput:
        """占位：返回标识性空区域，保证管线骨架可跑通（算法待 LLM 重做）。"""
        return SceneUnderstandOutput(
            scene_type=inp.scene_type,
            style=inp.style,
            regions=[],
        )

    def _from_scene_vector(self, inp) -> SceneUnderstandOutput:
        """占位实现：仅做归一化 + 面积计算，规则式语义解析已清理。

        该路径保留 scene_vector 归一化工具调用（独立几何工具），但不再做
        词表归一化 / 门连通解析等规则式语义推断——这些将由 LLM 编排重做。
        """
        norm = normalize_scene_vector(inp.scene_vector)
        rv = norm.scene_vector
        constraints = dict(inp.constraints or {})

        if norm.excluded_room_ids:
            constraints["_excluded_room_ids"] = norm.excluded_room_ids
        if norm.excluded_opening_ids:
            constraints["_excluded_opening_ids"] = norm.excluded_opening_ids

        regions = []
        for room_idx, room in enumerate(rv.get("rooms", [])):
            boundary = room.get("floor", [])
            area = polygon_area(boundary) if len(boundary) >= 3 else 0.0
            regions.append(SceneRegion(
                region_id=room.get("id", f"room_{room_idx}"),
                region_type=room.get("type") or inp.region_type or "",
                boundary=boundary,
                area=area,
                height=room.get("height") or constraints.get("room_height") or 2.8,
                structural_edges=room.get("structural_walls", []),
            ))

        return SceneUnderstandOutput(
            scene_type=inp.scene_type,
            style=inp.style,
            regions=regions,
            constraints=constraints,
        )
