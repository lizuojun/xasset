# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-07
@Description: 获取户型数据、特征、布局信息等

"""

from House.data_download import *
from House.data_oss import *
from House.house_data import *

# 临时目录
DATA_DIR_HOUSE = os.path.dirname(__file__) + '/temp/'
DATA_DIR_HOUSE_EMPTY = os.path.dirname(__file__) + '/temp/empty/'
DATA_DIR_HOUSE_SAMPLE = os.path.dirname(__file__) + '/temp/sample/'
if not os.path.exists(DATA_DIR_HOUSE):
    os.makedirs(DATA_DIR_HOUSE)
if not os.path.exists(DATA_DIR_HOUSE_EMPTY):
    os.makedirs(DATA_DIR_HOUSE_EMPTY)
if not os.path.exists(DATA_DIR_HOUSE_SAMPLE):
    os.makedirs(DATA_DIR_HOUSE_SAMPLE)
# OSS位置
DATA_OSS_HOUSE = 'ihome-alg-sample-room'
DATA_OSS_HOUSE_FINE = 'ihome-alg-sample-room-fine'
DATA_OSS_HOUSE_EMPTY = 'ihome-alg-sample-room-empty'
# 房屋数据
HOUSE_DATA_DICT = {}
HOUSE_FEATURE_DICT = {}


# 数据下载：列举数据
def list_house_dir(src_dir):
    house_list = []
    if not os.path.exists(src_dir):
        return house_list
    for house_file in os.listdir(src_dir):
        if not house_file.endswith('.json'):
            continue
        hosue_id = house_file[:-5]
        house_list.append(hosue_id)
    return house_list


# 数据下载：列举数据
def list_house_oss(src_oss, index=0, number=10000):
    house_list, file_list = [], []
    try:
        file_list = oss_list_file(src_oss, object_ext='.json', object_idx=index, object_cnt=number)
    except Exception as e:
        print(e)
        if src_oss == DATA_OSS_HOUSE_FINE:
            return list_house_dir(DATA_DIR_HOUSE_SAMPLE)
    for house_file in file_list:
        if not house_file.endswith('.json'):
            continue
        hosue_id = house_file[:-5]
        house_list.append(hosue_id)
    return house_list


# 数据下载：样板间
def download_house(house_id, des_dir, house_ext='.json', reload=False):
    house_file = house_id + house_ext
    house_path = os.path.join(des_dir, house_file)
    if os.path.exists(house_path) and not reload:
        return house_path
    try:
        # OSS下载
        if oss_exist_file(house_file, DATA_OSS_HOUSE):
            oss_download_file(house_file, house_path, DATA_OSS_HOUSE)
        # 居然下载
        else:
            # 下载数据
            download_scene_by_id(house_id, des_dir)
            # 上传数据
            if os.path.exists(house_path):
                oss_upload_file(house_file, house_path, DATA_OSS_HOUSE)
    except Exception as e:
        print(e)
    return house_path


# 数据下载：空户型
def download_house_empty(house_id, des_dir, house_ext='.json', reload=False):
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    house_file = house_id + house_ext
    house_path = os.path.join(des_dir, house_file)
    if os.path.exists(house_path) and not reload:
        return house_path
    try:
        # OSS下载
        if oss_exist_file(house_file, DATA_OSS_HOUSE_EMPTY):
            oss_download_file(house_file, house_path, DATA_OSS_HOUSE_EMPTY)
        # 居然下载
        else:
            # 下载数据
            download_scene_by_id(house_id, des_dir)
            # 上传数据
            if os.path.exists(house_path):
                oss_upload_file(house_file, house_path, DATA_OSS_HOUSE_EMPTY)
    except Exception as e:
        print(e)
    return house_path


# 数据解析：加载户型数据
def load_house_data(reload=False):
    global HOUSE_DATA_DICT
    if len(HOUSE_DATA_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'house_data_dict.json')
        HOUSE_DATA_DICT = {}
        if os.path.exists(json_path):
            try:
                HOUSE_DATA_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return HOUSE_DATA_DICT


# 数据解析：保存户型数据
def save_house_data():
    global HOUSE_DATA_DICT
    json_path = os.path.join(os.path.dirname(__file__), 'house_data_dict.json')
    with open(json_path, "w") as f:
        json.dump(HOUSE_DATA_DICT, f, indent=4)
        f.close()
    print('save house data success')


# 数据解析：增加户型数据
def add_house_data(house_id, house_info):
    if house_id == '':
        return
    global HOUSE_DATA_DICT
    load_house_data()
    HOUSE_DATA_DICT[house_id] = house_info


# 数据解析：获取户型数据 深拷贝
def get_house_data_by_id(house_id):
    global HOUSE_DATA_DICT
    load_house_data()
    if house_id in HOUSE_DATA_DICT:
        return HOUSE_DATA_DICT[house_id].copy()
    else:
        return {}


# 特征提取：加载户型特征
def load_house_feature(reload=False):
    global HOUSE_FEATURE_DICT
    if len(HOUSE_FEATURE_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'house_feature_dict.json')
        HOUSE_FEATURE_DICT = {}
        if os.path.exists(json_path):
            try:
                HOUSE_FEATURE_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return HOUSE_FEATURE_DICT


# 特征提取：保存户型特征
def save_house_feature():
    global HOUSE_FEATURE_DICT
    json_path = os.path.join(os.path.dirname(__file__), 'house_feature_dict.json')
    with open(json_path, "w") as f:
        json.dump(HOUSE_FEATURE_DICT, f, indent=4)
        f.close()
    print('save house feature success')


# 特征提取：增加户型特征
def add_house_feature(house_id, room_id, room_feature):
    if house_id == '':
        return
    global HOUSE_FEATURE_DICT
    load_house_feature()
    if house_id in HOUSE_FEATURE_DICT:
        feature_dict = HOUSE_FEATURE_DICT[house_id]
        feature_dict[room_id] = room_feature
    else:
        feature_dict = {room_id: room_feature}
        HOUSE_FEATURE_DICT[house_id] = feature_dict


# 特征提取：获取户型特征 深拷贝
def get_house_feature_by_id(house_id):
    global HOUSE_FEATURE_DICT
    load_house_feature()
    if house_id in HOUSE_FEATURE_DICT:
        return HOUSE_FEATURE_DICT[house_id].copy()
    else:
        return {}


# 数据检索：获取户型数据 自动下载 解析数据 提取特征
def get_house_data_feature(house_id, reload=False):
    # 户型数据
    house_id_new = house_id
    house_data_info = {}
    house_feature_info = {}

    # 数据标识
    house_id = os.path.basename(house_id)
    if house_id.endswith('.json'):
        house_id = house_id[:-5]
    # 加载数据
    house_data_all = load_house_data()
    house_feature_all = load_house_feature()
    if house_id in house_data_all and house_id in house_feature_all and not reload:
        house_data_info = house_data_all[house_id]
        house_feature_info = house_feature_all[house_id]
        return house_id_new, house_data_info, house_feature_info
    # 本地数据
    temp_dir = DATA_DIR_HOUSE_SAMPLE
    if not os.path.exists(temp_dir):
        temp_dir = os.path.dirname(__file__) + '/temp'
    house_path = os.path.join(temp_dir, house_id + '.json')
    if not os.path.exists(house_path):
        temp_dir = DATA_DIR_HOUSE_EMPTY
        if not os.path.exists(temp_dir):
            temp_dir = os.path.dirname(__file__) + '/temp'
        house_path = os.path.join(temp_dir, house_id + '.json')
    if os.path.exists(house_path):
        try:
            # 解析数据
            house_json = json.load(open(house_path, 'r', encoding='utf-8'))
            house_id_new, house_data_info, house_feature_info = get_house_data_feature_by_json(house_json, house_id)
            return house_id_new, house_data_info, house_feature_info
        except Exception as e:
            os.remove(house_path)
            print(e)
    # 下载数据
    download_house_empty(house_id, temp_dir)
    if not os.path.exists(house_path):
        download_house(house_id, temp_dir)
    if not os.path.exists(house_path):
        print()
        print('file not exist:', house_id)
        return house_id_new, house_data_info, house_feature_info
    try:
        # 解析数据
        house_json = json.load(open(house_path, 'r', encoding='utf-8'))
        house_id_new, house_data_info, house_feature_info = get_house_data_feature_by_json(house_json, house_id)
    except Exception as e:
        house_id_new = house_id
        house_data_info = {}
        house_feature_info = {}
        print(e)
    return house_id_new, house_data_info, house_feature_info


# 数据解析：获取户型数据 深拷贝
def get_house_data_feature_by_path(house_path, house_id='', todo_room=[]):
    house_id_new, house_data_info, house_feature_info = house_id, {}, {}
    if os.path.exists(house_path):
        house_file = os.path.basename(house_path)
        if house_file.endswith('.json'):
            house_json = json.load(open(house_path, 'r', encoding='utf-8'))
            if house_id == '':
                house_id = house_file[:-5].split('_')[0]
            if house_id == 'scene':
                house_id = ''
            house_id_new, house_data_info, house_feature_info = \
                get_house_data_feature_by_json(house_json, house_id, todo_room)
    return house_id_new, house_data_info, house_feature_info


# 数据检索：获取户型数据 解析数据 提取特征 增加数据 增加特征
def get_house_data_feature_by_json(house_json, house_id='', todo_room=[]):
    # 户型数据
    house_id_new, house_data_info, house_feature_info = house_id, {}, {}

    # 解析数据
    if len(house_id_new) <= 0 and 'uid' in house_json:
        house_id_new = house_json['uid']
    house_data = HouseData()
    house_data.load_json(house_json, load_mesh=False, load_room=todo_room)
    if len(house_data.house_info) <= 0:
        return house_id, house_data_info, house_feature_info
    # 提取户型
    house_data_info = {'id': house_id, 'room': house_data.house_info['room']}
    for room_info in house_data_info['room']:
        if room_info['type'] not in ROOM_TYPE_LIST:
            for type_one in ROOM_TYPE_LIST:
                if room_info['id'].startswith(type_one):
                    room_info['type'] = type_one
                    break
    # 校正坐标
    if 'room' in house_data_info:
        for room_one in house_data_info['room']:
            if 'coordinate' not in room_one:
                room_one['coordinate'] = 'xzy'
            if 'unit' not in room_one:
                room_one['unit'] = 'm'
    # 返回数据
    return house_id_new, house_data_info, house_feature_info


# 数据加载
load_house_data()


# 功能测试
if __name__ == '__main__':
    house_list = list_house_oss(DATA_OSS_HOUSE_EMPTY, number=1000)
    # 单批
    house_id = '0d8edd78-6d9b-46c3-b3c9-296d17273da3'

    house_id_new, house_data_info, house_feature_info = get_house_data_feature(house_id, True)
    print('house:', house_id)
    print(house_data_info)

    # 批量提取
    house_list = list_house_oss(DATA_OSS_HOUSE_FINE)
    for house_idx, house_id in enumerate(house_list):
        house_id_new, house_data_info, house_feature_info = get_house_data_feature(house_id, True)
        print('house:', house_id, house_idx)
        add_house_data(house_id_new, house_data_info)
    save_house_data()
    save_house_feature()



