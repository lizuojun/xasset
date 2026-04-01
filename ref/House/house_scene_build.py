# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2020-09-01
@Description: 全屋重建接口

"""

import json
import requests
import datetime
from House.data_oss import *
from LayoutDecoration.recon_main import house_recon_pipeline
from LayoutDecoration.house_recon import ReconHouse, SceneJson
from LayoutDecoration.house_replace import ReplaceHouse

# 临时目录
DATA_DIR_SERVER_SCHEME = os.path.dirname(__file__) + '/../temp/scheme'
if not os.path.exists(DATA_DIR_SERVER_SCHEME):
    os.makedirs(DATA_DIR_SERVER_SCHEME)
# OSS位置
DATA_OSS_LAYOUT = 'ihome-alg-layout'
DATA_URL_LAYOUT = 'https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com'

# 渲染服务地址
RENDER_HSF_ENV = ''
RENDER_HSF_URL = ''
RENDER_HSF_PRE = 'mtop.uncenter.render-dispatcher.pre'
RENDER_HSF_PRO = 'mtop.uncenter.render-dispatcher'
RENDER_HSF_LOC = '11.22.140.164'
# 渲染服务前缀
RENDER_TASK_KEY = 'rd-test-render_'
# 房间类型转换
ROOM_BUILD_TYPE = {
    'LivingDiningRoom': 'LivingDiningRoom',
    'LivingRoom': 'LivingDiningRoom',
    'DiningRoom': 'LivingDiningRoom',
    'MasterBedroom': 'MasterBedroom',
    'SecondBedroom': 'MasterBedroom',
    'Bedroom': 'MasterBedroom',
    'KidsRoom': 'MasterBedroom',
    'ElderlyRoom': 'MasterBedroom',
    'NannyRoom': 'MasterBedroom',
    'Library': 'Library',

    'Kitchen': 'Kitchen',
    'MasterBathroom': 'Bathroom',
    'SecondBathroom': 'Bathroom',
    'Bathroom': 'Bathroom',
    'Balcony': 'Balcony',
    'Terrace': 'Balcony',
    'Lounge': 'Library',
    'LaundryRoom': 'Other',

    'Hallway': 'LivingDiningRoom',
    'Aisle': 'LivingDiningRoom',
    'Corridor': 'LivingDiningRoom',
    'Stairwell': 'LivingDiningRoom',
    'StorageRoom': 'Other',
    'CloakRoom': 'Other',
    'EquipmentRoom': 'Other',
    'Auditorium': 'Other',
    'OtherRoom': 'Other',
    'Courtyard': '',
    'Garage': '',

    'undefined': 'Other',
    'none': 'Other',
    '': ''
}


# 全屋场景构建
def house_build_house(house_data, house_layout, house_style='', house_mode={}):
    house_scene, house_outdoor = {}, {}
    try:
        build_mode = {
            'mesh': True,
            'customized_ceiling': False,
            'win_door': True,
            'mat': True,
            'floor_line': True,
            'bg_wall': True,
            'kitchen': True,
            'light': True,
            'debug': False,
            'white_list': True
        }
        for build_key, build_val in house_mode.items():
            if build_key in build_mode:
                build_mode[build_key] = build_val
        # 布局
        house_data = house_recon_pipeline(house_data, house_layout, house_style, build_mode=build_mode)
        # 外景
        house_outdoor = house_data['global_light_params']['outdoor_scene']
        # 重建
        ReconHouse(house_data)
        # 输出 scene json
        scene = SceneJson(house_data, house_layout)
        house_scene = scene.write_scene_json()
    except Exception as e:
        print('call hard recon error:', e)
        house_scene = {}
        house_outdoor = 'sea_sky'

    # 返回信息
    return house_scene, house_outdoor


# 全屋场景替换
def house_replace_house(house_data, house_layout, org_scene, replace_info, material_org={}, house_style='', house_mode={}):
    house_scene, house_outdoor = {}, {}
    # try:
    build_mode = {
        'mesh': True,
        'customized_ceiling': True,
        'win_door': True,
        'mat': True,
        'floor_line': True,
        'bg_wall': True,
        'kitchen': True,
        'light': True,
        'debug': False,
        'white_list': False,
        'replace': True
    }
    for build_key, build_val in house_mode.items():
        if build_key in build_mode:
            build_mode[build_key] = build_val
    # 布局
    house_data = house_recon_pipeline(house_data, house_layout, house_style, build_mode=build_mode)
    # 外景
    house_outdoor = house_data['global_light_params']['outdoor_scene']
    # 重建
    r = ReplaceHouse(house_data, org_scene, replace_info, material_org, view=False)
    house_scene, op_list = r.replace(house_layout)
    # except Exception as e:
    #     print('call hard recon error:', e)
    #     house_scene = {}
    #     house_outdoor = 'sea_sky'
    #     removed = []
    #     added = []
    #     op_list = []

    # 返回信息
    return house_scene, op_list


# 单屋场景构建
def house_build_room(room_data, room_layout, room_style='', room_mode={}, house_id='', mid_wall={}):
    house_data = {'id': house_id, 'room': [room_data]}
    if len(mid_wall) > 0:
        house_data['mid_wall'] = mid_wall
    house_layout = {room_data['id']: room_layout}
    # 机位窗帘检测
    if 'intersect' in room_data:
        intersect_data = room_data['intersect']
        if 'floor' in intersect_data and len(intersect_data['floor']) > 0:
            floor_set = intersect_data['floor']
            for scheme_one in room_layout['layout_scheme']:
                for group_one in scheme_one['group']:
                    if group_one['type'] in ['Window']:
                        obj_list_new = []
                        obj_list_old = group_one['obj_list']
                        for object_one in obj_list_old:
                            if object_one['type'].startswith('curtain'):
                                x_0, y_0 = object_one['position'][0], object_one['position'][2]
                                floor_inter = False
                                for floor_one in floor_set:
                                    if len(floor_one) < 4:
                                        continue
                                    x_1, y_1 = floor_one[0], floor_one[1]
                                    x_2, y_2 = floor_one[2], floor_one[3]
                                    if abs(x_1 - x_2) <= abs(y_1 - y_2):
                                        if abs(x_0 - x_1) < 0.2 and abs(x_0 - x_2) < 0.2:
                                            if min(y_1, y_2) < y_0 < max(y_1, y_2):
                                                floor_inter = True
                                                break
                                    else:
                                        if abs(y_0 - y_1) < 0.2 and abs(y_0 - y_2) < 0.2:
                                            if min(x_1, x_2) < x_0 < max(x_1, x_2):
                                                floor_inter = True
                                                break
                                if not floor_inter:
                                    obj_list_new.append(object_one)
                        group_one['obj_list'] = obj_list_new
    return house_build_house(house_data, house_layout, room_style, room_mode)


# 全屋数据转换
def house_build_trans(house_data, house_layout):
    global ROOM_BUILD_TYPE
    house_id = ''
    if 'id' in house_data:
        house_id = house_data['id']
    house_data_new, house_layout_new = {'id': house_id, 'room': []}, {}
    # 户型
    room_list_old, room_list_new, room_dict_old, room_dict_new = [], [], {}, {}
    if 'room' in house_data:
        room_list_old = house_data['room']
    for room_old in room_list_old:
        # 对照
        room_key_old = room_old['id']
        room_key_new = room_key_old
        room_type_old = room_old['type']
        room_type_new = room_type_old
        if room_type_old in ROOM_BUILD_TYPE:
            room_type_new = ROOM_BUILD_TYPE[room_type_old]
            room_key_new = '-'.join([room_type_new] + room_key_old.split('-')[1:])
        room_dict_old[room_key_old] = room_key_new
        room_dict_new[room_key_new] = {'id': room_key_old, 'type': room_type_old}
        # 新建
        room_new = room_old.copy()
        room_new['id'] = room_key_new
        room_new['type'] = room_type_new
        if 'floor' in room_old:
            room_new['floor'] = room_old['floor'][:]
        for unit_type in ['door_info', 'hole_info', 'window_info', 'baywindow_info']:
            if unit_type not in room_old:
                continue
            unit_list_old = room_old[unit_type]
            unit_list_new = []
            for unit_old in unit_list_old:
                unit_new = unit_old.copy()
                unit_list_new.append(unit_new)
                if 'to' in unit_new:
                    unit_type_old = unit_old['to'].split('-')[0]
                    unit_key_old = unit_old['to']
                    unit_key_new = unit_old['to']
                    if unit_type_old in ROOM_BUILD_TYPE:
                        unit_type_new = ROOM_BUILD_TYPE[unit_type_old]
                        unit_key_new = '-'.join([unit_type_new] + unit_old['to'].split('-')[1:])

                    room_dict_old[unit_key_old] = unit_key_new
                    room_dict_new[unit_key_new] = {'id': unit_key_old, 'type': unit_type_old}
            room_new[unit_type] = unit_list_new
        room_list_new.append(room_new)
    for room_new in room_list_new:
        for unit_type in ['door_info', 'hole_info', 'window_info', 'baywindow_info']:
            if unit_type not in room_new:
                continue
            unit_list_new = room_new[unit_type]
            for unit_new in unit_list_new:
                if 'to' in unit_new:
                    room_to_old = unit_new['to']
                    if room_to_old in room_dict_old:
                        unit_new['to'] = room_dict_old[room_to_old]
    house_data_new['room'] = room_list_new
    # 布局
    for room_key_old, room_layout_old in house_layout.items():
        room_key_new = room_key_old
        if room_key_old in room_dict_old:
            room_key_new = room_dict_old[room_key_old]
        room_layout_new = room_layout_old.copy()
        if 'room_type' in room_layout_old:
            room_type_old = room_layout_old['room_type']
            if room_type_old in ROOM_BUILD_TYPE:
                room_layout_new['room_type'] = ROOM_BUILD_TYPE[room_type_old]
        for scheme_type in ['layout_sample', 'layout_scheme']:
            if scheme_type not in room_layout_old:
                continue
            scheme_list_old = room_layout_old[scheme_type]
            scheme_list_new = []
            for scheme_old in scheme_list_old:
                scheme_new = scheme_old.copy()
                room_type_old = scheme_old['type']
                if room_type_old in ROOM_BUILD_TYPE:
                    scheme_new['type'] = ROOM_BUILD_TYPE[room_type_old]
                scheme_list_new.append(scheme_new)
            room_layout_new[scheme_type] = scheme_list_new
        house_layout_new[room_key_new] = room_layout_new
    return house_data_new, house_layout_new, room_dict_new


# 功能测试
if __name__ == '__main__':
    design_id = '0734059a-ba7e-44bc-a719-5ccffbff02ff'
