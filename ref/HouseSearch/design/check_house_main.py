import requests
import os
import uuid

from House.house_save import house_save, SAVE_MODE_FRAME, oss_download_file
from HouseSearch.design.design_house import HouseInfoConvert
from HouseSearch.design.design_house_v2 import HouseInfoConvertV2
from HouseSearch.design.inner_walls_refine import room_inner_walls_refine
from HouseSearch.util import ROOM_CVT_TABLE, get_refine_rooms, update_offset, combine_living_rooms, compute_poly_area
import traceback


def change_one_room_type(origin_room_type):
    return origin_room_type


def cvt_room_type_str(room_data):
    origin_room_type = room_data['id'].split('-')[0]
    change_room_type = change_one_room_type(origin_room_type)

    room_data['id'] = '-'.join(([change_room_type] + room_data['id'].split('-')[1:]))
    room_data['type'] = change_room_type
    for door in room_data['door_info']:
        if len(door['to']) > 0:
            origin_room_type, element_id = door['to'].split('-')
            change_room_type = change_one_room_type(origin_room_type)
            door['to'] = change_room_type + '-' + element_id

    for hole in room_data['hole_info']:
        if len(hole['to']) > 0:
            origin_room_type, element_id = hole['to'].split('-')
            change_room_type = change_one_room_type(origin_room_type)
            hole['to'] = change_room_type + '-' + element_id
    for win in room_data['window_info']:
        if len(win['to']) > 0:
            origin_room_type, element_id = win['to'].split('-')
            change_room_type = change_one_room_type(origin_room_type)
            win['to'] = change_room_type + '-' + element_id
    for win in room_data['baywindow_info']:
        if len(win['to']) > 0:
            origin_room_type, element_id = win['to'].split('-')
            change_room_type = change_one_room_type(origin_room_type)
            win['to'] = change_room_type + '-' + element_id


def post_processing_house_data(house_json_data, design_version=23):
    # if design_version >= 23:
    #     return room_inner_walls_refine(house_json_data)

    # 合并客餐厅
    # combine_living_rooms(house_json_data)

    # 点refine 房间refine
    get_refine_rooms(house_json_data)

    for room_idx in range(len(house_json_data['room'])):
        house_json_data['room'][room_idx] = update_offset(house_json_data['room'][room_idx], offset=0.06)

    # 计算面积
    for room_idx in range(len(house_json_data['room'])-1, -1, -1):
        house_json_data['room'][room_idx]['area'] = compute_poly_area(house_json_data['room'][room_idx]['floor'])
        if house_json_data['room'][room_idx]['area'] < 0.1:
            house_json_data['room'].pop(room_idx)

    return house_json_data


def check_origin_design_house_data(design_id, design_json=None, mid_point=False, sample_data=True):
    design_version = 23
    try:
        if design_json:

            try:
                design_version = int(design_json['meta']['version'].split('.')[-1])
            except Exception as e:
                print("get design version fail", e)
                design_version = 21

            if design_version >= 23:
                house_info = HouseInfoConvertV2(design_json, design_id)
                house_info.build(sample_data, sample_data)
            else:
                house_info = HouseInfoConvert(design_json, design_id)
                house_info.build(sample_data, sample_data)
            house_json_data = house_info.house_info
        else:
            house_json_data = {}

    except Exception as e:
        print(traceback.print_exc())
        print("design convert house_data error!", e)
        return {}

    if mid_point:
        return house_json_data

    # 中线处理过程
    return post_processing_house_data(house_json_data, design_version)


# 数据解析
def house_design_parse(design_url):
    # 方案信息
    house_data_info = {}
    # 原始方案
    house_design_json = {}
    try:
        if os.path.exists(design_url) and design_url.endswith('.json'):
            house_design_json = json.load(open(design_url, 'r'))
        if len(house_design_json) <= 0:
            response_info = requests.get(design_url, timeout=3)
            house_design_json = response_info.json()
    except requests.exceptions.RequestException:
        print('call design json error:', 'time out')
    except Exception as e:
        print('call design json error:', e)
    # 解析方案 TODO:
    house_data_info = check_origin_design_house_data(design_id="", design_json=house_design_json)
    # 返回信息
    return house_data_info


if __name__ == '__main__':
    from HouseSearch.util import get_http_data_from_url
    from LayoutDecoration.house_info import HouseData
    import json

    from Demo.test_local import get_design_json_daily

    # design_url = get_design_json_daily("7a9571e6-0b7d-41bb-a585-6b4319bf6385")
    # "2c473676-d32e-489d-923e-c4b7bba81127", "https://jr-prod-cms-assets.oss-cn-beijing.aliyuncs.com/Asset/f4a3178c-8af0-4f9a-a139-4e890b292046/v1607953930.json"

    design_url = "https://jr-prod-cms-assets.oss-cn-beijing.aliyuncs.com/design/2021-09-15/json/30756925-efc7-4021-9721-439ff6a1d6c5.json"

    house_design_json = get_http_data_from_url(design_url)
    house_data_info = check_origin_design_house_data(design_id="", design_json=house_design_json)

    print(house_data_info)
