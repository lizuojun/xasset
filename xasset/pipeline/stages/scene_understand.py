# xasset/pipeline/stages/scene_understand.py
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext

HOUSE_DEFAULTS = {
    "room_height":            2.8,
    "door_height":            2.1,
    "window_sill_height":     0.9,
    "window_height":          1.5,
    "bay_window_sill_height": 0.45,
    "bay_window_height":      1.5,
}


@dataclass
class DoorInfo:
    id: str
    pts: list[list[float]]      # 四角坐标 [[x,z]*4]，单位 m
    normal: list[float]         # [nx, nz]，由 pts 计算
    center: list[float]         # [x, z]，由 pts 计算
    width: float                # 宽度 m，由 pts 计算
    height: float               # 高度 m（输入值或默认值）
    to_room: "str | None"
    to_room_type: "str | None" = None  # 连通房间类型，由调用方解算后传入；无全屋信息时为 None
    thickness: "float | None" = None   # 门框厚度 m（可选，未提供时与墙厚一致）
    seg_start: "list[float] | None" = None  # 沿墙线段起点 [x, z]
    seg_end: "list[float] | None" = None    # 沿墙线段终点 [x, z]


@dataclass
class WindowInfo:
    id: str
    window_type: str            # "normal" | "bay"
    pts: list[list[float]]
    sill_height: float          # m（输入值或默认值）
    height: float               # m（输入值或默认值）
    width: float                # m，由 pts 计算
    depth: "float | None"       # m，仅 bay window 有值
    thickness: "float | None" = None   # 窗框厚度 m（可选，未提供时与墙厚一致）
    seg_start: "list[float] | None" = None  # 沿墙线段起点 [x, z]
    seg_end: "list[float] | None" = None    # 沿墙线段终点 [x, z]


@dataclass
class SceneRegion:
    region_type: str             # "living_room" | "bedroom" | "dining_room" | etc.
    boundary: list[list[float]]  # polygon vertices, XZ plane
    area: float                  # m²
    height: float = field(default=HOUSE_DEFAULTS["room_height"])
    doors: list = field(default_factory=list)
    windows: list = field(default_factory=list)


@dataclass
class SceneUnderstandOutput:
    scene_type: str
    regions: list[SceneRegion]
    style: str | None = None
    constraints: dict = field(default_factory=dict)


def _shoelace_area(boundary: list[list[float]]) -> float:
    """Compute polygon area using the Shoelace formula."""
    n = len(boundary)
    total = 0.0
    for i in range(n):
        x0, z0 = boundary[i][0], boundary[i][1]
        x1, z1 = boundary[(i + 1) % n][0], boundary[(i + 1) % n][1]
        total += x0 * z1 - x1 * z0
    return 0.5 * abs(total)


def _door_geometry(pts):
    """Compute normal, center, width from door pts (4 corners)."""
    p0, p1 = pts[0], pts[1]
    dx = p1[0] - p0[0]
    dz = p1[1] - p0[1]
    width = (dx ** 2 + dz ** 2) ** 0.5
    center = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2]
    length = width if width > 1e-9 else 1.0
    normal = [-dz / length, dx / length]
    return normal, center, width


def _window_width(pts):
    """Compute window width as distance between pts[0] and pts[1]."""
    p0, p1 = pts[0], pts[1]
    dx = p1[0] - p0[0]
    dz = p1[1] - p0[1]
    return (dx ** 2 + dz ** 2) ** 0.5


class SceneUnderstandStage:
    name = "scene_understand"
    layer = "understand"
    scene_types = ["*"]

    def run(self, ctx: PipelineContext) -> None:
        if ctx.input.scene_vector:
            output = self._parse_scene_vector(ctx.input)
        else:
            output = self._stub_output(ctx.input)
        ctx.stage_outputs["understand"] = output

    def _stub_output(self, inp) -> SceneUnderstandOutput:
        """Stub: returns a fixed living room region for any house input."""
        return SceneUnderstandOutput(
            scene_type=inp.scene_type,
            style=inp.style,
            regions=[
                SceneRegion(
                    region_type="living_room",
                    boundary=[[0, 0, 0], [500, 0, 0], [500, 0, 400], [0, 0, 400]],
                    area=20.0,
                )
            ],
        )

    def _parse_scene_vector(self, inp) -> SceneUnderstandOutput:
        """Parse SceneVector JSON into SceneUnderstandOutput."""
        rv = inp.scene_vector
        constraints = inp.constraints or {}
        regions = []

        for room in rv.get("rooms", []):
            # boundary and area
            boundary = room.get("floor", [])
            area = _shoelace_area(boundary) if len(boundary) >= 3 else 0.0

            # height
            height = (
                room.get("height")
                or constraints.get("room_height")
                or HOUSE_DEFAULTS["room_height"]
            )

            # region_type
            region_type = room.get("type") or inp.region_type or "living_room"

            # doors
            doors = []
            for d in room.get("doors", []):
                pts = d.get("pts", [])
                normal, center, width = _door_geometry(pts) if len(pts) >= 2 else ([0, 1], [0, 0], 0.0)
                door_height = (
                    d.get("height")
                    or constraints.get("door_height")
                    or HOUSE_DEFAULTS["door_height"]
                )
                door_thickness = d.get("thickness", None)
                door_seg_start = d.get("seg_start") or (pts[0] if len(pts) >= 2 else None)
                door_seg_end   = d.get("seg_end")   or (pts[1] if len(pts) >= 2 else None)
                doors.append(DoorInfo(
                    id=d["id"],
                    pts=pts,
                    normal=normal,
                    center=center,
                    width=width,
                    height=door_height,
                    to_room=d.get("to_room"),
                    to_room_type=d.get("to_room_type"),
                    thickness=door_thickness,
                    seg_start=door_seg_start,
                    seg_end=door_seg_end,
                ))

            # windows
            windows = []
            for w in room.get("windows", []):
                pts = w.get("pts", [])
                width = _window_width(pts) if len(pts) >= 2 else 0.0
                wtype = w.get("window_type", "normal")
                if wtype == "bay":
                    sill_height = (
                        w.get("sill_height")
                        or constraints.get("bay_window_sill_height")
                        or HOUSE_DEFAULTS["bay_window_sill_height"]
                    )
                    win_height = (
                        w.get("height")
                        or constraints.get("bay_window_height")
                        or HOUSE_DEFAULTS["bay_window_height"]
                    )
                    depth = w.get("depth", None)
                else:
                    sill_height = (
                        w.get("sill_height")
                        or constraints.get("window_sill_height")
                        or HOUSE_DEFAULTS["window_sill_height"]
                    )
                    win_height = (
                        w.get("height")
                        or constraints.get("window_height")
                        or HOUSE_DEFAULTS["window_height"]
                    )
                    depth = None
                win_thickness  = w.get("thickness", None)
                win_seg_start  = w.get("seg_start") or (pts[0] if len(pts) >= 2 else None)
                win_seg_end    = w.get("seg_end")   or (pts[1] if len(pts) >= 2 else None)
                windows.append(WindowInfo(
                    id=w["id"],
                    window_type=wtype,
                    pts=pts,
                    sill_height=sill_height,
                    height=win_height,
                    width=width,
                    depth=depth,
                    thickness=win_thickness,
                    seg_start=win_seg_start,
                    seg_end=win_seg_end,
                ))

            regions.append(SceneRegion(
                region_type=region_type,
                boundary=boundary,
                area=area,
                height=height,
                doors=doors,
                windows=windows,
            ))

        return SceneUnderstandOutput(
            scene_type=inp.scene_type,
            style=inp.style,
            regions=regions,
            constraints=constraints,
        )
