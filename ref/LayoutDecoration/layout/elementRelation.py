import copy
import numpy as np
from LayoutDecoration.Base.math_util import get_pt_distance, convex_p_find, compute_line_face_normal


# 墙线段上挖出新的墙线段, pts
from LayoutDecoration.Base.math_util import check_pt_in_line
from LayoutDecoration.Base.recon_params import *


class ElementRelation(object):
    def __init__(self, room_type, room_id, mesh_uid_str, floor_pts, floor_wall_info, door_info_dict, window_info_dict,
                 build_params, skip_wall_inds=[]):
        self.uid = mesh_uid_str
        self.room_id = room_id
        self.room_type = room_type
        self.floor_pts = floor_pts
        self.floor_wall_info = floor_wall_info

        poly = [[floor_pts[pt][0], floor_pts[pt][1]] for pt in range(len(floor_pts))]

        self.element_info = {}

        self.build_params = build_params
        self.skip_wall_inds = skip_wall_inds

        self.build_wall_elements(poly, door_info_dict, window_info_dict)

    def build_wall_elements(self, wall_pts_list, door_info_dict, window_info_dict):
        # 主题墙、背景墙、普通墙配置
        if 'param_main_wall' not in self.build_params:
            self.build_params['param_main_wall'] = get_default_wall_info()
        param_wall_info = self.build_params['param_main_wall']

        # 踢脚线配置
        if 'param_baseboard' not in self.build_params:
            self.build_params['param_baseboard'] = get_default_baseboard_info()
        param_baseboard_info = self.build_params['param_baseboard']

        # 门与门框配置
        if 'param_door' not in self.build_params:
            self.build_params['param_door'] = get_default_door_info()
        param_door_info = self.build_params['param_door']

        # 窗与窗框配置
        if 'param_window' not in self.build_params:
            self.build_params['param_window'] = get_default_window_info()
        param_window_info = self.build_params['param_window']

        convex_list = convex_p_find(wall_pts_list)
        for floor_idx in range(len(wall_pts_list)):
            self.element_info[floor_idx] = []
            if floor_idx in self.skip_wall_inds:
                continue
            start_pt = wall_pts_list[floor_idx]
            end_pt = wall_pts_list[(floor_idx + 1) % len(wall_pts_list)]
            offset_dir = compute_line_face_normal(start_pt, end_pt,
                                                  wall_pts_list[(floor_idx - 1) % len(wall_pts_list)],
                                                  convex_list[floor_idx])
            u_dir = [end_pt[0]-start_pt[0], 0.0, end_pt[1]-start_pt[1]]
            offset_dir = [-offset_dir[0], -offset_dir[1]]

            # 处理面墙线，将门窗填入
            element_info = {'Door': [], 'Window': [], 'BaseBoard': [], 'WallInner': []}
            for wall_idx in range(len(self.floor_wall_info[floor_idx])):
                line_pts_list = [self.floor_wall_info[floor_idx][wall_idx]['inner_pts'][0],
                                 self.floor_wall_info[floor_idx][wall_idx]['inner_pts'][1]]
                line_pts_type = [{'type': 0, 'bottom': 0, 'top': 0}, {'type': 0, 'bottom': 0, 'top': 0}]
                # self.mesh_info[floor_idx] = {'Door': [], 'Window': [], 'BaseBoard': [], 'WallInner': []}

                baseboard_type = []
                baseboard_pts = []

                # 配置门与窗
                if floor_idx in door_info_dict:
                    for door in door_info_dict[floor_idx]:
                        if door['wall_ind'] == wall_idx:
                            line_pts_list, line_pts_type, element_info = self.add_door_to_line(door,
                                                                                            line_pts_list,
                                                                                            line_pts_type,
                                                                                            offset_dir, param_door_info,
                                                                                            element_info)
                if floor_idx in window_info_dict:
                    for window in window_info_dict[floor_idx]:
                        if window['wall_ind'] == wall_idx:
                            line_pts_list, line_pts_type, element_info = self.add_window_to_line(window,
                                                                                              line_pts_list,
                                                                                              line_pts_type, offset_dir,
                                                                                              param_window_info,
                                                                                              element_info)
                for i in range(len(line_pts_type)):
                    if line_pts_type[i]['type'] == 2:
                        continue
                    else:
                        baseboard_type.append(2)
                        baseboard_pts.append(line_pts_list[i])

                baseboard_type[0] = convex_list[floor_idx]
                baseboard_type[-1] = convex_list[(floor_idx + 1) % len(wall_pts_list)]
                for line_idx in range(len(baseboard_pts) // 2):
                    line_start = baseboard_pts[2 * line_idx]
                    line_end = baseboard_pts[2 * line_idx + 1]

                    connect_type = [baseboard_type[2 * line_idx], baseboard_type[2 * line_idx + 1]]
                    element_info['BaseBoard'].append(
                        {
                            'floor_ind': floor_idx,
                            'wall_ind': wall_idx,
                            'line_ind': line_idx,
                            'start': line_start,
                            'end': line_end,
                            'connect_type': connect_type,
                            'normal': offset_dir

                        }
                    )
                segment = copy.deepcopy(self.floor_wall_info[floor_idx][wall_idx])
                segment['line_pts_list'] = line_pts_list
                segment['line_pts_type'] = line_pts_type
                element_info['WallInner'].append(
                    {
                        'u_dir': u_dir.copy(),
                        'offset_dir': offset_dir.copy(),
                        'line_pts_list': line_pts_list.copy(),
                        'line_pts_type': line_pts_type.copy(),
                        'segment': segment,
                        'height': param_wall_info['normal_height']
                    }
                )
                self.element_info[floor_idx] = element_info

    def add_door_to_line(self, door_info, line_pts_list, line_pts_type, wall_offset_dir,
                         param_info, mesh_info):
        if door_info['to'] == '' or self.room_id == '':
            door_type = 'Entry'
        elif 'BathRoom' in [ROOM_BUILD_TYPE[self.room_type], ROOM_BUILD_TYPE[door_info['to_type']]]:
            door_type = 'Bathroom'
        elif 'Kitchen' in [ROOM_BUILD_TYPE[self.room_type], ROOM_BUILD_TYPE[door_info['to_type']]]:
            door_type = 'Kitchen'
        elif 'Balcony' in [ROOM_BUILD_TYPE[self.room_type], ROOM_BUILD_TYPE[door_info['to_type']]]:
            door_type = 'Balcony'
        else:
            door_type = 'Other'
        door_info['type'] = door_type
        # 两点为一个墙线段
        # pts = [door_info[1], door_info[2]]
        pts = door_info['wall_pts']
        if len(pts) != 2:
            return line_pts_list

        for line_idx in range(len(line_pts_list) // 2 - 1, -1, -1):
            wall_start = line_pts_list[2 * line_idx]
            wall_end = line_pts_list[2 * line_idx + 1]

            in_line, pt = check_pt_in_line(pts[0], [wall_start, wall_end])
            door_info['wall_pts'][0] = copy.deepcopy(pt)
            if in_line:
                # 按墙线顺序添加开放空间
                in_line, pt = check_pt_in_line(pts[1], [pts[0], wall_end])
                door_info['wall_pts'][1] = copy.deepcopy(pt)
                if in_line:
                    line_pts_list.insert(2 * line_idx + 1, pts[0])
                    line_pts_list.insert(2 * line_idx + 2, pts[1])

                    # 添加门的信息
                    mesh_info = self.build_door_window_element(mesh_info, door_info, wall_offset_dir, param_info)
                    line_pts_type.insert(2 * line_idx + 1, {'type': 1, 'height': param_info['door_height']})
                    line_pts_type.insert(2 * line_idx + 2, {'type': 1, 'height': param_info['door_height']})

                else:
                    in_line, pt = check_pt_in_line(pts[0], [pts[1], wall_end])
                    door_info['wall_pts'][0] = copy.deepcopy(pt)
                    if in_line:
                        line_pts_list.insert(2 * line_idx + 1, pts[1])
                        line_pts_list.insert(2 * line_idx + 2, pts[0])

                        # 添加门的信息
                        mesh_info = self.build_door_window_element(mesh_info, door_info, wall_offset_dir, param_info)
                        line_pts_type.insert(2 * line_idx + 1, {'type': 1, 'height': param_info['door_height']})
                        line_pts_type.insert(2 * line_idx + 2, {'type': 1, 'height': param_info['door_height']})

                break

        return line_pts_list, line_pts_type, mesh_info

    def add_window_to_line(self, window_info, line_pts_list, line_pts_type, wall_offset_dir, param_info, mesh_info):
        # 两点为一个墙线段
        # pts = [window_info[1], window_info[2]]
        pts = window_info['wall_pts']
        if len(pts) != 2:
            return line_pts_list
        window_length = get_pt_distance(pts[0], pts[1])
        if window_info['baywindow']:
            param_info['window_height'] = window_info['height']
            param_info['window_top'] = 2.0
        else:
            if self.room_type == 'Kitchen':
                param_info['window_height'] = 1.0
                param_info['window_top'] = 2.0
            elif window_length > 2.5:
                # 落地窗
                param_info['window_height'] = 0.1
                param_info['window_top'] = 2.3

            else:
                param_info['window_height'] = window_info['height']
                param_info['window_top'] = 2.0
                if param_info['window_height'] < 0.1:
                    param_info['window_height'] = 0.1

        if window_info['baywindow']:
            win_type = 'BayWindow'
        else:
            if window_length > 2.5 or ('Balcony' in [window_info['to_type'], self.room_type] and window_length > 1.12) \
                    or param_info['window_height'] < 0.2001:
                win_type = 'FrenchWindow'
            else:
                win_type = 'Window'
        window_info['type'] = win_type
        for line_idx in range(len(line_pts_list) // 2 - 1, -1, -1):
            wall_start = line_pts_list[2 * line_idx]
            wall_end = line_pts_list[2 * line_idx + 1]

            in_line, pt = check_pt_in_line(pts[0], [wall_start, wall_end])
            window_info['wall_pts'][0] = copy.deepcopy(pt)
            if in_line:
                # 按墙线顺序添加开放空间
                in_line, pt = check_pt_in_line(pts[1], [pts[0], wall_end])
                window_info['wall_pts'][1] = copy.deepcopy(pt)
                if in_line:
                    line_pts_list.insert(2 * line_idx + 1, pts[0])
                    line_pts_list.insert(2 * line_idx + 2, pts[1])

                    # 添加窗的信息
                    mesh_info = self.build_door_window_element(mesh_info, window_info, wall_offset_dir, param_info)
                    line_pts_type.insert(2 * line_idx + 1, {'type': 2, 'bottom': param_info['window_height'],
                                                            'top': param_info['window_top']})
                    line_pts_type.insert(2 * line_idx + 2, {'type': 2, 'bottom': param_info['window_height'],
                                                            'top': param_info['window_top']})

                else:
                    in_line, pt = check_pt_in_line(pts[0], [pts[1], wall_end])
                    window_info['wall_pts'][0] = copy.deepcopy(pt)
                    if in_line:
                        line_pts_list.insert(2 * line_idx + 1, pts[1])
                        line_pts_list.insert(2 * line_idx + 2, pts[0])

                        # 添加窗的信息
                        mesh_info = self.build_door_window_element(mesh_info, window_info, wall_offset_dir, param_info)
                        line_pts_type.insert(2 * line_idx + 1, {'type': 2, 'bottom': param_info['window_height'],
                                                                'top': param_info['window_top']})
                        line_pts_type.insert(2 * line_idx + 2, {'type': 2, 'bottom': param_info['window_height'],
                                                                'top': param_info['window_top']})

                break

        return line_pts_list, line_pts_type, mesh_info

    def build_door_window_element(self, mesh_info, element_info, wall_offset_dir, param_info):
        info = copy.deepcopy(element_info)
        info['normal'] = wall_offset_dir
        info['length'] = get_pt_distance(element_info['wall_pts'][0], element_info['wall_pts'][1])

        if param_info['type'] == 'Door':

            info['height'] = param_info['door_height']
            pos, rot = self.set_pos_and_rot(info['wall_pts'], info['depth'], info['normal'], 0.)
            info['pos'] = pos
            info['rot'] = rot
            mesh_info['Door'].append(info)
        elif param_info['type'] == 'Window':
            info['bottom'] = param_info['window_height']
            info['top'] = param_info['window_top']
            pos, rot = self.set_pos_and_rot(info['wall_pts'], info['depth'], info['normal'], info['bottom'], win=True)
            info['pos'] = pos
            info['rot'] = rot
            mesh_info['Window'].append(info)
        return mesh_info

    def set_pos_and_rot(self, pts, depth, normal, height, win=False):
        mid_p = [0.5 * (pts[0][0] + pts[1][0]), height,
                 0.5 * (pts[0][1] + pts[1][1])]
        pos = [mid_p[0] - depth * 0.5 * normal[0], height, mid_p[2] - depth * 0.5 * normal[1]]
        if win:
            true_normal = - np.array(normal)
        else:
            true_normal = np.array(normal)
        ang = np.arcsin(-true_normal[1])
        if true_normal[0] < -0.001:
            ang = np.pi - ang
        ang += np.pi / 2
        rotation = [0.0, np.sin(ang/2.), 0.0, np.cos(ang/2.)]
        return pos, rotation