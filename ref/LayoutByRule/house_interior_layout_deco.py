# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-11-25
@Description: 装饰家具布局

"""

from Furniture.furniture_group_comp import *
from LayoutByRule.house_calculator import *

# 部件尺寸
UNIT_DEPTH_WINDOW_FRAME = 0.03
# 关键组合
GROUP_TYPE_RELATE = ['Meeting', 'Bed', 'Media', 'Work', 'Rest']


# 其他装饰区域摆放
def room_rect_layout_deco(rect_list, line_list, deco_dict, rect_used, group_todo, group_ready,
                          room_type='', room_area=10, room_height=UNIT_HEIGHT_WALL, room_dict={},
                          door_mode=1, door_pt_entry=[]):
    # 返回信息
    group_result = []
    # 打印信息
    suit_print = False
    if room_type in ['OtherRoom'] and True:
        suit_print = True
    # 分类处理
    object_wall, object_floor, object_ceil, object_door, object_open, object_back = [], [], [], [], [], []
    object_window, object_curtain = [], []
    mesh_wall, mesh_ceil, mesh_floor, mesh_door, mesh_window, mesh_back = [], [], [], [], [], []
    for group_one in group_todo:
        if len(group_one) <= 0:
            continue
        # 补充物品
        add_default_object(group_one, room_type, room_area)
        # 分类物品
        if group_one['type'] == 'Wall':
            object_list, mesh_list = object_wall, mesh_wall
        elif group_one['type'] == 'Ceiling':
            object_list, mesh_list = object_ceil, mesh_ceil
        elif group_one['type'] == 'Floor':
            object_list, mesh_list = object_floor, mesh_floor
        elif group_one['type'] == 'Door':
            object_list, mesh_list = object_door, mesh_door
        elif group_one['type'] == 'Window':
            object_list, mesh_list = object_open, mesh_window
        elif group_one['type'] == 'Back':
            object_list, mesh_list = object_back, mesh_back
        else:
            continue
        old_obj_list, old_mat_list = [], []
        if 'obj_list' in group_one:
            old_obj_list = group_one['obj_list']
        if 'mat_list' in group_one:
            old_mat_list = group_one['mat_list']
        # 排序物品
        for obj_new in old_obj_list:
            # 数量排除
            if obj_new['count'] >= 3:
                continue
            # 尺寸排序
            find_idx = -1
            size_new = [abs(obj_new['size'][i] * obj_new['scale'][i]) / 100 for i in range(3)]
            width_new, height_new, depth_new = size_new[0], size_new[1], size_new[2]
            for obj_idx, obj_old in enumerate(object_list):
                # 数量排序
                if group_one['type'] == 'Floor' and obj_new['count'] > obj_old['count']:
                    find_idx = obj_idx
                    break
                # 类型排序
                if group_one['type'] == 'Floor' and obj_new['type'] in ['electronics/air-conditioner - floor-based']:
                    find_idx = obj_idx
                    break
                # 尺寸排序
                size_old = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
                width_old, height_old, depth_old = size_old[0], size_old[1], size_old[2]
                if group_one['type'] == 'Ceiling':
                    if height_new < 0.8 and height_old < 0.8:
                        if width_new + depth_new + height_new > width_old + depth_old + height_old:
                            find_idx = obj_idx
                            break
                    else:
                        if width_new + depth_new >= width_old + depth_old:
                            find_idx = obj_idx
                            break
                else:
                    if width_new + height_new >= width_old + height_old:
                        find_idx = obj_idx
                        break
            # 物品删除
            if group_one['type'] == 'Floor' and size_new[1] > UNIT_HEIGHT_ARMOIRE_MIN and size_new[2] < 0.1:
                if obj_new['type'] in ['cabinet/floor-based cabinet', 'storage unit/floor-based storage unit']:
                    continue
            # 物品增加
            if find_idx <= -1:
                object_list.append(obj_new)
            elif object_list[find_idx]['id'] == obj_new['id'] and group_one['type'] in ['Floor']:
                object_list[find_idx]['count'] += 1
            else:
                object_list.insert(find_idx, obj_new)
        # 增加面片
        for mesh_new in old_mat_list:
            mesh_list.append(mesh_new)
    # 窗户窗帘
    for object_one in object_open:
        if object_one['type'].startswith('window'):
            object_window.append(object_one)
        elif object_one['type'].startswith('curtain'):
            object_curtain.append(object_one)

    # 墙面检测 顶面检测 地面检测 TODO:
    todo_wall, todo_ceil, todo_floor = [], [], []
    main_ceil, face_ceil, rest_ceil = {}, {}, {}
    for rect_idx, rect_one in enumerate(rect_list):
        # 矩形信息
        rect_type, type_pre, type_post = rect_one['type'], rect_one['type_pre'], rect_one['type_post']
        rect_width, rect_depth, rect_height = rect_one['width'], rect_one['depth'], rect_one['height']
        rect_angle = rect_one['angle']
        p1, p2, p3, p4 = rect_one['p1'], rect_one['p2'], rect_one['p3'], rect_one['p4']
        unit_edge, unit_margin = rect_one['unit_edge'], rect_one['unit_margin']
        # 线段信息
        line_idx = rect_one['index']
        line_one = line_list[line_idx]
        score_pre, score_post = line_one['score_pre'], line_one['score_post']
        line_pre = line_list[(line_idx - 1 + len(line_list)) % len(line_list)]
        line_post = line_list[(line_idx + 1 + len(line_list)) % len(line_list)]
        line_width = line_one['width']
        # 背景厚度
        back_depth = 0
        if 'back_depth' in rect_one:
            back_depth = rect_one['back_depth']

        # 布局信息
        wall_info = {
            'type': rect_type, 'width': rect_width, 'depth': rect_depth, 'height': rect_height, 'angle': rect_angle,
            'p1': p1[:], 'p2': p2[:], 'center': [rect_one['center'][0], 0, rect_one['center'][1]],
            'group': '', 'object': '', 'offset': [0, 0, 0], 'position': [],
            'unit_edge': unit_edge, 'unit_margin': unit_margin, 'back_depth': back_depth
        }
        ceil_info = {
            'type': rect_type, 'width': rect_width, 'depth': rect_depth, 'height': rect_height, 'angle': rect_angle,
            'p1': p1[:], 'p2': p2[:], 'center': rect_one['center'][:],
            'group': '', 'object': '', 'offset': [0, 0, 0], 'position': [],
            'unit_edge': unit_edge, 'unit_margin': unit_margin, 'back_depth': back_depth
        }
        floor_info = {
            'type': rect_type, 'width': rect_width, 'depth': rect_depth, 'height': rect_height, 'angle': rect_angle,
            'p1': p1[:], 'p2': p2[:], 'center': [rect_one['center'][0], 0, rect_one['center'][1]],
            'group': '', 'object': '', 'offset': [0, 0, 0], 'position': [],
            'type_pre': type_pre, 'type_post': type_post,
            'unit_edge': unit_edge, 'unit_margin': unit_margin, 'back_depth': back_depth
        }
        if rect_idx in rect_used:
            param_list = rect_used[rect_idx]
            param_one = param_list[0]
            group_set = param_one['group']
            group_one = group_set[0]
            # 组合信息
            group_type, group_zone = group_one['type'], ''
            group_size, group_size_min = group_one['size'], group_one['size_min']
            group_rest, group_offset = group_one['size_rest'], group_one['offset']
            group_position, group_angle = group_one['position'], rot_to_ang(group_one['rotation'])
            group_regulate, neighbor_more, neighbor_zone = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
            if 'zone' in group_one:
                group_zone = group_one['zone']
            if 'regulation' in group_one:
                group_regulate = group_one['regulation']
            if 'neighbor_more' in group_one:
                neighbor_more = group_one['neighbor_more']
            if 'neighbor_zone' in group_one:
                neighbor_zone = group_one['neighbor_zone']
            # 区域信息
            region_point = group_position[:]
            tmp_x = (group_regulate[3] - group_regulate[1]) / 2
            tmp_z = (group_regulate[2] - group_regulate[0]) / 2
            if group_type in ['Meeting', 'Bed']:
                tmp_z += max(neighbor_zone[2], neighbor_more[2]) / 2
                ceil_info['depth'] = group_size[2] + group_regulate[2] - group_regulate[0] + neighbor_more[2]
            elif group_type in ['Work'] and room_type in ['Library']:
                tmp_z += max(neighbor_zone[2], neighbor_more[2]) / 2
                ceil_info['depth'] = group_size[2] + group_regulate[2] - group_regulate[0] + neighbor_more[2]
            elif group_type in ['Armoire', 'Cabinet']:
                tmp_x += (neighbor_zone[3] - neighbor_zone[1]) / 2
                tmp_z += neighbor_zone[2] / 2
                ceil_info['depth'] = group_size[2] + group_regulate[2] - group_regulate[0] + neighbor_more[2]
            elif group_type in ['Toilet']:
                tmp_x += (neighbor_zone[3] - neighbor_zone[1]) / 2
                tmp_z += neighbor_zone[2] / 2
                ceil_info['depth'] = group_size[2] + group_regulate[2] - group_regulate[0] + neighbor_more[2]
            add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
            add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
            region_point[0] += add_x
            region_point[2] += add_z
            # 区域判断
            if group_type in ['Meeting', 'Bed']:
                if unit_edge > 0:
                    continue
                if 'seed_size_new' in group_one and group_one['seed_size_new'][1] > UNIT_HEIGHT_ARMOIRE_MIN:
                    continue
            elif group_type in ['Cabinet', 'Appliance']:
                if room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
                    continue
            # 墙面信息
            if group_type in ['Meeting', 'Bed', 'Media', 'Dining', 'Work', 'Rest']:
                if abs(normalize_line_angle(rect_angle - group_angle)) < 0.01 or \
                        abs(normalize_line_angle(rect_angle - group_angle - math.pi)) < 0.01:
                    width_side1 = group_rest[1] + group_regulate[1]
                    width_side2 = group_rest[3] + group_regulate[3]
                    unit_margin += group_regulate[unit_edge]
                    wall_width = (width_side1 + width_side2) - abs(width_side1 - width_side2) + group_size_min[0]
                    if rect_width < min(group_size_min[0] - 0.2, 1.0) or rect_height > room_height - 0.1:
                        wall_width = 0
                    tmp_x, tmp_z = group_offset[0], -group_size[2] / 2 - unit_margin
                    if group_type in ['Work', 'Rest']:
                        tmp_x = 0
                        wall_width = (width_side1 + width_side2) + group_size_min[0]
                    elif group_type in ['Media'] and rect_height > 1.0:
                        wall_width = 0
                else:
                    width_side1 = group_rest[2] + group_regulate[2]
                    width_side2 = group_rest[0] + group_regulate[0]
                    unit_margin += group_regulate[unit_edge]
                    wall_width = (width_side1 + width_side2) - abs(width_side1 - width_side2) + group_size_min[2]
                    if rect_width < min(group_size_min[0] - 0.2, 1.0) or rect_height > UNIT_HEIGHT_WALL - 0.1:
                        wall_width = 0
                    tmp_x, tmp_z = group_offset[2], -group_size[0] / 2 - unit_margin
                    if group_type in ['Work', 'Rest']:
                        tmp_x = 0
                        wall_width = (width_side1 + width_side2) + group_size_min[2]
                    elif group_type in ['Media'] and rect_height > 1.0:
                        wall_width = 0
                if wall_width > rect_width:
                    wall_width = rect_width
                if wall_width > 0.1 and back_depth < UNIT_DEPTH_BACK_MID / 2:
                    p0 = group_position[:]
                    # 计算p1
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x + wall_width / 2) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x + wall_width / 2) * math.sin(rect_angle)
                    p1 = [p0[0] + add_x, p0[2] + add_z]
                    # 计算p2
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x - wall_width / 2) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x - wall_width / 2) * math.sin(rect_angle)
                    p2 = [p0[0] + add_x, p0[2] + add_z]
                    # 墙面信息
                    wall_add = wall_info.copy()
                    wall_add['width'], wall_add['p1'], wall_add['p2'] = wall_width, p1[:], p2[:]
                    wall_add['group'], wall_add['object'] = group_type, group_one['obj_main']
                    wall_add['offset'], wall_add['position'] = group_one['offset'][:], group_one['position'][:]
                    wall_add['back_depth'] = group_rest[0]
                    if group_type in ['Dining', 'Work', 'Rest'] and group_rest[0] > 0.1:
                        wall_add['back_depth'] = 0
                    todo_wall.append(wall_add)
            if group_type in ['Armoire', 'Cabinet', 'Appliance', 'Toilet'] and unit_edge in [0, 2]:
                group_direct = 0
                if 'region_direct' in group_one:
                    group_direct = group_one['region_direct']
                wall_width = group_size_min[0]
                wall_width += group_regulate[1]
                wall_width += group_regulate[3]
                tmp_x, tmp_z = group_offset[0], -group_size[2] / 2
                if group_regulate[1] + group_regulate[3] < 0:
                    tmp_x = group_offset[0] + (group_regulate[3] - group_regulate[1]) / 2
                max_h = UNIT_HEIGHT_ARMOIRE_MIN
                if group_type in ['Appliance'] and group_one['code'] >= 11:
                    max_h = 0.8
                elif group_type in ['Cabinet'] and room_type not in ROOM_TYPE_LEVEL_2:
                    max_h = UNIT_HEIGHT_ARMOIRE_MID
                if rect_height < max_h and back_depth < UNIT_DEPTH_BACK_MID / 2:
                    p0 = group_position[:]
                    # 计算p1
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x + wall_width / 2) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x + wall_width / 2) * math.sin(rect_angle)
                    p1 = [p0[0] + add_x, p0[2] + add_z]
                    # 计算p2
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x - wall_width / 2) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x - wall_width / 2) * math.sin(rect_angle)
                    p2 = [p0[0] + add_x, p0[2] + add_z]
                    # 墙面信息
                    wall_add = wall_info.copy()
                    wall_add['group'], wall_add['object'] = group_type, group_one['obj_main']
                    wall_add['offset'], wall_add['position'] = group_one['offset'][:], group_one['position'][:]
                    wall_add['width'], wall_add['p1'], wall_add['p2'] = wall_width, p1[:], p2[:]
                    todo_wall.append(wall_add)
                if rect_width - group_size[0] > 1 and abs(group_direct) >= 1:
                    wall_width = rect_width - group_size[0]
                    tmp_x, tmp_z = group_offset[0], -group_size[2] / 2
                    p0 = group_position[:]
                    # 计算p1
                    width_side = - (group_size[0] / 2) * group_direct
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x + width_side) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x + width_side) * math.sin(rect_angle)
                    p1 = [p0[0] + add_x, p0[2] + add_z]
                    # 计算p2
                    width_side = - (group_size[0] / 2 + wall_width) * group_direct
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x + width_side) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x + width_side) * math.sin(rect_angle)
                    p2 = [p0[0] + add_x, p0[2] + add_z]
                    # 墙面信息
                    if back_depth < UNIT_DEPTH_BACK_MID / 2:
                        wall_add = wall_info.copy()
                        wall_add['group'], wall_add['object'] = '', ''
                        wall_add['offset'], wall_add['position'] = [0, 0, 0], []
                        wall_add['width'], wall_add['p1'], wall_add['p2'] = wall_width, p1[:], p2[:]
                        todo_wall.append(wall_add)
                    # 地面信息
                    floor_add = floor_info.copy()
                    floor_add['group'], floor_add['object'] = group_type, group_one['obj_main']
                    floor_add['offset'], floor_add['position'] = group_one['offset'][:], group_one['position'][:]
                    floor_add['width'], floor_add['p1'], floor_add['p2'] = wall_width, p1[:], p2[:]
                    todo_floor.append(floor_add)
            if group_type in ['Bath', 'Toilet']:
                p1_side, p2_side = {}, {}
                side_type, side_width, side_height = line_one['type'], line_one['width'], line_one['height']
                side_angle, side_edge, side_score = line_one['angle'] + math.pi / 2, 0, 0
                type_pre, type_post = line_pre['type'], line_post['type']
                score_pre, score_post = line_one['score_pre'], line_one['score_post']
                width_pre, width_post = line_pre['width'], line_post['width']
                height_pre, height_post = line_pre['height'], line_post['height']
                if group_type in ['Bath']:
                    width_well = max(MID_GROUP_PASS * 2, line_width)
                else:
                    width_well = MID_GROUP_PASS
                if abs(group_offset[0]) > 0.4 and abs(group_offset[2]) < 0.1:
                    p1_old, p2_old = line_one['p1'][:], line_one['p2'][:]
                    r1, r2 = 0.2, 0.8
                    r0 = r2 - r1
                    p1_side = [p1_old[0] * (1 - r1) + p2_old[0] * r1, p1_old[1] * (1 - r1) + p2_old[1] * r1]
                    p2_side = [p1_old[0] * (1 - r2) + p2_old[0] * r2, p1_old[1] * (1 - r2) + p2_old[1] * r2]
                    side_type, side_width, side_height = line_one['type'], line_one['width'] * r0, line_one['height']
                    side_angle, side_edge = normalize_line_angle(line_one['angle'] + math.pi / 2), 1
                elif score_pre == 4 and type_pre == UNIT_TYPE_GROUP and width_pre > width_well * 0.5 and height_pre < UNIT_HEIGHT_WALL - 0.1:
                    p1_old, p2_old = line_pre['p2'][:], line_pre['p1'][:]
                    r1, r2 = MIN_GROUP_PASS / width_pre, MID_GROUP_PASS / width_pre
                    if group_type in ['Toilet']:
                        r1, r2 = min(0.5 + 0.1 / width_pre, 1), min(0.5 + 0.5 / width_pre, 1)
                    r0 = r2 - r1
                    p1_side = [p1_old[0] * (1 - r1) + p2_old[0] * r1, p1_old[1] * (1 - r1) + p2_old[1] * r1]
                    p2_side = [p1_old[0] * (1 - r2) + p2_old[0] * r2, p1_old[1] * (1 - r2) + p2_old[1] * r2]
                    side_type, side_width, side_height = type_pre, width_pre * r0, line_pre['height']
                    side_angle, side_edge = normalize_line_angle(line_pre['angle'] + math.pi / 2), 3
                elif score_post == 4 and type_post == UNIT_TYPE_GROUP and width_post > width_well * 0.5 and height_post < UNIT_HEIGHT_WALL - 0.1:
                    p1_old, p2_old = line_post['p1'][:], line_post['p2'][:]
                    r1, r2 = MIN_GROUP_PASS / width_post, MID_GROUP_PASS / width_post
                    if group_type in ['Toilet']:
                        r1, r2 = min(0.5 + 0.1 / width_post, 1), min(0.5 + 0.5 / width_post, 1)
                    r0 = r2 - r1
                    p1_side = [p1_old[0] * (1 - r1) + p2_old[0] * r1, p1_old[1] * (1 - r1) + p2_old[1] * r1]
                    p2_side = [p1_old[0] * (1 - r2) + p2_old[0] * r2, p1_old[1] * (1 - r2) + p2_old[1] * r2]
                    side_type, side_width, side_height = type_post, width_post * r0, line_post['height']
                    side_angle, side_edge = normalize_line_angle(line_post['angle'] + math.pi / 2), 1
                elif line_one['type'] == UNIT_TYPE_GROUP and line_width >= width_well * 0.8:
                    p1_old, p2_old = line_one['p1'][:], line_one['p2'][:]
                    r1, r2 = min(0.5 + MIN_GROUP_PASS / line_width, 1), min(0.5 + MID_GROUP_PASS / line_width, 1)
                    if group_type in ['Toilet'] and unit_edge in [1, 3]:
                        r1, r2 = 0, 1
                    r0 = r2 - r1
                    p1_side = [p1_old[0] * (1 - r1) + p2_old[0] * r1, p1_old[1] * (1 - r1) + p2_old[1] * r1]
                    p2_side = [p1_old[0] * (1 - r2) + p2_old[0] * r2, p1_old[1] * (1 - r2) + p2_old[1] * r2]
                    side_type, side_width, side_height = line_one['type'], line_one['width'] * r0, line_one['height']
                    side_angle, side_edge = normalize_line_angle(line_one['angle'] + math.pi / 2), 1
                if len(p1_side) > 0 and len(p2_side) > 0 and side_width > 0 and side_height < UNIT_HEIGHT_WALL - 0.1:
                    wall_side = wall_info.copy()
                    wall_side['type'] = UNIT_TYPE_SIDE
                    wall_side['group'], wall_side['object'] = group_type, ''
                    wall_side['offset'], wall_side['position'] = group_one['offset'][:], group_one['position'][:]
                    wall_side['width'], wall_side['p1'], wall_side['p2'] = side_width, p1_side[:], p2_side[:]
                    wall_side['height'] = side_height
                    if wall_side['height'] > 1.2:
                        wall_side['height'] = 1.2
                    wall_side['angle'] = side_angle
                    wall_side['unit_edge'] = side_edge
                    if side_score >= 4:
                        todo_wall.insert(0, wall_side)
                    else:
                        todo_wall.append(wall_side)
            # 顶面信息
            ceil_info['group'], ceil_info['object'] = group_type, group_one['obj_main']
            ceil_info['offset'], ceil_info['position'] = group_one['offset'][:], group_one['position'][:]
            ceil_info['center'] = region_point
            if group_type in ['Meeting', 'Bed', 'Toilet'] or (group_type in ['Work'] and room_type in ['Library']):
                todo_ceil.insert(0, ceil_info)
                main_ceil = ceil_info
            elif group_type in ['Media']:
                face_ceil = ceil_info
            elif group_type in ['Dining']:
                if len(main_ceil) > 0:
                    todo_ceil.insert(1, ceil_info)
                else:
                    todo_ceil.insert(0, ceil_info)
                rest_ceil = ceil_info
            elif group_type in ['Work'] and room_type not in ['Library']:
                continue
            elif group_type in ['Cabinet']:
                if group_zone in ['DiningRoom', 'CloakRoom']:
                    continue
                else:
                    info_width, info_depth = ceil_info['width'], ceil_info['depth']
                    if info_depth > info_width + 0.1:
                        continue
                    todo_ceil.append(ceil_info)
            else:
                todo_ceil.append(ceil_info)
            # 地面信息
            if group_type in ['Meeting', 'Toilet'] or (group_type in ['Media'] and group_one['size'][2] > 0.15):
                width_rest1, width_rest2 = group_rest[1], group_rest[3]
                width_side1, width_side2 = group_regulate[1], group_regulate[3]
                tmp_x, tmp_z = 0, -group_size[2] / 2
                width_half = group_size[0] / 2
                if group_type in ['Media']:
                    depth_well = UNIT_WIDTH_DOOR
                    floor_info['depth'] = depth_well
                if width_side1 > 0 and width_side2 > 0 and abs(width_side1 - width_side2) <= 0.1:
                    # 计算p1
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x + width_half) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x + width_half) * math.sin(rect_angle)
                    p1 = [group_position[0] + add_x, group_position[2] + add_z]
                    # 计算p2
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x + width_half + width_side2) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x + width_half + width_side2) * math.sin(rect_angle)
                    p2 = [group_position[0] + add_x, group_position[2] + add_z]
                    # 计算p3
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x - width_half) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x - width_half) * math.sin(rect_angle)
                    p3 = [group_position[0] + add_x, group_position[2] + add_z]
                    # 计算p4
                    add_x = tmp_z * math.sin(rect_angle) + (tmp_x - width_half - width_side1) * math.cos(rect_angle)
                    add_z = tmp_z * math.cos(rect_angle) - (tmp_x - width_half - width_side1) * math.sin(rect_angle)
                    p4 = [group_position[0] + add_x, group_position[2] + add_z]
                    # 地面信息
                    floor_add = floor_info.copy()
                    floor_add['width'] = (width_side1 + width_side2) / 2
                    floor_add['group'], floor_add['object'] = group_type, group_one['obj_main']
                    floor_add['offset'], floor_add['position'] = group_one['offset'][:], group_one['position'][:]
                    floor_add['p1'], floor_add['p2'] = p1[:], p2[:]
                    floor_add['p3'], floor_add['p4'] = p3[:], p4[:]
                    if rect_one['score_post'] > rect_one['score_pre']:
                        floor_add['p1'], floor_add['p2'] = p3[:], p4[:]
                        floor_add['p3'], floor_add['p4'] = p1[:], p2[:]
                    elif rect_one['score_pre'] == 1 == rect_one['score_post']:
                        line_idx = rect_one['index']
                        line_idx_pre = (line_idx - 1 + len(line_list)) % len(line_list)
                        line_idx_post = (line_idx + 1 + len(line_list)) % len(line_list)
                        line_pre, line_post = line_list[line_idx_pre], line_list[line_idx_post]
                        # 两侧优先
                        if line_post['type'] == UNIT_TYPE_SIDE and line_post['width'] < UNIT_DEPTH_CURTAIN + 0.01 \
                                and width_side1 < UNIT_DEPTH_GROUP_MIN:
                            floor_add['p1'], floor_add['p2'] = p3[:], p4[:]
                            floor_add['p3'], floor_add['p4'] = p1[:], p2[:]
                        elif line_post['type'] > line_pre['type']:
                            floor_add['p1'], floor_add['p2'] = p3[:], p4[:]
                            floor_add['p3'], floor_add['p4'] = p1[:], p2[:]
                    floor_add['back_depth'] = 0
                    todo_floor.append(floor_add)
                else:
                    if width_side1 > 0 and (width_rest1 > 0 or width_rest2 <= 0):
                        # 计算p3
                        add_x = tmp_z * math.sin(rect_angle) + (tmp_x - width_half) * math.cos(rect_angle)
                        add_z = tmp_z * math.cos(rect_angle) - (tmp_x - width_half) * math.sin(rect_angle)
                        p3 = [group_position[0] + add_x, group_position[2] + add_z]
                        # 计算p4
                        add_x = tmp_z * math.sin(rect_angle) + (tmp_x - width_half - width_side1) * math.cos(rect_angle)
                        add_z = tmp_z * math.cos(rect_angle) - (tmp_x - width_half - width_side1) * math.sin(rect_angle)
                        p4 = [group_position[0] + add_x, group_position[2] + add_z]
                        # 地面信息
                        floor_add = floor_info.copy()
                        floor_add['width'] = width_side1
                        floor_add['group'], floor_add['object'] = group_type, group_one['obj_main']
                        floor_add['offset'], floor_add['position'] = group_one['offset'][:], group_one['position'][:]
                        floor_add['p1'], floor_add['p2'] = p3[:], p4[:]
                        floor_add['back_depth'] = 0
                        todo_floor.append(floor_add)
                    if width_side2 > 0 and (width_rest2 > 0 or width_rest1 <= 0):
                        # 计算p1
                        add_x = tmp_z * math.sin(rect_angle) + (tmp_x + width_half) * math.cos(rect_angle)
                        add_z = tmp_z * math.cos(rect_angle) - (tmp_x + width_half) * math.sin(rect_angle)
                        p1 = [group_position[0] + add_x, group_position[2] + add_z]
                        # 计算p2
                        add_x = tmp_z * math.sin(rect_angle) + (tmp_x + width_half + width_side2) * math.cos(rect_angle)
                        add_z = tmp_z * math.cos(rect_angle) - (tmp_x + width_half + width_side2) * math.sin(rect_angle)
                        p2 = [group_position[0] + add_x, group_position[2] + add_z]
                        # 地面信息
                        floor_add = floor_info.copy()
                        floor_add['width'] = width_side2
                        floor_add['group'], floor_add['object'] = group_type, group_one['obj_main']
                        floor_add['offset'], floor_add['position'] = group_one['offset'][:], group_one['position'][:]
                        floor_add['p1'], floor_add['p2'] = p1[:], p2[:]
                        floor_add['back_depth'] = 0
                        todo_floor.append(floor_add)
        else:
            if rect_type == UNIT_TYPE_WINDOW and rect_height < 0.1:
                continue
            elif rect_type == UNIT_TYPE_GROUP:
                continue
            # 墙面信息
            wall_flag = True
            if rect_type == UNIT_TYPE_WINDOW:
                wall_flag = False
            elif line_one['score'] == 2 and line_pre['type'] == line_post['type'] == UNIT_TYPE_WINDOW:
                if rect_width < MID_GROUP_PASS * 4:
                    wall_flag = False
                    rect_height = min(line_pre['height'], line_post['height'])
            if back_depth < UNIT_DEPTH_BACK_MID * 0.5 and wall_flag:
                wall_width = rect_width
                wall_add = wall_info.copy()
                wall_add['group'], wall_add['object'] = '', ''
                wall_add['offset'], wall_add['position'] = [0, 0, 0], []
                wall_add['width'], wall_add['p1'], wall_add['p2'] = wall_width, p1[:], p2[:]
                todo_wall.append(wall_add)
            # 地面信息
            floor_add = floor_info.copy()
            floor_add['height'] = rect_height
            if score_pre == 1:
                if 'unit_group' in line_pre:
                    floor_add['group'] = line_pre['unit_group']
                if type_pre in [UNIT_TYPE_SIDE] and line_pre['width'] <= UNIT_DEPTH_CURTAIN + 0.01:
                    floor_add['type_pre'] = UNIT_TYPE_WINDOW
            elif score_post == 1:
                if 'unit_group' in line_post:
                    floor_add['group'] = line_post['unit_group']
                if type_post in [UNIT_TYPE_SIDE] and line_post['width'] <= UNIT_DEPTH_CURTAIN + 0.01:
                    floor_add['type_post'] = UNIT_TYPE_WINDOW
            if back_depth < UNIT_DEPTH_BACK_MID * 0.5:
                todo_floor.append(floor_add)
    # 顶面补充
    if len(main_ceil) <= 0 and len(group_ready) > 0:
        for group_one in group_ready:
            group_type = group_one['type']
            group_position, group_angle = group_one['position'], rot_to_ang(group_one['rotation'])
            group_regulate, neighbor_more, neighbor_zone = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
            if 'regulation' in group_one:
                group_regulate = group_one['regulation']
            if 'neighbor_more' in group_one:
                neighbor_more = group_one['neighbor_more']
            if 'neighbor_zone' in group_one:
                neighbor_zone = group_one['neighbor_zone']
            if group_type in ['Meeting', 'Bed']:
                region_point = group_position[:]
                tmp_x = (group_regulate[3] - group_regulate[1]) / 2
                tmp_z = (group_regulate[2] - group_regulate[0]) / 2
                tmp_z += neighbor_zone[2] / 2
                add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                region_point[0] += add_x
                region_point[2] += add_z
                ceil_info = {'type': UNIT_TYPE_GROUP, 'width': group_one['size'][0], 'depth': group_one['size'][2],
                             'height': group_one['size'][1], 'angle': rot_to_ang(group_one['rotation']),
                             'p1': [], 'p2': [], 'center': region_point[:],
                             'group': group_one['type'], 'object': group_one['obj_main'],
                             'offset': group_one['offset'][:], 'position': group_one['position'][:],
                             'unit_edge': 0, 'unit_margin': 0, 'back_depth': 0}
                todo_ceil.insert(0, ceil_info)
                break
    if len(rest_ceil) <= 0 and len(group_ready) > 0:
        for group_one in group_ready:
            group_type = group_one['type']
            group_position, group_angle = group_one['position'], rot_to_ang(group_one['rotation'])
            group_regulate, neighbor_more, neighbor_zone = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
            if 'regulation' in group_one:
                group_regulate = group_one['regulation']
            if 'neighbor_more' in group_one:
                neighbor_more = group_one['neighbor_more']
            if 'neighbor_zone' in group_one:
                neighbor_zone = group_one['neighbor_zone']
            if group_type in ['Dining', 'Work', 'Rest']:
                region_point = group_position[:]
                tmp_x = (group_regulate[3] - group_regulate[1]) / 2
                tmp_z = (group_regulate[2] - group_regulate[0]) / 2
                if room_type in ['DiningRoom', 'Library', 'Balcony', 'Terrace']:
                    tmp_z += neighbor_zone[2] / 2
                elif len(group_ready) <= 1:
                    tmp_z += neighbor_zone[2] / 2
                add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                region_point[0] += add_x
                region_point[2] += add_z
                ceil_info = {'type': UNIT_TYPE_GROUP, 'width': group_one['size'][0], 'depth': group_one['size'][2],
                             'height': group_one['size'][1], 'angle': rot_to_ang(group_one['rotation']),
                             'p1': [], 'p2': [], 'center': region_point[:],
                             'group': group_one['type'], 'object': group_one['obj_main'],
                             'offset': group_one['offset'][:], 'position': group_one['position'][:],
                             'unit_edge': 0, 'unit_margin': 0, 'back_depth': 0}
                todo_ceil.insert(1, ceil_info)
                break

    # 房门检测 门洞检测
    todo_door = []
    if 'Door' in deco_dict:
        door_info = deco_dict['Door']
        todo_door = door_info['door_list']
        # 门洞信息
        for unit_one in todo_door:
            unit_size = [unit_one['width'], unit_one['height'], unit_one['depth']]
            unit_position = [unit_one['center'][0], 0, unit_one['center'][1]]
            unit_rotation = [0, math.sin(unit_one['angle'] / 2), 0, math.cos(unit_one['angle'] / 2)]
            unit_one['size'] = unit_size
            unit_one['position'] = unit_position
            unit_one['rotation'] = unit_rotation
    # 窗户检测 窗帘检测
    todo_window, todo_curtain = [], []
    if 'Window' in deco_dict:
        window_info = deco_dict['Window']
        todo_window, todo_curtain = window_info['window_list'], window_info['curtain_list']
        # 窗户信息
        for unit_one in todo_window:
            unit_bot = unit_one['bottom']
            unit_size = [unit_one['width'], unit_one['height'], unit_one['depth']]
            unit_position = [unit_one['center'][0], unit_bot, unit_one['center'][1]]
            unit_rotation = [0, math.sin(unit_one['angle'] / 2), 0, math.cos(unit_one['angle'] / 2)]
            unit_one['size'] = unit_size
            unit_one['position'] = unit_position
            unit_one['rotation'] = unit_rotation
        # 窗帘信息
        for unit_one in todo_curtain:
            unit_bot = unit_one['bottom'] - UNIT_HEIGHT_CURTAIN_BOT * 1
            if unit_one['width'] > 2:
                if 'width_origin' in unit_one and unit_one['width'] > unit_one['width_origin'] * 0.5:
                    unit_bot = 0
                else:
                    unit_bot = unit_one['bottom'] - UNIT_HEIGHT_CURTAIN_BOT * 2
            if unit_bot < UNIT_HEIGHT_WINDOW_BOTTOM:
                unit_bot = 0
            unit_size = [unit_one['width'], room_height - unit_bot, unit_one['depth']]
            unit_position = [unit_one['center'][0], unit_bot, unit_one['center'][1]]
            unit_rotation = [0, math.sin(unit_one['angle'] / 2), 0, math.cos(unit_one['angle'] / 2)]
            unit_one['size'] = unit_size
            unit_one['position'] = unit_position
            unit_one['rotation'] = unit_rotation
    # 背景检测
    todo_back = []

    # 分类布局
    group_wall = room_rect_layout_wall(todo_wall, object_wall, mesh_wall, room_type, room_height)
    group_ceil = room_rect_layout_ceil(todo_ceil, object_ceil, mesh_ceil, room_type, room_height)
    group_floor = room_rect_layout_floor(todo_floor, object_floor, mesh_floor, room_type, room_height)
    group_door = room_rect_layout_door(todo_door, object_door, mesh_door, room_type, room_height, room_dict, door_mode)
    group_window = room_rect_layout_window(todo_window, todo_curtain, object_window, object_curtain, mesh_window,
                                           room_type, room_height, room_dict)
    group_back = room_rect_layout_back(todo_back, object_back, mesh_back, room_type, room_height)
    # 检测布局
    wall_done, floor_done = [], []
    if 'obj_list' in group_wall:
        wall_done = group_wall['obj_list']
    if 'obj_list' in group_floor:
        floor_done = group_floor['obj_list']
    for object_idx in range(len(floor_done) - 1, -1, -1):
        object_old = floor_done[object_idx]
        size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
        pos_old = object_old['position']
        if size_old[2] > 0.2:
            continue
        object_del = False
        for object_new in wall_done:
            size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
            pos_new = object_new['position']
            dis_new = max(abs(pos_new[0] - pos_old[0]), abs(pos_new[2] - pos_old[2]))
            if dis_new < size_new[0] / 2 + size_old[0] / 2:
                if pos_old[1] + size_old[1] > pos_new[1]:
                    object_del = True
                    break
        if object_del:
            floor_done.pop(object_idx)

    # 返回布局
    group_result.append(group_wall)
    group_result.append(group_ceil)
    group_result.append(group_floor)
    group_result.append(group_door)
    group_result.append(group_window)
    return group_result


def room_rect_layout_wall(todo_wall, object_wall, mesh_wall, room_type='', room_height=UNIT_HEIGHT_WALL):
    # 分析布局
    used_wall = {}

    # 附着布局
    object_wait, object_plat_list, object_plat_dict = [], [], {}
    for object_idx in range(len(object_wall) - 1, -1, -1):
        object_one = object_wall[object_idx]
        relate_obj, relate_grp = '', ''
        if 'relate' in object_one:
            relate_obj = object_one['relate']
        if 'relate_group' in object_one:
            relate_grp = object_one['relate_group']
        if relate_grp == '' and not relate_obj == '':
            if 'relate_position' in object_one and len(object_one['relate_position']) > 0:
                object_wait.append(object_one)
                plat_id, plat_pos = object_one['relate'], object_one['relate_position']
                plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                object_plat_dict[plat_key] = {}
            object_wall.pop(object_idx)
    for object_idx in range(len(object_wall) - 1, -1, -1):
        object_one = object_wall[object_idx]
        plat_id, plat_pos = object_one['id'], object_one['position']
        plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
        if 'fake_id' in object_one and object_one['fake_id'].startswith('link'):
            plat_key = object_one['fake_id'] + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
        if plat_key in object_plat_dict:
            object_plat_list.append(object_one)
            object_wall.pop(object_idx)
    for object_one in object_plat_list:
        object_wall.insert(0, object_one)

    # 关联布局
    object_find = []
    for object_idx, object_one in enumerate(object_wall):
        if object_idx in object_find:
            continue
        relate_group, relate_role, relate_obj = '', '', ''
        if 'relate_group' in object_one:
            relate_group = object_one['relate_group']
        if 'relate_role' in object_one:
            relate_role = object_one['relate_role']
        if 'relate' in object_one:
            relate_obj = object_one['relate']
        if relate_obj == '' and relate_role == '':
            continue
        if len(object_wall) <= 1 and room_type in ROOM_TYPE_LEVEL_1:
            continue
        object_width = abs(object_one['size'][0] * object_one['scale'][0] / 100)
        # 最佳参数
        param_best = {'index': -1, 'score': -100, 'count': 1, 'group': [], 'unit_edge': 0, 'relate_group': ''}
        # 矩形查找
        best_idx, best_one, best_width = -1, {}, 0
        for info_idx, info_one in enumerate(todo_wall):
            if info_idx in used_wall:
                continue
            info_type, info_group, info_object = info_one['type'], info_one['group'], info_one['object']
            info_width, info_height, info_edge = info_one['width'], info_one['height'], info_one['unit_edge']
            if not info_group == relate_group:
                continue
            if info_group in ['Armoire', 'Cabinet', 'Appliance', 'Bath', 'Toilet']:
                if info_width < object_width * 0.9:
                    continue
            elif info_width < object_width * 1.0:
                continue
            elif info_group in ['Meeting', 'Dining', 'Work'] and info_height > UNIT_HEIGHT_WALL - 0.1:
                continue
            elif 'back_depth' in info_one and info_one['back_depth'] > 0.20:
                continue
            if info_object == relate_obj:
                best_idx, best_one = info_idx, info_one
            elif info_group == relate_group and info_group in ['Bath', 'Toilet']:
                if 'normal_position' in object_one:
                    normal_position = object_one['normal_position']
                    if abs(normal_position[0]) < 0.15 and info_edge == 0:
                        best_idx, best_one = info_idx, info_one
                    elif abs(normal_position[0]) > 0.15 and info_edge > 0:
                        best_idx, best_one = info_idx, info_one
            elif info_group == relate_group and relate_obj == '':
                best_idx, best_one = info_idx, info_one
            if best_idx >= 0:
                break
        # 最佳参数
        if 0 <= best_idx < len(todo_wall) and len(best_one) > 0:
            info_idx, info_one = best_idx, best_one
            # 参数信息
            param_best['index'] = info_idx
            param_best['score'] = 10
            param_best['count'] = 1
            param_best['unit_edge'] = info_one['unit_edge']
            param_best['relate_group'] = info_one['group']
            # 新建信息
            object_add = copy_exist_object(object_one)
            # 添加信息
            param_add = param_best.copy()
            param_add['group'].append(object_add)
            index_add = int(param_add['index'])
            if index_add not in used_wall:
                used_wall[index_add] = []
            used_wall[index_add].append(param_add)
            object_find.append(object_idx)
        # 放弃布局
        if object_idx not in object_find and relate_group in ['Bath', 'Toilet']:
            if 'normal_position' in object_one:
                normal_position = object_one['normal_position']
                if abs(normal_position[0]) > 0.15:
                    object_find.append(object_idx)

    # 遍历布局
    for object_idx, object_one in enumerate(object_wall):
        if object_idx in object_find:
            continue
        object_type = object_one['type']
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        object_width, object_height, object_depth = object_size[0], object_size[1], object_size[2]
        # 最佳参数
        param_best = {'index': -1, 'score': -100, 'count': 1, 'group': [], 'unit_edge': 0,
                      'relate': '', 'relate_group': '', 'relate_position': []}
        # 矩形查找
        for info_idx, info_one in enumerate(todo_wall):
            if info_idx in used_wall:
                continue
            info_type, info_group, info_edge = info_one['type'], info_one['group'], info_one['unit_edge']
            info_width, info_depth, info_height = info_one['width'], info_one['depth'], info_one['height']
            back_depth = 0
            if 'back_depth' in info_one:
                info_back = info_one['back_depth']
            if info_group in ['Bath', 'Toilet'] and not info_edge == 0:
                continue
            if info_group in ['Meeting', 'Bed', 'Work'] and 'cabinet' in object_type:
                continue
            if info_group in ['Meeting', 'Dining', 'Work'] and info_height > UNIT_HEIGHT_WALL - UNIT_HEIGHT_CEIL:
                continue
            if info_group in ['Cabinet', 'Applance'] and info_height > UNIT_HEIGHT_ARMOIRE_MIN:
                continue
            if info_type in [UNIT_TYPE_GROUP, UNIT_TYPE_SIDE] and 'lamp' in object_type:
                continue
            if info_type in [UNIT_TYPE_AISLE] and object_depth > 0.2:
                continue
            if info_depth < object_depth:
                continue
            if back_depth > 0.2:
                continue
            # 墙体排除
            if info_type == UNIT_TYPE_WINDOW:
                continue
            elif info_type == UNIT_TYPE_GROUP:
                if info_height + object_height > room_height - UNIT_HEIGHT_CEIL:
                    continue
                if info_group in ['Dining', 'Work', 'Rest']:
                    if info_height > UNIT_HEIGHT_ARMOIRE_MIN:
                        continue
                    if info_width < object_width * 1.2:
                        continue
                elif info_group in ['Armoire', 'Cabinet', 'Appliance', 'Bath', 'Toilet']:
                    if info_width < object_width * 1.0:
                        continue
                elif info_width < object_width * 0.8:
                    continue
            elif info_type == UNIT_TYPE_AISLE:
                if info_width < object_width * 2 or info_width < 2:
                    continue
            else:
                if room_type in ROOM_TYPE_LEVEL_3 or room_type in ['Library'] or object_width > 1.5:
                    if info_width < object_width * 1 or info_width < 0.5:
                        continue
                else:
                    if info_width < min(object_width * 2, MID_GROUP_PASS * 2) and object_depth < 0.2:
                        continue
                    elif info_width < min(object_width * 2, MID_GROUP_PASS * 2) or info_width < 1.0:
                        continue
            # 位置分数
            score_place = 0
            if info_type == UNIT_TYPE_GROUP:
                if info_group in ['Meeting', 'Bed']:
                    score_place = 8
                elif info_group in ['Dining', 'Work']:
                    score_place = 6
                elif info_group in ['Rest', 'Cabinet', 'Appliance']:
                    score_place = 4
                    if info_edge in [1, 3]:
                        score_place -= 5
                elif room_type in ROOM_TYPE_LEVEL_3:
                    score_place -= 2
            elif info_type == UNIT_TYPE_AISLE:
                score_place = -5
            else:
                pass
            # 数量处理
            count_best = 1
            # 宽度分数
            score_width = abs(info_width - object_width * count_best) / info_width * 5
            # 整体分数
            score_best = score_place + score_width
            if score_best > param_best['score']:
                param_best['index'] = info_idx
                param_best['score'] = score_best
                param_best['count'] = count_best
                param_best['unit_edge'] = info_one['unit_edge']
                param_best['relate'] = info_one['object']
                param_best['relate_group'] = info_one['group']
                param_best['relate_position'] = info_one['position']
        # 参数判断
        if param_best['index'] < 0:
            continue
        # 参数信息
        param_add = param_best.copy()
        object_add = copy_exist_object(object_one)
        param_add['group'].append(object_add)
        # 参数添加
        index_add = int(param_add['index'])
        if index_add not in used_wall:
            used_wall[index_add] = []
        used_wall[index_add].append(param_add)

    # 计算布局
    group_wall = {
        'type': 'Wall',
        'size': [0, 0, 0],
        'offset': [0, 0, 0],
        'position': [0, 0, 0],
        'rotation': [0, 0, 0, 1],
        'obj_main': '',
        'obj_list': [],
        'mat_list': mesh_wall
    }
    for info_idx, param_list in used_wall.items():
        # 线段信息
        info_one = todo_wall[info_idx]
        info_type, info_group, info_object = info_one['type'], info_one['group'], info_one['object']
        info_width, info_depth, info_height = info_one['width'], info_one['depth'], info_one['height']
        info_angle, info_edge = info_one['angle'], info_one['unit_edge']
        p1, p2, ratio_w = info_one['p1'], info_one['p2'], 0.5
        back_depth = info_one['back_depth']
        # 遍历参数
        for param_idx, param_one in enumerate(param_list):
            object_all = param_one['group']
            for object_idx, object_one in enumerate(object_all):
                plat_id, plat_pos = object_one['id'], object_one['position']
                plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                relate_group = ''
                if 'relate_group' in object_one:
                    relate_group = object_one['relate_group']
                # 更新信息
                origin_size, origin_scale = object_one['size'], object_one['scale']
                object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
                object_width, object_height = object_size[0], object_size[1]
                object_y = object_one['position'][1]
                if info_height > 1.5 and len(relate_group) > 0:
                    pass
                else:
                    if object_y < max(info_height + 0.1, 1.0):
                        object_y = max(info_height + 0.1, 1.0)
                    if object_y > room_height - object_height - 0.1:
                        object_y = room_height - object_height - 0.1
                    if len(info_group) <= 0:
                        if object_y < 1.5 - object_height and object_height < 1.0:
                            object_y = 2.0 - object_height
                    else:
                        if object_y < info_height + 0.02:
                            object_y = info_height + 0.02
                if object_width > info_width:
                    object_one['scale'][0] *= (info_width / object_width)
                    object_size[0] = info_width
                ratio_w = 0.5
                if relate_group in ['Toilet']:
                    if 'normal_position' in object_one:
                        normal_position = object_one['normal_position']
                        if abs(normal_position[0]) < MIN_GROUP_PASS and info_edge == 0:
                            ratio_w -= normal_position[0] / info_width
                elif object_height > object_width * 2 and relate_group == '':
                    ratio_w = min(0.5, 0.6 * object_width / info_width)

                if len(object_all) >= 2:
                    if 'normal_position' in object_one:
                        normal_position = object_one['normal_position']
                        ratio_w -= normal_position[0] / info_width
                    else:
                        continue
                # 计算位置
                dd = object_size[2] / 2
                if info_height > 1.5 and 'normal_position' in object_one:
                    rely_depth = object_one['normal_position'][2] + info_depth / 2
                    if 0 < rely_depth < 0.1:
                        dd += rely_depth
                pp = [0, 0]
                pp[0] = p1[0] * (1 - ratio_w) + p2[0] * ratio_w + dd * math.sin(info_angle)
                pp[1] = p1[1] * (1 - ratio_w) + p2[1] * ratio_w + dd * math.cos(info_angle)
                # 更新信息
                object_one['position'] = [pp[0], object_y, pp[1]]
                object_one['rotation'] = [0, math.sin(info_angle / 2), 0, math.cos(info_angle / 2)]
                object_one['relate'] = ''
                object_one['relate_role'] = ''
                object_one['relate_group'] = param_one['relate_group']
                object_one['relate_position'] = []
                if param_one['relate_group'] in ['Cabinet', 'Armoire', 'Appliance']:
                    pass
                # 新增分组
                group_wall['obj_list'].append(object_one)
                if plat_key in object_plat_dict:
                    object_plat_dict[plat_key] = object_one

    # 附着布局
    for object_one in object_wait:
        if 'relate_position' in object_one and len(object_one['relate_position']) > 0:
            plat_id, plat_pos = object_one['relate'], object_one['relate_position']
            plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            if plat_key not in object_plat_dict:
                continue
            plat_one = object_plat_dict[plat_key]
            if len(plat_one) <= 0:
                continue
            plat_pos_new, plat_ang_new = plat_one['position'], rot_to_ang(plat_one['rotation'])
            plat_pos_old, plat_ang_old = plat_pos, plat_ang_new
            if 'relate_rotation' in object_one and len(object_one['relate_rotation']) > 0:
                plat_ang_old = rot_to_ang(object_one['relate_rotation'])
            object_pos_old, object_ang_old = object_one['position'], rot_to_ang(object_one['rotation'])
            tmp_x, tmp_z = object_pos_old[0] - plat_pos_old[0], object_pos_old[2] - plat_pos_old[2]
            tmp_y = object_pos_old[1] - plat_pos_old[1]
            plat_ang_dlt = plat_ang_new - plat_ang_old
            add_x = tmp_z * math.sin(plat_ang_dlt) + tmp_x * math.cos(plat_ang_dlt)
            add_z = tmp_z * math.cos(plat_ang_dlt) - tmp_x * math.sin(plat_ang_dlt)
            object_pos_new = [plat_pos_new[0] + add_x, plat_pos_new[1] + tmp_y, plat_pos_new[2] + add_z]
            object_ang_new = object_ang_old + plat_ang_dlt
            object_rot_new = [0, math.sin(object_ang_new / 2), 0, math.cos(object_ang_new / 2)]
            object_one['position'] = object_pos_new[:]
            object_one['rotation'] = object_rot_new[:]
            object_one['relate'] = plat_one['id']
            object_one['relate_role'] = ''
            object_one['relate_group'] = ''
            object_one['relate_position'] = plat_one['position'][:]
            object_one['relate_rotation'] = plat_one['rotation'][:]
            # 添加信息
            group_wall['obj_list'].append(object_one)

    # 返回布局
    return group_wall


def room_rect_layout_ceil(todo_ceil, object_ceil, mesh_ceil, room_type='', room_height=UNIT_HEIGHT_WALL):
    # 分析布局
    used_ceil = {}

    # 附着布局
    object_wait, object_plat_list, object_plat_dict = [], [], {}
    for object_idx in range(len(object_ceil) - 1, -1, -1):
        object_one = object_ceil[object_idx]
        relate_obj, relate_grp = '', ''
        if 'relate' in object_one:
            relate_obj = object_one['relate']
        if 'relate_group' in object_one:
            relate_grp = object_one['relate_group']
        if relate_grp == '' and not relate_obj == '':
            if 'relate_position' in object_one and len(object_one['relate_position']) > 0:
                object_wait.append(object_one)
                plat_id, plat_pos = object_one['relate'], object_one['relate_position']
                plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                object_plat_dict[plat_key] = {}
            object_ceil.pop(object_idx)
    for object_idx in range(len(object_ceil) - 1, -1, -1):
        object_one = object_ceil[object_idx]
        plat_id, plat_pos = object_one['id'], object_one['position']
        plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
        if 'fake_id' in object_one and object_one['fake_id'].startswith('link'):
            plat_key = object_one['fake_id'] + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
        if plat_key in object_plat_dict:
            object_plat_list.append(object_one)
            object_ceil.pop(object_idx)
    for object_one in object_plat_list:
        object_ceil.insert(0, object_one)

    # 关联布局
    object_find = []
    for object_idx, object_one in enumerate(object_ceil):
        relate_obj, relate_grp = '', ''
        if 'relate' in object_one:
            relate_obj = object_one['relate']
        if 'relate_group' in object_one:
            relate_grp = object_one['relate_group']
        if relate_obj == '':
            continue
        origin_size, origin_scale = object_one['size'], object_one['scale']
        object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        if object_size[1] > 1.5 and origin_scale[1] > 1.5:
            scale_fix = 1.5 / origin_scale[1]
            origin_scale = [object_one['scale'][i] * scale_fix for i in range(3)]
            object_one['scale'] = origin_scale[:]
            object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        if object_size[1] > 1.5 and 'pendant light' in object_one['type']:
            continue
        # 尺寸信息
        height_max = 1.2
        if relate_grp in ['Meeting', 'Bed']:
            height_max = 0.8
        if object_size[1] > height_max:
            object_ratio = abs(height_max) / object_size[1]
            object_scale = object_one['scale']
            object_scale[0] *= object_ratio
            object_scale[1] *= object_ratio
            object_scale[2] *= object_ratio
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        # 矩形查找
        for info_idx, info_one in enumerate(todo_ceil):
            if info_idx in used_ceil:
                continue
            info_type, info_group, info_object = info_one['type'], info_one['group'], info_one['object']
            info_angle, info_width, info_depth = info_one['angle'], info_one['width'], info_one['depth']
            if not info_group == object_one['relate_group']:
                continue
            relate_find = False
            if info_group in ['Meeting', 'Bed', 'Dining']:
                relate_find = True
            elif info_object == object_one['relate']:
                relate_find = True
            if relate_find:
                if object_size[0] > object_size[2] * 2:
                    if 'unit_edge' in info_one and info_one['unit_edge'] in [1, 3]:
                        info_angle = ang_to_ang(info_angle + math.pi / 2)
                elif object_size[2] > object_size[0] * 2:
                    if 'unit_edge' in info_one and info_one['unit_edge'] in [0, 2]:
                        info_angle = ang_to_ang(info_angle + math.pi / 2)
                if 'center' in info_one and len(info_one['center']) > 0:
                    # 新建信息
                    object_add = copy_exist_object(object_one)
                    # 附着信息
                    if 'fake_id' in object_add and object_add['fake_id'].startswith('link'):
                        plat_id_old, plat_pos = object_add['id'], object_add['position']
                        plat_key_old = object_add['fake_id'] + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                        plat_id_new = 'link_%d' % info_idx
                        plat_key_new = plat_id_new + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                        object_wait_set = []
                        for object_wait_one in object_wait:
                            if 'relate_position' in object_wait_one and len(object_wait_one['relate_position']) > 0:
                                plat_id, plat_pos = object_wait_one['relate'], object_wait_one['relate_position']
                                plat_key_one = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                                if plat_key_one == plat_key_old:
                                    object_wait_add = copy_exist_object(object_wait_one)
                                    object_wait_add['relate'] = plat_id_new
                                    object_wait_set.append(object_wait_add)
                        object_add['id'] = plat_id_new
                        for object_wait_one in object_wait_set:
                            object_wait.append(object_wait_one)
                        object_plat_dict[plat_key_new] = object_add
                    # 参数信息
                    object_position = info_one['center'][:]
                    object_position[1] = room_height - UNIT_HEIGHT_CEIL - object_size[1]
                    object_rotation = [0, math.sin(info_angle / 2), 0, math.cos(info_angle / 2)]
                    object_relation = info_one['group']
                    object_add['position'] = object_position
                    object_add['rotation'] = object_rotation
                    object_add['relate'] = ''
                    object_add['relate_role'] = ''
                    object_add['relate_group'] = object_relation
                    object_add['relate_position'] = []
                    # 添加信息
                    param_add = {'index': info_idx, 'count': 1, 'group': [object_add]}
                    index_add = int(param_add['index'])
                    used_ceil[index_add] = param_add
                    object_find.append(object_idx)
                    break

    # 遍历布局
    for object_idx, object_one in enumerate(object_ceil):
        if object_idx in object_find:
            continue
        if object_one['count'] > 2:
            continue
        relate_obj, relate_grp = '', ''
        if 'relate' in object_one:
            relate_obj = object_one['relate']
        if 'relate_group' in object_one:
            relate_grp = object_one['relate_group']
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        if object_size[1] < 1.0:
            if max(object_size[0], object_size[2]) > 5.0:
                continue
        if object_size[1] < 1.0 and 'air-conditioning vent' in object_one['type']:
            if max(object_size[0], object_size[2]) > 3.0:
                continue
        if object_size[1] > 1.5 and 'pendant light' in object_one['type']:
            if max(object_size[0], object_size[2]) < 0.5:
                continue
        # 矩形查找
        for info_idx, info_one in enumerate(todo_ceil):
            if info_idx in used_ceil:
                continue
            info_type, info_group, info_object = info_one['type'], info_one['group'], info_one['object']
            info_angle, info_width, info_depth = info_one['angle'], info_one['width'], info_one['depth']
            if object_size[0] > object_size[2] * 2:
                if 'unit_edge' in info_one and info_one['unit_edge'] in [1, 3]:
                    info_angle = ang_to_ang(info_angle + math.pi / 2)
            elif object_size[2] > object_size[0] * 2:
                if 'unit_edge' in info_one and info_one['unit_edge'] in [0, 2]:
                    info_angle = ang_to_ang(info_angle + math.pi / 2)
            if info_group in ['Meeting'] and object_size[1] > 1.5:
                continue
            elif info_group in ['Dining'] and object_size[0] > info_width:
                continue
            elif info_group in ['Media']:
                continue
            elif info_group in ['Cabinet'] and len(relate_grp) > 0:
                continue
            elif object_size[0] > info_width and object_size[0] > object_size[2] * 10:
                continue
            if 'center' in info_one and len(info_one['center']) > 0:
                # 新建信息
                object_add = copy_exist_object(object_one)
                # 附着信息
                if 'fake_id' in object_add and object_add['fake_id'].startswith('link'):
                    plat_id_old, plat_pos = object_add['id'], object_add['position']
                    plat_key_old = object_add['fake_id'] + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                    plat_id_new = 'link_%d' % info_idx
                    plat_key_new = plat_id_new + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                    object_wait_set = []
                    for object_wait_one in object_wait:
                        if 'relate_position' in object_wait_one and len(object_wait_one['relate_position']) > 0:
                            plat_id, plat_pos = object_wait_one['relate'], object_wait_one['relate_position']
                            plat_key_one = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                            if plat_key_one == plat_key_old:
                                object_wait_add = copy_exist_object(object_wait_one)
                                object_wait_add['relate'] = plat_id_new
                                object_wait_set.append(object_wait_add)
                    object_add['id'] = plat_id_new
                    for object_wait_one in object_wait_set:
                        object_wait.append(object_wait_one)
                    object_plat_dict[plat_key_new] = object_add
                # 参数信息
                object_position = info_one['center'][:]
                object_position[1] = room_height - UNIT_HEIGHT_CEIL - object_size[1]
                object_rotation = [0, math.sin(info_angle / 2), 0, math.cos(info_angle / 2)]
                object_relation = info_one['group']
                object_add['position'] = object_position
                object_add['rotation'] = object_rotation
                object_add['relate'] = ''
                object_add['relate_role'] = ''
                object_add['relate_group'] = object_relation
                object_add['relate_position'] = []
                # 添加信息
                param_add = {'index': info_idx, 'count': 1, 'group': [object_add]}
                index_add = int(param_add['index'])
                used_ceil[index_add] = param_add
                break

    # 计算布局
    group_ceiling = {
        'type': 'Ceiling',
        'size': [0, 0, 0],
        'offset': [0, 0, 0],
        'position': [0, 0, 0],
        'rotation': [0, 0, 0, 1],
        'obj_main': '',
        'obj_list': [],
        'mat_list': mesh_ceil
    }
    for info_idx, param_one in used_ceil.items():
        info_one = todo_ceil[info_idx]
        info_width, info_depth = info_one['width'], info_one['depth']
        # 遍历分组
        for object_idx, object_one in enumerate(param_one['group']):
            if 'fake_id' in object_one and object_one['fake_id'].startswith('link'):
                object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                if object_size[2] > info_depth * 0.6:
                    object_one['scale'][2] = info_depth * 0.6 / object_size[2]
            else:
                group_ceiling['obj_list'].append(object_one)

    # 附着布局
    for object_one in object_wait:
        if 'relate_position' in object_one and len(object_one['relate_position']) > 0:
            plat_id, plat_pos = object_one['relate'], object_one['relate_position']
            plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            if plat_key not in object_plat_dict:
                continue
            plat_one = object_plat_dict[plat_key]
            if len(plat_one) <= 0:
                continue
            plat_pos_new, plat_ang_new = plat_one['position'], rot_to_ang(plat_one['rotation'])
            plat_pos_old, plat_ang_old = plat_pos, plat_ang_new
            plat_scale_new = plat_one['scale']
            if 'relate_rotation' in object_one and len(object_one['relate_rotation']) > 0:
                plat_ang_old = rot_to_ang(object_one['relate_rotation'])
            object_pos_old, object_ang_old = object_one['position'], rot_to_ang(object_one['rotation'])
            tmp_x, tmp_z = object_pos_old[0] - plat_pos_old[0], object_pos_old[2] - plat_pos_old[2]
            tmp_y = object_pos_old[1] - plat_pos_old[1]
            plat_ang_dlt = 0 - plat_ang_old
            add_x = tmp_z * math.sin(plat_ang_dlt) + tmp_x * math.cos(plat_ang_dlt)
            add_z = tmp_z * math.cos(plat_ang_dlt) - tmp_x * math.sin(plat_ang_dlt)
            tmp_x, tmp_z = add_x, add_z
            tmp_x *= plat_scale_new[0]
            tmp_z *= plat_scale_new[2]
            plat_ang_dlt = plat_ang_new - 0
            add_x = tmp_z * math.sin(plat_ang_dlt) + tmp_x * math.cos(plat_ang_dlt)
            add_z = tmp_z * math.cos(plat_ang_dlt) - tmp_x * math.sin(plat_ang_dlt)
            object_pos_new = [plat_pos_new[0] + add_x, plat_pos_new[1] + tmp_y, plat_pos_new[2] + add_z]
            object_ang_new = plat_ang_dlt
            object_rot_new = [0, math.sin(object_ang_new / 2), 0, math.cos(object_ang_new / 2)]
            object_one['position'] = object_pos_new[:]
            object_one['rotation'] = object_rot_new[:]
            object_one['relate'] = plat_one['id']
            object_one['relate_role'] = ''
            object_one['relate_group'] = ''
            object_one['relate_position'] = plat_one['position'][:]
            object_one['relate_rotation'] = plat_one['rotation'][:]
            # 添加信息
            group_ceiling['obj_list'].append(object_one)

    # 返回布局
    return group_ceiling


def room_rect_layout_floor(todo_floor, object_floor, mesh_floor, room_type='', room_height=UNIT_HEIGHT_WALL):
    # 分析布局
    used_floor = {}
    prior_electric, prior_lighting = ['electronics/air-conditioner - floor-based'], ['lighting/floor lamp']

    # 附着布局
    object_wait, object_plat_list, object_plat_dict = [], [], {}
    for object_idx in range(len(object_floor) - 1, -1, -1):
        object_one = object_floor[object_idx]
        relate_obj, relate_grp = '', ''
        if 'relate' in object_one:
            relate_obj = object_one['relate']
        if 'relate_group' in object_one:
            relate_grp = object_one['relate_group']
        if relate_grp == '' and not relate_obj == '':
            if 'relate_position' in object_one and len(object_one['relate_position']) > 0:
                object_wait.append(object_one)
                plat_id, plat_pos = object_one['relate'], object_one['relate_position']
                plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                object_plat_dict[plat_key] = {}
            object_floor.pop(object_idx)
        elif object_one['position'][1] > 0.1:
            object_floor.pop(object_idx)
    for object_idx in range(len(object_floor) - 1, -1, -1):
        object_one = object_floor[object_idx]
        plat_id, plat_pos = object_one['id'], object_one['position']
        plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
        if 'fake_id' in object_one and object_one['fake_id'].startswith('link'):
            plat_key = object_one['fake_id'] + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
        if plat_key in object_plat_dict:
            object_plat_list.append(object_one)
            object_floor.pop(object_idx)
    for object_one in object_plat_list:
        object_floor.insert(0, object_one)

    # 关联布局
    object_find = []
    for object_idx, object_one in enumerate(object_floor):
        relate_group, relate_role, relate_obj = '', '', ''
        if 'relate_group' in object_one:
            relate_group = object_one['relate_group']
        if 'relate_role' in object_one:
            relate_role = object_one['relate_role']
        if 'relate' in object_one:
            relate_obj = object_one['relate']
        if relate_obj == '' and relate_role == '':
            continue
        object_id, object_type, object_count = object_one['id'], object_one['type'], object_one['count']
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        object_width, object_height, object_depth = object_size[0], object_size[1], object_size[2]
        if object_count >= 3:
            continue
        if ('shelf' in object_type or 'cabinet' in object_type) and object_size[1] > 1.0:
            if 'Bathroom' in room_type:
                continue
            elif object_size[2] < 0.2 and object_size[0] > 4 * object_size[2]:
                continue
        # 最佳参数
        param_best = {'index': -1, 'score': -100, 'count': 1, 'group': [], 'relate_group': ''}
        # 矩形查找
        for info_idx, info_one in enumerate(todo_floor):
            info_type, info_group, info_object = info_one['type'], info_one['group'], info_one['object']
            info_width, info_depth, info_height = info_one['width'], info_one['depth'], info_one['height']
            if not info_type == UNIT_TYPE_GROUP:
                continue
            if not info_group == relate_group:
                continue
            relate_find = False
            if info_object == object_one['relate']:
                relate_find = True
            if relate_find:
                group_position, group_angle = info_one['center'], info_one['angle']
                if 'position' in info_one and len(info_one['position']) >= 3:
                    group_position = info_one['position']
                if object_one['normal_position'][2] > 0.2 and info_group == 'Meeting':
                    continue
                if object_one['normal_position'][2] > 0.5:
                    continue
                tmp_x = object_one['normal_position'][0] + info_one['offset'][0]
                tmp_z = object_one['normal_position'][2] + info_one['offset'][2]
                add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                new_x = group_position[0] + add_x
                new_z = group_position[2] + add_z
                new_ang = group_angle + rot_to_ang(object_one['normal_rotation'])
                p1, p2 = info_one['p1'], info_one['p2']
                d1, d2 = abs(p1[0] - new_x) + abs(p1[1] - new_z), abs(p2[0] - new_x) + abs(p2[1] - new_z)
                if max(d1, d2) < 1.0 and info_width > object_width * 0.5:
                    # 参数信息
                    param_best['index'] = info_idx
                    param_best['score'] = 10
                    param_best['count'] = 1
                    param_best['relate_group'] = info_one['group']
                    # 参数信息
                    param_add = param_best.copy()
                    object_add = copy_exist_object(object_one)
                    object_add['count'] = object_count
                    param_add['group'].append(object_add)
                    # 参数信息
                    object_add['position'][0] = new_x
                    object_add['position'][2] = new_z
                    object_add['rotation'] = [0, math.sin(new_ang / 2), 0, math.cos(new_ang / 2)]
                    param_add['relate_ready'] = 1
                    # 参数复制
                    if 'p3' in info_one:
                        swap_flag = False
                        if 'type_pre' in info_one and 'type_post' in info_one:
                            type_pre, type_post = info_one['type_pre'], info_one['type_post']
                            if type_pre in [UNIT_TYPE_SIDE] and type_post not in [UNIT_TYPE_SIDE]:
                                if object_one['normal_position'][0] > 0 and object_one['count'] <= 1:
                                    object_one['normal_position'][0] *= -1
                                    swap_flag = True
                        if swap_flag:
                            tmp_x = object_one['normal_position'][0] + info_one['offset'][0]
                            tmp_z = object_one['normal_position'][2] + info_one['offset'][2]
                            add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                            add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                            new_x = group_position[0] + add_x
                            new_z = group_position[2] + add_z
                            object_add['position'][0] = new_x
                            object_add['position'][2] = new_z
                            info_one['p1'] = info_one['p3'][:]
                            info_one['p2'] = info_one['p4'][:]
                            info_one.pop('p3')
                            info_one.pop('p4')
                        else:
                            info_add = info_one.copy()
                            info_add['p1'] = info_one['p3'][:]
                            info_add['p2'] = info_one['p4'][:]
                            info_one.pop('p3')
                            info_one.pop('p4')
                            info_add.pop('p3')
                            info_add.pop('p4')
                            todo_floor.append(info_add)
                    # 参数添加
                    index_add = int(param_add['index'])
                    if index_add not in used_floor:
                        used_floor[index_add] = []
                    used_floor[index_add].append(param_add)
                    object_find.append(object_idx)
                    break

    # 遍历布局
    for object_idx, object_one in enumerate(object_floor):
        if object_idx in object_find:
            continue
        if object_one['position'][1] > 0.1:
            continue
        object_id, object_type, object_count = object_one['id'], object_one['type'], object_one['count']
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        object_width, object_height, object_depth = object_size[0], object_size[1], object_size[2]
        if object_count >= 3:
            continue
        if max(object_size[0], object_size[1], object_size[2]) <= 0.3:
            continue
        if ('shelf' in object_type or 'cabinet' in object_type) and object_size[1] > 1.0:
            if 'Bathroom' in room_type:
                continue
            elif object_size[2] < 0.2 and object_size[0] > 4 * object_size[2]:
                continue
        # 最佳参数
        param_best = {'index': -1, 'score': -100, 'count': 1, 'group': [], 'relate_group': ''}
        # 矩形查找
        for info_idx, info_one in enumerate(todo_floor):
            if info_idx in used_floor:
                continue
            info_type, info_group = info_one['type'], info_one['group']
            info_type_pre, info_type_post = info_one['type_pre'], info_one['type_post']
            info_width, info_height, info_depth = info_one['width'], info_one['height'], info_one['depth']
            # 宽度排除
            if info_width > object_width * 0.50 and 'fake_id' in object_one and object_one['fake_id'].startswith('link'):
                pass
            elif info_width < object_width * 0.80 and info_group == '':
                continue
            elif info_width < max(object_width + MIN_GROUP_PASS * 0.0, MID_GROUP_PASS * 1.0):
                if info_type_pre in [UNIT_TYPE_NONE, UNIT_TYPE_DOOR, UNIT_TYPE_SIDE]:
                    if info_type_post in [UNIT_TYPE_NONE, UNIT_TYPE_DOOR, UNIT_TYPE_SIDE]:
                        continue
            elif info_width < max(object_width + MIN_GROUP_PASS * 4.0, MID_GROUP_PASS * 2.0):
                if info_type_pre in [UNIT_TYPE_DOOR]:
                    if info_type_post in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE]:
                        continue
                if info_type_post in [UNIT_TYPE_DOOR]:
                    if info_type_pre in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE]:
                        continue
            if info_width < object_width + MIN_GROUP_PASS * 2 and info_group == '':
                if info_type_pre in [UNIT_TYPE_GROUP, UNIT_TYPE_AISLE]:
                    if info_type_post in [UNIT_TYPE_GROUP, UNIT_TYPE_AISLE]:
                        continue
            # 深度排除
            if info_depth < object_depth * 0.8 and info_type == UNIT_TYPE_GROUP:
                continue
            elif info_depth < object_depth * 0.2 and info_type == UNIT_TYPE_WALL:
                continue
            elif object_depth > 0.2 and info_type == UNIT_TYPE_WALL:
                if info_depth < object_depth * 0.8 and info_depth < MIN_GROUP_PASS * 2:
                    continue
            elif info_type == UNIT_TYPE_AISLE:
                if object_depth > info_depth:
                    continue
                if object_depth > 0.15:
                    continue

            # 高度排除
            if info_height < object_height * 0.8 and info_type == UNIT_TYPE_WINDOW:
                continue
            if object_height <= 0.5 and info_group in ['Media']:
                continue
            # 其他排除
            if object_type in prior_electric:
                if info_group == '' or info_width < object_width:
                    continue
                if info_type_pre == UNIT_TYPE_GROUP and info_type_post == UNIT_TYPE_GROUP:
                    continue
                if info_group == 'Media' and info_width < object_width + MID_GROUP_PASS:
                    continue
            if object_type in prior_lighting:
                if info_width < object_width:
                    continue
                elif info_width < object_width + MIN_GROUP_PASS and len(info_group) <= 0:
                    continue
                if info_type_pre == info_type_post == UNIT_TYPE_WINDOW:
                    if info_width < MID_GROUP_PASS * 2:
                        continue
            # 位置分数
            score_place = 0
            if object_type in prior_electric or object_type in prior_lighting:
                if info_group in ['Meeting', 'Work', 'Rest']:
                    score_place += 2
                elif info_group in ['Media']:
                    if object_type in prior_lighting:
                        continue
                    score_place -= 2
                elif info_group in ['Cabinet']:
                    score_place += 0
                elif info_group in [''] and object_type in prior_lighting:
                    continue
                elif info_type in [UNIT_TYPE_SIDE, UNIT_TYPE_AISLE, UNIT_TYPE_WINDOW]:
                    score_place -= 2
                elif info_type_pre in [UNIT_TYPE_NONE, UNIT_TYPE_DOOR] and info_type_post in [UNIT_TYPE_NONE, UNIT_TYPE_DOOR]:
                    score_place -= 2
            else:
                if info_type in [UNIT_TYPE_SIDE, UNIT_TYPE_AISLE, UNIT_TYPE_WINDOW]:
                    score_place -= 4
                elif info_type_pre in [UNIT_TYPE_NONE, UNIT_TYPE_DOOR] and info_type_post in [UNIT_TYPE_NONE, UNIT_TYPE_DOOR]:
                    score_place -= 4
                elif info_type_pre in [UNIT_TYPE_SIDE] or info_type_post in [UNIT_TYPE_SIDE]:
                    score_place -= 2
                elif info_group in ['Meeting', 'Work', 'Rest']:
                    score_place += 2
                elif info_group in ['Media']:
                    score_place += 4
                elif info_group in ['Cabinet']:
                    score_place += 1
                else:
                    score_place -= 1
                # 两侧分数
                if UNIT_TYPE_GROUP in [info_type_pre, info_type_post]:
                    if info_width < object_width + MID_GROUP_PASS:
                        score_place -= 2
                    else:
                        score_place += 1
                elif UNIT_TYPE_SIDE in [info_type_pre, info_type_post]:
                    if info_width < object_width + MID_GROUP_PASS:
                        score_place -= 2
            if info_type_pre in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE] or info_type_post in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                score_place -= 1
                if info_type == UNIT_TYPE_AISLE:
                    score_place -= 2
            count_best = object_count
            # 数量处理
            if object_count == 2:
                if 'p3' in info_one:
                    score_place *= 2
                else:
                    count_best = 1
            # 宽度分数
            score_width = abs(info_width - object_width * 1) / info_width * 1
            if object_type in prior_electric:
                score_width = 1 - abs(info_width - object_width * 1.5) / info_width
            elif object_type in prior_lighting:
                score_width = 1 - abs(info_width - object_width * 2.0) / info_width
            # 整体分数
            score_best = score_place + score_width
            if score_best > param_best['score']:
                param_best['index'] = info_idx
                param_best['score'] = score_best
                param_best['count'] = count_best
                param_best['relate_group'] = info_one['group']
        # 参数判断
        if param_best['index'] < 0:
            continue
        # 数量重置
        info_best = todo_floor[param_best['index']]
        if object_count == 1 and 'p3' in info_best:
            if object_type in prior_lighting or object_type in prior_electric:
                pass
            elif info_best['type'] == UNIT_TYPE_GROUP and info_best['group'] == 'Media' and object_height > 1.0:
                object_count = 2
                param_best['count'] = object_count
        # 参数信息
        param_add = param_best.copy()
        object_add = copy_exist_object(object_one)
        object_add['count'] = object_count
        if 'fake_id' in object_one and object_one['fake_id'].startswith('link') and 'plants' in object_type:
            pass
        elif object_width >= info_best['width']:
            adjust_scale = info_best['width'] / object_width
            object_add['scale'][0] *= adjust_scale
            object_add['scale'][1] *= adjust_scale
            object_add['scale'][2] *= adjust_scale
            pass
        object_add['position'] = object_one['position'][:]
        object_add['rotation'] = object_one['rotation'][:]
        param_add['group'].append(object_add)
        # 参数添加
        index_add = int(param_add['index'])
        if index_add not in used_floor:
            used_floor[index_add] = []
        used_floor[index_add].append(param_add)
        # 更新墙体
        info_old = todo_floor[index_add]
        if object_count == 1 and 'p3' in info_old:
            info_add = info_old.copy()
            info_add['p1'] = info_old['p3'][:]
            info_add['p2'] = info_old['p4'][:]
            info_old.pop('p3')
            info_old.pop('p4')
            info_add.pop('p3')
            info_add.pop('p4')
            todo_floor.append(info_add)

    # 计算布局
    group_floor = {
        'type': 'Floor',
        'size': [0, 0, 0],
        'offset': [0, 0, 0],
        'position': [0, 0, 0],
        'rotation': [0, 0, 0, 1],
        'obj_main': '',
        'obj_list': [],
        'mat_list': mesh_floor
    }
    for info_idx, param_list in used_floor.items():
        # 线段信息
        info_one = todo_floor[info_idx]
        info_width, info_height = info_one['width'], info_one['height']
        info_type, info_type_pre, info_type_post = info_one['type'], info_one['type_pre'], info_one['type_post']
        info_group = info_one['group']
        info_angle = info_one['angle']
        p1, p2 = info_one['p1'], info_one['p2']
        back_depth = info_one['back_depth']
        # 遍历参数
        for param_idx, param_one in enumerate(param_list):
            object_one = param_one['group'][0]
            relate_group = param_one['relate_group']
            plat_id, plat_pos = object_one['id'], object_one['position']
            plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            # 更新信息
            if 'relate_ready' in param_one:
                pass
            else:
                # 分组信息
                object_type, object_rely = object_one['type'], ''
                origin_size, origin_scale = object_one['size'], object_one['scale']
                if 'relate_group' in object_one:
                    object_rely = object_one['relate_group']
                object_size = [origin_size[i] * origin_scale[i] / 100 for i in range(3)]
                ratio_w = object_size[0] / 2 / info_width
                width_rest = 0
                if info_type == UNIT_TYPE_GROUP:
                    if info_width - object_size[0] > MID_GROUP_PASS * 2:
                        width_rest = (info_width - object_size[0]) * 0.5
                else:
                    if info_width - object_size[0] > MID_GROUP_PASS and object_type in prior_lighting:
                        width_rest = (info_width - object_size[0]) * 0.50
                    elif info_width - object_size[0] < 0.1 and info_group == '':
                        width_rest = (info_width - object_size[0]) * 0.50
                    elif info_type_pre == info_type_post == UNIT_TYPE_GROUP:
                        width_rest = (info_width - object_size[0]) * 0.50
                    elif info_type_pre == UNIT_TYPE_GROUP:
                        width_rest = (info_width - object_size[0]) * 1.00
                        if object_type in prior_electric or object_type in prior_lighting:
                            width_rest = (info_width - object_size[0]) * 0.00
                        elif object_rely == info_group:
                            width_rest = (info_width - object_size[0]) * 0.00
                        elif info_type_post == UNIT_TYPE_SIDE:
                            width_rest = (info_width - object_size[0]) * 0.00
                        else:
                            relate_group = ''
                    elif info_type_post == UNIT_TYPE_GROUP:
                        width_rest = (info_width - object_size[0]) * 0.00
                        if object_type in prior_electric or object_type in prior_lighting:
                            width_rest = (info_width - object_size[0]) * 1.00
                        elif object_rely == info_group:
                            width_rest = (info_width - object_size[0]) * 1.00
                        elif info_type_pre == UNIT_TYPE_SIDE:
                            width_rest = (info_width - object_size[0]) * 1.00
                        else:
                            relate_group = ''
                    elif info_type_pre < info_type_post:
                        width_rest = (info_width - object_size[0]) * 1.00
                        if info_type in [UNIT_TYPE_WINDOW]:
                            width_rest -= UNIT_DEPTH_CURTAIN
                    elif info_type_pre > info_type_post:
                        width_rest = (info_width - object_size[0]) * 0.00
                        if info_type in [UNIT_TYPE_WINDOW]:
                            width_rest += UNIT_DEPTH_CURTAIN
                ratio_w += width_rest / info_width
                # 计算位置
                if back_depth < 0.01:
                    back_depth = 0.01
                if info_type in [UNIT_TYPE_WINDOW]:
                    back_depth = max(back_depth, UNIT_DEPTH_CURTAIN)
                dd = object_size[2] / 2 + back_depth
                pp = [0, 0]
                pp[0] = p1[0] * (1 - ratio_w) + p2[0] * ratio_w + dd * math.sin(info_angle)
                pp[1] = p1[1] * (1 - ratio_w) + p2[1] * ratio_w + dd * math.cos(info_angle)
                object_one['position'] = [pp[0], object_one['position'][1], pp[1]]
                object_one['rotation'] = [0, math.sin(info_angle / 2), 0, math.cos(info_angle / 2)]
            object_one['relate'] = ''
            object_one['relate_role'] = ''
            object_one['relate_group'] = relate_group
            object_one['relate_position'] = []
            # 新增分组
            group_floor['obj_list'].append(object_one)
            if plat_key in object_plat_dict:
                object_plat_dict[plat_key] = object_one
            # 重复分组
            if param_one['count'] == 2 and 'p3' in info_one:
                # 计算位置
                p1, p2 = info_one['p3'], info_one['p4']
                pp = [0, 0]
                pp[0] = p1[0] * (1 - ratio_w) + p2[0] * ratio_w + dd * math.sin(info_angle)
                pp[1] = p1[1] * (1 - ratio_w) + p2[1] * ratio_w + dd * math.cos(info_angle)
                # 更新信息
                object_new = copy_exist_object(object_one)
                object_new['position'] = [pp[0], object_one['position'][1], pp[1]]
                object_new['rotation'] = [0, math.sin(info_angle / 2), 0, math.cos(info_angle / 2)]
                if 'plants' in object_type:
                    object_new['scale'][0] *= -1
                object_new['relate'] = ''
                object_new['relate_role'] = ''
                object_new['relate_group'] = param_one['relate_group']
                object_new['relate_position'] = []
                # 新增分组
                group_floor['obj_list'].append(object_new)

    # 附着布局
    for object_one in object_wait:
        if 'relate_position' in object_one and len(object_one['relate_position']) > 0:
            plat_id, plat_pos = object_one['relate'], object_one['relate_position']
            plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            if plat_key not in object_plat_dict:
                continue
            plat_one = object_plat_dict[plat_key]
            if len(plat_one) <= 0:
                continue
            plat_pos_new, plat_ang_new = plat_one['position'], rot_to_ang(plat_one['rotation'])
            plat_pos_old, plat_ang_old = plat_pos, plat_ang_new
            if 'relate_rotation' in object_one and len(object_one['relate_rotation']) > 0:
                plat_ang_old = rot_to_ang(object_one['relate_rotation'])
            object_pos_old, object_ang_old = object_one['position'], rot_to_ang(object_one['rotation'])
            tmp_x, tmp_z = object_pos_old[0] - plat_pos_old[0], object_pos_old[2] - plat_pos_old[2]
            tmp_y = object_pos_old[1] - plat_pos_old[1]
            plat_ang_dlt = plat_ang_new - plat_ang_old
            add_x = tmp_z * math.sin(plat_ang_dlt) + tmp_x * math.cos(plat_ang_dlt)
            add_z = tmp_z * math.cos(plat_ang_dlt) - tmp_x * math.sin(plat_ang_dlt)
            object_pos_new = [plat_pos_new[0] + add_x, plat_pos_new[1] + tmp_y, plat_pos_new[2] + add_z]
            object_ang_new = object_ang_old + plat_ang_dlt
            object_rot_new = [0, math.sin(object_ang_new / 2), 0, math.cos(object_ang_new / 2)]
            object_one['position'] = object_pos_new[:]
            object_one['rotation'] = object_rot_new[:]
            object_one['relate'] = plat_one['id']
            object_one['relate_role'] = ''
            object_one['relate_group'] = ''
            object_one['relate_position'] = plat_one['position'][:]
            object_one['relate_rotation'] = plat_one['rotation'][:]
            # 添加信息
            group_floor['obj_list'].append(object_one)

    # 返回布局
    return group_floor


def room_rect_layout_door(todo_door, object_door, mesh_door, room_type='', room_height=UNIT_HEIGHT_WALL, room_dict={},
                          door_mode=1):
    used_door = []
    # 门体布局
    for info_idx, info_one in enumerate(todo_door):
        info_width, info_height, info_depth = info_one['size'][0], info_one['size'][1], info_one['size'][2]
        # 连通参数
        unit_to_room, unit_to_type = '', ''
        if 'unit_to_room' in info_one:
            unit_to_room = info_one['unit_to_room']
        if 'unit_to_type' in info_one:
            unit_to_type = info_one['unit_to_type']
        if len(unit_to_type) <= 0 and len(unit_to_room) > 0:
            if unit_to_room in room_dict:
                unit_to_type = room_dict[unit_to_room]
            else:
                unit_to_type = unit_to_room.split('-')[0]
        # 开关参数
        if not door_mode == 1:
            room_type_score = sort_room_type(room_type)
            room_unit_score = sort_room_type(unit_to_type)
            if room_type_score >= room_unit_score:
                continue
        # 部件遍历
        object_best, score_best = {}, 0
        for object_one in object_door:
            object_width = abs(object_one['size'][0] * object_one['scale'][0]) / 100
            object_height = abs(object_one['size'][1] * object_one['scale'][1]) / 100
            object_depth = abs(object_one['size'][2] * object_one['scale'][2]) / 100
            dlt = [abs(object_width - info_width), abs(object_height - info_height), abs(object_depth - info_depth)]
            score_new = 10 - dlt[0] - dlt[1] - dlt[2]
            if 'entry' in object_one['type'] and unit_to_room == '':
                score_new += 1
            if 'entry' in object_one['type'] and not unit_to_room == '':
                score_new -= 1
            if 'sliding' in object_one['type'] and info_width > 1.2:
                score_new += 2
            if 'sliding' in object_one['type'] and info_width < 1.0:
                score_new -= 2
            if score_new > score_best:
                score_best = score_new
                object_best = object_one
        # 部件判断
        if len(object_best) <= 0:
            continue
        # 开关参数
        close_pos, close_ang = [info_one['center'][0], 0, info_one['center'][1]], info_one['angle']
        open_pos, open_ang = [info_one['center_open2'][0], 0, info_one['center_open2'][1]], info_one['angle_open2']
        if unit_to_room == '':
            open_pos, open_ang = [info_one['center_open1'][0], 0, info_one['center_open1'][1]], info_one['angle_open1']
        # 参数信息
        param_add = {'size': info_one['size'][:],
                     'position': info_one['position'][:], 'rotation': info_one['rotation'][:], 'group': [],
                     'to': info_one['unit_to_room'],
                     'close_pos': close_pos, 'close_ang': close_ang, 'open_pos': open_pos, 'open_ang': open_ang,
                     'open_flag': 0}
        if room_type in ROOM_TYPE_LEVEL_1 and unit_to_type in ['Corridor']:
            pass
        elif room_type in ['Kitchen', 'Balcony', 'Terrace', 'CloakRoom', 'StorageRoom', 'OtherRoom']:
            unit_position = close_pos
            unit_rotation = [0, math.sin(close_ang / 2), 0, math.cos(close_ang / 2)]
            param_add['position'] = unit_position
            param_add['rotation'] = unit_rotation
        elif not door_mode == 1 and not unit_to_room == '' and unit_to_type not in ['Kitchen']:
            if info_width <= 1.2 and 'center_open2' in info_one:
                unit_position = open_pos
                unit_rotation = [0, math.sin(open_ang / 2), 0, math.cos(open_ang / 2)]
                param_add['position'] = unit_position
                param_add['rotation'] = unit_rotation
                param_add['open_flag'] = 1
        object_add = copy_exist_object(object_best)
        object_add['unit_to_room'] = unit_to_room
        object_add['unit_to_type'] = unit_to_type
        param_add['group'].append(object_add)
        used_door.append(param_add)
    # 计算布局
    group_door = {
        'type': 'Door',
        'size': [0, 0, 0],
        'offset': [0, 0, 0],
        'position': [0, 0, 0],
        'rotation': [0, 0, 0, 1],
        'obj_main': '',
        'obj_list': [],
        'mat_list': mesh_door
    }
    for param_one in used_door:
        param_size, param_bot = param_one['size'][:], 0
        # 遍历分组
        for object_idx, object_one in enumerate(param_one['group']):
            object_scale = [param_size[i] * 100 / object_one['size'][i] for i in range(3)]
            object_one['scale'] = object_scale[:]
            object_one['position'] = param_one['position'][:]
            object_one['rotation'] = param_one['rotation'][:]
            # 入口出口
            object_one['from'] = ''
            object_one['to'] = param_one['to']
            # 关门开门
            object_one['close_pos'] = param_one['close_pos']
            object_one['close_ang'] = param_one['close_ang']
            object_one['open_pos'] = param_one['open_pos']
            object_one['open_ang'] = param_one['open_ang']
            object_one['open_flag'] = param_one['open_flag']
            # 新增分组
            group_door['obj_list'].append(object_one)
    # 返回布局
    return group_door


def room_rect_layout_window(todo_window, todo_curtain, object_window, object_curtain, mesh_window,
                            room_type='', room_height=UNIT_HEIGHT_WALL, room_dict={}, door_mode=1):
    used_window, used_curtain = [], []
    # 附着布局
    object_wait, object_plat_list, object_plat_dict = [], [], {}
    for object_idx in range(len(object_curtain) - 1, -1, -1):
        object_one = object_curtain[object_idx]
        relate_obj, relate_grp = '', ''
        if 'relate' in object_one:
            relate_obj = object_one['relate']
        if 'relate_group' in object_one:
            relate_grp = object_one['relate_group']
        if not relate_obj == '':
            if 'relate_position' in object_one and len(object_one['relate_position']) >= 3:
                object_add = copy_exist_object(object_one)
                object_wait.append(object_add)
                plat_id, plat_pos = object_one['relate'], object_one['relate_position']
                plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                object_plat_dict[plat_key] = {}
    for object_idx in range(len(object_curtain) - 1, -1, -1):
        object_one = object_curtain[object_idx]
        plat_id, plat_pos = object_one['id'], object_one['position']
        plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
        if 'fake_id' in object_one and object_one['fake_id'].startswith('link'):
            plat_key = object_one['fake_id'] + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
        if plat_key in object_plat_dict:
            object_plat_list.append(object_one)
            object_curtain.pop(object_idx)
    for object_one in object_plat_list:
        object_curtain.insert(0, object_one)
    # 关联角度
    for object_one in object_wait:
        if 'relate_rotation' in object_one and len(object_one['relate_rotation']) >= 4:
            continue
        if 'relate_position' in object_one and len(object_one['relate_position']) >= 3:
            plat_id, plat_pos = object_one['relate'], object_one['relate_position']
            plat_key_old = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            for plat_one in object_plat_list:
                plat_id, plat_pos, plat_rot = plat_one['id'], plat_one['position'], plat_one['rotation']
                plat_key_new = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                if plat_key_old == plat_key_new:
                    object_one['relate_rotation'] = plat_one['rotation'][:]

    # 窗户布局
    for info_idx, info_one in enumerate(todo_window):
        info_width, info_height, info_depth = info_one['size'][0], info_one['size'][1], info_one['size'][2]
        # 连通参数
        unit_to_room, unit_to_type = '', ''
        if 'unit_to_room' in info_one:
            unit_to_room = info_one['unit_to_room']
        if 'unit_to_type' in info_one:
            unit_to_type = info_one['unit_to_type']
        if len(unit_to_type) <= 0 and len(unit_to_room) > 0:
            if unit_to_room in room_dict:
                unit_to_type = room_dict[unit_to_room]
            else:
                unit_to_type = unit_to_room.split('-')[0]
        # 开关参数
        if not door_mode == 1:
            room_type_score = sort_room_type(room_type)
            room_unit_score = sort_room_type(unit_to_type)
            if room_type_score >= room_unit_score:
                continue
        # 部件遍历
        object_best, score_best = {}, 0
        for object_idx, object_one in enumerate(object_window):
            object_width = abs(object_one['size'][0] * object_one['scale'][0]) / 100
            object_height = abs(object_one['size'][1] * object_one['scale'][1]) / 100
            object_depth = abs(object_one['size'][2] * object_one['scale'][2]) / 100
            dlt = [abs(object_width - info_width), abs(object_height - info_height), abs(object_depth - info_depth)]
            score_new = 10 - dlt[0] - dlt[1] - dlt[2]
            if 'entry' in object_one['type'] and unit_to_room == '':
                score_new += 1
            if 'entry' in object_one['type'] and not unit_to_room == '':
                score_new -= 1
            if 'sliding' in object_one['type'] and info_width > 1.2:
                score_new += 2
            if 'sliding' in object_one['type'] and info_width < 1.0:
                score_new -= 2
            if score_new > score_best:
                score_best = score_new
                object_best = object_one
        # 部件判断
        if len(object_best) <= 0:
            continue
        # 参数信息
        param_add = {'size': info_one['size'][:],
                     'position': info_one['position'][:], 'rotation': info_one['rotation'][:], 'group': [],
                     'to': info_one['unit_to_room']}
        object_add = copy_exist_object(object_best)
        object_add['unit_to_room'] = unit_to_room
        object_add['unit_to_type'] = unit_to_type
        param_add['group'].append(object_add)
        used_window.append(param_add)
    # 窗帘布局
    for info_idx, info_one in enumerate(todo_curtain):
        info_width, info_height, info_depth = info_one['size'][0], info_one['size'][1], info_one['size'][2]
        object_best, score_best, index_best = {}, 0, -1
        for object_idx, object_one in enumerate(object_curtain):
            if object_one['size'][0] / 100 > 2 > info_width and 'Bathroom' in room_type:
                continue
            # delta 1
            object_width = abs(object_one['size'][0] * object_one['scale'][0]) / 100
            object_height = abs(object_one['size'][1] * object_one['scale'][1]) / 100
            object_depth = abs(object_one['size'][2] * object_one['scale'][2]) / 100
            dlt_1 = [abs(object_width - info_width), abs(object_height - info_height), abs(object_depth - info_depth)]
            # delta 2
            origin_width = abs(object_one['size'][0] * 1) / 100
            origin_height = abs(object_one['size'][1] * 1) / 100
            origin_depth = abs(object_one['size'][2] * 1) / 100
            dlt_2 = [abs(origin_width - info_width), abs(origin_height - info_height), abs(origin_depth - info_depth)]
            # delta f
            dlt = dlt_1
            if dlt_1[0] + dlt_1[1] + dlt_1[2] > dlt_2[0] + dlt_2[1] + dlt_2[2]:
                dlt = dlt_2
            if room_type in ROOM_TYPE_LEVEL_3 and info_width < 3 and 'width_original' in info_one:
                dlt = [abs(object_width - info_one['width_original']), 0, 0]
            # score
            score_new = 10 - dlt[0] - dlt[1] - dlt[2]
            if info_width >= 3 and object_width >= 2:
                if 'fake_id' in object_one and object_one['fake_id'].startswith('link'):
                    score_new += 2
            if score_new > score_best:
                score_best = score_new
                object_best = object_one
                index_best = object_idx
        # 参数判断
        if len(object_best) <= 0:
            continue
        # 新建信息
        object_add = copy_exist_object(object_best)
        # 附着信息
        if 'fake_id' in object_add and object_add['fake_id'].startswith('link'):
            plat_id_old, plat_pos = object_add['id'], object_add['position']
            plat_key_old = object_add['fake_id'] + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            plat_id_new = 'link_%d' % info_idx
            plat_key_new = plat_id_new + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            object_wait_set = []
            for object_wait_one in object_wait:
                if 'relate_position' in object_wait_one and len(object_wait_one['relate_position']) > 0:
                    plat_id, plat_pos = object_wait_one['relate'], object_wait_one['relate_position']
                    plat_key_one = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
                    if plat_key_one == plat_key_old:
                        object_wait_add = copy_exist_object(object_wait_one)
                        object_wait_add['relate'] = plat_id_new
                        object_wait_set.append(object_wait_add)
            object_add['id'] = plat_id_new
            for object_wait_one in object_wait_set:
                object_wait.append(object_wait_one)
            object_plat_dict[plat_key_new] = object_add
        # 参数信息
        if object_add['position'][1] > room_height - info_height:
            object_add['position'][1] = room_height - info_height
        # 添加信息
        param_add = info_one.copy()
        param_add['group'] = [object_add]
        used_curtain.append(param_add)

    # 计算布局
    group_window = {
        'type': 'Window',
        'size': [0, 0, 0],
        'offset': [0, 0, 0],
        'position': [0, 0, 0],
        'rotation': [0, 0, 0, 1],
        'obj_main': '',
        'obj_list': [],
        'mat_list': mesh_window
    }
    for param_one in used_window:
        param_size, param_bot = param_one['size'][:], 0
        # 遍历分组
        for object_idx, object_one in enumerate(param_one['group']):
            object_scale = [param_size[i] * 100 / object_one['size'][i] for i in range(3)]
            object_one['scale'] = object_scale[:]
            object_one['position'] = param_one['position'][:]
            object_one['rotation'] = param_one['rotation'][:]
            # 入口出口
            object_one['from'] = ''
            object_one['to'] = param_one['to']
            # 新增分组
            group_window['obj_list'].append(object_one)
    for param_one in used_curtain:
        param_size, param_bot = param_one['size'][:], 0
        if 'bottom' in param_one:
            param_bot = param_one['bottom']
        # 遍历分组
        for object_idx, object_one in enumerate(param_one['group']):
            plat_id, plat_pos = object_one['id'], object_one['position']
            plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            # 更新信息
            object_scale = [param_size[i] * 100 / object_one['size'][i] for i in range(3)]
            object_scale[2] = (param_size[2] - UNIT_DEPTH_WINDOW_FRAME * 2) * 100 / object_one['size'][2]
            object_one['scale'] = object_scale[:]
            object_one['position'] = param_one['position'][:]
            object_one['rotation'] = param_one['rotation'][:]
            # 厚度调整
            if object_scale[2] > 2:
                tmp_x, tmp_z = 0, object_one['size'][2] / 200 - param_size[2] / 2 + UNIT_DEPTH_WINDOW_FRAME
                ang = rot_to_ang(param_one['rotation'])
                add_x = tmp_z * math.sin(ang) + tmp_x * math.cos(ang)
                add_z = tmp_z * math.cos(ang) - tmp_x * math.sin(ang)
                object_one['scale'][2] = 1
                object_one['position'][0] += add_x
                object_one['position'][2] += add_z
            # 高度调整
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_pos, object_top = object_one['position'], room_height - 0.15
            if param_bot >= 0.1:
                if param_size[0] <= 1.2:
                    object_pos[1] = param_bot
                elif param_size[0] < 2.0 and ('Bathroom' in room_type or 'Kitchen' in room_type):
                    object_pos[1] = param_bot
            elif param_bot <= 0.2:
                object_pos[1] = 0
            if object_pos[1] + object_size[1] > object_top:
                scale_y = (object_top - object_pos[1]) / (object_one['size'][1] / 100)
                object_one['scale'][1] = scale_y
                object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            # 新增分组
            if 'fake_id' in object_one and object_one['fake_id'].startswith('link'):
                pass
            else:
                group_window['obj_list'].append(object_one)
            if plat_key in object_plat_dict:
                object_plat_dict[plat_key] = object_one

    # 附着布局
    curtain_face = {}
    for object_old in object_wait:
        object_one = object_old
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        if 'relate_position' in object_old and len(object_old['relate_position']) > 0:
            plat_id, plat_pos = object_old['relate'], object_old['relate_position']
            plat_key = plat_id + '_%.2f_%.2f' % (plat_pos[0], plat_pos[2])
            if plat_key not in object_plat_dict:
                continue
            plat_one = object_plat_dict[plat_key]
            if len(plat_one) <= 0:
                continue
            plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
            plat_pos_new, plat_ang_new = plat_one['position'], rot_to_ang(plat_one['rotation'])
            plat_pos_old, plat_ang_old = plat_pos, plat_ang_new
            plat_scale_new = plat_one['scale']
            if 'relate_rotation' in object_one and len(object_one['relate_rotation']) > 0:
                plat_ang_old = rot_to_ang(object_one['relate_rotation'])
            object_pos_old, object_ang_old = object_one['position'], rot_to_ang(object_one['rotation'])
            tmp_x, tmp_z = object_pos_old[0] - plat_pos_old[0], object_pos_old[2] - plat_pos_old[2]
            tmp_y = object_pos_old[1] - plat_pos_old[1]
            plat_ang_dlt = 0 - plat_ang_old
            add_x = tmp_z * math.sin(plat_ang_dlt) + tmp_x * math.cos(plat_ang_dlt)
            add_z = tmp_z * math.cos(plat_ang_dlt) - tmp_x * math.sin(plat_ang_dlt)
            if add_x < -0.1:
                if plat_key not in curtain_face:
                    curtain_face[plat_key] = [[], []]
                curtain_face[plat_key][0].append(object_one)
            if add_x > 0.1:
                if plat_key not in curtain_face:
                    curtain_face[plat_key] = [[], []]
                curtain_face[plat_key][1].append(object_one)
            tmp_x, tmp_z = add_x, add_z
            if abs(tmp_x) < min(object_size[0] * plat_scale_new[0] * 0.2, plat_size[0] * 0.2):
                tmp_x = 0
            if abs(tmp_z) <= 0.02:
                tmp_z = 0
            plat_ang_dlt = plat_ang_new - 0
            add_x = tmp_z * math.sin(plat_ang_dlt) + tmp_x * math.cos(plat_ang_dlt)
            add_z = tmp_z * math.cos(plat_ang_dlt) - tmp_x * math.sin(plat_ang_dlt)
            add_y = tmp_y
            add_x *= plat_scale_new[0]
            add_z *= plat_scale_new[0]
            add_y *= plat_scale_new[1]
            object_pos_new = [plat_pos_new[0] + add_x, plat_pos_new[1] + add_y, plat_pos_new[2] + add_z]
            object_ang_new = plat_ang_dlt
            object_rot_new = [0, math.sin(object_ang_new / 2), 0, math.cos(object_ang_new / 2)]
            object_one['scale'][0] *= plat_scale_new[0]
            object_one['scale'][1] *= plat_scale_new[1]
            object_one['position'] = object_pos_new[:]
            object_one['rotation'] = object_rot_new[:]
            object_one['relate'] = plat_one['id']
            object_one['relate_role'] = ''
            object_one['relate_group'] = ''
            object_one['relate_position'] = plat_one['position'][:]
            object_one['relate_rotation'] = plat_one['rotation'][:]
            # 添加信息
            group_window['obj_list'].append(object_one)
    # 对称翻转
    for plat_key, plat_set in curtain_face.items():
        if len(plat_set) < 2:
            continue
        side_list_1, side_list_2 = plat_set[0], plat_set[1]
        for side_1 in side_list_1:
            for side_2 in side_list_2:
                if not side_1['id'] == side_2['id']:
                    continue
                ang_1 = rot_to_ang(side_1['rotation'])
                ang_2 = rot_to_ang(side_2['rotation'])
                if abs(ang_to_ang(ang_1 - ang_2)) <= 0.1:
                    ang_2_new = ang_to_ang(ang_2 + math.pi)
                    side_2['rotation'] = [0, math.sin(ang_2_new / 2), 0, math.cos(ang_2_new / 2)]

    # 返回布局
    return group_window


def room_rect_layout_back(todo_back, object_back, mesh_back, room_type='', room_height=UNIT_HEIGHT_WALL):
    # 背景布局 TODO:

    # 计算布局
    group_background = {
        'type': 'Background',
        'size': [0, 0, 0],
        'offset': [0, 0, 0],
        'position': [0, 0, 0],
        'rotation': [0, 0, 0, 1],
        'obj_main': '',
        'obj_list': [],
        'mat_list': mesh_back
    }
    # 返回布局
    return group_background


# 并列排序
def sort_aside_object(object_wall, object_tied):
    object_sort = []
    for object_idx in object_tied:
        object_one = object_wall[object_idx]
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        object_angle = rot_to_ang(object_one['normal_rotation'])
        object_pos_idx = 0
        if abs(object_angle + math.pi / 2) < 0.1 or abs(object_angle - math.pi / 2) < 0.1:
            object_pos_idx = 2
        score_new = object_size[0] + object_one['normal_position'][object_pos_idx]
        index_new = -1
        for index_old, index_obj in enumerate(object_sort):
            object_old = object_wall[index_obj]
            object_size = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
            score_old = object_size[0] + object_size[2] - abs(object_old['normal_position'][object_pos_idx])
            if score_new > score_old:
                index_new = index_old
                break
        if 0 <= index_new < len(object_sort):
            object_sort.insert(index_new, object_idx)
        else:
            object_sort.append(object_idx)
    return object_sort


# 并列调整
def move_aside_object(wall_info, object_wall, object_tied):
    # 墙面信息
    info_width, info_depth, info_edge = wall_info['width'], wall_info['depth'], wall_info['unit_edge']
    # 调整角度
    object_ang, object_pos_i = 0, 0
    if len(object_tied) > 0:
        object_idx = object_tied[0]
        object_one = object_wall[object_idx]
        if 'normal_rotation' in object_one:
            object_ang = rot_to_ang(object_one['normal_rotation'])
        if info_edge in [0, 2]:
            object_pos_i = 0
            if abs(object_ang - 0) < 0.1 or abs(object_ang - math.pi) < 0.1:
                pass
            elif abs(object_ang + math.pi / 2) < 0.1 or abs(object_ang - math.pi / 2) < 0.1:
                for object_idx in object_tied:
                    object_one = object_wall[object_idx]
                    normal_pos = object_one['normal_position'][:]
                    normal_pos[0] = normal_pos[2]
                    normal_pos[2] = -info_depth / 2
                    object_one['normal_position'] = normal_pos[:]
                    object_one['normal_rotation'] = [0, 0, 0, 1]
            else:
                return []
        elif info_edge in [1, 3]:
            object_pos_i = 2
            if abs(object_ang - 0) < 0.1 or abs(object_ang - math.pi) < 0.1:
                for object_idx in object_tied:
                    object_one = object_wall[object_idx]
                    normal_pos = object_one['normal_position'][:]
                    normal_pos[2] = normal_pos[0]
                    normal_pos[0] = -info_depth / 2
                    object_one['normal_position'] = normal_pos[:]
                    object_one['normal_rotation'] = [0, 0.70711, 0, 0.70711]
            elif abs(object_ang + math.pi / 2) < 0.1 or abs(object_ang - math.pi / 2) < 0.1:
                pass
            else:
                return []
    # 调整保持
    object_keep = False
    if len(object_tied) > 0:
        object_idx = object_tied[0]
        object_one = object_wall[object_idx]
        if 'relate' in object_one and 'object' in wall_info:
            if object_one['relate'] == wall_info['object']:
                object_keep = True
    # 调整居中
    if len(object_tied) >= 2 and not object_keep:
        best_idx, best_val = -1, -10
        for object_idx in object_tied:
            object_one = object_wall[object_idx]
            object_width = abs(object_one['size'][0] * object_one['scale'][0]) / 100
            object_val = object_width - abs(object_one['normal_position'][object_pos_i])
            if object_val > best_val:
                best_idx, best_val = object_idx, object_val
        if 0 <= best_idx < len(object_wall):
            object_one = object_wall[best_idx]
            object_pos_add = -object_one['normal_position'][object_pos_i]
        for object_idx in object_tied:
            object_one = object_wall[object_idx]
            object_one['normal_position'][object_pos_i] += object_pos_add
    # 判断宽度
    object_move = []
    for object_idx in object_tied:
        object_one = object_wall[object_idx]
        object_width = abs(object_one['size'][0] * object_one['scale'][0]) / 100
        object_pos_x = object_one['normal_position'][object_pos_i]
        min_x, max_x = object_pos_x - object_width / 2, object_pos_x + object_width / 2
        if -info_width / 2 - 0.02 < min_x < max_x < info_width / 2 + 0.02:
            object_move.append(object_idx)
        elif -info_width / 2 - 0.20 < min_x < max_x < info_width / 2 + 0.20:
            if len(object_tied) <= 1:
                object_move.append(object_idx)
            elif min_x < -info_width / 2:
                max_x_new = info_width / 2
                for side_idx in object_tied:
                    side_one = object_wall[side_idx]
                    side_width = abs(side_one['size'][0] * side_one['scale'][0]) / 100
                    side_pos_x = side_one['normal_position'][object_pos_i]
                    side_min_x, side_max_x = side_pos_x - side_width / 2, side_pos_x + side_width / 2
                    if max_x < side_min_x < max_x_new:
                        max_x_new = side_min_x
                if max_x_new - max_x > -info_width / 2 - min_x:
                    object_one['normal_position'][object_pos_i] += min(max_x_new - max_x, -info_width / 2 - min_x + 0.1)
                    object_move.append(object_idx)
            elif max_x > info_width / 2:
                min_x_new = -info_width / 2
                for side_idx in object_tied:
                    side_one = object_wall[side_idx]
                    side_width = abs(side_one['size'][0] * side_one['scale'][0]) / 100
                    side_pos_x = side_one['normal_position'][object_pos_i]
                    side_min_x, side_max_x = side_pos_x - side_width / 2, side_pos_x + side_width / 2
                    if min_x > side_max_x > min_x_new:
                        min_x_new = side_max_x
                if min_x - min_x_new > max_x - info_width / 2:
                    object_one['normal_position'][object_pos_i] -= min(min_x - min_x_new, max_x - info_width / 2 + 0.1)
                    object_move.append(object_idx)
    # 返回结果
    return object_move


# 数据拷贝
def copy_exist_object(object_one):
    object_new = object_one.copy()
    object_new['size'] = object_one['size'][:]
    object_new['scale'] = object_one['scale'][:]
    object_new['position'] = object_one['position'][:]
    object_new['rotation'] = object_one['rotation'][:]
    if 'origin_position' in object_one:
        object_new['origin_position'] = object_one['origin_position'][:]
    if 'origin_rotation' in object_one:
        object_new['origin_rotation'] = object_one['origin_rotation'][:]
    if 'normal_position' in object_one:
        object_new['normal_position'] = object_one['normal_position'][:]
    if 'normal_rotation' in object_one:
        object_new['normal_rotation'] = object_one['normal_rotation'][:]
    if 'relate_position' in object_one:
        object_new['relate_position'] = object_one['relate_position'][:]
    return object_new


# 排序房间
def sort_room_type(room_type):
    room_prior = 0
    if room_type in ['Kitchen']:
        room_prior = 1000
    elif room_type in ['LivingDiningRoom', 'LivingRoom']:
        room_prior = 900
    elif room_type in ['DiningRoom']:
        room_prior = 800
    elif room_type in ['Library']:
        room_prior = 700
    elif room_type in ['Hallway', 'Aisle', 'Corridor', 'Stairwell']:
        room_prior = 600
    elif room_type in ROOM_TYPE_LEVEL_2:
        room_prior = 500
    elif room_type in ROOM_TYPE_LEVEL_3:
        room_prior = 200

    return room_prior
