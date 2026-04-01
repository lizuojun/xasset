# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-09
@Description: 目标户型导入

"""

from House.house_sample import *
from Furniture.furniture_group_comp import *

# 临时目录
DATA_DIR_IMPORT = os.path.dirname(__file__) + '/temp/'
DATA_DIR_IMPORT_HOUSE = os.path.dirname(__file__) + '/temp/house/'
DATA_DIR_IMPORT_SAMPLE = os.path.dirname(__file__) + '/temp/sample/'
if not os.path.exists(DATA_DIR_IMPORT):
    os.makedirs(DATA_DIR_IMPORT)
if not os.path.exists(DATA_DIR_IMPORT_HOUSE):
    os.makedirs(DATA_DIR_IMPORT_HOUSE)
if not os.path.exists(DATA_DIR_IMPORT_SAMPLE):
    os.makedirs(DATA_DIR_IMPORT_SAMPLE)

# 种子模式
LAYOUT_SEED_TRANSFER = 0  # 迁移布局
LAYOUT_SEED_PROPOSE = 1  # 推荐布局
LAYOUT_SEED_SCHEME = 2  # 方案布局
LAYOUT_SEED_ADJUST = 3  # 调整布局
LAYOUT_SEED_ADVICE = 4  # 参考布局
# 保留数量
LAYOUT_KEEP_COUNT = 3  # 保留数量


# 导入户型 目标产生布局所需数据，包括：户型信息、户型特征、推荐功能区
def import_house(house_id, sample_num=3, sample_id='', sample_idx=-1, seed_mode=LAYOUT_SEED_PROPOSE):
    # 户型信息
    data_id, data_info, feature_info = get_house_data_feature(house_id, reload=True)
    # 纠正房间
    correct_house_data(data_info)
    # 样板信息
    if len(data_info) <= 0:
        layout_info = {}
    else:
        # 指定样板
        if not sample_id == '' or sample_idx >= 0:
            sample_id = import_house_sample_one(sample_id, sample_idx)
        if sample_num <= 0:
            if sample_id == '':
                sample_num = 3
            else:
                sample_num = 1
        # 本身样板
        sample_self = False
        if house_id == sample_id:
            sample_self = True
        # 推荐样板
        layout_info = import_house_detail(data_info, sample_num, sample_id, sample_self, seed_mode)
    # 返回信息
    return data_info, feature_info, layout_info


# 导入户型 目标产生布局所需数据，包括：户型信息、户型特征、推荐功能区
def import_house_by_json(house_json, sample_num=3, sample_id='', sample_idx=-1, seed_mode=LAYOUT_SEED_PROPOSE):
    # 户型信息
    data_id, data_info, feature_info = get_house_data_feature_by_json(house_json)
    if seed_mode <= LAYOUT_SEED_TRANSFER and 'room' in data_info:
        for room_one in data_info['room']:
            room_one['furniture_info'] = []
    # 纠正房间
    correct_house_data(data_info)
    # 样板信息
    if len(data_info) <= 0:
        layout_info = {}
    else:
        # 指定样板
        if not sample_id == '' or sample_idx >= 0:
            sample_id = import_house_sample_one(sample_id, sample_idx)
        if sample_num <= 0:
            if sample_id == '':
                sample_num = 3
            else:
                sample_num = 1
        # 本身样板
        sample_self = False
        if data_id == sample_id:
            sample_self = True
        # 推荐样板
        layout_info = import_house_detail(data_info, sample_num, sample_id, sample_self, seed_mode)
    # 调整样板
    import_house_adjust(data_info, layout_info)

    # 返回信息
    return data_info, feature_info, layout_info


# 导入户型 目标产生布局所需数据，包括：户型信息、户型特征、推荐功能区
def import_house_by_info(house_info, sample_num=3, sample_id='', sample_idx=-1, seed_mode=LAYOUT_SEED_PROPOSE):
    # 户型信息
    data_id, data_info, feature_info = '', house_info, {}
    if 'id' in house_info:
        data_id = house_info['id']
    if seed_mode <= LAYOUT_SEED_TRANSFER and 'room' in data_info:
        for room_one in data_info['room']:
            room_one['furniture_info'] = []
    # 纠正房间
    correct_house_data(data_info)

    # 样板信息
    if len(data_info) <= 0:
        # 解析失败
        layout_info = {}
    else:
        # 指定样板
        if not sample_id == '' or sample_idx >= 0:
            sample_id = import_house_sample_one(sample_id, sample_idx)
        if sample_num <= 0:
            if sample_id == '':
                sample_num = 3
            else:
                sample_num = 1
        # 本身样板
        sample_self = False
        if data_id == sample_id:
            sample_self = True
        # 推荐样板
        layout_info = import_house_detail(data_info, sample_num, sample_id, sample_self, seed_mode)
    # 调整样板
    import_house_adjust(data_info, layout_info)

    # 返回信息
    return data_info, feature_info, layout_info


# 导入户型
def import_house_by_sample(house_info, sample_info, replace_info={}, replace_note={}):
    layout_info = {}
    # 户型信息
    data_info, feature_info = house_info, {}
    if 'room' not in house_info:
        return data_info, feature_info, layout_info
    # 纠正房间
    correct_house_data(data_info)

    # 组合信息
    sample_house, sample_num = '', 1
    for room_id, room_sample in sample_info.items():
        layout_sample = []
        if 'layout_sample' in room_sample and len(room_sample['layout_sample']) > 0:
            layout_sample = room_sample['layout_sample']
        elif 'layout_scheme' in room_sample and len(room_sample['layout_scheme']) > 0:
            layout_sample = room_sample['layout_scheme']
        for sample_old in layout_sample:
            sample_house = 'sample_house'
            if sample_old['source_house'] == 'sample_house':
                sample_house = 'sample_house'
            elif len(sample_old['source_house']) > 0:
                sample_house = 'sample_house_' + sample_old['source_house']
            break
        if not sample_house == '':
            break
    # 清空组合
    if not sample_house == '':
        del_furniture_group(sample_house, '')
        del_sample_layout(sample_house, '')
    # 添加组合
    sample_dict = {}
    for room_id, room_sample in sample_info.items():
        layout_sample = []
        if 'layout_sample' in room_sample and len(room_sample['layout_sample']) > 0:
            layout_sample = room_sample['layout_sample']
        elif 'layout_scheme' in room_sample and len(room_sample['layout_scheme']) > 0:
            layout_sample = room_sample['layout_scheme']
        room_type, room_area = '', 10
        if 'room_type' in room_sample:
            room_type = room_sample['room_type']
        if 'room_area' in room_sample:
            room_area = room_sample['room_area']
        room_area_int = int(room_area)
        room_area_str = str(room_area_int)
        for sample_old in layout_sample:
            sample_old['source_house'] = sample_house
            source_house, source_room = sample_old['source_house'], sample_old['source_room']
            source_group = sample_old['group']
            # 添加布局
            sample_add = add_sample_layout(room_type, room_area_int, sample_old)
            if room_type not in sample_dict:
                sample_dict[room_type] = {}
            if room_area_str not in sample_dict[room_type]:
                sample_dict[room_type][room_area_str] = []
            sample_dict[room_type][room_area_str].append(sample_add)
            # 添加区域 TODO:
            sample_sub_list = []
            source_grp_food, source_grp_work, source_grp_bath, source_grp_wear = [], [], [], []
            for group_one in source_group:
                group_zone = ''
                if 'zone' in group_one:
                    group_zone = group_one['zone']
                if group_zone in ['DiningRoom']:
                    source_grp_food.append(group_one)
                elif group_zone in ['Library']:
                    source_grp_work.append(group_one)
                elif group_zone in ['Bathroom']:
                    source_grp_bath.append(group_one)
                elif group_zone in ['CloakRoom']:
                    source_grp_wear.append(group_one)
            if room_type in ['LivingRoom', 'LivingDiningRoom'] and len(source_grp_food) >= 1:
                source_area, group_area_all, group_area_max = 0, 0, 0
                for group_one in source_grp_food:
                    group_size = group_one['size']
                    group_area = group_size[0] * group_size[2]
                    group_area_all += group_area
                source_area = group_area_all * 2.0
                # 新建方案
                sample_new = sample_old.copy()
                sample_new['type'] = 'DiningRoom'
                sample_new['area'] = source_area
                sample_new['group'] = source_grp_food
                sample_new['group_area'] = group_area_all
                sample_new['source_room_area'] = source_area
                sample_sub_list.append(sample_new)
            if room_type in ['LivingRoom', 'LivingDiningRoom'] and len(source_grp_work) >= 1:
                source_area, group_area_all, group_area_max = 0, 0, 0
                for group_one in source_grp_work:
                    group_size = group_one['size']
                    group_area = group_size[0] * group_size[2]
                    group_area_all += group_area
                source_area = group_area_all * 2.0
                # 新建方案
                sample_new = sample_old.copy()
                sample_new['type'] = 'Library'
                sample_new['area'] = source_area
                sample_new['group'] = source_grp_work
                sample_new['group_area'] = group_area_all
                sample_new['source_room_area'] = source_area
                sample_sub_list.append(sample_new)
            if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom'] and len(source_grp_wear) >= 2:
                source_area, group_area_all, group_area_max = 0, 0, 0
                for group_one in source_grp_wear:
                    group_size = group_one['size']
                    group_area = group_size[0] * group_size[2]
                    group_area_all += group_area
                source_area = group_area_all * 2.0
                # 新建方案
                sample_new = sample_old.copy()
                sample_new['type'] = 'CloakRoom'
                sample_new['area'] = source_area
                sample_new['group'] = source_grp_wear
                sample_new['group_area'] = group_area_all
                sample_new['source_room_area'] = source_area
                sample_sub_list.append(sample_new)
            if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom'] and len(source_grp_bath) >= 1:
                source_area, group_area_all, group_area_max = 0, 0, 0
                for group_one in source_grp_bath:
                    group_size = group_one['size']
                    group_area = group_size[0] * group_size[2]
                    group_area_all += group_area
                    if group_area_max < group_area:
                        group_area_max = group_area
                source_area = group_area_all * 2.0
                if group_area_max > 2:
                    source_area = group_area_max
                # 新建方案
                sample_new = sample_old.copy()
                sample_new['type'] = 'Bathroom'
                sample_new['area'] = source_area
                sample_new['group'] = source_grp_bath
                sample_new['group_area'] = group_area_all
                sample_new['source_room_area'] = source_area
                sample_sub_list.append(sample_new)
            for sample_new in sample_sub_list:
                room_type_new = sample_new['type']
                room_area_int_new = int(sample_new['area'])
                room_area_str_new = str(room_area_int_new)
                sample_add = add_sample_layout(room_type_new, room_area_int_new, sample_new)
                sample_add['source_zone'] = sample_new['type']
                if room_type_new not in sample_dict:
                    sample_dict[room_type_new] = {}
                if room_area_str_new not in sample_dict[room_type_new]:
                    sample_dict[room_type_new][room_area_str_new] = []
                sample_dict[room_type_new][room_area_str_new].append(sample_add)

            # 添加组合
            for group_one in source_group:
                if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
                    add_furniture_group(source_house, source_room, group_one)

    # 房间信息
    room_list, type_have = [], {}
    if 'room' in house_info:
        room_list = house_info['room']
    for room_one in room_list:
        room_type, room_area = '', 0
        if 'type' in room_one:
            room_type = room_one['type']
        if 'area' in room_one:
            room_area = room_one['area']
        # 房间类型
        if room_type not in type_have:
            type_have[room_type] = 0
        type_have[room_type] += 1
        # 通向房间
        next_type = []
        if room_area < 5:
            pass
        room_one['next'] = next_type
    # 卧室大小
    bedroom_min_id, bedroom_max_id = '', ''
    bedroom_min_area, bedroom_max_area = 100, 0
    # 阳台大小
    balcony_min_id, balcony_max_id = '', ''
    balcony_min_area, balcony_max_area = 100, 0
    # 浴室大小
    bathroom_min_id, bathroom_max_id = '', ''
    bathroom_min_area, bathroom_max_area = 100, 0
    # 卧室阳台
    for room_one in room_list:
        room_id, room_type, room_area = room_one['id'], room_one['type'], room_one['area']
        if room_type not in ROOM_TYPE_MAIN:
            continue
        elif int(room_area) <= 0:
            continue
        if room_type in ROOM_TYPE_LEVEL_2:
            if room_area > bedroom_max_area:
                bedroom_max_area = room_area
                bedroom_max_id = room_id
            if room_area < bedroom_min_area:
                bedroom_min_area = room_area
                bedroom_min_id = room_id
        elif room_type in ['Balcony', 'Terrace']:
            if room_area > balcony_max_area:
                balcony_max_area = room_area
                balcony_max_id = room_id
            if room_area < balcony_min_area:
                balcony_min_area = room_area
                balcony_min_id = room_id
        elif room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
            if room_area > bathroom_max_area:
                bathroom_max_area = room_area
                bathroom_max_id = room_id
            if room_area < bathroom_min_area:
                bathroom_min_area = room_area
                bathroom_min_id = room_id

    # 遍历房间
    for room_one in room_list:
        # 房间信息
        room_id, room_type, room_area = room_one['id'], room_one['type'], room_one['area']
        room_style, room_height, room_link = '', UNIT_HEIGHT_WALL, []
        if 'style' in room_one:
            room_style = room_one['style']
        if 'height' in room_one:
            room_height = room_one['height']
        if 'link' in room_one:
            room_link = room_one['link']
        layout_sample = []
        if room_id in sample_info:
            sample_id, sample_room_id, sample_sort = sample_house, room_id, 0
            room_layout = sample_info[room_id]
            sample_list_old, sample_list_new = [], []
            if 'layout_sample' in room_layout and len(room_layout['layout_sample']) > 0:
                sample_list_old = room_layout['layout_sample']
            elif 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
                sample_list_old = room_layout['layout_scheme']
            for sample_old in sample_list_old:
                sample_new = sample_old.copy()
                sample_new['group'] = []
                if 'group' in sample_old:
                    group_list_old = sample_old['group']
                    group_list_new = []
                    for group_old in group_list_old:
                        group_new = copy_group(group_old)
                        group_list_new.append(group_new)
                    sample_new['group'] = group_list_new
                sample_list_new.append(sample_new)
            layout_sample = sample_list_new
        else:
            sample_id, sample_room_id, sample_sort = sample_house, '', 0
            if room_id == bedroom_max_id:
                sample_sort += 1
            if room_id == bedroom_min_id:
                sample_sort -= 1
            if room_id == balcony_max_id:
                sample_sort += 1
            if room_id == balcony_min_id:
                sample_sort -= 1
            if room_id == bathroom_max_id:
                sample_sort += 1
            if room_id == bathroom_min_id:
                sample_sort -= 1
            # 校正儿童房
            if len(sample_id) > 0 and len(sample_info) > 0 and 'Bedroom' in room_type and room_area < 8:
                room_area_min, room_area_max = 100, 0
                for room_key, room_val in sample_info.items():
                    if 'room_type' not in room_val:
                        continue
                    if 'room_area' not in room_val:
                        continue
                    room_type_one, room_area_one = room_val['room_type'], room_val['room_area']
                    if 'Bedroom' in room_type_one:
                        room_area_min = min(room_area_min, room_area_one)
                        room_area_max = max(room_area_max, room_area_one)
                if room_area_min > room_area + 8:
                    room_type = 'KidsRoom'
                    room_one['type'] = room_type
            # 指定样板间
            if len(layout_sample) <= 0 and len(sample_id) > 0 and len(sample_info) > 0:
                layout_sample = unique_room_sample(sample_dict)
                if len(layout_sample) > 0 and 'type' in layout_sample[0]:
                    room_type = layout_sample[0]['type']
            # 匹配样板间
            if len(layout_sample) <= 0 and len(sample_id) > 0 and len(sample_info) > 0:
                layout_sample = assign_room_sample(room_type, room_area, sample_dict, [], [], [],
                                                   sample_num, sample_id, sample_room_id, sample_sort, type_have)
                search_sample = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library',
                                 'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
                if len(layout_sample) <= 0 and ('Bathroom' in room_type or room_type in search_sample):
                    layout_sample = search_room_sample(room_type, room_area, [], [], [],
                                                       sample_num, '', '', sample_sort, type_have)
            # 搜索样板间
            if len(layout_sample) <= 0:
                layout_sample = search_room_sample(room_type, room_area, [], [], [],
                                                   sample_num, sample_id, sample_room_id, sample_sort, type_have)
        # 种子信息
        replace_soft, furniture_list, decorate_list = [], [], []
        if room_id in replace_info:
            replace_dict = replace_info[room_id]
            if 'soft' in replace_dict:
                replace_soft = replace_dict['soft']
        if len(replace_soft) > 0:
            for object_id in replace_soft:
                object_type, object_style, object_size = get_furniture_data(object_id)
                object_one = {
                    'id': object_id,
                    'type': object_type,
                    'style': object_style,
                    'size': object_size,
                    'scale': [1, 1, 1],
                    'position': [0, 0, 0],
                    'rotation': [0, 0, 0, 1],
                    'entityId': ''
                }
                furniture_list.append(object_one)
        decorate_keep = ['build element/beam', 'build element/column', 'obstacle/flue - square']
        if 'decorate_info' in room_one:
            for object_one in room_one['decorate_info']:
                object_type, object_size = object_one['type'], object_one['size']
                object_role = compute_decorate_mesh(object_type, object_size)
                if object_role in ['background']:
                    if min(object_size[0], object_size[2]) < 100:
                        decorate_list.append(object_one)
                    else:
                        decorate_part = compute_decorate_part(object_one, object_role)
                        for decorate_one in decorate_part:
                            decorate_list.append(decorate_one)
                elif object_role in ['cabinet']:
                    if object_type in decorate_keep:
                        decorate_list.append(object_one)
                    elif min(object_size[0], object_size[2]) < 100:
                        decorate_list.append(object_one)
                    else:
                        decorate_part = compute_decorate_part(object_one, object_role)
                        for decorate_one in decorate_part:
                            decorate_list.append(decorate_one)
        # 种子信息
        if len(furniture_list) > 0:
            layout_seed, layout_keep, layout_plus, layout_mesh = compute_room_seed(furniture_list, decorate_list,
                                                                                   '', room_area, replace_note)
        else:
            layout_seed, layout_keep, layout_plus, layout_mesh = compute_room_seed(furniture_list, decorate_list,
                                                                                   '', room_area, replace_note)
            if 'layout_seed' in sample_info:
                layout_seed = sample_info['layout_seed']
            if 'layout_keep' in sample_info:
                layout_keep = sample_info['layout_keep']
            if 'layout_plus' in sample_info:
                layout_plus = sample_info['layout_plus']
        correct_room_seed(layout_seed)
        # 模板信息
        layout_sample = import_room_adjust(layout_sample, layout_seed, layout_keep, room_type, room_area, room_link,
                                           sample_id, sample_room_id, sample_info, seed_mode=LAYOUT_SEED_SCHEME)
        # 返回信息
        layout_info[room_id] = {
            'room_type': room_type,
            'room_style': room_style,
            'room_area': room_area,
            'room_height': room_height,
            'layout_seed': layout_seed,
            'layout_keep': layout_keep,
            'layout_plus': layout_plus,
            'layout_mesh': layout_mesh,
            'layout_sample': layout_sample,
            'layout_scheme': []
        }

    # 调整样板
    import_house_adjust(data_info, layout_info)

    # 返回信息
    return data_info, feature_info, layout_info


# 导入户型
def import_room_by_sample(room_info, sample_info, replace_soft=[], replace_note={}):
    # 样板信息
    layout_sample = []
    if 'layout_sample' in sample_info and len(sample_info['layout_sample']) > 0:
        layout_sample = sample_info['layout_sample']
    elif 'layout_scheme' in sample_info and len(sample_info['layout_scheme']) > 0:
        layout_sample = sample_info['layout_scheme']
    # 组合信息
    sample_house, sample_num = '', 1
    for sample_idx, sample_one in enumerate(layout_sample):
        # 清空组合
        sample_house = 'sample_house'
        if sample_one['source_house'] == 'sample_house':
            sample_house = 'sample_house'
        del_furniture_group(sample_house, '')
        del_sample_layout(sample_house, '')
        # 添加组合
        source_house, source_room = sample_house, sample_one['source_room']
        for group_one in sample_one['group']:
            if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
                correct_room_seed(group_one['obj_list'])
            if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
                add_furniture_group(source_house, source_room, group_one)

    # 房间信息
    room_one = room_info
    room_id, room_type, room_area = room_one['id'], room_one['type'], room_one['area']
    room_style = ''
    if 'style' in room_one:
        room_style = room_one['style']
    room_height, ceil_height = UNIT_HEIGHT_WALL, UNIT_HEIGHT_CEIL
    if 'height' in room_one:
        room_height = room_one['height']

    room_link = []
    if 'link' in room_one:
        room_link = room_one['link']
    sample_room = room_id
    # 纠正信息
    correct_room_data(room_one)
    room_type = room_one['type']
    # 房间信息
    furniture_list, decorate_list = [], []
    for object_key in replace_soft:
        object_type, object_style, object_size = get_furniture_data(object_key)
        object_scale, object_pos, object_rot = [1, 1, 1], [0, 0, 0], [0, 0, 0, 1]
        object_add = {
            'id': object_key,
            'type': object_type,
            'style': object_style,
            'size': object_size,
            'scale': object_scale,
            'position': object_pos,
            'rotation': object_rot,
            'entityId': ''
        }
        if object_key in replace_note:
            object_add = copy_object(replace_note[object_key])
        furniture_list.append(object_add)
    decorate_keep = ['build element/beam', 'build element/column', 'obstacle/flue - square']
    if 'decorate_info' in room_one:
        for object_one in room_one['decorate_info']:
            object_type, object_size = object_one['type'], object_one['size']
            object_role = compute_decorate_mesh(object_type, object_size)
            if object_role in ['background']:
                decorate_list.append(object_one)
            elif object_role in ['cabinet'] and object_type in decorate_keep:
                decorate_list.append(object_one)

    # 种子信息
    if len(furniture_list) > 0:
        layout_seed, layout_keep, layout_plus, layout_mesh = compute_room_seed(furniture_list, decorate_list,
                                                                               room_type, room_area, replace_note)
    else:
        layout_seed, layout_keep, layout_plus, layout_mesh = compute_room_seed(furniture_list, decorate_list,
                                                                               '', room_area, replace_note)
        if 'layout_seed' in sample_info:
            layout_seed = sample_info['layout_seed']
        if 'layout_keep' in sample_info:
            layout_keep = sample_info['layout_keep']
        if 'layout_plus' in sample_info:
            layout_plus = sample_info['layout_plus']
    correct_room_seed(layout_seed)

    # 模板信息
    layout_sample = import_room_adjust(layout_sample, layout_seed, layout_keep, room_type, room_area, room_link,
                                       sample_house, sample_room, {}, seed_mode=LAYOUT_SEED_SCHEME)
    # 返回信息
    layout_info = {
        'room_type': room_type,
        'room_style': room_style,
        'room_area': room_area,
        'room_height': room_height,
        'ceil_height': ceil_height,
        'layout_seed': layout_seed,
        'layout_keep': layout_keep,
        'layout_plus': layout_plus,
        'layout_mesh': layout_mesh,
        'layout_sample': layout_sample,
        'layout_scheme': []
    }
    return layout_info


# 导入户型
def import_room_by_group(room_info, group_list):
    # 房间信息
    room_one = room_info
    room_type, room_style = room_one['type'], ''
    room_area, room_height = room_one['area'], UNIT_HEIGHT_WALL
    if 'style' in room_one:
        room_style = room_one['style']
    if 'height' in room_one:
        room_height = room_one['height']
    room_link = []
    if 'link' in room_one:
        room_link = room_one['link']
    # 纠正信息
    room_one['furniture_info'] = []
    correct_room_data(room_info)
    room_type = room_one['type']

    # 种子信息
    layout_seed, layout_keep, layout_plus, layout_mesh = [], [], [], []

    # 模板信息
    group_list_new, group_area_all = [], 0
    for group_old in group_list:
        group_one = copy_group(group_old)
        group_list_new.append(group_one)
        group_size = group_one['size']
        group_area_all += group_size[0] * group_size[2]
    sample_one = {
        'code': 10000,
        'score': 80,
        'type': room_type,
        'style': 'Other',
        'area': room_area,
        'decorate': {},
        'group': group_list_new,
        'group_area': group_area_all,
        'source_house': 'scene_house',
        'source_room': 'scene_room',
        'source_room_area': room_area
    }
    layout_sample = [sample_one]
    layout_sample = import_room_adjust(layout_sample, layout_seed, layout_keep, room_type, room_area, room_link,
                                       '', '', {}, seed_mode=LAYOUT_SEED_SCHEME)
    # 返回信息
    layout_info = {
        'room_type': room_type,
        'room_style': room_style,
        'room_area': room_area,
        'room_height': room_height,
        'layout_seed': layout_seed,
        'layout_keep': layout_keep,
        'layout_plus': layout_plus,
        'layout_mesh': layout_mesh,
        'layout_sample': layout_sample,
        'layout_scheme': []
    }
    return layout_info


# 导入户型
def import_house_detail(house_info, sample_num=3, sample_id='', sample_self=False, seed_mode=LAYOUT_SEED_PROPOSE):
    # 布局信息
    layout_info = {}
    if len(house_info) <= 0:
        layout_info = {}
        return layout_info

    # 房间信息
    room_list, type_have = [], {}
    if 'room' in house_info:
        room_list = house_info['room']
    for room_one in room_list:
        room_type = room_one['type']
        if room_type not in type_have:
            type_have[room_type] = 0
        type_have[room_type] += 1
    # 卧室大小
    bedroom_min_id, bedroom_max_id = '', ''
    bedroom_min_area, bedroom_max_area = 100, 0
    # 阳台大小
    balcony_min_id, balcony_max_id = '', ''
    balcony_min_area, balcony_max_area = 100, 0
    # 浴室大小
    bathroom_min_id, bathroom_max_id = '', ''
    bathroom_min_area, bathroom_max_area = 100, 0
    if sample_num <= 0:
        sample_num = 1
    # 卧室阳台
    for room_one in room_list:
        room_id, room_type, room_area = room_one['id'], room_one['type'], room_one['area']
        if room_type not in ROOM_TYPE_MAIN:
            continue
        elif int(room_area) <= 0:
            continue
        if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']:
            if room_area > bedroom_max_area:
                bedroom_max_area = room_area
                bedroom_max_id = room_id
            if room_area < bedroom_min_area:
                bedroom_min_area = room_area
                bedroom_min_id = room_id
        elif room_type in ['Balcony', 'Terrace']:
            if room_area > balcony_max_area:
                balcony_max_area = room_area
                balcony_max_id = room_id
            if room_area < balcony_min_area:
                balcony_min_area = room_area
                balcony_min_id = room_id
        elif room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
            if room_area > bathroom_max_area:
                bathroom_max_area = room_area
                bathroom_max_id = room_id
            if room_area < bathroom_min_area:
                bathroom_min_area = room_area
                bathroom_min_id = room_id

    # 遍历房间
    for room_one in house_info['room']:
        # 房间信息
        room_id, room_type, room_area = room_one['id'], room_one['type'], room_one['area']
        room_style = ''
        if 'style' in room_one:
            room_style = room_one['style']
        room_height = UNIT_HEIGHT_WALL
        if 'height' in room_one:
            room_height = room_one['height']
        room_link = []
        if 'link' in room_one:
            room_link = room_one['link']
        # 种子信息
        layout_seed, layout_keep, layout_plus, layout_mesh = [], [], [], []
        if seed_mode in [LAYOUT_SEED_PROPOSE]:
            layout_seed, layout_keep, layout_plus, layout_mesh = import_room_seed(room_one, seed_mode)
            room_type = room_one['type']
        # 调整信息
        sample_room_id, sample_sort = '', 0
        if sample_self:
            sample_room_id = room_id
        else:
            # 特殊情况 客厅升级为客餐厅 客餐厅过小则可以考虑仅作为客厅或餐厅
            if room_type == 'LivingDiningRoom':
                if 'DiningRoom' in type_have:
                    if int(room_area) < 30:
                        room_type = 'LivingRoom'
                elif 'LivingRoom' in type_have:
                    if int(room_area) < 20:
                        room_type = 'DiningRoom'
                else:
                    if int(room_area) > 20:
                        room_type = 'LivingDiningRoom'
                    elif int(room_area) <= 9:
                        room_type = 'DiningRoom'
            elif room_type == 'LivingRoom':
                if 'DiningRoom' in type_have:
                    if room_area >= 30:
                        room_type = 'LivingDiningRoom'
                elif 'LivingRoom' in type_have and type_have['LivingRoom'] >= 2 and int(room_area) <= 5:
                    room_type = 'Hallway'
                elif int(room_area) <= 3:
                    room_type = 'Hallway'
                    type_have['LivingRoom'] -= 1
                elif room_area >= 20:
                    room_type = 'LivingDiningRoom'
            elif room_type == 'DiningRoom':
                if 'LivingRoom' in type_have or 'LivingDiningRoom' in type_have:
                    pass
                else:
                    if int(room_area) <= 9:
                        room_type = 'DiningRoom'
                    else:
                        room_type = 'LivingDiningRoom'
            elif room_area >= 20 and 'LivingDiningRoom' not in type_have:
                if 'LivingRoom' not in type_have and 'DiningRoom' not in type_have:
                    room_type = 'LivingDiningRoom'
            # 布局模板
            sample_sort = 0
            if room_id == bedroom_max_id and room_area > 15:
                sample_sort += 1
            if room_id == bedroom_min_id and room_area < 10:
                sample_sort -= 1
            if room_id == balcony_max_id and room_area > 10:
                sample_sort += 1
            if room_id == balcony_min_id and room_area < 5:
                sample_sort -= 1
            if room_id == bathroom_max_id and room_area > 10:
                sample_sort += 1
            if room_id == bathroom_min_id and room_area < 5:
                sample_sort -= 1

        # 模板信息
        layout_sample = search_room_sample(room_type, room_area, layout_seed, layout_keep, layout_plus,
                                           sample_num, sample_id, sample_room_id, sample_sort, type_have)
        layout_sample = import_room_adjust(layout_sample, layout_seed, layout_keep, room_type, room_area, room_link,
                                           sample_id, sample_room_id)
        layout_info[room_id] = {
            'room_type': room_type,
            'room_style': room_style,
            'room_area': room_area,
            'room_height': room_height,
            'layout_seed': layout_seed,
            'layout_keep': layout_keep,
            'layout_plus': layout_plus,
            'layout_mesh': layout_mesh,
            'layout_sample': layout_sample,
            'layout_scheme': []
        }

    # 返回信息
    return layout_info


# 导入户型
def import_room_detail(room_info, sample_num=3, sample_id='', sample_room_id='', seed_mode=LAYOUT_SEED_PROPOSE):
    # 布局信息
    layout_info = {}
    if sample_num <= 0:
        if sample_id == '':
            sample_num = 3
        else:
            sample_num = 1
    # 房间信息
    room_id, room_type, room_area = room_info['id'], room_info['type'], room_info['area']
    room_mirror = 0
    if 'mirror' in room_info:
        room_mirror = room_info['mirror']
    room_style = ''
    if 'style' in room_info:
        room_style = room_info['style']
    room_height = UNIT_HEIGHT_WALL
    if 'height' in room_info:
        room_height = room_info['height']
    room_link = []
    if 'link' in room_info:
        room_link = room_info['link']

    # 种子信息
    layout_seed, layout_keep, layout_plus, layout_mesh = [], [], [], []
    if seed_mode in [LAYOUT_SEED_PROPOSE]:
        layout_seed, layout_keep, layout_plus, layout_mesh = import_room_seed(room_info, seed_mode)
        room_type = room_info['type']
    # 模板信息
    if seed_mode == LAYOUT_SEED_TRANSFER:
        layout_sample = search_room_sample(room_type, room_area, layout_seed, layout_keep, layout_plus,
                                           sample_num, sample_id, sample_room_id)
        layout_sample = import_room_adjust(layout_sample, layout_seed, layout_keep, room_type, room_area, room_link,
                                           sample_id, sample_room_id)
    elif seed_mode == LAYOUT_SEED_PROPOSE and (len(layout_seed) + len(layout_keep)) >= LAYOUT_KEEP_COUNT:
        layout_sample = search_room_origin(room_type, room_area, room_mirror, layout_seed, layout_keep, layout_plus,
                                           sample_num)
        layout_sample = import_room_adjust(layout_sample, layout_seed, layout_keep, room_type, room_area, room_link,
                                           sample_id, sample_room_id)
    elif seed_mode == LAYOUT_SEED_ADVICE:
        layout_sample = search_room_sample(room_type, room_area, layout_seed, layout_keep, layout_plus,
                                           sample_num, sample_id, sample_room_id)
        layout_sample = import_room_adjust(layout_sample, layout_seed, layout_keep, room_type, room_area, room_link,
                                           sample_id, sample_room_id, {}, seed_mode)
    else:
        layout_sample = search_room_sample(room_type, room_area, layout_seed, layout_keep, layout_plus,
                                           sample_num, sample_id, sample_room_id)
        layout_sample = import_room_adjust(layout_sample, layout_seed, layout_keep, room_type, room_area, room_link,
                                           sample_id, sample_room_id)
    # 参考信息
    if seed_mode in [LAYOUT_SEED_ADVICE]:
        for sample_one in layout_sample:
            sample_one['source_house'] = ''
            sample_one['source_room'] = ''
    # 返回信息
    layout_info = {
        'room_type': room_type,
        'room_style': room_style,
        'room_area': room_area,
        'room_height': room_height,
        'layout_seed': layout_seed,
        'layout_keep': layout_keep,
        'layout_plus': layout_plus,
        'layout_mesh': layout_mesh,
        'layout_sample': layout_sample,
        'layout_scheme': []
    }
    return layout_info


# 导入户型
def import_house_self(house_info, replace_info={}):
    # 布局信息
    layout_info = {}
    if len(house_info) <= 0:
        return layout_info
    # 布局信息
    house_info, layout_info, group_info = extract_house_layout_by_info(house_info)
    for room_id, room_layout in layout_info.items():
        # 房间信息
        room_type, room_area = '', 10
        if 'room_type' in room_layout:
            room_type = room_layout['room_type']
        if 'room_area' in room_layout:
            room_area = room_layout['room_area']
        replace_soft, furniture_list, decorate_list = [], [], []
        if room_id in replace_info:
            replace_dict = replace_info[room_id]
            if 'soft' in replace_dict:
                replace_soft = replace_dict['soft']
        if len(replace_soft) <= 0:
            continue
        for object_id in replace_soft:
            object_type, object_style, object_size = get_furniture_data(object_id)
            object_one = {
                'id': object_id,
                'type': object_type,
                'style': object_style,
                'size': object_size,
                'scale': [1, 1, 1],
                'position': [0, 0, 0],
                'rotation': [0, 0, 0, 1],
                'entityId': ''
            }
            furniture_list.append(object_one)

        # 种子信息
        layout_seed, layout_keep, layout_plus, layout_mesh = compute_room_seed(furniture_list, decorate_list,
                                                                               room_type, room_area)
        # 模板信息
        layout_scheme = []
        if 'layout_scheme' in room_layout:
            layout_scheme = room_layout['layout_scheme']
        import_room_adjust_self(layout_scheme, layout_seed, layout_keep)

        # 更新信息
        room_layout['layout_seed'] = layout_seed
        room_layout['layout_keep'] = layout_keep
        room_layout['layout_plus'] = layout_plus
        room_layout['layout_mesh'] = layout_mesh
    # 返回信息
    return layout_info


# 导入户型
def import_room_self(room_info, replace_soft=[]):
    # 房间信息
    room_type, room_area = '', 0
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    # 布局信息
    layout_info, group_info = extract_room_layout_by_info(room_info)

    # 种子信息
    furniture_list, decorate_list = [], []
    for object_id in replace_soft:
        object_type, object_style, object_size = get_furniture_data(object_id)
        object_one = {
            'id': object_id,
            'type': object_type,
            'style': object_style,
            'size': object_size,
            'scale': [1, 1, 1],
            'position': [0, 0, 0],
            'rotation': [0, 0, 0, 1],
            'entityId': ''
        }
        furniture_list.append(object_one)
    layout_seed, layout_keep, layout_plus, layout_mesh = compute_room_seed(furniture_list, decorate_list,
                                                                           room_type, room_area)
    # 模板信息
    layout_scheme = []
    if 'layout_scheme' in layout_info:
        layout_scheme = layout_info['layout_scheme']
    import_room_adjust_self(layout_scheme, layout_seed, layout_keep)

    # 更新信息
    layout_info['layout_seed'] = layout_seed
    layout_info['layout_keep'] = layout_keep
    layout_info['layout_plus'] = layout_plus
    layout_info['layout_mesh'] = layout_mesh
    # 返回信息
    return layout_info


# 导入户型 启动信息
def import_room_seed(room_info, seed_mode=LAYOUT_SEED_PROPOSE):
    # 纠正信息
    correct_room_data(room_info)
    room_area = room_info['area']
    # 原有信息
    furniture_list, decorate_list = [], []
    if 'furniture_info' in room_info:
        furniture_list = room_info['furniture_info']
    if 'decorate_info' in room_info:
        decorate_list = room_info['decorate_info']
    # 启动信息
    seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list, '', room_area)
    # 纠正类型
    correct_room_type(room_info, seed_list, keep_list)
    room_type = room_info['type']
    # 纠正连通
    correct_room_link(room_info)
    # 启动信息
    for object_set in [seed_list, keep_list]:
        for object_new in object_set:
            object_id = object_new['id']
            object_type, object_style = object_new['type'], object_new['style']
            object_size, object_scale = object_new['size'], object_new['scale']
            object_size_now = [abs(object_size[i] * object_scale[i]) / 100 for i in range(3)]
            object_cate = ''
            object_group, object_role = compute_furniture_role(object_type, object_size_now, room_type, object_id, object_cate)
            if not object_group == object_new['group'] and not object_group == '':
                object_new['group'] = object_group
                object_new['role'] = object_role
    # 吊顶信息
    room_info['ceil_height'] = 0
    room_info['ceil_bottom'] = UNIT_HEIGHT_WALL
    if 'height' in room_info:
        room_info['ceil_bottom'] = room_info['height']
    for object_one in decorate_list:
        # 吊顶
        if 'role' in object_one and object_one['role'] == 'ceiling':
            ceil_height = object_one['size'][1] * object_one['scale'][1] / 100
            ceil_bottom = object_one['position'][1]
            room_info['ceil_height'] = ceil_height
            room_info['ceil_bottom'] = ceil_bottom
            break

    # 返回信息
    return seed_list, keep_list, plus_list, mesh_list


# 导入户型 调整信息
def import_house_adjust(house_info, layout_info):
    if 'room' not in house_info:
        return
    room_list = house_info['room']
    # 提取衣帽间
    cloakroom_dict, bedroom_dict = {}, {}
    for room_id, room_layout in layout_info.items():
        room_type = room_layout['room_type']
        if room_type in ['CloakRoom']:
            if len(room_layout['layout_sample']) <= 0:
                cloakroom_dict[room_id] = ''
            elif len(room_layout['layout_sample'][0]['group']) <= 0:
                cloakroom_dict[room_id] = ''
        if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']:
            bedroom_dict[room_id] = ''
    # 调整衣帽间
    for room_id, room_to in cloakroom_dict.items():
        room_area = 0
        # 查找卧室
        for room_old in room_list:
            if room_old['id'] == room_id:
                if 'area' in room_old:
                    room_area = room_old['area']
                door_list = room_old['door_info']
                for door_old in door_list:
                    if door_old['to'] in bedroom_dict:
                        room_to = door_old['to']
                        cloakroom_dict[room_id] = room_to
                        break
                break
        if room_to == '' and len(bedroom_dict) > 0:
            for bedroom_key, bedroom_val in bedroom_dict.items():
                room_to = bedroom_key
                break
        if room_to in layout_info and room_id in layout_info:
            layout_info[room_id]['layout_sample'] = []
            sample_list = layout_info[room_to]['layout_sample']
            for sample_old in sample_list:
                sample_new = sample_old.copy()
                sample_new['code'], sample_new['decorate'], sample_new['group'] = 0, {}, []
                for group_old in sample_old['group']:
                    if group_old['type'] in ['Armoire', 'Cabinet'] and group_old['size'][1] >= UNIT_HEIGHT_ARMOIRE_MIN:
                        if room_area < 3 and group_old['size'][0] > 1:
                            group_new = get_default_group_layout('cabinet armoire small')
                            sample_new['group'].append(group_new)
                            sample_new['code'] += 10000
                        else:
                            group_new = copy_group(group_old)
                            sample_new['group'].append(group_new)
                            sample_new['code'] += 10000
                if len(sample_new['group']) <= 0:
                    if room_area < 3:
                        group_new = get_default_group_layout('cabinet armoire small')
                        sample_new['group'].append(group_new)
                        sample_new['code'] += 10000
                    else:
                        group_new = get_default_group_layout('cabinet armoire')
                        sample_new['group'].append(group_new)
                        sample_new['code'] += 10000
                if len(sample_new['group']) <= 1:
                    if room_area < 3:
                        group_new = get_default_group_layout('cabinet armoire small')
                        sample_new['group'].append(group_new)
                        sample_new['code'] += 10000
                    else:
                        group_new = get_default_group_layout('cabinet armoire')
                        sample_new['group'].append(group_new)
                        sample_new['code'] += 10000
                layout_info[room_id]['layout_sample'].append(sample_new)
    # 提取盥洗室 TODO:
    pass
    # 调整盥洗室 TODO:
    pass


# 导入户型 调整信息
def import_room_adjust(layout_sample, seed_list, keep_list, room_type='', room_area=10, room_link=[],
                       source_house='', source_room='', source_layout={}, seed_mode=LAYOUT_SEED_PROPOSE):
    # 检查种子
    for sample_one in layout_sample:
        # 初始种子
        group_list = sample_one['group']
        for group_idx, group_one in enumerate(group_list):
            if group_one['type'] not in GROUP_RULE_FUNCTIONAL:
                continue
            if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                continue
            group_one['seed_list'] = []
            group_one['keep_list'] = []
        todo_list = []
        seed_dict, seed_used, keep_dict, keep_used = {}, {}, {}, {}
        for seed_one in seed_list:
            todo_list.append(seed_one)
            seed_dict[seed_one['id']] = seed_one
        for keep_one in keep_list:
            todo_list.append(keep_one)
            keep_dict[keep_one['id']] = keep_one
        # 默认种子
        work_list, rest_list = [], []
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type in GROUP_RULE_FUNCTIONAL:
                if group_type in ['Work']:
                    work_list.append(group_one)
                elif group_type in ['Rest']:
                    rest_list.append(group_one)
            else:
                continue
            group_obj = group_one['obj_main']
            if group_obj in seed_dict:
                pass
            else:
                continue
            seed_id = group_obj
            seed_one = seed_dict[seed_id]
            seed_id, seed_type = seed_one['id'], seed_one['type']
            seed_size = [seed_one['size'][i] * seed_one['scale'][i] / 100 for i in range(3)]
            # 更新信息
            seed_used[seed_id] = 1
            group_one['seed_list'].append(seed_id)
            group_one['seed_size_new'] = [seed_size[i] for i in range(3)]
            group_one['seed_size_old'] = group_one['size'][:]
            # 种子位置
            seed_position, seed_rotation = group_one['position'][:], group_one['rotation'][:]
            if 'scheme' in sample_one['source_house']:
                group_one['seed_position'] = seed_position[:]
                group_one['seed_rotation'] = seed_rotation[:]
            pass
        # 更新种子
        for seed_one in todo_list:
            seed_id, seed_type = seed_one['id'], seed_one['type']
            seed_size = [seed_one['size'][i] * seed_one['scale'][i] / 100 for i in range(3)]
            seed_group, seed_role = seed_one['group'], seed_one['role']
            seed_position, seed_rotation = [0, 0, 0], [0, 0, 0, 1]
            if 'position' in seed_one and 'rotation' in seed_one:
                seed_position, seed_rotation = seed_one['position'][:], seed_one['rotation'][:]
            if seed_id in seed_used:
                continue
            # 确认种子
            repeat_seed, repeat_size = '', [0, 0, 0]
            for group_idx, group_one in enumerate(group_list):
                group_type, group_size, group_size_min = group_one['type'], group_one['size'], group_one['size']
                if group_type not in GROUP_RULE_FUNCTIONAL:
                    continue
                # 种子判断
                main_id = group_one['obj_main']
                main_type, main_style, main_size = get_furniture_data(main_id)
                main_role = GROUP_RULE_FUNCTIONAL[group_type]['main']
                main_cate, main_group_new, main_role_new = compute_furniture_cate_by_id(main_id, main_type)
                if group_type in ['Media']:
                    main_role = 'table'
                if seed_group in ['Work', 'Rest'] and group_type in ['Work', 'Rest']:
                    if min(len(work_list), len(rest_list)) <= 0 < max(len(work_list), len(rest_list)):
                        seed_group = group_type
                if seed_group == group_type and seed_role == main_role:
                    if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                        continue
                    if 'size_min' in group_one:
                        group_size_min = group_one['size_min']
                    group_new, group_old, group_obj_keep, group_obj_chair = {}, {}, [], ''
                    if group_type in ['Dining', 'Work', 'Rest']:
                        for old_one in group_one['obj_list']:
                            old_role = old_one['role']
                            old_size = [old_one['size'][i] * old_one['scale'][i] / 100 for i in range(3)]
                            if old_role in ['chair'] and max(old_size[0], old_size[2]) < 1.0:
                                group_obj_chair = old_one
                                break
                    # 替换
                    if seed_mode == LAYOUT_SEED_ADJUST and seed_type not in ['table/dining set', 'table/dinning set', 'bed/bed set']:
                        pass
                    # 电视柜
                    elif group_type in ['Media']:
                        if group_size[2] < 0.15:
                            group_new = get_default_group_layout('media')
                        elif 'code' in group_one and group_one['code'] == 1000:
                            group_new = get_default_group_layout('media')
                    # 组合
                    elif seed_type in ['table/dining set', 'table/dinning set']:
                        group_new = get_default_group_layout('dining set')
                    elif group_type in ['Dining'] and seed_role in ['table'] and seed_size[2] > seed_size[0] * 0.8 and seed_size[0] > 2.0:
                        group_new = get_default_group_layout('dining set')
                    # 圆桌
                    elif seed_type in ['table/dining table - round'] and max(seed_size[0], seed_size[2]) < min(seed_size[0], seed_size[2]) * 1.2:
                        group_new = get_default_group_layout('dining round')
                        if len(group_obj_chair) > 0:
                            keep_list.append(group_obj_chair)
                            group_obj_keep = [group_obj_chair['id']]
                    # 方桌
                    elif group_type in ['Dining'] and not seed_type == main_type:
                        group_new = get_default_group_layout('dining')
                        if len(group_obj_chair) > 0:
                            keep_list.append(group_obj_chair)
                            group_obj_keep = [group_obj_chair['id']]
                    elif group_type in ['Dining'] and abs(group_size_min[0] - group_size_min[2]) < 0.2 and abs(seed_size[0] - seed_size[2]) > 0.2:
                        group_new = get_default_group_layout('dining')
                        if len(group_obj_chair) > 0:
                            keep_list.append(group_obj_chair)
                            group_obj_keep = [group_obj_chair['id']]
                    elif group_type in ['Dining'] and group_size_min[0] > 2.0 > 1.8 > seed_size[0]:
                        group_new = get_default_group_layout('dining')
                        if len(group_obj_chair) > 0:
                            keep_list.append(group_obj_chair)
                            group_obj_keep = [group_obj_chair['id']]
                    # 组合床
                    elif seed_type in ['bed/bed set']:
                        group_new = get_default_group_layout('bed set')
                    # 儿童床
                    elif group_type in ['Bed'] and seed_size[0] > seed_size[2] and seed_size[1] > UNIT_HEIGHT_SHELF_MIN:
                        group_new = get_default_group_layout('bed kid')
                    # 单人床
                    elif seed_type in ['bed/single bed'] and group_size[0] < seed_size[0]:
                        group_new = get_default_group_layout('bed single')
                    # 衣柜
                    elif group_type in ['Armoire']:
                        if group_size[0] < seed_size[0] - 0.5 or group_size[1] < seed_size[1] - 0.5:
                            group_new = get_default_group_layout('cabinet armoire')
                    # 橱柜
                    elif group_type in ['Cabinet']:
                        if '玄关' in main_cate or '鞋柜' in main_cate:
                            group_new = get_default_group_layout('cabinet door')
                        elif '书柜' in main_cate:
                            group_new = get_default_group_layout('cabinet book')
                        elif '餐边柜' in main_cate:
                            group_new = get_default_group_layout('cabinet dining')
                        elif group_size[0] < seed_size[0] - 0.5 or group_size[1] < seed_size[1] - 0.5:
                            group_new = get_default_group_layout('cabinet tall')
                        elif group_size[1] > seed_size[1] + 0.5:
                            group_new = get_default_group_layout('cabinet short')
                    # 更新分组
                    if len(group_new) > 0:
                        group_new['seed_list'] = []
                        group_new['keep_list'] = group_obj_keep
                        group_list[group_idx] = group_new
                        group_old = group_one
                        group_one = group_new
                    # 更新尺寸
                    group_size, group_size_min = group_one['size'][:], group_one['size_min'][:]
                    if seed_type in ['table/dining set', 'table/dinning set', 'bed/bed set']:
                        group_size = [seed_size[i] for i in range(3)]
                        group_size_min = [seed_size[i] for i in range(3)]
                    elif group_size[0] < seed_size[0] - 0.1 and group_type in ['Rest']:
                        group_size = [seed_size[i] for i in range(3)]
                        group_size_min = [seed_size[i] for i in range(3)]
                    elif group_size[2] < seed_size[2] - 0.1 and group_type in ['Rest']:
                        group_size = [seed_size[i] for i in range(3)]
                        group_size_min = [seed_size[i] for i in range(3)]
                    elif not group_one == group_old and len(group_old) > 0:
                        group_size = [seed_size[i] for i in range(3)]
                        group_size_min = [seed_size[i] for i in range(3)]
                    else:
                        if group_size[0] < seed_size[0] and group_type in ['Armoire', 'Cabinet', 'Appliance']:
                            width_rest = seed_size[0] - group_size[0]
                            group_one['offset'][0] -= width_rest / 2
                            group_one['size_rest'][1] += width_rest / 2
                            group_one['size_rest'][3] += width_rest / 2
                        if group_size[2] < seed_size[2] and group_type in ['Armoire', 'Cabinet', 'Appliance']:
                            depth_rest = seed_size[2] - group_size[2]
                            group_one['offset'][2] -= depth_rest / 2
                            group_one['size_rest'][2] += depth_rest
                            group_size[2] = seed_size[2]
                    # 更新位置
                    if not group_type == 'Media':
                        seed_angle = rot_to_ang(seed_rotation)
                        tmp_x, tmp_z = -group_one['offset'][0], -group_one['offset'][2]
                        add_x = tmp_z * math.sin(seed_angle) + tmp_x * math.cos(seed_angle)
                        add_z = tmp_z * math.cos(seed_angle) - tmp_x * math.sin(seed_angle)
                        seed_position[0] += add_x
                        seed_position[2] += add_z
                    # 更新信息
                    seed_used[seed_id] = 1
                    group_one['seed_list'].append(seed_id)
                    group_one['seed_size_new'] = [seed_size[i] for i in range(3)]
                    group_one['seed_size_old'] = group_one['size'][:]
                    if 'scheme' in sample_one['source_house']:
                        group_one['seed_position'] = seed_position[:]
                        group_one['seed_rotation'] = seed_rotation[:]
                    elif 'target_place' in sample_one and sample_one['target_place'] == 1:
                        group_one['seed_position'] = seed_position[:]
                        group_one['seed_rotation'] = seed_rotation[:]
                    group_one['size'] = group_size[:]
                    group_one['size_min'] = group_size_min[:]
                    if group_type == 'Media':
                        group_one['size_min'] = group_size[:]
                    # 主要家具
                    repeat_seed, repeat_size = group_one['obj_main'], group_size[:]
                    break
                elif seed_group == group_type:
                    if group_type in ['Rest'] and seed_role in ['chair']:
                        group_new = get_default_group_layout('chair rest')
                        if len(group_new) > 0:
                            group_new['seed_list'] = []
                            group_new['keep_list'] = []
                            sample_one['group'][group_idx] = group_new
                            group_one = group_new
                        group_size = [seed_size[i] for i in range(3)]
                        group_size_min = [seed_size[i] for i in range(3)]
                        seed_used[seed_id] = 1
                        group_one['seed_list'].append(seed_id)
                        group_one['seed_size_new'] = [seed_size[i] for i in range(3)]
                        group_one['seed_size_old'] = group_one['size'][:]
                        if 'scheme' in sample_one['source_house']:
                            group_one['seed_position'] = seed_position[:]
                            group_one['seed_rotation'] = seed_rotation[:]
                        elif 'target_place' in sample_one and sample_one['target_place'] == 1:
                            group_one['seed_position'] = seed_position[:]
                            group_one['seed_rotation'] = seed_rotation[:]
                        group_one['size'] = group_size[:]
                        group_one['size_min'] = group_size_min[:]
                        break
                    else:
                        group_one['keep_list'].append(seed_id)
                        if seed_mode == LAYOUT_SEED_PROPOSE and len(seed_list) + len(keep_list) >= LAYOUT_KEEP_COUNT:
                            if seed_id in keep_dict:
                                keep_one = keep_dict[seed_id]
                                if keep_one['role'] == 'table':
                                    group_one['keep_role'] = keep_one['role']
                                    group_one['keep_position'] = keep_one['position'][:]
                                    group_one['keep_rotation'] = keep_one['rotation'][:]
                                elif 'keep_position' not in group_one:
                                    group_one['keep_role'] = keep_one['role']
                                    group_one['keep_position'] = keep_one['position'][:]
                                    group_one['keep_rotation'] = keep_one['rotation'][:]
            # 更新重复
            if seed_id in seed_used and not repeat_seed == '':
                for group_idx in range(len(group_list) - 1, -1, -1):
                    group_one = group_list[group_idx]
                    if not group_one['obj_main'] == repeat_seed:
                        continue
                    if 'seed_list' in group_one and len(group_one['seed_list']) <= 0:
                        group_list.pop(group_idx)
        # 补充种子
        for seed_one in seed_list:
            if seed_mode in [LAYOUT_SEED_TRANSFER, LAYOUT_SEED_ADJUST]:
                break
            seed_id, seed_type = seed_one['id'], seed_one['type']
            seed_size = [seed_one['size'][i] * seed_one['scale'][i] / 100 for i in range(3)]
            seed_group, seed_role = seed_one['group'], seed_one['role']
            seed_position, seed_rotation = seed_one['position'][:], seed_one['rotation'][:]
            if seed_id in seed_used:
                continue
            # 补充桌子
            if 'table' in seed_type or 'chair' in seed_type:
                group_seed = get_default_group_layout_list('table')
            # 补充柜子
            elif 'storage unit' in seed_type or 'cabinet' in seed_type or 'shelf' in seed_type:
                group_seed = get_default_group_layout_list('cabinet')
            # 补充电视
            elif 'media' in seed_type:
                group_seed = get_default_group_layout_list('media')
            # 补充其他
            else:
                group_seed = []
            group_new = {}
            delta_new = 100
            for group_one in group_seed:
                group_type, group_size = group_one['type'], group_one['size']
                if group_type not in GROUP_RULE_FUNCTIONAL:
                    continue
                # 种子品类
                main_role = GROUP_RULE_FUNCTIONAL[group_type]['main']
                if group_type == 'Media':
                    main_role = 'table'
                if seed_group == group_type and seed_role == main_role:
                    delta_cur = abs(group_size[0] - seed_size[0]) + abs(group_size[1] - seed_size[1])
                    if delta_new > delta_cur:
                        group_new = group_one
                        delta_new = delta_cur
            if len(group_new) > 0:
                # 更新分组
                group_list.append(group_new)
                group_one = group_new
                group_one['seed_list'] = []
                group_one['keep_list'] = []
                # 更新尺寸
                group_size, group_size_min = group_one['size'][:], group_one['size_min'][:]
                if seed_type in ['table/dining set', 'table/dinning set', 'bed/bed set']:
                    group_size = [seed_size[i] for i in range(3)]
                    group_size_min = [seed_size[i] for i in range(3)]
                if group_size[0] < seed_size[0]:
                    group_size[0] = seed_size[0]
                if group_size_min[0] < seed_size[0] and group_type in ['Meeting', 'Bed']:
                    group_size_min[0] = seed_size[0]
                if group_size[2] < seed_size[2] and group_type not in ['Meeting', 'Bed']:
                    group_size[2] = seed_size[2]
                # 更新信息
                seed_used[seed_id] = 1
                group_one['seed_list'].append(seed_id)
                group_one['seed_size_new'] = [seed_size[i] for i in range(3)]
                group_one['seed_size_old'] = group_one['size'][:]
                if 'scheme' in sample_one['source_house']:
                    group_one['seed_position'] = seed_position[:]
                    group_one['seed_rotation'] = seed_rotation[:]
                group_one['size'] = group_size[:]
                group_one['size_min'] = group_size_min[:]
                if group_type == 'Media':
                    group_one['size_min'] = group_size[:]
        # 保持种子 迁移模式
        if seed_mode in [LAYOUT_SEED_TRANSFER, LAYOUT_SEED_ADJUST]:
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] in ['Meeting', 'Dining', 'Bed']:
                    if 'seed_list' not in group_one:
                        group_one['seed_list'] = []
                    if len(group_one['seed_list']) <= 0:
                        object_main = group_one['obj_main']
                        if not object_main == '':
                            group_one['seed_list'].append(object_main)
    # 增减分组
    for sample_one in layout_sample:
        # 初始打分 -1代表未标注未评价
        sample_one['score'] = -1
        group_list = sample_one['group']
        for group_one in group_list:
            group_one['position'] = [0, 0, 0]
            group_one['rotation'] = [0, 0, 0, 1]
        group_cnt_func = 0
        # 删除分组
        seed_kid, seed_rest, seed_armoire = False, False, False
        group_shower, group_toilet = {}, {}
        if room_type in ['LivingRoom'] and room_area < 20:
            for group_idx in range(len(group_list) - 1, -1, -1):
                group_one = group_list[group_idx]
                group_type, group_zone, group_size = group_one['type'], '', group_one['size']
                if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                    continue
                if group_type in ['Dining']:
                    if seed_kid and room_area < 15:
                        group_list.pop(group_idx)
        elif room_type in ROOM_TYPE_LEVEL_2:
            for group_idx, group_one in enumerate(group_list):
                if len(seed_list) <= 0 and len(keep_list) <= 0:
                    break
                if group_one['type'] in ['Bed'] and 'seed_size_new' in group_one:
                    seed_size = group_one['seed_size_new']
                    if seed_size[0] > max(seed_size[2], 1.5) and seed_size[1] > UNIT_HEIGHT_SHELF_MIN:
                        seed_kid = True
                elif group_one['type'] in ['Rest'] and 'seed_size_new' in group_one:
                    seed_size = group_one['seed_size_new']
                    if seed_size[0] > 0.5:
                        seed_rest = True
                elif group_one['type'] in ['Armoire', 'Cabinet'] and 'seed_size_new' in group_one:
                    seed_size = group_one['seed_size_new']
                    if seed_size[1] > UNIT_HEIGHT_SHELF_MIN:
                        seed_armoire = True
            for group_idx in range(len(group_list) - 1, -1, -1):
                group_one = group_list[group_idx]
                group_type, group_zone, group_size = group_one['type'], '', group_one['size']
                if 'zone' in group_one:
                    group_zone = group_one['zone']
                if group_type == 'Cabinet' and group_size[1] > UNIT_HEIGHT_ARMOIRE_MIN:
                    group_type = 'Armoire'
                if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                    continue
                if group_type in ['Media']:
                    if seed_kid and room_area < 15:
                        group_list.pop(group_idx)
                elif group_type in ['Armoire']:
                    if 'CloakRoom' in room_link and room_area < 18:
                        group_list.pop(group_idx)
                    elif seed_kid and room_area < 10:
                        group_list.pop(group_idx)
                    elif seed_kid and room_area < 15 and group_size[0] > 1:
                        group_list.pop(group_idx)
                    elif seed_armoire and 'seed_size_new' not in group_one:
                        group_list.pop(group_idx)
                elif group_type in ['Work', 'Rest']:
                    if seed_kid and room_area < 8:
                        group_list.pop(group_idx)
                    elif seed_rest:
                        group_list.pop(group_idx)
                elif group_type in ['Bath', 'Toilet']:
                    group_list.pop(group_idx)
                elif group_zone in ['Bathroom']:
                    group_list.pop(group_idx)
        elif room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
            for group_idx in range(len(group_list) - 1, -1, -1):
                group_one = group_list[group_idx]
                group_type, group_zone, group_size = group_one['type'], '', group_one['size']
                if 'zone' in group_one:
                    group_zone = group_one['zone']
                if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                    continue
                if group_type in ['Bath', 'Toilet']:
                    if len(room_link) >= 2 and 'Bathroom' in room_link:
                        group_list.pop(group_idx)
                    elif group_type in ['Bath']:
                        if len(group_shower) <= 0:
                            group_shower = group_one
                        else:
                            size_old = group_shower['size']
                            if abs(size_old[0] - group_size[0]) + abs(size_old[1] - group_size[1]) <= 0.1:
                                group_list.pop(group_idx)
                    elif group_type in ['Toilet']:
                        if len(group_toilet) <= 0:
                            group_toilet = group_one
                        else:
                            size_old = group_toilet['size']
                            if abs(size_old[0] - group_size[0]) + abs(size_old[1] - group_size[1]) <= 0.1:
                                group_list.pop(group_idx)
                elif group_type in ['Cabinet']:
                    if len(room_link) == 1 and 'Bathroom' in room_link[0] and room_area < 4:
                        group_list.pop(group_idx)
        # 统计分组
        for group_idx, group_one in enumerate(group_list):
            if group_one['type'] in GROUP_RULE_FUNCTIONAL:
                group_cnt_func += 1
        # 增加电视
        if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'ElderlyRoom', 'LivingDiningRoom', 'LivingRoom']:
            find_main, find_media, dump_media = False, False, False
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] in ['Meeting', 'Bed']:
                    find_main = True
                if group_one['type'] in ['Bed'] and group_one['size'][1] > 1.5:
                    dump_media = True
                if group_one['type'] in ['Media']:
                    if group_one['size'][2] < 0.15 and room_area >= 12 and seed_mode in [LAYOUT_SEED_PROPOSE]:
                        sample_one['group'].pop(group_idx)
                        sample_one['code'] -= 10000
                        group_cnt_func -= 1
                        dump_media = True
                        break
                    else:
                        find_media = True
                        break
            if group_cnt_func >= 5 and seed_mode in [LAYOUT_SEED_TRANSFER, LAYOUT_SEED_SCHEME]:
                if room_area < 20 and not dump_media:
                    find_media = True
            if group_cnt_func >= 2 and room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom']:
                if room_area <= 12 and not dump_media:
                    find_media = True
            if group_cnt_func >= 2 and room_type in ['ElderlyRoom']:
                if room_area < 12 and not dump_media:
                    find_media = True
            if find_main and not find_media and not seed_kid:
                default_type = 'media'
                if seed_mode in [LAYOUT_SEED_SCHEME]:
                    default_type = 'tv'
                    if 'Bedroom' in room_type:
                        default_type = 'tv small'
                elif room_area >= 12:
                    default_type = 'media'
                elif room_area >= 6:
                    if len(seed_list) >= 3:
                        default_type = ''
                    elif group_cnt_func >= 4:
                        default_type = ''
                    elif group_cnt_func >= 3:
                        default_type = 'tv small'
                    else:
                        default_type = 'tv small'
                else:
                    default_type = 'tv'
                if not default_type == '':
                    group_layout_new = get_default_group_layout(default_type)
                    if len(group_layout_new) > 0:
                        sample_one['group'].append(group_layout_new)
                        sample_one['code'] += 10000
        # 增加衣柜
        if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom']:
            find_cabinet, cabinet_width = False, 0.5
            if seed_mode in [LAYOUT_SEED_PROPOSE]:
                cabinet_width = 1.2
            for group_idx, group_one in enumerate(group_list):
                if 'CloakRoom' in room_link and room_area <= 15:
                    find_cabinet = True
                    break
                if room_type in ['SecondBedroom', 'Bedroom'] and group_cnt_func >= 3 and room_area <= 10:
                    find_cabinet = True
                    break
                group_type, group_size = group_one['type'], group_one['size']
                if group_type in ['Armoire'] and group_size[1] > UNIT_HEIGHT_ARMOIRE_MIN and group_size[0] > cabinet_width:
                    find_cabinet = True
                    break
                elif group_type in ['Cabinet'] and group_size[1] > UNIT_HEIGHT_ARMOIRE_MIN and group_size[0] > cabinet_width:
                    find_cabinet = True
                    break
            if not find_cabinet and room_area >= 12:
                group_layout_new = get_default_group_layout('cabinet armoire')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
            elif not find_cabinet and room_area >= 6:
                group_layout_new = get_default_group_layout('cabinet armoire small')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        if room_type in ['CloakRoom']:
            if len(group_list) == 1:
                group_layout_new = copy_group(group_list[0])
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 增加卫浴
        if room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
            find_shower, find_toilet, find_cabinet = False, False, False
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] == 'Bath':
                    find_shower = True
                if group_one['type'] == 'Toilet':
                    find_toilet = True
                if group_one['type'] == 'Cabinet':
                    find_cabinet = True
            if len(room_link) >= 2 and 'Bathroom' in room_link:
                find_shower, find_toilet, find_cabinet = True, True, True
            if room_area > 2 and not find_toilet:
                default_type = 'bath toilet'
                group_layout_new = get_default_group_layout(default_type)
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
            if room_area > 4 and not find_shower:
                default_type = 'bath shower'
                group_layout_new = get_default_group_layout(default_type)
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
            if room_area > 4 and not find_cabinet:
                default_type = 'cabinet bath'
                group_layout_new = get_default_group_layout(default_type)
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 增加洗衣机
        if room_type in ['Balcony', 'Terrace', 'LaundryRoom']:
            find_washer, find_table = False, False
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] == 'Appliance':
                    find_washer = True
                if group_one['type'] == 'Rest':
                    find_table = True
            if room_area > 4 and not find_washer and not find_table:
                default_type = 'washer'
                group_layout_new = get_default_group_layout(default_type)
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 增加矮柜
        if seed_kid and room_area >= 8:
            find_cabinet, cabinet_width = False, 0.5
            if seed_mode in [LAYOUT_SEED_PROPOSE]:
                cabinet_width = 1.2
            for group_idx, group_one in enumerate(group_list):
                group_type, group_size = group_one['type'], group_one['size']
                if group_type == 'Cabinet' and group_size[1] < UNIT_HEIGHT_SHELF_MIN:
                    find_cabinet += 1
                    break
            if find_cabinet <= 0:
                group_layout_new = get_default_group_layout('cabinet kid')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 其他模式
        if len(source_layout) <= 0 and seed_mode not in [LAYOUT_SEED_PROPOSE]:
            continue

        # 增加玄关
        if (room_type in ['LivingRoom', 'DiningRoom', 'LivingDiningRoom'] and '' in room_link) or \
                room_type in ['Hallway'] or \
                (room_type in ['Aisle', 'Corridor', 'Stairwell'] and '' in room_link):
            find_cabinet = False
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] in ['Cabinet']:
                    find_cabinet = True
                    break
            if not find_cabinet and room_area >= 6:
                group_layout_new = get_default_group_layout('cabinet door')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 增加餐柜
        if room_type in ['DiningRoom', 'LivingDiningRoom']:
            find_cabinet = False
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] in ['Cabinet']:
                    find_cabinet = True
                    break
            if not find_cabinet and room_area >= 6:
                group_layout_new = get_default_group_layout('cabinet dining')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 增加书柜 TODO:
        if room_type in ['Library']:
            find_cabinet = 0
            for group_idx, group_one in enumerate(group_list):
                group_type, group_size = group_one['type'], group_one['size']
                if group_type in ['Cabinet', 'Armoire']:
                    find_cabinet += 1
                    break
            if (find_cabinet <= 0 and room_area >= 6) or (find_cabinet <= 1 and room_area >= 15):
                group_layout_new = get_default_group_layout('cabinet book')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000

        # 增加浴室柜 洗衣机 TODO:
        if room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
            find_cabinet, find_washer = 0, 0
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] in ['Cabinet']:
                    find_cabinet += 1
                if group_one['type'] in ['Appliance']:
                    find_washer += 1
            if len(room_link) == 1 and 'Bathroom' in room_link[0] and room_area < 4:
                find_cabinet, find_washer = 1, 1
            if find_cabinet <= 0:
                group_layout_new = get_default_group_layout('cabinet bath')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
            if find_washer <= 0 and room_area >= 8:
                default_type = 'washer'
                group_layout_new = get_default_group_layout(default_type)
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000

        # 增加办公桌椅
        if (room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom'] and room_area >= 12) \
                or (room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom'] and 'CloakRoom' in room_link) \
                or (room_type in ['LivingRoom'] and room_area >= 25) \
                or (room_type in ['LivingDiningRoom'] and room_area >= 50):
            find_table = False
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] in ['Work', 'Rest']:
                    find_table = True
                    break
            if not find_table:
                rand_value = random.randint(0, 10)
                group_layout_new = {}
                if room_type in ['LivingRoom', 'LivingDiningRoom']:
                    group_layout_new = get_default_group_layout('table piano')
                else:
                    if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom']:
                        group_layout_new = get_default_group_layout('table dress')
                    else:
                        group_layout_new = get_default_group_layout('table work')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 增加休闲桌椅
        if (room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom'] and room_area >= 25) \
                or (room_type in ['Library'] and room_area >= 15):
            find_table = False
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] in ['Rest']:
                    find_table = True
                    break
            if not find_table:
                group_layout_new = get_default_group_layout('table rest')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 增加钢琴桌椅
        if (room_type in ['LivingRoom'] and room_area >= 25) or (room_type in ['Library'] and room_area >= 25):
            pass

        # 增加儿童家具
        if seed_kid:
            room_type = 'KidsRoom'
        # 增加儿童桌椅
        if room_type in ['KidsRoom'] and room_area >= 5:
            find_table = False
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] == 'Work':
                    find_table = True
                    break
            if not find_table:
                group_layout_new = get_default_group_layout('table kid')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000
        # 增加儿童矮柜
        if room_type in ['KidsRoom']:
            find_cabinet = 0
            for group_idx, group_one in enumerate(group_list):
                if group_one['type'] == 'Cabinet' and group_one['size'][1] < UNIT_HEIGHT_SHELF_MIN:
                    find_cabinet += 1
                    break
            if find_cabinet <= 0:
                group_layout_new = get_default_group_layout('cabinet kid')
                if len(group_layout_new) > 0:
                    sample_one['group'].append(group_layout_new)
                    sample_one['code'] += 10000

    # 补充模板
    if len(layout_sample) <= 0 and room_type in ['Balcony', 'Terrace', 'LaundryRoom']:
        sample_one = {
            'code': 10100,
            'score': -1,
            'type': 0,
            'area': 2,
            'style': 'contemporary',
            'group': [],
            'group_area': 0.29812079567416366,
            'source_house': source_house,
            'source_room': source_room,
            'source_room_area': 2
        }
        group_layout_new = get_default_group_layout('washer')
        sample_one['group'].append(group_layout_new)
        layout_sample.append(sample_one)
    # 返回信息
    return layout_sample


# 导入户型 调整信息
def import_room_adjust_deco(layout_sample, deco_list):
    # 检查饰品
    for sample_one in layout_sample:
        # 初始种子
        for group_one in sample_one['group']:
            group_type = group_one['type']
            if group_type not in GROUP_RULE_DECORATIVE:
                continue
            object_list, object_todo = group_one['obj_list'], []
            for deco_one in deco_list:
                deco_group, deco_role, deco_todo = '', '', []
                if 'group' in deco_one:
                    deco_group = deco_one['group']
                if 'role' in deco_one:
                    deco_role = deco_one['role']
                if not deco_group == group_type:
                    continue
                for object_one in object_list:
                    object_role, object_relate = '', ''
                    if 'role' in object_one:
                        object_role = object_one['role']
                    if 'relate' in object_one:
                        object_relate = object_one['relate']
                    if deco_role == object_role:
                        deco_todo.append(object_one)
                    elif deco_group in ['Wall', 'Ceiling'] and len(object_relate) > 0:
                        deco_todo.append(object_one)
                if len(deco_todo) <= 0:
                    object_add = {
                        'id': deco_one['id'], 'type': deco_one['type'], 'style': deco_one['style'],
                        'size': deco_one['size'][:], 'scale': [1, 1, 1],
                        'position': [0, 0, 0], 'rotation': [0, 0, 0, 1], 'role': deco_role, 'count': 1,
                        'relate': '', 'relate_group': '', 'relate_role': '', 'relate_position': [],
                        'origin_position': [0, 0, 0], 'origin_rotation': [0, 0, 0, 1],
                        'normal_position': [0, 0, 0], 'normal_rotation': [0, 0, 0, 1]
                    }
                    object_todo.append(object_add)
                else:
                    object_add, object_dlt = {}, 10
                    size_new = [abs(deco_one['size'][i] * deco_one['scale'][i]) / 100 for i in range(3)]
                    # 最大
                    deco_max = deco_todo[0]
                    size_max = [abs(deco_max['size'][i] * deco_max['scale'][i]) / 100 for i in range(3)]
                    for deco_old in deco_todo:
                        size_old = [abs(deco_old['size'][i] * deco_old['scale'][i]) / 100 for i in range(3)]
                        if size_old[0] > size_max[0]:
                            deco_max, size_max = deco_old, size_old
                    # 最近
                    for deco_old in deco_todo:
                        size_old = [abs(deco_old['size'][i] * deco_old['scale'][i]) / 100 for i in range(3)]
                        size_dlt = abs(size_new[0] - size_old[0]) + abs(size_new[1] - size_old[1]) + abs(size_new[2] - size_old[2])
                        role_old = deco_old['role']
                        if 'relate_group' in deco_old and deco_old['relate_group'] in ['Meeting', 'Bed']:
                            if role_old == deco_role:
                                if size_old[0] > size_new[0]:
                                    if deco_old == deco_max:
                                        size_dlt *= 0.25
                                    elif abs(size_old[0] - size_max[0]) + abs(size_old[2] - size_max[2]) <= 0.01:
                                        deco_old['id'] = deco_one['id']
                                        deco_old['type'], deco_old['style'] = deco_one['type'], deco_one['style']
                                        deco_old['size'], deco_old['scale'] = deco_one['size'][:], deco_one['scale'][:]
                                        size_dlt *= 0.50
                                    else:
                                        size_dlt *= 0.50
                                else:
                                    size_dlt *= 1.00
                        if size_dlt <= object_dlt:
                            object_add = deco_old
                            object_dlt = size_dlt
                    if len(object_add) > 0:
                        object_add['id'] = deco_one['id']
                        object_add['type'], object_add['style'] = deco_one['type'], deco_one['style']
                        object_add['size'], object_add['scale'] = deco_one['size'][:], deco_one['scale'][:]
                        if 'relate_role' in object_add and object_add['relate_role'] not in ['sofa', 'bed']:
                            object_add['relate'], object_add['relate_group'], object_add['relate_role'] = '', '', ''
                        pass
            for object_add in object_todo:
                object_list.append(object_add)
    # 返回信息
    return layout_sample


# 导入户型 调整信息
def import_room_adjust_self(layout_sample, seed_list, keep_list):
    # 检查种子
    for sample_one in layout_sample:
        group_list = sample_one['group']
        # 初始种子
        for group_one in group_list:
            if group_one['type'] not in GROUP_RULE_FUNCTIONAL:
                continue
            group_one['seed_list'] = []
            group_one['keep_list'] = []
        seed_used, seed_dict, todo_list = {}, {}, []
        for seed_one in seed_list:
            todo_list.append(seed_one)
            seed_dict[seed_one['id']] = seed_one
        for keep_one in keep_list:
            todo_list.append(keep_one)
        # 默认种子
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type not in GROUP_RULE_FUNCTIONAL:
                continue
            group_obj = group_one['obj_main']
            if group_obj not in seed_dict:
                continue
            seed_id = group_obj
            seed_one = seed_dict[seed_id]
            seed_id, seed_type = seed_one['id'], seed_one['type']
            seed_size = [seed_one['size'][i] * seed_one['scale'][i] / 100 for i in range(3)]
            # 更新信息
            seed_used[seed_id] = 1
            group_one['seed_list'].append(seed_id)
            group_one['seed_size_new'] = [seed_size[i] for i in range(3)]
            group_one['seed_size_old'] = group_one['size'][:]
        # 更新种子
        for seed_one in todo_list:
            seed_id, seed_type = seed_one['id'], seed_one['type']
            seed_size = [seed_one['size'][i] * seed_one['scale'][i] / 100 for i in range(3)]
            seed_group, seed_role = seed_one['group'], seed_one['role']
            if seed_id in seed_used:
                continue
            # 确认种子
            repeat_seed, repeat_size = '', [0, 0, 0]
            for group_idx, group_one in enumerate(group_list):
                group_type = group_one['type']
                if group_type not in GROUP_RULE_FUNCTIONAL:
                    continue
                # 种子判断
                main_role = GROUP_RULE_FUNCTIONAL[group_type]['main']
                if group_type == 'Media':
                    main_role = 'table'
                if seed_group == group_type and seed_role == main_role:
                    if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                        continue
                    # 更新尺寸
                    group_size, group_size_min = group_one['size'][:], group_one['size_min'][:]
                    # 更新信息
                    seed_used[seed_id] = 1
                    group_one['seed_list'].append(seed_id)
                    group_one['seed_size_new'] = [seed_size[i] for i in range(3)]
                    group_one['seed_size_old'] = group_one['size'][:]
                    group_one['size'] = group_size[:]
                    group_one['size_min'] = group_size_min[:]
                    if group_type == 'Media':
                        group_one['size_min'] = group_size[:]
                    # 主要家具
                    repeat_seed, repeat_size = group_one['obj_main'], group_size[:]
                    break
                elif seed_group == group_type:
                    # 更新信息
                    group_one['keep_list'].append(seed_id)
            # 更新重复
            if seed_id in seed_used and not repeat_seed == '':
                for group_idx in range(len(group_list) - 1, -1, -1):
                    group_one = group_list[group_idx]
                    if not group_one['obj_main'] == repeat_seed:
                        continue
                    if 'seed_list' in group_one and len(group_one['seed_list']) <= 0:
                        group_list.pop(group_idx)


# 导入样板间
def import_house_sample_oss(house_start=0, house_count=10):
    if house_start < 0:
        return
    if house_count < 0 or house_count > 100:
        return
    house_list = []
    # 列表1
    house_list_1 = list_house_oss(DATA_OSS_HOUSE_FINE)
    if house_start < len(house_list_1):
        house_end = house_start + house_count
        if house_end > len(house_list_1):
            house_end = len(house_list_1)
        for i in range(house_start, house_end):
            house_list.append(house_list_1[i])
    # 列表2
    if house_start + house_count > len(house_list_1):
        house_end = house_start + house_count - len(house_list_1)
        house_start = house_start - len(house_list_1)
        house_list_2 = list_house_oss(DATA_OSS_HOUSE, 0, house_end)
        if house_start < 0:
            house_start = 0
        if house_end > len(house_list_2):
            house_end = len(house_list_2)
        for i in range(house_start, house_end):
            house_list.append(house_list_2[i])
    import_house_sample_list(house_list)


# 导入样板间
def import_house_sample_one(sample_id='', sample_index=0, reload=False):
    if sample_id == '':
        if sample_index < 0:
            return sample_id
        house_list_1 = list_house_oss(DATA_OSS_HOUSE_FINE)
        if sample_index < len(house_list_1):
            sample_id = house_list_1[sample_index]
        else:
            sample_index -= len(house_list_1)
            house_list_2 = list_house_oss(DATA_OSS_HOUSE, sample_index, 1)
            if len(house_list_2) > 0:
                sample_id = house_list_2[0]
    if sample_id == '':
        return
    global FURNITURE_GROUP_DICT
    FURNITURE_GROUP_DICT = load_furniture_group()
    if sample_id in FURNITURE_GROUP_DICT and not reload:
        return sample_id
    extract_house_layout(sample_id, auto_add=1, check_mode=1, print_flag=False)
    return sample_id


# 导入样板间
def import_house_sample_list(house_list):
    # 清除样板
    clear_house_sample()
    clear_furniture_group()
    # 更新样板
    print()
    house_cnt = 0
    for house_id in house_list:
        print('house sample %03d:' % house_cnt, house_id)
        extract_house_layout(house_id, auto_add=1, check_mode=1, print_flag=False)
        house_cnt += 1
    print()
    save_house_sample()
    save_furniture_group()


# 功能测试
if __name__ == '__main__':
    # 户型导入
    house_id = '0d8edd78-6d9b-46c3-b3c9-296d17273da3'
    house_id = '0000ac7d-2b7c-4012-a190-e65bd0c47cdb'
    house_id = '4fe15c9f-0a1c-4521-abba-42745fd40ae8'
    house_id = '355ab8b3-1609-4346-8202-1546938d57f2'
    house_id = '02b7f283-6ccd-4ac8-96b2-4b726a3d19ea'
    house_id = '0000bca3-ef76-4fd5-8b3a-5ed2c0c5d831'
    house_data_info, house_feature_info, house_layout_info = import_house(house_id)
    print('import house:', house_id)
    print(house_data_info)
    print(house_feature_info)
    print(house_layout_info)

