# xasset/pipeline/stages/mesh_utils.py
"""Ear-cut triangulation utilities, extracted from ref/LayoutDecoration/mesh/recon_mesh.py."""
import math


def check_poly_clock(poly: list[list[float]]) -> bool:
    """Return True if polygon is clockwise (XZ plane), False if CCW."""
    n = len(poly)
    area = 0.0
    for i in range(n):
        x0, z0 = poly[i][0], poly[i][1]
        x1, z1 = poly[(i + 1) % n][0], poly[(i + 1) % n][1]
        area += x0 * z1 - x1 * z0
    return area < 0  # negative = CW in standard math coords


def _in_triangle(p, a, b, c) -> bool:
    """Test if point p is inside triangle abc (2D)."""
    def cross(o, u, v):
        return (u[0] - o[0]) * (v[1] - o[1]) - (u[1] - o[1]) * (v[0] - o[0])
    d1 = cross(p, a, b)
    d2 = cross(p, b, c)
    d3 = cross(p, c, a)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


def _is_ear(poly: list[list[float]], i: int) -> bool:
    """Return True if vertex i is an ear of the polygon."""
    n = len(poly)
    a = poly[(i - 1) % n]
    b = poly[i]
    c = poly[(i + 1) % n]
    cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if cross <= 0:
        return False
    for j in range(n):
        if j in {(i - 1) % n, i, (i + 1) % n}:
            continue
        if _in_triangle(poly[j], a, b, c):
            return False
    return True


def ear_cut_triangulation(poly: list[list[float]]) -> list[list[int]]:
    """
    Ear-cut triangulate a simple polygon (2D, XZ).
    Polygon must be CCW. Returns list of [i, j, k] index triples into original poly.
    """
    if check_poly_clock(poly):
        poly = poly[::-1]

    tris = []
    remaining = list(range(len(poly)))

    while len(remaining) > 3:
        found = False
        for idx in range(len(remaining)):
            local_poly = [poly[j] for j in remaining]
            if _is_ear(local_poly, idx):
                prev_i = remaining[(idx - 1) % len(remaining)]
                curr_i = remaining[idx]
                next_i = remaining[(idx + 1) % len(remaining)]
                tris.append([prev_i, curr_i, next_i])
                remaining.pop(idx)
                found = True
                break
        if not found:
            break

    if len(remaining) == 3:
        tris.append(remaining[:])
    return tris


def build_polygon_mesh(
    poly_3d: list[list[float]],
    normal: list[float],
) -> tuple[list[list[float]], list[list[int]]]:
    """
    Triangulate a 3D coplanar polygon (ear-cut on XZ or XY projection).
    Returns (vertices, faces) where faces are indices into vertices.
    normal determines which projection axis to drop for 2D ear-cut.
    """
    ax = max(range(3), key=lambda i: abs(normal[i]))
    if ax == 1:  # Y-up normal → project to XZ
        poly_2d = [[v[0], v[2]] for v in poly_3d]
    elif ax == 0:  # X normal → project to YZ
        poly_2d = [[v[1], v[2]] for v in poly_3d]
    else:  # Z normal → project to XY
        poly_2d = [[v[0], v[1]] for v in poly_3d]

    faces = ear_cut_triangulation(poly_2d)
    return poly_3d, faces
