# xasset/pipeline/stages/vector_normalize.py
"""
Vector normalization utilities for scene_vector data.

Call normalize_scene_vector() BEFORE passing data to Pipeline / DB storage.
Thresholds (configurable, defaults match architecture spec):
  min_seg_len = 0.05 m  (5 cm)
  angle_deg   = 5.0 °
  dev_dist    = 0.05 m  (5 cm)
All output polygons are CCW (counter-clockwise).
"""
from __future__ import annotations
import copy
import math
from dataclasses import dataclass, field
from xasset.pipeline.stages.mesh_utils import check_poly_clock


@dataclass
class NormalizeResult:
    scene_vector: dict
    excluded_room_ids: list[str] = field(default_factory=list)
    excluded_opening_ids: list[str] = field(default_factory=list)


def _dist(a: list[float], b: list[float]) -> float:
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def _perp_dist(b: list[float], a: list[float], c: list[float]) -> float:
    """Perpendicular distance from point b to line a→c."""
    ax, az = a
    cx, cz = c
    bx, bz = b
    dx, dz = cx - ax, cz - az
    length = math.sqrt(dx * dx + dz * dz)
    if length < 1e-9:
        return _dist(b, a)
    return abs(dx * (az - bz) - dz * (ax - bx)) / length


def _angle_deg(a: list[float], b: list[float], c: list[float]) -> float:
    """Deflection angle at vertex b (0° = straight/collinear)."""
    v1 = [b[0] - a[0], b[1] - a[1]]
    v2 = [c[0] - b[0], c[1] - b[1]]
    len1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    len2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
    if len1 < 1e-9 or len2 < 1e-9:
        return 0.0
    cos_a = (v1[0] * v2[0] + v1[1] * v2[1]) / (len1 * len2)
    cos_a = max(-1.0, min(1.0, cos_a))
    deflection = math.degrees(math.acos(cos_a))
    return min(deflection, 180.0 - deflection)


def normalize_polygon(
    pts: list[list[float]],
    min_seg_len: float = 0.05,
    angle_deg: float = 5.0,
    dev_dist: float = 0.05,
    enforce_ccw: bool = True,
) -> list[list[float]] | None:
    """
    Clean a 2D polygon by removing noise vertices, then enforce CCW winding.
    Returns None if fewer than 3 vertices remain after cleaning.
    """
    pts = [list(p) for p in pts]

    for _ in range(100):
        changed = False
        n = len(pts)
        if n < 3:
            return None

        # Pass A: short segment removal
        to_remove = set()
        for i in range(n):
            j = (i + 1) % n
            if j in to_remove:
                continue
            if _dist(pts[i], pts[j]) < min_seg_len:
                to_remove.add(j)
        if to_remove:
            pts = [p for idx, p in enumerate(pts) if idx not in to_remove]
            changed = True
            if len(pts) < 3:
                return None
            continue

        # Pass B: collinearity simplification
        n = len(pts)
        to_remove = set()
        for i in range(n):
            if i in to_remove:
                continue
            a = pts[(i - 1) % n]
            b = pts[i]
            c = pts[(i + 1) % n]
            if _perp_dist(b, a, c) < dev_dist or _angle_deg(a, b, c) < angle_deg:
                to_remove.add(i)
        if to_remove:
            pts = [p for idx, p in enumerate(pts) if idx not in to_remove]
            changed = True
            if len(pts) < 3:
                return None

        if not changed:
            break

    if len(pts) < 3:
        return None
    # Step C: enforce CCW winding (skip for openings — door/window pts must keep
    # original vertex order so that pts[0]/pts[1] remain the wall-face endpoints,
    # which _door_pos_key relies on for cross-room deduplication)
    if enforce_ccw and check_poly_clock(pts):
        pts = pts[::-1]
    return pts


def normalize_scene_vector(
    scene_vector: dict,
    min_seg_len: float = 0.05,
    angle_deg: float = 5.0,
    dev_dist: float = 0.05,
) -> NormalizeResult:
    """
    Normalize all polygon data in a scene_vector dict (deep copy).
    Degenerate regions/openings are excluded with clear markers.
    """
    rv = copy.deepcopy(scene_vector)
    excluded_rooms: list[str] = []
    excluded_openings: list[str] = []
    clean_rooms = []

    for room in rv.get("rooms", []):
        room_id = room.get("id", "")

        floor = room.get("floor", [])
        clean_floor = normalize_polygon(floor, min_seg_len, angle_deg, dev_dist)
        if clean_floor is None:
            excluded_rooms.append(room_id)
            continue
        room["floor"] = clean_floor

        clean_doors = []
        for d in room.get("doors", []):
            pts = d.get("pts", [])
            # enforce_ccw=False: door pts are wall-opening rectangles, not room polygons.
            # Reversing winding would change pts[0]/pts[1] to the interior side,
            # breaking the _door_pos_key used for cross-room dedup in scene_understand.
            clean_pts = normalize_polygon(pts, min_seg_len, angle_deg, dev_dist, enforce_ccw=False) if len(pts) >= 3 else pts
            if clean_pts is None:
                excluded_openings.append(d.get("id", ""))
                continue
            d["pts"] = clean_pts
            clean_doors.append(d)
        room["doors"] = clean_doors

        clean_windows = []
        for w in room.get("windows", []):
            pts = w.get("pts", [])
            # Same reasoning as doors: no CCW enforcement for window opening pts.
            clean_pts = normalize_polygon(pts, min_seg_len, angle_deg, dev_dist, enforce_ccw=False) if len(pts) >= 3 else pts
            if clean_pts is None:
                excluded_openings.append(w.get("id", ""))
                continue
            w["pts"] = clean_pts
            clean_windows.append(w)
        room["windows"] = clean_windows

        clean_rooms.append(room)

    rv["rooms"] = clean_rooms
    return NormalizeResult(
        scene_vector=rv,
        excluded_room_ids=excluded_rooms,
        excluded_opening_ids=excluded_openings,
    )
