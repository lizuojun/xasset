# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-10-24
@Description: 主要家具布局

"""

from Furniture.furniture_group import *
from Furniture.furniture_group_comp import *
from LayoutByRule.house_calculator import *


# 主要功能区域布局
def room_rect_layout_main(line_list, group_todo, room_type='', room_area=10, room_link=[],
                          door_pt_entry=[], door_pt_cook=[], door_pt_bath=[], door_pt_wear=[], door_pt_open=[],
                          seed_pt_media=[]):
    # 组合检查
    group_result = []
    if len(group_todo) <= 0:
        return group_result
    group_sort, group_main, group_side, group_pair, types_pair = [], [], [], [], []
    index_copy, param_copy, param_aside = [], {}, {}
    for group_one in group_todo:
        group_type = group_one['type']
        if group_type in GROUP_PAIR_FUNCTIONAL:
            group_sort.append(group_one)
            group_main.append(group_one)
            types_pair += GROUP_PAIR_FUNCTIONAL[group_type]
    for group_one in group_todo:
        group_type = group_one['type']
        if group_type in GROUP_PAIR_FUNCTIONAL:
            continue
        elif group_type in types_pair:
            group_pair.append(group_one)
        else:
            if group_type in ['Dining', 'Rest', 'Toilet'] and len(group_main) > 0:
                group_side.append(group_one)
            if group_type in ['Dining']:
                # 原样
                group_sort.append(group_one)
                index_copy.append(len(group_sort) - 1)
                # 旋转
                group_sort.append(spin_exist_group(group_one, -1))
                index_copy.append(len(group_sort) - 1)
                # 默认
                group_size_min, seed_list = [1, 1, 1], []
                if 'size_min' in group_one:
                    group_size_min = group_one['size_min']
                if 'seed_list' in group_one:
                    seed_list = group_one['seed_list']
                if min(group_size_min[0], group_size_min[2]) >= 1.2 and len(seed_list) <= 0:
                    # 新增
                    group_new = get_default_group_layout('dining')
                    group_sort.append(group_new)
                    index_copy.append(len(group_sort) - 1)
                    # 旋转
                    group_sort.append(spin_exist_group(group_new, -1))
                    index_copy.append(len(group_sort) - 1)
            elif group_type in ['Bath']:
                group_sort.insert(0, group_one)
            else:
                group_sort.append(group_one)

    # 种子参数
    for group_idx, group_one in enumerate(group_todo):
        if 'seed_position' in group_one and group_one['type'] == 'Media':
            seed_pt = group_one['seed_position']
            seed_pt_media = [seed_pt[0], seed_pt[2]]

    # 组合布局
    line_used, line_face, find_copy = {}, {}, False
    for group_idx, group_one in enumerate(group_sort):
        # 组合信息
        if group_idx in index_copy and find_copy:
            continue
        group_type, group_size = group_one['type'], group_one['size']
        group_width, group_height, group_depth = group_size[0], group_size[1], group_size[2]
        if 'size_min' in group_one:
            group_width_min, group_depth_min = group_one['size_min'][0], group_one['size_min'][2]
        else:
            group_width_min, group_depth_min = group_width, group_depth
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
        # 线段查找
        for line_idx, line_one in enumerate(line_list):
            # 初步判断
            if line_idx in line_used and len(line_used[line_idx]) >= 3:
                continue
            # 线段信息
            line_type = line_one['type']
            line_width, line_height, line_angle = line_one['width'], line_one['height'], line_one['angle']
            line_idx_pre = (line_idx - 1 + len(line_list)) % len(line_list)
            line_idx_post = (line_idx + 1 + len(line_list)) % len(line_list)
            line_idx_pre2 = (line_idx - 2 + len(line_list)) % len(line_list)
            line_idx_post2 = (line_idx + 2 + len(line_list)) % len(line_list)
            line_pre, line_post = line_list[line_idx_pre], line_list[line_idx_post]
            line_pre2, line_post2 = line_list[line_idx_pre2], line_list[line_idx_post2]
            type_pre, type_post = line_pre['type'], line_post['type']
            score_pre, score_post = line_one['score_pre'], line_one['score_post']
            score_pre_new, score_post_new, curtain_pre, curtain_post = score_pre, score_post, 0, 0
            width_cur, width_pre, width_post, window_flag = line_width, line_pre['width'], line_post['width'], 0
            if score_pre == 1 and type_pre in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                if line_pre['score_pre'] == 1 and line_pre2['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                    width_pre += line_pre2['width'] * 0.5
                if line_one['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                    width_cur += line_post['width'] * 0.5
                if width_cur < width_pre and group_type in GROUP_PAIR_FUNCTIONAL:
                    continue
                window_flag = 1
            if score_post == 1 and type_post in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                if line_post['score_post'] == 1 and line_post2['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                    width_post += line_post2['width'] * 0.5
                if line_one['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                    width_cur += line_pre['width'] * 0.5
                if width_cur < width_post and group_type in GROUP_PAIR_FUNCTIONAL:
                    continue
                window_flag = 1
            if score_pre == 1 and type_pre in [UNIT_TYPE_AISLE]:
                if score_post == 1 and type_post in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                    continue
            if score_post == 1 and type_post in [UNIT_TYPE_AISLE]:
                if score_pre == 1 and type_pre in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                    continue
            if score_pre == 1 and type_pre in [UNIT_TYPE_SIDE] and line_pre['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                width_pre = line_pre2['width']
                score_pre_new, curtain_pre = 4, 1
            if score_post == 1 and type_post in [UNIT_TYPE_SIDE] and line_post['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                width_post = line_post2['width']
                score_post_new, curtain_post = 4, 1
            unit_to_room, unit_to_type = '', ''
            if 'unit_to_room' in line_one:
                unit_to_room = line_one['unit_to_room']
            if 'unit_to_type' in line_one:
                unit_to_type = line_one['unit_to_type']
            # 类型重置
            if line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                if group_type in ['Meeting'] and line_width > UNIT_WIDTH_HOLE and line_width > group_width:
                    if unit_to_room in [''] or unit_to_type in ['Balcony', 'Terrace']:
                        line_type = UNIT_TYPE_WINDOW
                elif group_type in ['Dining']:
                    if score_pre_new == 4 and type_pre in [UNIT_TYPE_WALL] and width_pre > line_width:
                        pass
                    elif score_post_new == 4 and type_post in [UNIT_TYPE_WALL] and width_post > line_width:
                        pass
                    elif score_pre_new == 1 and width_pre < 1.0 and line_pre['score_pre'] == 4 and \
                            line_pre2['type'] in [UNIT_TYPE_WALL] and line_pre2['width'] > line_width + line_pre['width']:
                        pass
                    elif score_post_new == 1 and width_post < 1.0 and line_post['score_post'] == 4 and \
                            line_post2['type'] in [UNIT_TYPE_WALL] and line_post2['width'] > line_width + line_post['width']:
                        pass
                    elif unit_to_type in ['Kitchen']:
                        if score_pre_new == 4 and type_pre in [UNIT_TYPE_SIDE]:
                            pass
                        elif score_post_new == 4 and type_post in [UNIT_TYPE_SIDE]:
                            pass
                        else:
                            line_type = UNIT_TYPE_WINDOW
                    elif unit_to_type in ['Balcony', 'Terrace']:
                        line_type = UNIT_TYPE_WINDOW
                    elif unit_to_type in ['none', 'OtherRoom'] and len(door_pt_cook) <= 0:
                        line_type = UNIT_TYPE_WINDOW
                elif group_type in ['Work'] and line_width > UNIT_WIDTH_HOLE:
                    if unit_to_room in [''] or unit_to_type in ['Balcony', 'Terrace']:
                        line_type = UNIT_TYPE_WINDOW
            # 墙体筛选
            if line_type in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                pass
            elif line_type in [UNIT_TYPE_AISLE] and line_one['depth'] > 3:
                pass
            else:
                continue
            if line_width <= 0.2:
                continue

            # 阳角并列
            if score_pre == 2 and type_pre in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                if line_pre['width'] < MIN_GROUP_PASS < MID_GROUP_PASS < line_one['width']:
                    line_idx_pre2 = (line_idx - 2 + len(line_list)) % len(line_list)
                    if line_idx_pre2 not in line_used:
                        window_flag = 2
            if score_post == 2 and type_post in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                if line_post['width'] < MIN_GROUP_PASS < MID_GROUP_PASS < line_one['width']:
                    line_idx_post2 = (line_idx + 2 + len(line_list)) % len(line_list)
                    if line_idx_post2 not in line_used:
                        window_flag = 2
            if MIN_GROUP_PASS < line_width < group_width_min and window_flag <= 0:
                width_rest_add = 0
                if line_one['score_pre'] == 2:
                    width_rest_add = UNIT_WIDTH_DOOR
                if line_one['score_post'] == 2:
                    width_rest_add = UNIT_WIDTH_DOOR
                if line_one['score_pre'] == 1 and line_pre['type'] == UNIT_TYPE_DOOR and group_type in ['Dining']:
                    width_rest_add = UNIT_WIDTH_DOOR
                if line_one['score_post'] == 1 and line_post['type'] == UNIT_TYPE_DOOR and group_type in ['Dining']:
                    width_rest_add = UNIT_WIDTH_DOOR
                if group_width_min > 2.0 and width_rest_add <= 0:
                    width_rest_add = group_width_min / 10
                if line_width + width_rest_add < group_width_min / 2:
                    continue
                if line_width + width_rest_add < group_width_min:
                    if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                        pass
                    elif len(group_sort) >= 2:
                        pass
                    elif group_type in ['Work', 'Rest'] and line_width > UNIT_WIDTH_HOLE:
                        pass
                    else:
                        continue
            if line_width < group_width_min + 0.1 and group_type in ['Bath', 'Toilet']:
                continue
            # 尺寸判断
            max_pass, min_pass, mid_pass = 20, 0, MIN_GROUP_PASS
            if group_type in GROUP_PAIR_FUNCTIONAL:
                merge_type = [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                max_pass, min_pass = 20, 0
                if room_area > MAX_ROOM_AREA_LIVING:
                    max_pass, min_pass, mid_pass = 20, MIN_GROUP_PASS, MID_GROUP_PASS
                if window_flag >= 1 and line_width > min(group_width_min + MID_GROUP_PASS * 2, group_width + MID_GROUP_PASS, 4):
                    merge_type = []
                elif 'back_depth' in line_one and line_one['back_depth'] >= 0.001 and \
                        line_width > group_width + MIN_GROUP_PASS:
                    merge_type = []
            elif group_type in ['Dining']:
                merge_type = [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                max_pass, min_pass = 20, 0
                if line_one['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_DOOR]:
                    side_room = ''
                    if 'unit_to_type' in line_pre:
                        side_room = line_pre['unit_to_type']
                    if side_room in ['Kitchen'] and 3 > line_width > line_pre['width'] > UNIT_WIDTH_DOOR:
                        merge_type = [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                    elif len(side_room) > 0 and line_idx in line_face:
                        merge_type = [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                if line_one['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_DOOR]:
                    side_room = ''
                    if 'unit_to_type' in line_post:
                        side_room = line_post['unit_to_type']
                    if side_room in ['Kitchen'] and 3 > line_width > line_post['width'] > UNIT_WIDTH_DOOR:
                        merge_type = [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                    elif len(side_room) > 0 and line_idx in line_face:
                        merge_type = [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                if window_flag >= 1 and line_width > min(group_width + MID_GROUP_PASS, 3):
                    merge_type = []
            elif group_type in ['Work', 'Rest']:
                merge_type = [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                max_pass, min_pass = 20, 0
            elif group_type in ['Bath', 'Toilet']:
                merge_type = [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                max_pass, min_pass = 20, MIN_GROUP_PASS / 2
                if group_depth > MID_GROUP_PASS:
                    min_pass = 0
                if line_width > 0.5:
                    merge_type = [UNIT_TYPE_WALL]
            else:
                merge_type = [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                max_pass, min_pass = 20, MIN_GROUP_PASS * 2
                if room_type in ['Balcony', 'Terrace']:
                    min_pass = 0
            dlt_pass = 0
            if group_type in ['Meeting'] and group_depth > 2.0:
                if line_width > min(group_width_min, 2.5) and group_depth - group_depth_min > 1:
                    dlt_pass = 0.5
            elif group_type in ['Dining'] and room_area > MAX_ROOM_AREA_LIVING:
                mid_pass = room_area / 100
            elif group_type in ['Bath'] and group_depth - group_depth_min > 0.2:
                mid_pass = 0
            suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                compute_suit_ratio(line_list, line_idx, group_width, group_depth - dlt_pass,
                                   [0, 1], merge_type, max_pass, min_pass, mid_pass, line_used)
            suit_width_best = line_width * (suit_ratio_best[1] - suit_ratio_best[0])
            if suit_ratio[0] < 0 - 10 or suit_ratio[1] > 0 + 10:
                continue
            elif suit_width_best > min(group_width, 3.0) * 2 and group_one in group_main and len(group_side) > 0:
                p1, p2 = line_one['p1'], line_one['p2']
                p1_distance_entry, p2_distance_entry = 0, 0
                p1_distance_open, p2_distance_open = 0, 0
                if len(door_pt_entry) >= 2:
                    p1_distance_entry = abs(p1[0] - door_pt_entry[0]) + abs(p1[1] - door_pt_entry[1])
                    p2_distance_entry = abs(p2[0] - door_pt_entry[0]) + abs(p2[1] - door_pt_entry[1])
                if len(door_pt_open) >= 2:
                    p1_distance_open = abs(p1[0] - door_pt_open[0]) + abs(p1[1] - door_pt_open[1])
                    p2_distance_open = abs(p2[0] - door_pt_open[0]) + abs(p2[1] - door_pt_open[1])
                if p1_distance_entry - p1_distance_open > p2_distance_entry - p2_distance_open:
                    aside_width = max(group_width + 1, suit_width_best * 0.5)
                    aside_ratio = [0, min(suit_ratio_best[0] + aside_width / line_width, 1)]
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width, group_depth - dlt_pass,
                                           aside_ratio, merge_type, max_pass, min_pass, mid_pass, line_used)
                else:
                    aside_width = max(group_width + 1, suit_width_best * 0.5)
                    aside_ratio = [max(suit_ratio_best[1] - aside_width / line_width, 0), 1]
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width, group_depth - dlt_pass,
                                           aside_ratio, merge_type, max_pass, min_pass, mid_pass, line_used)
            # 最佳尺寸
            suit_width_best = line_width * (suit_ratio_best[1] - suit_ratio_best[0])
            suit_depth_best = 10
            line_depth_all, line_depth_min = line_one['depth_all'], 10
            for depth_one in line_depth_all:
                ratio_pre, ratio_post = depth_one[0], depth_one[1]
                if 0 < depth_one[2] < line_depth_min:
                    line_depth_min = depth_one[2]
                if ratio_pre >= suit_ratio_best[1] or ratio_post <= suit_ratio_best[0]:
                    pass
                elif 0 < depth_one[2] <= suit_depth_best:
                    suit_depth_best = depth_one[2]
            if group_type in GROUP_PAIR_FUNCTIONAL:
                if 0.5 < suit_width_best < min(group_width, 2.0):
                    suit_depth, suit_depth_best = suit_depth_min, suit_depth_min
            if group_type in ['Meeting'] and suit_width < group_width_min - 0.1:
                if suit_width_best > group_width_min * 0.8 and group_depth + MAX_GROUP_PASS > suit_depth > group_depth:
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width_min, group_depth_min,
                                           [0, 1], merge_type, max_pass, min_pass)
                    suit_depth, suit_depth_best = suit_depth_min, suit_depth_min
                elif suit_width_best > 1 and line_width > group_width_min and group_depth + MAX_GROUP_PASS > suit_depth > group_depth:
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width_min, group_depth_min,
                                           [0, 1], merge_type, max_pass, min_pass)
                    suit_depth, suit_depth_best = suit_depth_min, suit_depth_min
                elif line_width > min(group_width_min * 0.8, 2.0):
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width_min, group_depth_min,
                                           [0, 1], merge_type, max_pass, min_pass)
                    suit_depth, suit_depth_best = suit_depth_min, suit_depth_min
                suit_width_best = line_width * (suit_ratio_best[1] - suit_ratio_best[0])
                if max(group_width_min - 0.4, 2) < suit_width_best < group_width_min:
                    suit_ratio[0] = max(suit_ratio_best[0] - 0.4 / line_width, suit_ratio[0])
                    suit_ratio[1] = min(suit_ratio_best[1] + 0.4 / line_width, suit_ratio[1])
                    suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
            elif group_type in ['Bed'] and suit_width < group_width_min:
                if line_width > min(group_width_min, 1.8) and suit_width > 1 and room_type in ['KidsRoom']:
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, min(group_width_min, 1.8), min(group_depth_min, 1.0),
                                           [0, 1], merge_type, max_pass, min_pass)
            elif group_type in ['Dining'] and suit_width_best < group_width and suit_depth_min > MID_GROUP_PASS:
                if 0 <= suit_ratio[0] <= suit_ratio[1] <= 1:
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width, group_depth_min,
                                           [0, 1], merge_type, max_pass, min_pass, mid_pass, line_used)
                if suit_width > group_width:
                    suit_depth = suit_depth_min
            elif group_type in ['Work'] and suit_width < group_width_min - 0.1:
                if suit_width_best > min(group_width_min * 0.8, 1.5):
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, min(group_width_min * 0.8, 1.5), group_depth_min,
                                           [0, 1], merge_type, max_pass, min_pass)
                    suit_depth, suit_depth_best = suit_depth_min, suit_depth_min
            elif group_type in ['Bath'] and suit_width < group_width_min:
                group_depth_new = group_depth_min
                for depth_one in line_one['depth_all']:
                    if depth_one[1] - depth_one[0] > 0.5 and depth_one[2] > group_depth_min:
                        group_depth_new = depth_one[2]
                        break
                suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                    compute_suit_ratio(line_list, line_idx, group_width, group_depth_new,
                                       [0, 1], merge_type, max_pass, min_pass)
                suit_depth = suit_depth_min
            elif group_type in ['Toilet'] and suit_width < group_width_min and room_area <= 6:
                min_pass, dlt_pass = 0, 0.2
                suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                    compute_suit_ratio(line_list, line_idx, group_width, group_depth_min - dlt_pass,
                                       [0, 1], merge_type, max_pass, min_pass)
                suit_depth = suit_depth_min
            # 最佳尺寸
            if line_idx in line_face:
                if line_face[line_idx] <= 0 and line_idx in line_used:
                    param_old = line_used[line_idx][0]
                else:
                    suit_depth = min(suit_depth, line_face[line_idx])
            elif score_pre == 1 and line_idx_pre in line_face:
                suit_depth = min(suit_depth, line_face[line_idx_pre])
            elif score_post == 1 and line_idx_post in line_face:
                suit_depth = min(suit_depth, line_face[line_idx_post])
            if suit_depth_best > suit_depth:
                suit_depth_best = suit_depth
            if suit_width_best < line_width * (suit_ratio_best[1] - suit_ratio_best[0]):
                suit_width_best = line_width * (suit_ratio_best[1] - suit_ratio_best[0])
            # 两侧处理
            well_width = group_width_min
            if group_type == 'Dining':
                well_width = group_width + MIN_GROUP_PASS
            well_aside, flag_aside = False, 0
            if line_width >= MID_GROUP_PASS * 0.5 and line_one['score_pre'] == 1:
                if line_pre['type'] in [UNIT_TYPE_AISLE] and line_pre['depth'] > 3:
                    well_aside, flag_aside = True, -1
            if line_width >= MID_GROUP_PASS * 0.5 and line_one['score_post'] == 1:
                if line_post['type'] in [UNIT_TYPE_AISLE] and line_post['depth'] > 3:
                    well_aside, flag_aside = True, 1
            if line_width >= MID_GROUP_PASS * 1.0 and line_one['score_pre'] == 2 and line_pre['type'] in [UNIT_TYPE_WALL]:
                well_aside, flag_aside = True, -1
            if line_width >= MID_GROUP_PASS * 1.0 and line_one['score_post'] == 2 and line_post['type'] in [UNIT_TYPE_WALL]:
                well_aside, flag_aside = True, 1
            if suit_width < well_width and well_aside:
                # 阳角放宽
                if line_one['score_pre'] == 2 and 0 <= suit_ratio[0] <= 0.01 and \
                        line_pre['type'] in [UNIT_TYPE_WALL] and flag_aside <= -1:
                    width_rest_add = min(well_width - suit_width, MIN_GROUP_PASS * 1)
                    if group_type in ['Meeting']:
                        if 1.5 < suit_width < group_width_min - 0.1 and suit_depth > group_depth:
                            width_rest_add = min(well_width - suit_width, MIN_GROUP_PASS * 2)
                        else:
                            width_rest_add = 0
                    elif group_type in ['Dining']:
                        if suit_width < group_width:
                            width_rest_add = min(well_width - suit_width, MIN_GROUP_PASS * 2)
                    elif group_type in ['Bed']:
                        width_rest_add = min(well_width - suit_width, MIN_GROUP_PASS * 1)
                    suit_ratio[0] -= width_rest_add / line_width
                elif line_one['score_pre'] == 1 and 0 <= suit_ratio[0] <= 0.01 and \
                        line_pre['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE] and flag_aside <= -1:
                    depth_set = line_pre['depth_ext']
                    depth_rat_1, depth_rat_2 = 1, 1
                    for depth_idx in range(len(depth_set) - 1, -1, -1):
                        if depth_idx == len(depth_set) - 1:
                            depth_rat_1 = depth_set[depth_idx][1]
                        if depth_set[depth_idx][2] >= suit_depth - 0.01:
                            depth_rat_1 = depth_set[depth_idx][0]
                        else:
                            break
                    width_side = line_pre['width'] * (depth_rat_2 - depth_rat_1)
                    width_rest_add = min(well_width - suit_width, width_side, MID_GROUP_PASS)
                    if line_pre['type'] in [UNIT_TYPE_AISLE]:
                        width_rest_add = min(well_width - suit_width, line_pre['width'], MID_GROUP_PASS * 2)
                    elif 'unit_to_room' in line_pre and len(line_pre['unit_to_room']) <= 0:
                        width_rest_add = 0
                    suit_ratio[0] = 0 - width_rest_add / line_width
                    if group_type in ['Dining'] and line_pre['width'] > UNIT_WIDTH_HOLE:
                        suit_ratio[0] = 0 - min(line_pre['width'] - MIN_GROUP_PASS, UNIT_WIDTH_HOLE * 1.5) / line_width
                if line_one['score_post'] == 2 and 1 >= suit_ratio[1] >= 0.99 and \
                        line_post['type'] in [UNIT_TYPE_WALL] and flag_aside >= 1:
                    width_rest_add = 0
                    if group_type in ['Meeting']:
                        if 1.5 < suit_width < group_width_min - 0.1 and suit_depth > group_depth:
                            width_rest_add = min(well_width - suit_width, MIN_GROUP_PASS * 2)
                        else:
                            width_rest_add = 0
                    elif group_type in ['Dining']:
                        if suit_width < group_width:
                            width_rest_add = min(well_width - suit_width, MIN_GROUP_PASS * 2)
                    elif group_type in ['Bed']:
                        width_rest_add = min(well_width - suit_width, MIN_GROUP_PASS * 1)
                    suit_ratio[1] += width_rest_add / line_width
                elif line_one['score_post'] == 1 and 1 >= suit_ratio[1] >= 0.99 and \
                        line_post['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE] and flag_aside >= 1:
                    depth_set = line_post['depth_ext']
                    depth_rat_1, depth_rat_2 = 0, 0
                    for depth_idx in range(0, len(depth_set)):
                        if depth_idx == 0:
                            depth_rat_2 = depth_set[depth_idx][0]
                        if depth_set[depth_idx][2] >= suit_depth - 0.01:
                            depth_rat_2 = depth_set[depth_idx][1]
                        else:
                            break
                    width_side = line_post['width'] * (depth_rat_2 - depth_rat_1)
                    width_rest_add = min(well_width - suit_width, width_side, MID_GROUP_PASS)
                    if line_post['type'] in [UNIT_TYPE_AISLE]:
                        width_rest_add = min(well_width - suit_width, line_post['width'], MID_GROUP_PASS * 2)
                    elif 'unit_to_room' in line_post and len(line_post['unit_to_room']) <= 0:
                        width_rest_add = 0
                    suit_ratio[1] = 1 + width_rest_add / line_width
                    if group_type in ['Dining'] and line_post['width'] > UNIT_WIDTH_HOLE:
                        suit_ratio[1] = 1 + min(line_post['width'] - MIN_GROUP_PASS, UNIT_WIDTH_HOLE * 1.5) / line_width
                suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
            # 种子处理
            if 'seed_position' in group_one and 'seed_rotation' in group_one:
                seed_position, seed_rotation = group_one['seed_position'], group_one['seed_rotation']
                seed_point = [seed_position[0], seed_position[2]]
                seed_ratio = suit_ratio[:]
                dis1, dis2, dis3 = compute_line_distance(line_one, seed_ratio, seed_point, depth=group_depth / 2)
                seed_flag = False
                if min(dis1, dis2, dis3) < UNIT_WIDTH_DOOR:
                    seed_flag = True
                elif min(dis1, dis2, dis3) < 1 and group_type in ['Dining'] and line_idx not in line_used:
                    seed_flag = True
                if seed_flag and line_width > 0.1:
                    if determine_line_angle(line_angle) == 0:
                        seed_p0_z = seed_position[0]
                        line_p1_z = line_one['p1'][0]
                        line_p2_z = line_one['p2'][0]
                        if line_p2_z - line_p1_z > 0:
                            seed_ratio[0] = ((seed_p0_z - group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                            seed_ratio[1] = ((seed_p0_z + group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                        elif line_p2_z - line_p1_z < 0:
                            seed_ratio[0] = ((seed_p0_z + group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                            seed_ratio[1] = ((seed_p0_z - group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                    elif determine_line_angle(line_angle) == 1:
                        seed_p0_z = seed_position[2]
                        line_p1_z = line_one['p1'][1]
                        line_p2_z = line_one['p2'][1]
                        if line_p2_z - line_p1_z > 0:
                            seed_ratio[0] = ((seed_p0_z - group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                            seed_ratio[1] = ((seed_p0_z + group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                        elif line_p2_z - line_p1_z < 0:
                            seed_ratio[0] = ((seed_p0_z + group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                            seed_ratio[1] = ((seed_p0_z - group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                    if suit_ratio[0] > seed_ratio[0]:
                        suit_ratio[0] = seed_ratio[0]
                    if suit_ratio[1] < seed_ratio[1]:
                        suit_ratio[1] = seed_ratio[1]
                    suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                    if suit_depth > group_depth + MID_GROUP_PASS:
                        suit_depth = group_depth + MID_GROUP_PASS
                    if suit_depth < group_depth:
                        suit_depth = group_depth
                    if suit_depth_min > suit_depth:
                        suit_depth_min = suit_depth
            elif 'obj_type' in group_one and 'table/dining table - round' in group_one['obj_type']:
                if suit_depth < group_depth - 0.2:
                    continue

            # 尺寸判断
            if suit_width < group_width_min - 0.02:
                seed_flag = 0
                if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                    seed_flag = 1
                if 'keep_list' in group_one and len(group_one['keep_list']) > 0:
                    seed_flag = 1
                if seed_flag > 0 and suit_width > MID_GROUP_PASS * 1.5:
                    # 进深放宽
                    if line_width < group_width_min and 0 <= suit_ratio[0] <= suit_ratio[1] <= 1:
                        suit_ratio = [0, 1]
                        suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                elif suit_width > 3 > group_width_min * 0.5 or suit_width > max(2, group_width_min - 0.1):
                    if line_width < group_width_min and 0 <= suit_ratio[0] <= suit_ratio[1] <= 1:
                        suit_ratio = [0, 1]
                        suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                elif suit_width > group_width_min - 0.20:
                    if group_type in ['Meeting', 'Bed']:
                        pass
                    else:
                        continue
                elif suit_width > min(group_width_min * 0.8, 1.5):
                    if group_type in ['Work', 'Rest']:
                        pass
                    else:
                        continue
                else:
                    continue
            if suit_width < group_width_min:
                if suit_width > group_width * 0.8 and (suit_ratio[0] > 0.1 or suit_ratio[1] < 0.9):
                    pass
                elif group_type in ['Meeting'] and suit_width < min(group_width_min - 0.5, 2) and suit_depth > 5:
                    continue
                elif group_type in ['Dining', 'Work'] and group_width_min < group_width - 0.1:
                    continue

            # 避让参数
            ratio_aside, param_aside_temp = [], {}
            group_aside, group_aside_type = {}, ''
            ratio_new_ex = []
            if line_idx in line_used:
                param_idx = len(line_used[line_idx]) - 1
                param_old = line_used[line_idx][param_idx]
                group_old = param_old['group'][0]
                group_aside_type = group_old['type']
            # 并列判断
            if line_idx in line_used and group_aside_type not in types_pair:
                param_idx = len(line_used[line_idx]) - 1
                param_old = line_used[line_idx][param_idx]
                width_rest = param_old['width_rest']
                group_old = param_old['group'][0]
                width_old, depth_old = group_old['size'][0], group_old['size'][2]
                if group_old['type'] in types_pair and width_rest < group_width + MID_GROUP_PASS * 2:
                    continue
                if line_width - width_old <= max(0.1, group_width_min):
                    continue
                # 占用效果计算
                ratio_old = param_old['ratio']
                ratio_width = param_old['width'] / line_width
                ratio_new, ratio_aside, ratio_pair = [], [], []
                # 优先保证电视正对
                if 'ratio_pair' in param_old and len(param_old['ratio_pair']) > 0:
                    ratio_pair = param_old['ratio_pair'][:]
                if 'ratio_aside' in param_old and len(param_old['ratio_aside']) > 0:
                    ratio_pair = param_old['ratio_aside'][:]
                if 'ratio_swap' in param_old and len(param_old['ratio_swap']) > 0:
                    ratio_pair = param_old['ratio_swap'][:]
                if len(ratio_pair) >= 2:
                    if (ratio_pair[0] + ratio_pair[1]) / 2 < (ratio_old[0] + ratio_old[1]) / 2 - 0.01 and ratio_old[1] - group_width / line_width - ratio_old[0] > ratio_width:
                        ratio_max = max(ratio_old[1], suit_ratio[1])
                        ratio_key = ratio_max - group_width / line_width
                        if ratio_key > ratio_pair[1] and line_width * (ratio_pair[1] - ratio_old[0]) > width_old:
                            ratio_key = ratio_pair[1]
                        if ratio_key < ratio_old[0] + ratio_width:
                            ratio_key = ratio_old[0] + ratio_width
                        ratio_new = [ratio_key, ratio_max]
                        ratio_aside = [ratio_old[0], ratio_key]
                        if ratio_new[1] < suit_ratio[1]:
                            ratio_new[1] = suit_ratio[1]
                    elif (ratio_pair[0] + ratio_pair[1]) / 2 > (ratio_old[0] + ratio_old[1]) / 2 + 0.01 and ratio_old[1] - group_width / line_width - ratio_old[0] > ratio_width:
                        ratio_min = min(ratio_old[0], suit_ratio[0])
                        ratio_key = ratio_min + group_width / line_width
                        if ratio_key < ratio_pair[0] and line_width * (ratio_old[1] - ratio_pair[0]) > width_old:
                            ratio_key = ratio_pair[0]
                        if ratio_key > ratio_old[1] - ratio_width:
                            ratio_key = ratio_old[1] - ratio_width
                        ratio_new = [ratio_min, ratio_key]
                        ratio_aside = [ratio_key, ratio_old[1]]
                        if ratio_new[0] > suit_ratio[0]:
                            ratio_new[0] = suit_ratio[0]
                    else:
                        rest_width_0 = line_width * (ratio_pair[0] - suit_ratio[0])
                        rest_width_1 = line_width * (suit_ratio[1] - ratio_pair[1])
                        if rest_width_0 < group_width_min and rest_width_1 < group_width_min:
                            if line_width * (ratio_pair[1] - ratio_pair[0]) - width_old < group_width_min:
                                continue
                        elif rest_width_0 > rest_width_1 and rest_width_0 > group_width_min:
                            ratio_new = [suit_ratio[0], ratio_pair[0]]
                            ratio_aside = [ratio_pair[0], ratio_old[1]]
                        elif rest_width_1 > rest_width_0 and rest_width_1 > group_width_min:
                            ratio_new = [ratio_pair[1], suit_ratio[1]]
                            ratio_aside = [ratio_old[0], ratio_pair[1]]
                if len(ratio_new) > 0 and len(ratio_aside) >= 2 and len(ratio_pair) >= 2:
                    width_aside = line_width * (ratio_aside[1] - ratio_aside[0])
                    width_pair = line_width * (ratio_pair[1] - ratio_pair[0])
                    if width_aside - width_old > MID_GROUP_PASS and width_aside - width_pair > MID_GROUP_PASS:
                        width_neighbor = MID_GROUP_PASS
                        if ratio_aside[1] < ratio_old[1] - 0.01:
                            ratio_key = ratio_old[0] + ratio_width + width_neighbor / line_width
                            ratio_new = [ratio_key, ratio_old[1]]
                            ratio_aside = [ratio_old[0], ratio_key]
                        elif ratio_aside[0] > ratio_old[0] + 0.01:
                            ratio_key = ratio_old[1] - ratio_width - width_neighbor / line_width
                            ratio_new = [ratio_old[0], ratio_key]
                            ratio_aside = [ratio_key, ratio_old[1]]
                # 其次参考进门距离
                elif group_type in ['Dining', 'Toilet'] and (len(door_pt_entry) > 0 or len(door_pt_cook) > 0):
                    dis1, dis2, dis3, dis_depth = 0, 0, 0, 0
                    width_rest_add = MIN_GROUP_PASS * 2
                    if group_old['type'] in ['Bath']:
                        width_old, width_rest_old = param_old['width'], param_old['width_rest']
                        if 'size_rest' in group_old:
                            size_rest = group_old['size_rest']
                            if 'code' in group_old and group_old['code'] >= 1100:
                                width_rest_add = MIN_GROUP_PASS * 1.0
                            elif width_old > MID_GROUP_PASS:
                                width_rest_add = 0
                            elif width_rest_old > size_rest[1] - size_rest[3] > 0.1:
                                width_rest_add = size_rest[1] - size_rest[3]
                            elif width_rest_old > size_rest[3] - size_rest[1] > 0.1:
                                width_rest_add = size_rest[3] - size_rest[1]
                            elif width_rest_old > MIN_GROUP_PASS * 5 and room_area > 8:
                                width_rest_add = MIN_GROUP_PASS * 5
                            elif width_rest_old > MIN_GROUP_PASS * 4 and room_area > 6:
                                width_rest_add = MIN_GROUP_PASS * 4
                            elif width_rest_old > MIN_GROUP_PASS * 3:
                                width_rest_add = MIN_GROUP_PASS * 3
                            elif width_rest_old > MIN_GROUP_PASS * 2:
                                width_rest_add = MIN_GROUP_PASS * 2
                            if width_rest_add > MID_GROUP_PASS * 2:
                                width_rest_add = MID_GROUP_PASS * 2
                            elif width_rest_add < MID_GROUP_PASS * 1 and room_area > 6:
                                width_rest_add = MID_GROUP_PASS * 1
                            elif width_rest_add < MIN_GROUP_PASS * 2 and room_area > 6:
                                width_rest_add = MIN_GROUP_PASS * 2
                    elif group_old['type'] in ['Meeting', 'Media']:
                        width_rest_old = param_old['width_rest']
                        if 'size_rest' in group_old:
                            size_rest = group_old['size_rest']
                            if width_rest_old < max(group_width + width_rest_add, 2):
                                width_rest_add = 0
                                if size_rest[1] + size_rest[3] > group_width - width_rest_old + 0.4:
                                    width_rest_add = -(group_width - width_rest_old)
                    if len(door_pt_cook) > 0 and group_type == 'Dining':
                        dis_depth = group_depth / 2
                        dis1, dis2, dis3 = compute_line_distance(line_one, ratio_old, door_pt_cook, dis_depth, 1)
                    elif len(door_pt_entry) > 0:
                        dis1, dis2, dis3 = compute_line_distance(line_one, ratio_old, door_pt_entry, dis_depth, 1)
                    if dis1 >= dis2:
                        ratio_key = ratio_old[0] + ratio_width + width_rest_add / line_width
                        if ratio_key > suit_ratio[1] - group_width / line_width:
                            ratio_key = suit_ratio[1] - group_width / line_width
                        if ratio_key < ratio_old[0] + ratio_width and width_rest_add >= 0:
                            ratio_key = ratio_old[0] + ratio_width
                        ratio_new = [ratio_key, suit_ratio[1]]
                        ratio_aside = [ratio_old[0], ratio_key]
                    else:
                        ratio_key = ratio_old[1] - ratio_width - width_rest_add / line_width
                        if ratio_key < suit_ratio[0] + group_width / line_width:
                            ratio_key = suit_ratio[0] + group_width / line_width
                        if ratio_key > ratio_old[1] - ratio_width and width_rest_add >= 0:
                            ratio_key = ratio_old[1] - ratio_width
                        ratio_new = [suit_ratio[0], ratio_key]
                        ratio_aside = [ratio_key, ratio_old[1]]
                    if len(ratio_new) > 0:
                        width_aside = line_width * (ratio_aside[1] - ratio_aside[0])
                        width_rest = (width_aside - width_old) / 2
                        if width_rest > max(MIN_GROUP_PASS, width_rest_add):
                            if ratio_aside[1] < ratio_old[1] - 0.01:
                                ratio_key = ratio_old[0] + ratio_width + width_rest / line_width
                                ratio_new = [ratio_key, ratio_new[1]]
                                ratio_aside = [ratio_old[0], ratio_key]
                            elif ratio_aside[0] > ratio_old[0] + 0.01:
                                ratio_key = ratio_old[1] - ratio_width - width_rest / line_width
                                ratio_new = [ratio_new[0], ratio_key]
                                ratio_aside = [ratio_key, ratio_old[1]]
                # 最后比较预留空间
                else:
                    ratio_used_0 = [ratio_old[0], ratio_old[0] + ratio_width]
                    ratio_used_1 = [ratio_old[1] - ratio_width, ratio_old[1]]
                    ratio_new_0 = compute_diff_ratio(ratio_old, ratio_used_0)
                    ratio_new_1 = compute_diff_ratio(ratio_old, ratio_used_1)
                    ratio_aside = ratio_used_0
                    ratio_new = ratio_new_0
                    if ratio_new_1[1] - ratio_new_1[0] > ratio_new_0[1] - ratio_new_0[0]:
                        ratio_aside = ratio_used_1
                        ratio_new = ratio_new_1
                # 计算占用
                if len(ratio_new) > 0:
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width, group_depth - dlt_pass, ratio_new, merge_type, max_pass, min_pass)
                    suit_width_best = line_width * (suit_ratio_best[1] - suit_ratio_best[0])
                    if suit_width > group_width + MID_GROUP_PASS * 2 > suit_width_best:
                        suit_ratio_best = suit_ratio[:]
                else:
                    continue
                # 占用限制无法满足
                if suit_width < min(group_width, group_width_min + MIN_GROUP_PASS * 2):
                    continue
                # 避让参数
                if line_idx not in param_aside_temp:
                    param_aside_temp[line_idx] = {}
                param_aside_temp[line_idx][param_idx] = ratio_aside
            # 碰撞判断
            elif len(line_used) > 0:
                if line_idx in line_face:
                    depth_rest = line_face[line_idx]
                    if depth_rest <= 0:
                        pass
                    elif depth_rest < min(group_depth, 2.0):
                        continue
                line_new, ratio_new, width_new, depth_new = line_one, suit_ratio, group_width, group_depth
                # 碰撞计算
                suit_once = True
                for used_idx, param_list in line_used.items():
                    line_old = line_list[used_idx]
                    param_old = param_list[0]
                    group_old = param_old['group'][0]
                    # 无法碰撞
                    ratio_old, width_old, depth_old = param_old['ratio'][:], param_old['width'], param_old['depth']
                    width_old_min = width_old
                    if group_old['type'] in GROUP_PAIR_FUNCTIONAL:
                        if 'size_min' in group_old:
                            width_old_min = group_old['size_min'][0]
                        width_rest_old = param_old['width_rest']
                        if 'type_swap' in param_old and param_old['type_swap'] >= 1:
                            width_old += min(max(width_rest_old * 1.0, 0), width_old * 0.5)
                        elif width_old < 2 or (width_old < 3 and room_area > MID_ROOM_AREA_LIVING):
                            width_old += min(max(width_rest_old * 1.0, 0), width_old * 0.5)
                        depth_rest_old = param_old['depth_rest']
                        if 'type_swap' in param_old and param_old['type_swap'] > 0 and 'depth_swap' in param_old:
                            depth_old = param_old['depth_swap'] + MIN_GROUP_PASS
                        elif abs(ang_to_ang(line_new['angle'] - line_old['angle'] - math.pi)) <= 0.1:
                            depth_rest_max = MID_GROUP_PASS * 1
                            depth_old += max(min(depth_rest_old, depth_rest_max), MIN_GROUP_PASS)
                        else:
                            depth_rest_max = MID_GROUP_PASS * 2
                            depth_old += max(min(depth_rest_old, depth_rest_max), MIN_GROUP_PASS)
                        # 深度更新
                        depth_new = group_depth
                    elif group_old['type'] in ['Bath']:
                        # 深度更新
                        depth_rest_old = param_old['depth_rest']
                        if depth_rest_old > MID_GROUP_PASS * 3:
                            depth_rest_old = MID_GROUP_PASS * 3
                        if depth_old >= MID_GROUP_PASS and width_old >= MID_GROUP_PASS / 2:
                            if 'code' in group_old and group_old['code'] >= 1100:
                                depth_old += 0
                            elif 'size_rest' in group_old:
                                size_rest_old = group_old['size_rest']
                                if depth_old < 1.5 and depth_rest_old > depth_old * 0.5:
                                    depth_old += 0
                                elif size_rest_old[1] < MIN_GROUP_PASS / 2 < size_rest_old[3] and depth_rest_old > 0:
                                    depth_old += depth_rest_old
                                elif size_rest_old[3] < MIN_GROUP_PASS / 2 < size_rest_old[1] and depth_rest_old > 0:
                                    depth_old += depth_rest_old
                                elif depth_rest_old < 0:
                                    depth_old += depth_rest_old
                        elif depth_rest_old > MID_GROUP_PASS and depth_rest_old + depth_old > 3:
                            depth_old += min(MID_GROUP_PASS * 1, depth_rest_old)
                        elif abs(ang_to_ang(line_angle - line_old['angle'] - math.pi)) < 0.1:
                            depth_old += min(MID_GROUP_PASS * 2, depth_rest_old)
                        elif depth_rest_old > depth_old * 0.5:
                            depth_old += min(MIN_GROUP_PASS * 1, depth_rest_old)
                        elif 0 < depth_rest_old < depth_old * 0.5:
                            depth_old += depth_rest_old
                        if depth_rest_old <= 0:
                            width_new += MIN_GROUP_PASS * 2
                        # 宽度更新
                        width_rest_old = param_old['width_rest']
                        width_rest_add = MIN_GROUP_PASS * 1
                        if 'size_rest' in group_old:
                            size_rest_old = group_old['size_rest']
                            if 'code' in group_old and group_old['code'] >= 1100:
                                width_rest_add = min(MIN_GROUP_PASS * 1.0, width_rest_old)
                            elif min(size_rest_old[1], size_rest_old[3]) > MIN_GROUP_PASS:
                                width_rest_add = min(MIN_GROUP_PASS * 0.5, width_rest_old)
                            elif size_rest_old[1] < MIN_GROUP_PASS / 2 < size_rest_old[3]:
                                width_rest_dif = max(abs(size_rest_old[3] - size_rest_old[1]), MIN_GROUP_PASS * 1)
                                width_rest_add = min(width_rest_dif, width_rest_old)
                            elif size_rest_old[3] < MIN_GROUP_PASS / 2 < size_rest_old[1]:
                                width_rest_dif = max(abs(size_rest_old[3] - size_rest_old[1]), MIN_GROUP_PASS * 1)
                                width_rest_add = min(width_rest_dif, width_rest_old)
                            elif width_rest_old > MIN_GROUP_PASS * 5 and room_area > 8:
                                width_rest_add = MIN_GROUP_PASS * 5
                            elif width_rest_old > MIN_GROUP_PASS * 4 and room_area > 6:
                                width_rest_add = MIN_GROUP_PASS * 4
                            elif width_rest_old > MIN_GROUP_PASS * 3:
                                width_rest_add = MIN_GROUP_PASS * 3
                            elif width_rest_old > MIN_GROUP_PASS * 2:
                                width_rest_add = MIN_GROUP_PASS * 2
                            if width_rest_add > MID_GROUP_PASS * 2:
                                width_rest_add = MID_GROUP_PASS * 2
                            width_old += width_rest_add
                        # 深度更新
                        if room_area >= 8:
                            depth_new = group_depth + MID_GROUP_PASS
                        elif room_area >= 4:
                            depth_new = group_depth + MIN_GROUP_PASS
                    center_old = (ratio_old[0] + ratio_old[1]) / 2
                    ratio_old_best = ratio_old
                    if 'ratio_swap' in param_old and len(param_old['ratio_swap']) > 0:
                        ratio_old_best = param_old['ratio_swap']
                    elif 'ratio_best' in param_old and len(param_old['ratio_best']) > 0:
                        ratio_old_best = param_old['ratio_best']
                    width_old_best = line_old['width'] * (ratio_old_best[1] - ratio_old_best[0])
                    if min(width_old * 0.8, 2) < width_old_best < width_old * 1.0:
                        width_old = width_old_best
                        ratio_old = ratio_old_best
                    # 无法碰撞
                    suit_once, impact_once, ratio_new_ex, ratio_old_ex, distance_impact, depth_impact = \
                        compute_line_impact(line_new, ratio_new, width_new, depth_new,
                                            line_old, ratio_old, width_old, depth_old, ratio_old_best)
                    if suit_once and not impact_once:
                        if distance_impact >= 0 and depth_impact > group_depth:
                            suit_depth = min(suit_depth, depth_impact)
                            suit_depth_best = min(suit_depth_min, depth_impact)
                        break
                    elif suit_once and line_new == line_old:
                        suit_ratio = ratio_new_ex[:]
                        suit_ratio_best = ratio_new_ex[:]
                        break
                    ratio_aside = []
                    # 避让正对
                    if group_old['type'] in GROUP_PAIR_FUNCTIONAL:
                        if 'ratio_pair' in param_old and len(param_old['ratio_pair']) > 0:
                            ratio_aside = param_old['ratio_pair'][:]
                        elif 'ratio_best' in param_old and len(param_old['ratio_best']) > 0:
                            ratio_aside = param_old['ratio_best'][:]
                    # 避让进门
                    elif (len(door_pt_cook) > 0 and group_type == 'Dining') or \
                            (len(door_pt_entry) > 0 and group_type == 'Toilet'):
                        if group_type == 'Dining':
                            door_pt = door_pt_cook
                            width_add = MIN_GROUP_PASS
                            dis1, dis2, dis3 = compute_line_distance(line_old, ratio_old, door_pt, group_depth / 2, 1)
                            if dis1 >= dis2:
                                ratio_aside = [ratio_old[0], ratio_old[0] + (width_old + width_add) / line_old['width']]
                            else:
                                ratio_aside = [ratio_old[1] - (width_old + width_add) / line_old['width'], ratio_old[1]]
                        elif group_type == 'Toilet':
                            door_pt = door_pt_entry
                            width_add = MIN_GROUP_PASS
                            dis1, dis2, dis3 = compute_line_distance(line_old, ratio_old, door_pt, 0, 1)
                            if dis1 > dis2 + MIN_GROUP_PASS:
                                ratio_aside = [ratio_old[0], ratio_old[0] + (width_old + width_add) / line_old['width']]
                            elif dis2 > dis1 + MIN_GROUP_PASS:
                                ratio_aside = [ratio_old[1] - (width_old + width_add) / line_old['width'], ratio_old[1]]
                            else:
                                ratio_aside = [ratio_old[0], ratio_old[0] + (width_old + width_add) / line_old['width']]
                    # 避让碰撞
                    if len(ratio_aside) > 0:
                        if line_old['width'] * (ratio_aside[1] - ratio_aside[0]) < width_old:
                            center_aside = (ratio_aside[0] + ratio_aside[1]) / 2
                            if line_old['width'] * (ratio_aside[1] - ratio_old[0]) >= width_old and \
                                    center_aside < center_old - 0.1:
                                ratio_aside = [ratio_old[0], ratio_aside[1]]
                            elif line_old['width'] * (ratio_old[1] - ratio_aside[0]) >= width_old and \
                                    center_aside > center_old + 0.1:
                                ratio_aside = [ratio_aside[0], ratio_old[1]]
                            elif center_aside < center_old - 0.1:
                                ratio_aside[1] = ratio_old[0] + (width_old_min + MIN_GROUP_PASS) / line_old['width']
                            elif center_aside > center_old + 0.1:
                                ratio_aside[0] = ratio_old[1] - (width_old_min + MIN_GROUP_PASS) / line_old['width']
                        if line_old['width'] * (ratio_aside[1] - ratio_aside[0]) >= width_old_min:
                            if group_type in ['Toilet']:
                                suit_once, impact_once, ratio_old_ex, ratio_new_ex, distance_impact, depth_impact = \
                                    compute_line_impact(line_old, ratio_aside, width_old, depth_old,
                                                        line_new, ratio_new, width_new, depth_new)
                                if suit_once:
                                    if ratio_aside[0] <= 0.01 and ratio_old_ex[0] >= 0.01:
                                        suit_once = False
                                    elif ratio_aside[1] >= 0.99 and ratio_old_ex[1] <= 0.99:
                                        suit_once = False
                                if suit_once:
                                    if line_idx not in param_aside_temp:
                                        param_aside_temp[line_idx] = {}
                                    if used_idx not in param_aside_temp:
                                        param_aside_temp[used_idx] = {}
                                    param_aside_temp[line_idx][0] = ratio_new_ex[:]
                                    param_aside_temp[used_idx][0] = ratio_aside[:]
                                    break
                                else:
                                    break
                            else:
                                suit_once, impact_once, ratio_new_ex, ratio_old_ex, distance_impact, depth_impact = \
                                    compute_line_impact(line_new, ratio_new, width_new, depth_new,
                                                        line_old, ratio_aside, width_old_min, depth_old)
                                if suit_once and not impact_once:
                                    if line_idx not in param_aside_temp:
                                        param_aside_temp[line_idx] = {}
                                    if used_idx not in param_aside_temp:
                                        param_aside_temp[used_idx] = {}
                                    param_aside_temp[line_idx][0] = ratio_new_ex[:]
                                    param_aside_temp[used_idx][0] = ratio_aside[:]
                                    if suit_depth > group_depth and suit_depth > depth_impact > group_depth:
                                        suit_depth = depth_impact
                                        suit_depth_best = min(suit_depth_best, suit_depth)
                                    break
                    # 避让空间
                    suit_once, impact_once, ratio_new_ex, ratio_old_ex, distance_impact, depth_impact = \
                        compute_line_impact(line_new, ratio_new, width_new, depth_new,
                                            line_old, ratio_old, width_old, depth_old)
                    if not suit_once:
                        if depth_impact > group_depth and distance_impact > 0:
                            more_depth = max(depth_impact, group_depth + distance_impact)
                            suit_depth = min(more_depth, suit_depth)
                            suit_depth_min = min(more_depth, suit_depth_min)
                        break
                    if impact_once:
                        if line_idx not in param_aside_temp:
                            param_aside_temp[line_idx] = {}
                        if used_idx not in param_aside_temp:
                            param_aside_temp[used_idx] = {}
                        param_aside_temp[line_idx][0] = ratio_new_ex[:]
                        param_aside_temp[used_idx][0] = ratio_old_ex[:]
                        if suit_depth > group_depth and suit_depth > depth_impact:
                            suit_depth = depth_impact
                            suit_depth_best = min(suit_depth_best, suit_depth)
                        break
                # 碰撞排除
                if not suit_once:
                    continue
            # 靠边判断
            if suit_width_best > min(max(group_width, 0.5), 1.0) and group_type in ['Bath']:
                depth_all, depth_cur = line_one['depth_all'], 0
                for depth_one in depth_all:
                    if depth_one[0] <= suit_ratio_best[0] + 0.01 < suit_ratio_best[1] - 0.01 < depth_one[1]:
                        depth_cur = depth_one[2]
                        break
                    elif depth_one[0] >= suit_ratio_best[1]:
                        break
                if len(door_pt_entry) > 0:
                    dis1, dis2, dis3 = compute_line_distance(line_one, suit_ratio, door_pt_entry, group_depth / 2, 1)
                    if dis1 > dis2 and abs(suit_ratio_best[0] - 0) < abs(1 - suit_ratio_best[1]):
                        suit_ratio = suit_ratio_best[:]
                        suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                        suit_width_best = suit_width
                        if depth_cur >= suit_depth:
                            suit_depth, suit_depth_best = depth_cur, depth_cur
                    elif dis2 > dis1 and abs(suit_ratio_best[0] - 0) > abs(1 - suit_ratio_best[1]):
                        suit_ratio = suit_ratio_best[:]
                        suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                        suit_width_best = suit_width
                        if depth_cur >= suit_depth:
                            suit_depth, suit_depth_best = depth_cur, depth_cur
            # 打印分数
            suit_print = False
            if 'Library' in room_type and group_type in ['Work'] and False:
                suit_print = True

            # 位置分数
            score_place = 0
            group_width_well = group_width + MIN_GROUP_PASS * 2
            group_depth_well = group_depth + MIN_GROUP_PASS * 2
            if group_type in ['Media', 'Work']:
                group_width_well = group_width + MIN_GROUP_PASS * 4
            elif group_type in ['Dining']:
                if group_width > group_width_min + MIN_GROUP_PASS * 2:
                    group_width_well = group_width + MIN_GROUP_PASS * 2
                elif group_width < group_width_min + MIN_GROUP_PASS * 1:
                    group_width_well = group_width + MIN_GROUP_PASS * 1
                else:
                    group_width_well = group_width + MIN_GROUP_PASS * 0
            elif group_type in ['Bath']:
                if group_width > group_width_min + MIN_GROUP_PASS * 2:
                    group_width_well = group_width + MIN_GROUP_PASS * 0
                else:
                    group_width_well = group_width + MIN_GROUP_PASS * 2
            # 挡门处理
            for side_idx in [-1, 1]:
                side_type, side_type2, side_room, side_room2 = 0, 0, '', ''
                side_width, side_depth, side_flag = 0, 0, False
                if side_idx == -1:
                    line_side, line_side2 = line_pre, line_pre2
                    side_index, side_score = line_idx_pre, line_one['score_pre']
                    side_type, side_type2 = line_side['type'], line_side2['type']
                    side_width, side_depth = line_side['width'], line_side['depth']
                else:
                    line_side, line_side2 = line_post, line_post2
                    side_index, side_score = line_idx_post, line_one['score_post']
                    side_type, side_type2 = line_side['type'], line_side2['type']
                    side_width, side_depth = line_side['width'], line_side['depth']
                if 'unit_to_type' in line_side:
                    side_room = line_side['unit_to_type']
                if 'unit_to_type' in line_side2:
                    side_room2 = line_side2['unit_to_type']
                if side_type in [UNIT_TYPE_DOOR] and side_score == 1:
                    if group_type in ['Dining'] and side_room in ['Kitchen']:
                        pass
                    else:
                        side_flag = True
                elif side_type in [UNIT_TYPE_AISLE] and side_score == 1:
                    if side_depth < max(UNIT_WIDTH_HOLE, group_depth_min + MIN_GROUP_PASS):
                        side_flag = True
                elif side_type in [UNIT_TYPE_SIDE] and side_type2 in [UNIT_TYPE_DOOR]:
                    if side_width > UNIT_DEPTH_CURTAIN + 0.01 and side_score == 1:
                        side_flag = True
                        side_type, side_room = side_type2, side_room2
                elif side_type in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW] and side_type2 in [UNIT_TYPE_DOOR]:
                    if line_type in [UNIT_TYPE_WINDOW] and line_width < side_width:
                        pass
                    elif side_idx == -1 and suit_ratio[0] < 0 - 0.1 and line_width < group_width:
                        side_flag = True
                        side_type, side_room = side_type2, side_room2
                    elif side_idx == 1 and suit_ratio[1] > 1 + 0.1 and line_width < group_width:
                        side_flag = True
                        side_type, side_room = side_type2, side_room2
                #
                if side_flag:
                    if group_type in ['Meeting', 'Bed', 'Dining']:
                        if side_type in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE]:
                            if suit_width < min(group_width, 5):
                                depth_ext_well = group_depth
                                if group_type in ['Bed']:
                                    depth_ext_well = max(group_depth_min + MID_GROUP_PASS, 3.0)
                                if score_pre_new == 1:
                                    depth_ext_side = line_pre['depth_ext']
                                    if len(depth_ext_side) >= 1 and depth_ext_side[-1][2] < depth_ext_well:
                                        score_place -= 2
                                if score_post_new == 1:
                                    depth_ext_side = line_post['depth_ext']
                                    if len(depth_ext_side) >= 1 and depth_ext_side[0][2] < depth_ext_well:
                                        score_place -= 2
                            elif suit_width < group_width + MID_GROUP_PASS * 2:
                                if line_pre['depth'] < group_depth and score_pre_new <= 1:
                                    score_place -= 1
                                if line_post['depth'] < group_depth and score_post_new <= 1:
                                    score_place -= 1
                    elif group_type in ['Work', 'Bath']:
                        if side_type in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE, UNIT_TYPE_SIDE]:
                            if suit_width < min(group_width, 2.0):
                                score_place -= 2

            # 靠门处理
            if len(door_pt_entry) > 0:
                dis1, dis2, dis3 = compute_line_distance(line_one, [0, 1], door_pt_entry, depth=group_depth * 0, mode=1)
                dis4, dis5, dis6 = compute_line_distance(line_one, [0, 1], door_pt_entry, depth=group_depth / 2, mode=1)
                dis7, dis8, dis9 = compute_line_distance(line_one, [0, 1], door_pt_entry, depth=group_depth * 1, mode=1)
                dis_door_limit = MID_GROUP_PASS * 1.5
                if room_type in ROOM_TYPE_LEVEL_1 and room_area > MAX_ROOM_AREA_LIVING:
                    dis_door_limit = MID_GROUP_PASS * 2.0
                elif room_type in ROOM_TYPE_LEVEL_1 and room_area < MID_ROOM_AREA_LIVING:
                    dis_door_limit = MID_GROUP_PASS * 1.0
                elif room_type in ROOM_TYPE_LEVEL_3:
                    dis_door_limit = MID_GROUP_PASS * 0.5
                dis_door_inner = compute_point_inner(line_one['p1'], line_one['p2'], door_pt_entry)
                if dis_door_inner <= -0.1:
                    pass
                else:
                    if min(dis1, dis2, dis3) < dis_door_limit or min(dis4, dis5, dis6) < dis_door_limit or min(dis7, dis8, dis9) < dis_door_limit:
                        if group_type in ['Meeting']:
                            if max(dis4, dis5, dis6) - suit_width > dis_door_limit:
                                pass
                            else:
                                if suit_width < group_width_well:
                                    if dis4 < dis_door_limit and line_one['score_pre'] in [1, 4]:
                                        score_place -= 2
                                    if dis5 < dis_door_limit and line_one['score_post'] in [1, 4]:
                                        score_place -= 2
                        elif group_type in ['Dining'] and room_type not in ['DiningRoom']:
                            if max(dis4, dis5, dis6) - suit_width > dis_door_limit:
                                pass
                            else:
                                if suit_width < group_width_well:
                                    if dis4 < dis_door_limit and line_one['score_pre'] in [1, 4]:
                                        score_place -= 2
                                    if dis5 < dis_door_limit and line_one['score_post'] in [1, 4]:
                                        score_place -= 2
                        elif group_type in ['Bed'] and group_width < group_depth:
                            if min(dis1, dis2, dis3) < dis_door_limit:
                                score_place -= 2
                        elif suit_width < group_width_well:
                            if dis4 < dis_door_limit and line_one['score_pre'] in [1, 4]:
                                score_place -= 2
                            if dis5 < dis_door_limit and line_one['score_post'] in [1, 4]:
                                score_place -= 2
            # 凹陷处理
            sink_flag, sink_rest = False, MIN_GROUP_PASS * 2
            if suit_depth_best > group_depth + max(room_area / 10, MAX_GROUP_PASS) and group_type in ['Meeting']:
                sink_flag = False
            elif score_pre_new + score_post_new >= 8 and line_one['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                if group_type in ['Meeting']:
                    if 5 > suit_width > min(group_width + sink_rest * 2, group_width_min + sink_rest * 4, 3.0):
                        if suit_width_best > min(group_width_min, 3):
                            if min(group_depth + MIN_GROUP_PASS, 3) < suit_depth < max(group_depth + MAX_GROUP_PASS, 5):
                                sink_flag = True
                elif group_type in ['Bed']:
                    if line_width > min(group_width + sink_rest * 2, 2.5) and suit_width > 2.0:
                        if line_pre['width'] > UNIT_DEPTH_GROUP and line_post['width'] > UNIT_TYPE_GROUP:
                            sink_flag = True
                        elif line_pre['width'] > group_depth or line_post['width'] > group_depth:
                            sink_flag = True
                    elif line_width < min(group_width + sink_rest, 2.5):
                        score_place -= 2
                elif group_type in ['Dining']:
                    if line_idx_pre in line_used or line_idx_post in line_used:
                        sink_flag = False
                    elif suit_width > group_width + sink_rest * 2 and suit_depth - group_depth > MID_GROUP_PASS:
                        sink_flag = True
                    elif line_width < group_width + MIN_GROUP_PASS:
                        score_place -= 6
                    elif line_width < group_width + MID_GROUP_PASS:
                        score_place -= 4
                    else:
                        score_place -= 2
            elif score_pre_new + score_post_new >= 8 and line_one['type'] in [UNIT_TYPE_DOOR]:
                if group_type in ['Dining']:
                    if line_width < group_width + MID_GROUP_PASS * 2 and room_type in ['DiningRoom']:
                        score_place -= 6
                    elif line_width < group_width + MID_GROUP_PASS:
                        score_place -= 4
                    else:
                        score_place -= 2
            elif score_pre_new + score_post_new >= 5 and line_one['type'] in [UNIT_TYPE_WALL]:
                if 5 > suit_width >= min(group_width + sink_rest * 2, 2.5) and group_type in ['Meeting', 'Bed']:
                    if suit_ratio[0] <= 0.01 or suit_ratio[1] >= 0.99:
                        sink_flag = True
            elif score_pre_new + score_post_new >= 5 and line_one['type'] == UNIT_TYPE_WINDOW:
                if 5 > suit_width >= min(group_width + sink_rest * 2, 2.0) and group_type in ['Work', 'Rest']:
                    if suit_ratio[0] <= 0.01 or suit_ratio[1] >= 0.99:
                        sink_flag = True
            if sink_flag:
                depth_pre, depth_post = line_one['depth_pre'], line_one['depth_post']
                depth_pre_more, depth_post_more = line_one['depth_pre_more'], line_one['depth_post_more']
                if max(depth_pre, depth_post) > line_width and score_pre_new + score_post_new == 8:
                    if line_type in [UNIT_TYPE_WINDOW] or \
                            (line_width > group_width and min(depth_pre, depth_post) > group_width_min):
                        score_place -= 2
                elif min(depth_pre_more, depth_post_more) > line_width and score_pre_new + score_post_new == 8:
                    if line_type in [UNIT_TYPE_WINDOW] or line_width > group_width:
                        score_place -= 2
                else:
                    if suit_ratio[0] <= 0 and line_one['score_pre'] >= 4:
                        side_depth = line_one['depth_pre']
                        if side_depth > max(group_depth_min, group_depth / 2):
                            if side_depth > min(group_depth, UNIT_DEPTH_ASIDE + 0.01):
                                if suit_width < min(group_width + sink_rest, 2.5):
                                    score_place += 0
                                else:
                                    score_place += 1
                    if suit_ratio[1] >= 1 and line_one['score_post'] >= 4:
                        side_depth = line_one['depth_post']
                        if side_depth > max(group_depth_min, group_depth / 2):
                            if side_depth > min(group_depth, UNIT_DEPTH_ASIDE + 0.01):
                                if suit_width < min(group_width + sink_rest, 2.5):
                                    score_place += 0
                                else:
                                    score_place += 1
            if line_width < min(group_width + 1.5, group_width * 1.5):
                if score_pre_new + score_post_new >= 8 and group_type in ['Meeting'] and suit_depth >= max(group_depth * 2, 5):
                    score_place -= 1
                    if line_width < group_width + MID_GROUP_PASS * 1:
                        score_place -= 1
                if line_one['score_pre'] >= 4 and line_pre['type'] in [UNIT_TYPE_DOOR]:
                    score_place -= 1
                    if line_width < group_width + MID_GROUP_PASS * 1:
                        score_place -= 1
                if line_one['score_post'] >= 4 and line_post['type'] in [UNIT_TYPE_DOOR]:
                    score_place -= 1
                    if line_width < group_width + MID_GROUP_PASS * 1:
                        score_place -= 1

            # 斜墙处理
            if determine_line_angle(line_one['angle']) < 0:
                if group_type == 'Bed':
                    score_place -= 4
                else:
                    score_place -= 4

            # 靠窗处理
            door_flag, window_flag, aisle_flag = 0, 0, 0
            if suit_ratio[0] <= 0.0 - 0.2 and line_pre['type'] in [UNIT_TYPE_DOOR]:
                door_flag += 1
            if suit_ratio[1] >= 1.0 + 0.2 and line_post['type'] in [UNIT_TYPE_DOOR]:
                door_flag += 1
            if line_type == UNIT_TYPE_WINDOW:
                window_flag = 2
            elif suit_ratio[0] <= 0.0 - 0.2 and line_pre['type'] in [UNIT_TYPE_WINDOW] and line_width < group_width_well:
                window_flag = 1
            elif suit_ratio[1] >= 1.0 + 0.2 and line_post['type'] in [UNIT_TYPE_WINDOW] and line_width < group_width_well:
                window_flag = 1
            if suit_ratio[0] <= 0.0 - 0.1 and score_pre == 2:
                aisle_flag += 1
            if suit_ratio[1] >= 1.0 + 0.1 and score_post == 2:
                aisle_flag += 1
            if (door_flag >= 1 or aisle_flag >= 1) and group_type in ['Meeting', 'Dining']:
                score_place -= 1
                if len(index_copy) > 0 and group_idx in [index_copy[1], index_copy[-1]]:
                    if line_idx not in line_used:
                        score_place -= 1
            elif line_one['type'] in [UNIT_TYPE_DOOR] and group_type in ['Dining']:
                if group_idx in [index_copy[1], index_copy[-1]]:
                    if line_idx in line_used:
                        pass
                    elif suit_depth > max(suit_width, group_depth, 3) and line_idx not in line_face:
                        pass
                    else:
                        score_place -= 1
            if window_flag >= 1:
                if group_type in ['Meeting']:
                    if line_width > UNIT_WIDTH_HOLE and len(unit_to_room) <= 0:
                        pass
                    else:
                        score_place -= 2
                    if line_one['score_pre'] == 4 and line_pre['type'] in [UNIT_TYPE_WINDOW]:
                        score_place -= 1
                    if line_one['score_post'] == 4 and line_post['type'] in [UNIT_TYPE_WINDOW]:
                        score_place -= 1
                    if line_one['score'] == 8 and line_width < group_width + MID_GROUP_PASS * 2:
                        score_place -= 2
                elif group_type in ['Bed']:
                    score_place -= 2
                    if window_flag >= 2:
                        score_place -= 2
                elif group_type in ['Dining']:
                    if line_width > UNIT_WIDTH_HOLE and unit_to_type in ['Balcony', 'Terrace'] and line_idx not in line_face:
                        score_place -= 2
                    if group_idx in [index_copy[1], index_copy[-1]] and line_idx in line_face:
                        score_place -= 1
                elif group_type in ['Work', 'Rest']:
                    if line_height < 0.1:
                        if room_type in ROOM_TYPE_LEVEL_1:
                            continue
                        else:
                            score_place -= 4
                    elif group_height > UNIT_HEIGHT_SHELF_MIN:
                        score_place -= 4
                    elif group_height > UNIT_HEIGHT_TABLE_MAX:
                        score_place -= 2
                    elif line_height >= UNIT_HEIGHT_WALL - 0.01 and line_width > UNIT_WIDTH_HOLE:
                        pass
                    elif line_width > group_width_min + MID_GROUP_PASS * 2:
                        score_place += 2
                elif group_type in ['Bath']:
                    if group_width_min < MID_GROUP_PASS:
                        score_place -= 4
                elif group_type in ['Toilet']:
                    if 1.5 > line_width > group_width and line_height > 0.2:
                        score_place += 1

            # 狭窄处理
            if group_type in ['Dining']:
                suit_width_side, suit_depth_side = suit_width, suit_depth_best
                suit_width_pass, suit_depth_pass = MID_GROUP_PASS, MID_GROUP_PASS
                if room_area > MAX_ROOM_AREA_LIVING * 2:
                    suit_width_pass, suit_depth_pass = MID_GROUP_PASS * 2, MID_GROUP_PASS * 2
                if line_idx in line_face:
                    suit_depth_pass = MIN_GROUP_PASS
                if suit_ratio[0] <= 0.01 and score_pre == 1 and type_pre in [UNIT_TYPE_AISLE]:
                    if line_pre['depth'] < group_depth + suit_depth_pass:
                        suit_width_side -= MID_GROUP_PASS
                    else:
                        suit_width_side += min(line_pre['width'], MID_GROUP_PASS)
                if suit_ratio[1] <= 0.99 and score_post == 1 and type_post in [UNIT_TYPE_AISLE]:
                    if line_post['depth'] < group_depth + suit_depth_pass:
                        suit_width_side -= MID_GROUP_PASS
                    else:
                        suit_width_side += min(line_post['width'], MID_GROUP_PASS)
                # width
                if suit_width_side < group_width + 0.1:
                    score_place -= 2
                    if line_idx in line_used:
                        score_place -= 1
                elif suit_width_side < group_width + suit_width_pass * 1:
                    if line_idx not in line_face:
                        score_place -= 1
                    if line_idx in line_used:
                        score_place -= 1
                if suit_width_side < group_width_min + suit_width_pass * 1:
                    score_place -= 2
                    if group_width_min + suit_width_pass < group_width:
                        score_place -= 2
                # depth
                if suit_depth_best < group_depth + 0.1:
                    score_place -= 2
                elif suit_depth_best < group_depth + suit_depth_pass * 1:
                    if line_idx not in line_face:
                        score_place -= 1
                if suit_depth_best < group_depth_min + suit_depth_pass * 2:
                    score_place -= 2
                    if group_depth_min + suit_depth_pass < group_depth:
                        score_place -= 2
            elif group_type in ['Bath']:
                if suit_depth_best > max(line_width, UNIT_WIDTH_HOLE) and line_width > suit_width:
                    score_place -= 1

            # 两侧处理
            line_aisle = 0
            if line_one['score_pre'] == 1 and suit_ratio[0] <= 0.1:
                if line_pre['type'] in [UNIT_TYPE_SIDE] and line_pre['width'] > UNIT_DEPTH_CURTAIN + 0.01:
                    line_aisle += 1
            elif suit_ratio[0] > 0.5:
                line_aisle += 1
            if line_one['score_post'] == 1 and suit_ratio[1] >= 0.9:
                if line_post['type'] in [UNIT_TYPE_SIDE] and line_post['width'] > UNIT_DEPTH_CURTAIN + 0.01:
                    line_aisle += 1
            elif suit_ratio[1] < 0.5:
                line_aisle += 1
            if line_aisle >= 1:
                if group_type in ['Meeting', 'Bed', 'Dining'] and line_width < group_width + 2:
                    score_place -= line_aisle
                elif group_type in ['Toilet'] and line_width < group_width + 1:
                    score_place -= line_aisle
            # 碰撞处理
            if line_idx in line_used and len(suit_ratio) >= 2:
                suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                if suit_width < min(group_width + 0.2, group_width * 1.1):
                    score_place -= 2
                elif suit_width < min(group_width + 0.4, group_width * 1.2):
                    score_place -= 1
            elif line_idx in param_aside_temp:
                ratio_new = param_aside_temp[line_idx][0]
                width_new = line_width * (ratio_new[1] - ratio_new[0])
                if group_type in ['Dining']:
                    if width_new < group_width_min + MID_GROUP_PASS * 2:
                        if group_idx in [index_copy[1], index_copy[-1]]:
                            score_place -= 0
                        else:
                            score_place -= 1
                    elif width_new < group_width_min + MID_GROUP_PASS * 1:
                        score_place -= 2
                elif group_type in ['Toilet'] and len(line_old) > 0:
                    if abs(ang_to_ang(line_angle - line_old['angle'] - math.pi)) < 0.1:
                        if width_new < group_width_min + MID_GROUP_PASS * 2:
                            score_place -= 1
                        elif width_new < group_width_min + MID_GROUP_PASS * 1:
                            score_place -= 2
            if line_idx in line_face:
                if line_face[line_idx] > group_depth + MID_GROUP_PASS:
                    score_place += 1

            # 距离分数 进门距离 厨房距离 厕所距离
            score_distance = 0
            suit_distance_entry, suit_distance_limit = 0, 6
            suit_distance_cook, suit_distance_bath, suit_distance_sofa, suit_distance_open = 0, 0, 0, 0
            if room_area > MID_ROOM_AREA_LIVING * 2:
                suit_distance_limit = 9
            if group_type in ['Dining'] and room_type not in ['DiningRoom']:
                well_ratio = suit_ratio_best[:]
                # 厨房距离
                if len(door_pt_cook) > 0:
                    dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_cook, group_depth / 2, 1)
                    dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_cook, group_depth * 1, 1)
                    suit_distance_cook = max(suit_distance_limit - min(dis1, dis2, dis3, dis4, dis5, dis6), 0)
                    if unit_to_type in ['Kitchen']:
                        suit_distance_cook = max(suit_distance_limit - min(dis4, dis5, dis6), 0)
                # 浴室距离
                if len(door_pt_bath) > 0:
                    dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_bath, group_depth * 0, 1)
                    dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_bath, group_depth / 2, 1)
                    suit_distance_bath = min(dis1, dis2, dis3, dis4, dis5, dis6, 3)
                # 沙发距离
                if len(line_used) > 0 and room_area > MAX_ROOM_AREA_LIVING:
                    line_sofa, ratio_sofa, depth_sofa, angle_sofa = {}, 0.5, 3, 0
                    for used_idx, used_val in line_used.items():
                        if len(used_val) > 0:
                            para_sofa = used_val[0]
                            line_sofa = line_list[used_idx]
                            if 'ratio_best' in para_sofa and len(para_sofa['ratio_best']) >= 2:
                                ratio_best = para_sofa['ratio_best']
                                ratio_sofa = (ratio_best[0] + ratio_best[1]) / 2
                            if 'depth' in para_sofa:
                                depth_sofa = para_sofa['depth']
                            angle_sofa = line_sofa['angle'] + math.pi / 2
                            break
                    if len(line_sofa) > 0:
                        tmp_x, tmp_z = 0, depth_sofa * 1
                        add_x = tmp_z * math.sin(angle_sofa) + tmp_x * math.cos(angle_sofa)
                        add_z = tmp_z * math.cos(angle_sofa) - tmp_x * math.sin(angle_sofa)
                        used_p1, used_p2 = line_sofa['p1'], line_sofa['p2']
                        used_p0 = [used_p1[0] * (1 - ratio_sofa) + used_p2[0] * ratio_sofa + add_x,
                                   used_p1[1] * (1 - ratio_sofa) + used_p2[1] * ratio_sofa + add_z]
                        dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, used_p0, group_depth * 0.0, 2)
                        dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, used_p0, group_depth * 0.5, 2)
                        suit_distance_sofa = min(dis1, dis2, dis3, dis4, dis5, dis6, 6)
                score_distance += suit_distance_cook * 0.5
                score_distance += suit_distance_bath * 0.5
                score_distance += suit_distance_sofa * 0.5
            elif group_type in ['Meeting', 'Bed', 'Bath', 'Toilet']:
                well_ratio = suit_ratio[:]
                if group_type in ['Meeting']:
                    if line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                        if suit_width > max(group_width, 3) and suit_width_best > 1.5:
                            well_ratio = suit_ratio_best[:]
                elif group_type in ['Bed']:
                    well_ratio[0] = max(well_ratio[0], 0)
                    well_ratio[1] = min(well_ratio[1], 1)
                # 进门距离
                if group_type in ['Meeting'] and len(door_pt_entry) > 0:
                    dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_entry, group_depth / 2, 1)
                    dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_entry, suit_depth / 2, 1)
                    suit_distance_entry = min(max(dis1, dis2) - group_width, max(dis4, dis5) - group_width, suit_distance_limit)
                    if suit_depth > max(group_depth + 2, 5):
                        face_depth = max(group_depth + 1, suit_depth * 0.5)
                        dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_entry, face_depth, 1)
                        suit_distance_entry = min(max(dis4, dis5) - group_width, suit_distance_limit)
                    elif line_width > max(group_depth + 2, 5) and line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                        face_depth = max(group_depth + 1, suit_depth * 0.5)
                        dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_entry, face_depth, 1)
                        suit_distance_entry = min(max(dis4, dis5) - group_width, suit_distance_limit)
                elif group_type in ['Bed'] and len(door_pt_entry) > 0:
                    dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_entry, 0, 1)
                    suit_distance_entry = max(dis1, dis2)
                elif group_type in ['Bath'] and len(door_pt_entry) > 0:
                    well_depth = min(suit_depth * 1.0, group_depth + 1.0, min(0.4 * room_area, 2.0))
                    dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_entry, 0, 1)
                    dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_entry, well_depth, 1)
                    suit_distance_entry = min(max(dis1, dis2, dis4, dis5), 0.8 * room_area)
                elif group_type in ['Toilet'] and len(door_pt_entry) > 0:
                    well_depth = min(suit_depth * 1.0, group_depth + 0.4, min(0.4 * room_area, 2.0))
                    if suit_width_best > group_width:
                        well_ratio = suit_ratio_best
                    if len(ratio_new_ex) >= 2 and ratio_new_ex[0] >= suit_ratio[0] and ratio_new_ex[1] <= suit_ratio[1]:
                        well_ratio = ratio_new_ex
                    dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_entry, 0, 1)
                    dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_entry, well_depth, 1)
                    suit_distance_entry = min(max(dis1, dis2, dis4, dis5), 0.8 * room_area)
                # 厨房距离 阳台距离
                if group_type in ['Meeting']:
                    door_pt_main = door_pt_entry[:]
                    if len(door_pt_cook) > 0 and len(door_pt_entry) > 0:
                        if abs(door_pt_entry[0] - door_pt_cook[0]) + abs(door_pt_entry[1] - door_pt_cook[1]) < 0.1:
                            door_pt_main = []
                    if len(door_pt_bath) > 0 and len(door_pt_entry) > 0:
                        if abs(door_pt_entry[0] - door_pt_bath[0]) + abs(door_pt_entry[1] - door_pt_bath[1]) < 0.1:
                            door_pt_main = []
                    if len(door_pt_main) <= 0 or (len(door_pt_cook) > 0 and len(door_pt_open) > 0):
                        if len(door_pt_cook) > 0 and (room_area > MID_ROOM_AREA_LIVING or len(door_pt_open) > 0):
                            dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_cook, 0, 1)
                            dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_cook, group_depth, 1)
                            suit_distance_cook = min(dis1, dis2, dis3, dis4, dis5, dis6, suit_distance_limit)
                        if len(door_pt_open) > 0 and room_area < 50:
                            dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_open, 0, 1)
                            dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_open, group_depth, 1)
                            if suit_depth > max(group_depth + 2, 5) or line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                                face_depth = max(group_depth + 1, suit_depth * 0.5)
                                dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_open, face_depth, 1)
                            suit_distance_open = max(6 - min(dis1, dis2, dis3, dis4, dis5, dis6), 0)
                    elif len(door_pt_cook) > 0 and room_area > MID_ROOM_AREA_LIVING:
                        dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_cook, 0, 1)
                        dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_cook, group_depth, 1)
                        suit_distance_cook = min(dis1, dis2, dis3, dis4, dis5, dis6, suit_distance_limit)
                        if len(door_pt_open) <= 0:
                            suit_distance_open = suit_distance_cook
                    elif len(door_pt_cook) <= 0 and len(door_pt_open) > 0 and room_area < 50:
                        dis1, dis2, dis3 = compute_line_distance(line_one, well_ratio, door_pt_open, group_depth / 2, 1)
                        dis4, dis5, dis6 = compute_line_distance(line_one, well_ratio, door_pt_open, group_depth, 1)
                        suit_distance_open = max(6 - min(dis1, dis2, dis3, dis4, dis5, dis6), 0)
                score_distance += suit_distance_entry * 1.0
                score_distance += suit_distance_cook * 0.5
                score_distance += suit_distance_open * 0.5
            # 尺寸分数
            score_width, score_depth = 0, 0
            group_width_well, group_depth_well = group_width, group_depth
            if group_type in ['Dining']:
                group_width_well = group_width + MID_GROUP_PASS * 1
                group_depth_well = group_depth + MID_GROUP_PASS * 0
                if group_idx in [index_copy[1], index_copy[-1]]:
                    group_width_well = group_width + MID_GROUP_PASS * 0
                    group_depth_well = group_depth + MID_GROUP_PASS * 1
                if 'size_rest' in group_one:
                    size_rest = group_one['size_rest']
                    if size_rest[0] < 0.1 < size_rest[2]:
                        group_depth_well += (size_rest[2] - size_rest[0])
            # 尺寸处理
            group_width_seed, group_width_pair = group_width_min, 1.5
            if 'seed_size_new' in group_one:
                group_width_seed = group_one['seed_size_new'][0]
            if group_idx < len(group_pair):
                if 'seed_size_new' in group_pair[group_idx]:
                    group_width_pair = group_pair[group_idx]['seed_size_new'][0]
                else:
                    group_width_pair = group_pair[group_idx]['size'][0]
            # 宽度处理
            if group_type in ['Meeting', 'Bed', 'Media']:
                if line_type in [UNIT_TYPE_WALL]:
                    if room_area > MID_ROOM_AREA_LIVING * 2:
                        score_width = suit_width
                    elif suit_width > max(group_width_min + MID_GROUP_PASS * 2, group_width + MID_GROUP_PASS * 1):
                        score_width = max(group_width_min + MID_GROUP_PASS * 2, group_width + MID_GROUP_PASS * 1)
                    else:
                        score_width = suit_width
                else:
                    if suit_width > min(group_width_min + MIN_GROUP_PASS * 2, group_width + MIN_GROUP_PASS * 1, 4):
                        score_width = min(group_width_min + MIN_GROUP_PASS * 2, group_width + MIN_GROUP_PASS * 1, 4)
                    else:
                        score_width = suit_width
                if group_width_pair > max(group_width, group_width_seed, suit_width_best):
                    score_width = suit_width_best
                    if suit_width > group_width or abs(suit_width_best - suit_width) < 0.1:
                        more_width = suit_width
                        if suit_ratio[0] > 0.01:
                            more_width += line_width * (suit_ratio[0] - 0)
                        if suit_ratio[0] >= 0:
                            if score_pre == 1 and line_pre['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE]:
                                more_width += line_pre['width']
                        if suit_ratio[1] < 0.99:
                            more_width += line_width * (1 - suit_ratio[1])
                        if suit_ratio[1] <= 1:
                            if score_post == 1 and line_post['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE]:
                                more_width += line_post['width']
                        score_width -= (more_width - group_width_pair)
                elif group_width_seed > suit_width + 0.1:
                    more_width = suit_width
                    if abs(suit_ratio[0] - 0) <= 0.1:
                        if score_pre == 1 and line_pre['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE] and line_pre['depth'] > group_depth_min:
                            more_width += line_pre['width']
                    if abs(suit_ratio[1] - 1) <= 0.1:
                        if score_post == 1 and line_post['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE] and line_post['depth'] > group_depth_min:
                            more_width += line_post['width']
                    score_width += (more_width - group_width_seed)
            elif group_type in ['Dining']:
                score_width = suit_width
                if score_width < group_width_well:
                    pass
                elif room_type in ['DiningRoom'] or suit_ratio[0] < -0.5 or suit_ratio[1] > 1.5:
                    score_width = group_width_well
                elif score_width > group_width_well:
                    score_width = group_width_well
            elif group_type in ['Work', 'Rest']:
                if suit_width > max(group_width, group_depth):
                    score_width = max(group_width, group_depth) + suit_width / 10
                else:
                    score_width = suit_width
            elif group_type in ['Bath']:
                score_width = suit_width
                if suit_width > group_width > 0.4:
                    score_width = min(suit_width, group_width + MIN_GROUP_PASS)
                elif suit_width < group_width + 0.1 and 'size_rest' in group_one:
                    size_rest = group_one['size_rest']
                    if size_rest[1] > 0.2 > 0.1 > size_rest[3] or size_rest[3] > 0.2 > 0.1 > size_rest[1]:
                        right_width = min(group_width + abs(size_rest[1] - size_rest[3]), 0.8)
                        score_width = suit_width + 2 * (suit_width - right_width)
            elif group_type in ['Toilet']:
                score_width = suit_width
                if suit_width >= group_width + MIN_GROUP_PASS * 2:
                    score_width = group_width + MIN_GROUP_PASS * 2
            # 深度处理
            min_pass, max_pass = MIN_GROUP_PASS, 1.5
            if group_type in GROUP_PAIR_FUNCTIONAL:
                score_depth = suit_depth
                if suit_depth >= 4.0 and line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                    score_depth = group_depth
                elif suit_depth > min(group_depth + 2, 5):
                    score_depth = min(group_depth + MID_GROUP_PASS * 1, suit_depth * 0.6)
                elif suit_depth > min(group_depth + 1, 4) and suit_width * suit_depth > room_area * 0.5:
                    score_depth = min(group_depth + MID_GROUP_PASS * 1, suit_depth * 0.6)
                else:
                    score_depth = group_depth + min(suit_depth - group_depth, MID_GROUP_PASS * 2)
            elif group_type in ['Dining']:
                score_depth = suit_depth
                if score_depth < group_depth_well:
                    pass
                elif group_depth_well <= score_depth <= group_depth_well + MID_GROUP_PASS:
                    score_depth = group_depth_well
                elif room_type in ['DiningRoom']:
                    score_depth = group_depth_well
                elif score_depth > group_depth_well:
                    score_depth = group_depth_well
            elif group_type in ['Work', 'Rest']:
                aside_depth = group_depth
                if line_one['score_pre'] == 4 and line_pre['type'] == UNIT_TYPE_WALL:
                    if aside_depth < line_pre['width']:
                        aside_depth = line_pre['width']
                if line_one['score_post'] == 4 and line_post['type'] == UNIT_TYPE_WALL:
                    if aside_depth < line_post['width']:
                        aside_depth = line_post['width']
                if aside_depth > group_depth + MIN_GROUP_PASS * 2:
                    score_depth = group_depth + MIN_GROUP_PASS * 2
                elif aside_depth >= group_depth:
                    score_depth = group_depth
                elif suit_depth >= group_depth:
                    score_depth = group_depth
                else:
                    score_depth = group_depth / 2
            elif group_type in ['Bath']:
                if group_width > group_depth > MID_GROUP_PASS > group_depth_min:
                    score_depth = min(suit_depth, 2.0)
                elif group_depth > MID_GROUP_PASS > group_depth_min:
                    well_depth = min(group_depth, 2.0)
                    score_depth = 0 - abs(suit_depth - well_depth)
                else:
                    well_depth = min(group_depth + 1.0, 1.5)
                    score_depth = 0 - abs(suit_depth - well_depth)
            # 优先分数
            score_prior = 0
            seed_position, seed_distance_rely, seed_distance_face = [], 10, 10
            if 'seed_position' in group_one and 'seed_rotation' in group_one:
                seed_position, seed_rotation = group_one['seed_position'], group_one['seed_rotation']
                seed_point = [seed_position[0], seed_position[2]]
                seed_angle = rot_to_ang(seed_rotation)
                # 角度判断
                seed_turn = 0
                seed_angle_dlt_1 = normalize_line_angle(line_angle + math.pi / 2 - seed_angle)
                seed_angle_dlt_2 = normalize_line_angle(line_angle - math.pi / 2 - seed_angle)
                if group_type in ['Meeting', 'Bed']:
                    if abs(seed_angle_dlt_1) < 0.01:
                        seed_turn = 0
                    elif abs(seed_angle_dlt_2) < 0.01:
                        seed_turn = 2
                    else:
                        seed_turn = -1
                # 距离判断
                dis1, dis2, dis3 = compute_line_distance(line_one, suit_ratio, seed_point, depth=group_depth / 2)
                dis4, dis5, dis6 = compute_line_distance(line_one, suit_ratio, seed_point, depth=group_depth / 2 + 1.5)
                seed_distance_rely = min(dis1, dis2, dis3)
                seed_distance_face = min(dis4, dis5, dis6)
                if seed_turn == 0 and seed_distance_rely < seed_distance_face:
                    score_prior += (10 - seed_distance_rely)
                elif seed_turn == 2 and suit_depth > group_depth + 1:
                    score_prior += (10 - seed_distance_face)
                else:
                    score_prior -= 10
            elif group_type in GROUP_PAIR_FUNCTIONAL and len(seed_pt_media) > 0:
                seed_point = [seed_pt_media[0], seed_pt_media[1]]
                # 距离判断
                dis1, dis2, dis3 = compute_line_distance(line_one, suit_ratio, seed_point, depth=suit_depth)
                score_prior += (10 - min(dis1, dis2, dis3))
            elif 'keep_position' in group_one and 'keep_rotation' in group_one and 'keep_role' in group_one:
                keep_role = group_one['keep_role']
                keep_position, keep_rotation = group_one['keep_position'], group_one['keep_rotation']
                keep_point = [keep_position[0], keep_position[2]]
                if keep_role in ['table', 'side sofa']:
                    dis1, dis2, dis3 = compute_line_distance(line_one, suit_ratio, keep_point, depth=group_depth_min)
                    dis4, dis5, dis6 = compute_line_distance(line_one, suit_ratio, keep_point, depth=suit_depth_best)
                    score_prior += (5 - min(dis1, dis2, dis3) - min(dis4, dis5, dis6))
            # 优先比例
            if len(seed_position) > 0:
                seed_ratio, seed_prior = suit_ratio[:], False
                seed_p0_z, line_p1_z, line_p2_z = seed_position[0], line_one['p1'][0], line_one['p2'][0]
                if 'seed_position' in group_one and 'seed_rotation' in group_one:
                    seed_position = group_one['seed_position']
                    # 比例判断
                    if determine_line_angle(line_angle) == 0:
                        seed_p0_z, line_p1_z, line_p2_z = seed_position[0], line_one['p1'][0], line_one['p2'][0]
                        seed_prior = True
                    elif determine_line_angle(line_angle) == 1:
                        seed_p0_z, line_p1_z, line_p2_z = seed_position[2], line_one['p1'][1], line_one['p2'][1]
                        seed_prior = True
                elif group_type in GROUP_PAIR_FUNCTIONAL and len(seed_pt_media) > 0:
                    # 比例判断
                    if determine_line_angle(line_angle) == 0:
                        seed_p0_z, line_p1_z, line_p2_z = seed_pt_media[0], line_one['p1'][0], line_one['p2'][0]
                        seed_prior = True
                    elif determine_line_angle(line_angle) == 1:
                        seed_p0_z, line_p1_z, line_p2_z = seed_pt_media[1], line_one['p1'][1], line_one['p2'][1]
                        seed_prior = True
                if seed_prior:
                    if line_p2_z - line_p1_z > 0:
                        seed_ratio[0] = ((seed_p0_z - group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                        seed_ratio[1] = ((seed_p0_z + group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                    elif line_p2_z - line_p1_z < 0:
                        seed_ratio[0] = ((seed_p0_z + group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                        seed_ratio[1] = ((seed_p0_z - group_width / 2) - line_p1_z) / (line_p2_z - line_p1_z)
                if suit_ratio[0] < (seed_ratio[0] + seed_ratio[1]) / 2 < suit_ratio[1]:
                    if suit_ratio[0] < seed_ratio[0] or suit_ratio[0] - 0.1 < seed_ratio[0]:
                        suit_ratio[0] = seed_ratio[0]
                    if suit_ratio[1] > seed_ratio[1] or suit_ratio[1] + 0.1 > seed_ratio[1]:
                        suit_ratio[1] = seed_ratio[1]
                    suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                    suit_ratio_best = suit_ratio[:]

            # 整体分数
            suit_score = score_place + score_distance + score_width + score_depth + score_prior
            if suit_print:
                print('group %02d line %02d score: %.2f %.2f %.2f %.2f %.2f = %.2f' %
                      (group_idx, line_idx, score_place, score_distance, score_width, score_depth, score_prior, suit_score))
            if suit_score <= param_best['score']:
                continue
            # 最佳参数
            param_best['index'] = line_idx
            param_best['score'] = suit_score
            param_best['vertical'] = 0
            param_best['width'] = group_width
            param_best['depth'] = group_depth
            param_best['depth_suit'] = suit_depth
            param_best['width_rest'] = suit_width - group_width
            param_best['depth_rest'] = suit_depth - group_depth
            param_best['ratio'] = suit_ratio[:]
            param_best['ratio_best'] = suit_ratio_best[:]
            # 避让参数
            param_aside[group_idx] = param_aside_temp
            # 靠墙参数
            if len(seed_position) > 0:
                if suit_depth > group_depth + 1.0 and seed_distance_face < seed_distance_rely:
                    group_one['seed_center'] = 1
                else:
                    group_one['seed_center'] = 0
        # 暂存布局
        group_idx_new = group_idx
        if group_idx in index_copy and int(param_best['index']) >= 0:
            param_add = param_best.copy()
            param_add['ratio'] = param_best['ratio'][:]
            param_add['ratio_best'] = param_best['ratio_best'][:]
            if group_idx in [index_copy[1], index_copy[-1]] and group_type in ['Dining']:
                param_add['vertical'] = 1
            param_copy[group_idx] = param_add
        if group_idx in index_copy:
            if len(index_copy) > 0 and index_copy[0] == group_idx:
                if int(param_best['index']) >= 0 and group_type in ['Bed']:
                    find_copy = True
                continue
            if not find_copy:
                for param_idx, param_one in param_copy.items():
                    line_idx_old = param_one['index']
                    if param_one['width_rest'] >= 0 and param_one['depth_rest'] >= 0 and line_idx_old not in line_used:
                        find_copy = True
                        break
            if find_copy or index_copy[-1] == group_idx:
                score_best, vertical_best = -100, 0
                param_best = {'index': -1}
                for param_idx, param_one in param_copy.items():
                    param_score, param_vertical = param_one['score'], param_one['vertical']
                    if param_score > score_best:
                        param_best = param_one
                        score_best = param_score
                        group_idx_new = param_idx
                    elif param_score == score_best and param_vertical <= param_best['vertical'] and \
                            param_one['depth_rest'] > param_one['width_rest']:
                        param_best = param_one
                        score_best = param_score
                        group_idx_new = param_idx
                group_one = group_sort[group_idx_new]
            else:
                continue
        # 调整布局
        if group_idx in index_copy:
            if 'width_rest' in param_best and param_best['width_rest'] < MID_GROUP_PASS:
                # 当前
                line_idx = param_best['index']
                line_one = line_list[line_idx]
                # 左右
                line_idx_pre = (line_idx - 1 + len(line_list)) % len(line_list)
                line_idx_post = (line_idx + 1 + len(line_list)) % len(line_list)
                line_idx_pre2 = (line_idx - 2 + len(line_list)) % len(line_list)
                line_idx_post2 = (line_idx + 2 + len(line_list)) % len(line_list)
                line_idx_pre3 = (line_idx - 3 + len(line_list)) % len(line_list)
                line_idx_post3 = (line_idx + 3 + len(line_list)) % len(line_list)
                line_pre, line_post = line_list[line_idx_pre], line_list[line_idx_post]
                line_pre2, line_post2 = line_list[line_idx_pre2], line_list[line_idx_post2]
                line_pre3, line_post3 = line_list[line_idx_pre3], line_list[line_idx_post3]
                ratio_one = param_best['ratio']
                width_add1, width_add2 = 0, 0
                if 0.00 <= ratio_one[0] <= 0.01:
                    width_add1 = 0
                    if line_one['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_DOOR]:
                        width_add1 = line_pre['width'] / 2
                    elif line_one['score_pre'] == 2 and line_pre['type'] in [UNIT_TYPE_WALL]:
                        if line_pre2['type'] == UNIT_TYPE_SIDE and line_pre2['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                            width_add1 = UNIT_WIDTH_DOOR * 0.5
                            if 'depth_all' in line_pre and len(line_pre['depth_all']) > 0:
                                depth_add = line_pre['depth_all'][-1][2]
                                if depth_add > width_add1:
                                    width_add1 = depth_add
                            width_add_max = UNIT_WIDTH_DOOR * 1.0
                            if width_add1 > width_add_max:
                                width_add1 = width_add_max
                        elif param_best['vertical'] >= 1:
                            width_add1 = UNIT_WIDTH_DOOR * 0.5
                            if 'depth_all' in line_pre and len(line_pre['depth_all']) > 0:
                                depth_add = line_pre['depth_all'][-1][2]
                                if depth_add > width_add1:
                                    width_add1 = depth_add
                            width_add_max = min(UNIT_WIDTH_DOOR * 1.0, (group_width - group_width_min) * 0.25)
                            if width_add1 > width_add_max:
                                width_add1 = width_add_max
                if 0.99 <= ratio_one[1] <= 1.00:
                    width_add2 = 0
                    if line_one['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_DOOR]:
                        width_add2 = line_post['width'] / 2
                    elif line_one['score_post'] == 2 and line_post['type'] in [UNIT_TYPE_WALL]:
                        if line_post2['type'] == UNIT_TYPE_SIDE and line_post2['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                            width_add2 = UNIT_WIDTH_DOOR * 0.5
                            if 'depth_all' in line_post and len(line_post['depth_all']) > 0:
                                depth_add = line_post['depth_all'][0][2]
                                if depth_add > width_add2:
                                    width_add2 = depth_add
                            width_add_max = UNIT_WIDTH_DOOR * 1.0
                            if width_add2 > width_add_max:
                                width_add2 = width_add_max
                        elif param_best['vertical'] >= 1:
                            width_add2 = UNIT_WIDTH_DOOR * 0.5
                            if 'depth_all' in line_post and len(line_post['depth_all']) > 0:
                                depth_add = line_post['depth_all'][0][2]
                                if depth_add > width_add2:
                                    width_add2 = depth_add
                            width_add_max = min(UNIT_WIDTH_DOOR * 1.0, (group_width - group_width_min) * 0.25)
                            if width_add2 > width_add_max:
                                width_add2 = width_add_max
                if width_add1 > width_add2 * 2:
                    width_add2 = 0
                if width_add2 > width_add1 * 2:
                    width_add1 = 0
                param_best['ratio'][0] -= width_add1 / line_one['width']
                param_best['width'] += width_add1
                param_best['width_rest'] += width_add1
                param_best['ratio'][1] += width_add2 / line_one['width']
                param_best['width'] += width_add2
                param_best['width_rest'] += width_add2

        # 参数判断
        index_best = int(param_best['index'])
        if index_best < 0:
            continue
        # 参数信息
        param_add = param_best.copy()
        param_add['ratio'] = param_best['ratio'][:]
        param_add['ratio_best'] = param_best['ratio_best'][:]
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
            room_rect_layout_pair(param_add, group_pair[group_idx], line_list, line_used, line_face,
                                  max_pass, min_pass, room_type, room_area, door_pt_entry)
        # 避让更新
        if group_idx_new in param_aside:
            for line_index, line_aside in param_aside[group_idx_new].items():
                if len(line_used[line_index]) <= 0:
                    continue
                for param_index, line_ratio in line_aside.items():
                    # 避让修正
                    param_old = line_used[line_index][param_index]
                    if line_index == index_best:
                        param_old['ratio_aside'] = line_ratio[:]
                    else:
                        param_old['ratio_aside'] = line_ratio[:]
                    # 相对修正
                    line_old = line_list[line_index]
                    group_old = param_old['group'][0]
                    width_old = group_old['size'][0]
                    ratio_old = line_ratio
                    if 'index_pair' in param_old:
                        index_new = param_old['index_pair']
                        if index_new in line_used:
                            param_new = line_used[index_new][0]
                            group_new = param_new['group'][0]
                            line_new = line_list[index_new]
                            width_new, depth_new, ratio_new, ratio_new_best, ratio_pair = \
                                compute_pair_ratio(line_old, ratio_old, line_new)
                            ratio_cur = param_new['ratio']
                            if len(ratio_new) <= 0:
                                continue
                            elif abs(ratio_cur[0] - ratio_new[0]) <= 0.1 and abs(ratio_cur[1] - ratio_new[1]) <= 0.1:
                                pass
                            elif width_new >= 1:
                                score_new = (ratio_pair[1] - ratio_pair[0]) * 10
                                # 补充宽度
                                group_pass = MID_GROUP_PASS
                                if group_old['type'] == 'Meeting':
                                    if width_new > width_old > group_new['size'][0]:
                                        width_new = width_old
                                    elif width_new > group_new['size'][0] + group_pass * 2:
                                        width_new = group_new['size'][0] + group_pass * 2
                                else:
                                    if width_new > width_old > group_new['size'][0]:
                                        width_new = width_old
                                width_rest = width_new - group_new['size'][0]
                                # 更新参数
                                param_new['score'] = score_new
                                param_new['width'] = width_new
                                param_new['width_rest'] = width_rest
                                param_new['ratio'] = ratio_new
                                param_new['ratio_best'] = ratio_new_best
                            param_old['ratio_pair'] = ratio_pair
                    if 'ratio_swap' in param_old:
                        param_new = line_used[line_index][-1]
                        for param_cur in [param_old, param_new]:
                            if 'ratio_best' in param_cur:
                                ratio_best = param_cur['ratio_best']
                                if line_ratio[0] <= ratio_best[0] <= ratio_best[1] <= line_ratio[1]:
                                    pass
                                else:
                                    param_cur['ratio_best'] = line_ratio[:]
                            if 'ratio_pair' in param_cur:
                                ratio_best = param_cur['ratio_pair']
                                if line_ratio[0] <= ratio_best[0] <= ratio_best[1] <= line_ratio[1]:
                                    pass
                                else:
                                    param_cur['ratio_pair'] = line_ratio[:]
                            if 'ratio_swap' in param_cur:
                                ratio_best = param_cur['ratio_swap']
                                if line_ratio[0] <= ratio_best[0] <= ratio_best[1] <= line_ratio[1]:
                                    pass
                                else:
                                    param_cur['ratio_swap'] = line_ratio[:]

    # 计算布局
    group_result, group_direct = [], 0
    for line_idx in line_used.keys():
        # 线段信息
        line_one = line_list[line_idx]
        line_type, line_width, line_height = line_one['type'], line_one['width'], line_one['height']
        line_angle = normalize_line_angle(line_one['angle'])
        line_room = ''
        if 'unit_to_type' in line_one:
            line_room = line_one['unit_to_type']
        line_idx_pre = (line_idx - 1 + len(line_list)) % len(line_list)
        line_idx_pre2 = (line_idx - 2 + len(line_list)) % len(line_list)
        line_pre = line_list[line_idx_pre]
        line_pre2 = line_list[line_idx_pre2]
        line_idx_post = (line_idx + 1 + len(line_list)) % len(line_list)
        line_idx_post2 = (line_idx + 2 + len(line_list)) % len(line_list)
        line_post = line_list[line_idx_post]
        line_post2 = line_list[line_idx_post2]
        p1, p2, score_pre, score_post = line_one['p1'], line_one['p2'], line_one['score_pre'], line_one['score_post']
        score_pre_new, score_post_new, curtain_pre, curtain_post = score_pre, score_post, 0, 0
        if score_pre == 1:
            if line_pre['type'] in [UNIT_TYPE_SIDE] and line_pre['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                score_pre_new, curtain_pre = 4, 1
            elif line_pre['type'] in [UNIT_TYPE_AISLE] and line_pre['depth'] > 3:
                score_pre_new, curtain_pre = 4, 0
            elif line_pre['type'] in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE] and line_pre['width'] < UNIT_WIDTH_HOLE:
                if line_pre2['type'] in [UNIT_TYPE_SIDE] and line_pre2['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                    score_pre_new, curtain_pre = 4, 1
        if score_post == 1:
            if line_post['type'] in [UNIT_TYPE_SIDE] and line_post['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                score_post_new, curtain_post = 4, 1
            elif line_post['type'] in [UNIT_TYPE_AISLE] and line_post['depth'] > 3:
                score_post_new, curtain_post = 4, 0
            elif line_post['type'] in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE] and line_post['width'] < UNIT_WIDTH_HOLE:
                if line_post2['type'] in [UNIT_TYPE_SIDE] and line_post2['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                    score_post_new, curtain_post = 4, 1
        type_pre, type_post = line_pre['type'], line_post['type']
        # 遍历参数
        param_list = line_used[line_idx]
        for param_idx, param_one in enumerate(param_list):
            group_one = param_one['group'][0]
            group_type, group_code = group_one['type'], group_one['code']
            group_width, group_depth = group_one['size'][0], group_one['size'][2]
            group_width_min, group_depth_min = group_one['size_min'][0], group_one['size_min'][2]
            group_width_well, group_depth_max = group_width, group_depth
            if 'depth_suit' in param_one and param_one['depth_suit'] > group_depth:
                group_depth_max = param_one['depth_suit']
            p1, p2 = line_one['p1'], line_one['p2']
            # 布局信息
            group_ratio = param_one['ratio']
            group_width_rest, group_depth_rest = param_one['width_rest'], param_one['depth_rest']
            ratio_pre, ratio_post, ratio_dir = group_ratio[0], group_ratio[1], 0
            ratio_aside, ratio_pair, ratio_best, ratio_suit, ratio_face = [], [], [], [], []
            type_swap = 0
            if 'type_swap' in param_one:
                type_swap = param_one['type_swap']
            # 起止比例
            if 'ratio_aside' in param_one and len(param_one['ratio_aside']) > 0:
                ratio_aside = param_one['ratio_aside'][:]
            if 'ratio_pair' in param_one and len(param_one['ratio_pair']) > 0:
                ratio_pair = param_one['ratio_pair'][:]
                if group_type in ['Dining']:
                    ratio_pair = []
            if 'ratio_best' in param_one and len(param_one['ratio_best']) > 0:
                ratio_best = param_one['ratio_best'][:]
                width_best = line_width * (ratio_best[1] - ratio_best[0])
                if group_type in ['Bath']:
                    if 0.01 < ratio_best[0] < ratio_best[1] < 0.99:
                        ratio_best = []
                    if len(ratio_aside) > 1 and len(ratio_best) > 1 and width_best > MID_GROUP_PASS:
                        if ratio_aside[0] - 0.1 <= ratio_best[0] < ratio_best[1] <= ratio_aside[1] + 0.1:
                            ratio_aside = []
                if len(ratio_best) >= 2 and width_best < 0.1:
                    ratio_best = []
            # 布局方向
            if group_type in ['Meeting'] and ratio_dir == 0:
                if len(ratio_aside) >= 2:
                    if abs((ratio_aside[0] - 0) - (1 - ratio_aside[1])) <= 0.01:
                        ratio_dir = 0
                        if group_width_rest < 0:
                            if curtain_pre and not curtain_post:
                                ratio_dir = 1
                            elif curtain_post and not curtain_pre:
                                ratio_dir = -1
                    elif ratio_aside[0] - 0 < 1 - ratio_aside[1]:
                        ratio_dir = 1
                    else:
                        ratio_dir = -1
                elif len(ratio_pair) >= 2:
                    if abs((ratio_pair[0] - 0) - (1 - ratio_pair[1])) <= 0.01:
                        ratio_dir = 0
                    elif ratio_pair[0] - 0 < 1 - ratio_pair[1]:
                        ratio_dir = 1
                    else:
                        ratio_dir = -1
            elif group_type in ['Dining'] and ratio_dir == 0:
                if group_width_rest > 0 and group_depth_rest < 0:
                    if ratio_pre <= 0.01 and ratio_post >= 0.99:
                        depth_all = line_one['depth_all']
                        if len(depth_all) > 0:
                            if depth_all[0][2] > max(group_depth + 0.2, depth_all[-1][2] + 0.2):
                                ratio_dir = 1
                            elif depth_all[-1][2] > max(group_depth + 0.2, depth_all[0][2] + 0.2):
                                ratio_dir = -1
            elif group_type in ['Bath'] and ratio_dir == 0:
                if len(ratio_aside) >= 2:
                    if abs((ratio_aside[0] - 0) - (1 - ratio_aside[1])) <= 0.01:
                        ratio_dir = 0
                    elif ratio_aside[0] - 0 < 1 - ratio_aside[1]:
                        ratio_dir = 1
                    else:
                        ratio_dir = -1
                elif score_pre_new > score_post_new:
                    ratio_dir = 1
                    if score_pre < score_post_new:
                        ratio_dir = 0
                elif score_post_new > score_pre_new:
                    ratio_dir = -1
                    if score_post < score_pre_new:
                        ratio_dir = 0
                elif len(ratio_best) >= 2:
                    if abs(ratio_best[0] - 0) < 0.01 and abs(ratio_best[1] - 1) > 0.01:
                        ratio_dir = 1
                    elif abs(ratio_best[0] - 0) > 0.01 and abs(ratio_best[1] - 1) < 0.01:
                        ratio_dir = -1
                    elif group_width < 1.0 or group_code < 1100:
                        if curtain_pre >= 1:
                            ratio_dir = 1
                        elif curtain_post >= 1:
                            ratio_dir = -1
                        elif score_pre == 4 and type_pre in [UNIT_TYPE_WINDOW]:
                            ratio_dir = 1
                        elif score_post == 4 and type_post in [UNIT_TYPE_WINDOW]:
                            ratio_dir = -1
                        elif line_one['depth_pre'] > line_one['depth_post']:
                            ratio_dir = 1
                        elif line_one['depth_pre'] < line_one['depth_post']:
                            ratio_dir = -1
                    else:
                        if score_pre == 4 and type_pre in [UNIT_TYPE_WALL]:
                            ratio_dir = 1
                        elif score_post == 4 and type_post in [UNIT_TYPE_WALL]:
                            ratio_dir = -1
                elif len(group_ratio) >= 2:
                    if abs(group_ratio[0] - 0) < 0.01 and abs(group_ratio[1] - 1) > 0.01:
                        ratio_dir = 1
                    elif abs(group_ratio[0] - 0) > 0.01 and abs(group_ratio[1] - 1) < 0.01:
                        ratio_dir = -1
            elif group_type in ['Work', 'Toilet'] and ratio_dir == 0:
                if len(ratio_aside) >= 2 and (ratio_aside[0] - 0 > 0.2 or 1 - ratio_aside[1] > 0.2):
                    if ratio_aside[0] - 0 <= 1 - ratio_aside[1]:
                        ratio_dir = 1
                    else:
                        ratio_dir = -1
                elif len(ratio_best) >= 2:
                    if param_idx >= 1:
                        if ratio_pre - 0 > 1 - ratio_post + 0.1:
                            ratio_dir = 1
                        elif ratio_pre - 0 + 0.1 < 1 - ratio_post:
                            ratio_dir = -1
                    elif group_type not in ['Work']:
                        if line_one['depth_pre'] > line_one['depth_post']:
                            ratio_dir = 1
                        elif line_one['depth_pre'] < line_one['depth_post']:
                            ratio_dir = -1
                        elif line_one['score_pre'] >= 4 > line_one['score_post']:
                            ratio_dir = 1
                        elif line_one['score_post'] >= 4 > line_one['score_pre']:
                            ratio_dir = -1
                    ratio_dir_old = ratio_dir
                    if 0.00 <= ratio_pre < 0.01 and ratio_dir_old == 0 and group_width_rest < 1.0:
                        if curtain_post <= 0 < curtain_pre:
                            ratio_dir = 1
                        elif score_post_new < score_pre_new == 4:
                            ratio_dir = 1
                    if 0.99 < ratio_post <= 1.00 and ratio_dir_old == 0 and group_width_rest < 1.0:
                        if curtain_pre <= 0 < curtain_post:
                            ratio_dir = -1
                        elif score_pre_new < score_post_new == 4:
                            ratio_dir = -1
                elif group_width_rest < 0.1:
                    ratio_dir = 0
            # 最佳比例
            width_find = line_width * (group_ratio[1] - group_ratio[0])
            if len(ratio_aside) > 0 and 'seed_position' not in group_one:
                width_aside = line_width * (ratio_aside[1] - ratio_aside[0])
                if group_width_min - 0.1 < width_aside < group_width + 0.1:
                    ratio_suit = ratio_aside
                elif group_width_min - 0.1 < width_aside and group_type in ['Dining', 'Bath', 'Toilet']:
                    ratio_suit = ratio_aside
            if len(ratio_suit) <= 0 and len(ratio_best) > 0:
                if abs(ratio_best[0] - 0) < 0.05:
                    ratio_best[0] = 0
                if abs(ratio_best[1] - 1) < 0.05:
                    ratio_best[1] = 1
                width_best = line_width * (ratio_best[1] - ratio_best[0])
                if group_type in ['Meeting', 'Bed']:
                    if width_best >= min(group_width, group_width_min + 0.5):
                        if not type_swap == 1:
                            ratio_suit = ratio_best[:]
                    else:
                        width_well = min(group_width, group_width_min + 0.5)
                        if group_width_min >= max(width_best, 3):
                            width_well = group_width_min
                        if 1 - ratio_best[1] < ratio_best[0] - 0:
                            ratio_pre = ratio_best[1] - width_well / line_width
                            ratio_post = ratio_best[1]
                            ratio_suit = [ratio_pre, ratio_post]
                        elif ratio_best[0] - 0 < 1 - ratio_best[1]:
                            ratio_pre = ratio_best[0]
                            ratio_post = ratio_best[0] + width_well / line_width
                            ratio_suit = [ratio_pre, ratio_post]
                        elif ratio_pre < 0 < ratio_post <= 1:
                            ratio_new = ratio_post - width_well / line_width
                            if ratio_new > ratio_pre:
                                ratio_pre = min(ratio_new, 0)
                                ratio_suit = [ratio_pre, ratio_post]
                        elif ratio_post > 1 > ratio_pre >= 0:
                            ratio_new = ratio_pre + width_well / line_width
                            if ratio_new < ratio_post:
                                ratio_post = max(ratio_new, 1)
                                ratio_suit = [ratio_pre, ratio_post]
                elif group_type in ['Media']:
                    if width_best >= min(group_width, group_width_min + 0.5):
                        ratio_suit = ratio_best[:]
                    else:
                        width_well = min(group_width, group_width_min + 0.5)
                        if 1 - ratio_best[1] < ratio_best[0] - 0:
                            ratio_pre = ratio_best[1] - width_well / line_width
                            ratio_post = ratio_best[1]
                            ratio_suit = [ratio_pre, ratio_post]
                        elif ratio_best[0] - 0 < 1 - ratio_best[1]:
                            ratio_pre = ratio_best[0]
                            ratio_post = ratio_best[0] + width_well / line_width
                            ratio_suit = [ratio_pre, ratio_post]
                        elif ratio_pre < 0 < ratio_post <= 1:
                            ratio_new = ratio_post - width_well / line_width
                            if ratio_new > ratio_pre:
                                ratio_pre = min(ratio_new, 0)
                                ratio_suit = [ratio_pre, ratio_post]
                        elif ratio_post > 1 > ratio_pre >= 0:
                            ratio_new = ratio_pre + width_well / line_width
                            if ratio_new < ratio_post:
                                ratio_post = max(ratio_new, 1)
                                ratio_suit = [ratio_pre, ratio_post]
                elif group_type in ['Dining']:
                    group_width_well = group_width + MID_GROUP_PASS
                    if width_best > group_width_well:
                        ratio_suit = ratio_best[:]
                    elif param_one['vertical'] > 0 and width_best > group_width:
                        ratio_suit = ratio_best[:]
                    else:
                        if 0.1 < 1 - ratio_best[1] < ratio_best[0] - 0:
                            ratio_pre = ratio_best[1] - group_width / line_width
                            ratio_post = ratio_best[1]
                            ratio_suit = [ratio_pre, ratio_post]
                        elif 0.1 < ratio_best[0] - 0 < 1 - ratio_best[1]:
                            ratio_pre = ratio_best[0]
                            ratio_post = ratio_best[0] + group_width / line_width
                            ratio_suit = [ratio_pre, ratio_post]
                        elif ratio_pre < 0 < ratio_post <= 1:
                            ratio_new = ratio_post - group_width_well / line_width
                            if ratio_new > ratio_pre:
                                ratio_pre = min(ratio_new, 0)
                                ratio_suit = [ratio_pre, ratio_post]
                        elif ratio_post > 1 > ratio_pre >= 0:
                            ratio_new = ratio_pre + group_width_well / line_width
                            if ratio_new < ratio_post:
                                ratio_post = max(ratio_new, 1)
                                ratio_suit = [ratio_pre, ratio_post]
                elif group_type in ['Work'] and line_type in [UNIT_TYPE_WINDOW]:
                    pass
                elif group_type in ['Bath'] and width_best > MID_GROUP_PASS:
                    ratio_suit = ratio_best[:]
                elif width_best > group_width - 0.01:
                    ratio_suit = ratio_best[:]
            if len(ratio_suit) <= 0:
                ratio_suit = group_ratio[:]
            # 调整比例
            if 0 < ratio_suit[0] - group_ratio[0] < 0.05 and abs(group_ratio[0] - 0) < 0.05:
                ratio_suit[0] = group_ratio[0]
            elif 0 < group_ratio[1] - ratio_suit[1] < 0.05 and abs(group_ratio[1] - 1) < 0.05:
                ratio_suit[1] = group_ratio[1]
            ratio_suit[0] = max(ratio_suit[0], group_ratio[0])
            ratio_suit[1] = min(ratio_suit[1], group_ratio[1])
            if len(ratio_suit) > 0 and abs(ratio_suit[1] - ratio_suit[0]) > 0.01:
                # 最佳尺寸
                width_suit = line_width * (ratio_suit[1] - ratio_suit[0])
                width_well = group_width_min
                if group_type in ['Meeting']:
                    width_well = min(group_width, group_width_min + 0.5)
                    if group_width_min >= 3:
                        width_well = group_width_min
                elif group_type in ['Dining']:
                    width_well = group_width
                elif group_type in ['Bath']:
                    width_well = max(group_width, 0.8)
                elif group_type in ['Toilet']:
                    width_well = max(group_width, 0.6)
                if width_suit < width_well - 0.01 and width_suit < group_width - 0.01:
                    ratio_pre, ratio_post = group_ratio[0], group_ratio[1]
                    if width_suit > group_width_min and group_type in ['Meeting']:
                        ratio_pre, ratio_post = ratio_suit[0], ratio_suit[1]
                    elif width_suit > MID_GROUP_PASS and group_type in ['Bath']:
                        ratio_pre, ratio_post = ratio_suit[0], ratio_suit[1]
                elif width_suit >= width_well and group_type in ['Bath']:
                    ratio_max = min(width_suit, width_well) / line_width
                    if abs(width_suit - 0.1 - width_well) < 0.4:
                        ratio_max = (width_suit - 0.1) / line_width
                    if ratio_pre <= 0.01 < ratio_post < 0.90:
                        ratio_pre, ratio_post = ratio_suit[0], ratio_suit[0] + ratio_max * width_suit / width_well
                        if curtain_pre <= 0:
                            ratio_pre += UNIT_DEPTH_CURTAIN / line_width * 0.6
                    elif 0.1 < ratio_pre < 0.99 <= ratio_post:
                        ratio_pre, ratio_post = ratio_suit[1] - ratio_max * width_suit / width_well, ratio_suit[1]
                        if curtain_post <= 0:
                            ratio_post -= UNIT_DEPTH_CURTAIN / line_width * 0.6
                    else:
                        ratio_pre, ratio_post = ratio_suit[0], ratio_suit[1]
                else:
                    ratio_pre, ratio_post = ratio_suit[0], ratio_suit[1]
                # 扩展比例
                if ratio_suit[1] > 1 and ratio_suit[0] >= 0:
                    if line_width * (1 - ratio_suit[0]) > group_width > line_width * (ratio_suit[1] - 1):
                        ratio_suit[1] = 1
                        ratio_post = ratio_suit[1]
                    elif line_width * (1 - ratio_suit[0]) > group_width_min > 2 > line_width * (ratio_suit[1] - 1) * 4:
                        ratio_suit[1] = 1
                        ratio_post = ratio_suit[1]
                elif ratio_suit[0] < 0 and ratio_suit[1] <= 1:
                    if line_width * (ratio_suit[1] - 0) > group_width > line_width * (0 - ratio_suit[0]):
                        ratio_suit[0] = 0
                        ratio_pre = ratio_suit[0]
                    elif line_width * (ratio_suit[1] - 0) > group_width_min > 2 > line_width * (0 - ratio_suit[0]) * 4:
                        ratio_suit[0] = 0
                        ratio_pre = ratio_suit[0]
                # 靠边比例
                if group_type in ['Bed']:
                    width_well, width_left = group_width + 0.8, 0.8
                    if group_size[0] > group_size[2] and group_size[1] > UNIT_HEIGHT_SHELF_MIN:
                        width_well, width_left = group_width, 0.0
                    elif len(door_pt_wear) > 0:
                        width_well, width_left = group_width, 0.0
                    elif line_width > max(group_width, min(width_suit, 3)) + 0.5:
                        width_well, width_left = min(group_width, width_suit), 0.0
                    if width_suit < width_well:
                        if curtain_pre >= 1:
                            ratio_dir = 1
                        elif curtain_post >= 1:
                            ratio_dir = -1
                        else:
                            dis1, dis2, dis3 = compute_line_distance(line_one, ratio_suit, door_pt_entry, 0, 2)
                            if dis1 > dis2 + 1:
                                ratio_dir = 1
                            elif dis2 > dis1 + 1:
                                ratio_dir = -1
                        width_well = max(min(group_width_min + 0.5, 2.4), width_suit - width_left)
                        ratio_well = width_well / line_width
                    else:
                        ratio_dir_old = ratio_dir
                        if 0.00 <= ratio_pre < 0.01 and ratio_dir_old == 0:
                            if curtain_post <= 0 < curtain_pre and width_suit < max(width_well + 0.5, 3):
                                ratio_dir = 1
                            elif score_post_new < score_pre_new == 4 and width_suit < max(width_well + 0.5, 3):
                                ratio_dir = 1
                            elif line_one['depth_post'] < line_one['depth_pre']:
                                ratio_dir = 1
                        if 0.99 < ratio_post <= 1.00 and ratio_dir_old == 0:
                            if curtain_pre <= 0 < curtain_post and width_suit < max(width_well + 0.5, 3):
                                ratio_dir = -1
                            elif score_pre_new < score_post_new == 4 and width_suit < max(width_well + 0.5, 3):
                                ratio_dir = -1
                            elif line_one['depth_pre'] < line_one['depth_post']:
                                ratio_dir = -1
                        width_well = max(min(group_width + 0.5, 2.5), width_suit - width_left)
                        ratio_well = width_well / line_width
                    if ratio_dir >= 1:
                        ratio_post = ratio_pre + ratio_well
                        if width_suit >= width_well and curtain_pre <= 0:
                            ratio_pre += UNIT_DEPTH_CURTAIN / line_width
                    elif ratio_dir <= -1:
                        ratio_pre = ratio_post - ratio_well
                        if width_suit >= width_well and curtain_post <= 0:
                            ratio_post -= UNIT_DEPTH_CURTAIN / line_width
                    group_direct = ratio_dir
            # 限制比例
            if ratio_pre <= group_ratio[0]:
                ratio_pre = group_ratio[0]
            if ratio_post >= group_ratio[1]:
                ratio_post = group_ratio[1]

            # 靠窗判断
            window_flag, door_flag = 0, 0
            if line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                window_flag = 1
            if window_flag == 0 and ratio_pre < 0:
                if line_pre['type'] in [UNIT_TYPE_SIDE, UNIT_TYPE_AISLE]:
                    pass
                else:
                    window_flag = score_pre
                if score_pre == 1 and ratio_pre > 0 - 0.1:
                    window_flag = 0
                if score_pre == 1 and line_pre['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE]:
                    window_flag = 0
                    door_flag += 1
            if window_flag == 0 and ratio_post > 1:
                if line_post['type'] in [UNIT_TYPE_SIDE, UNIT_TYPE_AISLE]:
                    pass
                else:
                    window_flag = score_post
                if score_post == 1 and ratio_post < 1 + 0.1:
                    window_flag = 0
                if score_post == 1 and line_post['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE]:
                    window_flag = 0
                    door_flag += 1
            if window_flag == 1:
                if ratio_pre < 0.0 - 0.1 and 1.0 + 0.1 < ratio_post:
                    pass
                elif ratio_pre < 0.1 < 1 < ratio_post:
                    if line_width * (1 - ratio_pre) > group_width_min + MID_GROUP_PASS * 2:
                        ratio_post = 1
                        window_flag = 2
                elif ratio_pre < 0 < 0.9 < ratio_post:
                    if line_width * (ratio_post - 0) > group_width_min + MID_GROUP_PASS * 2:
                        ratio_pre = 0
                        window_flag = 2
                elif ratio_pre < 0 < 1 < ratio_post:
                    if line_width > group_width:
                        ratio_pre, ratio_post = 0, 1
                        window_flag = 2
            else:
                if score_pre == 1 and line_pre['type'] in [UNIT_TYPE_WINDOW] and ratio_pre <= 0.01:
                    window_flag = 2
                if score_post == 1 and line_pre['type'] in [UNIT_TYPE_WINDOW] and ratio_post >= 0.99:
                    window_flag = 2
            # 旋转判断
            vertical_flag = param_one['vertical']
            # 悬空判断
            type_swap, index_swap, width_swap, depth_swap, angle_swap, ratio_swap = 0, line_idx, 0, 0, 0, []
            if 'type_swap' in param_one:
                type_swap = param_one['type_swap']
                index_swap = param_one['index_swap']
                width_swap = param_one['width_swap']
                depth_swap = param_one['depth_swap']
                ratio_swap = param_one['ratio_swap']
            # 沙发悬空
            if type_swap == 1 and index_swap == line_idx:
                if 0 <= param_idx + 1 < len(param_list):
                    param_pair = param_list[param_idx + 1]
                    if 'index_swap' in param_pair:
                        param_pair['ratio_swap'] = [ratio_pre, ratio_post]
                group_width_rest = min(group_width_rest, MID_GROUP_PASS)
                angle_swap = math.pi
                ratio_dir = 0
            # 沙发靠墙
            elif type_swap == 2 and index_swap == line_idx:
                if 0 <= param_idx + 1 < len(param_list):
                    param_pair = param_list[param_idx + 1]
                    if 'index_swap' in param_pair:
                        param_pair['ratio_swap'] = [ratio_pre, ratio_post]
                        param_pair['width_swap'] = line_width * (ratio_post - ratio_pre)
            # 电视靠墙 电视悬空
            elif (type_swap == 1 and not index_swap == line_idx) or (type_swap == 2 and not index_swap == line_idx):
                group_width_rest = width_swap - group_width
                if len(ratio_swap) >= 2:
                    ratio_pre, ratio_post = ratio_swap[0], ratio_swap[1]
                if type_swap == 2:
                    angle_swap = math.pi

            # 宽度深度
            depth_rest_old, depth_rest_new = group_depth_rest, group_depth_rest
            width_rest_new = line_width * (ratio_post - ratio_pre) - group_width
            if -0.1 < width_rest_new < 0:
                width_rest_new = 0
            if group_width_rest > width_rest_new:
                group_width_rest = width_rest_new
            if vertical_flag <= 0 and door_flag >= 2:
                group_width_rest = min(width_rest_new, group_width_min - group_width)

            # 对面参数
            param_face = {}
            if 'index_pair' in param_one and param_one['index_pair'] in line_used:
                param_list_face = line_used[param_one['index_pair']]
                for param_idx_face, param_one_face in enumerate(param_list_face):
                    group_one_face = param_one_face['group'][0]
                    if 'type' in group_one_face and group_one_face['type'] in ['Media']:
                        param_face = param_one_face
                        break

            # 遍历组合
            group_cnt = 1
            for group_idx in range(group_cnt):
                # 组合信息
                group_one = param_one['group'][group_idx]
                group_size, group_size_min = group_one['size'], group_one['size_min']
                group_width, group_height, group_depth = group_size[0], group_size[1], group_size[2]
                group_width_min, group_depth_min = group_size_min[0], group_size_min[2]
                group_width_rest1, group_width_rest2 = 0, 0
                group_depth_rest1, group_depth_rest2 = 0, 0
                if 'size_rest' in group_one:
                    group_size_rest = group_one['size_rest']
                    group_width_rest1, group_width_rest2 = group_size_rest[1], group_size_rest[3]
                    group_depth_rest1, group_depth_rest2 = group_size_rest[0], group_size_rest[2]
                group_angle = line_angle + math.pi / 2

                # 初步判断
                width_ratio = line_width * (ratio_post - ratio_pre)
                if 'seed_list' in group_one and len(group_one['seed_list']) > 0 and width_ratio > MID_GROUP_PASS * 2:
                    pass
                elif width_ratio > 3 > group_width_min * 0.5:
                    pass
                elif width_ratio < group_width_min - 0.05 and group_type in ['Dining']:
                    continue

                # 横向宽度
                group_width_dump1, group_width_dump2, group_depth_dump1, group_depth_dump2 = 0, 0, 0, 0  # 四周放弃
                ratio_middle = (ratio_pre + ratio_post) / 2
                # 裁剪宽度
                if group_width_rest < -0.01:
                    if group_type in ['Media'] and group_width + group_width_rest > 2:
                        group_width_dump1 = -group_width_rest / 2
                        group_width_dump2 = -group_width_rest / 2
                    elif group_width_rest1 > MID_GROUP_PASS and group_width_rest2 > MID_GROUP_PASS:
                        if group_width_rest1 >= group_width_rest2:
                            group_width_dump1 = group_width_rest1 - group_width_rest2
                            group_width_more = -group_width_rest - group_width_dump1
                            if group_width_more > 0:
                                group_width_dump1 += group_width_more / 2
                                group_width_dump2 += group_width_more / 2
                        else:
                            group_width_dump2 = group_width_rest2 - group_width_rest1
                            group_width_more = -group_width_rest - group_width_dump2
                            if group_width_more > 0:
                                group_width_dump1 += group_width_more / 2
                                group_width_dump2 += group_width_more / 2
                    elif group_width_rest1 > group_width_rest2:
                        if group_width_rest1 - group_width_rest2 > -group_width_rest:
                            group_width_dump1 = group_width_rest1 - group_width_rest2
                            if group_type in ['Bath']:
                                group_width_dump1 = -group_width_rest
                        else:
                            group_width_dump1 = group_width_rest1
                            group_width_dump2 = 0 - group_width_rest - group_width_dump1
                            if group_width_dump2 < 0:
                                if -group_width_dump2 < group_width_rest2:
                                    group_width_dump1 -= (-group_width_dump2)
                                    group_width_dump2 = 0
                                else:
                                    group_width_dump1 -= (group_width_rest2 - group_width_dump2) / 2
                                    group_width_dump2 = (-group_width_dump2 - group_width_rest2) / 2
                    elif group_width_rest1 < group_width_rest2:
                        if group_width_rest2 - group_width_rest1 > -group_width_rest:
                            group_width_dump2 = group_width_rest2 - group_width_rest1
                            if group_type in ['Bath']:
                                group_width_dump2 = -group_width_rest
                        else:
                            group_width_dump2 = group_width_rest2
                            group_width_dump1 = 0 - group_width_rest - group_width_dump2
                            if group_width_dump1 < 0:
                                if -group_width_dump1 < group_width_rest1:
                                    group_width_dump2 -= (-group_width_dump1)
                                    group_width_dump1 = 0
                                else:
                                    group_width_dump2 -= (group_width_rest1 - group_width_dump1) / 2
                                    group_width_dump1 = (-group_width_dump1 - group_width_rest1) / 2
                    else:
                        if max(group_width_rest1, group_width_rest2) < 0.1:
                            if score_pre_new <= 2 and score_post_new >= 4:
                                group_width_dump1, group_width_dump2 = 0, -group_width_rest
                                if type_swap == 1:
                                    group_width_dump1, group_width_dump2 = -group_width_rest, 0
                            elif score_pre_new >= 4 and score_post_new <= 2:
                                group_width_dump1, group_width_dump2 = -group_width_rest, 0
                                if type_swap == 1:
                                    group_width_dump1, group_width_dump2 = 0, -group_width_rest
                            else:
                                group_width_dump1 = -group_width_rest / 2
                                group_width_dump2 = -group_width_rest / 2
                        else:
                            group_width_dump1 = -group_width_rest / 2
                            group_width_dump2 = -group_width_rest / 2
                if group_depth_rest < -0.01:
                    if group_type in ['Dining']:
                        if abs(group_depth_rest) < 0.15:
                            group_depth_dump1 = 0
                            group_depth_dump2 = 0
                        elif abs(group_depth_rest) < group_depth / 4:
                            group_depth_dump1 = 0
                            group_depth_dump2 = -group_depth_rest
                        else:
                            group_depth_dump1 = group_depth_rest1
                            group_depth_dump2 = -group_depth_rest - group_depth_dump1
                    elif group_type in ['Bath', 'Toilet']:
                        if group_type in ['Bath'] and abs(group_depth_rest) < group_depth / 3:
                            group_depth_dump1 = group_depth_rest1
                            group_depth_dump2 = -group_depth_rest - group_depth_dump1
                    else:
                        group_depth_dump1 = group_depth_rest1
                        group_depth_dump2 = -group_depth_rest - group_depth_dump1
                        if group_depth_dump2 < 0:
                            group_depth_dump2 *= 0.5
                        elif group_depth_dump2 > 0:
                            if group_type in ['Meeting'] and 'depth_rest' in param_face:
                                param_face['depth_rest'] += group_depth_dump2
                # 扩展宽度
                if group_width_rest > 0 and group_type in ['Meeting']:
                    width_dlt = group_width_rest
                    width_sub = group_width_rest1 - group_width_rest2
                    # 适应区间
                    if group_width_rest1 > group_width_rest2 + 0.1:
                        if group_width_rest1 - group_width_rest2 >= width_dlt:
                            group_width_dump2 = -width_dlt
                        else:
                            group_width_dump1 = 0 - (width_dlt - width_sub) / 2
                            group_width_dump2 = 0 - (width_dlt + width_sub) / 2
                    elif group_width_rest2 > group_width_rest1 + 0.1:
                        if group_width_rest2 - group_width_rest1 >= width_dlt:
                            group_width_dump1 = -width_dlt
                        else:
                            group_width_dump1 = 0 - (width_dlt - width_sub) / 2
                            group_width_dump2 = 0 - (width_dlt + width_sub) / 2
                    else:
                        width_dlt = min(group_width_rest, MID_GROUP_PASS * 2.0)
                        group_width_dump1 = -width_dlt / 2
                        group_width_dump2 = -width_dlt / 2
                    # 最佳区间
                    if (len(ratio_pair) > 0 or len(ratio_best) > 0) and type_swap == 0:
                        if len(ratio_pair) > 0:
                            ratio_middle = (ratio_pair[1] + ratio_pair[0]) / 2
                        elif len(ratio_best) > 0 and line_width * (ratio_best[1] - ratio_best[0]) > group_width:
                            ratio_middle = (ratio_best[1] + ratio_best[0]) / 2
                        center_bias = group_width_rest2 - group_width_dump2 - (group_width_rest1 - group_width_dump1)
                        center_suit = (ratio_pre + ratio_post) / 2 + center_bias / 2 / line_width
                        offset_best = (ratio_middle - center_suit) * line_width
                        if abs(offset_best) < group_width_rest:
                            if offset_best > 0 and group_width_rest1 - group_width_dump1 > 0:
                                offset_max = group_width_rest1 - group_width_dump1
                                if offset_max > offset_best:
                                    offset_max = offset_best
                                if offset_max > 0:
                                    group_width_dump1 += offset_max
                                    group_width_dump2 -= offset_max
                                pass
                            elif offset_best < 0 and group_width_rest2 - group_width_dump2 > 0:
                                offset_max = group_width_rest2 - group_width_dump2
                                if offset_max > -offset_best:
                                    offset_max = -offset_best
                                if offset_max > 0:
                                    group_width_dump1 -= offset_max
                                    group_width_dump2 += offset_max
                elif group_width_rest > 0 and group_type in ['Bed']:
                    width_dlt = group_width_rest
                    if group_width_rest1 > 0.1 > group_width_rest2:
                        group_width_dump2 = -min(width_dlt / 2, group_width_rest1)
                    elif group_width_rest2 > 0.1 > group_width_rest1:
                        group_width_dump1 = -min(width_dlt / 2, group_width_rest2)
                elif group_width_rest > 0 and group_type in ['Media']:
                    width_dlt = min(group_width_rest, MID_GROUP_PASS)
                    if room_type in ROOM_TYPE_LEVEL_2:
                        if group_width_rest >= 1 and abs(group_direct) >= 1:
                            width_dlt = min(group_width_rest * 0.5, MID_GROUP_PASS)
                            ratio_dir = -group_direct
                        else:
                            width_dlt = min(group_width_rest, 0.1)
                    group_width_dump1 = 0 - width_dlt / 2
                    group_width_dump2 = 0 - width_dlt / 2
                elif group_width_rest > 0 and group_type in ['Dining']:
                    width_dlt = group_width_rest
                    if window_flag >= 1:
                        if width_dlt >= MID_GROUP_PASS * 2:
                            width_dlt = MID_GROUP_PASS * 2
                        elif width_dlt >= MID_GROUP_PASS * 1:
                            width_dlt = MID_GROUP_PASS * 1
                    elif vertical_flag >= 1:
                        if width_dlt >= MID_GROUP_PASS + UNIT_WIDTH_DODGE:
                            width_dlt = MID_GROUP_PASS
                        elif width_dlt >= MIN_GROUP_PASS * 2:
                            width_dlt = MIN_GROUP_PASS * 2
                        elif width_dlt >= MIN_GROUP_PASS * 1:
                            width_dlt = MIN_GROUP_PASS * 1
                        else:
                            width_dlt = 0
                    elif width_dlt >= MID_GROUP_PASS * 2:
                        width_dlt = MID_GROUP_PASS * 1
                    elif width_dlt >= MID_GROUP_PASS * 1:
                        width_dlt = MIN_GROUP_PASS * 1
                    else:
                        width_dlt = 0
                    group_width_dump1 = 0 - width_dlt / 2
                    group_width_dump2 = 0 - width_dlt / 2
                    if ratio_dir >= 1:
                        group_width_dump1 = 0 - width_dlt
                        group_width_dump2 = 0
                    elif ratio_dir < -1:
                        group_width_dump1 = 0
                        group_width_dump2 = 0 - width_dlt
                elif group_width_rest > 0 and group_type in ['Work', 'Rest']:
                    width_dlt = group_width_rest
                    if group_width > 2 or room_area <= 15:
                        if width_dlt >= MIN_GROUP_PASS:
                            width_dlt = MIN_GROUP_PASS
                    elif width_dlt >= MID_GROUP_PASS:
                        width_dlt = MID_GROUP_PASS
                    elif width_dlt < MIN_GROUP_PASS:
                        width_dlt = 0
                    group_width_dump1 = group_width_dump2 = -width_dlt / 2
                elif group_width_rest > 0 and group_type in ['Bath', 'Toilet']:
                    width_dlt = group_width_rest
                    if group_one['code'] >= 1100:
                        if ratio_dir <= -1:
                            group_width_dump2 = 0
                        elif ratio_dir >= 1:
                            group_width_dump1 = 0
                        else:
                            group_width_dump1 = group_width_dump2 = -width_dlt / 2
                    elif group_width_rest1 < MIN_GROUP_PASS < group_width_rest2:
                        if width_dlt > group_width_rest2 - group_width_rest1:
                            width_dlt = min(group_width_rest2 - group_width_rest1 + 0.3, group_width_rest)
                            group_width_dump1 = -width_dlt
                        elif width_dlt < (group_width_rest2 - group_width_rest1) / 2:
                            width_dlt = (group_width_rest2 - group_width_rest1 - width_dlt) / 2
                            group_width_dump1 = -width_dlt
                            group_width_dump2 = width_dlt
                        else:
                            group_width_dump1 = -width_dlt
                    elif group_width_rest2 < MIN_GROUP_PASS < group_width_rest1:
                        if width_dlt > group_width_rest1 - group_width_rest2:
                            width_dlt = group_width_rest1 - group_width_rest2
                            group_width_dump2 = -width_dlt
                        elif width_dlt < -(group_width_rest1 - group_width_rest2) / 2:
                            width_dlt = (group_width_rest1 - group_width_rest2 - width_dlt) / 2
                            group_width_dump1 = width_dlt
                            group_width_dump2 = -width_dlt
                        else:
                            group_width_dump2 = -width_dlt
                    elif group_width_rest1 < MIN_GROUP_PASS and group_width_rest2 < MIN_GROUP_PASS:
                        if group_type in ['Bath']:
                            if group_code >= 1100:
                                width_dlt = 0
                            elif width_dlt > MID_GROUP_PASS:
                                width_dlt = MID_GROUP_PASS
                        else:
                            if width_dlt > MID_GROUP_PASS and room_area > MID_ROOM_AREA_BATH:
                                width_dlt = MID_GROUP_PASS
                            elif width_dlt > MIN_GROUP_PASS * 2:
                                width_dlt = MIN_GROUP_PASS * 2
                        group_width_dump1 = group_width_dump2 = -width_dlt / 2
                # 剩余宽度
                width_rest_new += group_width_dump1
                width_rest_new += group_width_dump2

                # 横向比例
                ratio_center_1 = (ratio_pre + ratio_post) / 2
                ratio_center_2 = ratio_center_1 + (group_width_dump1 - group_width_dump2) / line_width / 2
                if group_cnt <= 1:
                    if ratio_dir >= 1:
                        ratio_w = ratio_pre + (group_width / 2 - group_width_dump2) / line_width
                    elif ratio_dir <= -1:
                        ratio_w = ratio_post - (group_width / 2 - group_width_dump1) / line_width
                    else:
                        ratio_w = ratio_center_2
                else:
                    ratio_w = ratio_pre + (group_width / 2 - group_width_dump2) / line_width
                    ratio_pre = ratio_pre + (group_width - group_width_dump1 - group_width_dump2) / line_width
                # 横向位置
                if abs(angle_swap - math.pi) < 0.1:
                    ratio_w = (ratio_pre + ratio_post) / 2 - (ratio_w - (ratio_pre + ratio_post) / 2)
                pp = [p1[0] * (1 - ratio_w) + p2[0] * ratio_w, p1[1] * (1 - ratio_w) + p2[1] * ratio_w]

                # 纵向深度
                angle = line_angle + math.pi / 2
                depth = group_depth / 2 - group_depth_dump1
                depth_curtain, depth_dodge, depth_back, depth_front = UNIT_DEPTH_CURTAIN, 0, 0, 0
                # 后向深度 窗帘
                if line_one['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] or window_flag == 1:
                    if group_type in ['Meeting', 'Bed', 'Dining']:
                        if line_type in [UNIT_TYPE_DOOR] and group_type in ['Dining']:
                            depth_pre, depth_post = line_one['depth_pre'], line_one['depth_post']
                            if 1 < max(depth_pre, depth_post) < max(group_depth, 3):
                                depth_dodge = min(depth_rest_new * 1.0, depth_curtain)
                            elif depth_rest_new <= 1:
                                depth_dodge = min(depth_rest_new * 1.0, 1)
                            else:
                                depth_dodge = min(depth_rest_new * 0.5, 1)
                            depth_dodge = max(depth_dodge, depth_curtain)
                            depth += depth_dodge
                            depth_rest_new -= depth_dodge
                        else:
                            depth_dodge = max(depth_dodge, depth_curtain)
                            depth += depth_dodge
                            depth_rest_new -= depth_dodge
                    elif group_depth_rest > depth_curtain:
                        depth_dodge = max(depth_dodge, depth_curtain)
                        depth += depth_dodge
                elif (ratio_pre < -0.1 and score_pre == 1 and line_pre['type'] in [UNIT_TYPE_DOOR]) or \
                        (ratio_post > 1.1 and score_post == 1 and line_post['type'] in [UNIT_TYPE_DOOR]):
                    if group_type in ['Dining'] and \
                            (line_pre['unit_to_type'] in ['Kitchen'] or line_post['unit_to_type'] in ['Kitchen']):
                        depth_dodge = min(depth_rest_new * 0.5, depth_rest_new - 0.2, 0.6)
                    else:
                        depth_dodge = min(depth_rest_new * 0.5, depth_rest_new - 0.2, 1.2)
                    depth_dodge = max(depth_dodge, depth_curtain)
                    depth += depth_dodge
                    depth_rest_new -= depth_dodge
                # 后向深度 过道
                elif score_pre_new <= 1 and type_pre in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] and \
                        score_post_new <= 1 and type_post in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE]:
                    if group_type in ['Dining']:
                        if depth_rest_new > UNIT_WIDTH_HOLE:
                            depth_dodge = min(depth_rest_new * 0.5, depth_rest_new - 0.2, 1.0)
                            depth += depth_dodge
                            depth_rest_new -= depth_dodge
                        else:
                            depth_dodge = min(depth_rest_new * 1.0, depth_rest_new - 0.2, 1.0)
                            depth += depth_dodge
                            depth_rest_new -= depth_dodge
                # 后向深度 背景
                if 'back_depth' in line_one and window_flag <= 0:
                    depth_back = line_one['back_depth']
                    group_one['back_depth'] = depth_back
                if score_pre_new + score_post_new >= 8 and group_type in ['Dining']:
                    if depth_rest_new >= 1.0 and param_idx <= 0 and line_type in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE]:
                        depth_back = max(0.5, depth_back)

                # 调整深度
                depth += depth_back
                depth_rest_new -= depth_back
                # 前向深度
                depth_front = 0
                if depth_rest_new > 0:
                    depth_rest_max = max(depth_rest_new + group_depth_dump1, 0)
                    if group_type in GROUP_PAIR_FUNCTIONAL and depth_rest_max < 3:
                        depth_front = depth_rest_max * 0.5
                    elif group_type in ['Media']:
                        depth_front = depth_rest_max * 0.1
                    elif group_type in ['Dining']:
                        pass
                    elif group_type in ['Bath'] and depth_rest_max < MIN_GROUP_PASS * 2:
                        depth_front = depth_rest_max * 1.0
                    else:
                        depth_front = min(depth_rest_max * 0.4, MID_GROUP_PASS)
                elif depth_rest_new < 0 and group_type in ['Dining', 'Bath']:
                    depth_front = depth_rest_new
                if group_size[0] > group_size[2] and group_size[1] > UNIT_HEIGHT_SHELF_MIN and group_type in ['Bed']:
                    depth_front = 0
                elif depth_front > MID_GROUP_PASS - group_depth > 0 and group_type in ['Media']:
                    depth_front = MID_GROUP_PASS - group_depth
                elif abs(angle_swap - math.pi) < 0.1:
                    depth_front = min(MID_GROUP_PASS * 2, depth_front)
                elif depth_front > MID_GROUP_PASS * 2:
                    depth_front = MID_GROUP_PASS * 2
                elif depth_front < 0:
                    depth_front = depth_rest_new
                # 前向深度
                if -group_depth_dump2 > depth_front > 0:
                    group_depth_dump2 = -depth_front
                elif depth_rest_new >= depth_front:
                    group_depth_dump2 = -depth_front
                    depth_rest_new -= depth_front
                elif depth_rest_new > 0:
                    group_depth_dump2 = -depth_rest_new

                # 居中判断
                center_flag = 0
                # 餐桌居中
                depth_pre, depth_post = line_one['depth_pre'], line_one['depth_post']
                depth_pre_more, depth_post_more = line_one['depth_pre_more'], line_one['depth_post_more']
                if group_type in ['Dining'] and depth_rest_new > 0:
                    depth_rest_now = depth_rest_new
                    if room_type in ['DiningRoom'] and (room_area >= 7 or depth_rest_new > MID_GROUP_PASS):
                        center_flag = 1
                    elif score_pre == 4 and score_post == 4 and depth_rest_new > MID_GROUP_PASS:
                        depth_base_min, depth_base_max = min(depth_pre, depth_post), max(depth_pre, depth_post)
                        if group_depth + depth_rest_new > depth_base_min > group_depth + depth_dodge + depth_back:
                            depth_rest_now = min(depth_base_min - group_depth - depth_dodge - depth_back, MID_GROUP_PASS * 2.0)
                        elif group_depth + depth_rest_new > depth_base_max > group_depth + depth_dodge + depth_back:
                            depth_rest_now = min(depth_base_max - group_depth - depth_dodge - depth_back, MID_GROUP_PASS * 2.0)
                        elif group_depth + depth_rest_new > max(depth_pre_more, depth_post_more) > min(group_depth + depth_dodge + depth_back, 2.0):
                            depth_rest_now = min(max(depth_pre_more, depth_post_more) - group_depth - depth_dodge - depth_back, MID_GROUP_PASS * 2.0)
                            depth_rest_now = max(depth_rest_now, 0)
                        elif depth_rest_new > MID_GROUP_PASS * 2.0:
                            depth_rest_now = MID_GROUP_PASS * 2.0
                        else:
                            depth_rest_now = MID_GROUP_PASS * 1.0
                    elif line_type in [UNIT_TYPE_DOOR] and depth_rest_new > 2 and line_room not in ['Kitchen']:
                        center_flag = 1
                    elif score_pre == 4 and score_post <= 2 and group_depth < depth_pre and ratio_pre < 0.1:
                        if line_idx_pre in line_used:
                            pass
                        else:
                            if group_depth + MID_GROUP_PASS < depth_pre:
                                center_flag = 1
                            depth_rest_now = min(depth_pre - group_depth, MID_GROUP_PASS * 2, group_depth_rest)
                    elif score_pre <= 2 and score_post == 4 and group_depth < depth_post and ratio_post > 0.9:
                        if line_idx_post in line_used:
                            pass
                        else:
                            if group_depth + MID_GROUP_PASS < depth_post:
                                center_flag = 1
                            depth_rest_now = min(depth_post - group_depth, MID_GROUP_PASS * 2, group_depth_rest)
                    # 居中处理
                    if center_flag >= 1:
                        if depth_rest_now > 4.0:
                            depth += max(depth_rest_now / 2, 0)
                            depth_add = max(min(depth_rest_now / 4, MIN_GROUP_PASS * 2), 0)
                        else:
                            depth_rest_now -= MID_GROUP_PASS
                            depth += max(depth_rest_now / 2, 0)
                            depth_add = max(min(depth_rest_now / 4, MIN_GROUP_PASS * 2), 0)
                        group_depth_dump1 = -depth_add * 1
                        group_depth_dump2 = -depth_add * 1
                    else:
                        if ratio_pre < 0 or ratio_post > 1:
                            if group_depth_dump2 < -MIN_GROUP_PASS * 2:
                                group_depth_dump2 = -MIN_GROUP_PASS * 2
                        elif score_pre == 4 and group_depth < depth_pre:
                            depth_add = max(min(depth_rest_now * 1.00, MID_GROUP_PASS * 2), 0)
                            if ratio_pre > 0.1:
                                depth += max(depth_add * 0.75, 0)
                                group_depth_dump1 = -depth_add * 0.25
                                group_depth_dump2 = -depth_add * 0.00
                            else:
                                depth += max(depth_add * 0.25, 0)
                                group_depth_dump1 = -depth_add * 0.25
                                group_depth_dump2 = -depth_add * 0.25
                        elif score_post == 4 and group_depth < depth_post:
                            depth_add = max(min(depth_rest_now * 1.00, MID_GROUP_PASS * 2), 0)
                            if ratio_post < 0.9:
                                depth += max(depth_add * 0.75, 0)
                                group_depth_dump1 = -depth_add * 0.25
                                group_depth_dump2 = -depth_add * 0.00
                            else:
                                depth += max(depth_add * 0.25, 0)
                                group_depth_dump1 = -depth_add * 0.25
                                group_depth_dump2 = -depth_add * 0.25
                        elif depth_rest_now >= MID_GROUP_PASS * 1:
                            if vertical_flag == 0:
                                if depth_rest_now >= MID_GROUP_PASS * 2.0 and len(param_list) <= 1:
                                    depth_add = max(min(depth_rest_now * 0.5, MID_GROUP_PASS), 0)
                                    depth += max(depth_add * 1.00, 0)
                                    group_depth_dump1 = -depth_add * 0.50
                                    group_depth_dump2 = -depth_add * 0.50
                                else:
                                    depth_add = max(min(depth_rest_now * 0.5, MID_GROUP_PASS), 0)
                                    group_depth_dump2 = -depth_add * 0.50
                            elif vertical_flag == 1:
                                if depth_rest_now >= MID_GROUP_PASS * 3.0 or max(group_depth_rest1, group_depth_rest2) > 0.1:
                                    depth_add = max(min(depth_rest_now * 0.5, MID_GROUP_PASS), 0)
                                    depth += max(depth_add * 1.00, 0)
                                    group_depth_dump1 = -depth_add * 0.50
                                    group_depth_dump2 = -depth_add * 0.50
                                else:
                                    depth_add = max(min(depth_rest_now * 0.5, MID_GROUP_PASS), 0)
                                    group_depth_dump2 = -depth_add * 0.50
                            elif window_flag == 1:
                                depth_add = max(min(depth_rest_now * 0.5, MID_GROUP_PASS), 0)
                                depth += max(depth_add * 1.00, 0)
                                group_depth_dump2 = -depth_add
                # 书桌居中
                elif group_type in ['Work'] and room_type in ['Library'] and depth_rest_new > MID_GROUP_PASS and room_area > 8:
                    depth_add = depth_rest_new / 2
                    if line_type == UNIT_TYPE_WINDOW and line_height >= 0.5:
                        group_depth_dump2 = -depth_rest_new / 4
                    elif group_height >= UNIT_HEIGHT_TABLE_MAX:
                        depth_add, center_flag = 0, 0
                    elif group_width_rest <= MIN_GROUP_PASS:
                        group_depth_dump2 = -depth_rest_new / 4
                        if room_area <= 8 and line_width >= 2:
                            depth += depth_add
                    elif group_ratio[0] < -0.1 or group_ratio[1] > 1.1:
                        depth_add = depth_rest_new * 0.25
                        if depth_add > MID_GROUP_PASS:
                            depth_add = MID_GROUP_PASS
                        if depth_add * 0.50 < MIN_GROUP_PASS:
                            depth_add = 0
                        depth += depth_add
                        group_depth_dump1 = -depth_add * 0.50
                        group_depth_dump2 = -depth_add * 0.50
                    elif group_width > 1.5 > group_width_min * 1.5:
                        depth_add, center_flag = 0, 0
                    else:
                        center_flag = 1
                        depth_add = depth_rest_new / 2
                        angle_add = math.pi
                        if depth_add > MID_GROUP_PASS:
                            depth_add = MID_GROUP_PASS
                        if group_width < group_depth:
                            depth_add = depth_rest_new / 8
                        depth += depth_add
                        group_depth_dump1 = -depth_rest_new / 8
                        group_depth_dump2 = -depth_rest_new / 8
                        group_angle += angle_add
                # 休闲居中
                elif group_type == 'Rest' and depth_rest_new > MID_GROUP_PASS and group_width_rest > 0:
                    depth_add = (depth_rest_new - depth_back) / 2
                    if group_ratio[0] < -0.1 or group_ratio[1] > 1.1:
                        depth_add = (depth_rest_new - depth_back) / 4
                        depth += depth_add
                        group_depth_dump1 = -depth_rest_new / 8
                        group_depth_dump2 = -depth_rest_new / 8
                    else:
                        center_flag = 1
                        depth_add = (depth_rest_new - depth_back) / 2
                        angle_add = math.pi
                        if depth_add > MIN_GROUP_PASS * 2:
                            depth_add = MIN_GROUP_PASS * 2
                        if group_width < group_depth:
                            depth_add = depth_rest_new / 8
                        depth += depth_add
                        group_depth_dump1 = -depth_rest_new / 8
                        group_depth_dump2 = -depth_rest_new / 8
                        group_angle += angle_add
                elif group_type == 'Rest' and depth_rest_new > 0 and group_width_rest > 0 and window_flag >= 1:
                    angle_add = math.pi
                    group_depth_dump1 = -depth_rest_new / 8
                    group_depth_dump2 = -depth_rest_new / 8
                    group_angle += angle_add
                # 对调居中
                elif abs(angle_swap - math.pi) < 0.1:
                    center_flag = 1
                    if depth_rest_new + group_depth_dump2 > UNIT_DEPTH_CURTAIN:
                        group_depth_dump1 = -min(UNIT_DEPTH_CURTAIN / 2, (depth_rest_new + group_depth_dump2) / 2)
                    else:
                        group_depth_dump1 = 0
                    depth += (depth_swap - group_depth)

                # 纵向位置
                depth_rest_new += group_depth_dump1
                depth_rest_new += group_depth_dump2
                x_delta, y_delta = depth * math.sin(angle), depth * math.cos(angle)
                po = [pp[0] + x_delta, pp[1] + y_delta]

                # 更新范围
                size_rest_0 = -group_depth_dump1
                size_rest_1 = min(-group_width_dump1, MID_GROUP_PASS * 1.5)
                size_rest_2 = -group_depth_dump2
                size_rest_3 = min(-group_width_dump2, MID_GROUP_PASS * 1.5)
                if abs(angle_swap - math.pi) < 0.1 and group_depth_max * 0.5 >= depth_swap:
                    size_rest_0 += min(group_depth_max * 0.5 - depth_swap, UNIT_DEPTH_GROUP_MID)

                # 更新位置
                group_angle += angle_swap
                group_one['position'] = [po[0], group_one['position'][1], po[1]]
                group_one['rotation'] = [0, math.sin(group_angle / 2), 0, math.cos(group_angle / 2)]
                group_one['regulation'] = [size_rest_0, size_rest_1, size_rest_2, size_rest_3]
                if vertical_flag == 1:
                    group_one = spin_exist_group(group_one, 1)
                    group_ang = group_angle - math.pi / 2
                    group_one['rotation'] = [0, math.sin(group_ang / 2), 0, math.cos(group_ang / 2)]
                # 特别信息
                group_one['vertical'] = vertical_flag
                group_one['window'] = window_flag
                group_one['center'] = center_flag
                # 区域信息
                group_one['region_direct'] = ratio_dir
                group_one['region_beside'] = [score_pre_new, score_post_new]
                pass
                # 新增组合
                group_result.append(group_one)

            # 更新参数
            param_one['ratio'] = [ratio_pre, ratio_post]
            param_one['width_rest'] = width_rest_new
            param_one['depth_rest'] = depth_rest_new

    # 返回信息
    return group_result


# 成对功能区域布局
def room_rect_layout_pair(param_old, group_new, line_list, line_used, line_face,
                          max_pass=-1, min_pass=-1, room_type='', room_area=10, door_pt_entry=[]):
    index_face = {}
    # 原有组合
    index_old = param_old['index']
    line_old = line_list[index_old]
    depth_pre, depth_post = line_old['depth_pre'], line_old['depth_post']
    angle_old, stand_old = line_old['angle'], determine_line_angle(line_old['angle'])
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
    # 对面组合
    group_size = group_new['size']
    seed_size = group_size[:]
    if 'seed_size_new' in group_new and len(group_new['seed_size_new']) >= 3:
        seed_size = group_new['seed_size_new']

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
    # 线段遍历
    width_idx, width_max, depth_max = -1, 0, 10
    depth_idx, depth_min = -1, 10
    for line_idx, line_one in enumerate(line_list):
        # 线段计算
        width_new, depth_new, ratio_new, ratio_new_best, ratio_face = compute_pair_ratio(line_old, ratio_old, line_one)
        if len(ratio_new) <= 0 or width_new <= 0.5:
            continue
        if len(ratio_face) >= 2:
            width_face = line_old['width'] * (ratio_face[1] - ratio_face[0])
            if width_face < min(width_old * 0.2, 1.5):
                continue
        # 线段调整
        if abs(ratio_new[0] - 0) < 0.01:
            ratio_new[0] = 0
        if abs(ratio_new[1] - 1) < 0.01:
            ratio_new[1] = 1
        line_side_1 = line_list[(line_idx - 1 + len(line_list)) % len(line_list)]
        line_side_2 = line_list[(line_idx + 1 + len(line_list)) % len(line_list)]
        # 扩展
        if width_new < seed_size[0] and ratio_new[0] > 0:
            ratio_min = max(0, ratio_new[0] - (seed_size[0] - width_new) / line_one['width'])
            width_new += (ratio_new[0] - ratio_min) * line_one['width']
            ratio_new[0] = ratio_min
        if width_new < seed_size[0] and abs(ratio_new[0] - 0) < 0.01 and line_one['score_pre'] == 1:
            if line_side_1['type'] in [UNIT_TYPE_AISLE, UNIT_TYPE_WALL] and line_side_1['depth'] >= depth_new:
                width_add = min(line_side_1['width'], seed_size[0] - width_new)
                ratio_min = 0 - width_add / line_one['width']
                width_new += width_add
                ratio_new[0] = ratio_min
        if width_new < seed_size[0] and ratio_new[1] < 1:
            ratio_max = min(1, ratio_new[1] + (seed_size[0] - width_new) / line_one['width'])
            width_new += (ratio_max - ratio_new[1]) * line_one['width']
            ratio_new[1] = ratio_max
        if width_new < seed_size[0] and abs(ratio_new[1] - 1) < 0.01 and line_one['score_post'] == 1:
            if line_side_2['type'] in [UNIT_TYPE_AISLE, UNIT_TYPE_WALL] and line_side_2['depth'] >= depth_new:
                width_add = min(line_side_2['width'], seed_size[0] - width_new)
                ratio_max = 1 + width_add / line_one['width']
                width_new += width_add
                ratio_new[1] = ratio_max
        # 深度最小
        if depth_new < depth_min:
            depth_idx, depth_min = line_idx, depth_new
        # 两侧过小
        line_idx_pre = (line_idx - 1 + len(line_list)) % len(line_list)
        line_idx_post = (line_idx + 1 + len(line_list)) % len(line_list)
        line_pre, line_post = line_list[line_idx_pre], line_list[line_idx_post]
        if width_new <= 1.5 and depth_new <= 3:
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
        elif width_new > min(width_max * 1.0, width_old) and max_pass < depth_rest:
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
            if depth_rest < -0.1 and depth_old - depth_old_min > 0.2 - depth_rest:
                depth_rest = 0
                param_old['depth_rest'] = depth_old_min + 0.2 - depth_old
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
    line_pair_1 = line_list[(index_pair - 1 + len(line_list)) % len(line_list)]
    line_pair_2 = line_list[(index_pair + 1 + len(line_list)) % len(line_list)]
    pair_width, pair_depth, pair_merge = 0, 0, 0
    if 'width' in line_pair:
        pair_width = line_pair['width']
    if 'depth' in line_pair:
        pair_depth = line_pair['depth']
    face_depth = 0
    if 'depth_face' in param_pair:
        face_depth = param_pair['depth_face']
    # 对面
    if line_pair['type'] not in [UNIT_TYPE_WALL]:
        type_old, size_old = group_old['type'], group_old['size']
        if type_old not in ['Meeting']:
            return {}, index_face
        elif pair_width < width_old_min:
            if face_depth < max(2.0, depth_old_min) + 0.5 and room_area > 10:
                return {}, index_face
        elif pair_width > min(width_old_min, 3):
            pass
        elif pair_depth > max_pass * 0.5:
            return {}, index_face
    elif line_pair['score_pre'] == 1 and line_pair_1['type'] in [UNIT_TYPE_WINDOW] or \
            line_pair['score_post'] == 1 and line_pair_2['type'] in [UNIT_TYPE_WINDOW]:
        ratio_face = param_pair['ratio_face']
        if ratio_face[1] - ratio_face[0] <= 0.8:
            pair_merge = UNIT_TYPE_WINDOW
    elif line_pair['score_pre'] == 1 and line_pair_1['type'] in [UNIT_TYPE_DOOR] or \
            line_pair['score_post'] == 1 and line_pair_2['type'] in [UNIT_TYPE_DOOR]:
        ratio_face = param_pair['ratio_face']
        if ratio_face[1] - ratio_face[0] <= 0.8:
            pair_merge = UNIT_TYPE_DOOR
    # 删除判断
    if 'adjust' in group_new and group_new['adjust'] >= 1:
        if pair_width < 1.5:
            return {}, index_face

    # 对调判断
    width_new, depth_new = group_size[0], group_size[2]
    type_swap, depth_add = 0, MID_GROUP_PASS
    if room_area < MAX_ROOM_AREA_LIVING * 0.5:
        depth_add = MIN_GROUP_PASS * 2
    elif room_area < MAX_ROOM_AREA_LIVING * 1.5:
        depth_add = MIN_GROUP_PASS * 4
    width_swap, depth_swap = param_pair['width'], max(depth_old, 1.5) + depth_new + depth_add
    width_face, depth_face = max(width_old, width_new, 2.5), param_pair['depth_face']
    width_most = param_old['width'] + param_old['width_rest']
    depth_most = param_old['depth'] + param_old['depth_rest']
    ratio_most = param_old['ratio'][:]
    if line_pair['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
        depth_face -= UNIT_DEPTH_CURTAIN
    depth_group = depth_old + depth_new + MIN_GROUP_PASS
    if room_area > MAX_ROOM_AREA_LIVING or (depth_face > 4 and room_area > MAX_ROOM_AREA_LIVING * 0.5):
        depth_group = min(max(2.5, depth_group), 4.0)
        depth_ratio = 1.00
        if room_type in ['LivingRoom']:
            depth_ratio = min(depth_group + MID_GROUP_PASS * 2, depth_face - 1.0) / depth_face
        elif depth_face * 0.50 > depth_face - 3 > depth_group + MID_GROUP_PASS:
            depth_ratio = 0.5
        elif depth_face - 3 > depth_group:
            depth_ratio = min(depth_group + MID_GROUP_PASS, depth_face - 3) / depth_face
            if depth_group < depth_pre < depth_face - 3:
                depth_ratio = depth_pre / depth_face
            elif depth_group < depth_post < depth_face - 3:
                depth_ratio = depth_post / depth_face
            elif depth_group < depth_pre < depth_face - 2:
                depth_ratio = min(depth_group + MID_GROUP_PASS * 3, depth_pre) / depth_face
            elif depth_group < depth_post < depth_face - 2:
                depth_ratio = min(depth_group + MID_GROUP_PASS * 3, depth_post) / depth_face
            elif depth_face * width_face <= min(room_area - 15, room_area * 0.3):
                depth_ratio = min(depth_group + MID_GROUP_PASS * 3, depth_face - 1.0) / depth_face
        elif depth_face - 2 > depth_group:
            depth_ratio = min(depth_group + MIN_GROUP_PASS, depth_face - 2) / depth_face
            if depth_face * width_face <= min(room_area - 15, room_area * 0.3):
                depth_ratio = min(depth_group + MID_GROUP_PASS * 3, depth_face - 1.0) / depth_face
        elif depth_face * 0.50 > depth_group:
            depth_ratio = min(depth_group + MIN_GROUP_PASS, depth_face * 0.5) / depth_face
        #
        elif depth_face * width_face >= room_area - 10 and depth_face >= 4 and room_type in ['LivingDiningRoom']:
            depth_ratio = min(depth_group + MID_GROUP_PASS, depth_face - 2) / depth_face
        elif depth_face * width_face >= room_area * 0.7 and depth_face >= 4 and room_type in ['LivingDiningRoom']:
            depth_ratio = min(depth_group + MID_GROUP_PASS, depth_face - 2) / depth_face
        #
        elif line_pair['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and pair_width > UNIT_WIDTH_DOOR * 1.5:
            if depth_face * width_face >= room_area - 20 and depth_face - 2.5 > depth_old:
                depth_ratio = min(depth_group + MIN_GROUP_PASS * 1, depth_face - 2.5) / depth_face
            elif depth_face * width_face >= room_area * 0.7 and depth_face - 2.5 > depth_old:
                depth_ratio = min(depth_group + MIN_GROUP_PASS * 1, depth_face - 2.5) / depth_face
            else:
                depth_ratio = min(depth_group + MID_GROUP_PASS * 1, depth_face - 0.2) / depth_face
        elif width_old > pair_width and pair_merge >= 1:
            if pair_merge == UNIT_TYPE_WINDOW:
                depth_ratio = min(depth_group + MID_GROUP_PASS, depth_face - UNIT_DEPTH_CURTAIN) / depth_face
            elif pair_merge == UNIT_TYPE_DOOR and depth_face - UNIT_WIDTH_DODGE > min(depth_group + MID_GROUP_PASS, 3):
                depth_ratio = min(depth_group + MID_GROUP_PASS, depth_face - UNIT_WIDTH_DODGE) / depth_face
            else:
                depth_ratio = (depth_group + MID_GROUP_PASS) / depth_face
                if depth_ratio + MID_GROUP_PASS / depth_face > 0.9:
                    depth_ratio = 1.0
        else:
            depth_ratio = (depth_group + MID_GROUP_PASS * 1) / depth_face
            if depth_ratio + MID_GROUP_PASS / depth_face > 0.9:
                depth_ratio = 1.0
        depth_well = depth_face * depth_ratio - depth_old - depth_new
        depth_swap = depth_old + depth_new + min(depth_well, MID_GROUP_PASS * 3)
    if depth_swap + 0.4 >= depth_face and pair_merge <= 0:
        depth_swap = depth_face
    else:
        depth_all = line_old['depth_all']
        for depth_one in depth_all:
            if 2 < depth_one[2] < depth_min:
                depth_min = depth_one[2]
        if depth_face - 2.0 > depth_min > depth_group + 0.5 and pair_width < width_old + MID_GROUP_PASS:
            depth_swap = depth_min - 1.0
        elif depth_group < depth_min < depth_swap:
            depth_swap = depth_min
        elif depth_group < depth_min + depth_old < depth_face - 2:
            depth_swap = depth_min + depth_old
        elif depth_group < depth_min + depth_old_min < depth_face - 2:
            depth_swap = depth_min + depth_old_min

    # 对调类型
    if 'seed_center' in group_old and group_old['seed_center'] >= 1:
        pass
    elif param_pair['depth_rest'] > max_pass * 0.5 and group_old['type'] in ['Meeting']:
        if line_pair['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and depth_swap <= depth_face:
            if line_old['type'] not in [UNIT_TYPE_WALL]:
                return {}, index_face
            depth_swap = min(depth_swap, depth_face)
            type_swap = 1
        elif depth_swap >= depth_face + 0.1:
            return {}, index_face
        elif depth_swap >= depth_face - 1.0:
            if line_old['type'] not in [UNIT_TYPE_WALL]:
                pass
            elif pair_merge == UNIT_TYPE_WINDOW:
                type_swap = 1
            elif pair_merge == UNIT_TYPE_DOOR and depth_swap > max(depth_old, 1.5) + depth_new + MID_GROUP_PASS * 1:
                type_swap = 1
        elif depth_swap <= depth_face - 0.1:
            if line_old['type'] not in [UNIT_TYPE_WALL]:
                if depth_face - 3 > depth_group:
                    return {}, index_face
            elif depth_swap < depth_min - 1.5:
                depth_swap = min(depth_swap, depth_min)
                type_swap = 1
            elif depth_swap <= depth_min < depth_face - 0.1:
                depth_swap = min(depth_swap, depth_min)
                type_swap = 1
            elif depth_swap < depth_face - 1.0:
                type_swap = 1
    elif param_pair['depth_rest'] > min_pass and group_old['type'] in ['Meeting']:
        line_pair = line_list[index_pair]
        line_side_1 = line_list[(index_pair - 1 + len(line_list)) % len(line_list)]
        line_side_2 = line_list[(index_pair + 1 + len(line_list)) % len(line_list)]
        if line_pair['type'] in [UNIT_TYPE_DOOR]:
            if line_pair['width'] < UNIT_WIDTH_HOLE:
                depth_swap = param_pair['depth_face'] - UNIT_DEPTH_DODGE
                type_swap = 1
            else:
                depth_swap = param_pair['depth_face'] - UNIT_DEPTH_CURTAIN
                type_swap = 1
        elif line_pair['type'] in [UNIT_TYPE_WINDOW]:
            if line_pair['width'] >= UNIT_WIDTH_HOLE or param_pair['width'] > width_old:
                depth_swap = param_pair['depth_face'] - UNIT_DEPTH_CURTAIN
                type_swap = 1
            else:
                return {}, index_face
        elif line_pair['type'] in [UNIT_TYPE_WALL] and line_pair['score'] == 2:
            line_type_1, line_type_2 = line_side_1['type'], line_side_2['type']
            if line_type_1 in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and \
                    line_type_2 in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                if depth_swap <= depth_face - 0.1 or ratio_old_best[0] > 0.1 or ratio_old_best[1] < 0.9:
                    if pair_width < min(width_new, 2.0):
                        return {}, index_face
                elif depth_swap <= depth_face - 1.0:
                    depth_swap = depth_face - 1.0
                    type_swap = 1
            elif depth_swap >= depth_face - 1.0:
                if pair_merge == UNIT_TYPE_DOOR:
                    pass
                elif pair_merge == UNIT_TYPE_WINDOW:
                    type_swap = 1
    elif group_old['type'] in ['Meeting']:
        if line_pair['type'] in [UNIT_TYPE_WINDOW, UNIT_TYPE_DOOR]:
            if line_pair['width'] >= UNIT_WIDTH_HOLE or param_pair['width'] > width_old:
                depth_swap = param_pair['depth_face'] - UNIT_DEPTH_CURTAIN
                type_swap = 1
            else:
                return {}, index_face
    # 种子信息
    seed_center = 0
    if 'seed_position' in group_old and 'seed_center' in group_old:
        seed_position = group_old['seed_position']
        seed_center = group_old['seed_center']
        if seed_center <= 0:
            width_swap = width_old
            depth_swap = min(depth_face, depth_old + depth_new + MID_GROUP_PASS * 2)
            type_swap = 0
        elif seed_center >= 1:
            width_swap = width_old
            depth_swap = min(depth_face, depth_old + depth_new + MID_GROUP_PASS * 1)
            p1, p2 = line_old['p1'], seed_position
            dis, ang = xyz_to_ang(p1[0], p1[1], p2[0], p2[2])
            depth_seed = abs(dis * math.sin(ang - line_old['angle'])) + depth_old_min / 2
            if depth_old < depth_seed < depth_face:
                depth_swap = depth_seed
            type_swap = 1
    # 对调信息
    ratio_face = param_pair['ratio_face'][:]
    ratio_cent = (ratio_face[0] + ratio_face[1]) * 0.5
    width_well = max(width_old, width_new) + MID_GROUP_PASS * 2
    width_rest = param_old['width_rest']
    depth_rest = depth_swap - depth_old - depth_new
    if width_swap < max(width_old, width_new) + MID_GROUP_PASS * 1:
        width_well = max(width_old, width_new) + MID_GROUP_PASS * 1
    if width_most > width_swap:
        if depth_most < depth_swap:
            ratio_most = ratio_face[:]
            width_rest = width_swap - width_old
        elif abs(ratio_face[0] - 0) > 0.2 and abs(ratio_face[1] - 1) > 0.2:
            ratio_face = ratio_most[:]
            width_swap = line_old['width'] * (ratio_face[1] - ratio_face[0])
        elif abs(ratio_face[0] - 0) < abs(ratio_face[1] - 1) and type_swap >= 1:
            ratio_face[1] = min(ratio_face[0] + width_well / line_old['width'], ratio_most[1])
            ratio_most[1] = min(ratio_most[1], ratio_face[1])
            width_swap = line_old['width'] * (ratio_face[1] - ratio_face[0])
        elif abs(ratio_face[1] - 1) < abs(ratio_face[0] - 0) and type_swap >= 1:
            ratio_face[0] = max(ratio_face[1] - width_well / line_old['width'], ratio_most[0])
            ratio_face[0] = max(ratio_most[0], ratio_face[0])
            width_swap = line_old['width'] * (ratio_face[1] - ratio_face[0])
        elif ratio_cent < 0.4 and ratio_face[0] + width_well / line_old['width'] < ratio_most[1]:
            if ratio_face[0] + width_old / line_old['width'] < ratio_old_best[1]:
                ratio_face[1] = ratio_old_best[1]
            else:
                ratio_face[1] = min(ratio_face[0] + width_well / line_old['width'], ratio_most[1])
            ratio_most[1] = min(ratio_most[1], ratio_face[1])
            width_swap = line_old['width'] * (ratio_face[1] - ratio_face[0])
        elif ratio_cent > 0.6 and ratio_face[1] - width_well / line_old['width'] > ratio_most[0]:
            if ratio_face[1] - width_old / line_old['width'] > ratio_old_best[0]:
                ratio_face[0] = ratio_old_best[0]
            else:
                ratio_face[0] = max(ratio_face[1] - width_well / line_old['width'], ratio_most[0])
            ratio_most[0] = max(ratio_most[0], ratio_face[0])
            width_swap = line_old['width'] * (ratio_face[1] - ratio_face[0])

    if type_swap > 0:
        # 对面组合 参数1
        param_pair['index'] = param_old['index']
        param_pair['ratio'] = ratio_face[:]
        param_pair['width_rest'] = width_swap - width_new
        param_pair['depth_rest'] = max(depth_rest, 0)
        # 对面组合 参数2
        param_pair['index_swap'] = index_pair
        param_pair['type_swap'] = type_swap
        param_pair['width_swap'] = width_swap
        param_pair['depth_swap'] = depth_swap
        param_pair['ratio_swap'] = ratio_face[:]
        param_pair['ratio_best'] = ratio_face[:]
        # 对面占用
        line_face[index_pair] = depth_face - depth_swap
    else:
        # 对面占用
        line_face[index_pair] = 0
    # 原有组合
    param_old['index_pair'] = index_pair
    param_old['ratio_pair'] = ratio_face[:]
    param_old['ratio_best'] = ratio_face[:]
    if type_swap > 0:
        # 原有组合 参数1
        param_old['ratio'] = ratio_most[:]
        param_old['width_rest'] = width_rest
        param_old['depth_rest'] = depth_rest
        # 原有组合 参数2
        param_old['index_swap'] = param_old['index']
        param_old['type_swap'] = type_swap
        param_old['width_swap'] = width_swap
        param_old['depth_swap'] = depth_swap
        param_old['ratio_swap'] = ratio_face[:]
    else:
        param_old['depth_rest'] = depth_rest
    if width_swap > width_old:
        width_well = max(width_old, width_new) + MID_GROUP_PASS * 2
        ratio_0, ratio_1 = ratio_old[0], ratio_old[1]
        if abs(ratio_face[0] - ratio_0) <= 0.01 and abs(ratio_face[1] - ratio_1) <= 0.01:
            pass
        elif ratio_face[1] >= 1 > ratio_face[0]:
            ratio_0 = max(ratio_face[1] - width_well / line_old['width'], ratio_old[0])
            param_old['ratio'] = [ratio_0, ratio_1]
        elif ratio_face[0] <= 0 < ratio_face[1]:
            ratio_1 = min(ratio_face[0] + width_well / line_old['width'], ratio_old[1])
            param_old['ratio'] = [ratio_0, ratio_1]
        else:
            param_old['ratio'] = ratio_face[:]
        width_suit = line_old['width'] * (ratio_1 - ratio_0)
        param_old['width_rest'] = width_suit - param_old['width']

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
    if type_swap >= 1:
        index_face = {}
    return param_add, index_face


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
    group_add = group_one.copy()
    group_size = group_one['size']
    group_add['size'] = [group_size[2], group_size[1], group_size[0]]
    group_add['offset'] = group_one['offset'][:]
    group_add['position'] = group_one['position'][:]
    group_add['rotation'] = group_one['rotation'][:]
    if 'size_min' in group_one:
        group_size_min = group_one['size_min']
        group_add['size_min'] = [group_size_min[2], group_size_min[1], group_size_min[0]]
    if 'size_rest' in group_one:
        group_size_rest = group_one['size_rest']
        if spin <= -1:
            group_add['size_rest'] = [group_size_rest[1], group_size_rest[2], group_size_rest[3], group_size_rest[0]]
        else:
            group_add['size_rest'] = [group_size_rest[3], group_size_rest[0], group_size_rest[1], group_size_rest[2]]
    if 'regulation' in group_one:
        group_size_fix = group_one['regulation']
        if spin <= -1:
            group_add['regulation'] = [group_size_fix[1], group_size_fix[2], group_size_fix[3], group_size_fix[0]]
        else:
            group_add['regulation'] = [group_size_fix[3], group_size_fix[0], group_size_fix[1], group_size_fix[2]]
    if 'seed_list' in group_one:
        group_add['seed_list'] = group_one['seed_list'][:]
    group_add['obj_list'] = []
    return group_add
