# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-09-28
@Description: 全屋硬装处理

"""

from LayoutByRule.house_calculator import *

ROOM_TYPE_LEVEL_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library']
ROOM_TYPE_LEVEL_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
ROOM_TYPE_LEVEL_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom', 'Kitchen',
                     'Balcony', 'Terrace', 'Lounge', 'Auditorium',
                     'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                     'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom']
ROOM_TYPE_LEVEL_4 = ['Hallway', 'Aisle', 'Corridor', 'Stairwell',
                     'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom']


# 房间硬装：墙面 地面 屋顶 门窗
def room_decorate(line_list, room_info, room_type='', room_area=10, room_height=UNIT_HEIGHT_WALL):
    # 墙面
    wall_info = room_wall()
    # 地面
    floor_info = room_floor()
    # 顶面
    ceiling_info = room_ceiling(line_list, room_type, room_area)
    # 门 洞
    door_info = room_door(line_list, room_info, room_type, room_area)
    # 窗 窗帘
    window_info = room_window(line_list, room_info, room_type, room_area, room_height)
    # 返回
    decorate_info = {
        'Wall': wall_info,
        'Floor': floor_info,
        'Ceiling': ceiling_info,
        'Door': door_info,
        'Window': window_info
    }
    return decorate_info


def room_wall():
    deco_info = {
        'type': 'Wall',
        'info_list': []
    }
    return deco_info


def room_floor():
    deco_info = {
        'type': 'Floor',
        'baseboard_list': []
    }
    return deco_info


def room_ceiling(line_list, room_type='', room_area=10):
    deco_info = {
        'type': 'Ceiling',
        'cornice_list': [],
        'light_list': []
    }
    # 返回
    return deco_info


def room_door(line_list, room_info, room_type='', room_area=10):
    deco_info = {
        'type': 'Door',
        'door_list': []
    }
    # 门洞位置
    unit_list = []
    if 'door_info' in room_info:
        for unit_one in room_info['door_info']:
            unit_list.append(unit_one)
    if 'hole_info' in room_info:
        for unit_one in room_info['hole_info']:
            unit_list.append(unit_one)
    for unit_one in unit_list:
        if room_area <= 1.5:
            break
        unit_pts, unit_pos, unit_ang = unit_one['pts'], [], 0
        # 尺寸
        unit_width, unit_depth = UNIT_WIDTH_DOOR, UNIT_DEPTH_WALL_INSIDE
        unit_height, unit_bottom = UNIT_HEIGHT_DOOR_TOP, 0
        if len(unit_pts) >= 8:
            unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                        (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
            dis_1, ang_1 = compute_dis_ang(unit_pts[0], unit_pts[1], unit_pts[2], unit_pts[3])
            dis_2, ang_2 = compute_dis_ang(unit_pts[2], unit_pts[3], unit_pts[4], unit_pts[5])
            if dis_1 > dis_2:
                unit_width, unit_depth, unit_ang = dis_1, dis_2, ang_2
            else:
                unit_width, unit_depth, unit_ang = dis_2, dis_1, ang_1
        elif len(unit_pts) >= 2:
            unit_pos = [unit_pts[0], unit_pts[1]]
        else:
            continue
        if unit_width < 0.6:
            continue
        # 方向
        line_idx_best, line_one_best = -1, {}
        line_dis_x, line_dis_y = 100, 100
        for line_idx, line_one in enumerate(line_list):
            if line_one['type'] not in [UNIT_TYPE_DOOR]:
                continue
            p1, p2, ang = line_one['p1'], line_one['p2'], line_one['angle']
            p0 = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
            if abs(p0[0] - unit_pos[0]) + abs(p0[1] - unit_pos[1]) < line_dis_x + line_dis_y:
                line_idx_best, line_one_best = line_idx, line_one
                line_dis_x, line_dis_y = abs(p0[0] - unit_pos[0]), abs(p0[1] - unit_pos[1])
        if len(line_one_best) <= 0:
            continue
        unit_dir = 1
        index_side1 = (line_idx_best - 1 + len(line_list)) % len(line_list)
        index_side2 = (line_idx_best + 1 + len(line_list)) % len(line_list)
        line_side1 = line_list[index_side1]
        line_side2 = line_list[index_side2]
        if line_one_best['score_pre'] == 4 > line_one_best['score_post']:
            unit_dir = 1
            if line_side1['type'] in [UNIT_TYPE_DOOR] and line_side1['width'] > 0.5:
                unit_dir = -1
        elif line_one_best['score_post'] == 4 > line_one_best['score_pre']:
            unit_dir = -1
            if line_side2['type'] in [UNIT_TYPE_DOOR] and line_side2['width'] > 0.5:
                unit_dir = 1
        elif line_one_best['score_post'] == 1 == line_one_best['score_pre']:
            if line_side1['width'] > line_side2['width'] > 1.5:
                unit_dir = -1
            elif line_side2['width'] > line_side1['width'] > 1.5:
                unit_dir = 1
            elif line_side1['width'] > line_side2['width'] > 0.5:
                unit_dir = 1
            elif line_side2['width'] > line_side1['width'] > 0.5:
                unit_dir = -1
            elif 1.0 > line_side1['width'] > 0.5 > line_side2['width'] and 'Bathroom' in room_type:
                unit_dir = -1
            elif 1.0 > line_side2['width'] > 0.5 > line_side1['width'] and 'Bathroom' in room_type:
                unit_dir = 1
            else:
                unit_dir = 1
        elif line_one_best['score_post'] == 4 == line_one_best['score_pre']:
            if line_side2['width'] > line_side1['width']:
                unit_dir = -1
        # 角度
        unit_angle_line = line_one_best['angle']
        if min(line_dis_x, line_dis_y) > 0.5:
            unit_dir = 0
            unit_angle_line = unit_ang
        unit_angle_close = normalize_line_angle(unit_angle_line - math.pi * 0.5 * unit_dir)
        unit_angle_open1 = normalize_line_angle(unit_angle_line + math.pi)
        unit_angle_open2 = normalize_line_angle(unit_angle_line + 0)
        # 轴心
        x_o, y_o = line_one_best['p1'][0], line_one_best['p1'][1]
        if unit_dir <= -1:
            x_o, y_o = line_one_best['p2'][0], line_one_best['p2'][1]
        edge_len, edge_idx, edge_min = int(len(unit_pts) / 2), -1, 100
        for j in range(edge_len):
            x_p = unit_pts[(2 * j + 0) % len(unit_pts)]
            y_p = unit_pts[(2 * j + 1) % len(unit_pts)]
            edge_now = abs(x_p - x_o) + abs(y_p - y_o)
            if edge_now < edge_min:
                edge_idx = j
                edge_min = edge_now
        x_p = unit_pts[(2 * edge_idx + 0) % len(unit_pts)]
        y_p = unit_pts[(2 * edge_idx + 1) % len(unit_pts)]
        open_ang = normalize_line_angle(unit_angle_line - math.pi * 0.5)
        x_p_1 = x_p + unit_depth * math.sin(open_ang)
        y_p_1 = y_p + unit_depth * math.cos(open_ang)
        x_p_2 = x_p
        y_p_2 = y_p
        # 中心
        unit_center_close, unit_center_open1, unit_center_open2 = unit_pos[:], unit_pos[:], unit_pos[:]
        # 外开
        dis_1, ang_1 = compute_dis_ang(x_p_1, y_p_1, unit_pos[0], unit_pos[1])
        ang_1_dlt = ang_1 - unit_angle_line
        if unit_dir <= -1:
            ang_1_dlt = ang_1 - unit_angle_line - math.pi
        ang_new = normalize_line_angle(unit_angle_line - math.pi / 2 + ang_1_dlt)
        unit_center_open1 = [x_p_1 + dis_1 * math.sin(ang_new), y_p_1 + dis_1 * math.cos(ang_new)]
        # 内开
        dis_2, ang_2 = compute_dis_ang(x_p_2, y_p_2, unit_pos[0], unit_pos[1])
        ang_2_dlt = ang_2 - unit_angle_line
        if unit_dir <= -1:
            ang_2_dlt = ang_2 - unit_angle_line - math.pi
        ang_new = normalize_line_angle(unit_angle_line + math.pi / 2 + ang_2_dlt)
        unit_center_open2 = [x_p_2 + dis_2 * math.sin(ang_new), y_p_2 + dis_2 * math.cos(ang_new)]
        # 通向
        unit_to_room, unit_to_type = '', ''
        if 'unit_to_room' in line_one_best:
            unit_to_room = line_one_best['unit_to_room']
        if 'unit_to_type' in line_one_best:
            unit_to_type = line_one_best['unit_to_type']
        # 矩形
        rect_one = {
            'type': UNIT_TYPE_DOOR,
            'width': unit_width,
            'depth': unit_depth,
            'height': unit_height,
            'bottom': unit_bottom,
            'angle': unit_angle_close,
            'center': unit_center_close,
            'angle_open1': unit_angle_open1,
            'center_open1': unit_center_open1,
            'angle_open2': unit_angle_open2,
            'center_open2': unit_center_open2,
            'unit_to_room': unit_to_room,
            'unit_to_type': unit_to_type
        }
        deco_info['door_list'].append(rect_one)
    # 返回
    return deco_info


def room_window(line_list, room_info, room_type='', room_area=10, room_height=UNIT_HEIGHT_WALL):
    deco_info = {
        'type': 'Window',
        'window_list': [],
        'curtain_list': []
    }
    window_list, curtain_list = [], []
    # 窗户位置
    unit_list = []
    if 'window_info' in room_info:
        for unit_one in room_info['window_info']:
            unit_list.append(unit_one)
    if 'baywindow_info' in room_info:
        for unit_one in room_info['baywindow_info']:
            unit_list.append(unit_one)
    for unit_one in unit_list:
        unit_pts, unit_pos = unit_one['pts'], []
        # 尺寸
        unit_width, unit_depth = UNIT_WIDTH_DOOR, UNIT_DEPTH_WALL_INSIDE
        unit_height, unit_bottom = UNIT_HEIGHT_WINDOW_TOP, 0
        if len(unit_pts) >= 8:
            unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                        (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
            dis_1, ang_1 = compute_dis_ang(unit_pts[0], unit_pts[1], unit_pts[2], unit_pts[3])
            dis_2, ang_2 = compute_dis_ang(unit_pts[2], unit_pts[3], unit_pts[4], unit_pts[5])
            if dis_1 > dis_2:
                unit_width, unit_depth = dis_1, dis_2
            else:
                unit_width, unit_depth = dis_2, dis_1
        elif len(unit_pts) >= 2:
            unit_pos = [unit_pts[0], unit_pts[1]]
        else:
            continue
        if unit_width < 0.4:
            continue
        # 方向
        line_dis_min, line_idx_best, line_one_best = 100, -1, {}
        line_dlt_min_x, line_dlt_min_y = 0, 0
        for line_idx, line_one in enumerate(line_list):
            if line_one['type'] not in [UNIT_TYPE_WINDOW]:
                continue
            p1, p2, ang = line_one['p1'], line_one['p2'], line_one['angle']
            p0 = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
            line_dis_new = abs(p0[0] - unit_pos[0]) + abs(p0[1] - unit_pos[1])
            if line_dis_new < line_dis_min:
                line_dis_min, line_idx_best, line_one_best = line_dis_new, line_idx, line_one
                line_dlt_min_x, line_dlt_min_y = abs(p0[0] - unit_pos[0]), abs(p0[0] - unit_pos[0])
        if len(line_one_best) <= 0:
            continue
        if min(line_dlt_min_x, line_dlt_min_y) >= 0.5:
            continue
        unit_height, unit_bottom = UNIT_HEIGHT_WINDOW_TOP - line_one_best['height'], line_one_best['height']
        unit_dir = 1
        if line_one_best['score_pre'] == 4 > line_one_best['score_post']:
            unit_dir = 1
        elif line_one_best['score_post'] == 4 > line_one_best['score_pre']:
            unit_dir = -1
        elif line_one_best['score_pre'] == 2 > line_one_best['score_post']:
            unit_dir = -1
        elif line_one_best['score_post'] == 2 > line_one_best['score_pre']:
            unit_dir = 1
        elif line_one_best['score_post'] == 1 == line_one_best['score_pre']:
            index_side1 = (line_idx_best - 1 + len(line_list)) % len(line_list)
            index_side2 = (line_idx_best + 1 + len(line_list)) % len(line_list)
            line_side1 = line_list[index_side1]
            line_side2 = line_list[index_side2]
            if line_side1['width'] < line_side2['width']:
                unit_dir = 1
            else:
                unit_dir = -1
        # 宽度
        if line_one_best['width'] < unit_width * 0.5:
            continue
        # 角度
        unit_angle_line = line_one_best['angle']
        unit_angle_close = normalize_line_angle(unit_angle_line - math.pi * 0.5 * unit_dir)
        # 中心
        unit_center_close = unit_pos[:]
        # 通向
        unit_to_room, unit_to_type = '', ''
        if 'unit_to_room' in line_one_best:
            unit_to_room = line_one_best['unit_to_room']
        if 'unit_to_type' in line_one_best:
            unit_to_type = line_one_best['unit_to_type']
        # 矩形
        rect_one = {
            'type': UNIT_TYPE_WINDOW,
            'width': unit_width,
            'depth': unit_depth,
            'height': unit_height,
            'bottom': unit_bottom,
            'angle': unit_angle_close,
            'center': unit_center_close,
            'unit_to_room': unit_to_room,
            'unit_to_type': unit_to_type
        }
        window_list.append(rect_one)

    # 窗帘位置
    curtain_side = {}
    for line_idx, line_one in enumerate(line_list):
        line_type = line_one['type']
        if line_type not in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
            continue
        if line_idx in curtain_side:
            continue
        unit_to_room, unit_to_type = '', ''
        if 'unit_to_room' in line_one:
            unit_to_room = line_one['unit_to_room']
        if 'unit_to_type' in line_one:
            unit_to_type = line_one['unit_to_type']
        if len(unit_to_type) <= 0 and len(unit_to_room) > 0:
            unit_to_type = unit_to_room.split('-')[0]
        if line_type in [UNIT_TYPE_DOOR]:
            if line_one['width'] < UNIT_WIDTH_CURTAIN * 3:
                continue
            elif unit_to_room == '':
                continue
            elif room_type in ROOM_TYPE_LEVEL_3:
                continue
            elif room_type in ROOM_TYPE_LEVEL_1 and unit_to_type in ['Library']:
                continue
            elif room_type in ROOM_TYPE_LEVEL_1 and unit_to_type in ROOM_TYPE_LEVEL_2:
                if line_one['width'] < 3:
                    continue
            elif room_type in ROOM_TYPE_LEVEL_1 and unit_to_type not in ['Balcony', 'Terrace']:
                if line_one['width'] > UNIT_WIDTH_HOLE and unit_to_type in ['OtherRoom']:
                    pass
                else:
                    continue
            elif room_type in ROOM_TYPE_LEVEL_2 and unit_to_type not in ['Balcony', 'Terrace']:
                if line_one['width'] > UNIT_WIDTH_HOLE and unit_to_type in ['OtherRoom']:
                    pass
                else:
                    continue
            elif room_type in ROOM_TYPE_LEVEL_3 and unit_to_type not in ['Balcony', 'Terrace']:
                continue
        elif line_type in [UNIT_TYPE_WINDOW]:
            if line_one['height'] < 0.5 and room_type in ROOM_TYPE_LEVEL_4:
                continue
            elif line_one['height'] < 0.5 and room_type in ROOM_TYPE_LEVEL_2 and len(unit_to_room) > 0:
                continue
            elif line_one['width'] < 3.0 and unit_to_type in ['Library', 'Kitchen']:
                continue
        # 窗户朝向
        room_to = unit_to_type
        if len(room_to) > 0:
            # 不装窗帘
            if room_type in ROOM_TYPE_LEVEL_1:
                if room_to in ['Balcony', 'Terrace', 'EquipmentRoom']:
                    pass
                elif room_to in ['Kitchen', 'Bathroom', 'MasterBathroom', 'SecondBathroom']:
                    continue
                elif line_one['width'] > UNIT_WIDTH_CURTAIN * 6:
                    pass
                else:
                    continue
            elif room_type in ROOM_TYPE_LEVEL_3:
                continue
            elif room_to in ['Kitchen', 'Bathroom', 'MasterBathroom', 'SecondBathroom']:
                continue
        # 部件高度
        unit_bottom = line_one['height']
        if line_type == UNIT_TYPE_DOOR:
            unit_bottom = 0
        elif line_type == UNIT_TYPE_WINDOW and unit_bottom > UNIT_HEIGHT_WINDOW_TOP / 2:
            unit_bottom = 0
        unit_height = room_height - unit_bottom
        # 部件厚度
        unit_depth = UNIT_DEPTH_WALL_OUTSIDE
        if room_to not in ['', 'Balcony', 'Terrace']:
            unit_depth = UNIT_DEPTH_WALL_INSIDE
        if 'unit_depth' in line_one:
            unit_depth = line_one['unit_depth']

        # 两侧信息
        line_idx_side1 = (line_idx - 1 + len(line_list)) % len(line_list)
        line_idx_side2 = (line_idx + 1 + len(line_list)) % len(line_list)
        line_side1, line_side2 = line_list[line_idx_side1], line_list[line_idx_side2]
        type_side1, type_side2 = line_side1['type'], line_side2['type']
        width_side1, width_side2 = line_side1['width'], line_side2['width']
        angle_side1, angle_side2 = line_side1['angle'], line_side2['angle']
        # 两侧信息 修正
        line_idx_side11 = (line_idx - 2 + len(line_list)) % len(line_list)
        line_idx_side22 = (line_idx + 2 + len(line_list)) % len(line_list)
        line_side11, line_side22 = line_list[line_idx_side11], line_list[line_idx_side22]
        type_side11, type_side22 = line_side11['type'], line_side22['type']
        width_side11, width_side22 = line_side11['width'], line_side22['width']
        angle_side11, angle_side22 = line_side11['angle'], line_side22['angle']
        if abs(angle_side1 - angle_side11) <= 0.1 and type_side11 in [UNIT_TYPE_WINDOW]:
            width_side1 = line_side1['width'] / 2
        if abs(angle_side2 - angle_side22) <= 0.1 and type_side22 in [UNIT_TYPE_WINDOW]:
            width_side2 = line_side2['width'] / 2
        # 两侧扩展
        extend_side1, extend_side2, extend_width1, extend_width2 = 0, 0, 0, 0
        expand_width1, expand_width2 = 0, 0
        # 部件宽度
        line_width, line_angle, p1, p2 = line_one['width'], line_one['angle'], line_one['p1'][:], line_one['p2'][:]
        line_width_original, p1_original, p2_original = line_width, p1[:], p2[:]
        if line_width <= 0.75:
            if abs(ang_to_ang(line_angle - angle_side1 - math.pi / 2)) <= 0.1:
                if type_side1 in [UNIT_TYPE_WINDOW] and width_side1 > 2 * line_width:
                    continue
            if abs(ang_to_ang(line_angle - angle_side1)) <= 0.1:
                if type_side1 in [UNIT_TYPE_SIDE] and width_side1 < UNIT_DEPTH_CURTAIN + 0.01:
                    continue
            if abs(ang_to_ang(line_angle - angle_side2 + math.pi / 2)) <= 0.1:
                if type_side2 in [UNIT_TYPE_WINDOW] and width_side2 > 2 * line_width:
                    continue
            if abs(ang_to_ang(line_angle - angle_side2)) <= 0.1:
                if type_side2 in [UNIT_TYPE_SIDE] and width_side2 < UNIT_DEPTH_CURTAIN + 0.01:
                    continue
        if 'width_original' in line_one:
            line_width_original = line_one['width_original']
            line_width_delta = line_width - line_width_original
            width_delta_1, width_delta_2 = 0, 0
            if 'p1_original' in line_one and 'p2_original' in line_one:
                p1_original = line_one['p1_original']
                p2_original = line_one['p2_original']
                width_delta_1, angle_delta_1 = compute_dis_ang(p1[0], p1[1], p1_original[0], p1_original[1])
                width_delta_2, angle_delta_2 = compute_dis_ang(p2[0], p2[1], p2_original[0], p2_original[1])
            elif 'p1_original' in line_one and 'p2_original' not in line_one:
                p1_original = line_one['p1_original'][:]
                width_delta_1, angle_delta_1 = compute_dis_ang(p1[0], p1[1], p1_original[0], p1_original[1])
            elif 'p1_original' not in line_one and 'p2_original' in line_one:
                p2_original = line_one['p2_original'][:]
                width_delta_2, angle_delta_2 = compute_dis_ang(p2[0], p2[1], p2_original[0], p2_original[1])
            # 后序扩张
            if width_delta_1 > max(width_delta_2 + 0.1, width_delta_2 * 2.0) or width_delta_1 > 0.01 > width_delta_2:
                line_width_delta = width_delta_1 - width_delta_2
                # 对称扩张
                if abs(line_angle - angle_side2) <= 0.1 and type_side2 in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE, UNIT_TYPE_SIDE]:
                    if width_side2 >= line_width_delta * 2:
                        if width_side2 < min(line_width * 0.8, 1.5) and width_delta_1 < 0.5:
                            line_width_delta = width_side2
                        ratio = line_width_delta / line_width
                        p2_new = [p1[0] + (1 + ratio) * (p2[0] - p1[0]), p1[1] + (1 + ratio) * (p2[1] - p1[1])]
                        line_width, p2 = line_width + line_width_delta, p2_new[:]
                    elif width_side2 >= line_width_delta * 1:
                        ratio = width_side2 / line_width
                        p2_new = [p1[0] + (1 + ratio) * (p2[0] - p1[0]), p1[1] + (1 + ratio) * (p2[1] - p1[1])]
                        line_width, p2 = line_width + width_side2, p2_new[:]
                    else:
                        ratio = width_side2 / line_width
                        p2_new = [p1[0] + (1 + ratio) * (p2[0] - p1[0]), p1[1] + (1 + ratio) * (p2[1] - p1[1])]
                        line_width, p2 = line_width + width_side2, p2_new[:]
                elif abs(line_angle - angle_side2) <= 0.1 and type_side2 in [UNIT_TYPE_DOOR] and line_width_original > width_side2:
                    ratio = width_side2 / line_width
                    p2_new = [p1[0] + (1 + ratio) * (p2[0] - p1[0]), p1[1] + (1 + ratio) * (p2[1] - p1[1])]
                    line_width, p2 = line_width + width_side2, p2_new[:]
                    if abs(line_angle - angle_side22) <= 0.1 and type_side22 in [UNIT_TYPE_WALL, UNIT_TYPE_SIDE]:
                        if width_side22 >= line_width_delta * 2:
                            ratio = line_width_delta / line_width
                            p2_new = [p1[0] + (1 + ratio) * (p2[0] - p1[0]), p1[1] + (1 + ratio) * (p2[1] - p1[1])]
                            line_width, p2 = line_width + line_width_delta, p2_new[:]
                        elif width_side22 >= line_width_delta * 1:
                            ratio = width_side22 / line_width
                            p2_new = [p1[0] + (1 + ratio) * (p2[0] - p1[0]), p1[1] + (1 + ratio) * (p2[1] - p1[1])]
                            line_width, p2 = line_width + width_side22, p2_new[:]
                        else:
                            ratio = width_side22 / line_width
                            p2_new = [p1[0] + (1 + ratio) * (p2[0] - p1[0]), p1[1] + (1 + ratio) * (p2[1] - p1[1])]
                            line_width, p2 = line_width + width_side22, p2_new[:]
                # 对称收缩
                else:
                    if width_delta_1 > max(width_delta_2 + 1.5, width_delta_2 * 2.0):
                        ratio = (width_delta_1 - width_delta_2) / line_width
                        p1_new = [p1[0] + ratio * (p2[0] - p1[0]), p1[1] + ratio * (p2[1] - p1[1])]
                        line_width, p1 = line_width_original + width_delta_2 * 2.0, p1_new[:]
            # 前序扩张
            elif width_delta_2 > max(width_delta_1 + 0.1, width_delta_1 * 2.0) or width_delta_2 > 0.01 > width_delta_1:
                line_width_delta = width_delta_2 - width_delta_1
                # 对称扩张
                if abs(line_angle - angle_side1) <= 0.1 and type_side1 in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE, UNIT_TYPE_SIDE]:
                    if width_side1 >= line_width_delta * 2:
                        if width_side1 < min(line_width * 0.8, 1.5) and width_delta_2 < 0.5:
                            line_width_delta = width_side1
                        ratio = line_width_delta / line_width
                        p1_new = [p2[0] + (1 + ratio) * (p1[0] - p2[0]), p2[1] + (1 + ratio) * (p1[1] - p2[1])]
                        line_width, p1 = line_width + line_width_delta, p1_new[:]
                    elif width_side1 >= line_width_delta:
                        ratio = width_side1 / line_width
                        p1_new = [p2[0] + (1 + ratio) * (p1[0] - p2[0]), p2[1] + (1 + ratio) * (p1[1] - p2[1])]
                        line_width, p1 = line_width + width_side1, p1_new[:]
                    else:
                        ratio = width_side1 / line_width
                        p1_new = [p2[0] + (1 + ratio) * (p1[0] - p2[0]), p2[1] + (1 + ratio) * (p1[1] - p2[1])]
                        line_width, p1 = line_width + width_side1, p1_new[:]
                elif abs(line_angle - angle_side1) <= 0.1 and type_side1 in [UNIT_TYPE_DOOR] and line_width_original > width_side1:
                    ratio = width_side1 / line_width
                    p1_new = [p2[0] + (1 + ratio) * (p1[0] - p2[0]), p2[1] + (1 + ratio) * (p1[1] - p2[1])]
                    line_width, p1 = line_width + width_side1, p1_new[:]
                    if abs(line_angle - angle_side11) <= 0.1 and type_side11 in [UNIT_TYPE_WALL, UNIT_TYPE_SIDE]:
                        if width_side11 >= line_width_delta * 2:
                            ratio = line_width_delta / line_width
                            p1_new = [p2[0] + (1 + ratio) * (p1[0] - p2[0]), p2[1] + (1 + ratio) * (p1[1] - p2[1])]
                            line_width, p1 = line_width + line_width_delta, p1_new[:]
                        elif width_side11 >= line_width_delta:
                            ratio = width_side11 / line_width
                            p1_new = [p2[0] + (1 + ratio) * (p1[0] - p2[0]), p2[1] + (1 + ratio) * (p1[1] - p2[1])]
                            line_width, p1 = line_width + width_side11, p1_new[:]
                        else:
                            ratio = width_side11 / line_width
                            p1_new = [p2[0] + (1 + ratio) * (p1[0] - p2[0]), p2[1] + (1 + ratio) * (p1[1] - p2[1])]
                            line_width, p1 = line_width + width_side11, p1_new[:]
                # 对称收缩
                else:
                    if width_delta_2 > max(width_delta_1 + 1.5, width_delta_1 * 2.0):
                        ratio = 1 - (width_delta_2 - width_delta_1) / line_width
                        p2_new = [p1[0] + ratio * (p2[0] - p1[0]), p1[1] + ratio * (p2[1] - p1[1])]
                        line_width, p2 = line_width_original + width_delta_1 * 2.0, p2_new[:]
        else:
            width_rest = UNIT_WIDTH_CURTAIN_SIDE
            if 'Bath' in room_type:
                width_rest = UNIT_WIDTH_CURTAIN_SIDE * 1.0
            elif unit_height <= 0.5:
                width_rest = UNIT_WIDTH_CURTAIN_SIDE * 3.0
            elif line_type == UNIT_TYPE_DOOR or line_width > 4 * UNIT_WIDTH_CURTAIN:
                width_rest = UNIT_WIDTH_CURTAIN_SIDE * 6.0
            elif room_to in ['Balcony', 'Terrace']:
                width_rest = UNIT_WIDTH_CURTAIN_SIDE * 6.0
            if abs(line_angle - angle_side1) <= 0.1 and type_side1 in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE]:
                extend_side1 = 1
                if width_side1 <= width_rest:
                    extend_width1 = width_side1
                elif line_width > UNIT_WIDTH_CURTAIN * 2:
                    extend_width1 = width_rest
            if abs(line_angle - angle_side2) <= 0.1 and type_side2 in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE]:
                extend_side2 = 1
                if width_side2 <= width_rest:
                    extend_width2 = width_side2
                elif line_width > UNIT_WIDTH_CURTAIN * 2:
                    extend_width2 = width_rest
            # 保持对称
            if extend_side1 >= 1 or extend_side2 >= 1:
                if width_side1 > extend_width2 + 0.5 and extend_width1 >= min(line_width_original, 2):
                    extend_width1 = extend_width2
                if width_side2 > extend_width1 + 0.5 and extend_width2 >= min(line_width_original, 2):
                    extend_width2 = extend_width1
                # 右侧扩展
                if extend_side1 >= 1:
                    ratio = extend_width1 / line_side1['width']
                    x1, y1, x2, y2 = line_side1['p2'][0], line_side1['p2'][1], line_side1['p1'][0], line_side1['p1'][1]
                    p1[0], p1[1] = x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio
                    expand_width1 = width_side1 - extend_width1
                # 左侧扩展
                if extend_side2 >= 1:
                    ratio = extend_width2 / line_side2['width']
                    x1, y1, x2, y2 = line_side2['p1'][0], line_side2['p1'][1], line_side2['p2'][0], line_side2['p2'][1]
                    p2[0], p2[1] = x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio
                    expand_width2 = width_side2 - extend_width2
            line_width = line_width + extend_width1 + extend_width2

        # 递进扩展
        extent_more, extent_side = False, min(line_width, 1.5)
        if abs(line_angle - angle_side11) <= 0.1 and abs(line_angle - angle_side22) <= 0.1 \
                and width_side11 < extent_side and width_side22 < extent_side \
                and abs(ang_to_ang(angle_side1 - line_angle + math.pi / 2)) < math.pi / 2 \
                and abs(ang_to_ang(angle_side2 - line_angle - math.pi / 2)) < math.pi / 2 \
                and room_to in ['', 'Balcony', 'Terrace']:
            extent_more = True
        elif abs(angle_side1 - angle_side11) <= 0.1 and abs(angle_side2 - angle_side22) <= 0.1 \
                and width_side1 + width_side11 < extent_side and width_side2 + width_side22 < extent_side \
                and abs(ang_to_ang(angle_side1 - line_angle + math.pi / 2)) < math.pi / 2 \
                and abs(ang_to_ang(angle_side2 - line_angle - math.pi / 2)) < math.pi / 2 \
                and room_to in ['', 'Balcony', 'Terrace']:
            if line_side11['score_pre'] == 1 and not line_side22['score_post'] == 1:
                pass
            elif line_side22['score_post'] == 1 and not line_side11['score_pre'] == 1:
                pass
            elif line_side11['score_pre'] == 1 and line_side11['score_post'] in [1, 4] and width_side11 >= 0.25:
                pass
            elif line_side22['score_pre'] in [1, 4] and line_side22['score_post'] == 1 and width_side22 >= 0.25:
                pass
            elif max(line_side11['width'], line_side22['width']) * line_width >= min(room_area * 0.5, room_area - 2.0):
                pass
            else:
                extent_more = True
        if extent_more:
            p1_side11, p2_side22 = line_side11['p1'], line_side22['p2']
            dis_new, ang_new = compute_dis_ang(p1_side11[0], p1_side11[1], p2_side22[0], p2_side22[1])
            tmp_x, tmp_z = dis_new * math.cos(ang_new - line_angle), dis_new * math.sin(ang_new - line_angle)
            if abs(tmp_z) <= 0.05:
                p1, p2 = p1_side11[:], p2_side22[:]
                # 递进扩展
                line_idx_side111 = (line_idx - 3 + len(line_list)) % len(line_list)
                line_idx_side222 = (line_idx + 3 + len(line_list)) % len(line_list)
                line_side111, line_side222 = line_list[line_idx_side111], line_list[line_idx_side222]
                type_side111, type_side222 = line_side111['type'], line_side222['type']
                width_side111, width_side222 = line_side111['width'], line_side222['width']
                angle_side111, angle_side222 = line_side111['angle'], line_side222['angle']
                p1_new, p2_new = p1_side11[:], p2_side22[:]
                if abs(angle_side111 - angle_side11) <= 0.1 and width_side111 + width_side11 < line_width \
                        and type_side111 in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
                    p1_new = line_side111['p1'][:]
                elif abs(angle_side111 - line_angle) <= 0.1 and width_side111 < extent_side \
                        and type_side111 in [UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
                    if width_side11 < 1.5 and abs(ang_to_ang(angle_side11 - line_angle + math.pi / 2)) < math.pi / 2:
                        p1_new = line_side111['p1'][:]
                if abs(angle_side222 - angle_side22) <= 0.1 and width_side222 + width_side22 < line_width \
                        and type_side222 in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE]:
                    p2_new = line_side222['p2'][:]
                elif abs(angle_side222 - line_angle) <= 0.1 and width_side222 < extent_side \
                        and type_side222 in [UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
                    if width_side22 < 1.5 and abs(ang_to_ang(angle_side22 - line_angle - math.pi / 2)) < math.pi / 2:
                        p2_new = line_side222['p2'][:]
                dis_new, ang_new = compute_dis_ang(p1_new[0], p1_new[1], p2_new[0], p2_new[1])
                tmp_x, tmp_z = dis_new * math.cos(ang_new - line_angle), dis_new * math.sin(ang_new - line_angle)
                if abs(tmp_z) <= 0.05:
                    p1, p2 = p1_new, p2_new
                dis_new, ang_new = compute_dis_ang(p1[0], p1[1], p2[0], p2[1])
                line_width = dis_new
                line_width_original = dis_new
                curtain_side[line_idx_side1] = 1
                curtain_side[line_idx_side2] = 1
                curtain_side[line_idx_side11] = 1
                curtain_side[line_idx_side22] = 1
        extent_base = False
        if type_side1 in [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL] and type_side2 in [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL] \
                and width_side1 < extent_side and width_side2 < extent_side \
                and abs(ang_to_ang(angle_side1 - line_angle + math.pi / 2)) < math.pi / 2 \
                and abs(ang_to_ang(angle_side2 - line_angle - math.pi / 2)) < math.pi / 2 \
                and room_to in ['', 'Balcony', 'Terrace']:
            extent_base = True
        if extent_base and not extent_more:
            p1_new, p2_new = line_side1['p1'], line_side2['p2']
            dis_new, ang_new = compute_dis_ang(p1[0], p1[1], p1_new[0], p1_new[1])
            tmp_x_1, tmp_z_1 = dis_new * math.cos(ang_new - line_angle), dis_new * math.sin(ang_new - line_angle)
            dis_new, ang_new = compute_dis_ang(p1[0], p1[1], p2_new[0], p2_new[1])
            tmp_x_2, tmp_z_2 = dis_new * math.cos(ang_new - line_angle), dis_new * math.sin(ang_new - line_angle)
            if abs(tmp_z_1 - tmp_z_2) < 0.1 and abs(tmp_z_1) < 1.0:
                p1, p2 = p1_new[:], p2_new[:]
                dis_new, ang_new = compute_dis_ang(p1[0], p1[1], p2[0], p2[1])
                line_width = dis_new
                line_width_original = dis_new
                curtain_side[line_idx_side1] = 1
                curtain_side[line_idx_side2] = 1
        # 内角外角
        angle_inner = normalize_line_angle(line_angle + math.pi * 0.5)
        angle_outer = normalize_line_angle(line_angle - math.pi * 0.5)
        # 独立窗帘
        if line_width >= UNIT_WIDTH_CURTAIN or extend_side1 >= 1 or extend_side2 >= 1:
            unit_depth = UNIT_DEPTH_CURTAIN
            if line_width < UNIT_WIDTH_CURTAIN * 3 and unit_height > 0.2:
                unit_depth = UNIT_DEPTH_CURTAIN / 2
            x_delta = unit_depth * math.sin(angle_inner)
            y_delta = unit_depth * math.cos(angle_inner)
            x1, y1, x2, y2 = p1[0], p1[1], p2[0], p2[1]
            x3, y3, x4, y4 = x2 + x_delta, y2 + y_delta, x1 + x_delta, y1 + y_delta
            x_center = x1 * 0.5 + x2 * 0.5 + x_delta * 0.5
            y_center = y1 * 0.5 + y2 * 0.5 + y_delta * 0.5
            rect_one = {
                'type': UNIT_TYPE_SIDE,
                'width': line_width,
                'depth': unit_depth,
                'height': unit_height,
                'bottom': unit_bottom,
                'angle': angle_inner,
                'index': line_idx,
                'p1': [round(x1, 3), round(y1, 3)],
                'p2': [round(x2, 3), round(y2, 3)],
                'p3': [round(x3, 3), round(y3, 3)],
                'p4': [round(x4, 3), round(y4, 3)],
                'center': [round(x_center, 3), round(y_center, 3)],
                'width_original': line_width_original
            }
            if line_width_original < UNIT_WIDTH_CURTAIN * 0.5:
                pass
            else:
                curtain_list.append(rect_one)
    for curtain_idx in range(len(curtain_list) - 1, -1, -1):
        curtain_one = curtain_list[curtain_idx]
        if 'index' in curtain_one and curtain_one['index'] in curtain_side:
            curtain_list.pop(curtain_idx)

    # 窗帘融合
    curtain_room, curtain_done, curtain_from = False, [], 0
    if room_type in ROOM_TYPE_LEVEL_1 or room_type in ROOM_TYPE_LEVEL_2 or room_type in ['Balcony', 'Terrace']:
        curtain_room = True
    if len(curtain_list) >= 2 and curtain_room:
        for curtain_idx, curtain_one in enumerate(curtain_list):
            curtain_pre = curtain_list[(curtain_idx - 1 + len(curtain_list)) % len(curtain_list)]
            p1, p2 = curtain_pre['p1'], curtain_pre['p2']
            q1, q2 = curtain_one['p1'], curtain_one['p2']
            dis_pre, ang_pre = compute_dis_ang(p1[0], p1[1], p2[0], p2[1])
            dis_new, ang_new = compute_dis_ang(p1[0], p1[1], q1[0], q1[1])
            tmp_x_1, tmp_z_1 = dis_new * math.cos(ang_new - ang_pre), dis_new * math.sin(ang_new - ang_pre)
            dis_new, ang_new = compute_dis_ang(p1[0], p1[1], q2[0], q2[1])
            tmp_x_2, tmp_z_2 = dis_new * math.cos(ang_new - ang_pre), dis_new * math.sin(ang_new - ang_pre)
            if abs(tmp_z_1) > 0.2 or abs(tmp_z_2) > 0.2 or min(abs(tmp_x_1), abs(tmp_x_2)) > dis_pre + 0.5:
                curtain_from = curtain_idx
                break
        for curtain_step in range(len(curtain_list)):
            curtain_idx = (curtain_from + curtain_step) % len(curtain_list)
            curtain_one = curtain_list[curtain_idx]
            curtain_find = False
            for curtain_pre in curtain_done:
                if curtain_pre['width'] <= 0.001:
                    continue
                p1, p2 = curtain_pre['p1'], curtain_pre['p2']
                p3, p4 = curtain_pre['p3'], curtain_pre['p4']
                q1, q2 = curtain_one['p1'], curtain_one['p2']
                dis_pre, ang_pre = compute_dis_ang(p1[0], p1[1], p2[0], p2[1])
                dis_new, ang_new = compute_dis_ang(p1[0], p1[1], q1[0], q1[1])
                tmp_x_1, tmp_z_1 = dis_new * math.cos(ang_new - ang_pre), dis_new * math.sin(ang_new - ang_pre)
                dis_new, ang_new = compute_dis_ang(p1[0], p1[1], q2[0], q2[1])
                tmp_x_2, tmp_z_2 = dis_new * math.cos(ang_new - ang_pre), dis_new * math.sin(ang_new - ang_pre)
                if abs(tmp_z_1) < 0.2 and abs(tmp_z_2) < 0.2 and min(abs(tmp_x_1), abs(tmp_x_2)) < dis_pre + 0.5:
                    if dis_pre >= 5 and curtain_one['width'] >= 3:
                        pass
                    else:
                        curtain_find = True
                        r1 = min(0, tmp_x_1 / dis_pre, tmp_x_2 / dis_pre)
                        r2 = max(1, tmp_x_1 / dis_pre, tmp_x_2 / dis_pre)
                        p1_new = [p1[0] * (1 - r1) + p2[0] * r1, p1[1] * (1 - r1) + p2[1] * r1]
                        p2_new = [p1[0] * (1 - r2) + p2[0] * r2, p1[1] * (1 - r2) + p2[1] * r2]
                        p3_new = [p4[0] * (1 - r2) + p3[0] * r2, p4[1] * (1 - r2) + p3[1] * r2]
                        p4_new = [p4[0] * (1 - r1) + p3[0] * r1, p4[1] * (1 - r1) + p3[1] * r1]
                        curtain_pre['p1'], curtain_pre['p2'] = p1_new, p2_new
                        curtain_pre['p3'], curtain_pre['p4'] = p3_new, p4_new
                        dis_new, ang_new = compute_dis_ang(p1_new[0], p1_new[1], p2_new[0], p2_new[1])
                        cen_x, cen_y = (p1_new[0] + p2_new[0] + p3_new[0] + p4_new[0]) / 4, \
                                       (p1_new[1] + p2_new[1] + p3_new[1] + p4_new[1]) / 4
                        curtain_pre['width'] = dis_new
                        curtain_pre['center'] = [cen_x, cen_y]
                        pass
            if not curtain_find:
                curtain_done.append(curtain_one)
    else:
        curtain_done = curtain_list

    # 返回信息
    deco_info['window_list'] = window_list
    deco_info['curtain_list'] = curtain_done
    return deco_info


def room_background(line_list, group_list, room_type=''):
    deco_info = {
        'type': 'Background',
        'info_list': []
    }
    # 返回
    return deco_info


def room_mesh():
    pass


# 功能测试
if __name__ == '__main__':
    pass
