# -*- coding: utf-8 -*-
import json
import os

import requests

from HouseSearch.data_oss import oss_upload_file, oss_exist_file, oss_download_file, oss_get_json

DATA_DIR_MODEL_INFO = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(DATA_DIR_MODEL_INFO):
    os.makedirs(DATA_DIR_MODEL_INFO)

MODEL_SERVICE_HSF_IP_PRO = "calcifer-api.alibaba-inc.com.vipserver"
MODEL_SERVICE_HSF_IP_PRE = "pre-calcifer-api.alibaba-inc.com.vipserver"
MODEL_SERVICE_HSF_IP_LOC = "11.167.121.119"

MODEL_SEARCH_HSF_URL = ''

FURNITURE_STATUS_DICT = {}

DATA_OSS_MODEL = 'model'
DATA_OSS_DATABASE = 'ihome-alg-sample-data'


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


def model_info_hsf_get(object_list):
    return_info = {}
    local_file_num = 0
    for jid in object_list:
        model_file = jid + '.json'
        model_path = os.path.join(DATA_DIR_MODEL_INFO, model_file)
        if os.path.exists(model_path):
            house_data = json.load(open(model_path, 'r'))
            return_info[jid] = house_data
            local_file_num += 1
            continue

        if oss_exist_file(DATA_OSS_MODEL + '/' + model_file, DATA_OSS_DATABASE):
            try:
                oss_download_file(DATA_OSS_MODEL + '/' + model_file, model_path, DATA_OSS_DATABASE)
                # 本地
                if os.path.exists(model_path):
                    house_data = json.load(open(model_path, 'r'))
                    return_info[jid] = house_data
                    local_file_num += 1
            except:
                print("load local model info fail!, jid %s" % jid)
                continue
    if local_file_num == len(object_list):
        return return_info

    # 接口获取
    global MODEL_SEARCH_HSF_URL
    url = MODEL_SEARCH_HSF_URL
    if url == '':
        url = model_search_hsf_url()
        MODEL_SEARCH_HSF_URL = url

    if url == "daily_test":
        info_json = get_model_info_daily(object_list)
        for jid in info_json:
            model_file = jid + '.json'
            model_path = os.path.join(DATA_DIR_MODEL_INFO, model_file)
            # # 本地
            with open(model_path, "w") as f:
                json.dump(info_json[jid], f, indent=4)
                f.close()
            # 上传
            if os.path.exists(model_path):
                oss_upload_file(DATA_OSS_MODEL + '/' + model_file, model_path, DATA_OSS_DATABASE)
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
            for jid in info_json:
                model_file = jid + '.json'
                model_path = os.path.join(DATA_DIR_MODEL_INFO, model_file)
                # 本地
                with open(model_path, "w") as f:
                    json.dump(info_json[jid], f, indent=4)
                    f.close()

                # 上传
                if os.path.exists(model_path):
                    oss_upload_file(DATA_OSS_MODEL + '/' + model_file, model_path, DATA_OSS_DATABASE)

        if not info_json:
            print('call json hsf error:', 'fail', object_list)
    except Exception as e:
        print('call json hsf error:', e)

    return info_json


# 加载模型效性状态数据
def load_furniture_status_data(reload=False):
    global FURNITURE_STATUS_DICT
    if len(FURNITURE_STATUS_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_status_dict.json')
        FURNITURE_STATUS_DICT = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_STATUS_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    # 返回信息
    return FURNITURE_STATUS_DICT


# 保存模型效性状态数据
def save_furniture_status_data():
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_status_dict.json')
    with open(json_path, "w") as f:
        json.dump(FURNITURE_STATUS_DICT, f, indent=4)
        f.close()
    print('save furniture status data success')


def add_furniture_valid(jid, valid):
    if jid == '':
        return
    global FURNITURE_STATUS_DICT
    load_furniture_status_data()
    FURNITURE_STATUS_DICT[jid] = valid


def get_model_valid(jid):
    global FURNITURE_STATUS_DICT
    load_furniture_status_data()

    # 0代表有效、1代表无效、如果没查到也按0处理了
    valid = 0
    if jid in FURNITURE_STATUS_DICT:
        valid = FURNITURE_STATUS_DICT[jid]
    else:
        info = model_info_hsf_get([jid])
        if jid in info:
            if 'auditStatus' in info[jid]:
                if info[jid]['auditStatus'] != 0:
                    # 模型库中 auditStatus == 0 代表有效
                    valid = 1
                add_furniture_valid(jid, valid)

    return valid


if __name__ == '__main__':
    import time

    all_jids = open("all_jids.txt", 'r').read().split()
    all_good_jids = []
    idx = 0
    # for jid in all_jids:
    #     print(idx)
    #     check = get_model_valid(jid)
    #     if check == 0:
    #         all_good_jids.append(jid)
    #         idx += 1

    group_list = json.load(open("../Furniture/furniture_group_def.json", "r"))["Group"]
    for name in group_list:
        for model in group_list[name]['obj_list']:
            if model['id'] in all_jids:
                continue
            else:
                all_jids.append(model['id'])

    with open("all_good_jids.txt", 'w') as f:
        for i in all_jids:
            f.write(i+'\n')

    save_furniture_status_data()

    # oss_upload_file("furniture_status_dict.json", "./furniture_status_dict.json", "ihome-alg-sample-data")
