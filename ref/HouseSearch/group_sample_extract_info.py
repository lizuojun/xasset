"""
    客服线设计还原服务-样板间表单生成
"""
from Extract.extract_cache import oss_get_json, get_house_data, extract_room_layout_by_info, get_furniture_data_more, \
    download_to, oss_upload_json, oss_exist_file, get_furniture_data
from House.house_service import get_design_json_daily
import copy, json, math, os

from HouseSearch.data_oss import oss_get_json

target_furnishing_map = {
    "Meeting/sofa": ["living_group/sofa", "主沙发"],
    "Meeting/side sofa": ["living_group/side_sofa", "边沙发"],
    "Meeting/rug": ["living_group/rug", "地毯"],
    "Meeting/table": ["living_group/table", "茶几"],
    "Meeting/side table": ["living_group/side_table", "边几"],
    "Media_LivingDiningRoom/table": ["living_group/media_table", "电视柜"],
    "Meeting/art_paint": ["living_group/picture", "挂画"],
    "Meeting/lighting": ["living_group/lighting", "灯具"],
    "Dining/table": ["dining_group/table", "餐桌"],
    "Dining/chair": ["dining_group/chair", "餐椅"],
    "Dining/art_paint": ["dining_group/picture", "挂画"],
    "Dining/lighting": ["dining_group/lighting", "灯具"],
    "Cabinet/dining_cabinet": ["dining_cabinet/dining_cabinet", "餐边柜"],
    "Cabinet/shoe_cabinet": ["shoe_cabinet/shoe_cabinet", "玄关-鞋柜"],
    "Bed/bed": ["bed_group/bed", "床"],
    "Bed/side table": ["bed_group/side_table", "床头柜"],
    "Bed/lighting": ["bed_group/lighting", "灯具"],
    "Media_Bedroom/table": ["bed_media/media_table", "电视柜"],
    "Armoire/armoire": ["armoire/armoire", "衣柜"],
    "Work/table": ["work_group/table", "办公桌"],
    "Work/chair": ["work_group/chair", "办公椅"],
    "Dress/table": ["dress_group/table", "梳妆台"],
    "Dress/chair": ["dress_group/chair", "梳妆椅"],
}

SCHEME_LIVING_TABLE = {
    "decorating": {
        "name": "硬装",
        "items": [
            {
                "name": "室内门",
                "must": True,
                "type": "goods",
                "key": "swing_door",
                "model_list": []
            },
            {
                "name": "推拉门",
                "must": False,
                "key": "sliding_door",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "天花板",
                "must": True,
                "key": "ceiling",
                "type": "radio",
                "model_list": [
                    {"id": "db593061-992e-4fa9-b4f4-f4db7cc0ef25", "type": "单层吊顶",
                     "img_url": "https://gw.alicdn.com/imgextra/i4/O1CN01O28s1S1xggQvDvKQ4_!!6000000006473-2-tps-430-430.png"},
                    {"id": "9cf1d147-27a3-4b10-9ab0-7e25d3feee51", "type": "双层吊顶",
                     "img_url": "https://gw.alicdn.com/imgextra/i1/O1CN01eAKWrb1nW13BRtZa5_!!6000000005096-2-tps-430-430.png"}
                ]
            },
            {
                "name": "地面",
                "must": True,
                "key": "floor",
                "type": "radioPicture",
                "model_list": []
            },
            {
                "name": "主背景墙(沙发/床)",
                "must": False,
                "key": "main_back_wall",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "次背景墙(电视)",
                "must": False,
                "key": "rest_back_wall",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "墙面",
                "must": True,
                "type": "radioPicture",
                "key": "wall",
                "model_list": []
            },
            {
                "name": "窗户",
                "key": "window",
                "type": "goods",
                "must": False,
                "model_list": []
            }]
    },
    "custom_furniture": {
        "name": "个性化定制家具",
        "items": [
            {
                "name": "定制化电视柜",
                "key": "custom_media",
                "type": "goods",
                "must": False,
                "model_list": []
            },
            {
                "key": "custom_shelf",
                "type": "goods",
                "name": "定制化书柜",
                "must": False,
                "model_list": []
            },
            {
                "key": "custom_dining_cabinet",
                "type": "goods",
                "name": "定制化餐边柜/酒柜",
                "must": False,
                "model_list": []
            },
            {
                "key": "custom_shoe_cabinet",
                "type": "goods",
                "name": "定制化鞋柜",
                "must": False,
                "model_list": []
            }]
    },
    "furnishing": {
        "name": "主家具组合",
        "items": [
            {
                "key": "living_group",
                "must": False,
                "name": "沙发+茶几+边柜+电视柜+挂画+灯具+地毯",
                "items": [
                    {
                        "key": "sofa",
                        "type": "goods",
                        "must": False,
                        "name": "沙发",
                        "model_list": []
                    },
                    {
                        "key": "side_sofa",
                        "type": "goods",
                        "must": False,
                        "name": "边沙发",
                        "model_list": []
                    },
                    {
                        "key": "side_table",
                        "type": "goods",
                        "must": False,
                        "name": "边柜",
                        "model_list": []
                    },
                    {
                        "key": "rug",
                        "type": "goods",
                        "must": False,
                        "name": "地毯",
                        "model_list": []
                    },
                    {
                        "key": "table",
                        "type": "goods",
                        "must": False,
                        "name": "茶几",
                        "model_list": []
                    },
                    {
                        "key": "media_table",
                        "type": "goods",
                        "must": False,
                        "name": "电视柜",
                        "model_list": []
                    },
                    {
                        "key": "picture",
                        "type": "goods",
                        "must": False,
                        "name": "挂画",
                        "model_list": []
                    },
                    {
                        "key": "lighting",
                        "type": "goods",
                        "must": False,
                        "name": "灯具",
                        "model_list": []
                    }
                ]
            },
            {
                "key": "dining_group",
                "must": False,
                "name": "餐桌椅+挂画+灯具",
                "items": [
                    {
                        "key": "table",
                        "type": "goods",
                        "must": False,
                        "name": "餐桌",
                        "model_list": []
                    },
                    {
                        "key": "chair",
                        "type": "goods",
                        "must": False,
                        "name": "餐椅",
                        "model_list": []
                    },
                    {
                        "key": "picture",
                        "type": "goods",
                        "must": False,
                        "name": "挂画",
                        "model_list": []
                    },
                    {
                        "key": "lighting",
                        "type": "goods",
                        "must": False,
                        "name": "灯具",
                        "model_list": []
                    }]
            },
            {
                "key": "dining_cabinet",
                "must": False,
                "name": "餐边柜/酒柜",
                "items": [
                    {
                        "key": "dining_cabinet",
                        "type": "goods",
                        "must": False,
                        "name": "餐边柜",
                        "model_list": []
                    }
                ]
            },
            {
                "key": "shoe_cabinet",
                "name": "鞋柜",
                "must": False,
                "items": [
                    {
                        "key": "shoe_cabinet",
                        "type": "goods",
                        "name": "玄关/鞋柜",
                        "must": False,
                        "model_list": []
                    }
                ]
            }
        ]
    },
    "accessory": {
        "name": "软体&配套",
        "items": [
            {
                "key": "curtain",
                "type": "goods",
                "name": "窗帘",
                "must": False,
                "model_list": []
            },
            {
                "key": "side_table",
                "type": "goods",
                "name": "边几",
                "must": False,
                "model_list": []
            },
            {
                "key": "chair",
                "type": "goods",
                "name": "单椅",
                "must": False,
                "model_list": []
            },
            {
                "key": "plant",
                "type": "goods",
                "name": "植物",
                "must": False,
                "model_list": []
            },
            {
                "key": "picture",
                "type": "goods",
                "name": "挂画",
                "must": False,
                "model_list": []
            },
            {
                "key": "floor_lamp",
                "type": "goods",
                "name": "落地灯",
                "must": False,
                "model_list": []
            },
            {
                "key": "storage_cabinet",
                "type": "goods",
                "name": "斗柜",
                "must": False,
                "model_list": []
            }
        ]
    }
}

SCHEME_BEDROOM_TABLE = {
    "decorating": {
        "name": "硬装",
        "items": [
            {
                "name": "室内门",
                "must": True,
                "type": "goods",
                "key": "swing_door",
                "model_list": []
            },
            {
                "name": "推拉门",
                "must": False,
                "key": "sliding_door",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "天花板",
                "must": True,
                "key": "ceiling",
                "type": "radio",
                "model_list": [
                    {"id": "db593061-992e-4fa9-b4f4-f4db7cc0ef25", "type": "单层吊顶",
                     "img_url": "https://gw.alicdn.com/imgextra/i4/O1CN01O28s1S1xggQvDvKQ4_!!6000000006473-2-tps-430-430.png"},
                    {"id": "9cf1d147-27a3-4b10-9ab0-7e25d3feee51", "type": "双层吊顶",
                     "img_url": "https://gw.alicdn.com/imgextra/i1/O1CN01eAKWrb1nW13BRtZa5_!!6000000005096-2-tps-430-430.png"}
                ]
            },
            {
                "name": "地面",
                "must": True,
                "key": "floor",
                "type": "radioPicture",
                "model_list": []
            },
            {
                "name": "主背景墙(沙发/床)",
                "must": False,
                "key": "main_back_wall",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "次背景墙(电视)",
                "must": False,
                "key": "rest_back_wall",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "墙面",
                "must": True,
                "type": "radioPicture",
                "key": "wall",
                "model_list": []
            },
            {
                "name": "窗户",
                "key": "window",
                "type": "goods",
                "must": False,
                "model_list": []
            }]
    }
    ,
    "custom_furniture": {
        "name": "个性化定制家具",
        "items": [
            {
                "name": "定制化衣柜",
                "key": "custom_cabinet",
                "type": "goods",
                "must": False,
                "model_list": []
            },
            {
                "name": "定制化梳妆台",
                "key": "custom_work",
                "type": "goods",
                "must": False,
                "model_list": []
            }]
    },
    "furnishing": {
        "name": "主家具组合",
        "items": [
            {
                "name": "床+床头柜",
                "key": "bed_group",
                "must": False,
                "items": [
                    {
                        "key": "bed",
                        "name": "床",
                        "type": "goods",
                        "must": False,
                        "model_list": []
                    },
                    {
                        "key": "side_table",
                        "name": "床头柜",
                        "type": "goods",
                        "must": False,
                        "model_list": []
                    },
                    {
                        "key": "lighting",
                        "name": "灯具",
                        "type": "goods",
                        "must": False,
                        "model_list": []
                    }
                ]
            },
            {
                "key": "bed_media",
                "name": "电视柜",
                "must": False,
                "items": [
                    {
                        "name": "电视柜",
                        "must": False,
                        "type": "goods",
                        "key": "media_table",
                        "model_list": []
                    }
                ]
            },
            {
                "key": "armoire",
                "name": "衣柜",
                "must": False,
                "items": [
                    {
                        "name": "衣柜",
                        "must": False,
                        "type": "goods",
                        "key": "armoire",
                        "model_list": []
                    }
                ]
            },
            {
                "key": "work_group",
                "name": "书桌+椅子",
                "must": False,
                "items": [
                    {
                        "name": "办公桌",
                        "must": False,
                        "type": "goods",
                        "key": "table",
                        "model_list": []
                    },
                    {
                        "name": "办公椅",
                        "must": False,
                        "type": "goods",
                        "key": "chair",
                        "model_list": []
                    }
                ]
            },
            {
                "key": "dress_group",
                "name": "梳妆台+椅子",
                "must": False,
                "items": [
                    {
                        "name": "梳妆台",
                        "must": False,
                        "type": "goods",
                        "key": "table",
                        "model_list": []
                    },
                    {
                        "name": "椅子",
                        "type": "goods",
                        "key": "chair",
                        "must": False,
                        "model_list": []
                    }
                ]
            }]
    },
    "accessory": {
        "name": "软体&配套",
        "items": [
            {
                "name": "窗帘",
                "must": False,
                "key": "curtain",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "地毯",
                "must": False,
                "key": "rug",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "床头柜吊灯",
                "must": False,
                "key": "lighting",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "植物",
                "must": False,
                "key": "plant",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "挂画",
                "must": False,
                "key": "picture",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "单椅",
                "must": False,
                "key": "chair",
                "type": "goods",
                "model_list": []
            },
            {
                "name": "斗柜",
                "must": False,
                "key": "storage_cabinet",
                "type": "goods",
                "model_list": []
            }

        ]
    }
}

category_path = os.path.join(os.path.dirname(__file__), "../Furniture/furniture_refer_dict.json")
category_change = json.load(open(category_path))['category_id']

material_jid_info = {}


def check_cate(cate_id):
    for i in category_change:
        if category_change[i] == cate_id:
            if '/' in i:
                i = i.replace('/', '-')
            return i
    return ""


def check_cate_type(obj_type):
    if "wall fabric" in obj_type:
        return "墙布"
    if 'plant' in obj_type:
        return "植物"
    return obj_type


def get_furniture_detail_info(model_id):
    obj_type, _, _, _, _, obj_category_id = get_furniture_data_more(model_id)
    search_type = check_cate(obj_category_id)
    if len(search_type) == 0:
        search_type = check_cate_type(obj_type)
    return search_type


def get_scheme_table_info(table_list, now_type):
    for item_data in table_list:
        if item_data["key"] == now_type:
            return item_data
    else:
        return {}


def extract_hard_deco(temp_table, room_info, material_info):
    decorating_table = temp_table['decorating']['items']

    for key in ["door", "win", "floor", "wall", "background"]:
        if key not in material_info:
            material_info[key] = {}

    for entry_key in material_info["door"]:
        for door_data in material_info["door"][entry_key]:
            if 'id' not in door_data:
                continue
            model_id = door_data['id']
            search_type = get_furniture_detail_info(model_id)
            if search_type in ["单开门", "室内门", "平开门"]:
                now_type = "swing_door"
            else:
                now_type = "sliding_door"

            now_type_list = get_scheme_table_info(decorating_table, now_type)
            model_list = [i["id"] for i in now_type_list['model_list']]
            if model_id in model_list:
                continue

            instance = {
                "id": door_data['id'],
                "type": search_type,
                "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + door_data['id'] + "/iso.jpg"
            }
            now_type_list['model_list'].append(instance)

    for win_data in material_info["win"]:
        if 'id' not in win_data:
            continue
        model_id = win_data['id']

        now_type_list = get_scheme_table_info(decorating_table, 'window')
        model_list = [i["id"] for i in now_type_list['model_list']]
        if model_id in model_list:
            continue
        search_type = get_furniture_detail_info(model_id)

        instance = {
            "id": win_data['id'],
            "type": search_type,
            "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + win_data['id'] + "/iso.jpg"
        }
        now_type_list['model_list'].append(instance)

    # floor
    for floor_data in material_info['floor']:
        if floor_data['area'] < 1:
            continue
        model_id = floor_data['jid']

        if model_id not in material_jid_info:
            material_jid_info[model_id] = floor_data

        now_type_list = get_scheme_table_info(decorating_table, 'floor')
        model_list = [i["id"] for i in now_type_list['model_list']]
        if model_id in model_list:
            continue

        search_type = get_furniture_detail_info(model_id)

        instance = {
            "id": floor_data['jid'],
            "type": search_type,
            "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + floor_data['jid'] + "/iso.jpg"
        }
        now_type_list['model_list'].append(instance)

    # wall
    for wall_data in material_info['wall']:
        if wall_data['area'] < 1:
            continue
        model_id = wall_data['jid']
        color_data = ""
        if wall_data["colorMode"] == "color":
            if wall_data["color"]:
                color_data = "rgb(%d,%d,%d)" % (wall_data["color"][0], wall_data["color"][1], wall_data["color"][2])

        if model_id not in material_jid_info:
            material_jid_info[model_id] = wall_data

        now_type_list = get_scheme_table_info(decorating_table, 'wall')
        model_list = [i["id"] for i in now_type_list['model_list']]
        if model_id in model_list:
            continue
        search_type = get_furniture_detail_info(model_id)

        instance = {
            "id": wall_data['jid'],
            "type": search_type,
            "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + wall_data['jid'] + "/iso.jpg"
        }
        if len(color_data) > 0:
            instance["color"] = color_data

        now_type_list['model_list'].append(instance)

    # back_wall
    for wall_data in material_info['background']:
        model_id = wall_data['id']
        if "Functional" in wall_data and wall_data["Functional"] in ["Meeting", "Bed"] :
            now_type_list = get_scheme_table_info(decorating_table, 'main_back_wall')
        elif "Functional" in wall_data and wall_data["Functional"] in ["Media"]:
            now_type_list = get_scheme_table_info(decorating_table, 'rest_back_wall')
        else:
            now_type_list = get_scheme_table_info(decorating_table, 'main_back_wall')

        model_list = [i["id"] for i in now_type_list['model_list']]

        if model_id in model_list:
            continue

        if model_id not in material_jid_info:
            material_jid_info[model_id] = wall_data

        search_type = get_furniture_detail_info(model_id)

        instance = {
            "id": wall_data['id'],
            "type": search_type,
            "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + wall_data['id'] + "/iso.jpg"
        }
        now_type_list['model_list'].append(instance)


def check_cabinet_detail_info(obj, dining_group=None, main_door=None):
    # 餐边柜/酒柜
    # 鞋柜/玄关柜
    # 斗柜
    search_type = get_furniture_detail_info(obj['id'])
    if search_type in ["酒柜", "餐边柜"]:
        obj['refine_role'] = "dining_cabinet"
    elif search_type in ["鞋柜", "玄关柜"]:
        obj['refine_role'] = "shoe_cabinet"
    elif search_type in ["边柜", "斗柜", "储物柜/架"]:
        obj['refine_role'] = "storage"
    elif search_type in ["衣柜"]:
        obj['refine_role'] = "armoire"
        obj['refine_type'] = "Armoire"
    else:
        print(obj['id'], search_type)
    pass


def check_dress_group_info(obj_id):
    # 梳妆台
    search_type = get_furniture_detail_info(obj_id)
    if search_type in ["梳妆台"]:
        return True
    else:
        return False


def extract_furnishing(temp_scheme_table, room_info, room_group, if_bed_room=False):
    furnishing_table = temp_scheme_table['furnishing']['items']
    accessory_table = temp_scheme_table['accessory']['items']
    # livingDiningRoom:
    main_group_list = []
    group_list = {}
    for group in room_group:
        if group['type'] not in group_list:
            group_list[group['type']] = []

        if group['type'] == "Media":
            if if_bed_room:
                group['refine_type'] = group['type'] + "_Bedroom"
            else:
                group['refine_type'] = group['type'] + "_LivingDiningRoom"

        if group['type'] == "Work" and if_bed_room:
            obj_main = group['obj_main']
            if check_dress_group_info(obj_main):
                group['refine_type'] = "Dress"

        if group['type'] == 'Meeting' or group['type'] == 'Dining':
            main_group_list.append(group)

        group_list[group['type']].append(group)

    addition_group = {
        "curtain": [],  #
        "side_table": [],  #
        "chair": [],  #
        "plant": [],  #
        "picture": [],  #
        "floor_lamp": [],
        "light": [],  #
        "storage_cabinet": [],
        "rug": []  #
    }

    # 公共挂画
    if 'Wall' in group_list:
        obj_list = group_list['Wall'][0]['obj_list']
        for obj in obj_list:
            if obj['type'] in ['accessory/accessory - wall-attached', 'art/art - wall-attached']:
                pos_2d = [obj['position'][0], obj['position'][2]]
                for main_group in main_group_list:
                    main_obj_jid = main_group['obj_main']
                    main_obj_2d = [main_group['position'][0] + main_group['offset'][0],
                                   main_group['position'][2] + main_group['offset'][2]]
                    if math.sqrt((pos_2d[0] - main_obj_2d[0]) ** 2 + (pos_2d[1] - main_obj_2d[1]) ** 2) < 0.8:
                        obj['relate'] = main_group['obj_main']
                        obj['relate_group'] = main_group['type']
                        if main_group['type'] == 'Meeting':
                            obj['relate_role'] = "sofa"
                        elif main_group['type'] == 'Dining':
                            obj['relate_role'] = "table"
                        obj['if_in_group'] = True
                        obj['role'] = 'art_paint'
                        main_group['obj_list'].append(obj)

                if obj['role'] == 'art_paint':
                    continue
                else:
                    addition_group['picture'].append(obj)

    # plant
    if 'Floor' in group_list:
        obj_list = group_list['Floor'][0]['obj_list']
        for obj in obj_list:
            if 'plant' in obj['type']:
                addition_group['plant'].append(obj)

    # light
    if 'Ceiling' in group_list:
        obj_list = group_list['Ceiling'][0]['obj_list']
        for obj in obj_list:
            if 'light' in obj['type']:
                if 'relate_role' not in obj:
                    obj['relate_role'] = ''
                if 'relate_group' not in obj:
                    obj['relate_group'] = ''

                obj['role'] = "lighting"
                if obj['relate_group'] in group_list:
                    group_list[obj['relate_group']][0]['obj_list'].append(obj)
                elif obj['relate_role'] == "sofa" and "Meeting" in group_list:
                    group_list["Meeting"][0]['obj_list'].append(obj)
                elif obj['relate_role'] == "bed" and "Bed" in group_list:
                    group_list["Bed"][0]['obj_list'].append(obj)
                elif obj['relate_role'] == "table" and "Dining" in group_list:
                    group_list["Dining"][0]['obj_list'].append(obj)
                else:
                    addition_group['light'].append(obj)

    # curtain
    if 'Window' in group_list:
        obj_list = group_list['Window'][0]['obj_list']
        for obj in obj_list:
            if 'curtain' in obj['type']:
                addition_group['curtain'].append(obj)

    # side_table chair
    if 'Rest' in group_list:
        for group in group_list['Rest']:
            for obj in group['obj_list']:
                if obj['role'] == 'table':
                    addition_group['side_table'].append(obj)
                elif obj['role'] == 'chair':
                    addition_group['chair'].append(obj)

    # storage_cabinet
    if 'Cabinet' in group_list:
        for group in group_list['Cabinet']:
            for obj in group['obj_list']:
                if obj['role'] != 'cabinet':
                    continue
                check_cabinet_detail_info(obj)
                if 'refine_role' in obj and obj['refine_role'] == 'storage':
                    addition_group['storage_cabinet'].append(obj)

    # 更新furnishing
    for group_type in group_list:
        for group in group_list[group_type]:
            group_type_name = group_type
            if "refine_type" in group:
                group_type_name = group['refine_type']

            for obj in group['obj_list']:
                model_id = obj['id']
                role_type_name = obj['role']
                if "refine_role" in obj:
                    role_type_name = obj['refine_role']

                check_name = group_type_name + "/" + role_type_name
                if check_name not in target_furnishing_map:
                    continue
                first_type_name, second_type_name = target_furnishing_map[check_name][0].split('/')

                now_type_list = get_scheme_table_info(furnishing_table, first_type_name)
                if not now_type_list:
                    continue

                now_second_type_list = get_scheme_table_info(now_type_list['items'], second_type_name)

                model_list = [i["id"] for i in
                              now_second_type_list['model_list']]
                if model_id in model_list:
                    continue

                search_type = get_furniture_detail_info(obj['id'])
                now_second_type_list['model_list'].append({
                    "id": model_id,
                    "type": search_type,
                    "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + model_id + "/iso.jpg"
                })

    # 更新 accessory
    for item_info in accessory_table:
        item_key = item_info["key"]
        now_type_list = get_scheme_table_info(accessory_table, item_key)
        if item_key in addition_group:
            for obj in addition_group[item_key]:
                model_id = obj['id']
                model_list = [i["id"] for i in now_type_list['model_list']]
                if model_id in model_list:
                    continue

                search_type = get_furniture_detail_info(obj['id'])
                now_type_list['model_list'].append({
                    "id": model_id,
                    "type": search_type,
                    "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + model_id + "/iso.jpg"
                })


def get_room_custom_cache(house_id, target_room_id):
    design_url = get_design_json_daily(house_id)
    house_para, house_data = get_house_data(house_id, design_url, '')

    # 定制材质更新
    # house_data_deco = get_house_data_daily(design_url)['data']

    room_info = {}
    for target_room_info in house_data['room']:
        if target_room_info['id'] == target_room_id:
            room_info = target_room_info

    # for target_room_info in house_data_deco['room']:
    # if target_room_info['id'] == target_room_id:
    #     room_info['decorate_shejijia_info'] = target_room_info['decorate_info']
    #     room_info['door_shejijia_info'] = target_room_info['door_info']
    #     room_info['window_shejijia_info'] = target_room_info['window_info']
    #     room_info['baywindow_shejijia_info'] = target_room_info['baywindow_info']
    #     room_info['hole_shejijia_info'] = target_room_info['hole_info']

    sample_layout, sample_group = extract_room_layout_by_info(room_info)

    return room_info, sample_layout


def extract_sample_room_custom_detail_info(house_id, room_id, fix_room_type=None):
    if '-' not in room_id:
        raise ValueError("extract_sample_room_custom_detail_info input param room_id (%s) value error " % room_id)


    room_info, room_group = get_room_custom_cache(house_id, room_id)
    room_type = room_info["type"]
    if fix_room_type:
        room_type = fix_room_type
    # 定制
    if room_type in ["LivingDiningRoom", "LivingRoom", "Corridor"]:
        bed_flag = False
    elif room_type in ["MasterBedroom", "Bedroom", "SecondBedroom"]:
        bed_flag = True
    else:
        return {}

    if not bed_flag:
        temp_scheme_table = copy.deepcopy(SCHEME_LIVING_TABLE)
    else:
        temp_scheme_table = copy.deepcopy(SCHEME_BEDROOM_TABLE)

    # 硬装
    extract_hard_deco(temp_scheme_table, room_info, room_info['material_info'])

    # 软装
    extract_furnishing(temp_scheme_table, room_info, room_group['layout_scheme'][0]['group'], bed_flag)

    return temp_scheme_table


def show_results(extract_table, show_dir):
    for item_key in extract_table:
        if item_key == "style":
            continue
        item = extract_table[item_key]
        for first_item_key in item['items']:
            first_item = item['items'][first_item_key]
            base_path = os.path.join(show_dir, item["name"], first_item['name'])

            if not os.path.exists(base_path):
                os.makedirs(base_path)

            if "model_list" in first_item:
                for second_item in first_item['model_list']:
                    if '/' in second_item['type']:
                        second_item['type'] = second_item['type'].replace('/', '-')
                    obj_id = second_item['id']
                    src_url = "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + obj_id + "/iso.jpg"
                    download_to(src_url, os.path.join(base_path, obj_id + "_" + second_item['type'] + ".jpg"))
                    if not os.path.exists(os.path.join(base_path, obj_id + "_" + second_item['type'] + ".jpg")):
                        with open(os.path.join(base_path, obj_id + "_" + second_item['type'] + ".txt"), "w") as f:
                            f.write("")
            else:
                for second_item_key in first_item['items']:
                    second_item = first_item['items'][second_item_key]
                    for third_item in second_item['model_list']:
                        if '/' in third_item['type']:
                            third_item['type'] = third_item['type'].replace('/', '-')

                        if 'id' in third_item:
                            obj_id = third_item['id']
                            src_url = "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" + obj_id + "/iso.jpg"

                            download_to(src_url, os.path.join(base_path,
                                                              obj_id + "_" + second_item['name'] + "_" + third_item[
                                                                  'type'] + ".jpg"))
                            if not os.path.exists(os.path.join(base_path,
                                                               obj_id + "_" + second_item['name'] + "_" + third_item[
                                                                   'type'] + ".jpg")):
                                with open(os.path.join(base_path, obj_id + "_" + second_item['name'] + third_item[
                                    'type'] + ".txt"),
                                          "w") as f:
                                    f.write("")


def build_sample_extract_info(house_id, design_url, room_list=[], reload=True):
    if not reload and oss_exist_file("rd_temp/extract_info/" + house_id + ".json", "ihome-alg-layout"):
        return oss_get_json("rd_temp/extract_info/" + house_id + ".json", "ihome-alg-layout")

    house_table = {}
    # for house_id in check_house_id_list:
    _, house_data = get_house_data(house_id, design_url, reload=True)
    for room_data in house_data['room']:
        room_id = room_data['id']
        if len(room_list) == 0:
            if room_data['type'] in ["LivingDiningRoom", 'LivingRoom', "MasterBedroom", "Bedroom", "SecondBedroom"]:
                table = extract_sample_room_custom_detail_info(house_id, room_id, room_data['type'])
                house_table[room_id] = table
        else:
            if room_id in room_list:
                table = extract_sample_room_custom_detail_info(house_id, room_id, room_data['type'])
                house_table[room_id] = table

    if reload or oss_exist_file("rd_temp/extract_info/" + house_id + ".json", "ihome-alg-layout"):
        oss_upload_json("rd_temp/extract_info/" + house_id + ".json", house_table, "ihome-alg-layout")

    return house_table


def combine_extract_base_advisor_scheme_table(base_table, extract_table):
    if "decorating" in base_table and "decorating" in extract_table:
        for base_item in base_table["decorating"]["items"]:
            base_item_key = base_item["key"]

            target_extract_table = get_scheme_table_info(extract_table["decorating"]["items"], base_item_key)
            if "model_list" in target_extract_table:
                target_extract_model_list = target_extract_table["model_list"]
            else:
                target_extract_model_list = []

            if len(target_extract_model_list) > 0:
                if base_item_key != "ceiling":
                    base_item["model_list"] += target_extract_model_list
                    base_item["initialValue"] = target_extract_model_list[0]["id"]
            else:
                base_item["initialValue"] = ""

    if "custom_furniture" in base_table and "custom_furniture" in extract_table:
        for base_item in base_table["custom_furniture"]["items"]:
            base_item_key = base_item["key"]

            target_extract_table = get_scheme_table_info(extract_table["custom_furniture"]["items"], base_item_key)
            if "model_list" in target_extract_table:
                target_extract_model_list = target_extract_table["model_list"]
            else:
                target_extract_model_list = []
            if len(target_extract_model_list) > 0:
                base_item["model_list"] += target_extract_model_list
                base_item["initialValue"] = target_extract_model_list[0]["id"]
            else:
                base_item["initialValue"] = ""

    if "accessory" in base_table and "accessory" in extract_table:
        for base_item in base_table["accessory"]["items"]:
            base_item_key = base_item["key"]

            target_extract_table = get_scheme_table_info(extract_table["accessory"]["items"], base_item_key)
            if "model_list" in target_extract_table:
                target_extract_model_list = target_extract_table["model_list"]
            else:
                target_extract_model_list = []
            if len(target_extract_model_list) > 0:
                base_item["model_list"] += target_extract_model_list
                base_item["initialValue"] = target_extract_model_list[0]["id"]
            else:
                base_item["initialValue"] = ""

    if "furnishing" in base_table and "furnishing" in extract_table:
        # group
        for base_item in base_table["furnishing"]["items"]:
            base_item_key = base_item["key"]
            target_extract_base_items = get_scheme_table_info(extract_table["furnishing"]["items"], base_item_key)

            for base_sub_item in base_item["items"]:
                base_sub_item_key = base_sub_item["key"]
                if "items" in target_extract_base_items:
                    target_extract_sub_table = get_scheme_table_info(target_extract_base_items["items"],
                                                                     base_sub_item_key)
                    if "model_list" in target_extract_sub_table:
                        target_extract_model_list = target_extract_sub_table["model_list"]
                    else:
                        target_extract_model_list = []
                else:
                    target_extract_model_list = []

                if len(target_extract_model_list) > 0:
                    base_sub_item["model_list"] += target_extract_model_list
                    base_sub_item["initialValue"] = target_extract_model_list[0]["id"]
                else:
                    base_sub_item["initialValue"] = ""

    return base_table


def get_sample_extract_info_with_room_type(house_id, design_url, reload=False):
    if len(house_id) == 0:
        return {}

    if oss_exist_file("rd_temp/extract_info/" + house_id + ".json", "ihome-alg-layout") and not reload:
        house_table = oss_get_json("rd_temp/extract_info/" + house_id + ".json", "ihome-alg-layout")

    else:
        house_table = build_sample_extract_info(house_id, design_url, reload=reload)

    # 检查尺寸
    for room_key in house_table:
        table_data = house_table[room_key]
        if "custom_furniture" not in table_data:
            break

        for item in table_data["custom_furniture"]["items"]:
            item_key = item["key"]
            if item_key in ["picture", "curtain"]:
                need_flap = True
            else:
                need_flap = False
            for model in item["model_list"]:
                key = model["type"]
                if "(" in key:
                    key = key.split("(")[0]
                jid = model["id"]
                obj_type, obj_style_en, obj_size = get_furniture_data(jid)

                if need_flap:
                    size = [obj_size[0] / 10, obj_size[1] / 10]
                else:
                    size = [obj_size[0] / 10, obj_size[2] / 10]

                width = int(size[0]) * 100
                length = int(size[1]) * 100
                model["width"] = width
                model["length"] = length
                model["type"] = key

        for main_item in table_data["furnishing"]["items"]:
            for item in main_item["items"]:
                item_key = item["key"]
                if item_key in ["picture", "curtain"]:
                    need_flap = True
                else:
                    need_flap = False
                for model in item["model_list"]:
                    key = model["type"]
                    if "(" in key:
                        key = key.split("(")[0]
                    jid = model["id"]
                    obj_type, obj_style_en, obj_size = get_furniture_data(jid)

                    if need_flap:
                        size = [obj_size[0] / 10, obj_size[1] / 10]
                    else:
                        size = [obj_size[0] / 10, obj_size[2] / 10]

                    width = int(size[0]) * 100
                    length = int(size[1]) * 100
                    model["width"] = width
                    model["length"] = length
                    model["type"] = key

        for item in table_data["accessory"]["items"]:
            item_key = item["key"]
            if item_key in ["picture", "curtain"]:
                need_flap = True
            else:
                need_flap = False
            for model in item["model_list"]:
                key = model["type"]
                if "(" in key:
                    key = key.split("(")[0]
                jid = model["id"]
                obj_type, obj_style_en, obj_size = get_furniture_data(jid)

                if need_flap:
                    size = [obj_size[0] / 10, obj_size[1] / 10]
                else:
                    size = [obj_size[0] / 10, obj_size[2] / 10]

                width = int(size[0]) * 100
                length = int(size[1]) * 100
                model["width"] = width
                model["length"] = length
                model["type"] = key

    out_table = {"LivingDiningRoom": {}, "Bedroom": {}}
    for room_key in house_table:

        if not "furnishing" in house_table[room_key]:
            continue
        item_table_list = house_table[room_key]["furnishing"]["items"]
        target_room_type = ""
        for item in item_table_list:
            if "living_group" == item["key"]:
                target_room_type = "LivingDiningRoom"
                break
            elif "bed_group" == item["key"]:
                target_room_type = "Bedroom"
                break
            else:
                target_room_type = ""

        if target_room_type in ["LivingDiningRoom", "LivingRoom"]:
            out_table["LivingDiningRoom"] = house_table[room_key]
        elif target_room_type in ["Bedroom", "MasterBedroom"]:
            out_table["Bedroom"] = house_table[room_key]

    base_json = oss_get_json("rd_temp/extract_info/all/table.json", "ihome-alg-layout")
    for room_style_key in base_json["form_options"]:
        now_items = base_json["form_options"][room_style_key]
        if "Bedroom" in room_style_key:
            combine_extract_base_advisor_scheme_table(now_items, out_table["Bedroom"])
        else:
            combine_extract_base_advisor_scheme_table(now_items, out_table["LivingDiningRoom"])

    return base_json


def merge_info_json_data(global_json, temp_json):
    # 硬装
    for item_info in global_json["decorating"]["items"]:  # 子项一级类目
        type_name = item_info["key"]
        temp_decorating_list = get_scheme_table_info(temp_json["decorating"]["items"], type_name)

        if temp_decorating_list["model_list"]:
            used_jid_list = [i['id'] for i in item_info["model_list"]]
            for model in temp_decorating_list["model_list"]:
                if len(model["id"]) > 0 and model["id"] in used_jid_list:
                    continue
                item_info["model_list"].append(model)

    # 定制
    for item_info in global_json["custom_furniture"]["items"]:  # 子项一级类目
        type_name = item_info["key"]
        temp_custom_list = get_scheme_table_info(temp_json["custom_furniture"]["items"], type_name)

        if temp_custom_list["model_list"]:
            used_jid_list = [i['id'] for i in item_info["model_list"]]
            for model in temp_custom_list["model_list"]:
                if len(model["id"]) > 0 and model["id"] in used_jid_list:
                    continue
                item_info["model_list"].append(model)

    # 软装
    for item_info in global_json["furnishing"]["items"]:  # 子项一级类目
        first_type_name = item_info["key"]
        add_temp_fur_list = get_scheme_table_info(temp_json["furnishing"]["items"], first_type_name)
        for item_sub_info in item_info["items"]:  # 子项二级类目
            second_type_name = item_sub_info["key"]
            add_temp_fur_sub_list = get_scheme_table_info(add_temp_fur_list["items"], second_type_name)

            if add_temp_fur_sub_list["model_list"]:
                used_jid_list = [i['id'] for i in
                                 item_sub_info["model_list"]]
                for model in add_temp_fur_sub_list["model_list"]:
                    if len(model["id"]) > 0 and model["id"] in used_jid_list:
                        continue
                    item_sub_info["model_list"].append(model)

    # 配件
    for item_info in global_json["accessory"]["items"]:  # 子项一级类目
        type_name = item_info["key"]
        temp_acc_list = get_scheme_table_info(temp_json["accessory"]["items"], type_name)

        if temp_acc_list["model_list"]:
            used_jid_list = [i['id'] for i in item_info["model_list"]]
            for model in temp_acc_list["model_list"]:
                if len(model["id"]) > 0 and model["id"] in used_jid_list:
                    continue
                item_info["model_list"].append(model)


def check_model_exists(find_list, key):
    for item in find_list:
        if item["id"] == key:
            return True
    return False


def build_customer_sample_info_from_layout(room_data, layout_info, now_table_param, room_type, style):
    if style == "Contemporary":
        style = "Modern"
    else:
        style = "Nordic"

    if "ingRoom" in room_type:
        room_type = "LivingDiningRoom"
    else:
        room_type = "Bedroom"

    all_table_path = os.path.join(os.path.dirname(__file__), "source/table.json")
    all_table = json.load(open(all_table_path, "r"))
    base_table = all_table["form_options"][room_type + "_" + style]

    floor_used_info = None
    wall_used_info = None
    door_used_info = None
    if "construct_info" in room_data:
        used_construct_info = room_data["construct_info"]
        try:
            if "Floor" in used_construct_info and len(used_construct_info["Floor"]) > 0:
                floor_used_info = used_construct_info["Floor"][0]["material"]["main"]
            if "Wall" in used_construct_info and len(used_construct_info["Wall"]) > 0:
                wall_used_info = used_construct_info["Wall"][0]["segments"][0]["material"]["main"]
            if "Door" in used_construct_info and len(used_construct_info["Door"]) > 0:
                for door in used_construct_info["Door"]:
                    if door["length"] < 1.0:
                        door_used_info = door["obj_info"]
        except:
            pass

    # 硬装替换
    if not now_table_param:
        if room_type == "Bedroom":
            now_table_param = copy.deepcopy(SCHEME_BEDROOM_TABLE)
        else:
            now_table_param = copy.deepcopy(SCHEME_LIVING_TABLE)

    for item in now_table_param["decorating"]["items"]:
        item_key = item["key"]
        if "model_list" in item and len(item["model_list"]) > 0:
            base_items = get_scheme_table_info(base_table["decorating"]["items"], item_key)
            if base_items and "model_list" in base_items and len(base_items["model_list"]) > 0:
                base_items["initialValue"] = item["model_list"][0]["id"]
                if not check_model_exists(base_items["model_list"], base_items["initialValue"]):
                    base_items["model_list"].insert(0, {"type": "当前模型", "id": base_items["initialValue"],
                                                        "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                   base_items["initialValue"] + "/iso.jpg"})
                    if "color" in item["model_list"][0]:
                        base_items["model_list"][0]["color"] = item["model_list"][0]["color"]

        else:
            if item_key == "swing_door" and door_used_info:
                base_items = get_scheme_table_info(base_table["decorating"]["items"], item_key)
                if base_items and "model_list" in base_items and len(base_items["model_list"]) > 0:
                    base_items["initialValue"] = door_used_info["jid"]
                    base_items["model_list"].insert(0, {"type": "当前模型", "id": base_items["initialValue"],
                                                        "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                   base_items["initialValue"] + "/iso.jpg"})
            elif item_key == "wall" and wall_used_info:
                base_items = get_scheme_table_info(base_table["decorating"]["items"], item_key)
                if base_items and "model_list" in base_items and len(base_items["model_list"]) > 0:
                    base_items["initialValue"] = wall_used_info["jid"]
                    base_items["model_list"].insert(0, {"type": "当前模型", "id": base_items["initialValue"],
                                                        "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                   base_items["initialValue"] + "/iso.jpg"})
                    if "colorMode" in wall_used_info and wall_used_info["colorMode"] == "color":
                        base_items["model_list"][0]["color"] = "rgb(%d,%d,%d)" % (
                        wall_used_info["color"][0], wall_used_info["color"][1], wall_used_info["color"][2])

            elif item_key == "floor" and floor_used_info:
                base_items = get_scheme_table_info(base_table["decorating"]["items"], item_key)
                if base_items and "model_list" in base_items and len(base_items["model_list"]) > 0:
                    base_items["initialValue"] = floor_used_info["jid"]
                    base_items["model_list"].insert(0, {"type": "当前模型", "id": base_items["initialValue"],
                                                        "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                   base_items["initialValue"] + "/iso.jpg"})

    # 软装写入
    if layout_info:
        for group in layout_info["layout_scheme"][0]["group"]:
            group_type = group["type"]
            if group_type == "Media":
                group_type = group_type + "_" + room_type

            for obj in group["obj_list"]:
                obj_role = obj["role"]
                if group_type == "Cabinet":
                    if "zone" in group:
                        if group["zone"] == "DiningRoom":
                            obj_role = "dining_cabinet"
                        elif group["zone"] == "Hallway":
                            obj_role = "shoe_cabinet"

                key = group_type + "/" + obj_role
                if key in target_furnishing_map:
                    target_item_key = target_furnishing_map[key][0]
                    main_key, sub_key = target_item_key.split('/')
                    main_items = get_scheme_table_info(base_table["furnishing"]["items"], main_key)

                    if main_items and "items" in main_items:
                        sub_items = get_scheme_table_info(main_items["items"], sub_key)
                        if sub_items and "model_list" in sub_items:
                            sub_items["initialValue"] = obj["id"]
                            if not check_model_exists(sub_items["model_list"], obj["id"]):
                                sub_items["model_list"].insert(0, {"type": "当前模型", "id": obj["id"],
                                                                   "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                              obj["id"] + "/iso.jpg"})

        # 配饰写入
        for group in layout_info["layout_scheme"][0]["group"]:
            group_type = group["type"]
            # 窗帘
            if group_type == "Window":
                main_items = get_scheme_table_info(base_table["accessory"]["items"], "curtain")
                for obj in group["obj_list"]:
                    if "curtain" in obj["type"]:
                        if main_items and "items" in main_items:
                            main_items["initialValue"] = obj["id"]
                            if not check_model_exists(main_items["model_list"], obj["id"]):
                                main_items["model_list"].insert(0, {"type": "当前模型", "id": obj["id"],
                                                                    "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                               obj["id"] + "/iso.jpg"})
            elif group_type == "Floor":
                main_items = get_scheme_table_info(base_table["accessory"]["items"], "plant")
                for obj in group["obj_list"]:
                    if main_items and "items" in main_items:
                        main_items["initialValue"] = obj["id"]
                        if not check_model_exists(main_items["model_list"], obj["id"]):
                            main_items["model_list"].insert(0, {"type": "当前模型", "id": obj["id"],
                                                                "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                           obj["id"] + "/iso.jpg"})
            elif group_type == "Ceiling":
                for obj in group["obj_list"]:
                    main_group = obj["relate_group"]
                    role = "lighting"
                    if main_group + "/" + role in target_furnishing_map:
                        target_item_key = target_furnishing_map[main_group + "/" + role][0]
                        main_key, sub_key = target_item_key.split('/')
                        main_items = get_scheme_table_info(base_table["furnishing"]["items"], main_key)

                        if main_items and "items" in main_items:
                            sub_items = get_scheme_table_info(main_items["items"], sub_key)
                            if sub_items and "model_list" in sub_items:
                                sub_items["initialValue"] = obj["id"]
                                if not check_model_exists(sub_items["model_list"], obj["id"]):
                                    sub_items["model_list"].insert(0, {"type": "当前模型", "id": obj["id"],
                                                                       "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                                  obj["id"] + "/iso.jpg"})
            elif group_type == "Wall":
                for obj in group["obj_list"]:
                    main_group = obj["relate_group"]

                    role = "art_paint"
                    if main_group + "/" + role in target_furnishing_map:
                        target_item_key = target_furnishing_map[main_group + "/" + role][0]
                        main_key, sub_key = target_item_key.split('/')
                        main_items = get_scheme_table_info(base_table["furnishing"]["items"], main_key)

                        if main_items and "items" in main_items:
                            sub_items = get_scheme_table_info(main_items["items"], sub_key)
                            if sub_items and "model_list" in sub_items:
                                sub_items["initialValue"] = obj["id"]
                                if not check_model_exists(sub_items["model_list"], obj["id"]):
                                    sub_items["model_list"].insert(0, {"type": "当前模型", "id": obj["id"],
                                                                       "img_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/" +
                                                                                  obj["id"] + "/iso.jpg"})

    return base_table


if __name__ == '__main__':
    # 单个解析：
    design_list = [
                   "f5c7153a-6457-45c9-ae3e-9428acf6c0f6",
                   "24f05ffb-0898-4408-98bc-c2dbb8a757ef",
                   "839d2b3d-06f6-4ab7-b3e9-e5ebcc035a7f",
                   "f3c39b41-decc-47d0-a6a5-aa279e2ac8e4",
    "7641c960-994d-4a9e-89ca-0c2528c41ae9",
    "a7c14501-b743-4397-b850-017360bb0002",
    "4312dd6a-ac45-4297-b334-b042922c38ad",
    "cffb9d94-6367-4b55-a312-b14648540ede",
    "7cafdcb4-9ce9-45fd-9748-3a72b67025a6",
    "8d6cd145-b2fa-4709-9e62-7165e6882fee",
    "ea48de3a-42b2-40f1-8fef-f4474843bac0"]
    #for i in design_list:
    design_id = "a7c14501-b743-4397-b850-017360bb0002"
    design_url = get_design_json_daily(design_id)
    table = get_sample_extract_info_with_room_type(design_id, design_url, True)
    print(table)
    1 / 0
    #
    # 1 / 0
    # a = get_sample_extract_info_with_room_type("bf3c4382-4b70-4c7e-9225-d7336b6e307a", "https://jr-prod-cms-assets.oss-cn-beijing.aliyuncs.com/design/2021-08-26/json/fb2155a0-0e63-4d52-a328-2e25cae1c875.json")
    # print(a)
    out_json = {}
    for file_name in ["./temp/现代客餐厅", "./temp/北欧客餐厅", "./temp/北欧-卧室", "./temp/现代-卧室"]:
        check_house_id_list = []
        if "客餐厅" in file_name:
            key_name = "LivingDiningRoom"
        else:
            key_name = "Bedroom"

        if "北欧" in file_name:
            style_name = "Nordic"
        else:
            style_name = "Modern"

        for lines in open(file_name, "r").readlines():
            room_key = lines.split(' ')[0]
            if len(room_key) > 10:
                check_house_id_list.append(room_key)

        # check_house_id_list = ["7d0c71b7-317b-48eb-8c44-131c31880faf_LivingDiningRoom-5296"]
        if "客餐厅" in file_name:
            build_temp_json = copy.deepcopy(SCHEME_LIVING_TABLE)
        else:
            build_temp_json = copy.deepcopy(SCHEME_BEDROOM_TABLE)

        for room_key in check_house_id_list:
            house_id, room_id = room_key.split('_')
            table = build_sample_extract_info(house_id, "", [room_id], reload=True)
            print(table)
            merge_info_json_data(build_temp_json, table[room_id])

        out_json[key_name + "_" + style_name] = build_temp_json

    # print(material_jid_info)
    # # with open("material_jid_info.json", "w") as f:
    # #     f.write(json.dumps(build_temp_json, indent=4))
    #     # show_results(table[room_id], show_dir="temp/卧室-现代/" + room_key)
    out = {
        "form_options": out_json,
        "support_space_list": [
            {
                "id": "LivingDiningRoom",
                "name": "客餐厅",
                "value": "LivingDiningRoom",
            },
            {
                "id": "LivingDiningRoom",
                "name": "主卧",
                "value": "Bedroom",
            },
            {
                "id": "LivingDiningRoom",
                "name": "次卧",
                "value": "Bedroom",
            }
        ],
        "support_style_list": [
            {
                "id": "Modern",
                "name": "现代",
                "value": "Modern",
            },
            {
                "id": "Nordic",
                "name": "北欧",
                "value": "Nordic",
            }
        ]}
    with open("temp/table.json", "w") as f:
        f.write(json.dumps(out, ensure_ascii=False))
