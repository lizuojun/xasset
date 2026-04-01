# -*- coding: utf-8 -*-

"""
@Author:
@Date:
@Description:

"""
import datetime
import os
import copy
import json

# from Demo.config import run_time, thread_pool_task_waiting

from Furniture.furniture import get_furniture_data_more
from HouseSearch.seed.service import thread_pool_task_waiting

room_type_ch_dict = {
    "LivingRoom": {
        "d2a64592-caa7-4ab1-877e-561323315774": "三人沙发",
        "a5af8349-bd50-46aa-b97a-2940125aafae": "双人沙发",
        "cb8152d7-710f-4b4d-9ced-9a979899fc62": "沙发贵妃椅",
        "81780f40-fa53-41c3-8579-65706f4ad50d": "多人沙发",
        "ce3a5686-8c2e-49c4-931a-041b0fb883b8": "组合沙发",
        "c2dcb449-4729-4cfe-9e38-1fc1453211a5": "单人沙发",
        "ad3a29e8-8c78-449c-83be-751954a0837a": "U型沙发",
        "58b818d4-2750-4ed9-bcde-59fb7c351769": "L型沙发",
        "182f769f-981f-4a8e-9aef-7efe9917cf19": "懒人沙发",
        "dddf7d67-6277-4fd6-8fc1-7738295f9824": "脚凳/沙发凳",
        "a1804c08-fbdc-4696-9c38-3d3b143c1b02": "电视柜",
        "9eaee326-16c4-4244-87d5-38e7b57a4e38": "茶几",
        "ce4d79f2-546b-46c3-97b5-7c69c2137780": "边柜",
        "5ad47fd2-b143-4af2-9961-e88a57b4a337": "角几/边几"
    },
    "DiningRoom": {
        "2e336e49-2a54-46cb-bcee-67d2e5361e61": "餐边柜",
        "9e33036f-777c-4ef2-b7ea-e4189f1bf107": "酒柜",
        "9161c9e8-49e8-48bd-9ee8-0c75dd267413": "餐桌",
        "30c7fefc-a32e-48e1-9458-dfab61595dc7": "餐椅"
    },
    "MasterBedroom": {
        "24670bf9-9c9f-41ae-b190-f5f65eab4ddb": "单人床",
        "89404b8a-5bb6-42cf-95fa-73c9bfba4c97": "床头柜",
        "bb8b2c7e-cc9e-4e4e-a208-d76cb1dd6e11": "豪华大床",
        "1a620859-3fda-444c-965f-e3d6893611a8": "床凳",
        "41ac92b5-5f88-46d0-a59a-e1ed31739154": "双人床"
    },
    "Library": {
        "5c76d84c-aa8c-4bb8-88fc-cbf8da81be71": "书桌/书台",
        "3ed785b5-df30-4db8-b49f-4c06c125ec59": "洽谈桌椅",
        "9a44fdee-fd49-4756-a2d7-86d8b8f575c1": "办公桌椅",
        "0b71b677-e56e-4f5e-8e71-e675ea9a786b": "书柜",
        "f46d6117-fbfc-4580-b238-7b27d9d7d832": "书架"
    },
    "Kidsroom": {
        "e5118969-c2ae-494a-b63c-a80b0a6c163d": "婴儿床",
        "4909c460-b0f0-4cd1-af59-4898c310f3f5": "高低床",
        "8f58f84c-1424-4aaf-aef5-62ae1da722ab": "儿童床",
        "9e3580ed-915c-4851-8564-cd869c402983": "儿童桌椅",
        "76ed61b1-acb6-4ca3-80b1-5a4d467f7ecd": "儿童架"}
}

room_type_en_dict = {
    "LivingRoom": {
        "d2a64592-caa7-4ab1-877e-561323315774": "Meeting/sofa",
        "a5af8349-bd50-46aa-b97a-2940125aafae": "Meeting/side sofa",
        "cb8152d7-710f-4b4d-9ced-9a979899fc62": "Meeting/side sofa",
        "81780f40-fa53-41c3-8579-65706f4ad50d": "Meeting/sofa",
        "ce3a5686-8c2e-49c4-931a-041b0fb883b8": "Meeting/sofa",
        "c2dcb449-4729-4cfe-9e38-1fc1453211a5": "Meeting/side sofa",
        "126722b5-f356-467f-8c8c-814bb0a20f05": "Meeting/side sofa",
        "ad3a29e8-8c78-449c-83be-751954a0837a": "Meeting/sofa",
        "58b818d4-2750-4ed9-bcde-59fb7c351769": "Meeting/sofa",
        "182f769f-981f-4a8e-9aef-7efe9917cf19": "Meeting/side sofa",
        "dddf7d67-6277-4fd6-8fc1-7738295f9824": "Meeting/side sofa",
        "a1804c08-fbdc-4696-9c38-3d3b143c1b02": "Media/table",
        "9eaee326-16c4-4244-87d5-38e7b57a4e38": "Meeting/table",
        "ce4d79f2-546b-46c3-97b5-7c69c2137780": "Cabinet/cabinet",
        "9e33036f-777c-4ef2-b7ea-e4189f1bf107": "Cabinet/cabinet",
        "5ad47fd2-b143-4af2-9961-e88a57b4a337": "Meeting/side table"
    },
    "DiningRoom": {
        "2e336e49-2a54-46cb-bcee-67d2e5361e61": "Cabinet/cabinet",
        "9e33036f-777c-4ef2-b7ea-e4189f1bf107": "Cabinet/cabinet",
        "9161c9e8-49e8-48bd-9ee8-0c75dd267413": "Dining/table",
        "30c7fefc-a32e-48e1-9458-dfab61595dc7": "Dining/chair"
    },
    "LivingDiningRoom":
        {
            "2e336e49-2a54-46cb-bcee-67d2e5361e61": "Cabinet/cabinet",
            "9e33036f-777c-4ef2-b7ea-e4189f1bf107": "Cabinet/cabinet",
            "9161c9e8-49e8-48bd-9ee8-0c75dd267413": "Dining/table",
            "30c7fefc-a32e-48e1-9458-dfab61595dc7": "Dining/chair",
            "d2a64592-caa7-4ab1-877e-561323315774": "Meeting/sofa",
            "a5af8349-bd50-46aa-b97a-2940125aafae": "Meeting/side sofa",
            "cb8152d7-710f-4b4d-9ced-9a979899fc62": "Meeting/side sofa",
            "126722b5-f356-467f-8c8c-814bb0a20f05": "Meeting/side sofa",
            "81780f40-fa53-41c3-8579-65706f4ad50d": "Meeting/sofa",
            "ce3a5686-8c2e-49c4-931a-041b0fb883b8": "Meeting/sofa",
            "c2dcb449-4729-4cfe-9e38-1fc1453211a5": "Meeting/side sofa",
            "ad3a29e8-8c78-449c-83be-751954a0837a": "Meeting/sofa",
            "58b818d4-2750-4ed9-bcde-59fb7c351769": "Meeting/sofa",
            "182f769f-981f-4a8e-9aef-7efe9917cf19": "Meeting/side sofa",
            "dddf7d67-6277-4fd6-8fc1-7738295f9824": "Meeting/side sofa",
            "a1804c08-fbdc-4696-9c38-3d3b143c1b02": "Media/table",
            "9eaee326-16c4-4244-87d5-38e7b57a4e38": "Meeting/table",
            "ce4d79f2-546b-46c3-97b5-7c69c2137780": "Cabinet/cabinet",
            "5ad47fd2-b143-4af2-9961-e88a57b4a337": "Meeting/side table"
        },
    "MasterBedroom": {
        "24670bf9-9c9f-41ae-b190-f5f65eab4ddb": "Bed/bed",
        "89404b8a-5bb6-42cf-95fa-73c9bfba4c97": "Bed/side table",
        "bb8b2c7e-cc9e-4e4e-a208-d76cb1dd6e11": "Bed/bed",
        "1a620859-3fda-444c-965f-e3d6893611a8": "Bed/side table",
        "41ac92b5-5f88-46d0-a59a-e1ed31739154": "Bed/bed"
    },
    "Library": {
        "5c76d84c-aa8c-4bb8-88fc-cbf8da81be71": "Work/table",
        "3ed785b5-df30-4db8-b49f-4c06c125ec59": "Work/chair",
        "9a44fdee-fd49-4756-a2d7-86d8b8f575c1": "Work/chair",
        "0b71b677-e56e-4f5e-8e71-e675ea9a786b": "Cabinet/cabinet",
        "f46d6117-fbfc-4580-b238-7b27d9d7d832": "Cabinet/cabinet"
    },
    "Kidsroom": {
        "e5118969-c2ae-494a-b63c-a80b0a6c163d": "Bed/bed",
        "4909c460-b0f0-4cd1-af59-4898c310f3f5": "Bed/bed",
        "8f58f84c-1424-4aaf-aef5-62ae1da722ab": "Bed/bed",
        "9e3580ed-915c-4851-8564-cd869c402983": "Work/table",
        "76ed61b1-acb6-4ca3-80b1-5a4d467f7ecd": "Cabinet/cabinet"}
}

hard_info_ch = {
    "floor": {
        "5c10c875-c168-425a-9ee0-e53c03adddc6": "大理石铺砖",
        "d7981192-acaf-4097-ba62-53af7e58daa7": "地砖",
        "8cdfd5a3-58e8-4ddc-8368-00da8be442c0": "瓷砖",

        "c2f39dcd-db2e-413c-aff2-b45b2f546fb2": "竹地板",
        "ad0a33f3-ccd9-471f-9b5d-b4603183b2ba": "实木地板",
        "afe92ff7-0055-44d1-a94e-a18a67c808c4": "软木地板",
        "9f362ebe-639b-4fc3-9d60-9df6b750e649": "其它地板",
        "c2c10779-adbc-4ab4-aace-a3378e430e2c": "防腐木地板",
        "d5033161-825a-48c3-b6ed-0f6d48feb48a": "实木复合地板",
        "6b2d08a7-83b3-4bf8-b90d-b461c6b6498d": "强化复合地板"
    },
    "wall": {
        "1704ab2a-0d96-4300-87f7-e00c61dd3d41": "墙漆",
        "7b53d24e-7991-449f-844c-0a1b9e84e53d": "墙砖",
        "cefcb22d-8af0-4e93-ab5d-c1149c18b7bc": "艺术涂料",

    },
    "back_wall": {
        "fda8e92c-9959-4eef-8b71-c1bce298b55b": "通用背景墙",
        "5f06ba07-6dfc-4742-a161-f01eb9bab42c": "木质背景墙",
        "1d25742d-252c-4a66-ba36-11f51f4bc685": "石膏板背景墙",
        "796daa6a-9eba-4173-8551-4a076db87370": "大理石背景墙",
        "677c8f6a-d684-4e1b-91d9-4cb756bc59fe": "自定义背景墙",
        "e25de33e-5406-4971-8c6d-961c9f0c5fe4": "参数化护墙板",
        "bf75580f-d801-42e8-8f3f-4c43aa762628": "背景墙/墙面固定家具"}
}

material_info = {'floor': [{'jid': "0f3ae039-a064-4243-9bb8-ce49bb5c744f",
                            "color": [255, 255, 255], 'size': [0.8, 0.8], 'colorMode': 'texture',
                            'seam': False,
                            'material_id': 100,
                            'texture_url':
                                'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/0f3ae039-a064-4243-9bb8-ce49bb5c744f/wallfloor_mini.png',
                            }], 'wall': [
    {'jid': "0a0365fa-4fc6-4279-b109-ca7cb3d08342",
     "color": [255, 255, 255], 'size': [2.2, 2.2], 'colorMode': 'texture',
     'seam': False,
     'material_id': 101,
     'texture_url':
         'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/0a0365fa-4fc6-4279-b109-ca7cb3d08342/wallfloor_mini.png',
     }
]}


def get_furniture_role(base_type, base_size, room_type="LivingDiningRoom"):
    # 餐桌 - 餐椅(1)、沙发 - 边沙发(2)、沙发 - 边桌(3)、边沙发 - 茶几(4)、茶几 - 电视柜(5)、床 - 床头柜(6)、床add(7)、客add(8)
    if 'DiningRoom' in room_type:
        if 'dining table' in base_type and 70 < base_size[1] < 85 and max(base_size[0], base_size[2]) > 90:
            return 'Dining/table'
        if 'table/table' in base_type and 70 < base_size[1] < 85 and max(base_size[0], base_size[2]) > 90:
            return 'Dining/table'
        if 'chair' in base_type and max(base_size) < 80:
            return 'Dining/chair'
    if 'Living' in room_type:
        if (
                'type L' in base_type or 'multi' in base_type or 'three' in base_type or 'corner' in base_type or 'double' in base_type) \
                and base_size[0] > 130:
            return 'Meeting/sofa'
        if 'sofa' in base_type and base_size[0] < 130:
            return 'Meeting/side sofa'
        if 'chair' in base_type and max(base_size[0], base_size[2]) > 80:
            return 'Meeting/side sofa'
        if 'coffee' in base_type or ('table' in base_type and base_size[1] < 60 and base_size[0] > 80):
            return 'Meeting/table'
        if 'side table' in base_type or ('table' in base_type and base_size[0] < 130 and base_size[1] < 60):
            return 'Meeting/side table'
        if 'media' in base_type:
            return 'Media/table'
    if 'bed' in base_type:
        return 'Bed/bed'
    if 'night' in base_type:
        return 'Bed/side table'
    if 'sofa' in base_type:
        return 'Rest/chair'
    if 'lamp' in base_type:
        return 'Rest/table'
    if 'cabinet' in base_type and base_size[1] <= 130:
        return 'Cabinet/cabinet'
    if 'storage' in base_type and base_size[1] <= 130:
        return 'Cabinet/cabinet'
    if 'shelf' in base_type and base_size[1] <= 130:
        return 'Cabinet/cabinet'
    if 'armoire' in base_type:
        return 'Armoire/armoire'
    if 'cabinet' in base_type and base_size[1] > 130:
        return 'Cabinet/cabinet'
    if 'storage' in base_type and base_size[1] > 130:
        return 'Cabinet/cabinet'
    if 'shelf' in base_type and base_size[1] > 130:
        return 'Cabinet/cabinet'
    if 'dining table' in base_type and 70 < base_size[1] < 90:
        return 'Dining/table'
    if 'table/table' in base_type and 70 < base_size[1] < 90:
        return 'Dining/table'

    if 'rug' in base_type:
        if room_type in ["LivingDiningRoom", "DiningRoom", "LivingRoom"]:
            return 'Meeting/rug'
        else:
            return 'Bed/rug'

    return 'Accessory/accessory'


def get_furniture_role_detail(category_id, base_type, base_size, room_type='LivingDiningRoom'):
    if room_type in room_type_en_dict:
        all_need_cate = room_type_en_dict[room_type]
        if category_id in all_need_cate:
            return all_need_cate[category_id]
    return get_furniture_role(base_type, base_size, room_type)


def get_jid_color(jid):
    color = [255, 255, 255]
    size = [1.0, 1.0]
    return color, size

    data_info = get_model_info_daily([jid])
    if jid in data_info and 'color' in data_info[jid]:
        color_list = json.loads(data_info[jid]['color'])
        color = color_list[0]['color']
    if jid in data_info and 'properties' in data_info[jid]:
        if 'length' in data_info[jid]['properties'] and 'width' in data_info[jid]['properties']:
            h = float(data_info[jid]['properties']['length']) / 100.

            w = float(data_info[jid]['properties']['width']) / 100.
            size = [w, h]
    return color, size


def get_mat_info(jid, mat_id):
    color, size = get_jid_color(jid)
    return {'jid': jid,
            'texture_url':
                'https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/%s/wallfloor_mini.png' % jid,
            'color': color,
            'colorMode': 'texture',
            'size': size,
            'seam': False,
            'material_id': mat_id}


def check_all_chair_table_roles(furniture_role_list):
    dining_chair_list = []
    dining_table_list = []
    side_sofa_list = []
    sofa_list = []

    bed_list = []
    for obj in furniture_role_list:
        if obj['role'] == 'Dining/chair':
            dining_chair_list.append(obj)
        elif obj['role'] == 'Dining/table':
            dining_table_list.append(obj)
        elif obj['role'] == 'Meeting/side sofa':
            side_sofa_list.append(obj)
        elif obj['role'] == 'Meeting/sofa':
            sofa_list.append(obj)
        elif obj['role'] == 'Bed/bed':
            bed_list.append(obj)

    for obj in bed_list:
        if obj['size'][0] > 220:
            obj['scale'][0] = 0.85

    # 检查长凳作为椅子
    if len(dining_table_list) > 1:
        for table_obj in dining_table_list:
            if table_obj['size'][1] < 50 and min(table_obj['size'][2], table_obj['size'][0]) < 40 and max(
                    table_obj['size'][2], table_obj['size'][0]) > 90:
                table_obj['role'] = 'Dining/chair'
                # dining_chair_list.append(table_obj)

    # 没有边沙发, 挑选最大的餐椅作为边沙发
    if len(dining_chair_list) > 1 and len(side_sofa_list) == 0:
        area_list = []
        for chair_obj in dining_chair_list:
            size = chair_obj['size'][0] * chair_obj['size'][1] * chair_obj['size'][2]
            area_list.append((size, chair_obj))
        obj = sorted(area_list, reverse=True, key=lambda x: x[0])[0][1]
        obj['role'] = 'Meeting/side sofa'

    # 没有沙发, 挑选最大的边沙发作为沙发
    if len(side_sofa_list) > 0 and len(sofa_list) == 0:
        area_list = []
        for target_obj in side_sofa_list:
            size = target_obj['size'][0] * target_obj['size'][1] * target_obj['size'][2]
            area_list.append((size, target_obj))
        obj = sorted(area_list, reverse=True, key=lambda x: x[0])[0][1]
        obj['role'] = 'Meeting/sofa'

    print("change")


def check_furniture_role_info(furniture_role_list, object_id, room_type):
    object_type, object_style, object_size, obj_type_id, obj_style_id, obj_category_id = get_furniture_data_more(
        object_id)

    object_one = {
        'id': object_id,
        'type': object_type,
        'style': object_style,
        'category_id': obj_category_id,
        'style_id': obj_style_id,
        'size': object_size,
        'scale': [1, 1, 1],
        'position': [0, 0, 0],
        'rotation': [0, 0, 0, 1],
        'entityId': '',
        'role': get_furniture_role_detail(obj_category_id, object_type, object_size, room_type)
    }
    furniture_role_list.append(object_one)


def get_furniture_roles_info(furniture_list, room_type):
    furniture_role_list = []

    note_dict = {}

    # 并行检查所有家具
    task_var_list = []
    for object_id in furniture_list:
        # 输入参数 (list, None)
        task_var_list.append(((furniture_role_list, object_id, room_type), None))

    thread_pool_task_waiting(check_furniture_role_info, task_var_list)

    # # 检查硬装
    # mat_id = 100
    # for object_info in furniture_role_list:
    #     object_id = object_info['id']
    #     obj_category_id = object_info['category_id']
    #     if obj_category_id in hard_info_ch['floor'] and not material_role_list['floor']:
    #         material_role_list['floor'].append(get_mat_info(object_id, mat_id))
    #         mat_id += 1
    #
    #     if obj_category_id in hard_info_ch['wall'] and not material_role_list['wall']:
    #         material_role_list['wall'].append(get_mat_info(object_id, mat_id))
    #         mat_id += 1

    # 检查餐桌、餐椅、边沙发是否可以互换的情况
    # check_all_chair_table_roles(furniture_role_list)

    for i in furniture_role_list:
        group, role = i['role'].split('/')
        if role in ["accessory"]:
            continue
        note_dict[i['id']] = i
        note_dict[i['id']]['group'] = group
        note_dict[i['id']]['role'] = role
        if room_type in ["LivingDiningRoom", "LivingRoom"]:
            if group == "Meeting" and role == "sofa":
                note_dict[i['id']]['main'] = True
        elif room_type in ["Bedroom", "MasterBedroom", "SecondBedroom"]:
            if group == "Bed" and role == "bed":
                note_dict[i['id']]['main'] = True

    return note_dict
