# -*- coding: utf-8 -*-
"""
@Author: wpy
@Date: 2020-07-15
@Description:根据polygon多边形 生成mesh数据
"""
import copy
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

from ..Base.math_util import map_uv_from_3d, map_uv


class Mesh(object):
    def __init__(self, mesh_type, mesh_uid):
        self.u_dir = [1, 0, 0]
        self.uv = []
        self.uid = mesh_uid
        self.mesh_type = mesh_type
        self.xyz = []
        self.normals = []
        self.faces = []
        self.contour = []
        self.uv_norm_pt = None
        self.area = None
        self.ceramic = False
        self.tile_count = 0

        self.face_normal = [0.0, 1.0, 0.0]
        self.mat = {
            "uid": mesh_uid + '_material',
            "jid": "",
            "texture": "",
            "normaltexture": "",
            "color": [255, 255, 255, 255],
            "colorMode": 'color',
            "contentType": [
                "material",
                "paint"
            ],
            "UVTransform": [
                1, 0, 0,
                0, 1, 0,
                0, 0, 1
            ]

        }

    def build_exists_mesh(self, v, n, uv, f, contour=[], uv_norm_pt=None):
        self.uv = uv
        self.xyz, self.normals, self.faces = v, n, f
        self.contour = contour
        self.uv_norm_pt = uv_norm_pt
        self.face_normal = n[:3]
        self.area = 0.
        face_pts = np.reshape(np.reshape(self.xyz, [-1, 3])[self.faces], [-1, 3, 3])
        for face in face_pts:
            self.area += 0.5 * np.linalg.norm(np.cross(face[0] - face[1], face[0] - face[2]))

    # poly为三维多边形点集合， normal为该多边形法向量
    def build_mesh(self, poly, normal):
        if len(poly) < 3:
            return [], [], []
        self.face_normal = normal
        xyz, normals, faces = [], [], []
        pt_idx = 0
        temp_pts = []
        for pt_ind in range(len(poly)):
            dis = np.linalg.norm(np.array(poly[pt_ind]) - poly[(pt_ind + 1) % len(poly)])
            if dis < 1e-3:
                continue
            temp_pts.append(poly[pt_ind])
        self.contour = copy.deepcopy(temp_pts)
        if len(temp_pts) < 3:
            return [], [], []
        temp_pts = self.check_poly_clock(temp_pts, normal)
        # xyz build
        self.area = 0.
        while len(temp_pts) >= 3:
            p, pts_list = self.ear_cut_triangulation(temp_pts, normal)
            if p == -1:
                break
            for i in pts_list:
                xyz += i
                normals += normal
            for i in range(3):
                faces.append(pt_idx + i)
            pt_idx += 3
            temp_pts.pop(p)
            self.area += 0.5 * np.linalg.norm(np.cross(np.array(pts_list[0]) - pts_list[1], np.array(pts_list[0]) - pts_list[2]))
        self.xyz, self.normals, self.faces = xyz, normals, faces
        if len(xyz) > 0:
            self.uv_norm_pt = (0.5 * (np.min(np.reshape(xyz, [-1, 3]), axis=0) + np.max(np.reshape(xyz, [-1, 3]), axis=0))).tolist()
        return xyz, normals, faces

    @staticmethod
    def ear_cut_triangulation(temp_pts, normal):
        num_p = len(temp_pts)
        for p in range(num_p):
            one = np.array(temp_pts[p]) - np.array(temp_pts[(p - 1) % num_p])
            two = np.array(temp_pts[(p + 1) % num_p]) - np.array(temp_pts[p])
            crossRes = np.cross(one, two)

            if np.sum(crossRes * normal) <= 0:
                continue

            # 凸点
            tri_prev = temp_pts[(p - 1) % num_p]
            tri_next = temp_pts[(p + 1) % num_p]
            tri_now = temp_pts[p]
            # 判断 如果出现有别的点在该三角形中，则该点无法切割
            cut_yes = True
            for check_p in range(num_p):
                if check_p in [p, (p - 1) % num_p, (p + 1) % num_p]:
                    continue
                if Mesh.in_triangle(temp_pts[check_p], tri_prev, tri_now, tri_next):
                    cut_yes = False
                    break

            # 该点可以切割
            if cut_yes:
                return p, [tri_prev, tri_now, tri_next]

            continue

        return -1, []

    # 重心法
    # PA = u * CA + v * BA
    @staticmethod
    def in_triangle(p, a, b, c):
        v0 = np.array(c) - np.array(a)
        v1 = np.array(b) - np.array(a)
        v2 = np.array(p) - np.array(a)

        dot00 = np.dot(v0, v0)
        dot01 = np.dot(v0, v1)
        dot02 = np.dot(v0, v2)
        dot11 = np.dot(v1, v1)
        dot12 = np.dot(v1, v2)

        invert = 1 / (dot00 * dot11 - dot01 * dot01 + 1e-5)
        u = (dot11 * dot02 - dot01 * dot12) * invert
        if u < 0 or u > 1:
            return False
        v = (dot00 * dot12 - dot01 * dot02) * invert
        if v < 0 or v > 1:
            return False

        return u + v <= 1

    def set_u_dir(self, u_dir):
        self.u_dir = copy.deepcopy(u_dir)

    def set_face_normal(self, normal):
        self.face_normal = copy.deepcopy(normal)

    def set_uv_norm_pt(self, uv_norm_pt):
        self.uv_norm_pt = copy.deepcopy(uv_norm_pt)

    def build_uv(self, uv_ratio, mat_info=None):
        if len(self.xyz) == 0:
            return [], np.array([0, 0])
        else:
            normed_xyz = np.array(self.xyz).reshape(-1, 3)
            if self.uv_norm_pt is None:
                normed_xyz = normed_xyz - np.mean(normed_xyz, axis=0)
            else:
                normed_xyz = normed_xyz - self.uv_norm_pt
            self.uv = map_uv_from_3d(normed_xyz, self.face_normal, self.u_dir)
            self.uv = np.reshape(np.reshape(self.uv, [-1, 2]) * np.sign([uv_ratio[0], uv_ratio[2]]), [-1]).tolist()
            self.mat['UVTransform'] = [
                abs(uv_ratio[0]), 0, 0.,
                0, abs(uv_ratio[2]), 0.,
                uv_ratio[1] + 0.5, uv_ratio[3] + 0.5, 1
            ]
            # u_scale=0.1
            # v_scale=0.1
            # u_translation = 0.5
            # v_translation = 0.5
            # self.mat['UVTransform'] = [
            #     u_scale, 0, u_translation,
            #     0, v_scale, v_translation,
            #     0, 0, 1
            # ]
            if mat_info:
                self.mat = copy.deepcopy(mat_info)
                self.mat['jid'] = mat_info['jid']
                self.mat['texture'] = mat_info['texture']
                self.mat['normaltexture'] = mat_info['normaltexture']
                self.mat['color'] = copy.deepcopy(mat_info['color'])
                self.mat['contentType'] = copy.deepcopy(mat_info['contentType'])
        return self.uv

    # 三维平面点 顺序判断
    def check_poly_clock(self, poly_pts, normal):
        poly = np.array(poly_pts)
        axis = np.argmax(np.max(poly, axis=0)-np.min(poly, axis=0))
        convex_p_idx = np.argmax(poly, axis=0)[axis]
        convex_prev_idx = (convex_p_idx - 1) % len(poly)
        convex_next_idx = (convex_p_idx + 1) % len(poly)
        one = np.array(poly_pts[convex_p_idx]) - np.array(poly_pts[convex_prev_idx])
        two = np.array(poly_pts[convex_next_idx]) - np.array(poly_pts[convex_prev_idx])
        crossRes = np.cross(one, two)
        if np.sum(crossRes * normal) <= 0:
            poly_pts.reverse()
        return poly_pts

    def ceramic_layout(self, mat, gap_width=0.005, texture_list=[]):
        if 'seam_width' in mat:
            gap_width = mat['seam_width']
        gap_width += 1e-5
        floor_height = 0.002
        uv_ratio = mat['uv_ratio']
        ceramic_width = max(1. / uv_ratio[0], 0.1)
        ceramic_height = max(1. / uv_ratio[2], 0.1)

        if 'pave' in mat and mat['pave'] in ['pingpu', 'renzipu', 'gongzipu', 'yugupu']:
            pave = mat['pave']
        else:
            if max(ceramic_height, ceramic_width) / min(ceramic_height, ceramic_width) > 2.1:
                pave = 'gongzipu'
            else:
                pave = 'pingpu'
        contour = self.contour
        contour.append(contour[0])
        mapped_contour, r = map_uv(contour, self.u_dir, self.face_normal)
        mapped_y = np.mean(mapped_contour[:, 1])

        size = np.max(mapped_contour, axis=0) - np.min(mapped_contour, axis=0)
        start = np.min(mapped_contour, axis=0)
        tile_meshes = []

        polygon_contour = Polygon(mapped_contour[:, [0, 2]])
        if not polygon_contour.is_valid:
            polygon_contour = polygon_contour.buffer(0)
        area = polygon_contour.area
        centroid = [polygon_contour.centroid.x, polygon_contour.centroid.y]

        all_tiles, all_tiles_rot, all_tiles_center = self.ceramic_pave(start, size,
                                                                       (ceramic_width, ceramic_height),
                                                                       gap_width,
                                                                       pave)

        coords = []
        coords_center = []
        coords_rot = []
        for i, tiles in enumerate(all_tiles):
            p = Polygon(tiles[0])
            res = polygon_contour.intersection(p)
            if res.is_empty:
                continue
            if isinstance(res, Polygon):
                coords += [np.asarray(res.exterior.coords)]
                coords_center.append(all_tiles_center[i])
                coords_rot.append(all_tiles_rot[i])
            elif isinstance(res, MultiPolygon):
                coord = list(res.geoms)
                coords += [np.asarray(i.exterior.coords) for i in coord if isinstance(i, Polygon)]
                coords_center += [all_tiles_center[i]] * len(coord)
                coords_rot += [all_tiles_rot[i]] * len(coord)

        # mulPoly = MultiPolygon(all_tiles)
        # intersection = polygon_contour.intersection(mulPoly)
        #
        # if isinstance(intersection, Polygon):
        #     coords = [np.asarray(intersection.exterior.coords)]
        # else:
        #     coords = list(intersection.geoms)
        #     coords = [np.asarray(i.exterior.coords) for i in coords if isinstance(i, Polygon)]

        # from matplotlib import pyplot as plt
        # plt.figure()
        # plt.axis('equal')
        # # for rect in all_tiles:
        # #     tmp = list(rect[0])
        # #     tmp.append(tmp[0])
        # #     plt.plot(np.array(tmp)[:, 0], np.array(tmp)[:, 1], color='blue', linewidth=2)
        # plt.plot(mapped_contour[:, 0], mapped_contour[:, 2], color='green')
        #
        # for c in coords:
        #     plt.plot(c[:, 0], c[:, 1], color='red')
        # plt.show()
        tile_mesh_template = Mesh(self.mesh_type, '%s_%d' % (self.uid, len(tile_meshes)))
        tile_mesh_template.mat['jid'] = mat['jid']
        tile_mesh_template.mat['texture'] = mat['texture']
        tile_mesh_template.mat['color'] = mat['color']
        tile_mesh_template.mat['colorMode'] = mat['colorMode']
        tile_mesh_template.mat['matType'] = 'ceramic'

        n = self.face_normal * 4
        f = [0, 1, 2, 2, 3, 0]

        if uv_ratio[0] == uv_ratio[2]:
            inds = np.random.randint(2, size=len(coords))
        else:
            inds = [0] * len(coords)
        inds = [0] * len(coords)
        uv_ratio_rand_ind = np.random.choice([1, 1], size=len(coords) * 2)
        centroid = np.dot([centroid[0], mapped_y + 0.1, centroid[1]], r).tolist()

        for i, coord in enumerate(coords):
            if coord.size == 0:
                continue
            # tile_mesh = Mesh(mesh.mesh_type, '%s_%d' % (mesh.uid, len(tile_meshes)))
            coord = coord[:-1, :]
            tile_mesh = copy.deepcopy(tile_mesh_template)
            tile_mesh.uid = '%s_%d' % (self.uid, len(tile_meshes))
            tile_mesh.mat['uid'] = tile_mesh.uid + '_material'

            # coord_center = 0.5 * (np.min(coord, axis=0) + np.max(coord, axis=0))
            # min_center = [(coord_center[0] - start[0]) // (ceramic_width + gap_width) * (ceramic_width + gap_width) + 0.5 * ceramic_width + start[0],
            #           (coord_center[1] - start[2]) // (ceramic_height + gap_width) * (ceramic_height + gap_width) + 0.5 * ceramic_height + start[2]]
            min_center = coords_center[i]
            # min_dis = 1e5
            # min_center = coord_center
            # for tc in tile_center_list:
            #     dis = np.linalg.norm(coord_center - tc)
            #     if dis < min_dis:
            #         min_dis = dis
            #         min_center = tc
            norm_center_pt = np.dot([min_center[0], floor_height + mapped_y, min_center[1]], r).tolist()
            rot_back_coords = np.dot(
                np.stack([coord[:, 0], floor_height * np.ones_like(coord[:, 0]) + mapped_y, coord[:, 1]],
                         axis=-1), r)

            # if len(rot_back_coords) == 4:
            #     v = rot_back_coords.reshape([-1]).tolist()
            #     tile_mesh.build_exists_mesh(v, n, None, f)
            # else:
            tile_mesh.build_mesh(rot_back_coords.tolist(), self.face_normal)
            tile_mesh.set_uv_norm_pt(norm_center_pt)
            uv_ratio_rand = [uv_ratio_rand_ind[i * 2] * uv_ratio[0], uv_ratio[1],
                             uv_ratio_rand_ind[i * 2 + 1] * uv_ratio[2], uv_ratio[3]]
            # if len(rot_back_coords) == 4:
            #     coord = coord - min_center
            #     coord = np.stack([coord[:, inds[i]], coord[:, 1 - inds[i]]], axis=-1)
            #     tile_mesh.uv = (coord * np.array([uv_ratio_rand[0], uv_ratio_rand[2]]) + np.array(
            #         [uv_ratio_rand[1] + 0.5, uv_ratio_rand[3] + 0.5])).reshape([-1]).tolist()
            # else:
            tile_mesh.build_uv(uv_ratio_rand)
            if len(rot_back_coords) == 4:
                tile_mesh.uv = np.reshape(np.reshape(tile_mesh.uv, [-1, 2])[:, [inds[i], 1-inds[i]]], [-1]).tolist()
            tile_meshes.append([tile_mesh, coords_rot[i]])
        # 合并mesh
        # 一石多面
        ref_list = copy.deepcopy(texture_list)
        ref_list.append((mat['jid'], mat['texture']))
        np.random.seed(19941115)
        np.random.shuffle(tile_meshes)
        res = []
        for i in range(len(ref_list)):
            combined_tile_mesh = copy.deepcopy(tile_mesh_template)
            vertices_dict = {}
            faces_dict = {}
            uv_dict = {}
            normals_dict = {}

            inter = len(tile_meshes) // len(ref_list) + 1
            start = i * inter
            end = (i + 1) * inter
            if end > len(tile_meshes):
                end = len(tile_meshes)
            if start >= len(tile_meshes):
                break
            for mesh, rot in tile_meshes[start:end]:
                if rot not in vertices_dict:
                    vertices_dict[rot] = []
                    faces_dict[rot] = []
                    uv_dict[rot] = []
                    normals_dict[rot] = []
                vertices = vertices_dict[rot]
                faces = faces_dict[rot]
                uv = uv_dict[rot]
                normals = normals_dict[rot]
                assert len(vertices) % 3 == 0
                base = len(vertices) // 3

                vertices += mesh.xyz
                face = (np.array(mesh.faces) + base).tolist()
                faces += face
                uv += mesh.uv
                normals += mesh.normals

            for rot in vertices_dict:
                vertices = vertices_dict[rot]
                faces = faces_dict[rot]
                uv = uv_dict[rot]
                normals = normals_dict[rot]
                combined_tile_mesh.build_exists_mesh(vertices, normals, uv, faces)
                combined_tile_mesh.mat['texture'] = ref_list[i][1]
                combined_tile_mesh.mat['jid'] = ref_list[i][0]
                rot_ = rot / 180. * np.pi
                combined_tile_mesh.mat['UVTransform'] = [
                    abs(uv_ratio[0]) * np.cos(rot_), abs(uv_ratio[2]) * np.sin(rot_), 0.,
                    abs(uv_ratio[0]) * (-np.sin(rot_)), abs(uv_ratio[2]) * np.cos(rot_), 0.,
                    uv_ratio[1] + 0.5, uv_ratio[3] + 0.5, 1
                ]
                # combined_tile_mesh.uid = '%s_%d_%d' % (self.uid, i, rot)
                combined_tile_mesh.uid = '%s_%d_%d' % (self.uid, i, rot)
                combined_tile_mesh.mat['uid'] = combined_tile_mesh.uid + '_material'
                combined_tile_mesh.ceramic = True
                combined_tile_mesh.tile_count = len(tile_meshes[start:end])
                res.append(copy.deepcopy(combined_tile_mesh))

        return res, area, centroid

    def ceramic_pave(self, floor_start, floor_size, ceramic_size, gap_width, pave_method):
        all_tiles = []
        all_tiles_rot = []
        all_tiles_center = []
        width = floor_size[0]
        height = floor_size[2]
        ceramic_width, ceramic_height = ceramic_size
        if pave_method == 'gongzipu':
            if ceramic_width > ceramic_height:
                rot = 0
            else:
                rot = 90
                ceramic_height, ceramic_width = ceramic_size
            for i in range(int(width // (ceramic_width + gap_width)) + 2):
                x_start_base = i * (ceramic_width + gap_width) + floor_start[0]

                for j in range(int(height // (ceramic_height + gap_width)) + 2):
                    y_start = j * (ceramic_height + gap_width) + floor_start[2]
                    y_end = (j + 1) * ceramic_height + j * gap_width + floor_start[2]
                    x_start = x_start_base - ceramic_width / 2 * (j % 2)
                    x_end = x_start + ceramic_width
                    all_tiles.append((
                        ((x_start, y_start), (x_start, y_end), (x_end, y_end), (x_end, y_start), (x_start, y_start)),
                        []
                    )
                    )
                    all_tiles_rot.append(rot)
                    all_tiles_center.append([0.5 * (x_start + y_start), 0.5 * (x_end + y_end)])

            # def norm_center(coord_center):
            #     j = (coord_center[1] - floor_start[2]) // (ceramic_height + gap_width)
            #     bias = ceramic_width / 2 * (j % 2)
            #     return [(coord_center[0] - floor_start[0] + bias) // (ceramic_width + gap_width) * (
            #                 ceramic_width + gap_width) + 0.5 * ceramic_width + floor_start[0] -bias,
            #      (coord_center[1] - floor_start[2]) // (ceramic_height + gap_width) * (
            #                  ceramic_height + gap_width) + 0.5 * ceramic_height + floor_start[2]]
        elif pave_method == 'renzipu':
            if ceramic_width > ceramic_height:
                rot = 0
            else:
                rot = -90
                ceramic_height, ceramic_width = ceramic_size
            sqr2 = np.sqrt(2)
            for i in range(int(width // ((ceramic_width + gap_width) * sqr2)) + 2):
                x_start = i * (ceramic_width + gap_width) * sqr2 + floor_start[0] - ceramic_height / sqr2
                x_start2 = x_start + (ceramic_height + ceramic_width + gap_width) / sqr2
                for j in range(int((height + ceramic_width) // ((ceramic_height + gap_width) * sqr2)) + 2):
                    y_start = j * (ceramic_height + gap_width) * sqr2 + floor_start[2] - ceramic_width / sqr2
                    y_start2 = y_start + (-ceramic_height + ceramic_width - gap_width) / sqr2
                    # y_end = y_start + ceramic_height + sqr2

                    all_tiles.append((
                        (
                            (x_start, y_start),
                            (x_start + ceramic_height / sqr2, y_start - ceramic_height / sqr2),
                            (x_start + (ceramic_height + ceramic_width) / sqr2, y_start + (-ceramic_height + ceramic_width) / sqr2),
                            (x_start + ceramic_width / sqr2, y_start + ceramic_width / sqr2),

                         ),
                        []
                    )
                    )
                    all_tiles_center.append(np.mean(all_tiles[-1][0], axis=0))
                    all_tiles.append((
                        (
                            (x_start2, y_start2),
                            (x_start2 - ceramic_height / sqr2, y_start2 - ceramic_height / sqr2),
                            (x_start2 + (-ceramic_height + ceramic_width) / sqr2, y_start2 - (ceramic_height + ceramic_width) / sqr2),
                            (x_start2 + ceramic_width / sqr2, y_start2 - ceramic_width / sqr2),

                        ),
                        []
                    )
                    )
                    all_tiles_rot.append(rot+45)
                    all_tiles_rot.append(rot-45)
                    all_tiles_center.append(np.mean(all_tiles[-1][0], axis=0))
        elif pave_method == 'yugupu':
            if ceramic_width > ceramic_height:
                rot = 0
            else:
                rot = -90
                ceramic_height, ceramic_width = ceramic_size
            sqr2 = np.sqrt(2)
            diag_l = np.sqrt(ceramic_width ** 2 + ceramic_height ** 2)
            pave_width = diag_l / sqr2
            pave_height = ceramic_height * sqr2
            for i in range(int(width // (pave_width + gap_width)) * 2 + 1):
                x_start = 2 * i * (pave_width + gap_width) + floor_start[0]
                x_start2 = (2 * i + 1) * (pave_width + gap_width) + floor_start[0]
                for j in range(int((height + ceramic_width) // pave_height) + 2):
                    y_start = j * (pave_height + gap_width) + floor_start[2] - pave_height / sqr2

                    all_tiles.append((
                        (
                            (x_start, y_start),
                            (x_start, y_start - pave_height),
                            (x_start + pave_width, y_start - pave_height - pave_width),
                            (x_start + pave_width, y_start - pave_width),

                         ),
                        []
                    )
                    )
                    all_tiles_center.append(np.mean(all_tiles[-1][0], axis=0))
                    all_tiles.append((
                        (
                            (x_start2, y_start - pave_width),
                            (x_start2, y_start - pave_height - pave_width),
                            (x_start2 + pave_width, y_start - pave_height),
                            (x_start2 + pave_width, y_start),

                        ),
                        []
                    )
                    )
                    all_tiles_rot.append(rot-45)
                    all_tiles_rot.append(rot+45)
                    all_tiles_center.append(np.mean(all_tiles[-1][0], axis=0))
            pass
        else:
            for i in range(int(width // (ceramic_width + gap_width)) + 1):
                x_start = i * ceramic_width + i * gap_width + floor_start[0]
                x_end = (i + 1) * ceramic_width + i * gap_width + floor_start[0]
                for j in range(int(height // (ceramic_height + gap_width)) + 1):
                    y_start = j * ceramic_height + j * gap_width + floor_start[2]
                    y_end = (j + 1) * ceramic_height + j * gap_width + floor_start[2]

                    all_tiles.append((
                        ((x_start, y_start), (x_start, y_end), (x_end, y_end), (x_end, y_start), (x_start, y_start)),
                        []
                    )
                    )
                    all_tiles_rot.append(0)
                    all_tiles_center.append([0.5 * (x_start + y_start), 0.5 * (x_end + y_end)])

            # def norm_center(coord_center):
            #     return [(coord_center[0] - floor_start[0]) // (ceramic_width + gap_width) * (
            #                 ceramic_width + gap_width) + 0.5 * ceramic_width + floor_start[0],
            #      (coord_center[1] - floor_start[2]) // (ceramic_height + gap_width) * (
            #                  ceramic_height + gap_width) + 0.5 * ceramic_height + floor_start[2]]
        return all_tiles, all_tiles_rot, all_tiles_center


if __name__ == '__main__':
    import time
    all_tiles = []
    floor = [(0,0), (40, 5), (90, 0), (90, 90), (80, 90), (80, 80), (1, 80), (0, 0)]
    f_p = Polygon(floor)
    for i in range(10000):
        all_tiles.append((
            (
                (i*1+0.1, i*1+0.1),
                ((i+1) * 1, i*1+0.1),
                ((i+1) * 1, (i+1)*1),
                (i*1+0.1, (i+1)*1),

            ),
            []
        )
        )
    start = time.time()

    mulPoly = MultiPolygon(all_tiles)
    r = f_p.intersection(mulPoly)
    print(time.time()-start)

    start = time.time()
    for tiles in all_tiles:
        p = Polygon(tiles[0])
        # if f_p.covers(p):
        #     continue
        res = f_p.intersection(p)
    print(time.time() - start)
