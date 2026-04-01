# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-10-24
@Description: 智能布局服务 支持多数项目的链路调试

"""

import time
import socket
import traceback

from layout_def import *
from layout_service_log import *
from layout_sample_analyze import *

from House.house_scene_build import *
from House.house_scene_render import *

from ImportHouse.room_search import *
from HouseSearch.house_propose import get_sample_key, check_sample_group
from HouseSearch.house_search_main import house_search_get_sample_info
from LayoutRecord.layout_record import *
from LayoutCustomized.customized_layout import layout_house_customized

# 临时目录
DATA_DIR_SERVER_GROUP = os.path.dirname(__file__) + '/temp/group/'
if not os.path.exists(DATA_DIR_SERVER_GROUP):
    os.makedirs(DATA_DIR_SERVER_GROUP)
# 设计目录
DATA_DIR_RECORD = os.path.dirname(__file__) + '/LayoutRecord/'
if not os.path.exists(DATA_DIR_RECORD):
    os.makedirs(DATA_DIR_RECORD)

# 布局服务计数
LAYOUT_SAMPLE_CNT = 0
LAYOUT_SAMPLE_LOC = ''

# 家具推荐环境
SAMPLE_PROPOSE_ENV = ''
SAMPLE_PROPOSE_URL = ''
# 家具推荐服务 预发
SAMPLE_PROPOSE_PRE = 'https://tuipre.taobao.com/recommend'
SAMPLE_PROPOSE_SID_PRE = 39552
SAMPLE_PROPOSE_USR_ID_PRE = 2206486991823
# 家具推荐服务 线上
SAMPLE_PROPOSE_PRO = 'https://tui.alibaba-inc.com/recommend'
SAMPLE_PROPOSE_SID_PRO = 39552
SAMPLE_PROPOSE_APP_ID_PRO = 22614
SAMPLE_PROPOSE_USR_ID_PRO = 999999999
# 家具推荐服务 原有
SAMPLE_PROPOSE_OLD = 'https://tui.alibaba-inc.com/recommend'
SAMPLE_PROPOSE_SID_OLD = 39552
SAMPLE_PROPOSE_APP_ID_OLD = 22614
SAMPLE_PROPOSE_USR_ID_OLD = 999999999

# 布局机位房间
LAYOUT_VIEW_ROOM_TYPE = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library',
                         'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                         'MasterBathroom', 'SecondBathroom', 'Bathroom', 'Kitchen']


# 全屋布局方案
def layout_sample_house(house_info, sample_info, replace_info={}, replace_note={}, layout_num=3, style_mode='',
                        deco_mode=2, view_mode=0, path_mode=-1, clear_mode=0):
    # 户型信息
    house_id = ''
    if 'id' in house_info:
        house_id = house_info['id']
    # 方案信息
    for room_key, room_sample in sample_info.items():
        layout_sample = []
        if 'layout_sample' in room_sample and len(room_sample['layout_sample']) > 0:
            layout_sample = room_sample['layout_sample']
        elif 'layout_scheme' in room_sample and len(room_sample['layout_scheme']) > 0:
            layout_sample = room_sample['layout_scheme']
        for sample_one in layout_sample:
            group_list = []
            if 'group' in sample_one:
                group_list = sample_one['group']
            for group_idx in range(len(group_list) - 1, -1, -1):
                group_one = group_list[group_idx]
                if group_one['type'] in ['Meeting']:
                    pass
                elif group_one['type'] in ['Rest']:
                    object_one = {}
                    if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
                        object_one = group_one['obj_list'][0]
                    if 'position' in object_one and object_one['position'][1] > 0.2:
                        group_list.pop(group_idx)
    # 返回信息
    data_info, layout_info, propose_info, region_info, scene_info, route_info = {}, {}, {}, {}, {}, {}

    # 种子处理
    replace_room = {}
    if 'none' in replace_info:
        replace_val, replace_key = replace_info['none'], ''
        if 'soft' in replace_val and len(replace_val['soft']) > 0:
            replace_key = replace_val['soft'][0]
            if replace_key not in replace_note:
                object_type, object_style, object_size = get_furniture_data(replace_key)
                object_new = {
                    'id': replace_key, 'type': object_type, 'style': object_style,
                    'size': object_size[:], 'scale': [1, 1, 1],
                    'position': [0, 0, 0], 'rotation': [0, 0, 0, 1]
                }
                replace_note[replace_key] = object_new
            object_new = replace_note[replace_key]
            room_type = parse_object_room(object_new)
            replace_info[room_type] = replace_val
            replace_info.pop('none')
    room_list, room_wait_dict, room_type_dict, room_area_dict = [], {}, {}, {}
    replace_more, replace_keep, replace_deco = {}, {}, {}
    if 'room' in house_info:
        room_list = house_info['room']
    room_type_list_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']
    room_type_list_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom']
    room_type_list_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom']
    for room_idx, room_one in enumerate(room_list):
        room_key, room_type, room_area = '', '', 0
        if 'id' in room_one:
            room_key = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        if 'area' in room_one:
            room_area = room_one['area']
        if len(room_key) <= 0:
            continue
        room_type_dict[room_key] = room_type
        room_area_dict[room_key] = room_area
        if room_key in replace_room:
            # 还原信息
            replace_val = replace_room[room_key]
            replace_type, replace_style, replace_seed = '', '', []
            if 'type' in replace_val:
                replace_type = replace_val['type']
            if 'style' in replace_val:
                replace_style = replace_val['style']
            # 还原风格
            if len(replace_style) > 0:
                replace_style = get_furniture_style_en(replace_style)
                replace_val['style'] = replace_style
                style_mode = replace_style
            # 还原种子
            furniture_list, decorate_list = [], []
            if 'furniture_info' in room_one:
                furniture_list = room_one['furniture_info']
            if 'decorate_info' in room_one:
                decorate_list = room_one['decorate_info']
            if len(furniture_list) > 0:
                # 查找种子
                seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list, room_type)
                seed_one = {}
                for seed_one in seed_list:
                    seed_key, seed_style, seed_group, seed_role = seed_one['id'], '', '', ''
                    if 'style' in seed_one:
                        seed_style = seed_one['style']
                    if 'group' in seed_one and 'role' in seed_one:
                        seed_group, seed_role = seed_one['group'], seed_one['role']
                    if seed_role in ['sofa', 'bed', 'table']:
                        replace_seed.append(seed_key)
                        replace_note[seed_key] = seed_one
                        if len(replace_style) <= 0 and len(seed_style) > 0:
                            replace_style = seed_style
                            style_mode = seed_style
                if len(replace_seed) <= 0 and len(seed_one) > 0:
                    seed_key, seed_style, seed_group, seed_role = seed_one['id'], '', '', ''
                    if 'style' in seed_one:
                        seed_style = seed_one['style']
                    replace_seed.append(seed_key)
                    replace_note[seed_key] = seed_one
                    if len(replace_style) <= 0 and len(seed_style) > 0:
                        replace_style = seed_style
                        style_mode = seed_style
                if len(replace_seed) > 0:
                    replace_more[room_key] = {'soft': replace_seed}
                    replace_keep[room_key] = {'soft': replace_seed}
        elif room_key in replace_info:
            replace_more[room_key] = replace_info[room_key].copy()
        elif room_type in replace_info:
            if room_type not in room_wait_dict:
                room_wait_dict[room_type] = []
            room_wait_dict[room_type].append(room_key)
        elif room_type in room_type_list_1:
            for type_new in room_type_list_1:
                if type_new in replace_info:
                    if type_new not in room_wait_dict:
                        room_wait_dict[type_new] = []
                    room_wait_dict[type_new].append(room_key)
                    break
        elif room_type in room_type_list_2:
            for type_new in room_type_list_2:
                if type_new in replace_info:
                    if type_new not in room_wait_dict:
                        room_wait_dict[type_new] = []
                    room_wait_dict[type_new].append(room_key)
                    break
        elif room_type in room_type_list_3:
            for type_new in room_type_list_3:
                if type_new in replace_info:
                    if type_new not in room_wait_dict:
                        room_wait_dict[type_new] = []
                    room_wait_dict[type_new].append(room_key)
                    break
    for type_new, room_set in room_wait_dict.items():
        if type_new not in replace_info:
            continue
        if len(room_set) <= 0:
            pass
        room_max, area_max = room_set[0], 0
        for room_key in room_set:
            if room_key in room_area_dict:
                area_new = room_area_dict[room_key]
                if area_new > area_max:
                    room_max, area_max = room_key, area_new
        if len(room_max) > 0:
            replace_more[room_max] = replace_info[type_new].copy()
    for room_key, room_val in replace_more.items():
        room_type = ''
        if room_key in room_type_dict:
            room_type = room_type_dict[room_key]
        replace_wall, replace_floor, replace_soft = [], [], []
        if 'wall' in room_val:
            replace_wall = room_val['wall']
        if 'floor' in room_val:
            replace_floor = room_val['floor']
        if 'soft' in room_val:
            replace_soft = room_val['soft']
        # 墙面
        for object_key in replace_wall:
            if len(object_key) <= 0:
                continue
            if object_key not in replace_note:
                object_type, object_style, object_size = get_furniture_data(object_key)
                object_new = {
                    'id': object_key, 'type': object_type, 'style': object_style,
                    'size': object_size[:], 'scale': [1, 1, 1],
                    'position': [0, 0, 0], 'rotation': [0, 0, 0, 1]
                }
                replace_note[object_key] = object_new
        # 地面
        for object_key in replace_floor:
            if len(object_key) <= 0:
                continue
            if object_key not in replace_note:
                object_type, object_style, object_size = get_furniture_data(object_key)
                object_new = {
                    'id': object_key, 'type': object_type, 'style': object_style,
                    'size': object_size[:], 'scale': [1, 1, 1],
                    'position': [0, 0, 0], 'rotation': [0, 0, 0, 1]
                }
                replace_note[object_key] = object_new
        # 软装
        for object_key in replace_soft:
            if len(object_key) <= 0:
                continue
            # 添加
            if object_key not in replace_note:
                object_type, object_style, object_size = get_furniture_data(object_key)
                object_new = {
                    'id': object_key, 'type': object_type, 'style': object_style,
                    'size': object_size[:], 'scale': [1, 1, 1],
                    'position': [0, 0, 0], 'rotation': [0, 0, 0, 1]
                }
                replace_note[object_key] = object_new
            # 尺寸
            parse_object_size(object_new)
            # 类型
            parse_object_type(object_new, room_type)
            # 角色
            origin_size, origin_scale = object_new['size'], object_new['scale']
            object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
            func_group, func_role = compute_furniture_role(object_new['type'], object_size, room_type)
            # 装饰
            if func_group in GROUP_RULE_DECORATIVE:
                deco_group, deco_role = func_group, func_role
                object_new['group'] = deco_group
                object_new['role'] = deco_role
                if room_key not in replace_deco:
                    replace_deco[room_key] = [object_new]
                else:
                    replace_deco[room_key].append(object_new)
            # 朝向
            object_one = replace_note[object_key]
            parse_object_turn(object_key, object_one, func_role)
    # 布局处理
    refine_mode = 0
    if len(sample_info) > 0:
        refine_mode = 1
    data_info, layout_info, propose_info, region_info = \
        layout_house_by_sample(house_info, sample_info, replace_more, replace_note, refine_mode=refine_mode)
    # 定制处理
    group_type_main = ['Meeting', 'Bed', 'Media', 'Work', 'Dining', 'Bath', 'Toilet']
    region_more = house_rect_region_customized(house_info, layout_info, group_type_main)
    data_info = layout_house_customized(data_info, region_more)
    # 特征处理
    for room_idx, room_one in enumerate(room_list):
        room_key = room_one['id']
        layout_one, region_one = {}, []
        if room_key in layout_info:
            layout_one = layout_info[room_key]
        room_one['layout'] = layout_one

    # 给定方案
    if len(sample_info) > 0:
        # 推荐处理
        room_list = data_info['room']
        for room_info in room_list:
            room_key, room_data, room_layout_old, room_layout_new = room_info['id'], room_info, {}, {}
            if room_key in layout_info:
                room_layout_old = layout_info[room_key]
            source_house, source_room, room_sample_set = '', '', []
            # 方案处理
            if 'layout_scheme' in room_layout_old and len(room_layout_old['layout_scheme']) > 0:
                scheme_one = room_layout_old['layout_scheme'][0]
                if 'source_house' in scheme_one:
                    source_house = scheme_one['source_house']
                    source_house = source_house.lstrip('sample_house_')
                if 'source_room' in scheme_one:
                    source_room = scheme_one['source_room']
            if source_room in sample_info:
                # 信息打印
                layout_log_0 = 'propose room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S') + ' ' + room_key
                layout_log_0 += ' sample ' + source_room
                # 方案推荐
                layout_log_update(layout_log_0)
                room_sample_set = []
            else:
                # 信息打印
                layout_log_0 = 'propose room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S') + ' ' + room_key
                layout_log_update(layout_log_0)
                # 方案推荐
                room_sample_set = propose_sample_local(room_info, 1, house_id)
                layout_log_0 = 'propose done ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                layout_log_update(layout_log_0)

            # 房间信息
            room_type, room_area, room_link = '', 10, []
            if 'type' in room_info:
                room_type = room_info['type']
            if 'area' in room_info:
                room_area = room_info['area']
            if 'link' in room_info:
                room_link = room_info['link']
            # 方案整合
            if len(room_sample_set) > 0:
                sample_list_new, scheme_list_new = [], []
                for room_sample_idx, room_sample_add in enumerate(room_sample_set):
                    # 方案处理
                    sample_list_add, scheme_list_add = [], []
                    if 'layout_sample' in room_sample_add:
                        sample_list_add = room_sample_add['layout_sample']
                    if 'layout_scheme' in room_sample_add:
                        scheme_list_add = room_sample_add['layout_scheme']
                    if 'room_type' in room_sample_add and len(room_sample_add['room_type']) > 0:
                        room_type = room_sample_add['room_type']
                    # 调试信息
                    if '1282' in room_key and room_sample_idx == 0 and False:
                        print('propose debug')
                    # 组合调整
                    origin_house, origin_room, source_house, source_room, group_have, group_well = '', '', '', '', [], 0
                    if len(scheme_list_add) > 0:
                        scheme_one, group_list = scheme_list_add[0], []
                        if 'origin_sample_house' in scheme_one:
                            origin_house = scheme_one['origin_sample_house']
                        elif 'target_sample_house' in scheme_one:
                            origin_house = scheme_one['target_sample_house']
                        if 'origin_sample_room' in scheme_one:
                            origin_room = scheme_one['origin_sample_room']
                        elif 'target_sample_room' in scheme_one:
                            origin_room = scheme_one['target_sample_room']
                        if 'source_house' in scheme_one:
                            source_house = scheme_one['source_house']
                        if 'source_room' in scheme_one:
                            source_room = scheme_one['source_room']
                        if 'group' in scheme_one:
                            group_list = scheme_one['group']
                        for group_one in group_list:
                            group_type = group_one['type']
                            if group_type in GROUP_RULE_FUNCTIONAL:
                                group_have.append(group_type)
                    # 方案调整
                    if len(group_have) <= 2:
                        import_room_adjust(scheme_list_add, [], [], room_type, room_area, room_link)
                    if room_key in replace_deco:
                        import_room_adjust_deco(scheme_list_add, replace_deco[room_key])
                    # 打印信息
                    layout_log_0 = 'propose from ' + source_house + ' ' + source_room + ' ' + origin_house
                    layout_log_update(layout_log_0)
                    # 种子信息
                    replace_soft = []
                    if room_key in replace_more:
                        replace_dict = replace_more[room_key]
                        if 'soft' in replace_dict:
                            replace_soft = replace_dict['soft']
                    if room_key in replace_keep:
                        scheme_list = room_sample_add['layout_scheme']
                        for scheme_idx, scheme_one in enumerate(scheme_list):
                            scheme_one['target_place'] = 1
                    # 方案布局
                    refine_mode = 0
                    if room_key in replace_more:
                        refine_mode = 1
                    room_data_add, room_layout_add, room_propose_add, room_region_add = \
                        layout_room_by_sample(room_info, room_sample_add, replace_soft, replace_note, refine_mode=refine_mode)
                    sample_list_add, scheme_list_add = [], []
                    if 'layout_sample' in room_layout_add:
                        sample_list_add = room_layout_add['layout_sample']
                    if 'layout_scheme' in room_layout_add:
                        scheme_list_add = room_layout_add['layout_scheme']
                    # 方案增加
                    if len(sample_list_add) > 0 and len(scheme_list_add) > 0:
                        sample_list_new.append(sample_list_add[0])
                        scheme_list_new.append(scheme_list_add[0])
                        # 无效处理
                        scheme_one, group_list = scheme_list_add[0], []
                        if 'group' in scheme_one:
                            group_list = scheme_one['group']
                        for group_one in group_list:
                            group_type = group_one['type']
                            if group_type not in GROUP_RULE_FUNCTIONAL:
                                continue
                            if group_type not in group_have and False:
                                group_one['obj_list'] = []
                # 更新处理
                room_layout_new = room_layout_old.copy()
                room_layout_new['layout_sample'] = sample_list_new
                room_layout_new['layout_scheme'] = scheme_list_new
                layout_info[room_key] = room_layout_new
            else:
                # 更新处理
                room_layout_new = room_layout_old.copy()
                layout_info[room_key] = room_layout_new
            # 房间机位
            view_type = LAYOUT_VIEW_ROOM_TYPE[:]
            if len(layout_info) == 1:
                for room_key, room_val in layout_info.items():
                    if 'room_type' in room_val and len(room_val['room_type']) > 0:
                        view_type.append(room_val['room_type'])
            if room_type in view_type:
                camera_info = room_rect_view(room_data, room_layout_new, view_mode)
                wander_info = room_rect_path(room_data, room_layout_new, path_mode)
                room_rect_link(room_data, room_layout_new, house_info, view_type)
                if len(camera_info) > 0:
                    scene_info[room_key] = camera_info
                if len(wander_info) > 0:
                    route_info[room_key] = wander_info
            else:
                room_null_view(room_data, room_layout_new)
                room_null_path(room_data, room_layout_new)
            # 原始机位
            if 'wander' in room_data and len(room_data['wander']) > 0:
                wander_origin = room_data['wander']
                scheme_set = []
                if 'layout_scheme' in room_layout_new:
                    scheme_set = room_layout_new['layout_scheme']
                for scheme_idx, scheme_one in enumerate(scheme_set):
                    scheme_one['wander_origin'] = [wander_origin]
    # 推荐方案
    else:
        # 方案检索
        layout_log_0 = 'propose house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        # 方案检索
        house_sample_info = house_search_get_sample_info(house_info, replace_more, replace_note, layout_num, style_mode)
        layout_log_0 = 'propose done ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        # 推荐处理
        room_list = data_info['room']
        for room_info in room_list:
            room_key, room_data, room_layout_old, room_layout_new = room_info['id'], room_info, {}, {}
            if len(room_key) <= 0:
                continue
            if room_key in layout_info:
                room_layout_old = layout_info[room_key]
            source_house, source_room, room_sample_set = '', '', []
            # 信息打印
            layout_log_0 = 'propose room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S') + ' ' + room_key
            layout_log_update(layout_log_0)
            # 方案组合
            room_sample_set = []
            for sample_data_info in house_sample_info:
                if room_key in sample_data_info['sample']:
                    room_sample_set.append(sample_data_info['sample'][room_key])
            # 信息打印
            layout_log_0 = 'propose done ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
            layout_log_update(layout_log_0)
            pass
            # 房间信息
            room_type, room_area, room_link = '', 10, []
            if 'type' in room_info:
                room_type = room_info['type']
            if 'area' in room_info:
                room_area = room_info['area']
            if 'link' in room_info:
                room_link = room_info['link']
            # 方案整合
            view_type = LAYOUT_VIEW_ROOM_TYPE[:]
            if len(layout_info) == 1:
                for room_key, room_val in layout_info.items():
                    if 'room_type' in room_val and len(room_val['room_type']) > 0:
                        view_type.append(room_val['room_type'])
            if len(room_sample_set) > 0:
                sample_list_new, scheme_list_new = [], []
                for room_sample_idx, room_sample_add in enumerate(room_sample_set):
                    # 方案处理
                    sample_list_add, scheme_list_add = [], []
                    if 'layout_sample' in room_sample_add:
                        sample_list_add = room_sample_add['layout_sample']
                    if 'layout_scheme' in room_sample_add:
                        scheme_list_add = room_sample_add['layout_scheme']
                    if 'room_type' in room_sample_add and len(room_sample_add['room_type']) > 0:
                        copy_type = room_sample_add['room_type']
                        if room_type in view_type and copy_type not in view_type:
                            pass
                        else:
                            room_type = copy_type
                    # 调试信息
                    if '9538' in room_key and room_sample_idx == 1 and False:
                        print('propose debug')
                    # 组合调整
                    origin_house, origin_room, source_house, source_room, group_have, group_well = '', '', '', '', [], 0
                    if len(scheme_list_add) > 0:
                        scheme_one, group_list, group_tune = scheme_list_add[0], [], []
                        if 'origin_sample_house' in scheme_one:
                            origin_house = scheme_one['origin_sample_house']
                        elif 'target_sample_house' in scheme_one:
                            origin_house = scheme_one['target_sample_house']
                        if 'origin_sample_room' in scheme_one:
                            origin_room = scheme_one['origin_sample_room']
                        elif 'target_sample_room' in scheme_one:
                            origin_room = scheme_one['target_sample_room']
                        if 'source_house' in scheme_one:
                            source_house = scheme_one['source_house']
                        if 'source_room' in scheme_one:
                            source_room = scheme_one['source_room']
                        if 'group' in scheme_one:
                            group_list = scheme_one['group']
                        for group_one in group_list:
                            group_type = group_one['type']
                            if group_type in GROUP_RULE_FUNCTIONAL:
                                group_have.append(group_type)
                                if group_type in ['Cabinet', 'Armoire'] and group_one['size'][0] < 0.5:
                                    group_well += 0
                                else:
                                    group_well += 1
                            if room_type in ['DiningRoom'] and group_type in ['Meeting']:
                                pass
                            else:
                                group_tune.append(group_one)
                        scheme_one['group'] = group_tune
                    # 方案调整
                    if group_well <= 2:
                        import_room_adjust(scheme_list_add, [], [], room_type, room_area, room_link)
                    elif room_type in ['LivingRoom', 'LivingDiningRoom'] and room_area > 25:
                        import_room_adjust(scheme_list_add, [], [], room_type, room_area, room_link)
                    if room_key in replace_deco:
                        import_room_adjust_deco(scheme_list_add, replace_deco[room_key])
                    # 打印信息
                    layout_log_0 = 'propose from ' + source_house + ' ' + source_room + ' ' + origin_house
                    layout_log_update(layout_log_0)
                    # 种子信息
                    replace_soft = []
                    if room_key in replace_more:
                        replace_dict = replace_more[room_key]
                        if 'soft' in replace_dict:
                            replace_soft = replace_dict['soft']
                    if room_key in replace_keep:
                        scheme_list = room_sample_add['layout_scheme']
                        for scheme_idx, scheme_one in enumerate(scheme_list):
                            scheme_one['target_place'] = 1
                    # 方案布局
                    room_data_add, room_layout_add, room_propose_add, room_region_add = \
                        layout_room_by_sample(room_info, room_sample_add, replace_soft, replace_note, refine_mode=0)
                    sample_list_add, scheme_list_add = [], []
                    if 'layout_sample' in room_layout_add:
                        sample_list_add = room_layout_add['layout_sample']
                    if 'layout_scheme' in room_layout_add:
                        scheme_list_add = room_layout_add['layout_scheme']
                    # 方案增加
                    if len(sample_list_add) > 0 and len(scheme_list_add) > 0:
                        sample_list_new.append(sample_list_add[0])
                        scheme_list_new.append(scheme_list_add[0])
                        # 无效处理
                        scheme_one, group_list = scheme_list_add[0], []
                        if 'group' in scheme_one:
                            group_list = scheme_one['group']
                        for group_one in group_list:
                            group_type = group_one['type']
                            if group_type not in GROUP_RULE_FUNCTIONAL:
                                continue
                            if group_type not in group_have and False:
                                group_one['obj_list'] = []
                # 更新处理
                room_layout_new = room_layout_old.copy()
                room_layout_new['layout_sample'] = sample_list_new
                room_layout_new['layout_scheme'] = scheme_list_new
                layout_info[room_key] = room_layout_new
            else:
                # 更新处理
                room_layout_new = room_layout_old.copy()
                layout_info[room_key] = room_layout_new
            # 房间机位
            if room_type in view_type:
                camera_info = room_rect_view(room_data, room_layout_new, view_mode)
                if len(camera_info) > 0:
                    scene_info[room_key] = camera_info
                wander_info = room_rect_path(room_data, room_layout_new, path_mode)
                if len(wander_info) > 0:
                    route_info[room_key] = wander_info
                room_rect_link(room_data, room_layout_new, house_info, view_type)
            else:
                room_null_view(room_data, room_layout_new)
                room_null_path(room_data, room_layout_new)
            # 原始机位
            if 'wander' in room_data and len(room_data['wander']) > 0:
                wander_origin = room_data['wander']
                scheme_set = []
                if 'layout_scheme' in room_layout_new:
                    scheme_set = room_layout_new['layout_scheme']
                for scheme_idx, scheme_one in enumerate(scheme_set):
                    scheme_one['wander_origin'] = [wander_origin]

    # 门窗处理
    if deco_mode < 2:
        for room_id, room_layout_info in layout_info.items():
            for scheme_one in room_layout_info['layout_scheme']:
                for group_one in scheme_one['group']:
                    if group_one['type'] in ['Door']:
                        group_one['obj_list'] = []
                    elif group_one['type'] in ['Window']:
                        obj_list_new = []
                        obj_list_old = group_one['obj_list']
                        for object_one in obj_list_old:
                            if object_one['type'].startswith('curtain'):
                                obj_list_new.append(object_one)
                        group_one['obj_list'] = obj_list_new
        for room_id, room_propose_info in propose_info.items():
            for propose_one in room_propose_info:
                target_list_new = []
                target_list_old = propose_one['target_scope']
                for target_one in target_list_old:
                    if target_one['type'].startswith('door') or target_one['type'].startswith('window'):
                        pass
                    else:
                        target_list_new.append(target_one)
                propose_one['target_scope'] = target_list_new
    # 镜像处理
    house_rect_mirror(layout_info)
    # 清空处理
    if clear_mode == 1:
        for room_key, room_layout in layout_info.items():
            scheme_list, group_list = [], []
            if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
                scheme_list = room_layout['layout_scheme']
            for scheme_one in scheme_list:
                group_list = []
                if 'group' in scheme_one:
                    group_list = scheme_one['group']
                for group_one in group_list:
                    group_type, object_list, object_find = group_one['type'], [], False
                    if 'obj_list' in group_one:
                        object_list = group_one['obj_list']
                    if group_type in GROUP_RULE_FUNCTIONAL:
                        object_keep = []
                        if object_find:
                            group_one['obj_list'] = object_keep
                        else:
                            for object_one in object_list:
                                if object_one['id'] in replace_note:
                                    object_find = True
                                    object_keep = [object_one]
                                    break
                            group_one['obj_list'] = object_keep
                    elif group_type in ['Ceiling', 'Door', 'Window']:
                        continue
                    else:
                        group_one['obj_list'] = []
    # 种子处理
    for room_key, room_val in replace_more.items():
        replace_wall, replace_floor, replace_soft = [], [], []
        if 'wall' in room_val:
            replace_wall = room_val['wall']
        if 'floor' in room_val:
            replace_floor = room_val['floor']
        if 'soft' in room_val:
            replace_soft = room_val['soft']

        group_list = []
        if room_key in layout_info and 'layout_scheme' in layout_info[room_key]:
            scheme_set = layout_info[room_key]['layout_scheme']
            if len(scheme_set) > 0 and 'group' in scheme_set[0]:
                group_list = scheme_set[0]['group']
        replace_used, replace_dump = [], []
        for replace_key in replace_soft:
            replace_use = False
            for group_one in group_list:
                object_list = group_one['obj_list']
                for object_one in object_list:
                    if object_one['id'] == replace_key:
                        replace_use = True
                        break
                if replace_use:
                    break
            if replace_use:
                replace_used.append(replace_key)
            elif replace_key in replace_note:
                note_new = replace_note[replace_key]
                if 'group' in note_new and 'role' in note_new:
                    pass
                else:
                    continue
                for used_key in replace_used:
                    if used_key not in replace_note:
                        continue
                    note_old = replace_note[used_key]
                    if 'group' in note_old and 'role' in note_old:
                        pass
                    else:
                        continue
                    if note_old['group'] == note_new['group'] and note_old['role'] == note_new['role']:
                        replace_dump.append(replace_key)
                        break
        room_val['used'] = replace_used
        room_val['dump'] = replace_dump
    for room_key, room_val in replace_info.items():
        if room_key in replace_more:
            replace_info[room_key] = replace_more[room_key]
        else:
            for room_key_more, room_val_more in replace_more.items():
                if room_key in room_wait_dict and room_key_more in room_wait_dict[room_key]:
                    if 'used' in room_val_more and len(room_val_more['used']) > 0:
                        replace_info[room_key] = replace_more[room_key_more]
                        break

    # 返回信息
    return data_info, layout_info, propose_info, region_info, scene_info, route_info


# 单屋布局方案
def layout_sample_room(room_info, sample_info, replace_info={}, replace_note={}, layout_num=3, style_mode='',
                       house_id='', deco_mode=2, view_mode=0, path_mode=-1, clear_mode=0):
    # 方案信息
    if 'layout_sample' in sample_info:
        layout_sample = sample_info['layout_sample']
        for sample_one in layout_sample:
            group_list = []
            if 'group' in sample_one:
                group_list = sample_one['group']
            for group_idx in range(len(group_list) - 1, -1, -1):
                group_one = group_list[group_idx]
                if group_one['type'] in ['Meeting']:
                    if 'type' in room_info and room_info['type'] in ['DiningRoom']:
                        group_list.pop(group_idx)
                elif group_one['type'] in ['Rest']:
                    object_one = {}
                    if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
                        object_one = group_one['obj_list'][0]
                    if 'position' in object_one and object_one['position'][1] > 0.2:
                        group_list.pop(group_idx)
    # 返回信息
    data_info, layout_info, propose_info, region_info, scene_info, route_info = {}, {}, {}, {}, {}, {}

    # 种子处理
    replace_soft = []
    if 'soft' in replace_info:
        replace_soft = replace_info['soft']

    # 给定方案
    if len(sample_info) > 0:
        # 布局处理
        data_info, layout_info, propose_info, region_info = \
            layout_room_by_sample(room_info, sample_info, replace_soft, replace_note, refine_mode=1)
        room_data, room_layout = data_info, layout_info
        # 机位处理
        camera_info = room_rect_view(room_data, room_layout, view_mode)
        if len(camera_info) > 0:
            scene_info = camera_info
        wander_info = room_rect_path(room_data, room_layout, path_mode)
        if len(wander_info) > 0:
            route_info = wander_info
        # 原始机位
        if 'wander' in room_data and len(room_data['wander']) > 0:
            wander_origin = room_data['wander']
            scheme_set = []
            if 'layout_scheme' in room_layout:
                scheme_set = room_layout['layout_scheme']
            for scheme_idx, scheme_one in enumerate(scheme_set):
                scheme_one['wander_origin'] = [wander_origin]
    # 推荐方案
    else:
        # 布局处理
        data_info, layout_info, propose_info, region_info = \
            layout_room_by_sample(room_info, sample_info, replace_soft, replace_note, refine_mode=1)
        # 推荐房间 布局房间 拼接布局
        room_key, room_data, room_layout_old = room_info['id'], room_info, {}
        room_layout_old = layout_info
        # 打印信息
        layout_log_0 = 'propose room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S') + ' ' + room_key
        layout_log_update(layout_log_0)
        room_sample_set = propose_sample(room_info, room_layout_old, layout_num, house_id)
        layout_log_0 = 'propose done ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        # 方案整合
        if len(room_sample_set) > 0:
            sample_list_new, scheme_list_new = [], []
            for room_sample_add in room_sample_set:
                # 方案处理
                sample_list_add, scheme_list_add = [], []
                if 'layout_sample' in room_sample_add:
                    sample_list_add = room_sample_add['layout_sample']
                if 'layout_scheme' in room_sample_add:
                    scheme_list_add = room_sample_add['layout_scheme']
                group_have = []
                if len(scheme_list_add) > 0:
                    scheme_one, group_list = scheme_list_add[0], []
                    if 'group' in scheme_one:
                        group_list = scheme_one['group']
                    for group_one in group_list:
                        group_type = group_one['type']
                        if group_type in GROUP_RULE_FUNCTIONAL:
                            group_have.append(group_type)
                # 方案布局
                room_data_add, room_layout_add, room_propose_add, room_region_add = \
                    layout_room_by_sample(room_info, room_sample_add, [], {}, refine_mode=0)
                sample_list_add, scheme_list_add = [], []
                if 'layout_sample' in room_layout_add:
                    sample_list_add = room_layout_add['layout_sample']
                if 'layout_scheme' in room_layout_add:
                    scheme_list_add = room_layout_add['layout_scheme']
                # 方案增加
                if len(sample_list_add) > 0 and len(scheme_list_add) > 0:
                    sample_list_new.append(sample_list_add[0])
                    scheme_list_new.append(scheme_list_add[0])
                    # 无效处理
                    scheme_one, group_list = scheme_list_add[0], []
                    if 'group' in scheme_one:
                        group_list = scheme_one['group']
                    for group_one in group_list:
                        group_type = group_one['type']
                        if group_type in GROUP_RULE_FUNCTIONAL and group_type not in group_have:
                            group_one['obj_list'] = []
            # 更新处理
            room_layout_new = room_layout_old.copy()
            room_layout_new['layout_sample'] = sample_list_new
            room_layout_new['layout_scheme'] = scheme_list_new
            layout_info = room_layout_new
            # 机位处理
            camera_info = room_rect_view(room_data, room_layout_new, view_mode)
            if len(camera_info) > 0:
                scene_info = camera_info
            wander_info = room_rect_path(room_data, room_layout_new, path_mode)
            if len(wander_info) > 0:
                route_info = wander_info
            # 原始机位
            if 'wander' in room_data and len(room_data['wander']) > 0:
                wander_origin = room_data['wander']
                scheme_set = []
                if 'layout_scheme' in room_layout_new:
                    scheme_set = room_layout_new['layout_scheme']
                for scheme_idx, scheme_one in enumerate(scheme_set):
                    scheme_one['wander_origin'] = [wander_origin]
        pass

    # 门窗处理
    if deco_mode < 2:
        for scheme_one in layout_info['layout_scheme']:
            for group_one in scheme_one['group']:
                if group_one['type'] in ['Door']:
                    group_one['obj_list'] = []
                elif group_one['type'] in ['Window']:
                    obj_list_new = []
                    obj_list_old = group_one['obj_list']
                    for object_one in obj_list_old:
                        if object_one['type'].startswith('curtain'):
                            obj_list_new.append(object_one)
                    group_one['obj_list'] = obj_list_new
        for propose_one in propose_info:
            target_list_new = []
            target_list_old = propose_one['target_scope']
            for target_one in target_list_old:
                if target_one['type'].startswith('door') or target_one['type'].startswith('window'):
                    pass
                else:
                    target_list_new.append(target_one)
            propose_one['target_scope'] = target_list_new
    # 镜像处理
    room_rect_mirror(layout_info)
    # 清空处理
    if clear_mode == 1:
        room_layout = layout_info
        scheme_list, group_list = [], []
        if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
            scheme_list = room_layout['layout_scheme']
        for scheme_one in scheme_list:
            group_list = []
            if 'group' in scheme_one:
                group_list = scheme_one['group']
            for group_one in group_list:
                group_type, object_list, object_find = group_one['type'], [], False
                if 'obj_list' in group_one:
                    object_list = group_one['obj_list']
                if group_type in GROUP_RULE_FUNCTIONAL:
                    object_keep = []
                    if object_find:
                        group_one['obj_list'] = object_keep
                    else:
                        for object_one in object_list:
                            if object_one['id'] in replace_note:
                                object_find = True
                                object_keep = [object_one]
                                break
                        group_one['obj_list'] = object_keep
                elif group_type in ['Ceiling', 'Door', 'Window']:
                    continue
                else:
                    group_one['obj_list'] = []

    # 返回信息
    return data_info, layout_info, propose_info, region_info, scene_info, route_info


# 单屋布局场景
def layout_scene_room(room_info, group_list, scene_info, deco_mode=2, view_mode=0, path_mode=-1):
    # 布局处理
    data_info, layout_info, propose_info, region_info = layout_room_by_group(room_info, group_list)

    # 机位处理
    scheme_list = []
    if 'layout_scheme' in layout_info:
        scheme_list = layout_info['layout_scheme']
    for scheme_one in scheme_list:
        scene_new = room_copy_view(scene_info)
        scheme_one['scene'] = [scene_new]

    # 赋值处理
    group_have = []
    if len(group_list) > 0:
        group_have = [group_list[0]['type']]
    room_data, room_layout = data_info, layout_info

    # 机位处理
    camera_info = room_rect_view(room_data, room_layout, view_mode)
    # 点位处理
    wander_info = room_rect_path(room_data, room_layout, path_mode)
    # 无效处理
    if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
        scheme_one = room_layout['layout_scheme'][0]
        group_list = []
        if 'group' in scheme_one:
            group_list = scheme_one['group']
        for group_one in group_list:
            group_type = group_one['type']
            if group_type in GROUP_RULE_FUNCTIONAL and group_type not in group_have:
                group_one['obj_list'] = []

    # 门窗处理
    if deco_mode < 2:
        for scheme_one in layout_info['layout_scheme']:
            for group_one in scheme_one['group']:
                if group_one['type'] in ['Door']:
                    group_one['obj_list'] = []
                elif group_one['type'] in ['Window']:
                    obj_list_new = []
                    obj_list_old = group_one['obj_list']
                    for object_one in obj_list_old:
                        if object_one['type'].startswith('curtain'):
                            obj_list_new.append(object_one)
                    group_one['obj_list'] = obj_list_new
        for propose_one in propose_info:
            target_list_new = []
            target_list_old = propose_one['target_scope']
            for target_one in target_list_old:
                if target_one['type'].startswith('door') or target_one['type'].startswith('window'):
                    pass
                else:
                    target_list_new.append(target_one)
            propose_one['target_scope'] = target_list_new

    # 返回信息
    return data_info, layout_info, propose_info, camera_info, wander_info


# 全屋布局参考
def layout_advice_house(house_info, sample_num):
    # 计算特征
    data_info, layout_info, propose_info, region_info = layout_house_by_refer(house_info, sample_num)
    # 返回信息
    return data_info, layout_info, propose_info, region_info


# 单屋布局参考
def layout_advice_room(room_info, sample_num):
    # 纠正点列
    correct_room_point(room_info)
    # 纠正类型
    room_id, room_type, room_area = '', '', 10
    if 'id' in room_info:
        room_id = room_info['id']
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    furniture_list, decorate_list = [], []
    if 'furniture_info' in room_info:
        furniture_list = room_info['furniture_info']
    if 'decorate_info' in room_info:
        decorate_list = room_info['decorate_info']
    # 纠正类型
    if room_type not in ROOM_TYPE_MAIN:
        seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list, room_type,
                                                                       room_area)
        correct_room_type(room_info, seed_list, keep_list)
    # 纠正连通
    correct_room_link(room_info)
    # 计算特征
    data_info, layout_info, propose_info, region_info = layout_room_by_refer(room_info, sample_num)
    # 返回信息
    return data_info, layout_info, propose_info, region_info


# 全屋布局参考
def layout_advice_list(house_list=[], sample_flag=False, reload=True):
    source_list, target_list = [], []
    # 默认
    if len(house_list) <= 0:
        if sample_flag:
            source_list = get_source_list()
        else:
            target_list = get_target_list()
    # 指定
    else:
        if sample_flag:
            source_list = house_list
        else:
            target_list = house_list

    # 文件名
    house_file = 'house_feature.json'
    house_dict = {}
    # 样板间
    if sample_flag:
        house_file = 'house_feature_sample.json'
        for house_idx, house_key in enumerate(source_list):
            if 0 <= house_idx < 2000:
                pass
            else:
                continue
            if house_idx % 10 == 0 and house_idx >= 1:
                print('fetch house source %04d' % house_idx)
            if house_idx % 100 == 0 and house_idx >= 1:
                save_room_sample()
                save_furniture_data()
            sample_para, sample_data, sample_layout, sample_group = get_house_sample(house_key, reload)
            if 'room' in sample_para:
                room_dict = sample_para['room']
                for room_key, room_val in room_dict.items():
                    if 'feature' in room_val:
                        room_vec = room_val['feature']
                        house_dict[house_key + '_' + room_key] = room_vec
    # 空户型
    else:
        house_file = 'house_feature_target.json'
        for house_idx, house_key in enumerate(target_list):
            if house_idx % 10 == 0 and house_idx >= 1:
                print('fetch house target %04d' % house_idx)
            if house_idx % 100 == 0 and house_idx >= 1:
                # save_room_data()
                pass
            house_para, house_data = get_house_data(house_key, '', '', reload)
            if 'room' in house_para:
                room_dict = house_para['room']
                for room_key, room_val in room_dict.items():
                    if 'feature' in room_val:
                        room_vec = room_val['feature']
                        house_dict[house_key + '_' + room_key] = room_vec

    # 保存
    json_path = os.path.join(DATA_DIR_SERVER_SCHEME, house_file)
    with open(json_path, "w") as f:
        json.dump(house_dict, f, indent=4)
        f.close()
    if os.path.exists(json_path):
        oss_upload_file(house_file, json_path, DATA_OSS_DATABASE)
    # 保存
    # save_room_data()
    save_room_sample()
    save_furniture_data()


# 全屋组合提取
def layout_group_house(house_info):
    data_info, layout_info, group_info = group_house(house_info)
    return data_info, layout_info, group_info


# 全屋机位布局
def layout_camera_house(house_info, scheme_mode=''):
    # 解析
    house_data = layout_sample_analyze(house_info, scheme_mode)
    house_layout = {}
    if 'layout' in house_data:
        # 生成方案
        house_layout = house_data['layout']
    # 机位
    house_view = layout_sample_camera(house_data)
    # 返回
    return house_data, house_layout, house_view


# 单屋机位布局
def layout_camera_room(room_info, scheme_mode=''):
    # 解析
    room_data = room_info
    # 机位
    room_view = {}
    # 返回
    return room_view


# 布局服务入口
def layout_sample_param(param_info):
    # 户型参数
    house_id, room_id, plat_id = '', '', ''
    house_data, room_data = {}, {}
    sample_scene, sample_scene_url, sample_scene_list = {}, '', []
    house_sample, room_sample = {}, {}
    house_replace, room_replace, note_replace = {}, {}, {}
    if 'house_id' in param_info:
        house_id = param_info['house_id']
    if 'room_id' in param_info:
        room_id = param_info['room_id']
    if 'plat_id' in param_info:
        plat_id = param_info['plat_id']
    if 'house_data' in param_info:
        house_data = param_info['house_data']
    if 'room_data' in param_info:
        room_data = param_info['room_data']
    if 'sample_scene' in param_info:
        sample_scene = param_info['sample_scene']
    if 'sample_scene_url' in param_info:
        sample_scene_url = param_info['sample_scene_url']
    if 'sample_scene_list' in param_info:
        sample_scene_list = param_info['sample_scene_list']
        if len(sample_scene_url) > 0:
            sample_scene_list.insert(0, sample_scene_url)
    if 'house_sample' in param_info:
        house_sample = param_info['house_sample']
    if 'room_sample' in param_info:
        room_sample = param_info['room_sample']
    if 'house_replace' in param_info:
        house_replace = param_info['house_replace']
    if 'room_replace' in param_info:
        room_replace = param_info['room_replace']
    if 'note_replace' in param_info:
        note_replace = param_info['note_replace']
    if 'replace_info' in param_info:
        house_replace = param_info['replace_info']
    # 户型位置
    house_idx = -1
    data_url, scene_url, image_url = '', '', ''
    scene_path, scene_flag = '', False
    design_id, design_url = '', ''
    if 'data_idx' in param_info:
        house_idx = param_info['data_idx']
    if 'data_url' in param_info:
        data_url = param_info['data_url']
    if 'scene_url' in param_info:
        scene_url = param_info['scene_url']
    if 'image_url' in param_info:
        image_url = param_info['image_url']
    if 'design_id' in param_info:
        design_id = param_info['design_id']
    if 'design_url' in param_info:
        design_url = param_info['design_url']
    if 'scene_url_trigger' in param_info:
        scene_flag = param_info['scene_url_trigger']
    if design_id == '' and not house_id == '':
        design_id = house_id
    # 场景参数
    group_sample, group_vector, room_best, room_more = {}, [], '', []
    if len(sample_scene) > 0:
        sample_scene = room_copy_view(sample_scene)
        group_sample, group_vector, room_best, room_more = parse_vector_data(sample_scene)
    if len(sample_scene_url) > 0:
       group_sample, group_vector, room_best, room_more = parse_vector_url(sample_scene_url)
    # 样板参数
    sample_house, sample_room, sample_json, sample_url, sample_info = '', '', {}, '', {}
    sample_data, sample_layout, sample_group, sample_scene = {}, {}, {}, {}
    sample_vector = {}
    if 'sample_house' in param_info:
        sample_house = param_info['sample_house']
    if 'sample_room' in param_info:
        sample_room = param_info['sample_room']
    if 'sample_house_id' in param_info:
        sample_house = param_info['sample_house_id']
    if 'sample_room_id' in param_info:
        sample_room = param_info['sample_room_id']
    if 'sample_house_json' in param_info:
        sample_json = param_info['sample_house_json']
    if 'sample_house_json_url' in param_info:
        sample_url = param_info['sample_house_json_url']
    if len(sample_json) > 0:
        sample_data, sample_layout, sample_group, sample_scene = parse_sample_data(sample_json)
        sample_info = sample_data
    elif len(sample_url) > 0:
        sample_data, sample_layout, sample_group, sample_scene = parse_sample_url(sample_url)
        sample_info = sample_data

    # 布局模式
    layout_mode = LAYOUT_MODE_SCHEME
    if 'layout_mode' in param_info:
        if param_info['layout_mode'] == LAYOUT_MODE_ADVICE:
            layout_mode = LAYOUT_MODE_ADVICE
        if param_info['layout_mode'] == LAYOUT_MODE_GROUP:
            layout_mode = LAYOUT_MODE_GROUP
        if param_info['layout_mode'] == LAYOUT_MODE_CAMERA:
            layout_mode = LAYOUT_MODE_CAMERA
    layout_num, propose_num = 4, 2
    if layout_mode in [LAYOUT_MODE_TRANSFER, LAYOUT_MODE_ADJUST, LAYOUT_MODE_CAMERA]:
        layout_num, propose_num = 1, 1
    elif layout_mode in [LAYOUT_MODE_ADVICE]:
        layout_num, propose_num = 1, 1
    if 'layout_number' in param_info:
        layout_num = param_info['layout_number']
    if 'propose_number' in param_info:
        propose_num = param_info['propose_number']
    if layout_num <= 0 or layout_num > 10:
        layout_num = 3
    if 0 < len(sample_scene_list) < layout_num:
        layout_num = len(sample_scene_list)
    # 整体布局
    if layout_mode == LAYOUT_MODE_TRANSFER:
        layout_mode_str = 'layout transfer'
    elif layout_mode == LAYOUT_MODE_PROPOSE:
        layout_mode_str = 'layout propose'
    elif layout_mode == LAYOUT_MODE_SCHEME:
        layout_mode_str = 'layout scheme'
    elif layout_mode == LAYOUT_MODE_ADJUST:
        layout_mode_str = 'layout adjust'
    # 参考布局
    elif layout_mode == LAYOUT_MODE_ADVICE:
        layout_mode_str = 'layout advice'
    # 组合布局
    elif layout_mode == LAYOUT_MODE_GROUP:
        layout_mode_str = 'layout group'
    # 配饰布局
    elif layout_mode == LAYOUT_MODE_ADORN:
        layout_mode_str = 'layout adorn'
    # 机位布局
    elif layout_mode == LAYOUT_MODE_CAMERA:
        layout_mode_str = 'layout camera'
    else:
        layout_mode_str = 'layout propose'

    # 超时参数
    layout_time = 15
    if 'layout_time' in param_info:
        layout_time = int(param_info['layout_time'])
    # 保存模式
    scheme_mode, style_mode, struct_mode, render_mode, render_room = '', '', '', '', []
    save_mode, view_mode, path_mode = [], 0, -1
    clear_mode = 0
    if 'scheme_mode' in param_info:
        scheme_mode = str(param_info['scheme_mode']).lower()
        # 绘制
        if 'image' in scheme_mode:
            save_mode.append(SAVE_MODE_IMAGE)
        if 'frame' in scheme_mode:
            save_mode.append(SAVE_MODE_FRAME)
        # 数据
        if 'data' in scheme_mode:
            save_mode.append(SAVE_MODE_DATA)
        if 'group' in scheme_mode:
            save_mode.append(SAVE_MODE_GROUP)
        if 'layout' in scheme_mode:
            save_mode.append(SAVE_MODE_LAYOUT)
        if 'propose' in scheme_mode:
            save_mode.append(SAVE_MODE_PROPOSE)
        # 机位
        if 'render' in scheme_mode:
            save_mode.append(SAVE_MODE_RENDER)
            view_mode = VIEW_MODE_SINGLE
        if 'single' in scheme_mode:
            view_mode = VIEW_MODE_SINGLE
        if 'sphere' in scheme_mode:
            view_mode = VIEW_MODE_SPHERE
        if 'wander' in scheme_mode:
            save_mode.append(SAVE_MODE_WANDER)
            path_mode = PATH_MODE_WANDER
        # 清空
        if 'clear' in scheme_mode:
            clear_mode = 1
    if 'style_mode' in param_info:
        style_mode = param_info['style_mode']
    if 'struct_mode' in param_info:
        struct_mode = param_info['struct_mode']
    if 'render_mode' in param_info:
        render_mode = str(param_info['render_mode']).lower()
    if 'render_room' in param_info:
        render_room = param_info['render_room']
    # 商品模式
    todo_room = []
    if 'house_item' in param_info:
        todo_room = parse_anchor_room(param_info['house_item'])

    # 打印信息
    layout_log_create(layout_time)
    layout_log_0 = layout_mode_str + ' ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    # 打印信息
    target_id = house_id
    if target_id == '' and not design_id == '':
        target_id = design_id
    layout_log_0 = 'target house: %s, room: %s, layout: %d, propose: %d' % (target_id, room_id, 1, 1)
    layout_log_update(layout_log_0)

    # 解析模板
    if len(sample_info) <= 0 and len(sample_house) > 0 and layout_mode in [LAYOUT_MODE_ADVICE]:
        sample_data, sample_layout, sample_group, sample_scene = parse_sample_id(sample_house)
        sample_info = sample_data
    # 解析户型
    if layout_mode in [LAYOUT_MODE_ADVICE]:
        if 'house_list' in param_info:
            house_list = param_info['house_list']
            layout_advice_list(house_list=house_list, sample_flag=False)
        if 'sample_list' in param_info:
            sample_list = param_info['sample_list']
            layout_advice_list(house_list=sample_list, sample_flag=True)

    # 布局信息
    house_para_info = {}
    house_data_info, house_layout_info, house_propose_info, house_region_info, \
    house_group_info, house_scene_info, house_route_info, house_view_info = {}, {}, {}, {}, {}, {}, {}, {}
    room_data_info, room_layout_info, room_propose_info, room_region_info, \
    room_group_info, room_scene_info, room_route_info, room_view_info = {}, {}, {}, {}, {}, {}, {}, {}
    sample_data_info, sample_layout_info, sample_scene_info = {}, {}, {}
    try:
        # 户型解析
        if len(house_data) <= 0 and len(room_data) <= 0:
            house_para_info, house_data_info = {}, {}
            # house_idx
            if house_id == '' and 0 <= house_idx and design_id == '' and scene_url == '' and data_url == '':
                house_list = list_house_oss(DATA_OSS_HOUSE_EMPTY, house_idx, 1)
                if len(house_list) > 0:
                    house_id = house_list[0]
            # data url
            if len(house_data_info) <= 0 and not data_url == '':
                pass
            # design url design id
            if len(house_data_info) <= 0 and not design_id == '':
                reload = False
                if len(scene_url) > 0 and layout_mode in [LAYOUT_MODE_CAMERA]:
                    reload = True
                house_para_info, house_data_info = parse_design_data(design_id, design_url, scene_url, reload)
                if 'id' in house_data_info:
                    house_id = design_id
                    house_data_info['id'] = design_id
            # scene url
            if len(house_data_info) <= 0 and not scene_url == '':
                scene_have, scene_path = download_scene_by_url(scene_url, DATA_DIR_SERVER_INPUT)
                if scene_have and os.path.exists(scene_path):
                    house_id_new, house_data_info, house_feature_info = get_house_data_feature_by_path(scene_path, '', todo_room)
            # house id
            if len(house_data_info) <= 0 and not house_id == '':
                house_id_new, house_data_info, house_feature_info = get_house_data_feature(house_id, True)
                if len(house_data_info) <= 0 and design_id == '':
                    design_id = house_id
            # image url
            if len(house_data_info) <= 0 and not image_url == '':
                pass
            # 户型更新
            if len(house_data_info) > 0:
                house_data, room_list = house_data_info, []
                if 'room' in house_data_info:
                    room_list = house_data_info['room']
                if len(room_id) > 0:
                    for room_one in room_list:
                        if room_id == str(room_one['id']):
                            room_data = room_one
                            break
                if len(room_best) > 0 and len(room_data) <= 0:
                    for room_one in room_list:
                        type_old_1 = str(room_one['type'])
                        type_old_2 = str(room_one['id']).split('-')[0]
                        if type_old_1 == room_best or type_old_2 == room_best:
                            room_data = room_one
                            break
                        if type_old_1 in room_more or type_old_2 in room_more:
                            room_data = room_one
                if len(todo_room) > 0:
                    for room_idx in range(len(room_list) - 1, -1, -1):
                        room_one, room_flag = room_list[room_idx], False
                        for todo_key in todo_room:
                            if todo_key in room_one['id']:
                                room_flag = True
                                break
                        if not room_flag:
                            room_list.pop(room_idx)
        layout_log_0 = 'resolve success' + ' ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)

        # 场景匹配
        if len(house_data) > 0 and len(room_data) <= 0 and len(sample_scene) > 0:
            room_list, room_info = [], {}
            group_set, group_vec, room_best, room_more = parse_vector_data(sample_scene)
            if 'room' in house_data:
                room_list = house_data['room']
            for room_one in room_list:
                if 'type' in room_one:
                    room_type = room_one['type']
                    if room_type == room_best:
                        room_data = room_one
                        break
                    elif room_type in room_more:
                        room_data = room_one
                        continue
                    elif len(room_data) <= 0:
                        room_data = room_one
                        continue

        # 单屋布局
        if len(room_data) > 0:
            if 'id' in room_data and room_id == '':
                room_id = room_data['id']
            if 'coordinate' not in room_data:
                room_data['coordinate'] = 'xzy'
            if 'unit' not in room_data:
                room_data['unit'] = 'm'
            # 布局方案
            data_info, layout_info, propose_info, region_info, \
            group_info, scene_info, route_info, view_info = {}, {}, {}, {}, {}, {}, {}, {}
            if len(sample_scene) > 0:
                data_info, layout_info, propose_info, scene_info, route_info = \
                    layout_scene_room(room_data, group_sample, sample_scene,
                                      deco_mode=2, view_mode=view_mode, path_mode=path_mode)
            elif len(room_sample) > 0:
                data_info, layout_info, propose_info, region_info, region_info, scene_info, route_info = \
                    layout_sample_room(room_data, room_sample, room_replace, note_replace, layout_num, style_mode,
                                       house_id=target_id, deco_mode=2, view_mode=view_mode, path_mode=path_mode, clear_mode=clear_mode)
            elif layout_mode == LAYOUT_MODE_ADVICE:
                if len(room_data) > 0:
                    data_info, layout_info, propose_info, region_info = layout_advice_room(room_data, layout_num)
                elif len(house_data) > 0:
                    data_info, layout_info, propose_info, region_info = layout_advice_house(house_data, layout_num)
            elif layout_mode == LAYOUT_MODE_GROUP:
                if len(room_data) > 0 and 'furniture_info' in room_data:
                    data_info, scheme_info, group_info = group_room(room_data)
            elif layout_mode == LAYOUT_MODE_CAMERA:
                if len(room_data) > 0:
                    layout_camera_room(room_data, scheme_mode)
            else:
                data_info, layout_info, propose_info, region_info, scene_info, route_info = \
                    layout_sample_room(room_data, room_sample, room_replace, note_replace, layout_num, style_mode,
                                       house_id=target_id, deco_mode=2, view_mode=view_mode, path_mode=path_mode, clear_mode=clear_mode)
            # 组装信息
            if 'room' not in house_data:
                house_data = {'id': house_id, 'room': []}
            if len(house_data['room']) <= 0:
                house_data['room'].append(data_info)
            house_data_info = house_data
            room_data_info = data_info
            room_layout_info = layout_info
            room_propose_info = propose_info
            room_region_info = region_info
            room_group_info = group_info
            room_scene_info = scene_info
            room_route_info = route_info
            if len(layout_info) > 0:
                house_layout_info[room_id] = layout_info
            if len(propose_info) > 0:
                house_propose_info[room_id] = propose_info
            if len(region_info) > 0:
                house_region_info[room_id] = region_info
            if len(group_info) > 0:
                house_group_info[room_id] = group_info
        # 全屋布局
        elif len(house_data) > 0 and 'room' in house_data:
            if 'id' in house_data and house_id == '':
                house_id = house_data['id']
            if 'room' in house_data:
                for room_one in house_data['room']:
                    if 'coordinate' not in room_one:
                        room_one['coordinate'] = 'xzy'
                    if 'unit' not in room_one:
                        room_one['unit'] = 'm'
            # 布局方案
            data_info, layout_info, propose_info, region_info, \
            group_info, scene_info, route_info, view_info = {}, {}, {}, {}, {}, {}, {}, {}
            if len(house_sample) > 0:
                data_info, layout_info, propose_info, region_info, scene_info, route_info = \
                    layout_sample_house(house_data, house_sample, house_replace, note_replace, layout_num, style_mode,
                                        deco_mode=2, view_mode=view_mode, path_mode=path_mode, clear_mode=clear_mode)
            elif layout_mode == LAYOUT_MODE_ADVICE:
                if len(room_data) > 0:
                    data_info, layout_info, propose_info, region_info = layout_advice_room(room_data, layout_num)
                elif len(house_data) > 0:
                    data_info, layout_info, propose_info, region_info = layout_advice_house(house_data, layout_num)
            elif layout_mode == LAYOUT_MODE_GROUP:
                data_info, layout_info, group_info = layout_group_house(house_data)
            elif layout_mode == LAYOUT_MODE_CAMERA:
                if len(room_data) > 0:
                    layout_camera_room(room_data, scheme_mode)
                elif len(house_data) > 0:
                    data_info, layout_info, view_info = layout_camera_house(house_data, scheme_mode)
            elif len(sample_scene_list) > 0:
                # 解析
                sample_data, sample_layout, sample_group, sample_scene = parse_sample_list(sample_scene_list)
                if len(sample_house) <= 0 and 'id' in sample_data:
                    sample_house = sample_data['id']
                sample_data_info, sample_layout_info, sample_scene_info = sample_data, sample_layout, sample_scene
                # 布局
                data_info, layout_info, propose_info, region_info, scene_info, route_info = \
                    layout_sample_house(house_data, sample_layout, house_replace, note_replace, layout_num, style_mode,
                                        deco_mode=2, view_mode=view_mode, path_mode=path_mode, clear_mode=clear_mode)
            elif len(sample_info) <= 0 and len(sample_house) > 0:
                layout_num = 1
                # 解析
                sample_data, sample_layout, sample_group, sample_scene = parse_sample_id(sample_house)
                sample_data_info, sample_layout_info, sample_scene_info = sample_data, sample_layout, sample_scene
                # 布局
                data_info, layout_info, propose_info, region_info, scene_info, route_info = \
                    layout_sample_house(house_data, sample_layout, house_replace, note_replace, layout_num, style_mode,
                                        deco_mode=2, view_mode=view_mode, path_mode=path_mode, clear_mode=clear_mode)
            else:
                data_info, layout_info, propose_info, region_info, scene_info, route_info = \
                    layout_sample_house(house_data, house_sample, house_replace, note_replace, layout_num, style_mode,
                                        deco_mode=2, view_mode=view_mode, path_mode=path_mode, clear_mode=clear_mode)
            # 组装信息
            house_data_info = data_info
            house_layout_info = layout_info
            house_propose_info = propose_info
            house_region_info = region_info
            house_group_info = group_info
            house_scene_info = scene_info
            house_route_info = route_info
            house_view_info = view_info

        # 特征分析
        if len(sample_info) > 0 and len(sample_group) > 0 and layout_mode in [LAYOUT_MODE_ADVICE]:
            sample_vector = parse_vector_sample(sample_group)
            if len(group_vector) <= 0 and len(sample_vector) >= 1:
                for vector_one in sample_vector.values():
                    group_vector = vector_one
                    break

        # 打印信息
        layout_log_0 = 'layout success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        # 保存信息
        if len(save_mode) > 0:
            if not scene_path == '' and not os.path.exists(scene_path):
                if not scene_url == '':
                    scene_path = house_scene_path(scene_url, house_id, '', DATA_DIR_SERVER_INPUT)
            save_id = house_id
            if save_id == '':
                if len(house_layout_info) <= 0:
                    save_id = 'null'
                elif len(house_layout_info) == 1:
                    save_id = 'room'
                else:
                    save_id = 'house'
            if len(sample_scene) > 0 and 'id' in sample_scene:
                if len(room_id) > 0:
                    save_id += ('_' + room_id)
                save_id += ('_' + sample_scene['id'])
            if SAVE_MODE_IMAGE in save_mode or SAVE_MODE_FRAME in save_mode:
                save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
                if 'local' in scheme_mode:
                    save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, 'local')
                if 'region' in scheme_mode:
                    house_save_region(house_id, scene_path, layout_num, 0,
                               house_data_info, house_layout_info, house_propose_info, house_region_info,
                               save_id, save_dir, save_mode, suffix_flag=False, sample_flag=True, upload_flag=False)
                else:
                    house_save(house_id, scene_path, layout_num, 0,
                               house_data_info, house_layout_info, house_propose_info,
                               save_id, save_dir, save_mode, suffix_flag=False, sample_flag=True, upload_flag=False)
                if len(sample_scene_list) == 1 and len(sample_data_info) > 0:
                    house_save(sample_house, '', 1, 1,
                               sample_data_info, sample_layout_info, {},
                               sample_house + '_sample', save_dir, [SAVE_MODE_FRAME],
                               suffix_flag=False, sample_flag=False, upload_flag=False)
                    scene_url = sample_scene_list[0]
                    if os.path.exists(scene_url) and scene_url.endswith('.json'):
                        scene_json = json.load(open(scene_url, 'r'))
                    else:
                        response_info = requests.get(scene_url, timeout=1)
                        response_json = response_info.json()
                        scene_json = response_json
                    if len(scene_json) > 0:
                        json_path = os.path.join(save_dir, sample_house + '_sample_scene.json')
                        with open(json_path, "w") as f:
                            # json.dump(scene_json, f, indent=4)
                            json.dump(scene_json, f)
                            f.close()
            if SAVE_MODE_GROUP in save_mode:
                save_dir = layout_sample_mkdir(DATA_DIR_SERVER_GROUP, save_id)
                upload_group, upload_room = False, False
                group_save(house_group_info, save_id, save_dir, 10, 15, save_mode, upload_group, upload_room)
                pass

        # 打印信息
        layout_log_0 = 'layout success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
    except Exception as e:
        house_layout_info = {}
        # 错误信息
        layout_log_0 = 'layout error ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        # 错误信息
        layout_log_e = str(e)
        layout_log_update(layout_log_e)
        layout_log_e = str(traceback.format_exc())
        layout_log_update(layout_log_e)
        # 保存日志
        log_loc = layout_sample_host()
        log_dir = 'layout_sample'
        if len(log_loc) > 0:
            log_dir = log_loc + '/layout_sample'
        save_id = house_id
        if save_id == '':
            if len(house_layout_info) <= 0:
                save_id = 'null'
            elif len(house_layout_info) == 1:
                save_id = 'room'
            else:
                save_id = 'house'
        layout_log_upload(log_dir, save_id, log_mod=0)

    # 计数信息
    layout_sample_count()

    # 输出处理
    layout_log, house_vector, room_vector, sample_dict = '', {}, [], {}
    for room_key, room_val in house_layout_info.items():
        if 'layout_scheme' not in room_val:
            continue
        layout_log += (' ' + room_key)
        if 'room_type' not in room_val:
            continue
        scheme_list, scheme_max = room_val['layout_scheme'], {}
        # 单屋模板
        sample_key_list = []
        for scheme_idx, scheme_one in enumerate(scheme_list):
            source_house, source_room = '', ''
            if 'source_house' in scheme_one:
                source_house = scheme_one['source_house']
            if 'source_room' in scheme_one:
                source_room = scheme_one['source_room']
            if len(source_house) > 0 and len(source_room) > 0:
                sample_key_list.append(source_house + '_' + source_room)
        sample_dict[room_key] = sample_key_list
        # 单屋方案
        room_type, group_list, vector_new = '', [], []
        if 'room_type' in room_val:
            room_type = room_val['room_type']
        for scheme_idx, scheme_one in enumerate(scheme_list):
            if len(scheme_max) <= 0:
                scheme_max = scheme_one
            elif 'group' in scheme_max and 'group' in scheme_one:
                group_list_old, group_list_new = scheme_max['group'], scheme_one['group']
                group_best_old, group_best_new = 0, 0
                for group_one in group_list_old:
                    group_type, group_size = group_one['type'], group_one['size']
                    if 'regulation' in group_one:
                        group_next = group_one['regulation']
                        group_size[0] += group_next[1]
                        group_size[0] += group_next[3]
                        group_size[2] += group_next[0]
                        group_size[2] += group_next[2]
                    if group_type in ['Media']:
                        group_best_old += 10
                    elif group_type in ['Dining'] and room_type in ['LivingRoom']:
                        pass
                    elif group_type in GROUP_TYPE_MAIN:
                        group_best_old += 100
                    elif group_type in ['Armoire', 'Cabinet'] and min(group_size[0], group_size[1]) > 0.8:
                        group_best_old += 20
                        group_best_old += group_size[0]
                    elif group_type in GROUP_TYPE_REST:
                        group_best_old += 10
                for group_one in group_list_new:
                    group_type, group_size = group_one['type'], group_one['size']
                    if 'regulation' in group_one:
                        group_next = group_one['regulation']
                        group_size[0] += group_next[1]
                        group_size[0] += group_next[3]
                        group_size[2] += group_next[0]
                        group_size[2] += group_next[2]
                    if group_type in ['Media']:
                        group_best_new += 1
                    elif group_type in ['Dining'] and room_type in ['LivingRoom']:
                        pass
                    elif group_type in GROUP_TYPE_MAIN:
                        group_best_new += 100
                    elif group_type in ['Armoire', 'Cabinet'] and min(group_size[0], group_size[1]) > 0.8:
                        group_best_new += 20
                        group_best_new += group_size[0]
                    elif group_type in GROUP_TYPE_REST:
                        group_best_new += 10
                if group_best_new > group_best_old:
                    scheme_max = scheme_one
            pass
        if 'group' in scheme_max:
            room_type, group_list = room_val['room_type'], scheme_max['group']
        if len(room_type) <= 0 and 'room_type' in room_val:
            room_type = room_val['room_type']
        vector_new = compute_room_vector(group_list, room_type)
        # 全屋特征
        house_vector[room_key] = vector_new
        # 单屋特征
        if room_key == room_id:
            room_vector = vector_new
    layout_version = '20211203.1100'
    layout_output = {
        'house_id': house_id,
        'room_id': room_id,
        'house_data': house_data_info,
        'room_data': room_data_info,
        'house_layout': house_layout_info,
        'room_layout': room_layout_info,
        'house_group': house_group_info,
        'room_group': room_group_info,
        'room_scene': room_scene_info,
        'house_scene': house_scene_info,
        'layout_version': layout_version
    }

    # 特征信息
    if layout_mode in [LAYOUT_MODE_ADVICE]:
        layout_output = {
            'house_id': house_id,
            'room_id': room_id,
            'house_data': {},
            'house_feature': house_vector,
            'room_feature': room_vector,
            'scene_feature': group_vector,
            'sample_feature': sample_vector,
            'layout_version': layout_version
        }
        if 'data' in scheme_mode:
            layout_output['house_data'] = house_data_info
    elif layout_mode in [LAYOUT_MODE_CAMERA]:
        layout_output = {
            'house_id': house_id,
            'house_view': house_view_info,
            'house_item': [],
            'layout_version': layout_version
        }
        if 'board' in scheme_mode:
            layout_output = {
                'house_id': house_id,
                'house_view': {},
                'house_item': [],
                'layout_version': layout_version
            }
        if 'house_item' in param_info:
            house_item_info = param_info['house_item']
            house_item_sort = parse_anchor_item(house_item_info, house_view_info)
            layout_output['house_item'] = house_item_sort
    # 场景信息
    elif len(room_scene_info) > 0 or len(house_scene_info) > 0 or len(sample_scene_list) > 0:
        house_scene_json = {}
        # 返回信息
        layout_output = {
            'house_id': house_id,
            'room_id': room_id,
            'image_key': [],
            'scene_info': [],
            'scene_feature': group_vector,
            'layout_sample': {},
            'layout_version': layout_version
        }
        if 'sample' in scheme_mode:
            layout_output['layout_sample'] = sample_dict
        # 房间别名
        room_alias = {}
        if len(house_data_info) > 0 and 'room' in house_data_info:
            room_list = house_data_info['room']
            for room_idx, room_one in enumerate(room_list):
                room_key, room_ali = room_one['id'], room_one['id']
                if 'alias' in room_one:
                    room_ali = room_one['alias']
                if len(room_key) > 0 and len(room_ali) > 0:
                    room_alias[room_key] = room_ali
        if len(room_data_info) > 0:
            room_one = room_data_info
            room_key, room_ali = room_one['id'], room_one['id']
            if 'alias' in room_one:
                room_ali = room_one['alias']
            if len(room_key) > 0 and len(room_ali) > 0:
                room_alias[room_key] = room_ali

        # 单屋重建
        if len(room_scene_info) > 0:
            save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, house_id)
            if len(room_data_info) > 0 and len(room_layout_info) > 0:
                room_data_each, room_layout_each = room_data_info, room_layout_info
                room_scheme_each = {}
                if 'layout_scheme' in room_layout_each and len(room_layout_each['layout_scheme']) > 0:
                    room_scheme_each = room_layout_each['layout_scheme'][0]
                # 方案信息
                room_style_each = ''
                if 'style' in room_scheme_each:
                    room_style_each = room_scheme_each['style']
                # 户型重建
                room_build_mode = {}
                if 'no_ceiling' in struct_mode:
                    room_build_mode['customized_ceiling'] = False
                mid_wall = {}
                if 'mid_wall' in house_data_info:
                    mid_wall = house_data_info['mid_wall']
                house_scene_json, house_scene_outdoor = \
                    house_build_room(room_data_each, room_layout_each, room_style_each, room_mode=room_build_mode,
                                     house_id=house_id, mid_wall=mid_wall)

                # 户型保存
                save_time = datetime.datetime.now().strftime('%H-%M-%S')
                save_id = house_id + '_%s' % save_time
                json_path = os.path.join(save_dir, save_id + '.json')
                with open(json_path, "w") as f:
                    # json.dump(house_scene_json, f, indent=4)
                    json.dump(house_scene_json, f)
                    f.close()
                # 户型上传
                scene_key = house_scene_upload(house_scene_json, save_id, json_path)
                # 户型机位
                if len(scene_key) > 0:
                    house_scene_detail = {'url': scene_key, 'room': []}
                    # 方案信息
                    room_type_each, room_style_each, room_group_each = '', '', ''
                    # 物品信息
                    room_object_each, room_object_dict = [], {}
                    room_object_main, room_object_style = '', ''
                    # 机位信息
                    room_camera_each, room_vision_each, room_wander_each = {}, [], []
                    room_background_each, room_outdoor_each = [], ''
                    # 模板信息
                    room_scene_house, room_scene_room = '', ''

                    # 方案信息
                    if 'type' in room_scheme_each:
                        room_type_each = room_scheme_each['type']
                    if 'style' in room_scheme_each:
                        room_style_each = room_scheme_each['style']
                    room_group_list = room_scheme_each['group']
                    for group_one in room_group_list:
                        room_object_list = group_one['obj_list']
                        for object_one in room_object_list:
                            object_key = object_one['id']
                            object_ref = {}
                            object_ref = parse_object_data(object_one, group_one, room_type_each)
                            room_object_each.append(object_key)
                            if len(object_ref) > 0:
                                room_object_dict[object_key] = object_ref
                            if len(room_object_main) <= 0:
                                room_object_main = object_key
                            elif 'role' in object_one and object_one['role'] in ['sofa', 'bed']:
                                room_object_main = object_key
                    # 机位列表
                    room_scene_list, room_wander_list, room_camera_list = [], [], []
                    if 'wander' in room_scheme_each:
                        room_wander_list = room_scheme_each['wander']
                    if len(room_wander_list) > 0:
                        camera_list = room_wander_list[0]
                        for camera_one in camera_list:
                            room_wander_each.append(camera_one)
                    room_scene_each = room_scene_info
                    # 房间视角
                    if 'camera' in room_scene_each:
                        room_camera_each = room_scene_each['camera']
                    if 'vision' in room_scene_each:
                        room_vision_each = room_scene_each['vision']
                    if 'intersect' in room_scene_each:
                        room_data_each['intersect'] = room_scene_each['intersect']
                    # 房间物品
                    if 'object' in room_scene_each and len(room_scene_each['object']) > 0:
                        room_object_main = room_scene_each['object']
                    if len(room_object_main) > 0:
                        type_id, style_id, category_id = get_furniture_data_refer_id(room_object_main)
                        room_object_style = style_id
                    # 房间外景
                    if 'outdoor' in room_scene_each:
                        room_outdoor_each = room_scene_each['outdoor']
                    if len(house_scene_outdoor) > 0:
                        room_outdoor_each = house_scene_outdoor
                    if len(room_outdoor_each) <= 0:
                        room_outdoor_each = 'sea_sky'
                    # 房间模板
                    if 'source_house' in room_scheme_each:
                        room_scene_house = room_scheme_each['source_house']
                    if 'source_room' in room_scheme_each:
                        room_scene_room = room_scheme_each['source_room']
                    # 房间锚点
                    room_anchor_base = {}
                    if 'camera' in room_scene_each:
                        room_anchor_base = room_scene_each['camera']
                    room_anchor_hard, room_anchor_soft = [], []
                    room_anchor_link, room_anchor_door = [], []
                    room_board_wall, room_board_ceil, room_board_floor = [], [], []
                    if 'anchor_hard' in room_scene_each:
                        room_anchor_hard = room_scene_each['anchor_hard']
                        if len(room_anchor_hard) > 0 and 'position' in room_anchor_hard[0]:
                            room_background_each = room_anchor_hard[0]['position']
                    if 'anchor_soft' in room_scene_each:
                        room_anchor_soft = room_scene_each['anchor_soft']
                    if 'anchor_link' in room_scene_each:
                        anchor_set = room_scene_each['anchor_link']
                        for anchor_one in anchor_set:
                            anchor_new = anchor_one.copy()
                            if 'position_fix' in anchor_new:
                                anchor_new['position'] = anchor_new['position_fix'][:]
                                anchor_new.pop('position_fix')
                            anchor_key = anchor_one['id']
                            if anchor_key in room_alias:
                                anchor_new['id'] = room_alias[anchor_key]
                            room_anchor_link.append(anchor_new)
                    if 'anchor_door' in room_scene_each:
                        anchor_set = room_scene_each['anchor_door']
                        for anchor_one in anchor_set:
                            anchor_new = anchor_one.copy()
                            if 'position_fix' in anchor_new:
                                anchor_new['position'] = anchor_new['position_fix'][:]
                                anchor_new.pop('position_fix')
                            anchor_key = anchor_one['link_id']
                            if anchor_key in room_alias:
                                anchor_new['link_id'] = room_alias[anchor_key]
                            anchor_key = anchor_one['link_id_2']
                            if anchor_key in room_alias:
                                anchor_new['link_id_2'] = room_alias[anchor_key]
                            room_anchor_door.append(anchor_new)
                    if 'board_wall' in room_scheme_each:
                        room_board_wall = room_scheme_each['board_wall']
                    if 'board_ceiling' in room_scheme_each:
                        room_board_ceil = room_scheme_each['board_ceiling']
                    if 'board_floor' in room_scheme_each:
                        room_board_floor = room_scheme_each['board_floor']
                    room_camera_more = {
                        'camera': room_anchor_base,
                        'anchor_hard': room_anchor_hard,
                        'anchor_soft': room_anchor_soft,
                        'anchor_room': room_anchor_link
                    }
                    room_camera_list.append(room_camera_more)
                    # 房间添加
                    room_key = room_data_each['id']
                    room_ali = room_key
                    if room_key in room_alias:
                        room_ali = room_alias[room_key]
                    room_scene_detail = {
                        'id': room_ali,
                        'size': room_layout_each['room_area'],
                        'type': room_layout_each['room_type'],
                        'style': room_style_each,
                        'camera': room_camera_each,
                        'camera_more': room_camera_list,
                        'anchor_door': room_anchor_door,
                        'board_wall': room_board_wall,
                        'board_ceiling': room_board_ceil,
                        'board_floor': room_board_floor,
                        'vision': room_vision_each,
                        'wander': room_wander_each,
                        'object': room_object_each,
                        'anchor': room_object_dict,
                        'background': room_background_each,
                        'outdoor': room_outdoor_each,
                        'source_house': room_scene_house,
                        'source_room': room_scene_room,
                        'source_object': room_object_main,
                        'source_style': room_object_style
                    }
                    house_scene_detail['room'].append(room_scene_detail)
                    layout_output['scene_info'].append(house_scene_detail)
                pass
                # 方案出图
                if len(scene_key) > 0:
                    # 渲染标识
                    save_id = house_id
                    if save_id == '':
                        if len(house_layout_info) <= 0:
                            save_id = 'null'
                        elif len(house_layout_info) == 1:
                            save_id = 'room'
                        else:
                            save_id = 'house'
                    if len(sample_scene) > 0 and 'id' in sample_scene:
                        room_scheme_time = datetime.datetime.now().strftime('%H-%M-%S')
                        if len(room_id) > 0:
                            save_id += '_%s_%s' % (room_id, room_scheme_time)
                        save_id += '_%s_%s' % (sample_scene['id'], room_scheme_time)
                    # 渲染处理
                    if 'camera' in room_scene_info and (SAVE_MODE_RENDER in save_mode):
                        room_scene_each = room_scene_info
                        room_wander_list, room_wander_each = [], []
                        if 'wander' in room_scheme_each:
                            room_wander_list = room_scheme_each['wander']
                        if len(room_wander_list) > 0:
                            camera_list = room_wander_list[0]
                            for camera_one in camera_list:
                                room_wander_each.append(camera_one)
                        # 渲染参数
                        render_key = ''
                        camera_param, render_key, render_val = room_scene_each['camera'], '', {}
                        outdoor_type = ''
                        if 'outdoor' in room_scene_each:
                            outdoor_type = room_scene_each['outdoor']
                        # 渲染处理
                        if len(house_scene_json) > 0:
                            render_id = save_id
                            render_key, render_val = house_scene_render(render_id, house_scene_json,
                                                                        camera_param, outdoor_type, view_mode, save_dir)
                        # 打印信息
                        if len(render_val) > 0:
                            layout_log_0 = 'render success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            layout_log_update(layout_log_0)
                        else:
                            layout_log_0 = 'render failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            layout_log_update(layout_log_0)
                        # 添加渲染
                        if len(render_key) > 0:
                            layout_output['image_key'].append(render_key)
                    # 打印信息
                    layout_log_0 = 'render end ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                    layout_log_update(layout_log_0)
        # 全屋重建
        elif len(house_scene_info) > 0:
            save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, house_id)
            if len(house_data_info) > 0 and len(house_layout_info) > 0:
                # 方案遍历
                house_style_list, house_build_dict = [], {}
                for layout_idx in range(layout_num):
                    # 户型方案
                    house_data_copy = house_data_info.copy()
                    house_layout_copy, house_style_each, house_build_mode = {}, '', {}
                    # 户型房间
                    room_list_old, room_list_new = [], []
                    if 'room' in house_data:
                        room_list_old = house_data['room']
                    for room_old in room_list_old:
                        room_new = room_old.copy()
                        room_new['furniture_info'] = []
                        room_list_new.append(room_new)
                    house_data_copy['room'] = room_list_new
                    house_data_copy['style'] = ''
                    # 户型布局
                    room_style_main, room_style_rest, room_style_last = '', '', ''
                    for room_key, room_val in house_layout_info.items():
                        room_layout_new = room_val.copy()
                        room_sample_set, room_scheme_set = [], []
                        if 'layout_sample' in room_val:
                            room_sample_set = room_val['layout_sample']
                        if 'layout_scheme' in room_val:
                            room_scheme_set = room_val['layout_scheme']
                        if len(room_sample_set) > 0:
                            room_sample_one = room_sample_set[layout_idx % len(room_sample_set)]
                            room_layout_new['layout_sample'] = [room_sample_one]
                        if len(room_scheme_set) > 0:
                            room_scheme_one = room_scheme_set[layout_idx % len(room_scheme_set)]
                            room_layout_new['layout_scheme'] = [room_scheme_one]
                            house_layout_copy[room_key] = room_layout_new
                            if 'type' in room_scheme_one and 'style' in room_scheme_one and len(house_style_each) <= 0:
                                room_type, room_style = room_scheme_one['type'], room_scheme_one['style']
                                if len(room_style) <= 0:
                                    pass
                                elif room_type in ['LivingDiningRoom', 'LivingRoom']:
                                    room_style_main = room_style
                                    house_style_each = room_style
                                elif room_type in ['DiningRoom', 'Library'] or room_type in ROOM_TYPE_LEVEL_2:
                                    room_style_rest = room_style
                                elif len(house_style_each) <= 0:
                                    room_style_last = room_style
                    if len(room_style_main) > 0:
                        house_style_each = get_furniture_style_en(room_style_main)
                    elif len(room_style_rest) > 0:
                        house_style_each = get_furniture_style_en(room_style_rest)
                    elif len(room_style_last) > 0:
                        house_style_each = get_furniture_style_en(room_style_last)
                    house_style_list.append(house_style_each)
                    house_data_copy['style'] = house_style_each
                    if len(sample_scene_list) > 0:
                        house_build_mode['white_list'] = False
                        house_build_mode['bg_wall'] = False
                    if 'no_ceiling' in struct_mode:
                        house_build_mode['customized_ceiling'] = False
                    # 户型软装
                    house_data_copy['layout'] = {}
                    # 户型硬装 户型重建
                    layout_log_0 = 'build begin ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                    layout_log_update(layout_log_0)
                    house_scene_json, house_scene_outdoor = house_build_house(house_data_copy, house_layout_copy,
                                                                              house_style_each, house_build_mode)
                    layout_log_0 = 'build end ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                    layout_log_update(layout_log_0)
                    # 户型软装
                    house_data_copy['layout'] = house_layout_copy
                    # 户型保存
                    layout_log_0 = 'upload begin ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                    layout_log_update(layout_log_0)
                    save_time = datetime.datetime.now().strftime('%H-%M-%S')
                    save_id = house_id + '_%s_%d' % (save_time, layout_idx)
                    json_path = os.path.join(save_dir, save_id + '.json')
                    with open(json_path, "w") as f:
                        # json.dump(house_scene_json, f, indent=4)
                        json.dump(house_scene_json, f)
                        f.close()
                    # 户型上传
                    scene_key = house_scene_upload(house_scene_json, save_id, json_path)
                    layout_log_0 = 'upload end ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                    layout_log_update(layout_log_0)
                    # 户型记录
                    house_build_dict[layout_idx] = scene_key
                    # 户型机位 户型点位
                    if len(scene_key) > 0:
                        house_scene_detail = {'url': scene_key, 'room': []}
                        for room_key, room_val in house_layout_copy.items():
                            room_layout_each = room_val
                            # 方案信息
                            room_type_each, room_style_each, room_group_each = '', '', ''
                            # 物品信息
                            room_object_each, room_object_dict = [], {}
                            room_object_main, room_object_style = '', ''
                            # 机位信息
                            room_camera_each, room_vision_each, room_wander_each = {}, [], []
                            room_background_each, room_outdoor_each = [], ''
                            # 模板信息
                            room_scene_house, room_scene_room = '', ''
                            if 'layout_scheme' in room_layout_each and len(room_layout_each['layout_scheme']) > 0:
                                room_scheme_each = room_layout_each['layout_scheme'][0]
                                if 'group' not in room_scheme_each:
                                    continue
                                if 'scene' not in room_scheme_each:
                                    continue
                                # 方案信息
                                if 'type' in room_scheme_each:
                                    room_type_each = room_scheme_each['type']
                                if 'style' in room_scheme_each:
                                    room_style_each = room_scheme_each['style']
                                room_group_list = room_scheme_each['group']
                                for group_one in room_group_list:
                                    room_object_list = group_one['obj_list']
                                    for object_one in room_object_list:
                                        object_key = object_one['id']
                                        object_ref = {}
                                        object_ref = parse_object_data(object_one, group_one, room_type_each)
                                        room_object_each.append(object_key)
                                        room_object_dict[object_key] = object_ref
                                        if len(room_object_main) <= 0:
                                            room_object_main = object_key
                                        elif 'role' in object_one and object_one['role'] in ['sofa', 'bed']:
                                            room_object_main = object_key
                                # 机位列表
                                room_scene_list, room_wander_list, room_camera_list = [], [], []
                                if 'scene' in room_scheme_each:
                                    room_scene_list = room_scheme_each['scene']
                                # 点位列表
                                if 'wander' in room_scheme_each:
                                    room_wander_list = room_scheme_each['wander']
                                if len(room_wander_list) > 0:
                                    camera_list = room_wander_list[0]
                                    for camera_one in camera_list:
                                        room_wander_each.append(camera_one)
                                # 房间别名
                                room_ali = room_key
                                if room_key in room_alias:
                                    room_ali = room_alias[room_key]
                                room_anchor_door = []
                                room_board_wall, room_board_ceil, room_board_floor = [], [], []
                                # 遍历机位
                                for room_scene_idx, room_scene_each in enumerate(room_scene_list):
                                    # 主要信息
                                    if room_scene_idx <= 0:
                                        # 房间机位
                                        if 'camera' in room_scene_each:
                                            room_camera_each = room_scene_each['camera']
                                        if 'vision' in room_scene_each:
                                            room_vision_each = room_scene_each['vision']
                                        # 房间物品
                                        if 'object' in room_scene_each and len(room_scene_each['object']) > 0:
                                            room_object_main = room_scene_each['object']
                                        if len(room_object_main) > 0:
                                            type_id, style_id, category_id = get_furniture_data_refer_id(
                                                room_object_main)
                                            if style_id == '':
                                                type_old, style_old, size_old = get_furniture_data(room_object_main)
                                                style_id = get_furniture_style_id(style_old)
                                            room_object_style = style_id
                                        # 房间外景
                                        if 'outdoor' in room_scene_each:
                                            room_outdoor_each = room_scene_each['outdoor']
                                        if len(house_scene_outdoor) > 0:
                                            room_outdoor_each = house_scene_outdoor
                                        if len(room_outdoor_each) <= 0:
                                            room_outdoor_each = 'sea_sky'
                                        # 房间模板
                                        if 'source_house' in room_scheme_each:
                                            room_scene_house = room_scheme_each['source_house']
                                        if 'source_room' in room_scheme_each:
                                            room_scene_room = room_scheme_each['source_room']
                                    # 房间锚点
                                    room_anchor_base = {}
                                    if 'camera' in room_scene_each:
                                        room_anchor_base = room_scene_each['camera']
                                    room_anchor_hard, room_anchor_soft = [], []
                                    room_anchor_link, room_anchor_door = [], []
                                    room_board_wall, room_board_ceil, room_board_floor = [], [], []
                                    if 'anchor_hard' in room_scene_each:
                                        room_anchor_hard = room_scene_each['anchor_hard']
                                        if len(room_anchor_hard) > 0 and 'position' in room_anchor_hard[0]:
                                            room_background_each = room_anchor_hard[0]['position']
                                    if 'anchor_soft' in room_scene_each:
                                        room_anchor_soft = room_scene_each['anchor_soft']
                                    if 'anchor_link' in room_scene_each:
                                        anchor_set = room_scene_each['anchor_link']
                                        for anchor_one in anchor_set:
                                            anchor_new = anchor_one.copy()
                                            if 'position_fix' in anchor_new:
                                                anchor_new['position'] = anchor_new['position_fix'][:]
                                                anchor_new.pop('position_fix')
                                            anchor_key = anchor_one['id']
                                            if anchor_key in room_alias:
                                                anchor_new['id'] = room_alias[anchor_key]
                                            room_anchor_link.append(anchor_new)
                                    if 'anchor_door' in room_scene_each:
                                        anchor_set = room_scene_each['anchor_door']
                                        for anchor_one in anchor_set:
                                            anchor_new = anchor_one.copy()
                                            if 'position_fix' in anchor_new:
                                                anchor_new['position'] = anchor_new['position_fix'][:]
                                                anchor_new.pop('position_fix')
                                            anchor_key = anchor_one['link_id']
                                            if anchor_key in room_alias:
                                                anchor_new['link_id'] = room_alias[anchor_key]
                                            anchor_key = anchor_one['link_id_2']
                                            if anchor_key in room_alias:
                                                anchor_new['link_id_2'] = room_alias[anchor_key]
                                            room_anchor_door.append(anchor_new)
                                    if 'board_wall' in room_scheme_each:
                                        room_board_wall = room_scheme_each['board_wall']
                                    if 'board_ceiling' in room_scheme_each:
                                        room_board_ceil = room_scheme_each['board_ceiling']
                                    if 'board_floor' in room_scheme_each:
                                        room_board_floor = room_scheme_each['board_floor']
                                    room_camera_more = {
                                        'camera': room_anchor_base,
                                        'anchor_hard': room_anchor_hard,
                                        'anchor_soft': room_anchor_soft,
                                        'anchor_room': room_anchor_link
                                    }
                                    room_camera_list.append(room_camera_more)
                                # 房间添加
                                if len(room_scene_list) > 0:
                                    room_scene_detail = {
                                        'id': room_ali,
                                        'size': room_layout_each['room_area'],
                                        'type': room_layout_each['room_type'],
                                        'style': room_style_each,
                                        'camera': room_camera_each,
                                        'camera_more': room_camera_list,
                                        'anchor_door': room_anchor_door,
                                        'board_wall': room_board_wall,
                                        'board_ceiling': room_board_ceil,
                                        'board_floor': room_board_floor,
                                        'vision': room_vision_each,
                                        'wander': room_wander_each,
                                        'object': room_object_each,
                                        'anchor': room_object_dict,
                                        'background': room_background_each,
                                        'outdoor': room_outdoor_each,
                                        'source_house': room_scene_house,
                                        'source_room': room_scene_room,
                                        'source_object': room_object_main,
                                        'source_style': room_object_style
                                    }
                                    house_scene_detail['room'].append(room_scene_detail)
                        # 添加机位
                        layout_output['scene_info'].append(house_scene_detail)
                    pass
                # 打印信息
                layout_log_0 = 'render begin ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                layout_log_update(layout_log_0)
                # 方案出图
                for room_one in house_data_info['room']:
                    if SAVE_MODE_RENDER in save_mode:
                        pass
                    else:
                        break
                    room_key = room_one['id']
                    room_type = room_one['type']
                    if room_key not in house_layout_info:
                        continue
                    room_data_each, room_layout_each = room_one, house_layout_info[room_key]
                    room_scheme_list = room_layout_each['layout_scheme']
                    if len(room_scheme_list) <= 0:
                        continue
                    if room_key in house_scene_info:
                        pass
                    elif 'wander_origin' in room_scheme_list[0]:
                        pass
                    else:
                        continue
                    if len(render_room) > 0 and room_type not in render_room:
                        continue
                    for layout_idx in range(layout_num):
                        # 方案信息
                        room_scheme_idx = layout_idx
                        room_scheme_each = room_scheme_list[room_scheme_idx % len(room_scheme_list)]
                        room_layout_copy = room_layout_each.copy()
                        room_layout_copy['layout_scheme'] = [room_scheme_each]
                        # 机位列表
                        room_scene_list = []
                        if 'scene' in room_scheme_each:
                            room_scene_list = room_scheme_each['scene']
                        if len(room_scene_list) > 0:
                            room_scene_each = room_scene_list[0]
                        else:
                            room_scene_each = DEFAULT_SCENE_INFO.copy()
                        # 漫游点位
                        room_wander_list, room_wander_each = [], []
                        if 'wander' in room_scheme_each:
                            room_wander_list = room_scheme_each['wander']
                        if 'wander_origin' in room_scheme_each:
                            room_wander_list = room_scheme_each['wander_origin']
                        if len(room_wander_list) > 0:
                            camera_list = room_wander_list[0]
                            for camera_one in camera_list:
                                room_wander_each.append(camera_one)
                        # 机位调整
                        if SAVE_MODE_WANDER in save_mode and len(room_wander_each) > 0:
                            room_scene_list = []
                            for camera_idx, camera_val in enumerate(room_wander_each):
                                if camera_idx >= 10:
                                    break
                                room_scene_copy = room_scene_each.copy()
                                room_scene_copy['camera'] = camera_val
                                room_scene_list.append(room_scene_copy)
                        # 遍历渲染
                        for room_scene_idx, room_scene_each in enumerate(room_scene_list):
                            # 渲染标识
                            save_id = house_id
                            if save_id == '':
                                if len(house_layout_info) <= 0:
                                    save_id = 'null'
                                elif len(house_layout_info) == 1:
                                    save_id = 'room'
                                else:
                                    save_id = 'house'
                            if len(room_scene_each) > 0 and 'id' in room_scene_each:
                                room_scheme_time = datetime.datetime.now().strftime('%H-%M-%S')
                                if len(room_key) > 0:
                                    save_id += '_%s_%d_%d' % (room_key, room_scheme_idx, room_scene_idx)
                                else:
                                    new_key = room_scene_each['id']
                                    save_id += '_%s_%d_%d' % (new_key, room_scheme_idx, room_scene_idx)
                            # 渲染处理
                            if 'camera' in room_scene_each and (SAVE_MODE_RENDER in save_mode):
                                # 场景位置
                                render_loc = ''
                                if layout_idx in house_build_dict:
                                    render_loc = house_build_dict[layout_idx]
                                # 渲染参数
                                render_key = ''
                                camera_param, render_key, render_val = room_scene_each['camera'], '', {}
                                outdoor_type = house_scene_outdoor
                                if 'outdoor' in room_scene_each:
                                    outdoor_type = room_scene_each['outdoor']
                                # 渲染处理
                                if len(house_scene_json) > 0:
                                    render_key, render_val = house_scene_render(save_id, house_scene_json, camera_param,
                                                                                outdoor_type, view_mode, save_dir,
                                                                                render_loc)
                                # 添加信息
                                if len(render_val) > 0:
                                    layout_output['image_key'].append(render_key)
                # 打印信息
                layout_log_0 = 'render end ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                layout_log_update(layout_log_0)

    # 图片信息
    if 'result' in render_mode:
        # 位置
        save_id = house_id
        if save_id == '':
            if len(house_layout_info) <= 0:
                save_id = 'null'
            elif len(house_layout_info) == 1:
                save_id = 'room'
            else:
                save_id = 'house'
        save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        # 图片
        key_list, val_list = [], []
        if 'image_key' in layout_output:
            key_list = layout_output['image_key']
        if 'image_val' in layout_output:
            val_list = layout_output['image_val']
        time.sleep(10)
        if view_mode == VIEW_MODE_SPHERE:
            time.sleep(10)
        image_dict = house_scene_render_fetch(key_list, image_dir=save_dir)
        for val_one in val_list:
            key_one = val_one['id']
            if key_one in image_dict:
                image_one = image_dict[key_one]
                if 'url' in image_one:
                    val_one['url'] = image_one['url']
                if 'loc' in image_one:
                    val_one['loc'] = image_one['loc']
    # 输出信息
    if 'group' in scheme_mode:
        save_id = 'house'
        save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        group_save_plan(house_layout_info, save_id, save_dir)
        pass
    if 'output' in scheme_mode:
        save_id = house_id
        if save_id == '':
            if len(house_layout_info) <= 0:
                save_id = 'null'
            elif len(house_layout_info) == 1:
                save_id = 'room'
            else:
                save_id = 'house'
        if len(sample_scene) > 0 and 'id' in sample_scene:
            if len(room_id) > 0:
                save_id += ('_' + room_id)
            save_id += ('_' + sample_scene['id'])
        save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        json_path = os.path.join(save_dir, save_id + '_output.json')
        with open(json_path, "w") as f:
            json.dump(layout_output, f, indent=4)
            f.close()

    # 保存日志
    log_loc = layout_sample_host()
    log_dir = 'layout_sample'
    if len(log_loc) > 0:
        log_dir = log_loc + '/layout_sample'
    save_id = house_id
    if save_id == '':
        if len(house_layout_info) <= 0:
            save_id = 'null'
        elif len(house_layout_info) == 1:
            save_id = 'room'
        else:
            save_id = 'house'
    layout_log_upload(log_dir, save_id)

    # 返回信息
    return layout_output


# 布局户型纠正
def layout_adjust_floor(house_data, room_data):
    room_list = []
    if 'room' in house_data:
        room_list = house_data['room'][:]
    if len(room_data) > 0:
        room_list.append(room_data)
    for room_idx, room_one in enumerate(room_list):
        room_one['furniture_info'] = []
        room_one['decorate_info'] = []
    pass


# 布局服务地址
def layout_sample_host():
    global LAYOUT_SAMPLE_LOC
    if len(LAYOUT_SAMPLE_LOC) <= 0:
        host_name = socket.gethostname()
        LAYOUT_SAMPLE_LOC = host_name
    return LAYOUT_SAMPLE_LOC


# 布局服务目录
def layout_sample_mkdir(save_dir, save_id):
    save_dir_new = os.path.join(save_dir, save_id)
    if not os.path.exists(save_dir_new):
        os.makedirs(save_dir_new)
    return save_dir_new


# 布局服务计数
def layout_sample_count(count_max=1000):
    # 调用信息
    global LAYOUT_SAMPLE_CNT
    LAYOUT_SAMPLE_CNT += 1
    if LAYOUT_SAMPLE_CNT >= count_max:
        # 重置
        LAYOUT_SAMPLE_CNT = 0
        # 清空
        layout_sample_clear()


# 布局服务清空
def layout_sample_clear():
    # 清空
    if os.path.exists(DATA_DIR_SERVER_SCHEME):
        shutil.rmtree(DATA_DIR_SERVER_SCHEME)
    if os.path.exists(DATA_DIR_SERVER_SERVICE):
        shutil.rmtree(DATA_DIR_SERVER_SERVICE)
    # 重建
    if not os.path.exists(DATA_DIR_SERVER_SCHEME):
        os.makedirs(DATA_DIR_SERVER_SCHEME)
    if not os.path.exists(DATA_DIR_SERVER_SERVICE):
        os.makedirs(DATA_DIR_SERVER_SERVICE)


# 方案推荐服务
def propose_sample(room_info, room_layout, scheme_num=3, house_id='', request_log=False):
    global SAMPLE_PROPOSE_ENV
    # 房间特征
    scheme_list = room_layout['layout_scheme']
    room_id, room_type, group_list, room_vector = room_info['id'], '', [], []
    if len(scheme_list) > 0:
        scheme_one = scheme_list[0]
        if 'group' in scheme_one:
            room_type, group_list = room_layout['room_type'], scheme_one['group']
    compute_room_vector(group_list, room_type)
    if room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                     'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']:
        pass
    else:
        return []

    # 方案推荐
    sample_key_list, sample_url_list, sample_key_dict = [], [], {}
    # 推荐服务
    env = propose_sample_env()
    if 'pre' in env:
        server_url = SAMPLE_PROPOSE_PRE
        propose_data = {
            "design_id": house_id + '_' + room_id
        }
        request_data = {
            '_sid_': SAMPLE_PROPOSE_SID_PRE,
            'userId': SAMPLE_PROPOSE_USR_ID_PRE,
            'input_json': json.dumps(propose_data)
        }
    else:
        server_url = SAMPLE_PROPOSE_PRO
        propose_data = {
            "design_id": house_id + '_' + room_id
        }
        request_data = {
            'appid': SAMPLE_PROPOSE_APP_ID_PRO,
            'userId': SAMPLE_PROPOSE_USR_ID_PRO,
            'DEBUG': 'true',
            'input_json': json.dumps(propose_data)
        }
    try:
        response_info = requests.post(server_url, data=request_data)
        response_data = response_info.json()
        if 'result' in response_data and len(response_data['result']) > 0:
            if 'return_list' in response_data['result'][0]:
                response_list = response_data['result'][0]['return_list']
                for response_idx, response_one in enumerate(response_list):
                    rank_key_new = len(sample_key_list)
                    if 'rank' in response_one:
                        rank_key_new = int(response_one['rank'])
                    if 'design_id' in response_one and 'room_id' in response_one:
                        design_key, room_key = response_one['design_id'], response_one['room_id']
                        sample_key = design_key + '_' + room_key
                        # 纠正排序
                        rank_key_add = 0
                        rank_key_new += rank_key_add
                        if sample_key in sample_key_dict:
                            continue
                        sample_key_dict[sample_key] = rank_key_new
                        # 推荐排序
                        design_idx = -1
                        for sample_key_idx, sample_key_one in enumerate(sample_key_list):
                            if sample_key_one in sample_key_dict:
                                rank_key_old = sample_key_dict[sample_key_one]
                                if rank_key_new < rank_key_old:
                                    design_idx = sample_key_idx
                                    break
                        if 0 <= design_idx < len(sample_key_list):
                            sample_key_list.insert(design_idx, sample_key)
                        else:
                            sample_key_list.append(sample_key)
                    if 'output_url' in response_one:
                        sample_url_list.append(response_one['output_url'])
            # 记录日志
            if request_log:
                request_file = '%s_%s_request_good.json' % (house_id, room_id)
                request_path = os.path.join(DATA_DIR_SERVER_SERVICE, request_file)
                with open(request_path, "w") as f:
                    json.dump(propose_data, f, indent=4)
                    f.close()
                response_file = '%s_%s_response_good.json' % (house_id, room_id)
                response_path = os.path.join(DATA_DIR_SERVER_SERVICE, response_file)
                with open(response_path, "w") as f:
                    json.dump(response_data, f, indent=4)
                    f.close()
        else:
            # 记录日志
            if request_log:
                request_file = '%s_%s_request_fail.json' % (house_id, room_id)
                request_path = os.path.join(DATA_DIR_SERVER_SERVICE, request_file)
                with open(request_path, "w") as f:
                    json.dump(propose_data, f, indent=4)
                    f.close()
                response_file = '%s_%s_response_fail.json' % (house_id, room_id)
                response_path = os.path.join(DATA_DIR_SERVER_SERVICE, response_file)
                with open(response_path, "w") as f:
                    json.dump(response_data, f, indent=4)
                    f.close()
        # 筛除
        for response_idx in range(len(sample_key_list) - 1, -1, -1):
            if len(sample_key_list[response_idx]) <= 0:
                sample_key_list.pop(response_idx)
        for response_idx in range(len(sample_url_list) - 1, -1, -1):
            if len(sample_url_list[response_idx]) <= 0:
                sample_url_list.pop(response_idx)
        # 打印
        if len(sample_key_list) <= 0 and len(sample_url_list) <= 0:
            layout_log_0 = 'propose room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S') + ' failure '
            layout_log_update(layout_log_0)
            # 记录
            request_file = '%s_%s_request_fail.json' % (house_id, room_id)
            request_path = os.path.join(DATA_DIR_SERVER_SERVICE, request_file)
            with open(request_path, "w") as f:
                json.dump(propose_data, f, indent=4)
                f.close()
            response_file = '%s_%s_response_fail.json' % (house_id, room_id)
            response_path = os.path.join(DATA_DIR_SERVER_SERVICE, response_file)
            with open(response_path, "w") as f:
                json.dump(response_data, f, indent=4)
                f.close()
    except Exception as e:
        # 错误日志
        layout_log_0 = 'propose room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S') + ' failure '
        layout_log_update(layout_log_0)
        print(e)

    # 方案方案
    sample_type_list = []
    if room_type in ROOM_TYPE_LEVEL_1:
        sample_type_list = ROOM_TYPE_LEVEL_1
    elif room_type in ROOM_TYPE_LEVEL_2:
        sample_type_list = ROOM_TYPE_LEVEL_2
    elif room_type in ROOM_TYPE_LEVEL_3:
        sample_type_list = ROOM_TYPE_LEVEL_3

    # 方案解析
    sample_info_list = []
    sample_data, sample_layout, sample_group, sample_scene = {}, {}, {}, {}
    if len(sample_key_list) > 0:
        for sample_idx, sample_key in enumerate(sample_key_list):
            if len(sample_info_list) >= scheme_num:
                break
            if len(sample_key) <= 0:
                continue
            sample_data, sample_layout, sample_group, sample_scene = parse_sample_key(sample_key)
            # 房间筛选
            sample_best = {}
            for room_key, room_val in sample_layout.items():
                if len(sample_best) <= 0:
                    sample_best = room_val
                    continue
                scheme_list_old = sample_best['layout_scheme']
                scheme_list_new = room_val['layout_scheme']
                if len(scheme_list_old) <= 0 and len(scheme_list_new) > 0:
                    sample_best = room_val
                    continue
                if room_val['room_type'] in sample_type_list and len(scheme_list_new) > 0:
                    sample_best = room_val
                if room_val['room_type'] in [room_type] and len(scheme_list_new) > 0:
                    sample_best = room_val
                    break
            sample_info_list.append(sample_best)
    else:
        for sample_idx, sample_url in enumerate(sample_url_list):
            if len(sample_info_list) >= scheme_num:
                break
            if len(sample_url) <= 0:
                continue
            sample_key = ''
            if len(sample_key_list) > sample_idx:
                sample_key = sample_key_list[sample_idx]
            sample_data, sample_layout, sample_group, sample_scene = parse_sample_url(sample_url, sample_key)
            # 房间筛选
            sample_best = {}
            for room_key, room_val in sample_layout.items():
                if len(sample_best) <= 0:
                    sample_best = room_val
                    continue
                scheme_list_old = sample_best['layout_scheme']
                scheme_list_new = room_val['layout_scheme']
                if len(scheme_list_old) <= 0 and len(scheme_list_new) > 0:
                    sample_best = room_val
                    continue
                if room_val['room_type'] in sample_type_list and len(scheme_list_new) > 0:
                    sample_best = room_val
                if room_val['room_type'] in [room_type] and len(scheme_list_new) > 0:
                    sample_best = room_val
                    break
            sample_info_list.append(sample_best)

    # 方案抽取
    sample_info_fine = sample_info_list
    if len(sample_info_list) > scheme_num > 0:
        sample_info_fine = sample_info_list[0: scheme_num]
    return sample_info_fine


# 方案推荐环境
def propose_sample_env():
    global SAMPLE_PROPOSE_ENV
    if SAMPLE_PROPOSE_ENV == '':
        try:
            r = requests.get('http://jmenv.tbsite.net:8080/env', timeout=1)
            r.raise_for_status()
            env = r.text.strip()
            SAMPLE_PROPOSE_ENV = env
        except Exception as e:
            print('get environment error:', e)
    return SAMPLE_PROPOSE_ENV


# 方案推荐入口
def propose_sample_local(room_info, scheme_num=3, house_id=''):
    room_id, room_type, group_list, room_vector = room_info['id'], '', [], []
    if 'type' in room_info:
        room_type = room_info['type']
    if room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                     'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']:
        pass
    else:
        return []
    # 方案推荐
    sample_key_list, sample_url_list, sample_key_dict = [], [], {}
    # 本地推荐
    response_list = get_sample_key(house_id, room_id, room_info)
    for response_idx, sample_key in enumerate(response_list):
        # 纠正排序
        rank_key_new = len(sample_key_list)
        if sample_key in sample_key_dict:
            continue
        sample_key_dict[sample_key] = rank_key_new

        # 推荐排序
        design_idx = -1
        for sample_key_idx, sample_key_one in enumerate(sample_key_list):
            if sample_key_one in sample_key_dict:
                rank_key_old = sample_key_dict[sample_key_one]
                if rank_key_new < rank_key_old:
                    design_idx = sample_key_idx
                    break
        if 0 <= design_idx < len(sample_key_list):
            sample_key_list.insert(design_idx, sample_key)
        else:
            sample_key_list.append(sample_key)
    # 方案筛除
    for response_idx in range(len(sample_key_list) - 1, -1, -1):
        if len(sample_key_list[response_idx]) <= 0:
            sample_key_list.pop(response_idx)
    for response_idx in range(len(sample_url_list) - 1, -1, -1):
        if len(sample_url_list[response_idx]) <= 0:
            sample_url_list.pop(response_idx)

    # 方案方案
    sample_type_list = []
    if room_type in ROOM_TYPE_LEVEL_1:
        sample_type_list = ROOM_TYPE_LEVEL_1
    elif room_type in ROOM_TYPE_LEVEL_2:
        sample_type_list = ROOM_TYPE_LEVEL_2
    elif room_type in ROOM_TYPE_LEVEL_3:
        sample_type_list = ROOM_TYPE_LEVEL_3

    # 方案解析
    sample_info_list = []
    sample_data, sample_layout, sample_group, sample_scene = {}, {}, {}, {}
    if len(sample_key_list) > 0:
        for sample_idx, sample_key in enumerate(sample_key_list):
            if len(sample_info_list) >= scheme_num:
                break
            if len(sample_key) <= 0:
                continue
            sample_data, sample_layout, sample_group, sample_scene = parse_sample_key(sample_key)
            # 房间筛选
            sample_best = {}
            for room_key, room_val in sample_layout.items():
                if len(sample_best) <= 0:
                    sample_best = room_val
                    continue
                scheme_list_old = sample_best['layout_scheme']
                scheme_list_new = room_val['layout_scheme']
                if len(scheme_list_old) <= 0 and len(scheme_list_new) > 0:
                    sample_best = room_val
                    continue
                if room_val['room_type'] in sample_type_list and len(scheme_list_new) > 0:
                    sample_best = room_val
                if room_val['room_type'] in [room_type] and len(scheme_list_new) > 0:
                    sample_best = room_val
                    break
            sample_info_list.append(sample_best)
    else:
        for sample_idx, sample_url in enumerate(sample_url_list):
            if len(sample_info_list) >= scheme_num:
                break
            if len(sample_url) <= 0:
                continue
            sample_key = ''
            if len(sample_key_list) > sample_idx:
                sample_key = sample_key_list[sample_idx]
            sample_data, sample_layout, sample_group, sample_scene = parse_sample_url(sample_url, sample_key)
            # 房间筛选
            sample_best = {}
            for room_key, room_val in sample_layout.items():
                if len(sample_best) <= 0:
                    sample_best = room_val
                    continue
                scheme_list_old = sample_best['layout_scheme']
                scheme_list_new = room_val['layout_scheme']
                if len(scheme_list_old) <= 0 and len(scheme_list_new) > 0:
                    sample_best = room_val
                    continue
                if room_val['room_type'] in sample_type_list and len(scheme_list_new) > 0:
                    sample_best = room_val
                if room_val['room_type'] in [room_type] and len(scheme_list_new) > 0:
                    sample_best = room_val
                    break
            sample_info_list.append(sample_best)

    # 方案抽取
    sample_info_fine = sample_info_list
    if len(sample_info_list) > scheme_num > 0:
        sample_info_fine = sample_info_list[0: scheme_num]
    return sample_info_fine


# 布局特征解析
def parse_vector_data(scene_data):
    if 'center' not in scene_data:
        if 'aabb' in scene_data and len(scene_data['aabb']) >= 4:
            scene_bbox = scene_data['aabb']
            scene_data['center'] = ((scene_bbox[0] + scene_bbox[2]) / 2, (scene_bbox[1] + scene_bbox[3]) / 2)
    group_one, group_set, group_vec = {}, [], []
    scene_type, input_type = '', ''
    room_best, room_more = '', []
    if 'type' in scene_data:
        scene_type = scene_data['type']
    if scene_type in ['sofa', 'Meeting']:
        input_type = 'sofa set'
        room_best, room_more = 'LivingDiningRoom', ['LivingDiningRoom', 'LivingRoom']
    elif scene_type in ['tv', 'Media']:
        input_type = 'media'
        room_best, room_more = 'LivingDiningRoom', ['LivingDiningRoom', 'LivingRoom']
    elif scene_type in ['dining', 'dinning', 'Dining']:
        input_type = 'dining set'
        room_best, room_more = 'DiningRoom', ['DiningRoom', 'LivingDiningRoom', 'LivingRoom']
    elif scene_type in ['bed', 'Bed']:
        input_type = 'bed set'
        room_best, room_more = 'Bedroom', ['MasterBedroom', 'SecondBedroom', 'Bedroom']
    if len(input_type) > 0:
        group_one = get_default_group_layout(input_type)
    if len(group_one) > 0:
        scene_bbox, scene_height, scene_center, scene_normal = [-1, -0.5, 1, 0.5], 1, [0, 0, 0], [0, 0, 1]
        if 'aabb' in scene_data:
            scene_bbox = scene_data['aabb']
        if 'height' in scene_data:
            scene_height = scene_data['height']
        if 'center' in scene_data:
            scene_center = [scene_data['center'][0], 0, scene_data['center'][1]]
        if 'normal' in scene_data:
            scene_normal = scene_data['normal']
        # 距离角度
        dis, ang = xyz_to_ang(0, 0, scene_normal[0], scene_normal[2])
        # 位置调整
        group_pos = scene_center[:]
        group_one['position'] = group_pos[:]
        group_one['rotation'] = [0, math.sin(ang / 2), 0, math.cos(ang / 2)]
        group_one['offset'] = [0, 0, 0]
        # 尺寸调整
        width_x, width_z = abs(scene_bbox[2] - scene_bbox[0]), abs(scene_bbox[3] - scene_bbox[1])
        if abs(ang + math.pi / 2) < 0.1 or abs(ang - math.pi / 2) < 0.1:
            group_w, group_d = width_z, width_x
        else:
            group_w, group_d = width_x, width_z
        group_h = scene_height
        group_one['size'] = [group_w, group_h, group_d]
        group_one['size_min'] = [group_w, group_h, group_d]
        group_one['size_rest'] = [0, 0, 0, 0]
        group_one['scale'] = [1, 1, 1]
        # 风格调整
        group_one['style'] = ''
        # 家具调整
        group_one['obj_main'] = scene_data['id']
    group_set = [group_one]
    group_vec = compute_room_vector(group_set, room_best)
    return group_set, group_vec, room_best, room_more


# 布局特征解析
def parse_vector_url(scene_url='', scene_type=''):
    scene_json = {}
    if len(scene_url) > 0:
        if os.path.exists(scene_url) and scene_url.endswith('.json'):
            scene_json = json.load(open(scene_url, 'r'))
        else:
            response_info = requests.get(scene_url, timeout=1)
            response_json = response_info.json()
            scene_json = response_json
    group_new, group_set, group_vec = {}, [], []
    room_type, room_best, room_more = '', '', []
    if len(scene_json) > 0:
        house_data_info, house_layout_info, house_group_info = extract_house_layout_by_scene(scene_json)
    for room_key, room_val in house_group_info.items():
        if 'group_functional' not in room_val:
            continue
        group_list = room_val['group_functional']
        for group_old in group_list:
            count_new = 0
            count_old = len(group_old['obj_list'])
            if 'obj_list' in group_new:
                count_new = len(group_new['obj_list'])
            if count_new < count_old:
                room_type = room_val['room_type']
                group_new = group_old
    if len(group_new) > 0:
        group_type = group_new['type']
        if group_type in ['Meeting']:
            room_best, room_more = 'LivingDiningRoom', ['LivingDiningRoom', 'LivingRoom']
        elif group_type in ['Media']:
            room_best, room_more = 'LivingDiningRoom', ['LivingDiningRoom', 'LivingRoom']
            if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom']:
                room_best, room_more = room_type, ['MasterBedroom', 'SecondBedroom', 'Bedroom']
            elif room_type in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                room_best, room_more = room_type, ['KidsRoom', 'ElderlyRoom', 'NannyRoom']
        elif scene_type in ['Dining']:
            room_best, room_more = 'DiningRoom', ['DiningRoom', 'LivingDiningRoom', 'LivingRoom']
        elif scene_type in ['Bed']:
            room_best, room_more = 'Bedroom', ['Bedroom', 'MasterBedroom', 'SecondBedroom']
        group_set = [group_new]
        group_vec = compute_room_vector(group_set, room_best)
    return group_set, group_vec, room_best, room_more


# 布局场景解析
def parse_vector_sample(sample_group):
    sample_vec = {}
    for room_key, room_group in sample_group.items():
        room_best, group_list = '', []
        if 'room_type' in room_group:
            room_best = room_group['room_type']
        if 'group_functional' in room_group:
            group_list = room_group['group_functional']
        if len(group_list) > 0:
            group_vec = compute_room_vector(group_list, room_best)
            sample_vec[room_key] = group_vec
    return sample_vec


# 布局模板解析 多方案
def parse_sample_list(scene_list):
    sample_data, sample_layout, sample_group, sample_scene = {'id': '', 'room': []}, {}, {}, {}
    room_used = {}
    for scene_idx, scene_url in enumerate(scene_list):
        if os.path.exists(scene_url) and scene_url.endswith('.json'):
            scene_json = json.load(open(scene_url, 'r'))
        else:
            response_info = requests.get(scene_url, timeout=1)
            response_json = response_info.json()
            scene_json = response_json
        if len(scene_json) <= 0:
            continue
        scene_id = os.path.basename(scene_url).split('.')[0]
        new_data_info, new_layout_info, new_group_info = extract_house_layout_by_scene(scene_json)
        # 整理
        camera_dict = {}
        if 'scene' in new_data_info:
            for scene_one in new_data_info['scene']:
                scene_room, scene_camera = '', {}
                if 'roomId' in scene_one:
                    scene_room = scene_one['roomId']
                if 'camera' in scene_one:
                    scene_camera = scene_one['camera']
                if len(scene_room) > 0 and len(scene_camera) > 0:
                    camera_dict[scene_room] = scene_camera
        for room_key, room_layout in new_layout_info.items():
            if 'layout_scheme' in room_layout:
                scheme_list = room_layout['layout_scheme']
                for scheme_one in scheme_list:
                    if 'group' not in scheme_one:
                        continue
                    if len(scheme_one['group']) <= 0:
                        continue
                    group_one = scheme_one['group'][0]
                    if group_one['type'] not in GROUP_RULE_FUNCTIONAL:
                        break
                    # 相机信息
                    camera_info = {}
                    if room_key in camera_dict:
                        camera_info = camera_dict[room_key]
                    # 外景信息
                    scene_info = parse_sample_view(group_one, camera_info, scene_id, room_key)
                    scheme_one['scene'] = [scene_info]

        # 返回
        if len(scene_list) <= 1:
            sample_data, sample_layout, sample_group, sample_scene = new_data_info, new_layout_info, new_group_info, {}
            return sample_data, sample_layout, sample_group, sample_scene
        # 整理
        room_keep, room_dump = [], []
        for room_key, room_layout in new_layout_info.items():
            if room_key in camera_dict:
                room_keep.append(room_key)
                continue
            else:
                room_fine = False
                for camera_key, camera_val in camera_dict.items():
                    if room_key.endswith(camera_key):
                        camera_dict[room_key] = camera_val
                        room_fine = True
                        break
                if room_fine:
                    room_keep.append(room_key)
                    continue
            if len(camera_dict) > 0:
                continue
            scheme_list, group_list = [], []
            if 'layout_scheme' in room_layout:
                scheme_list = room_layout['layout_scheme']
            if len(scheme_list) > 0 and 'group' in scheme_list[0]:
                group_list = scheme_list[0]['group']
            if len(group_list) <= 0:
                room_dump.append(room_key)
            else:
                group_one = group_list[0]
                if group_one['type'] in ['Meeting', 'Bed'] and len(group_one['obj_list']) <= 1:
                    room_dump.append(room_key)
        # 添加
        for room_data in new_data_info['room']:
            room_key, room_key_new = '', ''
            if 'id' in room_data:
                room_key = room_data['id']
            room_key_new = scene_id + '_' + room_key
            if len(room_keep) > 0 and room_key not in room_keep:
                continue
            if room_key in room_dump:
                continue
            if room_key_new in room_used:
                continue
            room_data['id'] = room_key_new
            sample_data['room'].append(room_data)
        for room_key, room_group in new_group_info.items():
            room_key_new = scene_id + '_' + room_key
            if len(room_keep) > 0 and room_key not in room_keep:
                continue
            if room_key in room_dump:
                continue
            if room_key_new in room_used:
                continue
            sample_group[room_key_new] = room_group
        for room_key, room_layout in new_layout_info.items():
            room_key_new = scene_id + '_' + room_key
            if len(room_keep) > 0 and room_key not in room_keep:
                continue
            if room_key in room_dump:
                continue
            if room_key_new in room_used:
                continue
            else:
                room_used[room_key_new] = 1
            sample_layout[room_key_new] = room_layout
            scheme_list = []
            if 'layout_scheme' in room_layout:
                scheme_list = room_layout['layout_scheme']
            for scheme_one in scheme_list:
                scheme_one['source_room'] = room_key_new
            if 'layout_scheme' in room_layout:
                scheme_list = room_layout['layout_scheme']
                for scheme_one in scheme_list:
                    if 'scene' in scheme_one and len(scheme_one['scene']) > 0:
                        scene_info = scheme_one['scene'][0]
                        sample_scene[room_key_new] = scene_info
                    if 'group' not in scheme_one:
                        continue
                    if len(scheme_one['group']) <= 0:
                        continue
                    group_one = scheme_one['group'][0]
                    if group_one['type'] not in GROUP_RULE_FUNCTIONAL:
                        break
                    # 相机信息
                    camera_info = {}
                    if room_key in camera_dict:
                        camera_info = camera_dict[room_key]
                    # 外景信息
                    scene_info = parse_sample_view(group_one, camera_info, scene_id, room_key)
                    scheme_one['scene'] = [scene_info]
                    sample_scene[room_key_new] = scene_info
                    break
    return sample_data, sample_layout, sample_group, sample_scene


# 布局模板解析 样板间
def parse_sample_id(sample_id=''):
    sample_data, sample_layout, sample_group, sample_scene = {'id': '', 'room': []}, {}, {}, {}
    house_para, house_data = get_house_data(sample_id)
    sample_data, sample_layout, sample_group = extract_house_layout_by_info(house_data, check_mode=1)
    # sample_data, sample_layout, sample_group = extract_house_layout_by_design(sample_id, check_mode=1)
    pass
    # 生成场景
    if len(sample_data) > 0 and len(sample_layout) > 0:
        sample_id = sample_data['id']
        room_list = sample_data['room']
        for room_one in room_list:
            room_key = room_one['id']
            if room_key not in sample_layout:
                continue
            room_layout = sample_layout[room_key]
            if 'layout_scheme' in room_layout:
                scheme_list = room_layout['layout_scheme']
                for scheme_one in scheme_list:
                    if 'group' not in scheme_one:
                        continue
                    if len(scheme_one['group']) <= 0:
                        continue
                    group_one = scheme_one['group'][0]
                    if group_one['type'] not in GROUP_RULE_FUNCTIONAL:
                        break
                    # 相机信息
                    camera_info = {}
                    if 'camera_info' in room_one:
                        camera_info = room_one['camera_info']
                    if len(camera_info) <= 0:
                        break
                    # 外景信息
                    outdoor_type = ''
                    if 'outdoor' in room_one:
                        outdoor_type = room_one['outdoor']
                    elif 'outdoor_type' in room_one:
                        outdoor_type = room_one['outdoor_type']
                    scene_info = parse_sample_view(group_one, camera_info, sample_id, room_key, outdoor_type)
                    scheme_one['scene'] = [scene_info]
                    sample_scene[room_key] = scene_info
                    break
    return sample_data, sample_layout, sample_group, sample_scene


# 布局模板解析 样板间
def parse_sample_key(sample_key=''):
    sample_data, design_key, house_key, room_key = {}, '', '', ''
    if len(sample_key) > 0:
        sample_key_set = sample_key.split('_')
        design_key = sample_key_set[0]
        if len(sample_key_set) >= 2:
            house_key = sample_key_set[0]
            room_key = sample_key_set[-1]
    sample_data, sample_layout, sample_group, sample_scene = {}, {}, {}, {}
    # 获取信息
    if len(house_key) > 0:
        sample_layout_old = get_house_sample_layout(house_key)
        # 布局
        if room_key in sample_layout_old:
            sample_layout[room_key] = sample_layout_old[room_key]
        else:
            sample_layout = sample_layout_old
        # 添加
        for room_key, room_val in sample_layout.items():
            scheme_one = {}
            if 'layout_scheme' in room_val and len(room_val['layout_scheme']) > 0:
                scheme_one = room_val['layout_scheme'][0]
            group_set_new = []
            if 'group' in scheme_one:
                group_set_old = scheme_one['group']
                for group_old in group_set_old:
                    group_new = group_old.copy()

                    # 打组后处理
                    if 'obj_type' in group_new and 'basin' in group_new['obj_type']:
                        continue

                    check_sample_group(group_new)
                    group_set_new.append(group_new)
            add_furniture_group_list(house_key, room_key, group_set_new)
    # 解析信息
    if len(sample_layout) <= 0:
        house_para, house_data = get_house_data(house_key)
        if 'room' in house_data:
            sample_data = house_data.copy()
            sample_data['id'] = house_key
            sample_data['room'] = []
            for room_one in house_data['room']:
                if len(room_key) <= 0:
                    sample_data['room'].append(room_one)
                elif 'id' in room_one and room_one['id'] == room_key:
                    sample_data['room'].append(room_one)
                    break
            sample_data, sample_layout, sample_group, sample_scene = parse_sample_data(sample_data)
    # 返回信息
    return sample_data, sample_layout, sample_group, sample_scene


# 布局模板解析 小场景
def parse_sample_url(sample_url='', sample_key=''):
    sample_json = {}
    if len(sample_url) > 0:
        if os.path.exists(sample_url) and sample_url.endswith('.json'):
            sample_scene = json.load(open(sample_url, 'r'))
        else:
            response_info = requests.get(sample_url, timeout=1)
            response_json = response_info.json()
            sample_scene = response_json
        # 轮廓json
        if 'room' in sample_scene and 'uid' not in sample_scene:
            sample_json = sample_scene
        # 场景json
        elif len(sample_scene) > 0:
            sample_json, design_key, room_key = {}, '', ''
            if len(sample_key) > 0:
                sample_key_set = sample_key.split('_')
                design_key = sample_key_set[0]
                if len(sample_key_set) >= 2:
                    room_key = sample_key_set[-1]
            house_id_new, house_data, house_feature = get_house_data_feature_by_json(sample_scene, design_key)
            # 轮廓json
            if 'room' in house_data:
                sample_json = house_data.copy()
                if len(sample_key) <= 0:
                    sample_key = os.path.basename(sample_url).split('.')[0]
                sample_json['id'] = sample_key
                sample_json['room'] = []
                for room_one in house_data['room']:
                    if len(room_key) <= 0:
                        sample_json['room'].append(room_one)
                    elif 'id' in room_one and room_one['id'] == room_key:
                        sample_json['room'].append(room_one)
                        break
        # 轮廓json
        if len(sample_json) > 0:
            if len(sample_key) <= 0 and len(sample_url) > 0:
                sample_key = os.path.basename(sample_url).split('.')[0]
            sample_json['id'] = sample_key
    return parse_sample_data(sample_json)


# 布局模板解析
def parse_sample_data(sample_json):
    sample_data, sample_layout, sample_group, sample_scene = {'id': '', 'room': []}, {}, {}, {}
    if len(sample_json) > 0:
        sample_data, sample_layout, sample_group = extract_house_layout_by_info(sample_json, check_mode=1)
    if len(sample_layout) <= 0:
        sample_data = {}
    # 生成场景
    if len(sample_data) > 0 and len(sample_layout) > 0:
        sample_id = sample_data['id']
        room_list = sample_data['room']
        for room_idx, room_one in enumerate(room_list):
            room_key = room_one['id']
            if room_key not in sample_layout:
                continue
            room_layout = sample_layout[room_key]
            if 'layout_scheme' in room_layout:
                scheme_list = room_layout['layout_scheme']
                for scheme_one in scheme_list:
                    if 'group' not in scheme_one:
                        continue
                    if len(scheme_one['group']) <= 0:
                        continue
                    group_one = scheme_one['group'][0]
                    if group_one['type'] not in GROUP_RULE_FUNCTIONAL:
                        break
                    # 外景信息
                    outdoor_type = ''
                    if 'outdoor' in room_one:
                        outdoor_type = room_one['outdoor']
                    elif 'outdoor_type' in room_one:
                        outdoor_type = room_one['outdoor_type']

                    # 相机信息
                    camera_info = {}
                    if 'camera_info' in room_one:
                        camera_info = room_one['camera_info']
                    if len(camera_info) <= 0:
                        scene_info = room_copy_view(DEFAULT_SCENE_INFO)
                    else:
                        scene_info = parse_sample_view(group_one, camera_info, sample_id, room_key, outdoor_type)
                    scheme_one['scene'] = [scene_info]
                    sample_scene[room_key] = scene_info
                    break
    return sample_data, sample_layout, sample_group, sample_scene


# 布局视角解析
def parse_sample_view(group_one, camera_info={}, scene_house='', scene_room='', outdoor_type=''):
    scene_type = group_one['type']
    # 平面
    scene_rect = compute_furniture_rect(group_one['size'], group_one['position'], group_one['rotation'])
    scene_x_min = min(scene_rect[0], scene_rect[2], scene_rect[4], scene_rect[6])
    scene_x_max = max(scene_rect[0], scene_rect[2], scene_rect[4], scene_rect[6])
    scene_z_min = min(scene_rect[1], scene_rect[3], scene_rect[5], scene_rect[7])
    scene_z_max = max(scene_rect[1], scene_rect[3], scene_rect[5], scene_rect[7])
    scene_aabb = (scene_x_min, scene_z_min, scene_x_max, scene_z_max)
    # 高度
    scene_height = group_one['size'][1]
    # 位置
    scene_center = []
    if 'position' in group_one and len(group_one['position']) >= 3:
        group_pos = group_one['position']
        scene_center = (group_pos[0], group_pos[2])
    if 'obj_list' in group_one and len(group_one['obj_list']):
        object_one = group_one['obj_list'][0]
        object_pos = object_one['position']
        scene_center = (object_pos[0], object_pos[2])
    # 角度
    scene_angle = rot_to_ang(group_one['rotation'])
    scene_normal = [round(math.sin(scene_angle), 4), 0, round(math.cos(scene_angle), 4)]
    # 视角
    scene_camera = copy.deepcopy(camera_info)
    # 返回
    scene_info = {
        'id': scene_house,
        'room': scene_room,
        'type': scene_type,
        'aabb': scene_aabb,
        'height': scene_height,
        'center': scene_center,
        'normal': scene_normal,
        'camera': scene_camera,
        'outdoor': outdoor_type,
        'source_house': scene_house,
        'source_room': scene_room
    }
    return scene_info


# 布局户型解析
def parse_design_data(design_id, design_url, scene_url='', reload=False):
    house_para_info, house_data_info = get_house_data(design_id, design_url, scene_url, reload)
    # house_data_info = house_design_trans(design_id)
    if 'id' in house_data_info:
        house_id = design_id
        house_data_info['id'] = design_id
    if 'room' not in house_data_info:
        house_para_info, house_data_info = {}, {}
    elif 'room' in house_data_info and len(house_data_info['room']) <= 0:
        house_para_info, house_data_info = {}, {}
    return house_para_info, house_data_info


# 布局模型解析
def parse_object_data(object_one, group_one={}, room_type=''):
    object_ref = {}
    object_key, object_grp, object_role, object_type, object_rely = '', '', '', '', ''
    if 'id' in object_one:
        object_key = object_one['id']
    if 'type' in group_one:
        object_grp = group_one['type']
    elif 'group' in object_one:
        object_grp = object_one['group']
    if 'role' in object_one:
        object_role = object_one['role']
    if 'type' in object_one:
        object_type = object_one['type']
    if 'relate' in group_one:
        object_rely = group_one['relate']
    # 类型 风格 品类
    object_cate = []
    type_id, style_id, category_id = '', '', ''
    if object_type in GROUP_SEED_LIST or have_furniture_data_key(object_key, 'type_id'):
        # 基本品类
        type_id, style_id, category_id = get_furniture_data_refer_id(object_key)
        if len(category_id) <= 0 and 'category' in object_one:
            category_id = object_one['category']
        if len(category_id) <= 0 and 'categories' in object_one:
            category_set = object_one['categories']
            if len(category_set) >= 1:
                category_id = category_set[0]
        # 扩展品类
        cate_set_1, cate_set_2, cate_id_1, cate_id_2 = \
            get_furniture_category_by_role(object_grp, object_role, object_type, object_rely, room_type)
        object_cate = cate_id_1[:]
        if category_id in object_cate:
            object_cate.remove(category_id)
            object_cate.insert(0, category_id)
        elif len(category_id) > 0:
            object_cate.append(category_id)
        elif len(cate_id_2) > 0:
            category_id = cate_id_2[0]
        elif len(cate_id_1) > 0:
            category_id = cate_id_1[0]
    # 实际尺寸
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    object_ref = {
        'type_id': type_id, 'style_id': style_id, 'category_id': category_id, 'category_more': object_cate,
        'size': object_size, 'type': object_type
    }
    return object_ref


# 物品房间纠正
def parse_object_room(object_one):
    room_type = ''
    # 模型信息
    object_key = object_one['id']
    object_type, object_style, object_cate_id = '', '', ''
    if 'type' in object_one:
        object_type = object_one['type']
    if 'style' in object_one:
        object_style = object_one['style']
    if 'category' in object_one:
        object_cate_id = object_one['category']
    elif 'categories' in object_one and len(object_one['categories']) >= 1:
        object_cate_id = object_one['categories'][0]
        object_one['category'] = object_cate_id
    else:
        type_id, style_id, object_cate_id = get_furniture_data_refer_id(object_key, '', False)
        object_one['category'] = object_cate_id
    # 房间信息
    category_name, room_type = get_furniture_room_by_category(object_cate_id)
    if len(room_type) > 0:
        if room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
            room_type = 'LivingDiningRoom'
        elif room_type in ROOM_TYPE_LEVEL_2:
            room_type = 'Bedroom'
        elif room_type in ['Library']:
            room_type = 'Library'
        elif 'Bathroom' in room_type:
            room_type = 'Bathroom'
        else:
            room_type = 'Bedroom'
        return room_type
    # 角色信息
    correct_object_type(object_one, object_type, room_type)
    object_type = object_one['type']
    origin_size, origin_scale = object_one['size'], object_one['scale']
    object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
    object_group, object_role = compute_furniture_role(object_type, object_size, room_type, object_key, object_cate_id)
    if object_group in ['Meeting', 'Media', 'Dining', 'Appliance']:
        room_type = 'LivingDiningRoom'
    elif object_group in ['Bed', 'Armoire', 'Cabinet']:
        room_type = 'Bedroom'
    elif object_group in ['Work', 'Rest']:
        room_type = 'Library'
    elif object_group in ['Bath', 'Toilet']:
        room_type = 'Bathroom'
    else:
        room_type = 'Bedroom'
    return room_type


# 物品类型纠正
def parse_object_type(object_one, room_type=''):
    correct_object_type(object_one, object_type='', room_type=room_type)


# 物品尺寸纠正
def parse_object_size(object_one):
    object_key = object_one['id']
    fixed_size = get_furniture_size_by_jid(object_key)
    if len(fixed_size) >= 3:
        origin_size, origin_scale = object_one['size'], object_one['scale']
        if abs(origin_scale[0] - 1) < 0.01 and abs(origin_scale[2] - 1) < 0.01:
            if abs(origin_size[0] - fixed_size[0]) > 0.1 and abs(origin_size[2] - fixed_size[2]) > 0.1:
                origin_scale = [abs(fixed_size[i] / origin_size[i]) for i in range(3)]
                object_one['scale'] = origin_scale


# 物品角度纠正
def parse_object_turn(object_key, object_one, object_role=''):
    object_type, object_style, object_size = get_furniture_data(object_key)
    if len(object_type) > 0 and len(object_size) >= 3:
        object_turn = 0
        if object_size[2] > object_size[0] * 2 and object_size[2] > 60:
            if object_role in ['table', 'armoire', 'cabinet']:
                object_turn = get_furniture_turn(object_key)
                if object_turn == 0:
                    object_turn = -1
                    add_furniture_turn(object_key, object_turn)
        # 信息纠正
        origin_size, origin_scale = object_one['size'], object_one['scale']
        if object_turn in [-1, 1]:
            # 尺寸纠正
            x, y, z = origin_size[0], origin_size[1], origin_size[2]
            origin_size[0], origin_size[1], origin_size[2] = z, y, x
            x, y, z = origin_scale[0], origin_scale[1], origin_scale[2]
            origin_scale[0], origin_scale[1], origin_scale[2] = z, y, x
            object_one['size'] = origin_size[:]
            object_one['scale'] = origin_scale[:]
            # 角度纠正
            origin_angle = rot_to_ang(object_one['rotation'])
            object_angle = ang_to_ang(origin_angle - object_turn * math.pi / 2)
            object_one['rotation'] = [0, math.sin(object_angle / 2), 0, math.cos(object_angle / 2)]
            object_one['turn_fix'] = 1
        elif object_turn in [-2, 2]:
            # 角度纠正
            origin_angle = rot_to_ang(object_one['rotation'])
            object_angle = ang_to_ang(origin_angle - object_turn * math.pi / 2)
            object_one['rotation'] = [0, math.sin(object_angle / 2), 0, math.cos(object_angle / 2)]
            object_one['turn_fix'] = 1


# 布局锚点解析
def parse_anchor_room(item_list):
    todo_room = []
    for item_idx in range(len(item_list) - 1, -1, -1):
        item_one = item_list[item_idx]
        if 'id' in item_one and 'room_id' in item_one:
            pass
        else:
            continue
        item_key, room_key = item_one['id'], item_one['room_id']
        if len(room_key) > 0 and room_key not in todo_room:
            todo_room.append(room_key)
    return todo_room


# 布局锚点解析
def parse_anchor_item(item_list, view_list):
    for item_idx in range(len(item_list) - 1, -1, -1):
        item_one = item_list[item_idx]
        if 'id' in item_one and 'room_id' in item_one:
            pass
        else:
            continue
        item_key, room_key = item_one['id'], item_one['room_id']
        board_find, object_find, object_rank = {}, {}, 0
        for view_one in view_list:
            if room_key not in view_one['id']:
                continue
            board_list = view_one['board_wall']
            for board_one in board_list:
                object_list = board_one['relate_soft']
                for object_one in object_list:
                    if item_key == object_one['id']:
                        object_find = object_one
                        break
                if len(object_find) > 0:
                    board_find = board_one
                    break
            if len(board_find) > 0:
                break
        if 'group' in object_find and 'role' in object_find:
            object_group, object_role = object_find['group'], object_find['role']
            # 主要家具 主要分组
            if object_role in ['sofa', 'bed']:
                object_rank = 1
            elif object_role in ['table'] and object_group in ['Dining', 'Work'] or object_role in ['bath', 'toilet']:
                object_rank = 2
            elif object_role in ['table'] and object_group in ['Media'] or object_role in ['shower']:
                object_rank = 3
            # 主要家具 次要分组
            elif object_role in ['armoire', 'cabinet', 'appliance']:
                object_rank = 4
            # 次要家具
            elif object_role in ['table', 'side table', 'chair', 'tv']:
                object_rank = 5
            else:
                object_rank = 6
        board_copy = board_find.copy()
        model_copy = object_find.copy()
        if 'relate_soft' in board_copy:
            board_copy.pop('relate_soft')
            model_copy['rank'] = object_rank
            item_one['board_info'] = board_copy
            item_one['model_info'] = model_copy
        else:
            item_list.pop(item_idx)
    item_sort = []
    for item_one in item_list:
        rank_one, rank_idx = 10, -1
        if 'model_info' in item_one and 'rank' in item_one['model_info']:
            rank_one = item_one['model_info']['rank']
        for item_idx, item_old in enumerate(item_sort):
            rank_old = 10
            if 'model_info' in item_old and 'rank' in item_old['model_info']:
                rank_old = item_old['model_info']['rank']
            if rank_one < rank_old:
                rank_idx = item_idx
                break
        if 0 <= rank_idx < len(item_sort):
            item_sort.insert(rank_idx, item_one)
        else:
            item_sort.append(item_one)
    return item_sort


# 功能测试
if __name__ == '__main__':
    # 清空缓存
    layout_sample_clear()
    layout_log_clear()
    pass

    # 测试场景布局 方案生成 单批
    layout_param_input = smart_decoration_input_scene_test_99
    # layout_param_output = layout_sample_param(layout_param_input)
    pass

    # 测试场景布局 方案生成 全景
    layout_param_input = {
        "house_id": "384e8bf2-a589-41e3-ae9f-f613ef6eecba", "room_id": "",
        "house_data": {},
        "design_url": "",
        "scene_url": "",
        "layout_mode": 2,
        "scheme_mode": "frame output sphere render wander"
    }
    json_path = os.path.join(DATA_DIR_SERVER_INPUT, 'house_data_with_views_v2.json')
    json_path = ''
    if len(json_path) > 0 and os.path.exists(json_path):
        json_data = json.load(open(json_path, 'r', encoding='utf-8'))
        if 'id' in json_data:
            layout_param_input['house_id'] = json_data['id']
        layout_param_input['house_data'] = json_data
        layout_sample_param(layout_param_input)
    pass

    # 测试场景布局 方案生成
    layout_param_input = smart_decoration_input_scene_test_20
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_21
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_22
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_23
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_24
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_25
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_26
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_27
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_28
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_29
    # layout_sample_param(layout_param_input)
    pass
    # 测试场景布局 方案生成
    layout_param_input = smart_decoration_input_scene_test_30
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_31
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_32
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_33
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_34
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_35
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_36
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_37
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_38
    # layout_sample_param(layout_param_input)
    layout_param_input = smart_decoration_input_scene_test_39
    # layout_sample_param(layout_param_input)
    pass

    # 测试参考布局
    layout_param_input = smart_decoration_input_advice_test_99
    # layout_sample_param(layout_param_input)
    pass
    design_list = [
        # 00
        "1dd7d28e-926e-4588-a87c-2365c9473059",
        "a819ab88-6011-4c76-b7da-8fbc0a543cfa",
        "fd85fc24-7a91-422a-b553-636945759649",
        "b64544d3-fc22-424e-83fc-6def3c9d95dc",
        "34fff621-bdce-4b1a-80d2-9878a7a3a4ba",

        "99977d52-0bc9-46c0-af5f-eba1f9741cd6",
        "652c58c8-b63c-4801-b80a-58220af91456",
        "d39eb7ec-5465-40e6-879c-7390100f9523",
        "4c05f01f-e152-47e0-b30b-382104e3d7e1",
        "5adc9759-4844-4750-8a3a-62411465e7e2"
    ]
    for design_idx, design_key in enumerate(design_list):
        #
        if 9 <= design_idx <= 9:
            pass
        else:
            continue
        layout_param_input['house_id'] = design_key
        layout_sample_param(layout_param_input)
    pass

    # 测试分析布局 TODO:
    layout_param_input = smart_decoration_input_analyze_test_99
    # layout_sample_param(layout_param_input)
    pass

    # 数据更新
    # save_room_sample()
    # save_furniture_data()
    pass
