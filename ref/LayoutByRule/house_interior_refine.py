# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2020-02-29
@Description: 全屋布局优化

"""

import copy
import datetime
import requests
import multiprocessing
from scipy.spatial.transform import Rotation as R
from shapely.geometry.polygon import Polygon
from Furniture.furniture_group import *
from Furniture.furniture_analysis import *

# 提升组合类型
RAISE_GROUP_MAIN = ['Media', 'Work', 'Rest', 'Cabinet']
RAISE_GROUP_LIST = ['Meeting', 'Media', 'Dining', 'Work', 'Rest', 'Cabinet']
RAISE_GROUP_ROLE = ['sofa', 'table', 'side table', 'chair', 'cabinet']
# 提升组合计数
RAISE_COUNT_PLAT = 0
# 沙发扶手宽度
UNIT_WIDTH_SOFA_SINGLE = 1.50
UNIT_WIDTH_SOFA_HANDLE = 0.15
# 柜体抽屉宽度
UNIT_WIDTH_PLAT_SINGLE = 0.30
# 配饰尺寸纠正
UNIT_SCALE_LOWER = ['2a568730-1095-44a3-b2c9-4bf84782bba3', '4ef47d22-4f9d-4a0b-af30-6bee8bb074ab',
                    'b7be3f5b-d338-4a0f-b1fb-15a1422ffb9a', '3e8caebb-dbf0-4eb2-841f-76a34710ea72']
UNIT_SCALE_UPPER = ['258fd611-62ce-4ea0-9de2-0451b3286782']
UNIT_SCALE_OTHER = ['cc48f96b-137a-4e46-b7f2-e9c4caf9cc98', '9da24ebf-4690-4146-bb21-93ee0bcb1d6c',
                    'c8e286e4-32dc-4a52-bb1d-0bd10fa816fc', '3b1497f2-1c96-4f21-8946-8611a03e88c0']
UNIT_SCALE_ERROR = ['b2b81db3-ffa2-4b08-9dbb-d56464d3b231', 'b213ad3d-b377-4af4-be14-676d94239e2d']
# 平台承载分析
UNIT_SHAPE_LOCAL = ['0723ca8f-5e6c-4c5d-96a0-ae2a9cfe7e09']


# 家具丰富提升
def house_rect_raise(house_layout_info, raise_mode=1, limit_num=16):
    layout_info = house_layout_info
    # 遍历房间
    for room_key, room_val in layout_info.items():
        room_rect_raise(room_val, raise_mode, limit_num)


# 家具丰富提升
def room_rect_raise(room_layout_info, raise_mode=1, limit_num=16):
    layout_info, layout_seed = room_layout_info, []
    room_type, room_style, room_area = layout_info['room_type'], layout_info['room_style'], layout_info['room_area']
    if 'layout_seed' in layout_info:
        layout_seed = layout_info['layout_seed']
    if len(layout_seed) > 0:
        room_style = layout_seed[0]['style']
    global RAISE_GROUP_MAIN

    # 查找方案
    scheme_list = layout_info['layout_scheme']
    raise_dict, raise_more = {}, []
    if raise_mode >= 1:
        raise_dict, raise_more = compute_scheme_raise(room_type, room_style, scheme_list)

    # 确定方案
    scheme_raise_todo, scheme_raise_dict = [], {}
    for layout_idx, layout_one in enumerate(scheme_list):
        group_base, group_more = layout_one['group'], []
        if 'group_propose' in layout_one:
            group_more = layout_one['group_propose']
        group_todo = [group_base]
        for group_list in group_more:
            group_todo.append(group_list)
        # 组合遍历
        for group_list_idx, group_list_one in enumerate(group_todo):
            scheme_raise_dict = {}
            scheme_count_todo = len(scheme_raise_todo)
            for group_idx, group_one in enumerate(group_list_one):
                group_type = group_one['type']
                if group_type not in RAISE_GROUP_LIST:
                    continue
                object_list, seed_list = group_one['obj_list'], []
                if 'seed_list' in group_one:
                    seed_list = group_one['seed_list']
                for object_idx, object_one in enumerate(object_list):
                    # 平台信息
                    plat_id, plat_one = object_one['id'], object_one
                    plat_role, plat_type, plat_style = plat_one['role'], plat_one['type'], plat_one['style']
                    plat_size, plat_width, plat_height = [], 1, 1
                    if 'size' in plat_one and 'scale' in plat_one:
                        plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
                        plat_width, plat_height = plat_size[0], plat_size[1]
                    normal_pos = [0, 0, 0]
                    if 'normal_position' in plat_one:
                        normal_pos = plat_one['normal_position']
                    # 原有配饰
                    raise_used, raise_none = [], 0
                    for access_idx in range(len(object_list) - 1, -1, -1):
                        # 配饰信息
                        access_one, access_role, access_pos = object_list[access_idx], '', [0, 0, 0]
                        if 'role' in access_one:
                            access_role = access_one['role']
                        if 'normal_position' in access_one:
                            access_pos = access_one['normal_position']
                        # 依附信息
                        relate_id, relate_role, relate_shift = '', '', []
                        if 'relate' in access_one:
                            relate_id = access_one['relate']
                        if 'relate_role' in access_one:
                            relate_role = access_one['relate_role']
                        if access_role in ['tv'] and len(relate_role) <= 0:
                            relate_role = 'table'
                        if 'normal_position' in access_one:
                            relate_shift = access_one['normal_position']
                        if relate_role == plat_role:
                            if relate_role in ['side table']:
                                if len(access_pos) >= 3 and len(normal_pos) >= 3:
                                    if abs(access_pos[0] - normal_pos[0]) < 0.5:
                                        if abs(access_pos[2] - normal_pos[2]) < 0.5:
                                            raise_used.append(access_one)
                            else:
                                raise_used.append(access_one)
                            if group_list_idx > 0 and access_one in raise_used and access_role not in ['tv']:
                                object_list.pop(access_idx)
                    if group_type in ['Media'] and plat_role in ['table']:
                        raise_none = 1
                    if raise_mode == 0:
                        if plat_role in RAISE_GROUP_ROLE:
                            raise_used = overlap_plat_raise(raise_used, plat_one)
                        continue
                    if group_list_idx == 0 and len(raise_used) > raise_none:
                        raise_used = overlap_plat_raise(raise_used, plat_one)
                        continue
                    if plat_role not in RAISE_GROUP_ROLE or plat_type.startswith('sofa') or plat_type.startswith('chair'):
                        continue
                    elif resolve_plat_raise(group_type, plat_role, plat_type, plat_height) <= 0:
                        continue
                    if group_type in ['Meeting'] and plat_role in ['table'] and plat_height < 0.50:
                        pass
                    elif group_type in ['Dining', 'Work'] and plat_role in ['table'] and plat_height < 1.00:
                        pass
                    else:
                        continue
                    plat_pack = get_furniture_pack(plat_id)
                    plat_turn = get_furniture_turn(plat_id)
                    if plat_pack in ['Assembly']:
                        continue
                    if abs(plat_turn) > 0.1 and abs(abs(plat_turn) - 1) > 0.1:
                        continue
                    # 平台信息
                    plat_pos = plat_one['position']
                    plat_key1 = group_type + '_' + plat_role
                    plat_key2 = group_type + '_' + plat_role + '_%0.1f_%0.1f' % (plat_pos[0], plat_pos[2])
                    if plat_role in ['side table']:
                        plat_key2 = group_type + '_' + plat_role
                    raise_base, raise_wait = [], []
                    if plat_key2 in raise_dict:
                        raise_temp = raise_dict[plat_key2]
                        if len(raise_temp) > 0:
                            raise_base = raise_temp[scheme_count_todo % len(raise_temp)]
                    elif plat_key1 in raise_dict:
                        raise_temp = raise_dict[plat_key1]
                        if len(raise_temp) > 0:
                            raise_base = raise_temp[scheme_count_todo % len(raise_temp)]
                    if len(raise_more) > 0:
                        raise_temp = raise_more
                        raise_wait = raise_temp[scheme_count_todo % len(raise_temp)]
                    if len(raise_base) <= 0:
                        continue
                    # 任务信息
                    plat_key = '%s_%.1f_%.1f' % (plat_id, plat_pos[0], plat_pos[2])
                    if plat_key in scheme_raise_dict:
                        continue
                    if len(group_todo) <= 1:
                        scheme_raise_dict[plat_key] = {'group': group_one, 'plat': plat_one,
                                                       'base': raise_base, 'wait': raise_wait}
                    elif group_list_idx in [1]:
                        scheme_raise_dict[plat_key] = {'group': group_one, 'plat': plat_one,
                                                       'base': raise_base, 'wait': raise_wait}
                    elif len(raise_used) > 0:
                        raise_used = overlap_plat_raise(raise_used, plat_one)
            # 任务记录
            if len(scheme_raise_dict) > 0:
                scheme_raise_todo.append(scheme_raise_dict)

    # 并发分析
    process_sync, process_list, process_queue = False, [], multiprocessing.Queue()
    if not process_sync:
        object_used = {}
        for scheme_idx, scheme_one in enumerate(scheme_raise_todo):
            object_todo = []
            for raise_key, raise_one in scheme_one.items():
                plat_one = raise_one['plat']
                plat_id = plat_one['id']
                if plat_id in object_used:
                    continue
                object_used[plat_id] = 1
                if not have_furniture_plat(plat_id):
                   object_todo.append(plat_one)
            if len(object_todo) > 0 and len(scheme_raise_todo) > 0:
                process_one = AsyncShape(object_todo, process_queue)
                process_list.append(process_one)
                process_one.start()
            elif len(scheme_raise_todo) > 6:
                object_todo_1 = object_todo[0:int(len(object_todo) / 2)]
                object_todo_2 = object_todo[int(len(object_todo) / 2):len(object_todo)]
                #
                process_one = AsyncShape(object_todo_1, process_queue)
                process_list.append(process_one)
                process_one.start()
                #
                process_two = AsyncShape(object_todo_2, process_queue)
                process_list.append(process_two)
                process_two.start()
                pass
        if process_queue:
            process_done = [process_queue.get() for process_one in process_list]
            for shape_dict in process_done:
                for shape_key, shape_val in shape_dict.items():
                    if len(shape_val) > 0:
                        add_furniture_plat(shape_key, shape_val)
                    else:
                        get_furniture_data(shape_key, '', True, True)
    if len(scheme_raise_todo) > 0:
        print('refine room', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))

    # 布局方案
    shape_cnt = 0
    for scheme_idx, scheme_one in enumerate(scheme_raise_todo):
        raise_dict = {}
        for raise_key, raise_one in scheme_one.items():
            # 平台
            group_one, plat_one = raise_one['group'], raise_one['plat']
            group_type, plat_id = group_one['type'], plat_one['id']
            plat_pack = get_furniture_pack(plat_id)
            if plat_pack in ['Assembly']:
                continue
            if not have_furniture_plat(plat_id):
                if group_type in ['Cabinet'] and shape_cnt < 3:
                    shape_cnt += 1
                else:
                    continue
            # 配饰
            raise_base, raise_wait = raise_one['base'], raise_one['wait']
            raise_swap = False
            if plat_one['role'] in ['side table'] and plat_id in raise_dict:
                raise_face = raise_dict[plat_id]
                raise_base = raise_face
                raise_swap = True
            raise_done = replace_plat_raise(group_one, plat_one, raise_base, raise_wait, raise_swap, room_type)
            raise_done = overlap_plat_raise(raise_done, plat_one)
            if group_one['type'] in ['Media']:
                add_furniture_group_deco(group_one)
            if plat_one['role'] in ['side table'] and plat_one['id'] not in raise_dict:
                raise_dict[plat_one['id']] = raise_done
    if len(scheme_raise_todo) > 0:
        print('refine room', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))


# 家具丰富提升
def group_rect_raise(group_one, item_one={}, layout_num=1, room_type='', room_style=''):
    # 商品
    plat_dict, item_size = 'plat', []
    if len(item_one) > 0:
        plat_dict = item_one['relate_role']
        item_size = [abs(item_one['size'][i] * item_one['scale'][i]) / 100 for i in range(3)]
    group_new = group_one.copy()
    group_new['obj_list'] = group_one['obj_list'][:]
    # 平台
    plat_one, plat_key, plat_role = {}, '', ''
    obj_set = group_new['obj_list']
    for obj_idx, obj_one in enumerate(obj_set):
        if len(plat_one) <= 0:
            plat_one = obj_one
            plat_key = obj_one['id']
        if 'role' in obj_one and obj_one['role'] in plat_dict:
            plat_one = obj_one
            plat_key = obj_one['id']
            plat_role = obj_one['role']
            break
    # 查找
    deco_one, deco_dlt, deco_bot = {}, 10, 0
    obj_set = group_new['obj_list']
    for obj_idx, obj_one in enumerate(obj_set):
        if len(item_one) <= 0:
            break
        if 'relate' in obj_one and obj_one['relate'] == plat_key:
            obj_size = [abs(obj_one['size'][i] * obj_one['scale'][i]) / 100 for i in range(3)]
            obj_diff = abs(obj_size[0] - item_size[0]) + abs(obj_size[1] - item_size[1]) + abs(obj_size[2] - item_size[2])
            if obj_diff < deco_dlt:
                deco_one = obj_one
                deco_dlt = obj_diff
    # 生成
    if len(deco_one) <= 0 and len(plat_one) > 0 and len(group_new) > 0:
        # 布局方案
        group_type, group_style, group_size = group_new['type'], group_new['style'], group_new['size']
        group_min = {'type': group_type, 'style': group_style, 'size': group_size, 'obj_list': [plat_one]}
        group_set = compute_plat_raise(room_type, room_style, group_min, plat_one, layout_num, [], True, True)
        for group_add in group_set:
            if len(item_one) <= 0:
                break
            # 查找
            obj_set = group_add['obj_list']
            for obj_idx, obj_one in enumerate(obj_set):
                if 'relate' in obj_one and obj_one['relate'] == plat_key:
                    obj_size = [abs(obj_one['size'][i] * obj_one['scale'][i]) / 100 for i in range(3)]
                    obj_diff = abs(obj_size[0] - item_size[0]) + abs(obj_size[1] - item_size[1]) + \
                               abs(obj_size[2] - item_size[2])
                    obj_lift = obj_one['position'][1]
                    if obj_lift < deco_bot and len(deco_one) > 0:
                        break
                    if obj_diff < deco_dlt:
                        deco_one = obj_one
                        deco_dlt = obj_diff
                        deco_bot = obj_lift
            if len(deco_one) > 0 and len(group_add) > 0:
                obj_set_new = group_new['obj_list']
                obj_set_add = group_add['obj_list']
                for obj_idx in range(len(obj_set_new) - 1, -1, -1):
                    obj_one = obj_set_new[obj_idx]
                    if 'relate' in obj_one and obj_one['relate'] == plat_key:
                        obj_set_new.pop(obj_idx)
                for obj_idx in range(len(obj_set_add) - 1, -1, -1):
                    obj_one = obj_set_add[obj_idx]
                    if 'relate' in obj_one and obj_one['relate'] == plat_key:
                        obj_set_new.append(obj_one)
                break
    if len(item_one) > 0 and len(deco_one) > 0:
        group_new['target'] = [deco_one]
    return group_new


# 家具避让删减
def house_rect_erase(house_layout_info):
    layout_info = house_layout_info
    # 遍历房间
    for room_key, room_val in layout_info.items():
        room_rect_erase(room_val)


# 家具避让删减 TODO:
def room_rect_erase(room_layout_info):
    scheme_list = []
    if 'layout_scheme' in room_layout_info:
        scheme_list = room_layout_info['layout_scheme']
    # 遍历方案
    for scheme_idx, scheme_one in enumerate(scheme_list):
        group_list, group_todo, group_keep = scheme_one['group'], [], []
        # 分类
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type in ['Meeting', 'Bed', 'Dining', 'Work', 'Rest']:
                group_todo.append(group_one)
            elif group_type in ['Armoire', 'Cabinet', 'Window']:
                group_keep.append(group_one)
        # 检测 TODO:
        for group_one in group_todo:
            pass
        pass


# 家具镜像调整
def house_rect_mirror(house_layout_info):
    layout_info = house_layout_info
    # 遍历房间
    for room_key, room_val in layout_info.items():
        room_rect_mirror(room_val)
    pass


# 家具镜像调整
def room_rect_mirror(room_layout_info):
    scheme_list = []
    if 'layout_scheme' in room_layout_info:
        scheme_list = room_layout_info['layout_scheme']
    for scheme_idx, scheme_one in enumerate(scheme_list):
        group_list, object_list = [], []
        if 'group' in scheme_one:
            group_list = scheme_one['group']
        for group_idx, group_one in enumerate(group_list):
            group_type, group_rely, object_list = '', 0, []
            if 'type' in group_one:
                group_type = group_one['type']
            if 'region_direct' in group_one:
                group_rely = group_one['region_direct']
            if 'obj_list' in group_one:
                object_list = group_one['obj_list']
            if group_type not in ['Armoire', 'Cabinet']:
                continue
            if group_rely not in [-1, 1]:
                continue
            if len(object_list) <= 0:
                continue
            object_main = object_list[0]
            object_main_id = object_main['id']
            object_rely = get_furniture_direct(object_main_id)
            if object_rely == 0 or group_rely == -object_rely:
                continue
            plat_pos, plat_ang = object_main['position'], rot_to_ang(object_main['rotation'])
            # 镜像处理
            plat_scale = object_main['scale']
            plat_scale[0] *= -1
            # 遍历物品
            for object_idx, object_one in enumerate(object_list):
                if 'relate' in object_one and object_one['relate'] == object_main_id:
                    pass
                else:
                    continue
                # 镜像处理
                normal_pos, normal_rot = object_one['position'][:], object_one['rotation']
                if 'normal_position' in object_one:
                    normal_pos = object_one['normal_position'][:]
                if 'normal_rotation' in object_one:
                    normal_rot = object_one['normal_rotation']
                normal_pos[0] *= -1
                normal_ang = -rot_to_ang(normal_rot)
                object_one['normal_rotation'] = [0, math.sin(normal_ang / 2), 0, math.cos(normal_ang / 2)]
                # 镜像处理
                tmp_x = normal_pos[0]
                tmp_z = normal_pos[2]
                add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
                add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
                object_pos = [plat_pos[0] + add_x, plat_pos[1] + normal_pos[1], plat_pos[2] + add_z]
                object_ang = plat_ang + normal_ang
                object_one['position'] = object_pos
                object_one['rotation'] = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]


# 方案装饰查找
def compute_scheme_raise(room_type, room_style, scheme_list, fine_flag=False):
    global RAISE_GROUP_MAIN
    global RAISE_GROUP_ROLE
    raise_dict, raise_more = {}, []
    raise_num, raise_old = 3, []
    plat_size, plat_width, plat_height = [], 1, 1
    for layout_idx, layout_one in enumerate(scheme_list):
        group_list = layout_one['group']
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            if group_type not in RAISE_GROUP_LIST:
                continue
            object_list = group_one['obj_list']
            for object_idx, object_one in enumerate(object_list):
                # 平台信息
                plat_id, plat_one = object_one['id'], object_one
                plat_role, plat_type, plat_style = plat_one['role'], plat_one['type'], plat_one['style']
                if 'size' in plat_one and 'scale' in plat_one:
                    plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
                    plat_width, plat_height = plat_size[0], plat_size[1]
                if plat_role not in RAISE_GROUP_ROLE:
                    continue
                if plat_type.startswith('chair'):
                    continue
                # 平台信息
                plat_pos = plat_one['position']
                plat_key1 = group_type + '_' + plat_role
                plat_key2 = group_type + '_' + plat_role + '_%0.1f_%0.1f' % (plat_pos[0], plat_pos[2])
                if plat_role in ['side table']:
                    plat_key2 = group_type + '_' + plat_role
                if plat_key2 in raise_dict:
                    continue
                # 配饰信息
                room_type_new, room_style_new = room_type, room_style
                group_type_new, plat_role_new = group_type, plat_role
                if room_type in ['KidsRoom']:
                    room_style_new = ''
                    fine_flag = True
                if group_type in ['Meeting', 'Media', 'Rest', 'Bed']:
                    room_type_new = ''
                if group_type in ['Rest'] and plat_role in ['chair']:
                    room_type_new, group_type_new, plat_role_new = '', 'Meeting', 'sofa'
                raise_list = get_furniture_group_deco(room_type_new, room_style_new, group_type_new, plat_role_new,
                                                      '', '', '', plat_height, raise_num, raise_old, fine_flag)
                if group_type in ['Dining']:
                    for raise_one in raise_list:
                        dining_rand = compute_deco_raise(random.randint(0, 20), '餐具组合')
                        flower_rand = compute_deco_raise(random.randint(0, 20), '花卉')
                        if 'side table' in plat_type:
                            dining_rand = compute_deco_raise(random.randint(0, 20), '水杯')
                        for object_one in raise_one:
                            object_id = object_one['id']
                            object_type = object_one['type']
                            if object_id not in UNIT_SCALE_OTHER:
                                continue
                            object_new = dining_rand
                            if 'plants' in object_type:
                                object_new = flower_rand
                            object_one['id'] = object_new['id']
                            object_one['type'] = object_new['type']
                            object_one['style'] = object_new['style']
                            object_one['size'] = object_new['size']
                            object_one['scale'] = object_new['scale']
                if len(raise_list) <= 0 and 'window' in plat_role:
                    raise_list = get_furniture_group_deco(room_type, room_style, 'Meeting', 'sofa',
                                                          '', '', '', plat_height, raise_num, raise_old, fine_flag)
                elif len(raise_list) <= 0 and 'table' in plat_role:
                    raise_list = get_furniture_group_deco('', room_style, 'Meeting', 'table',
                                                          '', '', '', plat_height, raise_num, raise_old, fine_flag)
                # 添加信息
                raise_dict[plat_key1] = raise_list
                raise_dict[plat_key2] = raise_list
    if 'Bathroom' in room_type:
        pass
    else:
        raise_more = get_furniture_group_deco(room_type, room_style, 'Cabinet', 'cabinet',
                                              '', '', '', plat_height, raise_num, raise_old, fine_flag)
    return raise_dict, raise_more


# 家具装饰查找
def compute_plat_raise(room_type, room_style, group_one, plat_one, raise_num=3, raise_old=[],
                       fine_flag=False, pack_flag=False):
    group_type, plat_id = '', ''
    plat_role, plat_type, plat_style = '', '', ''
    plat_size, plat_width, plat_height = [], 1, 1
    if 'type' in group_one:
        group_type = group_one['type']
    if 'id' in plat_one:
        plat_id = plat_one['id']
    if 'role' in plat_one:
        plat_role = plat_one['role']
    if 'type' in plat_one:
        plat_type = plat_one['type']
    if 'style' in plat_one:
        plat_style = plat_one['style']
    if 'size' in plat_one and 'scale' in plat_one:
        plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
        plat_width, plat_height = plat_size[0], plat_size[1]
    # 装饰判断
    group_list = []
    if resolve_plat_raise(group_type, plat_role, plat_type, plat_height) <= 0:
        return group_list
    plat_pack = get_furniture_pack(plat_id)
    if plat_pack in ['Assembly']:
        return group_list
    # 家具类目
    plat_cate = compute_plat_cate(plat_one, room_type)
    # 基本配饰
    room_type_new, group_type_new, plat_role_new = room_type, group_type, plat_role
    if group_type in ['Meeting', 'Media', 'Rest', 'Bed']:
        room_type_new, group_type_new, plat_role_new = '', group_type, plat_role
    if group_type in ['Rest'] and plat_role in ['chair']:
        room_type_new, group_type_new, plat_role_new = '', 'Meeting', 'sofa'
    if plat_cate in ['玄关台', '玄关柜']:
        room_type_new, group_type_new, plat_role_new = '', 'Work', 'table'
    raise_list = get_furniture_group_deco(room_type_new, room_style, group_type_new, plat_role_new,
                                          plat_id, plat_type, plat_style, plat_height,
                                          raise_num, raise_old, fine_flag)
    if group_type in ['Dining']:
        for raise_one in raise_list:
            dining_rand = compute_deco_raise(random.randint(0, 100), '餐具组合')
            flower_rand = compute_deco_raise(random.randint(0, 100), '花卉')
            if 'side table' in plat_type:
                dining_rand = compute_deco_raise(random.randint(0, 100), '水杯')
            for object_one in raise_one:
                object_id = object_one['id']
                object_type = object_one['type']
                if object_id not in UNIT_SCALE_OTHER:
                    continue
                object_new = dining_rand
                if 'plants' in object_type:
                    object_new = flower_rand
                object_one['id'] = object_new['id']
                object_one['type'] = object_new['type']
                object_one['style'] = object_new['style']
                object_one['size'] = object_new['size']
                object_one['scale'] = object_new['scale']
    elif len(raise_list) <= 0 and 'table' in plat_role:
        raise_list = get_furniture_group_deco('', room_style, 'Meeting', 'table', '', '', '', plat_height,
                                              raise_num, raise_old, fine_flag)
    elif len(raise_list) <= 0 and 'window' in plat_role:
        raise_list = get_furniture_group_deco('', room_style, 'Meeting', 'sofa',
                                              '', '', '', plat_height,
                                              raise_num, raise_old, fine_flag)

    # 指定配置 TODO:
    pass

    # 补充配饰
    raise_more = []
    if plat_role in ['sofa', 'chair']:
        raise_more = raise_list[:]
    elif plat_role in ['table', 'side table'] and group_type not in ['Dining']:
        if plat_cate in ['茶桌', '茶几'] or group_type in ['Meeting']:
            raise_more = get_furniture_group_deco(room_type, room_style, 'Cabinet', 'cabinet',
                                                  '', '', plat_style, plat_height, raise_num, raise_old, fine_flag)
            pass
        elif plat_cate in ['书桌', '书台'] or room_type in ['Library']:
            raise_more = get_furniture_group_deco('Library', room_style, 'Cabinet', 'cabinet',
                                                  '', '', plat_style, plat_height, raise_num, raise_old, fine_flag)
        elif plat_cate in ['梳妆台']:
            raise_more = []
        else:
            raise_more = get_furniture_group_deco(room_type, room_style, 'Cabinet', 'cabinet',
                                                  '', '', plat_style, plat_height, raise_num, raise_old, fine_flag)
    elif plat_role in ['cabinet']:
        if plat_cate in ['玄关台', '玄关柜']:
            raise_more = get_furniture_group_deco(room_type, room_style, 'Cabinet', 'cabinet',
                                                  '', '', plat_style, plat_height, raise_num, raise_old, fine_flag)
        elif plat_cate in ['餐边柜']:
            raise_more = get_furniture_group_deco('DiningRoom', room_style, 'Cabinet', 'cabinet',
                                                  '', '', plat_style, plat_height, raise_num, raise_old, fine_flag)
        elif plat_cate in ['浴室柜', '洗衣机柜']:
            raise_more = []
    if len(raise_more) <= 0:
        for raise_idx, raise_one in enumerate(raise_list):
            raise_more.insert(0, raise_one)

    # 组装配饰
    if len(raise_list) <= 0:
        return group_list
    # 纠正配饰
    for i in range(raise_num):
        # 基础配饰
        raise_new = raise_list[(i + 0) % len(raise_list)]
        group_new = copy_group(group_one)
        plat_new = plat_one
        if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
            if plat_one == group_one['obj_list'][0]:
                plat_new = group_new['obj_list'][0]
        # 修正配饰
        unique_fix = False
        unique_fix_3 = ['茶具组合', '食物组合', '杂志']
        unique_fix_2 = ['水壶', '食物', '花卉', '烛台']
        unique_fix_1 = ['水杯', '食物']
        # 修正处理
        if plat_role in ['table'] and group_new['type'] in ['Dining'] and i == 1:
            room_type_new, group_type_new, plat_role_new = '', 'Meeting', 'table'
            raise_back = get_furniture_group_deco(room_type_new, room_style, group_type_new, plat_role_new,
                                                  plat_id, plat_type, plat_style, plat_height,
                                                  raise_num, raise_old, fine_flag)
            if len(raise_back) > 0:
                group_new['type'] = 'Rest'
                raise_new = raise_back[0]
                unique_fix = True
                unique_fix_3 = ['茶具组合', '食物组合', '杂志']
                unique_fix_2 = ['水壶', '食物', '花卉', '烛台']
                unique_fix_1 = ['水杯', '食物']
        if unique_fix:
            random.shuffle(unique_fix_1)
            random.shuffle(unique_fix_2)
            random.shuffle(unique_fix_3)
            object_max = {}
            for object_one in raise_new:
                if len(object_max) <= 0:
                    object_max = object_one
                elif abs(object_one['size'][0] * object_one['scale'][0]) > abs(object_max['size'][0] * object_max['scale'][0]):
                    object_max = object_one
            for object_one in raise_new:
                object_id = object_one['id']
                object_cate = get_furniture_cate(object_id)
                if object_cate in unique_fix_1:
                    if len(unique_fix_1) >= 2:
                        unique_fix_1.remove(object_cate)
                    continue
                if object_cate in unique_fix_2:
                    if len(unique_fix_2) >= 2:
                        unique_fix_2.remove(object_cate)
                    continue
                if object_cate in unique_fix_3:
                    if len(unique_fix_3) >= 2:
                        unique_fix_3.remove(object_cate)
                    continue
                object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                if max(object_size[0], object_size[2]) > 0.30 or object_max == object_one:
                    object_cate = unique_fix_3[0]
                    if len(unique_fix_3) >= 2:
                        unique_fix_3.remove(object_cate)
                elif max(object_size[0], object_size[2]) > 0.20:
                    object_cate = unique_fix_2[0]
                    if len(unique_fix_2) >= 2:
                        unique_fix_2.remove(object_cate)
                else:
                    object_cate = unique_fix_1[0]
                    if len(unique_fix_1) >= 2:
                        unique_fix_1.remove(object_cate)
                object_new = compute_deco_raise(random.randint(0, 100), object_cate)
                object_one['id'] = object_new['id']
                object_one['type'] = object_new['type']
                object_one['style'] = object_new['style']
                object_one['size'] = object_new['size']
                object_one['scale'] = object_new['scale']
                if object_cate in ['水壶', '水杯', '茶具组合', '食物组合', '相框']:
                    object_one['normal_rotation'] = [0, 0, 0, 1]
        # 候补配饰
        raise_add = raise_more[(i + 0) % len(raise_more)]
        if len(raise_add) > len(raise_new) and not unique_fix:
            raise_new = raise_add
        # 布局处理
        object_done = replace_plat_raise(group_new, plat_new, raise_new, raise_add, False, room_type)
        object_done = overlap_plat_raise(object_done, plat_new)
        group_list.append(group_new)
    return group_list


# 家具装饰替换
def replace_plat_raise(group_one, plat_one, object_list, object_wait=[], object_swap=False, room_type=''):
    # 分组信息
    group_type = ''
    if 'type' in group_one:
        group_type = group_one['type']
    # 平台信息
    plat_id = plat_one['id']
    plat_role, plat_type, plat_cate = plat_one['role'], plat_one['type'], compute_plat_cate(plat_one, room_type)
    plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
    plat_pos, plat_rot, plat_ang = plat_one['position'], plat_one['rotation'], rot_to_ang(plat_one['rotation'])
    if room_type in ['DiningRoom']:
        if plat_cate in ['边柜']:
            plat_cate = '餐边柜'
    elif room_type in ['KidsRoom']:
        if '书桌' in plat_cate or '书台' in plat_cate or '玄关台' in plat_cate:
            plat_cate = '儿童桌椅'
        elif '衣柜' in plat_cate or '柜' in plat_cate or '架' in plat_cate:
            plat_cate = '儿童柜架'
    # 平台分析
    flat_todo, tilt_todo = compute_plat_shape(plat_one, group_one)
    if len(tilt_todo) > 0:
        for tilt_idx in range(len(tilt_todo) - 1, -1, -1):
            tilt_one = tilt_todo[tilt_idx]
            if tilt_one[4] > 2.2 and tilt_one[4] > plat_size[1] * 0.8 and len(tilt_todo) > 1:
                tilt_todo.pop(tilt_idx)
            elif tilt_one[4] < 1.5 and tilt_one[4] < plat_size[1] * 0.6 and len(tilt_todo) > 1:
                tilt_todo.pop(tilt_idx)
            elif tilt_one[3] - tilt_one[0] < 0.25 and len(tilt_todo) > 1:
                tilt_todo.pop(tilt_idx)
        for tilt_idx in range(len(tilt_todo) - 1, -1, -1):
            tilt_one = tilt_todo[tilt_idx]
            for flat_idx in range(len(flat_todo) - 1, -1, -1):
                flat_one = flat_todo[flat_idx]
                if flat_one[0] >= tilt_one[3] - 0.05 or flat_one[3] <= tilt_one[0] + 0.05:
                    continue
                elif flat_one[1] >= tilt_one[4] - 0.05 or flat_one[4] <= tilt_one[1] - 0.05:
                    continue
                elif flat_one[2] >= tilt_one[5] + 0.05 or flat_one[5] <= tilt_one[2] - 0.05:
                    continue
                if flat_one[5] - flat_one[2] > 0.4:
                    flat_one[2] = (flat_one[2] + flat_one[5]) / 4
                elif flat_one[2] < tilt_one[2] + 0.10 < flat_one[5] - 0.10:
                    flat_one[2] = tilt_one[2] + 0.10
                flat_one[6] = min(flat_one[6], 0.3)
            pass

    # 装饰分析
    locate_info, napkin_dict = [], {}
    if group_type in ['Dining'] and plat_role in ['table']:
        deco_size = plat_size[:]
        if len(flat_todo) >= 1:
            deco_one = flat_todo[0]
            deco_size, deco_lift = [deco_one[3] - deco_one[0], deco_one[6], deco_one[5] - deco_one[2]], deco_one[1]
        locate_info = extract_furniture_locate(plat_one, [deco_size[0], deco_lift, deco_size[2]])
    object_dict, object_diff, object_more, napkin_lift = {}, {}, [], 0.002
    height_dict, height_used, height_more, height_list = {}, {}, {}, []

    for object_idx in range(len(object_list) - 1, -1, -1):
        object_one = object_list[object_idx]
        object_id = object_one['id']
        # 餐具处理
        if len(locate_info) >= 2:
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            # 餐巾处理
            if object_size[1] < 0.01 and object_size[0] < 1.00:
                continue
        # 其他处理
        if object_id not in object_dict:
            object_dict[object_id] = [object_one]
        else:
            object_dict[object_id].append(object_one)
    for object_one in object_wait:
        object_id = object_one['id']
        if have_furniture_by_cate(object_id, '鞋子') and plat_cate not in ['鞋柜']:
            continue
        if have_furniture_by_cate(object_id, '毛巾') and '浴室柜' not in plat_cate:
            continue
        origin_size = object_one['size']
        if abs(origin_size[0]) + abs(origin_size[2]) > 80:
            continue
        if object_id not in object_dict and object_id not in object_diff:
            object_diff[object_id] = object_one
    object_more = list(object_diff.values())
    if len(locate_info) >= 2:
        for object_idx in range(len(object_list) - 1, -1, -1):
            object_one = object_list[object_idx]
            object_id = object_one['id']
            # 餐巾处理
            if object_id in object_dict and len(object_dict[object_id]) == 4:
                object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                if object_size[1] < 0.01 and object_size[1] < napkin_lift and object_size[0] < 1.00:
                    napkin_lift = object_size[1]
    else:
        for object_one in object_list:
            if 'relate_shifting' not in object_one:
                continue
            object_shift = object_one['relate_shifting']
            object_y = int(object_shift[1] * 100)
            for height_key, height_val in height_dict.items():
                if abs(object_y - height_key) <= 5:
                    object_y = height_key
                    break
            if object_y not in height_dict:
                height_dict[object_y] = [object_one]
            else:
                height_dict[object_y].append(object_one)
        for object_one in object_wait:
            if 'relate_shifting' not in object_one:
                continue
            object_shift = object_one['relate_shifting']
            object_y = int(object_shift[1] * 100)
            for height_key, height_val in height_more.items():
                if abs(object_y - height_key) <= 5:
                    object_y = height_key
                    break
            if object_y not in height_more:
                height_more[object_y] = [object_one]
            else:
                height_more[object_y].append(object_one)

    # 餐具布局
    plant_width = 0.15
    if len(locate_info) == 2 and 'normal_position' in plat_one:
        deco_size, deco_lift = plat_size[:], plat_size[1]
        if len(flat_todo) >= 1:
            deco_one = flat_todo[0]
            deco_size, deco_lift = [deco_one[3] - deco_one[0], deco_one[6], deco_one[5] - deco_one[2]], deco_one[1]
        object_build, object_begin = [], plat_one['normal_position']
        locate_start, locate_count = locate_info[0], locate_info[1]
        object_cnt = 0
        for object_key, object_set in object_dict.items():
            object_cnt += 1
            if len(object_set) < 4:
                for object_one in object_set:
                    object_build.append(object_one)
                    # 桌布 花卉
                    if len(object_set) <= 1:
                        # 尺寸
                        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                        if min(object_size[0], object_size[2]) > min(deco_size[0], deco_size[2]) * 0.4:
                            ratio_new = min(deco_size[0], deco_size[2]) * 0.4 / min(object_size[0], object_size[2])
                            object_one['scale'][0] *= ratio_new
                            object_one['scale'][1] *= ratio_new
                            object_one['scale'][2] *= ratio_new
                        # 角度
                        if 'plants' in object_one['type']:
                            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                            if object_size[2] > object_size[0] * 1.02 or object_size[2] > object_size[0] + 0.02:
                                object_one['normal_rotation'] = [0, math.sin(math.pi / 2), 0, math.cos(math.pi / 2)]
                            else:
                                object_one['normal_rotation'] = [0, 0, 0, 1]
                continue
            object_one = object_set[0]
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_lift = 0
            if object_size[1] > napkin_lift > 0.0001:
                object_lift = max(napkin_lift, 0.0002)
                napkin_dict[object_key] = object_lift
            object_set = []
            if locate_count > 0:
                # 缩放
                if max(object_size[0], object_size[2]) > (deco_size[2] - plant_width) / 2:
                    object_ratio = (deco_size[2] - plant_width) / 2 / max(object_size[0], object_size[2])
                    object_one['scale'][0] *= object_ratio
                    object_one['scale'][1] *= object_ratio
                    object_one['scale'][2] *= object_ratio
                    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            for i in range(locate_count):
                object_new = copy_object(object_one)
                object_dis = deco_size[2] / 2 - object_size[2] / 2
                if object_dis < min(plat_size[0], plat_size[2]) / 2 - object_size[2] * 0.5 - 0.05:
                    object_dis = min(plat_size[0], plat_size[2]) / 2 - object_size[2] * 0.5 - 0.05
                object_ang = locate_start + i * math.pi * 2 / locate_count
                x, z = object_dis * math.sin(object_ang), object_dis * math.cos(object_ang)
                y = deco_lift + object_lift
                a = object_ang + 0
                object_new['relate_shifting'] = [x, y, z]
                object_new['normal_position'] = [object_begin[0] + x, object_begin[1] + y, object_begin[2] + z]
                object_new['normal_rotation'] = [0, math.sin(a / 2), 0, math.cos(a / 2)]
                object_set.append(object_new)
                object_build.append(object_new)
            # 更新
            object_dict[object_key] = object_set
        # 更新
        object_list = object_build
    elif len(locate_info) == 4 and 'normal_position' in plat_one:
        deco_size, deco_lift = plat_size[:], plat_size[1]
        if len(flat_todo) >= 1:
            deco_one = flat_todo[0]
            deco_size, deco_lift = [deco_one[3] - deco_one[0], deco_one[6], deco_one[5] - deco_one[2]], deco_one[1]
        object_build, object_begin = [], plat_one['normal_position']
        object_cnt = 0
        for object_key, object_set in object_dict.items():
            object_cnt += 1
            if len(object_set) < 4:
                for object_one in object_set:
                    object_build.append(object_one)
                    # 桌布 花卉
                    if len(object_set) <= 1:
                        # 尺寸
                        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                        if min(object_size[0], object_size[2]) > min(deco_size[0], deco_size[2]) * 0.4:
                            ratio_new = min(deco_size[0], deco_size[2]) * 0.4 / min(object_size[0], object_size[2])
                            object_one['scale'][0] *= ratio_new
                            object_one['scale'][1] *= ratio_new
                            object_one['scale'][2] *= ratio_new
                        # 角度
                        if 'plants' in object_one['type']:
                            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                            if object_size[2] > object_size[0] * 1.05 or object_size[2] > object_size[0] + 0.02:
                                object_one['normal_rotation'] = [0, math.sin(math.pi / 2), 0, math.cos(math.pi / 2)]
                            else:
                                object_one['normal_rotation'] = [0, 0, 0, 1]
                continue
            object_one = object_set[0]
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_lift = 0
            if object_size[1] > napkin_lift > 0.0001:
                object_lift = max(napkin_lift, 0.0002)
                napkin_dict[object_key] = object_lift
            object_set = []
            # 水平
            locate_space, object_space, locate_count = locate_info[0], locate_info[0], locate_info[1]
            if locate_count > 0:
                # 缩放
                if object_size[2] > (deco_size[2] - plant_width) / 2:
                    object_ratio_min = (deco_size[2] - plant_width) / 2 / object_size[2]
                    object_one['scale'][0] *= object_ratio_min
                    object_one['scale'][1] *= object_ratio_min
                    object_one['scale'][2] *= object_ratio_min
                    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if locate_count > 1:
                object_space = locate_space / (locate_count - 1)
                object_space_all = deco_size[0] - 0.3
                if object_space > object_space_all / locate_count:
                    object_space = object_space_all / locate_count
                    locate_space = object_space * (locate_count - 1)
            for i in range(locate_count):
                # 复制
                object_new_1 = copy_object(object_one)
                object_new_2 = copy_object(object_one)
                x, z = -locate_space / 2 + i * object_space, -deco_size[2] / 2 + object_size[2] / 2
                y = deco_lift + object_lift
                if object_size[2] < 0.1:
                    z += 0.05
                object_new_1['relate_shifting'] = [x, y, z]
                object_new_1['normal_position'] = [object_begin[0] + x, object_begin[1] + y, object_begin[2] + z]
                object_new_1['normal_rotation'] = [0, math.sin(math.pi / 2), 0, math.cos(math.pi / 2)]
                object_new_2['relate_shifting'] = [x, y, -z]
                object_new_2['normal_position'] = [object_begin[0] + x, object_begin[1] + y, object_begin[2] - z]
                object_new_2['normal_rotation'] = [0, math.sin(0 / 2), 0, math.cos(0 / 2)]
                object_set.append(object_new_1)
                object_build.append(object_new_1)
                object_set.append(object_new_2)
                object_build.append(object_new_2)
            # 竖直
            locate_space, object_space, locate_count = locate_info[2], locate_info[2], locate_info[3]
            if locate_count > 0:
                # 缩放
                if object_size[2] > (deco_size[0] - plant_width) / 2:
                    object_ratio_min = (deco_size[0] - plant_width) / 2 / object_size[2]
                    object_one['scale'][0] *= object_ratio_min
                    object_one['scale'][1] *= object_ratio_min
                    object_one['scale'][2] *= object_ratio_min
                    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if locate_count > 1:
                object_space = locate_space / (locate_count - 1)
                object_space_all = deco_size[2] - 0.3
                if object_space > object_space_all / locate_count:
                    object_space = object_space_all / locate_count
                    locate_space = object_space * (locate_count - 1)
            for i in range(locate_count):
                # 复制
                object_new_1 = copy_object(object_one)
                object_new_2 = copy_object(object_one)
                x, z = -deco_size[0] / 2 + object_size[2] / 2, -locate_space / 2 + i * object_space
                y = deco_lift + object_lift
                if object_size[2] < 0.1:
                    x += 0.05
                object_new_1['relate_shifting'] = [x, y, z]
                object_new_1['normal_position'] = [object_begin[0] + x, object_begin[1] + y, object_begin[2] + z]
                object_new_1['normal_rotation'] = [0, math.sin(-math.pi / 4), 0, math.cos(-math.pi / 4)]
                object_new_2['relate_shifting'] = [-x, y, z]
                object_new_2['normal_position'] = [object_begin[0] - x, object_begin[1] + y, object_begin[2] + z]
                object_new_2['normal_rotation'] = [0, math.sin(math.pi / 4), 0, math.cos(math.pi / 4)]
                object_set.append(object_new_1)
                object_build.append(object_new_1)
                object_set.append(object_new_2)
                object_build.append(object_new_2)
            # 更新
            object_dict[object_key] = object_set
        # 更新
        object_list = object_build
    if len(height_dict) <= 0:
        object_y = int(plat_size[1] * 100)
        height_dict[object_y] = object_list

    # 配饰布局
    deco_main = []
    object_done, object_fine, object_used, object_used_count, object_tooth_count = [], [], {}, 0, 0
    unique_base, unique_more, random_base = random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)
    unique_food_1 = ['酒具组合1', '食物', '食物组合', '花卉', '工艺品', '烛台']
    unique_food_2 = ['水杯', '水壶', '酒具', '茶具', '花卉', '食物', '盒子']
    unique_food_3 = ['水杯', '水壶', '酒具', '茶具', '花卉', '食物', '盒子']
    unique_work_1 = ['水杯', '水壶', '花卉', '杂志', '工艺品', '相框']
    unique_work_2 = ['水杯', '水壶', '书籍', '杂志', '工艺品', '相框', '配饰']
    unique_play_1 = ['相框', '书籍', '儿童台灯']
    unique_play_2 = ['闹钟', '玩具', '儿童工艺品']
    unique_make_1 = ['相框', '杂志', '化妆品组合1']
    unique_door_1 = ['酒具组合1', '茶具组合', '花卉', '工艺品', '相框', '盒子', '书籍组合2', '书籍组合3',
                     '包', '衣帽', '毛绒玩具']
    # 高低
    unique_lift_top, unique_lift_mid, unique_lift_bot, unique_high_bot = 1.5, 1.0, 0.5, 0.3
    unique_cate_mid = ['水壶', '酒具', '花卉', '相框', '毛巾']
    unique_cate_bot = ['盒子', '包', '衣帽', '毛绒玩具']
    # 平面
    unique_cate_pad = ['书籍', '杂志', '毛巾', '饰品']
    # 吧台
    unique_cate_bar = ['酒具组合1', '茶具组合', '花卉']
    # 儿童
    unique_cate_kid = ['玩具', '儿童工艺品', '儿童台灯']
    # 纠正
    if group_type in ['Meeting']:
        unique_food_1 = ['茶具组合', '花卉']
        unique_work_1 = ['花卉', '杂志', '工艺品']
        unique_work_2 = ['水杯', '水壶', '食物', '书籍', '相框']
    elif group_type in ['Rest']:
        unique_work_1 = ['水杯', '水壶', '花卉', '相框', '杂志']
        unique_work_2 = ['水杯', '水壶', '食物', '相框', '杂志']
    # 遍历布局
    for deco_idx, deco_one in enumerate(flat_todo):
        random.shuffle(unique_food_1)
        random.shuffle(unique_food_2)
        random.shuffle(unique_food_3)
        random.shuffle(unique_work_1)
        random.shuffle(unique_make_1)
        random.shuffle(unique_door_1)
        if deco_idx == 0:
            deco_main = deco_one[:]
        elif deco_idx <= 2 and abs(deco_one[1] - deco_main[1]) < 0.01:
            if abs(deco_one[2] - deco_main[2]) < 0.01 and abs(deco_one[5] - deco_main[5]) < 0.01:
                deco_main[0] = min(deco_main[0], deco_one[0])
                deco_main[3] = max(deco_main[3], deco_one[3])
        deco_size, deco_lift = [deco_one[3] - deco_one[0], deco_one[6], deco_one[5] - deco_one[2]], deco_one[1]
        deco_center = [(deco_one[0] + deco_one[3]) / 2, deco_one[1], (deco_one[2] + deco_one[5]) / 2]
        # 分层排除
        if plat_role in ['sofa', 'chair'] and group_type in ['Meeting', 'Rest'] and deco_idx >= 1:
            if deco_center[2] > 0 or deco_size[0] < 1:
                continue
        elif plat_role in ['table'] and group_type in ['Meeting', 'Rest'] and deco_idx >= 1:
            if deco_lift < 0.05:
                continue
            elif '餐桌' in plat_cate:
                continue
        elif plat_role in ['table'] and group_type in ['Dining'] and deco_idx >= 1:
            continue
        elif '梳妆台' in plat_cate and deco_idx >= 1:
            if deco_center[1] < 0.6 and deco_one[2] > 0:
                continue
            elif deco_center[1] < 0.1 and deco_size[0] < 0.2:
                continue
            elif deco_center[1] >= plat_size[1] - 0.01 and deco_center[1] > 1:
                continue
            if deco_center[1] > 0.6 and min(deco_size[0], deco_size[2]) < 0.2:
                deco_size[1] = deco_size[2]
        elif ('书桌' in plat_cate or '书柜' in plat_cate or '书架' in plat_cate) and deco_idx >= 1:
            if deco_lift < 0.1 and deco_size[1] < 0.1:
                continue
        elif ('浴室柜' in plat_cate or '洗衣机柜' in plat_cate) and deco_idx >= 1:
            if abs(deco_lift - deco_main[1]) < 0.25:
                if deco_one[0] > deco_main[3] - 0.05 or deco_one[3] < deco_main[0] + 0.05:
                    if deco_one[2] > 0:
                        continue
                    elif abs(deco_lift - deco_main[1]) < 0.05:
                        continue
                    if deco_one[3] < deco_main[0] + 0.05 and -deco_main[3] < deco_main[0]:
                        if deco_one[3] >= -deco_main[3] + 0.05:
                            continue
                    elif deco_one[0] > deco_main[3] - 0.05 and -deco_main[0] > deco_main[3]:
                        if deco_one[0] <= -deco_main[0] - 0.05:
                            continue
                elif deco_one[2] >= (deco_main[2] + deco_main[5]) / 2 or deco_main[2] < deco_one[2] < deco_main[2] + 0.4:
                    continue
                elif deco_one[5] <= (deco_main[2] + deco_main[5]) / 2 or deco_main[5] > deco_one[5] > deco_main[5] - 0.4:
                    continue
                elif deco_size[2] < (deco_main[5] - deco_main[2]) / 2:
                    continue
                elif deco_lift <= 0.1:
                    continue
            elif deco_lift >= plat_size[1] - 0.1 and deco_one[6] > 0.1:
                continue
            elif deco_size[1] > 0.30:
                deco_size[1] = 0.30
        # 分层排除
        if plat_role in ['table', 'side table', 'cabinet'] and deco_idx >= 1 and len(flat_todo) >= 3:
            # 过高
            if deco_lift >= plat_size[1] - 0.1 and deco_lift > 1.5:
                continue
            # 过窄
            elif deco_size[0] * 2 < deco_size[2] and deco_size[0] < 0.2:
                continue
            # 过矮
            elif deco_size[0] > 0.25 and deco_size[1] < 0.15:
                if '儿童' in plat_cate:
                    continue
        # 分层装饰
        object_todo, object_fine = object_list, []
        height_best, height_suit, height_fine = 0, 0, height_dict
        # 分层判断
        single_flag, unique_type = False, ''
        if deco_size[0] < UNIT_WIDTH_PLAT_SINGLE * 1.5 and len(object_todo) >= 1 \
                and plat_role in ['sofa', 'chair']:
            single_flag = True
        elif deco_size[0] < UNIT_WIDTH_PLAT_SINGLE and len(object_todo) >= 1 \
                and plat_role in ['cabinet', 'table', 'side table']:
            single_flag = True
        elif deco_size[0] < UNIT_WIDTH_PLAT_SINGLE * 1.0 and deco_size[2] > UNIT_WIDTH_PLAT_SINGLE * 1.5 \
                and plat_cate in ['玄关柜', '餐边柜']:
            single_flag = True
        elif deco_size[0] < UNIT_WIDTH_PLAT_SINGLE * 1.5 and deco_size[1] > UNIT_WIDTH_PLAT_SINGLE * 0.5 \
                and plat_cate in ['茶几', '茶桌', '玄关柜', '餐边柜']:
            single_flag = True
        elif deco_size[0] > UNIT_WIDTH_PLAT_SINGLE * 1.0 and deco_size[1] < UNIT_WIDTH_PLAT_SINGLE * 1.5 \
                and plat_cate in ['玄关柜', '餐边柜']:
            if deco_lift > unique_lift_top or deco_lift < unique_lift_bot:
                single_flag = True
        # 单独配饰
        if single_flag:
            object_one = copy_object(object_todo[0])
            unique_base += 1
            if plat_role in ['sofa', 'chair']:
                unique_type = '抱枕'
            elif group_type in ['Dining']:
                unique_type = '花卉'
            elif plat_role in ['table', 'side table'] and group_type in ['Meeting', 'Bed', 'Rest'] and deco_idx >= 1:
                unique_type = unique_work_1[deco_idx % len(unique_work_1)]
            elif '餐桌' in plat_cate:
                unique_type = unique_food_3[deco_idx % len(unique_food_3)]
            elif '儿童' in plat_cate and '桌' in plat_cate:
                if deco_size[0] > 0.30 and deco_size[2] > 0.20:
                    unique_type = unique_play_1[deco_idx % len(unique_play_1)]
                    if deco_lift <= unique_lift_bot - 0.1:
                        if deco_size[1] > 0.3:
                            unique_type = '毛绒玩具'
                        else:
                            unique_type = '书籍'
                    elif deco_lift >= unique_lift_mid + 0.1:
                        if deco_size[1] > 0.3:
                            unique_type = '毛绒玩具'
                        else:
                            unique_type = '书籍'
                else:
                    unique_type = unique_play_2[deco_idx % len(unique_play_2)]
                    if deco_lift <= unique_lift_bot:
                        if deco_size[1] > 0.3:
                            unique_type = '毛绒玩具'
                        else:
                            unique_type = '书籍'
                    if unique_type in ['闹钟']:
                        unique_play_2.remove(unique_type)
            elif '梳妆台' in plat_cate:
                if deco_size[0] > 0.20 and deco_size[2] > 0.20:
                    unique_type = unique_make_1[deco_idx % len(unique_make_1)]
                else:
                    unique_type = '化妆品'
            elif '梳妆台' in plat_cate:
                unique_type = '化妆品'
            elif '玄关柜' in plat_cate and deco_idx >= 1:
                if deco_lift <= unique_lift_bot - 0.1 and deco_size[1] < unique_high_bot:
                    unique_type = '鞋子'
                if deco_lift <= unique_lift_bot - 0.1 and deco_size[1] > unique_high_bot:
                    unique_type = unique_cate_bot[(deco_idx + 1) % len(unique_cate_bot)]
            elif '玄关柜' in plat_cate:
                unique_type = unique_door_1[deco_idx % len(unique_door_1)]
                if unique_type not in unique_cate_bot and deco_lift <= 0.5:
                    unique_type = unique_cate_bot[(deco_idx + 1) % len(unique_cate_bot)]
            elif '鞋柜' in plat_cate and deco_idx >= 1 and deco_lift <= 0.9 and deco_size[1] < 0.3:
                unique_type = '鞋子'
            elif '儿童' in plat_cate and '柜' in plat_cate:
                if deco_size[0] > 0.30 and deco_size[2] > 0.20:
                    unique_type = unique_play_1[deco_idx % len(unique_play_1)]
                    if deco_lift <= unique_lift_bot - 0.1:
                        unique_type = '毛绒玩具'
                    elif deco_lift >= unique_lift_mid + 0.1:
                        unique_type = '书籍'
                else:
                    unique_type = unique_play_2[deco_idx % len(unique_play_2)]
                    if unique_type in ['闹钟']:
                        unique_play_2.remove(unique_type)
            elif '书桌' in plat_cate or '书柜' in plat_cate or '书架' in plat_cate:
                if deco_size[0] > 0.4 and deco_lift < 0.5:
                    unique_type = '书籍组合3'
                elif deco_size[0] > 0.4:
                    unique_type = '书籍组合2'
                elif deco_size[0] > 0.15 and deco_size[2] > 0.2 and deco_lift > 0.5:
                    if deco_size[1] > 0.20:
                        unique_type = '书籍组合1'
                    else:
                        unique_type = '书籍'
                else:
                    unique_type = unique_work_1[deco_idx % len(unique_work_1)]
            elif '餐边柜' in plat_cate:
                if deco_size[1] > 0.20:
                    unique_type = unique_food_1[deco_idx % len(unique_food_1)]
                else:
                    unique_type = unique_food_2[deco_idx % len(unique_food_2)]
                if unique_type in unique_food_2 and deco_size[0] > UNIT_WIDTH_PLAT_SINGLE:
                    single_flag = False
            elif '浴室柜' in plat_cate or '洗衣机柜' in plat_cate:
                if deco_size[0] > UNIT_WIDTH_PLAT_SINGLE * 0.8 and deco_size[2] > UNIT_WIDTH_PLAT_SINGLE * 0.5:
                    unique_type = '洗浴品组合2'
                elif deco_size[0] > UNIT_WIDTH_PLAT_SINGLE * 0.5 and deco_size[2] > UNIT_WIDTH_PLAT_SINGLE * 0.5:
                    unique_type = '洗浴品组合1'
                else:
                    unique_type = '洗浴品'
            object_old = {}
            if not unique_type == '':
                unique_base += 1
                object_old = compute_deco_raise(unique_base, unique_type, '', object_used)
            elif len(object_more) > 0:
                object_old = object_more[unique_base % len(object_more)]
            if len(object_old) > 0:
                object_one['id'] = object_old['id']
                object_one['type'] = object_old['type']
                object_one['style'] = object_old['style']
                object_one['size'] = object_old['size'][:]
                object_one['scale'] = object_old['scale'][:]
                object_one['normal_rotation'] = [0, 0, 0, 1]
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_turn = False
            object_ratio_x = deco_size[0] / object_size[0]
            object_ratio_y = deco_size[1] / object_size[1] * 0.95
            object_ratio_z = deco_size[2] / object_size[2]
            if deco_size[2] > deco_size[0] * 1.5 and object_size[0] >= object_size[2] * 0.5:
                if '浴室柜' in plat_cate or '洗衣机柜' in plat_cate:
                    object_turn = False
                elif object_size[0] > object_size[2] * 0.5 and deco_size[0] > 0.2:
                    object_turn = False
                else:
                    object_turn = True
            if object_turn:
                object_ratio_x = deco_size[2] / object_size[0]
                object_ratio_y = deco_size[1] / object_size[1] * 0.95
                object_ratio_z = deco_size[0] / object_size[2]
                if deco_center[0] <= 0:
                    object_one['normal_rotation'] = [0, math.sin(-math.pi / 4), 0, math.cos(-math.pi / 4)]
                else:
                    object_one['normal_rotation'] = [0, math.sin(math.pi / 4), 0, math.cos(math.pi / 4)]
            object_ratio_min = min(object_ratio_x, object_ratio_y, object_ratio_z, 1)
            object_scale = object_one['scale']
            object_scale[0] *= object_ratio_min
            object_scale[1] *= object_ratio_min
            object_scale[2] *= object_ratio_min
            object_todo = [object_one]
        # 单层配饰
        else:
            if deco_idx >= len(height_fine):
                height_fine = height_more
            for height_key, height_val in height_fine.items():
                prior_new = len(height_val)
                if height_key in height_used:
                    prior_new = 0.1
                elif group_type in ['Work'] and deco_idx <= 0 and not 50 < height_key < 120:
                    prior_new = 0.0
                elif deco_idx >= 1:
                    height_best, height_suit = height_key, prior_new
                    break
                if prior_new >= height_suit:
                    height_best, height_suit = height_key, prior_new
            if height_best in height_fine:
                object_todo = height_fine[height_best]
            if group_type in ['Dining']:
                height_used[height_best] = 1
            elif group_type in ['Meeting'] and deco_idx <= 0:
                height_used[height_best] = 1
            elif plat_role in ['table', 'side table', 'cabinet']:
                if plat_role in ['table', 'side table'] and group_type in ['Meeting', 'Bed', 'Rest'] and deco_idx >= 1:
                    unique_type = ''
                elif '餐桌' in plat_cate:
                    unique_type = unique_food_3[deco_idx % len(unique_food_3)]
                elif '儿童' in plat_cate and '桌' in plat_cate:
                    if deco_size[0] > 0.20 and deco_size[2] > 0.20:
                        unique_type = '儿童工艺品'
                    else:
                        unique_type = '儿童配饰'
                elif '梳妆台' in plat_cate:
                    if random.randint(0, 10) < 2 and deco_idx <= 0 and deco_size[0] > 0.60 and deco_size[2] > 0.30:
                        unique_type = '化妆品组合3'
                    elif deco_size[0] > 0.25 and deco_size[2] > 0.25:
                        unique_type = '化妆品组合2'
                    elif deco_size[0] > 0.20 and deco_size[2] > 0.20:
                        unique_type = unique_make_1[deco_idx % len(unique_make_1)]
                    else:
                        unique_type = '化妆品'
                elif '玄关柜' in plat_cate:
                    if deco_idx >= 1 and deco_lift <= unique_lift_bot and deco_size[1] < unique_high_bot - 0.1:
                        unique_type = '鞋子'
                    else:
                        unique_type = ''
                elif '鞋柜' in plat_cate:
                    if deco_idx >= 1 and deco_lift <= unique_lift_mid - 0.2 and deco_size[1] < unique_high_bot:
                        unique_type = '鞋子'
                    else:
                        unique_type = ''
                elif '儿童' in plat_cate and '柜' in plat_cate:
                    if deco_size[0] > 0.20 and deco_size[2] > 0.20:
                        unique_type = '儿童工艺品'
                    else:
                        unique_type = '儿童配饰'
                elif '书桌' in plat_cate or '书柜' in plat_cate or '书架' in plat_cate:
                    if deco_idx <= 0:
                        if deco_size[0] > 0.20 and deco_size[2] > 0.20:
                            unique_type = unique_work_1[deco_idx % len(unique_work_1)]
                        else:
                            unique_type = '书籍'
                    elif min(deco_size[0], deco_size[1], deco_size[2]) > 0.15:
                        if deco_size[0] > 0.3 and deco_lift < 0.5:
                            unique_type = '书籍组合3'
                        elif deco_size[0] > 0.3:
                            unique_type = '书籍组合2'
                        elif deco_size[0] > 0.2:
                            unique_type = '书籍组合1'
                        elif deco_size[0] > 0.15 and deco_size[2] > 0.2 and deco_lift > 0.5:
                            unique_type = '书籍组合1'
                        else:
                            unique_type = '书籍'
                elif '餐边柜' in plat_cate:
                    if deco_size[1] > 0.20:
                        unique_type = unique_food_1[deco_idx % len(unique_food_1)]
                    else:
                        unique_type = unique_food_2[deco_idx % len(unique_food_2)]
                elif '浴室柜' in plat_cate or '洗衣机柜' in plat_cate:
                    if deco_size[0] > UNIT_WIDTH_PLAT_SINGLE * 0.8 and deco_size[2] > UNIT_WIDTH_PLAT_SINGLE * 0.5:
                        unique_type = '洗浴品组合2'
                        if deco_idx >= 1 and -0.05 < deco_lift - deco_main[1] < 0.05:
                            unique_type = '洗浴品组合1'
                    elif deco_size[0] > UNIT_WIDTH_PLAT_SINGLE * 0.5 and deco_size[2] > UNIT_WIDTH_PLAT_SINGLE * 0.5:
                        unique_type = '洗浴品组合1'
                    else:
                        unique_type = '洗浴品'
                # 规定品类
                unique_flag = False
                if deco_idx >= 1 and not unique_type == '':
                    unique_flag = True
                elif '洗浴品' in unique_type or '化妆品' in unique_type:
                    unique_flag = True
                if unique_flag:
                    object_one = copy_object(object_todo[0])
                    unique_base += 1
                    object_old = compute_deco_raise(unique_base, unique_type)
                    if len(object_old) > 0:
                        object_one['id'] = object_old['id']
                        object_one['type'] = object_old['type']
                        object_one['style'] = object_old['style']
                        object_one['size'] = object_old['size'][:]
                        object_one['scale'] = object_old['scale'][:]
                        object_one['normal_rotation'] = [0, 0, 0, 1]
                    object_todo = [object_one]
                # 扩展品类
                elif len(object_more) > 0 and height_best in height_used:
                    unique_base += 1
                    object_one = copy_object(object_more[unique_base % len(object_more)])
                    object_todo = [object_one]
                # 原有品类
                elif len(object_todo) > 0 and deco_idx <= 0 and group_type in ['Meeting', 'Media']:
                    height_used[height_best] = 1
                else:
                    height_used[height_best] = 1
                # 补充品类
                if unique_type in ['酒具', '酒具组合1', '酒具组合2', '茶具', '茶具组合', '食物', '食物组合',
                                   '花卉', '绿植', '工艺品', '烛台', '书籍', '书籍组合3', '杂志']:
                    unique_type = ''
                elif unique_type in ['书籍组合1', '书籍组合2']:
                    unique_type = '书籍组合1'
                elif '化妆品' in unique_type:
                    unique_type = '化妆品'
                elif '洗浴品组合2' in unique_type:
                    unique_type = '洗浴品组合1'
                elif '洗浴品' in unique_type:
                    unique_type = '洗浴品'
            else:
                height_used[height_best] = 1
        # 无效配饰
        if len(object_todo) <= 0:
            continue

        # 装饰整理
        if not single_flag:
            object_todo, unique_more = cluster_plat_raise(plat_one, group_one, deco_one, object_todo, object_more,
                                                          object_used, unique_more, unique_type)
        min_x, min_z, max_x, max_z, object_max, object_max_score = 10, 10, -10, -10, {}, 0
        for object_one in object_todo:
            if 'relate_shifting' not in object_one:
                continue
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            normal_ang = 0
            if 'normal_rotation' in object_one:
                normal_ang = rot_to_ang(object_one['normal_rotation'])
            object_width, object_depth = object_size[0], object_size[2]
            if abs(normal_ang - math.pi / 2) < 0.1 or abs(normal_ang + math.pi / 2) < 0.1:
                object_width, object_depth = object_size[2], object_size[0]
            object_shift = object_one['relate_shifting']
            tmp_x, tmp_z = object_shift[0], object_shift[2]
            min_x, min_z = min(min_x, tmp_x - object_width / 2), min(min_z, tmp_z - object_depth / 2)
            max_x, max_z = max(max_x, tmp_x + object_width / 2), max(max_z, tmp_z + object_depth / 2)
            # 最大装饰
            if len(object_max) < 0:
                object_max = object_one
                object_max_score = object_size[0] + object_size[1] + object_size[2]
            elif object_max_score < object_size[0] + object_size[1] + object_size[2]:
                object_max = object_one
                object_max_score = object_size[0] + object_size[1] + object_size[2]

        # 装饰调整
        dir_x, dir_z, dlt_x, dlt_z = 0, 0, 0, 0
        if group_type in ['Meeting', 'Rest'] and plat_role in ['sofa', 'chair']:
            dir_x, dir_z = 1, -1
            if deco_center[0] >= 0.3:
                dir_x = 1
            elif deco_center[0] <= -0.3:
                dir_x = -1
            if single_flag or deco_size[0] > min(2.0, (max_x - min_x) * 0.8):
                dir_x = 0
            if dir_x <= -1:
                new_x = deco_one[0]
                dlt_x = new_x - min_x
            elif dir_x >= 1:
                new_x = deco_one[3]
                dlt_x = new_x - max_x
            else:
                dlt_x = deco_center[0] - (min_x + max_x) / 2
            if dir_z <= -1:
                new_z = deco_one[2]
                dlt_z = new_z - min_z
            elif dir_z >= 1:
                new_z = deco_one[5]
                dlt_z = new_z - max_z
            else:
                dlt_z = deco_center[2] - (min_z + max_z) / 2
        elif group_type in ['Dining'] and plat_role in ['table']:
            dlt_x, dlt_z = 0, 0
        elif group_type in ['Meeting', 'Bed'] and plat_role in ['side table'] and len(object_max) > 0:
            new_x = object_max['relate_shifting'][0]
            new_z = object_max['relate_shifting'][2]
            dlt_x = deco_center[0] - new_x
            dlt_z = deco_center[2] - new_z
        else:
            if group_type in ['Media'] and plat_role in ['table']:
                if deco_idx >= 1 and deco_size[0] > UNIT_WIDTH_PLAT_SINGLE:
                    dir_x, dir_z = 1, -1
            elif group_type in ['Work'] and plat_role in ['table']:
                if max_x - min_x > deco_size[0]:
                    dir_x = 1
                if '书桌' in plat_cate or '书台' in plat_cate:
                    if deco_idx >= 1 and deco_size[0] < plat_size[0] * 0.5:
                        dir_x, dir_z = 1, -1
                if '玄关台' in plat_cate or '吧台' in plat_cate:
                    if deco_idx >= 1 and deco_size[0] < plat_size[0] * 0.5:
                        dir_x, dir_z = 1, -1
                if '梳妆台' in plat_cate:
                    if deco_idx <= 0:
                        dir_x = 1
                    if max(deco_size[0], deco_size[1], deco_size[2]) < 0.2:
                        dir_x, dir_z = 0, 0
                    elif deco_size[2] <= 0.2:
                        dir_x, dir_z = 1, -1
            elif group_type in ['Cabinet'] and plat_role in ['cabinet']:
                dir_x, dir_z = 1, -1
                if '玄关柜' in plat_cate and deco_idx >= 1 and deco_size[2] < deco_size[0] < deco_size[2] * 2:
                    dir_z = -1
                elif '餐边柜' in plat_cate and len(object_todo) <= 1 and deco_size[0] < deco_size[2]:
                    dir_z = 0
                elif '浴室柜' in plat_cate or '洗衣机柜' in plat_cate:
                    if abs(deco_lift - deco_main[1]) < 0.01 or deco_size[0] > deco_size[2] * 1.5:
                        if deco_center[0] > 0:
                            dir_x = 1
                        elif deco_center[0] < 0:
                            dir_x = -1
                        dir_z = -1
                elif min_z < deco_one[2]:
                    dir_z = -1
            elif group_type in ['Window'] and plat_role in ['window']:
                dir_x, dir_z = 1, -1
            if dir_x <= -1:
                new_x = deco_one[0] + min(deco_size[0] / 20, 0.02)
                dlt_x = new_x - min_x
            elif dir_x >= 1:
                new_x = deco_one[3] - min(deco_size[0] / 20, 0.02)
                dlt_x = new_x - max_x
            else:
                dlt_x = deco_center[0] - (min_x + max_x) / 2
            if dir_z <= -1:
                new_z = deco_one[2] + min(deco_size[2] / 20, 0.02)
                dlt_z = new_z - min_z
            elif dir_z >= 1:
                new_z = deco_one[5] - min(deco_size[2] / 10, 0.04)
                dlt_z = new_z - max_z
            else:
                dlt_z = deco_center[2] - (min_z + max_z) / 2

        # 装饰更新
        overlap_todo, overlap_dict = [], {}
        for object_idx, object_one in enumerate(object_todo):
            object_one = copy_object(object_one)
            if 'top_of' in object_one:
                object_one.pop('top_of')
            # 判断
            if 'relate_shifting' not in object_one:
                continue
            # 偏移
            object_id = object_one['id']
            object_cate = get_furniture_cate(object_id)
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_shift = object_one['relate_shifting']
            tmp_x, tmp_y, tmp_z = object_shift[0], object_shift[1], object_shift[2]
            tmp_x += dlt_x
            tmp_z += dlt_z
            tmp_y = deco_lift + 0.001
            # 微调
            if object_size[1] < 0.01:
                if max(tmp_x + object_size[0] / 2, tmp_x + object_size[2] / 2) > deco_one[3] - 0.02:
                    dlt_x_new = deco_one[3] - 0.02 - max(tmp_x + object_size[0] / 2, tmp_x + object_size[2] / 2)
                    tmp_x += dlt_x_new
                if min(tmp_x - object_size[0] / 2, tmp_x - object_size[2] / 2) < deco_one[0] + 0.02:
                    dlt_x_new = deco_one[0] + 0.02 - min(tmp_x - object_size[0] / 2, tmp_x - object_size[2] / 2)
                    tmp_x += dlt_x_new
            # 居中
            if group_type in ['Dining'] and plat_role in ['table']:
                if object_id in object_dict and len(object_dict[object_id]) == 1:
                    tmp_x, tmp_z = deco_center[0], deco_center[2]
            # 竖直
            if plat_role in ['table', 'side table', 'cabinet', 'appliance']:
                if object_id in napkin_dict:
                    tmp_y = deco_lift + napkin_dict[object_id]
            # 判断
            limit_width, limit_depth = 0.00, 0.00
            if plat_role in ['table'] and group_type in ['Dining']:
                pass
            elif plat_role in ['sofa', 'chair']:
                limit_width, limit_depth = 0.10, 0.10
                if tmp_x - object_size[0] / 2 < deco_one[0] - min(limit_width * 1.0, object_size[0] / 4):
                    continue
                if tmp_x + object_size[0] / 2 > deco_one[3] + min(limit_width * 1.0, object_size[0] / 4):
                    continue
                if tmp_z - object_size[2] / 2 < deco_one[2] - min(limit_depth * 0.2, object_size[2] / 4):
                    continue
                if tmp_z + object_size[2] / 2 > deco_one[5] + min(limit_depth * 1.5, object_size[2] / 4):
                    continue
            elif plat_role in ['side table'] and (len(object_todo) <= 1 or object_one == object_max):
                pass
            else:
                limit_width, limit_depth = 0.05, 0.05
                if group_type in ['Media']:
                    limit_width, limit_depth = 0.00, 0.00
                if get_furniture_cate(object_id) in ['化妆品组合1', '化妆品组合2', '化妆品组合3']:
                    pass
                elif len(object_todo) <= 1:
                    pass
                elif abs(tmp_x) + abs(tmp_z) <= 0.01 and plat_role in ['side table']:
                    pass
                elif tmp_x - object_size[0] / 2 < deco_one[0] - min(limit_width * 2, object_size[0] / 3):
                    continue
                elif tmp_x + object_size[0] / 2 > deco_one[3] + min(limit_width * 2, object_size[0] / 3):
                    continue
                elif tmp_z - object_size[2] / 2 < deco_one[2] - limit_depth:
                    continue
                elif tmp_z + object_size[2] / 2 > deco_one[5] + min(limit_depth * 2, object_size[2] / 2):
                    continue
            # 角度
            normal_ang = 0
            if 'normal_rotation' in object_one:
                normal_ang = rot_to_ang(object_one['normal_rotation'])
            if deco_size[0] * 1.5 < deco_size[2] and abs(tmp_x) > plat_size[0] / 3 and len(object_todo) <= 1:
                if '玄关柜' in plat_cate:
                    normal_ang = math.pi / 2
                    if tmp_x < 0:
                        normal_ang = -math.pi / 2
            # 缩放
            limit_width, limit_depth = 0.00, 0.00
            if plat_role in ['table'] and group_type in ['Dining']:
                pass
            else:
                # 边缘
                if plat_role in ['sofa', 'chair']:
                    limit_width, limit_depth = min(0.05, deco_size[0] / 10), min(0.05, deco_size[2] / 10)
                elif group_type in ['Media']:
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), -min(0.02, deco_size[2] / 20)
                elif '书桌' in plat_cate or '书台' in plat_cate or '玄关台' in plat_cate or '吧台' in plat_cate:
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), 0
                elif '梳妆台' in plat_cate and deco_idx <= 0:
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), -min(0.02, deco_size[2] / 20)
                elif '玄关柜' in plat_cate and (deco_lift > unique_lift_top or deco_lift < unique_lift_bot):
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), -min(0.04, deco_size[2] / 10)
                elif '玄关柜' in plat_cate:
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), -min(0.02, deco_size[2] / 20)
                elif '鞋柜' in plat_cate:
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), -min(0.02, deco_size[2] / 20)
                elif '书柜' in plat_cate or '书架' in plat_cate:
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), 0
                elif '餐边柜' in plat_cate:
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), -min(0.02, deco_size[2] / 20)
                elif deco_lift < plat_size[1] - 0.1:
                    limit_width, limit_depth = -min(0.02, deco_size[0] / 20), 0
                # 缩放
                object_ratio_x, object_ratio_z = 1, 1
                object_width, object_depth = object_size[0], object_size[2]
                if abs(normal_ang - math.pi / 2) < 0.1 or abs(normal_ang + math.pi / 2) < 0.1:
                    object_width, object_depth = object_size[2], object_size[0]
                # 横向
                object_ratio_x, object_shift_x = 1, 0
                push_flag, pull_flag = False, False
                if tmp_x - object_width / 2 < deco_one[0] - limit_width:
                    object_ratio_x -= (deco_one[0] - limit_width - (tmp_x - object_width / 2)) / object_width
                    object_shift_x += (deco_one[0] - limit_width - (tmp_x - object_width / 2)) / 2
                    pull_flag = True
                if tmp_x + object_width / 2 > deco_one[3] + limit_width:
                    object_ratio_x -= (tmp_x + object_width / 2 - (deco_one[3] + limit_width)) / object_width
                    object_shift_x -= (tmp_x + object_width / 2 - (deco_one[3] + limit_width)) / 2
                    push_flag = True
                if push_flag and pull_flag:
                    tmp_x = deco_center[0]
                else:
                    tmp_x += object_shift_x
                # 纵向
                object_ratio_z, object_shift_z = 1, 0
                push_flag, pull_flag = False, False
                if tmp_z - object_depth / 2 < deco_one[2] - limit_depth:
                    object_ratio_z -= (deco_one[2] - limit_depth - (tmp_z - object_depth / 2)) / object_depth
                    object_shift_z += (deco_one[2] - limit_depth - (tmp_z - object_depth / 2)) / 2
                    pull_flag = True
                if tmp_z + object_depth / 2 > deco_one[5] + limit_depth:
                    object_ratio_z -= (tmp_z + object_depth / 2 - (deco_one[5] + limit_depth)) / object_depth
                    object_shift_z -= (tmp_z + object_depth / 2 - (deco_one[5] + limit_depth)) / 2
                    push_flag = True
                if push_flag and pull_flag:
                    tmp_z = deco_center[2]
                else:
                    tmp_z += object_shift_z
                # 缩放
                object_ratio = min(object_ratio_x, object_ratio_z, 1)
                object_scale = object_one['scale']
                object_scale[0] *= object_ratio
                object_scale[1] *= object_ratio
                object_scale[2] *= object_ratio
            # 尺寸
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if deco_size[1] < object_size[1]:
                object_ratio = deco_size[1] / object_size[1] * 0.95
                object_scale = object_one['scale']
                object_scale[0] *= object_ratio
                object_scale[1] *= object_ratio
                object_scale[2] *= object_ratio
            # 替换
            replace_type = ''
            if object_id in UNIT_SCALE_ERROR:
                replace_type = object_cate
            if plat_role in ['side table'] and 'plants' in object_one['type']:
                replace_type = '花卉'
            elif group_type in ['Dining'] and plat_role in ['table']:
                if object_id in object_dict and len(object_dict[object_id]) == 1 and object_size[1] > 0.05:
                    replace_type = '花卉'
            elif object_cate in ['玩具']:
                if group_type in ['Meeting', 'Rest']:
                    replace_type = unique_work_2[object_idx % len(unique_work_2)]
            elif object_cate in ['儿童工艺品']:
                if group_type in ['Meeting', 'Rest']:
                    replace_type = '花卉'
            elif object_cate in ['鞋子']:
                if plat_cate in ['鞋柜'] and deco_idx > 0:
                    pass
                elif plat_cate in ['玄关柜'] and deco_lift < unique_lift_bot:
                    pass
                elif group_type in ['Meeting', 'Work', 'Media']:
                    replace_type = unique_work_2[object_idx % len(unique_work_2)]
                elif group_type in ['Cabinet'] and deco_lift >= 1:
                    replace_type = unique_work_2[object_idx % len(unique_work_2)]
                elif group_type in ['Cabinet'] and deco_idx <= 0:
                    replace_type = unique_work_2[object_idx % len(unique_work_2)]
                elif object_id in object_used:
                    replace_type = '鞋子'
            elif object_cate in ['毛巾']:
                if group_type in ['Meeting', 'Work', 'Media']:
                    replace_type = unique_work_2[object_idx % len(unique_work_2)]
                elif '浴室柜' not in plat_cate and '玄关柜' not in plat_cate:
                    replace_type = unique_work_2[object_idx % len(unique_work_2)]
                elif object_id in object_used:
                    replace_type = '毛巾'
            elif object_cate in ['酒具', '酒具组合1', '酒具组合2', '茶具', '茶具组合', '食物组合', '花卉']:
                random_base += 1
                if '玄关柜' in plat_cate:
                    if deco_lift < unique_lift_mid:
                        replace_type = unique_cate_bot[random_base % len(unique_cate_bot)]
                    elif deco_size[1] < object_size[1] * 0.8 or deco_size[1] < 0.15:
                        replace_type = unique_cate_pad[random_base % len(unique_cate_pad)]
                    elif object_id in object_used:
                        replace_type = unique_cate_mid[random_base % len(unique_cate_mid)]
                elif '鞋柜' in plat_cate:
                    replace_type = unique_cate_bot[random_base % len(unique_cate_bot)]
                elif '儿童' in plat_cate:
                    replace_type = unique_cate_kid[random_base % len(unique_cate_kid)]
                    if object_cate in ['花卉']:
                        replace_type = '儿童台灯'
            elif object_cate in ['书籍', '书籍组合1', '书籍组合2', '书籍组合3']:
                random_base += 1
                if '茶桌' in plat_cate or '茶几' in plat_cate:
                    if object_cate in ['书籍组合2', '书籍组合3']:
                        replace_type = unique_food_1[random_base % len(unique_food_1)]
                    elif object_size[0] > 0.20 and object_size[1] > 0.20:
                        replace_type = unique_work_1[random_base % len(unique_work_1)]
                    else:
                        replace_type = unique_work_2[random_base % len(unique_work_2)]
                elif '玄关柜' in plat_cate:
                    if single_flag:
                        replace_type = unique_door_1[random_base % len(unique_door_1)]
                    elif deco_lift < unique_lift_bot:
                        replace_type = unique_cate_bot[random_base % len(unique_cate_bot)]
                    else:
                        replace_type = unique_cate_mid[random_base % len(unique_cate_mid)]
                elif '餐边柜' in plat_cate:
                    if single_flag:
                        replace_type = unique_food_1[random_base % len(unique_food_1)]
                    elif object_size[0] > 0.20 and object_size[1] > 0.20:
                        replace_type = unique_food_1[random_base % len(unique_food_1)]
                    else:
                        replace_type = unique_food_2[random_base % len(unique_food_2)]
                elif '儿童' in plat_cate and object_cate in ['书籍组合1', '书籍组合2', '书籍组合3']:
                    if object_size[0] > 0.20 and object_size[1] > 0.20:
                        if deco_lift > unique_lift_mid + 0.1:
                            replace_type = '书籍'
                        else:
                            replace_type = unique_play_1[random_base % len(unique_play_1)]
                    else:
                        replace_type = unique_play_2[random_base % len(unique_play_2)]
                        if unique_type in ['闹钟']:
                            unique_play_2.remove(unique_type)
                scale_min = min(object_one['scale'][0], object_one['scale'][1], object_one['scale'][2])
                if scale_min < 0.60 and replace_type == '':
                    if object_cate in ['书籍组合1', '书籍组合2', '书籍组合3']:
                        replace_type = '书籍'
                    else:
                        replace_type = unique_work_2[object_idx % len(unique_work_2)]
                elif object_id in object_used:
                    replace_type = object_cate
            elif object_cate in ['电脑']:
                random_base += 1
                if '玄关柜' in plat_cate:
                    replace_type = unique_cate_bot[random_base % len(unique_cate_bot)]
            elif object_cate in ['化妆品', '化妆品组合1', '化妆品组合2', '化妆品组合3']:
                random_base += 1
                if '吧台' in plat_cate:
                    replace_type = unique_cate_bar[random_base % len(unique_cate_bar)]
                elif '玄关柜' in plat_cate:
                    replace_type = unique_cate_bot[random_base % len(unique_cate_bot)]
                elif '梳妆台' in plat_cate:
                    pass
                else:
                    replace_type = unique_cate_bot[random_base % len(unique_cate_bot)]
            elif object_cate in ['洗浴品', '洗浴品组合1', '洗浴品组合2']:
                if '浴室柜' in plat_cate:
                    if object_tooth_count < 2 and 0.5 < deco_lift < 1.5:
                        if abs(deco_center[0]) > 0.2 and object_size[0] > 0.1:
                            object_tooth_count += 1
                            replace_type = '牙刷'
                else:
                    pass
            elif object_id in object_used:
                if plat_role in ['table', 'cabinet'] and group_type not in ['Dining']:
                    random_base += 1
                    if '玄关柜' in plat_cate:
                        if deco_lift > unique_lift_mid:
                            replace_type = unique_cate_mid[random_base % len(unique_cate_mid)]
                        else:
                            replace_type = unique_cate_bot[random_base % len(unique_cate_bot)]
                    elif '儿童' in plat_cate:
                        if object_cate in ['儿童工艺品']:
                            replace_type = '相框'
                        else:
                            replace_type = unique_type
                    elif unique_type == '':
                        replace_type = unique_work_2[random_base % len(unique_work_2)]
                    else:
                        replace_type = unique_type
            elif min(object_one['scale'][0], object_one['scale'][1], object_one['scale'][2]) < 0.7:
                if plat_role in ['table', 'cabinet'] and group_type not in ['Dining']:
                    if '玄关柜' in plat_cate:
                        if deco_lift < unique_lift_bot:
                            replace_type = unique_cate_bot[object_idx % len(unique_cate_bot)]
                        else:
                            replace_type = '饰品'
                    elif unique_type == '':
                        replace_type = unique_work_2[object_idx % len(unique_work_2)]
                    elif '酒具组合2' in object_cate:
                        replace_type = '酒具组合1'
                    elif '酒具组合1' in object_cate:
                        replace_type = '酒具'
                    elif '化妆品组合1' in object_cate:
                        replace_type = '化妆品'
                    elif '化妆品组合' in object_cate:
                        replace_type = '化妆品组合1'
                    elif '洗浴品组合1' in object_cate:
                        replace_type = '洗浴品'
                    elif '洗浴品组合' in object_cate:
                        replace_type = '洗浴品组合1'
                    elif '化妆品' in object_cate or '洗浴品' in object_cate:
                        continue
                    else:
                        replace_type = unique_type
            elif group_type in ['Work'] and plat_role in ['table'] and deco_idx == 0 and \
                    min(object_size[0], object_size[1]) > 0.3:
                if '电脑' in object_cate:
                    replace_type = ''
                elif '梳妆台' in plat_cate:
                    replace_type = ''
                elif '儿童' in plat_cate:
                    replace_type = '台灯'
                else:
                    replace_type = '花卉'
            # 替换
            if not replace_type == '':
                unique_base += 1
                object_new = compute_deco_raise(unique_base, replace_type, '', object_used)
                if len(object_new) > 0:
                    if object_new['id'] in UNIT_SCALE_ERROR:
                        unique_base += 1
                        object_new = compute_deco_raise(unique_base, replace_type, '', object_used)
                if len(object_new) > 0:
                    object_one['id'] = object_new['id']
                    object_one['type'] = object_new['type']
                    object_one['style'] = object_new['style']
                    object_one['size'] = object_new['size'][:]
                    object_one['scale'] = object_new['scale'][:]
                    size_new = object_one['size']
                    if abs(normal_ang - math.pi / 2) < 0.1 or abs(normal_ang + math.pi / 2) < 0.1:
                        object_ratio_x = (deco_size[2] + limit_depth * 1) * 100 / size_new[0]
                        object_ratio_z = object_size[2] * 100 / size_new[2]
                        if len(object_todo) <= 1:
                            object_ratio_z = deco_size[0] * 100 / size_new[2]
                    else:
                        object_ratio_x = object_size[0] * 100 / size_new[0]
                        object_ratio_z = (deco_size[2] + limit_depth * 1) * 100 / size_new[2]
                        if len(object_todo) <= 1:
                            object_ratio_x = deco_size[0] * 100 / size_new[0]
                    object_ratio_y = deco_size[1] * 100 / size_new[1]
                    object_ratio = min(object_ratio_x, object_ratio_z, object_ratio_y, 1.1)
                    object_one['scale'] = [object_ratio, object_ratio, object_ratio]
                object_cate = replace_type
            # 缩放
            scale_new = object_one['scale']
            if object_one['id'] in UNIT_SCALE_LOWER and max(scale_new[0], scale_new[1], scale_new[2]) > 0.8:
                object_one['scale'] = [0.8, 0.8, 0.8]
            elif object_one['id'] in UNIT_SCALE_UPPER and max(scale_new[0], scale_new[1], scale_new[2]) < 1.2:
                object_one['scale'] = [1.2, 1.2, 1.2]
            object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if min(scale_new[0], scale_new[1], scale_new[2]) < 0.60:
                if '玄关柜' in plat_cate and max(object_size[0], object_size[2]) < 0.15:
                    continue
            object_depth = object_size[2]
            if abs(normal_ang - math.pi / 2) < 0.1 or abs(normal_ang + math.pi / 2) < 0.1:
                object_depth = object_size[0]
            # 判断
            if unique_type in ['酒具', '酒具组合1', '酒具组合2']:
                tmp_z = deco_center[2]
                object_scale = object_one['scale']
                if min(object_scale[0], object_scale[1], object_scale[2]) < 0.80:
                    object_one['scale'] = [0.80, object_scale[1], 0.80]
                if tmp_z - object_depth / 2 < deco_one[2]:
                    tmp_z = deco_one[2] + object_depth / 2
            elif unique_type in ['花卉', '烛台'] and object_depth < deco_size[2]:
                if tmp_z - object_depth / 2 < deco_one[2]:
                    tmp_z = deco_one[2] + object_depth / 2
            # 位置
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
            object_one['normal_position'] = [normal_pos[0] + tmp_x, normal_pos[1] + tmp_y, normal_pos[2] + tmp_z]
            object_one['relate_shifting'] = [tmp_x, tmp_y, tmp_z]
            # 朝向
            if group_type in ['Media', 'Work', 'Cabinet']:
                if abs(object_size[0] - object_size[2]) < 0.01 and deco_size[0] >= deco_size[2]:
                    object_one['normal_rotation'] = [0, 0, 0, 1]
                    normal_ang = 0
                elif abs(object_size[0] - object_size[2]) < 0.20 and max(object_size[0], object_size[2]) < 0.30:
                    if abs(ang_to_ang(normal_ang)) > math.pi / 2 * 0.9 and deco_size[0] >= deco_size[2]:
                        object_one['normal_rotation'] = [0, 0, 0, 1]
                        normal_ang = 0
            elif group_type in ['Window'] and 'pillow' in object_one['type']:
                normal_ang += math.pi
                object_one['normal_rotation'] = [0, math.sin(normal_ang / 2), 0, math.cos(normal_ang / 2)]
            elif plat_role in ['side table'] and 'lamp' in object_one['type']:
                normal_ang = 0
                object_one['normal_rotation'] = [0, 0, 0, 1]
            object_ang = plat_ang + normal_ang
            object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
            object_one['rotation'] = object_rot
            # 添加
            object_one['group'] = group_type
            object_one['relate'] = plat_one['id']
            object_one['relate_role'] = plat_role
            object_one['relate_position'] = plat_one['position'][:]
            if 'obj_list' not in group_one:
                group_one['obj_list'] = []
            group_one['obj_list'].append(object_one)
            object_done.append(object_one)
            object_fine.append(object_one)
            object_id = object_one['id']
            if object_id not in object_used:
                object_used[object_id] = 1
            else:
                object_used[object_id] += 1
            object_used_count += 1

        # 装饰居中
        center_flag = False
        if plat_role in ['table', 'cabinet', 'side table'] and len(object_fine) == 1:
            center_flag = True
        if center_flag:
            object_one = object_fine[0]
            object_shift = object_one['relate_shifting']
            tmp_x, tmp_y, tmp_z = object_shift[0], object_shift[1], object_shift[2]
            tmp_x = deco_center[0]
            if deco_size[0] * 1.5 < deco_size[2]:
                tmp_z = deco_center[2]
            # 位置
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
            object_one['normal_position'] = [normal_pos[0] + tmp_x, normal_pos[1] + tmp_y, normal_pos[2] + tmp_z]
            object_one['relate_shifting'] = [tmp_x, tmp_y, tmp_z]
            # 朝向
            if deco_size[0] * 1.2 > deco_size[2]:
                normal_ang = 0
                object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                if object_size[0] * 1.5 < object_size[2]:
                    normal_ang = math.pi / 2
                object_one['normal_rotation'] = [0, math.sin(normal_ang / 2), 0, math.cos(normal_ang / 2)]
                object_ang = plat_ang + normal_ang
                object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
                object_one['rotation'] = object_rot
            elif deco_size[0] * 1.5 < deco_size[2] and abs(tmp_x) > plat_size[0] / 3:
                if '玄关柜' in plat_cate:
                    normal_ang = math.pi / 2
                    if tmp_x < 0:
                        normal_ang = -math.pi / 2
                    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                    if object_size[0] * 1.5 < object_size[2]:
                        normal_ang = 0
                    object_one['normal_rotation'] = [0, math.sin(normal_ang / 2), 0, math.cos(normal_ang / 2)]
                    object_ang = plat_ang + normal_ang
                    object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
                    object_one['rotation'] = object_rot
        # 装饰靠后
        backto_flag = False
        if plat_role in ['sofa', 'chair'] and len(object_fine) < len(object_todo):
            backto_flag = True
        if backto_flag:
            pass

        # 装饰尺寸
        for object_idx, object_one in enumerate(object_fine):
            if group_type in ['Dining']:
                size_max, size_dir = object_one['size'][:], [0, 0, 0]
                size_max[0] = min(max(size_max[0], deco_size[0] * 30), deco_size[0] * 50)
                size_max[2] = min(max(size_max[2], deco_size[2] * 30), deco_size[2] * 50)
                size_max[1] = deco_size[1] * 100
                object_one['size_max'] = size_max
                object_one['size_dir'] = size_dir
                continue
            object_type = object_one['type']
            object_cate = get_furniture_cate(object_one['id'])
            pass
            # 尺寸信息
            limit_x, limit_z = -min(0.02, deco_size[0] / 20), -min(0.02, deco_size[2] / 20)
            object_x_min, object_z_min = deco_one[0] - limit_x, deco_one[2] - limit_z
            object_x_max, object_z_max = deco_one[3] + limit_x, deco_one[5] + limit_z
            shift_one = object_one['relate_shifting']
            size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            object_z_add = 0
            # 左侧避碰
            for aside_idx in [object_idx - 1]:
                if plat_cate in ['sofa', 'chair']:
                    break
                elif aside_idx < 0 or aside_idx >= len(object_fine):
                    continue
                object_1 = object_fine[aside_idx]
                shift_1 = object_1['relate_shifting']
                size_1 = [abs(object_1['size'][i] * object_1['scale'][i]) / 100 for i in range(3)]
                if shift_1[0] + size_1[0] / 2 <= shift_one[0] - size_one[0] / 2:
                    continue
                object_z_add_1 = 0
                if shift_1[0] - size_1[0] / 2 >= shift_one[0] + size_one[0] / 2:
                    object_x_max = min(object_x_max, (shift_1[0] - size_1[0] / 2 + shift_one[0] + size_one[0] / 2) / 2)
                elif shift_1[2] + size_1[2] / 2 <= shift_one[2] - size_one[2] / 2:
                    object_z_min = max(object_z_min, shift_1[2] + size_1[2] / 2)
                elif shift_1[2] - size_1[2] / 2 >= shift_one[2] + size_one[2] / 2:
                    object_z_max = min(object_z_max, shift_1[2] - size_1[2] / 2)
                elif shift_1[2] <= shift_one[2]:
                    object_z_min = max(object_z_min, shift_1[2] + size_2[2] / 2 * 1.0)
                    object_z_min = min(object_z_min, deco_one[5] - size_one[2] / 2 + limit_z)
                    object_z_add_1 = object_z_min - (shift_one[2] - size_one[2] / 2)
                elif shift_1[2] >= shift_one[2]:
                    object_z_max = min(object_z_max, shift_1[2] - size_2[2] / 2 * 1.0)
                    object_z_max = max(object_z_max, deco_one[2] + size_one[2] / 2 - limit_z)
                    object_z_add_1 = object_z_max - (shift_one[2] + size_one[2] / 2)
                if abs(object_z_add_1) > abs(object_z_add):
                    object_z_add = object_z_add_1
            # 右侧避碰
            for aside_idx in [object_idx + 1]:
                if plat_cate in ['sofa', 'chair']:
                    break
                elif aside_idx < 0 or aside_idx >= len(object_fine):
                    continue
                object_2 = object_fine[aside_idx]
                shift_2 = object_2['relate_shifting']
                size_2 = [abs(object_2['size'][i] * object_2['scale'][i]) / 100 for i in range(3)]
                if shift_2[0] - size_2[0] / 2 >= shift_one[0] + size_one[0] / 2:
                    continue
                object_z_add_2 = 0
                if shift_2[0] + size_2[0] / 2 <= shift_one[0] - size_one[0] / 2:
                    object_x_min = max(object_x_min, (shift_2[0] + size_2[0] / 2 + shift_one[0] - size_one[0] / 2) / 2)
                elif shift_2[2] + size_2[2] / 2 <= shift_one[2] - size_one[2] / 2:
                    object_z_min = max(object_z_min, shift_2[2] + size_2[2] / 2)
                elif shift_2[2] - size_2[2] / 2 >= shift_one[2] + size_one[2] / 2:
                    object_z_max = min(object_z_max, shift_2[2] - size_2[2] / 2)
                elif shift_2[2] <= shift_one[2]:
                    object_z_min = max(object_z_min, shift_2[2] + size_2[2] / 2 * 1.0)
                    object_z_min = min(object_z_min, deco_one[5] - size_one[2] / 2 + limit_z)
                    object_z_add_2 = object_z_min - (shift_one[2] - size_one[2] / 2)
                elif shift_2[2] >= shift_one[2]:
                    object_z_max = min(object_z_max, shift_2[2] - size_2[2] / 2 * 1.0)
                    object_z_max = max(object_z_max, deco_one[2] + size_one[2] / 2 - limit_z)
                    object_z_add_2 = object_z_max - (shift_one[2] + size_one[2] / 2)
                if abs(object_z_add_2) > abs(object_z_add):
                    object_z_add = object_z_add_2
            # 避免碰撞
            if abs(object_z_add) > 0.01:
                tmp_x, tmp_y, tmp_z = shift_one[0], shift_one[1], shift_one[2]
                tmp_z += object_z_add
                # 位置
                add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
                add_y = tmp_y
                add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
                object_pos = [plat_pos[0] + add_x, plat_pos[1] + add_y, plat_pos[2] + add_z]
                object_one['position'] = object_pos
                object_one['normal_position'] = [normal_pos[0] + tmp_x, normal_pos[1] + tmp_y, normal_pos[2] + tmp_z]
                object_one['relate_shifting'] = [tmp_x, tmp_y, tmp_z]
            # 尺寸关系
            size_max_rat = 1.5
            if len(object_fine) <= 1:
                size_max_rat = 2.0
            size_max = size_one[:]
            size_max_x, size_max_z = object_x_max - object_x_min, object_z_max - object_z_min
            size_max[0] = int(max(size_max[0], min(size_max_x, size_max[0] * size_max_rat)) * 100)
            size_max[1] = int(deco_size[1] * 100 - 2)
            size_max[2] = int(max(size_max[2], min(size_max_z, size_max[2] * size_max_rat)) * 100)
            object_one['size_max'] = size_max
            if 'pillow' in object_type:
                size_max[0] = max(size_max[0], int(size_one[0] * 150))
                size_max[1] = max(size_max[1], int(size_one[1] * 150))
                size_max[2] = max(size_max[2], int(size_one[2] * 150))
                pass
            # 依靠关系
            angle_one = 0
            if 'normal_rotation' in object_one:
                angle_one = rot_to_ang(object_one['normal_rotation'])
            object_width, object_depth = size_one[0], size_one[2]
            if abs(angle_one - math.pi / 2) < 0.1 or abs(angle_one + math.pi / 2) < 0.1:
                object_width, object_depth = size_one[2], size_one[0]
            size_dir = [0, 0, 0]
            if abs(shift_one[0] - object_width - object_x_min) <= 0.02:
                size_dir[0] = -1
            elif abs(shift_one[0] + object_width - object_x_max) <= 0.02:
                size_dir[0] = 1
            if abs(shift_one[2] - object_depth - object_z_min) <= 0.02:
                size_dir[2] = -1
            elif abs(shift_one[2] + object_depth - object_z_max) <= 0.02:
                size_dir[2] = 1
            if deco_size[0] < 0.15 and len(object_fine) <= 1:
                size_dir[0] = 0
            if deco_size[2] < 0.15 and len(object_fine) <= 1:
                size_dir[2] = 0
            if '梳妆台' in plat_cate and max(object_width, object_depth) > 0.2:
                size_dir[2] = -1
            elif ('书桌' in plat_cate or '书柜' in plat_cate or '书架' in plat_cate) and '书籍' in object_cate:
                size_dir[2] = -1
            elif 'pillow' in object_type:
                size_dir[2] = -1
            if object_idx == 0 and len(object_fine) > 1 and size_dir[0] == 0:
                shift_side_1 = shift_one[0] - object_x_min
                shift_side_2 = object_x_max - shift_one[0]
                if shift_side_1 > shift_side_2 + 0.05:
                    size_dir[0] = 1
                elif shift_side_1 < shift_side_2 + 0.01:
                    size_dir[0] = -1
                if size_dir[0] == 0 and 'pillow' in object_type:
                    size_dir[0] = 1
            elif object_idx == len(object_fine) - 1 and len(object_fine) > 1 and size_dir[0] == 0:
                shift_side_1 = shift_one[0] - object_x_min
                shift_side_2 = object_x_max - shift_one[0]
                if shift_side_2 > shift_side_1 + 0.05:
                    size_dir[0] = -1
                elif shift_side_2 < shift_side_1 + 0.01:
                    size_dir[0] = 1
                if size_dir[0] == 0 and 'pillow' in object_type:
                    size_dir[0] = -1
            object_one['size_dir'] = size_dir

    # 挂饰布局
    if plat_cate in ['玄关柜', '衣柜'] and len(tilt_todo) > 0:
        unique_main, unique_rest = '挂饰', '挂饰'
        for deco_idx, deco_one in enumerate(tilt_todo):
            deco_mid_x = (deco_one[0] + deco_one[3]) / 2
            deco_top, deco_bak = deco_one[4] - min(0.15, (deco_one[4] - deco_size[1]) / 10), deco_one[2]
            deco_size = [deco_one[3] - deco_one[0] - 0.04, deco_top - deco_one[1], deco_one[6]]
            if deco_size[0] > 0.4:
                if plat_cate in ['玄关柜']:
                    unique_main = '玄关挂饰'
                elif plat_cate in ['衣柜']:
                    unique_main = '衣柜挂饰'
            # 全部挂饰
            object_one, size_one, object_two, size_two = {}, [], {}, []
            # 主要挂饰
            object_one = {
                'id': '', 'type': '', 'style': '', 'size': [10, 10, 10], 'scale': [1, 1, 1],
                'position': [0, 0, 0], 'rotation': [0, 0, 0, 1], 'role': '', 'group': ''
            }
            random_base += 1
            object_new = compute_deco_raise(random_base, unique_main, '', [])
            if len(object_new) > 0:
                size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                if deco_size[1] < size_new[1] * 0.9:
                    random_base += 1
                    object_new = compute_deco_raise(random_base, unique_main, '', [])
            if len(object_new) > 0:
                object_one['id'] = object_new['id']
                object_one['type'] = object_new['type']
                object_one['style'] = object_new['style']
                object_one['size'] = object_new['size'][:]
                object_one['scale'] = object_new['scale'][:]
                size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            else:
                continue
            # 次要挂饰
            if deco_size[0] - size_one[0] > 0.3:
                object_two = {
                    'id': '', 'type': '', 'style': '', 'size': [10, 10, 10], 'scale': [1, 1, 1],
                    'position': [0, 0, 0], 'rotation': [0, 0, 0, 1], 'role': '', 'group': ''
                }
                random_base += 1
                object_new = compute_deco_raise(random_base, unique_rest, '', [])
                if len(object_new) > 0:
                    size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                    if deco_size[1] < size_new[1] * 0.8:
                        random_base += 1
                        object_new = compute_deco_raise(random_base, unique_rest, '', [])
                if len(object_new) > 0:
                    object_two['id'] = object_new['id']
                    object_two['type'] = object_new['type']
                    object_two['style'] = object_new['style']
                    object_two['size'] = object_new['size'][:]
                    object_two['scale'] = object_new['scale'][:]
                    size_two = [abs(object_two['size'][i] * object_two['scale'][i]) / 100 for i in range(3)]
                    if deco_size[0] - size_one[0] < size_two[0] * 0.8:
                        object_two, size_two = {}, []
            # 居中布局
            if len(object_two) <= 0:
                # 缩放
                scale_mid = 1.0
                scale_mid = min(deco_size[0] / size_one[0], deco_size[1] / size_one[1], scale_mid)
                object_one['scale'] = [scale_mid, scale_mid, scale_mid]
                size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                object_one['size_max'] = [deco_size[0] * 100, deco_size[1] * 100, deco_size[2] * 100]
                object_one['size_cur'] = 0
                # 位置
                tmp_x, tmp_y, tmp_z = deco_mid_x, deco_top - size_one[1], deco_bak + size_one[2] / 2
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
                object_one['position'] = object_pos[:]
                object_one['normal_position'] = [normal_pos[0] + tmp_x, normal_pos[1] + tmp_y, normal_pos[2] + tmp_z]
                object_one['relate_shifting'] = [tmp_x, tmp_y, tmp_z]
                # 扭转
                normal_ang = 0
                object_one['normal_rotation'] = [0, 0, 0, 1]
                object_ang = plat_ang + normal_ang
                object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
                object_one['rotation'] = object_rot
                pass
            # 靠左布局
            else:
                # 缩放
                scale_mid = 1.0
                object_one['scale'] = [scale_mid, scale_mid, deco_size[1] / size_one[1], scale_mid]
                size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                object_one['size_max'] = [size_one[0] * 100, deco_size[1] * 100, deco_size[2] * 100]
                object_one['size_cur'] = 0
                # 位置
                tmp_x, tmp_y, tmp_z = deco_one[0] + size_one[0] / 2 + 0.02, deco_top - size_one[1], deco_bak + size_one[2] / 2
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
                object_one['position'] = object_pos[:]
                object_one['normal_position'] = [normal_pos[0] + tmp_x, normal_pos[1] + tmp_y, normal_pos[2] + tmp_z]
                object_one['relate_shifting'] = [tmp_x, tmp_y, tmp_z]
                # 扭转
                normal_ang = 0
                object_one['normal_rotation'] = [0, 0, 0, 1]
                object_ang = plat_ang + normal_ang
                object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
                object_one['rotation'] = object_rot
                pass

                # 缩放
                scale_mid = 1.0
                scale_mid = min((deco_size[0] - size_one[0]) / size_two[0], deco_size[1] / size_two[1], scale_mid)
                object_two['scale'] = [scale_mid, scale_mid, scale_mid]
                size_two = [abs(object_two['size'][i] * object_two['scale'][i]) / 100 for i in range(3)]
                object_two['size_max'] = [(deco_size[0] - size_one[0]) * 100, deco_size[1] * 100, deco_size[2] * 100]
                object_two['size_cur'] = 0
                # 位置
                tmp_x, tmp_y, tmp_z = deco_mid_x + size_one[0] / 2, deco_top - size_two[1], deco_bak + size_two[2] / 2
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
                object_two['position'] = object_pos[:]
                object_two['normal_position'] = [normal_pos[0] + tmp_x, normal_pos[1] + tmp_y, normal_pos[2] + tmp_z]
                object_two['relate_shifting'] = [tmp_x, tmp_y, tmp_z]
                # 扭转
                normal_ang = 0
                object_two['normal_rotation'] = [0, 0, 0, 1]
                object_ang = plat_ang + normal_ang
                object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
                object_two['rotation'] = object_rot
                pass

            # 添加
            object_one['group'] = group_type
            object_one['relate'] = plat_one['id']
            object_one['relate_role'] = plat_role
            object_one['relate_position'] = plat_one['position'][:]
            if 'obj_list' not in group_one:
                group_one['obj_list'] = []
            group_one['obj_list'].append(object_one)
            object_done.append(object_one)
            # 添加
            if len(object_two) > 0:
                object_two['group'] = group_type
                object_two['relate'] = plat_one['id']
                object_two['relate_role'] = plat_role
                object_two['relate_position'] = plat_one['position'][:]
                if 'obj_list' not in group_one:
                    group_one['obj_list'] = []
                group_one['obj_list'].append(object_two)
                object_done.append(object_two)

    # 装饰返回
    return object_done


# 家具装饰判断
def resolve_plat_raise(group_type, plat_role, plat_type, plat_height=0):
    if plat_type in PACK_OBJECT_TYPE_0:
        return -1
    elif group_type in ['Bed'] and 'bed' in plat_role:
        return 0
    elif group_type in ['Bed'] and 'side table' in plat_role and plat_height > 1.0:
        return 0
    elif group_type in ['Media'] and 'table' in plat_role and plat_height > 1.5 and False:
        return 0
    return 1


# 家具装饰叠加
def overlap_plat_raise(object_list, plat_one, plat_idx=0):
    global RAISE_COUNT_PLAT
    # 平台信息
    plat_role, plat_type = plat_one['role'], plat_one['type']
    if plat_idx <= 0:
        plat_idx = RAISE_COUNT_PLAT
        RAISE_COUNT_PLAT += 1
    plat_top = (plat_idx + 1) * 1000
    plat_one['top_id'] = plat_top
    plat_one['top_of'] = 0
    # 配饰信息
    overlap_todo, overlap_dict = [], {}
    for object_idx, object_one in enumerate(object_list):
        if 'top_of' not in object_one:
            object_one['top_id'] = plat_top + 200 + object_idx
            object_one['top_of'] = plat_top
        if 'relate_shifting' not in object_one:
            continue
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        object_shift = object_one['relate_shifting']
        tmp_x, tmp_y, tmp_z = object_shift[0], object_shift[1], object_shift[2]
        if plat_role in ['table']:
            overlap_todo.append(object_one)
            overlap_dict[len(overlap_todo) - 1] = [[tmp_x, tmp_y, tmp_z], object_size]
    # 装饰叠加
    for old_idx, old_obj in enumerate(overlap_todo):
        if not old_obj['top_of'] == plat_top:
            continue
        old_pos, old_size = overlap_dict[old_idx][0], overlap_dict[old_idx][1]
        bot_list = []
        for new_idx, new_obj in enumerate(overlap_todo):
            if new_idx == old_idx:
                continue
            if new_obj['top_of'] == old_obj['top_id']:
                continue
            new_pos, new_size = overlap_dict[new_idx][0], overlap_dict[new_idx][1]
            # 判断
            dlt_pos = [new_pos[i] - old_pos[i] for i in range(3)]
            if max(abs(dlt_pos[0]), abs(dlt_pos[2])) > min(new_size[0] / 2, new_size[2] / 2):
                continue
            elif dlt_pos[1] > new_size[1] + 0.1 or dlt_pos[1] < -0.1:
                continue
            # 排序
            bot_new = [new_idx, dlt_pos[1], new_size[0], new_size[1], new_size[2]]
            if len(bot_list) <= 0:
                bot_list.append(bot_new)
            else:
                bot_old = bot_list[0]
                bot_flag = False
                if abs(bot_new[1] - bot_old[1]) >= 0.001:
                    if bot_new[1] <= 0 <= bot_old[1]:
                        bot_flag = True
                    elif bot_old[1] <= bot_new[1] <= 0:
                        bot_flag = True
                    else:
                        bot_flag = False
                elif bot_new[3] <= 0.01 < bot_old[3]:
                    bot_flag = True
                elif bot_new[2] + bot_new[4] > bot_old[2] + bot_old[4]:
                    bot_flag = True
                if bot_flag:
                    bot_list.insert(0, bot_new)
                else:
                    bot_list.append(bot_new)
        if len(bot_list) <= 0:
            continue
        else:
            new_idx = bot_list[0][0]
            new_obj = overlap_todo[new_idx]
            old_obj['top_of'] = new_obj['top_id']
    # 返回信息
    return object_list


# 家具品类判断
def compute_plat_cate(plat_one, room_type=''):
    cate_id = ''
    if 'category' in plat_one:
        cate_id = plat_one['category']
    else:
        type_id, style_id, cate_id = get_furniture_data_refer_id(plat_one['id'], '', False)
    plat_cate = get_furniture_category_by_id(cate_id)
    if plat_cate in ['镜柜'] and 'Bathroom' in room_type:
        plat_cate = '浴室柜'
    return plat_cate


# 家具区域计算
def compute_plat_shape(plat_one, group_one={}):
    # 组合信息
    group_type = ''
    if 'type' in group_one:
        group_type = group_one['type']
    # 家具信息
    plat_id, plat_role, plat_type = plat_one['id'], plat_one['role'], plat_one['type']
    plat_cate = compute_plat_cate(plat_one)
    plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]

    # 承载信息
    flat_dict, flat_deco = {}, []
    # 分类处理
    if plat_role in ['sofa', 'chair']:
        flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
    elif plat_role in ['table', 'side table']:
        if plat_size[1] >= UNIT_HEIGHT_TABLE_MAX or plat_size[1] > plat_size[0] * 0.75:
            flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        elif group_type in ['Meeting', 'Work', 'Rest', 'Media']:
            flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        elif plat_type in ['table/coffee table - irregular shape', 'table/coffee table - round', 'table/console table']:
            flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        elif plat_type in ['table/side table', 'table/night table']:
            flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        elif plat_type in ['media unit/floor-based media unit']:
            flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        elif plat_size[2] > 1.2:
            flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        elif plat_size[1] < 0.4:
            flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        else:
            pass
    elif plat_role in ['cabinet']:
        flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
    elif plat_role in ['window']:
        flat_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        if len(flat_dict) <= 0:
            # 拐角飘窗
            if plat_size[2] > min(plat_size[0] * 0.8, 1.0):
                x_1, y_1, z_1 = -plat_size[0] * 100 / 2 + 20, 6, -plat_size[2] * 100 / 2 + 20
                w_1, d_1 = plat_size[0] * 100 - 40, 40
                x_2, y_2, z_2 = plat_size[0] * 100 / 2 - 20, 6, plat_size[2] * 100 / 2 - 20
                w_2, d_2 = 40, plat_size[2] * 100 - 80
                flat_dict = {
                    6: [
                        [x_1, y_1, z_1, x_1 + w_1, y_1, z_1 + d_1, 50],
                        [x_2 - w_2, y_2, z_2 - d_2, x_2, y_2, z_2, 50]
                    ]
                }
            # 矩形飘窗
            else:
                x_1, y_1, z_1 = -plat_size[0] * 100 / 2 + 10, 6, -plat_size[2] * 100 / 2 + 20
                w_1, d_1 = plat_size[0] * 100 - 20, min(plat_size[2] * 100 - 20, 50)
                flat_dict = {
                    6: [
                        [x_1, y_1, z_1, x_1 + w_1, y_1, z_1 + d_1, 50]
                    ]
                }
    if len(flat_dict) <= 0:
        if plat_role in ['table'] and group_type in ['Meeting', 'Dining', 'Work']:
            deco_delta = min(0.05, plat_size[0] / 20, plat_size[2] / 20)
            deco_one = [-plat_size[0] / 2 + deco_delta, plat_size[1], -plat_size[2] / 2 + deco_delta,
                        plat_size[0] / 2 - deco_delta, plat_size[1], plat_size[2] / 2 - deco_delta, 0.5]
            flat_deco = [deco_one]
    else:
        plat_scale = plat_one['scale']
        lift_min, lift_max = 0.5, 1.0
        if '浴室柜' in plat_cate:
            lift_min, lift_max = min(0.5, plat_size[1] / 4), 1.0
            if plat_size[1] < 1.5:
                lift_min = min(0.30, lift_min)
                lift_max = min(0.80, lift_max)
        elif '玄关柜' in plat_cate:
            lift_min, lift_max = min(0.5, plat_size[1] / 4), 1.5
        elif plat_role in ['table'] and group_type in ['Meeting', 'Media']:
            lift_min, lift_max = 0.2, UNIT_HEIGHT_TABLE_MAX
        elif plat_role in ['cabinet'] and group_type in ['Cabinet'] and plat_size[1] < UNIT_HEIGHT_SHELF_MIN:
            lift_min, lift_max = 0.4, UNIT_HEIGHT_SHELF_MIN
        for info_key, info_val in flat_dict.items():
            for info_one in info_val:
                deco_one = [info_one[i] / 100 for i in range(len(info_one))]
                deco_one[0] *= plat_scale[0]
                deco_one[1] *= plat_scale[1]
                deco_one[2] *= plat_scale[2]
                deco_one[3] *= plat_scale[0]
                deco_one[4] *= plat_scale[1]
                deco_one[5] *= plat_scale[2]
                deco_one[6] *= plat_scale[1]
                deco_find = -1

                for deco_idx, deco_old in enumerate(flat_deco):
                    size_one = (deco_one[3] - deco_one[0]) * (deco_one[5] - deco_one[2])
                    size_old = (deco_old[3] - deco_old[0]) * (deco_old[5] - deco_old[2])
                    height_one = deco_one[1] * 10
                    height_old = deco_old[1] * 10
                    if plat_role in ['sofa', 'chair']:
                        if deco_one[0] < 0 < deco_one[3]:
                            if deco_old[3] < 0 or deco_old[0] > 0:
                                deco_find = deco_idx
                                break
                            elif size_one > size_old:
                                deco_find = deco_idx
                                break
                        else:
                            if deco_old[0] < 0 < deco_old[3]:
                                continue
                            elif size_one > size_old:
                                deco_find = deco_idx
                                break
                    else:
                        if plat_size[1] > UNIT_HEIGHT_TABLE_MAX:
                            if lift_min < deco_one[1] < lift_max:
                                height_one += 100
                                if '浴室柜' in plat_cate and deco_one[2] >= -plat_size[2] / 4:
                                    height_one -= 50
                            if lift_min < deco_old[1] < lift_max:
                                height_old += 100
                                if '浴室柜' in plat_cate and deco_old[2] >= -plat_size[2] / 2 + plat_size[2] / 6:
                                    height_old -= 50
                        if height_one >= 100 and height_old >= 100:
                            if size_one > size_old * 1.5:
                                deco_find = deco_idx
                                break
                            elif size_one < size_old / 1.5:
                                continue
                            elif deco_one[6] > deco_old[6] * 1.5:
                                deco_find = deco_idx
                                break
                            elif deco_one[6] < deco_old[6] / 1.5:
                                continue
                            elif height_one + size_one + deco_one[0] / 10 > height_old + size_old + deco_old[0] / 10:
                                deco_find = deco_idx
                                break
                        if height_one + size_one + deco_one[0] / 10 > height_old + size_old + deco_old[0] / 10:
                            deco_find = deco_idx
                            break
                if 0 <= deco_find < len(flat_deco):
                    flat_deco.insert(deco_find, deco_one)
                else:
                    flat_deco.append(deco_one)
    # 纠错
    if plat_role in ['table', 'side table'] and len(flat_deco) > 0:
        deco_one, deco_error = flat_deco[0], False
        deco_width, deco_depth = deco_one[3] - deco_one[0], deco_one[5] - deco_one[2]
        if deco_depth < min(plat_size[2] / 4, 0.2):
            deco_error = True
        elif deco_width < min(plat_size[0] / 4, 0.2):
            deco_error = True
        if deco_error:
            if '儿童' in plat_cate:
                flat_fine = []
                for flat_idx, flat_one in enumerate(flat_deco):
                    if flat_one[6] >= 0.4 and flat_one[1] >= min(plat_size[1] * 0.5, 0.5) and flat_idx > 0:
                        flat_width, flat_depth = flat_one[3] - flat_one[0], flat_one[5] - flat_one[2]
                        if flat_width > 0.2 and flat_depth > 0.2:
                            flat_fine = [flat_one]
                            break
                        elif flat_width > 0.2 and flat_depth > 0.1 and len(flat_fine) <= 0:
                            flat_fine = [flat_one]
                        elif flat_width > 0.1 and flat_depth > 0.2 and len(flat_fine) <= 0:
                            flat_fine = [flat_one]
                flat_deco = flat_fine
            elif plat_size[1] <= UNIT_HEIGHT_SHELF_MIN:
                deco_delta = min(0.05, plat_size[0] / 20, plat_size[2] / 20)
                deco_one = [-plat_size[0] / 2 + deco_delta, plat_size[1], -plat_size[2] / 2 + deco_delta,
                            plat_size[0] / 2 - deco_delta, plat_size[1], plat_size[2] / 2 - deco_delta, 0.5]
                flat_deco = [deco_one]
            else:
                flat_deco = []
    # 纠错
    if ('沙发' in plat_cate or plat_role in ['sofa', 'chair']) and len(flat_deco) > 0:
        deco_main = flat_deco[0]
        side_width, back_depth = 0.15, 0.10
        if plat_size[0] > UNIT_WIDTH_SOFA_SINGLE * 1.2:
            side_width, back_depth = 0.25, 0.20
            if plat_size[0] > UNIT_WIDTH_SOFA_SINGLE * 1.8:
                side_width = 0.35
            if plat_size[2] > UNIT_WIDTH_SOFA_SINGLE * 0.8:
                back_depth = 0.30
        if plat_id in ['95f863cb-1353-45c5-a623-ca93b8f29a5a', '41b538ee-8789-4275-9bd1-98a563722dea']:
            side_width, back_depth = 0.50, 0.40
        if plat_size[2] > UNIT_WIDTH_SOFA_SINGLE and deco_main[2] > -0.05 and (deco_main[3] < -0.5 or deco_main[0] > 0.5):
            deco_main[2] = max(deco_main[2], -plat_size[2] / 2 + back_depth)
            deco_main[6] = min(deco_main[6], max(0.30, plat_size[1] + 0.1 - deco_main[1]))
        else:
            deco_main[0] = max(deco_main[0], -plat_size[0] / 2 + side_width)
            deco_main[2] = max(deco_main[2], -plat_size[2] / 2 + back_depth)
            deco_main[3] = min(deco_main[3], plat_size[0] / 2 - side_width)
            deco_main[6] = min(deco_main[6], max(0.30, plat_size[1] + 0.1 - deco_main[1]))
            if deco_main[2] > -plat_size[2] / 2 + back_depth + 0.2 and plat_size[0] > UNIT_WIDTH_SOFA_SINGLE * 1.5:
                if deco_main[5] - deco_main[2] < 0.3:
                    deco_main[2] = -plat_size[2] / 2 + back_depth + 0.2
            if deco_main[5] > -plat_size[2] / 2 + back_depth + 0.5 and plat_size[0] > UNIT_WIDTH_SOFA_SINGLE * 1.5:
                if deco_main[5] - deco_main[2] > 0.5:
                    deco_main[5] = -plat_size[2] / 2 + back_depth + 0.5
    elif ('茶几' in plat_cate or '茶桌' in plat_cate) and len(flat_deco) > 0:
        deco_main = flat_deco[0]
        deco_width, deco_depth = deco_main[3] - deco_main[0], deco_main[5] - deco_main[2]
        if abs(deco_width - deco_depth) < 0.1:
            deco_delta = min(0.1, deco_width / 6)
            deco_main[0] += deco_delta
            deco_main[2] += deco_delta
            deco_main[3] -= deco_delta
            deco_main[5] -= deco_delta
        elif deco_width > deco_depth:
            deco_delta = min(0.1, deco_width / 6)
            deco_main[0] += deco_delta
            deco_main[3] -= deco_delta
            deco_delta = min(0.05, deco_depth / 6)
            deco_main[2] += deco_delta
            deco_main[5] -= deco_delta
        elif deco_width < deco_depth:
            deco_delta = min(0.1, deco_depth / 6)
            deco_main[2] += deco_delta
            deco_main[5] -= deco_delta
            deco_delta = min(0.05, deco_width / 6)
            deco_main[0] += deco_delta
            deco_main[3] -= deco_delta
    elif '梳妆台' in plat_cate and len(flat_deco) > 0:
        deco_main = flat_deco[0]
        deco_width, deco_depth = deco_main[3] - deco_main[0], deco_main[5] - deco_main[2]
        if deco_main[1] < plat_size[1] - 0.1:
            deco_delta = min(0.15, deco_depth / 3)
            if deco_main[2] < -plat_size[2] / 2 + deco_delta:
                deco_main[2] = -plat_size[2] / 2 + deco_delta
    elif '浴室柜' in plat_cate and len(flat_deco) > 0:
        if len(flat_deco) >= 3:
            if abs(flat_deco[0][1] - flat_deco[1][1]) <= 0.05 and abs(flat_deco[0][1] - flat_deco[2][1]) <= 0.05:
                dump_idx = -1
                if flat_deco[1][0] + 0.1 < flat_deco[0][0] < flat_deco[2][0] - 0.1:
                    dump_idx = 0
                elif flat_deco[2][0] + 0.1 < flat_deco[0][0] < flat_deco[1][0] - 0.1:
                    dump_idx = 0
                elif flat_deco[0][0] + 0.1 < flat_deco[1][0] < flat_deco[2][0] - 0.1:
                    dump_idx = 1
                elif flat_deco[2][0] + 0.1 < flat_deco[1][0] < flat_deco[0][0] - 0.1:
                    dump_idx = 1
                elif flat_deco[0][0] + 0.1 < flat_deco[2][0] < flat_deco[1][0] - 0.1:
                    dump_idx = 2
                elif flat_deco[1][0] + 0.1 < flat_deco[2][0] < flat_deco[0][0] - 0.1:
                    dump_idx = 2
                if 0 <= dump_idx < len(flat_deco):
                    flat_deco.pop(dump_idx)
        deco_main = flat_deco[0]
        deco_width, deco_depth = deco_main[3] - deco_main[0], deco_main[5] - deco_main[2]
        # 划分宽度
        deco_part = 3
        for info_key, info_val in flat_dict.items():
            if int(info_key) / 100 >= deco_main[1] - 0.1:
                continue
            if len(info_val) >= 2:
                if (info_val[0][0] + info_val[0][3]) / 2 * (info_val[-1][0] + info_val[-1][3]) / 2 < 0:
                    if info_val[0][3] - info_val[0][0] > 10 and info_val[-1][3] + info_val[-1][0] > 10:
                        deco_part = 5
        if deco_width > 1.2:
            deco_part = 5
        step_width = deco_width / deco_part
        # 划分平面
        if deco_width > min(deco_depth * 3, 0.5) and deco_main[0] < 0 < deco_main[3]:
            # 右侧平面
            deco_one = deco_main[:]
            deco_one[0] = deco_one[3] - step_width
            deco_one[5] = deco_one[2] + min(deco_depth, 0.20)
            # 左侧平面
            deco_two = deco_main
            deco_two[3] = deco_two[0] + step_width
            deco_two[5] = deco_two[2] + min(deco_depth, 0.20)
            # 添加平面
            flat_deco.insert(0, deco_one)
            if deco_part >= 5:
                deco_mid = deco_main[:]
                deco_mid[0] = deco_two[3] + step_width * 0.75
                deco_mid[3] = deco_one[0] - step_width * 0.75
                deco_mid[5] = deco_mid[2] + min(deco_depth, 0.20)
                flat_deco.insert(0, deco_mid)

    # 依附信息
    tilt_dict, tilt_deco = {}, []
    # 分类处理
    if plat_cate in ['玄关柜', '衣柜']:
        tilt_dict = get_furniture_plat_detail(plat_id, plat_type, 'bak')
        if len(tilt_dict) > 0:
            for info_key, info_val in tilt_dict.items():
                for info_one in info_val:
                    deco_one = [info_one[i] / 100 for i in range(len(info_one))]
                    deco_one[0] *= plat_scale[0]
                    deco_one[1] *= plat_scale[1]
                    deco_one[2] *= plat_scale[2]
                    deco_one[3] *= plat_scale[0]
                    deco_one[4] *= plat_scale[1]
                    deco_one[5] *= plat_scale[2]
                    deco_one[6] *= plat_scale[1]
                    deco_find = -1
                    for deco_idx, deco_old in enumerate(tilt_deco):
                        size_one = (deco_one[3] - deco_one[0]) * (deco_one[4] - deco_one[1])
                        size_old = (deco_old[3] - deco_old[0]) * (deco_old[4] - deco_old[1])
                        if size_one + deco_one[0] / 10 > size_old + deco_old[0] / 10:
                            deco_find = deco_idx
                            break
                    if 0 <= deco_find < len(tilt_deco):
                        tilt_deco.insert(deco_find, deco_one)
                    else:
                        tilt_deco.append(deco_one)
        elif len(flat_deco) > 0:
            deco_main = flat_deco[0]
            deco_width, deco_depth = deco_main[3] - deco_main[0], deco_main[5] - deco_main[2]
            if deco_depth > max(0.3, plat_size[2] - 0.02):
                deco_main[2] = deco_main[5] - deco_depth / 2 + 0.01

    # 返回信息
    return flat_deco, tilt_deco


def rotate(quaternion, v):
    r = R.from_quat(quaternion)
    v = r.apply(v)
    return v


def extract_mesh_data(house_data, mesh_url):
    if len(mesh_url) == 0:
        return house_data
    try:
        r = requests.get(mesh_url)
        if r.ok:
            mesh_info = r.json()
            mesh_fur_dict = {}
            for cus_data in mesh_info:
                fur = format_mesh_data(cus_data)
                room_id = cus_data['id']
                if 'isCutom' in cus_data:
                    fur['isCutom'] = cus_data['isCutom']
                if 'isOpenDoor' in cus_data:
                    fur['isOpenDoor'] = cus_data['isOpenDoor']
                if room_id not in mesh_fur_dict:
                    mesh_fur_dict[room_id] = [fur]
                else:
                    mesh_fur_dict[room_id].append(fur)
            for room in house_data['room']:
                if room['id'] in mesh_fur_dict:
                    if 'furniture_info' in room:
                        room['furniture_info'] += mesh_fur_dict[room['id']]
                    else:
                        room['furniture_info'] = mesh_fur_dict[room['id']]
            return house_data
        else:
            return house_data
    except Exception as e:
        print(e)
        return house_data


def format_mesh_data(cus_data):
    new_fur = {}
    cabinet_data = {}
    mesh_data = {}
    room_type = cus_data['room_type']
    cabinetId = cus_data['cabinetId']
    cabinet_data[cabinetId] = {}
    cus_list = []
    for child in cus_data['childGraphics']:
        if child['class'] == 'HSCore.Model.DExtruding':
            # print(child['id'])
            cabinet_data[cabinetId][child['id']] = []
            graphicObj = child['graphicObj']
            objects = graphicObj['objects']
            meshDefs = graphicObj['meshDefs']
            for m in meshDefs:
                mid = m['meshKey']
                xyz = np.reshape([m['vertexPositions'][str(i)] for i in range(len(m['vertexPositions']))], [-1, 3]).tolist()
                uv = [m['vertexUVs'][str(i)] for i in range(len(m['vertexUVs']))]
                normal = np.reshape([m['vertexNormals'][str(i)] for i in range(len(m['vertexNormals']))], [-1, 3]).tolist()
                face = np.reshape([m['faceIndices'][str(i)] for i in range(len(m['faceIndices']))], [-1, 3]).tolist()
                assert mid not in mesh_data
                mesh_data[mid] = {
                    'xyz': xyz,
                    'uv': uv,
                    'normal': normal,
                    'face': face,
                }

            for obj in objects:
                obj['position'] = [obj['position']['0'], obj['position']['1'], obj['position']['2']]
                obj['rotation'] = [obj['rotation']['0'], obj['rotation']['1'], obj['rotation']['2'], obj['rotation']['3']]
                obj['scale'] = [obj['scale']['0'], obj['scale']['1'], obj['scale']['2']]
                cabinet_data[cabinetId][child['id']].append(obj)

                # visualize mesh
                v = mesh_data[obj['mesh']]['xyz'] * np.array(obj['scale'])
                uv = mesh_data[obj['mesh']]['uv']

                v = rotate(obj['rotation'], v)
                n = rotate(obj['rotation'], mesh_data[obj['mesh']]['normal'])

                v = v + np.array(obj['position'])
                # 坐标系转换
                v[:, 1] = -v[:, 1]
                v[:, [1, 2]] = v[:, [2, 1]]
                f = mesh_data[obj['mesh']]['face']

                color = [list(np.random.choice(list(np.arange(256)), 3))] * len(v)
                cus_list.append(
                    {
                        'xyz': v.tolist(),
                        'normal': n.tolist(),
                        'face': f,
                        'color': color,
                        'uv': uv
                    }
                )

    xyz = []
    normal = []
    face = []
    color = []
    uv = []
    for cus in cus_list:
        f = (np.array(cus['face']) + len(xyz)).tolist()
        face += f
        xyz += cus['xyz']
        normal += cus['normal']
        color += cus['color']
        uv += cus['uv']
    m = {
        'xyz': np.reshape(xyz, [-1]).tolist(),
        'normal': np.reshape(normal, [-1]).tolist(),
        'face': np.reshape(face, [-1]).tolist(),
        'uv': np.reshape(uv, [-1]).tolist(),
    }

    maxp = np.max(xyz, axis=0)
    minp = np.min(xyz, axis=0)
    pos = (0.5 * (maxp + minp)).tolist()
    size = (maxp - minp).tolist()

    new_fur['size'] = size
    new_fur['position'] = pos
    new_fur['rotation'] = [0, 0, 0]
    new_fur['scale'] = [1, 1, 1]
    new_fur['mesh_info'] = m
    return new_fur


def project_mesh(v, f, pro_axis=1):
    v_cp = np.reshape(v, [-1, 3])
    f_pts_3d = [v_cp[face] for face in f]
    pts = np.reshape(f_pts_3d, [-1, 3])
    bdox_size = (np.max(pts, axis=0) - np.min(pts, axis=0)).tolist()
    v_2d = []
    for i in range(3):
        if i != pro_axis:
            v_2d.append(np.array(v_cp)[:, i])
    v_2d = np.array(v_2d).transpose()
    height_lower = np.min(pts, axis=0)[1]
    height_upper = np.max(pts, axis=0)[1]
    x_lower = np.min(pts, axis=0)[0]
    x_upper = np.max(pts, axis=0)[0]
    z_lower = np.min(pts, axis=0)[2]
    z_upper = np.max(pts, axis=0)[2]
    polys = []
    f_cp = np.reshape(f, [-1, 3])
    for face in f_cp:
        f_pts = v_2d[face]
        v1 = f_pts[0] - f_pts[1]
        v2 = f_pts[2] - f_pts[1]
        if abs(np.cross(v1, v2)) > 1e-3:
            poly = Polygon(f_pts)
            polys.append(poly)
    if len(polys) == 0:
        return [], [[x_lower, x_upper], [height_lower, height_upper], [z_lower, z_upper]], bdox_size, 1.
    polys.sort(key=lambda x: -x.area)

    cmb_poly = polys[0]

    err_face_area = 0.
    for i in range(1, len(polys)):
        area = polys[i].area
        if area < 1e-3:
            continue
        if cmb_poly.covers(polys[i]):
            continue
        try:
            cmb_poly = cmb_poly.union(polys[i])
        except Exception as e:
            print(e)
            err_face_area += area

    if err_face_area / (cmb_poly.area + 1e-3) > 0.1:
        print('extract customized ceiling failed')

    bounds = cmb_poly.bounds
    area = 0.
    bounds_area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])

    if isinstance(cmb_poly, Polygon):
        coords = [np.asarray(cmb_poly.buffer(0).exterior.coords).tolist()]
        p = Polygon(coords[0])
        area += p.area
    else:
        coords_all = list(cmb_poly.geoms)
        coords_all = [np.asarray(i.buffer(0).exterior.coords).tolist() for i in coords_all if isinstance(i, Polygon)]
        coords = []
        for c in coords_all:
            p = Polygon(c)
            if p.area < 1e-2 or p.area * 10 < bounds_area:
                continue
            coords.append(c)
            area += p.area
    area_ratio = 1. - area / (bounds_area + 1e-3)

    coords_refined = []
    for c in coords:
        c = list(c)
        c_refined = []
        for i in range(len(c)):
            curt_p = c[i]
            if np.linalg.norm(np.array(curt_p) - c[(i-1) % len(c)]) < 1e-3:
                continue
            else:
                c_refined.append(copy.deepcopy(curt_p))
        c_refined_2 = []
        for i in range(len(c_refined)):
            last_p = c_refined[(i - 1) % len(c_refined)]
            curt_p = c_refined[i]
            next_p = c_refined[(i + 1) % len(c_refined)]
            v1 = np.array(curt_p) - last_p
            v1 = v1 / np.linalg.norm(v1)
            v2 = np.array(next_p) - curt_p
            v2 = v2 / np.linalg.norm(v2)
            if abs(np.cross(v1, v2)) < 1e-3:
                continue
            else:
                c_refined_2.append(copy.deepcopy(curt_p))
        # plt.figure()
        # plt.plot(np.array(c)[:, 0], np.array(c)[:, 1], marker='o')
        # plt.plot(np.array(c_refined_2)[:, 0], np.array(c_refined_2)[:, 1], marker='*')
        # plt.show()

        for i in range(len(c_refined_2)):
            c_refined_2[i] = [c_refined_2[i][0], height_lower, c_refined_2[i][1]]
        coords_refined.append(c_refined_2)

    return coords_refined, [[x_lower, x_upper], [z_lower, z_upper], [height_lower, height_upper]], bdox_size, area_ratio


def bot_mesh_contour(v, f, bot_val):
    minx = min(bot_val[0], bot_val[3]) / 100.
    miny = min(bot_val[2], bot_val[5]) / 100.
    maxx = max(bot_val[0], bot_val[3]) / 100.
    maxy = max(bot_val[2], bot_val[5]) / 100.
    height = bot_val[1] / 100.

    v_cp = np.reshape(v, [-1, 3])
    faces = np.reshape(f, [-1, 3])
    f_pts_3d = [v_cp[face] for face in faces]

    all_face_pts = []
    for f_pts in f_pts_3d:
        if (np.abs(f_pts[:, 1] - height) < 1e-1).all():
            if (minx - 1e-3 < f_pts[:, 0]).all() and (f_pts[:, 0] < maxx + 1e-3).all() and \
                    (miny - 1e-3 < f_pts[:, 2]).all() and (f_pts[:, 2] < maxy + 1e-3).all():
                v1 = f_pts[1] - f_pts[0]
                v2 = f_pts[2] - f_pts[0]
                norm = np.cross(v1, v2)
                norm = norm / np.linalg.norm(norm)
                if abs(norm[1]) < 0.9:
                    continue
                all_face_pts.append(f_pts)
            pass
        else:
            continue
    poly = []
    flags = [True] * len(all_face_pts)
    cur_poly = None
    while True:
        break_flag = False
        if cur_poly is not None:
            for i, f_pts in enumerate(all_face_pts):
                if not flags[i]:
                    continue

                new_poly = Polygon(f_pts[:, [0, 2]])
                if cur_poly.intersects(new_poly):
                    cur_poly = cur_poly.union(new_poly)
                    break_flag = True
                    flags[i] = False
        if not break_flag:
            for i, f_pts in enumerate(all_face_pts):
                if not flags[i]:
                    continue
                if cur_poly is not None:
                    poly.append(copy.deepcopy(cur_poly))
                cur_poly = Polygon(f_pts[:, [0, 2]])

                flags[i] = False
                break
        if np.sum(flags) == 0:
            poly.append(copy.deepcopy(cur_poly))
            break
    if len(all_face_pts) == 0:
        return [[
            [bot_val[0], bot_val[1], bot_val[2]],
            [bot_val[0], bot_val[1], bot_val[5]],
            [bot_val[3], bot_val[4], bot_val[5]],
            [bot_val[3], bot_val[4], bot_val[5]]
        ],
            bot_val[6], False]
    else:
        all_face_pts = np.array(all_face_pts)
        # plt.figure()
        # plt.axis('equal')
        # for ff in all_face_pts:
        #     ff = ff.tolist()
        #     ff = np.array(ff + ff[:1])
        #     plt.plot(ff[:, 0], ff[:, 2])
        poly = sorted(poly, key=lambda x: -x.area)[0]
        if isinstance(poly, Polygon):
            contour = [(poly.area, np.array(poly.exterior.coords))]
        else:
            contour = [(i.area, np.array(i.exterior.coords)) for i in list(poly.geoms)]
        contour.sort(key=lambda x: -x[0])
        contour_pts = contour[0][1]
        area = contour[0][0]
        valid = area / (maxx - minx) / (maxy - miny) > 0.9
        # plt.figure()
        # plt.axis('equal')
        # plt.plot(contour_pts[:, 0], contour_pts[:, 1])
        if valid:
            return [[
                [bot_val[0], bot_val[1], bot_val[2]],
                [bot_val[0], bot_val[1], bot_val[5]],
                [bot_val[3], bot_val[4], bot_val[5]],
                [bot_val[3], bot_val[4], bot_val[5]]
            ],
                bot_val[6], valid]
        else:
            contour_pts = [[i[0], height, i[1]] for i in contour_pts]
            return [np.round(np.array(contour_pts) * 100., 3).tolist(), bot_val[6], valid]


def line_face_intersect(face_pts, line_org, line_dir):
    f_p = np.array(face_pts)[0]
    fa = np.array(face_pts)[1] - f_p
    fb = np.array(face_pts)[2] - f_p
    a = [
        [fa[0], fb[0],  line_dir[0]],
        [fa[1], fb[1], line_dir[1]],
        [fa[2], fb[2], line_dir[2]]
    ]
    b = line_org - f_p
    rank = np.linalg.matrix_rank(a)
    if rank == 3:
        # a,b vector scale, depth(signed)
        r = np.linalg.solve(a, b)
        if r[0] + r[1] > 1. or r[0] < 0. or r[1] < 0.:
            return False, 0.
        else:
            return True, r[2]
    else:
        return False, 0


def find_open_faces(mesh, bot):
    bot_center = [0.5 * (bot[0] + bot[3]), bot[1] + bot[6] * 0.5, 0.5 * (bot[2] + bot[5])]
    bot_center = np.array(bot_center) / 100.
    bot_size = [abs(bot[0] - bot[3]) / 100., abs(bot[2] - bot[5]) / 100.]
    xyz = np.reshape(mesh['xyz'], [-1, 3])
    face = np.reshape(mesh['face'], [-1, 3])
    directions = [
        [1, 0, 0],
        [0, 0, 1]
    ]
    open_state = [True] * 4
    depth_thresh = 0.8
    for i in range(2):
        direct = directions[i]

        for f in face:
            face_pts = xyz[f]
            flag, depth = line_face_intersect(face_pts, bot_center, direct)
            if flag:
                if depth_thresh * bot_size[i] > depth > 1e-3:
                    open_state[i] = False
                elif -depth_thresh * bot_size[i] < depth < -1e-3:
                    open_state[i + 2] = False
                else:
                    continue
            if not open_state[i] and not open_state[i + 2]:
                break
    return open_state


# 家具内空查找
def compute_plat_inner(plat_one, group_one={}):
    # 家具信息
    plat_id, plat_role, plat_type = plat_one['id'], plat_one['role'], plat_one['type']
    # origin_size, origin_scale = plat_one['size'], plat_one['scale']
    # origin_width, origin_depth = origin_size[0], origin_size[2]
    # plat_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
    # plat_cate = compute_plat_cate(plat_one)
    # plat_pos, plat_ang = [0, 0, 0], 0
    # plat_mesh = {}
    # if 'position' in plat_one:
    #     plat_pos = plat_one['position']
    # if 'rotation' in plat_one:
    #     plat_ang = rot_to_ang(plat_one['rotation'])
    if 'mesh_info' in plat_one:
        plat_mesh = plat_one['mesh_info']
        model_set = glm_read_mesh([plat_mesh])
        bot_dict, decor_bak, frt_dict, ratio = glm_shape_obj(model_set[0], plat_type)
        v = plat_mesh['xyz']
        f = plat_mesh['face']
        coords, bounds, size, empty_area_rate = project_mesh(v, f, pro_axis=1)
        coords = [(np.array(c) * 100.).tolist() for c in coords]
        if empty_area_rate < 0.1:
            #  一字型柜体
            #  柜体分析
            all_bot_open_state = []
            for bot_key, bot_val in bot_dict.items():
                for box_one in bot_val:
                    open_state = find_open_faces(plat_mesh, box_one)
                    all_bot_open_state.append(open_state)
            sta_states = np.sum(all_bot_open_state, axis=0)
            directions = [
                [1, 0, 0],
                [0, 0, 1],
                [-1, 0, 0],
                [0, 0, -1],
            ]
            direct = directions[int(np.argmax(sta_states))]
            direct_xyz = [direct[0], direct[2], direct[1]]
            focus_center = ((np.mean(bounds, axis=1) + direct_xyz) * 100.).tolist()
        else:
            focus_center = (np.mean(bounds, axis=1) * 100).tolist()
        customized = True
    else:
        # 承载位置
        bot_dict = get_furniture_plat_detail(plat_id, plat_type, 'bot')
        # 柜门位置
        frt_dict = get_furniture_plat_detail(plat_id, plat_type, 'frt')
        focus_center = [0, 0, 100.]
        model = get_furniture_plat_detail(plat_id, plat_type, 'model')
        v = np.array(model.vertices) / 100.
        f = [f.v_indices for f in model.faces]
        coords, bounds, size, empty_area_rate = project_mesh(v, f, pro_axis=1)
        coords = [(np.array(c) * 100.).tolist() for c in coords]
        customized = False

    bot_contour = {}
    for bot_key, bot_val in bot_dict.items():
        bot_contour[bot_key] = []
        for box_one in bot_val:
            contour = bot_mesh_contour(v, f, box_one)
            bot_contour[bot_key].append(contour)
    # 下空位置
    und_dict = coords

    # 校正位置
    # bot_list, frt_list, und_list = [], [], []
    # for bot_key, bot_val in bot_dict.items():
    #     for box_one in bot_val:
    #         # 尺寸
    #         width = (box_one[3] - box_one[0]) / 100 * origin_scale[0]
    #         depth = (box_one[5] - box_one[2]) / 100 * origin_scale[2]
    #         height = box_one[6] / 100 * origin_scale[1]
    #         # 偏移
    #         tmp_x = (box_one[0] + box_one[3]) / 200 * origin_scale[0]
    #         tmp_y = (box_one[1] + box_one[4]) / 200 * origin_scale[1]
    #         tmp_z = (box_one[2] + box_one[5]) / 200 * origin_scale[2]
    #         add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
    #         add_y = tmp_y
    #         add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
    #         # 位置
    #         pos_x = plat_pos[0] + add_x
    #         pos_y = plat_pos[1] + add_y
    #         pos_z = plat_pos[2] + add_z
    #         # 增加
    #         box_add = {
    #             'size': [width, height, depth],
    #             'position': [pos_x, pos_y, pos_z]
    #         }
    #         bot_list.append(box_add)
    # for frt_key, frt_val in frt_dict.items():
    #     for box_one in frt_val:
    #         pass
    #     pass
    # for und_key, und_val in und_dict.items():
    #     for box_one in und_val:
    #         # 尺寸
    #         width = (box_one[3] - box_one[0]) / 100 * origin_scale[0]
    #         depth = (box_one[5] - box_one[2]) / 100 * origin_scale[2]
    #         height = box_one[6] / 100 * origin_scale[1]
    #         # 偏移
    #         tmp_x = (box_one[0] + box_one[3]) / 200 * origin_scale[0]
    #         tmp_y = (box_one[1] + box_one[4]) / 200 * origin_scale[1]
    #         tmp_z = (box_one[2] + box_one[5]) / 200 * origin_scale[2]
    #         add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
    #         add_y = tmp_y
    #         add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
    #         # 位置
    #         pos_x = plat_pos[0] + add_x
    #         pos_y = plat_pos[1] + add_y
    #         pos_z = plat_pos[2] + add_z
    #         # 增加
    #         box_add = {
    #             'size': [width, height, depth],
    #             'position': [pos_x, pos_y, pos_z]
    #         }
    #         bot_list.append(box_add)
    #     pass
    normal_inner = {
        'bot': bot_contour,
        'frt': frt_dict,
        'und': und_dict,
        "focus_center": focus_center,
        "customized": customized
    }
    # origin_inner = {
    #     'bot': bot_list,
    #     'frt': [],
    #     'und': und_list
    # }
    # # 返回信息
    # return_inner = {
    #     'normal_inner': normal_inner,
    #     'origin_inner': origin_inner
    # }
    return normal_inner


# 家具装饰整理
def cluster_plat_raise(plat_one, group_one, deco_info, object_list, object_more=[], object_used={},
                       unique_more=0, unique_type=''):
    # 结果
    object_sort = []
    # 平台
    if len(plat_one) <= 0:
        return object_sort, unique_more
    plat_role, plat_cate = '', ''
    if 'role' in plat_one:
        plat_role = plat_one['role']
    plat_cate = compute_plat_cate(plat_one)
    plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
    width_max, depth_max = plat_size[0], plat_size[2]
    if len(deco_info) >= 6:
        width_max = deco_info[3] - deco_info[0]
        depth_max = deco_info[5] - deco_info[2]
    group_type = ''
    if 'type' in group_one:
        group_type = group_one['type']
    unique_main_1 = ['花卉', '工艺品']
    unique_side_1 = ['工艺品', '相框', '杂志']
    if group_type in ['Meeting', 'Work', 'Rest'] and plat_role in ['table']:
        if '餐桌' in plat_cate:
            unique_main_1 = ['食物组合', '茶具组合', '花卉']
            unique_side_1 = ['水杯', '水壶', '酒具', '食物']
        elif '茶几' in plat_cate:
            unique_main_1 = ['花卉', '食物组合', '茶具组合']
            unique_side_1 = ['水杯', '水壶', '食物', '相框', '杂志']
        elif '儿童' in unique_type or '玩具' in unique_type:
            unique_main_1 = ['相框', '书籍', '儿童台灯']
            unique_side_1 = ['闹钟', '玩具', '儿童工艺品']
        elif '书桌' in plat_cate or '书台' in plat_cate:
            unique_side_1 = ['工艺品', '相框', '杂志']
        elif '梳妆' in plat_cate:
            unique_side_1 = ['花卉', '相框', '杂志']
        elif group_type in ['Rest']:
            unique_main_1 = ['食物组合', '茶具组合', '花卉']
            unique_side_1 = ['水杯', '水壶', '食物', '花卉', '相框', '杂志']
        else:
            unique_side_1 = ['花卉', '相框', '杂志']
    elif group_type in ['Cabinet'] and plat_role in ['cabinet']:
        if '玄关柜' in plat_cate or '玄关台' in plat_cate:
            unique_main_1 = ['花卉', '工艺品', '书籍组合2', '书籍组合3', '包', '衣帽', '毛绒玩具']
            unique_side_1 = ['相框', '盒子', '毛巾', '包', '毛绒玩具']
        elif '儿童' in unique_type or '玩具' in unique_type:
            unique_main_1 = ['相框', '书籍', '儿童台灯']
            unique_side_1 = ['闹钟', '玩具', '儿童工艺品']
    random.shuffle(unique_main_1)
    random.shuffle(unique_side_1)
    # 排序
    object_dump = ['46933696-6950-4da6-a7f7-2a1f681cda0a', '918be658-3b0a-4fa9-895b-ed5810a300bc']
    for object_idx, object_one in enumerate(object_list):
        if 'relate_shifting' not in object_one:
            continue
        if object_one['id'] in object_dump and len(object_list) > 1:
            continue
        if plat_one['role'] in ['sofa', 'chair'] and len(object_list) > 1:
            if object_one['normal_rotation'][3] < 0.95 and object_one['normal_rotation'][1] < 0.95:
                continue
            elif 'pillow' not in object_one['type']:
                continue
        elif plat_one['role'] in ['window'] and 'pillow' in object_one['type']:
            if object_one['normal_rotation'][3] < 0.95 and object_one['normal_rotation'][1] < 0.95 and len(object_list) >= 3:
                continue
        if 'pendant light' in object_one['type']:
            continue
        # 查找
        object_find = -1
        for sort_idx, sort_one in enumerate(object_sort):
            if object_one['relate_shifting'][0] > sort_one['relate_shifting'][0]:
                object_find = sort_idx
                break
        # 复制
        object_new = copy_object(object_one)
        object_new['relate_shifting'] = object_one['relate_shifting'][:]
        # 校正
        cate_one = get_furniture_cate(object_one['id'])
        size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        if plat_one['role'] in ['sofa', 'chair']:
            if len(object_list) <= 1:
                object_new['normal_rotation'] = [0, 0, 0, 1]
            elif 'normal_rotation' in object_new and object_new['normal_rotation'][1] > 0.95:
                object_new['normal_rotation'] = [0, 0, 0, 1]
            if object_new['id'] in ['8570be4e-8e98-43ae-89b7-3463c165bffd']:
                object_new['id'] = 'a3bcd02c-a527-4781-b2d3-0c43cd99b3d5'
        elif plat_one['role'] in ['cabinet']:
            if len(object_list) <= 1:
                object_new['normal_rotation'] = [0, 0, 0, 1]
            elif 'normal_rotation' in object_one and object_one['normal_rotation'][1] > 0.95:
                object_one['normal_rotation'] = [0, 0, 0, 1]
        elif plat_one['role'] in ['table', 'side table'] and group_type in ['Meeting', 'Bed', 'Rest']:
            object_old = {}
            if size_one[0] > 0.80:
                unique_more += 1
                unique_old = unique_main_1[object_idx % len(unique_main_1)]
                object_old = compute_deco_raise(unique_more, unique_old)
                size_one = [abs(object_old['size'][i]) / 100 for i in range(3)]
            if size_one[0] > width_max * 0.8 or size_one[2] > depth_max * 0.8:
                if 'lamp' in object_one['type']:
                    pass
                elif 'side table' in plat_one['role']:
                    pass
                else:
                    unique_more += 1
                    unique_old = unique_main_1[object_idx % len(unique_main_1)]
                    object_old = compute_deco_raise(unique_more, unique_old)
            if len(object_old) > 0:
                object_new['id'] = object_old['id']
                object_new['type'] = object_old['type']
                object_new['style'] = object_old['style']
                object_new['size'] = object_old['size'][:]
                object_new['scale'] = object_old['scale'][:]
                object_new['normal_rotation'] = [0, 0, 0, 1]
            cate_one = get_furniture_cate(object_new['id'])
            if len(unique_main_1) >= 2 and cate_one in unique_main_1:
                unique_main_1.remove(cate_one)
        # 横向
        if group_type in ['Dining']:
            object_sort.append(object_new)
        elif 0 <= object_find < len(object_sort):
            object_sort.insert(object_find, object_new)
        else:
            object_sort.append(object_new)
    if group_one['type'] in ['Dining']:
        return object_sort, unique_more
    elif plat_one['role'] in ['sofa', 'chair', 'table', 'side table', 'cabinet', 'armoire', 'appliance', 'window']:
        pass
    else:
        return object_sort, unique_more
    if len(object_sort) <= 0 and len(object_list) > 0:
        object_sort = [object_list[0]]

    # 平台
    if len(deco_info) < 6:
        return object_sort, unique_more
    # 纵向
    z_min, z_max = 10, -10
    for object_idx, object_one in enumerate(object_sort):
        shift_one = object_one['relate_shifting']
        size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        if shift_one[2] - size_one[2] / 2 < z_min:
            z_min = shift_one[2] - size_one[2] / 2
        if shift_one[2] + size_one[2] / 2 > z_max:
            z_max = shift_one[2] + size_one[2] / 2
    # 收拢
    delta_max = 0.05
    for object_idx, object_one in enumerate(object_sort):
        shift_flag, scale_flag = False, 0
        if plat_role in ['sofa', 'chair']:
            shift_one = object_one['relate_shifting']
            size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            shift_flag = True
        elif plat_role in ['cabinet', 'table']:
            shift_one = object_one['relate_shifting']
            size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if shift_one[2] + size_one[2] / 2 > z_min + depth_max + delta_max:
                shift_flag = True
            elif len(object_sort) == 2 and shift_one[2] - size_one[2] / 2 - z_min > depth_max / 2:
                shift_flag = True
        else:
            break
        if shift_flag:
            depth_1, depth_2 = z_min, z_min
            if 0 <= object_idx - 1 < len(object_sort):
                object_1 = object_sort[object_idx - 1]
                shift_1 = object_1['relate_shifting']
                size_1 = [abs(object_1['size'][i] * object_1['scale'][i]) / 100 for i in range(3)]
                if shift_1[0] - size_1[0] / 2 >= shift_one[0] + size_one[0] / 2:
                    depth_1 = z_min
                elif shift_1[2] + size_1[2] / 2 >= shift_one[2] - size_one[2] / 2:
                    depth_1 = z_min
                else:
                    depth_1 = shift_1[2] + size_1[2] / 2
            if 0 <= object_idx + 1 < len(object_sort):
                object_2 = object_sort[object_idx + 1]
                shift_2 = object_2['relate_shifting']
                size_2 = [abs(object_2['size'][i] * object_2['scale'][i]) / 100 for i in range(3)]
                if shift_2[0] + size_2[0] / 2 <= shift_one[0] - size_one[0] / 2:
                    depth_2 = z_min
                elif shift_2[2] + size_2[2] / 2 >= shift_one[2] - size_one[2] / 2:
                    depth_2 = z_min
                else:
                    depth_2 = shift_2[2] + size_2[2] / 2
            depth_0, depth_d = shift_one[2], 0
            shift_one[2] = min(max(depth_1, depth_2) + size_one[2] / 2 - depth_d, depth_0)

    # 排除
    delta_max = 0.10
    delta_set = ['584c0af5-de65-4c15-9c04-881ffa2dad1f', '0f78d235-4dbe-4cf0-9e32-fdd3ab3323b9',
                 'feb90f54-e9c2-435b-88e1-2816e7a5af72']
    for object_idx in range(len(object_sort) - 1, -1, -1):
        if plat_role in ['sofa', 'chair']:
            pass
        elif plat_role in ['cabinet', 'table']:
            pass
        else:
            break
        object_one = object_sort[object_idx]
        shift_one = object_one['relate_shifting']
        angle_one = rot_to_ang(object_one['normal_rotation'])
        size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        if shift_one[2] + size_one[2] / 2 > z_min + depth_max + delta_max:
            if len(object_sort) > 1:
                object_sort.pop(object_idx)
                continue
        if object_idx - 1 >= 0:
            object_old = object_sort[object_idx - 1]
            shift_old = object_old['relate_shifting']
            if abs(shift_one[0] - shift_old[0]) < 0.1 and abs(shift_one[2] - shift_old[2]) < 0.1:
                if abs(shift_one[0] - shift_old[0]) < max(size_one[0], size_one[2]) and size_one[0] < 0.15:
                    object_sort.pop(object_idx)
                    continue
    # 分组
    object_move, object_same = [], []
    step_max, step_min = 0.10, 0.05
    if plat_role in ['sofa', 'chair']:
        step_max, step_min = 5.00, 0.01
    elif group_type not in ['Meeting'] and plat_role in ['table']:
        step_max, step_min = 0.10, 0.02
    for object_idx, object_one in enumerate(object_sort):
        # 相同
        if len(object_same) <= 0:
            object_same.append([object_idx, 1])
        else:
            side_idx = object_same[-1][0]
            side_one = object_sort[side_idx]
            if side_one['id'] == object_one['id']:
                object_same[-1][1] += 1
            else:
                object_same.append([object_idx, 1])
        # 移动
        if object_idx <= 0:
            continue
        object_old = object_sort[object_idx - 1]
        shift_old = object_old['relate_shifting']
        size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
        shift_one = object_one['relate_shifting']
        size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        object_step = (shift_old[0] - size_old[0] / 2) - (shift_one[0] + size_one[0] / 2)
        if plat_role in plat_role in ['sofa', 'chair']:
            if shift_old[2] + size_old[2] / 2 < shift_one[2] - size_one[2] + 0.10:
                object_step = 0
            elif shift_old[2] - size_old[2] / 2 > shift_one[2] + size_one[2] - 0.10:
                object_step = 0
        # 移动
        if object_one['id'] in delta_set:
            object_step = -0.1
            object_move.append([object_idx, object_step])
        elif abs(object_step) > 0.05 and plat_role in ['sofa', 'chair']:
            object_move.append([object_idx, object_step * 0.5])
        elif -0.03 < object_step < 0 and plat_role in ['table', 'cabinet']:
            object_move.append([object_idx, object_step])
        elif object_step > step_max:
            object_step = object_step - step_min
            object_move.append([object_idx, object_step])
    # 移动
    for object_idx, object_one in enumerate(object_sort):
        if len(object_move) <= 0:
            break
        for move_one in object_move:
            if object_idx >= move_one[0]:
                object_one['relate_shifting'][0] += move_one[1]
    # 删除
    same_max = 1
    if group_type in ['Meeting', 'Media', 'Cabinet']:
        object_dump = -1
        for same_one in object_same:
            if same_one[1] >= same_max + 1:
                object_dump = same_one[0] + same_max
                break
        if 0 < object_dump < len(object_sort):
            for object_idx in range(len(object_sort) - 1, -1, -1):
                if object_idx >= object_dump:
                    object_sort.pop(object_idx)
    # 补充
    if width_max <= UNIT_WIDTH_PLAT_SINGLE:
        return object_sort, unique_more
    # 现有
    x_max, x_min = deco_info[3], deco_info[3]
    if len(object_sort) > 0:
        # 右侧
        object_side_2 = object_sort[0]
        shift_side_2 = object_side_2['relate_shifting']
        angle_side_2 = rot_to_ang(object_side_2['normal_rotation'])
        size_side_2 = [abs(object_side_2['size'][i] * object_side_2['scale'][i]) / 100 for i in range(3)]
        # 左侧
        object_side_1 = object_sort[-1]
        shift_side_1 = object_side_1['relate_shifting']
        angle_side_1 = rot_to_ang(object_side_1['normal_rotation'])
        size_side_1 = [abs(object_side_1['size'][i] * object_side_1['scale'][i]) / 100 for i in range(3)]
        if len(object_sort) <= 2:
            angle_side_2, object_side_2['normal_rotation'] = 0, [0, 0, 0, 1]
            angle_side_1, object_side_1['normal_rotation'] = 0, [0, 0, 0, 1]
        # 范围
        x_min_side_2, x_max_side_2 = shift_side_2[0] - size_side_2[0] / 2, shift_side_2[0] + size_side_2[0] / 2
        x_min_side_1, x_max_side_1 = shift_side_1[0] - size_side_1[0] / 2, shift_side_1[0] + size_side_1[0] / 2
        if abs(angle_side_2 - math.pi / 2) < 0.1 or abs(angle_side_2 + math.pi / 2) < 0.1:
            x_min_side_2, x_max_side_2 = shift_side_2[0] - size_side_2[2] / 2, shift_side_2[0] + size_side_2[2] / 2
        if abs(angle_side_1 - math.pi / 2) < 0.1 or abs(angle_side_1 + math.pi / 2) < 0.1:
            x_min_side_1, x_max_side_1 = shift_side_1[0] - size_side_1[2] / 2, shift_side_1[0] + size_side_1[2] / 2

        if x_min_side_1 >= x_min_side_2:
            shift_side_1[0] += (x_min_side_2 - 0.01 - x_min_side_1)
            x_min_side_1 = x_min_side_2 - 0.01
        elif x_max_side_2 <= x_max_side_1:
            shift_side_2[0] += (x_max_side_1 + 0.01 - x_max_side_2)
            x_max_side_2 = x_max_side_1 + 0.01
        x_max = max(x_max_side_2, x_max_side_1)
        x_min = min(x_min_side_2, x_min_side_1)

    # 补充
    width_add, count_max = 0.1, 10
    if group_type in ['Meeting'] and plat_role in ['sofa', 'chair']:
        width_add, count_max = 0.4, 6
    elif group_type in ['Meeting', 'Rest'] and plat_role in ['table']:
        width_add, count_max = 0.1, 5
    elif group_type in ['Meeting', 'Bed'] and plat_role in ['side table']:
        width_add, count_max = 0.1, 5
    elif group_type in ['Media'] and plat_role in ['table']:
        width_add, count_max = 0.1, 5
    elif group_type in ['Work'] and plat_role in ['table']:
        width_add, count_max = 0.1, 5
    elif group_type in ['Cabinet'] and plat_role in ['cabinet']:
        if '玄关柜' in plat_cate:
            width_add, count_max = 0.1, 10
        elif '鞋柜' in plat_cate:
            width_add, count_max = 0.1, 10
        else:
            width_add, count_max = 0.1, 6
    if '化妆品' in unique_type:
        width_add, count_max = 0.1, 3
    elif '洗浴品' in unique_type:
        width_add, count_max = 0.1, 3
    elif '儿童' in unique_type or '玩具' in unique_type:
        width_add, count_max = 0.1, 3

    if len(object_more) <= 0:
        object_more = object_list
    if len(object_more) <= 0:
        return object_sort, unique_more
    width_obj, start_obj = x_max - x_min, random.randint(0, 100) % len(object_more)
    width_cnt = min(int((width_max - width_obj) / width_add), count_max - len(object_sort))
    for i in range(width_cnt):
        if len(object_more) <= 0:
            break
        # 原有
        object_old = object_sort[i % len(object_sort)]
        shift_old = object_old['relate_shifting']
        size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
        # 复制
        object_one = copy_object(object_more[(start_obj + i) % len(object_more)])
        # 替换
        replace_step = 0.02
        replace_type = unique_type
        if i >= len(object_more) and unique_type == '':
            replace_type = unique_side_1[i % len(unique_side_1)]
            replace_step = 0.02
        elif i >= len(object_more) and plat_role in ['table', 'side table'] and group_type in ['Meeting', 'Rest']:
            replace_type = unique_side_1[i % len(unique_side_1)]
            replace_step = 0.02
        elif i >= width_cnt - 1 and i >= 1 and width_max - (x_max - x_min) > 0.30:
            if group_type in ['Meeting', 'Work', 'Rest'] and plat_role in ['table']:
                replace_type = unique_side_1[i % len(unique_side_1)]
                replace_step = 0.02
        # 补充
        if not replace_type == '':
            unique_more += 1
            object_old = compute_deco_raise(unique_more, replace_type)
            if len(object_old) > 0:
                object_one['id'] = object_old['id']
                object_one['type'] = object_old['type']
                object_one['style'] = object_old['style']
                object_one['size'] = object_old['size'][:]
                object_one['scale'] = object_old['scale'][:]
                object_one['normal_rotation'] = [0, 0, 0, 1]
        object_new = copy_object(object_one)
        object_new['relate_shifting'] = object_one['relate_shifting'][:]
        size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
        if 'pillow' in object_new['type']:
            object_new['normal_rotation'] = [0, 0, 0, 1]
        # 替换
        elif (size_new[2] > depth_max or size_new[1] > deco_info[6] or object_new['id'] in object_used) and \
                plat_role in ['cabinet', 'table']:
            unique_more += 1
            random_type = unique_type
            if len(random_type) < 0:
                random_type = '配饰'
            object_add = compute_deco_raise(unique_more, random_type, '', object_used)
            if len(object_add) > 0:
                object_new['id'] = object_add['id']
                object_new['type'] = object_add['type']
                object_new['style'] = object_add['style']
                object_new['size'] = object_add['size'][:]
                object_new['scale'] = object_add['scale'][:]
                size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
        # 宽度
        width_new, depth_new = size_new[0], size_new[2]
        width_min = 0.15
        if unique_type in ['化妆品', '洗浴品'] or width_new < 0.10:
            width_min = 0.10
        if '餐边柜' in plat_cate and len(object_list) >= 3:
            replace_step = 0.03
        replace_step = max(replace_step, width_min - width_new)
        # 角度
        angle_new = rot_to_ang(object_one['normal_rotation'])
        if abs(angle_new - math.pi) < 0.1 or abs(angle_new + math.pi) < 0.1:
            angle_new = 0
            object_new['normal_rotation'] = [0, 0, 0, 1]
        if abs(angle_new - math.pi / 2) < 0.1 or abs(angle_new + math.pi / 2) < 0.1:
            angle_new = 0
            object_new['normal_rotation'] = [0, 0, 0, 1]

        # 更新
        shift_new = object_new['relate_shifting']
        if (plat_role in ['table', 'side table'] and '梳妆台' not in plat_cate) or '餐边柜' in plat_cate:
            if i % 2 == 0:
                shift_new[0] = x_min - replace_step - width_new / 2
                x_min = shift_new[0] - width_new / 2 - replace_step
            else:
                shift_new[0] = x_max + replace_step + width_new / 2
                x_max = shift_new[0] + width_new / 2 + replace_step
        else:
            shift_new[0] = x_min - replace_step - width_new / 2
            x_min = shift_new[0] - width_new / 2 - replace_step
        shift_new[1] = shift_old[1]
        shift_new[2] = z_min + depth_new
        if depth_new > depth_max * 0.8:
            shift_new[2] = z_min + depth_new / 2
        elif z_max - depth_new / 2 > z_min + depth_new / 2:
            shift_max = z_max - depth_new / 2 - (z_min + depth_new / 2)
            shift_new[2] = z_min + depth_new / 2 + shift_max * 0.2 + shift_max * random.randint(0, 40) / 100
        object_sort.append(object_new)
        # 判断
        if x_max - x_min > width_max:
            break
    # 返回
    return object_sort, unique_more


# 家具装饰补充
def compute_deco_raise(deco_idx, deco_set='', deco_id='', deco_used={}):
    raise_object_list = get_furniture_list_id(deco_set)
    if len(raise_object_list) <= 0:
        return {}
    object_id = raise_object_list[deco_idx % len(raise_object_list)]
    if not deco_id == '':
        if deco_id in raise_object_list:
            object_id = deco_id
    elif object_id in deco_used:
        for i in range(5):
            deco_idx += 1
            object_id = raise_object_list[deco_idx % len(raise_object_list)]
            if object_id not in deco_used:
                break
    object_type, object_style, object_size = get_furniture_data(object_id)
    object_new = {
        'id': object_id, 'type': object_type, 'style': object_style,
        'size': object_size[:], 'scale': [1, 1, 1]
    }
    return object_new


# 家具装饰递减
def compute_deco_small(object_old, deco_idx, deco_used={}):
    cate_old = get_furniture_cate(object_old['id'])
    cate_new = cate_old
    if '化妆品组合3' in cate_old:
        cate_new = '化妆品组合2'
    elif '化妆品组合2' in cate_old:
        cate_new = '化妆品组合1'
    elif '化妆品组合1' in cate_old:
        cate_new = '化妆品'
    elif '洗浴品组合2' in cate_old:
        cate_new = '洗浴品组合1'
    elif '洗浴品组合1' in cate_old:
        cate_new = '洗浴品'
    else:
        return
    object_new = compute_deco_raise(deco_idx, cate_new, '', deco_used)
    object_old['id'] = object_new['id']
    object_old['type'] = object_new['type']
    object_old['style'] = object_new['style']
    object_old['size'] = object_new['size'][:]
    object_old['scale'] = object_new['scale'][:]


# 家具分析并发
class AsyncShape(multiprocessing.Process):
    # 并行处理构造
    def __init__(self, input_new, output_new):
        multiprocessing.Process.__init__(self)
        self.input_set = input_new
        self.output_set = output_new

    # 并行处理执行
    def run(self):
        shape_dict = {}
        print('% 6d' % self.pid, 'from', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
        for object_one in self.input_set:
            object_key, object_type, object_size = object_one['id'], object_one['type'], object_one['size']
            if object_key in UNIT_SHAPE_LOCAL:
                object_val = get_furniture_plat(object_key, object_type)
            else:
                object_val = get_furniture_plat(object_key, object_type)
            shape_dict[object_key] = object_val
        self.output_set.put(shape_dict)
        print('% 6d' % self.pid, 'done', datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    pass


# 功能测试
if __name__ == '__main__':
    pass
