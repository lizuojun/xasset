# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-22
@Description: 全屋矩形分析计算

"""

import math

# 部件参数
UNIT_TYPE_NONE = 0
UNIT_TYPE_GROUP = 1
UNIT_TYPE_DOOR = 2
UNIT_TYPE_SIDE = 3
UNIT_TYPE_WINDOW = 4
UNIT_TYPE_AISLE = 5
UNIT_TYPE_WALL = 6
# 部件参数
UNIT_WIDTH_GROUP = 1.5
UNIT_DEPTH_GROUP = 1.0
UNIT_WIDTH_GROUP_MAX = 5.0
UNIT_WIDTH_GROUP_MIN = 0.4
UNIT_DEPTH_GROUP_MAX = 4.0
UNIT_DEPTH_GROUP_MIN = 0.2
UNIT_DEPTH_GROUP_MID = 0.6
# 部件参数
UNIT_WIDTH_DOOR = 0.85
UNIT_WIDTH_HOLE = 1.50
UNIT_WIDTH_AISLE = 1.50
UNIT_WIDTH_DOOR_FRAME = 0.05
# 部件参数
UNIT_WIDTH_WALL_MIN = 0.05
UNIT_DEPTH_WALL_INSIDE = 0.12
UNIT_DEPTH_WALL_OUTSIDE = 0.24
# 部件参数
UNIT_DEPTH_BACK_ERR = 9.0
UNIT_DEPTH_BACK_MID = 0.1
UNIT_DEPTH_BACK_MAX = 0.5
# 部件参数
UNIT_WIDTH_DODGE = 0.85
UNIT_DEPTH_DODGE = 0.85
UNIT_DEPTH_ASIDE = 0.85
UNIT_WIDTH_MERGE = 0.30
UNIT_WIDTH_MERGE_MAX = 0.60
UNIT_WIDTH_MERGE_MIN = 0.15
# 部件参数
UNIT_WIDTH_CURTAIN = 0.50
UNIT_DEPTH_CURTAIN = 0.23
UNIT_WIDTH_CURTAIN_SIDE = 0.23
UNIT_HEIGHT_CURTAIN_BOT = 0.15
# 部件参数
UNIT_HEIGHT_WALL = 2.8
UNIT_HEIGHT_CEIL = 0.15
UNIT_HEIGHT_CEIL_MAX = 0.3
UNIT_HEIGHT_DOOR_TOP = 2.05
UNIT_HEIGHT_WINDOW_TOP = 2.4
UNIT_HEIGHT_WINDOW_BOTTOM = 0.4
UNIT_HEIGHT_GROUP = 1
# 部件参数
UNIT_WIDTH_ARMOIRE_MIN = 1.0
UNIT_WIDTH_ARMOIRE_MID = 1.5
UNIT_DEPTH_ARMOIRE_MIN = 0.2
UNIT_DEPTH_ARMOIRE_MID = 0.5
UNIT_HEIGHT_ARMOIRE_MIN = 1.5
UNIT_HEIGHT_ARMOIRE_MID = 1.8
# 部件参数
UNIT_RATIO_RATIO_1 = 0
UNIT_RATIO_RATIO_2 = 1
UNIT_RATIO_DEPTH = 2
UNIT_RATIO_HEIGHT = 3
UNIT_RATIO_INDEX = 4
UNIT_RATIO_MARGIN = 5
UNIT_RATIO_EDGE = 6
UNIT_RATIO_TYPE = 7
UNIT_RATIO_GROUP = 8
UNIT_RATIO_TO_ROOM = 9
# 房间参数
MIN_ROOM_AREA = 1.5
MID_ROOM_AREA_BATH = 6.0
MID_ROOM_AREA_CLOAK = 5.0
MAX_ROOM_AREA_LIVING = 30
MID_ROOM_AREA_LIVING = 20
MIN_ROOM_AREA_LIVING = 10

# 房间类型
ROOM_TYPE_LEVEL_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library']
ROOM_TYPE_LEVEL_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
ROOM_TYPE_LEVEL_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom', 'Kitchen',
                     'Balcony', 'Terrace', 'Lounge', 'Auditorium',
                     'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                     'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom']
ROOM_TYPE_LEVEL_4 = ['Hallway', 'Aisle', 'Corridor', 'Stairwell',
                     'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom']


# 轮廓分析 全屋分析
def house_rect(data_info, room_list=[], unit_dict={}):
    # 矩形信息
    house_rect_info = {}

    # 房间类型
    room_type_all = {}
    for room_info in data_info['room']:
        room_type_all[room_info['id']] = room_info['type']
    # 门口位置
    door_main = {}
    for room_info in data_info['room']:
        door_list = []
        if 'door_info' in room_info and len(room_info['door_info']) > 0:
            for door_one in room_info['door_info']:
                door_list.append(door_one)
        if 'hole_info' in room_info and len(room_info['hole_info']) > 0:
            for door_one in room_info['hole_info']:
                door_list.append(door_one)
        # 入户门
        if len(door_main) <= 0:
            for door_one in door_list:
                door_to_id = door_one['to']
                if door_to_id == '':
                    door_main = door_one
                    break
    # 门口位置
    door_main_pt = []
    if 'pts' in door_main:
        door_point = door_main['pts']
        door_main_pt = [(door_point[0] + door_point[2] + door_point[4] + door_point[6]) / 4,
                        (door_point[1] + door_point[3] + door_point[5] + door_point[7]) / 4]

    # 遍历房间
    room_list = data_info['room']
    for room_info in room_list:
        room_id = room_info['id']
        if len(room_list) > 0 and room_id not in room_list:
            continue
        room_type = room_info['type']
        room_area = round(float(room_info['area']), 1)
        type_list, unit_list, height_list = [], [], []
        if room_id in unit_dict:
            unit_list = unit_dict[room_id]['unit']
            height_list = unit_dict[room_id]['height']
        room_rect_all = room_rect(room_info, type_list, unit_list, height_list, [], room_type, room_area, door_main_pt)
        house_rect_info[room_id] = {
            'room_type': room_info['type'],
            'room_size': room_info['area'],
            'room_rect': room_rect_all
        }
    # 返回信息
    return house_rect_info


# 轮廓分析 单屋分析
def room_rect(room_info, type_list=[], unit_list=[], height_list=[], back_list=[],
              room_type='', room_area=10, main_door=[], open_unit=[UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]):
    # 线段分析
    line_list, line_list_ori = room_line(room_info, type_list, unit_list, height_list, back_list,
                                         room_type, room_area, main_door, open_unit)
    # 矩形方案
    rect_info_all = room_rect_of_line(room_info, line_list)
    # 返回信息
    return rect_info_all


# 轮廓分析 单屋分析
def room_rect_of_line(room_info, line_list):
    # 矩形方案
    rect_info_all, rect_info_one = [], {'rect': [], 'line': []}

    # 线段分析
    room_type, room_area = '', 0
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    ratio_min = 1.0
    if room_type in ROOM_TYPE_LEVEL_3:
        ratio_min = 0.5
    if 0 < room_area < MIN_ROOM_AREA * ratio_min:
        rect_info_one['line'] = line_list
        rect_info_all.append(rect_info_one)
        return rect_info_all

    # 线段选择
    fine_list, todo_list = [], []
    for line_idx in range(len(line_list)):
        line_cur = line_list[line_idx]
        line_type, line_width, line_depth = line_cur['type'], line_cur['width'], line_cur['depth']
        line_score, score_pre, score_post = line_cur['score'], line_cur['score_pre'], line_cur['score_post']
        if line_score >= 8 and line_width < 1.0 and line_depth <= UNIT_DEPTH_GROUP_MIN:
            line_score = 5
        # 排除
        if line_type in [UNIT_TYPE_GROUP, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
            pass
        elif line_type in [UNIT_TYPE_SIDE] and line_width > 1 and 0.1 < line_depth:
            pass
        else:
            continue
        # 家具
        if line_type == UNIT_TYPE_GROUP:
            if line_cur['unit_flag'] >= 1:
                if line_cur['unit_edge'] in [1, 3] and line_cur['width'] < min(line_cur['depth'] * 0.5, 1.0):
                    continue
                else:
                    fine_list.append(line_idx)
            continue
        # 排除
        if line_width < UNIT_DEPTH_GROUP_MIN / 2:
            continue
        # 前段
        index_side1 = (line_idx - 1 + len(line_list)) % len(line_list)
        line_side1 = line_list[index_side1]
        type_side1, score_side1 = line_side1['type'], line_side1['score']
        width_side1, depth_side1 = line_side1['width'], line_side1['depth']
        if score_side1 >= 8 and width_side1 < 1.0 and depth_side1 <= UNIT_DEPTH_GROUP_MIN:
            score_side1 = 5
        elif type_side1 in [UNIT_TYPE_DOOR]:
            score_side1 = 2
        # 前前段
        index_side1_pre = (line_idx - 2 + len(line_list)) % len(line_list)
        line_side1_pre = line_list[index_side1_pre]
        # 后段
        index_side2 = (line_idx + 1) % len(line_list)
        line_side2 = line_list[index_side2]
        type_side2, score_side2 = line_side2['type'], line_side2['score']
        width_side2, depth_side2 = line_side2['width'], line_side2['depth']
        if score_side2 >= 8 and width_side2 < 1.0 and depth_side2 <= UNIT_DEPTH_GROUP_MIN:
            score_side2 = 5
        elif type_side2 in [UNIT_TYPE_DOOR]:
            score_side2 = 2
        # 后后段
        index_side2_post = (line_idx + 2) % len(line_list)
        line_side2_post = line_list[index_side2_post]
        # 墙壁 窗户
        if 0 <= line_score <= 4:
            if score_pre == 1 and type_side1 == UNIT_TYPE_SIDE and width_side1 <= UNIT_DEPTH_CURTAIN + 0.01:
                if line_width >= UNIT_WIDTH_GROUP_MIN and line_width > line_side1_pre['width']:
                    fine_list.append(line_idx)
                    if index_side1_pre in fine_list and line_side1_pre['width'] < line_width:
                        todo_list.append(index_side1_pre)
                else:
                    todo_list.append(line_idx)
            elif score_post == 1 and type_side2 == UNIT_TYPE_SIDE and width_side2 <= UNIT_DEPTH_CURTAIN + 0.01:
                if line_width >= UNIT_WIDTH_GROUP_MIN and line_width > line_side2_post['width']:
                    fine_list.append(line_idx)
                    if index_side2_post in fine_list and line_side2_post['width'] < line_width:
                        todo_list.append(index_side2_post)
                else:
                    todo_list.append(line_idx)
            else:
                fine_list.append(line_idx)
            continue
        elif line_score <= 6:
            # 优先
            if score_pre == 4 and score_side1 <= 2:
                if type_side1 == UNIT_TYPE_SIDE and width_side1 <= UNIT_DEPTH_CURTAIN + 0.01:
                    if line_width >= UNIT_WIDTH_GROUP_MIN and line_width > line_side1_pre['width']:
                        fine_list.append(line_idx)
                    else:
                        todo_list.append(line_idx)
                else:
                    fine_list.append(line_idx)
                continue
            elif score_pre <= 2 and score_side2 <= 2:
                fine_list.append(line_idx)
                continue
            # 相等
            if score_pre == 4 and 2 < score_side1 <= 6:
                # 尺寸
                if line_width >= width_side1 * 1.5:
                    fine_list.append(line_idx)
                    continue
                elif line_width * 1.5 <= width_side1:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                # 分数
                elif line_score < score_side1 and line_width > 1:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                elif line_score > score_side1 and line_width > 1:
                    fine_list.append(line_idx)
                    continue
                # 分数
                elif line_score == score_side1 and line_width > 1 and type_side2 == UNIT_TYPE_GROUP:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                elif line_score == score_side1 and line_width > 1 and not type_side2 == UNIT_TYPE_GROUP:
                    if index_side1 in fine_list:
                        if index_side1 in todo_list:
                            fine_list.append(line_idx)
                        else:
                            todo_list.append(line_idx)
                    else:
                        fine_list.append(line_idx)
                    continue
                # 尺寸
                elif line_width >= width_side1:
                    fine_list.append(line_idx)
                    continue
            elif score_pre <= 2 and 2 < score_side2 <= 6:
                # 尺寸
                if line_width > width_side2 * 1.5:
                    fine_list.append(line_idx)
                    continue
                elif line_width * 1.5 <= width_side2:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                # 分数
                elif line_score < score_side2 and line_width > 1:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                elif line_score > score_side2 and line_width > 1:
                    fine_list.append(line_idx)
                    continue
                # 分数
                elif line_score == score_side2 and line_width > 1 and type_side1 == UNIT_TYPE_GROUP:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                elif line_score == score_side2 and line_width > 1 and not type_side1 == UNIT_TYPE_GROUP:
                    fine_list.append(line_idx)
                    continue
                # 尺寸
                elif line_width >= width_side2:
                    fine_list.append(line_idx)
                    continue
            # 让位
            if score_pre == 4 and score_side1 > 6:
                if line_width - depth_side1 >= UNIT_WIDTH_GROUP_MIN:
                    if line_cur['depth'] > UNIT_WIDTH_GROUP:
                        line_cur['depth'] = UNIT_WIDTH_GROUP
                    fine_list.append(line_idx)
                    if width_side1 < UNIT_WIDTH_GROUP * 2:
                        todo_list.append(line_idx)
                    continue
            if score_pre <= 2 and score_side2 > 6:
                if line_width - depth_side2 >= UNIT_WIDTH_GROUP_MIN:
                    if line_cur['depth'] > UNIT_WIDTH_GROUP:
                        line_cur['depth'] = UNIT_WIDTH_GROUP
                    fine_list.append(line_idx)
                    if width_side2 < UNIT_WIDTH_GROUP * 2:
                        todo_list.append(line_idx)
                    continue
        elif line_score == 8:
            # 优先
            if 'back_ratio' in line_cur and line_cur['back_ratio'][1] - line_cur['back_ratio'][0] >= 0.9:
                fine_list.append(line_idx)
                todo_side = 0
                if line_type in [UNIT_TYPE_WINDOW]:
                    if score_pre == 4:
                        if type_side1 == UNIT_TYPE_SIDE and width_side1 <= UNIT_DEPTH_CURTAIN + 0.01:
                            if line_width > line_side1_pre['width']:
                                todo_side += 1
                        elif line_width > line_side1['width']:
                            todo_side += 1
                    if score_post == 4:
                        if type_side2 == UNIT_TYPE_SIDE and width_side2 <= UNIT_DEPTH_CURTAIN + 0.01:
                            if line_width > line_side2_post['width']:
                                todo_side += 1
                        elif line_width > line_side2['width']:
                            todo_side += 1
                if line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and todo_side < 2:
                    todo_list.append(line_idx)
                continue
            elif score_side1 < 8 and score_side2 < 8:
                fine_list.append(line_idx)
                line_width_max = UNIT_WIDTH_GROUP_MAX * 0.8
                if room_area <= 10:
                    line_width_max = UNIT_WIDTH_GROUP_MAX * 0.6
                if line_width > line_width_max:
                    if score_side1 >= 5 and line_width - depth_side1 > UNIT_WIDTH_GROUP and line_width > width_side1 > UNIT_WIDTH_GROUP:
                        todo_list.append(line_idx)
                    elif score_side1 >= 5 and type_side1 in [UNIT_TYPE_AISLE] and line_type not in [UNIT_TYPE_AISLE]:
                        todo_list.append(line_idx)
                    elif score_side2 >= 5 and line_width - depth_side2 > UNIT_WIDTH_GROUP and line_width > width_side2 > UNIT_WIDTH_GROUP:
                        todo_list.append(line_idx)
                    elif score_side2 >= 5 and type_side2 in [UNIT_TYPE_AISLE] and line_type not in [UNIT_TYPE_AISLE]:
                        todo_list.append(line_idx)
                continue
            # 一侧
            elif score_side2 == 8 and score_side1 < 8:
                side_rest = width_side2 - line_cur['depth']
                this_rest = line_width - depth_side2
                if type_side1 in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
                    this_rest -= UNIT_WIDTH_DODGE
                if line_side2_post['type'] in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
                    side_rest -= UNIT_WIDTH_DODGE
                if line_depth <= UNIT_WIDTH_GROUP_MIN:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                elif depth_side2 <= UNIT_WIDTH_GROUP_MIN:
                    fine_list.append(line_idx)
                    continue
                elif side_rest >= this_rest and side_rest >= UNIT_WIDTH_GROUP / 2:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                elif this_rest >= side_rest and this_rest >= UNIT_WIDTH_GROUP / 2:
                    if index_side2 in todo_list:
                        fine_list.append(line_idx)
                    else:
                        fine_list.append(line_idx)
                    continue
                else:
                    if line_cur['width'] > width_side2:
                        fine_list.append(line_idx)
                        continue
                    else:
                        fine_list.append(line_idx)
                        todo_list.append(line_idx)
            elif score_side1 == 8 and score_side2 < 8:
                side_rest = width_side1 - line_depth
                this_rest = line_width - depth_side1
                if type_side2 in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
                    this_rest -= UNIT_WIDTH_DODGE
                if line_side1_pre['type'] in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
                    side_rest -= UNIT_WIDTH_DODGE
                if depth_side1 <= UNIT_WIDTH_GROUP_MIN:
                    fine_list.append(line_idx)
                    continue
                elif line_depth <= UNIT_WIDTH_GROUP_MIN:
                    fine_list.append(line_idx)
                    if index_side1 in fine_list and index_side1 in todo_list:
                        fine_list.remove(index_side1)
                    else:
                        todo_list.append(line_idx)
                    continue
                elif side_rest >= this_rest and side_rest >= UNIT_WIDTH_GROUP / 2:
                    if index_side1 not in todo_list:
                        fine_list.append(line_idx)
                        todo_list.append(line_idx)
                    else:
                        fine_list.append(line_idx)
                    continue
                elif this_rest >= side_rest and this_rest >= UNIT_WIDTH_GROUP / 2:
                    fine_list.append(line_idx)
                    continue
                else:
                    if line_width > width_side1:
                        fine_list.append(line_idx)
                        continue
                    else:
                        fine_list.append(line_idx)
                        todo_list.append(line_idx)
            # 两侧
            elif score_side1 == score_side2 == 8:
                if index_side1 in fine_list:
                    side_rest = width_side2 - line_cur['depth']
                    this_rest = line_cur['width'] - depth_side1 - depth_side2
                    if index_side1 not in todo_list:
                        fine_list.append(line_idx)
                        todo_list.append(line_idx)
                        continue
                else:
                    side_rest = width_side2 - line_cur['depth']
                    this_rest = line_cur['width'] - depth_side2
                if side_rest >= this_rest and side_rest >= UNIT_WIDTH_GROUP:
                    fine_list.append(line_idx)
                    continue
                elif this_rest >= side_rest and this_rest > UNIT_WIDTH_GROUP:
                    fine_list.append(line_idx)
                    todo_list.append(line_idx)
                    continue
                else:
                    if line_cur['width'] > width_side2:
                        fine_list.append(line_idx)
                        continue
                    else:
                        fine_list.append(line_idx)
                        todo_list.append(line_idx)

    # 矩形划分
    rect_list = []
    for line_idx in fine_list:
        line_cur = line_list[line_idx]
        line_type, line_score = line_cur['type'], line_cur['score']
        line_width, line_depth = line_cur['width'], line_cur['depth']
        score_pre, score_post = line_cur['score_pre'], line_cur['score_post']
        depth_pre, depth_post = line_cur['depth_pre'], line_cur['depth_post']
        # 排除
        if line_type in [UNIT_TYPE_GROUP, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
            pass
        elif line_type in [UNIT_TYPE_SIDE] and line_width > 1 and 0.1 < line_depth:
            pass
        else:
            continue
        # 扩展
        x1_temp, y1_temp, x2_temp, y2_temp = line_cur['p1'][0], line_cur['p1'][1], line_cur['p2'][0], line_cur['p2'][1]

        # 前段
        index_side1 = (line_idx - 1 + len(line_list)) % len(line_list)
        line_side1 = line_list[index_side1]
        type_side1, width_side1 = line_side1['type'], line_side1['width']
        if score_pre == 4 and type_side1 == UNIT_TYPE_SIDE and width_side1 <= UNIT_DEPTH_CURTAIN + 0.01:
            index_side1 = (line_idx - 2 + len(line_list)) % len(line_list)
            line_side1 = line_list[index_side1]
            type_side1, width_side1 = line_side1['type'], line_side1['width']
        # 阳角
        if line_cur['score_pre'] == 2:
            type_side1 = UNIT_TYPE_NONE
        # 平行
        elif line_cur['score_pre'] == 1 and type_side1 in [UNIT_TYPE_WALL]:
            if len(line_side1['depth_all']) > 0:
                ratio_find = line_side1['depth_all'][-1][1]
                for depth_idx in range(len(line_side1['depth_all']) - 1, -1, -1):
                    depth_one = line_side1['depth_all'][depth_idx]
                    if depth_one[2] >= line_depth - 0.1:
                        ratio_find = depth_one[0]
                    else:
                        break
                x1_temp = line_side1['p1'][0] + ratio_find * (line_side1['p2'][0] - line_side1['p1'][0])
                y1_temp = line_side1['p1'][1] + ratio_find * (line_side1['p2'][1] - line_side1['p1'][1])
            else:
                x1_temp = line_side1['p1'][0]
                y1_temp = line_side1['p1'][1]

        # 后段
        index_side2 = (line_idx + 1 + len(line_list)) % len(line_list)
        line_side2 = line_list[index_side2]
        type_side2, width_side2 = line_side2['type'], line_side2['width']
        if score_post == 4 and type_side2 == UNIT_TYPE_SIDE and width_side2 <= UNIT_DEPTH_CURTAIN + 0.01:
            index_side2 = (line_idx + 2 + len(line_list)) % len(line_list)
            line_side2 = line_list[index_side2]
            type_side2, width_side2 = line_side2['type'], line_side2['width']
        # 阳角
        if line_cur['score_post'] == 2:
            type_side2 = UNIT_TYPE_NONE
        # 平行
        elif line_cur['score_post'] == 1 and type_side2 in [UNIT_TYPE_WALL]:
            if len(line_side2['depth_all']) > 0:
                ratio_find = line_side2['depth_all'][0][0]
                for depth_idx in range(len(line_side2['depth_all'])):
                    depth_one = line_side2['depth_all'][depth_idx]
                    if depth_one[2] >= line_cur['depth'] - 0.1:
                        ratio_find = depth_one[1]
                    else:
                        break
                x2_temp = line_side2['p1'][0] + ratio_find * (line_side2['p2'][0] - line_side2['p1'][0])
                y2_temp = line_side2['p1'][1] + ratio_find * (line_side2['p2'][1] - line_side2['p1'][1])
            else:
                x2_temp = line_side2['p2'][0]
                y2_temp = line_side2['p2'][1]

        # 修正
        score_side1, score_side2 = line_cur['score_pre'], line_cur['score_post']
        ratio_1, ratio_2 = 0, 1
        if line_idx in todo_list:
            width = line_cur['width']
            # 前段
            if line_cur['score_pre'] == 4 and index_side1 in fine_list and index_side1 not in todo_list:
                width -= line_side1['depth']
                ratio_1 = line_side1['depth'] / line_cur['width']
                x1 = line_cur['p1'][0] + (line_cur['p2'][0] - line_cur['p1'][0]) * ratio_1
                y1 = line_cur['p1'][1] + (line_cur['p2'][1] - line_cur['p1'][1]) * ratio_1
                score_side1 = 1
                type_side1 = UNIT_TYPE_SIDE
            else:
                x1 = line_cur['p1'][0]
                y1 = line_cur['p1'][1]
            # 后段
            if line_cur['score_post'] == 4 and index_side2 in fine_list and index_side2 not in todo_list:
                width -= line_side2['depth']
                ratio_2 = 1 - line_side2['depth'] / line_cur['width']
                x2 = line_cur['p1'][0] + (line_cur['p2'][0] - line_cur['p1'][0]) * ratio_2
                y2 = line_cur['p1'][1] + (line_cur['p2'][1] - line_cur['p1'][1]) * ratio_2
                score_side2 = 1
                type_side2 = UNIT_TYPE_SIDE
            else:
                x2 = line_cur['p2'][0]
                y2 = line_cur['p2'][1]
            todo_list.pop(todo_list.index(line_idx))
        elif line_type in [UNIT_TYPE_GROUP] and line_cur['height'] > UNIT_HEIGHT_GROUP - 0.1:
            width = line_cur['width']
            x1, y1 = line_cur['p1'][0], line_cur['p1'][1]
            x2, y2 = line_cur['p2'][0], line_cur['p2'][1]
            x1_old, y1_old, x2_old, y2_old, width_old = x1, y1, x2, y2, width
            if type_side1 in [UNIT_TYPE_SIDE] and line_cur['score_pre'] == 4 and width > UNIT_WIDTH_HOLE:
                ratio = UNIT_DEPTH_CURTAIN / width_old
                x1 = x1_old * (1 - ratio) + x2_old * ratio
                y1 = y1_old * (1 - ratio) + y2_old * ratio
                width -= UNIT_DEPTH_CURTAIN
            if type_side2 in [UNIT_TYPE_SIDE] and line_cur['score_post'] == 4 and width > UNIT_WIDTH_HOLE:
                ratio = 1 - UNIT_DEPTH_CURTAIN / width_old
                x2 = x1_old * (1 - ratio) + x2_old * ratio
                y2 = y1_old * (1 - ratio) + y2_old * ratio
                width -= UNIT_DEPTH_CURTAIN
        elif line_type in [UNIT_TYPE_WINDOW]:
            x1, y1 = line_cur['p1'][0], line_cur['p1'][1]
            x2, y2 = line_cur['p2'][0], line_cur['p2'][1]
            # x1_new, y1_new, x2_new, y2_new = x1, y1, x2, y2
            # x1, y1, x2, y2 = x1_new, y1_new, x2_new, y2_new
            width, angle = calculate_line_angle(x1, y1, x2, y2)
        else:
            width = line_cur['width']
            x1, y1 = line_cur['p1'][0], line_cur['p1'][1]
            x2, y2 = line_cur['p2'][0], line_cur['p2'][1]

        if width < UNIT_WIDTH_GROUP_MIN * 0.25:
            continue
        if width < UNIT_WIDTH_GROUP_MIN * 0.50 and line_score <= 5:
            continue
        if width < UNIT_WIDTH_GROUP_MIN * 1.00 and line_type in [UNIT_TYPE_WINDOW]:
            continue

        # 矩形
        angle = normalize_line_angle(line_cur['angle'] + math.pi / 2)
        depth = line_depth
        if 'back_depth' in line_cur and depth < line_cur['back_depth'] * 2:
            depth += line_cur['back_depth']
        if line_type in [UNIT_TYPE_AISLE] and depth > 3:
            depth = min(depth_pre, depth_post, 1)
        x_delta = depth * math.sin(angle)
        y_delta = depth * math.cos(angle)
        x3, y3, x4, y4 = x2 + x_delta, y2 + y_delta, x1 + x_delta, y1 + y_delta
        x_center = x1 * 0.5 + x2 * 0.5 + x_delta * 0.5
        y_center = y1 * 0.5 + y2 * 0.5 + y_delta * 0.5

        # 扩展
        x_min = min(x1_temp, x2_temp, x3, x4)
        x_max = max(x1_temp, x2_temp, x3, x4)
        y_min = min(y1_temp, y2_temp, y3, y4)
        y_max = max(y1_temp, y2_temp, y3, y4)
        # 矩形
        rect_one = {
            'type': line_type,
            'score': score_side1 + score_side2,
            'width': width,
            'depth': depth,
            'height': line_cur['height'],
            'angle': angle,
            'index': line_idx,
            'ratio': [ratio_1, ratio_2],
            'p1': [round(x1, 3), round(y1, 3)],
            'p2': [round(x2, 3), round(y2, 3)],
            'p3': [round(x3, 3), round(y3, 3)],
            'p4': [round(x4, 3), round(y4, 3)],
            'center': [round(x_center, 3), round(y_center, 3)],
            'expand': [x_min, y_min, x_max, y_max],
            'type_pre': type_side1,
            'type_post': type_side2,
            'score_pre': score_side1,
            'score_post': score_side2,
            'depth_pre': line_cur['depth_pre'],
            'depth_post': line_cur['depth_post'],
            'depth_all': line_cur['depth_all'],
            'unit_margin': line_cur['unit_margin'],
            'unit_edge': line_cur['unit_edge'],
            'unit_group': line_cur['unit_group']
        }
        if 'back_depth' in line_cur:
            rect_one['back_depth'] = line_cur['back_depth']
        rect_list.append(rect_one)

    # 返回信息
    rect_info_one['line'] = line_list
    rect_info_one['rect'] = rect_list
    rect_info_all.append(rect_info_one)
    return rect_info_all


# 轮廓分析 要求：房间轮廓和部件轮廓都使用逆时针点列描述 水平正方向向右 竖直正方向向下
def room_line(room_info, type_list=[], unit_list=[], height_list=[], back_list=[],
              room_type='', room_area=10, main_door=[], open_unit=[UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]):
    # 线段列表
    room_type, room_area, line_list, line_ori = '', 0, [], []
    if 'floor' not in room_info:
        return line_list, line_ori
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    # 部件列表
    type_list_3 = []
    unit_list_1, unit_list_2, unit_list_3, unit_list_4 = [], [], [], []
    height_list_1, height_list_2, height_list_3, height_list_4 = [], [], [], []
    to_room_list_1, to_room_list_2, to_room_list_3, to_room_list_4 = [], [], [], []
    to_room_link = {}
    # 通行区域
    for unit_one in room_info['door_info']:
        normalize_unit_clock(unit_one)
        unit_list_1.append(unit_one['pts'])
        to_room_list_1.append(unit_one['to'])
        if 'link' not in unit_one:
            continue
        to_room, to_type = unit_one['to'], unit_one['link']
        if len(to_type) > 0:
            to_room_link[to_room] = to_type
    # 通行区域
    for unit_one in room_info['hole_info']:
        normalize_unit_clock(unit_one)
        unit_list_1.append(unit_one['pts'])
        to_room_list_1.append(unit_one['to'])
        to_room, to_type = unit_one['to'], unit_one['link']
        if 'link' not in unit_one:
            continue
        if len(to_type) > 0:
            to_room_link[to_room] = to_type
    # 照明区域
    for unit_one in room_info['window_info']:
        normalize_unit_clock(unit_one)
        unit_list_2.append(unit_one['pts'])
        to_room_list_2.append(unit_one['to'])
        height_list_2.append(unit_one['height'])
        if 'link' not in unit_one:
            continue
        to_room, to_type = unit_one['to'], unit_one['link']
        if len(to_type) > 0:
            to_room_link[to_room] = to_type
    # 照明区域
    for unit_one in room_info['baywindow_info']:
        normalize_unit_clock(unit_one)
        unit_list_2.append(unit_one['pts'])
        to_room_list_2.append(unit_one['to'])
        height_list_2.append(unit_one['height'])
        if 'link' not in unit_one:
            continue
        to_room, to_type = unit_one['to'], unit_one['link']
        if len(to_type) > 0:
            to_room_link[to_room] = to_type
    # 家具区域
    for type_one in type_list:
        type_list_3.append(type_one)
    for unit_one in unit_list:
        unit_list_3.append(unit_one)
    for height_one in height_list:
        height_list_3.append(height_one)
    # 背景区域
    for unit_one in back_list:
        unit_list_4.append(unit_one)
        height_list_4.append(UNIT_HEIGHT_WALL)

    # 原始轮廓 顶点
    floor_pts = room_info['floor']
    if len(floor_pts) >= 2:
        begin_x, begin_z = floor_pts[0], floor_pts[1]
        end_x, end_z = floor_pts[-2], floor_pts[-1]
        if abs(begin_x - end_x) + abs(begin_z - end_z) >= 0.01:
            room_info['floor'].append(begin_x)
            room_info['floor'].append(begin_z)
    floor_len = int(len(floor_pts) / 2)
    # 原始轮廓 线段
    line_ori, line_hor, line_ver, line_tlt = [], [], [], []
    width_min = UNIT_WIDTH_WALL_MIN
    for i in range(floor_len - 1):
        # 起点终点
        x1, y1, x2, y2 = floor_pts[2 * i + 0], floor_pts[2 * i + 1], floor_pts[2 * i + 2], floor_pts[2 * i + 3]
        length, angle = calculate_line_angle(x1, y1, x2, y2)
        # 跳过
        x0 = floor_pts[(2 * i - 2 + len(floor_pts)) % len(floor_pts)]
        y0 = floor_pts[(2 * i - 1 + len(floor_pts)) % len(floor_pts)]
        x3 = floor_pts[(2 * i + 4 + len(floor_pts)) % len(floor_pts)]
        y3 = floor_pts[(2 * i + 5 + len(floor_pts)) % len(floor_pts)]
        length_side_1, angle_side_1 = calculate_line_angle(x0, y0, x1, y1)
        length_side_2, angle_side_2 = calculate_line_angle(x2, y2, x3, y3)
        if length_side_1 <= 0.001:
            x0 = floor_pts[(2 * i - 4 + len(floor_pts)) % len(floor_pts)]
            y0 = floor_pts[(2 * i - 3 + len(floor_pts)) % len(floor_pts)]
            length_side_1, angle_side_1 = calculate_line_angle(x0, y0, x1, y1)
        if length_side_2 <= 0.001:
            x3 = floor_pts[(2 * i + 6 + len(floor_pts)) % len(floor_pts)]
            y3 = floor_pts[(2 * i + 7 + len(floor_pts)) % len(floor_pts)]
            length_side_2, angle_side_2 = calculate_line_angle(x2, y2, x3, y3)
        if length <= width_min * 0.5:
            continue
        elif length <= width_min * 1:
            if min(length_side_1, length_side_2) > 0.4 and max(length_side_1, length_side_2) > 3.0 \
                    and abs(normalize_line_angle(angle_side_1 - angle_side_2)) < 0.1:
                continue
            else:
                continue
        elif length <= width_min * 2 and length < width_min + 0.01 * room_area / 10:
            if min(length_side_1, length_side_2) > 0.4 and max(length_side_1, length_side_2) > 3.0 \
                    and abs(normalize_line_angle(angle_side_1 - angle_side_2)) < 0.1:
                continue
            elif length < length_side_1 and length < length_side_2:
                angle_inner = normalize_line_angle(angle_side_1 + math.pi * 0.5 * 1)
                if abs(normalize_line_angle(angle - angle_inner)) <= 0.01 and len(line_ori) >= 1:
                    last_one = line_ori[-1]
                    last_p1, last_p2 = last_one['p1'], last_one['p2']
                    if abs(last_p1[0] - x2) <= width_min * 2 and abs(last_p2[0] - x2) <= width_min * 2:
                        last_p1[0], last_p2[0] = x2, x2
                continue
        # 拼接
        if len(line_ori) > 0:
            line_old = line_ori[-1]
            x1_old, y1_old = line_old['p1'][0], line_old['p1'][1]
            x2_old, y2_old = line_old['p2'][0], line_old['p2'][1]
            angle_old = line_old['angle']
            if abs(normalize_line_angle(angle - angle_old)) < 0.1:
                length = abs(x2_old - x1) + abs(y2_old - y1)
                if length < width_min:
                    line_ori.pop(-1)
                    x1, y1 = x1_old, y1_old
                elif length < width_min * 2 and length < width_min + 0.01 * room_area / 10:
                    line_ori.pop(-1)
                    x1, y1 = x1_old, y1_old
        # 垂直
        if abs(x2 - x1) <= width_min * 2 and abs(y2 - y1) >= 5 * abs(x2 - x1):
            skip_dis, skip_ang = calculate_line_angle(x0, y0, x2, y2)
            angle_dlt = normalize_line_angle(skip_ang - angle)
            if angle_dlt > 0:
                x1 = x2
            else:
                x2 = x1
        if abs(y2 - y1) <= width_min * 2 and abs(x2 - x1) >= 5 * abs(y2 - y1):
            skip_dis, skip_ang = calculate_line_angle(x0, y0, x2, y2)
            angle_dlt = normalize_line_angle(skip_ang - angle)
            if angle_dlt > 0:
                y1 = y2
            else:
                y2 = y1
        # 线段角度
        length, angle = calculate_line_angle(x1, y1, x2, y2)
        line_width = length
        line_one = {
            'p1': [x1, y1],
            'p2': [x2, y2],
            'width': line_width,
            'angle': angle
        }
        line_ori.append(line_one)
    # 原始轮廓 去重
    width_min = UNIT_WIDTH_WALL_MIN
    for line_idx in range(len(line_ori) - 1, -1, -1):
        line_0 = line_ori[(line_idx - 1 + len(line_ori)) % len(line_ori)]
        line_1 = line_ori[(line_idx + 0 + len(line_ori)) % len(line_ori)]
        line_2 = line_ori[(line_idx + 1 + len(line_ori)) % len(line_ori)]
        angle0, angle1, angle2 = line_0['angle'], line_1['angle'], line_2['angle']
        width0, width1, width2 = line_0['width'], line_1['width'], line_2['width']
        x1, y1, x2, y2 = line_1['p2'][0], line_1['p2'][1], line_2['p1'][0], line_2['p1'][1]
        if abs(angle1 - angle2) < 0.1 and abs(x2 - x1) + abs(y2 - y1) < width_min * 2:
            line_2['p1'] = line_1['p1'][:]
            line_2['width'] += width1
            x1, y1, x2, y2 = line_2['p1'][0], line_2['p1'][1], line_2['p2'][0], line_2['p2'][1]
            length, angle = calculate_line_angle(x1, y1, x2, y2)
            if normalize_line_angle(angle - angle1) < 0:
                if abs(x2 - x1) <= width_min * 2 and abs(y2 - y1) >= 5 * abs(x2 - x1):
                    line_2['p2'][0] = x1
                if abs(y2 - y1) <= width_min * 2 and abs(x2 - x1) >= 5 * abs(y2 - y1):
                    line_2['p2'][1] = y1
            elif normalize_line_angle(angle - angle1) > 0:
                if abs(x2 - x1) <= width_min * 2 and abs(y2 - y1) >= 5 * abs(x2 - x1):
                    line_2['p1'][0] = x2
                if abs(y2 - y1) <= width_min * 2 and abs(x2 - x1) >= 5 * abs(y2 - y1):
                    line_2['p1'][1] = y2
            line_ori.pop(line_idx)
    # 原始轮廓 分类
    for line_one in line_ori:
        angle = line_one['angle']
        # 横墙
        if determine_line_angle(angle) == 0:
            line_hor.append(line_one)
        # 竖墙
        elif determine_line_angle(angle) == 1:
            line_ver.append(line_one)
        # 斜墙
        else:
            line_tlt.append(line_one)

    # 原始轮廓 门洞
    door_hor, door_ver, door_tlt = [], [], []
    link_hor, link_ver, link_tlt = [], [], []
    for unit_idx, unit_one in enumerate(unit_list_1):
        edge_len = int(len(unit_one) / 2)
        for j in range(edge_len):
            x1 = unit_one[(2 * j + 0) % len(unit_one)]
            y1 = unit_one[(2 * j + 1) % len(unit_one)]
            x2 = unit_one[(2 * j + 2) % len(unit_one)]
            y2 = unit_one[(2 * j + 3) % len(unit_one)]
            if abs(x2 - x1) + abs(y2 - y1) <= 0.5:
                continue
            # 线段角度
            length, angle = calculate_line_angle(x1, y1, x2, y2)
            line_width = length
            line_one = {
                'p1': [x1, y1],
                'p2': [x2, y2],
                'width': line_width,
                'angle': angle
            }
            link_key = to_room_list_1[(unit_idx + len(to_room_list_1)) % len(to_room_list_1)]
            link_type = link_key.split('-')[0]
            if link_key in to_room_link:
                link_type = to_room_link[link_key]
            # 横墙
            if determine_line_angle(angle) == 0:
                door_hor.append(line_one)
                link_hor.append(link_type)
            # 竖墙
            elif determine_line_angle(angle) == 1:
                door_ver.append(line_one)
                link_ver.append(link_type)
            # 斜墙
            else:
                door_tlt.append(line_one)
                link_ver.append(link_type)

    # 原始轮廓 硬装
    group_hor, group_ver, group_tlt = [], [], []
    for unit_idx, unit_one in enumerate(unit_list_4):
        edge_len = int(len(unit_one) / 2)
        j = 0
        x1 = unit_one[(2 * j + 0) % len(unit_one)]
        y1 = unit_one[(2 * j + 1) % len(unit_one)]
        x2 = unit_one[(2 * j + 2) % len(unit_one)]
        y2 = unit_one[(2 * j + 3) % len(unit_one)]
        x3 = unit_one[(2 * j + 4) % len(unit_one)]
        y3 = unit_one[(2 * j + 5) % len(unit_one)]
        if abs(x2 - x1) + abs(y2 - y1) <= 0.5:
            continue
        # 线段角度
        depth, angle = calculate_line_angle(x2, y2, x3, y3)
        width, angle = calculate_line_angle(x1, y1, x2, y2)
        line_one = {
            'p1': [x1, y1],
            'p2': [x2, y2],
            'width': width,
            'depth': depth,
            'angle': angle
        }
        # 横墙
        if determine_line_angle(angle) == 0:
            group_hor.append(line_one)
        # 竖墙
        elif determine_line_angle(angle) == 1:
            group_ver.append(line_one)
        # 斜墙
        else:
            group_tlt.append(line_one)

    # 处理轮廓 分裂线段
    for line_idx, line_cur in enumerate(line_ori):
        # 当前
        x1, y1, x2, y2 = line_cur['p1'][0], line_cur['p1'][1], line_cur['p2'][0], line_cur['p2'][1]
        width, angle = line_cur['width'], line_cur['angle']
        # 对面
        face_wall, side_wall, tilt_wall, face_door, side_door, face_room, side_room = [], [], [], [], [], [], []
        face_group, side_group = [], []
        # 横墙
        if determine_line_angle(angle) == 0:
            face_wall, tilt_wall, face_door, side_door = line_hor, line_tlt, door_hor, door_ver
            face_room, side_room = link_hor, link_ver
            face_group, side_group = group_hor, group_ver
        # 竖墙
        elif determine_line_angle(angle) == 1:
            face_wall, tilt_wall, face_door, side_door = line_ver, line_tlt, door_ver, door_hor
            face_room, side_room = link_ver, link_hor
            face_group, side_group = group_ver, group_hor
        # 斜墙
        elif width > UNIT_WIDTH_GROUP:
            face_wall, face_door, side_door = class_line_tilt(line_cur, line_tlt, door_tlt)
            index_side1 = (line_idx - 1 + len(line_ori)) % len(line_ori)
            index_side2 = (line_idx + 1 + len(line_ori)) % len(line_ori)
            side_wall = [line_ori[index_side1], line_ori[index_side2]]

        # 部件检测
        width_aisle = UNIT_WIDTH_AISLE
        if room_type in ROOM_TYPE_LEVEL_1:
            if room_area <= 20:
                width_aisle = UNIT_WIDTH_AISLE * 0.80
            elif room_area <= 40:
                width_aisle = UNIT_WIDTH_AISLE * 1.00
            else:
                width_aisle = UNIT_WIDTH_AISLE * 1.20
        elif room_type in ROOM_TYPE_LEVEL_2:
            if room_area <= 10:
                width_aisle = UNIT_WIDTH_AISLE * 0.80
            elif room_area <= 20:
                width_aisle = UNIT_WIDTH_AISLE * 1.00
            else:
                width_aisle = UNIT_WIDTH_AISLE * 1.20
        elif room_type in ROOM_TYPE_LEVEL_3:
            width_aisle = UNIT_DEPTH_CURTAIN
        ratio_list_group = split_line_unit(x1, y1, x2, y2, unit_list_3, UNIT_TYPE_GROUP, False,
                                           type_list_3, height_list_3, to_room_list_3)
        ratio_list_door = split_line_unit(x1, y1, x2, y2, unit_list_1, UNIT_TYPE_DOOR, False,
                                          [], height_list_1, to_room_list_1)
        ratio_list_window = split_line_unit(x1, y1, x2, y2, unit_list_2, UNIT_TYPE_WINDOW, False,
                                            [], height_list_2, to_room_list_2)
        ratio_list_depth, ratio_list_floor, ratio_list_aisle = \
            split_line_face(line_cur, face_wall, side_wall, tilt_wall, face_door, side_door,
                            face_room, side_room, face_group, side_group, width_aisle, room_type, room_area, main_door)
        # 部件比例
        ratio_list_all = [ratio_list_group, ratio_list_door, ratio_list_window, ratio_list_aisle]
        ratio_list_norm, ratio_dump_norm = [], []
        for ratio_list_one in ratio_list_all:
            for ratio_new in ratio_list_one:
                ratio_find = False
                ratio_move, ratio_depth = min(0.1, ratio_new[1] - ratio_new[0]), ratio_new[:]
                ratio_type, ratio_width = ratio_new[UNIT_RATIO_TYPE], width * (ratio_new[1] - ratio_new[0])
                if ratio_new[UNIT_RATIO_TYPE] == UNIT_TYPE_AISLE and ratio_new[2] >= 3 and ratio_move > 0.1:
                    find_pre, find_post = False, False
                    for ratio_idx, ratio_one in enumerate(ratio_list_norm):
                        if ratio_new[0] - ratio_move < ratio_one[1] < ratio_new[0] + ratio_move:
                            find_pre = True
                        if ratio_new[1] - ratio_move < ratio_one[0] < ratio_new[1] + ratio_move:
                            find_post = True
                        if ratio_one[1] >= ratio_new[1]:
                            break
                    if find_pre and find_post:
                        continue
                for ratio_idx, ratio_one in enumerate(ratio_list_norm):
                    if ratio_new[1] <= ratio_one[0] + 0.01:
                        if abs(ratio_new[1] - ratio_one[0]) <= 0.05:
                            ratio_one[0] = ratio_new[1]
                        ratio_find = True
                        ratio_list_norm.insert(ratio_idx, ratio_new[:])
                        break
                    elif ratio_new[0] < ratio_one[0] < ratio_new[1]:
                        if ratio_new[UNIT_RATIO_TYPE] in [UNIT_TYPE_DOOR] and ratio_width <= UNIT_WIDTH_HOLE:
                            if ratio_one[1] - ratio_one[0] > ratio_new[1] - ratio_new[0]:
                                ratio_one[0] = ratio_new[1]
                                ratio_list_norm.insert(ratio_idx, ratio_new[:])
                                break
                            else:
                                ratio_one[0] = ratio_new[0]
                                ratio_one[UNIT_RATIO_TYPE] = ratio_new[UNIT_RATIO_TYPE]
                                ratio_find = True
                                break
                        # 前端
                        ratio_add = ratio_new[:]
                        ratio_add[1] = ratio_one[0]
                        ratio_list_norm.insert(ratio_idx, ratio_add)
                        # 中段
                        if ratio_one[UNIT_RATIO_TYPE] in [UNIT_TYPE_WINDOW]:
                            height_1, height_2 = ratio_one[UNIT_RATIO_HEIGHT], ratio_new[UNIT_RATIO_HEIGHT]
                            ratio_one[UNIT_RATIO_HEIGHT] = min(height_1, height_2)
                        else:
                            ratio_one[UNIT_RATIO_HEIGHT] = UNIT_HEIGHT_WALL
                        # 后段
                        if ratio_new[1] <= ratio_one[1]:
                            ratio_find = True
                            break
                        else:
                            ratio_new[0] = ratio_one[1]
                            continue
                    elif ratio_new[0] >= ratio_one[0] and ratio_new[1] <= ratio_one[1]:
                        if ratio_new[UNIT_RATIO_TYPE] in [UNIT_TYPE_DOOR]:
                            ratio_one[UNIT_RATIO_TYPE] = ratio_new[UNIT_RATIO_TYPE]
                            ratio_find = True
                            break
                        if ratio_new[UNIT_RATIO_TYPE] in [UNIT_TYPE_WINDOW]:
                            if ratio_one[UNIT_RATIO_TYPE] in [UNIT_TYPE_WINDOW]:
                                height_1, height_2 = ratio_one[UNIT_RATIO_HEIGHT], ratio_new[UNIT_RATIO_HEIGHT]
                                ratio_one[UNIT_RATIO_HEIGHT] = min(height_1, height_2)
                            else:
                                ratio_one[UNIT_RATIO_HEIGHT] = UNIT_HEIGHT_WALL
                        ratio_find = True
                        break
                    elif ratio_new[0] >= ratio_one[1] - 0.01:
                        continue
                    else:
                        if ratio_new[UNIT_RATIO_TYPE] in [UNIT_TYPE_DOOR]:
                            if ratio_one[UNIT_RATIO_TYPE] in [UNIT_TYPE_GROUP]:
                                if ratio_one[1] - ratio_new[0] < (ratio_new[1] - ratio_new[0]) * 0.2:
                                    if ratio_one[1] - ratio_new[0] > (ratio_one[1] - ratio_one[0]) * 0.2:
                                        ratio_one[UNIT_RATIO_HEIGHT] = max(ratio_one[UNIT_RATIO_HEIGHT], ratio_new[UNIT_RATIO_HEIGHT])
                                    ratio_new[0] = ratio_one[1]
                                elif ratio_one[1] - ratio_new[0] > (ratio_new[1] - ratio_new[0]) * 0.9 or width * (ratio_new[1] - ratio_one[1]) < UNIT_WIDTH_MERGE_MIN:
                                    ratio_one[1] = max(ratio_new[1], ratio_one[1])
                                    ratio_one[UNIT_RATIO_HEIGHT] = max(ratio_one[UNIT_RATIO_HEIGHT], ratio_new[UNIT_RATIO_HEIGHT])
                                    ratio_find = True
                                    break
                                else:
                                    ratio_one[1] = ratio_new[0]
                            else:
                                ratio_one[1] = ratio_new[0]
                        elif ratio_new[UNIT_RATIO_TYPE] in [UNIT_TYPE_WINDOW]:
                            if ratio_one[UNIT_RATIO_TYPE] in [UNIT_TYPE_WINDOW]:
                                height_1, height_2 = ratio_one[UNIT_RATIO_HEIGHT], ratio_new[UNIT_RATIO_HEIGHT]
                                ratio_one[UNIT_RATIO_HEIGHT] = min(height_1, height_2)
                            else:
                                ratio_one[UNIT_RATIO_HEIGHT] = UNIT_HEIGHT_WALL
                        ratio_new[0] = ratio_one[1]
                        continue
                if not ratio_find and ratio_new[1] - ratio_new[0] >= 0.01:
                    ratio_list_norm.append(ratio_new[:])
                elif ratio_find and ratio_depth[UNIT_RATIO_TYPE] == UNIT_TYPE_AISLE:
                    ratio_list_depth.append(ratio_depth)
        # 深度比例
        for ratio_list_idx, ratio_list_old in enumerate([ratio_list_depth, ratio_list_floor]):
            ratio_list_new = []
            for ratio_new in ratio_list_old:
                ratio_find = False
                for ratio_idx, ratio_one in enumerate(ratio_list_new):
                    if ratio_new[1] <= ratio_one[0]:
                        ratio_find = True
                        ratio_list_new.insert(ratio_idx, ratio_new[:])
                        break
                    elif ratio_new[0] < ratio_one[0] < ratio_new[1]:
                        ratio_add = ratio_new[:]
                        ratio_add[1] = ratio_one[0]
                        ratio_list_new.insert(ratio_idx, ratio_add)
                        ratio_new[0] = ratio_one[0]
                        continue
                    elif ratio_new[0] >= ratio_one[0] and ratio_new[1] <= ratio_one[1]:
                        if ratio_new[2] < ratio_one[2]:
                            old_0, old_1, old_d = ratio_one[0], ratio_one[1], ratio_one[2]
                            new_0, new_1, new_d = ratio_new[0], ratio_new[1], ratio_new[2]
                            ratio_one[0] = old_0
                            ratio_one[1] = new_1
                            ratio_one[2] = new_d
                            ratio_new[0] = new_1
                            ratio_new[1] = old_1
                            ratio_new[2] = old_d
                            continue
                        else:
                            ratio_find = True
                            break
                    elif ratio_one[0] <= ratio_new[0] < ratio_new[0] + 0.001 < ratio_one[1] < ratio_new[1]:
                        if ratio_new[2] < ratio_one[2]:
                            ratio_one[1] = ratio_new[0]
                        else:
                            ratio_new[0] = ratio_one[1]
                        continue
                    elif ratio_new[0] >= ratio_one[1]:
                        continue
                    else:
                        ratio_new[0] = ratio_one[1]
                        continue
                if not ratio_find:
                    ratio_list_new.append(ratio_new[:])
            if ratio_list_idx == 0:
                ratio_list_depth = ratio_list_new
            elif ratio_list_idx == 1:
                ratio_list_floor = ratio_list_new

        # 调整终点
        if len(ratio_list_norm) > 0:
            ratio_begin = ratio_list_norm[-1][1]
            ratio_end = 1
            x_begin = x1 + (x2 - x1) * ratio_begin
            y_begin = y1 + (y2 - y1) * ratio_begin
            x_end = x1 + (x2 - x1) * ratio_end
            y_end = y1 + (y2 - y1) * ratio_end
            unit_width = math.sqrt((x_end - x_begin) * (x_end - x_begin) + (y_end - y_begin) * (y_end - y_begin))
            if unit_width < 0.01:
                ratio_list_norm[-1][1] = 1
        # 添加线段
        ratio_list_norm.append([1, 1, 0, 0, 0, 0, 0, UNIT_TYPE_WALL, '', ''])
        ratio_begin, ratio_end = 0, 0
        # 分裂线段
        for ratio_idx, ratio_one in enumerate(ratio_list_norm):
            # 墙壁
            if ratio_one[0] > ratio_begin:
                ratio_end = ratio_one[0]
                x_begin = x1 + (x2 - x1) * ratio_begin
                y_begin = y1 + (y2 - y1) * ratio_begin
                x_end = x1 + (x2 - x1) * ratio_end
                y_end = y1 + (y2 - y1) * ratio_end
                unit_type = UNIT_TYPE_WALL
                unit_width = math.sqrt((x_end - x_begin) * (x_end - x_begin) + (y_end - y_begin) * (y_end - y_begin))
                unit_depth, unit_height = 0, 0
                x_begin = round(x_begin, 3)
                y_begin = round(y_begin, 3)
                x_end = round(x_end, 3)
                y_end = round(y_end, 3)
                unit_width = round(unit_width, 3)
                if unit_width > 0.05:
                    line_one = {
                        'type': unit_type,
                        'score': 0,
                        'width': unit_width,
                        'depth': 0,
                        'depth_all': [],
                        'depth_ext': [],
                        'height': unit_height,
                        'angle': angle,
                        'p1': [x_begin, y_begin],
                        'p2': [x_end, y_end],
                        'score_pre': 0,
                        'score_post': 0,
                        'depth_pre': 0,
                        'depth_post': 0,
                        'depth_pre_more': 0,
                        'depth_post_more': 0,
                        'unit_index': 0,
                        'unit_depth': unit_depth,
                        'unit_margin': 0,
                        'unit_edge': 0,
                        'unit_flag': 0,
                        'unit_group': '',
                        'unit_to_room': '',
                        'unit_to_type': ''
                    }
                    # 进深
                    for ratio_list_idx, ratio_list_one in enumerate([ratio_list_depth, ratio_list_floor]):
                        depth_all = []
                        for depth_one in ratio_list_one:
                            if depth_one[0] > ratio_end:
                                break
                            if depth_one[1] < ratio_begin:
                                continue
                            r0 = (depth_one[0] - ratio_begin) / (ratio_end - ratio_begin)
                            r1 = (depth_one[1] - ratio_begin) / (ratio_end - ratio_begin)
                            r0 = round(r0, 3)
                            r1 = round(r1, 3)
                            if r0 < 0:
                                r0 = 0
                            if r1 > 1:
                                r1 = 1
                            if abs(r0 - r1) < 0.01:
                                continue
                            depth_all.append([r0, r1, depth_one[2]])
                        # depth_all
                        if ratio_list_idx == 0:
                            for depth_one in depth_all:
                                line_one['depth_all'].append(depth_one.copy())
                        # depth_ext
                        elif ratio_list_idx == 1:
                            for depth_one in depth_all:
                                line_one['depth_ext'].append(depth_one.copy())
                    line_list.append(line_one)
                else:
                    ratio_end = ratio_begin
            # 其他
            if ratio_one[1] > ratio_end:
                ratio_begin = ratio_end
                ratio_end = ratio_one[1]
                x_begin = x1 + (x2 - x1) * ratio_begin
                y_begin = y1 + (y2 - y1) * ratio_begin
                x_end = x1 + (x2 - x1) * ratio_end
                y_end = y1 + (y2 - y1) * ratio_end
                unit_type = ratio_one[UNIT_RATIO_TYPE]
                unit_width = math.sqrt((x_end - x_begin) * (x_end - x_begin) + (y_end - y_begin) * (y_end - y_begin))
                unit_depth, unit_height = ratio_one[UNIT_RATIO_DEPTH], ratio_one[UNIT_RATIO_HEIGHT]
                unit_index, unit_margin, unit_edge = ratio_one[UNIT_RATIO_INDEX], ratio_one[UNIT_RATIO_MARGIN], ratio_one[UNIT_RATIO_EDGE]
                unit_group = ratio_one[UNIT_RATIO_GROUP]
                line_depth = 0
                if unit_type == UNIT_TYPE_GROUP:
                    line_depth = unit_depth
                elif unit_type == UNIT_TYPE_DOOR:
                    line_depth = UNIT_DEPTH_ASIDE
                elif unit_type == UNIT_TYPE_SIDE:
                    line_depth = UNIT_DEPTH_ASIDE
                elif unit_type == UNIT_TYPE_WINDOW:
                    line_depth = UNIT_DEPTH_ASIDE
                elif unit_type == UNIT_TYPE_AISLE:
                    line_depth = max(ratio_one[2] - UNIT_DEPTH_DODGE, 0)
                unit_to_room = ratio_one[UNIT_RATIO_TO_ROOM]
                unit_to_type = ''
                if unit_to_room in to_room_link:
                    unit_to_type = to_room_link[unit_to_room]
                x_begin = round(x_begin, 3)
                y_begin = round(y_begin, 3)
                x_end = round(x_end, 3)
                y_end = round(y_end, 3)
                unit_width = round(unit_width, 3)
                unit_depth = round(unit_depth, 3)
                unit_height = round(unit_height, 3)
                line_one = {
                    'type': unit_type,
                    'score': 0,
                    'width': unit_width,
                    'depth': line_depth,
                    'depth_all': [],
                    'depth_ext': [],
                    'height': unit_height,
                    'angle': angle,
                    'p1': [x_begin, y_begin],
                    'p2': [x_end, y_end],
                    'score_pre': 0,
                    'score_post': 0,
                    'depth_pre': unit_depth,
                    'depth_post': unit_depth,
                    'depth_pre_more': unit_depth,
                    'depth_post_more': unit_depth,
                    'unit_index': unit_index,
                    'unit_depth': unit_depth,
                    'unit_margin': unit_margin,
                    'unit_edge': unit_edge,
                    'unit_flag': 0,
                    'unit_group': unit_group,
                    'unit_to_room': unit_to_room,
                    'unit_to_type': unit_to_type
                }
                if unit_type in [UNIT_TYPE_GROUP, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]:
                    # 进深
                    for ratio_list_idx, ratio_list_one in enumerate([ratio_list_depth, ratio_list_floor]):
                        depth_all = []
                        for depth_one in ratio_list_one:
                            if depth_one[0] > ratio_end:
                                break
                            if depth_one[1] < ratio_begin:
                                continue
                            r0 = (depth_one[0] - ratio_begin) / (ratio_end - ratio_begin)
                            r1 = (depth_one[1] - ratio_begin) / (ratio_end - ratio_begin)
                            r0 = round(r0, 3)
                            r1 = round(r1, 3)
                            if r0 < 0:
                                r0 = 0
                            if r1 > 1:
                                r1 = 1
                            if abs(r0 - r1) < 0.01:
                                continue
                            depth_all.append([r0, r1, depth_one[2]])
                        # depth_all
                        if ratio_list_idx == 0:
                            for depth_one in depth_all:
                                line_one['depth_all'].append(depth_one.copy())
                        # depth_ext
                        elif ratio_list_idx == 1:
                            for depth_one in depth_all:
                                line_one['depth_ext'].append(depth_one.copy())
                elif unit_type in [UNIT_TYPE_DOOR]:
                    # 进深
                    for ratio_list_idx, ratio_list_one in enumerate([ratio_list_depth, ratio_list_floor]):
                        depth_all = []
                        for depth_one in ratio_list_one:
                            if depth_one[0] > ratio_end:
                                break
                            if depth_one[1] < ratio_begin:
                                continue
                            r0 = (depth_one[0] - ratio_begin) / (ratio_end - ratio_begin)
                            r1 = (depth_one[1] - ratio_begin) / (ratio_end - ratio_begin)
                            r0 = round(r0, 3)
                            r1 = round(r1, 3)
                            if r0 < 0:
                                r0 = 0
                            if r1 > 1:
                                r1 = 1
                            depth_all.append([r0, r1, depth_one[2]])
                        # depth_all
                        if ratio_list_idx == 0:
                            for depth_one in depth_all:
                                line_one['depth_all'].append(depth_one.copy())
                        # depth_ext
                        elif ratio_list_idx == 1:
                            for depth_one in depth_all:
                                line_one['depth_ext'].append(depth_one.copy())
                elif unit_type in [UNIT_TYPE_SIDE]:
                    line_one['depth_all'] = [[0, 1, line_depth]]
                    line_one['depth_ext'] = [[0, 1, line_depth]]
                elif unit_type in [UNIT_TYPE_AISLE]:
                    if line_depth < 2:
                        line_one['depth_all'] = [[0, 1, line_depth]]
                    line_one['depth_ext'] = [[0, 1, line_depth + UNIT_DEPTH_DODGE]]
                line_list.append(line_one)
            # 更新
            if ratio_end > ratio_begin:
                ratio_begin = ratio_end

    # 处理轮廓 吸收线段
    for line_idx in range(len(line_list) - 1, -1, -1):
        line_cur = line_list[line_idx]
        type_cur, width_cur, depth_cur = line_cur['type'], line_cur['width'], line_cur['depth']
        # 排除
        if type_cur in [UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
            pass
        elif type_cur in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
            side_idx = (line_idx + 1 + len(line_list)) % len(line_list)
            line_side = line_list[side_idx]
            type_side = line_side['type']
            angle_cur, angle_side = line_cur['angle'], line_side['angle']
            link_cur, link_side, open_cur, open_side, open_merge = '', '', False, False, False
            if 'unit_to_type' in line_cur:
                link_cur = line_cur['unit_to_type']
            if 'unit_to_type' in line_side:
                link_side = line_side['unit_to_type']
            if type_cur in [UNIT_TYPE_DOOR] and link_cur in ['Balcony', 'Terrace']:
                open_cur = True
            elif type_cur in [UNIT_TYPE_WINDOW] and link_cur in ['Balcony', 'Terrace', '']:
                open_cur = True
            elif type_cur in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and link_cur in ['Balcony', 'Terrace', 'EquipmentRoom', 'OtherRoom']:
                open_cur = True
            if type_side in [UNIT_TYPE_DOOR] and link_side in ['Balcony', 'Terrace']:
                open_side = True
            elif type_side in [UNIT_TYPE_WINDOW] and link_side in ['Balcony', 'Terrace', '']:
                open_side = True
            # 通向阳台
            if open_cur and open_side:
                if type_cur == type_side:
                    open_merge = True
                elif type_cur in open_unit and type_side in open_unit:
                    open_merge = True
            # 合并门窗
            if abs(angle_cur - angle_side) < 0.1 and open_merge:
                width_old = line_side['width']
                width_add = line_cur['width']
                width_new = width_old + width_add
                line_side['p1'] = line_cur['p1'][:]
                line_side['height'] = min(line_side['height'], line_cur['height'])
                # 合并进深
                if 'depth_all' in line_side and 'depth_all' in line_cur:
                    for depth_one in line_side['depth_all']:
                        depth_one[0] = (depth_one[0] * width_old + width_add) / width_new
                        depth_one[1] = (depth_one[1] * width_old + width_add) / width_new
                    for depth_one in reversed(line_cur['depth_all']):
                        depth_add = depth_one.copy()
                        depth_add[0] = depth_add[0] * width_add / width_new
                        depth_add[1] = depth_add[1] * width_add / width_new
                        if len(line_side['depth_all']) > 0 and abs(line_side['depth_all'][0][2] - depth_add[2]) <= 0.01:
                            line_side['depth_all'][0][0] = depth_add[0]
                        else:
                            line_side['depth_all'].insert(0, depth_add)
                if 'depth_ext' in line_side and 'depth_ext' in line_cur:
                    for depth_one in line_side['depth_ext']:
                        depth_one[0] = (depth_one[0] * width_old + width_add) / width_new
                        depth_one[1] = (depth_one[1] * width_old + width_add) / width_new
                    for depth_one in reversed(line_cur['depth_ext']):
                        depth_add = depth_one.copy()
                        depth_add[0] = depth_add[0] * width_add / width_new
                        depth_add[1] = depth_add[1] * width_add / width_new
                        if len(line_side['depth_ext']) > 0 and abs(line_side['depth_ext'][0][2] - depth_add[2]) <= 0.01:
                            line_side['depth_ext'][0][0] = depth_add[0]
                        else:
                            line_side['depth_ext'].insert(0, depth_add)
                line_side['width'] = width_new
                # 更新部件
                line_list.pop(line_idx)
                line_cur, width_cur = line_side, line_side['width']
                side_idx = (line_idx + 1 + len(line_list)) % len(line_list)
                line_side = line_list[side_idx]
                width_side, angle_side = line_side['width'], line_side['angle']
                if abs(angle_cur - angle_side) < 0.1 and line_side['type'] in [UNIT_TYPE_AISLE, UNIT_TYPE_WALL] and \
                        width_side < width_cur * 0.5:
                    line_cur['width'] += line_side['width']
                    line_cur['p2'] = line_side['p2'][:]
                    line_list.pop(side_idx)
                continue
            elif type_cur in [UNIT_TYPE_DOOR]:
                continue
        else:
            continue

        # 长度
        merge_width = UNIT_WIDTH_MERGE
        # 避让
        dodge_flag, group_flag, merge_flag, merge_type, merge_room = False, False, False, UNIT_TYPE_NONE, ''
        for side_order in [1, -1]:
            side_idx = (line_idx + side_order + len(line_list)) % len(line_list)
            line_side = line_list[side_idx]
            side_type, side_room = line_side['type'], ''
            side_width, side_depth, side_height = line_side['width'], line_side['depth'], line_side['height']
            if 'unit_to_type' in line_side:
                side_room = line_side['unit_to_type']
            if side_type in [UNIT_TYPE_GROUP]:
                if side_height >= UNIT_HEIGHT_WALL - 0.1 and side_width >= UNIT_WIDTH_HOLE:
                    side_type = UNIT_TYPE_WINDOW
            angle_cur = normalize_line_angle(line_cur['angle'])
            angle_side = normalize_line_angle(line_side['angle'])
            angle_inner = normalize_line_angle(angle_cur + math.pi * 0.5 * side_order)
            if abs(angle_inner - angle_side) < 0.1:
                side_type, side_width = line_side['type'], line_side['width']
                if side_type in [UNIT_TYPE_DOOR] and side_width < UNIT_WIDTH_HOLE and line_cur['width'] > 0.1:
                    dodge_flag = True
            if abs(angle_cur - angle_side) < 0.1:
                if side_type in [UNIT_TYPE_GROUP] and type_cur in [UNIT_TYPE_WALL]:
                    group_flag = True
                if side_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                    if side_type in [UNIT_TYPE_AISLE] and side_depth >= 3:
                        merge_flag = False
                    elif side_room in ['Balcony', 'Terrace'] and width_cur < max(1.0, side_width):
                        merge_flag = True
                        merge_type, merge_room = side_type, side_room
                    elif side_room in ['Balcony', 'Terrace'] and side_width > min(0.5, width_cur):
                        merge_flag = True
                        merge_type, merge_room = side_type, side_room
                    elif side_room in ['Kitchen'] and side_type in [UNIT_TYPE_WINDOW]:
                        merge_flag = False
                    elif side_room in [''] and side_width > 1.5 and side_type in [UNIT_TYPE_WINDOW]:
                        merge_flag = True
                        merge_type, merge_room = side_type, side_room
                    elif merge_flag and not side_room == merge_room:
                        if merge_room in ['Balcony', 'Terrace'] and side_room in ROOM_TYPE_LEVEL_4:
                            pass
                        else:
                            merge_flag = False
                    elif line_cur['type'] in [UNIT_TYPE_AISLE] and line_cur['width'] > UNIT_WIDTH_MERGE and depth_cur > 3 > side_width:
                        merge_flag = False
                    elif line_cur['width'] < UNIT_WIDTH_MERGE_MIN * 1.0:
                        merge_flag = True
                        merge_type, merge_room = side_type, side_room
                    elif line_cur['width'] < min(UNIT_WIDTH_MERGE_MAX * 3.0, side_width * 0.50):
                        merge_flag = True
                        merge_type, merge_room = side_type, side_room
                    elif line_cur['width'] < min(UNIT_WIDTH_MERGE_MAX * 3.0, side_width * 1.00) and side_width > 1.0:
                        merge_flag = True
                        merge_type, merge_room = side_type, side_room
                    elif line_cur['width'] < min(UNIT_WIDTH_MERGE_MAX * 2.0, side_width * 1.00) and side_width > 0.5:
                        merge_flag = True
                        merge_type, merge_room = side_type, side_room
                if side_type in [UNIT_TYPE_AISLE] and type_cur in [UNIT_TYPE_WALL]:
                    if line_cur['width'] < 0.1 and side_width > 0.5:
                        merge_flag = True
                        merge_type, merge_room = side_type, side_room
        if dodge_flag and merge_type in [UNIT_TYPE_WINDOW]:
            continue
        if group_flag and merge_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
            continue
        if not merge_flag:
            continue
        # 两侧
        line_op = 0
        line_idx_1 = (line_idx - 1 + len(line_list)) % len(line_list)
        line_idx_2 = (line_idx + 1 + len(line_list)) % len(line_list)
        line_one_1 = line_list[line_idx_1]
        line_one_2 = line_list[line_idx_2]
        line_type_1, line_type_2 = line_one_1['type'], line_one_2['type']
        side_type_1, side_type_2 = '', ''
        if 'unit_to_type' in line_one_1:
            side_type_1 = line_one_1['unit_to_type']
        if 'unit_to_type' in line_one_2:
            side_type_2 = line_one_2['unit_to_type']

        if line_type_1 in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
            if line_type_2 in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
                if abs(normalize_line_angle(line_one_1['angle'] - line_cur['angle'])) <= 0.01:
                    if abs(normalize_line_angle(line_one_2['angle'] - line_cur['angle'])) <= 0.01:
                        if line_type_1 in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE] and line_type_2 in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                            pass
                        elif line_type_1 in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and line_type_2 in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                            if side_type_1 in ['Balcony', 'Terrace', ''] or side_type_2 in ['Balcony', 'Terrace', '']:
                                pass
                            else:
                                continue
        for side_order in [1, -1]:
            side_idx = (line_idx + side_order + len(line_list)) % len(line_list)
            line_side = line_list[side_idx]
            side_type, side_room = line_side['type'], ''
            side_width, side_depth, side_height = line_side['width'], line_side['depth'], line_side['height']
            if 'unit_to_type' in line_side:
                side_room = line_side['unit_to_type']
            if side_type in [UNIT_TYPE_DOOR] and side_room in ['Balcony', 'Terrace']:
                side_type = UNIT_TYPE_WINDOW
            # 普门
            if side_type in [UNIT_TYPE_DOOR]:
                # 距离
                distance = 5.0
                if len(main_door) > 0:
                    p0, p1, p2 = main_door, line_side['p1'], line_side['p2']
                    p3 = [p1[0] / 2 + p1[0] / 2, p1[1] / 2 + p2[1] / 2]
                    d3 = math.sqrt((p3[0] - p0[0]) * (p3[0] - p0[0]) + (p3[1] - p0[1]) * (p3[1] - p0[1]))
                    distance = d3
                # 主门
                if distance < 1.0:
                    merge_width = UNIT_WIDTH_MERGE_MIN * 1.5
                # 门洞
                elif side_width > UNIT_WIDTH_HOLE:
                    if room_type in ['DiningRoom']:
                        pass
                    elif room_type in ROOM_TYPE_LEVEL_1:
                        if side_room == '':
                            merge_width = max(UNIT_WIDTH_MERGE_MAX * 1.0, side_width * 0.50)
                        elif side_room in ['Balcony', 'Terrace']:
                            merge_width = max(UNIT_WIDTH_MERGE_MAX * 2.0, side_width * 1.00)
                        elif side_room in ['Kitchen']:
                            merge_width = UNIT_WIDTH_MERGE_MIN
                        else:
                            merge_width = min(UNIT_WIDTH_MERGE_MAX * 2.0, side_width * 0.50)
                    elif room_type in ROOM_TYPE_LEVEL_2:
                        if side_room == '':
                            merge_width = max(UNIT_WIDTH_MERGE_MAX * 1.0, side_width * 0.50)
                        elif side_room in ['Balcony', 'Terrace']:
                            merge_width = max(UNIT_WIDTH_MERGE_MAX * 2.0, side_width * 1.00)
                        else:
                            merge_width = min(UNIT_WIDTH_MERGE_MAX * 2.0, side_width * 0.50)
                    elif room_type in ROOM_TYPE_LEVEL_3:
                        pass
                    else:
                        merge_width = UNIT_WIDTH_MERGE_MAX + UNIT_WIDTH_MERGE
                # 走廊
                elif line_cur['type'] in [UNIT_TYPE_AISLE]:
                    merge_width = UNIT_WIDTH_MERGE_MIN
                    if room_type in ROOM_TYPE_LEVEL_2:
                        merge_width = UNIT_WIDTH_MERGE
                # 厨房
                elif 'Kitchen' in side_room or 'Bathroom' in side_room:
                    merge_width = UNIT_WIDTH_MERGE * 1.0
                # 客厅
                elif room_type in ROOM_TYPE_LEVEL_1:
                    merge_width = UNIT_WIDTH_MERGE * 1.0
                    if line_cur['width'] < min(UNIT_WIDTH_MERGE * 1.5, side_width * 0.50):
                        merge_width = min(UNIT_WIDTH_MERGE * 1.5, side_width * 0.50)
                # 卧室
                elif room_type in ROOM_TYPE_LEVEL_2:
                    merge_width = UNIT_WIDTH_MERGE * 1.0
                # 厨卫
                elif room_type in ROOM_TYPE_LEVEL_3:
                    merge_width = UNIT_WIDTH_MERGE * 1.0
            # 窗户
            elif side_type in [UNIT_TYPE_WINDOW]:
                side_idx_2 = (line_idx + side_order * 2 + len(line_list)) % len(line_list)
                line_side_2 = line_list[side_idx_2]
                if line_side_2['type'] == UNIT_TYPE_GROUP:
                    if line_side_2['height'] > UNIT_HEIGHT_WALL - 0.1 and line_side_2['width'] > 1 > side_width:
                        side_width += line_side_2['width']
                if room_type in ROOM_TYPE_LEVEL_4:
                    merge_width = UNIT_WIDTH_MERGE_MIN
                elif side_width > UNIT_WIDTH_HOLE + UNIT_WIDTH_DOOR:
                    merge_width = min(UNIT_WIDTH_MERGE_MAX * 3, side_width * 0.50)
                elif side_width > UNIT_WIDTH_HOLE:
                    merge_width = min(UNIT_WIDTH_MERGE_MAX * 3, side_width * 1.00)
                elif side_width > UNIT_WIDTH_DOOR:
                    merge_width = max(UNIT_WIDTH_MERGE_MAX + UNIT_WIDTH_MERGE, side_width * 1.00)
                elif side_width < 0.5:
                    merge_width = min(UNIT_WIDTH_MERGE_MAX, side_width)
                else:
                    merge_width = UNIT_WIDTH_MERGE_MAX + UNIT_WIDTH_MERGE
            # 窗户
            elif side_type in [UNIT_TYPE_GROUP] and side_height > UNIT_HEIGHT_WALL - 0.1:
                if 'Bath' in room_type:
                    merge_width = UNIT_WIDTH_MERGE_MIN
                else:
                    merge_width = UNIT_WIDTH_MERGE
            # 走廊
            elif side_type in [UNIT_TYPE_AISLE]:
                if side_depth >= 3:
                    if line_cur['width'] < 0.1 and side_width > 0.5:
                        merge_width = UNIT_WIDTH_MERGE_MIN
                    else:
                        continue
                elif line_type_1 in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE] and line_type_2 in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                    merge_width = UNIT_WIDTH_MERGE_MAX * 3
                elif side_width > UNIT_WIDTH_DOOR:
                    merge_width = UNIT_WIDTH_MERGE_MAX

            # 吸收
            if side_type in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
                line_op, line_new = merge_side_line(line_cur, line_side, side_order, merge_width)
                if line_op <= -1:
                    line_list.pop(line_idx)
                    break
            elif side_type in [UNIT_TYPE_GROUP] and side_height >= UNIT_HEIGHT_WALL - 0.1:
                line_op, line_new = merge_side_line(line_cur, line_side, side_order, merge_width)
                if line_op <= -1:
                    line_list.pop(line_idx)
                    break
            elif side_type in [UNIT_TYPE_GROUP]:
                merge_width = UNIT_WIDTH_MERGE_MIN
                line_op, line_new = merge_side_line(line_cur, line_side, side_order, merge_width)
                if line_op <= -1:
                    line_list.pop(line_idx)
                    break
        if line_op <= -1:
            continue

    # 处理轮廓 靠墙处理
    for line_idx in range(len(line_list) - 1, -1, -1):
        line_cur = line_list[line_idx]
        if line_cur['type'] not in [UNIT_TYPE_GROUP]:
            continue
        if line_cur['unit_flag'] in [-1, 1]:
            continue
        unit_best_index = line_idx
        unit_best_width = line_cur['width']
        unit_best_margin = line_cur['unit_margin']
        unit_best_edge = line_cur['unit_edge']
        unit_index_list = [line_idx]
        # 遍历信息
        for rest_idx in range(len(line_list) - 1, -1, -1):
            if rest_idx == line_idx:
                continue
            line_old = line_list[rest_idx]
            if not line_old['type'] == UNIT_TYPE_GROUP:
                continue
            if not line_old['unit_index'] == line_cur['unit_index']:
                continue
            if not line_old['unit_group'] == line_cur['unit_group']:
                continue
            # 添加索引
            unit_index_list.append(rest_idx)
            # 比较靠墙
            if line_old['unit_edge'] > 0 and unit_best_margin <= 0.01:
                continue
            elif line_old['unit_edge'] == 0 and line_old['unit_margin'] <= 0.01:
                pass
            elif line_old['width'] < unit_best_width * 0.5:
                continue
            elif line_old['width'] > unit_best_width * 2.0:
                pass
            elif line_old['unit_margin'] > unit_best_margin + 0.05:
                continue
            elif line_old['unit_margin'] < unit_best_margin - 0.05:
                pass
            elif line_old['unit_edge'] > unit_best_edge:
                continue
            unit_best_index = rest_idx
            unit_best_width = line_old['width']
            unit_best_margin = line_old['unit_margin']
            unit_best_edge = line_old['unit_edge']
        # 更新信息
        for suit_idx in unit_index_list:
            line_new = line_list[suit_idx]
            if suit_idx == unit_best_index:
                line_new['unit_flag'] = 1
            elif line_new['width'] < UNIT_DEPTH_BACK_MAX and line_new['depth'] >= UNIT_DEPTH_BACK_ERR:
                line_new['unit_flag'] = -1
            else:
                line_new['unit_flag'] = -1
                if line_new['unit_margin'] > 0.01:
                    line_new['depth'] = line_new['unit_margin']

    # 处理轮廓 避让线段
    for line_idx in range(len(line_list) - 1, -1, -1):
        line_cur = line_list[line_idx]
        type_cur, width_cur, depth_cur = line_cur['type'], line_cur['width'], line_cur['depth']
        # 排除
        if type_cur in [UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
            pass
        else:
            continue
        # 两侧
        for side_order in [-1, 1]:
            side_idx = (line_idx + side_order + len(line_list)) % len(line_list)
            line_side = line_list[side_idx]
            side_type, side_room, side_flag = line_side['type'], '', False
            side_width, side_depth, side_height = line_side['width'], line_side['depth'], line_side['height']
            side_width_original = side_width
            if 'width_original' in line_side:
                side_width_original = line_side['width_original']
            if 'unit_to_type' in line_side:
                side_room = line_side['unit_to_type']
            if side_type in [UNIT_TYPE_GROUP] and side_height >= UNIT_HEIGHT_WALL - 0.1:
                side_type = UNIT_TYPE_WINDOW
            # 角度
            angle_cur = normalize_line_angle(line_cur['angle'])
            angle_side = normalize_line_angle(line_side['angle'])
            angle_inner = normalize_line_angle(angle_cur + math.pi * 0.5 * side_order)
            angle_outer = normalize_line_angle(angle_cur - math.pi * 0.5 * side_order)
            # 长度
            dodge_width, dodge_type = UNIT_WIDTH_DODGE, UNIT_TYPE_SIDE
            # 平行
            if abs(angle_cur - angle_side) < 0.1:
                if type_cur in [UNIT_TYPE_WINDOW]:
                    pass
                elif side_type == UNIT_TYPE_GROUP:
                    if room_area <= 10 or room_type in ROOM_TYPE_LEVEL_3:
                        pass
                    elif line_cur['type'] in [UNIT_TYPE_AISLE] and line_cur['depth'] > 3:
                        pass
                elif side_type == UNIT_TYPE_AISLE and side_depth < 1.5:
                    side_idx2 = (line_idx + side_order * 2 + len(line_list)) % len(line_list)
                    line_post = line_list[side_idx2]
                    type_side2 = line_post['type']
                    width_side2 = line_post['width']
                    angle_side2 = normalize_line_angle(line_post['angle'])
                    if type_cur in [UNIT_TYPE_AISLE]:
                        pass
                    elif side_width < 1.0 and side_depth > 1.0 and abs(angle_inner - angle_side2) < 0.1 and type_side2 in [UNIT_TYPE_WINDOW]:
                        side_flag = True
                        dodge_width, dodge_type = UNIT_DEPTH_CURTAIN, UNIT_TYPE_SIDE
                    elif side_width < 1.0 and side_depth > 0.5 and abs(angle_cur - angle_side2) < 0.1 and width_side2 < UNIT_DEPTH_CURTAIN + 0.01:
                        side_flag = True
                        dodge_width, dodge_type = UNIT_DEPTH_CURTAIN, UNIT_TYPE_SIDE
                    elif side_width < 0.5 and side_depth > 1.0 and abs(angle_cur - angle_side2) < 0.1 and type_side2 in [UNIT_TYPE_SIDE]:
                        pass
                    else:
                        side_flag = True
                        dodge_width, dodge_type = UNIT_WIDTH_DODGE * 0.5, UNIT_TYPE_AISLE
            # 阴角
            elif abs(angle_inner - angle_side) < 0.1:
                if type_cur in [UNIT_TYPE_WINDOW]:
                    if side_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and side_width > width_cur:
                        if side_room in ROOM_TYPE_LEVEL_1 or side_room in ROOM_TYPE_LEVEL_2:
                            pass
                        else:
                            dodge_width = UNIT_DEPTH_CURTAIN
                            side_flag = True
                elif side_type in [UNIT_TYPE_DOOR]:
                    # 距离
                    distance = 5.0
                    if len(main_door) > 0:
                        p0, p1, p2 = main_door, line_side['p1'], line_side['p2']
                        p3 = [p1[0] / 2 + p1[0] / 2, p1[1] / 2 + p2[1] / 2]
                        d3 = math.sqrt((p3[0] - p0[0]) * (p3[0] - p0[0]) + (p3[1] - p0[1]) * (p3[1] - p0[1]))
                        distance = d3
                    # 避让
                    side_flag = True
                    # 主门
                    if distance < 1.0:
                        side_flag = True
                        dodge_width, dodge_type = UNIT_WIDTH_DODGE, UNIT_TYPE_SIDE
                        if side_room == '' and room_area < MAX_ROOM_AREA_LIVING:
                            dodge_width = UNIT_WIDTH_DODGE * 0.5
                    # 推门
                    elif side_width >= UNIT_WIDTH_HOLE * 0.8 or room_type in ROOM_TYPE_LEVEL_3:
                        side_flag = True
                        dodge_width, dodge_type = UNIT_DEPTH_DODGE, UNIT_TYPE_SIDE
                        if side_width >= UNIT_WIDTH_HOLE:
                            dodge_width = UNIT_DEPTH_CURTAIN
                            if side_room in ['Kitchen', 'MasterBathroom', 'SecondBathroom', 'Bathroom', 'OtherRoom']:
                                side_flag = False
                    # 正常
                    elif type_cur in [UNIT_TYPE_AISLE] and width_cur < UNIT_WIDTH_HOLE and depth_cur > 5:
                        side_flag = False
                    elif side_width < UNIT_WIDTH_DODGE:
                        side_flag = True
                        dodge_width, dodge_type = side_width, UNIT_TYPE_SIDE
                    elif side_width >= side_width_original:
                        side_flag = True
                        dodge_width, dodge_type = max(side_width_original - (side_width - side_width_original), 0), UNIT_TYPE_SIDE
                        if room_type in ROOM_TYPE_LEVEL_2:
                            dodge_width = min(dodge_width, UNIT_DEPTH_DODGE)
                    else:
                        side_flag = True
                        dodge_width, dodge_type = side_width, UNIT_TYPE_SIDE
                elif side_type in [UNIT_TYPE_WINDOW]:
                    side_flag = True
                    dodge_width, dodge_type = UNIT_DEPTH_CURTAIN, UNIT_TYPE_SIDE
                elif side_type in [UNIT_TYPE_GROUP] and side_height >= UNIT_HEIGHT_WALL - 0.1:
                    side_flag = True
                    dodge_width, dodge_type = UNIT_DEPTH_CURTAIN, UNIT_TYPE_SIDE
                    if side_width - side_width_original > 1:
                        side_flag = False
            # 阳角
            elif abs(angle_outer - angle_side) < 0.1:
                pass
            # 其他
            else:
                angle_dlt = (angle_side - angle_cur) * side_order
                angle_dlt = normalize_line_angle(angle_dlt)
                if type_cur in [UNIT_TYPE_WINDOW]:
                    pass
                # 锐角
                elif math.pi / 2 < angle_dlt <= math.pi:
                    side_flag = True
                    angle_dlt = math.pi - angle_dlt
                    if angle_dlt < 0.001:
                        dodge_width = line_side['width']
                    elif angle_dlt > math.pi / 2 - 0.001:
                        dodge_width = 0
                    else:
                        dodge_width = UNIT_WIDTH_DODGE / math.tan(angle_dlt)
                        if dodge_width < UNIT_WIDTH_DODGE:
                            dodge_width = UNIT_WIDTH_DODGE
                        if dodge_width > line_side['width']:
                            dodge_width = line_side['width']
                # 钝角
                elif 0 < angle_dlt <= math.pi / 2:
                    if side_type == UNIT_TYPE_DOOR:
                        side_flag = True
                        if room_type in ROOM_TYPE_LEVEL_3:
                            side_flag = False
                        elif line_side['width'] >= UNIT_WIDTH_HOLE:
                            dodge_width = UNIT_DEPTH_CURTAIN / 2
                            side_flag = True
                        elif line_side['width'] < UNIT_WIDTH_DODGE:
                            dodge_width = line_side['width']
                            side_flag = True
                    elif side_type == UNIT_TYPE_WINDOW:
                        dodge_width = UNIT_DEPTH_CURTAIN
                        side_flag = True
                    elif side_type in [UNIT_TYPE_GROUP] and side_height >= UNIT_HEIGHT_WALL - 0.1:
                        dodge_width = UNIT_DEPTH_CURTAIN
                        side_flag = True

            # 避让
            if side_flag:
                line_op, line_new = dodge_side_line(line_cur, line_side, side_order, dodge_width, dodge_type)
                # 分裂
                if line_op >= 1:
                    line_list.insert(line_idx, line_new)
                    line_idx += 1
                    if line_cur['width'] < 0.01:
                        pair_idx = (line_idx - side_order + len(line_list)) % len(line_list)
                        line_pair = line_list[pair_idx]
                        if abs(normalize_line_angle(line_pair['angle'] - line_cur['angle'])) < 0.1:
                            line_side['width'] += line_cur['width']
                            if side_order <= -1:
                                line_side['p1'] = line_cur['p1'][:]
                            else:
                                line_side['p2'] = line_cur['p2'][:]
                        else:
                            line_side['width'] += line_cur['width']
                            if side_order <= -1:
                                line_side['p2'] = line_cur['p2'][:]
                            else:
                                line_side['p1'] = line_cur['p1'][:]
                        line_list.pop(line_idx)
                # 退化
                elif line_op <= -1:
                    continue

    # 处理轮廓 背景线段
    for line_idx in range(len(line_list) - 1, -1, -1):
        line_cur = line_list[line_idx]
        line_pre = line_list[(line_idx - 1) % len(line_list)]
        line_post = line_list[(line_idx + 1) % len(line_list)]
        # 排除
        if line_cur['type'] not in [UNIT_TYPE_GROUP, UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
            continue
        if len(back_list) <= 0:
            break
        # 当前
        line_width = line_cur['width']
        x1, y1, x2, y2 = line_cur['p1'][0], line_cur['p1'][1], line_cur['p2'][0], line_cur['p2'][1]
        ratio_list_back = split_line_unit(x1, y1, x2, y2, back_list, UNIT_TYPE_GROUP, False, [], [], [])
        if line_cur['type'] in [UNIT_TYPE_GROUP]:
            pass
        elif line_cur['type'] in [UNIT_TYPE_SIDE] and line_cur['width'] <= UNIT_DEPTH_CURTAIN + 0.01:
            pass
        elif len(ratio_list_back) > 0:
            # 合并
            depth_new = 0
            ratio_new = [100, -100]
            for ratio_one in ratio_list_back:
                if line_width * (ratio_one[1] - ratio_one[0]) < UNIT_DEPTH_CURTAIN + 0.01:
                    if line_width > UNIT_DEPTH_CURTAIN + 0.01:
                        continue
                if ratio_one[0] < ratio_new[0]:
                    ratio_new[0] = ratio_one[0]
                if ratio_one[1] > ratio_new[1]:
                    ratio_new[1] = ratio_one[1]
                if ratio_one[UNIT_RATIO_DEPTH] > depth_new:
                    depth_new = ratio_one[UNIT_RATIO_DEPTH]
            # 更新
            if 0 < ratio_new[0] < 0.05:
                ratio_new[0] = 0
            if 0.95 < ratio_new[1] < 1:
                ratio_new[1] = 1
            if ratio_new[1] > ratio_new[0]:
                curtain_flag, curtain_lift = False, 0
                if ratio_new[0] <= 0 and line_pre['type'] in [UNIT_TYPE_WINDOW] and line_pre['height'] > 0.5:
                    if abs(depth_new - UNIT_DEPTH_CURTAIN) < 0.05:
                        curtain_flag = True
                        curtain_lift = line_pre['height']
                if ratio_new[1] >= 1 and line_post['type'] in [UNIT_TYPE_WINDOW] and line_post['height'] > 0.5:
                    if abs(depth_new - UNIT_DEPTH_CURTAIN) < 0.05:
                        curtain_flag = True
                        curtain_lift = line_post['height']
                # 分裂
                if depth_new > 0.05 or line_width * (ratio_new[1] - ratio_new[0]) > 2:
                    line_1, line_2, line_3 = {}, {}, {}
                    if depth_new >= UNIT_DEPTH_BACK_ERR and line_width * (ratio_new[1] - ratio_new[0]) > 1:
                        depth_new = UNIT_DEPTH_BACK_MID
                    if ratio_new[0] - 0 > 0.05:
                        line_1 = line_cur.copy()
                        x1_new = (x1 * (1 - ratio_new[0]) + x2 * ratio_new[0])
                        y1_new = (y1 * (1 - ratio_new[0]) + y2 * ratio_new[0])
                        line_1['p1'] = [x1, y1]
                        line_1['p2'] = [x1_new, y1_new]
                        line_1['width'] = line_width * (ratio_new[0] - 0)
                    if ratio_new[1] - ratio_new[0] > 0.05:
                        line_2 = line_cur.copy()
                        x1_new = (x1 * (1 - ratio_new[0]) + x2 * ratio_new[0])
                        y1_new = (y1 * (1 - ratio_new[0]) + y2 * ratio_new[0])
                        x2_new = (x1 * (1 - ratio_new[1]) + x2 * ratio_new[1])
                        y2_new = (y1 * (1 - ratio_new[1]) + y2 * ratio_new[1])
                        line_2['p1'] = [x1_new, y1_new]
                        line_2['p2'] = [x2_new, y2_new]
                        line_2['width'] = line_width * (ratio_new[1] - ratio_new[0])
                        if curtain_flag:
                            line_2['type'] = UNIT_TYPE_WINDOW
                            line_2['depth'] = UNIT_DEPTH_CURTAIN
                            line_2['height'] = curtain_lift
                        elif depth_new >= UNIT_DEPTH_BACK_MAX:
                            line_2['type'] = UNIT_TYPE_SIDE
                            line_2['depth'] = UNIT_DEPTH_BACK_MID
                            line_2['depth_all'] = [[0, 1, UNIT_DEPTH_BACK_MID]]
                            line_2['depth_ext'] = [[0, 1, UNIT_DEPTH_BACK_MID]]
                        else:
                            line_2['back_depth'] = depth_new
                            line_2['back_ratio'] = [0, 1]
                    if 1 - ratio_new[1] > 0.05:
                        line_3 = line_cur.copy()
                        x2_new = (x1 * (1 - ratio_new[1]) + x2 * ratio_new[1])
                        y2_new = (y1 * (1 - ratio_new[1]) + y2 * ratio_new[1])
                        line_3['p1'] = [x2_new, y2_new]
                        line_3['p2'] = [x2, y2]
                        line_3['width'] = line_width * (1 - ratio_new[1])
                    line_add = 0
                    if len(line_3) > 0:
                        line_list.insert(line_idx, line_3)
                        line_add += 1
                    if len(line_2) > 0:
                        line_list.insert(line_idx, line_2)
                        line_add += 1
                    if len(line_1) > 0:
                        line_list.insert(line_idx, line_1)
                        line_add += 1
                    if line_add > 0:
                        line_list.pop(line_idx + line_add)
                # 其他
                else:
                    line_cur['back_depth'] = depth_new
                    line_cur['back_ratio'] = ratio_new

    # 处理轮廓 估算线段
    for line_idx in range(len(line_list) - 1, -1, -1):
        line_cur = line_list[line_idx]
        line_cur['score'] = 0
        # 排除
        line_min_width = 0.001
        if line_cur['type'] in [UNIT_TYPE_SIDE]:
            line_min_width = UNIT_DEPTH_CURTAIN + 0.01
        if line_cur['width'] < line_min_width:
            line_cur['score'] = -1
            line_cur['score_pre'] = 0
            line_cur['score_post'] = 0
            line_cur['depth_pre'] = 0
            line_cur['depth_post'] = 0
            continue
        # 前段
        score_pre, depth_pre, depth_pre_more = check_side_line(line_idx, line_list, -1)
        line_cur['score'] += score_pre
        line_cur['score_pre'] = score_pre
        line_cur['depth_pre'] = depth_pre
        line_cur['depth_pre_more'] = depth_pre_more
        # 后段
        score_post, depth_post, depth_post_more = check_side_line(line_idx, line_list, 1)
        line_cur['score'] += score_post
        line_cur['score_post'] = score_post
        line_cur['depth_post'] = depth_post
        line_cur['depth_post_more'] = depth_post_more
        # 对面
        line_face, depth_face, depth_max = {}, 1.0, 0
        if 'depth_all' in line_cur:
            if len(line_cur['depth_all']) <= 0:
                if line_cur['type'] in [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]:
                    line_cur['depth_all'] = [[0, 1, min(depth_pre, depth_post)]]
                elif line_cur['type'] in [UNIT_TYPE_AISLE]:
                    line_cur['depth_all'] = [[0, 1, line_cur['depth']]]
            for depth_one in line_cur['depth_all']:
                if depth_max < depth_one[2]:
                    depth_max = depth_one[2]
            depth_all = line_cur['depth_all']
            if len(depth_all) > 0:
                if score_pre == 4 and depth_all[0][0] <= 0.01 and depth_all[0][2] > depth_pre_more + 0.10:
                    if depth_all[0][1] - depth_all[0][0] <= UNIT_WIDTH_DOOR * 0.5 / line_cur['width']:
                        depth_all[0][2] = depth_post_more
                    else:
                        depth_add = depth_all[0][:]
                        depth_add[2] = depth_pre_more
                        depth_add[1] = depth_add[0] + UNIT_WIDTH_DOOR * 0.5 / line_cur['width']
                        depth_all[0][0] = depth_add[1]
                        depth_all.insert(0, depth_add)
                elif score_post == 4 and depth_all[-1][1] >= 0.99 and depth_all[-1][2] > depth_post_more + 0.10:
                    if depth_all[-1][1] - depth_all[-1][0] <= UNIT_WIDTH_DOOR * 0.5 / line_cur['width']:
                        depth_all[-1][2] = depth_post_more
                    else:
                        depth_add = depth_all[-1][:]
                        depth_add[2] = depth_post_more
                        depth_add[0] = depth_add[1] - UNIT_WIDTH_DOOR * 0.5 / line_cur['width']
                        depth_all[-1][1] = depth_add[0]
                        depth_all.append(depth_add)
        if 'depth_ext' in line_cur:
            if len(line_cur['depth_ext']) <= 0:
                if line_cur['type'] in [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]:
                    line_cur['depth_ext'] = [[0, 1, min(depth_pre, depth_post)]]
                elif line_cur['type'] in [UNIT_TYPE_AISLE]:
                    line_cur['depth_ext'] = [[0, 1, line_cur['depth']]]
        # 深度扩展
        line_depth = depth_max
        if line_cur['type'] in [UNIT_TYPE_AISLE] and line_depth > 2.0:
            pass
        elif line_depth > min(depth_pre, depth_post):
            line_depth = min(depth_pre, depth_post)
        if score_pre > score_post and depth_pre > depth_post \
                and depth_post <= UNIT_DEPTH_GROUP_MIN and line_cur['width'] >= depth_pre:
            line_depth = depth_pre
        if score_post > score_pre and depth_post > depth_pre \
                and depth_pre <= UNIT_DEPTH_GROUP_MIN and line_cur['width'] >= depth_post:
            line_depth = depth_post
        if line_depth > depth_face > 0 and len(line_face) > 0:
            line_depth = depth_face
        # 深度限制
        if line_cur['type'] == UNIT_TYPE_GROUP:
            pass
        elif line_cur['type'] == UNIT_TYPE_WINDOW:
            if line_depth > UNIT_DEPTH_DODGE + UNIT_DEPTH_CURTAIN:
                line_depth = UNIT_DEPTH_DODGE + UNIT_DEPTH_CURTAIN
            line_cur['depth'] = line_depth
        else:
            line_cur['depth'] = line_depth

    # 返回
    return line_list, line_ori


# 分裂线段 部件分割
def split_line_unit(x1, y1, x2, y2, unit_list, unit_type=0, unit_pop=False, type_list=[], height_list=[], to_room_list=[]):
    unit_ratio_list = []
    # 轻微倾斜
    if abs(x1 - x2) <= 0.1 and abs(y1 - y2) > abs(x1 - x2):
        x2 = x1
    if abs(y1 - y2) <= 0.1 and abs(x1 - x2) > abs(y1 - y2):
        y2 = y1
    line_width, line_angle = calculate_line_angle(x1, y1, x2, y2)
    for unit_idx in range(len(unit_list) - 1, -1, -1):
        unit_ratio = []
        unit_one = unit_list[unit_idx][:]
        if len(unit_list[unit_idx]) == 10:
            unit_one = unit_list[unit_idx][0:-2]
        edge_len = int(len(unit_one) / 2)
        unit_group, unit_height, unit_to_room = '', UNIT_HEIGHT_WALL, ''
        if 0 <= unit_idx < len(type_list):
            unit_group = type_list[unit_idx]
        if 0 <= unit_idx < len(height_list):
            unit_height = height_list[unit_idx]
            if unit_type == UNIT_TYPE_WINDOW:
                if unit_height > UNIT_HEIGHT_WINDOW_TOP / 2:
                    unit_height = UNIT_HEIGHT_WINDOW_BOTTOM
        if 0 <= unit_idx < len(to_room_list):
            unit_to_room = to_room_list[unit_idx]
        for j in range(edge_len):
            x_p = unit_one[(2 * j + 0) % len(unit_one)]
            y_p = unit_one[(2 * j + 1) % len(unit_one)]
            x_q = unit_one[(2 * j + 2) % len(unit_one)]
            y_q = unit_one[(2 * j + 3) % len(unit_one)]
            x_r = unit_one[(2 * j + 4) % len(unit_one)]
            y_r = unit_one[(2 * j + 5) % len(unit_one)]
            x_s = unit_one[(2 * j + 6) % len(unit_one)]
            y_s = unit_one[(2 * j + 7) % len(unit_one)]
            # 宽度 深度 角度
            unit_margin = 0
            unit_width, unit_angle = calculate_line_angle(x_p, y_p, x_q, y_q)
            side_width_1, side_angle_1 = calculate_line_angle(x_q, y_q, x_r, y_r)
            side_width_2, side_angle_2 = calculate_line_angle(x_s, y_s, x_p, y_p)
            if max(side_width_1, side_width_2) > 0.5 > unit_width and unit_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                continue
            unit_depth = max(side_width_1, side_width_2)
            # 靠墙吸附
            group_margin = UNIT_WIDTH_MERGE * 1.0
            if j in [0]:
                group_margin = UNIT_WIDTH_MERGE * 1.0
            if unit_group in ['Meeting', 'Bed', 'Media']:
                if j in [0, 1, 3]:
                    group_margin = UNIT_WIDTH_MERGE * 1.5
                else:
                    group_margin = UNIT_WIDTH_MERGE * 1.0
            elif unit_group in ['Dining']:
                if j in [1, 3]:
                    group_margin = UNIT_WIDTH_MERGE * 1.0
                else:
                    group_margin = UNIT_WIDTH_MERGE * 1.0
            elif unit_group in ['Work', 'Rest']:
                if j in [1, 3]:
                    group_margin = UNIT_WIDTH_MERGE * 1.5
                else:
                    group_margin = UNIT_WIDTH_MERGE * 1.0
            elif unit_group in ['Armoire', 'Cabinet', 'Bath']:
                if j in [1, 3]:
                    group_margin = UNIT_WIDTH_MERGE * 1.5
                else:
                    group_margin = UNIT_WIDTH_MERGE * 1.5
            elif unit_group in ['']:
                group_margin = min(UNIT_WIDTH_MERGE * 1.0, unit_depth - 0.01)
            if abs(normalize_line_angle(line_angle - unit_angle)) > 0.2 and unit_type == UNIT_TYPE_GROUP:
                continue
            if determine_line_angle(line_angle) == 0:
                if not determine_line_angle(unit_angle) == 0:
                    continue
                unit_rely = False
                if abs(y_p - y1) < group_margin and (x2 - x1) * (y_p - y1) <= 0:
                    unit_rely = True
                elif y_q < y1 < y_r or y_q > y1 > y_r:
                    unit_rely = True
                if unit_type in [UNIT_TYPE_GROUP] and abs(normalize_line_angle(line_angle - unit_angle)) < 0.1 and unit_rely:
                    unit_margin = round((abs(y_p - y1) + abs(y_q - y1)) / 2, 2)
                    if unit_margin <= unit_depth - 0.01:
                        unit_depth += unit_margin
                    y_p, y_q = y1, y1
                elif unit_type in [UNIT_TYPE_WINDOW] and abs(normalize_line_angle(line_angle - unit_angle - math.pi)) < 0.1 and \
                        abs(y_p - y1) < group_margin and unit_width > 1:
                    unit_margin = round((abs(y_p - y1) + abs(y_q - y1)) / 2, 2)
                    if unit_margin <= unit_depth - 0.01:
                        unit_depth += unit_margin
                    y_p, y_q = y1, y1
                elif abs(y_p - y1) < 0.1 and abs(y_q - y1) < 0.1:
                    y_p, y_q = y1, y1
                elif abs((y_p + y_s) / 2 - y1) < 0.1 and abs((y_q + y_r) / 2 - y1) < 0.1:
                    y_p, y_q = y1, y1
                else:
                    continue
                # 分裂比例
                if abs(x2 - x1) >= 0.00001:
                    r_p = (x_p - x1) / (x2 - x1)
                    r_q = (x_q - x1) / (x2 - x1)
                elif abs(y2 - y1) >= 0.00001:
                    r_p = (y_p - y1) / (y2 - y1)
                    r_q = (y_q - y1) / (y2 - y1)
                else:
                    break
            elif determine_line_angle(line_angle) == 1:
                if not determine_line_angle(unit_angle) == 1:
                    continue
                unit_rely = False
                if abs(x_p - x1) < group_margin and (y2 - y1) * (x_p - x1) >= 0:
                    unit_rely = True
                elif x_q < x1 < x_r or x_q > x1 > x_r:
                    unit_rely = True
                if unit_type in [UNIT_TYPE_GROUP] and abs(normalize_line_angle(line_angle - unit_angle)) < 0.2 and unit_rely:
                    unit_margin = round((abs(x_p - x1) + abs(x_q - x1)) / 2, 2)
                    if unit_margin <= unit_depth - 0.01:
                        unit_depth += unit_margin
                    x_p, x_q = x1, x1
                elif unit_type in [UNIT_TYPE_WINDOW] and abs(normalize_line_angle(line_angle - unit_angle - math.pi)) < 0.2 and \
                        abs(x_p - x1) < group_margin and unit_width > 1:
                    unit_margin = round((abs(x_p - x1) + abs(x_q - x1)) / 2, 2)
                    if unit_margin <= unit_depth - 0.01:
                        unit_depth += unit_margin
                    x_p, x_q = x1, x1
                elif abs(x_p - x1) < 0.1 and abs(x_q - x1) < 0.1:
                    x_p, x_q = x1, x1
                elif abs((x_p + x_s) / 2 - x1) < 0.1 and abs((x_q + x_r) / 2 - x1) < 0.1:
                    x_p, x_q = x1, x1
                else:
                    continue
                # 分裂比例
                if abs(x2 - x1) >= 0.00001:
                    r_p = (x_p - x1) / (x2 - x1)
                    r_q = (x_q - x1) / (x2 - x1)
                elif abs(y2 - y1) >= 0.00001:
                    r_p = (y_p - y1) / (y2 - y1)
                    r_q = (y_q - y1) / (y2 - y1)
                else:
                    break
            else:
                if not determine_line_angle(line_angle - unit_angle) == 1:
                    continue
                dis_pre, ang_pre = line_width, line_angle
                dis_new, ang_new = calculate_line_angle(x1, y1, x_p, y_p)
                tmp_x_1, tmp_z_1 = dis_new * math.cos(ang_new - ang_pre), dis_new * math.sin(ang_new - ang_pre)
                dis_new, ang_new = calculate_line_angle(x1, y1, x_q, y_q)
                tmp_x_2, tmp_z_2 = dis_new * math.cos(ang_new - ang_pre), dis_new * math.sin(ang_new - ang_pre)
                if abs(tmp_z_1) < 0.2 and abs(tmp_z_2) < 0.2 \
                        and 0 - 0.1 < min(tmp_x_1, tmp_x_2) < max(tmp_x_1, tmp_x_2) < dis_pre + 0.1:
                    pass
                else:
                    continue
                if dis_pre < 0.001:
                    continue
                r_p, r_q = tmp_x_1 / dis_pre, tmp_x_2 / dis_pre
            if r_p <= 0.001 and r_q <= 0.001:
                continue
            if r_p >= 0.999 and r_q >= 0.999:
                continue
            if r_p <= -1 < r_q < 1 and j in [1, 3] and unit_margin > UNIT_WIDTH_MERGE * 0.5:
                continue
            if abs(r_p - r_q) < 0.001:
                continue
            # 线段比例
            if 0 <= r_p <= r_q <= 1:
                unit_ratio = [r_p, r_q, unit_depth, unit_height, unit_idx, unit_margin, j, unit_type, unit_group, unit_to_room]
            elif 0 <= r_q <= r_p <= 1:
                unit_ratio = [r_q, r_p, unit_depth, unit_height, unit_idx, unit_margin, j, unit_type, unit_group, unit_to_room]
            elif 0 <= r_p <= 1 <= r_q:
                unit_ratio = [r_p, 1, unit_depth, unit_height, unit_idx, unit_margin, j, unit_type, unit_group, unit_to_room]
            elif 0 <= r_q <= 1 <= r_p:
                unit_ratio = [r_q, 1, unit_depth, unit_height, unit_idx, unit_margin, j, unit_type, unit_group, unit_to_room]
            elif r_p <= 0 <= r_q <= 1:
                unit_ratio = [0, r_q, unit_depth, unit_height, unit_idx, unit_margin, j, unit_type, unit_group, unit_to_room]
            elif r_q <= 0 <= r_p <= 1:
                unit_ratio = [0, r_p, unit_depth, unit_height, unit_idx, unit_margin, j, unit_type, unit_group, unit_to_room]
            elif r_p <= 0 <= 1 <= r_q:
                unit_ratio = [0, 1, unit_depth, unit_height, unit_idx, unit_margin, j, unit_type, unit_group, unit_to_room]
            elif r_q <= 0 <= 1 <= r_p:
                unit_ratio = [0, 1, unit_depth, unit_height, unit_idx, unit_margin, j, unit_type, unit_group, unit_to_room]
            else:
                continue
            if line_width * unit_ratio[0] < 0.05:
                unit_ratio[0] = 0
            if line_width * (1 - unit_ratio[1]) < 0.05:
                unit_ratio[1] = 1
            if unit_type == UNIT_TYPE_DOOR:
                unit_ratio[0] -= UNIT_WIDTH_DOOR_FRAME / line_width
                unit_ratio[1] += UNIT_WIDTH_DOOR_FRAME / line_width
                if unit_ratio[0] < 0:
                    unit_ratio[0] = 0
                if unit_ratio[1] > 1:
                    unit_ratio[1] = 1
            break
        # 不含部件
        if len(unit_ratio) <= 0:
            continue
        if abs(unit_ratio[0] - unit_ratio[1]) < 0.001:
            continue
        # 包含部件
        if unit_pop:
            unit_list.pop(unit_idx)
        if len(unit_ratio_list) <= 0:
            unit_ratio_list.append(unit_ratio)
            continue
        ratio_find = False
        for ratio_idx, ratio_one in enumerate(unit_ratio_list):
            if ratio_one[0] >= unit_ratio[0]:
                ratio_find = True
                break
        if ratio_find:
            unit_ratio_list.insert(ratio_idx, unit_ratio)
        else:
            unit_ratio_list.append(unit_ratio)
    return unit_ratio_list


# 分裂线段 进深检测
def split_line_face(line_cur, face_wall, side_wall, tilt_wall, face_door, side_door, face_room, side_room,
                    face_group, side_group, width_aisle=UNIT_WIDTH_AISLE, room_type='', room_area=20, main_door=[]):
    ratio_list_depth, ratio_list_floor, ratio_list_aisle = [], [], []
    # 当前
    x1_cur, y1_cur, x2_cur, y2_cur = line_cur['p1'][0], line_cur['p1'][1], line_cur['p2'][0], line_cur['p2'][1]
    width_cur = line_cur['width']
    angle_cur = normalize_line_angle(line_cur['angle'])
    # 走道
    if room_area <= 10 or 'Bathroom' in room_type:
        width_aisle = UNIT_WIDTH_AISLE / 4

    # 对墙
    depth_max, depth_min, depth_max_rat, depth_min_rat = 2.0, 10.0, [], []
    for face_idx, face_one in enumerate(face_wall):
        # 对边
        x1_one, y1_one, x2_one, y2_one = face_one['p1'][0], face_one['p1'][1], face_one['p2'][0], face_one['p2'][1]
        angle_one, depth_one = face_one['angle'], UNIT_DEPTH_DODGE
        # 自身
        if abs(x1_cur - x1_one) < 0.01 and abs(y1_cur - y1_one) < 0.01:
            if abs(x2_cur - x2_one) < 0.01 and abs(y2_cur - y2_one) < 0.01:
                continue
        # 横墙
        if determine_line_angle(angle_cur) == 0 and determine_line_angle(angle_one) == 0:
            # 排除阳角
            if (x2_cur - x1_cur) * (y1_one - y2_cur) > 0:
                continue
            if abs(angle_cur - angle_one) > 1:
                r_p, r_q = (x1_one - x1_cur) / (x2_cur - x1_cur), (x2_one - x1_cur) / (x2_cur - x1_cur)
                # 前后
                if r_p > r_q:
                    r_o = r_p
                    r_p = r_q
                    r_q = r_o
                if r_p > 0.99 or r_q < 0.01:
                    continue
                if abs(min(r_q, 1) - max(r_p, 0)) < 0.1 and width_cur * abs(min(r_q, 1) - max(r_p, 0)) < 0.2:
                    continue
                depth_one = abs(y1_one - y1_cur)
                if depth_one > depth_max:
                    if len(depth_max_rat) <= 0:
                        depth_max, depth_max_rat = depth_one, [r_p, r_q]
                    elif r_p >= depth_max_rat[1] - 0.01 or r_q <= depth_max_rat[0] + 0.01:
                        depth_max, depth_max_rat = depth_one, [r_p, r_q]
                else:
                    if len(depth_max_rat) <= 0:
                        depth_max, depth_max_rat = depth_one, [r_p, r_q]
                    elif r_p <= depth_max_rat[0] + 0.01 and r_q >= depth_max_rat[1] - 0.01:
                        depth_max, depth_max_rat = depth_one, [r_p, r_q]
                if depth_one < depth_min:
                    if len(depth_min_rat) <= 0:
                        depth_min, depth_min_rat = depth_one, [r_p, r_q]
                    elif r_p >= depth_min_rat[1] - 0.01 or r_q <= depth_min_rat[0] + 0.01:
                        depth_min, depth_min_rat = depth_one, [r_p, r_q]
                else:
                    if len(depth_min_rat) <= 0:
                        depth_min, depth_min_rat = depth_one, [r_p, r_q]
                    elif r_p <= depth_min_rat[0] + 0.01 and r_q >= depth_min_rat[1] - 0.01:
                        depth_min, depth_min_rat = depth_one, [r_p, r_q]
            else:
                continue
        # 竖墙
        elif determine_line_angle(angle_cur) == 1 and determine_line_angle(angle_one) == 1:
            # 排除阳角
            if (y2_cur - y1_cur) * (x1_one - x2_cur) < 0:
                continue
            if abs(angle_cur - angle_one) > 1:
                r_p, r_q = (y1_one - y1_cur) / (y2_cur - y1_cur), (y2_one - y1_cur) / (y2_cur - y1_cur)
                # 前后
                if r_p > r_q:
                    r_o = r_p
                    r_p = r_q
                    r_q = r_o
                if r_p > 0.99 or r_q < 0.01:
                    continue
                depth_one = abs(x1_one - x1_cur)
                if depth_one > depth_max:
                    if len(depth_max_rat) <= 0:
                        depth_max, depth_max_rat = depth_one, [r_p, r_q]
                    elif r_p >= depth_max_rat[1] - 0.01 or r_q <= depth_max_rat[0] + 0.01:
                        depth_max, depth_max_rat = depth_one, [r_p, r_q]
                else:
                    if len(depth_max_rat) <= 0:
                        depth_max, depth_max_rat = depth_one, [r_p, r_q]
                    elif r_p <= depth_max_rat[0] + 0.01 and r_q >= depth_max_rat[1] - 0.01:
                        depth_max, depth_max_rat = depth_one, [r_p, r_q]
                if depth_one < depth_min:
                    if len(depth_min_rat) <= 0:
                        depth_min, depth_min_rat = depth_one, [r_p, r_q]
                    elif r_p >= depth_min_rat[1] - 0.01 or r_q <= depth_min_rat[0] + 0.01:
                        depth_min, depth_min_rat = depth_one, [r_p, r_q]
                else:
                    if len(depth_min_rat) <= 0:
                        depth_min, depth_min_rat = depth_one, [r_p, r_q]
                    elif r_p <= depth_min_rat[0] + 0.01 and r_q >= depth_min_rat[1] - 0.01:
                        depth_min, depth_min_rat = depth_one, [r_p, r_q]
            else:
                continue
        # 斜墙
        else:
            continue
    for face_idx, face_one in enumerate(face_wall):
        # 对边
        x1_one, y1_one, x2_one, y2_one = face_one['p1'][0], face_one['p1'][1], face_one['p2'][0], face_one['p2'][1]
        angle_one, width_one, depth_one = face_one['angle'], face_one['width'], UNIT_DEPTH_DODGE
        # 自身
        if abs(x1_cur - x1_one) < 0.01 and abs(y1_cur - y1_one) < 0.01:
            if abs(x2_cur - x2_one) < 0.01 and abs(y2_cur - y2_one) < 0.01:
                continue
        # 横墙
        if determine_line_angle(angle_cur) == 0 and determine_line_angle(angle_one) == 0:
            # 排除阳角
            if (x2_cur - x1_cur) * (y1_one - y2_cur) > 0:
                continue
            if abs(angle_cur - angle_one) > 1:
                r_p, r_q = (x1_one - x1_cur) / (x2_cur - x1_cur), (x2_one - x1_cur) / (x2_cur - x1_cur)
                depth_one = abs(y1_one - y1_cur)
            else:
                continue
        # 竖墙
        elif determine_line_angle(angle_cur) == 1 and determine_line_angle(angle_one) == 1:
            # 排除阳角
            if (y2_cur - y1_cur) * (x1_one - x2_cur) < 0:
                continue
            if abs(angle_cur - angle_one) > 1:
                r_p, r_q = (y1_one - y1_cur) / (y2_cur - y1_cur), (y2_one - y1_cur) / (y2_cur - y1_cur)
                depth_one = abs(x1_one - x1_cur)
            else:
                continue
        # 斜墙
        else:
            continue
        # 前后
        if r_p > r_q:
            r_o = r_p
            r_p = r_q
            r_q = r_o
        # 排除
        if r_q <= 0 + max(0.01, 0.1 / width_cur) or r_p >= 1 - max(0.01, 0.1 / width_cur):
            continue

        # 分裂
        split_flag, split_type = False, UNIT_TYPE_AISLE
        width_face = width_cur * abs(min(r_q, 1) - max(r_p, 0))
        if depth_one < depth_min + 0.1 < min(depth_max - 0.5, 3) and r_p <= depth_min_rat[0] + 0.01 and r_q >= depth_min_rat[1] - 0.01:
            if UNIT_WIDTH_DOOR * 0.50 < width_face < max(UNIT_WIDTH_DOOR * 1.50, width_cur * 0.30):
                split_flag, split_type = True, UNIT_TYPE_AISLE
            elif UNIT_WIDTH_DOOR * 0.50 < width_face < max(UNIT_WIDTH_DOOR * 2.00, width_cur * 0.50) and depth_one < width_aisle * 1.5:
                split_flag, split_type = True, UNIT_TYPE_AISLE
            elif depth_one <= width_aisle * 1.0 and width_face > 0.5:
                split_flag, split_type = True, UNIT_TYPE_AISLE
        elif depth_one <= width_aisle * 1.0 and width_face > 0.5:
            split_flag, split_type = True, UNIT_TYPE_AISLE
        elif depth_one <= width_aisle * 1.5 and width_face < 1.5 and (r_p <= 0 or r_q >= 1):
            if room_area > 15 and room_type in ROOM_TYPE_LEVEL_2:
                split_flag, split_type = True, UNIT_TYPE_AISLE
        elif depth_one >= depth_max - 0.1 >= max(depth_min + 0.5, 4) and r_p <= depth_max_rat[0] + 0.01 and r_q >= depth_max_rat[1] - 0.01:
            if UNIT_WIDTH_DOOR * 0.50 < width_face < max(UNIT_WIDTH_DOOR * 1.50, width_cur * 0.30):
                if room_area < width_face * 10:
                    pass
                elif max(width_cur * (depth_max_rat[0] - 0), width_cur * (1 - depth_max_rat[1])) <= 2:
                    pass
                else:
                    split_flag, split_type = True, UNIT_TYPE_AISLE
        elif depth_one >= depth_max - 0.1 >= 4 and width_cur < UNIT_WIDTH_HOLE:
            if UNIT_WIDTH_DOOR * 0.50 < width_face < UNIT_WIDTH_HOLE:
                if room_area < width_face * 10:
                    pass
                else:
                    split_flag, split_type = True, UNIT_TYPE_AISLE
        if split_flag:
            # 退化
            if r_p <= 0 + 0.001 and r_q >= 1 - 0.001:
                ratio_new = [0, 1, depth_one, 0, 0, 0, 0, UNIT_TYPE_AISLE, '', '']
                if depth_one <= 2:
                    ratio_list_depth.append(ratio_new.copy())
                ratio_list_floor.append(ratio_new.copy())
                ratio_list_aisle.append(ratio_new.copy())
                return ratio_list_depth, ratio_list_floor, ratio_list_aisle
            # 增加
            if r_p < 0 + 0.001:
                r_p = 0
            if r_q > 1 - 0.001:
                r_q = 1
            ratio_new = [r_p, r_q, depth_one, 0, 0, 0, 0, split_type, '', '']
            ratio_list_aisle.append(ratio_new)
        else:
            # 增加
            if r_p < 0 + 0.001:
                r_p = 0
            if r_q > 1 - 0.001:
                r_q = 1
            ratio_new = [r_p, r_q, depth_one, 0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
            ratio_find = False
            for ratio_idx, ratio_one in enumerate(ratio_list_depth):
                if ratio_new[0] <= ratio_one[0]:
                    ratio_list_depth.insert(ratio_idx, ratio_new)
                    ratio_find = True
                    break
            if not ratio_find:
                ratio_list_depth.append(ratio_new)
    # 侧墙
    if len(face_wall) <= 0 and len(tilt_wall) <= 0 and len(side_wall) >= 2:
        for i in [0, 1]:
            side_one = side_wall[i]
            angle_one = side_one['angle']
            angle_inside = angle_cur + (i - 0.5) * math.pi
            if abs(normalize_line_angle(angle_one - angle_inside)) < math.pi / 2 * 0.9:
                depth_one = side_one['width']
                ratio_new = [i * 0.5, (i + 1) * 0.5, depth_one, 0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
                ratio_find = False
                for ratio_idx, ratio_one in enumerate(ratio_list_depth):
                    if ratio_new[0] < ratio_one[0]:
                        ratio_list_depth.insert(ratio_idx, ratio_new)
                        ratio_find = True
                        break
                if not ratio_find:
                    ratio_list_depth.append(ratio_new)
    # 斜墙
    for tilt_one in tilt_wall:
        # 对边
        x1_one, y1_one, x2_one, y2_one = tilt_one['p1'][0], tilt_one['p1'][1], tilt_one['p2'][0], tilt_one['p2'][1]
        angle_one, width_one = tilt_one['angle'], tilt_one['width']
        if width_one <= UNIT_WIDTH_GROUP:
            continue
        # 自身
        if abs(x1_cur - x1_one) < 0.01 and abs(y1_cur - y1_one) < 0.01:
            if abs(x2_cur - x2_one) < 0.01 and abs(y2_cur - y2_one) < 0.01:
                continue
        r_p, r_q, d_p, d_q = 0, 0, 0, 0
        # 横墙
        if determine_line_angle(angle_cur) == 0:
            # 排除阳角
            if abs(normalize_line_angle(angle_one - (angle_cur + math.pi))) > math.pi / 2:
                continue
            r_p, r_q = (x1_one - x1_cur) / (x2_cur - x1_cur), (x2_one - x1_cur) / (x2_cur - x1_cur)
            d_p, d_q = abs(y1_one - y1_cur), abs(y2_one - y2_cur)
        # 竖墙
        elif determine_line_angle(angle_cur) == 1:
            # 排除阳角
            if abs(normalize_line_angle(angle_one - (angle_cur + math.pi))) > math.pi / 2:
                continue
            r_p, r_q = (y1_one - y1_cur) / (y2_cur - y1_cur), (y2_one - y1_cur) / (y2_cur - y1_cur)
            d_p, d_q = abs(x1_one - x1_cur), abs(x2_one - x2_cur)
        # 斜墙
        else:
            break
        if r_p > r_q:
            r_o, d_o = r_p, d_p
            r_p, d_p = r_q, d_q
            r_q, d_q = r_o, d_o
        if r_p <= 0:
            d_p = d_q + (d_p - d_q) * (0 - r_q) / (r_p - r_q)
            r_p = 0
        if r_q >= 1:
            d_q = d_p + (d_q - d_p) * (1 - r_p) / (r_q - r_p)
            r_q = 1
        num = 5
        for i in range(num):
            ratio_new = [r_p + (r_q - r_p) * i / num, r_p + (r_q - r_p) * (i + 1) / num, d_p + (d_q - d_p) * i / num,
                         0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
            ratio_find = False
            for ratio_idx, ratio_one in enumerate(ratio_list_depth):
                if ratio_new[0] < ratio_one[0]:
                    ratio_list_depth.insert(ratio_idx, ratio_new)
                    ratio_find = True
                    break
            if not ratio_find:
                ratio_list_depth.append(ratio_new)
    # 墙体
    ratio_list_floor = []
    for ratio_list_old in [ratio_list_aisle, ratio_list_depth]:
        for ratio_old in ratio_list_old:
            ratio_new = ratio_old[:]
            ratio_find = False
            for ratio_idx, ratio_one in enumerate(ratio_list_depth):
                if ratio_new[0] <= ratio_one[0]:
                    ratio_list_floor.insert(ratio_idx, ratio_new)
                    ratio_find = True
                    break
            if not ratio_find:
                ratio_list_floor.append(ratio_new)
    # 剔除
    for ratio_idx in range(len(ratio_list_floor) - 1, -1, -1):
        ratio_one = ratio_list_floor[ratio_idx]
        if ratio_one[1] - ratio_one[0] <= 0.02:
            ratio_list_floor.pop(ratio_idx)
        elif 0 <= ratio_idx - 1 < len(ratio_list_floor):
            ratio_old = ratio_list_floor[ratio_idx - 1]
            if abs(ratio_one[2] - ratio_old[2]) < 0.01:
                ratio_old[2] = min(ratio_old[2], ratio_one[2])
                ratio_old[1] = max(ratio_old[1], ratio_one[1])
                ratio_list_floor.pop(ratio_idx)

    # 对门
    depth_ratio_door = []
    for face_idx, face_one in enumerate(face_door):
        face_link = ''
        if 0 <= face_idx < len(face_room):
            face_link = face_room[face_idx]
        # 对边
        x1_one, y1_one, x2_one, y2_one = face_one['p1'][0], face_one['p1'][1], face_one['p2'][0], face_one['p2'][1]
        angle_one = face_one['angle']
        width_one = max(abs(x1_one - x2_one), abs(y1_one - y2_one))
        # 自身
        if abs(x1_cur - x1_one) < 0.01 and abs(y1_cur - y1_one) < 0.01:
            if abs(x2_cur - x2_one) < 0.01 and abs(y2_cur - y2_one) < 0.01:
                continue
        # 横墙
        if determine_line_angle(angle_cur) == 0 and determine_line_angle(angle_one) == 0:
            # 排除通向
            if room_type in ROOM_TYPE_LEVEL_1 and 2.0 < width_cur < 4.0:
                if face_link in ROOM_TYPE_LEVEL_2 or face_link in ROOM_TYPE_LEVEL_3:
                    continue
            # 排除阳角
            if (x2_cur - x1_cur) * (y1_one - y2_cur) > 0:
                continue
            # 进深影响
            if abs(angle_one - angle_cur) < 1:
                r_p = (x1_one - x1_cur) / (x2_cur - x1_cur)
                r_q = (x2_one - x1_cur) / (x2_cur - x1_cur)
                depth_one = abs(y1_one - y1_cur)
                width_one = abs(x1_one - x2_one)
            else:
                continue
        # 竖墙
        elif determine_line_angle(angle_cur) == 1 and determine_line_angle(angle_one) == 1:
            # 排除通向
            if room_type in ROOM_TYPE_LEVEL_1 and 2.0 < width_cur < 4.0:
                if face_link in ROOM_TYPE_LEVEL_2 or face_link in ROOM_TYPE_LEVEL_3:
                    continue
            # 排除阳角
            if (y2_cur - y1_cur) * (x1_one - x2_cur) < 0:
                continue
            # 进深影响
            if abs(angle_one - angle_cur) < 1:
                r_p = (y1_one - y1_cur) / (y2_cur - y1_cur)
                r_q = (y2_one - y1_cur) / (y2_cur - y1_cur)
                depth_one = abs(x1_one - x1_cur)
                width_one = abs(y1_one - y2_one)
            else:
                continue
        # 斜墙
        else:
            break
        # 前后
        if r_p > r_q:
            r_o = r_p
            r_p = r_q
            r_q = r_o
        # 排除
        side_flag = False
        if width_cur * abs(0 - r_q) < 0.2 and width_cur > 1:
            r_d = min(width_cur * (r_q - r_p), UNIT_WIDTH_DOOR) / width_cur
            r_p, r_q = 0, 0 + r_d
            side_flag = True
        if width_cur * abs(r_p - 1) < 0.2 and width_cur > 1:
            r_d = min(width_cur * (r_q - r_p), UNIT_WIDTH_DOOR) / width_cur
            r_p, r_q = 1 - r_d, 1
            side_flag = True
        if r_q <= 0 or r_p >= 1:
            continue
        # 分裂
        if depth_one <= width_aisle and not side_flag:
            continue
        else:
            depth_dodge = UNIT_DEPTH_DODGE / 2
            if room_type in ['Balcony', 'Terrace', 'Kitchen'] and width_one > 0.5:
                depth_dodge = 0
            elif room_type in ROOM_TYPE_LEVEL_3 and width_one > UNIT_WIDTH_HOLE:
                depth_dodge = 0
            elif room_type in ROOM_TYPE_LEVEL_3:
                depth_dodge = UNIT_DEPTH_DODGE * 1
            elif room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
                if face_link in ['']:
                    depth_dodge = UNIT_DEPTH_DODGE * 1
                elif width_one > UNIT_WIDTH_HOLE * 1.0:
                    depth_dodge = UNIT_DEPTH_CURTAIN * 1
                elif width_one > UNIT_WIDTH_HOLE * 0.8 and face_link in ['Kitchen']:
                    depth_dodge = UNIT_DEPTH_CURTAIN * 1
            elif face_link in ['']:
                depth_dodge = UNIT_DEPTH_DODGE * 1
            depth_one -= depth_dodge
            if r_p < 0:
                r_p = 0
            if r_q > 1:
                r_q = 1
            ratio_new = [r_p, r_q, depth_one, 0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
            depth_ratio_door.append(ratio_new)
    # 侧门
    for side_idx, side_one in enumerate(side_door):
        side_link = ''
        if 0 <= side_idx < len(side_room):
            side_link = side_room[side_idx]
        # 侧边
        x1_one, y1_one, x2_one, y2_one = side_one['p1'][0], side_one['p1'][1], side_one['p2'][0], side_one['p2'][1]
        angle_one, depth_one = side_one['angle'], UNIT_DEPTH_DODGE
        dodge_ratio = 0
        # 横墙
        if determine_line_angle(angle_cur) == 0 and determine_line_angle(angle_one) == 1:
            width_one = abs(y1_one - y2_one)
            if abs(x1_one - x2_cur) < abs(x1_one - x1_cur):
                suit_angle = normalize_line_angle(angle_cur + math.pi / 2)
            else:
                suit_angle = normalize_line_angle(angle_cur - math.pi / 2)
            # 排除通向
            if room_type in ROOM_TYPE_LEVEL_2 and 0.5 < depth_one < 1.5 and 2.0 < width_cur < 4.0:
                if side_link in ['CloakRoom']:
                    continue
            # 排除阳角
            if (x2_cur - x1_cur) * (y1_one - y2_cur) > 0:
                continue
            if abs(angle_one - suit_angle) > 1:
                depth_one = min(abs(y1_one - y1_cur), abs(y2_one - y1_cur))
            else:
                continue
            # 起止方向
            if abs(x1_one - x1_cur) < 0.1 and abs(x2_one - x1_cur) < 0.1:
                dodge_ratio = -1
            elif abs(x1_one - x2_cur) < 0.1 and abs(x2_one - x2_cur) < 0.1:
                dodge_ratio = 1
            elif x1_cur < (x1_one + x2_one) / 2 < x2_cur or x2_cur < (x1_one + x2_one) / 2 < x1_cur:
                dodge_ratio = ((x1_one + x2_one) / 2 - x1_cur) / (x2_cur - x1_cur)
            else:
                continue
        # 竖墙
        elif determine_line_angle(angle_cur) == 1 and determine_line_angle(angle_one) == 0:
            width_one = abs(x1_one - x2_one)
            if abs(y1_one - y2_cur) < abs(y1_one - y1_cur):
                suit_angle = normalize_line_angle(angle_cur + math.pi / 2)
            else:
                suit_angle = normalize_line_angle(angle_cur - math.pi / 2)
            # 排除通向
            if room_type in ROOM_TYPE_LEVEL_2 and 0.5 < depth_one < 1.5 and 2.0 < width_cur < 4.0:
                if side_link in ['CloakRoom']:
                    continue
            # 排除阳角
            if (y2_cur - y1_cur) * (x1_one - x2_cur) < 0:
                continue
            if abs(angle_one - suit_angle) > 1:
                depth_one = min(abs(x1_one - x1_cur), abs(x2_one - x1_cur))
            else:
                continue
            # 起止方向
            if abs(y1_one - y1_cur) < 0.1 and abs(y2_one - y1_cur) < 0.1:
                dodge_ratio = 0
            elif abs(y1_one - y2_cur) < 0.1 and abs(y2_one - y2_cur) < 0.1:
                dodge_ratio = 1
            elif y1_cur < (y1_one + y2_one) / 2 < y2_cur or y2_cur < (y1_one + y2_one) / 2 < y1_cur:
                dodge_ratio = ((y1_one + y2_one) / 2 - y1_cur) / (y2_cur - y1_cur)
            else:
                continue

        # 斜墙
        else:
            width_one, angle_one = calculate_line_angle(x1_one, y1_one, x2_one, y2_one)
            dis1_1, angle1_1 = calculate_line_angle(x1_cur, y1_cur, x1_one, y1_one)
            dis1_2, angle1_2 = calculate_line_angle(x1_cur, y1_cur, x2_one, y2_one)
            dis2_1, angle2_1 = calculate_line_angle(x2_cur, y2_cur, x1_one, y1_one)
            dis2_2, angle2_2 = calculate_line_angle(x2_cur, y2_cur, x2_one, y2_one)
            depth_one = min(dis1_1, dis1_2, dis2_1, dis2_2)
            angle_dlt1 = abs(normalize_line_angle(angle1_1 - angle_cur))
            angle_dlt2 = abs(normalize_line_angle(angle2_1 - angle_cur))
            if abs(angle_dlt1 - math.pi / 2) < 0.01:
                dodge_ratio = 0
            elif abs(angle_dlt2 - math.pi / 2) < 0.01:
                dodge_ratio = 1
            else:
                continue
        # 分裂
        dodge_width = UNIT_WIDTH_DODGE * 1.00
        if width_one >= UNIT_WIDTH_HOLE * 0.8:
            if room_type in ['DiningRoom']:
                dodge_width = UNIT_DEPTH_CURTAIN * 1.0
            elif room_type in ['LivingDiningRoom', 'LivingRoom'] and width_cur < UNIT_WIDTH_HOLE:
                dodge_width = UNIT_DEPTH_CURTAIN * 1.0
            elif side_link in ['', 'Kitchen']:
                dodge_width = UNIT_WIDTH_DODGE * 0.50
            else:
                continue
        elif room_type in ROOM_TYPE_LEVEL_1:
            dodge_width = UNIT_WIDTH_DODGE * 0.50
        elif room_type in ROOM_TYPE_LEVEL_2:
            dodge_width = UNIT_WIDTH_DODGE * 0.50

        if dodge_width > width_one:
            dodge_width = width_one
        if len(main_door) > 0:
            p1 = [(x1_one + x2_one) / 2, (y1_one + y2_one) / 2]
            p2 = main_door
            distance = math.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]))
            if distance < 0.5:
                dodge_width = UNIT_WIDTH_DODGE * 1.00
        if dodge_ratio <= 0:
            r_p, r_q = 0, dodge_width / width_cur
            if r_q > 1:
                r_q = 1
        elif dodge_ratio >= 1:
            r_q, r_p = 1, 1 - dodge_width / width_cur
            if r_p < 0:
                r_p = 0
        else:
            r_p, r_q = dodge_ratio - dodge_width / width_cur, dodge_ratio + dodge_width / width_cur
            if r_p < 0:
                r_p = 0
            if r_q > 1:
                r_q = 1
        ratio_new = [r_p, r_q, depth_one, 0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
        depth_ratio_door.append(ratio_new)

    # 对柜
    for face_one in face_group:
        # 对边
        x1_one, y1_one, x2_one, y2_one = face_one['p1'][0], face_one['p1'][1], face_one['p2'][0], face_one['p2'][1]
        angle_one, depth_one = face_one['angle'], UNIT_DEPTH_DODGE
        # 横墙
        if determine_line_angle(angle_cur) == 0 and determine_line_angle(angle_one) == 0:
            r_p, r_q = (x1_one - x1_cur) / (x2_cur - x1_cur), (x2_one - x1_cur) / (x2_cur - x1_cur)
            depth_one = abs(y1_one - y1_cur)
            if abs(r_q - r_p) > 0.5 and depth_one < UNIT_DEPTH_CURTAIN + 0.01:
                continue
        # 竖墙
        elif determine_line_angle(angle_cur) == 1 and determine_line_angle(angle_one) == 1:
            r_p, r_q = (y1_one - y1_cur) / (y2_cur - y1_cur), (y2_one - y1_cur) / (y2_cur - y1_cur)
            depth_one = abs(x1_one - x1_cur)
            if abs(r_q - r_p) > 0.2 and depth_one < UNIT_DEPTH_CURTAIN + 0.01:
                continue
        # 斜墙
        else:
            continue
        # 前后
        if r_p > r_q:
            r_o = r_p
            r_p = r_q
            r_q = r_o
        # 排除
        if r_q <= 0 + max(0.01, 0.1 / width_cur) or r_p >= 1 - max(0.01, 0.1 / width_cur):
            continue
        if depth_one >= UNIT_DEPTH_DODGE:
            continue
        else:
            # 增加
            if r_p < 0:
                r_p = 0
            if r_q > 1:
                r_q = 1
            ratio_new = [r_p, r_q, depth_one, 0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
            ratio_find = False
            for ratio_idx, ratio_one in enumerate(ratio_list_depth):
                if ratio_new[0] <= ratio_one[0]:
                    ratio_list_depth.insert(ratio_idx, ratio_new)
                    ratio_find = True
                    break
            if not ratio_find:
                ratio_list_depth.append(ratio_new)
    # 侧柜
    for side_one in side_group:
        # 侧边
        x1_one, y1_one, x2_one, y2_one = side_one['p1'][0], side_one['p1'][1], side_one['p2'][0], side_one['p2'][1]
        unit_width, unit_depth, unit_angle = side_one['width'], side_one['depth'], side_one['angle']
        dodge_ratio = 0
        # 横墙
        if determine_line_angle(angle_cur) == 0 and determine_line_angle(unit_angle) == 1:
            # 排除单元
            if min(y1_one, y2_one) > y1_cur + 0.1 or max(y1_one, y2_one) < y1_cur - 0.1:
                continue
            elif min(x1_cur, x2_cur) > x1_one + unit_depth or max(x1_cur, x2_cur) < x1_one - unit_depth:
                continue
            depth_one = min(abs(y1_one - y1_cur), abs(y2_one - y1_cur))
            # 起止方向
            if abs(x1_one - x1_cur) < UNIT_DEPTH_CURTAIN + 0.01 and abs(x2_one - x1_cur) < UNIT_DEPTH_CURTAIN + 0.01:
                dodge_ratio = -1
            elif abs(x1_one - x2_cur) < UNIT_DEPTH_CURTAIN + 0.01 and abs(x2_one - x2_cur) < UNIT_DEPTH_CURTAIN + 0.01:
                dodge_ratio = 1
            elif x1_cur < (x1_one + x2_one) / 2 < x2_cur or x2_cur < (x1_one + x2_one) / 2 < x1_cur:
                dodge_ratio = ((x1_one + x2_one) / 2 - x1_cur) / (x2_cur - x1_cur)
            else:
                continue
        # 竖墙
        elif determine_line_angle(angle_cur) == 1 and determine_line_angle(unit_angle) == 0:
            # 排除单元
            if min(x1_one, x2_one) > x1_cur + 0.1 or max(x1_one, x2_one) < x1_cur - 0.1:
                continue
            elif min(y1_cur, y2_cur) > y1_one + unit_depth or max(y1_cur, y2_cur) < y1_one - unit_depth:
                continue
            depth_one = min(abs(x1_one - x1_cur), abs(x2_one - x1_cur))
            # 起止方向
            if abs(y1_one - y1_cur) < UNIT_DEPTH_CURTAIN + 0.01 and abs(y2_one - y1_cur) < UNIT_DEPTH_CURTAIN + 0.01:
                dodge_ratio = 0
            elif abs(y1_one - y2_cur) < UNIT_DEPTH_CURTAIN + 0.01 and abs(y2_one - y2_cur) < UNIT_DEPTH_CURTAIN + 0.01:
                dodge_ratio = 1
            elif y1_cur < (y1_one + y2_one) / 2 < y2_cur or y2_cur < (y1_one + y2_one) / 2 < y1_cur:
                dodge_ratio = ((y1_one + y2_one) / 2 - y1_cur) / (y2_cur - y1_cur)
            else:
                continue
        # 斜墙
        else:
            continue
        # 分裂
        dodge_depth = max(UNIT_DEPTH_CURTAIN, depth_one)
        dodge_angle = normalize_line_angle(unit_angle + math.pi / 2)
        if abs(normalize_line_angle(dodge_angle - angle_cur)) < math.pi / 4:
            r_p, r_q = max(dodge_ratio, 0), min(dodge_ratio + dodge_depth / width_cur, 1)
        elif abs(normalize_line_angle(dodge_angle - angle_cur - math.pi)) < math.pi / 4:
            r_p, r_q = max(dodge_ratio - dodge_depth / width_cur, 0), min(dodge_ratio, 1)
        else:
            r_p, r_q = max(dodge_ratio - dodge_depth * 0.5 / width_cur, 0), min(dodge_ratio + dodge_depth * 0.5 / width_cur, 1)
        # 分裂
        split_flag, split_type = False, UNIT_TYPE_SIDE
        if depth_one < 0.1:
            split_flag = True
        if split_flag:
            ratio_new = [r_p, r_q, depth_one, 0, 0, 0, 0, split_type, '', '']
            ratio_list_aisle.append(ratio_new)
        else:
            ratio_new = [r_p, r_q, depth_one, 0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
            depth_ratio_door.append(ratio_new)

    # 添加
    for ratio_new in depth_ratio_door:
        ratio_find, ratio_dump = False, []
        for ratio_idx, ratio_one in enumerate(ratio_list_depth):
            if ratio_new[1] <= ratio_one[0]:
                break
            elif ratio_new[0] <= ratio_one[0] and ratio_one[1] <= ratio_new[1]:
                if ratio_new[2] <= ratio_one[2]:
                    ratio_one[2] = ratio_new[2]
                ratio_new[0] = ratio_one[1]
            elif ratio_one[0] <= ratio_new[0] and ratio_new[1] <= ratio_one[1]:
                if ratio_new[2] < ratio_one[2]:
                    # 前段
                    if ratio_new[0] - ratio_one[0] > 0.05 or width_cur * (ratio_new[0] - ratio_one[0]) > 0.2:
                        ratio_add = [ratio_one[0], ratio_new[0], ratio_one[2], 0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
                        ratio_list_depth.insert(ratio_idx, ratio_add)
                        ratio_idx += 1
                    else:
                        ratio_new[0] = ratio_one[0]
                    # 中段
                    ratio_list_depth.insert(ratio_idx, ratio_new)
                    ratio_idx += 1
                    # 后段
                    if ratio_one[1] - ratio_new[1] > 0.05 and width_cur * (ratio_one[1] - ratio_new[1]) > 0.2:
                        ratio_add = [ratio_new[1], ratio_one[1], ratio_one[2], 0, 0, 0, 0, UNIT_TYPE_WALL, '', '']
                        ratio_list_depth.insert(ratio_idx, ratio_add)
                        ratio_idx += 1
                    else:
                        ratio_new[1] = ratio_one[1]
                    # 删除
                    ratio_list_depth.pop(ratio_idx)
                ratio_find = True
                break
        if ratio_new[1] - ratio_new[0] <= 0.02:
            continue
        if ratio_find:
            continue
        # 增加
        for ratio_idx, ratio_one in enumerate(ratio_list_depth):
            # 前段
            if ratio_new[0] < ratio_one[1] < ratio_new[1]:
                if ratio_new[2] < ratio_one[2]:
                    ratio_one[1] = ratio_new[0]
                else:
                    ratio_new[0] = ratio_one[1]
                continue
            # 中段
            if ratio_new[0] < ratio_new[1] < ratio_one[0]:
                ratio_list_depth.insert(ratio_idx, ratio_new)
                ratio_find = True
                break
            # 后段
            if ratio_new[0] < ratio_one[0] < ratio_new[1]:
                if ratio_new[2] < ratio_one[2]:
                    ratio_one[0] = ratio_new[1]
                else:
                    ratio_new[1] = ratio_one[0]
                ratio_list_depth.insert(ratio_idx, ratio_new)
                ratio_find = True
                break
        if not ratio_find:
            ratio_list_depth.append(ratio_new)
    # 剔除
    for ratio_idx in range(len(ratio_list_depth) - 1, -1, -1):
        ratio_one = ratio_list_depth[ratio_idx]
        if ratio_one[1] - ratio_one[0] <= 0.02:
            ratio_list_depth.pop(ratio_idx)
        elif 0 <= ratio_idx - 1 < len(ratio_list_depth):
            ratio_old = ratio_list_depth[ratio_idx - 1]
            if abs(ratio_one[2] - ratio_old[2]) < 0.01:
                ratio_old[2] = min(ratio_old[2], ratio_one[2])
                ratio_old[1] = max(ratio_old[1], ratio_one[1])
                ratio_list_depth.pop(ratio_idx)

    # 返回信息
    return ratio_list_depth, ratio_list_floor, ratio_list_aisle


# 分裂线段 斜墙分类
def class_line_tilt(line_cur, line_list, door_list):
    face_wall, face_door, side_door = [], [], []
    angle_cur = line_cur['angle']
    for line_one in line_list:
        angle_one = line_one['angle']
        angle_dlt = abs(normalize_line_angle(angle_cur - angle_one))
        if abs(angle_dlt - math.pi) < 0.01:
            face_wall.append(line_one)
    for line_one in door_list:
        angle_one = line_one['angle']
        angle_dlt = abs(normalize_line_angle(angle_cur - angle_one))
        if abs(angle_dlt - math.pi) < 0.01 or abs(angle_dlt) < 0.01:
            face_door.append(line_one)
        elif abs(angle_dlt - math.pi / 2) < 0.01:
            side_door.append(line_one)
    return face_wall, face_door, side_door


# 吸收部件
def merge_side_line(line_cur, line_side, side_order=-1, merge_width=UNIT_DEPTH_GROUP_MIN):
    if abs(line_cur['angle'] - line_side['angle']) <= 0.1:
        if line_cur['width'] < merge_width:
            width_old = line_side['width']
            width_add = line_cur['width']
            width_new = width_old + width_add
            if side_order < 0:
                line_side['p2'] = line_cur['p2'][:]
                line_side['p2_original'] = line_side['p2'][:]
                if 'depth_all' in line_side and 'depth_all' in line_cur:
                    for depth_one in line_side['depth_all']:
                        depth_one[0] = depth_one[0] * width_old / width_new
                        depth_one[1] = depth_one[1] * width_old / width_new
                    for depth_one in line_cur['depth_all']:
                        depth_add = depth_one.copy()
                        depth_add[0] = (depth_add[0] * width_add + width_old) / width_new
                        depth_add[1] = (depth_add[1] * width_add + width_old) / width_new
                        if len(line_side['depth_all']) > 0 and abs(line_side['depth_all'][-1][2] - depth_add[2]) <= 0.01:
                            line_side['depth_all'][-1][1] = depth_add[1]
                        else:
                            line_side['depth_all'].append(depth_add)
                if 'depth_ext' in line_side and 'depth_ext' in line_cur:
                    for depth_one in line_side['depth_ext']:
                        depth_one[0] = depth_one[0] * width_old / width_new
                        depth_one[1] = depth_one[1] * width_old / width_new
                    for depth_one in line_cur['depth_ext']:
                        depth_add = depth_one.copy()
                        depth_add[0] = (depth_add[0] * width_add + width_old) / width_new
                        depth_add[1] = (depth_add[1] * width_add + width_old) / width_new
                        if len(line_side['depth_ext']) > 0 and abs(line_side['depth_ext'][-1][2] - depth_add[2]) <= 0.01:
                            line_side['depth_ext'][-1][1] = depth_add[1]
                        else:
                            line_side['depth_ext'].append(depth_add)
            else:
                line_side['p1'] = line_cur['p1'][:]
                line_side['p1_original'] = line_side['p1'][:]
                if 'depth_all' in line_side and 'depth_all' in line_cur:
                    for depth_one in line_side['depth_all']:
                        depth_one[0] = (depth_one[0] * width_old + width_add) / width_new
                        depth_one[1] = (depth_one[1] * width_old + width_add) / width_new
                    for depth_one in reversed(line_cur['depth_all']):
                        depth_add = depth_one.copy()
                        depth_add[0] = depth_add[0] * width_add / width_new
                        depth_add[1] = depth_add[1] * width_add / width_new
                        if len(line_side['depth_all']) > 0 and abs(line_side['depth_all'][0][2] - depth_add[2]) <= 0.01:
                            line_side['depth_all'][0][0] = depth_add[0]
                        else:
                            line_side['depth_all'].insert(0, depth_add)
                if 'depth_ext' in line_side and 'depth_ext' in line_cur:
                    for depth_one in line_side['depth_ext']:
                        depth_one[0] = (depth_one[0] * width_old + width_add) / width_new
                        depth_one[1] = (depth_one[1] * width_old + width_add) / width_new
                    for depth_one in reversed(line_cur['depth_ext']):
                        depth_add = depth_one.copy()
                        depth_add[0] = depth_add[0] * width_add / width_new
                        depth_add[1] = depth_add[1] * width_add / width_new
                        if len(line_side['depth_ext']) > 0 and abs(line_side['depth_ext'][0][2] - depth_add[2]) <= 0.01:
                            line_side['depth_ext'][0][0] = depth_add[0]
                        else:
                            line_side['depth_ext'].insert(0, depth_add)
            #
            line_side['width'] = width_new
            if 'width_original' not in line_side:
                line_side['width_original'] = line_side['width']
            if line_cur['type'] in [UNIT_TYPE_GROUP]:
                if width_add > width_old:
                    if line_side['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                        line_side['height'] = UNIT_HEIGHT_WALL
                    line_side['type'] = line_cur['type']
                    line_side['depth'] = max(line_cur['depth'], line_side['depth'])
                    line_side['unit_flag'] = line_cur['unit_flag']
                    line_side['unit_edge'] = line_cur['unit_edge']
                    line_side['unit_group'] = line_cur['unit_group']
            return -1, line_cur
        elif line_cur['type'] == line_side['type'] and not line_cur['type'] == UNIT_TYPE_GROUP:
            width_old = line_side['width']
            width_add = line_cur['width']
            width_new = width_old + width_add
            if side_order < 0:
                line_side['p2'] = line_cur['p2'][:]
                if line_side['type'] == UNIT_TYPE_WINDOW:
                    # depth_all
                    for depth_one in line_side['depth_all']:
                        depth_one[0] = depth_one[0] * width_old / width_new
                        depth_one[1] = depth_one[1] * width_old / width_new
                    for depth_one in line_cur['depth_all']:
                        depth_add = depth_one.copy()
                        depth_add[0] = (depth_add[0] * width_add + width_old) / width_new
                        depth_add[1] = (depth_add[1] * width_add + width_old) / width_new
                        line_side['depth_all'].append(depth_add)
                        if len(line_side['depth_all']) > 0 and abs(
                                line_side['depth_all'][-1][2] - depth_add[2]) <= 0.01:
                            line_side['depth_all'][-1][1] = depth_add[1]
                        else:
                            line_side['depth_all'].append(depth_add)
                    # depth_ext
                    for depth_one in line_side['depth_ext']:
                        depth_one[0] = depth_one[0] * width_old / width_new
                        depth_one[1] = depth_one[1] * width_old / width_new
                    for depth_one in line_cur['depth_ext']:
                        depth_add = depth_one.copy()
                        depth_add[0] = (depth_add[0] * width_add + width_old) / width_new
                        depth_add[1] = (depth_add[1] * width_add + width_old) / width_new
                        line_side['depth_ext'].append(depth_add)
                        if len(line_side['depth_ext']) > 0 and abs(
                                line_side['depth_ext'][-1][2] - depth_add[2]) <= 0.01:
                            line_side['depth_ext'][-1][1] = depth_add[1]
                        else:
                            line_side['depth_ext'].append(depth_add)
            else:
                line_side['p1'] = line_cur['p1'][:]
                if line_side['type'] == UNIT_TYPE_WINDOW:
                    # depth_all
                    for depth_one in line_side['depth_all']:
                        depth_one[0] = (depth_one[0] * width_old + width_add) / width_new
                        depth_one[1] = (depth_one[1] * width_old + width_add) / width_new
                    for depth_one in reversed(line_cur['depth_all']):
                        depth_add = depth_one.copy()
                        depth_add[0] = depth_add[0] * width_add / width_new
                        depth_add[1] = depth_add[1] * width_add / width_new
                        if len(line_side['depth_all']) > 0 and abs(line_side['depth_all'][0][2] - depth_add[2]) <= 0.01:
                            line_side['depth_all'][0][0] = depth_add[0]
                        else:
                            line_side['depth_all'].insert(0, depth_add)
                    # depth_ext
                    for depth_one in line_side['depth_ext']:
                        depth_one[0] = (depth_one[0] * width_old + width_add) / width_new
                        depth_one[1] = (depth_one[1] * width_old + width_add) / width_new
                    for depth_one in reversed(line_cur['depth_ext']):
                        depth_add = depth_one.copy()
                        depth_add[0] = depth_add[0] * width_add / width_new
                        depth_add[1] = depth_add[1] * width_add / width_new
                        if len(line_side['depth_ext']) > 0 and abs(
                                line_side['depth_ext'][0][2] - depth_add[2]) <= 0.01:
                            line_side['depth_ext'][0][0] = depth_add[0]
                        else:
                            line_side['depth_ext'].insert(0, depth_add)
            line_side['width'] = width_new
            # 进深融合
            return -1, line_cur
    return 0, line_cur


# 避让部件
def dodge_side_line(line_cur, line_side, side_order=-1, dodge_width=UNIT_WIDTH_DODGE, dodge_type=UNIT_TYPE_SIDE):
    # 当前
    x1, y1, x2, y2 = line_cur['p1'][0], line_cur['p1'][1], line_cur['p2'][0], line_cur['p2'][1]
    # 分裂
    separate = False
    # 退化
    line_width, side_width, side_room = line_cur['width'], line_side['width'], line_side['unit_to_type']
    if line_width <= dodge_width < 1.2 or (line_width <= dodge_width + 0.4 and dodge_width > UNIT_DEPTH_CURTAIN + 0.01):
        line_cur['type'] = dodge_type
        line_cur['depth'] = line_side['width']
        return -1, line_cur
    elif line_width <= UNIT_DEPTH_CURTAIN * 3 and dodge_width < UNIT_DEPTH_CURTAIN + 0.01 and side_room not in ['Balcony', 'Terrace']:
        line_cur['type'] = dodge_type
        line_cur['depth'] = line_side['width']
        return -1, line_cur
    # 分裂
    else:
        separate = True

    # 分裂
    if separate:
        type_cur = line_cur['type']
        if side_order < 0:
            ratio_new = dodge_width / line_cur['width']
            x_new = x1 + (x2 - x1) * ratio_new
            y_new = y1 + (y2 - y1) * ratio_new
            # 深度
            depth_all_old = line_cur['depth_all']
            depth_all_new = []
            for depth_one in depth_all_old:
                if depth_one[1] <= ratio_new:
                    continue
                elif depth_one[0] >= ratio_new:
                    r0 = (depth_one[0] - ratio_new) / (1 - ratio_new)
                    r1 = (depth_one[1] - ratio_new) / (1 - ratio_new)
                    depth_new = [r0, r1, depth_one[2]]
                    depth_all_new.append(depth_new)
                else:
                    r0 = 0
                    r1 = (depth_one[1] - ratio_new) / (1 - ratio_new)
                    depth_new = [r0, r1, depth_one[2]]
                    depth_all_new.append(depth_new)
            # 新建
            line_new = {
                'type': dodge_type,
                'score': 0,
                'width': dodge_width,
                'depth': 0,
                'depth_all': [],
                'depth_ext': [],
                'height': line_side['height'],
                'angle': line_cur['angle'],
                'p1': [x1, y1],
                'p2': [x_new, y_new],
                'score_pre': 0,
                'score_post': 0,
                'depth_pre': UNIT_DEPTH_ASIDE,
                'depth_post': UNIT_DEPTH_ASIDE,
                'depth_pre_more': UNIT_DEPTH_ASIDE,
                'depth_post_more': UNIT_DEPTH_ASIDE,
                'unit_index': 0,
                'unit_depth': 0,
                'unit_margin': 0,
                'unit_edge': 0,
                'unit_flag': 0,
                'unit_group': '',
                'unit_to_room': '',
                'unit_to_type': ''
            }
            # 原有
            line_cur['type'] = type_cur
            line_cur['p1'] = [x_new, y_new]
            line_cur['width'] -= dodge_width
            line_cur['depth_all'] = depth_all_new
            line_cur['depth_ext'] = depth_all_new
        else:
            ratio_new = 1 - dodge_width / line_cur['width']
            x_new = x1 + (x2 - x1) * ratio_new
            y_new = y1 + (y2 - y1) * ratio_new
            # 深度
            depth_all_old = line_cur['depth_all']
            depth_all_new = []
            for depth_one in depth_all_old:
                if depth_one[1] <= ratio_new:
                    r0 = depth_one[0] / ratio_new
                    r1 = depth_one[1] / ratio_new
                    depth_new = [r0, r1, depth_one[2]]
                    depth_all_new.append(depth_new)
                elif depth_one[0] >= ratio_new:
                    break
                else:
                    r0 = depth_one[0] / ratio_new
                    r1 = 1
                    depth_new = [r0, r1, depth_one[2]]
                    depth_all_new.append(depth_new)
            # 新建
            left_width = line_cur['width'] - dodge_width
            line_new = {
                'type': type_cur,
                'score': 0,
                'width': left_width,
                'depth': line_cur['depth'],
                'depth_all': depth_all_new,
                'depth_ext': depth_all_new,
                'height': line_cur['height'],
                'angle': line_cur['angle'],
                'p1': [x1, y1],
                'p2': [x_new, y_new],
                'score_pre': 0,
                'score_post': 0,
                'depth_pre': 0,
                'depth_post': 0,
                'depth_pre_more': 0,
                'depth_post_more': 0,
                'unit_index': 0,
                'unit_depth': 0,
                'unit_margin': 0,
                'unit_edge': 0,
                'unit_flag': 0,
                'unit_group': '',
                'unit_to_room': '',
                'unit_to_type': ''
            }
            # 原有
            line_cur['type'] = dodge_type
            line_cur['p1'] = [x_new, y_new]
            line_cur['width'] = dodge_width
            line_cur['depth'] = 0
            line_cur['depth_all'] = []
            line_cur['depth_ext'] = []
        return 1, line_new
    else:
        return 0, line_cur


# 检测部件
def check_side_line(line_idx, line_list, side_order=-1):
    # 当前 side_order=-1表示前段 side_order=1表示后段
    line_cur = line_list[line_idx]
    type_cur = line_cur['type']
    width_cur, depth_cur, height_cur = line_cur['width'], line_cur['depth'], line_cur['height']
    angle_cur = normalize_line_angle(line_cur['angle'])
    angle_inner = normalize_line_angle(angle_cur + math.pi / 2 * side_order)
    angle_outer = normalize_line_angle(angle_cur - math.pi / 2 * side_order)

    # 邻边
    side_idx = 1
    line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
    type_side = line_side['type']
    width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
    angle_side = normalize_line_angle(line_side['angle'])
    score_side = 0
    # 平行
    if abs(angle_cur - angle_side) < 0.1:
        # 分数
        score_side = 1
        if type_side in [UNIT_TYPE_GROUP]:
            unit_width, unit_depth = line_side['width'], line_side['depth']
            if unit_width < UNIT_DEPTH_BACK_MAX and unit_depth > UNIT_DEPTH_BACK_ERR:
                score_side = 4
        elif type_side in [UNIT_TYPE_WALL]:
            # 背景厚度
            back_depth_1, back_depth_2 = 0, 0
            if 'back_depth' in line_cur:
                back_depth_1 = line_cur['back_depth']
            if 'back_depth' in line_side:
                back_depth_2 = line_side['back_depth']
            if abs(back_depth_1 - back_depth_2) > 0.02:
                score_side = 4
        # 检测
        if abs(angle_cur - angle_side) < 0.1 and type_cur == type_side == UNIT_TYPE_GROUP:
            if abs(depth_cur - depth_side) < 0.1 or min(height_cur, height_side) > UNIT_HEIGHT_WALL - 0.01:
                side_idx += 1
                line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
                type_side = line_side['type']
                width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
                angle_side = normalize_line_angle(line_side['angle'])
                # 递进
                if abs(angle_cur - angle_side) < 0.1 and type_cur == type_side == UNIT_TYPE_GROUP:
                    if abs(depth_cur - depth_side) < 0.1 or min(height_cur, height_side) > UNIT_HEIGHT_WALL - 0.01:
                        side_idx += 1
                        line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
                        type_side = line_side['type']
                        width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
                        angle_side = normalize_line_angle(line_side['angle'])
                        # 递进
                        if abs(angle_cur - angle_side) < 0.1 and type_cur == type_side == UNIT_TYPE_GROUP:
                            if abs(depth_cur - depth_side) < 0.1 or min(height_cur, height_side) > UNIT_HEIGHT_WALL - 0.01:
                                side_idx += 1
                                line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
                                type_side = line_side['type']
                                width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
                                angle_side = normalize_line_angle(line_side['angle'])
        if abs(angle_cur - angle_side) < 0.1 and type_cur == UNIT_TYPE_GROUP and type_side not in [UNIT_TYPE_SIDE] \
                and width_side < width_cur:
            side_idx += 1
            line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
            type_side = line_side['type']
            width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
            angle_side = normalize_line_angle(line_side['angle'])
            # 递进
            if abs(angle_cur - angle_side) < 0.1 and type_cur == UNIT_TYPE_GROUP and type_side not in [UNIT_TYPE_SIDE] \
                    and width_side < width_cur:
                side_idx += 1
                line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
                type_side = line_side['type']
                width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
                angle_side = normalize_line_angle(line_side['angle'])
                # 递进
                if abs(angle_cur - angle_side) < 0.1 and type_cur == UNIT_TYPE_GROUP and type_side not in [UNIT_TYPE_SIDE]\
                        and width_side < width_cur:
                    side_idx += 1
                    line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
                    type_side = line_side['type']
                    width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
                    angle_side = normalize_line_angle(line_side['angle'])

        # 检测
        if type_cur in [UNIT_TYPE_GROUP] and height_cur > UNIT_HEIGHT_WALL - 0.01:
            type_cur = UNIT_TYPE_WINDOW
        if type_side in [UNIT_TYPE_GROUP] and height_side > UNIT_HEIGHT_WALL - 0.01:
            type_side = UNIT_TYPE_WINDOW
        if abs(angle_cur - angle_side) < 0.1 and type_cur in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and \
                type_side in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]:
            side_idx += 1
            line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
            type_side = line_side['type']
            width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
            angle_side = normalize_line_angle(line_side['angle'])
            # 递进
            if type_side in [UNIT_TYPE_GROUP] and height_side > UNIT_HEIGHT_WALL - 0.01:
                type_side = UNIT_TYPE_WINDOW
            if abs(angle_cur - angle_side) < 0.1 and type_cur in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and \
                    type_side in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]:
                side_idx += 1
                line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
                type_side = line_side['type']
                width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
                angle_side = normalize_line_angle(line_side['angle'])
                # 递进
                if type_side in [UNIT_TYPE_GROUP] and height_side > UNIT_HEIGHT_WALL - 0.01:
                    type_side = UNIT_TYPE_WINDOW
                if abs(angle_cur - angle_side) < 0.1 and type_cur in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and \
                        type_side in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]:
                    side_idx += 1
                    line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
                    type_side = line_side['type']
                    width_side, depth_side, height_side = line_side['width'], line_side['depth'], line_side['height']
                    angle_side = normalize_line_angle(line_side['angle'])
        # 窗帘
        if abs(angle_cur - angle_side) < 0.1 and \
                type_side in [UNIT_TYPE_SIDE, UNIT_TYPE_WALL] and width_side < UNIT_DEPTH_CURTAIN + 0.01:
            side_idx += 1
            line_side = line_list[(line_idx + side_order * side_idx + len(line_list)) % len(line_list)]
    # 阴角
    elif abs(angle_inner - angle_side) < 0.1 or abs(angle_inner - angle_side) < abs(angle_outer - angle_side):
        # 分数
        score_side = 4
        pass
    # 阳角
    elif abs(angle_outer - angle_side) < 0.1 or abs(angle_outer - angle_side) < abs(angle_inner - angle_side):
        score_side = 2
    # 斜角
    elif abs(angle_outer - angle_side) > 0.5 and abs(angle_inner - angle_side) > 0.5 and line_side['width'] < 0.5:
        score_side = 2

    # 索引
    line_idx_side = (line_idx + side_order * side_idx + len(line_list)) % len(line_list)
    # 邻边
    line_side = line_list[line_idx_side]
    type_side = line_side['type']
    depth_side, depth_more = line_side['depth'], 0
    angle_side = normalize_line_angle(line_side['angle'])
    # 平行
    if abs(angle_cur - angle_side) < 0.1:
        unit_width, unit_depth = line_side['width'], line_side['depth']
        if type_side in [UNIT_TYPE_WALL] or (type_side in [UNIT_TYPE_AISLE] and unit_depth > 3.0):
            if type_cur in [UNIT_TYPE_AISLE] and line_cur['depth'] > UNIT_DEPTH_ASIDE:
                unit_depth = line_cur['depth']
            elif type_cur in [UNIT_TYPE_GROUP] and line_cur['depth'] > UNIT_DEPTH_ASIDE:
                unit_depth = line_cur['depth']
            else:
                if unit_depth < UNIT_DEPTH_ASIDE:
                    unit_depth = UNIT_DEPTH_ASIDE
        elif type_side in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
            if unit_depth < UNIT_DEPTH_ASIDE:
                unit_depth = UNIT_DEPTH_ASIDE
        depth_side, depth_more = unit_depth, unit_depth
    # 阴角
    elif abs(angle_inner - angle_side) < 0.1 or abs(angle_inner - angle_side) < abs(angle_outer - angle_side):
        depth_side, depth_more, depth_limit = 0, 0, 0
        for side_idx in range(5):
            side_one = line_list[(line_idx_side + side_idx * side_order + len(line_list)) % len(line_list)]
            if side_idx == 0:
                if side_one['type'] in [UNIT_TYPE_DOOR]:
                    if side_one['width'] > UNIT_WIDTH_HOLE and 'width_original' in side_one:
                        depth_side += min(side_one['width'], UNIT_DEPTH_DODGE) * 0.5
                    break
                else:
                    depth_side += side_one['width']
            elif abs(side_one['angle'] - angle_side) < 0.01:
                if side_one['type'] in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                    depth_side += side_one['width']
                elif side_one['type'] in [UNIT_TYPE_GROUP] and side_one['unit_edge'] in [0, 2] \
                        and (line_cur['unit_edge'] in [1, 3] or line_cur['unit_group'] in ['Meeting', 'Bed'] or type_cur in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]):
                    if depth_limit <= 0:
                        depth_limit = side_one['width']
                    elif side_one['width'] > min(depth_limit, 1):
                        break
                    depth_side += side_one['width']
                elif side_one['type'] in [UNIT_TYPE_GROUP] and side_one['unit_edge'] in [1, 3] \
                        and type_cur in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                    if depth_limit <= 0:
                        depth_limit = side_one['width']
                    elif side_one['width'] > min(depth_limit, 1):
                        break
                    depth_side += side_one['width']
                elif side_one['type'] in [UNIT_TYPE_AISLE] and side_one['depth'] > 0.5 and type_cur in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                    if depth_limit <= 0:
                        depth_limit = side_one['width']
                        depth_side += side_one['width']
                    else:
                        break
                elif side_one['type'] in [UNIT_TYPE_AISLE] and side_one['depth'] > max(width_cur, 2):
                    if depth_limit <= 0:
                        depth_limit = side_one['width']
                        depth_side += side_one['width']
                    else:
                        break
                else:
                    break
            else:
                break
        for side_idx in range(5):
            side_one = line_list[(line_idx_side + side_idx * side_order + len(line_list)) % len(line_list)]
            if side_idx == 0:
                depth_more += side_one['width']
            elif abs(side_one['angle'] - angle_side) < 0.01:
                depth_more += side_one['width']
            else:
                break
    # 阳角
    elif abs(angle_outer - angle_side) < 0.1 or abs(angle_outer - angle_side) < abs(angle_inner - angle_side):
        depth_side, depth_more = UNIT_DEPTH_ASIDE, UNIT_DEPTH_ASIDE
    # 斜角
    elif abs(angle_outer - angle_side) > 0.5 and abs(angle_inner - angle_side) > 0.5 and line_side['width'] < 0.5:
        depth_side, depth_more = UNIT_DEPTH_ASIDE, UNIT_DEPTH_ASIDE
    else:
        depth_side, depth_more = UNIT_DEPTH_ASIDE, UNIT_DEPTH_ASIDE

    # 返回
    return score_side, depth_side, depth_more


# 计算角度
def calculate_line_angle(x1, y1, x2, y2):
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


# 规范角度
def normalize_line_angle(angle_old):
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


# 判断角度
def determine_line_angle(angle_old):
    angle_new = normalize_line_angle(angle_old)
    if abs(angle_new - math.pi * 0.5) < 0.05 or abs(angle_new + math.pi * 0.5) < 0.05:
        return 0
    elif abs(angle_new) < 0.05 or abs(angle_new - math.pi) < 0.05 or abs(angle_new + math.pi) < 0.05:
        return 1
    return -1


# 规范顺序
def normalize_unit_clock(unit_one):
    point_list = unit_one['pts']
    point_numb = len(point_list) // 2
    point_edge, point_flag = 0, True
    for i in range(point_numb - 1):
        point_edge += round(
            (point_list[2 * i + 2] - point_list[2 * i + 0]) * (point_list[2 * i + 3] + point_list[2 * i + 1]), 3)
    point_edge += round((point_list[0] - point_list[-2]) * (point_list[1] + point_list[-1]), 3)
    if point_edge >= 0:
        point_flag = True
    else:
        point_flag = False
    if not point_flag:
        unit_one['pts'] = []
        for i in range(point_numb - 1, -1, -1):
            unit_one['pts'].append(point_list[2 * i + 0])
            unit_one['pts'].append(point_list[2 * i + 1])


# 功能测试
if __name__ == '__main__':
    pass
