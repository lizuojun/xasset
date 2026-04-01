# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-07
@Description: 提取功能区布局数据，包括功能区的包围盒、内部布局、外部布局等信息，作为样本数据，同时提供布局绘制功能

"""

from House.house_save import *
from House.house_scene import *
from Furniture.furniture_group_layout import *

# 临时数据目录
DATA_DIR_HOUSE = os.path.dirname(__file__) + '/temp/'
DATA_DIR_HOUSE_EMPTY = os.path.dirname(__file__) + '/temp/empty/'
DATA_DIR_HOUSE_INPUT = os.path.dirname(__file__) + '/temp/input/'
DATA_DIR_HOUSE_SAMPLE = os.path.dirname(__file__) + '/temp/sample/'
DATA_DIR_HOUSE_SCHEME = os.path.dirname(__file__) + '/temp/scheme/'
if not os.path.exists(DATA_DIR_HOUSE):
    os.makedirs(DATA_DIR_HOUSE)
if not os.path.exists(DATA_DIR_HOUSE_EMPTY):
    os.makedirs(DATA_DIR_HOUSE_EMPTY)
if not os.path.exists(DATA_DIR_HOUSE_INPUT):
    os.makedirs(DATA_DIR_HOUSE_INPUT)
if not os.path.exists(DATA_DIR_HOUSE_SAMPLE):
    os.makedirs(DATA_DIR_HOUSE_SAMPLE)
if not os.path.exists(DATA_DIR_HOUSE_SCHEME):
    os.makedirs(DATA_DIR_HOUSE_SCHEME)

# OSS数据位置
DATA_OSS_HOUSE = 'ihome-alg-sample-room'
DATA_OSS_HOUSE_FINE = 'ihome-alg-sample-room-fine'
DATA_OSS_HOUSE_EMPTY = 'ihome-alg-sample-room-empty'

# 单屋方案
HOUSE_SAMPLE_DICT = {}
HOUSE_SAMPLE_TUNE = {}

# 梯度面积
ROOM_AREA_MAIN = [0, 10, 12, 15, 20, 30, 40, 50, 100]
ROOM_AREA_OTHER = [0, 6, 10, 14, 20, 30, 100]
# 房间面积
ROOM_AREA_LIVINGROOM = 20
ROOM_AREA_BEDROOM = 10
ROOM_AREA_BALCONY = 7.5
ROOM_AREA_BATHROOM = 5
ROOM_AREA_STORAGE = 2.5
# 房间类型
ROOM_TYPE_LEVEL_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library']
ROOM_TYPE_LEVEL_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
ROOM_TYPE_LEVEL_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom', 'Kitchen',
                     'Balcony', 'Terrace', 'Lounge', 'Auditorium',
                     'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                     'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom']
# 家具纠正
FURNITURE_TYPE_FIX = ['200 - on the floor', '300 - on top of others', '400 - attach to wall', '500 - attach to ceiling']
# 部件高度
UNIT_HEIGHT_WALL = 2.6
UNIT_HEIGHT_CEIL = 0.15
UNIT_HEIGHT_ARMOIRE_MIN = 1.5


# 数据下载：列举数据
def list_house_dir(src_dir):
    house_list = []
    if not os.path.exists(src_dir):
        return house_list
    for house_file in os.listdir(src_dir):
        if not house_file.endswith('.json'):
            continue
        house_id = house_file[:-5]
        house_list.append(house_id)
    return house_list


# 数据下载：列举数据
def list_house_oss(src_oss, index=0, number=10000):
    house_list, file_list = [], []
    try:
        file_list = oss_list_file(src_oss, object_ext='.json', object_idx=index, object_cnt=number)
    except Exception as e:
        print(e)
        if src_oss == DATA_OSS_HOUSE_FINE:
            return list_house_dir(DATA_DIR_HOUSE_SAMPLE)
    for house_file in file_list:
        if not house_file.endswith('.json'):
            continue
        hosue_id = house_file[:-5]
        house_list.append(hosue_id)
    return house_list


# 数据下载：样板间
def download_house(house_id, des_dir, house_ext='.json', reload=False):
    house_file = house_id + house_ext
    house_path = os.path.join(des_dir, house_file)
    if os.path.exists(house_path) and not reload:
        return house_path
    try:
        # OSS下载
        if oss_exist_file(house_file, DATA_OSS_HOUSE_FINE):
            oss_download_file(house_file, house_path, DATA_OSS_HOUSE_FINE)
        elif oss_exist_file(house_file, DATA_OSS_HOUSE):
            oss_download_file(house_file, house_path, DATA_OSS_HOUSE)
        # 居然下载
        else:
            # 下载数据
            download_scene_by_id(house_id, des_dir)
            # 上传数据
            if os.path.exists(house_path):
                oss_upload_file(house_file, house_path, DATA_OSS_HOUSE)
    except Exception as e:
        print(e)
    return house_path


# 数据解析：加载布局数据
def load_house_sample(reload=False):
    global HOUSE_SAMPLE_DICT
    if len(HOUSE_SAMPLE_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'house_sample_dict.json')
        HOUSE_SAMPLE_DICT = {}
        if os.path.exists(json_path):
            try:
                HOUSE_SAMPLE_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return HOUSE_SAMPLE_DICT


# 数据解析：保存布局数据
def save_house_sample():
    global HOUSE_SAMPLE_DICT
    json_path = os.path.join(os.path.dirname(__file__), 'house_sample_dict.json')
    with open(json_path, 'w') as f:
        json.dump(HOUSE_SAMPLE_DICT, f, indent=4)
        f.close()
    print('save room layout success')


# 数据解析：清空布局数据
def clear_house_sample():
    global HOUSE_SAMPLE_DICT
    HOUSE_SAMPLE_DICT.clear()
    print('clear house sample success')
    save_house_sample()


# 数据解析：增加布局数据
def add_sample_layout(room_type, room_area, layout_info, layout_mode=''):
    global HOUSE_SAMPLE_DICT
    load_house_sample()
    room_area = str(int(room_area))
    if room_type not in HOUSE_SAMPLE_DICT:
        HOUSE_SAMPLE_DICT[room_type] = {}
    if room_area not in HOUSE_SAMPLE_DICT[room_type]:
        HOUSE_SAMPLE_DICT[room_type][room_area] = []
    room_code_put = 'append'
    room_code_new = int(layout_info['code'] / 100) * 100
    for layout_idx, layout_one in enumerate(HOUSE_SAMPLE_DICT[room_type][room_area]):
        if layout_one['source_house'] == layout_info['source_house']:
            room_code_put = 'replace'
            break
        room_code_one = int(layout_one['code'] / 100) * 100
        if room_code_new > room_code_one:
            room_code_put = 'insert'
            break
    if layout_mode in ['insert']:
        room_code_put = layout_mode
    # 新增方案
    layout_add = layout_info.copy()
    if 'scene' in layout_info:
        layout_add['scene'] = {}
    group_list = []
    for group_one in layout_info['group']:
        if group_one['type'] in GROUP_RULE_FUNCTIONAL:
            group_add = group_one.copy()
            group_add['obj_list'] = []
            group_list.append(group_add)
    layout_add['group'] = group_list
    # 新增操作
    if room_code_put == 'insert':
        HOUSE_SAMPLE_DICT[room_type][room_area].insert(layout_idx, layout_add)
    elif room_code_put == 'replace':
        HOUSE_SAMPLE_DICT[room_type][room_area][layout_idx] = layout_add
    elif room_code_put == 'append':
        HOUSE_SAMPLE_DICT[room_type][room_area].append(layout_add)
    return layout_add


# 数据解析：增加布局数据
def del_sample_layout(source_house, source_room):
    global HOUSE_SAMPLE_DICT
    load_house_sample()
    for room_type, area_dict in HOUSE_SAMPLE_DICT.items():
        for room_area, layout_list in area_dict.items():
            for layout_idx in range(len(layout_list) - 1, -1, -1):
                layout_one = layout_list[layout_idx]
                if layout_one['source_house'] == source_house:
                    if layout_one['source_room'] == source_room or source_room == '':
                        layout_list.pop(layout_idx)


# 数据检索
def get_sample_layout(room_type, room_area):
    room_layout_list = []
    global HOUSE_SAMPLE_DICT
    load_house_sample()
    room_area = str(int(room_area))
    if room_type not in HOUSE_SAMPLE_DICT:
        return room_layout_list
    if room_area not in HOUSE_SAMPLE_DICT[room_type]:
        return room_layout_list
    return HOUSE_SAMPLE_DICT[room_type][room_area]


# 数据解析：全屋布局
def extract_house_layout(house_id, auto_add=0, check_mode=1, print_flag=False):
    # 布局信息
    house_data_info, house_layout_info, house_group_info = {}, {}, {}
    house_id = os.path.basename(house_id)
    if house_id.endswith('.json'):
        house_id = house_id[:-5]

    # 加载数据
    temp_dir = DATA_DIR_HOUSE_SAMPLE
    if not os.path.exists(temp_dir):
        temp_dir = os.path.dirname(__file__) + '/temp/'
    download_house(house_id, temp_dir)
    house_path = os.path.join(temp_dir, house_id + '.json')
    if not os.path.exists(house_path):
        return house_data_info, house_layout_info, house_group_info
    # 解析数据
    house_json = json.load(open(house_path, 'r', encoding='utf-8'))
    house_data_info, house_layout_info, house_group_info = extract_house_layout_by_scene(house_json, house_id, auto_add,
                                                                                         check_mode, print_flag)
    # 返回信息
    return house_data_info, house_layout_info, house_group_info


# 数据解析：全屋布局
def extract_house_layout_by_url(house_url, auto_add=0, check_mode=1, print_flag=False):
    house_dir = DATA_DIR_HOUSE_INPUT
    pass


# 数据解析：全屋布局
def extract_house_layout_by_path(house_path, auto_add=0, check_mode=1, print_flag=False):
    # 布局信息
    house_data_info, house_layout_info, house_group_info = {}, {}, {}
    if not os.path.exists(house_path):
        return house_data_info, house_layout_info, house_group_info

    # 解析数据
    house_json = json.load(open(house_path, 'r', encoding='utf-8'))
    house_id = ''
    if house_id == '' and 'uid' in house_json:
        house_id = house_json['uid']
    house_data_info, house_layout_info, house_group_info = extract_house_layout_by_scene(house_json, house_id, auto_add,
                                                                                         check_mode, print_flag)
    # 返回信息
    return house_data_info, house_layout_info, house_group_info


# 数据解析：全屋布局
def extract_house_layout_by_scene(house_json, house_id='', auto_add=0, check_mode=1, print_flag=False):
    try:
        if house_id == '' and 'uid' in house_json:
            house_id = house_json['uid']
    except Exception as e:
        print('get house layout by json error.')
        print(e)

    # 解析数据
    house_data = HouseData()
    house_data.load_json(house_json)
    room_list = []
    if 'room' in house_data.house_info:
        room_list = house_data.house_info['room']
    house_data_info = {'id': house_id, 'room': room_list}
    if 'scene' in house_data.house_info:
        house_data_info['scene'] = house_data.house_info['scene']

    # 解析数据 家具信息
    furniture_dict, material_dict, mesh_dict = {}, {}, {}
    for furniture_one in house_json['furniture']:
        furniture_uid, furniture_jid = furniture_one['uid'], furniture_one['jid']
        furniture_dict[furniture_uid] = furniture_jid
    # 解析数据 纹理信息
    for material_one in house_json['material']:
        material_uid, material_jid, texture_path = material_one['uid'], material_one['jid'], material_one['texture']
        material_dict[material_uid] = {
            'material_jid': material_jid,
            'texture_path': texture_path
        }
        pass
    # 解析数据 面片信息
    for mesh_one in house_json['mesh']:
        mesh_uid, mesh_type, material_uid = '', '', ''
        if 'uid' in mesh_one:
            mesh_uid = mesh_one['uid']
        if 'type' in mesh_one:
            mesh_type = mesh_one['type']
        if 'material' in mesh_one:
            material_uid = mesh_one['material']
        if mesh_type in MESH_TYPE_MAIN and material_uid in material_dict:
            material_jid, texture_path = material_dict[material_uid]['material_jid'], \
                                         material_dict[material_uid]['texture_path']
            mesh_dict[mesh_uid] = {
                'type': mesh_type,
                'material_uid': material_uid,
                'material_jid': material_jid,
                'texture_path': texture_path
            }

    # 解析数据 房间信息
    room_have = []
    for room_json in house_json['scene']['room']:
        room_type = room_json['type']
        room_id = room_json['instanceid']
        if room_type not in ROOM_TYPE_LIST:
            for type_one in ROOM_TYPE_LIST:
                if room_id.startswith(type_one):
                    room_type = type_one
                    room_json['type'] = type_one
                    break
        room_have.append(room_type)

    # 纠正房间
    correct_house_data(house_data_info)

    # 解析全屋
    house_data_info, house_layout_info, house_group_info = extract_house_layout_by_info(house_data_info, check_mode)

    # 添加全屋
    replace_house_layout(house_layout_info, house_group_info, house_id, auto_add)

    # 返回信息
    return house_data_info, house_layout_info, house_group_info


# 数据添加
def replace_house_layout(house_layout, house_group, house_id='', auto_add=1):
    house_layout_info, house_group_info = house_layout, house_group
    # 添加全屋
    for room_key, room_layout_info in house_layout_info.items():
        if auto_add <= 0:
            break
        room_type, room_area, room_group_info = 'none', 0, {}
        if 'room_type' in room_layout_info:
            room_type = room_layout_info['room_type']
        if 'room_area' in room_layout_info:
            room_area = room_layout_info['room_area']
        if room_key in house_group_info:
            room_group_info = house_group_info[room_key]

        # 解析数据 添加处理 检查房间面积决定是否添加
        room_area_int = int(room_area)
        room_area_min = int(room_area_int * 0.8)
        room_area_max = int(room_area_int * 1.2)
        room_area_has = False
        if auto_add >= 2:
            room_type_same = [room_type]
            # 特殊情况 卧室扩充为主卧、次卧、卧室
            if room_type == 'MasterBedroom':
                room_type_same = ['MasterBedroom', 'Bedroom']
            elif room_type == 'SecondBedroom':
                room_type_same = ['SecondBedroom', 'Bedroom']
            elif room_type == 'Bedroom':
                room_type_same = ['MasterBedroom', 'SecondBedroom', 'Bedroom']
            # 特殊情况 儿童房扩充为儿童房、老人房、保姆房
            elif room_type == 'KidsRoom' or room_type == 'ElderlyRoom' or room_type == 'NannyRoom':
                room_type_same = ['KidsRoom', 'ElderlyRoom', 'NannyRoom']
            # 检查房间面积
            for room_type_one in room_type_same:
                for room_size_one in range(room_area_min, room_area_max + 1):
                    layout_have = get_sample_layout(room_type_one, room_size_one)
                    if len(layout_have) > 0:
                        room_area_has = True
                        break
                if room_area_has:
                    break
            # 检查区域面积
            if not room_area_has:
                # 添加布局
                for layout_one in room_layout_info['layout_scheme']:
                    add_sample_layout(room_type, room_area_int, layout_one)
                    room_area_has = True
                # 添加分组
                if room_area_has:
                    for group_one in room_group_info['group_functional']:
                        add_furniture_group(house_id, room_key, group_one)
                    for group_one in room_group_info['group_decorative']:
                        add_furniture_group(house_id, room_key, group_one)
        elif auto_add > 0:
            # 添加布局
            for layout_one in room_layout_info['layout_scheme']:
                if len(room_group_info['group_functional']) <= 0:
                    if room_type in ROOM_TYPE_LEVEL_1 or room_type in ROOM_TYPE_LEVEL_2:
                        continue
                add_sample_layout(room_type, room_area_int, layout_one)
            # 添加分组
            for group_one in room_group_info['group_functional']:
                add_furniture_group(house_id, room_key, group_one)
            for group_one in room_group_info['group_decorative']:
                add_furniture_group(house_id, room_key, group_one)


# 数据解析：单屋布局
def extract_room_layout_by_scene(room_json, furniture_dict, mesh_dict, room_type='', room_area=10, door_pt_entry=[],
                                 check_mode=1, print_flag=False):
    # 布局信息
    room_layout_info = {
        'room_type': '',
        'room_style': '',
        'room_area': 0,
        'room_height': UNIT_HEIGHT_WALL,
        'layout_scheme': []
    }
    room_scheme_info = {
        'code': 0,
        'score': 0,
        'type': 0,
        'style': '',
        'area': 0,
        'material': {},
        'decorate': {},
        'group': [],
        'group_area': 0,
        'source_house': '',
        'source_room': '',
        'source_room_area': 0
    }
    room_group_info = {
        'room_type': '',
        'room_style': '',
        'room_area': 0,
        'room_height': UNIT_HEIGHT_WALL,
        'group_functional': [],
        'group_decorative': []
    }

    # 解析数据 房间类型
    if room_type == '':
        room_type = room_json['type']
    room_mirror = 0
    # 解析数据 家具信息
    furniture_list, decorate_list, mesh_list, mesh_have = [], [], [], {}
    for child_one in room_json['children']:
        child_ref = child_one['ref']
        if child_ref in furniture_dict or child_ref in mesh_dict:
            pass
        else:
            continue
        if child_ref in furniture_dict:
            # 家具信息
            furniture_info = {}
            furniture_id = furniture_dict[child_ref]
            furniture_info['id'] = furniture_id
            furniture_type, furniture_style, furniture_size = get_furniture_data(furniture_id)
            if furniture_type == '':
                continue
            furniture_info['type'] = furniture_type
            furniture_info['style'] = furniture_style
            furniture_info['size'] = furniture_size
            furniture_info['scale'] = child_one['scale']
            # 家具位置
            furniture_info['position'] = child_one['pos']
            furniture_info['rotation'] = child_one['rot']
            # 家具关联
            furniture_info['group'] = ''
            furniture_info['role'] = ''
            furniture_info['count'] = 1
            furniture_info['relate'] = ''
            # 数据记录
            furniture_list.append(furniture_info)
        elif child_ref in mesh_dict:
            # 面片信息
            mesh_one = mesh_dict[child_ref]
            mesh_type, material_uid, material_jid, texture_path = mesh_one['type'], mesh_one['material_uid'], \
                                                                  mesh_one['material_jid'], mesh_one['texture_path']
            if material_uid not in mesh_have:
                mesh_info = {
                    'type': mesh_type,
                    'uid': material_uid,
                    'jid': material_jid,
                    'texture': texture_path,
                    'count': 1
                }
                # 数据记录
                mesh_have[material_uid] = mesh_info
                mesh_list.append(mesh_info)
            else:
                mesh_have[material_uid]['count'] += 1
    # 解析数据 提取打组
    group_functional, group_decorative = extract_furniture_group(furniture_list, decorate_list,
                                                                 room_type, room_mirror, check_mode, print_flag)
    # 解析数据 纹理信息
    for group_one in group_decorative:
        group_type = group_one['type']
        for mesh_one in mesh_list:
            mesh_type = mesh_one['type']
            if group_type not in mesh_type:
                continue
            group_one['mat_list'].append(mesh_one)

    # 解析数据 整理打组
    style_main, count_list, group_area = '', [0, 0, 0], 0
    for group_one in group_functional:
        # 矩形信息
        group_type, group_size = group_one['type'], group_one['size'][:]
        group_position, group_rotation = group_one['position'][:], group_one['rotation'][:]
        group_angle = rot_to_ang(group_rotation)
        # 分组信息
        group_add = {
            'type': group_one['type'],
            'code': group_one['code'],
            'size': group_size,
            'offset': group_one['offset'][:],
            'position': group_position,
            'rotation': group_rotation,
            'size_min': group_one['size_min'][:],
            'size_rest': group_one['size_rest'][:],
            'obj_main': group_one['obj_main'],
            'obj_type': group_one['obj_type'],
            'obj_list': [],
            'relate': '',
            'relate_role': '',
            'relate_position': []
        }
        for obj_one in group_add['obj_list']:
            if 'origin_position' in obj_one and len(obj_one['origin_position']) > 0:
                obj_one['position'] = obj_one['origin_position'][:]
            if 'origin_rotation' in obj_one and len(obj_one['origin_rotation']) > 0:
                obj_one['rotation'] = obj_one['origin_rotation'][:]
        room_scheme_info['group'].append(group_add)
        group_area += group_size[0] * group_size[2]
        # 风格信息
        if style_main == '':
            style_main = group_one['style']
        elif group_one['type'] == 'Meeting' or group_one['type'] == 'Bed':
            style_main = group_one['style']
        # 数量信息
        count_list[0] += 1
        accessory_count = int(group_one['code']) % 10
        furniture_count = len(group_one['obj_list']) - accessory_count
        count_list[1] += furniture_count
        count_list[2] += accessory_count
    # 解析数据 更新打组
    room_code = count_list[0] * 10000 + count_list[1] * 100 + count_list[2]
    room_style = style_main
    room_scheme_info['code'] = room_code
    room_scheme_info['type'] = room_type
    room_scheme_info['style'] = room_style
    room_scheme_info['area'] = room_area
    room_scheme_info['group_area'] = group_area
    if room_area < group_area:
        room_scheme_info['area'] = group_area * 1.5
    # 解析数据 更新打组
    room_group_info['room_type'] = room_type
    room_group_info['room_style'] = room_style
    room_group_info['room_area'] = room_area
    room_group_info['group_functional'] = group_functional
    room_group_info['group_decorative'] = group_decorative

    # 返回信息
    if len(room_scheme_info['group']) > 0:
        room_scheme_info['score'] = 80
        room_layout_info['layout_scheme'].append(room_scheme_info)
    return room_layout_info, room_group_info


# 数据解析：全屋布局
def extract_house_layout_by_design(design_id, check_mode=1, reload_flag=False, print_flag=False):
    # 布局信息
    house_data_info, house_layout_info, house_group_info = {}, {}, {}
    if design_id == '':
        return house_data_info, house_layout_info, house_group_info
    house_data_info = house_design_trans(design_id, reload_flag)
    if 'room' in house_data_info and len(house_data_info['room']) > 0:
        pass
    else:
        house_id_new, house_data_info, house_feature_info = get_house_data_feature(design_id, True)
    correct_house_type(house_data_info)
    house_data_info, house_layout_info, house_group_info = extract_house_layout_by_info(house_data_info, check_mode)
    return house_data_info, house_layout_info, house_group_info


# 数据解析：单屋布局
def extract_room_layout_by_design(design_id, room_id, check_mode=1, print_flag=False):
    # 布局信息
    room_data_info, room_layout_info, room_group_info = {}, {}, {}
    if design_id == '':
        return room_data_info, room_layout_info, room_group_info
    house_data_info = house_design_trans(design_id)
    if 'room' in house_data_info and len(house_data_info['room']) > 0:
        pass
    else:
        house_id_new, house_data_info, house_feature_info = get_house_data_feature(design_id, True)
    if 'room' in house_data_info and len(house_data_info['room']) > 0:
        for room_one in house_data_info['room']:
            if 'id' in room_one and room_one['id'] == room_id:
                room_data_info = room_one
                break
    if len(room_data_info) > 0:
        room_layout_info, room_group_info = extract_room_layout_by_info(room_data_info, check_mode)
    return room_data_info, room_layout_info, room_group_info


# 数据解析：全屋布局
def extract_house_layout_by_info(house_info, check_mode=1):
    # 布局信息
    house_data_info, house_layout_info, house_group_info = house_info, {}, {}

    # 解析数据 房间信息
    house_id = ''
    if 'id' in house_info:
        house_id = house_info['id']
    room_list = []
    if 'room' in house_data_info:
        room_list = house_data_info['room']
    # 解析数据 布局信息
    room_used = {}
    for room_idx, room_one in enumerate(room_list):
        # 解析数据 房间信息
        room_id, room_type, room_style, room_area = '', '', '', 0
        if 'id' in room_one:
            room_id = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        if room_id == '' or room_id in room_used:
            if room_type == '':
                room_type = 'none'
            room_id = room_type + '_%02d' % room_idx
            if room_id in room_used:
                room_id = room_type + '_%03d' % room_idx
            room_one['id'] = room_id
        if room_id == '':
            continue
        room_used[room_id] = 1
        # 解析数据 布局信息
        room_layout_info, room_group_info = extract_room_layout_by_info(room_one, check_mode, house_id)
        if 'type' in room_one:
            room_type = room_one['type']
        if 'style' in room_one:
            room_style = room_one['style']
        if 'area' in room_one:
            room_area = room_one['area']

        room_height = UNIT_HEIGHT_WALL
        if 'height' in room_one:
            room_height = room_one['height']
        if len(room_layout_info['layout_scheme']) <= 0:
            continue
        layout_scheme_one = room_layout_info['layout_scheme'][0]
        if room_area <= layout_scheme_one['area']:
            room_area = layout_scheme_one['area']
        if len(room_style) <= 0 and 'style' in layout_scheme_one:
            room_style = layout_scheme_one['style']
        room_layout_info['room_type'] = room_type
        room_layout_info['room_style'] = room_style
        room_layout_info['room_area'] = room_area
        room_layout_info['room_height'] = room_height
        house_layout_info[room_id] = room_layout_info
        # 解析数据 更新打组
        room_group_info['room_type'] = room_type
        room_group_info['room_style'] = room_style
        room_group_info['room_area'] = room_area
        room_group_info['room_height'] = room_height
        house_group_info[room_id] = room_group_info
    return house_data_info, house_layout_info, house_group_info


# 数据解析：单屋布局
def extract_room_layout_by_info(room_info, check_mode=1, house_id=''):
    room_id = ''
    if 'id' in room_info:
        room_id = room_info['id']
    # 纠正信息
    correct_room_data(room_info)

    # 纠正类型
    room_type, room_area = '', 10
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    furniture_list, decorate_list, material_info, painting_info = [], [], {}, {}
    if 'furniture_info' in room_info:
        furniture_list = room_info['furniture_info']
    if 'decorate_info' in room_info:
        decorate_list = room_info['decorate_info']
    else:
        room_info['decorate_info'] = []
    if 'material_info' in room_info:
        material_info = room_info['material_info']
    if 'hard_deco_info' in room_info:
        painting_info = room_info['hard_deco_info']

    # 纠正类型
    seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list, room_type, room_area)
    correct_room_type(room_info, seed_list, keep_list)
    # 纠正连通
    correct_room_link(room_info)

    # 房间信息
    room_type, room_style, room_height = '', '', UNIT_HEIGHT_WALL
    if 'type' in room_info:
        room_type = room_info['type']
    if 'style' in room_info:
        room_style = room_info['style']
    if 'height' in room_info:
        room_height = room_info['height']
    # 房门信息
    door_list = []
    if 'door_info' in room_info and len(room_info['door_info']) > 0:
        for unit_one in room_info['door_info']:
            door_list.append(unit_one)
    if 'hole_info' in room_info and len(room_info['hole_info']) > 0:
        for unit_one in room_info['hole_info']:
            door_list.append(unit_one)
    door_entry, door_pt_entry = {}, []
    door_bath_list, door_pt_bath_list = [], []
    for unit_one in door_list:
        door_to_id = unit_one['to']
        if door_to_id == '':
            door_entry = unit_one
        elif 'Hallway' in door_to_id and len(door_entry) <= 0:
            door_entry = unit_one
        elif 'Bathroom' in door_to_id:
            door_bath_list.append(unit_one)
    if 'pts' in door_entry:
        unit_pts = door_entry['pts']
        if len(unit_pts) >= 8:
            door_pt = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                       (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
            door_pt_entry = door_pt
        elif len(unit_pts) >= 2:
            door_pt = [unit_pts[0], unit_pts[1]]
            door_pt_entry = door_pt
    for unit_one in door_bath_list:
        unit_pts = unit_one['pts']
        if len(unit_pts) >= 8:
            door_pt = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                       (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
            door_pt_bath_list.append(door_pt)
        elif len(unit_pts) >= 2:
            door_pt = [unit_pts[0], unit_pts[1]]
            door_pt_bath_list.append(door_pt)

    # 窗户信息
    window_list = []
    if 'window_info' in room_info and len(room_info['window_info']) > 0:
        for unit_one in room_info['window_info']:
            window_list.append(unit_one)
    if 'baywindow_info' in room_info and len(room_info['baywindow_info']) > 0:
        for unit_one in room_info['baywindow_info']:
            window_list.append(unit_one)
    window_pt_list = []
    for unit_one in window_list:
        if 'pts' in unit_one:
            unit_pts = unit_one['pts']
            if len(unit_pts) >= 8:
                unit_pt_one = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                               (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                window_pt_list.append(unit_pt_one)
            elif len(unit_pts) >= 2:
                unit_pt_one = [unit_pts[0], unit_pts[1]]
                window_pt_list.append(unit_pt_one)

    # 布局信息
    room_data_info = room_info
    room_layout_info = {
        'room_type': '',
        'room_style': '',
        'room_area': 0,
        'room_height': UNIT_HEIGHT_WALL,
        'layout_scheme': [],
        'layout_mesh': []
    }
    room_group_info = {
        'room_type': '',
        'room_style': '',
        'room_area': 0,
        'room_height': UNIT_HEIGHT_WALL,
        'group_functional': [],
        'group_decorative': []
    }

    # 解析数据 房间信息
    room_one = room_info
    room_type, room_area, room_mirror = '', 20, 0
    if 'type' in room_one:
        room_type = room_one['type']
    if 'area' in room_one:
        room_area = room_one['area']
    if 'mirror' in room_one:
        room_mirror = room_one['mirror']

    # 解析数据 打组信息
    decorate_keep = []
    if 'furniture_info' in room_one:
        # 解析数据 软装信息
        for object_idx, object_one in enumerate(furniture_list):
            object_id, origin_size, origin_scale = object_one['id'], object_one['size'][:], object_one['scale'][:]
            origin_type, origin_style = '', ''
            if 'type' in object_one:
                origin_type = object_one['type']
            if 'style' in object_one:
                origin_style = object_one['style']
            refine_type, refine_style, refine_size = '', '', []
            if origin_type.startswith('customizedproducts'):
                refine_type, refine_style, refine_size = origin_type, origin_style, origin_size[:]
            elif have_furniture_data(object_id):
                refine_type, refine_style, refine_size = get_furniture_data(object_id)
            # 更新信息
            object_type, object_style = '', ''
            if 'type' in object_one:
                object_type = object_one['type']
            if 'style' in object_one:
                object_style = object_one['style']
            if 'bay window' in origin_type and len(origin_size) >= 3 and abs(origin_size[0]) > 0.01:
                pass
            elif 'parametric corner window' in origin_type and len(origin_size) >= 3 and abs(origin_size[0]) > 0.01:
                pass
            elif refine_type in FURNITURE_TYPE_FIX and origin_type not in FURNITURE_TYPE_FIX and len(origin_type) > 0:
                object_type, object_style, origin_size = origin_type, refine_style, refine_size
            elif not refine_type == '' and len(refine_size) >= 3 and abs(refine_size[0]) > 0.01:
                object_type, object_style, origin_size = refine_type, refine_style, refine_size
            # 旋转信息
            object_turn, object_turn_fix = get_furniture_turn(object_id), 0
            if abs(object_turn) >= 1:
                object_one['turn'] = object_turn
            elif 'turn' in object_one and abs(object_one['turn']) > 0:
                object_turn = object_one['turn']
            if 'turn_fix' in object_one:
                object_turn_fix = object_one['turn_fix']
            if object_turn in [-1, 1] and object_turn_fix <= 0:
                # 尺寸纠正
                x, y, z = origin_size[0], origin_size[1], origin_size[2]
                origin_size[0], origin_size[1], origin_size[2] = z, y, x
                x, y, z = origin_scale[0], origin_scale[1], origin_scale[2]
                origin_scale[0], origin_scale[1], origin_scale[2] = z, y, x
                object_one['size'] = origin_size[:]
                object_one['scale'] = origin_scale[:]
                # 角度纠正
                origin_angle = rot_to_ang(object_one['rotation'])
                object_angle = ang_to_ang(origin_angle - object_turn * math.pi / 2)
                object_one['rotation'] = [0, math.sin(object_angle / 2), 0, math.cos(object_angle / 2)]
                object_one['turn_fix'] = 1
            elif object_turn in [-2, 2] and object_turn_fix <= 0:
                # 角度纠正
                origin_angle = rot_to_ang(object_one['rotation'])
                object_angle = ang_to_ang(origin_angle - object_turn * math.pi / 2)
                object_one['rotation'] = [0, math.sin(object_angle / 2), 0, math.cos(object_angle / 2)]
                object_one['turn_fix'] = 1
            object_one['type'] = object_type
            object_one['style'] = object_style
            if object_turn_fix <= 0:
                object_one['size'] = origin_size[:]
                object_one['scale'] = origin_scale[:]
            object_one['group'] = ''
            object_one['role'] = ''
            object_one['count'] = 1
            if 'relate' not in object_one:
                object_one['relate'] = ''
            # 纠正模型
            correct_object_type(object_one, object_type, room_type)
            # 纠正吊顶
            if object_type in GROUP_MESH_DICT['ceiling']:
                object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
                if object_size[0] > 0.5 or object_size[2] > 0.5:
                    object_set = []
                    if 'customized_ceiling' in material_info:
                        object_set = material_info['customized_ceiling']
                    object_add = copy_object(object_one)
                    object_set.append(object_add)
                    material_info['customized_ceiling'] = object_set
            # 纠正背景墙
            if object_type in GROUP_MESH_DICT['background']:
                object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
                if object_size[0] > 0.5 or object_size[1] > 0.5:
                    object_set = []
                    if 'background' in material_info:
                        object_set = material_info['background']
                    object_add = copy_object(object_one)
                    object_set.append(object_add)
                    material_info['background'] = object_set
        # 解析数据 硬装信息
        for object_idx, object_one in enumerate(decorate_list):
            object_id, origin_size, origin_scale = object_one['id'], object_one['size'][:], object_one['scale'][:]
            object_turn, object_turn_fix = get_furniture_turn(object_id), 0
            if abs(object_turn) >= 1:
                object_one['turn'] = object_turn
            elif 'turn' in object_one and abs(object_one['turn']) > 0:
                object_turn = object_one['turn']
            if 'turn_fix' in object_one:
                object_turn_fix = object_one['turn_fix']
            if object_turn in [-1, 1] and object_turn_fix <= 0:
                x, y, z = origin_size[0], origin_size[1], origin_size[2]
                origin_size[0], origin_size[1], origin_size[2] = z, y, x
                x, y, z = origin_scale[0], origin_scale[1], origin_scale[2]
                origin_scale[0], origin_scale[1], origin_scale[2] = z, y, x
                object_one['size'] = origin_size[:]
                object_one['scale'] = origin_scale[:]
                # 角度纠正
                origin_angle = rot_to_ang(object_one['rotation'])
                object_angle = ang_to_ang(origin_angle - object_turn * math.pi / 2)
                object_one['rotation'] = [0, math.sin(object_angle / 2), 0, math.cos(object_angle / 2)]
                object_one['turn_fix'] = 1
            elif object_turn in [-2, 2] and object_turn_fix <= 0:
                # 角度纠正
                origin_angle = rot_to_ang(object_one['rotation'])
                object_angle = ang_to_ang(origin_angle - object_turn * math.pi / 2)
                object_one['rotation'] = [0, math.sin(object_angle / 2), 0, math.cos(object_angle / 2)]
                object_one['turn_fix'] = 1
            object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
            object_type = object_one['type']
            # 柜体
            if object_type in GROUP_MESH_DICT['cabinet']:
                object_bottom = object_one['position'][1]
                if object_size[0] > 3.0 and object_size[2] > 3.0:
                    continue
                if object_size[0] > 10 or object_size[1] > 10 or object_size[2] > 10:
                    continue
                if object_size[0] > 0.5 and object_size[1] > 0.5 and 0.01 < object_size[2] < 1.0:
                    if 'kitchen' not in object_one['type'] and 'build element' not in object_one['type']:
                        if -0.2 <= object_bottom <= 0.2:
                            object_one['style'] = ''
                            object_one['group'] = ''
                            object_one['role'] = ''
                            object_one['count'] = 1
                            object_one['relate'] = ''
                            furniture_list.append(object_one)
                            continue
                if object_size[0] > 0.5 or object_size[2] > 0.5:
                    decorate_keep.append(object_one)
                elif object_one['type'] in ['kitchen cabinet/base cabinet']:
                    decorate_keep.append(object_one)
            # 背景
            elif object_type in GROUP_MESH_DICT['background']:
                # if object_size[0] > 0.5 and object_size[2] > 1.0:
                #     continue
                if object_size[0] > 0.5 or object_size[1] > 0.5:
                    decorate_keep.append(object_one)
            # 吊顶
            elif object_type in GROUP_MESH_DICT['ceiling']:
                if object_size[0] > 0.5 or object_size[2] > 0.5:
                    decorate_keep.append(object_one)
            # 纠正吊顶
            if object_type in GROUP_MESH_DICT['ceiling']:
                if object_size[0] > 0.5 or object_size[2] > 0.5:
                    object_set = []
                    if 'customized_ceiling' in material_info:
                        object_set = material_info['customized_ceiling']
                    object_add = copy_object(object_one)
                    object_set.append(object_add)
                    material_info['customized_ceiling'] = object_set
            # 纠正背景墙
            if object_type in GROUP_MESH_DICT['background']:
                if object_size[0] > 0.5 or object_size[1] > 0.5:
                    object_set = []
                    if 'background' in material_info:
                        object_set = material_info['background']
                    object_add = copy_object(object_one)
                    object_set.append(object_add)
                    material_info['background'] = object_set
        # 解析数据 提取打组
        group_functional, group_decorative = extract_furniture_group(furniture_list, decorate_list,
                                                                     room_type, room_mirror, check_mode, False)
        # 解析数据 整理打组
        room_scheme_info = {
            'code': 0,
            'score': 0,
            'type': 0,
            'style': '',
            'area': 0,
            'material': material_info,
            'decorate': {},
            'painting': painting_info,
            'group': [],
            'group_area': 0,
            'source_house': '',
            'source_room': '',
            'source_room_area': 0
        }
        style_main, count_list, group_area, group_list = '', [0, 0, 0], 0, []
        for group_idx, group_one in enumerate(group_functional):
            # 矩形信息
            group_type, group_style, group_size = '', '', group_one['size'][:]
            if 'type' in group_one:
                group_type = group_one['type']
            if 'style' in group_one:
                group_style = group_one['style']
            group_position, group_rotation = group_one['position'][:], group_one['rotation'][:]
            group_angle = rot_to_ang(group_rotation)
            # 分组信息
            group_add = {
                'type': group_type,
                'style': group_style,
                'code': group_one['code'],
                'size': group_size,
                'offset': group_one['offset'][:],
                'position': group_position,
                'rotation': group_rotation,
                'size_min': group_one['size_min'][:],
                'size_rest': group_one['size_rest'][:],
                'obj_main': group_one['obj_main'],
                'obj_type': group_one['obj_type'],
                'obj_list': group_one['obj_list'],
                'relate': '',
                'relate_role': '',
                'relate_position': []
            }
            for obj_one in group_add['obj_list']:
                if 'origin_position' in obj_one and len(obj_one['origin_position']) > 0:
                    obj_one['position'] = obj_one['origin_position'][:]
                if 'origin_rotation' in obj_one and len(obj_one['origin_rotation']) > 0:
                    obj_one['rotation'] = obj_one['origin_rotation'][:]
            room_scheme_info['group'].append(group_add)
            group_area += group_size[0] * group_size[2]
            # 风格信息
            if style_main == '':
                style_main = group_one['style']
            elif group_one['type'] == 'Meeting' or group_one['type'] == 'Bed':
                style_main = group_one['style']
            # 数量信息
            count_list[0] += 1
            accessory_count = int(group_one['code']) % 10
            furniture_count = len(group_one['obj_list']) - accessory_count
            count_list[1] += furniture_count
            count_list[2] += accessory_count
        for group_idx, group_one in enumerate(group_decorative):
            # 分组信息
            group_add = {
                'type': group_one['type'],
                'style': '',
                'size': [0, 0, 0],
                'offset': [0, 0, 0],
                'position': [0, 0, 0],
                'rotation': [0, 0, 0, 1],
                'obj_main': '',
                'obj_list': group_one['obj_list'],
                'mat_list': group_one['mat_list'],
            }
            room_scheme_info['group'].append(group_add)
        # 解析数据 更新打组
        room_code = count_list[0] * 10000 + count_list[1] * 100 + count_list[2]
        room_style = style_main
        room_scheme_info['code'] = room_code
        room_scheme_info['type'] = room_type
        room_scheme_info['style'] = room_style
        room_scheme_info['area'] = room_area
        room_scheme_info['group_area'] = group_area
        if room_area < group_area:
            room_scheme_info['area'] = group_area * 1.5
        source_house, source_room = 'sample_house', 'sample_room'
        if not house_id == '':
            source_house = house_id
        if 'id' in room_one and not room_one['id'] == '':
            source_room = room_one['id']
        room_scheme_info['source_house'] = source_house
        room_scheme_info['source_room'] = source_room
        room_scheme_info['source_room_area'] = room_area
        # 解析数据 更新打组
        room_group_info['room_type'] = room_type
        room_group_info['room_style'] = room_style
        room_group_info['room_area'] = room_area
        room_group_info['room_height'] = room_height
        room_group_info['group_functional'] = group_functional
        room_group_info['group_decorative'] = group_decorative
        for group_one in group_functional:
            add_furniture_group(source_house, source_room, group_one)
        for group_one in group_decorative:
            add_furniture_group(source_house, source_room, group_one)

    # 返回信息
    if len(room_scheme_info['group']) > 0:
        room_scheme_info['score'] = 80
        room_layout_info['layout_scheme'].append(room_scheme_info)
        correct_room_zone(room_info, room_layout_info)
    room_layout_info['layout_mesh'] = decorate_keep
    return room_layout_info, room_group_info


# 数据解析：全屋纠正
def correct_house_data(house_info):
    if 'room' not in house_info:
        return
    # 纠正数据
    room_list = []
    if 'room' in house_info:
        room_list = house_info['room']
    for room_idx, room_one in enumerate(room_list):
        correct_room_data(room_one)
    # 纠正类型
    correct_house_type(house_info)
    # 纠正连通
    correct_house_link(house_info)

    # 纠正镜像
    room_mirror = 0
    for room_idx, room_one in enumerate(room_list):
        if 'mirror' in room_one:
            room_mirror = room_one['mirror']
            if room_mirror > 0:
                break
    if room_mirror > 0:
        house_info['mirror'] = 1
        mid_wall_pts = []
        if 'mid_wall' in house_info and 'wall_pts' in house_info['mid_wall']:
            mid_wall_pts = house_info['mid_wall']['wall_pts']
        for point_one in mid_wall_pts:
            if len(point_one) >= 2:
                point_one[1] *= -1


# 数据解析：纠正点列
def correct_house_point(house_info):
    if 'room' not in house_info:
        return
    room_list = house_info['room']
    # 纠正点列
    for room_info in room_list:
        if 'coordinate' not in room_info:
            room_info['coordinate'] = 'xyz'
        if 'unit' not in room_info:
            room_info['unit'] = 'm'
        correct_room_point(room_info)


# 数据解析：纠正类型
def correct_house_type(house_info):
    room_list = house_info['room']
    # 纠正房间
    live_list, food_list, rest_list = [], [], []  # 客厅 餐厅 卧室
    cook_list, bath_list, open_list, hall_list = [], [], [], []  # 厨房 卫浴 阳台 门厅
    none_list = []  # 其他
    todo_list_2, todo_list_3 = [], []
    # 遍历房间
    max_room, max_area = {}, 0
    for room_idx, room_one in enumerate(room_list):
        # 纠正类型
        room_id, room_type, room_area = '', '', 10
        if 'id' in room_one:
            room_id = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        if 'area' in room_one:
            room_area = room_one['area']
        if room_area >= max_area:
            max_room, max_area = room_one, room_area
        furniture_list, decorate_list = [], []
        if 'furniture_info' in room_one:
            furniture_list = room_one['furniture_info']
        if 'decorate_info' in room_one:
            decorate_list = room_one['decorate_info']
        seed_list, keep_list, plus_list, mesh_list = [], [], [], []
        if len(furniture_list) > 0:
            if room_type not in ROOM_TYPE_MAIN:
                seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list,
                                                                               room_type, room_area)
                correct_room_type(room_one, seed_list, keep_list)
            elif room_type in ROOM_TYPE_LEVEL_3 and room_area > 20 and len(furniture_list) > 10:
                seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list,
                                                                               '', room_area)
                correct_room_type(room_one, seed_list, keep_list)
            elif room_area <= 5 or room_area >= 30:
                seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list, '', room_area)
                correct_room_type(room_one, seed_list, keep_list)
        # 记录全屋
        room_type_old = room_type
        room_type_new = room_one['type']
        if 'Living' in room_type_new and room_area > 5:
            live_list.append(room_one)
        elif 'Dining' in room_type_new and room_area > 5:
            food_list.append(room_one)
        elif 'Kitchen' in room_type_new:
            cook_list.append(room_one)
        elif 'Bathroom' in room_type_new:
            bath_list.append(room_one)
        elif 'Bedroom' in room_type_new:
            if room_area > 5:
                rest_list.append(room_one)
            # 开放信息
            door_list, hole_list = room_one['door_info'], room_one['hole_info']
            open_flag = False
            for door_one in door_list:
                if 'to' in door_one and door_one['to'] == '':
                    open_flag = True
                    break
            for door_one in hole_list:
                if 'to' in door_one and door_one['to'] == '':
                    open_flag = True
                    break
            # 待定信息
            if room_type_old in ['', 'none', 'undefined', 'OtherRoom'] and not open_flag:
                find_idx = -1
                for rest_idx, rest_one in enumerate(todo_list_2):
                    if 'area' in rest_one and rest_one['area'] < room_area:
                        find_idx = rest_idx
                        break
                if 0 <= find_idx < len(todo_list_2):
                    todo_list_2.insert(find_idx, room_one)
                else:
                    todo_list_2.append(room_one)
            elif room_type_old in ['', 'none', 'undefined', 'OtherRoom'] and open_flag:
                find_idx = -1
                for rest_idx, rest_one in enumerate(todo_list_3):
                    if 'area' in rest_one and rest_one['area'] < room_area:
                        find_idx = rest_idx
                        break
                if 0 <= find_idx < len(todo_list_3):
                    todo_list_3.insert(find_idx, room_one)
                else:
                    todo_list_3.append(room_one)
        elif 'Hallway' in room_type_new:
            hall_list.append(room_one)
        elif room_type_new in ['', 'none', 'undefined', 'OtherRoom']:
            none_list.append(room_one)

    # 纠正客厅
    if len(live_list) <= 0:
        min_idx, max_idx, min_area, max_area = 0, 0, 100, 0
        ent_room = {}
        for room_idx, room_one in enumerate(room_list):
            room_type, room_area = '', 10
            if 'type' in room_one:
                room_type = room_one['type']
            if 'area' in room_one:
                room_area = room_one['area']
            if room_area < min_area:
                min_idx = room_idx
                min_area = room_area
            if room_area > max_area:
                max_idx = room_idx
                max_area = room_area
            if room_area > 20:
                # 开放信息
                open_flag = False
                for door_one in room_one['door_info']:
                    if 'to' in door_one and door_one['to'] == '':
                        open_flag = True
                        break
                if open_flag:
                    ent_room = room_one
        max_room, min_room = room_list[max_idx], room_list[min_idx]
        if len(room_list) <= 1 and len(none_list) <= 0:
            pass
        elif len(food_list) <= 0 and len(rest_list) == 1 and max_room == rest_list[0]:
            pass
        else:
            if max_area > 20:
                max_room['type'] = 'LivingDiningRoom'
                if len(food_list) >= 2 and max_room in food_list:
                    max_room['type'] = 'LivingRoom'
                elif len(food_list) >= 1 and max_room not in food_list:
                    max_room['type'] = 'LivingRoom'
                live_list.append(room_one)
                if max_room in food_list:
                    food_list.remove(max_room)
                if max_room in none_list:
                    none_list.remove(max_room)
            elif room_area > 15:
                max_room['type'] = 'LivingRoom'
                live_list.append(room_one)
                if max_room in none_list:
                    none_list.remove(max_room)
            elif room_area > 10:
                max_room['type'] = 'DiningRoom'
                live_list.append(room_one)
                if max_room in none_list:
                    none_list.remove(max_room)
            if len(ent_room) > 0:
                if ent_room['type'] in ['LivingDiningRoom', 'LivingRoom']:
                    pass
                else:
                    ent_room['type'] = 'LivingRoom'
                    live_list.append(room_one)
                    if ent_room in none_list:
                        none_list.remove(ent_room)
    if len(live_list) >= 2:
        min_idx, max_idx, min_area, max_area = 0, 0, 100, 0
        for room_idx, room_one in enumerate(live_list):
            room_area = 0
            if 'area' in room_one:
                room_area = room_one['area']
            if room_area < min_area:
                min_idx = room_idx
                min_area = room_area
            if room_area > max_area:
                max_idx = room_idx
                max_area = room_area
        if max_area > min_area + 5 and 0 <= max_idx < len(live_list) and 0 <= min_idx < len(live_list):
            max_room, min_room = live_list[max_idx], live_list[min_idx]
            max_type, min_type = '', ''
            max_wait, min_wait = '', ''
            if 'door_info' in min_room:
                for unit_one in min_room['door_info']:
                    if 'to' in unit_one and len(unit_one['to']) <= 0 and min_area < 10:
                        min_wait = 'Hallway'
                        break
                    elif 'to' in unit_one and 'Kitchen' in unit_one['to'] and len(min_wait) <= 0:
                        min_wait = 'DiningRoom'
            if 'type' in max_room:
                max_type = max_room['type']
            if 'type' in min_room:
                min_type = min_room['type']
            if 'Living' in max_type and 'Living' in min_type:
                if len(food_list) <= 0:
                    if min_area >= 15:
                        min_room['type'] = 'DiningRoom'
                        food_list.append(min_room)
                    elif min_area >= 10 and max_area < 20:
                        min_room['type'] = 'DiningRoom'
                        food_list.append(min_room)
                    else:
                        if 'area' in max_room and int(max_room['area']) >= 12:
                            max_room['type'] = 'LivingDiningRoom'
                        if len(min_wait) > 0:
                            min_room['type'] = min_wait
                        elif min_type in ['LivingRoom'] and min_area > 10:
                            pass
                        else:
                            min_room['type'] = 'OtherRoom'
                elif len(min_wait) > 0:
                    min_room['type'] = min_wait
                elif min_type in ['LivingRoom'] and min_area > 10:
                    pass
                elif min_area > 15:
                    min_room['type'] = 'Bedroom'
                else:
                    min_room['type'] = 'OtherRoom'
                live_list.pop(min_idx)
        elif max_area >= min_area >= 8 and len(food_list) <= 0:
            max_room, min_room = live_list[max_idx], live_list[min_idx]
            if max_room['type'] in ['LivingDiningRoom'] and min_room['type'] in ['LivingRoom'] and min_area > 10:
                min_room['type'] = 'LivingRoom'
                if max_area < 30:
                    max_room['type'] = 'DiningRoom'
                    live_list.remove(max_room)
                    food_list.append(max_room)
            else:
                min_room['type'] = 'DiningRoom'
                live_list.remove(min_room)
                food_list.append(min_room)
                if max_area < 30:
                    max_room['type'] = 'LivingRoom'
    # 纠正餐厅
    if len(live_list) >= 1 and len(food_list) <= 0 and len(none_list) >= 2:
        max_idx, max_door = 0, 0
        for room_idx, room_one in enumerate(none_list):
            room_area, room_door = 10, 0
            if room_one in live_list:
                continue
            if 'area' in room_one:
                room_area = room_one['area']
            if 'door_info' in room_one:
                room_door += len(room_one['door_info'])
            if 'hole_info' in room_one:
                room_door += len(room_one['hole_info'])
            if room_door > max_door and room_area > 10:
                max_idx = room_idx
                max_door = room_door
        max_room = none_list[max_idx]
        if max_door >= 3:
            max_room['type'] = 'DiningRoom'
            food_list.append(room_one)
            if max_room in none_list:
                none_list.remove(max_room)
    if len(live_list) >= 1 and len(food_list) >= 1:
        live_flag = 1
        for room_idx, room_one in enumerate(live_list):
            if 'area' not in room_one:
                continue
            if room_one['type'] in ['LivingDiningRoom']:
                live_flag = 1
                room_door = 0
                if 'door_info' in room_one:
                    room_door += len(room_one['door_info'])
                if 'hole_info' in room_one:
                    room_door += len(room_one['hole_info'])
                if room_one['area'] > 30:
                    live_flag = 3
                elif room_one['area'] > 20:
                    live_flag = 2
        for room_idx, room_one in enumerate(food_list):
            if live_flag < 2:
                break
            if 'area' not in room_one:
                continue
            if 'floor' not in room_one:
                continue
            room_area, wall_max = room_one['area'], 1
            # 原始轮廓 顶点
            floor_pts = room_one['floor']
            floor_len = int(len(floor_pts) / 2)
            # 原始轮廓 线段
            for i in range(floor_len - 1):
                # 起点终点
                x1, y1, x2, y2 = floor_pts[2 * i + 0], floor_pts[2 * i + 1], floor_pts[2 * i + 2], floor_pts[2 * i + 3]
                wall_new = abs(x2 - x1) + abs(y2 - y1)
                wall_max = max(wall_max, wall_new)
            if live_flag >= 2 and room_area < 10 and room_area / wall_max <= 1:
                room_one['type'] = 'OtherRoom'
            elif live_flag >= 3 and room_area <= 18 and room_area / wall_max <= 1.8:
                room_one['type'] = 'OtherRoom'
    # 纠正客厅
    if len(live_list) == 1:
        room_one = live_list[0]
        room_area = 0
        if 'area' in room_one:
            room_area = room_one['area']
        if len(food_list) <= 0 and room_area >= 10:
            if room_area <= 30 and len(room_list) == 1:
                pass
            elif room_area >= 25:
                room_one['type'] = 'LivingDiningRoom'
        elif room_area >= 40:
            room_one['type'] = 'LivingDiningRoom'
    # 纠正卧室
    if len(rest_list) <= 1:
        for room_idx, room_one in enumerate(none_list):
            room_area = 10
            if 'area' in room_one:
                room_area = room_one['area']
            room_type_old = room_one['type']
            # 开放信息
            open_flag = False
            for door_one in room_one['door_info']:
                if 'to' in door_one and door_one['to'] == '':
                    open_flag = True
                    break
            if room_area >= 15 and not open_flag:
                room_one['type'] = 'Bedroom'
                rest_list.append(room_one)
            elif room_area >= 12 and len(rest_list) <= 0 and not open_flag:
                room_one['type'] = 'Bedroom'
                rest_list.append(room_one)
            # 待定信息
            if room_type_old in ['', 'none', 'undefined', 'OtherRoom'] and not open_flag:
                find_idx = -1
                for rest_idx, rest_one in enumerate(todo_list_2):
                    if 'area' in rest_one and rest_one['area'] < room_area:
                        find_idx = rest_idx
                        break
                if 0 <= find_idx < len(todo_list_2):
                    todo_list_2.insert(find_idx, room_one)
                else:
                    todo_list_2.append(room_one)
            elif room_type_old in ['', 'none', 'undefined', 'OtherRoom'] and open_flag:
                find_idx = -1
                for rest_idx, rest_one in enumerate(todo_list_3):
                    if 'area' in rest_one and rest_one['area'] < room_area:
                        find_idx = rest_idx
                        break
                if 0 <= find_idx < len(todo_list_3):
                    todo_list_3.insert(find_idx, room_one)
                else:
                    todo_list_3.append(room_one)
    # 增加厨房
    if len(todo_list_2) >= 1 and len(cook_list) <= 0 and len(rest_list) >= 3:
        room_one = todo_list_2[-1]
        room_type, room_area, room_furniture = '', 10, []
        if 'type' in room_one:
            room_type = room_one['type']
        if 'area' in room_one:
            room_area = room_one['area']
        if 'furniture_info' in room_one:
            room_furniture = room_one['furniture_info']
        if room_area < 15 and len(room_furniture) <= 0:
            room_one['type'] = 'Kitchen'
            cook_list.append(room_one)
    # 增加阳台
    if len(todo_list_3) >= 1 and len(rest_list) >= 3:
        room_one = todo_list_3[-1]
        room_type, room_area, room_furniture = '', 10, []
        if 'type' in room_one:
            room_type = room_one['type']
        if 'area' in room_one:
            room_area = room_one['area']
        if 'furniture_info' in room_one:
            room_furniture = room_one['furniture_info']
        if room_area < 10 and len(room_furniture) <= 0:
            room_one['type'] = 'Balcony'
            open_list.append(room_one)

    # 兜底处理
    if len(room_list) == 1:
        room_one = room_list[0]
        room_type, room_area = '', 10
        if 'type' in room_one:
            room_type = room_one['type']
        if 'area' in room_one:
            room_area = room_one['area']
        if room_type not in ['', 'none', 'undefined', 'OtherRoom']:
            pass
        elif room_area > 14:
            room_one['type'] = 'LivingDiningRoom'
        elif room_area > 7:
            room_one['type'] = 'Bedroom'
        else:
            room_one['type'] = 'Bathroom'

    # 调整别名
    for room_one in room_list:
        # 纠正类型
        room_id, room_type, room_area = '', '', 10
        if 'id' in room_one:
            room_id = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        # 别名
        room_alias = room_id
        room_split = room_alias.split('-')
        if not room_split[0] == room_type:
            room_alias = room_type + '-' + room_split[-1]
        room_one['alias'] = room_alias


# 数据解析：纠正连通
def correct_house_link(house_info):
    if 'room' not in house_info:
        return
    room_list = house_info['room']
    # 纠正连通
    type_dict, link_dict = {}, {}
    for room_idx, room_one in enumerate(room_list):
        room_key, room_type = '', ''
        if 'id' in room_one:
            room_key = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        if len(room_key) > 0 and len(room_type) > 0:
            type_dict[room_key] = room_type
    for room_idx, room_one in enumerate(room_list):
        link_list = []
        unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow = [], [], [], []
        if 'door_info' in room_one:
            unit_list_door = room_one['door_info']
        if 'hole_info' in room_one:
            unit_list_hole = room_one['hole_info']
        if 'window_info' in room_one:
            unit_list_window = room_one['window_info']
        if 'baywindow_info' in room_one:
            unit_list_baywindow = room_one['baywindow_info']
        for unit_list_one in [unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow]:
            door_flag = False
            if unit_list_one == unit_list_door or unit_list_one == unit_list_hole:
                door_flag = True
            for unit_one in unit_list_one:
                unit_to, unit_to_type, unit_pos = '', '', []
                if 'to' in unit_one:
                    unit_to = unit_one['to']
                if len(unit_to) <= 0:
                    unit_to_type = ''
                elif unit_to in type_dict:
                    unit_to_type = type_dict[unit_to]
                    unit_one['link'] = unit_to_type
                else:
                    continue
                if door_flag:
                    link_list.append(unit_to_type)
        # 模型连通
        object_list = []
        if 'furniture_info' in room_one:
            object_list = room_one['furniture_info']
        for object_one in object_list:
            object_type = object_one['type']
            if object_type.startswith('door'):
                pass
            elif object_type.startswith('window'):
                pass
            else:
                continue
            object_pos = object_one['position']
            for unit_list_one in [unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow]:
                for unit_one in unit_list_one:
                    unit_pts, unit_pos = unit_one['pts'], []
                    if len(unit_pts) >= 8:
                        unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                                         (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                    elif len(unit_pts) >= 2:
                        unit_pos = [unit_pts[0], unit_pts[1]]
                    else:
                        continue
                    if abs(object_pos[0] - unit_pos[0]) + abs(object_pos[2] - unit_pos[1]) <= 0.1:
                        unit_to_room, unit_to_type = '', ''
                        if 'to' in unit_one:
                            unit_to_room = unit_one['to']
                        if 'link' in unit_one:
                            unit_to_type = unit_one['link']
                        if len(unit_to_type) <= 0 and len(unit_to_room) > 0:
                            unit_to_type = unit_to_room.split('-')[0]
                        object_one['unit_to_room'] = unit_to_room
                        object_one['unit_to_type'] = unit_to_type
                        break
        # 房间连通
        room_one['link'] = link_list
        link_dict[room_one['id']] = link_list
    for room_idx, room_one in enumerate(room_list):
        unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow = [], [], [], []
        if 'door_info' in room_one:
            unit_list_door = room_one['door_info']
        if 'hole_info' in room_one:
            unit_list_hole = room_one['hole_info']
        for unit_list_one in [unit_list_door, unit_list_hole]:
            for unit_one in unit_list_one:
                unit_to, unit_to_link = '', []
                if 'to' in unit_one:
                    unit_to = unit_one['to']
                if unit_to in link_dict:
                    unit_to_link = link_dict[unit_to]
                unit_one['to_link'] = unit_to_link


# 数据解析：纠正避让
def correct_house_move(house_layout, object_one, room_id=''):
    room_layout = {}
    if len(room_id) > 0:
        for room_key, room_val in house_layout.items():
            if room_id == room_key:
                room_layout = room_val
                break
    if len(room_layout) <= 0:
        for room_key, room_val in house_layout.items():
            if 'floor' not in room_val:
                continue
            line_ori = compute_room_line(room_val)
            edge_idx, line_idx, unit_rat = compute_furniture_rely(object_one, line_ori)
            if 0 <= line_idx < len(line_ori) and 0 <= edge_idx < 4:
                room_layout = room_val
                break
    if len(room_layout) > 0:
        correct_room_move(room_layout, object_one)


# 数据解析：纠正排序
def correct_house_sort(house_layout):
    room_sort_list, room_sort_dict = [], {}
    room_sort_code, room_sort_item = {}, []
    for room_key, room_val in house_layout.items():
        room_type, room_area = room_val['room_type'], room_val['room_area']
        room_code = room_area
        if room_type in ROOM_TYPE_LEVEL_1:
            room_code = room_area * 16
        elif room_type in ROOM_TYPE_LEVEL_2:
            room_code = room_area * 8
        elif room_type in ['Kitchen']:
            room_code = room_area * 4
        elif 'Bathroom' not in room_type:
            room_code = room_area * 2
        elif room_type in ROOM_TYPE_LEVEL_3:
            room_code = room_area * 1
        else:
            room_code = room_area * 1
        room_sort_code[room_key] = room_code
    room_sort_item = sorted(room_sort_code.items(), key=lambda kv: (kv[1], kv[0]))
    room_sort_type = {}
    for room_one in room_sort_item:
        room_key = room_one[0]
        room_sort_list.insert(0, room_key)
    for room_key in room_sort_list:
        if room_key in house_layout:
            room_val = house_layout[room_key]
            room_type = room_val['room_type']
            if room_type in room_sort_type:
                room_sort_type[room_type].append(room_key)
            else:
                room_sort_type[room_type] = [room_key]
    for room_type, room_list in room_sort_type.items():
        room_type_en, room_type_ch = room_type, room_type
        if room_type_en in ROOM_TYPE_NAME:
            room_type_ch = ROOM_TYPE_NAME[room_type_en]
        if room_type_ch == '':
            room_type_ch = '未知'
        # 编号
        for room_idx, room_key in enumerate(room_list):
            room_name = room_type_ch
            if len(room_list) > 1:
                room_name = room_type_ch + "%d" % (room_idx + 1)
            if room_key in house_layout:
                room_val = house_layout[room_key]
                room_val['room_name'] = room_name
            room_sort_dict[room_key] = room_name
    return room_sort_list, room_sort_dict


# 数据解析：纠正单屋
def correct_room_data(room_info):
    global HOUSE_SAMPLE_TUNE
    # 坐标信息
    if 'coordinate' not in room_info:
        room_info['coordinate'] = 'xyz'
    if 'unit' not in room_info:
        room_info['unit'] = 'm'
    # 纠正坐标
    correct_room_point(room_info)
    # 纠正连通
    correct_room_link(room_info)
    # 房间信息
    room_area = 0
    if 'area' in room_info:
        room_area = room_info['area']
    # 软装信息
    furniture_list, furniture_dump = [], []
    if 'furniture_info' in room_info:
        furniture_list = room_info['furniture_info']
    if 'decorate_info' not in room_info:
        room_info['decorate_info'] = []
    if 'material_info' not in room_info:
        room_info['material_info'] = {}
    for object_idx, object_one in enumerate(furniture_list):
        if ('size' in object_one and len(object_one['size']) < 3) or 'size' not in object_one:
            object_type, object_style, object_size = get_furniture_data(object_one['id'])
            object_one['size'] = object_size[:]
            object_one['scale'] = [1, 1, 1]
            if 'coordinate' in room_info and room_info['coordinate'] == 'xyz':
                object_one['size'] = [abs(object_size[i]) / 100 for i in range(3)]
        # 容错硬装
        if 'type' in object_one and object_one['type'] in GROUP_MESH_LIST:
            object_size = [0, 0, 0]
            if 'size' in object_one and 'scale' in object_one:
                object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if 0.2 < object_size[2] < 0.5 and object_one['type'] in ['build element/background wall']:
                if 'relate' in object_one:
                    pass
            else:
                room_info['decorate_info'].append(object_one)
                furniture_dump.append(object_one)
                continue
        # 更新家具
        object_new = object_one
        # 种子家具
        object_id = object_one['id']
        origin_type, origin_style, origin_size, origin_scale = '', '', [], [1, 1, 1]
        if 'type' in object_one:
            origin_type = object_one['type']
        if 'style' in object_one:
            origin_style = object_one['style']
            origin_style = get_furniture_style_en(origin_style)
        if 'size' in object_one:
            object_size, object_scale = object_one['size'][:], [1, 1, 1]
            if 'scale' in object_one:
                object_scale = object_one['scale'][:]
            origin_size, origin_scale = object_size[:], object_scale[:]
            if 'scale' in object_one:
                origin_scale = object_one['scale'][:]
            if 'coordinate' in room_info and room_info['coordinate'] == 'xyz':
                origin_size = [object_size[0], object_size[2], object_size[1]]
                origin_scale = [object_scale[0], object_scale[2], object_scale[1]]
                if len(origin_size) >= 3 and len(origin_scale) >= 3 and False:
                    if abs(origin_scale[0]) > 0.001:
                        origin_size[0] /= origin_scale[0]
                    if abs(origin_scale[1]) > 0.001:
                        origin_size[1] /= origin_scale[1]
                    if abs(origin_scale[2]) > 0.001:
                        origin_size[2] /= origin_scale[2]
                if 'unit' in room_info and room_info['unit'] == 'm':
                    origin_size[0] *= 100
                    origin_size[1] *= 100
                    origin_size[2] *= 100
        # 错误家具
        current_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        current_type = ''
        if 'type' in object_one:
            current_type = object_one['type'].split('/')[0]
        if max(current_size[0], current_size[2]) < 0.01:
            if 'position' in object_one and max(abs(object_one['position'][0]), abs(object_one['position'][0])) < 0.01:
                furniture_dump.append(object_one)
                continue
        if abs(current_size[0] * current_size[2]) > room_area * 0.8:
            if current_type in ['door', 'window', 'curtain', '200 - on the floor']:
                furniture_dump.append(object_one)
                continue
        # 信息扩充
        category_id = ''
        if 'categories' in object_one and len(object_one['categories']) > 0:
            category_id = object_one['categories'][0]
            if len(category_id) > 0:
                object_new['category'] = category_id
        # 信息添加
        if not have_furniture_data(object_id):
            if len(origin_type) > 0 and len(origin_size) == 3:
                object_info = {
                    'type': origin_type,
                    'style': origin_style,
                    'size': origin_size[:],
                    'size_obj': origin_size[:],
                    'category_id': category_id
                }
                add_furniture_data(object_id, object_info)
            else:
                print('fetch object data', object_id)
                get_furniture_data(object_id)
        # 信息纠正
        if origin_type.startswith('customizedproducts'):
            object_type, object_style, object_size = origin_type, origin_style, origin_size[:]
        else:
            object_type, object_style, object_size = get_furniture_data(object_id)
        if 0 <= abs(origin_size[0] - object_size[0]) <= 1 and \
                0 <= abs(origin_size[1] - object_size[1]) <= 1 and \
                0 <= abs(origin_size[2] - object_size[2]) <= 1:
            HOUSE_SAMPLE_TUNE[object_id] = 1
        elif 0 <= abs(origin_size[0] * origin_scale[0] - object_size[0]) <= 10 and \
                0 <= abs(origin_size[2] * origin_scale[2] - object_size[2]) <= 10 and False:
            if object_id not in HOUSE_SAMPLE_TUNE:
                object_info = {
                    'type': object_type,
                    'style': object_style,
                    'size': origin_size[:],
                    'size_obj': origin_size[:],
                    'category_id': category_id
                }
                add_furniture_data(object_id, object_info)
                HOUSE_SAMPLE_TUNE[object_id] = 1
                print('tune furniture soft', object_id, origin_size, origin_scale, object_size)
        elif not category_id == '' and not have_furniture_data_key(object_id, 'category_id'):
            object_info = {
                'type': object_type,
                'style': object_style,
                'size': object_size[:],
                'size_obj': object_size[:],
                'category_id': category_id
            }
            add_furniture_data(object_id, object_info)
        if origin_type.startswith('customizedproducts'):
            object_type, object_style, object_size = origin_type, origin_style, origin_size[:]
        else:
            object_type, object_style, object_size = get_furniture_data(object_id)
        # 种子纠错
        object_origin, object_error = False, False
        if object_type == '' and not origin_type == '':
            object_origin = True
        elif (len(object_size) < 3 or abs(object_size[0]) <= 0.01) and \
                len(origin_size) >= 3 and abs(origin_size[0]) > 0.01:
            object_origin = True
        elif 'type' in object_one and 'bay window' in origin_type and \
                len(origin_size) >= 3 and abs(origin_size[0]) > 0.01:
            object_origin = True
        elif 'type' in object_one and 'parametric corner window' in origin_type and \
                len(origin_size) >= 3 and abs(origin_size[0]) > 0.01:
            object_origin = True
        # 原始信息
        if object_origin:
            object_type, object_style = '', ''
            if 'type' in object_one:
                object_type = object_one['type']
            if 'style' in object_one:
                object_style = object_one['style']
            if len(origin_size) >= 3:
                object_size = origin_size[:]
            object_new['size'] = object_size[:]
        # 错误信息
        elif object_type == '':
            object_type_id, object_style_id, object_category_id = get_furniture_data_refer_id(object_id)
            object_style_new = get_furniture_style_by_id(object_style_id)
            object_style_new = get_furniture_style_en(object_style_new)
            # 错误记录
            if (object_type == '' or object_style_new == '') and object_id not in ['', 'none', 'undefined']:
                object_error = True
            if not object_style_new == '' and not object_style_new == object_style:
                object_style = object_style_new
        if object_type == 'sofa/single seat sofa':
            if object_size[0] >= 160 and object_size[1] >= 60 and object_size[2] <= 120:
                object_type = 'sofa/ multi seat sofa'
        elif object_type in SOFA_CORNER_TYPE_0 and object_size[2] <= 100:
            object_error = True
        # 种子纠错
        if object_error:
            if object_type in SOFA_CORNER_TYPE_0 and object_size[2] <= 100:
                object_type = 'sofa/ multi seat sofa'
            elif object_size[0] + object_size[1] + object_size[2] >= 300:
                object_type = 'sofa/ multi seat sofa'
                if object_style == '' and 'style' in room_info:
                    object_style = room_info['style']
                if object_size[2] > 150:
                    object_type = 'sofa/type U sofa'

        # 确定类型
        object_new['type'] = object_type
        object_new['style'] = object_style
        if object_type in FURNITURE_TYPE_FIX:
            cate_id = ''
            if 'category' in object_new:
                cate_id = object_new['category']
            elif 'categories' in object_new and len(object_new['categories']) >= 1:
                cate_id = object_new['categories'][0]
            elif have_furniture_data_key(object_id, 'category_id'):
                type_id, style_id, cate_id = get_furniture_data_refer_id(object_id, '', False)
                object_one['category'] = cate_id
            elif object_type in ['300 - on top of others'] and current_size[0] + current_size[2] > 0.5:
                type_id, style_id, cate_id = get_furniture_data_refer_id(object_id, '', False)
                object_one['category'] = cate_id
            if len(cate_id) >= 0:
                object_cate_old = get_furniture_category_by_id(cate_id)
                object_type_new = get_furniture_type_by_category(object_cate_old)
                if len(object_type_new) > 0:
                    object_new['type'] = object_type_new
        # 确定尺寸
        if 'turn_fix' in object_one and object_one['turn_fix'] >= 1:
            pass
        else:
            object_new['size'] = object_size[:]
            object_new['scale'] = origin_scale[:]
        # 确定位置
        if 'position' in object_one:
            position_old = object_one['position'][:]
            object_new['position'] = position_old
            if 'coordinate' in room_info:
                if room_info['coordinate'] == 'xyz':
                    object_new['position'] = [position_old[0], position_old[2], position_old[1]]
        else:
            object_new['position'] = [0, 0, 0]
        # 确定旋转
        if 'rotation' in object_one:
            rotation_old = object_one['rotation'][:]
            object_new['rotation'] = rotation_old
            # 坐标纠正
            ang_dlt = 0
            if len(rotation_old) == 1:
                ang_new = normalize_angle((rotation_old[0] - ang_dlt) * math.pi / 180 * (-1))
                object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
            elif len(rotation_old) == 3:
                ang_new = normalize_angle((rotation_old[2] - ang_dlt) * math.pi / 180 * (-1))
                object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
            elif len(rotation_old) == 4:
                pass
            else:
                object_new['rotation'] = [0, 0, 0, 1]
        else:
            object_new['rotation'] = [0, 0, 0, 1]
    for object_one in furniture_dump:
        furniture_list.remove(object_one)
    # 材质信息
    if 'wall' in room_info['material_info']:
        if 'coordinate' in room_info and room_info['coordinate'] == 'xyz':
            for wall_mat in room_info['material_info']['wall']:
                if 'wall' in wall_mat:
                    wall_mat['wall'] = [[wall_mat['wall'][0][0], -wall_mat['wall'][0][1]], [wall_mat['wall'][1][0], -wall_mat['wall'][1][1]]]

    # 硬装信息
    decorate_list, decorate_dump, decorate_soft = [], [], []
    if 'decorate_info' in room_info:
        decorate_list = room_info['decorate_info']
    for object_one in decorate_list:
        object_new = object_one
        # 类型
        object_id = ''
        object_type, object_style = '', ''
        origin_size, origin_scale = [100, 100, 100], [1, 1, 1]
        if 'id' in object_one:
            object_id = object_one['id']
        if 'type' in object_one:
            object_type = object_one['type']
        if 'style' in object_one:
            object_style = object_one['style']
        if object_type in GROUP_MESH_SOFT:
            decorate_soft.append(object_one)
            decorate_dump.append(object_one)
        elif object_one['type'] in GROUP_MESH_DICT['ceiling']:
            object_set = []
            if 'customized_ceiling' in room_info['material_info']:
                object_set = room_info['material_info']['customized_ceiling']
            # temp code,该模型有问题
            if object_one['id'] != '64790bf9-f96f-4986-9560-2c7c204febde':
                object_set.append(object_one)
                room_info['material_info']['customized_ceiling'] = object_set
            decorate_dump.append(object_one)
        elif object_one['type'] in GROUP_MESH_DICT['background']:
            object_set = []
            if 'background' in room_info['material_info']:
                object_set = room_info['material_info']['background']
            object_set.append(object_one)
            room_info['material_info']['background'] = object_set
            decorate_dump.append(object_one)
        elif object_type in GROUP_MESH_LIST:
            pass
        else:
            pass
        if 'size' in object_one:
            object_size, object_scale = object_one['size'][:], [1, 1, 1]
            if 'scale' in object_one:
                object_scale = object_one['scale'][:]
            origin_size, origin_scale = object_size[:], object_scale[:]
            if 'scale' in object_one:
                origin_scale = object_one['scale'][:]
            if 'coordinate' in room_info and room_info['coordinate'] == 'xyz':
                origin_size = [object_size[0], object_size[2], object_size[1]]
                origin_scale = [object_scale[0], object_scale[2], object_scale[1]]
                if len(origin_size) >= 3 and len(origin_scale) >= 3 and False:
                    if abs(origin_scale[0]) > 0.001:
                        origin_size[0] /= origin_scale[0]
                    if abs(origin_scale[1]) > 0.001:
                        origin_size[1] /= origin_scale[1]
                    if abs(origin_scale[2]) > 0.001:
                        origin_size[2] /= origin_scale[2]
                if 'unit' in room_info and room_info['unit'] == 'm':
                    origin_size[0] *= 100
                    origin_size[1] *= 100
                    origin_size[2] *= 100
        # 信息扩充
        category_id = ''
        if 'categories' in object_one and len(object_one['categories']) > 0:
            category_id = object_one['categories'][0]
            if len(category_id) > 0:
                object_new['category'] = category_id
        # 信息纠正
        object_size = origin_size
        # 确定尺寸
        object_new['size'] = object_size[:]
        object_new['scale'] = origin_scale[:]
        # 确定位置
        if 'position' in object_one:
            position_old = object_one['position'][:]
            object_new['position'] = position_old
            if 'coordinate' in room_info:
                if room_info['coordinate'] == 'xyz':
                    object_new['position'] = [position_old[0], position_old[2], position_old[1]]
        else:
            continue
        # 确定旋转
        if 'rotation' in object_one:
            rotation_old = object_one['rotation'][:]
            object_new['rotation'] = rotation_old
            # 坐标纠正
            ang_dlt = 0
            if len(rotation_old) == 1:
                ang_new = normalize_angle((rotation_old[0] - ang_dlt) * math.pi / 180 * (-1))
                object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
            elif len(rotation_old) == 3:
                ang_new = normalize_angle((rotation_old[2] - ang_dlt) * math.pi / 180 * (-1))
                object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
            elif len(rotation_old) == 4:
                pass
            else:
                continue
        else:
            continue
        # 确定实体
        if 'entityId' not in object_one:
            object_new['entityId'] = ''
        pass
    for object_one in decorate_dump:
        decorate_list.remove(object_one)
    for object_one in decorate_soft:
        furniture_list.append(object_one)
    # 纠正朝向
    correct_room_turn(room_info)

    # 坐标信息
    room_info['coordinate'] = 'xzy'
    room_info['unit'] = 'cm'


# 数据解析：纠正点列
def correct_room_point(room_info):
    # 纠正点列
    if 'coordinate' in room_info and room_info['coordinate'] == 'xyz':
        room_info['mirror'] = 1
        # 轮廓
        if 'floor' in room_info:
            point_list_old = room_info['floor']
            point_list_new = correct_unit_point(point_list_old)
            # point_list_new = correct_unit_clock(point_list_new)
            room_info['floor'] = point_list_new
        # 机位
        if 'wander' in room_info:
            wander_list_old = room_info['wander']
            for wander_one in wander_list_old:
                wander_pos, wander_tar = [], []
                if 'pos' in wander_one:
                    wander_pos = wander_one['pos'][:]
                if 'target' in wander_one:
                    wander_tar = wander_one['target'][:]
                if wander_pos[2] <= 0.01:
                    wander_pos[2] = 1.3
                if wander_tar[2] <= 0.01:
                    wander_tar[2] = 1.3
                if len(wander_pos) >= 3:
                    wander_pos_new = [wander_pos[0], wander_pos[2], -wander_pos[1]]
                    wander_one['pos'] = wander_pos_new
                if len(wander_tar) >= 3:
                    wander_tar_new = [wander_tar[0], wander_tar[2], -wander_tar[1]]
                    wander_one['target'] = wander_tar_new
        # 部件
        for unit_name in ['door_info', 'hole_info', 'window_info', 'baywindow_info']:
            if unit_name in room_info:
                unit_list = room_info[unit_name]
                for unit_one in unit_list:
                    if 'pts' in unit_one:
                        point_list_old = unit_one['pts']
                        point_list_new = correct_unit_point(point_list_old)
                        unit_one['pts'] = point_list_new
        # 装修
        for unit_name in ['furniture_info', 'decorate_info']:
            if unit_name in room_info:
                unit_list = room_info[unit_name]
                for unit_one in unit_list:
                    if 'position' in unit_one:
                        unit_one['position'][1] *= -1


# 数据解析：纠正点列
def correct_unit_point(point_list):
    point_list_new = []
    point_count = int(len(point_list) / 2)
    for point_index in range(point_count):
        x = point_list[point_index * 2 + 0]
        y = -point_list[point_index * 2 + 1]
        point_list_new.insert(0, y)
        point_list_new.insert(0, x)
    return point_list_new


# 数据解析：纠正序列
def correct_unit_clock(point_list):
    clock_flag = compute_clockwise(point_list)
    point_list_new = []
    if clock_flag:
        point_list_new = point_list
    else:
        point_count = int(len(point_list) / 2)
        for point_index in range(point_count):
            x = point_list[point_index * 2 + 0]
            y = point_list[point_index * 2 + 1]
            point_list_new.insert(0, y)
            point_list_new.insert(0, x)
    return point_list_new


# 数据解析：纠正朝向
def correct_room_turn(room_info, width_min=0.05):
    if 'floor' not in room_info:
        return
    # 原始轮廓 线段
    line_ori = compute_room_line(room_info, width_min)
    # 原始轮廓 主门
    door_main, door_main_pt = {}, []
    for door_one in room_info['door_info']:
        if door_one['to'] == '':
            door_main = door_one
            break
        elif len(door_main) <= 0:
            door_main = door_one
    if len(door_main) > 0:
        door_pts = door_main['pts']
        door_main_pt = [(door_pts[0] + door_pts[2] + door_pts[4] + door_pts[6]) / 4,
                        (door_pts[1] + door_pts[3] + door_pts[5] + door_pts[7]) / 4]

    # 软装信息
    furniture_list = []
    furniture_rely = ['sofa', 'bed', 'table', 'media unit', 'electronics',
                      'cabinet', 'shelf', 'storage unit', 'bath',
                      '200 - on the floor', '300 - on top of others']
    if 'furniture_info' in room_info:
        furniture_list = room_info['furniture_info']
    for object_idx, object_one in enumerate(furniture_list):
        object_id, object_type = object_one['id'], object_one['type'].split('/')[0]
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        # 靠墙判断
        object_turn_fix, object_rely_fix = 0, False
        if 'turn_fix' in object_one:
            object_turn_fix = object_one['turn_fix']
        if object_turn_fix <= 0:
            if object_type in furniture_rely:
                object_rely_fix = True
            elif object_one['type'] in ['accessory/accessory - wall-attached']:
                if object_size[2] > 0.4 and object_size[2] > object_size[0]:
                    object_rely_fix = True
        if object_rely_fix:
            edge_idx, line_idx, unit_rat = compute_furniture_rely(object_one, line_ori)
            if 0 <= line_idx < len(line_ori) and 0 <= edge_idx < 4:
                # 纠正标准
                if object_size[2] > object_size[0] * 1.2 and object_size[2] > 0.6 and object_type not in ['bed']:
                    if object_size[2] < object_size[0] * 1.5 and object_type in ['table']:
                        pass
                    elif edge_idx == 1:
                        object_turn = -1
                        object_one['turn'], object_one['turn_fix'] = object_turn, 0
                        add_furniture_turn(object_id, object_turn)
                    elif edge_idx == 3:
                        object_turn = 1
                        object_one['turn'], object_one['turn_fix'] = object_turn, 0
                        add_furniture_turn(object_id, object_turn)
                elif object_size[0] > object_size[2] * 1.2 and object_size[0] > 0.5:
                    if edge_idx == 2:
                        object_turn = 2
                        object_one['turn'], object_one['turn_fix'] = object_turn, 0
                        add_furniture_turn(object_id, object_turn)
                elif object_one['type'] in ['accessory/accessory - wall-attached']:
                    if edge_idx == 1:
                        object_turn = -1
                        object_one['turn'], object_one['turn_fix'] = object_turn, 0
                        add_furniture_turn(object_id, object_turn)
                    elif edge_idx == 3:
                        object_turn = 1
                        object_one['turn'], object_one['turn_fix'] = object_turn, 0
                        add_furniture_turn(object_id, object_turn)
                # 纠正朝向
                line_one = line_ori[line_idx]
                rect_ang = ang_to_ang(line_one['angle'] + math.pi / 2)
                # 记录靠墙
                object_one['relate'] = 'wall'
                object_one['relate_role'] = 'wall'
            else:
                if object_size[2] > object_size[0] * 1.2 and object_size[2] > 1.0 and object_type in ['table', 'cabinet']:
                    object_turn = -1
                    object_one['turn'], object_one['turn_fix'] = object_turn, 0
                    add_furniture_turn(object_id, object_turn)
                else:
                    object_one['turn'], object_one['turn_fix'] = 0, 1

    # 硬装信息
    decorate_list = []
    if 'decorate_info' in room_info:
        decorate_list = room_info['decorate_info']
    for object_idx, object_one in enumerate(decorate_list):
        object_id, object_type = object_one['id'], object_one['type'].split('/')[0]
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]

        # 靠墙判断
        object_turn_fix, object_rely_fix = 0, False
        edge_idx = 0
        if 'turn_fix' in object_one:
            object_turn_fix = object_one['turn_fix']
        if object_turn_fix <= 0:
            if 'edge' in object_one and 'form' in object_one and len(object_one['form']) > 0:
                edge_idx = int(object_one['edge'])
            if 1 <= edge_idx < 4:
                object_rely_fix = True
            else:
                edge_idx, line_idx, unit_rat = compute_furniture_rely(object_one, line_ori)
                if 0 <= line_idx < len(line_ori) and 0 <= edge_idx < 4:
                    object_one['relate'] = 'wall'
                    object_one['relate_role'] = 'wall'
                    if 1 <= edge_idx < 4:
                        object_rely_fix = True
                    else:
                        object_one['turn'], object_one['turn_fix'] = 0, 1
        if object_rely_fix:
            # 纠正标准
            if object_size[2] > object_size[0] * 1.2 and object_size[2] > 0.6 and object_type not in ['bed']:
                if edge_idx == 1:
                    object_turn = -1
                    object_one['turn'], object_one['turn_fix'] = object_turn, 0
                    add_furniture_turn(object_id, object_turn)
                elif edge_idx == 3:
                    object_turn = 1
                    object_one['turn'], object_one['turn_fix'] = object_turn, 0
                    add_furniture_turn(object_id, object_turn)
            elif object_size[0] > object_size[2] * 1.2 and object_size[0] > 0.5:
                if edge_idx == 2:
                    object_turn = 2
                    object_one['turn'], object_one['turn_fix'] = object_turn, 0
                    add_furniture_turn(object_id, object_turn)


# 数据解析：纠正类型
def correct_room_type(room_info, seed_list=[], keep_list=[], plus_list=[]):
    room_id, room_type, room_area = '', '', 0
    if 'id' in room_info:
        room_id = room_info['id']
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    if '14225' in room_id and False:
        print('correct room ', room_id, '------debug------')
    # 原有类型
    if room_type not in ROOM_TYPE_LIST and not room_id == '':
        for type_new in ROOM_TYPE_LIST:
            if type_new.lower() in room_id.lower():
                room_type = type_new
                break
    room_type_old = room_type
    # 窗户判断
    room_open, room_hole, room_link = 0, 0, ''
    if 'window_info' in room_info:
        unit_list = room_info['window_info']
        unit_max = 0
        for unit_one in unit_list:
            unit_pts = unit_one['pts']
            unit_len = int(len(unit_pts) / 2)
            for i in range(unit_len - 1):
                x1, y1, x2, y2 = unit_pts[2 * i + 0], unit_pts[2 * i + 1], unit_pts[2 * i + 2], unit_pts[2 * i + 3]
                unit_dis = max(abs(x1 - x2), abs(y1 - y2))
                if unit_dis >= 3:
                    unit_max = unit_dis
                    break
                else:
                    unit_max = max(unit_dis, unit_max)
            room_open += unit_max
    if 'hole_info' in room_info:
        unit_list = room_info['hole_info']
        for unit_one in unit_list:
            unit_to = unit_one['to']
            if unit_to == '':
                room_link = unit_to
            else:
                room_link = unit_to
            unit_pts = unit_one['pts']
            if len(unit_pts) >= 8:
                unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                            (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                unit_dis = abs(unit_pts[0] - unit_pos[0]) + abs(unit_pts[1] - unit_pos[1])
                room_hole += unit_dis
    if 'door_info' in room_info:
        unit_list = room_info['door_info']
        for unit_one in unit_list:
            unit_to, unit_link = '', ''
            if 'to' in unit_one:
                unit_to = unit_one['to']
            if 'link' in unit_one:
                unit_link = unit_one['link']
            if len(unit_link) > 0:
                room_link = unit_link
            else:
                room_link = unit_to
            unit_pts = unit_one['pts']
            if len(unit_pts) >= 8:
                unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                            (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                unit_dis = abs(unit_pts[0] - unit_pos[0]) + abs(unit_pts[1] - unit_pos[1])
                if unit_dis > room_hole:
                    room_hole = unit_dis

    # 锚点判断
    if len(seed_list) > 0:
        ready_group, ready_group_area, ready_group_area_all = {}, {}, 0
        for object_one in seed_list:
            object_group, object_role, object_id = object_one['group'], object_one['role'], object_one['id']
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_area = object_size[0] * object_size[2]
            if object_group in ['Meeting'] and object_role in ['side sofa']:
                continue
            ready_group[object_group] = object_id
            if object_group not in ready_group_area:
                ready_group_area[object_group] = object_area
            else:
                ready_group_area[object_group] += object_area
            ready_group_area_all += object_area
        if len(ready_group) <= 0:
            pass
        elif room_area >= 100:
            room_type = 'LivingDiningRoom'
        elif 'Bed' in ready_group:
            if 'Bedroom' not in room_type:
                if room_area >= 50:
                    pass
                elif room_type in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                    pass
                elif room_type in ['Library']:
                    pass
                else:
                    room_type = 'Bedroom'
        elif 'Meeting' in ready_group and 'Dining' in ready_group:
            room_type = 'LivingDiningRoom'
            if room_area < 15:
                room_type = 'LivingRoom'
        elif 'Meeting' in ready_group:
            if 'Library' in room_type and 'Work' in ready_group:
                pass
            elif 'Library' in room_type and 'Cabinet' in ready_group:
                pass
            elif 'Living' not in room_type and 10 < room_area:
                room_type = 'LivingDiningRoom'
                if room_area < 15:
                    room_type = 'LivingRoom'
            elif 'Dining' in ready_group and 10 < room_area:
                room_type = 'LivingDiningRoom'
                if room_area < 15:
                    room_type = 'LivingRoom'
        elif 'Dining' in ready_group:
            if 'Dining' not in room_type:
                if 'Living' in room_type_old:
                    room_type = 'LivingDiningRoom'
                else:
                    room_type = 'LivingDiningRoom'
                    room_area_sub = 0
                    if 'Dining' in ready_group_area:
                        room_area_sub = ready_group_area['Dining'] * 1.5
                    if room_area - room_area_sub < 20:
                        room_type = 'DiningRoom'
        elif 'Armoire' in ready_group and 'Bedroom' not in room_type:
            if room_type in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                pass
            elif room_type in ['Library']:
                pass
            else:
                room_type = 'Bedroom'
        elif 'Bath' in ready_group or 'Toilet' in ready_group:
            room_type = 'Bathroom'
        elif 'Work' in ready_group:
            # type
            object_id = ready_group['Work']
            object_type, object_style, object_size = get_furniture_data(object_id)
            category_name, room_type = get_furniture_room_by_object(object_id)
            if room_area <= 10 and room_open + room_hole >= 3:
                room_type = 'Balcony'
            # cate
            if room_type == '':
                type_id, style_id, category_id = get_furniture_data_refer_id(object_id, reload=False)
                if not category_id == '':
                    category_name, room_type = get_furniture_room_by_category(category_id)
            # check
            if room_type == '' and room_type_old == '':
                if object_type in ['table/console table']:
                    room_type = 'Library'
                elif object_type in ['table/table'] and room_area > 10 and room_info['type'] == '':
                    room_type = 'Library'
            if room_type == '':
                room_type = room_type_old
        elif 'Rest' in ready_group:
            if room_area >= 30:
                room_type = 'Library'
            elif room_area <= ROOM_AREA_BALCONY and room_type not in ROOM_TYPE_MAIN:
                room_type = 'Balcony'
            elif room_area >= 8 and 'Cabinet' in ready_group and 'Bedroom' in room_type:
                room_type = 'Library'
        elif 'Cabinet' in ready_group:
            # type
            object_id = ready_group['Cabinet']
            object_type, object_style, object_size = get_furniture_data(object_id)
            category_name, room_type = get_furniture_room_by_object(object_id)
            # cate
            if room_type == '':
                type_id, style_id, category_id = get_furniture_data_refer_id(object_id, reload=False)
                if not category_id == '':
                    category_name, room_type = get_furniture_room_by_category(category_id)
                    if room_type_old in ROOM_TYPE_MAIN and room_type_old not in ['OtherRoom']:
                        room_type = room_type_old
            # check
            if room_type == '' and room_type_old == '':
                if object_type in ['cabinet/bookcase - L shaped', 'shelf/book shelf']:
                    room_type = 'Library'
            if room_type == '':
                room_type = room_type_old

    # 类型判断
    if room_type not in ROOM_TYPE_LIST and not room_type == '':
        for room_type_one in ROOM_TYPE_LIST:
            if room_type.lower() == room_type_one.lower():
                room_type = room_type_one
                break
    if room_type not in ROOM_TYPE_LIST and not room_type == '':
        room_type = ''
    # 标识判断
    if room_type in ['', 'none', 'undefined'] and not room_id == '':
        for type_new in ROOM_TYPE_LIST:
            if type_new.lower() in room_id.lower():
                room_type = type_new
                break
    # 补充判断
    if len(seed_list) <= 0 and len(keep_list) > 0:
        pass

    # 面积判断
    if room_type in ['', 'none', 'undefined', 'OtherRoom']:
        if room_area >= ROOM_AREA_LIVINGROOM:
            room_type = 'LivingDiningRoom'
        elif room_area <= ROOM_AREA_STORAGE:
            room_type = 'StorageRoom'
            if room_link == '':
                room_type = 'Hallway'
            elif room_open > min(room_area / 3, 2) or room_hole > min(room_area / 3, 1):
                room_type = 'Balcony'
        elif ROOM_AREA_STORAGE <= room_area <= ROOM_AREA_BATHROOM:
            if 'Bedroom' in room_link:
                if room_open > min(room_area / 3, 2) or room_hole > min(room_area / 3, 1):
                    room_type = 'Balcony'
                else:
                    room_type = 'CloakRoom'
            elif room_link == '':
                room_type = 'Hallway'
            elif room_open > min(room_area / 3, 2) or room_hole > min(room_area / 3, 1):
                room_type = 'Balcony'
            else:
                room_type = 'Bathroom'
        elif ROOM_AREA_BATHROOM < room_area <= ROOM_AREA_BEDROOM:
            if 'Bedroom' in room_link:
                room_type = 'Bathroom'
            elif room_link == '':
                room_type = 'Hallway'
            elif room_open > min(room_area / 3, 2):
                room_type = 'Balcony'
            else:
                room_type = 'OtherRoom'
        else:
            room_type = 'Bedroom'
            if room_open > min(room_area / 3, 2):
                room_type = 'Balcony'
                if room_link == '':
                    room_type = 'Hallway'
    if 0.01 < room_area < 2.00 and room_type in ROOM_TYPE_LEVEL_2:
        room_type = 'CloakRoom'

    # 纠正类型
    room_info['type'] = room_type
    for seed_one in seed_list:
        if seed_one['group'] == 'Meeting':
            if 'Bedroom' in room_type or room_type in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                seed_one['group'] == 'Rest'
                seed_one['role'] == 'chair'
        if seed_one['group'] == 'Work':
            if 'Living' in room_type:
                seed_one['group'] = 'Dining'

    # 别名
    room_alias = room_id
    room_split = room_alias.split('-')
    if not room_split[0] == room_type:
        room_alias = room_type + '-' + room_split[-1]
    room_info['alias'] = room_alias

    # 返回类型
    return room_type


# 数据解析：纠正连通 纠正门窗
def correct_room_link(room_info):
    room_type = ''
    if 'type' in room_info:
        room_type = room_info['type']
    # 全部门窗
    room_link_set = []
    unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow = [], [], [], []
    if 'door_info' in room_info:
        unit_list_door = room_info['door_info']
    if 'hole_info' in room_info:
        unit_list_hole = room_info['hole_info']
    if 'window_info' in room_info:
        unit_list_window = room_info['window_info']
    if 'baywindow_info' in room_info:
        unit_list_baywindow = room_info['baywindow_info']
    # 纠正多门
    unit_have = []
    for unit_one in unit_list_door:
        unit_pts, unit_pos = unit_one['pts'], []
        if len(unit_pts) >= 8:
            unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                        (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
        elif len(unit_pts) >= 2:
            unit_pos = [unit_pts[0], unit_pts[1]]
        if len(unit_pos) >= 2:
            unit_pos_new = unit_pos[:]
            unit_pos_err = False
            for unit_old in unit_have:
                unit_pts, unit_pos = unit_old['pts'], []
                if len(unit_pts) >= 8:
                    unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                                (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                elif len(unit_pts) >= 2:
                    unit_pos = [unit_pts[0], unit_pts[1]]
                unit_pos_old = unit_pos[:]
                if abs(unit_pos_new[0] - unit_pos_old[0]) + abs(unit_pos_new[1] - unit_pos_old[1]) < 0.2:
                    unit_pos_err = True
                    break
            if not unit_pos_err:
                unit_have.append(unit_one)
    unit_list_door = unit_have
    room_info['door_info'] = unit_have
    # 纠正门窗
    door_move, door_dump, door_main, door_long = [], [], [], []
    for unit_one in unit_list_door:
        unit_to = ''
        if 'to' in unit_one:
            unit_to = unit_one['to']
        if unit_to == '':
            unit_pts = unit_one['pts']
            x_p = unit_pts[(0 + 0) % len(unit_pts)]
            y_p = unit_pts[(0 + 1) % len(unit_pts)]
            x_q = unit_pts[(0 + 2) % len(unit_pts)]
            y_q = unit_pts[(0 + 3) % len(unit_pts)]
            x_r = unit_pts[(0 + 4) % len(unit_pts)]
            y_r = unit_pts[(0 + 5) % len(unit_pts)]
            dis_1, ang_1 = xyz_to_ang(x_p, y_p, x_q, y_q)
            dis_2, ang_2 = xyz_to_ang(x_q, y_q, x_r, y_r)
            if len(unit_list_door) + len(unit_list_hole) <= 1:
                pass
            elif max(dis_1, dis_2) > UNIT_WIDTH_DOOR * 3:
                door_move.append(unit_one)
            elif max(dis_1, dis_2) < UNIT_WIDTH_DOOR / 3:
                door_dump.append(unit_one)
            elif max(dis_1, dis_2) > 0.5 and room_type in ['Balcony', 'Terrace']:
                door_move.append(unit_one)
            elif max(dis_1, dis_2) > 0.2 and ('Bathroom' in room_type or room_type in ROOM_TYPE_LEVEL_2):
                door_move.append(unit_one)
            else:
                if max(dis_1, dis_2) > UNIT_WIDTH_DOOR * 1.5:
                    door_long.append(unit_one)
                door_main.append(unit_one)
    if len(door_move) < len(unit_list_door):
        for unit_one in door_move:
            unit_one['height'] = 0
            unit_list_door.remove(unit_one)
            unit_list_window.append(unit_one)
    for unit_one in door_dump:
        unit_list_door.remove(unit_one)
    for unit_one in door_long:
        if len(door_main) - len(door_long) < 1:
            break
        unit_one['height'] = 0
        unit_list_door.remove(unit_one)
        unit_list_window.append(unit_one)
    # 纠正连通
    for unit_list_one in [unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow]:
        door_flag = False
        if unit_list_one == unit_list_door or unit_list_one == unit_list_hole:
            door_flag = True
        for unit_one in unit_list_one:
            unit_link = ''
            if 'to' in unit_one:
                unit_to = unit_one['to']
            if 'link' in unit_one:
                unit_link = unit_one['link']
            if unit_link not in ROOM_TYPE_LIST:
                unit_link = unit_to.split('-')[0]
                if unit_link not in ROOM_TYPE_LIST:
                    unit_link = ''
            unit_one['link'] = unit_link
            if door_flag:
                unit_one['height'] = 0
                room_link_set.append(unit_link)
    room_info['link'] = room_link_set
    # 模型连通
    object_list = []
    if 'furniture_info' in room_info:
        object_list = room_info['furniture_info']
    for object_one in object_list:
        object_type = object_one['type']
        if object_type.startswith('door'):
            pass
        elif object_type.startswith('window'):
            pass
        else:
            continue
        object_pos = object_one['position']
        for unit_list_one in [unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow]:
            for unit_one in unit_list_one:
                unit_pts, unit_pos = unit_one['pts'], []
                if len(unit_pts) >= 8:
                    unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                                (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                elif len(unit_pts) >= 2:
                    unit_pos = [unit_pts[0], unit_pts[1]]
                else:
                    continue
                if abs(object_pos[0] - unit_pos[0]) + abs(object_pos[2] - unit_pos[1]) <= 0.1:
                    unit_to_room, unit_to_type = '', ''
                    if 'to' in unit_one:
                        unit_to_room = unit_one['to']
                    if 'link' in unit_one:
                        unit_to_type = unit_one['link']
                    if len(unit_to_type) <= 0 and len(unit_to_room) > 0:
                        unit_to_type = unit_to_room.split('-')[0]
                    object_one['unit_to_room'] = unit_to_room
                    object_one['unit_to_type'] = unit_to_type
                    break
    pass


# 数据解析：划分区域
def correct_room_zone(room_info, room_layout):
    room_type = room_info['type']
    if room_type in ROOM_TYPE_LEVEL_1 or room_type in ROOM_TYPE_LEVEL_2:
        pass
    else:
        return
    unit_list_door, unit_list_hole, unit_list_window, unit_list_baywindow = [], [], [], []
    if 'door_info' in room_info:
        unit_list_door = room_info['door_info']
    if 'hole_info' in room_info:
        unit_list_hole = room_info['hole_info']
    if 'window_info' in room_info:
        unit_list_window = room_info['window_info']
    if 'baywindow_info' in room_info:
        unit_list_baywindow = room_info['baywindow_info']
    scheme_list = []
    if 'layout_scheme' in room_layout:
        scheme_list = room_layout['layout_scheme']
    for scheme_idx, scheme_one in enumerate(scheme_list):
        group_list, zone_list, sofa_list, cloth_list = [], [], [], []
        if 'group' in scheme_one:
            group_list = scheme_one['group']
        # 入户门 厨房门 厕所门
        for unit_list_one in [unit_list_door, unit_list_hole]:
            for unit_one in unit_list_one:
                door_to_id = unit_one['to']
                door_to_type = ''
                if len(door_to_type) <= 0 and 'link' in unit_one:
                    door_to_type = unit_one['link']
                if 'pts' in unit_one and len(unit_one['pts']) >= 8:
                    unit_pts = unit_one['pts']
                    zone_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4, 0,
                                (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                    if door_to_id in ['']:
                        zone_list.append({'zone': 'Hallway', 'group': 'Door', 'position': zone_pos})
                    elif door_to_type in ['Kitchen']:
                        zone_list.append({'zone': 'DiningRoom', 'group': 'Door', 'position': zone_pos})
                    elif door_to_type in ['Bathroom', 'MasterBathroom', 'SecondBathroom']:
                        zone_list.append({'zone': 'Bathroom', 'group': 'Door', 'position': zone_pos})
        # 办公 休息 卫浴 衣帽
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type not in GROUP_RULE_FUNCTIONAL:
                continue
            zone_pos = group_one['position'][:]
            if group_type in ['Meeting']:
                group_one['zone'] = 'LivingRoom'
                zone_list.append({'zone': 'LivingRoom', 'group': group_type, 'position': zone_pos})
                sofa_list.append(group_one)
            elif group_type in ['Dining']:
                group_one['zone'] = 'DiningRoom'
                zone_list.append({'zone': 'DiningRoom', 'group': group_type, 'position': zone_pos})
            elif group_type in ['Media']:
                if room_type in ['LivingRoom', 'LivingDiningRoom']:
                    group_one['zone'] = 'LivingRoom'
                    zone_list.append({'zone': 'LivingRoom', 'group': group_type, 'position': zone_pos})
                elif room_type in ['Library']:
                    group_one['zone'] = 'Library'
                    zone_list.append({'zone': 'Library', 'group': group_type, 'position': zone_pos})
                elif room_type in ROOM_TYPE_LEVEL_2:
                    group_one['zone'] = 'Bedroom'
                    zone_list.append({'zone': 'Bedroom', 'group': group_type, 'position': zone_pos})
            elif group_type in ['Bed']:
                group_one['zone'] = 'Bedroom'
                zone_list.append({'zone': 'Bedroom', 'group': group_type, 'position': zone_pos})
            elif group_type in ['Work', 'Rest']:
                if 'obj_type' in group_one and 'table' in group_one['obj_type']:
                    group_one['zone'] = 'Library'
                    zone_list.append({'zone': 'Library', 'group': group_type, 'position': zone_pos})
            elif group_type in ['Bath', 'Toilet']:
                group_one['zone'] = 'Bathroom'
                zone_list.append({'zone': 'Bathroom', 'group': group_type, 'position': zone_pos})
            elif group_type in ['Armoire'] and room_type in ROOM_TYPE_LEVEL_2:
                cloth_list.append(group_one)
        if len(cloth_list) == 1:
            group_one = cloth_list[0]
            zone_pos = group_one['position'][:]
            group_one['zone'] = 'CloakRoom'
            zone_list.append({'zone': 'CloakRoom', 'group': 'Armoire', 'position': zone_pos})
        elif len(cloth_list) > 1:
            cloth_link = {}
            for old_idx, old_one in enumerate(cloth_list):
                old_size, old_pos = old_one['size'], old_one['position']
                cloth_link[old_idx] = []
                for new_idx, new_one in enumerate(cloth_list):
                    new_size, new_pos = new_one['size'], new_one['position']
                    dis_x, dis_z = abs(new_pos[0] - old_pos[0]), abs(new_pos[2] - old_pos[2])
                    if max(dis_x, dis_z) < old_size[0] + new_size[0] + 0.2 and min(dis_x, dis_z) < min(old_size[2], new_size[2]) / 2:
                        cloth_link[old_idx].append(new_idx)
                    elif max(dis_x, dis_z) < min(old_size[0] + new_size[2] * 0.5 + 0.2, old_size[2] + new_size[0] * 0.5 + 0.2):
                        cloth_link[old_idx].append(new_idx)
            max_set = []
            for old_idx, old_set in cloth_link.items():
                if len(old_set) > len(max_set):
                    max_set = old_set
            if len(max_set) > 0:
                grp = cloth_list[max_set[0]]
                rect = compute_furniture_rect(grp['size'], grp['position'], grp['rotation'])
                min_x = min(rect[0], rect[2], rect[4], rect[6])
                max_x = max(rect[0], rect[2], rect[4], rect[6])
                min_z = min(rect[1], rect[3], rect[5], rect[7])
                max_z = max(rect[1], rect[3], rect[5], rect[7])
                for max_idx in max_set:
                    grp = cloth_list[max_idx]
                    grp['zone'] = 'CloakRoom'
                    rect = compute_furniture_rect(grp['size'], grp['position'], grp['rotation'])
                    min_x = min(rect[0], rect[2], rect[4], rect[6], min_x)
                    max_x = max(rect[0], rect[2], rect[4], rect[6], max_x)
                    min_z = min(rect[1], rect[3], rect[5], rect[7], min_z)
                    max_z = max(rect[1], rect[3], rect[5], rect[7], max_z)
                zone_pos = [(min_x + max_x) / 2, 0, (min_z + max_z) / 2]
                zone_list.append({'zone': 'CloakRoom', 'group': 'Armoire', 'position': zone_pos})
        # 区域
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type not in GROUP_RULE_FUNCTIONAL:
                continue
            if group_type not in ['Cabinet']:
                continue
            if 'zone' in group_one and len(group_one['zone']) > 0:
                continue
            if 'obj_main' in group_one:
                obj_main = group_one['obj_main']
                type_id, style_id, category_id = get_furniture_data_refer_id(obj_main)
                obj_cate, obj_zone = get_furniture_room_by_category(category_id)
                if obj_main in ['ffb41867-04a3-4b02-ab2a-28a35fffb8c6']:
                    pass
                elif obj_zone in ['Hallway', 'Bathroom']:
                    group_one['zone'] = obj_zone
                    continue
                elif obj_zone in ['DiningRoom']:
                    pass
            group_pos = group_one['position']
            group_rect = compute_furniture_rect(group_one['size'], group_one['position'], group_one['rotation'])
            #
            near_idx, near_dis, near_zone, near_group, near_pos, near_rot = -1, 10, '', '', [], []
            for zone_idx, zone_val in enumerate(zone_list):
                zone_type, zone_group, zone_pos = zone_val['zone'], zone_val['group'], zone_val['position']
                dis_0 = abs(group_pos[0] - zone_pos[0]) + abs(group_pos[2] - zone_pos[2])
                dis_1 = abs(group_rect[0] - zone_pos[0]) + abs(group_rect[1] - zone_pos[2])
                dis_2 = abs(group_rect[2] - zone_pos[0]) + abs(group_rect[3] - zone_pos[2])
                dis_3 = abs(group_rect[4] - zone_pos[0]) + abs(group_rect[5] - zone_pos[2])
                dis_4 = abs(group_rect[6] - zone_pos[0]) + abs(group_rect[7] - zone_pos[2])
                zone_dis = min(dis_0, dis_1, dis_2, dis_3, dis_4)
                if zone_dis < near_dis:
                    near_idx, near_dis = zone_idx, zone_dis,
                    near_zone, near_group, near_pos = zone_type, zone_group, zone_pos
            if len(near_zone) > 0 and (near_dis < 2 or (near_dis < 4 and near_group in ['Meeting', 'Dining'])):
                group_one['zone'] = near_zone
                if near_group in ['Meeting'] and len(near_pos) > 0 and len(sofa_list) == 1:
                    plat_ang = rot_to_ang(sofa_list[0]['rotation'])
                    tmp_x, tmp_z = group_pos[0] - near_pos[0], group_pos[2] - near_pos[2]
                    add_x = tmp_z * math.sin(-plat_ang) + tmp_x * math.cos(-plat_ang)
                    add_z = tmp_z * math.cos(-plat_ang) - tmp_x * math.sin(-plat_ang)
                    if -0.5 < add_x < 0.5 and -2.5 < add_z < -0.1:
                        group_one['relate_group'], group_one['relate_role'] = 'Meeting', 'sofa'
                elif near_group in ['Media'] and len(near_pos) > 0:
                    group_one['relate_group'], group_one['relate_role'] = 'Media', 'tv'


# 数据解析：纠正避让
def correct_room_move(room_layout, object_one):
    # 物品信息
    plat_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    plat_pos, plat_rot, plat_ang = object_one['position'], object_one['rotation'], rot_to_ang(object_one['rotation'])
    plat_fix_y = 0.05
    # 避让信息
    plat_mov_x = 0
    plat_mov_z = min(plat_size[0], plat_size[2], 0.5)
    plat_add_x = plat_mov_z * math.sin(plat_ang) + plat_mov_x * math.cos(plat_ang)
    plat_add_z = plat_mov_z * math.cos(plat_ang) - plat_mov_x * math.sin(plat_ang)
    # 分组信息
    scheme_list = []
    if 'layout_scheme' in room_layout:
        scheme_list = room_layout['layout_scheme']
    for scheme_idx, scheme_one in enumerate(scheme_list):
        group_list, group_todo, object_todo = [], [], []
        if 'group' in scheme_one:
            group_list = scheme_one['group']
        # 避让检测
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            # 组合检测
            if group_type in GROUP_RULE_FUNCTIONAL:
                group_rect = compute_furniture_rect(group_one['size'], group_one['position'], group_one['rotation'])
                point_0 = [(group_rect[0] + group_rect[2]) / 2, 0, (group_rect[1] + group_rect[3]) / 2]
                point_1 = [group_rect[0], 0, group_rect[1]]
                point_2 = [group_rect[2], 0, group_rect[3]]
                for obj_pos in [point_0, point_1, point_2]:
                    plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
                    plat_on = False
                    # 垂直距离
                    if abs(plat_dis[1]) >= plat_size[1] + plat_fix_y:
                        plat_on = False
                        continue
                    # 水平距离
                    ang = 0 - rot_to_ang(plat_rot)
                    dis_x = plat_dis[2] * math.sin(ang) + plat_dis[0] * math.cos(ang)
                    dis_z = plat_dis[2] * math.cos(ang) - plat_dis[0] * math.sin(ang)
                    if abs(dis_z) >= plat_size[2] / 2 + 0.02:
                        plat_on = False
                        continue
                    if abs(dis_x) >= plat_size[0] / 2 - 0.05:
                        if abs(dis_x) <= plat_size[0] / 2 + 0.05:
                            wait_on = True
                            break
                        plat_on = False
                        continue
                    # 符合要求
                    plat_on = True
                    group_todo.append(group_one)
                    break
            # 物品检测
            elif group_type in ['Wall', 'Floor']:
                obj_set = []
                if 'obj_list' in group_one:
                    obj_set = group_one['obj_list']
                for obj_idx, obj_one in enumerate(obj_set):
                    obj_pos = obj_one['position']
                    plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
                    plat_on = False
                    # 垂直距离
                    if abs(plat_dis[1]) >= plat_size[1] + plat_fix_y:
                        plat_on = False
                        continue
                    # 水平距离
                    ang = 0 - rot_to_ang(plat_rot)
                    dis_x = plat_dis[2] * math.sin(ang) + plat_dis[0] * math.cos(ang)
                    dis_z = plat_dis[2] * math.cos(ang) - plat_dis[0] * math.sin(ang)
                    if abs(dis_z) >= plat_size[2] / 2 + 0.02:
                        plat_on = False
                        continue
                    if abs(dis_x) >= plat_size[0] / 2 - 0.05:
                        if abs(dis_x) <= plat_size[0] / 2 + 0.05:
                            wait_on = True
                            break
                        plat_on = False
                        continue
                    # 符合要求
                    plat_on = True
                    object_todo.append(obj_one)
        # 避让处理
        for group_idx, group_one in enumerate(group_todo):
            # 组合避让
            group_pos = group_one['position']
            group_pos[0] += plat_add_x
            group_pos[2] += plat_add_z
            # 物品避让
            object_list = group_one['obj_list']
            for object_idx, object_one in enumerate(object_list):
                object_pos = object_one['position']
                object_pos[0] += plat_add_x
                object_pos[2] += plat_add_z
        for object_idx, object_one in enumerate(object_todo):
            object_pos = object_one['position']
            object_pos[0] += plat_add_x
            object_pos[2] += plat_add_z


# 数据解析：纠正家具
def correct_room_seed(seed_list, keep_list=[]):
    for object_one in seed_list:
        object_id = object_one['id']
        if object_id.startswith('link'):
            continue
        object_type, object_style, object_size = get_furniture_data(object_id)
        if object_type == 'sofa/single seat sofa' and object_size[0] >= 160:
            object_type = 'sofa/ multi seat sofa'
        elif object_type in SOFA_CORNER_TYPE_0 and object_size[2] <= 100:
            object_type = 'sofa/ multi seat sofa'
        object_one['type'] = object_type
        object_one['style'] = object_style
    for object_one in keep_list:
        object_id = object_one['id']
        object_type, object_style, object_size = get_furniture_data(object_id)
        if object_type == 'sofa/single seat sofa' and object_size[0] >= 160:
            object_type = 'sofa/ multi seat sofa'
        elif object_type in SOFA_CORNER_TYPE_0 and object_size[2] <= 100:
            object_type = 'sofa/ multi seat sofa'
        object_one['type'] = object_type
        object_one['style'] = object_style


# 数据解析：纠正家具
def correct_object_type(object_one, object_type='', room_type=''):
    if len(object_type) <= 0 and 'type' in object_one:
        object_type = object_one['type']
    object_cate_id = ''
    if 'category' in object_one:
        object_cate_id = object_one['category']
    elif 'categories' in object_one and len(object_one['categories']) >= 1:
        object_cate_id = object_one['categories'][0]
        object_one['category'] = object_cate_id
    # 纠正模型
    object_key = object_one['id']
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    if object_type in ['200 - on the floor']:
        size_fix, type_fix = object_size, ''
        if room_type in ROOM_TYPE_LEVEL_2:
            if size_fix[0] > 1.0 and 0.1 < size_fix[1] < 1.0 and size_fix[2] > 1.5:
                type_fix = 'bed/king-size bed'
                if size_fix[0] > 2.0 and 0.1 < size_fix[1] < 0.5 and size_fix[2] < 1.5:
                    type_fix = 'bed/crib'
                elif size_fix[0] < 1.8:
                    type_fix = 'bed/single bed'
        if type_fix == '':
            if size_fix[0] > 1.0 and size_fix[1] > 0.5 and 0.1 < size_fix[2] < 0.8:
                type_fix = 'cabinet/floor-based cabinet'
            elif 0.1 < size_fix[0] < 1.0 and 0.1 < size_fix[1] < 3.0 and 0.1 < size_fix[2] < 1.0:
                if abs(object_one['position'][1]) < 0.1:
                    type_fix = 'accessory/accessory - on top of others'
                elif abs(object_one['position'][1]) > 0.2:
                    type_fix = 'accessory/accessory - on top of others'
        if not type_fix == '':
            object_type = type_fix
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
    elif object_type in ['300 - on top of others']:
        cate_key, cate_fix, type_fix = '', '', ''
        if 'category' in object_one:
            cate_key = object_one['category']
            cate_fix = get_furniture_category_by_id(cate_key)
            if not cate_fix == '':
                type_fix = get_furniture_type_by_category(cate_fix)
        if not type_fix == '':
            object_one['type'] = type_fix
        elif object_size[0] > 0.5 and object_size[1] > 0.5 and object_size[2] < 0.1:
            type_fix = 'art/art - wall-attached'
            object_one['type'] = type_fix
    elif object_type in ['sofa/ multi seat sofa', 'sofa/sofa set', 'sofa/sofa bed',
                         'sofa/left corner sofa', 'sofa/right corner sofa', 'sofa/type L sofa', 'sofa/type U sofa']:
        if object_size[0] < 1.5:
            type_fix = 'sofa/single seat sofa'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
        elif object_size[0] > 2.0 and object_size[2] < min(1.25, object_size[0] * 0.5) and \
                object_type in SOFA_CORNER_TYPE_0:
            type_fix = 'sofa/ multi seat sofa'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
    elif object_type in ['sofa/single seat sofa']:
        if object_size[0] > 2.0:
            type_fix = 'sofa/ multi seat sofa'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
        elif object_size[0] > 1.5:
            type_fix = 'sofa/double seat sofa'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
    elif object_type.startswith('bed'):
        if max(object_size[0], object_size[1], object_size[2]) < 0.1:
            pass
        elif max(object_size[0], object_size[2]) < 0.8 and object_size[1] < 0.8:
            type_fix = 'table/side table'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
        elif max(object_size[0], object_size[2]) > 0.8 and min(object_size[0], object_size[2]) < 0.5:
            type_fix = 'cabinet/floor-based cabinet'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
    elif object_type in ['wardrobe/base wardrobe']:
        size_fix, type_fix = object_size, ''
        if room_type in ROOM_TYPE_LEVEL_2:
            if size_fix[0] > 1.5 and 0.1 < size_fix[1] < 0.8 and 1.0 < size_fix[2] < size_fix[0]:
                type_fix = 'bed/king-size bed'
                if size_fix[0] > 2.0 and 0.1 < size_fix[1] < 0.5 and size_fix[2] < 1.5:
                    type_fix = 'bed/crib'
            elif size_fix[2] > 1.5 and 0.1 < size_fix[1] < 0.8 and 1.0 < size_fix[0] < size_fix[2]:
                type_fix = 'bed/king-size bed'
                if size_fix[2] > 2.0 and 0.1 < size_fix[1] < 0.5 and size_fix[0] < 1.5:
                    type_fix = 'bed/crib'
        if not type_fix == '':
            object_one['type'] = type_fix
    elif object_type.startswith('cabinet') and object_size[1] < 0.5:
        object_category_new, object_group_new, object_role_new = \
            compute_furniture_cate_by_id(object_key, object_type, object_cate_id)
        if object_group_new in ['Media'] and object_role_new in ['table']:
            type_fix = 'media unit/floor-based media unit'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
    elif object_type.startswith('table') and max(object_size[0], object_size[2]) < 0.6:
        if max(object_size[0], object_size[2]) < 0.5 or 0.6 < object_size[1] < 1.0:
            type_fix = 'table/side table'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
    elif object_type.startswith('table') and min(object_size[0], object_size[2]) < 0.8 and \
            1.5 < max(object_size[0], object_size[2]):
        if min(object_size[0], object_size[2]) * 4 < max(object_size[0], object_size[2]):
            if object_size[1] < 0.75:
                type_fix = 'media unit/floor-based media unit'
                object_one['type'] = type_fix
                add_furniture_type(object_key, type_fix)
            else:
                type_fix = 'cabinet/floor-based cabinet'
                object_one['type'] = type_fix
                add_furniture_type(object_key, type_fix)
    elif object_type in ['table/side table'] and object_size[0] > 1.0:
        object_category_new, object_group_new, object_role_new = \
            compute_furniture_cate_by_id(object_key, object_type, object_cate_id)
        if object_group_new in ['Meeting'] and object_role_new in ['table']:
            type_fix = 'table/coffee table - rectangular'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)
        elif object_size[0] > 1.0 and 0.2 < object_size[2] < 0.8:
            type_fix = 'table/coffee table - rectangular'
            object_one['type'] = type_fix
            add_furniture_type(object_key, type_fix)


# 数据计算：计算轮廓
def compute_room_line(room_info, width_min=0.05):
    # 原始轮廓 顶点
    floor_pts = room_info['floor']
    if len(floor_pts) >= 2:
        begin_x, begin_z = floor_pts[0], floor_pts[1]
        end_x, end_z = floor_pts[-2], floor_pts[-1]
        if abs(begin_x - end_x) + abs(begin_z - end_z) >= 0.01:
            room_info['floor'].append(begin_x)
            room_info['floor'].append(begin_z)
    else:
        return []
    floor_len = int(len(floor_pts) / 2)
    # 原始轮廓 线段
    line_ori = []
    for i in range(floor_len - 1):
        # 起点终点
        x1, y1, x2, y2 = floor_pts[2 * i + 0], floor_pts[2 * i + 1], floor_pts[2 * i + 2], floor_pts[2 * i + 3]
        length, angle = xyz_to_ang(x1, y1, x2, y2)
        # 跳过
        if length <= width_min:
            continue
        # 拼接
        if len(line_ori) > 0:
            line_old = line_ori[-1]
            x1_old, y1_old = line_old['p1'][0], line_old['p1'][1]
            x2_old, y2_old = line_old['p2'][0], line_old['p2'][1]
            angle_old = line_old['angle']
            if abs(ang_to_ang(angle - angle_old)) < 0.1 and abs(x2_old - x1) + abs(y2_old - y1) < width_min:
                line_ori.pop(-1)
                x1, y1 = x1_old, y1_old
        # 垂直
        if abs(x2 - x1) <= width_min and abs(y2 - y1) >= 5 * abs(x2 - x1):
            x2 = x1
        if abs(y2 - y1) <= width_min and abs(x2 - x1) >= 5 * abs(y2 - y1):
            y2 = y1
        # 线段角度
        length, angle = xyz_to_ang(x1, y1, x2, y2)
        line_width = length
        line_one = {
            'p1': [x1, y1],
            'p2': [x2, y2],
            'width': line_width,
            'angle': angle
        }
        line_ori.append(line_one)
    # 原始轮廓 去重
    for line_idx in range(len(line_ori) - 1, -1, -1):
        line_1 = line_ori[line_idx]
        line_2 = line_ori[0]
        x1, y1, x2, y2 = line_1['p2'][0], line_1['p2'][1], line_2['p1'][0], line_2['p1'][1]
        angle1, angle2 = line_1['angle'], line_2['angle']
        if abs(angle1 - angle2) < 0.1 and abs(x2 - x1) + abs(y2 - y1) < width_min:
            line_2['p1'] = line_1['p1'][:]
            line_2['width'] += line_1['width']
            line_ori.pop(line_idx)
    return line_ori


# 数据计算：计算种子
def compute_room_seed(furniture_list_old, decorate_list, room_type='', room_area=15, furniture_dict={}):
    furniture_list = []
    for furniture_idx, furniture_one in enumerate(furniture_list_old):
        furniture_type = furniture_one['type'].split('/')[0]
        furniture_size = [abs(furniture_one['size'][i]) * abs(furniture_one['scale'][i]) / 100 for i in range(3)]
        furniture_pos = [0, 0, 0]
        if 'position' in furniture_one:
            furniture_pos = furniture_one['position']
        if furniture_type in ['sofa', 'bed', 'media unit', 'media', 'electronics',
                              'table', 'chair', 'wardrobe', 'storage unit', 'cabinet', 'shelf', 'basin', 'stool']:
            furniture_list.append(furniture_one)
        elif furniture_type in ['200 - on the floor'] \
                and abs(furniture_size[0] + furniture_size[2]) > 2 and furniture_pos[1] < 0.1:
            furniture_list.append(furniture_one)
        elif furniture_type in ['shower', 'bath', 'toilet']:
            furniture_list.append(furniture_one)
        elif furniture_type in ['300 - on top of others'] and \
                abs(furniture_size[0] + furniture_size[2]) > 2:
            furniture_list.append(furniture_one)

    # 种子信息
    seed_list, keep_list, plus_list, mesh_list = [], [], [], []
    seed_list_sub1, seed_list_sub2, seed_list_sub3 = [], [], []
    # 软装信息
    for object_idx, object_one in enumerate(furniture_list):
        object_key = object_one['id']
        object_type, object_style, object_cate_id = '', '', ''
        if 'type' in object_one:
            object_type = object_one['type']
        if 'style' in object_one:
            object_style = object_one['style']
        if 'category' in object_one:
            object_cate_id = object_one['category']
        elif 'categories' in object_one and len(object_one['categories']) >= 1:
            object_cate_id = object_one['categories'][0]
            object_one['category'] = object_cate_id
        # 排除硬装
        if object_type in GROUP_MESH_LIST:
            continue
        if object_type in DECO_OBJECT_TYPE_0:
            continue
        # 纠正模型
        correct_object_type(object_one, object_type, room_type)
        object_type = object_one['type']
        origin_size, origin_scale = object_one['size'], object_one['scale']
        object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        # 计算角色
        object_group, object_role = compute_furniture_role(object_type, object_size, room_type, object_key, object_cate_id)
        object_one['group'], object_one['role'] = object_group, object_role
        if object_key in furniture_dict:
            object_old = furniture_dict[object_key]
            object_old['group'], object_old['role'] = object_group, object_role
        # 主要家具
        if object_type in GROUP_SEED_LIST:
            # 次要家具
            if object_role in ['table', 'side table'] and object_group in ['Meeting', 'Bed']:
                keep_list.append(object_one)
            # 主要家具
            else:
                object_size_new = object_size
                if object_role in ['sofa', 'bed']:
                    seed_list_sub1.append(object_one)
                elif object_role in ['table', 'armoire', 'cabinet']:
                    find_idx = -1
                    for sub_idx, sub_one in enumerate(seed_list_sub2):
                        object_size_old = [abs(sub_one['size'][i] * sub_one['scale'][i]) for i in range(3)]
                        if object_size_new[0] + object_size_new[1] > object_size_old[0] + object_size_old[1]:
                            find_idx = sub_idx
                            break
                    if 0 <= find_idx < len(seed_list_sub2):
                        seed_list_sub2.insert(find_idx, object_one)
                    else:
                        seed_list_sub2.append(object_one)
                elif not object_role == '':
                    seed_list_sub3.append(object_one)
                else:
                    plus_list.append(object_one)
        else:
            # 次要家具
            if object_group in ['Meeting'] and object_role in ['side sofa']:
                seed_list_sub3.append(object_one)
            elif object_group in ['Rest'] and object_role in ['chair']:
                seed_list_sub3.append(object_one)
            elif object_group in ['Cabinet'] and object_role in ['cabinet']:
                seed_list_sub3.append(object_one)
            elif object_group in ['Door', 'Window']:
                keep_list.append(object_one)
            elif object_group in GROUP_RULE_DECORATIVE:
                plus_list.append(object_one)
            elif object_role in ['sofa']:
                object_one['role'] = 'side sofa'
                keep_list.append(object_one)
            elif object_role in ['tv']:
                keep_list.append(object_one)
            elif object_role not in ['', 'rug', 'accessory']:
                keep_list.append(object_one)
    # 硬装信息
    for object_idx, object_one in enumerate(decorate_list):
        object_one = object_one
        # 角色
        object_role = compute_decorate_mesh(object_one['type'], object_one['size'])
        object_one['group'] = ''
        object_one['role'] = object_role
        # 判错
        object_y = object_one['position'][1]
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        object_width, object_height, object_depth = object_size[0], object_size[1], object_size[2]
        if object_role == 'ceiling' and object_y <= 0:
            continue
        elif object_y + object_height <= 0:
            continue
        if object_role == 'background' and object_height <= 0.1 and object_depth >= 1:
            continue
        elif object_width > 10 or object_depth > 10:
            continue
        # 添加
        mesh_list.append(object_one)
    # 排序种子
    for seed_one in seed_list_sub1:
        seed_list.append(seed_one)
    for seed_one in seed_list_sub2:
        seed_list.append(seed_one)
    for seed_one in seed_list_sub3:
        seed_list.append(seed_one)
    # 种子纠正
    table_meet, table_food = [], []
    for seed_one in seed_list:
        if seed_one['group'] in ['Meeting'] and seed_one['role'] in ['table']:
            table_meet.append(seed_one)
        elif seed_one['group'] in ['Dining'] and seed_one['role'] in ['table']:
            table_food.append(seed_one)
    if room_type in ['LivingDiningRoom']:
        if len(table_meet) <= 0 and len(table_food) >= 2:
            table_new = table_food[0]
            for table_one in table_food:
                if table_one['size'][1] + table_one['size'][2] <= table_new['size'][1] + table_new['size'][2]:
                    table_new = table_one
            if table_new['size'][1] < 50:
                table_new['group'] = 'Meeting'
        if len(table_meet) >= 2 and len(table_food) <= 0:
            table_new = table_meet[0]
            for table_one in table_meet:
                if table_one['size'][1] + table_one['size'][2] >= table_new['size'][1] + table_new['size'][2]:
                    table_new = table_one
            if table_new['size'][1] > 50:
                table_new['group'] = 'Dining'
    # 面积纠正
    if len(seed_list) <= 0 and len(keep_list) > 0 and room_area <= 5:
        object_main = {}
        for object_one in keep_list:
            object_group, object_role = object_one['group'], object_one['role']
            if object_role in ['table', 'side table']:
                object_one['group'], object_one['role'] = 'Rest', 'table'
                object_main = object_one
                break
            elif object_role in ['side sofa']:
                object_one['group'], object_one['role'] = 'Rest', 'chair'
        if len(object_main) > 0:
            keep_list.remove(object_main)
            seed_list.append(object_main)
    if len(seed_list) <= 0 and len(plus_list) > 0 and room_area <= 5:
        object_main = {}
        for object_one in plus_list:
            object_type = object_one['type']
            if 'table' in object_type:
                object_one['group'], object_one['role'] = 'Rest', 'table'
                object_main = object_one
                break
        if len(object_main) > 0:
            plus_list.remove(object_main)
            seed_list.append(object_main)
    # 分组纠正
    if len(seed_list) > 0 and len(keep_list) > 0:
        group_main_1, group_main_2 = '', ''
        for object_one in seed_list:
            object_group, object_role = object_one['group'], object_one['role']
            if object_group in ['Meeting', 'Bed']:
                group_main_1 = object_group
            elif object_group in ['Dining', 'Work']:
                group_main_2 = object_group
        for object_one in keep_list:
            object_group, object_role = object_one['group'], object_one['role']
            if object_role in ['side table']:
                if not group_main_1 == '':
                    object_one['group'], object_one['role'] = group_main_1, 'side table'
            if object_role in ['side sofa']:
                if not group_main_2 == '' and object_one['type'] in ['chair/chair', 'chair/armchair']:
                    object_one['group'], object_one['role'] = group_main_2, 'chair'
    # 分组纠正
    if len(furniture_dict) > 0:
        for object_one in seed_list:
            object_key = object_one['id']
            if object_key in furniture_dict:
                object_one = furniture_dict[object_key]
                if 'group' in object_one and 'role' in object_one:
                    object_one['group'], object_one['role'] = object_one['group'], object_one['role']
        for object_one in keep_list:
            object_key = object_one['id']
            if object_key in furniture_dict:
                object_one = furniture_dict[object_key]
                if 'group' in object_one and 'role' in object_one:
                    object_one['group'], object_one['role'] = object_one['group'], object_one['role']
    return seed_list, keep_list, plus_list, mesh_list


# 数据计算：计算特征 TODO:
def compute_room_vector(group_list, room_type, size_ratio=1.0):
    global ROOM_TYPE_CODE
    # 特征信息
    if room_type in ROOM_TYPE_CODE:
        room_code = ROOM_TYPE_CODE[room_type]
    else:
        room_code = ROOM_TYPE_CODE['none']
    room_vector = [room_code, 0, 0, 0, 0, 0, 0, 0, 0]
    # 组合计算
    for group_one in group_list:
        group_type, group_size = group_one['type'], group_one['size'][:]
        group_regulate, group_neighbor = [0, 0, 0, 0], [0, 0, 0, 0]
        if 'regulation' in group_one:
            group_regulate = group_one['regulation'][:]
        if 'neighbor_best' in group_one:
            group_neighbor = group_one['neighbor_best'][:]
        # 调整尺寸
        group_size[0] += group_regulate[1]
        group_size[0] += group_regulate[3]
        group_size[2] += group_regulate[0]
        group_size[2] += group_regulate[2]
        group_size[0] += group_neighbor[1]
        group_size[0] += group_neighbor[3]
        group_size[2] += group_neighbor[0]
        group_size[2] += group_neighbor[2]
        if group_type in ['Bed']:
            group_size[0] = min(group_size[0], 2.8)
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

    # 返回信息
    return room_vector


# 数据计算：计算区域 TODO:
def compute_room_region(group_list, room_type):
    room_region, deco_region = [], []
    for group_one in group_list:
        group_type, group_size = group_one['type'], group_one['size'][:]
        group_pos, group_rot = group_one['position'], group_one['rotation']
        # 主要区域
        if group_type in ['Meeting', 'Bed', 'Bath']:
            pass
        elif group_type in ['Dining'] and room_type in ['DiningRoom']:
            pass
        elif group_type in ['Work'] and room_type in ['Library']:
            pass
        # 电视区域
        elif group_type in ['Media']:
            pass
        # 工作区域
        elif group_type in ['Dining', 'Work', 'Toilet']:
            pass
        # 柜体区域
        elif group_type in ['Armoire', 'Cabinet']:
            pass
        else:
            continue
        # 增加区域
        region_add = {'type': group_type, 'size': group_size[:], 'position': group_pos[:], 'rotation': group_rot[:]}
        # 确认区域
        region_fix = {}
        if group_type in ['Armoire', 'Cabinet']:
            for region_idx, region_old in enumerate(room_region):
                if region_old['type'] in ['Armoire', 'Cabinet']:
                    size_new, size_old = region_add['size'], region_old['size']
                    if size_new[0] * size_new[1] * size_new[2] > size_old[0] * size_old[1] * size_old[2]:
                        room_region[region_idx] = region_add
                    region_fix = room_region[region_idx]
                    break
        if len(region_fix) <= 0:
            room_region.append(region_add)
    return room_region


# 数据检索
def unique_room_sample(sample_dict):
    room_layout_fine = []
    for type_key, type_val in sample_dict.items():
        for area_key, area_val in type_val.items():
            for room_one in area_val:
                if 'source_room_flag' in room_one and room_one['source_room_flag'] >= 1:
                    room_new = room_one.copy()
                    room_new['group'] = []
                    for group_one in room_one['group']:
                        group_add = group_one.copy()
                        group_add['size'] = group_one['size'][:]
                        group_add['offset'] = group_one['offset'][:]
                        group_add['size_min'] = group_one['size_min'][:]
                        room_new['group'].append(group_add)
                    room_layout_fine.append(room_new)
                    break
    return room_layout_fine


# 数据检索
def assign_room_sample(room_type, room_area, sample_dict, seed_list=[], keep_list=[], plus_list=[],
                       sample_num=1, sample_id='', sample_room_id='', sample_sort=0, type_have={}):
    # 单屋布局
    room_layout_fine = []
    # 加载模板
    room_layout_dict = sample_dict

    # 匹配规则
    room_area = float(room_area)
    room_area_int = int(room_area)
    if room_type in ['SecondBedroom', 'Bedroom'] and room_area_int >= 18:
        room_type = 'MasterBedroom'
    type_list = [room_type]
    # 客厅、餐厅、客餐厅
    if room_type == 'LivingDiningRoom':
        type_list = ['LivingDiningRoom']
    # 主卧、次卧、卧室
    elif room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom']:
        type_list = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'ElderlyRoom']
        if room_area_int <= 15:
            type_list = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
    # 儿童房
    elif room_type in ['KidsRoom']:
        type_list = ['KidsRoom']
        type_count = 0
        for type_one in type_list:
            if type_one in room_layout_dict:
                type_count += 1
        if type_count < sample_num:
            type_list = ['KidsRoom', 'SecondBedroom', 'Bedroom']
    # 老人房、保姆房
    elif room_type in ['ElderlyRoom', 'NannyRoom']:
        type_list = ['ElderlyRoom', 'NannyRoom', 'SecondBedroom']
        type_count = 0
        for type_one in type_list:
            if type_one in room_layout_dict:
                type_count += 1
        if type_count < sample_num:
            type_list = ['ElderlyRoom', 'NannyRoom', 'SecondBedroom', 'Bedroom']
    # 书房
    elif room_type in ['Library']:
        type_list = ['Library']
    # 洗手间
    elif room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
        type_list = ['MasterBathroom', 'SecondBathroom', 'Bathroom']
    # 阳台
    elif room_type in ['Balcony', 'Terrace', 'Lounge', 'Auditorium']:
        type_list = ['Balcony', 'Terrace', 'Lounge', 'Auditorium']
    # 门厅、过道、走廊
    elif room_type in ['Hallway', 'Aisle', 'Corridor', 'Stairwell']:
        type_list = ['Hallway', 'Aisle', 'Corridor', 'Stairwell']
    # 洗衣房
    elif room_type in ['LaundryRoom']:
        type_list = ['LaundryRoom']
    # 其他
    elif room_type in ['OtherRoom']:
        type_list = ['Balcony', 'Terrace', 'OtherRoom']
    # 补充类型
    type_comp, group_dump = [], []  # 丢弃分组
    if room_type == 'LivingRoom':
        if room_area > 30:
            type_list = ['LivingRoom', 'LivingDiningRoom']
            group_dump = ['Dining']
        elif room_area > 20 and len(sample_id) > 0:
            type_list = ['LivingRoom', 'LivingDiningRoom']
            group_dump = ['Dining']
        else:
            type_list = ['LivingRoom', 'LivingDiningRoom']
            group_dump = ['Dining']
        # 客厅餐厅
        if room_type not in sample_dict and 'LivingDiningRoom' not in sample_dict:
            type_list = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']
            group_dump = []
        elif room_type not in sample_dict and 'LivingDiningRoom' in sample_dict:
            type_list = ['LivingRoom', 'LivingDiningRoom']
            group_dump = []
    elif room_type == 'DiningRoom':
        type_list = ['DiningRoom', 'LivingDiningRoom']
        group_dump = ['Meeting', 'Media']
        # 客厅餐厅
        if room_type not in sample_dict and 'LivingDiningRoom' not in sample_dict:
            type_list = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']
    elif room_type == 'LivingDiningRoom':
        type_list = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']
        type_comp = ['LivingRoom', 'DiningRoom']

    # 查找模板
    sample_room_list, sample_room_self = [], False
    sample_room_back = []
    for type_one in type_list:
        if type_one not in room_layout_dict:
            continue
        for room_area_old, room_list_old in room_layout_dict[type_one].items():
            room_area_old = int(room_area_old)
            if room_area_old <= 0:
                continue
            for room_one in room_list_old:
                if not sample_id == '' and not room_one['source_house'] == sample_id:
                    continue
                if not sample_room_id == '' and not room_one['source_room'] == sample_room_id:
                    continue
                room_new = {}
                sample_comp = False
                # 房间处理
                if room_type in ['LaundryRoom']:
                    if len(room_one['group']) <= 0:
                        continue
                    if not room_one['group'][0]['type'] == 'Appliance':
                        continue
                elif room_type in ['Lounge']:
                    if len(room_one['group']) <= 0:
                        continue
                    if not room_one['group'][0]['type'] == 'Rest':
                        continue
                elif room_type in ['Kitchen']:
                    if len(room_one['group']) <= 0:
                        pass
                elif room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom'] and room_area > 2.5:
                    have_bath, have_toilet, have_cabinet = False, False, False
                    for group_one in room_one['group']:
                        if group_one['type'] in ['Bath']:
                            have_bath = True
                        elif group_one['type'] in ['Toilet']:
                            have_toilet = True
                        elif group_one['type'] in ['Cabinet']:
                            have_cabinet = True
                    if room_area >= 2.5 and not have_bath and not have_toilet:
                        sample_room_back.append(room_one)
                        continue
                    elif room_area >= 5 and (not have_bath or not have_toilet or not have_cabinet):
                        sample_room_back.append(room_one)
                        continue
                elif room_type in ROOM_TYPE_LEVEL_2:
                    have_main = False
                    for group_one in room_one['group']:
                        if group_one['type'] in ['Bed']:
                            have_main = True
                    if not have_main:
                        continue
                elif room_type in ['Balcony', 'Terrace', 'OtherRoom']:
                    have_main = False
                    for group_one in room_one['group']:
                        if group_one['type'] in ['Rest', 'Cabinet']:
                            have_main = True
                    if not have_main:
                        continue
                else:
                    if len(room_one['group']) <= 0:
                        continue
                # 查找样板
                type_new, area_new = type_one, room_one['area']
                if type_one in ['LivingDiningRoom']:
                    have_meeting, have_dining, have_media = False, False, False
                    area_meeting, area_dining, area_media = 0, 0, 0
                    if len(room_one['group']) >= 0:
                        for group_one in room_one['group']:
                            group_type, group_size = group_one['type'], group_one['size']
                            if group_type in ['Meeting']:
                                have_meeting = True
                                area_meeting = group_size[0] * group_size[2]
                            elif group_type in ['Dining']:
                                have_dining = True
                                area_dining = group_size[0] * group_size[2]
                            elif group_type in ['Media']:
                                have_media = True
                                area_media = group_size[0] * group_size[2]
                    if len(group_dump) > 0:
                        if 'Dining' in group_dump:
                            # type_new = 'LivingRoom'
                            if room_area < 15:
                                area_new = (area_meeting + area_media) * 2
                            else:
                                area_new = room_one['area'] - area_dining
                        elif 'Living' in group_dump:
                            # type_new = 'DiningRoom'
                            if room_area < 15:
                                area_new = area_dining * 2
                            else:
                                area_new = room_one['area'] - (area_meeting + area_media)
                    elif have_meeting and have_dining:
                        type_new = 'LivingDiningRoom'
                    elif have_meeting and not have_dining:
                        type_new = 'LivingRoom'
                    elif have_dining and not have_meeting:
                        type_new = 'DiningRoom'
                    else:
                        type_new = 'LivingRoom'
                if type_new in type_comp:
                    for sample_one in sample_room_list:
                        if not sample_one['source_house'] == room_one['source_house']:
                            continue
                        if sample_one['type'] not in type_comp:
                            continue
                        if sample_one['type'] == type_one:
                            continue
                        room_new = sample_one
                        room_new['area'] += room_one['area']
                        room_new['group_area'] += room_one['group_area']
                        sample_comp = True
                # 新建样板
                if not sample_comp:
                    room_new = room_one.copy()
                    room_new['type'] = type_new
                    room_new['area'] = area_new
                    room_new['group'] = []
                    sample_room_list.append(room_new)
                # 添加分组
                for group_one in room_one['group']:
                    if group_one['type'] in group_dump:
                        continue
                    group_add = group_one.copy()
                    group_add['size'] = group_one['size'][:]
                    group_add['offset'] = group_one['offset'][:]
                    group_add['size_min'] = group_one['size_min'][:]
                    room_new['group'].append(group_add)
                # 本身样板
                if not sample_room_id == '' and room_one['source_room'] == sample_room_id:
                    sample_room_self = True
                    break
            if sample_room_self:
                break
        if sample_room_self:
            break
    # 补充模板
    for room_one in sample_room_list:
        if len(sample_room_back) <= 0:
            break
        for room_old in sample_room_back:
            if not room_one['source_house'] == room_old['source_house']:
                continue
            if room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
                have_cabinet = False
                for group_one in room_one['group']:
                    if group_one['type'] in ['Cabinet']:
                        have_cabinet = True
                        break
                if not have_cabinet:
                    for group_old in room_old['group']:
                        if group_old['type'] in ['Cabinet']:
                            group_add = group_one.copy()
                            group_add['size'] = group_one['size'][:]
                            group_add['offset'] = group_one['offset'][:]
                            group_add['size_min'] = group_one['size_min'][:]
                            room_one['group'].append(group_add)
                            room_one['area'] += room_old['area']
                            break
        pass

    # 种子排序
    sample_room_sort0 = []
    for room_one in sample_room_list:
        if len(seed_list) <= 0 and len(keep_list) <= 0:
            break
        seed_used, keep_used, seed_good, keep_good = [], [], 0, 0
        # 种子匹配
        source_house, source_room = room_one['source_house'], room_one['source_room']
        group_list = get_furniture_group_list(source_house, source_room, GROUP_RULE_FUNCTIONAL.keys())
        for group_one in group_list:
            if 'obj_list' not in group_one:
                continue
            group_type = group_one['type']
            object_list = group_one['obj_list']
            for object_one in object_list:
                object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
                object_height = object_one['size'][1] * object_one['scale'][1] / 100
                if object_role in ['', 'accessory', 'rug']:
                    continue
                # 种子匹配
                for seed_one in seed_list:
                    seed_id, seed_type = seed_one['id'], seed_one['type']
                    seed_group, seed_role = seed_one['group'], seed_one['role']
                    seed_height = seed_one['size'][1] * seed_one['scale'][1] / 100
                    if seed_id in seed_used:
                        continue
                    if not seed_group == group_type:
                        continue
                    if seed_role in ['', 'accessory', 'rug']:
                        continue
                    if seed_role in ['armoire', 'cabinet'] and object_role in ['armoire', 'cabinet']:
                        seed_same = False
                        if seed_height <= UNIT_HEIGHT_ARMOIRE_MIN and object_height <= UNIT_HEIGHT_ARMOIRE_MIN:
                            seed_same = True
                        elif seed_height >= UNIT_HEIGHT_ARMOIRE_MIN and object_height >= UNIT_HEIGHT_ARMOIRE_MIN:
                            seed_same = True
                        elif abs(seed_height - object_height) <= 0.1:
                            seed_same = True
                        if seed_same:
                            seed_good += 1
                            seed_used.append(seed_id)
                            break
                    elif seed_role == object_role:
                        seed_good += 1
                        seed_used.append(seed_id)
                        break
                # 保留匹配
                for keep_one in keep_list:
                    keep_id, keep_type = keep_one['id'], keep_one['type']
                    keep_group, keep_role = keep_one['group'], keep_one['role']
                    if keep_id in keep_used:
                        continue
                    if not keep_group == group_type:
                        continue
                    if keep_role in ['', 'accessory', 'rug']:
                        continue
                    if keep_role == object_role:
                        keep_good += 1
                        keep_used.append(keep_id)
                        break
        # 面积匹配
        area_good = 1 - abs(room_area - room_one['area']) / 100
        if 'Bath' in room_type and room_area < 5:
            group_area = 1.0
            for group_one in group_list:
                group_area = group_one['size'][0] * group_one['size'][2]
                if group_one['type'] == 'Bath':
                    break
            area_good = 1 - abs(group_area) / 100
        # 整体匹配
        room_good = seed_good + keep_good + area_good
        if room_type in ['KidsRoom']:
            if room_type == room_one['type']:
                room_good += 1
        room_one['good'] = room_good
        find_idx = -1
        for sample_idx, sample_old in enumerate(sample_room_sort0):
            if room_good > sample_old['good']:
                find_idx = sample_idx
                break
            pass
        if 0 <= find_idx < len(sample_room_sort0):
            sample_room_sort0.insert(find_idx, room_one)
        else:
            sample_room_sort0.append(room_one)

    # 房型排序
    sample_room_sort1, sample_room_sort2 = [], []
    for room_one in sample_room_list:
        room_area_new = room_one['area']
        room_type_new = room_one['type']
        if room_type_new in ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'ElderlyRoom']:
            if 'group' in room_one and len(room_one['group']) > 0:
                group_main = room_one['group'][0]
                if 'type' in group_main and group_main['type'] in ['Bed']:
                    if 'size' in group_main and 'size_min' in group_main:
                        main_area_max = (group_main['size'][0] * group_main['size'][2])
                        main_area_min = (group_main['size_min'][0] * group_main['size_min'][2])
                        room_area_new -= (main_area_max - main_area_min)
        # 类型排序
        if room_one['type'] in ['LivingRoom', 'DiningRoom', 'Bedroom', 'Bathroom']:
            sample_room_sort = sample_room_sort2
        elif room_one['type'] in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
            sample_room_sort = sample_room_sort2
        elif room_one['type'] in ['Balcony', 'Terrace', 'OtherRoom']:
            sample_room_sort = sample_room_sort2
        elif room_one['type'] == room_type or room_one['source_room'].startswith(room_type):
            if room_one['type'] in ['LivingRoom', 'DiningRoom']:
                sample_room_sort = sample_room_sort2
            else:
                sample_room_sort = sample_room_sort1
        else:
            sample_room_sort = sample_room_sort2
        # 面积排序
        find_idx = -1
        for sample_idx, sample_old in enumerate(sample_room_sort):
            room_area_old = sample_old['area']
            room_type_old = sample_old['type']
            if room_type_old in ['LivingDiningRoom'] and not room_type_old == room_type:
                room_area_old *= 0.8
            elif room_type_old in ['Library']:
                if 'group' in sample_old and len(sample_old['group']) > 0:
                    group_main = sample_old['group'][0]
                    if 'type' in group_main and group_main['type'] not in ['Work']:
                        room_area_old *= 0.5
            elif room_type_old in ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'ElderlyRoom']:
                if 'group' in sample_old and len(sample_old['group']) > 0:
                    group_main = sample_old['group'][0]
                    if 'type' in group_main and group_main['type'] in ['Bed']:
                        if 'size' in group_main and 'size_min' in group_main:
                            main_area_max = (group_main['size'][0] * group_main['size'][2])
                            main_area_min = (group_main['size_min'][0] * group_main['size_min'][2])
                            room_area_old -= (main_area_max - main_area_min)
            # 面积排序
            if sample_sort >= 1:
                if abs(room_area_old - room_area * 2.0) > abs(room_area_new - room_area * 2.0):
                    find_idx = sample_idx
                    break
            elif sample_sort <= -1:
                if abs(room_area_old - room_area * 0.5) > abs(room_area_new - room_area * 0.5):
                    find_idx = sample_idx
                    break
            else:
                delta_old = abs(room_area_old - room_area)
                delta_new = abs(room_area_new - room_area)
                if room_type in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                    if room_type_old not in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                        delta_old += 5
                    if room_type_new not in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                        delta_new += 5
                else:
                    if room_type_old in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                        delta_old += 5
                    if room_type_new in ['KidsRoom', 'ElderlyRoom', 'NannyRoom']:
                        delta_new += 5
                if room_type in ['LivingDiningRoom'] and room_area < 20:
                    delta_old = room_area_old - room_area
                    delta_new = room_area_new - room_area
                if delta_new < delta_old:
                    find_idx = sample_idx
                    break
        if 0 <= find_idx < len(sample_room_sort):
            sample_room_sort.insert(find_idx, room_one)
        else:
            sample_room_sort.append(room_one)

    # 添加模板
    for sample_idx, room_one in enumerate(sample_room_sort0):
        if len(room_layout_fine) >= sample_num:
            break
        room_layout_fine.append(room_one)
    for sample_idx, room_one in enumerate(sample_room_sort1):
        if len(room_layout_fine) >= sample_num:
            break
        room_layout_fine.append(room_one)
    for sample_idx, room_one in enumerate(sample_room_sort2):
        if len(room_layout_fine) >= sample_num:
            break
        room_layout_fine.append(room_one)

    # 返回信息
    return room_layout_fine


# 数据检索
def search_room_sample(room_type, room_area, seed_list=[], keep_list=[], plus_list=[],
                       sample_num=3, sample_id='', sample_room_id='', sample_sort=0, type_have={}):
    # 加载模板
    room_layout_dict = load_house_sample()
    # 查找模板
    room_layout_fine = assign_room_sample(room_type, room_area, room_layout_dict, seed_list, keep_list, plus_list,
                                          sample_num, sample_id, sample_room_id, sample_sort, type_have)

    # 返回信息
    return room_layout_fine


# 数据检索
def search_room_origin(room_type, room_area, room_mirror=0, seed_list=[], keep_list=[], plus_list=[], sample_num=3):
    # 提取打组
    if len(seed_list) > 0:
        group_have = []
        for seed_one in seed_list:
            if 'group' in seed_one:
                group_have.append(seed_one['group'])
        for seed_one in keep_list:
            if 'group' in seed_one and seed_one['group'] in ['Media', 'Cabinet']:
                group_have.append(seed_one['group'])
        furniture_list, decorate_list = [], []
        for list_one in [seed_list, keep_list, plus_list]:
            for furniture_one in list_one:
                if 'group' in furniture_one and furniture_one['group'] in group_have:
                    furniture_add = copy_object(furniture_one)
                    furniture_add['group'] = ''
                    furniture_add['role'] = ''
                    furniture_add['count'] = 1
                    furniture_add['relate'] = ''
                    furniture_add['relate_role'] = ''
                    furniture_list.append(furniture_add)
        group_functional, group_decorative = extract_furniture_group(furniture_list, decorate_list,
                                                                     room_type, room_mirror, 0, False)
    # 补齐打组
    else:
        group_functional, group_decorative = [], []
    # 整理打组
    seed_used = {}
    for group_idx in range(len(group_functional) - 1, -1, -1):
        group_one = group_functional[group_idx]
        group_type, group_code = group_one['type'], group_one['code']
        if group_type == 'Dining' and group_code <= 120:
            group_functional.pop(group_idx)
            continue
        # 种子信息
        object_id = group_one['obj_main']
        seed_id = object_id
        if group_type == 'Media':
            for object_one in group_one['obj_list']:
                if object_one['role'] == 'table':
                    seed_id = object_one['id']
                    break
        seed_used[seed_id] = 1
    for seed_one in seed_list:
        seed_id, seed_type = seed_one['id'], seed_one['type']
        seed_size = [seed_one['size'][i] * seed_one['scale'][i] / 100 for i in range(3)]
        seed_group, seed_role = seed_one['group'], seed_one['role']
        if seed_id in seed_used:
            continue
        group_add = create_room_origin(seed_type, seed_size, seed_group, seed_role)
        if len(group_add) > 0:
            group_functional.append(group_add)

    # 构造布局
    room_layout_list_old = search_room_sample(room_type, room_area, seed_list, keep_list, plus_list, sample_num)
    room_group_list_list = []
    for layout_old in room_layout_list_old:
        room_group_list_one = []
        for group_old in layout_old['group']:
            group_find = False
            for group_new in group_functional:
                if group_new['type'] == group_old['type']:
                    group_find = True
                    break
            if not group_find:
                source_house, source_room = layout_old['source_house'], layout_old['source_room']
                group_type, group_main, group_size = group_old['type'], group_old['obj_main'], group_old['size']
                group_detail = get_furniture_group(source_house, source_room, group_type, group_main, group_size)
                group_detail_add = copy_group(group_detail)
                room_group_list_one.append(group_detail_add)
        room_group_list_list.append(room_group_list_one)
    # 构造布局
    room_layout_list_new = []
    for sample_idx in range(sample_num):
        # 单屋布局
        room_layout_one = {
            'code': 0,
            'score': 0,
            'type': 0,
            'style': '',
            'area': 0,
            'material': {},
            'decorate': {},
            'group': [],
            'group_area': 0,
            'source_house': '',
            'source_room': '',
            'source_room_area': 0
        }
        # 整理打组
        style_main, count_list, group_area, group_list = '', [0, 0, 0], 0, []
        for group_one in group_functional:
            group_list.append(group_one)
        for group_one in room_group_list_list[sample_idx % len(room_group_list_list)]:
            group_list.append(group_one)
        for group_idx, group_one in enumerate(group_list):
            # 矩形信息
            group_size, group_offset, furniture_rect = rect_group(group_one)
            # 主要家具 位置旋转
            group_position = group_one['position'][:]
            group_rotation = group_one['rotation'][:]
            object_id = group_one['obj_list'][0]['id']
            object_type = group_one['obj_list'][0]['type']
            object_size = group_one['obj_list'][0]['size']
            object_scale = group_one['obj_list'][0]['scale']
            group_size_object = []
            for size_idx, size_one in enumerate(object_size):
                group_size_object.append(abs(object_size[size_idx] * object_scale[size_idx] / 100))
            # 剩余信息
            width_rest1 = group_offset[0] - group_size_object[0] / 2 + group_size[0] / 2
            width_rest2 = group_size[0] / 2 - group_offset[0] - group_size_object[0] / 2
            depth_rest1 = group_offset[2] - group_size_object[2] / 2 + group_size[2] / 2
            depth_rest2 = group_size[2] / 2 - group_offset[2] - group_size_object[2] / 2
            # 分组信息
            group_add = {
                'type': group_one['type'],
                'code': group_one['code'],
                'size': group_size,
                'offset': group_offset,
                'position': group_position,
                'rotation': group_rotation,
                'size_min': group_size_object,
                'size_rest': [depth_rest1, width_rest1, depth_rest2, width_rest2],
                'obj_main': object_id,
                'obj_type': object_type,
                'obj_list': [],
                'relate': '',
                'relate_role': '',
                'relate_position': []
            }
            room_layout_one['group'].append(group_add)
            group_area += group_size[0] * group_size[2]

            # 风格信息
            if style_main == '':
                style_main = group_one['style']
            elif group_one['type'] == 'Meeting' or group_one['type'] == 'Bed':
                style_main = group_one['style']
            # 数量信息
            count_list[0] += 1
            accessory_count = int(group_one['code']) % 10
            furniture_count = len(group_one['obj_list']) - accessory_count
            count_list[1] += furniture_count
            count_list[2] += accessory_count
        # 更新布局
        room_layout_one['code'] = count_list[0] * 10000 + count_list[1] * 100 + count_list[2]
        room_layout_one['type'] = room_type
        room_layout_one['area'] = room_area
        room_layout_one['style'] = style_main
        room_layout_one['group_area'] = group_area
        if room_area < group_area:
            room_layout_one['area'] = group_area * 1.5
        source_house, source_room = 'scheme_house_%d' % sample_idx, 'scheme_room_%d' % sample_idx
        room_layout_one['source_house'] = source_house
        room_layout_one['source_room'] = source_room
        # 清除
        del_furniture_group(source_house, source_room)
        # 添加
        for group_one in group_list:
            add_furniture_group(source_house, source_room, group_one)
        room_layout_list_new.append(room_layout_one)

    # 返回信息
    return room_layout_list_new


# 数据检索
def create_room_origin(seed_type, seed_size, seed_group, seed_role, room_type=''):
    group_detail = {}
    if seed_group == 'Media':
        group_detail = get_default_group('media')
    elif seed_group == 'Dining':
        # 组合
        if seed_type in ['table/dining set', 'table/dinning set']:
            group_detail = get_default_group('dining set')
        # 圆桌
        elif seed_type == 'table/dining table - round':
            group_detail = get_default_group('dining round')
        # 方桌
        else:
            group_detail = get_default_group('dining')
    # 补充桌子
    elif seed_group == 'Work':
        group_detail = get_default_group('table work')
    elif seed_group == 'Rest':
        group_detail = get_default_group('table rest')
    # 补充衣柜
    elif seed_group == 'Armoire':
        group_detail = get_default_group('cabinet armoire')
    # 补充柜体 餐柜 书柜 矮柜 衣柜
    elif seed_group == 'Cabinet':
        if room_type in ['DiningRoom']:
            group_detail = get_default_group('cabinet dining')
        elif room_type in ['Library']:
            group_detail = get_default_group('cabinet book')
        elif seed_size[1] < UNIT_HEIGHT_ARMOIRE_MIN:
            group_detail = get_default_group('cabinet short')
        else:
            group_detail = get_default_group('cabinet armoire')
    return group_detail


# 数据清除
def delete_room_origin():
    pass


# 数据更新：家具更新
def refresh_house_object(src_oss, des_dir='', obj_ext='.obj'):
    if src_oss == '':
        return
    house_list = list_house_oss(src_oss)
    if len(house_list) <= 0:
        return
    for house_id in house_list:
        # 数据标识
        house_id = os.path.basename(house_id)
        if house_id.endswith('.json'):
            house_id = house_id[:-5]
        # 加载数据
        temp_dir = DATA_DIR_HOUSE_SAMPLE
        if not os.path.exists(temp_dir):
            temp_dir = os.path.dirname(__file__) + '/temp/'
        download_house(house_id, temp_dir)
        house_path = os.path.join(temp_dir, house_id + '.json')
        if not os.path.exists(house_path):
            continue
        # 解析数据
        house_json = json.load(open(house_path, 'r', encoding='utf-8'))
        # 全部家具
        furniture_dict = {}
        for furniture_one in house_json['furniture']:
            furniture_uid, furniture_jid = furniture_one['uid'], furniture_one['jid']
            furniture_dict[furniture_uid] = furniture_jid
        # 遍历房间
        for room_json in house_json['scene']['room']:
            # 房间信息
            room_id, room_type = room_json['instanceid'], room_json['type']
            if room_type not in ROOM_TYPE_MAIN:
                continue
            # 家具信息
            for child_one in room_json['children']:
                child_ref = child_one['ref']
                if child_ref not in furniture_dict:
                    continue
                obj_id = furniture_dict[child_ref]
                if des_dir == '':
                    des_dir = DATA_DIR_FURNITURE
                if not os.path.exists(des_dir):
                    os.makedirs(des_dir)
                obj_file = obj_id + obj_ext
                obj_path = os.path.join(des_dir, obj_file)
                # 居然下载
                if obj_ext == '.obj':
                    download_obj(obj_id, des_dir, True)
                elif obj_ext == '.json':
                    download_json(obj_id, des_dir)
                elif obj_ext == '.jpg':
                    temp_dir = DATA_DIR_FURNITURE
                    if not os.path.exists(temp_dir):
                        temp_dir = os.path.dirname(__file__) + '/temp/'
                    download_json(obj_id, temp_dir, True)
                    download_img(obj_id, temp_dir, des_dir)
                # 上传数据
                if os.path.exists(obj_path):
                    oss_upload_file(obj_file, obj_path, DATA_OSS_FURNITURE)


# 数据更新：布局更新
def refresh_house_layout(src_oss):
    if src_oss == '':
        return
    house_list = list_house_oss(src_oss)
    if len(house_list) <= 0:
        return
    # 清空布局
    clear_group_layout()
    # 遍历户型
    for house_idx, house_id in enumerate(house_list):
        print('house sample %03d:' % house_idx, house_id)
        print_flag = False
        del_sample_layout(house_id, '')
        # 提取布局
        house_data_info, house_layout_info, house_group_info = \
            extract_house_layout(house_id, auto_add=1, check_mode=2, print_flag=print_flag)
        # 添加布局
        for room_id, room_group in house_group_info.items():
            for group_info in room_group['group_functional']:
                group_type = group_info['type']
                if group_type not in ['Meeting', 'Bed', 'Dining', 'Work', 'Rest']:
                    continue
                layout_info = parse_group_layout(group_info)
                add_group_layout(layout_info)
    print()
    save_house_sample()
    save_furniture_group()
    save_group_layout()


# 数据更新：
def refresh_design_layout(house_list, auto_add=0):
    # 遍历户型
    for house_idx, house_key in enumerate(house_list):
        print('house sample %03d:' % house_idx, house_key)
        print_flag = False
        del_sample_layout(house_key, '')
        # 提取布局
        house_data_info, house_layout_info, house_group_info = \
            extract_house_layout_by_design(house_key, check_mode=2, print_flag=print_flag)
        replace_house_layout(house_layout_info, house_group_info, house_key, auto_add)
        # 添加布局
        for room_id, room_group in house_group_info.items():
            for group_info in room_group['group_functional']:
                group_type = group_info['type']
                if group_type not in ['Meeting', 'Bed', 'Dining', 'Work', 'Rest']:
                    continue
                layout_info = parse_group_layout(group_info)
                add_group_layout(layout_info)
    # 保存数据
    if len(house_list) > 0:
        print()
        save_house_sample()
        save_furniture_group()
        save_group_layout()


# 数据导出：户型数据
def export_house_data(des_dir=DATA_DIR_HOUSE_SCHEME, src_oss=DATA_OSS_HOUSE_EMPTY, index=0, number=10):
    # 批量提取
    house_list = list_house_oss(src_oss, index, number)
    if len(house_list) > 0:
        print()
    # 遍历户型
    for house_idx, house_id in enumerate(house_list):
        print('house data export %03d:' % house_idx, house_id)
        house_data_info, house_layout_info, house_group_info = extract_house_layout(house_id)
        # 保存布局
        save_id = house_id
        save_dir = des_dir
        if save_dir == '':
            save_dir = DATA_DIR_HOUSE_SCHEME
        save_mode = [SAVE_MODE_DATA]
        house_save(house_id, '', 0, 0,
                   house_data_info, house_layout_info, {},
                   save_id, save_dir, save_mode, suffix_flag=False, sample_flag=False, upload_flag=False)


# 数据导出：户型图像
def export_house_image(des_dir=DATA_DIR_HOUSE_IMAGE, src_oss=DATA_OSS_HOUSE_EMPTY, index=0, number=10, layout=True):
    # 批量绘制
    house_list = list_house_oss(src_oss, index, number)
    if len(house_list) > 0:
        print()
    # 遍历户型
    for house_idx, house_id in enumerate(house_list):
        print('house image export %03d:' % house_idx, house_id)
        house_data_info, house_layout_info, house_group_info = extract_house_layout(house_id)
        # 保存布局
        save_id = house_id
        save_dir = des_dir
        if save_dir == '':
            save_dir = DATA_DIR_HOUSE_IMAGE
        save_mode = [SAVE_MODE_IMAGE]
        if not layout:
            house_layout_info = {}
        house_save(house_id, '', 0, 0,
                   house_data_info, house_layout_info, {},
                   save_id, save_dir, save_mode, suffix_flag=False, sample_flag=True)


# 数据生成：模拟推荐
def generate_furniture_propose(propose_one, scheme_num=3):
    propose_one['target_furniture'] = []
    propose_one['target_furniture_size'] = {}
    # 推荐信息
    room_type, target_scope = propose_one['type'], propose_one['target_scope']
    if 'Bathroom' in room_type:
        room_type = 'Bathroom'
    elif 'Bedroom' in room_type or room_type in ['ElderlyRoom', 'NannyRoom']:
        room_type = 'Bedroom'
    room_style, style_list, style_fine = '', [], 0
    if 'target_style' in propose_one and len(propose_one['target_style']) > 0:
        style_id = propose_one['target_style'][0]
        room_style = get_furniture_style_by_id(style_id)
        room_style = get_furniture_style_en(room_style)
    if not room_style == '':
        style_list = get_furniture_style_refer_en(room_style)
    # 遍历房间
    room_todo = []
    global FURNITURE_GROUP_DICT
    load_furniture_group()
    for house_id, house_info in FURNITURE_GROUP_DICT.items():
        for room_id, group_list in house_info.items():
            if room_type not in room_id:
                continue
            style_find = False
            for group_one in group_list:
                group_style = group_one['style']
                if group_style in style_list:
                    style_find = True
                    break
            if style_find:
                room_todo.insert(0, group_list)
            else:
                room_todo.append(group_list)
    # 遍历组合
    propose_todo, propose_good, propose_size = [], [], {}
    for group_list in room_todo:
        replace_dict, replace_good = {}, 0
        for target_idx, target_one in enumerate(target_scope):
            target_id, target_role, target_type = target_one['id'], target_one['role'], target_one['type']
            size_min, size_max, size_cur = target_one['size_min'], target_one['size_max'], target_one['size_cur']
            size_dict = {}
            # 内部查找
            for group_one in group_list:
                for object_one in group_one['obj_list']:
                    object_id, object_role, object_type = object_one['id'], object_one['role'], object_one['type']
                    object_size = object_one['size']
                    if object_type == target_type:
                        size_dict[object_id] = object_size
                    elif object_role == target_role and object_role not in ['accessory', '']:
                        if object_role == 'table':
                            if object_type.startswith('table') and not target_type.startswith('table'):
                                continue
                            if target_type.startswith('table') and not object_type.startswith('table'):
                                continue
                        elif object_role == 'cabinet' and group_one['type'] in ['Wall']:
                            continue
                        size_dict[object_id] = object_size
            # 内部比较
            replace_id_best, replace_size_best, replace_diff_best = target_id, size_cur, 500
            if target_role == 'cabinet':
                replace_id_best = ''
            for replace_id_one, replace_size_one in size_dict.items():
                replace_diff = abs(replace_size_one[0] - size_cur[0]) + abs(replace_size_one[1] - size_cur[1]) + \
                               abs(replace_size_one[2] - size_cur[2])
                if replace_diff <= replace_diff_best:
                    replace_id_best = replace_id_one
                    replace_size_best = replace_size_one
                    replace_diff_best = replace_diff
            # 替换信息 ID 尺寸 分数
            replace_dict[target_id] = replace_id_best
            propose_size[replace_id_best] = replace_size_best
            if len(size_dict) > 0:
                replace_good += 1
            if replace_size_best[0] > size_max[0] and replace_size_best[2] > size_max[2]:
                replace_good -= 1
        # 推荐排序
        find_idx = -1
        for good_idx, good_one in enumerate(propose_good):
            if good_one < replace_good:
                find_idx = good_idx
                break
        if 0 <= find_idx < len(propose_good):
            propose_todo.insert(find_idx, replace_dict)
            propose_good.insert(find_idx, replace_good)
        else:
            propose_todo.append(replace_dict)
            propose_good.append(replace_good)
        if (len(propose_todo) > scheme_num and len(propose_todo) >= 10) or len(propose_todo) >= scheme_num * 2:
            break
    for i in range(scheme_num):
        replace_dict = propose_todo[i % len(propose_todo)]
        for replace_id in replace_dict.values():
            if replace_id in propose_size:
                replace_size = propose_size[replace_id]
                propose_one['target_furniture_size'][replace_id] = replace_size
        propose_one['target_furniture'].append(replace_dict)


# 数据生成：模拟替换
def generate_furniture_replace(house_id):
    replace_info = {}
    # 户型解析
    house_path = download_house(house_id, DATA_DIR_HOUSE_EMPTY)
    if not os.path.exists(house_path):
        return replace_info
    house_json = json.load(open(house_path, 'r', encoding='utf-8'))
    # 家具信息
    furniture_dict = {}
    for furniture_one in house_json['furniture']:
        furniture_uid, furniture_jid = furniture_one['uid'], furniture_one['jid']
        furniture_dict[furniture_uid] = furniture_jid
    # 布局信息
    for room_json in house_json['scene']['room']:
        room_id, room_type = room_json['instanceid'], room_json['type']
        if room_type not in ROOM_TYPE_MAIN:
            continue
        # 家具列表
        furniture_list = []
        for child_one in room_json['children']:
            child_ref = child_one['ref']
            if child_ref in furniture_dict:
                # 家具信息
                furniture_info = {}
                furniture_id = furniture_dict[child_ref]
                furniture_info['id'] = furniture_id
                furniture_type, furniture_style, furniture_size = get_furniture_data(furniture_id)
                if furniture_type == '':
                    continue
                furniture_info['type'] = furniture_type
                furniture_info['style'] = furniture_style
                furniture_info['size'] = furniture_size
                furniture_info['scale'] = child_one['scale']
                # 家具位置
                furniture_info['position'] = child_one['pos']
                furniture_info['rotation'] = child_one['rot']
                # 家具关联
                furniture_info['group'] = ''
                furniture_info['role'] = ''
                furniture_info['count'] = 1
                furniture_info['relate'] = ''
                furniture_info['relate_role'] = ''
                # 数据记录
                furniture_list.append(furniture_info)
        # 替换列表
        replace_soft = []
        for object_one in furniture_list:
            object_id = object_one['id']
            object_type, object_style = object_one['type'], object_one['style']
            object_size, object_scale = object_one['size'], object_one['scale']
            object_size_now = [abs(object_size[i] * object_scale[i]) / 100 for i in range(3)]
            if object_type == '':
                continue
            object_cate_id = ''
            object_group, object_role = compute_furniture_role(object_type, object_size_now, room_type, object_id, object_cate_id)
            if object_group == '':
                continue
            if object_role in ['', 'tv', 'rug', 'accessory']:
                continue
            # 替换信息
            like_list = compute_furniture_like(object_group, object_role)
            if len(like_list) >= 2:
                like_idx = random.randint(0, len(like_list) - 1)
                like_one = like_list[like_idx]
                if like_one == object_one['id']:
                    like_idx = (like_idx + 2) % len(like_list)
                    like_one = like_list[like_idx]
                replace_soft.append(like_one)
            if len(replace_soft) >= 2:
                break
        replace_info[room_id] = {'soft': replace_soft}
    # 替换信息
    return replace_info


# 数据加载
load_house_sample()


# 功能测试
if __name__ == '__main__':
    # 本地提取
    house_id = '0d8edd78-6d9b-46c3-b3c9-296d17273da3'
    house_id = '4de5a8c0-9b0a-4ed4-a561-fbb7b96122bf'
    house_id = 'a2e4a324-07b1-42bc-be2e-91bfc5f76564'
    house_id = '1b8d20f5-c51e-40db-88e1-2d782e8321c0'
    house_id = 'a2e4a324-07b1-42bc-be2e-91bfc5f76564'
    house_path = os.path.join(DATA_DIR_HOUSE_INPUT, house_id + '.json')
    house_data_info, house_layout_info, house_group_info = extract_house_layout_by_path(house_path)

    # 批量提取
    # refresh_house_layout(DATA_OSS_HOUSE_FINE)
    pass
    house_list = ['1b8d20f5-c51e-40db-88e1-2d782e8321c0']
    refresh_design_layout(house_list, auto_add=1)
    pass

    # 更新家具
    # refresh_house_object(DATA_OSS_HOUSE_FINE)
    pass

    # 纠正提取
    house_id = '355ab8b3-1609-4346-8202-1546938d57f2'
    house_data_info, house_layout_info, house_group_info = extract_house_layout(house_id, auto_add=1, check_mode=1)

    pass

    # 户型数据
    export_house_data(des_dir=DATA_DIR_HOUSE_SCHEME, src_oss=DATA_OSS_HOUSE_FINE, index=0, number=20)
    pass
    # 户型图片
    export_house_image(des_dir=DATA_DIR_HOUSE_IMAGE, src_oss=DATA_OSS_HOUSE_FINE, index=0, number=20, layout=True)
    pass

    # 数据更新
    # save_furniture_data()
    pass

