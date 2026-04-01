import json

import requests
import urllib.parse
from HouseSearch.seed.service import thread_pool_task_waiting

SOFT_SERVICE_PROPOSE_URL = 'https://tui.alibaba-inc.com/recommend'
SOFT_SERVICE_PROPOSE_APP_ID = 18328


# 推荐返回调整
def response_tran_list(response_list):
    replace_dict = {}
    for replace_idx, replace_one in enumerate(response_list):
        if replace_idx >= 20:
            break
        replace_orig_dict = replace_one['Virt2ModelMap']
        replace_size_dict = replace_one['ModelSizeMap']
        for source_id, replace_id in replace_orig_dict.items():
            if source_id not in replace_dict:
                replace_dict[source_id] = []
            if replace_id not in replace_size_dict:
                continue
            replace_size = replace_size_dict[replace_id]
            size_set = replace_size.split('&')
            if len(size_set) >= 3:
                size_x = float(size_set[0].split('=')[-1])
                size_z = float(size_set[1].split('=')[-1])
                size_y = float(size_set[2].split('=')[-1])
                if size_x <= -1 or size_y <= -1:
                    continue
                object_info = {'id': replace_id, 'size': [size_x, size_y, size_z]}
                replace_dict[source_id].append(object_info)
            else:
                continue
    return replace_dict


# 推荐返回调整
def response_tran_dict(response_dict):
    replace_dict = {}
    for target_key, target_val in response_dict.items():
        source_id = target_key
        replace_dict[source_id] = []
        for target_idx, target_one in enumerate(target_val):
            if target_idx >= 20:
                break
            if 'modelId' in target_one and 'x' in target_one and 'y' in target_one and 'z' in target_one:
                replace_id = target_one['modelId']
                size_x, size_z, size_y = target_one['x'], target_one['y'], target_one['z']
                if size_x <= -1 or size_y <= -1:
                    continue
                object_info = {'id': replace_id, 'size': [size_x, size_y, size_z]}
                replace_dict[source_id].append(object_info)
    return replace_dict


# 软装tpp接口请求
def multi_furniture_seeds_service_processing(house_room_key_input_info):
    response_dict = {}
    output_furniture_list = []

    # 并行请求tpp
    task_var_list = []
    for room_key in house_room_key_input_info:
        # 输入参数 (list, None)
        propose_list = house_room_key_input_info[room_key]
        for propose_data in propose_list:
            task_var_list.append(((output_furniture_list, room_key, propose_data), None))

    thread_pool_task_waiting(tpp_furniture_replace_service_info, task_var_list)

    # 结果处理 output_furniture_list
    for response_data in output_furniture_list:
        room_key, replace_data = response_data[0], response_data[1]
        if room_key not in response_dict:
            response_dict[room_key] = {}
        for replace_jid in replace_data:
            if 'id' in replace_data[replace_jid][0]:
                response_dict[room_key][replace_jid] = replace_data[replace_jid][0]['id']

    return response_dict


def tpp_furniture_replace_service_info(output_furniture_list, room_key, propose_data):
    request_data = {
        'appid': SOFT_SERVICE_PROPOSE_APP_ID,
        'userId': 0,
        'input_json': json.dumps(propose_data)
    }

    # 初次调用
    response_info = requests.post(SOFT_SERVICE_PROPOSE_URL, data=request_data)
    # print(request_data)
    # print(urllib.parse.urlencode(request_data))
    response_data = response_info.json()
    response_dict = {}

    response_good = False
    if 'result' in response_data and len(response_data['result']) > 0:
        if 'return_map' in response_data['result'][0]:
            response_map = response_data['result'][0]['return_map']
            response_dict = response_tran_dict(response_map)
            if len(response_dict) > 0:
                response_good = True
        elif 'returnCollectionList' in response_data['result'][0]:
            response_list = response_data['result'][0]['returnCollectionList']
            response_dict = response_tran_list(response_list)
            if len(response_dict) > 0:
                response_good = True

    if not response_good:
        response_info = requests.post(SOFT_SERVICE_PROPOSE_URL, data=request_data)
        response_data = response_info.json()
        if 'result' in response_data and len(response_data['result']) > 0:
            if 'return_map' in response_data['result'][0]:
                response_map = response_data['result'][0]['return_map']
                response_dict = response_tran_dict(response_map)
                if len(response_dict) > 0:
                    response_good = True
            elif 'returnCollectionList' in response_data['result'][0]:
                response_list = response_data['result'][0]['returnCollectionList']
                response_dict = response_tran_list(response_list)
                if len(response_dict) > 0:
                    response_good = True

    for model_data in propose_data['SlotRuleAIDesgin']:
        jid = model_data['model_id']
        size = [model_data['xPerfect'], model_data['zPerfect'], model_data['yPerfect']]

        if jid in response_dict:
            return_data = response_dict[jid]
            check_jid = []
            check_dis = []
            for d in return_data:
                if d['id'] in check_jid:
                    continue

                dis = [(d['size'][i] / 100. - size[i])**2 for i in range(3)]
                check_dis.append((sum(dis), d))
                check_jid.append(d['id'])

            if len(check_dis) > 0:
                # check_top = sorted(check_dis, key=lambda x: x[0])[0][1]
                response_dict[jid][0] = check_dis[0][1]

    output_furniture_list.append((room_key, response_dict))
