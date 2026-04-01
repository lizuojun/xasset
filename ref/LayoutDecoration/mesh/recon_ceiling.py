import copy
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from .recon_mesh import Mesh


class CeilingBuild(object):
    def __init__(self, room_type, mesh_uid_str, floor_pts, height=2.8, params_info=None, expand=False):
        self.uid = mesh_uid_str
        self.room_type = room_type
        self.floor_pts = floor_pts
        # customized ceiling height
        self.default_ceiling_height = 0.15
        self.height = height
        self.mesh_info = []
        self.floor_pts_cp = copy.deepcopy(floor_pts)
        if expand:
            min = np.min(floor_pts, axis=0)
            max = np.max(floor_pts, axis=0)
            self.floor_pts_cp = [[min[0], min[1]], [min[0], max[1]], [max[0], max[1]], [max[0], min[1]]]

    def build_mesh(self):
        if self.floor_pts_cp != self.floor_pts:
            expand_poly = Polygon(self.floor_pts_cp)
            org_poly = Polygon(self.floor_pts)
            remained_poly = expand_poly.difference(org_poly)
            if isinstance(remained_poly, MultiPolygon):
                coords = list(remained_poly)
                coords = [np.asarray(i.exterior.coords) for i in coords]
            else:
                coords = [np.asarray(remained_poly.exterior.coords)]

            for i in range(len(coords)):
                coord = coords[i]
                if len(coord) == 0:
                    continue
                poly = [[coord[pt][0], self.height - self.default_ceiling_height, coord[pt][1]] for pt in range(len(coord))]
                mesh = Mesh("Ceiling", self.uid + '_%d' % i)
                mesh.build_mesh(poly, [0, -1, 0])
                self.mesh_info.append(mesh)
        poly = [[self.floor_pts_cp[pt][0], self.height, self.floor_pts_cp[pt][1]] for pt in range(len(self.floor_pts_cp))]

        mesh = Mesh("Ceiling", self.uid)
        mesh.build_mesh(poly, [0, -1, 0])

        self.mesh_info.append(mesh)

        poly = [[self.floor_pts_cp[pt][0], self.height - 0.01, self.floor_pts_cp[pt][1]] for pt in
                range(len(self.floor_pts_cp))]

        mesh = Mesh("Ceiling", self.uid + '_2')
        mesh.build_mesh(poly, [0, -1, 0])

        self.mesh_info.append(mesh)

    def build_material(self, material):
        main_mat = material['main']
        seam_mat = material['seam'] if 'seam' in material else None
        added_meshes = []
        for mesh in self.mesh_info:
            if 'type' in main_mat and ('ceramic main floor' in main_mat['type'] or 'ceramic wall' in main_mat['type']) and seam_mat is not None:
                mesh.mat['jid'] = seam_mat['jid']
                mesh.mat['texture'] = seam_mat['texture']
                mesh.mat['color'] = seam_mat['color']
                mesh.mat['colorMode'] = seam_mat['colorMode']
                mesh.build_uv(seam_mat['uv_ratio'])

                ceramic_meshes, area, centroid = mesh.ceramic_layout(main_mat)
                for m in ceramic_meshes:
                    added_meshes.append(m)
            else:
                mesh.mat['jid'] = main_mat['jid']
                mesh.mat['texture'] = main_mat['texture']
                mesh.mat['color'] = main_mat['color']
                mesh.mat['colorMode'] = main_mat['colorMode']
                mesh.build_uv(np.array(main_mat['uv_ratio']))
        self.mesh_info += added_meshes
