# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-07
@Description: 获取家具数据，包括类目、风格、尺寸等

"""

import random
from Furniture.data_oss import *
from Furniture.data_download import *
from Furniture.glm_shape import *
from Furniture.furniture_refer import *

# 临时目录
DATA_DIR_FURNITURE = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(DATA_DIR_FURNITURE):
    os.makedirs(DATA_DIR_FURNITURE)
# OSS位置
DATA_OSS_FURNITURE = 'ihome-alg-furniture'

# 家具数据
FURNITURE_DATA_DICT = {}
FURNITURE_DATA_CATE = {}
FURNITURE_CATE_DICT = {}

FURNITURE_DATA_PACK = {}
FURNITURE_DATA_PLAT = {}

FURNITURE_DATA_TYPE = {}
FURNITURE_DATA_TURN = {}
FURNITURE_DATA_SIZE = {
    'f2daf2ca-5b52-4660-9f8f-9a56ed745137': [270.89999389648436, 81.19090270996093, 215.5]
}
# 尺寸限制
FURNITURE_JSON_RATIO = 1.01


# 数据下载：列举数据
def list_furniture_dir(src_dir):
    furniture_list = []
    if not os.path.exists(src_dir):
        return furniture_list
    for furniture_file in os.listdir(src_dir):
        if not furniture_file.endswith('.json'):
            continue
        furniture_id = furniture_file[:-5]
        furniture_list.append(furniture_id)
    return furniture_list


# 数据下载：列举数据
def list_furniture_oss(src_oss, number=10000):
    furniture_list = []
    file_list = oss_list_file(src_oss, object_ext='.json', object_cnt=number)
    for furniture_file in file_list:
        if not furniture_file.endswith('.json'):
            continue
        furniture_id = furniture_file[:-5]
        furniture_list.append(furniture_id)
    return furniture_list


# 数据下载：家具数据
def download_furniture(furniture_id, des_dir, obj_ext='.json', reload=False):
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    obj_file = furniture_id + obj_ext
    obj_path = os.path.join(des_dir, obj_file)
    if os.path.exists(obj_path) and not reload:
        return
    # 下载数据
    if obj_ext == '.obj':
        if have_furniture_pack(furniture_id):
            pass
        else:
            download_obj(furniture_id, des_dir, reload)
            if not os.path.exists(obj_path):
                add_furniture_pack(furniture_id, 'none')
    elif obj_ext == '.json':
        download_json(furniture_id, des_dir, reload)
    elif obj_ext == '.jpg':
        temp_dir = DATA_DIR_FURNITURE
        if not os.path.exists(temp_dir):
            temp_dir = os.path.dirname(__file__) + '/temp/'
        download_json(furniture_id, temp_dir)
        download_img(furniture_id, temp_dir, des_dir)
    elif obj_ext == '.top':
        temp_dir = DATA_DIR_FURNITURE
        if not os.path.exists(temp_dir):
            temp_dir = os.path.dirname(__file__) + '/temp/'
        download_json(furniture_id, temp_dir)
        download_img(furniture_id, temp_dir, des_dir, 'top')
    elif obj_ext == '.txt':
        temp_dir = DATA_DIR_FURNITURE
        if not os.path.exists(temp_dir):
            temp_dir = os.path.dirname(__file__) + '/temp/'
        download_json(furniture_id, temp_dir)
        download_img(furniture_id, temp_dir, des_dir, 'txt')
    elif obj_ext == '.txt_fc':
        temp_dir = DATA_DIR_FURNITURE
        if not os.path.exists(temp_dir):
            temp_dir = os.path.dirname(__file__) + '/temp/'
        download_json(furniture_id, temp_dir)
        download_img(furniture_id, temp_dir, des_dir, 'txt_fc')
    # 上传数据
    if os.path.exists(obj_path) and False:
        oss_upload_file(obj_file, obj_path, DATA_OSS_FURNITURE)


# 数据下载：家具数据
def download_furniture_image(furniture_id, des_dir, img_name=''):
    temp_dir = DATA_DIR_FURNITURE
    if not os.path.exists(temp_dir):
        temp_dir = os.path.dirname(__file__) + '/temp/'
    download_json(furniture_id, temp_dir)
    download_img(furniture_id, temp_dir, des_dir, img_type='', img_name=img_name)


# 数据解析：加载家具数据
def load_furniture_data(reload=False):
    # 家具详细信息
    global FURNITURE_DATA_DICT
    if len(FURNITURE_DATA_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_dict.json')
        FURNITURE_DATA_DICT = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_DATA_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return FURNITURE_DATA_DICT


# 数据解析：保存家具型数据
def save_furniture_data():
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_dict.json')
    with open(json_path, "w") as f:
        json.dump(FURNITURE_DATA_DICT, f, indent=4)
        f.close()
    print('save furniture data success')


# 数据解析：判断家具数据
def have_furniture_data(furniture_id):
    global FURNITURE_DATA_DICT
    load_furniture_data()
    if furniture_id in FURNITURE_DATA_DICT:
        return True
    else:
        return False


# 数据解析：判断家具数据
def have_furniture_data_key(furniture_id, key=''):
    global FURNITURE_DATA_DICT
    load_furniture_data()
    if furniture_id in FURNITURE_DATA_DICT:
        if not key == '':
            furniture_info = FURNITURE_DATA_DICT[furniture_id]
            if key in furniture_info:
                return True
            else:
                return False
        return True
    else:
        return False


# 数据解析：增加家具数据
def add_furniture_data(obj_id, obj_new):
    if obj_id == '':
        return
    global FURNITURE_DATA_DICT
    load_furniture_data()
    if obj_id in FURNITURE_DATA_DICT:
        obj_old = FURNITURE_DATA_DICT[obj_id]
        if 'type_id' in obj_old and 'type_id' not in obj_new:
            obj_new['type_id'] = obj_old['type_id']
        if 'style_id' in obj_old and 'style_id' not in obj_new:
            obj_new['style_id'] = obj_old['style_id']
        if 'category_id' in obj_old and 'category_id' not in obj_new:
            obj_new['category_id'] = obj_old['category_id']
    FURNITURE_DATA_DICT[obj_id] = obj_new


# 数据解析：加载家具数据
def load_furniture_cate(reload=False):
    global FURNITURE_DATA_CATE
    global FURNITURE_CATE_DICT
    if len(FURNITURE_DATA_CATE) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_cate.json')
        FURNITURE_DATA_CATE = {}
        FURNITURE_CATE_DICT = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_DATA_CATE = json.load(open(json_path, 'r', encoding='utf-8'))
            except Exception as e:
                print(e)
        for cate_key, cate_val in FURNITURE_DATA_CATE.items():
            for cate_one in cate_val:
                if cate_one in FURNITURE_CATE_DICT and cate_key in ['配饰']:
                    continue
                FURNITURE_CATE_DICT[cate_one] = cate_key
    return FURNITURE_DATA_CATE


# 数据解析：保存家具数据
def save_furniture_cate():
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_cate.json')
    with open(json_path, "w") as f:
        json.dump(FURNITURE_DATA_CATE, f, ensure_ascii=False, indent=4)
        f.close()
    print('save furniture cate success')


# 数据解析：获取家具数据
def have_furniture_by_cate(object_id, object_cate):
    global FURNITURE_DATA_CATE
    global FURNITURE_CATE_DICT
    load_furniture_cate()
    if object_id in FURNITURE_CATE_DICT:
        if object_cate == FURNITURE_CATE_DICT[object_id]:
            return True
    return False


# 数据解析：获取家具数据
def get_furniture_list_id(object_cate):
    global FURNITURE_DATA_CATE
    load_furniture_cate()
    id_list = []
    if object_cate in FURNITURE_DATA_CATE:
        id_list = FURNITURE_DATA_CATE[object_cate]
    return id_list


# 数据解析：获取家具数据
def get_furniture_list_by_rand(object_cate):
    global FURNITURE_DATA_CATE
    load_furniture_cate()
    id_list = []
    if object_cate in FURNITURE_DATA_CATE:
        cate_val = FURNITURE_DATA_CATE[object_cate]
        id_idx = random.randint(0, 100) % len(cate_val)
        id_one = cate_val[id_idx]
        id_list.append(id_one)
    elif len(object_cate) > 0:
        for cate_key, cate_val in FURNITURE_DATA_CATE.items():
            if object_cate in cate_key:
                id_idx = random.randint(0, 100) % len(cate_val)
                id_one = cate_val[id_idx]
                id_list.append(id_one)
    obj_list = []
    for obj_id in id_list:
        obj_type, obj_style, obj_size = get_furniture_data(obj_id, '', False, False)
        obj_type_id, obj_style_id, obj_category_id = get_furniture_data_refer_id(obj_id, '', False)
        obj_one = {
            'id': obj_id, 'type': obj_type, 'style': obj_style, 'size': obj_size[:], 'scale': [1, 1, 1],
            'category': obj_category_id, 'position': [0, 0, 0], 'rotation': [0, 0, 0, 1], 'role': '', 'count': 1
        }
        obj_list.append(obj_one)
    return obj_list


# 数据解析：获取家具数据
def get_furniture_list_by_list(id_list):
    obj_list = []
    for obj_id in id_list:
        obj_type, obj_style, obj_size = get_furniture_data(obj_id, '', False, False)
        obj_type_id, obj_style_id, obj_category_id = get_furniture_data_refer_id(obj_id, '', False)
        obj_one = {
            'id': obj_id, 'type': obj_type, 'style': obj_style, 'size': obj_size[:], 'scale': [1, 1, 1],
            'category': obj_category_id, 'position': [0, 0, 0], 'rotation': [0, 0, 0, 1], 'role': '', 'count': 1
        }
        obj_list.append(obj_one)
    return obj_list


# 数据解析：获取家具数据
def get_furniture_cate(object_id):
    global FURNITURE_DATA_CATE
    load_furniture_cate()
    object_cate = ''
    for cate_key, cate_val in FURNITURE_DATA_CATE.items():
        if object_id in cate_val:
            object_cate = cate_key
    return object_cate


# 数据解析：加载家具数据 组合桌 组合床 高低桌 高低柜
def load_furniture_pack(reload=False):
    global FURNITURE_DATA_PACK
    if len(FURNITURE_DATA_PACK) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_pack.json')
        FURNITURE_DATA_PACK = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_DATA_PACK = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return FURNITURE_DATA_PACK


# 数据解析：保存家具数据
def save_furniture_pack():
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_pack.json')
    with open(json_path, "w") as f:
        json.dump(FURNITURE_DATA_PACK, f, indent=4)
        f.close()
    print('save furniture pack success')


# 数据解析：判断家具数据
def have_furniture_pack(furniture_id):
    global FURNITURE_DATA_PACK
    load_furniture_pack()
    if furniture_id in FURNITURE_DATA_PACK:
        return True
    else:
        return False


# 数据解析：增加家具数据
def add_furniture_pack(furniture_id, pack_type='none'):
    if furniture_id == '':
        return
    global FURNITURE_DATA_PACK
    load_furniture_pack()
    FURNITURE_DATA_PACK[furniture_id] = pack_type


# 数据解析：判断家具数据
def get_furniture_pack(furniture_id):
    global FURNITURE_DATA_PACK
    load_furniture_pack()
    if furniture_id in FURNITURE_DATA_PACK:
        return FURNITURE_DATA_PACK[furniture_id]
    else:
        return ''


# 数据解析：加载家具数据 配件位置
def load_furniture_plat(reload=False):
    global FURNITURE_DATA_PLAT
    if len(FURNITURE_DATA_PLAT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_plat.json')
        FURNITURE_DATA_PLAT = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_DATA_PLAT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return FURNITURE_DATA_PLAT


# 数据解析：保存家具数据
def save_furniture_plat():
    # 水平
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_plat.json')
    with open(json_path, "w") as f:
        json.dump(FURNITURE_DATA_PLAT, f, indent=4)
        f.close()
    # 打印
    print('save furniture plat success')


# 数据解析：判断家具数据
def have_furniture_plat(furniture_id):
    global FURNITURE_DATA_PLAT
    load_furniture_plat()
    if furniture_id in FURNITURE_DATA_PLAT:
        return True
    else:
        return False


# 数据解析：增加家具数据
def add_furniture_plat(furniture_id, furniture_plat):
    if furniture_id == '':
        return
    global FURNITURE_DATA_PLAT
    load_furniture_plat()
    FURNITURE_DATA_PLAT[furniture_id] = furniture_plat


# 数据解析：获取家具数据
def get_furniture_plat(furniture_id, furniture_type='', reload=False):
    global FURNITURE_DATA_PLAT
    load_furniture_plat()
    if furniture_id in FURNITURE_DATA_PLAT and not reload:
        return FURNITURE_DATA_PLAT[furniture_id]
    download_furniture(furniture_id, DATA_DIR_FURNITURE + '/obj', '.obj')
    obj_path = os.path.join(DATA_DIR_FURNITURE + '/obj', furniture_id + '.obj')
    if not os.path.exists(obj_path):
        FURNITURE_DATA_PLAT[furniture_id] = {}
        return {}
    if not furniture_type == '':
        obj_type = furniture_type
    else:
        obj_type, obj_style, obj_size = get_furniture_data(furniture_id)
    model, decor_bot, decor_bak, decor_frt, ratio = glm_shape_obj_by_path(obj_path, obj_type)
    furniture_plat = {
        'bot': decor_bot,
        'bak': decor_bak,
        'frt': decor_frt,
        'model': model
    }
    FURNITURE_DATA_PLAT[furniture_id] = furniture_plat
    return furniture_plat


# 数据解析：获取家具数据
def get_furniture_plat_detail(furniture_id, furniture_type='', plat_type='bot', reload=False):
    furniture_plat = get_furniture_plat(furniture_id, furniture_type, reload)
    if plat_type in furniture_plat:
        return furniture_plat[plat_type]
    else:
        return {}


# 数据解析：加载家具数据
def load_furniture_type(reload=False):
    global FURNITURE_DATA_TYPE
    if len(FURNITURE_DATA_TYPE) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_type.json')
        FURNITURE_DATA_TYPE = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_DATA_TYPE = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return FURNITURE_DATA_TYPE


# 数据解析：保存家具数据
def save_furniture_type():
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_type.json')
    with open(json_path, "w") as f:
        json.dump(FURNITURE_DATA_TYPE, f, indent=4)
        f.close()
    print('save furniture type success')


# 数据解析：判断家具数据
def have_furniture_type(furniture_id):
    global FURNITURE_DATA_TYPE
    load_furniture_type()
    if furniture_id in FURNITURE_DATA_TYPE:
        return True
    else:
        return False


# 数据解析：判断家具数据
def add_furniture_type(furniture_id, furniture_type=''):
    global FURNITURE_DATA_TYPE
    load_furniture_type()
    if furniture_id not in FURNITURE_DATA_TYPE:
        FURNITURE_DATA_TYPE[furniture_id] = {'type': ''}
    if furniture_id in FURNITURE_DATA_TYPE:
        if not furniture_type == '':
            FURNITURE_DATA_TYPE[furniture_id]['type'] = furniture_type


# 数据解析：判断家具朝向
def get_furniture_direct(furniture_id):
    global FURNITURE_DATA_TYPE
    load_furniture_type()
    if furniture_id in FURNITURE_DATA_TYPE:
        furniture_val = FURNITURE_DATA_TYPE[furniture_id]
        if 'closeness_direction' in furniture_val:
            furniture_direct = furniture_val['closeness_direction']
            if furniture_direct in ['LEFT', 'left']:
                return -1
            elif furniture_direct in ['RIGHT', 'right']:
                return 1
    return 0


# 数据解析：加载家具数据
def load_furniture_size(reload=False):
    global FURNITURE_DATA_SIZE
    if len(FURNITURE_DATA_SIZE) <= 0 or reload:
        pass
    return FURNITURE_DATA_SIZE


# 数据解析：加载家具数据
def load_furniture_turn(reload=False):
    global FURNITURE_DATA_TURN
    if len(FURNITURE_DATA_TURN) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_turn.json')
        FURNITURE_DATA_TURN = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_DATA_TURN = json.load(open(json_path, 'r', encoding='utf-8'))
            except Exception as e:
                print(e)
    return FURNITURE_DATA_TURN


# 数据解析：保存家具数据
def save_furniture_turn():
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_data_turn.json')
    with open(json_path, "w") as f:
        json.dump(FURNITURE_DATA_TURN, f, ensure_ascii=False, indent=4)
        f.close()
    print('save furniture turn success')


def have_furniture_turn(furniture_id):
    global FURNITURE_DATA_TURN
    load_furniture_type()
    if furniture_id in FURNITURE_DATA_TURN:
        return True
    else:
        return False


# 数据解析：判断家具数据
def get_furniture_turn(furniture_id):
    global FURNITURE_DATA_TURN
    load_furniture_turn()
    if furniture_id in FURNITURE_DATA_TURN:
        return FURNITURE_DATA_TURN[furniture_id]
    return 0


# 数据解析：判断家具数据
def add_furniture_turn(furniture_id, furniture_turn=0):
    global FURNITURE_DATA_TURN
    load_furniture_turn()
    FURNITURE_DATA_TURN[furniture_id] = furniture_turn


# 数据解析：获取家具数据 深拷贝
def get_furniture_data_by_id(obj_id):
    global FURNITURE_DATA_DICT
    load_furniture_data()
    if obj_id in FURNITURE_DATA_DICT:
        return FURNITURE_DATA_DICT[obj_id].copy()
    else:
        return {}


# 数据检索：获取家具数据 自动下载 解析数据
def get_furniture_data(furniture_id, furniture_dir='', auto_add=True, reload=False):
    furniture_id = os.path.basename(furniture_id)
    if furniture_id.endswith('.obj'):
        furniture_id = furniture_id[:-4]
    elif furniture_id.endswith('.json'):
        furniture_id = furniture_id[:-5]
    # 已有数据
    furniture_all = load_furniture_data()
    furniture_fix_type = load_furniture_type()
    furniture_fix_size = load_furniture_size()
    furniture_fix_turn = load_furniture_turn()
    obj_info = {}
    if furniture_id in furniture_all and not reload:
        obj_info = furniture_all[furniture_id]
        if 'type' in obj_info and 'style' in obj_info and 'size' in obj_info:
            pass
        else:
            print('get furniture data error', furniture_id)
    if 'type' in obj_info and 'style' in obj_info and 'size' in obj_info:
        obj_type, obj_style_en = obj_info['type'], obj_info['style']
        obj_size = [abs(obj_info['size'][i]) for i in range(3)]
        # 纠正尺寸
        size_old = obj_size[:]
        if furniture_id in furniture_fix_size:
            obj_size = furniture_fix_size[furniture_id][:]
        # 纠正类型
        if furniture_id in furniture_fix_type:
            furniture_new = furniture_fix_type[furniture_id]
            if 'type' in furniture_new:
                obj_type = furniture_new['type']
        # 返回信息
        return obj_type, obj_style_en, obj_size
    # 解析数据
    obj_type, obj_style, obj_style_en, obj_size = '', '', '', [0, 0, 0]
    obj_type_id, obj_style_id, obj_category_id = '', '', ''
    obj_pack = '3D'
    # 属性
    try:
        json_info = download_hsf_get(furniture_id)
        if not json_info:
            return '', '', [0, 0, 0]
        if 'item' not in json_info:
            return '', '', [0, 0, 0]
        attributes = json_info['item']['attributes']
        boundingbox = json_info['item']['boundingBox']
        if 'productType' in json_info['item']:
            obj_pack = json_info['item']['productType']
    except Exception as e:
        print(e)
        attributes = []
        boundingbox = {}
    # 类型 风格
    for attribute_one in attributes:
        # 类型
        if attribute_one['name'] == 'ContentType':
            if len(attribute_one['values']) > 0:
                obj_type = attribute_one['values'][0]['value']
                obj_type_id = attribute_one['values'][0]['id']
            else:
                obj_type = ''
        # 风格
        elif attribute_one['name'] in ['风格', 'Styles']:
            if len(attribute_one['values']) > 0:
                obj_style = attribute_one['values'][0]['value']
                obj_style_id = attribute_one['values'][0]['id']
            else:
                obj_style = ''
        # 判断
        if obj_type == '' or obj_style == '':
            pass
        else:
            break
    obj_style_en = get_furniture_style_en(obj_style)
    # 品类
    if 'item' in json_info and 'categories' in json_info['item']:
        categories = json_info['item']['categories']
        if categories and len(categories) > 0:
            obj_category_id = categories[0]
    # 尺寸
    if 'xLen' in boundingbox:
        size_x, size_y, size_z = boundingbox['xLen'], boundingbox['zLen'], boundingbox['yLen']
        obj_size = [size_x, size_y, size_z]
    else:
        obj_size = [0, 0, 0]
    # 组合
    if obj_pack not in ['3d', '3D']:
        add_furniture_pack(furniture_id, obj_pack)
    # 判断
    if obj_type == '' or obj_size[0] == 0 or obj_size[2] == 0:
        return obj_type, obj_style_en, obj_size
    # 纠正
    if furniture_id in furniture_fix_size:
        obj_size = furniture_fix_size[furniture_id][:]
    if furniture_id in furniture_fix_type:
        furniture_new = furniture_fix_type[furniture_id]
        if 'type' in furniture_new:
            obj_type = furniture_new['type']
    # 记录
    if auto_add:
        obj_info = get_furniture_data_by_id(furniture_id)
        obj_info['type'] = obj_type
        obj_info['style'] = obj_style_en
        obj_info['size'] = obj_size
        obj_info['size_obj'] = obj_size[:]
        obj_info['type_id'] = obj_type_id
        obj_info['style_id'] = obj_style_id
        obj_info['category_id'] = obj_category_id
        add_furniture_data(furniture_id, obj_info)
    # 返回
    return obj_type, obj_style_en, obj_size


# 数据获取：获取居然信息
def get_furniture_data_more(furniture_id, furniture_dir='', auto_add=True, reload=False):
    # 信息
    obj_type, obj_style, obj_style_en, obj_size = '', '', '', [0, 0, 0]
    obj_type_id, obj_style_id, obj_category_id = '', '', ''
    # 已有数据
    obj_info = {}
    furniture_all = load_furniture_data()
    if furniture_id in furniture_all and not reload:
        obj_info = furniture_all[furniture_id]
    if 'type' in obj_info and 'style' in obj_info and 'size' in obj_info:
        obj_type, obj_style_en = obj_info['type'], obj_info['style']
        obj_size = [abs(obj_info['size'][i]) for i in range(3)]
    if 'type_id' in obj_info and 'style_id' in obj_info and 'category_id' in obj_info:
        obj_type_id, obj_style_id, obj_category_id = obj_info['type_id'], obj_info['style_id'], obj_info['category_id']
    if not obj_type == '' and not obj_type_id == '' and not obj_style_id == '' and not obj_category_id == '':
        return obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id
    # 文件
    json_info = download_hsf_get(furniture_id)
    if not json_info:
        return obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id
    if 'item' not in json_info:
        return obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id
    # 尺寸
    if 'item' in json_info and 'boundingBox' in json_info['item']:
        bounding_box = json_info['item']['boundingBox']
        obj_size = [bounding_box['xLen'], bounding_box['zLen'], bounding_box['yLen']]
    # 类型 风格
    if 'item' in json_info and 'attributes' in json_info['item']:
        for attribute_one in json_info['item']['attributes']:
            if attribute_one['name'] == 'ContentType':
                if 'values' in attribute_one and len(attribute_one['values']) > 0:
                    obj_type = attribute_one['values'][0]['value']
                    obj_type_id = attribute_one['values'][0]['id']
            elif attribute_one['name'] in ['风格', 'Styles']:
                if 'values' in attribute_one and len(attribute_one['values']) > 0:
                    obj_style = attribute_one['values'][0]['value']
                    obj_style_id = attribute_one['values'][0]['id']
            # 判断
            if obj_type == '' or obj_style == '':
                pass
            else:
                break
    obj_style_en = get_furniture_style_en(obj_style)
    # 品类
    if 'item' in json_info and 'categories' in json_info['item']:
        categories = json_info['item']['categories']
        if categories and len(categories) > 0:
            obj_category_id = categories[0]
    # 记录
    if auto_add:
        obj_info = get_furniture_data_by_id(furniture_id)
        obj_info['type'] = obj_type
        obj_info['style'] = obj_style_en
        obj_info['size'] = obj_size
        obj_info['size_obj'] = obj_size[:]
        obj_info['type_id'] = obj_type_id
        obj_info['style_id'] = obj_style_id
        obj_info['category_id'] = obj_category_id
        add_furniture_data(furniture_id, obj_info)
    # 返回
    return obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id


# 数据获取
def get_furniture_data_refer_id(furniture_id, furniture_dir='', reload=False):
    type_id, style_id, category_id = '', '', ''
    furniture_id = os.path.basename(furniture_id)
    if furniture_id.endswith('.obj'):
        furniture_id = furniture_id[:-4]
    elif furniture_id.endswith('.json'):
        furniture_id = furniture_id[:-5]
    # 已有数据
    obj_info = {}
    furniture_all = load_furniture_data()
    if furniture_id in furniture_all and not reload:
        obj_info = furniture_all[furniture_id]
    type_cnt, style_cnt, category_cnt = 0, 0, 0
    if 'type_id' in obj_info:
        type_id = obj_info['type_id']
        type_cnt = 1
    if 'style_id' in obj_info:
        style_id = obj_info['style_id']
        style_cnt = 1
    if 'category_id' in obj_info and len(obj_info['category_id']) > 0:
        category_id = obj_info['category_id']
        category_cnt = 1
    if 'category' in obj_info and len(obj_info['category']) > 0:
        category_id = obj_info['category']
        category_cnt = 1
        # 更新
        obj_info['category_id'] = category_id
        if 'category' in obj_info:
            obj_info.pop('category')
    if type_cnt + style_cnt >= 1 and category_cnt >= 1:
        return type_id, style_id, category_id
    # 解析数据
    obj_type, obj_style, obj_style_en, obj_size = '', '', '', [0, 0, 0]
    try:
        json_info = download_hsf_get(furniture_id)
        if not json_info:
            return type_id, style_id, category_id
        if 'item' not in json_info:
            return type_id, style_id, category_id
        attributes = json_info['item']['attributes']
        boundingbox = json_info['item']['boundingBox']
    except Exception as e:
        print(e)
        attributes = []
        boundingbox = {}
    # 类型 风格
    for attribute_one in attributes:
        # 类型
        if attribute_one['name'] == 'ContentType':
            if len(attribute_one['values']) > 0:
                obj_type = attribute_one['values'][0]['value']
                type_id = attribute_one['values'][0]['id']
            else:
                obj_type = ''
                type_id = ''
        # 风格
        elif attribute_one['name'] in ['风格', 'Styles']:
            if len(attribute_one['values']) > 0:
                obj_style = attribute_one['values'][0]['value']
                style_id = attribute_one['values'][0]['id']
            else:
                obj_style = ''
                style_id = ''
        # 判断
        if type_id == '' or style_id == '':
            pass
        else:
            break
    obj_style_en = get_furniture_style_en(obj_style)
    # 尺寸
    if 'xLen' in boundingbox:
        size_x, size_y, size_z = boundingbox['xLen'], boundingbox['zLen'], boundingbox['yLen']
        obj_size = [size_x, size_y, size_z]
    else:
        obj_size = [0, 0, 0]
    # 品类
    if 'categories' in json_info['item']:
        if json_info['item']['categories'] and len(json_info['item']['categories']) > 0:
            category_id = json_info['item']['categories'][0]
    # 添加
    obj_info = get_furniture_data_by_id(furniture_id)
    obj_info['type'] = obj_type
    obj_info['style'] = obj_style_en
    obj_info['size'] = obj_size
    obj_info['size_obj'] = obj_size[:]
    obj_info['type_id'] = type_id
    obj_info['style_id'] = style_id
    obj_info['category_id'] = category_id
    add_furniture_data(furniture_id, obj_info)
    return type_id, style_id, category_id


# 获取数据
def get_furniture_data_check(furniture_id):
    global FURNITURE_DATA_TYPE
    load_furniture_type()
    if furniture_id in FURNITURE_DATA_TYPE:
        return FURNITURE_DATA_TYPE[furniture_id]
    else:
        return {}


# 数据更新：更新模型信息
def refresh_furniture_data_all(data_flag=True, file_flag=False):
    load_furniture_data()
    # 批量信息 检查尺寸
    furniture_cnt = 0
    furniture_cnt_data = 0
    furniture_cnt_file = 0
    furniture_cnt_skip = 0
    for furniture_id, furniture_data in FURNITURE_DATA_DICT.items():
        furniture_cnt += 1
        # 文件下载
        if file_flag:
            json_path = os.path.join(DATA_DIR_FURNITURE + '/obj/', furniture_id + '.obj')
            if os.path.exists(json_path):
                continue
            download_furniture(furniture_id, DATA_DIR_FURNITURE + '/obj/', '.obj')
            download_furniture(furniture_id, DATA_DIR_FURNITURE, '.jpg')
            download_furniture(furniture_id, DATA_DIR_FURNITURE, '.json')
            download_furniture(furniture_id, DATA_DIR_FURNITURE + '/top/', '.top')
            download_furniture(furniture_id, DATA_DIR_FURNITURE + '/txt/', '.txt')
            download_furniture(furniture_id, DATA_DIR_FURNITURE + '/txt_fc/', '.txt_fc')
            furniture_cnt_file += 1
            # 打印信息
            if furniture_cnt_file % 100 == 0:
                print('check furniture file %05d %05d' % (furniture_cnt_file, furniture_cnt))
            if furniture_cnt_file >= 100:
                break
        # 数据更新
        if data_flag:
            if furniture_cnt <= furniture_cnt_skip:
                continue
            if 'type' in furniture_data and 'style' in furniture_data and 'size' in furniture_data:
                pass
            else:
                print(furniture_id)
                furniture_cnt_data += 1
                # 打印信息
                if furniture_cnt_data % 100 == 0:
                    print('check furniture data %05d %05d' % (furniture_cnt_data, furniture_cnt))
                    save_furniture_data()
            # 品类风格
            obj_type, obj_style_en, obj_size = get_furniture_data(furniture_id, '', True, True)
            old_type_id, old_style_id, old_category_id = get_furniture_data_refer_id(furniture_id, '', False)
            obj_type_id, obj_style_id, obj_category_id = get_furniture_data_refer_id(furniture_id, '', True)
            if not old_category_id == obj_category_id:
                furniture_cnt_data += 1
                # 打印信息
                if furniture_cnt_data % 100 == 0:
                    print('check furniture data %05d %05d' % (furniture_cnt_data, furniture_cnt))
                    save_furniture_data()
            if obj_style_en == '' and not obj_style_id == '':
                object_style = get_furniture_style_by_id(obj_style_id)
                object_style_en = get_furniture_style_en(object_style)
                furniture_data['style'] = object_style_en
        # 打印信息
        if furniture_cnt % 100 == 0:
            print('check furniture %05d %05d' % (furniture_cnt_data, furniture_cnt))
            save_furniture_data()
        if furniture_cnt >= furniture_cnt_skip + 40000:
            break
    # 打印信息
    print('check furniture %05d %05d' % (furniture_cnt_data, furniture_cnt))


# 数据更新：更新模型信息
def refresh_furniture_data_set(furniture_list):
    load_furniture_data()
    load_furniture_pack()
    load_furniture_turn()
    for furniture_idx, furniture_key in enumerate(furniture_list):
        # 更新基本信息
        obj_type, obj_style_en, obj_size = get_furniture_data(furniture_key, '', True, True)
        obj_type_id, obj_style_id, obj_category_id = get_furniture_data_refer_id(furniture_key, '', True)
        # 更新组合标签 TODO:

        # 更新朝向标签 TODO:
        pass
    save_furniture_data()
    save_furniture_pack()
    save_furniture_turn()
    pass


# 数据更新：更新模型信息
def refresh_furniture_data_obj():
    load_furniture_data()
    # 批量信息 检查尺寸
    furniture_cnt = 0
    furniture_cnt_fix = 0
    for furniture_id, furniture_data in FURNITURE_DATA_DICT.items():
        furniture_cnt += 1
        # 打印信息
        if furniture_cnt % 1000 == 0:
            print('check furniture %05d %05d' % (furniture_cnt_fix, furniture_cnt))
        obj_type, obj_style_en, obj_size = get_furniture_data(furniture_id)
        # 检查json尺寸
        if 'size_obj' in furniture_data:
            # obj_type, obj_style_en, obj_size = get_furniture_data(furniture_id, '', True, True)
            size_old = furniture_data['size']
            size_new = furniture_data['size_obj']
            if size_old[0] > size_new[0] * FURNITURE_JSON_RATIO or size_old[1] > size_new[1] * FURNITURE_JSON_RATIO or \
                    size_old[2] > size_new[2] * FURNITURE_JSON_RATIO:
                furniture_cnt_fix += 1
            continue
        # 检查obj尺寸
        download_furniture(furniture_id, DATA_DIR_FURNITURE + '/obj', '.obj')
        obj_path = os.path.join(DATA_DIR_FURNITURE + '/obj', furniture_id + '.obj')
        if not os.path.exists(obj_path):
            furniture_data['size_obj'] = [0, 0, 0]
            continue
        # 读取模型
        obj = glm_read_obj(obj_path)
        if not obj:
            furniture_data['size_obj'] = [0, 0, 0]
            continue
        # 模型尺寸
        size_max = obj.bbox.max
        size_min = obj.bbox.min
        size_obj = [size_max[0] - size_min[0], size_max[1] - size_min[1], size_max[2] - size_min[2]]
        size_new = [round(i, 4) for i in size_obj]
        furniture_data['size_obj'] = size_new[:]
        # 纠正尺寸
        size_old = furniture_data['size']
        if size_old[0] > size_new[0] * FURNITURE_JSON_RATIO or size_old[1] > size_new[1] * FURNITURE_JSON_RATIO or \
                size_old[2] > size_new[2] * FURNITURE_JSON_RATIO:
            furniture_cnt_fix += 1
    # 打印信息
    print('check furniture %05d / %05d' % (furniture_cnt_fix, furniture_cnt))


# 数据更新：更新几何数据
def refresh_furniture_shape(shape_type=''):
    pass


# 数据修正：修正模型尺寸
def correct_furniture_size(furniture_id, size_old):
    global FURNITURE_DICT_SIZE
    if furniture_id in FURNITURE_DICT_SIZE:
        size_new = FURNITURE_DICT_SIZE[furniture_id]
        if len(size_old) >= 3:
            size_old[0] = size_new[0]
            size_old[1] = size_new[1]
            size_old[2] = size_new[2]


# 数据加载
load_furniture_data()
load_furniture_cate()
load_furniture_pack()
load_furniture_plat()
load_furniture_turn()
load_furniture_type()


# 功能测试
if __name__ == '__main__':
    # 批量信息
    furniture_list_0 = [
        "888ffe40-ad39-4bee-8c4c-ed03c3369533",
        "ad6fb4d5-c114-4887-946f-19fe61e38e20",
        "4ce8dbb4-1da6-4908-b9c7-89623d6a6af3",
        "f448278c-9b14-4fde-8cfe-df93832244c3",
        "09f1e2fc-eb93-4173-bc1a-8891374f8b87",
        "99a01dac-43a9-4e6b-b443-9a1c83241b4c"
    ]
    # furniture_list_0 = []
    furniture_list = furniture_list_0
    for furniture_one in furniture_list:
        download_furniture(furniture_one, DATA_DIR_FURNITURE, '.jpg')
        # download_furniture(furniture_one, DATA_DIR_FURNITURE + '/obj/', '.obj')
        obj_type, obj_style_en, obj_size = get_furniture_data(furniture_one, '', True, True)
        obj_type_id, obj_style_id, obj_category_id = get_furniture_data_refer_id(furniture_one, '', True)
        print('furniture:', furniture_one)
        print(obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id)

    # 单批信息
    furniture_id = "888ffe40-ad39-4bee-8c4c-ed03c3369533"
    download_furniture(furniture_id, DATA_DIR_FURNITURE, '.jpg')
    download_furniture(furniture_id, DATA_DIR_FURNITURE, '.json')
    download_furniture(furniture_id, DATA_DIR_FURNITURE + '/obj/', '.obj')
    # download_furniture(furniture_id, DATA_DIR_FURNITURE + '/txt/', '.txt')
    pass

    # 单批信息
    obj_type, obj_style_en, obj_size = get_furniture_data(furniture_id, '', False, False)
    obj_type_id, obj_style_id, obj_category_id = get_furniture_data_refer_id(furniture_id, '', False)
    print('furniture:', furniture_id)
    print(obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id)

    obj_type, obj_style_en, obj_size = get_furniture_data(furniture_id, '', True, True)
    obj_type_id, obj_style_id, obj_category_id = get_furniture_data_refer_id(furniture_id, '', True)
    print('furniture:', furniture_id)
    print(obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id)

    obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id = get_furniture_data_more(furniture_id)
    print('furniture:', furniture_id)
    print(obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id)

    # 更新模型
    from Furniture.glm_interface import *
    # refresh_furniture_data_obj()
    # refresh_furniture_data_all()
    pass

    # 更新品类
    for cate_key, cate_val in FURNITURE_DATA_CATE.items():
        continue
        print('category:', cate_key)
        for furniture_id in cate_val:
            obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id = \
                get_furniture_data_more(furniture_id)
    pass

    # 保存信息
    save_furniture_data()
    pass

