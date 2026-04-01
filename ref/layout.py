# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-09
@Description: 布局算法入口

"""
from ImportHouse.import_house import *
from LayoutByRule.layout_by_rule import *
from LayoutByRule.house_interior_view import *
from LayoutByRule.house_interior_analyze import *

# 临时数据目录
DATA_DIR_SERVER = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(DATA_DIR_SERVER):
    os.makedirs(DATA_DIR_SERVER)
DATA_DIR_SERVER_EMPTY = os.path.dirname(__file__) + '/temp/empty/'
if not os.path.exists(DATA_DIR_SERVER_EMPTY):
    os.makedirs(DATA_DIR_SERVER_EMPTY)
DATA_DIR_SERVER_INPUT = os.path.dirname(__file__) + '/temp/input/'
if not os.path.exists(DATA_DIR_SERVER_INPUT):
    os.makedirs(DATA_DIR_SERVER_INPUT)
DATA_DIR_SERVER_GROUP = os.path.dirname(__file__) + '/temp/group/'
if not os.path.exists(DATA_DIR_SERVER_GROUP):
    os.makedirs(DATA_DIR_SERVER_GROUP)
DATA_DIR_SERVER_SAMPLE = os.path.dirname(__file__) + '/temp/sample/'
if not os.path.exists(DATA_DIR_SERVER_SAMPLE):
    os.makedirs(DATA_DIR_SERVER_SAMPLE)
DATA_DIR_SERVER_SCHEME = os.path.dirname(__file__) + '/temp/scheme/'
if not os.path.exists(DATA_DIR_SERVER_SCHEME):
    os.makedirs(DATA_DIR_SERVER_SCHEME)
DATA_DIR_SERVER_RENDER = os.path.dirname(__file__) + '/temp/render/'
if not os.path.exists(DATA_DIR_SERVER_RENDER):
    os.makedirs(DATA_DIR_SERVER_RENDER)
DATA_DIR_SERVER_SERVICE = os.path.dirname(__file__) + '/temp/service/'
if not os.path.exists(DATA_DIR_SERVER_SERVICE):
    os.makedirs(DATA_DIR_SERVER_SERVICE)


# 全屋布局
def layout_house_by_id(house_id, sample_num=3, sample_id='', sample_idx=-1, seed_mode=LAYOUT_SEED_PROPOSE):
    # step1 导入户型 产生布局所需数据，包括：户型信息、户型特征、推荐功能区
    house_data_info, house_feature_info, house_layout_info = \
        import_house(house_id, sample_num, sample_id, sample_idx, seed_mode)
    if len(house_data_info) <= 0 or len(house_layout_info) <= 0:
        print('layout house: import error.')
        return house_data_info, house_layout_info, {}, {}
    else:
        print('layout house: import ok.')
    # step2 全屋布局
    house_region_info, house_propose_info = layout_by_rule(house_data_info, house_layout_info, sample_id)
    print('layout house: layout by rule ok.')
    # 返回信息
    return house_data_info, house_layout_info, house_propose_info, house_region_info


# 全屋布局
def layout_house_by_index(house_idx, sample_num=3, sample_id='', sample_idx=-1, seed_mode=LAYOUT_SEED_PROPOSE):
    house_list = list_house_oss(DATA_OSS_HOUSE_EMPTY, house_idx, 1)
    if len(house_list) < 1:
        return '', {}, {}, {}, {}
    house_id = house_list[0]
    house_data_info, house_layout_info, house_propose_info, house_region_info = \
        layout_house_by_id(house_id, sample_num, sample_id, sample_idx, seed_mode)
    # 返回信息
    return house_id, house_data_info, house_layout_info, house_propose_info, house_region_info


# 全屋布局
def layout_house_by_json(house_json, sample_num=3, sample_id='', sample_idx=-1, seed_mode=LAYOUT_SEED_PROPOSE):
    # step1 导入户型 目标产生布局所需数据，包括：户型信息、户型特征、推荐功能区
    house_data_info, house_feature_info, house_layout_info = \
        import_house_by_json(house_json, sample_num, sample_id, sample_idx, seed_mode)
    if len(house_data_info) <= 0 or len(house_layout_info) <= 0:
        print('layout house: import error.')
        return house_data_info, house_layout_info, {}, {}
    else:
        print('layout house: import ok.')
    # step2 全屋布局
    house_region_info, house_propose_info = layout_by_rule(house_data_info, house_layout_info)
    print('layout house: layout by rule ok.')
    # 返回信息
    return house_data_info, house_layout_info, house_propose_info, house_region_info


# 全屋布局
def layout_house_by_info(house_info, sample_num=3, sample_id='', sample_idx=-1, seed_mode=LAYOUT_SEED_PROPOSE):
    # step1 导入户型
    house_data_info, house_feature_info, house_layout_info = \
        import_house_by_info(house_info, sample_num, sample_id, sample_idx, seed_mode)
    if len(house_data_info) <= 0 or len(house_layout_info) <= 0:
        print('layout house: import error.')
        return house_data_info, house_layout_info, {}, {}
    else:
        print('layout house: import ok.')
    # step2 全屋布局
    house_region_info, house_propose_info = layout_by_rule(house_data_info, house_layout_info)
    print('layout house: layout by rule ok.')
    # 返回信息
    return house_data_info, house_layout_info, house_propose_info, house_region_info


# 全屋布局
def layout_house_by_sample(house_info, sample_info, replace_info={}, replace_note={}, refine_mode=0):
    # step1 导入户型
    house_data_info, house_feature_info, house_layout_info = \
        import_house_by_sample(house_info, sample_info, replace_info, replace_note)
    print('layout house: import ok.')
    # step2 全屋布局
    house_region_info, house_propose_info = layout_by_rule(house_data_info, house_layout_info)
    print('layout house: layout by rule ok.')
    # step3 全屋替换
    adjust_house(house_layout_info, house_propose_info)
    refine_house(house_layout_info, refine_mode)
    pass
    # 返回信息
    return house_data_info, house_layout_info, house_propose_info, house_region_info


# 全屋特征
def layout_house_by_refer(house_info, sample_num=3):
    # step1 导入户型
    house_data_info, house_feature_info, house_layout_info = import_house_by_info(house_info, sample_num, sample_id='', sample_idx=-1, seed_mode=LAYOUT_SEED_ADVICE)
    if len(house_data_info) <= 0 or len(house_layout_info) <= 0:
        print('layout house: import error.')
        return house_data_info, house_layout_info, {}, {}
    else:
        print('layout house: import ok.')
    # step2 全屋布局
    house_region_info, house_propose_info, group_type_main = layout_by_rule_house_refer(house_data_info, house_layout_info)
    print('layout house: layout by rule ok.')
    # 返回信息
    return house_data_info, house_layout_info, house_propose_info, house_region_info


# 全屋布局 定制柜体
def layout_house_by_refer_customized(house_info, sample_num=3):
    # step1 导入户型
    house_data_info, house_feature_info, house_layout_info = import_house_by_info(house_info, sample_num)
    if len(house_data_info) <= 0 or len(house_layout_info) <= 0:
        print('layout house: import error.')
        return house_data_info, house_layout_info, {}, {}
    else:
        print('layout house: import ok.')
    # step2 全屋布局
    house_region_info, house_propose_info, group_type_main = layout_by_rule_house_refer(house_data_info, house_layout_info)
    print('layout house: layout by rule ok.')
    # step3 定制柜布局
    house_region_info = house_rect_region_customized(house_info, house_layout_info, group_type_main)
    # 返回信息
    return house_data_info, house_layout_info, house_propose_info, house_region_info


# 单屋布局
def layout_room_by_info(room_info, sample_num=3, sample_id='', sample_room_id='', seed_mode=LAYOUT_SEED_PROPOSE):
    # 布局信息
    room_data_info, room_layout_info, room_propose_info, room_region_info = room_info, {}, [], {}
    # step1 导入户型
    room_layout_info = import_room_detail(room_info, sample_num, sample_id, sample_room_id, seed_mode)
    # step2 单屋布局
    room_region_info, room_propose_info = layout_by_rule_room(room_data_info, room_layout_info)
    # 返回信息
    return room_data_info, room_layout_info, room_propose_info, room_region_info


# 单屋布局
def layout_room_by_sample(room_info, sample_info, replace_list=[], replace_note={}, refine_mode=0):
    # step1 导入户型
    layout_info = import_room_by_sample(room_info, sample_info, replace_list, replace_note)
    room_data_info, room_layout_info = room_info, layout_info
    # step2 单屋布局
    room_region_info, room_propose_info = layout_by_rule_room(room_data_info, room_layout_info)
    # step3 单屋替换
    adjust_room(room_layout_info, room_propose_info)
    refine_room(room_layout_info, refine_mode)
    # 返回信息
    return room_data_info, room_layout_info, room_propose_info, room_region_info


# 单屋特征
def layout_room_by_refer(room_info, sample_num=3):
    # 布局信息
    room_data_info, room_layout_info, room_propose_info, room_region_info = room_info, {}, [], {}
    # step1 导入户型
    room_layout_info = import_room_detail(room_info, sample_num, '', '', LAYOUT_SEED_ADVICE)
    # step2 单屋布局
    room_region_info, room_propose_info = layout_by_rule_room_refer(room_data_info, room_layout_info)
    # 返回信息
    return room_data_info, room_layout_info, room_propose_info, room_region_info


# 单屋布局
def layout_room_by_group(room_info, group_list):
    # step1 导入户型
    layout_info = import_room_by_group(room_info, group_list)
    room_data_info, room_layout_info = room_info, layout_info
    # step2 单屋布局
    room_region_info, room_propose_info = layout_by_rule_group(room_data_info, room_layout_info)
    # 返回信息
    return room_data_info, room_layout_info, room_propose_info, room_region_info


# 全屋替换
def replace_house(house_info, replace_info):
    # 布局信息
    house_data_info, house_layout_info, house_propose_info, house_region_info = house_info, {}, {}, {}
    # step1 导入户型
    house_layout_info = import_house_self(house_info, replace_info)
    # step2 全屋替换
    house_region_info, house_propose_info = replace_by_rule(house_data_info, house_layout_info)
    # 返回信息
    return house_data_info, house_layout_info, house_propose_info, house_region_info


# 单屋替换
def replace_room(room_info, replace_soft):
    # 布局信息
    room_data_info, room_layout_info, room_propose_info, room_region_info = room_info, {}, [], {}
    # step1 导入户型
    room_layout_info = import_room_self(room_info, replace_soft)
    # step2 单屋替换
    room_region_info, room_propose_info = replace_by_rule_room(room_data_info, room_layout_info)
    # 返回信息
    return room_data_info, room_layout_info, room_propose_info, room_region_info


# 全屋调整
def adjust_house(layout_info, propose_info, adjust_mode=0):
    house_rect_adjust(layout_info, propose_info, adjust_mode)


# 单屋调整
def adjust_room(layout_info, propose_info, adjust_mode=0):
    room_rect_adjust(layout_info, propose_info, adjust_mode)


# 全屋优化
def refine_house(layout_info, raise_mode=1):
    house_rect_raise(layout_info, raise_mode)
    house_rect_erase(layout_info)


# 单屋优化
def refine_room(layout_info, raise_mode=1):
    room_rect_raise(layout_info, raise_mode)
    room_rect_erase(layout_info)


# 打组布局
def group_house(house_info, check_mode=1):
    layout_info, group_info, region_info = house_rect_analyze(house_info)
    house_data_info, house_layout_info, house_group_info = house_info, layout_info, group_info
    return house_data_info, house_layout_info, house_group_info


# 打组布局
def group_room(room_info, check_mode=1):
    layout_info, group_info, region_info = room_rect_analyze(room_info)
    room_data_info, room_layout_info, room_group_info = room_info, layout_info, group_info
    return room_data_info, room_layout_info, room_group_info


# 相机布局
def view_house(house_info, layout_info={}, view_mode=VIEW_MODE_SPHERE, path_mode=PATH_MODE_WANDER, view_type=[]):
    # step1 分析布局
    if len(layout_info) <= 0:
        layout_info, group_info, region_info = house_rect_analyze(house_info)
    room_list = []
    if 'room' in house_info:
        room_list = house_info['room']
    # step2 机位处理
    scene_info, route_info = {}, {}
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
        # 房间信息
        room_type, room_area, room_link = '', 10, []
        if 'type' in room_info:
            room_type = room_info['type']
        if 'area' in room_info:
            room_area = room_info['area']
        if 'link' in room_info:
            room_link = room_info['link']
        # 更新处理
        room_layout_new = room_layout_old.copy()
        layout_info[room_key] = room_layout_new
        # 房间机位
        if len(view_type) <= 0:
            view_type = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                         'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                         'Library',
                         'Kitchen',
                         'MasterBathroom', 'SecondBathroom', 'Bathroom']
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
    return house_info, layout_info, scene_info, route_info


# 相机布局
def view_room(room_info, layout_info={}, view_mode=VIEW_MODE_SPHERE, path_mode=PATH_MODE_WANDER, view_type=[]):
    # step1 分析布局
    if len(layout_info) <= 0:
        layout_info, group_info, region_info = room_rect_analyze(room_info)
    # step2 机位处理
    camera_info, wander_info = {}, {}
    if len(room_info) > 0:
        room_key, room_data, room_layout_old, room_layout_new = room_info['id'], room_info, layout_info, {}
        source_house, source_room, room_sample_set = '', '', []
        # 方案处理
        if 'layout_scheme' in room_layout_old and len(room_layout_old['layout_scheme']) > 0:
            scheme_one = room_layout_old['layout_scheme'][0]
            if 'source_house' in scheme_one:
                source_house = scheme_one['source_house']
                source_house = source_house.lstrip('sample_house_')
            if 'source_room' in scheme_one:
                source_room = scheme_one['source_room']
        # 房间信息
        room_type, room_area, room_link = '', 10, []
        if 'type' in room_info:
            room_type = room_info['type']
        if 'area' in room_info:
            room_area = room_info['area']
        if 'link' in room_info:
            room_link = room_info['link']
        # 更新处理
        room_layout_new = room_layout_old.copy()
        layout_info[room_key] = room_layout_new
        # 房间机位
        if len(view_type) <= 0:
            view_type = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                         'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                         'Library',
                         'Kitchen',
                         'MasterBathroom', 'SecondBathroom', 'Bathroom']
        if room_type in view_type:
            camera_info = room_rect_view(room_data, room_layout_new, view_mode)
            wander_info = room_rect_path(room_data, room_layout_new, path_mode)
            room_rect_link(room_data, room_layout_new, {}, view_type)
        else:
            room_null_view(room_data, room_layout_new)
            room_null_path(room_data, room_layout_new)
    return room_info, layout_info, camera_info, wander_info


# 功能测试
if __name__ == '__main__':
    # 单批布局
    house_id = '355ab8b3-1609-4346-8202-1546938d57f2'
    house_data_info, house_layout_info, house_propose_info, house_region_info = layout_house_by_id(house_id)

    # 批量布局
    house_list_test = list_house_oss(DATA_OSS_HOUSE_FINE, 0, 10)
    for house_idx, house_id in enumerate(house_list_test):
        print()
        print('layout house:', house_idx)
        # 布局
        sample_num, sample_id, sample_idx = 0, '', house_idx % 10
        house_data_info, house_layout_info, house_propose_info, house_region_info = \
            layout_house_by_id(house_id, sample_num, sample_id, sample_idx)
