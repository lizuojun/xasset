from LayoutDecoration.layout.room_area_segmentation import RoomAreaSegmentation
from LayoutDecoration.house_info import HouseData
from House.house_scene import house_scene_parse
from LayoutByRule.house_interior_analyze import house_rect_analyze
from LayoutDecoration.models.model_api import get_attr_calcifer_id
from matplotlib import pyplot as plt
import numpy as np
plt.switch_backend('macosx')


def cmb_mat(house_data):

    for room in house_data['room']:
        floor_meshes = room['mesh']['floor']
        wall_meshes = room['mesh']['wall']

        cmb_mat_dict = {}
        mat_ind = 0
        for floor_mesh in floor_meshes:
            floor = floor_mesh['material']

            jid = floor['jid'] if 'jid' in floor else ''
            if len(jid.split('-')) == 5:
                pass
            elif 'colorMode' in floor and floor['colorMode'] == 'color' and 'color' in floor:
                jid = '-'.join(floor['color'])

            elif ('colorMode' in floor and floor['colorMode'] == 'texture') or ('texture' in floor and len(floor['texture']) > 0) :
                jid = floor['texture_url']
            elif 'color' in floor:
                jid = '-'.join(floor['color'])

            if len(jid.split('-')) == 5:
                attr_calcifer_id = get_attr_calcifer_id(jid)
                if attr_calcifer_id is not None:
                    jid = attr_calcifer_id

            if jid not in cmb_mat_dict:
                cmb_mat_dict[jid] = mat_ind
                mat_ind += 1
            floor['mid'] = cmb_mat_dict[jid]

        for wall_mesh in wall_meshes:
            wall = wall_mesh['material']

            jid = wall['jid'] if 'jid' in wall else ''
            if len(jid.split('-')) == 5:
                pass
            elif 'colorMode' in wall and wall['colorMode'] == 'color' and 'color' in wall:
                jid = '-'.join(wall['color'])

            elif ('colorMode' in wall and wall['colorMode'] == 'texture') or ('texture' in wall and len(wall['texture']) > 0) :
                jid = wall['texture_url']
            elif 'color' in wall:
                jid = '-'.join(wall['color'])
            if jid not in cmb_mat_dict:
                cmb_mat_dict[jid] = mat_ind
                mat_ind += 1
            wall['mid'] = cmb_mat_dict[jid]


def cmb_mesh(house_data, dis_thresh=0.01):
    for room in house_data['room']:
        floor_meshes = room['mesh']['floor']
        region_mesh_dict = {}

        for floor_mesh in floor_meshes:
            xyz = np.reshape(floor_mesh['xyz'], newshape=[-1, 3])
            faces = np.reshape([floor_mesh['faces']], newshape=[-1, 3])
            poly = [xyz[i.tolist()] for i in faces]
            mid = floor_mesh['material']['mid']
            if mid in region_mesh_dict:
                region_mesh_dict[mid].append(poly)
            else:
                region_mesh_dict[mid] = [poly]

        for mid, meshes in region_mesh_dict.items():
            flags = [True for _ in range(len(meshes))]
            all_area = []
            for i in range(len(meshes)):
                if not flags[i]:
                    continue
                flags[i] = False
                cur_area = []
                while True:
                    pass


def mesh_parse(scene_url):
    # house_data
    house_data = house_scene_parse(scene_url, True)
    # house_layout
    layout_info, group_info, region_info = house_rect_analyze(house_data)
    house_layout = {}
    for room in house_data['room']:
        room_uid = room['id']
        if room_uid in layout_info:
            if len(layout_info[room_uid]['layout_scheme']) > 0:
                house_layout[room_uid] = layout_info[room_uid]['layout_scheme'][0]['group']
    # house info
    house = HouseData(house_data)
    # 硬装功能区分割
    RoomAreaSegmentation(house.house_info, house_layout, build_mode={'customized_ceiling': False, 'debug': True})
    print()

    # 合并材质
    cmb_mat(house_data)
    # 解析mesh材质

    color = ['blue', 'red', 'orange', 'g', 'cyan', 'pink', 'yellow', 'tomato', 'yellowgreen', 'maroon', 'lightcoral']
    plt.figure()
    plt.title('LivingDiningRoom')
    for room in house_data['room']:
        if room['type'] not in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
            continue

        for ind, mesh in enumerate(room['mesh']['floor']):
            xyz = np.reshape(mesh['xyz'], newshape=[-1, 3])
            faces = np.reshape([mesh['faces']], newshape=[-1, 3])
            poly = [xyz[i.tolist() + i.tolist()[:1]] for i in faces]
            mid = mesh['material']['mid']
            for p in poly:
                # plt.plot(p[:, 0], p[:, 2], color=color[mid])
                plt.fill(p[:, 0], p[:, 2], color=color[mid])
    plt.axis('equal')
    plt.show()


if __name__ == '__main__':
    scene_url = '/Users/liqing.zhc/code/sample_scene_data/sceneParse/tmp/customized_ceiling_data/scene_000001_北欧_一厅_一室_一卫_b94dacb3-2fbe-4319-81b7-5e48dc52fb75/scene.json'
    mesh_parse(scene_url)
    print()
