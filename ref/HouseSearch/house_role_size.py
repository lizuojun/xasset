import json, requests
from collections import OrderedDict
from functools import lru_cache

from Extract.extract_cache import get_house_base_data, correct_house_data
from Extract.import_region import add_house_region
from HouseSearch.put_home_sample_search import house_group_size_search, compute_room_group_size, \
    house_group_size_search_max
from HouseSearch.seed.service import thread_pool_task_waiting, thread_pool_task_waiting_main


SOFT_SERVICE_PROPOSE_URL = 'https://tui.alibaba-inc.com/recommend'
SOFT_SERVICE_PROPOSE_APP_ID = 23919

map_role_data = {
    "Bedroom": [
        {"map_role": ["Bed", "bed"], "catName": "床", "categoryGroupId": "CHUANG", "limit": 1},
        {"map_role": ["Bed", "side table"], "catName": "床头柜", "categoryGroupId": "CHUANGTOUGUI", "limit": 1},
        {"map_role": ["Work", "table"], "catName": "梳妆台", "categoryGroupId": "SHUZHUANGTAI", "limit": 1},
        {"map_role": ["Armoire", "armoire"], "catName": "衣柜", "categoryGroupId": "YIGUI", "limit": 1}
    ],
    "LivingRoom": [
        {"map_role": ["Meeting", "sofa"], "catName": "沙发", "categoryGroupId": "SHAFA", "limit": 1},
        {"map_role": ["Media", "table"], "catName": "电视柜", "categoryGroupId": "DIANSHIGUI", "limit": 1},
        {"map_role": ["Meeting", "table"], "catName": "茶几", "categoryGroupId": "CHAJI", "limit": 1},
        {"map_role": ["Dining", "table"], "catName": "餐桌", "categoryGroupId": "CANZHUO", "limit": 1},
        {"map_role": ["Dining", "chair"], "catName": "椅", "categoryGroupId": "YI", "limit": 1},
        {"map_role": ["Cabinet", "cabinet", "Hallway"], "catName": "鞋柜", "categoryGroupId": "XIEGUI", "limit": 1}
    ]
}

rec_style_role_data = {
    "Bedroom":
        {
            "Bed_bed": {
                "catName": "床",
                "categoryId": [
                    "24670bf9-9c9f-41ae-b190-f5f65eab4ddb",
                    "41ac92b5-5f88-46d0-a59a-e1ed31739154",
                    "bb8b2c7e-cc9e-4e4e-a208-d76cb1dd6e11"],
                "size": [1500, 1900],
                "style": {
                    "Nordic": ["50c7b1fd-984d-46a8-bd1f-6effb6b9ab6b", "63425d9c-9fe6-4375-8ba9-92719d02f1be"],
                    "Modern": ["326c23d5-9469-4a63-bdf5-c8acb2738299", "19b9974d-363d-47df-81b5-81893d48a813"],
                    "Japanese": ["4b7be1f3-20e5-445d-9e82-cbc368683221", "f1e5f869-97e3-42d6-b9f5-6a05365b14b3"],
                    "Luxury": ["73acd523-ece0-4a84-9825-0b90c0ce291f", "96771847-ac1e-4916-a361-0020d509d8df"]
                }
            },
            "Bed_side table": {
                "catName": "床头柜",
                "categoryId": ["89404b8a-5bb6-42cf-95fa-73c9bfba4c97"],
                "style": {
                    "Nordic": ["8bd704bc-17fb-4097-86de-9ebce83a31f9", "63425d9c-9fe6-4375-8ba9-92719d02f1be"],
                    "Modern": ["1de47660-d8ac-4361-9ce1-f0bf58e3a2da", "19b9974d-363d-47df-81b5-81893d48a813"],
                    "Japanese": ["0b912c41-63c5-4da7-86b6-0278fdddd980", "f1e5f869-97e3-42d6-b9f5-6a05365b14b3"],
                    "Luxury": ["995601ea-a43f-4bd7-a892-70e89827a215", "96771847-ac1e-4916-a361-0020d509d8df"]
                }
            },
            "Work_table": {
                "catName": "梳妆台",
                "categoryId": ["469c4481-d969-416f-8796-988cc28ca9c3"],
                "style": {
                    "Nordic": ["4f691e78-4740-40c7-8069-39f9de007d5e", "63425d9c-9fe6-4375-8ba9-92719d02f1be"],
                    "Modern": ["310d4a4e-5238-4c0f-b558-028baa8f370c", "19b9974d-363d-47df-81b5-81893d48a813"],
                    "Japanese": ["89bfd6de-d653-4ae0-bcc1-d2f7a488cab1", "f1e5f869-97e3-42d6-b9f5-6a05365b14b3"],
                    "Luxury": ["66e2b009-e3a9-483b-a84b-e139bbfc8eb6", "96771847-ac1e-4916-a361-0020d509d8df"]
                }
            },
            "Armoire_armoire": {
                "catName": "衣柜",
                "categoryId": ["2dd2368f-a3eb-43c2-8a6b-d585cd19d9a6"],
                "style": {
                    "Nordic": ["82df9eb4-43fd-45db-93dd-279e8da566cb", "63425d9c-9fe6-4375-8ba9-92719d02f1be"],
                    "Modern": ["faff5518-52ee-4bd5-9f98-a3f24ea52c1a", "19b9974d-363d-47df-81b5-81893d48a813"],
                    "Japanese": ["8f759133-dc75-4911-b8a9-e70c1e93f565", "f1e5f869-97e3-42d6-b9f5-6a05365b14b3"],
                    "Luxury": ["31056a07-d513-4ce2-8a05-d7b08a96975b", "96771847-ac1e-4916-a361-0020d509d8df"]
                }
            }
        }
    ,
    "LivingRoom": {
        "Meeting_sofa": {
            "catName": "沙发",
            "categoryId": ["a5af8349-bd50-46aa-b97a-2940125aafae", "d2a64592-caa7-4ab1-877e-561323315774",
                           "81780f40-fa53-41c3-8579-65706f4ad50d"],
            "size": [2500, 3500],
            "style": {
                "Nordic": ["bcbad41e-8e07-4f13-93b0-f850f8c50840", "63425d9c-9fe6-4375-8ba9-92719d02f1be"],
                "Modern": ["e4b3541b-a952-47d4-b740-b1f43b8d2af4", "19b9974d-363d-47df-81b5-81893d48a813"],
                "Japanese": ["b40fc616-e40f-4457-939c-530fc47d7d3b", "f1e5f869-97e3-42d6-b9f5-6a05365b14b3"],
                "Luxury": ["412ccc9b-c115-4e44-82f3-bdf8759755e2", "96771847-ac1e-4916-a361-0020d509d8df"]
            }
        },
        "Meeting_table": {
            "categoryId": ["9eaee326-16c4-4244-87d5-38e7b57a4e38"],
            "catName": "茶几",
            "style": {
                "Nordic": ["372ca4e4-3d92-4d0a-a5f2-8b1a153e69c1", "63425d9c-9fe6-4375-8ba9-92719d02f1be"],
                "Modern": ["d025e0f7-0afd-491b-a961-1b357ae22016", "19b9974d-363d-47df-81b5-81893d48a813"],
                "Japanese": ["a181f639-9b2a-4849-8f1e-7dcbf1a246a9", "f1e5f869-97e3-42d6-b9f5-6a05365b14b3"],
                "Luxury": ["2391a9e2-c0d0-4f09-a1a6-df6a66a9dda7", "96771847-ac1e-4916-a361-0020d509d8df"]
            }
        },
        "Media_table": {
            "catName": "电视柜",
            "categoryId": ["a1804c08-fbdc-4696-9c38-3d3b143c1b02"],
            "style": {
                "Nordic": ["bfa028dc-c91a-41f4-9b13-e57c5c774710", "63425d9c-9fe6-4375-8ba9-92719d02f1be"],
                "Modern": ["44e4d290-6ab3-4335-a593-f1930a791f01", "19b9974d-363d-47df-81b5-81893d48a813"],
                "Japanese": ["7ddde7b5-460d-4763-ad82-fca2b78d81c1", "f1e5f869-97e3-42d6-b9f5-6a05365b14b3"],
                "Luxury": ["3e30207c-03bf-493a-8ed2-b8d944a36387", "96771847-ac1e-4916-a361-0020d509d8df"]
            }
        }
    }
}


def get_return_format(house_size_target, house_type_dict):
    # key room_id target size_info
    out = {}
    for room_id in house_size_target:
        if room_id in house_type_dict:
            room_type = house_type_dict[room_id]
            if room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
                now_type = "LivingRoom"
            elif room_type in ["MasterBedroom", "Bedroom", "SecondBedroom"]:
                now_type = "Bedroom"
            else:
                continue
        else:
            continue

        temp = []
        now_room_size = house_size_target[room_id]
        if now_type not in map_role_data:
            continue

        for target_item in map_role_data[now_type]:
            group, role = target_item["map_role"][0:2]
            if group not in now_room_size or role not in now_room_size[group]:
                temp.append({
                    "categoryGroupId": target_item["categoryGroupId"],
                    "sizeMax": [1, 1, 1],
                    "limit": 1
                })
            else:
                size = [int(i * 1000) for i in now_room_size[group][role]]
                # change 2 1
                size[2], size[1] = size[1], size[2]
                temp.append({
                    "categoryGroupId": target_item["categoryGroupId"],
                    "sizeMax": size,
                    "limit": 1
                })
        out[room_id] = temp

    return out


def compute_use_house_data(house_data):
    if "room" not in house_data:
        return

    used_rooms = []
    all_bed_rooms = []
    for room_idx in range(len(house_data['room']) - 1, -1, -1):
        now_type = house_data['room'][room_idx]["type"]
        if now_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
            used_rooms.append(house_data['room'][room_idx])
        elif now_type in ["MasterBedroom", "Bedroom", "SecondBedroom"]:
            all_bed_rooms.append((house_data['room'][room_idx]["area"], room_idx))
        else:
            continue

    if all_bed_rooms:
        all_bed_rooms = sorted(all_bed_rooms, key=lambda x: x[0], reverse=True)
        used_rooms.append(house_data['room'][all_bed_rooms[0][1]])

    house_data['room'] = used_rooms


def refine_house_data(house_data):
    if "room" not in house_data:
        return

    used_rooms = []
    all_bed_rooms = []
    for room_idx in range(len(house_data['room']) - 1, -1, -1):
        now_type = house_data['room'][room_idx]["type"]
        if now_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
            used_rooms.append(house_data['room'][room_idx])
        elif now_type in ["MasterBedroom", "Bedroom", "SecondBedroom"]:
            used_rooms.append(house_data['room'][room_idx])
        else:
            continue

    house_data['room'] = used_rooms


def get_scheme_return_format(scheme):
    out = {}
    out_style = {"Modern": "Contemporary", "Nordic": "Swedish", "Luxury": "Light Luxury", "Japanese": "Japanese"}
    for room_id in scheme:
        room_schemes = []
        for style in ["Nordic", "Modern", "Japanese", "Luxury"]:
            target_style = out_style[style]
            items_list = []
            for item in scheme[room_id][style]:
                items_list.append(item)
            one_scheme = {"style": target_style, "items": items_list}
            room_schemes.append(one_scheme)
        out[room_id] = room_schemes

    return out


def tpp_input_scheme(house_id, room_id, area, model_id, category_list, category_name, style_id, size_data, cur_size):
    input_json = {
        "userId": "2207709684211",
        "imeisi": "",
        "designId": house_id,
        "currentRoomId": room_id,
        "currentRoomArea": "",
        "currentWallPaint": "",
        "modelRoomInfo": [
            {
                "categoryId": category_list[0],
                "categoryName": "",
                "modelId": model_id,
                "room_id": room_id
            }
        ],
        "interiorRoomInfo": [
        ],
        "currentModelInfo": {"modelId": model_id, "categoryId": category_list[0], "categoryName": "",
                             "styleId": style_id, "brandId": "", "isTransferModel": "true",
                             "role": ""},
        "categoryInfo": {"categoryId": category_list[0], "categoryName": "", "dim_x": ",",
                         "dim_y": ",",
                         "dim_z": ",", "color": "", "brandId": ""},
        "size_ori": [str(cur_size[0] / 1000.), str(cur_size[2] / 1000.), str(cur_size[1] / 1000.)],
        "scale_ori": ["1.0", "1.0", "1.0"],
        "page": 1,
        "pageSize": 15,
        "area_flag": "all",
        "modelBlacklist": []
    }
    return input_json


# 软装tpp接口请求
def multi_furniture_seeds_service_processing(input_keys):
    response_dict = {}
    output_furniture_list = []

    # 并行请求tpp
    task_var_list = []
    for input_key in input_keys:
        # 输入参数 (list, None)
        style, input_json = input_key
        task_var_list.append(((style, input_json, output_furniture_list), None))

    thread_pool_task_waiting(tpp_furniture_soft_service_info, task_var_list)

    # 结果处理 output_furniture_list
    for key_data in output_furniture_list:
        style, data = key_data
        if style not in response_dict:
            response_dict[style] = [data]
        else:
            response_dict[style].append(data)

    return response_dict


def tpp_furniture_soft_service_info(style, input_json, output_furniture_list):
    request_data = {
        'appid': SOFT_SERVICE_PROPOSE_APP_ID,
        'userId': 999999999,
        'input_json': json.dumps(input_json)
    }

    # 初次调用
    response_info = requests.post(SOFT_SERVICE_PROPOSE_URL, data=request_data)
    response_data = response_info.json()
    response_dict = {}

    response_good = False
    if 'result' in response_data and len(response_data['result']) > 0:
        result_list = response_data['result'][0]
        if "return_list" in result_list and len(result_list["return_list"]) > 0:
            output_furniture_list.append([style, result_list["return_list"][0]])
            response_good = True

    if not response_good:
        response_info = requests.post(SOFT_SERVICE_PROPOSE_URL, data=request_data)
        response_data = response_info.json()
        response_dict = {}
        if 'result' in response_data and len(response_data['result']) > 0:
            result_list = response_data['result'][0]
            if "return_list" in result_list and len(result_list["return_list"]) > 0:
                output_furniture_list.append([style, result_list["return_list"][0]])


def multi_room_processing(house_id, room_key, room_area, room_size_data, room_type, now_scheme):
    if room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
        now_type = "LivingRoom"
    elif room_type in ["MasterBedroom", "Bedroom", "SecondBedroom"]:
        now_type = "Bedroom"
    else:
        return

    style_data_map = rec_style_role_data[now_type]
    temp = {}
    input_multi_items = []
    for group in room_size_data:
        temp[group] = {}
        for role in room_size_data[group]:
            size = [int(i * 1000) for i in room_size_data[group][role]]
            # change 2 1
            size[2], size[1] = size[1], size[2]
            temp[group][role] = size

            role_key = group + '_' + role

            if role_key in style_data_map:
                role_info = style_data_map[role_key]

                target_cate = role_info["categoryId"]
                if "role_key" == "Bed_bed":
                    if size[0] > style_data_map[role_key]["size"][1]:
                        target_cate = target_cate[2:]
                    elif size[0] > style_data_map[role_key]["size"][0]:
                        target_cate = target_cate[1:]
                elif "role_key" == "Meeting_sofa":
                    if size[0] > style_data_map[role_key]["size"][1]:
                        target_cate = target_cate[2:]
                    elif size[0] > style_data_map[role_key]["size"][0]:
                        target_cate = target_cate[1:]

                for style in ["Nordic", "Modern", "Japanese", "Luxury"]:
                    input_json = tpp_input_scheme(house_id, room_key, room_area, role_info["style"][style][0],
                                                  target_cate, role_info["catName"],
                                                  role_info["style"][style][1], size, cur_size=size)
                    input_multi_items.append([style, input_json])

    style_model_data = multi_furniture_seeds_service_processing(input_multi_items)
    for style_key in style_model_data:
        if style_key in now_scheme:
            now_scheme[style_key] += style_model_data[style_key]


def role_size_interface(house_id, design_url, scene_url, return_scheme):
    _, house_data = get_house_base_data(house_id, design_url, scene_url)
    correct_house_data(house_data)

    add_house_region(house_id, house_data, recal_region_method='')
    refine_house_data(house_data)

    if not return_scheme:
        house_size_target = house_group_size_search_max(house_data, True)
        map_key = {}
        for room_data in house_data["room"]:
            map_key[room_data["id"]] = room_data["type"]

        return_format = get_return_format(house_size_target, map_key)

        return return_format
    else:
        house_size_target = house_group_size_search(house_data, False)

        # data_info, layout_info, propose_info = search_advice_house(house_data)

        # 四个风格
        scheme = {}

        room_process_data = []
        for room_info in house_data["room"]:
            room_key = room_info["id"]
            if room_key not in house_size_target:
                continue

            room_area = room_info["area"]
            room_type = room_info['type']

            scheme[room_key] = {"Modern": [], "Luxury": [], "Nordic": [], "Japanese": []}
            now_scheme = scheme[room_key]

            room_process_data.append(
                ((house_id, room_key, room_area, house_size_target[room_key], room_type, now_scheme), None))

        thread_pool_task_waiting_main(multi_room_processing, room_process_data)

        map_key = {}
        for room_data in house_data["room"]:
            map_key[room_data["id"]] = room_data["type"]

        scheme = get_scheme_return_format(scheme)

        return scheme


if __name__ == '__main__':
    test = {
        "meta_id": "215098",
        "scene_json": "",
        "design_json": "",
        "return_scheme": False
    }
    OrderedDict()
    ans = role_size_interface(test["meta_id"], "", test["scene_json"], False)
    print(ans)
