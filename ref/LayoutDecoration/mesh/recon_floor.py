import numpy as np
import copy
from .recon_mesh import Mesh


class FloorBuild(object):
    def __init__(self, room_type, mesh_uid_str, floor_pts, expand=False):
        self.uid = mesh_uid_str
        self.room_type = room_type
        self.floor_pts = floor_pts
        self.floor_pts_cp = copy.deepcopy(floor_pts)
        if expand:
            min = np.min(floor_pts, axis=0)
            max = np.max(floor_pts, axis=0)
            self.floor_pts_cp = [[min[0], min[1]], [min[0], max[1]], [max[0], max[1]], [max[0], min[1]]]

        self.mesh_info = []

    def build_mesh(self):
        poly = [[self.floor_pts_cp[pt][0], 0.0, self.floor_pts_cp[pt][1]] for pt in range(len(self.floor_pts_cp))]
        if len(poly) == 0:
            return

        refined_poly = [poly[0]]
        for i in range(len(poly) - 1):
            l = np.linalg.norm(np.array(poly[i + 1]) - np.array(refined_poly[-1]))
            if l > 1e-3:
                refined_poly.append(poly[i + 1])
        mesh = Mesh("Floor", self.uid)
        mesh.build_mesh(refined_poly, [0, 1, 0])

        self.mesh_info.append(mesh)

    def build_material(self, material):
        main_mat = material['main']
        seam_mat = material['seam'] if 'seam' in material else None
        added_meshes = []
        for mesh in self.mesh_info:
            # fix by lizuojun 2021.06.01
            if 'type' in main_mat and ('ceramic main floor' in main_mat['type'] or 'ceramic wall' in main_mat['type']) and seam_mat is not None and len(self.floor_pts) >= 3:
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

