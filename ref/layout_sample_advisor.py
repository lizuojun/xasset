import datetime
import time

from Extract.extract_cache import get_house_data, oss_upload_json, correct_house_data, get_furniture_data
from House.house_scene_build import house_build_house
from HouseSearch.group_sample_build_info import build_customer_replace_sample_info
from HouseSearch.sample_layout.region_layout import room_sample_layout_zone
from LayoutGroup.GroupBasedHouseSearch.multi_seed_search_engine import search
from HouseSearch.group_sample_extract_info import build_customer_sample_info_from_layout
from HouseSearch.sample_refine.advisor_group_sample_refine import advisor_sample_refine, advisor_scheme_refine
from HouseSearch.sample_refine.draw_group_process import draw_zone_list_process, show_room_data
from ImportHouse.room_search import search_advice_room
from layout import view_house, view_room

from layout_sample import layout_sample_room
from layout_sample_analyze import layout_sample_camera
import copy


def _generate_group_multiseed(sample_layout, replace_list, replace_dict):
    group_items = dict()
    for jid, value in replace_dict.items():
        group_name = value['group']
        if group_name not in group_items:
            group_items[group_name] = []

        value["id"] = jid
        group_items[group_name].append(value)

    for layout_sample in sample_layout['layout_sample']:
        for group in layout_sample['group']:
            group_name = group['type']
            if group_name not in group_items:
                continue
            seed_list = group_items[group_name]
            search(seed_list, group)


def generate_group_multiseed(sample_layout, replace_list, replace_dict):
    pass


def camera_update_request(house_camera_list):
    for room in house_camera_list:
        if room["type"] not in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
            if "camera" in room and "camera_more" in room:
                camera_one = room["camera"].copy()
                if len(room["camera_more"]) > 0:
                    room["camera_more"][0]['camera'] = copy.deepcopy(camera_one)
        if "anchor_door" in room:
            room["anchor_door"] = []
        if "broad_wall" in room:
            room["broad_wall"] = []
        if "board_ceiling" in room:
            room["board_ceiling"] = []
        if "board_floor" in room:
            room["board_floor"] = []


def pipeline_build_scene_data(new_house_data, layout_info, room_id, struct_mode):
    house_mode = {
        'mesh': True,
        'customized_ceiling': True,
        'win_door': True,
        'mat': True,
        'floor_line': True,
        'bg_wall': True,
        'kitchen': False,
        'light': True,
        'debug': False,
        'white_list': False
    }

    if "no_ceiling" in struct_mode:
        house_mode['customized_ceiling'] = False

    house_scene, house_outdoor = house_build_house(new_house_data, layout_info, '',
                                                   house_mode)
    data_time = time.strftime("%Y-%m-%d") + "/"
    name_time = str(int(time.time() * 1000))

    scene_name = room_id + "_" + name_time + ".json"
    oss_upload_json("layout_scene_advisor/" + data_time + scene_name, house_scene, "ihome-alg-layout")

    scene_url = "https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com/layout_scene_advisor/" + data_time + scene_name

    return name_time, scene_url


def pipeline(room_data, table_param, house_id="", style="Swedish", content_house_id="", struct_mode=""):
    room_id = room_data["id"]
    room_type = room_data["type"]
    layout_log_0 = 'target house: %s, room: %s, layout: %d, propose: %d %s' % (house_id, room_id, 1, 1,
                                                                               datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    print(layout_log_0)

    # correct_data 去掉furniture_info
    room_data["furniture_info"] = []
    new_house_data = None
    if len(house_id) > 0:
        _, house_data = get_house_data(house_id, oss_source=True)
        for room in house_data["room"]:
            room["furniture_info"] = []

        correct_house_data(house_data)
        for room in house_data["room"]:
            if room_id == room["id"]:
                new_house_data = house_data
                break

    # 人工划分调整
    print(room_data)
    draw_zone_list_process(room_data)
    # 构建方案与布局
    # step1 预布局
    #  _, advice_layout_info, _ = search_advice_room(room_data)

    # step2 构建方案
    sample_layout, replace_list, replace_dict = build_customer_replace_sample_info(room_data, table_param,
                                                                                   None, "",
                                                                                   target_style=style,
                                                                                   house_data=new_house_data)

    # generate_group_multiseed(sample_layout, replace_dict, advice_layout_info)

    # 根据方案与划分重新规划位置
    advisor_sample_refine(sample_layout, replace_dict, room_data["region_info"])

    if "new_zone" in struct_mode:
        new_zone_pipeline = True
    else:
        new_zone_pipeline = False

    # step2 布局
    if new_zone_pipeline and "region_info" in room_data and room_data["region_info"]:
        data_info, layout_info = room_sample_layout_zone(room_data, sample_layout)
        data_info, layout_info, camera_info, wander_info = view_room(data_info, layout_info, view_mode=1)

    else:
        data_info, layout_info, _, _, _, _ = layout_sample_room(room_data, sample_layout, {"soft": []}, {}, view_mode=1)

    advisor_scheme_refine(layout_info, replace_dict)

    # 生成scene.json
    if not new_house_data:
        new_house_data = {"id": "", "room": [room_data]}
    else:
        new_house_data["layout"] = {data_info["id"]: layout_info}

    scheme_table = build_customer_sample_info_from_layout(room_data, layout_info, table_param, room_type, style)

    name_time, scene_url = pipeline_build_scene_data(new_house_data, {data_info["id"]: layout_info}, room_id,
                                                     struct_mode)

    # 相机处理
    house_camera_list = layout_sample_camera(new_house_data)

    camera_update_request(house_camera_list)

    # 风格重置
    for room in house_camera_list:
        room["style"] = style

    scene_info = {
        "house_id": "advisor_layout_diy_" + room_id + "_" + name_time,
        "scene_info": {
            "url": scene_url,
            "room": house_camera_list,
            "style": style
        },
        "ai_design_schema": scheme_table
    }
    return scene_info


def test_eas_input(inputs, zone_test=True):
    room_data = None
    scheme_table = None
    style = "Swedish"

    scheme_id = ""
    if "scheme_id" in inputs:
        scheme_id = inputs["scheme_id"]

    design_id = ""
    if "design_id" in inputs:
        design_id = inputs["design_id"]

    if "style" in inputs:
        style = inputs["style"]
        if style == "Nordic":
            style = "Swedish"
        else:
            style = "Contemporary"

    if "room_data" in inputs:
        room_data = inputs["room_data"]
        if type(room_data) == str:
            try:
                room_data = json.loads(room_data)
            except:
                room_data = {}

    if "scheme_table" in inputs:
        scheme_table = inputs["scheme_table"]
        if type(scheme_table) == str:
            try:
                scheme_table = json.loads(scheme_table)
            except:
                scheme_table = {}

    if room_data and scheme_table:
        return_data = pipeline(room_data, scheme_table, design_id, content_house_id=scheme_id, style=style, struct_mode='new_zone')
        if "scene_info" in return_data:
            if "url" in return_data["scene_info"]:
                print(return_data["scene_info"]["url"])
        return return_data

    return {}


if __name__ == '__main__':
    import json
    from LayoutTest.layout_test_case import *

    # res = test_eas_input(test_advisor_0922_07) # 电视柜
    # res = test_eas_input(test_advisor_0922_08) # 地毯
    # res = test_eas_input(test_advisor_0922_09) # 背景墙
    # res = test_eas_input(test_advisor_0922_10)  # 门套窗户颜色 地毯尺寸
    # _, house_data = get_house_data("18584217-29de-42d9-bfde-77ca6be1c6d1")
    # 929bf844-ab25-4eb6-a630-845c6a76480b
    #
    res = test_eas_input(test_layout_region_035)  #
    print(res)
