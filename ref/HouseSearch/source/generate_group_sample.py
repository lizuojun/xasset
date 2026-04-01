import json
import re

from Extract.extract_cache import cal_sample_vector, get_house_data, get_house_sample
from Furniture.materials import get_material_data
from House.house_service import get_scene_json_daily
from HouseSearch.util import get_http_data_from_url
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


def extract_material_feat(layout, feat, room_id):
    if 'mat_vector' not in feat:
        feat['mat_vector'] = {}
    for r_id, room_layout in layout.items():
        if r_id != room_id:
            continue
        mat = room_layout['layout_scheme'][0]['material']
        if 'floor' in mat:
            tem_floor = [i for i in mat['floor'] if i is not None]
            for i in tem_floor:
                if 'area' not in i:
                    i['area'] = 0.1
            tem_floor = sorted(tem_floor, key=lambda x: -x['area'])
            floor_rgbs = []
            for floor in tem_floor:
                if 'Functional' not in floor or floor['Functional'] == 'Main':
                    floor_rgbs.append(get_material_data(floor['jid'])[-1])
            if len(floor_rgbs) >= 1:
                feat['mat_vector']['floor'] = floor_rgbs[0]
            else:
                feat['mat_vector']['floor'] = [255, 255, 255]
        if 'wall' in mat:
            tem_wall = [i for i in mat['wall'] if i is not None]
            for i in tem_wall:
                if 'area' not in i:
                    i['area'] = 0.1
            tem_wall = sorted(tem_wall, key=lambda x: -x['area'])
            wall_rgbs = []
            for wall in tem_wall:
                if 'Functional' not in wall or wall['Functional'] == 'Main':
                    wall_rgbs.append(get_material_data(wall['jid'])[-1])
            if len(wall_rgbs) >= 1:
                feat['mat_vector']['wall'] = wall_rgbs[0]
            else:
                feat['mat_vector']['wall'] = [255, 255, 255]
    return feat


def generate_sample_data_living_room(source_id, design_id, design_url, scene_url, spec_style):
    out_list = []
    sample_para, sample_data, sample_layout, sample_group = extract_sample_house(design_id, design_url, scene_url, reload=True)

    for room_data in sample_data['room']:
        if not room_data:
            continue

        if room_data["type"] not in ["LivingRoom", "LivingDiningRoom"]:
            continue

        room_id = room_data['id']

        try:
            room_layout_info, room_group_info = extract_room_layout_by_info(room_data)
            group_vector_info, group_code = get_group_vector(room_group_info['group_functional'])
            vector = cal_sample_vector(room_group_info['group_functional'], room_group_info['room_type'])

            item = {
                "source_id": source_id,
                "style_type": spec_style,
                "key": design_id + "_" + room_id,
                "vector": vector,
                "roles_vec": group_vector_info
            }
            extract_material_feat(sample_layout, item, room_id)
            out_list.append(item)
        except:
            continue

    return out_list


if __name__ == '__main__':
    import time
    # group_sample_data_roles 为本地方案数据信息
    old_sample_data = json.load(open("../group_sample_data_roles.json", "r"))

    # 方案designId来源 base 代表宫霞做200+的样板间 也是客餐厅样板间来源
    source_data = json.load(open("source.json", "r"))["base_small"]

    old_base_data = json.load(open("living_dict.json", "r"))["base"]
    for house_source_id, design_id, target_style in source_data:
        # scene_url获取是异步的 速度比较慢 可能出现后面使用url时还没有生成好的情况
        scene_url = get_scene_json_daily(design_id)
        while not get_http_data_from_url(scene_url):
            time.sleep(2)

        design_url = get_design_json_daily(design_id)

        old_base_data += generate_sample_data_living_room("", design_id, design_url, scene_url, spec_style=target_style)

    old_sample_data["base"] = {"LivingDiningRoom": old_base_data}

    with open("../new_group_sample_data_roles.json", "w") as f:
        f.write(json.dumps(old_sample_data))