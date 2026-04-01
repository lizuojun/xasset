# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2020-08-12
@Description: 功能区域布局

"""

from Furniture.furniture_group import *
from LayoutByRule.house_calculator import *


# 功能区域摆放
# from LayoutByRule.temp.visual_test import test_visual_house_region_data


# 根据现在位置 目标区域大小直接更新regulation
def group_regulation_update(zone_one, group_one):
    zone_pos, zone_ang, zone_size = zone_one['position'], rot_to_ang(zone_one['rotation']), zone_one["size"]
    z_size = [zone_size[0], zone_size[2]]

    group_pos, group_ang, group_size = group_one["position"], rot_to_ang(group_one['rotation']), group_one["size"]
    g_size = [group_size[0], group_size[2]]

    group_to_zone_pos = [group_pos[0] - zone_pos[0], group_pos[2] - zone_pos[2]]
    group_to_zone_pos = [math.cos(-zone_ang) * group_to_zone_pos[0] + math.sin(-zone_ang) * group_to_zone_pos[1],
                         -math.sin(-zone_ang) * group_to_zone_pos[0] + math.cos(-zone_ang) * group_to_zone_pos[1]]
    offset_3 = (0.0 + z_size[0]/2.) - (group_to_zone_pos[0] + g_size[0]/2.)
    offset_1 = (group_to_zone_pos[0] - g_size[0] / 2.) - (0.0 - z_size[0] / 2.)

    offset_2 = (0.0 + z_size[1] / 2.) - (group_to_zone_pos[1] + g_size[1] / 2.)
    offset_0 = (group_to_zone_pos[1] - g_size[1] / 2.) - (0.0 - z_size[1] / 2.)

    if offset_1 > 0:
        group_one['regulation'][1] = offset_1

    if offset_2 > 0:
        group_one['regulation'][2] = offset_2

    if offset_3 > 0:
        group_one['regulation'][3] = offset_3

    if group_one["type"] in ["Armoire", "Bed", "Media"]:
        group_one['regulation'] = [offset_0, offset_1, offset_2, offset_3]

    if group_one["type"] in ["Meeting"] and offset_2 < -0.5:
        group_one['regulation'][2] = offset_2


def room_rect_layout_zone(line_list, zone_list, group_main, group_rest, room_type='', room_area=10,
                          door_pt_entry=[], door_pt_cook=[], door_pt_bath=[], door_pt_wear=[], door_pt_open=[]):
    # 组合检查
    group_result = []
    if len(group_main) <= 0 and len(group_rest) < 0:
        return group_result
    group_sort, group_back, group_pair, types_pair = [], [], [], []

    group_main_type = {}
    for group_one in group_main:
        group_main_type[group_one['type']] = []
    group_rest_type = {}
    for group_one in group_rest:
        group_rest_type[group_one['type']] = []

    for group_one in group_main:
        group_type = group_one['type']
    for group_one in group_main:
        group_sort.append(group_one)
    for group_one in group_rest:
        group_sort.append(group_one)

    # 区域参数
    for zone_idx, zone_one in enumerate(zone_list):
        edge_idx, line_idx, unit_rat = compute_zone_rely(zone_one, line_list)
        if len(unit_rat) >= 2:
            if abs(unit_rat[0] - 0) < 0.01:
                unit_rat[0] = 0
            elif abs(unit_rat[1] - 1) < 0.05:
                unit_rat[1] = 1
        zone_one['edge_idx'], zone_one['line_idx'], zone_one['unit_rat'] = edge_idx, line_idx, unit_rat

    # 组合布局
    line_used, line_face, zone_used = {}, {}, {}
    for group_idx, group_one in enumerate(group_sort):
        # 组合信息
        if group_one in group_back and len(line_used) > 0:
            continue
        group_type, group_size = group_one['type'], group_one['size']

        if 'zone' in group_one:
            group_room_type = group_one['zone']
        else:
            group_room_type = ''

        group_width, group_height, group_depth = group_size[0], group_size[1], group_size[2]
        # 最佳参数
        param_best = {
            'index': -1,
            'score': -100,
            'vertical': 0,
            'width': 0,
            'depth': 0,
            'depth_suit': 0,
            'width_rest': 0,
            'depth_rest': 0,
            'ratio': [0, 1],
            'ratio_best': [0, 1],
            'group': []
        }
        # 区域查找
        for zone_idx, zone_one in enumerate(zone_list):
            if zone_idx in zone_used:
                continue
            zone_room_type, zone_type, zone_size = zone_one['zone'], zone_one['type'], zone_one['size']
            edge_idx, line_idx, unit_rat = zone_one['edge_idx'], zone_one['line_idx'], zone_one['unit_rat']
            if group_type == zone_type:
                if group_type == "Cabinet" and group_room_type != zone_room_type:
                    continue

                zone_used[zone_idx] = 1
                suit_width, suit_depth = zone_size[0], zone_size[2]
                suit_ratio, suit_ratio_best = [0, 1], [0, 1]
                # 侧面
                # if edge_idx in [1, 3]:
                #     group_one = spin_exist_group(group_one)
                #     group_type, group_size = group_one['type'], group_one['size']
                #     group_width, group_height, group_depth = group_size[0], group_size[1], group_size[2]
                # 靠墙
                if edge_idx in [0, 1, 2, 3]:
                    line_one = line_list[line_idx]
                    line_width = line_one['width']
                    max_pass, min_pass, mid_pass = 2.0, MIN_GROUP_PASS, 0
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width, group_depth,
                                           unit_rat, [], max_pass, min_pass, mid_pass, line_used)

                    if len(unit_rat) > 0:
                        suit_ratio[0], suit_ratio[1] = unit_rat[0], unit_rat[1]
                        suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                        suit_depth = max(suit_depth, zone_size[2])
                        suit_ratio_best = unit_rat[:]
                        if line_width * (unit_rat[1] - unit_rat[0]) > group_width:
                            suit_ratio_best = unit_rat[:]
                # 悬空 TODO: 扩展比例
                else:
                    suit_ratio = [0, 1]
                # 参数
                param_best['index'] = line_idx
                param_best['score'] = 10
                param_best['vertical'] = 0
                param_best['width'] = group_width
                param_best['depth'] = group_depth
                param_best['depth_suit'] = suit_depth
                param_best['width_rest'] = suit_width - group_width
                param_best['depth_rest'] = suit_depth - group_depth
                param_best['ratio'] = suit_ratio[:]
                param_best['ratio_best'] = suit_ratio_best[:]
                param_best['zone'] = zone_one

                if line_idx >= 0:
                    param_best['width'] = line_list[line_idx]["width"]

                break

        # 参数判断
        index_best = int(param_best['index'])
        if 'zone' not in param_best:
            continue
        # 参数信息
        param_add = param_best.copy()
        param_add['ratio'] = param_best['ratio'][:]
        param_add['ratio_best'] = param_best['ratio_best'][:]
        param_add['zone'] = param_best['zone'].copy()
        group_add = copy_exist_group(group_one)
        param_add['group'].append(group_add)
        if index_best not in line_used:
            line_used[index_best] = []
        line_used[index_best].append(param_add)

        # 成对布局
        if group_idx < len(group_pair):
            max_pass, min_pass = 2.0, 0.6
            if group_type == 'Meeting':
                max_pass, min_pass = min(1.5 + room_area / 50, 3.0), MIN_GROUP_PASS
            elif group_type == 'Bed':
                max_pass, min_pass = min(1.5 + room_area / 50, 3.0), MIN_GROUP_PASS
            compute_zone_pair(param_add, group_pair[group_idx], line_list, line_used, line_face,
                              max_pass, min_pass, room_type, room_area, door_pt_entry)

    # 计算布局
    group_result = []
    for line_idx in line_used.keys():
        # 遍历参数
        param_list = line_used[line_idx]
        for param_idx, param_one in enumerate(param_list):
            # 布局信息
            group_ratio = param_one['ratio']
            line_width = param_one["width"]
            group_width_rest, group_depth_rest = param_one['width_rest'], param_one['depth_rest']
            ratio_pre, ratio_post, ratio_dir = group_ratio[0], group_ratio[1], 0

            # 查找功能区
            group_width = param_one["group"][0]["size"][0]

            # 区域信息
            if 'zone' not in param_one:
                continue

            zone_one = param_one['zone']
            zone_type, zone_size = zone_one['type'], zone_one['size']
            zone_pos, zone_rot, zone_ang = zone_one['position'], zone_one['rotation'], rot_to_ang(
                zone_one['rotation'])
            zone_width, zone_depth = zone_size[0], zone_size[2]
            edge_idx, line_idx, unit_rat = zone_one['edge_idx'], zone_one['line_idx'], zone_one['unit_rat']
            if edge_idx in [0, 1, 2, 3] and line_idx >= 0:
                # 起点终点
                line_one = line_list[line_idx]
                line_width = line_one["width"]
                p1, p2 = line_one["p1"], line_one["p2"]

            else:
                # 悬空放置, 直接使用输入区域的位置与目标尺寸、朝向
                # 起点终点
                line_one = None
                zone_rec = compute_zone_rect(zone_size, zone_pos, zone_rot)
                p1, p2 = None, None

            # 找到对应组合
            group_cnt = 1
            for group_idx in range(group_cnt):
                # 组合信息
                group_one = param_one['group'][group_idx]
                group_type = group_one["type"]
                group_size, group_size_min = group_one['size'], group_one['size_min']
                group_width, group_height, group_depth = group_size[0], group_size[1], group_size[2]

                update_pos = [zone_pos[0], zone_pos[1], zone_pos[2]]

                width_rest_new = 0.0

                # 尺寸对应检查
                if group_type in ["Media", "Work", "Rest"]:
                    # 宽
                    if group_width > zone_width * 1.5:
                        continue
                    if group_depth > zone_depth * 1.5:
                        continue

                # 尺寸对应检查
                if group_type in ["Cabinet"]:
                    if group_width > zone_width * 1.2:
                        continue
                    if group_depth > zone_depth * 1.2:
                        continue

                # 严格后背对齐
                if group_type in ["Meeting", "Bed"]:
                    depth_rest_new = zone_depth / 2. - group_depth / 2.
                    update_pos[0] -= math.sin(zone_ang) * depth_rest_new
                    update_pos[2] -= math.cos(zone_ang) * depth_rest_new

                # 严格靠墙对齐
                elif line_one:
                    mid_ratio = 0.5 * (ratio_pre + ratio_post)
                    old_middle_x = (1 - mid_ratio) * p1[0] + mid_ratio * p2[0]
                    old_middle_y = (1 - mid_ratio) * p1[1] + mid_ratio * p2[1]

                    if edge_idx in [1, 3]:
                        width_rest_new = line_width * (ratio_post - ratio_pre) - group_depth
                        depth_rest_new = zone_width / 2. - group_width / 2.
                    else:
                        depth_rest_new = zone_depth / 2. - group_depth / 2.
                        width_rest_new = line_width * (ratio_post - ratio_pre) - group_width

                    # 尺寸超出后的延墙移动
                    if width_rest_new < - 0.1:
                        if group_type not in ["Media"]:
                            ratio_rest = abs(width_rest_new) / line_width
                            if 1 - ratio_post + ratio_pre > ratio_rest:
                                if line_width * (1 - ratio_post) > 0.3:
                                    max_move_ratio = 0.99 - ratio_post

                                    if max_move_ratio > ratio_rest:
                                        max_move_ratio = ratio_rest

                                    ratio_rest -= max_move_ratio
                                    ratio_post += max_move_ratio

                                if line_width * ratio_pre > 0.3:
                                    max_move_ratio = ratio_pre - 0.01

                                    if max_move_ratio > ratio_rest:
                                        max_move_ratio = ratio_rest

                                    ratio_rest -= max_move_ratio
                                    ratio_pre -= max_move_ratio

                                mid_ratio = 0.5 * (ratio_pre + ratio_post)
                                new_middle_x = (1 - mid_ratio) * p1[0] + mid_ratio * p2[0]
                                new_middle_y = (1 - mid_ratio) * p1[1] + mid_ratio * p2[1]

                                update_pos[0] += new_middle_x - old_middle_x
                                update_pos[2] += new_middle_y - old_middle_y

                            else:
                                group_one["size"][0] *= 0.9
                        else:
                            pass

                    # 高顶衣柜背面贴墙横移处理 width_rest_new > 0.1 为有横移空间
                    elif group_type in ["Armoire"] and edge_idx == 0 and width_rest_new > 0.1 and group_height >= 1.8:
                        ratio_width = abs(group_width) / line_width
                        line_pre_idx = (line_idx - 1) % len(line_list)
                        line_next_idx = (line_idx + 1) % len(line_list)
                        move_over = False

                        if ratio_pre > 0.1 and ratio_post > 0.95:
                            # 贴 unit_rat[1]
                            ratio_post = 1.0
                            ratio_pre = 1.0 - ratio_width
                            move_over = True
                        elif ratio_pre < 0.05 and ratio_post < 0.9:
                            # 贴 unit_rat[0]
                            ratio_pre = 0.0
                            ratio_post = ratio_width
                            move_over = True
                        elif ratio_pre < 0.05 and ratio_post > 0.95:
                            # 找
                            if line_pre_idx in line_used:
                                for _data in line_used[line_pre_idx]:
                                    if "group" in _data and _data["group"] and _data["group"][0]["type"] == "Bed":
                                        # 贴 unit_rat[0]
                                        ratio_pre = 0.0
                                        ratio_post = ratio_width
                                        move_over = True
                                        break
                            if not move_over and line_next_idx in line_used:
                                for _data in line_used[line_next_idx]:
                                    if "group" in _data and _data["group"] and _data["group"][0]["type"] == "Bed":
                                        # 贴 unit_rat[1]
                                        ratio_post = 1.0
                                        ratio_pre = 1.0 - ratio_width
                                        move_over = True
                                        break

                        if move_over:
                            mid_ratio = 0.5 * (ratio_pre + ratio_post)
                            new_middle_x = (1 - mid_ratio) * p1[0] + mid_ratio * p2[0]
                            new_middle_y = (1 - mid_ratio) * p1[1] + mid_ratio * p2[1]

                            update_pos[0] += new_middle_x - old_middle_x
                            update_pos[2] += new_middle_y - old_middle_y

                    update_pos[0] -= math.sin(zone_ang + edge_idx * math.pi * 0.5) * depth_rest_new
                    update_pos[2] -= math.cos(zone_ang + edge_idx * math.pi * 0.5) * depth_rest_new

                # 更新位置
                group_one['position'] = [update_pos[0], update_pos[1], update_pos[2]]
                group_one['rotation'] = [0, math.sin(zone_ang / 2), 0, math.cos(zone_ang / 2)]
                group_one['regulation'] = [0.0, 0.0, 0.0, 0.0]

                # 更新regulation
                group_regulation_update(zone_one, group_one)

                # 特别信息
                group_one['center'] = 0
                # 区域信息
                # group_one['region_direct'] = ratio_dir
                # group_one['region_middle'] = (ratio_pre + ratio_post) / 2
                # group_one['region_center'] = []
                # group_one['region_extent'] = group_depth

                # if len(group_one['region_center']) <= 0:
                #    group_one['region_center'] = [po[0], 0, po[1]]
                # group_one['region_extent'] = region_depth
                # 新增组合
                group_result.append(group_one)

            # 更新参数
            # param_one['ratio'] = [ratio_pre, ratio_post]
            # param_one['width_rest'] = width_rest_new
            # param_one['depth_rest'] = depth_rest_new

    # test_visual_house_region_data(line_list, zone_list, group_result)
    # 返回信息
    return group_result


# 数据计算：区域靠墙
def compute_zone_rely(zone_one, line_list):
    object_type, object_size = zone_one['type'], [abs(zone_one['size'][i]) for i in range(3)]
    object_pos, object_rot = zone_one['position'], zone_one['rotation']
    # 家具矩形
    if 'unit' in zone_one:
        object_unit = zone_one['unit']
    else:
        object_unit = compute_furniture_rect(object_size, object_pos, object_rot)
        zone_one['unit'] = object_unit
    # 靠墙判断
    rely_dlt = 0.40
    if object_type.startswith('Meeting') or object_type.startswith('sofa'):
        rely_dlt = 0.45
    elif object_type.startswith('Bed') or object_type.startswith('bed'):
        rely_dlt = 0.40
    elif object_type.startswith('Cabinet') or object_type.startswith('cabinet'):
        rely_dlt = 0.40

    unit_one = object_unit
    edge_len, edge_idx = int(len(unit_one) / 2), -1

    rely_dis, rely_idx, rely_rat = 0, -1, []
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
        # if unit_width < unit_depth / 2 or unit_width < 0.2:
        #     continue
        unit_dis, unit_idx, unit_rat = 0, -1, []

        max_unit_dis, max_unit_idx = -1000, -1
        for line_idx, line_one in enumerate(line_list):
            # 重合方向
            x1, y1, x2, y2 = line_one['p1'][0], line_one['p1'][1], line_one['p2'][0], line_one['p2'][1]
            line_width, line_angle = line_one['width'], line_one['angle']
            if abs(ang_to_ang(line_angle - unit_angle)) > 0.1:
                continue
            if abs(y1 - y2) < 0.1 and abs(x1 - x2) < 0.1:
                continue
            elif abs(y1 - y2) < 0.1:
                if abs(y1 - y_p) > rely_dlt * 1.0:
                    continue
                elif abs(y1 - y_p) > rely_dlt * 0.5 and j > 0:
                    continue
            elif abs(x1 - x2) < 0.1:
                if abs(x1 - x_p) > rely_dlt * 1.0:
                    continue
                elif abs(x1 - x_p) > rely_dlt * 0.5 and j > 0:
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

            temp_dis = line_width * (r2 - r1)
            if temp_dis > max_unit_dis:
                max_unit_dis = temp_dis
                unit_idx, unit_dis = line_idx, temp_dis
                unit_rat = [min(r_p, r_q), max(r_p, r_q)]

        if 0 <= unit_idx < len(line_list):
            if unit_dis > rely_dis:
                edge_idx, rely_dis, rely_idx, rely_rat = j, unit_dis, unit_idx, unit_rat
            if unit_dis > unit_width * 0.9 and unit_width > unit_depth:
                break
    return edge_idx, rely_idx, rely_rat


# 数据计算：区域成对
def compute_zone_pair(param_old, group_new, line_list, line_used, line_face,
                      max_pass=-1, min_pass=-1, room_type='', room_area=10, door_pt_entry=[]):
    zone_one = param_old['zone']
    zone_type, zone_size = zone_one['type'], zone_one['size']
    edge_idx, line_idx, unit_rat = zone_one['edge_idx'], zone_one['line_idx'], zone_one['unit_rat']
    index_face = {}

    if line_idx < 0 or line_idx >= len(line_list):
        mid_ang = rot_to_ang(zone_one["rotation"])
        angle_old, stand_old = mid_ang, determine_line_angle(mid_ang)
        return {}, index_face
    else:
        # 原有组合
        line_old = line_list[param_old['index']]
        angle_old, stand_old = line_old['angle'], determine_line_angle(line_old['angle'])

    if stand_old < 0:
        return {}, index_face

    ratio_old, group_old = param_old['ratio'], param_old['group'][0]
    width_old, depth_old = group_old['size'][0], group_old['size'][2]
    width_old_min, depth_old_min = group_old['size_min'][0], group_old['size_min'][2]
    ratio_old_best = ratio_old
    if 'ratio_best' in param_old:
        ratio_old_best = param_old['ratio_best']
    ratio_half = (ratio_old_best[0] + ratio_old_best[1]) / 2
    if min_pass <= -1:
        min_pass = MIN_GROUP_PASS
    if max_pass <= -1:
        max_pass = MAX_GROUP_PASS
    # 新增组合
    group_one, group_size = group_new, group_new['size']
    # 最佳参数
    param_pair = {
        'index': -1,
        'score': -100,
        'vertical': 0,
        'width': 0,
        'depth': 0,
        'depth_suit': 0,
        'width_rest': 0,
        'depth_rest': 0,
        'ratio': [0, 1],
        'ratio_best': [0.5, 0.5],
        'ratio_face': [0, 1],
        'group': []
    }
    if edge_idx == 0:
        line_old, ratio_old = line_list[line_idx], unit_rat
        width_idx, width_max, depth_max = -1, 0, 10
        depth_idx, depth_min = -1, 10
        # 遍历线段
        for line_idx, line_one in enumerate(line_list):
            width_new, depth_new, ratio_new, ratio_new_best, ratio_face = \
                compute_pair_ratio(line_old, ratio_old, line_one)
            # 宽度过小
            if len(ratio_new) <= 0:
                continue
            if width_new <= 0.5:
                continue
            # 深度最小
            if depth_new < depth_min:
                depth_idx, depth_min = line_idx, depth_new
            # 两侧过小
            line_idx_pre = (line_idx - 1 + len(line_list)) % len(line_list)
            line_idx_post = (line_idx + 1 + len(line_list)) % len(line_list)
            line_pre, line_post = line_list[line_idx_pre], line_list[line_idx_post]
            if width_new < 1.5:
                if line_pre['type'] in [UNIT_TYPE_DOOR] and line_one['score_pre'] == 1:
                    continue
                if line_post['type'] in [UNIT_TYPE_DOOR] and line_one['score_post'] == 1:
                    continue
                if line_one['score'] == 6:
                    continue
            if depth_new > depth_old + MID_GROUP_PASS + MIN_GROUP_PASS:
                if ratio_face[0] >= ratio_old_best[1]:
                    continue
                if ratio_face[1] <= ratio_old_best[0]:
                    continue
            depth_rest = depth_new - depth_old - group_size[2]
            # 宽度最大
            if width_new > min(width_max * 1.0, width_old) and min_pass < depth_rest < max_pass:
                width_idx, width_max, depth_max = line_idx, width_new, depth_rest
            elif width_new > min(width_max * 0.5, 1.5) and min_pass < depth_rest < max_pass:
                if 0.5 < depth_rest < 2.0 < depth_max:
                    width_idx, width_max, depth_max = line_idx, width_new, depth_rest
                elif depth_max < 1.5 < depth_rest < 2.0:
                    width_idx, width_max, depth_max = line_idx, width_new, depth_rest
            elif ratio_face[0] < ratio_half < ratio_face[1]:
                width_idx, width_max, depth_max = line_idx, width_new, depth_rest
            if width_idx == line_idx:
                # 补充宽度
                group_pass = MID_GROUP_PASS
                if ratio_face[0] > 0.01 and line_one['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_WALL]:
                    width_add = min(line_post['width'], (ratio_face[0] - 0) * line_old['width'])
                    width_new += width_add
                    ratio_face[0] -= width_add / line_old['width']
                    ratio_new[1] += width_add / line_one['width']
                    pass
                if ratio_face[1] < 0.99 and line_one['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_WALL]:
                    width_add = min(line_pre['width'], (1 - ratio_face[1]) * line_old['width'])
                    width_new += width_add
                    ratio_face[1] += width_add / line_old['width']
                    ratio_new[0] -= width_add / line_one['width']
                    pass
                if group_old['type'] == 'Meeting':
                    if width_new > width_old > group_new['size'][0]:
                        width_new = min(width_old + group_pass * 2, width_new)
                    elif width_new > group_new['size'][0] + group_pass * 2 > width_old:
                        width_new = min(group_new['size'][0] + group_pass * 2, width_new)
                else:
                    if width_new > width_old > group_new['size'][0]:
                        width_new = min(width_old + group_pass * 2, width_new)
                width_rest = width_new - group_size[0]
                # 补充深度
                depth_rest = depth_new - depth_old - group_size[2]
                # 更新参数
                param_pair['index'] = line_idx
                param_pair['score'] = (ratio_face[1] - ratio_face[0]) * 10
                param_pair['width'] = group_size[0]
                param_pair['depth'] = group_size[2]
                param_pair['width_rest'] = width_rest
                param_pair['depth_rest'] = depth_rest
                param_pair['ratio'] = ratio_new
                param_pair['ratio_best'] = ratio_new_best
                param_pair['ratio_face'] = ratio_face
                param_pair['depth_face'] = depth_new
                # 更新最佳
                if ratio_face[0] < -0.01 or ratio_face[1] > 1.01:
                    ratio_old_1 = ratio_face[:]
                    if ratio_face[0] < -0.01 and ratio_face[1] < 1.01:
                        ratio_old_1[0] = max(ratio_face[0], ratio_old_1[0])
                    if ratio_face[0] > -0.01 and ratio_face[1] > 1.01:
                        ratio_old_1[1] = min(ratio_face[1], ratio_old_1[1])
                    width, depth, ratio, ratio_best, ratio_face = compute_pair_ratio(line_old, ratio_old_1, line_one)
                    if width > group_new['size'][0]:
                        param_pair['ratio_best'] = ratio_best[:]
        # 参数判断
        index_pair = int(param_pair['index'])
        if index_pair < 0:
            return {}, index_face
        line_pair = line_list[index_pair]
        pair_width, pair_depth = 0, 0
        if 'width' in line_pair:
            pair_width = line_pair['width']
        if 'depth' in line_pair:
            pair_depth = line_pair['depth']
        if line_pair['type'] not in [UNIT_TYPE_WALL]:
            type_old, size_old = group_old['type'], group_old['size']
            if type_old not in ['Meeting']:
                return {}, index_face
            elif pair_width < width_old_min:
                depth_face = 0
                if 'depth_face' in param_pair:
                    depth_face = param_pair['depth_face']
                if depth_face > max(3, size_old[2]) + UNIT_DEPTH_DODGE / 2:
                    pass
                else:
                    return {}, index_face
            elif pair_depth > max_pass * 0.5:
                return {}, index_face
        # 原有组合
        param_old['index_pair'] = index_pair
    elif edge_idx == 2:
        ratio_face = param_old['ratio_best']
        width_swap, depth_swap = zone_size[0], zone_size[2]
        depth_rest = depth_swap - depth_old - group_size[2]
        type_swap = 1
        # 新增组合 参数1
        param_pair['index'] = param_old['index']
        param_pair['score'] = (ratio_face[1] - ratio_face[0]) * 10
        param_pair['width'] = group_size[0]
        param_pair['depth'] = group_size[2]
        param_pair['width_rest'] = width_swap - group_size[0]
        param_pair['depth_rest'] = max(depth_rest, 0.1 - group_size[2])
        param_pair['ratio'] = ratio_face[:]
        param_pair['ratio_best'] = ratio_face[:]
        param_pair['ratio_face'] = ratio_face
        param_pair['depth_face'] = depth_swap
        # 新增组合 参数2
        param_pair['index_swap'] = -1
        param_pair['type_swap'] = type_swap
        param_pair['width_swap'] = width_swap
        param_pair['depth_swap'] = depth_swap
        param_pair['ratio_swap'] = ratio_face[:]
        param_pair['ratio_best'] = ratio_face[:]
        # 原有组合 参数1
        param_old['ratio'] = ratio_face[:]
        param_old['depth_rest'] = depth_rest
        # 原有组合 参数2
        param_old['index_swap'] = param_old['index']
        param_old['type_swap'] = type_swap
        param_old['width_swap'] = width_swap
        param_old['depth_swap'] = depth_swap
        param_old['ratio_swap'] = ratio_face[:]
    elif edge_idx == -1:
        pass
    else:
        return {}, index_face

    # 参数信息
    param_add = param_pair.copy()
    param_add['ratio'] = param_pair['ratio'][:]
    param_add['ratio_best'] = param_pair['ratio_best'][:]
    param_add['ratio_face'] = param_pair['ratio_face'][:]

    group_add = copy_exist_group(group_new)
    param_add['group'].append(group_add)
    index_pair = int(param_add['index'])
    if index_pair not in line_used:
        line_used[index_pair] = []
    line_used[index_pair].append(param_add)
    return param_add, index_face


# 数据计算：区域矩形
def compute_zone_rect(size, position, rotation, adjust=[0, 0, 0, 0], direct=0):
    # 角度
    ang = rot_to_ang(rotation)
    angle = ang
    # 尺寸
    width_x, width_y, width_z = size[0], size[1], size[2]
    center_x, center_y, center_z = position[0], position[1], position[2]
    # 矩形
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
        return [x2, z2, x3, z3, x4, z4, x1, z1]
    return [x1, z1, x2, z2, x3, z3, x4, z4]


# 拷贝组合
def copy_exist_group(group_one):
    group_add = group_one.copy()
    group_add['size'] = group_one['size'][:]
    group_add['offset'] = group_one['offset'][:]
    group_add['position'] = group_one['position'][:]
    group_add['rotation'] = group_one['rotation'][:]
    if 'size_min' in group_one:
        group_add['size_min'] = group_one['size_min'][:]
    if 'size_rest' in group_one:
        group_add['size_rest'] = group_one['size_rest'][:]
    if 'regulation' in group_one:
        group_add['regulation'] = group_one['regulation'][:]
    if 'seed_list' in group_one:
        group_add['seed_list'] = group_one['seed_list'][:]
    group_add['obj_list'] = []
    return group_add


# 旋转组合
def spin_exist_group(group_one, spin=1):
    group_size = group_one['size']
    group_one['size'] = [group_size[2], group_size[1], group_size[0]]
    group_one['size_min'] = [group_one['size_min'][2], group_one['size_min'][1], group_one['size_min'][0]]

    group_one['obj_list'] = []
    return group_one


# 功能测试
if __name__ == '__main__':
    zone = {'type': 'Armoire', 'size': [1.662, 2.6000062721999995, 0.7952729999999999], 'scale': [1.0, 1.0, 1.0], 'position': [1.2266365000000001, 0, 1.7429999999999999], 'rotation': [0, 0.7071067811865475, 0, 0.7071067811865476], 'zone': '', 'unit': [0.8290000000000004, 0.9119999999999998, 0.829, 2.574, 1.6242729999999999, 2.574, 1.6242730000000003, 0.912], 'edge_idx': 0, 'line_idx': 8, 'unit_rat': [0, 1.0]}
    group = {'type': 'Armoire', 'style': 'Contemporary', 'code': 10, 'size': [1.7248781, 2.5000080000000002, 0.60000312816], 'offset': [-0.0, 0, -0.0], 'position': [1.1290015640800002, 0, 1.7429999999999999], 'rotation': [0, 0.7071067811865475, 0, 0.7071067811865477], 'size_min': [1.7248781, 2.5000080000000002, 0.60000312816], 'size_rest': [0.0, 0.0, 0.0, 0.0], 'obj_main': '9e7376fd-384d-4258-88b5-c59f12e3a35e', 'obj_type': 'storage unit/armoire - L shaped', 'obj_list': [], 'relate': '', 'relate_role': '', 'relate_position': [], 'zone': 'CloakRoom', 'seed_list': [], 'keep_list': [], 'regulation': [0.0, 0.0, 0.0, 0.0]}
    group_regulation_update(zone, group)
