# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-06-27
@Description: 默认家具打组 补充布局模板
"""

from Furniture.furniture import *


# 默认分组
DEFAULT_GROUP_DICT = {}
# 默认家具
DEFAULT_OBJECT_DICT = {}


# 数据解析：加载组合数据
def load_default_group(reload=False):
    global DEFAULT_GROUP_DICT
    global DEFAULT_OBJECT_DICT
    if len(DEFAULT_GROUP_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_group_def.json')
        if os.path.exists(json_path):
            try:
                json_info = json.load(open(json_path, 'r'))
                if 'Group' in json_info:
                    DEFAULT_GROUP_DICT = json_info['Group']
                if 'Object' in json_info:
                    DEFAULT_OBJECT_DICT = json_info['Object']
            except Exception as e:
                print(e)


# 数据解析：保存打组数据
def save_default_group():
    # 默认组合
    global DEFAULT_GROUP_DICT
    global DEFAULT_OBJECT_DICT
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_group_def.json')
    with open(json_path, 'w') as f:
        json_info = {'Group': DEFAULT_GROUP_DICT,
                     'Object': DEFAULT_OBJECT_DICT}
        json.dump(json_info, f, indent=4)
        f.close()
    # 打印信息
    print('save default group success')


# 修复默认分组
def fix_default_group():
    global DEFAULT_GROUP_DICT
    for group_key, group_one in DEFAULT_GROUP_DICT.items():
        obj_list = []
        if 'obj_list' in group_one:
            obj_list = group_one['obj_list']
        if len(obj_list) <= 0:
            continue
        obj_main = obj_list[0]
        # 家具分组
        group_type = group_one['type']
        group_one['position'] = obj_main['position'][:]
        group_one['rotation'] = obj_main['rotation'][:]
        group_one['position'][1] = 0
        # 家具信息
        id_main, type_main, role_main = obj_main['id'], obj_main['type'], obj_main['role']
        size_main = [obj_main['size'][i] * obj_main['scale'][i] / 100 for i in range(3)]
        lift_main = obj_main['position'][1]
        pos_adjust = [0 - group_one['position'][0], 0 - group_one['position'][1], 0 - group_one['position'][2]]
        ang_adjust = 0 - rot_to_ang(group_one['rotation'])
        if group_type in ['Cabinet', 'Armoire'] and lift_main > 0.05 and size_main[1] > 1.50:
            pos_adjust[1] = 0 - lift_main
        # 家具整理
        for obj_one in obj_list:
            # 记录位置
            origin_position = obj_one['position'][:]
            origin_rotation = obj_one['rotation'][:]
            normal_position = [0, 0, 0]
            normal_rotation = [0, 0, 0, 1]
            obj_one['adjust_position'] = [0, 0, 0]
            obj_one['origin_position'] = origin_position[:]
            obj_one['origin_rotation'] = origin_rotation[:]
            obj_one['normal_position'] = normal_position[:]
            obj_one['normal_rotation'] = normal_rotation[:]
            # 规范位置
            pos_old_x = origin_position[0] + pos_adjust[0]
            pos_old_y = origin_position[1] + pos_adjust[1]
            pos_old_z = origin_position[2] + pos_adjust[2]
            pos_new_x = pos_old_z * math.sin(ang_adjust) + pos_old_x * math.cos(ang_adjust)
            pos_new_y = pos_old_y
            pos_new_z = pos_old_z * math.cos(ang_adjust) - pos_old_x * math.sin(ang_adjust)
            # 规范朝向
            ang_old = rot_to_ang(origin_rotation)
            ang_new = ang_to_ang(ang_old + ang_adjust)
            # 更新信息
            normal_position = [pos_new_x, pos_new_y, pos_new_z]
            normal_rotation = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
            # 原始位置
            obj_one['origin_position'] = origin_position[:]
            obj_one['origin_rotation'] = origin_rotation[:]
            # 规范位置
            obj_one['normal_position'] = normal_position[:]
            obj_one['normal_rotation'] = normal_rotation[:]
            pass
    save_default_group()


# 获取默认分组
def get_default_group(input_type):
    global DEFAULT_GROUP_DICT
    # 分组细节
    group_one = {}
    if input_type in DEFAULT_GROUP_DICT:
        group_one = DEFAULT_GROUP_DICT[input_type]
    return group_one


# 获取默认分组
def get_default_group_main(group_type, group_main, group_size=[]):
    global DEFAULT_GROUP_DICT
    group_list = []
    for group_one in DEFAULT_GROUP_DICT.values():
        if 'type' not in group_one:
            continue
        if group_one['type'] == group_type:
            if group_one['obj_main'] == group_main or group_main == '':
                group_list.append(group_one)
    group_cur = {}
    delta_cur = 100
    for group_one in group_list:
        if len(group_size) <= 0:
            return group_one
        delta_new = 0
        delta_new += abs(group_one['size'][0] - group_size[0])
        delta_new += abs(group_one['size'][1] - group_size[1])
        delta_new += abs(group_one['size'][2] - group_size[2])
        if delta_new < delta_cur:
            delta_cur = delta_new
            group_cur = group_one
    return group_cur


# 获取默认分组
def get_default_group_list(input_type):
    global DEFAULT_GROUP_DICT
    # 分组细节
    group_list = []
    for sample_type, group_one in DEFAULT_GROUP_DICT.items():
        if input_type in sample_type:
            group_list.append(group_one)
    return group_list


# 获取默认分组
def get_default_group_layout(input_type):
    global DEFAULT_GROUP_DICT
    # 分组细节
    group_one = {}
    if input_type in DEFAULT_GROUP_DICT:
        group_one = DEFAULT_GROUP_DICT[input_type]
    # 分组信息
    group_layout = {}
    if len(group_one) > 0:
        group_layout = {
            'type': group_one['type'],
            'code': group_one['code'],
            'size': group_one['size'][:],
            'offset': group_one['offset'][:],
            'position': group_one['position'][:],
            'rotation': group_one['rotation'][:],
            'size_min': group_one['size'][:],
            'size_rest': [0, 0, 0, 0],
            'obj_main': group_one['obj_main'],
            'obj_type': group_one['obj_type'],
            'obj_list': [],
            'seed_list': [],
            'adjust': 1
        }
        # 更新尺寸
        group_size = group_one['size'][:]
        group_offset = group_one['offset']
        origin_size = group_one['obj_list'][0]['size']
        origin_scale = group_one['obj_list'][0]['scale']
        object_size = [origin_size[i] * origin_scale[i] / 100 for i in range(3)]
        width_rest1 = group_offset[0] - object_size[0] / 2 + group_size[0] / 2
        width_rest2 = group_size[0] / 2 - group_offset[0] - object_size[0] / 2
        depth_rest1 = group_offset[2] - object_size[2] / 2 + group_size[2] / 2
        depth_rest2 = group_size[2] / 2 - group_offset[2] - object_size[2] / 2
        group_layout['size_min'] = object_size[:]
        group_layout['size_rest'] = [depth_rest1, width_rest1, depth_rest2, width_rest2]
    return group_layout


# 获取默认分组
def get_default_group_layout_list(input_type):
    global DEFAULT_GROUP_DICT
    # 分组细节
    group_layout_list = []
    for sample_type, group_one in DEFAULT_GROUP_DICT.items():
        if input_type in sample_type:
            group_layout = get_default_group_layout(sample_type)
            group_layout_list.append(group_layout)
    return group_layout_list


# 获取默认物品
def get_default_object(group_type, object_role, room_type='', room_area=10):
    object_list = []
    if group_type in DEFAULT_OBJECT_DICT:
        for group_add in DEFAULT_OBJECT_DICT[group_type]:
            room_list, room_area_min = group_add['room'], group_add['area']
            if (room_type == '' or room_type in room_list) and room_area >= room_area_min:
                object_dict = group_add['object']
                for obj_role, obj_list in object_dict.items():
                    if object_role == '' or object_role == obj_role:
                        object_list = obj_list
                        break
            if len(object_list) > 0:
                break
    return object_list


# 增加默认物品
def add_default_object(group_one, room_type='', room_area=10):
    global DEFAULT_OBJECT_DICT
    group_type = group_one['type']
    if group_type not in DEFAULT_OBJECT_DICT:
        return
    # 组合沙发
    if group_type in ['Meeting']:
        if 'size' in group_one and len(group_one['size']) >= 3:
            group_size = group_one['size']
            if group_size[0] >= 3 and group_size[2] >= 2:
                if 'obj_list' in group_one and len(group_one['obj_list']) <= 1:
                    return
    # 其他物品
    for group_add in DEFAULT_OBJECT_DICT[group_type]:
        room_list, room_area_min = group_add['room'], group_add['area']
        # 物品
        object_dict, backup_dict, number_dict, attach_list = group_add['object'], {}, {}, []
        if 'backup' in group_add:
            backup_dict = group_add['backup']
        if 'number' in group_add:
            number_dict = group_add['number']
        if (room_type == '' or room_type in room_list) and room_area >= room_area_min:
            pass
        else:
            continue
        # 查找物品
        object_have, object_fine = group_one['obj_list'], []
        for object_role, object_list in object_dict.items():
            object_need, object_find = 1, 0
            if object_role in number_dict:
                object_need = number_dict[object_role]
            if len(object_list) <= 0:
                continue
            object_rand = random.randint(0, 100)
            backup_rand = random.randint(0, 100)
            object_new = object_list[object_rand % len(object_list)]
            new_id, new_role = object_new['id'], object_role
            new_type, new_relate = object_new['type'], object_new['relate']
            new_width = object_new['size'][0] * object_new['scale'][0]
            for object_old in object_have:
                old_id, old_role = object_old['id'], object_old['role']
                old_type, old_relate = object_old['type'], object_old['relate']
                old_width = object_old['size'][0] * object_old['scale'][0]
                if group_type in ['Wall']:
                    if old_role in ['art', 'mirror', 'accessory'] and new_role in ['art', 'mirror', 'accessory']:
                        old_role = new_role
                if old_role == new_role or old_id == new_id:
                    if 'count' not in object_old:
                        object_find += 1
                    elif object_old['count'] <= 2:
                        object_find += 1
                elif old_role in ['bath'] and new_role in ['screen']:
                    if 'count' not in object_old:
                        object_find += 1
                    elif object_old['count'] <= 2:
                        object_find += 1
                elif old_type == new_type and abs(old_width - new_width) < 0.5 and old_relate == new_relate:
                    if 'count' not in object_old:
                        object_find += 1
                    elif object_old['count'] <= 2:
                        object_find += 1
            object_need -= object_find
            if object_need <= 0:
                continue
            backup_list = []
            if new_id in backup_dict:
                backup_list = backup_dict[new_id]
            backup_list.insert(0, new_id)
            for backup_idx in range(object_need):
                # 增加物品
                object_add = new_default_object(object_new)
                add_id = backup_list[(backup_idx + backup_rand) % len(backup_list)]
                if not add_id == object_add['id']:
                    add_type, add_style, add_size = get_furniture_data(add_id)
                    object_add['id'] = add_id
                    object_add['type'], object_add['style'] = add_type, add_style
                    object_add['size'], object_add['scale'] = add_size[:], [1, 1, 1]
                object_fine.append(object_add)
                # 增加附着
                attach_list = []
                if 'attach' in object_add:
                    attach_list = object_add['attach']
                for attach_one in attach_list:
                    if 'relate' in attach_one and attach_one['relate'] == object_add['id']:
                        attach_add = new_default_object(attach_one)
                        object_fine.append(attach_add)
                object_add['attach'] = []
        # 添加物品
        for object_add in object_fine:
            group_one['obj_list'].append(object_add)


# 拷贝默认物品
def new_default_object(object_one):
    object_new = object_one.copy()
    object_new['size'] = object_one['size'][:]
    object_new['scale'] = object_one['scale'][:]
    object_new['position'] = object_one['position'][:]
    object_new['rotation'] = object_one['rotation'][:]
    if 'origin_position' in object_one:
        object_new['origin_position'] = object_one['origin_position'][:]
    if 'origin_rotation' in object_one:
        object_new['origin_rotation'] = object_one['origin_rotation'][:]
    if 'normal_position' in object_one:
        object_new['normal_position'] = object_one['normal_position'][:]
    if 'normal_rotation' in object_one:
        object_new['normal_rotation'] = object_one['normal_rotation'][:]
    if 'relate_position' in object_one:
        object_new['relate_position'] = object_one['relate_position'][:]
    return object_new


# 转化角度
def rot_to_ang(rot):
    rot_1 = rot[1]
    rot_3 = rot[3]
    if rot_1 > 1:
        rot_1 = 1
    elif rot_1 < -1:
        rot_1 = -1
    if rot_3 > 1:
        rot_3 = 1
    elif rot_3 < -1:
        rot_3 = -1
    # 计算
    ang = 0
    if abs(rot_1 - 1) < 0.0001 or abs(rot_1 + 1) < 0.0001:
        ang = math.pi
    elif abs(rot_3 - 1) < 0.0001 or abs(rot_3 + 1) < 0.0001:
        ang = 0
    else:
        if rot_1 >= 0 and rot_3 >= 0:
            ang = math.asin(rot_1) * 2
        elif rot_1 <= 0 and rot_3 >= 0:
            ang = math.asin(rot_1) * 2
        elif rot_1 >= 0 and rot_3 <= 0:
            ang = math.acos(rot_3) * 2
        elif rot_1 <= 0 and rot_3 <= 0:
            ang = -math.acos(rot_3) * 2
    # 规范
    if ang > math.pi * 2:
        ang -= math.pi * 2
    elif ang < -math.pi * 2:
        ang += math.pi * 2
    # 规范
    if ang > math.pi:
        ang -= math.pi * 2
    elif ang < -math.pi:
        ang += math.pi * 2
    # 返回
    return ang


# 规范角度
def ang_to_ang(angle_old):
    angle_new = angle_old
    # 计算
    if abs(angle_new - 2 * math.pi) <= 0.01:
        angle_new = 0
    elif abs(angle_new + 2 * math.pi) <= 0.01:
        angle_new = 0
    elif abs(angle_new - math.pi) <= 0.01:
        angle_new = math.pi
    elif abs(angle_new + math.pi) <= 0.01:
        angle_new = math.pi
    else:
        # 规范
        if angle_new > 2 * math.pi:
            angle_new -= 2 * math.pi
        elif angle_new < -2 * math.pi:
            angle_new += 2 * math.pi
        # 规范
        if angle_new <= -math.pi:
            angle_new += 2 * math.pi
        if angle_new > math.pi:
            angle_new -= 2 * math.pi
    # 返回
    return angle_new


# 数据加载
load_default_group()


# 功能测试
if __name__ == '__main__':
    fix_default_group()
    pass

