# xasset/pipeline/stages/scene_understand.py
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext
from xasset.pipeline.stages.vector_normalize import normalize_scene_vector

HOUSE_DEFAULTS = {
    "room_height":            2.8,
    "door_height":            2.1,
    "window_sill_height":     0.9,
    "window_height":          1.5,
    "bay_window_sill_height": 0.45,
    "bay_window_height":      1.5,
}

# Room importance for door-opens-into resolution.
# Higher rank = less important = the door opens INTO this room.
ROOM_IMPORTANCE: dict[str, int] = {
    "living_room": 1,
    "dining_room": 2,
    "bedroom":     3,
    "kitchen":     4,
    "bathroom":    5,
    "balcony":     6,
}
_DEFAULT_IMPORTANCE = 9


@dataclass
class DoorInfo:
    id: str
    pts: list[list[float]]      # 四角坐标 [[x,z]*4]，单位 m
    normal: list[float]         # [nx, nz]，由 pts 计算
    center: list[float]         # [x, z]，由 pts 计算
    width: float                # 宽度 m，由 pts 计算
    height: float               # 高度 m（输入值或默认值）
    to_room: "str | None"
    to_room_type: "str | None" = None  # 连通房间类型，第二遍扫描填入
    thickness: "float | None" = None   # 门框厚度 m（可选，未提供时与墙厚一致）
    seg_start: "list[float] | None" = None  # 沿墙线段起点 [x, z]
    seg_end: "list[float] | None" = None    # 沿墙线段终点 [x, z]
    opens_into: "str | None" = None
    # None  → 外门（入户门等），只画门扇线，不画弧
    # str   → 内门，值为应画弧线的那个房间的 region_id
    door_type: str = "swing"
    # "swing"   → 平开门（默认）
    # "sliding" → 推拉门（通阳台，或宽度 > 1.2m）


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
    structural_edges: list = field(default_factory=list)  # boundary edge indices that are structural (承重墙)
    region_id: str = ""          # room id from scene_vector; used by door ownership logic


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


def _door_pos_key(seg_start, seg_end) -> frozenset:
    """Stable position key for a door — order-independent, rounded to 1mm."""
    return frozenset([
        (round(seg_start[0], 3), round(seg_start[1], 3)),
        (round(seg_end[0],   3), round(seg_end[1],   3)),
    ])


_SLIDING_DOOR_WIDTH_THRESHOLD = 1.2  # m — wider than this → sliding


def _detect_door_type(door: "DoorInfo") -> str:
    """Return 'sliding' if door connects to balcony or is wider than threshold."""
    if door.to_room_type == "balcony":
        return "sliding"
    if door.width > _SLIDING_DOOR_WIDTH_THRESHOLD:
        return "sliding"
    return "swing"


def _resolve_door_connectivity(regions: list[SceneRegion]) -> None:
    """
    Second-pass post-processing over all regions:
      1. Fill DoorInfo.to_room_type from the connected room's region_type.
      2. Fill DoorInfo.opens_into:
           None  → exterior door (to_room is None); no arc drawn by renderer
           str   → region_id of the room whose side draws the arc (less important / smaller room)
    Mutates DoorInfo objects in-place.
    """
    id_to_region: dict[str, SceneRegion] = {r.region_id: r for r in regions if r.region_id}

    # Collect candidates per unique door position
    # key → [(region_id, importance, area, door)]
    candidates: dict[frozenset, list] = {}
    for region in regions:
        imp = ROOM_IMPORTANCE.get(region.region_type, _DEFAULT_IMPORTANCE)
        for door in region.doors:
            # 1. Resolve to_room_type
            if door.to_room and door.to_room in id_to_region:
                door.to_room_type = id_to_region[door.to_room].region_type

            # 1b. Detect door_type (needs to_room_type resolved first)
            door.door_type = _detect_door_type(door)

            # 2. Collect for opens_into resolution
            if door.seg_start and door.seg_end:
                key = _door_pos_key(door.seg_start, door.seg_end)
                candidates.setdefault(key, []).append(
                    (region.region_id, imp, region.area, door)
                )

    # Decide opens_into for each unique door position
    for key, cands in candidates.items():
        is_exterior = any(c[3].to_room is None for c in cands)
        if is_exterior:
            # Exterior door (entrance etc.) — no arc, just panel line
            for _, _, _, door in cands:
                door.opens_into = None
        else:
            # Interior shared door — arc on the less-important / smaller room's side
            winner = max(cands, key=lambda c: (c[1], -c[2]))
            winner_id = winner[0]
            for _, _, _, door in cands:
                door.opens_into = winner_id


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
        norm = normalize_scene_vector(inp.scene_vector)
        rv = norm.scene_vector
        constraints = dict(inp.constraints or {})
        regions = []

        for room_idx, room in enumerate(rv.get("rooms", [])):
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
                region_id=room.get("id", f"room_{room_idx}"),
                region_type=region_type,
                boundary=boundary,
                area=area,
                height=height,
                doors=doors,
                windows=windows,
                structural_edges=room.get("structural_walls", []),
            ))

        # Second pass: resolve door connectivity and ownership across all regions
        _resolve_door_connectivity(regions)

        if norm.excluded_room_ids:
            constraints["_excluded_room_ids"] = norm.excluded_room_ids
        if norm.excluded_opening_ids:
            constraints["_excluded_opening_ids"] = norm.excluded_opening_ids

        return SceneUnderstandOutput(
            scene_type=inp.scene_type,
            style=inp.style,
            regions=regions,
            constraints=constraints,
        )
