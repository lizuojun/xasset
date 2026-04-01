# -*- coding: utf-8 -*-

import json
import os

from HouseSearch.source.basic_style import get_target_style
from HouseSearch.model.model_hsf import get_model_valid
from ImportHouse.room_search import get_room_data, get_room_sample, cal_room_vector, cal_house_vector, get_house_data

DATA_DIR_FEATURE_INFO = os.path.dirname(__file__) + '/temp/feature'
if not os.path.exists(DATA_DIR_FEATURE_INFO):
    os.makedirs(DATA_DIR_FEATURE_INFO)

DATA_DIR_HOUSE_INFO = os.path.dirname(__file__) + '/temp/house'
if not os.path.exists(DATA_DIR_HOUSE_INFO):
    os.makedirs(DATA_DIR_HOUSE_INFO)

source_house_info = json.load(open(os.path.join(os.path.dirname(__file__), "group_sample_data_roles.json"), 'r'))
source_house_info_keys = list(source_house_info.keys())
CHECK_ROOM_TYPE = ["DiningRoom", "LivingDiningRoom", "LivingRoom", "MasterBedroom", "Bedroom", "SecondBedroom",
                   "KidsRoom", "ElderlyRoom", "Library", "Balcony"]
LD_TYPE = ["DiningRoom", "LivingDiningRoom", "LivingRoom"]
BED_TYPE = ["MasterBedroom", "Bedroom", "SecondBedroom", "KidsRoom", "ElderlyRoom"]
base_living_rooms_info = json.load(open(os.path.join(os.path.dirname(__file__), "group_sample_data_roles.json"), 'r'))["base"]

DATA_OSS_FEATURE = "feature"
DATA_OSS_HOUSE = "design_json_res"

bad_room_list = ["LivingDiningRoom-3526", "LivingDiningRoom-37508"]
acc_not_need = ["bfa9ec25-34a1-4054-ba03-b1cb332f6088", "6b50c2e9-11f2-42cd-8cf3-4e603b4321cd", "8119c803-98ae-4198-80e4-caeb2a880da4"]
bad_key_list = json.load(open(os.path.join(os.path.dirname(__file__), "./source/bad_key.json"), 'r'))
bad_group_key_list = json.load(open(os.path.join(os.path.dirname(__file__), "./source/bad_group_key.json"), 'r'))


def get_search_room_type(room_type):
    if room_type in ['SecondBedroom', 'Bedroom', 'MasterBedroom']:
        return 'Bedroom'
    return room_type


def check_room_type_same(room_type1, room_type2):
    if room_type1 in LD_TYPE and room_type2 in LD_TYPE:
        return True
    if room_type1 in BED_TYPE and room_type2 in BED_TYPE:
        return True
    return False


def compute_vector_sim(source_feat, target_feat):
    # 0 表示类型 1 2 主功能区长宽(沙发、床) 5 6 副主功能区长宽(书桌、餐桌)
    # 11 客餐厅 12 客厅 13 餐厅
    add_score = 0.

    if (source_feat[0]) < 20:
        add = [0.0, 3.0, 1.0, 2.0, 0.0, 5.0, 5.0, 0.3, 0.3]

        if source_feat[0] == 12:
            add = [0.0, 100.0, 100.0, 10.0, 10.0, 0.0, 0.0, 5.3, 5.3]

        if source_feat[0] == 13:
            if target_feat[0] != 13:
                add_score += 200.
            add = [0.0, 0.0, 0.0, 0.0, 0.0, 100.5, 100.5, 5.3, 5.3]

        # 主要部分缺失 电视柜
        if source_feat[4] > 0.2 and target_feat[4] < 0.2:
            add_score += 10.

        # 主要部分缺失 桌
        if source_feat[5] > 0.2 and target_feat[5] < 0.2:
            add_score += 200.

        punish = [0.0, 0.5, 3.5, 0.1, 0.1, 3, 3, 0.3, 0.3]

    elif (source_feat[0]) < 30:
        add = [0.0, 100.0, 100.0, 0.1, 0.1, 0.1, 0.1, 5.0, 5.0]
        # 主要部分缺失 柜子
        if source_feat[-2] > 0.1 and target_feat[-2] < 0.1:
            add_score += 20.

        # 主要部分缺失 电视柜
        if source_feat[4] > 0.2 and target_feat[4] < 0.2:
            add_score += 20.

        punish = [0.0, 1.0, 2.0, 0.3, 0.3, 1.0, 1.0, 3.0, 3.0]

    else:
        add = [0.0, 100.0, 1.0, 0.8, 0.8, 1.5, 1.5, 1.0, 1.0]
        punish = [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    # 主要部分缺失 沙发/床
    if source_feat[0] != 13 and source_feat[1] > 0.1 and target_feat[1] < 0.1:
        add_score += 1000.

    for idx in range(1, len(source_feat)):
        if target_feat[idx] > source_feat[idx]:
            add_score += add[idx] * (target_feat[idx] - source_feat[idx])

    sum_list = [punish[idx] * (abs(source_feat[idx] - target_feat[idx])) for idx in range(1, len(source_feat))]
    return sum(sum_list) + add_score


def compute_role_vector_sim(role_vector, target_vector):
    add = 0.
    for group_name in role_vector:
        group_vec = role_vector[group_name]

        if group_name not in target_vector:
            return 30.

        for i in range(len(group_vec)):
            if target_vector[group_name][i] < 0.1 and group_vec[i] > 0.:
                add += 2.

            add += 1. * float(group_vec[i] > 0.) * abs(target_vector[group_name][i] - group_vec[i])

    return add


def room_group_search(room_type, room_vector, role_vector=None, key_list=[], target_style="", spec_style="", sample_num=10):
    scores = []
    hash_room = []
    # 主卧检索主卧
    if "MasterBedroom" in room_type:
        master_bedroom_flag = True
    else:
        master_bedroom_flag = False

    for key_data in key_list:

        if len(spec_style) > 0:
            if key_data['spec_style'] != spec_style:
                continue
        else:
            if len(target_style) > 0 and key_data['style_type'] != target_style:
                continue

        house_id, room_id = key_data['key'].split('_')

        if key_data['key'] in bad_key_list:
            continue

        if role_vector and key_data['key'] in bad_group_key_list:
            continue

        # 重复room_id去除
        if room_id in hash_room:
            continue
        else:
            hash_room.append(room_id)

        if master_bedroom_flag and "SecondBedroom" in room_id:
            continue

        if master_bedroom_flag and "SecondBedroom" in room_id:
            continue

        score = compute_vector_sim(room_vector, key_data['vector'])
        if role_vector:
            score += 2. * compute_role_vector_sim(role_vector, key_data['roles_vec'])
        scores.append((score, key_data))

    scores = sorted(scores, key=lambda x: x[0])

    # out_list = sorted(out_list, key=lambda x: x[0], reverse=True)
    # 增加功能区打分
    if len(scores) == 0:
        return []

    out_final_list = []
    for idx in range(min(sample_num, len(scores))):
        out_final_list.append({"key": scores[idx][1]['key'], "score": scores[idx][0], "mat_vec": scores[idx][1]['mat_vector']})

    return out_final_list


def get_base_target_rooms(room_param, target_style="Modern", spec_style="", source="", sample_num=10):
    room_type = get_search_room_type(room_param['type'])

    room_vector = room_param['feature']
    role_vector = None
    if 'role_vector' in room_param:
        role_vector = room_param['role_vector']

    key_list = []

    if len(source) == 0:
        source_list = ["pub"]
    else:
        source_list = []
        for key in source_house_info_keys:
            if key in source:
                source_list.append(key)

    if room_type in CHECK_ROOM_TYPE:

        if room_type in ["LivingRoom", "LivingDiningRoom"]:
            key_list = base_living_rooms_info["LivingDiningRoom"]
        else:
            for key in source_list:
                key_list += source_house_info[key][room_type]

        # 兜底尺寸
        if room_type == "LivingDiningRoom":
            if room_vector[5] * room_vector[6] < 0.1:
                room_vector[5] = 1.4
                room_vector[6] = 1.4

            if room_vector[1] * room_vector[2] < 0.1:
                room_vector[1] = 2.0
                room_vector[2] = 1.2

                room_vector[5] = 1.4
                room_vector[6] = 1.4

            if room_vector[3] * room_vector[4] < 0.1 and room_vector[1] * room_vector[2] > 9.0:
                room_vector[3] = 2.4
                room_vector[4] = 0.5

                room_vector[1] -= 0.1
                room_vector[2] -= 0.1

        elif room_type == "LivingRoom":
            if room_vector[1] * room_vector[2] < 0.1:
                room_vector[1] = 1.4
                room_vector[2] = 1.2

        key_final_match = room_group_search(room_type, room_vector, role_vector, key_list, target_style=target_style,
                                            spec_style=spec_style,
                                            sample_num=sample_num)
        return key_final_match

    return []


# 本地查找
def get_target_house_rooms(house_para, target_style, spec_style, source):
    return []


def get_house_sample_key(house_id, house_data=None, style="", spec_style="", source="pub+shejijia"):
    target_style = get_target_style(style)
    if house_data:
        house_vector = cal_house_vector(house_data)
        house_para = {}
        for room_info in house_data['room']:
            room_id = room_info['id']
            if room_id not in house_vector:
                continue

            house_para[room_id] = {"type": room_info['type'], "area": room_info['area'],
                                   "feature": house_vector[room_id]}
    else:
        house_para, _ = get_house_data(house_id)

    key_list = get_target_house_rooms(house_para, target_style, spec_style=spec_style, source=source)
    return []


def get_sample_key(house_id, room_id, room_data=None, style="Contemporary", spec_style="", source="pub+shejijia"):
    target_style = get_target_style(style)

    if room_data:
        room_vector, room_type = cal_room_vector(room_data)
        room_param = {'area': room_data['area'], 'type': room_type, 'feature': room_vector, 'sample': []}
    else:
        room_param, _ = get_room_data(house_id, room_id)

    key_list = get_base_target_rooms(room_param, target_style, spec_style=spec_style, source=source)
    if len(key_list) == 0:
        print(house_id + "_" + room_id + " get no local sample!")

    return [item['key'] for item in key_list]


def check_group_valid(group_one):
    group_valid_score = 0
    # 只检查主要家具
    need_check_role = ['table', 'sofa', 'bed']

    need_check_size_role = ['cabinet', 'airmore']

    for obj in group_one['obj_list']:
        if obj['role'] in need_check_role:
            group_valid_score += get_model_valid(obj['id'])

    return group_valid_score


def check_sample_group(group_one):
    for obj_idx in range(len(group_one['obj_list']) - 1, -1, -1):
        if "link" in group_one['obj_list'][obj_idx]['id']:
            group_one['obj_list'].pop(obj_idx)
        if group_one['obj_list'][obj_idx]['id'] in acc_not_need:
            group_one['obj_list'].pop(obj_idx)


def get_group_score_sim(target_vec, vector):
    # assert len(vector) == len(target_vec)
    su = 0.
    num = 0
    for i in range(len(vector)):
        if vector[i] < 0.01:
            continue

        su += abs(vector[i] - target_vec[i]) + float(vector[i] > target_vec[i] * 1.2)
        num += 1

    return su / float(num)


def get_base_target_group(vector, group_name, key_list, target_style="Modern"):
    scores = []
    for key_data in key_list:
        if key_data['style_type'] != target_style:
            continue
        if key_data['valid'][0] > 0 or key_data['valid'][2] > 0:
            continue
        house_id, room_id = key_data['key'].split('_')

        if key_data['key'] in bad_key_list:
            continue

        if key_data['key'] in bad_group_key_list:
            continue

        for target_group_name in key_data['group_vec']:
            if target_group_name == group_name:
                target_vec = key_data['group_vec'][target_group_name]
                score = get_group_score_sim(target_vec, vector)
                if score < 0.1:
                    return [house_id, room_id]
                else:
                    scores.append((score, key_data))

    if len(scores) > 0:
        scores = sorted(scores, key=lambda x: x[0])

        house_id, room_id = scores[0][1]['key'].split('_')
        return [house_id, room_id]
    else:
        return []


def get_used_group_room_type_list(group_name):
    info = {"Dining": ["DiningRoom", "LivingDiningRoom"],
            "Meeting": ["LivingRoom", "LivingDiningRoom"],
            "Work": ["MasterBedroom", "Bedroom"],
            "Cabinet": ["LivingDiningRoom", "DiningRoom"],
            "Bed": ["MasterBedroom", "Bedroom"],
            "Media": ["MasterBedroom", "LivingRoom"],
            "Armoire": ["MasterBedroom", "Bedroom"]}
    if group_name in info:
        return info[group_name]
    else:
        return ["MasterBedroom", "LivingRoom"]


def search_best_fit_group_sample(vector, group_name, room_type="", target_style="Modern"):
    if len(room_type) == 0:
        room_type_list = get_used_group_room_type_list(group_name)
    else:
        room_type_list = [room_type]

    for room_type in room_type_list:
        key_list = source_house_info[room_type]

        return_info = get_base_target_group(vector, group_name, key_list, target_style)
        if len(return_info) == 0:
            print("vector search group %s has no best fit!" % group_name)
            return {}

        house_id, room_id = return_info[0], return_info[1]
        print(group_name, house_id + "_" + room_id)
        room_para, room_layout, room_group = get_room_sample(house_id, room_id)

        best_fit_group_list = []
        for group in room_group['group_functional']:
            if group['type'] == group_name:
                best_fit_group_list.append([group['size'][0] * group['size'][2], group])
        if len(best_fit_group_list) == 0:
            print("vector search group %s has no best fit!" % group_name)
            return {}
        scores = sorted(best_fit_group_list, key=lambda x: x[0])

        return scores[0][1]


if __name__ == '__main__':
    import time

    t = time.time()
    get_house_sample_key("6d3037cc-2ca8-4a87-87ac-23125539ceaa")
    # print(get_sample_key("6d3037cc-2ca8-4a87-87ac-23125539ceaa", "DiningRoom-7994"))
    # get_base_target_rooms()
    print(time.time() - t)
