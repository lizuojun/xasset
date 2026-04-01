from Furniture.furniture import get_furniture_turn
from HouseSearch.house_propose import get_base_target_rooms, CHECK_ROOM_TYPE
from HouseSearch.house_sample_parse import house_search_parse_sample_key
from HouseSearch.house_style import get_check_styles
from ImportHouse.room_search import cal_room_vector, get_furniture_data, get_room_sample

CHECK_GROUP_VECTOR_RULES = {
    "Dining": {
        "table": 1,
        "chair": 2
    },
    "Meeting": {
        "sofa": 1,
        "side sofa": 2,
        "table": 1,
        "side table": 1
    },
    "Work": {
        "table": 1,
        "chair": 1
    },
    "Cabinet": {
        "cabinet": 1
    },
    "Rest": {
        "table": 1,
        "chair": 2
    },
    "Bed": {
        "bed": 1,
        "side table": 1,
        "table": 1
    },
    "Media": {
        "tv": 1,
        "table": 1
    },
    "Armoire": {
        "armoire": 1
    },
}


def house_search_sample_keys_list_with_seeds(house_data, target_style, sample_num, seeds, seeds_role_notes):
    house_sample_list = house_search_sample_keys_list(house_data, target_style=target_style, sample_num=sample_num,
                                                      seeds=seeds, seeds_role_notes=seeds_role_notes)

    return house_sample_list


def compute_room_role_vector(seed_info_list, room_type):
    out_info = {}
    checked_roles_size = {}

    for seed in seed_info_list:
        jid = seed["jid"]
        group_type = seed["group"]
        if group_type not in CHECK_GROUP_VECTOR_RULES:
            continue

        if group_type not in checked_roles_size:
            checked_roles_size[group_type] = {}

        used_jid = []
        need_roles_info = CHECK_GROUP_VECTOR_RULES[group_type]

        role = seed['role']
        if role not in need_roles_info:
            continue

        _, _, obj_size = get_furniture_data(jid)
        if abs(get_furniture_turn(jid)) == 1:
            obj_size[0], obj_size[2] = obj_size[2], obj_size[0]
        role_size = [obj_size[i] / 100. for i in range(3)]

        if role_size[0] < 0.1:
            role_size[0] += 0.1
        if role_size[2] < 0.1:
            role_size[2] += 0.1

        if role not in checked_roles_size[group_type]:
            checked_roles_size[group_type][role] = [role_size]
            used_jid.append(jid)
        else:
            if jid in used_jid:
                continue
            checked_roles_size[group_type][role].append(role_size)

    # 出特征
    for group_type in checked_roles_size:
        vec_all = []
        need_roles_info = CHECK_GROUP_VECTOR_RULES[group_type]
        for key_role in need_roles_info:
            num = need_roles_info[key_role]
            vec = [0., 0.] * num
            if key_role in checked_roles_size[group_type]:
                area_list = [[i, i[0] * i[1] * i[2]] for i in checked_roles_size[group_type][key_role]]
                area_list = sorted(area_list, reverse=True, key=lambda x: x[1])
                for role_idx in range(len(area_list[:num])):
                    vec[2 * role_idx + 0] = round(area_list[role_idx][0][0], 1)
                    vec[2 * role_idx + 1] = round(area_list[role_idx][0][2], 1)

            vec_all += vec

        if group_type in out_info:
            old_vec = out_info[group_type]
            if vec_all[0] * vec_all[1] > old_vec[0] * old_vec[1]:
                out_info[group_type] = vec_all
        else:
            out_info[group_type] = vec_all

    return out_info


def get_region_vector(room_data):
    ROOM_TYPE_CODE = {
        'LivingDiningRoom': 11, 'LivingRoom': 12, 'DiningRoom': 13,
        'MasterBedroom': 21, 'SecondBedroom': 22, 'Bedroom': 23, 'KidsRoom': 24, 'ElderlyRoom': 25, 'NannyRoom': 26,
        'Library': 31,
        'Kitchen': 51,
        'MasterBathroom': 61, 'SecondBathroom': 62, 'Bathroom': 63,
        'Balcony': 71, 'Terrace': 72, 'Lounge': 73, 'LaundryRoom': 74,
        'Hallway': 81, 'Aisle': 82, 'Corridor': 83, 'Stairwell': 84,
        'StorageRoom': 91, 'CloakRoom': 92, 'EquipmentRoom': 93, 'Auditorium': 94, 'OtherRoom': 95,
        'Courtyard': 96, 'Garage': 97,
        'none': 99
    }
    room_type = room_data["type"]
    # 特征信息
    if room_type in ROOM_TYPE_CODE:
        room_code = ROOM_TYPE_CODE[room_type]
    else:
        room_code = ROOM_TYPE_CODE['none']

    room_vector = [room_code, 0, 0, 0, 0, 0, 0, 0, 0]
    if "region_info" not in room_data:
        return room_vector

    for group_one in room_data["region_info"]:
        group_type, group_size = group_one['type'], group_one['size'][:]
        # 计算特征
        if group_type in ['Meeting', 'Bed', 'Bath']:
            if room_vector[1] + room_vector[2] < group_size[0] + group_size[2]:
                room_vector[1], room_vector[2] = round(group_size[0], 1), round(group_size[2], 1)
        elif group_type in ['Media']:
            if room_vector[3] + room_vector[4] < group_size[0] + group_size[2]:
                room_vector[3], room_vector[4] = round(group_size[0], 1), round(group_size[2], 1)
        elif group_type in ['Dining']:
            if room_vector[5] + room_vector[6] < group_size[0] + group_size[2]:
                room_vector[5], room_vector[6] = round(group_size[0], 1), round(group_size[2], 1)
        elif group_type in ['Work', 'Rest'] and room_type not in ['LivingDiningRoom', 'LivingRoom']:
            if room_vector[5] + room_vector[6] < group_size[0] + group_size[2]:
                room_vector[5], room_vector[6] = round(group_size[0], 1), round(group_size[2], 1)
        elif group_type in ['Toilet']:
            if room_vector[5] + room_vector[6] < group_size[0] + group_size[2]:
                room_vector[5], room_vector[6] = round(group_size[0], 1), round(group_size[2], 1)
        elif group_type in ['Armoire', 'Cabinet', 'Appliance']:
            if room_vector[7] + room_vector[8] < group_size[0] + group_size[2]:
                room_vector[7], room_vector[8] = round(group_size[0], 1), round(group_size[2], 1)

    return room_vector, room_type


# 按每个房间进行查找, 四个风格查找key
def house_search_sample_keys_list(house_data, sample_num=4, target_style="random", seeds=None, seeds_role_notes=None):
    check_style = get_check_styles(target_style)
    # check_style = {"Luxury": [], "Modern": [], "Nordic": [], "Japanese": []}
    need_room_table = {}
    for room_data in house_data['room']:
        room_id = room_data['id']
        change_room_type = ""

        if room_data["type"] == "NannyRoom":
            change_room_type = "ElderlyRoom"
            need_room_table[room_id] = {}
        else:
            if room_data["type"] in CHECK_ROOM_TYPE:
                need_room_table[room_id] = {}
            else:
                continue
        if "region_info" in room_data and len(room_data["region_info"]) > 0:
            room_vector, room_type = get_region_vector(room_data)
        else:
            room_vector, room_type = cal_room_vector(room_data)
        if len(change_room_type) > 0:
            room_type = change_room_type

        room_param = {'area': room_data['area'], 'type': room_type, 'feature': room_vector,
                      'role_vector': [], 'sample': []}
        # 软装种子
        if seeds and room_id in seeds:
            seeds_list = []
            for jid in seeds[room_id]:
                if jid not in seeds_role_notes:
                    continue

                seeds_list.append(
                    {"jid": jid, "group": seeds_role_notes[jid]["group"], "role": seeds_role_notes[jid]["role"]})

            room_param['role_vector'] = compute_room_role_vector(seeds_list, room_type)

        for style in check_style:
            need_room_table[room_id][style] = get_room_sample_key_with_score(room_param, style=style, spec_style="")

    # 计算所有房间之和
    all_scores = []
    for check_idx in range(10):
        for style in check_style:
            add_scores = 0.
            for room_id in need_room_table:
                sample_keys = need_room_table[room_id][style]
                if len(sample_keys) > check_idx:
                    now_score = sample_keys[check_idx]['score']
                    add_scores += now_score
                else:
                    add_scores += 100.

            all_scores.append((add_scores, [style, check_idx]))

    if target_style == 'random' or target_style == '':
        all_scores = sorted(all_scores, key=lambda x: x[0])

    out_sample_info_list = []
    for sample_idx in range(sample_num):
        score = all_scores[sample_idx][0]
        style, check_idx = all_scores[sample_idx][1]
        print(style)
        room_sample_info = {"score": score, "style": style, "sample": {}, "mat_vec": {}}
        for room_id in need_room_table:
            if len(need_room_table[room_id][style]) > check_idx:
                room_sample_info["sample"][room_id] = need_room_table[room_id][style][check_idx]['key']
                room_sample_info['mat_vec'][room_id] = need_room_table[room_id][style][check_idx]['mat_vec']

        out_sample_info_list.append(room_sample_info)

    return out_sample_info_list


# 根据sample_key查找对应的sample_data
def get_sample_data_from_house_sample_keys(house_sample_keys_info):
    layout_sample_info = {"info": house_sample_keys_info, "sample": {}}
    for room_id in house_sample_keys_info['sample']:
        _, layout, _, _ = house_search_parse_sample_key(house_sample_keys_info['sample'][room_id])

        for target_room_id in layout:
            layout_sample_info['sample'][room_id] = layout[target_room_id]
            for scheme in layout[target_room_id]["layout_scheme"]:
                scheme["target_sample_house"] = scheme["source_house"]
                scheme["target_sample_room"] = scheme["source_room"]

                scheme["source_house"] = "sample_house"
                scheme["source_room"] += "_diy"
            break

    return layout_sample_info


# 包一层入口
def get_room_sample_key_with_score(room_param, style, spec_style, source="pub", sample_num=10):
    return get_base_target_rooms(room_param, style, spec_style=spec_style, source=source, sample_num=sample_num)


if __name__ == '__main__':
    room_para, room_layout, room_group = get_room_sample("5469cba6-3605-410a-bb5c-b6b3478aebb2",
                                                         "LivingDiningRoom-11239")
    print()
