# xasset/pipeline/stages/uv_utils.py
"""UV mapping utilities. UV in world units (meters); tiling deferred to StylizeStage."""


def compute_wall_uv(
    verts: list[list[float]],
    u_axis: list[float],
    v_axis: list[float],
) -> list[list[float]]:
    """
    Project vertices onto (u_axis, v_axis) to get world-space UV.
    u_axis and v_axis should be unit vectors.
    """
    uvs = []
    for v in verts:
        u = v[0] * u_axis[0] + v[1] * u_axis[1] + v[2] * u_axis[2]
        vv = v[0] * v_axis[0] + v[1] * v_axis[1] + v[2] * v_axis[2]
        uvs.append([u, vv])
    return uvs


def map_uv_planar(
    verts: list[list[float]],
    normal: list[float],
) -> list[list[float]]:
    """
    Planar UV projection based on dominant normal axis.
    For floor/ceiling (normal≈Y): U=X, V=Z
    For wall facing X: U=Z, V=Y
    For wall facing Z: U=X, V=Y
    """
    ax = max(range(3), key=lambda i: abs(normal[i]))
    if ax == 1:  # floor / ceiling
        return compute_wall_uv(verts, u_axis=[1, 0, 0], v_axis=[0, 0, 1])
    elif ax == 0:  # wall facing X
        return compute_wall_uv(verts, u_axis=[0, 0, 1], v_axis=[0, 1, 0])
    else:  # wall facing Z
        return compute_wall_uv(verts, u_axis=[1, 0, 0], v_axis=[0, 1, 0])
