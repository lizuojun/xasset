import json
import time
import urllib.parse

import requests
import copy
from HouseSearch.main_seed import get_room_main_furniture_seeds, check_need_hard_type
from HouseSearch.util import gen_random_str
from ImportHouse.room_search import get_room_sample, get_room_data

HARD_SERVICE_PROPOSE_URL = 'https://tui.alibaba-inc.com/recommend'
HARD_SERVICE_PROPOSE_APP_ID = 25371


# 请求硬装搭配生成v1.0 https://yuque.antfin-inc.com/docs/share/84e3c570-fbd8-47bd-a04a-39cb9fed8219?#
def get_material_seeds_service_room_data(house_data, sample_info, furniture_seeds_info, sample_result_room_idx=0):
    target_house_id = house_data['id']

    room_main_furniture = get_room_main_furniture_seeds(furniture_seeds_info)
    house_room_key_list = []

    source_room_id_list = []
    for source_room_id in sample_info['info']['sample']:
        if source_room_id in furniture_seeds_info:
            house_key = sample_info['info']['sample'][source_room_id]
            house_id, room_id_key = house_key.split('_')
            room_type, room_id = room_id_key.split('-')

            one_request_info = {
                "designId": house_id,
                "roomId": room_id,
                "roomType": room_type,
                "mainFurn": ""
            }

            if source_room_id in room_main_furniture and room_main_furniture[source_room_id]:
                one_request_info["mainFurn"] = room_main_furniture[source_room_id]['id']
            else:
                continue

            source_room_id_list.append(source_room_id)
            house_room_key_list.append(one_request_info)

    if len(house_room_key_list) == 0:
        return {}

    request_id = target_house_id + "_" + str(int(time.time())) + "_" + gen_random_str(10)
    request_info = {
        "userId": 0,
        "requestId": request_id,
        "roomList": house_room_key_list
    }
    response_dict = {}
    for request_retry_idx in range(3):
        request_data = {
            'appid': HARD_SERVICE_PROPOSE_APP_ID,
            'userId': 0,
            'inputJson': json.dumps(request_info)
        }
        # 初次调用

        response_info = requests.post(HARD_SERVICE_PROPOSE_URL, data=request_data)
        response_data = response_info.json()

        if 'result' in response_data and response_data['result'][0]['resultList']:
            for source_idx, return_result in enumerate(response_data['result'][0]['resultList']):
                source_room_id = source_room_id_list[source_idx]
                if len(return_result['hardRoomList']) == 0:
                    continue
                all_rooms_length = len(return_result['hardRoomList'])
                response_dict[source_room_id] = return_result['hardRoomList'][sample_result_room_idx % all_rooms_length]
            break

    # 更新
    hard_target = {}
    return_type_hard = {}
    if response_dict:
        for source_room_id in response_dict:
            house_id = response_dict[source_room_id]['designId']
            room_id = response_dict[source_room_id]['roomType'] + "-" + response_dict[source_room_id]['roomId']

            room_para, room_layout, room_group = get_room_sample(house_id, room_id)
            if room_layout:
                hard_target[source_room_id] = (house_id, room_id)
                if response_dict[source_room_id]['roomType'] in ["LivingDiningRoom", "LivingRoom", "MasterBedroom",
                                                                 "Bedroom", "SecondBedroom"]:
                    return_type_hard[response_dict[source_room_id]['roomType']] = copy.deepcopy(
                        room_layout['layout_scheme'][0]['material'])
                    return_type_hard[response_dict[source_room_id]['roomType']][
                        "hard_source_key"] = house_id + "_" + room_id

    if 'check_hard_target' not in house_data:
        house_data['check_hard_target'] = []

    house_data['check_hard_target'].append(hard_target)

    return return_type_hard


# 直接根据主家具请求固定类型硬装
def update_main_furniture_seed_hard_replace(request_id, main_object_id, room_type, target_hard_type_info):
    need_replace_info = {}
    for item in target_hard_type_info:
        if 'contentType' in target_hard_type_info[item]:
            now_content = target_hard_type_info[item]['contentType']
            if "build element" in now_content:
                continue
            need_replace_info[now_content] = {"origin_id": target_hard_type_info[item]["seekId"], "replace_id": ""}

    house_room_key_list = []
    request_info = {
        "userId": 0,
        "type": "i2r",
        "requestId": request_id,
        "roomList": house_room_key_list
    }
    one_request_info = {"designId": "", "roomId": "", "roomType": room_type,
                        "mainFurn": main_object_id}
    house_room_key_list.append(one_request_info)
    for request_retry_idx in range(3):
        request_data = {
            'appid': HARD_SERVICE_PROPOSE_APP_ID,
            'userId': 0,
            'inputJson': json.dumps(request_info)
        }
        # 初次调用

        response_info = requests.post(HARD_SERVICE_PROPOSE_URL, data=request_data)
        # print(HARD_SERVICE_PROPOSE_URL + '?' + urllib.parse.urlencode(request_data))
        response_data = response_info.json()

        if 'result' in response_data and response_data['result'][0]['resultList']:
            for source_idx, return_result in enumerate(response_data['result'][0]['resultList']):

                if len(return_result['hardRoomList']) == 0:
                    continue

                # 找到第一个对应相关材质类型返回
                for hard_room_key_info in return_result['hardRoomList']:
                    house_id = hard_room_key_info['designId']
                    room_id = hard_room_key_info['roomType'] + "-" + hard_room_key_info['roomId']

                    room_para, room_data = get_room_data(house_id, room_id)
                    if room_data:
                        check_need_hard_type(room_data['material_info'], need_replace_info)

                        need_replace_num = 0
                        for content in need_replace_info:
                            if len(need_replace_info[content]['replace_id']) == 0:
                                need_replace_num += 1
                        if need_replace_num == 0:
                            for item in target_hard_type_info:
                                content_type = target_hard_type_info[item]['contentType']
                                if content_type in need_replace_info and len(
                                        need_replace_info[content_type]['replace_id']) > 0:
                                    target_hard_type_info[item]['replaceId'] = need_replace_info[content_type][
                                        'replace_id']

                            return

                    else:
                        continue

            break
    return


# 根据替换家具请求相似
def update_hard_sim_seed_replace(request_id, target_hard_type_info, poolid=None):
    origin_seek_replace_id = {}
    for item in target_hard_type_info:
        if 'contentType' in target_hard_type_info[item]:
            now_content = target_hard_type_info[item]['contentType']
            if "build element" in now_content:
                continue
            if target_hard_type_info[item]["seekId"] != target_hard_type_info[item]["replaceId"]:
                continue

            origin_seek_replace_id[target_hard_type_info[item]["seekId"]] = target_hard_type_info[item]["seekId"]
    if not origin_seek_replace_id:
        return

    house_room_key_list = []
    if type(poolid) is str and len(poolid) > 0:
        request_info = {
            "userId": 0,
            "type": "similar",
            "poolId": poolid,
            "requestId": request_id,
            "roomList": house_room_key_list
        }
    else:
        request_info = {
            "userId": 0,
            "type": "similar",
            "requestId": request_id,
            "roomList": house_room_key_list
        }

    for jid in origin_seek_replace_id:
        one_request_info = {"mainFurn": jid}
        house_room_key_list.append(one_request_info)

    # 请求并处理结果
    for request_retry_idx in range(3):
        request_data = {
            'appid': HARD_SERVICE_PROPOSE_APP_ID,
            'userId': 0,
            'inputJson': json.dumps(request_info)
        }
        # 初次调用

        response_info = requests.post(HARD_SERVICE_PROPOSE_URL, data=request_data)
        # print(HARD_SERVICE_PROPOSE_URL + '?' + urllib.parse.urlencode(request_data))
        response_data = response_info.json()

        if 'result' in response_data and response_data['result'][0]['resultList']:
            for source_idx, return_result in enumerate(response_data['result'][0]['resultList']):
                if len(return_result['simiModelList']) == 0:
                    continue
                seek_id = return_result["mainFurn"]
                replace_id = ""
                # 找到第一个对应相关材质类型返回
                if len(return_result['simiModelList']) > 0:
                    replace_id = return_result['simiModelList'][0]["modelId"]
                if seek_id in origin_seek_replace_id and len(replace_id) > 0:
                    origin_seek_replace_id[seek_id] = replace_id
            break

    for item in target_hard_type_info:
        seek_id = target_hard_type_info[item]["seekId"]
        if seek_id in origin_seek_replace_id:
            target_hard_type_info[item]["replaceId"] = origin_seek_replace_id[seek_id]

    # 检查装企套餐包id是否都替换成功, 否则走公库替换
    if type(poolid) is str and len(poolid) > 0:
        print("second public replace hard items")
        update_hard_sim_seed_replace(request_id+"_pub_replace_2nd", target_hard_type_info, None)
    print(target_hard_type_info)


def get_material_seeds_service_with_hard_type(main_object_id, room_type, target_hard_type_info, poolid=None):
    request_id = "ihome_split_transfer" + str(int(time.time())) + "_" + gen_random_str(10)

    # if room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom", "MasterBedroom", "Bedroom", "SecondBedroom",
    #                  "KidsRoom", "ElderlyRoom"]:
    #     update_main_furniture_seed_hard_replace(request_id, main_object_id, room_type, target_hard_type_info)
    # else:
    update_hard_sim_seed_replace(request_id, target_hard_type_info, poolid=poolid)


def update_base_soft_groups(layout_scheme, source_key):
    need_type = ["Wall", "Ceiling", "Floor", "Door", "Window", "Background", "Customize"]
    house_id, room_id = source_key.split('_')
    room_para, room_layout, room_group = get_room_sample(house_id, room_id)
    # layout_scheme[0] = room_layout["layout_scheme"][0]
    if room_group:
        layout_scheme[0]["source_room"] = room_id
        layout_scheme[0]["source_house"] = house_id
        for i in range(len(layout_scheme[0]["group"])-1, -1, -1):
            group = layout_scheme[0]["group"][i]
            if group['type'] in need_type:
                layout_scheme[0]["group"].pop(i)

        layout_scheme[0]["group"] += room_group["group_decorative"]
