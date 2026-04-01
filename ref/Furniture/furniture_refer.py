# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-11-11
@Description: 家具类目

"""

import os
import json

# 家具参考字典
FURNITURE_REFER_DICT = {}
FURNITURE_REFER_ITEM = {}

# 家具类型字典
furniture_type_dict_en = {}
# 家具风格字典
furniture_style_dict_ch = {}
furniture_style_dict_en = {}
furniture_style_dict_id_1 = {}
furniture_style_dict_id_2 = {}
# 家具风格对照
furniture_style_dict_room = {}
# 家具风格对照
furniture_style_dict_object = {}
# 家具品类字典
furniture_category_dict_id_1 = {}
furniture_category_dict_id_2 = {}
# 家具品类对照
furniture_category_dict_room = {}
furniture_category_dict_role = {}
furniture_category_dict_role_map = {}
furniture_category_dict_type_1 = {}
furniture_category_dict_type_2 = {}
# 家具组合对照
furniture_role_dict_cate_set = {}
furniture_role_dict_cate_id = {}
# 家具角色对照
furniture_role_dict_jid = {}
furniture_size_dict_jid = {}
furniture_zone_dict_jid = {}


# 加载参考数据
def load_furniture_refer(reload=False):
    global FURNITURE_REFER_DICT
    global FURNITURE_REFER_ITEM
    global furniture_type_dict_en
    global furniture_style_dict_ch
    global furniture_style_dict_en
    global furniture_style_dict_id_1
    global furniture_style_dict_id_2
    global furniture_style_dict_room
    global furniture_style_dict_object
    global furniture_category_dict_id_1
    global furniture_category_dict_id_2
    global furniture_category_dict_room
    global furniture_category_dict_role
    global furniture_category_dict_role_map
    global furniture_category_dict_type_1
    global furniture_category_dict_type_2
    global furniture_role_dict_cate_set
    global furniture_role_dict_cate_id
    global furniture_role_dict_jid
    global furniture_size_dict_jid
    global furniture_zone_dict_jid
    # load
    if len(FURNITURE_REFER_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_refer_dict.json')
        FURNITURE_REFER_DICT = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_REFER_DICT = json.load(open(json_path, 'r', encoding='utf-8'))
            except Exception as e:
                print(e)
    if len(FURNITURE_REFER_ITEM) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_refer_item.json')
        FURNITURE_REFER_ITEM = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_REFER_ITEM = json.load(open(json_path, 'r', encoding='utf-8'))
            except Exception as e:
                print(e)

    # type
    if 'type' in FURNITURE_REFER_DICT:
        furniture_type_dict_en = FURNITURE_REFER_DICT['type']

    # style
    if 'style_id' in FURNITURE_REFER_DICT:
        furniture_style_dict_id_1 = FURNITURE_REFER_DICT['style_id']
        furniture_style_dict_id_2 = {}
        for style_name, style_id in furniture_style_dict_id_1.items():
            furniture_style_dict_id_2[style_id] = style_name
    # style
    if 'style_ch' in FURNITURE_REFER_DICT:
        furniture_style_dict_ch = FURNITURE_REFER_DICT['style_ch']
    if 'style_en' in FURNITURE_REFER_DICT:
        furniture_style_dict_en = FURNITURE_REFER_DICT['style_en']
    # style
    if 'style_room' in FURNITURE_REFER_DICT:
        furniture_style_dict_room = FURNITURE_REFER_DICT['style_room']
    if 'style_object' in FURNITURE_REFER_DICT:
        furniture_style_dict_object = FURNITURE_REFER_DICT['style_object']

    # category
    if 'category_id' in FURNITURE_REFER_DICT:
        furniture_category_dict_id_1 = FURNITURE_REFER_DICT['category_id']
        furniture_category_dict_id_2 = {}
        for category_name, category_id in furniture_category_dict_id_1.items():
            furniture_category_dict_id_2[category_id] = category_name
    if 'category_room' in FURNITURE_REFER_DICT:
        furniture_category_dict_room = FURNITURE_REFER_DICT['category_room']
    if 'category_role' in FURNITURE_REFER_DICT:
        furniture_category_dict_role = FURNITURE_REFER_DICT['category_role']
    if 'category_role_map' in FURNITURE_REFER_DICT:
        furniture_category_dict_role_map = FURNITURE_REFER_DICT['category_role_map']

    # type
    if 'type_category' in FURNITURE_REFER_DICT:
        furniture_category_dict_type_1 = FURNITURE_REFER_DICT['type_category']
        furniture_category_dict_type_2 = {}
        for type_old, cate_old in furniture_category_dict_type_1.items():
            cate_set = cate_old.split(' ')
            for cate_new in cate_set:
                furniture_category_dict_type_2[cate_new] = type_old
    # role
    if 'role_category' in FURNITURE_REFER_DICT:
        furniture_role_dict_cate_set = FURNITURE_REFER_DICT['role_category']
        for group_key, group_cate in furniture_role_dict_cate_set.items():
            cate_id_set = []
            for cate_one in group_cate:
                if cate_one in furniture_category_dict_id_1:
                    cate_id_one = furniture_category_dict_id_1[cate_one]
                    cate_id_set.append(cate_id_one)
            furniture_role_dict_cate_id[group_key] = cate_id_set

    # object
    if 'object_role' in FURNITURE_REFER_DICT:
        furniture_role_dict_jid = FURNITURE_REFER_DICT['object_role']
    if 'object_size' in FURNITURE_REFER_DICT:
        furniture_size_dict_jid = FURNITURE_REFER_DICT['object_size']
    if 'object_zone' in FURNITURE_REFER_DICT:
        furniture_zone_dict_jid = FURNITURE_REFER_DICT['object_zone']

    # refer
    return FURNITURE_REFER_DICT


# 保存参考数据
def save_furniture_refer():
    global FURNITURE_REFER_DICT
    # type
    if len(furniture_type_dict_en) > 0:
        FURNITURE_REFER_DICT['type'] = furniture_type_dict_en
    # style
    if len(furniture_style_dict_id_1) > 0:
        FURNITURE_REFER_DICT['style_id'] = furniture_style_dict_id_1
    # style
    if len(furniture_style_dict_ch) > 0:
        FURNITURE_REFER_DICT['style_ch'] = furniture_style_dict_ch
    if len(furniture_style_dict_en) > 0:
        FURNITURE_REFER_DICT['style_en'] = furniture_style_dict_en
    # style
    if len(furniture_style_dict_room) > 0:
        FURNITURE_REFER_DICT['style_room'] = furniture_style_dict_room
    if len(furniture_style_dict_object) > 0:
        FURNITURE_REFER_DICT['style_object'] = furniture_style_dict_object
    # category
    if len(furniture_category_dict_id_1) > 0:
        FURNITURE_REFER_DICT['category_id'] = furniture_category_dict_id_1
    if len(furniture_category_dict_room) > 0:
        FURNITURE_REFER_DICT['category_room'] = furniture_category_dict_room
    if len(furniture_category_dict_role) > 0:
        FURNITURE_REFER_DICT['category_role'] = furniture_category_dict_role
    if len(furniture_category_dict_role_map) > 0:
        FURNITURE_REFER_DICT['category_role_map'] = furniture_category_dict_role_map
    # category
    if len(furniture_category_dict_type_1) > 0:
        FURNITURE_REFER_DICT['type_category'] = furniture_category_dict_type_1
    if len(furniture_role_dict_cate_set) > 0:
        FURNITURE_REFER_DICT['role_category'] = furniture_role_dict_cate_set
    # object
    if len(furniture_role_dict_jid) > 0:
        FURNITURE_REFER_DICT['object_role'] = furniture_role_dict_jid
    if len(furniture_size_dict_jid) > 0:
        FURNITURE_REFER_DICT['object_size'] = furniture_size_dict_jid
    if len(furniture_zone_dict_jid) > 0:
        FURNITURE_REFER_DICT['object_zone'] = furniture_zone_dict_jid
    # save
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_refer_dict.json')
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(FURNITURE_REFER_DICT, f, indent=4, ensure_ascii=False)
        f.close()
    print('save furniture info success')


# 获取家具风格
def get_furniture_style_en(style_old):
    style_new = style_old
    if style_old.lower() in furniture_style_dict_en:
        style_old = furniture_style_dict_en[style_old.lower()]
    if style_old in furniture_style_dict_ch:
        style_new = furniture_style_dict_ch[style_old]
    if style_old not in furniture_style_dict_ch and style_old not in furniture_style_dict_en and not style_old == '':
        print(style_old)
    return style_new


# 获取家具风格
def get_furniture_style_id(style_old):
    style_new, style_id = style_old, ''
    if style_old.lower() in furniture_style_dict_en:
        style_old = furniture_style_dict_en[style_old.lower()]
    if style_old in furniture_style_dict_id_1:
        style_id = furniture_style_dict_id_1[style_old]
    return style_id


# 获取家具风格
def get_furniture_style_by_id(style_id):
    style_name = ''
    if style_id in furniture_style_dict_id_2:
        style_name = furniture_style_dict_id_2[style_id]
    return style_name


# 获取家具风格
def get_furniture_style_refer(style_old, refer_mode='room'):
    style_new, style_list, style_id_list = style_old, [], []
    if style_old in ['']:
        return style_new, style_list, style_id_list
    if style_old.lower() in furniture_style_dict_en:
        style_old = furniture_style_dict_en[style_old.lower()]
        style_new = style_old
    if style_old not in furniture_style_dict_ch:
        print(style_old)
    style_list = [style_new]
    if refer_mode == 'room':
        if style_old in furniture_style_dict_room:
            style_list = furniture_style_dict_room[style_old]
    else:
        if style_old in furniture_style_dict_object:
            style_list = furniture_style_dict_object[style_old]
    for style_one in style_list:
        if style_one in furniture_style_dict_id_1:
            style_id = furniture_style_dict_id_1[style_one]
            style_id_list.append(style_id)
    return style_new, style_list, style_id_list


# 获取风格参考
def get_furniture_style_refer_en(style_old, refer_mode='room'):
    style_new = ''
    if style_old.lower() in furniture_style_dict_en:
        style_old = furniture_style_dict_en[style_old.lower()]
        style_new = style_old
    style_list = [style_new]
    if refer_mode == 'room':
        if style_old in furniture_style_dict_room:
            style_list = furniture_style_dict_room[style_old]
    else:
        if style_old in furniture_style_dict_object:
            style_list = furniture_style_dict_object[style_old]
    style_list_en = []
    for style_one in style_list:
        if style_one in furniture_style_dict_ch:
            style_list_en.append(furniture_style_dict_ch[style_one])
    return style_list_en


# 获取家具类型
def get_furniture_category_by_id(category_id):
    category_name = ''
    if category_id in furniture_category_dict_id_2:
        category_name = furniture_category_dict_id_2[category_id]
    return category_name


# 获取家具房间
def get_furniture_room_by_category(category_id):
    category_name, room_type = '', ''
    if category_id in furniture_category_dict_id_2:
        category_name = furniture_category_dict_id_2[category_id]
    if category_name in furniture_category_dict_room:
        room_type = furniture_category_dict_room[category_name]
    else:
        category_name_0 = category_name.split('/')[0]
        if category_name_0 in furniture_category_dict_room:
            room_type = furniture_category_dict_room[category_name_0]
    return category_name, room_type


# 获取家具角色
def get_furniture_role_by_category(category_id):
    category_name, group_name, group_role = '', '', ''
    if category_id in furniture_category_dict_id_2:
        category_name = furniture_category_dict_id_2[category_id]
    if category_name in furniture_category_dict_role:
        group_name, group_role = furniture_category_dict_role[category_name]
    return category_name, group_name, group_role


# 获取家具类型
def get_furniture_type_by_category(category_name):
    cate_key = category_name
    type_new = ''
    if cate_key in furniture_category_dict_type_2:
        type_new = furniture_category_dict_type_2[cate_key]
    return type_new


# 获取家具房间
def get_furniture_room_by_object(object_id):
    category_name, room_type = '', ''
    return category_name, room_type


# 获取角色品类
def get_furniture_category_by_key(role_key):
    cate_new, id_new = '', ''
    # 类目
    object_key_1 = role_key
    cate_set_1, cate_id_1 = [], []
    if len(object_key_1) > 0 and object_key_1 in furniture_role_dict_cate_set:
        cate_set_1 = furniture_role_dict_cate_set[object_key_1]
    if len(object_key_1) > 0 and object_key_1 in furniture_role_dict_cate_id:
        cate_id_1 = furniture_role_dict_cate_id[object_key_1]
    if len(cate_set_1) >= 1:
        cate_new = cate_set_1[0]
    if len(cate_id_1) >= 1:
        id_new = cate_id_1[0]
    return cate_new, id_new


# 计算角色品类
def get_furniture_category_by_role(object_group, object_role, object_type, object_rely='', room_type=''):
    group_key = object_group.lower().strip()
    role_key = object_role.lower().strip()
    type_key = (object_type.split('/')[-1]).lower().strip()
    # 房间
    room_key = ''
    if room_type in ['LivingDiningRoom', 'LivingRoom']:
        room_key = 'live'
    elif room_type in ['DiningRoom']:
        room_key = 'cook'
    elif room_type in ['Library']:
        room_key = 'book'
    elif room_type in ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'ElderlyRoom', 'NannyRoom']:
        room_key = 'bed'
    elif room_type in ['KidsRoom']:
        room_key = 'kid'
    elif room_type in ['Kitchen']:
        room_key = 'cook'
    elif room_type in ['MasterBathroom', 'SecondBathroom', 'Bathroom']:
        room_key = 'bath'
    elif room_type in ['Balcony', 'Terrace', 'Lounge', 'LaundryRoom']:
        room_key = 'rest'
    elif room_type in ['Hallway', 'Aisle', 'Corridor', 'Stairwell']:
        room_key = 'door'

    # 检索
    object_key_1, object_key_2 = '', ''
    # 角色
    if group_key in ['wall', 'ceiling', 'floor', 'door', 'window']:
        object_key_1 = group_key + ' ' + type_key
        if group_key in ['ceiling']:
            object_key_1 = group_key + ' ' + type_key + ' ' + room_key
    elif len(role_key) > 0:
        object_key_1 = group_key + ' ' + role_key
    # 房间
    if role_key in ['cabinet']:
        if object_rely in ['cook', 'bath', 'door']:
            object_key_1 = group_key + ' ' + role_key + ' ' + object_rely
        else:
            object_key_1 = group_key + ' ' + role_key + ' ' + room_key
    elif role_key in ['bed'] and room_key in ['kid']:
        object_key_1 = group_key + ' ' + role_key + ' ' + room_key
    elif role_key in ['table', 'chair'] and group_key in ['work'] and room_key in ['kid']:
        object_key_1 = group_key + ' ' + role_key + ' ' + room_key
    # 品类
    if type_key in ['desk lamp']:
        object_key_1 = group_key + ' ' + 'lamp'

    # 详细
    if role_key in ['sofa', 'side sofa', 'bed'] and group_key in ['meeting', 'bed']:
        object_key_2 = object_key_1 + ' ' + type_key

    # 类目
    cate_set_1, cate_set_2, cate_id_1, cate_id_2 = [], [], [], []
    if len(object_key_1) > 0 and object_key_1 in furniture_role_dict_cate_set:
        cate_set_1 = furniture_role_dict_cate_set[object_key_1]
    if len(object_key_2) > 0 and object_key_2 in furniture_role_dict_cate_set:
        cate_set_2 = furniture_role_dict_cate_set[object_key_2]
    # 类目
    if len(object_key_1) > 0 and object_key_1 in furniture_role_dict_cate_id:
        cate_id_1 = furniture_role_dict_cate_id[object_key_1]
    if len(object_key_2) > 0 and object_key_2 in furniture_role_dict_cate_id:
        cate_id_2 = furniture_role_dict_cate_id[object_key_2]

    # 返回
    return cate_set_1, cate_set_2, cate_id_1, cate_id_2


# 获取家具角色
def get_furniture_role_by_item(item_key):
    item_val = {}
    if item_key in FURNITURE_REFER_ITEM:
        item_val = FURNITURE_REFER_ITEM[item_key]
    return item_val


# 获取家具角色
def get_furniture_role_by_jid(object_key):
    object_group_role = []
    if object_key in furniture_role_dict_jid:
        object_group_role = furniture_role_dict_jid[object_key]
    return object_group_role


# 增加家具角色映射
def add_furniture_role_by_jid(object_key, item):
    if type(item) == list and len(item) >= 2:
        furniture_role_dict_jid[object_key] = item
    else:
        return False
    return True


# 家具角色
def del_furniture_role_by_jid(object_key):
    if object_key in furniture_role_dict_jid:
        del furniture_role_dict_jid[object_key]
        return True
    else:
        return False


# 获取家具角色(根据类目)
def get_furniture_role_by_cate_id(object_key):
    object_group_role = []
    if object_key in furniture_category_dict_role_map:
        object_group_role = furniture_category_dict_role_map[object_key]
    return object_group_role


# 获取家具尺寸
def get_furniture_size_by_jid(object_key):
    object_fixed_size = []
    if object_key in furniture_size_dict_jid:
        object_fixed_size = furniture_size_dict_jid[object_key]
    return object_fixed_size


# 获取家具区域
def get_furniture_zone_by_jid(object_key):
    object_fixed_zone = []
    if object_key in furniture_zone_dict_jid:
        object_fixed_zone = furniture_zone_dict_jid[object_key]
    return object_fixed_zone


# 数据加载
load_furniture_refer()


# 功能测试
if __name__ == '__main__':
    load_furniture_refer(reload=True)
    save_furniture_refer()
    pass
