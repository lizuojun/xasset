import copy
import json
import os
from shapely.geometry import Polygon, MultiPolygon, LineString
import numpy as np
from trimesh import Trimesh, visual
from LayoutDecoration.mesh.recon_mesh import Mesh
from LayoutDecoration.libs.utils import correct_room_move
from LayoutDecoration.Base.math_util import rot_to_mat, combine_coincident_lines, map_uv, is_coincident_line
from matplotlib import pyplot as plt
from matplotlib import patches

import os
import json
from DataAccess.data_oss import oss_download_file

temp_dir = os.path.join(os.path.dirname(__file__), './temp/')
customized_feature_wall_tmp_folder = os.path.join(temp_dir, './customized_feature_wall/')
customized_data_bucket = 'ihome-alg-sample-data'
customized_data_oss_dir = 'customized_data/'
if not os.path.exists(customized_feature_wall_tmp_folder):
    os.makedirs(customized_feature_wall_tmp_folder)

class ReplaceHouse:
    # 端头墙mesh所属房间计算
    # 墙mesh所在地面floor起点计算，用于作为铺贴的norm_pt
    # 复用墙mesh xyz face norm,给定材质计算uv
    # 地面根据得到的mesh轮廓，重新三角化，切瓷砖，算铺贴
    def __init__(self, house_data, org_scene, replace_info, material_org, view=False):
        self.view = view
        self.org_scene = org_scene
        self.replace_info = replace_info
        self.material_org = material_org
        self.mesh = org_scene['mesh']
        self.furniture = org_scene['furniture']
        self.material = dict([(i['uid'], i) for i in org_scene['material']])
        self.children = dict([(i['instanceid'], i['children']) for i in org_scene['scene']['room']])
        self.house_info = {'rooms': {}}
        for room in house_data['room']:
            if 'construct_info' in room:
                room_id = room['id']
                self.house_info['rooms'][room_id] = room['construct_info']
        room = org_scene['scene']['room']
        # load room
        self.room_list = []
        instance_id_list = [0]
        furniture_id_list = [0]
        for room_one in room:
            for child in room_one['children']:
                if 'instanceid' in child and child['instanceid'].isdecimal():
                    instance_id_list.append(int(child['instanceid']))
        for fur in org_scene['furniture']:
            if fur['uid'].strip('/model').isdecimal():
                furniture_id_list.append(int(fur['uid'].strip('/model')))
        self.instanceid = max(instance_id_list) + 1
        self.furniture_id = max(furniture_id_list) + 1
        self.adds = {
            'mesh': [],
            'furniture': [],
            'material': [],
            'children': {}
        }
        self.removed = {
            'mesh': [],
            'furniture': [],
            'material': [],
            'children': {}
        }
        self.moved = {
            'mesh': [],
            'furniture': [],
            'material': [],
            'children': {}
        }
        for room_one in room:
            if room_one['instanceid'] in self.replace_info or room_one['instanceid'] not in self.house_info['rooms']:
                self.room_list.append(
                    {
                        'id': room_one['instanceid'],
                        'type': room_one['type'],
                        'children': room_one['children'],

                    }
                )

        self.mesh_dict = dict()
        construct_id_list = [0]
        for mesh_one in self.mesh:
            self.mesh_dict[mesh_one['uid']] = mesh_one
            if 'constructid' not in mesh_one:
                continue
            construct_id = mesh_one['constructid']
            if construct_id.isdecimal():
                construct_id_list.append(int(construct_id))
        self.construct_id_start = max(construct_id_list) + 1

    def replace(self, house_layout):
        room_mesh_dict = self.collect_mesh_by_room()
        # wall
        room_wall_mesh_dict = self.collect_mesh_by_type(room_mesh_dict, 'WallInner')
        room_floor_mesh_dict = self.collect_mesh_by_type(room_mesh_dict, 'Floor')
        self.replace_mesh(room_wall_mesh_dict, room_floor_mesh_dict)
        self.replace_background(house_layout)
        scene = self.replace_scene_json(self.org_scene)
        op_list = self.changes_to_op(room_mesh_dict)
        # json.dump(scene, open('/Users/liqing.zhc/code/ihome-layout/LayoutDecoration/replace_test.json', 'w'))
        return scene, op_list

    def changes_to_op(self, room_mesh_dict):
        op_list = []
        for room_id, rm_instance_ids in self.removed['children'].items():
            op_list += [(
                {
                    "operation": "remove_mesh",
                    "roomId": room_id,
                    "instanceId": instance
                }
            ) for instance in rm_instance_ids]
        add_mat_dict = dict([(i['uid'], i) for i in self.adds['material']])
        add_mesh_dict = dict([(i['uid'], i) for i in self.adds['mesh']])
        add_fur_dict = dict([(i['uid'], i) for i in self.adds['furniture']])

        add_mesh_dict_check = copy.deepcopy(add_mesh_dict)
        for room_id, instances in self.adds['children'].items():
            for instance in instances:
                ref = instance['ref']
                if ref not in add_mesh_dict:
                    if ref not in add_fur_dict:
                        print('not found instance')
                else:
                    add_mesh_dict_check.pop(ref)
                    add_mesh = add_mesh_dict[ref]
                    mesh_mat = add_mat_dict[add_mesh['material']]
                    new_mesh = {
                        "operation": "add_mesh",
                        "roomId": room_id,
                        "position": [0, 0, 0],
                        "rotation": [0, 0, 0, 1],
                        "scale": [1, 1, 1],
                        "constructid": add_mesh['constructid'],
                        "xyz": add_mesh['xyz'],
                        "normal": add_mesh['normal'],
                        "uv": add_mesh['uv'],
                        "faces": add_mesh['faces'],
                        "material": {
                            "jid": mesh_mat['jid'],
                            "texture": mesh_mat['texture'],
                            "normaltexture": mesh_mat['normaltexture'],
                            "color": mesh_mat['color'],
                            "colorMode": mesh_mat['colorMode'],
                            "UVTransform": mesh_mat['UVTransform'] if 'UVTransform' in mesh_mat else [
                                1, 0, 0, 0, 1, 0, 0, 0, 1],
                            "normalUVTransform": mesh_mat['normalUVTransform'] if 'normalUVTransform' in mesh_mat else [
                                1, 0, 0, 0, 1, 0, 0, 0, 1],
                            "contentType": mesh_mat['contentType'] if 'contentType' in mesh_mat else [],
                        }
                    }
                    op_list.append(new_mesh)
        print('mesh left: ', len(add_mesh_dict_check))
        return op_list

    def replace_mesh(self, room_wall_mesh_dict, room_floor_mesh_dict):
        wall_height = 2.8
        for room_id, room_wall_mesh_list in room_wall_mesh_dict.items():
            print('wall: ', room_id)
            # if len(room_wall_mesh_list) > 0:
            #     wall_polygons = self.merge_wall_mesh(room_wall_mesh_list)
            # else:
            #     wall_polygons = []
            # if self.view:
            #     plt.figure()
            #     for w in wall_polygons:
            #         wall = w['wall']
            #         plt.plot(np.array(wall)[:, 0], np.array(wall)[:, 1], color='red', linewidth=5)
            floor = [] if room_id not in self.house_info['rooms'] else self.house_info['rooms'][room_id]['floor_pts']
            mesh_floor_dict, mesh_wall_dict = self.wall_mesh_floor(room_wall_mesh_list, floor)
            for mesh_uid, floor_ind in mesh_floor_dict.items():
                if floor_ind == -1:
                    wall = mesh_wall_dict[mesh_uid]
                    norm_pt = [0.5 * (wall[0][0] + wall[1][0]), wall_height / 2., 0.5 * (wall[0][1] + wall[1][1])]
                    u_dir = [wall[1][0] - wall[0][0], 0, wall[1][1] - wall[0][1]]
                else:
                    norm_pt = 0.5 * (floor[floor_ind] + np.array(floor[(floor_ind + 1) % len(floor)]))
                    norm_pt = [norm_pt[0], wall_height / 2., norm_pt[1]]
                    u_dir = np.array(floor[(floor_ind + 1) % len(floor)]) - floor[floor_ind]
                    u_dir = [u_dir[0], 0., u_dir[1]]
                true_room_id = room_id
                if room_id not in self.house_info['rooms']:
                    wall = mesh_wall_dict[mesh_uid]
                    wall_line = LineString(wall)
                    for r_id, room_info in self.house_info['rooms'].items():
                        floor_poly = Polygon(room_info['floor_pts'])
                        if floor_poly.intersects(wall_line):
                            true_room_id = r_id
                            break
                if true_room_id not in self.replace_info or 'wall' not in self.replace_info[true_room_id]:
                    continue
                if 'all' not in self.replace_info[true_room_id]['wall']:
                    mesh_one = self.mesh_dict[mesh_uid]
                    if 'material' not in mesh_one or mesh_one['material'] not in self.material:
                        continue
                    mesh_one_mat = self.material[mesh_one['material']]
                    if mesh_one_mat['jid'] not in self.replace_info[true_room_id]['wall']:
                        continue
                    mat = self.replace_info[true_room_id]['wall'][mesh_one_mat['jid']]
                else:
                    if floor_ind < 0:
                        floor_ind = 0
                    wall_info = self.house_info['rooms'][true_room_id]['Wall'][floor_ind]
                    if len(wall_info) == 0:
                        continue
                    mat = wall_info['segments'][0]['material']['main']
                adds, removes = self.build_exist_mesh(self.mesh_dict[mesh_uid], norm_pt, mat, u_dir)
                self.adds['mesh'] += adds['mesh']
                self.adds['material'] += adds['material']
                if room_id not in self.adds['children']:
                    self.adds['children'][room_id] = []
                self.adds['children'][room_id] += adds['children']

                for i in self.children[room_id]:
                    if i['ref'] in removes['mesh']:
                        removes['children'].append(i['instanceid'])
                self.removed['mesh'] += removes['mesh']
                self.removed['material'] += removes['material']
                if room_id not in self.removed['children']:
                    self.removed['children'][room_id] = []
                self.removed['children'][room_id] += removes['children']

        # floor
        for room_id, room_floor_mesh_list in room_floor_mesh_dict.items():
            if room_id not in self.house_info['rooms']:
                continue
            print('floor: ', room_id)
            if len(room_floor_mesh_list) > 0:
                floor_polygons = self.merge_floor_mesh(room_floor_mesh_list)
            else:
                floor_polygons = []
            # if self.view:
            #     plt.figure()
            #     for poly in floor_polygons:
            #         hell = poly['polygons']['hell']
            #         holes = poly['polygons']['holes']
            #         plt.plot(np.array(hell)[:, 0], np.array(hell)[:, 2], color='green', linewidth=3)
            #         for hole in holes:
            #             plt.plot(np.array(hole)[:, 0], np.array(hole)[:, 2], color='black', linewidth=1)
            #     plt.show()

            # TODO Done 假设提取的所有地面都没有洞，消除在其他polygon的hell中的其他polygon
            not_valid_polygon = []
            for i in range(len(floor_polygons)):
                if i in not_valid_polygon:
                    continue
                hell_i = Polygon(np.array(floor_polygons[i]['polygons']['hell'])[:, [0, 2]])
                for j in range(i + 1, len(floor_polygons)):
                    hell_j = Polygon(np.array(floor_polygons[j]['polygons']['hell'])[:, [0, 2]])
                    if hell_i.area > hell_j.area:
                        if hell_i.contains(hell_j):
                            not_valid_polygon.append(j)
                    else:
                        if hell_j.contains(hell_i):
                            not_valid_polygon.append(i)
            valid_floor_polygons = [floor_polygons[i] for i in range(len(floor_polygons)) if i not in not_valid_polygon]
            if len(valid_floor_polygons) > 0:
                floor_info = self.house_info['rooms'][room_id]['Floor'][0]
                mat = floor_info['material']
                # mat里包含 main seam 和 default

                for i, polygon in enumerate(valid_floor_polygons):
                    if self.view:
                        plt.figure()
                        plt.title('floor contour-%s-%d' % (room_id, i))
                    uid = room_id + '_floor_%d' % i
                    adds, removes = self.build_new_mesh(polygon['polygons']['hell'], mat, uid, "Floor")
                    self.adds['mesh'] += adds['mesh']
                    self.adds['material'] += adds['material']
                    if room_id not in self.adds['children']:
                        self.adds['children'][room_id] = []
                    self.adds['children'][room_id] += adds['children']

                    self.removed['mesh'] += removes['mesh']
                    self.removed['material'] += removes['material']
                    if room_id not in self.removed['children']:
                        self.removed['children'][room_id] = []
                    self.removed['children'][room_id] += removes['children']
                    if self.view:
                        plt.plot(np.array(polygon['polygons']['hell'])[:, 0], np.array(polygon['polygons']['hell'])[:, 2])
                        for add_m in adds['mesh']:
                            faces = np.reshape(add_m['faces'], [-1, 3])
                            xyz = np.reshape(add_m['xyz'], [-1, 3])
                            for f in faces:
                                f = list(f)
                                face_pts = xyz[f + f[:1], :]
                                plt.plot(face_pts[:, 0], face_pts[:, 2], color='black')
                                unit_poly = patches.Polygon(face_pts[:, [0, 2]], edgecolor='black', facecolor='green')
                                plt.gca().add_patch(unit_poly)
                        plt.show()
            # floor 移除所有floor mesh相关元素
            self.removed['mesh'] += room_floor_mesh_list
            self.removed['material'] += [self.mesh_dict[i]['material'] for i in room_floor_mesh_list]
            if room_id not in self.removed['children']:
                self.removed['children'][room_id] = []
            for i in self.children[room_id]:
                if i['ref'] in room_floor_mesh_list:
                    self.removed['children'][room_id].append(i['instanceid'])

    def find_fur_entity_id(self, obj, room_id):
        entityIds = []
        for fur in self.furniture:
            if fur['jid'] == obj['id']:
                entityIds.append(fur['uid'])
        min_dis = 1e5
        entityid = None
        instanceid = None
        for ref in entityIds:

            ins = [i for i in self.children[room_id] if i['ref'] == ref]
            if len(ins) == 0:
                continue

            pos = ins[0]['pos']
            ins_id = ins[0]['instanceid']
            dis = np.linalg.norm(np.array(obj['position']) - pos)
            if dis < min_dis:
                min_dis = dis
                entityid = ref
                instanceid = ins_id
        return entityid, instanceid

    def replace_background(self, house_layout):
        for room_id, room_info in self.house_info['rooms'].items():
            if room_id not in self.replace_info or 'background' not in self.replace_info[room_id]:
                continue
            bg_walls = room_info['BgWall']
            for bg_wall in bg_walls:
                obj_info = bg_wall['obj_info']
                bg_type = bg_wall['type']
                org_backgrounds = []
                back_pts = None
                pos = None
                if room_id in self.material_org and 'background' in self.material_org[room_id]:
                    for bg in self.material_org[room_id]['background']:
                        if bg['Functional'] == bg_type:
                            flag, _, _ = is_coincident_line([bg_wall['back_p1'], bg_wall['back_p2']], bg['back_pts'])
                            if flag:
                                org_backgrounds.append(bg)
                if len(org_backgrounds) > 0:
                    org_backgrounds.sort(key=lambda x: -x['size'][0] * x['size'][1] * x['size'][2] * x['scale'][0] * x['scale'][1] * x['scale'][2])
                if len(org_backgrounds) > 0 and not org_backgrounds[0]['id'].endswith('.json'):
                    org_background = org_backgrounds[0]
                    org_pos = org_background['position']
                    org_size = org_background['size']
                    org_scale = org_background['scale']
                    org_rot = org_background['rotation']
                    obj_info['pos'] = org_pos
                    obj_info['rot'] = org_rot
                    obj_info['scale'] = [org_size[i] * org_scale[i] / obj_info['size'][i] for i in range(3)]

                # 被移除的配饰类别
                art_paint_type = 'art'
                acc_type = 'accessory'
                accessory_remove_strategy = obj_info['accessory'] if 'accessory' in obj_info else 0
                if accessory_remove_strategy == 1:
                    accessory_remove_types = [acc_type]
                elif accessory_remove_strategy == 2:
                    accessory_remove_types = [acc_type, art_paint_type]
                else:
                    accessory_remove_types = []
                # 移除
                if len(org_backgrounds) > 0:
                    org_background = org_backgrounds[0]
                    if org_background['id'].endswith('.json'):
                        removes = {
                            'mesh': org_background['uid_list'],
                            'children': []
                        }
                        for i in self.children[room_id]:
                            if i['ref'] in removes['mesh']:
                                removes['children'].append(i['instanceid'])
                        self.removed['mesh'] += removes['mesh']
                        if room_id not in self.removed['children']:
                            self.removed['children'][room_id] = []
                        self.removed['children'][room_id] += removes['children']
                        print('warning-replace: unsupport mesh background wall remove')
                    else:
                        entityId, instanceid = self.find_fur_entity_id(org_background, room_id)
                        if entityId is not None:
                            # self.removed['furniture'].append(entityId)
                            if room_id not in self.removed['children']:
                                self.removed['children'][room_id] = []
                            self.removed['children'][room_id].append(instanceid)

                # 移除配饰
                layout = house_layout[room_id]
                layout_copy = copy.deepcopy(layout)
                layout_tem = copy.deepcopy(layout)
                object_one_scale = {
                    'size': obj_info['size'],
                    'scale': copy.deepcopy(obj_info['scale']),
                    'position': obj_info['pos'],
                    'rotation': obj_info['rot']
                }
                object_one_scale['scale'][-1] = 0.4 * 100 / object_one_scale['size'][-1]
                correct_room_move(layout_tem, object_one_scale)
                group_list = layout_tem['layout_scheme'][0]['group']
                for group in group_list:
                    for obj in group['obj_list']:
                        if 'correct_move' in obj and obj['correct_move']:
                            if np.sum([i in obj['type'] for i in accessory_remove_types]) > 0 and group['type'] == 'Wall':
                                entityId, instanceid = self.find_fur_entity_id(obj, room_id)
                                if entityId is not None:
                                    # self.removed['furniture'].append(entityId)
                                    if room_id not in self.removed['children']:
                                        self.removed['children'][room_id] = []
                                    self.removed['children'][room_id].append(instanceid)
                                    print('remove attachment: %s' % obj['id'])

                if len(org_backgrounds) == 0:
                    # object_one_scale['scale'][-1] = 0.2 * 100 / object_one_scale['size'][-1]
                    object_one_scale = {
                        'size': obj_info['size'],
                        'scale': obj_info['scale'],
                        'position': obj_info['pos'],
                        'rotation': obj_info['rot']
                    }
                    correct_room_move(layout_copy, object_one_scale)
                    # 移动被修正的碰撞物体
                    group_list = layout_copy['layout_scheme'][0]['group']
                    for group in group_list:
                        for obj in group['obj_list']:
                            if 'correct_move' in obj and obj['correct_move']:
                                if np.sum([i in obj['type'] for i in accessory_remove_types]) > 0 and group['type'] == 'Wall':
                                    # entityId, instanceid = self.find_fur_entity_id(obj, room_id)
                                    # if entityId is not None:
                                    #     # self.removed['furniture'].append(entityId)
                                    #     if room_id not in self.removed['children']:
                                    #         self.removed['children'][room_id] = []
                                    #     self.removed['children'][room_id].append(instanceid)
                                    pass
                                else:
                                    entityId, instanceid = self.find_fur_entity_id(obj, room_id)
                                    if room_id not in self.moved['children']:
                                        self.moved['children'][room_id] = []
                                    self.moved['children'][room_id].append({
                                        'ref': entityId,
                                        'pos': obj['position']
                                    })

                #  增加
                contentType = obj_info['contentType'] if 'contentType' in obj_info else ''
                contentType = obj_info['type'] if contentType == '' and 'type' in obj_info else contentType

                uid = '%d/model' % self.furniture_id
                furniture_scheme = {
                    'jid': obj_info['jid'],
                    'uid': uid,
                    'title': '' if 'title' not in obj_info else obj_info['title'],
                    "type": "standard",
                    "contentType": contentType
                }
                self.instanceid += 1
                instance = {"pos": obj_info['pos'] if 'pos' in obj_info else [0, 0, 0],
                            "rot": obj_info['rot'] if 'rot' in obj_info else [0, 0, 0, 1],
                            "scale": obj_info['scale'] if 'scale' in obj_info else [1, 1, 1],
                            'ref': uid,
                            'instanceid': str(self.instanceid)}
                self.adds['furniture'].append(furniture_scheme)
                if room_id not in self.adds['children']:
                    self.adds['children'][room_id] = []
                self.adds['children'][room_id].append(instance)
                print('add background')


        # 指定替换背景墙
        for room_id, room_re in self.replace_info.items():
            if 'background' in room_re:
                if isinstance(room_re['background'], dict):
                    for org, obj_info in room_re['background'].items():
                        org_background = None
                        for bg in self.material_org[room_id]['background']:
                            if bg['id'] == org:
                                org_background = bg
                                break
                        if org_background is None:
                            continue

                        org_pos = org_background['position']
                        org_size = org_background['size']
                        org_scale = org_background['scale']
                        org_rot = org_background['rotation']

                        bounds = obj_info['bounds']
                        org_pos = [org_pos[0] - np.mean(bounds[0]), org_pos[1] - bounds[2][0],
                                   org_pos[2] - np.mean(bounds[1])]
                        obj_info['pos'] = org_pos
                        obj_info['rot'] = org_rot
                        obj_info['scale'] = [org_size[i] * org_scale[i] / obj_info['size'][i] for i in range(3)]

                        entityId, instanceid = self.find_fur_entity_id(org_background, room_id)
                        if entityId is not None:
                            # self.removed['furniture'].append(entityId)
                            if room_id not in self.removed['children']:
                                self.removed['children'][room_id] = []
                            self.removed['children'][room_id].append(instanceid)

                        obj_path = obj_info['id']
                        local_obj_path = os.path.join(customized_feature_wall_tmp_folder, obj_path)
                        if not os.path.exists(local_obj_path):
                            oss_download_file(customized_data_oss_dir + obj_path,
                                              local_obj_path,
                                              customized_data_bucket)

                        if not os.path.exists(local_obj_path):
                            print('Warning: house construct customized ceiling mesh obj lost')
                            return {}
                        obj_mesh = json.load(open(local_obj_path, 'r'))
                        for mesh_id, m in enumerate(obj_mesh):
                            xyz = m['xyz']
                            face = m['face']
                            normal = m['normal']
                            uv = m['uv']
                            material = m['material']

                            scale = obj_info['scale']
                            pos = obj_info['pos']
                            bounds = obj_info['bounds']
                            rot = obj_info['rot']
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
                            xyz += pos
                            xyz = np.reshape(xyz, [-1]).tolist()

                            now_mesh_json = {
                                "jid": "",
                                "uid": obj_info['id'].strip('.json') + '_%s_%s' % (0, mesh_id),
                                'xyz': xyz,
                                'normal': normal,
                                'uv': uv,
                                'faces': face,
                                'material': material['uid'],
                                # 'type': m['type'] if len(m['type']) != 0 else 'CustomizedPlatform',
                                'type': 'InnerWall',
                                'mainFlag': True,
                                'constructid': obj_info['id'].strip('.json') + '_%s_%s' % (room_id, mesh_id)
                            }
                            self.instanceid += 1
                            instance = {"pos": [0, 0, 0], "rot": [0, 0, 0, 1], "scale": [1., 1., 1.], 'ref': now_mesh_json['uid'],
                                        'instanceid': str(self.instanceid)}
                            adds = {
                                'mesh': [now_mesh_json],
                                'material': [material],
                                'children': [instance],
                            }
                            self.adds['mesh'] += adds['mesh']
                            self.adds['material'] += adds['material']
                            if room_id not in self.adds['children']:
                                self.adds['children'][room_id] = []
                            self.adds['children'][room_id] += adds['children']

    def replace_scene_json(self, org_scene):
        scene = copy.deepcopy(org_scene)
        #  remove first, then add
        mesh_res = []
        for mesh in scene['mesh']:
            if mesh['uid'] not in self.removed['mesh']:
                mesh_res.append(mesh)
        scene['mesh'] = mesh_res
        fur_res = []
        for fur in scene['furniture']:
            if fur['uid'] not in self.removed['furniture']:
                fur_res.append(fur)
        scene['furniture'] = fur_res
        # 材质存在公用情况，不移除
        # material_res = []
        # for material in scene['material']:
        #     if material['uid'] not in self.removed['material']:
        #         material_res.append(material)
        #
        # scene['material'] = material_res
        # 移动物品
        for room_id, moved_objs in self.moved['children'].items():
            for obj in moved_objs:
                min_match_child = None
                min_dis = 1e5
                for room in scene['scene']['room']:
                    if room['instanceid'] != room_id:
                        continue
                    for child in room['children']:
                        if child['ref'] != obj['ref']:
                            continue
                        dis = np.linalg.norm(np.array(child['pos']) - obj['pos'])
                        if dis < min_dis:
                            min_dis = dis
                            min_match_child = child
                if min_match_child is not None:
                    min_match_child['pos'] = obj['pos']
        rooms = []
        for room in scene['scene']['room']:
            copy_room = copy.deepcopy(room)
            copy_room['children'] = []
            room_id = room['instanceid']
            for child in room['children']:
                if room_id not in self.removed['children'] or child['instanceid'] not in self.removed['children'][room_id]:
                    copy_room['children'].append(child)
            rooms.append(copy_room)
        scene['scene']['room'] = rooms
        # #  添加新增
        scene['mesh'] += self.adds['mesh']
        scene['furniture'] += self.adds['furniture']
        scene['material'] += self.adds['material']
        for i, room in enumerate(scene['scene']['room']):
            room_id = room['instanceid']
            if room_id in self.adds['children']:
                scene['scene']['room'][i]['children'] += self.adds['children'][room_id]
        return scene

    def collect_mesh_by_room(self):
        room_mesh_dict = {}
        for room_one in self.room_list:
            room_mesh_dict[room_one['id']] = []
            for child_idx, child_one in enumerate(room_one['children']):
                child_uid = child_one['ref']
                if child_uid in self.mesh_dict:
                    room_mesh_dict[room_one['id']].append(child_uid)
        return room_mesh_dict

    def collect_mesh_by_type(self, room_mesh_dict, t_type):
        room_t_type_mesh_dict = {}
        for room_id, room_mesh in room_mesh_dict.items():
            if room_id not in self.replace_info and room_id in self.house_info['rooms']:
                continue

            if (room_id not in self.house_info['rooms'] or 'wall' in self.replace_info[room_id]) and t_type == 'WallInner':
                room_t_type_mesh_dict[room_id] = []
                wall_isolated_dict = {}
                for mesh_uid in room_mesh:
                    mesh_one = self.mesh_dict[mesh_uid]
                    if mesh_one['type'] == t_type:
                        room_t_type_mesh_dict[room_id].append(mesh_uid)
                    elif t_type == 'WallInner' and mesh_one['type'] in ['WallOuter', 'Back', 'Front']:
                        construct_id = mesh_one['constructid']
                        if construct_id not in wall_isolated_dict:
                            wall_isolated_dict[construct_id] = {
                                'WallOuter': [],
                                'Back': [],
                                'Front': [],
                            }
                        wall_isolated_dict[construct_id][mesh_one['type']].append(mesh_uid)
                for construct_id, v in wall_isolated_dict.items():
                    if len(v['WallOuter']) > 1:
                        room_t_type_mesh_dict[room_id] += v['WallOuter']
                        room_t_type_mesh_dict[room_id] += v['Back']
                        room_t_type_mesh_dict[room_id] += v['Front']
            elif (room_id not in self.house_info['rooms'] or 'floor' in self.replace_info[room_id]) and t_type == 'Floor':
                room_t_type_mesh_dict[room_id] = []
                for mesh_uid in room_mesh:
                    mesh_one = self.mesh_dict[mesh_uid]
                    if mesh_one['type'] == t_type:
                        room_t_type_mesh_dict[room_id].append(mesh_uid)
        return room_t_type_mesh_dict

    def wall_mesh_floor(self, room_mesh, room_floor):
        mesh_wall_dict = {}
        mesh_floor_dict = {}
        for mesh_uid in room_mesh:
            mesh_one = self.mesh_dict[mesh_uid]
            cur_xyz = np.around(np.reshape(mesh_one['xyz'], [-1, 3]), 3)
            cur_faces = np.reshape(mesh_one['faces'], [-1, 3])
            face_pts = np.reshape([cur_xyz[i] for i in cur_faces], [-1, 3])
            facet_pt_2d = face_pts[:, [0, 2]]
            min_xy = np.min(facet_pt_2d, axis=0)
            max_xy = np.max(facet_pt_2d, axis=0)
            wall = [[min_xy[0], min_xy[1]], [max_xy[0], max_xy[1]]]
            floor_ind = self.find_wall_floor(wall, room_floor)
            mesh_floor_dict[mesh_uid] = floor_ind
            mesh_wall_dict[mesh_uid] = wall
        return mesh_floor_dict, mesh_wall_dict

    @staticmethod
    def find_wall_floor(wall, floor):
        for i in range(len(floor)):
            floor_wall = [floor[i], floor[(i + 1) % len(floor)]]
            flag, _, _ = is_coincident_line(wall, floor_wall, dis_thresh=0.1)
            if flag:
                return i
        return -1

    def merge_wall_mesh(self, room_mesh):
        xyz = []
        faces = []
        normal = []
        for mesh_uid in room_mesh:
            mesh_one = self.mesh_dict[mesh_uid]
            cur_xyz = (np.around(np.reshape(mesh_one['xyz'], [-1, 3]), 3)).tolist()
            cur_faces = (np.reshape(mesh_one['faces'], [-1, 3]) + len(xyz)).tolist()
            cur_norm = (np.reshape(mesh_one['normal'], [-1, 3])).tolist()

            xyz += cur_xyz
            faces += cur_faces
            normal += cur_norm

        tri_mesh = Trimesh(xyz, faces=faces, vertex_normals=normal)

        facets = tri_mesh.facets
        facets_boundary = tri_mesh.facets_boundary
        facets_normal = tri_mesh.facets_normal
        wall_polygons = []
        if self.view:
            self.color_visual(tri_mesh)
        for i, facet in enumerate(facets):
            # facets n x m
            # facet m
            # facet_pt_ind m x 3
            # facet_pt m x 3 x 3
            facet_pt_ind = np.array(tri_mesh.faces)[facet]
            facet_pt = [np.array(tri_mesh.vertices)[i] for i in facet_pt_ind]
            facet_pt_2d = np.reshape([i[:, [0, 2]] for i in facet_pt], [-1, 2])
            min_xy = np.min(facet_pt_2d, axis=0)
            max_xy = np.max(facet_pt_2d, axis=0)
            wall = [[min_xy[0], min_xy[1]], [max_xy[0], max_xy[1]]]

            #
            # outline = tri_mesh.outline(facet)
            # paths = [line.points for line in outline.entities if len(line.points) >= 3]
            # flag = np.array([[line.closed for line in outline.entities]]).all() == 1
            # outline.show()
            # boundary
            facet_boundary = facets_boundary[i]
            paths = self.construct_boundary_into_paths(facet_boundary)
            flag = np.array([int(i[0] == i[-1]) for i in paths]).all() == 1
            if not flag:
                print('not closed outline')
            facet_boundary_pt = [np.array(tri_mesh.vertices)[i[:-1]] for i in paths]
            hell, holes = self.construct_paths_into_polygon(facet_boundary_pt, facets_normal[i], wall)
            if len(hell) == 0:
                continue
            wall_polygons.append({
                'wall': wall,
                'polygons': {
                    'hell': hell,
                    'holes': holes
                }
            })

        return wall_polygons

    def merge_floor_mesh(self, room_mesh):
        xyz = []
        faces = []
        normal = []
        for mesh_uid in room_mesh:
            mesh_one = self.mesh_dict[mesh_uid]
            cur_xyz = (np.around(np.reshape(mesh_one['xyz'], [-1, 3]), 3)).tolist()
            cur_faces = (np.reshape(mesh_one['faces'], [-1, 3]) + len(xyz)).tolist()
            cur_norm = (np.reshape(mesh_one['normal'], [-1, 3])).tolist()

            xyz += cur_xyz
            faces += cur_faces
            normal += cur_norm

        tri_mesh = Trimesh(xyz, faces=faces, vertex_normals=normal)

        facets = tri_mesh.facets
        facets_boundary = tri_mesh.facets_boundary
        facets_normal = tri_mesh.facets_normal
        floor_polygons = []
        if self.view:
            self.color_visual(tri_mesh)
        for i, facet in enumerate(facets):
            # facets n x m
            # facet m
            # facet_pt_ind m x 3
            # facet_pt m x 3 x 3
            facet_pt_ind = np.array(tri_mesh.faces)[facet]
            facet_pt = [np.array(tri_mesh.vertices)[i] for i in facet_pt_ind]
            facet_pt_2d = np.reshape([i[:, [0, 2]] for i in facet_pt], [-1, 2])

            #
            # outline = tri_mesh.outline(facet)
            # paths = [line.points for line in outline.entities if len(line.points) >= 3]
            # flag = np.array([[line.closed for line in outline.entities]]).all() == 1
            # outline.show()
            # boundary
            facet_boundary = facets_boundary[i]
            paths = self.construct_boundary_into_paths(facet_boundary)
            flag = np.array([int(i[0] == i[-1]) for i in paths]).all() == 1
            if not flag:
                print('not closed outline')
            facet_boundary_pt = [np.array(tri_mesh.vertices)[i[:-1]] for i in paths]
            hell, holes = self.construct_paths_into_polygon(facet_boundary_pt, [0, 1., 0])
            if len(hell) == 0:
                continue
            floor_polygons.append({
                'height': hell[0][1],
                'polygons': {
                    'hell': hell,
                    'holes': holes
                }
            })

        return floor_polygons

    @staticmethod
    def construct_boundary_into_paths(facet_boundary):
        paths = []
        boundary = copy.deepcopy(facet_boundary)
        boundary = list([list(i) for i in boundary])
        while True:
            is_isolated = True
            for i, isolated_p in enumerate(paths):
                for j, remained_b in enumerate(boundary):
                    flag = False
                    if isolated_p[-1] == remained_b[0]:
                        flag = True
                    elif isolated_p[-1] == remained_b[1]:
                        flag = True
                        remained_b.reverse()
                    if flag:
                        is_isolated = False
                        paths[i].append(remained_b[1])
                        boundary.pop(j)
                        break
                if not is_isolated:
                    break
            if len(boundary) == 0:
                break
            if is_isolated:
                paths.append(boundary[0])
                boundary.pop(0)
                if len(boundary) == 0:
                    break
        return paths

    def construct_paths_into_polygon(self, facet_boundary_pt, normal, wall=None):
        if abs(abs(np.dot([0, 1, 0], normal)) - 1.) < 1e-3:
            final_pts_2d = [np.array(i)[:, [0, 2]] for i in facet_boundary_pt]
        else:
            u_dir = np.array(wall[1]) - wall[0]
            final_pts_2d = [map_uv(i, [u_dir[0], 0, u_dir[1]], face_normal=normal)[0][:, [0, 2]] for i in facet_boundary_pt]
        areas = [Polygon(i).area for i in final_pts_2d]
        inds = np.argsort(areas)
        hell = facet_boundary_pt[inds[-1]] if areas[inds[-1]] > 1e-3 else []
        holes = [facet_boundary_pt[i] for i in inds[:-1] if areas[i] > 1e-3]
        if len(hell) == 0:
            return hell, holes
        hell_2d = np.array(final_pts_2d[inds[-1]] if areas[inds[-1]] > 1e-3 else [])
        holes_2d = np.array([final_pts_2d[i] for i in inds[:-1] if areas[i] > 1e-3])
        # hell_ind = self.refine_polygons(hell_2d)
        # holes_ind = [self.refine_polygons(i) for i in holes_2d]
        # hell = hell[hell_ind, :]
        # holes = [holes[i][holes_ind[i]] for i in range(len(holes_ind))]
        if self.view:
            plt.figure()
            plt.title('paths into polygon')
            plt.plot(hell_2d[:, 0], hell_2d[:, 1], color='green')
            colors = ['red', 'yellow', 'black', 'blue', 'pink', 'orange', 'cyan']
            for i, hole in enumerate(holes_2d):
                plt.plot(hole[:, 0], hole[:, 1], color=colors[i%len(colors)])
            plt.show()
        return hell, holes

    @staticmethod
    def refine_polygons(paths_2d):
        refined_paths = []
        for i in range(len(paths_2d)):
            cur = [paths_2d[(i - 1) % len(paths_2d)], paths_2d[i]]
            vec_cur = np.array(cur[1]) - cur[0]
            vec_cur = vec_cur / (np.linalg.norm(vec_cur) + 1e-8)
            next_ = [paths_2d[i], paths_2d[(i + 1) % len(paths_2d)]]
            vec_next = np.array(next_[1]) - next_[0]
            vec_next = vec_next / (np.linalg.norm(vec_next) + 1e-8)
            if abs(np.cross(vec_cur, vec_next)) > 1e-3:
                refined_paths.append(i)
        print(len(paths_2d), len(refined_paths))
        return refined_paths

    def color_visual(self, tri_mesh):
        color_dict = [
            [255,0,0],#red
            [255,255,0],#yellow
            [0,255,0],#green
            [0,255,255],#
            [0,0,255],#blue
            [255,0,255],#purple
            [10,10,10],#black
        ]
        face_color = np.zeros([len(tri_mesh.faces), 3])
        for i, facet in enumerate(tri_mesh.facets):
            face_color[facet] = color_dict[i % len(color_dict)]
        tri_mesh.visual = visual.create_visual(
                face_colors=face_color,
                vertex_colors=None,
                mesh=tri_mesh)

        # new_faces = []
        # new_faces += list(tri_mesh.faces[facets[3]])
        # new_faces += list(tri_mesh.faces[facets[5]])
        # new_faces += list(tri_mesh.faces[facets[6]])
        # tri_mesh.faces = new_faces
        # tri_mesh.process()
        tri_mesh.show()

    @staticmethod
    def merge_mesh_by_projected_lines(faces_pts):
        projected_lines = []
        for face in faces_pts:
            flag, cmb = combine_coincident_lines([face[0], face[1]], [face[0], face[2]])
            if not flag:
                print('invalid condition')
            projected_lines.append(cmb)
        remained_inds = list(range(len(projected_lines)))
        isolated_lines = []
        isolated_inds = []
        while True:
            is_isolated = True
            for i, isolated_l in enumerate(isolated_lines):
                for j, remained_l in enumerate(remained_inds):
                    flag, cmb = combine_coincident_lines(isolated_l, projected_lines[remained_l])
                    if flag:
                        is_isolated = False
                        isolated_lines[i] = cmb
                        isolated_inds[i].append(remained_l)
                        remained_inds.pop(j)
                        break
                if not is_isolated:
                    break
            if len(remained_inds) == 0:
                break
            if is_isolated:
                isolated_lines.append(projected_lines[remained_inds[0]])
                isolated_inds.append([remained_inds[0]])
                remained_inds.pop(0)
                if len(remained_inds) == 0:
                    break
        return isolated_lines, isolated_inds

    @staticmethod
    def merge_lines(mesh_wall_lines):
        room_wall_lines = copy.deepcopy(mesh_wall_lines)
        room_isolated_lines = []
        room_isolated_uids = []
        while True:
            is_isolated = True
            for i, isolated_l in enumerate(room_isolated_lines):
                for j, remained_l in enumerate(room_wall_lines):
                    flag, cmb = combine_coincident_lines(isolated_l, remained_l['line'])
                    if flag:
                        is_isolated = False
                        room_isolated_lines[i] = cmb
                        room_isolated_uids[i].append(remained_l)
                        room_wall_lines.pop(j)
                        break
                if not is_isolated:
                    break
            if len(room_wall_lines) == 0:
                break
            if is_isolated:
                room_isolated_lines.append(room_wall_lines[0]['line'])
                room_isolated_uids.append([room_wall_lines[0]])
                room_wall_lines.pop(0)
                if len(room_wall_lines) == 0:
                    break
        return room_isolated_lines, room_isolated_uids

    @staticmethod
    def merge_mesh_contour(faces_pts):
        remained_face_pts = copy.deepcopy(faces_pts)
        remained_poly = [Polygon(i) for i in remained_face_pts]
        isolated_poly = []
        while True:
            is_isolated = True
            for i, isolated_p in enumerate(isolated_poly):
                for j, remained_p in enumerate(remained_poly):
                    if remained_p.intersects(isolated_p):
                        is_isolated = False
                        try:
                            isolated_poly[i] = isolated_p.union(remained_p)
                        except Exception as e:
                            print(e)
                        remained_poly.pop(j)
                        break
                if not is_isolated:
                    break
            if len(remained_poly) == 0:
                break
            if is_isolated:
                isolated_poly.append(remained_poly[0])
                remained_poly.pop(0)
                if len(remained_poly) == 0:
                    break
        isolated_poly = [{'shell': np.asarray(i.exterior.coords).tolist(),
                          'holes': [np.asarray(j.coords).tolist() for j in i.interiors]} for i in isolated_poly]
        return isolated_poly

    @staticmethod
    def merge_polygons_contour(polygons):
        remained_poly = copy.deepcopy(polygons)
        remained_poly = [Polygon(shell=i['shell'], holes=i['holes']) for i in remained_poly]
        isolated_poly = []
        while True:
            is_isolated = True
            for i, isolated_p in enumerate(isolated_poly):
                for j, remained_p in enumerate(remained_poly):
                    if remained_p.intersects(isolated_p):
                        is_isolated = False
                        isolated_poly[i] = isolated_p.union(remained_p)
                        remained_poly.pop(j)
                        break
                if not is_isolated:
                    break
            if len(remained_poly) == 0:
                break
            if is_isolated:
                isolated_poly.append(remained_poly[0])
                remained_poly.pop(0)
                if len(remained_poly) == 0:
                    break
        isolated_poly = [{'shell': np.asarray(i.exterior.coords).tolist(),
                          'holes': [np.asarray(j.coords).tolist() for j in i.interiors]} for i in isolated_poly]
        return isolated_poly

    def build_exist_mesh(self, mesh_one, norm_pt, mat, u_dir):
        mesh_uid = mesh_one['uid']
        xyz = mesh_one['xyz']
        faces = mesh_one['faces']
        normal = mesh_one['normal']
        m = Mesh(mesh_one['type'], mesh_uid)
        m.build_exists_mesh(xyz, normal, [], faces, uv_norm_pt=norm_pt)
        m.set_u_dir(u_dir)

        m.mat['jid'] = mat['jid']
        m.mat['texture'] = mat['texture']
        m.mat['color'] = mat['color']
        m.mat['colorMode'] = mat['colorMode']
        m.build_uv(np.array(mat['uv_ratio']))
        now_mesh_json = {
            "jid": "",
            "uid": m.uid,
            'xyz': m.xyz,
            'normal': m.normals,
            'uv':  m.uv,
            'faces': m.faces,
            'material': m.mat['uid'],
            'type': m.mesh_type,
            'mainFlag': True,
            'constructid': mesh_one['constructid']
        }
        self.instanceid += 1
        instance = {"pos": [0, 0, 0], "rot": [0, 0, 0, 1], "scale": [1., 1., 1.], 'ref': m.uid,
                    'instanceid': str(self.instanceid)}
        adds = {
            'mesh': [now_mesh_json],
            'material': [m.mat],
            'children': [instance],
        }
        removes = {
            'mesh': [mesh_one['uid']],
            'material': [mesh_one['material']],
            'children': [],
        }
        return adds, removes

    def build_new_mesh(self, poly, material, uid, mesh_type):
        main_mat = material['main']
        seam_mat = material['seam'] if 'seam' in material else None
        mesh = Mesh(mesh_type, uid)
        mesh.build_mesh(np.array(poly).tolist(), [0, 1, 0])
        added_meshes = []
        if 'type' in main_mat and ('ceramic main floor' in main_mat['type'] or 'ceramic wall' in main_mat['type']) and seam_mat is not None and len(
                poly) >= 3:
            mesh.mat['jid'] = seam_mat['jid']
            mesh.mat['texture'] = seam_mat['texture']
            mesh.mat['color'] = seam_mat['color']
            mesh.mat['colorMode'] = seam_mat['colorMode']
            mesh.build_uv(seam_mat['uv_ratio'])
            refs = main_mat['refs'] if 'refs' in main_mat else []
            ceramic_meshes, area, centroid = mesh.ceramic_layout(main_mat, texture_list=refs)
            for m in ceramic_meshes:
                added_meshes.append(m)
        else:
            mesh.mat['jid'] = main_mat['jid']
            mesh.mat['texture'] = main_mat['texture']
            mesh.mat['color'] = main_mat['color']
            mesh.mat['colorMode'] = main_mat['colorMode']
            mesh.build_uv(np.array(main_mat['uv_ratio']))
        all_mesh = [mesh] + added_meshes

        mesh_json_list = []
        material_json_list = []
        instance_list = []
        for m in all_mesh:
            self.construct_id_start += 1
            now_mesh_json = {
                "jid": "",
                "uid": m.uid,
                'xyz': m.xyz,
                'normal': m.normals,
                'uv': m.uv,
                'faces': m.faces,
                'material': m.mat['uid'],
                'type': m.mesh_type,
                'mainFlag': True,
                'constructid': self.construct_id_start
            }
            self.instanceid += 1
            instance = {"pos": [0, 0, 0], "rot": [0, 0, 0, 1], "scale": [1., 1., 1.], 'ref': m.uid,
                        'instanceid': str(self.instanceid)}
            mesh_json_list.append(now_mesh_json)
            material_json_list.append(m.mat)
            instance_list.append(instance)

        adds = {
            'mesh': mesh_json_list,
            'material': material_json_list,
            'children': instance_list,
        }
        removes = {
            'mesh': [],
            'material': [],
            'children': []
        }
        return adds, removes


if __name__ == '__main__':
    scene_json = json.load(open('/Users/liqing.zhc/code/ihome-layout/LayoutCustomized/test_2.json'))
    r = ReplaceHouse('', scene_json, True)
    new_scene = r.replace()
