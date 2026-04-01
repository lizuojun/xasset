# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-12-08
@Description: 智能组合服务 支持组合提取、组合生成、组合渲染、一键配饰、内空检测

"""

import time
import shutil
import traceback
from copy import deepcopy

from layout import *
from layout_def import *
from House.house_scene import *
from House.house_scene_render import *
from ImportHouse.room_search import *
from LayoutByRule.house_interior_refine import extract_mesh_data

from HouseSearch.group_scene_search import search_scene_list
from LayoutGroup.generate_group import generate_group

# 临时目录
DATA_DIR_SERVER_INPUT = os.path.dirname(__file__) + '/temp/input/'
if not os.path.exists(DATA_DIR_SERVER_INPUT):
    os.makedirs(DATA_DIR_SERVER_INPUT)
DATA_DIR_SERVER_SCHEME = os.path.dirname(__file__) + '/temp/scheme/'
if not os.path.exists(DATA_DIR_SERVER_SCHEME):
    os.makedirs(DATA_DIR_SERVER_SCHEME)
DATA_DIR_SERVER_GROUP = os.path.dirname(__file__) + '/temp/group/'
if not os.path.exists(DATA_DIR_SERVER_GROUP):
    os.makedirs(DATA_DIR_SERVER_GROUP)
# 设计目录
DATA_DIR_RECORD = os.path.dirname(__file__) + '/LayoutRecord/'
if not os.path.exists(DATA_DIR_RECORD):
    os.makedirs(DATA_DIR_RECORD)

# 组合服务位置
DATA_OSS_LAYOUT = 'ihome-alg-layout'
DATA_URL_LAYOUT = 'https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com'
# 组合服务计数
LAYOUT_GROUP_CNT = 0

# 家具推荐服务
FURNITURE_PROPOSE_UAT = 'https://tui.alibaba-inc.com/recommend'
FURNITURE_PROPOSE_PRE = 'https://tuipre.taobao.com/recommend'
FURNITURE_PROPOSE_PRO = 'https://tui.alibaba-inc.com/recommend'
FURNITURE_PROPOSE_URL = ''

FURNITURE_PROPOSE_APP_ID = 18328
FURNITURE_PROPOSE_APP_ID = 20724
FURNITURE_PROPOSE_APP_ID = 21349

FURNITURE_PROPOSE_USR_ID = 999999999
# 推荐饰品类目
ACCESSORY_PROPOSE_CATE = {
    '水杯': '306683105552086396',
    '水壶': '399285165658374617',
    '餐具': '1065999068730034507',
    '餐具组合': '1065999068730034507',
    '餐巾': '349015944510734521',
    '桌布': '224423740170333958',
    '桌旗': '565485912911220765',
    '酒具': '968111435184745614',
    '酒具组合1': '968111435184745614',
    '酒具组合2': '968111435184745614',
    '茶具': '466455169483545160',
    '茶具组合': '466455169483545160',
    '花卉': '106720406196150644',
    '绿植': '757066893061548622',
    '植物': '698674408537181596',
    '工艺品': '813701230071893827',
    '烛台': '917040543660950016',
    '相框': '927012310643543623',
    '雕塑': '850542737243497106',
    '香薰': '117929994474730583',
    '器皿': '910895025086708910',
    '装饰画': '418921774629632064',
    '电脑': '1046340838530186815',
    '娱乐': '1046340838530186815',
    '台灯': '271659787935123395',
    '书籍': '513852033238140987',
    '书籍组合1': '513852033238140987',
    '书籍组合2': '513852033238140987',
    '书籍组合3': '513852033238140987',
    '杂志': '513852033238140987',
    '化妆品': '488822817059193722',
    '化妆品组合1': '488822817059193722',
    '化妆品组合2': '488822817059193722',
    '化妆品组合3': '488822817059193722',
    '洗浴品': '488822817059193722',
    '洗浴品组合1': '488822817059193722',
    '洗浴品组合2': '488822817059193722',
    '抱枕': '905951098803818693',
    '盖毯': '17832309032120881',
    '毛巾': '1099346382666601118',
    '鞋子': '585723299142419563'
}
# 推荐家具错误
FURNITURE_PROPOSE_ERROR = [
    'a6b3f563-fae5-4cf1-a4d8-9e4039101560',
    '9c3ed38a-6f44-4feb-8069-1538550dded7',
    '407d2225-7fe1-439a-8f9d-bb8ef8d94430'
]
FURNITURE_PROPOSE_WRINK = [
    '4dff5417-99cb-41cd-a26b-f905cf165b36',
    'd9a13d5c-a68a-4302-8fd6-556602d9ff2e',
    '150a6cad-6d0e-4ab4-aaa5-c4b3508d3469'
]
FURNITURE_PROPOSE_PIANO = ['1b51dd12-0f5e-4d3d-bf6f-1e9e73dc14cb']

# 推荐飘窗种子
FURNITURE_PROPOSE_WINDOW = [
    'abd99c3d-1917-44ec-9f96-e86ed474109a',
    '47aa19fa-34fc-44b1-8bdb-da62086daa0b',
    '190187da-f385-4f20-9535-bf4645147260']

# 推荐家具种子
FURNITURE_PROPOSE_SEED = {
    'Meeting sofa': '沙发', 'Meeting table': '茶几', 'Meeting side sofa': '边椅', 'Meeting side table': '边几', 'Meeting rug': '地毯',
    'Dining table': '餐桌', 'Dining chair': '餐椅', 'Dining cabinet': '餐边柜',
    'Bed bed': '床', 'Bed table': '床前几', 'Bed side table': '床头柜', 'Bed rug': '地毯',
    'Media table': '电视柜', 'Media tv': '电视',
    'Library Work table': '办公桌', 'Library Work table': '办公椅', 'Library Work rug': '地毯',
    'Bedroom Work table': '梳妆桌', 'Bedroom Work table': '梳妆椅', 'Bedroom Work rug': '地毯',
    'Rest table': '休闲桌', 'Rest chair': '休闲椅',
    'Hallway cabinet': '玄关柜',
    'CloakRoom cabinet': '衣柜', 'CloakRoom armoire': '衣柜',
}


# 组合提取服务
def layout_group_extract_once(design_id, upload_group=False, upload_room=False, local_group=False,
                              save_code=20, save_num=20, save_mode=[]):
    design_id = design_id.rstrip()
    layout_log_0 = 'group house ' + design_id
    print(layout_log_0)
    try:
        # house_data = house_design_trans(design_id)
        house_para, house_data = get_house_data(design_id)
        if 'room' in house_data and len(house_data['room']) > 0:
            pass
        else:
            house_id_new, house_data_new, house_feature_new = get_house_data_feature(design_id, True)
            house_data = house_data_new
        house_data_info, house_layout_info, house_group_info = group_house(house_data)
        save_dir = layout_group_mkdir(DATA_DIR_SERVER_GROUP, design_id)
        group_save(house_group_info, design_id, save_dir, save_code, save_num, [SAVE_MODE_GROUP],
                   upload_group, upload_room)
        if len(save_mode) > 0:
            house_save(design_id, '', 1, 1,
                       house_data_info, house_layout_info, {},
                       design_id + '_sample', DATA_DIR_SERVER_GROUP, save_mode,
                       suffix_flag=False, sample_flag=False, upload_flag=False)
        # 添加组合
        if local_group:
            # 清空组合
            del_furniture_group(design_id, '')
            # 添加组合
            for room_id, room_group in house_group_info.items():
                room_type, room_style = room_group['room_type'], room_group['room_style']
                group_functional, group_decorative = room_group['group_functional'], room_group['group_decorative']
                # 判断组合
                if 'Bath' in room_type:
                    object_wall, object_floor = [], []
                    for group_one in group_decorative:
                        if group_one['type'] == 'Wall':
                            if 'obj_list' in group_one:
                                object_wall = group_one['obj_list']
                        elif group_one['type'] == 'Floor':
                            if 'obj_list' in group_one:
                                object_floor = group_one['obj_list']
                    if len(group_functional) >= 2 or len(object_wall) + len(object_floor) >= 2:
                        for group_one in group_functional:
                            add_furniture_group(design_id, room_id, group_one, fine_flag=True)
                        for group_one in group_decorative:
                            add_furniture_group(design_id, room_id, group_one, fine_flag=True)
                else:
                    for group_one in group_functional:
                        add_furniture_group(design_id, room_id, group_one, fine_flag=True)
                    for group_one in group_decorative:
                        add_furniture_group(design_id, room_id, group_one, fine_flag=True)
                # 下载家具
                for group_one in group_functional:
                    for object_one in group_one['obj_list']:
                        object_id = object_one['id']
                        download_furniture(object_id, DATA_DIR_FURNITURE, '.jpg')
                        download_furniture(object_id, DATA_DIR_FURNITURE, '.json')
                for group_one in group_decorative:
                    for object_one in group_one['obj_list']:
                        object_id = object_one['id']
                        download_furniture(object_id, DATA_DIR_FURNITURE, '.jpg')
                        download_furniture(object_id, DATA_DIR_FURNITURE, '.json')
            # 保存组合
            save_furniture_group_fine()
    except Exception as e:
        layout_log_0 = 'group error ' + design_id
        print(layout_log_0)
        print(e)


# 组合提取服务
def layout_group_extract_more(design_list, upload_group=False, upload_room=False, save_code=20, save_num=20):
    if len(design_list) <= 0:
        return
    # 遍历户型
    for url_idx, url_one in enumerate(design_list):
        design_id = url_one.rstrip()
        layout_log_0 = 'group house %s %03d' % (design_id, url_idx)
        print(layout_log_0)
        try:
            # house_data = house_design_trans(design_id)
            house_para, house_data = get_house_data(design_id)
            if len(house_data) <= 0:
                layout_log_0 = 'house empty %s %03d' % (design_id, url_idx)
                print(layout_log_0)
            house_data_info, house_layout_info, house_group_info = group_house(house_data)
            save_dir = layout_group_mkdir(DATA_DIR_SERVER_GROUP, design_id)
            group_save(house_group_info, design_id, save_dir, save_code, save_num, [SAVE_MODE_GROUP],
                       upload_group, upload_room)
        except Exception as e:
            layout_log_0 = 'group error %s %03d' % (design_id, url_idx)
            print(layout_log_0)
            print(e)


# 组合生成服务 TODO:
def layout_group_generate(plat_id, plat_entity, house_group, layout_num=3, propose_num=3, request_log=False):
    group_origin, group_sample, group_scheme = {}, [], []
    if plat_id == '' and plat_entity == '':
        return group_origin, group_sample, group_scheme
    # 组合提取
    plat_info, plat_group, room_id, room_area, room_type, room_style = group_analyze(plat_id, plat_entity, house_group)
    # 组合检索 TODO:

    # 组合生成 TODO:
    pass

    # 组合替换 TODO:
    pass
    # 配饰生成 TODO:

    # 配饰推荐

    # 配饰替换

    # 打印信息
    layout_log_0 = 'finish group ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    print(layout_log_0)
    # 返回信息
    return group_origin, group_sample, group_scheme


# 配饰生成服务
def layout_group_decorate(plat_id, plat_entity, house_group, layout_num=3, propose_num=3, request_log=False):
    group_origin, group_sample, group_scheme = {}, [], []
    if plat_id == '' and plat_entity == '':
        return group_origin, group_sample, group_scheme
    # 组合提取
    plat_info, plat_group, room_id, room_area, room_type, room_style = group_analyze(plat_id, plat_entity, house_group)
    if 'type' not in plat_group:
        return group_origin, group_sample, group_scheme
    if 'style' not in plat_group:
        plat_group['style'] = ''
    plat_type = plat_info['type']
    # 配饰布局
    object_origin = []
    if len(plat_group) > 0 and len(plat_info) > 0:
        plat_position, plat_rotation = plat_info['position'], plat_info['rotation']
        object_list = plat_group['obj_list']
        # 原有方案
        for object_one in object_list:
            if 'relate' in object_one and object_one['relate'] == plat_id:
                if 'relate_position' in object_one:
                    relate_position = object_one['relate_position']
                    if abs(relate_position[0] - plat_position[0]) + abs(relate_position[2] - plat_position[2]) < 0.1:
                        object_origin.append(object_one)
        group_object = object_origin
        group_object.insert(0, plat_info)
        group_origin = copy_group(plat_group)
        group_origin['obj_list'] = group_object
        # 布局方案
        group_type, group_style, group_size = plat_group['type'], plat_group['style'], plat_group['size']
        group_min = {'type': group_type, 'style': group_style, 'size': group_size, 'obj_list': [plat_info]}
        group_set = compute_plat_raise(room_type, room_style, group_min, plat_info, layout_num, [], True, True)
        for group_add in group_set:
            group_sample.append(group_add)
    # 配饰补充
    for group_idx, group_one in enumerate(group_sample):
        group_type, group_size = group_one['type'], group_one['size']
        if group_type in ['Media'] and group_idx > 0:
            pass
        elif group_type in ['Media'] and group_size[1] > 1.0:
            pass
        else:
            add_furniture_group_deco(group_one)
    # 配饰推荐
    propose_info = []
    if len(group_sample) > 0:
        for group_one in group_sample:
            target_scope = accessory_scope(group_one, plat_id)
            propose_one = {
                'id': room_id, 'type': room_type, 'area': room_area,
                'target_seed': [{'id': plat_id, 'type': plat_type, 'entityId': plat_entity}],
                'target_style': [], 'target_scope': target_scope
            }
            propose_info.append(propose_one)
        propose_accessory(propose_info, propose_num, plat_id, False, request_log)
    # 配饰替换
    layout_log_0 = 'adjust group ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    print(layout_log_0)
    if len(group_sample) > 0:
        group_scheme = group_replace(group_sample, propose_info, plat_info)
    layout_log_0 = 'finish group ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    print(layout_log_0)
    # 返回信息
    return group_origin, group_sample, group_scheme


# 内空布局服务
def layout_inner_generate(plat_id, plat_entity, house_data, layout_num=1, propose_num=1, request_log=False):
    inner_data = {}
    # 遍历房间
    room_list = []
    if 'room' in house_data:
        room_list = house_data['room']
    for room_one in room_list:
        room_name = room_one['id']
        for object_one in room_one['furniture_info']:
            object_id = ''
            if 'id' in object_one:
                object_id = object_one['id']
            if object_id == plat_id or plat_id == '':
                inner_origin = compute_plat_inner(object_one)
                if room_name not in inner_data:
                    inner_data[room_name] = []
                inner_data[room_name].append(inner_origin)
                if plat_id != '':
                    return inner_data
    # 返回信息
    return inner_data


# 组合服务入口
def layout_group_param(param_info, request_log=False):
    # 户型参数
    house_id, room_id, plat_id, plat_entity, mesh_url = '', '', '', '', ''
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
    # 商品参数
    item_id = ''
    scene_item, view_width, view_height = {}, 800, 800
    if 'scene_item' in param_info:
        scene_item = param_info['scene_item']
        item_id = 'item'
        if 'id' in scene_item:
            item_id = scene_item['id']
    # 场景参数
    scene_list = []

    # 布局模式
    layout_mode = LAYOUT_MODE_ADORN
    if 'layout_mode' in param_info:
        if param_info['layout_mode'] == LAYOUT_MODE_GROUP:
            layout_mode = LAYOUT_MODE_GROUP
        elif param_info['layout_mode'] == LAYOUT_MODE_ADORN:
            layout_mode = LAYOUT_MODE_ADORN
        elif param_info['layout_mode'] == LAYOUT_MODE_INNER:
            layout_mode = LAYOUT_MODE_INNER
    layout_num, propose_num = 2, 2
    if layout_mode == LAYOUT_MODE_ADJUST:
        layout_num, propose_num = 1, 1
    if 'layout_number' in param_info:
        layout_num = param_info['layout_number']
    if 'propose_number' in param_info:
        propose_num = param_info['propose_number']

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
    if len(save_mode) <= 0:
        save_mode.append(SAVE_MODE_GROUP)

    # 组合信息
    house_layout_info, house_group_info = {}, {}
    plat_group_origin, plat_group_sample, plat_group_scheme = {}, [], []
    plat_inner_origin = {}
    try:
        # 打印信息
        print()
        layout_log_0 = 'layout group ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
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
            scene_each = {
                'id': house_id,
                'url': '',
                'loc': scene_path,
                'layout': house_layout_info
            }
            scene_list.append(scene_each)
        # 组合提取
        elif len(house_data) > 0 and 'room' in house_data:
            if 'id' in house_data and house_id == '':
                house_id = house_data['id']
            room_list = []
            if 'room' in house_data:
                room_list = house_data['room']
            if len(mesh_url) > 0:
                house_data = extract_mesh_data(house_data, mesh_url)
            for room_one in room_list:
                if 'coordinate' not in room_one:
                    room_one['coordinate'] = 'xyz'
                if 'unit' not in room_one:
                    room_one['unit'] = 'm'
                if 'door_info' not in room_one:
                    room_one['door_info'] = []
                if 'hole_info' not in room_one:
                    room_one['hole_info'] = []
                if 'window_info' not in room_one:
                    room_one['window_info'] = []
                if 'baywindow_info' not in room_one:
                    room_one['baywindow_info'] = []
            house_data_info, house_layout_info, house_group_info = group_house(house_data)
            scene_each = {
                'id': house_id,
                'url': '',
                'loc': scene_path,
                'layout': house_layout_info
            }
            scene_list.append(scene_each)

        # 组合生成
        if len(house_group_info) <= 0 or layout_mode == LAYOUT_MODE_GROUP and not plat_id == '':
            plat_group_origin, plat_group_sample, plat_group_scheme = \
                layout_group_generate(plat_id, plat_entity, house_group_info, layout_num, propose_num, request_log)
        # 配饰生成
        elif len(house_group_info) > 0 and layout_mode == LAYOUT_MODE_ADORN and not plat_id == '':
            plat_group_origin, plat_group_sample, plat_group_scheme = \
                layout_group_decorate(plat_id, plat_entity, house_group_info, layout_num, propose_num, request_log)
        # 内空生成
        elif len(house_group_info) > 0 and layout_mode == LAYOUT_MODE_INNER:
            plat_inner_origin = \
                layout_inner_generate(plat_id, plat_entity, house_data, layout_num, propose_num, request_log)
        # 场景生成
        elif len(house_group_info) >= 0 and len(scene_item) > 0:
            item_key, item_val, item_room, item_group, item_role = '', {}, [], [], []
            if 'item' in scene_item:
                item_key = scene_item['item']
                item_val = get_furniture_role_by_item(item_key)
            if 'room' in item_val:
                item_room = item_val['room']
            if 'group' in item_val:
                item_group = item_val['group']
            if 'role' in item_val:
                item_role = item_val['role']
            scene_list = group_search(item_room, item_group, item_role, house_num=10, house_rand=True, content_type_list=[])
            for scene_each in scene_list:
                scene_key, scene_url, scene_layout = scene_each['id'], scene_each['url'], scene_each['layout']
                house_have, scene_path = download_scene_by_url(scene_url, DATA_DIR_SERVER_INPUT, scene_key)
                if house_have and os.path.exists(scene_path):
                    scene_each['loc'] = scene_path
                    if len(scene_layout) <= 0:
                        house_id_new, house_data, house_feature = get_house_data_feature_by_path(scene_path)
                        if len(house_id_new) > 0:
                            scene_each['id'] = house_id_new
                        if len(house_data) > 0 and 'room' in house_data:
                            room_list = []
                            if 'room' in house_data:
                                room_list = house_data['room']
                            for room_one in room_list:
                                if 'coordinate' not in room_one:
                                    room_one['coordinate'] = 'xyz'
                                if 'unit' not in room_one:
                                    room_one['unit'] = 'm'
                            house_data, house_layout, house_group = group_house(house_data)
                            scene_each['layout'] = house_layout

        # 打印信息
        layout_log_0 = 'layout group success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        # 保存组合
        if len(save_mode) > 0:
            if len(plat_group_scheme + plat_group_sample) > 0:
                save_id = plat_id
                save_dir = layout_group_mkdir(DATA_DIR_SERVER_GROUP, save_id)
                group_list = []
                for group_new in [plat_group_origin]:
                    group_list.append(group_new)
                    pass
                for group_new in plat_group_sample:
                    group_list.append(group_new)
                    pass
                for group_new in plat_group_scheme:
                    group_list.append(group_new)
                if SAVE_MODE_GROUP in save_mode:
                    group_save_list(group_list, save_id, save_dir, '')
            elif len(plat_id) > 0:
                save_id = plat_id
                save_dir = layout_group_mkdir(DATA_DIR_SERVER_GROUP, save_id)
                group_list = []
                for group_new in [plat_group_origin]:
                    group_list.append(group_new)
                if SAVE_MODE_GROUP in save_mode:
                    group_save_list(group_list, save_id, save_dir, '')
            else:
                save_id = house_id
                save_dir = layout_group_mkdir(DATA_DIR_SERVER_GROUP, save_id)
                upload_group, upload_room = False, False
                if SAVE_MODE_RENDER in save_mode:
                    pass
                elif SAVE_MODE_GROUP in save_mode:
                    group_save(house_group_info, save_id, save_dir, 10, 15, save_mode, upload_group, upload_room)
                if len(save_mode) > 0:
                    house_save(house_id, '', 1, 1,
                               house_data_info, house_layout_info, {},
                               house_id + '_sample', save_dir, save_mode,
                               suffix_flag=False, sample_flag=False, upload_flag=False)

        # 打印信息
        layout_log_0 = 'layout group success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
    except Exception as e:
        house_group_info, house_layout_info = {}, {}
        # 错误信息
        print(traceback.print_exc())
        layout_log_0 = 'layout group failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        print(layout_log_0)
        print(e)

    # 计数信息
    layout_group_count()

    # 镜像信息
    room_mirror = 0
    if len(room_data) > 0 and 'mirror' in room_data:
        room_mirror = room_data['mirror']
    elif len(house_data) > 0 and 'room' in house_data:
        for room_one in house_data['room']:
            if len(room_one) > 0 and 'mirror' in room_one:
                room_mirror = room_one['mirror']
                break

    # 输出处理
    group_num = 0
    group_origin, group_sample, group_scheme = [], [], []
    inner_origin = {}
    if plat_id == '':
        group_sample = house_group_info
        for room_key, room_group in group_sample.items():
            if 'group_functional' in room_group:
                group_num += len(room_group['group_functional'])
    else:
        # 组合调整
        group_one = plat_group_origin
        group_origin = group_trans_overlap(group_one, room_mirror, skip_id=plat_id)
        for group_one in plat_group_sample:
            group_add = group_trans_overlap(group_one, room_mirror, skip_id=plat_id)
            group_sample.append(group_add)
        for group_one in plat_group_scheme:
            group_add = group_trans_overlap(group_one, room_mirror, skip_id=plat_id)
            group_scheme.append(group_add)
        group_num = len(group_scheme)
        # 内空调整
        inner_origin = plat_inner_origin

    # 输出信息
    layout_version = '20220411.2000'
    layout_output = {
        'house_id': house_id,
        'room_id': room_id,
        'group_num': group_num,
        'group_origin': group_origin,
        'group_sample': group_sample,
        'group_scheme': group_scheme,
        'layout_version': layout_version
    }
    if layout_mode in [LAYOUT_MODE_INNER]:
        layout_output = {
            'house_id': house_id,
            'room': plat_inner_origin,
            'layout_version': layout_version
        }

    # 渲染信息
    if SAVE_MODE_RENDER in save_mode:
        layout_output = {
            'house_id': house_id,
            'room_id': room_id,
            'image_key': [],
            'image_val': [],
            'layout_version': layout_version
        }
        for scene_each in scene_list:
            # 户型位置
            scene_key, scene_path, scene_layout = scene_each['id'], scene_each['loc'], scene_each['layout']
            scene_key_old, scene_key_new = '', ''
            save_dir = layout_group_mkdir(DATA_DIR_SERVER_GROUP, scene_key)
            house_scene_json = json.load(open(scene_path, 'r', encoding='utf-8'))
            # 装修渲染
            if 'decorate' in render_mode:
                item_id = 'decorate'
                # 户型原样
                if 'original' in render_mode:
                    # 户型保存
                    save_time = datetime.datetime.now().strftime('%H-%M-%S')
                    save_id = scene_key + '_original'
                    json_path = os.path.join(save_dir, save_id + '.json')
                    with open(json_path, "w") as f:
                        # json.dump(house_scene_json, f, indent=4)
                        json.dump(house_scene_json, f)
                        f.close()
                    # 户型上传
                    scene_key_old = house_scene_upload(house_scene_json, save_id, json_path)
                # 户型处理
                house_keep_type = parse_object_keep()
                house_scene_clear_object(house_scene_json, house_keep_type)
                # 户型保存
                save_time = datetime.datetime.now().strftime('%H-%M-%S')
                save_id = scene_key
                json_path = os.path.join(save_dir, save_id + '.json')
                with open(json_path, "w") as f:
                    # json.dump(house_scene_json, f, indent=4)
                    json.dump(house_scene_json, f)
                    f.close()
                # 户型上传
                scene_key_new = house_scene_upload(house_scene_json, save_id, json_path)
                # 遍历房间
                for room_key, room_val in scene_layout.items():
                    room_type = room_val['room_type']
                    room_layout = room_val
                    room_scheme, group_todo = {}, []
                    if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
                        room_scheme = room_layout['layout_scheme'][0]
                        if 'group' in room_scheme:
                            group_todo = room_scheme['group']
                    # 遍历组合
                    group_find = group_filter(group_todo, render_mode, {})
                    for group_idx, group_one in enumerate(group_find):
                        group_type = group_one['type']
                        # 机位处理
                        camera_param, render_key, render_val = {}, '', {}
                        outdoor_type, view_mode = '', 0
                        camera_param = group_camera(group_one)
                        # 渲染处理
                        render_id = '%s_%s-%s_decorate' % (save_id, room_type, group_type)
                        if len(house_scene_json) > 0 and len(camera_param) > 0:
                            render_key, render_val = \
                                house_scene_render(render_id, house_scene_json, camera_param, outdoor_type, view_mode,
                                                   save_dir, scene_key_new, view_width, view_height)
                        # 打印信息
                        if len(render_val) > 0:
                            layout_log_0 = 'render success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            print(layout_log_0)
                        else:
                            layout_log_0 = 'render failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            print(layout_log_0)
                        # 添加渲染
                        if len(render_key) > 0:
                            layout_output['image_key'].append(render_key)
                        # 对比渲染
                        if 'original' in render_mode:
                            render_id = '%s_%s-%s_original' % (save_id, room_type, group_type)
                            if len(house_scene_json) > 0 and len(camera_param) > 0:
                                render_key, render_val = \
                                    house_scene_render(render_id, house_scene_json,
                                                       camera_param, outdoor_type, view_mode, save_dir, scene_key_old)
                            if len(render_key) > 0:
                                layout_output['image_key'].append(render_key)
            # 商品渲染
            if 'object' in render_mode and len(scene_item) > 0:
                # 遍历房间
                operate_dict = {}
                for room_key, room_val in scene_layout.items():
                    room_type = room_val['room_type']
                    room_layout = room_val
                    room_scheme, group_todo = {}, []
                    if 'layout_scheme' in room_layout and len(room_layout['layout_scheme']) > 0:
                        room_scheme = room_layout['layout_scheme'][0]
                        if 'group' in room_scheme:
                            group_todo = room_scheme['group']
                    # 遍历组合
                    group_find = group_filter(group_todo, render_mode, scene_item, room_type)
                    if len(group_find) <= 0:
                        continue
                    # 组合处理
                    operate_info = {}
                    for group_idx, group_one in enumerate(group_find):
                        group_new, operate_info = group_adjust(group_one, group_todo, room_type=room_type)
                    operate_dict[room_key] = operate_info
                # 户型原样
                if 'original' in render_mode:
                    operate_back = {}
                    for room_key, room_val in operate_dict.items():
                        room_val_old = {
                            'target': [],
                            'relate': [],
                            'append': room_val['append'],
                            'remove': room_val['remove'],
                            'adjust': []
                        }
                        room_val_new = {
                            'target': room_val['target'],
                            'relate': room_val['relate'],
                            'append': [],
                            'remove': [],
                            'adjust': []
                        }
                        operate_back[room_key] = room_val_old
                        operate_dict[room_key] = room_val_new
                    # 户型处理
                    house_scene_switch_object(house_scene_json, operate_back)
                    # 户型保存
                    save_time = datetime.datetime.now().strftime('%H-%M-%S')
                    save_id = scene_key + '_original'
                    json_path = os.path.join(save_dir, save_id + '.json')
                    with open(json_path, "w") as f:
                        # json.dump(house_scene_json, f, indent=4)
                        json.dump(house_scene_json, f)
                        f.close()
                    # 户型上传
                    scene_key_old = house_scene_upload(house_scene_json, save_id, json_path)
                # 户型处理
                house_scene_switch_object(house_scene_json, operate_dict)
                # 户型保存
                save_time = datetime.datetime.now().strftime('%H-%M-%S')
                save_id = scene_key
                json_path = os.path.join(save_dir, save_id + '.json')
                with open(json_path, "w") as f:
                    # json.dump(house_scene_json, f, indent=4)
                    json.dump(house_scene_json, f)
                    f.close()
                # 户型上传
                scene_key_new = house_scene_upload(house_scene_json, save_id, json_path)
                # 遍历房间
                for room_key, operate_val in operate_dict.items():
                    target_list = []
                    if 'target' in operate_val:
                        target_list = operate_val['target']
                    for object_idx, object_one in enumerate(target_list):
                        # 商品处理
                        item_size = [1, 1, 1]
                        if 'item' in object_one:
                            item_one = object_one['item']
                            item_size = [abs(item_one['size'][i] * item_one['scale'][i]) / 100 for i in range(3)]
                        # 机位处理
                        camera_param, render_key, render_val = {}, '', {}
                        outdoor_type, view_mode = '', 0
                        if 'camera' in object_one:
                            camera_param = object_one['camera']
                        # 渲染处理
                        render_id = '%s_%s' % (save_id, room_key)
                        if len(house_scene_json) > 0 and len(camera_param) > 0:
                            render_key, render_val = \
                                house_scene_render(render_id, house_scene_json,
                                                   camera_param, outdoor_type, view_mode, save_dir, scene_key_new)
                        # 打印信息
                        if len(render_val) > 0:
                            layout_log_0 = 'render success ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            print(layout_log_0)
                        else:
                            layout_log_0 = 'render failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            print(layout_log_0)
                        # 添加渲染
                        if len(render_key) > 0:
                            layout_output['image_key'].append(render_key)
                        # 添加信息
                        if len(render_key) > 0:
                            # 区域信息 TODO:
                            item_region = compute_furniture_pixel(object_one, camera_param, view_width, view_height)
                            image_val = {
                                'id': render_key,
                                'url': '',
                                'loc': '',
                                'item_size': item_size,
                                'item_region': item_region
                            }
                            layout_output['image_val'].append(image_val)
                        # 对比渲染
                        if 'original' in render_mode:
                            render_id = '%s_%s_original' % (save_id, room_key)
                            if len(house_scene_json) > 0 and len(camera_param) > 0:
                                render_key, render_val = \
                                    house_scene_render(render_id, house_scene_json,
                                                       camera_param, outdoor_type, view_mode, save_dir, scene_key_old)
                            if len(render_key) > 0:
                                layout_output['image_key'].append(render_key)
                print(layout_output['image_key'])
    # 图片信息
    if 'result' in render_mode:
        # 位置
        save_id = plat_id
        if len(item_id) > 0:
            save_id = item_id
        save_dir = layout_group_mkdir(DATA_DIR_SERVER_GROUP, save_id)
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
        save_dir = layout_group_mkdir(DATA_DIR_SERVER_GROUP, save_id)
        save_des = os.path.join(save_dir, save_id + '_output.json')
        with open(save_des, "w") as f:
            json.dump(layout_output, f, indent=4)
            f.close()

    # 返回信息
    return layout_output


# 组合服务目录
def layout_group_mkdir(save_dir, save_id):
    save_dir_new = os.path.join(save_dir, save_id)
    if not os.path.exists(save_dir_new):
        os.makedirs(save_dir_new)
    return save_dir_new


# 组合服务计数
def layout_group_count(count_max=200):
    # 调用信息
    global LAYOUT_GROUP_CNT
    LAYOUT_GROUP_CNT += 1
    if LAYOUT_GROUP_CNT >= count_max:
        # 重置
        LAYOUT_GROUP_CNT = 0
        # 清空
        layout_group_clear()


# 组合服务清空
def layout_group_clear():
    # 清空
    if os.path.exists(DATA_DIR_SERVER_GROUP):
        shutil.rmtree(DATA_DIR_SERVER_GROUP)
    if os.path.exists(DATA_DIR_SERVER_SERVICE):
        shutil.rmtree(DATA_DIR_SERVER_SERVICE)
    # 重建
    if not os.path.exists(DATA_DIR_SERVER_GROUP):
        os.makedirs(DATA_DIR_SERVER_GROUP)
    if not os.path.exists(DATA_DIR_SERVER_SERVICE):
        os.makedirs(DATA_DIR_SERVER_SERVICE)


# 布局户型解析
def parse_design_data(design_id, design_url, scene_url=''):
    house_para_info, house_data_info = get_house_data(design_id, design_url, scene_url)
    if 'id' in house_data_info:
        house_id = design_id
        house_data_info['id'] = design_id
    if 'room' not in house_data_info:
        house_para_info, house_data_info = {}, {}
    elif 'room' in house_data_info and len(house_data_info['room']) <= 0:
        house_para_info, house_data_info = {}, {}
    return house_para_info, house_data_info


# 保留物品类型
def parse_object_keep():
    keep_type = []
    # 硬装
    for mesh_key, mesh_set in GROUP_MESH_DICT.items():
        for type_new in mesh_set:
            keep_type.append(type_new)
    # 门窗
    type_door = [
        'door/single swing door', 'door/double sliding door', 'door/single swing door',
        'door/entry/single swing door', 'door/entry/double swing door - asymmetrical',
        'barn door/barn door'
    ]
    type_window = [
        'window/window', 'window/bay window', 'window/floor-based window',
        'parametric corner window'
    ]
    for type_new in type_door:
        keep_type.append(type_new)
    for type_new in type_window:
        keep_type.append(type_new)
    # 挂画
    type_art = [
        'art/art - wall-attached', 'mirror/wall-attached mirror', 'accessory/accessory - wall-attached',
        'accessory/clock - wall-attached', 'accessory/bathroom accessory - wall-attached', 'attachment/taps',
        'lighting/wall lamp', 'appliance/appliance - wall-attached', 'toilet/wall-attached toilet',
        'cabinet/wall-attached cabinet']
    for type_new in type_art:
        keep_type.append(type_new)
    # 返回
    return keep_type


# 组合解析处理
def group_analyze(plat_id, plat_entity, house_group):
    # 组合提取
    plat_info, plat_group, plat_type, plat_style = {}, {}, '', ''
    room_id, room_area, room_type, room_style = '', '', '', ''
    for room_name, room_group in house_group.items():
        group_functional, group_decorative = [], []
        if 'group_functional' in room_group:
            group_functional = room_group['group_functional']
        if 'group_decorative' in room_group:
            group_decorative = room_group['group_decorative']
        for group_one in group_functional:
            object_set = group_one['obj_list']
            for object_one in object_set:
                object_id, object_entity = '', ''
                if 'id' in object_one:
                    object_id = object_one['id']
                if 'entityId' in object_one:
                    object_entity = object_one['entityId']
                if object_id == plat_id or plat_id == '':
                    room_id, room_area = room_name, room_group['room_area']
                    room_type, room_style = room_group['room_type'], room_group['room_style']
                    if object_entity == plat_entity or plat_entity == '':
                        plat_info, plat_group = object_one, group_one
                        plat_type, plat_style = object_one['type'], object_one['style']
                        break
                    else:
                        plat_info, plat_group = object_one, group_one
                        plat_type, plat_style = object_one['type'], object_one['style']
                        continue
        for group_one in group_decorative:
            if group_one['type'] not in ['Window']:
                continue
            for object_one in group_one['obj_list']:
                object_id, object_entity = '', ''
                if 'id' in object_one:
                    object_id = object_one['id']
                if 'entityId' in object_one:
                    object_entity = object_one['entityId']
                if object_id == plat_id or plat_id == '':
                    room_id, room_area = room_name, room_group['room_area']
                    room_type, room_style = room_group['room_type'], room_group['room_style']
                    if object_entity == plat_entity or plat_entity == '':
                        plat_info, plat_group = object_one, group_one
                        plat_type, plat_style = object_one['type'], object_one['style']
                        break
                    else:
                        plat_info, plat_group = object_one, group_one
                        plat_type, plat_style = object_one['type'], object_one['style']
                        continue
    group_type = ''
    if 'type' in plat_group:
        group_type = plat_group['type']
    # 组合纠正
    if not group_type == '':
        room_list = list_room_by_group(group_type)
        if room_type not in room_list:
            room_type = ''
            if len(room_list) > 0:
                room_type = room_list[0]
    # 信息返回
    return plat_info, plat_group, room_id, room_area, room_type, room_style


# 组合解析处理
def group_analyze_all(house_group):
    # 组合提取
    plat_info_list, plat_group_list, plat_type, plat_style = [], [], '', ''
    room_id, room_area, room_type, room_style = '', '', '', ''
    for room_name, room_group in house_group.items():
        group_functional, group_decorative = [], []
        if 'group_functional' in room_group:
            group_functional = room_group['group_functional']
        if 'group_decorative' in room_group:
            group_decorative = room_group['group_decorative']
        for group_one in group_functional:
            object_set = group_one['obj_list']
            for object_one in object_set:
                object_id, object_entity = '', ''
                if 'id' in object_one:
                    object_id = object_one['id']
                if 'entityId' in object_one:
                    object_entity = object_one['entityId']

                room_id, room_area = room_name, room_group['room_area']
                room_type, room_style = room_group['room_type'], room_group['room_style']

                plat_info, plat_group = object_one, group_one
                plat_type, plat_style = object_one['type'], object_one['style']
                plat_info_list.append(plat_info)
                plat_group_list.append(plat_group)

        for group_one in group_decorative:
            if group_one['type'] not in ['Window']:
                continue
            for object_one in group_one['obj_list']:
                object_id, object_entity = '', ''
                if 'id' in object_one:
                    object_id = object_one['id']
                if 'entityId' in object_one:
                    object_entity = object_one['entityId']

                room_id, room_area = room_name, room_group['room_area']
                room_type, room_style = room_group['room_type'], room_group['room_style']

                plat_info, plat_group = object_one, group_one
                plat_type, plat_style = object_one['type'], object_one['style']
                plat_info_list.append(plat_info)
                plat_group_list.append(plat_group)

    group_type = ''
    if 'type' in plat_group:
        group_type = plat_group['type']
    # 组合纠正
    if not group_type == '':
        room_list = list_room_by_group(group_type)
        if room_type not in room_list:
            room_type = ''
            if len(room_list) > 0:
                room_type = room_list[0]
    # 信息返回
    return plat_info, plat_group, room_id, room_area, room_type, room_style


# 组合配饰替换
def group_replace(group_sample, propose_info, plat_info):
    group_scheme = []
    # 平台信息
    plat_id = plat_info['id']
    plat_type = plat_info['type']
    plat_size = [abs(plat_info['size'][i] * plat_info['scale'][i]) / 100 for i in range(3)]
    # 配饰调整
    random_idx = random.randint(0, 100)
    for group_idx, group_one in enumerate(group_sample):
        if 'obj_list' not in group_one:
            continue
        group_type = group_one['type']
        if len(propose_info) <= 0:
            continue
        propose_idx = group_idx % len(propose_info)
        propose_one = propose_info[propose_idx]
        if 'target_furniture' not in propose_one or 'target_furniture_size' not in propose_one:
            continue
        # 配饰计数
        object_dict = {}
        if group_one['type'] in ['Meeting', 'Media', 'Dining', 'Cabinet']:
            for object_one in group_one['obj_list']:
                object_id, object_role = object_one['id'], object_one['role']
                if object_role in ['accessory']:
                    if object_id not in object_dict:
                        object_dict[object_id] = 1
                    else:
                        object_dict[object_id] += 1
        # 配饰替换
        replace_list = propose_one['target_furniture']
        replace_size = propose_one['target_furniture_size']
        for replace_idx, replace_dict in enumerate(replace_list):
            group_new = copy_group(group_one)
            object_list, object_hide = group_new['obj_list'], group_new['obj_hide']
            object_dump, object_show = [], False
            # 更新物品
            plat_one, plat_pos, plat_ang, cloth_range, cloth_above = {}, [], 0, [], plat_size[1] + 0.2
            for object_todo in [object_list, object_hide]:
                for object_idx, object_one in enumerate(object_todo):
                    object_id = object_one['id']
                    if object_id == plat_id:
                        plat_one = object_one
                        plat_pos = plat_one['position']
                        plat_ang = rot_to_ang(plat_one['rotation'])
                        continue
                    cate_old = get_furniture_cate(object_id)
                    size_old = [abs(object_one['size'][i] * object_one['scale'][i]) for i in range(3)]
                    # 盖毯检查
                    if group_type in ['Meeting', 'Rest'] and 'cloth' in object_one['type']:
                        if replace_idx == 1:
                            pass
                        else:
                            object_dump.append(object_one)
                            continue
                    # 抱枕检查
                    elif group_type in ['Meeting', 'Rest'] and 'pillow' in object_one['type']:
                        if object_id in replace_dict:
                            replace_id = replace_dict[object_id]
                        else:
                            replace_id = object_id
                        if get_furniture_cate(replace_id) not in ['抱枕']:
                            object_new = compute_deco_raise(random_idx + object_idx, '抱枕')
                            replace_id = object_new['id']
                            replace_dict[object_id] = replace_id
                            replace_size[replace_id] = object_new['size'][:]
                    # 电视检查
                    elif group_type in ['Media'] and 'electronics/TV - on top of others' in object_one['type']:
                        if replace_idx == 1:
                            object_dump.append(object_one)
                            object_show = True
                            continue
                    # 桌布检查
                    elif group_type in ['Dining'] and size_old[1] < UNIT_HEIGHT_CLOTH_MAX * 100:
                        if group_idx == 0 and replace_idx in [1, 2]:
                            pass
                        else:
                            object_dump.append(object_one)
                            continue
                        if size_old[0] < 100:
                            object_dump.append(object_one)
                            continue
                    # 推荐检查
                    if object_id not in replace_dict:
                        if group_type in ['Dining'] and size_old[1] < UNIT_HEIGHT_CLOTH_MAX * 100:
                            if replace_idx < len(replace_list) - 1:
                                object_dump.append(object_one)
                        elif group_type in ['Meeting'] and ('cloth' in object_one['role'] or 'cloth' in object_one['type']):
                            if replace_idx < len(replace_list) - 1:
                                object_dump.append(object_one)
                        continue
                    replace_id = replace_dict[object_id]
                    if replace_id not in replace_size:
                        continue
                    size_new = replace_size[replace_id]
                    if min(size_new[0], size_new[1], size_new[2]) <= 0.000001:
                        size_new = object_one['size'][:]
                    if get_furniture_cate(replace_id) in ['鞋子']:
                        if group_type in ['Media', 'Work', 'Rest']:
                            continue
                        elif plat_size[1] > UNIT_HEIGHT_SHELF_MIN:
                            continue
                    # 尺寸检查
                    if group_type in ['Dining'] and size_old[1] < UNIT_HEIGHT_CLOTH_MAX * 100:
                        if size_new[1] > 10:
                            object_dump.append(object_one)
                            continue
                    # 缩放检查
                    size_max = size_old[:]
                    if 'size_max' in object_one:
                        size_max = object_one['size_max'][:]
                    scale_max = min(size_max[0] / size_new[0], size_max[1] / size_new[1], size_max[2] / size_new[2])
                    scale_new = [size_old[0] / size_new[0], size_old[1] / size_new[1], size_old[2] / size_new[2]]
                    # 布艺
                    cloth_fix = False
                    if 'type' in object_one and 'cloth' in object_one['type']:
                        cloth_fix = True
                    elif 'role' in object_one and 'cloth' in object_one['role']:
                        cloth_fix = True
                    # 盖毯
                    if group_type in ['Meeting', 'Rest'] and cloth_fix:
                        scale_max = min(size_max[0] / size_new[0], 1, size_max[2] / size_new[2])
                        scale_new = [1, 1, 1]
                        # 范围
                        cloth_size = [abs(size_new[i] * scale_new[i]) / 100 for i in range(3)]
                        cloth_width = max(cloth_size[0], cloth_size[2]) + 0.2
                        cloth_shift = object_one['normal_position']
                        cloth_range = [cloth_shift[0] - cloth_width / 2, cloth_shift[2] - cloth_width / 2,
                                       cloth_shift[0] + cloth_width / 2, cloth_shift[2] + cloth_width / 2]
                        cloth_above = plat_pos[1] + cloth_shift[1] + cloth_size[1] + 0.1
                    # 抱枕
                    elif group_type in ['Meeting', 'Rest'] and 'pillow' in object_one['type']:
                        # 尺寸
                        type_new = 'accessory/simulated pillow'
                        object_one['type'] = type_new
                        # 缩放
                        scale_mid = min(size_old[0] / size_new[0], 1.0)
                        scale_new = [scale_mid, scale_mid, scale_mid]
                        # 俯仰
                        object_one['adjust_pitch'] = math.pi / 3
                        # 遮盖
                        object_shift = object_one['normal_position']
                        object_one['position'][1] = cloth_above
                        object_one['normal_position'][1] = cloth_above
                        object_one['relate_shifting'][1] = cloth_above
                        if len(cloth_range) >= 4:
                            if cloth_range[0] < object_shift[0] < cloth_range[2]:
                                if cloth_range[1] < object_shift[2] < cloth_range[3]:
                                    pass
                    # 电视
                    elif group_type in ['Media'] and 'electronics/TV - on top of others' in object_one['type']:
                        scale_max = size_max[0] / size_new[0]
                        scale_new = [min(scale_max, 1.2), min(scale_max, 1.2), min(size_old[2] / size_new[2], 1.0)]
                    # 桌布
                    elif group_type in ['Dining'] and size_old[1] < UNIT_HEIGHT_CLOTH_MAX * 100:
                        if size_new[0] < size_new[2]:
                            scale_new = [size_old[2] / size_new[0], size_old[1] / size_new[1], size_old[0] / size_new[2]]
                            # 使用角度
                            if 'rotation' in object_one:
                                angle_rot = object_one['rotation']
                                angle_new = rot_to_ang(angle_rot) + math.pi / 2
                                object_one['rotation'] = [0, math.sin(angle_new / 2), 0, math.cos(angle_new / 2)]
                            # 标准角度
                            if 'normal_rotation' in object_one:
                                angle_rot = object_one['normal_rotation']
                                angle_new = rot_to_ang(angle_rot) + math.pi / 2
                                object_one['normal_rotation'] = [0, math.sin(angle_new / 2), 0, math.cos(angle_new / 2)]
                        if get_furniture_cate(replace_id) in ['桌旗'] or min(size_new[0], size_new[2]) < 50:
                            if size_new[0] < size_new[2]:
                                scale_new[0] = 1
                                scale_new[2] = (size_old[0] + 20) / size_new[2]
                            else:
                                scale_new[0] = (size_old[0] + 20) / size_new[0]
                                scale_new[2] = 1
                        scale_new[1] = min(abs(size_old[1] / size_new[1]), 1.5)
                    # 餐具
                    elif group_type in ['Dining']:
                        scale_mid = min(scale_max, 1.0)
                        scale_new = [scale_mid, scale_mid, scale_mid]
                        if scale_mid < 0.50:
                            continue
                    # 挂饰
                    elif '挂饰' in cate_old:
                        scale_mid = min(size_max[0] / size_new[0], 1.0)
                        scale_new = [scale_mid, scale_mid, scale_mid]
                    # 其他
                    else:
                        scale_mid = min(scale_max, 1.0)
                        if scale_mid < 0.70:
                            if '化妆品' in cate_old or '洗浴品' in cate_old:
                                object_dump.append(object_one)
                                continue
                            elif '洗浴品' in cate_old or '洗浴品' in cate_old:
                                object_dump.append(object_one)
                                continue
                            elif 'pillow' in object_one['type']:
                                pass
                            else:
                                compute_deco_small(object_one, replace_idx)
                                replace_id = object_one['id']
                                size_new = object_one['size'][:]
                                scale_max = min(size_max[0] / size_new[0], size_max[1] / size_new[1],
                                                size_max[2] / size_new[2])
                                scale_mid = min(scale_max, 1.0)
                        scale_new = [scale_mid, scale_mid, scale_mid]
                    if replace_id in UNIT_SCALE_LOWER and max(scale_new[0], scale_new[1], scale_new[2]) > 0.8:
                        scale_new = [0.8, 0.8, 0.8]
                    if replace_id in UNIT_SCALE_UPPER and max(scale_new[0], scale_new[1], scale_new[2]) < 1.2:
                        scale_new = [1.2, 1.2, 1.2]
                    object_one['id'] = replace_id
                    object_one['size'] = size_new
                    object_one['scale'] = scale_new
                    # 位置检查
                    if '挂饰' in cate_old and len(plat_pos) > 0:
                        size_now = [abs(size_new[i] * scale_new[i]) for i in range(3)]
                        height_new, depth_new = size_now[1], size_now[2]
                        height_old, depth_old = size_old[1], size_old[2]
                        move_y, move_z = (height_old - height_new) / 100, (depth_new - depth_old) / 100
                        shift_old = object_one['relate_shifting']
                        tmp_x, tmp_y, tmp_z = shift_old[0], shift_old[1] + move_y, shift_old[2] + move_z
                        add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
                        add_y = tmp_y
                        add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
                        object_pos = [plat_pos[0] + add_x, plat_pos[1] + add_y, plat_pos[2] + add_z]
                        if 'normal_position' in plat_one:
                            normal_pos = plat_one['normal_position'][:]
                        else:
                            plat_one['normal_position'] = [0, 0, 0]
                            plat_one['normal_rotation'] = [0, 0, 0, 1]
                            if 'position' in plat_one:
                                plat_one['normal_position'][1] = plat_one['position'][1]
                            normal_pos = plat_one['normal_position'][:]
                        object_one['position'] = object_pos
                        object_one['normal_position'] = [normal_pos[0] + tmp_x, normal_pos[1] + tmp_y,
                                                         normal_pos[2] + tmp_z]
                        object_one['relate_shifting'] = [tmp_x, tmp_y, tmp_z]
                    elif 'size_dir' in object_one:
                        size_now = [abs(size_new[i] * scale_new[i]) for i in range(3)]
                        width_new, depth_new = size_now[0], size_now[2]
                        width_old, depth_old = size_old[0], size_old[2]
                        angle_one = 0
                        if 'normal_rotation' in object_one:
                            angle_one = rot_to_ang(object_one['normal_rotation'])
                        if abs(angle_one - math.pi / 2) < 0.1 or abs(angle_one + math.pi / 2) < 0.1:
                            width_new, depth_new = size_now[2], size_now[0]
                            width_old, depth_old = size_old[2], size_old[0]
                        size_dir, move_x, move_z = object_one['size_dir'], 0, 0
                        if width_new - width_old > 2 and size_dir[0] in [-1, 1]:
                            move_x = -size_dir[0] * (width_new - width_old) / 200
                        if depth_new - depth_old > 2 and size_dir[2] in [-1, 1]:
                            move_z = -size_dir[2] * (depth_new - depth_old) / 200
                        if (abs(move_x) > 0.01 or abs(move_z) > 0.01) and len(plat_one) > 0 and 'relate_shifting' in object_one:
                            plat_pos, plat_ang = plat_one['position'], rot_to_ang(plat_one['rotation'])
                            shift_old = object_one['relate_shifting']
                            tmp_x, tmp_y, tmp_z = shift_old[0] + move_x, shift_old[1], shift_old[2] + move_z
                            add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
                            add_y = tmp_y
                            add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
                            object_pos = [plat_pos[0] + add_x, plat_pos[1] + add_y, plat_pos[2] + add_z]
                            if 'normal_position' in plat_one:
                                normal_pos = plat_one['normal_position'][:]
                            else:
                                plat_one['normal_position'] = [0, 0, 0]
                                plat_one['normal_rotation'] = [0, 0, 0, 1]
                                if 'position' in plat_one:
                                    plat_one['normal_position'][1] = plat_one['position'][1]
                                normal_pos = plat_one['normal_position'][:]
                            object_one['position'] = object_pos
                            object_one['normal_position'] = [normal_pos[0] + tmp_x, normal_pos[1] + tmp_y,
                                                             normal_pos[2] + tmp_z]
                            object_one['relate_shifting'] = [tmp_x, tmp_y, tmp_z]

                    # 角度检查
                    plant_flag = False
                    if 'plants' in object_one['type']:
                        plant_flag = True
                    if group_one['type'] in ['Dining'] and size_old[1] > UNIT_HEIGHT_CLOTH_MAX * 100:
                        if object_id in object_dict and object_dict[object_id] == 1:
                            plant_flag = True
                    if 'role' in plat_one and plat_one['role'] in ['side table'] and size_new[1] > 0.1:
                        if 'lamp' not in object_one['type']:
                            plant_flag = True
                    if plant_flag:
                        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                        angle_old = 0
                        if 'normal_rotation' in object_one:
                            angle_old = rot_to_ang(object_one['normal_rotation'])
                        angle_flag = False
                        if abs(ang_to_ang(angle_old + math.pi / 2)) < 0.1 or abs(ang_to_ang(angle_old - math.pi / 2)) < 0.1:
                            if object_size[0] > object_size[2] * 1.01 or object_size[0] > object_size[2] + 0.01:
                                angle_flag = True
                        else:
                            if object_size[2] > object_size[0] * 1.01 or object_size[2] > object_size[0] + 0.01:
                                angle_flag = True
                        if angle_flag:
                            # 使用角度
                            angle_new = rot_to_ang(object_one['rotation']) + math.pi / 2
                            object_one['rotation'] = [0, math.sin(angle_new / 2), 0, math.cos(angle_new / 2)]
                            # 标准角度
                            angle_new = rot_to_ang(object_one['normal_rotation']) + math.pi / 2
                            object_one['normal_rotation'] = [0, math.sin(angle_new / 2), 0, math.cos(angle_new / 2)]
            # 删除物品
            top_old, top_new, top_dlt, top_dump = 1000, 1100, 0, {}
            for object_one in object_dump:
                if 'cloth' in object_one['role'] or 'cloth' in object_one['type']:
                    if 'top_id' in object_one:
                        top_new = object_one['top_id']
                        top_dlt = abs(object_one['size'][1] * object_one['scale'][1]) / 100
                if 'top_id' in object_one and 'top_of' in object_one:
                    top_dump[object_one['top_id']] = object_one['top_of']
                if object_one in object_list:
                    object_list.remove(object_one)
                if object_one in object_hide:
                    object_hide.remove(object_one)
            if len(top_dump) > 0:
                for object_one in object_list:
                    if object_one['role'] in ['table'] and 'top_id' in object_one:
                        top_old = object_one['top_id']
                        continue
                    if 'top_of' in object_one and object_one['top_of'] in top_dump:
                        if object_one['top_of'] == top_new:
                            object_one['position'][1] -= top_dlt
                            object_one['normal_position'][1] -= top_dlt
                            object_one['origin_position'][1] -= top_dlt
                            if 'relate_shifting' in object_one:
                                object_one['relate_shifting'][1] -= top_dlt
                        top_sub = top_dump[object_one['top_of']]
                        if top_sub in top_dump:
                            top_sub = top_old
                        object_one['top_of'] = top_sub
            # 显示物品
            for object_one in object_hide:
                if not object_show:
                    break
                object_list.append(object_one)
            # 添加分组
            group_scheme.append(group_new)
    # 调整方案
    if len(group_scheme) <= 0:
        for group_idx, group_one in enumerate(group_sample):
            group_scheme.append(group_one)
    # 返回信息
    return group_scheme


# 组合场景查找 TODO:
def group_search(item_room, item_group, item_role, house_num=2, house_rand=True, content_type_list=[]):
    scene_list = []
    # 方案检索
    content_type_list = ['appliance/refrigerator']
    search_list = search_scene_list(item_room, item_group, item_role, house_num, seed=random_seed, content_type_list=content_type_list)
    for key_info in search_list:
        scene_key = key_info["sample_key"].split('_')[0]
        scene_url = key_info["scene_url"]
        scene_each = {'id': scene_key, 'url': scene_url, 'loc': '', 'layout': {}}
        scene_list.append(scene_each)
    # 返回信息
    return scene_list


# 组合场景过滤
def group_filter(group_list, group_mode=['object'], scene_item={}, scene_room=''):
    group_find = []
    for group_idx, group_one in enumerate(group_list):
        group_type = group_one['type']
        # 找物体
        if 'object' in group_mode:
            if len(scene_item) <= 0:
                continue
            item_key, item_val, item_room, item_group, item_role = '', {}, [], [], []
            if 'item' in scene_item:
                item_key = scene_item['item']
                item_val = get_furniture_role_by_item(item_key)
            if 'room' in item_val:
                item_room = item_val['room']
            if 'group' in item_val:
                item_group = item_val['group']
            if 'role' in item_val:
                item_role = item_val['role'][:]
                if group_type in ['Meeting'] and 'side sofa' in item_role and 'side table' in item_role:
                    item_role.remove('side table')
            if scene_room not in item_room:
                continue
            if group_type not in item_group:
                continue
            item_info = scene_item.copy()
            item_info['role'] = item_role
            item_info['around_role'] = []
            item_info['relate_role'] = []
            item_info['relate_category'] = {}
            if 'around_role' in item_val:
                item_info['around_role'] = item_val['around_role'].copy()
            if 'relate_role' in item_val:
                item_info['relate_role'] = item_val['relate_role'].copy()
            if 'relate_category' in item_val:
                item_info['relate_category'] = item_val['relate_category'].copy()
            group_one['item'] = item_info
            group_find.append(group_one)
        # 找硬装
        elif 'decorate' in group_mode:
            if group_type not in ['Meeting', 'Bed', 'Media', 'Dining', 'Work']:
                continue
            object_list, object_rely = group_one['obj_list'], ''
            if len(object_list) > 0 and 'relate' in object_list[0]:
                object_rely = object_list[0]['relate']
            # 渲染背景
            if object_rely not in ['wall']:
                continue
            group_find.append(group_one)
    # 返回信息
    return group_find


# 组合商品处理
def group_adjust(group_old, group_list=[], room_type='', room_height=UNIT_HEIGHT_WALL):
    # 组合生成
    group_new = generate_group(group_old, group_list)
    item_one, target_one, target_err = {}, {}, False
    if 'item' in group_new:
        item_one = group_new['item']
    if 'target' in group_new and len(group_new['target']) > 0:
        target_one = group_new['target'][0]
    if len(item_one) > 0 and len(target_one) <= 0:
        group_new = group_rect_raise(group_old, item_one, layout_num=1, room_type=room_type)
        if 'target' in group_new and len(group_new['target']) > 0:
            target_one = group_new['target'][0]
    # 机位调整
    if len(item_one) > 0 and len(target_one) > 0:
        # 原有
        pos_old, tar_old = item_one['camera_position'], item_one['camera_target']
        # 目标
        obj_pos, obj_ang = target_one['position'], rot_to_ang(group_new['rotation'])
        # obj_pos, obj_ang = target_one['position'], rot_to_ang(use_rot)
        if target_one['role'] in ['side sofa', 'chair']:
            obj_norm = target_one['normal_position']
            grp_side, cur_size, min_size = group_old['neighbor_more'], group_old['size'], group_old['size_min']
            obj_rest = cur_size[2] + grp_side[2] - (min_size[2] / 2 + obj_norm[2])
            obj_turn = math.pi / 4
            if obj_rest > pos_old[2] - tar_old[2]:
                pass
            elif obj_norm[0] <= 0 - 0.2:
                if obj_norm[2] > 1.5 and abs(obj_norm[0]) > 1:
                    obj_ang = rot_to_ang(group_new['rotation']) + math.pi / 2
                else:
                    obj_ang = rot_to_ang(group_new['rotation']) - obj_turn
                    if grp_side[1] < min(grp_side[3], 1.0):
                        target_err = True
            elif obj_norm[0] >= 0 + 0.2:
                if obj_norm[2] > 1.5 and abs(obj_norm[0]) > 1:
                    obj_ang = rot_to_ang(group_new['rotation']) - math.pi / 2
                else:
                    obj_ang = rot_to_ang(group_new['rotation']) + obj_turn
                    if grp_side[3] < min(grp_side[1], 1.0):
                        target_err = True
        # 计算
        pos_new, tar_new = pos_old[:], tar_old[:]
        tar_new = [obj_pos[0] + tar_old[0], obj_pos[1] + tar_old[1], obj_pos[2] + tar_old[2]]
        tmp_x, tmp_y, tmp_z = pos_old[0] - tar_old[0], pos_old[1] - tar_old[1], pos_old[2] - tar_old[2]
        add_x = tmp_z * math.sin(obj_ang) + tmp_x * math.cos(obj_ang)
        add_y = tmp_y
        add_z = tmp_z * math.cos(obj_ang) - tmp_x * math.sin(obj_ang)
        pos_new = [tar_new[0] + add_x, tar_new[1] + add_y, tar_new[2] + add_z]
        # 更新
        target_one['item'] = item_one
        target_one['camera'] = {
            "aspect": 1.0, "fov": 60, "near": 0.1, "far": 1000, "up": [0, 1, 0],
            "pos": pos_new[:], "target": tar_new[:]
        }
    # 替换信息
    target_list = []
    relate_list = []
    remove_list = group_old['obj_list'][:]
    append_list = group_new['obj_list'][:]
    if len(target_one) > 0 and not target_err:
        target_list.append(target_one)
        obj_key, obj_pos = target_one['id'], target_one['position']
        for obj_one in append_list:
            relate_key, relate_pos = '', []
            if 'relate' in obj_one and 'relate_position' in obj_one:
                relate_key, relate_pos = obj_one['relate'], obj_one['relate_position']
            if relate_key == obj_key:
                if len(relate_pos) >= 3:
                    if abs(relate_pos[0] - obj_pos[0]) + abs(relate_pos[2] - obj_pos[2]) < 0.1:
                        relate_list.append(obj_one)
    for old_idx in range(len(remove_list) - 1, -1, -1):
        old_obj = remove_list[old_idx]
        old_key, old_pos = old_obj['id'], old_obj['position']
        old_find, new_find = True, False
        for new_idx in range(len(append_list) - 1, -1, -1):
            new_obj = append_list[new_idx]
            new_key, new_pos = new_obj['id'], new_obj['position']
            if old_key == new_key and abs(old_pos[0] - new_pos[0]) + abs(old_pos[2] - new_pos[2]) <= 0.1:
                new_find = True
                append_list.pop(new_idx)
                break
        if new_find:
            remove_list.pop(old_idx)
    operate_info = {
        'target': target_list,
        'relate': relate_list,
        'remove': remove_list,
        'append': append_list,
        'adjust': []
    }
    return group_new, operate_info


# 组合机位生成
def group_camera(group_one, group_item={}, group_view=''):
    group_type, group_size = group_one['type'], group_one['size']
    group_width, group_depth = max(group_size[0], 2), group_size[2]
    group_pos, group_rot = group_one['position'], group_one['rotation']
    group_ang = rot_to_ang(group_rot)
    # 相机位置 x z 平面坐标 y 竖直坐标
    tmp_x = 0
    tmp_z = group_width * math.sin(math.pi / 3) - group_depth / 2
    add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
    add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
    # object
    if len(group_item) > 0:
        camera_pos = [group_pos[0] + add_x, 1.2, group_pos[2] + add_z]  # x,y,z
        camera_tar = [group_pos[0] + 0, 1.2, group_pos[2] + 0]
        camera_new = {
            'aspect': 1.0, 'fov': 60, 'near': 0.1, 'far': 1000,
            'up': [0, 1, 0],
            'pos': camera_pos,
            'target': camera_tar
        }
    # wall
    elif group_view in ['', 'wall']:
        camera_pos = [group_pos[0] + add_x, 1.2, group_pos[2] + add_z]  # x,y,z
        camera_tar = [group_pos[0] + 0, 1.2, group_pos[2] + 0]
        camera_new = {
            'aspect': 1.0, 'fov': 60, 'near': 0.1, 'far': 1000,
            'up': [0, 1, 0],
            'pos': camera_pos,
            'target': camera_tar
        }
    # floor
    elif group_view in ['floor']:
        camera_pos = [group_pos[0] + 0, 1.2, group_pos[2] + 0]
        camera_tar = [group_pos[0] + 0, 0.0, group_pos[2] + 0]
        camera_new = {
            'aspect': 1.0, 'fov': 60, 'near': 0.1, 'far': 1000,
            'up': [0, 1, 0],
            'pos': camera_pos,
            'target': camera_tar
        }
    # other
    else:
        camera_pos = [group_pos[0] + add_x, 1.2, group_pos[2] + add_z]
        camera_tar = [group_pos[0] + 0, 1.2, group_pos[2] + 0]
        camera_new = {
            'aspect': 1.0, 'fov': 60, 'near': 0.1, 'far': 1000,
            'up': [0, 1, 0],
            'pos': camera_pos,
            'target': camera_tar
        }
    return camera_new


# 推荐服务输入
def accessory_scope(group_one, plat_id=''):
    # 物品信息
    object_list, object_hide, object_dict, target_scope = [], [], {}, []
    if 'obj_list' in group_one:
        object_list = group_one['obj_list']
    if 'obj_hide' in group_one:
        object_hide = group_one['obj_hide']
    object_todo = []
    for object_one in object_list:
        object_id = object_one['id']
        if object_id not in object_dict:
            object_dict[object_id] = 1
            object_todo.append(object_one)
        else:
            object_dict[object_id] += 1
    for object_one in object_hide:
        object_id = object_one['id']
        if object_id not in object_dict:
            object_dict[object_id] = 1
            object_todo.append(object_one)
        else:
            object_dict[object_id] += 1
    # 组合信息
    group_type = ''
    if 'type' in group_one:
        group_type = group_one['type']
    # 物品推荐
    plat_role, plat_cate = '', ''
    unique_work_1 = ['水杯', '水壶', '花卉', '电脑', '相框', '书籍', '书籍组合1', '书籍组合2', '书籍组合3', '杂志']
    unique_work_2 = ['水杯', '水壶', '工艺品', '相框', '书籍', '雕塑', '香薰']
    unique_game_1 = ['电脑', '娱乐', '书籍组合3']
    random.shuffle(unique_work_1)
    random.shuffle(unique_work_2)
    random.shuffle(unique_game_1)
    for object_idx, object_one in enumerate(object_todo):
        # 平台判断
        object_id = object_one['id']
        if object_id == plat_id:
            plat_role = object_one['role']
            type_id, style_id, cate_id = get_furniture_data_refer_id(plat_id)
            plat_cate = get_furniture_category_by_id(cate_id)
            continue
        object_role, object_type = object_one['role'], object_one['type']
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]

        object_shift = object_one['relate_shifting']
        # 推荐尺寸
        size_cur = [object_size[i] * 100 * 1.0 for i in range(3)]
        size_min = [object_size[i] * 100 * 0.8 for i in range(3)]
        size_max = [object_size[i] * 100 * 1.5 for i in range(3)]
        type_id, style_id, cate_id = get_furniture_data_refer_id(object_id)
        if 'size_max' in object_one:
            size_max = object_one['size_max'][:]
        # 推荐品类
        object_cate_old = get_furniture_cate(object_id)
        object_cate_new = ''
        if group_type in ['Meeting', 'Rest'] and object_role in ['cloth']:
            if 'cloth' in object_role or 'cloth' in object_type:
                object_cate_new = '盖毯'
        elif group_type in ['Dining'] and object_role in ['accessory', 'cloth']:
            if 'cloth' in object_role or 'cloth' in object_type:
                size_cur[1], size_min[1], size_max[1] = 1, 0.1, 2
                object_cate_new = '桌布'
            elif object_id in object_dict and object_dict[object_id] >= 4 and size_cur[1] > 5:
                specify_cate, specify_cate_id = get_furniture_category_by_key('dining accessory')
                if not specify_cate_id == '':
                    cate_id = specify_cate_id
                object_cate_new = '餐具组合'
            elif object_id in object_dict and object_dict[object_id] >= 4 and size_cur[1] < 2:
                size_cur[1], size_min[1], size_max[1] = 1, 0.1, 2
                object_cate_new = '餐巾'
            elif object_id in object_dict and object_dict[object_id] <= 1 and size_cur[1] > 5:
                specify_cate, specify_cate_id = get_furniture_category_by_key('dining plants')
                if not specify_cate_id == '':
                    cate_id = specify_cate_id
                object_cate_new = '花卉'
        elif group_type in ['Meeting', 'Bed'] and 'lamp' in object_type:
            object_cate_new = '台灯'
        elif group_type in ['Meeting', 'Bed'] and 'plants' in object_type:
            object_cate_new = '花卉'
        elif '书桌' in plat_cate or '书柜' in plat_cate:
            if object_cate_old in unique_work_1:
                pass
            else:
                object_cate_new = unique_work_2[object_idx % len(unique_work_2)]
        elif '鞋柜' in plat_cate:
            if 'lamp' in object_type:
                object_cate_new = '台灯'
            elif 'plants' in object_type:
                object_cate_new = '花卉'
            elif object_cate_old in ['鞋子', '花卉']:
                pass
            else:
                object_cate_new = unique_work_2[object_idx % len(unique_work_2)]
        elif object_cate_old in ['娱乐']:
            object_cate_new = unique_game_1[0]
        else:
            object_cate_new = object_cate_old
        if FURNITURE_PROPOSE_APP_ID in [20724, 21349]:
            cate_id = accessory_category(object_id, object_type, object_cate_new, object_size, object_shift)
        target_one = {
            'id': object_id, 'type': object_one['type'], 'role': object_one['role'],
            'size_min': size_min, 'size_max': size_max, 'size_cur': size_cur,
            'cate_id': cate_id, 'group': group_type
        }
        target_scope.append(target_one)
    return target_scope


# 推荐服务类目
def accessory_category(object_id, object_type, object_cate='', object_size=[], object_shift=[]):
    cate_new = object_cate
    global ACCESSORY_PROPOSE_CATE
    unique_more_1 = ['花卉', '工艺品']
    unique_more_2 = ['水杯', '水壶', '相框', '香薰']
    random.shuffle(unique_more_1)
    random.shuffle(unique_more_2)
    if cate_new not in ACCESSORY_PROPOSE_CATE:
        cate_old = get_furniture_cate(object_id)
        cate_new = ''
        if cate_old in ['水杯', '水壶', '餐具', '餐具组合', '桌布', '酒具', '酒具组合1', '酒具组合2', '茶具', '茶具组合',
                        '花卉', '绿植', '工艺品', '烛台', '相框',
                        '电脑', '书籍', '书籍组合1', '书籍组合2', '书籍组合3', '杂志',
                        '化妆品', '化妆品组合1', '化妆品组合2', '化妆品组合3', '牙刷', '洗浴品', '洗浴品组合1', '洗浴品组合2',
                        '抱枕', '盖毯', '毛巾', '鞋子']:
            cate_new = cate_old
    if cate_new == '':
        if 'pillow' in object_type:
            cate_new = '抱枕'
        elif 'cloth' in object_type:
            cate_new = '桌布'
        elif 'plants' in object_type:
            cate_new = '绿植'
        elif 'lamp' in object_type:
            cate_new = '台灯'
        elif len(object_size) >= 3 and max(object_size[0], object_size[1], object_size[2]) > 0.30:
            cate_new = unique_more_1[0]
        else:
            cate_new = unique_more_2[0]
    if cate_new in ACCESSORY_PROPOSE_CATE:
        cate_id = ACCESSORY_PROPOSE_CATE[cate_new]
    else:
        cate_id = ACCESSORY_PROPOSE_CATE['工艺品']
    return cate_id


# 推荐服务调用
def propose_accessory(propose_info, scheme_num=3, plat_id='', request_loc=False, request_log=False):
    if len(propose_info) <= 0:
        return
    # 本地推荐
    if request_loc:
        for propose_one in propose_info:
            generate_furniture_propose(propose_one, scheme_num)
        return
    # 推荐服务
    server_url = propose_accessory_url()
    # 启动信息
    target_seed, target_style = [], []
    if len(propose_info) > 0:
        propose_one = propose_info[0]
        if 'target_seed' in propose_one and len(propose_one['target_seed']) > 0:
            for seed_one in propose_one['target_seed']:
                seed_id = seed_one['id']
                # 窗户种子
                if 'window' in seed_one['type'] and len(FURNITURE_PROPOSE_WINDOW) > 0:
                    seed_id = FURNITURE_PROPOSE_WINDOW[random.randint(0, 100) % len(FURNITURE_PROPOSE_WINDOW)]
                target_seed.append(seed_id)
        if 'target_style' in propose_one:
            target_style = propose_one['target_style']
    seed_id = ''
    if len(target_seed) > 0:
        seed_id = target_seed[0]
    # 遍历方案
    for propose_idx, propose_one in enumerate(propose_info):
        if 'target_furniture' not in propose_one:
            propose_one['target_furniture'] = []
        if 'target_furniture_size' not in propose_one:
            propose_one['target_furniture_size'] = {}
        if 'target_furniture_log' not in propose_one:
            propose_one['target_furniture_log'] = {}
        if len(propose_one['target_scope']) <= 0:
            continue
        # 范围参数
        scope_list, scope_dict, decor_dict = propose_one['target_scope'], {}, {}
        for object_one in scope_list:
            object_id, object_role, object_type = object_one['id'], object_one['role'], object_one['type']
            if object_role in ['accessory'] and 'pillow' not in object_type:
                decor_dict[object_id] = 1
            scope_dict[object_id] = object_one
        # 选品参数
        object_list = []
        for object_one in propose_one['target_scope']:
            object_new = {
                'model_id': object_one['id'],
                'xMin': round(object_one['size_min'][0], 1),
                'zMin': round(object_one['size_min'][1], 1),
                'yMin': round(object_one['size_min'][2], 1),
                'xMax': round(object_one['size_max'][0], 1),
                'zMax': round(object_one['size_max'][1], 1),
                'yMax': round(object_one['size_max'][2], 1),
                'xPerfect': round(object_one['size_cur'][0], 1),
                'zPerfect': round(object_one['size_cur'][1], 1),
                'yPerfect': round(object_one['size_cur'][2], 1),
                'cateLayout': object_one['type'],
                'cate_id': object_one['cate_id']
            }
            object_list.append(object_new)
        if len(object_list) <= 0:
            # 错误日志
            layout_log_0 = 'propose empty ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
            print(layout_log_0)
            print(e)
            continue
        # 房间参数
        room_id, room_type, room_area = propose_one['id'], propose_one['type'], propose_one['area']
        room_attr = {
            'isCurrent': 'true',
            'modelIds': target_seed,
            'roomId': '1',
            'roomType': room_type,
            'area': room_area,
            'styleIds': target_style
        }
        # 请求参数 分批请求
        propose_list = []
        request_limit = 7
        request_count = math.ceil((len(object_list) - 0) / request_limit)
        if request_count <= 0:
            object_once = [object_list[0]]
            if len(object_once) > 0:
                propose_once = {
                    'isAIDesign': 'true',
                    'input_model_id': seed_id,
                    'roomsAttribute': [],
                    'needSizeRuleAbsolutely': 'true',
                    'SlotRuleAIDesgin': object_once
                }
                propose_once['roomsAttribute'].append(room_attr)
                propose_list.append(propose_once)
        else:
            for request_index in range(request_count):
                object_once = []
                for i in range(request_limit):
                    object_idx = 0 + request_index * request_limit + i
                    if object_idx >= len(object_list):
                        break
                    object_once.append(object_list[object_idx])
                if len(object_once) > 0:
                    propose_once = {
                        'isAIDesign': 'true',
                        'input_model_id': seed_id,
                        'roomsAttribute': [],
                        'needSizeRuleAbsolutely': 'true',
                        'SlotRuleAIDesgin': object_once
                    }
                    propose_once['roomsAttribute'].append(room_attr)
                    propose_list.append(propose_once)
        # 调用服务
        try:
            target_furniture = propose_one['target_furniture']
            target_furniture_size = propose_one['target_furniture_size']
            target_furniture_log = propose_one['target_furniture_log']
            for scheme_idx in range(scheme_num):
                target_furniture.append({})
            process_sync, process_list, process_queue = True, [], multiprocessing.Queue()
            response_todo = []
            # 顺序执行
            if process_sync or len(propose_list) <= 2:
                for request_idx, propose_data in enumerate(propose_list):
                    request_data = {
                        'appid': FURNITURE_PROPOSE_APP_ID,
                        'userId': FURNITURE_PROPOSE_USR_ID,
                        'DEBUG': 'true',
                        'input_json': json.dumps(propose_data)
                    }
                    # 初次调用
                    response_info = requests.post(server_url, data=request_data)
                    response_data = response_info.json()
                    response_dict = {}
                    # 打印信息
                    layout_log_0 = 'propose %d %d 0: %02d ' % (propose_idx, request_idx, len(object_list)) + \
                                   datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                    print(layout_log_0)
                    # 解析信息
                    if 'result' in response_data and len(response_data['result']) > 0:
                        if 'return_map' in response_data['result'][0]:
                            response_map = response_data['result'][0]['return_map']
                            response_dict = response_tran_dict(response_map)
                            if len(response_dict) > 0:
                                response_good = True
                        elif 'returnCollectionList' in response_data['result'][0]:
                            response_list = response_data['result'][0]['returnCollectionList']
                            response_dict = response_tran_list(response_list)
                    if len(response_dict) <= 0:
                        # 记录日志
                        request_file = '%s_request_fail_%d_%d.json' % (plat_id, propose_idx, request_idx)
                        request_path = os.path.join(DATA_DIR_SERVER_SERVICE, request_file)
                        with open(request_path, "w") as f:
                            json.dump(propose_data, f, indent=4)
                            f.close()
                        response_file = '%s_response_fail_%d_%d.json' % (plat_id, propose_idx, request_idx)
                        response_path = os.path.join(DATA_DIR_SERVER_SERVICE, response_file)
                        with open(response_path, "w") as f:
                            json.dump(response_data, f, indent=4)
                            f.close()
                        # 再次调用
                        response_info = requests.post(server_url, data=request_data)
                        response_data = response_info.json()
                        # 打印信息
                        layout_log_0 = 'propose %d %d 0: %02d ' % (propose_idx, request_idx, len(object_list)) + \
                                       datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                        print(layout_log_0)
                        # 解析信息
                        if 'result' in response_data and len(response_data['result']) > 0:
                            if 'return_map' in response_data['result'][0]:
                                response_map = response_data['result'][0]['return_map']
                                response_dict = response_tran_dict(response_map)
                            elif 'returnCollectionList' in response_data['result'][0]:
                                response_list = response_data['result'][0]['returnCollectionList']
                                response_dict = response_tran_list(response_list)
                    if len(response_dict) > 0:
                        response_todo.append(response_dict)
                        # 记录日志
                        if request_log:
                            request_file = '%s_request_good_%d_%d.json' % (plat_id, propose_idx, request_idx)
                            request_path = os.path.join(DATA_DIR_SERVER_SERVICE, request_file)
                            with open(request_path, "w") as f:
                                json.dump(propose_data, f, indent=4)
                                f.close()
                            response_file = '%s_response_good_%d_%d.json' % (plat_id, propose_idx, request_idx)
                            response_path = os.path.join(DATA_DIR_SERVER_SERVICE, response_file)
                            with open(response_path, "w") as f:
                                json.dump(response_data, f, indent=4)
                                f.close()
            # 并发执行
            else:
                for request_idx, propose_data in enumerate(propose_list):
                    process_one = AsyncPropose(propose_data, process_queue)
                    process_list.append(process_one)
                    process_one.start()
                if process_queue:
                    process_done = [process_queue.get() for process_one in process_list]
                    for response_dict in process_done:
                        response_todo.append(response_dict)
            # 解析结果
            replace_used = {}
            for response_dict in response_todo:
                for source_id, target_list in response_dict.items():
                    target_cnt, target_log = 0, []
                    for target_idx, target_one in enumerate(target_list):
                        if 'id' not in target_one:
                            continue
                        target_id = target_one['id']
                        # 尺寸判断
                        if 'size' not in target_one:
                            target_log.append({'id': target_id, 'log': 'size_err'})
                            continue
                        target_size = target_one['size']
                        if len(target_size) < 3:
                            target_log.append({'id': target_id, 'log': 'size_err'})
                            continue
                        if target_id in FURNITURE_PROPOSE_ERROR:
                            target_log.append({'id': target_id, 'log': 'base_err'})
                            continue
                        if source_id in scope_dict:
                            scope_one = scope_dict[source_id]
                            object_role, object_type = scope_one['role'], scope_one['type']
                            object_min = scope_one['size_min']
                            object_max = scope_one['size_max']
                            if object_role in ['sofa', 'armoire', 'cabinet']:
                                if target_size[0] <= object_min[0] * 0.8:
                                    target_log.append({'id': target_id, 'log': 'size_min'})
                                    continue
                                elif target_size[2] >= object_max[2] * 1.2:
                                    target_log.append({'id': target_id, 'log': 'size_max'})
                                    continue
                            elif object_role in ['table'] and 'round' in object_type:
                                if target_size[2] >= object_max[2] * 1.2:
                                    target_log.append({'id': target_id, 'log': 'size_max'})
                                    continue
                            elif object_role in ['toilet']:
                                if target_size[0] >= object_max[0] * 2 or target_size[2] >= object_max[2] * 2:
                                    target_log.append({'id': target_id, 'log': 'size_max'})
                                    continue
                            elif 'cloth' in object_type or 'cloth' in object_role:
                                pass
                            elif 'pillow' in object_type or 'pillow' in object_role:
                                pass
                            elif object_role in ['accessory']:
                                if target_size[0] >= object_max[0] * 2:
                                    target_log.append({'id': target_id, 'log': 'size_max'})
                                    continue

                        # 重复判断
                        if source_id in decor_dict and source_id in scope_dict:
                            scope_one = scope_dict[source_id]
                            object_type = scope_one['type']
                            if 'pillow' in object_type:
                                pass
                            elif target_id in replace_used:
                                target_log.append({'id': target_id, 'log': 'same_err'})
                                continue
                            replace_used[target_id] = 1

                        # 数据记录
                        target_id, target_size = target_one['id'], target_one['size']
                        target_furniture_size[target_id] = target_size[:]
                        if 0 <= target_cnt < len(target_furniture):
                            target_furniture[target_cnt][source_id] = target_id
                        # 钢琴处理
                        if source_id in FURNITURE_PROPOSE_PIANO and target_cnt == 0:
                            target_furniture[target_cnt][source_id] = source_id
                            target_log.append({'id': target_id, 'log': 'type_err'})
                        else:
                            target_log.append({'id': target_id, 'log': 'ok'})

                        # 数量判断
                        target_cnt += 1
                        if target_cnt >= scheme_num:
                            break
                    target_furniture_log[source_id] = target_log
        except Exception as e:
            # 错误日志
            layout_log_0 = 'propose failure ' + datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
            print(layout_log_0)
            print(e)
            continue
    # 纠正推荐
    random_idx = random.randint(0, 100)
    for propose_idx, propose_one in enumerate(propose_info):
        random_idx = random_idx + propose_idx * scheme_num
        target_seed, target_scope, target_furniture, target_furniture_size, target_furniture_log = [], [], [], {}, {}
        if 'target_seed' in propose_one:
            target_seed = propose_one['target_seed']
        if 'target_scope' in propose_one:
            target_scope = propose_one['target_scope']
        if 'target_furniture' in propose_one:
            target_furniture = propose_one['target_furniture']
        if 'target_furniture_size' in propose_one:
            target_furniture_size = propose_one['target_furniture_size']
        if 'target_furniture_log' in propose_one:
            target_furniture_log = propose_one['target_furniture_log']
        # 平台信息
        plat_info, plat_type, plat_cate = {}, '', ''
        if len(target_seed) > 0:
            plat_info, plat_type, plat_cate = target_seed[0], '', ''
            if 'type' in plat_info:
                plat_type = plat_info['type']
            type_id, style_id, category_id = get_furniture_data_refer_id(plat_info['id'], '', False)
            if not category_id == '':
                plat_cate = get_furniture_category_by_id(category_id)
                plat_cate = plat_cate.split('/')[0]
        # 类目信息
        target_list, target_dict, target_used = [], {}, []
        for object_idx, object_one in enumerate(target_scope):
            object_id = object_one['id']
            object_type, object_role, object_cate = object_one['type'], object_one['role'], object_one['cate_id']
            object_cate = get_furniture_cate(object_id)
            if object_id in target_dict:
                continue
            # 沙发
            if 'group' in object_one and object_one['group'] in ['Meeting', 'Rest'] and 'sofa' in plat_type:
                if 'cloth' in object_role or 'cloth' in object_type or object_cate in ['盖毯']:
                    # target_list.append(object_one)
                    target_dict[object_id] = '盖毯'
                    pass
                elif 'pillow' in object_type or object_cate in ['抱枕']:
                    # target_list.append(object_one)
                    target_dict[object_id] = '抱枕'
                    pass
            # 茶几
            elif 'group' in object_one and object_one['group'] in ['Meeting', 'Bed', 'Rest'] and 'table' in plat_type:
                if 'lamp' in object_type:
                    pass
                elif 'plants' in object_type:
                    pass
                elif object_cate in ['水杯', '水壶', '茶具组合', '酒具', '酒具组合1', '酒具组合2',
                                     '花卉', '绿植', '工艺品', '烛台', '相框', '台灯', '烛台', '雕塑', '香薰', '杂志']:
                    pass
                elif object_cate in ['食物', '食物组合', '盒子']:
                    target_list.append(object_one)
                    target_dict[object_id] = object_cate
                elif object_cate in ['电脑', '娱乐', '闹钟', '玩具', '书籍', '书籍组合1', '书籍组合2', '书籍组合3']:
                    target_list.append(object_one)
                    target_dict[object_id] = object_cate
                elif object_cate in ['儿童工艺品', '儿童台灯', '儿童配饰']:
                    target_list.append(object_one)
                    target_dict[object_id] = object_cate
                elif len(target_scope) <= 1:
                    target_list.append(object_one)
                    target_dict[object_id] = '花卉'
                elif 'size_cur' in object_one and object_one['size_cur'][1] > 30:
                    if random.randint(0, 100) < 30:
                        target_list.append(object_one)
                        target_dict[object_id] = '相框'
            # 餐桌椅
            elif 'group' in object_one and object_one['group'] in ['Dining']:
                if 'cloth' in object_role or 'cloth' in object_type:
                    target_list.append(object_one)
                    target_dict[object_id] = '桌布'
                    if 'side table' in plat_type or 'round' in plat_type:
                        pass
                elif object_cate == '花卉' or 'plants' in object_type:
                    # target_list.append(object_one)
                    target_dict[object_id] = '花卉'
                    pass
                else:
                    # target_list.append(object_one)
                    target_dict[object_id] = '餐具组合'
                    if plat_type in ['table/side table']:
                        target_dict[object_id] = '水杯'
            # 电视柜
            elif object_cate == '电视' or 'tv' in object_role:
                if 'electronics/TV - on top of others' in object_type:
                    target_list.append(object_one)
                    target_dict[object_id] = '电视'
            # 办公桌 书柜 玄关柜 衣柜
            elif object_cate in ['水杯', '水壶', '茶具组合', '酒具', '酒具组合1', '酒具组合2',
                                 '花卉', '绿植', '工艺品', '烛台', '相框', '台灯', '烛台', '雕塑', '香薰', '杂志']:
                pass
            elif object_cate in ['食物', '食物组合', '盒子']:
                target_list.append(object_one)
                target_dict[object_id] = object_cate
            elif object_cate in ['电脑', '娱乐', '闹钟', '玩具', '书籍', '书籍组合1', '书籍组合2', '书籍组合3']:
                target_list.append(object_one)
                target_dict[object_id] = object_cate
            elif object_cate in ['抱枕', '盖毯']:
                target_list.append(object_one)
                # target_dict[object_id] = object_cate
                pass
            elif object_cate in ['毛巾', '包', '衣帽', '毛绒玩具']:
                target_list.append(object_one)
                target_dict[object_id] = object_cate
            elif object_cate in ['玄关挂饰', '衣柜挂饰', '挂饰']:
                target_list.append(object_one)
                target_dict[object_id] = object_cate
            elif object_cate in ['儿童工艺品', '儿童台灯', '儿童配饰']:
                target_list.append(object_one)
                target_dict[object_id] = object_cate
            # 梳妆台
            elif plat_cate in ['梳妆台']:
                if object_cate in ['化妆品组合1', '化妆品组合2', '化妆品组合3', '化妆品', '相框']:
                    target_list.append(object_one)
                    target_dict[object_id] = object_cate
                else:
                    target_list.append(object_one)
                    target_dict[object_id] = '化妆品'
            # 餐边柜
            elif plat_cate in ['餐边柜']:
                if object_cate in ['花卉', '酒具', '酒具组合1', '酒具组合2']:
                    target_list.append(object_one)
                    target_dict[object_id] = object_cate
            # 浴室柜
            elif '化妆品' in object_cate or '洗浴品' in object_cate:
                target_list.append(object_one)
                target_dict[object_id] = object_cate
        for replace_idx in range(scheme_num):
            target_used.append({})
        # 推荐信息
        for object_idx, object_one in enumerate(target_list):
            object_id = object_one['id']
            object_cate = ''
            backup_list = []
            if object_id in target_dict:
                object_cate = target_dict[object_id]
                if object_cate in ['桌布']:
                    backup_1 = get_furniture_list_id('桌布')
                    backup_2 = get_furniture_list_id('桌旗')
                    backup_c = max(len(backup_1), len(backup_2))
                    if 'round' in plat_type:
                        for backup_i in range(backup_c):
                            backup_one = backup_1[backup_i % len(backup_1)]
                            if backup_one in FURNITURE_PROPOSE_WRINK:
                                continue
                            backup_list.append(backup_one)
                            if len(backup_list) >= 20:
                                break
                    else:
                        r = random.randint(0, 99)
                        for backup_i in range(backup_c):
                            backup_one = backup_1[(backup_i + 0) % len(backup_1)]
                            backup_two = backup_2[(backup_i + r) % len(backup_2)]
                            if backup_one in FURNITURE_PROPOSE_WRINK:
                                continue
                            if backup_two in FURNITURE_PROPOSE_WRINK:
                                continue
                            backup_list.append(backup_one)
                            backup_list.append(backup_two)
                            if len(backup_list) >= 20:
                                break
                # elif object_cate in ['儿童工艺品', '儿童配饰']:
                #     backup_list = [object_id]
                else:
                    backup_list = get_furniture_list_id(object_cate)
            if len(backup_list) <= 0:
                continue
            if object_id in target_furniture_log:
                log_list = target_furniture_log[object_id]
                for log_one in log_list:
                    log_one['log'] = 'type_err'
            if len(target_furniture) < scheme_num:
                scheme_add = scheme_num - len(target_furniture)
                for replace_idx in range(scheme_add):
                    target_furniture.append({})
            type_old, style_old, size_old = get_furniture_data(object_id)
            size_max = object_one['size_max']
            for replace_idx, replace_one in enumerate(target_furniture):
                # 已有
                object_used = target_used[replace_idx]
                # 抽取
                random_idx += 1
                object_id_new = backup_list[random_idx % len(backup_list)]
                if object_id_new in UNIT_SCALE_ERROR:
                    random_idx += 1
                    object_id_new = backup_list[random_idx % len(backup_list)]
                type_new, style_new, size_new = get_furniture_data(object_id_new)
                for i in range(10):
                    if object_cate in ['桌布', '桌旗']:
                        break
                    elif size_new[0] > size_max[0] * 1.5 or size_new[1] > size_old[1] * 2:
                        random_idx += 1
                        object_id_new = backup_list[random_idx % len(backup_list)]
                        type_new, style_new, size_new = get_furniture_data(object_id_new)
                    elif object_id_new in object_used:
                        random_idx += 1
                        object_id_new = backup_list[random_idx % len(backup_list)]
                        type_new, style_new, size_new = get_furniture_data(object_id_new)
                    else:
                        break
                target_used[replace_idx][object_id_new] = 1
                # 记录
                object_id_old = object_id
                if object_id in replace_one:
                    object_id_old = replace_one[object_id]
                if len(size_new) < 3:
                    continue
                if object_id_old in target_furniture_size:
                    target_furniture_size.pop(object_id_old)
                replace_one[object_id] = object_id_new
                target_furniture_size[object_id_new] = size_new
    # 记录日志
    for propose_idx, propose_one in enumerate(propose_info):
        if not request_log:
            break
        target_furniture_log = propose_one['target_furniture_log']
        request_file = '%s_request_log_%d.json' % (plat_id, propose_idx)
        request_path = os.path.join(DATA_DIR_SERVER_SERVICE, request_file)
        with open(request_path, "w") as f:
            json.dump(target_furniture_log, f, indent=4)
            f.close()


# 推荐返回调整
def response_tran_list(response_list):
    replace_dict = {}
    for replace_idx, replace_one in enumerate(response_list):
        if replace_idx >= 20:
            break
        replace_orig_dict = replace_one['Virt2ModelMap']
        replace_size_dict = replace_one['ModelSizeMap']
        for source_id, replace_id in replace_orig_dict.items():
            if source_id not in replace_dict:
                replace_dict[source_id] = []
            if replace_id not in replace_size_dict:
                continue
            replace_size = replace_size_dict[replace_id]
            size_set = replace_size.split('&')
            if len(size_set) >= 3:
                size_x = float(size_set[0].split('=')[-1])
                size_z = float(size_set[1].split('=')[-1])
                size_y = float(size_set[2].split('=')[-1])
                if size_x <= -1 or size_y <= -1:
                    continue
                object_info = {'id': replace_id, 'size': [size_x, size_y, size_z]}
                replace_dict[source_id].append(object_info)
            else:
                continue
    return replace_dict


# 推荐返回调整
def response_tran_dict(response_dict):
    replace_dict = {}
    for target_key, target_val in response_dict.items():
        source_id = target_key
        replace_dict[source_id] = []
        for target_idx, target_one in enumerate(target_val):
            if target_idx >= 20:
                break
            if 'modelId' in target_one and 'x' in target_one and 'y' in target_one and 'z' in target_one:
                replace_id = target_one['modelId']
                size_x, size_z, size_y = target_one['x'], target_one['y'], target_one['z']
                if size_x <= -1 or size_y <= -1:
                    continue
                object_info = {'id': replace_id, 'size': [size_x, size_y, size_z]}
                replace_dict[source_id].append(object_info)
    return replace_dict


# 更新组合数据
def refresh_furniture_group():
    house_list_path = os.path.join(DATA_DIR_RECORD, 'hs_design_fine.txt')
    house_list_group = []
    if os.path.exists(house_list_path):
        f = open(house_list_path, 'r')
        line_list = f.readlines()
        for line_one in line_list:
            line_new = line_one.split('=')[-1].rstrip()
            if line_new == '#':
                break
            house_list_group.append(line_new)
            if len(house_list_group) >= 100:
                break
    house_list_group = ['870c6e14-5d7f-42ff-9060-1a6ebd25a109']
    # 遍历方案
    for design_id in house_list_group:
        layout_group_extract_once(design_id, upload_group=False, upload_room=False, local_group=False,
                                  save_code=10, save_num=25, save_mode=[SAVE_MODE_IMAGE])
    # 更新数据
    save_furniture_data()


# 更新装饰数据
def refresh_furniture_decor():
    obj_list = []
    for obj_one in obj_list:
        get_furniture_plat(obj_one, '', True)
    save_furniture_plat()


# 推荐服务并发
class AsyncPropose(multiprocessing.Process):
    # 并行处理构造
    def __init__(self, input_new, output_new):
        multiprocessing.Process.__init__(self)
        self.input_set = input_new
        self.output_set = output_new

    # 并行处理执行
    def run(self):
        propose_dict = {}
        print('% 6d' % self.pid, 'from', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
        server_url = FURNITURE_PROPOSE_UAT
        for propose_data in self.input_set:
            request_data = {
                'appid': FURNITURE_PROPOSE_APP_ID,
                'userId': FURNITURE_PROPOSE_USR_ID,
                'DEBUG': 'true',
                'input_json': json.dumps(propose_data)
            }
            response_info = requests.post(server_url, data=request_data)
            response_data = response_info.json()
            response_good = False
            if 'result' in response_data and len(response_data['result']) > 0:
                if 'return_map' in response_data['result'][0]:
                    response_map = response_data['result'][0]['return_map']
                    response_dict = response_tran_dict(response_map)
                    if len(response_dict) > 0:
                        response_good = True
                elif 'returnCollectionList' in response_data['result'][0]:
                    response_list = response_data['result'][0]['returnCollectionList']
                    response_dict = response_tran_list(response_list)
                    if len(response_dict) > 0:
                        response_good = True
            if not response_good:
                response_info = requests.post(server_url, data=request_data)
                response_data = response_info.json()
                if 'return_map' in response_data['result'][0]:
                    response_map = response_data['result'][0]['return_map']
                    response_dict = response_tran_dict(response_map)
                    if len(response_dict) > 0:
                        response_good = True
                elif 'returnCollectionList' in response_data['result'][0]:
                    response_list = response_data['result'][0]['returnCollectionList']
                    response_dict = response_tran_list(response_list)
                    if len(response_dict) > 0:
                        response_good = True
        self.output_set.put(propose_dict)
        print('% 6d' % self.pid, 'done', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    pass


# 推荐服务地址
def propose_accessory_url():
    global FURNITURE_PROPOSE_URL
    if FURNITURE_PROPOSE_URL == '':
        env, loc, ver = '', '', ''
        try:
            r = requests.get('http://jmenv.tbsite.net:8080/env', timeout=1)
            r.raise_for_status()
            env = r.text.strip()
        except Exception as e:
            print('get environment error:', e)
        if 'daily' in env:
            FURNITURE_PROPOSE_URL = FURNITURE_PROPOSE_PRO
        elif 'pre' in env:
            FURNITURE_PROPOSE_URL = FURNITURE_PROPOSE_PRO
        else:
            FURNITURE_PROPOSE_URL = FURNITURE_PROPOSE_PRO
    return FURNITURE_PROPOSE_URL


# 功能测试
if __name__ == '__main__':
    random_seed = 6
    # 清空缓存
    # layout_group_clear()
    # refresh_furniture_group()
    pass

    # 测试接口 组合生成
    pass

    # 测试接口 组合提取
    layout_param_input = smart_decoration_input_group_test_99
    # layout_param_output = layout_group_param(layout_param_input)
    pass

    # 测试接口 组合配饰
    layout_param_input = smart_decoration_input_adorn_test_01_v2
    if 'plat_id' in layout_param_input:
        plat_id = layout_param_input['plat_id']
        get_furniture_data_more(plat_id)
    # layout_param_output = layout_group_param(layout_param_input, True)
    pass
    # 测试接口 组合配饰
    layout_param_input = smart_decoration_input_adorn_test_03
    if 'plat_id' in layout_param_input:
        plat_id = layout_param_input['plat_id']
        get_furniture_data_more(plat_id)
    layout_param_output = layout_group_param(layout_param_input, True)
    pass

    # 测试接口 组合内空
    layout_param_input = smart_decoration_input_inner_test_99
    if 'plat_id' in layout_param_input:
        plat_id = layout_param_input['plat_id']
        get_furniture_data_more(plat_id)
    # layout_param_output = layout_group_param(layout_param_input, True)
    pass

    # 测试接口 组合渲染
    layout_param_input = smart_decoration_input_render_test_99
    # layout_param_output = layout_group_param(layout_param_input)
    pass
    # 测试接口 组合渲染
    layout_param_input = smart_decoration_input_render_test_01
    # layout_param_output = layout_group_param(layout_param_input)
    layout_param_input = smart_decoration_input_render_test_02
    # layout_param_output = layout_group_param(layout_param_input)
    layout_param_input = smart_decoration_input_render_test_03
    # layout_param_output = layout_group_param(layout_param_input)
    layout_param_input = smart_decoration_input_render_test_04
    # layout_param_output = layout_group_param(layout_param_input)
    pass

    # 数据更新
    # save_furniture_data()
    # save_furniture_plat()
    pass
