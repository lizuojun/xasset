# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2021-08-31
@Description: 空间硬装服务

"""
import copy
import time
import shutil

from layout import *
from layout_def import *
from House.house_scene_render import *
from House.house_scene_build import house_replace_house
from HouseSearch.house_seed import *
from ImportHouse.room_search import *
from ImportHouse.room_search_more import get_house_data
from Extract.group_material import house_data_group_wall
from Extract.group_win_door import house_data_group_win_door
from Extract.group_feature_wall import house_data_group_feature_wall


# 布局服务计数
LAYOUT_SAMPLE_CNT = 0
LAYOUT_SAMPLE_LOC = ''

# 临时目录
DATA_DIR_SERVER_INPUT = os.path.dirname(__file__) + '/temp/input/'
if not os.path.exists(DATA_DIR_SERVER_INPUT):
    os.makedirs(DATA_DIR_SERVER_INPUT)
DATA_DIR_SERVER_SCHEME = os.path.dirname(__file__) + '/temp/scheme/'
if not os.path.exists(DATA_DIR_SERVER_SCHEME):
    os.makedirs(DATA_DIR_SERVER_SCHEME)
# 设计目录
DATA_DIR_RECORD = os.path.dirname(__file__) + '/LayoutRecord/'
if not os.path.exists(DATA_DIR_RECORD):
    os.makedirs(DATA_DIR_RECORD)

# 组合服务位置
DATA_OSS_LAYOUT = 'ihome-alg-layout'
DATA_URL_LAYOUT = 'https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com'


# 布局服务入口
def layout_sample_decoration(param_info):
    # 户型参数
    house_id, room_id, plat_id, plat_entity = '', '', '', ''
    house_data, room_data = {}, {}
    house_replace, room_replace, note_replace = {}, {}, {}
    if 'house_id' in param_info:
        house_id = param_info['house_id']
    if 'room_id' in param_info:
        room_id = param_info['room_id']
    if 'plat_id' in param_info:
        plat_id = param_info['plat_id']
    if 'plat_entity' in param_info:
        plat_entity = param_info['plat_entity']
    if 'house_data' in param_info:
        house_data = param_info['house_data']
    if 'room_data' in param_info:
        room_data = param_info['room_data']
    if 'house_replace' in param_info:
        house_replace = param_info['house_replace']
    if 'room_replace' in param_info:
        room_replace = param_info['room_replace']
    if 'note_replace' in param_info:
        note_replace = param_info['note_replace']
    if 'replace_info' in param_info:
        house_replace = param_info['replace_info']
    # 户型位置
    house_idx = -1
    data_url, scene_url, image_url, scene_path = '', '', '', ''
    design_id, design_url = '', ''
    if 'data_idx' in param_info:
        house_idx = param_info['data_idx']
    if 'data_url' in param_info:
        data_url = param_info['data_url']
    if 'scene_url' in param_info:
        scene_url = param_info['scene_url']
    if 'image_url' in param_info:
        image_url = param_info['image_url']
    if 'design_id' in param_info:
        design_id = param_info['design_id']
    if 'design_url' in param_info:
        design_url = param_info['design_url']
    if design_id == '' and not house_id == '':
        design_id = house_id
    # 布局模式
    layout_mode = LAYOUT_MODE_PAINT
    if 'layout_mode' in param_info:
        layout_mode = int(param_info['layout_mode'])
    layout_num, propose_num = 2, 2
    if layout_mode == LAYOUT_MODE_ADJUST:
        layout_num, propose_num = 1, 1
    if 'layout_number' in param_info:
        layout_num = param_info['layout_number']
    if 'propose_number' in param_info:
        propose_num = param_info['propose_number']
    # 商品参数
    item_id = ''
    # 场景参数
    scene_list = []

    # 保存模式
    render_mode, scheme_mode = '', ''
    save_mode = []
    if 'render_mode' in param_info:
        render_mode = str(param_info['render_mode']).lower()
    if 'scheme_mode' in param_info:
        scheme_mode = str(param_info['scheme_mode']).lower()
        if 'image' in scheme_mode:
            save_mode.append(SAVE_MODE_IMAGE)
        if 'frame' in scheme_mode:
            save_mode.append(SAVE_MODE_FRAME)
        if 'render' in scheme_mode:
            save_mode.append(SAVE_MODE_RENDER)
        if 'layout' in scheme_mode:
            save_mode.append(SAVE_MODE_LAYOUT)
        if 'group' in scheme_mode:
            save_mode.append(SAVE_MODE_GROUP)
    # if len(save_mode) <= 0:
    #     save_mode.append(SAVE_MODE_GROUP)

    # 组合信息
    house_layout_info, house_group_info = {}, {}
    decoration_operation = []
    # if True:
    try:
        # 打印信息
        print()
        layout_log_0 = 'layout paint ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        if not house_id == '':
            layout_log_0 = 'target house: %s, room: %s, plat: %s' % (house_id, room_id, plat_id)
            print(layout_log_0)
        elif not design_id == '':
            layout_log_0 = 'target house: %s, room: %s' % (design_id, room_id)
            print(layout_log_0)
        elif not plat_id == '':
            layout_log_0 = 'target plat: %s' % plat_id
            print(layout_log_0)
        # 户型参数
        if len(house_data) <= 0 and len(room_data) <= 0:
            house_para_info, house_data_info = {}, {}
            # design id
            if len(house_data_info) <= 0 and not design_id == '':
                house_para_info, house_data_info = parse_design_data(design_id, design_url, scene_url)
                if 'id' in house_data_info:
                    house_id = design_id
                    house_data_info['id'] = design_id
                if 'room' in house_data_info and len(house_data_info['room']) <= 0:
                    house_data_info = {}
            # house id
            if len(house_data_info) <= 0 and scene_url == '' and not house_id == '':
                house_id_new, house_data_info, house_feature_info = get_house_data_feature(house_id, True)
                house_data = house_data_info

            # 户型轮廓 TODO:
            if len(house_data_info) <= 0 and not data_url == '':
                pass
            # 户型场景
            if len(house_data_info) <= 0 and not scene_url == '':
                house_have, scene_path = download_scene_by_url(scene_url, DATA_DIR_SERVER_INPUT)
                if house_have and os.path.exists(scene_path):
                    house_id_new, house_data_info, house_feature_info = get_house_data_feature_by_path(scene_path)
                    if len(house_id) <= 0 and len(house_id_new) > 0:
                        house_id = house_id_new
            # 户型图片 TODO:
            if len(house_data_info) <= 0 and not image_url == '':
                pass
            # 户型更新
            if len(house_data_info) > 0:
                house_data = house_data_info
                if not room_id == '' and 'room' in house_data_info:
                    for room_one in house_data_info['room']:
                        if room_id == room_one['id']:
                            room_data = room_one
                            break
        # 保存参数
        if SAVE_MODE_SCENE in save_mode:
            if scene_url == '' and not design_id == '':
                scene_url = house_scene_url(design_id)

        # 组合提取
        if len(room_data) > 0 and 'furniture_info' in room_data:
            if 'id' in room_data and room_id == '':
                room_id = room_data['id']
            if 'coordinate' not in room_data:
                room_data['coordinate'] = 'xyz'
            if 'unit' not in room_data:
                room_data['unit'] = 'm'
            room_data_info, room_scheme_info, room_group_info = group_room(room_data)
            if len(room_group_info) > 0:
                house_group_info[room_id] = room_group_info
            if len(room_scheme_info) > 0:
                house_layout_info[room_id] = room_scheme_info
        # 组合提取
        elif len(house_data) > 0 and 'room' in house_data:
            if 'id' in house_data and house_id == '':
                house_id = house_data['id']
            room_list = []
            if 'room' in house_data:
                room_list = house_data['room']
            for room_one in room_list:
                if 'coordinate' not in room_one:
                    room_one['coordinate'] = 'xyz'
                if 'unit' not in room_one:
                    room_one['unit'] = 'm'
            # sample_para, sample_data, house_layout_info, sample_group = get_house_sample(house_id)
            house_data_info_org = copy.deepcopy(house_data)
            house_data_info, house_layout_info, house_group_info = group_house(house_data)
            for room in house_data_info['room']:
                for r in house_data_info_org['room']:
                    if r['id'] == room['id'] and r['type'] != 'none':
                        room['type'] = r['type']
                        break

        # 硬装替换
        if len(house_layout_info) > 0 and len(house_replace) > 0:
            if len(scene_path) == 0:
                house_have, scene_path = download_scene_by_url(scene_url, DATA_DIR_SERVER_INPUT)
            house_data_info = house_data_group_win_door(house_id, house_data_info, house_layout_info, upload=False)
            house_data_info = house_data_group_wall(house_id, house_data_info, house_layout_info, False)
            replace_bg = False
            for _, v in house_replace.items():
                if 'background' in v:
                    replace_bg = True
                    break
            if replace_bg:
                house_data_info = house_data_group_feature_wall(house_id, house_data_info, house_layout_info, False)
            house_scene_json, decoration_operation = \
                layout_paint_replace(house_data_info, house_layout_info, scene_path, house_replace)
            scene_path_new = scene_path
            if SAVE_MODE_RENDER in save_mode or 'scene' in scheme_mode:
                # 户型保存
                save_id = house_id
                if save_id == '':
                    if len(house_layout_info) <= 0:
                        save_id = 'null'
                    elif len(house_layout_info) == 1:
                        save_id = 'room'
                    else:
                        save_id = 'house'
                save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
                save_time = datetime.datetime.now().strftime('%H-%M-%S')
                json_path = os.path.join(save_dir, save_id + '_new.json')
                with open(json_path, "w") as f:
                    # json.dump(house_scene_json, f, indent=4)
                    json.dump(house_scene_json, f)
                    f.close()
                scene_path_new = json_path
            scene_each = {
                'id': house_id,
                'url': '',
                'loc': scene_path_new,
                'layout': house_layout_info
            }
            scene_list.append(scene_each)

        # 打印信息
        layout_log_0 = 'layout paint success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        # 保存组合
        if len(save_mode) > 0:
            save_id = house_id
            save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
            upload_group, upload_room = False, False
            if SAVE_MODE_RENDER in save_mode:
                pass
            elif SAVE_MODE_GROUP in save_mode:
                group_save(house_group_info, save_id, save_dir, 10, 15, save_mode, upload_group, upload_room)
            if len(save_mode) > 0:
                house_save(house_id, '', 1, 1, house_data_info, house_layout_info, {}, house_id + '_sample',
                           save_dir, save_mode, suffix_flag=False, sample_flag=False, upload_flag=False)

        # 打印信息
        layout_log_0 = 'layout paint success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    # try:
        print(layout_log_0)
    except Exception as e:
        layout_log_0 = 'layout paint failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        print(e)

    # 计数信息
    layout_sample_count()

    # 镜像信息
    room_mirror = 0
    if len(room_data) > 0 and 'mirror' in room_data:
        room_mirror = room_data['mirror']
    elif len(house_data) > 0 and 'room' in house_data:
        for room_one in house_data['room']:
            if len(room_one) > 0 and 'mirror' in room_one:
                room_mirror = room_one['mirror']
                break

    # 渲染信息 TODO:
    scene_key_new = ''
    if SAVE_MODE_RENDER in save_mode:
        for scene_each in scene_list:
            # 户型位置
            scene_key, scene_path, scene_layout = scene_each['id'], scene_each['loc'], scene_each['layout']
            scene_key_old, scene_key_new = '', ''
            save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, scene_key)
            house_scene_json = json.load(open(scene_path, 'r', encoding='utf-8'))
            # 装修渲染
            if 'decorate' in render_mode:
                item_id = 'decorate'
            # 户型保存
            save_time = datetime.datetime.now().strftime('%H-%M-%S')
            save_id = scene_key + '-' + save_time
            json_path = os.path.join(save_dir, save_id + '.json')
            with open(json_path, "w") as f:
                # json.dump(house_scene_json, f, indent=4)
                json.dump(house_scene_json, f)
                f.close()
            # 户型上传
            scene_key_new = house_scene_upload(house_scene_json, save_id, json_path)
    # 输出处理
    layout_version = '20210913.1200'
    layout_output = {
        'house_id': house_id,
        'room_id': room_id,
        'scene_url': scene_key_new,
        'operation': decoration_operation,
        'image_key': [],
        'image_val': [],
        'layout_version': layout_version
    }

    # 图片信息
    if 'result' in render_mode:
        # 位置
        save_id = plat_id
        if len(item_id) > 0:
            save_id = item_id
        save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        # 图片
        key_list, val_list = [], []
        if 'image_key' in layout_output:
            key_list = layout_output['image_key']
        if 'image_val' in layout_output:
            val_list = layout_output['image_val']
        time.sleep(10)
        image_dict = house_scene_render_fetch(key_list, image_dir=save_dir)
        for val_one in val_list:
            key_one = val_one['id']
            if key_one in image_dict:
                image_one = image_dict[key_one]
                if 'url' in image_one:
                    val_one['url'] = image_one['url']
                if 'loc' in image_one:
                    val_one['loc'] = image_one['loc']
    # 输出信息
    if 'output' in scheme_mode:
        save_id = plat_id
        if len(plat_id) > 0:
            save_id = plat_id
        elif len(item_id) > 0:
            save_id = item_id
        elif len(house_id) > 0:
            save_id = house_id
        save_dir = layout_sample_mkdir(DATA_DIR_SERVER_SCHEME, save_id)
        save_des = os.path.join(save_dir, save_id + '_output.json')
        with open(save_des, "w") as f:
            json.dump(layout_output, f, indent=4)
            f.close()
    # 返回信息
    return layout_output


# 布局服务目录
def layout_sample_mkdir(save_dir, save_id):
    save_dir_new = os.path.join(save_dir, save_id)
    if not os.path.exists(save_dir_new):
        os.makedirs(save_dir_new)
    return save_dir_new


# 布局服务计数
def layout_sample_count(count_max=1000):
    # 调用信息
    global LAYOUT_SAMPLE_CNT
    LAYOUT_SAMPLE_CNT += 1
    if LAYOUT_SAMPLE_CNT >= count_max:
        # 重置
        LAYOUT_SAMPLE_CNT = 0
        # 清空
        layout_sample_clear()


# 布局服务清空
def layout_sample_clear():
    # 清空
    if os.path.exists(DATA_DIR_SERVER_SCHEME):
        shutil.rmtree(DATA_DIR_SERVER_SCHEME)
    if os.path.exists(DATA_DIR_SERVER_SERVICE):
        shutil.rmtree(DATA_DIR_SERVER_SERVICE)
    # 重建
    if not os.path.exists(DATA_DIR_SERVER_SCHEME):
        os.makedirs(DATA_DIR_SERVER_SCHEME)
    if not os.path.exists(DATA_DIR_SERVER_SERVICE):
        os.makedirs(DATA_DIR_SERVER_SERVICE)


# 布局户型解析
def parse_design_data(design_id, design_url, scene_url=''):
    house_para_info, house_data_info = get_house_data(design_id, design_url, scene_url, reload=True, correct_house=False)
    if 'id' in house_data_info:
        house_id = design_id
        house_data_info['id'] = design_id
    if 'room' not in house_data_info:
        house_para_info, house_data_info = {}, {}
    elif 'room' in house_data_info and len(house_data_info['room']) <= 0:
        house_para_info, house_data_info = {}, {}
    return house_para_info, house_data_info


# 硬装替换服务 TODO:
def layout_paint_replace(house_info, layout_info, scene_path='', replace_info={}, replace_note={}):
    # 种子处理
    room_list, replace_more, replace_keep, replace_room = [], {}, {}, {}
    if 'room' in house_info:
        room_list = house_info['room']
    room_type_list_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']
    room_type_list_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom']
    room_type_list_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom']
    for room_one in room_list:
        room_key, room_type = '', ''
        if 'id' in room_one:
            room_key = room_one['id']
        if 'type' in room_one:
            room_type = room_one['type']
        if len(room_key) <= 0:
            continue
        if room_key in replace_room:
            # 还原信息
            replace_val = replace_room[room_key]
            replace_type, replace_style, replace_seed = '', '', []
            if 'type' in replace_val:
                replace_type = replace_val['type']
            if 'style' in replace_val:
                replace_style = replace_val['style']
            # 还原风格
            if len(replace_style) > 0:
                replace_style = get_furniture_style_en(replace_style)
                replace_val['style'] = replace_style
                style_mode = replace_style
            # 还原种子
            furniture_list, decorate_list = [], []
            if 'furniture_info' in room_one:
                furniture_list = room_one['furniture_info']
            if 'decorate_info' in room_one:
                decorate_list = room_one['decorate_info']
            if len(furniture_list) > 0:
                # 查找种子
                seed_list, keep_list, plus_list, mesh_list = compute_room_seed(furniture_list, decorate_list, room_type)
                seed_one = {}
                for seed_one in seed_list:
                    seed_key, seed_style, seed_group, seed_role = seed_one['id'], '', '', ''
                    if 'style' in seed_one:
                        seed_style = seed_one['style']
                    if 'group' in seed_one and 'role' in seed_one:
                        seed_group, seed_role = seed_one['group'], seed_one['role']
                    if seed_role in ['sofa', 'bed', 'table']:
                        replace_seed.append(seed_key)
                        replace_note[seed_key] = seed_one
                        if len(replace_style) <= 0 and len(seed_style) > 0:
                            replace_style = seed_style
                            style_mode = seed_style
                if len(replace_seed) <= 0 and len(seed_one) > 0:
                    seed_key, seed_style, seed_group, seed_role = seed_one['id'], '', '', ''
                    if 'style' in seed_one:
                        seed_style = seed_one['style']
                    replace_seed.append(seed_key)
                    replace_note[seed_key] = seed_one
                    if len(replace_style) <= 0 and len(seed_style) > 0:
                        replace_style = seed_style
                        style_mode = seed_style
                if len(replace_seed) > 0:
                    replace_more[room_key] = {'soft': replace_seed}
                    replace_keep[room_key] = {'soft': replace_seed}
        elif room_key in replace_info:
            replace_more[room_key] = replace_info[room_key]
        elif room_type in replace_info:
            replace_more[room_key] = replace_info[room_type]
        elif room_type in room_type_list_1:
            for type_new in room_type_list_1:
                if type_new in replace_info:
                    replace_more[room_key] = replace_info[type_new]
                    break
        elif room_type in room_type_list_2:
            for type_new in room_type_list_2:
                if type_new in replace_info:
                    replace_more[room_key] = replace_info[type_new]
                    break
        elif room_type in room_type_list_3:
            for type_new in room_type_list_3:
                if type_new in replace_info:
                    replace_more[room_key] = replace_info[type_new]
                    break
    for room_key, room_val in replace_more.items():
        replace_wall, replace_floor, replace_soft = [], [], []
        if 'wall' in room_val:
            replace_wall = room_val['wall']
        if 'floor' in room_val:
            replace_floor = room_val['floor']
        if 'soft' in room_val:
            replace_soft = room_val['soft']
        for object_key in replace_soft:
            if object_key not in replace_note:
                object_type, object_style, object_size = get_furniture_data(object_key)
                object_new = {
                    'id': object_key, 'type': object_type, 'style': object_style,
                    'size': object_size[:], 'scale': [1, 1, 1],
                    'position': [0, 0, 0], 'rotation': [0, 0, 0, 1]
                }
                replace_note[object_key] = object_new
    # 硬装信息
    paint_replace = {}
    material_org = {}
    room_entity_id_dict = dict([(k.split('-')[-1], k) for k in list(layout_info.keys())])
    for room_key, room_fix in replace_info.items():
        if room_key.split('-')[-1] not in room_entity_id_dict:
            continue
        room_key = room_entity_id_dict[room_key.split('-')[-1]]
        layout_one, scheme_set = layout_info[room_key], []
        if 'layout_scheme' in layout_one:
            scheme_set = layout_one['layout_scheme']
        for scheme_one in scheme_set:
            material_old, material_new = {}, {}
            if 'material' in scheme_one:
                material_old = scheme_one['material']
            material_new['id'], material_new['type'] = material_old['id'], material_old['type']
            replace_mat = update_room_replace_material_seed(material_new, room_fix)
            paint_replace[room_key] = replace_mat
            material_org[room_key] = material_old

            scheme_one['material'] = material_new

    # 原有场景
    scene_json_old = {}
    if len(scene_path) > 0 and os.path.exists(scene_path):
        scene_json_old = json.load(open(scene_path, 'r', encoding='utf-8'))

    scene_json_new, decoration_changes = house_replace_house(house_info, layout_info, scene_json_old, paint_replace, material_org, house_mode={'debug':False})
    # 更新场景 删除MESH 添加MESH TODO:
    # scene_json_new, decoration_remove, decoration_append = scene_json_old, [], {}

    # 返回信息
    return scene_json_new, decoration_changes


# 功能测试
if __name__ == '__main__':
    # 清空缓存
    layout_sample_clear()
    pass
    start = time.time()
    # 测试接口 铺贴替换
    layout_param_input = smart_decoration_input_paint_test_98
    layout_param_output = layout_sample_decoration(layout_param_input)
    pass
    print(time.time()-start)
    # 数据更新
    # save_furniture_data()
    save_material_data()
    save_ceramic_reference_data()
    pass
