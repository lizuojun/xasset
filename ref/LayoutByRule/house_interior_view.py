# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2020-05-12
@Description: 全屋布局机位 全屋布局点位

"""

from Furniture.furniture_group import *

# 部件参数
UNIT_TYPE_NONE = 0
UNIT_TYPE_GROUP = 1
UNIT_TYPE_DOOR = 2
UNIT_TYPE_SIDE = 3
UNIT_TYPE_WINDOW = 4
UNIT_TYPE_AISLE = 5
UNIT_TYPE_WALL = 6
# 部件参数
UNIT_WIDTH_DOOR = 0.85
UNIT_WIDTH_DODGE = 0.85
UNIT_DEPTH_DODGE = 0.85
UNIT_DEPTH_CURTAIN = 0.23
# 部件参数
UNIT_HEIGHT_WALL = 2.80
UNIT_HEIGHT_CEIL = 0.15
UNIT_HEIGHT_VIEW_MIN = 1.00
UNIT_HEIGHT_VIEW_MID = 1.25
UNIT_HEIGHT_VIEW_MAX = 1.50

# 默认视角
DEFAULT_SCENE_INFO = {
    "id": "000001",
    "type": "",
    "aabb": (-1, -0.5, 1, 0.5),
    "center": (0, 0),
    "height": 1.0,
    "camera": {
        "aspect": 1.0, "pitch": 0, "fov": 60, "near": 0.1, "far": 1000,
        "up": [0, 1, 0],
        "pos": [0, 1.1, 3.0],
        "target": [0, 1.1, 2]
    },
    "normal": [0, 0, 1]
}
# 房间级别
ROOM_TYPE_LEVEL_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library']
ROOM_TYPE_LEVEL_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']

# 机位模式
VIEW_MODE_SINGLE = 0
VIEW_MODE_SPHERE = 1
# 点位模式
PATH_MODE_WANDER = 0


# 布局机位
def room_rect_view(room_info, layout_info, view_mode=0):
    # 调试信息
    if '4459' in room_info['id'] and True:
        print('layout view:', room_info['id'], 'debug')
    room_type, room_area = '', 0
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    furniture_list, decorate_list = [], []
    if 'furniture_info' in room_info:
        furniture_list = room_info['furniture_info']
    if 'decorate_info' in room_info:
        decorate_list = room_info['decorate_info']
    # 更新视角
    scheme_list = []
    if 'layout_scheme' in layout_info:
        scheme_list = layout_info['layout_scheme']
    if len(scheme_list) <= 0:
        group_fake = {'type': 'Wall', 'size': [1, 1, 1], 'offset': [0, 0, 0], 'position': [0, 0, 0], 'rotation':[0, 0, 0, 1], 'obj_list': []}
        scheme_fake = {'group': [group_fake]}
        scheme_list = [scheme_fake]
    scene_best = {}
    for scheme_idx, scheme_one in enumerate(scheme_list):
        scene_list, scene_info = [], {}
        if 'scene' in scheme_one and len(scheme_one['scene']) > 0:
            scene_info = scheme_one['scene'][0]
        elif room_area >= 2:
            scene_info = room_copy_view(DEFAULT_SCENE_INFO)
        else:
            scheme_one['scene'] = scene_list
            continue
        if len(scene_info) <= 0:
            scene_info = room_copy_view(DEFAULT_SCENE_INFO)
        else:
            scene_info = room_copy_view(scene_info)
        scene_type = ''
        # 原有视角
        scene_bbox, scene_height, scene_center, scene_normal = [-1, -0.5, 1, 0.5], 1, [0, 0, 0], [0, 0, 1]
        if 'aabb' in scene_info:
            scene_bbox = scene_info['aabb']
        if 'height' in scene_info:
            scene_height = scene_info['height']
        if 'center' in scene_info:
            scene_center = scene_info['center']
        if 'normal' in scene_info:
            scene_normal = scene_info['normal']

        # 组合分类
        group_list, group_zone = scheme_one['group'], []
        group_main, group_face, group_side, group_wait = {}, {}, {}, []
        # 主要分组
        for group_idx, group_one in enumerate(group_list):
            group_type, group_size = group_one['type'], group_one['size']
            # 主要组合
            if group_type in ['Meeting', 'Dining', 'Bed']:
                pass
            elif group_type in ['Bath'] and room_type in ['Bathroom', 'MasterBathroom', 'SecondBathroom']:
                pass
            elif group_type in ['Work'] and room_type in ['Library']:
                pass
            elif group_type in ['Work', 'Rest'] and room_type in ['Balcony', 'Terrace']:
                pass
            elif group_type in ['Armoire', 'Cabinet'] and group_size[0] > 0.5 and group_size[2] > 0.1:
                group_wait.append(group_one)
                continue
            elif group_type in ['Rest', 'Toilet']:
                group_wait.append(group_one)
                continue
            elif group_type in ['Wall']:
                if room_type in ['Kitchen'] and len(furniture_list) + len(decorate_list) <= 1:
                    continue
                if len(group_main) <= 0:
                    if len(group_wait) > 0:
                        group_main = group_wait[0]
                    else:
                        group_main = group_one
                continue
            else:
                continue
            if len(group_main) <= 0:
                group_main = group_one
            group_dict = {'main': group_one, 'face': {}, 'side': {}}
            group_zone.append(group_dict)
        if len(group_main) <= 0:
            continue
        elif len(group_zone) <= 0:
            group_zone = [{'main': group_main, 'face': {}, 'side': {}}]
        # 其他分组
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type in ['Media', 'Cabinet', 'Armoire', 'Work', 'Toilet']:
                pass
            else:
                continue
            group_pos_new, group_ang_new = group_one['position'], rot_to_ang(group_one['rotation'])
            for group_dict in group_zone:
                group_old = group_dict['main']
                if group_one == group_old:
                    break
                group_type_old = group_old['type']
                if group_type_old in ['Cabinet', 'Armoire']:
                    break
                group_pos_old, group_ang_old = group_old['position'], rot_to_ang(group_old['rotation'])
                dlt_x, dlt_z = group_pos_new[0] - group_pos_old[0], group_pos_new[2] - group_pos_old[2]
                tmp_x = dlt_z * math.sin(-group_ang_old) + dlt_x * math.cos(-group_ang_old)
                tmp_z = dlt_z * math.cos(-group_ang_old) - dlt_x * math.sin(-group_ang_old)
                if group_type in ['Media'] and abs(ang_to_ang(group_ang_old + math.pi - group_ang_new)) < 0.1:
                    if abs(tmp_x) < 2 and abs(tmp_z) < 6:
                        group_face = group_one
                        group_dict['face'] = group_face
                        break
                elif group_type in ['Toilet'] and len(group_main) > 0 and len(group_side) <= 0:
                    group_side = group_one
                    size_new = group_one['size']
                    if len(group_dict['side']) > 0:
                        size_old = group_dict['side']['size']
                        if size_old[0] + size_old[1] + size_old[2] > size_new[0] + size_new[1] + size_new[2]:
                            group_side = group_dict['side']
                    group_dict['side'] = group_side
                elif group_type in ['Cabinet', 'Armoire', 'Work']:
                    if abs(tmp_x) < 1 and 0 < tmp_z < 3 and group_one['size'][1] > 1 \
                            and group_type_old not in ['Bath', 'Toilet']:
                        if abs(tmp_x) > 0.2 and abs(tmp_x) > group_one['size'][0] / 2:
                            pass
                        else:
                            group_face = group_one
                            group_dict['face'] = group_face
                            break
                    if abs(tmp_x) + abs(tmp_z) < 10:
                        size_new = group_one['size']
                        if group_type_old in ['Bath', 'Toilet'] and size_new[0] < 0.5:
                            continue
                        group_side = group_one
                        if len(group_dict['side']) > 0:
                            size_old = group_dict['side']['size']
                            if size_old[0] + size_old[1] + size_old[2] > size_new[0] + size_new[1] + size_new[2]:
                                group_side = group_dict['side']
                        group_dict['side'] = group_side
                        break

        # 初始机位
        if len(group_main) <= 0:
            continue
        elif len(group_zone) <= 0:
            group_zone = [{'main': group_main, 'face': {}, 'side': {}}]
        if 'camera' not in scene_info:
            continue
        group_size = group_main['size']
        dis, ang = xyz_to_ang(0, 0, scene_normal[0], scene_normal[2])
        # 原有位置
        ang_old = ang
        pos_old_0 = [0, 0]
        if len(scene_center) >= 2:
            pos_old_0 = [scene_center[0], 0, scene_center[1]]
        elif len(scene_bbox) >= 4:
            pos_old_0 = [scene_bbox[0] / 2 + scene_bbox[2] / 2, 0, scene_bbox[1] / 2 + scene_bbox[3] / 2]
        pos_old_1 = scene_info['camera']['pos']
        pos_old_2 = scene_info['camera']['target']
        # 更新位置
        pos_new_0 = group_main['position']
        ang_new = rot_to_ang(group_main['rotation'])
        if 'obj_list' in group_main and len(group_main['obj_list']) > 0:
            object_one = group_main['obj_list'][0]
            object_pos = object_one['position']
            pos_new_0 = [object_pos[0], 0, object_pos[2]]
        # 相机位置
        ang_dlt = ang_new - ang_old
        tmp_x, tmp_z = pos_old_1[0] - pos_old_0[0], pos_old_1[2] - pos_old_0[2]
        add_x = tmp_z * math.sin(ang_dlt) + tmp_x * math.cos(ang_dlt)
        add_z = tmp_z * math.cos(ang_dlt) - tmp_x * math.sin(ang_dlt)
        pos_new_1 = [pos_new_0[0] + add_x, pos_old_1[1], pos_new_0[2] + add_z]
        # 目标位置
        tmp_x, tmp_z = pos_old_2[0] - pos_old_0[0], pos_old_2[2] - pos_old_0[2]
        add_x = tmp_z * math.sin(ang_dlt) + tmp_x * math.cos(ang_dlt)
        add_z = tmp_z * math.cos(ang_dlt) - tmp_x * math.sin(ang_dlt)
        pos_new_2 = [pos_new_0[0] + add_x, pos_old_2[1], pos_new_0[2] + add_z]
        # 更新机位
        scene_info['camera']['pos'] = pos_new_1[:]
        scene_info['camera']['target'] = pos_new_2[:]
        # 更新位置
        scene_info['center'] = (pos_new_0[0], pos_new_0[2])
        scene_info['height'] = group_size[1]
        scene_rect = compute_furniture_rect(group_main['size'], group_main['position'], group_main['rotation'])
        scene_x_min = min(scene_rect[0], scene_rect[2], scene_rect[4], scene_rect[6])
        scene_x_max = max(scene_rect[0], scene_rect[2], scene_rect[4], scene_rect[6])
        scene_z_min = min(scene_rect[1], scene_rect[3], scene_rect[5], scene_rect[7])
        scene_z_max = max(scene_rect[1], scene_rect[3], scene_rect[5], scene_rect[7])
        scene_aabb = (scene_x_min, scene_z_min, scene_x_max, scene_z_max)
        scene_info['aabb'] = scene_aabb
        scene_angle = rot_to_ang(group_main['rotation'])
        scene_normal = [round(math.sin(scene_angle), 4), 0, round(math.cos(scene_angle), 4)]
        scene_info['normal'] = scene_normal
        pass

        # 机位列表
        scene_list_single, scene_list_sphere = [], []
        for group_dict in group_zone:
            group_main, group_face, group_side = group_dict['main'], group_dict['face'], group_dict['side']
            type_main, type_face, type_side = '', '', ''
            size_main, size_face, size_side = [], [], []
            if len(group_main) > 0:
                type_main, size_main = group_main['type'], group_main['size']
            if len(group_face) > 0:
                type_face, size_face = group_face['type'], group_face['size']
            if len(group_side) > 0:
                type_side, size_side = group_side['type'], group_side['size']
            # 主要组合
            if len(group_main) > 0:
                if type_main in ['Wall']:
                    if room_type in ['Kitchen']:
                        if view_mode == VIEW_MODE_SINGLE and len(furniture_list) + len(decorate_list) <= 0:
                            continue
                    elif view_mode == VIEW_MODE_SINGLE:
                        continue
                elif type_main in ['Meeting']:
                    pass
                elif type_main in ['Bed', 'Armoire', 'Cabinet']:
                    if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'CloakRoom']:
                        if view_mode == VIEW_MODE_SINGLE and room_area <= 5:
                            continue
                    elif room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
                        if view_mode == VIEW_MODE_SINGLE and room_area <= 5:
                            continue
                        if size_main[0] * size_main[2] >= room_area / 4:
                            continue
                elif type_main in ['Rest']:
                    if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'CloakRoom']:
                        if view_mode == VIEW_MODE_SINGLE:
                            continue
                elif type_main in ['Bath', 'Toilet']:
                    if 'code' in group_main and group_main['code'] > 1100:
                        pass
                    elif room_area <= 4:
                        if len(size_side) > 0 and size_side[0] > 0.6:
                            group_main, group_side = group_dict['side'], group_dict['main']
                        else:
                            continue
                    elif type_main in ['Toilet'] and len(group_side) > 0:
                        group_main, group_side = group_dict['side'], group_dict['main']
                    elif max(size_main[0], size_main[2]) < 1.5 and len(group_side) > 0:
                        group_main, group_side = group_dict['side'], group_dict['main']
                    elif size_main[2] > min(size_main[0] * 1.5, 1.0) and len(group_side) > 0:
                        group_main, group_side = group_dict['side'], group_dict['main']
                elif 'Bathroom' in room_type:
                    continue
                scene_main = room_copy_view(DEFAULT_SCENE_INFO)
                scene_list = room_calc_view(room_info, scene_main, group_main, group_side, group_face, view_mode)
                if len(scene_list) > 0:
                    for scene_one in scene_list:
                        scene_list_single.append(scene_one)
                    scene_list_sphere.append(scene_list[0])
                if len(scene_best) <= 0:
                    scene_best = scene_main
            # 对面组合
            if len(group_face) > 0 and type_main in ['Meeting']:
                scene_face = room_copy_view(DEFAULT_SCENE_INFO)
                scene_list = room_calc_view(room_info, scene_face, group_face, {}, group_main, view_mode)
                if len(scene_list) > 0:
                    scene_list_single.append(scene_list[0])
            # 次要组合
            if len(group_side) > 0 and type_side in ['Armoire', 'Cabinet', 'Work'] and (room_type in ROOM_TYPE_LEVEL_2 or room_type in ['Library']):
                scene_side = room_copy_view(DEFAULT_SCENE_INFO)
                scene_list = room_calc_view(room_info, scene_side, group_side, group_main, {}, view_mode)
                if len(scene_list) > 0:
                    scene_list_single.append(scene_list[0])

        # 添加机位
        scheme_one['scene'] = scene_list_sphere
        scheme_one['scene_single'] = scene_list_single
        scheme_one['scene_sphere'] = scene_list_sphere
        # 穿模检测
        if view_mode == VIEW_MODE_SINGLE:
            scheme_one['scene'] = scene_list_single
            for scene_one in scene_list_single:
                room_mark_soft(room_info, scheme_one, scene_one)

    # 返回信息
    return scene_best


# 布局点位
def room_rect_path(room_info, layout_info, path_mode=-1, path_step=1.5):
    # 调试信息
    if '3993' in room_info['id'] and True:
        print('layout path:', room_info['id'], 'debug')
    # 返回信息
    route_entry, route_aisle, route_group = [], [], []
    wander_best = {}

    # 房间信息
    room_type, room_area = '', 0
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    door_link, line_list = [], []
    if 'door_link' in room_info:
        door_link = room_info['door_link']
    if 'line_unit' in room_info:
        line_list = room_info['line_unit']

    # 进门路线
    if len(door_link) >= 2 and len(line_list) > 0:
        # 检测路线
        for line_idx, line_one in enumerate(line_list):
            # 类型
            line_type, line_width, line_depth = line_one['type'], line_one['width'], line_one['depth']
            if line_type in [UNIT_TYPE_DOOR]:
                pass
            elif line_type in [UNIT_TYPE_AISLE] and line_width < UNIT_WIDTH_DOOR * 2 and line_depth > 5:
                pass
            else:
                continue
            score_pre, score_post = 4, 1
            # 点位
            p1, p2 = line_one['p1'], line_one['p2']
            if 'p1_original' in line_one:
                p1 = line_one['p1_original']
            if 'p2_original' in line_one:
                p2 = line_one['p2_original']
            x1, z1 = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            door_width, door_score, door_first, door_aisle, door_room = line_one['width'], line_one['score'], False, False, ''

            # 进门
            if abs(x1 - door_link[0]) + abs(z1 - door_link[1]) < 0.2:
                door_first = True
            elif door_width < UNIT_WIDTH_DOOR * 0.8 and door_score >= 6:
                continue
            elif door_width < UNIT_WIDTH_DOOR * 1.5:
                door_first = False
            if 'unit_to_type' in line_one:
                door_room = line_one['unit_to_type']
            if door_room in ['Balcony', 'Terrace']:
                continue
            # 前序走道
            side_width_1, side_dir = 0, 0 - 1
            if side_dir <= -1 and line_one['score_pre'] == 4 and door_width < UNIT_WIDTH_DOOR * 1.5:
                side_width_1 = line_one['depth_pre_more']
            # 后序走道
            side_width_2, side_dir = 0, 0 + 1
            if side_dir >= 1 and line_one['score_post'] == 4 and door_width < UNIT_WIDTH_DOOR * 1.5:
                side_width_2 = line_one['depth_post_more']
            # 进门走道
            turn_width = max(UNIT_WIDTH_DOOR, side_width_1, side_width_2)
            turn_angle = ang_to_ang(line_one['angle'] + math.pi / 2)
            if door_width > UNIT_WIDTH_DOOR * 1.5:
                turn_width = max(UNIT_WIDTH_DOOR * 0.5, side_width_1, side_width_2)
            elif door_width < UNIT_WIDTH_DOOR * 1.0:
                if line_one['score_pre'] == 1:
                    line_pre = line_list[(line_idx - 1 + len(line_list)) % len(line_list)]
                    if line_pre['type'] in [UNIT_TYPE_DOOR] and line_pre['width'] > door_width:
                        continue
                elif line_one['score_post'] == 1:
                    line_post = line_list[(line_idx + 1 + len(line_list)) % len(line_list)]
                    if line_post['type'] in [UNIT_TYPE_DOOR] and line_post['width'] > door_width:
                        continue
            if 'depth_ext' in line_one:
                depth_ext, depth_max = line_one['depth_ext'], 0
                for depth_one in depth_ext:
                    if depth_one[1] - depth_one[0] > 0.5 or (depth_one[0] < 0.4 and 0.6 < depth_one[1]):
                        depth_max = depth_one[2]
                        break
                if depth_max > 2 and (door_first or door_width < UNIT_WIDTH_DOOR * 1.5):
                    if door_first:
                        turn_width = depth_max * 1.0
                        score_pre, score_post = 4, 4
                        if depth_max >= 4:
                            depth_pre, depth_post = line_one['depth_pre_more'], line_one['depth_post_more']
                            if 1 < max(depth_pre, depth_post) < depth_max - 0.5:
                                turn_width = max(depth_pre, depth_post)
                            else:
                                turn_width = depth_max * 0.5
                            score_pre, score_post = 4, 1
                    elif line_one['score_pre'] == 4 or line_one['score_post'] == 4:
                        turn_width = depth_max * 1.0
                        score_pre, score_post = 4, 4
                        if depth_max >= 4:
                            depth_pre, depth_post = line_one['depth_pre_more'], line_one['depth_post_more']
                            if 1 < max(depth_pre, depth_post) < depth_max - 0.5:
                                turn_width = max(depth_pre, depth_post)
                            else:
                                turn_width = depth_max * 0.5
                            score_pre, score_post = 4, 1
                    elif line_type in [UNIT_TYPE_AISLE]:
                        turn_width = depth_max * 1.0
                        score_pre, score_post = 4, 4
                    else:
                        if depth_max >= 4:
                            turn_width *= 0.5
            x2, z2 = x1 + turn_width * math.sin(turn_angle), z1 + turn_width * math.cos(turn_angle)
            path_width, path_angle = turn_width, turn_angle
            x3, z3, x4, z4 = x1, z1, x2, z2
            path_one = {'type': line_type, 'width': path_width, 'angle': path_angle, 'p1': [x3, z3], 'p2': [x4, z4],
                        'group': '', 'score_pre': score_pre, 'score_post': score_post,
                        'width_dlt': max(UNIT_WIDTH_DOOR, line_width) / 2 - 0.1}
            if path_width > UNIT_WIDTH_DOOR * 2:
                path_one['type'] = UNIT_TYPE_AISLE
                route_aisle.insert(0, path_one)
            elif door_first:
                route_entry.insert(0, path_one)
            else:
                route_entry.append(path_one)
    # 走道路线
    if len(line_list) > 0:
        # 检测路线
        line_used = {}
        for line_idx, line_one in enumerate(line_list):
            if line_idx in line_used:
                continue
            # 类型
            line_type = line_one['type']
            line_width, line_depth, line_angle = line_one['width'], line_one['depth'], line_one['angle']
            line_pre = line_list[(line_idx - 1 + len(line_list)) % len(line_list)]
            line_post = line_list[(line_idx + 1 + len(line_list)) % len(line_list)]
            score_pre, score_post = 0, 0
            if 'score_pre' in line_one:
                score_pre = line_one['score_pre']
            if 'score_post' in line_one:
                score_post = line_one['score_post']
            if line_type in [UNIT_TYPE_SIDE] and line_width > UNIT_DEPTH_CURTAIN + 0.01:
                line_type = UNIT_TYPE_SIDE
                line_depth = UNIT_DEPTH_DODGE
                if score_pre == 4 and score_post <= 1 and line_post['type'] not in [UNIT_TYPE_DOOR]:
                    pass
                elif score_pre <= 1 and score_post == 4 and line_pre['type'] not in [UNIT_TYPE_DOOR]:
                    pass
                else:
                    continue
            elif line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and line_width > UNIT_WIDTH_DOOR * 2.0:
                line_type = UNIT_TYPE_AISLE
                line_depth = UNIT_DEPTH_DODGE
            elif line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and line_width > UNIT_WIDTH_DOOR * 1.5 \
                    and score_pre + score_post == 5:
                line_type = UNIT_TYPE_AISLE
                line_depth = UNIT_DEPTH_DODGE
            elif line_type in [UNIT_TYPE_DOOR] and line_width > UNIT_WIDTH_DOOR * 1.5 \
                    and score_pre == score_post == 1 and line_width > max(line_pre['width'], line_post['width']) + 0.2:
                line_type = UNIT_TYPE_AISLE
                line_depth = UNIT_DEPTH_DODGE
            elif line_type in [UNIT_TYPE_AISLE] and line_width > UNIT_WIDTH_DODGE * 0.5 + 0.01:
                depth_max, depth_min = 1, 10
                if 'depth_ext' in line_one:
                    depth_ext = line_one['depth_ext']
                    for depth_one in depth_ext:
                        depth_max = max(depth_max, depth_one[2])
                        depth_min = min(depth_min, depth_one[2])
                if depth_max < 4:
                    line_depth = depth_max
                else:
                    continue
            elif line_type in [UNIT_TYPE_WALL] and line_width > 1 and score_pre + score_post >= 6:
                if line_width > 3 and score_pre + score_post >= 8:
                    continue
                depth_max, depth_min = 1, 10
                if 'depth_ext' in line_one:
                    depth_ext = line_one['depth_ext']
                    for depth_one in depth_ext:
                        depth_max = max(depth_max, depth_one[2])
                        depth_min = min(depth_min, depth_one[2])
                if UNIT_WIDTH_DOOR * 1.0 < depth_min < UNIT_WIDTH_DOOR * 2.0:
                    line_depth = depth_min
                elif UNIT_WIDTH_DOOR * 1.0 < depth_max < UNIT_WIDTH_DOOR * 3.0 and room_type in ROOM_TYPE_LEVEL_1:
                    line_depth = depth_max
                elif UNIT_WIDTH_DOOR * 1.0 < line_depth < UNIT_WIDTH_DOOR * 2.0:
                    pass
                else:
                    continue
            else:
                continue
            line_used[line_idx] = line_idx
            path_width, path_angle = line_width, line_angle
            p1, p2 = line_one['p1'], line_one['p2']
            if path_width < 0.01:
                continue
            # 扩展
            for side_dir in [-1, 1]:
                if line_type in [UNIT_TYPE_WALL]:
                    # 前序
                    if score_pre == 2:
                        plus_width = UNIT_WIDTH_DOOR / 4
                        r = 0 - plus_width / line_width
                        x1, z1, x2, z2 = p1[0], p1[1], p2[0], p2[1]
                        x_new = x1 * (1 - r) + x2 * r
                        z_new = z1 * (1 - r) + z2 * r
                        p1 = [x_new, z_new]
                        path_width += plus_width
                    # 后序
                    if score_post == 2:
                        plus_width = UNIT_WIDTH_DOOR / 4
                        r = 1 + plus_width / line_width
                        x1, z1, x2, z2 = p1[0], p1[1], p2[0], p2[1]
                        x_new = x1 * (1 - r) + x2 * r
                        z_new = z1 * (1 - r) + z2 * r
                        p2 = [x_new, z_new]
                        path_width += plus_width
                    # 完成
                    break
                for i in range(1, 10, 1):
                    side_idx = (line_idx + i * side_dir + len(line_list)) % len(line_list)
                    side_one = line_list[side_idx]
                    side_type, side_width, side_angle = side_one['type'], side_one['width'], side_one['angle']
                    if side_width < 0.01:
                        break
                    if abs(ang_to_ang(side_angle - line_angle)) > 0.1:
                        if i == 1 and side_dir == -1:
                            if line_one['score_pre'] == 2:
                                plus_width = 0 + UNIT_WIDTH_DOOR
                                if line_width < 0.01:
                                    continue
                            elif line_one['score_pre'] == 4 and side_one['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                                plus_width = 0 - UNIT_WIDTH_DOOR * 0.5
                            else:
                                break
                            r = 0 - plus_width / line_width
                            p1_side, p2_side = line_one['p1'], line_one['p2']
                            x1, z1, x2, z2 = p1_side[0], p1_side[1], p2_side[0], p2_side[1]
                            x_new = x1 * (1 - r) + x2 * r
                            z_new = z1 * (1 - r) + z2 * r
                            p1 = [x_new, z_new]
                            path_width += plus_width
                        elif i == 1 and side_dir == 1:
                            if line_one['score_post'] == 2:
                                plus_width = UNIT_WIDTH_DOOR
                                if line_width < 0.01:
                                    continue
                            elif line_one['score_post'] == 4 and side_one['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                                plus_width = 0 - UNIT_WIDTH_DOOR * 0.5
                            else:
                                break
                            r = 1 + plus_width / line_width
                            p1_side, p2_side = line_one['p1'], line_one['p2']
                            x1, z1, x2, z2 = p1_side[0], p1_side[1], p2_side[0], p2_side[1]
                            x_new = x1 * (1 - r) + x2 * r
                            z_new = z1 * (1 - r) + z2 * r
                            p2 = [x_new, z_new]
                            path_width += plus_width
                        break
                    #
                    if side_type in [UNIT_TYPE_SIDE] and side_width > UNIT_DEPTH_CURTAIN + 0.01:
                        pass
                    elif side_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and side_width < 3:
                        if side_dir <= -1 and side_one['score_pre'] == 2:
                            break
                        elif side_dir >= 1 and side_one['score_post'] == 2:
                            break
                    elif side_type in [UNIT_TYPE_AISLE]:
                        pass
                    elif side_type in [UNIT_TYPE_WALL] and side_width < 5:
                        pass
                    else:
                        break
                    line_used[side_idx] = line_idx
                    path_width += side_width
                    if side_dir == -1:
                        p1 = side_one['p1']
                        if side_one['score_pre'] == 2:
                            plus_width = UNIT_WIDTH_DOOR
                            r = 0 - plus_width / side_width
                            p1_side, p2_side = side_one['p1'], side_one['p2']
                            x1, z1, x2, z2 = p1_side[0], p1_side[1], p2_side[0], p2_side[1]
                            x_new = x1 * (1 - r) + x2 * r
                            z_new = z1 * (1 - r) + z2 * r
                            p1 = [x_new, z_new]
                            path_width += plus_width
                            break
                        score_pre = side_one['score_pre']
                    elif side_dir == 1:
                        p2 = side_one['p2']
                        if side_one['score_post'] == 2:
                            plus_width = UNIT_WIDTH_DOOR
                            r = 1 + plus_width / side_width
                            p1_side, p2_side = side_one['p1'], side_one['p2']
                            x1, z1, x2, z2 = p1_side[0], p1_side[1], p2_side[0], p2_side[1]
                            x_new = x1 * (1 - r) + x2 * r
                            z_new = z1 * (1 - r) + z2 * r
                            p2 = [x_new, z_new]
                            path_width += plus_width
                            break
                        score_post = side_one['score_post']
            turn_width = line_depth * 0.5
            if line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]:
                line_type = UNIT_TYPE_AISLE
            turn_angle = ang_to_ang(line_angle + math.pi / 2)
            x1, z1, x2, z2 = p1[0], p1[1], p2[0], p2[1]
            x3, z3 = x1 + turn_width * math.sin(turn_angle), z1 + turn_width * math.cos(turn_angle)
            x4, z4 = x2 + turn_width * math.sin(turn_angle), z2 + turn_width * math.cos(turn_angle)
            # 添加
            path_one = {'type': line_type, 'width': path_width, 'angle': path_angle, 'p1': [x3, z3], 'p2': [x4, z4],
                        'group': '', 'score_pre': score_pre, 'score_post': score_post}
            if path_width < 1:
                continue
            route_aisle.append(path_one)
        # 反向路线
        for path_idx, path_one in enumerate(route_aisle):
            x3, z3, x4, z4 = path_one['p1'][0], path_one['p1'][1], path_one['p2'][0], path_one['p2'][1]
            score_pre, score_post = path_one['score_pre'], path_one['score_post']
            if len(door_link) >= 2:
                if abs(x4 - door_link[0]) + abs(z4 - door_link[1]) < abs(x3 - door_link[0]) + abs(z3 - door_link[1]):
                    path_one['p1'], path_one['p2'] = [x4, z4], [x3, z3]
                    path_one['angle'] = ang_to_ang(path_one['angle'] + math.pi)
                    path_one['score_pre'], path_one['score_post'] = score_post, score_pre
            elif x4 + z4 < x3 + z3:
                path_one['p1'], path_one['p2'] = [x4, z4], [x3, z3]
                path_one['angle'] = ang_to_ang(path_one['angle'] + math.pi)
                path_one['score_pre'], path_one['score_post'] = score_post, score_pre
        # 添加进门
        for path_one in route_entry:
            route_aisle.insert(0, path_one)

    # 方案信息
    scheme_list = []
    if 'layout_scheme' in layout_info:
        scheme_list = layout_info['layout_scheme']
    if len(scheme_list) <= 0:
        scheme_new = {'group': []}
        scheme_list.append(scheme_new)
    # 软装路线
    for scheme_idx, scheme_one in enumerate(scheme_list):
        # 定义路线
        route_list, route_info, wander_list = [], {}, []
        # 检测组合
        group_list, group_main, group_side, group_face = scheme_one['group'], {}, {}, {}
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type in GROUP_RULE_FUNCTIONAL and len(group_main) <= 0:
                group_main = group_one
            if group_type in ['Meeting', 'Bed', 'Dining', 'Work', 'Rest']:
                if len(group_main) <= 0:
                    group_main = group_one
                elif len(group_side) <= 0 and not group_one == group_main:
                    group_side = group_one
            elif group_type in ['Media']:
                group_face = group_one
            else:
                continue
        # 检测路线
        group_pass, group_path = 0.4, []
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type in ['Meeting', 'Bed', 'Dining', 'Work', 'Rest']:
                if group_type in ['Work', 'Rest'] and group_one == group_side:
                    continue
            else:
                continue
            group_pos, group_ang = group_one['position'], rot_to_ang(group_one['rotation'])
            group_size, group_center, group_vertical, group_extent = group_one['size'], 0, 0, 0
            neighbor_rest, neighbor_more, neighbor_best = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
            if 'center' in group_one:
                group_center = group_one['center']
            if 'vertical' in group_one:
                group_vertical = group_one['vertical']
            if 'region_extent' in group_one:
                group_extent = group_one['region_extent']
            if 'size_rest' in group_one:
                neighbor_rest = group_one['size_rest']
            if 'neighbor_more' in group_one:
                neighbor_more = group_one['neighbor_more'][:]
                if group_type in ['Meeting'] and len(group_face) <= 0 and group_center <= 0:
                    neighbor_more[1] = min(neighbor_more[1], 1.0)
                    neighbor_more[3] = min(neighbor_more[3], 1.0)
            if 'neighbor_best' in group_one:
                neighbor_best = group_one['neighbor_best'][:]
            if len(neighbor_more) >= 4:
                # 冗余调整 横向
                if group_type in ['Meeting'] and len(group_face) > 0 and group_center >= 1:
                    neighbor_face = [0, 0, 0, 0]
                    if 'neighbor_more' in group_face:
                        face_pos = group_face['position']
                        face_size, face_side = group_face['size'], group_face['neighbor_more']
                        face_dis, face_ang = xyz_to_ang(group_pos[0], group_pos[2], face_pos[0], face_pos[2])
                        face_mov = face_dis * math.sin(face_ang - group_ang)
                        neighbor_face[1] = face_size[0] / 2 - face_mov + face_side[3] - group_size[0] / 2
                        neighbor_face[3] = face_size[0] / 2 + face_mov + face_side[1] - group_size[0] / 2
                    neighbor_more[1] = max(neighbor_more[1], neighbor_face[1])
                    neighbor_more[3] = max(neighbor_more[3], neighbor_face[3])
            x1, z1 = group_pos[0], group_pos[2]
            # 前
            route_flag, route_role = False, ''
            score_pre, score_post = 1, 1
            if group_type in ['Meeting', 'Bed']:
                route_flag, route_role = True, 'main'
                tmp_x = 0 - group_size[0] * 0.5 - min(neighbor_more[1] * 1.00 - 0, UNIT_WIDTH_DODGE)
                tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 0.60 - 0, UNIT_WIDTH_DODGE * 2)
                if neighbor_more[2] < UNIT_DEPTH_CURTAIN:
                    tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 1.0 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
            elif group_type in ['Dining'] and group_center >= 1:
                route_flag, route_role = True, 'side'
                tmp_x = 0 - group_size[0] * 0.5 - min(neighbor_more[1] * 1.0 - 0, UNIT_WIDTH_DODGE)
                tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 1.0 - 0, UNIT_WIDTH_DODGE * 2)
                if neighbor_more[2] > max(neighbor_more[0], neighbor_more[1], neighbor_more[3], 0.2):
                    route_flag = True
                else:
                    route_flag = False
            elif group_type in ['Dining'] and group_center <= 0 and group_vertical <= 0:
                route_flag, route_role = True, 'side'
                tmp_x = 0 - group_size[0] * 0.5 - min(neighbor_more[1] * 1.0 - 0, UNIT_WIDTH_DODGE)
                tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 1.0 - 0, UNIT_WIDTH_DODGE * 2)
                if neighbor_more[2] < 0.01 and neighbor_rest[2] < 0.4:
                    route_flag = False
            elif group_type in ['Work'] and group_center <= 0 and group_vertical <= 0 and room_type in ['Library']:
                route_flag, route_role = True, 'side'
                tmp_x = 0 - group_size[0] * 0.5 - min(neighbor_more[1] * 1.0 - 0, UNIT_WIDTH_DODGE)
                tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 1.0 - 0, UNIT_WIDTH_DODGE * 2)
                if neighbor_more[2] < 0.01 and neighbor_rest[2] < 0.4:
                    route_flag = False
            elif group_type in ['Dining', 'Work', 'Rest'] and group_center <= 0 and group_vertical >= 1:
                route_flag = True
                tmp_x = 0 - group_size[0] * 0.5 - min(neighbor_more[1] * 1.0 - 0, UNIT_WIDTH_DODGE * 2)
                tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 1.0 - 0, UNIT_WIDTH_DODGE)
                if neighbor_more[2] < UNIT_DEPTH_CURTAIN:
                    tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 0.5 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
            if route_flag:
                add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
                add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
                x3, z3 = x1 + add_x, z1 + add_z
                tmp_x = 0 + group_size[0] * 0.5 + min(neighbor_more[3] * 1.0 - 0, UNIT_WIDTH_DODGE)
                add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
                add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
                x4, z4 = x1 + add_x, z1 + add_z
                line_type = UNIT_TYPE_GROUP
                # 添加
                path_width, path_angle = room_calc_vector(x3, z3, x4, z4)
                path_one = {'type': line_type, 'width': path_width, 'angle': path_angle, 'p1': [x3, z3], 'p2': [x4, z4],
                            'role': route_role, 'group': group_type, 'score_pre': score_pre, 'score_post': score_post}
                group_path.append(path_one)

            # 后
            route_flag, route_role = False, ''
            score_pre, score_post = 1, 1
            if group_type in ['Meeting', 'Bed'] and group_center >= 1 and neighbor_rest[0] >= UNIT_DEPTH_CURTAIN:
                route_flag, route_role = True, ''
                tmp_x = 0 - group_size[0] * 0.5 - min(neighbor_more[1] * 1.0 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5 + neighbor_rest[0] * 0.2
            elif group_type in ['Meeting', 'Bed'] and group_center >= 1 and group_extent > max(4, group_size[2] + 0.5):
                route_flag, route_role = True, 'back'
                tmp_x = 0 - group_size[0] * 0.5 - min(neighbor_more[1] * 1.0 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5
            elif group_type in ['Dining'] and group_center >= 1:
                route_flag, route_role = True, 'side'
                tmp_x = 0 - group_size[0] * 0.5 - min(neighbor_more[1] * 1.0 - 0, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5 - min(neighbor_more[2] * 0.5 - 0, UNIT_WIDTH_DODGE)
                if neighbor_more[0] > max(neighbor_more[1], neighbor_more[2], neighbor_more[3], 0.2):
                    route_flag = True
                else:
                    route_flag = False
            if route_flag:
                add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
                add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
                x3, z3 = x1 + add_x, z1 + add_z
                tmp_x = 0 + group_size[0] * 0.5 + (neighbor_more[3] * 1.0 - UNIT_DEPTH_CURTAIN)
                add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
                add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
                x4, z4 = x1 + add_x, z1 + add_z
                line_type = UNIT_TYPE_GROUP
                # 添加
                path_width, path_angle = room_calc_vector(x3, z3, x4, z4)
                path_one = {'type': line_type, 'width': path_width, 'angle': path_angle, 'p1': [x3, z3], 'p2': [x4, z4],
                            'role': route_role, 'group': group_type, 'score_pre': score_pre, 'score_post': score_post}
                group_path.append(path_one)

            # 左
            route_flag, route_half = False, False
            score_pre, score_post = 4, 1
            if group_type in ['Meeting', 'Bed'] \
                    and (neighbor_more[1] + neighbor_rest[1] > group_pass or neighbor_more[1] > group_pass * 0.5 or 0.001 < neighbor_more[1] < UNIT_DEPTH_CURTAIN):
                route_flag = True
                tmp_x = 0 - group_size[0] * 0.5 - min(max(neighbor_more[1], neighbor_best[1]) * 0.5, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5 - min(neighbor_more[0] * 1.0, UNIT_WIDTH_DODGE)
                if max(neighbor_more[1], neighbor_best[1]) * 0.5 < UNIT_DEPTH_CURTAIN:
                    add_x = min(max(neighbor_more[1], neighbor_best[1]) * 0.5 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                    tmp_x = 0 - group_size[0] * 0.5 - add_x
                else:
                    side_well = UNIT_WIDTH_DODGE
                    if neighbor_rest[1] > 1 and group_size[0] > 3:
                        side_well = UNIT_WIDTH_DODGE * 0.5
                    add_x = min(max(neighbor_more[1], neighbor_best[1]) * 0.5, side_well)
                    tmp_x = 0 - group_size[0] * 0.5 - add_x
                if group_type in ['Bed'] and neighbor_rest[1] < min(0.1, neighbor_rest[3]) \
                        and neighbor_more[1] < group_pass:
                    route_flag = False
                if group_center >= 1:
                    score_pre, score_post = 1, 1
            elif group_type in ['Dining'] and group_center >= 1:
                route_flag = True
                tmp_x = 0 - group_size[0] * 0.5 - min(max(neighbor_best[1], neighbor_more[1]) - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5 - min(neighbor_best[0] * 1.0, UNIT_WIDTH_DODGE)
                score_pre = 1
                if neighbor_more[1] > max(neighbor_more[3] + 0.1, 0.5) or neighbor_more[1] > UNIT_WIDTH_DOOR:
                    route_flag = True
                elif neighbor_best[1] > max(neighbor_best[3] + 0.1, 0.5) or neighbor_best[1] > UNIT_WIDTH_DOOR:
                    route_flag = True
                elif neighbor_best[1] > 0.5 and neighbor_more[2] > 1:
                    route_flag = True
                else:
                    route_flag = False
            elif group_type in ['Dining', 'Work', 'Rest'] and group_center <= 0 and neighbor_more[1] + neighbor_rest[1] > group_pass:
                route_flag = True
                tmp_x = 0 - group_size[0] * 0.5 - min(max(neighbor_best[1], neighbor_more[1]) - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5 - min(neighbor_best[0] * 1.0 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
            if route_flag:
                add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
                add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
                x3, z3 = x1 + add_x, z1 + add_z
                tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 1.0 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
                add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
                x4, z4 = x1 + add_x, z1 + add_z
                line_type = UNIT_TYPE_GROUP
                # 添加
                path_width, path_angle = room_calc_vector(x3, z3, x4, z4)
                path_one = {'type': line_type, 'width': path_width, 'angle': path_angle, 'p1': [x3, z3], 'p2': [x4, z4],
                            'group': group_type, 'score_pre': score_pre, 'score_post': score_post}
                group_path.append(path_one)

            # 右
            route_flag, route_half = False, False
            score_pre, score_post = 4, 1
            if group_type in ['Meeting', 'Bed'] \
                    and (neighbor_more[3] + neighbor_rest[3] > group_pass or neighbor_more[3] > group_pass * 0.5 or 0.001 < neighbor_more[3] < UNIT_DEPTH_CURTAIN):
                route_flag = True
                tmp_x = 0 + group_size[0] * 0.5 + min(max(neighbor_more[3], neighbor_best[3]) * 0.5, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5 - min(neighbor_more[0] * 1.0, UNIT_WIDTH_DODGE)
                if max(neighbor_more[3], neighbor_best[3]) < UNIT_DEPTH_CURTAIN:
                    add_x = min(max(neighbor_more[3], neighbor_best[3]) * 0.5 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                    tmp_x = 0 + group_size[0] * 0.5 + add_x
                else:
                    side_well = UNIT_WIDTH_DODGE * 1.5
                    if neighbor_rest[3] > 1 and group_size[0] > 3:
                        side_well = UNIT_WIDTH_DODGE * 0.5
                    add_x = min(max(neighbor_more[3], neighbor_best[3]) * 0.5, side_well)
                    tmp_x = 0 + group_size[0] * 0.5 + add_x
                if group_type in ['Bed'] and neighbor_rest[3] < min(0.1, neighbor_rest[1]) \
                        and neighbor_more[3] < group_pass:
                    route_flag = False
                if group_center >= 1:
                    score_pre, score_post = 1, 1
            elif group_type in ['Dining'] and group_center >= 1:
                route_flag = True
                tmp_x = 0 + group_size[0] * 0.5 + min(max(neighbor_best[3], neighbor_more[3]) - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5 - min(neighbor_best[0] * 1.0, UNIT_WIDTH_DODGE)
                score_pre = 1
                if neighbor_more[3] > max(neighbor_more[1] + 0.1, 0.5) or neighbor_more[3] > UNIT_WIDTH_DOOR:
                    route_flag = True
                elif neighbor_best[3] > max(neighbor_best[1] + 0.1, 0.5) or neighbor_best[3] > UNIT_WIDTH_DOOR:
                    route_flag = True
                elif neighbor_best[3] > 0.5 and neighbor_more[2] > 1:
                    route_flag = True
                else:
                    route_flag = False
            elif group_type in ['Dining', 'Work', 'Rest'] and group_center <= 0 and neighbor_more[3] + neighbor_rest[3] > group_pass:
                route_flag = True
                tmp_x = 0 + group_size[0] * 0.5 + min(max(neighbor_best[3], neighbor_more[3]) - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                tmp_z = 0 - group_size[2] * 0.5 - min(neighbor_best[0] * 1.0 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
            if route_flag:
                add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
                add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
                x3, z3 = x1 + add_x, z1 + add_z
                tmp_z = 0 + group_size[2] * 0.5 + min(neighbor_more[2] * 1.0 - UNIT_DEPTH_CURTAIN, UNIT_WIDTH_DODGE)
                add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
                add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
                x4, z4 = x1 + add_x, z1 + add_z
                line_type = UNIT_TYPE_GROUP
                # 添加
                path_width, path_angle = room_calc_vector(x3, z3, x4, z4)
                path_one = {'type': line_type, 'width': path_width, 'angle': path_angle, 'p1': [x3, z3], 'p2': [x4, z4],
                            'group': group_type, 'score_pre': score_pre, 'score_post': score_post}
                group_path.append(path_one)
        # 反向路线
        route_group = group_path
        for path_idx, path_one in enumerate(route_group):
            x3, z3, x4, z4 = path_one['p1'][0], path_one['p1'][1], path_one['p2'][0], path_one['p2'][1]
            score_pre, score_post = path_one['score_pre'], path_one['score_post']
            if len(door_link) >= 2:
                if abs(x4 - door_link[0]) + abs(z4 - door_link[1]) < abs(x3 - door_link[0]) + abs(z3 - door_link[1]):
                    path_one['p1'], path_one['p2'] = [x4, z4], [x3, z3]
                    path_one['angle'] = ang_to_ang(path_one['angle'] + math.pi)
                    path_one['score_pre'], path_one['score_post'] = score_post, score_pre
            elif x4 + z4 < x3 + z3:
                path_one['p1'], path_one['p2'] = [x4, z4], [x3, z3]
                path_one['angle'] = ang_to_ang(path_one['angle'] + math.pi)
                path_one['score_pre'], path_one['score_post'] = score_post, score_pre

        # 融合路线
        path_merge = []
        # 融合一级
        merge_entry, merge_aisle, merge_group = route_entry, [], []
        for path_one in route_aisle:
            path_new = path_one.copy()
            path_new['p1'], path_new['p2'] = path_one['p1'][:], path_one['p2'][:]
            path_fix = 1
            for used_idx, path_old in enumerate(merge_aisle):
                path_fix = room_path_merge(path_old, path_new, room_area)
                if path_fix <= 0:
                    break
            if path_fix >= 1 and path_one not in merge_entry:
                merge_aisle.append(path_new)
        for path_one in route_group:
            path_new = path_one.copy()
            path_new['p1'], path_new['p2'] = path_one['p1'][:], path_one['p2'][:]
            path_fix = 1
            for used_idx, path_old in enumerate(merge_group):
                if 'role' in path_new and path_new['role'] in ['side']:
                    break
                path_fix = room_path_merge(path_old, path_new, room_area)
                if path_fix <= 0:
                    break
            if path_fix >= 1:
                merge_group.append(path_new)
        # 融合二级
        merge_final = []
        for path_set in [merge_aisle, merge_group, merge_entry]:
            for path_idx, path_one in enumerate(path_set):
                path_new = path_one.copy()
                path_new['p1'], path_new['p2'] = path_one['p1'][:], path_one['p2'][:]
                path_fix = 1
                for used_idx, path_old in enumerate(merge_final):
                    path_fix = room_path_merge(path_old, path_new, room_area)
                    if path_fix <= 0:
                        break
                path_len = 0
                if 'width' in path_new:
                    path_len = path_new['width']
                if path_fix >= 1 and path_len > 0.1:
                    find_idx = -1
                    for path_idx, path_old in enumerate(merge_final):
                        type_new, type_old = path_new['type'], path_old['type']
                        width_new, width_old = path_new['width'], path_old['width']
                        if type_new in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                            width_new *= 1.5
                        if type_old in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                            width_old *= 1.5
                        if width_new > width_old:
                            find_idx = path_idx
                            break
                    if 0 <= find_idx < len(merge_final):
                        merge_final.insert(find_idx, path_new)
                    else:
                        merge_final.append(path_new)
        path_merge = merge_final

        # 对齐路线
        path_aside = []
        for path_idx, path_one in enumerate(path_merge):
            path_new = path_one
            path_fix = 1
            for used_idx, path_old in enumerate(path_aside):
                path_fix = room_path_aside(path_old, path_new)
                if path_fix <= 0:
                    break
            path_len = 0
            if 'width' in path_new:
                path_len = path_new['width']
            if path_fix >= 1 and path_len > 0.1:
                find_idx = -1
                for path_idx, path_old in enumerate(path_aside):
                    type_old, width_old = path_old['type'], path_old['width']
                    type_new, width_new = path_new['type'], path_new['width']
                    # score_pre_old, score_post_old = path_old['score_pre'], path_old['score_post']
                    # score_pre_new, score_post_new = path_new['score_pre'], path_new['score_post']
                    if type_new in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE] and type_old not in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                        find_idx = path_idx
                        break
                    elif type_new not in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE] and type_old in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                        continue
                    if width_new > width_old:
                        find_idx = path_idx
                        break
                if 0 <= find_idx < len(path_aside):
                    path_aside.insert(find_idx, path_new)
                else:
                    path_aside.append(path_new)

        # 交叉路线
        path_cross = []
        for path_idx, path_one in enumerate(path_aside):
            path_new = path_one
            path_fix = 1
            for used_idx, path_old in enumerate(path_cross):
                path_fix = room_path_cross(path_old, path_new, room_area)
                if path_fix <= 0:
                    break
            if path_fix >= 1:
                path_cross.append(path_new)
        # 排序路线
        path_final = room_path_queue(path_cross, door_link)
        # 切分路线
        route_line, route_point = room_path_point(path_final, step_width=path_step)
        wander_point = room_path_scene(route_point, group_main, group_side)
        # 添加路线
        route_list.append(route_line)
        wander_list.append(wander_point)
        scheme_one['route'] = route_list
        scheme_one['wander'] = wander_list
        if len(wander_best) <= 0:
            wander_best = wander_point

    # 返回信息
    return wander_best


# 布局出入
def room_rect_link(room_info, layout_info, house_info={}, link_type=[], board_mode=1):
    # 调试信息
    if '5126' in room_info['id'] and False:
        print('layout link:', room_info['id'], 'debug')
    # 房间信息
    if len(link_type) <= 0:
        link_type = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library',
                     'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
    room_id, room_type, room_height = room_info['id'], room_info['type'], UNIT_HEIGHT_WALL
    if 'height' in room_info:
        room_height = room_info['height']
    room_list, target_room_type, target_room_door, target_room_more = [], {}, {}, {}
    if 'room' in house_info:
        room_list = house_info['room']
    for room_idx, room_one in enumerate(room_list):
        room_key_new, room_type_new = room_one['id'], room_one['type']
        if room_key_new == room_info['id']:
            continue
        if room_type_new in link_type:
            door_link = []
            if 'door_link' in room_one:
                door_link = room_one['door_link']
            if len(door_link) >= 2:
                target_room_type[room_key_new] = room_one['type']
                target_room_door[room_key_new] = door_link
        elif room_type_new in ['Aisle', 'Corridor', 'Stairwell', 'LaundryRoom']:
            target_room_more[room_key_new] = room_type_new
            continue
        else:
            continue
    # 方案信息
    scheme_list = []
    if 'layout_scheme' in layout_info:
        scheme_list = layout_info['layout_scheme']

    # 穿梭信息
    anchor_set_door, anchor_set_link = [], []
    anchor_mov_flat, anchor_mov_lift = 0.3, 1.0
    # 门窗锚点
    line_list, target_link_pos, target_link_role, target_link_more = [], {}, {}, {}
    if 'line_unit' in room_info:
        line_list = room_info['line_unit']
    for line_idx, line_one in enumerate(line_list):
        # 类型
        line_type, link_room, link_type, link_room_2, link_type_2 = line_one['type'], '', '', '', ''
        if line_type not in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
            continue
        if 'unit_to_room' in line_one:
            link_room = line_one['unit_to_room']
        if 'unit_to_type' in line_one:
            link_type = line_one['unit_to_type']
        if link_room in target_link_pos:
            continue
        line_pre = line_list[(line_idx - 1) % len(line_list)]
        line_post = line_list[(line_idx + 1) % len(line_list)]
        p1, p2 = line_one['p1'], line_one['p2']
        if 'p1_original' in line_one:
            p1 = line_one['p1_original']
        if 'p2_original' in line_one:
            p2 = line_one['p2_original']
        if link_room in target_room_type:
            x1, z1 = p1[0] * 0.50 + p2[0] * 0.50, p1[1] * 0.50 + p2[1] * 0.50
            if line_one['score_pre'] == 4 and line_pre['type'] in [UNIT_TYPE_DOOR]:
                if line_one['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
                    x1, z1 = p1[0] * 0.25 + p2[0] * 0.75, p1[1] * 0.25 + p2[1] * 0.75
                elif line_one['score_post'] == 2:
                    x1, z1 = p1[0] * 0.25 + p2[0] * 0.75, p1[1] * 0.25 + p2[1] * 0.75
            if line_one['score_post'] == 4 and line_post['type'] in [UNIT_TYPE_DOOR]:
                if line_one['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
                    x1, z1 = p1[0] * 0.75 + p2[0] * 0.25, p1[1] * 0.75 + p2[1] * 0.25
                elif line_one['score_pre'] == 2:
                    x1, z1 = p1[0] * 0.75 + p2[0] * 0.25, p1[1] * 0.75 + p2[1] * 0.25
            turn_width = anchor_mov_flat
            turn_angle = ang_to_ang(line_one['angle'] + math.pi / 2)
            x2, z2 = x1 + turn_width * math.sin(turn_angle), z1 + turn_width * math.cos(turn_angle)
            target_link_pos[link_room] = [x2, z2]
            target_link_role[link_room] = line_one['type']
        elif link_room in target_room_more:
            x1, z1 = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            dis_min, dis_key = 10, ''
            for target_key, target_pos in target_room_door.items():
                dis_new = abs(x1 - target_pos[0]) + abs(z1 - target_pos[1])
                if dis_new < dis_min:
                    dis_min, dis_key = dis_new, target_key
            if dis_key in target_room_type:
                turn_width = anchor_mov_flat
                turn_angle = ang_to_ang(line_one['angle'] + math.pi / 2)
                x2, z2 = x1 + turn_width * math.sin(turn_angle), z1 + turn_width * math.cos(turn_angle)
                target_link_pos[link_room] = [x2, z2]
                target_link_role[link_room] = line_one['type']
                target_link_more[link_room] = dis_key
                link_room_2, link_type_2 = dis_key, target_room_type[dis_key]
        if line_type in [UNIT_TYPE_DOOR]:
            x1, z1 = p1[0] * 0.50 + p2[0] * 0.50, p1[1] * 0.50 + p2[1] * 0.50
            anchor_ang = ang_to_ang(line_one['angle'] + math.pi / 2)
            anchor_rot = [0, math.sin(anchor_ang / 2), 0, math.cos(anchor_ang / 2)]
            x2, z2 = x1 + 0.1 * math.sin(anchor_ang), z1 + 0.1 * math.cos(anchor_ang)
            anchor_one = {
                'link_id': link_room, 'link_type': link_type,
                'link_id_2': link_room_2, 'link_type_2': link_room_2,
                'position': [x2, UNIT_HEIGHT_WALL / 2, z2], 'rotation': anchor_rot,
                'original_position': [x1, 0, z1], 'original_rotation': anchor_rot
            }
            anchor_set_door.append(anchor_one)
    # 穿梭锚点
    for target_key, target_pos in target_link_pos.items():
        target_key_new = target_key
        if target_key in target_link_more:
            target_key_new = target_link_more[target_key]
        if target_key_new in target_room_type and len(target_pos) >= 2:
            target_role = 'door'
            if target_key_new in target_link_role:
                target_line = target_link_role[target_key_new]
                if target_line in [UNIT_TYPE_DOOR]:
                    target_role = 'door'
                elif target_line in [UNIT_TYPE_WINDOW]:
                    target_role = 'window'
            target_pos_y = anchor_mov_lift - (len(anchor_set_link) % 3) * 0.4
            anchor_one = {
                'id': target_key_new,
                'type': target_room_type[target_key_new],
                'role': target_role,
                'position': [target_pos[0], target_pos_y, target_pos[1]]
            }
            anchor_set_link.append(anchor_one)
    # 更新锚点
    for scheme_idx, scheme_one in enumerate(scheme_list):
        scene_list = []
        if 'scene' in scheme_one and len(scheme_one['scene']) > 0:
            scene_list = scheme_one['scene']
        for scene_idx, scene_one in enumerate(scene_list):
            anchor_add_link, anchor_add_door = [], []
            for anchor_old in anchor_set_link:
                anchor_new = anchor_old.copy()
                anchor_new['position'] = anchor_old['position'][:]
                anchor_add_link.append(anchor_new)
            for anchor_old in anchor_set_door:
                anchor_new = anchor_old.copy()
                anchor_new['position'] = anchor_old['position'][:]
                anchor_new['rotation'] = anchor_old['rotation'][:]
                anchor_add_door.append(anchor_new)
            scene_one['anchor_link'] = anchor_add_link
            scene_one['anchor_door'] = anchor_add_door
            room_mark_link(room_info, scene_one)

    # 面板信息 垂直面 左地面 右地面
    board_mov_flat, board_mov_lift = 0.005, 0.005
    for scheme_idx, scheme_one in enumerate(scheme_list):
        board_set_wall, board_set_ceil, board_set_floor = [], [], []
        if board_mode <= 0:
            continue
        line_list = []
        if 'line_unit' in scheme_one:
            line_list = scheme_one['line_unit']
        # 遍历组合
        group_list, group_wait = scheme_one['group'], []
        for group_idx, group_one in enumerate(group_list):
            # 组合信息
            group_type, group_size = group_one['type'], group_one['size']
            vertical_flag, center_flag, window_flag = 0, 0, 0
            if 'vertical' in group_one:
                vertical_flag = group_one['vertical']
            if 'center' in group_one:
                center_flag = group_one['center']
            if 'window' in group_one:
                window_flag = group_one['window']
            # 组合判断
            if group_type in ['Meeting', 'Bed', 'Dining', 'Work', 'Rest', 'Toilet']:
                pass
            elif group_type in ['Media', 'Armoire', 'Cabinet', 'Appliance'] and center_flag <= 0 \
                    and group_size[1] < UNIT_HEIGHT_SHELF_MIN + 0.2:
                pass
            else:
                group_wait.append(group_one)
                continue
            # 组合信息
            group_pos, group_rot = group_one['position'], group_one['rotation']
            group_ang = rot_to_ang(group_rot)
            neighbor_base = [0, 0, 0, 0]
            group_regulate = [0, 0, 0, 0]
            if 'neighbor_base' in group_one:
                neighbor_base = group_one['neighbor_base'][:]
            if 'regulation' in group_one:
                group_regulate = group_one['regulation'][:]
            # 面板范围
            board_top, board_bot = room_height - UNIT_HEIGHT_CEIL * 2, min(group_size[1], UNIT_HEIGHT_SHELF_MIN + 0.2)
            board_width, board_height = group_size[0], board_top - board_bot
            board_pos, board_rot, board_ang = group_pos[:], group_rot[:], group_ang
            # 居中组合
            if (center_flag >= 1 and len(line_list) > 0) or (vertical_flag >= 1 and len(line_list) > 0) or \
                    (group_type in ['Dining', 'Work', 'Rest'] and hor_or_ver(group_ang) <= -1 and len(line_list) > 0):
                near_idx, near_dis, near_width = 0, 100, 1
                for line_idx, line_one in enumerate(line_list):
                    line_type = line_one['type']
                    line_width, line_height, line_group = line_one['width'], line_one['height'], ''
                    if 'unit_group' in line_one:
                        line_group = line_one['unit_group']
                    if line_width < 0.5:
                        continue
                    if line_type in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE]:
                        pass
                    elif line_type in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and line_width > UNIT_WIDTH_DOOR * 1.5:
                        pass
                    elif line_type in [UNIT_TYPE_GROUP] and line_height <= UNIT_HEIGHT_SHELF_MIN:
                        pass
                    elif line_type in [UNIT_TYPE_GROUP] and line_group in ['Cabinet'] and group_type in ['Meeting']:
                        pass
                    else:
                        continue
                    # 背面
                    line_angle, face_angle = line_one['angle'], ang_to_ang(group_ang + math.pi / 2)
                    p1, p2 = line_one['p1'], line_one['p2']
                    x0, z0 = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
                    flag_left, flag_back = room_calc_locate(group_pos[0], group_pos[2], x0, z0,
                                                            group_ang, group_size[0], group_size[2])
                    if flag_back >= 0 and abs(ang_to_ang(line_angle - face_angle)) < 0.1:
                        continue
                    # 距离
                    dis1, dis2, dis3 = room_calc_distance(line_one, [0, 1], [group_pos[0], group_pos[2]], 0, 2)
                    near_new = min(dis1, dis2, dis3)
                    if line_width < 2.0:
                        near_new += 2
                    if near_new < near_dis:
                        near_idx, near_dis, near_width = line_idx, near_new, line_width
                # 墙体信息
                line_idx, line_one = near_idx, line_list[near_idx]
                line_ang, p1, p2 = line_one['angle'], line_one['p1'], line_one['p2']
                line_pre = line_list[(line_idx - 1 + len(line_list)) % len(line_list)]
                line_post = line_list[(line_idx + 1 + len(line_list)) % len(line_list)]
                type_pre, type_post = line_pre['type'], line_post['type']
                score_pre, score_post = line_one['score_pre'], line_one['score_post']
                # 面板尺寸
                width_base, width_side_1, width_side_2 = line_one['width'], 0, 0
                if score_pre == 1 and type_pre in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE]:
                    width_side_1 = line_pre['width']
                if score_post == 1 and type_post in [UNIT_TYPE_WALL, UNIT_TYPE_AISLE]:
                    width_side_2 = line_pre['width']
                board_width, board_height = width_base + width_side_1 + width_side_2, board_top - board_bot
                # 面板位置
                board_pos, board_ang = [(p1[0] + p2[0]) / 2, 0, (p1[1] + p2[1]) / 2], ang_to_ang(line_ang + math.pi / 2)
                tmp_x = (width_side_2 - width_side_1) / 2
                tmp_y = (board_top + board_bot) / 2
                tmp_z = board_mov_flat
                add_x = tmp_z * math.sin(board_ang) + tmp_x * math.cos(board_ang)
                add_y = tmp_y
                add_z = tmp_z * math.cos(board_ang) - tmp_x * math.sin(board_ang)
                pos_x, pos_y, pos_z = board_pos[0] + add_x, board_pos[1] + add_y, board_pos[2] + add_z
                board_pos, board_rot = [pos_x, pos_y, pos_z], [0, math.sin(board_ang / 2), 0, math.cos(board_ang / 2)]
            # 靠墙组合
            else:
                # 面板尺寸
                width_base, width_side_1, width_side_2 = group_size[0], min(neighbor_base[1], 1), min(neighbor_base[3], 1)
                board_width, board_height = width_base + width_side_1 + width_side_2, board_top - board_bot
                # 扩展尺寸 TODO:
                pass
                # 面板位置
                tmp_x = (width_side_2 - width_side_1) / 2
                tmp_y = (board_top + board_bot) / 2
                tmp_z = 0 - group_size[2] / 2 + board_mov_flat - group_regulate[0]
                add_x = tmp_z * math.sin(board_ang) + tmp_x * math.cos(board_ang)
                add_y = tmp_y
                add_z = tmp_z * math.cos(board_ang) - tmp_x * math.sin(board_ang)
                pos_x, pos_y, pos_z = board_pos[0] + add_x, board_pos[1] + add_y, board_pos[2] + add_z
                board_pos, board_rot = [pos_x, pos_y, pos_z], group_rot[:]
            # 面板目标
            object_list, object_todo = group_one['obj_list'], []
            for object_one in object_list:
                if 'role' in object_one and object_one['role'] not in ['', 'accessory']:
                    if 'entityId' in object_one and len(object_one['entityId']) > 0:
                        object_add = {
                            'id': object_one['id'], 'group': group_type, 'role': object_one['role'],
                            'position': object_one['position'][:], 'rotation': object_one['rotation'][:],
                            'entityId': object_one['entityId']
                        }
                        object_todo.append(object_add)
            # 面板信息
            board_add = {
                'type': group_type, 'size': [board_width, board_height, 0.1],
                'position': board_pos, 'rotation': board_rot,
                'relate_role': 'wall', 'relate_soft': object_todo
            }
            board_set_wall.append(board_add)
            # 贴地面板 TODO:
            pass
        # 遍历墙面 TODO:柜架
        pass
        # 遍历装饰 TODO:墙顶地门窗
        pass
        # 添加面板
        scheme_one['board_wall'] = board_set_wall
        scheme_one['board_ceiling'] = board_set_ceil
        scheme_one['board_floor'] = board_set_floor


# 清空机位
def room_null_view(room_info, layout_info):
    scheme_list = []
    if 'layout_scheme' in layout_info:
        scheme_list = layout_info['layout_scheme']
    for scheme_idx, scheme_one in enumerate(scheme_list):
        scheme_one['scene'] = []


# 清空点位
def room_null_path(room_info, layout_info):
    scheme_list = []
    if 'layout_scheme' in layout_info:
        scheme_list = layout_info['layout_scheme']
    for scheme_idx, scheme_one in enumerate(scheme_list):
        scheme_one['route'] = []


# 复制机位
def room_copy_view(scene_one):
    scene_new = scene_one.copy()
    if 'aabb' in scene_one:
        scene_new['aabb'] = scene_one['aabb'][:]
    if 'center' in scene_one:
        scene_new['center'] = scene_one['center'][:]
    # 机位
    camera_one = {}
    if 'camera' in scene_one:
        camera_one = scene_one['camera']
    camera_new = camera_one.copy()
    if 'up' in camera_one:
        camera_new['up'] = camera_one['up'][:]
    if 'pos' in camera_one:
        camera_new['pos'] = camera_one['pos'][:]
    if 'target' in camera_one:
        camera_new['target'] = camera_one['target'][:]
    scene_new['camera'] = camera_new
    # 墙体
    if 'intersect' in scene_one:
        intersect_old, intersect_new = scene_one['intersect'], {}
        for unit_key, unit_val in intersect_old.items():
            intersect_new[unit_key] = unit_val[:]
        scene_new['intersect'] = intersect_new
    # 视野
    if 'vision' in scene_one:
        scene_new['vision'] = scene_one['vision'][:]
    return scene_new


# 计算机位
def room_calc_view(room_info, scene_info, group_main, group_side={}, group_face={}, view_mode=0):
    room_type, room_area, room_lift = '', 0, 0
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    if 'layerAltitude' in room_info:
        room_lift = room_info['layerAltitude']
    # 原有机位
    center_pos, camera_info = scene_info['center'], scene_info['camera']
    pos_old_1 = camera_info['pos']
    pos_old_2 = camera_info['target']
    dis_tar, ang_tar = xyz_to_ang(pos_old_1[0], pos_old_1[2], pos_old_2[0], pos_old_2[2])
    # 家具位置
    pos_grp = group_main['position'][:]
    ang_grp = rot_to_ang(group_main['rotation'])
    if 'obj_main' in group_main:
        scene_info['object'] = group_main['obj_main']
    # 家具角度
    dis_dlt, ang_dlt = xyz_to_ang(center_pos[0], center_pos[1], pos_old_1[0], pos_old_1[2])
    # 家具范围
    group_type, group_size, group_offset = group_main['type'], group_main['size'], [0, 0, 0]
    group_center_flag, group_vertical_flag = 0, 0
    if 'offset' in group_main:
        group_offset = group_main['offset']
    if 'center' in group_main:
        group_center_flag = group_main['center']
    if 'vertical' in group_main:
        group_vertical_flag = group_main['vertical']
    neighbor_rest, neighbor_base, neighbor_more = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
    if 'size_rest' in group_main and len(group_main['size_rest']) >= 4:
        neighbor_rest = group_main['size_rest'][:]
    if 'neighbor_base' in group_main and len(group_main['neighbor_base']) >= 4:
        neighbor_base = group_main['neighbor_base'][:]
        neighbor_more = group_main['neighbor_base'][:]
    if 'neighbor_more' in group_main and len(group_main['neighbor_more']) >= 4:
        neighbor_more = group_main['neighbor_more'][:]

    # 进门视角
    group_none = False
    if group_type not in GROUP_RULE_FUNCTIONAL:
        group_none = True
    elif group_type in ['Cabinet', 'Toilet']:
        if len(group_side) <= 0 and len(group_face) <= 0:
            group_none = True
        elif room_area <= 4:
            group_none = True
        elif neighbor_more[2] < 0.2:
            if 'Bathroom' in room_type:
                group_none = True
    if group_none:
        floor_pts, floor_len = [], 0
        door_info, hole_info, door_one, door_pts, door_pos = [], [], {}, [], []
        if 'floor' in room_info:
            floor_pts = room_info['floor']
            floor_len = int(len(floor_pts) / 2)
        if 'door_info' in room_info:
            door_info = room_info['door_info']
            if len(door_one) <= 0 and len(door_info) > 0:
                door_one = door_info[0]
                door_pts = door_one['pts']
        if 'hole_info' in room_info:
            hole_info = room_info['hole_info']
            if len(door_one) <= 0 and len(hole_info) > 0:
                door_one = hole_info[0]
                door_pts = door_one['pts']
        # 虚拟组合
        group_main = {
            'type': '', 'size': [1, 1, 1], 'offset': [0, 0, 0],
            'position': [0, 0, 0], 'rotation': [0, 0, 0, 1]
        }
        # 进门视角
        if floor_len >= 2 and len(door_pts) >= 8 and (room_area <= 5 or group_type in ['Cabinet', 'Toilet']):
            door_pos = [(door_pts[0] + door_pts[2] + door_pts[4] + door_pts[6]) / 4,
                        (door_pts[1] + door_pts[3] + door_pts[5] + door_pts[7]) / 4]
            x0, z0 = door_pos[0], door_pos[1]
            # 起始
            x1, z1, x2, z2 = floor_pts[0], floor_pts[1], floor_pts[2], floor_pts[3]
            x3, z3 = (x1 + x2) / 2, (z1 + z2) / 2
            dis_new, ang_new = room_calc_vector(x1, z1, x2, z2)
            if dis_new <= 0.4:
                x1, z1, x2, z2 = floor_pts[2], floor_pts[3], floor_pts[0], floor_pts[1]
                x3, z3 = (x1 + x2) / 2, (z1 + z2) / 2
                dis_new, ang_new = room_calc_vector(x1, z1, x2, z2)
            ang_grp, ang_mov = ang_new + math.pi / 2, ang_new + math.pi / 2
            pos_grp = [x3 + UNIT_WIDTH_DOOR * math.sin(ang_mov), 0, z3 + UNIT_WIDTH_DOOR * math.cos(ang_mov)]
            # 最佳
            for i in range(floor_len - 1):
                x1, z1, x2, z2 = floor_pts[2 * i + 0], floor_pts[2 * i + 1], floor_pts[2 * i + 2], floor_pts[2 * i + 3]
                x3, z3 = (x1 + x2) / 2, (z1 + z2) / 2
                dis_new, ang_new = room_calc_vector(x1, z1, x2, z2)
                dis_mid, ang_mid = room_calc_vector(x0, z0, x3, z3)
                if abs(dis_mid * math.cos(ang_mid - ang_new)) < dis_new * 0.5 and \
                        abs(dis_mid * math.sin(ang_mid - ang_new)) < 0.2:
                    dis_mov = 0.5
                    ang_grp = ang_new - math.pi / 2
                    ang_mov = ang_new + math.pi / 2
                    x4, z4 = x0, z0
                    if dis_mid > UNIT_WIDTH_DOOR * 1.0:
                        rat = UNIT_WIDTH_DOOR * 0.3 / dis_mid
                        x4 = x0 * (1 - rat) + x3 * rat
                        z4 = z0 * (1 - rat) + z3 * rat
                    pos_grp = [x4 + dis_mov * math.sin(ang_mov), 0, z4 + dis_mov * math.cos(ang_mov)]
                    ang_dlt = ang_mid
                    break
            # 尺寸
            group_size = [UNIT_WIDTH_DOOR, 1, 0.2]
            group_rest = [0, 0, 0.2, 0]
            # 更新
            group_main['size'] = group_size
            group_main['position'] = pos_grp
            group_main['rotation'] = [0, math.sin(ang_grp / 2), 0, math.cos(ang_grp / 2)]
            group_main['neighbor_base'] = group_rest
            group_main['neighbor_more'] = group_rest
            group_side = {}
            neighbor_base = group_rest[:]
            neighbor_more = group_rest[:]
        # 朝墙视角
        elif floor_len >= 2 and 'line_unit' in room_info:
            dis_mov = 0.50
            # 起始
            x1, z1, x2, z2 = floor_pts[0], floor_pts[1], floor_pts[2], floor_pts[3]
            x3, z3 = (x1 + x2) / 2, (z1 + z2) / 2
            dis_new, ang_new = room_calc_vector(x1, z1, x2, z2)
            ang_grp, ang_mov = ang_new + math.pi / 2, ang_new + math.pi / 2
            pos_grp = [x3 + dis_mov * math.sin(ang_mov), 0, z3 + dis_mov * math.cos(ang_mov)]
            # 最佳
            line_list, line_area, line_look = room_info['line_unit'], 1, 1
            for line_idx, line_one in enumerate(line_list):
                line_type = line_one['type']
                if line_type not in [UNIT_TYPE_WALL, UNIT_TYPE_WINDOW]:
                    continue
                line_width, line_depth, line_angle = line_one['width'], 1.0, line_one['angle']
                if line_type in [UNIT_TYPE_WINDOW]:
                    if room_type in ['Kitchen'] and line_width > 1.0:
                        line_width *= 1.5
                    else:
                        line_width *= 0.5
                if 'depth_all' in line_one:
                    depth_all, depth_min = line_one['depth_all'], 1.5
                    for depth_one in depth_all:
                        r1, r2, d = depth_one[0], depth_one[1], depth_one[2]
                        if d < depth_min and r2 - r1 > 0.2:
                            depth_min = d
                        if r1 < 0.4 and r2 > 0.6 and d > line_depth:
                            line_depth = d
                            break
                line_depth = max(line_depth, depth_min)
                if line_width < 1 and line_depth > max(3, line_width * 3):
                    continue
                if line_width * line_depth > line_area:
                    line_area = line_width * line_depth
                    line_look = line_depth
                    ang_grp, ang_mov, dis_mov = line_angle + math.pi / 2, line_angle + math.pi / 2, line_depth * 0.50
                    x1, z1, x2, z2 = line_one['p1'][0], line_one['p1'][1], line_one['p2'][0], line_one['p2'][1]
                    x3, z3 = (x1 + x2) / 2, (z1 + z2) / 2
                    pos_grp = [x3 + dis_mov * math.sin(ang_mov), 0, z3 + dis_mov * math.cos(ang_mov)]
            # 尺寸
            group_size = [UNIT_WIDTH_DOOR, 1, line_look * 0.20]
            group_rest = [0, 0, max(line_look * 0.30 - 0.10, 0), 0]
            if line_look * 0.40 > 1.0:
                group_rest = [0, 0, max(line_look * 0.20 - 0.10, 0), 0]
            # 更新
            group_main['size'] = group_size
            group_main['position'] = pos_grp
            group_main['rotation'] = [0, math.sin(ang_grp / 2), 0, math.cos(ang_grp / 2)]
            group_main['neighbor_base'] = group_rest
            group_main['neighbor_more'] = group_rest
            group_side = {}
            neighbor_base = group_rest[:]
            neighbor_more = group_rest[:]

    # 相机范围
    min_x, max_x, min_z, max_z = -group_size[0] / 2, group_size[0] / 2, -group_size[2] / 2, group_size[2] / 2
    if len(neighbor_more) >= 4:
        # 冗余调整 横向
        if group_type in ['Meeting'] and len(group_face) > 0 and group_center_flag >= 1:
            neighbor_face = [0, 0, 0, 0]
            if 'neighbor_more' in group_face:
                face_pos = group_face['position']
                face_size, face_side = group_face['size'], group_face['neighbor_more']
                face_dis, face_ang = xyz_to_ang(pos_grp[0], pos_grp[2], face_pos[0], face_pos[2])
                face_mov = face_dis * math.sin(face_ang - ang_grp)
                neighbor_face[1] = face_size[0] / 2 - face_mov + face_side[3] - group_size[0] / 2
                neighbor_face[3] = face_size[0] / 2 + face_mov + face_side[1] - group_size[0] / 2
            neighbor_more[1] = max(neighbor_more[1], neighbor_face[1])
            neighbor_more[3] = max(neighbor_more[3], neighbor_face[3])
        elif group_type in ['Bed'] and len(group_side) > 0:
            if neighbor_rest[1] >= max(neighbor_rest[3] + neighbor_more[3], 0.3):
                neighbor_base[1] = 0
                neighbor_more[1] = 0
            elif neighbor_rest[3] >= max(neighbor_rest[1] + neighbor_more[1], 0.3):
                neighbor_base[3] = 0
                neighbor_more[3] = 0
        # 冗余调整 纵向
        elif group_type in ['Media', 'Cabinet'] and 'type' in group_face and group_face['type'] in ['Meeting', 'Bed']:
            x1, z1 = group_main['position'][0], group_main['position'][2]
            x2, z2 = group_face['position'][0], group_face['position'][2]
            dis_more, ang_more = xyz_to_ang(x1, z1, x2, z2)
            dis_more += min(group_face['size'][0], group_face['size'][2]) * 0.25
            dis_diff = abs(ang_to_ang(ang_more - ang_grp))
            if dis_diff < math.pi / 4:
                neighbor_more[2] = max(neighbor_more[2], dis_more * math.cos(ang_more - ang_grp))
        elif group_type in ['Armoire', 'Cabinet', 'Work'] and len(group_side) > 0 and group_side['type'] in ['Bed', 'Work', 'Rest', 'Bath', 'Toilet']:
            x1, z1 = group_main['position'][0], group_main['position'][2]
            x2, z2 = group_side['position'][0], group_side['position'][2]
            dis_more, ang_more = xyz_to_ang(x1, z1, x2, z2)
            dis_diff = abs(ang_to_ang(ang_more - ang_grp))
            dis_side = dis_more * math.cos(ang_more - ang_grp)
            ang_side = rot_to_ang(group_side['rotation'])
            if group_side['type'] in ['Bath']:
                if abs(ang_to_ang(ang_grp - ang_side - math.pi * 1)) < math.pi / 8:
                    dis_side = group_side['size'][2] * 0.80
                else:
                    dis_side -= min(group_side['size'][0], group_side['size'][2]) * 0.60
            elif group_side['type'] in ['Work']:
                if abs(ang_to_ang(ang_more - ang_side - math.pi / 2)) < math.pi / 4:
                    dis_side += group_side['size'][0] * 0.50
                elif abs(ang_to_ang(ang_more - ang_side + math.pi / 2)) < math.pi / 4:
                    dis_side += group_side['size'][0] * 0.50
                else:
                    dis_side += min(group_side['size'][0], group_side['size'][2]) * 0.50
            elif group_side['type'] in ['Bed']:
                if abs(ang_to_ang(ang_more - ang_side - math.pi / 2)) < math.pi / 4:
                    dis_side += group_side['size'][0] * 0.50 - UNIT_DEPTH_CURTAIN
                elif abs(ang_to_ang(ang_more - ang_side + math.pi / 2)) < math.pi / 4:
                    dis_side += group_side['size'][0] * 0.50 - UNIT_DEPTH_CURTAIN
                else:
                    dis_side += min(group_side['size'][0], group_side['size'][2]) * 0.50 - UNIT_DEPTH_CURTAIN
            else:
                dis_side += min(group_side['size'][0], group_side['size'][2]) * 0.40
            if dis_diff < math.pi / 6 or (dis_diff < math.pi / 3 and group_size[0] > 2):
                neighbor_more[2] = max(neighbor_more[2], dis_side - group_size[2] / 2)
            else:
                neighbor_more[2] = max(neighbor_more[2], 1)
        # 相机范围
        mov_0, mov_1, mov_2, mov_3 = 0, 0, 0, 0
        if group_type in ['Media', 'Dining', 'Armoire', 'Cabinet', 'Work', 'Bath', 'Toilet']:
            neighbor_more[0] = min(neighbor_more[0], 3.0)
            neighbor_more[1] = min(neighbor_more[1], 3.0)
            neighbor_more[2] = min(neighbor_more[2], 3.0)
            neighbor_more[3] = min(neighbor_more[3], 3.0)
            mov_0, mov_2 = max(neighbor_more[0] * 1.0 - 0.2, -0.0), max(neighbor_more[2] * 1.0 - 0.2, -0.0)
            mov_1, mov_3 = max(neighbor_more[1] * 1.0 - 0.5, -0.2), max(neighbor_more[3] * 1.0 - 0.5, -0.2)
        elif group_type in ['Wall']:
            neighbor_more[0] = min(neighbor_more[0], 3.0)
            neighbor_more[1] = min(neighbor_more[1], 3.0)
            neighbor_more[2] = min(neighbor_more[2], 3.0)
            neighbor_more[3] = min(neighbor_more[3], 3.0)
            mov_0, mov_2 = max(neighbor_more[0] * 1.0 - 0.0, -0.0), max(neighbor_more[2] * 1.0 - 0.0, -0.0)
            mov_1, mov_3 = max(neighbor_more[1] * 1.0 - 0.2, -0.2), max(neighbor_more[3] * 1.0 - 0.2, -0.2)
        else:
            neighbor_more[0] = min(neighbor_more[0], 1.0)
            neighbor_more[1] = min(neighbor_more[1], 1.0)
            neighbor_more[2] = min(neighbor_more[2], 3.0)
            neighbor_more[3] = min(neighbor_more[3], 1.0)
            mov_0, mov_2 = max(neighbor_more[0] * 1.0 - 0.1, -0.2), max(neighbor_more[2] * 1.0 - 0.1, -0.2)
            mov_1, mov_3 = max(neighbor_more[1] * 0.5 - 0.2, -0.2), max(neighbor_more[3] * 0.5 - 0.2, -0.2)
        min_z -= mov_0
        min_x -= mov_1
        max_z += mov_2
        max_x += mov_3
        if neighbor_rest[2] > 2.5:
            max_z = group_size[2] / 2 - 0.2
        if neighbor_more[2] <= 1.2 and group_size[0] >= 1.0:
            if group_type in ['Armoire', 'Cabinet'] and 'Bedroom' in room_type:
                return []

    # 相机方向
    ang_dlt, ang_set = 0, [0]
    if group_type not in GROUP_RULE_FUNCTIONAL:
        ang_dlt = 0
        ang_set = [ang_dlt]
    elif group_type in ['Meeting']:
        ang_dlt = 0
        ang_set = [ang_dlt, 0 - math.pi / 5, 0 + math.pi / 5]
    elif group_type in ['Bed']:
        ang_dlt = 0
        ang_set = [ang_dlt, 0 - math.pi / 6, 0 + math.pi / 6]
        if neighbor_more[1] > max(neighbor_more[3], 0.5) and neighbor_more[2] < 0.1:
            ang_dlt = -math.pi / 2
            ang_set = [ang_dlt]
        elif neighbor_more[3] > max(neighbor_more[1], 0.5) and neighbor_more[2] < 0.1:
            ang_dlt = math.pi / 2
            ang_set = [ang_dlt]
        elif room_area <= 8:
            ang_dlt = 0
            ang_set = [ang_dlt]
    elif group_type in ['Dining']:
        if neighbor_more[2] > max(neighbor_more[0], 0.8):
            ang_dlt = 0
        elif neighbor_more[3] > max(neighbor_more[1], 0.8):
            ang_dlt = math.pi / 2
        elif neighbor_more[1] > max(neighbor_more[3], 0.8):
            ang_dlt = -math.pi / 2
        elif neighbor_more[0] > max(neighbor_more[2], 0.8):
            ang_dlt = math.pi
        #
        elif neighbor_more[3] >= max(neighbor_more[1], neighbor_more[2], 0.5):
            ang_dlt = math.pi / 2
        elif neighbor_more[1] >= max(neighbor_more[2], neighbor_more[3], 0.5):
            ang_dlt = -math.pi / 2
        #
        elif neighbor_rest[2] > max(neighbor_rest[0] + 0.2, 0.2):
            ang_dlt = math.pi
        elif neighbor_rest[3] > max(neighbor_rest[1] + 0.2, 0.2):
            ang_dlt = -math.pi / 2
        elif neighbor_rest[1] > max(neighbor_rest[3] + 0.2, 0.2):
            ang_dlt = math.pi / 2
        elif neighbor_rest[0] > max(neighbor_rest[2] + 0.2, 0.2):
            ang_dlt = 0
        #
        elif neighbor_more[3] > max(neighbor_more[1], 0.2):
            ang_dlt = math.pi / 2
        elif neighbor_more[1] > max(neighbor_more[3], 0.2):
            ang_dlt = -math.pi / 2
        elif neighbor_more[3] > max(neighbor_more[0], 0.2):
            ang_dlt = math.pi / 2
        elif neighbor_more[1] > max(neighbor_more[0], 0.2):
            ang_dlt = -math.pi / 2
        elif neighbor_more[2] > max(neighbor_more[0], 0.2):
            ang_dlt = 0
        elif neighbor_more[0] > max(neighbor_more[2], 0.2):
            ang_dlt = math.pi
        elif 'type' in group_side and group_side['type'] in ['Meeting']:
            x1, z1 = group_main['position'][0], group_main['position'][2]
            x2, z2 = group_side['position'][0], group_side['position'][2]
            dis_side, ang_side = xyz_to_ang(x1, z1, x2, z2)
            if abs(ang_to_ang(ang_side - 0)) <= math.pi / 4:
                ang_dlt = 0
            elif abs(ang_to_ang(ang_side - math.pi)) <= math.pi / 4:
                ang_dlt = math.pi
            elif abs(ang_to_ang(ang_side - math.pi / 2)) <= math.pi / 4:
                ang_dlt = math.pi / 2
            elif abs(ang_to_ang(ang_side + math.pi / 2)) <= math.pi / 4:
                ang_dlt = -math.pi / 2
            else:
                ang_dlt = 0
        else:
            ang_dlt = 0
        ang_set = [ang_dlt]
    elif group_type in ['Work']:
        if len(group_side) > 0 and group_side['type'] in ['Bed']:
            pass
        elif group_center_flag >= 1:
            ang_dlt = math.pi
            ang_set = [ang_dlt]
        elif neighbor_more[0] > 0.2 > neighbor_more[2]:
            ang_dlt = math.pi
            ang_set = [ang_dlt]
    elif group_type in ['Bath'] and group_size[2] > group_size[0] * 1.5:
        if neighbor_more[3] >= max(neighbor_more[1], neighbor_more[2], 0.5):
            ang_dlt = math.pi / 2
        elif neighbor_more[1] >= max(neighbor_more[2], neighbor_more[3], 0.5):
            ang_dlt = -math.pi / 2
        ang_set = [ang_dlt]

    # 相机列表
    scene_list = []
    for ang_idx, ang_dlt in enumerate(ang_set):
        tmp_x, tmp_z = dis_dlt * math.sin(ang_dlt), dis_dlt * math.cos(ang_dlt)
        rat_x, rat_z = 1, 1
        if tmp_x > max_x and abs(tmp_x) > 0.001:
            rat_x = min(rat_x, abs(max_x / tmp_x))
        if tmp_x < min_x and abs(tmp_x) > 0.001:
            rat_x = min(rat_x, abs(min_x / tmp_x))
        if tmp_z > max_z and abs(tmp_z) > 0.001:
            rat_z = min(rat_z, abs(max_z / tmp_z))
        if tmp_z < min_z and abs(tmp_z) > 0.001:
            rat_z = min(rat_z, abs(min_z / tmp_z))
        tmp_x, tmp_z = dis_dlt * min(rat_x, rat_z) * math.sin(ang_dlt), dis_dlt * min(rat_x, rat_z) * math.cos(ang_dlt)
        add_x = tmp_z * math.sin(ang_grp) + tmp_x * math.cos(ang_grp)
        add_z = tmp_z * math.cos(ang_grp) - tmp_x * math.sin(ang_grp)
        pos_new_1 = [pos_grp[0] + add_x, pos_old_1[1], pos_grp[2] + add_z]

        # 新建场景
        scene_copy = scene_info
        if ang_idx >= 1:
            scene_copy = room_copy_view(scene_info)
        camera_copy = scene_copy['camera']
        camera_copy = room_calc_camera(group_main, camera_copy, pos_new_1, view_mode)
        camera_good = room_judge_camera([group_side], camera_copy)
        if ang_idx > 0 and not camera_good:
            continue

        # 类型检测
        if len(group_main) > 0 and 'type' in group_main:
            scene_copy['group'] = group_type
        if group_type in ['Armoire', 'Cabinet', 'Work']:
            if len(group_side) > 0 and group_side['type'] in ['Bed', 'Bath', 'Toilet']:
                camera_y = 1.1
                if 'Bathroom' in room_type or group_side['type'] in ['Work', 'Rest']:
                    pass
                else:
                    camera_one = scene_copy['camera']
                    camera_one['pos'][1] = camera_y
                    camera_one['target'][1] = camera_y

        # 穿墙检测
        mark_floor, mark_door, mark_window = room_mark_wall(room_info, group_main, scene_copy)
        scene_copy['intersect'] = {'floor': mark_floor, 'door': mark_door, 'window': mark_window}
        if len(mark_floor) > 0:
            camera_info['near'] = min(camera_info['near'] + 0.5, dis_tar - 0.1)
            mark_floor, mark_door, mark_window = room_mark_wall(room_info, group_main, scene_copy)
            scene_copy['intersect'] = {'floor': [], 'door': mark_door, 'window': mark_window}

        # 硬装检测
        scene_copy['anchor_hard'] = []
        hard_width, hard_depth, hard_height = 0.3, 0.3, 1.8
        if len(group_main) > 0:
            tmp_pos, tmp_ang = group_main['position'], rot_to_ang(group_main['rotation'])
            tmp_size, tmp_size_min = group_main['size'], group_main['size']
            # 靠墙 沙发
            if group_center_flag <= 0:
                tmp_x, tmp_y, tmp_z = -tmp_size[0] / 2 + hard_width * 1, hard_height, -tmp_size[2] / 2 + hard_depth * 1
                if neighbor_rest[1] + neighbor_base[1] < neighbor_rest[3] + neighbor_base[3]:
                    tmp_x = group_size[0] / 2 - hard_width * 1
            # 靠墙 餐桌
            elif group_vertical_flag >= 1:
                tmp_x, tmp_y, tmp_z = -tmp_size[0] / 2 + hard_width * 1, hard_height, 0
            # 悬空 沙发
            else:
                tmp_x, tmp_y, tmp_z = -tmp_size[0] / 2 + hard_width * 1, hard_height, -tmp_size[2] / 2 + hard_depth * 1
            add_x = tmp_z * math.sin(tmp_ang) + tmp_x * math.cos(tmp_ang)
            add_z = tmp_z * math.cos(tmp_ang) - tmp_x * math.sin(tmp_ang)
            new_x = tmp_pos[0] + add_x
            new_y = tmp_y
            new_z = tmp_pos[2] + add_z
            anchor_one = {
                'id': '',
                'type': 'Wall',
                'role': 'wall',
                'position': [new_x, new_y, new_z]
            }
            if len(anchor_one) > 0:
                scene_copy['anchor_hard'].append(anchor_one)
        # 软装检测
        scene_copy['anchor_soft'] = []
        soft_height_min, soft_height_max = 1.2, 1.6
        if len(group_main) > 0 and 'obj_list' in group_main:
            object_list = group_main['obj_list']
            anchor_one = {}
            for object_idx, object_one in enumerate(object_list):
                object_role, object_entity = '', ''
                if 'role' in object_one:
                    object_role = object_one['role']
                if 'entityId' in object_one:
                    object_entity = object_one['entityId']
                if object_role in ['sofa']:
                    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                    object_pos = object_one['position'][:]
                    object_pos[1] = object_pos[1] + object_size[1] + 0.2
                    # 规范高度
                    norm_height = int(object_pos[1] / 0.20) * 0.20 + 0.20
                    norm_height = max(soft_height_min, norm_height)
                    norm_height = min(soft_height_max, norm_height)
                    object_pos[1] = norm_height
                    # 增加锚点
                    anchor_one = {
                        'id': object_one['id'],
                        'type': group_type,
                        'role': object_role,
                        'position': object_pos,
                        'entityId': object_entity
                    }
                elif object_role in ['table', 'bed']:
                    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                    object_pos = object_one['position'][:]
                    object_pos[1] = object_pos[1] + object_size[1] + 0.2
                    # 规范化
                    norm_height = int(object_pos[1] / 0.20) * 0.20 + 0.20
                    norm_height = max(soft_height_min, norm_height)
                    norm_height = min(soft_height_max, norm_height)
                    object_pos[1] = norm_height
                    # 增加锚点
                    anchor_one = {
                        'id': object_one['id'],
                        'type': group_type,
                        'role': object_role,
                        'position': object_pos,
                        'entityId': object_entity
                    }
                    break
            if len(anchor_one) > 0:
                scene_copy['anchor_soft'].append(anchor_one)

        # 添加场景
        scene_list.append(scene_copy)

    # 相机高度
    if 0.1 < abs(room_lift) < 10:
        for scene_one in scene_list:
            camera_one = scene_one['camera']
            camera_one['pos'][1] += room_lift
            camera_one['target'][1] += room_lift
            pass

    # 返回机位
    return scene_list


# 检测机位
def room_mark_soft(room_info, scheme_info, scene_info):
    include_set, occlude_set = [], []
    if 'group' not in scheme_info:
        return include_set, occlude_set
    if 'camera' not in scene_info:
        return include_set, occlude_set
    # 房间信息
    room_type, room_area = '', 0
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    # 相机信息
    camera_info = scene_info['camera']
    camera_pos, target_pos = camera_info['pos'], camera_info['target']
    dis, ang = xyz_to_ang(camera_pos[0], camera_pos[2], target_pos[0], target_pos[2])
    near, far = dis, 5
    if 'near' in camera_info and 'far' in camera_info:
        near, far = camera_info['near'], camera_info['far']
    near = max(near * 0.8, near - 0.2)
    far = min(far, 10)
    fov = camera_info['fov'] / 180 * math.pi
    # 物品信息
    group_list = scheme_info['group']
    for group_idx, group_one in enumerate(group_list):
        group_type, object_list = '', []
        if 'type' in group_one:
            group_type = group_one['type']
        if 'obj_list' in group_one:
            object_list = group_one['obj_list']
        for object_idx, object_one in enumerate(object_list):
            object_key = object_one['id']
            if object_key.startswith('link_'):
                continue
            object_type, object_role = object_one['type'], object_one['role']
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_pos, object_rot = object_one['position'], object_one['rotation']
            if min(object_size[0], object_size[2]) > 10:
                continue
            elif min(object_size[0], object_size[2]) > 2 and room_type in ['Kitchen']:
                continue
            if group_type in GROUP_RULE_FUNCTIONAL:
                if 'art' in object_type or 'ceiling light' in object_type or 'lamp' in object_type:
                    pass
                elif object_role in ['', 'accessory']:
                    relate_role = ''
                    if 'relate_role' in object_one:
                        relate_role = object_one['relate_role']
                    if object_pos[1] < 0.50 and object_pos[1] + object_size[1] > 0.75 and relate_role in ['table', 'side table', 'rug']:
                        pass
                    else:
                        continue
            elif group_type in GROUP_RULE_DECORATIVE:
                if 'art' in object_type or 'ceiling light' in object_type or 'lamp' in object_type:
                    pass
                elif 'curtain' in object_type:
                    pass
                else:
                    continue
            else:
                continue
            # 锚点信息
            object_ang = rot_to_ang(object_rot)
            object_bot = object_pos[1] + object_size[1] * 0.0
            object_mid = object_pos[1] + object_size[1] * 0.5
            object_top = object_pos[1] + object_size[1] * 1.0
            camera_dis, camera_ang = xyz_to_ang(object_pos[0], object_pos[2], camera_pos[0], camera_pos[2])
            camera_dis_x = camera_dis * math.sin(camera_ang - object_ang)
            camera_dis_z = camera_dis * math.cos(camera_ang - object_ang)
            width_x, width_z = object_size[0], object_size[2]
            # 锚点靠背
            tmp_x = -width_x / 2
            tmp_z = -width_z / 2
            add_x1 = tmp_z * math.sin(object_ang) + tmp_x * math.cos(object_ang)
            add_z1 = tmp_z * math.cos(object_ang) - tmp_x * math.sin(object_ang)
            tmp_x = width_x / 2
            tmp_z = -width_z / 2
            add_x2 = tmp_z * math.sin(object_ang) + tmp_x * math.cos(object_ang)
            add_z2 = tmp_z * math.cos(object_ang) - tmp_x * math.sin(object_ang)
            # 锚点覆盖
            object_pos_x, object_pos_z = object_pos[0], object_pos[2]
            fix_0 = room_mark_point(camera_pos[0], camera_pos[2], object_pos_x, object_pos_z, ang, fov, near, far)
            object_pos_x, object_pos_z = object_pos[0] + add_x1, object_pos[2] + add_z1
            fix_1 = room_mark_point(camera_pos[0], camera_pos[2], object_pos_x, object_pos_z, ang, fov, near, far)
            object_pos_x, object_pos_z = object_pos[0] + add_x2, object_pos[2] + add_z2
            fix_2 = room_mark_point(camera_pos[0], camera_pos[2], object_pos_x, object_pos_z, ang, fov, near, far)
            if fix_0 + fix_1 + fix_2 >= 2:
                object_one['vision'] = 1
                object_id = object_one['id']
                if object_id not in include_set:
                    include_set.append(object_id)
            # 锚点穿插
            if abs(camera_dis_x) <= width_x * 0.5 + 0.001 and abs(camera_dis_z) <= width_z * 0.5 + 0.001:
                if object_role in ['sofa', 'bed']:
                    pass
                elif object_bot <= camera_pos[1] < object_top + 0.1:
                    # 机位上升
                    if object_top + 0.1 <= 1.25:
                        camera_pos[1] = object_top + 0.1
                        target_pos[1] = object_top + 0.1
                    # 机位前移
                    elif dis > 0.001:
                        dlt_x, dlt_z = target_pos[0] - camera_pos[0], target_pos[2] - camera_pos[2]
                        mov_d = min(width_x, width_z, 1) + 0.05
                        if abs(ang_to_ang(ang - object_ang - math.pi / 2)) < 0.1:
                            mov_d = width_x * 0.5 + 0.05 - camera_dis_x
                        elif abs(ang_to_ang(ang - object_ang + math.pi / 2)) < 0.1:
                            mov_d = width_x * 0.5 + 0.05 + camera_dis_x
                        elif abs(ang_to_ang(ang - object_ang)) < 0.1:
                            mov_d = width_z * 0.5 + 0.05 - camera_dis_z
                        elif abs(ang_to_ang(ang - object_ang + math.pi)) < 0.1:
                            mov_d = width_z * 0.5 + 0.05 + camera_dis_z
                        mov_x, mov_z = dlt_x * mov_d / dis, dlt_z * mov_d / dis
                        camera_pos[0] += mov_x
                        camera_pos[2] += mov_z
                        target_pos[0] += mov_x
                        target_pos[2] += mov_z
            elif fix_0 + fix_1 + fix_2 >= 2 and camera_dis > 0.001:
                if 'lamp' in object_type or 'plant' in object_type or object_role in ['', 'accessory']:
                    tilt_bot = math.atan((object_bot - camera_pos[1]) / camera_dis)
                    tilt_mid = math.atan((object_mid - camera_pos[1]) / camera_dis)
                    tilt_top = math.atan((object_top - camera_pos[1]) / camera_dis)
                    if tilt_mid <= 0 - fov * 0.25 and tilt_top <= 0 + fov * 0.10 and 2 <= camera_dis <= 4:
                        occlude_set.append(object_id)
                    elif tilt_bot <= 0 - fov * 0.25 and tilt_top <= 0 + fov * 0.10 and 0 <= camera_dis <= 2:
                        occlude_set.append(object_id)
    scene_info['vision'] = include_set
    scene_info['hidden'] = occlude_set
    return include_set, occlude_set


# 检测机位 判断户型与视截体
def room_mark_wall(room_info, group_info, scene_info):
    if 'camera' not in scene_info:
        return
    # 相机参数
    camera_info = scene_info['camera']
    fov = camera_info['fov'] / 180 * math.pi
    pos_0, pos_1 = camera_info['pos'], camera_info['target']
    dis, ang = xyz_to_ang(pos_0[0], pos_0[2], pos_1[0], pos_1[2])
    near, far = dis, 5
    if 'near' in camera_info and 'far' in camera_info:
        near, far = camera_info['near'], camera_info['far']
    # 组合矩形
    group_rect = compute_furniture_rect(group_info['size'], group_info['position'], group_info['rotation'])
    group_near, group_far = 100, 0
    for edge_idx in range(int(len(group_rect) / 2)):
        x, z = group_rect[2 * edge_idx], group_rect[2 * edge_idx + 1]
        dis_new, ang_new = xyz_to_ang(pos_0[0], pos_0[2], x, z)
        dis_cos = abs(dis_new * math.cos(ang_new - ang))
        group_near = min(dis_cos, group_near)
        group_far = max(dis_cos, group_far)
    near = min(group_near, near)
    far = group_far
    mid = (near + far) * 0.5
    # 标记部件
    mark_floor, mark_door, mark_window = [], [], []

    # 标记墙体
    floor_pts = room_info['floor']
    floor_len = int(len(floor_pts) / 2)
    for i in range(floor_len - 1):
        x1, y1, x2, y2 = floor_pts[2 * i + 0], floor_pts[2 * i + 1], floor_pts[2 * i + 2], floor_pts[2 * i + 3]
        if room_mark_line(pos_0[0], pos_0[2], x1, y1, x2, y2, ang, fov, near, far, mid):
            mark_floor.append([x1, y1, x2, y2])
            continue
    # 标记部件
    set_list = [room_info['door_info'], room_info['hole_info'], room_info['window_info'], room_info['baywindow_info']]
    set_list = []
    for set_idx, set_one in enumerate(set_list):
        for info_one in set_one:
            unit_one = []
            if 'pts' in info_one:
                unit_one = info_one['pts']
            unit_len = int(len(unit_one) / 2)
            mark_flag = False
            for i in range(unit_len - 1):
                x1, y1, x2, y2 = unit_one[2 * i + 0], unit_one[2 * i + 1], unit_one[2 * i + 2], unit_one[2 * i + 3]
                if room_mark_line(pos_0[0], pos_0[2], x1, y1, x2, y2, ang, fov, near, far, mid):
                    mark_flag = True
                    break
            if mark_flag:
                if set_idx < 2:
                    mark_door.append(unit_one)
                else:
                    mark_window.append(unit_one)

    # 返回信息
    return mark_floor, mark_door, mark_window


# 检测机位 判断户型与机位锚点连线
def room_mark_link(room_info, scene_info):
    # 墙体信息
    floor_pts = room_info['floor']
    floor_len = int(len(floor_pts) / 2)
    # 锚地信息
    camera_info, camera_pos = {}, []
    anchor_list, anchor_pos = [], []
    if 'camera' in scene_info:
        camera_info = scene_info['camera']
        if 'pos' in camera_info:
            camera_pos = camera_info['pos']
    if 'anchor_link' in scene_info:
        anchor_list = scene_info['anchor_link']
    for anchor_info in anchor_list:
        if 'position' in anchor_info:
            anchor_pos = anchor_info['position']
        if len(camera_pos) < 3 or len(anchor_pos) < 3:
            continue
        # 锚点线段
        x1, z1, x2, z2 = camera_pos[0], camera_pos[2], anchor_pos[0], anchor_pos[2]
        dis_old, ang_old = room_calc_vector(x1, z1, x2, z2)
        if dis_old < 0.2:
            continue
        rat_min, rat_ang, rat_pts = 2, 0, []
        # 墙体线段
        for i in range(floor_len - 1):
            x3, z3, x4, z4 = floor_pts[2 * i + 0], floor_pts[2 * i + 1], floor_pts[2 * i + 2], floor_pts[2 * i + 3]
            dis_new, ang_new = room_calc_vector(x3, z3, x4, z4)
            if dis_new < 0.01:
                continue
            if abs(ang_to_ang(ang_new - ang_old)) < 0.01 or abs(ang_to_ang(ang_new - ang_old - math.pi)) < 0.01:
                continue
            dis_3, ang_3 = room_calc_vector(x1, z1, x3, z3)
            dis_4, ang_4 = room_calc_vector(x1, z1, x4, z4)
            tmp_x_3, tmp_z_3 = dis_3 * math.cos(ang_3 - ang_old), dis_3 * math.sin(ang_3 - ang_old)
            tmp_x_4, tmp_z_4 = dis_4 * math.cos(ang_4 - ang_old), dis_4 * math.sin(ang_4 - ang_old)
            if tmp_z_3 * tmp_z_4 < -0.01:
                rat_x = abs(tmp_z_3) / (abs(tmp_z_3) + abs(tmp_z_4))
                dis_x = tmp_x_3 * (1 - rat_x) + tmp_x_4 * rat_x
                rat_c = dis_x / dis_old
                if 0 - 0.2 / dis_new <= rat_c <= 1 + 0.2 / dis_new and rat_c < rat_min:
                    rat_min, rat_ang = rat_c, ang_new
                    x_s1 = floor_pts[(2 * i - 2 + len(floor_pts)) % len(floor_pts)]
                    z_s1 = floor_pts[(2 * i - 1 + len(floor_pts)) % len(floor_pts)]
                    x_s2 = floor_pts[(2 * i + 4 + len(floor_pts)) % len(floor_pts)]
                    z_s2 = floor_pts[(2 * i + 5 + len(floor_pts)) % len(floor_pts)]
                    # 前序
                    dis_s1, ang_s1 = room_calc_vector(x_s1, z_s1, x3, z3)
                    if dis_s1 < 0.01:
                        x_s1 = floor_pts[(2 * i - 4 + len(floor_pts)) % len(floor_pts)]
                        z_s1 = floor_pts[(2 * i - 3 + len(floor_pts)) % len(floor_pts)]
                        dis_s1, ang_s1 = room_calc_vector(x_s1, z_s1, x3, z3)
                    # 后续
                    dis_s2, ang_s2 = room_calc_vector(x4, z4, x_s2, z_s2)
                    if dis_s2 < 0.01:
                        x_s2 = floor_pts[(2 * i + 6 + len(floor_pts)) % len(floor_pts)]
                        z_s2 = floor_pts[(2 * i + 7 + len(floor_pts)) % len(floor_pts)]
                        dis_s2, ang_s2 = room_calc_vector(x4, z4, x_s2, z_s2)
                    dis_hor, dis_rat, dis_ver = 0.4, 0.5, 0.4
                    if abs(ang_to_ang(ang_new - ang_s1 + math.pi / 2)) < 0.1 and \
                            abs(ang_to_ang(ang_new - ang_s2 + math.pi / 2)) < 0.1:
                        dis_hor, dis_rat = 0.4, 0 - 0.4 / dis_new
                    elif abs(ang_to_ang(ang_new - ang_s1 - math.pi / 2)) < 0.1 and \
                            abs(ang_to_ang(ang_new - ang_s2 - math.pi / 2)) < 0.1:
                        dis_hor, dis_rat = 0.4, 1 + 0.4 / dis_new
                    elif abs(ang_to_ang(ang_3 - ang_old)) < abs(ang_to_ang(ang_4 - ang_old)):
                        dis_hor, dis_rat = 0.0, 0 - 0.0 / dis_new
                    else:
                        dis_hor, dis_rat = 0.0, 1 + 0.0 / dis_new
                    x_new = x3 * (1 - dis_rat) + x4 * dis_rat
                    z_new = z3 * (1 - dis_rat) + z4 * dis_rat
                    x_new += dis_ver * math.sin(ang_new + math.pi / 2)
                    z_new += dis_ver * math.cos(ang_new + math.pi / 2)
                    rat_pts = [x_new, z_new]
        if 0 <= rat_min <= 1 and len(rat_pts) >= 2:
            x_new, z_new = rat_pts[0], rat_pts[1]
            anchor_info['position_fix'] = [x_new, anchor_pos[1], z_new]


# 检测机位 判断线段与视截体
def room_mark_line(x0, y0, x1, y1, x2, y2, ang, fov, near, far, mid):
    # 计算参数
    dis_1, ang_1 = xyz_to_ang(x0, y0, x1, y1)
    dis_2, ang_2 = xyz_to_ang(x0, y0, x2, y2)
    # 纠正参数
    fov_new = abs(fov)
    ang_1_new = ang_to_ang(ang_1 - ang)
    dis_1_new = dis_1 * math.cos(ang_1_new)
    ang_2_new = ang_to_ang(ang_2 - ang)
    dis_2_new = dis_2 * math.cos(ang_2_new)
    # 端点命中
    if abs(ang_1_new) < fov_new / 2 * 0.9 and near < dis_1_new < mid:
        return True
    if abs(ang_2_new) < fov_new / 2 * 0.9 and near < dis_2_new < mid:
        return True
    # 横跨命中
    if min(ang_1_new, ang_2_new) <= -math.pi / 2 or max(ang_1_new, ang_2_new) >= math.pi / 2:
        pass
    elif min(dis_1_new, dis_2_new) >= min(far, 3):
        pass
    elif min(dis_1_new, dis_2_new) >= min(mid, 3) and ang_1_new * ang_2_new < 0:
        pass
    elif min(ang_1_new, ang_2_new) <= -fov_new / 2 and max(ang_1_new, ang_2_new) >= fov_new / 2:
        if min(dis_1_new, dis_2_new) <= near * 1.0 <= max(dis_1_new, dis_2_new):
            return True
        if min(dis_1_new, dis_2_new) <= near * 0.8 <= max(dis_1_new, dis_2_new):
            return True
        if min(dis_1_new, dis_2_new) <= far <= max(dis_1_new, dis_2_new):
            return True
        if near < dis_1_new < far and near < dis_2_new < far:
            return True
    elif abs(ang_1_new) < fov_new / 2 < abs(ang_2_new) and ang_1_new * ang_2_new < 0:
        if near < dis_1_new < far:
            return True
    elif abs(ang_2_new) < fov_new / 2 < abs(ang_1_new) and ang_1_new * ang_2_new < 0:
        if near < dis_2_new < far:
            return True
    # 返回信息
    return False


# 检测机位 判断点位与视截体
def room_mark_point(x0, y0, x1, y1, ang, fov, near, far):
    # 计算参数
    dis_1, ang_1 = xyz_to_ang(x0, y0, x1, y1)
    # 纠正参数
    fov_new = abs(fov)
    ang_1_new = ang_to_ang(ang_1 - ang)
    dis_1_new = dis_1 * math.cos(ang_1_new)
    # 端点命中
    if abs(ang_1_new) < fov_new / 2 * 1.1 and near < dis_1_new < far:
        return 1
    return 0


# 计算角度
def room_calc_vector(x1, y1, x2, y2):
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


# 计算方位
def room_calc_locate(x1, z1, x2, z2, angle, width=1.0, depth=1.0, delta=0.1):
    # 左侧
    tmp_x, tmp_z = -width / 2, 0
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_left = x1 + add_x
    z1_left = z1 + add_z
    dis_left = (x1_left - x2) * (x1_left - x2) + (z1_left - z2) * (z1_left - z2)
    # 右侧
    tmp_x, tmp_z = width / 2, 0
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_right = x1 + add_x
    z1_right = z1 + add_z
    dis_right = (x1_right - x2) * (x1_right - x2) + (z1_right - z2) * (z1_right - z2)

    # 后侧
    tmp_x, tmp_z = 0, -depth / 2
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_back = x1 + add_x
    z1_back = z1 + add_z
    dis_back = (x1_back - x2) * (x1_back - x2) + (z1_back - z2) * (z1_back - z2)
    # 前侧
    tmp_x, tmp_z = 0, depth / 2
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_front = x1 + add_x
    z1_front = z1 + add_z
    dis_front = (x1_front - x2) * (x1_front - x2) + (z1_front - z2) * (z1_front - z2)

    # 返回
    flag_left, flag_back = 0, 0
    if dis_left < dis_right - delta:
        flag_left = 1
    elif dis_right < dis_left - delta:
        flag_left = -1
    if dis_back < dis_front - delta * 2:
        flag_back = 1
    elif dis_front < dis_back - delta * 2:
        flag_back = -1
    return flag_left, flag_back


# 计算距离
def room_calc_distance(line, ratio, point, depth=0, mode=2):
    if len(point) < 2:
        return 10, 10, 10
    p1 = line['p1'][:]
    p2 = line['p2'][:]
    ratio_po = (ratio[0] + ratio[1]) / 2
    if depth > 0.01:
        angle = line['angle'] + math.pi / 2
        x_delta = depth * math.sin(angle)
        y_delta = depth * math.cos(angle)
        p1[0] += x_delta
        p2[0] += x_delta
        p1[1] += y_delta
        p2[1] += y_delta
    p1_suit = [p1[0] * (1 - ratio[0]) + p2[0] * ratio[0], p1[1] * (1 - ratio[0]) + p2[1] * ratio[0]]
    p2_suit = [p1[0] * (1 - ratio[1]) + p2[0] * ratio[1], p1[1] * (1 - ratio[1]) + p2[1] * ratio[1]]
    p3_suit = [p1[0] * (1 - ratio_po) + p2[0] * ratio_po, p1[1] * (1 - ratio_po) + p2[1] * ratio_po]
    if mode == 1:
        distance_p1 = abs(p1_suit[0] - point[0]) + abs(p1_suit[1] - point[1])
        distance_p2 = abs(p2_suit[0] - point[0]) + abs(p2_suit[1] - point[1])
        distance_p3 = abs(p3_suit[0] - point[0]) + abs(p3_suit[1] - point[1])
    else:
        distance_p1 = math.sqrt((p1_suit[0] - point[0]) * (p1_suit[0] - point[0]) + (p1_suit[1] - point[1]) * (p1_suit[1] - point[1]))
        distance_p2 = math.sqrt((p2_suit[0] - point[0]) * (p2_suit[0] - point[0]) + (p2_suit[1] - point[1]) * (p2_suit[1] - point[1]))
        distance_p3 = math.sqrt((p3_suit[0] - point[0]) * (p3_suit[0] - point[0]) + (p3_suit[1] - point[1]) * (p3_suit[1] - point[1]))
    return distance_p1, distance_p2, distance_p3


# 计算相机
def room_calc_camera(group_main, camera_info, camera_pos, view_mode=0):
    # 原有参数
    pos_old_1, pos_old_2, dis_old = camera_info['pos'], camera_info['target'], 2.5
    dis_tar, ang_tar = xyz_to_ang(pos_old_1[0], pos_old_1[2], pos_old_2[0], pos_old_2[2])
    # 组合位置
    group_type = group_main['type']
    group_pos, group_ang = group_main['position'], rot_to_ang(group_main['rotation'])
    group_size, group_offset = group_main['size'], group_main['offset']
    pos_grp = group_pos[:]
    # 相机位置
    pos_new_1 = camera_pos[:]
    if pos_new_1[1] < UNIT_HEIGHT_VIEW_MIN:
        pos_new_1[1] = UNIT_HEIGHT_VIEW_MIN
    add_x, add_z = pos_new_1[0] - pos_grp[0], pos_new_1[2] - pos_grp[2]
    tmp_x = add_z * math.sin(-group_ang) + add_x * math.cos(-group_ang)
    tmp_z = add_z * math.cos(-group_ang) - add_x * math.sin(-group_ang)
    dis_new, ang_new = xyz_to_ang(pos_grp[0], pos_grp[2], pos_new_1[0], pos_new_1[2])
    dis_rat = max(dis_new / dis_old, 0.5)
    # 相机广角
    fov_max, fov_add = 75, 1.0
    if view_mode == VIEW_MODE_SINGLE and group_type in ['Armoire', 'Cabinet']:
        if dis_new < min(max(group_size[0], group_size[2], 1.5) * 0.5, 1.5):
            fov_max = 90
    fov_new = min(camera_info['fov'] / dis_rat, fov_max)
    fov_dlt = max(group_size[0], group_size[2]) * 0.5 + fov_add
    if dis_new * math.tan(fov_new / 2 * math.pi / 180) < fov_dlt:
        dis_all = math.sqrt(fov_dlt * fov_dlt + dis_new * dis_new)
        fov_cal = math.asin(fov_dlt / dis_all) / math.pi * 180 * 2
        fov_new = min(fov_cal, fov_max)
    # 目标位置
    pos_new_2 = [pos_grp[0] + add_x * 0.9, pos_new_1[1], pos_grp[2] + add_z * 0.9]
    if pos_new_2[1] > pos_new_1[1]:
        pos_new_2[1] = pos_new_1[1]
    dis_new, ang_tar = xyz_to_ang(pos_new_1[0], pos_new_1[2], pos_grp[0], pos_grp[2])
    # 目标距离
    group_size_min = group_size
    if 'size_min' in group_main and len(group_main['size_min']) >= 4:
        group_size_min = group_main['size_min']
    dis_grp = math.sqrt(group_size_min[0] / 2 * group_size_min[0] / 2 + group_size_min[2] / 2 * group_size_min[2] / 2)
    if dis_new - dis_grp < dis_tar + 0.1:
        dis_tar = dis_new - dis_grp - 0.1
        if dis_tar < 0.2:
            dis_tar = 0.2
    tar_x, tar_z = dis_tar * math.sin(ang_tar), dis_tar * math.cos(ang_tar)
    pos_new_2[0] = pos_new_1[0] + tar_x
    pos_new_2[2] = pos_new_1[2] + tar_z
    # 相机高度
    pos_lift_1 = pos_new_1[1] * dis_rat
    pos_lift_2 = pos_new_2[1] * dis_rat
    pos_new_1[1], pos_new_2[1] = pos_lift_1, pos_lift_2
    if pos_new_1[1] < UNIT_HEIGHT_VIEW_MIN or pos_new_1[1] > UNIT_HEIGHT_VIEW_MAX:
        pos_dlt = UNIT_HEIGHT_VIEW_MID - pos_new_1[1]
        pos_new_1[1] += (pos_dlt * 1.0)
        pos_new_2[1] += (pos_dlt * 1.0)

    # 俯仰角度 TODO:
    pitch_new = 0
    if dis_new > 0.01 and abs(pos_new_1[1] - pos_new_2[1]) > dis_new * 0.01:
        lift_dlt = pos_new_2[1] - pos_new_1[1]
        pitch_new = math.atan(lift_dlt / dis_new) * 180 / math.pi
        pass
    # 取景距离
    near_new = min(camera_info['near'] * dis_rat + 0.01, dis_tar + 0.05)
    far_new = camera_info['far']
    if far_new < dis_new * 2:
        far_new = dis_new * 2
    # 更新机位
    camera_info['pitch'] = pitch_new
    camera_info['fov'] = fov_new
    camera_info['near'] = near_new
    camera_info['far'] = far_new
    camera_info['pos'] = pos_new_1
    camera_info['target'] = pos_new_2
    return camera_info


# 判断相机
def room_judge_camera(group_list, camera_info):
    camera_pos = camera_info['pos']
    for group_idx, group_one in enumerate(group_list):
        if len(group_one) <= 0:
            continue
        group_type, group_size = group_one['type'], group_one['size']
        if group_type in ['Armoire', 'Cabinet', 'Appliance']:
            pass
        else:
            continue
        group_pos, group_ang = group_one['position'], rot_to_ang(group_one['rotation'])
        mov_x, mov_z = camera_pos[0] - group_pos[0], camera_pos[2] - group_pos[2]
        if abs(mov_x) + abs(mov_z) >= 5:
            continue
        tmp_x = mov_z * math.sin(-group_ang) + mov_x * math.cos(-group_ang)
        tmp_z = mov_z * math.cos(-group_ang) - mov_x * math.sin(-group_ang)
        if abs(tmp_x) < group_size[0] / 2 and abs(tmp_z) < group_size[2] / 2:
            return False
    return True


# 融合路线
def room_path_merge(path_old, path_new, room_area=10):
    path_fix = 1
    # 参数
    dis_old, dis_new = path_old['width'], path_new['width']
    ang_old, ang_new = path_old['angle'], path_new['angle']
    role_old, role_new = '', ''
    if 'role' in path_old:
        role_old = path_old['role']
    if 'role' in path_new:
        role_new = path_new['role']
    # 距离
    dlt_tmp_x, dlt_tmp_z = max(0.04 * room_area, 1.0), max(0.02 * room_area, 0.5)
    if path_new['type'] in [UNIT_TYPE_GROUP] and role_new in ['back']:
        dlt_tmp_z = 0.2
    elif path_new['type'] in [UNIT_TYPE_DOOR]:
        dlt_tmp_z = UNIT_WIDTH_DOOR * 0.50 + 0.1
    elif path_old['type'] in [UNIT_TYPE_GROUP] and role_old in ['main']:
        dlt_tmp_z = UNIT_WIDTH_DOOR * 1.00
    elif path_old['type'] in [UNIT_TYPE_GROUP] and path_new['type'] in [UNIT_TYPE_AISLE]:
        dlt_tmp_z = UNIT_WIDTH_DOOR * 0.50 + 0.1
        if 'width_dlt' in path_new and path_new['width_dlt'] < dlt_tmp_z:
            dlt_tmp_z = path_new['width_dlt']
    elif path_old['type'] in [UNIT_TYPE_AISLE] and path_new['type'] in [UNIT_TYPE_AISLE]:
        dlt_tmp_z = UNIT_WIDTH_DOOR * 0.50 + 0.0
    elif path_old['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] \
            and path_new['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE]:
        dlt_tmp_z = UNIT_WIDTH_DOOR * 1.00
    elif path_old['type'] in [UNIT_TYPE_AISLE] and dis_old > UNIT_WIDTH_DOOR * 4:
        dlt_tmp_z = UNIT_WIDTH_DOOR * 1.00
    # 平行
    if abs(ang_to_ang(ang_new - ang_old - 0)) < 0.1 or abs(ang_to_ang(ang_new - ang_old - math.pi)) < 0.1:
        x1, z1, x2, z2 = path_old['p1'][0], path_old['p1'][1], path_old['p2'][0], path_old['p2'][1]
        x3, z3, x4, z4 = path_new['p1'][0], path_new['p1'][1], path_new['p2'][0], path_new['p2'][1]
        dis_3, ang_3 = room_calc_vector(x1, z1, x3, z3)
        dis_4, ang_4 = room_calc_vector(x1, z1, x4, z4)
        tmp_x_3, tmp_z_3 = dis_3 * math.cos(ang_3 - ang_old), dis_3 * math.sin(ang_3 - ang_old)
        tmp_x_4, tmp_z_4 = dis_4 * math.cos(ang_4 - ang_old), dis_4 * math.sin(ang_4 - ang_old)
        # 重合
        if abs(tmp_z_3) <= dlt_tmp_z:
            if -dlt_tmp_x < max(tmp_x_3, tmp_x_4) and min(tmp_x_3, tmp_x_4) < dis_old + dlt_tmp_x:
                rat_1 = min(min(tmp_x_3, tmp_x_4) / dis_old, 0)
                rat_2 = max(max(tmp_x_3, tmp_x_4) / dis_old, 1)
                x1_new = x1 * (1 - rat_1) + x2 * rat_1
                z1_new = z1 * (1 - rat_1) + z2 * rat_1
                x2_new = x1 * (1 - rat_2) + x2 * rat_2
                z2_new = z1 * (1 - rat_2) + z2 * rat_2
                path_width, path_angle = room_calc_vector(x1_new, z1_new, x2_new, z2_new)
                path_old['width'], path_old['angle'] = path_width, path_angle
                path_old['p1'], path_old['p2'] = [x1_new, z1_new], [x2_new, z2_new]
                if path_new['type'] > path_old['type']:
                    if path_old['type'] in [UNIT_TYPE_GROUP] and path_new['type'] in [UNIT_TYPE_DOOR]:
                        if abs(tmp_z_3) < dlt_tmp_z:
                            if tmp_x_3 <= tmp_x_4:
                                path_old['score_pre'] = 4
                            else:
                                path_old['score_post'] = 4
                    path_old['type'] = path_new['type']
                if path_new['type'] in [UNIT_TYPE_DOOR] and rat_2 >= 1:
                    if tmp_x_4 > tmp_x_3 and path_new['score_post'] == 4:
                        path_old['score_post'] = 4
                    if tmp_x_3 > tmp_x_4 and path_new['score_pre'] == 4:
                        path_old['score_post'] = 4
                path_fix = 0
    if path_fix <= 0 and role_new in ['main', 'back']:
        path_old['role'] = role_new
    return path_fix


# 对齐路线
def room_path_aside(path_old, path_new):
    path_fix = 1
    # 参数
    dis_old, dis_new = path_old['width'], path_new['width']
    ang_old, ang_new = path_old['angle'], path_new['angle']
    dlt_tmp_x, dlt_tmp_z = 1.0, 0.4
    # 平行
    if abs(ang_to_ang(ang_new - ang_old - 0)) < 0.1 or abs(ang_to_ang(ang_new - ang_old - math.pi)) < 0.1:
        x1, z1, x2, z2 = path_old['p1'][0], path_old['p1'][1], path_old['p2'][0], path_old['p2'][1]
        x3, z3, x4, z4 = path_new['p1'][0], path_new['p1'][1], path_new['p2'][0], path_new['p2'][1]
        dis_3, ang_3 = room_calc_vector(x1, z1, x3, z3)
        dis_4, ang_4 = room_calc_vector(x1, z1, x4, z4)
        tmp_x_3, tmp_z_3 = dis_3 * math.cos(ang_3 - ang_old), dis_3 * math.sin(ang_3 - ang_old)
        tmp_x_4, tmp_z_4 = dis_4 * math.cos(ang_4 - ang_old), dis_4 * math.sin(ang_4 - ang_old)
        # 平行
        if 0 < abs(tmp_z_3) < dlt_tmp_z * 2.0:
            path_cur, dis_cur = path_old, dis_old
            x1_cur, z1_cur, x2_cur, z2_cur = path_old['p1'][0], path_old['p1'][1], path_old['p2'][0], path_old['p2'][1]
            x1_new, z1_new, x2_new, z2_new = x1_cur, z1_cur, x2_cur, z2_cur
            if abs(dis_cur) <= 0.01:
                pass
            elif path_old['type'] in [UNIT_TYPE_AISLE] and path_new['type'] in [UNIT_TYPE_DOOR] and abs(tmp_z_3) > dlt_tmp_z:
                pass
            elif path_old['type'] in [UNIT_TYPE_DOOR] and path_new['type'] in [UNIT_TYPE_AISLE] and abs(tmp_z_3) > dlt_tmp_z:
                pass
            elif -min(dlt_tmp_x, dis_cur * 0.4) < max(tmp_x_3, tmp_x_4) < min(dlt_tmp_x, dis_cur * 0.4):
                rat_1 = max(tmp_x_3, tmp_x_4) / dis_cur
                if 0 < rat_1 < 1 and path_cur['score_pre'] == 4 and path_cur['type'] in [UNIT_TYPE_DOOR]:
                    rat_1 = 0
                x1_new = x1_cur * (1 - rat_1) + x2_cur * rat_1
                z1_new = z1_cur * (1 - rat_1) + z2_cur * rat_1
                path_cur['p1'] = [x1_new, z1_new]
                # 更新
                path_width, path_angle = room_calc_vector(x1_new, z1_new, x2_new, z2_new)
                path_cur['width'], path_cur['angle'] = path_width, path_angle
                path_fix = 1
            elif dis_cur - min(dlt_tmp_x, dis_cur * 0.4) < min(tmp_x_3, tmp_x_4) < dis_cur + min(dlt_tmp_x, dis_cur * 0.4):
                rat_2 = min(tmp_x_3, tmp_x_4) / dis_cur
                if 0 < rat_2 < 1 and path_cur['score_post'] == 4 and path_cur['type'] in [UNIT_TYPE_DOOR]:
                    rat_2 = 1
                x2_new = x1_cur * (1 - rat_2) + x2_cur * rat_2
                z2_new = z1_cur * (1 - rat_2) + z2_cur * rat_2
                path_cur['p2'] = [x2_new, z2_new]
                # 更新
                path_width, path_angle = room_calc_vector(x1_new, z1_new, x2_new, z2_new)
                path_cur['width'], path_cur['angle'] = path_width, path_angle
                path_fix = 1
                pass
    return path_fix


# 交叉路线
def room_path_cross(path_old, path_new, room_area=10):
    path_fix = 1
    # 参数
    dis_old, dis_new = path_old['width'], path_new['width']
    ang_old, ang_new = path_old['angle'], path_new['angle']
    if abs(dis_new) < 0.01:
        path_fix = -1
        return path_fix
    dlt_tmp_x, dlt_tmp_z = max(min(room_area * 0.05, UNIT_WIDTH_DOOR), 0.2), max(min(room_area * 0.05, UNIT_WIDTH_DOOR), 0.2)
    if path_old['type'] in [UNIT_TYPE_DOOR] and path_new['type'] in [UNIT_TYPE_DOOR]:
        dlt_tmp_x = min(dlt_tmp_x, 0.5)
        dlt_tmp_z = min(dlt_tmp_z, 0.5)
    # 垂直
    if abs(ang_to_ang(ang_new - ang_old - math.pi / 2)) < 0.1 or abs(ang_to_ang(ang_new - ang_old + math.pi / 2)) < 0.1:
        x1, z1, x2, z2 = path_old['p1'][0], path_old['p1'][1], path_old['p2'][0], path_old['p2'][1]
        x3, z3, x4, z4 = path_new['p1'][0], path_new['p1'][1], path_new['p2'][0], path_new['p2'][1]
        dis_3, ang_3 = room_calc_vector(x1, z1, x3, z3)
        dis_4, ang_4 = room_calc_vector(x1, z1, x4, z4)
        tmp_x_3, tmp_z_3 = dis_3 * math.cos(ang_3 - ang_old), dis_3 * math.sin(ang_3 - ang_old)
        tmp_x_4, tmp_z_4 = dis_4 * math.cos(ang_4 - ang_old), dis_4 * math.sin(ang_4 - ang_old)
        score_pre_new, score_post_new = path_new['score_pre'], path_new['score_post']
        # 交叉
        if 0 - dlt_tmp_x < tmp_x_3 < dis_old + dlt_tmp_x:
            # path new
            x3_new, z3_new, x4_new, z4_new = x3, z3, x4, z4
            if tmp_x_3 <= 0 + 0.01 and path_old['score_pre'] >= 4 and tmp_z_3 * tmp_z_4 >= 0:
                pass
            elif tmp_x_3 >= dis_old - 0.01 and path_old['score_post'] >= 4 and tmp_z_3 * tmp_z_4 >= 0:
                pass
            elif tmp_x_3 <= 0 - 0.10 and path_old['score_post'] >= 4 \
                    and path_old['type'] in [UNIT_TYPE_DOOR] and path_new['type'] not in [UNIT_TYPE_DOOR]:
                pass
            elif tmp_x_3 >= dis_old + 0.10 and path_old['score_pre'] >= 4 \
                    and path_old['type'] in [UNIT_TYPE_DOOR] and path_new['type'] not in [UNIT_TYPE_DOOR]:
                pass
            elif abs(tmp_z_3) <= abs(tmp_z_4) and 0 - dlt_tmp_z < tmp_z_3 < 0 + dlt_tmp_z:
                rat_1, rat_2 = 0, 1
                if abs(dis_new) < 0.01:
                    pass
                elif path_new['score_pre'] == 4:
                    if tmp_x_3 < dis_old * 0.5 and path_old['score_pre'] < 4:
                        pass
                    elif tmp_x_3 > dis_old * 0.5 and path_old['score_post'] < 4:
                        pass
                    elif tmp_z_3 * tmp_z_4 >= 0:
                        if 0 - dlt_tmp_z * 0.5 < tmp_z_3 < 0 + dlt_tmp_z * 0.5 and tmp_z_3 < 0:
                            rat_1 = 0 - abs(tmp_z_3) / dis_new
                    else:
                        pass
                    if path_new['score_post'] < 4:
                        if tmp_z_3 * tmp_z_4 >= 0:
                            pass
                        elif path_new['type'] in [UNIT_TYPE_DOOR] and abs(tmp_z_4) > abs(tmp_z_3) * 2:
                            pass
                        else:
                            rat_2 = 1 - abs(tmp_z_4) / dis_new
                elif tmp_z_3 * tmp_z_4 >= 0:
                    rat_1 = 0 - abs(tmp_z_3) / dis_new
                else:
                    rat_1 = 0 + abs(tmp_z_3) / dis_new
                    if path_new['score_pre'] >= 4 and path_old['type'] in [UNIT_TYPE_GROUP]:
                        rat_1 = 0
                    elif path_new['score_pre'] == 1 and path_old['type'] in [UNIT_TYPE_DOOR] and path_new['type'] in [UNIT_TYPE_GROUP]:
                        rat_1 = 0
                x3_new = x3 * (1 - rat_1) + x4 * rat_1
                z3_new = z3 * (1 - rat_1) + z4 * rat_1
                x4_new = x3 * (1 - rat_2) + x4 * rat_2
                z4_new = z3 * (1 - rat_2) + z4 * rat_2
                path_new['p1'] = [x3_new, z3_new]
                path_new['p2'] = [x4_new, z4_new]
                path_width, path_angle = room_calc_vector(x3_new, z3_new, x4_new, z4_new)
                path_new['width'], path_new['angle'] = path_width, path_angle
                if path_old['type'] in [UNIT_TYPE_DOOR]:
                    path_new['score_pre'] = 4
                path_fix = 1
                pass
            elif abs(tmp_z_4) <= abs(tmp_z_3) and 0 - dlt_tmp_z < tmp_z_4 < 0 + dlt_tmp_z:
                rat_1, rat_2 = 0, 1
                if abs(dis_new) < 0.01:
                    pass
                elif path_new['score_post'] == 4:
                    if tmp_x_3 < dis_old * 0.5 and path_old['score_pre'] < 4:
                        pass
                    elif tmp_x_3 > dis_old * 0.5 and path_old['score_post'] < 4:
                        pass
                    elif tmp_z_3 * tmp_z_4 >= 0:
                        if 0 - dlt_tmp_z * 0.5 < tmp_z_4 < 0 + dlt_tmp_z * 0.5 and tmp_z_4 > 0:
                            rat_2 = 1 + abs(tmp_z_4) / dis_new
                    else:
                        pass
                    if path_new['score_pre'] < 4:
                        if tmp_z_3 * tmp_z_4 >= 0:
                            pass
                        elif path_new['type'] in [UNIT_TYPE_DOOR] and abs(tmp_z_3) > abs(tmp_z_4) * 2:
                            pass
                        else:
                            rat_2 = 1 - abs(tmp_z_4) / dis_new
                elif tmp_z_3 * tmp_z_4 >= 0:
                    rat_2 = 1 + abs(tmp_z_4) / dis_new
                else:
                    rat_2 = 1 - abs(tmp_z_4) / dis_new
                    if path_new['score_post'] >= 4 and path_old['type'] in [UNIT_TYPE_GROUP]:
                        rat_2 = 1
                    elif path_new['score_post'] == 1 and path_old['type'] in [UNIT_TYPE_DOOR] and path_new['type'] in [UNIT_TYPE_GROUP]:
                        rat_2 = 1
                x3_new = x3 * (1 - rat_1) + x4 * rat_1
                z3_new = z3 * (1 - rat_1) + z4 * rat_1
                x4_new = x3 * (1 - rat_2) + x4 * rat_2
                z4_new = z3 * (1 - rat_2) + z4 * rat_2
                path_new['p1'] = [x3_new, z3_new]
                path_new['p2'] = [x4_new, z4_new]
                path_width, path_angle = room_calc_vector(x3_new, z3_new, x4_new, z4_new)
                path_new['width'], path_new['angle'] = path_width, path_angle
                if path_old['type'] in [UNIT_TYPE_DOOR]:
                    path_new['score_post'] = 4
                path_fix = 1
            # path old
            x1_new, z1_new, x2_new, z2_new = x1, z1, x2, z2
            if path_fix == 1 and 0.001 < abs(tmp_x_3) < min(1.5, dis_new * 1.0, dis_old * 0.8):
                rat_1 = tmp_x_3 / dis_old
                if max(tmp_z_3, tmp_z_4) < 0 - dlt_tmp_z or min(tmp_z_3, tmp_z_4) > 0 + dlt_tmp_z:
                    pass
                elif abs(tmp_z_3) <= 0.05 and score_pre_new >= 4:
                    pass
                elif abs(tmp_z_4) <= 0.05 and score_post_new >= 4:
                    pass
                elif path_old['score_pre'] < 4:
                    x1_new = x1 * (1 - rat_1) + x2 * rat_1
                    z1_new = z1 * (1 - rat_1) + z2 * rat_1
                    path_old['p1'] = [x1_new, z1_new]
                    path_width, path_angle = room_calc_vector(x1_new, z1_new, x2_new, z2_new)
                    path_old['width'], path_old['angle'] = path_width, path_angle
                    if path_new['type'] in [UNIT_TYPE_DOOR]:
                        path_old['score_pre'] = 4
                elif path_old['score_pre'] == 4 and 0.001 < abs(tmp_x_3) < min(UNIT_TYPE_DOOR, dis_old * 0.2):
                    if path_new['type'] in [UNIT_TYPE_DOOR] and path_old['type'] not in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                        x1_new = x1 * (1 - rat_1) + x2 * rat_1
                        z1_new = z1 * (1 - rat_1) + z2 * rat_1
                        path_old['p1'] = [x1_new, z1_new]
                        path_width, path_angle = room_calc_vector(x1_new, z1_new, x2_new, z2_new)
                        path_old['width'], path_old['angle'] = path_width, path_angle
                        if path_new['type'] in [UNIT_TYPE_DOOR]:
                            path_old['score_pre'] = 1
            if path_fix == 1 and 0.001 < abs(tmp_x_3 - dis_old) < min(1.5, dis_new * 1.0, dis_old * 0.8):
                rat_2 = tmp_x_3 / dis_old
                if max(tmp_z_3, tmp_z_4) < 0 - dlt_tmp_z or min(tmp_z_3, tmp_z_4) > 0 + dlt_tmp_z:
                    pass
                elif abs(tmp_z_3) <= 0.05 and score_pre_new >= 4:
                    pass
                elif abs(tmp_z_4) <= 0.05 and score_post_new >= 4:
                    pass
                elif path_old['score_post'] < 4:
                    x2_new = x1 * (1 - rat_2) + x2 * rat_2
                    z2_new = z1 * (1 - rat_2) + z2 * rat_2
                    path_old['p2'] = [x2_new, z2_new]
                    path_width, path_angle = room_calc_vector(x1_new, z1_new, x2_new, z2_new)
                    path_old['width'], path_old['angle'] = path_width, path_angle
                    if path_new['type'] in [UNIT_TYPE_DOOR]:
                        path_old['score_post'] = 4
                elif path_old['score_post'] == 4 and abs(tmp_x_3 - dis_old) < min(0.5, dis_old * 0.2) and \
                        path_old['type'] in [UNIT_TYPE_AISLE] and path_new['type'] in [UNIT_TYPE_AISLE]:
                    x2_new = x1 * (1 - rat_2) + x2 * rat_2
                    z2_new = z1 * (1 - rat_2) + z2 * rat_2
                    path_old['p2'] = [x2_new, z2_new]
                    path_width, path_angle = room_calc_vector(x1_new, z1_new, x2_new, z2_new)
                    path_old['width'], path_old['angle'] = path_width, path_angle
                    if path_new['type'] in [UNIT_TYPE_DOOR]:
                        path_old['score_post'] = 4
                elif path_old['score_post'] == 4 and 0.001 < abs(tmp_x_3) < min(0.5, dis_old * 0.2):
                    if path_new['type'] in [UNIT_TYPE_DOOR] and path_old['type'] not in [UNIT_TYPE_DOOR, UNIT_TYPE_AISLE]:
                        x2_new = x1 * (1 - rat_2) + x2 * rat_2
                        z2_new = z1 * (1 - rat_2) + z2 * rat_2
                        path_old['p2'] = [x2_new, z2_new]
                        path_width, path_angle = room_calc_vector(x1_new, z1_new, x2_new, z2_new)
                        path_old['width'], path_old['angle'] = path_width, path_angle
                        if path_new['type'] in [UNIT_TYPE_DOOR]:
                            path_old['score_post'] = 1
    return path_fix


# 排序路线
def room_path_queue(path_cross, zero_pts=[]):
    path_final = []
    x0, z0 = -10, -10
    if len(zero_pts) >= 2:
        x0, z0 = zero_pts[0], zero_pts[1]
    path_len, path_end, path_used = len(path_cross), {}, {}
    for i in range(path_len):
        dis_min, idx_min = 1000, -1
        for path_idx, path_one in enumerate(path_cross):
            if path_idx in path_used:
                continue
            x1, z1, x2, z2 = path_one['p1'][0], path_one['p1'][1], path_one['p2'][0], path_one['p2'][1]
            dis_1, ang_1 = room_calc_vector(x0, z0, x1, z1)
            dis_2, ang_2 = room_calc_vector(x0, z0, x2, z2)
            dis_new, ang_new = min(dis_1, dis_2), path_one['angle']
            if len(path_end) > 0:
                ang_old = path_end['angle']
                if abs(ang_to_ang(ang_new - ang_old - 0)) < 0.1 or abs(ang_to_ang(ang_new - ang_old - math.pi)) < 0.1:
                    dis_new = min(dis_1, dis_2) - 1
                elif len(zero_pts) >= 2:
                    x0_new, z0_new = x0, z0
                    dis_1, ang_1 = room_calc_vector(x0_new, z0_new, x1, z1)
                    dis_2, ang_2 = room_calc_vector(x0_new, z0_new, x2, z2)
                    dis_new = min(dis_1, dis_2)
                    if dis_new > 1 and len(zero_pts) >= 2:
                        x0_new, z0_new = zero_pts[0], zero_pts[1]
                        dis_1, ang_1 = room_calc_vector(x0_new, z0_new, x1, z1)
                        dis_2, ang_2 = room_calc_vector(x0_new, z0_new, x2, z2)
                        dis_new = min(dis_1, dis_2, dis_new)
            if dis_new < dis_min:
                dis_min = dis_new
                idx_min = path_idx
        if 0 <= idx_min < path_len:
            path_one = path_cross[idx_min]
            path_end = path_one
            path_used[idx_min] = 1
            path_final.append(path_end)
            x0, z0 = path_end['p2'][0], path_end['p2'][1]
    return path_final


# 切分路线 点列
def room_path_point(path_list, step_width=1.5):
    path_point = []
    last_point = []
    for path_idx, path_one in enumerate(path_list):
        path_width, path_angle = path_one['width'], path_one['angle']
        x1, z1, x2, z2 = path_one['p1'][0], path_one['p1'][1], path_one['p2'][0], path_one['p2'][1]
        point_set = []
        if path_width < step_width * 0.5:
            pass
        elif path_width < step_width * 1.5:
            x3 = x1 * 0.5 + x2 * 0.5
            z3 = z1 * 0.5 + z2 * 0.5
            point_one = {
                'position': [x3, 0, z3],
                'direction': path_angle,
            }
            point_set = [point_one]
            # 添加
            path_point.append(point_one)
        elif path_width < step_width * 2.0:
            x3 = x1 * 0.5 + x2 * 0.5
            z3 = z1 * 0.5 + z2 * 0.5
            point_one = {
                'position': [x3, 0, z3],
                'direction': path_angle,
            }
            point_set = [point_one]
            # 添加
            path_point.append(point_one)
        else:
            point_cnt = int(path_width / step_width - 0.5) + 1
            point_dis = 0
            for point_idx in range(point_cnt):
                ratio = (point_idx + 0.5) * step_width / path_width
                if ratio > 1 + 0.1 / path_width:
                    continue
                elif ratio > 1 - 0.4 / path_width:
                    ratio = 1 - 0.4 / path_width
                x3 = x1 * (1 - ratio) + x2 * ratio
                z3 = z1 * (1 - ratio) + z2 * ratio
                point_one = {
                    'position': [x3, 0, z3],
                    'direction': path_angle,
                }
                point_set.append(point_one)
                path_point.append(point_one)
        path_one['point'] = point_set
    return path_list, path_point


# 切分路线 机位
def room_path_scene(point_list, group_main, group_side={}, point_near=0.75):
    if len(group_main) <= 0 and len(point_list) >= 1:
        pos, ang = point_list[0]['position'], point_list[0]['direction']
        group_main = {
            'type': '',
            'size': [0.2, 0.2, 0.2],
            'scale': [1, 1, 1],
            'position': pos[:],
            'rotation': [0, math.sin(ang / 2), 0, math.cos(ang / 2)],
            'offset': [0, 0, 0]
        }
    if len(group_main) <= 0:
        scene_set = []
        return scene_set
    # 最佳位置
    group_pos, group_ang = group_main['position'], rot_to_ang(group_main['rotation'])
    group_size, group_offset = group_main['size'], group_main['offset']
    tmp_x, tmp_z = 0, group_size[2] / 2
    if abs(group_offset[0]) > 0.5:
        tmp_x, tmp_z = group_offset[0], group_size[2] / 2
    add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
    add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
    pos_x, pos_z = group_pos[0] + add_x, group_pos[2] + add_z

    # 最近点位
    near_idx, near_dis, near_pos = 0, 100, []
    for point_idx, point_one in enumerate(point_list):
        point_pos = point_one['position']
        point_dis = abs(point_pos[0] - pos_x) + abs(point_pos[2] - pos_z)
        if point_dis < near_dis:
            near_dis = point_dis
            near_idx = point_idx
            near_pos = point_pos

    # 最近机位
    scene_info = room_copy_view(DEFAULT_SCENE_INFO)
    camera_info = scene_info['camera']
    camera_pos = [pos_x, UNIT_HEIGHT_VIEW_MID, pos_z]
    room_calc_camera(group_main, camera_info, camera_pos)

    # 全部机位
    scene_set = []
    point_cnt = len(point_list)
    param_set = room_move_param(group_main, group_side)
    point_fix = []
    for point_idx in range(point_cnt):
        move_idx = (near_idx + point_idx) % point_cnt
        move_pos = point_list[move_idx]['position']
        move_ang = point_list[move_idx]['direction']
        # 近点检测
        move_err = False
        for point_old in point_fix:
            delta_x, delta_z = move_pos[0] - point_old[0], move_pos[2] - point_old[2]
            if abs(delta_x) + abs(delta_z) < point_near:
                move_err = True
                break
        if move_err:
            continue
        else:
            point_fix.append(move_pos)
        if move_idx == near_idx and len(point_list) > 1:
            camera_new = room_move_scene(camera_info, move_pos, move_ang, param_set)
        else:
            camera_new = room_move_scene(camera_info, move_pos, move_ang, param_set)
        scene_set.append(camera_new)
        # 对齐机位
        camera_pos, camera_tar = camera_new['pos'], camera_new['target']
        if camera_pos[1] > UNIT_HEIGHT_VIEW_MAX:
            camera_pos[1] = UNIT_HEIGHT_VIEW_MAX
        camera_tar[1] = camera_pos[1]
    return scene_set


# 调整机位 参数
def room_move_param(group_main, group_side={}):
    param_set = []
    for group_one in [group_main, group_side]:
        if len(group_one) <= 0:
            continue
        group_pos, group_ang = group_one['position'], rot_to_ang(group_one['rotation'])
        group_size, group_offset = group_one['size'], group_one['offset']
        param_one = [group_pos[0], group_pos[2], group_ang, group_size[0], group_size[2], group_pos[0], group_pos[2]]
        if abs(group_offset[0]) > 0.5:
            tmp_x, tmp_z = group_offset[0], 0
            add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
            add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
            pos_x, pos_z = group_pos[0] + add_x, group_pos[2] + add_z
            param_one[-2], param_one[-1] = pos_x, pos_z
        param_set.append(param_one)
    return param_set


# 调整机位 相机
def room_move_scene(camera_old, move_pos, move_ang, move_loc=[]):
    camera_new = camera_old.copy()
    pos_old, tar_old = camera_old['pos'], camera_old['target']
    dis_tar, ang_tar = xyz_to_ang(pos_old[0], pos_old[2], tar_old[0], tar_old[2])
    pos_new = move_pos
    # mode 0
    dlt_x, dlt_z = pos_new[0] - pos_old[0], pos_new[2] - pos_old[2]
    source_0 = [pos_old[0] + dlt_x, pos_old[1], pos_old[2] + dlt_z]
    target_0 = [tar_old[0] + dlt_x, tar_old[1], tar_old[2] + dlt_z]
    # mode 1
    ang_dlt = move_ang - ang_tar
    tmp_x, tmp_z = tar_old[0] - pos_old[0], tar_old[2] - pos_old[2]
    add_x = tmp_z * math.sin(ang_dlt) + tmp_x * math.cos(ang_dlt)
    add_z = tmp_z * math.cos(ang_dlt) - tmp_x * math.sin(ang_dlt)
    source_1 = [pos_new[0] + 0, pos_old[1], pos_new[2] + 0]
    target_1 = [pos_new[0] + add_x, pos_old[1], pos_new[2] + add_z]
    # mode 2
    source_2 = source_1[:]
    target_2 = target_1[:]
    if len(move_loc) > 0:
        loc_tar = []
        for loc_one in move_loc:
            # 参数
            pos_grp, ang_grp = [loc_one[0], 0, loc_one[1]], loc_one[2]
            max_x, max_z = loc_one[3], loc_one[4]
            # 比较
            add_x, add_z = pos_new[0] - pos_grp[0], pos_new[2] - pos_grp[2]
            tmp_x = add_z * math.sin(-ang_grp) + add_x * math.cos(-ang_grp)
            tmp_z = add_z * math.cos(-ang_grp) - add_x * math.sin(-ang_grp)
            if abs(tmp_x) < max_x / 2 + 0.5 and abs(tmp_z) < max_z / 2 + 1.0:
                loc_tar = [loc_one[5], 0, loc_one[6]]
                break
        if len(loc_tar) > 0:
            dis_new, ang_new = xyz_to_ang(pos_new[0], pos_new[2], loc_tar[0], loc_tar[2])
            if abs(ang_to_ang(ang_new - math.pi * 0.0)) < math.pi / 6:
                ang_new = math.pi * 0.0
            elif abs(ang_to_ang(ang_new - math.pi * 0.5)) < math.pi / 6:
                ang_new = math.pi * 0.5
            elif abs(ang_to_ang(ang_new + math.pi * 0.5)) < math.pi / 6:
                ang_new = -math.pi * 0.5
            elif abs(ang_to_ang(ang_new - math.pi * 1.0)) < math.pi / 6:
                ang_new = math.pi * 1.0
            ang_dlt = ang_new - ang_tar
            tmp_x, tmp_z = tar_old[0] - pos_old[0], tar_old[2] - pos_old[2]
            add_x = tmp_z * math.sin(ang_dlt) + tmp_x * math.cos(ang_dlt)
            add_z = tmp_z * math.cos(ang_dlt) - tmp_x * math.sin(ang_dlt)
            source_2 = [pos_new[0] + 0, pos_old[1], pos_new[2] + 0]
            target_2 = [pos_new[0] + add_x, pos_old[1], pos_new[2] + add_z]
    # camera
    camera_new['pos'] = source_2
    camera_new['target'] = target_2
    camera_new['pos_1'] = source_1
    camera_new['target_1'] = target_1
    return camera_new
