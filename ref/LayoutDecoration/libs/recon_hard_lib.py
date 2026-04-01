import os
import numpy as np
import json
import time
import copy
import requests
# import math
# import uuid
# from PIL import Image
# from io import BytesIO
# from scipy.spatial.transform import Rotation as R
# from ..Base.recon_mesh import Mesh
from ..Base.recon_params import ROOM_BUILD_TYPE, PRIME_GENERAL_WALL_ROOM_TYPES
# from LayoutDecoration.cv.img_process import generate_img_ui
# from ..net_utils.data_oss import oss_upload_byte
from ..Base.math_util import is_coincident_line
from .utils import correct_room_move


class HardLib:
    def __init__(self, hard_libs=None, room_sample_mat_dict={}):
        self.hard_lib_file = os.path.join(os.path.dirname(__file__), 'hard_lib.json')
        if hard_libs is not None:
            self.HARD_LIBS = hard_libs
        else:
            self.HARD_LIBS = json.load(open(self.hard_lib_file, 'rb'), encoding='utf-8')
        self.room_floor_type = ''
        self.master_bedroom = [None, 0.]
        self.bedroom_customized_ceiling_id = None
        self.room_sample_mat_dict = room_sample_mat_dict

    def determine_mat_texture_postfix(self, output_path='./hard_lib.json', fix_posfix=True):
        if fix_posfix:
            for k, v in self.HARD_LIBS['tiles'].items():
                for mat in v:
                    if len(mat['texture_url']) > 0:
                        continue
                    jid = mat['jid']
                    if 'model_id' in list(mat.keys()):
                        prefix = 'http://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/%d/wallfloor' % mat['model_id']
                    else:
                        prefix = 'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/%s/wallfloor' % jid
                    r = requests.head(prefix + '.jpg')
                    if r.status_code == requests.codes.ok:
                        texture_url = prefix + '.jpg'
                    else:
                        r = requests.head(prefix + '.png')
                        if r.status_code == requests.codes.ok:
                            texture_url = prefix + '.png'
                        else:
                            texture_url = ''
                            # print('no texture url: %s %s' % (k, jid))
                    mat['texture_url'] = texture_url

                    if len(texture_url) == 0 and isinstance(mat['color'], str):
                        print(jid)

        with open(output_path, 'w') as f:
            json.dump(self.HARD_LIBS, f, indent='  ')

    def get_jid_ins(self, types=None, jid=None):
        libs = self.HARD_LIBS.copy()
        if types is None:
            return self.get_dict_son(libs, [], [], target_key='jid', target_v=jid)
        tree = []
        if isinstance(types, str):
            types = [types]
        for k in types:
            libs = libs[k]
            tree.append(k)
        for k, v in libs.items():
            for ins in v:
                if ins['jid'] == jid:
                    tree.append(k)
                    return ins, tree

    def get_dict_son(self, d, res, keys, target_key=None, target_v=None):
        for k, v in d.items():
            cur_keys = copy.deepcopy(keys)
            if isinstance(v, list):
                tem = self.get_list_son(v, res, cur_keys + [k], target_key, target_v)
                if tem is not None:
                    return tem
            elif isinstance(v, dict):
                if target_key is not None:
                    if target_key in v and v[target_key] == target_v:
                        return v, cur_keys + [k]
                tem = self.get_dict_son(v, res, cur_keys + [k], target_key, target_v)
                if tem is not None:
                    return tem
            else:
                res.append((v, cur_keys + [k]))

    def get_list_son(self, l, res, keys, target_key=None, target_v=None):
        for i, item in enumerate(l):
            cur_keys = copy.deepcopy(keys)
            if isinstance(item, list):
                tem = self.get_list_son(item, res, cur_keys + [i], target_key, target_v)
                if tem is not None:
                    return tem
            elif isinstance(item, dict):
                if target_key is not None:
                    if target_key in item and item[target_key] == target_v:
                        return item, cur_keys + [i]
                tem = self.get_dict_son(item, res, cur_keys + [i], target_key, target_v)
                if tem is not None:
                    return tem
            else:
                res.append((item, cur_keys + [i]))

    def get_door(self, types='swing door', index=None, cond={}, jid=None):
        if jid is not None:
            door, tree = self.get_jid_ins('door', jid)
        elif index is not None and 0 <= index < len(self.HARD_LIBS['door'][types]):
            door = self.HARD_LIBS['door'][types][index]
        else:
            if len(cond) == 0:
                door = np.random.choice(self.HARD_LIBS['door'][types])
            else:
                candidates = []
                for d in self.HARD_LIBS['door'][types]:
                    isvalid = True
                    for k, v in cond.items():
                        isvalid = isvalid and k in d and v(d[k])
                    if isvalid:
                        candidates.append(d)
                if len(candidates) > 0:
                    door = np.random.choice(candidates)
                else:
                    door = np.random.choice(self.HARD_LIBS['door'][types])

        ret_door = {'jid': door['jid'],
                    'size': [door['size'][0] / 1000., door['size'][2] / 1000., door['size'][1] / 1000.],
                    'contentType': door['contentType']}
        return ret_door

    def get_window(self, types='window', index=None, cond={}, jid=None):
        if jid is not None:
            win, tree = self.get_jid_ins('window', jid)
        elif index is not None and 0 <= index < len(self.HARD_LIBS['window'][types]):
            win = self.HARD_LIBS['window'][types][index]
        else:
            if len(cond) == 0:
                win = np.random.choice(self.HARD_LIBS['window'][types])
            else:
                candidates = []
                for d in self.HARD_LIBS['window'][types]:
                    isvalid = True
                    for k, v in cond.items():
                        isvalid = isvalid and k in d and v(d[k])
                    if isvalid:
                        candidates.append(d)
                if len(candidates) > 0:
                    win = np.random.choice(candidates)
                else:
                    win = np.random.choice(self.HARD_LIBS['window'][types])
        wall_offset = win['wall_offset'] if 'wall_offset' in win else None
        ret_win = {'jid': win['jid'],
                   'size': [win['size'][0] / 1000., win['size'][2] / 1000., win['size'][1] / 1000.],
                   'wall_offset': wall_offset,
                   'contentType': win['contentType']}
        return ret_win

    def get_material(self, types=('tiles', 'wooden'), index=None, jid=None):
        material_list = self.HARD_LIBS.copy()
        if isinstance(types, str):
            types = [types]
        for k in types:
            material_list = material_list[k]
        mat = None
        tree = []
        if jid is not None:
            mat, tree = self.get_jid_ins('tiles', jid)
        elif index is not None and 0 <= index < len(material_list):
            mat = material_list[index]
        if mat is None:
            print('random selected material')
            mat = np.random.choice(material_list)
        # mat = material_list[9]
        jid = mat['jid']
        if jid == 'user-specified':
            jid = ''
        texture_url = mat['texture_url']
        uv_ratio = [1000. / mat['size'][0], 1000. / mat['size'][1]]

        # print(texture_url)
        formated_mat = {
            'code': 1,
            "texture":
                texture_url,
            "jid": jid,
            "uv_ratio": [uv_ratio[0], 0, uv_ratio[1], 0],
            "color": [255, 255, 255, 255] if 'color' not in mat or isinstance(mat['color'], str) else mat['color'],
            "colorMode": 'texture' if len(texture_url) > 0 else 'color',
            'type': tree,
            'contentType': mat['contentType']
        }
        return formated_mat

    def config_hard_type(self, house_info, hard_type, hard_for_room, house_layout={}, sell_info=None, build_mode={}):
        # determine consistent bedroom customized ceiling
        for room_name, room_data in house_info['rooms'].items():
            if ROOM_BUILD_TYPE[room_data['type']] == 'MasterBedroom':
                if room_data['area'] > self.master_bedroom[1]:
                    self.master_bedroom = [room_data['id'], room_data['area']]
        doors = []
        for room_name, layouts in house_layout.items():
            for layout in layouts:
                if layout['type'] == 'Door':
                    for door in layout['obj_list']:
                        if 'door' in door['type'] and 'from' in door and 'to' in door and 'close_pos' in door and 'close_ang' in door:
                            doors.append(copy.deepcopy(door))

        # self.config_user_image(house_info)
        for room_name, room_info in house_info['rooms'].items():
            # UNIT mm毫米
            if 'customized_ceiling' not in build_mode or build_mode['customized_ceiling']:
                self.config_customized_ceiling_info(room_info, house_layout[room_name] if room_name in house_layout else {}, hard_type, hard_for_room)
            # unit m米
            if 'win_door' not in build_mode or build_mode['win_door']:
                self.config_win_door_info(room_info, hard_type, sell_info, doors, hard_for_room)
            # unit m米
            if 'mat' not in build_mode or build_mode['mat']:
                self.config_mat_info(room_info, hard_type, sell_info, hard_for_room)
            # if 'floor_line' not in build_mode or build_mode['floor_line']:
            #     self.config_floor_line_info(room_info, hard_type)
            # unit mm毫米
            if 'bg_wall' not in build_mode or build_mode['bg_wall']:
                self.config_bg_wall(room_info, hard_type, house_layout[room_name] if room_name in house_layout else {}, hard_for_room)

    def config_customized_ceiling_info(self, room_info, layouts, hard_type, hard_for_room, self_transfer=False):
        self_transfer = hard_for_room['self_transfer'][room_info['id']] if room_info['id'] in hard_for_room['self_transfer'] else False

        if len(room_info['CustomizedCeiling']) == 0:
            return
        flag = room_info['id'] in hard_for_room['customizedCeiling'] and len(hard_for_room['customizedCeiling'][room_info['id']]) == 1
        if self_transfer and flag:
            for customized_ceiling in room_info['CustomizedCeiling']:
                customized_ceiling['mesh'] = False
            chosen_customized = np.random.choice(hard_for_room['customizedCeiling'][room_info['id']])
            for customized_ceiling_id in range(len(room_info['CustomizedCeiling'])):
                room_info['CustomizedCeiling'][customized_ceiling_id]['ceiling_height'] = abs(chosen_customized['bounds'][-1][1] - chosen_customized['bounds'][-1][0])
            ceiling_height = 2.65
            for customized_ceiling_id in range(len(room_info['CustomizedCeiling'])):
                room_info['CustomizedCeiling'][customized_ceiling_id]['obj_info']['name'] = 'customizedCeiling_%s_%d' % (
                room_info['id'], customized_ceiling_id)

                floor_center = (np.min(room_info['floor_pts'], axis=0) + np.max(room_info['floor_pts'], axis=0)) * 0.5
                chosen_position = [floor_center[0], chosen_customized['position'][1], floor_center[1]]
                chosen_customized['position'] = chosen_position
                attachment = chosen_customized['attachment'] if 'attachment' in chosen_customized else []
                for fur in attachment:
                    fur['pos'] = [fur['pos'][0] + chosen_customized['position'][0],
                                  fur['pos'][1] + chosen_customized['position'][1],
                                  fur['pos'][2] + chosen_customized['position'][2]]
                room_info['CustomizedCeiling'][customized_ceiling_id]['obj_info']['ceiling'].append(
                    {
                        'jid': chosen_customized['id'],
                        'pos': chosen_customized['position'],
                        'scale': chosen_customized['scale'],
                        'rot': chosen_customized['rotation'],
                        'contentType': chosen_customized['contentType'],
                        'bounds': chosen_customized['bounds'],
                        'attachment': attachment
                    }
                )
                # 默认自迁移情况下，每个房间的吊顶使用一个模型表示，因此只在第一个吊顶区域下放置该模型，其他吊顶区域不放置obj。因此直接break
                ceiling_height = customized_ceiling['room_height'] - room_info['CustomizedCeiling'][customized_ceiling_id]['ceiling_height']
                break
            for i in range(len(layouts)):
                layout = layouts[i]
                if layout['type'] == 'Ceiling':
                    for j in range(len(layout['obj_list'])):
                        fur_obj = layout['obj_list'][j]
                        if ('type' in fur_obj and 'lighting' in fur_obj['type']) or fur_obj['role'] == 'lighting':
                            if fur_obj['position'][1] + fur_obj['size'][1] * fur_obj['scale'][1] / 100. > ceiling_height:
                                fur_obj['position'][1] = ceiling_height- fur_obj['size'][1] * fur_obj['scale'][1] / 100.
        else:
            room_type = ROOM_BUILD_TYPE[room_info['type']]
            if room_type in ['Library', 'KidsRoom']:
                room_type = 'MasterBedroom'
            if room_info['id'] in self.room_sample_mat_dict and self.room_sample_mat_dict[room_info['id']] in hard_type['customizedCeiling']:
                specified_style_ceiling = hard_type['customizedCeiling'][self.room_sample_mat_dict[room_info['id']]]
            else:
                specified_style_ceiling = hard_type['customizedCeiling'][room_type]
            if len(specified_style_ceiling) == 0:
                for customized_ceiling in room_info['CustomizedCeiling']:
                    customized_ceiling['mesh'] = False
                return
            if specified_style_ceiling is None or len(specified_style_ceiling) == 0:
                if hard_type['style'] in self.HARD_LIBS['ceiling']:
                    specified_style_ceiling = self.HARD_LIBS['ceiling']['nordic']
            suited_valid_id_list = []
            common_suited_ids = set(range(len(specified_style_ceiling)))
            num = 0
            for customized_ceiling in room_info['CustomizedCeiling']:
                if customized_ceiling['type'] in ['living', 'dining', 'bed', 'work']:
                    num += 1
                    floor_pts = np.array(customized_ceiling['layout_pts'])
                    floor_l = np.sqrt(np.sum(np.square(floor_pts[0] - floor_pts[1])))
                    floor_w = np.sqrt(np.sum(np.square(floor_pts[1] - floor_pts[2])))
                    floor_ratio = floor_l / floor_w

                    if floor_ratio < 1:
                        floor_ratio = 1. / floor_ratio
                        floor_l = floor_w
                        floor_w = floor_l / floor_ratio

                    suited_ceiling_inds = []
                    for i in range(len(specified_style_ceiling)):
                        size = specified_style_ceiling[i]['size']
                        size = [i / 1000. for i in size]
                        resizeable = specified_style_ceiling[i]['resizeable']
                        scalable = True
                        if 'scale' in specified_style_ceiling[i]:
                            scalable = specified_style_ceiling[i]['scale']
                        ceiling_ratio = size[0] / size[1]
                        if ceiling_ratio < 1:
                            ceiling_ratio = 1. / ceiling_ratio

                        ceiling_l = size[0]
                        ceiling_w = size[1]
                        if ceiling_l < ceiling_w:
                            ceiling_l = ceiling_w
                            ceiling_w = size[0]

                        scale_l = ceiling_l / floor_l
                        scale_w = ceiling_w / floor_w
                        if scale_l < 1.:
                            scale_l = 1. / scale_l
                        if scale_w < 1.:
                            scale_w = 1. / scale_w
                        if (resizeable or (ceiling_ratio / floor_ratio < 1.2 and floor_ratio / ceiling_ratio < 1.2)) \
                                and (scalable or (scale_l < 1.2 and scale_w < 1.2)):
                            suited_ceiling_inds.append(i)
                    if len(suited_ceiling_inds) == 0:
                        print('warning: no suited ceiling')
                        suited_ceiling_inds = specified_style_ceiling
                    suited_valid_id_list.append(suited_ceiling_inds)
                    common_suited_ids = common_suited_ids & set(suited_ceiling_inds)
            if num == 0:
                return
            if room_type == 'MasterBedroom' and self.bedroom_customized_ceiling_id is not None:
                suited_valid_id_list = [
                        self.bedroom_customized_ceiling_id if self.bedroom_customized_ceiling_id in i else np.random.choice(
                            i) for i in suited_valid_id_list]
            else:
                if len(common_suited_ids) == 0:
                    suited_valid_id_list = [np.random.choice(i) for i in suited_valid_id_list]
                else:
                    suited_valid_id_list = [np.random.choice(list(common_suited_ids))] * len(suited_valid_id_list)
                if room_type == 'MasterBedroom':
                    self.bedroom_customized_ceiling_id = suited_valid_id_list[0]

            for customized_ceiling_id in range(len(room_info['CustomizedCeiling'])):
                customized_ceiling = room_info['CustomizedCeiling'][customized_ceiling_id]
                if customized_ceiling['type'] in ['living', 'dining', 'bed', 'work']:
                    height = customized_ceiling['room_height']
                    floor_pts = np.array(customized_ceiling['layout_pts'])
                    floor_l = np.sqrt(np.sum(np.square(floor_pts[0] - floor_pts[1])))
                    floor_w = np.sqrt(np.sum(np.square(floor_pts[1] - floor_pts[2])))

                    choosen_ceiling_ind = suited_valid_id_list[customized_ceiling_id]
                    jid = specified_style_ceiling[choosen_ceiling_ind]['jid']
                    size = specified_style_ceiling[choosen_ceiling_ind]['size']
                    contentType = specified_style_ceiling[choosen_ceiling_ind]['contentType']
                    size = [i / 1000. for i in size]
                    ceiling_l = size[0]
                    ceiling_w = size[1]
                    ceiling_h = size[2]

                    if np.argmax(np.abs(floor_pts[0] - floor_pts[1])) == 1:
                        pitch = np.pi / 2.
                    else:
                        pitch = 0.

                    if (ceiling_l - ceiling_w) * (floor_l - floor_w) >= 0:
                        scale = [floor_l / ceiling_l, customized_ceiling['ceiling_height'] / ceiling_h, floor_w / ceiling_w]
                    else:
                        scale = [floor_w / ceiling_l, customized_ceiling['ceiling_height'] / ceiling_h, floor_l / ceiling_w]
                        pitch -= np.pi / 2

                    if 'rot' in specified_style_ceiling[choosen_ceiling_ind]:
                        pitch -= specified_style_ceiling[choosen_ceiling_ind]['rot'] / 180 * np.pi
                    # rot = self.euler_to_quaternion(0, pitch, 0)
                    pitch = (abs(pitch) + 1e-8) % np.pi
                    rot = [0, np.sin(pitch / 2.), 0, np.cos(pitch / 2.)]

                    pos = np.mean(floor_pts, axis=0)

                    if 'bounds' in specified_style_ceiling[choosen_ceiling_ind]:
                        bounds = specified_style_ceiling[choosen_ceiling_ind]['bounds']
                        pos = [pos[0] - np.mean(bounds[0]), height - size[-1] * scale[1] - bounds[2][0],
                               pos[1] - np.mean(bounds[1])]

                    else:
                        pos = [pos[0], height - size[-1] * scale[1], pos[1]]
                        bounds = [[0, 0], [0, 0], [0, 0]]

                    room_info['CustomizedCeiling'][customized_ceiling_id]['obj_info']['name'] = 'customizedCeiling_%s_%d' % (room_info['id'], customized_ceiling_id)
                    room_info['CustomizedCeiling'][customized_ceiling_id]['obj_info']['ceiling'].append(
                        {
                            'jid': jid,
                            'pos': pos,
                            'scale': scale,
                            'rot': rot,
                            'contentType': contentType,
                            'bounds': bounds
                        }
                    )

                    if 'light' in specified_style_ceiling[choosen_ceiling_ind]:
                        light_type = specified_style_ceiling[choosen_ceiling_ind]['light']['type']
                        # if light_type == 'spot light':
                        #     room_info['CustomizedCeiling'][customized_ceiling_id]['obj_info']['SpotLight'].append(copy.deepcopy(
                        #         specified_style_ceiling[choosen_ceiling_ind]['light']['layout']))
                        # elif light_type == 'strip light':
                        #     room_info['CustomizedCeiling'][customized_ceiling_id]['obj_info']['MeshLight'].append(copy.deepcopy(
                        #         specified_style_ceiling[choosen_ceiling_ind]['light']['layout']))
                    if 'center_under_height' in specified_style_ceiling[choosen_ceiling_ind]:
                        room_info['CustomizedCeiling'][customized_ceiling_id]['obj_info']['ceiling'][-1]['center_under_height'] = specified_style_ceiling[choosen_ceiling_ind]['center_under_height'] / 1000.

            # 调整灯具
            living_rect = None
            living_height = 0
            dining_rect = None
            dining_height = 0
            bed_rect = None
            bed_height = 2.8
            for customized_ceiling_id in range(len(room_info['CustomizedCeiling'])):
                customized_ceiling = room_info['CustomizedCeiling'][customized_ceiling_id]
                if customized_ceiling['type'] == 'living' and living_rect is None:
                    living_rect = customized_ceiling['layout_pts']
                    living_height = customized_ceiling['room_height'] - customized_ceiling['ceiling_height']

                    if len(customized_ceiling['obj_info']['ceiling']) > 0:
                        if 'center_under_height' in customized_ceiling['obj_info']['ceiling'][-1]:
                            living_height = customized_ceiling['room_height'] - customized_ceiling['obj_info']['ceiling'][-1]['center_under_height']

                if customized_ceiling['type'] == 'dining' and dining_rect is None:
                    dining_rect = customized_ceiling['layout_pts']
                    dining_height = customized_ceiling['room_height'] - customized_ceiling['ceiling_height']
                    if len(customized_ceiling['obj_info']['ceiling']) > 0:
                        if 'center_under_height' in customized_ceiling['obj_info']['ceiling'][-1]:
                            dining_height = customized_ceiling['room_height'] - customized_ceiling['obj_info']['ceiling'][-1]['center_under_height']
                if customized_ceiling['type'] == 'bed' and bed_rect is None:
                    bed_rect = customized_ceiling['layout_pts']
                    bed_height = customized_ceiling['room_height'] - customized_ceiling['ceiling_height']
                    if len(customized_ceiling['obj_info']['ceiling']) > 0:
                        if 'center_under_height' in customized_ceiling['obj_info']['ceiling'][-1]:
                            bed_height = customized_ceiling['room_height'] - customized_ceiling['obj_info']['ceiling'][-1]['center_under_height']
            if living_rect is not None or dining_rect is not None or bed_rect is not None:
                living_light = []
                dining_light = []
                bed_light = []
                for i in range(len(layouts)):
                    layout = layouts[i]
                    if layout['type'] == 'Ceiling':
                        for j in range(len(layout['obj_list'])):
                            fur_obj = layout['obj_list'][j]
                            if ('type' in fur_obj and 'lighting' in fur_obj['type']) or fur_obj['role'] == 'lighting':
                                if living_rect is not None and np.min(living_rect, axis=0)[0] < fur_obj['position'][0] < \
                                        np.max(living_rect, axis=0)[0] and np.min(living_rect, axis=0)[1] < \
                                        fur_obj['position'][2] < np.max(living_rect, axis=0)[1]:
                                    living_light.append((i, j))
                                if dining_rect is not None and np.min(dining_rect, axis=0)[0] < fur_obj['position'][0] < \
                                        np.max(dining_rect, axis=0)[0] and np.min(dining_rect, axis=0)[1] < \
                                        fur_obj['position'][2] < np.max(dining_rect, axis=0)[1]:
                                    dining_light.append((i, j))
                                if bed_rect is not None and np.min(bed_rect, axis=0)[0] < fur_obj['position'][0] < \
                                        np.max(bed_rect, axis=0)[0] and np.min(bed_rect, axis=0)[1] < \
                                        fur_obj['position'][2] < np.max(bed_rect, axis=0)[1]:
                                    bed_light.append((i, j))
                if len(living_light) == 1 and len(dining_light) > 1:
                    layouts[living_light[0][0]]['obj_list'][living_light[0][1]]['position'][0] = \
                        np.mean(living_rect, axis=0)[0]
                    fur_obj = layouts[living_light[0][0]]['obj_list'][living_light[0][1]]
                    if fur_obj['position'][1] + fur_obj['size'][1] * fur_obj['scale'][1] / 100. > 2.5:
                        fur_obj['position'][1] = living_height - fur_obj['size'][1] * fur_obj['scale'][1] / 100.
                    layouts[living_light[0][0]]['obj_list'][living_light[0][1]]['position'][2] = \
                        np.mean(living_rect, axis=0)[1]
                if len(dining_light) == 1 and len(living_light) > 1:
                    # layouts[dining_light[0][0]]['obj_list'][dining_light[0][1]]['position'][0] = \
                    #     np.mean(dining_rect, axis=0)[0]
                    fur_obj = layouts[dining_light[0][0]]['obj_list'][dining_light[0][1]]
                    if fur_obj['position'][1] + fur_obj['size'][1] * fur_obj['scale'][1] / 100. > 2.5:
                        fur_obj['position'][1] = dining_height - fur_obj['size'][1] * fur_obj['scale'][1] / 100.
                    # layouts[dining_light[0][0]]['obj_list'][dining_light[0][1]]['position'][2] = \
                    #     np.mean(dining_rect, axis=0)[1]
                if len(bed_light) >= 1:
                    for i, j in bed_light:
                        fur_obj = layouts[i]['obj_list'][j]
                        if fur_obj['position'][1] + fur_obj['size'][1] * fur_obj['scale'][1] / 100. > 2.5:
                            fur_obj['position'][1] = bed_height - fur_obj['size'][1] * fur_obj['scale'][1] / 100.

    def config_win_door_info(self, room_info, hard_type, sell_info, referenced_doors=[], hard_for_room={}):
        room_type = ROOM_BUILD_TYPE[room_info['type']]
        if room_type in ['Library', 'KidsRoom']:
            room_type = 'MasterBedroom'

        for door in room_info['Door']:
            if door['is_hole'] and 'Bathroom' not in [door['target_room_type'], door['base_room_type']]:
                continue
            #  调整door方向
            door_pos = door['obj_info']['pos']
            matched_door = None
            min_dis = 1e8
            for refer_door in referenced_doors:
                if sorted([refer_door['from'], refer_door['to']]) == sorted([door['base_room_id'], door['target_room_id']]):
                    refer_pos = refer_door['close_pos']
                    dis = np.linalg.norm(np.array(door_pos) - np.array(refer_pos))
                    if dis < min_dis:
                        min_dis = dis
                        matched_door = refer_door
            if matched_door is None:
                for refer_door in referenced_doors:
                    refer_pos = refer_door['close_pos']
                    dis = np.linalg.norm(np.array(door_pos) - np.array(refer_pos))
                    if dis < min_dis:
                        min_dis = dis
                        matched_door = refer_door
            if min_dis > 0.1:
                matched_door = None
            # print(min_dis)
            if matched_door is not None:
                door['obj_info']['rot'] = [0.0, np.sin(matched_door['close_ang'] / 2.), 0.0, np.cos(matched_door['close_ang'] / 2.)]

            if 'Kitchen' in [ROOM_BUILD_TYPE[door['target_room_type']], room_type] or \
                    'Balcony' in [ROOM_BUILD_TYPE[door['target_room_type']], room_type]:
                # if 'Balcony' in door_connect_info:
                #     print(door.door_length)
                if door['length'] < 1.:
                    door_aspect = 0
                elif door['length'] < 2.4:
                    door_aspect = 1
                else:
                    door_aspect = 2
                valid_door_list = []
                suited_err = 1e7
                suited_door = None
                prior, backup = (
                    hard_type['door']['Kitchen'],
                    hard_type['door']['Balcony']) if 'Kitchen' in [ROOM_BUILD_TYPE[door['target_room_type']], room_type] else (
                    hard_type['door']['Balcony'], hard_type['door']['Kitchen'])
                for door_info in prior:
                    length, height, _ = door_info['size']
                    if length < 1.:
                        lib_door_aspect = 0
                    elif length < 2.4:
                        lib_door_aspect = 1
                    else:
                        lib_door_aspect = 2
                    if lib_door_aspect == door_aspect:
                        valid_door_list.append(door_info)
                    else:
                        if abs(door['length'] - length) < suited_err and lib_door_aspect > 0:
                            suited_err = abs(door['length'] - length)
                            suited_door = door_info

                if len(valid_door_list) == 0:
                    for door_info in hard_type['door']['sliding door'] + hard_type['door']['swing door']:
                        length, height, _ = door_info['size']
                        r = length / height
                        if length < 1.:
                            lib_door_aspect = 0
                        elif length < 2.4:
                            lib_door_aspect = 1
                        else:
                            lib_door_aspect = 2
                        if lib_door_aspect == door_aspect:
                            valid_door_list.append(door_info)
                        else:
                            if abs(door['length'] - length) < suited_err and lib_door_aspect > 0:
                                suited_err = abs(door['length'] - length)
                                suited_door = door_info
                    if len(valid_door_list) == 0:
                        for door_info in backup:
                            length, _, _ = door_info['size']
                            if length < 1.:
                                lib_door_aspect = 0
                            elif length < 2.4:
                                lib_door_aspect = 1
                            else:
                                lib_door_aspect = 2
                            if lib_door_aspect == door_aspect:
                                valid_door_list.append(door_info)
                            else:
                                if abs(door['length'] - length) < suited_err and lib_door_aspect > 0:
                                    suited_err = abs(door['length'] - length)
                                    suited_door = door_info
                if len(valid_door_list) == 0:
                    # valid_door_list = back_up_set
                    choosen_door = suited_door
                else:
                    choosen_door = np.random.choice(valid_door_list)
            # fix by lizuojun 2021.05.30
            elif door['target_room_type'] == '':
                entry_doors = hard_type['door']['entry']
                valid_door_list = []
                for door_info in entry_doors:
                    length, _, height = door_info['size']
                    if (length < height) == (door['length'] < door['height']):
                        valid_door_list.append(door_info)
                if len(valid_door_list) == 0:
                    valid_door_list = entry_doors
                choosen_door = np.random.choice(valid_door_list)
            elif ROOM_BUILD_TYPE[door['target_room_type']] == '':
                entry_doors = hard_type['door']['entry']
                valid_door_list = []
                for door_info in entry_doors:
                    length, _, height = door_info['size']
                    if (length < height) == (door['length'] < door['height']):
                        valid_door_list.append(door_info)
                if len(valid_door_list) == 0:
                    valid_door_list = entry_doors
                choosen_door = np.random.choice(valid_door_list)
            else:
                if door['length'] < 1.:
                    if 'Bathroom' in [ROOM_BUILD_TYPE[door['target_room_type']], room_type]:
                        bathroom_doors = hard_type['door']['Bathroom']
                        choosen_door = np.random.choice(bathroom_doors)
                    elif 'MasterBedroom' in [ROOM_BUILD_TYPE[door['target_room_type']], room_type]:
                        bedroom_doors = hard_type['door']['MasterBedroom']
                        choosen_door = np.random.choice(bedroom_doors)

                    else:
                        bedroom_doors = hard_type['door']['MasterBedroom']
                        choosen_door = np.random.choice(bedroom_doors)
                else:
                    suited_err = 1e7
                    choosen_door = None
                    for door_info in hard_type['door']['sliding door']:
                        length, _, _ = door_info['size']
                        if abs(length - door['length']) < suited_err:
                            choosen_door = door_info
                            suited_err = abs(length - door['length'])

            door['obj_info']['jid'] = choosen_door['jid']
            door['obj_info']['contentType'] = choosen_door['contentType']
            door['obj_info']['scale'] = [door['length'] / choosen_door['size'][0],
                                         door['height'] / choosen_door['size'][1],
                                         min(0.25, choosen_door['size'][2]) / choosen_door['size'][2]]
            if 'pocket' in choosen_door:
                door['material']['main'] = choosen_door['pocket']
            if sell_info is not None and choosen_door['jid'] not in sell_info:
                sell_info[choosen_door['jid']] = {'role': 'Door', 'group': 'Wall'}

        for window in room_info['Window']:
            if room_info['id'] in hard_for_room['window']:
                win_hard_type = hard_for_room['window'][room_info['id']]
            else:
                win_hard_type = None
            if room_info['type'] in hard_type['window']:
                default_win_hard_type = hard_type['window'][room_info['type']]
            elif room_type in hard_type['window']:
                default_win_hard_type = hard_type['window'][room_type]
            else:
                default_win_hard_type = hard_type['window']['All']
            if win_hard_type is None:
                win_hard_type = default_win_hard_type
            wall_offset = 0.
            if window['type'] == 'FrenchWindow' and window['length'] > 2.5:
                suited_err = 1e7
                if len(win_hard_type['FrenchWindow']) > 0:
                    for win in win_hard_type['FrenchWindow']:
                        if abs(win['size'][0] - window['length']) < suited_err:
                            choosen_window = win
                            suited_err = abs(win['size'][0] - window['length'])
                else:
                    for win in default_win_hard_type['FrenchWindow']:
                        if abs(win['size'][0] - window['length']) < suited_err:
                            choosen_window = win
                            suited_err = abs(win['size'][0] - window['length'])
                # choosen_window = np.random.choice(win_hard_type['Balcony'])
            elif window['type'] == 'FrenchWindow' and window['length'] > 1.12:
                if len(win_hard_type['FrenchWindow']) > 0:
                    choosen_window = np.random.choice(win_hard_type['FrenchWindow'])
                else:
                    choosen_window = np.random.choice(default_win_hard_type['FrenchWindow'])
            elif window['type'] == 'BayWindow' and window['length'] > 2. and len(
                    win_hard_type['BayWindow']) > 0:
                if len(win_hard_type['BayWindow']) > 0:
                    choosen_window = np.random.choice(win_hard_type['BayWindow'])
                else:
                    choosen_window = np.random.choice(default_win_hard_type['BayWindow'])
                wall_offset = choosen_window['wall_offset'] / 1000. if 'wall_offset' in choosen_window else 0.
            else:
                normal_win_list = win_hard_type['single'] + win_hard_type['double'] + win_hard_type['triple']
                suited_err = 1e7
                for win in normal_win_list:
                    if abs(win['size'][0] - window['length']) < suited_err:
                        choosen_window = win
                        suited_err = abs(win['size'][0] - window['length'])
                if suited_err > 1.:
                    normal_win_list = default_win_hard_type['single'] + default_win_hard_type['double'] + default_win_hard_type['triple']
                    for win in normal_win_list:
                        if abs(win['size'][0] - window['length']) < suited_err:
                            choosen_window = win
                            suited_err = abs(win['size'][0] - window['length'])

            window['obj_info']['jid'] = choosen_window['jid']
            window['obj_info']['contentType'] = choosen_window['contentType']
            window['obj_info']['scale'] = [window['length'] / choosen_window['size'][0],
                                           window['height'] / choosen_window['size'][1],
                                           window['depth'] / choosen_window['size'][2]]
            window['obj_info']['pos'][0] -= window['normal'][0] * wall_offset
            window['obj_info']['pos'][2] -= window['normal'][1] * wall_offset
            if 'pocket' in choosen_window:
                window['material']['main'] = choosen_window['pocket']

    def config_mat_info(self, room_info, hard_type, sell_info, hard_for_room):
        # room_type = room_info['type']
        # room_type = ROOM_BUILD_TYPE[room_info['type']]
        # if room_type == 'Balcony':
        #     room_type = 'LivingDiningRoom'
        # elif room_type == 'Library':
        #     room_type = 'MasterBedroom'
        # # elif room_type == 'KidsRoom':
        # #     room_type = 'MasterBedroom'

        wall_room_type = room_info['type'] if room_info['id'] not in self.room_sample_mat_dict else self.room_sample_mat_dict[room_info['id']]
        if wall_room_type not in hard_type['WallInner']:
            wall_room_type = ROOM_BUILD_TYPE[room_info['type']]
            if wall_room_type not in hard_type['WallInner']:
                if wall_room_type == 'Balcony':
                    wall_room_type = 'LivingDiningRoom'
                elif wall_room_type == 'Library':
                    wall_room_type = 'MasterBedroom'

        wall_mesh_mat_meeting, wall_mesh_mat_media, wall_mesh_mat_hallway = None, None, None
        wall_mesh_mat_subbed = None
        wall_mesh_mat_bed = None
        if room_info['id'] in hard_for_room['WallInner'] and len(hard_for_room['WallInner'][room_info['id']]) > 0:
            choosen_wall_mesh_mat = np.random.choice(hard_for_room['WallInner'][room_info['id']])
        else:
            choosen_wall_mesh_mat = np.random.choice(hard_type['WallInner'][wall_room_type])
        if wall_room_type in PRIME_GENERAL_WALL_ROOM_TYPES and ('Media' in choosen_wall_mesh_mat or
                                                                'SubBed' in choosen_wall_mesh_mat or
                                                                'Bed' in choosen_wall_mesh_mat):
            wall_mesh_mat_bed = choosen_wall_mesh_mat['Bed'] if 'Bed' in choosen_wall_mesh_mat else None
            wall_mesh_mat_subbed = choosen_wall_mesh_mat['SubBed'] if 'SubBed' in choosen_wall_mesh_mat else None
            wall_mesh_mat_media = choosen_wall_mesh_mat['Media'] if 'Media' in choosen_wall_mesh_mat else None
            wall_mesh_mat_general = choosen_wall_mesh_mat['general'] if 'general' in choosen_wall_mesh_mat else None

        elif ROOM_BUILD_TYPE[wall_room_type] == 'LivingDiningRoom' and ('Media' in choosen_wall_mesh_mat or
                                                                        'Meeting' in choosen_wall_mesh_mat or
                                                                        'Hallway' in choosen_wall_mesh_mat):
            wall_mesh_mat_meeting = choosen_wall_mesh_mat['Meeting'] if 'Meeting' in choosen_wall_mesh_mat else None
            wall_mesh_mat_media = choosen_wall_mesh_mat['Media'] if 'Media' in choosen_wall_mesh_mat else None
            wall_mesh_mat_hallway = choosen_wall_mesh_mat['Hallway'] if 'Hallway' in choosen_wall_mesh_mat else None
            wall_mesh_mat_general = choosen_wall_mesh_mat['general'] if 'general' in choosen_wall_mesh_mat else None
        else:
            wall_mesh_mat_subbed = None
            wall_mesh_mat_bed = None
            wall_mesh_mat_general = choosen_wall_mesh_mat

        for wall in room_info['Wall']:
            if wall_room_type in PRIME_GENERAL_WALL_ROOM_TYPES:
                if 'functional' in wall and 'PrimeBed' in wall['functional'] and wall_mesh_mat_bed is not None:
                    wall_mesh_mat = copy.deepcopy(wall_mesh_mat_bed)
                elif 'functional' in wall and 'SubPrimeBed' in wall['functional'] and wall_mesh_mat_subbed is not None:
                    wall_mesh_mat = copy.deepcopy(wall_mesh_mat_subbed)
                elif 'functional' in wall and 'Media' in wall['functional'] and wall_mesh_mat_media is not None:
                    wall_mesh_mat = copy.deepcopy(wall_mesh_mat_media)
                else:
                    wall_mesh_mat = copy.deepcopy(wall_mesh_mat_general)
                wall_length = np.linalg.norm(np.array(wall['layout_pts'][0]) - np.array(
                    wall['layout_pts'][1]))
                scale = min(1. / wall['height'] / wall_mesh_mat['uv_ratio'][2],
                            1. / wall_length / wall_mesh_mat['uv_ratio'][0])
                if 0.5 < scale < 2.:
                    wall_mesh_mat['uv_ratio'][0] *= scale
                    wall_mesh_mat['uv_ratio'][2] *= scale
                for s in wall['segments']:
                    s['material'] = {}
                    wall_mesh_mat['mesh'] = 'Wall'
                    s['material']['main'] = wall_mesh_mat
                    s['material']['seam'] = hard_type['TileGap']
                    s['material']['default'] = hard_type['Ceiling']['default']
            elif wall_room_type == 'LivingDiningRoom':
                for s in wall['segments']:
                    if 'Functional' in s and 'Media' in s['Functional'] and wall_mesh_mat_media is not None:
                        wall_mesh_mat = copy.deepcopy(wall_mesh_mat_media)
                        # print('media 材质')
                    elif 'Functional' in s and 'Meeting' in s['Functional'] and wall_mesh_mat_meeting is not None:
                        wall_mesh_mat = copy.deepcopy(wall_mesh_mat_meeting)
                        # print('meeting 材质')
                    elif 'Functional' in s and 'Hallway' in s['Functional'] and wall_mesh_mat_hallway is not None:
                        wall_mesh_mat = copy.deepcopy(wall_mesh_mat_hallway)
                        # print('hallway 材质')
                    else:
                        wall_mesh_mat = copy.deepcopy(wall_mesh_mat_general)
                    wall_mesh_mat['mesh'] = 'Wall'
                    s['material'] = {}
                    s['material']['main'] = wall_mesh_mat
                    s['material']['seam'] = hard_type['TileGap']
                    s['material']['default'] = hard_type['Ceiling']['default']

            else:
                wall_mesh_mat = copy.deepcopy(wall_mesh_mat_general)
                for s in wall['segments']:
                    s['material'] = {}
                    wall_mesh_mat['mesh'] = 'Wall'
                    s['material']['main'] = wall_mesh_mat
                    s['material']['seam'] = hard_type['TileGap']
                    s['material']['default'] = hard_type['Ceiling']['default']

        if room_info['id'] in hard_for_room['Baseboard'] and len(hard_for_room['Baseboard'][room_info['id']]) > 0:
            baseboard_mesh_mat = np.random.choice(hard_for_room['Baseboard'][room_info['id']])
        else:
            baseboard_room_type = room_info['type'] if room_info['id'] not in self.room_sample_mat_dict else \
                self.room_sample_mat_dict[room_info['id']]
            if baseboard_room_type not in hard_type['Baseboard']:
                baseboard_room_type = ROOM_BUILD_TYPE[room_info['type']]
                if baseboard_room_type not in hard_type['Baseboard']:
                    if baseboard_room_type == 'Balcony':
                        baseboard_room_type = 'LivingDiningRoom'
                    elif baseboard_room_type == 'Library':
                        baseboard_room_type = 'MasterBedroom'
            baseboard_mesh_mat = np.random.choice(hard_type['Baseboard'][baseboard_room_type])
        for baseboard in room_info['BaseBoard']:
            baseboard_mesh_mat['mesh'] = 'BaseBoard'
            baseboard['material']['main'] = baseboard_mesh_mat
            baseboard['material']['default'] = hard_type['Ceiling']['default']

        floor_room_type = room_info['type'] if room_info['id'] not in self.room_sample_mat_dict else \
        self.room_sample_mat_dict[room_info['id']]
        if floor_room_type not in hard_type['Floor']:
            floor_room_type = ROOM_BUILD_TYPE[room_info['type']]
            if floor_room_type not in hard_type['Floor']:
                if floor_room_type == 'Balcony':
                    floor_room_type = 'LivingDiningRoom'
                elif floor_room_type == 'Library':
                    floor_room_type = 'MasterBedroom'
        floor_mesh_mat = None
        for floor in room_info['Floor']:
            if room_info['id'] in hard_for_room['Floor'] and len(hard_for_room['Floor'][room_info['id']]) > 0:
                floor_mesh_mat = np.random.choice(hard_for_room['Floor'][room_info['id']])
            else:
                floor_mesh_mat = np.random.choice(hard_type['Floor'][floor_room_type])
            tile_gap_mat = hard_type['TileGap']
            floor_mesh_mat['mesh'] = 'Floor'
            tile_gap_mat['mesh'] = 'Seam'
            floor['material']['main'] = floor_mesh_mat
            floor['material']['seam'] = tile_gap_mat
            floor['material']['default'] = hard_type['Ceiling']['default']
        self.room_floor_type = floor_mesh_mat['type']

        ceiling_room_type = room_info['type'] if room_info['id'] not in self.room_sample_mat_dict else \
        self.room_sample_mat_dict[room_info['id']]
        if ceiling_room_type not in hard_type['Ceiling']:
            ceiling_room_type = ROOM_BUILD_TYPE[room_info['type']]
            if ceiling_room_type not in hard_type['Ceiling']:
                if ceiling_room_type == 'Balcony':
                    ceiling_room_type = 'LivingDiningRoom'
                elif ceiling_room_type == 'Library':
                    ceiling_room_type = 'MasterBedroom'
        if room_info['id'] in hard_for_room['Ceiling'] and len(hard_for_room['Ceiling'][room_info['id']]) > 0:
            ceiling_mesh_mat = np.random.choice(hard_for_room['Ceiling'][room_info['id']])
        else:
            ceiling_mesh_mat = np.random.choice(hard_type['Ceiling'][ceiling_room_type])
        for ceiling in room_info['Ceiling']:
            ceiling_mesh_mat['mesh'] = 'Ceiling'
            ceiling['material']['main'] = ceiling_mesh_mat
            ceiling['material']['default'] = hard_type['Ceiling']['default']

        pocket_mat = hard_type['Pocket']
        for door in room_info['Door']:
            if 'main' not in door['material']:
                pocket_mat['mesh'] = 'Pocket'
                door['material']['main'] = pocket_mat
            door['material']['floor'] = floor_mesh_mat
            door['material']['default'] = hard_type['Ceiling']['default']

        for window in room_info['Window']:
            if 'main' not in window['material']:
                window['material']['main'] = pocket_mat
            window['material']['default'] = hard_type['Ceiling']['default']
            if 'Wall' in window['related'] and 'Segment' in window['related']:
                window['material'] = room_info['Wall'][window['related']['Wall']]['segments'][window['related']['Segment']]['material']
        for customized_ceiling in room_info['CustomizedCeiling']:
            customized_ceiling['material']['main'] = hard_type['Ceiling']['default']
            customized_ceiling['material']['default'] = hard_type['Ceiling']['default']

    def config_floor_line_info(self, room_info, hard_type):
        if np.random.rand() > 0:
            return
        floor_height = 0.006
        if 'ceramic main floor' in self.room_floor_type and hard_type['style'] == 'chinese' and \
                ROOM_BUILD_TYPE[room_info['type']] == 'LivingDiningRoom':
            # ceiling corresponded
            idx = -1
            for customized_ceiling in room_info['CustomizedCeiling']:
                idx += 1
                rect = customized_ceiling['layout_pts']
                if customized_ceiling['type'] in ['living', 'dining']:
                    decorate_line_width = np.random.randint(50, 80) / 1000.
                else:
                    decorate_line_width = np.random.randint(25, 40) / 1000.
                size = np.max(rect, axis=0) - np.min(rect, axis=0)
                size = size.tolist()
                size.sort()
                double_decorate_line = (customized_ceiling['type'] in ['living', 'dining'] and size[0] >= 4. and size[1] >= 4.) or (
                        customized_ceiling['type'] == 'hallway' and size[0] >= 0.8 and size[1] >= 4.)

                shrink_scale = 0.9 if double_decorate_line else 0.8
                shrink_length = size[0] * (1. - shrink_scale)
                center = np.mean(rect, axis=0)
                scaled_outer_rect = rect - np.sign(rect - center) * shrink_length
                scaled_inner_rect = scaled_outer_rect - np.sign(rect - center) * decorate_line_width
                verts = []
                faces = []
                norms = []
                for i in range(4):
                    verts += [scaled_outer_rect[i][0], floor_height, scaled_outer_rect[i][1]]
                    verts += [scaled_inner_rect[i][0], floor_height, scaled_inner_rect[i][1]]
                    faces += [2 * i, 2 * i + 1, (2 * i + 2) % 8]
                    faces += [2 * i + 1, (2 * i + 3) % 8, (2 * i + 2) % 8]
                    norms += ([0, 1, 0, 0, 1, 0])
                if double_decorate_line:
                    shrink_length = shrink_length * shrink_scale
                    scaled_outer_rect = scaled_inner_rect - np.sign(scaled_inner_rect - center) * shrink_length
                    scaled_inner_rect = scaled_outer_rect - np.sign(scaled_inner_rect - center) * decorate_line_width
                    for i in range(4):
                        verts += [scaled_outer_rect[i][0], floor_height, scaled_outer_rect[i][1]]
                        verts += [scaled_inner_rect[i][0], floor_height, scaled_inner_rect[i][1]]
                        faces += [8 + 2 * i, 8 + 2 * i + 1, 8 + (2 * i + 2) % 8]
                        faces += [8 + 2 * i + 1, 8 + (2 * i + 3) % 8, 8 + (2 * i + 2) % 8]
                        norms += ([0, 1, 0, 0, 1, 0])
                mesh = Mesh("FloorLine", 'floorLineMesh_%d' % idx)
                mesh.build_exists_mesh(verts, norms, None, faces)
                # mesh.set_u_dir(mesh['u_dir'])
                mesh.set_face_normal(norms[:3])
                floor_line_mat = hard_type['FloorLine']
                uv_ratio = np.array(floor_line_mat['uv_ratio'])
                mesh.mat['jid'] = floor_line_mat['jid']
                mesh.mat['texture'] = floor_line_mat['texture']
                mesh.mat['color'] = floor_line_mat['color']
                mesh.build_uv(uv_ratio)

                room_info['Mesh'].append(
                    {
                        'name': mesh.uid,
                        'type': mesh.mesh_type,
                        'uv': mesh.uv,
                        'uid': mesh.uid,
                        'xyz': mesh.xyz,
                        'normals': mesh.normals,
                        'faces': mesh.faces,
                        'u_dir': mesh.u_dir,
                        'uv_norm_pt': mesh.uv_norm_pt,
                        'layout_pts': mesh.contour,
                        'material': mesh.mat,
                        'related': {
                            'CustomizedCeiling': customized_ceiling['name']
                        }
                    }
                )

    def config_bg_wall(self, room_info, hard_type, room_layout=None, hard_for_room={}):
        # if hard_type['style'] not in ['chinese', 'european']:
        #     return

        # bottom = 0.115  # same with baseboard height
        bottom = 0.  # same with baseboard height
        height = room_info['height']
        wall_depth = 0.02

        for wall in room_info['Wall']:
            if ROOM_BUILD_TYPE[room_info['type']] == 'LivingDiningRoom':
                if 'Meeting' in wall['functional'] and hard_type['meeting wall'] is not None:
                    p1 = wall['functional']['Meeting'][0]
                    p2 = wall['functional']['Meeting'][1]
                    bg_type = 'Meeting'
                    if room_info['id'] in hard_for_room['meeting wall'] and len(
                            hard_for_room['meeting wall'][room_info['id']]) > 0:
                        choosen_wall = np.random.choice(hard_for_room['meeting wall'][room_info['id']])
                    else:
                        choosen_wall = np.random.choice(hard_type['meeting wall'])
                elif 'Media' in wall['functional'] and hard_type['media wall'] is not None:
                    p1 = wall['functional']['Media'][0]
                    p2 = wall['functional']['Media'][1]
                    bg_type = 'Media'
                    if room_info['id'] in hard_for_room['media wall'] and len(
                            hard_for_room['media wall'][room_info['id']]) > 0:
                        choosen_wall = np.random.choice(hard_for_room['media wall'][room_info['id']])
                    else:
                        choosen_wall = np.random.choice(hard_type['media wall'])
                else:
                    continue
            elif ROOM_BUILD_TYPE[room_info['type']] == 'MasterBedroom' and 'PrimeBed' in wall['functional'] and hard_type['bed wall'] is not None:
                p1 = wall['functional']['PrimeBed'][0]
                p2 = wall['functional']['PrimeBed'][1]
                bg_type = 'Bed'
                if room_info['id'] in hard_for_room['bed wall'] and len(
                        hard_for_room['bed wall'][room_info['id']]) > 0:
                    choosen_wall = np.random.choice(hard_for_room['bed wall'][room_info['id']])
                else:
                    choosen_wall = np.random.choice(hard_type['bed wall'])
            else:
                continue

            length = np.linalg.norm(np.array(p2) - np.array(p1))
            if length < 2.:
                continue
            break_continue = False
            for door in room_info['Door']:
                door_line = door['layout_pts']
                door_line_cp = door_line.copy()
                v = np.array(door_line_cp[0]) - door_line_cp[1]
                v = v / np.linalg.norm(v)
                door_line_cp[0] += v * 0.05
                door_line_cp[1] -= v * 0.05
                flag, remained_edge, rm_edge = is_coincident_line([p1, p2], door_line_cp)
                if len(rm_edge) > 0:
                    if len(remained_edge) == 1:
                        p1 = remained_edge[0][0]
                        p2 = remained_edge[0][1]
                    else:
                        break_continue = True
                        break
            if break_continue:
                continue
            for win in room_info['Window']:
                win_line = win['layout_pts']
                win_line_cp = win_line.copy()
                v = np.array(win_line_cp[0]) - win_line_cp[1]
                v = v / np.linalg.norm(v)
                win_line_cp[0] += v * 0.05
                win_line_cp[1] -= v * 0.05
                flag, remained_edge, rm_edge = is_coincident_line([p1, p2], win_line_cp)
                if len(rm_edge) > 0:
                    if len(remained_edge) == 1:
                        p1 = remained_edge[0][0]
                        p2 = remained_edge[0][1]
                    else:
                        break_continue = True
                        break
            if break_continue:
                continue

            for hole in room_info['Hole']:
                hole_line = hole['layout_pts']
                hole_line_cp = hole_line.copy()
                v = np.array(hole_line_cp[0]) - hole_line_cp[1]
                v = v / np.linalg.norm(v)
                hole_line_cp[0] += v * 0.05
                hole_line_cp[1] -= v * 0.05
                flag, remained_edge, rm_edge = is_coincident_line([p1, p2], hole_line_cp)
                if len(rm_edge) > 0:
                    if len(remained_edge) == 1:
                        p1 = remained_edge[0][0]
                        p2 = remained_edge[0][1]
                    else:
                        break_continue = True
                        break
            if break_continue:
                continue
            length = np.linalg.norm(np.array(p2) - np.array(p1))
            adj_height = min(height, max(2.2, length * 0.8))
            adj_height = height
            # print(length, adj_height)

            s = choosen_wall['scale'][2] if 'scale' in choosen_wall else 1.
            back_depth = min(wall_depth, choosen_wall['size'][1] * s / 1000.)  # layout['back_depth']
            # back_depth = 0.5

            if choosen_wall['size'][1] / 1000. > 0.25:
                continue
            scale = [length / choosen_wall['size'][0] * 1000.,
                     adj_height / choosen_wall['size'][2] * 1000.,
                     back_depth / choosen_wall['size'][1] * 1000.]
            if abs(wall['normal'][0]) < 1e-3:
                wall['normal'][0] = 0
                wall['normal'][1] = np.sign(wall['normal'][1])
            if abs(wall['normal'][1]) < 1e-3:
                wall['normal'][1] = 0
                wall['normal'][0] = np.sign(wall['normal'][0])
            pos = [0.5 * (p1[0] + p2[0]) + wall['normal'][0] * (back_depth / 2. + 0.002), bottom,
                   0.5 * (p1[1] + p2[1]) + wall['normal'][1] * (back_depth / 2. + 0.002)]

            if 'bounds' in choosen_wall:
                bounds = choosen_wall['bounds']
                pos = [pos[0] - np.mean(bounds[0]), pos[1] - bounds[2][0],
                       pos[2] - np.mean(bounds[1])]

            else:
                bounds = [[0, 0], [0, 0], [0, 0]]
            ang = np.arcsin(-wall['normal'][1])
            if wall['normal'][0] < -0.001:
                ang = np.pi + ang
            ang += np.pi / 2
            choosen_wall = choosen_wall.copy()
            choosen_wall.update(
                {
                    'jid': choosen_wall['jid'],
                    'pos': pos,
                    'scale': scale,
                    'rot': [0, np.sin(ang / 2.), 0, np.cos(ang / 2.)],
                    'size': [choosen_wall['size'][0] / 10., choosen_wall['size'][2] / 10.,
                             choosen_wall['size'][1] / 10.],
                    'contentType': choosen_wall['contentType'],
                    'bounds': bounds,
                    'coords': choosen_wall['coords'] if 'coords' in choosen_wall else []
                }
            )
            room_info['BgWall'].append(
                {'name': '%s_%s_bg_wall' % (room_info['id'], bg_type),
                 'type': bg_type,
                 'back_p1': p1,
                 'back_p2': p2,
                 'length': length,
                 'height': adj_height,
                 'depth': back_depth,
                 'normal': wall['normal'],
                 'obj_info': choosen_wall
                 }
            )
            if room_layout is not None and len(room_layout) > 0:
                object_one = {
                    'jid': choosen_wall['jid'],
                    'position': pos,
                    'scale': scale,
                    'rotation': choosen_wall['rot'],
                    'size': choosen_wall['size']
                }
                correct_room_move(room_layout, object_one)

    @staticmethod
    def euler_to_quaternion(yaw, pitch, roll):
        qx = np.sin(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) - np.cos(roll / 2) * np.sin(pitch / 2) * np.sin(
            yaw / 2)
        qy = np.cos(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.cos(pitch / 2) * np.sin(
            yaw / 2)
        qz = np.cos(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2) - np.sin(roll / 2) * np.sin(pitch / 2) * np.cos(
            yaw / 2)
        qw = np.cos(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.sin(pitch / 2) * np.sin(
            yaw / 2)

        return [qx, qy, qz, qw]

    def get_content_type(self, auto_add):
        try:
            from Furniture.furniture import get_furniture_data

            for cate in self.HARD_LIBS.keys():
                if cate == 'tv_paint':
                    continue
                for cate2 in self.HARD_LIBS[cate].keys():
                    for i, v in enumerate(self.HARD_LIBS[cate][cate2]):
                        jid = v['jid']
                        obj_type, obj_style_en, obj_size = get_furniture_data(jid, '', False, False)
                        if 'contentType' not in self.HARD_LIBS[cate][cate2][i] or \
                                self.HARD_LIBS[cate][cate2][i]['contentType'] != obj_type:
                            self.HARD_LIBS[cate][cate2][i]['contentType'] = obj_type
                        print(obj_type)
            print('done')
            if auto_add:
                with open(self.hard_lib_file, 'w') as f:
                    json.dump(self.HARD_LIBS, f, indent='  ')

        except Exception as e:
            print(e)
            pass


# def transfer_light_for_scene_json(outdoor_scene, scene_json):
#     outdoor_scene_list = {
#         'daytime': ['ljz_day', 'sea_sky', 'northern_snow'],
#         "dusk": ['dusk', 'shenzhen_night', 'peoples_square_night'],  # [17-19]
#         "night": ['ljz_night', 'moonlit_golf', 'wuhan_night']  # [20-5]
#     }
#
#     if outdoor_scene in outdoor_scene_list['daytime']:
#         cur_time = 'daytime'
#     elif outdoor_scene in outdoor_scene_list['dusk']:
#         cur_time = 'dusk'
#     elif outdoor_scene in outdoor_scene_list['night']:
#         cur_time = 'night'
#     else:
#         raise Exception('error: invalid outdoor scene argument')
#
#     scene_json["zncz_outdoor"] = outdoor_scene
#
#     for i, light in enumerate(scene_json['lights']):
#         if light['nodeType'] == 'VraySun':
#             if len(light['full_day_param']) == 0:
#                 continue
#             scene_json['lights'][i]['src_position'] = light['full_day_param'][cur_time]['sun_src_pos']
#             scene_json['lights'][i]['target_position'] = light['full_day_param'][cur_time]['sun_target_pos']
#             scene_json['lights'][i]['enabled'] = light['full_day_param'][cur_time]['enable_sun']
#             scene_json['lights'][i]['filter_Color'] = light['full_day_param'][cur_time]['sun_color']
#         elif light['nodeType'] == 'VrayLightDome':
#             if len(light['full_day_param']) == 0:
#                 continue
#             scene_json['lights'][i]['textureTemperature'] = light['full_day_param'][cur_time]['dome_temperature']
#         elif light['nodeType'] == 'VRayLight' and light['type'] == 0:
#             if len(light['full_day_param']) == 0:
#                 continue
#             scene_json['lights'][i]['color_temperature'] = light['full_day_param'][cur_time]['temperature']
#             scene_json['lights'][i]['multiplier'] = light['full_day_param'][cur_time]['intensity']
#         elif light['nodeType'] == 'VRayIES':
#             if len(light['full_day_param']) == 0:
#                 continue
#             scene_json['lights'][i]['temperature'] = light['full_day_param'][cur_time]['temperature']
#             scene_json['lights'][i]['multiplier'] = light['full_day_param'][cur_time]['intensity']
#             scene_json['lights'][i]['power'] = light['full_day_param'][cur_time]['intensity']
#         elif light['nodeType'] == 'FurnitureLight':
#             if len(light['full_day_param']) == 0:
#                 continue
#             scene_json['lights'][i]['temperature'] = light['full_day_param'][cur_time]['temperature']
#             scene_json['lights'][i]['intensity'] = light['full_day_param'][cur_time]['intensity']
#         elif light['nodeType'] == 'VRayLight' and light['type'] == 3:
#             if len(light['full_day_param']) == 0:
#                 continue
#             scene_json['lights'][i]['temperature'] = light['full_day_param'][cur_time]['temperature']
#             scene_json['lights'][i]['multiplier'] = light['full_day_param'][cur_time]['intensity']
#         else:
#             print('ignored light type: %s' % light)
#
#     return scene_json
#
#
# def add_user_paint_to_scene_json(user_specified_paint_list, scene_json_in):
#     offline_paint_list = [
#         {
#             'jid': '532875b8-8e63-4f8b-9f70-cc73f20c79c3',
#             'size': [80, 80, 3.5]
#         },
#         {
#             'jid': '35170c2d-540e-412c-ba9c-9c7d261eb5b2',
#             'size': [93.9522, 124.939, 5]
#         },
#         {
#             'jid': 'e70dbcf9-076c-407b-80cc-47f44a2e2e56',
#             'size': [149.236, 109.777, 2.5]
#         },
#
#     ]
#     scene_json = copy.deepcopy(scene_json_in)
#     paint_uid_list = []
#     jid_dict = {}
#     for fur in scene_json['furniture']:
#         if fur['title'] == "art/art - wall-attached":
#             paint_uid_list.append(fur['uid'])
#             jid_dict[fur['uid']] = fur['jid']
#
#     paint_room_list = []
#     for room in scene_json['scene']['room']:
#         if room['type'] in ['MasterBedroom', 'LivingDiningRoom']:
#             for child in room['children']:
#                 if child['ref'] in paint_uid_list:
#                     paint_room_list.append([room['instanceid'], child])
#
#     if len(paint_room_list) == 0:
#         return scene_json
#     if len(user_specified_paint_list) == 1:
#         choosen_paints = [i for i in paint_room_list if 'LivingDiningRoom' in i[0]]
#         if len(choosen_paints) == 0:
#             choosen_paints = [i for i in paint_room_list if 'MasterBedroom' in i[0]]
#         choosen_paints.sort(key=lambda x: -x[1]['size'][0] * x[1]['size'][1] * x[1]['scale'][0] * x[1]['scale'][1])
#         choosen_paints = [choosen_paints[0 % (len(choosen_paints))]]
#     else:  # len(user_specified_paint_list) == 2
#         user_specified_paint_list = user_specified_paint_list[:2]
#
#         choosen_paints_living = [i for i in paint_room_list if 'LivingDiningRoom' in i[0]]
#         choosen_paints_living.sort(key=lambda x: -x[1]['size'][0] * x[1]['size'][1] * x[1]['scale'][0] * x[1]['scale'][1])
#         choosen_paints_bedroom = [i for i in paint_room_list if 'MasterBedroom' in i[0]]
#         choosen_paints_bedroom.sort(key=lambda x: -x[1]['size'][0] * x[1]['size'][1] * x[1]['scale'][0] * x[1]['scale'][1])
#         if len(choosen_paints_living) > 0 and len(choosen_paints_bedroom) > 0:
#             choosen_paints = [choosen_paints_living[0 % (len(choosen_paints_living))],
#                               choosen_paints_bedroom[0 % (len(choosen_paints_bedroom))]]
#         elif len(choosen_paints_living) == 0:
#             if len(choosen_paints_bedroom) >= 2:
#                 choosen_paints = [choosen_paints_bedroom[0 % (len(choosen_paints_bedroom))],
#                                   choosen_paints_bedroom[1 % (len(choosen_paints_bedroom))]]
#             else:
#                 choosen_paints = [choosen_paints_bedroom[0 % (len(choosen_paints_bedroom))]]
#         else:
#             if len(choosen_paints_living) >= 2:
#                 choosen_paints = [choosen_paints_living[0 % (len(choosen_paints_living))],
#                                   choosen_paints_living[1 % (len(choosen_paints_living))]]
#             else:
#                 choosen_paints = [choosen_paints_living[0 % (len(choosen_paints_living))]]
#
#     for i in range(len(choosen_paints)):
#         paint_url = user_specified_paint_list[i]
#
#         try:
#             re = requests.get(paint_url)
#             re.raise_for_status()
#         except Exception as e:
#             print('download user\'s image error:', e)
#             return scene_json
#         image = Image.open(BytesIO(re.content))
#         user_image_size = image.size
#
#         ratio = user_image_size[0] / user_image_size[1]
#         if ratio < 0.8:
#             offline_paint = offline_paint_list[1]
#         elif ratio < 1.2:
#             offline_paint = offline_paint_list[0]
#         else:
#             offline_paint = offline_paint_list[2]
#         room_id, obj = choosen_paints[i]
#
#         size = obj['size']
#         area_scale = obj['scale'][0] * size[0] * obj['scale'][1] * size[1] / offline_paint['size'][0] / offline_paint['size'][1]
#         s = (user_image_size[0] / user_image_size[1]) / (offline_paint['size'][0] / offline_paint['size'][1])
#         scale = [np.sqrt(s), 1. / np.sqrt(s), 1]
#         scale = np.array(scale) * area_scale
#         obj['scale'] = scale.tolist()
#         size_s = scale * np.array(offline_paint['size']) / 100.
#         if obj['pos'][1] + size_s[1] > 2.2:
#             add_scale = (2.2 - obj['pos'][1]) / size_s[1]
#             scale = scale * add_scale
#             obj['scale'] = scale.tolist()
#             size_s = scale * np.array(offline_paint['size']) / 100.
#
#         pos = obj['pos']
#         rot = obj['rot']
#         paint_scale = 0.98
#         mesh_pts = [[size_s[0] * paint_scale / 2., (1 - paint_scale) / 2. * size_s[1], size_s[2] / 2. + 0.003],
#                     [-size_s[0] * paint_scale / 2., (1 - paint_scale) / 2. * size_s[1], size_s[2] / 2. + 0.003],
#                     [-size_s[0] * paint_scale / 2., size_s[1] * (1. + paint_scale) * 0.5, size_s[2] / 2. + 0.003],
#                     [size_s[0] * paint_scale / 2., size_s[1] * (1. + paint_scale) * 0.5, size_s[2] / 2. + 0.003]]
#         r = R.from_quat(rot)
#         mesh_pts = r.apply(mesh_pts)
#         mesh_pts = np.array(mesh_pts) + np.array(pos)
#         normal = r.apply([0, 0, 1])
#
#         mesh = Mesh('UserArt', 'userArt_%d' % i)
#         mesh.build_mesh(mesh_pts.tolist(), normal.tolist())
#         mesh.mat['jid'] = ''
#         mesh.mat['texture'] = paint_url
#         mesh.mat['color'] = [255, 255, 255, 255]
#         u_dir = -mesh_pts[0] + mesh_pts[1]
#         u_dir = u_dir / np.linalg.norm(u_dir)
#         mesh.set_u_dir(u_dir)
#         mesh.build_uv([1. / size_s[0] / paint_scale, 0, 1. / size_s[1] / paint_scale, 0])
#         mesh_scheme = {
#                     "jid": "",
#                     "uid": mesh.uid,
#                     'xyz': mesh.xyz,
#                     'normal': mesh.normals,
#                     'uv': mesh.uv,
#                     'faces': mesh.faces,
#                     'material': mesh.uid + '_material',
#                     'type': mesh.mesh_type
#                 }
#         scene_json['mesh'].append(mesh_scheme)
#         scene_json['material'].append(mesh.mat)
#         instance = {"pos": [0, 0, 0], "rot": [0, 0, 0, 1], "scale": [1., 1., 1.], 'ref': mesh.uid,
#                     'instanceid': str(1000000+i)}
#         for room_ind in range(len(scene_json['scene']['room'])):
#             if scene_json['scene']['room'][room_ind]['instanceid'] == room_id:
#                 scene_json['scene']['room'][room_ind]['children'].append(instance)
#
#         uid = "%d/model" % (400000+i)
#
#         scene_json['furniture'].append(
#                                         {
#                                             "jid": offline_paint['jid'],
#                                             "uid": uid,
#                                             "title": "art/art - wall-attached-user_specified",
#                                             "type": "standard"
#                                         }
#         )
#         an_id = 0
#         len_anchor = len(scene_json['zncz_anchor'][room_id])
#         for _ in range(len_anchor):
#             if scene_json['zncz_anchor'][room_id][an_id]['jid'] == offline_paint['jid']:
#                 scene_json['zncz_anchor'][room_id].pop(an_id)
#             else:
#                 an_id += 1
#
#         an_id = 0
#         len_anchor = len(scene_json['zncz_soft_sell'])
#         for _ in range(len_anchor):
#             if scene_json['zncz_soft_sell'][an_id]['jid'] == jid_dict[obj['ref']]:
#                 scene_json['zncz_soft_sell'].pop(an_id)
#             else:
#                 an_id += 1
#
#         obj['ref'] = uid
#     return scene_json
#
#
# def add_user_tv_char_to_scene_json(outdoor_scene, location, user_char, scene_json_in):
#     scene_json = copy.deepcopy(scene_json_in)
#     tv_uid_list = []
#     tv_jid_dict = {}
#     for fur in scene_json['furniture']:
#         if fur['title'] in ['electronics/TV - wall-attached', 'electronics/TV - on top of others']:
#             tv_uid_list.append(fur['uid'])
#             tv_jid_dict[fur['uid']] = fur['jid']
#
#     tv_room_list = []
#     for room in scene_json['scene']['room']:
#         if room['type'] in ['MasterBedroom', 'LivingDiningRoom']:
#             for child in room['children']:
#                 if child['ref'] in tv_uid_list:
#                     tv_room_list.append((room['instanceid'], child))
#
#     if len(tv_room_list) == 0:
#         return scene_json
#     chosen_tv_list = [i for i in tv_room_list if 'LivingDiningRoom' in i[0]]
#     if len(chosen_tv_list) == 0:
#         chosen_tv_list = [i for i in tv_room_list if 'MasterBedroom' in i[0]]
#     chosen_tv_list.sort(key=lambda x: -x[1]['size'][0] * x[1]['size'][1] * x[1]['scale'][0] * x[1]['scale'][1])
#     room_id, chosen_tv = chosen_tv_list[0]
#
#     hard = HardLib()
#     query_tv = None
#     for tv_ins in hard.HARD_LIBS['tv_paint']:
#         if tv_jid_dict[chosen_tv['ref']] == tv_ins['jid']:
#             query_tv = tv_ins
#             break
#     if query_tv is None:
#         print('invalid tv', chosen_tv)
#         return scene_json
#
#     pts = query_tv['pts']
#     bg_img_path = os.path.join(os.path.dirname(__file__), 'assets/%s.png' % outdoor_scene)
#     screen_size = (np.array(pts[2]) - np.array(pts[0])) * np.array(chosen_tv['scale']) / 100.
#     font_path = os.path.join(os.path.dirname(__file__), 'assets/simsun.ttc')
#     city = '地球' if location == '' else location
#     combined_img = generate_img_ui(screen_size, bg_img_path, font_path, city, user_char)
#     start_base = round(time.time() * 1000)
#     start_base_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, str(start_base))
#     upload_img_path = 'zncz/edit/%s/%s_tv.png' % (time.strftime('%Y-%m-%d'), str(start_base_uuid))
#     bucket = 'ihome-alg-layout'
#     oss_upload_byte(upload_img_path, combined_img, bucket)
#
#     testure_url = 'https://%s.oss-cn-hangzhou.aliyuncs.com/%s' % (bucket, upload_img_path)
#
#     mesh_pts = np.array(pts) * np.array(chosen_tv['scale']) / 100. + np.array([0, 0, 0.005])
#     pos = chosen_tv['pos']
#     rot = chosen_tv['rot']
#     r = R.from_quat(rot)
#     mesh_pts = r.apply(mesh_pts)
#     mesh_pts = np.array(mesh_pts) + np.array(pos)
#     normal = r.apply([0, 0, 1])
#
#     mesh = Mesh('UserTV', 'userTV')
#     mesh.build_mesh(mesh_pts.tolist(), normal.tolist())
#     mesh.mat['jid'] = ''
#     mesh.mat['texture'] = testure_url
#     mesh.mat['color'] = [255, 255, 255, 255]
#     u_dir = mesh_pts[0] - mesh_pts[-1]
#     u_dir = u_dir / np.linalg.norm(u_dir)
#     mesh.set_u_dir(u_dir)
#     mesh.build_uv([1. / screen_size[0], 0, 1. / screen_size[1], 0])
#
#     mesh_scheme = {
#                 "jid": "",
#                 "uid": mesh.uid,
#                 'xyz': mesh.xyz,
#                 'normal': mesh.normals,
#                 'uv': mesh.uv,
#                 'faces': mesh.faces,
#                 'material': mesh.uid + '_material',
#                 'type': mesh.mesh_type
#             }
#     scene_json['mesh'].append(mesh_scheme)
#     scene_json['material'].append(mesh.mat)
#     instance = {"pos": [0, 0, 0], "rot": [0, 0, 0, 1], "scale": [1., 1., 1.], 'ref': mesh.uid,
#                 'instanceid': str(2000000)}
#     for room_ind in range(len(scene_json['scene']['room'])):
#         if scene_json['scene']['room'][room_ind]['instanceid'] == room_id:
#             scene_json['scene']['room'][room_ind]['children'].append(instance)
#     return scene_json


if __name__ == '__main__':
    hard_lib = HardLib()
    # hard_lib.determine_mat_texture_postfix('./__hard_lib.json', True)
    hard_lib.get_content_type(False)
    # with open('/Users/liqing.zhc/5f9cad2b-552f-306f-b431-56f1c9f8d018.json', 'r') as f:
    #     scene_json = json.load(f)
    #     outdoor_scene = transfer_light_for_scene_json('dusk', scene_json)
    #     user_paint_scene = add_user_paint_to_scene_json(['https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com/zncz/layout/2020-11-28/1606538109129eEUdFqUDn87dT1bywDUd.png'],
    #                                                     scene_json)
    #     tv_char_scene = add_user_tv_char_to_scene_json('dusk', '杭州', '扎比较好新的技术帮唱嘉宾',scene_json)
    #
    #     with open('./outdoor_scene.json', 'w') as f:
    #         json.dump(scene_json, f)
    #
    #     with open('./user_paint_scene.json', 'w') as f:
    #         json.dump(user_paint_scene, f)
    #     with open('./tv_char_scene.json', 'w') as f:
    #         json.dump(tv_char_scene, f)