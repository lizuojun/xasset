# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2021-09-05
@Description: 种子替换接口

"""

import os
import sys
import traceback

sys.path.append(os.path.dirname(__file__))

from layout_def import *
from House.house_scene_render import *
from House.house_scene_build import house_replace_house
from Extract.group_material import house_data_group_wall
from Extract.group_win_door import house_data_group_win_door
from Extract.group_feature_wall import house_data_group_feature_wall

from HouseSearch.house_seed import *
from HouseSearch.house_search_main import house_search_get_sample_info
from ImportHouse.room_search import *

# 布局服务计数
LAYOUT_SAMPLE_CNT = 0
LAYOUT_SAMPLE_LOC = ''

# 临时目录
DATA_DIR_SERVER_INPUT = os.path.dirname(__file__) + '/temp/input/'
if not os.path.exists(DATA_DIR_SERVER_INPUT):
    os.makedirs(DATA_DIR_SERVER_INPUT)
DATA_DIR_SERVER_SCHEME = os.path.dirname(__file__) + '/temp/scheme/'
if not os.path.exists(DATA_DIR_SERVER_SCHEME):
    os.makedirs(DATA_DIR_SERVER_SCHEME)
# 设计目录
DATA_DIR_RECORD = os.path.dirname(__file__) + '/LayoutRecord/'
if not os.path.exists(DATA_DIR_RECORD):
    os.makedirs(DATA_DIR_RECORD)

# 组合服务位置
DATA_OSS_LAYOUT = 'ihome-alg-layout'
DATA_URL_LAYOUT = 'https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com'


# 布局服务入口
def layout_sample_replace(param_info):
    # 户型参数
    house_id, room_id, plat_id, plat_entity = '', '', '', ''
    house_data, room_data = {}, {}
    house_replace, room_replace, note_replace = {}, {}, {}
    if 'house_id' in param_info:
        house_id = param_info['house_id']
    if 'room_id' in param_info:
        room_id = param_info['room_id']
    if 'plat_id' in param_info:
        plat_id = param_info['plat_id']
    if 'plat_entity' in param_info:
        plat_entity = param_info['plat_entity']
    if 'house_data' in param_info:
        house_data = param_info['house_data']
    if 'room_data' in param_info:
        room_data = param_info['room_data']
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
    data_url, scene_url, image_url, scene_path = '', '', '', ''
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
    # 布局模式
    layout_mode = LAYOUT_MODE_SEEDS
    if 'layout_mode' in param_info:
        layout_mode = int(param_info['layout_mode'])
    layout_num, propose_num = 2, 2
    if layout_mode == LAYOUT_MODE_ADJUST:
        layout_num, propose_num = 1, 1
    if 'layout_number' in param_info:
        layout_num = param_info['layout_number']
    if 'propose_number' in param_info:
        propose_num = param_info['propose_number']
    # 商品参数
    item_id = ''
    # 场景参数
    scene_list = []

    # 保存模式
    render_mode, scheme_mode = '', ''
    save_mode = []
    if 'render_mode' in param_info:
        render_mode = str(param_info['render_mode']).lower()
    if 'scheme_mode' in param_info:
        scheme_mode = str(param_info['scheme_mode']).lower()
        if 'image' in scheme_mode:
            save_mode.append(SAVE_MODE_IMAGE)
        if 'frame' in scheme_mode:
            save_mode.append(SAVE_MODE_FRAME)
        if 'render' in scheme_mode:
            save_mode.append(SAVE_MODE_RENDER)
        if 'layout' in scheme_mode:
            save_mode.append(SAVE_MODE_LAYOUT)
        if 'group' in scheme_mode:
            save_mode.append(SAVE_MODE_GROUP)
    if len(save_mode) <= 0:
        save_mode.append(SAVE_MODE_GROUP)

    # 组合信息
    house_layout_info, house_group_info = {}, {}
    decoration_operate, furniture_operate = {}, {}
    scene_loc_new, scene_url_new = '', ''
    try:
        # 打印信息
        print()
        layout_log_0 = 'layout replace ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        if not house_id == '':
            layout_log_0 = 'target house: %s, room: %s, plat: %s' % (house_id, room_id, plat_id)
            print(layout_log_0)
        elif not design_id == '':
            layout_log_0 = 'target house: %s, room: %s' % (design_id, room_id)
            print(layout_log_0)
        elif not plat_id == '':
            layout_log_0 = 'target plat: %s' % plat_id
            print(layout_log_0)
        # 户型参数
        if len(house_data) <= 0 and len(room_data) <= 0:
            house_para_info, house_data_info = {}, {}
            # design id
            if len(house_data_info) <= 0 and not design_id == '':
                house_para_info, house_data_info = parse_design_data(design_id, design_url, scene_url)
                if 'id' in house_data_info:
                    house_id = design_id
                    house_data_info['id'] = design_id
                if 'room' in house_data_info and len(house_data_info['room']) <= 0:
                    house_data_info = {}
            # house id
            if len(house_data_info) <= 0 and scene_url == '' and not house_id == '':
                house_id_new, house_data_info, house_feature_info = get_house_data_feature(house_id, True)
                house_data = house_data_info

            # 户型轮廓 TODO:
            if len(house_data_info) <= 0 and not data_url == '':
                pass
            # 户型场景
            if len(house_data_info) <= 0 and not scene_url == '':
                house_have, scene_path = download_scene_by_url(scene_url, DATA_DIR_SERVER_INPUT)
                if house_have and os.path.exists(scene_path):
                    house_id_new, house_data_info, house_feature_info = get_house_data_feature_by_path(scene_path)
                    if len(house_id) <= 0 and len(house_id_new) > 0:
                        house_id = house_id_new
            # 户型图片 TODO:
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
        # 保存参数
        if SAVE_MODE_SCENE in save_mode:
            if scene_url == '' and not design_id == '':
                scene_url = house_scene_url(design_id)

        # 组合提取
        if len(room_data) > 0 and 'furniture_info' in room_data:
            if 'id' in room_data and room_id == '':
                room_id = room_data['id']
            if 'coordinate' not in room_data:
                room_data['coordinate'] = 'xyz'
            if 'unit' not in room_data:
                room_data['unit'] = 'm'
            room_data_info, room_scheme_info, room_group_info = group_room(room_data)
            if len(room_group_info) > 0:
                house_group_info[room_id] = room_group_info
            if len(room_scheme_info) > 0:
                house_layout_info[room_id] = room_scheme_info
        # 组合提取
        elif len(house_data) > 0 and 'room' in house_data:
            if 'id' in house_data and house_id == '':
                house_id = house_data['id']
            room_list = []
            if 'room' in house_data:
                room_list = house_data['room']
            for room_one in room_list:
                if 'coordinate' not in room_one:
                    room_one['coordinate'] = 'xyz'
                if 'unit' not in room_one:
                    room_one['unit'] = 'm'
            house_data_info, house_layout_info, house_group_info = group_house(house_data)

        # 装修替换
        if len(house_layout_info) > 0 and len(house_replace) > 0:
            if len(scene_path) == 0:
                house_have, scene_path = download_scene_by_url(scene_url, DATA_DIR_SERVER_INPUT)
            house_data_info = house_data_group_win_door(house_id, house_data_info, house_layout_info, upload=False)
            house_data_info = house_data_group_wall(house_id, house_data_info, house_layout_info, False)
            house_data_info = house_data_group_feature_wall(house_id, house_data_info, house_layout_info, False)
            house_scene_json, decoration_operate, furniture_operate = \
                replace_house_both(house_data_info, house_layout_info, scene_path, house_replace)
            scene_loc_new = scene_path
            if 'scene' in scheme_mode:
                # 户型保存
                save_id = house_id
                if save_id == '':
                    if len(house_layout_info) <= 0:
                        save_id = 'null'
                    elif len(house_layout_info) == 1:
                        save_id = 'room'
                    else:
                        save_id = 'house'
                save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
                save_time = datetime.datetime.now().strftime('%H-%M-%S')
                json_path = os.path.join(save_dir, save_id + '_new.json')
                with open(json_path, "w") as f:
                    # json.dump(house_scene_json, f, indent=4)
                    json.dump(house_scene_json, f)
                    f.close()
                # 户型上传
                scene_url_new = house_scene_upload(house_scene_json, save_id, json_path)
                # 户型位置
                scene_loc_new = json_path
            scene_each = {
                'id': house_id,
                'url': scene_url_new,
                'loc': scene_loc_new,
                'layout': house_layout_info
            }
            scene_list.append(scene_each)

        # 打印信息
        layout_log_0 = 'layout replace success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        # 保存信息
        if len(save_mode) > 0:
            save_id = house_id
            save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
            upload_group, upload_room = False, False
            if SAVE_MODE_RENDER in save_mode:
                pass
            elif SAVE_MODE_GROUP in save_mode:
                group_save(house_group_info, save_id, save_dir, 10, 15, save_mode, upload_group, upload_room)
            if len(save_mode) > 0:
                house_save(house_id, '', 1, 1, house_data_info, house_layout_info, {}, house_id + '_sample',
                           save_dir, save_mode, suffix_flag=False, sample_flag=False, upload_flag=False)
        # 打印信息
        layout_log_0 = 'layout replace success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        print(house_replace)
    except Exception as e:
        layout_log_0 = 'layout replace failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        traceback.print_exc()
        print(layout_log_0)
        print(e)

    # 计数信息
    layout_sample_count()

    # 镜像信息
    room_mirror = 0
    if len(room_data) > 0 and 'mirror' in room_data:
        room_mirror = room_data['mirror']
    elif len(house_data) > 0 and 'room' in house_data:
        for room_one in house_data['room']:
            if len(room_one) > 0 and 'mirror' in room_one:
                room_mirror = room_one['mirror']
                break

    # 输出处理
    layout_version = '20210915.1200'
    layout_output = {
        'house_id': house_id,
        'room_id': room_id,
        'scene_url': scene_url_new,
        'decoration_operate': decoration_operate,
        'furniture_operate': furniture_operate,
        'image_key': [],
        'image_val': [],
        'layout_version': layout_version
    }

    # 渲染信息 TODO:
    if SAVE_MODE_RENDER in save_mode:
        for scene_each in scene_list:
            # 户型位置
            scene_key, scene_path, scene_layout = scene_each['id'], scene_each['loc'], scene_each['layout']
            scene_key_old, scene_key_new = '', ''
            save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, scene_key)
            house_scene_json = json.load(open(scene_path, 'r', encoding='utf-8'))
            # 装修渲染
            if 'decorate' in render_mode:
                item_id = 'decorate'
                # 户型保存
                save_time = datetime.datetime.now().strftime('%H-%M-%S')
                save_id = scene_key
                json_path = os.path.join(save_dir, save_id + '.json')
                with open(json_path, "w") as f:
                    # json.dump(house_scene_json, f, indent=4)
                    json.dump(house_scene_json, f)
                    f.close()
                # 户型上传
                scene_key_new = house_scene_upload(house_scene_json, save_id, json_path)
    # 图片信息
    if 'result' in render_mode:
        # 位置
        save_id = plat_id
        if len(item_id) > 0:
            save_id = item_id
        save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        # 图片
        key_list, val_list = [], []
        if 'image_key' in layout_output:
            key_list = layout_output['image_key']
        if 'image_val' in layout_output:
            val_list = layout_output['image_val']
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
        save_id = plat_id
        if len(plat_id) > 0:
            save_id = plat_id
        elif len(item_id) > 0:
            save_id = item_id
        elif len(house_id) > 0:
            save_id = house_id
        save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        save_des = os.path.join(save_dir, save_id + '_output.json')
        with open(save_des, "w") as f:
            json.dump(layout_output, f, indent=4)
            f.close()

    # 返回信息
    return layout_output


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


# 调整服务入口 增加选品
def layout_sample_adjust(house_info, object_add, room_key):
    house_layout_copy = {}
    if 'layout' in house_info:
        house_layout_copy = house_info['layout']
    if len(house_layout_copy) > 0:
        correct_house_move(house_layout_copy, object_add, room_key)


# 布局户型解析
def parse_design_data(design_id, design_url, scene_url=''):
    house_para_info, house_data_info = get_house_data(design_id, design_url, scene_url)
    if 'id' in house_data_info:
        house_id = design_id
        house_data_info['id'] = design_id
    if 'room' not in house_data_info:
        house_para_info, house_data_info = {}, {}
    elif 'room' in house_data_info and len(house_data_info['room']) <= 0:
        house_para_info, house_data_info = {}, {}
    return house_para_info, house_data_info


# 种子替换处理
def replace_house_both(house_info, layout_info, scene_path='', replace_info={}, replace_note={}):
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
        # 软装
        for object_key in replace_soft:
            # 添加
            if object_key not in replace_note:
                object_type, object_style, object_size = get_furniture_data(object_key)
                object_new = {
                    'id': object_key, 'type': object_type, 'style': object_style,
                    'size': object_size[:], 'scale': [1, 1, 1],
                    'position': [0, 0, 0], 'rotation': [0, 0, 0, 1]
                }
                replace_note[object_key] = object_new
            # 类型
            object_new = replace_note[object_key]
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
    paint_replace, material_org = {}, {}
    for room_key, room_fix in replace_info.items():
        if room_key not in layout_info:
            continue
        layout_one, scheme_set = layout_info[room_key], []
        if 'layout_scheme' in layout_one:
            scheme_set = layout_one['layout_scheme']
        for scheme_one in scheme_set:
            # 硬装替换
            material_old, material_new = {}, {}
            if 'material' in scheme_one:
                material_old = scheme_one['material']
            material_new['id'], material_new['type'] = material_old['id'], material_old['type']
            # update_room_layout_material_seed(material_new, room_fix)
            # paint_replace[room_key] = {'material_old': material_old, 'material_new': material_new}
            replace_mat = update_room_replace_material_seed(material_new, room_fix)
            if len(replace_mat) > 0:
                paint_replace[room_key] = replace_mat
                scheme_one['material'] = material_new
            material_org[room_key] = material_old

    # 原有场景
    scene_json_old = {}
    if len(scene_path) > 0 and os.path.exists(scene_path):
        scene_json_old = json.load(open(scene_path, 'r', encoding='utf-8'))
    # 更新场景 硬装处理
    scene_json_new, decoration_operate = \
        house_replace_house(house_info, layout_info, scene_json_old, paint_replace, material_org)
    # 更新场景 软装处理
    scene_json_new, furniture_operate = \
        replace_house_soft(house_info, layout_info, replace_info, replace_note, scene_json_new)

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
        replace_used = []
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
        room_val['used'] = replace_used
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
    return scene_json_new, decoration_operate, furniture_operate


# 硬装替换处理 TODO:
def replace_house_deco():
    pass


# 软装替换处理
def replace_house_soft(house_info, layout_info, replace_info={}, replace_note={}, scene_json_old={}):
    scene_json_new, furniture_remove, furniture_append = scene_json_old, [], {}
    # 房间信息
    room_list = []
    if 'room' in house_info:
        room_list = house_info['room']
    house_sample = house_search_get_sample_info(house_info, replace_info, replace_note, 1, '')
    house_operate = {}
    # 遍历房间
    house_layout = layout_info
    for room_one in room_list:
        # 房间信息
        room_key, room_type, room_area = room_one['id'], room_one['type'], room_one['area']
        if room_key not in house_layout or room_key not in replace_info:
            continue
        room_data, room_sample, room_replace = room_one, house_layout[room_key], replace_info[room_key]
        replace_soft, replace_dict, replace_size, replace_done = [], {}, {}, []
        if 'soft' in room_replace:
            replace_soft = room_replace['soft']
        # 方案信息
        scheme_old, scheme_new, group_have, group_func = {}, {}, [], []
        if 'layout_scheme' in room_sample and len(room_sample['layout_scheme']) > 0:
            scheme_old = room_sample['layout_scheme'][0]
            group_have = scheme_old['group']
        for group_idx, group_one in enumerate(group_have):
            if group_one['type'] in GROUP_RULE_FUNCTIONAL:
                group_func.append(group_one)
        for object_idx, object_key in enumerate(replace_soft):
            object_type, object_style, object_cate_id = '', '', ''
            if object_key in replace_note:
                object_one = replace_note[object_key]
                if 'type' in object_one:
                    object_type = object_one['type']
                if 'style' in object_one:
                    object_style = object_one['style']
                if 'category' in object_one:
                    object_cate_id = object_one['category']
                elif 'categories' in object_one and len(object_one['categories']) >= 1:
                    object_cate_id = object_one['categories'][0]
                    object_one['category'] = object_cate_id
                # 纠正模型
                correct_object_type(object_one, object_type, room_type)
                object_type = object_one['type']
                origin_size, origin_scale = object_one['size'], object_one['scale']
                object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
            else:
                object_type, object_style, object_size, object_type_id, object_style_id, object_category_id = \
                    get_furniture_data_more(object_key)
                object_one = {
                    'id': object_key, 'type': object_type, 'style': object_style,
                    'size': object_size[:], 'scale': [1, 1, 1], 'category': object_category_id,
                    'position': [0, 0, 0], 'rotation': [0, 0, 0, 1],
                }
                replace_note[object_key] = object_one
            # 计算角色
            object_group, object_role = \
                compute_furniture_role(object_type, object_size, room_type, object_key, object_cate_id)
            object_one['group'], object_one['role'] = object_group, object_role
        # 布局处理
        room_layout = {}
        group_find, group_todo, group_done = [], [], []
        # 分支0:空白布局
        if len(group_func) <= 0:
            room_sample_set = []
            for sample_data_info in house_sample:
                if room_key in sample_data_info['sample']:
                    room_sample_set.append(sample_data_info['sample'][room_key])
            if len(room_sample_set) > 0:
                room_data, room_layout, room_propose, room_region = \
                    layout_room_by_sample(room_data, room_sample_set[0], replace_soft, replace_note)
                room_operate = replace_soft_operate(room_sample, room_layout)
                house_operate[room_key] = room_operate
            continue
        # 分支1:替换微调
        for object_idx, object_key in enumerate(replace_soft):
            if object_key not in replace_note:
                continue
            object_one, object_find = replace_note[object_key], []
            object_size = object_one['size'][:]
            object_group, object_role = object_one['group'], object_one['role']
            object_zone = ''
            if 'zone' in group_one:
                object_zone = group_one['zone']
            if len(object_zone) <= 0:
                type_id, style_id, category_id = get_furniture_data_refer_id(object_key)
                obj_cate, obj_zone = get_furniture_room_by_category(category_id)
            # 替换目标
            for group_old in group_find:
                if group_old['type'] == object_group:
                    pass
                else:
                    continue
                object_list, object_find = group_old['obj_list'], []
                # 类目判断
                for object_old in object_list:
                    if 'role' in object_old and object_old['role'] == object_role:
                        if object_role in ['cabinet']:
                            obj_zone_old = ''
                            if 'zone' in group_old:
                                obj_zone_old = group_old['zone']
                            if len(obj_zone_old) <= 0:
                                type_id_old, style_id_old, category_id_old = get_furniture_data_refer_id(object_key)
                                obj_cate_old, obj_zone_old = get_furniture_room_by_category(category_id_old)
                            if obj_zone_old == obj_zone or len(obj_zone) <= 0:
                                pass
                            else:
                                continue
                        object_find.append(object_old)
                # 替换策略
                if len(object_find) > 0:
                    object_wait = [object_find[0]]
                    for object_old in object_wait:
                        replace_dict[object_old['id']] = object_key
                        replace_size[object_key] = object_size
                elif object_group in ['Cabinet']:
                    continue
                else:
                    object_find.append(object_one)
                    group_rect_append(group_old, object_one)
                replace_done.append(object_key)
            if len(object_find) > 0:
                continue
            # 替换目标
            for group_old in group_have:
                if group_old['type'] == object_group:
                    pass
                else:
                    continue
                object_list, object_find = group_old['obj_list'], []
                for object_old in object_list:
                    if 'role' in object_old and object_old['role'] == object_role:
                        if object_role in ['cabinet']:
                            obj_zone_old = ''
                            if 'zone' in group_old:
                                obj_zone_old = group_old['zone']
                            if len(obj_zone_old) <= 0:
                                type_id_old, style_id_old, category_id_old = get_furniture_data_refer_id(object_key)
                                obj_cate_old, obj_zone_old = get_furniture_room_by_category(category_id_old)
                            if obj_zone_old == obj_zone or len(obj_zone) <= 0:
                                pass
                            else:
                                continue
                        object_find.append(object_old)
                # 替换策略
                if len(object_find) > 0:
                    object_wait = [object_find[0]]
                    for object_old in object_wait:
                        replace_dict[object_old['id']] = object_key
                        replace_size[object_key] = object_size
                elif object_group in ['Cabinet']:
                    continue
                else:
                    object_find.append(object_one)
                    group_rect_append(group_old, object_one)
                replace_done.append(object_key)
                group_find.append(group_old)
        group_push = group_rect_adjust(group_find, replace_dict, replace_size, {}, room_type)
        for group_new in group_push:
            group_done.append(group_new)

        # 分支2:添加微调 TODO:
        for object_idx, object_key in enumerate(replace_soft):
            if object_key not in replace_note:
                continue
            if object_key in replace_done:
                continue
            object_one, object_find = replace_note[object_key], []
            object_size = object_one['size'][:]
            object_group, object_role = object_one['group'], object_one['role']

        # 分支3:重新布局 TODO:

        pass
        # 方案生成
        group_list_old, group_list_new = scheme_old['group'], group_done
        for group_one in group_list_old:
            if group_one in group_find:
                continue
            group_list_new.append(group_one)
        scheme_new = scheme_old.copy()
        scheme_new['group'] = group_list_new
        room_layout = room_sample.copy()
        room_layout['layout_scheme'] = [scheme_new]
        house_layout[room_key] = room_layout
        # 方案比较
        room_operate = replace_soft_operate(room_sample, room_layout)
        house_operate[room_key] = room_operate
        pass
    # 处理场景
    scene_json_new, furniture_operate = house_scene_switch_object(scene_json_old, house_operate)
    return scene_json_new, furniture_operate


# 定制替换处理 TODO:
def replace_house_custom():
    pass


# 组合替换处理 TODO:
def replace_house_group():
    pass


# 软装替换操作
def replace_soft_operate(room_sample, room_layout):
    # 替换信息
    target_list, relate_list, remove_list, append_list = [], [], [], []
    group_list_old, group_list_new = [], []
    if 'layout_scheme' in room_sample and len(room_sample['layout_scheme']) > 0:
        scheme_old = room_sample['layout_scheme'][0]
        group_list_old = scheme_old['group']
        for group_one in group_list_old:
            group_type, object_list = group_one['type'], group_one['obj_list']
            if group_type in GROUP_RULE_FUNCTIONAL or group_type in ['Wall', 'Ceiling', 'Floor']:
                for object_one in object_list:
                    remove_list.append(object_one)
            elif group_type in ['Window']:
                for object_one in object_list:
                    object_type = object_one['type']
                    if 'curtain' in object_type:
                        remove_list.append(object_one)
    if 'layout_scheme' in room_layout and len(room_sample['layout_scheme']) > 0:
        scheme_new = room_layout['layout_scheme'][0]
        group_list_new = scheme_new['group']
        for group_one in group_list_new:
            group_type, object_list = group_one['type'], group_one['obj_list']
            if group_type in GROUP_RULE_FUNCTIONAL or group_type in ['Wall', 'Ceiling', 'Floor']:
                for object_one in object_list:
                    append_list.append(object_one)
            elif group_type in ['Window']:
                for object_one in object_list:
                    object_type = object_one['type']
                    if 'curtain' in object_type:
                        append_list.append(object_one)
    for old_idx in range(len(remove_list) - 1, -1, -1):
        old_obj = remove_list[old_idx]
        old_key, old_pos = old_obj['id'], old_obj['position']
        old_find, new_find = True, False
        for new_idx in range(len(append_list) - 1, -1, -1):
            new_obj = append_list[new_idx]
            new_key, new_pos = new_obj['id'], new_obj['position']
            if old_key == new_key and abs(old_pos[0] - new_pos[0]) + abs(old_pos[2] - new_pos[2]) <= 0.1:
                new_find = True
                append_list.pop(new_idx)
                break
        if new_find:
            remove_list.pop(old_idx)
    operate_info = {
        'target': target_list,
        'relate': relate_list,
        'remove': remove_list,
        'append': append_list,
        'adjust': []
    }
    return operate_info


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


# 物品角度纠正
def parse_object_turn(object_key, object_one, object_role=''):
    object_type, object_style, object_size = get_furniture_data(object_key)
    if len(object_type) > 0 and len(object_size) >= 3:
        object_turn = get_furniture_turn(object_key)
        if object_size[2] > object_size[0] * 2 and object_size[2] > 60:
            if object_role in ['table', 'armoire', 'cabinet']:
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


# 功能测试
if __name__ == '__main__':
    # 清空缓存
    layout_sample_clear()
    pass

    # 测试接口 软装替换
    layout_param_input = smart_decoration_input_soft_test_91
    layout_param_output = layout_sample_replace(layout_param_input)
    pass

    # 测试接口 硬装替换
    layout_param_input = smart_decoration_input_paint_test_99
    # layout_param_output = layout_sample_replace(layout_param_input)
    pass

    # 数据更新
    # save_furniture_data()
    pass
