"""
根据content_type与group_type检索样板间group_info/scene.json

种子家具到样板间group的映射

"""

import json
import os
import random

source_scene_info = json.load(open(os.path.join(os.path.dirname(__file__), "source/seeds_scene_table.json"), 'r'))
jid_content_info = json.load(open(os.path.join(os.path.dirname(__file__), "source/seeds_content_table.json"), "r"))
scene_map = json.load(open(os.path.join(os.path.dirname(__file__), "source/scene_map.json"), 'r'))


def search_scene_list(room_type_list, group_name_list, role_list, layout_num=2, search_random=True, seed=2,
                      content_type_list=[]):
    max_list = search_max_scene_group(room_type_list, group_name_list, role_list, layout_num, content_type_list)
    if search_random:
        random.seed(seed)
        random.shuffle(max_list)

    return max_list[:layout_num]


def check_jid_content_type(jid, content_type_list):
    if len(content_type_list) == 0:
        return True
    if jid in jid_content_info:
        return jid_content_info[jid] in content_type_list

    return False


def search_max_scene_group(room_type_list, group_name_list, role_list, layout_num=2, content_type_list=[]):
    """
    :param group_name:
    :param room_type_list:
    :param role_list:
    :return: scene_info_list = [{"sample_key":{}, "sample_info":{}, "scene_url":""}]
    """
    max_length = 5 * layout_num
    search_key_list = []
    if len(group_name_list) == 0:
        group_name_list = ["Work", "Rest", "Meeting", "Dining"]

    for group_name in group_name_list:
        if group_name not in source_scene_info:
            continue

        for role_name in source_scene_info[group_name]:
            if role_name in role_list or len(role_list) == 0:
                for jid in source_scene_info[group_name][role_name]:

                    if not check_jid_content_type(jid, content_type_list):
                        continue

                    sample_keys = source_scene_info[group_name][role_name][jid]
                    for sample_key in sample_keys:
                        try:
                            house_id, room_id = sample_key.split('_')
                            room_type, _ = room_id.split("-")
                        except:
                            continue

                        # todo jid 比较

                        if house_id not in scene_map:
                            continue

                        scene_url = scene_map[house_id]

                        if scene_url[-1] == '\n':
                            scene_url = scene_url[:-1]

                        if room_type in room_type_list or len(room_type_list) == 0:
                            info = {"sample_key": sample_key, "sample_info": {}, "scene_url": scene_url}

                            # if len(search_key_list) > max_length:
                            #    return search_key_list[:max_length]

                            search_key_list.append(info)

    print("fetch max scene group length %d" % len(search_key_list))
    return search_key_list


# a = search_scene_list(["LivingDiningRoom"], ["Meeting"], ["sofa"], ['sofa/double seat sofa'], 2, True, 1)
# print(a)
# a = search_scene_list(["LivingDiningRoom"], ["Meeting"], ["sofa"], 2, True, 3222)
# print(a)


if __name__ == "__main__":
    random_seed = 15
    print(search_scene_list(['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Kitchen'],
                            ["Appliance"], ["appliance"], 10, seed=random_seed,
                            content_type_list=['appliance/refrigerator']))
