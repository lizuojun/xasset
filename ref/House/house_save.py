# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2019-06-16
@Description: 全屋布局测试

"""

import datetime
from House.house_draw import *

# 临时目录
DATA_DIR_HOUSE = os.path.dirname(__file__) + '/temp/'
DATA_DIR_HOUSE_SCHEME = os.path.dirname(__file__) + '/temp/scheme/'
DATA_DIR_HOUSE_GROUP = os.path.dirname(__file__) + '/temp/group/'
if not os.path.exists(DATA_DIR_HOUSE):
    os.makedirs(DATA_DIR_HOUSE)
if not os.path.exists(DATA_DIR_HOUSE_SCHEME):
    os.makedirs(DATA_DIR_HOUSE_SCHEME)
if not os.path.exists(DATA_DIR_HOUSE_GROUP):
    os.makedirs(DATA_DIR_HOUSE_GROUP)
# OSS位置
DATA_OSS_GROUP = 'ihome-alg-layout'
DATA_OSS_GROUP_HS = 'tp-publish-robin-assembly-json'
# RAM信息
ACCESS_ID_GROUP = ''
ACCESS_SECRET_GROUP = ''
ACCESS_ENDPOINT_GROUP = 'http://oss-cn-zhangjiakou.aliyuncs.com'

SAVE_MODE_SCENE = 0
SAVE_MODE_IMAGE = 1
SAVE_MODE_FRAME = 2
SAVE_MODE_RENDER = 3
SAVE_MODE_WANDER = 4

SAVE_MODE_DATA = 10
SAVE_MODE_GROUP = 11
SAVE_MODE_LAYOUT = 12
SAVE_MODE_PROPOSE = 13
SAVE_MODE_SAMPLE = 14

SAVE_GROUP_EXAMPLE = {
    'meta': {
        'version': '0.1',
        'origin': 'Floorplan web editor',
        'magic': '171bd2f43d70',
        'unit': 'cm'
    },
    'boundingBox': {
        'xLen': 150.8,
        'yLen': 160.33,
        'zLen': 196.83
    },
    'Products': []
}


# 保存布局
def house_save(house_id, house_path, layout_num, propose_num, house_data_info, house_layout_info, house_propose_info,
               save_id='', save_dir=DATA_DIR_HOUSE_SCHEME, save_mode=[SAVE_MODE_IMAGE],
               suffix_flag=False, sample_flag=True, upload_flag=False):
    # 保存参数
    if save_id == '':
        save_id = house_id
    # 绘制参数
    group_to_draw = ['Meeting', 'Bed', 'Media', 'Dining', 'Work', 'Rest', 'Armoire', 'Cabinet', 'Appliance',
                     'Bath', 'Toilet',
                     'Wall', 'Ceiling', 'Floor', 'Door', 'Window', 'Background']
    # 保存场景
    if SAVE_MODE_SCENE in save_mode:
        pass
    # 保存图像
    if SAVE_MODE_IMAGE in save_mode or SAVE_MODE_FRAME in save_mode:
        # 模板方案
        if layout_num <= 0 and sample_flag:
            layout_idx = 0
            image_path = os.path.join(save_dir, save_id + '.png')
            draw_house_layout_index(house_data_info, house_layout_info, {}, image_path, layout_idx, -1,
                                    [], group_to_draw, True, True, True, draw_detail=2)
        # 推荐方案
        for layout_idx in range(layout_num):
            if len(house_layout_info) <= 0:
                break
            # 模板方案
            if sample_flag:
                image_path = os.path.join(save_dir, save_id + '_image_%02d_00.png' % layout_idx)
                draw_house_layout_index(house_data_info, house_layout_info, {}, image_path, layout_idx, -1,
                                        [], group_to_draw, True, True, True, draw_detail=2)
            # 选品方案
            if propose_num <= 0:
                continue
            for propose_idx in range(propose_num):
                image_path = os.path.join(save_dir, save_id + '_image_%02d_%02d.png' % (layout_idx, propose_idx + 1))
                draw_house_layout_index(house_data_info, house_layout_info, {}, image_path, layout_idx, propose_idx,
                                        [], group_to_draw, True, True, True, draw_detail=2)
    # 保存户型
    if SAVE_MODE_DATA in save_mode:
        json_path = os.path.join(save_dir, save_id + '_data.json')
        json_data = house_data_info
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
            f.close()
    # 保存方案
    if SAVE_MODE_LAYOUT in save_mode:
        json_path = os.path.join(save_dir, save_id + '_layout.json')
        json_data = house_layout_info
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
            f.close()
    # 保存选品
    if SAVE_MODE_PROPOSE in save_mode:
        json_path = os.path.join(save_dir, save_id + '_propose.json')
        json_data = house_propose_info
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
            f.close()


# 保存布局
def house_save_region(house_id, house_path, layout_num, propose_num, house_data_info, house_layout_info,
                      house_propose_info, house_region_info,
                      save_id='', save_dir=DATA_DIR_HOUSE_SCHEME, save_mode=[SAVE_MODE_IMAGE],
                      suffix_flag=False, sample_flag=True, upload_flag=False):
    # 保存参数
    if save_id == '':
        save_id = house_id
    # 绘制参数
    group_to_draw = ['Meeting', 'Bed', 'Media', 'Dining', 'Work', 'Rest', 'Armoire', 'Cabinet', 'Appliance',
                     'Bath', 'Toilet',
                     'Wall', 'Ceiling', 'Floor', 'Door', 'Window', 'Background']
    # 保存场景
    if SAVE_MODE_SCENE in save_mode:
        pass
    # 保存图像
    if SAVE_MODE_IMAGE in save_mode or SAVE_MODE_FRAME in save_mode:
        # 模板方案
        if layout_num <= 0 and sample_flag:
            layout_idx = 0
            image_path = os.path.join(save_dir, save_id + '.png')
            draw_house_layout_index(house_data_info, house_layout_info, {}, image_path, layout_idx, -1,
                                    [], group_to_draw, True, True, True, draw_detail=2)
        # 推荐方案
        for layout_idx in range(layout_num):
            if len(house_layout_info) <= 0:
                break
            # 模板方案
            if sample_flag:
                image_path = os.path.join(save_dir, save_id + '_image_%02d_00.png' % layout_idx)
                draw_house_layout_index(house_data_info, house_layout_info, house_region_info,
                                        image_path, layout_idx, -1, [],
                                        group_to_draw, True, True, True, draw_detail=2)
            # 选品方案
            if propose_num <= 0:
                continue
            for propose_idx in range(propose_num):
                image_path = os.path.join(save_dir, save_id + '_image_%02d_%02d.png' % (layout_idx, propose_idx + 1))
                draw_house_layout_index(house_data_info, house_layout_info, house_region_info,
                                        image_path, layout_idx, propose_idx, [],
                                        group_to_draw, True, True, True, draw_detail=2)
    # 保存户型
    if SAVE_MODE_DATA in save_mode:
        json_path = os.path.join(save_dir, save_id + '_data.json')
        json_data = house_data_info
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
            f.close()
    # 保存方案
    if SAVE_MODE_LAYOUT in save_mode:
        json_path = os.path.join(save_dir, save_id + '_layout.json')
        json_data = house_layout_info
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
            f.close()
    # 保存选品
    if SAVE_MODE_PROPOSE in save_mode:
        json_path = os.path.join(save_dir, save_id + '_propose.json')
        json_data = house_propose_info
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
            f.close()


# 保存组合
def group_save(house_group_info, save_id='', save_dir=DATA_DIR_HOUSE_GROUP,
               save_code=10, save_num=50, save_mode=[SAVE_MODE_GROUP], upload_group=False, upload_room=True):
    for room_id, room_group in house_group_info.items():
        # 组合提取
        group_list_functional, group_list_decorative = room_group['group_functional'], room_group['group_decorative']
        # 房间信息
        room_type, room_style, room_area, room_code = '', '', 0, ''
        if 'room_type' in room_group:
            room_type = room_group['room_type']
        if 'room_style' in room_group:
            room_style = room_group['room_style']
        if 'room_area' in room_group:
            room_area = room_group['room_area']
        if 'room_code' in room_group:
            room_code = room_group['room_code']
        if room_type == '':
            room_type = 'none'
        # 房间风格
        style_dict, style_best = {}, ''
        for group_one in group_list_functional:
            if group_one['type'] in ['Meeting', 'Dining', 'Bed', 'Armoire', 'Work', 'Rest']:
                group_style = group_one['style']
                if group_style in style_dict:
                    style_dict[group_style] += 1
                else:
                    style_dict[group_style] = 1
                if style_best not in style_dict:
                    style_best = group_style
                elif style_dict[style_best] < style_dict[group_style]:
                    style_best = group_style
        room_style = style_best
        if room_style == '':
            room_style = 'Other'
        else:
            room_style = room_style.split('/')[0]
        # 组合
        for group_one in group_list_functional:
            if group_one['type'] in ['Bath', 'Toilet']:
                continue
            group_add = group_trans_compose(group_one, group_list_decorative, save_code, save_num)
            if 'Products' not in group_add:
                continue
            if len(group_add['Products']) <= 0:
                continue
            # 文件
            group_type, group_size = group_one['type'], group_one['size']
            group_style = ''
            if 'style' in group_one:
                group_style = group_one['style']
                # Changed by WenYin
                group_style = group_style.replace("/", "-")
                if group_style == "":
                    group_style = "blank"
            group_file = 'Group_%s_%s_%s_%s_%.2f_%.2f.json' % (save_id, room_id, group_type, group_style,
                                                               group_size[0], group_size[2])
            group_date = datetime.date.today()
            # 保存
            json_file = group_file
            json_path = os.path.join(save_dir, json_file)
            json_data = group_add
            with open(json_path, "w") as f:
                json.dump(json_data, f, indent=4)
                f.close()
            # 上传 数字家
            group_dir = save_id
            if len(group_dir) <= 0:
                group_dir = 'house'
            json_file = 'sample_group/' + group_dir + '/' + group_file
            if os.path.exists(json_path):
                oss_upload_file(json_file, json_path, DATA_OSS_GROUP)
                pass
            # 上传 设计家
            json_file = group_date.strftime('%Y.%m.%d') + '/' + group_file
            if os.path.exists(json_path) and upload_group:
                oss_upload_file(json_file, json_path, DATA_OSS_GROUP_HS,
                                ACCESS_ID_GROUP, ACCESS_SECRET_GROUP, ACCESS_ENDPOINT_GROUP)
        # 单屋
        room_file = 'Room_%s_%s_%03d_%s_%s.json' % (room_style, room_type, int(room_area), save_id, room_id)
        room_info = []
        for group_one in group_list_functional:
            if 'obj_list' not in group_one:
                continue
            if len(group_one['obj_list']) <= 0:
                continue
            room_info.append(group_one)
        for group_one in group_list_decorative:
            if 'obj_list' not in group_one:
                continue
            if len(group_one['obj_list']) <= 0:
                continue
            room_info.append(group_one)
        if len(room_info) <= 0:
            continue
        # 保存
        json_file = room_file
        json_path = os.path.join(save_dir, json_file)
        json_data = room_info
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
            f.close()
        # 上传
        group_dir = save_id
        if len(group_dir) <= 0:
            group_dir = 'room'
        # 删除
        if os.path.exists(json_path):
            os.remove(json_path)


# 保存组合
def group_save_list(group_list, save_id='', save_dir=DATA_DIR_HOUSE_GROUP, position_mode=''):
    for group_idx, group_one in enumerate(group_list):
        group_add = group_trans_compose(group_one, [], 10, 50, position_mode)
        if 'Products' not in group_add:
            continue
        if len(group_add['Products']) <= 0:
            continue
        # 文件
        group_type = ''
        if 'type' in group_one:
            group_type = group_one['type']
        group_file = 'Group_%s_%s_%d.json' % (group_type, save_id, group_idx)
        # 保存
        json_file = group_file
        json_path = os.path.join(save_dir, json_file)
        json_data = group_add
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
            f.close()


# 保存组合
def group_save_plan(house_layout_info, save_id='', save_dir=DATA_DIR_HOUSE_GROUP,
                    save_code=10, save_num=50, save_mode=[SAVE_MODE_GROUP], save_type=[]):
    for room_id, room_layout in house_layout_info.items():
        if 'layout_scheme' not in room_layout:
            continue
        scheme_list = room_layout['layout_scheme']
        for scheme_idx, scheme_one in enumerate(scheme_list):
            if 'group' not in scheme_one:
                continue
            group_list = scheme_one['group']
            group_func, group_deco = [], []
            for group_idx, group_one in enumerate(group_list):
                group_type = group_one['type']
                if group_type in GROUP_RULE_FUNCTIONAL:
                    if group_type in save_type or len(save_type) <= 0:
                        group_func.append(group_one)
                elif group_type in ['Wall', 'Floor']:
                    group_deco.append(group_one)
            for group_idx, group_one in enumerate(group_func):
                group_add = group_trans_compose(group_one, group_deco, save_code, save_num)
                if 'Products' not in group_add:
                    continue
                if len(group_add['Products']) <= 0:
                    continue
                # 文件
                group_type, group_size = group_one['type'], group_one['size']
                group_file = 'Group_%s_%s_%s_%d_%d.json' % (save_id, room_id, group_type, scheme_idx, group_idx)
                # 保存
                json_file = group_file
                json_path = os.path.join(save_dir, json_file)
                json_data = group_add
                with open(json_path, "w") as f:
                    json.dump(json_data, f, indent=4)
                    f.close()


# 分组转换
def group_trans_compose(group_one, group_list_deco=[], save_code=10, save_num=50, position_mode=''):
    # 新建
    group_add = SAVE_GROUP_EXAMPLE.copy()
    group_unit = 'cm'
    ratio_unit = 100
    if 'unit' in group_add:
        group_unit = group_add['unit']
    if group_unit == 'cm':
        ratio_unit = 100
    elif group_unit == 'm':
        ratio_unit = 1
    # 数量
    if 'obj_list' not in group_one:
        return group_add
    if len(group_one['obj_list']) < 0:
        return group_add
    # 编码
    group_code = 100
    if 'code' in group_one:
        group_code = group_one['code']
    if group_code < save_code:
        return group_add
    # 尺寸
    group_size = group_one['size']
    group_add['boundingBox']['xLen'] = group_size[0] * ratio_unit
    group_add['boundingBox']['yLen'] = group_size[2] * ratio_unit
    group_add['boundingBox']['zLen'] = group_size[1] * ratio_unit
    # 分类
    object_main = group_one['obj_list'][0]
    object_list_1, object_list_2, object_list_3, object_list_4, object_list_5 = [], [], [], [], []
    # 家具
    for object_one in group_one['obj_list']:
        if object_one['role'] in [object_main['role'], 'table']:
            object_list_1.append(object_one)
        elif object_one['role'] not in ['accessory', '']:
            object_list_2.append(object_one)
        else:
            object_list_3.append(object_one)
    # 装饰
    for group_new in group_list_deco:
        if group_new['type'] not in ['Wall', 'Floor']:
            continue
        for object_one in group_new['obj_list']:
            if 'relate_group' in object_one and object_one['relate_group'] == group_one['type']:
                if group_one['type'] == 'Dining':
                    continue
                if 'relate' in object_one and object_one['relate'] == group_one['obj_main']:
                    if group_new['type'] == 'Wall':
                        object_list_4.append(object_one)
                    else:
                        object_list_5.append(object_one)
    # 排序
    object_list = []
    for object_list_one in [object_list_1, object_list_2, object_list_3, object_list_4, object_list_5]:
        object_list_old = []
        for object_new in object_list_one:
            # 新增
            object_pos_new = [0, 0, 0]
            if 'normal_position' in object_new:
                object_pos_new = object_new['normal_position']
            # 位置模式
            if position_mode == 'origin':
                object_pos_new = object_new['position']
            object_dis_new = abs(object_pos_new[0]) + abs(object_pos_new[1]) + abs(object_pos_new[2])
            if 'role' in object_new and object_new['role'] in ['accessory', '']:
                object_dis_new = -object_pos_new[0] - object_pos_new[1] * 10 - object_pos_new[2]
            # 已有
            object_idx_new = -1
            for object_idx, object_old in enumerate(object_list_old):
                object_pos_old = [0, 0, 0]
                if 'normal_position' in object_old:
                    object_pos_old = object_old['normal_position']
                # 位置模式
                if position_mode == 'origin':
                    object_pos_old = object_new['position']
                object_dis_old = abs(object_pos_old[0]) + abs(object_pos_old[1]) + abs(object_pos_old[2])
                if 'role' in object_old and object_old['role'] in ['accessory', '']:
                    object_dis_old = -object_pos_old[0] - object_pos_old[1] * 10 - object_pos_old[2]
                if object_dis_new < object_dis_old:
                    object_idx_new = object_idx
                    object_list_old.insert(object_idx, object_new)
                    break
            if object_idx_new < 0:
                object_list_old.append(object_new)
        for object_old in object_list_old:
            object_list.append(object_old)
    # 丢弃
    if len(object_list) > save_num > 0:
        for object_idx in range(len(object_list) - 1, save_num - 1, -1):
            object_list.pop(object_idx)
    # 遍历
    group_add['Products'] = []
    min_x, min_y, min_z, max_x, max_y, max_z = 100, 100, 100, -100, -100, -100
    for object_one in object_list:
        object_id = object_one['id']
        object_turn = get_furniture_turn(object_id)
        if 'turn' in object_one and abs(object_one['turn']) > 0:
            object_turn = object_one['turn']
        object_size = [object_one['size'][i] * object_one['scale'][i] / 100 for i in range(3)]
        object_scale = object_one['scale']
        if 'normal_position' in object_one and len(object_one['normal_position']) > 0:
            object_pos = object_one['normal_position'][:]
        else:
            object_pos = [0, 0, 0]
        if 'normal_rotation' in object_one and len(object_one['normal_rotation']) > 0:
            object_rot = object_one['normal_rotation']
            object_ang = rot_to_ang(object_rot)
        else:
            object_rot = [0, 0, 0, 1]
            object_ang = 0
        # 位置模式
        if position_mode == 'origin':
            object_pos = object_one['position'][:]
            object_rot = object_one['rotation']
            object_ang = rot_to_ang(object_rot)
        # 尺寸范围
        [x1, z1, x2, z2, x3, z3, x4, z4] = group_bound(object_size, object_pos, object_rot)
        y1, y2 = object_pos[1], object_pos[1] + object_size[1]
        # 尺寸下限
        min_x = min(min_x, x1, x2, x3, x4)
        min_y = min(min_y, y1, y2)
        min_z = min(min_z, z1, z2, z3, z4)
        # 尺寸上限
        max_x = max(max_x, x1, x2, x3, x4)
        max_y = max(max_y, y1, y2)
        max_z = max(max_z, z1, z2, z3, z4)
        # 规范打组
        tmp_x = -object_pos[0]
        tmp_z = object_pos[2]
        group_ang = math.pi
        add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
        add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
        object_pos_new = [add_x, add_z, object_pos[1]]
        object_ang_new = -object_ang + group_ang + math.pi + object_turn * math.pi / 2
        # 添加打组
        origin_size, object_role = object_one['size'][:], ''
        if 'role' in object_one:
            object_role = object_one['role']
        if object_id.endswith('.json'):
            continue
        object_add = {
            'id': object_id,
            'position': {
                'x': object_pos_new[0] * ratio_unit,
                'y': object_pos_new[1] * ratio_unit,
                'z': object_pos_new[2] * ratio_unit
            },
            'rotation': object_ang_new * 180 / math.pi,
            'scale': {'XScale': object_scale[0], 'YScale': object_scale[2], 'ZScale': object_scale[1],},
            'size': [origin_size[0], origin_size[2], origin_size[1]],
            'role': object_role
        }
        group_add['Products'].append(object_add)
    # 校正
    offset_x, offset_z = (max_x + min_x) / 2, (max_z + min_z) / 2
    for object_add in group_add['Products']:
        # 位置模式
        if position_mode == 'origin':
            break
        object_add['position']['x'] += offset_x * ratio_unit
        object_add['position']['y'] += offset_z * ratio_unit
    group_add['boundingBox']['xLen'] = (max_x - min_x) * ratio_unit
    group_add['boundingBox']['yLen'] = (max_z - min_z) * ratio_unit
    group_add['boundingBox']['zLen'] = (max_y - min_y) * ratio_unit
    # 返回
    return group_add


# 分组转换
def group_trans_detail(group_one, room_mirror=0, entity_dict={}):
    group_new, group_type = [], group_one['type']
    for object_one in group_one['obj_list']:
        object_id = object_one['id']
        object_turn = get_furniture_turn(object_id)
        if 'turn' in object_one and abs(object_one['turn']) > 0:
            object_turn = object_one['turn']
        object_size, object_scale = object_one['size'], object_one['scale']
        object_position, object_rotation = object_one['position'], object_one['rotation']
        object_angle = rot_to_ang(object_rotation) + object_turn * math.pi / 2
        # 其他
        object_mat = {}
        object_host = 'floor'
        object_entity = ''
        # 材质
        if 'materials' in object_one:
            object_mat = object_one['materials']
        # 依附
        if 'hostType' in object_one:
            object_host = object_one['hostType']
        else:
            if group_type in ['Wall', 'Ceiling', 'Floor']:
                object_host = group_type.lower()
            elif group_type in ['Door', 'Window', 'Background']:
                object_host = 'wall'
            elif 'role' in object_one and object_one['role'] in ['screen']:
                object_host = 'wall'
            elif 'relate' in object_one and len(object_one['relate']) > 0:
                object_host = 'others'
        # 贴墙
        if 'role' in object_one and object_one['role'] in ['tv']:
            if 'type' in object_one and 'wall' in object_one['type']:
                object_host = 'wall'
                object_one['top_of'] = 0
        # 实例
        if 'entityId' in object_one:
            object_entity = object_one['entityId']
        if object_entity in entity_dict:
            object_entity = ''
        else:
            entity_dict[object_entity] = 1
        # 镜像
        mirror_dlt = 1
        if room_mirror == 1:
            mirror_dlt = -1
        # 调整
        adjust_lift, adjust_pitch = 0, 0
        if 'adjust_lift' in object_one:
            adjust_lift = object_one['adjust_lift']
        object_add = {
            'id': object_one['id'],
            'type': object_one['type'],
            'style': object_one['style'],
            'scale': [object_scale[0], object_scale[2], object_scale[1]],
            'position': [object_position[0], object_position[2] * mirror_dlt, object_position[1] + adjust_lift],
            'rotation': [0, 0, object_angle * 180 / math.pi * mirror_dlt],
            'group': group_type,
            'materials': object_mat,
            'hostType': object_host,
            'entityId': object_entity
        }
        if 'adjust_pitch' in object_one:
            adjust_pitch = object_one['adjust_pitch']
            adjust_angle = rot_to_ang(object_rotation)
            if abs(adjust_angle) < 0.2:
                object_add['rotation'][0] = adjust_pitch * 180 / math.pi
            elif abs(adjust_angle + math.pi) < 0.2 and abs(adjust_angle - math.pi) < 0.1:
                object_add['rotation'][0] = -adjust_pitch * 180 / math.pi
            elif abs(adjust_angle + math.pi / 2) < 0.2:
                object_add['rotation'][1] = -adjust_pitch * 180 / math.pi
            elif abs(adjust_angle - math.pi / 2) < 0.2:
                object_add['rotation'][1] = adjust_pitch * 180 / math.pi
            else:
                object_add['rotation'][0] = 0
                object_add['rotation'][1] = 0
        # 俯仰
        if 'tilt' in object_one:
            object_add['rotation'][0] = object_one['tilt'] * 180 / math.pi
        group_new.append(object_add)
    return group_new


# 分组转换
def group_trans_overlap(group_one, room_mirror=0, skip_id=''):
    group_new, group_old, group_top = [], [], 1000
    group_type = ''
    if 'type' in group_one:
        group_type = group_one['type']
    if 'obj_list' in group_one:
        object_list = group_one['obj_list']
        for object_one in object_list:
            object_id = object_one['id']
            if object_id == skip_id:
                continue
            else:
                object_turn = get_furniture_turn(object_id)
                if 'turn' in object_one and abs(object_one['turn']) > 0:
                    object_turn = object_one['turn']
                object_size, object_scale = object_one['size'], object_one['scale']
                object_position, object_rotation = object_one['position'], object_one['rotation']
                object_angle = rot_to_ang(object_rotation) + object_turn * math.pi / 2
                # 其他
                object_mat = {}
                object_host = 'floor'
                object_entity = ''
                # 材质
                if 'materials' in object_one:
                    object_mat = object_one['materials']
                # 依附
                if 'hostType' in object_one:
                    object_host = object_one['hostType']
                else:
                    if group_type in ['Wall', 'Ceiling', 'Floor']:
                        object_host = group_type.lower()
                    elif group_type in ['Door', 'Window', 'Background']:
                        object_host = 'wall'
                    elif 'role' in object_one and object_one['role'] in ['screen']:
                        object_host = 'wall'
                    elif 'relate' in object_one and len(object_one['relate']) > 0:
                        object_host = 'others'
                # 贴墙
                if 'role' in object_one and object_one['role'] in ['tv']:
                    if 'type' in object_one and 'wall' in object_one['type']:
                        object_host = 'wall'
                        object_one['top_of'] = 0
                # 实例
                if 'entityId' in object_one:
                    object_entity = object_one['entityId']
                # 镜像
                mirror_dlt = 1
                if room_mirror == 1:
                    mirror_dlt = -1
                # 调整
                adjust_lift, adjust_pitch = 0, 0
                if 'adjust_lift' in object_one:
                    adjust_lift = object_one['adjust_lift']
                object_add = {
                    'id': object_one['id'],
                    'type': object_one['type'],
                    'style': object_one['style'],
                    'scale': [object_scale[0], object_scale[2], object_scale[1]],
                    'position': [object_position[0], object_position[2] * mirror_dlt, object_position[1] + adjust_lift],
                    'rotation': [0, 0, object_angle * 180 / math.pi * mirror_dlt],
                    'materials': object_mat,
                    'hostType': object_host,
                    'entityId': object_entity,
                    'top_id': -1,
                    'top_of': 0
                }
                # if 'entityId' not in object_one:
                #     object_add.pop('entityId')
                if 'adjust_pitch' in object_one:
                    adjust_pitch = object_one['adjust_pitch']
                    adjust_angle = rot_to_ang(object_rotation)
                    if abs(adjust_angle) < 0.2:
                        object_add['rotation'][0] = adjust_pitch * 180 / math.pi
                    elif abs(adjust_angle + math.pi) < 0.2 and abs(adjust_angle - math.pi) < 0.1:
                        object_add['rotation'][0] = -adjust_pitch * 180 / math.pi
                    elif abs(adjust_angle + math.pi / 2) < 0.2:
                        object_add['rotation'][1] = -adjust_pitch * 180 / math.pi
                    elif abs(adjust_angle - math.pi / 2) < 0.2:
                        object_add['rotation'][1] = adjust_pitch * 180 / math.pi
                    else:
                        object_add['rotation'][0] = 0
                        object_add['rotation'][1] = 0
                if 'top_id' in object_one:
                    object_add['top_id'] = object_one['top_id']
                if 'top_of' in object_one:
                    object_add['top_of'] = object_one['top_of']
                group_old.append(object_add)
    for object_one in group_old:
        top_of = 0
        if 'top_of' in object_one:
            top_of = object_one['top_of']
        object_sub = False
        for object_old in group_old:
            if object_old == object_one:
                continue
            top_id = 0
            if 'top_id' in object_old:
                top_id = object_old['top_id']
            if top_of == top_id:
                if 'sub_list' not in object_old:
                    object_old['sub_list'] = []
                object_old['sub_list'].append(object_one)
                object_sub = True
                break
        if not object_sub:
            group_new.append(object_one)
    for object_one in group_old:
        # object_one.pop('entityId')
        object_one.pop('top_id')
        object_one.pop('top_of')
    return group_new


# 家具顶点
def group_bound(size, position, rotation, adjust=[0, 0, 0, 0], direct=0):
    # 角度
    ang = rot_to_ang(rotation)
    # 尺寸
    width_x, width_z = size[0], size[2]
    # 中心
    center_x, center_z = position[0], position[2]
    # 矩形
    angle = ang
    tmp_x = (width_x / 2 + adjust[3])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x1 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z1 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = -(width_x / 2 + adjust[1])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x2 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z2 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = -(width_x / 2 + adjust[1])
    tmp_z = (width_z / 2 + adjust[2])
    add_x3 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z3 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = (width_x / 2 + adjust[3])
    tmp_z = (width_z / 2 + adjust[2])
    add_x4 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z4 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    [x1, x2, x3, x4] = [center_x + add_x1, center_x + add_x2, center_x + add_x3, center_x + add_x4]
    [z1, z2, z3, z4] = [center_z + add_z1, center_z + add_z2, center_z + add_z3, center_z + add_z4]
    if direct >= 1:
        return [x2, z2, x3, z3, x4, z4, x1, z1]
    return [x1, z1, x2, z2, x3, z3, x4, z4]


# 数据构建
def house_build(house_data_info, house_layout_info={}, save_id='', save_dir=DATA_DIR_HOUSE_SCHEME):
    pass


# 数据转换
def house_scene_by_layout(house_id, layout_info, layout_index=0, propose_index=-1, decorate_flag=False):
    house_json_info = {}
    # 数据标识
    house_id = os.path.basename(house_id)
    if house_id.endswith('.json'):
        house_id = house_id[:-5]
    # 加载数据
    temp_dir = DATA_DIR_HOUSE_EMPTY
    if not os.path.exists(temp_dir):
        temp_dir = os.path.dirname(__file__) + '/temp/'
    download_house(house_id, temp_dir)
    house_path = os.path.join(temp_dir, house_id + '.json')
    if not os.path.exists(house_path):
        return house_json_info
    # 解析数据
    try:
        house_json = json.load(open(house_path, 'r', encoding='utf-8'))
    except Exception as e:
        print('get house json error.')
        print(e)
    house_json_new = house_scene_by_layout_detail(house_json, layout_info, layout_index, propose_index, decorate_flag)
    return house_json_new


# 数据转换
def house_scene_by_layout_path(house_path, layout_info, layout_index=0, propose_index=-1, decorate_flag=False):
    house_json_info = {}
    if not os.path.exists(house_path):
        return house_json_info
    # 解析数据
    try:
        house_json = json.load(open(house_path, 'r', encoding='utf-8'))
    except Exception as e:
        print('get house json error.')
        print(e)
    house_json_new = house_scene_by_layout_detail(house_json, layout_info, layout_index, propose_index, decorate_flag)
    return house_json_new


# 数据转换
def house_scene_by_layout_detail(house_json, layout_info, layout_index=0, propose_index=-1, decorate_flag=False):
    furniture_dict_dump, furniture_dict_keep = {}, {}
    # 清空家具
    furniture_count = len(house_json['furniture'])
    for furniture_idx in range(furniture_count - 1, -1, -1):
        uid = house_json['furniture'][furniture_idx]['uid']
        jid = house_json['furniture'][furniture_idx]['jid']
        obj_type, obj_style_eng, obj_size = get_furniture_data(jid)
        if obj_type in GROUP_FURNITURE_LIST:
            uid = house_json['furniture'][furniture_idx]['uid']
            furniture_dict_dump[uid] = jid
            house_json['furniture'].pop(furniture_idx)
        else:
            furniture_dict_keep[jid] = uid
    furniture_count = 20000
    # 统计面片
    mesh_dict_main, mesh_dict_dump, mesh_dict_rest = {}, {}, {}
    mesh_count = len(house_json['mesh'])
    for mesh_idx in range(mesh_count - 1, -1, -1):
        mesh_one = house_json['mesh'][mesh_idx]
        mesh_uid, mesh_type, material_uid = mesh_one['uid'], mesh_one['type'], mesh_one['material']
        mesh_add = {
            'uid': mesh_uid,
            'type': mesh_type,
            'material': material_uid
        }
        if mesh_type in MESH_TYPE_MAIN:
            mesh_dict_main[mesh_uid] = mesh_add
        elif mesh_type in MESH_TYPE_DUMP:
            mesh_dict_dump[mesh_uid] = mesh_add
        elif mesh_type in MESH_TYPE_REST or mesh_type in MESH_TYPE_DECO:
            mesh_dict_rest[mesh_uid] = mesh_add
        elif mesh_type == '':
            pass
        else:
            print('mesh type unknown', mesh_type)
            pass

    # 更新房间
    for room in house_json['scene']['room']:
        room_id = room['instanceid']
        if room_id not in layout_info:
            # 清空装修
            children_count = len(room['children'])
            for child_idx in range(children_count - 1, -1, -1):
                child_one = room['children'][child_idx]
                child_ref = child_one['ref']
                # 清空硬装
                if child_ref in mesh_dict_dump:
                    room['children'].pop(child_idx)
            continue
        # 硬装更换
        material_dict = {}
        # 清空装修
        children_count = len(room['children'])
        for child_idx in range(children_count - 1, -1, -1):
            child_one = room['children'][child_idx]
            child_ref = child_one['ref']
            # 清空家具
            if child_ref in furniture_dict_dump:
                room['children'].pop(child_idx)
            # 清空硬装
            elif child_ref in mesh_dict_dump:
                room['children'].pop(child_idx)
            # 更换硬装
            elif child_ref in mesh_dict_main:
                mesh_type, material_uid = mesh_dict_main[child_ref]['type'], mesh_dict_main[child_ref]['material']
                if material_uid not in material_dict:
                    material_dict[material_uid] = {
                        'type': mesh_type,
                        'count': 0
                    }
                material_dict[material_uid]['count'] += 1
        # 遍历方案
        if 'layout_scheme' not in layout_info[room_id]:
            continue
        if len(layout_info[room_id]['layout_scheme']) <= 0:
            continue
        layout_index_new = layout_index % len(layout_info[room_id]['layout_scheme'])
        room_type, room_layout_one = layout_info[room_id]['room_type'], \
                                     layout_info[room_id]['layout_scheme'][layout_index_new]
        group_list = room_layout_one['group']
        if propose_index >= 0 and 'group_propose' in room_layout_one and len(room_layout_one['group_propose']) > 0:
            propose_index_new = propose_index % len(room_layout_one['group_propose'])
            group_list = room_layout_one['group_propose'][propose_index_new]
        # 遍历家具
        for group_one in group_list:
            if 'obj_list' not in group_one:
                continue
            for furniture_one in group_one['obj_list']:
                # 家具信息
                furniture_id, furniture_type = furniture_one['id'], furniture_one['type']
                furniture_scale = furniture_one['scale']
                furniture_position = furniture_one['position']
                furniture_rotation = furniture_one['rotation']
                furniture_angle = rot_to_ang(furniture_rotation)
                # 特殊处理
                if furniture_id == '58808826-073f-4cc6-9060-920f50b9a403':
                    furniture_angle += math.pi / 2
                elif furniture_id == '7fd324ff-5114-4b8e-9662-259249aa40fa':
                    furniture_angle += math.pi
                furniture_rotation = [0, math.sin(furniture_angle / 2), 0, math.cos(furniture_angle / 2)]
                # 添加家具
                if furniture_id not in furniture_dict_keep:
                    furniture_count += 1
                    uid = str(furniture_count) + '/model'
                    jid = furniture_id
                    furniture_dict_keep[jid] = uid
                    furniture_one = {
                        'uid': uid,
                        'jid': jid,
                        'aid': [],
                        'title': furniture_type
                    }
                    house_json['furniture'].append(furniture_one)
                else:
                    uid = furniture_dict_keep[furniture_id]
                # 添加实例
                child_new = {
                    'ref': uid,
                    'instanceid': str(furniture_count),
                    'pos': furniture_position,
                    'rot': furniture_rotation,
                    'scale': furniture_scale
                }
                room['children'].append(child_new)
        # 遍历纹理
        for material_uid, material_one in material_dict.items():
            if not decorate_flag:
                break
            # 遍历方案
            mesh_type, mesh_count = material_one['type'], material_one['count']
            best_material, best_count = {}, -1
            for group_one in room_layout_one['group']:
                if 'mat_list' not in group_one:
                    continue
                for material_new in group_one['mat_list']:
                    if not material_new['type'] == mesh_type:
                        continue
                    if best_count <= 0:
                        best_count = material_one['count']
                        best_material = material_new
                    elif abs(best_count - mesh_count) > abs(material_one['count'] - mesh_count):
                        best_count = material_one['count']
                        best_material = material_new
                if best_count > 0:
                    break
            # 替换方案
            if best_count > 0 and len(best_material) > 0:
                material_new, texture_new = house_scene_check_texture(best_material['jid'], best_material['texture'])
                for material_old in house_json['material']:
                    if material_old['uid'] == material_uid:
                        material_old['jid'] = material_new
                        material_old['texture'] = texture_new
                        break

    # 返回场景
    return house_json


# 纹理检查
def house_scene_check_texture(material_old, texture_old):
    material_new, texture_new = material_old, texture_old
    if 'wallfloor' in texture_old:
        return material_new, texture_new
    elif material_old == 'local':
        return material_new, texture_new
    elif len(material_old) <= 0 and len(texture_old) > 0:
        material_new = texture_old.split('/')[-1].split('_')[0]
        texture_new = 'https://juran-prod-assets.s3.cn-north-1.amazonaws.com.cn/i/%s/wallfloor.jpg' % material_new
    return material_new, texture_new

