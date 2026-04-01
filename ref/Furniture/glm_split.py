# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2021-07-07
@Description:

"""

import json
import requests
from Furniture.glm_interface import *


def glm_split_mesh(model, type=''):
    decor_bot = {}
    # 范围
    size = [model.bbox.max[0] - model.bbox.min[0],
            model.bbox.max[1] - model.bbox.min[1],
            model.bbox.max[2] - model.bbox.min[2]]
    h_min, h_max = 0, size[1]
    w_min, w_max = 0 - size[0] * 0.5, 0 + size[0] * 0.5
    d_min, d_max = 0 - size[2] * 0.5, 0 + size[2] * 0.5
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
    h_dlt, w_dlt, d_dlt, s_min = 0, 5, 5, 10
    edge_min = min(5, size[0] / 20, size[2] / 20)
    norm_min = 0.90
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
            if min(d0, d1, d2) < edge_min:
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
            dict_now = dict_bak
            d = int(max(v0[2], v1[2], v2[2]))
            if abs(d - d_min) < 1:
                continue
            if abs(d - d_max) < 10:
                continue
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
                    elif face_one[5] - side_one[5] > 20 and side_one[3] + w_dlt > face_one[3] and \
                            face_one[3] < (side_one[0] + side_one[3]) / 2:
                        face_one[2] = max(face_one[2], side_one[5] + w_dlt + 1)
                        break
                    # 0 + 3
                    elif side_one[5] - face_one[5] > 20 and side_one[3] + w_dlt > face_one[3] and \
                            side_one[0] > (face_one[0] + face_one[3]) / 2:
                        side_one[2] = max(side_one[2], face_one[5] + w_dlt + 1)
                        continue
                    # 1 + 2
                    elif face_one[2] - side_one[2] < -40 and side_one[3] + w_dlt > face_one[3] and \
                            face_one[3] < (side_one[0] + side_one[3]) / 2:
                        face_one[5] = min(face_one[5], side_one[2] - w_dlt - 1)
                        break
                    # 2 + 3
                    elif side_one[2] - face_one[2] < -20 and side_one[3] + w_dlt > face_one[3] and \
                            side_one[0] > (face_one[0] + face_one[3]) / 2:
                        side_one[5] = min(side_one[5], face_one[2] - w_dlt - 1)
                        continue
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
                    if side_one[0] > face_one[3] + w_dlt:
                        break
                    elif side_one[1] > face_one[4] + w_dlt:
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
                if max(dlt_x, dlt_y) < s_min or min(dlt_x, dlt_y) < 2:
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

    # 排序 水平
    bot_list = list(dict_bot.keys())
    bot_list.sort()
    # 排序 竖直
    ver_list = list(dict_ver.keys())
    ver_list.sort()
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
                        bot_width, top_width = bot_one[3] - bot_one[0], top_one[3] - top_one[0]
                        bot_depth, top_depth = bot_one[5] - bot_one[2], top_one[5] - top_one[2]
                        # 扩展
                        if old_key - bot_key > 50:
                            pass
                        elif old_key - bot_key > 20 and 'cabinet' in type:
                            bot_one[6] = min(bot_one[6], old_key - bot_key - 1)
                        elif old_key - bot_key > 10 and bot_key < 50:
                            bot_one[6] = min(bot_one[6], old_key - bot_key - 1)
                        elif top_one[3] < (bot_one[0] + bot_one[3]) / 2 and top_depth > bot_depth * 0.5:
                            bot_one[0] = max(top_one[3], bot_one[0])
                        elif top_one[0] > (bot_one[0] + bot_one[3]) / 2 and top_depth > bot_depth * 0.5:
                            bot_one[3] = min(top_one[0], bot_one[3])
                        elif top_one[5] < (bot_one[2] + bot_one[5]) / 2 and top_width > bot_width * 0.5:
                            bot_one[2] = max(top_one[5], bot_one[2])
                        elif top_one[2] > (bot_one[2] + bot_one[5]) / 2 and top_width > bot_width * 0.5:
                            bot_one[5] = min(top_one[2], bot_one[5])
                        # 纵向
                        elif bot_one[2] - 5 <= top_one[2] and bot_one[5] + 5 >= top_one[5] \
                                and bot_depth > min(top_depth + 20, top_depth * 2):
                            if bot_one[5] - top_one[5] >= top_one[2] - bot_one[2]:
                                bot_one[2] = max(top_one[5], bot_one[2])
                            else:
                                bot_one[5] = min(top_one[2], bot_one[5])
                        # 横向
                        elif bot_one[0] - 5 <= top_one[0] and bot_one[3] + 5 >= top_one[3] \
                                and bot_width > min(top_width + 20, top_width * 2):
                            if bot_one[3] - top_one[3] >= top_one[0] - bot_one[0]:
                                bot_one[0] = max(top_one[3], bot_one[0])
                            else:
                                bot_one[3] = min(top_one[0], bot_one[3])
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

    return decor_bot, ver_list, bak_list


def glm_split_mesh_by_json(mesh_json, mesh_type=''):
    model_set = glm_read_mesh(mesh_json)
    model_min, model_max = [], []
    model_box, model_mid = [0, 0, 0], [0, 0, 0]
    for model_one in model_set:
        # min
        if len(model_min) <= 0:
            model_min = model_one.bbox.min[:]
        else:
            model_min[0] = min(model_one.bbox.min[0], model_min[0])
            model_min[1] = min(model_one.bbox.min[1], model_min[1])
            model_min[2] = min(model_one.bbox.min[2], model_min[2])
        # max
        if len(model_max) <= 0:
            model_max = model_one.bbox.max[:]
        else:
            model_max[0] = max(model_one.bbox.max[0], model_max[0])
            model_max[1] = max(model_one.bbox.max[1], model_max[1])
            model_max[2] = max(model_one.bbox.max[2], model_max[2])
    if len(model_min) > 0 and len(model_max) > 0:
        model_box[0] = (model_max[0] - model_min[0]) * 100
        model_box[1] = (model_max[1] - model_min[1]) * 100
        model_box[2] = (model_max[2] - model_min[2]) * 100
        model_mid[0] = (model_max[0] + model_min[0]) * 100 / 2
        model_mid[1] = (model_max[1] + model_min[1]) * 100 / 2
        model_mid[2] = (model_max[2] + model_min[2]) * 100 / 2
    else:
        return model_set, [mesh_json]

    # decor
    bot_side_0, bot_side_1, bot_side_2, bot_side_3 = [], [], [], []
    bot_grid_0, bot_grid_1, bot_grid_2, bot_grid_3 = [], [], [], []
    for model_one in model_set:
        # size
        size = [model_one.bbox.max[0] - model_one.bbox.min[0],
                model_one.bbox.max[1] - model_one.bbox.min[1],
                model_one.bbox.max[2] - model_one.bbox.min[2]]
        if min(size[0], size[2]) < 0.1:
            continue
        # face
        bot_dict, ver_list, bak_list = glm_split_mesh(model_one, mesh_type)
        for bot_key, bot_set in bot_dict.items():
            for bot_val in bot_set:
                dis_x, dis_z = bot_val[3] - bot_val[0], bot_val[5] - bot_val[0]
                if bot_val[5] < model_mid[2]:
                    if bot_val[0] < model_mid[0] < bot_val[3]:
                        if len(bot_side_0) <= 0:
                            bot_side_0 = bot_val
                        elif dis_x > dis_z and dis_x > bot_side_3[3] - bot_side_3[0]:
                            bot_side_0 = bot_val
                elif bot_val[3] < model_mid[0]:
                    if bot_val[2] < model_mid[2] < bot_val[5]:
                        if len(bot_side_1) <= 0:
                            bot_side_1 = bot_val
                        elif dis_z > dis_x and dis_z > bot_side_1[5] - bot_side_1[2]:
                            bot_side_1 = bot_val
                elif bot_val[2] > model_mid[2]:
                    if bot_val[0] < model_mid[0] < bot_val[3]:
                        if len(bot_side_2) <= 0:
                            bot_side_2 = bot_val
                        elif dis_x > dis_z and dis_x > bot_side_2[3] - bot_side_2[0]:
                            bot_side_2 = bot_val
                elif bot_val[0] > model_mid[0]:
                    if bot_val[2] < model_mid[2] < bot_val[5]:
                        if len(bot_side_3) <= 0:
                            bot_side_3 = bot_val
                        elif dis_z > dis_x and dis_z > bot_side_3[5] - bot_side_3[2]:
                            bot_side_3 = bot_val
        # back
        if len(bot_side_0) > 0:
            if bot_side_0[3] - bot_side_0[0] > model_box[0] * 0.5 and bot_side_0[5] - bot_side_0[2] > 5:
                if len(bot_grid_0) < len(ver_list):
                    bot_grid_0 = ver_list
            else:
                bot_side_0 = []
        # left
        if len(bot_side_1) > 0:
            if bot_side_1[5] - bot_side_1[2] > model_box[2] * 0.5 and bot_side_1[3] - bot_side_1[0] > 5:
                if len(bot_grid_1) < len(bak_list):
                    bot_grid_1 = bak_list
            else:
                bot_side_1 = []
        # front
        if len(bot_side_2) > 0:
            if bot_side_2[3] - bot_side_2[0] > model_box[0] * 0.5 and bot_side_2[5] - bot_side_2[2] > 5:
                if len(bot_grid_2) < len(ver_list):
                    bot_grid_2 = ver_list
            else:
                bot_side_2 = []

        # right
        if len(bot_side_3) > 0:
            if bot_side_3[5] - bot_side_3[2] > model_box[2] * 0.5 and bot_side_3[3] - bot_side_3[0] > 5:
                if len(bot_grid_3) < len(bak_list):
                    bot_grid_3 = bak_list
            else:
                bot_side_3 = []

    # group side
    group_set = []
    min_x, max_x = model_min[0] * 100, model_max[0] * 100
    min_y, max_y = model_min[1] * 100, model_max[1] * 100
    min_z, max_z = model_min[2] * 100, model_max[2] * 100
    if len(bot_side_0) > 0:
        bbox, unit, grid = bot_side_0[:], [], bot_grid_0
        if len(bot_side_1) <= 0 or bot_side_1[2] >= bbox[5] - 5:
            bbox[0] = min_x
        if len(bot_side_3) <= 0 or bot_side_3[2] >= bbox[5] - 5:
            bbox[3] = max_x
        group_one = {'bbox': bbox, 'mesh': unit, 'edge': 0, 'form': [0, 0, 0], 'grid': grid}
        group_set.append(group_one)
    if len(bot_side_1) > 0:
        bbox, unit, grid = bot_side_1[:], [], bot_grid_1[:]
        if len(bot_side_0) <= 0 or bot_side_0[0] >= bbox[3] - 5:
            bbox[2] = min_z
        if len(bot_side_2) <= 0 or bot_side_2[0] >= bbox[3] - 5:
            bbox[5] = max_z
        group_one = {'bbox': bbox, 'mesh': unit, 'edge': 1, 'form': [0, 0, 0], 'grid': grid}
        group_set.append(group_one)
    if len(bot_side_2) > 0:
        bbox, unit, grid = bot_side_2[:], [], bot_grid_2[:]
        if len(bot_side_1) <= 0 or bot_side_1[5] <= bbox[2] + 5:
            bbox[0] = min_x
        if len(bot_side_3) <= 0 or bot_side_3[5] <= bbox[2] + 5:
            bbox[3] = max_x
        group_one = {'bbox': bbox, 'mesh': unit, 'edge': 2, 'form': [0, 0, 0], 'grid': grid}
        group_set.append(group_one)
    if len(bot_side_3) > 0:
        bbox, unit, grid = bot_side_3[:], [], bot_grid_3[:]
        if len(bot_side_0) <= 0 or bot_side_0[3] <= bbox[0] + 5:
            bbox[2] = min_z
        if len(bot_side_2) <= 0 or bot_side_2[3] <= bbox[0] + 5:
            bbox[5] = max_z
        group_one = {'bbox': bbox, 'mesh': unit, 'edge': 3, 'form': [0, 0, 0], 'grid': grid}
        group_set.append(group_one)
    # group mid
    bbox = [min_x, min_y, min_z, max_x, max_y, max_z, max_y - min_y]
    group_mid = {'bbox': bbox, 'mesh': [], 'edge': 4, 'form': [0, 0, 0], 'grid': []}
    group_set.append(group_mid)

    # split
    for mesh_idx, mesh_val in enumerate(mesh_json):
        # 读取
        xyz, face, normal, uv = [], [], [], []
        if 'xyz' in mesh_val:
            xyz = mesh_val['xyz']
        if 'face' in mesh_val:
            face = mesh_val['face']
        mesh_val['edge'] = 4
        mesh_val['form'] = [0, 0, 0]
        mesh_val['grid'] = []
        # 包含
        for group_idx, group_val in enumerate(group_set):
            group_val['part'] = []
        # 索引
        face_cnt = int(len(face) / 3)
        for idx in range(face_cnt):
            idx_1, idx_2, idx_3 = face[idx * 3 + 0], face[idx * 3 + 1], face[idx * 3 + 2]
            x1, x2, x3 = xyz[idx_1 * 3 + 0] * 100, xyz[idx_2 * 3 + 0] * 100, xyz[idx_3 * 3 + 0] * 100
            y1, y2, y3 = xyz[idx_1 * 3 + 1] * 100, xyz[idx_2 * 3 + 1] * 100, xyz[idx_3 * 3 + 1] * 100
            z1, z2, z3 = xyz[idx_1 * 3 + 2] * 100, xyz[idx_2 * 3 + 2] * 100, xyz[idx_3 * 3 + 2] * 100
            min_x, max_x = min(x1, x2, x3), max(x1, x2, x3)
            min_z, max_z = min(z1, z2, z3), max(z1, z2, z3)
            group_find = False
            for group_idx, group_val in enumerate(group_set):
                bbox, part = group_val['bbox'], group_val['part']
                if group_idx == len(group_set) - 1:
                    if group_find:
                        break
                    elif max(y1, y2, y3) <= 10:
                        break
                    else:
                        pass
                if bbox[0] - 1 <= min_x <= max_x <= bbox[3] + 1 and bbox[2] - 1 <= min_z <= max_z <= bbox[5] + 1:
                    part.append(idx_1)
                    part.append(idx_2)
                    part.append(idx_3)
                    group_find = True
        # 包含
        face_add = []
        for group_idx, group_val in enumerate(group_set):
            face_set = group_val['part']
            if len(face_set) >= 3 * 4:
                if group_idx == len(group_set) - 1:
                    face_set += face_add
                mesh_new = mesh_val.copy()
                mesh_new['face'] = face_set[:]
                mesh_new['edge'] = group_val['edge']
                mesh_new['form'] = group_val['form'][:]
                mesh_new['grid'] = group_val['grid'][:]
                group_val['mesh'].append(mesh_new)
            else:
                face_add += face_set
            group_val['part'] = []
    # check
    count_edge, count_mesh = [0, 0, 0, 0], [0, 0, 0, 0]
    for group_idx, group_val in enumerate(group_set):
        group_edge, group_mesh = group_val['edge'], group_val['mesh']
        if 0 <= group_edge < len(count_edge):
            count_edge[group_edge] = 1
        if 0 <= group_edge < len(count_mesh) and len(group_mesh) > 0:
            count_mesh[group_edge] = 1
    if count_mesh[0] + count_mesh[1] + count_mesh[2] + count_mesh[3] == 1:
        group_mid['mesh'] = mesh_json
        group_set = [group_mid]
    for edge_idx in range(4):
        group_find, group_form = {}, [0, 0, 0]
        if count_mesh[edge_idx] == 1:
            idx_left = (edge_idx + 1 + len(count_edge)) % len(count_edge)
            idx_right = (edge_idx - 1 + len(count_edge)) % len(count_edge)
            if count_edge[idx_left] >= 1:
                group_form[0] = 2
            if count_edge[idx_right] >= 1:
                group_form[2] = 2
            if len(group_set) == 1:
                group_find = group_set[0]
            else:
                for group_one in group_set:
                    if group_one['edge'] == edge_idx:
                        group_find = group_one
                        break
        if len(group_find) > 0:
            group_find['edge'] = edge_idx
            group_find['form'] = group_form
            mesh_set = group_find['mesh']
            for mesh_one in mesh_set:
                mesh_one['edge'] = edge_idx
                mesh_one['form'] = group_form
    split_set = []
    for group_idx, group_val in enumerate(group_set):
        mesh_set = group_val['mesh']
        if len(mesh_set) > 0:
            split_set.append(mesh_set)
    return model_set, split_set


if __name__ == '__main__':
    from Furniture.data_oss import *
    from Furniture.glm_render import *
    # 实验数据
    mesh_key = 'customized_data/520b0072-72cc-4774-85d9-2404d474539e_36893.json'
    mesh_key = 'customized_data/520b0072-72cc-4774-85d9-2404d474539e_45097.json'
    mesh_json = oss_download_json(mesh_key, 'ihome-alg-sample-data')
    # 读取造型 & 分割造型
    model_set, split_set = glm_split_mesh_by_json(mesh_json, '')

    # 显示模型
    if len(split_set) > 0:
        model_set = glm_read_mesh(split_set[-1])
        glm_normal_vertex(model_set)
        glm_render_initial()
        glm_render_reshape()
        glm_render_display(model_set, rotate=False)
    pass
