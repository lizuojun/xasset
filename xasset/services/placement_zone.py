# xasset/services/placement_zone.py
"""PlacementZoneService — generic 3D mesh placement-zone analysis.

Analyses an arbitrary triangle mesh and identifies regions where other
objects can be placed or attached.  Results are cached in an optional
asset_store (dict keyed by asset_id) under the key "placement_zones".
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Public data structures
# ---------------------------------------------------------------------------

@dataclass
class PlacementZone:
    zone_type: str              # "stable_top" | "stable_side" | "attach_point" | "cavity"
    center: list[float]         # [x, y, z]
    normal: list[float]         # [nx, ny, nz], normalised
    area: float                 # surface area in mesh units²
    bounds: list[list[float]]   # bounding-box corners [[x,y,z], ...]
    stability_score: float      # 0.0 – 1.0


@dataclass
class PlacementZoneResult:
    asset_id: str
    zones: list[PlacementZone] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _zone_to_dict(z: PlacementZone) -> dict:
    return asdict(z)


def _dict_to_zone(d: dict) -> PlacementZone:
    return PlacementZone(
        zone_type=d["zone_type"],
        center=d["center"],
        normal=d["normal"],
        area=d["area"],
        bounds=d["bounds"],
        stability_score=d["stability_score"],
    )


def _result_to_dict(r: PlacementZoneResult) -> dict:
    return {"asset_id": r.asset_id, "zones": [_zone_to_dict(z) for z in r.zones]}


def _dict_to_result(d: dict) -> PlacementZoneResult:
    return PlacementZoneResult(
        asset_id=d["asset_id"],
        zones=[_dict_to_zone(z) for z in d.get("zones", [])],
    )


# ---------------------------------------------------------------------------
# Core geometry helpers
# ---------------------------------------------------------------------------

_Y_AXIS = np.array([0.0, 1.0, 0.0])
_MIN_AREA = 0.01          # discard faces smaller than this (units²)
_CLUSTER_ANGLE_DEG = 30.0  # max angular difference for normal clustering
_CLUSTER_DIST = None       # spatial distance threshold set per-mesh (see below)


def _face_normal_and_area(v0, v1, v2) -> tuple[np.ndarray, float]:
    """Return (unit_normal, area) for triangle (v0,v1,v2)."""
    e1 = v1 - v0
    e2 = v2 - v0
    cross = np.cross(e1, e2)
    area = 0.5 * np.linalg.norm(cross)
    if area < 1e-12:
        return np.array([0.0, 1.0, 0.0]), 0.0
    normal = cross / (2.0 * area)  # cross / |cross|
    return normal, area


def _angle_between(n1: np.ndarray, n2: np.ndarray) -> float:
    """Angle in degrees between two unit vectors."""
    cos_a = float(np.clip(np.dot(n1, n2), -1.0, 1.0))
    return math.degrees(math.acos(cos_a))


def _angle_with_y(normal: np.ndarray) -> float:
    """Angle in degrees between normal and +Y axis."""
    return _angle_between(normal, _Y_AXIS)


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

class _FaceGroup:
    """Accumulated cluster of co-planar / co-normal triangles."""

    def __init__(self, normal: np.ndarray, center: np.ndarray, area: float,
                 verts: list[np.ndarray]):
        self.normal = normal
        self.weighted_center = center * area
        self.total_area = area
        self.all_verts: list[np.ndarray] = list(verts)

    def add(self, normal: np.ndarray, center: np.ndarray, area: float,
            verts: list[np.ndarray]):
        # Running weighted average of normal
        self.normal = (self.normal * self.total_area + normal * area)
        self.total_area += area
        length = np.linalg.norm(self.normal)
        if length > 1e-12:
            self.normal = self.normal / length
        self.weighted_center += center * area
        self.all_verts.extend(verts)

    @property
    def center(self) -> np.ndarray:
        if self.total_area < 1e-12:
            return self.weighted_center
        return self.weighted_center / self.total_area

    @property
    def unit_normal(self) -> np.ndarray:
        n = self.normal
        length = np.linalg.norm(n)
        if length < 1e-12:
            return _Y_AXIS.copy()
        return n / length

    def bounds(self) -> list[list[float]]:
        if not self.all_verts:
            c = self.center
            return [c.tolist()]
        pts = np.array(self.all_verts)
        mn = pts.min(axis=0)
        mx = pts.max(axis=0)
        # 8 corners of the AABB
        corners = []
        for xi in (mn[0], mx[0]):
            for yi in (mn[1], mx[1]):
                for zi in (mn[2], mx[2]):
                    corners.append([xi, yi, zi])
        return corners


def _cluster_faces(
    normals: list[np.ndarray],
    centers: list[np.ndarray],
    areas: list[float],
    face_verts: list[list[np.ndarray]],
    angle_thresh_deg: float,
    dist_thresh: float,
) -> list[_FaceGroup]:
    """Greedy clustering: merge a face into an existing group if its normal
    is within *angle_thresh_deg* of the group's normal AND its center is
    within *dist_thresh* of the group's center."""
    groups: list[_FaceGroup] = []
    for n, c, a, fv in zip(normals, centers, areas, face_verts):
        merged = False
        for g in groups:
            ang = _angle_between(n, g.unit_normal)
            # Accept both same-direction and opposite faces as the same cluster
            # only if same-direction (we do NOT merge flipped normals):
            if ang <= angle_thresh_deg:
                dist = float(np.linalg.norm(c - g.center))
                if dist <= dist_thresh:
                    g.add(n, c, a, fv)
                    merged = True
                    break
        if not merged:
            groups.append(_FaceGroup(n.copy(), c.copy(), a, fv))
    return groups


# ---------------------------------------------------------------------------
# Zone classification
# ---------------------------------------------------------------------------

def _classify_group(
    group: _FaceGroup,
    min_area: float,
    max_area: float,
    all_groups: list[_FaceGroup],
) -> Optional[PlacementZone]:
    """Turn a face cluster into a PlacementZone (or None if filtered out)."""
    area = group.total_area
    if area < min_area:
        return None

    normal = group.unit_normal
    center = group.center
    angle_y = _angle_with_y(normal)

    # --- cavity detection (simple heuristic) ---
    # A group is a cavity if its center is "inside" the bounding volume formed
    # by the other groups' vertices.  We use a cheap proxy: count how many
    # other-group centres are within a small radius and surround this one from
    # multiple sides (dot products span both positive and negative).
    is_cavity = _detect_cavity(group, all_groups)

    if is_cavity:
        zone_type = "cavity"
    elif angle_y <= 45.0:
        zone_type = "stable_top"
    elif area >= min_area:
        zone_type = "stable_side"
    else:
        zone_type = "attach_point"

    # Attach-point override: small areas with outward normal
    if area < min_area * 10 and not is_cavity and angle_y > 45.0:
        zone_type = "attach_point"

    # --- stability score ---
    if zone_type == "stable_top":
        score = float(np.dot(normal, _Y_AXIS))          # cos(angle with Y)
        score = max(0.0, min(1.0, score))
    elif zone_type == "stable_side":
        sin_a = math.sin(math.radians(angle_y))
        score = sin_a * (area / max_area) if max_area > 0 else 0.0
        score = max(0.0, min(1.0, score))
    elif zone_type == "attach_point":
        score = 0.5
    else:  # cavity
        score = (area / max_area) if max_area > 0 else 0.0
        score = max(0.0, min(1.0, score))

    return PlacementZone(
        zone_type=zone_type,
        center=center.tolist(),
        normal=normal.tolist(),
        area=float(area),
        bounds=group.bounds(),
        stability_score=float(score),
    )


def _detect_cavity(group: _FaceGroup, all_groups: list[_FaceGroup]) -> bool:
    """Heuristic: a group is a cavity if neighbouring group normals point
    inward toward it from at least 3 different directions (dot < 0)."""
    if len(all_groups) < 4:
        return False
    center = group.center
    inward_dirs = 0
    for other in all_groups:
        if other is group:
            continue
        to_group = center - other.center
        dist = np.linalg.norm(to_group)
        if dist < 1e-9:
            continue
        # If the other group's normal points toward this group's center
        if np.dot(other.unit_normal, to_group / dist) > 0.5:
            inward_dirs += 1
    return inward_dirs >= 3


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class PlacementZoneService:
    """Analyse a triangle mesh and return placement zones.

    Parameters
    ----------
    asset_store:
        Optional dict mapping asset_id -> computed_features dict.
        Used for cache read/write.  If None, caching is disabled.
    min_area:
        Minimum face-cluster area to emit a zone (default 0.01).
    """

    def __init__(
        self,
        asset_store: Optional[dict] = None,
        min_area: float = _MIN_AREA,
    ):
        self._store = asset_store if asset_store is not None else {}
        self._min_area = min_area

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, asset_id: str, mesh_data: dict) -> PlacementZoneResult:
        """Return placement zones for *asset_id*, using cache when available."""
        # 1. Cache lookup
        features = self._store.get(asset_id, {})
        cached = features.get("placement_zones")
        if cached is not None:
            return _dict_to_result(cached)

        # 2. Compute
        zones = self._compute_zones(mesh_data)
        result = PlacementZoneResult(asset_id=asset_id, zones=zones)

        # 3. Cache write
        features = dict(features)
        features["placement_zones"] = _result_to_dict(result)
        self._store[asset_id] = features

        return result

    # ------------------------------------------------------------------
    # Internal computation (overridable for testing)
    # ------------------------------------------------------------------

    def _compute_zones(self, mesh_data: dict) -> list[PlacementZone]:
        vertices_raw = mesh_data.get("vertices", [])
        faces_raw = mesh_data.get("faces", [])

        if not vertices_raw or not faces_raw:
            return []

        verts = np.array(vertices_raw, dtype=float)

        # Per-face normals, areas, centres, vertex lists
        normals: list[np.ndarray] = []
        areas: list[float] = []
        centers: list[np.ndarray] = []
        face_verts_list: list[list[np.ndarray]] = []

        for tri in faces_raw:
            i0, i1, i2 = int(tri[0]), int(tri[1]), int(tri[2])
            v0, v1, v2 = verts[i0], verts[i1], verts[i2]
            n, a = _face_normal_and_area(v0, v1, v2)
            if a < 1e-12:
                continue
            c = (v0 + v1 + v2) / 3.0
            normals.append(n)
            areas.append(a)
            centers.append(c)
            face_verts_list.append([v0.copy(), v1.copy(), v2.copy()])

        if not normals:
            return []

        # Spatial distance threshold: 10 % of mesh diagonal
        all_pts = np.vstack(face_verts_list)
        diag = float(np.linalg.norm(all_pts.max(axis=0) - all_pts.min(axis=0)))
        dist_thresh = max(diag * 0.10, 0.01)

        # Cluster
        groups = _cluster_faces(
            normals, centers, areas, face_verts_list,
            angle_thresh_deg=_CLUSTER_ANGLE_DEG,
            dist_thresh=dist_thresh,
        )

        max_area = max((g.total_area for g in groups), default=1.0)

        zones = []
        for g in groups:
            z = _classify_group(g, self._min_area, max_area, groups)
            if z is not None:
                zones.append(z)

        return zones
