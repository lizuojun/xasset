# -*- coding: utf-8 -*-

'''
@Author: lizuojun
@Date: 2020-10-30
@Description: 房间方案推荐

'''

import json
import shutil
from layout import *
from House.house_scene import *
from House.house_sample import *
from HouseSearch.design.check_house_main import house_design_parse
from HouseSearch.group.group_detail import get_cabinet_group_detail_name

# 临时目录
DATA_DIR_IMPORT = os.path.dirname(__file__) + '/temp/'
DATA_DIR_IMPORT_HOUSE = os.path.dirname(__file__) + '/temp/house/'
DATA_DIR_IMPORT_SAMPLE = os.path.dirname(__file__) + '/temp/sample/'
DATA_DIR_IMPORT_REGION = os.path.dirname(__file__) + '/temp/region/'
if not os.path.exists(DATA_DIR_IMPORT):
    os.makedirs(DATA_DIR_IMPORT)
if not os.path.exists(DATA_DIR_IMPORT_HOUSE):
    os.makedirs(DATA_DIR_IMPORT_HOUSE)
if not os.path.exists(DATA_DIR_IMPORT_SAMPLE):
    os.makedirs(DATA_DIR_IMPORT_SAMPLE)
if not os.path.exists(DATA_DIR_IMPORT_REGION):
    os.makedirs(DATA_DIR_IMPORT_REGION)

# OSS位置
DATA_OSS_DATABASE = 'ihome-alg-sample-data'
DATA_OSS_HOUSE = 'houseV2'
DATA_OSS_SAMPLE = 'sample'
# 方案数据
ROOM_DATA_DICT = {}
ROOM_SAMPLE_DICT = {}
ROOM_REGION_DICT = {}
# 方案数据
ROOM_SOURCE_LIST = ['870c6e14-5d7f-42ff-9060-1a6ebd25a109']
# 色系列表
ROOM_COLOR_RULE = {
    'Black_White_Gray': {},
    'Ground': {},
    'Green': {},
    'Wood': {},
    'None': {}
}
# 主次区域
GROUP_TYPE_MAIN = ['Meeting', 'Dining', 'Bed', 'Media', 'Bath', 'Toilet']
GROUP_TYPE_REST = ['Work', 'Rest', 'Armoire', 'Cabinet', 'Appliance']


# 加载全屋数据
def load_room_data(reload=False):
    global ROOM_DATA_DICT
    if len(ROOM_DATA_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'room_data_dict.json')
        ROOM_DATA_DICT = {}
        if os.path.exists(json_path):
            try:
                ROOM_DATA_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    # 返回信息
    return ROOM_DATA_DICT


# 保存全屋数据
def save_room_data():
    json_path = os.path.join(os.path.dirname(__file__), 'room_data_dict.json')
    with open(json_path, 'w') as f:
        json.dump(ROOM_DATA_DICT, f, indent=4)
        f.close()
    # 缓存位置
    house_bucket = DATA_OSS_DATABASE
    if os.path.exists(json_path):
        oss_upload_file('room_data_dict.json', json_path, house_bucket)
    print('save room data success')


# 加载全屋方案
def load_room_sample(reload=False):
    global ROOM_SAMPLE_DICT
    if len(ROOM_SAMPLE_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'room_sample_dict.json')
        ROOM_SAMPLE_DICT = {}
        if os.path.exists(json_path):
            try:
                ROOM_SAMPLE_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    # 返回信息
    return ROOM_SAMPLE_DICT


# 保存全屋方案
def save_room_sample():
    json_path = os.path.join(os.path.dirname(__file__), 'room_sample_dict.json')
    with open(json_path, 'w') as f:
        json.dump(ROOM_SAMPLE_DICT, f, indent=4)
        f.close()
    # 缓存位置
    house_bucket = DATA_OSS_DATABASE
    if os.path.exists(json_path):
        oss_upload_file('room_sample_dict.json', json_path, house_bucket)
    print('save room sample success')


# 获取方案列表
def get_source_list(house_path=''):
    if len(house_path) <= 0:
        house_path = os.path.join(os.path.dirname(__file__), 'room_source_list.txt')
    house_list = []
    if os.path.exists(house_path):
        f = open(house_path, 'r')
        line_list = f.readlines()
        for line_one in line_list:
            line_new = line_one.split('=')[-1].rstrip()
            if len(line_new) <= 0:
                continue
            house_list.append(line_new)
    return house_list


# 获取户型列表
def get_target_list(house_path=''):
    if len(house_path) <= 0:
        house_path = os.path.join(os.path.dirname(__file__), 'room_target_list.txt')
    house_list = []
    if os.path.exists(house_path):
        f = open(house_path, 'r')
        line_list = f.readlines()
        for line_one in line_list:
            line_new = line_one.split('=')[-1].rstrip()
            if len(line_new) <= 0:
                continue
            house_list.append(line_new)
    return house_list


# 获取户型地址
def get_target_url_dict(house_path=''):
    if len(house_path) <= 0:
        house_path = os.path.join(os.path.dirname(__file__), 'room_target_url.json')
    design_urls_dict = {}
    if os.path.exists(house_path):
        f = open(house_path, 'r')
        design_urls_dict = json.load(f)
    return design_urls_dict


# 获取全屋数据
def get_house_data(house_id, design_url='', scene_url='', reload=False, recalc=False, load_parametric=False, correct_house=True):
    global ROOM_DATA_DICT
    load_room_data()
    # 缓存位置
    house_bucket = DATA_OSS_DATABASE
    house_subdir = DATA_OSS_HOUSE
    # 查找信息
    house_para, house_data = {}, {}
    if house_id in ROOM_DATA_DICT and not reload:
        house_para = ROOM_DATA_DICT[house_id]
        if 'url' in house_para:
            # 位置
            house_file = house_id + '.json'
            house_path = os.path.join(DATA_DIR_IMPORT_HOUSE, house_file)
            house_url = house_para['url']
            # 读取
            if os.path.exists(house_path):
                print('fetch house data', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'tmp')
                try:
                    house_data = json.load(open(house_path, 'r'))
                except:
                    house_data = {}
            if 'room' not in house_data and oss_exist_file(house_subdir + '/' + house_file, house_bucket):
                # 读取
                print('fetch house data', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'url')
                oss_download_file(house_subdir + '/' + house_file, house_path, house_bucket)
                if os.path.exists(house_path):
                    house_data = oss_download_json(house_subdir + '/' + house_file, house_bucket)
    # 缓存信息
    if len(house_data) <= 0 and not reload:
        # 位置
        house_file = house_id + '.json'
        house_path = os.path.join(DATA_DIR_IMPORT_HOUSE, house_file)
        house_url = house_subdir + '/' + house_file
        # 读取
        if os.path.exists(house_path):
            print('fetch house data', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'tmp')
            house_data = json.load(open(house_path, 'r'))
        if 'room' not in house_data and oss_exist_file(house_subdir + '/' + house_file, house_bucket):
            # 读取
            print('fetch house data', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'url')
            oss_download_file(house_subdir + '/' + house_file, house_path, house_bucket)
            if os.path.exists(house_path):
                house_data = oss_download_json(house_subdir + '/' + house_file, house_bucket)
        if 'room' in house_data and len(house_data['room']) > 0:
            # 纠正
            if correct_house:
                correct_house_type(house_data)
            # 特征
            room_dict, room_para, room_list, room_data = {}, {}, house_data['room'], {}
            for room_data in room_list:
                room_key, room_area, room_type = '', 0, ''
                room_vector, room_sample = [], []
                # 基本
                if 'id' in room_data:
                    room_key = room_data['id']
                if 'area' in room_data:
                    room_area = room_data['area']
                if 'type' in room_data:
                    room_type = room_data['type']
                # 特征
                if recalc:
                    room_vector, room_type = cal_room_vector(room_data)
                # 增加
                room_para = {'area': room_area, 'type': room_type, 'feature': room_vector, 'sample': room_sample}
                if len(room_key) > 0:
                    room_dict[room_key] = room_para
            # 添加
            house_para = {'url': house_url, 'room': room_dict}
            ROOM_DATA_DICT[house_id] = house_para
    # 解析信息
    if len(house_data) <= 0 and (len(design_url) > 0 or len(scene_url) > 0):
        if len(house_data) <= 0 and len(design_url) > 0:
            house_data = house_design_parse(design_url)
        if len(house_data) <= 0 and len(scene_url) > 0:
            house_data = house_scene_parse(scene_url, house_id=house_id, load_parametric=load_parametric)
        house_data['id'] = house_id
        if 'room' in house_data and len(house_data['room']) > 0:
            # 位置
            house_file = house_id + '.json'
            house_path = os.path.join(DATA_DIR_IMPORT_HOUSE, house_file)
            house_url = house_subdir + '/' + house_file
            # 本地
            with open(house_path, 'w') as f:
                json.dump(house_data, f, indent=4)
                f.close()
            # 上传
            if os.path.exists(house_path):
                oss_upload_file(DATA_OSS_HOUSE + '/' + house_file, house_path, house_bucket)
            # 纠正
            if correct_house:
                correct_house_type(house_data)
            # 特征
            room_dict, room_para, room_list, room_data = {}, {}, house_data['room'], {}
            for room_data in room_list:
                room_key, room_area, room_type = '', 0, ''
                room_vector, room_sample = [], []
                # 基本
                if 'id' in room_data:
                    room_key = room_data['id']
                if 'area' in room_data:
                    room_area = room_data['area']
                if 'type' in room_data:
                    room_type = room_data['type']
                # 特征
                if recalc:
                    room_vector, room_type = cal_room_vector(room_data)
                # 增加
                room_para = {'area': room_area, 'type': room_type, 'feature': room_vector, 'sample': room_sample}
                if len(room_key) > 0:
                    room_dict[room_key] = room_para
            # 添加
            house_para = {'url': house_url, 'room': room_dict}
            ROOM_DATA_DICT[house_id] = house_para
        else:
            # print('extract error:', house_id)
            house_para, house_data = {}, {}
    # 获取信息
    if len(house_data) <= 0:
        house_data = house_design_trans(house_id)
        if 'room' in house_data and len(house_data['room']) > 0:
            # 位置
            house_file = house_id + '.json'
            house_path = os.path.join(DATA_DIR_IMPORT_HOUSE, house_file)
            house_url = house_subdir + '/' + house_file
            # 本地
            with open(house_path, 'w') as f:
                json.dump(house_data, f, indent=4)
                f.close()
            # 上传
            pass
            # 纠正
            if correct_house:
                correct_house_type(house_data)
            # 特征
            room_dict, room_para, room_list, room_data = {}, {}, house_data['room'], {}
            for room_data in room_list:
                room_key, room_area, room_type = '', 0, ''
                room_vector, room_sample = [], []
                # 基本
                if 'id' in room_data:
                    room_key = room_data['id']
                if 'area' in room_data:
                    room_area = room_data['area']
                if 'type' in room_data:
                    room_type = room_data['type']
                # 特征
                if recalc:
                    room_vector, room_type = cal_room_vector(room_data)
                # 增加
                room_para = {'area': room_area, 'type': room_type, 'feature': room_vector, 'sample': room_sample}
                if len(room_key) > 0:
                    room_dict[room_key] = room_para
            # 添加
            house_para = {'url': house_url, 'room': room_dict}
            ROOM_DATA_DICT[house_id] = house_para
        else:
            # print('extract error', house_id)
            house_para, house_data = {}, {}
    # 纠正信息
    house_data['id'] = house_id
    # 返回信息
    return house_para, house_data


# 获取单屋数据
def get_room_data(house_id, room_id, reload=False, recalc=False):
    house_para, house_data = get_house_data(house_id, '', '', reload, recalc)
    # 查找信息
    room_dict, room_para, room_list, room_data = {}, {}, [], {}
    if 'room' in house_para and len(house_para['room']) > 0:
        room_dict = house_para['room']
        for room_key, room_one in room_dict.items():
            if room_key == room_id and len(room_id) > 0:
                room_para = room_one
                break
    if 'room' in house_data and len(house_data['room']) > 0:
        room_list = house_data['room']
        for room_one in room_list:
            if 'id' in room_one and room_one['id'] == room_id and len(room_id) > 0:
                room_data = room_one
                break
    # 查找特征
    room_key, room_area, room_type = '', 0, ''
    room_vector, room_sample = [], []
    if 'id' in room_data:
        room_key = room_data['id']
    if 'area' in room_data:
        room_area = room_data['area']
    if 'type' in room_data:
        room_type = room_data['type']
    if 'feature' in room_para:
        room_vector = room_para['feature'][:]
    if 'sample' in room_para:
        room_sample = room_para['sample'][:]
    # 特征
    if len(room_vector) <= 0 and len(room_key) > 0:
        if recalc:
            room_vector, room_type = cal_room_vector(room_data)
        # 增加
        room_para = {'area': room_area, 'type': room_type, 'feature': room_vector, 'sample': room_sample}
        if len(room_key) > 0:
            room_dict[room_key] = room_para
    # 返回信息
    return room_para, room_data


# 计算全屋特征
def cal_house_vector(house_data, reload=False):
    house_vector = {}
    if 'layout' in house_data and len(house_data['layout']) > 0 and not reload:
        house_data_info, house_layout_info, house_propose_info = house_data, house_data['layout'], {}
    else:
        house_data_info, house_layout_info, house_propose_info = search_advice_house(house_data)
    for room_key, room_val in house_layout_info.items():
        room_data = room_val
        # 查看缓存
        room_vector, room_region = [], []
        if 'vector' in room_data and len(room_data['vector']) > 0 and not reload:
            room_vector = room_data['vector']
        if 'region' in room_data and len(room_data['region']) > 0 and not reload:
            room_region = room_data['region']
        # 计算特征
        if len(room_vector) <= 0 or len(room_region) <= 0:
            scheme_list, scheme_max = room_val['layout_scheme'], {}
            room_type, group_list = '', []
            if 'room_type' in room_val:
                room_type = room_val['room_type']
            for scheme_idx, scheme_one in enumerate(scheme_list):
                if len(scheme_max) <= 0:
                    scheme_max = scheme_one
                elif 'group' in scheme_max and 'group' in scheme_one:
                    group_list_old, group_list_new = scheme_max['group'], scheme_one['group']
                    group_best_old, group_best_new = 0, 0
                    for group_one in group_list_old:
                        group_type, group_size = group_one['type'], group_one['size'][:]
                        if 'regulation' in group_one:
                            group_regulate = group_one['regulation']
                            group_size[0] += group_regulate[1]
                            group_size[0] += group_regulate[3]
                            group_size[2] += group_regulate[0]
                            group_size[2] += group_regulate[2]
                        if 'neighbor_best' in group_one:
                            group_neighbor = group_one['neighbor_base']
                            group_size[0] += group_neighbor[1]
                            group_size[0] += group_neighbor[3]
                            group_size[2] += group_neighbor[0]
                            group_size[2] += group_neighbor[2]
                        if group_type in ['Media']:
                            group_best_old += 1
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
                        group_type, group_size = group_one['type'], group_one['size'][:]
                        if 'regulation' in group_one:
                            group_regulate = group_one['regulation']
                            group_size[0] += group_regulate[1]
                            group_size[0] += group_regulate[3]
                            group_size[2] += group_regulate[0]
                            group_size[2] += group_regulate[2]
                        if 'neighbor_best' in group_one:
                            group_neighbor = group_one['neighbor_base']
                            group_size[0] += group_neighbor[1]
                            group_size[0] += group_neighbor[3]
                            group_size[2] += group_neighbor[0]
                            group_size[2] += group_neighbor[2]
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
            if 'group' in scheme_max:
                room_type, group_list = room_val['room_type'], scheme_max['group']
            if len(room_type) <= 0 and 'room_type' in room_val:
                room_type = room_val['room_type']
            room_vector = compute_room_vector(group_list, room_type)
            room_region = compute_room_region(group_list, room_type)
            room_val['vector'] = room_vector
            room_val['region'] = room_region
        house_vector[room_key] = room_vector
    return house_vector


# 计算单屋特征
def cal_room_vector(room_data, reload=False):
    # 查看缓存
    room_vector, room_region = [], []
    if 'vector' in room_data and len(room_data['vector']) > 0 and not reload:
        room_vector = room_data['vector']
    if 'region' in room_data and len(room_data['region']) > 0 and not reload:
        room_region = room_data['region']
    if 'layout' in room_data and len(room_data['layout']) > 0 and not reload:
        room_data_info, room_layout_info, room_propose_info = room_data, room_data['layout'], []
    else:
        room_data_info, room_layout_info, room_propose_info = search_advice_room(room_data)
    # 更新信息
    room_val, room_type = room_layout_info, ''
    if 'room_type' in room_val:
        room_type = room_val['room_type']
    # 计算特征
    if len(room_vector) <= 0 or len(room_region) <= 0:
        scheme_list, scheme_max, group_list = room_val['layout_scheme'], {}, []
        for scheme_idx, scheme_one in enumerate(scheme_list):
            if len(scheme_max) <= 0:
                scheme_max = scheme_one
            elif 'group' in scheme_max and 'group' in scheme_one:
                group_list_old, group_list_new = scheme_max['group'], scheme_one['group']
                group_best_old, group_best_new = 0, 0
                for group_one in group_list_old:
                    group_type, group_size = group_one['type'], group_one['size'][:]
                    group_regulate, group_neighbor = [0, 0, 0, 0], [0, 0, 0, 0]
                    if 'regulation' in group_one:
                        group_regulate = group_one['regulation'][:]
                    if 'neighbor_best' in group_one:
                        group_neighbor = group_one['neighbor_best'][:]
                    # 调整尺寸
                    group_size[0] += group_regulate[1]
                    group_size[0] += group_regulate[3]
                    group_size[2] += group_regulate[0]
                    group_size[2] += group_regulate[2]
                    group_size[0] += group_neighbor[1]
                    group_size[0] += group_neighbor[3]
                    group_size[2] += group_neighbor[0]
                    group_size[2] += group_neighbor[2]
                    # 计算得分
                    if group_type in ['Media']:
                        group_best_old += 1
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
                    group_type, group_size = group_one['type'], group_one['size'][:]
                    group_regulate, group_neighbor = [0, 0, 0, 0], [0, 0, 0, 0]
                    if 'regulation' in group_one:
                        group_regulate = group_one['regulation'][:]
                    if 'neighbor_best' in group_one:
                        group_neighbor = group_one['neighbor_best'][:]
                    # 调整尺寸
                    group_size[0] += group_regulate[1]
                    group_size[0] += group_regulate[3]
                    group_size[2] += group_regulate[0]
                    group_size[2] += group_regulate[2]
                    group_size[0] += group_neighbor[1]
                    group_size[0] += group_neighbor[3]
                    group_size[2] += group_neighbor[0]
                    group_size[2] += group_neighbor[2]
                    # 计算得分
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
        if 'group' in scheme_max:
            room_type, group_list = room_val['room_type'], scheme_max['group']
        room_vector = compute_room_vector(group_list, room_type)
        room_region = compute_room_region(group_list, room_type)
        room_data['vector'] = room_vector
        room_data['region'] = room_region
    # 返回信息
    return room_vector, room_type


# 获取全屋样板
def get_house_sample(house_id, reload=False):
    global ROOM_DATA_DICT
    global ROOM_SAMPLE_DICT
    load_room_data()
    load_room_sample()
    # 缓存位置
    house_bucket = DATA_OSS_DATABASE
    # 查找信息
    sample_data, sample_para, sample_layout, sample_group = {}, {}, {}, {}
    if house_id in ROOM_DATA_DICT:
        sample_data = ROOM_DATA_DICT[house_id]
    if house_id in ROOM_SAMPLE_DICT and not reload:
        sample_para = ROOM_SAMPLE_DICT[house_id]
        if 'url' in sample_para:
            # 位置
            house_file = house_id + '_group.json'
            house_path = os.path.join(DATA_DIR_IMPORT_SAMPLE, house_file)
            house_url = sample_para['url']
            # 读取
            if os.path.exists(house_path):
                print('fetch house group', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'tmp')
                try:
                    sample_group = json.load(open(house_path, 'r'))
                except:
                    sample_group = {}
            # 读取
            if len(sample_group) <= 0 and oss_exist_file(DATA_OSS_SAMPLE + '/' + house_file, house_bucket):
                print('fetch house group', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'url')
                oss_download_file(DATA_OSS_SAMPLE + '/' + house_file, house_path, house_bucket)
                if os.path.exists(house_path):
                    sample_group = json.load(open(house_path, 'r'))

            # 位置
            house_file = house_id + '_layout.json'
            house_path = os.path.join(DATA_DIR_IMPORT_SAMPLE, house_file)
            house_url = sample_para['url']
            # 读取
            if os.path.exists(house_path):
                print('fetch house layout', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'tmp')
                try:
                    sample_layout = json.load(open(house_path, 'r'))
                except:
                    sample_layout = {}
            # 读取
            if len(sample_layout) <= 0 and oss_exist_file(DATA_OSS_SAMPLE + '/' + house_file, house_bucket):
                print('fetch house layout', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'url')
                oss_download_file(DATA_OSS_SAMPLE + '/' + house_file, house_path, house_bucket)
                if os.path.exists(house_path):
                    sample_layout = json.load(open(house_path, 'r'))

    # 获取信息
    if len(sample_group) <= 0 or len(sample_layout) <= 0:
        house_para, house_data = get_house_data(house_id, '', '', False, False)
        if 'room' in house_data and len(house_data['room']) > 0:
            # 组合
            sample_data, sample_layout, sample_group = extract_house_layout_by_info(house_data, check_mode=2)
            # 位置
            house_file = house_id + '_group.json'
            house_path = os.path.join(DATA_DIR_IMPORT_SAMPLE, house_file)
            house_url = DATA_OSS_SAMPLE + '/' + house_file
            # 本地
            with open(house_path, 'w') as f:
                json.dump(sample_group, f, indent=4)
                f.close()
            # 上传
            if os.path.exists(house_path):
                oss_upload_file(DATA_OSS_SAMPLE + '/' + house_file, house_path, house_bucket)
            # 位置
            house_file = house_id + '_layout.json'
            house_path = os.path.join(DATA_DIR_IMPORT_SAMPLE, house_file)
            house_url = DATA_OSS_SAMPLE + '/' + house_file
            # 本地
            with open(house_path, 'w') as f:
                json.dump(sample_layout, f, indent=4)
                f.close()
            # 上传
            if os.path.exists(house_path):
                oss_upload_file(DATA_OSS_SAMPLE + '/' + house_file, house_path, house_bucket)
            # 特征
            room_dict, room_para, room_list, room_data = {}, {}, house_data['room'], {}
            for room_data in room_list:
                room_key, room_area, room_type, room_style = '', 0, '', ''
                room_group, room_vector, room_sample = [], [], []
                # 基本
                if 'id' in room_data:
                    room_key = room_data['id']
                if 'area' in room_data:
                    room_area = room_data['area']
                if 'type' in room_data:
                    room_type = room_data['type']
                # 组合
                if room_key in sample_group:
                    sample_one = sample_group[room_key]
                    if 'room_type' in sample_one:
                        room_type = sample_one['room_type']
                    if 'room_style' in sample_one:
                        room_style = sample_one['room_style']
                    if 'group_functional' in sample_one:
                        room_group = sample_one['group_functional']
                # 特征
                room_valid = cal_sample_valid(room_group, room_type)
                room_vector = cal_sample_vector(room_group, room_type)
                # 增加
                room_para = {'area': room_area, 'type': room_type, 'style': room_style, 'color': '',
                             'feature': room_vector, 'valid': room_valid, 'code': []}
                if len(room_key) > 0:
                    room_dict[room_key] = room_para
            # 添加
            sample_para = {'url': house_url, 'room': room_dict}
            ROOM_SAMPLE_DICT[house_id] = sample_para

    # 样板纠正
    house_key = house_id
    for room_key, room_val in sample_layout.items():
        layout_scheme = []
        if 'layout_scheme' in room_val:
            layout_scheme = room_val['layout_scheme']
        for scheme_one in layout_scheme:
            scheme_one['source_house'] = house_key
            scheme_one['source_room'] = room_key
    return sample_para, sample_data, sample_layout, sample_group


# 获取全屋样板
def get_house_sample_layout(house_id, reload=False):
    global ROOM_SAMPLE_DICT
    load_room_sample()
    # 缓存位置
    house_bucket = DATA_OSS_DATABASE
    # 查找信息
    sample_layout = {}
    if house_id in ROOM_SAMPLE_DICT and not reload:
        sample_para = ROOM_SAMPLE_DICT[house_id]
        if 'url' in sample_para:
            # 位置
            house_file = house_id + '_layout.json'
            house_path = os.path.join(DATA_DIR_IMPORT_SAMPLE, house_file)
            house_url = sample_para['url']
            # 读取
            if os.path.exists(house_path):
                print('fetch house layout', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'tmp')
                try:
                    sample_layout = json.load(open(house_path, 'r'))
                except:
                    sample_layout = {}
            # 读取
            if len(sample_layout) <= 0:
                print('fetch house layout', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'url')
                oss_download_file(DATA_OSS_SAMPLE + '/' + house_file, house_path, house_bucket)
                if os.path.exists(house_path):
                    sample_layout = json.load(open(house_path, 'r'))
    else:
        sample_para, sample_data, sample_layout, sample_group = get_house_sample(house_id, reload)

    # 样板纠正
    house_key = house_id
    for room_key, room_val in sample_layout.items():
        layout_scheme = []
        if 'layout_scheme' in room_val:
            layout_scheme = room_val['layout_scheme']
        for scheme_one in layout_scheme:
            scheme_one['source_house'] = house_key
            scheme_one['source_room'] = room_key
    return sample_layout


# 获取单屋样板
def get_room_sample(house_id, room_id, reload=False):
    sample_para, sample_data, sample_layout, sample_group = get_house_sample(house_id, reload)
    # 查找信息
    room_para, room_layout, room_group = {}, {}, {}
    if 'room' in sample_para and len(sample_para['room']) > 0:
        room_dict = sample_para['room']
        if room_id in room_dict:
            room_para = room_dict[room_id]
    if room_id in sample_layout:
        room_layout = sample_layout[room_id]
    if room_id in sample_group:
        room_group = sample_group[room_id]
    return room_para, room_layout, room_group


# 获取单屋样板
def get_sample_valid(house_id, room_id, reload=False):
    global ROOM_SAMPLE_DICT
    load_room_sample()
    # 查找信息
    sample_para, sample_group = {}, {}
    if house_id in ROOM_SAMPLE_DICT and not reload:
        sample_para = ROOM_SAMPLE_DICT[house_id]
    if len(sample_para) <= 0:
        sample_para, sample_data, sample_layout, sample_group = get_house_sample(house_id, reload)
    room_valid = [0, 0, 0, 0]
    # 查找信息
    if 'room' in sample_para and len(sample_para['room']) > 0:
        room_dict = sample_para['room']
        if room_id in room_dict:
            room_para = room_dict[room_id]
            if 'valid' in room_para:
                room_valid = room_para['valid']
    return room_valid


# 计算样板有效
def cal_sample_valid(group_list, room_type):
    room_valid = [0, 0, 0, 0]
    for group_one in group_list:
        group_type, object_type, object_main, object_info = group_one['type'], '', '', {}
        if 'obj_type' in group_one:
            object_type = group_one['obj_type']
        if 'obj_main' in group_one:
            object_main = group_one['obj_main']
        if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
            object_info = group_one['obj_list'][0]
        if group_type in ['Meeting', 'Bed', 'Bath'] or (group_type in ['Work'] and room_type in ['Library']):
            if 'bed set' in object_type or 'sofa set' in object_type:
                room_valid[0] += 1
            elif len(object_main) > 0 and abs(get_furniture_turn(object_main)) >= 1:
                room_valid[0] += 1
            elif len(object_info) > 0 and group_type in ['Meeting']:
                object_size = object_info['size']
                if object_size[2] > object_size[0] * 1.5:
                    room_valid[0] += 1
        elif group_type in ['Media']:
            pass
        elif group_type in ['Dining', 'Work', 'Rest', 'Toilet']:
            if 'dinning set' in object_type:
                room_valid[2] += 1
        elif group_type in ['Armoire', 'Cabinet', 'Appliance']:
            pass
    return room_valid


# 计算样板特征
def cal_sample_vector(group_list, room_type):
    global ROOM_TYPE_CODE
    room_code = 0
    if room_type in ROOM_TYPE_CODE:
        room_code = ROOM_TYPE_CODE[room_type]
    else:
        room_code = ROOM_TYPE_CODE['none']
    room_vector = [room_code, 0, 0, 0, 0, 0, 0, 0, 0]
    for group_one in group_list:
        group_type = group_one['type']
        group_size = group_one['size']
        if group_type in ['Meeting', 'Bed', 'Bath']:
            if room_vector[1] + room_vector[2] < group_size[0] + group_size[2]:
                room_vector[1], room_vector[2] = round(group_size[0], 1), round(group_size[2], 1)
        elif group_type in ['Media']:
            if room_vector[3] + room_vector[4] < group_size[0] + group_size[2]:
                room_vector[3], room_vector[4] = round(group_size[0], 1), round(group_size[2], 1)
        elif group_type in ['Dining', 'Work', 'Rest', 'Toilet']:
            if room_vector[5] + room_vector[6] < group_size[0] + group_size[2]:
                room_vector[5], room_vector[6] = round(group_size[0], 1), round(group_size[2], 1)
        elif group_type in ['Armoire', 'Cabinet', 'Appliance']:
            # 去除浴室柜 TODO:
            if room_type not in ['Bathroom', 'MasterBathroom']:
                if group_type == 'Cabinet':
                    name = get_cabinet_group_detail_name(group_one)
                    if name == 'bath_cabinet':
                        continue

            if room_vector[7] + room_vector[8] < group_size[0] + group_size[2]:
                room_vector[7], room_vector[8] = round(group_size[0], 1), round(group_size[2], 1)
    return room_vector


# 全屋布局参考
def search_advice_house(house_info, sample_num=2):
    data_info, layout_info, propose_info = house_info, {}, {}
    data_info, layout_info, propose_info, region_info = layout_house_by_refer(house_info, sample_num)
    # 返回信息
    return data_info, layout_info, propose_info


# 单屋布局参考
def search_advice_room(room_info, sample_num=2):
    # 纠正类型
    room_key, room_type, room_area = '', '', 10
    if 'id' in room_info:
        room_key = room_info['id']
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
    return data_info, layout_info, propose_info


# 全屋区域
def search_region_house(house_id, house_data, method='', reload=False):
    if len(house_id) <= 0 and 'id' in house_data and len(house_data['id']) > 0:
        house_id = house_data['id']
    region_dir = DATA_DIR_IMPORT_REGION
    region_file = house_id + '.json'
    region_path = os.path.join(region_dir, region_file)
    region_json = {}
    # 缓存
    if os.path.exists(region_path) and not reload:
        region_json = json.load(open(region_path, 'r', encoding='utf-8'))
    elif oss_exist_file('region/' + region_file, DATA_OSS_DATABASE) and not reload:
        oss_download_file('region/' + region_file, region_path, DATA_OSS_DATABASE)
        if os.path.exists(region_path) and not reload:
            region_json = json.load(open(region_path, 'r', encoding='utf-8'))
    # 重置
    room_list = []
    if 'room' in house_data:
        room_list = house_data['room']
    if len(room_list) <= 0:
        return house_data
    for room_one in room_list:
        room_one['region_info'] = []
    if len(region_json) > 0:
        room_cnt = 0
        for room_one in room_list:
            room_key = room_one['id']
            if room_key in region_json:
                room_one['region_info'] = region_json[room_key]
                room_cnt += 1
        if room_cnt >= 1:
            return house_data
    # 重算 TODO:
    data_info, layout_info, propose_info = {}, {}, {}
    if method == 'cnn':
        data_info, layout_info, propose_info = search_advice_house(house_data, sample_num=1)
    else:
        data_info, layout_info, propose_info = search_advice_house(house_data, sample_num=1)
    region_info = {}
    if len(layout_info) > 0:
        for room_one in room_list:
            room_key, room_type = room_one['id'], room_one['type']
            # 判断
            if room_type not in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                                 'MasterBedroom', 'SecondBedroom', 'Bedroom']:
                continue
            # 解算
            region_list = []
            if room_key in layout_info and layout_info[room_key]['layout_scheme']:
                scheme_info = layout_info[room_key]['layout_scheme'][0]
                group_list = scheme_info['group']
                for group_idx, group_one in enumerate(group_list):
                    group_type = group_one['type']
                    if group_type in ['Meeting', 'Dining', 'Media', 'Bed', 
                                      'Armoire', 'Cabinet', 'Work', 'Rest', 'Bath']:
                        group_size = group_one['size'][:]
                        group_pos, group_rot = group_one['position'][:], group_one['rotation'][:]
                        group_ang = rot_to_ang(group_rot)
                        # 调整
                        size_w_d, size_h_d = 0, 0
                        group_size[0] += size_w_d
                        group_size[2] += size_h_d
                        if group_type in ['Meeting', 'Dining', 'Work', 'Rest']:
                            group_pos[0] += math.sin(group_ang) * size_h_d / 2.
                            group_pos[2] += math.cos(group_ang) * size_h_d / 2.
                        region_one = {
                            'type': group_type,
                            'size': group_size,
                            'scale': [1., 1., 1.],
                            'position': group_pos,
                            'rotation': group_rot,
                            'zone': ''
                        }
                        if 'table/table' in group_one['obj_type'] and group_type in ['Cabinet']:
                            region_one['type'] = 'Work'
                        if 'scale' in group_one:
                            region_one['scale'] = group_one['scale']
                        if 'zone' in group_one:
                            region_one['zone'] = group_one['zone']
                        region_list.append(region_one)
            # 纠正
            if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom']:
                armoire_cnt, cabinet_max, cabinet_max_width = 0, {}, 0
                for region_one in region_list:
                    region_type = region_one['type']
                    if region_type in ['Armoire']:
                        armoire_cnt += 1
                    elif region_type in ['Cabinet']:
                        region_width = region_one['size'][0]
                        if region_width > cabinet_max_width:
                            cabinet_max = region_one
                            cabinet_max_width = region_width
                if armoire_cnt <= 0 and len(cabinet_max) > 0:
                    cabinet_max['type'] = 'Armoire'
            # 添加
            if len(region_list) > 0:
                room_one['region_info'] = region_list
            region_info[room_key] = region_list
    # 返回
    return house_data


# 单屋区域
def search_region_room(house_id, room_id, method='', reload=False):
    region_dir = DATA_DIR_IMPORT_REGION
    region_file = house_id + '.json'
    region_path = os.path.join(region_dir, region_file)
    region_json = {}
    # 缓存
    if os.path.exists(region_path) and not reload:
        region_json = json.load(open(region_path, 'r', encoding='utf-8'))
    elif oss_exist_file('region/' + region_file, DATA_OSS_DATABASE) and not reload:
        oss_download_file('region/' + region_file, region_path, DATA_OSS_DATABASE)
        if os.path.exists(region_path) and not reload:
            region_json = json.load(open(region_path, 'r', encoding='utf-8'))
    if room_id in region_json:
        return region_json[room_id]
    house_para, house_data = get_house_data(house_id, '', '')
    room_list = []
    if 'room' in house_data:
        room_list = house_data['room']
    if len(room_list) <= 0:
        return []
    # 重算 TODO:
    data_info, layout_info, propose_info = {}, {}, {}
    if method == 'cnn':
        data_info, layout_info, propose_info = search_advice_house(house_data, sample_num=1)
    else:
        data_info, layout_info, propose_info = search_advice_house(house_data, sample_num=1)
    if len(layout_info) > 0:
        for room_one in room_list:
            room_key, room_type = room_one['id'], room_one['type']
            # 判断
            if room_type not in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                                 'MasterBedroom', 'SecondBedroom', 'Bedroom']:
                continue
            if not room_key == room_id:
                continue
            # 解算
            region_list = []
            if room_key in layout_info and layout_info[room_key]['layout_scheme']:
                scheme_info = layout_info[room_key]['layout_scheme'][0]
                group_list = scheme_info['group']
                for group_idx, group_one in enumerate(group_list):
                    group_type = group_one['type']
                    if group_type in ['Meeting', 'Dining', 'Media', 'Bed',
                                      'Armoire', 'Cabinet', 'Work', 'Rest', 'Bath']:
                        group_size = group_one['size'][:]
                        group_pos, group_rot = group_one['position'][:], group_one['rotation'][:]
                        group_ang = rot_to_ang(group_rot)
                        # 调整
                        size_w_d, size_h_d = 0, 0
                        group_size[0] += size_w_d
                        group_size[2] += size_h_d
                        if group_type in ['Meeting', 'Dining', 'Work', 'Rest']:
                            group_pos[0] += math.sin(group_ang) * size_h_d / 2.
                            group_pos[2] += math.cos(group_ang) * size_h_d / 2.
                        region_one = {
                            'type': group_type,
                            'size': group_size,
                            'scale': [1., 1., 1.],
                            'position': group_pos,
                            'rotation': group_rot,
                            'zone': ''
                        }
                        if 'table/table' in group_one['obj_type'] and group_type in ['Cabinet']:
                            region_one['type'] = 'Work'
                        if 'scale' in group_one:
                            region_one['scale'] = group_one['scale']
                        if 'zone' in group_one:
                            region_one['zone'] = group_one['zone']
                        region_list.append(region_one)
            # 纠正
            if room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom']:
                armoire_cnt, cabinet_max, cabinet_max_width = 0, {}, 0
                for region_one in region_list:
                    region_type = region_one['type']
                    if region_type in ['Armoire']:
                        armoire_cnt += 1
                    elif region_type in ['Cabinet']:
                        region_width = region_one['size'][0]
                        if region_width > cabinet_max_width:
                            cabinet_max = region_one
                            cabinet_max_width = region_width
                if armoire_cnt <= 0 and len(cabinet_max) > 0:
                    cabinet_max['type'] = 'Armoire'
            # 添加
            if len(region_list) > 0:
                room_one['region_info'] = region_list
            return region_list
    return []


# 方案服务更新
def search_update_data(source_list=[], target_list=[], sample=False, reload=False):
    if len(source_list) <= 0 and sample:
        source_list = get_source_list()
    if len(target_list) <= 0 and not sample:
        target_list = get_target_list()
    # 样板间
    print()
    for source_idx, source_key in enumerate(source_list):
        if source_idx % 10 == 0:
            print('fetch house source %04d' % source_idx)
        get_house_sample(source_key, reload)
    # 空户型
    print()
    for target_idx, target_key in enumerate(target_list):
        if target_idx % 10 == 0:
            print('fetch house target %04d' % target_idx)
        get_house_data(target_key, '', '', reload)
    return source_list, target_list


# 方案缓存清空
def search_clear_temp():
    # 清空
    if os.path.exists(DATA_DIR_IMPORT_HOUSE):
        shutil.rmtree(DATA_DIR_IMPORT_HOUSE)
    if os.path.exists(DATA_DIR_IMPORT_SAMPLE):
        shutil.rmtree(DATA_DIR_IMPORT_SAMPLE)
    if os.path.exists(DATA_DIR_IMPORT_REGION):
        shutil.rmtree(DATA_DIR_IMPORT_REGION)
    # 重建
    if not os.path.exists(DATA_DIR_IMPORT_HOUSE):
        os.makedirs(DATA_DIR_IMPORT_HOUSE)
    if not os.path.exists(DATA_DIR_IMPORT_SAMPLE):
        os.makedirs(DATA_DIR_IMPORT_SAMPLE)
    if not os.path.exists(DATA_DIR_IMPORT_REGION):
        os.makedirs(DATA_DIR_IMPORT_REGION)


# 方案缓存加载
def search_fetch_temp():
    source_list = get_source_list()
    for source_idx, source_key in enumerate(source_list):
        get_house_sample_layout(source_key)


# 数据加载
load_room_data()
load_room_sample()


# 功能测试
if __name__ == '__main__':
    # 清空缓存
    search_clear_temp()
    # search_fetch_temp()
    pass

    # 全屋数据
    target_house_set = ['a5bad9de-497f-4fd2-a092-000f4d430925']
    target_house_set = []
    for target_house in target_house_set:
        house_para, house_data = get_house_data(target_house, '', '', reload=False, recalc=False)
    pass

    # 全屋样板
    sample_house_set = ['14b50bdf-1907-47c4-b797-b4a7c579602b']
    sample_house_set = []
    for sample_house in sample_house_set:
        sample_para, sample_data, sample_layout, sample_group = get_house_sample(sample_house, True)
    pass

    # 数据保存
    # save_room_sample()
    # save_furniture_data()
    pass

