import os
import numpy as np
# from tqdm import tqdm
import random
import copy
import json
import requests
from PIL import Image
import io
from ..libs.recon_hard_lib import HardLib
from ..Base.recon_params import PRIME_GENERAL_WALL_ROOM_TYPES, ROOM_BUILD_TYPE
from Furniture.materials import get_material_feature


class SampleRooms:
    def __init__(self, sample_rooms=None, hard_lib=None, white_list=True):
        if sample_rooms is not None:
            self.SAMPLE_ROOMS = sample_rooms
        else:
            self.SAMPLE_ROOMS = json.load(open(os.path.join(os.path.dirname(__file__), 'sample_rooms.json'), 'rb'), encoding='utf-8')
        if hard_lib is not None:
            self.hard_lib = hard_lib
        else:
            self.hard_lib = HardLib()

        # white_list_file_path = os.path.join(os.path.dirname(__file__), 'hs_support_list.txt')
        # if white_list:
        #     if os.path.exists(white_list_file_path):
        #         self.white_list = json.load(open(white_list_file_path, 'r'))
        #     else:
        #         self.white_list = None
        # else:
        self.white_list = white_list
        self.similar_hard = None
        self.types = ['LivingDiningRoom', 'MasterBedroom', 'Bathroom', 'Balcony', 'Kitchen']

        # check material
        styles = ['chinese', 'nordic', 'modern', 'european']
        mats = ['wall', 'floor', 'baseboard', 'FloorLine', 'TileGap']
        for style in styles:
            for config in self.SAMPLE_ROOMS[style]:
                for mat in mats:
                    if isinstance(config[mat], list):
                        valid_jids = []
                        for jid in config[mat]:
                            attribute = self.hard_lib.get_jid_ins('tiles', jid)
                            if attribute is None:
                                continue
                            else:
                                if attribute[0]['texture_url'] != '':
                                    valid_jids.append(jid)
                                # else:
                                #     print(jid)
                        if len(valid_jids) != 0:
                            config[mat] = valid_jids
                    elif isinstance(config[mat], dict):
                        for k, v in config[mat].items():
                            valid_jids = []
                            for jid in v:
                                attribute = self.hard_lib.get_jid_ins('tiles', jid)
                                if attribute is None:
                                    continue
                                else:
                                    if attribute[0]['texture_url'] != '':
                                        valid_jids.append(jid)
                                    # else:
                                    #     print(jid)
                            if len(valid_jids) != 0:
                                config[mat][k] = valid_jids
        # print(self.SAMPLE_ROOMS)

    # def add_to_white_list(self, jids):
    #     if self.white_list is not None:
    #         self.white_list += jids

    def get_hard_config(self, style, rand_style_hard, kids_room_hard_type, cabinet):
        ceiling_mat = {'code': 1,
                                    'texture': '',
                                    "contentType": [
                                        "material",
                                        "paint"
                                    ],
                                    'jid': '173bbbc1-6a51-4505-8322-6ff3a71e12c3',
                                    'uv_ratio': [1., 0., 1.0, 0.],
                                    'colorMode': 'color',
                                    'color': [248, 249, 251, 255]}
        baseboard_mat = {'code': 1,
                         'texture': 'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/%s/pocket_tex.jpg' %
                                    rand_style_hard['baseboard'][0],
                         'jid': rand_style_hard['baseboard'][0],
                         'uv_ratio': [1., 0., 1., 0.],
                         'colorMode': 'texture',
                         'color': [255, 255, 255, 255]}
        if kids_room_hard_type['prime wall'] != '':
            kids_prime_wall = self.hard_lib.get_material('tiles', jid=kids_room_hard_type['prime wall'])
        else:
            kids_prime_wall = None
        hard_default = {'area': '', 'style': style,
                        'Floor': {
                            'LivingDiningRoom': [self.hard_lib.get_material('tiles', jid=i) for i in
                                                 rand_style_hard['floor']['LivingDiningRoom']],
                            'MasterBedroom': [self.hard_lib.get_material('tiles', jid=i) for i in
                                              rand_style_hard['floor']['MasterBedroom']],
                            'Bathroom': [self.hard_lib.get_material('tiles', jid=i) for i in
                                         rand_style_hard['floor']['Bathroom']],
                            'Kitchen': [self.hard_lib.get_material('tiles', jid=i) for i in
                                        rand_style_hard['floor']['Kitchen']],
                            'KidsRoom': [self.hard_lib.get_material('tiles', jid=kids_room_hard_type['floor'])]
                        },
                        'WallInner': {
                            'LivingDiningRoom': [self.hard_lib.get_material('tiles', jid=i) for i in
                                                 rand_style_hard['wall']['LivingDiningRoom']],
                            'MasterBedroom': [self.hard_lib.get_material('tiles', jid=i) for i in
                                              rand_style_hard['wall']['MasterBedroom']],
                            'Bathroom': [self.hard_lib.get_material('tiles', jid=i) for i in
                                         rand_style_hard['wall']['Bathroom']],
                            'Kitchen': [self.hard_lib.get_material('tiles', jid=i) for i in
                                        rand_style_hard['wall']['Kitchen']],
                            'KidsRoom': [{
                                'general': self.hard_lib.get_material('tiles', jid=kids_room_hard_type['general wall']),
                                'Bed': None if kids_room_hard_type['prime wall'] == '' else kids_prime_wall,
                                'SubBed': None if not kids_room_hard_type['subprime'] else kids_prime_wall

                            }],
                        },
                        'door': {
                            'entry': [self.hard_lib.get_door(jid=i) for i in rand_style_hard['door']['entry']],
                            'MasterBedroom': [self.hard_lib.get_door(jid=i) for i in
                                              rand_style_hard['door']['MasterBedroom']],
                            'Balcony': [self.hard_lib.get_door(jid=i) for i in rand_style_hard['door']['Balcony']],
                            'Kitchen': [self.hard_lib.get_door(jid=i) for i in rand_style_hard['door']['Kitchen']],
                            'Bathroom': [self.hard_lib.get_door(jid=i) for i in rand_style_hard['door']['Bathroom']],
                            'sliding door': [self.hard_lib.get_door(jid=i) for i in
                                             rand_style_hard['door']['sliding door']],

                        },
                        'window': {
                            'FrenchWindow': [self.hard_lib.get_window(jid=i) for i in rand_style_hard['window']['Balcony']],
                            # 'MasterBedroom': [self.hard_lib.get_window(jid=i) for i in rand_style_hard['window']['MasterBedroom']],
                            'BayWindow': [self.hard_lib.get_window(types='Bay window') for _ in range(5)],
                            'single': [self.hard_lib.get_window(jid=i) for i in rand_style_hard['window']['single']],
                            'double': [self.hard_lib.get_window(jid=i) for i in rand_style_hard['window']['double']],
                            'triple': [self.hard_lib.get_window(jid=i) for i in rand_style_hard['window']['triple']],

                        },
                        'customizedCeiling': {
                            'LivingDiningRoom': [self.hard_lib.get_jid_ins('ceiling', i)[0] for i in
                                                 rand_style_hard['ceiling']],
                            'MasterBedroom': [self.hard_lib.get_jid_ins('ceiling', i)[0] for i in
                                              self.SAMPLE_ROOMS['nordic'][0]['ceiling']],

                        },

                        'Ceiling': {
                            'LivingDiningRoom': [ceiling_mat],
                            'MasterBedroom': [ceiling_mat],
                            'Bathroom': [ceiling_mat],
                            'Kitchen': [ceiling_mat],
                            'KidsRoom': [ceiling_mat],
                            'default': ceiling_mat
                        },
                        'CustomizedFeatureWall': {'code': 1,
                                                  "contentType": [
                                                      "material",
                                                      "paint"
                                                  ],
                                                  'texture': 'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/8e8f0b9a-2967-44c3-99dd-1a1532b74697/wallfloor.png',
                                                  'jid': '8e8f0b9a-2967-44c3-99dd-1a1532b74697',
                                                  'uv_ratio': [0.5, 0., 0.5, 0.],
                                                  'colorMode': 'texture',
                                                  'color': [255, 255, 255, 255]},
                        'Baseboard': {
                            'LivingDiningRoom': [baseboard_mat],
                            'MasterBedroom': [baseboard_mat],
                            'Bathroom': [baseboard_mat],
                            'Kitchen': [baseboard_mat],
                            'KidsRoom': [baseboard_mat],
                            'default': baseboard_mat
                        },
                        'Pocket': {'code': 1,
                                   'texture': 'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/%s/pocket_tex.jpg' % rand_style_hard['baseboard'][0],
                                   'jid': rand_style_hard['baseboard'][0],
                                   'uv_ratio': [1., 0., 1., 0.],
                                   'colorMode': 'texture',
                                   'color': [255, 255, 255, 255]},
                        'FloorLine': self.hard_lib.get_material('tiles',
                                                                jid=np.random.choice(rand_style_hard['FloorLine'])),
                        'TileGap': self.hard_lib.get_material('tiles', jid=np.random.choice(rand_style_hard['TileGap']))
                        if 'TileGap' in rand_style_hard else None,

                        'meeting wall': [self.hard_lib.get_jid_ins('bg wall', i)[0] for i in
                                         rand_style_hard['meeting wall']]
                        if 'meeting wall' in rand_style_hard else None,
                        'media wall': [self.hard_lib.get_jid_ins('bg wall', i)[0] for i in
                                       rand_style_hard['media wall']]
                        if 'media wall' in rand_style_hard else None,
                        'bed wall': [self.hard_lib.get_jid_ins('bg wall', i)[0] for i in rand_style_hard['bed wall']]
                        if 'bed wall' in rand_style_hard else None,

                        'kitchen': {
                            'cabinet': {
                                "sink": self.hard_lib.get_jid_ins('kitchen', cabinet['sink'])[0],
                                "floor": self.hard_lib.get_jid_ins('kitchen', cabinet['floor_cabinet'])[0],
                                "wall": self.hard_lib.get_jid_ins('kitchen', cabinet['wall_cabinet'])[0],
                            },
                            'cook': [self.hard_lib.get_jid_ins('kitchen', i)[0] for i in
                                     self.SAMPLE_ROOMS['kitchen']['cook']],
                            'range hood': [self.hard_lib.get_jid_ins('kitchen', i)[0] for i in
                                           self.SAMPLE_ROOMS['kitchen']['range hood']],
                            'fridge': [self.hard_lib.get_jid_ins('kitchen', i)[0] for i in
                                       self.SAMPLE_ROOMS['kitchen']['fridge']],
                            'pot': self.hard_lib.HARD_LIBS['kitchen']['pot'],
                            'kitchenware': self.hard_lib.HARD_LIBS['kitchen']['kitchenware'],
                            'fruit': self.hard_lib.HARD_LIBS['kitchen']['fruit'],
                            'sink bowl': self.hard_lib.HARD_LIBS['kitchen']['sink bowl'],
                            'appliances': self.hard_lib.HARD_LIBS['kitchen']['appliances'],
                            'others': self.hard_lib.HARD_LIBS['kitchen']['others'],

                            "gusset ceiling": [self.hard_lib.get_material(('kitchen', 'gusset ceiling'), index=i) for i
                                               in range(len(self.hard_lib.HARD_LIBS['kitchen']['gusset ceiling']))],
                            "gusset ceiling gap": self.hard_lib.get_material('tiles', jid=np.random.choice(
                                self.SAMPLE_ROOMS['kitchen']['gusset ceiling gap'])),
                            "light": self.hard_lib.HARD_LIBS['kitchen']['light']

                        }
                        }

        return hard_default

    def get_room_hard(self):
        return {'area': '', 'style': '',
                         'Floor': {},
                         'WallInner': {},
                         'door': {},
                         'window': {},
                         'customizedCeiling': {},
                         'Ceiling': {},
                         'Baseboard': {},
                         'Pocket': {},
                         'FloorLine': {},
                         'TileGap': {},
                         'meeting wall': {},
                         'media wall': {},
                         'bed wall': {},
                         'kitchen': {}
                         }

    def get_base_hard(self, style):
        rand_style_hard = np.random.choice(self.SAMPLE_ROOMS[style])
        # rand_style_hard = self.SAMPLE_ROOMS[style][0]
        cabinet = np.random.choice(self.SAMPLE_ROOMS['kitchen']['cabinet'])
        kids_room_hard_type = np.random.choice(self.SAMPLE_ROOMS['KidsRoom'])
        hard_default = self.get_hard_config(style, rand_style_hard, kids_room_hard_type, cabinet)

        return hard_default

    def check_white_list(self, jid):
        try:
            feat_data = get_material_feature(jid)
        except:
            feat_data = {}
        if len(feat_data) == 0:
            return True
        support = False
        if 'properties' in feat_data and 'support_mobile_scene' in feat_data['properties']:
            support = feat_data['properties']['support_mobile_scene'] == 'true'
        return support

    def get_similar_hard(self, style):
        if self.similar_hard is None:
            from LayoutDecoration.sample_room.similar_samples import SimilarHard
            self.similar_hard = SimilarHard()
        rand_style_hard = np.random.choice(self.SAMPLE_ROOMS[style])
        kids_room_hard_type = np.random.choice(self.SAMPLE_ROOMS['KidsRoom'])
        cabinet = np.random.choice(self.SAMPLE_ROOMS['kitchen']['cabinet'])

        style_hard_res = []
        self.get_dict_son(rand_style_hard, style_hard_res, [])
        self.get_dict_son(kids_room_hard_type, style_hard_res, [])

        style_hard_res = [i for i in style_hard_res if i[1][0] in ['door', 'floor', 'wall']]
        jid_list, _ = list(zip(*style_hard_res))

        jid_list = list(set(jid_list))
        similar_jid_dict = self.similar_hard.get_similar_hard_item(jid_list)
        similar_jid_list = []
        for k, v in similar_jid_dict.items():
            if len(v) != 0:
                similar_jid_dict[k] = random.choice(v)
                similar_jid_list.append(similar_jid_dict[k])
            else:
                similar_jid_dict[k] = None
        jid_attr_dict = self.similar_hard.get_jid_attribute(similar_jid_list)

        hard_default = self.get_hard_config(style, rand_style_hard, kids_room_hard_type, cabinet)

        for k, v in hard_default['Floor'].items():
            if 'ceramic' in ','.join(v['type']) or 'wooden' in ','.join(v['type']):
                similar_item_jid = similar_jid_dict[v['jid']]
                if similar_item_jid is not None:
                    hard_default['Floor'][k] = self.similar_hard.get_material(similar_item_jid,
                                                                              v['type'],
                                                                              jid_attr_dict[similar_item_jid])
                else:
                    print('lost similar item')
        for k, v in hard_default['WallInner'].items():
            if k not in ['Bathroom', 'Kitchen']:
                continue
            if 'ceramic' in ','.join(v['type']) or 'wooden' in ','.join(v['type']):
                similar_item_jid = similar_jid_dict[v['jid']]
                if similar_item_jid is not None:
                    hard_default['Floor'][k] = self.similar_hard.get_material(similar_item_jid,
                                                                              v['type'],
                                                                              jid_attr_dict[similar_item_jid])
                else:
                    print('lost similar item')
        for k, vs in hard_default['door'].items():
            for i, v in enumerate(vs):
                similar_item_jid = similar_jid_dict[v['jid']]
                if similar_item_jid is not None:
                    hard_default['door'][k][i] = self.similar_hard.get_door(similar_item_jid,
                                                                            jid_attr_dict[similar_item_jid])
                else:
                    print('lost similar item')

        return hard_default

    def get_transfer_hard(self, sample_hard, transfer_hard):
        meeting_wall, media_wall = True, True
        hard_for_room = self.get_room_hard()
        hard_for_room['self_transfer'] = {}
        content_type_list = {
            "tiles": [
                ["material", "tiles"],
                ["material", "sealant"],
                ["material", "matt tiles"],
                ["material", "marble tiles"],
                ["material", "wood grain tiles"],
                ["tiles", "ceramic main floor"],
                ["tiles", "ceramic wall"]
            ],
            "other": [
                ["material", "paint"],
                ["material", "flooring - hardwood"],
                ["material", "wallpaper"],
                ["material", "flooring - reinforced"],
        ]}
        transfer_hard_sample = {'Floor': {},
                                'WallInner': {},
                                'Door': {},
                                'Win': {},
                                'Ceiling': {},
                                'Baseboard': {},
                                'customizedCeiling': {}
                                }
        # 新旧ceiling字段分流
        for room_id, mat_dict in transfer_hard.items():
            if 'ceiling' in mat_dict and len(mat_dict['ceiling']) > 0:
                ceiling = []
                customized_ceiling = []
                for m in mat_dict['ceiling']:
                    if 'texture_url' in m:
                        ceiling.append(m)
                    else:
                        customized_ceiling.append(m)
                mat_dict['ceiling'] = ceiling
                if 'customized_ceiling' not in mat_dict:
                    mat_dict['customized_ceiling'] = customized_ceiling
                else:
                    mat_dict['customized_ceiling'] += customized_ceiling
        # 整合纹理
        for room_id, mat_dict in transfer_hard.items():
            if 'floor' in mat_dict:
                floor_mat = mat_dict['floor']
            else:
                floor_mat = []
            if 'wall' in mat_dict:
                wall_mat = mat_dict['wall']
            else:
                wall_mat = []
            if 'ceiling' in mat_dict:
                ceiling_mat = mat_dict['ceiling']
            else:
                ceiling_mat = []
            if 'baseboard' in mat_dict:
                baseboard_mat = mat_dict['baseboard']
            else:
                baseboard_mat = []
            if 'background' in mat_dict:
                bg_walls = mat_dict['background']
            else:
                bg_walls = []
            comb_floor = {}
            for floor in floor_mat:
                floor['texture_url'] = floor['texture_url'].replace('homestyler.com', 'shejijia.com')
                if 'amazonaws.com.cn' in floor['texture_url']:
                    comb_floor = {}
                    break
                if 'area' not in floor:
                    floor['area'] = 0.
                jid = floor['jid']
                if len(jid.split('-')) == 5:
                    if jid not in comb_floor:
                        comb_floor[jid] = floor
                    else:
                        comb_floor[jid]['area'] += floor['area']
                elif floor['colorMode'] == 'color':
                    if not isinstance(floor['color'], list):
                        continue
                    c = [str(color) for color in floor['color']]
                    jid = '-'.join(c)
                    if jid not in comb_floor:
                        comb_floor[jid] = floor
                    else:
                        comb_floor[jid]['area'] += floor['area']
                else:
                    jid = floor['texture_url']
                    if jid not in comb_floor:
                        comb_floor[jid] = floor
                    else:
                        comb_floor[jid]['area'] += floor['area']
            comb_wall = {}
            for wall in wall_mat:
                wall['texture_url'] = wall['texture_url'].replace('homestyler.com', 'shejijia.com')
                if 'amazonaws.com.cn' in wall['texture_url']:
                    comb_wall = {}
                    break
                if 'area' not in wall:
                    wall['area'] = 0.
                jid = wall['jid']
                if len(jid.split('-')) == 5:
                    if 'Functional' in wall:
                        jid = jid + '_Functional' + wall['Functional']
                    if jid not in comb_wall:
                        comb_wall[jid] = wall
                    else:
                        comb_wall[jid]['area'] += wall['area']
                elif wall['colorMode'] == 'color':
                    if not isinstance(wall['color'], list):
                        continue
                    c = [str(color) for color in wall['color']]
                    jid = '-'.join(c)
                    if 'Functional' in wall:
                        jid = jid + '_Functional' + wall['Functional']
                    if jid not in comb_wall:
                        comb_wall[jid] = wall
                    else:
                        comb_wall[jid]['area'] += wall['area']
                else:
                    jid = wall['texture_url']
                    if 'Functional' in wall:
                        jid = jid + '_Functional' + wall['Functional']
                    if jid not in comb_wall:
                        comb_wall[jid] = wall
                    else:
                        comb_wall[jid]['area'] += wall['area']
            comb_ceiling = {}
            for ceiling in ceiling_mat:
                ceiling['texture_url'] = ceiling['texture_url'].replace('homestyler.com', 'shejijia.com')
                if 'amazonaws.com.cn' in ceiling['texture_url']:
                    continue
                if 'area' not in ceiling:
                    ceiling['area'] = 0.
                jid = ceiling['jid']
                if len(jid.split('-')) == 5:
                    if jid not in comb_ceiling:
                        comb_ceiling[jid] = ceiling
                    else:
                        comb_ceiling[jid]['area'] += ceiling['area']
                elif ceiling['colorMode'] == 'color':
                    if not isinstance(ceiling['color'], list):
                        continue
                    c = [str(color) for color in ceiling['color']]
                    jid = '-'.join(c)
                    if jid not in comb_floor:
                        comb_ceiling[jid] = ceiling
                    else:
                        comb_ceiling[jid]['area'] += ceiling['area']
                else:
                    jid = ceiling['texture_url']
                    if jid not in comb_ceiling:
                        comb_ceiling[jid] = ceiling
                    else:
                        comb_ceiling[jid]['area'] += ceiling['area']
            comb_baseboard = {}
            for baseboard in baseboard_mat:
                baseboard['texture_url'] = baseboard['texture_url'].replace('homestyler.com', 'shejijia.com')
                if 'amazonaws.com.cn' in baseboard['texture_url']:
                    continue
                if 'area' not in baseboard:
                    baseboard['area'] = 0.
                jid = baseboard['jid']
                if len(jid.split('-')) == 5:
                    if jid not in comb_baseboard:
                        comb_baseboard[jid] = baseboard
                    else:
                        comb_baseboard[jid]['area'] += baseboard['area']
                elif baseboard['colorMode'] == 'color':
                    if not isinstance(baseboard['color'], list):
                        continue
                    c = [str(color) for color in baseboard['color']]
                    jid = '-'.join(c)
                    if jid not in comb_floor:
                        comb_baseboard[jid] = baseboard
                    else:
                        comb_baseboard[jid]['area'] += baseboard['area']
                else:
                    jid = baseboard['texture_url']
                    if jid not in comb_baseboard:
                        comb_baseboard[jid] = baseboard
                    else:
                        comb_baseboard[jid]['area'] += baseboard['area']

            comb_bg_wall = {}
            for bg_wall in bg_walls:
                if 'Functional' not in bg_wall:
                    continue
                if 'valid' in bg_wall and not bg_wall['valid']:
                    continue
                bg_wall['size'] = [bg_wall['size'][0] * 10.,
                                   bg_wall['size'][2] * 10.,
                                   bg_wall['size'][1] * 10.]
                bg_wall['jid'] = bg_wall['id']
                bg_wall['contentType'] = bg_wall['type']
                if bg_wall['Functional'] in comb_bg_wall:
                    comb_bg_wall[bg_wall['Functional']].append(bg_wall)
                else:
                    comb_bg_wall[bg_wall['Functional']] = [bg_wall]

            transfer_hard[room_id]['background'] = comb_bg_wall
            transfer_hard[room_id]['floor'] = list(comb_floor.values())
            if len(transfer_hard[room_id]['floor']) > 1:
                transfer_hard[room_id]['floor'].sort(key=lambda x: -x['area'])
            transfer_hard[room_id]['wall'] = list(comb_wall.values())
            if len(transfer_hard[room_id]['wall']) > 1:
                transfer_hard[room_id]['wall'].sort(key=lambda x: -x['area'])
            transfer_hard[room_id]['ceiling'] = list(comb_ceiling.values())
            if len(transfer_hard[room_id]['ceiling']) > 1:
                transfer_hard[room_id]['ceiling'].sort(key=lambda x: -x['area'])
            transfer_hard[room_id]['baseboard'] = list(comb_baseboard.values())
            if len(transfer_hard[room_id]['baseboard']) > 1:
                transfer_hard[room_id]['baseboard'].sort(key=lambda x: -x['area'])

        for room_id, room_hard in transfer_hard.items():
            if len(room_hard) == 0:
                continue
            room_type = room_hard['type'] if 'type' in room_hard else 'Other'
            wall_mat_list = []
            floor_mat_list = []
            ceiling_mat_list = []
            baseboard_mat_list = []
            for wall in room_hard['wall']:
                # print(wall['seam'])
                if wall['color'] is None and len(wall['texture_url']) == 0 and wall['jid'] in ['', 'generated']:
                    continue
                if wall['colorMode'] is not None:
                    if wall['colorMode'] == 'color' and wall['color'] is None:
                        continue
                    if wall['colorMode'] == 'texture' and len(wall['texture_url']) == 0 and wall['jid'] in ['', 'generated']:
                        continue
                    if wall['color'] is None:
                        wall['color'] = [255, 255, 255]
                else:
                    if len(wall['texture_url']) > 0 or wall['jid'] not in ['', 'generated']:
                        wall['colorMode'] = 'texture'
                    else:
                        wall['colorMode'] = 'color'
                if wall['color'] is None:
                    wall['color'] = [255, 255, 255]
                if type(wall['color']) is int:
                    wall['color'] = [255, 255, 255]
                # if wall['colorMode'] == 'color':
                #     wall['texture_url'] = ''
                if wall['seam'] is True or wall['seam'] in content_type_list['tiles']:
                    tree = ['tiles', 'ceramic wall']
                else:
                    tree = ['tiles', 'transfer']
                if wall['jid'] in ['', 'generated'] and len(wall['texture_url']) > 0:
                    wall['jid'] = wall['texture_url'].split('/')[-2]

                if len(wall['texture_url']) > 0 and not wall['texture_url'].startswith('https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/'):
                    wall['jid'] = ''
                if len(wall['jid'].split('-')) != 5:
                    wall['jid'] = ''
                else:
                    if self.white_list and ('support_mobile_scene' not in wall or not wall['support_mobile_scene']):
                        if not self.check_white_list(wall['jid']):
                            continue
                # print(wall['jid'])
                content_type = ''
                if 'contentType' in wall:
                    content_type = wall['contentType']
                elif isinstance(wall['seam'], list):
                    content_type = wall['seam']

                formated_mat = {
                    'code': 1,
                    "texture": wall['texture_url'],
                    "jid": wall['jid'],
                    "uv_ratio": [1. / wall['size'][0], 0, 1. / wall['size'][1], 0],
                    "color": wall['color'] + [255],
                    "colorMode": wall['colorMode'],
                    'type': tree,
                    "contentType": content_type,
                    "Functional": wall['Functional'] if "Functional" in wall else "",
                    "refs": [] if 'refs' not in wall else wall['refs']
                }
                if 'pave' in wall:
                    formated_mat['pave'] = wall['pave']
                wall_mat_list.append(formated_mat)
            for floor in room_hard['floor']:
                # print(floor['seam'])
                if floor['color'] is None and len(floor['texture_url']) == 0 and floor['jid'] in ['', 'generated']:
                    continue
                if floor['colorMode'] is not None:
                    if floor['colorMode'] == 'color' and floor['color'] is None:
                        continue
                    if floor['colorMode'] == 'texture' and len(floor['texture_url']) == 0 and floor['jid'] in ['', 'generated']:
                        continue
                    if floor['color'] is None:
                        floor['color'] = [255, 255, 255]
                else:
                    if len(floor['texture_url']) > 0 or floor['jid'] not in ['', 'generated']:
                        floor['colorMode'] = 'texture'
                    else:
                        floor['colorMode'] = 'color'
                if floor['color'] is None:
                    floor['color'] = [255, 255, 255]
                # if floor['colorMode'] == 'color':
                #     floor['texture_url'] = ''
                if floor['seam'] is True or floor['seam'] in content_type_list['tiles']:
                    tree = ['tiles', 'ceramic main floor']
                else:
                    tree = ['tiles', 'transfer']
                if floor['jid'] in ['', 'generated'] and len(floor['texture_url']) > 0:
                    floor['jid'] = floor['texture_url'].split('/')[-2]

                if len(floor['texture_url']) > 0 and not floor['texture_url'].startswith('https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/'):
                    floor['jid'] = ''
                if len(floor['jid'].split('-')) != 5:
                    floor['jid'] = ''
                else:
                    if self.white_list and ('support_mobile_scene' not in floor or not floor['support_mobile_scene']):
                        if not self.check_white_list(floor['jid']):
                            continue
                content_type = ''
                if 'contentType' in floor:
                    content_type = floor['contentType']
                elif isinstance(floor['seam'], list):
                    content_type = floor['seam']
                formated_mat = {
                    'code': 1,
                    "texture": floor['texture_url'],
                    "jid": floor['jid'],
                    "uv_ratio": [1. / floor['size'][0], 0, 1. / floor['size'][1], 0],
                    "color": floor['color'] + [255],
                    "colorMode": floor['colorMode'],
                    'type': tree,
                    "contentType": content_type,
                    "refs": [] if 'refs' not in floor else floor['refs']
                }
                if 'seam_width' in floor:
                    formated_mat['seam_width'] = floor['seam_width']
                if 'pave' in floor:
                    formated_mat['pave'] = floor['pave']
                floor_mat_list.append(formated_mat)
            for ceiling in room_hard['ceiling']:
                # print(floor['seam'])
                if ceiling['color'] is None and len(ceiling['texture_url']) == 0 and ceiling['jid'] in ['', 'generated']:
                    continue
                if ceiling['colorMode'] is not None:
                    if ceiling['colorMode'] == 'color' and ceiling['color'] is None:
                        continue
                    if ceiling['colorMode'] == 'texture' and len(ceiling['texture_url']) == 0 and ceiling['jid'] in ['', 'generated']:
                        continue
                    if ceiling['color'] is None:
                        ceiling['color'] = [255, 255, 255]
                else:
                    if len(ceiling['texture_url']) > 0 or ceiling['jid'] not in ['', 'generated']:
                        ceiling['colorMode'] = 'texture'
                    else:
                        ceiling['colorMode'] = 'color'
                if ceiling['color'] is None:
                    ceiling['color'] = [255, 255, 255]
                # if ceiling['colorMode'] == 'color':
                #     ceiling['texture_url'] = ''
                tree = ['tiles', 'transfer']
                if ceiling['jid'] in ['', 'generated'] and len(ceiling['texture_url']) > 0:
                    ceiling['jid'] = ceiling['texture_url'].split('/')[-2]

                if len(ceiling['texture_url']) > 0 and not ceiling['texture_url'].startswith('https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/'):
                    ceiling['jid'] = ''
                if len(ceiling['jid'].split('-')) != 5:
                    ceiling['jid'] = ''
                else:
                    if self.white_list and ('support_mobile_scene' not in ceiling or not ceiling['support_mobile_scene']):
                        if not self.check_white_list(ceiling['jid']):
                            continue
                content_type = ''
                if 'contentType' in ceiling:
                    content_type = ceiling['contentType']
                elif isinstance(ceiling['seam'], list):
                    content_type = ceiling['seam']
                formated_mat = {
                    'code': 1,
                    "texture": ceiling['texture_url'],
                    "jid": ceiling['jid'],
                    "uv_ratio": [1. / ceiling['size'][0], 0, 1. / ceiling['size'][1], 0],
                    "color": ceiling['color'] + [255],
                    "colorMode": ceiling['colorMode'],
                    'type': tree,
                    "contentType": content_type,
                    "refs": [] if 'refs' not in ceiling else ceiling['refs']
                }
                ceiling_mat_list.append(formated_mat)
            for baseboard in room_hard['baseboard']:
                # print(floor['seam'])
                if baseboard['color'] is None and len(baseboard['texture_url']) == 0 and baseboard['jid'] in ['', 'generated']:
                    continue
                if baseboard['colorMode'] is not None:
                    if baseboard['colorMode'] == 'color' and baseboard['color'] is None:
                        continue
                    if baseboard['colorMode'] == 'texture' and len(baseboard['texture_url']) == 0 and baseboard['jid'] in ['', 'generated']:
                        continue
                    if baseboard['color'] is None:
                        baseboard['color'] = [255, 255, 255]
                else:
                    if len(baseboard['texture_url']) > 0 or baseboard['jid'] not in ['', 'generated']:
                        baseboard['colorMode'] = 'texture'
                    else:
                        baseboard['colorMode'] = 'color'
                if baseboard['color'] is None:
                    baseboard['color'] = [255, 255, 255]
                # if baseboard['colorMode'] == 'color':
                #     baseboard['texture_url'] = ''
                tree = ['tiles', 'transfer']
                if baseboard['jid'] in ['', 'generated'] and len(baseboard['texture_url']) > 0:
                    baseboard['jid'] = baseboard['texture_url'].split('/')[-2]

                if len(baseboard['texture_url']) > 0 and not baseboard['texture_url'].startswith('https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/'):
                    baseboard['jid'] = ''
                if len(baseboard['jid'].split('-')) != 5:
                    baseboard['jid'] = ''
                else:
                    if self.white_list and ('support_mobile_scene' not in baseboard or not baseboard['support_mobile_scene']):
                        if not self.check_white_list(baseboard['jid']):
                            continue

                content_type = ''
                if 'contentType' in baseboard:
                    content_type = baseboard['contentType']
                elif isinstance(baseboard['seam'], list):
                    content_type = baseboard['seam']
                formated_mat = {
                    'code': 1,
                    "texture": baseboard['texture_url'],
                    "jid": baseboard['jid'],
                    "uv_ratio": [1. / baseboard['size'][0], 0, 1. / baseboard['size'][1], 0],
                    "color": baseboard['color'] + [255],
                    "colorMode": baseboard['colorMode'],
                    'type': tree,
                    "contentType": content_type,
                    "refs": [] if 'refs' not in baseboard else baseboard['refs']
                }
                baseboard_mat_list.append(formated_mat)
            if len(ceiling_mat_list) > 0:
                # floor_mat = np.random.choice(floor_mat_list)
                ceiling_mat = ceiling_mat_list[0]
            else:
                ceiling_mat = None
            if len(baseboard_mat_list) > 0:
                # floor_mat = np.random.choice(floor_mat_list)
                baseboard_mat = baseboard_mat_list[0]
            else:
                baseboard_mat = None
            if len(floor_mat_list) > 0:
                # floor_mat = np.random.choice(floor_mat_list)
                floor_mat = floor_mat_list[0]
            else:
                floor_mat = None
            if room_type in PRIME_GENERAL_WALL_ROOM_TYPES:
                if len(wall_mat_list) > 0:
                    general_wall_mat = []
                    bed_wall_mat = []
                    sub_bed_wall_mat = []
                    media_wall_mat = []
                    for mat in wall_mat_list:
                        if 'Functional' in mat:
                            if mat['Functional'] == 'Main':
                                general_wall_mat.append(mat)
                            elif mat['Functional'] == 'Bed':
                                bed_wall_mat.append(mat)
                            elif mat['Functional'] == 'Media':
                                media_wall_mat.append(mat)
                            else:
                                general_wall_mat.append(mat)
                        else:
                            general_wall_mat.append(mat)
                    if len(general_wall_mat) == 0:
                        general_wall_mat = wall_mat_list
                    if len(bed_wall_mat) == 0:
                        bed_wall_mat = None
                    else:
                        bed_wall_mat = bed_wall_mat[0]
                    if len(media_wall_mat) == 0:
                        media_wall_mat = None
                    else:
                        media_wall_mat = media_wall_mat[0]
                    if len(general_wall_mat) > 1:
                        sub_bed_wall_mat = general_wall_mat[1]
                    else:
                        sub_bed_wall_mat = None

                    if bed_wall_mat is None and media_wall_mat is None:
                        wall_mat = general_wall_mat[0]
                    else:
                        wall_mat = {
                            'general': general_wall_mat[0],
                            'Bed': bed_wall_mat,
                            'Media': media_wall_mat,
                            'SubBed': sub_bed_wall_mat
                        }
                else:
                    wall_mat = None
            elif ROOM_BUILD_TYPE[room_type] == 'LivingDiningRoom':
                if len(wall_mat_list) > 0:
                    general_wall_mat = []
                    meeting_wall_mat = []
                    media_wall_mat = []
                    hallway_wall_mat = []
                    for mat in wall_mat_list:
                        if 'Functional' in mat:
                            if mat['Functional'] == 'Main':
                                general_wall_mat.append(mat)
                            elif mat['Functional'] == 'Meeting':
                                meeting_wall_mat.append(mat)
                            elif mat['Functional'] == 'Media':
                                media_wall_mat.append(mat)
                            elif mat['Functional'] == 'Hallway':
                                hallway_wall_mat.append(mat)
                            else:
                                general_wall_mat.append(mat)
                        else:
                            general_wall_mat.append(mat)
                    if len(general_wall_mat) == 0:
                        general_wall_mat = wall_mat_list
                    if len(meeting_wall_mat) == 0:
                        meeting_wall_mat = None
                    else:
                        meeting_wall_mat = meeting_wall_mat[0]
                    if len(media_wall_mat) == 0:
                        media_wall_mat = None
                    else:
                        media_wall_mat = media_wall_mat[0]
                    if len(hallway_wall_mat) == 0:
                        hallway_wall_mat = None
                    else:
                        hallway_wall_mat = hallway_wall_mat[0]
                    if meeting_wall_mat is None and media_wall_mat is None and hallway_wall_mat is None:
                        wall_mat = general_wall_mat[0]
                    else:
                        wall_mat = {
                            'general': general_wall_mat[0],
                            'Meeting': meeting_wall_mat,
                            'Media': media_wall_mat,
                            'HallWay': hallway_wall_mat
                        }
                else:
                    wall_mat = None
            else:
                if len(wall_mat_list) > 0:
                    wall_mat = wall_mat_list[0]
                else:
                    wall_mat = None

            if 'door' in room_hard and len(room_hard['door']) > 0:
                doors = room_hard['door']
                for door_k, door_v in doors.items():
                    valid_door_v = []
                    for d in door_v:
                        if 'size' not in d:
                            continue
                        d['size'] = (np.array(d['size']) / 100.).tolist()
                        d['jid'] = d['id']
                        d['contentType'] = d['type'] if 'type' in d else 'door/single swing door'

                        # pocket
                        if 'pocket' in d:
                            pocket = d['pocket']
                            if pocket['colorMode'] is not None:
                                if pocket['color'] is None:
                                    pocket['color'] = [255, 255, 255]
                            else:
                                if len(pocket['texture_url']) > 0 or pocket['jid'] not in ['', 'generated']:
                                    pocket['colorMode'] = 'texture'
                                else:
                                    pocket['colorMode'] = 'color'
                            if pocket['color'] is None:
                                pocket['color'] = [255, 255, 255]
                            formated_mat = {
                                'code': 1,
                                "texture": pocket['texture_url'],
                                "jid": pocket['jid'],
                                "uv_ratio": [1. / pocket['size'][0], 0, 1. / pocket['size'][1], 0],
                                "color": pocket['color'] + [255],
                                "colorMode": pocket['colorMode'],
                                'type': ['tiles', 'transfer'],
                                "contentType": pocket['seam'] if isinstance(pocket['seam'], list) else ""
                            }
                            d['pocket'] = formated_mat
                        valid_door_v.append(d)
                    doors[door_k] = valid_door_v
            else:
                doors = None
            if 'win' in room_hard and len(room_hard['win']) > 0:
                wins = {
                    'FrenchWindow': [],
                    'BayWindow': [],
                    'single': [],
                    'double': [],
                    'triple': [],
                }
                for win in room_hard['win']:
                    if 'size' not in win:
                        continue
                    win['size'] = (np.array(win['size']) / 100.).tolist()
                    win['jid'] = win['id']
                    win['contentType'] = win['type'] if 'type' in win else 'window/window'
                    if 'pocket' in win:
                        pocket = win['pocket']
                        if pocket['colorMode'] is not None:
                            if pocket['color'] is None:
                                pocket['color'] = [255, 255, 255]
                        else:
                            if len(pocket['texture_url']) > 0 or pocket['jid'] not in ['', 'generated']:
                                pocket['colorMode'] = 'texture'
                            else:
                                pocket['colorMode'] = 'color'
                        if pocket['color'] is None:
                            pocket['color'] = [255, 255, 255]
                        formated_mat = {
                            'code': 1,
                            "texture": pocket['texture_url'],
                            "jid": pocket['jid'],
                            "uv_ratio": [1. / pocket['size'][0], 0, 1. / pocket['size'][1], 0],
                            "color": pocket['color'] + [255],
                            "colorMode": pocket['colorMode'],
                            'type': ['tiles', 'transfer'],
                            "contentType": pocket['seam'] if isinstance(pocket['seam'], list) else ""
                        }
                        win['pocket'] = formated_mat
                    if 'type' in win and 'bay window' in win['type']:
                        wins['BayWindow'].append(win)
                    elif 'type' in win and 'floor-based window' in win['type']:
                        wins['FrenchWindow'].append(win)
                    else:
                        if win['size'][0] < 0.8:
                            wins['single'].append(win)
                        elif win['size'][0] < 1.2:
                            wins['double'].append(win)
                        else:
                            wins['triple'].append(win)
            else:
                wins = None
            # if 'ceiling' in room_hard and len(room_hard['ceiling']) > 0:
            #     customized_ceilings = room_hard['ceiling']
            # else:
            #     customized_ceilings = None
            if 'customized_ceiling' in room_hard and len(room_hard['customized_ceiling']) > 0:
                customized_ceilings = room_hard['customized_ceiling']
                # print('吊顶')
            else:
                customized_ceilings = []

            self_transfer = room_hard['self_transfer'] if 'self_transfer' in room_hard else False
            customized_ceilings_info_list = []
            for c in customized_ceilings:
                if 'type' in c and c['type'] == 'CustomizedCeiling':
                    if c['size'][1] > 5:  # unit cm
                        unit_scale = 10.
                    else:  # unit m
                        unit_scale = 1000.
                    if (not c['valid'] or c['size'][1] * unit_scale > 800) and not self_transfer:
                        continue
                    c['jid'] = c['obj']
                    c['contentType'] = c['type'] if 'type' in c else 'CustomizedCeiling'
                    c['size'] = (np.array(c['size']) * unit_scale)[[0, 2, 1]].tolist()
                    c['resizeable'] = True
                    if (c['size'][0] < 2.0 or c['size'][1] < 2.0) and not self_transfer:
                        continue
                else:
                    c['jid'] = c['id'] if 'id' in c else ''
                    c['contentType'] = c['type'] if 'type' in c else 'build element/ceiling molding'
                    if 'size' not in c:
                        continue
                    c['size'] = (np.array(c['size']) * 10.)[[0, 2, 1]].tolist()
                    c['resizeable'] = True
                    if c['size'][0] < 2.0 or c['size'][1] < 2.0:
                        continue
                # print('可用吊顶', room_id)
                customized_ceilings_info_list.append(c)
            if len(customized_ceilings) > 0 and len(customized_ceilings_info_list) == 0:
                # 样板间无吊顶时，不使用兜底吊顶
                customized_ceilings_info_list = ['invalid sample']
            if len(customized_ceilings) == 0:
                customized_ceilings_info_list = ['no sample']

            # 提取存档
            wall_dict = {
                'Meeting': 'meeting wall',
                'Media': 'media wall',
                'Bed': 'bed wall',
            }
            hard_for_room['self_transfer'][room_id] = self_transfer
            if 'background' in room_hard and len(room_hard['background']) > 0:
                comb_bg_wall = room_hard['background']
                for func in comb_bg_wall.keys():
                    comb_bg_wall[func].sort(key=lambda x: -x['size'][0] * x['scale'][0])
                    if func in wall_dict:
                        sample_hard[wall_dict[func]] = [comb_bg_wall[func][0]]
                        if room_id not in hard_for_room[wall_dict[func]]:
                            hard_for_room[wall_dict[func]][room_id] = []
                        hard_for_room[wall_dict[func]][room_id] += [comb_bg_wall[func][0]]

            if room_type in transfer_hard_sample['customizedCeiling']:
                transfer_hard_sample["customizedCeiling"][room_type] += customized_ceilings_info_list
            else:
                transfer_hard_sample["customizedCeiling"][room_type] = customized_ceilings_info_list
            valid_customized_ceilings = [i for i in customized_ceilings_info_list if isinstance(i, dict)]
            if len(valid_customized_ceilings) > 0:
                if room_id not in hard_for_room['customizedCeiling']:
                    hard_for_room['customizedCeiling'][room_id] = []
                hard_for_room['customizedCeiling'][room_id] += valid_customized_ceilings
            if floor_mat is not None:
                if room_type in transfer_hard_sample["Floor"]:
                    transfer_hard_sample["Floor"][room_type].append(floor_mat)
                else:
                    transfer_hard_sample["Floor"][room_type] = [floor_mat]
                if room_id not in hard_for_room['Floor']:
                    hard_for_room['Floor'][room_id] = []
                hard_for_room['Floor'][room_id] += [floor_mat]

            if ceiling_mat is not None:
                if room_type in transfer_hard_sample["Ceiling"]:
                    transfer_hard_sample["Ceiling"][room_type].append(ceiling_mat)
                else:
                    transfer_hard_sample["Ceiling"][room_type] = [ceiling_mat]
                if room_id not in hard_for_room['Ceiling']:
                    hard_for_room['Ceiling'][room_id] = []
                hard_for_room['Ceiling'][room_id] += [ceiling_mat]
            if baseboard_mat is not None:
                if room_type in transfer_hard_sample["Baseboard"]:
                    transfer_hard_sample["Baseboard"][room_type].append(baseboard_mat)
                else:
                    transfer_hard_sample["Baseboard"][room_type] = [baseboard_mat]
                if room_id not in hard_for_room['Baseboard']:
                    hard_for_room['Baseboard'][room_id] = []
                hard_for_room['Baseboard'][room_id] += [baseboard_mat]
            if wall_mat is not None:
                if room_type in transfer_hard_sample["WallInner"]:
                    transfer_hard_sample["WallInner"][room_type].append(wall_mat)
                else:
                    transfer_hard_sample["WallInner"][room_type] = [wall_mat]
                if room_id not in hard_for_room['WallInner']:
                    hard_for_room['WallInner'][room_id] = []
                hard_for_room['WallInner'][room_id] += [wall_mat]
            if doors is not None:
                # entry_doors = []
                # other_doors = []
                #
                # for door_info in doors:
                #     if 'entry' in door_info and door_info['entry']:
                #         entry_doors.append(door_info)
                #     else:
                #         other_doors.append(door_info)

                if room_type in transfer_hard_sample["Door"]:
                    transfer_hard_sample["Door"][room_type] += [doors]
                else:
                    transfer_hard_sample["Door"][room_type] = [doors]

                # if 'entry' in transfer_hard_sample["Door"]:
                #     transfer_hard_sample["Door"]['entry'] += entry_doors
                # else:
                #     transfer_hard_sample["Door"]['entry'] = entry_doors
                # 暂时不支持按照房间id迁移door
                # if room_id not in hard_for_room['door']:
                #     hard_for_room['door'][room_id] = []
                # hard_for_room['door'][room_id] = doors
            if wins is not None:
                if room_type in transfer_hard_sample["Win"]:
                    transfer_hard_sample["Win"][room_type] += [wins]
                else:
                    transfer_hard_sample["Win"][room_type] = [wins]
                # 暂时不支持按照房间id迁移win
                if room_id not in hard_for_room['window']:
                    hard_for_room['window'][room_id] = []
                hard_for_room['window'][room_id] = copy.deepcopy(wins)

        # 融合
        for floor_room_type, floor_mat_list in transfer_hard_sample['Floor'].items():
            sample_hard['Floor'][floor_room_type] = floor_mat_list
        if 'LivingDiningRoom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['LivingDiningRoom'] = transfer_hard_sample['Floor']['LivingDiningRoom']
        elif 'LivingRoom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['LivingDiningRoom'] = transfer_hard_sample['Floor']['LivingRoom']
        elif 'DiningRoom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['LivingDiningRoom'] = transfer_hard_sample['Floor']['DiningRoom']

        if 'MasterBedroom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['MasterBedroom'] = transfer_hard_sample['Floor']['MasterBedroom']
        elif 'Bedroom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['MasterBedroom'] = transfer_hard_sample['Floor']['Bedroom']
        elif 'SecondBedroom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['MasterBedroom'] = transfer_hard_sample['Floor']['SecondBedroom']

        if 'Bathroom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['Bathroom'] = transfer_hard_sample['Floor']['Bathroom']
        elif 'MasterBathroom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['Bathroom'] = transfer_hard_sample['Floor']['MasterBathroom']
        elif 'SecondBathroom' in transfer_hard_sample['Floor']:
            sample_hard['Floor']['Bathroom'] = transfer_hard_sample['Floor']['SecondBathroom']

        # ceiling
        for ceiling_room_type, ceiling_mat_list in transfer_hard_sample['Ceiling'].items():
            sample_hard['Ceiling'][ceiling_room_type] = ceiling_mat_list
        if 'LivingDiningRoom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['LivingDiningRoom'] = transfer_hard_sample['Ceiling']['LivingDiningRoom']
        elif 'LivingRoom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['LivingDiningRoom'] = transfer_hard_sample['Ceiling']['LivingRoom']
        elif 'DiningRoom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['LivingDiningRoom'] = transfer_hard_sample['Ceiling']['DiningRoom']

        if 'MasterBedroom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['MasterBedroom'] = transfer_hard_sample['Ceiling']['MasterBedroom']
        elif 'Bedroom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['MasterBedroom'] = transfer_hard_sample['Ceiling']['Bedroom']
        elif 'SecondBedroom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['MasterBedroom'] = transfer_hard_sample['Ceiling']['SecondBedroom']

        if 'Bathroom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['Bathroom'] = transfer_hard_sample['Ceiling']['Bathroom']
        elif 'MasterBathroom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['Bathroom'] = transfer_hard_sample['Ceiling']['MasterBathroom']
        elif 'SecondBathroom' in transfer_hard_sample['Ceiling']:
            sample_hard['Ceiling']['Bathroom'] = transfer_hard_sample['Ceiling']['SecondBathroom']

        # baseboard
        for baseboard_room_type, baseboard_mat_list in transfer_hard_sample['Baseboard'].items():
            sample_hard['Baseboard'][baseboard_room_type] = baseboard_mat_list
        if 'LivingDiningRoom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['LivingDiningRoom'] = transfer_hard_sample['Baseboard']['LivingDiningRoom']
        elif 'LivingRoom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['LivingDiningRoom'] = transfer_hard_sample['Baseboard']['LivingRoom']
        elif 'DiningRoom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['LivingDiningRoom'] = transfer_hard_sample['Baseboard']['DiningRoom']

        if 'MasterBedroom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['MasterBedroom'] = transfer_hard_sample['Baseboard']['MasterBedroom']
        elif 'Bedroom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['MasterBedroom'] = transfer_hard_sample['Baseboard']['Bedroom']
        elif 'SecondBedroom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['MasterBedroom'] = transfer_hard_sample['Baseboard']['SecondBedroom']

        if 'Bathroom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['Bathroom'] = transfer_hard_sample['Baseboard']['Bathroom']
        elif 'MasterBathroom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['Bathroom'] = transfer_hard_sample['Baseboard']['MasterBathroom']
        elif 'SecondBathroom' in transfer_hard_sample['Baseboard']:
            sample_hard['Baseboard']['Bathroom'] = transfer_hard_sample['Baseboard']['SecondBathroom']
        # wall
        for wall_room_type, wall_mat_list in transfer_hard_sample['WallInner'].items():
            # if ROOM_BUILD_TYPE[wall_room_type] in sample_hard['WallInner']:
            #     sample_hard['WallInner'][ROOM_BUILD_TYPE[wall_room_type]] = wall_mat_list
            sample_hard['WallInner'][wall_room_type] = wall_mat_list

        if 'LivingDiningRoom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['LivingDiningRoom'] = transfer_hard_sample['WallInner']['LivingDiningRoom']
        elif 'LivingRoom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['LivingDiningRoom'] = transfer_hard_sample['WallInner']['LivingRoom']
        elif 'DiningRoom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['LivingDiningRoom'] = transfer_hard_sample['WallInner']['DiningRoom']

        if 'MasterBedroom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['MasterBedroom'] = transfer_hard_sample['WallInner']['MasterBedroom']
        elif 'Bedroom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['MasterBedroom'] = transfer_hard_sample['WallInner']['Bedroom']
        elif 'SecondBedroom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['MasterBedroom'] = transfer_hard_sample['WallInner']['SecondBedroom']

        if 'Bathroom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['Bathroom'] = transfer_hard_sample['WallInner']['Bathroom']
        elif 'MasterBathroom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['Bathroom'] = transfer_hard_sample['WallInner']['MasterBathroom']
        elif 'SecondBathroom' in transfer_hard_sample['WallInner']:
            sample_hard['WallInner']['Bathroom'] = transfer_hard_sample['WallInner']['SecondBathroom']

        # 门的迁移比较复杂，涉及两个空间。这里优先使用客餐厅的关联门，如果没有通往某个空间的门，再考虑使用其他空间的门作为种子
        transfered_door = {}
        sliding_door = []
        single_swing_door = []
        if 'LivingDiningRoom' in transfer_hard_sample['Door']:
            transfered_door = transfer_hard_sample['Door']['LivingDiningRoom'][0]
            for door_dict in transfer_hard_sample['Door']['LivingDiningRoom']:
                for doors in door_dict.values():
                    for door in doors:
                        if 'type' in door and 'sliding' in door['type'] and door not in sliding_door:
                            sliding_door.append(door)
                        elif 'type' in door and 'single swing' in door['type'] and door not in single_swing_door:
                            single_swing_door.append(door)
        elif 'LivingRoom' in transfer_hard_sample['Door']:
            transfered_door = transfer_hard_sample['Door']['LivingRoom'][0]
            if len(sliding_door) == 0:
                for door_dict in transfer_hard_sample['Door']['LivingRoom']:
                    for doors in door_dict.values():
                        for door in doors:
                            if 'type' in door and 'sliding' in door['type'] and door not in sliding_door:
                                sliding_door.append(door)
                            elif 'type' in door and 'single swing' in door['type'] and door not in single_swing_door:
                                single_swing_door.append(door)
        elif 'DiningRoom' in transfer_hard_sample['Door']:
            transfered_door = transfer_hard_sample['Door']['DiningRoom'][0]
            if len(sliding_door) == 0:
                for door_dict in transfer_hard_sample['Door']['DiningRoom']:
                    for doors in door_dict.values():
                        for door in doors:
                            if 'type' in door and 'sliding' in door['type'] and door not in sliding_door:
                                sliding_door.append(door)
                            elif 'type' in door and 'single swing' in door['type'] and door not in single_swing_door:
                                single_swing_door.append(door)

        # 补充主门
        if 'MasterBedroom' not in transfered_door:
            if 'Bedroom' in transfered_door:
                transfered_door['MasterBedroom'] = transfered_door['Bedroom']
            elif 'SecondBedroom' in transfered_door:
                transfered_door['MasterBedroom'] = transfered_door['SecondBedroom']
            elif 'Library' in transfered_door:
                transfered_door['MasterBedroom'] = transfered_door['Library']

        for door_room_type, door_mat_list in transfer_hard_sample['Door'].items():
            for door_mat_dict in door_mat_list:
                for target_room_type, door_list in door_mat_dict.items():
                    if ROOM_BUILD_TYPE[door_room_type] in ['Bathroom', 'Balcony', '', 'Kitchen']:
                        door_type = door_room_type
                    elif ROOM_BUILD_TYPE[target_room_type] in ['Bathroom', 'Balcony', '', 'Kitchen']:
                        door_type = target_room_type
                    elif ROOM_BUILD_TYPE[door_room_type] == 'LivingDiningRoom':
                        door_type = target_room_type
                    elif ROOM_BUILD_TYPE[target_room_type] == 'LivingDiningRoom':
                        door_type = door_room_type
                    else:
                        print('invalid door connect type %s-%s' % (door_room_type, target_room_type))
                        door_type = door_room_type

                    if door_type not in transfered_door:
                        transfered_door[door_type] = door_list
                    room_sliding_door = [door for door in door_list if ('type' in door and 'sliding' in door['type'] and door not in sliding_door)]
                    sliding_door += room_sliding_door
        if len(sliding_door) > 0:
            transfered_door['sliding door'] = sliding_door
        transfered_door['swing door'] = single_swing_door

        transfer_hard_sample['Door'] = transfered_door
        if 'entry' in transfer_hard_sample['Door']:
            valid_entry_doors = [i for i in transfer_hard_sample['Door']['entry'] if 'entry' in i['type']]
            if len(valid_entry_doors) > 0:
                transfer_hard_sample['Door']['entry'] = valid_entry_doors
            else:
                valid_entry_doors = [i for i in transfer_hard_sample['Door']['entry'] if 'sliding' not in i['type']]
                if len(valid_entry_doors) > 0:
                    transfer_hard_sample['Door']['entry'] = valid_entry_doors
        for door_room_type, door_mat_list in transfer_hard_sample['Door'].items():
            sample_hard['door'][door_room_type] = door_mat_list
        if 'MasterBedroom' in transfer_hard_sample['Door']:
            sample_hard['door']['MasterBedroom'] = transfer_hard_sample['Door']['MasterBedroom']
        elif 'Bedroom' in transfer_hard_sample['Door']:
            sample_hard['door']['MasterBedroom'] = transfer_hard_sample['Door']['Bedroom']
        elif 'SecondBedroom' in transfer_hard_sample['Door']:
            sample_hard['door']['MasterBedroom'] = transfer_hard_sample['Door']['SecondBedroom']
        elif 'Library' in transfer_hard_sample['Door']:
            sample_hard['door']['MasterBedroom'] = transfer_hard_sample['Door']['Library']

        if 'Bathroom' in transfer_hard_sample['Door']:
            sample_hard['door']['Bathroom'] = transfer_hard_sample['Door']['Bathroom']
        elif 'MasterBathroom' in transfer_hard_sample['Door']:
            sample_hard['door']['Bathroom'] = transfer_hard_sample['Door']['MasterBathroom']
        elif 'SecondBathroom' in transfer_hard_sample['Door']:
            sample_hard['door']['Bathroom'] = transfer_hard_sample['Door']['SecondBathroom']
        elif len(single_swing_door) > 0:
            sample_hard['door']['Bathroom'] = single_swing_door

        if 'Balcony' in transfer_hard_sample['Door']:
            sample_hard['door']['Balcony'] = transfer_hard_sample['Door']['Balcony']
        elif 'Terrace' in transfer_hard_sample['Door']:
            sample_hard['door']['Balcony'] = transfer_hard_sample['Door']['Terrace']
        else:
            sample_hard['door']['Balcony'] = []
        if 'Kitchen' in transfer_hard_sample['Door']:
            sample_hard['door']['Kitchen'] = transfer_hard_sample['Door']['Kitchen']
        else:
            sample_hard['door']['Kitchen'] = []

        # 窗
        cmb_win = {
            'FrenchWindow': [],
            'BayWindow': [],
            'single': [],
            'double': [],
            'triple': [],
        }
        for win_room_type, wins in transfer_hard_sample['Win'].items():
            for win_dict in wins:
                for win_type, ws in win_dict.items():
                    cmb_win[win_type] += ws
            if len(wins) > 0:
                # 同一房间类型只保留一份
                transfer_hard_sample['Win'][win_room_type] = wins[0]
        for win_type, ws in cmb_win.items():
            if len(ws) == 0:
                cmb_win[win_type] = sample_hard['window'][win_type]

        for win_room_type, win_dict in transfer_hard_sample['Win'].items():
            for win_type, ws in win_dict.items():
                if len(ws) == 0:
                    win_dict[win_type] = cmb_win[win_type]
        transfer_hard_sample['Win']['All'] = cmb_win
        sample_hard['window'] = transfer_hard_sample['Win']

        # 吊顶
        customized_ceiling_new = {}
        for room_type in transfer_hard_sample["customizedCeiling"].keys():
            valid_ceiling = [i for i in transfer_hard_sample["customizedCeiling"][room_type] if isinstance(i, dict) and ('valid' not in i or i['valid'])]
            invalid_ceiling = [i for i in transfer_hard_sample["customizedCeiling"][room_type] if i == 'invalid sample']
            if len(valid_ceiling) > 0:
                # 存在可用吊顶，则使用吊顶
                valid_ceiling.sort(key=lambda x: -x['size'][0] * x['size'][1])
                # transfer_hard_sample["customizedCeiling"][room_type]
                # transfer_hard_sample["customizedCeiling"][room_type] = transfer_hard_sample["customizedCeiling"][room_type][:1]
                customized_ceiling_new[room_type] = valid_ceiling[:1]
            elif len(invalid_ceiling) > 0:
                # 存在吊顶，但不可用，则不放入customized_ceiling_new ，后续融合时即会使用兜底
                # transfer_hard_sample["customizedCeiling"][room_type] = False
                pass
            else:
                # 不存在吊顶时，则后续融合时将该房间类型的可用吊顶置为空数组
                # transfer_hard_sample["customizedCeiling"][room_type] = []
                customized_ceiling_new[room_type] = []
        transfer_hard_sample["customizedCeiling"] = customized_ceiling_new

        for ceiling_room_type, ceiling_mat_list in transfer_hard_sample['customizedCeiling'].items():
            sample_hard['customizedCeiling'][ceiling_room_type] = ceiling_mat_list
        if 'LivingDiningRoom' in transfer_hard_sample['customizedCeiling'] and \
                len(transfer_hard_sample['customizedCeiling']['LivingDiningRoom']) > 0:
            sample_hard['customizedCeiling']['LivingDiningRoom'] = transfer_hard_sample['customizedCeiling']['LivingDiningRoom']
        elif 'LivingRoom' in transfer_hard_sample['customizedCeiling'] and \
                len(transfer_hard_sample['customizedCeiling']['LivingRoom']) > 0:
            sample_hard['customizedCeiling']['LivingDiningRoom'] = transfer_hard_sample['customizedCeiling']['LivingRoom']
        elif 'DiningRoom' in transfer_hard_sample['customizedCeiling'] and \
                len(transfer_hard_sample['customizedCeiling']['DiningRoom']) > 0:
            sample_hard['customizedCeiling']['LivingDiningRoom'] = transfer_hard_sample['customizedCeiling']['DiningRoom']

        if 'MasterBedroom' in transfer_hard_sample['customizedCeiling'] and \
                len(transfer_hard_sample['customizedCeiling']['MasterBedroom']) > 0:
            sample_hard['customizedCeiling']['MasterBedroom'] = transfer_hard_sample['customizedCeiling']['MasterBedroom']
        elif 'Bedroom' in transfer_hard_sample['customizedCeiling'] and \
                len(transfer_hard_sample['customizedCeiling']['Bedroom']) > 0:
            sample_hard['customizedCeiling']['MasterBedroom'] = transfer_hard_sample['customizedCeiling']['Bedroom']
        elif 'SecondBedroom' in transfer_hard_sample['customizedCeiling'] and \
                len(transfer_hard_sample['customizedCeiling']['SecondBedroom']) > 0:
            sample_hard['customizedCeiling']['MasterBedroom'] = transfer_hard_sample['customizedCeiling']['SecondBedroom']
        elif 'Library' in transfer_hard_sample['customizedCeiling'] and \
                len(transfer_hard_sample['customizedCeiling']['Library']) > 0:
            sample_hard['customizedCeiling']['MasterBedroom'] = transfer_hard_sample['customizedCeiling']['Library']

        return sample_hard, hard_for_room

    def store_similar_online_hard(self, save_path):
        res = []
        self.get_dict_son(self.SAMPLE_ROOMS, res, [])

        style_hard_res = [i for i in res if i[1][2] in ['door', 'floor', 'wall']]
        jid_list, _ = list(zip(*style_hard_res))

        jid_list = list(set(jid_list))
        similar_jid_dict = self.similar_hard.get_similar_hard_item(jid_list)
        similar_jid_list = []
        for k, v in similar_jid_dict.items():
            if len(v) != 0:
                similar_jid_list += v
        jid_attr_dict = self.similar_hard.get_jid_attribute(similar_jid_list)

        type_list = [
            'door&entry',
            'door&swing door',
            'door&sliding door',
            'tiles&ceramic wall',
            'tiles&ceramic main floor',
            'tiles&ceramic extra floor',
            'tiles&wooden'
        ]
        jid_list = []
        for k, v in similar_jid_dict.items():
            ins = sample.hard_lib.get_jid_ins(jid=k)
            if ins is not None and '&'.join(ins[1][:2]) in type_list:
                jid_list.append([k, ins])
        for jid, mat in jid_list:
            cur_folder = os.path.join(save_path, jid)
            if not os.path.exists(cur_folder):
                os.makedirs(cur_folder)
            if 'texture' in mat[0]:
                url = mat[0]['texture']
            else:
                url = 'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/%s/iso.jpg' % jid
            self.get_and_save_img(url, os.path.join(cur_folder, 'key_image_' + jid + '.png'))
            similar_res_list = similar_jid_dict[jid]
            for i, similar_jid in enumerate(similar_res_list):
                attr = jid_attr_dict[similar_jid]
                self.get_and_save_img(attr['image_url'], os.path.join(cur_folder, str(i) + '_' + similar_jid + '.png'))

    def export_samples_to_odps(self):
        res = []
        self.get_dict_son(self.SAMPLE_ROOMS, res, [])
        return res

    def get_dict_son(self, d, res, keys):
        for k, v in d.items():
            cur_keys = copy.deepcopy(keys)
            if isinstance(v, list):
                self.get_list_son(v, res, cur_keys + [k])
            elif isinstance(v, dict):
                self.get_dict_son(v, res, cur_keys + [k])
            else:
                res.append((v, cur_keys + [k]))

    def get_list_son(self, l, res, keys):
        for i, item in enumerate(l):
            cur_keys = copy.deepcopy(keys)
            if isinstance(item, list):
                self.get_list_son(item, res, cur_keys + [i])
            elif isinstance(item, dict):
                self.get_dict_son(item, res, cur_keys + [i])
            else:
                res.append((item, cur_keys + [i]))

    @staticmethod
    def get_and_save_img(url, path):
        try:
            re = requests.get(url)
            re.raise_for_status()
            image = Image.open(io.BytesIO(re.content))
            image.save(path)
        except Exception as e:
            print('invalid texture url', url, e)


def filter_hard_items(query_item, candidates):
    res = []
    for item in candidates:
        q_size = query_item['model_size'].split('&')
        q_size = [float(i[2:]) for i in q_size]
        item_size = item['model_size'].split('&')
        item_size = [float(i[2:]) for i in item_size]

        if query_item['jr_cate2'] == '门':
            if (item_size[0] < 100 <= q_size[0]) or \
                (100 <= item_size[0] < 240 and (q_size[0] >= 240 or q_size[0] < 100)) or \
                    item_size[0] >= 240 > q_size[0]:
                continue
            if query_item['jr_cate2'] != item['jr_cate2'] or query_item['jr_cate3'] != item['jr_cate3'] or query_item['jr_cate4'] != item['jr_cate4']:
                continue
            res.append(item.copy())
        elif query_item['jr_cate2'] == '瓷砖':
            if 0.8 < min(item_size[0], item_size[1]) / (min(q_size[0], q_size[1]) + 1e-3) < 1.2 and \
                    0.8 < max(item_size[0], item_size[1]) / (max(q_size[0], q_size[1]) + 1e-3) < 1.2:
                res.append(item.copy())
        elif query_item['jr_cate2'] == '地板':
            res.append(item.copy())
    return res


if __name__ == '__main__':
    sample = SampleRooms()
    store_similar_path = '/Users/liqing.zhc/code/ihome-zncz-project/module/LayoutDecoration/sample_room/tmp'
    sample.store_similar_online_hard(store_similar_path)

    res = sample.export_samples_to_odps()
    samples_types = ['wall', 'door', 'floor']
    query_res = {}

    for hard_type in samples_types:
        query_res[hard_type] = []
        cur_type_samples = [i for i in res if hard_type in i[1]]
        for item in cur_type_samples:
            ins = sample.hard_lib.get_jid_ins(jid=item[0])
            if ins is not None:
                ins, trees = ins
                if 'texture_url' in ins and ins['texture_url'] == '':
                    continue
                if 'texture_url' not in ins:
                    ins['texture_url'] = 'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/%s/iso.jpg' % \
                                         ins['jid']
                try:
                    re = requests.get(ins['texture_url'])
                    re.raise_for_status()
                except Exception as e:
                    print('invalid texture url', item, trees)
                query_res[hard_type].append((ins, trees))
            else:
                print('not found in hard library', item)

    print('_________________________________________________')
    type_dict = {
        'door&entry': ['建筑结构', '1df3e3a8-15b0-4647-bd69-e64350cab281', '门', '2fcca190-7fda-403c-8b0a-add380281544', '入户门', '5b8d742e-92b1-4529-8bc1-0f5d31826f09', '', ''],
        'door&swing door': ['建筑结构', '1df3e3a8-15b0-4647-bd69-e64350cab281', '门', '2fcca190-7fda-403c-8b0a-add380281544', '室内门', 'aa13fe61-23a6-47b3-8741-bab627cd2b30', '平开门', 'a6f133b9-80b1-41ab-a89b-be3b8f4823fa'],
        'door&bathroom': ['建筑结构', '1df3e3a8-15b0-4647-bd69-e64350cab281', '门', '2fcca190-7fda-403c-8b0a-add380281544', '室内门', 'aa13fe61-23a6-47b3-8741-bab627cd2b30', '平开门', 'a6f133b9-80b1-41ab-a89b-be3b8f4823fa'],
        'door&sliding door': ['建筑结构', '1df3e3a8-15b0-4647-bd69-e64350cab281', '门', '2fcca190-7fda-403c-8b0a-add380281544', '室内门', 'aa13fe61-23a6-47b3-8741-bab627cd2b30', '推拉门', '2bc73bd5-2f0a-467c-a8ec-4ff285b3a000'],
        # 'tiles&wallpaper solid': ['硬装', '壁纸', '素面'],
        # 'tiles&wallpaper pattern': ['硬装', '壁纸', '花纹'],
        'tiles&ceramic wall': ['硬装', '236a1cf0-d8de-4027-b7ce-aa3964be4921', '瓷砖', '8cdfd5a3-58e8-4ddc-8368-00da8be442c0', '墙砖', '7b53d24e-7991-449f-844c-0a1b9e84e53d', '', ''],
        'tiles&ceramic main floor': ['硬装', '236a1cf0-d8de-4027-b7ce-aa3964be4921', '瓷砖', '8cdfd5a3-58e8-4ddc-8368-00da8be442c0', '地砖', 'd7981192-acaf-4097-ba62-53af7e58daa7', '', ''],
        'tiles&ceramic extra floor': ['硬装', '236a1cf0-d8de-4027-b7ce-aa3964be4921', '瓷砖', '8cdfd5a3-58e8-4ddc-8368-00da8be442c0', '花砖', 'f329f2f4-b5a4-4ba2-91f0-6727864c9bd1', '', ''],
        'tiles&wooden': ['硬装', '236a1cf0-d8de-4027-b7ce-aa3964be4921', '地板', '8bd53440-2820-4161-9bfc-742e161936af', '', '', '', ''],
    }

    sample_res = []
    for hard_type in samples_types:
        for item in query_res[hard_type]:
            if len(item[0]['size']) == 2:
                size = 'x=%f&y=%f&z=%f' % (item[0]['size'][0] / 10, item[0]['size'][1] / 10, 0)
            else:
                size = 'x=%f&y=%f&z=%f' % (item[0]['size'][0] / 10, item[0]['size'][1] / 10, item[0]['size'][2] / 10)
            types = '&'.join([str(i) for i in item[1]])
            required_type = False
            for k, v in type_dict.items():
                if k in types:
                    types = ','.join(v)
                    required_type = True
                    break
            if not required_type:
                continue
            s = '%s,%s,%s,%s,%s' % (hard_type, item[0]['jid'], size, types, item[0]['texture_url'])
            if s not in sample_res:
                sample_res.append(s)
                print(s)