import time

import json
import copy
import requests

from Extract.extract_cache import get_house_data, house_scene_parse, get_refine_rooms, HouseData, oss_upload_json
from HouseSearch.group_sample_extract_info import build_customer_sample_info_from_layout
from layout import view_house
from layout_sample_analyze import layout_sample_camera


def camera_update_request(house_camera_list):
    for room in house_camera_list:
        if room["type"] not in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
            if "camera" in room and "camera_more" in room:
                camera_one = room["camera"].copy()
                if len(room["camera_more"]) > 0:
                    room["camera_more"][0]['camera'] = copy.deepcopy(camera_one)


def scene_diff_update(house_scene_json, diff_data):
    diff_map = {}
    for diff_item in diff_data:
        ins = diff_item["instanceId"]
        if ins not in diff_map:
            diff_map[ins] = diff_item

    if "scene" not in house_scene_json or "room" not in house_scene_json["scene"]:
        return house_scene_json

    scene_room_list = house_scene_json["scene"]["room"]
    for scene_room_data in scene_room_list:
        for instance_idx in range(len(scene_room_data["children"]) - 1, -1, -1):
            instance_id = scene_room_data["children"][instance_idx]["instanceid"]
            if instance_id in diff_map:
                now_item = diff_map[instance_id]
                if now_item["operation"] == "update_instance":
                    scene_room_data["children"][instance_idx]["pos"] = now_item["pos"].copy()
                    scene_room_data["children"][instance_idx]["rot"] = now_item["rot"].copy()
                    scene_room_data["children"][instance_idx]["scale"] = now_item["scale"].copy()
                elif now_item["operation"] == "remove_instance":
                    scene_room_data["children"].pop(instance_idx)
    return house_scene_json


def check_scene_diff_house_data(house_scene_json, diff_data):
    # if diff_data:
    #     house_scene_json = scene_diff_update(house_scene_json, diff_data)
    house_data = HouseData()
    house_data.load_json(house_scene_json, load_mesh=False)

    house_parametric_mesh_model = {}
    room_list = []
    if 'room' in house_data.house_info:
        room_list = house_data.house_info['room']
    for room in room_list:
        if room['id'] in house_parametric_mesh_model:
            if 'decorate_info' not in room['material_info']:
                room['decorate_info'] = []
            room['decorate_info'] += house_parametric_mesh_model[room['id']]

    house_data_info = {'id': "", 'room': room_list}

    if 'scene' in house_data.house_info:
        house_data_info['scene'] = house_data.house_info['scene']
    # 返回信息
    house_data_info = get_refine_rooms(house_data_info)

    return house_scene_json, house_data_info


def get_scene_data(url):
    try:
        response_info = requests.get(url, timeout=5)
        house_scene_json = response_info.json()
    except Exception as e:
        print(e)
        print("get scene_url data time error! %s" % url)
        return {}

    return house_scene_json


def scene_data_refine(url, diff_data, style, room_data):
    if room_data:
        room_id = room_data["id"]
    else:
        room_id = ""

    house_id = "scene_refined_%s" % room_id

    house_scene_json = get_scene_data(url)

    house_scene_data, house_data = check_scene_diff_house_data(house_scene_json, diff_data)

    house_info, layout_info, scene_info, route_info = view_house(house_data, view_mode=1)

    house_data["layout"] = layout_info

    house_camera_list = layout_sample_camera(house_data)

    room_layout = None
    for room_target_id in layout_info:
        if room_target_id == room_id:
            room_layout = layout_info[room_target_id]

    if not room_layout:
        max_groups = []
        for room_target_id in layout_info:
            if len(layout_info[room_target_id]["layout_scheme"]) > 0:
                num_g = len(layout_info[room_target_id]["layout_scheme"][0]["group"])
                max_groups.append((num_g, room_target_id))
        if len(max_groups) > 0:
            room_target_id = sorted(max_groups, key=lambda x: x[0], reverse=True)[0][1]
            room_layout = layout_info[room_target_id]
            room_id = room_target_id

    # 更新相机
    target_house_camera_list = []
    for room_camera in house_camera_list:
        if room_camera['id'] == room_id:
            target_house_camera_list.append(room_camera)

    camera_update_request(target_house_camera_list)

    if "type" in room_data:
        room_type = room_data["type"]
    elif room_id:
        if room_id in layout_info:
            room_layout = layout_info[room_id]
            room_type = room_layout["room_type"]
        else:
            room_type = ""
    else:
        room_type = ""

    scheme_table = build_customer_sample_info_from_layout(room_data, room_layout, {}, room_type, style)

    # data_time = time.strftime("%Y-%m-%d") + "/"
    # name_time = str(int(time.time() * 1000))
    #
    # scene_name = room_id + "_" + name_time + "_edited.json"
    # oss_upload_json("layout_scene_advisor/" + data_time + scene_name, house_scene_data, "ihome-alg-layout")
    #
    # scene_url = "https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com/layout_scene_advisor/" + data_time + scene_name

    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]

    scene_info = {
        "house_id": "advisor_layout_diy_" + house_id,
        "scene_info": {
            "url": url,
            "room": target_house_camera_list,
            "style": style
        },
        "ai_design_schema": scheme_table
    }

    return scene_info


def main_process(inputs):
    room_data = {}
    diff = {}
    scene_url = ""
    style = "Swedish"

    if "scene_url" in inputs:
        scene_url = inputs["scene_url"]

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

    if "diff" in inputs:
        diff = inputs["diff"]
        if type(diff) == str:
            try:
                diff = json.loads(diff)
            except:
                diff = {}

    if scene_url:
        return_data = scene_data_refine(scene_url, diff, style, room_data)
        if "scene_info" in return_data:
            if "url" in return_data["scene_info"]:
                print(return_data["scene_info"]["url"])

    else:
        return_data = {}

    return return_data


def get_diff_scene(url, diff):
    house_scene_json = get_scene_data(url)
    house_scene_data = scene_diff_update(house_scene_json, diff)

    data_time = time.strftime("%Y-%m-%d") + "/"
    name_time = str(int(time.time() * 1000))

    scene_name = name_time + "_edited.json"
    oss_upload_json("layout_scene_advisor/" + data_time + scene_name, house_scene_data, "ihome-alg-layout")

    scene_url = "https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com/layout_scene_advisor/" + data_time + scene_name
    print(scene_url)


if __name__ == '__main__':

    url = "https://homeai-inner.oss-cn-zhangjiakou.aliyuncs.com/design%20-%20smartb41a45b5-97eb-4db2-bfcd-ba8cd70dad32.json"
    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]

    # get_diff_scene(url, diff)
    scene_data_refine(url, {}, "", {})