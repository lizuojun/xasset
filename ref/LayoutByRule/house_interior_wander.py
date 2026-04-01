# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2021-05-20
@Description: 相机处理

"""

import math

# 房间级别
ROOM_TYPE_LEVEL_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library']
ROOM_TYPE_LEVEL_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
ROOM_TYPE_LEVEL_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom',
                     'Kitchen',
                     'Balcony', 'Terrace', 'Lounge', 'LaundryRoom',
                     'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                     'StorageRoom', 'CloakRoom', 'EquipmentRoom']
ROOM_TYPE_LEVEL_4 = ['Hallway', 'Aisle', 'Corridor', 'Stairwell']
# 部件参数
UNIT_HEIGHT_VIEW_MIN = 1.00
UNIT_HEIGHT_VIEW_MID = 1.25
UNIT_HEIGHT_VIEW_MAX = 1.50
# 漫游时长
ROOM_TIME_LEVEL_1 = 15
ROOM_TIME_LEVEL_2 = 10
ROOM_TIME_LEVEL_3 = 5


def connect_house(house_info):
    # 默认入户
    room_list, type_dict, room_first = [], {}, {}
    if 'room' in house_info:
        room_list = house_info['room']
    for room_idx, room_one in enumerate(room_list):
        room_key, room_type = '', ''
        if 'id' in room_one:
            room_key = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        if len(room_key) > 0 and len(room_type) > 0:
            type_dict[room_key] = room_type
        if room_type in ['LivingDiningRoom', 'LivingRoom']:
            room_first = room_one
    # 检测出入
    for room_idx, room_one in enumerate(room_list):
        connect_room(room_one, type_dict)
        if 'from' in room_one and len(room_one['from']) <= 0:
            if room_one['type'] in ['LivingDiningRoom', 'LivingRoom', 'Hallway', 'Aisle', 'Corridor', 'Stairwell']:
                room_first = room_one
    # 确认入户
    room_first['first'] = 1


def connect_room(room_info, type_dict):
    door_entry, link_dict = {}, {}
    # 房间信息
    room_key, room_type = '', ''
    if 'id' in room_info:
        room_key = room_info['id']
    if 'type' in room_info:
        room_type = room_info['type']
    # 房间级别
    room_major = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']
    room_minor = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
    room_other = ['Bathroom', 'MasterBathroom', 'SecondBathroom', 'Kitchen', 'Balcony', 'Terrace', 'StorageRoom', 'CloakRoom', 'EquipmentRoom']
    room_aisle = ['Hallway', 'Aisle', 'Corridor', 'Stairwell', 'Courtyard', 'Garage']
    # 连接部件
    unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow = [], [], [], []
    if 'door_info' in room_info:
        unit_list_door = room_info['door_info']
    if 'hole_info' in room_info:
        unit_list_hole = room_info['hole_info']
    if 'window_info' in room_info:
        unit_list_window = room_info['window_info']
    if 'baywindow_info' in room_info:
        unit_list_baywindow = room_info['baywindow_info']
    for unit_list_one in [unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow]:
        door_flag = False
        if unit_list_one == unit_list_door or unit_list_one == unit_list_hole:
            door_flag = True
        for unit_one in unit_list_one:
            unit_to, unit_to_type, unit_pos = '', '', []
            if 'to' in unit_one:
                unit_to = unit_one['to']
            if len(unit_to) <= 0:
                unit_to_type = ''
            elif unit_to in type_dict:
                unit_to_type = type_dict[unit_to]
                unit_one['link'] = unit_to_type
            else:
                continue
            if 'pts' in unit_one:
                unit_pts = unit_one['pts']
                if len(unit_pts) >= 8:
                    unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                                (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                elif len(unit_pts) >= 2:
                    unit_pos = [unit_pts[0], unit_pts[1]]
            if door_flag:
                link_dict[unit_to] = {'type': unit_to_type, 'position': unit_pos}
                if unit_to == '':
                    if room_type in room_minor and (unit_to_type in room_major or unit_to_type in room_aisle):
                        pass
                    else:
                        door_entry, main_entry = unit_one, True
                # 进门出门
                if room_type in room_major and unit_to_type in room_aisle:
                    if 'link' in door_entry and door_entry['link'] in ['Hallway']:
                        pass
                    else:
                        door_entry = unit_one
                elif room_type in room_major:
                    if len(door_entry) <= 0:
                        door_entry = unit_one
                    elif 'to' in door_entry and door_entry['to'] == '':
                        continue
                    elif 'link' in door_entry:
                        entry_link = door_entry['link']
                        if entry_link == '':
                            continue
                        elif entry_link in room_aisle:
                            continue
                        elif unit_to_type in room_major and entry_link not in room_major:
                            door_entry = unit_one
                elif room_type in room_minor and unit_to_type in room_major:
                    door_entry = unit_one
                elif room_type in room_minor and unit_to_type not in room_other and len(door_entry) <= 0:
                    door_entry = unit_one
                elif room_type in room_minor and unit_to_type in room_aisle and 'link' in door_entry and door_entry['link'] in room_other:
                    door_entry = unit_one
                elif room_type in room_other and unit_to_type not in room_other:
                    if unit_to_type in ['none', 'OtherRoom'] and len(door_entry) > 0:
                        pass
                    else:
                        door_entry = unit_one
                elif room_type not in room_major and len(door_entry) <= 0:
                    door_entry = unit_one
                elif room_type not in room_major and unit_to_type in room_aisle:
                    door_entry = unit_one
                elif len(door_entry) <= 0:
                    door_entry = unit_one
    # 进门出门
    door_from, door_exit = '', ''
    if 'to' in door_entry:
        door_from = door_entry['to']
        door_exit = door_entry['to']
    for unit_key, unit_val in link_dict.items():
        if unit_key == door_from:
            continue
        unit_to_type = unit_val['type']
        if unit_to_type in ROOM_TYPE_LEVEL_1 or unit_to_type in ROOM_TYPE_LEVEL_2:
            door_exit = unit_key
        elif unit_to_type in ROOM_TYPE_LEVEL_4:
            door_exit = unit_key
            break
        else:
            continue
    room_info['door_from'] = door_from
    room_info['door_exit'] = door_exit
    room_info['door_dict'] = link_dict


# 全屋漫游 TODO:
def wander_house(house_info, layout_info):
    house_wander_dict, house_wander_list = {}, []
    # 房间列表
    room_list, room_first = [], {}
    if 'room' in house_info:
        room_list = house_info['room']
    # 单屋漫游
    for room_idx, room_one in enumerate(room_list):
        room_key, room_type, room_door = '', '', []
        room_layout, room_scheme = {}, {}
        room_group, room_scene, room_route, room_wander = [], [], [], {}
        # 入户信息
        if 'first' in room_one and room_one['first'] >= 1:
            room_first = room_one
        # 房间信息
        if 'id' in room_one:
            room_key = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']

        # 布局信息
        if room_key in layout_info:
            room_layout = layout_info[room_key]
        if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
            room_scheme = room_layout['layout_scheme'][0]
        if 'group' in room_scheme:
            group_list = room_scheme['group']
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] in ['Meeting', 'Bed', 'Media', 'Dining', 'Work', 'Bath', 'Toilet']:
                    room_group.append(group_one)
                elif group_one['type'] in ['Cabinet'] and room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
                    room_group.append(group_one)
        if 'scene' in room_scheme:
            room_scene = room_scheme['scene']
        if 'route' in room_scheme and len(room_scheme['route']) > 0:
            room_route = room_scheme['route'][0]
        # 单屋机位
        single_old, sphere_old = [], []
        single_new, sphere_new = [], []
        # 单图机位
        if 'scene_single' in room_scheme:
            single_old = room_scheme['scene_single']
        elif 'scene' in room_scheme:
            single_old = room_scheme['scene']
        for scene_one in single_old:
            scene_new = {'group': scene_one['group'], 'camera': copy_camera(scene_one['camera'])}
            vision_set, hidden_set = [], []
            if 'vision' in scene_one:
                vision_set = scene_one['vision']
            if 'hidden' in scene_one:
                hidden_set = scene_one['hidden']
            scene_new['hidden'] = hidden_set
            single_new.append(scene_new)
        # 全景机位
        if 'scene_sphere' in room_scheme:
            sphere_old = room_scheme['scene_sphere']
        elif 'scene' in room_scheme:
            sphere_old = room_scheme['scene']
        for scene_one in sphere_old:
            scene_new = {'group': scene_one['group'], 'camera': copy_camera(scene_one['camera'])}
            sphere_new.append(scene_new)
            vision_set, hidden_set = [], []
            if 'vision' in scene_one:
                vision_set = scene_one['vision']
            if 'hidden' in scene_one:
                hidden_set = scene_one['hidden']
            scene_new['hidden'] = hidden_set
        # 漫游路线 单屋
        wander_list_room = wander_room(room_one, room_group, room_route)
        # 漫游路线 组合
        wander_list_group = wander_group(room_one, room_group, room_route)

        # 返回结果
        room_wander = {
            'camera_single': single_new,
            'camera_sphere': sphere_new,
            'wander_room': wander_list_room,
            'wander_group': wander_list_group
        }
        house_wander_dict[room_key] = room_wander
    # 全屋漫游
    room_used = {}
    for room_idx, room_one in enumerate(room_list):
        room_key = ''
        if 'id' in room_one:
            room_key = room_one['id']
    # 返回信息
    house_wander_info = {
        'room_wander': house_wander_dict,
        'house_wander': house_wander_list
    }
    house_info['wander_info'] = house_wander_info
    return house_wander_info


# 单屋漫游
def wander_room(room_info, room_group, route_list):
    if '3565' in room_info['id'] and False:
        print('layout wander:', room_info['id'], 'debug')
    # 房间信息
    room_type, room_area = '', 0
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    # 房门信息
    door_from, door_exit, door_dict = '', '', []
    if 'door_dict' in room_info:
        door_from = room_info['door_from']
        door_exit = room_info['door_exit']
        door_dict = room_info['door_dict']
    if len(door_dict) <= 0 or len(route_list) <= 0:
        return []
    # 组合信息
    group_main, group_side, group_face = {}, {}, {}
    for group_idx, group_one in enumerate(room_group):
        group_type = group_one['type']
        if group_type in ['Meeting', 'Bed']:
            group_main = group_one
        elif group_type in ['Dining'] and room_type in ['DiningRoom']:
            group_main = group_one
        elif group_type in ['Dining'] and room_type in ['LivingDiningRoom', 'LivingRoom']:
            group_side = group_one
        elif group_type in ['Work'] and room_type in ['Library']:
            group_main = group_one
        elif group_type in ['Cabinet'] and room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
            group_main = group_one
        elif group_type in ['Work', 'Rest', 'Bath', 'Toilet'] and len(group_main) <= 0:
            group_main = group_one
        elif group_type in ['Work', 'Rest', 'Bath', 'Toilet'] and len(group_side) <= 0:
            group_side = group_one
        elif group_type in ['Media']:
            group_face = group_one

    # 计算节点
    pos_set = []
    # 起点终点
    ent_val, ent_pos = {}, []
    ext_val, ext_pos = {}, []
    if door_from in door_dict:
        ent_val = door_dict[door_from]
        ent_pos = ent_val['position']
    if door_exit in door_dict:
        ext_val = door_dict[door_exit]
        ext_pos = ext_val['position']
    if len(ent_pos) <= 0 or len(ext_pos) <= 0:
        return []
    # 中间拐点
    mid_pos, mid_dis = [], -100
    grp_pos = []
    if len(group_main) > 0:
        grp_pos = group_main['position']
    for route_idx, route_one in enumerate(route_list):
        p1, p2 = route_one['p1'], route_one['p2']
        d1 = (abs(p1[0] - ent_pos[0]) + abs(p1[1] - ent_pos[1])) + abs(p1[0] - ext_pos[0]) + abs(p1[1] - ext_pos[1])
        d2 = (abs(p2[0] - ent_pos[0]) + abs(p2[1] - ent_pos[1])) + abs(p2[0] - ext_pos[0]) + abs(p2[1] - ext_pos[1])
        if len(grp_pos) > 0:
            d1 = d1 - (abs(p1[0] - grp_pos[2]) + abs(p1[1] - grp_pos[2]))
            d2 = d2 - (abs(p2[0] - grp_pos[2]) + abs(p2[1] - grp_pos[2]))
        if d1 > mid_dis and d1 >= d2:
            mid_pos, mid_dis = p1, d1
        elif d2 > mid_dis and d2 >= d1:
            mid_pos, mid_dis = p2, d2
    # 添加节点
    pos_set.append([ent_pos, mid_pos, ext_pos])

    # 连接节点
    path_set = []
    for pos_idx, pos_val in enumerate(pos_set):
        ent_pos, mid_pos, ext_pos = pos_val[0], pos_val[1], pos_val[2]
        # 起点出发
        path_one = []
        o1, o2 = ent_pos[:], mid_pos[:]
        dis_o1_o2 = abs(o2[0] - o1[0]) + abs(o2[1] - o1[1])
        for i in range(5):
            route_door = False
            if i <= 0:
                route_door = True
            p1, p2, min_to_o1, min_to_o2 = calc_route(o1, o2, route_list, route_door)
            if min_to_o2 <= 1.0:
                # add path
                path_one.append([p1, p2])
                # new path
                o1, o2 = p2[:], mid_pos[:]
                dis_o1_o2 = min_to_o2
                break
            elif min_to_o2 <= dis_o1_o2 - 0.1:
                # add path
                path_one.append([p1, p2])
                # new path
                o1, o2 = p2[:], mid_pos[:]
                dis_o1_o2 = min_to_o2
                continue
            else:
                break
        pass

        # 终点到达
        path_two = []
        o1, o2 = mid_pos[:], ext_pos[:]
        dis_o1_o2 = abs(o2[0] - o1[0]) + abs(o2[1] - o1[1])
        for i in range(5):
            p1, p2, min_to_o1, min_to_o2 = calc_route(o1, o2, route_list, route_door=True)
            if min_to_o2 <= 1.0:
                # add path
                path_two.append([p1, p2])
                # new path
                o1, o2 = p2[:], ext_pos[:]
                dis_o1_o2 = min_to_o2
                break
            elif min_to_o2 <= dis_o1_o2 - 0.1:
                # fix path TODO:
                pass
                # add path
                path_two.append([p1, p2])
                # new path
                o1, o2 = p2[:], ext_pos[:]
                dis_o1_o2 = min_to_o2
                continue
            else:
                break

        # 路线添加
        path_set.append(path_one)
        if room_type not in ROOM_TYPE_LEVEL_3:
            # path_set.append(path_two)
            pass

    # 整理机位
    wander_set = []
    for path_idx, path_one in enumerate(path_set):
        wander_one = []
        wander_ent = False
        if len(path_one) <= 1 and room_type in ROOM_TYPE_LEVEL_3:
            wander_ent = True
        elif len(group_main) <= 0 and room_type in ROOM_TYPE_LEVEL_2:
            wander_ent = True
        for line_idx, line_one in enumerate(path_one):
            p1_old, p2_old = line_one[0][:], line_one[1][:]
            dis, ang = calc_vector(p1_old[0], p1_old[1], p2_old[0], p2_old[1])
            # p1 p2
            p1, p2, p3, p4, p5 = p1_old, p2_old, p2_old[:], p2_old[:], p2_old[:]
            if wander_ent:
                mov_p1, mov_p2 = 0.2, 0.5
                # p1
                ratio = min(mov_p1 / dis, 0.1)
                x1 = p1[0] * (1 - ratio) + p2[0] * ratio
                z1 = p1[1] * (1 - ratio) + p2[1] * ratio
                p1 = [x1, z1]
                # p2
                ratio = min(mov_p2 / dis, 0.9)
                x2 = p1[0] * (1 - ratio) + p2[0] * ratio
                z2 = p1[1] * (1 - ratio) + p2[1] * ratio
                p2 = [x2, z2]
            else:
                mov_p1, mov_p2 = 0.2, 0.5
                if dis < 0.5:
                    mov_p2 = 0
                elif dis < 2.0:
                    mov_p2 = dis / 2
                # p1
                ratio = min(mov_p1 / dis, 0.1)
                x1 = p1[0] * (1 - ratio) + p2[0] * ratio
                z1 = p1[1] * (1 - ratio) + p2[1] * ratio
                p1 = [x1, z1]
                # p2
                ratio = min(1 - mov_p2 / dis, 0.9)
                x2 = p1[0] * (1 - ratio) + p2[0] * ratio
                z2 = p1[1] * (1 - ratio) + p2[1] * ratio
                p2 = [x2, z2]
            # p3 p4 p5
            pm = [p1_old[0] * 0.5 + p2_old[0] * 0.5, p1_old[1] * 0.5 + p2_old[1] * 0.5]
            p3 = pm[:]
            dis_main, ang_main, size_main = dis, ang, 2.0
            dis_side, ang_side, size_side = dis, ang, 1.0
            if len(group_main) > 0:
                p3 = [group_main['position'][0], group_main['position'][2]]
                pos_main = group_main['position']
                dis_main, ang_main = calc_vector(pm[0], pm[1], pos_main[0], pos_main[2])
                size_main = max(group_main['size'][0], group_main['size'][2]) / 2
                if dis_main > size_main + 2:
                    p3 = p2_old[:]
            else:
                ang1 = ang - math.pi / 4
                ang2 = ang + math.pi / 4
                p3 = [p2[0] + 0.2 * math.sin(ang1), p2[1] + 0.2 * math.cos(ang1)]
                p4 = [p2[0] + 0.2 * math.sin(ang2), p2[1] + 0.2 * math.cos(ang2)]
                pass
            if len(group_side) > 0:
                p4 = [group_side['position'][0], group_side['position'][2]]
                p5 = p4[:]
                pos_side = group_side['position']
                dis_side, ang_side = calc_vector(pm[0], pm[1], pos_side[0], pos_side[2])
                size_side = max(group_side['size'][0], group_side['size'][2]) / 2
                if dis_side < dis_main and dis_side < size_side + 1:
                    p3 = p4[:]
            if len(group_face) > 0:
                p5 = [group_face['position'][0], group_face['position'][2]]
            # 机位
            if wander_ent:
                camera_1 = {
                    'aspect': 1.0, 'pitch': 0, 'fov': 60, 'near': 0.060000000000000005, 'far': 1000, 'up': [0, 1, 0],
                    'pos': [p1[0], UNIT_HEIGHT_VIEW_MID, p1[1]], 'target': [p2_old[0], UNIT_HEIGHT_VIEW_MID, p2_old[1]]
                }
                camera_2 = {
                    'aspect': 1.0, 'pitch': 0, 'fov': 60, 'near': 0.060000000000000005, 'far': 1000, 'up': [0, 1, 0],
                    'pos': [p2[0], UNIT_HEIGHT_VIEW_MID, p2[1]], 'target': [p2_old[0], UNIT_HEIGHT_VIEW_MID, p2_old[1]]
                }
                camera_3 = {
                    'aspect': 1.0, 'pitch': 0, 'fov': 60, 'near': 0.060000000000000005, 'far': 1000, 'up': [0, 1, 0],
                    'pos': [p2[0], UNIT_HEIGHT_VIEW_MID, p2[1]], 'target': [p3[0], UNIT_HEIGHT_VIEW_MID, p3[1]]
                }
                camera_4 = {
                    'aspect': 1.0, 'pitch': 0, 'fov': 60, 'near': 0.060000000000000005, 'far': 1000, 'up': [0, 1, 0],
                    'pos': [p2[0], UNIT_HEIGHT_VIEW_MID, p2[1]], 'target': [p4[0], UNIT_HEIGHT_VIEW_MID, p4[1]]
                }
                wander_one.append(camera_1)
                wander_one.append(camera_2)
                wander_one.append(camera_3)
                wander_one.append(camera_4)
            else:
                camera_1 = {
                    'aspect': 1.0, 'pitch': 0, 'fov': 60, 'near': 0.060000000000000005, 'far': 1000, 'up': [0, 1, 0],
                    'pos': [p1[0], UNIT_HEIGHT_VIEW_MID, p1[1]], 'target': [p3[0], UNIT_HEIGHT_VIEW_MID, p3[1]]
                }
                camera_2 = {
                    'aspect': 1.0, 'pitch': 0, 'fov': 60, 'near': 0.060000000000000005, 'far': 1000, 'up': [0, 1, 0],
                    'pos': [p2[0], UNIT_HEIGHT_VIEW_MID, p2[1]], 'target': [p3[0], UNIT_HEIGHT_VIEW_MID, p3[1]]
                }
                wander_one.append(camera_1)
                wander_one.append(camera_2)
            # 附加
            if path_idx == 0 and line_idx == len(path_one) - 1:
                if len(group_main) > 0 and group_main['type'] in ['Meeting']:
                    camera_3 = {
                        'aspect': 1.0, 'pitch': 0, 'fov': 60, 'near': 0.060000000000000005, 'far': 1000, 'up': [0, 1, 0],
                        'pos': [p3[0], UNIT_HEIGHT_VIEW_MID, p3[1]], 'target': [p5[0], UNIT_HEIGHT_VIEW_MID, p5[1]]
                    }
                    wander_one.append(camera_3)
        wander_set.append(wander_one)

    # 返回
    return wander_set


# 组合漫游 TODO:
def wander_group(room_info, room_group, route_list):
    if len(room_group) <= 0 or len(route_list) <= 0:
        return []
    return []


# 计算路线
def calc_route(o1, o2, route_list, route_door=False):
    o1_o2 = abs(o2[0] - o1[0]) + abs(o2[1] - o1[1])
    min_p1, min_p2, min_to_o1, min_to_o2 = [], [], 100, 100
    for route_idx, route_one in enumerate(route_list):
        route_type, route_width = route_one['type'], route_one['width']
        route_pre, route_post = route_one['score_pre'], route_one['score_post']
        if route_type == 2 or route_pre == route_post == 4:
            if route_width <= 2 and not route_door:
                continue
        p1, p2 = route_one['p1'][:], route_one['p2'][:]
        # 起点
        p1_o1 = abs(p1[0] - o1[0]) + abs(p1[1] - o1[1])
        p2_o1 = abs(p2[0] - o1[0]) + abs(p2[1] - o1[1])
        p1_o2 = abs(p1[0] - o2[0]) + abs(p1[1] - o2[1])
        p2_o2 = abs(p2[0] - o2[0]) + abs(p2[1] - o2[1])
        # 起点
        split_flag = False
        dis_old, ang_old = calc_vector(p1[0], p1[1], p2[0], p2[1])
        dis_new, ang_new = calc_vector(p1[0], p1[1], o1[0], o1[1])
        tmp_x, tmp_z = dis_new * math.cos(ang_new - ang_old), dis_new * math.sin(ang_new - ang_old)
        if min(p1_o2, p2_o2) < 1.0 and abs(tmp_z) < 1.0:
            split_flag = True
        # p1 - p2
        if (p1_o1 < p2_o1 or split_flag) and p2_o2 < p1_o2 and p2_o2 < o1_o2:
            if p1_o1 < min_to_o1 or p2_o2 < 1.0:
                min_p1, min_p2 = p1, p2
                min_to_o1, min_to_o2 = p1_o1, p2_o2
                if min_to_o1 < 0.5:
                    break
                if min_to_o1 < 1.0 and min(p1_o2, p2_o2) < o1_o2 - 1:
                    break
                if min_to_o1 < 1.5 and min(p1_o2, p2_o2) < o1_o2 - 1.5:
                    break
                if min_to_o1 < 2.0 and min(p1_o2, p2_o2) < o1_o2 - 2.0:
                    break
            continue
        # p2 - p1
        elif (p2_o1 < p1_o1 or split_flag) and p1_o2 < p2_o2 and p1_o2 < o1_o2:
            if p2_o1 < min_to_o1 or p1_o2 < 1.0:
                min_p1, min_p2 = p2, p1
                min_to_o1, min_to_o2 = p2_o1, p1_o2
                if min_to_o1 < 0.5:
                    break
                if min_to_o1 < 1.0 and min(p1_o2, p2_o2) < o1_o2 - 1:
                    break
                if min_to_o1 < 1.5 and min(p1_o2, p2_o2) < o1_o2 - 1.5:
                    break
                if min_to_o1 < 2.0 and min(p1_o2, p2_o2) < o1_o2 - 2.0:
                    break
            continue
        # other
        else:
            continue
    if len(min_p1) >= 2 and len(min_p2) >= 2:
        if min_to_o1 > 1:
            dis_old, ang_old = calc_vector(min_p1[0], min_p1[1], min_p2[0], min_p2[1])
            dis_new, ang_new = calc_vector(min_p1[0], min_p1[1], o1[0], o1[1])
            tmp_x, tmp_z = dis_new * math.cos(ang_new - ang_old), dis_new * math.sin(ang_new - ang_old)
            if dis_old * 0.01 < tmp_x < dis_old * 0.99 and dis_old > 1:
                ratio = (tmp_x + 0.2) / dis_old
                x3 = min_p1[0] * (1 - ratio) + min_p2[0] * ratio
                z3 = min_p1[1] * (1 - ratio) + min_p2[1] * ratio
                min_p1 = [x3, z3]
                min_to_o1 = abs(min_p1[0] - o1[0]) + abs(min_p1[1] - o1[1])
        if min_to_o2 > 1:
            dis_old, ang_old = calc_vector(min_p1[0], min_p1[1], min_p2[0], min_p2[1])
            dis_new, ang_new = calc_vector(min_p1[0], min_p1[1], o2[0], o2[1])
            tmp_x, tmp_z = dis_new * math.cos(ang_new - ang_old), dis_new * math.sin(ang_new - ang_old)
            if dis_old * 0.01 < tmp_x < dis_old * 0.99 and dis_old > 1:
                ratio = (tmp_x + 0.2) / dis_old
                x3 = min_p1[0] * (1 - ratio) + min_p2[0] * ratio
                z3 = min_p1[1] * (1 - ratio) + min_p2[1] * ratio
                min_p2 = [x3, z3]
                min_to_o2 = abs(min_p2[0] - o2[0]) + abs(min_p2[1] - o2[1])
    return min_p1, min_p2, min_to_o1, min_to_o2


# 计算机位
def calc_camera():
    pass


# 计算矢量
def calc_vector(x1, y1, x2, y2):
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


# 复制机位
def copy_camera(camera_one):
    # 机位
    camera_new = camera_one.copy()
    if 'up' in camera_one:
        camera_new['up'] = camera_one['up'][:]
    if 'pos' in camera_one:
        camera_new['pos'] = camera_one['pos'][:]
    if 'target' in camera_one:
        camera_new['target'] = camera_one['target'][:]
    return camera_new


# 功能测试
if __name__ == '__main__':
    # 参数
    pass
