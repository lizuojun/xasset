# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2020-02-20
@Description: 替换家具打组
"""

from Furniture.furniture_group import *

# 部件尺寸
UNIT_HEIGHT_WALL = 2.80
UNIT_HEIGHT_CEIL = 0.15
UNIT_HEIGHT_ARMOIRE_MIN = 1.5
UNIT_HEIGHT_ARMOIRE_MID = 2.0
# 部件尺寸
UNIT_DEPTH_CURTAIN = 0.23
UNIT_DEPTH_FLOOR_FRAME = 0.02


# 调整家具位置
def pre_group_rect_adjust(group_list_src, replace_dict, replace_size, seed_dict,
                          room_type='', room_height=UNIT_HEIGHT_WALL, ceil_height=UNIT_HEIGHT_CEIL):
    group_list_add = []
    # 更新家具
    object_dict_new, relate_dict_new, corner_dict_new = {}, {}, {}
    for group_old in group_list_src:
        # 原有信息
        group_type, group_angle = group_old['type'], rot_to_ang(group_old['rotation'])
        group_width, group_depth = group_old['size'][0], group_old['size'][2]
        seed_list = []
        if 'seed_list' in group_old:
            for seed_id in group_old['seed_list']:
                seed_list.append(seed_id)
        if 'keep_list' in group_old:
            for seed_id in group_old['keep_list']:
                seed_list.append(seed_id)
        main_role = ''
        if group_type in GROUP_RULE_FUNCTIONAL:
            main_role = GROUP_RULE_FUNCTIONAL[group_type]['main']
            if group_type == 'Media':
                main_role = 'table'
            if group_type in ['Rest'] and len(group_old['obj_list']) == 1:
                obj_main = group_old['obj_list'][0]
                if 'role' in obj_main and len(obj_main['role']) > 0:
                    main_role = obj_main['role']
                pass
        vertical_flag, center_flag, corner_flag = 0, 0, 0
        if 'vertical' in group_old:
            vertical_flag = group_old['vertical']
        if 'center' in group_old:
            center_flag = group_old['center']
        region_direct, region_beside = 0, [1, 1]
        if 'region_direct' in group_old:
            region_direct = group_old['region_direct']
        if 'region_beside' in group_old:
            region_beside = group_old['region_beside']
        # 复制信息
        group_new = group_old.copy()
        group_new['obj_list'] = []

        # 替换处理
        for object_one in group_old['obj_list']:
            object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
            object_replace = False
            if object_id in replace_dict:
                object_replace = True
            if len(seed_list) > 0 and not object_replace:
                # 种子查找
                seed_wait, seed_best = [], {}
                if 'entityId' in object_one:
                    entity_id = object_one['entityId']
                    if entity_id in seed_dict:
                        seed_one = seed_dict[entity_id]
                        seed_group, seed_role = seed_one['group'], seed_one['role']
                        if seed_group == group_type and seed_role == object_role:
                            seed_wait.append(seed_one)
                if len(seed_wait) <= 0:
                    for seed_id in seed_list:
                        if seed_id in seed_dict:
                            seed_one = seed_dict[seed_id]
                            seed_group, seed_role = seed_one['group'], seed_one['role']
                            if seed_group == group_type and seed_role == object_role:
                                seed_wait.append(seed_one)
                # 种子查找
                obj_pos = object_one['position']
                for seed_temp in seed_wait:
                    if len(seed_best) <= 0:
                        seed_best = seed_temp
                        continue
                    temp_pos = seed_temp['position']
                    best_pos = seed_best['position']
                    temp_dis = compute_furniture_length(temp_pos[0], temp_pos[2], obj_pos[0], obj_pos[2])
                    best_dis = compute_furniture_length(best_pos[0], best_pos[2], obj_pos[0], obj_pos[2])
                    if temp_dis < best_dis:
                        seed_best = seed_temp
                if len(seed_best) > 0:
                    seed_size, seed_scale = seed_best['size'], seed_best['scale']
                    replace_id = seed_best['id']
                    replace_dict[object_id] = replace_id
                    replace_size[replace_id] = seed_size[:]
        # 缩放处理
        size_main, size_rest = [1, 1, 1], [0, 0, 0, 0]
        if 'size_rest' in group_old:
            size_rest = group_old['size_rest']
        for object_one in group_old['obj_list']:
            object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
            if object_role == main_role:
                size_main = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if object_role in ['accessory', '']:
                continue
            # 家具替换
            replace_id = object_id
            seed_size, seed_scale = object_one['size'], object_one['scale']
            if object_id in replace_dict:
                replace_id = replace_dict[object_id]
                if replace_id not in replace_size:
                    replace_id = object_id
                if replace_id in seed_dict:
                    seed_one = seed_dict[replace_id]
                    seed_size, seed_scale = seed_one['size'], seed_one['scale']
                else:
                    seed_scale = [1, 1, 1]
                seed_height = abs(seed_size[1] * seed_scale[1]) / 100
                if replace_id == object_id:
                    if replace_id in seed_dict:
                        seed_one = seed_dict[replace_id]
                        seed_one['scale'] = object_one['scale'][:]
                if seed_height > room_height - ceil_height:
                    seed_scale[1] = abs(room_height - ceil_height) / seed_height
                elif replace_id in seed_dict:
                    pass
                elif UNIT_HEIGHT_ARMOIRE_MID - 0.05 < seed_height < room_height - ceil_height - 0.05 \
                        and object_role in ['armoire', 'cabinet']:
                    seed_scale[1] = abs(room_height - ceil_height) / seed_height
            # 家具缩放
            if replace_id == object_id or replace_id == '':
                pass
            else:
                size_old = object_one['size'][:]
                size_max = [size_old[i] * 2.0 for i in range(3)]
                size_cur = [size_old[i] * 1.0 for i in range(3)]
                if 'size_max' in object_one:
                    size_max = object_one['size_max']
                if 'size_cur' in object_one:
                    size_cur = object_one['size_cur']
                type_new, style_new = object_one['type'], object_one['style']
                if replace_id in seed_dict:
                    seed_one = seed_dict[replace_id]
                    type_new, style_new, size_new = seed_one['type'], seed_one['style'], seed_one['size'][:]
                elif have_furniture_data(replace_id):
                    type_new, style_new, size_new = get_furniture_data(replace_id)
                elif 'size_cur' in object_one:
                    size_new = object_one['size_cur'][:]
                if replace_id in replace_size:
                    size_new = replace_size[replace_id]
                    # 推荐尺寸纠正
                    if size_new[0] < 0:
                        size_new[0] = object_one['size'][0]
                    if size_new[1] < 0:
                        size_new[1] = object_one['size'][1]
                    if size_new[2] < 0:
                        size_new[2] = object_one['size'][2]
                # 缩放纠正
                scale_new = [1, 1, 1]
                if replace_id in seed_dict:
                    scale_new = seed_scale[:]
                elif object_role == 'rug':
                    scale_new = [size_cur[0] / size_new[0], size_cur[1] / size_new[1],
                                 size_cur[2] / size_new[2]]
                elif group_type == 'Wall':
                    scale_new = [size_cur[0] / size_new[0], size_cur[1] / size_new[1],
                                 size_cur[2] / size_new[2]]
                    scale_min = min(scale_new[0], scale_new[1])
                    scale_new = [scale_min, scale_min, scale_min]
                # 选品信息
                object_new = object_one.copy()
                object_new['id'] = replace_id
                object_new['type'], object_new['style'], object_new['size'] = type_new, style_new, size_new[:]
                object_new['scale'] = scale_new[:]
                if replace_id not in object_dict_new:
                    object_dict_new[replace_id] = object_new
                elif not object_dict_new[replace_id]['role'] == object_role:
                    replace_id_new = replace_id + '_' + object_role
                    object_dict_new[replace_id_new] = object_new
                elif object_dict_new[replace_id]['scale'][0] > scale_new[0]:
                    object_dict_new[replace_id] = object_new

        # 偏移信息
        ratio_max_object, ratio_max_group, ratio_max_space = [0.1, 0.1, 0.1], [0.1, 0.1, 0.1], [0.1, 0.1, 0.1]
        offset_main_x, offset_main_z, offset_main_max = 0, 0, False
        for object_one in group_old['obj_list']:
            # 基本信息
            object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
            object_size_old = [abs(object_one['size'][i] * object_one['scale'][i] / 100) for i in range(3)]
            object_size_new = object_size_old[:]
            replace_id = object_id
            ratio_new_object, ratio_new_group, ratio_new_space = [1, 1, 1], [1, 1, 1], [1, 1, 1]
            if object_id == group_old['obj_main'] and object_role in ['lamp']:
                object_role = main_role
            group_size_old, group_size_max = group_old['size'][:], group_old['size'][:]
            if 'neighbor_base' in group_old:
                group_neighbor = group_old['neighbor_base'][:]
                group_size_max[0] += group_neighbor[1]
                group_size_max[0] += group_neighbor[3]
                group_size_max[2] += group_neighbor[0]
                group_size_max[2] += group_neighbor[2]

            # 替换信息
            if object_id in replace_dict:
                replace_id = replace_dict[object_id]
                if replace_id not in replace_size:
                    replace_id = object_id
            if replace_id in object_dict_new:
                object_new = object_dict_new[replace_id]
                if not object_role == object_dict_new[replace_id]['role']:
                    replace_id_new = replace_id + '_' + object_role
                    if replace_id_new in object_dict_new:
                        object_new = object_dict_new[replace_id_new]
                size_new, scale_new = object_new['size'], object_new['scale']
                object_size_new = [abs(size_new[i] * scale_new[i] / 100) for i in range(3)]
                ratio_new_object = [object_size_new[i] / object_size_old[i] for i in range(3)]
            if object_role == main_role and not object_role == '':
                ratio_new_group = [object_size_new[i] / group_size_old[i] for i in range(3)]
                ratio_new_space = [object_size_new[i] / group_size_max[i] for i in range(3)]

            # 家具偏移 主要家具
            if group_type in GROUP_RULE_FUNCTIONAL and object_role == main_role:
                # 家具比例
                for i in range(3):
                    ratio_max_object[i] = max(ratio_new_object[i], ratio_max_object[i])
                    ratio_max_group[i] = max(ratio_new_group[i], ratio_max_group[i])
                    ratio_max_space[i] = max(ratio_new_space[i], ratio_max_space[i])
                # 餐桌偏移
                if group_type in ['Dining']:
                    # 横向
                    if vertical_flag == 0 and ratio_max_object[0] > 1:
                        if region_direct >= 1:
                            offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                        elif region_direct <= -1:
                            offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                    elif vertical_flag == 1 and ratio_max_object[2] > 1:
                        if region_direct >= 1:
                            offset_main_z = size_main[2] * (1 - ratio_max_object[2]) / 2
                        elif region_direct <= -1:
                            offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                        elif region_beside[0] > 2 > region_beside[1]:
                            offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                        elif region_beside[1] > 2 > region_beside[0]:
                            offset_main_z = size_main[2] * (1 - ratio_max_object[2]) / 2
                    # 纵向
                    if vertical_flag == 0 and ratio_max_object[2] > 1:
                        offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                        if center_flag >= 1 and ratio_max_object[2] > 1.5:
                            offset_main_z = 0
                    elif vertical_flag == 1 and ratio_max_object[0] > 1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                    # 居中
                    if center_flag == 1 and region_direct == 0:
                        if vertical_flag == 0 and ratio_max_group[0] < 1:
                            offset_main_x = 0
                            offset_main_z = 0
                        elif vertical_flag == 1 and ratio_max_group[2] < 1:
                            offset_main_x = 0
                            offset_main_z = 0
                # 电视偏移
                elif group_type in ['Media']:
                    # 横向 靠右
                    if region_direct >= 1 and ratio_max_object[0] >= 1:
                        offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                    # 横向 靠左
                    elif region_direct <= -1 and ratio_max_object[0] >= 1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                    # 纵向
                    offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                # 书桌偏移
                elif group_type in ['Work', 'Rest']:
                    # 横向
                    if region_direct >= 1:
                        offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                        if ratio_max_group[0] >= max(1, ratio_max_object[0]):
                            offset_main_x = group_width * (1 - ratio_max_group[0]) / 2
                    elif region_direct <= -1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                        if ratio_max_group[0] >= max(1, ratio_max_object[0]):
                            offset_main_x = group_width * (ratio_max_group[0] - 1) / 2
                    # 纵向
                    if center_flag == 1:
                        offset_main_z = 0
                        if ratio_max_object[2] > 1:
                            offset_main_z = size_main[2] * (1 - ratio_max_object[2]) / 2
                    elif ratio_max_object[2] > 1:
                        offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                    else:
                        offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                # 柜体偏移
                elif group_type in ['Armoire', 'Cabinet', 'Appliance']:
                    # 横向
                    if region_direct >= 1:
                        offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                        if ratio_max_group[0] >= max(1, ratio_max_object[0]):
                            offset_main_x = group_width * (1 - ratio_max_group[0]) / 2
                    elif region_direct <= -1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                        if ratio_max_group[0] >= max(1, ratio_max_object[0]):
                            offset_main_x = group_width * (ratio_max_group[0] - 1) / 2
                    # 纵向
                    offset_main_z += size_main[2] * (ratio_max_object[2] - 1) / 2
                # 正对偏移
                else:
                    # 横向 靠右
                    if region_direct >= 1 and ratio_max_object[0] >= 1:
                        offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                    # 横向 靠左
                    elif region_direct <= -1 and ratio_max_object[0] >= 1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                    # 纵向
                    offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                # 过大偏移
                if group_type in ['Meeting', 'Bed', 'Dining']:
                    offset_max_x = group_old['size'][0] / 2 - object_size_new[0] / 2 - group_old['offset'][0]
                    offset_min_x = -group_old['size'][0] / 2 + object_size_new[0] / 2 - group_old['offset'][0]
                    offset_max_z = group_old['size'][2] / 2 - object_size_new[2] / 2 - group_old['offset'][2]
                    offset_min_z = -group_old['size'][2] / 2 + object_size_new[2] / 2 - group_old['offset'][2]
                    if group_type == 'Dining':
                        if offset_main_x > offset_max_x or offset_main_x < offset_min_x \
                                and ratio_max_group[0] <= 1:
                            # offset_main_x = -group_old['offset'][0]
                            offset_main_max = True
                        if offset_main_z > offset_max_z or offset_main_z < offset_min_z \
                                and ratio_max_group[2] <= 1:
                            offset_main_max = True
                    elif size_rest[1] + size_rest[3] >= 0.1:
                        if offset_main_x > offset_max_x > 0.1 or offset_main_x < offset_min_x < -0.1:
                            offset_main_x = -group_old['offset'][0]
                            offset_main_max = True
                        if offset_max_x <= 0.1 and offset_min_x >= -0.1:
                            offset_main_x = -group_old['offset'][0]
                            offset_main_max = True
                # 叠加偏移
                elif group_type in ['Armoire', 'Cabinet', 'Work', 'Rest']:
                    group_relate = ''
                    if 'relate' in group_old:
                        group_relate = group_old['relate']
                    if group_relate == object_id:
                        # 横向
                        if region_direct >= 1:
                            offset_main_x = size_main[0] * (1 - ratio_max_object[0]) * 1.5
                            if ratio_max_group[0] >= 1:
                                offset_main_x = group_width * (1 - ratio_max_group[0]) * 1.5
                        elif region_direct <= -1:
                            offset_main_x = size_main[0] * (ratio_max_object[0] - 1) * 1.5
                            if ratio_max_group[0] >= 1:
                                offset_main_x = group_width * (ratio_max_group[0] - 1) * 1.5
                # 卫浴偏移
                elif group_type in ['Bath']:
                    offset_main_x = 0
                # 周边变化
                if 'neighbor_more' in group_new:
                    neighbor_more = group_new['neighbor_more']
                    if offset_main_z * 2 > 0:
                        neighbor_more[2] = max(neighbor_more[2] - offset_main_z * 2, 0)
                    else:
                        neighbor_more[2] = min(neighbor_more[2] - offset_main_z * 2, 3)
                    if ratio_max_object[0] > 1.0:
                        neighbor_more[1] = max(neighbor_more[1] - abs(offset_main_x), 0)
                        neighbor_more[3] = max(neighbor_more[3] - abs(offset_main_x), 0)
            # 家具偏移 次要家具
            if group_type in ['Meeting'] and object_role == 'table' and not offset_main_max:
                if object_size_new[0] > size_main[0]:
                    ratio_new_main = [object_size_new[i] / size_main[i] for i in range(3)]
                    if ratio_new_main[0] > ratio_max_object[0]:
                        ratio_max_object[0] = ratio_new_main[0]
                break
            elif group_type in ['Dining'] and object_role == 'chair' and not offset_main_max:
                # 横向
                if region_direct >= 1 and ratio_new_object[0] > 1:
                    offset_main_x = size_main[0] * (1 - ratio_new_object[0]) / 2
                elif region_direct <= -1 and ratio_new_object[0] > 1:
                    offset_main_x = size_main[0] * (ratio_new_object[0] - 1) / 2
                break
            elif group_type in ['Rest'] and object_role == 'chair' and not offset_main_max:
                # 横向
                if region_direct >= 1 and ratio_new_object[0] > 1:
                    offset_main_x = size_main[0] * (1 - ratio_new_object[0]) / 2
                elif region_direct <= -1 and ratio_new_object[0] > 1:
                    offset_main_x = size_main[0] * (ratio_new_object[0] - 1) / 2
                break
            # 家具偏移 装饰物品
            if group_type in GROUP_RULE_FUNCTIONAL and object_role in ['accessory', '']:
                break
        # 空余信息
        width_rest = [0, 0, 0, 0]
        if 'size_rest' in group_old:
            width_rest = group_old['size_rest'][:]
        if 'neighbor_more' in group_old:
            group_neighbor = group_old['neighbor_more']
            width_rest[1] += group_neighbor[1]
            width_rest[3] += group_neighbor[3]
            if group_type in ['Dining', 'Work', 'Rest']:
                width_rest[0] += group_neighbor[0]
                width_rest[2] += group_neighbor[2]
        elif 'neighbor_base' in group_old:
            group_neighbor = group_old['neighbor_base']
            width_rest[1] += group_neighbor[1]
            width_rest[3] += group_neighbor[3]
            if group_type in ['Dining', 'Work', 'Rest']:
                width_rest[0] += group_neighbor[0]
                width_rest[2] += group_neighbor[2]
        else:
            group_neighbor = [1.0, 1.0, 1.0, 1.0]
            width_rest[1] += group_neighbor[1]
            width_rest[3] += group_neighbor[3]
            if group_type in ['Dining', 'Work', 'Rest']:
                width_rest[0] += group_neighbor[0]
                width_rest[2] += group_neighbor[2]
        # 水平空余
        if 'relate' in group_old and not group_old['relate'] == '':
            if 'neighbor_base' in group_old:
                group_neighbor = group_old['neighbor_base']
                if group_neighbor[1] > 0 and offset_main_x > 0:
                    width_rest[1] += offset_main_x
                    width_rest[3] = 0
                elif group_neighbor[3] > 0 and offset_main_x < 0:
                    width_rest[1] = 0
                    width_rest[3] -= offset_main_x
                else:
                    width_rest[1] = 0
                    width_rest[3] = 0
        elif region_direct == 0 and group_type in GROUP_RULE_FUNCTIONAL:
            if offset_main_x < 0:
                width_rest[1] += offset_main_x
                width_rest[3] -= offset_main_x
            else:
                width_rest[1] += offset_main_x
                width_rest[3] -= offset_main_x
            width_rest[1] += size_main[0] * (1 - ratio_max_object[0]) / 2
            width_rest[3] += size_main[0] * (1 - ratio_max_object[0]) / 2
        # 竖直空余
        if offset_main_z < 0:
            width_rest[0] += offset_main_z
            width_rest[2] -= offset_main_z
        else:
            width_rest[0] += offset_main_z
            width_rest[2] -= offset_main_z
        width_rest[0] += size_main[2] * (1 - ratio_max_object[2]) / 2
        width_rest[2] += size_main[2] * (1 - ratio_max_object[2]) / 2

        # 主要信息
        object_id_main = ''
        object_main_old = {}
        object_type_main_old, object_type_main_new = '', ''
        object_size_main_old, object_size_main_new, object_size_main = [1, 1, 1], [1, 1, 1], [1, 1, 1]
        object_position_main, object_rotation_main = [0, 0, 0], [0, 0, 0, 1]
        object_round_main = False
        object_dump_dict = {}
        # 更新处理
        object_list_old, object_seed_used = [], {}
        for object_idx, object_one in enumerate(group_old['obj_list']):
            if object_one['role'] == 'table' and group_type == 'Media':
                object_list_old.insert(0, object_one)
            else:
                object_list_old.append(object_one)
        for object_idx, object_one in enumerate(object_list_old):
            # 基本信息
            object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
            if have_furniture_data_key(object_id, 'category_id'):
                type_id, style_id, cate_id = get_furniture_data_refer_id(object_id, '', False)
                object_one['category'] = cate_id
            else:
                object_one['category'] = ''
            object_position = object_one['position']
            if object_role == main_role:
                object_main_old = object_one
            # 替换信息
            replace_id = object_id
            if object_id in replace_dict:
                replace_id = replace_dict[object_id]
            if replace_id == '':
                continue
            # 复制信息
            entity_id = ''
            if 'entityId' in object_one:
                entity_id = object_one['entityId']
            object_new = copy_object(object_one)
            object_new['entityId'] = entity_id
            object_turn = get_furniture_turn(replace_id)
            if abs(object_turn) > 0:
                object_new['turn'] = object_turn
            # 尺寸信息
            object_size_old = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_size_new = object_size_old[:]
            object_xz_old = object_size_old[0] / object_size_old[2]
            if replace_id in object_dict_new:
                object_tmp = object_dict_new[replace_id]
                if not object_tmp['role'] == object_role:
                    replace_id_new = replace_id + '_' + object_role
                    if replace_id_new in object_dict_new:
                        object_tmp = object_dict_new[replace_id_new]
                object_new['id'] = object_tmp['id']
                object_new['type'] = object_tmp['type']
                object_new['style'] = object_tmp['style']
                object_new['size'] = object_tmp['size'][:]
                object_new['scale'] = object_tmp['scale'][:]
                if object_new['scale'][0] < 0.99 or object_new['scale'][2] < 0.99:
                    if object_new['role'] not in ['', 'rug', 'accessory']:
                        object_new['fake_size'] = 1
                elif 'fake_size' in object_new:
                    object_new['fake_size'] = 0
            if replace_id in seed_dict:
                seed_tmp = seed_dict[replace_id]
                seed_entity = ''
                if entity_id in seed_dict:
                    seed_tmp = seed_dict[entity_id]
                    if not seed_tmp['id'] == replace_id:
                        seed_tmp = seed_dict[replace_id]
                if 'entityId' in seed_tmp:
                    seed_entity = seed_tmp['entityId']
                object_new['type'] = seed_tmp['type']
                object_new['style'] = seed_tmp['style']
                object_new['size'] = seed_tmp['size'][:]
                object_new['scale'] = seed_tmp['scale'][:]
                object_new['entityId'] = seed_entity
            # 更新信息
            object_size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
            object_xz_new = object_size_new[0] / object_size_new[2]
            # 功能家具
            if group_type in GROUP_RULE_FUNCTIONAL:
                x2, z2 = object_one['position'][0], object_one['position'][2]
                flag_left, flag_back = 0, 0
                if len(object_main_old) > 0:
                    x1, z1 = object_main_old['position'][0], object_main_old['position'][2]
                    flag_left, flag_back = \
                        compute_furniture_locate(x1, z1, x2, z2, group_angle, group_width, group_depth, group_depth * 0.1)
                # 丢弃家具 主要
                if object_role in ['tv'] and size_main[1] * (ratio_max_object[1] - 1) > 0.2:
                    object_dump_dict[object_id] = 1
                    continue
                if object_role == main_role and replace_id in seed_dict:
                    ratio_max_limit_x, ratio_max_limit_z = 1.20, 1.20
                    if group_type in ['Bed']:
                        ratio_max_limit_x, ratio_max_limit_z = 1.40, 1.40
                    elif group_type in ['Media']:
                        ratio_max_limit_x, ratio_max_limit_z = 1.40, 5.00
                    elif group_type in ['Dining', 'Work']:
                        ratio_max_limit_x, ratio_max_limit_z = 1.40, 1.40
                    elif group_type in ['Armoire', 'Cabinet']:
                        ratio_max_limit_x, ratio_max_limit_z = 1.20, 1.40
                    if ratio_max_space[0] > ratio_max_limit_x or ratio_max_space[2] > ratio_max_limit_z:
                        object_dump_dict[object_id] = 1
                        object_id_main = object_id
                        offset_main_x, offset_main_z = 0, 0
                        ratio_max_object = [1, 1, 1]
                        continue
                    elif ratio_max_space[0] > 1.0 and object_size_new[0] > 3:
                        scale_rat = 1
                        if object_role in ['sofa', 'bed'] and object_size_new[0] > 5:
                            scale_rat = max(group_size_max[0], 3) / object_size_new[0]
                        elif object_role in ['table'] and object_size_new[0] > 4:
                            scale_rat = max(group_size_max[0], 3) / object_size_new[0]
                        object_new['scale'][0] *= scale_rat
                        object_new['scale'][1] *= scale_rat
                        object_new['scale'][2] *= scale_rat
                        object_size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                # 丢弃家具 次要
                if object_role in ['side table', 'side plant', 'side lamp']:
                    if replace_id not in seed_dict or replace_id in object_seed_used:
                        if flag_left >= 1 and width_rest[1] < object_size_new[0] - 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                        elif flag_left <= -1 and width_rest[3] < object_size_new[0] - 0.2:
                            object_dump_dict[object_id] = 1
                            continue
                        elif group_type in ['Bed'] and object_size_main[1] > UNIT_HEIGHT_SHELF_MIN:
                            object_dump_dict[object_id] = 1
                            continue
                elif object_role in ['side sofa']:
                    if replace_id in object_seed_used:
                        if object_size_new[0] > object_size_old[0]:
                            object_dump_dict[object_id] = 1
                            continue
                elif object_role in ['chair']:
                    # 丢弃椅子
                    if object_type_main_new in ['table/dining set', 'table/dinning set']:
                        object_dump_dict[object_id] = 1
                        continue
                    elif object_size_main_new[0] * object_size_main_new[2] >= 6 and max(ratio_max_object[0], ratio_max_object[2]) >= 1.5:
                        object_dump_dict[object_id] = 1
                        continue
                    elif object_size_main_new[0] * object_size_main_new[2] >= 4 and ratio_max_object[2] >= 1.5:
                        object_dump_dict[object_id] = 1
                        continue
                    # 丢弃左右
                    if flag_left >= 1 and flag_back == 0:
                        if width_rest[1] < object_size_new[2] / 2 and width_rest[1] < 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                        elif object_size_main[0] > object_size_main[2] * 1.5 and abs(offset_main_x) > 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                    elif flag_left <= -1 and flag_back == 0:
                        if width_rest[3] < object_size_new[2] / 2 and width_rest[3] < 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                        elif object_size_main[0] > object_size_main[2] * 1.5 and abs(offset_main_x) > 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                    # 丢弃前后
                    if flag_back >= 1:
                        if width_rest[0] < object_size_new[2] / 2 and width_rest[0] < 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                    elif flag_back <= -1:
                        if width_rest[2] < object_size_new[2] / 2 and width_rest[2] < 0.1:
                            object_dump_dict[object_id] = 1
                            continue

                # 保持家具
                if 'keep_position' in group_old and replace_id in seed_dict:
                    tmp_x, tmp_y, tmp_z = 0, 0, 0
                # 主要家具
                elif object_role == main_role:
                    tmp_x, tmp_y, tmp_z = offset_main_x, 0, offset_main_z
                    if object_role == 'table' and group_type == 'Media':
                        object_rest = [0, 0, 0, 0]
                        if 'neighbor_base' in group_old:
                            object_rest = group_old['neighbor_base']
                        if ratio_max_group[0] > 1.01 and (region_direct <= -1 or region_beside[1] > 2 > region_beside[0]):
                            offset_pos, normal_pos = group_old['offset'], object_one['normal_position']
                            mov_x = 0 - group_size_old[0] / 2 - object_rest[1] - (offset_pos[0] + normal_pos[0] - object_size_new[0] / 2)
                            tmp_x = mov_x
                        elif ratio_max_group[0] > 1.01 and (region_direct >= 1 or region_beside[0] > 2 > region_beside[1]):
                            offset_pos, normal_pos = group_old['offset'], object_one['normal_position']
                            mov_x = 0 + group_size_old[0] / 2 + object_rest[3] - (offset_pos[0] + normal_pos[0] + object_size_new[0] / 2)
                            tmp_x = mov_x
                elif object_role == 'tv' and group_type == 'Media':
                    offset_side_x, offset_side_z = 0, (object_size_new[2] - object_size_old[2]) / 2
                    tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                # 地毯家具
                elif object_role == 'rug':
                    tmp_x, tmp_y, tmp_z = 0, 0, 0
                # 部件家具
                elif object_role in ['part'] and 'relate' in object_one:
                    relate_id_old = object_one['relate']
                    relate_id_new = ''
                    if relate_id_old in replace_dict:
                        relate_id_new = replace_dict[relate_id_old]
                        if relate_id_new == '':
                            continue
                    # 丢弃配件
                    if relate_id_old == object_id_main and not relate_id_old == relate_id_new:
                        continue
                # 配饰家具
                elif object_role in ['accessory'] and 'relate' in object_one and 'relate_position' in object_one:
                    relate_id_old, relate_position = object_one['relate'], object_one['relate_position']
                    # 丢弃配件
                    if relate_id_old in object_dump_dict:
                        continue
                    elif group_type in ['Dining'] and size_main[1] * (ratio_max_object[1] - 1) > 0.2:
                        continue
                    # 丢弃配件
                    relate_id_new = ''
                    if relate_id_old in replace_dict:
                        relate_id_new = replace_dict[relate_id_old]
                        if relate_id_new == '':
                            continue
                    # 丢弃配件
                    if relate_id_old == object_id_main and not relate_id_old == relate_id_new:
                        if corner_flag >= 1:
                            continue
                        if 'Bath' in room_type and group_type in ['Cabinet']:
                            continue
                    # 保留配件
                    if len(relate_position) > 2:
                        relate_key = relate_id_old + ('_%.2f_%.2f' % (relate_position[0], relate_position[2]))
                        if relate_key not in relate_dict_new:
                            relate_dict_new[relate_key] = {
                                'ratio': [1, 1, 1],
                                'offset': [0, 0, 0],
                                'group': {},
                                'relate_top': UNIT_HEIGHT_SHELF_MIN,
                                'relate_old': {},
                                'relate_new': {},
                                'object_top': [],
                                'object_side': []
                            }
                        if relate_id_new in object_dict_new and 'relate_top' in relate_dict_new[relate_key]:
                            plat_size = object_dict_new[relate_id_new]['size']
                            plat_scale = object_dict_new[relate_id_new]['scale']
                            plat_top = relate_dict_new[relate_key]['relate_top']
                            if plat_size[1] * plat_scale[1] / 100 >= plat_top:
                                continue
                        relate_dict_new[relate_key]['object_top'].append(object_new)
                        group_new['obj_list'].append(object_new)
                        continue
                # 次要家具
                else:
                    if object_role == 'table':
                        offset_side_x = 0
                        offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_main_x + offset_side_x, 0, offset_main_z * 2 + offset_side_z
                        if object_type_main_old in SOFA_CORNER_TYPE_0:
                            if object_type_main_new not in SOFA_CORNER_TYPE_0:
                                if offset_main_z > 0 - 0.2:
                                    tmp_z = offset_side_z + max(0.2, offset_main_z * 2)
                                else:
                                    tmp_z = offset_side_z
                        if corner_flag >= 1 and 'normal_position' in object_one:
                            normal_tmp_x = object_one['normal_position'][0]
                            normal_tmp_z = object_one['normal_position'][2]
                            normal_mov_x = 0.0
                            normal_mov_z = min(offset_main_z * 1.0, 0.3)
                            if object_type_main_new in ["sofa/left corner sofa"]:
                                if normal_tmp_z - (object_size_new[2] * 0.5 + object_size_main[2] * 0.5) < -0.1:
                                    if normal_tmp_x < 0:
                                        normal_mov_x = max(0 - normal_tmp_x * 2, 0 + 0.3)
                                    elif normal_tmp_x < 0 + 0.15:
                                        normal_mov_x = 0 + 0.3 - normal_tmp_x
                            elif object_type_main_new in ["sofa/right corner sofa"]:
                                if normal_tmp_z - (object_size_new[2] * 0.5 + object_size_main[2] * 0.5) < -0.1:
                                    if normal_tmp_x > 0:
                                        normal_mov_x = min(0 - normal_tmp_x * 2, 0 - 0.3)
                                    elif normal_tmp_x > 0 - 0.15:
                                        normal_mov_x = 0 - 0.3 - normal_tmp_x
                            else:
                                normal_mov_x = 0 - normal_tmp_x * 0.5
                            if object_type_main_old in SOFA_CORNER_TYPE_0:
                                if object_type_main_new not in SOFA_CORNER_TYPE_0:
                                    if offset_main_z > 0 - 0.2:
                                        normal_mov_z = max(0.2, offset_main_z * 2)
                            tmp_x = offset_main_x + normal_mov_x
                            tmp_z = offset_side_z + normal_mov_z
                        elif corner_flag <= 0 and 'normal_position' in object_one:
                            normal_tmp_z = object_one['normal_position'][2]
                            normal_mov_z = 0
                            if normal_tmp_z < (object_size_main_new[2] + object_size_new[2]) / 2 + 0.2:
                                normal_mov_z = 0.2
                            tmp_z += normal_mov_z
                    elif object_role == 'side table':
                        offset_side_x = 0
                        offset_side_x += offset_main_x
                        if flag_left >= 1:
                            offset_side_x += size_main[0] * (1 - ratio_max_object[0]) / 2
                            if object_size_new[0] > object_size_old[0]:
                                offset_side_x -= (object_size_new[0] - object_size_old[0]) / 2
                            if replace_id not in seed_dict or replace_id in object_seed_used:
                                if width_rest[1] < -offset_side_x + object_size_new[0] - 0.1:
                                    object_dump_dict[object_id] = 1
                                    continue
                        elif flag_left <= -1:
                            offset_side_x -= size_main[0] * (1 - ratio_max_object[0]) / 2
                            if object_size_new[0] > object_size_old[0]:
                                offset_side_x += (object_size_new[0] - object_size_old[0]) / 2
                            if replace_id not in seed_dict or replace_id in object_seed_used:
                                if width_rest[3] < offset_side_x + object_size_new[0] - 0.2:
                                    object_dump_dict[object_id] = 1
                                    continue
                        offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                    elif object_role == 'side sofa':
                        offset_side_x = 0
                        if flag_left >= 1:
                            offset_side_x -= (object_size_new[2] - object_size_old[2]) / 2
                        elif flag_left <= -1:
                            offset_side_x += (object_size_new[2] - object_size_old[2]) / 2
                        offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_main_x + offset_side_x, 0, offset_main_z * 2 + offset_side_z
                        if object_type_main_old in SOFA_CORNER_TYPE_0:
                            if object_type_main_new not in SOFA_CORNER_TYPE_0:
                                if offset_main_z > 0 - 0.2:
                                    tmp_z = max(0.2, offset_main_z * 2) + offset_side_z
                        if corner_flag >= 1 and 'normal_position' in object_one:
                            normal_tmp_x, normal_mov_x = object_one['normal_position'][0], 0.0
                            if object_type_main_new in ["sofa/left corner sofa"]:
                                if normal_tmp_x < 0 + 0.15:
                                    normal_mov_x = 0 + object_size_main[0] / 2 - normal_tmp_x
                            elif object_type_main_new in ["sofa/right corner sofa"]:
                                if normal_tmp_x > 0 - 0.15:
                                    normal_mov_x = 0 - object_size_main[0] / 2 - normal_tmp_x
                            tmp_x = offset_main_x + offset_side_x + normal_mov_x
                    elif object_role == 'chair':
                        offset_side_x = offset_main_x
                        offset_side_z = offset_main_z
                        if flag_left >= 1:
                            offset_side_x += (object_size_old[0] - object_size_new[0]) / 2
                            if ratio_max_object[0] > 1:
                                offset_side_x -= object_size_main_old[0] * (ratio_max_object[0] - 1) / 2
                        elif flag_left <= -1:
                            offset_side_x -= (object_size_old[0] - object_size_new[0]) / 2
                            if ratio_max_object[0] > 1:
                                offset_side_x += object_size_main_old[0] * (ratio_max_object[0] - 1) / 2
                        if flag_back >= 1:
                            if object_id_main in replace_dict and (not object_round_main) and \
                                    (not replace_dict[object_id_main] == object_id_main):
                                abs_z = abs(object_one['normal_position'][2])
                                fix_z = object_size_main_new[2] * 0.5 + object_size_new[2] * 0.5
                                min_z = 0 - object_size_main_new[2] * 0.5 - width_rest[2] + object_size_new[2] * 0.5
                                offset_side_z += (abs_z - max(fix_z, min_z))
                            elif ratio_max_object[2] > 1:
                                offset_side_z += (object_size_old[2] - object_size_new[2]) / 2
                                offset_side_z -= object_size_main_old[2] * (ratio_max_object[2] - 1)
                        elif flag_back <= -1:
                            if object_id_main in replace_dict and (not object_round_main) \
                                    and (not replace_dict[object_id_main] == object_id_main):
                                abs_z = abs(object_one['normal_position'][2])
                                fix_z = object_size_main_new[2] * 0.5 + object_size_new[2] * 0.5
                                max_z = 0 + object_size_main_new[2] * 0.5 + width_rest[2] - object_size_new[2] * 0.5
                                offset_side_z += (min(fix_z, max_z) - abs_z)
                            elif ratio_max_object[2] > 1:
                                offset_side_z -= (object_size_old[2] - object_size_new[2]) / 2
                                offset_side_z += object_size_main_old[2] * (ratio_max_object[2] - 1)
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                    elif object_role == 'bath':
                        offset_side_x, offset_side_z = 0, 0
                        object_angle_old = rot_to_ang(object_one['normal_rotation'])
                        if abs(object_angle_old - math.pi / 2) < 0.1 or abs(object_angle_old + math.pi / 2) < 0.1:
                            if region_direct >= 1:
                                offset_side_x -= (object_size_new[2] - object_size_old[2]) / 2
                            elif region_direct <= -1:
                                offset_side_x += (object_size_new[2] - object_size_old[2]) / 2
                            offset_side_z = (object_size_new[0] - object_size_old[0]) / 2
                        else:
                            if region_direct >= 1:
                                offset_side_x -= (object_size_new[0] - object_size_old[0]) / 2
                            elif region_direct <= -1:
                                offset_side_x += (object_size_new[0] - object_size_old[0]) / 2
                            offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                    elif object_role == 'screen':
                        offset_side_x, offset_side_z = 0, 0
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                    else:
                        offset_side_x, offset_side_z = 0, 0
                        if flag_left >= 1:
                            offset_side_x += size_main[0] * (1 - ratio_max_object[0]) / 2
                            offset_side_x += (object_size_old[0] - object_size_new[0]) / 2
                        elif flag_left <= -1:
                            offset_side_x -= size_main[0] * (1 - ratio_max_object[0]) / 2
                            offset_side_x -= (object_size_old[0] - object_size_new[0]) / 2
                        offset_side_z -= (object_size_old[2] - object_size_new[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                # 位置信息
                add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                add_y = tmp_y
                add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                object_new['position'][0] += add_x
                object_new['position'][1] += add_y
                object_new['position'][2] += add_z
                if 'normal_position' in object_one:
                    object_new['normal_position'] = object_one['normal_position'][:]
                    object_new['normal_position'][0] += tmp_x
                    object_new['normal_position'][1] += tmp_y
                    object_new['normal_position'][2] += tmp_z
                if 'origin_position' in object_one:
                    object_new['origin_position'] = object_one['origin_position'][:]
                    object_new['origin_position'][0] += add_x
                    object_new['origin_position'][1] += add_y
                    object_new['origin_position'][2] += add_z
                # 位置检查
                if object_role in ['table', 'side sofa'] and group_type in ['Meeting'] and corner_flag >= 1:
                    ang_adjust = 0 - group_angle
                    pos_adjust = [object_new['position'][i] - object_position_main[i] for i in range(3)]
                    pos_z = pos_adjust[2] * math.cos(ang_adjust) - pos_adjust[0] * math.sin(ang_adjust)
                    pos_x = pos_adjust[2] * math.sin(ang_adjust) + pos_adjust[0] * math.cos(ang_adjust)
                    # 调整
                    if object_role == 'table':
                        tmp_x = pos_x
                        tmp_z = pos_z
                        add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                        add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                        object_new['position'][0] = object_position_main[0] + add_x
                        object_new['position'][2] = object_position_main[2] + add_z
                    # 删除
                    elif object_role == 'side sofa':
                        if offset_main_z > 0.4 and object_size_main[2] > 1.4:
                            continue
                # 角度信息
                if object_role in ['table'] and group_type in ['Meeting'] and 'normal_rotation' in object_one:
                    ang_nor = rot_to_ang(object_one['normal_rotation'])
                    if abs(ang_nor) < 0.1 and object_xz_old > 1.1 and object_xz_new < 0.9:
                        ang_new = rot_to_ang(object_new['rotation']) + math.pi / 2
                        object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                    elif abs(ang_nor) > 0.1 and object_xz_new > 0.9:
                        ang_nor = 0
                        ang_new = rot_to_ang(object_rotation_main) + ang_nor
                        object_new['normal_rotation'] = [0, math.sin(ang_nor / 2), 0, math.cos(ang_nor / 2)]
                        object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                        pass
                elif object_role in ['side sofa', 'side table'] and 'normal_position' in object_one:
                    pos_nor, ang_nor = object_one['normal_position'], rot_to_ang(object_new['normal_rotation'])
                    ang_fix = False
                    if pos_nor[0] < 0 - 0.3:
                        if object_role in ['side sofa']:
                            if abs(ang_to_ang(ang_nor + math.pi / 2)) <= math.pi / 4:
                                ang_nor += math.pi
                                ang_fix = True
                            elif abs(ang_to_ang(ang_nor - math.pi / 2)) >= math.pi / 4 and abs(object_xz_old - 1) < 0.2:
                                ang_nor = math.pi / 2
                                ang_fix = True
                        elif object_role in ['side table']:
                            if abs(ang_to_ang(ang_nor)) >= math.pi / 4 and abs(object_xz_old - 1) < 0.2:
                                ang_nor = 0
                                ang_fix = True
                    elif pos_nor[0] > 0 + 0.3:
                        if object_role in ['side sofa']:
                            if abs(ang_to_ang(ang_nor - math.pi / 2)) <= math.pi / 4:
                                ang_nor -= math.pi
                                ang_fix = True
                            elif abs(ang_to_ang(ang_nor + math.pi / 2)) >= math.pi / 4 and abs(object_xz_old - 1) < 0.2:
                                ang_nor = -math.pi / 2
                                ang_fix = True
                        elif object_role in ['side table']:
                            if abs(ang_to_ang(ang_nor)) >= math.pi / 4 and abs(object_xz_old - 1) < 0.2:
                                ang_nor = 0
                                ang_fix = True
                    if ang_fix:
                        ang_new = rot_to_ang(object_rotation_main) + ang_nor
                        object_new['normal_rotation'] = [0, math.sin(ang_nor / 2), 0, math.cos(ang_nor / 2)]
                        object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                elif object_role == 'bath':
                    if region_direct >= 1:
                        pass
                    elif region_direct <= -1:
                        pass
                # 平台信息
                relate_key = object_id + '_%.2f_%.2f' % (object_position[0], object_position[2])
                if object_role in GROUP_RULE_FUNCTIONAL[group_type]['plat']:
                    if relate_key not in relate_dict_new:
                        relate_dict_new[relate_key] = {
                            'ratio': [1, 1, 1],
                            'offset': [0, 0, 0],
                            'group': {},
                            'relate_top': UNIT_HEIGHT_SHELF_MIN,
                            'relate_old': {},
                            'relate_new': {},
                            'object_top': [],
                            'object_side': []
                        }
                if relate_key in relate_dict_new:
                    relate_info = relate_dict_new[relate_key]
                    relate_info['ratio'] = [object_size_new[i] / object_size_old[i] for i in range(3)]
                    relate_info['offset'] = [tmp_x, 0, tmp_z]
                    relate_info['group'] = group_new
                    relate_info['relate_top'] = UNIT_HEIGHT_SHELF_MIN
                    relate_info['relate_old'] = object_one
                    relate_info['relate_new'] = object_new
                    if object_role == 'table' and group_type in ['Media']:
                        if len(group_old['obj_list']) > 0:
                            object_tv = group_old['obj_list'][0]
                            bottom_tv = object_tv['position'][1] - 0.05
                            if object_tv['type'] in ['electronics/TV - on top of others']:
                                bottom_tv += 0.05
                            relate_info['relate_top'] = bottom_tv
                    elif object_role == 'table' and group_type in ['Work', 'Rest']:
                        relate_info['relate_top'] = UNIT_HEIGHT_TABLE_MAX
                # 添加信息
                group_new['obj_list'].append(object_new)
                if replace_id in seed_dict:
                    object_seed_used[replace_id] = 1
                # 错误纠正
                if object_new['type'] in ['table/dining table', 'table/dining table - square', 'table/table']:
                    find_chair = False
                    for object_chair in object_list_old:
                        if 'role' in object_chair and object_chair['role'] in ['chair']:
                            find_chair = True
                            break
                    if object_size_new[0] * 1.2 < object_size_new[2] and find_chair:
                        ang_new = rot_to_ang(object_new['rotation']) + math.pi / 2
                        object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                # 主体信息
                if object_role == main_role:
                    object_id_main = object_id
                    object_type_main_old, object_type_main_new = object_type, object_new['type']
                    object_size_main_old, object_size_main_new = object_size_old[:], object_size_new[:]
                    object_size_main = object_size_new[:]
                    object_position_main = object_new['position'][:]
                    object_rotation_main = object_new['rotation'][:]
                    if group_type == 'Meeting' and group_old['obj_main'] in replace_dict:
                        if object_size_main[2] > object_size_main[0] * 0.6 and 2 <= object_size_main[0] < 3:
                            corner_flag = 1
                        elif object_size_main[2] >= 1.6:
                            corner_flag = 1
                        # 纠错信息
                        if corner_flag == 1:
                            if object_type not in SOFA_CORNER_TYPE_0:
                                corner_flag = 2
                        corner_dict_new[object_new['id']] = corner_flag
                    if abs(object_size_main_old[0] - object_size_main_old[2]) < abs(object_size_main_old[0]) * 0.1:
                        object_round_main = True
            # 装饰家具
            elif group_type in GROUP_RULE_DECORATIVE:
                # 关联关系
                relate_id_old, relate_id_new = '', ''
                relate_width, relate_height, relate_angle = 0, object_one['position'][1] - 0.1, 0
                normal_position, relate_position, relate_vertical, relate_offset = [0, 0, 0], [], 0, [0, 0, 0]
                object_width, object_height = object_size_new[0], object_size_new[1]
                object_angle = rot_to_ang(object_new['rotation'])
                if 'relate' in object_one:
                    relate_id_old = object_one['relate']
                if 'normal_position' in object_one:
                    normal_position = object_one['normal_position']
                if 'relate_position' in object_one:
                    relate_position = object_one['relate_position']
                # 参数计算
                if group_type in ['Wall', 'Ceiling', 'Floor']:
                    # 高度
                    if relate_id_old in replace_dict:
                        relate_id_new = replace_dict[relate_id_old]
                        if relate_id_new in replace_size:
                            relate_height = replace_size[relate_id_new][1] / 100
                    # 偏移
                    if len(relate_id_old) > 0 and len(relate_position) > 2:
                        relate_key = relate_id_old + '_%.2f_%.2f' % (relate_position[0], relate_position[2])
                        if relate_key in relate_dict_new:
                            relate_info = relate_dict_new[relate_key]
                            relate_plat, relate_group = relate_info['relate_new'], relate_info['group']
                            if len(relate_plat) > 0:
                                relate_width, relate_angle = 0, rot_to_ang(relate_plat['rotation'])
                                relate_vertical, relate_offset = 0, relate_info['offset']
                                if 'size' in relate_plat and 'scale' in relate_plat:
                                    relate_width = relate_plat['size'][0] * relate_plat['scale'][0] / 100
                                if 'vertical' in relate_group:
                                    relate_vertical = relate_group['vertical']
                # 墙面装饰
                if group_type == 'Wall':
                    # 高度
                    lift_max, lift_min = room_height - 0.2 - object_height, object_one['position'][1]
                    height_max = room_height - 0.2 - object_one['position'][1]
                    # 删除
                    if len(relate_position) > 2:
                        relate_key = relate_id_old + '_%.2f_%.2f' % (relate_position[0], relate_position[2])
                        relate_new = {}
                        if relate_key in relate_dict_new:
                            relate_new = relate_dict_new[relate_key]['relate_new']
                        if len(relate_new) > 0:
                            relate_id_new = relate_new['id']
                        if relate_id_new == relate_id_old:
                            lift_max = object_new['position'][1]
                        elif len(relate_new) > 0:
                            relate_height_new = abs(relate_new['size'][1] * relate_new['scale'][1] / 100)
                            if room_height - 0.2 - relate_height_new < object_size_new[1] * 0.8:
                                continue
                            else:
                                lift_min = max(lift_min, relate_height_new)
                                height_max = min(height_max, room_height - relate_height_new)
                    # 调整
                    if object_size_new[1] > height_max:
                        height_rat = height_max / object_size_new[1]
                        object_new['scale'][0] *= height_rat
                        object_new['scale'][1] *= height_rat
                    object_y = object_new['position'][1]
                    if object_y < lift_min:
                        object_y = lift_min
                    if object_y > lift_max:
                        object_y = lift_max
                    object_new['position'][1] = object_y
                    # 偏移
                    if len(relate_position) > 2:
                        if relate_vertical == 0:
                            tmp_x, tmp_y, tmp_z = relate_offset[0], 0, 0
                        else:
                            tmp_x, tmp_y, tmp_z = relate_offset[2], 0, 0
                        object_angle = rot_to_ang(object_new['rotation'])
                        add_x = tmp_z * math.sin(object_angle) + tmp_x * math.cos(object_angle)
                        add_y = tmp_y
                        add_z = tmp_z * math.cos(object_angle) - tmp_x * math.sin(object_angle)
                        object_new['position'][0] += add_x
                        object_new['position'][1] += add_y
                        object_new['position'][2] += add_z
                    # 添加
                    group_new['obj_list'].append(object_new)
                    continue
                # 顶面装饰
                elif group_type == 'Ceiling':
                    # 尺寸
                    if object_size_new[1] > object_size_old[1] and object_size_new[1] > room_height * 0.3:
                        height_ratio = room_height * 0.3 / object_size_new[1]
                        object_new['scale'][0] *= height_ratio
                        object_new['scale'][1] *= height_ratio
                        object_new['scale'][2] *= height_ratio
                        object_size_new = [abs(object_size_new[i] * height_ratio) for i in range(3)]
                    # 偏移
                    object_new['position'][1] += (object_size_old[1] - object_size_new[1])
                    if len(relate_position) > 2:
                        tmp_x, tmp_y, tmp_z = relate_offset[0], 0, relate_offset[2]
                        add_x = tmp_z * math.sin(relate_angle) + tmp_x * math.cos(relate_angle)
                        add_y = tmp_y
                        add_z = tmp_z * math.cos(relate_angle) - tmp_x * math.sin(relate_angle)
                        object_new['position'][0] += add_x
                        object_new['position'][1] += add_y
                        object_new['position'][2] += add_z
                    # 添加
                    group_new['obj_list'].append(object_new)
                    continue
                # 地面装饰
                elif group_type == 'Floor' and len(relate_position) > 2:
                    # 标志
                    offset_side_x, offset_side_z, offset_flag = 0, 0, False
                    if len(relate_position) > 2:
                        relate_key = relate_id_old + '_%.2f_%.2f' % (relate_position[0], relate_position[2])
                        relate_new = {}
                        if relate_key not in relate_dict_new:
                            relate_dict_new[relate_key] = {
                                'ratio': [],
                                'offset': [],
                                'group': {},
                                'relate_top': 1,
                                'relate_old': {},
                                'relate_new': {},
                                'object_top': [],
                                'object_side': []
                            }
                        else:
                            relate_new = relate_dict_new[relate_key]['relate_new']
                        # 删除
                        if len(relate_new) > 0:
                            relate_width_dlt = 0
                            if normal_position[0] <= 0 - 0.1:
                                relate_width_dlt = relate_group['neighbor_base'][1]
                            elif normal_position[0] <= 0 + 0.1:
                                relate_width_dlt = relate_group['neighbor_base'][3]
                            if relate_width_dlt < object_size_new[0]:
                                # 删除
                                if relate_width_dlt < 0.1:
                                    continue
                                elif relate_width_dlt < object_size_new[0] * 0.8:
                                    continue
                                # 缩放
                                scale_adjust = relate_width_dlt / object_size_new[0]
                                if object_type in ['electronics/air-conditioner - floor-based', 'lighting/floor lamp']:
                                    scale_adjust = max(scale_adjust, 0.8)
                                object_new['scale'] = [object_new['scale'][i] * scale_adjust for i in range(3)]
                                object_size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                        relate_dict_new[relate_key]['object_side'].append(object_new)
                        # 位置
                        offset_side_x, offset_side_z = 0, 0
                        if object_size_new[2] > object_size_old[2]:
                            offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        offset_flag = True
                    elif object_id in replace_dict:
                        # 位置信息
                        offset_side_x = 0
                        offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        offset_flag = True
                    # 偏移
                    if offset_flag:
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                        add_x = tmp_z * math.sin(object_angle) + tmp_x * math.cos(object_angle)
                        add_y = tmp_y
                        add_z = tmp_z * math.cos(object_angle) - tmp_x * math.sin(object_angle)
                        object_new['position'][0] += add_x
                        object_new['position'][1] += add_y
                        object_new['position'][2] += add_z
                    # 尺寸
                    else:
                        scale_new = [object_one['size_cur'][i] / object_new['size'][i] for i in range(3)]
                        object_new['scale'] = scale_new
                    group_new['obj_list'].append(object_new)
                    continue
                # 窗户装饰
                elif group_type == 'Window':
                    scale_new = [object_size_old[i] * 100 / object_new['size'][i] for i in range(3)]
                    object_new['scale'] = scale_new
                # 其他装饰
                else:
                    scale_new = [object_one['size_cur'][i] / object_new['size'][i] for i in range(3)]
                    object_new['scale'] = scale_new
                scale_new = object_new['scale']
                if 'lamp' in object_new['type']:
                    scale_new_max = max(scale_new[0], scale_new[1], scale_new[2])
                    scale_new_min = min(scale_new[0], scale_new[1], scale_new[2])
                    if scale_new_max > 1.1 or scale_new_min < 0.9:
                        object_new['scale'] = [1, 1, 1]
                # 添加信息
                group_new['obj_list'].append(object_new)
                continue

        # 增加分组
        if object_id_main in object_dump_dict:
            continue
        group_list_add.append(group_new)

    # 更新装饰
    for relate_key, relate_info in relate_dict_new.items():
        if len(relate_info['group']) <= 0:
            continue
        plat_group = relate_info['group']
        plat_ratio = relate_info['ratio']
        plat_offset = relate_info['offset']
        plat_direct = 0
        if 'region_direct' in plat_group:
            plat_direct = plat_group['region_direct']
        plat_old, plat_new = relate_info['relate_old'], relate_info['relate_new']
        plat_size = [plat_old['size'][i] * plat_old['scale'][i] / 100 for i in range(3)]
        plat_size_new = [plat_size[i] * plat_ratio[i] for i in range(3)]
        plat_angle = rot_to_ang(plat_old['rotation'])
        # 顶端配件
        accessory_top_list, accessory_top_dict = relate_info['object_top'], {}
        plat_id_old, plat_id_new = plat_old['id'], plat_new['id']
        if plat_id_new == plat_id_old:
            accessory_list_new = accessory_top_list
        else:
            accessory_list_new, accessory_list_old = compute_accessory_keep(accessory_top_list)
            if 'obj_list' in plat_group:
                accessory_list_obj = plat_group['obj_list']
                for object_old in accessory_list_old:
                    accessory_list_obj.remove(object_old)
        plat_ratio_min = plat_ratio[0]
        if plat_ratio[0] > plat_ratio[2]:
            plat_ratio_min = plat_ratio[2]
        if plat_ratio_min > 1.0:
            plat_ratio_min = 1.0
        plat_ratio_min = (plat_ratio_min + 1) * 0.5
        for object_one in accessory_list_new:
            # 移除
            if plat_new['type'] in PACK_OBJECT_TYPE_0:
                plat_group['obj_list'].remove(object_one)
                continue
            # 缩放
            object_one['scale'][0] *= plat_ratio_min
            object_one['scale'][1] *= plat_ratio_min
            object_one['scale'][2] *= plat_ratio_min
            # 位移
            x1, z1 = plat_old['position'][0], plat_old['position'][2]
            x2, z2 = object_one['position'][0], object_one['position'][2]
            dis, ang = compute_furniture_length(x1, z1, x2, z2)
            offset_x, offset_z = dis * math.sin(ang - plat_angle), dis * math.cos(ang - plat_angle)
            ratio_x, ratio_z = min(plat_ratio[0], 1), min(plat_ratio[2], 1)
            ratio_offset_x, ratio_offset_z = offset_x * ratio_x, offset_z * ratio_z
            if plat_id_new in corner_dict_new:
                ratio_offset_x, ratio_offset_z = offset_x, offset_z
            tmp_x, tmp_z = ratio_offset_x, ratio_offset_z
            # 移除
            limit_x, limit_z = plat_size_new[0] * 0.4, plat_size_new[2] * 0.4
            if plat_id_new in corner_dict_new:
                limit_z = plat_size_new[2] * 0.1
            if (abs(tmp_x) > limit_x + 0.05 or abs(tmp_z) > limit_z + 0.05) and not plat_id_old == plat_id_new:
                plat_group['obj_list'].remove(object_one)
                continue
            # 更新
            add_x = tmp_z * math.sin(plat_angle) + tmp_x * math.cos(plat_angle)
            add_z = tmp_z * math.cos(plat_angle) - tmp_x * math.sin(plat_angle)
            object_one['position'][0] = plat_new['position'][0] + add_x
            object_one['position'][2] = plat_new['position'][2] + add_z
            if 'normal_position' in object_one and 'normal_position' in plat_new:
                object_one['normal_position'][0] = plat_new['normal_position'][0] + tmp_x
                object_one['normal_position'][2] = plat_new['normal_position'][2] + tmp_z
            if 'origin_position' in object_one and 'origin_position' in plat_new:
                object_one['origin_position'][0] = plat_new['origin_position'][0] + add_x
                object_one['origin_position'][2] = plat_new['origin_position'][2] + add_z
            if plat_old['role'] in ['table', 'side table', 'cabinet']:
                if 'pendant light' in object_one['type']:
                    object_y = object_one['position'][1]
                elif plat_old['id'] == plat_new['id'] and abs(plat_ratio[1] - 1.0) < 0.1:
                    object_y = object_one['position'][1]
                else:
                    object_y = plat_new['position'][1] + plat_new['size'][1] * plat_new['scale'][1] / 100
                object_one['position'][1] = object_y
                if 'normal_position' in object_one and 'normal_position' in plat_new:
                    object_one['normal_position'][1] = object_y
                if 'origin_position' in object_one and 'origin_position' in plat_new:
                    object_one['origin_position'][1] = object_y
            object_one['relate'] = plat_new['id']
            object_one['relate_role'] = plat_new['role']
        # 侧边配件
        accessory_side_list = relate_info['object_side']
        for object_one in accessory_side_list:
            x1, z1 = plat_old['position'][0], plat_old['position'][2]
            x2, z2 = object_one['position'][0], object_one['position'][2]
            flag_left, flag_back = compute_furniture_locate(x1, z1, x2, z2, plat_angle, plat_old['size'][0], plat_old['size'][2])
            offset_side_x, offset_side_z = plat_offset[0], 0
            if flag_left >= 1:
                if plat_direct >= 1:
                    offset_side_x += plat_size[0] * (1 - plat_ratio[0]) * 0.5
                elif plat_direct == 0:
                    offset_side_x += plat_size[0] * (1 - plat_ratio[0]) * 0.5
            elif flag_left <= -1:
                if plat_direct <= -1:
                    offset_side_x -= plat_size[0] * (1 - plat_ratio[0]) * 0.5
                elif plat_direct == 0:
                    offset_side_x -= plat_size[0] * (1 - plat_ratio[0]) * 0.5
            tmp_x, tmp_z = offset_side_x, offset_side_z
            add_x = tmp_z * math.sin(plat_angle) + tmp_x * math.cos(plat_angle)
            add_z = tmp_z * math.cos(plat_angle) - tmp_x * math.sin(plat_angle)
            object_one['position'][0] += add_x
            object_one['position'][2] += add_z
            if 'normal_position' in object_one and 'normal_position' in plat_new:
                object_one['normal_position'][0] = plat_new['normal_position'][0] + tmp_x
                object_one['normal_position'][2] = plat_new['normal_position'][2] + tmp_z
            if 'origin_position' in object_one and 'origin_position' in plat_new:
                object_one['origin_position'][0] = plat_new['origin_position'][0] + add_x
                object_one['origin_position'][2] = plat_new['origin_position'][2] + add_z
            if 'lamp' in object_one['type']:
                scale_new = object_one['scale']
                scale_new_max = max(scale_new[0], scale_new[1], scale_new[2])
                scale_new_min = min(scale_new[0], scale_new[1], scale_new[2])
                if scale_new_max > 1.1 or scale_new_min < 0.9:
                    object_one['scale'] = [1, 1, 1]
    # 更新参数
    for group_new in group_list_add:
        compute_group_param(group_new)
    # 返回信息
    return group_list_add


# 判断位置方位
def compute_furniture_locate(x1, z1, x2, z2, angle, width=1.0, depth=1.0, delta=0.1):
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


# 计算家具距离
def compute_furniture_length(x1, y1, x2, y2):
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


# 计算配饰保持
def compute_accessory_keep(accessory_list):
    accessory_keep, accessory_dump = [], []
    accessory_lamp = True
    if accessory_lamp:
        for accessory_one in accessory_list:
            if 'type' in accessory_one and 'lamp' in accessory_one['type']:
                accessory_keep.append(accessory_one)
            else:
                accessory_dump.append(accessory_one)
    else:
        accessory_dict = {}
        for accessory_one in accessory_list:
            accessory_y = str(round(accessory_one['position'][1] + 0.05, 1))
            if accessory_y not in accessory_dict:
                accessory_dict[accessory_y] = []
            accessory_dict[accessory_y].append(accessory_one)

        for accessory_key, accessory_val in accessory_dict.items():
            if len(accessory_val) > len(accessory_keep):
                for accessory_one in accessory_keep:
                    accessory_dump.append(accessory_one)
                accessory_keep = accessory_val
            else:
                for accessory_one in accessory_val:
                    accessory_dump.append(accessory_one)
    return accessory_keep, accessory_dump


# 计算组合参数
def compute_group_param(group_one, keep_size=False):
    group_type, object_list = group_one['type'], group_one['obj_list']
    if group_type not in GROUP_RULE_FUNCTIONAL:
        return
    if len(object_list) <= 0:
        return
    object_info_main, object_move_main = object_list[0], [0, 0, 0]
    object_pos_main = object_info_main['position']
    if 'normal_position' in object_info_main:
        object_move_main = object_info_main['normal_position'][:]
    for object_one in object_list:
        object_one['group'] = group_type
        if 'normal_position' in object_one:
            object_norm_pos = object_one['normal_position']
            object_norm_pos[0] -= object_move_main[0]
            object_norm_pos[2] -= object_move_main[2]
    size_old, offset_old = [0, 0, 0], [0, 0, 0]
    neighbor_base_old, neighbor_more_old = [0, 0, 0, 0], [0, 0, 0, 0]
    neighbor_best_old, neighbor_zone_old = [0, 0, 0, 0], [0, 0, 0, 0]
    if 'size' in group_one:
        size_old = group_one['size'][:]
    if 'offset' in group_one:
        offset_old = group_one['offset'][:]
    if 'neighbor_base' in group_one:
        neighbor_base_old = group_one['neighbor_base']
    if 'neighbor_more' in group_one:
        neighbor_more_old = group_one['neighbor_more']
    if 'neighbor_best' in group_one:
        neighbor_best_old = group_one['neighbor_best']
    if 'neighbor_zone' in group_one:
        neighbor_zone_old = group_one['neighbor_zone']
    # 矩形信息
    if keep_size:
        group_size, group_offset = group_one['size'][:], group_one['offset'][:]
    else:
        group_size, group_offset, furniture_rect = rect_group(group_one)
    # 主要家具 位置旋转
    group_rotation = group_one['rotation'][:]
    group_angle = rot_to_ang(group_rotation)
    offset = [-group_offset[0], -group_offset[1], -group_offset[2]]
    offset_x = offset[2] * math.sin(group_angle) + offset[0] * math.cos(group_angle)
    offset_y = group_offset[1]
    offset_z = offset[2] * math.cos(group_angle) - offset[0] * math.sin(group_angle)
    group_position = [object_pos_main[0] + offset_x,
                      object_pos_main[1] + offset_y,
                      object_pos_main[2] + offset_z]
    neighbor_base_new = [
        (0 - group_offset[2] - group_size[2] / 2) - (0 - offset_old[2] - size_old[2] / 2 - neighbor_base_old[0]),
        (0 - group_offset[0] - group_size[0] / 2) - (0 - offset_old[0] - size_old[0] / 2 - neighbor_base_old[1]),
        (0 - offset_old[2] + size_old[2] / 2 + neighbor_base_old[2]) - (0 - group_offset[2] + group_size[2] / 2),
        (0 - offset_old[0] + size_old[0] / 2 + neighbor_base_old[3]) - (0 - group_offset[0] + group_size[0] / 2)
    ]
    neighbor_more_new = [
        (0 - group_offset[2] - group_size[2] / 2) - (0 - offset_old[2] - size_old[2] / 2 - neighbor_more_old[0]),
        (0 - group_offset[0] - group_size[0] / 2) - (0 - offset_old[0] - size_old[0] / 2 - neighbor_more_old[1]),
        (0 - offset_old[2] + size_old[2] / 2 + neighbor_more_old[2]) - (0 - group_offset[2] + group_size[2] / 2),
        (0 - offset_old[0] + size_old[0] / 2 + neighbor_more_old[3]) - (0 - group_offset[0] + group_size[0] / 2)
    ]
    neighbor_best_new = [
        (0 - group_offset[2] - group_size[2] / 2) - (0 - offset_old[2] - size_old[2] / 2 - neighbor_best_old[0]),
        (0 - group_offset[0] - group_size[0] / 2) - (0 - offset_old[0] - size_old[0] / 2 - neighbor_best_old[1]),
        (0 - offset_old[2] + size_old[2] / 2 + neighbor_best_old[2]) - (0 - group_offset[2] + group_size[2] / 2),
        (0 - offset_old[0] + size_old[0] / 2 + neighbor_best_old[3]) - (0 - group_offset[0] + group_size[0] / 2)
    ]
    neighbor_zone_new = [
        (0 - group_offset[2] - group_size[2] / 2) - (0 - offset_old[2] - size_old[2] / 2 - neighbor_zone_old[0]),
        (0 - group_offset[0] - group_size[0] / 2) - (0 - offset_old[0] - size_old[0] / 2 - neighbor_zone_old[1]),
        (0 - offset_old[2] + size_old[2] / 2 + neighbor_zone_old[2]) - (0 - group_offset[2] + group_size[2] / 2),
        (0 - offset_old[0] + size_old[0] / 2 + neighbor_zone_old[3]) - (0 - group_offset[0] + group_size[0] / 2)
    ]
    # 尺寸信息
    object_one = group_one['obj_list'][0]
    object_id, object_type = object_one['id'], object_one['type']
    origin_size, origin_scale = object_one['size'], object_one['scale']
    object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
    # 剩余信息
    width_rest1 = group_offset[0] - object_size[0] / 2 + group_size[0] / 2
    width_rest2 = group_size[0] / 2 - group_offset[0] - object_size[0] / 2
    depth_rest1 = group_offset[2] - object_size[2] / 2 + group_size[2] / 2
    depth_rest2 = group_size[2] / 2 - group_offset[2] - object_size[2] / 2
    # 更新信息
    group_one['size'] = group_size
    group_one['offset'] = group_offset
    group_one['position'] = group_position
    group_one['rotation'] = group_rotation
    group_one['size_min'] = object_size
    group_one['size_rest'] = [depth_rest1, width_rest1, depth_rest2, width_rest2]
    group_one['obj_main'] = object_id
    group_one['obj_type'] = object_type
    if 'neighbor_base' in group_one:
        group_one['neighbor_base'] = neighbor_base_new
    if 'neighbor_more' in group_one:
        group_one['neighbor_more'] = neighbor_more_new
    if 'neighbor_best' in group_one:
        group_one['neighbor_best'] = neighbor_best_new
    if 'neighbor_zone' in group_one:
        group_one['neighbor_zone'] = neighbor_zone_new


# 功能测试
if __name__ == '__main__':
    pass
