import os
import numpy as np
import copy
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
from LayoutDecoration.mesh.recon_mesh import Mesh
from LayoutDecoration.Base.recon_params import ROOM_BUILD_TYPE


class Edge:
    def __init__(self, start=None, end=None, norm=None, wall_ind=None):
        self.start = np.array(start) if start is not None else None
        self.end = np.array(end) if end is not None else None
        self.norm = np.array(norm) if norm is not None else None
        self.wall_ind = wall_ind

    def len(self):
        if self.start is None or self.end is None:
            return 0.
        else:
            return np.linalg.norm(self.start - self.end)

    def build_edge_center_length(self, center, length, norm, wall_ind):
        self.start = np.array(center) + length / 2. * (1. - np.abs(np.array(norm)))
        self.end = np.array(center) - length / 2. * (1. - np.abs(np.array(norm)))
        self.norm = norm
        self.wall_ind = wall_ind


class Region:
    def __init__(self, edges=None, points=None, region_width=0.):
        self.edges = edges
        self.points = points
        self.length = 0.
        for edge in edges:
            self.length += edge.len()
        self.length -= (len(edges) - 1) * region_width


class Kitchen:
    def __init__(self, room_info, house_id, debug_mode=False):
        if ROOM_BUILD_TYPE[room_info['type']] == 'Kitchen':

            self.pass_length = 0.8
            self.floor_cabinet_depth = 0.6
            self.wall_cabinet_depth = 0.3
            self.unit_std_length = 0.45
            self.wall_cabinet_std_length = 0.7

            # sync with LayoutDecoration/Base/recon_wallinner.py: add_window_to_line()
            self.floor_cabinet_height = 0.9  # sync with build_window
            self.wall_cabinet_height = self.floor_cabinet_height + 0.8  # sync with build_window
            self.wall_cabinet_h_length = 0.7  # sync with build_window
            self.valid_height = 2.4  # 2.2m

            self.min_length_pair = [0.6, 0.6, 0.5]  # 单水槽， 备餐区， 单灶台
            self.high_degree_length_inc = 0.3
            # self.mid_length_pair = [0.9, 0.8, 0.9]  # 双水槽， 备餐区， 双灶台
            self.extra_area_length = 0.45
            self.refrigerator_length = 0.7

            self.sink = Edge()
            self.preparation = []
            self.cooktop = Edge()
            self.cook_extra = Edge()
            self.sink_extra = Edge()
            self.fridge = Edge()
            self.extra = []
            self.floor_cabinets = []
            self.wall_cabinets = []

            self.all_doors = []
            self.all_wins = []

            self.floor_pts, self.wall_dict, self.valid_edge_dict = self.refine_floor_pts(room_info['floor_pts'])
            self.org_floor_pts = copy.deepcopy(room_info['floor_pts'])

            for door in room_info['Door']:
                k = door['related']['Wall']
                self.all_doors.append(
                    {
                        'wall_ind': self.wall_dict[k]['wall'],
                        'door_pts': door['layout_pts'],
                        'face_offset': np.array(door['normal']) / np.linalg.norm(door['normal']),
                        'door_to': door['target_room_id']
                    }
                )
            for win in room_info['Window']:
                k = win['related']['Wall']
                self.all_wins.append(
                    {
                        'wall_ind': self.wall_dict[k]['wall'],
                        'win_pts': win['layout_pts'],
                        'face_offset': np.array(win['normal']) / np.linalg.norm(win['normal']),
                        'height': win['height']
                    }
                )
            self.wall_face_offset = []
            self.org_wall_face_offset = []
            for wall in room_info['Wall']:
                self.org_wall_face_offset.append(wall['normal'])
                if not self.wall_dict[wall['name']]['pseudo']:
                    self.wall_face_offset.append(
                        np.array(wall['normal'])
                    )

            self.layout_estimate()
            if debug_mode:
                self.draw_layout(house_id)

    def config_kitchen(self, room_info, hard_type):
        if ROOM_BUILD_TYPE[room_info['type']] != 'Kitchen':
            return
        kitchen_hard_type = hard_type['kitchen']
        kitchen_info = []
        floor_cabinet_mat = kitchen_hard_type['cabinet']['floor']
        wall_cabinet_mat = kitchen_hard_type['cabinet']['wall']

        def get_rot(norm):
            ang = np.sum((norm - np.abs(norm)) * np.array([np.pi / 2., 0.]) + norm * np.array([0, -np.pi / 2.])) + np.pi / 2.
            rot = [0.0, np.sin(ang / 2.), 0.0, np.cos(ang / 2.)]
            return rot

        if self.sink.start is not None:
            sink_mat = kitchen_hard_type['cabinet']['sink']
            pos = (self.sink.start + self.sink.end) * 0.5 + self.sink.norm * self.floor_cabinet_depth * 0.5
            pos = [pos[0], 0., pos[1]]
            scale = [self.sink.len() / sink_mat['size'][0] * 100.,
                     self.floor_cabinet_height / sink_mat['size'][2] * 100.,
                     self.floor_cabinet_depth / sink_mat['size'][1] * 100.]
            jid = sink_mat['jid']
            rot = get_rot(self.sink.norm)
            kitchen_info.append({
                'jid': jid,
                'pos': pos,
                'scale': scale,
                'rot': rot,
                'type': 'sink',
                'size': [sink_mat['size'][0], sink_mat['size'][2], sink_mat['size'][1]]
            })
        range_hood_center_edge = Edge()

        # cook
        if self.cooktop.start is not None:
            cook_mat = [i for i in kitchen_hard_type['cook'] if 0.5 < i['size'][0] / 100. / self.cooktop.len() < 1.1]
            if len(cook_mat) == 0:
                cook_mat = sorted(kitchen_hard_type['cook'],
                                  key=lambda x: abs(x['size'][0] / 100. / self.cooktop.len() - 1.))
                cook_mat = [cook_mat[0]]
            cook_mat = np.random.choice(cook_mat)
            height_bias = 0.
            if 'height_bias' in cook_mat:
                height_bias = cook_mat['height_bias']
            pos = (self.cooktop.start + self.cooktop.end) * 0.5 + self.cooktop.norm * self.floor_cabinet_depth * 0.5
            cook_pos = [pos[0], self.floor_cabinet_height - height_bias / 100., pos[1]]
            cook_scale = [1., 1., 1.]
            cook_jid = cook_mat['jid']
            rot = get_rot(self.cooktop.norm)
            kitchen_info.append({
                'jid': cook_jid,
                'pos': cook_pos,
                'scale': cook_scale,
                'rot': rot,
                'type': 'cook',
                'size': [cook_mat['size'][0], cook_mat['size'][2], cook_mat['size'][1]]
            })

            range_hood_mat = [i for i in kitchen_hard_type['range hood'] if 0.7 < i['size'][0] / 100. / self.cooktop.len() < 1.6]
            if len(range_hood_mat) == 0:
                range_hood_mat = sorted(kitchen_hard_type['range hood'],
                                  key=lambda x: abs(x['size'][0] / 100. / self.cooktop.len() - 1.))
                range_hood_mat = [range_hood_mat[0]]
            range_hood_mat = np.random.choice(range_hood_mat)
            range_hood_scale = [1., 0.8, 1.]
            pos = (self.cooktop.start + self.cooktop.end) * 0.5 + self.cooktop.norm * range_hood_mat['size'][1] / 100. * 0.5 * range_hood_scale[1]
            range_hood_height_bias = range_hood_mat['height_bias']
            range_hood_pos = [pos[0], self.wall_cabinet_height - range_hood_height_bias / 100., pos[1]]
            range_hood_jid = range_hood_mat['jid']
            rot = get_rot(self.cooktop.norm)
            kitchen_info.append({
                'jid': range_hood_jid,
                'pos': range_hood_pos,
                'scale': range_hood_scale,
                'rot': rot,
                'type': 'range hood',
                'size': [range_hood_mat['size'][0], range_hood_mat['size'][2], range_hood_mat['size'][1]]
            })

            # range_hood_center_edge.buid_edge_center_length((self.cooktop.start + self.cooktop.end) * 0.5,
            #                                         range_hood_mat['size'][0] / 100.,
            #                                         self.cooktop.norm,
            #                                         self.cooktop.wall_ind)
            range_hood_center_edge.start = (self.cooktop.end + self.cooktop.start) * 0.5 + (-self.cooktop.end + self.cooktop.start) / self.cooktop.len() * range_hood_mat['size'][0] / 100. / 2.
            range_hood_center_edge.end = (self.cooktop.end + self.cooktop.start) * 0.5 + (-self.cooktop.start + self.cooktop.end) / self.cooktop.len() * range_hood_mat['size'][0] / 100. / 2.
            range_hood_center_edge.norm = self.cooktop.norm
            range_hood_center_edge.wall_ind = self.cooktop.wall_ind
        else:
            cook_mat = {}

        if self.fridge.start is not None:
            fridge_mat = np.random.choice(kitchen_hard_type['fridge'])
            floor_jid = fridge_mat['jid']
            if fridge_mat['size'][0] / 100. > self.fridge.len():
                scale = [self.fridge.len() / fridge_mat['size'][0] * 100., self.fridge.len() / fridge_mat['size'][0] * 100., 1]
            else:
                scale = [1., 1., 1.]
            pos = (self.fridge.start + self.fridge.end) * 0.5 + self.fridge.norm * scale[1] * fridge_mat['size'][1] / 100. * 0.5
            pos = [pos[0], 0, pos[1]]

            rot = get_rot(self.fridge.norm)
            kitchen_info.append({
                'jid': floor_jid,
                'pos': pos,
                'scale': scale,
                'rot': rot,
                'type': 'fridge',
                'size': [fridge_mat['size'][0], fridge_mat['size'][2], fridge_mat['size'][1]]
            })

        for cabinet in self.floor_cabinets:
            pos = (cabinet.start + cabinet.end) * 0.5 + cabinet.norm * self.floor_cabinet_depth * 0.5
            pos = [pos[0], 0., pos[1]]
            scale = [cabinet.len() / floor_cabinet_mat['size'][0] * 100.,
                     self.floor_cabinet_height / floor_cabinet_mat['size'][2] * 100.,
                     self.floor_cabinet_depth / floor_cabinet_mat['size'][1] * 100.]
            jid = floor_cabinet_mat['jid']
            rot = get_rot(cabinet.norm)
            kitchen_info.append({
                'jid': jid,
                'pos': pos,
                'scale': scale,
                'rot': rot,
                'type': 'floor_cabinet',
                'size': [floor_cabinet_mat['size'][0], floor_cabinet_mat['size'][2], floor_cabinet_mat['size'][1]]
            })
        for cabinet in self.wall_cabinets:
            inter1, _ = self.compute_closest_win_interaction([cabinet.start, cabinet.end], cabinet.wall_ind)
            inter2, _ = self.compute_closest_win_interaction([cabinet.start, cabinet.end], cabinet.wall_ind,
                                                             range_hood_center_edge)
            if inter1 < 1e-3:
                pos = (cabinet.start + cabinet.end) * 0.5 + cabinet.norm * self.wall_cabinet_depth * 0.5
                pos = [pos[0], self.wall_cabinet_height, pos[1]]
                scale = [cabinet.len() / wall_cabinet_mat['size'][0] * 100.,
                         self.wall_cabinet_h_length / wall_cabinet_mat['size'][2] * 100.,
                         self.wall_cabinet_depth / wall_cabinet_mat['size'][1] * 100.]
                jid = wall_cabinet_mat['jid']
                rot = get_rot(cabinet.norm)
                kitchen_info.append({
                    'jid': jid,
                    'pos': pos,
                    'scale': scale,
                    'rot': rot,
                    'type': 'wall_cabinet',
                    'size': [wall_cabinet_mat['size'][0], wall_cabinet_mat['size'][2], wall_cabinet_mat['size'][1]]
                })

        # accessory
        # cooktop: pot
        if self.cooktop.start is not None and self.cooktop.len() > self.min_length_pair[-1] + 0.1:
            pot_mat = np.random.choice(kitchen_hard_type['pot'])
            height_bias = 0.
            if 'height_bias' in cook_mat:
                height_bias = cook_mat['height_bias']
            pos = (self.cooktop.start + self.cooktop.end) * 0.5 + self.cooktop.norm * self.floor_cabinet_depth * 0.46 + \
                  (1. - np.abs(self.cooktop.norm)) * np.random.choice([-1, 1]) * cook_mat['size'][0] / 100. * 0.28
            pot_pos = [pos[0], self.floor_cabinet_height - height_bias / 100. + cook_mat['size'][2] / 100. - 0.005, pos[1]]

            rot = get_rot(-self.cooktop.norm)
            kitchen_info.append({
                'jid': pot_mat['jid'],
                'pos': pot_pos,
                'scale': [1, 1, 1],
                'rot': rot,
                'type': 'pot',
                'size': [pot_mat['size'][0], pot_mat['size'][2], pot_mat['size'][1]]
            })

        # preparation: kitchenware, fruit
        if len(self.preparation) > 0:
            kitchenware_pre = copy.deepcopy(self.preparation[-1])  # cook preparation
            inter, _ = self.compute_closest_win_interaction([kitchenware_pre.start, kitchenware_pre.end], kitchenware_pre.wall_ind)
            kitchenware_candidate = kitchen_hard_type['kitchenware']
            if inter > 0:
                kitchenware_candidate = [i for i in kitchenware_candidate if 'wall' not in i]
            kitchenware_mat = np.random.choice(kitchenware_candidate)
            kitchenware_pre.start = (kitchenware_pre.end + kitchenware_pre.start) * 0.5 + (-kitchenware_pre.end + kitchenware_pre.start) / kitchenware_pre.len() * kitchenware_mat['size'][0] / 2.
            kitchenware_pre.end = (kitchenware_pre.end + kitchenware_pre.start) * 0.5 + (-kitchenware_pre.start + kitchenware_pre.end) / kitchenware_pre.len() * kitchenware_mat['size'][0] / 2.
            # detect range hood
            signed_dis_range_hood = np.sum((range_hood_center_edge.end - kitchenware_pre.start) * (1 - np.abs(kitchenware_pre.norm)))
            signed_dis_preparation_cook = np.sum((kitchenware_pre.end - kitchenware_pre.start) * (1 - np.abs(kitchenware_pre.norm)))
            if signed_dis_range_hood * signed_dis_preparation_cook > 0:
                if kitchenware_mat['size'][0] < abs(-signed_dis_range_hood + signed_dis_preparation_cook):
                    kitchenware_pre.start = range_hood_center_edge.end
                else:
                    if len(self.preparation) > 0:
                        if abs(np.sum(self.preparation[0].end * (1 - np.abs(self.preparation[0].norm))) - np.sum(kitchenware_pre.end * np.abs(kitchenware_pre.norm))) < 1e-2:
                            displacement = (kitchenware_pre.end - kitchenware_pre.start) / kitchenware_pre.len() * (kitchenware_mat['size'][0] - abs(-signed_dis_range_hood + signed_dis_preparation_cook) + 0.1 * kitchenware_mat['size'][0])
                            kitchenware_pre.end += displacement
                            kitchenware_pre.start += displacement
                        else:
                            kitchenware_pre = copy.deepcopy(self.preparation[-1])  # cook preparation
                            kitchenware_pre.start = kitchenware_pre.end
                            kitchenware_pre.end = kitchenware_pre.start + kitchenware_pre.norm * self.floor_cabinet_depth
                            kitchenware_pre.norm = self.preparation[0].norm
                            kitchenware_pre.wall_ind = self.preparation[0].wall_ind
                            inter, _ = self.compute_closest_win_interaction(
                                [kitchenware_pre.start, kitchenware_pre.end], kitchenware_pre.wall_ind)
                            kitchenware_candidate = kitchen_hard_type['kitchenware']
                            if inter > 0:
                                kitchenware_candidate = [i for i in kitchenware_candidate if 'wall' not in i]
                            kitchenware_mat = np.random.choice(kitchenware_candidate)

            # norm_bias = True
            # if 'wall' in kitchenware_mat and kitchenware_mat['wall']:
            #     norm_bias = False
            pos = (kitchenware_pre.start + kitchenware_pre.end) * 0.5 + kitchenware_pre.norm * kitchenware_mat['size'][1] * 0.55
            kitchenware_pos = [pos[0], self.floor_cabinet_height, pos[1]]
            rot = get_rot(kitchenware_pre.norm)
            kitchen_info.append({
                'jid': kitchenware_mat['jid'],
                'pos': kitchenware_pos,
                'scale': [1, 1, 1],
                'rot': rot,
                'type': 'kitchenware',
                'size': [kitchenware_mat['size'][0], kitchenware_mat['size'][2], kitchenware_mat['size'][1]]
            })

            fruit_pre = self.preparation[0]
            fruit_mat = np.random.choice(kitchen_hard_type['fruit'])
            if len(self.preparation) > 1:
                remained_wide = 1.
            else:
                remained_wide = 1 - kitchenware_mat['size'][1] / self.floor_cabinet_depth
            norm_range = (self.floor_cabinet_depth * remained_wide - fruit_mat['size'][1]) / self.floor_cabinet_depth
            if norm_range > 0:
                pos = (fruit_pre.start + fruit_pre.end) * 0.5 + fruit_pre.norm * \
                      self.floor_cabinet_depth * ((np.random.rand() - 0.5) * norm_range + 1. - remained_wide / 2.)

                horiz_range = (fruit_pre.len() - fruit_mat['size'][0])
                pos += (1 - np.abs(fruit_pre.norm)) * (np.random.rand() - 0.5) * horiz_range
                # pos = (fruit_pre.start + fruit_pre.end) * 0.5 + fruit_pre.norm * self.floor_cabinet_depth * 0.7
                fruit_pos = [pos[0], self.floor_cabinet_height, pos[1]]
                rot = get_rot(fruit_pre.norm)
                kitchen_info.append({
                    'jid': fruit_mat['jid'],
                    'pos': fruit_pos,
                    'scale': [1, 1, 1],
                    'rot': rot,
                    'type': 'fruit',
                    'size': [fruit_mat['size'][0], fruit_mat['size'][2], fruit_mat['size'][1]]
                })
        # sink extra: bowl
        if self.sink_extra.start is not None:
            bowl_mat = np.random.choice(kitchen_hard_type['sink bowl'])
            rot = get_rot(self.sink_extra.norm)
            scale = 1 if bowl_mat['size'][0] < self.sink_extra.len() else self.sink_extra.len() / bowl_mat['size'][0]
            norm_range = (self.floor_cabinet_depth - bowl_mat['size'][1] * scale) / self.floor_cabinet_depth
            if norm_range > 0:
                pos = (self.sink_extra.start + self.sink_extra.end) * 0.5 + self.sink_extra.norm * \
                      self.floor_cabinet_depth * ((np.random.rand() - 0.5) * norm_range + 0.5)
            else:
                pos = (self.sink_extra.start + self.sink_extra.end) * 0.5 + self.sink_extra.norm * \
                       scale * bowl_mat['size'][1] / 2.
            horiz_range = (self.sink_extra.len() - bowl_mat['size'][0] * scale)
            pos += (1 - np.abs(self.sink_extra.norm)) * (np.random.rand() - 0.5) * horiz_range
            bowl_pos = [pos[0], self.floor_cabinet_height, pos[1]]
            kitchen_info.append({
                'jid': bowl_mat['jid'],
                'pos': bowl_pos,
                'scale': [scale, scale, scale],
                'rot': rot,
                'type': 'bowl',
                'size': [bowl_mat['size'][0], bowl_mat['size'][2], bowl_mat['size'][1]]
            })

        # cook extra: others
        if self.cook_extra.start is not None:
            try_time = 0
            while True:
                others_mat = np.random.choice(kitchen_hard_type['others'])
                try_time += 1
                if others_mat['size'][0] <= self.cook_extra.len() * 1.1:
                    break
                if try_time > 2 * len(kitchen_hard_type['others']):
                    others_mat = None
                    break
            if others_mat is not None:
                scale = 1 if others_mat['size'][0] < self.cook_extra.len() else self.cook_extra.len() / others_mat['size'][0]
                norm_range = (self.floor_cabinet_depth - others_mat['size'][1] * scale) / self.floor_cabinet_depth
                if norm_range > 0:
                    pos = (self.cook_extra.start + self.cook_extra.end) * 0.5 + self.cook_extra.norm * \
                           self.floor_cabinet_depth * ((np.random.rand() - 0.5) * norm_range + 0.5)
                else:
                    pos = (self.cook_extra.start + self.cook_extra.end) * 0.5 + self.cook_extra.norm * \
                          scale * others_mat['size'][1] / 2.
                horiz_range = (self.cook_extra.len() - others_mat['size'][0] * scale)
                pos += (1 - np.abs(self.cook_extra.norm)) * (np.random.rand() - 0.5) * horiz_range
                others_pos = [pos[0], self.floor_cabinet_height, pos[1]]
                rot = get_rot(self.cook_extra.norm)

                kitchen_info.append({
                    'jid': others_mat['jid'],
                    'pos': others_pos,
                    'scale': [scale, scale, scale],
                    'rot': rot,
                    'type': 'others',
                    'size': [others_mat['size'][0], others_mat['size'][2], others_mat['size'][1]]
                })
        # extra: appliances
        appliance_mats = np.random.choice(kitchen_hard_type['appliances'], len(self.extra))
        for i, extra in enumerate(self.extra):
            appliance_mat = appliance_mats[i]
            scale = 1 if appliance_mat['size'][0] < extra.len() else extra.len() / appliance_mat['size'][0]
            scale = scale if appliance_mat['size'][1] * scale < self.floor_cabinet_depth else self.floor_cabinet_depth / appliance_mat['size'][1]
            norm_range = (self.floor_cabinet_depth - appliance_mat['size'][1] * scale) / self.floor_cabinet_depth
            if norm_range > 0:
                pos = (extra.start + extra.end) * 0.5 + extra.norm * \
                      self.floor_cabinet_depth * ((np.random.rand() - 0.5) * norm_range + 0.5)
            else:
                pos = (extra.start + extra.end) * 0.5 + extra.norm * scale * appliance_mat['size'][1] / 2.
            horiz_range = (extra.len() - appliance_mat['size'][0] * scale)
            pos += (1 - np.abs(extra.norm)) * (np.random.rand() - 0.5) * horiz_range

            appliance_pos = [pos[0], self.floor_cabinet_height, pos[1]]
            rot = get_rot(extra.norm)

            kitchen_info.append({
                'jid': appliance_mat['jid'],
                'pos': appliance_pos,
                'scale': [scale, scale, scale],
                'rot': rot,
                'type': 'appliance',
                'size': [appliance_mat['size'][0], appliance_mat['size'][2], appliance_mat['size'][1]]
            })

        # kitchen ceiling
        poly = [[self.floor_pts[pt][0], self.valid_height, self.floor_pts[pt][1]] for pt in range(len(self.floor_pts))]

        gap_mesh_mat = hard_type['kitchen']['gusset ceiling gap']
        ceiling_mesh = Mesh("Ceiling", '%s_ceiling' % room_info['id'])
        ceiling_mesh.build_mesh(poly, [0, -1, 0])
        ceiling_mesh.mat['jid'] = gap_mesh_mat['jid']
        ceiling_mesh.mat['texture'] = gap_mesh_mat['texture']
        ceiling_mesh.mat['color'] = gap_mesh_mat['color']
        ceiling_mesh.build_uv(gap_mesh_mat['uv_ratio'])

        room_info['Mesh'].append({
                    'name': ceiling_mesh.uid,
                    'type': ceiling_mesh.mesh_type,
                    'uv': ceiling_mesh.uv,
                    'uid': ceiling_mesh.uid,
                    'xyz': ceiling_mesh.xyz,
                    'normals': ceiling_mesh.normals,
                    'faces': ceiling_mesh.faces,
                    'u_dir': ceiling_mesh.u_dir,
                    'uv_norm_pt': ceiling_mesh.uv_norm_pt,
                    'layout_pts': ceiling_mesh.contour,
                    'material': ceiling_mesh.mat,
                    'related': {}
                })
        polygon = Polygon(self.floor_pts)
        floor_center = [polygon.centroid.x, polygon.centroid.y]
        min_dis = 1e10
        min_centroid = None
        mesh_mat = np.random.choice(hard_type['kitchen']['gusset ceiling'])
        ceramic_meshes, area, centroid = ceiling_mesh.ceramic_layout(mesh_mat, gap_width=0.001)

        for m in ceramic_meshes:
            xyz = np.mean(np.reshape(m.xyz, [-1, 3]), axis=0)
            if np.linalg.norm(xyz[[0, 2]] - floor_center) < min_dis:
                min_centroid = xyz
                min_dis = np.linalg.norm(xyz[[0, 2]] - floor_center)
            room_info['Mesh'].append({
                'name': m.uid,
                'type': m.mesh_type,
                'uv': m.uv,
                'uid': m.uid,
                'xyz': m.xyz,
                'normals': m.normals,
                'faces': m.faces,
                'u_dir': m.u_dir,
                'uv_norm_pt': m.uv_norm_pt,
                'layout_pts': m.contour,
                'material': m.mat,
                'related': {
                    'Mesh': ceiling_mesh.uid
                }
            })

        light = np.random.choice(hard_type['kitchen']['light'])
        min_centroid[1] -= light['size'][2] / 100.
        room_size = np.max(self.floor_pts, axis=0) - np.min(self.floor_pts, axis=0)
        if (room_size[0] > room_size[1] and light['size'][0] > light['size'][1]) or \
                (room_size[0] < room_size[1] and light['size'][0] < light['size'][1]):
            rot = [0, 0, 0, 1]
        else:
            ang = np.pi / 2.
            rot = [0.0, np.sin(ang/2.), 0.0, np.cos(ang/2.)]
        kitchen_info.append({
            'jid': light['jid'],
            'pos': min_centroid.tolist(),
            'scale': [1, 1, 1],
            'rot': rot,
            'type': 'light',
            'size': [light['size'][0], light['size'][2], light['size'][1]]
        })
        room_info['Kitchen'] = kitchen_info

    def layout_estimate(self):
        try:
            regions = self.get_valid_area()
            regions = self.passable_refine(regions)
            self.layout_area_segmentation(regions)
        except Exception as e:
            print(e)

    def draw_layout(self, house_id):

        plt.figure()
        floor_pts = copy.deepcopy(self.org_floor_pts)
        floor_pts.append(floor_pts[0])
        plt.plot(np.array(floor_pts)[:, 0], np.array(floor_pts)[:, 1])
        floor_poly = Polygon(floor_pts)
        for win in self.all_wins:
            plt.plot(np.array(win['win_pts'])[:, 0], np.array(win['win_pts'])[:, 1], color='blue', linewidth=3)

        for door in self.all_doors:
            plt.plot(np.array(door['door_pts'])[:, 0], np.array(door['door_pts'])[:, 1], color='white', linewidth=3)

        # sink
        if self.sink.start is not None:
            sink_pts = np.array(
                [self.sink.start, self.sink.end, self.sink.end + self.sink.norm * self.floor_cabinet_depth,
                 self.sink.start + self.sink.norm * self.floor_cabinet_depth, self.sink.start])
            plt.plot(sink_pts[:, 0], sink_pts[:, 1], color='black')
            plt.text(np.mean(sink_pts[:, 0]) - 0.1, np.mean(sink_pts[:, 1]), 'sink', color='black')
        if self.sink_extra.start is not None:
            sink_extra_pts = np.array(
                [self.sink_extra.start, self.sink_extra.end,
                 self.sink_extra.end + self.sink_extra.norm * self.floor_cabinet_depth,
                 self.sink_extra.start + self.sink_extra.norm * self.floor_cabinet_depth, self.sink_extra.start])
            poly = Polygon(sink_extra_pts)
            inter = floor_poly.intersection(poly)
            sink_extra_pts = np.asarray(inter.exterior.coords)
            plt.plot(sink_extra_pts[:, 0], sink_extra_pts[:, 1], color='black')

        # cook
        if self.cooktop.start is not None:
            cook_pts = np.array(
                [self.cooktop.start, self.cooktop.end, self.cooktop.end + self.cooktop.norm * self.floor_cabinet_depth,
                 self.cooktop.start + self.cooktop.norm * self.floor_cabinet_depth, self.cooktop.start])
            plt.plot(cook_pts[:, 0], cook_pts[:, 1], color='red')
            plt.text(np.mean(cook_pts[:, 0]) - 0.1, np.mean(cook_pts[:, 1]), 'cook', color='red')
        if self.cook_extra.start is not None:
            cook_extra = self.cook_extra
            cook_extra_pts = np.array(
                [cook_extra.start, cook_extra.end, cook_extra.end + cook_extra.norm * self.floor_cabinet_depth,
                 cook_extra.start + cook_extra.norm * self.floor_cabinet_depth, cook_extra.start])
            poly = Polygon(cook_extra_pts)
            inter = floor_poly.intersection(poly)
            cook_extra_pts = np.asarray(inter.exterior.coords)
            plt.plot(cook_extra_pts[:, 0], cook_extra_pts[:, 1], color='red')

        if self.fridge.start is not None:
            refrigerator_pts = np.array(
                [self.fridge.start, self.fridge.end, self.fridge.end + self.fridge.norm * self.floor_cabinet_depth,
                 self.fridge.start + self.fridge.norm * self.floor_cabinet_depth, self.fridge.start])
            plt.plot(refrigerator_pts[:, 0], refrigerator_pts[:, 1], color='skyblue')
            plt.text(np.mean(refrigerator_pts[:, 0]) - 0.1, np.mean(refrigerator_pts[:, 1]), 'fridge', color='skyblue')

        for preparation in self.preparation:
            if preparation.start is not None:
                preparation_pts = np.array(
                    [preparation.start, preparation.end, preparation.end + preparation.norm * self.floor_cabinet_depth,
                     preparation.start + preparation.norm * self.floor_cabinet_depth, preparation.start])
                poly = Polygon(preparation_pts)
                inter = floor_poly.intersection(poly)
                preparation_pts = np.asarray(inter.exterior.coords)
                plt.plot(preparation_pts[:, 0], preparation_pts[:, 1], color='green')
        for extra in self.extra:
            if extra.start is not None:
                extra_pts = np.array(
                    [extra.start, extra.end, extra.end + extra.norm * self.floor_cabinet_depth,
                     extra.start + extra.norm * self.floor_cabinet_depth, extra.start])
                plt.plot(extra_pts[:, 0], extra_pts[:, 1], color='green')

        for cabinet in self.floor_cabinets:
            cabinet_pts = np.array(
                [cabinet.start, cabinet.end, cabinet.end + cabinet.norm * self.floor_cabinet_depth,
                 cabinet.start + cabinet.norm * self.floor_cabinet_depth, cabinet.start])
            poly = Polygon(cabinet_pts)
            inter = floor_poly.intersection(poly)
            cabinet_pts = np.asarray(inter.exterior.coords)
            if len(cabinet_pts) > 0:
                plt.plot(cabinet_pts[:, 0], cabinet_pts[:, 1], color='c', linestyle='--')
        plt.axis('equal')
        # plt.show()
        save_path = os.path.join(os.path.dirname(__file__), '../temp/%s/kitchen.png' % house_id)
        plt.savefig(save_path)

        plt.figure()
        floor_pts = copy.deepcopy(self.org_floor_pts)
        floor_pts.append(floor_pts[0])
        plt.plot(np.array(floor_pts)[:, 0], np.array(floor_pts)[:, 1])
        plt.axis('equal')
        save_path = os.path.join(os.path.dirname(__file__), '../temp/%s/kitchen_org_contour.png' % house_id)
        plt.savefig(save_path)

    def get_valid_area(self):

        edges = []
        door_edges = []
        for i in range(len(self.floor_pts)):
            edges.append(
                Edge(self.floor_pts[i], self.floor_pts[(i + 1) % len(self.floor_pts)],
                     self.wall_face_offset[i] / np.linalg.norm(self.wall_face_offset[i]), i))
        for door in self.all_doors:
            door_pts = np.array([door['door_pts'][0], door['door_pts'][1]])
            direct = door_pts - np.mean(door_pts, axis=0)
            door_pts = door_pts + direct / np.linalg.norm(direct, axis=1) * 0.01
            door_edges.append(Edge(door_pts[0], door_pts[1], door['face_offset'], door['wall_ind']))
            door_edges.append(Edge(door_pts[0], door_pts[0] + np.array(door['face_offset']) * self.pass_length, door['face_offset'][::-1], -1))
            door_edges.append(Edge(door_pts[1], door_pts[1] + np.array(door['face_offset']) * self.pass_length, door['face_offset'][::-1], -1))
            door_edges.append(Edge(door_pts[0] + np.array(door['face_offset']) * self.pass_length,
                                   door_pts[1] + np.array(door['face_offset']) * self.pass_length,
                                   door['face_offset'],
                                   -1))

        horizon_edges = []
        vertical_edges = []
        horizon_door_edges = []
        vertical_door_edges = []
        for i in range(len(edges)):
            if abs(edges[i].norm[0]) > abs(edges[i].norm[1]):
                vertical_edges.append(copy.deepcopy(edges[i]))
            else:
                horizon_edges.append(copy.deepcopy(edges[i]))
        for i in range(len(door_edges)):
            if abs(door_edges[i].norm[0]) > abs(door_edges[i].norm[1]):
                vertical_door_edges.append(copy.deepcopy(door_edges[i]))
            else:
                horizon_door_edges.append(copy.deepcopy(door_edges[i]))

        # rm edge part that is blocked by doors
        valid_edges_vertical = self.get_valid_edges(vertical_edges, vertical_door_edges, self.floor_cabinet_depth,
                                                    flag='vertical', door_target=True)
        valid_edges_vertical = self.get_valid_edges(valid_edges_vertical, vertical_edges, self.floor_cabinet_depth * 2,
                                                    flag='vertical', door_target=False)

        valid_edges_horizontal = self.get_valid_edges(horizon_edges, horizon_door_edges, self.floor_cabinet_depth,
                                                      flag='horizontal', door_target=True)
        valid_edges_horizontal = self.get_valid_edges(valid_edges_horizontal, horizon_edges,
                                                      self.floor_cabinet_depth * 2, flag='horizontal', door_target=False)

        regions = self.combine_isolated_valid_wall(valid_edges_vertical + valid_edges_horizontal)
        return regions

    def passable_refine(self, regions):
        # region 内
        refined_regions = []
        for region in regions:
            edges_flag = [True for _ in region.edges]
            start_ind = 0
            end_ind = len(region.edges) - 1
            for i in range(len(region.edges)):
                if not edges_flag[i]:
                    continue
                cur_edge = region.edges[i]
                for j in range(i + 1, len(region.edges)):
                    if i == j or not edges_flag[j] or not edges_flag[i]:
                        continue
                    tar_edge = region.edges[j]
                    if np.argmax(np.abs(cur_edge.norm)) != np.argmax(np.abs(tar_edge.norm)):
                        continue

                    ind = np.argmax(np.abs(cur_edge.norm))
                    dis = abs(tar_edge.start[ind] + tar_edge.norm[ind] * self.floor_cabinet_depth -
                              (cur_edge.start[ind] + cur_edge.norm[ind] * self.floor_cabinet_depth)
                              )
                    min_1 = min(cur_edge.start[1-ind], cur_edge.end[1-ind])
                    max_1 = max(cur_edge.start[1-ind], cur_edge.end[1-ind])
                    min_2 = min(tar_edge.start[1-ind], tar_edge.end[1-ind])
                    max_2 = max(tar_edge.start[1-ind], tar_edge.end[1-ind])
                    if max_1 <= min_2 or min_1 >= max_2:
                        continue

                    if dis < self.pass_length:
                        max_len_wall_ind = -1
                        max_len = -1
                        for w_i in range(len(region.edges)):
                            if region.edges[w_i].len() > max_len:
                                max_len = region.edges[w_i].len()
                                max_len_wall_ind = w_i
                        if i == max_len_wall_ind and region.edges[i].wall_ind not in [door['wall_ind'] for door in self.all_doors]:
                            edges_flag[j] = False
                        elif j == max_len_wall_ind and region.edges[j].wall_ind not in [door['wall_ind'] for door in self.all_doors]:
                            edges_flag[i] = False
                        elif i in [start_ind, end_ind] and j not in [start_ind, end_ind]:
                            edges_flag[i] = False
                            if i == start_ind:
                                start_ind += 1
                            else:
                                end_ind -= 1
                        elif i not in [start_ind, end_ind] and j in [start_ind, end_ind]:
                            edges_flag[j] = False
                            if j == start_ind:
                                start_ind += 1
                            else:
                                end_ind -= 1
                        else:
                            if 1e-3 < tar_edge.len() - cur_edge.len():
                                edges_flag[i] = False
                                if i == start_ind:
                                    start_ind += 1
                                else:
                                    end_ind -= 1
                            elif 1e-3 < cur_edge.len() - tar_edge.len():
                                edges_flag[j] = False
                                if j == start_ind:
                                    start_ind += 1
                                else:
                                    end_ind -= 1
                            else:
                                if j - i == 2 and region.edges[i+1].wall_ind in [win['wall_ind'] for win in self.all_wins]:
                                    flag = True
                                    for win in self.all_wins:
                                        if win['wall_ind'] == region.edges[i+1].wall_ind:
                                            pos = np.mean(win['win_pts'], axis=0)
                                            if np.linalg.norm(pos - region.edges[i+1].start) > np.linalg.norm(pos - region.edges[i+1].end):
                                                keep_edge_p = region.edges[i+1].start
                                            else:
                                                keep_edge_p = region.edges[i + 1].end
                                            i_edge_dis = min(np.linalg.norm(keep_edge_p - cur_edge.start), np.linalg.norm(keep_edge_p - cur_edge.end))
                                            j_edge_dis = min(np.linalg.norm(keep_edge_p - tar_edge.start), np.linalg.norm(keep_edge_p - tar_edge.end))
                                            if i_edge_dis < j_edge_dis:
                                                edges_flag[j] = False
                                                if j == start_ind:
                                                    start_ind += 1
                                                else:
                                                    end_ind -= 1
                                            else:
                                                edges_flag[i] = False
                                                if i == start_ind:
                                                    start_ind += 1
                                                else:
                                                    end_ind -= 1
                                            flag = False
                                            break
                                    if flag:
                                        n = np.random.choice([i, j])
                                        if n == start_ind:
                                            start_ind += 1
                                        else:
                                            end_ind -= 1
                                        edges_flag[n] = False
                                else:
                                    n = np.random.choice([i, j])
                                    if n == start_ind:
                                        start_ind += 1
                                    else:
                                        end_ind -= 1
                                    edges_flag[n] = False

            remained_edges = [region.edges[i] for i in range(len(region.edges)) if edges_flag[i]]
            remained_regions = self.combine_isolated_valid_wall(remained_edges, filter=False)
            refined_regions += remained_regions
        return refined_regions

    @staticmethod
    def get_valid_edges(edges, target_edges, depth_thresh, flag='vertical', door_target=False):
        assert flag in ['vertical', 'horizontal']
        cp_edges = []
        cp_target_edges = []
        if flag == 'horizontal':
            for edge in edges:
                cp_edges.append(Edge(edge.start[::-1], edge.end[::-1], edge.norm[::-1], edge.wall_ind))
            for edge in target_edges:
                cp_target_edges.append(Edge(edge.start[::-1], edge.end[::-1], edge.norm[::-1], edge.wall_ind))
        else:
            cp_edges = copy.deepcopy(edges)
            cp_target_edges = copy.deepcopy(target_edges)
        all_valid_edges = []
        for i in range(len(cp_edges)):
            edge_parts = [cp_edges[i]]

            for door_edge in cp_target_edges:
                cur_door_pt = door_edge.start
                last_door_pt = door_edge.end
                door_x = cur_door_pt[0]
                start_y_door = min(cur_door_pt[1], last_door_pt[1])
                end_y_door = max(cur_door_pt[1], last_door_pt[1])

                remained_edges = []
                for edge in edge_parts:
                    cur = edge.start
                    last = edge.end
                    face_offset = edge.norm
                    wall_ind = edge.wall_ind

                    start_y = min(cur[1], last[1])
                    end_y = max(cur[1], last[1])
                    wall_x = cur[0]
                    if (door_x - wall_x) * np.sign(face_offset[0]) > depth_thresh or (abs(wall_x - door_x) < 1e-3 and not door_target):
                        remained_edges.append(Edge([wall_x, start_y], [wall_x, end_y], face_offset, wall_ind))
                        continue

                    if start_y_door - end_y > -1e-3 or end_y_door - start_y < 1e-3:
                        remained_edges.append(Edge([wall_x, start_y], [wall_x, end_y], face_offset, wall_ind))
                        continue
                    elif start_y_door - start_y < 1e-3 and end_y_door - end_y < 1e-3:
                        remained_edges.append(Edge([wall_x, end_y_door], [wall_x, end_y], face_offset, wall_ind))
                    elif start_y_door - start_y > -1e-3:
                        remained_edges.append(Edge([wall_x, start_y], [wall_x, start_y_door], face_offset, wall_ind))
                        if end_y_door - end_y < 1e-3:
                            remained_edges.append(Edge([wall_x, end_y_door], [wall_x, end_y], face_offset, wall_ind))
                    else:
                        continue

                edge_parts = copy.deepcopy(remained_edges)
            all_valid_edges += sorted(edge_parts, key=lambda x: x.start[1])
        if flag == 'horizontal':
            for i in range(len(all_valid_edges)):
                all_valid_edges[i] = Edge(all_valid_edges[i].start[::-1],
                                          all_valid_edges[i].end[::-1],
                                          all_valid_edges[i].norm[::-1],
                                          all_valid_edges[i].wall_ind)
        return all_valid_edges

    def combine_isolated_valid_wall(self, edges, filter=True):
        # 输出region中的多条edge,按照index顺序首尾相连即：last.start->last.end = cur.start->cur.end = next.start->next.end
        regions = []
        edge_flag = [True for _ in range(len(edges))]
        for i in range(len(edges)):
            if edge_flag[i]:
                start = edges[i].start
                end = edges[i].end
                region_edges = [edges[i]]

                region_points = [start, end]
                edge_flag[i] = False
                while True:
                    find_valid = False
                    for j in range(len(edges)):
                        if edge_flag[j]:
                            next = edges[j]
                            if abs(next.start[0] - end[0]) < 1e-5 and abs(next.start[1] - end[1]) < 1e-5:
                                end = next.end
                                edge_flag[j] = False
                                region_edges.append(Edge(next.start, next.end, next.norm, next.wall_ind))
                                region_points.append(end)
                                find_valid = True
                                break
                            elif abs(next.end[0] - end[0]) < 1e-5 and abs(next.end[1] - end[1]) < 1e-5:
                                end = next.start
                                edge_flag[j] = False
                                region_edges.append(Edge(next.end, next.start, next.norm, next.wall_ind))
                                region_points.append(end)
                                find_valid = True
                                break
                    if not find_valid:
                        break

                while True:
                    find_valid = False
                    for j in range(len(edges)):
                        if edge_flag[j]:
                            next = edges[j]
                            if abs(next.start[0] - start[0]) < 1e-5 and abs(next.start[1] - start[1]) < 1e-5:
                                start = next.end
                                edge_flag[j] = False
                                region_edges.insert(0, Edge(next.end, next.start, next.norm, next.wall_ind))
                                region_points.insert(0, start)
                                find_valid = True
                                break
                            elif abs(next.end[0] - start[0]) < 1e-5 and abs(next.end[1] - start[1]) < 1e-5:
                                start = next.start
                                edge_flag[j] = False
                                region_edges.insert(0, Edge(next.start, next.end, next.norm, next.wall_ind))
                                region_points.insert(0, start)
                                find_valid = True
                                break
                    if not find_valid:
                        break

                # 过滤掉边缘过短的边
                if filter:
                    res_regions = []
                    while len(region_edges) > 0:
                        remained_edge_length = 0.
                        for e in region_edges[:-1]:
                            remained_edge_length += e.len()
                        if region_edges[-1].len() < self.floor_cabinet_depth + self.unit_std_length:
                            region_edges.pop()
                            region_points.pop()
                        elif len(region_edges) > 1 and \
                             region_edges[-1].len() < self.floor_cabinet_depth + self.unit_std_length * 2 and \
                             remained_edge_length > self.refrigerator_length + self.unit_std_length * 2 + \
                                np.sum(self.min_length_pair) + self.high_degree_length_inc * 3 + \
                                (len(region_edges) - 1) * self.floor_cabinet_depth and \
                                region_edges[-1].wall_ind not in [win['wall_ind'] for win in self.all_wins]:
                            region_edges.pop()
                            region_points.pop()
                        else:
                            break
                    region_edges.reverse()
                    region_points.reverse()
                    while len(region_edges) > 0:
                        remained_edge_length = 0.
                        for e in region_edges[:-1]:
                            remained_edge_length += e.len()
                        if region_edges[-1].len() < self.floor_cabinet_depth + self.unit_std_length:
                            region_edges.pop()
                            region_points.pop()
                        elif len(region_edges) > 1 and \
                             region_edges[-1].len() < self.floor_cabinet_depth + self.unit_std_length * 2 and \
                             remained_edge_length > self.refrigerator_length + self.unit_std_length * 2 + \
                             np.sum(self.min_length_pair) + self.high_degree_length_inc * 3 + \
                             (len(region_edges) - 1) * self.floor_cabinet_depth and \
                             region_edges[-1].wall_ind not in [win['wall_ind'] for win in self.all_wins]:
                            region_edges.pop()
                            region_points.pop()
                        else:
                            break
                    region_edges.reverse()
                    region_points.reverse()
                if len(region_edges) > 0:
                    regions.append(Region(region_edges, points=region_points, region_width=self.floor_cabinet_depth))

        return regions

    def layout_area_segmentation(self, regions):
        room_total_length = 0.
        for region in regions:
            room_total_length += region.length
        regions.sort(key=lambda x: -x.length)

        # TODO 目前只支持一个最大区域布置
        if len(regions) == 0:
            return
        regions = [regions[0]]
        # 如果只有一个区域，
        # 或者最大区域占了0.9以上，
        # 或者第二大区域很小,
        # 或者第一区域已经足够容纳标准的布局长度
        if len(regions) == 1 or \
                regions[0].length >= 0.9 * room_total_length or \
                (len(regions) > 1 and regions[1].length < self.unit_std_length) or \
                regions[0].length > 3. * self.high_degree_length_inc + np.sum(self.min_length_pair):
            assert regions[0].length > 1.5, 'too narrow area for kitchen layout'
            if len(regions[0].edges) == 1:
                self.layout_in_one_edge(regions[0].edges)
            elif len(regions[0].edges) == 2:
                # 水槽和灶台分别在一条边上，水槽优先选择有窗户的边
                self.layout_in_two_edge(regions[0].edges)
            elif len(regions[0].edges) == 3:
                # 水槽和灶台分别在一条边上，水槽优先选择有窗户的边，灶台在相邻边
                self.layout_in_three_edge(regions[0].edges)
            else:
                filtered_edges = copy.deepcopy(regions[0].edges)
                door_wall_inds = [i['wall_ind'] for i in self.all_doors]
                win_wall_inds = [i['wall_ind'] for i in self.all_wins]
                max_len_wall_ind = -1
                max_len = -1
                for edge in filtered_edges:
                    if edge.len() > max_len:
                        max_len = edge.len()
                        max_len_wall_ind = edge.wall_ind
                while len(filtered_edges) > 3:
                    if filtered_edges[0].wall_ind in win_wall_inds and filtered_edges[-1].wall_ind not in win_wall_inds and max_len_wall_ind != filtered_edges[-1].wall_ind:
                        filtered_edges.pop()
                    elif filtered_edges[0].wall_ind not in door_wall_inds and filtered_edges[-1].wall_ind in door_wall_inds and max_len_wall_ind != filtered_edges[0].wall_ind:
                        filtered_edges.pop(0)
                    elif filtered_edges[0].wall_ind in door_wall_inds and filtered_edges[-1].wall_ind not in door_wall_inds:
                        filtered_edges.pop(0)
                    elif filtered_edges[0].wall_ind not in door_wall_inds and filtered_edges[-1].wall_ind in door_wall_inds:
                        filtered_edges.pop()
                    elif filtered_edges[0].len() > filtered_edges[-1].len():
                        filtered_edges.pop()
                    else:
                        filtered_edges.pop(0)
                filtered_edges = self.combine_isolated_valid_wall(filtered_edges)[0].edges
                if len(filtered_edges) == 1:
                    self.layout_in_one_edge(filtered_edges)
                elif len(filtered_edges) == 2:
                    self.layout_in_two_edge(filtered_edges)
                else:
                    self.layout_in_three_edge(filtered_edges)
                # raise Exception('issue to be processed: too many segments in one connected edges group')
        # 第二大区域足够大且与第一大区域加起来占了0.9以上
        elif len(regions) > 1 and regions[0].length + regions[1].length >= 0.9 * room_total_length:
            print('two regions case, to be processed')
            pass
        else:
            # TODO 尚未考虑的特殊情况
            raise Exception("issue to be processed: too many area")

    def compute_closest_win_interaction(self, cupboard_edge, wall_ind, target_edge=None):
        max_interaction = -1.
        max_interaction_win = None
        if target_edge is None:
            t = self.all_wins
        else:
            if target_edge.start is None:
                return max_interaction, max_interaction_win
            t = [{
                'win_pts': [target_edge.start, target_edge.end],
                'wall_ind': target_edge.wall_ind
            }]
        for win in t:
            if win['wall_ind'] == wall_ind:
                win_pts = win['win_pts']
                if abs(win_pts[0][0] - win_pts[1][0]) < abs(win_pts[0][1] - win_pts[1][1]):
                    ind = 1
                else:
                    ind = 0
                cupboard_edge_start = min(cupboard_edge[0][ind], cupboard_edge[1][ind])
                cupboard_edge_end = max(cupboard_edge[0][ind], cupboard_edge[1][ind])
                win_edge_start = min(win_pts[0][ind], win_pts[1][ind])
                win_edge_end = max(win_pts[0][ind], win_pts[1][ind])

                interaction = min(cupboard_edge_end, win_edge_end) - max(cupboard_edge_start, win_edge_start)
                if interaction > 0 and interaction > max_interaction:
                    max_interaction = interaction
                    max_interaction_win = win
        return max_interaction, max_interaction_win

    def find_max_interaction_edge_part_with_win(self, edge, length):
        assert edge.len() > length
        global_max_interaction = 0
        global_closest_win_dis = 1e8
        best_edge = None
        for win in self.all_wins:
            if win['wall_ind'] == edge.wall_ind:
                win_pts = win['win_pts']
                if abs(win_pts[0][0] - win_pts[1][0]) < abs(win_pts[0][1] - win_pts[1][1]):
                    ind = 1
                else:
                    ind = 0
                win_center = 0.5 * (win_pts[0][ind] + win_pts[1][ind])
                edge_start = min(edge.start[ind], edge.end[ind])
                edge_end = max(edge.start[ind], edge.end[ind])
                win_edge_start = min(win_pts[0][ind], win_pts[1][ind])
                win_edge_end = max(win_pts[0][ind], win_pts[1][ind])

                interaction_start = max(edge_start, win_edge_start)
                interaction_end = min(edge_end, win_edge_end)
                interaction = interaction_end - interaction_start
                if interaction < length:
                    max_interaction = interaction
                    if abs(win_edge_end - win_edge_start - interaction) < 1e-3:
                        # too small window
                        target_start = win_center - length * 0.5
                        target_end = win_center + length * 0.5
                    else:
                        if edge_end < win_edge_end:
                            target_end = edge_end
                            target_start = target_end - length
                        elif edge_start > win_edge_start:
                            target_start = edge_start
                            target_end = target_start + length
                        else:  # this else statement will actually not be reached
                            target_start = 0
                            target_end = 0
                else:
                    max_interaction = length
                    best_start = win_center - length * 0.5
                    best_end = win_center + length * 0.5
                    if best_start < interaction_start:
                        target_start = interaction_start
                        target_end = interaction_start + length
                    elif best_end > interaction_end:
                        target_end = interaction_end
                        target_start = interaction_end - length
                    else:
                        target_start = best_start
                        target_end = best_end
                closest_win_dis = abs(target_start + length / 2. - win_center)

                if max_interaction - global_max_interaction > 1e-3 or (abs(max_interaction - global_max_interaction) < 1e-3 and closest_win_dis < global_closest_win_dis):
                    start = copy.deepcopy(edge.start)
                    start[ind] = target_start
                    end = copy.deepcopy(edge.start)
                    end[ind] = target_end
                    best_edge = Edge(start, end, edge.norm, edge.wall_ind)
                else:
                    continue
        if best_edge is None:
            start = (edge.end + edge.start) * 0.5 - 0.5 * length * (edge.end - edge.start) / edge.len()
            end = (edge.end + edge.start) * 0.5 + 0.5 * length * (edge.end - edge.start) / edge.len()
            best_edge = Edge(start, end, edge.norm, edge.wall_ind)
        else:
            if abs(np.sum((best_edge.end - best_edge.start) / best_edge.len() + (edge.end - edge.start) / edge.len())) < 1e-3:
                tmp = best_edge.start
                best_edge.start = best_edge.end
                best_edge.end = tmp
        return best_edge

    def layout_with_predefined_length_in_one_edge(self, edge, sink_len, cooktop_len,
                                                  sink_extra_len, cook_extra_len, refrigerator_len=0.):

        # 水槽取靠近窗户的位置
        wall_ind = edge.wall_ind
        length = np.linalg.norm(edge.end - edge.start)

        p1 = (sink_len + sink_extra_len + refrigerator_len) / length * (
                edge.end - edge.start) + edge.start
        p2 = (sink_len + sink_extra_len + refrigerator_len) / length * (
                -edge.end + edge.start) + edge.end

        inter_1 = self.compute_closest_win_interaction([edge.start, p1], wall_ind)
        inter_2 = self.compute_closest_win_interaction([edge.end, p2], wall_ind)
        edge_sink = [p1, edge.start] if inter_1 >= inter_2 else [p2, edge.end]

        if refrigerator_len > 1e-3:
            mid_p = refrigerator_len * (edge_sink[0] - edge_sink[1]) / np.linalg.norm(edge_sink[0] - edge_sink[1]) + edge_sink[1]
            self.fridge.start = mid_p
            self.fridge.end = edge_sink[1]
            self.fridge.norm = edge.norm
            self.fridge.wall_ind = wall_ind

            edge_sink = [edge_sink[0], mid_p]
        if sink_extra_len > 1e-3:
            mid_p = (np.array(edge_sink[0]) - np.array(edge_sink[1])) * sink_extra_len / np.linalg.norm(edge_sink[0] - edge_sink[1]) + edge_sink[1]
            self.sink_extra.start = mid_p
            self.sink_extra.end = edge_sink[1]
            self.sink_extra.norm = edge.norm
            self.sink_extra.wall_ind = wall_ind

            edge_sink = [edge_sink[0], mid_p]

        self.sink.start = edge_sink[0]
        self.sink.end = edge_sink[1]
        self.sink.norm = edge.norm
        self.sink.wall_ind = wall_ind

        # 灶台不能靠近窗户
        if inter_1 >= inter_2:
            edge_cooktop = [(cooktop_len + cook_extra_len) / length * (
                    -edge.end + edge.start) + edge.end,
                            edge.end]
        else:
            edge_cooktop = [(cooktop_len + cook_extra_len) / length * (
                    edge.end - edge.start) + edge.start,
                            edge.start]

        if cook_extra_len > 1e-3:
            mid_p = (np.array(edge_cooktop[0]) - np.array(edge_cooktop[1])) * cook_extra_len / np.linalg.norm(edge_cooktop[0] - edge_cooktop[1]) + edge_cooktop[1]
            self.cook_extra.start = mid_p
            self.cook_extra.end = edge_cooktop[1]
            self.cook_extra.norm = edge.norm
            self.cook_extra.wall_ind = wall_ind

            edge_cooktop = [edge_cooktop[0], mid_p]
        self.cooktop.start = edge_cooktop[0]
        self.cooktop.end = edge_cooktop[1]
        self.cooktop.norm = edge.norm
        self.cooktop.wall_ind = wall_ind

        # 备餐区
        self.preparation = [Edge(edge_cooktop[0], edge_sink[0], edge.norm, wall_ind)]

        cabinets_length = self.preparation[0].len() + self.cooktop.len() + self.cook_extra.len()
        cabinet_start = edge_cooktop[1] if cook_extra_len < 1e-3 else self.cook_extra.end
        direct = np.array(edge_cooktop[0]) - cabinet_start
        cabinet_end = direct / np.linalg.norm(direct) * cabinets_length + cabinet_start
        cabinet_edge = Edge(cabinet_start, cabinet_end, self.cooktop.norm, self.cooktop.wall_ind)
        self.add_cabinets(cabinet_edge, cabinet_edge)
        # fridge occlude with win
        if self.fridge.start is not None:
            max_interaction, _ = self.compute_closest_win_interaction([self.fridge.start, self.fridge.end], self.fridge.wall_ind)
            if max_interaction > 0:
                self.sink_extra.start = self.fridge.start
                self.fridge = Edge()
        # for extra in self.extra:
        #     self.add_cabinets(extra)
        self.add_cabinets(self.sink_extra, self.sink_extra)

    def layout_in_one_edge(self, edges):
        edge = edges[0]
        if edge.len() <= np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 0.5:  # 只能容纳一个单水槽0.6+单灶0.45+备餐区≈0.6  1.85m
            self.layout_with_predefined_length_in_one_edge(edge,
                                                           sink_len=self.min_length_pair[0],
                                                           cooktop_len=self.min_length_pair[-1],
                                                           sink_extra_len=0,
                                                           cook_extra_len=0)
        elif edge.len() <= np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 1.5:  # 可以将水槽或灶台其中之一由单升级为双  2.15m
            rand = int(np.random.rand() > 0.5)
            sink_len = rand * self.high_degree_length_inc + self.min_length_pair[0]
            cooktop_len = (1 - rand) * self.high_degree_length_inc + self.min_length_pair[-1]
            self.layout_with_predefined_length_in_one_edge(edge,
                                                           sink_len=sink_len,
                                                           cooktop_len=cooktop_len,
                                                           sink_extra_len=0,
                                                           cook_extra_len=0)
        elif edge.len() <= np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 2.5:  # 双水槽+双灶台  2.45m
            self.layout_with_predefined_length_in_one_edge(edge,
                                                           sink_len=self.high_degree_length_inc + self.min_length_pair[
                                                               0],
                                                           cooktop_len=self.high_degree_length_inc +
                                                                       self.min_length_pair[-1],
                                                           sink_extra_len=0,
                                                           cook_extra_len=0)
        elif edge.len() <= np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 2.5 + self.extra_area_length:  # 双水槽+双灶台 + 一个额外区域    2.75m
            rand = int(np.random.rand() > 0.5)
            sink_extra_len = rand * self.extra_area_length
            cook_extra_len = (1 - rand) * self.extra_area_length
            self.layout_with_predefined_length_in_one_edge(edge,
                                                           sink_len=self.high_degree_length_inc + self.min_length_pair[
                                                               0],
                                                           cooktop_len=self.high_degree_length_inc +
                                                                       self.min_length_pair[-1],
                                                           sink_extra_len=sink_extra_len,
                                                           cook_extra_len=cook_extra_len)
        elif edge.len() <= np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 2.5 + 2 * self.extra_area_length:  # 双水槽+双灶台 + 两个额外区域:   3.05m
            self.layout_with_predefined_length_in_one_edge(edge,
                                                           sink_len=self.high_degree_length_inc + self.min_length_pair[
                                                               0],
                                                           cooktop_len=self.high_degree_length_inc +
                                                                       self.min_length_pair[-1],
                                                           sink_extra_len=self.extra_area_length,
                                                           cook_extra_len=self.extra_area_length)
        elif edge.len() <= np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 2.5 + 2 * self.extra_area_length + self.refrigerator_length:  # 双水槽+双灶台 + 两个额外区域 + 冰箱:   3.75m
            self.layout_with_predefined_length_in_one_edge(edge,
                                                           sink_len=self.high_degree_length_inc + self.min_length_pair[
                                                               0],
                                                           cooktop_len=self.high_degree_length_inc +
                                                                       self.min_length_pair[-1],
                                                           sink_extra_len=self.extra_area_length,
                                                           cook_extra_len=self.extra_area_length,
                                                           refrigerator_len=self.refrigerator_length)
        elif edge.len() <= np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 2.5 + 4 * self.extra_area_length + self.refrigerator_length:  # 双水槽+双灶台 + 两个额外区域扩展长度 + 冰箱:    4.35m
            extra_length = edge.len() - (np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 2.5 + self.refrigerator_length + 2 * self.extra_area_length)
            self.layout_with_predefined_length_in_one_edge(edge,
                                                           sink_len=self.high_degree_length_inc + self.min_length_pair[
                                                               0],
                                                           cooktop_len=self.high_degree_length_inc +
                                                                       self.min_length_pair[-1],
                                                           sink_extra_len=self.extra_area_length + extra_length / 2.,
                                                           cook_extra_len=self.extra_area_length + extra_length / 2.,
                                                           refrigerator_len=self.refrigerator_length)
        else:
            # 截取一段edge出来
            croppped_length = np.sum(
                self.min_length_pair) + self.high_degree_length_inc * 2.5 + 4 * self.extra_area_length + self.refrigerator_length
            p1 = edge.start
            dis_p1 = 1e8
            p2 = edge.end
            dis_p2 = 1e8
            for win in self.all_wins:
                if win['wall_ind'] == edge.wall_ind:
                    win_pts = win['win_pts']
                    if np.linalg.norm(np.mean(win_pts, axis=0) - p1) < dis_p1:
                        dis_p1 = np.linalg.norm(np.mean(win_pts, axis=0) - p1)
                    if np.linalg.norm(np.mean(win_pts, axis=0) - p2) < dis_p2:
                        dis_p2 = np.linalg.norm(np.mean(win_pts, axis=0) - p2)
            if dis_p1 < dis_p2:
                cropped_edge = Edge(p1,
                                    croppped_length / edge.len() * (p2 - p1) + p1,
                                    edge.norm,
                                    edge.wall_ind)
            else:
                cropped_edge = Edge(croppped_length / edge.len() * (p1 - p2) + p2,
                                    p2,
                                    edge.norm,
                                    edge.wall_ind)

            self.layout_with_predefined_length_in_one_edge(cropped_edge,
                                                           sink_len=self.high_degree_length_inc + self.min_length_pair[
                                                               0],
                                                           cooktop_len=self.high_degree_length_inc +
                                                                       self.min_length_pair[-1],
                                                           sink_extra_len=self.extra_area_length * 2,
                                                           cook_extra_len=self.extra_area_length * 2,
                                                           refrigerator_len=self.refrigerator_length)

    def layout_in_two_edge(self, edges):
        # 根据前边的短边过滤，此处两条边长度都应该大于1.1m=self.floor_cupboard_depth + self.unit_min_length
        cp_edges = copy.deepcopy(edges)
        # ensure the cook end point and sink end point is the intersection point
        cp_edges[1].start = edges[1].end
        cp_edges[1].end = edges[1].start

        # get win edge
        max_interaction_1, max_interaction_win_1 = self.compute_closest_win_interaction([cp_edges[1].start, cp_edges[1].end], cp_edges[1].wall_ind)
        max_interaction_0, max_interaction_win_0 = self.compute_closest_win_interaction([cp_edges[0].start, cp_edges[0].end], cp_edges[0].wall_ind)

        if max_interaction_0 - max_interaction_1 > 1e-3:
            sink_edge_ind = 0
        elif abs(max_interaction_0 - max_interaction_1) < 1e-3:
            if cp_edges[0].len() > cp_edges[1].len():
                sink_edge_ind = 1
            else:
                sink_edge_ind = 0
        else:
            sink_edge_ind = 1

        sink_edge = copy.deepcopy(cp_edges[sink_edge_ind])
        cook_edge = copy.deepcopy(cp_edges[1 - sink_edge_ind])

        # 处理烟道
        direct = self.valid_edge_dict[sink_edge.wall_ind] - self.valid_edge_dict[cook_edge.wall_ind]
        if abs(direct) == 1 or \
                abs(direct) == len(self.org_floor_pts) - 1:
            # 没有烟道
            sink_gap_end = self.floor_cabinet_depth / 2.
            cook_gap_end = 0.
        else:  # == 3
            org_range_wall_ind = np.sign(direct) + self.valid_edge_dict[cook_edge.wall_ind]
            org_range_edge = Edge(self.org_floor_pts[org_range_wall_ind % len(self.org_floor_pts)],
                                  self.org_floor_pts[(org_range_wall_ind + 1) % len(self.org_floor_pts)],
                                  sink_edge.norm, wall_ind=-1)

            sink_gap_end = org_range_edge.len()

            org_range_wall_ind = -np.sign(direct) + self.valid_edge_dict[sink_edge.wall_ind]
            org_range_edge = Edge(self.org_floor_pts[org_range_wall_ind % len(self.org_floor_pts)],
                                  self.org_floor_pts[(org_range_wall_ind + 1) % len(self.org_floor_pts)],
                                  sink_edge.norm, wall_ind=-1)
            cook_gap_end = org_range_edge.len()

        sink_next_edge_ind = (np.sign(direct) + sink_edge.wall_ind) % len(self.floor_pts)
        if abs(self.valid_edge_dict[sink_edge.wall_ind] - self.valid_edge_dict[sink_next_edge_ind]) == 1 or \
                abs(self.valid_edge_dict[sink_edge.wall_ind] - self.valid_edge_dict[sink_next_edge_ind]) == len(
            self.org_floor_pts) - 1:
            # 没有烟道
            sink_gap_start = 0.
        else:  # == 3
            org_range_wall_ind = np.sign(direct) * 2 + self.valid_edge_dict[sink_edge.wall_ind]
            org_range_edge = Edge(self.org_floor_pts[org_range_wall_ind % len(self.org_floor_pts)],
                                  self.org_floor_pts[(org_range_wall_ind + 1) % len(self.org_floor_pts)],
                                  sink_edge.norm, wall_ind=-1)
            sink_gap_start = org_range_edge.len()

        cook_next_edge_ind = (-np.sign(direct) + cook_edge.wall_ind) % len(self.floor_pts)
        if abs(self.valid_edge_dict[cook_edge.wall_ind] - self.valid_edge_dict[cook_next_edge_ind]) == 1 or \
           abs(self.valid_edge_dict[cook_edge.wall_ind] - self.valid_edge_dict[cook_next_edge_ind]) == len(
           self.org_floor_pts) - 1:
            # 没有烟道
            cook_gap_start = 0.
        else:  # == 3
            org_range_wall_ind = -np.sign(direct) * 2 + self.valid_edge_dict[cook_edge.wall_ind]
            org_range_edge = Edge(self.org_floor_pts[org_range_wall_ind % len(self.org_floor_pts)],
                                  self.org_floor_pts[(org_range_wall_ind + 1) % len(self.org_floor_pts)],
                                  sink_edge.norm, wall_ind=-1)
            cook_gap_start = org_range_edge.len()

        # 处理sink
        sink_length = self.min_length_pair[0] if sink_edge.len() < self.min_length_pair[
            0] + self.high_degree_length_inc + sink_gap_start + sink_gap_end else self.min_length_pair[
                                                                                   0] + self.high_degree_length_inc

        if sink_edge.len() - sink_length - (sink_gap_start + sink_gap_end) <= self.extra_area_length:
            if abs(sink_length - self.min_length_pair[0]) < 1e-3:
                sink_length = sink_edge.len() - (sink_gap_start + sink_gap_end)
            if sink_gap_start > 1e-3:
                start = (sink_edge.end - sink_edge.start) * sink_gap_start / sink_edge.len() + sink_edge.start
                end = (sink_edge.start - sink_edge.end) * sink_gap_end / sink_edge.len() + sink_edge.end
                valid_edge = Edge(start, end, sink_edge.norm, sink_edge.wall_ind)
                self.sink = self.find_max_interaction_edge_part_with_win(valid_edge, sink_length)

                self.sink_extra.start = sink_edge.start
                self.sink_extra.end = self.sink.start
                self.sink_extra.norm = self.sink.norm
                self.sink_extra.wall_ind = self.sink.wall_ind
            else:
                self.sink.start = sink_edge.start
                self.sink.end = (sink_edge.end - sink_edge.start) * (sink_length + sink_gap_start) / sink_edge.len() + sink_edge.start
                self.sink.norm = sink_edge.norm
                self.sink.wall_ind = sink_edge.wall_ind

            sink_left_preparation_edge = Edge(self.sink.end, sink_edge.end, sink_edge.norm, sink_edge.wall_ind)

        elif sink_edge.len() - sink_length - (sink_gap_start + sink_gap_end) <= self.extra_area_length * 2 + self.refrigerator_length:
            start = (sink_edge.end - sink_edge.start) * (self.extra_area_length + sink_gap_start) / sink_edge.len() + sink_edge.start
            end = (sink_edge.start - sink_edge.end) * sink_gap_end / sink_edge.len() + sink_edge.end
            valid_edge = Edge(start, end, sink_edge.norm, sink_edge.wall_ind)
            self.sink = self.find_max_interaction_edge_part_with_win(valid_edge, sink_length)

            self.sink_extra.start = sink_edge.start
            self.sink_extra.end = self.sink.start
            self.sink_extra.norm = self.sink.norm
            self.sink_extra.wall_ind = self.sink.wall_ind

            sink_left_preparation_edge = Edge(self.sink.end, sink_edge.end, sink_edge.norm, sink_edge.wall_ind)
        else:
            self.fridge.start = (sink_edge.end - sink_edge.start) * sink_gap_start / sink_edge.len() + sink_edge.start
            self.fridge.end = (sink_edge.end - sink_edge.start) * self.refrigerator_length / sink_edge.len() + self.fridge.start
            self.fridge.norm = sink_edge.norm
            self.fridge.wall_ind = sink_edge.wall_ind

            max_interaction, _ = self.compute_closest_win_interaction([self.fridge.start, self.fridge.end],
                                                                      self.fridge.wall_ind)
            fridge_end = self.fridge.end
            if max_interaction > 0:
                self.fridge = Edge()
                fridge_end = sink_edge.start
                start = (sink_edge.end - sink_edge.start) * (self.extra_area_length + sink_gap_start) / sink_edge.len() + sink_edge.start
            else:
                start = (sink_edge.end - sink_edge.start) * self.extra_area_length / sink_edge.len() + fridge_end
            end = (sink_edge.start - sink_edge.end) * sink_gap_end / sink_edge.len() + sink_edge.end
            valid_edge = Edge(start, end, sink_edge.norm, sink_edge.wall_ind)
            self.sink = self.find_max_interaction_edge_part_with_win(valid_edge, sink_length)

            self.sink_extra.start = fridge_end
            self.sink_extra.end = self.sink.start
            self.sink_extra.norm = self.sink.norm
            self.sink_extra.wall_ind = self.sink.wall_ind

            sink_left_preparation_edge = Edge(self.sink.end, sink_edge.end, sink_edge.norm, sink_edge.wall_ind)

        # 处理cook
        cook_length = self.min_length_pair[-1] if cook_edge.len() < self.min_length_pair[
            -1] + self.high_degree_length_inc + self.floor_cabinet_depth + cook_gap_start else self.min_length_pair[
                                                                                   -1] + self.high_degree_length_inc
        if cook_edge.len() - cook_length - self.floor_cabinet_depth - cook_gap_start <= self.extra_area_length:
            self.cooktop.start = (cook_edge.end - cook_edge.start) * cook_gap_start / cook_edge.len() + cook_edge.start
            self.cooktop.end = (cook_edge.end - cook_edge.start) * cook_length / cook_edge.len() + self.cooktop.start
            self.cooktop.norm = cook_edge.norm
            self.cooktop.wall_ind = cook_edge.wall_ind

            cook_left_preparation_edge = Edge(self.cooktop.end, cook_edge.end, cook_edge.norm, cook_edge.wall_ind)
            if cook_gap_start > 1e-3:
                self.cook_extra.start = cook_edge.start
                self.cook_extra.end = (cook_edge.end - cook_edge.start) * cook_gap_start / cook_edge.len() + cook_edge.start
                self.cook_extra.norm = cook_edge.norm
                self.cook_extra.wall_ind = cook_edge.wall_ind
        elif cook_edge.len() - cook_length - self.floor_cabinet_depth <= self.extra_area_length * 2:
            self.cook_extra.start = cook_edge.start
            self.cook_extra.end = (cook_edge.end - cook_edge.start) * (self.extra_area_length + cook_gap_start) / cook_edge.len() + cook_edge.start
            self.cook_extra.norm = cook_edge.norm
            self.cook_extra.wall_ind = cook_edge.wall_ind

            self.cooktop.start = self.cook_extra.end
            self.cooktop.end = (cook_edge.end - cook_edge.start) * cook_length / cook_edge.len() + self.cook_extra.end
            self.cooktop.norm = cook_edge.norm
            self.cooktop.wall_ind = cook_edge.wall_ind

            cook_left_preparation_edge = Edge(self.cooktop.end, cook_edge.end, cook_edge.norm, cook_edge.wall_ind)
        elif self.fridge.start is not None or cook_edge.len() - cook_length - self.floor_cabinet_depth - cook_gap_start \
                <= self.extra_area_length * 2 + self.refrigerator_length:

            left_length = cook_edge.len() - cook_length - self.floor_cabinet_depth
            self.cook_extra.start = cook_edge.start
            self.cook_extra.end = (cook_edge.end - cook_edge.start) * left_length / 2. / cook_edge.len() + cook_edge.start
            self.cook_extra.norm = cook_edge.norm
            self.cook_extra.wall_ind = cook_edge.wall_ind

            self.cooktop.start = self.cook_extra.end
            self.cooktop.end = (cook_edge.end - cook_edge.start) * cook_length / cook_edge.len() + self.cook_extra.end
            self.cooktop.norm = cook_edge.norm
            self.cooktop.wall_ind = cook_edge.wall_ind

            cook_left_preparation_edge = Edge(self.cooktop.end, cook_edge.end, cook_edge.norm, cook_edge.wall_ind)
        else:
            self.fridge.start = (cook_edge.end - cook_edge.start) * cook_gap_start / cook_edge.len() + cook_edge.start
            self.fridge.end = (cook_edge.end - cook_edge.start) / cook_edge.len() * self.refrigerator_length + cook_edge.start
            self.fridge.norm = cook_edge.norm
            self.fridge.wall_ind = cook_edge.wall_ind

            max_interaction, _ = self.compute_closest_win_interaction([self.fridge.start, self.fridge.end],
                                                                      self.fridge.wall_ind)
            fridge_end = self.fridge.end
            if max_interaction > 0:
                self.fridge = Edge()
                fridge_end = cook_edge.start
            left_length = cook_edge.len() - cook_length - self.floor_cabinet_depth - self.refrigerator_length
            self.cook_extra.start = fridge_end
            self.cook_extra.end = (cook_edge.end - cook_edge.start) * left_length / 2. / cook_edge.len() + fridge_end
            self.cook_extra.norm = cook_edge.norm
            self.cook_extra.wall_ind = cook_edge.wall_ind

            self.cooktop.start = self.cook_extra.end
            self.cooktop.end = (cook_edge.end - cook_edge.start) * cook_length / cook_edge.len() + self.cook_extra.end
            self.cooktop.norm = cook_edge.norm
            self.cooktop.wall_ind = cook_edge.wall_ind

            cook_left_preparation_edge = Edge(self.cooktop.end, cook_edge.end, cook_edge.norm, cook_edge.wall_ind)

        wall_cabinets_length = self.cooktop.len() + cook_left_preparation_edge.len() + self.cook_extra.len() - cook_gap_start
        cook_wall_cabinet_edge = Edge(cook_left_preparation_edge.end + (cook_edge.start - cook_edge.end) / cook_edge.len() * cook_gap_end,
                            (cook_left_preparation_edge.start - cook_left_preparation_edge.end) / cook_left_preparation_edge.len() * wall_cabinets_length + cook_left_preparation_edge.end,
                            cook_left_preparation_edge.norm,
                            cook_left_preparation_edge.wall_ind
                            )
        sink_left_preparation_cabinet_edge = copy.deepcopy(sink_left_preparation_edge)
        sink_left_preparation_cabinet_edge.end = (sink_left_preparation_edge.start - sink_left_preparation_edge.end) / sink_left_preparation_edge.len() * max(self.wall_cabinet_depth, sink_gap_end) + sink_left_preparation_edge.end

        if sink_left_preparation_edge.len() < cook_left_preparation_edge.len():
            cook_left_preparation_edge.end = (cook_left_preparation_edge.start - cook_left_preparation_edge.end) / cook_left_preparation_edge.len() * self.floor_cabinet_depth + cook_left_preparation_edge.end
        else:
            sink_left_preparation_edge.end = (sink_left_preparation_edge.start - sink_left_preparation_edge.end) / sink_left_preparation_edge.len() * self.floor_cabinet_depth + sink_left_preparation_edge.end
        self.preparation = [sink_left_preparation_edge, cook_left_preparation_edge]

        self.add_cabinets(sink_left_preparation_edge, sink_left_preparation_cabinet_edge)
        cabinets_length = self.cooktop.len() + cook_left_preparation_edge.len() + self.cook_extra.len()
        cabinet_edge = Edge(cook_left_preparation_edge.end,
                            (cook_left_preparation_edge.start - cook_left_preparation_edge.end) / cook_left_preparation_edge.len() * cabinets_length + cook_left_preparation_edge.end,
                            cook_left_preparation_edge.norm,
                            cook_left_preparation_edge.wall_ind
                            )
        self.add_cabinets(cabinet_edge, cook_wall_cabinet_edge)
        if self.sink_extra.start is not None:
            sink_extra_wall_cabinet_edge = copy.deepcopy(self.sink_extra)
            sink_extra_wall_cabinet_edge.start = (self.sink_extra.end - self.sink_extra.start) / self.sink_extra.len() * sink_gap_start + self.sink_extra.start
            self.add_cabinets(self.sink_extra, sink_extra_wall_cabinet_edge)

    def layout_in_three_edge(self, edges):
        #
        max_interaction = 0
        max_edge_ind = -1
        for i in range(len(edges)):
            edge = edges[i]
            interaction, _ = self.compute_closest_win_interaction([edge.start, edge.end], edge.wall_ind)
            if interaction - max_interaction > 1e-3 or (abs(interaction - max_interaction) < 1e-3 and edge.len() > edges[max_edge_ind].len()):
                max_interaction = interaction
                max_edge_ind = i
        if max_edge_ind == -1:
            sink_edge_ind = 2
            cook_edge_ind = 1
        else:
            sink_edge_ind = max_edge_ind
            if sink_edge_ind in [0, 2]:
                cook_edge_ind = 1
            else:
                cook_edge_ind = np.random.choice([0, 2])
            # max_length = -1
            # for i in range(len(edges)):
            #     if i == sink_edge_ind:
            #         continue
            #     if edges[i].len() > max_length:
            #         max_length = edges[i].len()
            # candidates = [i for i in range(len(edges)) if i != sink_edge_ind and abs(edges[i].len() - max_length) < 0.2]
            # cook_edge_ind = np.random.choice(candidates)

        sink_edge = copy.deepcopy(edges[sink_edge_ind])
        cook_edge = copy.deepcopy(edges[cook_edge_ind])
        # ensure the cook end point and sink end point is the intersection point
        if sink_edge_ind > cook_edge_ind:
            sink_edge.start = edges[sink_edge_ind].end
            sink_edge.end = edges[sink_edge_ind].start
        else:
            cook_edge.start = edges[cook_edge_ind].end
            cook_edge.end = edges[cook_edge_ind].start

        # 按照两条边的方法进行部署
        # 冰箱额外处理：水槽在中间边或水槽不在中间边，但也部署不下时，冰箱部署在剩余边；其他情况冰箱部署在水槽边
        # 处理sink
        sink_length = self.min_length_pair[0] if sink_edge.len() < self.min_length_pair[
            0] + self.high_degree_length_inc + self.floor_cabinet_depth / 2. else self.min_length_pair[
                                                                                  0] + self.high_degree_length_inc

        if sink_edge.len() - sink_length - self.floor_cabinet_depth / 2. <= self.extra_area_length:

            # self.sink_extra.start = sink_edge.start
            # self.sink_extra.end = (sink_edge.end - sink_edge.start) * self.extra_area_length / sink_edge.len() + sink_edge.start
            # self.sink_extra.norm = sink_edge.norm
            # self.sink_extra.wall_ind = sink_edge.wall_ind
            if abs(sink_length - self.min_length_pair[0]) < 1e-3:
                sink_length = sink_edge.len() - self.floor_cabinet_depth / 2.
            self.sink.start = sink_edge.start
            self.sink.end = (sink_edge.end - sink_edge.start) * sink_length / sink_edge.len() + self.sink.start
            self.sink.norm = sink_edge.norm
            self.sink.wall_ind = sink_edge.wall_ind

            sink_left_preparation_edge = Edge(self.sink.end, sink_edge.end, sink_edge.norm, sink_edge.wall_ind)
        elif sink_edge.len() - sink_length - self.floor_cabinet_depth / 2. <= self.extra_area_length * 2 + self.refrigerator_length or sink_edge_ind == 1:
            start = (sink_edge.end - sink_edge.start) * self.extra_area_length / sink_edge.len() + sink_edge.start
            end = (sink_edge.start - sink_edge.end) * self.floor_cabinet_depth / 2. / sink_edge.len() + sink_edge.end
            valid_edge = Edge(start, end, sink_edge.norm, sink_edge.wall_ind)
            self.sink = self.find_max_interaction_edge_part_with_win(valid_edge, sink_length)

            self.sink_extra.start = sink_edge.start
            self.sink_extra.end = self.sink.start
            self.sink_extra.norm = self.sink.norm
            self.sink_extra.wall_ind = self.sink.wall_ind

            sink_left_preparation_edge = Edge(self.sink.end, sink_edge.end, sink_edge.norm, sink_edge.wall_ind)
        else:
            self.fridge.start = sink_edge.start
            self.fridge.end = (sink_edge.end - sink_edge.start) * self.refrigerator_length / sink_edge.len() + sink_edge.start
            self.fridge.norm = sink_edge.norm
            self.fridge.wall_ind = sink_edge.wall_ind

            max_interaction, _ = self.compute_closest_win_interaction([self.fridge.start, self.fridge.end],
                                                                      self.fridge.wall_ind)
            fridge_end = self.fridge.end
            if max_interaction > 0:
                self.fridge = Edge()
                fridge_end = sink_edge.start
            start = (
                                sink_edge.end - sink_edge.start) * self.extra_area_length / sink_edge.len() + fridge_end
            end = (sink_edge.start - sink_edge.end) * self.floor_cabinet_depth / 2. / sink_edge.len() + sink_edge.end
            valid_edge = Edge(start, end, sink_edge.norm, sink_edge.wall_ind)
            self.sink = self.find_max_interaction_edge_part_with_win(valid_edge, sink_length)

            self.sink_extra.start = fridge_end
            self.sink_extra.end = self.sink.start
            self.sink_extra.norm = self.sink.norm
            self.sink_extra.wall_ind = self.sink.wall_ind

            sink_left_preparation_edge = Edge(self.sink.end, sink_edge.end, sink_edge.norm, sink_edge.wall_ind)

        # 处理cook
        cook_length = self.min_length_pair[-1] if cook_edge.len() < self.min_length_pair[
            -1] + self.high_degree_length_inc + self.floor_cabinet_depth else self.min_length_pair[
                                                                                   -1] + self.high_degree_length_inc
        if cook_edge.len() - cook_length - self.floor_cabinet_depth <= self.extra_area_length * 2:
            self.cook_extra.start = cook_edge.start
            self.cook_extra.end = (
                                          cook_edge.end - cook_edge.start) * self.extra_area_length / cook_edge.len() + cook_edge.start
            self.cook_extra.norm = cook_edge.norm
            self.cook_extra.wall_ind = cook_edge.wall_ind

            self.cooktop.start = self.cook_extra.end
            self.cooktop.end = (cook_edge.end - cook_edge.start) * cook_length / cook_edge.len() + self.cook_extra.end
            self.cooktop.norm = cook_edge.norm
            self.cooktop.wall_ind = cook_edge.wall_ind

            cook_left_preparation_edge = Edge(self.cooktop.end, cook_edge.end, cook_edge.norm, cook_edge.wall_ind)
        elif self.fridge.start is not None or cook_edge.len() - cook_length - self.floor_cabinet_depth <= self.extra_area_length * 2 + self.refrigerator_length or cook_edge_ind == 1:

            left_length = cook_edge.len() - cook_length - self.floor_cabinet_depth
            self.cook_extra.start = cook_edge.start
            self.cook_extra.end = (
                                          cook_edge.end - cook_edge.start) * left_length / 2. / cook_edge.len() + cook_edge.start
            self.cook_extra.norm = cook_edge.norm
            self.cook_extra.wall_ind = cook_edge.wall_ind

            self.cooktop.start = self.cook_extra.end
            self.cooktop.end = (cook_edge.end - cook_edge.start) * cook_length / cook_edge.len() + self.cook_extra.end
            self.cooktop.norm = cook_edge.norm
            self.cooktop.wall_ind = cook_edge.wall_ind

            cook_left_preparation_edge = Edge(self.cooktop.end, cook_edge.end, cook_edge.norm, cook_edge.wall_ind)
        else:
            self.fridge.start = cook_edge.start
            self.fridge.end = (
                                                cook_edge.end - cook_edge.start) / cook_edge.len() * self.refrigerator_length + cook_edge.start
            self.fridge.norm = cook_edge.norm
            self.fridge.wall_ind = cook_edge.wall_ind

            max_interaction, _ = self.compute_closest_win_interaction([self.fridge.start, self.fridge.end],
                                                                      self.fridge.wall_ind)
            fridge_end = self.fridge.end
            if max_interaction > 0:
                self.fridge = Edge()
                fridge_end = sink_edge.start

            left_length = cook_edge.len() - cook_length - self.floor_cabinet_depth - self.refrigerator_length
            self.cook_extra.start = fridge_end
            self.cook_extra.end = (
                                          cook_edge.end - cook_edge.start) * left_length / 2. / cook_edge.len() + fridge_end
            self.cook_extra.norm = cook_edge.norm
            self.cook_extra.wall_ind = cook_edge.wall_ind

            self.cooktop.start = self.cook_extra.end
            self.cooktop.end = (cook_edge.end - cook_edge.start) * cook_length / cook_edge.len() + self.cook_extra.end
            self.cooktop.norm = cook_edge.norm
            self.cooktop.wall_ind = cook_edge.wall_ind

            cook_left_preparation_edge = Edge(self.cooktop.end, cook_edge.end, cook_edge.norm, cook_edge.wall_ind)

        if sink_edge_ind + cook_edge_ind == 1:  # 剩余边是第三条边
            extra_edge = copy.deepcopy(edges[2])
            extra_edge.start = edges[2].end
            extra_edge.end = edges[2].start
        else:
            extra_edge = copy.deepcopy(edges[0])
        if self.fridge.start is None:
            self.fridge.start = extra_edge.start
            self.fridge.end = (extra_edge.end - extra_edge.start) * self.refrigerator_length / extra_edge.len() + extra_edge.start
            self.fridge.norm = extra_edge.norm
            self.fridge.wall_ind = extra_edge.wall_ind
            max_interaction, _ = self.compute_closest_win_interaction([self.fridge.start, self.fridge.end],
                                                                      self.fridge.wall_ind)
            fridge_end = self.fridge.end
            if max_interaction > 0:
                self.fridge = Edge()
                fridge_end = sink_edge.start
            third_edge_left_preparation_edge = Edge(fridge_end, extra_edge.end, extra_edge.norm, extra_edge.wall_ind)
        else:
            third_edge_left_preparation_edge = Edge(extra_edge.start, extra_edge.end, extra_edge.norm, extra_edge.wall_ind)

        # wall cabinet edge
        wall_cabinets_length = self.cooktop.len() + cook_left_preparation_edge.len() + self.cook_extra.len()
        cook_wall_cabinet_edge = Edge(cook_left_preparation_edge.end,
                                      (
                                                  cook_left_preparation_edge.start - cook_left_preparation_edge.end) / cook_left_preparation_edge.len() * wall_cabinets_length + cook_left_preparation_edge.end,
                                      cook_left_preparation_edge.norm,
                                      cook_left_preparation_edge.wall_ind
                                      )
        sink_left_preparation_cabinet_edge = copy.deepcopy(sink_left_preparation_edge)
        sink_left_preparation_cabinet_edge.end = (
                                                             sink_left_preparation_edge.start - sink_left_preparation_edge.end) / sink_left_preparation_edge.len() * self.wall_cabinet_depth + sink_left_preparation_edge.end
        third_wall_cabinet_edge = copy.deepcopy(third_edge_left_preparation_edge)
        sink_left_extra_cabinet_wall_edge = copy.deepcopy(self.sink_extra)
        if sink_edge_ind not in [0, 2]:
            if sink_left_extra_cabinet_wall_edge.start is not None:
                sink_left_extra_cabinet_wall_edge.start = (sink_left_extra_cabinet_wall_edge.end - sink_left_extra_cabinet_wall_edge.start) / sink_left_extra_cabinet_wall_edge.len() * self.wall_cabinet_depth + sink_left_extra_cabinet_wall_edge.start
        else:
            third_wall_cabinet_edge.start = (third_edge_left_preparation_edge.start - third_edge_left_preparation_edge.end) / third_edge_left_preparation_edge.len() * self.wall_cabinet_depth + third_edge_left_preparation_edge.end
        if sink_left_preparation_edge.len() < cook_left_preparation_edge.len():
            cook_left_preparation_edge.end = (cook_left_preparation_edge.start - cook_left_preparation_edge.end) / cook_left_preparation_edge.len() * self.floor_cabinet_depth + cook_left_preparation_edge.end
        else:
            sink_left_preparation_edge.end = (sink_left_preparation_edge.start - sink_left_preparation_edge.end) / sink_left_preparation_edge.len() * self.floor_cabinet_depth + sink_left_preparation_edge.end
        if third_edge_left_preparation_edge.len() < self.cook_extra.len():
            self.cook_extra.start = (self.cook_extra.end - self.cook_extra.start) / self.cook_extra.len() * self.floor_cabinet_depth + self.cook_extra.start
        else:
            third_edge_left_preparation_edge.end = (third_edge_left_preparation_edge.start - third_edge_left_preparation_edge.end) / third_edge_left_preparation_edge.len() * self.floor_cabinet_depth + third_edge_left_preparation_edge.end
        if sink_left_preparation_edge.len() > 1e-3:
            self.preparation.append(sink_left_preparation_edge)
        if cook_left_preparation_edge.len() > 1e-3:
            self.preparation.append(cook_left_preparation_edge)
        if third_edge_left_preparation_edge.len() > 1e-3:
            self.extra.append(third_edge_left_preparation_edge)

        cabinets_length = self.cooktop.len() + cook_left_preparation_edge.len() + self.cook_extra.len()
        cabinet_edge = Edge(cook_left_preparation_edge.end,
                            (
                                        cook_left_preparation_edge.start - cook_left_preparation_edge.end) / cook_left_preparation_edge.len() * cabinets_length + cook_left_preparation_edge.end,
                            cook_left_preparation_edge.norm,
                            cook_left_preparation_edge.wall_ind
                            )
        self.add_cabinets(cabinet_edge, cook_wall_cabinet_edge)

        self.add_cabinets(self.sink_extra, sink_left_extra_cabinet_wall_edge)
        self.add_cabinets(sink_left_preparation_edge, sink_left_preparation_cabinet_edge)

        # fridge occlude with win
        # if self.fridge.start is not None:
        #     max_interaction, _ = self.compute_closest_win_interaction([self.fridge.start, self.fridge.end], self.fridge.wall_ind)
        #     if max_interaction > 0:
        #         self.extra.append(copy.deepcopy(self.fridge))
        #         self.fridge = Edge()
        # for extra in self.extra:
        self.add_cabinets(third_edge_left_preparation_edge, third_wall_cabinet_edge)

    def add_cabinets(self, floor_edge, wall_edge):
        if floor_edge.len() > 1e-3:

            unit_num = floor_edge.len() // self.unit_std_length
            if abs(floor_edge.len() / (unit_num + 1e-3) / self.unit_std_length - 1) > abs(self.unit_std_length / (floor_edge.len() / (unit_num + 1.)) - 1):
                unit_num += 1
            if unit_num > 0:
                unit_length = floor_edge.len() / unit_num
                # if 0.7 * self.unit_std_length <= edge.len() / (unit_num + 1e-3) <= 1.3 * self.unit_std_length:
                #     unit_length = edge.len() / unit_num
                # else:
                #     unit_num += 1
                #     unit_length = edge.len() / unit_num
                direct = floor_edge.end - floor_edge.start
                direct = direct / np.linalg.norm(direct) * unit_length
                for i in range(int(unit_num)):
                    self.floor_cabinets.append(
                        Edge(floor_edge.start + direct * i, floor_edge.start + direct * (i + 1),
                             floor_edge.norm, floor_edge.wall_ind))

        # wall cabinet
        if wall_edge.len() >= self.wall_cabinet_std_length / 2.:

            unit_num = wall_edge.len() // self.wall_cabinet_std_length
            if abs(wall_edge.len() / (unit_num + 1e-3) / self.unit_std_length - 1) > abs(
                    self.unit_std_length / (wall_edge.len() / (unit_num + 1.)) - 1):
                unit_num += 1
            if unit_num > 0:
                unit_length = wall_edge.len() / unit_num
                # if 0.7 * self.unit_std_length <= wall_edge.len() / (unit_num + 1e-3) <= 1.3 * self.unit_std_length:
                #     unit_length = wall_edge.len() / unit_num
                # else:
                #     unit_num += 1
                #     unit_length = wall_edge.len() / unit_num
                direct = wall_edge.end - wall_edge.start
                direct = direct / np.linalg.norm(direct) * unit_length
                for i in range(int(unit_num)):
                    self.wall_cabinets.append(
                        Edge(wall_edge.start + direct * i, wall_edge.start + direct * (i + 1),
                             wall_edge.norm, wall_edge.wall_ind))

    def refine_floor_pts(self, floor_pts):
        range_non_convex_p_inds = []

        for i in range(len(floor_pts)):
            prev_ind = (i - 1) % len(floor_pts)
            next_ind = (i + 1) % len(floor_pts)
            prev_edge = np.array(floor_pts[i]) - np.array(floor_pts[prev_ind])
            next_edge = np.array(floor_pts[next_ind]) - np.array(floor_pts[i])
            if np.cross(prev_edge, next_edge) > 0 and np.linalg.norm(prev_edge) <= self.floor_cabinet_depth and \
                    np.linalg.norm(next_edge) <= self.floor_cabinet_depth:

                prev_prev_pts = np.array(floor_pts[(i - 2) % len(floor_pts)])
                next_next_pts = np.array(floor_pts[(i + 2) % len(floor_pts)])
                if np.linalg.norm(np.array(floor_pts[prev_ind]) - prev_prev_pts) < self.floor_cabinet_depth * 1.2 or \
                        np.linalg.norm(
                            np.array(floor_pts[next_ind]) - next_next_pts) < self.floor_cabinet_depth * 1.2:
                    continue
                # 连续两个烟道点不符合烟道定义，剔除
                if len(range_non_convex_p_inds) > 0 and abs(range_non_convex_p_inds[-1][0] - i) < 1.5:
                    range_non_convex_p_inds.pop(-1)
                    continue
                # 求交点
                alpha = 1e-10
                k1 = (np.array(floor_pts[prev_ind])[0] - prev_prev_pts[0]) / (np.array(floor_pts[prev_ind])[1] - prev_prev_pts[1] + alpha)
                k2 = (np.array(floor_pts[next_ind])[0] - next_next_pts[0]) / (np.array(floor_pts[next_ind])[1] - next_next_pts[1] + alpha)

                intersect_x = (next_next_pts[1] - prev_prev_pts[1] + 1./(k1 + alpha) * prev_prev_pts[0] - 1./(k2 + alpha) * next_next_pts[0]) / (1./(k1 + alpha) - 1./(k2 + alpha) + alpha)
                intersect_y = (next_next_pts[0] - prev_prev_pts[0] + k1 * prev_prev_pts[1] - k2 * next_next_pts[1]) / (k1 - k2 + alpha)
                move_dis = np.linalg.norm(np.array([intersect_x, intersect_y]) - np.array(floor_pts[i]))
                if move_dis < np.linalg.norm(prev_edge) * 1.2 and move_dis < np.linalg.norm(next_edge) * 1.2:
                    range_non_convex_p_inds.append([i, [intersect_x, intersect_y]])

        out_pts = copy.deepcopy(floor_pts)
        wall_dict = {}
        for i in range(len(floor_pts)):
            wall_dict[i] = {'wall': i, 'pseudo': False}
        bias = 0
        for i in range(len(range_non_convex_p_inds)):
            range_pt_ind, pts = range_non_convex_p_inds[i]
            pop_pos = range_pt_ind - 1 - i * 2 + bias

            out_pts.pop(pop_pos)
            if pop_pos == -1:
                bias = 1
                out_pts.pop(pop_pos + 1)
                out_pts[pop_pos + 1] = pts
            elif pop_pos == len(out_pts) - 1:
                out_pts.pop(pop_pos)
                out_pts[0] = pts
            else:
                out_pts.pop(pop_pos)
                out_pts[pop_pos] = pts

            wall_dict[(range_pt_ind - 1) % len(wall_dict)]['pseudo'] = True
            wall_dict[range_pt_ind]['pseudo'] = True

            wall_dict[(range_pt_ind - 1) % len(wall_dict)]['wall'] -= 1
            if range_pt_ind == 0:
                for j in range(range_pt_ind + 1, len(wall_dict)):
                    wall_dict[j]['wall'] -= 1
            elif range_pt_ind == len(floor_pts) - 1:
                wall_dict[range_pt_ind]['wall'] = 0
            else:
                wall_dict[range_pt_ind]['wall'] -= 1
                for j in range(range_pt_ind + 1, len(wall_dict)):
                    wall_dict[j]['wall'] -= 2

        valid_edge_dict = {}
        for k, v in wall_dict.items():
            if v['wall'] == -1:
                wall_dict[k]['wall'] = len(out_pts) - 1
            if not v['pseudo']:
                valid_edge_dict[v['wall']] = k
        for i in range(len(out_pts)):
            out_pts[i][0] = round(out_pts[i][0], 5)
            out_pts[i][1] = round(out_pts[i][1], 5)

        return out_pts, wall_dict, valid_edge_dict



