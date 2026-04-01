# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-01-18
@Description: 解析户型数据，包括入户门、各个房间的轮廓、门、窗、门洞、飘窗等信息

"""

import os
import copy
import json
from shapely.geometry import Polygon, LineString

from Furniture.furniture import *
from House.house_data_detail import *


# 类型列表
ROOM_TYPE_MAIN = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                  'MasterBedroom', 'SecondBedroom', 'Bedroom',
                  'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                  'Library',
                  'Kitchen',
                  'MasterBathroom', 'SecondBathroom', 'Bathroom',
                  'Balcony', 'Terrace', 'Lounge', 'Auditorium',
                  'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                  'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom',
                  ]
ROOM_TYPE_LIST = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                  'MasterBedroom', 'SecondBedroom', 'Bedroom',
                  'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                  'Library',
                  'Kitchen',
                  'MasterBathroom', 'SecondBathroom', 'Bathroom',
                  'Balcony', 'Terrace', 'Lounge', 'Auditorium',
                  'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                  'StorageRoom', 'CloakRoom', 'LaundryRoom', 'EquipmentRoom', 'OtherRoom',
                  'Courtyard', 'Garage', 'OtherSpace',
                  'undefined', 'none']
ROOM_TYPE_CODE = {
    'LivingDiningRoom': 11, 'LivingRoom': 12, 'DiningRoom': 13,
    'MasterBedroom': 21, 'SecondBedroom': 22, 'Bedroom': 23, 'KidsRoom': 24, 'ElderlyRoom': 25, 'NannyRoom': 26,
    'Library': 31,
    'Kitchen': 51,
    'MasterBathroom': 61, 'SecondBathroom': 62, 'Bathroom': 63,
    'Balcony': 71, 'Terrace': 72, 'Lounge': 73, 'LaundryRoom': 74,
    'Hallway': 81, 'Aisle': 82, 'Corridor': 83, 'Stairwell': 84,
    'StorageRoom': 91, 'CloakRoom': 92, 'EquipmentRoom': 93, 'Auditorium': 94, 'OtherRoom': 95,
    'Courtyard': 96, 'Garage': 97,
    'none': 99
}
ROOM_TYPE_NAME = {
    'LivingDiningRoom': '客餐厅', 'LivingRoom': '客厅', 'DiningRoom': '餐厅',
    'MasterBedroom': '主卧', 'SecondBedroom': '次卧', 'Bedroom': '卧室',
    'KidsRoom': '儿童房', 'ElderlyRoom': '老人房', 'NannyRoom': '保姆房',
    'Library': '书房',
    'Kitchen': '厨房',
    'MasterBathroom': '主卫', 'SecondBathroom': '次卫', 'Bathroom': '卫浴',
    'Balcony': '阳台', 'Terrace': '阳台', 'Lounge': '休息室', 'Auditorium': '礼堂',
    'Hallway': '门厅', 'Aisle': '走道', 'Corridor': '走廊', 'Stairwell': '楼梯间',
    'StorageRoom': '储物间', 'CloakRoom': '衣帽间', 'LaundryRoom': '洗衣房', 'EquipmentRoom': '设备间', 'OtherRoom': '其他',
    'Courtyard': '院子', 'Garage': '车库',
    'undefined': '其他', 'none': '其他'
}

# 面片类型
MESH_TYPE_MAIN = ['WallInner', 'Ceiling', 'Floor']
MESH_TYPE_DUMP = ['CustomizedFixedFurniture', 'SlabSide', 'SlabTop', 'SlabBottom', 'LightBand']
MESH_TYPE_REST = ['CustomizedFeatureWall', 'CustomizedCeiling', 'CustomizedPlatform',
                  'CustomizedFurniture', 'CustomizedPersonalizedModel',
                  'Pocket', 'Cabinet',
                  'Front', 'Back', 'SlabSide', 'SlabTop', 'SlabBottom', 'SmartCustomizedCeiling']
MESH_TYPE_DECO = ['WallOuter', 'WallTop', 'WallBottom', 'Baseboard', 'Cornice',
                  'Door', 'Hole', 'Window', 'BayWindow', 'Flue',
                  'ArcwallInner', 'ArcwallOuter']
# 默认房间高度
ROOM_HEIGHT = 2.6


class HouseData(object):
    def __init__(self):
        self.juran_data = JunRanData()
        self.room_data = RoomData()
        self.house_info = {}

    def load_file(self, file_path):
        if not os.path.exists(file_path):
            print('house data load file failure: %s no file.' % file_path)
            return {}
        file_name = os.path.basename(file_path)
        try:
            json_data = json.load(open(file_path, 'r', encoding='utf-8'))
            house_info = self.load_json(json_data)
            if len(house_info.keys()) <= 0:
                print('house data load file failure: %s.' % file_name)
            elif len(house_info['maindoor']) <= 0:
                print('house data load file warning: %s no main door.' % file_name)
            elif not house_info['maindoor'][0]:
                print('house data load file warning: %s no main door.' % file_name)
            return house_info
        except Exception as e:
            print('house data load file failure: %s' % file_name, e)
            return {}

    def load_json(self, json_data, load_mesh=False, load_room=[]):
        if json_data is None:
            print('house data load json failure: no json.')
            return {}
        # junran data
        result = self.juran_data.load_data(json_data, load_room)
        if not result:
            print('house data load json failure: juran data.')
            return {}
        # furniture data
        furniture_dict = {}
        for furniture_one in json_data['furniture']:
            furniture_uid, furniture_jid = furniture_one['uid'], furniture_one['jid']
            furniture_dict[furniture_uid] = furniture_jid
        # room data
        result = self.room_data.load_data(self.juran_data.room_list, self.juran_data.mesh_dict,
                                          self.juran_data.material_dict, furniture_dict, load_mesh)
        if not result:
            print('house data load json failure: room data')
            return {}

        # room combine
        self.room_data.combine_room()

        # room info
        self.house_info['version'] = '0.9'
        self.house_info['room'] = []
        for room_info in self.room_data.room_list:
            room_add = room_info
            room_add.pop('door')
            room_add.pop('hole')
            room_add.pop('window')
            room_add.pop('window_height')
            room_add.pop('baywindow')
            room_add.pop('baywindow_height')
            room_add.pop('furniture')
            room_add.pop('decorate')
            self.house_info['room'].append(room_add)

        # scene info
        if 'extension' in json_data and 'topicalcases' in json_data['extension']:
            param_list = json_data['extension']['topicalcases']
            scene_list = []
            for param_one in param_list:
                if 'camera' not in param_one or 'roomId' not in param_one:
                    continue
                scene_one = {
                    'camera': copy.deepcopy(param_one['camera']),
                    'roomId': param_one['roomId']
                }
                scene_list.append(scene_one)
            self.house_info['scene'] = scene_list

        # furniture info
        for room_one in self.house_info['room']:
            furniture_set, furniture_cnt = [], 0
            if 'furniture_info' in room_one:
                furniture_set = room_one['furniture_info']
                furniture_cnt = len(furniture_set)
            for furniture_idx, furniture_one in enumerate(furniture_set):
                obj_key, obj_type, obj_style, obj_size = '', '', '', []
                if 'id' in furniture_one:
                    obj_key = furniture_one['id']
                obj_type, obj_style, obj_size = get_furniture_data(obj_key)
                furniture_one['type'] = obj_type
                furniture_one['style'] = obj_style
                furniture_one['size'] = obj_size[:]
        return self.house_info

    def get_room_by_id(self, room_id):
        for room_one in self.room_data.room_list:
            if room_one['id'] == room_id:
                return room_one
        return {}

    def get_room_by_type(self, room_type):
        for room_one in self.room_data.room_list:
            if room_one['type'] == room_type:
                return room_one
        return {}


class JunRanData(object):
    def __init__(self):
        self.json_data = {}
        self.room_list = []
        self.door_dict = {}
        self.furniture_list = []
        self.mesh_dict = {}

    def load_data(self, json_data_original, load_room=[]):
        self.json_data = json_data_original
        # load json
        try:
            uid = self.json_data['uid']
            furniture = self.json_data['furniture']
            mesh = self.json_data['mesh']
            material = self.json_data['material']
            extension = self.json_data['extension']
            scene = self.json_data['scene']
            room = scene['room']
        except Exception as e:
            print('juran data load data failure:', e)
            return False
        # load room
        self.room_list = []
        try:
            for room_one in room:
                if len(load_room) > 0:
                    room_flag = False
                    for todo_key in load_room:
                        if todo_key in room_one['instanceid']:
                            room_flag = True
                    if not room_flag:
                        continue
                room_tmp = {}
                room_tmp['id'] = room_one['instanceid']
                room_tmp['type'] = room_one['type']
                room_tmp['children'] = room_one['children']
                self.room_list.append(room_tmp)
        except Exception as e:
            print('juran data load room failure:', e)
            self.room_list = []
        if len(self.room_list) <= 0:
            print('juran data load data failure: no room')
            return False

        # load door
        self.door_dict = {}
        try:
            door_info_list = []
            room_id_list = []
            for door_one in extension['door']:
                if 'type' in door_one.keys() and door_one['type'] == 'entryDoor':
                    door_tmp = {'type': door_one['type'], 'dir': door_one['dir'], 'ref': door_one['ref']}
                    door_info_list.append(door_tmp)
                    room_id_list.append(door_one['roomId'])
            if len(room_id_list) > 0:
                self.door_dict = dict(zip(room_id_list, door_info_list))
        except Exception as e:
            print('juran data load data failure:', e)
            self.door_dict = {}
        # load furniture
        self.furniture_list = []
        try:
            for furniture_one in furniture:
                self.furniture_list.append(furniture_one['uid'])
        except Exception as e:
            print('juran data load data failure:', e)
            self.furniture_list = []
        # load mesh
        self.mesh_dict = {}
        try:
            mesh_uid_list = []
            mesh_xyz_list = []
            for mesh_one in mesh:
                mesh_tmp = {}
                mesh_tmp['xyz'] = mesh_one['xyz']
                mesh_tmp['faces'] = mesh_one['faces']
                mesh_tmp['type'] = mesh_one['type']
                if 'material' not in mesh_one:
                    continue
                if 'uv' not in mesh_one:
                    continue
                mesh_tmp['material'] = mesh_one['material']
                mesh_tmp['uv'] = mesh_one['uv']
                mesh_uid_list.append(mesh_one['uid'])
                mesh_xyz_list.append(mesh_tmp)
            self.mesh_dict = dict(zip(mesh_uid_list, mesh_xyz_list))
        except Exception as e:
            print('juran data load mesh failure:', e)
            self.mesh_dict = {}
        if len(self.mesh_dict) <= 0:
            print('juran data load data failure: no mesh')
            return False
        # load material
        self.material_dict = {}
        try:
            for material_one in material:
                material_uid = material_one['uid']
                self.material_dict[material_uid] = material_one
        except Exception as e:
            print('juran data load material failure:', e)
            self.material_dict = {}
        return True


class MainDoorData(object):
    def __init__(self):
        self.maindoor_list = []
        self.maindoor_dict = {}

    def load_data(self, door_dict, mesh_dict):
        maindoor_ref = []
        try:
            for room_id, door_info in door_dict.items():
                maindoor_ref = door_info['ref']
        except Exception as e:
            print('maindoor data load data failure: no maindoor', e)
            return False
        mesh_list = []
        for mesh_id, mesh_info in mesh_dict.items():
            if mesh_id in maindoor_ref:
                mesh_list.append(mesh_info)
        if len(mesh_list) <= 0:
            return False
        if len(mesh_list) == 1:
            mesh_one = mesh_list[0]
            mesh_faces = mesh_one['faces']
            mesh_xyz = mesh_one['xyz']
            x_list = []
            z_list = []
            for i in range(len(mesh_xyz) // 3):
                x_list.append(round(float(mesh_xyz[3 * i + 0]), 3))
                z_list.append(round(float(mesh_xyz[3 * i + 2]), 3))
            x_set = list(set(x_list))
            z_set = list(set(z_list))
            self.maindoor_list.append(x_set[0])
            self.maindoor_list.append(z_set[0])
            self.maindoor_list.append(x_set[0])
            self.maindoor_list.append(z_set[1])
            self.maindoor_list.append(x_set[1])
            self.maindoor_list.append(z_set[0])
            self.maindoor_list.append(x_set[1])
            self.maindoor_list.append(z_set[1])
        else:
            for mesh_one in mesh_list:
                mesh_faces = mesh_one['faces']
                mesh_xyz = mesh_one['xyz']
                # compute sum of y coordinate value
                y_sum = 0
                for i in range(len(mesh_xyz) // 3):
                    y_sum += float(mesh_xyz[3 * i + 1])
                if y_sum < 0.01:
                    for j in range(len(mesh_xyz) // 3):
                        self.maindoor_list.append(round(float(mesh_xyz[3 * j + 0]), 3))
                        self.maindoor_list.append(round(float(mesh_xyz[3 * j + 2]), 3))
        if len(self.maindoor_list) == 0:
            return False
        return True

    def find_door(self, room_list):
        if len(self.maindoor_list) <= 0:
            return False
        for room_index, room_info in enumerate(room_list):
            if 'door' not in room_info.keys():
                continue
            if len(room_info['door']) <= 0:
                continue
            for door_points in room_info['door']:
                if self.have_door(door_points):
                    self.maindoor_dict['pts'] = door_points
                    self.maindoor_dict['room'] = room_info['id']
                    # direction
                    length = ((door_points[7] - door_points[1]) ** 2 + (door_points[6] - door_points[0]) ** 2) ** 0.5
                    dis_y = door_points[1] - door_points[7]
                    dis_x = door_points[0] - door_points[6]
                    self.maindoor_dict['direction'] = [dis_x / length, dis_y / length]
                    return True
        return False

    def have_door(self, door_points):
        for i in range(len(self.maindoor_list) // 2):
            source_point = [self.maindoor_list[2 * i], self.maindoor_list[2 * i + 1]]
            for j in range(len(door_points) // 2):
                target_point = [door_points[2 * j], door_points[2 * j + 1]]
                if source_point == target_point:
                    return True
        return False


class RoomData(object):
    def __init__(self):
        self.room_list = []
        self.room_mesh_dict = {}

    def load_data(self, room_list, mesh_dict, material_dict, object_dict, load_mesh=False):
        object_list_door, object_list_hole, object_list_window = [], [], []
        for room_one in room_list:
            for child_idx, child_one in enumerate(room_one['children']):
                child_uid = child_one['ref']
                if child_uid in object_dict:
                    child_jid = object_dict[child_uid]
                    # 门
                    if child_jid in DEFAULT_DOOR_DICT:
                        object_one = {
                            'id': child_jid,
                            'size': DEFAULT_DOOR_DICT[child_jid]['size'][:],
                            'scale': child_one['scale'][:],
                            'position': child_one['pos'][:],
                            'rotation': child_one['rot'][:],
                        }
                        object_list_door.append(object_one)
                    # 洞
                    elif child_jid in DEFAULT_HOLE_DICT:
                        object_one = {
                            'id': child_jid,
                            'size': DEFAULT_HOLE_DICT[child_jid]['size'][:],
                            'scale': child_one['scale'][:],
                            'position': child_one['pos'][:],
                            'rotation': child_one['rot'][:],
                        }
                        object_list_hole.append(object_one)
                    # 窗
                    elif child_jid in DEFAULT_WINDOW_DICT:
                        object_one = {
                            'id': child_jid,
                            'size': DEFAULT_WINDOW_DICT[child_jid]['size'][:],
                            'scale': child_one['scale'][:],
                            'position': child_one['pos'][:],
                            'rotation': child_one['rot'][:],
                        }
                        object_list_window.append(object_one)
        for room_one in room_list:
            # 基本信息
            room_info = {'id': room_one['id'], 'type': room_one['type'], 'style': '', 'area': 0, 'height': ROOM_HEIGHT,
                         'coordinate': 'xzy', 'unit': 'm'}
            # 部件面片
            mesh_list_wall, mesh_list_ceiling, mesh_list_floor = [], [], []
            mesh_list_pocket, mesh_list_baseboard = [], []
            mesh_list_door, mesh_list_hole, mesh_list_window, mesh_list_baywindow = [], [], [], []
            try:
                for child_idx, child_one in enumerate(room_one['children']):
                    child_uid = child_one['ref']
                    if child_uid in mesh_dict:
                        mesh_uid = child_uid
                        mesh_one = mesh_dict[mesh_uid]
                        if mesh_one['type'] == 'WallInner':
                            mesh_list_wall.append(mesh_one)
                        elif mesh_one['type'] == 'Ceiling':
                            mesh_list_ceiling.append(mesh_one)
                        elif mesh_one['type'] == 'Floor':
                            mesh_list_floor.append(mesh_one)

                        elif mesh_one['type'] == 'Pocket':
                            mesh_list_pocket.append(mesh_one)
                        elif mesh_one['type'] == 'Baseboard':
                            mesh_list_baseboard.append(mesh_one)

                        elif mesh_one['type'] == 'Door':
                            mesh_list_door.append(mesh_one)
                        elif mesh_one['type'] == 'Hole':
                            mesh_list_hole.append(mesh_one)
                        elif mesh_one['type'] == 'Window':
                            mesh_list_window.append(mesh_one)
                        elif mesh_one['type'] == 'BayWindow':
                            mesh_list_baywindow.append(mesh_one)

                        elif mesh_one['type'] in ['WallInner', 'WallOuter', 'WallTop', 'WallBottom']:
                            pass
                        elif mesh_one['type'] in ['SlabTop', 'SlabBottom']:
                            pass
                        else:
                            pass
            except Exception as e:
                print('room data load data failure:', e)
                continue
            # height
            for mesh_one in mesh_list_ceiling:
                mesh_xyz = mesh_one['xyz']
                y_list, y_count = [], 0
                for i in range(len(mesh_xyz) // 3):
                    y_new = round(float(mesh_xyz[3 * i + 1]), 3)
                    y_list.append(y_new)
                    if y_new > 1.0:
                        y_count += 1
                    if y_count >= 4:
                        break
                room_info['height'] = max(y_list)
            # floor data
            floor_data = FloorData()
            floor_data.load_data(mesh_list_floor)
            room_info['floor'] = floor_data.floor_list
            if len(floor_data.floor_list) <= 0:
                room_info['area'] = 0
            else:
                room_info['area'] = round(compute_area(floor_data.floor_list), 4)

            # door data
            door_data = DoorData()
            door_data.load_data(mesh_list_door, floor_data.floor_list)
            door_data.load_object(object_list_door, floor_data.floor_list)
            room_info['door'] = door_data.door_list
            # hole data
            hole_data = HoleData()
            hole_data.load_data(mesh_list_hole, floor_data.floor_list)
            hole_data.load_object(object_list_hole, floor_data.floor_list)
            room_info['hole'] = hole_data.hole_list
            # window data
            window_data = WindowData()
            window_data.load_data(mesh_list_window, floor_data.floor_list)
            window_data.load_object(object_list_window, floor_data.floor_list)
            if len(window_data.window_list) == len(window_data.window_list_height):
                room_info['window'] = window_data.window_list
                room_info['window_height'] = window_data.window_list_height
            else:
                room_info['window'] = []
                room_info['window_height'] = []
            # baywindow data
            baywindow_data = BaywindowData()
            baywindow_data.load_data(mesh_list_baywindow, floor_data.floor_list)
            if len(baywindow_data.baywindow_list) == len(baywindow_data.baywindow_list_height):
                room_info['baywindow'] = baywindow_data.baywindow_list
                room_info['baywindow_height'] = baywindow_data.baywindow_list_height
            else:
                room_info['baywindow'] = []
                room_info['baywindow_height'] = []

            # furniture data
            furniture_list = []
            for child_one in room_one['children']:
                child_uid = child_one['ref']
                child_key = ''
                if 'instanceid' in child_one:
                    child_key = child_one['instanceid']
                else:
                    child_key = child_uid.strip('/model')
                if child_uid in object_dict:
                    child_jid = object_dict[child_uid]
                    furniture_one = {
                        'id': child_jid,
                        'type': '',
                        'style': '',
                        'size': [1, 1, 1],
                        'scale': child_one['scale'],
                        'position': child_one['pos'],
                        'rotation': child_one['rot'],
                        'entityId': child_key
                    }
                    furniture_list.append(furniture_one)
            room_info['furniture'] = furniture_list
            # decorate data
            room_info['decorate'] = []
            # material data
            room_info['material'] = compute_mesh(mesh_list_wall, mesh_list_ceiling, mesh_list_floor,
                                                 mesh_list_pocket, mesh_list_baseboard, material_dict, room_info)
            if load_mesh:
                room_info['mesh'] = {
                    'wall': [],
                    'floor': []
                }
                for m in mesh_list_floor:
                    if 'material' in m and m['material'] in material_dict:
                        m['material'] = material_dict[m['material']]
                        room_info['mesh']['floor'].append(m)
                for m in mesh_list_wall:
                    if 'material' in m and m['material'] in material_dict:
                        m['material'] = material_dict[m['material']]
                        room_info['mesh']['wall'].append(m)

            # 返回信息
            if len(room_info) <= 0:
                continue
            self.room_list.append(room_info)
        if len(self.room_list) == 0:
            print('room data load data failure: no room')
            return False
        return True

    def combine_room(self):
        index_recombination = [4, 5, 6, 7, 0, 1, 2, 3]
        # room old
        for i, room_old in enumerate(self.room_list):
            floor_list = room_old['floor']
            # room new
            for j, room_new in enumerate(self.room_list):
                if i == j:
                    continue
                door_list_new = room_new['door']
                hole_list_new = room_new['hole']
                window_list_new = room_new['window']
                # door
                for unit_one in door_list_new:
                    coincide = compute_coincide_list(unit_one, floor_list)
                    if not coincide:
                        continue
                    if unit_one not in room_old['door']:
                        unit_add = []
                        for index in index_recombination:
                            unit_add.append(unit_one[index])
                        room_old['door'].append(unit_add)
                        break
                # hole
                for unit_one in hole_list_new:
                    coincide = compute_coincide_list(unit_one, floor_list)
                    if not coincide:
                        continue
                    if unit_one not in room_old['door']:
                        unit_add = []
                        for index in index_recombination:
                            unit_add.append(unit_one[index])
                        room_old['hole'].append(unit_add)
                        break
                # window
                for unit_one in window_list_new:
                    coincide = compute_coincide_list(unit_one, floor_list)
                    if not coincide:
                        continue
                    if unit_one not in room_old['door']:
                        unit_add = []
                        for index in index_recombination:
                            unit_add.append(unit_one[index])
                        room_old['window'].append(unit_add)
                        break
        # repeat
        for i, room_old in enumerate(self.room_list):
            room_old['door'] = removal_same(room_old['door'])
            room_old['hole'] = removal_same(room_old['hole'])
            room_old['window'] = removal_same(room_old['window'])
        # connect
        self.connect_room()

    def connect_room(self):
        # room old
        for i, room_old in enumerate(self.room_list):
            # door old
            door_list = []
            for unit_idx, unit_old in enumerate(room_old['door']):
                if len(unit_old) <= 0:
                    continue
                unit_dict = {'pts': unit_old, 'to': ''}
                # room new
                for j, room_new in enumerate(self.room_list):
                    if i == j:
                        continue
                    unit_to = ''
                    for unit_new in room_new['door']:
                        if compute_coincide_unit(unit_old, unit_new):
                            unit_to = room_new['id']
                            unit_dict['to'] = unit_to
                            break
                    if not unit_to == '':
                        break
                door_list.append(unit_dict)
            room_old['door_info'] = door_list
            # hold old
            hole_list = []
            for unit_idx, unit_old in enumerate(room_old['hole']):
                if len(unit_old) <= 0:
                    continue
                unit_dict = {'pts': unit_old, 'to': ''}
                # room new
                for j, room_new in enumerate(self.room_list):
                    if i == j:
                        continue
                    unit_to = ''
                    for unit_new in room_new['hole']:
                        if compute_coincide_unit(unit_old, unit_new):
                            unit_to = room_new['id']
                            unit_dict['to'] = unit_to
                            break
                    if not unit_to == '':
                        break
                hole_list.append(unit_dict)
            room_old['hole_info'] = hole_list
            # window old
            window_list = []
            for unit_idx, unit_old in enumerate(room_old['window']):
                if len(unit_old) <= 0:
                    continue
                unit_height = 0
                if 0 <= unit_idx < len(room_old['window_height']):
                    unit_height = room_old['window_height'][unit_idx]
                unit_dict = {'pts': unit_old, 'height': unit_height, 'to': ''}
                # room new
                for j, room_new in enumerate(self.room_list):
                    if i == j:
                        continue
                    unit_to = ''
                    for unit_new in room_new['window']:
                        if compute_coincide_unit(unit_old, unit_new):
                            unit_to = room_new['id']
                            unit_dict['to'] = unit_to
                            break
                    if not unit_to == '':
                        break
                window_list.append(unit_dict)
            room_old['window_info'] = window_list
            # baywindow old
            baywindow_list = []
            for unit_idx, unit_old in enumerate(room_old['baywindow']):
                if len(unit_old) <= 0:
                    continue
                unit_height = 0
                if 0 <= unit_idx < len(room_old['baywindow_height']):
                    unit_height = room_old['baywindow_height'][unit_idx]
                unit_dict = {'pts': unit_old, 'height': unit_height, 'to': ''}
                # room new
                for j, room_new in enumerate(self.room_list):
                    if i == j:
                        continue
                    unit_to = ''
                    for unit_new in room_new['baywindow']:
                        if compute_coincide_unit(unit_old, unit_new):
                            unit_to = room_new['id']
                            unit_dict['to'] = unit_to
                            break
                    if not unit_to == '':
                        break
                baywindow_list.append(unit_dict)
            room_old['baywindow_info'] = baywindow_list
            # furniture info
            room_old['furniture_info'] = room_old['furniture']
            # decorate info
            room_old['decorate_info'] = room_old['decorate']
            # material info TODO:
            room_old['material_info'] = room_old['material']
            pass


def removal_same(data_list):
    new_data_list = []
    for data in data_list:
        if data not in new_data_list:
            new_data_list.append(data)
    return new_data_list


def compute_area(polygon):
    poly = []
    for i in range(len(polygon) // 2):
        poly.append((polygon[2 * i + 0], polygon[2 * i + 1]))
    poly_sh = Polygon(poly)
    return poly_sh.area


def cal_mat_size(p1, p2, p3, uv1, uv2, uv3):
    pts = np.array([p1, p2, p3])
    pts -= np.mean(pts, axis=0)

    uv = np.array([uv1, uv2, uv3], dtype=np.float)
    uv -= np.mean(uv, axis=0)
    if abs(pts[0, 0] * pts[1, 1] - pts[1, 0] * pts[0, 1]) > 1e-8:
        a = (pts[0, 1] * uv[1, 0] - pts[1, 1] * uv[0, 0]) / (pts[1, 0] * pts[0, 1] - pts[0, 0] * pts[1, 1])
        b = (pts[1, 0] * uv[0, 0] - pts[0, 0] * uv[1, 0]) / (pts[1, 0] * pts[0, 1] - pts[0, 0] * pts[1, 1])
        c = (pts[0, 1] * uv[1, 1] - pts[1, 1] * uv[0, 1]) / (pts[1, 0] * pts[0, 1] - pts[0, 0] * pts[1, 1])
        d = (pts[1, 0] * uv[0, 1] - pts[0, 0] * uv[1, 1]) / (pts[1, 0] * pts[0, 1] - pts[0, 0] * pts[1, 1])
    elif abs(pts[0, 0] * pts[2, 1] - pts[2, 0] * pts[0, 1]) > 1e-8:
        a = (pts[0, 1] * uv[2, 0] - pts[2, 1] * uv[0, 0]) / (pts[2, 0] * pts[0, 1] - pts[0, 0] * pts[2, 1])
        b = (pts[2, 0] * uv[0, 0] - pts[0, 0] * uv[2, 0]) / (pts[2, 0] * pts[0, 1] - pts[0, 0] * pts[2, 1])
        c = (pts[0, 1] * uv[2, 1] - pts[2, 1] * uv[0, 1]) / (pts[2, 0] * pts[0, 1] - pts[0, 0] * pts[2, 1])
        d = (pts[2, 0] * uv[0, 1] - pts[0, 0] * uv[2, 1]) / (pts[2, 0] * pts[0, 1] - pts[0, 0] * pts[2, 1])
    elif abs(pts[2, 0] * pts[1, 1] - pts[1, 0] * pts[2, 1]) > 1e-8:
        a = (pts[1, 1] * uv[2, 0] - pts[2, 1] * uv[1, 0]) / (pts[2, 0] * pts[1, 1] - pts[1, 0] * pts[2, 1])
        b = (pts[2, 0] * uv[1, 0] - pts[1, 0] * uv[2, 0]) / (pts[2, 0] * pts[1, 1] - pts[1, 0] * pts[2, 1])
        c = (pts[1, 1] * uv[2, 1] - pts[2, 1] * uv[1, 1]) / (pts[2, 0] * pts[1, 1] - pts[1, 0] * pts[2, 1])
        d = (pts[2, 0] * uv[1, 1] - pts[1, 0] * uv[2, 1]) / (pts[2, 0] * pts[1, 1] - pts[1, 0] * pts[2, 1])
    else:
        return False, 1., 1.

    sx = np.sqrt(a**2 + c**2)
    sy = np.sqrt(b**2 + d**2)
    if sx < 1e-5:
        sx = 1.0
    if sy < 1e-5:
        sy = 1.0
    return True, 1. / sx, 1. / sy


def group_mesh_material(mesh_set, material_dict):
    mesh_dict, lift_dict, mat_size = {}, {}, {}
    for mesh_one in mesh_set:
        mesh_key = ''
        if 'material' in mesh_one:
            mesh_key = mesh_one['material']
        if mesh_key not in material_dict:
            continue
        mesh_face, mesh_xyz, mesh_uv, mesh_area = [], [], [], 0
        if 'faces' in mesh_one:
            mesh_face = mesh_one['faces']
        if 'xyz' in mesh_one:
            mesh_xyz = mesh_one['xyz']
        if 'uv' in mesh_one:
            mesh_uv = mesh_one['uv']
        # cmp area
        mesh_len = int(len(mesh_face) / 3)
        mesh_lift = 0
        sx, sy = 1., 1.
        for mesh_idx in range(mesh_len):
            pts1_idx = mesh_face[mesh_idx * 3 + 0]
            pts2_idx = mesh_face[mesh_idx * 3 + 1]
            pts3_idx = mesh_face[mesh_idx * 3 + 2]
            if pts1_idx * 3 + 2 >= len(mesh_xyz) or pts1_idx * 2 + 1 >= len(mesh_uv):
                continue
            if pts2_idx * 3 + 2 >= len(mesh_xyz) or pts2_idx * 2 + 1 >= len(mesh_uv):
                continue
            if pts3_idx * 3 + 2 >= len(mesh_xyz) or pts3_idx * 2 + 1 >= len(mesh_uv):
                continue
            pts1_x, pts1_y, pts1_z = mesh_xyz[pts1_idx * 3 + 0], mesh_xyz[pts1_idx * 3 + 1], mesh_xyz[pts1_idx * 3 + 2]
            pts2_x, pts2_y, pts2_z = mesh_xyz[pts2_idx * 3 + 0], mesh_xyz[pts2_idx * 3 + 1], mesh_xyz[pts2_idx * 3 + 2]
            pts3_x, pts3_y, pts3_z = mesh_xyz[pts3_idx * 3 + 0], mesh_xyz[pts3_idx * 3 + 1], mesh_xyz[pts3_idx * 3 + 2]
            pts1_u, pts1_v = mesh_uv[pts1_idx * 2], mesh_uv[pts1_idx * 2 + 1]
            pts2_u, pts2_v = mesh_uv[pts2_idx * 2], mesh_uv[pts2_idx * 2 + 1]
            pts3_u, pts3_v = mesh_uv[pts3_idx * 2], mesh_uv[pts3_idx * 2 + 1]
            mesh_lift = max(pts1_y, pts2_y, pts3_y, mesh_lift)
            if abs(pts1_x - pts2_x) < 1e-8 and abs(pts1_x - pts3_x) < 1e-8:
                poly_sh = Polygon([(pts1_y, pts1_z), (pts2_y, pts2_z), (pts3_y, pts3_z)])
                mesh_area += poly_sh.area
                flag = cal_mat_size((pts1_y, pts1_z), (pts2_y, pts2_z), (pts3_y, pts3_z),
                                        (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                if flag[0]:
                    _, sx, sy = flag
            elif abs(pts1_y - pts2_y) < 1e-8 and abs(pts1_y - pts3_y) < 1e-8:
                poly_sh = Polygon([(pts1_x, pts1_z), (pts2_x, pts2_z), (pts3_x, pts3_z)])
                mesh_area += poly_sh.area
                flag = cal_mat_size((pts1_x, pts1_z), (pts2_x, pts2_z), (pts3_x, pts3_z),
                                      (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                if flag[0]:
                    _, sx, sy = flag
            elif abs(pts1_z - pts2_z) < 1e-8 and abs(pts1_z - pts3_z) < 1e-8:
                poly_sh = Polygon([(pts1_x, pts1_y), (pts2_x, pts2_y), (pts3_x, pts3_y)])
                mesh_area += poly_sh.area
                flag = cal_mat_size((pts1_x, pts1_y), (pts2_x, pts2_y), (pts3_x, pts3_y),
                                      (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                if flag[0]:
                    _, sx, sy = flag
            else:
                continue
        # add area
        if mesh_area <= 0:
            continue
        if mesh_key not in mesh_dict:
            mesh_dict[mesh_key] = mesh_area
        else:
            mesh_dict[mesh_key] += mesh_area
        lift_dict[mesh_key] = mesh_lift
        mat_size[mesh_key] = [sx, sy]
    # sort
    mesh_sort = []
    for mesh_key, mesh_val in mesh_dict.items():
        if mesh_key not in material_dict:
            continue
        lift_val = 0
        if mesh_key in lift_dict:
            lift_val = lift_dict[mesh_key]
        # val
        mesh_mat_old = material_dict[mesh_key]
        mesh_mat_add = {
            'jid': '',
            'texture_url': '',
            'color': [255, 255, 255],
            'colorMode': 'texture',
            'size': mat_size[mesh_key],
            'seam': False,
            'area': mesh_val,
            'lift': lift_val
        }
        if 'jid' in mesh_mat_old:
            mesh_mat_add['jid'] = mesh_mat_old['jid']
        if 'texture' in mesh_mat_old:
            mesh_mat_add['texture_url'] = mesh_mat_old['texture']
        if 'color' in mesh_mat_old and len(mesh_mat_old['color']) >= 3:
            mesh_mat_add['color'] = mesh_mat_old['color'][0:3]
        if len(mesh_mat_add['texture_url']) == 0:
            mesh_mat_add['colorMode'] = 'color'
        if 'UVTransform' in mesh_mat_old:
            mesh_mat_add['size'][0] *= 1./mesh_mat_old['UVTransform'][0]
            mesh_mat_add['size'][1] *= 1./mesh_mat_old['UVTransform'][4]
        # size seam
        if 'contentType' in mesh_mat_old:
            mesh_mat_add['seam'] = mesh_mat_old['contentType']
        # idx
        find_idx = -1
        for old_idx, old_val in enumerate(mesh_sort):
            if old_val['area'] < mesh_val:
                find_idx = old_idx
                break
        # add
        if find_idx >= 0:
            mesh_sort.insert(find_idx, mesh_mat_add)
        else:
            mesh_sort.append(mesh_mat_add)
    # type
    return mesh_sort


def group_wall_mesh(mesh_list_wall, material_dict):
    wall_list = []
    for mesh_one in mesh_list_wall:
        mesh_key = ''
        if 'material' in mesh_one:
            mesh_key = mesh_one['material']
        if mesh_key not in material_dict:
            continue
        mesh_face, mesh_xyz, mesh_uv, mesh_area = [], [], [], 0
        if 'faces' in mesh_one:
            mesh_face = mesh_one['faces']
        else:
            continue
        if 'xyz' in mesh_one:
            mesh_xyz = mesh_one['xyz']
        else:
            continue

        if 'uv' in mesh_one:
            mesh_uv = mesh_one['uv']
        mesh_xyz = np.reshape(mesh_xyz, [-1, 3])
        wall_base_height = np.min(mesh_xyz[:, 1])
        mesh_xz = mesh_xyz[:, [0, 2]]
        mesh_xyz = np.reshape(mesh_xyz, [-1])
        maxx = np.argmax(mesh_xz[:, 0])
        minx = np.argmin(mesh_xz[:, 0])
        if maxx == minx:
            maxy = np.argmax(mesh_xz[:, 1])
            miny = np.argmin(mesh_xz[:, 1])
            if maxy == miny:
                continue
            else:
                start_p = mesh_xz[miny]
                end_p = mesh_xz[maxy]
        else:
            start_p = mesh_xz[minx]
            end_p = mesh_xz[maxx]

        # cmp area
        mesh_len = int(len(mesh_face) / 3)
        mesh_lift = 0
        sx, sy = 1.0, 1.0
        for mesh_idx in range(mesh_len):
            pts1_idx = mesh_face[mesh_idx * 3 + 0]
            pts2_idx = mesh_face[mesh_idx * 3 + 1]
            pts3_idx = mesh_face[mesh_idx * 3 + 2]
            if pts1_idx * 3 + 2 >= len(mesh_xyz) or pts1_idx * 2 + 1 >= len(mesh_uv):
                continue
            if pts2_idx * 3 + 2 >= len(mesh_xyz) or pts2_idx * 2 + 1 >= len(mesh_uv):
                continue
            if pts3_idx * 3 + 2 >= len(mesh_xyz) or pts3_idx * 2 + 1 >= len(mesh_uv):
                continue
            pts1_x, pts1_y, pts1_z = mesh_xyz[pts1_idx * 3 + 0], mesh_xyz[pts1_idx * 3 + 1], mesh_xyz[pts1_idx * 3 + 2]
            pts2_x, pts2_y, pts2_z = mesh_xyz[pts2_idx * 3 + 0], mesh_xyz[pts2_idx * 3 + 1], mesh_xyz[pts2_idx * 3 + 2]
            pts3_x, pts3_y, pts3_z = mesh_xyz[pts3_idx * 3 + 0], mesh_xyz[pts3_idx * 3 + 1], mesh_xyz[pts3_idx * 3 + 2]
            pts1_u, pts1_v = mesh_uv[pts1_idx * 2], mesh_uv[pts1_idx * 2 + 1]
            pts2_u, pts2_v = mesh_uv[pts2_idx * 2], mesh_uv[pts2_idx * 2 + 1]
            pts3_u, pts3_v = mesh_uv[pts3_idx * 2], mesh_uv[pts3_idx * 2 + 1]
            mesh_lift = max(pts1_y, pts2_y, pts3_y, mesh_lift)
            if abs(pts1_x - pts2_x) < 1e-8 and abs(pts1_x - pts3_x) < 1e-8:
                poly_sh = Polygon([(pts1_y, pts1_z), (pts2_y, pts2_z), (pts3_y, pts3_z)])
                mesh_area += poly_sh.area
                flag = cal_mat_size((pts1_y, pts1_z), (pts2_y, pts2_z), (pts3_y, pts3_z),
                                      (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                if flag[0]:
                    _, sx, sy = flag
            elif abs(pts1_y - pts2_y) < 1e-8 and abs(pts1_y - pts3_y) < 1e-8:
                poly_sh = Polygon([(pts1_x, pts1_z), (pts2_x, pts2_z), (pts3_x, pts3_z)])
                mesh_area += poly_sh.area
                flag = cal_mat_size((pts1_x, pts1_z), (pts2_x, pts2_z), (pts3_x, pts3_z),
                                      (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                if flag[0]:
                    _, sx, sy = flag
            elif abs(pts1_z - pts2_z) < 1e-8 and abs(pts1_z - pts3_z) < 1e-8:
                poly_sh = Polygon([(pts1_x, pts1_y), (pts2_x, pts2_y), (pts3_x, pts3_y)])
                mesh_area += poly_sh.area
                flag = cal_mat_size((pts1_x, pts1_y), (pts2_x, pts2_y), (pts3_x, pts3_y),
                                      (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                if flag[0]:
                    _, sx, sy = flag
            else:
                continue
        # add area
        if mesh_area <= 0:
            continue

        mesh_mat = material_dict[mesh_key]
        mesh_mat_add = {
            'jid': '',
            'texture_url': '',
            'color': [255, 255, 255],
            'colorMode': 'texture',
            'size': [sx, sy],
            'seam': False,
            'wall': [np.array(start_p).tolist(), np.array(end_p).tolist()],
            'height': wall_base_height,
            'area': mesh_area
        }
        if 'jid' in mesh_mat:
            mesh_mat_add['jid'] = mesh_mat['jid']
        if 'texture' in mesh_mat:
            mesh_mat_add['texture_url'] = mesh_mat['texture']
        if 'color' in mesh_mat and len(mesh_mat['color']) >= 3:
            mesh_mat_add['color'] = mesh_mat['color'][0:3]
        if 'UVTransform' in mesh_mat:
            mesh_mat_add['size'][0] *= 1./mesh_mat['UVTransform'][0]
            mesh_mat_add['size'][1] *= 1./mesh_mat['UVTransform'][4]
        if len(mesh_mat_add['texture_url']) == 0:
            mesh_mat_add['colorMode'] = 'color'
        # size seam
        if 'contentType' in mesh_mat:
            mesh_mat_add['seam'] = mesh_mat['contentType']
        wall_list.append(mesh_mat_add)
    return wall_list


def compute_mesh(mesh_list_wall, mesh_list_ceiling, mesh_list_floor, mesh_list_pocket, mesh_list_baseboard, material_dict, room_info):
    material_data = {
        'id': '', 'type': '',
        'floor': [], 'wall': [],
        'ceiling': [],
        'win_pocket': [], 'door_pocket': [],
        'baseboard': [],
        'customized_ceiling': []
    }
    if 'id' in room_info:
        material_data['id'] = room_info['id']
    if 'type' in room_info:
        material_data['type'] = room_info['type']
    # wall TODO:
    # material_data['wall'] = group_mesh_material(mesh_list_wall, material_dict)
    material_data['wall'] = group_wall_mesh(mesh_list_wall, material_dict)
    # floor
    material_data['floor'] = group_mesh_material(mesh_list_floor, material_dict)
    material_data['ceiling'] = group_mesh_material(mesh_list_ceiling, material_dict)
    material_data['baseboard'] = group_mesh_material(mesh_list_baseboard, material_dict)

    # door window
    door_list, hole_list, window_list, baywindow_list = [], [], [], []
    if 'door' in room_info:
        door_list = room_info['door']
    if 'hole' in room_info:
        hole_list = room_info['hole']
    if 'window' in room_info:
        window_list = room_info['window']
    if 'baywindow' in room_info:
        baywindow_list = room_info['baywindow']
    # unit
    center_set_door, center_set_open = [], []
    for unit_set in [door_list, hole_list, window_list, baywindow_list]:
        for unit_one in unit_set:
            if len(unit_one) < 8:
                continue
            unit_x = (unit_one[0] + unit_one[2] + unit_one[4] + unit_one[6]) / 4
            unit_z = (unit_one[1] + unit_one[3] + unit_one[5] + unit_one[7]) / 4
            if unit_set in [door_list, hole_list]:
                center_set_door.append([unit_x, unit_z])
            elif unit_set in [window_list, baywindow_list]:
                center_set_open.append([unit_x, unit_z])
    # mesh
    mesh_door, mesh_open = [], []
    for mesh_one in mesh_list_pocket:
        if len(center_set_door) <= 0 and len(center_set_open) <= 0:
            break
        mesh_key = ''
        if 'material' in mesh_one:
            mesh_key = mesh_one['material']
        if mesh_key not in material_dict:
            continue
        mesh_face, mesh_xyz, mesh_uv, mesh_area = [], [], [], 0
        if 'faces' in mesh_one:
            mesh_face = mesh_one['faces']
        if 'xyz' in mesh_one:
            mesh_xyz = mesh_one['xyz']

        if 'uv' in mesh_one:
            mesh_uv = mesh_one['uv']
        # cmp rely
        mesh_len = int(len(mesh_face) / 3)
        for mesh_idx in range(mesh_len):
            pts1_idx = mesh_face[mesh_idx * 3 + 0]
            pts2_idx = mesh_face[mesh_idx * 3 + 1]
            pts3_idx = mesh_face[mesh_idx * 3 + 2]
            if pts1_idx * 3 + 2 >= len(mesh_xyz):
                continue
            if pts2_idx * 3 + 2 >= len(mesh_xyz):
                continue
            if pts3_idx * 3 + 2 >= len(mesh_xyz):
                continue
            pts1_x, pts1_y, pts1_z = mesh_xyz[pts1_idx * 3 + 0], mesh_xyz[pts1_idx * 3 + 1], mesh_xyz[pts1_idx * 3 + 2]
            pts2_x, pts2_y, pts2_z = mesh_xyz[pts2_idx * 3 + 0], mesh_xyz[pts2_idx * 3 + 1], mesh_xyz[pts2_idx * 3 + 2]
            pts3_x, pts3_y, pts3_z = mesh_xyz[pts3_idx * 3 + 0], mesh_xyz[pts3_idx * 3 + 1], mesh_xyz[pts3_idx * 3 + 2]
            mesh_x, mesh_z = (pts1_x + pts2_x + pts3_x) / 3, (pts1_z + pts2_z + pts3_z) / 3
            flag_door, flag_open = False, False
            if not flag_door and not flag_open:
                for center_one in center_set_door:
                    if abs(center_one[0] - mesh_x) + abs(center_one[1] - mesh_z) < 1.0:
                        flag_door = True
                        break
            if not flag_door and not flag_open:
                for center_one in center_set_open:
                    if abs(center_one[0] - mesh_x) + abs(center_one[1] - mesh_z) < 1.0:
                        flag_open = True
                        break
            if not flag_door and not flag_open and len(mesh_door) <= 0:
                flag_door = True
            if flag_door or flag_open:
                sx, sy = 1., 1.
                pts1_u, pts1_v = mesh_uv[pts1_idx * 2], mesh_uv[pts1_idx * 2 + 1]
                pts2_u, pts2_v = mesh_uv[pts2_idx * 2], mesh_uv[pts2_idx * 2 + 1]
                pts3_u, pts3_v = mesh_uv[pts3_idx * 2], mesh_uv[pts3_idx * 2 + 1]
                if abs(pts1_x - pts2_x) < 1e-8 and abs(pts1_x - pts3_x) < 1e-8:
                    poly_sh = Polygon([(pts1_y, pts1_z), (pts2_y, pts2_z), (pts3_y, pts3_z)])
                    mesh_area += poly_sh.area
                    flag = cal_mat_size((pts1_y, pts1_z), (pts2_y, pts2_z), (pts3_y, pts3_z),
                                          (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                    if flag[0]:
                        _, sx, sy = flag
                elif abs(pts1_y - pts2_y) < 1e-8 and abs(pts1_y - pts3_y) < 1e-8:
                    poly_sh = Polygon([(pts1_x, pts1_z), (pts2_x, pts2_z), (pts3_x, pts3_z)])
                    mesh_area += poly_sh.area
                    flag = cal_mat_size((pts1_x, pts1_z), (pts2_x, pts2_z), (pts3_x, pts3_z),
                                          (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                    if flag[0]:
                        _, sx, sy = flag
                elif abs(pts1_z - pts2_z) < 1e-8 and abs(pts1_z - pts3_z) < 1e-8:
                    poly_sh = Polygon([(pts1_x, pts1_y), (pts2_x, pts2_y), (pts3_x, pts3_y)])
                    mesh_area += poly_sh.area
                    flag = cal_mat_size((pts1_x, pts1_y), (pts2_x, pts2_y), (pts3_x, pts3_y),
                                          (pts1_u, pts1_v), (pts2_u, pts2_v), (pts3_u, pts3_v))
                    if flag[0]:
                        _, sx, sy = flag
                else:
                    continue
                mesh_mat_old = material_dict[mesh_key]
                mesh_mat_add = {
                    'jid': '',
                    'texture_url': '',
                    'color': [255, 255, 255],
                    'colorMode': 'texture',
                    'size': [sx, sy],
                    'seam': False,
                    'area': 0,
                    'lift': 0
                }
                if 'jid' in mesh_mat_old:
                    mesh_mat_add['jid'] = mesh_mat_old['jid']
                if 'texture' in mesh_mat_old:
                    mesh_mat_add['texture_url'] = mesh_mat_old['texture']
                if 'color' in mesh_mat_old and len(mesh_mat_old['color']) >= 3:
                    mesh_mat_add['color'] = mesh_mat_old['color'][0:3]
                if len(mesh_mat_add['texture_url']) == 0:
                    mesh_mat_add['colorMode'] = 'color'
                if 'UVTransform' in mesh_mat_old:
                    mesh_mat_add['size'][0] *= 1./mesh_mat_old['UVTransform'][0]
                    mesh_mat_add['size'][1] *= 1./mesh_mat_old['UVTransform'][4]
                # size seam
                if 'contentType' in mesh_mat_old:
                    mesh_mat_add['seam'] = mesh_mat_old['contentType']
                # add
                if flag_door:
                    mesh_door.append(mesh_mat_add)
                elif flag_open:
                    mesh_open.append(mesh_mat_add)
                break
    # type
    material_data['door_pocket'] = mesh_door
    material_data['win_pocket'] = mesh_open
    return material_data


