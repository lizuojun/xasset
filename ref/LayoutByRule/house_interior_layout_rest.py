# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-10-24
@Description: 次要家具布局

"""

from Furniture.furniture_group import *
from LayoutByRule.house_calculator import *

# 房间类型
ROOM_TYPE_FOR_REST_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library']
ROOM_TYPE_FOR_REST_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
ROOM_TYPE_FOR_REST_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom',
                        'Balcony', 'Terrace', 'Lounge', 'Auditorium',
                        'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                        'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom']
ROOM_TYPE_FOR_REST_4 = ['Hallway', 'Aisle', 'Corridor', 'Stairwell',
                        'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom']
# 房间类型
ROOM_TYPE_FOR_BATH_1 = ['MasterBathroom', 'SecondBathroom', 'Bathroom']


# 次要功能区域布局
def room_rect_layout_rest(rect_list, line_list, rect_used, group_todo, group_done,
                          room_type='', room_area=10, room_link=[],
                          door_pt_entry=[], door_pt_cook=[], door_pt_bath=[]):
    # 返回信息
    group_result = []
    if len(group_todo) <= 0:
        return group_result
    # 复制参数
    repeat_todo, repeat_used = {}, {}

    # 组合依赖
    group_door, group_cook, group_bath, group_work, group_wait = [], [], [], [], []
    rect_door, rect_cook, rect_bath, rect_work, rect_wear = [], [], [], [], []
    for group_one in group_todo:
        group_type, group_size = group_one['type'], group_one['size']
        group_zone, group_seed = '', ''
        if 'zone' in group_one:
            group_zone = group_one['zone']
        if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
            group_seed = group_one['seed_list'][0]
            group_zone = ''
        if group_type in ['Cabinet'] and len(group_zone) <= 0:
            seed_id = ''
            if 'obj_main' in group_one:
                seed_id = group_one['obj_main']
            if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                seed_id = group_one['seed_list'][0]
            type_id, style_id, category_id = get_furniture_data_refer_id(seed_id)
            obj_cate, obj_zone = get_furniture_room_by_category(category_id)
            fix_cate_zone = get_furniture_zone_by_jid(seed_id)
            if len(fix_cate_zone) >= 2:
                obj_cate, obj_zone = fix_cate_zone[0], fix_cate_zone[1]
            if obj_zone in ['DiningRoom', 'Hallway', 'Bathroom']:
                group_one['zone'] = obj_zone
                group_zone = obj_zone
            else:
                group_wait.append(group_one)
        if group_zone in ['Hallway']:
            group_door.append(group_one)
        elif group_zone in ['Library']:
            group_work.append(group_one)
        elif group_zone in ['DiningRoom']:
            group_cook.append(group_one)
        elif group_zone in ['Bathroom']:
            group_bath.append(group_one)
    # 矩形依赖
    rect_pt_head, rect_pt_food, rect_size_food, rect_size_bed = [], [], [], []
    for group_idx, group_one in enumerate(group_done):
        group_type, group_size = group_one['type'], group_one['size']
        if group_type in ['Bed']:
            group_pos, group_ang = group_one['position'], rot_to_ang(group_one['rotation'])
            tmp_x, tmp_z = 0, 0 - group_size[2] * 0.5
            add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
            add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
            rect_pt_head = [group_pos[0] + add_x, group_pos[2] + add_z]
            if 'size' in group_one:
                rect_size_bed = group_one['size']
            if 'seed_size_new' in group_one:
                rect_size_bed = group_one['seed_size_new']
        elif group_type in ['Dining']:
            group_pos, group_ang = group_one['position'], rot_to_ang(group_one['rotation'])
            rect_pt_food, rect_size_food = [group_pos[0], group_pos[2]], group_size[:]
    for rect_idx, rect_one in enumerate(rect_list):
        if len(door_pt_entry) < 2 and len(door_pt_bath) < 2 and len(rect_pt_food) < 2:
            break
        if rect_idx in rect_used:
            continue
        # 矩形信息
        rect_type, rect_width, rect_depth = rect_one['type'], rect_one['width'], rect_one['depth']
        # 初步判断
        if room_type in ['CloakRoom']:
            if rect_width > 0.5:
                rect_wear.append(rect_one)
            continue
        elif room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
            rect_bath.append(rect_one)
            rect_one['dis_bath'] = 0
            continue
        if rect_type not in [UNIT_TYPE_SIDE, UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]:
            continue
        if rect_width < 0.4:
            continue
        line_idx = rect_one['index']
        line_one = line_list[line_idx]
        dis_door, dis_cook, dis_bath = 10, 10, 10
        dir_door, dir_cook, dir_bath = 0, 0, 0
        # 玄关门
        link_hallway = False
        if room_type in ROOM_TYPE_LEVEL_1 and '' not in room_link:
            link_hallway = True
        if len(door_pt_entry) >= 2 and not link_hallway:
            dis1, dis2, dis3 = compute_line_distance(line_one, [0, 1], door_pt_entry, depth=0, mode=2)
            dis4, dis5, dis6 = compute_line_distance(line_one, [0, 1], door_pt_entry, depth=rect_depth, mode=2)
            dis7, dis8, dis9 = compute_line_distance(line_one, [0, 1], door_pt_entry, depth=1.5, mode=2)
            dis_door = min(dis1, dis2, dis3, dis4, dis5, dis6, dis7, dis8, dis9)
            if UNIT_WIDTH_HOLE < dis1 <= dis_door + 0.1 and rect_one['score_pre'] == 1:
                dis_door = min(dis2, dis3, dis5, dis6)
            elif UNIT_WIDTH_HOLE < dis2 <= dis_door + 0.1 and rect_one['score_post'] == 1:
                dis_door = min(dis1, dis3, dis4, dis6)
            if dis1 < min(dis2, dis3) - 0.1:
                dir_door = 1
            elif dis2 < min(dis1, dis3) - 0.1:
                dir_door = -1
        # 厨房门
        if len(door_pt_cook) >= 2:
            dis1, dis2, dis3 = compute_line_distance(line_one, [0, 1], door_pt_cook, depth=rect_depth / 2, mode=2)
            dis_cook = min(dis1, dis2, dis3)
            if dis1 < min(dis2, dis3) - 0.1:
                dir_cook = 1
            elif dis2 < min(dis1, dis3) - 0.1:
                dir_cook = -1
        if len(rect_pt_food) >= 2 and len(rect_size_food) >= 3:
            move_depth_1, move_depth_2 = rect_size_food[0] / 2, rect_size_food[2] / 2
            dis1, dis2, dis3 = compute_line_distance(line_one, [0, 1], rect_pt_food, depth=move_depth_1, mode=2)
            dis4, dis5, dis6 = compute_line_distance(line_one, [0, 1], rect_pt_food, depth=move_depth_2, mode=2)
            dis_food = min(dis1, dis2, dis3, dis4, dis5, dis6)
            if dis_cook > dis_food > dis_door or min(dis_cook, dis_door) > 2 > dis_food:
                dis_cook = dis_food
                dir_cook = 0
            elif dis_food > dis_cook + 1:
                dis_cook = dis_food
                dir_cook = 0
            elif dis_food < 0.5 < 1.0 < dis_door:
                dis_cook = dis_food
                dir_cook = 0
        # 浴室门
        if len(door_pt_bath) >= 2:
            dis1, dis2, dis3 = compute_line_distance(line_one, [0, 1], door_pt_bath, depth=0, mode=2)
            dis4, dis5, dis6 = compute_line_distance(line_one, [0, 1], door_pt_bath, depth=min(rect_depth, 1), mode=2)
            dis_bath = min(dis1, dis2, dis3, dis4, dis5, dis6)
            if dis1 < min(dis2, dis3) - 0.1:
                dir_bath = 1
            elif dis2 < min(dis1, dis3) - 0.1:
                dir_bath = -1

        # 玄关门
        if dis_door < 1 and room_type in ['LivingRoom', 'DiningRoom', 'LivingDiningRoom', 'Hallway']:
            if rect_type in [UNIT_TYPE_WINDOW]:
                pass
            elif dir_door == 1 and line_one['score_pre'] < 4 and line_one['width'] > 2:
                if line_one['score_pre'] == 1:
                    if abs(line_one['width'] - rect_width) < 0.1:
                        rect_door.append(rect_one)
                    elif rect_one['type_pre'] in [UNIT_TYPE_SIDE]:
                        rect_door.append(rect_one)
            elif dir_door == -1 and line_one['score_post'] < 4 and line_one['width'] > 2:
                if line_one['score_post'] == 1:
                    if abs(line_one['width'] - rect_width) < 0.1:
                        rect_door.append(rect_one)
                    elif rect_one['type_post'] in [UNIT_TYPE_SIDE]:
                        rect_door.append(rect_one)
            else:
                rect_door.append(rect_one)
        elif dis_door < 1 and room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom']:
            if dir_door == 1 and line_one['score_pre'] < 4 and line_one['width'] > 2:
                pass
            elif dir_door == -1 and line_one['score_post'] < 4 and line_one['width'] > 2:
                pass
            else:
                rect_door.append(rect_one)
        elif dis_door < min(3, dis_cook, dis_bath) and room_type in ['LivingRoom', 'LivingDiningRoom', 'Hallway']:
            if dir_door == 1 and line_one['score_pre'] < 4 and line_one['width'] > 2:
                pass
            elif dir_door == -1 and line_one['score_post'] < 4 and line_one['width'] > 2:
                pass
            else:
                rect_door.append(rect_one)
        # 厨房门
        if dis_cook < 1:
            if dir_cook == 1 and line_one['score_pre'] < 4 and line_one['width'] > 2:
                pass
            elif dir_cook == -1 and line_one['score_post'] < 4 and line_one['width'] > 2:
                pass
            elif rect_width <= 1 and room_area >= MID_ROOM_AREA_LIVING:
                pass
            else:
                rect_cook.append(rect_one)
        elif dis_cook < min(2, dis_door, dis_bath) or (dis_cook < 2 < rect_width and rect_one not in rect_door):
            if dir_cook == 1 and line_one['score_pre'] < 4 and line_one['width'] > 2:
                pass
            elif dir_cook == -1 and line_one['score_post'] < 4 and line_one['width'] > 2:
                pass
            else:
                rect_cook.append(rect_one)
        elif dis_cook < min(2, dis_bath) and len(group_door) <= 0:
            rect_cook.append(rect_one)
        # 浴室门
        if dis_bath < 1 and rect_one['score'] >= 5:
            if dir_bath == 1 and line_one['score_pre'] < 4 and line_one['width'] > 2:
                pass
            elif dir_bath == -1 and line_one['score_post'] < 4 and line_one['width'] > 2:
                pass
            elif dis_door <= 3 and room_type in ROOM_TYPE_LEVEL_1:
                pass
            elif dis_cook <= 3 and room_type in ROOM_TYPE_LEVEL_1:
                pass
            else:
                rect_bath.append(rect_one)
        elif dis_bath < 2 and rect_one['score'] >= 5 and room_type in ROOM_TYPE_FOR_REST_2:
            if dir_bath == 1 and line_one['score_pre'] < 4 and line_one['width'] > 2:
                pass
            elif dir_bath == -1 and line_one['score_post'] < 4 and line_one['width'] > 2:
                pass
            elif dis_door <= 3 and room_type in ROOM_TYPE_LEVEL_1:
                pass
            elif dis_cook <= 3 and room_type in ROOM_TYPE_LEVEL_1:
                pass
            else:
                rect_bath.append(rect_one)
        elif dis_bath < min(2, dis_door, dis_cook) and rect_one['score'] >= 5:
            if dir_bath == 1 and line_one['score_pre'] < 4 and line_one['width'] > 2:
                pass
            elif dir_bath == -1 and line_one['score_post'] < 4 and line_one['width'] > 2:
                pass
            elif dis_door <= 3 and room_type in ROOM_TYPE_LEVEL_1:
                pass
            elif dis_cook <= 3 and room_type in ROOM_TYPE_LEVEL_1:
                pass
            else:
                rect_bath.append(rect_one)
        # 更新
        rect_one['dis_door'], rect_one['dis_cook'], rect_one['dis_bath'] = dis_door, dis_cook, dis_bath
    # 清除依赖
    if len(rect_door) >= 2:
        well_door = False
        for rect_idx in range(len(rect_door) - 1, -1, -1):
            rect_one = rect_door[rect_idx]
            if 1 < rect_one['width'] < 3 and rect_one['dis_door'] < 1.5:
                well_door = True
                break
        if well_door:
            for rect_idx in range(len(rect_door) - 1, -1, -1):
                rect_one = rect_door[rect_idx]
                if rect_one['width'] < 1 or rect_one['width'] > 3 or rect_one['dis_door'] > 1.5:
                    rect_door.pop(rect_idx)
                    if rect_one['width'] > 1 and rect_one['dis_cook'] < 2.0:
                        rect_cook.append(rect_one)
    if len(rect_bath) >= 2:
        well_door = False
        for rect_idx in range(len(rect_bath) - 1, -1, -1):
            rect_one = rect_bath[rect_idx]
            if 1 < rect_one['width'] < 3 and ('dis_bath' in rect_one and rect_one['dis_bath'] < 1.5):
                well_door = True
                break
        if well_door:
            for rect_idx in range(len(rect_bath) - 1, -1, -1):
                rect_one = rect_bath[rect_idx]
                if rect_one['width'] < 1 or rect_one['width'] > 3 or ('dis_bath' in rect_one and rect_one['dis_bath'] > 1.5):
                    rect_bath.pop(rect_idx)
    # 补充依赖 TODO:
    if len(rect_bath) >= 1 and len(group_bath) <= 0 and 'Bedroom' in room_type:
        group_new = get_default_group_layout('cabinet bath')
        group_todo.append(group_new)
        group_bath.append(group_new)

    # 分类处理
    group_seed, group_food, group_work = [], [], []
    group_armoire, group_cabinet, group_appliance = [], [], []
    for group_idx, group_one in enumerate(group_todo):
        group_type = group_one['type']
        group_type_new = group_one['type']
        group_width, group_height, group_depth = group_one['size'][0], group_one['size'][1], group_one['size'][2]
        # 造型检查
        group_custom_mesh = False
        if 'obj_main' in group_one and group_one['obj_main'].endswith('.json'):
            group_custom_mesh = True
        object_type = group_one['obj_type']
        if len(door_pt_cook) > 0 and group_one in group_cook and group_custom_mesh:
            continue
        # 类型检查
        if group_type in ['Cabinet'] and group_height > UNIT_HEIGHT_ARMOIRE_MIN and room_type in ROOM_TYPE_FOR_REST_2:
            if group_height > UNIT_HEIGHT_ARMOIRE_MID and group_depth > UNIT_DEPTH_ARMOIRE_MIN:
                group_type_new = 'Armoire'
            elif group_height > UNIT_HEIGHT_ARMOIRE_MIN and group_depth > UNIT_DEPTH_ARMOIRE_MID:
                group_type_new = 'Armoire'
            elif group_width < 0.5 and group_depth < 0.5 and room_type in ['KidsRoom']:
                group_type_new = 'Rest'
        elif group_type in ['Cabinet'] and object_type in ['storage unit/dresser'] and room_type in ROOM_TYPE_FOR_REST_2:
            if group_width > 0.75 and group_height > 0.75:
                group_type_new = 'Armoire'
        elif group_type in ['Cabinet'] and group_height > UNIT_HEIGHT_ARMOIRE_MIN and room_type in ['CloakRoom']:
            if group_height > UNIT_HEIGHT_ARMOIRE_MID and group_depth > UNIT_DEPTH_ARMOIRE_MIN:
                group_type_new = 'Armoire'
            elif group_height > UNIT_HEIGHT_ARMOIRE_MIN and group_depth > UNIT_DEPTH_ARMOIRE_MID:
                group_type_new = 'Armoire'
        elif group_type in ['Armoire'] and group_height < UNIT_HEIGHT_ARMOIRE_MIN and room_type in ROOM_TYPE_FOR_REST_2:
            group_type_new = 'Cabinet'
        elif group_type in ['Rest'] and group_height > UNIT_HEIGHT_TABLE_MAX and room_type in ROOM_TYPE_FOR_REST_2:
            group_type_new = 'Rest'
        # 种子区域
        if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
            # 尺寸排序
            find_idx = -1
            for group_idx, group_old in enumerate(group_seed):
                if group_one['size'][0] + group_one['size'][1] > group_old['size'][0] + group_old['size'][1]:
                    find_idx = group_idx
                    break
            if find_idx >= 0:
                group_seed.insert(find_idx, group_one)
            else:
                group_seed.append(group_one)
        # 桌椅区域
        elif group_type_new in ['Dining']:
            # 尺寸排序
            find_idx = -1
            for group_idx, group_old in enumerate(group_food):
                size_one, size_old = group_one['size'], group_old['size']
                if size_one[0] + size_one[1] > size_old[0] + size_old[1]:
                    find_idx = group_idx
                    break
            if find_idx >= 0:
                group_food.insert(find_idx, group_one)
            else:
                group_food.append(group_one)
        elif group_type in ['Work', 'Rest']:
            # 尺寸排序
            find_idx = -1
            for group_idx, group_old in enumerate(group_work):
                size_one, size_old = group_one['size'], group_old['size']
                if size_one[0] + size_one[1] > size_old[0] + size_old[1]:
                    find_idx = group_idx
                    break
            if find_idx >= 0:
                group_work.insert(find_idx, group_one)
            else:
                group_work.append(group_one)
        # 通用衣柜
        elif group_type_new in ['Armoire']:
            # 尺寸排序
            find_idx = -1
            for group_idx, group_old in enumerate(group_armoire):
                # 优先重复
                delta_size = [abs(group_one['size'][i] - group_old['size'][i]) for i in range(3)]
                same_size = False
                if max(delta_size[0], delta_size[1], delta_size[2]) < 0.05:
                    same_size = True
                elif max(delta_size[1], delta_size[2]) < 0.05 and group_one['obj_main'] == group_old['obj_main']:
                    same_size = True
                if same_size:
                    find_idx = 0
                    repeat_key = group_type + '_' + str(round(group_height, 1)) + '_' + str(round(group_depth, 1))
                    if repeat_key not in repeat_todo:
                        if group_one['size'][0] > group_old['size'][0]:
                            repeat_todo[repeat_key] = [group_one, group_old]
                        else:
                            repeat_todo[repeat_key] = [group_old, group_one]
                    else:
                        repeat_todo[repeat_key].append(group_one)
                    break
                # 优先尺寸
                size_one, size_old = group_one['size'], group_old['size']
                if size_one[0] + size_one[1] + size_one[2] > size_old[0] + size_old[1] + size_old[2]:
                    find_idx = group_idx
                    break
            if find_idx <= -1 or group_type in ['Cabinet']:
                group_armoire.append(group_one)
            else:
                group_armoire.insert(find_idx, group_one)
        # 通用柜体
        elif group_type_new in ['Cabinet']:
            # 尺寸排序
            find_idx = -1
            # 优先依赖
            rely_one = 0
            if len(rect_door) > 0 and group_one in group_door:
                rely_one += 3
            elif len(rect_cook) > 0 and group_one in group_cook:
                rely_one += 2
            elif len(rect_bath) > 0 and group_one in group_bath:
                rely_one += 1
            elif len(rect_work) >= 0 and group_one in group_work:
                rely_one -= 1
            for group_idx, group_old in enumerate(group_cabinet):
                # 优先重复
                delta_size = [abs(group_one['size'][i] - group_old['size'][i]) for i in range(3)]
                same_size = False
                if max(delta_size[0], delta_size[1], delta_size[2]) < 0.05:
                    same_size = True
                elif max(delta_size[1], delta_size[2]) < 0.05 and group_one['obj_main'] == group_old['obj_main']:
                    same_size = True
                if same_size and (room_type in ROOM_TYPE_FOR_REST_2 or rely_one >= 2):
                    find_idx = 0
                    # 优先重复
                    repeat_key = group_type + '_' + str(round(group_height, 1)) + '_' + str(round(group_depth, 1))
                    if repeat_key not in repeat_todo:
                        if group_one['size'][0] > group_old['size'][0]:
                            repeat_todo[repeat_key] = [group_one, group_old]
                        else:
                            repeat_todo[repeat_key] = [group_old, group_one]
                    else:
                        repeat_todo[repeat_key].append(group_one)
                    break
                # 优先依赖
                rely_old = 0
                if len(rect_door) > 0 and group_old in group_door:
                    rely_old += 3
                elif len(rect_bath) > 0 and group_old in group_bath:
                    rely_old += 1
                elif len(rect_cook) > 0 and group_old in group_cook:
                    rely_old += 1
                elif len(rect_work) >= 0 and group_old in group_work:
                    rely_old -= 1
                if same_size:
                    pass
                elif rely_one > rely_old:
                    find_idx = group_idx
                    break
                elif rely_one < rely_old:
                    continue
                # 优先尺寸
                size_one, size_old = group_one['size'], group_old['size']
                code_one, code_old = group_one['code'], group_old['code']
                if size_one[0] + code_one / 5 > size_old[0] + code_old / 5:
                    find_idx = group_idx
                    break
            if find_idx >= 0:
                group_cabinet.insert(find_idx, group_one)
            else:
                group_cabinet.append(group_one)
        # 通用电器
        elif group_type in ['Appliance']:
            group_appliance.append(group_one)
    if len(group_armoire) >= 2:
        width_max = group_armoire[0]['size'][0]
        for group_idx in range(len(group_armoire) - 1, -1, -1):
            group_cur = group_armoire[group_idx]
            type_cur, width_cur = group_cur['type'], group_cur['size'][0]
            if type_cur in ['Cabinet'] and width_cur < width_max - 0.1:
                group_armoire.pop(group_idx)
                group_cabinet.append(group_cur)
    # 调整顺序
    group_sort = []
    if room_type in ROOM_TYPE_FOR_REST_1:
        for group_one in group_seed:
            group_sort.append(group_one)
        for group_one in group_food:
            group_sort.append(group_one)
        for group_one in group_cabinet:
            group_sort.append(group_one)
        for group_one in group_armoire:
            group_sort.append(group_one)
        for group_one in group_work:
            group_sort.append(group_one)
        for group_one in group_appliance:
            group_sort.append(group_one)
        for group_one in group_seed:
            group_sort.insert(0, group_one)
    elif room_type in ROOM_TYPE_FOR_REST_3:
        for group_one in group_seed:
            group_sort.append(group_one)
        for group_one in group_armoire:
            group_sort.append(group_one)
        for group_one in group_cabinet:
            group_sort.append(group_one)
        for group_one in group_appliance:
            group_sort.append(group_one)
    else:
        for group_one in group_armoire:
            if len(group_sort) == 1 and group_sort[0]['type'] in ['Work', 'Rest']:
                group_sort.insert(0, group_one)
            else:
                group_sort.append(group_one)
        for group_one in group_work:
            if 'CloakRoom' in room_link:
                group_sort.insert(0, group_one)
            else:
                group_sort.append(group_one)
        for group_one in group_cabinet:
            group_sort.append(group_one)
        for group_one in group_appliance:
            group_sort.append(group_one)
        for group_one in group_seed:
            group_sort.insert(0, group_one)

    # 悬空布局 TODO:
    back_point, back_width, back_depth, back_angle = [], 0, 0, 0
    back_type, back_todo = '', []
    for group_old in group_done:
        if group_old['type'] in ['Meeting', 'Bed', 'Media'] and 'center' in group_old and group_old['center'] >= 1:
            if 'regulation' in group_old and group_old['regulation'][0] > MIN_GROUP_PASS:
                back_point = compute_furniture_back(group_old['size'], group_old['position'], group_old['rotation'],
                                                    group_old['regulation'][0])
                back_width = abs(back_point[0] - back_point[2]) + abs(back_point[1] - back_point[3])
                back_depth = abs(back_point[2] - back_point[4]) + abs(back_point[3] - back_point[5])
                back_angle = ang_to_ang(rot_to_ang(group_old['rotation']) + math.pi)
                back_type = group_old['type']

    # 家具布局
    index_todo, index_have, index_side = [], 0, []
    for group_idx, group_one in enumerate(group_sort):
        group_type, group_zone = group_one['type'], ''
        group_width, group_height, group_depth = group_one['size'][0], group_one['size'][1], group_one['size'][2]
        group_width_min, group_depth_min = group_width, group_depth
        group_main_type, group_fake_flag = '', 0
        if 'zone' in group_one:
            group_zone = group_one['zone']
        if 'size_min' in group_one:
            group_width_min = group_one['size_min'][0]
            group_depth_min = group_one['size_min'][2]
        if 'obj_type' in group_one:
            group_main_type = group_one['obj_type']
        if 'adjust' in group_one:
            group_fake_flag = group_one['adjust']
        # 悬空放置
        group_relate_role = ''
        if 'relate_role' in group_one:
            group_relate_role = group_one['relate_role']
        if back_type in ['Meeting'] and group_relate_role in ['sofa']:
            if 0.5 < group_width < back_width and group_depth < back_depth:
                back_todo.append(group_one)
                continue

        # 复制数目
        repeat_cnt = 1
        if 'Bath' in room_type or 'Kid' in room_type:
            repeat_cnt = 1
        elif group_type in ['Armoire']:
            if group_width > UNIT_WIDTH_ARMOIRE_MIN * 0.8 and group_height > UNIT_HEIGHT_ARMOIRE_MIN:
                repeat_cnt = 3
        elif group_type in ['Cabinet']:
            repeat_cnt = 1
            if group_zone in ['Library', 'CloakRoom'] and group_height > UNIT_HEIGHT_ARMOIRE_MIN:
                if group_width > 0.6:
                    repeat_cnt = 2
        # 复制检查
        repeat_key = group_type + '_' + str(round(group_height, 1)) + '_' + str(round(group_depth, 1))
        if repeat_key in repeat_todo:
            repeat_cnt = len(repeat_todo[repeat_key])
            if repeat_key in repeat_used:
                if repeat_used[repeat_key] >= 3:
                    continue
                elif repeat_used[repeat_key] >= repeat_cnt:
                    continue
                elif group_width > UNIT_WIDTH_ARMOIRE_MID * 2:
                    continue
                else:
                    repeat_cnt = 1
        # 关联检查
        group_relate_door, group_relate_cook, group_relate_bath, group_relate_work = False, False, False, False
        if group_one in group_door:
            group_relate_door = True
        if group_one in group_cook:
            group_relate_cook = True
        if group_one in group_bath:
            group_relate_bath = True
        if group_one in group_work:
            group_relate_work = True
        # 最佳参数
        param_best = {
            'index': -1,
            'type': '',
            'score': -100,
            'count': 1,
            'width': 0,
            'depth': 0,
            'width_rest': 0,
            'ratio': [0, 1],
            'group': []
        }
        # 矩形查找
        for rect_idx, rect_one in enumerate(rect_list):
            # 矩形信息
            rect_angle = rect_one['angle']
            rect_width, rect_depth, rect_height = rect_one['width'], rect_one['depth'], rect_one['height']
            rect_type, type_pre, type_post = rect_one['type'], rect_one['type_pre'], rect_one['type_post']
            # 初步判断
            if rect_type == UNIT_TYPE_GROUP:
                continue
            if rect_type == UNIT_TYPE_WINDOW and group_type == 'Armoire':
                continue
            if rect_type == UNIT_TYPE_WINDOW and group_type == 'Cabinet' and group_height > UNIT_HEIGHT_ARMOIRE_MIN:
                continue
            if rect_type == UNIT_TYPE_AISLE and group_type in ['Work', 'Rest', 'Appliance']:
                continue
            if rect_idx in rect_used:
                if len(rect_used[rect_idx]) >= 2:
                    continue
                used_param = rect_used[rect_idx][0]
                rect_width = used_param['width_rest']
                if rect_width < 0.3 and rect_width < group_width:
                    continue
                if 'group' in used_param and len(used_param['group']) > 0:
                    group_used = used_param['group'][-1]
                    used_type, used_size = group_used['type'], group_used['size']
                    if group_type in ['Work'] and used_type in ['Armoire', 'Cabinet']:
                        if used_size[0] < 1.5:
                            continue
            # 线段信息
            line_idx = rect_one['index']
            line_one = line_list[line_idx]
            line_pre = line_list[(line_idx - 1 + len(line_list)) % len(line_list)]
            line_post = line_list[(line_idx + 1 + len(line_list)) % len(line_list)]
            line_pre2 = line_list[(line_idx - 2 + len(line_list)) % len(line_list)]
            line_post2 = line_list[(line_idx + 2 + len(line_list)) % len(line_list)]
            line_width = line_list[line_idx]['width']
            merge_type, merge_width = [], 0
            if type_pre in [UNIT_TYPE_WINDOW] and line_one['score_pre'] == 1 and line_pre['height'] > group_height:
                merge_type = [UNIT_TYPE_WINDOW]
                merge_width = max(merge_width, line_pre['width'])
            elif type_post in [UNIT_TYPE_WINDOW] and line_one['score_post'] == 1 and line_post['height'] > group_height:
                merge_type = [UNIT_TYPE_WINDOW]
                merge_width = max(merge_width, line_post['width'])
            if type_pre in [UNIT_TYPE_WALL] and line_one['score_pre'] == 1 and 0.5 < line_pre['width'] < line_width:
                if rect_type in [UNIT_TYPE_AISLE]:
                    merge_type = [UNIT_TYPE_WALL]
                    merge_width = max(merge_width, line_pre['width'])
            elif type_post in [UNIT_TYPE_WALL] and line_one['score_post'] == 1 and 0.5 < line_post['width'] < line_width:
                if rect_type in [UNIT_TYPE_AISLE]:
                    merge_type = [UNIT_TYPE_WALL]
                    merge_width = max(merge_width, line_post['width'])
            # 关联信息
            rect_relate_door, rect_relate_cook, rect_relate_bath = False, False, False
            if rect_one in rect_door:
                rect_relate_door = True
            if rect_one in rect_cook:
                rect_relate_cook = True
            if rect_one in rect_bath:
                rect_relate_bath = True

            # 高度判断
            if rect_type == UNIT_TYPE_WINDOW:
                if room_type in ROOM_TYPE_FOR_REST_1 and group_type in ['Work', 'Rest']:
                    if rect_height <= 0.1 and group_height >= 1.0:
                        if room_type not in ['Library'] and group_type in ['Work']:
                            continue
                elif group_height >= rect_one['height'] + 0.4 and group_type not in ['Work', 'Rest']:
                    continue
                elif determine_line_angle(rect_one['angle']) < 0 and group_type not in ['Rest']:
                    continue
            # 宽度判断
            min_width, min_depth, min_width_limit = group_width, group_depth, UNIT_WIDTH_GROUP
            if group_type in ['Armoire', 'Appliance'] and rect_one['score'] < 5 and rect_idx not in rect_used:
                if room_type in ROOM_TYPE_FOR_REST_3:
                    min_depth = group_depth + MIN_GROUP_PASS
            elif group_type in ['Cabinet'] and rect_width > min(1.0, group_width * 0.8) and rect_depth > 0.2:
                if room_type in ROOM_TYPE_FOR_REST_3 or rect_relate_door:
                    min_depth = min(group_depth, rect_depth)
            elif group_type in ['Rest'] and group_depth > group_depth_min * MID_GROUP_PASS:
                min_width = min(group_width_min + MID_GROUP_PASS, group_width)
                min_depth = min(group_depth_min + MID_GROUP_PASS, group_depth)
            elif type_pre in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] and \
                    type_post in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE]:
                min_width = min(group_width_min + MID_GROUP_PASS, group_width + MIN_GROUP_PASS)
            elif type_pre in [UNIT_TYPE_NONE, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] or \
                    type_post in [UNIT_TYPE_NONE, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE]:
                min_width = group_width - MIN_GROUP_PASS / 2
            if 'Bathroom' in room_type:
                min_width_limit = min(0.8, room_area / MID_ROOM_AREA_BATH)
            elif 'CloakRoom' in room_type:
                min_width_limit = min(0.8, room_area / MID_ROOM_AREA_CLOAK)
            else:
                min_width_limit = min(0.8, group_width_min * 0.8)
            if rect_width + merge_width < min_width:
                if rect_width + merge_width < min(group_width * 0.80, min_width_limit):
                    continue
            if rect_width + merge_width <= min_width:
                if rect_relate_door and group_relate_door:
                    pass
                elif rect_relate_bath and group_relate_bath:
                    pass
                elif rect_relate_bath and not group_relate_bath and index_have >= 1:
                    continue
                elif group_type in ['Armoire'] and index_have >= 1:
                    continue
                elif group_type in ['Cabinet'] and index_have >= 2:
                    continue
                elif group_type in ['Work', 'Rest'] or group_fake_flag >= 1:
                    if type_pre in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] and \
                            type_post in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE]:
                        continue
                elif group_type in ['Appliance']:
                    if type_pre in [UNIT_TYPE_SIDE] and line_one['score_pre'] == 1:
                        continue
                    if type_post in [UNIT_TYPE_SIDE] and line_one['score_post'] == 1:
                        continue
            if rect_width + merge_width <= min_width + MID_GROUP_PASS:
                if group_width < 0.5 and group_idx >= 1 and group_type in ['Cabinet']:
                    if type_pre in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR, UNIT_TYPE_SIDE] and \
                            type_post in [UNIT_TYPE_NONE, UNIT_TYPE_SIDE]:
                        continue
                    elif type_post in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR, UNIT_TYPE_SIDE] and \
                            type_pre in [UNIT_TYPE_NONE, UNIT_TYPE_SIDE]:
                        continue
            # 深度判断
            if room_type not in ROOM_TYPE_FOR_REST_3:
                if group_type in ['Appliance'] and rect_depth < UNIT_DEPTH_ASIDE * 0.5 < group_depth:
                    continue
                elif group_type in ['Cabinet'] and rect_depth < min(group_depth - 0.1, group_depth * 0.8):
                    if group_one in group_seed and rect_width > group_width * 0.5:
                        pass
                    elif group_relate_door and rect_relate_door and rect_width > group_width * 0.8:
                        pass
                    elif group_relate_bath and rect_relate_bath and rect_width > group_width * 0.8:
                        pass
                    else:
                        continue
            if 'back_depth' in rect_one and rect_one['back_depth'] > UNIT_DEPTH_BACK_MAX:
                continue
            max_pass, min_pass = 10, min(-0.10, 0 - min_depth * 0.2)
            group_width_new, group_depth_new = min(group_width, min_width), min(group_depth, min_depth)
            suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                compute_suit_ratio(line_list, line_idx, group_width_new, group_depth_new, [0, 1], merge_type, max_pass, min_pass)
            # 宽度判断
            if suit_width < min(min_width, min_width_limit) or suit_width < min_width * 0.5:
                if group_relate_door and rect_relate_door and rect_width > group_width * 0.8:
                    pass
                elif suit_width > min(min_width, min_width_limit) - 0.2:
                    if rect_depth > max(0.2, group_depth_min - 0.2) and rect_one['score'] >= 5:
                        suit_width, suit_ratio = rect_width, [0, 1]
                else:
                    continue
            # 深度判断
            if suit_depth < min_depth - 0.00 and group_type in ['Cabinet']:
                if group_relate_door and rect_relate_door and rect_width > group_width * 0.8:
                    pass
                elif rect_type in [UNIT_TYPE_AISLE] and suit_depth > min_depth - 0.05 and group_idx == 0:
                    pass
                elif suit_depth < min(min_depth * 0.80, min_depth - 0.05):
                    continue
            elif suit_depth < min_depth - 0.05 and group_type in ['Work', 'Rest']:
                continue
            elif suit_depth < min_depth - 0.10:
                continue
            # 扩展处理
            if group_relate_door and rect_relate_door and rect_width > group_width * 0.8:
                if rect_depth > min(group_depth * 0.5, 0.15):
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width_new, rect_depth - 0.01, [0, 1],
                                           merge_type, max_pass, min_pass)
            if type_pre in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] and \
                    type_post in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] and line_one['score'] <= 2:
                if suit_depth_min < group_depth + MID_GROUP_PASS and suit_width < group_width + MID_GROUP_PASS:
                    if group_type in ['Cabinet', 'Armoire'] and group_idx >= 2:
                        continue
                    elif group_type in ['Appliacne']:
                        continue
                if group_depth > max(group_width, 0.5):
                    if group_type in ['Cabinet', 'Armoire'] and group_idx >= 2:
                        continue

            # 占用判断
            same_size_flag, same_depth_flag, same_type_flag = False, False, False
            if rect_idx in rect_used:
                param_used = rect_used[rect_idx][0]
                ready_list = param_used['group']
                group_used = ready_list[0]
                # 占用
                ratio_old, width_old = param_used['ratio'], param_used['width']
                ratio_width = width_old / line_width
                ratio_used_0 = [ratio_old[0], ratio_old[0] + ratio_width]
                ratio_used_1 = [ratio_old[1] - ratio_width, ratio_old[1]]
                # 余下
                ratio_new_0 = compute_diff_ratio(suit_ratio, ratio_used_0)
                ratio_new_1 = compute_diff_ratio(suit_ratio, ratio_used_1)
                suit_width_0 = line_width * (ratio_new_0[1] - ratio_new_0[0])
                suit_width_1 = line_width * (ratio_new_1[1] - ratio_new_1[0])
                # 差异
                width_dlt = abs(group_width - group_used['size'][0])
                height_dlt = abs(group_height - group_used['size'][1])
                depth_dlt = abs(group_depth - group_used['size'][2])
                if max(suit_width_0, suit_width_1) < group_width - 0.15:
                    continue
                elif max(suit_width_0, suit_width_1) < group_width + MID_GROUP_PASS * 2:
                    if type_pre in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] and \
                            type_post in [UNIT_TYPE_DOOR, UNIT_TYPE_SIDE, UNIT_TYPE_AISLE] and \
                            line_one['score_pre'] == 1 and line_one['score_post'] == 1:
                        continue
                    elif group_height > UNIT_HEIGHT_ARMOIRE_MID and depth_dlt < 0.1 and width_dlt > 0.5:
                        continue
                # 尺寸
                if group_type == group_used['type']:
                    same_type_flag = True
                    if height_dlt < 0.05 and depth_dlt < 0.05:
                        same_size_flag = True
                    if height_dlt < 0.50 and depth_dlt < 0.01 and group_type in ['Rest', 'Cabinet']:
                        same_size_flag = True
                elif group_type in ['Armoire', 'Cabinet'] and group_used['type'] in ['Armoire', 'Cabinet']:
                    same_type_flag = True
                    if height_dlt < 0.05 and depth_dlt < 0.05:
                        same_size_flag = True
                    if height_dlt < 0.50 and depth_dlt < 0.01 and group_type in ['Rest', 'Cabinet']:
                        same_size_flag = True
                elif group_type in ['Work'] and group_used['type'] in ['Armoire', 'Cabinet']:
                    if height_dlt < 0.05 and depth_dlt < 0.05:
                        same_size_flag = True
                    if depth_dlt < 0.05:
                        same_depth_flag = True
            if line_one['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_GROUP] and line_pre['height'] > UNIT_HEIGHT_WALL - 0.1:
                if line_pre['unit_group'] in ['Meeting', 'Bed'] and line_pre['unit_edge'] in [1, 3]:
                    if rect_width < group_width + MID_GROUP_PASS * 2:
                        continue
            if line_one['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_GROUP] and line_post['height'] > UNIT_HEIGHT_WALL - 0.1:
                if line_post['unit_group'] in ['Meeting', 'Bed'] and line_post['unit_edge'] in [1, 3]:
                    if rect_width < group_width + MID_GROUP_PASS * 2:
                        continue

            # 打印分数
            suit_print = False
            if 'LivingDiningRoom' in room_type and group_type in ['Cabinet'] and False:
                suit_print = True

            # 位置分数
            score_place = rect_one['score']
            if score_place <= 2:
                if line_one['score'] == 8:
                    score_place = 4
                else:
                    if line_one['score_pre'] == 1:
                        if line_pre['type'] in [UNIT_TYPE_SIDE] and line_pre['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                            score_place += 3
                    if line_one['score_post'] == 1:
                        if line_post['type'] in [UNIT_TYPE_SIDE] and line_post['width'] < UNIT_DEPTH_CURTAIN + 0.01:
                            score_place += 3

            # 位置处理
            side_depth_1, side_depth_2 = group_depth, group_depth
            if score_place <= 2:
                if line_pre['type'] in [UNIT_TYPE_DOOR] and line_post['type'] in [UNIT_TYPE_DOOR]:
                    if line_width >= group_width + MID_GROUP_PASS:
                        score_place = 4
                elif line_pre['type'] in [UNIT_TYPE_WINDOW] and line_post['type'] in [UNIT_TYPE_WINDOW]:
                    if line_width >= group_width + 0:
                        score_place = 4
                elif line_pre['type'] in [UNIT_TYPE_GROUP, UNIT_TYPE_SIDE] \
                        and line_post['type'] in [UNIT_TYPE_GROUP, UNIT_TYPE_SIDE]:
                    if rect_width > MID_GROUP_PASS and room_type in ROOM_TYPE_FOR_REST_3:
                        score_place = 5
                elif line_one['score'] > 2 and group_height <= UNIT_HEIGHT_ARMOIRE_MIN:
                    score_place = line_one['score']
                    if line_pre['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] or \
                            line_post['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
                        score_place = min(line_one['score'], 4)
            elif score_place >= 5:
                # 两侧深度
                well_depth, side_depth_1, side_depth_2 = group_depth, line_one['depth_pre'], line_one['depth_post']
                # 深度判断 TODO:
                if rect_idx in rect_used:
                    if room_type not in ROOM_TYPE_FOR_REST_4:
                        score_place = 5
                elif max(side_depth_1, side_depth_2) < min(group_depth, well_depth) - 0.1:
                    score_place = 3
                elif group_type in ['Work', 'Rest'] and score_place >= 8:
                    score_place = 6
            if line_one['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR]:
                if line_one['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_GROUP, UNIT_TYPE_DOOR]:
                    if rect_width < group_width and group_height > UNIT_HEIGHT_SHELF_MIN:
                        score_place -= 2
                    elif rect_width < group_width + MID_GROUP_PASS * 2:
                        score_place -= 1
            # 斜墙处理
            if determine_line_angle(rect_one['angle']) < 0:
                score_place -= 2
            # 占用处理
            face_flag = False
            if rect_idx in rect_used:
                if same_size_flag:
                    score_place += 2
                elif same_depth_flag:
                    score_place += 0
                elif room_type in ROOM_TYPE_LEVEL_1:
                    if same_type_flag and rect_width < group_width:
                        continue
                    else:
                        score_place -= 4
                elif room_type in ROOM_TYPE_FOR_REST_2:
                    if rect_width < group_width + MIN_GROUP_PASS * 1:
                        score_place -= 4
                    elif rect_width < group_width + MIN_GROUP_PASS * 2:
                        score_place -= 2
                    elif rect_width > group_width + MIN_GROUP_PASS * 1 and group_type in ['Cabinet']:
                        if same_type_flag:
                            score_place += 1
                        else:
                            score_place -= 1
                elif room_type in ROOM_TYPE_FOR_REST_3:
                    if rect_width < group_width:
                        score_place -= 3
                    elif rect_width < group_width + MIN_GROUP_PASS * 2:
                        score_place -= 2
                else:
                    score_place -= 4
            # 相对处理
            if rect_idx in rect_used and same_size_flag:
                pass
            elif len(rect_used) > 0:
                for rect_idx_old in rect_used.keys():
                    rect_old = rect_list[rect_idx_old]
                    used_idx = rect_old['index']
                    line_old = line_list[used_idx]
                    depth_old, angle_old = rect_old['depth'], rect_old['angle']
                    if abs(ang_to_ang(rect_angle - angle_old)) < 0.01:
                        continue
                    width_new, depth_new, ratio_new, ratio_new_best, ratio_pair = \
                        compute_pair_ratio(line_old, [0, 1], line_one)
                    if width_new <= 0.01:
                        continue
                    if depth_new - depth_old >= max(group_depth * 2, 1) and room_type in ROOM_TYPE_FOR_REST_1:
                        continue
                    if depth_new - depth_old >= max(group_depth * 2, 1) and room_type in ROOM_TYPE_FOR_REST_2:
                        continue
                    if depth_new - depth_old >= MID_GROUP_PASS and room_type in ROOM_TYPE_FOR_REST_3:
                        continue
                    face_depth_well = max(MID_GROUP_PASS * 2, depth_old + group_depth + MID_GROUP_PASS)
                    face_ratio_well = min(ratio_pair[1], 1) - max(ratio_pair[0], 0)
                    if face_ratio_well > 0.5 and depth_new <= face_depth_well:
                        if group_type in ['Armoire']:
                            face_flag = True
                            score_place -= 2
                        elif group_type in ['Cabinet']:
                            face_flag = True
                            score_place -= 2
                        elif group_type in ['Appliance']:
                            face_flag = True
                            score_place -= 2
                    elif face_ratio_well > 0.5 and depth_new <= MID_GROUP_PASS * 2:
                        face_flag = True
                        score_place -= 2
                    elif face_ratio_well > 0.2 and depth_new <= MID_GROUP_PASS * 2:
                        score_place -= 2
                    break
                if face_flag and group_idx >= 1:
                    continue
                none_side_1, none_side_2 = False, False
                face_side_1, face_side_2 = False, False
                if rect_one['score_pre'] == 1:
                    if line_pre['type'] == UNIT_TYPE_GROUP or rect_one['type_pre'] == UNIT_TYPE_SIDE:
                        face_side_1 = True
                elif rect_one['score_pre'] == 2:
                    none_side_1 = True
                if rect_one['score_post'] == 1:
                    if line_post['type'] == UNIT_TYPE_GROUP or rect_one['type_post'] == UNIT_TYPE_SIDE:
                        face_side_2 = True
                elif rect_one['score_post'] == 2:
                    none_side_2 = True
                if group_type in ['Armoire', 'Cabinet'] and rect_width < group_width + MID_GROUP_PASS:
                    if face_side_1 and face_side_2:
                        score_place -= 4
                    elif face_side_1 and none_side_2:
                        score_place -= 2
                    elif face_side_2 and none_side_1:
                        score_place -= 2

            # 通道处理
            if rect_one['type'] == UNIT_TYPE_AISLE and group_type in ['Work', 'Appliance']:
                continue
            if rect_one['type'] == UNIT_TYPE_AISLE and group_type in ['Armoire', 'Cabinet']:
                if line_one['depth'] > UNIT_WIDTH_HOLE:
                    pass
                elif group_relate_door and not rect_relate_door:
                    continue
                elif group_relate_cook and not rect_relate_cook:
                    continue
                elif group_relate_bath and not rect_relate_bath:
                    continue
            if rect_width < group_width + MID_GROUP_PASS and group_type in ['Armoire', 'Cabinet', 'Appliance']:
                if rect_one['type_pre'] in [UNIT_TYPE_GROUP, UNIT_TYPE_AISLE] and rect_one['score_pre'] == 1:
                    if rect_one['type_post'] in [UNIT_TYPE_GROUP, UNIT_TYPE_AISLE] and rect_one['score_post'] == 1:
                        if room_type in ROOM_TYPE_FOR_REST_1 and len(group_sort) > 1:
                            if group_idx <= 0:
                                score_place -= 4
                            else:
                                continue
                if rect_one['type_pre'] in [UNIT_TYPE_GROUP] and 'unit_edge' in line_pre:
                    if line_pre['unit_edge'] >= 1:
                        score_place -= 1
                if rect_one['type_post'] in [UNIT_TYPE_GROUP] and 'unit_edge' in line_post:
                    if line_post['unit_edge'] >= 1:
                        score_place -= 1

            # 靠近处理
            if group_type in ['Work', 'Rest'] and rect_idx not in rect_used:
                if rect_relate_door or rect_relate_cook or rect_relate_bath:
                    continue
            elif group_type in ['Armoire']:
                if (rect_one['type_pre'] in [UNIT_TYPE_GROUP] and rect_one['score_pre'] == 1) or \
                        (rect_one['type_post'] in [UNIT_TYPE_GROUP] and rect_one['score_post'] == 1):
                    score_place -= 1
                    if rect_width < group_width:
                        score_place -= 1
            elif group_type in ['Appliance']:
                if line_one['score_pre'] == 1 and line_pre['type'] == UNIT_TYPE_GROUP and line_pre['unit_edge'] == 0:
                    if 'refrigerator' in group_main_type:
                        score_place += 1
                    elif 'conditioner' in group_main_type:
                        score_place += 2
                elif line_one['score_post'] == 1 and line_post['type'] == UNIT_TYPE_GROUP and line_post['unit_edge'] == 0:
                    if 'refrigerator' in group_main_type:
                        score_place += 1
                    elif 'conditioner' in group_main_type:
                        score_place += 2
            # 靠窗处理
            if group_type in ['Armoire', 'Appliance']:
                if rect_type == UNIT_TYPE_WINDOW:
                    if group_idx >= 1 and group_type in ['Cabinet']:
                        continue
                    elif rect_width < group_width * 0.8:
                        continue
                    score_place -= 2
                    if score_place > 4:
                        score_place = 4
                elif type_pre == UNIT_TYPE_WINDOW and rect_one['score_pre'] in [1, 4]:
                    if room_type not in ROOM_TYPE_FOR_REST_3:
                        score_place -= 2
                        if group_height > line_pre['height'] + 0.2 and rect_width < group_width:
                            score_place -= 2
                elif type_post == UNIT_TYPE_WINDOW and rect_one['score_post'] in [1, 4]:
                    if room_type not in ROOM_TYPE_FOR_REST_3:
                        score_place -= 2
                        if group_height > line_post['height'] + 0.2 and rect_width < group_width:
                            score_place -= 2

            # 长度处理
            if rect_width < min(group_width - 0.2, group_width * 0.8) and score_place > 2:
                score_place = 2
            if 'seed_size_new' in group_one and len(group_one['seed_size_new']) >= 3:
                seed_size = group_one['seed_size_new']
                if rect_width < min(seed_size[0] - 0.1, seed_size[0] * 0.9):
                    score_place = 0
            # 深度处理
            if rect_one['score_pre'] == 4 and line_pre['score_pre'] == 1:
                if line_pre['width'] < group_depth + MID_GROUP_PASS  and line_pre2['type'] in [UNIT_TYPE_GROUP]:
                    score_place -= 2
            if rect_one['score_post'] == 4 and line_post['score_post'] == 1:
                if line_post['width'] < group_depth + MID_GROUP_PASS and line_post2['type'] in [UNIT_TYPE_GROUP]:
                    score_place -= 2
            # 关联处理
            score_relate = 0
            if room_type in ['LivingDiningRoom', 'LivingRoom'] or group_relate_door:
                if (group_relate_door and rect_relate_door) \
                        or (group_relate_cook and rect_relate_cook) \
                        or (group_relate_bath and rect_relate_bath):
                    if rect_depth > group_depth - 0.1 and rect_width > min(group_width - 0.1, 1.5):
                        score_relate += 8
                        if group_relate_door and rect_relate_bath:
                            score_relate -= 2
                    elif rect_depth > max(group_depth * 0.5, 0.2) and rect_width > min(group_width - 0.1, 1.5):
                        score_relate += 6
                    elif rect_depth > max(group_depth * 0.5, 0.2):
                        score_relate += 2
                    else:
                        score_relate -= 2
                elif group_relate_door and not rect_relate_door:
                    rect_has = False
                    for rect_old in rect_door:
                        if rect_old['width'] > min(group_width * 0.5, 1.0):
                            rect_has = True
                            break
                    if rect_has or group_relate_cook or group_relate_bath:
                        continue
                elif group_relate_bath and not rect_relate_bath:
                    continue
                elif group_relate_cook and not rect_relate_cook:
                    score_relate -= 8
                    if group_idx >= 1 and (rect_relate_door or rect_relate_bath):
                        continue
                elif rect_relate_door and not group_relate_door:
                    if len(group_door) > 0 or group_type not in ['Cabinet']:
                        score_relate -= 8
                        continue
                    else:
                        score_relate -= 4
            elif room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom'] or group_relate_bath:
                if group_relate_bath and not rect_relate_bath:
                    continue

            # 距离分数
            score_distance = 0
            if len(door_pt_entry) > 0:
                if room_type in ROOM_TYPE_LEVEL_1:
                    pass
                elif room_type in ROOM_TYPE_FOR_REST_2:
                    if group_type in ['Armoire']:
                        dis_ratio = [0, 1]
                        if line_one['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_SIDE]:
                            dis_ratio[0] = 0 - line_pre['width'] / line_one['width']
                        if line_one['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_SIDE]:
                            dis_ratio[1] = 1 + line_post['width'] / line_one['width']
                        dis1, dis2, dis3 = compute_line_distance(line_one, dis_ratio, door_pt_entry, rect_depth / 2, 2)
                        suit_distance_entry = min(dis1, dis2, dis3, 6)
                        score_distance -= suit_distance_entry
                elif room_type in ROOM_TYPE_FOR_REST_3:
                    dis_ratio = [0, 1]
                    dis1, dis2, dis3 = compute_line_distance(line_one, dis_ratio, door_pt_entry, rect_depth / 2, 2)
                    suit_distance_entry = min(dis1, dis2, dis3)
                    if group_type in ['Cabinet', 'Appliance']:
                        suit_distance_entry = 0
                    score_distance -= suit_distance_entry
            if len(door_pt_bath) > 0:
                if room_type in ['LivingDiningRoom', 'LivingRoom']:
                    dis1, dis2, dis3 = compute_line_distance(line_one, [0, 1], door_pt_bath, rect_depth / 2, 2)
                    relate_flag = False
                    if rect_one in rect_bath:
                        relate_flag = True
                    if group_relate_bath and relate_flag:
                        if rect_depth > group_depth - 0.05 and rect_width > min(group_width - 0.05, UNIT_WIDTH_GROUP):
                            if score_place > 5:
                                score_place = 5
                            if rect_width >= group_width - 0.05:
                                score_distance += (8 - min(dis1, dis2, dis3))
                            else:
                                score_distance += (4 - min(dis1, dis2, dis3))
                        elif rect_depth > group_depth - 0.10:
                            score_place = 2
                            score_distance += 0
                        else:
                            score_distance -= 4
                    elif group_relate_bath and not relate_flag:
                        score_distance -= 8
                    elif relate_flag and not group_relate_bath and len(group_bath) > 0:
                        score_distance -= 8
                        if rect_idx in rect_used:
                            continue
            # 靠床处理
            if room_type in ROOM_TYPE_LEVEL_2 and len(rect_pt_head) >= 2 and len(rect_size_bed) >= 3:
                dis4, dis5, dis6 = compute_line_distance(line_one, [0, 1], rect_pt_head, rect_depth / 2, 2)
                suit_distance_bed = min(dis4, dis5, dis6)
                if group_type in ['Work', 'Cabinet'] and rect_size_bed[0] > rect_size_bed[2] and rect_size_bed[1] > UNIT_HEIGHT_SHELF_MIN:
                    score_distance += suit_distance_bed
                elif group_type in ['Armoire'] or group_idx <= 0:
                    score_distance -= suit_distance_bed

            # 尺寸分数
            score_width, score_depth, score_height = 0, 0, 0
            # 重复摆放
            repeat_max, group_width_max = 1, group_width
            if group_type in ['Armoire', 'Cabinet']:
                side_width = 0
                if line_one['score_pre'] == 1 and line_pre['type'] == UNIT_TYPE_SIDE:
                    side_width = MIN_GROUP_PASS - 0.05
                elif line_one['score_post'] == 1 and line_post['type'] == UNIT_TYPE_SIDE:
                    side_width = MIN_GROUP_PASS - 0.05
                elif line_one['score'] == 8 and group_width < 1.5 and group_width * 2 < line_width + MIN_GROUP_PASS:
                    side_width = MIN_GROUP_PASS
                repeat_key = group_type + '_' + str(round(group_height, 1)) + '_' + str(round(group_depth, 1))
                if repeat_key in repeat_todo:
                    repeat_max, group_width_max = 0, 0
                    for repeat_one in repeat_todo[repeat_key]:
                        if group_width_max + repeat_one['size'][0] >= rect_width * 1.1 + side_width:
                            break
                        else:
                            repeat_max += 1
                            group_width_max += repeat_one['size'][0]
                if repeat_max <= 1:
                    repeat_max = int((rect_width + side_width) / group_width)
                    group_width_max = repeat_max * group_width
                if repeat_max > repeat_cnt:
                    repeat_max = repeat_cnt
                    group_width_max = group_width
                count_best = repeat_max
                if count_best < 1:
                    count_best = 1
                if count_best > repeat_cnt:
                    count_best = repeat_cnt
            else:
                count_best = 1
            # 宽度处理
            score_width = group_width
            aside_width = rect_width
            if rect_idx in rect_used:
                score_width = rect_width / 2
                if score_width > group_width:
                    score_width = group_width
            else:
                if len(merge_type) > 0:
                    aside_width = min(suit_width, rect_width * 2)
                elif rect_one['score_pre'] == 2 or rect_one['score_post'] == 2:
                    if abs(rect_width - suit_width) < 0.1:
                        aside_width += min(rect_width * 0.1, 0.2)
                if aside_width > group_width_max > 0:
                    score_width = group_width_max
                    if room_type in ROOM_TYPE_FOR_REST_3 and group_type in ['Cabinet']:
                        score_width = min(aside_width, group_width_max + MID_GROUP_PASS)
                elif aside_width < group_width - 0.2:
                    score_width = rect_width - (group_width - rect_width) * 2
                elif aside_width < group_width - 0.1:
                    score_width = rect_width - (group_width - rect_width) * 1
                else:
                    score_width = min(aside_width, group_width * 2)
            # 深度处理
            score_depth = group_depth
            aside_depth = group_depth
            if rect_depth < group_depth:
                aside_depth = rect_depth
            if rect_one['score_pre'] == 4 and type_pre == UNIT_TYPE_WALL and rect_idx not in rect_used:
                if aside_depth < rect_one['depth_pre']:
                    aside_depth = rect_one['depth_pre']
            if rect_one['score_post'] == 4 and type_post == UNIT_TYPE_WALL and rect_idx not in rect_used:
                if aside_depth < rect_one['depth_post']:
                    aside_depth = rect_one['depth_post']
            if rect_one['score_pre'] == 1 and type_pre == UNIT_TYPE_GROUP and rect_idx not in rect_used:
                if group_type == 'Work' and aside_depth < rect_one['depth_pre']:
                    aside_depth = rect_one['depth_pre']
            if rect_one['score_post'] == 1 and type_post == UNIT_TYPE_GROUP and rect_idx not in rect_used:
                if group_type == 'Work' and aside_depth < rect_one['depth_post']:
                    aside_depth = rect_one['depth_post']
            if suit_depth < 3 and group_type in ['Appliance']:
                aside_depth = 0
            if aside_depth > group_depth + MIN_GROUP_PASS:
                score_depth = group_depth + MIN_GROUP_PASS
            elif aside_depth >= group_depth:
                score_depth = group_depth
            else:
                score_depth = aside_depth

            # 高度处理
            pass

            # 整体分数
            suit_score = score_place + score_relate + score_distance + score_width + score_depth + score_height
            if suit_print:
                print('group %02d rect %02d score: %.2f %.2f %.2f %.2f %.2f %.2f = %.2f' %
                      (group_idx, rect_idx, score_place, score_relate, score_distance, score_width, score_depth, score_height, suit_score))
            if suit_score > param_best['score']:
                param_best['index'] = rect_idx
                param_best['type'] = group_type
                param_best['score'] = suit_score
                param_best['count'] = count_best
                param_best['width'] = count_best * group_width
                param_best['depth'] = group_depth
                param_best['width_rest'] = rect_width - count_best * group_width
                param_best['ratio'] = suit_ratio[:]
                if rect_width < line_width < rect_width + UNIT_DEPTH_CURTAIN:
                    param_best['width_rest'] = line_width - count_best * group_width

        # 参数判断
        index_best = int(param_best['index'])
        if index_best < 0:
            continue
        # 复制检查
        count_best = param_best['count']
        repeat_key = group_type + '_' + str(round(group_height, 1)) + '_' + str(round(group_depth, 1))
        if count_best > 1 or repeat_key in repeat_todo:
            if repeat_key not in repeat_used:
                repeat_used[repeat_key] = count_best
            else:
                repeat_used[repeat_key] += count_best

        # 参数信息
        param_add = param_best.copy()
        param_add['ratio'] = param_best['ratio'][:]
        # 组合信息
        for i in range(count_best):
            if repeat_key in repeat_todo and 0 <= i < len(repeat_todo[repeat_key]):
                group_add = copy_exist_group(repeat_todo[repeat_key][i])
            else:
                group_add = copy_exist_group(group_one)
            param_add['group'].append(group_add)
        # 参数添加 扩展更新
        if index_best in rect_used:
            param_used = rect_used[index_best]
        else:
            rect_used[index_best] = []
            index_todo.append(index_best)
            rect_one = rect_list[index_best]
            rect_one['used'] = 1
            # 扩展信息
            best_ratio = param_best['ratio']
            if best_ratio[0] > 0 or best_ratio[1] < 1:
                rect_one = rect_list[index_best]
                line_one = line_list[rect_one['index']]
                x1_old = line_one['p1'][0]
                y1_old = line_one['p1'][1]
                x2_old = line_one['p2'][0]
                y2_old = line_one['p2'][1]
                # p1 p2
                x1_new = x1_old * (1 - best_ratio[0]) + x2_old * best_ratio[0]
                y1_new = y1_old * (1 - best_ratio[0]) + y2_old * best_ratio[0]
                x2_new = x1_old * (1 - best_ratio[1]) + x2_old * best_ratio[1]
                y2_new = y1_old * (1 - best_ratio[1]) + y2_old * best_ratio[1]
                # p3 p4
                angle = rect_one['angle']
                x_delta = group_depth * math.sin(angle)
                y_delta = group_depth * math.cos(angle)
                x3_new = x2_new + x_delta
                y3_new = y2_new + y_delta
                x4_new = x1_new + x_delta
                y4_new = y1_new + y_delta
                # 扩展
                x_min = min(x1_new, x2_new, x3_new, x4_new)
                x_max = max(x1_new, x2_new, x3_new, x4_new)
                y_min = min(y1_new, y2_new, y3_new, y4_new)
                y_max = max(y1_new, y2_new, y3_new, y4_new)
                if rect_one['expand'][0] < x_min:
                    rect_one['expand'][0] = x_min
                if rect_one['expand'][1] < y_min:
                    rect_one['expand'][1] = y_min
                if rect_one['expand'][2] > x_max:
                    rect_one['expand'][2] = x_max
                if rect_one['expand'][3] > y_max:
                    rect_one['expand'][3] = y_max
        rect_used[index_best].append(param_add)
        if 'group' in param_add:
            index_have += len(param_add['group'])

    # 计算布局
    group_result = []
    for rect_idx in index_todo:
        # 矩形信息
        rect_one = rect_list[rect_idx]
        rect_type = rect_one['type']
        rect_width, rect_depth, rect_height = rect_one['width'], rect_one['depth'], rect_one['height']
        rect_angle = normalize_line_angle(rect_one['angle'])
        p1, p2 = rect_one['p1'], rect_one['p2']
        if rect_type in [UNIT_TYPE_AISLE] and rect_depth > MIN_GROUP_PASS:
            rect_depth = max(rect_depth * 0.8, rect_depth - 0.1)
        # 布局信息
        param_list = rect_used[rect_idx]
        param_cnt = len(param_list)
        # 布局顺序
        ratio_pre, ratio_post, ratio_dir = -5, 5, 0
        score_pre, score_post = rect_one['score_pre'], rect_one['score_post']
        type_pre, type_post = rect_one['type_pre'], rect_one['type_post']
        curtain_pre, curtain_post = 0, 0
        width_pre, width_post = rect_depth, rect_depth
        # 部件信息
        line_idx = rect_one['index']
        line_one = line_list[line_idx]
        line_idx_pre = (line_idx - 1 + len(line_list)) % len(line_list)
        line_idx_post = (line_idx + 1 + len(line_list)) % len(line_list)
        line_idx_pre2 = (line_idx - 2 + len(line_list)) % len(line_list)
        line_idx_post2 = (line_idx + 2 + len(line_list)) % len(line_list)
        line_one_pre = line_list[line_idx_pre]
        line_one_post = line_list[line_idx_post]
        line_one_pre2 = line_list[line_idx_pre2]
        line_one_post2 = line_list[line_idx_post2]
        #
        if type_pre in [UNIT_TYPE_SIDE] and score_pre == 1 and line_one_pre['width'] < UNIT_DEPTH_CURTAIN + 0.01:
            type_pre, score_pre, curtain_pre = UNIT_TYPE_WALL, 4, 1
        if type_post in [UNIT_TYPE_SIDE] and score_post == 1 and line_one_post['width'] < UNIT_DEPTH_CURTAIN + 0.01:
            type_post, score_post, curtain_post = UNIT_TYPE_WALL, 4, 1
        if line_one['score_pre'] >= 4:
            width_pre = line_one['depth_pre']
        if line_one['score_post'] >= 4:
            width_post = line_one['depth_post']
        #
        if 'Bath' in room_type and param_cnt >= 2:
            param_1 = param_list[1]
            param_list.pop(1)
            param_list.insert(0, param_1)
        # 遍历参数
        for param_idx, param_one in enumerate(param_list):
            # 组合信息
            group_cnt = param_one['count']
            group_one = param_one['group'][0]
            group_type, group_zone = group_one['type'], ''
            group_width, group_depth, group_ratio = group_one['size'][0], group_one['size'][2], param_one['ratio'][:]
            if 'zone' in group_one:
                group_zone = group_one['zone']
                if group_zone in ['']:
                    if rect_one in rect_door:
                        group_zone = 'Hallway'
                    elif rect_one in rect_cook:
                        group_zone = 'DiningRoom'
                    elif rect_one in rect_bath and 'Bedroom' in room_type:
                        group_zone = 'Bathroom'
                elif group_zone in ['Hallway']:
                    if rect_one in rect_door:
                        group_zone = 'Hallway'
                    elif rect_one in rect_cook:
                        group_zone = 'DiningRoom'
                    elif rect_one in rect_bath and 'Bedroom' in room_type:
                        group_zone = 'Bathroom'
            # 布局方向
            if group_type in ['Cabinet'] and group_height >= UNIT_HEIGHT_ARMOIRE_MIN:
                if room_type in ROOM_TYPE_FOR_REST_2:
                    group_type = 'Armoire'
            if room_type in ROOM_TYPE_FOR_REST_3:
                if group_type in ['Appliance']:
                    if score_pre > score_post and type_pre >= type_post:
                        ratio_dir = 1
                    elif score_pre < score_post and type_pre <= type_post:
                        ratio_dir = -1
                    elif score_pre == score_post == 1:
                        ratio_dir = 0
                    elif len(door_pt_entry) > 0 and room_type not in ['Balcony', 'Terrace']:
                        dis1, dis2, dis3 = compute_point_distance(p1, p2, [0, 1], door_pt_entry, 2)
                        if abs(dis1 - dis2) <= MIN_GROUP_PASS:
                            ratio_dir = 0
                        elif dis1 < dis2:
                            ratio_dir = -1
                        elif dis1 > dis2:
                            ratio_dir = 1
                elif param_cnt <= 1:
                    dis1, dis2, dis3 = compute_point_distance(p1, p2, [0, 1], door_pt_entry, 2)
                    if abs(dis1 - dis2) <= MIN_GROUP_PASS:
                        ratio_dir = 0
                    elif rect_width > group_width and rect_depth < group_depth:
                        ratio_dir = 0
                    elif rect_width > group_width and min(width_pre, width_post) < group_depth:
                        ratio_dir = 0
                    elif dis1 < dis2 and rect_width > group_width + MID_GROUP_PASS:
                        ratio_dir = 1
                    elif dis1 > dis2 and rect_width > group_width + MID_GROUP_PASS:
                        ratio_dir = -1
                    if room_type in ROOM_TYPE_FOR_BATH_1 and param_one['width_rest'] < MID_GROUP_PASS:
                        if score_pre >= 4 and score_post <= 2 and type_pre >= type_post:
                            ratio_dir = 1
                        elif score_pre <= 2 and score_post >= 4 and type_pre <= type_post:
                            ratio_dir = -1
                    elif room_type in ROOM_TYPE_FOR_REST_4:
                        if score_pre >= 4 and score_post <= 2 and type_pre >= type_post:
                            ratio_dir = 1
                        elif score_pre <= 2 and score_post >= 4 and type_pre <= type_post:
                            ratio_dir = -1
            elif group_zone in ['Hallway'] and rect_one in rect_door and len(door_pt_entry) > 0:
                door_center = door_pt_entry
                dis1 = abs(p1[0] - door_center[0]) + abs(p1[1] - door_center[1])
                dis2 = abs(p2[0] - door_center[0]) + abs(p2[1] - door_center[1])
                if abs(dis1 - dis2) < rect_width * 0.25:
                    ratio_dir = 0
                elif dis1 < dis2:
                    ratio_dir = 1
                    if group_ratio[0] < 0.01 and line_one['score_pre'] == 4 and score_pre == 1:
                        p1_mov, p1_ang = xyz_to_ang(p1[0], p1[1], line_one['p1'][0], line_one['p1'][1])
                        if p1_mov < UNIT_WIDTH_DOOR:
                            group_ratio[0] = min(group_ratio[0], 0 - p1_mov / rect_width)
                            ratio_pre = group_ratio[0]
                    elif group_cnt <= 1 and param_one['width_rest'] <= 0.4 and line_one['score_pre'] == 1:
                        if score_post == 4:
                            ratio_dir = -1
                        else:
                            ratio_dir = 0
                elif dis2 < dis1:
                    ratio_dir = -1
                    if group_ratio[1] > 0.99 and line_one['score_post'] == 4 and score_post == 1:
                        p2_mov, p2_ang = xyz_to_ang(p2[0], p2[1], line_one['p2'][0], line_one['p2'][1])
                        if p2_mov < UNIT_WIDTH_DOOR:
                            group_ratio[1] = max(group_ratio[1], 1 + p2_mov / rect_width)
                            ratio_post = group_ratio[1]
                    elif group_cnt <= 1 and param_one['width_rest'] <= 0.4 and line_one['score_post'] == 1:
                        if score_pre == 4:
                            ratio_dir = 1
                        else:
                            ratio_dir = 0
            elif rect_type == UNIT_TYPE_WINDOW and group_type in ['Work', 'Rest'] and param_cnt <= 1 \
                    and min(width_pre, width_post) > group_depth:
                ratio_dir = 0
            elif min(score_pre, score_post) >= 4 and group_type in ['Cabinet', 'Appliance'] and group_cnt <= 1:
                ratio_dir = 0
            elif max(score_pre, score_post) <= 2 and group_type in ['Work', 'Rest', 'Cabinet', 'Appliance']:
                ratio_dir = 0
            elif curtain_pre > curtain_post or (score_pre > score_post and type_pre > type_post):
                ratio_dir = 1
                if room_type in ROOM_TYPE_FOR_REST_1:
                    if score_post >= 2 and rect_width > group_width + MID_GROUP_PASS:
                        ratio_dir = 0
                    elif group_type in ['Work'] and rect_width > group_width + MID_GROUP_PASS:
                        ratio_dir = 0
            elif curtain_post > curtain_pre or (score_post > score_pre and type_post > type_pre):
                ratio_dir = -1
                if room_type in ROOM_TYPE_FOR_REST_1:
                    if score_pre >= 2 and rect_width > group_width + MID_GROUP_PASS:
                        ratio_dir = 0
                    elif group_type in ['Work'] and rect_width > group_width + MID_GROUP_PASS:
                        ratio_dir = 0
            # 布局方向 足够
            elif len(door_pt_entry) > 0:
                door_center = door_pt_entry
                dis1 = abs(p1[0] - door_center[0]) + abs(p1[1] - door_center[1])
                dis2 = abs(p2[0] - door_center[0]) + abs(p2[1] - door_center[1])
                if dis1 > dis2 + MID_GROUP_PASS:
                    ratio_dir = 1
                elif dis2 > dis1 + MID_GROUP_PASS:
                    ratio_dir = -1
            else:
                ratio_dir = 0
            # 起止比例
            if ratio_pre < group_ratio[0]:
                ratio_pre = group_ratio[0]
            if ratio_post > group_ratio[1]:
                ratio_post = group_ratio[1]
            width_rest_new = rect_width * (ratio_post - ratio_pre) - group_width * group_cnt
            # 靠窗标志
            window_flag = 0
            if rect_type == UNIT_TYPE_WINDOW:
                window_flag = 1
            # 遍历组合
            for group_idx in range(group_cnt):
                # 组合信息
                group_one = param_one['group'][group_idx]
                group_width, group_depth = group_one['size'][0], group_one['size'][2]
                group_angle, group_height = rect_angle, group_one['size'][1]
                if rect_one['height'] < group_height:
                    rect_one['height'] = group_height
                # 剩余宽度
                group_regulation = [0, 0, 0, 0]
                # 横向比例
                rect_width_suit = (ratio_post - ratio_pre) * rect_width
                if score_pre == 1 and type_pre in [UNIT_TYPE_DOOR] and param_cnt <= 1 and group_cnt <= 1 and \
                        rect_width_suit - 0.1 < group_width and ratio_dir >= 0:
                    width_best = (ratio_post - ratio_pre) * rect_width
                    ratio_w = ratio_post - width_best * 0.5 / rect_width
                    width_dump = (group_width - width_best) * 0.5
                    group_regulation = [0, -width_dump, 0, -width_dump]
                elif score_post == 1 and type_post in [UNIT_TYPE_DOOR] and param_cnt <= 1 and group_cnt <= 1 and \
                        rect_width_suit - 0.1 < group_width and ratio_dir <= 0:
                    width_best = (ratio_post - ratio_pre) * rect_width
                    ratio_w = ratio_pre + width_best * 0.5 / rect_width
                    width_dump = (group_width - width_best) * 0.5
                    group_regulation = [0, -width_dump, 0, -width_dump]
                elif rect_width_suit < group_width and ratio_dir == 0:
                    ratio_w = (ratio_pre + ratio_post) * 0.5
                    width_dump = (group_width - (ratio_post - ratio_pre) * rect_width) * 0.5
                    if width_dump < 0.01:
                        width_dump = 0
                    group_regulation = [0, -width_dump, 0, -width_dump]
                else:
                    width_delta, width_delta_half, width_delta_mov = group_width, 0, 0
                    if param_cnt <= 1 and group_cnt <= 1:
                        width_delta_half = (rect_width_suit - group_width) * 0.5
                        if width_delta_half > 2.0 or -0.01 <= width_delta_half < 0:
                            width_delta_half = 0
                        if width_delta_half < -0.01:
                            pass
                        elif width_delta_half > MIN_GROUP_PASS * 2:
                            width_delta_half = MIN_GROUP_PASS * 2
                        elif width_delta_half > MIN_GROUP_PASS * 1:
                            width_delta_half = MIN_GROUP_PASS * 1
                        group_regulation = [0, width_delta_half, 0, width_delta_half]
                        width_delta = group_width + width_delta_half * 2
                        if ratio_dir >= 1:
                            group_regulation = [0, width_delta_half * 2, 0, 0]
                            if group_depth > rect_depth + 0.01 and width_delta_half > 0.01:
                                width_delta_mov = min(width_delta_half, 0.20)
                                group_regulation = [0, width_delta_half * 2 - width_delta_mov, 0, 0]
                            if width_delta_half > 0.2 and group_height <= UNIT_HEIGHT_SHELF_MIN:
                                group_regulation = [0, 0, 0, 0]
                        elif ratio_dir <= -1:
                            group_regulation = [0, 0, 0, width_delta_half * 2]
                            if group_depth > rect_depth + 0.01 and width_delta_half > 0.01:
                                width_delta_mov = min(width_delta_half, 0.20)
                                group_regulation = [0, 0, 0, width_delta_half * 2 - width_delta_mov]
                            if width_delta_half > 0.2 and group_height <= UNIT_HEIGHT_SHELF_MIN:
                                group_regulation = [0, 0, 0, 0]
                    elif param_cnt == 2:
                        width_delta_half = min(param_list[0]['width_rest'], param_list[1]['width_rest']) * 0.5
                        if param_idx <= 0:
                            width_delta_half = 0
                        group_regulation = [0, width_delta_half, 0, width_delta_half]
                        if ratio_dir >= 1:
                            group_regulation = [0, width_delta_half * 2, 0, 0]
                        elif ratio_dir <= -1:
                            group_regulation = [0, 0, 0, width_delta_half * 2]
                    else:
                        width_delta_half = (rect_width_suit - group_width * group_cnt) * 0.5
                        if group_idx < group_cnt - 1 or width_delta_half < 0.01:
                            width_delta_half = 0
                        if ratio_dir >= 1:
                            group_regulation = [0, width_delta_half * 2, 0, 0]
                        elif ratio_dir <= -1:
                            group_regulation = [0, 0, 0, width_delta_half * 2]
                    if ratio_dir >= 1:
                        ratio_w = ratio_pre + (group_width + width_delta_mov) / rect_width * 0.5
                        ratio_pre = ratio_pre + (width_delta + width_delta_mov) / rect_width
                    elif ratio_dir <= -1:
                        ratio_w = ratio_post - (group_width + width_delta_mov) / rect_width * 0.5
                        ratio_post = ratio_post - (width_delta + width_delta_mov) / rect_width
                    else:
                        if param_cnt <= 1 and group_cnt <= 1:
                            ratio_w = (ratio_pre + ratio_post) * 0.5
                            group_regulation = [0, width_delta_half, 0, width_delta_half]
                        else:
                            if width_rest_new > 0 and group_cnt == 1 and param_cnt == 2 and param_idx == 0 and \
                                    abs(param_list[0]['depth'] - param_list[1]['depth']) < 0.01:
                                width_rest_new = min(param_list[0]['width_rest'], param_list[1]['width_rest'])
                                ratio_pre += width_rest_new * 0.5 / rect_width
                            elif width_rest_new > 0 and group_cnt == 2 and param_cnt == 1 and group_idx == 0:
                                ratio_pre += width_rest_new * 0.5 / rect_width
                            elif score_pre < 4 and width_rest_new > 0 and param_idx == 0 and group_idx == 0:
                                ratio_pre += width_rest_new * 0.2 / rect_width
                            ratio_w = ratio_pre + width_delta / rect_width * 0.5
                            ratio_pre = ratio_pre + width_delta / rect_width

                # 补充深度
                angle = rect_angle
                depth = group_depth / 2 + group_regulation[0]
                depth_curtain, depth_back, depth_front = UNIT_DEPTH_CURTAIN, 0, 0
                # 窗帘深度
                if rect_type == UNIT_TYPE_WINDOW:
                    if rect_height - 0.2 < group_height:
                        depth += depth_curtain
                # 背景深度
                elif 'back_depth' in rect_one:
                    depth_back = rect_one['back_depth']
                    group_one['back_depth'] = depth_back
                    depth += depth_back

                # 前面深度
                depth_front = rect_depth - group_depth - group_regulation[0]
                if depth_front > 0:
                    depth_front = min(depth_front, MIN_GROUP_PASS)
                elif depth_front > -0.1 and (rect_type in [UNIT_TYPE_SIDE] or rect_one in rect_door):
                    depth_front = 0
                else:
                    depth_front *= 0.5
                group_regulation[2] = depth_front

                # 纵向位置
                x_delta, y_delta = depth * math.sin(angle), depth * math.cos(angle)
                pp = [p1[0] * (1 - ratio_w) + p2[0] * ratio_w, p1[1] * (1 - ratio_w) + p2[1] * ratio_w]
                po = [pp[0] + x_delta, pp[1] + y_delta]

                # 更新位置
                group_one['position'] = [po[0], group_one['position'][1], po[1]]
                group_one['rotation'] = [0, math.sin(group_angle / 2), 0, math.cos(group_angle / 2)]
                group_one['regulation'] = group_regulation
                # 特别信息
                group_one['vertical'] = 0
                group_one['window'] = window_flag
                group_one['center'] = 0
                group_one['switch'] = 0
                # 区域信息
                group_one['region_direct'] = ratio_dir
                group_one['region_beside'] = [score_pre, score_post]
                group_one['zone'] = group_zone
                # 新增组合
                if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                    group_result.insert(0, group_one)
                else:
                    group_result.append(group_one)
    # 计算布局
    if len(back_todo) > 0 and len(back_point) > 0:
        p1, p2 = [back_point[0], back_point[1]], [back_point[2], back_point[3]]
        ratio_w = 0.5
        for group_idx, group_one in enumerate(back_todo):
            group_width, group_depth = group_one['size'][0], group_one['size'][2]
            delta_depth = (group_depth / 2 + 0.01)
            x_delta, y_delta = delta_depth * math.sin(back_angle), delta_depth * math.cos(back_angle)
            pp = [p1[0] * (1 - ratio_w) + p2[0] * ratio_w, p1[1] * (1 - ratio_w) + p2[1] * ratio_w]
            po = [pp[0] + x_delta, pp[1] + y_delta]
            group_angle = back_angle
            group_width_rest, group_depth_rest = back_width - group_width, back_depth - group_depth
            # 更新位置
            group_one['position'] = [po[0], group_one['position'][1], po[1]]
            group_one['rotation'] = [0, math.sin(group_angle / 2), 0, math.cos(group_angle / 2)]
            group_one['regulation'] = [0, group_width_rest / 2, group_depth_rest, group_width_rest / 2]
            # 特别信息
            group_one['vertical'] = 0
            group_one['window'] = 0
            group_one['center'] = 1
            group_one['switch'] = 0
            # 区域信息
            group_one['region_direct'] = 0
            group_one['region_beside'] = [1, 1]
            # 新增组合
            if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                group_result.insert(0, group_one)
            else:
                group_result.append(group_one)

    # 返回信息
    return group_result


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
    group_add['obj_list'] = []
    return group_add


