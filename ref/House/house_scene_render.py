# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-12-1
@Description: 渲染方案

"""

import os
import json
import datetime
import requests
from House.data_oss import *

# 临时目录
DATA_DIR_SERVER_SCHEME = os.path.dirname(__file__) + '/../temp/scheme'
if not os.path.exists(DATA_DIR_SERVER_SCHEME):
    os.makedirs(DATA_DIR_SERVER_SCHEME)
DATA_DIR_SERVER_RENDER = os.path.dirname(__file__) + '/../temp/render/'
if not os.path.exists(DATA_DIR_SERVER_RENDER):
    os.makedirs(DATA_DIR_SERVER_RENDER)

# OSS位置
DATA_OSS_LAYOUT = 'ihome-alg-layout'
DATA_URL_LAYOUT = 'https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com'

# 渲染服务地址
RENDER_HSF_ENV = ''
RENDER_HSF_URL = ''
RENDER_HSF_PRE = 'mtop.uncenter.render-dispatcher.pre'
RENDER_HSF_PRO = 'mtop.uncenter.render-dispatcher'
RENDER_HSF_LOC = '11.22.140.164'
RENDER_HSF_LOC_URL = 'http://eas-zhangbei-b.alibaba-inc.com/api/predict/ihome_layout_test'
# 渲染服务前缀
RENDER_TASK_KEY = ''

# 渲染视角模式
VIEW_MODE_SINGLE = 0
VIEW_MODE_SPHERE = 1


# 全屋场景上传
def house_scene_upload(scene_json, scene_name, scene_path='', scene_oss='', scene_dir=''):
    if scene_name == '' and 'uid' in scene_json:
        scene_name = scene_json['uid']
    if scene_name == '':
        scene_name = 'house'
    # 保存
    if len(scene_path) > 0 and os.path.exists(scene_path):
        json_path = scene_path
    else:
        save_dir = DATA_DIR_SERVER_SCHEME
        if len(scene_dir) > 0 and os.path.exists(scene_dir):
            save_dir = scene_dir
        json_path = os.path.join(save_dir, scene_name + '_scene.json')
        with open(json_path, "w") as f:
            json.dump(scene_json, f, indent=4)
            f.close()
    # 上传
    if len(scene_oss) <= 0:
        scene_oss = 'layout_scene'
    scene_loc = scene_oss + '/' + datetime.date.today().strftime('%Y.%m.%d') + '/' + scene_name + '.json'
    scene_url = DATA_URL_LAYOUT + '/' + scene_loc
    oss_upload_file(scene_loc, json_path, DATA_OSS_LAYOUT)
    # 返回
    print(scene_url)
    return scene_url


# 全屋场景渲染
def house_scene_render(task_id, scene_json, camera_param, outdoor_type='', view_mode=0, save_dir='', scene_url='',
                       view_width=800, view_height=800):
    if (len(scene_json) <= 0 and len(scene_url) <= 0) or len(camera_param) <= 0:
        return {}
    if len(outdoor_type) <= 0:
        outdoor_type = 'northern_snow'
    render_param = {
        'camera': camera_param,
        'viewportWidth': view_width, 'viewportHeight': view_height, 'outdoor': outdoor_type
    }
    if view_mode == VIEW_MODE_SPHERE:
        render_param['offlineRenderImageType'] = 'HDPanorama'
        render_param['viewportWidth'] = 6000
        render_param['viewportHeight'] = 1000
    if len(scene_url) <= 0:
        scene_url = house_scene_upload(scene_json, task_id, '', 'layout_scene', save_dir)

    # 地址
    global RENDER_HSF_ENV
    global RENDER_HSF_URL
    global RENDER_TASK_KEY
    url = RENDER_HSF_URL
    pre = RENDER_TASK_KEY
    if url == '':
        url = render_hsf_url()
        pre = RENDER_TASK_KEY
    render_key = pre + str(task_id)
    render_val = {}
    # 参数
    header = {"Http-Rpc-Type": "JsonContent", "Content-Type": "application/json",
              "Http-Rpc-Timeout": "30000", "app-name": ""}
    arg1 = ['java.lang.String', 'java.lang.String', 'java.lang.String',
            'com.taobao.t3d.render.client.api.RenderBizType', 'com.taobao.t3d.render.client.api.RenderEngineType']
    arg2 = [scene_url, render_key, json.dumps(render_param), "auto_select", "T3D"]
    data = {"argsTypes": arg1, "argsObjs": arg2}
    # 请求
    response_json = {}
    try:
        print('render address', RENDER_HSF_ENV)
        if 'daily' in RENDER_HSF_ENV:
            header = {'Authorization': 'NmRjZjk2N2FmNmJiZTY2YjRmNmE1YjA0MTczYzc4ZDM3Yzc1ZWY1OQ=='}
            data = {'method': 'get_render', 'input': [render_key, scene_url, camera_param, outdoor_type, view_mode]}
            response_info = requests.post(url=url, headers=header, data=json.dumps(data), timeout=10)
            response_json = response_info.json()
            if len(response_json) >= 2:
                render_key = response_json[0]
                render_val = response_json[1]
                if 'success' in render_val and render_val['success']:
                    pass
                else:
                    print('render failure:', render_val)
                    render_val = {}
            else:
                print('render failure:', response_json)
        else:
            response_info = requests.post(url=url, headers=header, data=json.dumps(data))
            response_json = json.loads(response_info.text)
            if 'success' in response_json and response_json['success']:
                if 'data' in response_json:
                    render_val = response_json['data']
                    if 'success' in render_val and render_val['success']:
                        pass
                    else:
                        print('render failure:', render_val)
                        render_val = {}
            else:
                print('render failure:', response_json)
    except Exception as e:
        print('render failure:', e)
    return render_key, render_val


# 渲染图片获取
def house_scene_render_fetch(image_list=[], image_info={}, image_dir='', split_dir=False):
    if len(image_list) <= 0 and 'image_key' in image_info:
        image_list = image_info['image_key']
    time_now = datetime.datetime.now()
    time_str = time_now.strftime('%Y-%m-%d')
    image_used, image_info = {}, {}
    if len(image_dir) <= 0:
        image_dir = DATA_DIR_SERVER_RENDER
    elif not os.path.exists(image_dir):
        image_dir = DATA_DIR_SERVER_RENDER
    # 遍历场景
    for image_key in image_list:
        if image_key in image_used:
            continue
        # 来源位置
        image_loc = 'https://ossgw.alicdn.com/t3d-render/render-result/auto_select/'
        # 目标位置
        split_key = image_key.split('_')
        if len(split_key) > 1 and split_dir:
            house_key = split_key[0]
            index_key = split_key[1]
            image_dir = os.path.join(image_dir, house_key, index_key)
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        # 目标后缀
        suffix_set = []
        # 获取图片
        for image_idx in range(0, 1):
            # 判断
            image_src = image_loc + time_str + '/%s/%s.front.jpg' % (image_key, image_key)
            try:
                r = requests.get(image_src, timeout=1)
                r.raise_for_status()
                break
            except Exception as e:
                pass
            # 单图
            image_src = image_loc + time_str + '/%s/%s.jpg' % (image_key, image_key)
            image_des = image_dir + '/%s.jpg' % image_key
            try:
                r = requests.get(image_src, timeout=1)
                r.raise_for_status()
                with open(image_des, 'wb') as f:
                    f.write(r.content)
                image_used[image_key] = 1
                image_info[image_key] = {
                    'url': image_src,
                    'loc': image_des
                }
                print('fetch image good:', image_key, 'single')
            except Exception as e:
                pass
        # 获取全景
        suffix_set = ['front', 'back', 'left', 'right', 'top', 'bottom']
        for suffix_idx, suffix_one in enumerate(suffix_set):
            if suffix_idx <= 0 and image_key in image_used:
                break
            # 单图
            image_src = image_loc + time_str + '/%s/%s.%s.jpg' % (image_key, image_key, suffix_one)
            image_des = image_dir + '/%s.%s.jpg' % (image_key, suffix_one)
            try:
                r = requests.get(image_src, timeout=1)
                r.raise_for_status()
                with open(image_des, 'wb') as f:
                    f.write(r.content)
                if suffix_idx <= 0:
                    image_used[image_key] = 1
                    image_info[image_key] = {
                        'url': [image_src],
                        'loc': [image_des]
                    }
                    print('fetch image good:', image_key, 'sphere')
                else:
                    image_info[image_key]['url'].append(image_src)
                    image_info[image_key]['loc'].append(image_des)
            except Exception as e:
                pass
        # 获取失败
        if image_key not in image_used:
            print('fetch image fail:', image_key)
    # 返回图片
    return image_info


# 渲染服务地址
def render_hsf_url():
    global RENDER_HSF_ENV
    global RENDER_HSF_URL
    global RENDER_TASK_KEY
    if RENDER_HSF_URL == '':
        env, loc, ver = '', '', ''
        try:
            r = requests.get('http://jmenv.tbsite.net:8080/env', timeout=1)
            r.raise_for_status()
            env = r.text.strip()
        except Exception as e:
            print('get environment error:', e)
        if 'daily' in env:
            loc = RENDER_HSF_LOC
            ver = '1.1.0'
            RENDER_TASK_KEY = ''
        elif 'pre' in env:
            loc = RENDER_HSF_PRE
            ver = '1.1.0'
            RENDER_TASK_KEY = ''
        else:
            loc = RENDER_HSF_PRO
            ver = '1.1.0'
            RENDER_TASK_KEY = ''
        port = '12220'
        service = 'com.taobao.t3d.render.client.api.CloudRenderService'
        method = 'requestRender'
        RENDER_HSF_ENV = env
        RENDER_HSF_URL = 'http://%s:%s/%s/%s/%s' % (loc, port, service, ver, method)
        if 'daily' in env:
            RENDER_HSF_URL = RENDER_HSF_LOC_URL
    return RENDER_HSF_URL


# 功能测试
if __name__ == '__main__':
    # 列表
    image_list = ['4346fd79-f172-457f-a782-7cb74b5af017_LivingDiningRoom-3095_M8uJildrU9_162519164128127', '4346fd79-f172-457f-a782-7cb74b5af017_LivingDiningRoom-3095_original_fQtaLVl2dv_162519164138141']

    # 获取
    image_info = house_scene_render_fetch(image_list)
    pass
