import sys
import os
import numpy as np
import time
import copy
from shapely.geometry import Polygon
from matplotlib import patches as ptc
from matplotlib import pyplot as plt
from scipy.spatial.transform import Rotation as R
from ..mesh.recon_mesh import Mesh
from ..Base.recon_params import ROOM_BUILD_TYPE, PRIME_GENERAL_WALL_ROOM_TYPES
from ..Base.math_util import compute_furniture_rect


class LightConfig:
    def __init__(self, house_info, house_layout, cur_time='daytime', debug_mode=False):
        self.cur_time = 'daytime'
        self.global_light_full_day = None
        self.config_outdoor_scene(house_info, house_layout)
        self.config_light(house_info, house_layout, debug_mode)

    def config_outdoor_scene(self, house_info, house_layout):
        # outdoor_scene_list = {
        #     'morning': ['morning', 'kiara_sunrise', 'umhlanga_sunrise', 'northern_snow'],  # [6-9]
        #     'daytime': ['ljz_day', 'sea_sky', 'euro_garden', 'fallen_leaves',  # [10 - 16]
        #                   'bay_tour', 'north_euro_city', 'city_park', 'afternoon'],
        #     "dusk": ['dusk', 'shenzhen_night', 'peoples_square_night'],  # [17-19]
        #     "night": ['night', 'ljz_night', 'moonlit_golf', 'wuhan_night']  # [20-5]
        # }
        outdoor_scene_list = {
            'daytime': ['morning', 'kiara_sunrise', 'umhlanga_sunrise', 'northern_snow',
                        'ljz_day', 'sea_sky', 'euro_garden', 'fallen_leaves',
                        'bay_tour', 'north_euro_city', 'city_park', 'afternoon'],
            "dusk": ['dusk', 'shenzhen_night', 'peoples_square_night'],  # [17-19]
            "night": ['ljz_night', 'moonlit_golf', 'wuhan_night']  # [20-5]
        }

        if np.random.random() > 0.5:
            hour = int(time.strftime('%H'))
            if 6 <= hour <= 9:
                # cur_time = 'morning'
                real_cur_time = 'daytime'
            elif 10 <= hour <= 16:
                real_cur_time = 'daytime'
            elif 17 <= hour <= 19:
                real_cur_time = 'dusk'
            else:
                real_cur_time = 'night'
        else:
            real_cur_time = np.random.choice(['daytime', 'dusk', 'night'])
        real_cur_time = 'daytime'
        outdoor_scene = np.random.choice(outdoor_scene_list[real_cur_time])

        self.cur_time = real_cur_time

        global_light_full_day = {
            'daytime': {
                'outdoor_scene': outdoor_scene,
                'enable_sun': '',
                'dome_temperature': '',
                'sun_color': '',
                'sun_src_pos': '',
                'sun_target_pos': ''
            },
            'dusk': {
                'outdoor_scene': outdoor_scene,
                'enable_sun': '',
                'dome_temperature': '',
                'sun_color': '',
                'sun_src_pos': '',
                'sun_target_pos': ''
            },
            'night': {
                'outdoor_scene': outdoor_scene,
                'enable_sun': '',
                'dome_temperature': '',
                'sun_color': '',
                'sun_src_pos': '',
                'sun_target_pos': ''
            }
        }
        # print('light condition: ', outdoor_scene, self.cur_time)
        for cur_time in ['daytime', 'dusk', 'night']:
            if cur_time == 'daytime':

                global_light_full_day[cur_time]['enable_sun'] = True
                global_light_full_day[cur_time]['dome_temperature'] = 6500
                global_light_full_day[cur_time]['sun_color'] = [255, 247, 237, 255]
            elif cur_time == 'dusk':
                # sun_color = [139, 69, 19, 255]
                # sun_color = [139, 0, 0, 255]

                global_light_full_day[cur_time]['enable_sun'] = True
                global_light_full_day[cur_time]['dome_temperature'] = 3500
                global_light_full_day[cur_time]['sun_color'] = [255, 85, 10, 255]
            else:
                global_light_full_day[cur_time]['enable_sun'] = False
                global_light_full_day[cur_time]['dome_temperature'] = 3500
                global_light_full_day[cur_time]['sun_color'] = [135, 205, 239, 255]

        # sun position
        centroids = []
        for room_name, room_data in house_info['rooms'].items():
            # fix by lizuojun 2021.06.01
            # if len(room_data['floor_pts']) > 0:
            if len(room_data['floor_pts']) >= 3:
                poly = Polygon(room_data['floor_pts'])
                centroids.append([poly.centroid.x, poly.centroid.y])
        sun_target_pos = np.mean(centroids, axis=0)
        sun_target_pos = [sun_target_pos[0], 0, sun_target_pos[1]]

        livingDining_target = []
        masterBedRoom_target = []
        for room_name, room_data in house_info['rooms'].items():
            if ROOM_BUILD_TYPE[room_data['type']] == 'LivingDiningRoom':
                meeting_pos = None
                dining_pos = None
                if room_name not in house_layout:
                    continue
                for layout in house_layout[room_name]:
                    if layout['type'] == 'Meeting':
                        meeting_pos = layout['position']
                    elif layout['type'] == 'Dining':
                        dining_pos = layout['position']

                balcony_door_list = []
                balcony_win_list = []
                for door in room_data['Door']:
                    if 'Balcony' == ROOM_BUILD_TYPE[door['target_room_type']]:
                        if meeting_pos is not None:
                            dis = np.linalg.norm([door['obj_info']['pos'][0] - meeting_pos[0], door['obj_info']['pos'][2] - meeting_pos[2]])
                        elif dining_pos is not None:
                            dis = np.linalg.norm([door['obj_info']['pos'][0] - dining_pos[0], door['obj_info']['pos'][2] - dining_pos[2]])
                        else:
                            dis = 0
                        balcony_door_list.append([door, dis])
                for win in room_data['Window']:
                    if 'Balcony' == ROOM_BUILD_TYPE[win['target_room_type']] or ROOM_BUILD_TYPE[win['target_room_type']] == '':
                        if meeting_pos is not None:
                            dis = np.linalg.norm([win['obj_info']['pos'][0] - meeting_pos[0], win['obj_info']['pos'][2] - meeting_pos[2]])
                        elif dining_pos is not None:
                            dis = np.linalg.norm([win['obj_info']['pos'][0] - dining_pos[0], win['obj_info']['pos'][2] - dining_pos[2]])
                        else:
                            dis = 0
                        balcony_win_list.append([win, dis])

                if len(balcony_door_list) > 0:
                    balcony_door_list.sort(key=lambda x: x[-1])
                    src_pos = copy.deepcopy(balcony_door_list[0][0]['obj_info']['pos'])
                    livingDining_target.append([src_pos, balcony_door_list[0][0]['length']])
                elif len(balcony_win_list) > 0:
                    balcony_win_list.sort(key=lambda x: x[-1])
                    src_pos = copy.deepcopy(balcony_win_list[0][0]['obj_info']['pos'])
                    livingDining_target.append([src_pos, balcony_win_list[0][0]['length']])

            elif ROOM_BUILD_TYPE[room_data['type']] in PRIME_GENERAL_WALL_ROOM_TYPES:
                win_list = []
                for win in room_data['Window']:
                    win_list.append([win, -win['length']])
                if len(win_list) > 0:
                    win_list.sort(key=lambda x: x[-1])
                    src_pos = copy.deepcopy(win_list[0][0]['obj_info']['pos'])
                    masterBedRoom_target.append([src_pos, win_list[0][0]['length']])
        if len(livingDining_target) > 0:
            livingDining_target.sort(key=lambda x: x[-1])
            sun_src_pos = livingDining_target[0][0]
        elif len(masterBedRoom_target) > 0:
            masterBedRoom_target.sort(key=lambda x: x[-1])
            sun_src_pos = masterBedRoom_target[0][0]
        else:
            sun_src_pos = [0., 0, 10000.]

        sun_src_pos[1] = 0

        org_sun_src_pos = sun_src_pos.copy()
        for cur_time in ['daytime', 'dusk', 'night']:
            if cur_time == 'dusk':
                sun_angle = 20
            elif cur_time == 'daytime':
                sun_angle = 70
            else:
                sun_angle = 45
            sun_dis = 10000
            height = np.sin(sun_angle / 180 * np.pi) * sun_dis
            direction = np.array(sun_target_pos) - np.array(org_sun_src_pos)
            sun_src_pos = (np.array(sun_target_pos) - direction / np.linalg.norm(direction) * np.cos(sun_angle / 180 * np.pi) * sun_dis).tolist()
            sun_src_pos[1] = height
            global_light_full_day[cur_time]['sun_src_pos'] = sun_src_pos
            global_light_full_day[cur_time]['sun_target_pos'] = sun_target_pos

        house_info['global_light_params'] = dict()
        house_info['global_light_params']['outdoor_scene'] = global_light_full_day[self.cur_time]['outdoor_scene']
        house_info['global_light_params']['enable_sun'] = global_light_full_day[self.cur_time]['enable_sun']
        house_info['global_light_params']['dome_temperature'] = global_light_full_day[self.cur_time]['dome_temperature']
        house_info['global_light_params']['sun_color'] = global_light_full_day[self.cur_time]['sun_color']
        house_info['global_light_params']['sun_src_pos'] = global_light_full_day[self.cur_time]['sun_src_pos']
        house_info['global_light_params']['sun_target_pos'] = global_light_full_day[self.cur_time]['sun_target_pos']
        house_info['global_light_params']['full_day_param'] = global_light_full_day

        self.global_light_full_day = global_light_full_day

    def config_light(self, house_info, house_layout, debug_mode=False):
        if debug_mode:
            fig, ax = plt.subplots()
            plt.axis('equal')

        for room_id in house_info['rooms'].keys():
            room_info = house_info['rooms'][room_id]
            if room_id in house_layout:
                layout_info = house_layout[room_id]
            else:
                layout_info = []
            # print(room_info)
            if len(room_info['floor_pts']) < 3:
                continue
            self.config_room_light_v3(room_info, layout_info)
            if debug_mode:
                self.draw_room_light_layout(ax, room_info, layout_info, self.global_light_full_day[self.cur_time])
        if debug_mode:
            save_dir = os.path.join(os.path.dirname(__file__), '../temp/%s/' % house_info['id'])
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            save_path = save_dir + 'light_ploy.png'
            plt.savefig(save_path)

    def config_room_light_v2(self, room_info, layout_info):
        enable_light = True
        # window light
        enabled_win_light = True
        enabled_matrix_light = True
        if enable_light:

            # light layout
            light_win_door_num = 0
            visible_win_door_num = 0
            sun_direct = np.array(self.global_light_full_day[self.cur_time]['sun_target_pos']) - np.array(self.global_light_full_day[self.cur_time]['sun_src_pos'])
            sun_direct = sun_direct[[0, 2]] / np.linalg.norm(sun_direct[[0, 2]])

            light_win_door_num += len(room_info['Window'])
            for win in room_info['Window']:
                win_out_direct = np.array(win['normal']) / np.linalg.norm(win['normal'])
                if np.dot(win_out_direct, sun_direct) > 1e-3:
                    visible_win_door_num += 1
            for door in room_info['Door']:
                if door['length'] > 1.2 and ('Balcony' == ROOM_BUILD_TYPE[door['target_room_type']] or
                                             'LivingDiningRoom' == ROOM_BUILD_TYPE[door['target_room_type']]):
                    light_win_door_num += 1
                    door_out_direct = np.array(door['normal']) / np.linalg.norm(door['normal'])
                    if np.dot(door_out_direct, sun_direct) > 1e-3:
                        visible_win_door_num += 1

            light_params = {
                'daytime': {
                    'win_temperature': 7000.,
                    'win_inner_intensity': room_info['area'] * 10.,
                    'intensity_level': 5. if light_win_door_num > 1e-3 else 7.,
                    'fur_light_intensity': 1000,
                    'spot_light_intensity': 200,
                    'light_tem': 6500
                },
                'dusk': {
                    'win_temperature': 3000,
                    'win_inner_intensity': room_info['area'] * 10.,
                    'intensity_level': 3 if visible_win_door_num > 1e-3 else 5.,
                    'fur_light_intensity': 0.,
                    'spot_light_intensity': 200,
                    'light_tem': 3500
                },
                'night': {
                    'win_temperature': 8500,
                    'win_inner_intensity': room_info['area'] * 20.,
                    'intensity_level': 5.,
                    'fur_light_intensity': 1000,
                    'spot_light_intensity': 200,
                    'light_tem': int(np.random.choice([3000, 3250, 3500, 3750, 4000]))
                }
            }

            if enabled_win_light:
                for i, win in enumerate(room_info['Window']):
                    k = win['related']['Wall']
                    wall = [room_info['floor_pts'][k], room_info['floor_pts'][(k + 1) % len(room_info['floor_pts'])]]

                    direction, size, pos = self.add_sky_light(win, wall, inner_win=True)
                    full_day_param = {
                        'daytime': {
                            'intensity': size[0] * size[1] * light_params['daytime']['win_inner_intensity'],
                            'temperature': light_params['daytime']['win_temperature']
                        },
                        'dusk': {
                            'intensity': size[0] * size[1] * light_params['dusk']['win_inner_intensity'],
                            'temperature': light_params['dusk']['win_temperature']
                        },
                        'night': {
                            'intensity': size[0] * size[1] * light_params['night']['win_inner_intensity'],
                            'temperature': light_params['night']['win_temperature']
                        }
                    }
                    light_name = 'window_%s_area_light_%d' % (room_info['id'], i)
                    light = {
                        'name': light_name,
                        'type': 'AreaLight',
                        'direction': direction,
                        'intensity': full_day_param[self.cur_time]['intensity'],
                        'temperature': full_day_param[self.cur_time]['temperature'],
                        'size': size,
                        'pos': pos,
                        'full_day_param': full_day_param,
                        'related': {
                            'Window': win['name']
                        }
                    }
                    room_info['Light'].append(light)

                for i, door in enumerate(room_info['Door']):
                    if door['length'] > 1.2 and (ROOM_BUILD_TYPE[door['target_room_type']] == '' or ('LivingDiningRoom' == ROOM_BUILD_TYPE[door['target_room_type']] and 'Balcony' == ROOM_BUILD_TYPE[room_info['type']]) or 'Balcony' == ROOM_BUILD_TYPE[door['target_room_type']]):
                        k = door['related']['Wall']
                        wall = [room_info['floor_pts'][k],
                                room_info['floor_pts'][(k + 1) % len(room_info['floor_pts'])]]

                        direction, size, pos = self.add_sky_light(door, wall, inner_win=True)
                        full_day_param = {
                            'daytime': {
                                'intensity': size[0] * size[1] * light_params['daytime']['win_inner_intensity'],
                                'temperature': light_params['daytime']['win_temperature']
                            },
                            'dusk': {
                                'intensity': size[0] * size[1] * light_params['dusk']['win_inner_intensity'],
                                'temperature': light_params['dusk']['win_temperature']
                            },
                            'night': {
                                'intensity': size[0] * size[1] * light_params['night']['win_inner_intensity'],
                                'temperature': light_params['night']['win_temperature']
                            }
                        }
                        light_name = 'door_%s_area_light_%d' % (room_info['id'], i)
                        light = {
                            'name': light_name,
                            'type': 'AreaLight',
                            'direction': direction,
                            'intensity': full_day_param[self.cur_time]['intensity'],
                            'temperature': full_day_param[self.cur_time]['temperature'],
                            'size': size,
                            'pos': pos,
                            'full_day_param': full_day_param,
                            'related': {
                                'Door': door['name']
                            }
                        }
                        room_info['Light'].append(light)

            if True:
                # furniture light
                intensity_dict = {'sofa': 300,
                                  'table': 500,
                                  'cabinet': 400,
                                  'storage unit': 400,
                                  'shelf': 400,
                                  'bed': 300,
                                  'electronics': 300,
                                  'media unit': 300}

                light_height = 2.6
                spot_light_height = 2.
                fur_light_gap = 0.6
                forbiden_area = []
                for layout in layout_info:
                    if layout['type'] in ['Cabinet', 'Armoire'] and layout['size'][1] > 1.7:
                        forbiden_area += compute_furniture_rect(layout['size'], layout['position'], layout['rotation'])
                for layout in layout_info:
                    for fur_obj in layout['obj_list']:
                        if ('type' in fur_obj and 'lighting' in fur_obj['type']) or fur_obj['role'] == 'lighting':
                            full_day_param = {
                                'daytime': {
                                    'intensity': light_params['daytime']['fur_light_intensity'],
                                    'temperature': light_params['daytime']['light_tem']
                                },
                                'dusk': {
                                    'intensity': light_params['dusk']['fur_light_intensity'],
                                    'temperature': light_params['dusk']['light_tem']
                                },
                                'night': {
                                    'intensity': light_params['night']['fur_light_intensity'],
                                    'temperature': light_params['night']['light_tem']
                                }
                            }

                            light_name = 'furniture_%s_furniture_light_%s' % (room_info['id'], fur_obj['id'])
                            light = {
                                'name': light_name,
                                'type': 'FurnitureLight',
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'full_day_param': full_day_param,
                                'related': {
                                    'layout': fur_obj
                                }
                            }
                            room_info['Light'].append(light)

                    if layout['type'] in ['Meeting', 'Dining', 'Bed', 'Work', 'Rest', 'Cabinet']:
                        for obj in layout['obj_list']:
                            if obj['type'].split('/')[0] in ['sofa', 'table', 'cabinet', 'storage unit', 'shelf']:
                                size = np.array(obj['size']) * np.array(obj['scale']) / 100.
                                if size[1] < 1.7 or obj['type'].split('/')[0] not in ['cabinet', 'storage unit', 'shelf']:  # high cabinet
                                    area = compute_furniture_rect(size, obj['position'], obj['rotation'])
                                    area = np.array(area)
                                    p0 = area[0, :]
                                    p1 = area[1, :]
                                    p2 = area[2, :]
                                    # p0-p1: long axis
                                    # p2-p1: short axis
                                    if np.linalg.norm(p0 - p1) < np.linalg.norm(p1 - p2):
                                        p0 = area[2, :]
                                        p2 = area[0, :]
                                    # light_wide = 0.25 * min(size[0], size[2])
                                    if max(size[0], size[2]) > 1.:
                                        light_pts = [0.25 * p1 + 0.75 * p0 + (p2 - p1) * 0.5,
                                                     0.75 * p1 + 0.25 * p0 + (p2 - p1) * 0.5]
                                    else:
                                        light_pts = [0.5 * p1 + 0.5 * p0 + (p2 - p1) * 0.5]
                                    for i, pt in enumerate(light_pts):
                                        pos, status = self.adjust_light_pos(pt, forbiden_area,
                                                                            room_info['floor_pts'], fur_light_gap)
                                        if pos is None:
                                            continue
                                        full_day_param = {
                                            'daytime': {
                                                'intensity': light_params['daytime']['intensity_level'] * intensity_dict[obj['type'].split('/')[0]],
                                                'temperature': light_params['daytime']['light_tem']
                                            },
                                            'dusk': {
                                                'intensity': light_params['dusk']['intensity_level'] * intensity_dict[obj['type'].split('/')[0]],
                                                'temperature': light_params['dusk']['light_tem']
                                            },
                                            'night': {
                                                'intensity': light_params['night']['intensity_level'] * intensity_dict[obj['type'].split('/')[0]],
                                                'temperature': light_params['night']['light_tem']
                                            }
                                        }
                                        light_name = 'furniture_%s_spotlight_%s_%d' % (room_info['id'], obj['id'], i)
                                        light = {
                                            'name': light_name,
                                            'type': 'SpotLight',
                                            'direction': [0, -1, 0],
                                            'pos': [pos[0], spot_light_height, pos[1]],
                                            'intensity': full_day_param[self.cur_time]['intensity'],
                                            'temperature': full_day_param[self.cur_time]['temperature'],
                                            'physical_light': False,
                                            'full_day_param': full_day_param,
                                            'related': {
                                                'layout': obj
                                            }
                                        }
                                        room_info['Light'].append(light)
                                else:  ## TODO add vertical front area light for high cabinet
                                    # print('ignore high cabinet lighting')
                                    pass
                            elif obj['type'].split('/')[0] in ['bed']:
                                size = np.array(obj['size']) * np.array(obj['scale']) / 100.

                                base_pts = [[0.25 * size[0], 0,  -0.3 * size[2]],
                                            [-0.25 * size[0], 0, -0.3 * size[2]],
                                            [0, 0, -0.25 * size[2]],
                                            [0, 0, 0.25 * size[2]],
                                            ]
                                light_wides = [0.15 * min(size[0], size[2]),
                                               0.15 * min(size[0], size[2]),
                                               0.25 * min(size[0], size[2]),
                                               0.25 * min(size[0], size[2]),
                                              ]
                                r = R.from_quat(obj['rotation'])
                                light_pts = np.array(r.apply(base_pts)) + np.array(obj['position'])
                                light_pts = light_pts[:, [0, 2]]
                                for i, v in enumerate(zip(light_pts, light_wides)):
                                    pt, light_wide = v
                                    pos, status = self.adjust_light_pos(pt, forbiden_area, room_info['floor_pts'], fur_light_gap)
                                    if pos is None:
                                        continue
                                    full_day_param = {
                                        'daytime': {
                                            'intensity': light_params['daytime']['intensity_level'] * intensity_dict[
                                                obj['type'].split('/')[0]],
                                            'temperature': light_params['daytime']['light_tem']
                                        },
                                        'dusk': {
                                            'intensity': light_params['dusk']['intensity_level'] * intensity_dict[
                                                obj['type'].split('/')[0]],
                                            'temperature': light_params['dusk']['light_tem']
                                        },
                                        'night': {
                                            'intensity': light_params['night']['intensity_level'] * intensity_dict[
                                                obj['type'].split('/')[0]],
                                            'temperature': light_params['night']['light_tem']
                                        }
                                    }
                                    light_name = 'furniture_%s_spotlight_%s_%d' % (room_info['id'], obj['id'], i)
                                    light = {
                                        'name': light_name,
                                        'type': 'SpotLight',
                                        'direction': [0, -1, 0],
                                        'pos': [pos[0], spot_light_height, pos[1]],
                                        'intensity': full_day_param[self.cur_time]['intensity'],
                                        'temperature': full_day_param[self.cur_time]['temperature'],
                                        'physical_light': False,
                                        'full_day_param': full_day_param,
                                            'related': {
                                                'layout': obj
                                            }
                                        }
                                    room_info['Light'].append(light)
                    elif layout['type'] in ['Media']:
                        for obj in layout['obj_list']:
                            # if obj['type'].split('/')[0] in ['electronics', 'media unit']:
                            if obj['type'].split('/')[0] in ['media unit', 'cabinet', 'storage unit']:

                                size = np.array(obj['size']) * np.array(obj['scale']) / 100.
                                if obj['type'].split('/')[0] == 'media unit' and size[1] > 1.2:
                                    continue
                                base_pts = [[0.3 * size[0], 0, 0.2 * size[2]],
                                            [-0.3 * size[0], 0, 0.2 * size[2]],
                                            ]
                                r = R.from_quat(obj['rotation'])
                                light_pts = np.array(r.apply(base_pts)) + np.array(obj['position'])
                                light_pts = light_pts[:, [0, 2]]
                                for i, pt in enumerate(light_pts):
                                    pos, status = self.adjust_light_pos(pt, forbiden_area, room_info['floor_pts'], fur_light_gap)
                                    if pos is None:
                                        continue
                                    full_day_param = {
                                        'daytime': {
                                            'intensity': light_params['daytime']['intensity_level'] * intensity_dict[
                                                obj['type'].split('/')[0]],
                                            'temperature': light_params['daytime']['light_tem']
                                        },
                                        'dusk': {
                                            'intensity': light_params['dusk']['intensity_level'] * intensity_dict[
                                                obj['type'].split('/')[0]],
                                            'temperature': light_params['dusk']['light_tem']
                                        },
                                        'night': {
                                            'intensity': light_params['night']['intensity_level'] * intensity_dict[
                                                obj['type'].split('/')[0]],
                                            'temperature': light_params['night']['light_tem']
                                        }
                                    }
                                    light_name = 'furniture_%s_spotlight_%s_%d' % (room_info['id'], obj['id'], i)
                                    light = {
                                        'name': light_name,
                                        'type': 'SpotLight',
                                        'direction': [0, -1, 0],
                                        'pos': [pos[0], spot_light_height, pos[1]],
                                        'intensity': full_day_param[self.cur_time]['intensity'],
                                        'temperature': full_day_param[self.cur_time]['temperature'],
                                        'physical_light': False,
                                        'full_day_param': full_day_param,
                                        'related': {
                                                'layout': obj
                                            }
                                        }
                                    room_info['Light'].append(light)
                            # elif obj['type'].split('/')[0] in ['table', 'cabinet', 'storage unit']:
                            #     raise Exception('no tv media area???')

            # customized ceiling
            intensity_matrix = 1000
            light_wide = 0.5
            matrix_light_strip = 2.
            for cid, cust_ceiling in enumerate(room_info['CustomizedCeiling']):

                if cust_ceiling['type'] == 'hallway':
                    hallway_rect = np.array(cust_ceiling['layout_pts'])
                    hallway_center = np.mean(hallway_rect, axis=0)

                    # use spot light
                    hallway_edge_gap = 0.
                    hall_way_height = cust_ceiling['room_height'] - cust_ceiling['ceiling_height']
                    hallway_ceiling_floor = -np.sign(
                        hallway_rect - hallway_center) * hallway_edge_gap + hallway_rect

                    hallway_size = np.max(hallway_ceiling_floor, axis=0) - np.min(hallway_ceiling_floor, axis=0)
                    hallway_length_ind = np.argmax(hallway_size)
                    hallway_length = hallway_size[hallway_length_ind]

                    spot_light_interp = 1.5
                    light_num = hallway_length // spot_light_interp
                    light_start_gap = (hallway_length - light_num * spot_light_interp) / 2.
                    start_point = hallway_center - (hallway_length / 2. - light_start_gap) * (
                            np.array([0, 1]) == hallway_length_ind)
                    for i in range(int(light_num + 1)):
                        light_point = start_point + i * spot_light_interp * (np.array([0, 1]) == hallway_length_ind)
                        full_day_param = {
                            'daytime': {
                                'intensity': light_params['daytime']['spot_light_intensity'],
                                'temperature': light_params['daytime']['light_tem']
                            },
                            'dusk': {
                                'intensity': light_params['dusk']['spot_light_intensity'],
                                'temperature': light_params['dusk']['light_tem']
                            },
                            'night': {
                                'intensity': light_params['night']['spot_light_intensity'],
                                'temperature': light_params['night']['light_tem']
                            }
                        }

                        light_name = 'hallway_ceiling_%s_spotlight_%d' % (room_info['id'], i)
                        light = {
                            'name': light_name,
                            'type': 'SpotLight',
                            'temperature': full_day_param[self.cur_time]['temperature'],
                            'intensity': full_day_param[self.cur_time]['intensity'],
                            'pos': [light_point[0], hall_way_height - 0.01, light_point[1]],
                            'physical_light': True,
                            'direction': [0, -1, 0],
                            'full_day_param': full_day_param,
                            'related': {
                                'CustomizedCeiling': cust_ceiling['name']
                            }
                        }

                        room_info['Light'].append(light)
                    # area light
                    hallway_size = np.max(hallway_rect, axis=0) - np.min(hallway_rect, axis=0)
                    hallway_length_ind = np.argmax(hallway_size)
                    hallway_length = hallway_size[hallway_length_ind]
                    spot_light_interp = 2.
                    light_num = hallway_length // spot_light_interp
                    light_start_gap = (hallway_length - light_num * spot_light_interp) / 2.
                    start_point = hallway_center - (hallway_length / 2. - light_start_gap) * (
                            np.array([0, 1]) == hallway_length_ind)
                    light_wide = 0.3
                    full_day_param = {
                        'daytime': {
                            'intensity': 200 * light_wide * light_wide,
                            'temperature': light_params['daytime']['light_tem']
                        },
                        'dusk': {
                            'intensity': 200 * light_wide * light_wide,
                            'temperature': light_params['dusk']['light_tem']
                        },
                        'night': {
                            'intensity': 200 * light_wide * light_wide,
                            'temperature': light_params['night']['light_tem']
                        }
                    }
                    for i in range(int(light_num + 1)):
                        light_point = start_point + i * spot_light_interp * (np.array([0, 1]) == hallway_length_ind)
                        light_name = 'hallway_ceiling_%s_area_light_%d' % (room_info['id'], i)

                        pos, status = self.adjust_light_pos([light_point[0], light_point[1]], forbiden_area,
                                                            room_info['floor_pts'], light_wide)
                        if pos is not None:
                            light = {
                                'name': light_name,
                                'type': 'AreaLight',
                                'direction': [0, -1, 0],
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'size': [light_wide, light_wide],
                                'pos': [pos[0], light_height, pos[1]],
                                'full_day_param': full_day_param,
                                'related': {
                                    'CustomizedCeiling': cust_ceiling['name']
                                }
                            }
                            room_info['Light'].append(light)
                elif cust_ceiling['type'] == 'extra':
                    polygon = Polygon(cust_ceiling['layout_pts'])
                    if polygon.area > 2.:
                        light_name = 'extra_ceiling_%s_spotlight_%d' % (room_info['id'], cid)

                        full_day_param = {
                            'daytime': {
                                'intensity': light_params['daytime']['spot_light_intensity'],
                                'temperature': light_params['daytime']['light_tem']
                            },
                            'dusk': {
                                'intensity': light_params['dusk']['spot_light_intensity'],
                                'temperature': light_params['dusk']['light_tem']
                            },
                            'night': {
                                'intensity': light_params['night']['spot_light_intensity'],
                                'temperature': light_params['night']['light_tem']
                            }
                        }
                        pos = [polygon.centroid.x, cust_ceiling['room_height'] - cust_ceiling['ceiling_height'] - 0.01,
                                            polygon.centroid.y]
                        light = {
                            'name': light_name,
                            'type': 'SpotLight',
                            'direction': [0, -1, 0],
                            'pos': pos,
                            'intensity': full_day_param[self.cur_time]['intensity'],
                            'temperature': full_day_param[self.cur_time]['temperature'],
                            'physical_light': True,
                            'full_day_param': full_day_param,
                            'related': {
                                'CustomizedCeiling': cust_ceiling['name']
                            }
                        }
                        room_info['Light'].append(light)
                        light_wide = 0.5
                        pos, status = self.adjust_light_pos([pos[0], pos[2]], forbiden_area, room_info['floor_pts'],
                                                            light_wide)
                        if pos is not None:
                            full_day_param = {
                                'daytime': {
                                    'intensity': light_params['daytime']['intensity_level'] * 200 * light_wide * light_wide,
                                    'temperature': light_params['daytime']['light_tem']
                                },
                                'dusk': {
                                    'intensity': light_params['dusk']['intensity_level'] * 200 * light_wide * light_wide,
                                    'temperature': light_params['dusk']['light_tem']
                                },
                                'night': {
                                    'intensity': light_params['night']['intensity_level'] * 200 * light_wide * light_wide,
                                    'temperature': light_params['night']['light_tem']
                                }
                            }
                            light_name = 'extra_ceiling_%s_area_light_%d' % (room_info['id'], cid)
                            light = {
                                'name': light_name,
                                'type': 'AreaLight',
                                'direction': [0, -1, 0],
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'size': [light_wide, light_wide],
                                'pos': [pos[0], light_height, pos[1]],
                                'full_day_param': full_day_param,
                                'related': {
                                    'CustomizedCeiling': cust_ceiling['name']
                                }
                            }
                            room_info['Light'].append(light)
                elif cust_ceiling['type'] in ['living', 'dining', 'bed', 'work']:
                    # area lights matrix
                    if enabled_matrix_light:
                        ceiling_pts = cust_ceiling['layout_pts']
                        light_pos = self.add_area_light_matrix(ceiling_pts, gap_thresh=0.75, strip=matrix_light_strip)
                        for i, pos in enumerate(light_pos):
                            pos, status = self.adjust_light_pos(pos, forbiden_area, [], fur_light_gap)
                            if pos is None or abs(status) > matrix_light_strip * 0.3:
                                continue
                            #     use daytime light temperature
                            full_day_param = {
                                'daytime': {
                                    'intensity': light_params['daytime']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['daytime']['light_tem']
                                },
                                'dusk': {
                                    'intensity': light_params['dusk']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['dusk']['light_tem']
                                },
                                'night': {
                                    'intensity': light_params['night']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['night']['light_tem']
                                }
                            }
                            light_name = 'matrix_%s_area_light_%d_%d' % (room_info['id'], cid, i)
                            light = {
                                'name': light_name,
                                'type': 'AreaLight',
                                'direction': [0, -1, 0],
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'size': [light_wide, light_wide],
                                'pos': [pos[0], light_height, pos[1]],
                                'full_day_param': full_day_param,
                                'related': {
                                    'CustomizedCeiling': cust_ceiling['name']
                                }
                            }
                            room_info['Light'].append(light)

                    if 'SpotLight' in cust_ceiling['obj_info']:
                        for lid, layout in enumerate(cust_ceiling['obj_info']['SpotLight']):
                            lights = self.add_spot_light(layout,
                                                         cust_ceiling['obj_info']['ceiling'][0]['pos'],
                                                         cust_ceiling['obj_info']['ceiling'][0]['scale'],
                                                         cust_ceiling['obj_info']['ceiling'][0]['rot']
                                                         )
                            for pt in lights[1]:
                                full_day_param = {
                                    'daytime': {
                                        'intensity': light_params['daytime']['spot_light_intensity'],
                                        'temperature': light_params['daytime']['light_tem']
                                    },
                                    'dusk': {
                                        'intensity': light_params['dusk']['spot_light_intensity'],
                                        'temperature': light_params['dusk']['light_tem']
                                    },
                                    'night': {
                                        'intensity': light_params['night']['spot_light_intensity'],
                                        'temperature': light_params['night']['light_tem']
                                    }
                                }
                                light_name = 'ceiling_model_%s_spotlight_%d_%d' % (room_info['id'], cid, lid)
                                light = {
                                    'name': light_name,
                                    'type': 'SpotLight',
                                    'direction': [0, -1, 0],
                                    'pos': pt,
                                    'intensity': full_day_param[self.cur_time]['intensity'],
                                    'temperature': full_day_param[self.cur_time]['temperature'],
                                    'physical_light': True,
                                    'full_day_param': full_day_param,
                                    'related': {
                                        'CustomizedCeiling': cust_ceiling['name']
                                    }
                                }
                                room_info['Light'].append(light)
                    if 'MeshLight' in cust_ceiling['obj_info']:
                        for lid, layout in enumerate(cust_ceiling['obj_info']['MeshLight']):
                            verts, norms, faces, uv = self.add_strip_light_vertical(layout,
                                                                                    cust_ceiling['obj_info']['ceiling'][0]['pos'],
                                                                                    cust_ceiling['obj_info']['ceiling'][0]['scale'],
                                                                                    cust_ceiling['obj_info']['ceiling'][0]['rot']
                                                                                    )

                            strip_light_uid = '%s_CustomizedCeiling_strip_light_mesh_%d_%d' % (room_info['id'], cid, lid)
                            m = Mesh("Ceiling", strip_light_uid)
                            m.build_exists_mesh(verts, norms, uv, faces)
                            room_info['Mesh'].append({
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
                                    'CustomizedCeiling': cust_ceiling['name']
                                }
                            })
                            full_day_param = {
                                'daytime': {
                                    'intensity': light_params['daytime']['spot_light_intensity'],
                                    'temperature': light_params['daytime']['light_tem']
                                },
                                'dusk': {
                                    'intensity': light_params['dusk']['spot_light_intensity'],
                                    'temperature': light_params['dusk']['light_tem']
                                },
                                'night': {
                                    'intensity': light_params['night']['spot_light_intensity'],
                                    'temperature': light_params['night']['light_tem']
                                }
                            }
                            light = {
                                'name': strip_light_uid + '_light',
                                'type': 'MeshLight',
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'full_day_param': full_day_param,
                                'related': {
                                    'CustomizedCeiling': cust_ceiling['name'],
                                    'Mesh': strip_light_uid
                                }
                            }
                            room_info['Light'].append(light)

            # kitchen
            if ROOM_BUILD_TYPE[room_info['type']] == 'Kitchen':
                polygon = Polygon(room_info['floor_pts'])
                spot_light = [polygon.centroid.x, 2.3, polygon.centroid.y]

                pos, status = self.adjust_light_pos([spot_light[0], spot_light[2]], [], room_info['floor_pts'], 0.2)
                if pos is not None:
                    full_day_param = {
                        'daytime': {
                            'intensity': light_params['daytime']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['daytime']['light_tem']
                        },
                        'dusk': {
                            'intensity': light_params['dusk']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['dusk']['light_tem']
                        },
                        'night': {
                            'intensity': light_params['night']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['night']['light_tem']
                        }
                    }
                    light_name = 'kitchen_%s_area_light' % room_info['id']
                    light = {
                        'name': light_name,
                        'type': 'AreaLight',
                        'direction': [0, -1, 0],
                        'intensity': full_day_param[self.cur_time]['intensity'],
                        'temperature': full_day_param[self.cur_time]['temperature'],
                        'size': [0.2, 0.2],
                        'pos': [pos[0], spot_light[1], pos[1]],
                        'full_day_param': full_day_param,
                        'related': {}
                    }
                    room_info['Light'].append(light)
            if ROOM_BUILD_TYPE[room_info['type']] == 'Bathroom':
                polygon = Polygon(room_info['floor_pts'])
                area_light = [polygon.centroid.x, 2.3, polygon.centroid.y]
                pos, status = self.adjust_light_pos([area_light[0], area_light[2]], [], room_info['floor_pts'], 0.2)

                if pos is not None:
                    full_day_param = {
                        'daytime': {
                            'intensity': light_params['daytime']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['daytime']['light_tem']
                        },
                        'dusk': {
                            'intensity': light_params['dusk']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['dusk']['light_tem']
                        },
                        'night': {
                            'intensity': light_params['night']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['night']['light_tem']
                        }
                    }
                    light_name = 'bathroom_%s_area_light' % room_info['id']
                    light = {
                        'name': light_name,
                        'type': 'AreaLight',
                        'direction': [0, -1, 0],
                        'intensity': full_day_param[self.cur_time]['intensity'],
                        'temperature': full_day_param[self.cur_time]['temperature'],
                        'size': [0.2, 0.2],
                        'pos': [pos[0], area_light[1], pos[1]],
                        'full_day_param': full_day_param,
                        'related': {}
                    }
                    room_info['Light'].append(light)

    def config_room_light_v3(self, room_info, layout_info):
        enable_light = True
        # window light
        enabled_win_light = True
        enabled_matrix_light = True
        if enable_light:

            # light layout
            light_win_door_num = 0
            visible_win_door_num = 0
            sun_direct = np.array(self.global_light_full_day[self.cur_time]['sun_target_pos']) - np.array(self.global_light_full_day[self.cur_time]['sun_src_pos'])
            sun_direct = sun_direct[[0, 2]] / np.linalg.norm(sun_direct[[0, 2]])

            light_win_door_num += len(room_info['Window'])
            for win in room_info['Window']:
                win_out_direct = np.array(win['normal']) / np.linalg.norm(win['normal'])
                if np.dot(win_out_direct, sun_direct) > 1e-3:
                    visible_win_door_num += 1
            for door in room_info['Door']:
                if door['length'] > 1.2 and ('Balcony' == ROOM_BUILD_TYPE[door['target_room_type']] or
                                             'LivingDiningRoom' == ROOM_BUILD_TYPE[door['target_room_type']]):
                    light_win_door_num += 1
                    door_out_direct = np.array(door['normal']) / np.linalg.norm(door['normal'])
                    if np.dot(door_out_direct, sun_direct) > 1e-3:
                        visible_win_door_num += 1

            light_params = {
                'daytime': {
                    'win_temperature': 7000.,
                    'win_inner_intensity': room_info['area'] * 8.,
                    'intensity_level': 4.5 if light_win_door_num > 1e-3 else 7.,
                    'fur_light_intensity': 1000,
                    'spot_light_intensity': 100,
                    'light_tem': 6500
                },
                'dusk': {
                    'win_temperature': 3000,
                    'win_inner_intensity': room_info['area'] * 10.,
                    'intensity_level': 3 if visible_win_door_num > 1e-3 else 5.,
                    'fur_light_intensity': 0.,
                    'spot_light_intensity': 200,
                    'light_tem': 3500
                },
                'night': {
                    'win_temperature': 8500,
                    'win_inner_intensity': room_info['area'] * 20.,
                    'intensity_level': 5.,
                    'fur_light_intensity': 1000,
                    'spot_light_intensity': 200,
                    'light_tem': int(np.random.choice([3000, 3250, 3500, 3750, 4000]))
                }
            }

            if enabled_win_light:
                for i, win in enumerate(room_info['Window']):
                    k = win['related']['Wall']
                    wall = [room_info['floor_pts'][k], room_info['floor_pts'][(k + 1) % len(room_info['floor_pts'])]]

                    direction, size, pos = self.add_sky_light(win, wall, inner_win=True)
                    full_day_param = {
                        'daytime': {
                            'intensity': size[0] * size[1] * light_params['daytime']['win_inner_intensity'],
                            'temperature': light_params['daytime']['win_temperature']
                        },
                        'dusk': {
                            'intensity': size[0] * size[1] * light_params['dusk']['win_inner_intensity'],
                            'temperature': light_params['dusk']['win_temperature']
                        },
                        'night': {
                            'intensity': size[0] * size[1] * light_params['night']['win_inner_intensity'],
                            'temperature': light_params['night']['win_temperature']
                        }
                    }
                    light_name = 'window_%s_area_light_%d' % (room_info['id'], i)
                    light = {
                        'name': light_name,
                        'type': 'AreaLight',
                        'direction': direction,
                        'intensity': full_day_param[self.cur_time]['intensity'],
                        'temperature': full_day_param[self.cur_time]['temperature'],
                        'size': size,
                        'pos': pos,
                        'full_day_param': full_day_param,
                        'related': {
                            'Window': win['name']
                        }
                    }
                    room_info['Light'].append(light)

                for i, door in enumerate(room_info['Door']):
                    if door['length'] > 1.2 and (ROOM_BUILD_TYPE[door['target_room_type']] == '' or ('LivingDiningRoom' == ROOM_BUILD_TYPE[door['target_room_type']] and 'Balcony' == ROOM_BUILD_TYPE[room_info['type']]) or 'Balcony' == ROOM_BUILD_TYPE[door['target_room_type']]):
                        k = door['related']['Wall']
                        wall = [room_info['floor_pts'][k],
                                room_info['floor_pts'][(k + 1) % len(room_info['floor_pts'])]]

                        direction, size, pos = self.add_sky_light(door, wall, inner_win=True)
                        full_day_param = {
                            'daytime': {
                                'intensity': size[0] * size[1] * light_params['daytime']['win_inner_intensity'],
                                'temperature': light_params['daytime']['win_temperature']
                            },
                            'dusk': {
                                'intensity': size[0] * size[1] * light_params['dusk']['win_inner_intensity'],
                                'temperature': light_params['dusk']['win_temperature']
                            },
                            'night': {
                                'intensity': size[0] * size[1] * light_params['night']['win_inner_intensity'],
                                'temperature': light_params['night']['win_temperature']
                            }
                        }
                        light_name = 'door_%s_area_light_%d' % (room_info['id'], i)
                        light = {
                            'name': light_name,
                            'type': 'AreaLight',
                            'direction': direction,
                            'intensity': full_day_param[self.cur_time]['intensity'],
                            'temperature': full_day_param[self.cur_time]['temperature'],
                            'size': size,
                            'pos': pos,
                            'full_day_param': full_day_param,
                            'related': {
                                'Door': door['name']
                            }
                        }
                        room_info['Light'].append(light)

            if True:
                # furniture light
                intensity_dict = {'sofa': 300,
                                  'table': 500,
                                  'cabinet': 400,
                                  'storage unit': 400,
                                  'shelf': 400,
                                  'bed': 300,
                                  'electronics': 300,
                                  'media unit': 300}

                light_height = 2.6
                spot_light_height = 2.
                fur_light_gap = 0.6
                forbiden_area = []
                for layout in layout_info:
                    if layout['type'] in ['Cabinet', 'Armoire'] and layout['size'][1] > 1.7:
                        forbiden_area += compute_furniture_rect(layout['size'], layout['position'], layout['rotation'])
                for layout in layout_info:
                    for fur_obj in layout['obj_list']:
                        if ('type' in fur_obj and 'lighting' in fur_obj['type']) or fur_obj['role'] == 'lighting':
                            full_day_param = {
                                'daytime': {
                                    'intensity': light_params['daytime']['fur_light_intensity'],
                                    'temperature': light_params['daytime']['light_tem']
                                },
                                'dusk': {
                                    'intensity': light_params['dusk']['fur_light_intensity'],
                                    'temperature': light_params['dusk']['light_tem']
                                },
                                'night': {
                                    'intensity': light_params['night']['fur_light_intensity'],
                                    'temperature': light_params['night']['light_tem']
                                }
                            }

                            light_name = 'furniture_%s_furniture_light_%s' % (room_info['id'], fur_obj['id'])
                            light = {
                                'name': light_name,
                                'type': 'FurnitureLight',
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'full_day_param': full_day_param,
                                'related': {
                                    'layout': fur_obj
                                }
                            }
                            room_info['Light'].append(light)

            # customized ceiling
            # area lights matrix
            intensity_matrix = 250 * 1.0
            for cid, cust_ceiling in enumerate(room_info['CustomizedCeiling']):
                light_height = cust_ceiling['room_height'] - cust_ceiling['ceiling_height'] - 0.003
                if cust_ceiling['type'] == 'hallway':
                    hallway_rect = np.array(cust_ceiling['layout_pts'])
                    hallway_center = np.mean(hallway_rect, axis=0)

                    # use spot light
                    hallway_edge_gap = 0.
                    hall_way_height = cust_ceiling['room_height'] - cust_ceiling['ceiling_height']
                    hallway_ceiling_floor = -np.sign(
                        hallway_rect - hallway_center) * hallway_edge_gap + hallway_rect

                    hallway_size = np.max(hallway_ceiling_floor, axis=0) - np.min(hallway_ceiling_floor, axis=0)
                    hallway_length_ind = np.argmax(hallway_size)
                    hallway_length = hallway_size[hallway_length_ind]

                    spot_light_interp = 1.5
                    light_num = hallway_length // spot_light_interp
                    light_start_gap = (hallway_length - light_num * spot_light_interp) / 2.
                    start_point = hallway_center - (hallway_length / 2. - light_start_gap) * (
                            np.array([0, 1]) == hallway_length_ind)
                    for i in range(int(light_num + 1)):
                        light_point = start_point + i * spot_light_interp * (np.array([0, 1]) == hallway_length_ind)
                        full_day_param = {
                            'daytime': {
                                'intensity': light_params['daytime']['spot_light_intensity'],
                                'temperature': light_params['daytime']['light_tem']
                            },
                            'dusk': {
                                'intensity': light_params['dusk']['spot_light_intensity'],
                                'temperature': light_params['dusk']['light_tem']
                            },
                            'night': {
                                'intensity': light_params['night']['spot_light_intensity'],
                                'temperature': light_params['night']['light_tem']
                            }
                        }

                        light_name = 'hallway_ceiling_%s_spotlight_%d' % (room_info['id'], i)
                        light = {
                            'name': light_name,
                            'type': 'SpotLight',
                            'temperature': full_day_param[self.cur_time]['temperature'],
                            'intensity': full_day_param[self.cur_time]['intensity'],
                            'pos': [light_point[0], light_height, light_point[1]],
                            'physical_light': True,
                            'direction': [0, -1, 0],
                            'full_day_param': full_day_param,
                            'related': {
                                'CustomizedCeiling': cust_ceiling['name']
                            }
                        }

                        room_info['Light'].append(light)
                    # area light
                    hallway_size = np.max(hallway_rect, axis=0) - np.min(hallway_rect, axis=0)
                    hallway_length_ind = np.argmax(hallway_size)
                    hallway_length = hallway_size[hallway_length_ind]
                    hallway_area_light_interp = np.min(hallway_size) / 2.
                    light_num = hallway_length // hallway_area_light_interp
                    light_start_gap = (hallway_length - light_num * hallway_area_light_interp) / 2.
                    start_point = hallway_center - (hallway_length / 2. - light_start_gap) * (
                            np.array([0, 1]) == hallway_length_ind)
                    light_wide = hallway_area_light_interp
                    full_day_param = {
                        'daytime': {
                            'intensity': intensity_matrix * light_wide * light_wide * 2,
                            'temperature': light_params['daytime']['light_tem']
                        },
                        'dusk': {
                            'intensity': intensity_matrix * light_wide * light_wide,
                            'temperature': light_params['dusk']['light_tem']
                        },
                        'night': {
                            'intensity': intensity_matrix * light_wide * light_wide,
                            'temperature': light_params['night']['light_tem']
                        }
                    }
                    for i in range(int(light_num + 1)):
                        light_point = start_point + i * hallway_area_light_interp * (np.array([0, 1]) == hallway_length_ind)
                        light_name = 'hallway_ceiling_%s_area_light_%d' % (room_info['id'], i)

                        pos, status = self.adjust_light_pos([light_point[0], light_point[1]], forbiden_area,
                                                            room_info['floor_pts'], max(light_wide - 0.01, 0.1))
                        if pos is not None:
                            light = {
                                'name': light_name,
                                'type': 'AreaLight',
                                'direction': [0, -1, 0],
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'size': [light_wide, light_wide],
                                'pos': [pos[0], light_height, pos[1]],
                                'full_day_param': full_day_param,
                                'related': {
                                    'CustomizedCeiling': cust_ceiling['name']
                                }
                            }
                            room_info['Light'].append(light)
                elif cust_ceiling['type'] == 'extra' and False:
                    polygon = Polygon(cust_ceiling['layout_pts'])
                    if polygon.area > 0.3:
                        light_name = 'extra_ceiling_%s_spotlight_%d' % (room_info['id'], cid)

                        full_day_param = {
                            'daytime': {
                                'intensity': light_params['daytime']['spot_light_intensity'],
                                'temperature': light_params['daytime']['light_tem']
                            },
                            'dusk': {
                                'intensity': light_params['dusk']['spot_light_intensity'],
                                'temperature': light_params['dusk']['light_tem']
                            },
                            'night': {
                                'intensity': light_params['night']['spot_light_intensity'],
                                'temperature': light_params['night']['light_tem']
                            }
                        }
                        pos = [polygon.centroid.x, light_height, polygon.centroid.y]
                        light = {
                            'name': light_name,
                            'type': 'SpotLight',
                            'direction': [0, -1, 0],
                            'pos': pos,
                            'intensity': full_day_param[self.cur_time]['intensity'],
                            'temperature': full_day_param[self.cur_time]['temperature'],
                            'physical_light': True,
                            'full_day_param': full_day_param,
                            'related': {
                                'CustomizedCeiling': cust_ceiling['name']
                            }
                        }
                        room_info['Light'].append(light)
                        light_wide = 0.1
                        pos, status = self.adjust_light_pos([pos[0], pos[2]], forbiden_area, room_info['floor_pts'],
                                                            light_wide)
                        if pos is not None:
                            full_day_param = {
                                'daytime': {
                                    'intensity': light_params['daytime']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['daytime']['light_tem']
                                },
                                'dusk': {
                                    'intensity': light_params['dusk']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['dusk']['light_tem']
                                },
                                'night': {
                                    'intensity': light_params['night']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['night']['light_tem']
                                }
                            }
                            light_name = 'extra_ceiling_%s_area_light_%d' % (room_info['id'], cid)
                            light = {
                                'name': light_name,
                                'type': 'AreaLight',
                                'direction': [0, -1, 0],
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'size': [light_wide, light_wide],
                                'pos': [pos[0], light_height, pos[1]],
                                'full_day_param': full_day_param,
                                'related': {
                                    'CustomizedCeiling': cust_ceiling['name']
                                }
                            }
                            room_info['Light'].append(light)
                elif cust_ceiling['type'] in ['living', 'dining', 'bed', 'work', 'extra']:

                    light_wide = 0.5
                    gap_thresh = 0.5
                    matrix_light_strip = light_wide
                    if enabled_matrix_light:
                        ceiling_pts = cust_ceiling['layout_pts']
                        light_pos = self.add_area_light_matrix(ceiling_pts, gap_thresh=gap_thresh, strip=matrix_light_strip)
                        for i, pos in enumerate(light_pos):
                            pos, status = self.adjust_light_pos(pos, forbiden_area, [], fur_light_gap)
                            if pos is None or abs(status) > matrix_light_strip * 0.3:
                                continue
                            #     use daytime light temperature
                            full_day_param = {
                                'daytime': {
                                    'intensity': light_params['daytime']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['daytime']['light_tem']
                                },
                                'dusk': {
                                    'intensity': light_params['dusk']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['dusk']['light_tem']
                                },
                                'night': {
                                    'intensity': light_params['night']['intensity_level'] * intensity_matrix * light_wide * light_wide,
                                    'temperature': light_params['night']['light_tem']
                                }
                            }
                            light_name = 'matrix_%s_area_light_%d_%d' % (room_info['id'], cid, i)
                            light = {
                                'name': light_name,
                                'type': 'AreaLight',
                                'direction': [0, -1, 0],
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'size': [light_wide, light_wide],
                                'pos': [pos[0], light_height, pos[1]],
                                'full_day_param': full_day_param,
                                'related': {
                                    'CustomizedCeiling': cust_ceiling['name']
                                }
                            }
                            room_info['Light'].append(light)

                    if 'SpotLight' in cust_ceiling['obj_info']:
                        for lid, layout in enumerate(cust_ceiling['obj_info']['SpotLight']):
                            lights = self.add_spot_light(layout,
                                                         cust_ceiling['obj_info']['ceiling'][0]['pos'],
                                                         cust_ceiling['obj_info']['ceiling'][0]['scale'],
                                                         cust_ceiling['obj_info']['ceiling'][0]['rot']
                                                         )
                            for pt in lights[1]:
                                full_day_param = {
                                    'daytime': {
                                        'intensity': light_params['daytime']['spot_light_intensity'],
                                        'temperature': light_params['daytime']['light_tem']
                                    },
                                    'dusk': {
                                        'intensity': light_params['dusk']['spot_light_intensity'],
                                        'temperature': light_params['dusk']['light_tem']
                                    },
                                    'night': {
                                        'intensity': light_params['night']['spot_light_intensity'],
                                        'temperature': light_params['night']['light_tem']
                                    }
                                }
                                light_name = 'ceiling_model_%s_spotlight_%d_%d' % (room_info['id'], cid, lid)
                                light = {
                                    'name': light_name,
                                    'type': 'SpotLight',
                                    'direction': [0, -1, 0],
                                    'pos': pt,
                                    'intensity': full_day_param[self.cur_time]['intensity'],
                                    'temperature': full_day_param[self.cur_time]['temperature'],
                                    'physical_light': True,
                                    'full_day_param': full_day_param,
                                    'related': {
                                        'CustomizedCeiling': cust_ceiling['name']
                                    }
                                }
                                room_info['Light'].append(light)
                    if 'MeshLight' in cust_ceiling['obj_info']:
                        for lid, layout in enumerate(cust_ceiling['obj_info']['MeshLight']):
                            verts, norms, faces, uv = self.add_strip_light_vertical(layout,
                                                                                    cust_ceiling['obj_info']['ceiling'][0]['pos'],
                                                                                    cust_ceiling['obj_info']['ceiling'][0]['scale'],
                                                                                    cust_ceiling['obj_info']['ceiling'][0]['rot']
                                                                                    )

                            strip_light_uid = '%s_CustomizedCeiling_strip_light_mesh_%d_%d' % (room_info['id'], cid, lid)
                            m = Mesh("Ceiling", strip_light_uid)
                            m.build_exists_mesh(verts, norms, uv, faces)
                            room_info['Mesh'].append({
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
                                    'CustomizedCeiling': cust_ceiling['name']
                                }
                            })
                            full_day_param = {
                                'daytime': {
                                    'intensity': light_params['daytime']['spot_light_intensity'],
                                    'temperature': light_params['daytime']['light_tem']
                                },
                                'dusk': {
                                    'intensity': light_params['dusk']['spot_light_intensity'],
                                    'temperature': light_params['dusk']['light_tem']
                                },
                                'night': {
                                    'intensity': light_params['night']['spot_light_intensity'],
                                    'temperature': light_params['night']['light_tem']
                                }
                            }
                            light = {
                                'name': strip_light_uid + '_light',
                                'type': 'MeshLight',
                                'intensity': full_day_param[self.cur_time]['intensity'],
                                'temperature': full_day_param[self.cur_time]['temperature'],
                                'full_day_param': full_day_param,
                                'related': {
                                    'CustomizedCeiling': cust_ceiling['name'],
                                    'Mesh': strip_light_uid
                                }
                            }
                            room_info['Light'].append(light)

            # kitchen
            if ROOM_BUILD_TYPE[room_info['type']] == 'Kitchen':
                polygon = Polygon(room_info['floor_pts'])
                spot_light = [polygon.centroid.x, 2.3, polygon.centroid.y]

                pos, status = self.adjust_light_pos([spot_light[0], spot_light[2]], [], room_info['floor_pts'], 0.2)
                if pos is not None:
                    full_day_param = {
                        'daytime': {
                            'intensity': light_params['daytime']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['daytime']['light_tem']
                        },
                        'dusk': {
                            'intensity': light_params['dusk']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['dusk']['light_tem']
                        },
                        'night': {
                            'intensity': light_params['night']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['night']['light_tem']
                        }
                    }
                    light_name = 'kitchen_%s_area_light' % room_info['id']
                    light = {
                        'name': light_name,
                        'type': 'AreaLight',
                        'direction': [0, -1, 0],
                        'intensity': full_day_param[self.cur_time]['intensity'],
                        'temperature': full_day_param[self.cur_time]['temperature'],
                        'size': [0.2, 0.2],
                        'pos': [pos[0], spot_light[1], pos[1]],
                        'full_day_param': full_day_param,
                        'related': {}
                    }
                    room_info['Light'].append(light)
            if ROOM_BUILD_TYPE[room_info['type']] == 'Bathroom':
                polygon = Polygon(room_info['floor_pts'])
                area_light = [polygon.centroid.x, 2.3, polygon.centroid.y]
                pos, status = self.adjust_light_pos([area_light[0], area_light[2]], [], room_info['floor_pts'], 0.2)

                if pos is not None:
                    full_day_param = {
                        'daytime': {
                            'intensity': light_params['daytime']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['daytime']['light_tem']
                        },
                        'dusk': {
                            'intensity': light_params['dusk']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['dusk']['light_tem']
                        },
                        'night': {
                            'intensity': light_params['night']['intensity_level'] * 10000 * 0.2 * 0.2,
                            'temperature': light_params['night']['light_tem']
                        }
                    }
                    light_name = 'bathroom_%s_area_light' % room_info['id']
                    light = {
                        'name': light_name,
                        'type': 'AreaLight',
                        'direction': [0, -1, 0],
                        'intensity': full_day_param[self.cur_time]['intensity'],
                        'temperature': full_day_param[self.cur_time]['temperature'],
                        'size': [0.2, 0.2],
                        'pos': [pos[0], area_light[1], pos[1]],
                        'full_day_param': full_day_param,
                        'related': {}
                    }
                    room_info['Light'].append(light)

    def config_room_light_v1(self, info):
        defalt_light_temperature = 6500
        # window light
        biggest_win = None
        biggest_win_wall = None
        biggest_area = 0.
        for k, v in info.room_info['WallInner'].mesh_info.items():
            win_id = 0
            for win in v['Window']:
                wall = [info.floor_pts[k], info.floor_pts[(k + 1) % len(info.floor_pts)]]
                light = self.add_sky_light(win, wall, 1200, defalt_light_temperature, True)
                info.room_info['light']['AreaLight'].append(light)

                win_id += 1
                if win.window_height * win.window_length > biggest_area:
                    biggest_win = win
                    biggest_win_wall = wall
                    biggest_area = win.window_height * win.window_length
        if biggest_win is not None:
            light = self.add_sky_light(biggest_win, biggest_win_wall, 3000, defalt_light_temperature, False)
            info.room_info['light']['AreaLight'].append(light)

        # forbidden area: too high cabinet
        forbiden_area = []
        for layout in info.layout:
            if layout['type'] == 'Cabinet' and layout['size'][1] > 1.9:
                forbiden_area += compute_furniture_rect(layout['size'], layout['position'], layout['rotation'])
        # forbidden floor edge limit
        # meeting, media, bed
        light_wide = 0.5
        light_height = 2.6
        intensity = 1300
        for layout in info.layout:
            if layout['type'] in ['Meeting', 'Dining', 'Bed']:
                area = compute_furniture_rect(layout['size'], layout['position'], layout['rotation'])
                area = 0.99 * (np.array(area) - np.mean(area, axis=0)) + np.mean(area, axis=0)

                for i in range(4):
                    pos, status = self.adjust_light_pos(area[i], forbiden_area, info.floor_pts, light_wide * 1.)
                    if pos is None:
                        continue
                    light = {
                        'direction': [0, -1, 0],
                        'intensity': intensity,
                        'temperature': defalt_light_temperature,
                        'size': [light_wide, light_wide],
                        'pos': [pos[0], light_height, pos[1]],
                        'win': False,
                        'type': 'AreaLight'
                    }
                    info.room_info['light']['AreaLight'].append(light)

            elif layout['type'] == 'Media':
                area = compute_furniture_rect(layout['size'], layout['position'], layout['rotation'])
                area_center = np.mean(area, axis=0)

                pos, status = self.adjust_light_pos(area_center, forbiden_area, info.floor_pts, light_wide * 1.5)
                if pos is not None:
                    light = {
                        'direction': [0, -1, 0],
                        'intensity': intensity,
                        'temperature': defalt_light_temperature,
                        'size': [light_wide, light_wide],
                        'pos': [pos[0], light_height, pos[1]],
                        'win': False,
                        'type': 'AreaLight'
                    }
                    info.room_info['light']['AreaLight'].append(light)
        # kitchen light
        intensity = 800
        if info.room_type == 'Kitchen':
            polygon = Polygon(info.floor_pts)
            spot_light = [polygon.centroid.x, 2.3, polygon.centroid.y]
            pos, status = self.adjust_light_pos([spot_light[0], spot_light[2]], [], info.floor_pts, 0.2)
            light = {
                'direction': [0, -1, 0],
                'pos': spot_light,
                'intensity': intensity,
                'temperature': defalt_light_temperature,
                'type': 'SpotLight',
                'physical_light': True
            }
            info.room_info['light']['SpotLight'].append(light)
            if pos is not None:
                light = {
                    'direction': [0, -1, 0],
                    'intensity': intensity,
                    'temperature': defalt_light_temperature,
                    'size': [0.2, 0.2],
                    'pos': spot_light,
                    'win': False,
                    'type': 'AreaLight'
                }
                info.room_info['light']['AreaLight'].append(light)
        if info.room_type == 'Bathroom':
            polygon = Polygon(info.floor_pts)
            area_light = [polygon.centroid.x, 2.3, polygon.centroid.y]
            pos, status = self.adjust_light_pos([area_light[0], area_light[2]], [], info.floor_pts, 0.2)

            if pos is not None:
                light = {
                    'direction': [0, -1, 0],
                    'intensity': intensity,
                    'temperature': defalt_light_temperature,
                    'size': [0.2, 0.2],
                    'pos': [pos[0], area_light[1], pos[1]],
                    'win': False,
                    'type': 'AreaLight'
                }
                info.room_info['light']['AreaLight'].append(light)
        # living and dining
        intensity = 1300

        for cid, cust_ceiling in enumerate(info.room_info['CustomizedCeiling'].customized_ceiling):
            for lid, layout in enumerate(cust_ceiling['light']['SpotLight']):
                lights = self.add_spot_light(layout,
                                             cust_ceiling['instance_info']['pos'],
                                             cust_ceiling['instance_info']['scale'],
                                             cust_ceiling['instance_info']['rot']
                                             )
                for pt in lights[1]:
                    light = {
                        'direction': [0, -1, 0],
                        'pos': pt,
                        'intensity': intensity,
                        'temperature': defalt_light_temperature,
                        'type': 'SpotLight',
                        'physical_light': True
                    }
                    info.room_info['light']['SpotLight'].append(light)
            for lid, layout in enumerate(cust_ceiling['light']['StripLight']):
                verts, norms, faces, uv = self.add_strip_light_vertical(layout,
                                                                        cust_ceiling['instance_info']['pos'],
                                                                        cust_ceiling['instance_info']['scale'],
                                                                        cust_ceiling['instance_info']['rot']
                                                                        )

                strip_light_uid = '%s_CustomizedCeiling_strip_light_mesh_%d_%d' % (info.room_id, cid, lid)
                mesh = Mesh("Ceiling", strip_light_uid)
                mesh.build_exists_mesh(verts, norms, uv, faces)
                info.room_info['Ceiling'].mesh_info.append(mesh)
                light = {
                    'ref': strip_light_uid,
                    'intensity': intensity,
                    'temperature': defalt_light_temperature,
                    'type': 'StripLight'
                }
                info.room_info['light']['StripLight'].append(light)

        # hallway light
        for hallway in info.room_info['CustomizedCeiling'].hallway:
            for strip_light in hallway['light']['StripLight']:
                light = {
                    'ref': strip_light,
                    'intensity': intensity,
                    'temperature': defalt_light_temperature,
                    'type': 'StripLight'
                }
                info.room_info['light']['StripLight'].append(light)
            for spot_light in hallway['light']['SpotLight']:
                light = {
                    'direction': [0, -1, 0],
                    'pos': spot_light,
                    'intensity': intensity,
                    'temperature': defalt_light_temperature,
                    'type': 'SpotLight',
                    'physical_light': True
                }
                info.room_info['light']['SpotLight'].append(light)
            for spot_light in hallway['light']['AreaLight']:
                light_wide = 0.3
                pos, status = self.adjust_light_pos([spot_light[0], spot_light[2]], forbiden_area, info.floor_pts, light_wide)
                if pos is not None:
                    light = {
                        'direction': [0, -1, 0],
                        'intensity': intensity,
                        'temperature': defalt_light_temperature,
                        'size': [light_wide, light_wide],
                        'pos': [pos[0], light_height, pos[1]],
                        'win': False,
                        'type': 'AreaLight'
                    }
                    info.room_info['light']['AreaLight'].append(light)

        for spot_light in info.room_info['CustomizedCeiling'].extra_spot_light:
            light = {
                'direction': [0, -1, 0],
                'pos': spot_light,
                'intensity': intensity,
                'temperature': defalt_light_temperature,
                'type': 'SpotLight',
                'physical_light': True
            }
            info.room_info['light']['SpotLight'].append(light)
            light_wide = 0.3
            pos, status = self.adjust_light_pos([spot_light[0], spot_light[2]], forbiden_area, info.floor_pts, light_wide)
            if pos is not None:
                light = {
                    'direction': [0, -1, 0],
                    'intensity': intensity,
                    'temperature': defalt_light_temperature,
                    'size': [light_wide, light_wide],
                    'pos': [pos[0], light_height, pos[1]],
                    'win': False,
                    'type': 'AreaLight'
                }
                info.room_info['light']['AreaLight'].append(light)

    def draw_room_light_layout(self, ax, info, layouts, global_light_params):

        ax.plot(np.array(info['floor_pts'])[list(np.arange(len(info['floor_pts']))) + [0], 0], np.array(info['floor_pts'])[list(np.arange(len(info['floor_pts']))) + [0], 1])

        for layout in layouts:
            if layout['type'] in ['Meeting', 'Dining', 'Bed', 'Media', 'Work', 'Rest', 'Cabinet']:
                for fur in layout['obj_list']:
                    pos = fur['position']
                    rot = fur['rotation']
                    scale = fur['scale']
                    obj_type = fur['type']
                    obj_size = fur['size']
                    obj_size = [i / 100. for i in obj_size]
                    size = [obj_size[i] * scale[i] for i in range(len(scale))]

                    if obj_type.split('/')[0] not in ['electronics', 'media unit', 'sofa', 'table', 'cabinet', 'storage unit', 'shelf', 'bed']:
                        continue
                    # if size[1] > 1.7:
                    #     continue
                    base_pts = np.array([[0, 0, 0], [0, size[1], 0], [size[0], size[1], 0], [size[0], 0, 0],
                                         [0, 0, size[2]], [0, size[1], size[2]], [size[0], size[1], size[2]],
                                         [size[0], 0, size[2]]])
                    base_pts -= np.mean(base_pts, axis=0)
                    r = R.from_quat(rot)
                    cvt_pts = r.apply(base_pts)
                    tar_pts = cvt_pts + np.array(pos)
                    projected_pts = tar_pts[:, [0, 2]]
                    minc = np.min(projected_pts, axis=0)
                    maxc = np.max(projected_pts, axis=0)
                    convex_pts = np.array([[minc[0], minc[1]],
                                           [minc[0], maxc[1]],
                                           [maxc[0], maxc[1]],
                                           [maxc[0], minc[1]],
                                           [minc[0], minc[1]]]
                                          )
                    ax.plot(convex_pts[:, 0], convex_pts[:, 1], color='r')
                    ax.text(pos[0], pos[2] - 0.2, obj_type.split('/')[0], color='r')

        for light in info['Light']:
            if light['type'] == 'SpotLight':
                size = None

                light_type = 'spot'
                phisical = light['physical_light']
                pos = light['pos']
                direction = light['direction']
                intensity = light['intensity']
                text = str(int(intensity))
                self.draw_light(ax, pos, direction, light_type, size, text, phisical=phisical)

            if light['type'] == 'AreaLight':

                light_type = 'area'
                pos = light['pos']
                direction = light['direction']
                intensity = light['intensity']
                text = str(int(intensity))
                size = light['size']
                self.draw_light(ax, pos, direction, light_type, size, text)
        if global_light_params['enable_sun']:
            sun_light_type = 'area'
            direction = -np.array(global_light_params['sun_src_pos']) + np.array(global_light_params['sun_target_pos'])
            pos = -direction / np.linalg.norm(direction) * 10 + np.array(global_light_params['sun_target_pos'])
            # pos = global_light_params['sun_src_pos']
            self.draw_light(ax, pos, direction, sun_light_type, text='sun_0.1')

    @staticmethod
    def add_spot_light(layout, pos, scale, rot):
        x_list = copy.deepcopy(layout['x'])
        y_list = copy.deepcopy(layout['y'])
        z_list = copy.deepcopy(layout['z'])
        light_strip = 1500
        height_offset = 10

        lights = []
        for i in range(len(x_list)):
            x_list[i][0] *= scale[0]
            x_list[i][1] *= scale[0]
        for i in range(len(y_list)):
            y_list[i][0] *= scale[1]
            y_list[i][1] *= scale[1]
        for i in range(len(z_list)):
            z_list[i][0] *= scale[2]
            z_list[i][1] *= scale[2]

        if -1e-3 < abs(rot[1] * rot[-1] * 2) - 1 < 1e-3:
            temp = (np.array(z_list)).tolist()
            z_list = (-np.array(x_list)).tolist()
            x_list = temp
        if len(x_list) == 2:
            for x in x_list:
                columns = (abs(x[1] - x[0]) - 0.1) // light_strip + 1
                col_offset = ((x[1] - x[0]) - (columns - 1) * light_strip) / 2
                for col in range(int(columns)):
                    x_ = x[0] + col_offset + light_strip * col

                    if len(z_list) == 1:
                        z = z_list[0]
                        rows = (abs(z[1] - z[0]) - 0.1) // light_strip + 1
                        row_offset = ((z[1] - z[0]) - (rows - 1) * light_strip) / 2

                        for row in range(int(rows)):
                            z_ = z[0] + light_strip * row + row_offset

                            y_ = y_list[0][0] - height_offset
                            lights.append([x_ / 1000. + pos[0], y_ / 1000. + pos[1], z_ / 1000. + pos[2]])
                    else:
                        # len(z_list) == 2
                        z = [z_list[0][0], z_list[1][0]]
                        rows = abs(z[1] - z[0]) // light_strip + 1
                        row_offset = ((z[1] - z[0]) - (rows - 1) * light_strip) / 2

                        for row in range(int(rows)):
                            z_ = z[0] + light_strip * row + row_offset

                            y_ = y_list[0][0] - height_offset
                            lights.append([x_ / 1000. + pos[0], y_ / 1000. + pos[1], z_ / 1000. + pos[2]])

        if len(z_list) == 2:
            temp = x_list
            x_list = z_list
            z_list = temp
            for x in x_list:
                columns = (abs(x[1] - x[0]) - 0.1) // light_strip + 1
                col_offset = ((x[1] - x[0]) - (columns - 1) * light_strip) / 2
                for col in range(int(columns)):
                    x_ = x[0] + light_strip * col + col_offset

                    if len(z_list) == 1:
                        z = z_list[0]
                        rows = (abs(z[1] - z[0]) - 0.1) // light_strip + 1
                        row_offset = ((z[1] - z[0]) - (rows - 1) * light_strip) / 2

                        for row in range(int(rows)):
                            z_ = z[0] + light_strip * row + row_offset

                            y_ = y_list[0][0] - height_offset
                            lights.append([z_ / 1000. + pos[0], y_ / 1000. + pos[1], x_ / 1000. + pos[2]])
                    else:
                        # len(z_list) == 2
                        z = [z_list[0][0], z_list[1][0]]
                        rows = abs(z[1] - z[0]) // light_strip + 1
                        row_offset = ((z[1] - z[0]) - (rows - 1) * light_strip) / 2

                        for row in range(int(rows)):
                            z_ = z[0] + light_strip * row + row_offset

                            y_ = y_list[0][0] - height_offset
                            lights.append([z_ / 1000. + pos[0], y_ / 1000. + pos[1], x_ / 1000. + pos[2]])

        return ['spot light', lights]

    @staticmethod
    def add_strip_light(layout, pos, scale, rot):
        x_list = layout['x']
        y_list = layout['y']
        z_list = layout['z']
        verts = []
        faces = []
        norms = []
        uv = []
        valid_space_rate = 0.8
        points_ind = 0
        for i in range(len(x_list)):
            x_list[i][0] *= scale[0]
            x_list[i][1] *= scale[0]
        for i in range(len(y_list)):
            y_list[i][0] *= scale[1]
            y_list[i][1] *= scale[1]
        for i in range(len(z_list)):
            z_list[i][0] *= scale[2]
            z_list[i][1] *= scale[2]

        if -1e-3 < abs(rot[1] * rot[-1] * 2) - 1 < 1e-3:
            temp = (-np.array(z_list)).tolist()
            z_list = (-np.array(x_list)).tolist()
            x_list = temp

        for x in x_list:
            width = (x[1] - x[0]) * valid_space_rate
            x0 = (x[1] + x[0]) / 2. - width / 2.
            x1 = (x[1] + x[0]) / 2. + width / 2.
            if x0 > x1:
                temp = x0
                x0 = x1
                x1 = temp

            y = (y_list[0][0] + y_list[0][1]) / 2.
            if len(z_list) == 1:
                z = z_list[0]
            else:
                z = [z_list[0][0], z_list[1][0]]

            z_len = (z[1] - z[0]) * valid_space_rate
            z0 = (z[0] + z[1]) / 2 - z_len / 2.
            z1 = (z[0] + z[1]) / 2 + z_len / 2.
            if z0 > z1:
                temp = z0
                z0 = z1
                z1 = temp
            y_t = pos[1] - 0.01
            # y_t = pos[1] + y / 1000.
            verts += [x0 / 1000. + pos[0], y_t, z0 / 1000. + pos[2]]
            verts += [x0 / 1000. + pos[0], y_t, z1 / 1000. + pos[2]]
            verts += [x1 / 1000. + pos[0], y_t, z1 / 1000. + pos[2]]
            verts += [x1 / 1000. + pos[0], y_t, z0 / 1000. + pos[2]]

            # uv += [0. for _ in range(8)]
            uv += [x0 / 1000. + pos[0], z0 / 1000. + pos[2],
                   x0 / 1000. + pos[0], z1 / 1000. + pos[2],
                   x1 / 1000. + pos[0], z1 / 1000. + pos[2],
                   x1 / 1000. + pos[0], z0 / 1000. + pos[2]]

            faces += [0 + points_ind, 1 + points_ind, 2 + points_ind]
            faces += [0 + points_ind, 2 + points_ind, 3 + points_ind]
            # faces += [2 + points_ind, 1 + points_ind, 0 + points_ind]
            # faces += [3 + points_ind, 2 + points_ind, 0 + points_ind]

            points_ind += 4
            norms += [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]
            # norms += [0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0]

        if len(z_list) == 2:
            temp = x_list
            x_list = z_list
            z_list = temp
            for x in x_list:
                width = (x[1] - x[0]) * valid_space_rate
                x0 = (x[1] + x[0]) / 2. - width / 2.
                x1 = (x[1] + x[0]) / 2. + width / 2.
                if x0 > x1:
                    temp = x0
                    x0 = x1
                    x1 = temp
                y = (y_list[0][0] + y_list[0][1]) / 2.
                if len(z_list) == 1:
                    z = z_list[0]
                else:
                    z = [z_list[0][0], z_list[1][0]]

                z_len = (z[1] - z[0]) * valid_space_rate
                z0 = (z[0] + z[1]) / 2 - z_len / 2.
                z1 = (z[0] + z[1]) / 2 + z_len / 2.
                if z0 > z1:
                    temp = z0
                    z0 = z1
                    z1 = temp
                y_t = pos[1] - 0.01
                # y_t = pos[1] + y / 1000.

                verts += [z0 / 1000. + pos[0], y_t, x0 / 1000. + pos[2]]
                verts += [z0 / 1000. + pos[0], y_t, x1 / 1000. + pos[2]]
                verts += [z1 / 1000. + pos[0], y_t, x1 / 1000. + pos[2]]
                verts += [z1 / 1000. + pos[0], y_t, x0 / 1000. + pos[2]]
                uv += [z0 / 1000. + pos[0], x0 / 1000. + pos[2],
                       z0 / 1000. + pos[0], x1 / 1000. + pos[2],
                       z1 / 1000. + pos[0], x1 / 1000. + pos[2],
                       z1 / 1000. + pos[0], x0 / 1000. + pos[2]]
                faces += [0 + points_ind, 1 + points_ind, 2 + points_ind]
                faces += [0 + points_ind, 2 + points_ind, 3 + points_ind]
                # faces += [2 + points_ind, 1 + points_ind, 0 + points_ind]
                # faces += [3 + points_ind, 2 + points_ind, 0 + points_ind]

                points_ind += 4
                norms += [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]
                # norms += [0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0]
        return verts, norms, faces, uv

    @staticmethod
    def add_strip_light_vertical(layout, pos, scale, rot):
        x_list = layout['x']
        y_list = layout['y']
        z_list = layout['z']
        verts = []
        faces = []
        norms = []
        uv = []
        valid_space_rate = 1.01
        points_ind = 0
        for i in range(len(x_list)):
            x_list[i][0] *= scale[0]
            x_list[i][1] *= scale[0]
        for i in range(len(y_list)):
            y_list[i][0] *= scale[1]
            y_list[i][1] *= scale[1]
        for i in range(len(z_list)):
            z_list[i][0] *= scale[2]
            z_list[i][1] *= scale[2]

        if -1e-3 < abs(rot[1] * rot[-1] * 2) - 1 < 1e-3:
            temp = (-np.array(z_list)).tolist()
            z_list = (-np.array(x_list)).tolist()
            x_list = temp

        for ind, x in enumerate(x_list):
            x_t = (x[1] + x[0]) / 2. / 1000. + pos[0]

            y0 = y_list[0][0]
            y1 = y_list[0][1]
            if y0 > y1:
                temp = y0
                y0 = y1
                y1 = temp
            if len(z_list) == 1:
                z = z_list[0]
            else:
                z = [z_list[0][0], z_list[1][0]]

            z_len = (z[1] - z[0]) * valid_space_rate
            z0 = (z[0] + z[1]) / 2 - z_len / 2.
            z1 = (z[0] + z[1]) / 2 + z_len / 2.
            if z0 > z1:
                temp = z0
                z0 = z1
                z1 = temp
            verts += [x_t, y1 / 1000. + pos[1], z0 / 1000. + pos[2]]
            verts += [x_t, y1 / 1000. + pos[1], z1 / 1000. + pos[2]]
            verts += [x_t, y0 / 1000. + pos[1], z1 / 1000. + pos[2]]
            verts += [x_t, y0 / 1000. + pos[1], z0 / 1000. + pos[2]]

            # uv += [0. for _ in range(8)]
            uv += [y0 / 1000. + pos[0], z0 / 1000. + pos[2],
                   y0 / 1000. + pos[0], z1 / 1000. + pos[2],
                   y1 / 1000. + pos[0], z1 / 1000. + pos[2],
                   y1 / 1000. + pos[0], z0 / 1000. + pos[2]]
            if ind == 1:
                faces += [0 + points_ind, 1 + points_ind, 2 + points_ind]
                faces += [0 + points_ind, 2 + points_ind, 3 + points_ind]
            else:
                faces += [2 + points_ind, 1 + points_ind, 0 + points_ind]
                faces += [3 + points_ind, 2 + points_ind, 0 + points_ind]

            points_ind += 4
            n = (-1) ** ind
            norms += [n, 0, 0, n, 0, 0, n, 0, 0, n, 0, 0]

        if len(z_list) == 2:
            temp = x_list
            x_list = z_list
            z_list = temp
            for ind, x in enumerate(x_list):
                x_t = (x[1] + x[0]) / 2. / 1000. + pos[2]

                y0 = y_list[0][0]
                y1 = y_list[0][1]
                if y0 > y1:
                    temp = y0
                    y0 = y1
                    y1 = temp
                if len(z_list) == 1:
                    z = z_list[0]
                else:
                    z = [z_list[0][0], z_list[1][0]]

                z_len = (z[1] - z[0]) * valid_space_rate
                z0 = (z[0] + z[1]) / 2 - z_len / 2.
                z1 = (z[0] + z[1]) / 2 + z_len / 2.
                if z0 > z1:
                    temp = z0
                    z0 = z1
                    z1 = temp

                verts += [z0 / 1000. + pos[0], y1 / 1000. + pos[1], x_t]
                verts += [z1 / 1000. + pos[0], y1 / 1000. + pos[1], x_t]
                verts += [z1 / 1000. + pos[0], y0 / 1000. + pos[1], x_t]
                verts += [z0 / 1000. + pos[0], y0 / 1000. + pos[1], x_t]

                # uv += [0. for _ in range(8)]
                uv += [y0 / 1000. + pos[0], z0 / 1000. + pos[2],
                       y0 / 1000. + pos[0], z1 / 1000. + pos[2],
                       y1 / 1000. + pos[0], z1 / 1000. + pos[2],
                       y1 / 1000. + pos[0], z0 / 1000. + pos[2]]
                if ind == 0:
                    faces += [0 + points_ind, 1 + points_ind, 2 + points_ind]
                    faces += [0 + points_ind, 2 + points_ind, 3 + points_ind]
                else:
                    faces += [2 + points_ind, 1 + points_ind, 0 + points_ind]
                    faces += [3 + points_ind, 2 + points_ind, 0 + points_ind]

                points_ind += 4
                n = (-1) ** ind
                norms += [0, 0, n, 0, 0, n, 0, 0, n, 0, 0, n]
        return verts, norms, faces, uv

    def add_sky_light(self, win_door, wall, inner_win=True):
        if inner_win:
            offset = np.array(win_door['normal']) / np.linalg.norm(np.array(win_door['normal'])) * 0.15
            scale = 0.9
        else:
            offset = -np.array(win_door['normal']) / np.linalg.norm(np.array(win_door['normal'])) * 0.15
            scale = 1.2
        x_length = abs(win_door['layout_pts'][0][0] - win_door['layout_pts'][1][0])
        z_length = abs(win_door['layout_pts'][0][1] - win_door['layout_pts'][1][1])
        win_height = win_door['height']
        if x_length > z_length:
            xyz = np.array([[win_door['obj_info']['pos'][0] - x_length / 2., win_door['obj_info']['pos'][1], win_door['obj_info']['pos'][2] + offset[1]],
                            [win_door['obj_info']['pos'][0] - x_length / 2., win_door['obj_info']['pos'][1] + win_height,
                             win_door['obj_info']['pos'][2] + offset[1]],
                            [win_door['obj_info']['pos'][0] + x_length / 2., win_door['obj_info']['pos'][1] + win_height,
                             win_door['obj_info']['pos'][2] + offset[1]],
                            [win_door['obj_info']['pos'][0] + x_length / 2., win_door['obj_info']['pos'][1], win_door['obj_info']['pos'][2] + offset[1]]])
            if win_door['normal'][1] > 0:
                xyz = xyz[::-1, :]
        else:
            xyz = np.array([[win_door['obj_info']['pos'][0] + offset[0], win_door['obj_info']['pos'][1], win_door['obj_info']['pos'][2] - z_length / 2.],
                            [win_door['obj_info']['pos'][0] + offset[0], win_door['obj_info']['pos'][1] + win_height,
                             win_door['obj_info']['pos'][2] - z_length / 2.],
                            [win_door['obj_info']['pos'][0] + offset[0], win_door['obj_info']['pos'][1] + win_height,
                             win_door['obj_info']['pos'][2] + z_length / 2.],
                            [win_door['obj_info']['pos'][0] + offset[0], win_door['obj_info']['pos'][1], win_door['obj_info']['pos'][2] + z_length / 2.]])
            if win_door['normal'][0] > 0:
                xyz = xyz[::-1, :]
        center = np.mean(np.array(xyz), axis=0)
        xyz = scale * (xyz - center) + center
        if inner_win:
            x = xyz[:, 0]
            y = xyz[:, 1]
            z = xyz[:, 2]
            limits_low = np.min(np.array(wall), axis=0)
            limits_high = np.max(np.array(wall), axis=0)
            if x_length > z_length:
                x[x < limits_low[0] + 0.3] = limits_low[0] + 0.3
                x[x > limits_high[0] - 0.3] = limits_high[0] - 0.3
            else:
                z[z < limits_low[1] + 0.3] = limits_low[1] + 0.3
                z[z > limits_high[1] - 0.3] = limits_high[1] - 0.3
            y[y < 0.3] = 0.3
            y[y > 2.0] = 2.0
            xyz = np.stack([x, y, z], axis=-1)

        pos = np.mean(xyz, axis=0)
        size = np.max(xyz, axis=0) - np.min(xyz, axis=0)
        if x_length > z_length:
            size = size[[0, 1]]
        else:
            size = size[[2, 1]]

        direction = np.array(win_door['normal']) / np.linalg.norm(win_door['normal'])
        direction = [direction[0], 0, direction[1]]

        return direction, size.tolist(), pos.tolist()

    def adjust_light_pos(self, pos, fobiden_area, floor_pts, gap_thresh=0.6):

        limits_x = [1e8, 1e8]
        limits_y = [1e8, 1e8]
        for i in range(len(floor_pts)):
            minx = min(floor_pts[i][0], floor_pts[(i + 1) % len(floor_pts)][0])
            maxx = max(floor_pts[i][0], floor_pts[(i + 1) % len(floor_pts)][0])
            miny = min(floor_pts[i][1], floor_pts[(i + 1) % len(floor_pts)][1])
            maxy = max(floor_pts[i][1], floor_pts[(i + 1) % len(floor_pts)][1])
            if minx < pos[0] < maxx:
                if pos[1] > miny:
                    limits_y[0] = min(pos[1] - miny, limits_y[0])
                else:
                    limits_y[1] = min(-pos[1] + miny, limits_y[1])
            if miny < pos[1] < maxy:
                if pos[0] > minx:
                    limits_x[0] = min(pos[0] - minx, limits_x[0])
                else:
                    limits_x[1] = min(-pos[0] + minx, limits_x[1])
        for i in range(len(fobiden_area)):
            minx = min(fobiden_area[i][0], fobiden_area[(i + 1) % len(fobiden_area)][0])
            maxx = max(fobiden_area[i][0], fobiden_area[(i + 1) % len(fobiden_area)][0])
            miny = min(fobiden_area[i][1], fobiden_area[(i + 1) % len(fobiden_area)][1])
            maxy = max(fobiden_area[i][1], fobiden_area[(i + 1) % len(fobiden_area)][1])
            if minx < pos[0] < maxx:
                if pos[1] > miny:
                    limits_y[0] = min(pos[1] - miny, limits_y[0])
                else:
                    limits_y[1] = min(-pos[1] + miny, limits_y[1])
            if miny < pos[1] < maxy:
                if pos[0] > minx:
                    limits_x[0] = min(pos[0] - minx, limits_x[0])
                else:
                    limits_x[1] = min(-pos[0] + minx, limits_x[1])
        if limits_x[1] > gap_thresh and limits_x[0] > gap_thresh and limits_y[1] > gap_thresh and limits_y[
            0] > gap_thresh:
            return pos, 0
        if limits_x[1] + limits_x[0] < gap_thresh * 2 or limits_y[1] + limits_y[0] < gap_thresh * 2:
            return None, 0
        if limits_x[0] < gap_thresh:
            pos[0] += gap_thresh - limits_x[0]
            status = gap_thresh - limits_x[0]
        if limits_x[1] < gap_thresh:
            pos[0] -= gap_thresh - limits_x[1]
            status = gap_thresh - limits_x[1]
        if limits_y[0] < gap_thresh:
            pos[1] += gap_thresh - limits_y[0]
            status = gap_thresh - limits_y[0]
        if limits_y[1] < gap_thresh:
            pos[1] -= gap_thresh - limits_y[1]
            status = gap_thresh - limits_y[1]
        return pos, status

    def add_virtual_plane_light(self, xyz, norm, info, uid, intensity):
        uv = [0, 0] * 4
        norms = norm * 4
        faces = [0, 1, 2, 3, 0, 2]
        mesh = Mesh("Ceiling", uid)
        mesh.build_exists_mesh(xyz, norms, uv, faces)
        info.room_info['Ceiling'].mesh_info.append(mesh)
        info.room_info['light']['StripLight'].append([uid, intensity])

    @staticmethod
    def add_area_light_matrix(area_pts, gap_thresh=0.5, strip=2.):
        size = np.max(area_pts, axis=0) - np.min(area_pts, axis=0)
        if size[0] < gap_thresh * 2 or size[1] < gap_thresh * 2:
            return []
        center = np.mean(area_pts, axis=0)
        shrinked_size = size - gap_thresh * 2

        light_num = (shrinked_size + 0.5 * strip) // strip + 1
        light_strip = shrinked_size / (light_num - 1 + 1e-7)
        bias = shrinked_size / 2. * ((light_num - 1) < 1e-3) - shrinked_size / 2.
        light_pos = []
        for i in range(int(light_num[0])):
            for j in range(int(light_num[1])):
                light_pos.append([light_strip[0] * i + center[0] + bias[0], light_strip[1] * j + center[1] + bias[1]])

        return light_pos

    @staticmethod
    def draw_light(ax, pos, direction, light_type, size=None, text=None, phisical=True):
        assert light_type in ['sun', 'area', 'point', 'spot']
        pos = np.array(pos)
        if direction is not None:
            direction = np.array(direction) / np.linalg.norm(direction)
        if direction is not None and (abs(direction[0]) > 1e-3 or abs(direction[2]) > 1e-3):
            if size is None:
                size = [1, 1]
            pro_dir = direction[[0, 2]]
            per_dir = np.array([pro_dir[1], -pro_dir[0]])
            base_pts = np.array([[0, 0], per_dir * size[0]])
            base_pts -= np.mean(base_pts, axis=0)

            arrow_len = min(0.3, size[0] / 2.)
            start0 = per_dir * size[0] / 4
            arrow0_pts = [start0, start0 + pro_dir * arrow_len]
            start1 = -per_dir * size[0] / 4
            arrow1_pts = [start1, start1 + pro_dir * arrow_len]
            start2 = [0, 0]
            arrow2_pts = [start2, start2 + pro_dir * arrow_len]

            pts = np.array([base_pts,
                            arrow0_pts,
                            arrow1_pts,
                            arrow2_pts]) + np.array(pos[[0, 2]])
            for pt in pts:
                ax.plot(pt[:, 0], pt[:, 1], color='y')

        else:
            if size is None:
                size = [0.1, 0.1]
            if light_type == 'point':
                p = ptc.Circle(pos[[0, 2]], size[0], color='y')
                ax.add_patch(p)
            elif light_type == 'spot':
                p1 = ptc.Circle(pos[[0, 2]], size[0], color='y')
                ax.add_patch(p1)
                if phisical:
                    p2 = ptc.Circle(pos[[0, 2]], size[0] / 4, color='b')
                    ax.add_patch(p2)
            else:
                pts = np.array(
                    [[-size[0] / 2., -size[0] / 2.], [-size[0] / 2., size[0] / 2.], [size[0] / 2., size[0] / 2.],
                     [size[0] / 2., -size[0] / 2.], [-size[0] / 2., -size[0] / 2.]]) + np.array(pos[[0, 2]])
                ax.plot(pts[:, 0], pts[:, 1], color='y')

        if text is not None:
            plt.text(pos[0], pos[2], text, color='b')