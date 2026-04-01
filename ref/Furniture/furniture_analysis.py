# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2020-06-09
@Description: 家具分析算法

"""

import os
import json
import math
import requests
import datetime

# 临时目录
DATA_DIR_FURNITURE = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(DATA_DIR_FURNITURE):
    os.makedirs(DATA_DIR_FURNITURE)

# 几何分析服务
SHAPE_ANALYSIS_UAT = 'http://calcifer-api.alibaba-inc.com/api/v1/models/'
SHAPE_ANALYSIS_PRE = 'http://pre-calcifer-api.alibaba-inc.com.vipserver/api/v1/models/'
SHAPE_ANALYSIS_PRO = 'http://calcifer-api.alibaba-inc.com.vipserver/api/v1/models/'
SHAPE_ANALYSIS_URL = 'http://calcifer-api.alibaba-inc.com/api/v1/models/'

# 布艺仿真服务
CLOTH_SIMULATE_PRE = 'http://acs.wapa.taobao.com/gw/mtop.taobao.ihome.cloth.sim/1.0/'
CLOTH_SIMULATE_PRO = 'http://acs.wapa.taobao.com/gw/mtop.taobao.ihome.cloth.sim/1.0/'


# 环境更新
def furniture_analysis_url():
    global SHAPE_ANALYSIS_URL
    # 环境
    env, loc, ver = '', SHAPE_ANALYSIS_URL, ''
    try:
        r = requests.get('http://jmenv.tbsite.net:8080/env', timeout=1)
        r.raise_for_status()
        env = r.text.strip()
    except Exception as e:
        print('get environment error:', e)
    if 'daily' in env:
        loc = SHAPE_ANALYSIS_UAT
        ver = '1.0.0.daily'
    elif 'pre' in env:
        loc = SHAPE_ANALYSIS_PRE
        ver = '1.0.0.pre'
    else:
        loc = SHAPE_ANALYSIS_PRO
        ver = '1.0.0'
    SHAPE_ANALYSIS_URL = loc
    return SHAPE_ANALYSIS_URL


# 几何分析
def furniture_analysis_shape(object_id, object_type='', object_size=[], des_dir=''):
    global SHAPE_ANALYSIS_URL
    url = SHAPE_ANALYSIS_URL
    if url == '':
        url = furniture_analysis_url()

    # 地址
    src_key = 'support_region_compact_url'
    src_url = url + '/%s/algorithm?keys=%s' % (object_id, src_key)
    # 调用
    response_json = {}
    try:
        # print(object_id, 'call region url ', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S.%f'))
        response_info = requests.get(src_url, timeout=1)
        response_json = response_info.json()
    except requests.exceptions.RequestException:
        print('call region url error:', 'time out')
    except Exception as e:
        print('call region url error:', e)
    if des_dir == '':
        des_dir = os.path.join(DATA_DIR_FURNITURE, 'region')
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    object_key, region_url, region_val = object_id, '', {}
    if object_key in response_json:
        object_val = response_json[object_key]
        if src_key in object_val:
            region_url = 'http://ossgw.alicdn.com/homeai/' + object_val[src_key]
            region_path = os.path.join(des_dir, object_id + '_region.json')
            try:
                # print(object_id, 'call region data ', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S.%f'))
                response_info = requests.get(region_url, timeout=1)
                response_json = response_info.json()
                region_val = response_json
                # print(object_id, 'call region done ', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S.%f'))
            except requests.exceptions.RequestException:
                print('call region data error:', 'time out')
            except Exception as e:
                print('call region data error:', e)
    region_dict = {}
    if 'support_areas' in region_val:
        support_areas = region_val['support_areas']
        for support_info in support_areas:
            support_poly, support_lift, support_high = [], 0, 0
            if 'poly' in support_info:
                support_poly = support_info['poly']
            else:
                continue
            if len(support_poly) < 6:
                continue
            if 'ground_h' in support_info:
                support_lift = support_info['ground_h']
            else:
                continue
            if 'valid_h' in support_info:
                support_high = support_info['valid_h']
                if support_high < 0:
                    support_high = 50
            else:
                continue
            if len(object_size) >= 3 and support_lift > 150 and support_lift > object_size[1] - 10:
                continue
            x_min, z_min, x_max, z_max = support_poly[0], support_poly[1], support_poly[0], support_poly[1]
            support_lens = int(len(support_poly) / 2)
            for j in range(support_lens):
                x1 = support_poly[(2 * j + 0)]
                z1 = support_poly[(2 * j + 1)]
                x_min = min(x_min, x1)
                z_min = min(z_min, z1)
                x_max = max(x_max, x1)
                z_max = max(z_max, z1)
            support_lift_int = math.ceil(support_lift)
            if min(x_max - x_min, z_max - z_min) > 5 and support_high > 5:
                region_one = [x_min, support_lift, z_min, x_max, support_lift, z_max, support_high]
                if support_lift_int not in region_dict:
                    region_dict[support_lift_int] = []
                region_dict[support_lift_int].append(region_one)
    # print(object_id, 'call region done ', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S.%f'))
    return region_dict


# 布艺仿真
def furniture_analysis_cloth(object_list, cloth_one):
    pass


furniture_analysis_url()


# 功能测试
if __name__ == '__main__':
    furniture_id = '95f863cb-1353-45c5-a623-ca93b8f29a5a'
    furniture_analysis_shape(furniture_id)
    pass
