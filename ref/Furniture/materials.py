# -*- coding: utf-8 -*-

"""
@Author: zhanghuichao
@Date: 2021-09-01
@Description: 获取家具数据，包括类目、风格、尺寸等

"""

from Furniture.data_download import *
from Furniture.furniture_refer import *
import requests
from io import BytesIO
from PIL import Image
import numpy as np


def change_env_flag_mat(flag):
    global ENV_FLAG
    ENV_FLAG = flag


# 临时目录
DATA_DIR_FURNITURE = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(DATA_DIR_FURNITURE):
    os.makedirs(DATA_DIR_FURNITURE)
# OSS位置
DATA_OSS_FURNITURE = 'ihome-alg-furniture'

# 家具数据

MATERIAL_DATA_DICT = {}
MATERIAL_DATA_CATE_DICT = {}
CERAMIC_REFERENCE_DICT = {}
MATERIAL_FEATURE_DICT = {}

CERAMIC_REFERENCE_MATERIAL_URL = 'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/%s/reference.json'

DATA_DIR_MODEL_INFO = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(DATA_DIR_MODEL_INFO):
    os.makedirs(DATA_DIR_MODEL_INFO)

MODEL_SERVICE_HSF_IP_PRO = "calcifer-api.alibaba-inc.com.vipserver"
MODEL_SERVICE_HSF_IP_PRE = "pre-calcifer-api.alibaba-inc.com.vipserver"
MODEL_SERVICE_HSF_IP_LOC = "11.167.121.119"

MODEL_SEARCH_HSF_URL = ''


def model_search_hsf_url():
    global MODEL_SEARCH_HSF_URL
    if MODEL_SEARCH_HSF_URL == '':
        env, loc, ver = '', MODEL_SERVICE_HSF_IP_PRE, ''
        try:
            r = requests.get('http://jmenv.tbsite.net:8080/env', timeout=1)
            r.raise_for_status()
            env = r.text.strip()
        except Exception as e:
            print('get environment error:', e)
        if 'daily' in env:
            loc = MODEL_SERVICE_HSF_IP_LOC
            ver = '1.0.0.daily'
            return "daily_test"
        elif 'pre' in env:
            loc = MODEL_SERVICE_HSF_IP_PRE
            ver = '1.0.0'
        else:
            loc = MODEL_SERVICE_HSF_IP_PRO
            ver = '1.0.0'
        port = '12220'
        service = 'com.alibaba.ihome.calcifer.service.ModelService'
        method = 'queryModelsByJids'
        MODEL_SEARCH_HSF_URL = 'http://%s:%s/%s/%s/%s' % (loc, port, service, ver, method)
    return MODEL_SEARCH_HSF_URL


def get_model_info_daily(jid_list):
    INFO_HSF_LOC = 'http://eas-zhangbei-b.alibaba-inc.com/api/predict/ihome_layout_test'
    header = {'Authorization': 'NmRjZjk2N2FmNmJiZTY2YjRmNmE1YjA0MTczYzc4ZDM3Yzc1ZWY1OQ=='}
    data = {'method': 'get_furniture_model_info', 'input': jid_list}
    try:
        response_info = requests.post(url=INFO_HSF_LOC, headers=header, data=json.dumps(data), timeout=10)
        response_json = response_info.json()

        return response_json
    except Exception as e:
        print('call local json hsf error:', e)
    return {}


def model_info_hsf_get(object_list):
    global ENV_FLAG
    if ENV_FLAG == 'us':
        return {}
    # 接口获取
    global MODEL_SEARCH_HSF_URL
    url = MODEL_SEARCH_HSF_URL
    if url == '':
        url = model_search_hsf_url()
        MODEL_SEARCH_HSF_URL = url

    if url == "daily_test":
        info_json = get_model_info_daily(object_list)
        return info_json

    info_json = {}
    header = {'Http-Rpc-Type': 'JsonContent', 'Content-Type': 'application/json',
              'Http-Rpc-Timeout': '3000', 'app-name': ""}
    arg1 = ['java.util.List<java.lang.String>']
    arg2 = [object_list]
    data = {'argsTypes': arg1, 'argsObjs': arg2}
    try:
        response_info = requests.post(url=url, headers=header, data=json.dumps(data), timeout=2)
        response_json = response_info.json()
        if 'data' in response_json:
            info_json = response_json['data']['data']

        if not info_json:
            print('call json hsf error:', 'fail', object_list)
    except Exception as e:
        print('call json hsf error:', e)

    return info_json


# 数据解析：加载家具数据
def load_material_data(reload=False):
    # 家具详细信息
    global MATERIAL_DATA_DICT
    if len(MATERIAL_DATA_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'material_data_dict.json')
        MATERIAL_DATA_DICT = {}
        if os.path.exists(json_path):
            try:
                MATERIAL_DATA_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return MATERIAL_DATA_DICT


# 数据解析：加载家具数据
def load_material_feature_data(reload=False):
    # 家具详细信息
    global MATERIAL_FEATURE_DICT
    if len(MATERIAL_FEATURE_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'material_feature_dict.json')
        MATERIAL_FEATURE_DICT = {}
        if os.path.exists(json_path):
            try:
                MATERIAL_FEATURE_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return MATERIAL_FEATURE_DICT


# 数据解析：加载瓷砖一石多面
def load_ceramic_reference_data(reload=False):
    # 家具详细信息
    global CERAMIC_REFERENCE_DICT
    if len(CERAMIC_REFERENCE_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'material_ceramic_reference_dict.json')
        CERAMIC_REFERENCE_DICT = {}
        if os.path.exists(json_path):
            try:
                CERAMIC_REFERENCE_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return CERAMIC_REFERENCE_DICT


# 数据解析：加载家具数据
def load_material_cate_data(reload=False):
    # 家具详细信息
    global MATERIAL_DATA_CATE_DICT
    if len(MATERIAL_DATA_CATE_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'material_data_cate_dict.json')
        MATERIAL_DATA_CATE_DICT = {}
        if os.path.exists(json_path):
            try:
                MATERIAL_DATA_CATE_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return MATERIAL_DATA_CATE_DICT


# 数据解析：保存家具型数据
def save_material_data():
    json_path = os.path.join(os.path.dirname(__file__), 'material_data_dict.json')
    with open(json_path, "w") as f:
        json.dump(MATERIAL_DATA_DICT, f, indent=4)
        f.close()
    print('save material data success')


# 数据解析：保存家具型数据
def save_material_feature_data():
    json_path = os.path.join(os.path.dirname(__file__), 'material_feature_dict.json')
    with open(json_path, "w") as f:
        json.dump(MATERIAL_FEATURE_DICT, f, indent=4)
        f.close()
    print('save material feature success')


# 数据解析：保存瓷砖一石多面数据
def save_ceramic_reference_data():
    json_path = os.path.join(os.path.dirname(__file__), 'material_ceramic_reference_dict.json')
    with open(json_path, "w") as f:
        json.dump(CERAMIC_REFERENCE_DICT, f, indent=4)
        f.close()
    print('save material ceramic_reference data success')


# 数据解析：增加材质数据
def add_material_data(obj_id, obj_new):
    if obj_id == '':
        return
    global MATERIAL_DATA_DICT
    load_material_data()
    if obj_id in MATERIAL_DATA_DICT:
        obj_old = MATERIAL_DATA_DICT[obj_id]
        for k, v in obj_old.items():
            if k not in obj_new:
                obj_new[k] = v
    MATERIAL_DATA_DICT[obj_id] = obj_new


# 数据解析：增加材质数据
def add_material_feature(obj_id, obj_new):
    if obj_id == '':
        return
    global MATERIAL_FEATURE_DICT
    load_material_feature_data()
    if obj_id in MATERIAL_FEATURE_DICT:
        obj_old = MATERIAL_FEATURE_DICT[obj_id]
        for k, v in obj_old.items():
            if k not in obj_new:
                obj_new[k] = v
    MATERIAL_FEATURE_DICT[obj_id] = obj_new


# 数据解析：获取材质数据 深拷贝
def get_material_data_by_id(obj_id):
    global MATERIAL_DATA_DICT
    load_material_data()
    if obj_id in MATERIAL_DATA_DICT:
        return MATERIAL_DATA_DICT[obj_id].copy()
    else:
        return {}


# 获取一石多面关联数据
def get_ceramic_reference(jid):
    global CERAMIC_REFERENCE_DICT
    load_ceramic_reference_data()
    if jid in CERAMIC_REFERENCE_DICT:
        return CERAMIC_REFERENCE_DICT[jid].copy()
    else:
        url = CERAMIC_REFERENCE_MATERIAL_URL % jid
        ref_jid = []
        try:
            res = requests.get(url)
            if res.ok:
                reference = res.json()
                if 'data' in reference and 'references' in reference['data']:
                    ref_jid = []
                    for i in reference['data']['references']:
                        if 'product' in i and 'id' in i['product']:
                            ref_jid.append(i['product']['id'])
        except Exception as e:
            print(e)
            return []
        CERAMIC_REFERENCE_DICT[jid] = ref_jid
        return ref_jid


# color int值转为list
def cvt_color(in_color):
    out_color = []
    for i in range(3):
        out_color.append(in_color % 256)
        in_color = in_color // 256
    out_color.reverse()
    return out_color


# 数据检索：获取材质数据 自动下载 解析数据
def get_material_data(material_id, auto_add=True, reload=False):
    material_id = os.path.basename(material_id)
    if material_id.endswith('.obj'):
        material_id = material_id[:-4]
    elif material_id.endswith('.json'):
        material_id = material_id[:-5]
    # 已有数据
    material_all = load_material_data()
    obj_info = {}
    if material_id in material_all and not reload:
        obj_info = material_all[material_id]
        if 'textureUrl' in obj_info and 'style' in obj_info and 'size' in obj_info and 'type' in obj_info and\
                'color' in obj_info and 'category_id' in obj_info and 'rgb' in obj_info:
            pass
        else:
            print('get material data error', material_id)
    if 'textureUrl' in obj_info and 'style' in obj_info and 'size' in obj_info and 'type' in obj_info and \
            'color' in obj_info and 'category_id' in obj_info and 'rgb' in obj_info:
        return obj_info['textureUrl'], \
               obj_info['color'], \
               obj_info['size'], \
               obj_info['type'], \
               obj_info['category_id'], \
               obj_info['style'],\
               obj_info['rgb']

    # 解析数据
    obj_type, obj_style, obj_style_en, obj_size = '', '', '', [100., 100.]
    obj_type_id, obj_style_id, obj_category_id = '', '', ''
    textureUrl, color, obj_category_id = '', '', ''
    attributes = []
    # 属性
    try:
        json_info = download_hsf_get(material_id)
        if not json_info or 'item' not in json_info:
            return '', [255, 255, 255], [100, 100.], '', '', ''
        attributes = json_info['item']['attributes'] if 'attributes' in json_info['item'] else []
        tileSize = json_info['item']['tileSize'] if 'tileSize' in json_info['item'] else None
        if tileSize is not None:
            obj_size = tileSize.split(',')
            obj_size = [float(i) for i in obj_size]
        else:
            obj_size = [100., 100.]
        textureUrl = json_info['item']['textureUrl'] if 'textureUrl' in json_info['item'] else ''

        color = json_info['item']['name'] if 'name' in json_info['item'] else ''

        # 品类
        if 'categories' in json_info['item']:
            categories = json_info['item']['categories']
            if categories and len(categories) > 0:
                obj_category_id = categories[0]
    except Exception as e:
        print(e)

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
    valid_texture = True
    obj_style_en = get_furniture_style_en(obj_style)
    if color.isdecimal():
        color = cvt_color(int(color))
    else:
        if len(textureUrl) == 0:
            valid_texture = False
        color = [255, 255, 255]

    if len(textureUrl):
        try:
            r = requests.get(textureUrl)
            im = np.array(Image.open(BytesIO(r.content)))
            rgb = np.mean(im, axis=(0, 1)).tolist()
        except:
            print('get texture url failed: %s' % textureUrl)
            rgb = [255, 255, 255]
    else:
        rgb = color

    # 判断
    if obj_type == '' or not valid_texture or len(obj_category_id) == 0:
        return textureUrl, color, obj_size, obj_type, obj_category_id, obj_style_en, rgb

    # 记录
    if auto_add:
        obj_info = get_material_data_by_id(material_id)

        obj_info['textureUrl'] = textureUrl
        obj_info['color'] = color
        obj_info['size'] = obj_size
        obj_info['type'] = obj_type
        obj_info['category_id'] = obj_category_id
        obj_info['style'] = obj_style_en

        obj_info['type_id'] = obj_type_id
        obj_info['style_id'] = obj_style_id
        obj_info['rgb'] = rgb
        add_material_data(material_id, obj_info)
    # 返回
    return textureUrl, color, obj_size, obj_type, obj_category_id, obj_style_en, rgb


# 数据检索：获取材质数据 自动下载 解析数据
def get_material_feature(material_id, auto_add=True, reload=False):
    material_id = os.path.basename(material_id)
    if material_id.endswith('.obj'):
        material_id = material_id[:-4]
    elif material_id.endswith('.json'):
        material_id = material_id[:-5]
    # 已有数据
    material_all = load_material_feature_data()
    feature_info = {}

    if material_id in material_all and not reload:
        feature_info = material_all[material_id]
        return feature_info

    # 解析数据
    # 属性
    try:
        item_model_info = model_info_hsf_get([material_id])
        if material_id in item_model_info:
            feature_info = item_model_info[material_id]
    except Exception as e:
        print(e)

    # 记录
    if auto_add:
        add_material_feature(material_id, feature_info)
    # 返回
    return feature_info


def get_material_data_info(jid):
    if len(jid) == 0:
        return {}
    textureUrl, color, obj_size, obj_type, obj_category_id, obj_style_en, rgb = get_material_data(jid)
    obj_type = obj_type.split('/')
    obj_size = [i / 100. for i in obj_size]
    if obj_category_id in MATERIAL_DATA_CATE_DICT['瓷砖'] + MATERIAL_DATA_CATE_DICT['石材']:# + MATERIAL_DATA_CATE_DICT['地板单板'] + MATERIAL_DATA_CATE_DICT['地板']:
        seam = True
    else:
        seam = False

    return format_material({
        'jid': jid,
        'texture_url': textureUrl,
        'color': color,
        'colorMode': 'texture' if len(textureUrl) > 0 else 'color',
        'size': obj_size,
        'seam': seam,
        'area': 100.0, 'lift': 0,
        'contentType': obj_type,
    })


def format_material(mat):
    content_type = ''
    if 'contentType' in mat:
        content_type = mat['contentType']
    elif isinstance(mat['seam'], list):
        content_type = mat['seam']
    if mat['seam'] is True:
        tree = ['tiles', 'ceramic wall']
    else:
        tree = ['tiles', 'transfer']
    formated_mat = {
        'code': 1,
        "texture": mat['texture_url'],
        "jid": mat['jid'],
        "uv_ratio": [1. / mat['size'][0], 0, 1. / mat['size'][1], 0],
        "color": mat['color'] + [255],
        "colorMode": mat['colorMode'],
        'type': tree,
        "contentType": content_type,
        "Functional": mat['Functional'] if "Functional" in mat else "",
        "refs": [] if 'refs' not in mat else mat['refs']
    }
    return formated_mat


# 数据加载
load_material_data()
load_material_cate_data()
load_ceramic_reference_data()
load_material_feature_data()

# 功能测试
if __name__ == '__main__':
    # 批量信息
    data = get_material_data('bbea4759-36cc-49b1-aebb-beef81de3bf4', reload=True)
    data_feat = get_material_feature('df095d9f-1f39-49b9-bcb9-be6289d41db4', reload=True)
    print(data)
    data = get_material_data('ac46921b-1e8d-465b-a430-daf9cee6249e')
    print(data)
    data = get_material_data('e20746cb-ad6b-4659-9384-07dafcdb70d0')
    print(data)

    # 保存信息
    save_material_data()
    save_ceramic_reference_data()
    pass

