import json
import copy
from LayoutDecoration.house_info import HouseData
from LayoutDecoration.Base.recon_params import change_jr_to_recon_style
from LayoutDecoration.layout.room_area_segmentation import RoomAreaSegmentation
from LayoutDecoration.sample_room.sample_rooms import SampleRooms
from LayoutDecoration.libs.recon_hard_lib import HardLib
from LayoutDecoration.light.recon_light import LightConfig
from LayoutDecoration.kitchen.recon_kitchen import Kitchen


def house_recon_pipeline(house_data, layout_info, style, build_mode, sell_info=None):

    debug_mode = build_mode['debug'] if 'debug' in build_mode else False
    # # 全屋组织
    house = HouseData(house_data, debug_mode=debug_mode)

    #
    # layout准备
    house_layout = {}
    house_material = {}
    room_sample_mat_dict = {}
    # for room_uid in house.house_info['rooms'].keys():
    for room in house_data['room']:
        room_uid = room['id']
        if room_uid not in house.house_info['rooms']:
            continue
        if room_uid in layout_info:
            if len(layout_info[room_uid]['layout_scheme']) > 0:
                house_layout[room_uid] = layout_info[room_uid]['layout_scheme'][0]['group']
                if 'material' in layout_info[room_uid]['layout_scheme'][0]:
                    house_material[room_uid] = copy.deepcopy(layout_info[room_uid]['layout_scheme'][0]['material'])
                    room_sample_mat_dict[room_uid] = house_material[room_uid]['type'] if 'type' in house_material[room_uid] else 'LivingDiningRoom'

                for group in layout_info[room_uid]['layout_scheme'][0]['group']:
                    for obj in group['obj_list']:
                        if obj['id'].endswith('.json'):
                            house.house_info['rooms'][room_uid]['ParametricModel'].append(obj)
        if 'customized_info' in room:
            for customized_info in room['customized_info']:
                if 'obj_info' in customized_info:
                    house.house_info['rooms'][room_uid]['ParametricModel'] += customized_info['obj_info']

    # 硬装功能区分割
    RoomAreaSegmentation(house.house_info, house_layout, build_mode=build_mode)

    # 硬装离线库
    # style = 'Chinese'
    style = change_jr_to_recon_style(style)
    hard_lib = HardLib(room_sample_mat_dict=room_sample_mat_dict)

    # 硬装样板
    # import os
    # # import numpy as np
    # transfer_dir = '/Users/liqing.zhc/code/ihome-layout/HouseSearch/temp/house_data/'
    # # # 随机
    # # # names = os.listdir(transfer_dir)
    # # # transfer_path = os.path.join(transfer_dir, np.random.choice(names))
    # # # 指定
    # transfer_path = os.path.join(transfer_dir, '0a4a4b5f-bd96-45de-b60c-87d738231efe.json')
    # #
    # sample_house_data = json.load(open(transfer_path, 'r'))
    # house_material = {}
    # for room_data in sample_house_data['room']:
    #     house_material[room_data['id']] = room_data['material_info']

    white_list = build_mode['white_list'] if 'white_list' in build_mode else False
    # for room_id, room_mat in house_material.items():
    #     if 'living' in room_mat['type'].lower():
    #         house_material[room_id]['self_transfer'] = True
    sample_rooms = SampleRooms(hard_lib=hard_lib, white_list=white_list)
    base_hard_type = sample_rooms.get_base_hard(style)
    has_self_transfer = False
    for room_id, room_mat in house_material.items():
        if 'self_transfer' in room_mat and room_mat['self_transfer']:
            has_self_transfer = True
            break
    house_material_tmp = house_material.copy()

    if has_self_transfer:
        for room_id, room_mat in house_material_tmp.items():
            if 'self_transfer' not in room_mat or not room_mat['self_transfer']:
                house_material.pop(room_id)

    base_hard_type, hard_for_room = sample_rooms.get_transfer_hard(base_hard_type, house_material)
    # base_hard_type = sample_rooms.get_similar_hard(style)
    #
    # # 硬装配置
    hard_lib.config_hard_type(house.house_info, base_hard_type, hard_for_room, house_layout, sell_info, build_mode)

    # 厨房
    if 'kitchen' not in build_mode or build_mode['kitchen']:
        for room_id, room_info in house.house_info['rooms'].items():
            if room_info['type'] == 'Kitchen':
                if len(room_info['floor_pts']) >= 3:
                    k = Kitchen(room_info, house.house_info['id'], debug_mode)
                    k.config_kitchen(room_info, base_hard_type)
    # 灯光
    if 'light' not in build_mode or build_mode['light']:
        LightConfig(house.house_info, house_layout, debug_mode=debug_mode)
    #
    # 写入house_data
    house_data['global_light_params'] = house.house_info['global_light_params']
    for room in house_data['room']:
        room_id = room['id']
        if room_id in house.house_info['rooms']:
            room['light_info'] = house.house_info['rooms'][room_id]['Light']
            room['construct_info'] = house.house_info['rooms'][room_id]
            room['construct_info'].pop('Light')
    for room_uid, layout in house_layout.items():
        layout_info[room_uid]['layout_scheme'][0]['group'] = house_layout[room_uid]
    #
    # # ReconHouse(house_data)
    # # # 输出scene json格式
    # # scene = SceneJson(house_data, layout_info)

    return house_data


def main():
    input_json = json.load(open('/Users/liqing.zhc/code/HardDecorate/LayoutDecoration/test.json', 'r'))
    # 组装house_data 兼容room_data 构建mesh
    if 'house_data' not in input_json:
        if 'room_data' not in input_json:
            # return {}, {}
            house_data = {}
            exit(0)
        else:
            house_data = {'id': '', 'room': [input_json['room_data']]}
    else:
        house_data = input_json['house_data']
    # 风格提取
    if 'style' in input_json:
        jr_style = input_json['style']
    else:
        jr_style = ''

    # 组装全屋软装 兼容单屋
    if 'house_layout' in input_json:
        house_layout = input_json['house_layout']
    else:
        if 'room_layout' in input_json and input_json['room_layout']:
            house_layout = {input_json['room_layout']['type'] + '-0': input_json['room_layout']}
        else:
            house_layout = ''

    # 商品信息
    sell_info = {}
    if 'sell_info' in input_json:
        sell_info = input_json['sell_info']

    house, scene = house_recon_pipeline(house_data, house_layout, jr_style, {}, sell_info)
    scene_data = scene.write_scene_json()
    json.dump(scene_data, open('./scene.json', 'w'))
    house.get_scene_info()


if __name__ == '__main__':
    main()
