import numpy as np

from .recon_mesh import Mesh
from ..Base.math_util import get_pt_distance


class WindowBuild(object):
    def __init__(self, win):
        self.uid = win['name']
        self.pocket_style = 0

        self.target_room_id = win['target_room_id']
        self.target_room_type = win['target_room_type']
        self.base_room_type = win['base_room_type']
        self.base_room_id = win['base_room_id']
        name_list = sorted([self.target_room_id, self.base_room_id])

        self.pts = win['layout_pts']
        self.depth = win['depth']
        self.length = get_pt_distance(self.pts[0], self.pts[1])
        self.mesh_info = {'extension': []}
        self.face_offset = win['normal']
        self.pos = [0., 0., 0.]
        self.rotation = [0, 0, 0, 1]
        self.scale = [1, 1, 1]
        self.name = '_'.join(name_list + [str(round(self.length, 3))])
        self.jid = ''
        self.bottom = win['bottom']
        self.top = win['top']
        # 根据 window_length 和 高度 来判断放置什么窗

        # win_type = ['BayWindow', 'FrenchWindow', 'Window']
        self.win_type = win['type']

        self.height = self.top - self.bottom

        self.set_pos_and_rot(self.bottom)

    def build_mesh(self):
        # 设置 self.jid = ''
        ext_mesh = self.build_extension_mesh(self.pts)
        e_mesh_i = Mesh('Window', self.uid + '_ext_base')
        e_mesh_i.build_exists_mesh(ext_mesh[0], ext_mesh[1], ext_mesh[2], ext_mesh[3])

        self.mesh_info = {'extension': [e_mesh_i]}

    def build_extension_mesh(self, pts_org):
        base_vec = [1, 0]
        line_vec = np.array(pts_org[1]) - np.array(pts_org[0])
        if np.linalg.norm(line_vec) < 1e-3:
            r_matrix = np.mat([[1, 0], [0, 1.]])
        else:
            line_vec_norm = line_vec / np.linalg.norm(line_vec)
            sin = np.cross(base_vec, line_vec_norm)
            cos = np.dot(base_vec, line_vec_norm)

            r_matrix = np.mat([[cos, sin], [-sin, cos]])
        pts = np.array((r_matrix * np.mat(np.array(pts_org) - np.array(pts_org[0])).transpose()).transpose())
        r_matrix_inv = np.linalg.inv(r_matrix)
        if abs(pts[0][0] - pts[1][0]) < abs(pts[0][1] - pts[1][1]):
            base_axis = 0
            change_axis = 1
        else:
            base_axis = 1
            change_axis = 0

        offset = 0.5 * self.depth
        self_offset = np.array((r_matrix * np.mat(self.face_offset).transpose()).transpose())[0]
        if self_offset[1] > 0.5 and base_axis == 1:
            offset = -0.5 * self.depth
        elif self_offset[0] > 0.5 and base_axis == 0:
            offset = -0.5 * self.depth

        start = pts[0][change_axis]
        end = pts[1][change_axis]
        base = pts[0][base_axis]

        v_0 = [start, start, start, start, end, end,
               end, end, end, start, start, end,
               start, end, end, start]
        v_1 = [self.top, self.top, self.bottom, self.bottom,
               self.top, self.top, self.bottom, self.bottom,
               self.top, self.top, self.top,
               self.top, self.bottom, self.bottom, self.bottom,
               self.bottom]
        v_2 = [base, base + offset, base + offset, base,
               base + offset, base, base, base + offset,
               base + offset, base + offset, base, base,
               base + offset, base + offset, base, base]
        n_0 = [-1, -1, -1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        n_1 = [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, 1, 1, 1, 1]
        n_2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        face = [3, 1, 2, 1, 3, 0, 7, 5, 6, 5, 7, 4, 11, 9, 10, 9, 11, 8, 15, 13, 14, 13, 15, 12]

        # uv change
        uv = [
            0,
            -0.25,
            -0.24,
            -0.25,
            -0.24,
            -1.75,
            0,
            -1.75,
            -0.24,
            -0.25,
            0,
            -0.25,
            0,
            -1.75,
            -0.24,
            -1.75,
            -0.11706,
            -0.24,
            -1.27054,
            -0.24,
            -1.27054,
            0,
            -0.11706,
            0,
            1.27054,
            -0.24,
            0.11706,
            -0.24,
            0.11706,
            0,
            1.27054,
            0]

        v = []
        n = []

        if change_axis == 0:
            for i in range(len(v_0)):
                v.append(v_0[i])
                v.append(v_1[i])
                v.append(v_2[i])

                n.append(n_0[i])
                n.append(n_1[i])
                n.append(n_2[i])
        else:
            for i in range(len(v_0)):
                v.append(v_2[i])
                v.append(v_1[i])
                v.append(v_0[i])

                n.append(n_2[i])
                n.append(n_1[i])
                n.append(n_0[i])
        v = np.reshape(v, [-1, 3])
        v[:, [0, 2]] = np.array((r_matrix_inv * np.mat(v[:, [0, 2]]).transpose()).transpose()) + np.array(pts_org[0])
        v = np.reshape(v, [-1]).tolist()

        n = np.reshape(n, [-1, 3])
        n = np.array(n, np.float)
        n[:, [0, 2]] = np.array((r_matrix_inv * np.mat(n[:, [0, 2]]).transpose()).transpose())
        n = np.reshape(n, [-1]).tolist()
        return [v, n, uv, face]

    def set_pos_and_rot(self, height=0.6):
        mid_p = [0.5 * (self.pts[0][0] + self.pts[1][0]), height,
                 0.5 * (self.pts[0][1] + self.pts[1][1])]
        self.pos = [mid_p[0] - 0.5 * self.depth * self.face_offset[0], height,
                    mid_p[2] - 0.5 * self.depth * self.face_offset[1]]
        ang = np.arcsin(-self.face_offset[1])
        if self.face_offset[0] < -0.001:
            ang = np.pi - ang
        ang -= np.pi / 2
        self.rotation = [0.0, np.sin(ang / 2.), 0.0, np.cos(ang / 2.)]

    def build_material(self, material):
        main_mat = material['main']

        for name, meshes in self.mesh_info.items():
            for mesh in meshes:
                mesh.mat['jid'] = main_mat['jid']
                mesh.mat['texture'] = main_mat['texture']
                mesh.mat['color'] = main_mat['color']
                mesh.mat['colorMode'] = main_mat['colorMode']
                mesh.build_uv(np.array(main_mat['uv_ratio']))