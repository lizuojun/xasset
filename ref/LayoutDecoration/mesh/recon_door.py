import numpy as np

from .recon_mesh import Mesh
from ..Base.math_util import get_pt_distance
from ..Base.recon_params import ROOM_BUILD_TYPE


# pocket 古典风格 10 左右 默认6-8cm
# swing door 80-90 200
# sling door
# entry door
class DoorBuild(object):
    def __init__(self, door):
        self.pocket_style = 0
        self.uid = door['name']

        self.target_room_id = door['target_room_id']
        self.target_room_type = door['target_room_type']
        self.base_room_type = door['base_room_type']
        self.base_room_id = door['base_room_id']
        self.is_hole = door['is_hole']

        name_list = sorted([self.target_room_id, self.base_room_id])

        self.face_offset = door['normal']
        self.height = door['height']

        self.if_main_door = False
        if len(self.target_room_id) == 0:
            self.if_main_door = True

        self.pts = door['layout_pts']
        self.depth = door['depth']
        self.length = get_pt_distance(self.pts[0], self.pts[1])

        self.name = '_'.join(name_list + [str(round(self.length, 3))])

        self.mesh_info = {'pocket': [], 'extension': [], 'floor': []}
        self.pos = [0, 0, 0]
        self.rotation = [0, 0, 0, 1]
        self.scale = [1, 1, 1]
        self.jid = ''

        door_type = ['Entry', 'BathRoom', 'Kitchen', 'Balcony', 'Other']
        if self.target_room_id == '' or self.base_room_id == '':
            self.door_type = 'Entry'
        elif 'BathRoom' in [ROOM_BUILD_TYPE[self.base_room_type], ROOM_BUILD_TYPE[self.target_room_type]]:
            self.door_type = 'Bathroom'
        elif 'Kitchen' in [ROOM_BUILD_TYPE[self.base_room_type], ROOM_BUILD_TYPE[self.target_room_type]]:
            self.door_type = 'Kitchen'
        elif 'Balcony' in [ROOM_BUILD_TYPE[self.base_room_type], ROOM_BUILD_TYPE[self.target_room_type]]:
            self.door_type = 'Balcony'
        else:
            self.door_type = 'Other'

        self.set_pos_and_rot()

    def build_mesh(self):
        if self.if_main_door:
            self.create_main_door(self.pts)

        if self.length < 1.2:
            self.create_swing_door(self.pts)
        # 双扇 1.2 - 1.8
        elif 1.2 <= self.length < 1.81:
            self.create_sliding_door(self.pts)
        # 三扇 1.8-2.4
        elif 1.8 <= self.length < 2.41:
            self.create_three_sliding_door(self.pts)
        # 四扇 2.4~
        else:
            self.create_four_sliding_door(self.pts)

    def create_main_door(self, door_pts):
        # 设置 self.jid = ''
        self.build_door(door_pts)

    def create_swing_door(self, door_pts):
        self.build_door(door_pts)
        pass

    def create_sliding_door(self, door_pts):
        self.build_door(door_pts)
        pass

    def create_three_sliding_door(self, door_pts):
        self.build_door(door_pts)
        pass

    def create_four_sliding_door(self, door_pts):
        self.build_door(door_pts)
        pass

    def build_door(self, door_pts):
        # 设置 self.jid = ''
        pocket_mesh = self.build_pocket_mesh(door_pts)
        ext_mesh, floor_mesh = self.build_extension_mesh(door_pts)
        mesh_type = 'Hole' if self.is_hole else 'Door'
        p_mesh_i = Mesh(mesh_type, self.uid + '_pocket_base')
        p_mesh_i.build_exists_mesh(pocket_mesh[0], pocket_mesh[1], pocket_mesh[2], pocket_mesh[3])

        e_mesh_i = Mesh('Pocket', self.uid + '_ext_base')
        e_mesh_i.build_exists_mesh(ext_mesh[0], ext_mesh[1], ext_mesh[2], ext_mesh[3])

        base_room_type = ROOM_BUILD_TYPE[self.base_room_type]
        target_room_type = ROOM_BUILD_TYPE[self.target_room_type]

        build_floor = False
        if target_room_type == '':
            build_floor = True
        elif 'LivingDiningRoom' == target_room_type or 'Other' == target_room_type:
            build_floor = True
        elif base_room_type == 'LivingDiningRoom' or base_room_type == 'Other':
            build_floor = False
        else:
            pocket_room_type = sorted([target_room_type, base_room_type])
            if base_room_type == pocket_room_type[0]:
                build_floor = True
            else:
                build_floor = False
        if self.target_room_type == '':
            build_floor = True
        if build_floor:
            f_mesh_i = Mesh(mesh_type, self.uid + '_floor_base')
            f_mesh_i.build_exists_mesh(floor_mesh[0], floor_mesh[1], floor_mesh[2], floor_mesh[3])
            floor = [f_mesh_i]
            self.mesh_info = {'pocket': [p_mesh_i], 'extension': [e_mesh_i], 'floor': floor}
        else:
            floor = []
            self.mesh_info = {'pocket': [p_mesh_i], 'extension': [e_mesh_i], 'floor': floor}

    def build_pocket_mesh(self, pts_org):

        base_vec = [1, 0]
        line_vec = np.array(pts_org[1]) - np.array(pts_org[0])
        if np.linalg.norm(line_vec) < 1e-3:
            r_matrix = np.mat([[1, 0], [0, 1.]])
        else:
            line_vec_norm = line_vec / np.linalg.norm(line_vec)
            sin = np.cross(base_vec, line_vec_norm)
            cos = np.dot(base_vec, line_vec_norm)
            # if line_vec_norm[1] < 0:
            #     sin = -sin
            # if line_vec_norm[0] < 0:
            #     cos = -cos
            r_matrix = np.mat([[cos, sin], [-sin, cos]])
        # r_matrix = np.mat([[1, 0], [-0, 1.]])
        pts = np.array((r_matrix * np.mat(np.array(pts_org) - np.array(pts_org[0])).transpose()).transpose())
        r_matrix_inv = np.linalg.inv(r_matrix)

        def rotate_y(pc, r):
            cosy = np.cos(r)
            siny = np.sin(r)
            Ms = np.array(
                [[cosy, 0, siny],
                 [0, 1, 0],
                 [-siny, 0, cosy]])
            pc = np.dot(pc, Ms)
            return pc

        if abs(pts[0][0] - pts[1][0]) < abs(pts[0][1] - pts[1][1]):
            base_axis = 0
        else:
            base_axis = 1

        r = 0
        self_offset = np.array((r_matrix * np.mat(self.face_offset).transpose()).transpose())[0]
        if self_offset[1] > 0.5 and base_axis == 1:
            r = 1
        elif self_offset[0] > 0.5 and base_axis == 0:
            r = 1

        if abs(pts[0][0] - pts[1][0]) < abs(pts[0][1] - pts[1][1]):
            base_axis = 0
            change_axis = 1

            if r == 1:
                start = pts[0][change_axis]
                end = pts[1][change_axis]
            else:
                start = pts[1][change_axis]
                end = pts[0][change_axis]
        else:
            base_axis = 1
            change_axis = 0
            if r == 1:
                start = pts[1][change_axis]
                end = pts[0][change_axis]
            else:
                start = pts[0][change_axis]
                end = pts[1][change_axis]

        base = (pts[0][base_axis] + pts[1][base_axis]) * 0.5
        door_base = self.height
        middle_p = [0.5 * (start + end), 0, base]
        # left_key_p = [0.9953, 2.198, -2.9097]
        # right_key_p = [2.1085, 2.198, -2.9097]
        # left_down_p = [0.9953, 0., -2.9097]
        # right_down_p = [2.1085, 0., -2.9097]

        v_0 = [-0.01026, 0.0, 0.0, -0.066, -0.066, -0.05156, 0.0, 0.0, 0.01026, 0.05156, 0.066, 0.066, -0.066, -0.066,
               0.0,
               0.0, 0.0, 0.0, 0.066, -0.066, 0.0, 0.0, 0.066, 0.066, -0.066, -0.066, -0.066, -0.066, -0.05156, -0.05156,
               -0.066, -0.066, -0.01026, -0.01026, -0.05156, -0.05156, 0.0, 0.0, -0.01026, -0.01026, 0.0, 0.0, 0.0, 0.0,
               0.066, -0.066, -0.066, 0.066, 0.05156, -0.05156, -0.066, 0.066, 0.01026, -0.01026, -0.05156, 0.05156,
               0.0,
               0.0, -0.01026, 0.01026, 0.0, 0.0, 0.0, 0.0, 0.066, 0.066, 0.066, 0.066, 0.05156, 0.05156, 0.066, 0.066,
               0.01026, 0.01026, 0.05156, 0.05156, 0.0, 0.0, 0.01026, 0.01026, 0.0, 0.0, 0.0, 0.0]
        v_0_first_flag = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1,
                          1, 1,
                          1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0,
                          0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for idx, value in enumerate(v_0):
            if v_0_first_flag[idx]:
                v_0[idx] += start
            else:
                v_0[idx] += end

        v_2 = [0.00924, 0.004, 0.0, 0.0, 0.01216, 0.0201, 0.0, 0.004, 0.00924, 0.0201, 0.01216, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01216, 0.01216, 0.0, 0.0, 0.0201, 0.0201, 0.01216, 0.01216,
               0.00924, 0.00924, 0.0201, 0.0201, 0.004, 0.004, 0.00924, 0.00924, 0.0, 0.0, 0.004, 0.004, 0.01216,
               0.01216,
               0.0, 0.0, 0.0201, 0.0201, 0.01216, 0.01216, 0.00924, 0.00924, 0.0201, 0.0201, 0.004, 0.004, 0.00924,
               0.00924,
               0.0, 0.0, 0.004, 0.004, 0.01216, 0.01216, 0.0, 0.0, 0.0201, 0.0201, 0.01216, 0.01216, 0.00924, 0.00924,
               0.0201, 0.0201, 0.004, 0.004, 0.00924, 0.00924, 0.0, 0.0, 0.004, 0.004]

        for idx, value in enumerate(v_2):
            if change_axis == 1:
                if r == 1:
                    v_2[idx] = v_2[idx] + base
                else:
                    v_2[idx] = v_2[idx] + base
            else:
                if r == 1:
                    v_2[idx] = v_2[idx] + base
                else:
                    v_2[idx] = v_2[idx] + base

        v_1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.066, 0.0, 0.0, 0.0, 0.0, 0.0, 0.066, 0.066,
               0.0, 0.0, 0.0, 0.066, 0.066, 0.0, 0.0, 0.066, 0.05156, 0.0, 0.0, 0.066, 0.01026, 0.0, 0.0, 0.05156, 0.0,
               0.0,
               0.0, 0.01026, 0.0, 0.0, 0.0, 0.0, 0.066, 0.066, 0.066, 0.066, 0.05156, 0.05156, 0.066, 0.066, 0.01026,
               0.01026, 0.05156, 0.05156, 0.0, 0.0, 0.01026, 0.01026, 0.0, 0.0, 0.0, 0.0, 0.0, 0.066, 0.066, 0.0, 0.0,
               0.05156, 0.066, 0.0, 0.0, 0.01026, 0.05156, 0.0, 0.0, 0.0, 0.01026, 0.0, 0.0, 0.0, 0.0, 0.0]
        v_1_door_flag = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1,
                         1,
                         0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
                         1,
                         1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]

        for idx, value in enumerate(v_1):
            if v_1_door_flag[idx]:
                v_1[idx] += door_base

        v = []
        n_0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0,
               0.0, 0.0, -1.0, -1.0, -1.0, -1.0, -0.481808, -0.481808, -0.481808, -0.481808, 0.25436, 0.25436, 0.25436,
               0.25436, 0.454479, 0.454479, 0.454479, 0.454479, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.481808, 0.481808,
               0.481808,
               0.481808, -0.25436, -0.25436, -0.25436, -0.25436, -0.454479, -0.454479, -0.454479, -0.454479, -1.0, -1.0,
               -1.0, -1.0]

        n_1 = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0,
               0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.481808, 0.481808, 0.481808, 0.481808, -0.25436, -0.25436, -0.25436,
               -0.25436, -0.454479, -0.454479, -0.454479, -0.454479, -1.0, -1.0, -1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        n_2 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0,
               -1.0,
               -1.0, -1.0, -1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.876277, 0.876277, 0.876277, 0.876277, 0.96711, 0.96711,
               0.96711, 0.96711, 0.890758, 0.890758, 0.890758, 0.890758, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.876277,
               0.876277, 0.876277, 0.876277, 0.96711, 0.96711, 0.96711, 0.96711, 0.890758, 0.890758, 0.890758, 0.890758,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.876277, 0.876277, 0.876277, 0.876277, 0.96711, 0.96711,
               0.96711,
               0.96711, 0.890758, 0.890758, 0.890758, 0.890758, 0.0, 0.0, 0.0, 0.0]

        face = [4, 3, 5, 2, 5, 3, 0, 5, 2, 1, 0, 2, 7, 6, 8, 11, 8, 6, 9, 8, 11, 10, 9, 11, 14, 13, 15, 12, 15, 13, 17,
                16,
                18, 19, 18, 16, 22, 21, 23, 20, 23, 21, 26, 25, 27, 24, 27, 25, 30, 29, 31, 28, 31, 29, 34, 33, 35, 32,
                35,
                33, 38, 37, 39, 36, 39, 37, 42, 41, 43, 40, 43, 41, 46, 45, 47, 44, 47, 45, 50, 49, 51, 48, 51, 49, 54,
                53,
                55, 52, 55, 53, 58, 57, 59, 56, 59, 57, 61, 60, 62, 63, 62, 60, 66, 65, 67, 64, 67, 65, 70, 69, 71, 68,
                71,
                69, 74, 73, 75, 72, 75, 73, 78, 77, 79, 76, 79, 77, 82, 81, 83, 80, 83, 81]

        # v_0 =[0.98504, 0.9953, 0.9953, 0.9293, 0.9293, 0.94374, 2.1085, 2.1085, 2.11876, 2.16006, 2.1745, 2.1745, 0.9293, 0.9293, 0.9953, 0.9953, 0.9953, 2.1085, 2.1745, 0.9293, 2.1085, 2.1085, 2.1745, 2.1745, 0.9293, 0.9293, 0.9293, 0.9293, 0.94374, 0.94374, 0.9293, 0.9293, 0.98504, 0.98504, 0.94374, 0.94374, 0.9953, 0.9953, 0.98504, 0.98504, 0.9953, 0.9953, 0.9953, 0.9953, 2.1745, 0.9293, 0.9293, 2.1745, 2.16006, 0.94374, 0.9293, 2.1745, 2.11876, 0.98504, 0.94374, 2.16006, 2.1085, 0.9953, 0.98504, 2.11876, 2.1085, 0.9953, 0.9953, 2.1085, 2.1745, 2.1745, 2.1745, 2.1745, 2.16006, 2.16006, 2.1745, 2.1745, 2.11876, 2.11876, 2.16006, 2.16006, 2.1085, 2.1085, 2.11876, 2.11876, 2.1085, 2.1085, 2.1085, 2.1085]
        # v_1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.264, 0.0, 0.0, 2.198, 2.198, 2.198, 2.264, 2.264, 2.198, 0.0, 0.0, 2.264, 2.264, 0.0, 0.0, 2.264, 2.24956, 0.0, 0.0, 2.264, 2.20826, 0.0, 0.0, 2.24956, 2.198, 0.0, 0.0, 2.20826, 2.198, 0.0, 0.0, 2.198, 2.264, 2.264, 2.264, 2.264, 2.24956, 2.24956, 2.264, 2.264, 2.20826, 2.20826, 2.24956, 2.24956, 2.198, 2.198, 2.20826, 2.20826, 2.198, 2.198, 2.198, 2.198, 0.0, 2.264, 2.264, 0.0, 0.0, 2.24956, 2.264, 0.0, 0.0, 2.20826, 2.24956, 0.0, 0.0, 2.198, 2.20826, 0.0, 0.0, 2.198, 2.198, 0.0]
        # v_2 = [-2.90046, -2.9057, -2.9097, -2.9097, -2.89754, -2.8896, -2.9097, -2.9057, -2.90046, -2.8896, -2.89754, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.9097, -2.89754, -2.89754, -2.9097, -2.9097, -2.8896, -2.8896, -2.89754, -2.89754, -2.90046, -2.90046, -2.8896, -2.8896, -2.9057, -2.9057, -2.90046, -2.90046, -2.9097, -2.9097, -2.9057, -2.9057, -2.89754, -2.89754, -2.9097, -2.9097, -2.8896, -2.8896, -2.89754, -2.89754, -2.90046, -2.90046, -2.8896, -2.8896, -2.9057, -2.9057, -2.90046, -2.90046, -2.9097, -2.9097, -2.9057, -2.9057, -2.89754, -2.89754, -2.9097, -2.9097, -2.8896, -2.8896, -2.89754, -2.89754, -2.90046, -2.90046, -2.8896, -2.8896, -2.9057, -2.9057, -2.90046, -2.90046, -2.9097, -2.9097, -2.9057, -2.9057]

        uv = []
        for i in range(len(v_0)):
            uv.append(1 * v_1[i])
            uv.append(1 * v_0[i])

        n = np.array([n_0, n_1, n_2]).transpose()
        v = np.array([v_0, v_1, v_2]).transpose() - np.array(middle_p)
        n = rotate_y(n, -np.pi)
        if change_axis == 1:
            if r == 1:
                # print('a')
                v = rotate_y(v, -np.pi / 2.)
                n = rotate_y(n, -np.pi / 2.)
            else:
                # print('b')
                v = rotate_y(v, np.pi / 2.)
                n = rotate_y(n, np.pi / 2.)
        else:
            if r == 1:
                pass
                # v = rotate_y(v, np.pi)
                # n = rotate_y(n, np.pi)
            else:
                # print('d')
                v = rotate_y(v, np.pi)
                n = rotate_y(n, np.pi)

        v += np.array([(pts[0][0] + pts[1][0]) / 2., 0., (pts[0][1] + pts[1][1]) / 2.])
        n = n.reshape(-1).tolist()
        v = v.reshape(-1).tolist()

        v = np.reshape(v, [-1, 3])
        v[:, [0, 2]] = np.array((r_matrix_inv * np.mat(v[:, [0, 2]]).transpose()).transpose()) + np.array(pts_org[0])
        v = np.reshape(v, [-1]).tolist()

        n = np.reshape(n, [-1, 3])
        n[:, [0, 2]] = np.array((r_matrix_inv * np.mat(n[:, [0, 2]]).transpose()).transpose())
        n = np.reshape(n, [-1]).tolist()
        return [v, n, uv, face]

    def build_extension_mesh(self, pts_org, top=2.0):
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

        offset = self.depth
        self_offset = np.array((r_matrix * np.mat(self.face_offset).transpose()).transpose())[0]
        if self_offset[1] > 0.5 and base_axis == 1:
            offset = -self.depth
        elif self_offset[0] > 0.5 and base_axis == 0:
            offset = -self.depth

        height = 0.0
        start = pts[0][change_axis]
        end = pts[1][change_axis]
        base = pts[0][base_axis]

        v_0 = [start, start, start, start, end, end,
               end, end, end, start, start, end,
               start, end, end, start]
        v_1 = [top, top, height, height, top, top, height, height, top, top, top, top, height, height, height,
               height]
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

        uv_floor = uv
        v = np.reshape(v, [-1, 3])
        v[:, [0, 2]] = np.array((r_matrix_inv * np.mat(v[:, [0, 2]]).transpose()).transpose()) + np.array(pts_org[0])
        v = np.reshape(v, [-1]).tolist()

        n = np.array(n, np.float)
        n = np.reshape(n, [-1, 3])
        n[:, [0, 2]] = np.array((r_matrix_inv * np.mat(n[:, [0, 2]]).transpose()).transpose())
        n = np.reshape(n, [-1]).tolist()

        return [v, n, uv, face[:-6]], [v, n, uv_floor, face[-6:]]

    def set_pos_and_rot(self):
        mid_p = [0.5 * (self.pts[0][0] + self.pts[1][0]), 0.0,
                 0.5 * (self.pts[0][1] + self.pts[1][1])]
        self.pos = [mid_p[0] - self.depth * 0.5 * self.face_offset[0], 0.0, mid_p[2] - self.depth * 0.5 * self.face_offset[1]]
        ang = np.arcsin(-self.face_offset[1])
        if self.face_offset[1] < -0.001:
            ang = np.pi - ang
        ang += np.pi / 2
        self.rotation = [0.0, np.sin(ang/2.), 0.0, np.cos(ang/2.)]

    def build_material(self, material):
        main_mat = material['main']
        floor_mat = material['floor']

        for name, meshes in self.mesh_info.items():
            if name == 'floor':
                mat = floor_mat
            else:
                mat = main_mat
            for mesh in meshes:
                mesh.mat['jid'] = mat['jid']
                mesh.mat['texture'] = mat['texture']
                mesh.mat['color'] = mat['color']
                mesh.mat['colorMode'] = mat['colorMode']
                mesh.build_uv(np.array(mat['uv_ratio']))
