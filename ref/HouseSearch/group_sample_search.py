import json
import os

import copy

from Extract.extract_cache import get_room_sample, get_house_sample
from HouseSearch.house_propose import bad_group_key_list
from HouseSearch.house_search import compute_room_role_vector

source_house_info = json.load(open(os.path.join(os.path.dirname(__file__), "group_sample_data_roles.json"), 'r'))
source_house_info_keys = list(source_house_info.keys())

CHECK_ROOM_TYPE = ["DiningRoom", "LivingDiningRoom", "LivingRoom", "MasterBedroom", "Bedroom", "SecondBedroom",
                   "KidsRoom", "ElderlyRoom", "Library"]


def house_seed_dict_group_list_search(seed_dict, target_room_type, source_id="", sample=1, style="Modern", source="pub"):
    seed_group_type = {"Meeting": {}, "Dining": {}, "Work": {}, "Rest": {}, "Bed": {}, "Media": {}}

    for jid in seed_dict:
        group = seed_dict[jid]["group"]
        role = seed_dict[jid]["role"]
        if group in seed_group_type:
            if role not in seed_group_type[group]:
                seed_group_type[group][role] = []
            seed_group_type[group][role].append(jid)

    out_group = []
    for group_name in seed_group_type:
        if seed_group_type[group_name]:
            seeds_list = []
            for role in seed_group_type[group_name]:
                for jid in seed_group_type[group_name][role]:
                    seeds_list.append({"jid": jid, "group": group_name, "role": role})

            role_vector = compute_room_role_vector(seeds_list, target_room_type)
            if group_name in role_vector:
                role_vector = role_vector[group_name]
            else:
                continue

            out_group += search_group_info(group_name, None, role_vector, target_room_type, source_id=source_id, sample_num=1)
    return out_group


def house_room_zone_search_group_info(house_data, sample_num=1, style="Modern"):
    out_sample_data = {}
    for room_data in house_data["room"]:
        if "region_info" not in room_data:
            continue
        region_info = room_data["region_info"]

        group = []
        for region in region_info:
            group_sample_list = search_group_info(region["type"], [region["size"][0], region["size"][2]],
                                                  sample_num=sample_num,
                                                  target_room_type=room_data["type"], style=style)

            if group_sample_list:
                group_sample_list[0]["position"] = region["position"].copy()
                group_sample_list[0]["rotation"] = region["rotation"].copy()
                group.append(group_sample_list[0])

        room_scheme = {
            "room_type": room_data["type"],
            "room_area": room_data["area"],
            "room_style": "Contemporary",
            "room_height": 2.8,
            "layout_scheme": [{}]
        }
        room_scheme["layout_scheme"][0]["code"] = 10000
        room_scheme["layout_scheme"][0]["score"] = 100
        room_scheme["layout_scheme"][0]["type"] = room_data["type"]
        room_scheme["layout_scheme"][0]["area"] = room_data["area"]
        room_scheme["layout_scheme"][0]["material"] = {}
        room_scheme["layout_scheme"][0]["decorate"] = {}
        room_scheme["layout_scheme"][0]["painting"] = {}
        room_scheme["layout_scheme"][0]["group"] = group

        room_scheme["layout_scheme"][0]["source_room_area"] = room_data["area"]
        room_scheme["layout_scheme"][0]["source_house"] = "sample_house"
        room_scheme["layout_scheme"][0]["source_room"] = room_data["id"] + "_diy"

        out_sample_data[room_data["id"]] = room_scheme

    return [{"info": {}, "sample": out_sample_data}]


def search_group_info(group_name, size=None, roles_vec=None, target_room_type="LivingRoom", source_id="", sample_num=1,
                      style="Modern", source="pub"):
    group_sample_list = []

    if len(source_id) > 0 and group_name in ["Meeting", "Dining", "Media", "Work", "Bed"]:
        if target_room_type in ["LivingRoom", "LivingDiningRoom"]:
            sample_para, sample_data, sample_layout, sample_group = get_house_sample(source_id)
            for room_id in sample_group:
                if sample_group[room_id]["room_type"] in ["LivingDiningRoom", "LivingRoom"]:
                    for group in sample_group[room_id]["group_functional"]:
                        if group["type"] == group_name:
                            group_sample_list.append(group)
            return group_sample_list[:sample_num]

    if roles_vec:
        keys_list = search_group_roles(group_name, roles_vec, target_room_type=target_room_type,
                                       sample_num=sample_num * 2,
                                       style=style, source=source)
    else:
        keys_list = search_group_key(group_name, size, target_room_type=target_room_type, sample_num=sample_num * 2,
                                     style=style, source=source)

    for key_data in keys_list:
        key = key_data["key"]
        house_id, room_id = key.split('_')
        room_para, room_layout, room_group = get_room_sample(house_id, room_id)

        for g in room_group["group_functional"]:
            if g["type"] == group_name:
                new_g = copy.deepcopy(g)
                # new_g["source_house"] = house_id
                # new_g["source_room"] = room_id
                group_sample_list.append(new_g)
        if len(group_sample_list) >= sample_num:
            return group_sample_list

    return group_sample_list


def search_group_key(group_name, size, target_room_type="LivingRoom", sample_num=4, style="Modern", source="pub"):
    size_p = 1
    if group_name == "Dining":
        size_p = 5
    elif group_name == "Media":
        size_p = 3
    elif group_name == "Cabinet":
        size_p = 7
    elif group_name == "Work":
        size_p = 5
    elif group_name == "Armoire":
        size_p = 7

    source_list = source_house_info[source]
    if target_room_type in ["MasterBedroom", "SecondBedroom"]:
        target_room_type = "Bedroom"
    hash_room = []
    scores = []
    if target_room_type in CHECK_ROOM_TYPE:
        key_list = source_list[target_room_type]

        for key_data in key_list:
            if key_data['style_type'] != style:
                continue

            house_id, room_id = key_data['key'].split('_')

            if room_id in hash_room:
                continue
            else:
                hash_room.append(room_id)

            add = 0.0
            min_l = min(size) - min(key_data['vector'][size_p:size_p + 2])
            max_l = max(size) - max(key_data['vector'][size_p:size_p + 2])

            if min_l < 0. or max_l < 0:
                add += (min(min_l, max_l)) ** 2

            score = add + abs(min(key_data['vector'][size_p:size_p + 2]) - min(size)) + \
                    abs(max(key_data['vector'][size_p:size_p + 2]) - max(size))

            scores.append((score, key_data, group_name))

        scores = sorted(scores, key=lambda x: x[0])

        # 增加功能区打分
        if len(scores) == 0:
            return []

        out_final_list = []
        for idx in range(min(sample_num, len(scores))):
            idx += 1
            out_final_list.append({"key": scores[idx][1]['key'], "score": scores[idx][0],
                                   "size": scores[idx][1]['vector'][size_p:size_p + 2], "type": group_name})

        return out_final_list


def search_group_roles(group_name, roles_vec, target_room_type="LivingRoom", sample_num=1, style="Modern",
                       source="pub"):
    if target_room_type in ["MasterBedroom", "SecondBedroom", "Bedroom"]:
        target_room_type = "Bedroom"
    elif target_room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
        target_room_type = "LivingDiningRoom"

    source_list = source_house_info[source]

    hash_room = []
    scores = []
    if target_room_type in CHECK_ROOM_TYPE:
        key_list = source_list[target_room_type]

        for key_data in key_list[:300]:
            if key_data['style_type'] != style:
                continue

            house_id, room_id = key_data['key'].split('_')

            if roles_vec and key_data['key'] in bad_group_key_list:
                continue

            if room_id in hash_room:
                continue
            else:
                hash_room.append(room_id)

            if group_name not in key_data["roles_vec"]:
                continue

            s = [abs(key_data["roles_vec"][group_name][i] - roles_vec[i]) for i in range(len(roles_vec))]
            score = sum(s)

            scores.append((score, key_data, group_name))

    scores = sorted(scores, key=lambda x: x[0])

    # 增加功能区打分
    if len(scores) == 0:
        return []

    out_final_list = []
    for idx in range(min(sample_num, len(scores))):
        idx += 1
        out_final_list.append({"key": scores[idx][1]['key'], "score": scores[idx][0], "type": group_name})

    return out_final_list
