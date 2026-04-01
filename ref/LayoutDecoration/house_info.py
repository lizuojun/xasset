import copy
import numpy as np
import json
import os
from matplotlib import pyplot as plt
from LayoutDecoration.Base.math_util import find_pt_in_line
from LayoutDecoration.layout.elementRelation import ElementRelation

from LayoutDecoration.Base.recon_params import get_default_wall_info, ROOM_BUILD_TYPE

CHINESE_TYPE_CHANGE = \
    json.load(open(os.path.join(os.path.dirname(__file__), 'libs/furniture_refer_dict.json'), 'rb'), encoding='utf-8')[
        'category_chinese']
CHINESE_ID_TYPE_CHANGE = \
    json.load(open(os.path.join(os.path.dirname(__file__), 'libs/furniture_refer_dict.json'), 'rb'), encoding='utf-8')[
        'category_id']


def chinese_type_change(in_type):
    if in_type in CHINESE_TYPE_CHANGE:
        return CHINESE_TYPE_CHANGE[in_type]
    else:
        return ''


def get_category_id(in_type):
    if in_type in CHINESE_ID_TYPE_CHANGE:
        return CHINESE_ID_TYPE_CHANGE[in_type]
    else:
        return ''


class RoomData(object):
    def __init__(self, room_json, build_mesh=True):
        self.build_mesh = build_mesh
        self.area = room_json['area']
        self.floor_pts = [[room_json['floor'][2 * i], room_json['floor'][2 * i + 1]] for i in
                          range(len(room_json['floor']) // 2 - 1)]
        self.floor_wall_info = room_json['floor_wall_info']
        self.layout = []
        self.line_door_table = {}
        self.line_window_table = {}
        # self.line_hole_table = {}
        self.line_baywindow_table = {}

        self.door_list = []
        self.win_list = []

        self.room_id = room_json['id']
        self.room_type = room_json['type']
        if 'intersect' in room_json.keys():
            self.intersect_wall_inds = self.find_intersect_wall(room_json['intersect']['floor'])
        else:
            self.intersect_wall_inds = []
        self.room_json = {}
        # self.room_info = {'id': room_json['id'], 'type': room_json['type'], 'area': room_json['area'],
        #                   'light': {'SpotLight': [], 'StripLight': [], 'FurnitureLight': [], 'AreaLight': [],
        #                             'outdoor_scene': 'sea_sky'},
        #                   'customized_mesh': []}
        alias = room_json['type'] + '-' + room_json['id'].split('-')[-1]
        height = room_json['height'] if 'height' in room_json else 2.8
        if height < 2:
            height = 2.8
        self.room_info = {
            'id': room_json['id'],
            'height': height,
            'alias': room_json['alias'] if 'alias' in room_json else alias,
            'type': room_json['type'], 'area': room_json['area'], 'floor_pts': self.floor_pts,
            'Floor': [],
            'Wall': [],
            'Ceiling': [],
            'Mesh': [],
            'Door': [],
            'Hole': [],
            'Window': [],
            "BaseBoard": [],
            'CustomizedCeiling': [],
            'Light': [],
            'Kitchen': [],
            'BgWall': [],
            'ParametricModel': [],
            'Extension': {}
        }
        self.floor_node = None
        self.ceiling_node = None
        self.wall_node = None
        self.load(copy.deepcopy(room_json))
        self.config_room()

    def find_intersect_wall(self, intersect):
        if len(intersect) == 0:
            return []
        intersect_pts = np.array(intersect).reshape([-1, 2, 2])
        pts = np.array(self.floor_pts).reshape([-1, 2])
        intersect_wall = []
        for i in range(len(pts)):
            start = pts[i, :]
            end = pts[(i + 1) % len(pts), :]
            for inter_pt in intersect_pts:
                if (np.linalg.norm(inter_pt[0, :] - start) < 1e-3 and np.linalg.norm(inter_pt[1, :] - end) < 1e-3) \
                        or (
                        np.linalg.norm(inter_pt[1, :] - start) < 1e-3 and np.linalg.norm(inter_pt[0, :] - end) < 1e-3):
                    intersect_wall.append(i)
        return intersect_wall

    def load(self, room_json):
        self.room_json = room_json

        if 'door_info' not in room_json:
            room_json['door_info'] = []
        if 'window_info' not in room_json:
            room_json['window_info'] = []
        if 'hole_info' not in room_json:
            room_json['hole_info'] = []
        if 'baywindow_info' not in room_json:
            room_json['baywindow_info'] = []

        # 找到墙对应的门、窗、洞
        for start_idx in range(0, len(self.floor_pts)):
            if start_idx in self.intersect_wall_inds:
                continue
            start_pt = self.floor_pts[start_idx]
            end_pt = self.floor_pts[(start_idx + 1) % len(self.floor_pts)]

            for door_idx, door_info in enumerate(room_json['door_info']):
                if len(door_info['pts']) == 0:
                    continue
                near_pts = find_pt_in_line(door_info['pts'], [start_pt, end_pt])
                if len(near_pts) == 0:
                    continue
                # 检查位于哪一段墙上
                related_wall_ind = -1
                for wall_ind, wall_info in enumerate(self.floor_wall_info[start_idx]):
                    start_pt_wall = wall_info['inner_pts'][0]
                    end_pt_wall = wall_info['inner_pts'][1]
                    near_pts_on_wall = find_pt_in_line(door_info['pts'], [start_pt_wall, end_pt_wall])
                    if len(near_pts_on_wall) > 0:
                        related_wall_ind = wall_ind
                        break
                if related_wall_ind < 0:
                    print('invalid door pts')
                    continue
                door_pts = np.array(door_info['pts']).reshape([-1, 2])
                l1 = np.linalg.norm(door_pts[0, :] - door_pts[1, :])
                l2 = np.linalg.norm(door_pts[0, :] - door_pts[2, :])
                l3 = np.linalg.norm(door_pts[0, :] - door_pts[3, :])

                door_depth = min(min(l1, l2), l3)
                door_info_table = {'floor_ind': start_idx,
                                   'wall_ind': related_wall_ind,
                                   'ind': door_idx,
                                   'wall_pts': near_pts,
                                   'to': door_info['to'],
                                   'depth': door_depth,
                                   'to_type': door_info['to_type'],
                                   'room_type': self.room_type,
                                   'hole': False
                                   }
                if start_idx in self.line_door_table:
                    self.line_door_table[start_idx] += [door_info_table]
                else:
                    self.line_door_table[start_idx] = [door_info_table]
        for start_idx in range(0, len(self.floor_pts)):
            if start_idx in self.intersect_wall_inds:
                continue
            start_pt = self.floor_pts[start_idx]
            end_pt = self.floor_pts[(start_idx + 1) % len(self.floor_pts)]

            for hole_idx, hole_info in enumerate(room_json['hole_info']):
                if len(hole_info['pts']) == 0:
                    continue
                near_pts = find_pt_in_line(hole_info['pts'], [start_pt, end_pt])
                if len(near_pts) == 0:
                    continue
                # 检查位于哪一段墙上
                related_wall_ind = -1
                for wall_ind, wall_info in enumerate(self.floor_wall_info[start_idx]):
                    start_pt_wall = wall_info['inner_pts'][0]
                    end_pt_wall = wall_info['inner_pts'][1]
                    near_pts_on_wall = find_pt_in_line(hole_info['pts'], [start_pt_wall, end_pt_wall])
                    if len(near_pts_on_wall) > 0:
                        related_wall_ind = wall_ind
                        break
                if related_wall_ind < 0:
                    print('invalid hole pts')
                    continue
                hole_pts = np.array(hole_info['pts']).reshape([-1, 2])
                l1 = np.linalg.norm(hole_pts[0, :] - hole_pts[1, :])
                l2 = np.linalg.norm(hole_pts[0, :] - hole_pts[2, :])
                l3 = np.linalg.norm(hole_pts[0, :] - hole_pts[3, :])

                door_depth = min(min(l1, l2), l3)
                hole_info_table = {'floor_ind': start_idx,
                                   'wall_ind': related_wall_ind,
                                   'ind': hole_idx,
                                   'wall_pts': near_pts,
                                   'to': hole_info['to'],
                                   'depth': door_depth,
                                   'to_type': hole_info['to_type'],
                                   'room_type': self.room_type,
                                   'hole': True
                                   }
                if start_idx in self.line_door_table:
                    self.line_door_table[start_idx].append(hole_info_table)
                else:
                    self.line_door_table[start_idx] = [hole_info_table]

        for start_idx in range(0, len(self.floor_pts)):
            if start_idx in self.intersect_wall_inds:
                continue
            start_pt = self.floor_pts[start_idx]
            end_pt = self.floor_pts[(start_idx + 1) % len(self.floor_pts)]

            for win_idx, win_info in enumerate(room_json['window_info']):
                if len(win_info['pts']) == 0:
                    continue
                near_pts = find_pt_in_line(win_info['pts'], [start_pt, end_pt])
                if len(near_pts) == 0:
                    continue
                # 检查位于哪一段墙上
                related_wall_ind = -1
                for wall_ind, wall_info in enumerate(self.floor_wall_info[start_idx]):
                    start_pt_wall = wall_info['inner_pts'][0]
                    end_pt_wall = wall_info['inner_pts'][1]
                    near_pts_on_wall = find_pt_in_line(win_info['pts'], [start_pt_wall, end_pt_wall])
                    if len(near_pts_on_wall) > 0:
                        related_wall_ind = wall_ind
                        break
                if related_wall_ind < 0:
                    print('invalid window pts')
                    continue
                win_pts = np.array(win_info['pts']).reshape([-1, 2])
                l1 = np.linalg.norm(win_pts[0, :] - win_pts[1, :])
                l2 = np.linalg.norm(win_pts[0, :] - win_pts[2, :])
                l3 = np.linalg.norm(win_pts[0, :] - win_pts[3, :])

                door_depth = min(min(l1, l2), l3)
                win_info_table = {'floor_ind': start_idx,
                                   'wall_ind': related_wall_ind,
                                   'ind': win_idx,
                                  'wall_pts': near_pts,
                                  'to': win_info['to'],
                                  'depth': door_depth,
                                  'to_type': win_info['to_type'],
                                  'room_type': self.room_type,
                                  'height': win_info['height'],
                                  'baywindow': False
                                  }
                if start_idx in self.line_window_table:
                    self.line_window_table[start_idx].append(win_info_table)
                else:
                    self.line_window_table[start_idx] = [win_info_table]
        for start_idx in range(0, len(self.floor_pts)):
            if start_idx in self.intersect_wall_inds:
                continue
            start_pt = self.floor_pts[start_idx]
            end_pt = self.floor_pts[(start_idx + 1) % len(self.floor_pts)]

            for win_idx, win_info in enumerate(room_json['baywindow_info']):
                if len(win_info['pts']) == 0:
                    continue
                bb_min = np.min(np.reshape(win_info['pts'], [-1, 2]), axis=0)
                bb_max = np.max(np.reshape(win_info['pts'], [-1, 2]), axis=0)
                bbox = [[bb_min[0], bb_min[1]], [bb_min[0], bb_max[1]], [bb_max[0], bb_max[1]], [bb_max[0], bb_min[1]]]
                near_pts = find_pt_in_line(bbox, [start_pt, end_pt])
                if len(near_pts) == 0:
                    continue
                # 检查位于哪一段墙上
                related_wall_ind = -1
                for wall_ind, wall_info in enumerate(self.floor_wall_info[start_idx]):
                    start_pt_wall = wall_info['inner_pts'][0]
                    end_pt_wall = wall_info['inner_pts'][1]
                    near_pts_on_wall = find_pt_in_line(win_info['pts'], [start_pt_wall, end_pt_wall])
                    if len(near_pts_on_wall) > 0:
                        related_wall_ind = wall_ind
                        break
                if related_wall_ind < 0:
                    print('invalid baywindow pts')
                    continue
                win_pts = np.array(bbox).reshape([-1, 2])
                l1 = np.linalg.norm(win_pts[0, :] - win_pts[1, :])
                l2 = np.linalg.norm(win_pts[0, :] - win_pts[2, :])
                l3 = np.linalg.norm(win_pts[0, :] - win_pts[3, :])

                door_depth = min(min(l1, l2), l3)
                door_depth = 0.24
                win_info_table = {'floor_ind': start_idx,
                                   'wall_ind': related_wall_ind,
                                   'ind': win_idx,
                                  'wall_pts': near_pts,
                                  'to': win_info['to'],
                                  'depth': door_depth,
                                  'to_type': win_info['to_type'],
                                  'room_type': self.room_type,
                                  'height': win_info['height'],
                                  'baywindow': True
                                  }
                if start_idx in self.line_window_table:
                    self.line_window_table[start_idx].append(win_info_table)
                else:
                    self.line_window_table[start_idx] = [win_info_table]

    def config_room(self):
        # floor config
        mesh_uid_str = '%s_Floor_%d' % (self.room_id, 0)
        floor_list = [
            {
                'name': mesh_uid_str,
                'type': self.room_type,
                'layout_pts': self.floor_pts,
                'related': {},
                'material': {}
            }
        ]

        # ceiling config
        mesh_uid_str = '%s_Ceiling_%d' % (self.room_id, 0)
        ceiling_list = [
            {
                'name': mesh_uid_str,
                'type': self.room_type,
                'layout_pts': self.floor_pts,
                'related': {},
                'material': {}
            }
        ]

        # wall 及附属的门窗踢脚线 config
        build_params = {'param_main_wall': get_default_wall_info()}
        # if self.room_type == 'Balcony':
        #     line_window_table = {}
        #     build_params['param_main_wall']['no_door_wall_height'] = 1.0
        # else:
        line_window_table = self.line_window_table

        mesh_uid_str = '%s_WallInner_base' % self.room_id
        self.wall_node = ElementRelation(self.room_type, self.room_id, mesh_uid_str, self.floor_pts,
                                         self.floor_wall_info, self.line_door_table, line_window_table,
                                         build_params=build_params, skip_wall_inds=self.intersect_wall_inds)

        # self.room_info['WallInner'] = self.wall_node
        element_info = self.wall_node.element_info
        wall_list = []
        door_list = []
        window_list = []
        baseboard_list = []
        for floor_idx, wall in element_info.items():
            wall_list.append(
                {
                    'name': floor_idx,
                    'type': self.room_type,
                    'mesh_id': mesh_uid_str,
                    'layout_pts': [self.floor_pts[floor_idx], self.floor_pts[(floor_idx + 1) % len(self.floor_pts)]],
                    'normal': wall['WallInner'][0]['offset_dir'],
                    'height': wall['WallInner'][0]['height'],
                    'segments': [v['segment'] for v in wall['WallInner']],
                    'related': {},
                    'functional': {},
                    'material': {}
                }
            )
            for door in wall['Door']:
                mesh_uid_str = '%s_Door_%d_%d_%d' % (self.room_id, door['floor_ind'], door['wall_ind'], door['ind'])
                door_list.append(
                    {
                        'name': mesh_uid_str,
                        'type': door['type'],
                        'base_room_id': self.room_id,
                        'base_room_type': self.room_type,
                        'target_room_id': door['to'],
                        'target_room_type': door['to_type'],
                        'length': door['length'],
                        'depth': door['depth'],
                        'height': door['height'],
                        'layout_pts': door['wall_pts'],
                        'normal': door['normal'],
                        'is_hole': door['hole'],
                        'obj_info': {
                            "pos": door['pos'],
                            "rot": door['rot'],
                            "scale": [1, 1, 1],
                            "jid": "",
                        },
                        'related': {
                            'Wall': floor_idx,
                            'Segment':  door['wall_ind']
                        },
                        'material': {}
                    }
                )
            for window in wall['Window']:
                mesh_uid_str = '%s_Window_%d_%d_%d' % (self.room_id, window['floor_ind'], window['wall_ind'], window['ind'])
                window_list.append(
                    {
                        'name': mesh_uid_str,
                        'type': window['type'],
                        'base_room_id': self.room_id,
                        'base_room_type': self.room_type,
                        'target_room_id': window['to'],
                        'target_room_type': window['to_type'],
                        'length': window['length'],
                        'depth': window['depth'],
                        'top': window['top'],
                        'bottom': window['bottom'],
                        'height': window['top'] - window['bottom'],
                        'layout_pts': window['wall_pts'],
                        'normal': window['normal'],
                        'obj_info': {
                            "pos": window['pos'],
                            "rot": window['rot'],
                            "scale": [1, 1, 1],
                            "jid": "",
                        },
                        'related': {
                            'Wall': floor_idx,
                            'Segment': window['wall_ind']
                        },
                        'material': {}
                    }
                )

            for baseboard in wall['BaseBoard']:
                mesh_uid_str = '%s_BaseBoard_%d_%d_%d' % (self.room_id, baseboard['floor_ind'],
                                                          baseboard['wall_ind'], baseboard['line_ind'])
                baseboard_list.append({
                    "name": mesh_uid_str,
                    "layout_pts": [baseboard['start'], baseboard['end']],
                    "connect_type": baseboard['connect_type'],
                    "normal": baseboard['normal'],
                    'related': {
                        'Wall': floor_idx,
                        'Segment': baseboard['wall_ind']
                    },
                    'material': {}
                })

        wall_list.sort(key=lambda x: x['name'])

        self.room_info['Floor'] = floor_list
        self.room_info['Ceiling'] = ceiling_list
        self.room_info['Wall'] = wall_list
        self.room_info['Door'] = door_list
        self.room_info['Window'] = window_list
        self.room_info['BaseBoard'] = baseboard_list

    def add_layout(self, group_list):
        self.layout = copy.deepcopy(group_list)

    def get_scene_info(self):
        out_info_json = {'room_floor': copy.deepcopy(self.floor_pts),
                         'area': self.area, 'seed': [], 'furniture': [],
                         'door_info': copy.deepcopy(self.room_json['door_info']),
                         'window_info': copy.deepcopy(self.room_json['window_info']),
                         'baywindow_info': copy.deepcopy(self.room_json['baywindow_info']),
                         'hole_info': copy.deepcopy(self.room_json['hole_info']),
                         'id': self.room_id}
        out_info_json['room_floor'].append(out_info_json['room_floor'][0])
        fur_list = []
        seed_list = []
        if len(self.layout) > 0:
            for group in self.layout:
                for obj in group['obj_list']:
                    if 'type' not in obj:
                        cat = ''
                    else:
                        cat = chinese_type_change(obj['type'])
                    cat_id = get_category_id(cat)
                    fur_list.append({'jid': obj['id'], 'category': cat,
                                     'category_id': cat_id, 'size': {'xLen': obj['size'][0],
                                                                     'yLen': obj['size'][1],
                                                                     'zLen': obj['size'][2]},
                                     "scale": obj['scale'], "pos": obj['position'],
                                     "rot": obj['rotation'], "role": group['type'] + '_' + obj['role']
                                     })
                    if obj['role'] == 'sofa' and group['type'] == 'Meeting' and self.room_type in ['LivingRoom',
                                                                                                   'LivingDiningRoom']:
                        seed_list.append({'jid': obj['id'], 'category': cat,
                                          'category_id': cat_id})
                    if obj['role'] == 'table' and group['type'] == 'Dining' and self.room_type in ['DiningRoom',
                                                                                                   'LivingDiningRoom']:
                        seed_list.append({'jid': obj['id'], 'category': cat,
                                          'category_id': cat_id})
                    if obj['role'] == 'bed' and group['type'] == 'Bed':
                        seed_list.append({'jid': obj['id'], 'category': cat,
                                          'category_id': cat_id})

        if 'kitchen' in self.room_info:
            for obj in self.room_info['kitchen']:
                if obj['type'] in ['wall_cabinet', 'floor_cabinet', 'fridge', 'sink']:
                    fur_list.append(
                        {
                            'jid': obj['jid'],
                            'category': '橱柜',
                            'category_id': '9f5e1d30-853b-4b3d-b70d-68294190bc54',
                            'size': {'xLen': obj['size'][0], 'yLen': obj['size'][1], 'zLen': obj['size'][2]},
                            "scale": obj['scale'], "pos": obj['pos'],
                            "rot": obj['rot'], "role": obj['type'] + '_' + obj['type']
                        })
        out_info_json['furniture'] = fur_list
        out_info_json['seed'] = seed_list
        return out_info_json


class HouseData(object):
    def __init__(self, house_json, debug_mode=False):
        self.house_info = {
            'id': '' if 'id' not in house_json else house_json['id'],
            'global_light_params': {
                'outdoor_scene': 'sea_sky'
            },
            'rooms': {}
        }

        self.type_table = {'LivingDiningRoom': [], 'MasterBedroom': [], 'Bathroom': [], 'Balcony': [], 'Kitchen': [],
                           'Library': [], 'KidsRoom': []}
        self.room_table = {}

        assert 'room' in house_json
        if debug_mode:
            temp_folder = os.path.join(os.path.dirname(__file__), 'temp/')
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            house_id = house_json['id']
            folder = os.path.join(temp_folder, house_id)
            if not os.path.exists(folder):
                os.makedirs(folder)
        # if len(house_json['room']) > 0 and 'wall_info' in house_json['room'][0]:
        #     self.get_wall_info_hsf(house_json, debug_mode=debug_mode)
        # else:
        if not self.get_wall_info(house_json, debug_mode):
            self.get_default_wall_info(house_json)
        for room_info in house_json['room']:
            # if room_info['type'] not in ['LivingDiningRoom', 'Balcony']:
            #     continue
            for door in room_info['door_info']:
                door_to_room = [i for i in house_json['room'] if i['id'] == door['to']]
                if len(door_to_room) == 0:
                    if 'link' in door:
                        door['to_type'] = door['link']
                    else:
                        door['to_type'] = ''
                else:
                    door['to_type'] = door_to_room[0]['type']
            for win in room_info['window_info']:
                win_to_room = [i for i in house_json['room'] if i['id'] == win['to']]
                if len(win_to_room) == 0:
                    if 'link' in win:
                        win['to_type'] = win['link']
                    else:
                        win['to_type'] = ''
                else:
                    win['to_type'] = win_to_room[0]['type']
            for win in room_info['baywindow_info']:
                win_to_room = [i for i in house_json['room'] if i['id'] == win['to']]
                if len(win_to_room) == 0:
                    if 'link' in win:
                        win['to_type'] = win['link']
                    else:
                        win['to_type'] = ''
                else:
                    win['to_type'] = win_to_room[0]['type']
            for hole in room_info['hole_info']:
                hole_to_room = [i for i in house_json['room'] if i['id'] == hole['to']]
                if len(hole_to_room) == 0:
                    if 'link' in hole:
                        hole['to_type'] = hole['link']
                    else:
                        hole['to_type'] = ''
                else:
                    hole['to_type'] = hole_to_room[0]['type']
            if ROOM_BUILD_TYPE[room_info['type']] in self.type_table:
                self.type_table[ROOM_BUILD_TYPE[room_info['type']]].append(room_info['id'])
                self.room_table[room_info['id']] = RoomData(room_info)
                self.house_info['rooms'][room_info['id']] = self.room_table[room_info['id']].room_info

    # def build_mesh(self):
    #     for room_id in self.room_table.keys():
    #         self.room_table[room_id].recon_mesh()
    #         self.house_info['rooms'][room_id] = self.room_table[room_id].room_info

    def get_wall_info(self, house_json, debug_mode=False):

        if 'mid_wall' not in house_json:
            self.get_default_wall_info(house_json)
            return

        mid_walls = house_json['mid_wall']['wall_ind']
        mid_wall_pts = house_json['mid_wall']['wall_pts']
        if debug_mode:

            plt.figure()
            plt.axis('equal')

            # draw walls
            for room_info in house_json['room']:
                floor_pts = [[round(room_info['floor'][2 * i], 3), round(room_info['floor'][2 * i + 1], 3)] for i in
                             range(len(room_info['floor']) // 2 )]
                plt.plot(np.array(floor_pts)[:, 0], np.array(floor_pts)[:, 1])
            for wall in mid_walls:
                plt.plot([mid_wall_pts[wall[0]][0], mid_wall_pts[wall[1]][0]],
                         [mid_wall_pts[wall[0]][1], mid_wall_pts[wall[1]][1]])
                plt.text(mid_wall_pts[wall[0]][0], mid_wall_pts[wall[0]][1], str(wall[0]))
                plt.text(mid_wall_pts[wall[1]][0], mid_wall_pts[wall[1]][1], str(wall[1]))
            save_path = os.path.join(os.path.dirname(__file__), 'temp/%s/mid_wall_ind.png' % house_json['id'])
            plt.savefig(save_path)
            # plt.show()

        house_walls = dict([('%d_%d' % tuple(sorted(v)), {'mid_pts': [],
                                                          'inner_pts': [],
                                                          'outer_pts': [],
                                                          'mid_ind': [],
                                                          'norm': [],
                                                          'outer_wall': False}
                             ) for v in mid_walls])

        for room_info in house_json['room']:
            floor_pts = [[round(room_info['floor'][2 * i], 3), round(room_info['floor'][2 * i + 1], 3)] for i in
                         range(len(room_info['floor']) // 2 - 1)]
            floor_edge_to_mid_wall_dict = {}
            for i in range(len(floor_pts)):
                # 确定内墙点关联中线点
                prev = floor_pts[(i - 1) % len(floor_pts)]
                prev_mid_inds = self.get_closest_mid_pts(prev, mid_wall_pts)

                start = floor_pts[i]
                start_mid_inds = self.get_closest_mid_pts(start, mid_wall_pts)
                end = floor_pts[(i + 1) % len(floor_pts)]
                end_mid_inds = self.get_closest_mid_pts(end, mid_wall_pts)

                next = floor_pts[(i + 2) % len(floor_pts)]
                next_mid_inds = self.get_closest_mid_pts(next, mid_wall_pts)

                # prev到start
                inner_vec = np.array(start) - np.array(prev)
                prev_start_pair, _ = self.get_mid_inds(inner_vec, prev_mid_inds, start_mid_inds, mid_wall_pts, mid_walls)
                start_mid_inds_candidate = list(set([i[1] for i in prev_start_pair]))

                # next到end
                inner_vec = np.array(next) - np.array(end)
                end_next_pair, _ = self.get_mid_inds(inner_vec, end_mid_inds, next_mid_inds, mid_wall_pts, mid_walls)
                end_mid_inds_candidate = list(set([i[0] for i in end_next_pair]))

                # start到end
                inner_vec = np.array(end) - np.array(start)
                start_end_pair, mid_inter_inds_list = self.get_mid_inds(inner_vec, start_mid_inds_candidate,
                                                                        end_mid_inds_candidate,
                                                                        mid_wall_pts, mid_walls)
                # print(start_end_pair)
                if len(start_end_pair) != 1 or (len(start_end_pair) == 1 and start_end_pair[0][0] == start_end_pair[0][1]):
                    floor_edge_to_mid_wall_dict[i] = [{'mid_pts': [],
                                                       'mid_ind': [],
                                                       'inner_pts': [start, end],
                                                       'wall_name': '',
                                                       'depth': 0.,
                                                       'depth_bias_pt': []}]
                    if not(len(start_mid_inds) == 1 and len(end_mid_inds) == 1 and end_mid_inds == start_mid_inds):
                        print('warning: match mid-wall pts for room %s' % room_info['id'])
                        print(start_mid_inds, end_mid_inds, start_end_pair)
                        # for tem_i in range(len(floor_pts)):
                        #     start = floor_pts[tem_i]
                        #     end = floor_pts[(tem_i + 1) % len(floor_pts)]
                        #     floor_edge_to_mid_wall_dict[tem_i] = [{'mid_pts': [],
                        #                                            'mid_ind': [],
                        #                                            'inner_pts': [start, end],
                        #                                            'wall_name': '',
                        #                                            'depth': 0.,
                        #                                            'depth_bias_pt': []}]
                        return False

                    continue
                start_mid_ind, end_mid_ind = start_end_pair[0]
                mid_inter_inds = mid_inter_inds_list[0]
                # norm
                mid_wall_vec = np.array(mid_wall_pts[end_mid_ind]) - np.array(mid_wall_pts[start_mid_ind])
                norm = [-mid_wall_vec[1], mid_wall_vec[0]]
                norm = norm / np.linalg.norm(norm)
                if np.dot(norm, np.array(start) - np.array(mid_wall_pts[start_mid_ind])) < 0:
                    norm = - norm
                half_depth = abs(np.cross(np.array(start) - np.array(mid_wall_pts[start_mid_ind]), mid_wall_vec) / np.linalg.norm(
                    mid_wall_vec))
                dis_norm = norm * half_depth

                if len(mid_inter_inds) == 2:
                    corresponding_mid_wall = '%d_%d' % tuple(sorted([start_mid_ind, end_mid_ind]))
                    inner_pts = [start, end]
                    if len(house_walls[corresponding_mid_wall]['mid_ind']) > 0:
                        if [start_mid_ind, end_mid_ind] != house_walls[corresponding_mid_wall]['mid_ind']:
                            inner_pts = [end, start]
                    else:
                        house_walls[corresponding_mid_wall]['mid_pts'] = [mid_wall_pts[start_mid_ind],
                                                                          mid_wall_pts[end_mid_ind]]
                        house_walls[corresponding_mid_wall]['mid_ind'] = [start_mid_ind, end_mid_ind]

                    house_walls[corresponding_mid_wall]['inner_pts'].append(inner_pts)
                    house_walls[corresponding_mid_wall]['norm'].append(dis_norm.tolist())
                    floor_edge_to_mid_wall_dict[i] = [{'mid_pts': [mid_wall_pts[start_mid_ind],
                                                                   mid_wall_pts[end_mid_ind]],
                                                       'mid_ind': [start_mid_ind, end_mid_ind],
                                                       'inner_pts': [start, end],
                                                       'wall_name': corresponding_mid_wall,
                                                       'depth': half_depth * 2,
                                                       'depth_bias_pt': []}]
                else:
                    # 内墙轮廓点
                    inner_inter_pts = [start]
                    wall_names = []
                    for j in range(1, len(mid_inter_inds)):
                        if j < len(mid_inter_inds) - 1:
                            p = (np.array(mid_wall_pts[mid_inter_inds[j]]) + dis_norm).tolist()
                            inner_inter_pts.append(p)
                            end_pt = inner_inter_pts[j]
                        else:
                            end_pt = end

                        corresponding_mid_wall = '%d_%d' % tuple(sorted([mid_inter_inds[j - 1], mid_inter_inds[j]]))

                        inner_pts = [inner_inter_pts[j - 1], end_pt]
                        if len(house_walls[corresponding_mid_wall]['mid_ind']) > 0:
                            if [mid_inter_inds[j - 1], mid_inter_inds[j]] != house_walls[corresponding_mid_wall]['mid_ind']:
                                inner_pts = [end_pt, inner_inter_pts[j - 1]]
                        else:
                            house_walls[corresponding_mid_wall]['mid_pts'] = [mid_wall_pts[mid_inter_inds[j - 1]],
                                                                              mid_wall_pts[mid_inter_inds[j]]]
                            house_walls[corresponding_mid_wall]['mid_ind'] = [mid_inter_inds[j - 1], mid_inter_inds[j]]
                        house_walls[corresponding_mid_wall]['inner_pts'].append(inner_pts)

                        house_walls[corresponding_mid_wall]['norm'].append(dis_norm.tolist())
                        wall_names.append(corresponding_mid_wall)

                    inner_inter_pts.append(end)
                    floor_edge_to_mid_wall_dict[i] = [{'mid_pts': [mid_wall_pts[mid_inter_inds[ind]],
                                                                   mid_wall_pts[mid_inter_inds[ind + 1]]],
                                                       'mid_ind': [mid_inter_inds[ind], mid_inter_inds[ind + 1]],
                                                       'inner_pts': [inner_inter_pts[ind], inner_inter_pts[ind + 1]],
                                                       'wall_name': wall_names[ind],
                                                       'depth': half_depth * 2,
                                                       'depth_bias_pt': []} for ind in
                                                      range(len(mid_inter_inds) - 1)]

            # 添加变厚度点标签
            for i in range(len(floor_pts)):
                floor_to_wall = floor_edge_to_mid_wall_dict[i]
                if len(floor_to_wall) == 1 and len(floor_to_wall[0]['mid_ind']) == 0:
                    if floor_edge_to_mid_wall_dict[(i - 1) % len(floor_pts)][-1]['depth'] < floor_edge_to_mid_wall_dict[(i + 1) % len(floor_pts)][0]['depth']:
                        floor_edge_to_mid_wall_dict[(i + 1) % len(floor_pts)][0]['depth_bias_pt'].append(0)
                    else:
                        floor_edge_to_mid_wall_dict[(i - 1) % len(floor_pts)][-1]['depth_bias_pt'].append(1)
            room_info['floor_wall_info'] = floor_edge_to_mid_wall_dict

        # out wall detect
        wall_keys = list(house_walls.keys())
        for wall_name in wall_keys:
            wall_info = house_walls[wall_name]
            if len(wall_info['mid_ind']) == 0:
                house_walls.pop(wall_name)
            if len(wall_info['inner_pts']) == 1:
                wall_info['outer_wall'] = True
            else:
                wall_info['outer_wall'] = False

        # 建外墙
        used_wall_list = []
        all_outer_walls = []
        while True:
            sorted_outer_wall_name_list = []
            end = None
            while True:
                break_flag = False
                for wall_name_candidate, wall_info_candidate in house_walls.items():
                    if wall_name_candidate in used_wall_list or not wall_info_candidate['outer_wall']:
                        continue
                    if end is None:
                        end = wall_name_candidate.split('_')[1]
                        used_wall_list.append(wall_name_candidate)
                        sorted_outer_wall_name_list.append([wall_name_candidate, int(end)])

                    wall_start_end_list = wall_name_candidate.split('_')
                    if wall_name_candidate not in used_wall_list and end in wall_start_end_list:
                        end = wall_start_end_list[0] if wall_start_end_list[1] == end else wall_start_end_list[1]
                        used_wall_list.append(wall_name_candidate)
                        sorted_outer_wall_name_list.append([wall_name_candidate, int(end)])
                        break_flag = True
                        break
                if not break_flag:
                    break
            if len(sorted_outer_wall_name_list) == 0:
                break
            all_outer_walls.append(sorted_outer_wall_name_list)

        # 膨胀外墙
        for sorted_outer_wall_name_list in all_outer_walls:
            outer_wall_pts = []
            for i in range(len(sorted_outer_wall_name_list)):
                outer_wall_name, end_pt_ind = sorted_outer_wall_name_list[i]
                next_outer_wall_name, _ = sorted_outer_wall_name_list[(i + 1) % len(sorted_outer_wall_name_list)]

                connected_pt = mid_wall_pts[end_pt_ind]
                cur_wall = house_walls[outer_wall_name]['mid_pts']
                cur_norm = -np.array(house_walls[outer_wall_name]['norm'][0])

                next_wall = house_walls[next_outer_wall_name]['mid_pts']
                next_norm = -np.array(house_walls[next_outer_wall_name]['norm'][0])

                if abs(np.dot(cur_norm, next_norm) / np.linalg.norm(cur_norm) / np.linalg.norm(next_norm)) > 0.99:
                    cross_pt = (np.array(connected_pt) + cur_norm).tolist()
                    if np.linalg.norm(cur_norm - next_norm) > 1e-2:
                        cross_pt = (cross_pt, (np.array(connected_pt) + next_norm).tolist())
                else:
                    # 求直线交点
                    translated_cur_wall = np.array(cur_wall) + cur_norm
                    translated_next_wall = np.array(next_wall) + next_norm
                    alpha = 1e-10
                    k1 = (translated_cur_wall[0, 0] - translated_cur_wall[1, 0]) / (translated_cur_wall[0, 1] - translated_cur_wall[1, 1] + alpha)
                    k2 = (translated_next_wall[0, 0] - translated_next_wall[1, 0]) / (translated_next_wall[0, 1] - translated_next_wall[1, 1] + alpha)

                    intersect_x = (translated_next_wall[1, 1] - translated_cur_wall[1, 1] + 1. / (k1 + alpha) * translated_cur_wall[1, 0] - 1. / (k2 + alpha) * translated_next_wall[1, 0]) / (1. / (k1 + alpha) - 1. / (k2 + alpha) + alpha)
                    intersect_y = (translated_next_wall[1, 0] - translated_cur_wall[1, 0] + k1 * translated_cur_wall[1, 1] - k2 * translated_next_wall[1, 1]) / (k1 - k2 + alpha)
                    cross_pt = [intersect_x, intersect_y]
                outer_wall_pts.append([cross_pt, end_pt_ind])
            for i in range(len(sorted_outer_wall_name_list)):
                outer_start, related_mid_ind_start = outer_wall_pts[(i - 1) % len(outer_wall_pts)]
                if isinstance(outer_start, tuple):
                    outer_start = outer_start[1]
                outer_end, related_mid_ind_end = outer_wall_pts[i]
                if isinstance(outer_end, tuple):
                    outer_end = outer_end[0]
                outer_wall_name, end_pt_ind = sorted_outer_wall_name_list[i]
                if [related_mid_ind_start, related_mid_ind_end] == house_walls[outer_wall_name]['mid_ind']:
                    house_walls[outer_wall_name]['outer_pts'] = [outer_start, outer_end]
                else:
                    house_walls[outer_wall_name]['outer_pts'] = [outer_end, outer_start]

        house_json['house_wall'] = house_walls
        # 保存到floor相关的信息中
        for room_info in house_json['room']:
            for floor_ind, walls in room_info['floor_wall_info'].items():
                for i, wall in enumerate(walls):
                    wall_name = wall['wall_name']
                    if wall_name in house_walls:
                        room_info['floor_wall_info'][floor_ind][i]['outer_wall'] = house_walls[wall_name]['outer_wall']
                        room_info['floor_wall_info'][floor_ind][i]['outer_pts'] = house_walls[wall_name]['outer_pts']
                    else:
                        room_info['floor_wall_info'][floor_ind][i]['outer_wall'] = False
                        room_info['floor_wall_info'][floor_ind][i]['outer_pts'] = []
        if debug_mode:
            plt.figure()
            plt.axis('equal')

            for wall_name, wall_info in house_walls.items():
                inner = wall_info['inner_pts'][0]
                if len(wall_info['inner_pts']) == 2:
                    outer = wall_info['inner_pts'][1]
                else:
                    if len(wall_info['outer_pts']) == 0:
                        continue
                    outer = wall_info['outer_pts']
                mid = wall_info['mid_pts']
                x = [mid[0][0], inner[0][0], inner[1][0], mid[1][0], outer[1][0], outer[0][0], mid[0][0], mid[1][0]]
                y = [mid[0][1], inner[0][1], inner[1][1], mid[1][1], outer[1][1], outer[0][1], mid[0][1], mid[1][1]]
                plt.plot(x, y)
            save_path = os.path.join(os.path.dirname(__file__), 'temp/%s/mid_wall.png' % house_json['id'])
            plt.savefig(save_path)
            # plt.show()
        return True

    def get_wall_info_hsf(self, house_json, debug_mode=False):
        mid_walls = []
        mid_wall_pts = {}
        for room_json in house_json['room']:
            wall_info = list(room_json['wall_info']['lines'].values())
            mid_walls += [i['middle'] for i in wall_info]
            middle_points = room_json['wall_info']['points']
            mid_wall_pts.update(middle_points)
        if debug_mode:

            plt.figure()
            plt.axis('equal')

            # draw walls
            for room_info in house_json['room']:
                floor_pts = [[round(room_info['floor'][2 * i], 3), round(room_info['floor'][2 * i + 1], 3)] for i in
                             range(len(room_info['floor']) // 2)]
                plt.plot(np.array(floor_pts)[:, 0], np.array(floor_pts)[:, 1])
            for wall in mid_walls:
                plt.plot([mid_wall_pts[wall[0]][0], mid_wall_pts[wall[1]][0]],
                         [mid_wall_pts[wall[0]][1], mid_wall_pts[wall[1]][1]])
                plt.text(mid_wall_pts[wall[0]][0], mid_wall_pts[wall[0]][1], str(wall[0]))
                plt.text(mid_wall_pts[wall[1]][0], mid_wall_pts[wall[1]][1], str(wall[1]))
            save_path = os.path.join(os.path.dirname(__file__), 'temp/%s/mid_wall_ind.png' % house_json['id'])
            plt.savefig(save_path)
            plt.show()
        house_walls = dict([('%s_%s' % tuple(sorted(v)), {'mid_pts': [],
                                                          'inner_pts': [],
                                                          'outer_pts': [],
                                                          'mid_ind': [],
                                                          'norm': [],
                                                          'outer_wall': False}
                             ) for v in mid_walls])

        for room_json in house_json['room']:
            wall_info = list(room_json['wall_info']['lines'].values())
            middle_points = room_json['wall_info']['points']
            # 寻找起点
            floor_pts_start = [room_json['floor'][0], room_json['floor'][1]]
            floor_pts_second = [room_json['floor'][2], room_json['floor'][3]]
            floor_vect = np.array(floor_pts_second) - np.array(floor_pts_start)
            sorted_wall_info = []
            end = None
            for wall in wall_info:
                inner_pts = wall["inner"]
                if np.linalg.norm(np.array(inner_pts[0]) - np.array(floor_pts_start)) < 1e-5:
                    vec = np.array(inner_pts[1]) - np.array(inner_pts[0])
                    if abs(np.dot(vec, floor_vect) / np.linalg.norm(vec) / np.linalg.norm(floor_vect) - 1) < 1e-5:
                        sorted_wall_info.append(wall)
                        middle_vec = np.array(middle_points[wall['middle'][1]]) - np.array(middle_points[wall['middle'][0]])
                        if np.dot(vec, middle_vec) < 0:
                            wall['middle'].reverse()
                        end = wall['middle'][1]

                        break
                if np.linalg.norm(np.array(inner_pts[1]) - np.array(floor_pts_start)) < 1e-5:
                    vec = np.array(inner_pts[0]) - np.array(inner_pts[1])
                    if abs(np.dot(vec, floor_vect) / np.linalg.norm(vec) / np.linalg.norm(floor_vect) - 1) < 1e-5:
                        sorted_wall_info.append(wall)
                        middle_vec = np.array(middle_points[wall['middle'][0]]) - np.array(middle_points[wall['middle'][1]])
                        if np.dot(vec, middle_vec) < 0:
                            wall['middle'].reverse()
                        end = wall['middle'][0]

                        break
            # 排序形成环

            while True:

                if end is None:
                    print('invalid end point')
                    end = wall_info[0]['middle'][1]
                break_flag = True
                for wall in wall_info:
                    if wall in sorted_wall_info:
                        continue
                    if wall['middle'][0] == end:
                        sorted_wall_info.append(wall)
                        end = wall['middle'][1]
                        break_flag = False
                        break
                    elif wall['middle'][1] == end:
                        sorted_wall_info.append(wall)
                        end = wall['middle'][0]
                        break_flag = False
                        break

                if break_flag:
                    break

            floor_edge_to_mid_wall_dict = {}
            floor_pts = np.reshape(room_json['floor'], newshape=[-1, 2])
            for floor_ind in range(len(floor_pts)):
                floor_edge_to_mid_wall_dict[floor_ind] = []

            for floor_ind in range(len(floor_pts)):
                for wall in sorted_wall_info:
                    # info
                    inner_pts = wall["inner"]
                    wall_line = np.array(wall['inner'])

                    in_segment, same_dir = self.segment_in_segment(wall_line, [floor_pts[floor_ind], floor_pts[(floor_ind + 1) % len(floor_pts)]])
                    if in_segment:
                        if not same_dir:
                            wall['inner'].reverse()
                            wall['middle'].reverse()

                        mid_wall_vec = np.array(middle_points[wall['middle'][1]]) - np.array(
                            middle_points[wall['middle'][0]])
                        norm = [-mid_wall_vec[1], mid_wall_vec[0]]
                        norm = norm / np.linalg.norm(norm)
                        if np.dot(norm, np.array(wall['inner'][0]) - np.array(middle_points[wall['middle'][0]])) < 0:
                            norm = - norm
                        half_depth = abs(np.cross(np.array(inner_pts[0]) - np.array(middle_points[wall['middle'][0]]),
                                                  mid_wall_vec) / np.linalg.norm(mid_wall_vec))
                        dis_norm = norm * half_depth
                        corresponding_mid_wall = '%s_%s' % tuple(sorted([wall['middle'][0], wall['middle'][1]]))
                        if len(house_walls[corresponding_mid_wall]['mid_ind']) > 0:
                            if wall['middle'] != house_walls[corresponding_mid_wall]['mid_ind']:
                                inner_pts = [inner_pts[1], inner_pts[0]]
                        else:
                            house_walls[corresponding_mid_wall]['mid_pts'] = [middle_points[wall['middle'][0]], middle_points[wall['middle'][1]]]
                            house_walls[corresponding_mid_wall]['mid_ind'] = wall['middle']
                        house_walls[corresponding_mid_wall]['inner_pts'].append(inner_pts)

                        house_walls[corresponding_mid_wall]['norm'].append(dis_norm)

                        floor_edge_to_mid_wall_dict[floor_ind].append({'mid_pts': [middle_points[wall['middle'][0]],
                                                                                   middle_points[
                                                                                       wall['middle'][1]]],
                                                                       'mid_ind': [wall['middle'][0],
                                                                                   wall['middle'][1]],
                                                                       'inner_pts': inner_pts,
                                                                       'wall_name': corresponding_mid_wall,
                                                                       'depth': half_depth * 2,
                                                                       'depth_bias_pt': []})
                if len(floor_edge_to_mid_wall_dict[floor_ind]) == 0:
                    floor_edge_to_mid_wall_dict[floor_ind] = [{'mid_pts': [],
                                                               'mid_ind': [],
                                                               'inner_pts': [floor_pts[floor_ind], floor_pts[
                                                                   (floor_ind + 1) % len(floor_pts)]],
                                                               'wall_name': '',
                                                               'depth': 0.,
                                                               'depth_bias_pt': []}]
            for i in range(len(floor_pts)):
                floor_to_wall = floor_edge_to_mid_wall_dict[i]
                if len(floor_to_wall) == 1 and len(floor_to_wall[0]['mid_ind']) == 0:
                    if floor_edge_to_mid_wall_dict[(i - 1) % len(floor_pts)][-1]['depth'] < \
                            floor_edge_to_mid_wall_dict[(i + 1) % len(floor_pts)][0]['depth']:
                        floor_edge_to_mid_wall_dict[(i + 1) % len(floor_pts)][0]['depth_bias_pt'].append(0)
                    else:
                        floor_edge_to_mid_wall_dict[(i - 1) % len(floor_pts)][-1]['depth_bias_pt'].append(1)
            room_json['floor_wall_info'] = floor_edge_to_mid_wall_dict
        # out wall detect
        wall_keys = list(house_walls.keys())
        for wall_name in wall_keys:
            wall_info = house_walls[wall_name]
            if len(wall_info['mid_ind']) == 0:
                house_walls.pop(wall_name)
            if len(wall_info['inner_pts']) == 1:
                wall_info['outer_wall'] = True
            else:
                wall_info['outer_wall'] = False

        # 建外墙
        used_wall_list = []
        all_outer_walls = []
        while True:
            sorted_outer_wall_name_list = []
            end = None
            while True:
                break_flag = False
                for wall_name_candidate, wall_info_candidate in house_walls.items():
                    if wall_name_candidate in used_wall_list or not wall_info_candidate['outer_wall']:
                        continue
                    if end is None:
                        end = wall_name_candidate.split('_')[1]
                        used_wall_list.append(wall_name_candidate)
                        sorted_outer_wall_name_list.append([wall_name_candidate, end])

                    wall_start_end_list = wall_name_candidate.split('_')
                    if wall_name_candidate not in used_wall_list and end in wall_start_end_list:
                        end = wall_start_end_list[0] if wall_start_end_list[1] == end else wall_start_end_list[1]
                        used_wall_list.append(wall_name_candidate)
                        sorted_outer_wall_name_list.append([wall_name_candidate, end])
                        break_flag = True
                        break
                if not break_flag:
                    break
            if len(sorted_outer_wall_name_list) == 0:
                break
            all_outer_walls.append(sorted_outer_wall_name_list)

        # 膨胀外墙
        for sorted_outer_wall_name_list in all_outer_walls:
            outer_wall_pts = []
            for i in range(len(sorted_outer_wall_name_list)):
                outer_wall_name, end_pt_ind = sorted_outer_wall_name_list[i]
                next_outer_wall_name, _ = sorted_outer_wall_name_list[(i + 1) % len(sorted_outer_wall_name_list)]

                connected_pt = mid_wall_pts[end_pt_ind]
                cur_wall = house_walls[outer_wall_name]['mid_pts']
                cur_norm = -np.array(house_walls[outer_wall_name]['norm'][0])

                next_wall = house_walls[next_outer_wall_name]['mid_pts']
                next_norm = -np.array(house_walls[next_outer_wall_name]['norm'][0])

                if abs(np.dot(cur_norm, next_norm) / np.linalg.norm(cur_norm) / np.linalg.norm(next_norm)) > 0.99:
                    cross_pt = (np.array(connected_pt) + cur_norm).tolist()
                    if np.linalg.norm(cur_norm - next_norm) > 1e-2:
                        cross_pt = (cross_pt, (np.array(connected_pt) + next_norm).tolist())
                else:
                    # 求直线交点
                    translated_cur_wall = np.array(cur_wall) + cur_norm
                    translated_next_wall = np.array(next_wall) + next_norm
                    alpha = 1e-10
                    k1 = (translated_cur_wall[0, 0] - translated_cur_wall[1, 0]) / (
                                translated_cur_wall[0, 1] - translated_cur_wall[1, 1] + alpha)
                    k2 = (translated_next_wall[0, 0] - translated_next_wall[1, 0]) / (
                                translated_next_wall[0, 1] - translated_next_wall[1, 1] + alpha)

                    intersect_x = (translated_next_wall[1, 1] - translated_cur_wall[1, 1] + 1. / (k1 + alpha) *
                                   translated_cur_wall[1, 0] - 1. / (k2 + alpha) * translated_next_wall[1, 0]) / (
                                              1. / (k1 + alpha) - 1. / (k2 + alpha) + alpha)
                    intersect_y = (translated_next_wall[1, 0] - translated_cur_wall[1, 0] + k1 *
                                   translated_cur_wall[1, 1] - k2 * translated_next_wall[1, 1]) / (k1 - k2 + alpha)
                    cross_pt = [intersect_x, intersect_y]
                outer_wall_pts.append([cross_pt, end_pt_ind])
            for i in range(len(sorted_outer_wall_name_list)):
                outer_start, related_mid_ind_start = outer_wall_pts[(i - 1) % len(outer_wall_pts)]
                if isinstance(outer_start, tuple):
                    outer_start = outer_start[1]
                outer_end, related_mid_ind_end = outer_wall_pts[i]
                if isinstance(outer_end, tuple):
                    outer_end = outer_end[0]
                outer_wall_name, end_pt_ind = sorted_outer_wall_name_list[i]
                if [related_mid_ind_start, related_mid_ind_end] == house_walls[outer_wall_name]['mid_ind']:
                    house_walls[outer_wall_name]['outer_pts'] = [outer_start, outer_end]
                else:
                    house_walls[outer_wall_name]['outer_pts'] = [outer_end, outer_start]

        house_json['house_wall'] = house_walls
        # 保存到floor相关的信息中
        for room_info in house_json['room']:
            for floor_ind, walls in room_info['floor_wall_info'].items():
                for i, wall in enumerate(walls):
                    wall_name = wall['wall_name']
                    if wall_name in house_walls:
                        room_info['floor_wall_info'][floor_ind][i]['outer_wall'] = house_walls[wall_name][
                            'outer_wall']
                        room_info['floor_wall_info'][floor_ind][i]['outer_pts'] = house_walls[wall_name][
                            'outer_pts']
                    else:
                        room_info['floor_wall_info'][floor_ind][i]['outer_wall'] = False
                        room_info['floor_wall_info'][floor_ind][i]['outer_pts'] = []
        if debug_mode:
            plt.figure()
            plt.axis('equal')

            for wall_name, wall_info in house_walls.items():
                inner = wall_info['inner_pts'][0]
                if len(wall_info['inner_pts']) == 2:
                    outer = wall_info['inner_pts'][1]
                else:
                    if len(wall_info['outer_pts']) == 0:
                        continue
                    outer = wall_info['outer_pts']
                mid = wall_info['mid_pts']
                x = [mid[0][0], inner[0][0], inner[1][0], mid[1][0], outer[1][0], outer[0][0], mid[0][0], mid[1][0]]
                y = [mid[0][1], inner[0][1], inner[1][1], mid[1][1], outer[1][1], outer[0][1], mid[0][1], mid[1][1]]
                plt.plot(x, y)
            save_path = os.path.join(os.path.dirname(__file__), 'temp/%s/mid_wall.png' % house_json['id'])
            plt.savefig(save_path)
            plt.show()

    def segment_in_segment(self, short_line, long_line):
        line1_vec = np.array(short_line[1]) - np.array(short_line[0])
        line2_vec = np.array(long_line[1]) - np.array(long_line[0])
        if np.cross(line1_vec, line2_vec) > 1e-5:
            return False, False

        line12_vec1 = np.array(short_line[1]) - np.array(long_line[0])

        line12_vec2 = np.array(short_line[1]) - np.array(long_line[1])
        if np.linalg.norm(line12_vec1) > np.linalg.norm(line12_vec2):
            line12_vec = line12_vec1
        else:
            line12_vec = line12_vec2
        if np.cross(line1_vec, line12_vec) > 1e-5:
            return False, False

        if np.dot(line1_vec, line2_vec) > 0:
            same_dir = True
        else:
            same_dir = False
        if abs(short_line[0][0] - short_line[1][0]) < 1e-5:
            if min(short_line[0][1], short_line[1][1]) >= min(long_line[0][1], long_line[1][1]) - 1e-5 \
                    and max(short_line[0][1], short_line[1][1]) <= max(long_line[0][1], long_line[1][1]) + 1e-5:
                return True, same_dir
            else:
                return False, same_dir
        else:
            if min(short_line[0][0], short_line[1][0]) >= min(long_line[0][0], long_line[1][0]) - 1e-5 \
                    and max(short_line[0][0], short_line[1][0]) <= max(long_line[0][0], long_line[1][0]) + 1e-5:
                return True, same_dir
            else:
                return False, same_dir

    def get_mid_inds(self, inner_vec, base_mid_inds, target_mid_inds, mid_wall_pts, mid_wall_inds):
        wall_dict = dict([(i, []) for i in range(len(mid_wall_pts))])
        for wall_pair in mid_wall_inds:
            if wall_pair[1] not in wall_dict[wall_pair[0]]:
                wall_dict[wall_pair[0]].append(wall_pair[1])

            if wall_pair[0] not in wall_dict[wall_pair[1]]:
                wall_dict[wall_pair[1]].append(wall_pair[0])

        start_end_pair = []
        floor_full_mid_inds = []
        for base_mid_ind in base_mid_inds:
            for target_mid_ind in target_mid_inds:
                if base_mid_ind == target_mid_ind:
                    if [base_mid_ind, target_mid_ind] not in start_end_pair:
                        start_end_pair.append([base_mid_ind, target_mid_ind])
                        floor_full_mid_inds.append([base_mid_ind, target_mid_ind])
                    continue
                if target_mid_ind in wall_dict[base_mid_ind]:
                    if [base_mid_ind, target_mid_ind] not in start_end_pair:
                        start_end_pair.append([base_mid_ind, target_mid_ind])
                        floor_full_mid_inds.append([base_mid_ind, target_mid_ind])
                else:
                    mid_inter_inds = []
                    start_id = base_mid_ind

                    while True:
                        is_succeed = False
                        for next_ind in wall_dict[start_id]:
                            if next_ind in mid_inter_inds:
                                continue
                            cur_vec = np.array(mid_wall_pts[next_ind]) - np.array(mid_wall_pts[start_id])
                            if np.dot(cur_vec, inner_vec) / np.linalg.norm(inner_vec) / np.linalg.norm(
                                    cur_vec) > 0.999:
                                mid_inter_inds.append(next_ind)
                                start_id = next_ind
                                is_succeed = True
                                break
                        if not is_succeed:
                            mid_inter_inds = []
                            break
                        if len(mid_inter_inds) > 0 and mid_inter_inds[-1] == target_mid_ind:
                            break
                    if len(mid_inter_inds) > 0:
                        mid_inter_inds.insert(0, base_mid_ind)
                        floor_full_mid_inds.append(mid_inter_inds)
                        start_end_pair.append([base_mid_ind, target_mid_ind])
        return start_end_pair, floor_full_mid_inds

    def get_closest_mid_pts(self, pt, mid_pts):
        res = [[i, np.linalg.norm(np.array(pt) - np.array(mid_pts[i]))] for i in range(len(mid_pts))]
        res = [v for v in res if v[1] < 0.36]
        res.sort(key=lambda x: x[1])
        return [v[0] for v in res]

    def get_default_wall_info(self, house_json):
        for room_info in house_json['room']:
            floor_pts = [[round(room_info['floor'][2 * i], 3), round(room_info['floor'][2 * i + 1], 3)] for i in
                         range(len(room_info['floor']) // 2 - 1)]
            floor_edge_to_mid_wall_dict = {}
            for i in range(len(floor_pts)):
                start = floor_pts[i]
                end = floor_pts[(i + 1) % len(floor_pts)]
                floor_edge_to_mid_wall_dict[i] = [{'mid_pts': [],
                                                   'mid_ind': [],
                                                   'inner_pts': [start, end],
                                                   'wall_name': '',
                                                   'depth': 0.,
                                                   'depth_bias_pt': []}]
            room_info['floor_wall_info'] = floor_edge_to_mid_wall_dict

    # 构建点位算法的输入
    def get_scene_info(self):
        # 客餐厅 + 卧室 + 卫生间 点位
        out_scene_info_list = []
        for need_room_uid in self.type_table['LivingDiningRoom']:
            out_scene_info_list.append(self.room_table[need_room_uid].get_scene_info())

        for need_room_uid in self.type_table['MasterBedroom']:
            out_scene_info_list.append(self.room_table[need_room_uid].get_scene_info())

        for need_room_uid in self.type_table['Library']:
            out_scene_info_list.append(self.room_table[need_room_uid].get_scene_info())

        for need_room_uid in self.type_table['Bathroom']:
            out_scene_info_list.append(self.room_table[need_room_uid].get_scene_info())

        for need_room_uid in self.type_table['Kitchen']:
            out_scene_info_list.append(self.room_table[need_room_uid].get_scene_info())

        for need_room_uid in self.type_table['KidsRoom']:
            out_scene_info_list.append(self.room_table[need_room_uid].get_scene_info())

        return out_scene_info_list



#
# if __name__ == '__main__':
#     from matplotlib import pyplot as plt
#
#     data = json.load(open('/Users/liqing.zhc/Desktop/sample_rooms.json', 'r'))
#     vertices = dict([(v['id'], v) for v in data['data'] if v['Class'] == "HSCore.Model.Vertex"])
#     walls = dict([(v['id'], v) for v in data['data'] if v['Class'] == "HSCore.Model.Wall"])
#
#     house_walls = []
#     mid_wall_pts = []
#     key_dict = {}
#     for _, wall in walls.items():
#         org_vertice_key_from = wall['from']
#         if org_vertice_key_from in key_dict:
#             new_vertice_key_from = key_dict[org_vertice_key_from]
#             p = mid_wall_pts[new_vertice_key_from]
#             print('111')
#         else:
#             new_vertice_key_from = len(mid_wall_pts)
#             key_dict[org_vertice_key_from] = new_vertice_key_from
#             p = [vertices[wall['from']]['x'], vertices[wall['from']]['y']]
#             mid_wall_pts.append(copy.deepcopy(p))
#         from_p = p
#
#         org_vertice_key_to = wall['to']
#         if org_vertice_key_to in key_dict:
#             new_vertice_key_to = key_dict[org_vertice_key_to]
#             p = mid_wall_pts[new_vertice_key_to]
#         else:
#             new_vertice_key_to = len(mid_wall_pts)
#             key_dict[org_vertice_key_to] = new_vertice_key_to
#             p = [vertices[wall['to']]['x'], vertices[wall['to']]['y']]
#             mid_wall_pts.append(copy.deepcopy(p))
#         to_p = p
#         house_walls.append([new_vertice_key_from, new_vertice_key_to])
#         plt.plot([from_p[0], to_p[0]], [from_p[1], to_p[1]])
#     # plt.figure()
#     # for wid, wall in walls.items():
#     #     from_p = [vertices[wall['from']]['x'], vertices[wall['from']]['y']]
#     #     print(vertices[wall['from']]['z'])
#     #     to_p = [vertices[wall['to']]['x'], vertices[wall['to']]['y']]
#     #     print(vertices[wall['to']]['z'])
#     #     plt.plot([from_p[0], to_p[0]], [from_p[1], to_p[1]])
#     plt.show()
