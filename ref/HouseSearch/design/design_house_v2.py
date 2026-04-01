import json
import math
import os
import time
import copy
import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import Polygon, Point
from HouseSearch.util import compute_poly_area


# 计算点是否在直线上(所在延长直线，不是线段)
def check_on_line_extend(pt, line):
    p1, p2 = line
    if np.linalg.norm(np.array(p1) - np.array(p2)) < 1e-3:
        if np.linalg.norm(np.array(p1) - np.array(pt)) < 1e-3:
            return True
        else:
            return False
    pf = pt
    pt1 = [pt[0] - p1[0], pt[1] - p1[1]]
    pt2 = [pt[0] - p2[0], pt[1] - p2[1]]

    cross = pt1[0] * pt2[1] - pt1[1] * pt2[0]
    return abs(cross) < 0.0001


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
        if check_on_line_extend(wall_info['from'], [p_from, p_to]) and check_on_line_extend(wall_info['to'], [p_from, p_to]):
            return_wall_list.append(wall_info)

        elif abs(wall_info['from'][0] - p_from[0]) + abs(wall_info['from'][1] - p_from[1]) < 0.01 \
                and abs(wall_info['to'][0] - p_to[0]) + abs(wall_info['to'][1] - p_to[1]) < 0.01:
            # print(p_from, p_to, wall_info)
            return_wall_list.append(wall_info)

        elif abs(wall_info['from'][0] - p_to[0]) + abs(wall_info['from'][1] - p_to[1]) < 0.01 \
                and abs(wall_info['to'][0] - p_from[0]) + abs(wall_info['to'][1] - p_from[1]) < 0.01:
            # print(p_from, p_to, wall_info)
            return_wall_list.append(wall_info)

    return return_wall_list


def check_flag(item):
    if 'flag' in item:
        try:
            b = bin(item['flag'])[2:]
            if len(b) > 4 and b[-5] == '1': # 第5位为隐藏
                return False
            if len(b) > 2 and b[-3] == '1': # 第3位为删除
                return False
        except Exception as e:
            print("furniture flag", item['flag'], e)
            return False
    return True


class HouseInfoConvertV2(object):
    def __init__(self, design_json, design_id=''):
        self.design_id = design_id
        self.label_dict = design_json
        self.house_info = None

        self.Floorplan = dict(
            zip([item['id'] for item in self.label_dict['data'] if 'Floorplan' in item['l'] == 'Floorplan'],
                [item for item in self.label_dict['data'] if item['l'] == 'Floorplan']))

        self.Scene = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Scene'],
                              [item for item in self.label_dict['data'] if item['l'] == 'Scene']))

        self.Layer = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Layer'],
                              [item for item in self.label_dict['data'] if item['l'] == 'Layer']))

        self.Room = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Floor'],
                             [item for item in self.label_dict['data'] if item['l'] == 'Floor']))
        self.Ceiling = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Ceiling'],
                                     [item for item in self.label_dict['data'] if item['l'] == 'Ceiling']))

        self.Wall = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Wall'],
                             [item for item in self.label_dict['data'] if item['l'] == 'Wall']))

        self.Face = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Face'],
                             [item for item in self.label_dict['data'] if item['l'] == 'Face']))

        self.Loop = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Loop'],
                             [item for item in self.label_dict['data'] if item['l'] == 'Loop']))

        self.CoEdge = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'CoEdge'],
                [item for item in self.label_dict['data'] if item['l'] == 'CoEdge']))

        self.Edge = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Edge'],
                             [item for item in self.label_dict['data'] if item['l'] == 'Edge']))

        self.Vertex = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Vertex'],
                [item for item in self.label_dict['data'] if item['l'] == 'Vertex']))

        self.Door = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] in ['Door']],
                             [item for item in self.label_dict['data'] if item['l'] in ['Door']]))
        self.Window = {}

        # 0.29 openings 先找hole
        self.WindowBaseHole = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['l'] in ['Window',
                                                                                     'CornerWindow',
                                                                                     'POrdinaryWindow',
                                                                                     'CornerFlatWindow',
                                                                                     'WindowHole',
                                                                                     'BayWindow',
                                                                                 'ParmWinHole']],
                [item for item in self.label_dict['data'] if item['l'] in ['Window',
                                                                               'CornerWindow',
                                                                               'POrdinaryWindow',
                                                                               'CornerFlatWindow',
                                                                               'WindowHole',
                                                                               'BayWindow',
                                                                           'ParmWinHole']]))

        self.WindowState = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['l'] in ['POrdWindow', 'CorFWindow']],# POrdWindow 普通窗/落地窗
                [item for item in self.label_dict['data'] if item['l'] in ['POrdWindow', 'CorFWindow']]))# CorFWindow 转角窗

        self.BayWindowState = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['l'] in ['BayWindow', 'CorWindow']],# BayWindow 普通窗
                [item for item in self.label_dict['data'] if item['l'] in ['BayWindow', 'CorWindow']]))# CorFWindow 转角飘窗

        self.Hole = dict(zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Hole'],
                             [item for item in self.label_dict['data'] if item['l'] == 'Hole']))

        self.BayWindow = {}

        self.Pocket = dict(
            zip([item['id'] for item in self.label_dict['data'] if item['l'] == 'Pocket'],
                [item for item in self.label_dict['data'] if item['l'] == 'Pocket']))

        self.Materials = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['l'] == 'Material'])
        if 'materials' in self.label_dict:
            materialData = dict(
                [(item['id'], item) for item in self.label_dict['materials'] if
                 item['l'] == 'MaterialData'])
            for k, v in materialData.items():
                if k not in self.Materials:
                    self.Materials[k] = v
        if 'materials' in self.label_dict:
            materialData = dict(
                [(item['id'], item) for item in self.label_dict['materials'] if
                 item['l'] == 'MatData'])
            for k, v in materialData.items():
                if k not in self.Materials:
                    self.Materials[k] = v
            # self.Materials.update(dict(
            #     [(item['id'], item) for item in self.label_dict['materials'] if
            #      item['l'] == 'MaterialData']))
        self.Mixpaint = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['l'] == 'Mixpaint'])
        self.Polygon = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['l'] == 'Polygon'])
        self.Pattern = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['l'] == 'Pattern'])
        self.Block = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['l'] == 'Block'])
        self.Openings = {}
        self.rooms_wall_id_list = {}
        self.ceiling_dict = {}
        self.room_ceiling_dict = {}

        # opening根据ParmWinHole找到对应的窗类型
        for key in self.WindowBaseHole:
            holeInfo = self.WindowBaseHole[key]
            if "p" in holeInfo and len(holeInfo["p"]) > 0:
                p = holeInfo["p"][0]

                if p in self.WindowState:
                    self.Window[key] = holeInfo
                    if "parameters" in self.WindowState[p]:
                        if "elevation" in self.WindowState[p]["parameters"]:
                            height = self.WindowState[p]["parameters"]["elevation"]
                            if height < 0.3:
                                holeInfo["elevation"] = height

                elif p in self.BayWindowState:
                    self.BayWindow[key] = holeInfo
                    if "parameters" in self.BayWindowState[p]:
                        if "elevation" in self.BayWindowState[p]["parameters"]:
                            height = self.BayWindowState[p]["parameters"]["elevation"]
                            if height < 0.3:
                                holeInfo["elevation"] = height

                else:
                    self.Window[key] = holeInfo
                    if "z" in holeInfo:
                        if holeInfo["z"] < 0.3:
                            holeInfo["elevation"] = holeInfo["z"]
                        else:
                            holeInfo["elevation"] = 0.6

    def build(self, furniture=False, material=False):
        if self.house_info:
            return self.house_info

        wall_table = {}
        opening_table = {}
        opening_id_check = {}
        for wall_id, wall in self.Wall.items():
            from_p = self.Vertex[wall['from']]
            to_p = self.Vertex[wall['to']]
            if 'openings' in wall:
                opening_list = wall['openings']
            else:
                opening_list = []
            wall_table[wall_id] = {'id': wall_id, 'width': wall['width'], 'from': [from_p['x'], from_p['y']],
                                   'to': [to_p['x'], to_p['y']], "openings": opening_list}

        for ceiling_id, ceiling in self.Ceiling.items():
            loop_id = ceiling['outerLoop']
            loop = self.Loop[loop_id]

            sorted_coedges = []
            if len(loop['c']) > 0:
                sorted_coedges = [loop['c'][0]]
                while True:
                    next_coedge = self.CoEdge[sorted_coedges[-1]]['next']
                    if next_coedge in sorted_coedges:
                        break
                    sorted_coedges.append(next_coedge)

            contour = []
            for _, edge_id in enumerate(sorted_coedges):
                edge = self.Edge[self.CoEdge[edge_id]['c'][0]]

                from_p = self.Vertex[edge['ln'][0]]
                # to_p = self.Vertex[edge['ln'][1]]
                contour.append([from_p['x'], from_p['y']])
            self.ceiling_dict[ceiling_id] = contour

        room_list = []
        for room_id, room in self.Room.items():
            # print(room)
            room_type = "none"
            if "roomType" in room:
                room_type = room['roomType']
            room_info = {'id': room_type + '-' + room_id, 'type': room_type, 'floor': [], 'door_info': [],
                         'window_info': [], 'hole_info': [], 'baywindow_info': [], 'wall_width': [],
                         'furniture_info': [],
                         'material_info': []}
            self.rooms_wall_id_list[room_type + '-' + room_id] = []
            loop_id = room['c'][0]
            loop = self.Loop[loop_id]
            wall_idx = -1

            # plt.figure()
            # plt.axis('equal')
            # plt.title(room_type)
            sorted_coedges = []
            if len(loop['c']) > 0:
                sorted_coedges = [loop['c'][0]]
                while True:
                    next_coedge = self.CoEdge[sorted_coedges[-1]]['next']
                    if next_coedge in sorted_coedges:
                        break
                    sorted_coedges.append(next_coedge)

            # show_data_x = []
            # show_data_y = []
            for _, edge_id in enumerate(sorted_coedges):
                wall_idx += 1
                edge = self.Edge[self.CoEdge[edge_id]['c'][0]]

                from_p = self.Vertex[edge['ln'][0]]
                to_p = self.Vertex[edge['ln'][1]]
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
                        if wall_info_id in opening_table:
                            opening_table[wall_info_id].append(room_type + '-' + room_id)
                        else:
                            opening_table[wall_info_id] = [room_type + '-' + room_id]

                        wall_width = wall_info['width']
                        if 'openings' in wall_info:
                            for open_id in wall_info['openings']:
                                # 添加门信息
                                if open_id in self.Door and check_flag(self.Door[open_id]):
                                    door_info = self.get_component_info(self.Door[open_id], from_p, to_p)
                                    if len(door_info['pts']) > 0:
                                        room_info['door_info'].append(door_info)
                                        room_info['door_info'][-1]['wall_idx'] = wall_idx
                                        room_info['door_info'][-1]['to'] = open_id

                                        if open_id not in opening_id_check:
                                            opening_id_check[open_id] = [room_type + '-' + room_id]
                                        else:
                                            opening_id_check[open_id] += [room_type + '-' + room_id]

                                        if open_id not in self.Openings:
                                            self.Door[open_id]['room_id'] = room_type + '-' + room_id
                                            self.Openings[open_id] = self.Door[open_id]

                                # 添加窗信息
                                if open_id in self.Window and check_flag(self.Window[open_id]):
                                    window_info = self.get_component_info(self.Window[open_id], from_p, to_p)
                                    if len(window_info['pts']) > 0:
                                        room_info['window_info'].append(window_info)
                                        room_info['window_info'][-1]['wall_idx'] = wall_idx
                                        room_info['window_info'][-1]['to'] = open_id
                                        if "elevation" in self.Window[open_id]:
                                            room_info['window_info'][-1]['height'] = self.Window[open_id][
                                                "elevation"]

                                        if open_id not in opening_id_check:
                                            opening_id_check[open_id] = [room_type + '-' + room_id]
                                        else:
                                            opening_id_check[open_id] += [room_type + '-' + room_id]

                                        if open_id not in self.Openings:
                                            self.Window[open_id]['room_id'] = room_type + '-' + room_id
                                            self.Openings[open_id] = self.Window[open_id]

                                # 添加洞信息 按门处理
                                if open_id in self.Hole and check_flag(self.Hole[open_id]):
                                    hole_info = self.get_component_info(self.Hole[open_id], from_p, to_p)
                                    if len(hole_info['pts']) > 0:
                                        room_info['hole_info'].append(hole_info)
                                        room_info['hole_info'][-1]['wall_idx'] = wall_idx
                                        room_info['hole_info'][-1]['to'] = open_id

                                    if open_id not in opening_id_check:
                                        opening_id_check[open_id] = [room_type + '-' + room_id]
                                    else:
                                        opening_id_check[open_id] += [room_type + '-' + room_id]

                                    if open_id not in self.Openings:
                                        self.Hole[open_id]['room_id'] = room_type + '-' + room_id
                                        self.Openings[open_id] = self.Hole[open_id]

                                # 添加洞信息 按门处理
                                if open_id in self.BayWindow and check_flag(self.BayWindow[open_id]):
                                    hole_info = self.get_component_info(self.BayWindow[open_id], from_p, to_p)
                                    if len(hole_info['pts']) > 0:
                                        room_info['baywindow_info'].append(hole_info)
                                        room_info['baywindow_info'][-1]['wall_idx'] = wall_idx
                                        room_info['baywindow_info'][-1]['to'] = open_id

                                        if open_id not in opening_id_check:
                                            opening_id_check[open_id] = [room_type + '-' + room_id]
                                        else:
                                            opening_id_check[open_id] += [room_type + '-' + room_id]

                                        if "elevation" in self.BayWindow[open_id]:
                                            room_info['baywindow_info'][-1]['height'] = self.BayWindow[open_id]["elevation"]

                                        if open_id not in self.Openings:
                                            self.BayWindow[open_id]['room_id'] = room_type + '-' + room_id
                                            self.Openings[open_id] = self.BayWindow[open_id]

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
            for door_info in room_info['door_info'] + room_info['hole_info'] + room_info['window_info'] + room_info['baywindow_info']:
                open_idx = door_info['to']
                door_info['to'] = ''
                if open_idx not in opening_id_check:
                    continue
                else:
                    for target_id in opening_id_check[open_idx]:
                        if target_id != room_id:
                            door_info['to'] = target_id
                            break

            try:
                room_floor_poly = Polygon(np.reshape(room_info['floor'], [-1, 2]))
                max_inter = 0.
                max_ceiling_id = -1
                for cid, ceiling in self.ceiling_dict.items():
                    ceiling_poly = Polygon(ceiling)
                    inter_area = room_floor_poly.intersection(ceiling_poly).area
                    if inter_area > max_inter:
                        max_inter = inter_area
                        max_ceiling_id = cid
                if max_ceiling_id != -1:
                    self.room_ceiling_dict[room_id] = max_ceiling_id
            except:
                pass

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

    def get_materials(self):
        if not self.house_info:
            self.build()

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

            mat_info = {'id': room_id, 'type': room_type, 'floor': [], 'ceiling': [], 'wall': [],
                        'win_pocket': [], 'door_pocket': []}
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

            # ceiling material
            if room_id in self.room_ceiling_dict and 'material' in self.Ceiling[self.room_ceiling_dict[room_id]]:
                ceiling_mat_id = self.Ceiling[self.room_ceiling_dict[room_id]]['material']
                ceiling_export_mat = self.get_face_material(ceiling_mat_id)
                if ceiling_export_mat['area'] == -1:
                    for room_info in self.house_info['room']:
                        if room_info['id'] == room_id:
                            ceiling_export_mat['area'] = room_info['area']
                            break

                in_list = False
                for m_ind, ceiling_mat in enumerate(mat_info['ceiling']):
                    if ceiling_mat['jid'] == ceiling_export_mat['jid'] and ceiling_mat['jid'] not in ['', 'generated']:
                        in_list = True
                        if len(ceiling_mat['texture_url']) == 0 and len(ceiling_export_mat['texture_url']) > 0:
                            mat_info['ceiling'][m_ind]['texture_url'] = ceiling_export_mat['texture_url']
                        break
                if not in_list:
                    mat_info['ceiling'].append(ceiling_export_mat)

            # wall material
            loop_id = room['c'][0]
            loop = self.Loop[loop_id]
            wall_idx = -1

            sorted_coedges = []
            if len(loop['c']) > 0:
                sorted_coedges = [loop['c'][0]]
                while True:
                    next_coedge = self.CoEdge[sorted_coedges[-1]]['next']
                    if next_coedge in sorted_coedges:
                        break
                    sorted_coedges.append(next_coedge)
            if len(sorted_coedges) > 1:
                edge1 = self.Edge[self.CoEdge[sorted_coedges[0]]['c'][0]]
                edge2 = self.Edge[self.CoEdge[sorted_coedges[1]]['c'][0]]
                if edge1['ln'][1] != edge2['ln'][0]:
                    sorted_coedges.reverse()
            sorted_coedges_floor_pts = []
            for _, edge_id in enumerate(sorted_coedges):
                edge = self.Edge[self.CoEdge[edge_id]['c'][0]]
                from_p = self.Vertex[edge['ln'][0]]
                to_p = self.Vertex[edge['ln'][1]]
                # floor_vec = np.array([to_p['x'], to_p['y']]) - np.array([from_p['x'], from_p['y']])
                sorted_coedges_floor_pts.append([from_p['x'], from_p['y']])

            room_poly = Polygon(sorted_coedges_floor_pts)
            for ind, edge_id in enumerate(sorted_coedges):
                wall_idx += 1
                edge = self.Edge[self.CoEdge[edge_id]['c'][0]]
                from_p = self.Vertex[edge['ln'][0]]
                to_p = self.Vertex[edge['ln'][1]]
                floor_vec = np.array([to_p['x'], to_p['y']]) - np.array([from_p['x'], from_p['y']])
                # plt.arrow(from_p['x'], from_p['y'], to_p['x'] - from_p['x'], to_p['y'] - from_p['y'],  # 坐标与距离
                #           head_width=0.2, lw=2,  # 箭头⻓度，箭尾线宽
                #           length_includes_head=True)  # ⻓度计算包含箭头箭尾
                wall_info_list = get_wall_info(from_p, to_p, wall_table)
                for wall in wall_info_list:
                    wall_vec = np.array(wall['to']) - np.array(wall['from'])
                    wall_length = np.linalg.norm(wall_vec)
                    face_ids = self.get_room_face(wall, room_poly)
                    # if np.dot(floor_vec, wall_vec) > 0:
                    #     face_ids = wall['left']
                    # else:
                    #     face_ids = wall['right']
                    for face_id in face_ids:
                        inner_face_mat_ind = self.Face[face_id]['material']
                        export_mat = self.get_face_material(inner_face_mat_ind)
                        export_mat['wall'] = [wall['from'], wall['to']]
                        in_list = False
                        for m_ind, wall_mat in enumerate(mat_info['wall']):
                            if wall_mat['jid'] == export_mat['jid'] and wall_mat['jid'] not in ['', 'generated']:
                                # in_list = True
                                # wall_lens[m_ind] += wall_length
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

    def get_room_face(self, wall, room_poly):

        # wall_from_p = wall['from']
        # wall_to_p = wall['to']
        # wall_vec = np.array(wall_to_p) - np.array(wall_from_p)
        faces = []
        # left
        left_face_ids = wall['left']
        for fid in left_face_ids:
            outer_loop = self.Loop[self.Face[fid]['outerLoop']]

            sorted_coedges = []
            if len(outer_loop['c']) > 0:
                sorted_coedges = [outer_loop['c'][0]]
                while True:
                    next_coedge = self.CoEdge[sorted_coedges[-1]]['next']
                    if next_coedge in sorted_coedges:
                        break
                    sorted_coedges.append(next_coedge)

            left_from_p = []
            for coedge in sorted_coedges:
                # coedge = self.Loop[outer_loop]['children'][0]
                edge = self.Edge[self.CoEdge[coedge]['c'][0]]
                left_from_p.append([self.Vertex[edge['ln'][0]]['x'], self.Vertex[edge['ln'][0]]['y']])
            left_from_p = np.mean(left_from_p, axis=0)

            if room_poly.contains(Point(left_from_p)):
                faces.append(fid)
            # print('left')
        # left
        right_face_ids = wall['right']
        for fid in right_face_ids:
            outer_loop = self.Loop[self.Face[fid]['outerLoop']]

            sorted_coedges = []
            if len(outer_loop['c']) > 0:
                sorted_coedges = [outer_loop['c'][0]]
                while True:
                    next_coedge = self.CoEdge[sorted_coedges[-1]]['next']
                    if next_coedge in sorted_coedges:
                        break
                    sorted_coedges.append(next_coedge)

            right_from_p = []
            for coedge in sorted_coedges:
                # coedge = self.Loop[outer_loop]['children'][0]
                edge = self.Edge[self.CoEdge[coedge]['c'][0]]
                right_from_p.append([self.Vertex[edge['ln'][0]]['x'], self.Vertex[edge['ln'][0]]['y']])
            right_from_p = np.mean(right_from_p, axis=0)
            # to_p = self.Vertex[edge['to']]
            if room_poly.contains(Point(right_from_p)):
                faces.append(fid)
            # print('right')
        return faces

    def get_face_material(self, mat_id):
        wall_material = self.Materials[mat_id]
        face_material = copy.deepcopy(wall_material)
        seam_material = None
        texture_url_dict = {}
        jid = face_material['seekId'] if 'seekId' in face_material else 'generated'
        if len(jid.split('-')) != 5:
            face_material['seekId'] = ''
        # if jid in ['', 'generated'] and 'textureURI' in face_material and face_material['textureURI'] != '':
        #     face_material['seekId'] = face_material['textureURI'].split('/')[-2]
        #     jid = face_material['seekId']
        # if jid not in ['', 'generated'] and 'textureURI' in face_material and face_material['textureURI'] != '':
        #     texture_url_dict[jid] = face_material['textureURI']
        max_area = -1
        if 'mixpaint' in face_material:
            mixpaint = self.Mixpaint[face_material['mixpaint']]
            if 'c' in mixpaint and len(mixpaint['c']) > 0 and len(self.Polygon) > 0:

                polygon_inds = mixpaint['c']
                max_polygon_ind = -1
                for polygon_ind in polygon_inds:
                    if polygon_ind not in self.Polygon:
                        continue
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
                if max_polygon_ind in self.Polygon:
                    polygon = self.Polygon[max_polygon_ind]
                    polygon_material = polygon['material']
                    if isinstance(polygon_material, str):
                        polygon_material = self.Materials[polygon_material]
                    else:
                        if 'id' not in polygon_material:
                            polygon_material['id'] = max_polygon_ind
                    face_material = copy.deepcopy(polygon_material)
                    jid = face_material['seekId'] if 'seekId' in face_material else 'generated'
                    if len(jid.split('-')) != 5:
                        face_material['seekId'] = ''
                    # if jid in ['', 'generated'] and 'textureURI' in face_material and face_material['textureURI'] != '':
                    #     face_material['seekId'] = face_material['textureURI'].split('/')[-2]
                    #     jid = face_material['seekId']
                    # if jid in texture_url_dict and ('textureURI' not in face_material or face_material['textureURI'] == ''):
                    #     face_material['textureURI'] = texture_url_dict[jid]
                    if 'pattern' in polygon:
                        pattern = self.Pattern[polygon['pattern']]
                        if 'children' in pattern and len(pattern['children']) > 0 and pattern['children'][0] in self.Block:
                            block = self.Block[pattern['children'][0]]
                            block_material = self.Materials[block['material']]
                            face_material = copy.deepcopy(block_material)
                            jid = face_material['seekId'] if 'seekId' in face_material else 'generated'
                            if len(jid.split('-')) != 5:
                                face_material['seekId'] = ''
                            # if jid in ['', 'generated'] and 'textureURI' in face_material and face_material[
                            #     'textureURI'] != '':
                            #     face_material['seekId'] = face_material['textureURI'].split('/')[-2]
                            #     jid = face_material['seekId']
                            # if jid in texture_url_dict and (
                            #         'textureURI' not in face_material or face_material['textureURI'] == ''):
                            #     face_material['textureURI'] = texture_url_dict[jid]

                            if 'seamMaterial' in pattern:
                                seam_material = self.Materials[pattern['seamMaterial']] if isinstance(pattern['seamMaterial'], str) else pattern['seamMaterial']
                            elif 'seam' in pattern:
                                if 'material' in pattern['seam']:
                                    seam_material = self.Materials[pattern['seam']['material']] if isinstance(pattern['seam']['material'], str) else pattern['seam']['material']
        if seam_material is not None:
            color_mode = seam_material['colorMode'] if 'colorMode' in seam_material else None
            if color_mode is None:
                color_mode = seam_material['useColor'] if 'useColor' in seam_material else None
                if color_mode is not None:
                    color_mode = 'color' if color_mode else 'texture'
            seam_color = self.cvt_color(seam_material['color']) if 'color' in seam_material else None

            seam_jid = seam_material['seekId'] if 'seekId' in seam_material else 'generated'
            if len(seam_jid.split('-')) != 5:
                seam_material['seekId'] = ''
            # if seam_jid in ['', 'generated'] and 'textureURI' in seam_material and seam_material[
            #     'textureURI'] != '':
            #     seam_material['seekId'] = seam_material['textureURI'].split('/')[-2]
            #     seam_jid = seam_material['seekId']
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
                             'tileSize_y']] if 'tileSize_x' in seam_material and 'tileSize_y' in seam_material else [1, 1],
            }
            if len(seam_mat['texture_url']) == 0:
                seam_mat['colorMode'] = 'color'
            else:
                seam_mat['colorMode'] = 'texture'
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
                     face_material['tileSize_y']] if 'tileSize_x' in face_material and 'tileSize_y' in face_material else [1, 1],
            'seam': seam_mat,
            'material_id': face_material['id'],
            'area': max_area
        }
        if len(export_mat['texture_url']) == 0:
            export_mat['colorMode'] = 'color'
        else:
            export_mat['colorMode'] = 'texture'
        return export_mat

    def get_furnitures(self):
        if not self.house_info:
            self.build()

        type_id_room_id_change = {}
        for room_type_id in self.rooms_wall_id_list:
            room_class_id = room_type_id.split('-')[1]
            type_id_room_id_change[room_class_id] = room_type_id

        self.Furnitures = dict(
            [(item['id'], item) for item in self.label_dict['data'] if item['l'] == 'Content'])
        self.Products = dict([(item['id'], item) for item in self.label_dict['products'] if 'id' in item])
        room_polys = {}
        for room_info in self.house_info['room']:
            floor = np.reshape(room_info['floor'], [-1, 2])
            p = Polygon(floor)
            room_polys[room_info['id']] = p

        for fur in list(self.Furnitures.values()) + list(self.Openings.values()):
            if not check_flag(fur):
                continue

            if ('p' in fur and len(fur['p']) == 0) or ('p' in fur and fur['p'][0] not in self.Layer.keys()):
                continue

            pos = [fur['x'], fur['y'], fur['z']]
            if None in pos:
                continue

            if 'room_id' in fur:
                fur_room_id = fur['room_id']
            else:
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

            contentType = obj['contentType'] if "contentType" in obj else ''
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
            if 'pocket' in fur:
                pocket = self.Pocket[fur['pocket']]
                if 'material' in pocket:
                    fur_info['pocket'] = self.get_face_material(pocket['material'])
            for rid in range(len(self.house_info['room'])):
                if self.house_info['room'][rid]['id'] == fur_room_id:
                    self.house_info['room'][rid]['furniture_info'].append(fur_info)
                    break

    def cvt_color(self, in_color):
        out_color = []
        for i in range(3):
            out_color.append(in_color % 256)
            in_color = in_color // 256
        out_color.reverse()
        return out_color

    def get_component_info(self, component, from_p, to_p):
        assert (component['l'] in ['Door', 'Window', 'Hole',
                                       'CornerWindow',
                                       'POrdinaryWindow', 'CornerFlatWindow',
                                       'BayWindow', 'WindowHole', 'ParmWinHole',''])
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
        if component['l'] == 'Door':
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

        if check_on_line(coord, [[from_p['x'], from_p['y']], [to_p['x'], to_p['y']]]):
            out_pts = []
        else:
            return {'pts': [], 'to': '', 'width': length[1], 'wall_idx': 0, 'main_pts': component_main_pts}

        # 修正hole的宽度 from statistics
        if component['l'] == 'Hole':
            init_vector = [[-x_half_len, y_half_len], [-x_half_len, -y_half_len],
                           [x_half_len, -y_half_len], [x_half_len, y_half_len]]

            for pt in init_vector:
                out_pts += [pt[0] * cos_ang - pt[1] * sin_ang + coord[0], pt[0] * sin_ang + pt[1] * cos_ang + coord[1]]

        # 修正door的宽度 from statistics
        if component['l'] == 'Door':
            init_vector = [[-x_half_len, y_half_len], [-x_half_len, -y_half_len],
                           [x_half_len, -y_half_len], [x_half_len, y_half_len]]

            for pt in init_vector:
                out_pts += [pt[0] * cos_ang - pt[1] * sin_ang + coord[0], pt[0] * sin_ang + pt[1] * cos_ang + coord[1]]

        # 修正 window from statistics
        if component['l'] in ['Window', 'WindowHole']:
            init_vector = [[-x_half_len, y_half_len], [-x_half_len, -y_half_len],
                           [x_half_len, -y_half_len], [x_half_len, y_half_len]]

            for pt in init_vector:
                out_pts += [pt[0] * cos_ang - pt[1] * sin_ang + coord[0], pt[0] * sin_ang + pt[1] * cos_ang + coord[1]]

        # 修正 window from statistics
        if component['l'] in ['BayWindow', 'ParmWinHole']:
            init_vector = [[-x_half_len, y_half_len], [-x_half_len, -y_half_len],
                           [x_half_len, -y_half_len], [x_half_len, y_half_len]]

            for pt in init_vector:
                out_pts += [pt[0] * cos_ang - pt[1] * sin_ang + coord[0], pt[0] * sin_ang + pt[1] * cos_ang + coord[1]]

        component_info = {'pts': out_pts, 'to': '', 'width': length[1], 'wall_idx': 0, 'main_pts': component_main_pts}
        return component_info
