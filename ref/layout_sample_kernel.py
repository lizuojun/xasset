# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2021-03-09
@Description: 智能布局接口 支持我的家、放我家

"""

import os
import sys
import socket

sys.path.append(os.path.dirname(__file__))

from layout_service_log import *
from ImportHouse.room_search import *
from Extract.import_region import add_house_region
from HouseSearch.house_seed import get_material_data_info
from HouseSearch.house_propose import get_sample_key, check_sample_group
from HouseSearch.house_search_main import house_search_get_sample_info
from HouseSearch.target_seed_house_search import house_search_from_seed
from HouseSearch.put_home_sample_search import house_search_from_seed_new, template_update_house_data_region, house_search_from_material_seed_new
from HouseSearch.put_home_sample_search import update_furniture_role_data, armoire_house_data_refine
from LayoutCustomized.customized_layout import layout_house_customized
from LayoutDecoration.recon_main import house_recon_pipeline


# 布局服务计数
LAYOUT_SAMPLE_CNT = 0
LAYOUT_SAMPLE_LOC = ''

# 布局机位房间
LAYOUT_VIEW_ROOM_TYPE = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                         'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                         'Library',
                         'Kitchen',
                         'MasterBathroom', 'SecondBathroom', 'Bathroom']
# 返回结果定义
REPLACE_ERR_CODE_LIST = {
    "LAYOUT_ALGO_SEED_SUCCESS",  # 替换成功
    "LAYOUT_ALGO_SEED_ROLE_MAP_ERROR",  # 种子到布局角色映射失败
    "LAYOUT_ALGO_SEED_ROLE_NOT_RECOMMEND",  # 种子不在推荐布局角色列表里面(比如卧室放餐桌)
    "LAYOUT_ALGO_SEED_EXCEPTION",  # 程序报错
    "LAYOUT_ALGO_SEED_REPLACE_FAIL"  # 布局角色映射成功、替换失败
}


# 方案布局入口
def layout_sample_kernel(house_info, scene_list=[], layout_num=3, scheme_mode='', struct_mode={}, style_mode='',
                         replace_info={}, replace_note={}, replace_room={}, use_region=True):
    # 返回状态
    replace_err_code = ""
    # 户型信息
    house_id, room_id, scene_path = '', '', ''
    # 处理输入种子信息

    if 'id' in house_info:
        house_id = house_info['id']
    correct_house_data(house_info)

    update_furniture_role_data(replace_info, house_info)
    # TODO:
    if use_region:
        # add_house_region(house_id, house_info)
        search_region_house(house_id, house_info)

    # 内容数量
    if layout_num <= 0 or layout_num > 10:
        layout_num = 4
    if 0 < len(scene_list) < layout_num:
        layout_num = len(scene_list)
    # 内容信息
    sample_house, sample_info = '', {}
    sample_data, sample_layout, sample_group = {}, {}, {}
    if 0 < len(scene_list):
        sample_data, sample_layout, sample_group, sample_scene = parse_sample_list(scene_list)
        if len(sample_house) <= 0 and 'id' in sample_data:
            sample_house = sample_data['id']
        sample_info = sample_layout
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

    # 参数信息
    scheme_mode = scheme_mode.lower()
    save_mode, view_mode, path_mode = [], 0, -1
    clear_mode = 0
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
        path_mode = PATH_MODE_WANDER
    # 清空
    if 'clear' in scheme_mode:
        clear_mode = 1
    # 打印信息
    layout_time = 15
    layout_mode_str = 'layout scheme'
    layout_log_create(layout_time)
    layout_log_0 = layout_mode_str + ' ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    # 打印信息
    target_id = house_id
    layout_log_0 = 'target house: %s, room: %s, layout: %d, propose: %d' % (target_id, '', 1, 1)
    layout_log_update(layout_log_0)

    # 中间信息
    data_info, layout_info, propose_info, region_info, scene_info, route_info = {}, {}, {}, {}, {}, {}

    try:
        # 种子处理
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
                    seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list,
                                                                                   room_type)
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
            pave_info = {}
            if 'pave' in room_val:
                pave_info = room_val['pave']
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
                    mat_info = get_material_data_info(object_key)
                    object_new.update(mat_info)
                    if len(pave_info) and object_key in pave_info:
                        object_new['pave'] = pave_info[object_key]
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
                    mat_info = get_material_data_info(object_key)
                    object_new.update(mat_info)
                    if len(pave_info) and object_key in pave_info:
                        object_new['pave'] = pave_info[object_key]
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
                object_new = replace_note[object_key]
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
                    layout_log_0 = 'propose room ' + datetime.datetime.now().strftime(
                        '%Y.%m.%d-%H:%M:%S') + ' ' + room_key
                    layout_log_0 += ' sample ' + source_room
                    # 方案推荐
                    layout_log_update(layout_log_0)
                    room_sample_set = []
                else:
                    # 信息打印
                    layout_log_0 = 'propose room ' + datetime.datetime.now().strftime(
                        '%Y.%m.%d-%H:%M:%S') + ' ' + room_key
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
                        if '12626' in room_key and room_sample_idx == 0 and False:
                            print('propose room ', room_key, '------debug------')
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
                        room_data_add, room_layout_add, room_propose_add, room_region_add = \
                            layout_room_by_sample(room_info, room_sample_add, replace_soft, replace_note, refine_mode=1)
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
                view_type = LAYOUT_VIEW_ROOM_TYPE
                if len(replace_more) > 0 and 'room' in scheme_mode:
                    if room_key in replace_more:
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
                elif room_type in view_type:
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
            # 推荐处理
            house_sample_info = house_search_get_sample_info(house_info, replace_more, replace_note, layout_num,
                                                             style_mode)
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
                    if "seed_flag" in sample_data_info['info']:
                        for seed_id in sample_data_info['info']["seed_flag"]:
                            _replace_code = sample_data_info['info']["seed_flag"][seed_id]
                            if len(_replace_code) > 0:
                                replace_err_code = _replace_code

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
                            if room_type in ['LivingRoom'] and room_sample_add['room_type'] in ['LivingDiningRoom']:
                                pass
                            elif room_type in ['LivingDiningRoom'] and room_sample_add['room_type'] in ['LivingRoom']:
                                pass
                            else:
                                room_type = room_sample_add['room_type']
                        # 调试信息
                        if '8943' in room_key and room_sample_idx == 0 and True:
                            print('propose room ', room_key, '------debug------')
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
                                if room_type in ['LivingRoom'] and group_type in ['Dining']:
                                    pass
                                elif room_type in ['DiningRoom'] and group_type in ['Meeting']:
                                    pass
                                else:
                                    group_tune.append(group_one)
                            scheme_one['group'] = group_tune
                        # 方案调整
                        if group_well <= 2:
                            import_room_adjust(scheme_list_add, [], [], room_type, room_area, room_link)
                        elif room_type in ['LivingRoom', 'LivingDiningRoom'] and room_area > 25:
                            import_room_adjust(scheme_list_add, [], [], room_type, room_area, room_link)
                        elif room_type in ['LivingRoom'] and room_area < 20:
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
                            layout_room_by_sample(room_info, room_sample_add, replace_soft, replace_note,
                                                  refine_mode=refine_mode)
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
                view_type = LAYOUT_VIEW_ROOM_TYPE
                if len(replace_more) > 0 and 'room' in scheme_mode:
                    if room_key in replace_more:
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
                elif room_type in view_type:
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

        # 返回状态
        if len(replace_err_code) == 0:
            for room_key in replace_info:
                if "used" in replace_info[room_key]:
                    if "soft" in replace_info[room_key]:
                        if len(replace_info[room_key]["used"]) == len(replace_info[room_key]["soft"]):
                            replace_err_code = "LAYOUT_ALGO_SEED_SUCCESS"
                        else:
                            replace_err_code = "LAYOUT_ALGO_SEED_REPLACE_FAIL"
                else:
                    if "soft" in replace_info[room_key]:
                        if len(replace_info[room_key]["soft"]) > 0:
                            replace_err_code = "LAYOUT_ALGO_SEED_REPLACE_FAIL"

        # 打印信息
        layout_log_0 = 'layout success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        # 保存信息
        if len(save_mode) > 0:
            save_id = house_id
            if save_id == '':
                if len(layout_info) <= 0:
                    save_id = 'null'
                elif len(layout_info) == 1:
                    save_id = 'room'
                else:
                    save_id = 'house'
            if SAVE_MODE_IMAGE in save_mode or SAVE_MODE_FRAME in save_mode:
                save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
                if 'index' in scheme_mode:
                    index_set = scheme_mode.split('index')
                    if len(index_set) >= 2:
                        save_idx = int(index_set[1].split(' ')[0])
                        save_id = '%03d_%s' % (save_idx, save_id)
                house_save(house_id, scene_path, layout_num, 0,
                           data_info, layout_info, propose_info,
                           save_id, save_dir, save_mode, suffix_flag=False, sample_flag=True, upload_flag=False)
                if len(scene_list) == 1 and len(sample_info) > 0:
                    house_save(sample_house, '', 1, 1,
                               sample_data, sample_layout, {},
                               sample_house + '_sample', save_dir, [SAVE_MODE_FRAME],
                               suffix_flag=False, sample_flag=False, upload_flag=False)
                    #
                    scene_url = scene_list[0]
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
        # 打印信息
        layout_log_0 = 'layout success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
    except Exception as e:
        raise
        replace_err_code = "LAYOUT_ALGO_SEED_EXCEPTION"
        house_layout_info = {}
        # 错误信息
        layout_log_0 = 'layout error ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
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
    # 返回信息
    layout_output_list = []
    # 返回信息
    save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, house_id)
    # 方案遍历
    for layout_idx in range(layout_num):
        house_data_copy, house_layout_copy, house_style_each, house_build_mode = house_info.copy(), {}, '', struct_mode
        # 户型房间
        room_list_old, room_list_new = [], []
        if 'room' in house_info:
            room_list_old = house_info['room']
        for room_old in room_list_old:
            room_new = room_old.copy()
            room_new['furniture_info'] = []
            room_list_new.append(room_new)
        house_data_copy['room'] = room_list_new
        house_data_copy['style'] = ''
        # 户型布局
        room_style_main, room_style_rest, room_style_last = '', '', ''
        for room_key, room_val in layout_info.items():
            room_layout_new = room_val.copy()
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
                if 'type' in room_scheme_one and 'style' in room_scheme_one:
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
        if style_mode.lower() in furniture_style_dict_en and not house_style_each == style_mode:
            house_style_each = style_mode
        house_data_copy['style'] = house_style_each
        if len(scene_list) > 0:
            house_build_mode['white_list'] = False
            house_build_mode['bg_wall'] = False
        # 软装信息
        house_data_copy['layout'] = {}
        house_data_copy['replace'] = replace_more
        house_data_copy['replace_err_code'] = replace_err_code

        # 硬装信息
        layout_log_0 = 'build begin ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        house_data_copy = house_recon_pipeline(house_data_copy, house_layout_copy, house_style_each, house_build_mode)
        layout_log_0 = 'build end ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        # 更新信息
        house_data_copy['layout'] = house_layout_copy
        house_room_list = []
        if 'room' in house_data_copy:
            house_room_list = house_data_copy['room']
        for room_idx, room_one in enumerate(house_room_list):
            room_key, room_obj = '', []
            if 'id' in room_one:
                room_key = room_one['id']
            if room_key in house_layout_copy:
                room_layout, room_scheme, group_list = house_layout_copy[room_key], {}, []
                if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
                    room_scheme = room_layout['layout_scheme'][0]
                    if 'group' in room_scheme:
                        group_list = room_scheme['group']
                for group_one in group_list:
                    object_list = []
                    if 'obj_list' in group_one:
                        object_list = group_one['obj_list']
                    for object_one in object_list:
                        room_obj.append(object_one)
            room_one['coordinate'] = 'xzy'
            room_one['furniture_info'] = room_obj
        # 添加信息
        layout_output_list.append(house_data_copy)

    # 保存日志
    log_loc = layout_sample_host()
    log_dir = 'layout_sample'
    if len(log_loc) > 0:
        log_dir = log_loc + '/layout_sample'
    save_id = house_id
    if save_id == '':
        if len(layout_info) <= 0:
            save_id = 'null'
        elif len(layout_info) == 1:
            save_id = 'room'
        else:
            save_id = 'house'
    layout_log_upload(log_dir, save_id)

    # 返回信息
    return layout_output_list


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
def parse_design_data(design_id, design_url, scene_url=''):
    house_para_info, house_data_info = get_house_data(design_id, design_url, scene_url)
    # house_data_info = house_design_trans(design_id)
    if 'id' in house_data_info:
        house_id = design_id
        house_data_info['id'] = design_id
    if 'room' not in house_data_info:
        house_para_info, house_data_info = {}, {}
    elif 'room' in house_data_info and len(house_data_info['room']) <= 0:
        house_para_info, house_data_info = {}, {}
    return house_para_info, house_data_info


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
        room_type = 'LivingDiningRoom'
    return room_type


# 物品类型纠正
def parse_object_type(object_one, room_type=''):
    correct_object_type(object_one, object_type='', room_type=room_type)
    pass


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
        object_turn = get_furniture_turn(object_key)
        if object_size[2] > object_size[0] * 2.0 and object_size[2] > 60:
            if object_role in ['table', 'armoire', 'cabinet']:
                if object_turn == 0:
                    object_turn = 1
                    add_furniture_turn(object_key, object_turn)
        elif object_size[2] > object_size[0] * 1.5 and object_size[0] > 60:
            if object_role in ['table', 'cabinet'] and object_size[1] < 60:
                if object_turn == 0:
                    object_turn = 1
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
            object_one['turn'], object_one['turn_fix'] = object_turn, 1
        elif object_turn in [-2, 2]:
            # 角度纠正
            origin_angle = rot_to_ang(object_one['rotation'])
            object_angle = ang_to_ang(origin_angle - object_turn * math.pi / 2)
            object_one['rotation'] = [0, math.sin(object_angle / 2), 0, math.cos(object_angle / 2)]
            object_one['turn'], object_one['turn_fix'] = object_turn, 1


# 推荐默认户型
def search_seeds_house_templet(replace_info, sample_num, new=True, use_region=True):
    furniture_list = []
    material_dict = {}
    target_house_id = []
    room_type = "LivingRoom"
    for room_type in replace_info:
        if "soft" in replace_info[room_type]:
            furniture_list = replace_info[room_type]["soft"]
        if "floor" in replace_info[room_type]:
            material_dict['floor'] = replace_info[room_type]["floor"]
        if 'wall' in replace_info[room_type]:
            material_dict['wall'] = replace_info[room_type]["wall"]
        if "sample" in replace_info[room_type]:
            target_house_id = replace_info[room_type]["sample"]

    # 根据replace_info里面的role信息更新家具角色
    update_furniture_role_data(replace_info, {})

    if len(target_house_id) > 0:
        house_id = target_house_id[0]
        replace_info[room_type]["self_transfer"] = target_house_id
        put_flag = True

    else:
        if new:
            if len(furniture_list) > 0:
                put_flag, house_id, new_replace_info = house_search_from_seed_new(furniture_list, room_type,
                                                                                  sample_num=sample_num)
            else:
                # put_flag, house_id, new_replace_info = house_search_from_seed_new(material_list, room_type,
                #                                                                   sample_num=sample_num)
                # 根据材质检索
                put_flag, house_id, new_replace_info = house_search_from_material_seed_new(material_dict, room_type,
                                                                                  sample_num=sample_num)
        else:
            put_flag, house_id, new_replace_info = house_search_from_seed(furniture_list, room_type,
                                                                          sample_num=sample_num)

        # 合并
        for replace_key in new_replace_info:
            if replace_key not in replace_info:
                replace_info[replace_key] = new_replace_info[replace_key]
            else:
                for sub_key in new_replace_info[replace_key]:
                    if sub_key not in replace_info[replace_key]:
                        replace_info[replace_key][sub_key] = new_replace_info[replace_key][sub_key]

    _, house_data = get_house_data(house_id)

    if use_region:
        template_update_house_data_region(house_id, room_type, house_data)

    armoire_house_data_refine(house_id, house_data, replace_info)

    return put_flag, house_data, replace_info


# 功能测试
if __name__ == '__main__':
    # 清空缓存
    layout_sample_clear()
    layout_log_clear()
    pass

    # 解析户型
    TEST_HOUSE_SAMPLE = True
    TEST_MULTI_PUT_HOME = False

    print()
    if TEST_HOUSE_SAMPLE:
        design_id = '1840749'
        design_url = ''
        scene_url = ''
        house_para, house_data = get_house_data(design_id, design_url, scene_url)
        # 推荐方案 我的家
        scene_list = []
        layout_num = 1
        scheme_mode = 'sphere'
        struct_mode = {'customized_ceiling': True, 'bg_wall': True, 'debug': True}
        style_mode = ''
        replace_room = {
            "Balcony-11733": {"style": "", "type": "Balcony"},
            "Bedroom-6790": {"style": "", "type": "Bedroom"},
            "LivingRoom-2550": {"style": "", "type": "LivingRoom"},
            "Bathroom-10471": {"style": "", "type": "Bathroom"},
            "Bedroom-4388": {"style": "", "type": "Bedroom"},
            "Bathroom-9563": {"style": "", "type": "Bathroom"},
            "Bedroom-8415": {"style": "", "type": "Bedroom"},
            "Kitchen-12924": {"style": "", "type": "Kitchen"}
        }
        replace_info = {"LivingRoom-1254": {"soft": ["721230a2-d34d-4ef0-8460-7508eed3e32c"]}}
        layout_output = layout_sample_kernel(house_data, scene_list, layout_num, scheme_mode, struct_mode, style_mode,
                                             replace_info=replace_info, replace_note={})
        print(replace_info)
        # 机位
        exit()
        from Extract.data_oss import oss_upload_json
        from layout_sample_analyze import layout_sample_camera
        from layout_sample_construct import layout_sample_construct
        import time
        from Demo.buffer_render import get_pano_house

        for layout_idx, layout_one in enumerate(layout_output):
            # 重建
            scene_json = layout_sample_construct(layout_one)
            # 机位
            camera_set = layout_sample_camera(layout_one)

            data_time = time.strftime("%Y-%m-%d") + "/"
            name_time = str(int(time.time() * 1000))

            scene_name = name_time + "_edited.json"
            oss_upload_json("layout_scene_advisor/" + data_time + scene_name, scene_json, "ihome-alg-layout")

            scene_new_url = "https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com/layout_scene_advisor/" + data_time + scene_name
            camera_list = [i['wander'] for i in camera_set if 'living' in i['type'].lower()][0]
            url = get_pano_house(scene_new_url, camera_list, content_name=design_id + "test_new_data",
                                 need_svg_house_id=design_id)
            print(url)
            print(scene_new_url)
    # 多种子放我家 默认户型
    if TEST_MULTI_PUT_HOME:
        furniture_list = ['f7c57256-8eaa-4215-a22a-151046949e95', '60552aee-03b1-4b98-8646-e214829391fc',
                          'b0797be7-9cb2-4577-a9a5-fe340c7e0434', '47dd8fe1-dc1c-4f0d-aec1-a686ba1273da']

        room_type = "LivingRoom"
        scene_list = []
        layout_num = 3
        scheme_mode = 'sphere frame'
        struct_mode = {'customized_ceiling': True, 'bg_wall': True}
        style_mode = ''
        replace_info = {"LivingRoom": {"soft": furniture_list}}

        # 推荐默认户型
        put_success, house_data, replace_info = search_seeds_house_templet(replace_info, sample_num=layout_num)
        # 放入默认户型
        layout_output = layout_sample_kernel(house_data, [], layout_num, scheme_mode, struct_mode, style_mode,
                                             replace_info=replace_info, replace_note={}, replace_room={})

        print()
