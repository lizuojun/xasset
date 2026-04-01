import datetime
import json
import os

from HouseSearch.house_propose import get_base_target_rooms, get_search_room_type, CHECK_ROOM_TYPE, room_group_search
from ImportHouse.room_search import cal_room_vector, get_room_data, get_house_sample, get_house_data, \
    get_house_sample_layout, DATA_DIR_IMPORT_SAMPLE, DATA_OSS_DATABASE, DATA_OSS_SAMPLE, oss_download_file, \
    cal_sample_vector


def get_sample_group_oss(house_id):
    house_bucket = DATA_OSS_DATABASE
    # 查找信息
    sample_group = {}
    if True:
        # 位置
        house_file = house_id + '_group.json'
        house_path = os.path.join(DATA_DIR_IMPORT_SAMPLE, house_file)
        # 读取
        if os.path.exists(house_path):
            print('fetch house group', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'tmp')
            try:
                sample_group = json.load(open(house_path, 'r'))
            except:
                sample_group = {}
        # 读取
        if len(sample_group) <= 0:
            print('fetch house group', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'url')
            oss_download_file(DATA_OSS_SAMPLE + '/' + house_file, house_path, house_bucket)
            if os.path.exists(house_path):
                sample_group = json.load(open(house_path, 'r'))

    return sample_group


def get_sample_key_from_list(house_id, room_id, room_data=None, sample_num=10, sample_key_list=[]):
    if len(sample_key_list) == 0:
        return []

    if room_data:
        room_vector, room_type = cal_room_vector(room_data)
        room_param = {'area': room_data['area'], 'type': room_type, 'feature': room_vector, 'sample': []}
    else:
        room_param, _ = get_room_data(house_id, room_id)

    key_list = get_base_target_rooms_from_list(room_param, sample_key_list, sample_num=sample_num)
    if len(key_list) == 0:
        print(house_id + "_" + room_id + " get no sample!")

    return [item['key'] for item in key_list]


def get_source_house_info_from_list(sample_list):
    ROOM_TYPE_DICT = {"LivingRoom": [], 'LivingDiningRoom': [], 'DiningRoom': [], 'Bedroom': [], 'KidsRoom': [],
                      "ElderlyRoom": [], "Library": []}
    for house_id in sample_list:
        # house_para, house_data = get_house_data(house_id, reload=False)
        try:
            sample_group = get_sample_group_oss(house_id)
        except:
            continue
        # sample_para, sample_layout, sample_group = get_house_sample(house_id, reload=False)

        for room_id in sample_group:
            room_type = sample_group[room_id]['room_type']
            change_type = get_search_room_type(room_type)

            if change_type in ROOM_TYPE_DICT:
                vector = cal_sample_vector(sample_group[room_id]['group_functional'], change_type)

                if change_type == "LivingDiningRoom" and vector[1] * vector[2] < 0.1:
                    change_type = "DiningRoom"
                    if vector[5] * vector[6] < 0.1:
                        continue

                if change_type == "LivingDiningRoom" and vector[5] * vector[6] < 0.1:
                    change_type = "LivingRoom"
                    if vector[1] * vector[2] < 0.1:
                        continue

                ROOM_TYPE_DICT[change_type].append({'key': house_id + '_' + room_id, 'vector': vector,
                                                    'spec_style': "",
                                                    'style_type': ""})
    return ROOM_TYPE_DICT


def get_base_target_rooms_from_list(room_param, sample_list, sample_num=10):
    temp_source_house_info = get_source_house_info_from_list(sample_list)

    room_type = get_search_room_type(room_param['type'])

    room_vector = room_param['feature']
    key_list = []

    if room_type in CHECK_ROOM_TYPE:
        key_list = temp_source_house_info[room_type]

        if room_type == "LivingRoom":
            key_list += temp_source_house_info["LivingDiningRoom"]
        elif room_type == "LivingDiningRoom":
            key_list += temp_source_house_info["LivingRoom"]

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

        key_final_match = room_group_search(room_type, room_vector, None, key_list, target_style="",
                                            spec_style="",
                                            sample_num=sample_num)
        return key_final_match

    return []