import os
import json

# from Demo.check.utl import get_room_group_score
from Demo.test_local import get_design_json_daily
# from Furniture.data_oss import oss_get_json_file
from House.house_sample import compute_room_vector, extract_room_layout_by_info, get_furniture_turn, correct_house_data
from HouseSearch.data_oss import oss_download_file, oss_exist_file
from HouseSearch.house_propose import get_sample_key
from HouseSearch.model.model_hsf import get_model_valid

from HouseSearch.source.basic_style import check_base_style, STYLE_DICT
from ImportHouse.room_search import cal_room_vector, get_house_data, cal_sample_vector, get_room_data, get_house_sample, \
    get_room_sample, get_house_sample_layout, DATA_OSS_SAMPLE, DATA_DIR_IMPORT_SAMPLE
from Extract.group_material import house_data_group_wall
from Extract.get_house_data_universal import get_house_data_univ
from Extract.group_feature_wall import house_data_group_feature_wall
from Extract.group_win_door import house_data_group_win_door
from Extract.extract_sample import extract_sample_house
import traceback

test_list = ["db312f64-6013-4761-9460-ce18fd7c0538",
             "fe6fd6f7-cd8d-462a-bf2f-918444f9c796",
             "a57ecd5e-6be3-46f9-8a5c-29b132c1ac6c",
             "e3277086-1db1-4d23-a1fc-9c9ead6217a6",
             "7d1b2560-e926-4674-91e4-2199df910aa8",
             "e1d818ad-2ceb-4ad6-b348-f6c6837c05b7",
             "3f25fea2-d7ba-45f6-a73e-e10a1fc1c75c"]

sample_test = [
    "2be51abc-8f40-41a8-8c56-f7abb315be26",
    "79b1a854-1c6f-4451-9760-2802bebbaf3b",
    "75b8e799-d359-4740-956e-75ffab957475",
    "8c1d0e79-14d6-4027-9099-a30c7da0ea6c",
    "5174e875-876c-4c89-b64d-e179a9335155",
    "a7e43f69-5ab3-4cf0-8b5b-aec3ee39fb8b",
    "800316e9-70e8-40b6-9bac-19a3e6d0012b",
    "ad5c441c-36f3-46f5-a045-881cf1a2e05e",
    "58059e97-a503-4be5-9ded-11903951cbbc",
    "4da88383-ad96-49ff-ab5a-3024b841ad7d",
    "1d8333f5-7f2b-4aff-ba8a-d2b50ddfea31",
    "6b8fc980-1fa1-44d3-a0b6-40a92b3dcedb",
    "bb59ab9f-8fde-4b46-85ca-2623f3185617",
    "ad6386d3-2221-4c50-ada7-50bd02731a7e",
    "ba0cc09f-5e9d-4b90-be05-7200b6c38f47",
    "0af5f065-dc78-424a-8da5-2d5e060c2eac",
    "b9d1bfc9-e39a-4753-b326-b888c9519567",
    "b841eb60-d776-40d7-9094-40e4c8a99df5",
    "e0dc5270-ee9c-41a2-9923-6056ece81f84",
    "6d3a3607-1c41-4325-a6b3-41d13d016d06",
    "fef31a43-5e31-44d6-99e5-8565c8ba3c17",
    "c5059b3f-6393-4356-94ef-ac48331fc2fa",
    "2f4c7227-2911-4e57-9db4-d0d8b13c6220",
    "440cbe0b-51d6-4d4f-91ba-19742b904911",
    "151aa01a-5c23-4466-84b7-996642363d93",
    "810f174f-8030-498a-938d-3199aad8860c",
    "9111db2b-06b6-4e92-a146-88ce47398ad9",
    "325e972c-a9a6-4f54-8001-f6bd3b7c1424",
    "b29c73b2-b860-44ce-94c1-b22d43015601",
    "899d2eca-ab69-42f8-9490-d6a62a0a831e",
    "29cae2f8-8ffa-4280-8853-252842a721f8",
    "fb543c4f-f49c-4b22-93fb-ea55a1d1a025",
    "36adc97a-d26e-4794-a4b1-1c9e8a4be17a",
    "228a11f0-ed42-414e-ba19-ad5b6498a17e",
    "d5877a9a-b068-43f8-816d-7a8c8e72ba63",
    "1e420429-c30c-422d-ab08-51bb9fdb3372",
    "3c2874c2-d67e-4ece-bf40-ac69fbe75e0e",
    "ae6e156f-ac83-415a-affe-5184309c38e9",
    "f3d3c56d-0213-46e9-bbb7-10e760b34290",
    "f464fd22-c684-465d-9256-e7b2cad9ee81",
    "5cb8f6b7-9b55-417a-921c-522a0c3d92a8",
    "5a40c187-601f-439c-a2e8-b19587077cb2",
    "776b23df-db50-490d-9270-62b8bbe133d8",
    "74e439d9-d8bd-4eee-a8dd-f8662f429402",
    "67a513a8-cfcf-44b0-a3db-cbc2e90e9774",
    "4f582660-1bff-4b19-afb6-77eed1748bdb",
    "a1270191-e974-4d21-8aaf-0ec072819ec7",
    "e168b16e-8645-4215-85a8-83d56750a10d",
    "e6366803-582a-4d54-abbc-1e0fe1d5f156"
]

CHECK_ROOM_TYPE = ["DiningRoom", "LivingDiningRoom", "LivingRoom", "MasterBedroom", "Bedroom", "SecondBedroom",
                   "ElderlyRoom"]
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
        "tv":1,
        "table": 1
    },
    "Armoire": {
        "armoire": 1
    },
}
CHECK_MIN_CODE_GROUP = {"Dining": 120, "Work": 110, "Bed": 10000, "Meeting": 100001}

# source_id_list = open("room_source_list", 'r').read().split()
house_data_path = os.path.join(os.path.dirname(__file__), 'temp', 'house')
group_data_path = os.path.join(os.path.dirname(__file__), 'temp', 'group')
# no_need_jids = open("./temp/all_jids.txt", "r").read().split()
if not os.path.exists(house_data_path):
    os.makedirs(house_data_path)

if not os.path.exists(group_data_path):
    os.makedirs(group_data_path)


def get_group_vector(group_list):
    out_info = {}
    out_code = {}
    for group in group_list:
        group_code = group['code']
        if group['type'] not in CHECK_GROUP_VECTOR_RULES:
            continue

        checked_roles_size = {}
        used_jid = []
        need_roles_info = CHECK_GROUP_VECTOR_RULES[group['type']]
        for obj in group['obj_list']:
            role = obj['role']

            sofa_mirror_flag = False
            if role == "sofa" and obj['scale'][0] < -0.5:
                sofa_mirror_flag = True

            role_size = [obj['size'][i] * obj['scale'][i] / 100. for i in range(3)]

            if role not in need_roles_info:
                continue

            if role not in checked_roles_size:
                checked_roles_size[role] = [role_size]
                used_jid.append(obj['id'])
            else:
                if obj['id'] in used_jid:
                    continue
                checked_roles_size[role].append(role_size)

        # 出特征
        vec_all = []
        for key_role in need_roles_info:
            num = need_roles_info[key_role]
            vec = [0., 0.] * num
            if key_role in checked_roles_size:

                area_list = [[i, i[0] * i[1] * i[2]] for i in checked_roles_size[key_role]]
                area_list = sorted(area_list, reverse=True, key=lambda x: x[1])
                for role_idx in range(len(area_list[:num])):
                    vec[2 * role_idx + 0] = round(area_list[role_idx][0][0], 1)
                    vec[2 * role_idx + 1] = round(area_list[role_idx][0][2], 1)

            vec_all += vec

        if group['type'] in out_info:
            old_vec = out_info[group['type']]
            if vec_all[0] * vec_all[1] > old_vec[0] * old_vec[1]:
                out_info[group['type']] = vec_all
                out_code[group['type']] = group_code
        else:
            out_info[group['type']] = vec_all
            out_code[group['type']] = group_code

    return out_info, out_code


def get_search_room_type(room_type):
    if room_type in ['SecondBedroom', 'Bedroom', 'MasterBedroom']:
        return 'Bedroom'
    return room_type


def get_search_style(style, group_list):
    style = check_base_style(style)
    if style == "Other":
        style_dict = {}
        for i in STYLE_DICT:
            style_dict[i] = 0

        for group_info in group_list:
            new_style = check_base_style(group_info['style'])
            if new_style != "Other":
                style_dict[new_style] += 1
        max_num = 0
        max_key = "Other"
        for key in style_dict:
            if style_dict[key] > max_num:
                max_key = key
                max_num = style_dict[key]
        return max_key
    else:
        return style


def get_all_jids(all_jids, room_group_info):
    for group in room_group_info['group_functional']:
        for obj in group['obj_list']:
            if obj['id'] in all_jids:
                continue
            else:
                if 'bed set' in obj['type'] or 'sofa set' in obj['type'] or 'dining set' in obj['type']:
                    continue

                if 'wardrobe' in obj['type']:
                    continue
                if obj['id'] not in no_need_jids:
                    all_jids.append(obj['id'])
    for group in room_group_info['group_decorative']:
        for obj in group['obj_list']:
            if obj['id'] in all_jids:
                continue
            else:
                # if 'bed set' in obj['type'] or 'sofa set' in obj['type'] or 'dining set' in obj['type']:
                #     continue
                #
                # if 'wardrobe' in obj['type']:
                #     continue
                if obj['id'] not in no_need_jids:
                    all_jids.append(obj['id'])


def check_group_code(group_code):
    for group_name in group_code:
        if group_name in CHECK_MIN_CODE_GROUP:
            if group_code[group_name] < CHECK_MIN_CODE_GROUP[group_name]:
                return False

    return True


def check_group_valid(group_one):
    group_valid_score = 0
    # 只检查主要家具
    need_check_role = ['table', 'sofa', 'bed']

    need_check_size_role = ['cabinet', 'airmore']

    for obj in group_one['obj_list']:
        if obj['role'] in need_check_role:
            group_valid_score += get_model_valid(obj['id'])

    return group_valid_score


def cal_sample_valid(group_list, room_type):
    room_valid = [0, 0, 0, 0]
    for group_one in group_list:
        group_type, object_type, object_main, object_info = group_one['type'], '', '', {}
        if 'obj_type' in group_one:
            object_type = group_one['obj_type']
        if 'obj_main' in group_one:
            object_main = group_one['obj_main']
        if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
            object_info = group_one['obj_list'][0]
        if group_type in ['Meeting', 'Bed', 'Bath']:
            if 'bed set' in object_type or 'sofa set' in object_type:
                room_valid[0] += 1
            elif len(object_main) > 0 and abs(get_furniture_turn(object_main)) >= 1:
                room_valid[0] += 1
            elif len(object_info) > 0 and group_type in ['Meeting']:
                object_size = object_info['size']
                if object_size[2] > object_size[0] * 1.5:
                    room_valid[0] += 1
            else:
                room_valid[0] += 0  # check_group_valid(group_one)
        elif group_type in ['Media']:
            pass
        elif group_type in ['Dining', 'Work', 'Rest', 'Toilet']:
            if 'dinning set' in object_type:
                room_valid[2] += 1
            else:
                room_valid[0] += 0  # check_group_valid(group_one)
        elif group_type in ['Armoire', 'Cabinet', 'Appliance']:
            room_valid[3] += 0  # check_group_valid(group_one)
    return room_valid


def gen_base_source_data(input_id_list, source="pub"):
    ROOM_TYPE_DICT = {"LivingRoom": [], 'LivingDiningRoom': [], 'DiningRoom': [], 'Bedroom': [], 'KidsRoom': [],
                      "ElderlyRoom": [], "Library": []}
    need_sofa_jids_list = []
    print(len(input_id_list))
    for ind, item_info in enumerate(input_id_list):
        house_id, base_style, spec_style, design_url = item_info[0], item_info[1], item_info[2], item_info[3]

        # house_id = '520b0072-72cc-4774-85d9-2404d474539e'
        # design_url = ''
        print(ind, house_id)
        try:
            # house_para, house_data = get_house_data(house_id, design_url, reload=True)
            # sample_para, house_data, sample_layout, sample_group = get_house_sample(house_id, reload=True)

            house_data, sample_layout = extract_sample_house(house_id, design_url)

            for room_data in house_data['room']:
                room_id = room_data['id']

                room_layout_info, room_group_info = extract_room_layout_by_info(room_data)

                change_type = get_search_room_type(room_group_info['room_type'])
                if len(base_style) == 0:
                    change_style = get_search_style(room_group_info['room_style'], room_group_info['group_functional'])
                else:
                    change_style = base_style

                if change_type in ROOM_TYPE_DICT:
                    room_valid_score = cal_sample_valid(room_group_info['group_functional'], change_type)
                    if sum(room_valid_score) > 0:
                        continue

                    group_vector_info, group_code = get_group_vector(room_group_info['group_functional'])

                    if not check_group_code(group_code):
                        continue

                    if change_style == "Other" and change_type != "KidsRoom":
                        print(room_group_info['room_style'])
                        continue
                    vector = cal_sample_vector(room_group_info['group_functional'], room_group_info['room_type'])

                    if change_type == "LivingDiningRoom" and vector[1] * vector[2] < 0.1:
                        change_type = "DiningRoom"
                        if vector[5] * vector[6] < 0.1:
                            continue

                    if change_type == "LivingDiningRoom" and vector[5] * vector[6] < 0.1:
                        change_type = "LivingRoom"
                        if vector[1] * vector[2] < 0.1:
                            continue

                    # if change_type in ["LivingDiningRoom", "LivingRoom"]:
                    #     for group in room_group_info['group_functional']:
                    #         if group['type'] == "Meeting":
                    #             if group['obj_main'] not in need_sofa_jids_list and 'sofa' in group['obj_type']:
                    #                 need_sofa_jids_list.append(group['obj_main'])

                    # group_score = get_room_group_score(room_group_info['group_functional'], change_type)
                    #
                    # if group_score < 200:
                    #     continue

                    ROOM_TYPE_DICT[change_type].append({'key': house_id + '_' + room_id, 'vector': vector,
                                                        'spec_style': spec_style,
                                                        'style_type': change_style})
        except Exception as e:
            traceback.print_exc()
            print(e)
            print("error!")
            continue

    print(need_sofa_jids_list)

    return ROOM_TYPE_DICT
    # with open("group_sample_score_new_update.json", 'w') as f:
    #     f.write(json.dumps(ROOM_TYPE_DICT, indent=4))


def refine_group_sample():
    out_json = json.load(open("group_sample_data.json", "r"))
    for source in ["pub", "shejijia"]:
        for room_type in out_json[source]:
            for item_idx in range(len(out_json[source][room_type]) - 1, -1, -1):
                sample_info = out_json[source][room_type][item_idx]
                if "Meeting" in sample_info['group_code']:
                    if sample_info['group_code']['Meeting'] < 100001:
                        out_json[source][room_type].pop(item_idx)

    with open("group_sample_data_refine.json", "w") as f:
        f.write(json.dumps(out_json, indent=4, ensure_ascii=False))


if __name__ == '__main__':


    all_source = json.load(open("./source/source.json", 'r'))
    out_json = {}
    #
    # # add
    # out_json = json.load(open("./group_sample_data.json", 'r'))
    for name in ["leju"]:
        out_json[name] = gen_base_source_data(all_source[name], name)
    # # print()
    with open("group_sample_data_new.json", "w") as f:
        f.write(json.dumps(out_json, indent=4, ensure_ascii=False))

    # out_json = {}
    # all_source1 = json.load(open("./out_sample_1.json", 'r'))
    # all_source2 = json.load(open("./out_sample_1.json", 'r'))
    # for room_type in all_source1['pub_all']:
    #     if room_type in all_source2['pub_all']:
    #         all_source1['pub_all'][room_type] += all_source2['pub_all'][room_type]
    #
    # with open("group_sample_data_pub_all.json", "w") as f:
    #     f.write(json.dumps(all_source1, indent=4, ensure_ascii=False))

    # all_source = json.load(open("./group_sample_data_pub_all.json", 'r'))
    #
    # out_used_list = []
    # for room_type in all_source['pub']:
    #     if room_type in all_source['pub']:
    #         for item in all_source['pub'][room_type]:
    #             house_id, room_id = item['key'].split('_')
    #             house_file = house_id + '_layout.json'
    #
    #             try:
    #                 house_path = os.path.join(DATA_DIR_IMPORT_SAMPLE, house_file)
    #                 sample_layout = {}
    #                 # 读取
    #                 if os.path.exists(house_path):
    #                     # print('fetch house layout', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'tmp')
    #                     sample_layout = json.load(open(house_path, 'r'))
    #                 # 读取
    #                 if len(sample_layout) <= 0:
    #                     # print('fetch house layout', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'url')
    #                     oss_download_file(DATA_OSS_SAMPLE + '/' + house_file, house_path, "ihome-alg-sample-data")
    #                     if os.path.exists(house_path):
    #                         sample_layout = json.load(open(house_path, 'r'))
    #
    #                 base_style = check_base_style(sample_layout[room_id]['room_style'])
    #             except:
    #                 continue
    #             print(sample_layout[room_id]['room_style'], base_style)
    #             item['style_type'] = base_style
    #
    # with open("group_sample_data_pub_all.json", "w") as f:
    #     f.write(json.dumps(all_source, indent=4, ensure_ascii=False))
    #
    # all_source = json.load(open("./group_sample_data_pub_all.json", 'r'))
    #
    # out_used_list = []
    # for room_type in all_source['pub']:
    #     if room_type in all_source['pub']:
    #         for item in all_source['pub'][room_type]:
    #             house_id, room_id = item['key'].split('_')
    #             if house_id not in out_used_list:
    #                 out_used_list.append(house_id)
    #
    # print(len(out_used_list))
    # 1/0
    # out_json = {}
    # all_source1 = json.load(open("./out_sample_1.json", 'r'))
    # all_source2 = json.load(open("./out_sample_2.json", 'r'))
    # for room_type in all_source1['pub_all']:
    #     if room_type in all_source2['pub_all']:
    #         all_source1['pub_all'][room_type] += all_source2['pub_all'][room_type]
    #
    # with open("group_sample_data_pub_all.json", "w") as f:
    #     f.write(json.dumps(all_source1, indent=4, ensure_ascii=False))

    # all_source1 = json.load(open("./source/source_pub_all.json", 'r'))
    # all_source2 = json.load(open("./source/source_pub_all_2.json", 'r'))
    #
    # need_list = []
    # idx = 0
    # for item in all_source1['pub_all']:
    #     jid, design_url = item[0], item[-1]
    #     if oss_exist_file("houseV2/" + jid + '.json', "ihome-alg-sample-data"):
    #         print(idx)
    #         idx += 1
    #         need_list.append(jid)
    #
    # for item in all_source2['pub_all_2']:
    #     jid, design_url = item[0], item[-1]
    #     if oss_exist_file("houseV2/" + jid + '.json', "ihome-alg-sample-data"):
    #         print(idx)
    #         idx += 1
    #         need_list.append(jid)
    #
    # with open("all_need_jid_list.json", "w") as f:
    #     f.write(json.dumps(need_list, indent=4, ensure_ascii=False))
    # al_lines = open("odps_data_20210425.txt", "r").readlines()
    # test_line = "00021164-4fc8-472d-88b8-dd480dfd51e0,"
    # with open("test_data.txt","w") as f:
    #     all_jids = json.load(open("all_need_jid_list.json", 'r'))
    #     for jid in all_jids:
    #         print(jid)
    #         json_object = oss_get_json_file("houseV2/" + jid + '.json', "ihome-alg-sample-data")
    #         a = json.dumps(json_object)
    #         if len(a) < 1000:
    #             continue
    #
    #         f.write(jid + "," + a+"\n")

    # with open("odps_data_20210425_new.txt", "w") as f:
    #     for line in al_lines:
    #         jid = line[:len(test_line) - 1]
    #         data = line[len(test_line):]
    #         f.write(jid + "#" + data + "\n")
