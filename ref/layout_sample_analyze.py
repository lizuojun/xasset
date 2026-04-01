# -*- coding: utf-8 -*-
"""
@Author: lizuojun
@Date: 2021-04-19
@Description: 方案分析接口
"""

import os
import sys
import shutil

sys.path.append(os.path.dirname(__file__))

from LayoutByRule.house_interior_analyze import *
from LayoutByRule.house_interior_view import *

DATA_DIR_SERVER_SCHEME = os.path.dirname(__file__) + '/temp/scheme'
if not os.path.exists(DATA_DIR_SERVER_SCHEME):
    os.makedirs(DATA_DIR_SERVER_SCHEME)

# 布局机位房间
LAYOUT_VIEW_ROOM_TYPE = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library',
                         'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                         'MasterBathroom', 'SecondBathroom', 'Bathroom', 'Kitchen']


# 调整函数入口 增加选品
def layout_sample_analyze(house_info, scheme_mode='', struct_mode={}, replace_view={}):
    layout_info, group_info, region_info = house_rect_analyze(house_info)
    house_info['layout'] = layout_info

    # 户型信息
    house_id, room_id, scene_path = '', '', ''
    if 'id' in house_info:
        house_id = house_info['id']
    # 参数信息
    scheme_mode = scheme_mode.lower()
    save_mode, view_mode, path_mode = [], 0, -1
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
        path_mode = PATH_MODE_WANDER

    # 机位处理
    camera_dict = replace_view
    view_type = LAYOUT_VIEW_ROOM_TYPE[:]
    if len(layout_info) == 1:
        for room_key, room_val in layout_info.items():
            if 'room_type' in room_val and len(room_val['room_type']) > 0:
                view_type.append(room_val['room_type'])
    data_info, layout_info, scene_info, route_info = view_house(house_info, layout_info, camera_dict,
                                                                view_mode, path_mode, view_type)

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
            house_save(house_id, scene_path, 1, 0,
                       data_info, layout_info, {},
                       save_id, save_dir, save_mode, suffix_flag=False, sample_flag=True, upload_flag=False)
    # 打印信息
    layout_log_0 = 'analyze success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    print(layout_log_0)
    # 返回信息
    return house_info


# 机位函数入口
def layout_sample_camera(house_data_info, house_scene_outdoor='', room_alias_flag=True):
    # 房间布局
    house_layout_copy = {}
    if 'layout' in house_data_info:
        # 生成方案
        house_layout_copy = house_data_info['layout']
    # 房间外景
    if len(house_scene_outdoor) <= 0:
        house_scene_outdoor = 'sea_sky'
        if 'global_light_params' in house_data_info:
            if 'outdoor_scene' in house_data_info['global_light_params']:
                house_scene_outdoor = house_data_info['global_light_params']['outdoor_scene']
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
    # 房间机位
    house_camera_list = []
    room_sort, room_dict = correct_house_sort(house_layout_copy)
    for room_key in room_sort:
        if room_key not in house_layout_copy:
            continue
        room_layout_each = house_layout_copy[room_key]
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
            if 'wander' in room_scheme_each:
                room_wander_list = room_scheme_each['wander']
                if len(room_wander_list) > 0:
                    camera_list = room_wander_list[0]
                    for camera_one in camera_list:
                        room_wander_each.append(camera_one)
            # 房间别名
            room_ali = room_key
            if room_key in room_alias and room_alias_flag:
                room_ali = room_alias[room_key]
            room_anchor_door = []
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
                    room_anchor_set = room_scene_each['anchor_link']
                    for anchor_one in room_anchor_set:
                        anchor_new = anchor_one.copy()
                        if 'position_fix' in anchor_new:
                            anchor_new['position'] = anchor_new['position_fix'][:]
                            anchor_new.pop('position_fix')
                        anchor_key = anchor_one['id']
                        if anchor_key in room_alias and room_alias_flag:
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
                house_camera_list.append(room_scene_detail)
    # 打印信息
    layout_log_0 = 'camera success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    print(layout_log_0)
    return house_camera_list


# 相机布局
def view_house(house_info, layout_info={}, camera_dict={},
               view_mode=VIEW_MODE_SPHERE, path_mode=PATH_MODE_WANDER, view_type=[]):
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
        # 方案处理
        source_house, source_room = '', ''
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
            view_type = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library',
                         'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
        if room_type in view_type:
            # 计算机位
            camera_info = room_rect_view(room_data, room_layout_new, view_mode)
            wander_info = room_rect_path(room_data, room_layout_new, path_mode)
            # 传入机位
            camera_set, scene_set = [], []
            if room_key in camera_dict:
                camera_set = camera_dict[room_key]
            for camera_one in camera_set:
                scene_new = room_copy_view(camera_info)
                scene_new['camera'] = camera_one
                scene_set.append(scene_new)
            scheme_set = []
            if 'layout_scheme' in room_layout_new:
                scheme_set = room_layout_new['layout_scheme']
            for scheme_idx, scheme_one in enumerate(scheme_set):
                if len(scene_set) > 0:
                    scheme_one['scene'] = scene_set
            # 穿梭锚点
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
    return house_info, layout_info, scene_info, route_info


# 相机布局
def view_room(room_info, layout_info={}, camera_list={},
              view_mode=VIEW_MODE_SPHERE, path_mode=PATH_MODE_WANDER, view_type=[]):
    # step1 分析布局
    if len(layout_info) <= 0:
        layout_info, group_info, region_info = room_rect_analyze(room_info)
    # step2 机位处理
    camera_info, wander_info = {}, {}
    if len(room_info) > 0:
        room_key, room_data, room_layout_old, room_layout_new = room_info['id'], room_info, layout_info, {}
        # 方案处理
        source_house, source_room = '', ''
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
                         'MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom'
                         ]
        if room_type in view_type:
            # 计算机位
            camera_info = room_rect_view(room_data, room_layout_new, view_mode)
            wander_info = room_rect_path(room_data, room_layout_new, path_mode)
            # 传入机位 TODO:
            camera_set, scene_set = camera_list, []
            for camera_one in camera_set:
                scene_new = room_copy_view(camera_info)
                scene_new['camera'] = camera_one
                scene_set.append(scene_new)
            scheme_set = []
            if 'layout_scheme' in room_layout_new:
                scheme_set = room_layout_new['layout_scheme']
            for scheme_idx, scheme_one in enumerate(scheme_set):
                scheme_one['scene'] = scene_set
            # 穿梭锚点
            room_rect_link(room_data, room_layout_new, {}, view_type)
        else:
            room_null_view(room_data, room_layout_new)
            room_null_path(room_data, room_layout_new)
    return room_info, layout_info, camera_info, wander_info


# 布局模型解析
def parse_object_data(object_one, group_one={}, room_type=''):
    object_ref = {}
    object_key, object_grp, object_role, object_type, object_rely = '', '', '', '', ''
    if 'id' in object_one:
        object_key = object_one['id']
    if 'group' in object_one:
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
    # 重建
    if not os.path.exists(DATA_DIR_SERVER_SCHEME):
        os.makedirs(DATA_DIR_SERVER_SCHEME)


# 功能测试
if __name__ == '__main__':
    pass
