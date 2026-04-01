"""
    放我家默认户型逻辑: 卧室的分支规则较多, 比较恶心, 等待重写
"""
import json, os
import random
import numpy as np

from Extract.extract_cache import GROUP_TYPE_MAIN, GROUP_TYPE_REST, get_house_data, get_house_sample
from Furniture.furniture import get_furniture_data, add_furniture_role_by_jid
from House.house_sample import compute_room_seed
from HouseSearch.house_propose import compute_role_vector_sim
from HouseSearch.house_search import compute_room_role_vector
from HouseSearch.house_seed import parse_object_size, get_material_data_info
from HouseSearch.house_style import get_furniture_list_target_style
from HouseSearch.seed.seed_roles import refine_seeds_note
from HouseSearch.source.armoire_source import generate_new_armoire_room_data
from ImportHouse.room_search import search_advice_house
from LayoutGroup.GroupGenerate.find_sample_id import find_sample

target_house_room = {
    "LivingRoom": [
        "7a9571e6-0b7d-41bb-a585-6b4319bf6385_LivingDiningRoom-1250",  # 22 origin_1
        "34d9a608-73a5-42de-adf2-330660cb2834_LivingRoom-1590",  # 29 origin_2
        # "30f1dafd-b408-4ae4-8004-ba41d0f2b7a5_LivingRoom-2098",  # origin_3
        "5d12f045-8829-44ec-840f-ed645f837be3_LivingRoom-2169",  # 37 origin_4
        "6ba46ef8-3fea-4d0c-8383-08024338e0c5_LivingRoom-2506",  # 40 origin_5
        "2b52b376-8ffe-43ab-bcc5-ed8d0e402da9_LivingRoom-17995",  # 45 origin_6
        "9febe749-9f93-4bc6-9db4-aed04d4e713e_LivingDiningRoom-1938"  # 54 origin_7
    ],
    "Bedroom": [
        "a591c378-7df6-42ee-98e9-1b892fc05c5c_Bedroom-4300",  # 15
        "64aa2dd3-53bb-4b1f-9e61-ee1a7deb6b3d_Bedroom-6812",  # 16
        "dccea881-cf0a-40b2-97f5-af4e5c482c48_Bedroom-6855",  # 21
        "ed9cc4ae-619c-458f-807e-0846aa2bb1f8_Bedroom-3408",
        "33cd0a2a-041d-4d1d-8059-244404873d8f_MasterBedroom-28626",  # 16
        "63e358c4-293f-4d79-99c2-0aef95817346_Bedroom-7016",  # 21,
        "7d20e68e-9053-49d8-8ab8-c838c7115953_Bedroom-3408"
    ]
}

target_bedroom_material_vector = {
    'a591c378-7df6-42ee-98e9-1b892fc05c5c_Bedroom-4300': {
        'floor': [224.14404296875, 199.6067352294922, 163.54074096679688], 'wall': [250, 247, 237]},
    '64aa2dd3-53bb-4b1f-9e61-ee1a7deb6b3d_Bedroom-6812': {
        'floor': [74.98525607585907, 50.8184175491333, 32.65574491024017],
        'wall': [235, 233, 233]}, 'dccea881-cf0a-40b2-97f5-af4e5c482c48_Bedroom-6855': {
        'floor': [71.47294473648071, 43.81926453113556, 25.073474168777466],
        'wall': [237.58968353271484, 236.90703582763672, 223.42292022705078]},
    'ed9cc4ae-619c-458f-807e-0846aa2bb1f8_Bedroom-3408': {
        'floor': [197.506476521492, 167.15564793348312, 134.01533150672913],
        'wall': [222.28237225826607, 219.84975003410645, 214.84975003410645]},
    '33cd0a2a-041d-4d1d-8059-244404873d8f_MasterBedroom-28626': {
        'floor': [144.0988591797691, 134.73653204107384, 123.45881795140818],
        'wall': [234, 233, 230]}, '63e358c4-293f-4d79-99c2-0aef95817346_Bedroom-7016': {
        'floor': [144.0988591797691, 134.73653204107384, 123.45881795140818], 'wall': [233, 233, 228]},
    '7d20e68e-9053-49d8-8ab8-c838c7115953_Bedroom-3408': {
        'floor': [182.6505651473999, 154.06867384910583, 117.82409751415253],
        'wall': [239.24829006195068, 234.4949436187744, 227.91256618499756]}
}


origin_base_id_change = {
    "7a9571e6-0b7d-41bb-a585-6b4319bf6385_LivingDiningRoom-1250": "origin_1",
    "34d9a608-73a5-42de-adf2-330660cb2834_LivingRoom-2098": "origin_3",
    "2b97206e-8767-4beb-89c7-721fd333f138_LivingRoom-1590": "origin_2",
    "5d12f045-8829-44ec-840f-ed645f837be3_LivingRoom-2169": "origin_4",
    "6ba46ef8-3fea-4d0c-8383-08024338e0c5_LivingRoom-2506": "origin_5",
    "2b52b376-8ffe-43ab-bcc5-ed8d0e402da9_LivingRoom-17995": "origin_6",
    "9febe749-9f93-4bc6-9db4-aed04d4e713e_LivingDiningRoom-1938": "origin_7",

    "a591c378-7df6-42ee-98e9-1b892fc05c5c_Bedroom-4300": "bed_European",
    "64aa2dd3-53bb-4b1f-9e61-ee1a7deb6b3d_Bedroom-6812": "bed_Chinese",
    "dccea881-cf0a-40b2-97f5-af4e5c482c48_Bedroom-6855": "bed_Country",
    "ed9cc4ae-619c-458f-807e-0846aa2bb1f8_Bedroom-3408": "bed_Japanese",
    "33cd0a2a-041d-4d1d-8059-244404873d8f_MasterBedroom-28626": "bed_Modern",
    "63e358c4-293f-4d79-99c2-0aef95817346_Bedroom-7016": "bed_Luxury",
    "7d20e68e-9053-49d8-8ab8-c838c7115953_Bedroom-3408": "bed_Nordic",

    "8a45549b-374c-4db1-8f29-1845c656b1e8_Bedroom-3408": "bed_Japanese",
    "ab77bc51-f16e-4953-b91a-17d3f80f5dc6_MasterBedroom-28626": "bed_Modern",

    "eba8abc4-0fb8-457d-9425-5d9f93499f85_none-56037": "bed_Modern"
}

base_big_bedroom_room_list = {
    "bed_European": "ab77bc51-f16e-4953-b91a-17d3f80f5dc6_MasterBedroom-28626",
    "bed_Chinese": "ab77bc51-f16e-4953-b91a-17d3f80f5dc6_MasterBedroom-28626",
    "bed_Country": "ab77bc51-f16e-4953-b91a-17d3f80f5dc6_MasterBedroom-28626",
    "bed_Japanese": "8a45549b-374c-4db1-8f29-1845c656b1e8_Bedroom-3408",
    "bed_Modern": "ab77bc51-f16e-4953-b91a-17d3f80f5dc6_MasterBedroom-28626",
    "bed_Luxury": "ab77bc51-f16e-4953-b91a-17d3f80f5dc6_MasterBedroom-28626",
    "bed_Nordic": "8a45549b-374c-4db1-8f29-1845c656b1e8_Bedroom-3408"
}

base_big_armoire_room_list = {
    "bed_European": "eba8abc4-0fb8-457d-9425-5d9f93499f85_none-56037",
    "bed_Chinese": "eba8abc4-0fb8-457d-9425-5d9f93499f85_none-56037",
    "bed_Country": "eba8abc4-0fb8-457d-9425-5d9f93499f85_none-56037",
    "bed_Japanese": "eba8abc4-0fb8-457d-9425-5d9f93499f85_none-56037",
    "bed_Modern": "eba8abc4-0fb8-457d-9425-5d9f93499f85_none-56037",
    "bed_Luxury": "eba8abc4-0fb8-457d-9425-5d9f93499f85_none-56037",
    "bed_Nordic": "eba8abc4-0fb8-457d-9425-5d9f93499f85_none-56037",
}

check_house_id_list = ["eba8abc4-0fb8-457d-9425-5d9f93499f85"]

source_living_base_scheme = json.load(
    open(os.path.join(os.path.dirname(__file__), "source/living_dict.json"), 'r'))["base"]

target_size_template = {
    "LivingRoom": {
        "Dining": {"table": [0.8, 1.2, 0.8, "ratio"], "chair": [0.8, 3.0, 0.8, "fixed"]},
        "Media": {"table": [1.0, 10.0, 1.0, "ratio"]},
        "Meeting": {"sofa": [0.8, 1.5, 0.6, "ratio"], "side sofa": [0.8, 3.0, 0.8, "fixed"],
                    "table": [0.6, 1.5, 0.4, "ratio"], "side table": [0.8, 3.0, 0.8, "fixed"]}
    },
    "LivingDiningRoom": {
        "Dining": {"table": [0.8, 1.2, 0.8, "ratio"], "chair": [0.8, 3.0, 0.8, "fixed"]},
        "Media": {"table": [1.0, 10.0, 1.0, "ratio"]},
        "Meeting": {"sofa": [0.8, 1.5, 0.6, "ratio"], "side sofa": [0.8, 3.0, 0.8, "fixed"],
                    "table": [0.6, 1.5, 0.4, "ratio"], "side table": [0.8, 3.0, 0.8, "fixed"]}
    },
    "DiningRoom": {
        "Dining": {"table": [1.2, 1.5, 1.2, "ratio"], "chair": [1.0, 3.0, 1.0, "fixed"]}
    },
    "Bedroom": {
        "Bed": {"bed": [0.9, 1.5, 0.9, "ratio"], "side table": [0.65, 3.0, 0.65, "fixed"]},
        "Armoire": {"armoire": [1.2, 10.0, 1.1, "ratio"]},
        "Media": {"table": [1.2, 10.0, 1.5, "ratio"]}
    }
}

origin_base_id_multi_size_map = {
    "origin_1": {"Meeting/sofa": [2.5, 1.3], "Dining/table": [1.6, 0.8], "Media/table": [3.2, 0.46],
                 "Meeting/table": [1.5, 1.0]},
    "origin_2": {"Meeting/sofa": [3.0, 2.5], "Dining/table": [2.0, 0.8], "Media/table": [2.2, 0.8],
                 "Meeting/table": [1.5, 1.0], "Meeting/side table": [0.83, 0.83]},
    "origin_3": {"Meeting/sofa": [3.0, 1.4], "Dining/table": [2.0, 0.8], "Media/table": [3.0, 0.4],
                 "Meeting/table": [1.5, 1.0]},
    "origin_4": {"Meeting/sofa": [3.5, 2.5], "Dining/table": [2.0, 0.8], "Media/table": [3.0, 1.0],
                 "Meeting/table": [1.5, 1.0]},
    "origin_5": {"Meeting/sofa": [4.0, 2.5], "Dining/table": [3.0, 3.0], "Media/table": [3.5, 0.46],
                 "Meeting/table": [1.5, 1.0], "Meeting/side table": [1.0, 0.8]},
    "origin_6": {"Meeting/sofa": [4.0, 3.0], "Dining/table": [2.0, 0.8], "Media/table": [3.5, 0.8],
                 "Meeting/table": [1.5, 1.0], "Meeting/side table": [1.0, 0.8]},
    "origin_7": {"Meeting/sofa": [4.0, 3.0], "Dining/table": [2.7, 1.4], "Media/table": [4.8, 1.0],
                 "Meeting/table": [1.5, 1.3], "Meeting/side table": [1.5, 1.5]}
}

map_ihome_put_my_home_category = {
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


def refine_region_info(room_data, region_info):
    if room_data["type"] in ["MasterBedroom", "Bedroom", "SecondBedroom"]:
        cabinet_size_list = []
        arimore = None
        for region in region_info:
            if region["type"] == "Armoire":
                arimore = region
            elif region["type"] == "Cabinet":
                size = region["size"][0]
                cabinet_size_list.append((region, size))

        if not arimore and len(cabinet_size_list) > 0:
            cabinet_size_list = sorted(cabinet_size_list, key=lambda x: x[1], reverse=True)
            cabinet_size_list[0][0]["type"] = "Armoire"
            cabinet_size_list[0][0]["zone"] = ""


def template_update_house_data_region(house_id, room_type, house_data):
    # 使用house_id对应的方案区域
    sample_para, sample_data, sample_layout, sample_group = get_house_sample(house_id)
    for room_data in house_data["room"]:
        room_id = room_data["id"]
        region_info = []
        for target_room_id in sample_layout:
            if target_room_id == room_id and sample_layout[target_room_id]["layout_scheme"]:

                for group in sample_layout[target_room_id]["layout_scheme"][0]["group"]:
                    if group["type"] in ["Meeting", "Dining", "Media", "Bed", "Armoire", "Work", "Cabinet", "Bath",
                                         "Rest"]:
                        one_region = {
                            "type": group["type"],
                            "size": group["size"][:],
                            "scale": [1., 1., 1.],
                            "position": group["position"][:],
                            "rotation": group["rotation"][:],
                            "zone": ""
                        }
                        if "table/table" in group["obj_type"] and group["type"] == "Cabinet":
                            one_region["type"] = "Work"

                        if "zone" in group:
                            one_region["zone"] = group["zone"]
                        if "scale" in group:
                            one_region["scale"] = group["scale"]
                        region_info.append(one_region)
        refine_region_info(room_data, region_info)
        if region_info:
            room_data["region_info"] = region_info


def get_room_template_base_samples(role_vector, target_room, target_style, sample_num):
    if target_room not in origin_base_id_change:
        return []

    out_list = []
    source_key = origin_base_id_change[target_room]
    for item in source_living_base_scheme:
        if item["style_type"] and item["style_type"] not in target_style:
            continue

        if item["source_id"] and item["source_id"] != source_key:
            continue

        score = compute_role_vector_sim(role_vector, item["roles_vec"])
        out_list.append((item["key"], score))

    need_keys = sorted(out_list, key=lambda x: x[1])
    if len(need_keys) > 0:
        return [i[0] for i in need_keys[:sample_num]]
    else:
        return [target_room]


def get_role_vector_list(room_key):
    for room_item in source_living_base_scheme:
        if room_item["key"] == room_key:
            return room_item["roles_vec"]
    return {}


def search_template_base_rooms(role_vector, need_target_room_list):
    target_room_key = need_target_room_list[-1]

    out_list = []
    for room_key in need_target_room_list:
        target_role_vector = get_role_vector_list(room_key)
        score = compute_role_vector_sim(role_vector, target_role_vector)
        out_list.append((room_key, score))

    out_list = sorted(out_list, key=lambda x: x[1])
    if len(out_list) > 0:
        target_room_key = out_list[0][0]

    return target_room_key


def get_furniture_info_list(furniture_list, room_type, fake_room_area):
    furniture_info_list = []
    for jid in furniture_list:
        obj_type, obj_style_en, obj_size = get_furniture_data(jid)
        object_new = {
            'id': jid,
            'type': obj_type,
            'style': obj_style_en,
            'size': [s for s in obj_size],
            'scale': [1, 1, 1],
            'position': [0, 0, 0],
            'rotation': [0, 0, 0, 1]
        }
        parse_object_size(object_new)
        furniture_info_list.append(object_new)

    seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_info_list, [], room_type,
                                                                   room_area=fake_room_area)
    seed_all = seed_list + keep_list + plus_list
    if len(seed_all) == 0:
        seed_all = furniture_info_list

    seeds_note = {}
    for seed_one in seed_all:
        seed_key = seed_one['id']
        seeds_note[seed_key] = seed_one

    refine_seeds_note(seeds_note, room_type)

    return seeds_note


def check_seed_size_max_valid(now_house_size_target, seed_size_info):
    for seed_role_key in seed_size_info:
        if seed_role_key not in now_house_size_target:
            return False
        max_size = now_house_size_target[seed_role_key]
        now_size = seed_size_info[seed_role_key]

        if max_size[0] > now_size[0] and max_size[1] > now_size[1]:
            continue
        else:
            return False

    return True


def search_template_base_rooms_size(role_vector, seeds_note, need_target_room_list):
    seed_size_info = {}
    num_seeds = 0
    for key in seeds_note:
        if 'group' not in seeds_note or 'role' not in seeds_note:
            continue
        num_seeds += 1
        group, role = seeds_note[key]["group"], seeds_note[key]["role"]
        group_key = group + '/' + role
        if len(group_key) > 3:
            seed_size_info[group_key] = [seeds_note[key]["size"][0] / 100., seeds_note[key]["size"][2] / 100.]

    target_room_key = need_target_room_list[-1]

    search_size_template = origin_base_id_multi_size_map

    out_list = []
    for room_key in need_target_room_list:
        if room_key not in origin_base_id_change:
            continue
        source_key = origin_base_id_change[room_key]

        if source_key not in origin_base_id_multi_size_map:
            continue

        now_size_target = search_size_template[source_key]
        if check_seed_size_max_valid(now_size_target, seed_size_info):
            out_list.append((room_key, 0.0))

    # out_list = sorted(out_list, key=lambda x: x[1])
    if len(out_list) > 0:
        # target_room_key = random.choice(out_list)[0]
        target_room_key = out_list[0][0]
    else:
        if len(need_target_room_list) > 0:
            # random.seed()
            target_room_key = need_target_room_list[0]
    return target_room_key


def search_template_base_rooms_style(seed_info, need_target_room_list, target_style):
    out_list = []

    # 2022.02 更新
    # 根据role_vector 尺寸类型确定兜底大卧室型(主要用来放大衣柜/其他类型柜架兜底)
    # 2022.03 更新
    # 根据role_vector 尺寸类型确定兜底转角衣柜卧室型
    #
    use_base_room_flag = False
    use_big_armoire_flag = False
    for role_jid in seed_info:
        role_data = seed_info[role_jid]
        if role_data["size"][0] > 240 or role_data["size"][2] > 240:
            use_base_room_flag = True
        if role_data["role"] in ["cabinet"]:
            use_base_room_flag = True
        if role_data["role"] in ["armoire"] and role_data["size"][2] > 120:
            use_big_armoire_flag = True

    # 转角衣柜
    if use_big_armoire_flag:
        for room_key in base_big_armoire_room_list:
            source_key = base_big_armoire_room_list[room_key]
            style_ = room_key.split('_')[1]
            if style_ in target_style:
                out_list.append(source_key)

    # 使用卧室大户型
    elif use_base_room_flag:
        for room_key in base_big_bedroom_room_list:
            source_key = base_big_bedroom_room_list[room_key]
            style_ = room_key.split('_')[1]
            if style_ in target_style:
                out_list.append(source_key)

    # 使用一般户型
    if len(out_list) == 0:
        for room_key in need_target_room_list:
            if room_key not in origin_base_id_change:
                continue
            source_key = origin_base_id_change[room_key]
            style_ = source_key.split('_')[1]
            if style_ in target_style:
                out_list.append(room_key)

    if out_list:
        return out_list[0]
    else:
        return need_target_room_list[-1]


def house_search_from_seed_new(furniture_list=[], room_type="LivingRoom", sample_num=1):
    # step 1 获取候选房间列表
    if "-" in room_type:
        room_type, _ = room_type.split('-')
    if room_type in ["Bedroom", "MasterBedroom", "SecondBedroom", "KidsRoom"]:
        need_target_room_list = target_house_room["Bedroom"]
        fake_bedroom = True
        fake_room_area = 15.
    else:
        fake_bedroom = False
        need_target_room_list = target_house_room["LivingRoom"]
        fake_room_area = 35.

    # step 2 计算输入列表特征
    # step 2.1 计算输入列表布局角色
    seeds_note = get_furniture_info_list(furniture_list, room_type, fake_room_area)

    # step 2.2 计算输入特征
    role_vector = {}
    if seeds_note:
        seeds_list = []
        for jid in seeds_note:
            if 'group' in seeds_note and 'role' in seeds_note:
                seeds_list.append(
                    {"jid": jid, "group": seeds_note[jid]["group"], "role": seeds_note[jid]["role"]})

        role_vector = compute_room_role_vector(seeds_list, room_type)

    # step 3 根据特征算匹配度, 计算最优输入方案列表
    # step 3.1 计算输入特征
    target_style = get_furniture_list_target_style(seeds_note)
    if len(role_vector) == 0:
        seeds_note = {}
    # step 3.2 预算的户型特征进行匹配检索, 只会返回一个
    if fake_bedroom:
        target_room = search_template_base_rooms_style(seeds_note, need_target_room_list, target_style)
    else:
        target_room = search_template_base_rooms_size(role_vector, seeds_note, need_target_room_list)
    assert len(target_room) > 0

    # 根据模版户型与对应风格去找风格输入 自迁移使用的
    self_transfers = get_room_template_base_samples(role_vector, target_room, target_style, sample_num=1)

    # step 4 返回输出
    if len(seeds_note) > 0:
        replace_info = {room_type: {"soft": furniture_list, "sample": [], "self_transfer": self_transfers}}
    else:
        replace_info = {room_type: {"soft": [], "sample": [], "self_transfer": self_transfers}}
    search_success = False
    if self_transfers:
        search_success = True

    # 返回house_id
    house_id, room_id = target_room.split('_')
    if self_transfers:
        house_id, room_id = self_transfers[0].split('_')

    return search_success, house_id, replace_info


def house_search_from_material_seed_new(material_dict=[], room_type="LivingRoom", sample_num=1):
    mat_note = {}
    for k, v in material_dict.items():
        mat = [get_material_data_info(i) for i in v]
        mat_note[k] = mat
    if "-" in room_type:
        room_type, _ = room_type.split('-')
    out_list = []

    if room_type in ["Bedroom", "MasterBedroom", "SecondBedroom", "KidsRoom"]:
        need_target_room_list = target_house_room["Bedroom"]
        for room_key, mat_vec in target_bedroom_material_vector.items():
            score = 0
            for k, mats in mat_note.items():
                if k in mat_vec:
                    score += np.mean(np.abs(np.array(mats[0]['rgb'][:3]) - mat_vec[k][:3]))
                else:
                    score += 255
            out_list.append((room_key, score))
    else:
        need_target_room_list = target_house_room["LivingRoom"]
        for item in source_living_base_scheme:
            if not item["source_id"]:
                continue
            score = 0
            mat_vec = item['mat_vector'] if 'mat_vector' in item else {}
            for k, mats in mat_note.items():
                if k in mat_vec and isinstance(mats[0]['rgb'], list) and isinstance(mat_vec[k], list):
                    if len(mats[0]['rgb']) < 3 and len(mat_vec[k]) < 3:
                        score += 255
                    else:
                        score += np.mean(np.abs(np.array(mats[0]['rgb'][:3]) - mat_vec[k][:3]))
                else:
                    score += 255
            out_list.append((item["key"], score))
    # for target_room in need_target_room_list:
    #     if target_room not in origin_base_id_change:
    #         continue
    #     source_key = origin_base_id_change[target_room]

    need_keys = sorted(out_list, key=lambda x: x[1])

    target_room = need_target_room_list[-1]
    if len(need_keys) > 0:
        self_transfers = [i[0] for i in need_keys[:sample_num]]
    else:
        self_transfers = [target_room]

    # step 4 返回输出
    replace_info = {room_type: {"soft": [], "sample": [], "self_transfer": self_transfers}}
    search_success = False
    if self_transfers:
        search_success = True

    # 返回house_id
    house_id, room_id = target_room.split('_')
    if self_transfers:
        house_id, room_id = self_transfers[0].split('_')

    return search_success, house_id, replace_info


def house_search_from_seed_test(furniture_list=[], room_type="LivingRoom"):
    # step 1 获取候选房间列表
    if "-" in room_type:
        room_type, _ = room_type.split('-')
    if room_type in ["Bedroom", "MasterBedroom", "SecondBedroom", "KidsRoom"]:
        need_target_room_list = target_house_room["Bedroom"]
        fake_room_area = 15.
    else:
        need_target_room_list = target_house_room["LivingRoom"]
        fake_room_area = 35.

    # step 2 计算输入列表特征
    # step 2.1 计算输入列表布局角色
    seeds_note = get_furniture_info_list(furniture_list, room_type, fake_room_area)

    # step 3
    house_id = find_sample(seeds_note)

    # 返回house_id
    replace_info = {room_type: {"soft": furniture_list}}

    return True, house_id, replace_info


def compute_room_group_size(group_list, room_type):
    if room_type in ["Bedroom", "MasterBedroom", "SecondBedroom", "KidsRoom", "ElderlyRoom"]:
        now_target_group = target_size_template["Bedroom"]
    elif room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
        now_target_group = target_size_template[room_type]
    else:
        now_target_group = {}
    out_vector = {}
    for group in group_list:
        if group["type"] not in now_target_group:
            continue
        target_group_size = now_target_group[group["type"]]
        size = group["size"].copy()
        out_group = {}
        if size[0] < 0 or size[2] < 0:
            continue
        if group["type"] == "Bed":
            if group["size"][0] > 2.2:
                out_group["bed"] = [1.8, 1.3, size[2]]
                out_group["side table"] = [0.7, 0.8, 0.7]
                if size[0] < 2.7:
                    out_group["bed"] = [size[0] - 0.5, 1.3, size[2]]
                    out_group["side table"] = [0.7, 0.8, 0.7]
                else:
                    out_group["bed"] = [size[0] - 1.0, 1.3, size[2]]
                    out_group["side table"] = [0.7, 0.8, 0.7]
            else:
                out_group["bed"] = [min(size[0], 2.2), 1.3, size[2]]
            out_vector[group["type"]] = out_group
            continue

        if group["type"] == "Meeting":
            if group["size"][2] < 1.3 and group["size"][0] < 1.3:
                out_group["sofa"] = [1.8, 1.5, 1.0]
                out_vector[group["type"]] = out_group
                continue
            if group["size"][2] < 1.81:
                out_group["sofa"] = [size[0], 1.5, size[2]]
                out_vector[group["type"]] = out_group
                continue

        out_group = {}
        for role in target_group_size:
            role_target_size = target_group_size[role]
            if role_target_size[-1] == "fixed":
                out_group[role] = role_target_size[:3].copy()
            else:
                out_group[role] = [size[i] * role_target_size[i] for i in range(3)]

            out_group[role][1] = min(3.0, out_group[role][1])

        out_vector[group["type"]] = out_group

    return out_vector


def compute_room_group_size_max(group_list, room_type, room_area=40.):
    if room_type in ["Bedroom", "MasterBedroom", "SecondBedroom", "KidsRoom", "ElderlyRoom"]:
        now_target_group = target_size_template["Bedroom"]
    elif room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
        now_target_group = target_size_template[room_type]
    else:
        now_target_group = {}
    out_vector = {}
    for group in group_list:
        if group["type"] not in now_target_group:
            continue
        target_group_size = now_target_group[group["type"]]
        size = group["size"].copy()
        out_group = {}
        if size[0] < 0 or size[2] < 0:
            continue

        out_group = {}
        for role in target_group_size:
            role_target_size = target_group_size[role]
            if role_target_size[-1] == "fixed":
                out_group[role] = role_target_size[:3].copy()
            else:
                out_group[role] = [size[i] * 1.0 for i in range(3)]
            if role == 'sofa':
                if room_area > 45.:
                    out_group[role][0] *= 1.5

            if role == 'side table' and group['type'] == "Bed":
                out_group[role][0] = 0.8
                out_group[role][2] = 1.2

            out_group[role][1] = 3.0

        out_vector[group["type"]] = out_group

    return out_vector


# 最大尺寸/策略
def house_group_size_search_max(house_data, return_base_info=False):
    house_size_vector = {}
    for room_data in house_data["room"]:
        if "region_info" in room_data and len(room_data["region_info"]) > 0:
            group_list = room_data["region_info"]
            room_type = room_data["type"]
            room_size_data = compute_room_group_size_max(group_list, room_type, room_data["area"])
            house_size_vector[room_data["id"]] = room_size_data
        else:
            house_size_vector[room_data["id"]] = {}

    return house_size_vector


def house_group_size_search(house_data, return_base_info=False):
    house_size_vector = {}
    for room_data in house_data["room"]:
        if "region_info" in room_data and len(room_data["region_info"]) > 0:
            group_list = room_data["region_info"]
            room_type = room_data["type"]
            room_size_data = compute_room_group_size(group_list, room_type)
            house_size_vector[room_data["id"]] = room_size_data

    if house_size_vector:
        return house_size_vector

    house_data_info, house_layout_info, house_propose_info = search_advice_house(house_data)

    for room_key, room_val in house_layout_info.items():
        if room_key in house_size_vector:
            continue

        scheme_list, scheme_max = room_val['layout_scheme'], {}
        room_type, group_list = '', []
        if 'room_type' in room_val:
            room_type = room_val['room_type']
        for scheme_idx, scheme_one in enumerate(scheme_list):
            if len(scheme_max) <= 0:
                scheme_max = scheme_one
            elif 'group' in scheme_max and 'group' in scheme_one:
                group_list_old, group_list_new = scheme_max['group'], scheme_one['group']
                group_best_old, group_best_new = 0, 0
                for group_one in group_list_old:
                    group_type, group_size = group_one['type'], group_one['size'][:]
                    if 'regulation' in group_one:
                        group_next = group_one['regulation']
                        group_size[0] += group_next[1]
                        group_size[0] += group_next[3]
                        group_size[2] += group_next[0]
                        group_size[2] += group_next[2]
                    if group_type in ['Media']:
                        group_best_old += 10
                    elif group_type in ['Dining'] and room_type in ['LivingRoom']:
                        pass
                    elif group_type in GROUP_TYPE_MAIN:
                        group_best_old += 100
                    elif group_type in ['Armoire', 'Cabinet'] and min(group_size[0], group_size[1]) > 0.8:
                        group_best_old += 20
                        group_best_old += group_size[0]
                    elif group_type in GROUP_TYPE_REST:
                        group_best_old += 10
                for group_one in group_list_new:
                    group_type, group_size = group_one['type'], group_one['size'][:]
                    if 'regulation' in group_one:
                        group_next = group_one['regulation']
                        group_size[0] += group_next[1]
                        group_size[0] += group_next[3]
                        group_size[2] += group_next[0]
                        group_size[2] += group_next[2]
                    if group_type in ['Media']:
                        group_best_new += 1
                    elif group_type in ['Dining'] and room_type in ['LivingRoom']:
                        pass
                    elif group_type in GROUP_TYPE_MAIN:
                        group_best_new += 100
                    elif group_type in ['Armoire', 'Cabinet'] and min(group_size[0], group_size[1]) > 0.8:
                        group_best_new += 20
                        group_best_new += group_size[0]
                    elif group_type in GROUP_TYPE_REST:
                        group_best_new += 10
                if group_best_new > group_best_old:
                    scheme_max = scheme_one
            pass
        if 'group' in scheme_max:
            room_type, group_list = room_val['room_type'], scheme_max['group']
        if len(room_type) <= 0 and 'room_type' in room_val:
            room_type = room_val['room_type']

        room_size_data = compute_room_group_size(group_list, room_type)
        if return_base_info:
            # 返回ihome工程侧格式
            if room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
                now_type = "LivingRoom"
            elif room_type in ["MasterBedroom", "Bedroom", "SecondBedroom"]:
                now_type = "Bedroom"
            else:
                continue

            temp = {}
            for group in room_size_data:
                temp[group] = {}
                for role in room_size_data[group]:
                    size = [int(i * 1000) for i in room_size_data[group][role]]
                    # change 2 1
                    size[2], size[1] = size[1], size[2]
                    temp[group][role] = size
            house_size_vector[now_type] = temp
        else:
            house_size_vector[room_key] = room_size_data

    return house_size_vector


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


def real_house_furniture_role_size(house_id, design_url=""):
    _, house_data = get_house_data(house_id, design_url)
    compute_use_house_data(house_data)
    house_size_target = house_group_size_search(house_data, True)
    return house_size_target


def get_room_type(room_key, house_data):
    if room_key == "Bedroom" or room_key == "LivingRoom":
        return room_key

    room_type = room_key
    if house_data and "room" in house_data:
        for room in house_data["room"]:
            if room["id"] == room_key:
                room_type = room["type"]
                break
    if room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
        return "LivingRoom"
    if room_type in ["Bedroom", "SecondBedroom", "MasterBedroom"]:
        return "Bedroom"
    return room_type


def map_ihome_put_my_home_role_data(cate_key, room_key, house_data):
    room_type = get_room_type(room_key, house_data)
    if room_type in map_ihome_put_my_home_category:
        for item in map_ihome_put_my_home_category[room_type]:
            if item["categoryGroupId"] == cate_key:
                return item["map_role"]

    return []


def update_furniture_role_data(replace_info, house_data):
    for room_key in replace_info:
        if "soft" in replace_info[room_key] and "role" in replace_info[room_key]:
            furniture_list = replace_info[room_key]["soft"]
            role_dict = replace_info[room_key]["role"]
            for jid in role_dict:
                mapped_group_role = map_ihome_put_my_home_role_data(role_dict[jid], room_key, house_data)
                if mapped_group_role:
                    add_furniture_role_by_jid(jid, mapped_group_role)
    return True


def armoire_house_data_refine(house_id, house_data, replace_info):
    if house_id not in check_house_id_list:
        return

    target_house_id, target_room_id = base_big_armoire_room_list["bed_Modern"].split('_')
    furniture_list = []
    target_room_replace_info = {}

    for room_key in replace_info:
        if "Bedroom" in room_key and "soft" in replace_info[room_key]:
            furniture_list = replace_info[room_key]["soft"]
            target_room_replace_info = replace_info[room_key]

    if furniture_list:
        seeds_note = get_furniture_info_list(furniture_list, "Bedroom", 40.)
        size_data = None
        room_data = None
        for jid in seeds_note:
            if seeds_note[jid]['role'] == 'armoire':
                size_data = [i/100. for i in seeds_note[jid]['size']]

        if size_data:
            generated_room_data, armoire_region, work_region = generate_new_armoire_room_data(size_data)
        else:
            return

        if generated_room_data:
            for room_data in house_data["room"]:
                if room_data['id'] == target_room_id:
                    room_data["height"] = 2.8
                    room_data['floor'] = generated_room_data['floor']
                    target_room_replace_info["sample"] = target_room_replace_info["self_transfer"].copy()
                    target_room_replace_info["self_transfer"] = []
                    # room_data['door_info'] = generated_room_data['door_info']
                    # room_data['floor_wall_info'] = {}

                    if "region_info" in room_data:
                        for region in room_data["region_info"]:
                            if region["type"] == "Armoire":
                                region["size"] = armoire_region["size"]
                                region["position"] = armoire_region["position"]

        return


if __name__ == '__main__':
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


    def get_return_format(house_size_target):
        # key room_id target size_info
        out = {}
        for room_type in house_size_target:
            temp = []
            now_room_size = house_size_target[room_type]
            if room_type not in map_role_data:
                continue

            for target_item in map_role_data[room_type]:
                group, role = target_item["map_role"][0:2]
                if group in now_room_size and role in now_room_size[group]:
                    temp.append({
                        "categoryGroupId": target_item["categoryGroupId"],
                        "sizeMax": now_room_size[group][role],
                        "limit": 1
                    })
            out[room_type] = temp

        return out


    import time

    start_t = time.time()
    house_size_target = real_house_furniture_role_size("348f475f-a0df-4204-bdb2-3fceb5422271")
    house_size_target = get_return_format(house_size_target)
    print(time.time() - start_t)
    print(house_size_target)
