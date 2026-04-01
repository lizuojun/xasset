from House.house_scene import house_scene_parse
from LayoutDecoration.net_utils.data_oss import oss_download_file, oss_list_file
import random
import os
import shutil
from matplotlib import pyplot as plt
import requests
plt.switch_backend('macosx')
import numpy as np


def get_house_scene_material(scene_url):
    house_data = house_scene_parse(scene_url, True)

    transfer_hard = {}
    for room in house_data['room']:
        room_uid = room['id']
        room['material']['area'] = room['area']
        transfer_hard[room_uid] = room['material']

    for room_id, mat_dict in transfer_hard.items():
        if 'floor' in mat_dict:
            floor_mat = mat_dict['floor']
        else:
            floor_mat = []
        if 'wall' in mat_dict:
            wall_mat = mat_dict['wall']
        else:
            wall_mat = []
        comb_floor = {}
        for floor in floor_mat:
            if 'area' not in floor:
                floor['area'] = 0.
            jid = floor['jid']
            if len(jid.split('-')) == 5:
                if jid not in comb_floor:
                    comb_floor[jid] = floor
                else:
                    comb_floor[jid]['area'] += floor['area']
            elif floor['colorMode'] == 'color':
                jid = '-'.join(floor['color'])
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
            if 'area' not in wall:
                wall['area'] = 0.
            jid = wall['jid']
            if len(jid.split('-')) == 5:
                if jid not in comb_wall:
                    comb_wall[jid] = wall
                else:
                    comb_wall[jid]['area'] += wall['area']
            elif wall['colorMode'] == 'color':
                c = [str(color) for color in wall['color']]
                jid = '-'.join(c)
                if jid not in comb_wall:
                    comb_wall[jid] = wall
                else:
                    comb_wall[jid]['area'] += wall['area']
            else:
                jid = wall['texture_url']
                if jid not in comb_wall:
                    comb_wall[jid] = wall
                else:
                    comb_wall[jid]['area'] += wall['area']

        transfer_hard[room_id]['floor'] = list(comb_floor.values())
        if len(transfer_hard[room_id]['floor']) > 1:
            transfer_hard[room_id]['floor'].sort(key=lambda x: -x['area'])
        transfer_hard[room_id]['wall'] = list(comb_wall.values())
        if len(transfer_hard[room_id]['wall']) > 1:
            transfer_hard[room_id]['wall'].sort(key=lambda x: -x['area'])

    return transfer_hard


def download_sample_scene_data(num, save_dir):
    scenes = oss_list_file('ihome-alg-sample-data')
    random.shuffle(scenes)
    for scene in scenes[:num]:
        oss_download_file(scene, os.path.join(save_dir, scene), 'ihome-alg-sample-room')


def stat_data(key='floor'):
    download_path = './temp/sample_scenes/'
    scene_num = 1000
    scenes = os.listdir(download_path)
    # if len(scenes) < scene_num:
    #     download_sample_scene_data(scene_num - len(scenes), download_path)
    scenes = os.listdir(download_path)
    scenes = [os.path.join(download_path, i) for i in scenes if i.endswith('.json')]
    house_floor_mat_dict = {}
    for scene in scenes:
        try:
            mat = get_house_scene_material(scene)
        except Exception as e:
            print(e)
            continue
        flag = False
        for k, v in mat.items():
            floor_mats = v[key]
            room_type = v['type']
            num = 0
            for m in floor_mats:
                if m['area'] > 1:
                    num += 1
            if room_type not in house_floor_mat_dict:
                house_floor_mat_dict[room_type] = {'mat': [floor_mats], 'num': [num]}
            else:
                house_floor_mat_dict[room_type]['mat'].append(floor_mats)
                house_floor_mat_dict[room_type]['num'].append(num)

            if room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom'] and num > 1:
                flag = True
        if flag:
            dst_scene = scene.replace('sample_scenes', 'sample_scene_multi_wall')
            shutil.copy(scene, dst_scene)
            print(dst_scene)

    for room_type, mats in house_floor_mat_dict.items():

        if len(mats['num']) < 100:
            continue
        plt.figure()
        bins = np.arange(0, np.max(mats['num']) + 1) + 0.5
        plt.hist(mats['num'], bins=bins)
        max_n = 0
        for i, bin in enumerate(bins[:-1]):
            b1 = np.greater(bins[i + 1], np.array(mats['num']))
            b2 = np.greater(np.array(mats['num']), bins[i])
            n = np.sum(np.logical_and(b1, b2))
            plt.text(bin + 0.5, n + 1, str(n))
            if n > max_n:
                max_n = n
        plt.grid()
        x_major_locator = plt.MultipleLocator(1)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.ylim(0, max_n + 2)
        plt.xlim(0, max(5, np.max(mats['num']) + 1))
        plt.title(room_type)
    plt.show()


def check_data(key='floor'):
    from natsort import natsorted
    src_dir = '/Users/liqing.zhc/code/ihome-layout/LayoutDecoration/temp/sample_scene_multi_wall/'
    scenes = os.listdir(src_dir)
    scenes = natsorted(scenes)
    for scene in scenes:
        if scene == '.DS_Store':
            continue
        print('------------------------------------------------------------')
        print(scene)
        scene = os.path.join(src_dir, scene)
        # did = '0bd374c6-a29b-4d4c-875d-38c3422a8af5'
        # scene = '/Users/liqing.zhc/code/ihome-layout/LayoutDecoration/temp/sample_scene_multi_floor/%s.json' % did

        try:
            mat = get_house_scene_material(scene)
        except Exception as e:
            print(e)
            mat = None
            exit(0)
        flag = False
        for k, v in mat.items():
            floor_mats = v[key]
            room_type = v['type']
            if room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
                for m in floor_mats:
                    # if m['texture_url'].startswith('http'):
                    #     ret = requests.get(m['texture_url'])
                    #     if ret.ok:
                    #         print('@@@@@@@@@@@@@@@')
                    print(m)


if __name__ == '__main__':
    # stat_data('wall')
    check_data('wall')
