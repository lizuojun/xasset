import numpy as np
import copy
from .recon_mesh import Mesh


class WallBuild:
    def __init__(self, wall_info):
        self.wall_info = wall_info
        self.floor_pts = self.wall_info['layout_pts']
        self.wall_height = self.wall_info['height']
        self.uid = self.wall_info['mesh_id'] + '_%d' % self.wall_info['name']
        self.mesh_info = {}

    def build_mesh(self):

        # floor_idx = self.wall_info['name']

        norm_pt = (np.array(self.floor_pts[0]) + np.array(self.floor_pts[1])) / 2.
        norm_pt = [norm_pt[0], self.wall_height / 2., norm_pt[1]]

        segments = self.wall_info['segments']
        start_pt = self.floor_pts[0]
        end_pt = self.floor_pts[1]
        u_dir = [end_pt[0] - start_pt[0], 0.0, end_pt[1] - start_pt[1]]
        offset_dir = self.wall_info['normal']
        for wall_idx in range(len(segments)):
            # 对该面墙与踢脚线进行重建, 门窗信息在add_to_line里面重建
            # 过滤掉窗的情况 踢脚线不考虑

            line_pts_type = segments[wall_idx]['line_pts_type']
            line_pts_list = segments[wall_idx]['line_pts_list']

            segment = segments[wall_idx]

            # wall build
            meshes, norm_pt = self.build_wall_inner(self.uid + '_%d' % wall_idx, line_pts_list, line_pts_type, offset_dir, u_dir,
                                                    segment, norm_pt)
            self.mesh_info[wall_idx] = meshes

    def build_wall_inner(self, wall_uid, line_pts_list, line_pts_type, normal, u_dir, segment,
                         norm_pt=None):
        if np.max(np.max(line_pts_list, axis=0) - np.min(line_pts_list, axis=0)) < 1e-3:
            return [], norm_pt
        build_full_wall = len(segment['mid_ind']) > 0
        # door_height = param_wall_info['door_height']
        # window_top = param_wall_info['window_top']
        # window_height = param_wall_info['window_height']

        mesh = Mesh('WallInner', wall_uid + '_front')
        mesh_addition = None
        # 组成三维多边形 用于重建
        ploy_pts = [[line_pts_list[-1][0], 0.0, line_pts_list[-1][1]],
                    [line_pts_list[-1][0], self.wall_height, line_pts_list[-1][1]],
                    [line_pts_list[0][0], self.wall_height, line_pts_list[0][1]],
                    [line_pts_list[0][0], 0., line_pts_list[0][1]]]

        mesh_additions = []
        for i in range(1, len(line_pts_list) - 1, 2):
            ploy_pts.append([line_pts_list[i][0], 0.0, line_pts_list[i][1]])
            if line_pts_type[i]['type'] == 1:
                door_height = line_pts_type[i]['height']
                ploy_pts.append([line_pts_list[i][0], door_height, line_pts_list[i][1]])
                ploy_pts.append([line_pts_list[i + 1][0], door_height, line_pts_list[i + 1][1]])
            elif line_pts_type[i]['type'] == 2:
                window_top = line_pts_type[i]['top']
                window_height = line_pts_type[i]['bottom']
                ploy_pts.append([line_pts_list[i][0], window_top, line_pts_list[i][1]])
                ploy_pts.append([line_pts_list[i + 1][0], window_top, line_pts_list[i + 1][1]])
                mesh_addition = Mesh('WallInner', wall_uid + '_window_%d' % i)
                # 窗 window
                window_ploy_pts = [[line_pts_list[i + 1][0], 0.0, line_pts_list[i + 1][1]],
                                   [line_pts_list[i + 1][0], window_height, line_pts_list[i + 1][1]],
                                   [line_pts_list[i][0], window_height, line_pts_list[i][1]],
                                   [line_pts_list[i][0], 0., line_pts_list[i][1]]]
                mesh_addition.set_u_dir(u_dir)
                mesh_addition.build_mesh(window_ploy_pts, [normal[0], 0.0, normal[1]])
                mesh_additions.append(copy.deepcopy(mesh_addition))
            ploy_pts.append([line_pts_list[i + 1][0], 0.0, line_pts_list[i + 1][1]])

        mesh.set_u_dir(u_dir)
        mesh.build_mesh(ploy_pts, [normal[0], 0.0, normal[1]])
        if norm_pt is None:
            norm_pt = np.mean(ploy_pts, axis=0).tolist()
        mesh.set_uv_norm_pt(norm_pt)
        mesh_list = [mesh]
        for mesh_addition in mesh_additions:
            mesh_addition.set_uv_norm_pt(norm_pt)
            mesh_list.append(mesh_addition)

        # full wall mesh
        if build_full_wall:
            # outer face
            if segment['outer_wall'] and len(segment['outer_pts']) > 0:
                outer_pts = segment['outer_pts']
                mesh = Mesh('WallOuter', wall_uid + '_outer')
                # 组成三维多边形 用于重建

                ploy_pts = [[line_pts_list[-1][0], 0.0, line_pts_list[-1][1]],
                            [line_pts_list[-1][0], self.wall_height, line_pts_list[-1][1]],
                            [line_pts_list[0][0], self.wall_height, line_pts_list[0][1]],
                            [line_pts_list[0][0], 0., line_pts_list[0][1]]]

                mesh_additions = []
                for i in range(1, len(line_pts_list) - 1, 2):
                    ploy_pts.append([line_pts_list[i][0], 0.0, line_pts_list[i][1]])
                    if line_pts_type[i]['type'] == 1:
                        door_height = line_pts_type[i]['height']
                        ploy_pts.append([line_pts_list[i][0], door_height, line_pts_list[i][1]])
                        ploy_pts.append([line_pts_list[i + 1][0], door_height, line_pts_list[i + 1][1]])
                    elif line_pts_type[i]['type'] == 2:
                        window_top = line_pts_type[i]['top']
                        window_height = line_pts_type[i]['bottom']
                        ploy_pts.append([line_pts_list[i][0], window_top, line_pts_list[i][1]])
                        ploy_pts.append([line_pts_list[i + 1][0], window_top, line_pts_list[i + 1][1]])
                        mesh_addition = Mesh('WallOuter', wall_uid + '_window_outer')
                        # 窗 window
                        window_ploy_pts = [[line_pts_list[i + 1][0], 0.0, line_pts_list[i + 1][1]],
                                           [line_pts_list[i + 1][0], window_height, line_pts_list[i + 1][1]],
                                           [line_pts_list[i][0], window_height, line_pts_list[i][1]],
                                           [line_pts_list[i][0], 0., line_pts_list[i][1]]]

                        window_ploy_pts = (np.array(window_ploy_pts) -
                                           np.array([normal[0], 0.0, normal[1]]) * segment['depth'])[::-1, :]
                        mesh_addition.build_mesh(window_ploy_pts.tolist(), [-normal[0], 0.0, -normal[1]])
                        mesh_additions.append(copy.deepcopy(mesh_addition))
                    ploy_pts.append([line_pts_list[i + 1][0], 0.0, line_pts_list[i + 1][1]])

                ploy_pts = np.array(ploy_pts) - np.array([normal[0], 0.0, normal[1]]) * segment['depth']
                ploy_pts[0, :] = np.array([outer_pts[1][0], 0., outer_pts[1][1]])
                ploy_pts[1, :] = np.array([outer_pts[1][0], self.wall_height, outer_pts[1][1]])
                ploy_pts[2, :] = np.array([outer_pts[0][0], self.wall_height, outer_pts[0][1]])
                ploy_pts[3, :] = np.array([outer_pts[0][0], 0., outer_pts[0][1]])
                ploy_pts = ploy_pts[::-1, :]
                mesh.build_mesh(ploy_pts.tolist(), [-normal[0], 0.0, -normal[1]])
                mesh_list.append(mesh)
                mesh_list += mesh_additions

            mid_pts = segment['mid_pts']
            inner_pts = segment['inner_pts']
            # top face
            ploy_pts = [[inner_pts[0][0], self.wall_height, inner_pts[0][1]],
                        [mid_pts[0][0], self.wall_height, mid_pts[0][1]],
                        [mid_pts[1][0], self.wall_height, mid_pts[1][1]],
                        [inner_pts[1][0], self.wall_height, inner_pts[1][1]]]
            mesh_top = Mesh('WallTop', wall_uid + '_top')
            mesh_top.build_mesh(ploy_pts, [0., 1.0, 0])
            mesh_list.append(mesh_top)
            if segment['outer_wall'] and len(segment['outer_pts']) > 0:
                outer_pts = segment['outer_pts']
                ploy_pts = [
                    [mid_pts[0][0], self.wall_height, mid_pts[0][1]],
                    [outer_pts[0][0], self.wall_height, outer_pts[0][1]],
                    [outer_pts[1][0], self.wall_height, outer_pts[1][1]],
                    [mid_pts[1][0], self.wall_height, mid_pts[1][1]]
                ]
                mesh_top = Mesh('WallTop', wall_uid + '_top_outer')
                mesh_top.build_mesh(ploy_pts, [0., 1.0, 0])
                mesh_list.append(mesh_top)
            # bottom face
            ploy_pts = [
                [mid_pts[0][0], -0.002, mid_pts[0][1]],
                [inner_pts[0][0], -0.002, inner_pts[0][1]],
                [inner_pts[1][0], -0.002, inner_pts[1][1]],
                [mid_pts[1][0], -0.002, mid_pts[1][1]]
            ]
            mesh_bottom = Mesh('WallBottom', wall_uid + '_bottom')
            mesh_bottom.build_mesh(ploy_pts, [0., -1.0, 0])
            mesh_list.append(mesh_bottom)

            if segment['outer_wall'] and len(segment['outer_pts']) > 0:
                outer_pts = segment['outer_pts']
                ploy_pts = [
                    [mid_pts[0][0], -0.002, mid_pts[0][1]],
                    [outer_pts[0][0], -0.002, outer_pts[0][1]],
                    [outer_pts[1][0], -0.002, outer_pts[1][1]],
                    [mid_pts[1][0], -0.002, mid_pts[1][1]]
                ]
                mesh_bottom = Mesh('WallBottom', wall_uid + '_bottom_outer')
                mesh_bottom.build_mesh(ploy_pts, [0., -1.0, 0])
                mesh_list.append(mesh_bottom)
            # left face
            if 0 not in segment['depth_bias_pt']:
                ploy_pts = [[mid_pts[0][0], 0.0, mid_pts[0][1]],
                            [mid_pts[0][0], self.wall_height, mid_pts[0][1]],
                            [inner_pts[0][0], self.wall_height, inner_pts[0][1]],
                            [inner_pts[0][0], 0., inner_pts[0][1]]]
                norm = np.array(mid_pts[0]) - np.array(inner_pts[0])
                norm = norm / np.linalg.norm(norm)
                norm = [-norm[1], norm[0]]
                if np.dot(norm, np.array(inner_pts[1]) - np.array(inner_pts[0])) > 0:
                    norm = - np.array(norm)
                mesh_left = Mesh('WallLeft', wall_uid + '_left')
                mesh_left.build_mesh(ploy_pts, [norm[0], 0.0, norm[1]])
                mesh_list.append(mesh_left)

                if segment['outer_wall'] and len(segment['outer_pts']) > 0:
                    outer_pts = segment['outer_pts']
                    ploy_pts = [[outer_pts[0][0], 0., outer_pts[0][1]],
                                [outer_pts[0][0], self.wall_height, outer_pts[0][1]],
                                [mid_pts[0][0], self.wall_height, mid_pts[0][1]],
                                [mid_pts[0][0], 0.0, mid_pts[0][1]]
                                ]
                    norm = np.array(mid_pts[0]) - np.array(outer_pts[0])
                    norm = norm / np.linalg.norm(norm)
                    norm = [-norm[1], norm[0]]
                    if np.dot(norm, np.array(outer_pts[1]) - np.array(outer_pts[0])) > 0:
                        norm = - np.array(norm)
                    mesh_left = Mesh('WallLeft', wall_uid + '_left_outer')
                    mesh_left.build_mesh(ploy_pts, [norm[0], 0.0, norm[1]])
                    mesh_list.append(mesh_left)
            # right face
            if 1 not in segment['depth_bias_pt']:
                ploy_pts = [[inner_pts[1][0], 0., inner_pts[1][1]],
                            [inner_pts[1][0], self.wall_height, inner_pts[1][1]],
                            [mid_pts[1][0], self.wall_height, mid_pts[1][1]],
                            [mid_pts[1][0], 0.0, mid_pts[1][1]]
                            ]
                norm = np.array(mid_pts[1]) - np.array(inner_pts[1])
                norm = norm / np.linalg.norm(norm)
                norm = [-norm[1], norm[0]]
                if np.dot(norm, np.array(inner_pts[0]) - np.array(inner_pts[1])) > 0:
                    norm = - np.array(norm)
                mesh_right = Mesh('WallRight', wall_uid + '_right')
                mesh_right.build_mesh(ploy_pts, [norm[0], 0.0, norm[1]])
                mesh_list.append(mesh_right)

                if segment['outer_wall'] and len(segment['outer_pts']) > 0:
                    outer_pts = segment['outer_pts']
                    ploy_pts = [[mid_pts[0][0], 0.0, mid_pts[0][1]],
                                [mid_pts[0][0], self.wall_height, mid_pts[0][1]],
                                [outer_pts[0][0], self.wall_height, outer_pts[0][1]],
                                [outer_pts[0][0], 0., outer_pts[0][1]]]
                    norm = np.array(mid_pts[0]) - np.array(outer_pts[0])
                    norm = norm / np.linalg.norm(norm)
                    norm = [-norm[1], norm[0]]
                    if np.dot(norm, np.array(outer_pts[0]) - np.array(outer_pts[1])) > 0:
                        norm = - np.array(norm)
                    mesh_left = Mesh('WallRight', wall_uid + '_right_outer')
                    mesh_left.build_mesh(ploy_pts, [norm[0], 0.0, norm[1]])
                    mesh_list.append(mesh_left)

        mesh_list = self.build_material(segment['material'], mesh_list)

        return mesh_list, norm_pt

    def build_material(self, material, mesh_list):
        main_mat = material['main']
        seam_mat = material['seam'] if 'seam' in material else None
        default_mat = material['default']

        new_mesh = []
        for mesh in mesh_list:
            if mesh.mesh_type == 'WallInner':

                if 'type' in main_mat and ('ceramic main floor' in main_mat['type'] or 'ceramic wall' in main_mat['type']) and seam_mat is not None:
                    mesh.mat['jid'] = seam_mat['jid']
                    mesh.mat['texture'] = seam_mat['texture']
                    mesh.mat['color'] = seam_mat['color']
                    mesh.mat['colorMode'] = seam_mat['colorMode']
                    mesh.build_uv(seam_mat['uv_ratio'])

                    ceramic_meshes, area, centroid = mesh.ceramic_layout(main_mat)
                    for m in ceramic_meshes:
                        new_mesh.append(m)
                else:
                    mesh.mat['jid'] = main_mat['jid']
                    mesh.mat['texture'] = main_mat['texture']
                    mesh.mat['color'] = main_mat['color']
                    mesh.mat['colorMode'] = main_mat['colorMode']
                    mesh.build_uv(np.array(main_mat['uv_ratio']))
            else:
                mesh.mat['jid'] = default_mat['jid']
                mesh.mat['texture'] = default_mat['texture']
                mesh.mat['color'] = default_mat['color']
                mesh.mat['colorMode'] = default_mat['colorMode']
                mesh.build_uv(np.array(default_mat['uv_ratio']))

        return mesh_list + new_mesh
