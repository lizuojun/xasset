# -*- coding: utf-8 -*-
import math

from Furniture.furniture import get_furniture_data, get_furniture_data_more, get_furniture_data_refer_id, \
    get_furniture_size_by_jid
from Furniture.materials import get_material_data, MATERIAL_DATA_CATE_DICT, get_ceramic_reference, save_material_data, save_ceramic_reference_data
from Furniture.furniture_refer import get_furniture_category_by_role
from House.house_sample import compute_room_seed
from HouseSearch.main_seed import get_room_main_furniture_seeds
from HouseSearch.seed.seed_roles import refine_seeds_note
from HouseSearch.seed.soft_service import multi_furniture_seeds_service_processing


# 请求软装搭配生成 北原tpp接口
def get_furniture_seeds_service_room_data(house_data, sample_info, furniture_seeds_info):
    room_main_furniture = get_room_main_furniture_seeds(furniture_seeds_info)
    house_room_key_input_info = {}

    check_furniture_jid_seeds = {}
    for source_room_data in house_data['room']:
        source_room_id = source_room_data['id']
        room_type = source_room_data['type']
        if source_room_id not in furniture_seeds_info:
            continue

        if source_room_id not in room_main_furniture:
            continue

        if source_room_id not in sample_info['sample']:
            continue

        room_attr = {
            'isCurrent': 'true',
            'modelIds': [room_main_furniture[source_room_id]['id']],
            'roomId': '1',
            'roomType': source_room_data['type'],
            'area': source_room_data['area'],
            'styleIds': room_main_furniture[source_room_id]['style_id']
        }

        object_list = []
        used_jid = []
        for group in sample_info['sample'][source_room_id]['layout_scheme'][0]['group']:
            for object_one in group['obj_list']:
                if object_one['role'] not in ['sofa', 'table', 'side table', 'cabinet', 'side table', 'chair', 'bed', 'armoire']:
                    continue

                if object_one['role'] == 'sofa' and room_main_furniture[source_room_id]['role'] == "sofa":
                    check_furniture_jid_seeds[object_one['id']] = room_main_furniture[source_room_id]['id']

                if object_one['role'] == 'bed' and room_main_furniture[source_room_id]['role'] == "bed":
                    check_furniture_jid_seeds[object_one['id']] = room_main_furniture[source_room_id]['id']

                if object_one['id'] in used_jid:
                    continue

                size = [object_one['size'][i]*object_one['scale'][i]/100. for i in range(3)]
                group_type = group['type']
                object_role = object_one['role']
                object_type = object_one['type']
                object_id = object_one['id']

                object_rely, object_cate = '', ''
                if 'relate' in group:
                    object_rely = group['relate']

                if object_role in ['tv', 'electronics', 'screen', 'accessory', 'plants', '']:
                    continue
                else:
                    cate_set_1, cate_set_2, cate_id_1, cate_id_2 = \
                        get_furniture_category_by_role(group_type, object_role, object_type, object_rely, room_type)
                    if len(cate_id_2) >= 1:
                        cate_new = cate_id_2[0]
                    elif len(cate_id_1) >= 1:
                        cate_new = cate_id_1[0]
                    else:
                        type_id, style_id, category_id = get_furniture_data_refer_id(object_id)
                        cate_new = category_id

                object_new = {
                    'model_id': object_one['id'],
                    'xMin': round(size[0]*0.8, 1),
                    'zMin': round(size[1]*0.5, 1),
                    'yMin': round(size[2]*0.8, 1),
                    'xMax': round(size[0]*1.2, 1),
                    'zMax': round(size[1]*1.5, 1),
                    'yMax': round(size[2]*1.2, 1),
                    'xPerfect': round(size[0], 1),
                    'zPerfect': round(size[1], 1),
                    'yPerfect': round(size[2], 1),
                    'cateLayout': object_type,
                    'cate_id': cate_new
                }

                object_list.append(object_new)
                used_jid.append(object_one['id'])

        request_limit = 7
        request_count = math.ceil((len(object_list) - 1) / request_limit)
        propose_list = []
        for request_index in range(request_count):
            object_once = [object_list[0]]
            for i in range(request_limit):
                object_idx = 1 + request_index * request_limit + i
                if object_idx >= len(object_list):
                    break
                object_once.append(object_list[object_idx])
            if len(object_once) > 0:
                propose_once = {
                    'isAIDesign': 'true',
                    'input_model_id': room_main_furniture[source_room_id]['id'],
                    'roomsAttribute': [],
                    'needSizeRuleAbsolutely': 'true',
                    'SlotRuleAIDesgin': object_once
                }
                propose_once['roomsAttribute'].append(room_attr)
                propose_list.append(propose_once)

            house_room_key_input_info[source_room_id] = propose_list

    if not house_room_key_input_info:
        return {}

    # 同步更新
    response_dict = multi_furniture_seeds_service_processing(house_room_key_input_info)
    # print(house_room_key_input_info)
    for room_key in response_dict:
        for jid in response_dict[room_key]:
            if jid in check_furniture_jid_seeds:
                response_dict[room_key][jid] = check_furniture_jid_seeds[jid]

    return response_dict


# 物品尺寸纠正
def parse_object_size(object_one):
    object_key = object_one['id']
    fixed_size = get_furniture_size_by_jid(object_key)
    if len(fixed_size) >= 3:
        origin_size, origin_scale = object_one['size'], object_one['scale']
        if abs(origin_scale[0] - 1) < 0.01 and abs(origin_scale[2] - 1) < 0.01:
            if abs(origin_size[0] - fixed_size[0]) > 0.1 and abs(origin_size[2] - fixed_size[2]) > 0.1:
                origin_scale = [abs(fixed_size[i] / origin_size[i]) for i in range(3)]
                object_one['scale'] = origin_scale

def extract_input_seeds_info(seeds_info=None, seeds_note={}, house_data={}):
    room_data_info = {}
    for room in house_data["room"]:
        room_data_info[room["id"]] = {"area":room["area"], "type":room["type"]}

    furniture_seeds_info, material_seeds_info = {}, {}
    if not seeds_info:
        return furniture_seeds_info, {}, material_seeds_info

    for room_id in seeds_info:
        room_mat_seeds_info = {}
        room_fur_seeds_list = []

        # 检查三种主材
        if 'wall' in seeds_info[room_id] and len(seeds_info[room_id]['wall']) > 0:
            room_mat_seeds_info['wall'] = seeds_info[room_id]['wall']
        if 'ceiling' in seeds_info[room_id] and len(seeds_info[room_id]['ceiling']) > 0:
            room_mat_seeds_info['ceiling'] = seeds_info[room_id]['ceiling']
        if 'floor' in seeds_info[room_id] and len(seeds_info[room_id]['floor']) > 0:
            room_mat_seeds_info['floor'] = seeds_info[room_id]['floor']

        # 检查软装
        if 'soft' in seeds_info[room_id] and len(seeds_info[room_id]['soft']) > 0:
            room_fur_seeds_list = seeds_info[room_id]['soft']

        if room_mat_seeds_info:
            material_seeds_info[room_id] = room_mat_seeds_info
        if room_fur_seeds_list:
            furniture_seeds_info[room_id] = room_fur_seeds_list

    replace_note = {}

    for room_id in furniture_seeds_info:
        if room_id in room_data_info:
            room_type = room_data_info[room_id]["type"]
            room_area = room_data_info[room_id]["area"]
        else:
            room_area = 15.
            try:
                room_type = room_id.split('-')[0]
            except:
                room_type = ''
        soft_list = furniture_seeds_info[room_id]
        furniture_list = []
        if len(soft_list) > 0:
            for jid in soft_list:
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
                furniture_list.append(object_new)

            seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, [], room_type, room_area=room_area)
            for seed_one in seed_list + keep_list + plus_list:
                seed_key = seed_one['id']
                if seed_one['id'] in seeds_note:
                    if "group" in seeds_note[seed_key] and 'role' in seeds_note[seed_key]:
                        seed_one['group'], seed_one['role'] = seeds_note[seed_key]['group'], seeds_note[seed_key]['role']
                replace_note[seed_key] = seed_one
            # refine_seeds_note(replace_note, room_type)

    return furniture_seeds_info, replace_note, material_seeds_info


def update_room_layout_material_seed(material_info, seed_info, seed_note={}):
    # seed_mat = {}
    if 'wall' in seed_info and len(seed_info['wall']) > 0:
        jid = seed_info['wall'][0]
        seed_wall = get_material_data_info(jid)
        seed_wall['support_mobile_scene'] = True
        # seed_mat['wall'] = format_material(seed_wall)
        # seed_mat['wall']['support_mobile_scene'] = True
        if jid in seed_note:
            for k in seed_note[jid]:
                if k not in seed_wall:
                    seed_wall[k] = seed_note[jid][k]
        if seed_wall:
            material_info['wall'] = [seed_wall]
    if 'floor' in seed_info and len(seed_info['floor']) > 0:
        jid = seed_info['floor'][0]
        seed_floor = get_material_data_info(seed_info['floor'][0])
        seed_floor['support_mobile_scene'] = True
        # seed_mat['floor'] = format_material(seed_floor)
        # seed_mat['floor']['support_mobile_scene'] = True
        if jid in seed_note:
            for k in seed_note[jid]:
                if k not in seed_floor:
                    seed_floor[k] = seed_note[jid][k]
        if seed_floor:
            material_info['floor'] = [seed_floor]


def update_room_replace_material_seed(material_info, replace_info):
    replace_mat = {}
    for k in replace_info.keys():  # wall or floor
        if len(replace_info[k]) == 0:
            continue

        if k in ['wall', 'floor']:
            replace_mat[k] = {}
            if isinstance(replace_info[k], list):
                replace = [get_material_data_info(i) for i in replace_info[k]]
                material_info[k] = replace
                replace_mat[k] = {'all': [format_material(i) for i in replace]}
            elif isinstance(replace_info[k], dict):
                material_info[k] = []
                for org, tar in replace_info[k].items():
                    target = get_material_data_info(tar)
                    replace_mat[k][org] = format_material(target)
                    material_info[k].append(target)
        elif k in ['background']:
            replace_mat[k] = {}
            material_info[k] = []
            if isinstance(replace_info[k], list):
                for bg in replace_info[k]:
                    fur = get_furniture_data_info(bg['jid'])
                    fur['Functional'] = bg['Functional']
                    fur['accessory'] = bg['accessory'] if 'accessory' in bg else 0
                    material_info[k].append(fur)
                    if fur['Functional'] not in replace_mat[k]:
                        replace_mat[k][fur['Functional']] = []
                    replace_mat[k][fur['Functional']].append(fur)
            else:
                for org, tar in replace_info[k].items():
                    target = get_furniture_data_info(tar)
                    replace_mat[k][org] = target
                    material_info[k].append(target)
    return replace_mat


def get_material_data_info(jid):
    if len(jid) == 0:
        return {}
    textureUrl, color, obj_size, obj_type, obj_category_id, obj_style_en, rgb = get_material_data(jid)
    obj_type = obj_type.split('/')
    obj_size = [i / 100. for i in obj_size]
    refs = []
    if obj_category_id in MATERIAL_DATA_CATE_DICT['瓷砖'] + MATERIAL_DATA_CATE_DICT['石材']:# + MATERIAL_DATA_CATE_DICT['地板单板'] + MATERIAL_DATA_CATE_DICT['地板']:
        seam = True
        seam_width = 0.005
        refs = get_ceramic_reference(jid)
        refs = [(i, get_material_data(i)[0]) for i in refs]
    else:
        seam = False
        seam_width = 0.001
        if obj_category_id in MATERIAL_DATA_CATE_DICT['地板单板'] + MATERIAL_DATA_CATE_DICT['地板']:
            refs = get_ceramic_reference(jid)
            refs = [(i, get_material_data(i)[0]) for i in refs]
            if len(refs) > 0:
                seam = True

    return {
        'jid': jid,
        'texture_url': textureUrl,
        'color': color,
        'colorMode': 'texture' if len(textureUrl) > 0 else 'color',
        'size': obj_size,
        'seam': seam,
        'seam_width': seam_width,
        'area': 100.0, 'lift': 0,
        'contentType': obj_type,
        'refs': refs,
        'rgb': rgb
    }

import os
import json
from DataAccess.data_oss import oss_download_file

temp_dir = os.path.join(os.path.dirname(__file__), '../LayoutDecoration/temp/')
customized_feature_wall_tmp_folder = os.path.join(temp_dir, './customized_feature_wall/')
customized_data_bucket = 'ihome-alg-sample-data'
customized_data_oss_dir = 'customized_data/'
if not os.path.exists(customized_feature_wall_tmp_folder):
    os.makedirs(customized_feature_wall_tmp_folder)

def get_furniture_data_info(jid):
    if len(jid) == 0:
        return {}
    # mesh feature wall or customized ceiling
    if len(jid.split('_')) == 2 and jid.endswith('.json'):
        obj_path = jid.replace('.json', '_info.json')
        local_obj_path = os.path.join(customized_feature_wall_tmp_folder, obj_path)
        if not os.path.exists(local_obj_path):
            oss_download_file(customized_data_oss_dir + obj_path,
                              local_obj_path,
                              customized_data_bucket)

        if not os.path.exists(local_obj_path):
            print('Warning: house construct customized ceiling mesh obj lost')
            return {}
        obj_info = json.load(open(local_obj_path, 'r'))
        return obj_info
    obj_type, obj_style_en, obj_size = get_furniture_data(jid)
    obj_type = obj_type.split('/')

    return {
        'id': jid,
        'size': obj_size,
        'type': obj_type,
        'scale': [1, 1, 1]
    }


def format_material(mat):
    content_type = ''
    if 'contentType' in mat:
        content_type = mat['contentType']
    elif isinstance(mat['seam'], list):
        content_type = mat['seam']
    if mat['seam'] is True:
        tree = ['tiles', 'ceramic wall']
    else:
        tree = ['tiles', 'transfer']
    formated_mat = {
        'code': 1,
        "texture": mat['texture_url'],
        "jid": mat['jid'],
        "uv_ratio": [1. / mat['size'][0], 0, 1. / mat['size'][1], 0],
        "color": mat['color'] + [255],
        "colorMode": mat['colorMode'],
        'type': tree,
        "contentType": content_type,
        "Functional": mat['Functional'] if "Functional" in mat else "",
        "refs": [] if 'refs' not in mat else mat['refs']
    }
    return formated_mat


# 软装方案替换
def build_replace_sample_info(layout_info, replace_info):
    from Furniture.furniture_group_replace import pre_group_rect_adjust
    for source_room_id in replace_info:
        now_room_need_replace_info = replace_info[source_room_id]
        for idx, group in enumerate(layout_info['sample'][source_room_id]['layout_scheme'][0]['group']):
            group_replace_list = []
            for object_one in group['obj_list']:
                if object_one['role'] not in ['sofa', 'table', 'side table', 'cabinet', 'side table', 'chair', 'bed',
                                              'armoire']:
                    continue
                if object_one['id'] not in now_room_need_replace_info:
                    continue

                if now_room_need_replace_info[object_one['id']] not in group_replace_list:
                    group_replace_list.append(now_room_need_replace_info[object_one['id']])

            # 前置替换
            if len(group_replace_list) > 0:
                layout_info['sample'][source_room_id]['layout_scheme'][0]['group'][idx] = pre_group_rect_adjust(group)


if __name__ == '__main__':
    obj_type, obj_style_en, obj_size = get_furniture_data("5618072d-00a8-4681-9cb4-cbc011f2f63c")
    furniture_list = [{'id': '5618072d-00a8-4681-9cb4-cbc011f2f63c', 'type': 'sofa/double seat sofa', 'style': 'Light Luxury', 'size': [186.167, 136.421, 175.785], 'scale': [0.499551477974077, 0.4984569824293914, 0.4437238672241659], 'position': [0, 0, 0], 'rotation': [0, 0, 0, 1]}]
    seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, [], room_area=56, room_type="LivingDiningRoom")
    print()