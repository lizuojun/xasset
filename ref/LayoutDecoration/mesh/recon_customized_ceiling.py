from .recon_mesh import Mesh
import numpy as np


class CustomizedCeilingBuild:
    def __init__(self, customized_ceiling):
        self.customized_ceiling = customized_ceiling
        self.mesh_info = []

    def build_mesh(self):
        # return
        room_height = self.customized_ceiling['room_height']
        ceiling_height = self.customized_ceiling['ceiling_height']
        if self.customized_ceiling['type'] in ['living', 'dining', 'bed', 'work']:
            living_rect = self.customized_ceiling['layout_pts']
            for i in range(4):
                next_ind = (i + 1) % 4
                poly = [[living_rect[i][0], room_height - ceiling_height,
                         living_rect[i][1]],
                        [living_rect[i][0], room_height, living_rect[i][1]],
                        [living_rect[next_ind][0], room_height,
                         living_rect[next_ind][1]],
                        [living_rect[next_ind][0], room_height - ceiling_height,
                         living_rect[next_ind][1]]]
                mesh = Mesh("Ceiling", self.customized_ceiling['name'] + '_bounding_%d' % i)
                living_rect_center = np.mean(living_rect, axis=0)
                direct = np.array([living_rect[i][0] + living_rect[next_ind][0],
                                   living_rect[i][1] + living_rect[next_ind][
                                       1]]) / 2. - living_rect_center
                direct = direct / np.linalg.norm(direct)
                normal = [direct[0], 0, direct[1]]
                mesh.build_mesh(poly, normal)

                self.mesh_info.append(mesh)
        if self.customized_ceiling['type'] == 'hallway':
            hallway_rect = self.customized_ceiling['layout_pts']
            hall_way_height = room_height - ceiling_height

            poly = [[hallway_rect[pt][0], hall_way_height, hallway_rect[pt][1]] for pt in
                    range(len(hallway_rect))]

            mesh = Mesh("Ceiling", self.customized_ceiling['name'])
            mesh.build_mesh(poly, [0, -1, 0])
            self.mesh_info.append(mesh)

        if self.customized_ceiling['type'] in ['extra', 'cabinet']:
            area = self.customized_ceiling['layout_pts']
            poly = [[area[pt][0], room_height - ceiling_height, area[pt][1]] for pt in
                    range(len(area))]

            mesh = Mesh("Ceiling", self.customized_ceiling['name'])
            mesh.build_mesh(poly, [0, -1, 0])
            self.mesh_info.append(mesh)

    def build_material(self, material):
        main_mat = material['main']

        for mesh in self.mesh_info:
            mesh.mat['jid'] = main_mat['jid']
            mesh.mat['texture'] = main_mat['texture']
            mesh.mat['color'] = main_mat['color']
            mesh.mat['colorMode'] = main_mat['colorMode']
            mesh.build_uv(np.array(main_mat['uv_ratio']))