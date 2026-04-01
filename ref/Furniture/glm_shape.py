# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2019-06-15
@Description:

"""

from Furniture.glm_interface import *


def glm_shape_obj(model, type=''):
    decor_bot, decor_bak, decor_frt, ratio = {}, {}, {}, 1.0
    if not model:
        return decor_bot, decor_bak, decor_frt, ratio
    # 范围
    size = [model.bbox.max[0] - model.bbox.min[0],
            model.bbox.max[1] - model.bbox.min[1],
            model.bbox.max[2] - model.bbox.min[2]]
    h_min, h_max = 0, size[1]
    w_min, w_max = -size[0] * 0.5, size[0] * 0.5
    d_min, d_max = -size[2] * 0.5, size[2] * 0.5
    if h_max - h_min < 10 and w_max - w_min < 10 and d_max - d_min < 10:
        ratio = 100
        h_min, h_max = h_min * ratio, h_max * ratio
        w_min, w_max = w_min * ratio, w_max * ratio
        d_min, d_max = d_min * ratio, d_max * ratio
        size[0] *= ratio
        size[1] *= ratio
        size[2] *= ratio
    h_max = size[1] + 1
    # 步长
    h_dlt, w_dlt, d_dlt, s_min = 0, 2, 2, 10
    edge_min = min(5, size[0] / 20, size[2] / 20)
    norm_min = 0.90
    if 'shelf' in type:
        type = 'cabinet'
    # 类型
    if 'sofa' in type:
        h_min = min(25, size[1] * 0.3)
        h_max = max(50, size[1] * 0.6)
        if size[1] < 100:
            h_max = max(size[1] - 5, size[1] * 0.9)
        h_dlt, w_dlt, s_min = 2, 10, 20
        norm_min = 0.80
    elif 'window' in type:
        h_min = 0
        h_max = max(60, size[1] * 0.6)
        h_dlt, w_dlt, s_min = 5, 5, 20
    elif 'table' in type and 'dining' in type:
        h_min = min(50, size[1] * 0.8)
        h_dlt, w_dlt, s_min = 1, 1, 10
    elif 'table' in type and size[1] > 60:
        h_min = min(5, size[1] * 0.1)
    elif 'cabinet' in type and size[2] > size[0] * 0.4 and size[2] > 40:
        h_dlt = 1
    elif 'cabinet' in type:
        h_dlt = 1
    # 分类
    dict_bot, dict_ver, dict_bak = {}, {}, {}
    for index, triangle in enumerate(model.faces):
        if len(triangle.v_indices) < 3:
            continue
        normal = model.faces_normals[index + 1]
        if abs(normal[1]) > norm_min or abs(normal[0]) > norm_min or abs(normal[2]) > norm_min:
            pass
        else:
            continue
        v0_index, v1_index, v2_index = triangle.v_indices[0], triangle.v_indices[1], triangle.v_indices[2]
        v0_old, v1_old, v2_old = model.vertices[v0_index], model.vertices[v1_index], model.vertices[v2_index]
        v0 = [v0_old[0] * ratio, v0_old[1] * ratio, v0_old[2] * ratio]
        v1 = [v1_old[0] * ratio, v1_old[1] * ratio, v1_old[2] * ratio]
        v2 = [v2_old[0] * ratio, v2_old[1] * ratio, v2_old[2] * ratio]
        # 水平
        if abs(normal[1]) > norm_min:
            d0 = abs(v0[0] - v2[0]) + abs(v0[2] - v2[2])
            d1 = abs(v1[0] - v0[0]) + abs(v1[2] - v0[2])
            d2 = abs(v2[0] - v1[0]) + abs(v2[2] - v1[2])
            if min(d0, d1, d2) < edge_min:
                continue
        # 竖直
        elif abs(normal[0]) > norm_min:
            d0 = abs(v0[1] - v2[1]) + abs(v0[2] - v2[2])
            d1 = abs(v1[1] - v0[1]) + abs(v1[2] - v0[2])
            d2 = abs(v2[1] - v1[1]) + abs(v2[2] - v1[2])
            if min(d0, d1, d2) < edge_min:
                continue
        # 靠墙
        elif abs(normal[2]) > norm_min:
            d0 = abs(v0[0] - v2[0]) + abs(v0[1] - v2[1])
            d1 = abs(v1[0] - v0[0]) + abs(v1[1] - v0[1])
            d2 = abs(v2[0] - v1[0]) + abs(v2[1] - v1[1])
            if 'sofa' in type:
                if min(d0, d1, d2) < edge_min:
                    continue
            elif min(d0, d1, d2) < min(20, size[0] / 5, size[1] / 5):
                continue
        # 水平
        if abs(normal[1]) > norm_min:
            dict_now = dict_bot
            h = math.ceil(min(v0[1], v1[1], v2[1]))
            if 'sofa' in type:
                h = math.floor(min(v0[1], v1[1], v2[1]))
            if h <= h_min:
                continue
            elif h >= h_max:
                continue
            if abs(h - int(size[1])) <= 2:
                h = int(size[1])
            x_min, z_min = min(v0[0], v1[0], v2[0]), min(v0[2], v1[2], v2[2])
            x_max, z_max = max(v0[0], v1[0], v2[0]), max(v0[2], v1[2], v2[2])
            h_new = h
            # 查找
            if 'sofa' in type:
                for dlt in range(int(h_dlt) + 1):
                    h_1, h_2 = h + dlt, h - dlt
                    if h_1 in dict_now:
                        h_new = h_1
                        break
                    if h_2 in dict_now:
                        h_new = h_2
                        break
            else:
                for dlt in range(int(h_dlt), -1, -1):
                    h_1, h_2 = h + dlt, h - dlt
                    if h_1 in dict_now:
                        h_new = h_1
                        break
                    if h_2 in dict_now:
                        h_new = h_2
                        break
            h = h_new
            if h not in dict_now:
                dict_now[h] = [[x_min, h, z_min, x_max, h, z_max, 0]]
            else:
                face_set = dict_now[h]
                find_idx = -1
                for face_idx, face_one in enumerate(face_set):
                    if x_min + z_min < face_one[0] + face_one[2]:
                        find_idx = face_idx
                        break
                if find_idx >= 0:
                    face_set.insert(face_idx, [x_min, h, z_min, x_max, h, z_max, 0])
                else:
                    face_set.append([x_min, h, z_min, x_max, h, z_max, 0])
        # 竖直
        if abs(normal[0]) > norm_min:
            if 'table' in type or 'cabinet' in type or 'unit' in type:
                pass
            else:
                continue
            dict_now = dict_ver
            w = int((v0[0] + v1[0] + v2[0]) / 3)
            if abs(w - w_min) < 4:
                continue
            if abs(w - w_max) < 4:
                continue
            y_min, z_min = min(v0[1], v1[1], v2[1]), min(v0[2], v1[2], v2[2])
            y_max, z_max = max(v0[1], v1[1], v2[1]), max(v0[2], v1[2], v2[2])
            w_new = w
            for dlt in range(int(w_dlt), -1, -1):
                w_1, w_2 = w - dlt, w + dlt
                if w_1 in dict_now:
                    w_new = w_1
                    break
                if w_2 in dict_now:
                    w_new = w_2
                    break
            w = w_new
            if w not in dict_now:
                dict_now[w] = [[w, y_min, z_min, w, y_max, z_max, 0]]
            else:
                face_set = dict_now[w]
                find_idx = -1
                for face_idx, face_one in enumerate(face_set):
                    if y_min + z_min <= face_one[1] + face_one[2]:
                        find_idx = face_idx
                        break
                if find_idx >= 0:
                    face_set.insert(face_idx, [w, y_min, z_min, w, y_max, z_max, 0])
                else:
                    face_set.append([w, y_min, z_min, w, y_max, z_max, 0])
        # 靠墙
        if abs(normal[2]) > norm_min:
            if 'sofa' in type:
                pass
            elif 'table' in type or 'cabinet' in type:
                pass
            else:
                continue
            dict_now = dict_bak
            d = int(max(v0[2], v1[2], v2[2]))
            if abs(d - d_min) < 1:
                continue
            # if abs(d - d_max) < 10:
            #     continue
            x_min, y_min = min(v0[0], v1[0], v2[0]), min(v0[1], v1[1], v2[1])
            x_max, y_max = max(v0[0], v1[0], v2[0]), max(v0[1], v1[1], v2[1])
            d_new = d
            for dlt in range(int(d_dlt) + 1, -1, -1):
                d_1, d_2 = d + dlt, d - dlt
                if d_1 in dict_now:
                    d_new = d_1
                    break
                if d_2 in dict_now:
                    d_new = d_2
                    break
            d = d_new
            if d not in dict_now:
                dict_now[d] = [[x_min, y_min, d, x_max, y_max, d, 0]]
            else:
                face_set = dict_now[d]
                find_idx = -1
                for face_idx, face_one in enumerate(face_set):
                    if x_min + y_min <= face_one[0] + face_one[1]:
                        find_idx = face_idx
                        break
                if find_idx >= 0:
                    face_set.insert(face_idx, [x_min, y_min, d, x_max, y_max, d, 0])
                else:
                    face_set.append([x_min, y_min, d, x_max, y_max, d, 0])

    # 融合 水平
    face_min = 1
    for dict_now in [dict_bot]:
        # 遍历 水平
        dump_list = []
        for plat_key, plat_val in dict_now.items():
            plat_len = len(plat_val)
            # 舍弃
            if plat_len < face_min:
                dump_list.append(plat_key)
                continue
            # 添加
            face_list, face_used, face_sort = plat_val, {}, []
            for face_idx in range(plat_len):
                if face_idx in face_used:
                    continue
                face_used[face_idx] = face_idx
                face_one = face_list[face_idx][:]
                face_cnt = 1
                for side_idx in range(face_idx + 1, plat_len):
                    if side_idx in face_used:
                        continue
                    side_one = face_list[side_idx]
                    side_width = side_one[3] - side_one[0]
                    side_depth = side_one[5] - side_one[2]
                    face_width = face_one[3] - face_one[0]
                    face_depth = face_one[5] - face_one[2]
                    if side_one[0] > face_one[3] + w_dlt:
                        break
                    elif side_one[3] < face_one[0] - w_dlt:
                        break
                    elif side_one[2] > face_one[5] + w_dlt:
                        break
                    elif side_one[5] < face_one[2] - w_dlt:
                        break
                    elif side_width > side_depth * 5 and face_depth > side_depth * 5 and side_depth < 5:
                        continue
                    elif face_width > face_depth * 5 and side_depth > face_depth * 5 and face_depth < 5:
                        break
                    # 0 + 1
                    elif face_one[5] - side_one[5] > 40 and side_one[3] + w_dlt > face_one[3] and \
                            face_one[3] < (side_one[0] + side_one[3]) / 2:
                        face_one[2] = max(face_one[2], side_one[5] + w_dlt + 1)
                        break
                    # 0 + 3
                    elif side_one[5] - face_one[5] > 20 and side_one[3] + w_dlt > face_one[3] and \
                            side_one[0] > (face_one[0] + face_one[3]) / 2:
                        side_one[2] = max(side_one[2], face_one[5] + w_dlt + 1)
                        continue
                    # table
                    elif face_depth > face_width * 2 and side_width > min(side_depth * 1.5, side_depth + 10) and \
                            face_depth > 20 and face_depth > side_depth * 2 and 'table' in type:
                        side_one[0] = max(side_one[0], face_one[3] + w_dlt + 1)
                        break
                    elif face_width > face_depth * 2 and side_depth > min(side_width * 1.5, side_width + 10) and \
                            face_width > 20 and face_width > side_width * 2 and 'table' in type:
                        side_one[2] = max(side_one[2], face_one[5] + w_dlt + 1)
                        break
                    elif face_depth > face_width * 2 and face_depth > side_depth * 2 and 'table' in type:
                        side_one[0] = max(side_one[0], face_one[3] + w_dlt + 1)
                        side_one[0] = min(side_one[3] - 1, side_one[3])
                        break
                    elif face_width > face_depth * 2 and side_depth > face_depth * 2 and 'table' in type:
                        side_one[2] = max(side_one[2], face_one[5] + w_dlt + 1)
                        side_one[2] = min(side_one[5] - 1, side_one[2])
                        break
                    elif side_depth > side_width * 2 and side_depth > face_depth * 2 and 'table' in type:
                        side_one[2] = max(side_one[2], face_one[5] + w_dlt + 1)
                        side_one[2] = min(side_one[5] - 1, side_one[2])
                        break
                    else:
                        face_used[side_idx] = face_idx
                        face_one = [min(face_one[0], side_one[0]), plat_key, min(face_one[2], side_one[2]),
                                    max(face_one[3], side_one[3]), plat_key, max(face_one[5], side_one[5]), 0]
                        face_cnt += 1
                if face_cnt < face_min:
                    continue
                dlt_x, dlt_z = face_one[3] - face_one[0], face_one[5] - face_one[2]
                face_add = False
                if dict_now == dict_bot:
                    if plat_key > 100:
                        if max(dlt_x, dlt_z) > 15 and min(dlt_x, dlt_z) > 10:
                            face_add = True
                    else:
                        if max(dlt_x, dlt_z) > 20 and min(dlt_x, dlt_z) > 10:
                            face_add = True
                if min(dlt_x, dlt_z) < s_min:
                    face_add = False
                if face_add:
                    face_add = True
                    for sort_idx, face_old in enumerate(face_sort):
                        # 拐角处理
                        if face_one[5] - face_old[5] > 20:
                            if face_one[3] < (face_old[0] + face_old[3]) / 2:
                                if face_one[0] - 1 <= face_old[0] <= face_one[3] + 1:
                                    if face_one[2] < face_old[5]:
                                        face_old[0] = min(face_old[0], face_one[0])
                                        face_old[2] = min(face_old[2], face_one[2])
                                face_one[2] = max(face_one[2], face_old[5] + w_dlt + 1)
                                continue
                            elif face_one[0] > (face_old[0] + face_old[3]) / 2:
                                if face_one[0] - 1 <= face_old[3] <= face_one[3] + 1:
                                    if face_one[2] < face_old[5]:
                                        face_old[2] = min(face_old[2], face_one[2])
                                        face_old[3] = max(face_old[3], face_one[3])
                                face_one[2] = max(face_one[2], face_old[5] + w_dlt + 1)
                                continue
                        # 合并处理
                        if face_one[0] < face_old[0] + w_dlt and face_old[3] - w_dlt < face_one[3]:
                            if face_one[2] < face_old[2] + w_dlt and face_old[5] - w_dlt < face_one[5]:
                                face_sort[sort_idx] = face_one
                                face_add = False
                                break
                        if face_old[0] < face_one[0] + w_dlt and face_one[3] - w_dlt < face_old[3]:
                            if face_old[2] < face_one[2] + w_dlt and face_one[5] - w_dlt < face_old[5]:
                                face_add = False
                                break
                        face_merge = False
                        if face_old[0] - w_dlt <= face_one[0] <= face_old[3] + w_dlt:
                            if face_old[2] - w_dlt <= face_one[2] <= face_old[5] + w_dlt:
                                face_merge = True
                        if face_old[0] - w_dlt <= (face_one[0] + face_one[3]) / 2 <= face_old[3] + w_dlt:
                            if face_old[2] - w_dlt <= face_one[2] <= face_old[5] + w_dlt:
                                face_merge = True
                        if face_one[0] - w_dlt < face_old[0] < face_one[3] + w_dlt:
                            if face_one[2] - w_dlt < face_old[2] < face_one[5] + w_dlt:
                                face_merge = True
                        if face_merge:
                            face_old[0] = min(face_one[0], face_old[0])
                            face_old[2] = min(face_one[2], face_old[2])
                            face_old[3] = max(face_one[3], face_old[3])
                            face_old[5] = max(face_one[5], face_old[5])
                            face_add = False
                            break
                if face_add:
                    face_sort.append(face_one)
            # 合并
            face_good = []
            for face_one in face_sort:
                face_add = True
                for fine_idx, face_old in enumerate(face_good):
                    if face_one[0] < face_old[0] + w_dlt and face_old[3] - w_dlt < face_one[3]:
                        if face_one[2] < face_old[2] + w_dlt and face_old[5] - w_dlt < face_one[5]:
                            face_good[fine_idx] = face_one
                            face_one[2] = min(face_old[2], face_one[2])
                            face_one[3] = max(face_old[3], face_one[3])
                            face_one[5] = max(face_old[5], face_one[5])
                            face_add = False
                            break
                    if face_old[0] < face_one[0] + w_dlt and face_one[3] - w_dlt < face_old[3]:
                        if face_old[2] < face_one[2] + w_dlt and face_one[5] - w_dlt < face_old[5]:
                            face_old[2] = min(face_old[2], face_one[2])
                            face_old[3] = max(face_old[3], face_one[3])
                            face_old[5] = max(face_old[5], face_one[5])
                            face_add = False
                            break
                    if 'sofa' in type and abs(face_old[5] - face_one[5]) < w_dlt * 2:
                        if face_one[0] <= face_old[3] + 40:
                            face_old[2] = min(face_old[2], face_one[2])
                            face_old[3] = max(face_old[3], face_one[3])
                            face_old[5] = max(face_old[5], face_one[5])
                            face_add = False
                            break
                if face_add:
                    face_good.append(face_one)
            face_best = face_good
            # 合并
            face_best = []
            for face_one in face_good:
                face_add = True
                for fine_idx, face_old in enumerate(face_best):
                    if face_one[0] < face_old[0] + w_dlt and face_old[3] - w_dlt < face_one[3]:
                        if face_one[2] < face_old[2] + w_dlt and face_old[5] - w_dlt < face_one[5]:
                            face_best[fine_idx] = face_one
                            face_one[3] = max(face_old[3], face_one[3])
                            face_one[5] = max(face_old[5], face_one[5])
                            face_add = False
                            break
                    if face_old[0] < face_one[0] + w_dlt and face_one[3] - w_dlt < face_old[3]:
                        if face_old[2] < face_one[2] + w_dlt and face_one[5] - w_dlt < face_old[5]:
                            face_old[3] = max(face_old[3], face_one[3])
                            face_old[5] = max(face_old[5], face_one[5])
                            face_add = False
                            break
                    if 'sofa' in type:
                        if abs(face_old[5] - face_one[5]) < w_dlt * 2:
                            if face_one[0] <= face_old[3] + w_dlt * 4:
                                face_old[2] = min(face_old[2], face_one[2])
                                face_old[3] = max(face_old[3], face_one[3])
                                face_old[5] = max(face_old[5], face_one[5])
                                face_add = False
                                break
                if face_add:
                    face_best.append(face_one)
            # 添加
            if len(face_best) <= 0:
                dump_list.append(plat_key)
                continue
            else:
                dict_now[plat_key] = face_best
        # 舍弃 水平
        for dump_key in dump_list:
            dict_now.pop(dump_key)
    # 融合 竖直
    face_min = 1
    for dict_now in [dict_ver]:
        # 遍历 竖直
        dump_list = []
        for plat_key, plat_val in dict_now.items():
            plat_len = len(plat_val)
            # 舍弃
            if plat_len < face_min:
                dump_list.append(plat_key)
                continue
            # 添加
            face_list, face_used, face_sort = plat_val, {}, []
            for face_idx in range(plat_len):
                if face_idx in face_used:
                    continue
                face_used[face_idx] = face_idx
                face_one = face_list[face_idx][:]
                face_cnt = 1
                for side_idx in range(face_idx + 1, plat_len):
                    side_one = face_list[side_idx]
                    if side_one[1] > face_one[4] + w_dlt:
                        break
                    elif side_one[2] > face_one[5] + w_dlt:
                        break
                    else:
                        face_used[side_idx] = face_idx
                        face_one = [plat_key, min(face_one[1], side_one[1]), min(face_one[2], side_one[2]),
                                    plat_key, max(face_one[4], side_one[4]), max(face_one[5], side_one[5]), 0]
                        face_cnt += 1
                if face_cnt < face_min:
                    continue
                dlt_y, dlt_z = face_one[4] - face_one[1], face_one[5] - face_one[2]
                face_add = True
                if max(dlt_y, dlt_z) < s_min or min(dlt_y, dlt_z) < 2:
                    face_add = False
                if face_add:
                    face_add = True
                    for sort_idx, face_old in enumerate(face_sort):
                        # 合并处理
                        if face_one[1] < face_old[1] + w_dlt and face_old[4] - w_dlt < face_one[4]:
                            if face_one[2] < face_old[2] + w_dlt and face_old[5] - w_dlt < face_one[5]:
                                face_sort[sort_idx] = face_one
                                face_add = False
                                break
                        if face_old[1] < face_one[1] + w_dlt and face_one[4] - w_dlt < face_old[4]:
                            if face_old[2] < face_one[2] + w_dlt and face_one[5] - w_dlt < face_old[5]:
                                face_add = False
                                break
                        if face_old[1] - w_dlt < face_one[1] < face_old[4] + w_dlt:
                            if face_old[2] - w_dlt < face_one[2] < face_old[5] + w_dlt:
                                face_old[1] = min(face_one[1], face_old[1])
                                face_old[2] = min(face_one[2], face_old[2])
                                face_old[4] = max(face_one[4], face_old[4])
                                face_old[5] = max(face_one[5], face_old[5])
                                face_add = False
                                break
                        if face_one[1] - w_dlt < face_old[1] < face_one[4] + w_dlt:
                            if face_one[2] - w_dlt < face_old[2] < face_one[5] + w_dlt:
                                face_old[1] = min(face_one[1], face_old[1])
                                face_old[2] = min(face_one[2], face_old[2])
                                face_old[4] = max(face_one[4], face_old[4])
                                face_old[5] = max(face_one[5], face_old[5])
                                face_add = False
                                break
                if face_add:
                    face_sort.append(face_one)
            # 合并
            face_good = []
            for face_one in face_sort:
                face_add = True
                for fine_idx, face_old in enumerate(face_good):
                    if face_one[1] < face_old[1] + w_dlt and face_old[4] - w_dlt < face_one[4]:
                        if face_one[2] < face_old[2] + w_dlt and face_old[5] - w_dlt < face_one[5]:
                            face_good[fine_idx] = face_one
                            face_one[2] = min(face_old[2], face_one[2])
                            face_one[4] = max(face_old[4], face_one[4])
                            face_one[5] = max(face_old[5], face_one[5])
                            face_add = False
                            break
                    if face_old[1] < face_one[1] + w_dlt and face_one[4] - w_dlt < face_old[4]:
                        if face_old[2] < face_one[2] + w_dlt and face_one[5] - w_dlt < face_old[5]:
                            face_old[2] = min(face_old[2], face_one[2])
                            face_old[4] = max(face_old[4], face_one[4])
                            face_old[5] = max(face_old[5], face_one[5])
                            face_add = False
                            break
                if face_add:
                    face_good.append(face_one)
            face_best = face_good
            # 添加
            if len(face_best) <= 0:
                dump_list.append(plat_key)
                continue
            else:
                dict_now[plat_key] = face_best
        # 舍弃 竖直
        for dump_key in dump_list:
            dict_now.pop(dump_key)
    # 融合 靠墙
    face_min = 1
    for dict_now in [dict_bak]:
        # 遍历 靠墙
        dump_list = []
        for plat_key, plat_val in dict_now.items():
            plat_len = len(plat_val)
            # 舍弃
            if plat_len < face_min:
                dump_list.append(plat_key)
                continue
            # 添加
            face_list, face_used, face_sort = plat_val, {}, []
            for face_idx in range(plat_len):
                if face_idx in face_used:
                    continue
                face_used[face_idx] = face_idx
                face_one = face_list[face_idx][:]
                face_cnt = 1
                for side_idx in range(face_idx + 1, plat_len):
                    side_one = face_list[side_idx]
                    side_width = side_one[3] - side_one[0]
                    side_height = side_one[4] - side_one[1]
                    face_width = face_one[3] - face_one[0]
                    face_height = face_one[4] - face_one[1]
                    if side_one[0] > face_one[3] + w_dlt:
                        break
                    elif side_one[3] < face_one[0] - w_dlt:
                        break
                    elif side_one[1] > face_one[4] + w_dlt:
                        break
                    elif side_one[4] < face_one[1] - w_dlt:
                        break
                    elif side_width > side_height * 5 and face_height > side_height * 5 and side_height < 5:
                        continue
                    elif face_width > face_height * 5 and side_height > face_height * 5 and face_height < 5:
                        break
                    else:
                        face_used[side_idx] = face_idx
                        face_one = [min(face_one[0], side_one[0]), min(face_one[1], side_one[1]), plat_key,
                                    max(face_one[3], side_one[3]), max(face_one[4], side_one[4]), plat_key, 0]
                        face_cnt += 1
                if face_cnt < face_min:
                    continue
                dlt_x, dlt_y = face_one[3] - face_one[0], face_one[4] - face_one[1]
                face_add = True
                if max(dlt_x, dlt_y) < s_min or min(dlt_x, dlt_y) < s_min:
                    face_add = False
                if face_add:
                    face_add = True
                    for sort_idx, face_old in enumerate(face_sort):
                        face_dlt = min(10, (face_old[3] - face_old[0]) / 10)
                        # 合并处理
                        if face_one[0] < face_old[0] + face_dlt and face_old[3] - face_dlt < face_one[3]:
                            if face_one[1] < face_old[1] + w_dlt and face_old[4] - w_dlt < face_one[4]:
                                face_sort[sort_idx] = face_one
                                face_add = False
                                break
                        if face_old[0] < face_one[0] + face_dlt and face_one[3] - face_dlt < face_old[3]:
                            if face_old[1] < face_one[1] + w_dlt and face_one[4] - w_dlt < face_old[4]:
                                face_add = False
                                break
                            if face_one[1] < face_old[1] + w_dlt and face_old[4] - w_dlt < face_one[4]:
                                face_sort[sort_idx] = face_one
                                face_add = False
                                break
                        if face_old[0] - face_dlt < face_one[0] < face_old[3] + face_dlt:
                            if face_old[1] - w_dlt < face_one[1] < face_old[4] + w_dlt:
                                face_old[0] = min(face_one[0], face_old[0])
                                face_old[1] = min(face_one[1], face_old[1])
                                face_old[3] = max(face_one[3], face_old[3])
                                face_old[4] = max(face_one[4], face_old[4])
                                face_add = False
                                break
                        if face_one[0] - face_dlt < face_old[0] < face_one[3] + face_dlt:
                            if face_one[1] - w_dlt < face_old[1] < face_one[4] + w_dlt:
                                face_old[0] = min(face_one[0], face_old[0])
                                face_old[1] = min(face_one[1], face_old[1])
                                face_old[3] = max(face_one[3], face_old[3])
                                face_old[4] = max(face_one[4], face_old[4])
                                face_add = False
                                break
                if face_add:
                    face_sort.append(face_one)
            # 合并
            face_good = []
            for face_one in face_sort:
                face_add = True
                for fine_idx, face_old in enumerate(face_good):
                    if face_one[0] < face_old[0] + w_dlt and face_old[3] - w_dlt < face_one[3]:
                        if face_one[1] < face_old[1] + w_dlt and face_old[4] - w_dlt < face_one[4]:
                            face_good[fine_idx] = face_one
                            face_one[0] = min(face_old[0], face_one[0])
                            face_one[3] = max(face_old[3], face_one[3])
                            face_one[4] = max(face_old[4], face_one[4])
                            face_add = False
                            break
                    if face_old[0] < face_one[0] + w_dlt and face_one[3] - w_dlt < face_old[3]:
                        if face_old[1] < face_one[1] + w_dlt and face_one[4] - w_dlt < face_old[4]:
                            face_old[0] = min(face_old[0], face_one[0])
                            face_old[3] = max(face_old[3], face_one[3])
                            face_old[4] = max(face_old[4], face_one[4])
                            face_add = False
                            break
                if face_add:
                    face_good.append(face_one)
            face_best = face_good
            # 添加
            if len(face_best) <= 0:
                dump_list.append(plat_key)
                continue
            else:
                dict_now[plat_key] = face_best
        # 舍弃 竖直
        for dump_key in dump_list:
            dict_now.pop(dump_key)

    # 间隔 水平
    grid_dict, grid_step = {}, 50
    # 切分 水平
    for bot_key, bot_val in dict_bot.items():
        # 判断
        if bot_key <= 0:
            continue
        bot_set = dict_bot[bot_key]
        bot_set_new = []
        for bot_old in bot_set:
            bot_width = bot_old[3] - bot_old[0]
            bot_depth = bot_old[5] - bot_old[2]
            # 检查
            ver_key_list, ver_key_high = [], {}
            for ver_key, ver_val in dict_ver.items():
                if ver_key <= bot_old[0] + 1 or ver_key >= bot_old[3] - 1:
                    continue
                for ver_one in ver_val:
                    if ver_one[1] >= bot_old[1] + 20 or ver_one[4] <= bot_old[1] + 1:
                        continue
                    elif ver_one[2] >= bot_old[5] - 1 or ver_one[5] <= bot_old[2] + 1:
                        continue
                    elif 0 < ver_one[5] - bot_old[2] < min((bot_old[5] - bot_old[2]) * 0.2, 4):
                        continue
                    elif 0 < bot_old[5] - ver_one[2] < min((bot_old[5] - bot_old[2]) * 0.2, 4):
                        continue
                    else:
                        ver_key_list.append(ver_key)
                        ver_key_high[ver_key] = ver_one[4] - ver_one[1]
                        break
            ver_key_list.sort()
            ver_key_list.insert(0, bot_old[0])
            ver_key_list.append(bot_old[3])
            if len(ver_key_list) == 2 and ver_key_list[0] < 0 < ver_key_list[1]:
                if 'cabinet' in type and bot_old[1] > 10 and size[2] > size[0] * 0.5 and size[2] > 40:
                    if ver_key_list[0] < -ver_key_list[1] - 10 and -ver_key_list[1] - ver_key_list[0] > 20:
                        ver_key_list[1] = -ver_key_list[1]
                    elif ver_key_list[1] > -ver_key_list[0] + 10 and ver_key_list[1] + ver_key_list[0] > 20:
                        ver_key_list[0] = -ver_key_list[0]
            # 切分
            for ver_key_idx in range(len(ver_key_list)):
                if ver_key_idx + 1 >= len(ver_key_list):
                    break
                ver_key_one = ver_key_list[ver_key_idx + 0]
                ver_key_two = ver_key_list[ver_key_idx + 1]
                if ver_key_two - ver_key_one >= 10:
                    bot_new = bot_old[:]
                    bot_new[0], bot_new[3] = ver_key_one, ver_key_two
                    grid_width = bot_new[3] - bot_new[0]
                    grid_depth = bot_new[5] - bot_new[2]
                    grid_count = int(grid_depth / grid_width + 0.5)
                    if grid_count >= 3:
                        grid_ver_1 = grid_width
                        grid_ver_2 = grid_width
                        if ver_key_one in ver_key_high:
                            grid_ver_1 = ver_key_high[ver_key_one]
                        if ver_key_two in ver_key_high:
                            grid_ver_2 = ver_key_high[ver_key_two]
                        grid_count = min(int(grid_depth / grid_width + 0.5),
                                         int(grid_depth / grid_ver_1 + 0.5),
                                         int(grid_depth / grid_ver_2 + 0.5))
                    if grid_count >= 3 and grid_width < 20 and len(ver_key_list) >= 4 and max(grid_ver_1, grid_ver_2) < 15:
                        for grid_index in range(grid_count):
                            bot_new_grid = bot_new[:]
                            bot_new_grid[2] = bot_new[2] + (grid_index + 0) * grid_depth / grid_count + 1
                            bot_new_grid[5] = bot_new[2] + (grid_index + 1) * grid_depth / grid_count - 1
                            bot_set_new.append(bot_new_grid)
                    else:
                        bot_new[0], bot_new[3] = ver_key_one, ver_key_two
                        if len(ver_key_list) >= 3:
                            bot_new[0], bot_new[3] = ver_key_one + 1, ver_key_two - 1
                        bot_new[5] = bot_new[2] + bot_depth
                        if len(ver_key_list) == 3 and grid_depth / 2 > grid_width > 20:
                            bot_new[5] = bot_new[2] + grid_depth / 2
                        bot_set_new.append(bot_new)
                if ver_key_idx + 1 < len(ver_key_list) - 1:
                    grid_width = int((ver_key_two - ver_key_one) / 5) * 5
                    if 5 < grid_width < 50:
                        if grid_width not in grid_dict:
                            grid_dict[grid_width] = 1
                        else:
                            grid_dict[grid_width] += 1
        if len(bot_set_new) > 0:
            dict_bot[bot_key] = bot_set_new
    # 间隔 水平
    if len(grid_dict) > 1:
        grid_step = 5
        for grid_key, grid_cnt in grid_dict.items():
            if grid_cnt >= 2 and grid_key > grid_step:
                grid_step = grid_key
    if grid_step <= 5:
        grid_step = 50
    # 切分 靠墙
    for bak_key, bak_val in dict_bak.items():
        if 'sofa' in type:
            break
        bak_set = dict_bak[bak_key]
        bak_set_new = []
        for bak_old in bak_set:
            bak_width = bak_old[3] - bak_old[0]
            bak_height = bak_old[4] - bak_old[1]
            # 检查
            ver_key_list, ver_top_dict, ver_bot_dict = [], {}, {}
            for ver_key, ver_val in dict_ver.items():
                if ver_key <= bak_old[0] + 1 or ver_key >= bak_old[3] - 1:
                    continue
                for ver_one in ver_val:
                    if ver_one[2] >= bak_old[2] + 20 or ver_one[5] <= bak_old[2] + 1:
                        continue
                    elif ver_one[1] >= bak_old[4] - 1 or ver_one[4] <= bak_old[1] + 1:
                        continue
                    else:
                        if ver_one[1] > (bak_old[1] + bak_old[4]) / 2:
                            ver_top_dict[ver_key] = ver_one[1]
                        elif ver_one[4] < (bak_old[1] + bak_old[4]) / 2:
                            ver_bot_dict[ver_key] = ver_one[4]
                        else:
                            ver_key_list.append(ver_key)
                        break
            ver_key_list.sort()
            ver_key_list.insert(0, bak_old[0])
            ver_key_list.append(bak_old[3])
            # 切分
            for ver_key_idx in range(len(ver_key_list)):
                if ver_key_idx + 1 >= len(ver_key_list):
                    break
                ver_key_one = ver_key_list[ver_key_idx + 0]
                ver_key_two = ver_key_list[ver_key_idx + 1]
                if ver_key_two - ver_key_one >= 10:
                    bak_new = bak_old[:]
                    ver_bot, ver_top = bak_new[1], bak_new[4]
                    for top_key, top_val in ver_top_dict.items():
                        if ver_key_one <= top_key <= ver_key_two:
                            ver_top = min(ver_top, top_val)
                    for bot_key, bot_val in ver_bot_dict.items():
                        if ver_key_one <= bot_key <= ver_key_two:
                            ver_bot = max(ver_bot, bot_val)
                    bak_new[0], bak_new[3] = ver_key_one, ver_key_two
                    if len(ver_key_list) >= 3:
                        bak_new[0], bak_new[3] = ver_key_one + 1, ver_key_two - 1
                    bak_new[1], bak_new[4] = ver_bot, ver_top
                    bak_set_new.append(bak_new)

        if len(bak_set_new) > 0:
            dict_bak[bak_key] = bak_set_new

    # 排序 水平
    bot_list = list(dict_bot.keys())
    bot_list.sort()
    # 排序 靠墙
    bak_list = list(dict_bak.keys())
    bak_list.sort()

    # 遍历 水平
    bot_max_key, bot_max_one = 0, []
    for bot_key in bot_list:
        # 判断
        if bot_key <= 0:
            continue
        if bot_key >= size[1] - 5 and size[1] > 150:
            continue
        if bot_key >= size[1] - 5 and size[1] > 120 and size[2] > 50 and 'cabinet' in type:
            continue
        # 遍历
        bot_set = dict_bot[bot_key]
        for bot_one in bot_set:
            bot_one[6] = 50
            size_one = [bot_one[3] - bot_one[0], bot_one[1], bot_one[5] - bot_one[2]]
            # 判断
            for old_key in bot_list:
                if old_key <= bot_key:
                    continue
                old_set = dict_bot[old_key]
                for old_one in old_set:
                    # 错开
                    if old_one[0] > bot_one[3] - 1:
                        continue
                    elif old_one[2] > bot_one[5] - 1:
                        continue
                    elif old_one[3] < bot_one[0] + 1:
                        continue
                    elif old_one[5] < bot_one[2] + 1:
                        continue
                    # 尺寸
                    if 'sofa' in type:
                        pass
                    elif old_one[3] - old_one[0] < (bot_one[3] - bot_one[0]) * 0.25:
                        continue
                    elif old_one[5] - old_one[2] < (bot_one[5] - bot_one[2]) * 0.25:
                        continue
                    # 删除
                    if old_key - bot_key < 30 and 'sofa' in type:
                        if old_one[3] < (bot_one[0] + bot_one[3]) / 2:
                            bot_one[0] = old_one[3]
                        elif old_one[0] > (bot_one[0] + bot_one[3]) / 2:
                            bot_one[3] = old_one[0]
                        elif old_one[5] < (bot_one[2] + bot_one[5]) / 2:
                            bot_one[2] = old_one[5]
                        elif old_one[2] > (bot_one[2] + bot_one[5]) / 2:
                            bot_one[5] = old_one[2]
                        else:
                            bot_one[6] = 0
                            if abs(old_key - bot_key) <= 5:
                                if old_one[0] - 10 < bot_one[0] < bot_one[3] < old_one[3] + 10:
                                    if bot_one[2] < old_one[2] - 5:
                                        old_one[2] = min(old_one[2], bot_one[2])
                            break
                    else:
                        # 裁剪
                        top_one = old_one[:]
                        top_width, top_depth = top_one[3] - top_one[0], top_one[5] - top_one[2]
                        bot_width, bot_depth = bot_one[3] - bot_one[0], bot_one[5] - bot_one[2]
                        # 扩展
                        if old_key - bot_key > 50:
                            pass
                        elif old_key - bot_key > 20 and 'cabinet' in type:
                            bot_one[6] = min(bot_one[6], old_key - bot_key - 1)
                        elif old_key - bot_key > 10 and bot_key < 50:
                            bot_one[6] = min(bot_one[6], old_key - bot_key - 1)
                        elif top_one[3] < (bot_one[0] + bot_one[3]) / 2 and top_depth > bot_depth * 0.25:
                            bot_one[0] = max(top_one[3], bot_one[0])
                        elif top_one[0] > (bot_one[0] + bot_one[3]) / 2 and top_depth > bot_depth * 0.25:
                            bot_one[3] = min(top_one[0], bot_one[3])
                        elif top_one[5] < (bot_one[2] + bot_one[5]) / 2 and top_width > bot_width * 0.25:
                            bot_one[2] = max(top_one[5], bot_one[2])
                        elif top_one[2] > (bot_one[2] + bot_one[5]) / 2 and top_width > bot_width * 0.25:
                            bot_one[5] = min(top_one[2], bot_one[5])
                        # 横向
                        elif bot_one[0] - 5 <= top_one[0] and bot_one[3] + 5 >= top_one[3] \
                                and bot_width > min(top_width + 20, top_width * 2):
                            if bot_one[3] - top_one[3] >= top_one[0] - bot_one[0]:
                                bot_one[0] = max(top_one[3], bot_one[0])
                            else:
                                bot_one[3] = min(top_one[0], bot_one[3])
                        # 纵向
                        elif bot_one[2] - 5 <= top_one[2] and bot_one[5] + 5 >= top_one[5] \
                                and bot_depth > min(top_depth + 20, top_depth * 2):
                            if bot_one[5] - top_one[5] >= top_one[2] - bot_one[2]:
                                bot_one[2] = max(top_one[5], bot_one[2])
                            else:
                                bot_one[5] = min(top_one[2], bot_one[5])

                        # 压缩
                        else:
                            bot_one[6] = old_key - bot_key - 1
                if bot_one[6] < 50:
                    break
            if bot_one[6] <= 1:
                continue
        # 添加
        bot_new = []
        for bot_one in bot_set:
            # 高度
            if bot_one[6] < 5:
                continue
            size_one = [bot_one[3] - bot_one[0], bot_one[1], bot_one[5] - bot_one[2]]
            center_one = [(bot_one[3] + bot_one[0]) / 2, bot_one[1], (bot_one[5] + bot_one[2]) / 2]
            # 删除
            if 'sofa' in type:
                if len(bot_max_one) <= 0:
                    bot_max_key = bot_key
                    bot_max_one = bot_one
                else:
                    len_max = bot_max_one[3] - bot_max_one[0]
                    len_one = bot_one[3] - bot_one[0]
                    if bot_max_key < bot_key and len_max > 100:
                        if bot_max_one[5] - bot_max_one[2] > bot_one[5] - bot_one[2]:
                            if bot_max_one[0] < (bot_one[0] + bot_one[3]) / 2 < bot_max_one[3]:
                                continue
                        if bot_max_one[3] - bot_max_one[0] > min((bot_one[3] - bot_one[0]) * 0.5, 100) \
                                and bot_max_one[5] <= bot_one[2] + 5:
                            if bot_one[5] - (bot_max_one[5] + 30) > 20:
                                bot_one[2] = bot_max_one[5] + 30
                            elif bot_one[5] - (bot_max_one[5] + 20) > 20:
                                bot_one[2] = bot_max_one[5] + 20
                            elif bot_one[5] - (bot_max_one[5] + 10) > 20:
                                bot_one[2] = bot_max_one[5] + 10
                    if len_max < len_one:
                        bot_max_key = bot_key
                        bot_max_one = bot_one
                bot_new.append(bot_one)
            # 裁剪
            elif 'table' in type or 'cabinet' in type:
                if size_one[0] >= min(size[0] * 0.8, 100) and size_one[2] >= min(size[2] * 0.8, 100):
                    if abs(size_one[0] - size_one[2]) < min(size_one[0], size_one[2]) * 0.2:
                        if abs(size_one[1] - size[1]) < 10:
                            if size_one[1] > 50:
                                bot_one[0] = center_one[0] - max(size_one[0] * 0.4, size_one[0] * 0.5 - 10)
                                bot_one[2] = center_one[2] - max(size_one[2] * 0.4, size_one[2] * 0.5 - 10)
                                bot_one[3] = center_one[0] + max(size_one[0] * 0.4, size_one[0] * 0.5 - 10)
                                bot_one[5] = center_one[2] + max(size_one[2] * 0.4, size_one[2] * 0.5 - 10)
                bot_new.append(bot_one)
            # 添加
            else:
                bot_new.append(bot_one)
        # 添加
        if len(bot_new) > 0:
            if abs(bot_key - int(size[1])) <= 2:
                for bot_one in bot_new:
                    bot_one[1], bot_one[4] = size[1] + 0.05, size[1] + 0.05
            decor_bot[bot_key] = bot_new

    # 遍历 靠墙
    bak_max_key, bak_max_set = -size[2] / 2, []
    for bak_key in bak_list:
        # 判断
        if bak_key >= 0 + size[2] / 2 - 5 and 'cabinet' in type:
            bak_set = dict_bak[bak_key]
            decor_frt[bak_key] = bak_set
            continue
        if bak_key >= 0 + size[2] / 2 - 15 and 'cabinet' in type:
            continue
        if bak_key <= 0 - size[2] / 2 + 5 and 'sofa' in type:
            continue
        if bak_key >= 0 - size[2] / 2 + 50 and 'sofa' in type:
            continue
        if 'sofa' in type:
            bak_set = dict_bak[bak_key]
            for bak_one in bak_set:
                bak_one[6] = size[2] / 2 - bak_key
                if bak_one[4] <= size[1] / 2:
                    continue
                elif bak_one[4] - bak_one[1] < 5:
                    continue
                elif bak_one[0] >= size[0] - 10:
                    continue
                elif bak_one[3] <= 10:
                    continue
                else:
                    break
            if len(bak_max_set) <= 0:
                bak_max_key = bak_key
                bak_max_set = bak_set
            else:
                if bak_key > bak_max_key:
                    bak_max_key = bak_key
                    bak_max_set = bak_set
            continue
        # 遍历
        bak_set = dict_bak[bak_key]
        for bak_one in bak_set:
            bak_one[6] = size[2] / 2 - bak_key
            size_one = [bak_one[3] - bak_one[0], bak_one[4] - bak_one[1], bak_one[6]]
            for bot_key, bot_val in dict_bot.items():
                for bot_old in bot_val:
                    if bot_old[0] >= bak_one[3] - 5:
                        continue
                    elif bot_old[3] <= bak_one[0] + 5:
                        continue
                    elif bot_old[1] <= bak_one[1] or bot_old[4] >= bak_one[4]:
                        continue
                    elif bot_old[0] <= bak_one[0] <= bot_old[3] <= bak_one[0] + size_one[0] / 2:
                        if abs(bot_key - bak_one[1]) <= 10:
                            bak_one[1] = max(bot_key, bak_one[1])
                        elif abs(bot_key - bak_one[4]) <= 10:
                            bak_one[4] = min(bot_key, bak_one[4])
                        else:
                            bak_one[0] = bot_old[3]
                    elif bot_old[3] >= bak_one[3] >= bot_old[0] >= bak_one[3] - size_one[0] / 2:
                        if abs(bot_key - bak_one[1]) <= 10:
                            bak_one[1] = max(bot_key, bak_one[1])
                        elif abs(bot_key - bak_one[4]) <= 10:
                            bak_one[4] = min(bot_key, bak_one[4])
                        else:
                            bak_one[3] = bot_old[0]
                    else:
                        if abs(bot_key - bak_one[1]) <= abs(bot_key - bak_one[4]):
                            bak_one[1] = max(bot_key, bak_one[1])
                        else:
                            bak_one[4] = min(bot_key, bak_one[4])
            # 判断
            for old_key in bak_list:
                if old_key <= bak_key:
                    continue
                old_set = dict_bak[old_key]
                for old_one in old_set:
                    # 错开
                    if old_one[0] > bak_one[3] - 1:
                        continue
                    elif old_one[1] > bak_one[4] - 1:
                        continue
                    elif old_one[3] < bak_one[0] + 1:
                        continue
                    elif old_one[4] < bak_one[1] + 1:
                        continue
                    # 扩展
                    if old_key - bak_key > 50:
                        pass
                    elif old_one[0] > bak_one[3] - 20:
                        bak_one[3] = old_one[0]
                    elif old_one[3] < bak_one[0] + 20:
                        bak_one[0] = old_one[3]
                    # 压缩
                    else:
                        bak_one[6] = min(bak_one[6], old_key - bak_key - 1)
        # 添加
        bak_new = []
        for bak_one in bak_set:
            # 高度
            if bak_one[1] > 150:
                continue
            elif bak_one[4] - bak_one[1] < 75:
                continue
            # 宽度
            elif bak_one[3] - bak_one[0] < 20:
                continue
            # 深度
            elif bak_one[6] < 5:
                continue
            bak_new.append(bak_one)
        # 添加
        if len(bak_new) > 0:
            decor_bak[bak_key] = bak_new
    if len(bak_max_set) > 0 and 'sofa' in type:
        decor_bak[bak_max_key] = bak_max_set

    # 排错 水平
    if 'sofa' in type:
        bot_dump = []
        for bot_key, bot_set in decor_bot.items():
            if bot_key == bot_max_key:
                bot_len = len(bot_set)
                for bot_idx in range(bot_len - 1, 0, -1):
                    bot_one = bot_set[bot_idx - 0]
                    bot_pre = bot_set[bot_idx - 1]
                    if bot_pre[0] <= bot_one[0] + 10 and bot_one[3] - 10 < bot_pre[3]:
                        if bot_pre[2] < bot_one[2] < bot_pre[5]:
                            bot_set.pop(bot_idx)
                        if bot_pre[2] < bot_one[5] < bot_pre[5]:
                            bot_set.pop(bot_idx)
            else:
                bot_len = len(bot_set)
                for bot_idx in range(bot_len - 1, -1, -1):
                    bot_one = bot_set[bot_idx]
                    if bot_one[5] - bot_one[2] < (bot_max_one[5] - bot_max_one[2]) * 0.75:
                        bot_set.pop(bot_idx)
                    elif bot_one[3] - bot_one[0] < 30 and bot_key > bot_max_key:
                        bot_set.pop(bot_idx)
                if len(bot_set) <= 0:
                    bot_dump.append(bot_key)
        for bot_key in bot_dump:
            decor_bot.pop(bot_key)
        for bot_key, bot_set in decor_bot.items():
            for bot_one in bot_set:
                bot_one[2] = max(bak_max_key, bot_one[2])
    elif 'cabinet' in type and size[2] > size[0] * 0.4 and size[2] > 40:
        bot_list = list(decor_bot.keys())
        bot_list.sort()
        bot_dump = []
        for bot_idx, bot_key in enumerate(bot_list):
            if bot_key < 25 or bot_key > 100:
                continue
            if bot_idx + 1 >= len(bot_list):
                continue
            top_key = bot_list[bot_idx + 1]
            bot_set = decor_bot[bot_key]
            top_set = decor_bot[top_key]
            if len(bot_set) >= 3:
                continue
            if top_key - bot_key > 30:
                continue
            bot_one = bot_set[0]
            top_one = top_set[0]
            if bot_one[5] - bot_one[2] < 20 and bot_one[2] > top_one[5]:
                bot_dump.append(bot_key)
                continue
        for bot_key in bot_dump:
            decor_bot.pop(bot_key)

    # 返回
    return decor_bot, decor_bak, decor_frt, ratio


def glm_shape_obj_by_path(obj_path, obj_type=''):
    model = glm_read_obj(obj_path)
    decor_bot, decor_bak, decor_frt, ratio = glm_shape_obj(model, obj_type)
    return model, decor_bot, decor_bak, decor_frt, ratio


if __name__ == '__main__':
    from Furniture.glm_render import *
    # 实验数据
    obj_id, obj_type = '7f731dba-f177-4f09-ab8c-35570e893b83', 'cabinet'
    # 实验数据
    obj_path = os.path.join(DATA_DIR_FURNITURE_OBJ, obj_id + '.obj')
    # 读取模型
    model, decor_bot, decor_bak, decor_frt, ratio = glm_shape_obj_by_path(obj_path, obj_type)
    print(decor_bot)
    print(decor_bak)
    print(decor_frt)
    # 显示模型
    if model:
        model_set = [model]
        glm_normal_vertex(model_set, decor_bot, decor_bak, decor_frt, ratio=ratio)
        glm_render_initial()
        glm_render_reshape()
        glm_render_display(model_set, decor_bot, decor_bak, decor_frt, rotate=True)
    pass
