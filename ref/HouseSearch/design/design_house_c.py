import json
import math
import os
import time
import copy
import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import Polygon, Point
from HouseSearch.util import compute_poly_area


def check_on_line(pt, line):
    p1, p2 = line
    if np.linalg.norm(np.array(p1) - np.array(p2)) < 1e-3:
        if np.linalg.norm(np.array(p1) - np.array(pt)) < 1e-3:
            return True
        else:
            return False
    pf = pt
    cross = (p2[0] - p1[0]) * (pf[0] - p1[0]) + (p2[1] - p1[1]) * (pf[1] - p1[1])
    if cross < 0:
        return False
    d2 = (p2[0] - p1[0]) * (p2[0] - p1[0]) + (p2[1] - p1[1]) * (p2[1] - p1[1])

    if abs(d2) < 0.0001:
        return False

    if cross > d2:
        return False
    r = cross / d2
    px = p1[0] + (p2[0] - p1[0]) * r
    py = p1[1] + (p2[1] - p1[1]) * r

    return ((pf[0] - px) * (pf[0] - px) + (py - pf[1]) * (py - pf[1])) <= 0.0001


def get_wall_info(from_p, to_p, wall_table):
    p_from = [from_p['x'], from_p['y']]
    p_to = [to_p['x'], to_p['y']]
    return_wall_list = []
    for _, wall_info in wall_table.items():
        # 检查墙上两个点是否在 房间直线上
        if check_on_line(wall_info['from'], [p_from, p_to]) and check_on_line(wall_info['to'], [p_from, p_to]):
            return_wall_list.append(wall_info)

        # 房间线段在墙上
        elif check_on_line(p_from, [wall_info['from'], wall_info['to']]) and check_on_line(p_to, [wall_info['from'], wall_info['to']]):
            return_wall_list.append(wall_info)

    return return_wall_list


class HouseInfoConvert(object):
    def __init__(self, design_json, design_id=''):
        self.design_id = design_id
        self.label_dict = design_json
        self.house_info = None

        # a = []
        # for item in self.label_dict['data']:
        #     name = item['Class'].split('.')[-1]
        #     if name in a:
        #         continue
        #     a.append(name)

        self.CustomizedModel = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.CustomizedModel']],
                [item for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.CustomizedModel']]))

        self.DAssembly = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.DAssembly']],
                [item for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.DAssembly']]))

        self.PAssembly = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.PAssembly']],
                [item for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.PAssembly']]))

        self.Floorplan = dict(
            zip([item['id'] for item in self.label_dict['data'] if
                 'Floorplan' in item['Class'] == 'HSCore.Model.Floorplan'],
                [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Floorplan']))

        self.Scene = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Scene'],
                              [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Scene']))

        self.Layer = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Layer'],
                              [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Layer']))

        self.Room = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Floor'],
                             [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Floor']))

        self.Wall = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Wall'],
                             [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Wall']))

        self.Face = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Face'],
                             [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Face']))

        self.Loop = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Loop'],
                             [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Loop']))

        self.CoEdge = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.CoEdge'],
                [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.CoEdge']))

        self.Edge = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Edge'],
                             [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Edge']))

        self.Vertex = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Vertex'],
                [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Vertex']))

        self.Door = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.Door']],
                             [item for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.Door']]))

        self.State = dict(zip([item['id'] for item in self.label_dict['states'] if item['Class'] in ['HSCore.State']],
                              [item for item in self.label_dict['states'] if item['Class'] in ['HSCore.State']]))

        self.Window = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.Window',
                                                                                     'HSCore.Model.CornerWindow',
                                                                                     'HSCore.Model.POrdinaryWindow',
                                                                                     'HSCore.Model.CornerFlatWindow',
                                                                                     'HSCore.Model.Parametrization.WindowHole',
                                                                                     'HSCore.Model.BayWindow']],
                [item for item in self.label_dict['data'] if item['Class'] in ['HSCore.Model.Window',
                                                                               'HSCore.Model.CornerWindow',
                                                                               'HSCore.Model.POrdinaryWindow',
                                                                               'HSCore.Model.CornerFlatWindow',
                                                                               'HSCore.Model.Parametrization.WindowHole',
                                                                               'HSCore.Model.BayWindow']]))

        self.Hole = dict(zip([item['id'] for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Hole'],
                             [item for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Hole']))

        self.rooms_wall_id_list = {}

    def build(self, furniture=False, material=False):
        if self.house_info:
            return self.house_info

        wall_table = {}
        opening_table = {}
        for wall_id, wall in self.Wall.items():
            from_p = self.Vertex[wall['from']]
            to_p = self.Vertex[wall['to']]
            if 'openings' in wall:
                opening_list = wall['openings']
            else:
                opening_list = []
            wall_table[wall_id] = {'id': wall_id, 'width': wall['width'], 'from': [from_p['x'], from_p['y']],
                                   'to': [to_p['x'], to_p['y']], "openings": opening_list}

        room_list = []
        for room_id, room in self.Room.items():
            # print(room)
            room_type = "none"
            if "roomType" in room:
                room_type = room['roomType']
            room_info = {'id': room_type + '-' + room_id, 'type': room_type, 'floor': [], 'door_info': [],
                         'window_info': [], 'hole_info': [], 'baywindow_info': [], 'wall_width': [],
                         'furniture_info': [], 'custom_info': [],
                         'material_info': []}
            self.rooms_wall_id_list[room_type + '-' + room_id] = []
            loop_id = room['children'][0]
            loop = self.Loop[loop_id]
            wall_idx = -1

            # plt.figure()
            # plt.axis('equal')
            # plt.title(room_type)
            sorted_coedges = []
            if len(loop['children']) > 0:
                sorted_coedges = [loop['children'][0]]
                while True:
                    next_coedge = self.CoEdge[sorted_coedges[-1]]['next']
                    if next_coedge in sorted_coedges:
                        break
                    sorted_coedges.append(next_coedge)

            # show_data_x = []
            # show_data_y = []
            for _, edge_id in enumerate(sorted_coedges):
                wall_idx += 1
                edge = self.Edge[self.CoEdge[edge_id]['children'][0]]
                from_p = self.Vertex[edge['from']]
                to_p = self.Vertex[edge['to']]
                # show_data_x.append(from_p['x'])
                # show_data_x.append(to_p['x'])
                # show_data_y.append(from_p['y'])
                # show_data_y.append(to_p['y'])

                wall_info_list = get_wall_info(from_p, to_p, wall_table)
                # print(wall_info_list)
                # plt.plot(show_data_x, show_data_y)  # ⻓度计算包含箭头箭尾
                # plt.show()
                wall_width = 0.24

                if len(wall_info_list) > 0:
                    for wall_info in wall_info_list:
                        wall_info_id = wall_info['id']
                        self.rooms_wall_id_list[room_type + '-' + room_id].append(wall_info_id)

                        wall_width = wall_info['width']
                        if 'openings' in wall_info:
                            for open_id in wall_info['openings']:
                                # 添加门信息
                                if open_id in self.Door:
                                    door_info = self.get_component_info(self.Door[open_id], from_p, to_p)
                                    if len(door_info['pts']) > 0:
                                        room_info['door_info'].append(door_info)
                                        room_info['door_info'][-1]['wall_idx'] = wall_idx
                                        room_info['door_info'][-1]['to'] = wall_info_id
                                        room_info['door_info'][-1]['id'] = open_id

                                        if wall_info_id in opening_table:
                                            opening_table[wall_info_id].append(
                                                room_type + '-' + room_id + '-' + open_id)
                                        else:
                                            opening_table[wall_info_id] = [room_type + '-' + room_id + '-' + open_id]

                                # 添加窗信息
                                if open_id in self.Window:
                                    window_info = self.get_component_info(self.Window[open_id], from_p, to_p)
                                    if len(window_info['pts']) > 0:
                                        room_info['window_info'].append(window_info)
                                        room_info['window_info'][-1]['wall_idx'] = wall_idx
                                        room_info['window_info'][-1]['to'] = wall_info_id

                                # 添加洞信息 按门处理
                                if open_id in self.Hole:
                                    hole_info = self.get_component_info(self.Hole[open_id], from_p, to_p)
                                    if len(hole_info['pts']) > 0:
                                        room_info['hole_info'].append(hole_info)
                                        room_info['hole_info'][-1]['wall_idx'] = wall_idx
                                        room_info['hole_info'][-1]['to'] = wall_info_id
                                        room_info['hole_info'][-1]['id'] = open_id

                                        if wall_info_id in opening_table:
                                            opening_table[wall_info_id].append(room_type + '-' + room_id + '-' + open_id)
                                        else:
                                            opening_table[wall_info_id] = [room_type + '-' + room_id + '-' + open_id]

                room_info['wall_width'].append(wall_width)

                # now_p = [from_p['x'], from_p['y']]
                #  y 轴flip
                room_info['floor'].append(from_p['x'])
                room_info['floor'].append(from_p['y'])

            room_info['area'] = compute_poly_area(room_info['floor'])
            room_info['floor'] += room_info['floor'][:2]
            room_info['coordinate'] = 'xyz'
            room_info['unit'] = 'm'

            room_list.append(room_info)

        for room_info in room_list:
            room_id = room_info['id']
            room_info['height'] = 2.8
            for door_info in room_info['door_info']:
                wall_idx = door_info['to']
                door_info['to'] = ''
                if wall_idx not in opening_table:
                    continue
                else:
                    for target_id in opening_table[wall_idx]:
                        target_room_type, target_room_id, target_door_id = target_id.split('-')
                        if room_id != target_room_type + "-" + target_room_id:
                            if door_info['id'] == target_door_id:
                                door_info['to'] = target_room_type + "-" + target_room_id
                                break

            for window_info in room_info['window_info']:
                wall_idx = window_info['to']
                window_info['to'] = ''
                if wall_idx not in opening_table:
                    continue
                else:
                    for target_id in opening_table[wall_idx]:
                        target_room_type, target_room_id, target_door_id = target_id.split('-')
                        if room_id != target_room_type + "-" + target_room_id:
                            window_info['to'] = target_room_type + "-" + target_room_id
                            break

            for hole_info in room_info['hole_info']:
                wall_idx = hole_info['to']
                hole_info['to'] = ''
                if wall_idx not in opening_table:
                    continue
                else:
                    for target_id in opening_table[wall_idx]:
                        target_room_type, target_room_id, target_door_id = target_id.split('-')
                        if room_id != target_room_type + "-" + target_room_id:
                            if hole_info['id'] == target_door_id:
                                hole_info['to'] = target_room_type + "-" + target_room_id
                                break

        # 中线墙
        mid_walls = []
        mid_wall_pts = []
        key_dict = {}

        for _, wall in self.Wall.items():
            org_vertice_key_from = wall['from']
            if org_vertice_key_from in key_dict:
                new_vertice_key_from = key_dict[org_vertice_key_from]
            else:
                new_vertice_key_from = len(mid_wall_pts)

                mid_wall_pts.append([self.Vertex[wall['from']]['x'], self.Vertex[wall['from']]['y']])
                key_dict[org_vertice_key_from] = new_vertice_key_from

            org_vertice_key_to = wall['to']
            if org_vertice_key_to in key_dict:
                new_vertice_key_to = key_dict[org_vertice_key_to]
            else:
                new_vertice_key_to = len(mid_wall_pts)

                mid_wall_pts.append([self.Vertex[wall['to']]['x'], self.Vertex[wall['to']]['y']])
                key_dict[org_vertice_key_to] = new_vertice_key_to
            mid_walls.append([new_vertice_key_from, new_vertice_key_to])
        mid_wall = {'wall_ind': mid_walls, 'wall_pts': mid_wall_pts}
        self.house_info = {'id': self.design_id, 'room': room_list, 'mid_wall': mid_wall, 'height': 2.8}

        if furniture:
            self.get_furnitures()
        if material:
            self.get_materials()

        return self.house_info

    def get_component_info(self, component, from_p, to_p):
        assert (component['Class'] in ['HSCore.Model.Door', 'HSCore.Model.Window', 'HSCore.Model.Hole',
                                       'HSCore.Model.CornerWindow',
                                       'HSCore.Model.POrdinaryWindow', 'HSCore.Model.CornerFlatWindow',
                                       'HSCore.Model.BayWindow', 'HSCore.Model.Parametrization.WindowHole', ''])
        # 计算斜率
        # if 'ZScale' in component.keys():
        #     z_scale = component['ZScale']
        if abs(to_p['x'] - from_p['x']) < 0.1:
            z_rotation = 1.57079  # pi/2
        else:
            # y 翻转
            r = ((to_p['y']) - (from_p['y'])) / (to_p['x'] - from_p['x'])
            z_rotation = math.atan(r)

        length = [component['XLength'], component['YLength']]
        # 最小开放空间长度
        if component['Class'] == 'HSCore.Model.Door':
            if length[0] < 0.75:
                length[0] = 0.75
        else:
            if length[0] < 0.3:
                length[0] = 0.3

        x_scale, y_scale, z_scale = 1.0, 1.0, 1.0

        #  y 轴flip
        if 'YScale' in component.keys():
            y_scale = component['YScale']
        if 'XScale' in component.keys():
            x_scale = component['XScale']

        scale = [x_scale, y_scale, z_scale]
        coord = [component['x'], component['y']]

        cos_ang = math.cos(z_rotation)
        sin_ang = math.sin(z_rotation)

        x_half_len, y_half_len = length[0] * scale[0] / 2.0, length[1] * scale[1] / 2.0

        component_main_pts = [[-x_half_len * cos_ang + coord[0], -x_half_len * sin_ang + coord[1]],
                              [x_half_len * cos_ang + coord[0], x_half_len * sin_ang + coord[1]]]

        out_pts = []

        # 修正hole的宽度 from statistics
        if component['Class'] == 'HSCore.Model.Hole':
            init_vector = [[-x_half_len, y_half_len], [-x_half_len, -y_half_len],
                           [x_half_len, -y_half_len], [x_half_len, y_half_len]]

            for pt in init_vector:
                out_pts += [pt[0] * cos_ang - pt[1] * sin_ang + coord[0], pt[0] * sin_ang + pt[1] * cos_ang + coord[1]]

        # 修正door的宽度 from statistics
        if component['Class'] == 'HSCore.Model.Door':
            init_vector = [[-x_half_len, y_half_len], [-x_half_len, -y_half_len],
                           [x_half_len, -y_half_len], [x_half_len, y_half_len]]

            for pt in init_vector:
                out_pts += [pt[0] * cos_ang - pt[1] * sin_ang + coord[0], pt[0] * sin_ang + pt[1] * cos_ang + coord[1]]

        # 修正 window from statistics
        if component['Class'] in ['HSCore.Model.Window', 'HSCore.Model.Parametrization.WindowHole']:
            init_vector = [[-x_half_len, y_half_len], [-x_half_len, -y_half_len],
                           [x_half_len, -y_half_len], [x_half_len, y_half_len]]

            for pt in init_vector:
                out_pts += [pt[0] * cos_ang - pt[1] * sin_ang + coord[0], pt[0] * sin_ang + pt[1] * cos_ang + coord[1]]

        component_info = {'pts': out_pts, 'to': '', 'width': length[1], 'wall_idx': 0, 'main_pts': component_main_pts, 'id':component['id']}

        temp_line = [[from_p['x'], from_p['y']], [to_p['x'], to_p['y']]]
        if check_on_line(component_main_pts[0], temp_line) and check_on_line(component_main_pts[1], temp_line):
            return component_info
        else:
            return {'pts':[]}

    def get_materials(self):
        if not self.house_info:
            self.build()
        self.Materials = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Material'])
        if 'materials' in self.label_dict:
            materialData = dict(
                [(item['id'], item) for item in self.label_dict['materials'] if
                 item['Class'] == 'HSCore.Material.MaterialData'])
            for k, v in materialData.items():
                if k not in self.Materials:
                    self.Materials[k] = v
            # self.Materials.update(dict(
            #     [(item['id'], item) for item in self.label_dict['materials'] if
            #      item['Class'] == 'HSCore.Material.MaterialData']))
        self.Mixpaint = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Mixpaint'])
        self.Polygon = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Polygon'])
        self.Pattern = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Pattern'])
        self.Block = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Block'])

        wall_table = {}
        for wall_id, wall in self.Wall.items():
            from_p = self.Vertex[wall['from']]
            to_p = self.Vertex[wall['to']]

            wall_table[wall_id] = {'id': wall_id, 'width': wall['width'], 'from': [from_p['x'], from_p['y']],
                                   'to': [to_p['x'], to_p['y']],
                                   'left': wall['faces']['left'], 'right': wall['faces']['right']}

        for room_ind, room in self.Room.items():
            room_type = "none"
            if "roomType" in room:
                room_type = room['roomType']
            room_id = room_type + '-' + room_ind

            mat_info = {'id': room_id, 'type': room_type, 'floor': [], 'wall': [], 'win_pocket': [], 'door_pocket': []}
            wall_lens = []
            # floor material
            floor_export_mat = self.get_face_material(room['material'])
            if floor_export_mat['area'] == -1:
                for room_info in self.house_info['room']:
                    if room_info['id'] == room_id:
                        floor_export_mat['area'] = room_info['area']
                        break
            in_list = False
            for m_ind, floor_mat in enumerate(mat_info['floor']):
                if floor_mat['jid'] == floor_export_mat['jid'] and floor_mat['jid'] not in ['', 'generated']:
                    in_list = True
                    if len(floor_mat['texture_url']) == 0 and len(floor_export_mat['texture_url']) > 0:
                        mat_info['floor'][m_ind]['texture_url'] = floor_export_mat['texture_url']
                    break
            if not in_list:
                mat_info['floor'].append(floor_export_mat)

            # wall material
            loop_id = room['children'][0]
            loop = self.Loop[loop_id]
            wall_idx = -1

            sorted_coedges = []
            if len(loop['children']) > 0:
                sorted_coedges = [loop['children'][0]]
                while True:
                    next_coedge = self.CoEdge[sorted_coedges[-1]]['next']
                    if next_coedge in sorted_coedges:
                        break
                    sorted_coedges.append(next_coedge)

            for _, edge_id in enumerate(sorted_coedges):
                wall_idx += 1
                edge = self.Edge[self.CoEdge[edge_id]['children'][0]]
                from_p = self.Vertex[edge['from']]
                to_p = self.Vertex[edge['to']]
                floor_vec = np.array([to_p['x'], to_p['y']]) - np.array([from_p['x'], from_p['y']])
                # plt.arrow(from_p['x'], from_p['y'], to_p['x'] - from_p['x'], to_p['y'] - from_p['y'],  # 坐标与距离
                #           head_width=0.2, lw=2,  # 箭头⻓度，箭尾线宽
                #           length_includes_head=True)  # ⻓度计算包含箭头箭尾
                wall_info_list = get_wall_info(from_p, to_p, wall_table)
                for wall in wall_info_list:
                    wall_vec = np.array(wall['to']) - np.array(wall['from'])
                    wall_length = np.linalg.norm(wall_vec)
                    if np.dot(floor_vec, wall_vec) > 0:
                        face_ids = wall['left']
                    else:
                        face_ids = wall['right']
                    for face_id in face_ids:
                        inner_face_mat_ind = self.Face[face_id]['material']
                        export_mat = self.get_face_material(inner_face_mat_ind)

                        in_list = False
                        for m_ind, wall_mat in enumerate(mat_info['wall']):
                            if wall_mat['jid'] == export_mat['jid'] and wall_mat['jid'] not in ['', 'generated']:
                                in_list = True
                                wall_lens[m_ind] += wall_length
                                if len(wall_mat['texture_url']) == 0 and len(export_mat['texture_url']) > 0:
                                    mat_info['wall'][m_ind]['texture_url'] = export_mat['texture_url']
                                break
                        if not in_list:
                            mat_info['wall'].append(export_mat)
                            wall_lens.append(wall_length)

                        # print(face_id, wall_length)
            for m_ind in range(len(mat_info['wall'])):
                mat_info['wall'][m_ind]['area'] = wall_lens[m_ind]
            mat_info['wall'].sort(key=lambda x: -x['area'])
            for rid in range(len(self.house_info['room'])):
                if self.house_info['room'][rid]['id'] == room_id:
                    self.house_info['room'][rid]['material_info'] = mat_info
                    break

    def get_face_material(self, mat_id):
        wall_material = self.Materials[mat_id]
        face_material = copy.deepcopy(wall_material)
        seam_material = None
        texture_url_dict = {}
        jid = face_material['seekId'] if 'seekId' in face_material else 'generated'
        if jid in ['', 'generated'] and 'textureURI' in face_material and face_material['textureURI'] != '':
            face_material['seekId'] = face_material['textureURI'].split('/')[-2]
            jid = face_material['seekId']
        if jid not in ['', 'generated'] and 'textureURI' in face_material and face_material['textureURI'] != '':
            texture_url_dict[jid] = face_material['textureURI']
        max_area = -1
        if 'mixpaint' in face_material:
            mixpaint = self.Mixpaint[face_material['mixpaint']]
            if 'children' in mixpaint and len(mixpaint['children']) > 0:

                polygon_inds = mixpaint['children']

                max_polygon_ind = polygon_inds[0]
                for polygon_ind in polygon_inds:
                    cur_polygon = self.Polygon[polygon_ind]
                    if 'geomPolygons' in cur_polygon:
                        area = 0
                        for poly in cur_polygon['geomPolygons']:
                            outer = poly['outer']
                            outer = [[i['x'], i['y']] for i in outer]
                            holes = []
                            for hole in poly['holes']:
                                hole = [[i['x'], i['y']] for i in hole]
                                holes.append(hole)
                            area += Polygon(outer, holes).area
                        if area > max_area:
                            max_area = area
                            max_polygon_ind = polygon_ind

                polygon = self.Polygon[max_polygon_ind]
                polygon_material = polygon['material']
                if isinstance(polygon_material, str):
                    polygon_material = self.Materials[polygon_material]
                else:
                    if 'id' not in polygon_material:
                        polygon_material['id'] = max_polygon_ind
                face_material = copy.deepcopy(polygon_material)
                jid = face_material['seekId'] if 'seekId' in face_material else 'generated'
                if jid in ['', 'generated'] and 'textureURI' in face_material and face_material['textureURI'] != '':
                    face_material['seekId'] = face_material['textureURI'].split('/')[-2]
                    jid = face_material['seekId']
                if jid in texture_url_dict and ('textureURI' not in face_material or face_material['textureURI'] == ''):
                    face_material['textureURI'] = texture_url_dict[jid]
                if 'pattern' in polygon:
                    pattern = self.Pattern[polygon['pattern']]
                    if 'children' in pattern and len(pattern['children']) > 0 and pattern['children'][0] in self.Block:
                        block = self.Block[pattern['children'][0]]
                        block_material = self.Materials[block['material']]
                        face_material = copy.deepcopy(block_material)
                        jid = face_material['seekId'] if 'seekId' in face_material else 'generated'
                        if jid in ['', 'generated'] and 'textureURI' in face_material and face_material[
                            'textureURI'] != '':
                            face_material['seekId'] = face_material['textureURI'].split('/')[-2]
                            jid = face_material['seekId']
                        if jid in texture_url_dict and (
                                'textureURI' not in face_material or face_material['textureURI'] == ''):
                            face_material['textureURI'] = texture_url_dict[jid]
                        if 'seamMaterial' in pattern:
                            seam_material = pattern['seamMaterial']
                        elif 'seam' in pattern:
                            if 'material' in pattern['seam']:
                                seam_material = pattern['seam']['material']
        if seam_material is not None:
            color_mode = seam_material['colorMode'] if 'colorMode' in seam_material else None
            if color_mode is None:
                color_mode = seam_material['useColor'] if 'useColor' in seam_material else None
                if color_mode is not None:
                    color_mode = 'color' if color_mode else 'texture'
            seam_color = self.cvt_color(seam_material['color']) if 'color' in seam_material else None

            seam_jid = seam_material['seekId'] if 'seekId' in seam_material else 'generated'
            if seam_jid in ['', 'generated'] and 'textureURI' in seam_material and seam_material[
                'textureURI'] != '':
                seam_material['seekId'] = seam_material['textureURI'].split('/')[-2]
                seam_jid = seam_material['seekId']
            if seam_color is None and seam_jid not in ['', 'generated']:
                for _, mat in self.Materials.items():
                    if mat['seekId'] == seam_jid and 'color' in mat:
                        seam_color = self.cvt_color(mat['color'])
                        break
            seam_mat = {
                'jid': seam_jid,
                'texture_url': seam_material['textureURI'] if 'textureURI' in seam_material else '',
                'color': seam_color,
                'colorMode': color_mode,
                'size': [seam_material['tileSize_x'],
                         seam_material[
                             'tileSize_y']] if 'tileSize_x' in seam_material and 'tileSize_y' in seam_material else [1,
                                                                                                                     1],
            }
        else:
            seam_mat = False
        color_mode = face_material['colorMode'] if 'colorMode' in face_material else None
        if color_mode is None:
            color_mode = face_material['useColor'] if 'useColor' in face_material else None
            if color_mode is not None:
                color_mode = 'color' if color_mode else 'texture'
        color = self.cvt_color(face_material['color']) if 'color' in face_material else None
        if color is None and jid not in ['', 'generated']:
            for _, mat in self.Materials.items():
                if 'seekId' not in mat or 'color' not in mat:
                    continue
                if mat['seekId'] == jid and 'color' in mat:
                    color = self.cvt_color(mat['color'])
                    break
        export_mat = {
            'jid': face_material['seekId'] if 'seekId' in face_material else 'generated',
            'texture_url': face_material['textureURI'] if 'textureURI' in face_material else '',
            'color': color,
            'colorMode': color_mode,
            'size': [face_material['tileSize_x'],
                     face_material[
                         'tileSize_y']] if 'tileSize_x' in face_material and 'tileSize_y' in face_material else [1, 1],
            'seam': seam_mat,
            'material_id': face_material['id'],
            'area': max_area
        }
        return export_mat

    def get_furnitures(self, custom=True):
        if not self.house_info:
            self.build()

        type_id_room_id_change = {}
        for room_type_id in self.rooms_wall_id_list:
            room_class_id = room_type_id.split('-')[1]
            type_id_room_id_change[room_class_id] = room_type_id

        self.Furnitures = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['Class'] == 'HSCore.Model.Content'])
        self.Products = dict([(item['id'], item) for item in self.label_dict['products'] if 'id' in item])
        room_polys = {}
        for room_info in self.house_info['room']:
            floor = np.reshape(room_info['floor'], [-1, 2])
            p = Polygon(floor)
            room_polys[room_info['id']] = p
        for _, fur in self.Furnitures.items():
            if 'flag' in fur:
                try:
                    b = bin(fur['flag'])[2:]
                    if len(b) > 4 and b[-5] == '1':
                        continue
                    if len(b) > 2 and b[-3] == '1':
                        continue
                except Exception as e:
                    print("furniture flag", fur['flag'], e)
                    continue

            if ('parents' in fur and len(fur['parents']) == 0) or (
                    'parents' in fur and fur['parents'][0] not in self.Layer.keys()):
                continue

            pos = [fur['x'], fur['y'], fur['z']]
            if None in pos:
                continue

            fur_room_id = None
            for room_id, poly in room_polys.items():
                if poly.contains(Point([pos[0], pos[1]])):
                    fur_room_id = room_id
                    break
            if fur_room_id is None:
                continue

            entityId = fur['id']
            rot = [fur['XRotation'] if 'XRotation' in fur else 0, fur['YRotation'] if 'YRotation' in fur else 0,
                   fur['ZRotation'] if 'ZRotation' in fur else 0]
            scale = [fur['XScale'] if 'XScale' in fur else 1, fur['YScale'] if 'YScale' in fur else 1,
                     fur['ZScale'] if 'ZScale' in fur else 1]
            size = [fur['XLength'] if 'XLength' in fur else None, fur['YLength'] if 'YLength' in fur else None,
                    fur['ZLength'] if 'ZLength' in fur else None]
            if None in size:
                size = []
            seekId = fur['seekId']
            if seekId not in self.Products:
                continue
            obj = self.Products[seekId]
            jid = obj['id']
            contentType = obj['contentType']
            categories = obj['categories'] if 'categories' in obj else []
            productStyle = obj['productStyle'] if 'productStyle' in obj else ''

            fur_info = {
                "id": jid,
                "type": contentType,
                "style": productStyle,
                "size": size,
                "scale": scale,
                "position": pos,
                "rotation": rot,
                "entityId": entityId,
                "categories": categories
            }

            for rid in range(len(self.house_info['room'])):
                if self.house_info['room'][rid]['id'] == fur_room_id:
                    self.house_info['room'][rid]['furniture_info'].append(fur_info)
                    break

        # 处理定制
        if custom:
            # 定制1 CustomizedModel
            for _, fur in self.CustomizedModel.items():
                if 'flag' in fur:
                    try:
                        b = bin(fur['flag'])[2:]
                        if len(b) > 4 and b[-5] == '1':
                            continue
                        if len(b) > 2 and b[-3] == '1':
                            continue
                    except Exception as e:
                        print("customizedModel flag", fur['flag'], e)
                        continue

                if ('parents' in fur and len(fur['parents']) == 0) or (
                        'parents' in fur and fur['parents'][0] not in self.Layer.keys()):
                    continue

                pos = [fur['x'], fur['y'], fur['z']]
                if None in pos:
                    continue

                fur_room_id = None
                for room_id, poly in room_polys.items():
                    if poly.contains(Point([pos[0], pos[1]])):
                        fur_room_id = room_id
                        break
                if fur_room_id is None:
                    continue

                entityId = fur['id']
                rot = [fur['XRotation'] if 'XRotation' in fur else 0, fur['YRotation'] if 'YRotation' in fur else 0,
                       fur['ZRotation'] if 'ZRotation' in fur else 0]
                scale = [fur['XScale'] if 'XScale' in fur else 1, fur['YScale'] if 'YScale' in fur else 1,
                         fur['ZScale'] if 'ZScale' in fur else 1]
                size = [fur['XLength'] if 'XLength' in fur else None, fur['YLength'] if 'YLength' in fur else None,
                        fur['ZLength'] if 'ZLength' in fur else None]
                if None in size:
                    size = []
                seekId = fur['seekId']
                if seekId not in self.Products:
                    continue
                obj = self.Products[seekId]
                jid = obj['id']
                contentType = obj['contentType']
                categories = obj['categories'] if 'categories' in obj else []
                productStyle = obj['productStyle'] if 'productStyle' in obj else ''

                fur_info = {
                    "classType": "CustomizedModel",
                    "id": jid,
                    "type": contentType,
                    "style": productStyle,
                    "size": size,
                    "scale": scale,
                    "position": pos,
                    "rotation": rot,
                    "entityId": entityId,
                    "categories": categories
                }

                for rid in range(len(self.house_info['room'])):
                    if self.house_info['room'][rid]['id'] == fur_room_id:
                        self.house_info['room'][rid]['custom_info'].append(fur_info)
                        break

            # 定制2 DAssembly
            for _, fur in self.DAssembly.items():
                if 'flag' in fur:
                    try:
                        b = bin(fur['flag'])[2:]
                        if len(b) > 4 and b[-5] == '1':
                            continue
                        if len(b) > 2 and b[-3] == '1':
                            continue
                    except Exception as e:
                        print("customizedModel flag", fur['flag'], e)
                        continue

                if ('parents' in fur and len(fur['parents']) == 0) or (
                        'parents' in fur and fur['parents'][0] not in self.Layer.keys()):
                    continue

                pos = [fur['x'], fur['y'], fur['z']]
                if None in pos:
                    continue

                fur_room_id = None
                for room_id, poly in room_polys.items():
                    if poly.contains(Point([pos[0], pos[1]])):
                        fur_room_id = room_id
                        break
                if fur_room_id is None:
                    continue

                entityId = fur['id']
                rot = [fur['XRotation'] if 'XRotation' in fur else 0, fur['YRotation'] if 'YRotation' in fur else 0,
                       fur['ZRotation'] if 'ZRotation' in fur else 0]
                scale = [fur['XScale'] if 'XScale' in fur else 1, fur['YScale'] if 'YScale' in fur else 1,
                         fur['ZScale'] if 'ZScale' in fur else 1]
                size = [fur['XLength'] if 'XLength' in fur else None, fur['YLength'] if 'YLength' in fur else None,
                        fur['ZLength'] if 'ZLength' in fur else None]
                if None in size:
                    size = []
                seekId = fur['seekId']

                instance_id = "DAssembly" + "-" + fur['id']

                fur_info = {
                    "classType": "DAssembly",
                    "id": instance_id,
                    "size": size,
                    "scale": scale,
                    "position": pos,
                    "rotation": rot,
                    "entityId": entityId
                }

                for rid in range(len(self.house_info['room'])):
                    if self.house_info['room'][rid]['id'] == fur_room_id:
                        self.house_info['room'][rid]['custom_info'].append(fur_info)
                        break

            # 定制3 PAssembly
            for _, fur in self.PAssembly.items():
                if 'flag' in fur:
                    try:
                        b = bin(fur['flag'])[2:]
                        if len(b) > 4 and b[-5] == '1':
                            continue
                        if len(b) > 2 and b[-3] == '1':
                            continue
                    except Exception as e:
                        print("customizedModel flag", fur['flag'], e)
                        continue

                if ('parents' in fur and len(fur['parents']) == 0) or (
                        'parents' in fur and fur['parents'][0] not in self.Layer.keys()):
                    continue

                pos_p = [fur['x'], fur['y'], fur['z']]
                pos = [self.State[i]['value'] for i in pos_p]

                if None in pos:
                    continue

                fur_room_id = None
                for room_id, poly in room_polys.items():
                    if poly.contains(Point([pos[0], pos[1]])):
                        fur_room_id = room_id
                        break
                if fur_room_id is None:
                    continue

                entityId = fur['id']
                rot_p = [fur['XRotation'] if 'XRotation' in fur else 0, fur['YRotation'] if 'YRotation' in fur else 0,
                       fur['ZRotation'] if 'ZRotation' in fur else 0]
                rot = [self.State[i]['value'] for i in rot_p]
                scale = [1, 1, 1]
                size_p = [fur['XLength'] if 'XLength' in fur else None, fur['YLength'] if 'YLength' in fur else None,
                        fur['ZLength'] if 'ZLength' in fur else None]
                size = [self.State[i]['value'] for i in size_p]
                if None in size:
                    size = []
                seekId = fur['seekId']

                fur_info = {
                    "classType": "PAssembly",
                    "id": seekId,
                    "size": size,
                    "scale": scale,
                    "position": pos,
                    "rotation": rot,
                    "entityId": entityId
                }

                for rid in range(len(self.house_info['room'])):
                    if self.house_info['room'][rid]['id'] == fur_room_id:
                        self.house_info['room'][rid]['custom_info'].append(fur_info)
                        break

    def cvt_color(self, in_color):
        out_color = []
        for i in range(3):
            out_color.append(in_color % 256)
            in_color = in_color // 256
        out_color.reverse()
        return out_color


if __name__ == '__main__':
    import numpy as np
    from LayoutDecoration.house_info import HouseData

    # file_path = os.path.join(os.path.dirname(__file__), '../temp', 'abcf60aa-2e3c-3053-981f-4f002d301fda.json')
    file_path = '/Users/liqing.zhc/Desktop/design_v2.json'
    design_json_file = json.load(open(file_path, 'r'))
    t = time.time()
    house_info = HouseInfoConvert(design_json_file)
    house_info.build(furniture=True, material=True)

    # HouseData(house_info.house_info, True)
    # print(house_info.house_info)
    for room_data in house_info.house_info['room']:
        floor_pts = np.reshape(room_data['floor'], [-1, 2])
        plt.plot(floor_pts[:, 0], floor_pts[:, 1])
    plt.show()
    print(time.time() - t)
