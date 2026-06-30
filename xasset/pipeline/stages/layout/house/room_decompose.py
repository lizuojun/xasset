# xasset/pipeline/stages/layout/house/room_decompose.py
"""Room Decomposer — Step 2 of the Layout Layer.

Converts a SceneRegion into a flat list of WallSegments, each carrying:
  • geometric metadata (position, normal, length, corner types)
  • depth_profile (ray-cast depth samples along the segment)
  • wall_quality score

Public API
----------
    from xasset.pipeline.stages.layout.house.room_decompose import RoomDecomposer, WallSegment
    segs = RoomDecomposer().decompose(region)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from xasset.pipeline.stages.understand.scene_understand import SceneRegion

# ── Constants ─────────────────────────────────────────────────────────────────

CURTAIN_WIDTH     = 0.23   # m — curtain placement zone on each side of a window
DOOR_CORRIDOR     = 1.2    # m — keep-clear depth in front of a door opening
DEPTH_SAMPLE_STEP = 0.2    # m — uniform ray-cast sampling resolution
REF_LENGTH        = 3.0    # m — reference wall length for quality scoring
MIN_SEG_LEN       = 0.05   # m — segments shorter than this are discarded
DEPTH_MERGE_TOL   = 0.1    # m — adjacent depth samples within this range are merged
DEPTH_VIZ_SCALE   = 0.1    # factor: bar_height = depth * DEPTH_VIZ_SCALE in plot coords

CORNER_CONCAVE = "concave"
CORNER_CONVEX  = "convex"
CORNER_FLAT    = "flat"

_PERP_TOL = 0.15   # m — max perpendicular distance for opening → edge matching


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class DepthSample:
    """A merged depth interval along a WallSegment."""
    t0: float     # start ratio along segment [0, 1]
    t1: float     # end ratio along segment [0, 1]
    depth: float  # average available depth in metres toward room interior


@dataclass
class CurtainZone:
    """Curtain placement zone beside a window, stored separately from wall segments."""
    p0: list[float]
    p1: list[float]
    width: float
    inward_normal: list[float]
    window_id: str


@dataclass
class WallSegment:
    """One contiguous stretch of a boundary edge, annotated for layout use."""
    p0: list[float]             # start point [x, z]
    p1: list[float]             # end point [x, z]
    length: float               # metres
    inward_normal: list[float]  # unit vector pointing into the room [nx, nz]
    seg_type: str               # "wall" | "door" | "window"
    corner_pre: str             # corner type at p0: "concave"|"convex"|"flat"
    corner_post: str            # corner type at p1: "concave"|"convex"|"flat"
    edge_idx: int               # original boundary edge this segment belongs to
    depth_profile: list[DepthSample] = field(default_factory=list)
    wall_quality: float = 0.0
    opens_into: "str | None" = None  # door only: which room_id the door opens into
    used_ranges: list = field(default_factory=list)  # filled by GroupPlacer
# ── Geometry helpers ──────────────────────────────────────────────────────────

def _dist(a: list[float], b: list[float]) -> float:
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def _lerp(p0: list[float], p1: list[float], t: float) -> list[float]:
    return [p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1])]


def _proj_t(p0: list[float], p1: list[float], pt: list[float]) -> float | None:
    """Parametric t of pt projected onto segment p0→p1 (may exceed [0,1])."""
    dx = p1[0] - p0[0]
    dz = p1[1] - p0[1]
    len2 = dx * dx + dz * dz
    if len2 < 1e-12:
        return None
    return ((pt[0] - p0[0]) * dx + (pt[1] - p0[1]) * dz) / len2


def _perp_dist_to_line(pt: list[float], p0: list[float], p1: list[float]) -> float:
    """Perpendicular distance from pt to the infinite line through p0→p1."""
    dx = p1[0] - p0[0]
    dz = p1[1] - p0[1]
    length = math.sqrt(dx * dx + dz * dz)
    if length < 1e-9:
        return _dist(pt, p0)
    return abs((pt[0] - p0[0]) * dz - (pt[1] - p0[1]) * dx) / length


def _inward_normal(p0: list[float], p1: list[float]) -> list[float]:
    """Unit inward normal of edge p0→p1 in a CCW polygon (left perpendicular)."""
    dx = p1[0] - p0[0]
    dz = p1[1] - p0[1]
    length = math.sqrt(dx * dx + dz * dz)
    if length < 1e-9:
        return [0.0, 1.0]
    return [-dz / length, dx / length]


def _ray_cast_depth(
    origin: list[float],
    direction: list[float],
    boundary: list[list[float]],
    exclude_edge: int,
) -> float:
    """
    Cast a ray from origin in direction; return distance to nearest boundary edge
    (excluding exclude_edge).  Returns 0.0 if no forward intersection is found.

    Uses Cramer's rule to solve:
        origin + t*d  =  boundary[j] + s*(boundary[j+1] - boundary[j])
    """
    n = len(boundary)
    d_x, d_z = direction
    min_t = 1e9

    for j in range(n):
        if j == exclude_edge:
            continue
        ax, az = boundary[j]
        bx, bz = boundary[(j + 1) % n]
        ex, ez = bx - ax, bz - az          # edge direction
        fx, fz = ax - origin[0], az - origin[1]  # origin→edge_start

        det = ex * d_z - ez * d_x
        if abs(det) < 1e-9:
            continue  # parallel

        t = (ex * fz - ez * fx) / det
        s = (d_x * fz - d_z * fx) / det

        if t > 1e-6 and -1e-6 <= s <= 1.0 + 1e-6:
            if t < min_t:
                min_t = t

    return min_t if min_t < 1e9 else 0.0


# ── Corner detection ──────────────────────────────────────────────────────────

def _vertex_corners(boundary: list[list[float]]) -> list[str]:
    """
    Classify each vertex of a CCW polygon by interior corner type.

    Cross product of incoming × outgoing edge vectors at vertex i:
      cross < 0  →  right turn  →  concave (reflex, interior angle > 180°)
      cross > 0  →  left  turn  →  convex
      cross ≈ 0  →  collinear   →  flat
    """
    n = len(boundary)
    corners: list[str] = []
    for i in range(n):
        prev_p = boundary[(i - 1) % n]
        curr_p = boundary[i]
        next_p = boundary[(i + 1) % n]
        # Incoming edge vector
        v1x = curr_p[0] - prev_p[0]
        v1z = curr_p[1] - prev_p[1]
        # Outgoing edge vector
        v2x = next_p[0] - curr_p[0]
        v2z = next_p[1] - curr_p[1]
        cross = v1x * v2z - v1z * v2x
        if cross < -1e-9:
            corners.append(CORNER_CONCAVE)
        elif cross > 1e-9:
            corners.append(CORNER_CONVEX)
        else:
            corners.append(CORNER_FLAT)
    return corners


# ── Opening → edge projection ─────────────────────────────────────────────────

def _opening_abs_on_edge(
    p0: list[float],
    p1: list[float],
    L: float,
    seg_start: list[float],
    seg_end: list[float],
) -> tuple[float, float] | None:
    """
    Project a door/window opening's wall-face endpoints onto edge p0→p1.
    Returns (abs_start, abs_end) in metres along the edge, or None if not on
    this edge (perp distance > _PERP_TOL or projections outside [-5%,105%]).
    """
    mid = [(seg_start[0] + seg_end[0]) / 2.0, (seg_start[1] + seg_end[1]) / 2.0]
    if _perp_dist_to_line(mid, p0, p1) > _PERP_TOL:
        return None

    t0 = _proj_t(p0, p1, seg_start)
    t1 = _proj_t(p0, p1, seg_end)
    if t0 is None or t1 is None:
        return None
    if not (-0.05 <= t0 <= 1.05 and -0.05 <= t1 <= 1.05):
        return None

    abs0 = max(0.0, min(L, min(t0, t1) * L))
    abs1 = max(0.0, min(L, max(t0, t1) * L))
    if abs1 - abs0 < 1e-4:
        return None
    return (abs0, abs1)


def _openings_on_edge(
    p0: list[float],
    p1: list[float],
    L: float,
    doors: list,
    windows: list,
) -> list[tuple[float, float, str, str | None]]:
    """
    Return sorted list of (abs_start, abs_end, type_str, opens_into) for all
    doors and windows whose wall-face segment falls on edge p0→p1.
    opens_into is the door's opens_into field (None for exterior doors, region_id
    for interior doors); None for windows.
    """
    result: list[tuple[float, float, str, str | None]] = []
    for d in doors:
        if d.seg_start and d.seg_end:
            r = _opening_abs_on_edge(p0, p1, L, d.seg_start, d.seg_end)
            if r:
                result.append((r[0], r[1], "door", d.opens_into))
    for w in windows:
        if w.seg_start and w.seg_end:
            r = _opening_abs_on_edge(p0, p1, L, w.seg_start, w.seg_end)
            if r:
                result.append((r[0], r[1], "window", None))
    result.sort(key=lambda x: x[0])
    return result


# ── Edge segment builder ──────────────────────────────────────────────────────

def _build_edge_segments(
    p0: list[float],
    p1: list[float],
    edge_idx: int,
    corner_pre: str,
    corner_post: str,
    openings: list[tuple[float, float, str, str | None]],
) -> list[WallSegment]:
    """
    Build WallSegments for one boundary edge: wall segments between openings,
    plus the opening segments themselves.
    """
    L = _dist(p0, p1)
    if L < MIN_SEG_LEN:
        return []

    normal = _inward_normal(p0, p1)

    # Gather all intervals: wall gaps between openings
    intervals: list[tuple[float, float, str, str | None]] = []
    pos = 0.0
    for abs0, abs1, otype, opens_into in openings:
        if abs0 > pos + 1e-6:
            intervals.append((pos, abs0, "wall", None))
        intervals.append((abs0, abs1, otype, opens_into))
        pos = abs1
    if pos < L - 1e-6:
        intervals.append((pos, L, "wall", None))

    # Filter minimum length
    final = [(s, e, t, oi) for s, e, t, oi in intervals if e - s >= MIN_SEG_LEN]
    n_final = len(final)

    segs: list[WallSegment] = []
    for i, (start, end, itype, _opens_into) in enumerate(final):
        seg_len = end - start
        pt0 = _lerp(p0, p1, start / L)
        pt1 = _lerp(p0, p1, end / L)
        c_pre  = corner_pre  if i == 0           else CORNER_FLAT
        c_post = corner_post if i == n_final - 1 else CORNER_FLAT
        segs.append(WallSegment(
            p0=pt0,
            p1=pt1,
            length=seg_len,
            inward_normal=normal,
            seg_type=itype,
            corner_pre=c_pre,
            corner_post=c_post,
            edge_idx=edge_idx,
            opens_into=_opens_into,
        ))
    return segs


# ── Depth profile ─────────────────────────────────────────────────────────────

def _point_to_segment_dist(
    pt: list[float],
    a: list[float],
    b: list[float],
) -> float:
    """Shortest distance from pt to segment a→b."""
    ab_x, ab_z = b[0] - a[0], b[1] - a[1]
    len2 = ab_x * ab_x + ab_z * ab_z
    if len2 < 1e-12:
        return _dist(pt, a)
    t = max(0.0, min(1.0, ((pt[0] - a[0]) * ab_x + (pt[1] - a[1]) * ab_z) / len2))
    proj = [a[0] + t * ab_x, a[1] + t * ab_z]
    return _dist(pt, proj)


def _adjacent_door_cap(
    origin: list[float],
    seg: WallSegment,
    boundary: list[list[float]],
    region_doors: list,
) -> float:
    """
    For a sample point on a wall segment, check doors on adjacent edges.
    If a door is close to the shared corner (≤ 1m), its width projects onto
    the current wall, creating a shadow zone.  Within the zone depth is capped
    at the door's distance from the shared corner.
    """
    n = len(boundary)
    best_cap = float('inf')
    ei = seg.edge_idx

    for door in region_doors:
        if not door.seg_start or not door.seg_end:
            continue

        door_abs = None
        shadow_corner = None  # 0 = shadow from seg.p0, 1 = shadow from seg.p1

        # ── Door on edge_{ei-1} — shared corner is boundary[ei] (END of edge_prev)
        edge_prev = (ei - 1) % n
        p_prev_start = boundary[edge_prev]
        p_prev_end   = boundary[ei]
        L_prev = _dist(p_prev_start, p_prev_end)
        door_abs = _opening_abs_on_edge(
            p_prev_start, p_prev_end, L_prev,
            door.seg_start, door.seg_end,
        )
        if door_abs is not None:
            # door_abs measures from p_prev_start; corner is at p_prev_end
            door_corner_dist = L_prev - door_abs[1]
            shadow_corner = 0  # shadow from seg.p0
        else:
            # ── Door on edge_{ei+1} — shared corner is boundary[(ei+1)%n] (START of edge_next)
            edge_next = (ei + 1) % n
            p_next_start = boundary[edge_next]
            p_next_end   = boundary[(edge_next + 1) % n]
            L_next = _dist(p_next_start, p_next_end)
            door_abs = _opening_abs_on_edge(
                p_next_start, p_next_end, L_next,
                door.seg_start, door.seg_end,
            )
            if door_abs is not None:
                door_corner_dist = door_abs[0]  # closer endpoint to corner
                shadow_corner = 1  # shadow from seg.p1

        if shadow_corner is None:
            continue

        shadow_len = abs(door_abs[1] - door_abs[0])
        # Sample position along current EDGE relative to the shared corner
        # (not relative to this WallSegment, which may be a sub-span of the edge)
        if shadow_corner == 0:
            corner_dir = boundary[(ei + 1) % n]
            sample_dist = _proj_t(boundary[ei], corner_dir, origin)
        else:
            corner_dir = boundary[ei]
            sample_dist = _proj_t(boundary[(ei + 1) % n], corner_dir, origin)
        if sample_dist is None:
            continue
        sample_dist = sample_dist * _dist(
            boundary[ei], boundary[(ei + 1) % n]
        )

        if 0 <= sample_dist <= shadow_len:
            best_cap = min(best_cap, door_corner_dist)

    return best_cap


def _opposite_door_cap(
    origin: list[float],
    seg: WallSegment,
    boundary: list[list[float]],
    region_doors: list,
    region_id: str,
) -> float:
    """
    For a sample point on a wall segment, check if any door that opens INTO this
    room projects onto this point (e.g. entry door projecting onto the opposite
    wall).  If so, cap depth at ``distance_to_door_wall - DOOR_CORRIDOR``,
    leaving passage clearance in front of the door.
    """
    n = len(boundary)
    best_cap = float('inf')
    ei = seg.edge_idx

    for door in region_doors:
        if not door.seg_start or not door.seg_end:
            continue
        # Only doors that open INTO this room
        if door.opens_into is not None and door.opens_into != region_id:
            continue

        for j in range(n):
            if j == ei:
                continue
            p0 = boundary[j]
            p1 = boundary[(j + 1) % n]
            L = _dist(p0, p1)
            door_abs = _opening_abs_on_edge(p0, p1, L, door.seg_start, door.seg_end)
            if door_abs is None:
                continue

            # Project origin onto door's edge line; check if within door opening
            t = _proj_t(p0, p1, origin)
            if t is not None and door_abs[0] <= t * L <= door_abs[1]:
                dist_to_door_wall = _perp_dist_to_line(origin, p0, p1)
                cap = max(0.0, dist_to_door_wall - DOOR_CORRIDOR)
                best_cap = min(best_cap, cap)
            break  # door found on edge j, no need to check other edges

    return best_cap

def _compute_depth_profile(
    seg: WallSegment,
    boundary: list[list[float]],
    region_doors: list,
    region_id: str,
) -> list[DepthSample]:
    """
    Ray-cast from uniformly spaced points along the segment toward the room
    interior.  Merge consecutive samples whose depths are within DEPTH_MERGE_TOL.

    Depth is further capped by doors on adjacent walls: if a sample point lies
    within the shadow of a nearby door on a neighbouring wall, the depth is
    constrained to the distance from the sample point to the door opening.
    """
    L = seg.length
    n_samples = max(3, math.ceil(L / DEPTH_SAMPLE_STEP) + 1)
    nx, nz = seg.inward_normal

    raw_depths: list[float] = []
    for k in range(n_samples):
        t = k / (n_samples - 1)
        origin = _lerp(seg.p0, seg.p1, t)
        depth = _ray_cast_depth(origin, [nx, nz], boundary, seg.edge_idx)
        adj_cap = _adjacent_door_cap(origin, seg, boundary, region_doors)
        opp_cap = _opposite_door_cap(origin, seg, boundary, region_doors, region_id)
        depth = min(depth, adj_cap, opp_cap)
        raw_depths.append(depth)

    # Merge consecutive samples within DEPTH_MERGE_TOL into one DepthSample
    profile: list[DepthSample] = []
    i = 0
    while i < n_samples:
        j = i + 1
        while j < n_samples and abs(raw_depths[j] - raw_depths[i]) <= DEPTH_MERGE_TOL:
            j += 1
        avg_depth = sum(raw_depths[i:j]) / (j - i)
        t0 = i / (n_samples - 1) if n_samples > 1 else 0.0
        t1 = min(j / (n_samples - 1), 1.0) if n_samples > 1 else 1.0
        profile.append(DepthSample(t0=t0, t1=t1, depth=avg_depth))
        i = j

    return profile


# ── Wall quality ──────────────────────────────────────────────────────────────

def _wall_quality(seg: WallSegment) -> float:
    """
    Segment-level quality score in [0, 1]:
      0.5 * corner_bonus  (1.0 if either endpoint is concave, else 0.0)
      0.5 * length_score  (min(length / REF_LENGTH, 1.0))
    """
    corner_bonus = 1.0 if (
        seg.corner_pre == CORNER_CONCAVE or seg.corner_post == CORNER_CONCAVE
    ) else 0.0
    length_score = min(seg.length / REF_LENGTH, 1.0)
    return 0.5 * corner_bonus + 0.5 * length_score


# ── Curtain zones ──────────────────────────────────────────────────────────────

def _build_curtain_zones(
    p0: list[float],
    p1: list[float],
    L: float,
    windows: list,
) -> list[CurtainZone]:
    """Build CurtainZone objects for each window on edge p0→p1.

    The zone spans from curtain_left of the window to curtain_right,
    merging the window segment and its adjacent CURTAIN_WIDTH buffers into
    a single continuous placement zone.  Does not affect wall segmentation.
    """
    normal = _inward_normal(p0, p1)
    zones: list[CurtainZone] = []
    for w in windows:
        if not w.seg_start or not w.seg_end:
            continue
        r = _opening_abs_on_edge(p0, p1, L, w.seg_start, w.seg_end)
        if r is None:
            continue
        abs0, abs1 = r
        c0 = max(0.0, abs0 - CURTAIN_WIDTH)
        c1 = min(L, abs1 + CURTAIN_WIDTH)
        if c1 - c0 < 1e-4:
            continue
        start = _lerp(p0, p1, c0 / L)
        end   = _lerp(p0, p1, c1 / L)
        zones.append(CurtainZone(
            p0=start, p1=end,
            width=c1 - c0,
            inward_normal=normal,
            window_id=w.id,
        ))
    return zones


# ── RoomDecomposer ────────────────────────────────────────────────────────────

class RoomDecomposer:
    """Decomposes a SceneRegion into annotated WallSegments and CurtainZones."""

    def decompose(self, region: SceneRegion) -> tuple[list[WallSegment], list[CurtainZone]]:
        """
        Parameters
        ----------
        region : SceneRegion
            Room with CCW boundary polygon, DoorInfo list, and WindowInfo list.

        Returns
        -------
        tuple[list[WallSegment], list[CurtainZone]]
            WallSegments in boundary-edge traversal order (wall / door / window),
            plus curtain placement zones for each window.
            Only wall segments carry depth_profile and wall_quality.
        """
        boundary = region.boundary
        n = len(boundary)
        if n < 3:
            return [], []

        vc = _vertex_corners(boundary)
        all_segs: list[WallSegment] = []
        all_curtains: list[CurtainZone] = []

        for j in range(n):
            p0 = boundary[j]
            p1 = boundary[(j + 1) % n]

            L = _dist(p0, p1)
            if L < MIN_SEG_LEN:
                continue

            openings = _openings_on_edge(p0, p1, L, region.doors, region.windows)
            edge_segs = _build_edge_segments(
                p0, p1, j,
                vc[j], vc[(j + 1) % n],
                openings,
            )
            all_segs.extend(edge_segs)

            curtains = _build_curtain_zones(p0, p1, L, region.windows)
            all_curtains.extend(curtains)

        # Compute depth_profile and wall_quality, splitting at depth jumps.
        # Window segments also get depth/quality (furniture can go under a window).
        split_segs: list[WallSegment] = []
        for seg in all_segs:
            if seg.seg_type not in ("wall", "window"):
                split_segs.append(seg)
                continue
            seg.depth_profile = _compute_depth_profile(seg, boundary, region.doors, region.region_id)
            if len(seg.depth_profile) <= 1:
                seg.wall_quality = _wall_quality(seg)
                split_segs.append(seg)
                continue
            # Split at depth boundaries
            p0, p1 = seg.p0, seg.p1
            normal = seg.inward_normal
            edge_idx = seg.edge_idx
            for i, ds in enumerate(seg.depth_profile):
                sub_len = seg.length * (ds.t1 - ds.t0)
                if sub_len < MIN_SEG_LEN:
                    continue
                pt0 = _lerp(p0, p1, ds.t0)
                pt1 = _lerp(p0, p1, ds.t1)
                c_pre = seg.corner_pre if i == 0 else CORNER_FLAT
                c_post = seg.corner_post if i == len(seg.depth_profile) - 1 else CORNER_FLAT
                sub = WallSegment(
                    p0=pt0, p1=pt1, length=sub_len,
                    inward_normal=normal, seg_type=seg.seg_type,
                    corner_pre=c_pre, corner_post=c_post,
                    edge_idx=edge_idx,
                    depth_profile=[ds],
                )
                sub.wall_quality = _wall_quality(sub)
                split_segs.append(sub)
        all_segs = split_segs

        return all_segs, all_curtains
