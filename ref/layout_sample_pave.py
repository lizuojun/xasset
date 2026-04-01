# -*- coding: utf-8 -*-

"""
@Author: zhanghuichao
@Date: 2021-09-07
@Description: 铺贴信息计算

"""

import time
import shutil
import traceback
from layout import *
from layout_def import *
from House.house_scene_render import *
from House.house_scene_build import house_replace_house
from HouseSearch.house_seed import *
from Furniture.materials import get_material_feature, save_material_feature_data
from ImportHouse.room_search import *
from LayoutDecoration.house_pave import house_pave_pipeline
from Demo.proxy.design_json_get import get_design_url

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
def layout_sample_pave(param_info):
    # 户型参数
    house_id = ''
    house_data_info = {}
    house_material = {}
    house_count, house_area, house_price = {}, {}, {}
    house_usage = {}
    if 'house_id' in param_info:
        house_id = param_info['house_id']
    if 'house_data' in param_info:
        house_data_info = param_info['house_data']
    if 'house_material' in param_info:
        house_material = param_info['house_material']
    # 户型位置
    data_url, scene_url, image_url, scene_path = '', '', '', ''
    design_id, design_url = '', ''

    if 'scene_url' in param_info:
        scene_url = param_info['scene_url']

    if 'design_id' in param_info:
        design_id = param_info['design_id']
    if 'design_url' in param_info:
        design_url = param_info['design_url']
    if design_id == '' and not house_id == '':
        design_id = house_id

    # if True:
    try:
        # 打印信息
        print()
        layout_log_0 = 'layout paint ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        if not house_id == '':
            layout_log_0 = 'target house: %s' % house_id
            print(layout_log_0)
        elif not design_id == '':
            layout_log_0 = 'target house: %s' % design_id
            print(layout_log_0)
        # 户型参数
        if len(house_data_info) <= 0:
            house_para_info, house_data_info = {}, {}
            # design id
            if len(house_data_info) <= 0 and not design_id == '':
                if len(design_url) == 0:
                    design_url = get_design_url(design_id)
                    if len(design_url) == 0:
                        design_url = ''
                house_para_info, house_data_info = parse_design_data(design_id, design_url, scene_url)
                if 'id' in house_data_info:
                    house_id = design_id
                    house_data_info['id'] = design_id
                if 'room' in house_data_info and len(house_data_info['room']) <= 0:
                    house_data_info = {}

        if len(house_data_info) == 0 and not design_id == '':
            house_data_info = {'id': design_id, 'room': [], 'height': 2.8}
        # 硬装替换
        if len(house_material) > 0:
            house_usage = house_pave(house_data_info, house_material)
            print(house_usage)

        # 打印信息
        layout_log_0 = 'layout paint success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    # try:
        print(layout_log_0)
    except Exception as e:
        layout_log_0 = 'layout paint failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        print(e)
        traceback.print_exc()

    # 输出处理
    layout_version = '20210926.1200'
    layout_output = {
        'house_id': house_id,
        'data': house_usage,
        'layout_version': layout_version
    }
    save_material_data()
    save_ceramic_reference_data()
    save_material_feature_data()
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


# 铺贴信息
def house_pave(house_info, house_material):
    empty_house = len(house_info) == 0
    if empty_house:
        house_info = {'id': '', 'room': [], 'height': 2.8}
    # 种子处理
    formated_material = {}
    for room_id, mats in house_material.items():
        formated_material[room_id] = {}
        for k in mats.keys():
            if k not in ['floor', 'wall']:
                continue
            wall_mat = mats[k]
            if 'tile' in wall_mat and 'size' in wall_mat:
                mat = {
                    'jid': '',
                    'texture_url': 'https://not_exist_url',
                    'color': [255, 255, 255],
                    'colorMode': 'texture',
                    'size': wall_mat['size'],
                    'seam': wall_mat['tile'],
                    'area': 100.0, 'lift': 0,
                    'contentType': ['tmp'],
                    'refs': []
                }
            elif 'jid' in wall_mat:
                mat = get_material_data_info(wall_mat['jid'])
                try:
                    item_model_info = get_material_feature(wall_mat['jid'])
                    if 'features' in item_model_info:
                        if 'bind_item_length' in item_model_info['features'] and 'bind_item_width' in item_model_info['features']:
                            mat['size'] = [float(item_model_info['features']['bind_item_length']),
                                           float(item_model_info['features']['bind_item_width'])]
                except Exception as e:
                    traceback.print_exc()
                    print(e)
                    pass
                if 'tile' in wall_mat:
                    mat['seam'] = wall_mat['tile']
                if 'size' in wall_mat:
                    mat['size'] = wall_mat['size']
            else:
                print('invalid input')
                mat = {}

            mat = format_material(mat)
            if 'price' not in wall_mat:
                mat['price'] = 1.
            else:
                mat['price'] = wall_mat['price']
            if len(mat) > 0:
                formated_material[room_id][k] = mat
        if empty_house:
            if 'area' in house_material[room_id]:
                room_area = house_material[room_id]['area']
            else:
                print('empty house info and no area provided')
                return {}
                # room_area = 1.
            width = np.sqrt(room_area)
            floor = [0, 0, width, 0, width, width, 0, width, 0, 0]
            room_info = {'id': room_id, 'type': 'LivingDiningRoom', 'floor': floor, 'door_info': [],
                         'window_info': [], 'hole_info': [], 'baywindow_info': [], 'wall_width': [],
                         'furniture_info': [],
                         'material_info': [],
                         'area': room_area,
                         'coordinate': 'xyz',
                         'unit': 'm'}
            house_info['room'].append(room_info)

    # 硬装信息
    # paint_material = {}
    # for room_key, room_fix in house_material.items():
    #     material_new = {}
    #     seed_mat = update_room_layout_material_seed(material_new, room_fix)
    #     paint_material[room_key] = seed_mat

    house_usage = house_pave_pipeline(house_info, formated_material)

    # 返回信息
    return house_usage


# 功能测试
if __name__ == '__main__':
    # 清空缓存
    layout_sample_clear()
    pass

    # 测试接口 铺贴替换
    layout_param_input = smart_decoration_input_pave_test_98
    layout_param_output = layout_sample_pave(layout_param_input)
    pass

    # 数据更新
    # save_furniture_data()
    save_material_data()
    save_ceramic_reference_data()
    save_material_feature_data()
    pass
