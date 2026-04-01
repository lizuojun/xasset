from .recon_mesh import Mesh


class BaseBoardBuild(object):
    def __init__(self, baseboard):
        self.start_pt, self.end_pt = baseboard['layout_pts']
        self.offset = baseboard['normal']
        self.connect_type = baseboard['connect_type']
        self.uid = baseboard['name']

        self.mesh_info = []

    def build_mesh(self):
        v, n, uv, face = self.get_old_style_baseboard(self.start_pt,
                                                      self.end_pt,
                                                      self.offset,
                                                      self.connect_type)
        mesh = Mesh('BaseBoard', self.uid)
        mesh.build_exists_mesh(v, n, uv, face)
        self.mesh_info.append(mesh)

    # 原始测试版本 不支持斜墙
    def get_old_style_baseboard(self, start_pos, end_pos, line_normal, connect_type):
        pts_org = [start_pos, end_pos]
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
        start_pos, end_pos = pts[0], pts[1]

        # 踢脚线模版mesh问题 需要起始颠倒
        first_door_flag = connect_type[1]
        last_door_flag = connect_type[0]
        door_ext = 0.06
        wall_ext = 0.016

        if abs(start_pos[0] - end_pos[0]) < abs(start_pos[1] - end_pos[1]):
            base_axis = 0
            change_axis = 1
        else:
            base_axis = 1
            change_axis = 0

        offset = -0.016
        line_normal = np.array((r_matrix * np.mat(line_normal).transpose()).transpose())[0]
        if line_normal[1] > 0.5 and base_axis == 1:
            offset = 0.016
        elif line_normal[0] > 0.5 and base_axis == 0:
            offset = 0.016

        start = end_pos[change_axis]
        end = start_pos[change_axis]
        base = start_pos[base_axis]

        first_pos = start
        last_pos = end
        if first_door_flag == 2:
            if first_pos < last_pos:
                first_pos = start + door_ext
            else:
                first_pos = start - door_ext
        elif first_door_flag == 1:
            if first_pos < last_pos:
                first_pos = start - wall_ext
            else:
                first_pos = start + wall_ext

        if last_door_flag == 2:
            if first_pos < last_pos:
                last_pos = end - door_ext
            else:
                last_pos = end + door_ext
        elif last_door_flag == 1:
            if first_pos < last_pos:
                last_pos = end + wall_ext
            else:
                last_pos = end - wall_ext

        v_0 = [first_pos, last_pos, last_pos, first_pos, start, end, last_pos, first_pos,
               first_pos, last_pos, end, start, start, end, end, start]
        v_2 = [base + offset, base + offset, base + offset, base + offset, base, base, base + offset, base + offset,
               base + offset, base + offset, base, base, base, base, base, base]
        v_1 = [0.07, 0.07, 0.0, 0.0, 0.07, 0.07, 0.07, 0.07, 0.0, 0.0, 0.0, 0.0, 0.07, 0.07, 0.0, 0.0]
        v = []
        n_0 = [0.0] * 16
        n_1 = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 0., 0., 0., 0.]
        n_2 = [1.0, 1.0, 1.0, 1.0, 0., 0., 0., 0., 0., 0., 0., 0., -1, -1, -1, -1]
        n = []
        if change_axis == 0:
            for i in range(len(v_0)):
                v.append(v_0[i])
                v.append(v_1[i])
                v.append(v_2[i])
                if offset > 0.:
                    n.append(n_0[i])
                    n.append(n_1[i])
                    n.append(-n_2[i])
                else:
                    n.append(n_0[i])
                    n.append(n_1[i])
                    n.append(-n_2[i])
        else:
            for i in range(len(v_0)):
                v.append(v_2[i])
                v.append(v_1[i])
                v.append(v_0[i])
                if offset > 0.:
                    n.append(-n_2[i])
                    n.append(n_1[i])
                    n.append(n_0[i])
                else:
                    n.append(-n_2[i])
                    n.append(n_1[i])
                    n.append(n_0[i])

        uv = []
        for i in range(len(v_0)):
            uv.append(1 * v_1[i])
            uv.append(1 * v_0[i])

        face = [2, 1, 3, 0, 3, 1, 5, 4, 6, 7, 6, 4]
        face += [10, 9, 11, 8, 11, 9, 15, 13, 14, 13, 15, 12]

        v = np.reshape(v, [-1, 3])
        v[:, [0, 2]] = np.array((r_matrix_inv * np.mat(v[:, [0, 2]]).transpose()).transpose()) + np.array(pts_org[0])
        v = np.reshape(v, [-1]).tolist()

        n = np.array(n, np.float)
        n = np.reshape(n, [-1, 3])
        n[:, [0, 2]] = np.array((r_matrix_inv * np.mat(n[:, [0, 2]]).transpose()).transpose())
        n = np.reshape(n, [-1]).tolist()
        return v, n, uv, face

    def build_material(self, material):
        main_mat = material['main']
        for mesh in self.mesh_info:
            mesh.mat['jid'] = main_mat['jid']
            mesh.mat['texture'] = main_mat['texture']
            mesh.mat['color'] = main_mat['color']
            mesh.mat['colorMode'] = main_mat['colorMode']
            mesh.build_uv(np.array(main_mat['uv_ratio']))

import numpy as np
import trimesh
def get_rotation(v):
    alpha = np.arctan2(v[0], v[2])
    beta = -np.arcsin(v[1])
    r_y = np.mat([[np.cos(alpha), 0, np.sin(alpha)],
                  [0, 1, 0],
                  [-np.sin(alpha), 0, np.cos(alpha)]])
    r_z = np.mat([[np.cos(beta), -np.sin(beta), 0],
                  [np.sin(beta), np.cos(beta), 0],
                  [0, 0, 1]])
    r = r_y * r_z
    return r


def intersection_line_plane(p0, p1, p_co, p_no):
    u = p1 - p0
    dot = np.dot(p_no, u)

    if abs(dot) > 1e-6:
        # The factor of the point between p0 -> p1 (0 - 1)
        # if 'fac' is between (0 - 1) the point intersects with the segment.
        # Otherwise:
        #  < 0.0: behind p0.
        #  > 1.0: infront of p1.
        w = p0 - p_co
        fac = -np.dot(p_no, w) / dot
        u = u * fac
        return p0 + u
    else:
        # The segment is parallel to plane.
        return None


def construct_section_face(pts):
    if len(pts) == 0:
        return []
    newpts = pts.copy()

    faces = []
    index = list(range(len(pts)))
    while len(newpts) >= 3:
        p, pts_list = Mesh.ear_cut_triangulation(newpts, 2)

        faces.append([index[(p - 1) % len(index)], index[p % len(index)], index[(p + 1) % len(index)]])
        newpts.pop(p)
        index.pop(p)
    return faces


def construct_mesh_with_stretch(section_points, skeleton_points):
    section_points = np.array(section_points)
    skeleton_points = np.array(skeleton_points)
    # section_points_3d = section_points - np.mean(section_points, axis=0)
    section_points_3d = np.concatenate([section_points, np.zeros([len(section_points), 1])],
                                       axis=-1)
    verts_start = []
    verts_end = []
    faces = []
    section_p_num = len(section_points)
    skeleton_closed = (skeleton_points[-1, :] - skeleton_points[0, :] < 1e-5).all()
    if skeleton_closed:
        valid_skeleton_points_num = len(skeleton_points) - 1
    else:
        valid_skeleton_points_num = len(skeleton_points)
    for i in range(len(skeleton_points) - 1):
        v = skeleton_points[i + 1] - skeleton_points[i]
        r = get_rotation(v)
        section_points_stretch = np.array(r * section_points_3d.transpose()).transpose()
        for j in range(section_p_num):
            verts_start.append(section_points_stretch[j] + skeleton_points[i])
            verts_end.append(section_points_stretch[j] + skeleton_points[i + 1])
            faces.append([i * section_p_num + j, i * section_p_num + (j + 1) % section_p_num,
                          (i + 1) % valid_skeleton_points_num * section_p_num + j])
            faces.append([(i + 1) % valid_skeleton_points_num * section_p_num + j,
                          i * section_p_num + (j + 1) % section_p_num,
                          (i + 1) % valid_skeleton_points_num * section_p_num + (j + 1) % section_p_num])

    # repair face intersection
    verts = verts_start.copy()
    if not skeleton_closed:
        for j in range(section_p_num):
            verts.append(verts_end[(valid_skeleton_points_num - 2) * section_p_num + j])
        # section face
        added_face = construct_section_face(list(section_points_3d))
        faces = faces + added_face
        added_face = [[j + len(verts) - len(section_points) for j in i] for i in added_face]

        faces = faces + added_face

    if len(skeleton_points) > 2:
        for i in range(valid_skeleton_points_num):

            if i == 0 and not skeleton_closed:
                continue
            if i == valid_skeleton_points_num - 1 and not skeleton_closed:
                break
            p0_ind = (i - 1) % valid_skeleton_points_num
            p1_ind = i % valid_skeleton_points_num
            p2_ind = (i + 1) % valid_skeleton_points_num
            p0 = skeleton_points[p0_ind]
            p1 = skeleton_points[p1_ind]
            p2 = skeleton_points[p2_ind]

            p_co = p1

            line_mean = ((p0 - p1) / np.linalg.norm(p0 - p1) + (p2 - p1) / np.linalg.norm(p2 - p1)) / 2.
            line_cross = np.cross(p0 - p1, p2 - p1)
            p_no = np.cross(line_mean, line_cross)

            for j in range(section_p_num):
                p0s = verts_start[i * section_p_num + j]
                p1s = verts_end[i * section_p_num + j]
                repaired_p1s = intersection_line_plane(p0s, p1s, p_co, p_no)
                verts[i * section_p_num + j] = repaired_p1s

    m = trimesh.Trimesh(vertices=verts, faces=faces)
    # m.show()
    v_norms = m.vertex_normals
    uv = np.zeros([len(verts), 2])
    return np.array(verts), v_norms, uv, np.array(faces)