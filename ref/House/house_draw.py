# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-10
@Description: 绘制户型、功能区域、家具数据

"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
plt.switch_backend('agg')

from House.house import *
from Furniture.furniture_group import *
from Furniture.furniture_refer import *

DATA_DIR_HOUSE_IMAGE = os.path.dirname(__file__) + '/temp/picture/'
if not os.path.exists(DATA_DIR_HOUSE_IMAGE):
    os.makedirs(DATA_DIR_HOUSE_IMAGE)

# 房间绘制列表
DRAW_ROOM_LIST = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                  'MasterBedroom', 'SecondBedroom', 'Bedroom',
                  'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                  'Library',
                  'Kitchen',
                  'MasterBathroom', 'SecondBathroom', 'Bathroom',
                  'Balcony', 'Terrace', 'Lounge', 'Auditorium',
                  'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                  'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom',
                  'Courtyard', 'Garage',
                  'undefined', 'none']

# 房间绘制参数
DRAW_ROOM_PARAM = {
    'LivingDiningRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'LivingRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'DiningRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'MasterBedroom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'SecondBedroom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Bedroom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'KidsRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'ElderlyRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'NannyRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Library': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'MasterBathroom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'SecondBathroom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Bathroom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Kitchen': {
            'line_color': (0, 0, 0, 1),
            'line_style': '-',
            'line_width': 1,
            'fill': False,
            'face_color': None
        },
    'Balcony': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Terrace': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Lounge': {
            'line_color': (0, 0, 0, 1),
            'line_style': '-',
            'line_width': 1,
            'fill': False,
            'face_color': None
        },
    'LaundryRoom': {
            'line_color': (0, 0, 0, 1),
            'line_style': '-',
            'line_width': 1,
            'fill': False,
            'face_color': None
        },
    'Hallway': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Aisle': {
            'line_color': (0, 0, 0, 1),
            'line_style': '-',
            'line_width': 1,
            'fill': False,
            'face_color': None
        },
    'Corridor': {
            'line_color': (0, 0, 0, 1),
            'line_style': '-',
            'line_width': 1,
            'fill': False,
            'face_color': None
        },
    'Stairwell': {
            'line_color': (0, 0, 0, 1),
            'line_style': '-',
            'line_width': 1,
            'fill': False,
            'face_color': None
        },
    'StorageRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'CloakRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'EquipmentRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Auditorium': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'OtherRoom': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Default': {
        'line_color': (0.8, 0.8, 0.8, 0.1),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    }
}
# 部件绘制参数 部件包括：门窗洞、主门、飘窗、地面，其中地面根据房间类型绘制参数
DRAW_UNIT_PARAM = {
    'maindoor': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'floor': {
        'line_color': (0, 0, 0, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'door': {
        'line_color': (0.4, 0.4, 0.4, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'hole': {
        'line_color': (0.4, 0.4, 0.4, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'window': {
        'line_color': (0.8, 0.8, 0.8, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'baywindow': {
        'line_color': (0.8, 0.8, 0.8, 1),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    }
}
# 硬装绘制参数 部件包括：背景墙、吊顶、柜体
DRAW_MESH_PARAM = {
    'background': {
        'line_color': (0, 0, 0, 0.2),
        'line_style': '--',
        'line_width': 2,
        'fill': True,
        'face_color': None
    },
    'ceiling': {
        'line_color': (0, 0, 0, 0),
        'line_style': '--',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'cabinet': {
        'line_color': (0, 0, 0, 0.2),
        'line_style': '--',
        'line_width': 1,
        'fill': True,
        'face_color': None
    }
}
# 分组绘制参数
DRAW_GROUP_PARAM = {
    'Meeting': {
        'line_color': (0, 0, 1, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Media': {
        'line_color': (0, 1, 1, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Dining': {
        'line_color': (1, 0, 1, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Bed': {
        'line_color': (0, 0, 1, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Armoire': {
        'line_color': (1, 0.5, 0, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Cabinet': {
        'line_color': (1, 0.5, 0, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Work': {
        'line_color': (1, 0, 1, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Rest': {
        'line_color': (1, 0, 1, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Bath': {
        'line_color': (0, 0, 1, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Toilet': {
        'line_color': (1, 0, 1, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Default': {
        'line_color': (0, 0, 0, 0.5),
        'line_style': '-',
        'line_width': 1,
        'fill': False,
        'face_color': None
    }
}
# 家具绘制参数
DRAW_FURNITURE_PARAM = {
    'Default': {
        'line_color': (0, 0, 0, 1),
        'line_style': '--',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Wall': {
        'line_color': (0, 0, 0, 1),
        'line_style': '--',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Floor': {
        'line_color': (0, 0, 0, 1),
        'line_style': '--',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Ceiling': {
        'line_color': (0, 0, 0, 1),
        'line_style': '--',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Door': {
        'line_color': (0, 0, 0, 1),
        'line_style': '--',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Window': {
        'line_color': (0, 0, 0, 1),
        'line_style': '--',
        'line_width': 1,
        'fill': False,
        'face_color': None
    },
    'Background': {
        'line_color': (0, 0, 0, 1),
        'line_style': '--',
        'line_width': 1,
        'fill': False,
        'face_color': None
    }
}
# 矩形绘制参数
DRAW_RECT_PARAM = {
    'Default': {
        'line_color': (1, 0.5, 0, 1.0),
        'line_style': '--',
        'line_width': 1,
        'fill': True,
        'face_color': None
    },
    'Group': {
        'line_color': (0.5, 0.5, 0.5, 1.0),
        'line_style': '--',
        'line_width': 1,
        'fill': True,
        'face_color': None
    }
}
# 机位绘制参数
DRAW_CAMERA_PARAM = {
    'Default': {
        'line_color': (0, 0, 0, 1.0),
        'line_style': '--',
        'line_width': 2,
        'fill': False,
        'face_color': None
    }
}

# 标签字体大小
FONT_SIZE_ROOM = 16
FONT_SIZE_GROUP = 18
FONT_SIZE_FURNITURE = 12
# 画布尺寸大小
FIGURE_X = 20
FIGURE_Z = 20


# 绘制户型
def draw_house(house_id, image_path='', room_to_draw=[], room_label=False, draw_label=False):
    """

    :param house_id: 户型ID或样板间ID
    :param image_path: 图片路径
    :param room_to_draw: 绘制房间，默认全部类型房间
    :param draw_label: 是否绘制标签
    :return:
    """
    if house_id == '':
        return
    id_new, data_info, feature_info = get_house_data_feature(house_id)
    draw_house_info(data_info, image_path, room_to_draw, room_label, draw_label)


# 绘制户型
def draw_house_info(data_info, image_path='', room_to_draw=[], room_label=False):
    if len(data_info) <= 0:
        return
    # 补充参数
    if len(room_to_draw) == 0:
        room_to_draw = DRAW_ROOM_LIST
    # 创建图像
    if image_path == '':
        image_path = os.path.join(DATA_DIR_HOUSE_IMAGE, 'test_house_00_00.png')
    # 全屋尺寸
    room_dict_box = {}
    for room_info in data_info['room']:
        room_type = room_info['type']
        if room_type not in room_to_draw:
            continue
        # 房间大小
        floor = room_info['floor']
        floor_len = int(len(floor) / 2)
        if floor_len < 1:
            continue
        x_max = x_min = floor[0]
        y_max = y_min = floor[1]
        for i in range(floor_len):
            # 起点终点
            x = floor[2 * i + 0]
            y = floor[2 * i + 1]
            if x_max < x:
                x_max = x
            if x_min > x:
                x_min = x
            if y_max < y:
                y_max = y
            if y_min > y:
                y_min = y
        room_dict_box[room_info['id']] = [x_min, y_min, x_max, y_max]
    # 全屋尺寸
    house_box = [0, 0, 0, 0]
    for room_box in room_dict_box.values():
        if house_box[0] > room_box[0]:
            house_box[0] = room_box[0]
        if house_box[1] > room_box[1]:
            house_box[1] = room_box[1]
        if house_box[2] < room_box[2]:
            house_box[2] = room_box[2]
        if house_box[3] < room_box[3]:
            house_box[3] = room_box[3]
    if len(room_dict_box) < len(data_info['room']) / 2:
        house_box[0] = min(house_box[0], -5)
        house_box[1] = min(house_box[1], -5)
        house_box[2] = max(house_box[2], 5)
        house_box[3] = max(house_box[3], 5)
    # 画布尺寸
    figure_width = house_box[2] - house_box[0] + 1
    figure_height = house_box[3] - house_box[1] + 1
    figure = plt.figure(figsize=[FIGURE_X, FIGURE_Z * figure_height / figure_width])
    plt.xlim((house_box[0] - 0.5, house_box[2] + 0.5))
    plt.ylim((house_box[3] + 0.5, house_box[1] - 0.5))
    font_room = FONT_SIZE_ROOM
    if figure_height > figure_width:
        font_room = int(FONT_SIZE_ROOM * figure_height / figure_width)

    # 绘制房间
    room_list, room_dict = [], {}
    if 'room' in data_info:
        room_list = data_info['room']
    for room_info in room_list:
        if room_info['type'] not in room_to_draw:
            continue
        room_dict[room_info['id']] = room_info
        room_style, room_score = '', ''
        draw_room(room_info, [], font_room, room_label)

    # 保存图像
    plt.close(figure)
    figure.savefig(image_path, dpi=90)


# 绘制布局
def draw_house_layout(data_info, layout_info, rect_info={}, image_path='', room_to_draw=[], group_to_draw=[],
                      room_label=False, draw_label=False, draw_arrow=False, draw_detail=2):
    draw_house_layout_index(data_info, layout_info, rect_info, image_path, 0, -1, room_to_draw, group_to_draw,
                            room_label, draw_label, draw_arrow, draw_detail)


# 绘制布局
def draw_house_layout_index(data_info, layout_info, rect_info={}, image_path='', scheme_index=0, propose_index=-1,
                            room_to_draw=[], group_to_draw=[],
                            room_label=False, draw_label=False, draw_arrow=False, draw_detail=2):
    """

    :param data_info:
    :param layout_info:
    :param rect_info:
    :param image_path: 图片路径
    :param room_to_draw: 绘制房间，默认全部类型房间
    :param group_to_draw: 绘制分组
    :param draw_label: 是否绘制标签
    :param draw_arrow: 是否绘制箭头
    :param draw_detail: 1仅绘制分组包围盒 2仅绘制家具包围盒 3绘制全部包围盒
    :return:
    """
    # 补充参数
    if len(room_to_draw) == 0:
        room_to_draw = DRAW_ROOM_LIST
    house_id = ''
    if 'id' in data_info:
        house_id = data_info['id']
    # 创建图像
    if image_path == '':
        image_path = os.path.join(DATA_DIR_HOUSE_IMAGE, house_id + '_%02d_00.png' % scheme_index)
        if len(rect_info) > 0:
            image_path = os.path.join(DATA_DIR_HOUSE_IMAGE, house_id + '_rect_%02d_00.png' % scheme_index)
    # 全屋尺寸
    room_dict_box = {}
    if 'room' not in data_info:
        return
    for room_data in data_info['room']:
        room_key, room_type = '', ''
        if 'id' in room_data:
            room_key = room_data['id']
        if 'type' in room_data:
            room_type = room_data['type']
        if room_type == '':
            pass
        elif room_type not in room_to_draw:
            continue
        # 房间大小
        floor = []
        if 'floor' in room_data:
            floor = room_data['floor']
        else:
            floor = [-5, -5, -5, 5, 5, -5, 5, 5]
            if 'area' not in room_data:
                room_data['area'] = 100
            if room_key in layout_info:
                room_layout = layout_info[room_key]
                if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
                    room_scheme = room_layout['layout_scheme'][0]
                    if 'group' in room_scheme and len(room_scheme['group']) > 0:
                        room_group = room_scheme['group'][0]
                        if 'position' in room_group and len(room_group['position']) >= 3:
                            group_x, group_z = room_group['position'][0], room_group['position'][2]
                            floor = [group_x-5, group_z-5, group_x-5, group_z+5,
                                     group_x+5, group_z-5, group_x+5, group_z+5]
        floor_len = int(len(floor) / 2)
        if floor_len < 1:
            continue
        x_max = x_min = floor[0]
        y_max = y_min = floor[1]
        for i in range(floor_len):
            # 起点终点
            x = floor[2 * i + 0]
            y = floor[2 * i + 1]
            if x_max < x:
                x_max = x
            if x_min > x:
                x_min = x
            if y_max < y:
                y_max = y
            if y_min > y:
                y_min = y
        room_dict_box[room_data['id']] = [x_min, y_min, x_max, y_max]
    if len(room_dict_box) <= 0:
        return
    # 全屋尺寸
    house_box = []
    for room_key, room_box in room_dict_box.items():
        if len(house_box) <= 0:
            house_box = room_box[:]
            continue
        if house_box[0] > room_box[0]:
            house_box[0] = room_box[0]
        if house_box[1] > room_box[1]:
            house_box[1] = room_box[1]
        if house_box[2] < room_box[2]:
            house_box[2] = room_box[2]
        if house_box[3] < room_box[3]:
            house_box[3] = room_box[3]
    if len(room_dict_box) < len(data_info['room']) / 2:
        house_box[0] = min(house_box[0], -5)
        house_box[1] = min(house_box[1], -5)
        house_box[2] = max(house_box[2], 5)
        house_box[3] = max(house_box[3], 5)
    # 画布尺寸 TODO:
    figure_width = house_box[2] - house_box[0] + 1
    figure_height = house_box[3] - house_box[1] + 1
    # 画布铺满
    figure_fill = False
    if figure_fill:
        figure = plt.figure(figsize=[FIGURE_X, FIGURE_Z * figure_height / figure_width])
        plt.xlim((house_box[0] - 0.5, house_box[2] + 0.5))
        plt.ylim((house_box[3] + 0.5, house_box[1] - 0.5))
        font_room, font_group, font_furniture = FONT_SIZE_ROOM, FONT_SIZE_GROUP, FONT_SIZE_FURNITURE
        if figure_height > figure_width:
            font_room = int(FONT_SIZE_ROOM * figure_height / figure_width)
            font_group = int(FONT_SIZE_GROUP * figure_height / figure_width)
            font_furniture = int(FONT_SIZE_FURNITURE * figure_height / figure_width)
    # 画布平均
    else:
        figure = plt.figure(figsize=[FIGURE_X, FIGURE_Z])
        plt.xlim((-10, 10))
        plt.ylim((10, -10))
        font_room, font_group, font_furniture = FONT_SIZE_ROOM, FONT_SIZE_GROUP, FONT_SIZE_FURNITURE

    # 绘制房间
    room_list, room_dict = [], {}
    if 'room' in data_info:
        room_list = data_info['room']
    for room_data in room_list:
        room_id = room_data['id']
        room_type = room_data['type']
        if room_type == '':
            pass
        elif room_type not in room_to_draw:
            continue
        room_dict[room_id] = room_data
        # 绘制房间
        room_style, room_score = '', ''
        if room_id in layout_info:
            room_layout_one = layout_info[room_id]
            if 'layout_scheme' in room_layout_one and len(room_layout_one['layout_scheme']) > 0:
                layout_one = room_layout_one['layout_scheme'][0]
                if 'style' in layout_one:
                    room_style = get_furniture_style_en(layout_one['style'])
                if 'score' in layout_one:
                    room_score = str(round(float(layout_one['score']), 1))
        draw_room(room_data, [], font_room, room_label, room_style, room_score)
    # 绘制硬装
    for room_key, room_layout in layout_info.items():
        deco_list = []
        if 'layout_mesh' in room_layout:
            deco_list = room_layout['layout_mesh']
        draw_room_mesh(deco_list)
    # 绘制分组
    if len(group_to_draw) > 0 and len(layout_info) > 0:
        # 遍历房间
        for room_key, room_layout in layout_info.items():
            # 种子信息
            seed_dict = {}
            if 'layout_seed' in room_layout:
                for seed_one in room_layout['layout_seed']:
                    seed_dict[seed_one['id']] = 1
            if 'layout_keep' in room_layout:
                for seed_one in room_layout['layout_keep']:
                    seed_dict[seed_one['id']] = 1
            # 遍历方案
            if 'layout_scheme' not in room_layout:
                continue
            if len(room_layout['layout_scheme']) <= 0:
                continue
            layout_index_new = scheme_index % len(room_layout['layout_scheme'])
            room_type, room_layout_one = room_layout['room_type'], room_layout['layout_scheme'][layout_index_new]
            if room_type not in room_to_draw:
                continue
            # 分组信息
            group_list = room_layout_one['group']
            if propose_index >= 0 and 'group_propose' in room_layout_one and len(room_layout_one['group_propose']) > 0:
                propose_index_new = propose_index % len(room_layout_one['group_propose'])
                group_list = room_layout_one['group_propose'][propose_index_new]
            # 遍历分组
            group_obj_sum = 0
            for group_idx, group_one in enumerate(group_list):
                group_type, group_obj_list = group_one['type'], []
                if 'obj_list' in group_one:
                    group_obj_list = group_one['obj_list']
                if group_type in GROUP_RULE_FUNCTIONAL:
                    group_obj_sum += len(group_obj_list)
            for group_idx, group_one in enumerate(group_list):
                group_type = group_one['type']
                if group_type not in group_to_draw:
                    continue
                if group_type in GROUP_RULE_FUNCTIONAL and group_obj_sum <= 0:
                    draw_room_group(group_one, seed_dict, draw_label, font_group, draw_arrow)
                elif draw_detail == 1:
                    draw_room_group(group_one, seed_dict, draw_label, font_group, draw_arrow)
                elif draw_detail == 2:
                    draw_room_furniture(group_one, seed_dict, draw_label, font_furniture, draw_arrow)
                elif draw_detail == 3:
                    # draw_room_group(group_one, seed_dict, False, font_group, False)
                    draw_room_furniture(group_one, seed_dict, draw_label, font_furniture, draw_arrow)

            # 调试信息
            if '382641' not in room_key and False:
                continue
            # 绘制机位
            if 'scene' in room_layout_one:
                scene_list = room_layout_one['scene']
                draw_room_scene(scene_list)
            # 绘制点位
            if 'wander_origin' in room_layout_one and False:
                wander_list = room_layout_one['wander_origin']
                draw_room_wander_v1(wander_list)
                continue
            # 绘制路线
            if 'route' in room_layout_one:
                route_list = room_layout_one['route']
                draw_room_route(route_list)
            # 绘制点位
            if 'wander' in room_layout_one:
                wander_list = room_layout_one['wander']
                draw_room_wander_v1(wander_list)
    # 绘制矩形
    for room_id, room_rect_dict in rect_info.items():
        if room_id not in room_dict:
            continue
        scheme_cnt = len(room_rect_dict['room_rect'])
        for rect_list_idx, rect_list_one in enumerate(room_rect_dict['room_rect']):
            if not rect_list_idx == scheme_index % scheme_cnt:
                continue
            # 绘制矩形
            if 'rect' not in rect_list_one:
                break
            for rect_one in rect_list_one['rect']:
                draw_room_rectangle(rect_one)
            break

    # 绘制路径
    wander_info, house_wander, room_wander = {}, [], {}
    if 'wander_info' in data_info:
        wander_info = data_info['wander_info']
        if 'house_wander' in wander_info:
            house_wander = wander_info['house_wander']
        if 'room_wander' in wander_info:
            room_wander = wander_info['room_wander']
    for room_key, room_val in room_wander.items():
        wander_room, wander_group = [], []
        if 'wander_room' in room_val:
            wander_room = room_val['wander_room']
        if 'wander_group' in room_val:
            wander_group = room_val['wander_group']
        wander_set, wander_idx = wander_room, 0
        if len(wander_set) <= 0:
            continue
        wander_one = wander_set[wander_idx % len(wander_set)]
        draw_room_wander_v2([wander_one])

    # 保存图像
    plt.close(figure)
    figure.savefig(image_path, dpi=90)


# 绘制布局
def draw_house_scheme(house_id, data_info, layout_info, image_dir='',
                      room_to_draw=[], group_to_draw=[], room_id_draw=[],
                      room_label=False, draw_label=False, draw_arrow=False, draw_detail=2):
    # 补充参数
    if len(room_to_draw) == 0:
        room_to_draw = DRAW_ROOM_LIST
    if image_dir == '':
        image_dir = DATA_DIR_FURNITURE
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # 遍历房间
    room_dict = {}
    room_dict_box = {}
    for room_data in data_info['room']:
        # 判断标识
        if len(room_id_draw) > 0 and room_data['id'] not in room_id_draw:
            continue
        # 判断类型
        room_type = room_data['type']
        if room_type not in room_to_draw:
            continue
        if 'floor' not in room_data:
            continue
        # 房间大小
        floor = room_data['floor']
        floor_len = int(len(floor) / 2)
        if floor_len < 1:
            continue
        x_max = x_min = floor[0]
        y_max = y_min = floor[1]
        for i in range(floor_len):
            # 起点终点
            x = floor[2 * i + 0]
            y = floor[2 * i + 1]
            if x_max < x:
                x_max = x
            if x_min > x:
                x_min = x
            if y_max < y:
                y_max = y
            if y_min > y:
                y_min = y
        room_dict[room_data['id']] = room_data
        room_dict_box[room_data['id']] = [x_min, y_min, x_max, y_max]

    # 绘制布局
    for room_id, room_layout in layout_info.items():
        # 判断房间
        room_type = room_layout['room_type']
        if room_type not in room_to_draw:
            continue
        if room_id not in room_dict:
            continue
        if len(room_layout['layout_scheme']) > 0:
            room_dir = os.path.join(image_dir, room_type)
            if not os.path.exists(room_dir):
                os.makedirs(room_dir)
        room_box = [-5, -5, 5, 5]
        if room_id in room_dict_box:
            room_box = room_dict_box[room_id]
        # 种子信息
        seed_dict = {}
        if 'layout_seed' in room_layout:
            for seed_one in room_layout['layout_seed']:
                seed_dict[seed_one['id']] = 1
        if 'layout_keep' in room_layout:
            for seed_one in room_layout['layout_keep']:
                seed_dict[seed_one['id']] = 1
        # 遍历方案
        for layout_idx, layout_one in enumerate(room_layout['layout_scheme']):
            source_house = layout_one['source_house']
            source_room = layout_one['source_room']
            # 创建图像
            image_file = house_id + '_' + room_id + '_' + str(layout_idx) + '.jpg'
            image_path = os.path.join(image_dir, room_type, image_file)
            figure_width = room_box[2] - room_box[0] + 1
            figure_height = room_box[3] - room_box[1] + 1
            figure = plt.figure(figsize=[FIGURE_X, FIGURE_Z * figure_height / figure_width])
            plt.xlim((room_box[0] - 0.5, room_box[2] + 0.5))
            plt.ylim((room_box[3] + 0.5, room_box[1] - 0.5))
            font_room = FONT_SIZE_ROOM
            font_group = FONT_SIZE_GROUP
            font_furniture = FONT_SIZE_FURNITURE
            if figure_height > figure_width:
                font_room = int(FONT_SIZE_ROOM * figure_height / figure_width)
                font_group = int(FONT_SIZE_GROUP * figure_height / figure_width)
                font_furniture = int(FONT_SIZE_FURNITURE * figure_height / figure_width)
            # 绘制房间
            room_data = room_dict[room_id]
            room_style, room_score = '', ''
            if 'style' in layout_one:
                room_style = get_furniture_style_en(layout_one['style'])
            if 'score' in layout_one:
                room_score = str(round(float(layout_one['score']), 1))
            draw_room(room_data, [], font_room, room_label, room_style, room_score)
            # 绘制硬装
            deco_list = []
            if 'layout_mesh' in room_layout:
                deco_list = room_layout['layout_mesh']
            draw_room_mesh(deco_list)
            # 绘制分组
            for group_one in layout_one['group']:
                if group_one['type'] not in group_to_draw:
                    continue
                if draw_detail == 1:
                    draw_room_group(group_one, seed_dict, draw_label, font_group, draw_arrow)
                elif draw_detail == 2:
                    draw_room_furniture(group_one, seed_dict, draw_label, font_furniture, draw_arrow)
                elif draw_detail == 3:
                    draw_room_furniture(group_one, seed_dict, draw_label, font_furniture, draw_arrow)
            # 保存图像
            plt.close(figure)
            figure.savefig(image_path, dpi=90)


# 绘制房间 结构
def draw_room(room_info, skip_unit=[], font_size=FONT_SIZE_ROOM, room_label=False, room_style='', room_score=''):
    # 房间类型
    room_id, room_type, room_area = '', '', 0
    if 'id' in room_info:
        room_id = room_info['id']
    if 'type' in room_info:
        room_type = room_info['type']
    if 'area' in room_info:
        room_area = room_info['area']
    # 绘制部件
    unit_to_draw = DRAW_UNIT_PARAM.keys()
    for unit_type, unit_info in room_info.items():
        if unit_type.endswith('_info'):
            unit_type = unit_type[:-5]
        # 绘制参数
        if unit_type not in unit_to_draw:
            continue
        # 地面参数 其他参数
        if unit_type == 'floor':
            if room_type in DRAW_ROOM_PARAM:
                draw_param = DRAW_ROOM_PARAM[room_type]
            else:
                draw_param = DRAW_ROOM_PARAM['Default']
        else:
            draw_param = DRAW_UNIT_PARAM[unit_type]
        # 绘制地面
        unit_start_old, unit_start_new = [], []
        if unit_type == 'floor':
            unit_pts = unit_info
            unit_len = int(len(unit_pts) / 2)
            unit_array = np.zeros((unit_len, 2))
            if len(unit_pts) >= 2:
                unit_start_old = [unit_pts[0], unit_pts[1]]
            for i in range(unit_len):
                unit_array[i][0] = unit_pts[i*2+0]
                unit_array[i][1] = unit_pts[i*2+1]
                if len(unit_start_new) <= 0:
                    unit_start_new = unit_array[i][:]
                elif unit_start_new[0] - unit_start_new[1] > unit_array[i][0] - unit_array[i][1] + 0.05:
                    unit_start_new = unit_array[i][:]
            # 绘制矩形
            line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
            unit_poly = patches.Polygon(unit_array, color=line_color, fill=line_fill, linestyle=line_style)
            plt.gca().add_patch(unit_poly)
            # 绘制标签
            room_label_area = str(round(float(room_area), 1))
            room_label_type = room_type
            room_label_style = room_style
            room_label_score = room_score
            room_label_text = ''
            if room_area >= 3:
                room_label_text += room_id
                room_label_text += ' ' + room_label_area
                room_label_text += '\n'
                room_label_text += room_label_type
                room_label_text += ' ' + room_label_style
            else:
                room_label_text += room_id
                room_label_text += ' ' + room_label_area
                room_label_text += '\n'
            if room_label and len(unit_start_new) >= 2 and room_area >= 2:
                plt.annotate(room_label_text, xy=(unit_start_new[0] + 0.1, unit_start_new[1] - 0.1), fontsize=font_size)
            # 绘制起点
            if len(unit_start_old) >= 2:
                plt.plot(unit_start_old[0], unit_start_old[1], 'ks', label='point')
            continue
        # 依次绘制
        draw_param_old = draw_param
        for unit_one in unit_info:
            unit_pts = unit_one['pts']
            # 判断主门 主门跳过
            if unit_type == 'door' and unit_one['to'] == '':
                draw_param = DRAW_UNIT_PARAM['maindoor']
            else:
                draw_param = draw_param_old
            unit_len = int(len(unit_pts) / 2)
            unit_array = np.zeros((unit_len, 2))
            for i in range(unit_len):
                unit_array[i][0] = unit_pts[(i * 2 + 0) % len(unit_pts)]
                unit_array[i][1] = unit_pts[(i * 2 + 1) % len(unit_pts)]
            # 绘制矩形
            line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
            unit_poly = patches.Polygon(unit_array, color=line_color, fill=line_fill, linestyle=line_style)
            plt.gca().add_patch(unit_poly)


# 绘制房间 结构 TODO:
def draw_room_icon(room_info, skip_unit=[], draw_label=False, font_size=FONT_SIZE_ROOM, room_score=''):
    # floor
    # door
    # hole
    # window
    # baywindow
    pass


# 绘制房间 硬装
def draw_room_mesh(object_list):
    if len(object_list) <= 0:
        return
    for object_one in object_list:
        # 硬装信息
        object_type = object_one['type']
        object_size = [object_one['size'][i] * object_one['scale'][i] / 100 for i in range(3)]
        object_position = object_one['position']
        object_rotation = object_one['rotation']
        object_role = ''
        for mesh_role, type_list in GROUP_MESH_DICT.items():
            if object_type in type_list:
                object_role = mesh_role
                break
        # 绘制参数
        if object_role == '':
            continue
        if object_role not in DRAW_MESH_PARAM:
            continue
        draw_param = DRAW_MESH_PARAM[object_role]
        # 相对坐标
        width_x, width_z = object_size[0], object_size[2]
        if object_role in ['background']:
            if max(width_x, width_z) > 20 or min(width_x, width_z) > 5:
                continue
        x1 = x4 = -width_x / 2
        x2 = x3 = width_x / 2
        z1 = z2 = -width_z / 2
        z3 = z4 = width_z / 2
        # 旋转坐标
        angle = rot_to_ang(object_rotation)
        angle_sin = math.sin(angle)
        angle_cos = math.cos(angle)
        z1_new = z1 * angle_cos - x1 * angle_sin + object_position[2]
        x1_new = z1 * angle_sin + x1 * angle_cos + object_position[0]
        z2_new = z2 * angle_cos - x2 * angle_sin + object_position[2]
        x2_new = z2 * angle_sin + x2 * angle_cos + object_position[0]
        z3_new = z3 * angle_cos - x3 * angle_sin + object_position[2]
        x3_new = z3 * angle_sin + x3 * angle_cos + object_position[0]
        z4_new = z4 * angle_cos - x4 * angle_sin + object_position[2]
        x4_new = z4 * angle_sin + x4 * angle_cos + object_position[0]
        # 绝对坐标
        unit_array = np.array([[x1_new, z1_new], [x2_new, z2_new], [x3_new, z3_new], [x4_new, z4_new]])
        # 绘制矩形
        line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
        unit_poly = patches.Polygon(unit_array, color=line_color, fill=line_fill, linestyle=line_style)
        plt.gca().add_patch(unit_poly)
        if object_role == 'ceiling':
            # 相对坐标
            width_x = object_size[0] - 2 * object_size[1]
            width_z = object_size[2] - 2 * object_size[1]
            x1 = x4 = -width_x / 2
            x2 = x3 = width_x / 2
            z1 = z2 = -width_z / 2
            z3 = z4 = width_z / 2
            # 旋转坐标
            angle = rot_to_ang(object_rotation)
            angle_sin = math.sin(angle)
            angle_cos = math.cos(angle)
            z1_new = z1 * angle_cos - x1 * angle_sin + object_position[2]
            x1_new = z1 * angle_sin + x1 * angle_cos + object_position[0]
            z2_new = z2 * angle_cos - x2 * angle_sin + object_position[2]
            x2_new = z2 * angle_sin + x2 * angle_cos + object_position[0]
            z3_new = z3 * angle_cos - x3 * angle_sin + object_position[2]
            x3_new = z3 * angle_sin + x3 * angle_cos + object_position[0]
            z4_new = z4 * angle_cos - x4 * angle_sin + object_position[2]
            x4_new = z4 * angle_sin + x4 * angle_cos + object_position[0]
            # 绝对坐标
            unit_array2 = np.array([[x1_new, z1_new], [x2_new, z2_new], [x3_new, z3_new], [x4_new, z4_new]])
            unit_poly2 = patches.Polygon(unit_array2, color=line_color, fill=line_fill, linestyle=line_style)
            plt.gca().add_patch(unit_poly2)


# 绘制房间 硬装 TODO:
def draw_room_mesh_icon(deco_list):
    pass


# 绘制房间 组合
def draw_room_group(group_info, seed_dict={}, draw_label=False, font_size=FONT_SIZE_GROUP, draw_arrow=False):
    # 绘制参数
    if group_info['type'] not in GROUP_RULE_FUNCTIONAL:
        return
    if group_info['type'] in DRAW_GROUP_PARAM:
        draw_param = DRAW_GROUP_PARAM[group_info['type']]
    else:
        draw_param = DRAW_GROUP_PARAM['Default']
    # 分组信息
    group_size, group_position, group_rotation = group_info['size'], group_info['position'], group_info['rotation']
    # 相对坐标
    width_x, width_z = group_size[0], group_size[2]
    x1 = x4 = -width_x / 2
    x2 = x3 = width_x / 2
    z1 = z2 = -width_z / 2
    z3 = z4 = width_z / 2
    if 'regulation' in group_info:
        x1 = x4 = -(width_x / 2 + group_info['regulation'][1])
        x2 = x3 = width_x / 2 + group_info['regulation'][3]
        z1 = z2 = -(width_z / 2 + group_info['regulation'][0])
        z3 = z4 = width_z / 2 + group_info['regulation'][2]
    # 旋转坐标
    angle = rot_to_ang(group_rotation)
    angle_sin = math.sin(angle)
    angle_cos = math.cos(angle)
    z1_new = z1 * angle_cos - x1 * angle_sin + group_position[2]
    x1_new = z1 * angle_sin + x1 * angle_cos + group_position[0]
    z2_new = z2 * angle_cos - x2 * angle_sin + group_position[2]
    x2_new = z2 * angle_sin + x2 * angle_cos + group_position[0]
    z3_new = z3 * angle_cos - x3 * angle_sin + group_position[2]
    x3_new = z3 * angle_sin + x3 * angle_cos + group_position[0]
    z4_new = z4 * angle_cos - x4 * angle_sin + group_position[2]
    x4_new = z4 * angle_sin + x4 * angle_cos + group_position[0]
    # 绝对坐标
    unit_array = np.array([[x1_new, z1_new], [x2_new, z2_new], [x3_new, z3_new], [x4_new, z4_new]])
    # 绘制矩形
    line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
    unit_poly = patches.Polygon(unit_array, color=line_color, fill=line_fill, linestyle=line_style)
    plt.gca().add_patch(unit_poly)
    # 绘制标签
    if draw_label:
        x_center = (x1_new + x3_new) / 2
        z_center = (z1_new + z3_new) / 2
        plt.annotate(group_info['type'], xy=(x_center, z_center), ha='center', va='center', fontsize=font_size)
    # 绘制箭头
    if draw_arrow:
        x_center = (x1_new + x3_new) / 2
        z_center = (z1_new + z3_new) / 2
        x0 = 0
        z0 = width_z / 5
        z0_delta = z0 * angle_cos - x0 * angle_sin
        x0_delta = z0 * angle_sin + x0 * angle_cos
        plt.arrow(x_center, z_center, x0_delta, z0_delta, width=0.01)


# 绘制房间 机位
def draw_room_scene(scene_list):
    for scene_info in scene_list:
        if 'camera' not in scene_info:
            continue
        camera_info = scene_info['camera']
        if len(camera_info) <= 0:
            continue
        fov = camera_info['fov'] / 180 * math.pi
        pos_0, pos_1 = camera_info['pos'], camera_info['target']
        dis, ang = xyz_to_ang(pos_0[0], pos_0[2], pos_1[0], pos_1[2])
        if dis < 0.001:
            continue
        near, far = dis, 5
        if 'near' in camera_info and 'far' in camera_info:
            near, far = camera_info['near'], camera_info['far']
        pos_2 = pos_1[:]
        pos_2[0] = pos_0[0] * (1 - near / dis) + pos_1[0] * near / dis
        pos_2[2] = pos_0[2] * (1 - near / dis) + pos_1[2] * near / dis
        # 距离
        dis_1 = dis
        rat_1, rat_2, rat_3 = 1, 1, 1
        if dis > 0:
            rat_2 = min(near / dis, 1 / dis)
            rat_3 = min(far / dis, 1 / dis)
        # 近点
        ang_new = ang + fov / 2
        add_x, add_z = dis_1 * math.sin(ang_new), dis_1 * math.cos(ang_new)
        pos_1_1 = [pos_0[0] + add_x * rat_1, pos_0[2] + add_z * rat_1]
        pos_2_1 = [pos_0[0] + add_x * rat_2, pos_0[2] + add_z * rat_2]
        pos_3_1 = [pos_0[0] + add_x * rat_3, pos_0[2] + add_z * rat_3]
        # 远点
        ang_new = ang - fov / 2
        add_x, add_z = dis_1 * math.sin(ang_new), dis_1 * math.cos(ang_new)
        pos_1_2 = [pos_0[0] + add_x * rat_1, pos_0[2] + add_z * rat_1]
        pos_2_2 = [pos_0[0] + add_x * rat_2, pos_0[2] + add_z * rat_2]
        pos_3_2 = [pos_0[0] + add_x * rat_3, pos_0[2] + add_z * rat_3]
        # 绘制参数
        draw_param = DRAW_CAMERA_PARAM['Default']
        # 绝对坐标
        pos_0_0 = [pos_0[0], pos_0[2]]
        unit_array_1 = np.array([pos_0_0, pos_1_1, [pos_1[0], pos_1[2]], pos_1_2])
        unit_array_2 = np.array([pos_0_0, pos_2_1, [pos_2[0], pos_2[2]], pos_2_2])
        unit_array_3 = np.array([pos_0_0, pos_3_1, pos_3_2])
        # 绘制相机
        line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
        unit_poly_1 = patches.Polygon(unit_array_1, color=line_color, fill=line_fill, linestyle=line_style)
        unit_poly_2 = patches.Polygon(unit_array_2, color=line_color, fill=line_fill, linestyle=line_style)
        unit_poly_3 = patches.Polygon(unit_array_3, color=line_color, fill=line_fill, linestyle=line_style)
        plt.gca().add_patch(unit_poly_1)
        plt.gca().add_patch(unit_poly_2)
        plt.gca().add_patch(unit_poly_3)
        # 绘制端点
        plt.plot(pos_0[0], pos_0[2], 'gs', label='point', linewidth=2)
        # plt.plot(pos_1[0], pos_1[2], 'gs', label='point', linewidth=2)
        pass
        # 绘制锚点
        draw_anchor = False
        if draw_anchor:
            if 'anchor_hard' in scene_info and len(scene_info['anchor_hard']) > 0:
                if 'position' in scene_info['anchor_hard'][0]:
                    pos_anchor = scene_info['anchor_hard'][0]['position']
                    plt.plot(pos_anchor[0], pos_anchor[2], 'rs', label='point', linewidth=2)
            if 'anchor_soft' in scene_info and len(scene_info['anchor_soft']) > 0:
                if 'position' in scene_info['anchor_soft'][0]:
                    pos_anchor = scene_info['anchor_soft'][0]['position']
                    plt.plot(pos_anchor[0], pos_anchor[2], 'rs', label='point', linewidth=2)
            if 'anchor_link' in scene_info and len(scene_info['anchor_link']) > 0:
                anchor_set = scene_info['anchor_link']
                for anchor_one in anchor_set:
                    if 'position' in anchor_one:
                        pos_anchor = anchor_one['position']
                        plt.plot(pos_anchor[0], pos_anchor[2], 'bs', label='point', linewidth=2)
                    if 'position_fix' in anchor_one:
                        pos_anchor = anchor_one['position_fix']
                        plt.plot(pos_anchor[0], pos_anchor[2], 'bs', label='point', linewidth=2)
        # 绘制冲突
        if 'intersect' in scene_info:
            intersect_info = scene_info['intersect']
            for unit_key, unit_set in intersect_info.items():
                for unit_one in unit_set:
                    pos_c = []
                    if len(unit_one) >= 8:
                        pos_c = [(unit_one[0] + unit_one[2] + unit_one[4] + unit_one[6]) / 4,
                                 (unit_one[1] + unit_one[3] + unit_one[5] + unit_one[7]) / 4]
                    elif len(unit_one) >= 4:
                        pos_c = [(unit_one[0] + unit_one[2]) / 2, (unit_one[1] + unit_one[3]) / 2]
                    elif len(unit_one) >= 2:
                        pos_c = [unit_one[0], unit_one[1]]
                    if len(pos_c) >= 2:
                        plt.plot(pos_c[0], pos_c[1], 'gs', label='point', linewidth=2)


# 绘制房间 路线
def draw_room_route(route_list):
    # 绘制参数
    draw_param = DRAW_CAMERA_PARAM['Default']
    line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
    # 绘制路线
    for route_info in route_list:
        for path_one in route_info:
            # p1 p2
            pos_1, pos_2 = path_one['p1'], path_one['p2']
            # point
            route_point = path_one['point']

            # 绘制路线
            unit_array_1 = np.array([pos_1, pos_2, pos_1])
            unit_poly_1 = patches.Polygon(unit_array_1, color=line_color, fill=line_fill, linestyle=line_style)
            plt.gca().add_patch(unit_poly_1)


# 绘制房间 点位
def draw_room_wander_v1(wander_list):
    # 绘制参数
    draw_param = DRAW_CAMERA_PARAM['Default']
    line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
    # 绘制机位
    for wander_info in wander_list:
        for wander_one in wander_info:
            pos_old_1, pos_old_2 = wander_one['pos'], wander_one['target']
            pos_new_1, pos_new_2 = pos_old_1[:], pos_old_2[:]
            x1, z1, x2, z2 = pos_old_1[0], pos_old_1[2], pos_old_2[0], pos_old_2[2]
            dis, ang = xyz_to_ang(x1, z1, x2, z2)
            if dis > 0.2:
                r = 0.2 / dis
                pos_new_2[0] = x1 * (1 - r) + x2 * r
                pos_new_2[2] = z1 * (1 - r) + z2 * r
                pass
            # 点位
            plt.plot(pos_new_1[0], pos_new_1[2], 'gs', label='point', linewidth=2)
            # 方向
            pos_1, pos_2 = [pos_new_1[0], pos_new_1[2]], [pos_new_2[0], pos_new_2[2]]
            unit_array_1 = np.array([pos_1, pos_2, pos_1])
            unit_poly_1 = patches.Polygon(unit_array_1, color=line_color, fill=line_fill, linestyle=line_style)
            plt.gca().add_patch(unit_poly_1)
    pass


# 绘制房间 点位
def draw_room_wander_v2(wander_list):
    # 绘制参数
    draw_param = DRAW_CAMERA_PARAM['Default']
    line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
    # 绘制机位
    for wander_info in wander_list:
        for wander_one in wander_info:
            pos_old_1, pos_old_2 = wander_one['pos'], wander_one['target']
            pos_new_1, pos_new_2 = pos_old_1[:], pos_old_2[:]
            x1, z1, x2, z2 = pos_old_1[0], pos_old_1[2], pos_old_2[0], pos_old_2[2]
            dis, ang = xyz_to_ang(x1, z1, x2, z2)
            if dis > 0.2:
                r = 0.2 / dis
                pos_new_2[0] = x1 * (1 - r) + x2 * r
                pos_new_2[2] = z1 * (1 - r) + z2 * r
                pass
            # 点位
            plt.plot(pos_new_1[0], pos_new_1[2], 'rs', label='point', linewidth=4)
            # 方向
            pos_1, pos_2 = [pos_new_1[0], pos_new_1[2]], [pos_new_2[0], pos_new_2[2]]
            unit_array_1 = np.array([pos_1, pos_2, pos_1])
            unit_poly_1 = patches.Polygon(unit_array_1, color=line_color, fill=line_fill, linestyle=line_style)
            plt.gca().add_patch(unit_poly_1)
    pass


# 绘制房间 家具
def draw_room_furniture(group_one, seed_dict={}, draw_label=False, font_size=FONT_SIZE_FURNITURE, draw_arrow=False):
    # 绘制参数
    draw_param = DRAW_GROUP_PARAM['Default']
    group_type = group_one['type']
    if group_type in DRAW_FURNITURE_PARAM:
        draw_param = DRAW_FURNITURE_PARAM[group_type]
    # 遍历家具
    draw_list, skip_list, deco_count = [], [], 0
    if 'obj_list' in group_one:
        draw_list = group_one['obj_list']
    for furniture_one in draw_list:
        furniture_id, furniture_role, furniture_type = furniture_one['id'], furniture_one['role'], furniture_one['type']
        # 家具重复
        furniture_count = 1
        if 'count' in furniture_one:
            furniture_count = furniture_one['count']
        if furniture_count >= 3:
            continue
        # 角色判定
        if furniture_role in skip_list and group_type in GROUP_RULE_FUNCTIONAL:
            continue
        if furniture_role in ['accessory']:
            deco_count += 1
            if deco_count >= 15:
                continue
        # 位置
        furniture_position = furniture_one['position']
        furniture_rotation = furniture_one['rotation']
        furniture_angle = rot_to_ang(furniture_rotation)
        # 尺寸
        origin_size, origin_scale = furniture_one['size'], furniture_one['scale']
        furniture_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        # 相对坐标
        width_x, width_z = furniture_size[0], furniture_size[2]
        x1 = x4 = -width_x / 2
        x2 = x3 = width_x / 2
        z1 = z2 = -width_z / 2
        z3 = z4 = width_z / 2
        # 旋转坐标
        angle = furniture_angle
        angle_sin, angle_cos = math.sin(angle), math.cos(angle)
        z1_new = z1 * angle_cos - x1 * angle_sin + furniture_position[2]
        x1_new = z1 * angle_sin + x1 * angle_cos + furniture_position[0]
        z2_new = z2 * angle_cos - x2 * angle_sin + furniture_position[2]
        x2_new = z2 * angle_sin + x2 * angle_cos + furniture_position[0]
        z3_new = z3 * angle_cos - x3 * angle_sin + furniture_position[2]
        x3_new = z3 * angle_sin + x3 * angle_cos + furniture_position[0]
        z4_new = z4 * angle_cos - x4 * angle_sin + furniture_position[2]
        x4_new = z4 * angle_sin + x4 * angle_cos + furniture_position[0]
        # 绝对坐标
        unit_array = np.array([[x1_new, z1_new], [x2_new, z2_new], [x3_new, z3_new], [x4_new, z4_new]])
        # 绘制矩形
        line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param['line_style']
        unit_poly = patches.Polygon(unit_array, color=line_color, fill=line_fill, linestyle=line_style)
        plt.gca().add_patch(unit_poly)
        # 绘制标签
        role_flag, seed_flag, turn_flag, fake_flag = True, False, False, False
        mirror_flag, vision_flag, adjust_flag = False, False, False
        if group_type in GROUP_RULE_DECORATIVE and not group_type == 'Floor':
            role_flag = False
        if furniture_role in ['', 'accessory', 'rug', 'art', 'screen', 'back table']:
            role_flag = False
        elif furniture_role in ['plants']:
            if 'relate' in furniture_one and len(furniture_one['relate']) > 0:
                role_flag = False
        if furniture_id in seed_dict:
            seed_flag = True
        if not get_furniture_turn(furniture_id) == 0:
            turn_flag = True
        if 'turn' in furniture_one and abs(furniture_one['turn']) > 0:
            turn_flag = True
        if 'fake_size' in furniture_one and furniture_one['fake_size'] > 0:
            fake_flag = True
        if 'scale' in furniture_one and furniture_one['scale'][0] < -0.01:
            mirror_flag = True
        if 'vision' in furniture_one and furniture_one['vision'] > 0:
            vision_flag = True
        if 'adjust' in group_one and group_one['adjust'] > 0:
            adjust_flag = True

        if draw_label and role_flag:
            x_center = (x1_new + x3_new) / 2
            z_center = (z1_new + z3_new) / 2
            role_text, seed_text, fake_text = '', '', ''
            if role_flag:
                role_text = furniture_role
                if group_type in ['Rest'] and ('chair' in furniture_type or 'sofa' in furniture_type):
                    role_text = 'chair'
                if vision_flag:
                    role_text = '-' + role_text + '-'
            if seed_flag:
                seed_text = '\nseed'
            if turn_flag:
                fake_text += '\nturn'
            if fake_flag:
                fake_text += '\nfake'
            if mirror_flag:
                fake_text += '\nswap'
            if adjust_flag and not seed_flag:
                fake_text += '\nback'
            full_txt = role_text + seed_text + fake_text
            plt.annotate(full_txt, xy=(x_center, z_center), ha='center', va='center', fontsize=font_size)
        # 绘制箭头
        if draw_arrow and role_flag:
            x_center = (x1_new + x3_new) / 2
            z_center = (z1_new + z3_new) / 2
            x0 = 0
            z0 = width_z / 5
            z0_delta = z0 * angle_cos - x0 * angle_sin
            x0_delta = z0 * angle_sin + x0 * angle_cos
            plt.arrow(x_center, z_center, x0_delta, z0_delta, width=0.01)


# 绘制房间 家具 TODO:
def draw_room_furniture_icon(group_one, seed_dict={},
                             draw_label=False, font_size=FONT_SIZE_FURNITURE, draw_arrow=False):
    pass


# 绘制房间 矩形
def draw_room_rectangle(rect_one):
    # 参数
    draw_param = DRAW_RECT_PARAM['Default']
    rect_type, rect_score = rect_one['type'], rect_one['score']
    if rect_type == 1:
        draw_param = DRAW_RECT_PARAM['Group']
    if rect_score < 0:
        rect_score = 1
    (r, g, b, a) = draw_param['line_color']
    line_color = (r, g, b, 1.0 * rect_score / 10)
    # 顶点
    x1_new = rect_one['p1'][0]
    z1_new = rect_one['p1'][1]
    x2_new = rect_one['p2'][0]
    z2_new = rect_one['p2'][1]
    x3_new = rect_one['p3'][0]
    z3_new = rect_one['p3'][1]
    x4_new = rect_one['p4'][0]
    z4_new = rect_one['p4'][1]
    # 绝对坐标
    unit_array = np.array([[x1_new, z1_new], [x2_new, z2_new], [x3_new, z3_new], [x4_new, z4_new]])
    # 绘制分组
    line_fill, line_style = draw_param['fill'], draw_param['line_style']
    unit_poly = patches.Polygon(unit_array, color=line_color, fill=line_fill, linestyle=line_style)
    plt.gca().add_patch(unit_poly)


# 绘制组合
def draw_group_layout(group_one, image_path='', scheme_index=0,
                      draw_label=True, font_size=FONT_SIZE_GROUP, draw_arrow=True, draw_detail=2):
    # 创建图像
    if image_path == '':
        image_path = os.path.join(DATA_DIR_HOUSE_IMAGE, 'test_group_%02d_00.png' % scheme_index)
    group_pos = group_one['position']
    house_box = [group_pos[0] - 2, group_pos[2] - 2, group_pos[0] + 2, group_pos[2] + 2]
    figure_width = house_box[2] - house_box[0] + 1
    figure_height = house_box[3] - house_box[1] + 1
    figure = plt.figure(figsize=[FIGURE_X, FIGURE_Z * figure_height / figure_width])
    plt.xlim((house_box[0] - 0.5, house_box[2] + 0.5))
    plt.ylim((house_box[3] + 0.5, house_box[1] - 0.5))
    font_room, font_group, font_furniture = FONT_SIZE_ROOM, FONT_SIZE_GROUP, FONT_SIZE_FURNITURE
    # 种子信息
    seed_dict = {}
    if 'seed_list' in group_one:
        for seed_one in group_one['seed_list']:
            seed_dict[seed_one] = 1
    if 'keep_list' in group_one:
        for seed_one in group_one['keep_list']:
            seed_dict[seed_one] = 1
    # 绘制分组
    if draw_detail == 1:
        draw_room_group(group_one, seed_dict, draw_label, font_group, draw_arrow)
    elif draw_detail == 2:
        draw_room_furniture(group_one, seed_dict, draw_label, font_furniture, draw_arrow)
    elif draw_detail == 3:
        draw_room_furniture(group_one, seed_dict, draw_label, font_furniture, draw_arrow)
    # 保存图像
    plt.close(figure)
    figure.savefig(image_path, dpi=90)


# 功能测试
if __name__ == '__main__':
    house_id = '0d8edd78-6d9b-46c3-b3c9-296d17273da3'
    draw_house(house_id, '', [], room_label=True)
    pass
