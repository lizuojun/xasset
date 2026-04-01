import json
import re

from Extract.extract_cache import cal_sample_vector, get_house_data, get_house_sample
from House.house_service import get_scene_json_daily
from ImportHouse.room_search_more import extract_sample_house
from Demo.test_local import get_design_json_daily
from House.house_sample import extract_room_layout_by_info
from HouseSearch.generate_sample_scores import get_group_vector


def get_style_base(style):
    if style in ["简约", "现代"]:
        return "Modern"
    elif style == "轻奢":
        return "Luxury"
    elif style == "日式":
        return "Japanese"
    elif style == "北欧":
        return "Nordic"
    elif style == "美式":
        return "Country"
    elif style == "欧式":
        return "European"
    elif style in ["新中式", "中式"]:
        return "Chinese"
    else:
        return ""


base_ld = json.load(open("living_dict.json", "r"))
out_list = []

all_lines = open("./temp/new_all_add", 'r').readlines()
for line in all_lines:
    if line[-1] == '\n':
        line = line[:-1]

    _, style, _, _, design_key, *_ = line.split('\t')

    match = re.match(r'(.*)assetId=(.*)', design_key)
    design_id = match.groups(1)[1]
    if not match:
        continue
    style_match = get_style_base(style)
    if len(style_match) == 0:
        print(line)
        continue

    scene_url = get_scene_json_daily(design_id)
    print(design_id, scene_url)
    # continue
    if len(scene_url) == 0:
        continue

    try:
        sample_para, sample_data, sample_layout, sample_group = extract_sample_house(design_id, reload=True)
    except:
        print("error!")
        continue
    try:

        for room_data in sample_data['room']:
            if not room_data:
                continue

            if room_data["type"] not in ["LivingRoom", "LivingDiningRoom"]:
                continue

            room_id = room_data['id']

            room_layout_info, room_group_info = extract_room_layout_by_info(room_data)
            group_vector_info, group_code = get_group_vector(room_group_info['group_functional'])
            vector = cal_sample_vector(room_group_info['group_functional'], room_group_info['room_type'])

            item = {
                "source_id": "",
                "style_type": style_match,
                "key": design_id + "_" + room_id,
                "vector": vector,
                "roles_vec": group_vector_info
            }

            out_list.append(item)
    except:
        continue

out_dict = json.load(open("living_dict.json"))
out_dict["pub"] = out_list
with open("living_dict.json", "w") as f:
    f.write(json.dumps(out_dict))