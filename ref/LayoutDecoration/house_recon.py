import copy
import json
import os
import numpy as np
from .mesh.recon_door import DoorBuild
from .mesh.recon_window import WindowBuild
from .mesh.recon_baseboard import BaseBoardBuild
from .mesh.recon_floor import FloorBuild
from .mesh.recon_ceiling import CeilingBuild
from .mesh.recon_wall import WallBuild
from .mesh.recon_customized_ceiling import CustomizedCeilingBuild
from .net_utils.data_oss import oss_download_file
from .Base.math_util import rot_to_mat


class ReconHouse:
    def __init__(self, house_data):
        house_info = dict()
        house_info['rooms'] = dict()
        house_info['global_light_params'] = house_data['global_light_params']
        temp_dir = os.path.join(os.path.dirname(__file__), './temp/')
        customized_ceiling_tmp_folder = os.path.join(temp_dir, './customized_ceiling/')
        customized_feature_wall_tmp_folder = os.path.join(temp_dir, './customized_feature_wall/')
        customized_model_tmp_folder = os.path.join(temp_dir, './customized_model/')
        customized_data_bucket = 'ihome-alg-sample-data'
        customized_data_oss_dir = 'customized_data/'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        if not os.path.exists(customized_ceiling_tmp_folder):
            os.makedirs(customized_ceiling_tmp_folder)
        if not os.path.exists(customized_feature_wall_tmp_folder):
            os.makedirs(customized_feature_wall_tmp_folder)
        if not os.path.exists(customized_model_tmp_folder):
            os.makedirs(customized_model_tmp_folder)
        for room in house_data['room']:
            if 'construct_info' in room:
                room_id = room['id']
                house_info['rooms'][room_id] = room['construct_info']

        for room_id, room_info in house_info['rooms'].items():
            room_type = room_info['type']
            new_floor_list = self.build_floor(room_info)
            house_info['rooms'][room_id]['Mesh'] += new_floor_list

            for ceiling in room_info['Ceiling']:
                ceiling_node = CeilingBuild(room_type, ceiling['name'], ceiling['layout_pts'])
                ceiling_node.build_mesh()
                ceiling_node.build_material(ceiling['material'])
                for m in ceiling_node.mesh_info:
                    house_info['rooms'][room_id]['Mesh'].append(
                        {
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
                                'Ceiling': ceiling['name']
                            }
                        }
                    )

            for door_info in room_info['Door']:
                door = DoorBuild(door_info)
                door.build_mesh()
                door.build_material(door_info['material'])
                for name, door_meshs in door.mesh_info.items():
                    for m in door_meshs:
                        house_info['rooms'][room_id]['Mesh'].append(
                            {
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
                                    'Wall': door_info['related']['Wall'],
                                    'Segment': door_info['related']['Segment'],
                                    'Door': door.name
                                }
                            }
                        )

            for win_info in room_info['Window']:
                win = WindowBuild(win_info)
                win.build_mesh()
                win.build_material(win_info['material'])
                for name, window_meshs in win.mesh_info.items():
                    for m in window_meshs:
                        house_info['rooms'][room_id]['Mesh'].append(
                            {
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
                                    'Wall': win_info['related']['Wall'],
                                    'Segment': win_info['related']['Segment'],
                                    'Door': win.name
                                }
                            }
                        )

            for baseboard_info in room_info['BaseBoard']:
                baseboard = BaseBoardBuild(baseboard_info)
                baseboard.build_mesh()
                baseboard.build_material(baseboard_info['material'])
                for m in baseboard.mesh_info:
                    house_info['rooms'][room_id]['Mesh'].append(
                        {
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
                                'Wall': baseboard_info['related']['Wall'],
                                'Segment': baseboard_info['related']['Segment']
                            }
                        }
                    )

            new_wall_list = self.build_wall(room_info)
            house_info['rooms'][room_id]['Mesh'] += new_wall_list

            for customized_ceiling_info in room_info['CustomizedCeiling']:
                if customized_ceiling_info['type'] in ['living', 'dining', 'bed', 'work'] and len(customized_ceiling_info['obj_info']['ceiling']) == 0:
                    continue
                if 'mesh' not in customized_ceiling_info or customized_ceiling_info['mesh']:
                    customized_ceiling = CustomizedCeilingBuild(customized_ceiling_info)
                    customized_ceiling.build_mesh()
                    customized_ceiling.build_material(customized_ceiling_info['material'])
                    for m in customized_ceiling.mesh_info:
                        house_info['rooms'][room_id]['Mesh'].append(
                            {
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
                                    'CustomizedCeiling': customized_ceiling_info['name']
                                }
                            }
                        )

                # check customized_ceiling mesh
                for obj in customized_ceiling_info['obj_info']['ceiling']:
                    if obj['contentType'] == 'CustomizedCeiling':
                        print('-------use customized ceiling %s' % obj['jid'])
                        obj_path = obj['jid']
                        local_obj_path = os.path.join(customized_ceiling_tmp_folder, obj_path)
                        if not os.path.exists(local_obj_path):
                            oss_download_file(customized_data_oss_dir + obj_path,
                                              local_obj_path,
                                              customized_data_bucket)

                        if not os.path.exists(local_obj_path):
                            print('Warning: house construct customized ceiling mesh obj lost')
                            continue
                        obj_mesh = json.load(open(local_obj_path, 'r'))
                        for mid, m in enumerate(obj_mesh):
                            xyz = m['xyz']
                            face = m['face']
                            normal = m['normal']
                            uv = m['uv']
                            material = m['material']

                            scale = obj['scale']
                            pos = obj['pos']
                            bounds = obj['bounds']
                            rot = obj['rot']
                            normal_pt = [np.mean(bounds[0]), bounds[2][0], np.mean(bounds[1])]
                            xyz = np.reshape(xyz, [-1, 3]) - normal_pt
                            xyz = xyz * scale
                            if rot[1] > 1e-1:
                                xyz = (xyz * np.array([1., 1., -1.]))[:, [2, 1, 0]] + normal_pt
                                normal = (np.reshape(normal, [-1, 3]) * np.array([1., 1., -1.]))[:, [2, 1, 0]]
                                normal = np.reshape(normal, [-1]).tolist()
                            else:
                                xyz = xyz + normal_pt
                            xyz += pos
                            xyz = np.reshape(xyz, [-1]).tolist()
                            print(obj['jid'].strip('.json') + '_%s_%s_customized_transfer' % (room_id, mid))
                            house_info['rooms'][room_id]['Mesh'].append(
                                {
                                    'name': obj['jid'].strip('.json') + '_%s_%s' % (room_id, mid),
                                    'type': m['type'] if 'type' in m and len(m['type']) != 0 else 'CustomizedCeiling',
                                    # 'type': 'CustomizedCeiling',
                                    # 'type': 'Ceiling',
                                    'uv': uv,
                                    'uid': obj['jid'].strip('.json') + '_%s' % mid,
                                    'xyz': xyz,
                                    'normals': normal,
                                    'faces': face,
                                    'u_dir': [],
                                    'uv_norm_pt': [],
                                    'layout_pts': customized_ceiling_info['layout_pts'],
                                    'material': material,
                                    'related': {
                                        'CustomizedCeiling': customized_ceiling_info['name']
                                    }
                                }
                            )

            for bg_wall_info in room_info['BgWall']:
                if bg_wall_info['obj_info']['contentType'] == 'customized feature wall':
                    print('-------use customized feature wall')
                    obj = bg_wall_info['obj_info']
                    obj_path = obj['jid']
                    local_obj_path = os.path.join(customized_feature_wall_tmp_folder, obj_path)
                    if not os.path.exists(local_obj_path):
                        oss_download_file(customized_data_oss_dir + obj_path,
                                          local_obj_path,
                                          customized_data_bucket)

                    if not os.path.exists(local_obj_path):
                        print('Warning: house construct customized ceiling mesh obj lost')
                        continue
                    obj_mesh = json.load(open(local_obj_path, 'r'))
                    for mid, m in enumerate(obj_mesh):
                        xyz = m['xyz']
                        face = m['face']
                        normal = m['normal']
                        uv = m['uv']
                        material = m['material']

                        scale = obj['scale']
                        pos = obj['pos']
                        bounds = obj['bounds']
                        rot = obj['rot']
                        normal_pt = [np.mean(bounds[0]), bounds[2][0], np.mean(bounds[1])]
                        xyz = np.reshape(xyz, [-1, 3]) - normal_pt
                        xyz = xyz * scale
                        rot_matrix = rot_to_mat(rot)
                        xz = xyz[:, [0, 2]].transpose()
                        xz = np.array(np.mat(rot_matrix) * xz).transpose()
                        xyz[:, [0, 2]] = xz
                        xyz += normal_pt
                        # xyz = np.array((np.mat(rot_matrix) * (xyz.transpose()))).transpose() + normal_pt
                        normal = np.reshape(normal, [-1, 3])
                        normal_xz = normal[:, [0, 2]].transpose()
                        normal_xz = np.array(np.mat(rot_matrix) * normal_xz).transpose()
                        normal[:, [0, 2]] = normal_xz
                        # normal = np.array((np.mat(rot_matrix) * (normal.transpose()))).transpose()
                        normal = np.reshape(normal, [-1]).tolist()
                        # if rot[1] > 1e-1:
                        #     xyz = (xyz * np.array([1., 1., -1.]))[:, [2, 1, 0]] + normal_pt
                        #     normal = (np.reshape(normal, [-1, 3]) * np.array([1., 1., -1.]))[:, [2, 1, 0]]
                        #     normal = np.reshape(normal, [-1]).tolist()
                        # else:
                        #     xyz = xyz + normal_pt
                        xyz += pos
                        xyz = np.reshape(xyz, [-1]).tolist()
                        house_info['rooms'][room_id]['Mesh'].append(
                            {
                                'name': obj['jid'].strip('.json') + '_%s_%s' % (room_id, mid),
                                'type': m['type'] if len(m['type']) != 0 else 'CustomizedFeatureWall',
                                # 'type': 'CustomizedFeatureWall',
                                # 'type': 'Ceiling',
                                'uv': uv,
                                'uid': obj['jid'].strip('.json') + '_%s' % mid,
                                'xyz': xyz,
                                'normals': normal,
                                'faces': face,
                                'u_dir': [],
                                'uv_norm_pt': [],
                                'layout_pts': obj['coords'],
                                'material': material,
                                'related': {
                                    'BgWall': bg_wall_info['name']
                                }
                            }
                        )

            for mid, obj in enumerate(room_info['ParametricModel']):
                print('-------use ParametricModel')
                obj_path = obj['id']
                local_obj_path = os.path.join(customized_model_tmp_folder, obj_path)
                if not os.path.exists(local_obj_path):
                    oss_download_file(customized_data_oss_dir + obj_path,
                                      local_obj_path,
                                      customized_data_bucket)

                if not os.path.exists(local_obj_path):
                    print('Warning: house construct customized model mesh obj lost')
                    continue
                obj_mesh = json.load(open(local_obj_path, 'r'))
                for mesh_id, m in enumerate(obj_mesh):
                    xyz = m['xyz']
                    face = m['face']
                    normal = m['normal']
                    uv = m['uv']
                    material = m['material']

                    scale = obj['scale']
                    pos = obj['position']
                    # bounds = obj['bounds']
                    rot = obj['rotation']
                    if 'turn' in obj:
                        cos_turn = np.cos(obj['turn'] * np.pi / 4)
                        sin_turn = np.sin(obj['turn'] * np.pi / 4)
                        rot1 = rot[1] * cos_turn + rot[3] * sin_turn
                        rot3 = rot[3] * cos_turn - rot[1] * sin_turn
                        rot = [0, rot1, 0, rot3]
                    # normal_pt = [np.mean(bounds[0]), bounds[2][0], np.mean(bounds[1])]
                    xyz = np.reshape(xyz, [-1, 3]) #  - normal_pt
                    xyz = xyz * scale
                    rot_matrix = rot_to_mat(rot)
                    xz = xyz[:, [0, 2]].transpose()
                    xz = np.array(np.mat(rot_matrix) * xz).transpose()
                    xyz[:, [0, 2]] = xz
                    # xyz += normal_pt
                    normal = np.reshape(normal, [-1, 3])
                    normal_xz = normal[:, [0, 2]].transpose()
                    normal_xz = np.array(np.mat(rot_matrix) * normal_xz).transpose()
                    normal[:, [0, 2]] = normal_xz
                    # normal = np.array((np.mat(rot_matrix) * (normal.transpose()))).transpose()
                    normal = np.reshape(normal, [-1]).tolist()
                    # if rot[1] > 1e-1:
                    #     xyz = (xyz * np.array([1., 1., -1.]))[:, [2, 1, 0]] + normal_pt
                    #     normal = (np.reshape(normal, [-1, 3]) * np.array([1., 1., -1.]))[:, [2, 1, 0]]
                    #     normal = np.reshape(normal, [-1]).tolist()
                    # else:
                    #     xyz = xyz + normal_pt
                    xyz += pos
                    xyz = np.reshape(xyz, [-1]).tolist()
                    house_info['rooms'][room_id]['Mesh'].append(
                        {
                            'name': obj['id'].strip('.json') + '_%s_%s_%s' % (room_id, mid, mesh_id),
                            'type': m['type'] if len(m['type']) != 0 else 'CustomizedPlatform',
                            # 'type': 'CustomizedFeatureWall',
                            # 'type': 'Ceiling',
                            'uv': uv,
                            'uid': obj['id'].strip('.json') + '_%s_%s' % (mid, mesh_id),
                            'xyz': xyz,
                            'normals': normal,
                            'faces': face,
                            'u_dir': [],
                            'uv_norm_pt': [],
                            'layout_pts': obj['coords'],
                            'material': material,
                            'related': {
                                'ParametricModel': mid
                            }
                        }
                    )

    @staticmethod
    def build_floor(room_info):
        room_type = room_info['type']
        new_mesh_list = []
        for floor in room_info['Floor']:
            floor_node = FloorBuild(room_type, floor['name'], floor['layout_pts'])
            floor_node.build_mesh()
            floor_node.build_material(floor['material'])

            for m in floor_node.mesh_info:
                new_mesh_list.append(
                    {
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
                            'Floor': floor['name']
                        },
                        'area': m.area,
                        'tiles': m.tile_count
                    }
                )
        return new_mesh_list

    @staticmethod
    def build_wall(room_info):
        new_wall_list = []
        for wall_info in room_info['Wall']:
            wall = WallBuild(wall_info)
            wall.build_mesh()
            # wall.build_material(wall_info['material'])
            for name, wall_meshs in wall.mesh_info.items():
                for m in wall_meshs:
                    new_wall_list.append(
                        {
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
                                'Wall': wall_info['name'],
                                'Segment': name,
                            },
                            'area': m.area,
                            'tiles': m.tile_count
                        }
                    )
        return new_wall_list


class SceneJson:
    def __init__(self, house_data, layout_info):
        self.house_info = dict()
        self.house_info['rooms'] = dict()
        self.house_info['global_light_params'] = house_data['global_light_params']
        for room in house_data['room']:
            if 'construct_info' in room:
                room_id = room['id']
                self.house_info['rooms'][room_id] = room['construct_info']

        self.layout_info = {}
        for room_uid in self.house_info['rooms'].keys():
            if room_uid in layout_info:
                if len(layout_info[room_uid]['layout_scheme']) > 0:
                    self.layout_info[room_uid] = layout_info[room_uid]['layout_scheme'][0]['group']
        self.light_info = {}
        for room in house_data['room']:
            if 'light_info' in room:
                room_id = room['id']
                self.light_info[room_id] = room['light_info']
        self.furniture_id = 2000
        self.light_id = 3000
        self.instanceid = 0
        self.door_list = {}
        self.window_list = []

        self.json = {
            "uid": house_data['id'] if 'id' in house_data else '',
            "design_version": "0.1",
            "code_version": "0.12",
            "north_vector": [0, 1, 0],
            'scene': {
                "ref": "-1",
                "pos": [0, 0, 0],
                "rot": [0, 0, 0, 1],
                "scale": [1, 1, 1],
                "room": []
            },
            'furniture': [],
            'material': [],
            'lights': [],
            'mesh': [],
            'extension': {
                'door': [],
                'outdoor': [],
                "skybox": {
                    "type": "builtin",
                    "name": "sea_sky",
                    "label": "",
                    "intensity": 1,
                    "rotationY": 0,
                    "uvScale": 1,
                    "localOffsetY": 0,
                    "bgColor": [
                        233,
                        233,
                        233
                    ],
                    "fillMode": 1,
                    "texelSize": 1024,
                    "uvScaleX": 1,
                    "uvScaleY": 1,
                    "uvOffsetX": 0,
                    "uvOffsetY": 0
                },
                "pano": {},
                "perspective_view": {
                    "link": []
                },
                "area": []
            },
            "not_seed_wall_list": [],
            "zncz_outdoor": ''
        }
        self.furniture_scheme = {
            'jid': '',
            'uid': ''
        }
        self.mesh_scheme = {
            "jid": "",
            "uid": "",
            'xyz': [],
            'normal': [],
            'uv': [],
            'faces': [],
            'material': '',
            'type': '',
            'mainFlag': True
        }
        self.material_scheme = {
            "uid": "",
            "jid": "",
            "texture": "",
            "normaltexture": "",
            "color": [255, 255, 255, 255]
        }
        self.door_scheme = {
            "type": "",
            "roomId": "",
            "dir": "",
            "ref": []
        }
        self.room_scheme = {
            "type": "",
            "instanceid": "",
            "size": 0,
            "pos": [
                0,
                0,
                0
            ],
            "rot": [
                0,
                0,
                0,
                1
            ],
            "scale": [
                1,
                1,
                1
            ],
            "children": []
        }
        self.instance_scheme = {
            "ref": "",
            "pos": [0, 0, 0],
            "rot": [0, 0, 0, 1],
            "scale": [1., 1., 1.]
        }

    # 构建scene json
    def write_scene_json(self, room_id_trans_dict=None):
        if 'enable_sun' in self.house_info['global_light_params']:
            self.json["extension"]["outdoor"] = self.house_info['global_light_params']['outdoor_scene']
            self.json["extension"]["skybox"]["name"] = self.house_info['global_light_params']['outdoor_scene']

            self.add_dome_light()

        for room_uid in self.house_info['rooms'].keys():
            room_info = self.house_info['rooms'][room_uid]
            if room_uid in self.layout_info:
                room_layout = self.layout_info[room_uid]
            else:
                room_layout = []

            room_light = self.light_info[room_uid]
            now_room_json = copy.deepcopy(self.room_scheme)
            now_room_json['size'] = room_info['area']
            if room_id_trans_dict is None:
                now_room_json['instanceid'] = room_info['alias']
                now_room_json['type'] = room_info['type']
            else:
                now_room_json['instanceid'] = room_id_trans_dict[room_info['alias']]['id']
                now_room_json['type'] = room_id_trans_dict[room_info['alias']]['type']

            # mesh
            for mesh in room_info['Mesh']:
                constructed_id = mesh['name']
                if 'Segment' in mesh['related']:
                    constructed_id = room_info['Wall'][mesh['related']['Wall']]['segments'][mesh['related']['Segment']]['wall_name']
                self.add_hard_instance_to_scene_json(mesh, now_room_json, constructed_id)

            # lights
            # outdoor scene
            for light in room_light:
                if light['type'] == 'MeshLight':
                    # 灯带
                    self.add_strip_light_to_scene_json(room_info['id'], light)
                elif light['type'] == 'AreaLight':
                    #  面光源
                    self.add_area_light_to_scene_json(room_info['id'], light)
                elif light['type'] == 'SpotLight':
                    # 射灯
                    self.add_spot_light_to_scene_json(now_room_json, room_info['id'], light)

            # 吊顶
            for customized_ceiling in room_info['CustomizedCeiling']:
                if customized_ceiling['type'] in ['living', 'dining', 'bed', 'work']:
                    for ceiling in customized_ceiling['obj_info']['ceiling']:
                        self.add_furniture_instance_to_scene_json(ceiling, now_room_json)
                        if 'attachment' in ceiling:
                            for fur in ceiling['attachment']:
                                self.add_furniture_instance_to_scene_json(fur, now_room_json)
            # 厨房
            for item in room_info['Kitchen']:
                self.add_furniture_instance_to_scene_json(item, now_room_json)
            # door
            for door in room_info['Door']:
                door_pos = np.mean(door['layout_pts'], axis=0).tolist()

                door_instance_id = '-'.join(sorted([door['base_room_id'], door['target_room_id']]))
                valid_door = True
                if door_instance_id in self.door_list:
                    for exist_door_pos in self.door_list[door_instance_id]:
                        if np.linalg.norm(np.array(door_pos) - exist_door_pos) < 1.:
                            valid_door = False
                            break
                if valid_door:
                    if door_instance_id not in self.door_list:
                        self.door_list[door_instance_id] = []
                    self.door_list[door_instance_id].append(door_pos)
                    self.add_furniture_instance_to_scene_json(door['obj_info'], now_room_json)
            # window
            for window in room_info['Window']:
                if window['name'] in self.window_list:
                    continue
                self.window_list.append(window['name'])
                self.add_furniture_instance_to_scene_json(window['obj_info'], now_room_json)

            # bg wall
            for bg_wall in room_info['BgWall']:
                self.add_furniture_instance_to_scene_json(bg_wall['obj_info'], now_room_json)
            # ParametricModel
            for ParametricModel in room_info['ParametricModel']:
                for fur in ParametricModel['attachment']:
                    self.add_furniture_instance_to_scene_json(fur, now_room_json)

            # 家具软装加入
            for group_info in room_layout:
                # if group_info['type'] in ['Door', 'Window']:
                #     continue
                for fur_obj in group_info['obj_list']:
                    # if ('type' in fur_obj and 'curtain' in fur_obj['type']) or fur_obj['role'] == 'curtain':
                    #     continue
                    if group_info['type'] in ['Door', 'Window']:
                        if 'type' in fur_obj and 'door' in fur_obj['type'] or fur_obj['role'] == 'door':
                            continue
                        if'type' in fur_obj and 'window' in fur_obj['type'] or fur_obj['role'] == 'window':
                            continue
                    if fur_obj['role'] == 'rug':
                        fur_obj['position'][1] += 0.006
                    title = '' if 'type' not in fur_obj else fur_obj['type']
                    if 'turn' in fur_obj:
                        cos_turn = np.cos(fur_obj['turn'] * np.pi / 4)
                        sin_turn = np.sin(fur_obj['turn'] * np.pi / 4)
                        rot1 = fur_obj['rotation'][1] * cos_turn + fur_obj['rotation'][3] * sin_turn
                        rot3 = fur_obj['rotation'][3] * cos_turn - fur_obj['rotation'][1] * sin_turn
                        fur_obj['rotation'] = [0, rot1, 0, rot3]
                    instance_scheme = {
                        'uid': '',
                        "jid": fur_obj['id'],
                        "pos": fur_obj['position'],
                        "rot": fur_obj['rotation'],
                        "scale": fur_obj['scale'],
                        "title": title,
                        "size": [0, 0, 0] if 'size' not in fur_obj else fur_obj['size'],
                        'type': fur_obj['type']
                    }
                    self.add_furniture_instance_to_scene_json(instance_scheme, now_room_json)
                    if ('type' in fur_obj and 'lighting' in fur_obj['type']) or fur_obj['role'] == 'lighting':
                        if 'light_intensity' in fur_obj and 'light_temperature' in fur_obj:
                            self.add_furniture_light_to_scene_json(self.instanceid - 1,
                                                                   fur_obj['light_intensity'],
                                                                   fur_obj['light_temperature'],
                                                                   # fur_obj['intensityScale'],
                                                                   # fur_obj['full_day_param']
                                                                   )

            self.json['scene']['room'].append(now_room_json)

        return self.json

    def add_furniture_light_to_scene_json(self, instance_id, intensity=2000, temperature=6500, intensityScale=1.,
                                          full_day_param={}):
        light_id = '%d/model' % self.light_id
        self.light_id += 1
        furniture_light = {
            "uid": light_id,
            "nodeType": "FurnitureLight",
            "roomId": "none",
            "temperature": temperature,
            "intensity": intensity,
            "instanceid": "%d" % instance_id,
            "units": 1,
            "enabled": True if intensity > 1 else False,
            "affectSpecular": False,
            "intensityScale": intensityScale,
            # "full_day_param": full_day_param
        }
        self.json['lights'].append(furniture_light)

    def add_spot_light_to_scene_json(self, now_room_json, room_id, light):
        light_id = '%d/model' % self.light_id
        self.light_id += 1
        shot_light_scheme = {
            "direction": [
                0,
                -1,
                0
            ],
            "enabled": True,
            "ies_file": "fill_light_2.ies",
            "nodeType": "VRayIES",
            "multiplier": light['intensity'],
            "power": light['intensity'],
            "roomId": room_id,
            "src_position": light['pos'],
            "temperature": light['temperature'],
            "uid": light_id,
            "up_vector": [
                0,
                0,
                -1
            ],
            # "full_day_param": light["full_day_param"]
        }
        self.json['lights'].append(shot_light_scheme)
        if light['physical_light']:
            one_instance = copy.deepcopy(self.instance_scheme)
            one_instance['ref'] = light_id
            one_instance['pos'] = light['pos']
            one_instance['rot'] = [0, 0, 0, 1]
            one_instance['scale'] = [1, 1, 1]
            one_instance['instanceid'] = str(self.instanceid)
            self.instanceid += 1
            now_room_json['children'].append(one_instance)

            one_fur = copy.deepcopy(self.furniture_scheme)
            one_fur['uid'] = light_id
            one_fur['jid'] = '871d9185-ef70-4b78-8d0c-13d72dfc43b3'
            one_fur['title'] = 'light'
            one_fur["type"] = "standard"
            one_fur["contentType"] = 'lighting/downlight'

            self.add_furniture_light_to_scene_json(self.instanceid - 1, 0)

            self.json['furniture'].append(one_fur)

    def add_strip_light_to_scene_json(self, room_id, light):
        light_id = '%d/model' % self.light_id
        self.light_id += 1
        ceiling_light = {
            "doubleSided": True,
            "ies_file": "",
            "instanceId": "",
            "invisible": True,
            "multiplier": light['intensity'],
            "nodeType": "VRayLight",
            "on": True,
            "pos": [
                0,
                0,
                0
            ],
            "position": [],
            "ref": light['related']['Mesh'],
            "roomId": room_id,
            "rot": [
                0,
                0,
                0,
                1
            ],
            "scale": [
                1,
                1,
                1
            ],
            "temperature": light['temperature'],
            "type": 3,
            "uid": light_id,
            "units": 1,
            # "full_day_param": light["full_day_param"]
        }
        self.json['lights'].append(ceiling_light)

    def add_area_light_to_scene_json(self, room_id, light):
        light_id = '%d/model' % self.light_id
        self.light_id += 1
        if abs(light['direction'][1]) > 0.5:
            up_vector = [light['direction'][1], light['direction'][0], 0]
        else:
            up_vector = [light['direction'][2], 0, light['direction'][0]]
        ceiling_light = {
            "nodeType": "VRayLight",  # 固定参数
            "type": 0,  # 0 表示面光
            "uid": light_id,
            "enabled": True,
            "DoubleSided": False,  # 是否为双面
            "color_temperature": light['temperature'],  # 色温
            "direction": light['direction'],  # 灯光朝向
            "multiplier": light['intensity'],  # 强度
            "units": 1,  # 强度单位（用户不需要修改）
            "roomId": room_id,
            "size0": light['size'][0],  # 宽度
            "size1": light['size'][1],  # 高度
            "skylightPortal": False,  # 是否为 skylight portal，除窗口补光外均应使用 false
            "src_position": light['pos'],  # 位置
            "up_vector": up_vector,  # 朝上的正方向,
            # "full_day_param": light["full_day_param"]
        }
        self.json['lights'].append(ceiling_light)

    def add_dome_light(self):

        light_id = '%d/model' % self.light_id
        self.light_id += 1
        sun_light = {
            "enabled": self.house_info['global_light_params']['enable_sun'],
            "filter_Color": self.house_info['global_light_params']['sun_color'],
            "intensity_multiplier": 0.1,
            "nodeType": "VraySun",
            "roomId": "none",
            "size_multiplier": 6,
            "sky_model": 0,
            "src_position": self.house_info['global_light_params']['sun_src_pos'],
            "target_position": self.house_info['global_light_params']['sun_target_pos'],
            "turbidity": 4,
            "uid": light_id,
            # "full_day_param": self.house_info['global_light_params']['full_day_param']
        }
        self.json['lights'].append(sun_light)
        light_id = '%d/model' % self.light_id
        self.light_id += 1
        dome1 = {
            "uid": light_id,
            "nodeType": "VrayLightDome",
            "roomId": "none",
            "textureTemperature": self.house_info['global_light_params']['dome_temperature'],
            "multiplier": 0.1,
            "enabled": self.house_info['global_light_params']['enable_sun'],
            "units": 0,
            "affectSpecular": False,
            "affectDiffuse": True,
            "textureType": "diffuse"
        }
        self.json['lights'].append(dome1)

        light_id = '%d/model' % self.light_id
        self.light_id += 1
        dome2 = {
            "uid": light_id,
            "nodeType": "VrayLightDome",
            "roomId": "none",
            "textureTemperature": self.house_info['global_light_params']['dome_temperature'],
            "multiplier": 0.2,
            "enabled": self.house_info['global_light_params']['enable_sun'],
            "units": 0,
            "affectSpecular": True,
            "affectDiffuse": False,
            "textureType": "specular"
        }
        self.json['lights'].append(dome2)

    def add_furniture_instance_to_scene_json(self, instance_info, now_room_json):
        if instance_info['jid'].endswith('.json'):
            return
        uid = '%d/model' % self.furniture_id
        self.furniture_id += 1
        one_fur_instance = copy.deepcopy(self.instance_scheme)
        one_fur_instance['ref'] = uid
        one_fur_instance['pos'] = instance_info['pos'] if 'pos' in instance_info else [0, 0, 0]
        one_fur_instance['rot'] = instance_info['rot'] if 'rot' in instance_info else [0, 0, 0, 1]
        one_fur_instance['scale'] = instance_info['scale'] if 'scale' in instance_info else [1, 1, 1]
        one_fur_instance['size'] = [0, 0, 0] if 'size' not in instance_info else instance_info['size']
        one_fur_instance['instanceid'] = str(self.instanceid)
        self.instanceid += 1

        now_room_json['children'].append(one_fur_instance)
        one_fur_instance = copy.deepcopy(self.furniture_scheme)
        one_fur_instance['uid'] = uid
        one_fur_instance['jid'] = instance_info['jid']
        one_fur_instance['title'] = '' if 'title' not in instance_info else instance_info['title']
        one_fur_instance["type"] = "standard"
        contentType = instance_info['contentType'] if 'contentType' in instance_info else ''
        contentType = instance_info['type'] if contentType == '' and 'type' in instance_info else contentType
        one_fur_instance["contentType"] = contentType

        self.json['furniture'].append(one_fur_instance)

    def add_hard_instance_to_scene_json(self, mesh, now_room_json, constructed_id):
        if len(mesh['xyz']) < 3:
            return
        now_mesh_json = copy.deepcopy(self.mesh_scheme)
        now_mesh_json['uid'] = mesh['name']
        now_mesh_json['xyz'] = mesh['xyz']
        now_mesh_json['normal'] = mesh['normals']
        now_mesh_json['faces'] = mesh['faces']
        now_mesh_json['type'] = mesh['type']
        now_mesh_json['material'] = mesh['material']['uid']
        now_mesh_json['uv'] = mesh['uv']
        # if 'Segment' in mesh['related']:
        #     now_mesh_json['constructid'] = mesh['related']['Segment']['wall_name']
        # else:
        now_mesh_json['constructid'] = constructed_id

        if mesh['type'] == 'Ceiling':
            if 'CustomizedCeiling' in mesh['related']:
                now_mesh_json['mainFlag'] = False
        if 'matType' in mesh['material']:
            if mesh['material']['matType'] == 'ceramic':
                now_mesh_json['mainFlag'] = False
        if 'colorMode' in mesh['material'] and mesh['material']['colorMode'] == 'color':
            mesh['material'].pop('jid', '')
        instance = {"pos": [0, 0, 0], "rot": [0, 0, 0, 1], "scale": [1., 1., 1.], 'ref': mesh['name'],
                    'instanceid': str(self.instanceid)}
        self.instanceid += 1
        now_room_json['children'].append(instance)
        if 'mesh' not in self.json:
            self.json['mesh'] = []
        if 'material' not in self.json:
            self.json['material'] = []
        self.json['mesh'].append(now_mesh_json)
        self.json['material'].append(mesh['material'])


def construct_house(house_data):
    house_layout = house_data['layout'] if 'layout' in house_data else {}
    ReconHouse(house_data)
    scene = SceneJson(house_data, house_layout)
    scene_json = scene.write_scene_json()
    return scene_json
