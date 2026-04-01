# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-10-24
@Description: 智能布局服务 支持智能软装、方案裂变、机位模板

"""

import time


from House.house_scene_build import *
from House.house_scene_render import *
from HouseSearch.seed.hard_service import *

from layout_def import *
from layout_service_log import *
from ImportHouse.room_search import *
from LayoutByRule.house_interior_wander import *
from LayoutDecoration.recon_main import house_recon_pipeline

# 记录目录
DATA_DIR_RECORD = os.path.dirname(__file__) + '/LayoutRecord/'
if not os.path.exists(DATA_DIR_RECORD):
    os.makedirs(DATA_DIR_RECORD)

# 家具推荐服务
FURNITURE_PROPOSE_UAT = 'https://tui.taobao.com/recommend'
# FURNITURE_PROPOSE_UAT = 'https://tui.alibaba-inc.com/recommend'
FURNITURE_PROPOSE_APP_ID = 18328
FURNITURE_PROPOSE_USR_ID = 999999999
# 布局服务计数
LAYOUT_PROPOSE_CNT = 0
# 推荐饰品错误
FURNITURE_PROPOSE_ERROR = [
    'a6b3f563-fae5-4cf1-a4d8-9e4039101560',
    '9c3ed38a-6f44-4feb-8069-1538550dded7',
    '407d2225-7fe1-439a-8f9d-bb8ef8d94430'
]
FURNITURE_PROPOSE_CLEAR = []
# 推荐家具错误
FURNITURE_PROPOSE_PIANO = ['1b51dd12-0f5e-4d3d-bf6f-1e9e73dc14cb']

# 布局机位房间
LAYOUT_VIEW_ROOM_TYPE = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                         'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                         'Library',
                         'Kitchen',
                         'MasterBathroom', 'SecondBathroom', 'Bathroom']


# 全屋布局迁移
def layout_transfer_house(house_info, sample_house, sample_room, sample_info={}, sample_split=0,
                          poolid=None, deco_mode=0):
    house_id = ''
    if 'id' in house_info:
        house_id = house_info['id']
    # 方案提取
    layout_log_0 = 'extract house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    if len(sample_info) <= 0:
        sample_para, sample_info = get_house_data(sample_house)
        correct_house_type(sample_info)
        sample_data, sample_layout, sample_group = extract_house_layout_by_info(sample_info, check_mode=2)
    else:
        correct_house_type(sample_info)
        sample_data, sample_layout, sample_group = extract_house_layout_by_info(sample_info, check_mode=2)
    for room_key, room_layout in sample_layout.items():
        if room_key == sample_room:
            if 'layout_scheme' in room_layout:
                scheme_type = room_layout['room_type']
                scheme_list = room_layout['layout_scheme']
                for scheme_one in scheme_list:
                    if scheme_type in ['Kitchen']:
                        scheme_one['source_room_flag'] = 1
                    elif 'code' in scheme_one and scheme_one['code'] > 0:
                        scheme_one['source_room_flag'] = 1
    # 方案迁移
    layout_log_0 = 'transfer house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    replace_info, replace_dict = {}, {}
    data_info, layout_info, propose_info, region_info = \
        layout_house_by_sample(house_info, sample_layout, replace_info, replace_dict, refine_mode=0)
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

    # 默认房间
    sample_room_1, sample_room_2, sample_room_3 = '', '', ''
    sample_style_1, sample_style_2, sample_style_3 = '', '', ''
    for room_key, room_layout in layout_info.items():
        if len(room_layout['layout_scheme']) > 0:
            scheme_one = room_layout['layout_scheme'][0]
            if 'source_house' in scheme_one:
                scheme_house = scheme_one['source_house']
                if sample_house not in scheme_house:
                    continue
                scheme_room = scheme_one['source_room']
                scheme_type = scheme_one['type']
                scheme_style = ''
                if 'style' in scheme_one and len(scheme_one['style']) > 0:
                    scheme_style = scheme_one['style']
                elif 'group' in scheme_one and len(scheme_one['group']) > 0:
                    scheme_group = scheme_one['group'][0]
                    for scheme_object in scheme_group['obj_list']:
                        if 'style' in scheme_object and len(scheme_object['style']) > 0:
                            scheme_style = scheme_object['style']
                            break
                if scheme_type in ROOM_TYPE_LEVEL_1:
                    sample_room_1 = scheme_room
                    sample_style_1 = scheme_style
                    if len(sample_room_2) <= 0:
                        sample_room_2 = scheme_room
                        sample_style_2 = scheme_style
                elif scheme_type in ROOM_TYPE_LEVEL_2:
                    sample_room_2 = scheme_room
                    sample_style_2 = scheme_style
                    if len(sample_room_1) <= 0:
                        sample_room_1 = scheme_room
                        sample_style_1 = scheme_style
                elif scheme_type in ROOM_TYPE_LEVEL_3:
                    sample_room_3 = scheme_room
                    sample_style_3 = scheme_style

    # 方案机位
    scene_info, route_info = {}, {}
    view_mode, path_mode = VIEW_MODE_SPHERE, PATH_MODE_WANDER
    view_type = LAYOUT_VIEW_ROOM_TYPE
    data_info, layout_info, scene_info, route_info = view_house(data_info, layout_info, view_mode, path_mode, view_type)

    # 方案裂变
    if sample_split >= 1:
        # 房间裂变 TODO:

        pass

        # 软装搭配
        layout_log_0 = 'propose house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        for room_id, room_propose_info in propose_info.items():
            propose_furniture(room_propose_info, 1, 1, house_id, False, True, poolid=poolid)

        # 软装替换
        layout_log_0 = 'adjust house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        adjust_house(layout_info, propose_info)
        layout_log_0 = 'refine house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        refine_house(layout_info)
        layout_log_0 = 'finish house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        pass
        # 硬装搭配
        for room_key, room_layout_info in layout_info.items():
            room_type, room_style = '', ''
            room_scheme, room_paint, room_group, room_object = {}, {}, {}, {}
            if 'room_type' in room_layout_info:
                room_type = room_layout_info['room_type']
            if 'room_style' in room_layout_info:
                room_style = room_layout_info['room_style']
            if 'layout_scheme' in room_layout_info and len(room_layout_info['layout_scheme']) > 0:
                room_scheme = room_layout_info['layout_scheme'][0]
            if 'style' in room_scheme:
                room_style = room_scheme['style']
            if 'painting' in room_scheme:
                room_paint = room_scheme['painting']
            if 'group_propose' in room_scheme and len(room_scheme['group_propose']) > 0:
                room_group = room_scheme['group_propose'][0][0]
            elif 'group' in room_scheme and len(room_scheme['group']) > 0:
                room_group = room_scheme['group'][0]
            group_type = ''
            if 'type' in room_group:
                group_type = room_group['type']
            if group_type in ['Meeting', 'Bed', 'Dining', 'Work']:
                if 'obj_list' in room_group and len(room_group['obj_list']) > 0:
                    room_object = room_group['obj_list'][0]
            room_paint_new = propose_painting(room_object, room_paint, room_type, room_style, poolid=poolid)
            room_scheme['painting'] = room_paint_new

    # 硬装重建
    decorate_info = house_recon_pipeline(data_info, layout_info, 'modern', {})

    # 返回信息
    return data_info, layout_info, propose_info, decorate_info, sample_data, sample_layout, sample_group


# 单屋布局迁移
def layout_transfer_room(room_info, sample_house, sample_room, sample_info={}, sample_split=0,
                         house_id='', poolid=None, deco_mode=0):
    # 方案提取
    layout_log_0 = 'extract room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    if len(sample_info) <= 0:
        sample_data, sample_layout, sample_group = extract_room_layout_by_design(sample_house, sample_room,
                                                                                 check_mode=2)
    else:
        sample_data = sample_info
        if 'room' in sample_info and len(sample_info['room']) > 0:
            for room_one in sample_info['room']:
                if 'id' in room_one and room_one['id'] == sample_room:
                    sample_data = room_one
                    break
        sample_layout, sample_group = extract_room_layout_by_info(sample_data, 2)
    # 方案迁移
    layout_log_0 = 'transfer room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    replace_list, replace_dict = [], {}
    data_info, layout_info, propose_info, region_info = layout_room_by_sample(room_info, sample_layout,
                                                                              replace_list, replace_dict, refine_mode=0)
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

    # 方案裂变
    if sample_split >= 1:
        # 软装推荐
        layout_log_0 = 'propose room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        propose_furniture(propose_info, 1, 1, house_id, False, False, poolid=poolid)
        # 软装替换
        layout_log_0 = 'adjust room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        adjust_room(layout_info, propose_info)
        layout_log_0 = 'refine room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        refine_room(layout_info)
        layout_log_0 = 'finish room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)

    # 硬装重建
    room_key = room_info['id']
    house_data = {'id': house_id, 'room': [room_info]}
    house_layout = {room_key: layout_info}
    house_decorate = house_recon_pipeline(house_data, house_layout, 'modern', {})
    # 硬装重建 单屋硬装
    decorate_info = {}
    if 'rooms' in house_decorate:
        room_dict = house_decorate['rooms']
        if room_key in room_dict:
            decorate_info = room_dict[room_key]

    # 返回信息
    return data_info, layout_info, propose_info, decorate_info, sample_data, sample_layout, sample_group


# 全屋布局推荐
def layout_propose_house(house_info, layout_num=3, propose_num=3, deco_mode=0, request_log=False):
    house_id = ''
    if 'id' in house_info:
        house_id = house_info['id']
    # 软装布局
    data_info, layout_info, propose_info, region_info = layout_house_by_info(house_info, layout_num)
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

    # 软装搭配
    layout_log_0 = 'propose house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    for room_id, room_propose_info in propose_info.items():
        propose_furniture(room_propose_info, propose_num, 0, house_id, False, request_log)
    # 软装替换
    layout_log_0 = 'adjust house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    adjust_house(layout_info, propose_info)
    layout_log_0 = 'refine house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    refine_house(layout_info)
    layout_log_0 = 'finish house ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)

    # 硬装重建
    decorate_info = {}

    # 返回信息
    return data_info, layout_info, propose_info, decorate_info


# 单屋布局推荐
def layout_propose_room(room_info, layout_num=3, propose_num=3, house_id='', deco_mode=0, request_log=False):
    # 软装布局
    data_info, layout_info, propose_info, region_info = layout_room_by_info(room_info, layout_num)
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

    # 软装推荐
    layout_log_0 = 'propose room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    propose_furniture(propose_info, propose_num, 0, house_id, False, request_log)
    # 软装替换
    layout_log_0 = 'adjust room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    adjust_room(layout_info, propose_info)
    layout_log_0 = 'refine room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    refine_room(layout_info)
    layout_log_0 = 'finish room ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)

    # 硬装重建
    room_key = room_info['id']
    house_data = {'id': house_id, 'room': [room_info]}
    house_layout = {room_key: layout_info}
    house_decorate = {}
    # 单屋硬装
    decorate_info = {}
    if 'rooms' in house_decorate:
        room_dict = house_decorate['rooms']
        if room_key in room_dict:
            decorate_info = room_dict[room_key]
    # 返回信息
    return data_info, layout_info, propose_info, decorate_info


# 全屋布局调整
def layout_adjust_house(house_info, replace_info={}):
    # 种子处理
    room_list, replace_more = [], {}
    if 'room' in house_info:
        room_list = house_info['room']
    room_type_list_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']
    room_type_list_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom']
    room_type_list_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom']
    for room_one in room_list:
        room_key, room_type = '', ''
        if 'id' in room_one:
            room_key = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        if len(room_key) <= 0:
            continue
        if room_key in replace_info:
            replace_more[room_key] = replace_info[room_key]
        elif room_type in replace_info:
            replace_more[room_key] = replace_info[room_type]
        elif room_type in room_type_list_1:
            for type_new in room_type_list_1:
                if type_new in replace_info:
                    replace_more[room_key] = replace_info[type_new]
                    break
        elif room_type in room_type_list_2:
            for type_new in room_type_list_2:
                if type_new in replace_info:
                    replace_more[room_key] = replace_info[type_new]
                    break
        elif room_type in room_type_list_3:
            for type_new in room_type_list_3:
                if type_new in replace_info:
                    replace_more[room_key] = replace_info[type_new]
                    break

    # 全屋替换
    data_info, layout_info, propose_info, region_info = replace_house(house_info, replace_more)
    # 全屋调整
    adjust_house(layout_info, propose_info)
    # 全屋优化
    refine_house(layout_info, raise_flag=False)
    # 返回信息
    return data_info, layout_info, propose_info


# 单屋布局调整
def layout_adjust_room(room_info, replace_info={}):
    # 种子处理
    replace_soft = []
    if 'soft' in replace_info:
        replace_soft = replace_info['soft']

    # 单屋替换
    data_info, layout_info, propose_info, region_info = replace_room(room_info, replace_soft)
    # 单屋调整
    adjust_room(layout_info, propose_info)
    # 单屋优化
    refine_room(layout_info, raise_flag=False)
    # 返回信息
    return data_info, layout_info, propose_info


# 全屋布局机位
def layout_camera_house(house_info):
    pass


# 单屋布局机位
def layout_camera_room(room_info):
    pass


# 布局服务入口
def layout_propose_param(param_info, request_log=False):
    # 户型参数
    house_id, room_id, plat_id = '', '', ''
    house_list = []
    house_data, room_data = {}, {}
    if 'house_id' in param_info:
        house_id = param_info['house_id']
    if 'room_id' in param_info:
        room_id = param_info['room_id']
    if 'plat_id' in param_info:
        plat_id = param_info['plat_id']
    if 'house_list' in param_info:
        house_list = param_info['house_list']
    if 'house_data' in param_info:
        house_data = param_info['house_data']
        if len(house_data) > 0 and 'id' not in house_data and len(house_id) > 0:
            house_data['id'] = house_id
    if 'room_data' in param_info:
        room_data = param_info['room_data']
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
    if design_id == '' and not house_id == '':
        design_id = house_id
    # 商品参数
    scene_list = []
    # 样板参数
    sample_house, sample_room = '', ''
    sample_json, sample_url, sample_info = {}, '', {}
    house_replace, room_replace, note_replace = {}, {}, {}
    if 'sample_house' in param_info:
        sample_house = param_info['sample_house']
    if 'sample_room' in param_info:
        sample_room = param_info['sample_room']
    if 'sample_house_id' in param_info:
        sample_house = str(param_info['sample_house_id'])
    if 'sample_room_id' in param_info:
        sample_room = str(param_info['sample_room_id'])
    if 'sample_house_json' in param_info:
        sample_json = param_info['sample_house_json']
    if 'sample_house_json_url' in param_info:
        sample_url = param_info['sample_house_json_url']
    if 'house_replace' in param_info:
        house_replace = param_info['house_replace']
    if 'room_replace' in param_info:
        room_replace = param_info['room_replace']
    if 'note_replace' in param_info:
        note_replace = param_info['note_replace']

    # 布局模式
    layout_mode = LAYOUT_MODE_PROPOSE
    if 'layout_mode' in param_info:
        layout_mode = param_info['layout_mode']
    if not sample_house == '':
        if layout_mode not in [LAYOUT_MODE_TRANSFER, LAYOUT_MODE_SPLIT]:
            layout_mode = LAYOUT_MODE_TRANSFER
    if len(house_replace) > 0 or len(room_replace) > 0:
        layout_mode = LAYOUT_MODE_ADJUST
    layout_num, propose_num = 2, 3
    if layout_mode in [LAYOUT_MODE_TRANSFER, LAYOUT_MODE_ADJUST, LAYOUT_MODE_SPLIT, LAYOUT_MODE_CAMERA]:
        layout_num, propose_num = 1, 1
    if 'layout_number' in param_info:
        layout_num = param_info['layout_number']
    if 'propose_number' in param_info:
        propose_num = param_info['propose_number']
    if layout_num <= 0 or layout_num > 10:
        layout_num = 2
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
    # 裂变布局
    elif layout_mode == LAYOUT_MODE_SPLIT:
        layout_mode_str = 'layout split'
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

    # 保存模式
    scheme_mode, style_mode, struct_mode, render_mode, render_room = '', '', '', '', []
    save_mode, view_mode, path_mode = [], 0, -1
    if 'scheme_mode' in param_info:
        scheme_mode = str(param_info['scheme_mode']).lower()
        # 绘制
        if 'image' in scheme_mode:
            save_mode.append(SAVE_MODE_IMAGE)
        if 'frame' in scheme_mode:
            save_mode.append(SAVE_MODE_FRAME)
        # 数据
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
        pass
    if 'style_mode' in param_info:
        style_mode = param_info['style_mode']
    if 'struct_mode' in param_info:
        struct_mode = param_info['struct_mode']
    if 'render_mode' in param_info:
        render_mode = str(param_info['render_mode']).lower()
    if 'render_room' in param_info:
        render_room = param_info['render_room']

    # 打印信息
    layout_log_0 = layout_mode_str + ' ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    layout_log_update(layout_log_0)
    # 打印信息
    target_id = house_id
    if target_id == '' and not design_id == '':
        target_id = design_id
    layout_log_0 = 'target house: %s, room: %s, layout: %d, propose: %d' % (target_id, room_id, layout_num, propose_num)
    layout_log_update(layout_log_0)
    # 打印信息
    if layout_mode in [LAYOUT_MODE_TRANSFER, LAYOUT_MODE_SPLIT]:
        layout_log_0 = 'sample house: %s, room: %s' % (sample_house, sample_room)
        layout_log_update(layout_log_0)

    # 布局信息
    room_data_info, room_layout_info, room_propose_info, room_decorate_info = {}, {}, {}, {}
    house_data_info, house_layout_info, house_propose_info, house_decorate_info = {}, {}, {}, {}
    room_group_info, house_group_info, house_wander_info = {}, {}, {}
    sample_data_info, sample_layout_info, sample_group_info = {}, {}, {}
    try:
        # 户型参数
        if len(house_data) <= 0 and len(room_data) <= 0:
            house_para_info, house_data_info = {}, {}
            # house idx
            if house_id == '' and 0 <= house_idx and design_id == '' and scene_url == '' and data_url == '':
                house_list = list_house_oss(DATA_OSS_HOUSE_EMPTY, house_idx, 1)
                if len(house_list) > 0:
                    house_id = house_list[0]
            # data url
            if len(house_data_info) <= 0 and not data_url == '':
                if os.path.exists(data_url) and data_url.endswith('.json'):
                    house_data_info = json.load(open(data_url, 'r'))
                else:
                    response_info = requests.get(data_url, timeout=1)
                    response_json = response_info.json()
                    house_data_info = response_json
            # design url design id
            if len(house_data_info) <= 0 and not design_id == '':
                reload = False
                if len(scene_url) > 0 and layout_mode in [LAYOUT_MODE_CAMERA]:
                    reload = True
                house_para_info, house_data_info = parse_design_data(design_id, design_url, scene_url, reload)
                if 'id' in house_data_info:
                    house_id = design_id
                    house_data_info['id'] = design_id
                if 'room' in house_data_info and len(house_data_info['room']) <= 0:
                    house_data_info = {}
            # scene url
            if len(house_data_info) <= 0 and not scene_url == '':
                scene_have, scene_path = download_scene_by_url(scene_url, DATA_DIR_SERVER_INPUT)
                if scene_have and os.path.exists(scene_path):
                    house_id_new, house_data_info, house_feature_info = get_house_data_feature_by_path(scene_path)
            # house id
            if len(house_data_info) <= 0 and not house_id == '':
                house_id_new, house_data_info, house_feature_info = get_house_data_feature(house_id, True)
                if len(house_data_info) <= 0 and design_id == '':
                    design_id = house_id
            # image url TODO:
            if len(house_data_info) <= 0 and not image_url == '':
                pass
            # 户型更新
            if len(house_data_info) > 0:
                house_data = house_data_info
                if not room_id == '' and 'room' in house_data_info:
                    for room_one in house_data_info['room']:
                        if room_id == room_one['id']:
                            room_data = room_one
                            break
        # 样板参数
        if len(sample_info) <= 0 and len(sample_json) > 0:
            sample_info = sample_json
            if 'room' in sample_info and len(sample_info['room']) > 0:
                pass
            else:
                sample_info = {}
        if len(sample_info) <= 0 and len(sample_url) > 0:
            sample_info = house_data_fetch(sample_url)
            if len(sample_info) <= 0 and len(sample_house) > 0:
                sample_para, sample_info = get_house_data(design_id)
                # sample_info = house_design_trans(sample_house)

        # 布局处理 单屋布局
        if len(room_data) > 0:
            if 'id' in room_data and room_id == '':
                room_id = room_data['id']
            if 'coordinate' not in room_data:
                room_data['coordinate'] = 'xyz'
            if 'unit' not in room_data:
                room_data['unit'] = 'm'
            # 布局处理
            data_info, layout_info, propose_info, decorate_info = {}, {}, {}, {}
            sample_data, sample_layout, sample_group = {}, {}, {}
            scheme_info, group_info = {}, {}
            # 布局迁移
            if layout_mode == LAYOUT_MODE_TRANSFER:
                data_info, layout_info, propose_info, decorate_info, sample_data, sample_layout, sample_group = \
                    layout_transfer_room(room_data, sample_house, sample_room, sample_info, 0, house_id)
            # 布局推荐
            elif layout_mode == LAYOUT_MODE_PROPOSE:
                data_info, layout_info, propose_info, decorate_info = \
                    layout_propose_room(room_data, layout_num, propose_num, house_id, 0, request_log)
            # 布局调整
            elif layout_mode == LAYOUT_MODE_ADJUST:
                data_info, layout_info, propose_info = layout_adjust_room(room_data, room_replace)
            # 布局裂变
            elif layout_mode == LAYOUT_MODE_SPLIT:
                enterprise_package = ""
                enterprise_id = ""
                # poolid = None
                if "enterprise_id" in param_info:
                    enterprise_id = param_info["enterprise_id"]
                if "enterprise_package" in param_info:
                    enterprise_package = param_info["enterprise_package"]
                if enterprise_package != "":
                    poolid = "%s_%s" % (enterprise_id, enterprise_package)
                elif enterprise_id != "":
                    poolid = enterprise_id
                else:
                    poolid = None
                data_info, layout_info, propose_info, decorate_info, sample_data, sample_layout, sample_group = \
                    layout_transfer_room(room_data, sample_house, sample_room, sample_info, 1, house_id, poolid=poolid)
            # 布局组合
            elif layout_mode == LAYOUT_MODE_GROUP:
                if len(room_data) > 0 and 'furniture_info' in room_data:
                    data_info, scheme_info, group_info = group_room(room_data)
            # 布局机位
            elif layout_mode == LAYOUT_MODE_CAMERA:
                if len(room_data) > 0:
                    view_type = LAYOUT_VIEW_ROOM_TYPE
                    # 纠正信息
                    correct_room_data(room_data)
                    # 机位处理
                    data_info, layout_info, camera_info, wander_info = view_room(room_data, view_mode, path_mode, view_type)
            # 布局推荐
            else:
                data_info, layout_info, propose_info, decorate_info = \
                    layout_propose_room(room_data, layout_num, propose_num, house_id, 0, request_log)
            # 组装信息
            if 'room' not in house_data:
                house_data = {'id': house_id, 'room': []}
            if len(house_data['room']) <= 0:
                house_data['room'].append(data_info)
            room_data_info = data_info
            room_layout_info = layout_info
            room_propose_info = propose_info
            room_decorate_info = decorate_info
            room_group_info = group_info
            # 组装信息
            house_data_info = house_data
            if len(layout_info) > 0:
                house_layout_info[room_id] = room_layout_info
            if len(propose_info) > 0:
                house_propose_info[room_id] = room_propose_info
            if len(decorate_info) > 0:
                house_decorate_info[room_id] = room_decorate_info
            if len(group_info) > 0:
                house_group_info[room_id] = room_group_info
            if len(sample_data) > 0 and not sample_room == '':
                sample_data_info = {'id': sample_house, 'room': [sample_data]}
            if len(sample_layout) > 0 and not sample_room == '':
                sample_layout_info[sample_room] = sample_layout
            if len(sample_group) > 0 and not sample_room == '':
                sample_group_info[sample_room] = sample_group_info
        # 布局处理 全屋布局
        elif len(house_data) > 0 and 'room' in house_data:
            if 'id' in house_data and house_id == '':
                house_id = house_data['id']
            if 'room' in house_data:
                for room_one in house_data['room']:
                    if 'coordinate' not in room_one:
                        room_one['coordinate'] = 'xyz'
                    if 'unit' not in room_one:
                        room_one['unit'] = 'm'
            # 布局处理
            data_info, layout_info, propose_info, decorate_info = {}, {}, {}, {}
            sample_data, sample_layout, sample_group = {}, {}, {}
            scheme_info, group_info, wander_info = {}, {}, {}
            # 布局迁移
            if layout_mode == LAYOUT_MODE_TRANSFER:
                data_info, layout_info, propose_info, decorate_info, sample_data, sample_layout, sample_group = \
                    layout_transfer_house(house_data, sample_house, sample_room, sample_info, 0)
            # 布局推荐
            elif layout_mode == LAYOUT_MODE_PROPOSE:
                data_info, layout_info, propose_info, decorate_info = \
                    layout_propose_house(house_data, layout_num, propose_num, 0, request_log)
            # 布局调整
            elif layout_mode == LAYOUT_MODE_ADJUST:
                data_info, layout_info, propose_info = layout_adjust_house(house_data, house_replace)
            # 布局裂变
            elif layout_mode == LAYOUT_MODE_SPLIT:
                enterprise_package = ""
                enterprise_id = ""
                # poolid = None
                if "enterprise_id" in param_info:
                    enterprise_id = param_info["enterprise_id"]
                if "enterprise_package" in param_info:
                    enterprise_package = param_info["enterprise_package"]
                if enterprise_package != "":
                    poolid = "%s_%s" % (enterprise_id, enterprise_package)
                elif enterprise_id != "":
                    poolid = enterprise_id
                else:
                    poolid = None
                data_info, layout_info, propose_info, decorate_info, sample_data, sample_layout, sample_group = \
                    layout_transfer_house(house_data, sample_house, sample_room, sample_info, 1, poolid=poolid)
            # 布局组合
            elif layout_mode == LAYOUT_MODE_GROUP:
                data_info, scheme_info, group_info = group_house(house_data)
            # 布局机位
            elif layout_mode == LAYOUT_MODE_CAMERA:
                view_type = LAYOUT_VIEW_ROOM_TYPE
                # 纠正信息
                correct_house_data(house_data)
                # 机位处理
                data_info, layout_info, scene_info, route_info = view_house(house_data, {}, view_mode, path_mode, view_type)
                # 点位处理
                wander_info = wander_house(data_info, layout_info)
            # 布局推荐
            else:
                data_info, layout_info, propose_info, decorate_info = \
                    layout_propose_house(house_data, layout_num, propose_num, 0, request_log)
            # 组装信息
            house_data_info = data_info
            house_layout_info = layout_info
            house_propose_info = propose_info
            house_decorate_info = decorate_info
            #
            house_group_info = group_info
            house_wander_info = wander_info
            #
            sample_data_info = sample_data
            sample_layout_info = sample_layout
            sample_group_info = sample_group

        # 打印信息
        layout_log_0 = 'layout success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        # 保存布局
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
            save_dir = layout_propose_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
            sample_flag = True
            if layout_mode in [LAYOUT_MODE_TRANSFER, LAYOUT_MODE_ADJUST, LAYOUT_MODE_SPLIT, LAYOUT_MODE_CAMERA]:
                sample_flag = False
            house_save(house_id, scene_path, layout_num, propose_num,
                       house_data_info, house_layout_info, house_propose_info,
                       save_id, save_dir, save_mode, suffix_flag=False, sample_flag=sample_flag, upload_flag=False)
            if SAVE_MODE_FRAME in save_mode and len(sample_data_info) > 0 and (
                    len(sample_house) > 0 or len(sample_room) > 0):
                house_save(sample_house, '', layout_num, propose_num,
                           sample_data_info, sample_layout_info, {},
                           sample_house + '_sample', save_dir, [SAVE_MODE_FRAME],
                           suffix_flag=False, sample_flag=False, upload_flag=False)

        # 打印信息
        layout_log_0 = 'layout success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
    except Exception as e:
        house_layout_info = {}
        # 打印信息
        layout_log_0 = 'layout error ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        layout_log_e = str(e)
        layout_log_update(layout_log_e)

    # 计数信息
    layout_propose_count()

    # 镜像信息
    room_mirror = 0
    if len(room_data) > 0 and 'mirror' in room_data:
        room_mirror = room_data['mirror']
    elif len(house_data) > 0 and 'room' in house_data:
        for room_one in house_data['room']:
            if len(room_one) > 0 and 'mirror' in room_one:
                room_mirror = room_one['mirror']
                break

    # 传入信息
    sample_room_list, sample_room_dict = [], {}
    if 'room' in sample_data_info:
        sample_room_list = sample_data_info['room']
    for room_one in sample_room_list:
        room_key, room_type, room_object = '', '', []
        if 'id' in room_one:
            room_key = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        if len(room_key) <= 0:
            continue
        if room_key in sample_room_dict:
            room_object = sample_room_dict[room_key]
        object_todo = []
        if 'furniture_info' in room_one:
            object_todo = room_one['furniture_info']
        for object_one in object_todo:
            if 'id' in object_one:
                room_object.append(object_one['id'])
        sample_room_dict[room_key] = room_object
    # 软装信息
    layout_source, layout_detail, layout_region, layout_overlap = \
        parse_scheme_layout(house_layout_info, propose_num, room_mirror)
    # 硬装信息
    layout_region_new = parse_scheme_decorate(house_decorate_info, propose_num, room_mirror)
    parse_update_region(layout_region, layout_region_new)
    # 日志信息
    layout_log = ''
    # 版本信息
    layout_version = '20220411.2000'

    # 输出处理
    layout_output = {
        'house_id': house_id,
        'room_id': room_id,
        'layout_number': layout_num,
        'propose_number': propose_num,
        'layout_scheme': layout_overlap,
        'layout_log': layout_log,
        'layout_version': layout_version
    }
    # 房间顺序
    room_sort, room_dict = correct_house_sort(house_layout_info)
    if 'sample_house_id' in param_info or 'sample_house_json' in param_info or 'sample_house_json_url' in param_info:
        layout_output = {}
        for room_key in room_sort:
            detail_list, overlap_list = [], []
            if room_key in layout_detail:
                detail_list = layout_detail[room_key]
            if room_key in layout_overlap:
                overlap_list = layout_overlap[room_key]
            detail_one, overlap_one = [], []
            if len(detail_list) > 0:
                detail_one = detail_list[0]
            if len(overlap_list) > 0:
                overlap_one = overlap_list[0]
            # 样板
            sample_room = ''
            if room_key in layout_source:
                sample_room = layout_source[room_key]
            # 参考
            predict_list = []
            if room_key in layout_region:
                region_list = layout_region[room_key]
                if len(region_list) > 0:
                    predict_list = region_list[0]
            # 内容
            content_list = []
            for object_one in overlap_one:
                # 一级
                object_new = {
                    'id': object_one['id'],
                    'position': object_one['position'],
                    'rotation': object_one['rotation'],
                    'scale': object_one['scale'],
                    'materials': {}
                }
                if 'materials' in object_one:
                    object_new['materials'] = object_one['materials']
                if 'hostType' in object_one:
                    object_new['hostType'] = object_one['hostType']
                if 'entityId' in object_one:
                    object_new['entityId'] = object_one['entityId']
                if 'sub_list' in object_one:
                    sub_list_old, sub_list_new = object_one['sub_list'], []
                    for sub_one in sub_list_old:
                        # 二级
                        sub_new = {
                            'id': sub_one['id'],
                            'position': sub_one['position'],
                            'rotation': sub_one['rotation'],
                            'scale': sub_one['scale'],
                            'materials': {}
                        }
                        if 'materials' in sub_one:
                            sub_new['materials'] = sub_one['materials']
                        if 'hostType' in sub_one:
                            sub_new['hostType'] = sub_one['hostType']
                        if 'entityId' in sub_one:
                            sub_new['entityId'] = sub_one['entityId']
                        sub_list_new.append(sub_new)
                        if 'sub_list' in sub_one:
                            sub_sub_old, sub_sub_new = sub_one['sub_list'], []
                            for sub_sub_one in sub_sub_old:
                                # 三级
                                sub_new = {
                                    'id': sub_sub_one['id'],
                                    'position': sub_sub_one['position'],
                                    'rotation': sub_sub_one['rotation'],
                                    'scale': sub_sub_one['scale'],
                                    'materials': {}
                                }
                                if 'materials' in sub_sub_one:
                                    sub_new['materials'] = sub_sub_one['materials']
                                if 'hostType' in sub_sub_one:
                                    sub_new['hostType'] = sub_sub_one['hostType']
                                if 'entityId' in sub_sub_one:
                                    sub_new['entityId'] = sub_sub_one['entityId']
                                sub_sub_new.append(sub_new)
                            sub_new['sub_list'] = sub_sub_new
                    object_new['sub_list'] = sub_list_new
                content_list.append(object_new)
            # 记录
            sample_type = ''
            sample_todo, sample_done, sample_rest = [], [], []
            if sample_room in sample_layout_info:
                sample_room_info = sample_layout_info[sample_room]
                if 'room_type' in sample_room_info:
                    sample_type = sample_room_info['room_type']
            if sample_room in sample_room_dict:
                sample_todo = sample_room_dict[sample_room]
            for object_one in detail_one:
                if 'id' in object_one:
                    sample_done.append(object_one['id'])
            for object_key in sample_todo:
                if object_key not in sample_done:
                    if object_key not in sample_rest:
                        sample_rest.append(object_key)
            # 结果
            scheme_new = {
                'sourceRoom': sample_room,
                'sourceRoomType': sample_type,
                'predictData': predict_list,
                'contents': content_list,
                'sourceRoomRestContents': sample_rest
            }
            layout_output[room_key] = scheme_new
        # 铺贴 点位
        for room_key, room_layout in house_layout_info.items():
            # 点位
            room_scheme, room_paint = {}, {}
            if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
                room_scheme = room_layout['layout_scheme'][0]
            if 'painting' in room_scheme:
                room_paint = room_scheme['painting']
            # 机位列表
            room_scene_list = []
            if 'scene' in room_scheme:
                room_scene_list = room_scheme['scene']
            # 点位列表
            room_wander_list, room_wander_each = [], []
            if 'wander' in room_scheme:
                room_wander_list = room_scheme['wander']
            if len(room_wander_list) > 0:
                camera_list = room_wander_list[0]
                for camera_one in camera_list:
                    room_wander_each.append(camera_one)
            # 点位调整
            room_wander_each = []
            for scene_one in room_scene_list:
                if 'camera' in scene_one:
                    camera_one = scene_one['camera']
                    room_wander_each.append(camera_one)
            # 输出调整
            room_type_en, room_type_ch = room_key, room_key
            if 'room_type' in room_layout:
                room_type_en = room_layout['room_type']
                room_type_ch = room_type_en
                if room_type_en in ROOM_TYPE_NAME:
                    room_type_ch = ROOM_TYPE_NAME[room_type_en]
            camera_list = []
            for camera_idx, camera_one in enumerate(room_wander_each):
                camera_new = camera_one.copy()
                camera_new['pos'] = camera_one['pos'][:]
                camera_new['target'] = camera_one['target'][:]
                if room_mirror >= 1:
                    wander_pos, wander_tar = camera_one['pos'][:], camera_one['target'][:]
                    camera_new['pos'] = [wander_pos[0], -wander_pos[2], wander_pos[1]]
                    camera_new['target'] = [wander_tar[0], -wander_tar[2], wander_tar[1]]
                    pass

                # 归一化，修改target，使得视线方向不变，target到pos的距离为1
                lookat = [u-v for u, v in zip(camera_new['target'], camera_new['pos'])]
                denominator = math.sqrt(lookat[0]**2 + lookat[1]**2 + lookat[2]**2)
                lookat_normed = [u/denominator for u in lookat]
                camera_new['target'] = [u+v for u, v in zip(lookat_normed, camera_new['pos'])]

                camera_new['room'] = room_key
                camera_new['name'] = room_type_ch + '_%d' % camera_idx
                camera_list.append(camera_new)
            if room_key in layout_output:
                room_output = layout_output[room_key]
                room_output['hardDeco'] = room_paint
                room_output['wander'] = camera_list
    elif layout_mode == LAYOUT_MODE_CAMERA:
        layout_output = {
            'house_id': house_id,
            'room_id': room_id,
            'room_sort': room_sort,
            'layout_wander': house_wander_info,
            'layout_log': layout_log,
            'layout_version': layout_version
        }
        # 纠正镜像
        if room_mirror >= 1:
            house_wander_copy = copy.deepcopy(house_wander_info)
            house_wander_room = {}
            if 'room_wander' in house_wander_copy:
                house_wander_room = house_wander_copy['room_wander']
            for room_key, room_val in house_wander_room.items():
                camera_set_1, camera_set_2, wander_set_1, wander_set_2 = [], [], [], []
                if 'camera_single' in room_val:
                    camera_set_1 = room_val['camera_single']
                if 'camera_sphere' in room_val:
                    camera_set_2 = room_val['camera_sphere']
                if 'wander_room' in room_val:
                    wander_set_1 = room_val['wander_room']
                if 'wander_room' in room_val:
                    wander_set_2 = room_val['wander_group']
                for camera_set in [camera_set_1, camera_set_2]:
                    for camera_val in camera_set:
                        if 'camera' in camera_val:
                            camera_one = camera_val['camera']
                            camera_pos, camera_tar = camera_one['pos'][:], camera_one['target'][:]
                            camera_one['pos'] = [camera_pos[0], -camera_pos[2], camera_pos[1]]
                            camera_one['target'] = [camera_tar[0], -camera_tar[2], camera_tar[1]]
            house_wander_sort = {}
            for room_key in room_sort:
                if room_key in house_wander_room:
                    house_wander_sort[room_key] = house_wander_room[room_key]
            house_wander_copy['room_wander'] = house_wander_sort
            layout_output['layout_wander'] = house_wander_copy

    # 场景信息
    if 'scene' in scheme_mode and len(house_data_info) > 0 and len(house_layout_info) > 0:
        for layout_idx in range(layout_num):
            # 户型方案
            house_data_copy, house_layout_copy, house_style_each, house_build_mode = house_data_info.copy(), {}, '', {}
            # 户型房间
            room_list_old, room_list_new = [], []
            if 'room' in house_data:
                room_list_old = house_data['room']
            for room_old in room_list_old:
                room_new = room_old.copy()
                room_new['furniture_info'] = []
                room_list_new.append(room_new)
            house_data_copy['room'] = room_list_new
            for propose_idx in range(propose_num):
                # 户型布局
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
                        group_list_set = [room_scheme_one['group']]
                        if 'group_propose' in room_scheme_one and len(room_scheme_one['group_propose']) > 0:
                            group_list_set = room_scheme_one['group_propose']
                        room_scheme_new = room_scheme_one.copy()
                        group_list_new = group_list_set[propose_idx % len(group_list_set)]
                        room_scheme_new['group'] = group_list_new
                        room_scheme_new['group_propose'] = []
                        room_layout_new['layout_scheme'] = [room_scheme_new]
                        house_layout_copy[room_key] = room_layout_new
                # 户型重建
                layout_log_0 = 'build begin ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                layout_log_update(layout_log_0)
                house_scene_json, house_scene_outdoor = house_build_house(house_data_copy, house_layout_copy,
                                                                          house_style_each, house_build_mode)
                layout_log_0 = 'build end ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                layout_log_update(layout_log_0)
                # 户型保存
                save_id = house_id
                if save_id == '':
                    if len(house_layout_info) <= 0:
                        save_id = 'null'
                    elif len(house_layout_info) == 1:
                        save_id = 'room'
                    else:
                        save_id = 'house'
                save_dir = layout_propose_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
                save_time = datetime.datetime.now().strftime('%H-%M-%S')
                json_path = os.path.join(save_dir, save_id + '_scene_%02d_%02d.json' % (layout_idx, 0))
                with open(json_path, "w") as f:
                    # json.dump(house_scene_json, f, indent=4)
                    json.dump(house_scene_json, f)
                    f.close()
                # 场景信息
                scene_each = {
                    'id': save_id,
                    'url': '',
                    'loc': json_path,
                    'layout': house_layout_copy
                }
                scene_list.append(scene_each)
    # 渲染信息
    image_key_list, image_val_list = [], []
    if SAVE_MODE_RENDER in save_mode:
        for scene_each in scene_list:
            scene_key, scene_path, scene_layout = scene_each['id'], scene_each['loc'], scene_each['layout']
            # 户型上传
            save_id = scene_key
            scene_url_new = house_scene_upload(house_scene_json, save_id, scene_path)
            # 遍历房间
            for room_key, room_val in scene_layout.items():
                room_type = room_val['room_type']
                if len(render_room) > 0 and room_type not in render_room:
                    continue
                room_layout_each = room_val
                room_scheme_list = room_layout_each['layout_scheme']
                if len(room_scheme_list) <= 0:
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
                    # 点位列表
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
                            render_loc = scene_url_new
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
                                image_key_list.append(render_key)
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
        save_dir = layout_propose_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        # 图片
        key_list, val_list = image_key_list, image_val_list
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
    if 'output' in scheme_mode:
        save_id = house_id
        if save_id == '':
            if len(house_layout_info) <= 0:
                save_id = 'null'
            elif len(house_layout_info) == 1:
                save_id = 'room'
            else:
                save_id = 'house'
        save_dir = layout_propose_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        json_path = os.path.join(save_dir, save_id + '_output.json')
        with open(json_path, "w") as f:
            json.dump(layout_output, f, ensure_ascii=False, indent=4)
            f.close()

    # 返回信息
    return layout_output


# 布局服务目录
def layout_propose_mkdir(save_dir, save_id):
    save_dir_new = os.path.join(save_dir, save_id)
    if not os.path.exists(save_dir_new):
        os.makedirs(save_dir_new)
    return save_dir_new


# 布局服务计数
def layout_propose_count(count_max=200):
    # 调用信息
    global LAYOUT_PROPOSE_CNT
    LAYOUT_PROPOSE_CNT += 1
    if LAYOUT_PROPOSE_CNT >= count_max:
        # 重置
        LAYOUT_PROPOSE_CNT = 0
        # 清空
        layout_propose_clear()


# 布局服务清空
def layout_propose_clear():
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


# 家具推荐服务
def propose_furniture(propose_info, propose_num=3, propose_rand=0,
                      house_id='', request_loc=False, request_log=False, poolid=None):
    if len(propose_info) <= 0:
        return
    # 本地推荐
    if request_loc:
        for propose_one in propose_info:
            generate_furniture_propose(propose_one, propose_num)
        return
    # 推荐服务
    server_url = FURNITURE_PROPOSE_UAT
    # 启动信息
    target_seed, target_style = [], []
    if len(propose_info) > 0:
        propose_one = propose_info[0]
        if 'target_seed' in propose_one and len(propose_one['target_seed']) > 0:
            for seed_one in propose_one['target_seed']:
                target_seed.append(seed_one['id'])
        if 'target_style' in propose_one:
            target_style = propose_one['target_style']
        # 随机种子
        if len(target_seed) <= 0 and propose_rand >= 1:
            wait_set = []
            if 'target_scope' in propose_one:
                scope_list = propose_one['target_scope']
                for object_one in scope_list:
                    object_id, object_role, object_type = object_one['id'], object_one['role'], object_one['type']
                    if object_role in ['sofa', 'bed', 'table', 'cabinet', 'armoire']:
                        wait_set.append(object_id)
            if len(wait_set) > 0:
                wait_idx = random.randint(0, 10) % len(wait_set)
                target_seed.append(wait_set[wait_idx])
    seed_id = ''
    if len(target_seed) > 0:
        seed_id = target_seed[0]
    # 随机信息
    propose_from = 0
    if propose_rand >= 1:
        propose_from = random.randint(0, 20)
    # 遍历方案
    for propose_idx, propose_one in enumerate(propose_info):
        if 'target_furniture' not in propose_one:
            propose_one['target_furniture'] = []
        if 'target_furniture_size' not in propose_one:
            propose_one['target_furniture_size'] = {}
        if 'target_furniture_log' not in propose_one:
            propose_one['target_furniture_log'] = {}
        if len(propose_one['target_scope']) <= 0:
            continue
        # 范围参数
        scope_list, scope_dict, decor_dict = propose_one['target_scope'], {}, {}
        for object_one in scope_list:
            object_id, object_role, object_type = object_one['id'], object_one['role'], object_one['type']
            if object_role in ['accessory'] and 'pillow' not in object_type:
                decor_dict[object_id] = 1
            scope_dict[object_id] = object_one
        # 选品参数
        object_list = []
        for object_one in propose_one['target_scope']:
            object_key = object_one['id']
            if object_key == seed_id and propose_rand >= 1:
                object_key = seed_id + '_seed'
            object_new = {
                'model_id': object_key,
                'xMin': round(object_one['size_min'][0], 1),
                'zMin': round(object_one['size_min'][1], 1),
                'yMin': round(object_one['size_min'][2], 1),
                'xMax': round(object_one['size_max'][0], 1),
                'zMax': round(object_one['size_max'][1], 1),
                'yMax': round(object_one['size_max'][2], 1),
                'xPerfect': round(object_one['size_cur'][0], 1),
                'zPerfect': round(object_one['size_cur'][1], 1),
                'yPerfect': round(object_one['size_cur'][2], 1),
                'cateLayout': object_one['type'],
                'cate_id': object_one['cate_id']
            }
            object_list.append(object_new)
        if len(object_list) <= 0:
            # 打印信息
            layout_log_0 = 'propose empty ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
            layout_log_update(layout_log_0)
            layout_log_update(e)
            continue
        # 房间参数
        room_id, room_type, room_area = propose_one['id'], propose_one['type'], propose_one['area']
        room_attr = {
            'isCurrent': 'true',
            'modelIds': target_seed,
            'roomId': '1',
            'roomType': room_type,
            'area': room_area,
            'styleIds': target_style
        }
        # 请求参数 分批请求
        propose_list = []
        request_limit = 7
        request_count = math.ceil((len(object_list) - 1) / request_limit)
        if request_count <= 0:
            object_once = [object_list[0]]
            if len(object_once) > 0:
                propose_once = {
                    'isAIDesign': 'true',
                    'input_model_id': seed_id,
                    'roomsAttribute': [],
                    'needSizeRuleAbsolutely': 'true',
                    'SlotRuleAIDesgin': object_once,
                }
                if poolid is not None:
                    propose_once['poolBestId'] = poolid
                    propose_once['poolBasicId'] = poolid
                propose_once['roomsAttribute'].append(room_attr)
                propose_list.append(propose_once)
        else:
            for request_index in range(request_count):
                object_once = [object_list[0]]
                for i in range(request_limit):
                    object_idx = 1 + request_index * request_limit + i
                    if object_idx >= len(object_list):
                        break
                    object_once.append(object_list[object_idx])
                if len(object_once) > 0:
                    propose_once = {
                        'isAIDesign': 'true',
                        'input_model_id': seed_id,
                        'roomsAttribute': [],
                        'needSizeRuleAbsolutely': 'true',
                        'SlotRuleAIDesgin': object_once,
                    }
                    if poolid is not None:
                        propose_once['poolBestId'] = poolid
                        propose_once['poolBasicId'] = poolid
                        propose_once['vidId'] = poolid
                    propose_once['roomsAttribute'].append(room_attr)
                    propose_list.append(propose_once)
        # 调用服务
        try:
            target_furniture = propose_one['target_furniture']
            target_furniture_size = propose_one['target_furniture_size']
            target_furniture_log = propose_one['target_furniture_log']
            for scheme_idx in range(propose_num):
                target_furniture.append({})
            process_sync, process_list, process_queue = True, [], multiprocessing.Queue()
            response_todo = []
            # 顺序执行
            if process_sync or len(propose_list) <= 2:
                for request_idx, propose_data in enumerate(propose_list):
                    request_data = {
                        'appid': FURNITURE_PROPOSE_APP_ID,
                        'userId': FURNITURE_PROPOSE_USR_ID,
                        'DEBUG': 'true',
                        'input_json': json.dumps(propose_data)
                    }
                    # 初次调用
                    response_info = requests.post(server_url, data=request_data)
                    response_data = response_info.json()
                    response_dict = {}

                    # 打印信息
                    layout_log_0 = 'propose %d %d 0: %02d ' % (propose_idx, request_idx, len(object_list)) + \
                                   datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                    layout_log_update(layout_log_0)

                    # 解析信息
                    if 'result' in response_data and len(response_data['result']) > 0:
                        if 'return_map' in response_data['result'][0]:
                            response_map = response_data['result'][0]['return_map']
                            response_dict = response_tran_dict(response_map)
                            if len(response_dict) > 0:
                                response_good = True
                        elif 'returnCollectionList' in response_data['result'][0]:
                            response_list = response_data['result'][0]['returnCollectionList']
                            response_dict = response_tran_list(response_list)
                    if len(response_dict) <= 0:
                        # 记录日志
                        request_file = '%s_%s_request_fail_%d_%d.json' % (house_id, room_id, propose_idx, request_idx)
                        request_path = os.path.join(DATA_DIR_SERVER_SERVICE, request_file)
                        with open(request_path, "w") as f:
                            json.dump(propose_data, f, indent=4)
                            f.close()
                        response_file = '%s_%s_response_fail_%d_%d.json' % (house_id, room_id, propose_idx, request_idx)
                        response_path = os.path.join(DATA_DIR_SERVER_SERVICE, response_file)
                        with open(response_path, "w") as f:
                            json.dump(response_data, f, indent=4)
                            f.close()
                        # 再次调用
                        response_info = requests.post(server_url, data=request_data)
                        response_data = response_info.json()

                        # 打印信息
                        layout_log_0 = 'propose %d %d 0: %02d ' % (propose_idx, request_idx, len(object_list)) + \
                                       datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                        layout_log_update(layout_log_0)

                        # 解析信息
                        if 'result' in response_data and len(response_data['result']) > 0:
                            if 'return_map' in response_data['result'][0]:
                                response_map = response_data['result'][0]['return_map']
                                response_dict = response_tran_dict(response_map)
                            elif 'returnCollectionList' in response_data['result'][0]:
                                response_list = response_data['result'][0]['returnCollectionList']
                                response_dict = response_tran_list(response_list)
                    if len(response_dict) > 0:
                        response_todo.append(response_dict)
                        # 记录日志
                        if request_log:
                            request_file = '%s_%s_request_good_%d_%d.json' % (
                                house_id, room_id, propose_idx, request_idx)
                            request_path = os.path.join(DATA_DIR_SERVER_SERVICE, request_file)
                            with open(request_path, "w") as f:
                                json.dump(propose_data, f, indent=4)
                                f.close()
                            response_file = '%s_%s_response_good_%d_%d.json' % (
                                house_id, room_id, propose_idx, request_idx)
                            response_path = os.path.join(DATA_DIR_SERVER_SERVICE, response_file)
                            with open(response_path, "w") as f:
                                json.dump(response_data, f, indent=4)
                                f.close()
            # 并发执行
            else:
                for request_idx, propose_data in enumerate(propose_list):
                    process_one = AsyncPropose(propose_data, process_queue)
                    process_list.append(process_one)
                    process_one.start()
                if process_queue:
                    process_done = [process_queue.get() for process_one in process_list]
                    for response_dict in process_done:
                        response_todo.append(response_dict)
            # 解析结果
            replace_used = {}
            for response_dict in response_todo:
                source_cnt = 0
                for source_key, target_list in response_dict.items():
                    source_id = source_key
                    if source_key.endswith('_seed'):
                        source_id = source_key[:-5]
                    source_cnt += 1
                    target_cnt, target_log = 0, []
                    target_pool = []
                    if poolid:
                        for target_idx, target_one in enumerate(target_list):
                            if 'score' in target_one and target_one['score'] > 100:
                                target_pool.append(target_one)
                    for target_idx in range(len(target_list)):
                        target_key = (propose_from + target_idx) % len(target_list)
                        target_one = target_list[target_key]
                        if len(target_pool) > 0:
                            target_key = (propose_from + target_idx) % len(target_pool)
                            target_one = target_pool[target_key]
                        if 'id' not in target_one:
                            continue
                        target_id = target_one['id']
                        # 尺寸判断
                        if 'size' not in target_one:
                            target_log.append({'id': target_id, 'log': 'size_err'})
                            continue
                        target_size = target_one['size']
                        if len(target_size) < 3:
                            target_log.append({'id': target_id, 'log': 'size_err'})
                            continue
                        if target_id in FURNITURE_PROPOSE_ERROR:
                            target_log.append({'id': target_id, 'log': 'size_err'})
                            continue
                        if target_id in FURNITURE_PROPOSE_CLEAR:
                            target_log.append({'id': target_id, 'log': 'invalid'})
                            continue
                        if source_id in scope_dict:
                            scope_one = scope_dict[source_id]
                            object_role, object_type = scope_one['role'], scope_one['type']
                            object_min = scope_one['size_min']
                            object_max = scope_one['size_max']
                            if object_role in ['sofa', 'armoire', 'cabinet']:
                                if target_size[0] <= object_min[0] * 0.8:
                                    target_log.append({'id': target_id, 'log': 'size_min'})
                                    continue
                                elif target_size[2] >= object_max[2] * 1.2:
                                    target_log.append({'id': target_id, 'log': 'size_max'})
                                    continue
                            elif object_role in ['table'] and 'round' in object_type:
                                if target_size[2] >= object_max[2] * 1.2:
                                    target_log.append({'id': target_id, 'log': 'size_max'})
                                    continue
                            elif object_role in ['toilet']:
                                if target_size[0] >= object_max[0] * 2 or target_size[2] >= object_max[2] * 2:
                                    target_log.append({'id': target_id, 'log': 'size_max'})
                                    continue
                            elif 'cloth' in object_type or 'cloth' in object_role:
                                pass
                            elif 'pillow' in object_type or 'pillow' in object_role:
                                pass
                            elif object_role in ['accessory']:
                                if target_size[0] >= object_max[0] * 2:
                                    target_log.append({'id': target_id, 'log': 'size_max'})
                                    continue

                        # 重复判断
                        if source_id in decor_dict and source_id in scope_dict:
                            scope_one = scope_dict[source_id]
                            object_type = scope_one['type']
                            if 'pillow' in object_type:
                                pass
                            elif target_id in replace_used:
                                target_log.append({'id': target_id, 'log': 'same_err'})
                                continue
                            replace_used[target_id] = 1

                        # 数据记录
                        target_id, target_size = target_one['id'], target_one['size']
                        target_furniture_size[target_id] = target_size[:]
                        if 0 <= target_cnt < len(target_furniture):
                            target_furniture[target_cnt][source_id] = target_id
                        # 钢琴处理
                        if source_id in FURNITURE_PROPOSE_PIANO and target_cnt == 0:
                            target_furniture[target_cnt][source_id] = source_id
                            target_log.append({'id': target_id, 'log': 'type_err'})
                        else:
                            target_log.append({'id': target_id, 'log': 'ok'})
                        # 数量判断
                        target_cnt += 1
                        if target_cnt >= propose_num:
                            break
                    target_furniture_log[source_id] = target_log
        except Exception as e:
            # 打印信息
            layout_log_0 = 'propose failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
            layout_log_update(layout_log_0)
            layout_log_e = str(e)
            layout_log_update(layout_log_e)
            continue


# 家具推荐返回
def response_tran_list(response_list):
    replace_dict = {}
    for replace_idx, replace_one in enumerate(response_list):
        if replace_idx >= 20:
            break
        replace_orig_dict = replace_one['Virt2ModelMap']
        replace_size_dict = replace_one['ModelSizeMap']
        replace_score_dict = {}
        if 'ModelScoreMap' in replace_one:
            replace_score_dict = replace_one['ModelScoreMap']
        replace_score_mean = 0
        for source_id, replace_id in replace_orig_dict.items():
            if source_id not in replace_dict:
                replace_dict[source_id] = []
            if replace_id not in replace_size_dict:
                continue
            replace_score = replace_score_mean
            if replace_id in replace_score_dict:
                replace_score = replace_score_dict[replace_id]
            replace_size = replace_size_dict[replace_id]
            size_set = replace_size.split('&')
            if len(size_set) >= 3:
                size_x = float(size_set[0].split('=')[-1])
                size_z = float(size_set[1].split('=')[-1])
                size_y = float(size_set[2].split('=')[-1])
                if size_x <= -1 or size_y <= -1:
                    continue
                object_info = {'id': replace_id, 'size': [size_x, size_y, size_z], 'score': replace_score}
                replace_dict[source_id].append(object_info)
            else:
                continue
    return replace_dict


# 家具推荐返回
def response_tran_dict(response_dict):
    replace_dict = {}
    for target_key, target_val in response_dict.items():
        source_id = target_key
        replace_dict[source_id] = []
        for target_idx, target_one in enumerate(target_val):
            if target_idx >= 20:
                break
            if 'modelId' in target_one and 'x' in target_one and 'y' in target_one and 'z' in target_one:
                replace_id = target_one['modelId']
                size_x, size_z, size_y = target_one['x'], target_one['y'], target_one['z']
                if size_x <= -1 or size_y <= -1:
                    continue
                object_info = {'id': replace_id, 'size': [size_x, size_y, size_z], 'score': 0}
                replace_dict[source_id].append(object_info)
    return replace_dict


# 铺贴推荐服务
def propose_painting(seed_info, paint_info, room_type='', room_style='', poolid=None):
    for paint_key, paint_val in paint_info.items():
        paint_val['replaceId'] = paint_val['seekId']
    # 替换硬装
    try:
        get_material_seeds_service_with_hard_type(seed_info, room_type, paint_info, poolid=poolid)
    except Exception as e:
        # 打印信息
        layout_log_0 = 'propose_painting failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        layout_log_update(layout_log_0)
        layout_log_e = str(e)
        layout_log_update(layout_log_e)

    # 返回信息
    return paint_info


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


# 解析布局方案
def parse_scheme_layout(layout_info, propose_num=0, room_mirror=0):
    layout_source, layout_detail, layout_region, layout_overlap = {}, {}, {}, {}
    for room_key, room_layout in layout_info.items():
        if 'layout_scheme' not in room_layout:
            continue
        detail_list, region_list, overlap_list = [], [], []
        # 遍历布局
        for layout_idx, layout_one in enumerate(room_layout['layout_scheme']):
            if layout_idx == 0 and 'source_room' in layout_one:
                layout_source[room_key] = layout_one['source_room']
            # 推荐信息
            propose_zero = layout_one['group']
            if 'group_propose' in layout_one and len(layout_one['group_propose']) > 0:
                propose_list = layout_one['group_propose']
            else:
                propose_list = [propose_zero]
            if propose_num <= 0:
                propose_num = len(propose_list)
            # 遍历推荐
            for propose_idx in range(propose_num):
                # 方案信息
                propose_one, detail_one, region_one, overlap_one = [], [], [], []
                if 0 <= propose_idx < len(propose_list):
                    propose_one = propose_list[propose_idx]
                # 布局信息
                if len(propose_one) <= 0:
                    propose_one = propose_zero
                propose_entity = {}
                for group_one in propose_one:
                    # 实例标识
                    seed_list, keep_list, object_list = [], [], []
                    if 'seed_list' in group_one:
                        seed_list = group_one['seed_list']
                    if 'keep_list' in group_one:
                        keep_list = group_one['keep_list']
                    if 'obj_list' in group_one:
                        object_list = group_one['obj_list']
                    for object_one in object_list:
                        object_key = object_one['id']
                        if 'entityId' in object_one:
                            if object_key not in seed_list and object_key not in keep_list:
                                object_one.pop('entityId')
                    # 家具信息
                    group_new_1 = group_trans_detail(group_one, room_mirror, propose_entity)
                    for object_add in group_new_1:
                        detail_one.append(object_add)
                    # 叠加信息
                    group_new_2 = group_trans_overlap(group_one, room_mirror, '')
                    for object_add in group_new_2:
                        overlap_one.append(object_add)
                    # 区域信息
                    group_type = group_one['type']
                    if group_type in ['Meeting', 'Bed', 'Media', 'Work']:
                        front_rect, back_rect = compute_decorate_rect(group_one)
                        # 镜像
                        if room_mirror == 1:
                            for rect_one in [front_rect, back_rect]:
                                for point_one in rect_one:
                                    if len(point_one) >= 2:
                                        point_one[1] *= -1
                        # 吊顶
                        if len(front_rect) >= 0 and group_type in ['Meeting', 'Bed', 'Work']:
                            region_one.append({
                                'type': group_type + ' Region',
                                'boundingBox': front_rect
                            })
                        # 背景
                        if len(back_rect) >= 0 and group_type in ['Meeting', 'Bed', 'Media']:
                            region_one.append({
                                'type': group_type + ' Feature Wall',
                                'boundingBox': back_rect
                            })
                # 方案信息
                detail_list.append(detail_one)
                region_list.append(region_one)
                overlap_list.append(overlap_one)
        # 组装信息
        layout_detail[room_key] = detail_list
        layout_region[room_key] = region_list
        layout_overlap[room_key] = overlap_list
    # 返回信息
    return layout_source, layout_detail, layout_region, layout_overlap


# 解析布局方案
def parse_scheme_decorate(decorate_info, propose_num=0, room_mirror=0):
    decorate_dict = {}
    if 'room' in decorate_info:
        decorate_dict = decorate_info['room']
    layout_region = {}
    for room in decorate_dict:
        # 房间信息
        if 'construct_info' not in room:
            room['construct_info'] = {'id': room['id']}
        room_val = room['construct_info']
        room_key = room_val['id']
        room_type = ''
        if 'type' in room_val:
            room_type = room_val['type']
        # 区域信息
        region_list = []
        # 遍历布局
        for layout_idx in range(1):
            if propose_num <= 0:
                propose_num = 1
            # 遍历推荐
            for propose_idx in range(propose_num):
                # 方案信息
                region_one = []
                # 推荐信息
                ceiling_list = []
                if 'CustomizedCeiling' in room_val:
                    ceiling_list = room_val['CustomizedCeiling']
                for unit_idx, unit_one in enumerate(ceiling_list):
                    unit_type_old, unit_bbox_old = unit_one['type'], unit_one['layout_pts']
                    unit_type_new, unit_bbox_new = '', []
                    if unit_type_old in ['living', 'meeting']:
                        unit_type_new = 'Meeting'
                    elif unit_type_old in ['dining']:
                        unit_type_new = 'Dining'
                    elif unit_type_old in ['bed']:
                        unit_type_new = 'Bed'
                    elif unit_type_old in ['cabinet']:
                        unit_type_new = 'Cabinet'
                    elif unit_type_old in ['work']:
                        unit_type_new = 'Work'
                    elif unit_type_old in ['extra']:
                        continue
                    else:
                        continue
                    for point_old in unit_bbox_old:
                        point_new = point_old[:]
                        if room_mirror == 1:
                            if len(point_new) >= 2:
                                point_new[1] *= -1
                        unit_bbox_new.append(point_new)
                    region_one.append({
                        'type': unit_type_new + ' Region',
                        'boundingBox': unit_bbox_new
                    })
                # 方案信息
                region_list.append(region_one)
        # 组装信息
        layout_region[room_key] = region_list
    # 返回信息
    return layout_region


# 解析布局方案
def parse_update_region(layout_region_old, layout_region_new):
    for room_key, room_region_new in layout_region_new.items():
        if room_key not in layout_region_old:
            continue
        room_region_old = layout_region_old[room_key]
        for region_set_idx, region_set_new in enumerate(room_region_new):
            if region_set_idx < 0 or region_set_idx >= len(room_region_old):
                continue
            region_set_old = room_region_old[region_set_idx]
            for region_new in region_set_new:
                region_type, region_bbox = region_new['type'], region_new['boundingBox']
                region_find = False
                for region_old in region_set_old:
                    if region_old['type'] == region_type:
                        region_old['boundingBox'] = region_bbox
                        region_find = True
                if not region_find:
                    region_set_old.append(region_new)


# 家具推荐并发
class AsyncPropose(multiprocessing.Process):
    # 并行处理构造
    def __init__(self, input_new, output_new):
        multiprocessing.Process.__init__(self)
        self.input_set = input_new
        self.output_set = output_new

    # 并行处理执行
    def run(self):
        propose_dict = {}
        print('% 6d' % self.pid, 'from', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
        server_url = FURNITURE_PROPOSE_UAT
        for propose_data in self.input_set:
            request_data = {
                'appid': FURNITURE_PROPOSE_APP_ID,
                'userId': FURNITURE_PROPOSE_USR_ID,
                'DEBUG': 'true',
                'input_json': json.dumps(propose_data)
            }
            response_info = requests.post(server_url, data=request_data)
            response_data = response_info.json()
            response_good = False
            if 'result' in response_data and len(response_data['result']) > 0:
                if 'return_map' in response_data['result'][0]:
                    response_map = response_data['result'][0]['return_map']
                    response_dict = response_tran_dict(response_map)
                    if len(response_dict) > 0:
                        response_good = True
                elif 'returnCollectionList' in response_data['result'][0]:
                    response_list = response_data['result'][0]['returnCollectionList']
                    response_dict = response_tran_list(response_list)
                    if len(response_dict) > 0:
                        response_good = True
            if not response_good:
                response_info = requests.post(server_url, data=request_data)
                response_data = response_info.json()
                if 'return_map' in response_data['result'][0]:
                    response_map = response_data['result'][0]['return_map']
                    response_dict = response_tran_dict(response_map)
                    if len(response_dict) > 0:
                        response_good = True
                elif 'returnCollectionList' in response_data['result'][0]:
                    response_list = response_data['result'][0]['returnCollectionList']
                    response_dict = response_tran_list(response_list)
                    if len(response_dict) > 0:
                        response_good = True
        self.output_set.put(propose_dict)
        print('% 6d' % self.pid, 'done', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))

    pass


# 功能测试
if __name__ == '__main__':
    # 清空缓存
    layout_propose_clear()
    pass

    # 测试迁移
    layout_param_input = smart_decoration_input_transfer_test_00
    # layout_param_output = layout_propose_param(layout_param_input)
    pass

    # 测试推荐
    layout_param_input = smart_decoration_input_layout_test_09_v2
    layout_param_input = smart_decoration_input_layout_test_19_v2
    layout_param_input = smart_decoration_input_layout_test_99
    layout_param_output = layout_propose_param(layout_param_input, True)
    pass

    # 测试裂变
    layout_param_input = smart_decoration_input_split_test_91
    # layout_param_output = layout_propose_param(layout_param_input)
    layout_param_input = smart_decoration_input_split_test_92
    # layout_param_output = layout_propose_param(layout_param_input)
    layout_param_input = smart_decoration_input_split_test_93
    # layout_param_output = layout_propose_param(layout_param_input)
    pass

    # 测试机位
    layout_param_input = smart_decoration_input_wander_test_99
    # layout_param_output = layout_propose_param(layout_param_input, True)
    pass

    # 数据更新
    print()
    # save_furniture_data()
    pass
