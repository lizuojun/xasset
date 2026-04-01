# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-18
@Description: 家具组合布局

"""

from Furniture.furniture_group import *

# 组合布局
GROUP_LAYOUT_DICT = {}

# 组合布局示例
GROUP_LAYOUT_RULE = {
    'Meeting': {
        'table': [
            [0.0, 0.5, 0.0, 0.5, 0.00]
         ],
        'side sofa': [
            [-0.5, 0.5, -0.5, 0.5, 1.57],
            [0.5, 0.5, 0.5, 0.5, -1.57],
            [-0.5, 0.5, -0.5, 1.5, 1.57],
            [0.5, 0.5, 0.5, 1.5, -1.57]
        ],
        'side table': [
            [-0.5, 0.0, -0.5, 0.0, 0.00],
            [0.5, 0.0, 0.5, 0.0, 0.00]
        ],
        'count': 9,
        'sequence': ['table', 'side sofa', 'side table'],
        'scheme': []
    },
    'Dining3': {
        'chair': [
            [0.0, -0.5, -1.0, -0.5, 0.00],
            [0.0, -0.5, 0.0, -0.5, 0.00],
            [0.0, -0.5, 1.0, -0.5, 0.00],
            [0.0, 0.5, -1.0, 0.5, 3.14],
            [0.0, 0.5, 0.0, 0.5, 3.14],
            [0.0, 0.5, 1.0, 0.5, 3.14],
            [-0.5, 0.0, -1.0, 0.0, 1.57],
            [0.5, 0.0, 1.0, 0.0, -1.57]
        ],
        'count': 8,
        'sequence': ['chair'],
        'scheme': []
    },
    'Dining2': {
        'chair': [
            [0.0, -0.5, -0.5, -0.5, 0.00],
            [0.0, -0.5, 0.5, -0.5, 0.00],
            [0.0, 0.5, -0.5, 0.5, 3.14],
            [0.0, 0.5, 0.5, 0.5, 3.14],
            [-0.5, 0.0, -0.5, 0.0, 1.57],
            [0.5, 0.0, 0.5, 0.0, -1.57]
        ],
        'count': 6,
        'sequence': ['chair'],
        'scheme': []
    },
    'Dining1': {
        'chair': [
            [0.0, -0.5, 0.0, -0.5, 0.00],
            [0.0, 0.5, 0.0, 0.5, 3.14],
            [-0.5, 0.0, -0.5, 0.0, 1.57],
            [0.5, 0.0, 0.5, 0.0, -1.57]
        ],
        'count': 4,
        'sequence': ['chair'],
        'scheme': []
    },
    'Dining0': {
        'chair': [],
        'count': 0,
        'sequence': ['chair'],
        'scheme': []
    },
    'Bed': {
        'side table': [
            [-0.5, -0.5, -0.5, 0.5, 0.00],
            [0.5, -0.5, 0.5, 0.5, 0.00]
        ],
        'table': [
            [0.0, 0.5, 0.0, 0.5, 0.00]
         ],
        'count': 3,
        'sequence': ['side table', 'table'],
        'scheme': []
    },
    'Media': {
        'table': [
            [0.0, 0, 0.0, 0]
        ],
        'side table': [
            [-0.5, -0.5, -0.5, 0.5, 0.00],
            [0.5, -0.5, 0.5, 0.5, 0.00]
        ],
        'count': 3,
        'sequence': ['table', 'side table'],
        'scheme': []
    },
    'Work': {
        'chair': [
            [0.0, -0.5, 0.0, -0.5, 0.00],
            [0.0, 0.5, 0.0, 0.5, 3.14],
            [-0.5, 0.0, -0.5, 0.0, 1.57],
            [0.5, 0.0, 0.5, 0.0, -1.57]
        ],
        'count': 4,
        'sequence': ['chair'],
        'scheme': []
    },
    'Rest': {
        'chair': [
            [0.0, -0.5, 0.0, -0.5, 0.00],
            [0.0, 0.5, 0.0, 0.5, 3.14],
            [-0.5, 0.0, -0.5, 0.0, 1.57],
            [0.5, 0.0, 0.5, 0.0, -1.57]
        ],
        'count': 4,
        'sequence': ['chair'],
        'scheme': []
    }
}

# 无效布局
INVALID_CODE_NUMBER = 1000


# 数据解析：加载组合布局
def load_group_layout(reload=False):
    global GROUP_LAYOUT_DICT
    if len(GROUP_LAYOUT_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_group_form.json')
        GROUP_LAYOUT_DICT = {}
        if os.path.exists(json_path):
            try:
                GROUP_LAYOUT_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return GROUP_LAYOUT_DICT


# 数据解析：保存组合布局
def save_group_layout():
    global GROUP_LAYOUT_DICT
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_group_form.json')
    with open(json_path, "w") as f:
        json.dump(GROUP_LAYOUT_DICT, f, indent=4)
        f.close()
    print('save group layout success')


# 数据解析：清空组合布局
def clear_group_layout():
    global GROUP_LAYOUT_DICT
    GROUP_LAYOUT_DICT.clear()
    print('clear group layout success')
    save_group_layout()
    # 重置
    GROUP_LAYOUT_DICT = GROUP_LAYOUT_RULE.copy()


# 数据解析：增加组合布局
def add_group_layout(layout_info):
    if len(layout_info) <= 0:
        return
    object_type = layout_info['object_type']
    layout_base = layout_info['layout_base']
    layout_code = layout_info['layout_code']
    if len(layout_code) <= 0:
        return

    global GROUP_LAYOUT_DICT
    load_group_layout()
    if layout_base not in GROUP_LAYOUT_DICT:
        return

    # 查找布局
    layout_find = False
    layout_dict = GROUP_LAYOUT_DICT[layout_base]
    for layout_one in layout_dict['scheme']:
        layout_code_old = layout_one['layout_code']
        if not check_group_layout(layout_code_old, layout_code):
            continue
        # 增加记录
        layout_one['layout_count'] += 1
        if object_type not in layout_one['object_type']:
            layout_one['object_type'].append(object_type)
        layout_find = True
        break
    # 增加布局
    if not layout_find:
        layout_one = {
            'object_type': [object_type],
            'layout_code': layout_code,
            'layout_count': 1
        }
        layout_dict['scheme'].append(layout_one)
    pass


# 数据解析：获取组合布局
def get_group_layout():
    pass


# 数据解析：提取组合布局
def parse_group_layout(group_info):
    # 布局信息
    layout_info = {
        'object_type': '',
        'layout_size': [],
        'layout_base': '',
        'layout_code': [],
        'layout_object': []
    }
    if len(group_info['obj_list']) < 0:
        return layout_info

    # 基本信息
    obj_main = group_info['obj_list'][0]
    main_type = obj_main['type']
    main_size = [width_i / 100 for width_i in obj_main['size']]
    layout_info['object_type'] = main_type
    layout_info['layout_size'] = group_info['size'][:]
    # 数量判断
    obj_cnt = 0
    for obj_one in group_info['obj_list']:
        obj_role = obj_one['role']
        if obj_role in ['accessory', 'rug']:
            continue
        obj_cnt += 1
    if obj_cnt <= 1:
        return layout_info

    # 组合信息
    layout_base = group_info['type']
    if layout_base == 'Dining':
        if main_type == 'table/dining table - round':
            layout_base += '0'
        else:
            table_width = abs(main_size[0])
            chair_width = 1
            for obj_one in group_info['obj_list']:
                obj_role = obj_one['role']
                if obj_role == 'chair':
                    chair_width = abs(obj_one['size'][0] / 100)
                    break
            if chair_width <= 0:
                chair_width = 1
            chair_count = int(table_width / chair_width)
            if chair_count > 3:
                chair_count = 3
            layout_base += str(chair_count)
    layout_info['layout_base'] = layout_base
    if layout_base not in GROUP_LAYOUT_RULE:
        return layout_info
    if layout_base in ['Dining0', 'Media']:
        return layout_info

    # 布局信息
    layout_rule = GROUP_LAYOUT_RULE[layout_base]
    layout_sequence = layout_rule['sequence']
    layout_count = layout_rule['count']
    layout_code = [INVALID_CODE_NUMBER] * (layout_count * 3)
    layout_object = [''] * layout_count
    # 遍历家具
    for obj_one in group_info['obj_list']:
        obj_id = obj_one['id']
        obj_role = obj_one['role']
        if obj_role not in layout_sequence:
            continue
        obj_size = [width_i / 100 for width_i in obj_one['size']]
        obj_position = obj_one['position']
        obj_rotation = obj_one['rotation']
        obj_angle = rot_to_ang(obj_rotation)
        # 家具布局
        obj_code = [INVALID_CODE_NUMBER] * 3
        obj_code_idx = 0
        for role_one in layout_sequence:
            if not role_one == obj_role:
                obj_code_idx += len(layout_rule[role_one])
                continue
            best_idx = 0
            best_dis = 100
            best_dis_x = 0
            best_dis_z = 0
            best_ang = 0
            for base_idx, base_one in enumerate(layout_rule[role_one]):
                dis_x = obj_position[0] - (base_one[0] * main_size[0] + base_one[2] * obj_size[0])
                dis_z = obj_position[2] - (base_one[1] * main_size[2] + base_one[3] * obj_size[2])
                dis_xz = dis_x * dis_x + dis_z * dis_z
                if dis_xz < best_dis:
                    best_idx = base_idx
                    best_dis = dis_xz
                    best_dis_x = dis_x
                    best_dis_z = dis_z
                    best_ang = base_one[4]
            # 校正角度
            if abs(obj_angle - best_ang) > math.pi * 0.25 and obj_role == 'chair':
                obj_angle = best_ang
            obj_code = [best_dis_x, best_dis_z, obj_angle]
            obj_code = [round(i, 2) for i in obj_code]
            obj_code_idx += best_idx
            break
        layout_code[obj_code_idx * 3 + 0] = obj_code[0]
        layout_code[obj_code_idx * 3 + 1] = obj_code[1]
        layout_code[obj_code_idx * 3 + 2] = obj_code[2]
        layout_object[obj_code_idx] = obj_id
    layout_info['layout_code'] = layout_code
    layout_info['layout_object'] = layout_object
    # 返回信息
    return layout_info


# 数据解析：比较布局编码
def check_group_layout(code_old, code_new, code_dlt=0.05):
    if not len(code_old) == len(code_new):
        return False
    for i in range(len(code_old)):
        if code_dlt < abs(code_old[i] - code_new[i]) < INVALID_CODE_NUMBER / 10:
            return False
    return True


# 数据生成：应用组合布局 TODO:
def apply_group_layout(object_list, group_type='', group_style='', layout_num=3):
    # 返回信息
    group_list = []
    # 查找种子 TODO:
    if len(object_list) <= 0:
        if len(group_type) <= 0:
            group_type = 'Meeting'
        pass
    # 查找组合 TODO:
    if len(object_list) <= 1:
        pass
    # 查找布局 TODO:
    else:
        # 分配角色

        # 布局角色
        pass
    # 组合补充 TODO: 地毯 壁画 绿植
    for group_one in group_list:
        raise_group_layout(group_one)

    # 返回信息
    return group_list


# 数据生成：提升组合布局 TODO:
def raise_group_layout(group_info, object_have=[], object_todo=[]):
    pass


# 数据加载
load_group_layout()


# 功能测试
if __name__ == '__main__':
    # 更新所有分组布局信息
    furniture_group_all = load_furniture_group()
    for house_id, room_dict in furniture_group_all.items():
        for room_id, group_list in room_dict.items():
            for group_one in group_list:
                group_type = group_one['type']
                if group_type not in ['Meeting', 'Bed', 'Dining']:
                    continue
                layout_info = parse_group_layout(group_one)
                add_group_layout(layout_info)
    save_group_layout()
