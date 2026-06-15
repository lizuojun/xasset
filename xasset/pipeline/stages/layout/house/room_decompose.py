# xasset/pipeline/stages/layout/house/room_decompose.py
"""Room Decomposer — Step 2 of the Layout Layer.

Converts a SceneRegion into a flat list of WallSegments, each carrying:
  • geometric metadata (position, normal, length, corner types)
  • depth_profile (ray-cast depth samples along the segment)
  • wall_quality score
  • is_logical flag (aisle / curtain protective zones adjacent to openings)

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

AISLE_WIDTH       = 0.9    # m — protective zone on each side of a door opening
CURTAIN_WIDTH     = 0.23   # m — protective zone on each side of a window opening
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
class WallSegment:
    """One contiguous stretch of a boundary edge, annotated for layout use."""
    p0: list[float]             # start point [x, z]
    p1: list[float]             # end point [x, z]
    length: float               # metres
    inward_normal: list[float]  # unit vector pointing into the room [nx, nz]
    seg_type: str               # "wall" | "door" | "window" | "aisle" | "curtain"
    is_logical: bool            # True for aisle/curtain protective zones
    corner_pre: str             # corner type at p0: "concave"|"convex"|"flat"
    corner_post: str            # corner type at p1: "concave"|"convex"|"flat"
    edge_idx: int               # original boundary edge this segment belongs to
    depth_profile: list[DepthSample] = field(default_factory=list)
    wall_quality: float = 0.0
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
) -> list[tuple[float, float, str]]:
    """
    Return sorted list of (abs_start, abs_end, type_str) for all doors and
    windows whose wall-face segment falls on edge p0→p1.
    """
    result: list[tuple[float, float, str]] = []
    for d in doors:
        if d.seg_start and d.seg_end:
            r = _opening_abs_on_edge(p0, p1, L, d.seg_start, d.seg_end)
            if r:
                result.append((r[0], r[1], "door"))
    for w in windows:
        if w.seg_start and w.seg_end:
            r = _opening_abs_on_edge(p0, p1, L, w.seg_start, w.seg_end)
            if r:
                result.append((r[0], r[1], "window"))
    result.sort(key=lambda x: x[0])
    return result


# ── Edge segment builder ──────────────────────────────────────────────────────

def _build_edge_segments(
    p0: list[float],
    p1: list[float],
    edge_idx: int,
    corner_pre: str,
    corner_post: str,
    openings: list[tuple[float, float, str]],
) -> list[WallSegment]:
    """
    Build all WallSegments for one boundary edge, including logical aisle/curtain
    buffers adjacent to each opening.

    Buffer widths are clipped against the space available between openings so
    they never overlap with a neighbouring opening's interval.
    """
    L = _dist(p0, p1)
    if L < MIN_SEG_LEN:
        return []

    normal = _inward_normal(p0, p1)
    n_open = len(openings)

    # ── Build raw interval list ───────────────────────────────────────────────
    # Each entry: (start_m, end_m, seg_type, is_logical)
    raw: list[tuple[float, float, str, bool]] = []

    for i, (abs0, abs1, otype) in enumerate(openings):
        clip     = AISLE_WIDTH if otype == "door" else CURTAIN_WIDTH
        buf_type = "aisle"    if otype == "door" else "curtain"

        # Pre-buffer: clipped so it doesn't reach into the previous opening
        prev_end = openings[i - 1][1] if i > 0 else 0.0
        pre_len  = max(0.0, min(clip, abs0 - prev_end))
        if pre_len > 1e-6:
            raw.append((abs0 - pre_len, abs0, buf_type, True))

        # Opening itself
        raw.append((abs0, abs1, otype, False))

        # Post-buffer: clipped so it doesn't reach into the next opening
        next_start = openings[i + 1][0] if i < n_open - 1 else L
        post_len   = max(0.0, min(clip, next_start - abs1))
        if post_len > 1e-6:
            raw.append((abs1, abs1 + post_len, buf_type, True))

    raw.sort(key=lambda x: x[0])

    # ── Sweep: fill gaps with wall and handle any residual overlaps ───────────
    filled: list[tuple[float, float, str, bool]] = []
    pos = 0.0
    for start, end, itype, is_logical in raw:
        start = max(start, pos)      # truncate overlap
        if end <= start + 1e-6:
            continue
        if start > pos + 1e-6:
            filled.append((pos, start, "wall", False))
        filled.append((start, end, itype, is_logical))
        pos = end

    if pos < L - 1e-6:
        filled.append((pos, L, "wall", False))

    # ── Filter minimum length ─────────────────────────────────────────────────
    final = [(s, e, t, lg) for s, e, t, lg in filled if e - s >= MIN_SEG_LEN]
    n_final = len(final)

    # ── Convert intervals to WallSegment objects ──────────────────────────────
    segs: list[WallSegment] = []
    for i, (start, end, itype, is_logical) in enumerate(final):
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
            is_logical=is_logical,
            corner_pre=c_pre,
            corner_post=c_post,
            edge_idx=edge_idx,
        ))
    return segs


# ── Depth profile ─────────────────────────────────────────────────────────────

def _compute_depth_profile(
    seg: WallSegment,
    boundary: list[list[float]],
) -> list[DepthSample]:
    """
    Ray-cast from uniformly spaced points along the segment toward the room
    interior.  Merge consecutive samples whose depths are within DEPTH_MERGE_TOL.

    Sample count = max(3, ceil(length / DEPTH_SAMPLE_STEP) + 1) so that even
    very short segments get at least 3 samples (endpoints + midpoint).
    """
    L = seg.length
    n_samples = max(3, math.ceil(L / DEPTH_SAMPLE_STEP) + 1)
    nx, nz = seg.inward_normal

    raw_depths: list[float] = []
    for k in range(n_samples):
        t = k / (n_samples - 1)
        origin = _lerp(seg.p0, seg.p1, t)
        depth  = _ray_cast_depth(origin, [nx, nz], boundary, seg.edge_idx)
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
        t1 = (j - 1) / (n_samples - 1) if n_samples > 1 else 1.0
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


# ── RoomDecomposer ────────────────────────────────────────────────────────────

class RoomDecomposer:
    """Decomposes a SceneRegion into an annotated list of WallSegments."""

    def decompose(self, region: SceneRegion) -> list[WallSegment]:
        """
        Parameters
        ----------
        region : SceneRegion
            Room with CCW boundary polygon (floor vertices), DoorInfo list,
            and WindowInfo list (all populated by SceneUnderstandStage).

        Returns
        -------
        list[WallSegment]
            All segments in boundary-edge traversal order.  Geometric segments
            (wall / door / window) and logical segments (aisle / curtain) are
            interleaved.  Only geometric wall segments carry depth_profile and
            wall_quality.
        """
        boundary = region.boundary
        n = len(boundary)
        if n < 3:
            return []

        vc = _vertex_corners(boundary)
        all_segs: list[WallSegment] = []

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

        # Compute depth_profile and wall_quality for geometric wall segments only
        for seg in all_segs:
            if seg.seg_type == "wall" and not seg.is_logical:
                seg.depth_profile = _compute_depth_profile(seg, boundary)
                seg.wall_quality  = _wall_quality(seg)

        return all_segs
