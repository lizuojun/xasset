# 测试本地服务
import json
import time

import requests


INFO_HSF_LOC = 'http://eas-zhangbei-b.alibaba-inc.com/api/predict/ihome_layout_test'
INFO_HSF_HOUSE_DATA_LOC = 'http://eas-zhangbei-b.alibaba-inc.com/api/predict/ihome_house_data'


def get_design_json_daily(design_id):
    header = {'Authorization': 'NmRjZjk2N2FmNmJiZTY2YjRmNmE1YjA0MTczYzc4ZDM3Yzc1ZWY1OQ=='}
    data = {'method': 'get_scene_design_json', 'input': design_id}
    try:
        response_info = requests.post(url=INFO_HSF_LOC, headers=header, data=json.dumps(data), timeout=10)
        response_json = response_info.json()

        return response_json
    except Exception as e:
        print('call local json hsf error:', e)
    return {}


def get_scene_json_daily(design_id):
    header = {'Authorization': 'NmRjZjk2N2FmNmJiZTY2YjRmNmE1YjA0MTczYzc4ZDM3Yzc1ZWY1OQ=='}
    data = {'method': 'get_scene_json', 'input': design_id}
    try:
        response_info = requests.post(url=INFO_HSF_LOC, headers=header, data=json.dumps(data), timeout=10)
        response_json = response_info.json()
        return response_json["data"]
    except Exception as e:
        print('call local json hsf error:', e)
    return {}


def request_url_data(url):
    retry_time = 20
    retry_index = 0
    while True:
        try:
            ret = requests.get(url)
            if ret.ok:
                return ret.json()
            else:
                time.sleep(1)
                retry_index += 1
                if retry_index > retry_time:
                    break
        except Exception as e:
            print(e)
            break
    return {}


def get_house_data_daily(design_url):
    header = {'Authorization': 'ZGY1NjFkZTA0Y2NiYzdlMTMyYjQ3NzZmYzM3NmVmZDI4NDAyMDE0YQ=='}
    data = design_url
    try:
        response_info = requests.post(url=INFO_HSF_HOUSE_DATA_LOC, headers=header, data=data, timeout=10)
        response_json = response_info.json()
        url = response_json["url"]

        return request_url_data(url)
    except Exception as e:
        print('call local json hsf error:', e)
    return {}


if __name__ == '__main__':
    # 根据design id 获取design json 和 scene json 仅本地测试使用 尽量避免高qps
    design_id = 'f4b37572-f2b1-4500-8901-18945e1d5adc'
    print(get_design_json_daily(design_id))
    print(get_scene_json_daily(design_id))
