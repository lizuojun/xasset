"""
设计还原：表单生成
"""
import copy
import json
import math
import os

from Furniture.furniture import get_furniture_data_more, get_furniture_data, add_furniture_type, save_furniture_type, \
    add_furniture_data
from HouseSearch.group_sample_search import house_seed_dict_group_list_search
from HouseSearch.house_search import get_sample_data_from_house_sample_keys
from HouseSearch.house_search_main import house_search_get_sample_info
from HouseSearch.util import get_http_data_from_url

extract_map = {
    "living_group/sofa": ["Meeting", "sofa"],
    "living_group/side_sofa": ["Meeting", "side sofa"],
    "living_group/table": ["Meeting", "table"],
    "living_group/side_table": ["Meeting", "side table"],
    "living_group/rug": ["Meeting", "rug"],
    "living_group/lighting": ["Ceiling", "lighting", "Meeting", "sofa"],
    "living_group/picture": ["Wall", "art", "Meeting", "sofa"],
    "living_group/media_table": ["Media", "table"],

    "dining_group/table": ["Dining", "table"],
    "dining_group/chair": ["Dining", "chair"],
    "dining_group/picture": ["Wall", "art", "Dining", "table"],
    "dining_group/lighting": ["Ceiling", "lighting", "Dining", "table"],

    "bed_group/bed": ["Bed", "bed"],
    "bed_group/side_table": ["Bed", "side table"],
    "bed_group/lighting": ["Ceiling", "lighting", "Bed", "bed"],

    "dining_cabinet/dining_cabinet": ["Cabinet", "cabinet", "Dining", "table"],
    "shoe_cabinet/shoe_cabinet": ["Cabinet", "cabinet", "Entry", "entry"],

    "bed_media/media_table": ["Media", "table"],
    "armoire/armoire": ["Armoire", "armoire"],
    "work_group/table": ["Work", "table"],
    "work_group/chair": ["Work", "chair"],
    "dress_group/table": ["Work", "table"],
    "dress_group/chair": ["Work", "chair"],

    "accessory/curtain": ["Window", "curtain"],
    "accessory/rug": ["Bed", "rug"],
    "accessory/side_table": ["Rest", "table"],
    "accessory/chair": ["Rest", "chair"],
    "accessory/picture": ["Wall", "art"],
    "accessory/floor_lamp": ["Meeting", "side table"],
    "accessory/storage_cabinet": ["Cabinet", "cabinet"],
    "accessory/lighting": ["Bed", "side table lighting"]
}

material_json_path = os.path.join(os.path.dirname(__file__), "new_material_jid_info.json")
material_json = json.load(open(material_json_path))


def map_extract_group_role(key):
    if key in extract_map:
        return extract_map[key]
    return []


# 门信息创建
def get_furniture_material_info(jid, to_type, role):
    if jid in material_json:
        return material_json[jid].copy()
    else:
        obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id = get_furniture_data_more(jid)
        return {
            "id": jid,
            "type": obj_type,
            "style": obj_style_en,
            "size": obj_size,
            "scale": [
                1,
                1,
                1
            ],
            "position": [0.0, 0.0, 0.0],
            "rotation": [0, 0, 0, 1],
            "entityId": "0",
            "categories": [obj_category_id],
            "category": obj_category_id,
            "unit_to_room": "",
            "unit_to_type": to_type,
            "role": role,
            "count": 1,
            "relate": "",
            "relate_group": "",
            "relate_position": []
        }


# 门通向设置
def get_door_to_flag(door_to, door_to_type={}):
    if len(door_to) == 0:
        return "entry"
    elif "-" not in door_to:
        return "entry"
    else:
        if door_to in door_to_type:
            room_type = door_to_type[door_to]
        else:
            room_type, _ = door_to.split("-")
        if room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
            return "LivingDiningRoom"
        elif room_type in ["Bedroom", "SecondBedroom", "MasterBedroom", "KidsRoom", "NannyRoom", "ElderlyRoom", ""]:
            return "Bedroom"
        elif room_type in ["Kitchen"]:
            return "Kitchen"
        elif room_type in ["Balcony"]:
            return "Balcony"
        elif room_type in ["Bathroom", "SecondBathroom", "MasterBathroom"]:
            return "Bathroom"
        else:
            return "Other"


def get_hard_material_info(obj_jid, color_map=None):
    if obj_jid in material_json:
        return material_json[obj_jid].copy()
    else:
        out_info = {
            "jid": obj_jid,
            "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + obj_jid + "/wallfloor.jpg",
            "color": [
                255,
                255,
                255
            ],
            "colorMode": "texture",
            "size": [
                1,
                1
            ],
            "seam": False,
            "material_id": obj_jid,
            "area": 10.0,
            "wall": [
            ],
            "offset": True,
            "alias": obj_jid
        }
        if color_map and obj_jid in color_map:
            try:
                color_data = [int(i) for i in color_map[obj_jid]]
                out_info["colorMode"] = "color"
                out_info["color"] = color_data
            except:
                print("color_data fail", color_map[obj_jid])

        return out_info


def build_furniture_info(jid, role, relate_group, relate_role):
    obj_type, obj_style_en, obj_size = get_furniture_data(jid)
    return {
        "id": jid,
        "type": obj_type,
        "style": obj_style_en,
        "size": obj_size,
        "scale": [
            1.0,
            1.0,
            1.0,
        ],
        "position": [0, 0, 0
                     ],
        "rotation": [
            0,
            0.0,
            0,
            1.0
        ],
        "entityId": jid,
        "categories": [
            ""
        ],
        "category": "",
        "role": role,
        "count": 1,
        "relate": "",
        "relate_group": relate_group,
        "relate_position": [0, 0, 0
                            ],
        "relate_role": relate_role,
        "origin_position": [
            0, 0, 0
        ],
        "origin_rotation": [
            0,
            0.0,
            0,
            1.0
        ],
        "normal_position": [
            0, 0, 0
        ],
        "normal_rotation": [
            0,
            0,
            0,
            1.0
        ]
    }


def check_sofa_L_type(jid):
    url = "http://calcifer-api.alibaba-inc.com/api/v1/models/" + jid + "/algorithm?keys=l_sofa_shape_type"
    data = get_http_data_from_url(url)
    if data:
        if jid in data and "l_sofa_shape_type" in data[jid]:
            print(data[jid]["l_sofa_shape_type"])
            if data[jid]["l_sofa_shape_type"] == "右":
                add_furniture_type(jid, "sofa/right corner sofa")
            elif data[jid]["l_sofa_shape_type"] == "左":
                add_furniture_type(jid, "sofa/left corner sofa")
    # save_furniture_type()


def check_group_furniture_seed_info(group_one, group_data_map, group_name, role_name):
    if group_name in group_data_map and role_name in group_data_map[group_name]:
        for item_info in group_data_map[group_name][role_name]:
            jid, relate_group, relate_role = item_info["id"], item_info["relate_group"], item_info[
                "relate_role"]
            group_one["obj_list"].append(build_furniture_info(jid, role_name, relate_group, relate_role))


def build_cabinet_seed_group_sample_info(group_data_map, group_name="Cabinet"):
    out_group_list = []
    if group_name in group_data_map:
        if "cabinet" in group_data_map[group_name]:
            for s_info in group_data_map[group_name]["cabinet"]:
                obj_info = build_furniture_info(s_info["id"], "cabinet", s_info["relate_group"], s_info["relate_role"])
                group_temp = {
                    "type": "Cabinet",
                    "style": obj_info["style"],
                    "code": 10,
                    "size": [i / 100. for i in obj_info["size"]],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "offset": [
                        -0.0,
                        0,
                        -0.0
                    ],
                    "position": [
                        0, 0, 0
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "size_min": [i / 100. for i in obj_info["size"]],
                    "size_rest": [
                        0.0,
                        0.0,
                        0.0,
                        0.0
                    ],
                    "relate": "",
                    "relate_position": [],
                    "obj_main": obj_info["id"],
                    "obj_type": obj_info["type"],
                    "obj_list": [obj_info.copy()]
                }
                if s_info["relate_group"] == "Entry":
                    group_temp["zone"] = "Hallway"
                elif s_info["relate_group"] == "Dining":
                    group_temp["zone"] = "DiningRoom"
                out_group_list.append(group_temp)

    return out_group_list


def build_armoire_seed_group_sample_info(group_data_map, group_name="Armoire"):
    out_group_list = []
    if group_name in group_data_map:
        if "armoire" in group_data_map[group_name]:
            for s_info in group_data_map[group_name]["armoire"]:
                obj_info = build_furniture_info(s_info["id"], "armoire", "", "")
                group_temp = {
                    "type": "Armoire",
                    "style": obj_info["style"],
                    "code": 10,
                    "size": [i / 100. for i in obj_info["size"]],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "offset": [
                        -0.0,
                        0,
                        -0.0
                    ],
                    "position": [
                        0, 0, 0
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "size_min": [i / 100. for i in obj_info["size"]],
                    "size_rest": [
                        0.0,
                        0.0,
                        0.0,
                        0.0
                    ],
                    "relate": "",
                    "relate_position": [],
                    "obj_main": obj_info["id"],
                    "obj_type": obj_info["type"],
                    "obj_list": [obj_info.copy()]
                }
                out_group_list.append(group_temp)

    return out_group_list


def get_scheme_table_info(table_list, now_type):
    for item_data in table_list:
        if item_data["key"] == now_type:
            return item_data
    else:
        return {}


def get_default_entry_door(style):
    if style == "Swedish":
        return {
            "single": "ebe82a44-1f76-488e-b0ab-288c511afe22",
            "double": "01360f1e-6eb7-4e9d-a5b7-70ff0c359f92"
        }
    else:
        return {
            "single": "276cc863-47d8-4db8-8723-f626a04d1e8c",
            "double": "5d3ae088-e058-4665-bcbb-d05287ca5fc2"
        }


def get_default_ceiling(jid):
    if jid == "db593061-992e-4fa9-b4f4-f4db7cc0ef25":
        return {
            "id": "a9262ce3-2523-41d1-b289-ba14f76af345",
            "resizeable": True,
            "inner_decoration": True,
            "size": [
                384,
                12,
                764
            ],
            "contentType": "build element/ceiling molding"
        }
    else:
        return {
            "id": "251c1850-5d78-4c64-a3f5-78355388592d",
            "resizeable": True,
            "inner_decoration": True,
            "size": [
                347,
                20,
                310
            ],
            "contentType": "build element/gypsum ceiling"
        }


def update_group_rug_obj(group_one, obj_list):
    if len(obj_list) == 0:
        return
    if "id" not in obj_list[0]:
        return
    rug_jid = obj_list[0]["id"]
    main_size = group_one["size_min"].copy()
    main_pos = group_one["position"].copy()
    obj_type, obj_style_en, obj_size = get_furniture_data(rug_jid)
    if group_one["type"] == "Meeting":
        target_size = [330, 0.65, 180]
    else:
        target_size = [230, 0.65, 150]
    used_origin_rug = False
    for obj_idx in range(len(group_one["obj_list"]) - 1, -1, -1):
        if group_one["obj_list"][obj_idx]["role"] == "rug":
            group_one["obj_list"][obj_idx]["id"] = rug_jid
            group_one["obj_list"].pop(obj_idx)

            used_origin_rug = False

    if not used_origin_rug:
        if group_one["type"] == "Meeting":
            add_pos = main_size[2] * 0.7
        else:
            add_pos = 1.5 / 2.

        new_scale = [target_size[i] / (obj_size[i]) for i in [0, 1, 2]]
        # new_scale[1] = 0.8
        new_obj_data = {'id': rug_jid,
                        'type': obj_type,
                        'style': obj_style_en,
                        'size': obj_size.copy(),
                        'scale': new_scale,
                        'position': main_pos.copy(),
                        'rotation': [0, 0, 0, 1.0],
                        'entityId': 'new',
                        'categories': ['cabb5091-b54f-4fe9-b990-a7ac1b1b2803'],
                        'category': 'cabb5091-b54f-4fe9-b990-a7ac1b1b2803',
                        'relate': '', 'group': group_one["type"], 'role': 'rug', 'count': 1, 'relate_position': [],
                        'adjust_position': [0, 0, 0],
                        'origin_position': [0, 0, 0],
                        'origin_rotation': [0, 0, 0, 1.0],
                        'normal_position': [0.0, 0, add_pos],
                        'normal_rotation': [0, 0.0, 0, 1.0]
                        }

        # 高于地毯
        for obj in group_one["obj_list"]:
            obj["normal_position"][1] += (0.65 / 100.)

        group_one["obj_list"].append(new_obj_data)


def get_base_deco_groups():
    out_group = []
    for group_name in ["Ceiling", "Floor", "Window", "Door", "Wall"]:
        out_group.append({"type": group_name,
                          "code": 100,
                          "size": [
                              0, 0, 0
                          ],
                          "obj_main": "",
                          "offset": [
                              0, 0, 0
                          ],
                          "position": [
                              0, 0, 0
                          ],
                          "rotation": [
                              0,
                              -0.0,
                              0,
                              1.0
                          ],
                          "obj_list": []})

    return out_group


def build_customer_replace_sample_info(room_info, extract_customer_info, best_layout_info=None,
                                       origin_room_key="", target_style="Swedish", house_data=None):
    # 先提取软装list
    if not room_info:
        return {}, [], {}

    door_to_room_type_table = {}
    if house_data:
        for room in house_data["room"]:
            room_id = room["id"]
            door_to_room_type_table[room_id] = room["type"]

    room_type = room_info["type"]
    if room_type in ["LivingDiningRoom", "LivingRoom", "Dining"]:
        room_type = "LivingDiningRoom"
    else:
        room_type = "Bedroom"

    # 最佳床功能区尺寸:
    best_bed_group_size = None
    if best_layout_info:
        for scheme in best_layout_info["layout_scheme"]:
            for target_group in scheme["group"]:
                if target_group["type"] == "Bed":
                    best_bed_group_size = target_group["size"]
                    break
            break

    seeds_list = []
    seeds_table = {}
    group_data_map = {}
    if "custom_furniture" in extract_customer_info and "items" in extract_customer_info["custom_furniture"]:
        for first_group_item in extract_customer_info["custom_furniture"]["items"]:
            if first_group_item["key"] == "custom_cabinet":
                if "model_list" in first_group_item:
                    for model_info in first_group_item["model_list"]:
                        if "Armoire" not in group_data_map:
                            group_data_map["Armoire"] = {}
                        if "armoire" not in group_data_map["Armoire"]:
                            group_data_map["Armoire"]["armoire"] = []

                        group_data_map["Armoire"]["armoire"].append({"id": model_info["id"], "relate_group": "",
                                                                     "relate_role": ""})
                        obj_type, obj_style_en, obj_size = get_furniture_data(model_info["id"])
                        seeds_table[model_info["id"]] = {"group": "Armoire", "role": "armoire", "size": obj_size,
                                                         "type": obj_type,
                                                         "id": model_info["id"], "scale": [1, 1, 1],
                                                         "position": [0, 0, 0],
                                                         "rotation": [0, 0, 0, 1], "style": obj_style_en}

            elif first_group_item["key"] == "custom_media":
                if "model_list" in first_group_item:
                    for model_info in first_group_item["model_list"]:
                        if "Media" not in group_data_map:
                            group_data_map["Media"] = {}
                        if "table" not in group_data_map["Media"]:
                            group_data_map["Media"]["table"] = []

                        group_data_map["Media"]["table"].append({"id": model_info["id"], "relate_group": "",
                                                                 "relate_role": ""})
                        obj_type, obj_style_en, obj_size = get_furniture_data(model_info["id"])
                        seeds_table[model_info["id"]] = {"group": "Media", "role": "table", "size": obj_size,
                                                         "type": obj_type,
                                                         "id": model_info["id"], "scale": [1, 1, 1],
                                                         "position": [0, 0, 0],
                                                         "rotation": [0, 0, 0, 1], "style": obj_style_en}

    if "furnishing" in extract_customer_info and "items" in extract_customer_info["furnishing"]:
        for first_group_item in extract_customer_info["furnishing"]["items"]:
            first_key = first_group_item["key"]
            for second_group_item in first_group_item["items"]:
                second_group_key = second_group_item["key"]
                group_info = map_extract_group_role(first_key + "/" + second_group_key)
                if len(group_info) == 0:
                    continue

                group = group_info[0]
                role = group_info[1]
                relate_group, relate_role = "", ""
                if len(group_info) == 4:
                    relate_group, relate_role = group_info[2], group_info[3]
                else:
                    role = group_info[1]

                for model in second_group_item["model_list"]:

                    if group not in group_data_map:
                        group_data_map[group] = {}
                    if role not in group_data_map[group]:
                        group_data_map[group][role] = []
                    group_data_map[group][role].append({"id": model["id"], "relate_group": relate_group,
                                                        "relate_role": relate_role})
                    obj_type, obj_style_en, obj_size = get_furniture_data(model["id"])
                    seeds_table[model["id"]] = {"group": group, "role": role, "size": obj_size, "type": obj_type,
                                                "id": model["id"], "scale": [1, 1, 1], "position": [0, 0, 0],
                                                "rotation": [0, 0, 0, 1], "style": obj_style_en}
                    break

    if "accessory" in extract_customer_info and "items" in extract_customer_info["accessory"]:
        for item_info in extract_customer_info["accessory"]["items"]:
            group_key = "accessory"
            item_key = item_info["key"]
            group_info = map_extract_group_role(group_key + "/" + item_key)
            if len(group_info) == 0:
                continue

            group = group_info[0]
            role = group_info[1]
            relate_group = ""
            relate_role = ""

            for model in item_info["model_list"]:
                if group not in group_data_map:
                    group_data_map[group] = {}
                if role not in group_data_map[group]:
                    group_data_map[group][role] = []

                if group == "Wall" and role == "art":
                    if room_type in ["LivingDiningRoom", "LivingRoom"]:
                        relate_group, relate_role = "Meeting", "sofa"
                    elif room_type in ["DiningRoom"]:
                        relate_group, relate_role = "Dining", "table"
                    else:
                        relate_group, relate_role = "Bed", "bed"

                group_data_map[group][role].append({"id": model["id"], "relate_group": relate_group,
                                                    "relate_role": relate_role})
                obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id = \
                    get_furniture_data_more(model["id"])
                seeds_table[model["id"]] = {"group": group, "role": role, "size": obj_size, "type": obj_type,
                                            "id": model["id"], "scale": [1, 1, 1], "position": [0, 0, 0],
                                            "rotation": [0, 0, 0, 1], "style": obj_style_en,
                                            "category_id": obj_category_id}
                break

    sample_info_list = []
    # if len(origin_room_key) > 0:
    #     if
    #     search_sample_key_info = {'score': 0., 'style': 'Modern',
    #                               'sample': {room_info["id"]: origin_room_key}}
    #     layout_sample_info = get_sample_data_from_house_sample_keys(search_sample_key_info)
    #     scheme_info = layout_sample_info["sample"][room_info["id"]]["layout_scheme"][0]
    # else:
    # 软装提取list, 进行检索
    seeds_list = []
    for group in group_data_map:
        for role in group_data_map[group]:
            for model in group_data_map[group][role]:
                seeds_list.append(model["id"])

    seed_info = {room_info["id"]: {
        "soft": seeds_list
    }}
    # 检索方案
    sample_info_list = house_seed_dict_group_list_search(seeds_table, room_type, source_id=origin_room_key)
    sample_info_list += get_base_deco_groups()
    scheme_info = {"code": 10000,
                   "score": 100,
                   "type": room_type,
                   "style": "Contemporary",
                   "area": room_info["area"],
                   "material": {},
                   "group": sample_info_list,
                   "source_house": "sample_house",
                   "source_room": room_info["id"],
                   }

    # 软装尺寸处理
    # 主沙发处理
    if "Meeting" in group_data_map and "sofa" in group_data_map["Meeting"]:
        if len(group_data_map["Meeting"]["sofa"]) > 0:
            jid = group_data_map["Meeting"]["sofa"][0]["id"]
            check_sofa_L_type(jid)

    # 床处理
    target_bed_size = None
    target_side_table_size = None
    if "Bed" in group_data_map and "bed" in group_data_map["Bed"]:
        if len(group_data_map["Bed"]["bed"]) > 0:
            jid = group_data_map["Bed"]["bed"][0]['id']
            bed_info = seeds_table[jid]
            # check_sofa_L_type(jid)

            target_bed_size = bed_info["size"].copy()
            obj_new = {"id": bed_info["id"], "type": bed_info["type"], "obj_size": bed_info["size"],
                       "size": bed_info["size"],
                       "style": bed_info["style"]}

            add_furniture_data(bed_info["id"], obj_new)

    if "Bed" in group_data_map and "side table" in group_data_map["Bed"]:
        if len(group_data_map["Bed"]["side table"]) > 0:
            jid = group_data_map["Bed"]["side table"][0]['id']
            model_info = seeds_table[jid]

            target_side_table_size = model_info["size"].copy()
            if target_side_table_size[0] > 55:
                model_info["size"][0] = 55.
            obj_new = {"id": model_info["id"], "type": model_info["type"], "obj_size": model_info["size"],
                       "size": model_info["size"],
                       "style": model_info["style"]}

            add_furniture_data(model_info["id"], obj_new)

    # 方案处理
    if not scheme_info:
        return {}, [], {}

    material_info = {
        "id": room_info["id"],
        "type": room_info["type"],
        "floor": [
        ],
        "wall": [],
        "win_pocket": [],
        "door_pocket": [],
        "win": [],
        "door": {},
        "customized_ceiling": [],
        "background": [],
        "baseboard": []
    }

    hard_table_extract_info = {}
    color_map = {}
    if "decorating" in extract_customer_info and "items" in extract_customer_info["decorating"]:
        for name in ["swing_door", "sliding_door", "floor", "ceiling", "main_back_wall", "rest_back_wall", "wall",
                     "window", "basebaord", "main_wall_texture"]:
            item_list = get_scheme_table_info(extract_customer_info["decorating"]["items"], name)
            if item_list and "model_list" in item_list:
                item_list = item_list["model_list"]
                all_list = []
                for i in item_list:
                    all_list.append(i["id"])
                    if "color" in i and len(i["color"]) > 5:
                        color_map[i["id"]] = i["color"][4:-1].split(',')
                hard_table_extract_info[name] = all_list

    # 硬装门
    entry_door = get_default_entry_door(target_style)

    door_list = room_info["door_info"] + room_info["hole_info"]
    pocket = None
    for origin_door in door_list:
        l1 = math.sqrt((origin_door["pts"][0] - origin_door["pts"][2]) ** 2 + (
                origin_door["pts"][1] - origin_door["pts"][3]) ** 2)
        l2 = math.sqrt((origin_door["pts"][2] - origin_door["pts"][4]) ** 2 + (
                origin_door["pts"][3] - origin_door["pts"][5]) ** 2)
        door_length = max(l1, l2)
        door_flag = get_door_to_flag(origin_door["to"], door_to_room_type_table)
        if door_flag not in material_info["door"]:
            material_info["door"][door_flag] = []
        # 入户门
        if door_flag == "entry":
            if door_length < 1.2:
                if pocket:
                    entry_door["single"]["pocket"] = pocket.copy()
                material_info["door"][door_flag].append(get_hard_material_info(entry_door["single"]))
            else:
                if pocket:
                    entry_door["single"]["pocket"] = pocket.copy()
                material_info["door"][door_flag].append(get_hard_material_info(entry_door["double"]))
        # 非入户门
        else:
            if door_length < 1.2:
                if "swing_door" in hard_table_extract_info:
                    for door_jid in hard_table_extract_info["swing_door"]:
                        door_mat_info_temp = get_furniture_material_info(door_jid, door_flag, "door")
                        if pocket:
                            door_mat_info_temp["pocket"] = pocket.copy()
                        material_info["door"][door_flag].append(door_mat_info_temp)
            else:
                if "sliding_door" in hard_table_extract_info:
                    for door_jid in hard_table_extract_info["sliding_door"]:
                        door_mat_info_temp = get_furniture_material_info(door_jid, door_flag, "door")
                        if pocket:
                            door_mat_info_temp["pocket"] = pocket.copy()
                        material_info["door"][door_flag].append(door_mat_info_temp)

    # 硬装背景
    if "main_wall_texture" in hard_table_extract_info:
        for main_wall_jid in hard_table_extract_info["main_wall_texture"]:
            wall_info = get_hard_material_info(main_wall_jid, color_map)
            if room_type == "Bedroom":
                wall_info["Functional"] = "Bed"
            if room_type == "LivingDiningRoom":
                wall_info["Functional"] = "Meeting"
            material_info["wall"].append(wall_info)

    # 硬装窗
    if "window" in hard_table_extract_info:
        for window_jid in hard_table_extract_info["window"]:
            material_info["win"].append(get_furniture_material_info(window_jid, "", "window"))

    if "basebaord" in hard_table_extract_info:
        for base_jid in hard_table_extract_info["basebaord"]:
            # if len(material_info["baseboard"]) == 0:
            #     if "pocket" in door_mat_info_temp and door_mat_info_temp["pocket"]:
            #         pocket = door_mat_info_temp["pocket"]
            material_info["baseboard"].append(get_hard_material_info(base_jid))

    # 硬装背景墙
    if "main_back_wall" in hard_table_extract_info:
        for back_jid in hard_table_extract_info["main_back_wall"]:
            back_temp_info = get_furniture_material_info(back_jid, "", "background")
            if room_type == "Bedroom":
                back_temp_info["Functional"] = "Bed"
            if room_type == "LivingDiningRoom":
                back_temp_info["Functional"] = "Meeting"
            material_info["background"].append(back_temp_info)

    # 硬装背景墙
    if "rest_back_wall" in hard_table_extract_info:
        for back_jid in hard_table_extract_info["rest_back_wall"]:
            back_temp_info = get_furniture_material_info(back_jid, "", "background")
            back_temp_info["Functional"] = "Media"
            material_info["background"].append(back_temp_info)

    if "wall" in hard_table_extract_info:
        for wall_jid in hard_table_extract_info["wall"]:
            material_info["wall"].append(get_hard_material_info(wall_jid, color_map))

    if "floor" in hard_table_extract_info:
        for floor_jid in hard_table_extract_info["floor"]:
            material_info["floor"].append(get_hard_material_info(floor_jid))

    # 硬装ceiling
    if "ceiling" in hard_table_extract_info:
        for ceiling_jid in hard_table_extract_info["ceiling"]:
            material_info["customized_ceiling"].append(get_default_ceiling(ceiling_jid))

    if len(origin_room_key) == 0:
        scheme_info["material"] = material_info

    # 软装处理
    for group in scheme_info["group"]:
        group_type = group["type"]
        if group_type == "Ceiling":
            group["obj_list"] = []
            check_group_furniture_seed_info(group, group_data_map, "Ceiling", "lighting")
        elif group_type == "Wall":
            group["obj_list"] = []
            check_group_furniture_seed_info(group, group_data_map, "Wall", "art")
        elif group_type == "Floor":
            group["obj_list"] = []
            check_group_furniture_seed_info(group, group_data_map, "Floor", "plant")
            check_group_furniture_seed_info(group, group_data_map, "Floor", "lamp")
        elif group_type == "Window":
            group["obj_list"] = []
            check_group_furniture_seed_info(group, group_data_map, "Window", "curtain")

    # 床功能区修正
    # if best_bed_group_size and target_side_table_size and target_bed_size:
    #     now_size = 2 * target_side_table_size[0] + target_bed_size[0]
    #     if now_size > best_bed_group_size[0]:
    #         for group in scheme_info["group"]:
    #             if group['type'] == "Bed":
    #                 need_side_table = None
    #                 for obj_idx in range(len(group["obj_list"]) - 1, -1, -1):
    #                     if group["obj_list"][obj_idx]["role"] == "side table":
    #                         need_side_table = group["obj_list"][obj_idx]
    #                         group["obj_list"].pop(obj_idx)
    #                 if need_side_table:
    #                     group["obj_list"].append(need_side_table)

    # 软装 处理其他功能区 Cabinet/Rest
    # 去除柜子
    for group_idx in range(len(scheme_info["group"]) - 1, -1, -1):
        if scheme_info["group"][group_idx]['type'] == "Cabinet":
            scheme_info["group"].pop(group_idx)
    scheme_info["group"] += build_cabinet_seed_group_sample_info(group_data_map, "Cabinet")

    if "Armoire" in group_data_map:
        for group_idx in range(len(scheme_info["group"]) - 1, -1, -1):
            if scheme_info["group"][group_idx]['type'] == "Armoire":
                scheme_info["group"].pop(group_idx)
        now_armoire_list = build_armoire_seed_group_sample_info(group_data_map, "Armoire")
        if len(now_armoire_list) > 0:
            scheme_info["group"].insert(0, build_armoire_seed_group_sample_info(group_data_map, "Armoire")[0])

    # 去除rest
    for group_idx in range(len(scheme_info["group"]) - 1, -1, -1):
        if scheme_info["group"][group_idx]['type'] == "Rest":
            scheme_info["group"].pop(group_idx)

    if not "Work" in group_data_map:
        for group_idx in range(len(scheme_info["group"]) - 1, -1, -1):
            if scheme_info["group"][group_idx]['type'] == "Work":
                scheme_info["group"].pop(group_idx)
    else:
        work_group_default = None
        for group_idx in range(len(scheme_info["group"]) - 1, -1, -1):
            if scheme_info["group"][group_idx]['type'] == "Work":
                work_group_default = scheme_info["group"][group_idx]
                scheme_info["group"].pop(group_idx)
        if work_group_default:
            scheme_info["group"].append(work_group_default)

    # 地毯处理 对沙发/床功能区没有地毯的情况进行处理
    for need_group_type in ["Meeting", "Bed"]:
        if need_group_type in group_data_map and "rug" in group_data_map[need_group_type]:
            for group_one in scheme_info["group"]:
                if group_one['type'] == need_group_type:
                    update_group_rug_obj(group_one, group_data_map[need_group_type]["rug"])

    print("use sample room", scheme_info["source_house"] + "_" + scheme_info["source_room"])
    scheme_info["source_house"] = "sample_house"
    scheme_info["source_room"] += "_diy"

    # add_furniture_group_list(scheme_info["source_house"], scheme_info["source_room"], scheme_info["group"])

    # 合并
    layout_sample = {
        "room_type": room_info['type'],
        "room_style": "",
        "room_area": room_info['area'],
        "room_height": 2.6,
        "layout_seed": [],
        "layout_keep": [],
        "layout_plus": [],
        "layout_mesh": [],
        "layout_sample": [
            scheme_info],
        "layout_scheme": []
    }

    return layout_sample, seeds_list, seeds_table
