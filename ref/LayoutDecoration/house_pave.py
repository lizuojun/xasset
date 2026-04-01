import json
import copy
import numpy as np
from LayoutDecoration.house_info import HouseData
from LayoutDecoration.sample_room.sample_rooms import SampleRooms
from LayoutDecoration.house_recon import ReconHouse


def house_pave_pipeline(house_data, material_info, build_mode={}):
    debug_mode = build_mode['debug'] if 'debug' in build_mode else False
    # # 全屋组织
    house = HouseData(house_data, debug_mode=debug_mode)

    sample_rooms = SampleRooms()
    base_hard_type = sample_rooms.get_base_hard('modern')

    house_counts_dict = {}
    house_area_dict = {}
    house_price_dict = {}

    house_usage = {}
    house_info = house.house_info
    for room_id, room_info in house_info['rooms'].items():

        if room_id not in material_info:
            continue
        house_counts_dict[room_id] = dict()
        house_area_dict[room_id] = dict()
        house_price_dict[room_id] = dict()
        house_usage[room_id] = dict()
        if 'wall' in material_info[room_id]:
            wall_mesh_mat = material_info[room_id]['wall']
            for wall in room_info['Wall']:
                for s in wall['segments']:
                    s['material'] = {}
                    wall_mesh_mat['mesh'] = 'Wall'
                    s['material']['main'] = wall_mesh_mat
                    s['material']['seam'] = base_hard_type['TileGap']
                    s['material']['default'] = base_hard_type['Ceiling']['default']
            wall_mesh_list = ReconHouse.build_wall(room_info)
            wall_area = np.sum([i['area'] for i in wall_mesh_list if i['tiles'] == 0])
            wall_tiles_count = int(np.sum([i['tiles'] for i in wall_mesh_list if i['tiles'] > 0]))
            house_usage[room_id]['wall'] = {}
            if wall_tiles_count == 0:
                house_usage[room_id]['wall']['usage'] = wall_area
                house_usage[room_id]['wall']['unit'] = 'area'
            else:
                house_usage[room_id]['wall']['usage'] = wall_tiles_count
                house_usage[room_id]['wall']['unit'] = 'tile'
            house_usage[room_id]['wall']['price'] = wall_mesh_mat['price'] * house_usage[room_id]['wall']['usage']
            # house_counts_dict[room_id]['wall'] = wall_tiles_count
            # house_area_dict[room_id]['wall'] = wall_area
            # house_price_dict[room_id]['wall'] = wall_mesh_mat['price'] * (
            #     wall_tiles_count if wall_tiles_count > 0 else wall_area)
        if 'floor' in material_info[room_id]:
            floor_mesh_mat = material_info[room_id]['floor']
            for floor in room_info['Floor']:
                tile_gap_mat = base_hard_type['TileGap']
                floor_mesh_mat['mesh'] = 'Floor'
                tile_gap_mat['mesh'] = 'Seam'
                floor['material']['main'] = floor_mesh_mat
                floor['material']['seam'] = tile_gap_mat
                floor['material']['default'] = base_hard_type['Ceiling']['default']
            floor_mesh_list = ReconHouse.build_floor(room_info)
            floor_area = np.sum([i['area'] for i in floor_mesh_list if i['tiles'] == 0])
            floor_tiles_count = int(np.sum([i['tiles'] for i in floor_mesh_list if i['tiles'] > 0]))
            house_usage[room_id]['floor'] = {}
            if floor_tiles_count == 0:
                house_usage[room_id]['floor']['usage'] = floor_area
                house_usage[room_id]['floor']['unit'] = 'area'
            else:
                house_usage[room_id]['floor']['usage'] = floor_tiles_count
                house_usage[room_id]['floor']['unit'] = 'tile'
            house_usage[room_id]['floor']['price'] = floor_mesh_mat['price'] * house_usage[room_id]['floor']['usage']

            # house_counts_dict[room_id]['floor'] = floor_tiles_count
            # house_area_dict[room_id]['floor'] = floor_area
            # house_price_dict[room_id]['floor'] = floor_mesh_mat['price'] * (
            #     floor_tiles_count if floor_tiles_count > 0 else floor_area)

    return house_usage


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
