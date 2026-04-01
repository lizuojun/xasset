import copy
import math
import numpy as np


#
# def check_pt_in_line(pt, line):
#     line_x = sorted([line[0][0], line[1][0]])
#     line_y = sorted([line[0][1], line[1][1]])
#     x_length = abs(line_x[0] - line_x[1])
#     y_length = abs(line_y[0] - line_y[1])
#     if y_length > x_length:
#         if line_y[0] - 0.01 < pt[1] < line_y[1] + 0.01 and line_x[0] - 0.2 < pt[0] < line_x[1] + 0.2:
#             return True
#     else:
#         if line_x[0] - 0.01 < pt[0] < line_x[1] + 0.01 and line_y[0] - 0.2 < pt[1] < line_y[1] + 0.2:
#             return True
#     return False


def check_pt_in_line(pt, line):

    if np.linalg.norm(np.array(pt) - np.array(line[0])) > np.linalg.norm(np.array(pt) - np.array(line[1])):
        org = np.array(line[0])
        end = np.array(line[1])
    else:
        org = np.array(line[1])
        end = np.array(line[0])
    line_vec = end - org
    pt_vec = np.array(pt) - org

    if np.linalg.norm(np.array(pt) - end) < 1e-3:
        pt = (line_vec * (1. - 1e-3 / np.linalg.norm(line_vec)) + org).tolist()
        return True, pt
    elif np.linalg.norm(line_vec) < 1e-3:
        return False, pt
    if np.cross(line_vec, pt_vec) / np.linalg.norm(line_vec) < 1e-1 and \
            np.linalg.norm(pt_vec) < np.linalg.norm(line_vec) + 1e-3:
        if np.linalg.norm(pt_vec) >= np.linalg.norm(line_vec):
            pt = (line_vec * (1. - 1e-3 / np.linalg.norm(line_vec)) + org).tolist()
        return True, pt
    else:
        return False, pt


def get_pt_distance(pt_a, pt_b):
    return np.sum((np.array(pt_a) - np.array(pt_b)) ** 2) ** 0.5


def find_pt_in_line_backup(pts, line):
    pts = np.array(pts).reshape(-1, 2)
    # 垂直线
    if abs(line[0][0] - line[1][0]) < abs(line[0][1] - line[1][1]):
        # if abs(line[0][0] - line[1][0]) > 0.01:
        #     return []
        l = max(abs(pts[0][1] - pts[1][1]), abs(pts[1][1] - pts[2][1]))
        w = min(abs(pts[0][0] - pts[1][0]), abs(pts[1][0] - pts[2][0]))
        if l < w:
            return []
        mid_p = 0.25 * (pts[0][1] + pts[1][1] + pts[2][1] + pts[3][1])
        mid_p_base = 0.25 * (pts[0][0] + pts[1][0] + pts[2][0] + pts[3][0])
        line_base = line[0][0]
        half_l = 0.5 * l

        max_p = max(line[0][1], line[1][1])
        min_p = min(line[0][1], line[1][1])
        if (mid_p - half_l) < min_p - 1e-2 or (mid_p + half_l) > max_p + 1e-2:
            return []
        if (mid_p - half_l) < min_p:
            start_y = min_p + 1e-3
        else:
            start_y = mid_p - half_l
        if (mid_p + half_l) > max_p:
            end_y = max_p - 1e-3
        else:
            end_y = mid_p + half_l
        out_p = [[line[0][0], start_y], [line[0][0], end_y]]
        if (line[0][1] - line[1][1]) > 0:
            out_p = [out_p[1], out_p[0]]
    else:
        # if abs(line[0][1] - line[1][1]) > 0.01:
        #     return []
        l = max(abs(pts[0][0] - pts[1][0]), abs(pts[1][0] - pts[2][0]))
        w = max(abs(pts[0][1] - pts[1][1]), abs(pts[1][1] - pts[2][1]))
        if l < w:
            return []
        mid_p = 0.25 * (pts[0][0] + pts[1][0] + pts[2][0] + pts[3][0])
        mid_p_base = 0.25 * (pts[0][1] + pts[1][1] + pts[2][1] + pts[3][1])
        line_base = line[1][1]
        half_l = l / 2.
        max_p = max(line[0][0], line[1][0])
        min_p = min(line[0][0], line[1][0])
        if (mid_p - half_l) < min_p - 1e-2 or (mid_p + half_l) > max_p + 1e-2:
            return []
        if (mid_p - half_l) < min_p:
            start_x = min_p + 1e-3
        else:
            start_x = mid_p - half_l
        if (mid_p + half_l) > max_p:
            end_x = max_p - 1e-3
        else:
            end_x = mid_p + half_l
        out_p = [[start_x, line[1][1]], [end_x, line[1][1]]]

        if (line[0][0] - line[1][0]) > 0:
            out_p = [out_p[1], out_p[0]]
    if abs(mid_p_base - line_base) > 0.2 + w:
        return []

    return out_p


def find_pt_in_line(pts, line):
    pts = np.array(pts).reshape(-1, 2)
    width = np.linalg.norm(pts[0, :] - pts[1, :])
    length = np.linalg.norm(pts[1, :] - pts[2, :])
    if width > length:
        length = width
        width = np.linalg.norm(pts[1, :] - pts[2, :])
        parallel_pts = [[pts[0, :], pts[1, :]], [pts[2, :], pts[3, :]]]
        # vertical_pts = [[pts[1, :], pts[2, :]], [pts[0, :], pts[3, :]]]
    else:
        # vertical_pts = [[pts[0, :], pts[1, :]], [pts[2, :], pts[3, :]]]
        parallel_pts = [[pts[1, :], pts[2, :]], [pts[0, :], pts[3, :]]]

    line_vec = np.array(line[0]) - np.array(line[1])
    if np.linalg.norm(line_vec) < 1e-5:
        return []
    window_dir_vec = parallel_pts[0][0] - parallel_pts[0][1]
    # not parallel
    if abs(np.cross(line_vec, window_dir_vec)) / np.linalg.norm(line_vec) / np.linalg.norm(window_dir_vec) > np.sin(
            np.pi / 4):
        return []

    # in width range
    min_dis = 1e8
    for i in range(4):
        pt = pts[i, :]
        line_pt = line[0] if np.linalg.norm(np.array(line[0]) - pt) > np.linalg.norm(np.array(line[1]) - pt) else line[
            1]
        dis = abs(np.cross(pt - np.array(line_pt), np.array(line[0]) - np.array(line[1])) / np.linalg.norm(
            np.array(line[0]) - np.array(line[1])))
        if dis < min_dis:
            min_dis = dis
    if min_dis > width:
        return []

    parallel_pt = parallel_pts[0]
    beyond_line_length = 0.
    if np.linalg.norm(parallel_pt[0] - np.array(line[0])) > np.linalg.norm(parallel_pt[0] - np.array(line[1])):
        win_pt_vec = parallel_pt[0] - np.array(line[0])
        line_vec = np.array(line[1]) - np.array(line[0])
        project_length = np.dot(win_pt_vec, line_vec) / np.linalg.norm(line_vec)
        beyond_line_length += max(0., project_length - np.linalg.norm(line_vec))
        if project_length >= np.linalg.norm(line_vec) - 1e-3:
            project_length = np.linalg.norm(line_vec) - 1e-3
        project_pt1 = line_vec / np.linalg.norm(line_vec) * project_length + np.array(line[0])
    else:
        win_pt_vec = parallel_pt[0] - np.array(line[1])
        line_vec = np.array(line[0]) - np.array(line[1])
        project_length = np.dot(win_pt_vec, line_vec) / np.linalg.norm(line_vec)
        beyond_line_length += max(0., project_length - np.linalg.norm(line_vec))
        if project_length > np.linalg.norm(line_vec) - 1e-3:
            project_length = np.linalg.norm(line_vec) - 1e-3
        project_pt1 = line_vec / np.linalg.norm(line_vec) * project_length + np.array(line[1])

    if np.linalg.norm(parallel_pt[1] - np.array(line[0])) > np.linalg.norm(parallel_pt[1] - np.array(line[1])):
        win_pt_vec = parallel_pt[1] - np.array(line[0])
        line_vec = np.array(line[1]) - np.array(line[0])
        project_length = np.dot(win_pt_vec, line_vec) / np.linalg.norm(line_vec)
        beyond_line_length += max(0., project_length - np.linalg.norm(line_vec))
        if project_length > np.linalg.norm(line_vec) - 1e-3:
            project_length = np.linalg.norm(line_vec) - 1e-3
        project_pt2 = line_vec / np.linalg.norm(line_vec) * project_length + np.array(line[0])
    else:
        win_pt_vec = parallel_pt[1] - np.array(line[1])
        line_vec = np.array(line[0]) - np.array(line[1])
        project_length = np.dot(win_pt_vec, line_vec) / np.linalg.norm(line_vec)
        beyond_line_length += max(0., project_length - np.linalg.norm(line_vec))
        if project_length > np.linalg.norm(line_vec):
            project_length = np.linalg.norm(line_vec) - 1e-3
        project_pt2 = line_vec / np.linalg.norm(line_vec) * project_length + np.array(line[1])
    if beyond_line_length > length / 2.:
        return []

    if np.linalg.norm(project_pt1 - np.array(line[0])) > np.linalg.norm(project_pt2 - np.array(line[0])):
        return [project_pt2.tolist(), project_pt1.tolist()]
    else:
        return [project_pt1.tolist(), project_pt2.tolist()]


# 2维 判断
def pt_in_line(pt, line):
    if abs(line[0][0] - line[1][0]) < 0.01:
        if abs(line[0][0] - pt[0]) < 0.01 and min(line[0][1], line[1][1]) <= pt[1] <= max(line[0][1], line[1][1]):
            return True
    elif abs(line[0][1] - line[1][1]) < 0.01:
        if abs(line[0][1] - pt[1]) < 0.01 and min(line[0][0], line[1][0]) <= pt[0] <= max(line[0][0], line[1][0]):
            return True
    else:
        r_p_x = (pt[0] - line[0][0]) / (line[1][0] - line[0][0])
        r_p_y = (pt[1] - line[0][1]) / (line[1][1] - line[0][1])
        r_q_x = (pt[0] - line[0][0]) / (line[1][0] - line[0][0])
        r_q_y = (pt[1] - line[0][1]) / (line[1][1] - line[0][1])
        if abs(r_p_x - r_p_y) > 0.01 or abs(r_q_x - r_q_y) > 0.01:
            return True
    return False


def in_poly(p, a, b, c):
    pa = [p[0] - a[0], p[1] - a[1], p[2] - a[2]]
    pb = [p[0] - b[0], p[1] - b[1], p[2] - b[2]]
    pc = [p[0] - c[0], p[1] - c[1], p[2] - c[2]]

    t1 = np.cross(pa, pb)
    t2 = np.cross(pb, pc)
    t3 = np.cross(pc, pa)

    a1 = np.sum(t1 * t2)
    a2 = np.sum(t3 * t2)

    is_in = (a1 >= 0 and a2 >= 0) or (a1 <= 0 and a2 <= 0)
    return is_in


def poly_triangulation(floor_pts, normal):
    return []


def ear_cut_triangulation(floor_pts, normal, axis=1, r=1.):
    # 耳切法三角化
    # 1 先计算每个点的凹凸性
    convex_p_idx = []
    num_p = len(floor_pts)
    for p in range(num_p):
        one = np.array(floor_pts[p]) - np.array(floor_pts[(p - 1) % num_p])
        two = np.array(floor_pts[(p + 1) % num_p]) - np.array(floor_pts[p])
        crossRes = np.cross(one, two)
        if crossRes[axis] * r >= 0:
            convex_p_idx.append(p)

    for p in convex_p_idx:
        tri_now = floor_pts[p]
        tri_prev = floor_pts[(p - 1) % num_p]
        tri_next = floor_pts[(p + 1) % num_p]
        all_p = [(p - 1) % num_p, (p + 1) % num_p, p]
        no_need = False
        for i in range(num_p):
            if i in all_p:
                continue
            else:
                if in_poly(floor_pts[i], tri_prev, tri_now, tri_next, axis):
                    no_need = True
                    break
        if no_need:
            continue
        else:
            return p, [tri_prev, tri_now, tri_next]
    print("wrong!", convex_p_idx, floor_pts)


def map_uv(input_pts, u_dir, face_normal, target_normal=[0., 1., 0.]):
    target_p0 = np.zeros(shape=[3])
    target_p1 = np.array(target_normal).reshape([3])
    target_p2 = np.array([1., 0, 0]).reshape([3])
    target_p3 = np.cross(target_p1, target_p2)

    face_p0 = np.zeros(shape=[3])
    face_p2 = np.array(u_dir) / np.linalg.norm(np.array(u_dir))
    face_p1 = np.array(face_normal).reshape([3])
    face_p3 = np.cross(face_p1, face_p2)
    face_center = (face_p0 + face_p1 + face_p2 + face_p3) / 3.
    target_center = (target_p0 + target_p1 + target_p2 + target_p3) / 3.
    w = np.dot((target_p0 - target_center).reshape([3, 1]), (face_p0 - face_center).reshape([1, 3]))
    w += np.dot((target_p1 - target_center).reshape([3, 1]), (face_p1 - face_center).reshape([1, 3]))
    w += np.dot((target_p2 - target_center).reshape([3, 1]), (face_p2 - face_center).reshape([1, 3]))
    w += np.dot((target_p3 - target_center).reshape([3, 1]), (face_p3 - face_center).reshape([1, 3]))
    u, s, vh, = np.linalg.svd(w)
    r = np.dot(u, vh)
    final_pts = np.dot(input_pts, r.T)
    return final_pts, r


def map_uv_from_3d(pts, normal, u_dir):
    map_pts, _ = map_uv(pts, u_dir, normal)
    pts_plane = np.delete(map_pts, 1, axis=1)
    # if norm_pts is None:
    #     base_pts = np.min(pts_plane, axis=0)
    # else:
    #     base_pts = norm_pts
    # pts_plane = pts_plane - base_pts
    # if center_align:
    #     size = np.max(pts_plane, axis=0) - np.min(pts_plane, axis=0)
    #     u = -(pts_plane[:, 0] * uv_ratio[0] + uv_ratio[1] + 0.5 * (1 - size[0] * uv_ratio[0]))
    #     v = pts_plane[:, 1] * uv_ratio[2] + uv_ratio[3] + 0.5 * (1 - size[1] * uv_ratio[2])
    # else:
    # u = -(pts_plane[:, 0] * uv_ratio[0] + uv_ratio[1] + 0.5)
    # v = pts_plane[:, 1] * uv_ratio[2] + uv_ratio[3] + 0.5
    u = -pts_plane[:, 0]
    v = pts_plane[:, 1]

    out_uv = []
    for i in range(len(pts_plane)):
        out_uv.append(u[i])
        out_uv.append(v[i])
    return out_uv


# 计算多边形每个点的凹凸性, 最低点为凸顶点
def convex_p_find(floor_pts, axis=1, r=1., yz_flip=False):
    if len(floor_pts) == 0:
        return []
    # 耳切法三角化
    # 1 先计算每个点的凹凸性
    if len(floor_pts[0]) == 2:
        if yz_flip:
            temp_p = [[i[0], i[1], 0.] for i in floor_pts]
        else:
            temp_p = [[i[0], 0., i[1]] for i in floor_pts]
    else:
        temp_p = copy.deepcopy(floor_pts)
    convex_p_idx = []
    num_p = len(temp_p)
    for p in range(num_p):
        one = np.array(temp_p[p]) - np.array(temp_p[(p - 1) % num_p])
        two = np.array(temp_p[(p + 1) % num_p]) - np.array(temp_p[p])
        crossRes = np.cross(one, two)
        if crossRes[axis] * r >= 0:
            convex_p_idx.append(0)
        else:
            convex_p_idx.append(1)
    return convex_p_idx


# 计算多边形每条边(next - p)朝向多边形内部的法向量, 给出当前点与前后点, 以及当前的凹凸性
def compute_line_face_normal(p, next, prev, convex_flag):
    n = 1.
    if not convex_flag:
        n = -1.
    p = np.array(p)
    prev = np.array(prev)
    next = np.array(next)
    # start_p = 0.5 * (p + prev)
    # mid_p = 0.5 * (prev + next)
    normal_dir = n * (p - prev)

    line_normal = next - p
    line_normal = [-line_normal[1], line_normal[0]]

    norm = np.sqrt(line_normal[0] * line_normal[0] + line_normal[1] * line_normal[1]) + 0.0001
    if normal_dir[0] * line_normal[0] + normal_dir[1] * line_normal[1] > 0:
        line_normal = [-line_normal[0], -line_normal[1]]
    line_normal = [line_normal[0] / norm, line_normal[1] / norm]
    return line_normal


# 计算转角处(p1)的墙偏移值 暂时不用
def compute_corner_offset_vec(p0, p1, p2, width=0.24):
    # v0 = [p1[0] - p0[0], p1[1] - p0[1]]
    # v0_norm = np.sqrt(v0[0] ** 2 + v0[1] ** 2) + 1e-20
    # # 顺时针 右侧
    # v1_n = [v0[1] / v0_norm, -v0[0] / v0_norm]
    v1 = [p0[0] - p1[0], p0[1] - p1[1]]
    v1_norm = np.sqrt(v1[0] ** 2 + v1[1] ** 2) + 1e-20
    v2 = [p2[0] - p1[0], p2[1] - p1[1]]
    v2_norm = np.sqrt(v2[0] ** 2 + v2[1] ** 2) + 1e-20
    cos_theta = (v1[0] * v2[0] + v1[1] * v2[1]) / (v1_norm * v2_norm)
    # for num_wall=2
    cos_half_theta = np.sqrt((1 + cos_theta) / 2.)
    sin_half_theta = np.sqrt((1 - cos_theta) / 2.)
    v1 = [v1[0] / v1_norm, v1[1] / v1_norm]
    cos_x = v1[0]
    sin_x = v1[1]
    final_x = cos_x * cos_half_theta - sin_x * sin_half_theta
    final_y = sin_x * cos_half_theta + cos_x * sin_half_theta
    assert abs(cos_half_theta) > 1e-10
    norm = width / cos_half_theta
    return [final_x * norm, final_y * norm]


def check_if_anti(pts):
    convex_p_idx = np.argmax(np.array(pts), axis=0)[0]
    convex_prev_idx = (convex_p_idx - 1) % len(pts)
    convex_next_idx = (convex_p_idx + 1) % len(pts)
    x1 = pts[convex_prev_idx][0]
    y1 = pts[convex_prev_idx][1]
    x2 = pts[convex_p_idx][0]
    y2 = pts[convex_p_idx][1]
    x3 = pts[convex_next_idx][0]
    y3 = pts[convex_next_idx][1]
    if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) < 0:
        return True
    else:
        return False


def check_anti(room_info):
    out_pts = []
    floor_pts = room_info['floor']
    for i in range(len(floor_pts) // 2 - 1):
        out_pts.append([floor_pts[2 * i], floor_pts[2 * i + 1]])
    convex_p_idx = np.argmax(np.array(out_pts), axis=0)[0]
    convex_prev_idx = (convex_p_idx - 1) % len(out_pts)
    convex_next_idx = (convex_p_idx + 1) % len(out_pts)
    x1 = out_pts[convex_prev_idx][0]
    y1 = out_pts[convex_prev_idx][1]
    x2 = out_pts[convex_p_idx][0]
    y2 = out_pts[convex_p_idx][1]
    x3 = out_pts[convex_next_idx][0]
    y3 = out_pts[convex_next_idx][1]
    if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) < 0:
        return room_info
    else:
        new_out_pts = []
        out_pts.reverse()
        for i in out_pts:
            new_out_pts.append(i[0])
            new_out_pts.append(i[1])
        new_out_pts.append(new_out_pts[0])
        new_out_pts.append(new_out_pts[1])
        room_info['floor'] = new_out_pts
        return room_info


def compute_dis(input_p, p_list):
    if len(p_list) == 0:
        return 100
    for p in p_list:
        dis = (input_p[0] - p[0]) ** 2 + (input_p[1] - p[1]) ** 2
        if dis < 0.01:
            return 0.
        else:
            continue
    return 100.


def get_refine_pts(origin_floor):
    refined_pts = []
    out_floor = []

    for i in range(0, len(origin_floor) // 2, 1):
        ori_x = origin_floor[2 * i]
        ori_y = origin_floor[2 * i + 1]
        if compute_dis([ori_x, ori_y], refined_pts) < 0.01:
            continue
        else:
            if len(out_floor) > 0:
                if abs(ori_x - out_floor[0]) < abs(ori_y - out_floor[1]):
                    if abs(ori_x - out_floor[0]) < 3.2:
                        ori_x = out_floor[0]
                else:
                    if abs(ori_y - out_floor[1]) < 3.2:
                        ori_y = out_floor[1]
            refined_pts.append([ori_x, ori_y])
            out_floor.insert(0, ori_x)
            out_floor.insert(1, ori_y)
    ori_x = out_floor[-2]
    ori_y = out_floor[-1]
    need_flag = False
    if abs(ori_x - out_floor[0]) < abs(ori_y - out_floor[1]):
        if 0.01 < abs(ori_x - out_floor[0]) < 0.2:
            ori_x = out_floor[0]
            need_flag = True
    else:
        if 0.01 < abs(ori_y - out_floor[1]) < 0.2:
            ori_y = out_floor[1]
            need_flag = True
    if need_flag:
        out_floor.append(ori_x)
        out_floor.append(ori_y)
    out_floor.append(out_floor[0])
    out_floor.append(out_floor[1])
    refined_out_floor_pts = [out_floor[0], out_floor[1]]

    for i in range(1, len(out_floor) // 2 - 1):
        now_pt = out_floor[2 * i:2 * i + 2]
        next_pt = out_floor[2 * i + 2:2 * i + 4]
        prev_base_idx = (2 * i - 2) % len(out_floor)
        prev_pt = out_floor[prev_base_idx:prev_base_idx + 2]
        if abs(now_pt[0] - next_pt[0]) < 0.01 and abs(now_pt[0] - prev_pt[0]) < 0.01:
            continue
        if abs(now_pt[1] - next_pt[1]) < 0.01 and abs(now_pt[1] - prev_pt[1]) < 0.01:
            continue
        refined_out_floor_pts += now_pt

    now_pt = refined_out_floor_pts[0:2]
    next_pt = refined_out_floor_pts[2:4]
    prev_pt = refined_out_floor_pts[-2:]

    if abs(now_pt[0] - next_pt[0]) < 0.01 and abs(now_pt[0] - prev_pt[0]) < 0.01:
        refined_out_floor_pts[:2] = []
    elif abs(now_pt[1] - next_pt[1]) < 0.01 and abs(now_pt[1] - prev_pt[1]) < 0.01:
        refined_out_floor_pts[:2] = []

    refined_out_floor_pts += [refined_out_floor_pts[0], refined_out_floor_pts[1]]
    out_final = []
    for i in range(len(refined_out_floor_pts) // 2 - 1, -1, -1):
        out_final.append(refined_out_floor_pts[2 * i + 0])
        out_final.append(refined_out_floor_pts[2 * i + 1])
    return out_final


def find_one_inner_pt(floor_pts, start_idx):
    num_p = len(floor_pts)
    for p in range(num_p):
        if p == start_idx or p == start_idx + 1:
            continue
        a_pt = np.array([floor_pts[start_idx][0], 0.0, floor_pts[start_idx][1]])
        b_pt = np.array([floor_pts[start_idx + 1][0], 0.0, floor_pts[start_idx + 1][1]])
        now = np.array([floor_pts[p][0], 0.0, floor_pts[p][1]])
        one = now - a_pt
        two = now - b_pt
        crossRes = np.cross(one, two)
        if crossRes[1] > 0:
            return floor_pts[p]
    print("find_one_inner_pt_wrong!", start_idx, floor_pts[start_idx])
    # 12 [-6.694, 3.17]


def rot_to_ang(rot):
    rot_1 = rot[1]
    rot_3 = rot[3]
    if rot_1 > 1:
        rot_1 = 1
    elif rot_1 < -1:
        rot_1 = -1
    if rot_3 > 1:
        rot_3 = 1
    elif rot_3 < -1:
        rot_3 = -1
    # 计算
    ang = 0
    if abs(rot_1 - 1) < 0.0001 or abs(rot_1 + 1) < 0.0001:
        ang = math.pi
    elif abs(rot_3 - 1) < 0.0001 or abs(rot_3 + 1) < 0.0001:
        ang = 0
    else:
        if rot_1 >= 0 and rot_3 >= 0:
            ang = math.asin(rot_1) * 2
        elif rot_1 <= 0 and rot_3 >= 0:
            ang = math.asin(rot_1) * 2
        elif rot_1 >= 0 and rot_3 <= 0:
            ang = math.acos(rot_3) * 2
        elif rot_1 <= 0 and rot_3 <= 0:
            ang = -math.acos(rot_3) * 2
    # 规范
    if ang > math.pi * 2:
        ang -= math.pi * 2
    elif ang < -math.pi * 2:
        ang += math.pi * 2
    # 规范
    if ang > math.pi:
        ang -= math.pi * 2
    elif ang < -math.pi:
        ang += math.pi * 2
    # 返回
    return ang


def compute_furniture_rect(size, position, rotation, adjust=[0, 0, 0, 0], direct=0):
    # 角度
    ang = rot_to_ang(rotation)
    # 尺寸
    width_x, width_z = size[0], size[2]
    # 中心
    center_x, center_z = position[0], position[2]
    # 矩形
    angle = ang
    tmp_x = (width_x / 2 + adjust[3])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x1 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z1 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = -(width_x / 2 + adjust[1])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x2 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z2 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = -(width_x / 2 + adjust[1])
    tmp_z = (width_z / 2 + adjust[2])
    add_x3 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z3 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = (width_x / 2 + adjust[3])
    tmp_z = (width_z / 2 + adjust[2])
    add_x4 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z4 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    [x1, x2, x3, x4] = [center_x + add_x1, center_x + add_x2, center_x + add_x3, center_x + add_x4]
    [z1, z2, z3, z4] = [center_z + add_z1, center_z + add_z2, center_z + add_z3, center_z + add_z4]
    if direct >= 1:
        return [[x2, z2], [x3, z3], [x4, z4], [x1, z1]]
    return [[x1, z1], [x2, z2], [x3, z3], [x4, z4]]


def xyz_to_ang(x1, y1, x2, y2):
    if abs(x2 - x1) < 0.001:
        if y2 >= y1:
            length = y2 - y1
            angle = 0
        else:
            length = y1 - y2
            angle = math.pi
    elif abs(y2 - y1) < 0.001:
        if x2 >= x1:
            length = x2 - x1
            angle = math.pi / 2
        else:
            length = x1 - x2
            angle = math.pi / 2 * 3
    else:
        length = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        angle = math.acos((y2 - y1) / length)
        if x2 - x1 <= -0.001:
            angle = math.pi * 2 - angle
    # 规范
    if angle > math.pi * 2:
        angle -= math.pi * 2
    elif angle < -math.pi * 2:
        angle += math.pi * 2
    # 规范
    if angle > math.pi:
        angle -= math.pi * 2
    elif angle < -math.pi:
        angle += math.pi * 2
    return length, angle


def ang_to_ang(angle_old):
    angle_new = angle_old
    # 计算
    if abs(angle_new - 2 * math.pi) <= 0.01:
        angle_new = 0
    elif abs(angle_new + 2 * math.pi) <= 0.01:
        angle_new = 0
    elif abs(angle_new - math.pi) <= 0.01:
        angle_new = math.pi
    elif abs(angle_new + math.pi) <= 0.01:
        angle_new = math.pi
    else:
        # 规范
        if angle_new > 2 * math.pi:
            angle_new -= 2 * math.pi
        elif angle_new < -2 * math.pi:
            angle_new += 2 * math.pi
        # 规范
        if angle_new <= -math.pi:
            angle_new += 2 * math.pi
        if angle_new > math.pi:
            angle_new -= 2 * math.pi
    # 返回
    return angle_new


def compute_furniture_rely(object_one, line_list, rely_dlt=0.4):
    # 家具矩形
    object_pos, object_rot = object_one['position'], object_one['rotation']
    object_type = object_one['type']
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) for i in range(3)]
    object_unit = compute_furniture_rect(object_size, object_pos, object_rot)
    # 靠墙判断
    # rely_dlt = 0.4
    # if object_type.startswith('sofa'):
    #     rely_dlt = 0.4
    unit_one, unit_idx = object_unit, -1
    unit_one = np.reshape(unit_one, [-1])
    edge_len, edge_idx = int(len(unit_one) / 2), -1
    for j in range(edge_len):
        x_p = unit_one[(2 * j + 0) % len(unit_one)]
        y_p = unit_one[(2 * j + 1) % len(unit_one)]
        x_q = unit_one[(2 * j + 2) % len(unit_one)]
        y_q = unit_one[(2 * j + 3) % len(unit_one)]
        x_r = unit_one[(2 * j + 4) % len(unit_one)]
        y_r = unit_one[(2 * j + 5) % len(unit_one)]
        # 宽度深度
        unit_width, unit_angle = xyz_to_ang(x_p, y_p, x_q, y_q)
        if j <= 1:
            unit_depth = math.sqrt((x_r - x_q) * (x_r - x_q) + (y_r - y_q) * (y_r - y_q))
        else:
            x_o = unit_one[2 * j - 2]
            y_o = unit_one[2 * j - 1]
            unit_depth = math.sqrt((x_o - x_p) * (x_o - x_p) + (y_o - y_p) * (y_o - y_p))
        if unit_width < unit_depth / 2 or unit_width < 0.2:
            continue
        unit_idx = -1
        for line_idx in range(len(line_list)):
            x1 = line_list[line_idx][0]
            y1 = line_list[line_idx][1]
            x2 = line_list[(line_idx + 1) % len(line_list)][0]
            y2 = line_list[(line_idx + 1) % len(line_list)][1]
            if (x1 - x2) ** 2 + (y1 - y2) ** 2 < 1e-5:
                continue
            # 重合方向
            line_width, line_angle = xyz_to_ang(x1, y1, x2, y2)
            if abs(ang_to_ang(line_angle - unit_angle)) > 0.1:
                continue
            if abs(y1 - y2) < 0.1 and abs(x1 - x2) < 0.1:
                continue
            elif abs(y1 - y2) < 0.1:
                if abs(y1 - y_p) > rely_dlt:
                    continue
            elif abs(x1 - x2) < 0.1:
                if abs(x1 - x_p) > rely_dlt:
                    continue
            else:
                r_p_x = (x_p - x1) / (x2 - x1)
                r_p_y = (y_p - y1) / (y2 - y1)
                r_q_x = (x_q - x1) / (x2 - x1)
                r_q_y = (y_q - y1) / (y2 - y1)
                if abs(r_p_x - r_p_y) > 0.01 or abs(r_q_x - r_q_y) > 0.01:
                    continue
            # 重合比例
            if abs(x2 - x1) >= 0.00001:
                r_p = (x_p - x1) / (x2 - x1)
                r_q = (x_q - x1) / (x2 - x1)
            elif abs(y2 - y1) >= 0.00001:
                r_p = (y_p - y1) / (y2 - y1)
                r_q = (y_q - y1) / (y2 - y1)
            else:
                continue
            if r_p <= 0 and r_q <= 0:
                continue
            if r_p >= 1 and r_q >= 1:
                continue
            if abs(r_p - r_q) < 0.001:
                continue
            r1 = max(0, min(r_p, r_q))
            r2 = min(1, max(r_p, r_q))
            if line_width * (r2 - r1) < 0.1:
                continue
            unit_idx = line_idx
            break
        if 0 <= unit_idx < len(line_list):
            edge_idx = j
            break
    return unit_idx, edge_idx


def compute_furniture_rely_soft(object_one, line_list):
    # 家具矩形
    object_pos, object_rot = object_one['position'], object_one['rotation']
    object_type = object_one['type']
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    object_unit = compute_furniture_rect(object_size, object_pos, object_rot)
    object_unit = np.reshape(object_unit, [-1])
    # 靠墙判断
    rely_dlt = 0.1
    if object_type.startswith('sofa'):
        rely_dlt = 0.4
    unit_one, unit_idx = object_unit, -1
    edge_len, edge_idx = int(len(unit_one) / 2), -1
    rely_dis = 0
    for j in range(edge_len):
        x_p = unit_one[(2 * j + 0) % len(unit_one)]
        y_p = unit_one[(2 * j + 1) % len(unit_one)]
        x_q = unit_one[(2 * j + 2) % len(unit_one)]
        y_q = unit_one[(2 * j + 3) % len(unit_one)]
        x_r = unit_one[(2 * j + 4) % len(unit_one)]
        y_r = unit_one[(2 * j + 5) % len(unit_one)]
        # 宽度深度
        unit_width, unit_angle = xyz_to_ang(x_p, y_p, x_q, y_q)
        if j <= 1:
            unit_depth = math.sqrt((x_r - x_q) * (x_r - x_q) + (y_r - y_q) * (y_r - y_q))
        else:
            x_o = unit_one[2 * j - 2]
            y_o = unit_one[2 * j - 1]
            unit_depth = math.sqrt((x_o - x_p) * (x_o - x_p) + (y_o - y_p) * (y_o - y_p))
        if unit_width < unit_depth / 2 or unit_width < 0.2:
            continue
        unit_idx, unit_dis = -1, 0
        for line_idx, line_one in enumerate(line_list):
            # 重合方向
            x1, y1, x2, y2 = line_one['p1'][0], line_one['p1'][1], line_one['p2'][0], line_one['p2'][1]
            line_width, line_angle = line_one['width'], line_one['angle']
            if abs(ang_to_ang(line_angle - unit_angle)) > 0.1:
                continue
            if abs(y1 - y2) < 0.1 and abs(x1 - x2) < 0.1:
                continue
            elif abs(y1 - y2) < 0.1:
                if abs(y1 - y_p) > rely_dlt:
                    continue
            elif abs(x1 - x2) < 0.1:
                if abs(x1 - x_p) > rely_dlt:
                    continue
            else:
                r_p_x = (x_p - x1) / (x2 - x1)
                r_p_y = (y_p - y1) / (y2 - y1)
                r_q_x = (x_q - x1) / (x2 - x1)
                r_q_y = (y_q - y1) / (y2 - y1)
                if abs(r_p_x - r_p_y) > 0.01 or abs(r_q_x - r_q_y) > 0.01:
                    continue
            # 重合比例
            if abs(x2 - x1) >= 0.00001:
                r_p = (x_p - x1) / (x2 - x1)
                r_q = (x_q - x1) / (x2 - x1)
            elif abs(y2 - y1) >= 0.00001:
                r_p = (y_p - y1) / (y2 - y1)
                r_q = (y_q - y1) / (y2 - y1)
            else:
                continue
            if r_p <= 0 and r_q <= 0:
                continue
            if r_p >= 1 and r_q >= 1:
                continue
            if abs(r_p - r_q) < 0.001:
                continue
            r1 = max(0, min(r_p, r_q))
            r2 = min(1, max(r_p, r_q))
            if line_width * (r2 - r1) < 0.1:
                continue
            unit_idx, unit_dis = line_idx, line_width * (r2 - r1)
            break
        if 0 <= unit_idx < len(line_list):
            if unit_dis > rely_dis:
                edge_idx, rely_dis = j, unit_dis
            if unit_dis > unit_width * 0.9 and unit_width > unit_depth:
                break
    return unit_idx, edge_idx


def compute_room_line(room_info, width_min=0.05):
    # 原始轮廓 顶点
    floor_pts = room_info['floor']
    if len(floor_pts) >= 2:
        begin_x, begin_z = floor_pts[0], floor_pts[1]
        end_x, end_z = floor_pts[-2], floor_pts[-1]
        if abs(begin_x - end_x) + abs(begin_z - end_z) >= 0.01:
            room_info['floor'].append(begin_x)
            room_info['floor'].append(begin_z)
    else:
        return []
    floor_len = int(len(floor_pts) / 2)
    # 原始轮廓 线段
    line_ori = []
    for i in range(floor_len - 1):
        # 起点终点
        x1, y1, x2, y2 = floor_pts[2 * i + 0], floor_pts[2 * i + 1], floor_pts[2 * i + 2], floor_pts[2 * i + 3]
        length, angle = xyz_to_ang(x1, y1, x2, y2)
        # 跳过
        if length <= width_min:
            continue
        # 拼接
        if len(line_ori) > 0:
            line_old = line_ori[-1]
            x1_old, y1_old = line_old['p1'][0], line_old['p1'][1]
            x2_old, y2_old = line_old['p2'][0], line_old['p2'][1]
            angle_old = line_old['angle']
            if abs(ang_to_ang(angle - angle_old)) < 0.1 and abs(x2_old - x1) + abs(y2_old - y1) < width_min:
                line_ori.pop(-1)
                x1, y1 = x1_old, y1_old
        # 垂直
        if abs(x2 - x1) <= width_min and abs(y2 - y1) >= 5 * abs(x2 - x1):
            x2 = x1
        if abs(y2 - y1) <= width_min and abs(x2 - x1) >= 5 * abs(y2 - y1):
            y2 = y1
        # 线段角度
        length, angle = xyz_to_ang(x1, y1, x2, y2)
        line_width = length
        line_one = {
            'p1': [x1, y1],
            'p2': [x2, y2],
            'width': line_width,
            'angle': angle
        }
        line_ori.append(line_one)
    # 原始轮廓 去重
    for line_idx in range(len(line_ori) - 1, -1, -1):
        line_1 = line_ori[line_idx]
        line_2 = line_ori[0]
        x1, y1, x2, y2 = line_1['p2'][0], line_1['p2'][1], line_2['p1'][0], line_2['p1'][1]
        angle1, angle2 = line_1['angle'], line_2['angle']
        if abs(angle1 - angle2) < 0.1 and abs(x2 - x1) + abs(y2 - y1) < width_min:
            line_2['p1'] = line_1['p1'][:]
            line_2['width'] += line_1['width']
            line_ori.pop(line_idx)
    return line_ori


def is_coincident_line(base_line, rect_line, dis_thresh=1e-2):
    base_line = [[round(base_line[0][0], 3), round(base_line[0][1], 3)],
                 [round(base_line[1][0], 3), round(base_line[1][1], 3)]]
    rect_line = [[round(rect_line[0][0], 3), round(rect_line[0][1], 3)],
                 [round(rect_line[1][0], 3), round(rect_line[1][1], 3)]]
    base_vec = np.array(base_line[1]) - base_line[0]
    rect_vec = np.array(rect_line[1]) - rect_line[0]
    if np.linalg.norm(rect_vec) < 1e-3:
        return False, [base_line], []
    if np.linalg.norm(base_vec) < 1e-3:
        return False, [], []
    cross_vec_1 = np.array(rect_line[1]) - base_line[0]
    cross_vec_2 = np.array(rect_line[1]) - base_line[1]
    cross_vec = cross_vec_1 if np.linalg.norm(cross_vec_1) > np.linalg.norm(cross_vec_2) else cross_vec_2
    parallel = abs(np.cross(rect_vec, base_vec)) / np.linalg.norm(base_vec) / np.linalg.norm(rect_vec) < 1e-3
    dis = abs(np.cross(cross_vec, base_vec)) / np.linalg.norm(base_vec)
    if parallel and dis < dis_thresh:
        if np.dot(base_vec, rect_vec) < 0:
            rect_line = np.array([rect_line[1], rect_line[0]])
        base_vec_length = np.linalg.norm(base_vec)
        rect_start_vec = np.array(rect_line[0]) - base_line[0]
        start_project_length = np.dot(rect_start_vec, base_vec) / base_vec_length / base_vec_length

        rect_end_vec = np.array(rect_line[1]) - base_line[0]
        end_project_length = np.dot(rect_end_vec, base_vec) / base_vec_length / base_vec_length

        if (start_project_length <= 1e-3 and end_project_length <= 1e-3) or (
                start_project_length > 1. - 1e-3 and end_project_length > 1. - 1e-3):
            return False, [base_line], []
        elif start_project_length <= 1e-3 < end_project_length < 1. - 1e-3:
            # fix by lizuojun 2020.05.31
            val_1 = end_project_length * base_vec + np.array(base_line[0])
            # rm_edge = [base_line[0], end_project_length * base_vec + np.array(base_line[0])]
            # remained_edge = [[end_project_length * base_vec + np.array(base_line[0]), base_line[1]]]
            rm_edge = [base_line[0], val_1.tolist()]
            remained_edge = [[val_1.tolist(), base_line[1]]]
            return True, remained_edge, rm_edge
        elif 1e-3 < start_project_length < 1. - 1e-3 <= end_project_length:
            # fix by lizuojun 2020.05.31
            val_1 = start_project_length * base_vec + np.array(base_line[0])
            # rm_edge = [start_project_length * base_vec + np.array(base_line[0]), base_line[1]]
            # remained_edge = [[base_line[0], start_project_length * base_vec + np.array(base_line[0])]]
            rm_edge = [val_1.tolist(), base_line[1]]
            remained_edge = [[base_line[0], val_1.tolist()]]
            return True, remained_edge, rm_edge
        elif start_project_length <= 1e-3 and end_project_length >= 1.0 - 1e-3:
            return True, [], base_line
        else:
            # fix by lizuojun 2020.05.31
            val_1 = start_project_length * base_vec + np.array(base_line[0])
            val_2 = end_project_length * base_vec + np.array(base_line[0])
            return True, [[base_line[0], val_1.tolist()], [val_2.tolist(), base_line[1]]], [val_1.tolist(),
                                                                                            val_2.tolist()]
            # return True, [[base_line[0], start_project_length * base_vec + np.array(base_line[0])],
            #               [end_project_length * base_vec + np.array(base_line[0]), base_line[1]]], \
            #        [start_project_length * base_vec + np.array(base_line[0]),
            #         end_project_length * base_vec + np.array(base_line[0])]
    else:
        return False, [base_line], []


def extend_edge(base_edge, extend, thresh=1e-3, max_len=None):
    extend = np.array(extend)
    extend_len = np.linalg.norm(extend[0] - extend[1])
    # print(extend_len, max_len)
    if max_len is not None:
        max_len = min(max_len, extend_len)
    if abs(np.cross(np.array(base_edge[0]) - base_edge[1],
                np.array(extend[0]) - extend[1])) < 1e-3:
        if np.linalg.norm(np.array(base_edge[0]) - extend[0]) < thresh:
            if max_len is not None:
                extend[1] = (extend[1] - extend[0]) / extend_len * max_len + extend[0]
            base_edge = [extend[1], base_edge[1]]
            return True, np.array(base_edge).tolist()
        elif np.linalg.norm(np.array(base_edge[0]) - extend[1]) < thresh:
            if max_len is not None:
                extend[0] = (extend[0] - extend[1]) / extend_len * max_len + extend[1]
            base_edge = [extend[0], base_edge[1]]
            return True, np.array(base_edge).tolist()
        elif np.linalg.norm(np.array(base_edge[1]) - extend[0]) < thresh:
            if max_len is not None:
                extend[1] = (extend[1] - extend[0]) / extend_len * max_len + extend[0]
            base_edge = [base_edge[0], extend[1]]
            return True, np.array(base_edge).tolist()
        elif np.linalg.norm(np.array(base_edge[1]) - extend[1]) < thresh:
            if max_len is not None:
                extend[0] = (extend[0] - extend[1]) / extend_len * max_len + extend[1]
            base_edge = [base_edge[0], extend[0]]
            return True, np.array(base_edge).tolist()
    return False, np.array(base_edge).tolist()


def quaternion_to_rotation_matrix(quat):
    q = np.array(quat).copy()
    n = np.dot(q, q)
    if n < np.finfo(q.dtype).eps:
        return np.identity(3)
    q = q * np.sqrt(2.0 / n)
    q = np.outer(q, q)
    rot_matrix = np.array(
        [[1.0 - q[2, 2] - q[3, 3], q[1, 2] + q[3, 0], q[1, 3] - q[2, 0]],
         [q[1, 2] - q[3, 0], 1.0 - q[1, 1] - q[3, 3], q[2, 3] + q[1, 0]],
         [q[1, 3] + q[2, 0], q[2, 3] - q[1, 0], 1.0 - q[1, 1] - q[2, 2]]],
        dtype=q.dtype)
    return rot_matrix


def rot_to_mat(rot):
    angle = rot_to_ang(rot)
    rot = np.mat([[np.cos(-angle), -np.sin(-angle)],
                  [np.sin(-angle), np.cos(-angle)]])
    return rot


def combine_coincident_lines(base_line, tar_line):

    # base_line = [[round(base_line[0][0], 3), round(base_line[0][1], 3)],
    #              [round(base_line[1][0], 3), round(base_line[1][1], 3)]]
    # tar_line = [[round(tar_line[0][0], 3), round(tar_line[0][1], 3)],
    #              [round(tar_line[1][0], 3), round(tar_line[1][1], 3)]]
    base_vec = np.array(base_line[1]) - base_line[0]
    rect_vec = np.array(tar_line[1]) - tar_line[0]
    cross_vec_1 = np.array(tar_line[1]) - base_line[0]
    cross_vec_2 = np.array(tar_line[1]) - base_line[1]
    if np.linalg.norm(base_vec) < 1e-3:
        if np.linalg.norm(rect_vec) < 1e-3:
            if np.linalg.norm(cross_vec_1) < 1e-3:
                return True, base_line
            else:
                return False, []
        else:
            flag, _ = check_pt_in_line(base_line[0], tar_line)
            if flag:
                return True, tar_line
            else:
                return False, []
    elif np.linalg.norm(rect_vec) < 1e-3:
        flag, _ = check_pt_in_line(tar_line[0], base_line)
        if flag:
            return True, base_line
        else:
            return False, []
    else:
        cross_vec = cross_vec_1 if np.linalg.norm(cross_vec_1) > np.linalg.norm(cross_vec_2) else cross_vec_2
        if abs(np.cross(rect_vec, base_vec)) / np.linalg.norm(base_vec) / np.linalg.norm(rect_vec) < 1e-3 and \
               abs(np.cross(cross_vec, base_vec)) / np.linalg.norm(base_vec) < 1e-2:
            if np.dot(base_vec, rect_vec) < 0:
                tar_line = np.array([tar_line[1], tar_line[0]])
            base_vec_length = np.linalg.norm(base_vec)
            rect_start_vec = np.array(tar_line[0]) - base_line[0]
            start_project_length = np.dot(rect_start_vec, base_vec) / base_vec_length / base_vec_length

            rect_end_vec = np.array(tar_line[1]) - base_line[0]
            end_project_length = np.dot(rect_end_vec, base_vec) / base_vec_length / base_vec_length

            if (start_project_length <= -1e-3 and end_project_length <= -1e-3) or (
                    start_project_length > 1. + 1e-3 and end_project_length > 1. + 1e-3):
                return False, []
            elif start_project_length <= -1e-3 < end_project_length < 1. + 1e-3:
                return True, [tar_line[0], base_line[1]]
            elif 1e-3 < start_project_length < 1. + 1e-3 <= end_project_length:
                return True, [base_line[0], tar_line[1]]
            elif start_project_length <= 1e-3 and end_project_length >= 1.0 - 1e-3:
                return True, tar_line
            else:
                return True, base_line
        else:
            return False, []
