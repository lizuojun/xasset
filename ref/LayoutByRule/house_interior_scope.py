# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-09-28
@Description: 全屋布局调整

"""

from Furniture.furniture_group import *
from Furniture.furniture_group_comp import *
from Furniture.furniture_refer import *

# 临时目录
RECT_DIR_TEMP = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(RECT_DIR_TEMP):
    os.makedirs(RECT_DIR_TEMP)

# 部件尺寸
UNIT_HEIGHT_WALL = 2.80
UNIT_HEIGHT_CEIL = 0.15
UNIT_HEIGHT_ARMOIRE_MIN = 1.5
UNIT_HEIGHT_ARMOIRE_MID = 2.0
# 部件尺寸
UNIT_DEPTH_CURTAIN = 0.23
UNIT_DEPTH_FLOOR_FRAME = 0.02


# 布局模式
LAYOUT_SEED_TRANSFER = 0  # 迁移布局
LAYOUT_SEED_PROPOSE = 1  # 推荐布局
LAYOUT_SEED_SCHEME = 2  # 方案布局
LAYOUT_SEED_ADJUST = 3  # 调整布局
LAYOUT_SEED_REFER = 4  # 参考布局

# 默认家具
OBJECT_MEDIA_WALL = {}


# 计算家具位置
def house_rect_scope(house_data_info, house_layout_info):
    data_info, layout_info, propose_info = house_data_info, house_layout_info, {}
    if 'room' not in data_info:
        return propose_info
    # 遍历房间
    for room_one in data_info['room']:
        # 房间信息
        room_id = room_one['id']
        if room_id not in layout_info:
            continue
        room_data_info, room_layout_info = room_one, layout_info[room_id]
        room_propose_info = room_rect_scope(room_data_info, room_layout_info)
        propose_info[room_id] = room_propose_info
    # 返回信息
    return propose_info


# 计算家具位置
def room_rect_scope(room_data_info, room_layout_info):
    data_info, layout_info, propose_info = room_data_info, room_layout_info, []
    if len(layout_info) <= 0:
        return propose_info
    if 'floor' not in data_info:
        return propose_info
    if len(data_info['floor']) <= 2:
        return propose_info
    room_type, room_area = layout_info['room_type'], layout_info['room_area']
    room_height, ceil_height = UNIT_HEIGHT_WALL, UNIT_HEIGHT_CEIL
    if 'room_height' in layout_info:
        room_height = layout_info['room_height']
    if 'ceil_height' in layout_info:
        ceil_height = layout_info['ceil_height']
    # 计算方案
    if 'layout_scheme' not in layout_info:
        return propose_info
    if len(layout_info['layout_scheme']) <= 0:
        return propose_info
    layout_complete = True
    if 'layout_sample' not in layout_info:
        layout_complete = False
    elif len(layout_info['layout_sample']) <= 0:
        layout_complete = False
    # 贴墙电视
    global OBJECT_MEDIA_WALL
    if len(OBJECT_MEDIA_WALL) <= 0:
        OBJECT_MEDIA_WALL = copy_object_by_id(MEDIA_WALL_ID)
    # 遍历方案
    layout_scheme = layout_info['layout_scheme']
    for layout_idx, layout_one in enumerate(layout_scheme):
        # 调试打印
        if layout_info['room_type'] in ['Bathroom'] and layout_idx == 0 and False:
            print('scope room:', layout_info['room_type'], 'debug', layout_idx)
        # 硬装信息
        material_one = {}
        if 'material' in layout_one:
            material_one = layout_one['material']
        if 'self_transfer' in material_one and material_one['self_transfer']:
            if 'customized_ceiling' in material_one and len(material_one['customized_ceiling']) > 0:
                ceiling_one = material_one['customized_ceiling'][0]
                if 'size' in ceiling_one and len(ceiling_one['size']) >= 3:
                    if 'scale' in ceiling_one and len(ceiling_one['scale']) >= 3:
                        ceil_size = [abs(ceiling_one['size'][i] * ceiling_one['scale'][i]) / 100 for i in range(3)]
                        ceil_height = min(max(ceil_size[1], 0.05), 0.50)
        # 模板信息
        source_house, source_room = layout_one['source_house'], layout_one['source_room']
        object_wall, object_ceil, object_floor, object_window = [], [], [], []
        # 种子信息
        seed_list, keep_list, seed_dict, keep_dict = [], [], {}, {}
        if 'layout_seed' in room_layout_info:
            seed_list = room_layout_info['layout_seed']
        if 'layout_keep' in room_layout_info:
            keep_list = room_layout_info['layout_keep']
        for seed_one in seed_list:
            seed_id = seed_one['id']
            seed_dict[seed_id] = seed_one
        for keep_one in keep_list:
            keep_id = keep_one['id']
            keep_dict[keep_id] = keep_one

        # 遍历分组 布局信息
        group_list, group_side = layout_one['group'], {}
        for group_one in group_list:
            if group_one['type'] in ['Armoire', 'Cabinet']:
                if len(group_side) <= 0:
                    group_side = group_one
                elif group_side['size'][0] < group_one['size'][0]:
                    group_side = group_one
        for group_one in group_list:
            group_type, group_main = group_one['type'], group_one['obj_main']
            group_size, group_offset = group_one['size'], group_one['offset']
            group_size_min, group_size_old = group_size[:], group_size[:]
            if 'size_min' in group_one:
                group_size_min = group_one['size_min'][:]
            if 'seed_size_old' in group_one:
                group_size_old = group_one['seed_size_old'][:]
            if 'obj_list' not in group_one:
                group_one['obj_list'] = []
            # 特殊标志
            vertical_flag, center_flag, window_flag = 0, 0, 0
            if 'vertical' in group_one:
                vertical_flag = group_one['vertical']
            if 'center' in group_one:
                center_flag = group_one['center']
            if 'window' in group_one:
                window_flag = group_one['window']
            # 调整标志
            corner_flag, adjust_flag, stretch_flag = 0, 0, 0
            if 'adjust' in group_one and group_type in ['Armoire', 'Cabinet']:
                adjust_flag = group_one['adjust']
            if 'stretch' in group_one:
                stretch_flag = group_one['stretch']
            # 横向方向
            region_direct, region_middle = 0, 0.5
            if 'region_direct' in group_one:
                region_direct = group_one['region_direct']
            if 'region_middle' in group_one:
                region_middle = group_one['region_middle']
            # 功能区域
            if group_type in GROUP_RULE_FUNCTIONAL:
                # 默认分组
                if 'adjust' in group_one and group_one['adjust'] >= 1:
                    group_detail = get_furniture_group('sample_house', source_room, group_type, group_main, group_size_old)
                    if 'code' in group_detail and not group_detail['code'] == group_one['code']:
                        group_detail = {}
                    elif 'obj_main' in group_detail and not group_detail['obj_main'] == group_one['obj_main']:
                        group_detail = {}
                    if len(group_detail) <= 0:
                        group_detail = get_default_group_main(group_type, group_main, group_size_old)
                # 自身分组
                elif 'sample' in source_house or 'scheme' in source_house or 'scene' in source_house:
                    group_detail = get_furniture_group(source_house, source_room, group_type, group_main, group_size_old)
                    if len(group_detail) <= 0:
                        group_detail = get_default_group_main(group_type, group_main, group_size_old)
                    if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
                        group_one['obj_list'] = []
                # 默认分组
                else:
                    group_detail = get_furniture_group('sample_house', source_room, group_type, group_main, group_size_old)
                    if 'code' in group_detail and not group_detail['code'] == group_one['code']:
                        group_detail = {}
                    elif 'obj_main' in group_detail and not group_detail['obj_main'] == group_one['obj_main']:
                        group_detail = {}
                    if len(group_detail) <= 0:
                        group_detail = get_default_group_main(group_type, group_main, group_size_old)
                if 'obj_list' in group_detail and len(group_detail['obj_list']) > 0:
                    pass
                # 推荐分组
                elif 'source_house' in group_one and 'source_room' in group_one:
                    group_detail = get_furniture_group(source_house, source_room, group_type, group_main, group_size_old)
                # 本地分组
                else:
                    group_detail = get_furniture_group(source_house, source_room, group_type, group_main, group_size_old)
                # 补充物品
                if 'obj_list' in group_detail and layout_complete:
                    add_default_object(group_detail, room_type, room_area)
            # 装饰区域
            elif group_type in GROUP_RULE_DECORATIVE:
                group_detail = {
                    'obj_list': group_one['obj_list']
                }
                if group_type == 'Wall':
                    object_wall = group_one['obj_list']
                elif group_type == 'Ceiling':
                    object_ceil = group_one['obj_list']
                elif group_type == 'Floor':
                    object_floor = group_one['obj_list']
                elif group_type == 'Window':
                    object_window = group_one['obj_list']

            # 重置分组
            resolve_group_regulation(group_one)
            # 造型调整
            scale_rat = 1
            if 'size' in group_detail:
                group_size_old = group_detail['size']
                scale_x, scale_z = abs(group_size[0] / group_size_old[0]), abs(group_size[2] / group_size_old[2])
                scale_rat = min(scale_x, scale_z)
            if stretch_flag >= 1:
                pass
            elif group_main.endswith('.json'):
                stretch_flag = 1
            elif group_type in ['Media']:
                object_list_old = group_detail['obj_list']
                table_list_1, table_list_2 = [], []
                for object_one in object_list_old:
                    object_key, object_role = object_one['id'], ''
                    if 'role' in object_one:
                        object_role = object_one['role']
                    if object_role in ['table']:
                        if 'media unit' in object_one['type']:
                            table_list_1.append(object_one)
                        else:
                            table_list_2.append(object_one)
                        if object_key.endswith('.json'):
                            stretch_flag = 1
                if len(table_list_1) > 0:
                    for object_old in table_list_2:
                        object_list_old.remove(object_old)
            if stretch_flag >= 1 and scale_rat < 0.9:
                main_role, main_move = GROUP_RULE_FUNCTIONAL[group_type]['main'], [0, 0, 0]
                if group_type in ['Media']:
                    main_role = 'table'
                group_offset = group_one['offset']
                group_detail_new = group_detail.copy()
                object_list_old = group_detail['obj_list']
                object_list_new = []
                for object_one in object_list_old:
                    object_role, relate_role = '', ''
                    if 'role' in object_one:
                        object_role = object_one['role']
                    if 'relate_role' in object_one:
                        relate_role = object_one['relate_role']
                    # 新增
                    object_new = copy_object(object_one)
                    # 缩放
                    if object_role == main_role:
                        # 移动
                        origin_size, origin_scale = object_one['size'], object_one['scale']
                        object_size = [abs(origin_size[i] * origin_scale[i] / 100) for i in range(3)]
                        main_move[2] = object_size[2] * (scale_rat - 1) * 0.5
                        # 缩放
                        scale_new = object_new['scale']
                        scale_new[0] *= scale_rat
                        scale_new[2] *= scale_rat
                    elif relate_role == main_role:
                        scale_new = object_new['scale']
                        scale_new[0] *= scale_rat
                        scale_new[2] *= scale_rat
                    # 平移
                    if object_role in ['rug', 'screen']:
                        pass
                    else:
                        norm_pos = object_new['normal_position']
                        norm_pos[0] *= scale_rat
                        norm_pos[2] *= scale_rat
                    object_list_new.append(object_new)
                group_detail_new['obj_list'] = object_list_new
                group_detail = group_detail_new
                # offset
                if group_type in ['Media']:
                    group_offset[0] = group_detail['offset'][0] * scale_rat
                    group_offset[2] = group_detail['offset'][2] * scale_rat + main_move[2]
                else:
                    group_offset[0] = 0
                    group_offset[2] += main_move[2]

            # 重置范围
            group_size, group_offset = group_one['size'], group_one['offset']
            group_position,  group_angle = group_one['position'], rot_to_ang(group_one['rotation'])
            group_x_min, group_x_max = -group_size[0] / 2, group_size[0] / 2
            group_z_min, group_z_max = -group_size[2] / 2, group_size[2] / 2

            # 物品范围
            group_x_min_obj, group_x_max_obj = group_x_min, group_x_max
            group_z_min_obj, group_z_max_obj = group_z_min, group_z_max
            # 地毯范围
            group_x_min_rug, group_x_max_rug = group_x_min, group_x_max
            group_z_min_rug, group_z_max_rug = group_z_min, group_z_max
            group_neighbor_base, group_neighbor_more = [0, 0, 0, 0], [0, 0, 0, 0]
            if vertical_flag == 0 and center_flag == 0:
                if 'neighbor_base' in group_one:
                    group_neighbor_base = group_one['neighbor_base'][:]
                    group_neighbor_more = group_one['neighbor_base'][:]
                    group_x_min_obj -= group_neighbor_base[1]
                    group_x_max_obj += group_neighbor_base[3]
                    group_z_min_obj -= group_neighbor_base[0]
                    group_z_max_obj += group_neighbor_base[2]
                if 'neighbor_more' in group_one:
                    group_neighbor_more = group_one['neighbor_more'][:]
                group_x_min_rug -= group_neighbor_more[1]
                group_x_max_rug += group_neighbor_more[3]
                group_z_min_rug -= group_neighbor_more[0]
                group_z_max_rug += group_neighbor_more[2]
            elif center_flag >= 1 and group_type in ['Meeting']:
                if 'neighbor_more' in group_one:
                    group_neighbor_more = group_one['neighbor_more'][:]
                group_x_min_rug -= group_neighbor_more[1]
                group_x_max_rug += group_neighbor_more[3]
                group_z_min_rug -= group_neighbor_more[0]
                group_z_max_rug += group_neighbor_more[2]
            # 左右范围
            group_size_left1, group_size_right1 = 0, 0
            group_size_left2, group_size_right2 = 0, 0
            if 'size_rest' in group_one:
                group_size_left0, group_size_right0 = group_one['size_rest'][1], group_one['size_rest'][3]
                group_size_left1, group_size_right1 = group_one['size_rest'][1], group_one['size_rest'][3]
                group_size_left2, group_size_right2 = group_one['size_rest'][1], group_one['size_rest'][3]
            if vertical_flag == 0:
                if 'neighbor_base' in group_one:
                    group_neighbor_base = group_one['neighbor_base'][:]
                    group_size_left1 += min(group_neighbor_base[1], 1.0)
                    group_size_right1 += min(group_neighbor_base[3], 1.0)
                if 'neighbor_more' in group_one:
                    group_neighbor_more = group_one['neighbor_more'][:]
                    group_size_left2 += min(group_neighbor_more[1], 1.0)
                    group_size_right2 += min(group_neighbor_more[3], 1.0)

            # 计算尺寸
            if group_type in GROUP_RULE_DECORATIVE:
                compute_furniture_scope(group_one, [], room_type)
                continue
            # 检查家具
            if 'obj_list' not in group_detail:
                continue
            if group_size[0] <= 0 or group_size[2] <= 0:
                continue

            # 种子信息
            object_seed_id, object_seed_type, object_seed_role = '', '', ''
            object_keep_id, object_keep_type, object_keep_role = '', '', ''
            if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
                object_seed_id = group_one['seed_list'][0]
                for seed_one in seed_list:
                    if seed_one['id'] == object_seed_id:
                        object_seed_type = seed_one['type']
                        object_seed_role = seed_one['role']
            if 'keep_list' in group_one and len(group_one['keep_list']) > 0:
                object_keep_id = group_one['keep_list'][0]
                for keep_one in seed_list:
                    if keep_one['id'] == object_keep_id:
                        object_keep_type = keep_one['type']
                        object_keep_role = keep_one['role']
                for keep_one in keep_list:
                    if keep_one['id'] == object_keep_id:
                        object_keep_type = keep_one['type']
                        object_keep_role = keep_one['role']
            # 家具信息
            object_list_old, object_list, object_lift_bot = group_detail['obj_list'], [], 0
            object_media_old, object_media_new, object_table_old = {}, {}, {}
            for object_one in object_list_old:
                if object_one['role'] in ['tv']:
                    object_media_old = object_one
                if object_one['role'] in ['table']:
                    object_table_old = object_one
                if object_one['role'] in ['rug']:
                    object_bottom = object_one['position'][1]
                    object_height = abs(object_one['size'][1] * object_one['scale'][1]) / 100
                    if object_lift_bot < object_bottom + object_height < 0.05:
                        object_lift_bot = object_bottom + object_height
                object_list.append(object_one)
            if 'type' in object_media_old and 'TV - on top of others' in object_media_old['type']:
                if len(object_table_old) <= 0:
                    replace_furniture_media(object_media_old, OBJECT_MEDIA_WALL, group_one)
            # 家具复制
            side_table_copy, side_table_paste, side_sofa_copy, side_sofa_paste = [], 0,  [], 0
            side_table_left, side_table_right, side_sofa_left, side_sofa_right = [], [], [], []
            if group_type in ['Meeting', 'Bed']:
                side_table_copy, side_table_left, side_table_right = \
                    resolve_furniture_copy(group_detail['obj_list'], group_size_left1, group_size_right1,
                                           group_one, ['side table'])
            if group_type in ['Meeting']:
                side_sofa_copy, side_sofa_left, side_sofa_right = \
                    resolve_furniture_copy(group_detail['obj_list'], group_size_left2, group_size_right2,
                                           group_one, ['side sofa'])
            for object_add in side_table_copy:
                object_list.append(object_add)
                if object_add['normal_position'][0] < 0:
                    side_table_paste = -1
                else:
                    side_table_paste = 1
            for object_add in side_sofa_copy:
                object_list.append(object_add)
                if object_add['normal_position'][0] < 0:
                    side_sofa_paste = -1
                else:
                    side_sofa_paste = 1
            # 茶几调整
            table_swap, table_dump = False, False
            # 遍历家具
            object_main_id, object_main_type, object_main_plat = group_one['obj_main'], '', {}
            dump_list, stay_list, fake_flag, fake_dict, zoom_dict = [], [], 0, {}, {}
            for object_idx, object_one in enumerate(object_list):
                object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
                if object_one in side_sofa_copy:
                    if len(side_sofa_left) > 0 and side_sofa_left[0] in stay_list:
                        continue
                    elif len(side_sofa_right) > 0 and side_sofa_right[0] in stay_list:
                        continue
                # 标识
                if object_id == object_main_id:
                    object_main_type = object_type
                    if adjust_flag >= 1:
                        origin_size, origin_scale = object_one['size'], object_one['scale']
                        object_size = [abs(origin_size[i] * origin_scale[i] / 100) for i in range(3)]
                        if object_size[0] <= group_size[0] - 0.01:
                            origin_scale = [abs(group_size[i]) * 100 / (abs(origin_size[i]) + 0.01) for i in range(3)]
                            object_one['scale'] = origin_scale[:]
                if 'turn' in object_one and abs(object_one['turn']) >= 0.1:
                    object_turn = get_furniture_turn(object_id)
                    if abs(object_turn) <= 0.1:
                        add_furniture_turn(object_id, object_one['turn'])
                    pass
                # 位置
                origin_position, origin_rotation = object_one['position'][:], object_one['rotation']
                if 'normal_position' in object_one:
                    origin_position = object_one['normal_position'][:]
                if 'normal_rotation' in object_one:
                    origin_rotation = object_one['normal_rotation']
                origin_angle = rot_to_ang(origin_rotation)
                if object_role in ['tv'] and len(object_list) <= 1:
                    if origin_position[1] < 0.5 or origin_position[1] > 1.0:
                        origin_position[1] = 0.75
                elif object_role in ['back table']:
                    if origin_position[0] < 0 - 0.2 and group_neighbor_more[1] - group_neighbor_more[3] > 0.2:
                        origin_position[0] *= -1
                    elif origin_position[0] < 0 + 0.2 and group_neighbor_more[3] - group_neighbor_more[1] > 0.2:
                        origin_position[0] *= -1

                # 尺寸
                origin_size, origin_scale = object_one['size'], object_one['scale']
                object_size = [abs(origin_size[i] * origin_scale[i] / 100) for i in range(3)]
                object_width, object_depth, object_height = object_size[0], object_size[2], object_size[1]
                if abs(abs(origin_angle) - math.pi / 2) < 0.5:
                    object_width, object_depth = object_size[2], object_size[0]
                # 缩放
                fake_scale_offset = [1, 1, 1, 0, 0, 0, origin_position[0]]
                # 高度
                if object_height > room_height - ceil_height:
                    fake_flag = 1
                    if object_id in fake_dict:
                        fake_scale_offset = fake_dict[object_id]
                    fake_scale_offset[1] = abs(room_height - ceil_height) / abs(object_height)
                    fake_dict[object_id] = fake_scale_offset
                elif UNIT_HEIGHT_ARMOIRE_MID - 0.05 < object_height < room_height - ceil_height - 0.05:
                    if group_type in ['Armoire']:
                        fake_flag = 1
                        if object_id in fake_dict:
                            fake_scale_offset = fake_dict[object_id]
                        fake_scale_offset[1] = abs(room_height - ceil_height) / abs(object_height)
                        fake_dict[object_id] = fake_scale_offset
                    elif group_type in ['Cabinet'] and (object_width > 1.5 or room_type not in ['Library']):
                        fake_flag = 1
                        if object_id in fake_dict:
                            fake_scale_offset = fake_dict[object_id]
                        fake_scale_offset[1] = abs(room_height - ceil_height) / abs(object_height)
                        fake_dict[object_id] = fake_scale_offset
                # 依附
                relate_id, relate_role = '', ''
                if 'relate' in object_one:
                    relate_id = object_one['relate']
                if 'relate_role' in object_one:
                    relate_role = object_one['relate_role']
                # 缩放
                x_adjust, y_adjust, z_adjust = 0, 0, 0
                if object_role in ['rug']:
                    pass
                elif object_role in ['part'] and relate_role not in ['rug']:
                    pass
                elif object_role in ['accessory'] and relate_role not in ['rug']:
                    object_z_min = group_offset[2] + origin_position[2] - object_depth / 2
                    object_z_max = group_offset[2] + origin_position[2] + object_depth / 2
                    z_offset_1, z_offset_2 = object_z_min - group_z_min, group_z_max - object_z_max
                    if -0.1 < z_offset_1 < -0.001 < z_offset_2:
                        origin_position[2] -= z_offset_1
                else:
                    object_x_min = group_offset[0] + origin_position[0] - object_width / 2
                    object_x_max = group_offset[0] + origin_position[0] + object_width / 2
                    object_z_min = group_offset[2] + origin_position[2] - object_depth / 2
                    object_z_max = group_offset[2] + origin_position[2] + object_depth / 2

                    x_offset_1, x_offset_2 = object_x_min - group_x_min, group_x_max - object_x_max
                    z_offset_1, z_offset_2 = object_z_min - group_z_min, group_z_max - object_z_max
                    if object_role in ['table'] and group_type in ['Meeting']:
                        z_offset_1, z_offset_2 = object_z_min - group_z_min_rug, group_z_max_rug - object_z_max
                    elif object_role in ['side table', 'side lamp', 'side plant']:
                        x_offset_1, x_offset_2 = object_x_min - group_x_min_obj, group_x_max_obj - object_x_max
                        z_offset_1, z_offset_2 = object_z_min - group_z_min_obj, group_z_max_rug - object_z_max
                        if object_role in [object_seed_role, object_keep_role]:
                            x_offset_1, x_offset_2 = object_x_min - group_x_min_rug, group_x_max_rug - object_x_max
                            z_offset_1, z_offset_2 = object_z_min - group_z_min_rug, group_z_max_rug - object_z_max
                    elif object_role in ['side sofa', 'back table', 'accessory']:
                        x_offset_1, x_offset_2 = object_x_min - group_x_min_rug, group_x_max_rug - object_x_max
                        z_offset_1, z_offset_2 = object_z_min - group_z_min_rug, group_z_max_rug - object_z_max
                        if center_flag <= 0:
                            if origin_position[0] < 0 and side_sofa_paste > 0:
                                x_offset_1, x_offset_2 = object_x_min - group_x_min_obj, group_x_max_obj - object_x_max
                            elif origin_position[0] > 0 and side_sofa_paste < 0:
                                x_offset_1, x_offset_2 = object_x_min - group_x_min_obj, group_x_max_obj - object_x_max
                        else:
                            x_offset_1 = object_x_min - group_x_min_rug
                            x_offset_2 = group_x_max_rug - object_x_max
                    elif object_role in ['chair'] and group_type in ['Work', 'Rest']:
                        z_offset_1, z_offset_2 = object_z_min - group_z_min_rug, group_z_max_rug - object_z_max
                    # 丢弃判定
                    x_offset_d, z_offset_d = -0.010, -0.020
                    if object_role in ['armoire', 'cabinet', 'tv', 'appliance']:
                        x_offset_d = 0 - 0.01
                    elif object_role in ['table'] and group_type in ['Meeting']:
                        x_offset_d = 0 - 0.05
                    elif object_role in ['table'] and group_type in ['Bed']:
                        z_offset_d = 0 + 0.20
                    elif object_role in ['table'] and group_type in ['Media']:
                        z_offset_d = 0 + 0.10
                        if 'Living' in room_type:
                            z_offset_d = 0 - 0.10

                    # 缩小调整
                    if x_offset_1 < x_offset_d or x_offset_2 < x_offset_d or z_offset_2 < z_offset_d:
                        scale_flag = False
                        if object_role == object_seed_role:
                            scale_flag = True
                        # meeting
                        elif object_role in ['sofa', 'bed'] and (z_offset_1 < -0.05 or z_offset_2 < -0.05):
                            scale_flag = True
                        elif object_role in ['sofa', 'bed'] and z_offset_2 > z_offset_d:
                            if object_role in [object_seed_role, object_keep_role]:
                                if -0.80 < x_offset_1 < x_offset_d < x_offset_2:
                                    scale_flag = True
                                elif -0.80 < x_offset_2 < x_offset_d < x_offset_1:
                                    scale_flag = True
                            elif -0.40 < x_offset_1 < x_offset_d or -0.40 < x_offset_2 < x_offset_d:
                                scale_flag = True
                        elif object_role in ['table'] and group_type in ['Meeting'] and abs(z_offset_2) < 0.10:
                            scale_flag = True
                        elif object_role in ['table'] and group_type in ['Meeting'] and z_offset_2 > z_offset_d:
                            if object_role in [object_seed_role, object_keep_role]:
                                if -0.80 < x_offset_1 < x_offset_d < x_offset_2:
                                    scale_flag = True
                                elif -0.80 < x_offset_2 < x_offset_d < x_offset_1:
                                    scale_flag = True
                            elif -0.05 < x_offset_1 < x_offset_d or -0.05 < x_offset_2 < x_offset_d:
                                scale_flag = True
                        elif object_role in ['side table'] and z_offset_2 > z_offset_d:
                            if object_role in [object_seed_role, object_keep_role]:
                                if abs(side_table_paste) < 1:
                                    scale_flag = True
                                elif -0.40 < x_offset_1 < x_offset_d < x_offset_2:
                                    if -0.20 < x_offset_1:
                                        scale_flag = True
                                    elif side_table_paste <= 0:
                                        scale_flag = True
                                elif -0.40 < x_offset_2 < x_offset_d < x_offset_1:
                                    if -0.20 < x_offset_2:
                                        scale_flag = True
                                    elif side_table_paste >= 0:
                                        scale_flag = True
                            elif -0.02 < x_offset_1 < x_offset_d or -0.02 < x_offset_2 < x_offset_d:
                                scale_flag = True
                        elif object_role in ['side sofa'] and z_offset_2 > z_offset_d:
                            if object_role in [object_seed_role, object_keep_role]:
                                if abs(side_sofa_paste) < 1:
                                    scale_flag = True
                                    if x_offset_1 < x_offset_d and len(side_sofa_right) <= 0:
                                        origin_position[0] *= -0.2
                                        table_dump = True
                                    elif x_offset_2 < x_offset_d and len(side_sofa_left) <= 0:
                                        origin_position[0] *= -0.2
                                        table_dump = True
                                elif -0.80 < x_offset_1 < x_offset_d < x_offset_2:
                                    if side_sofa_paste <= 0:
                                        scale_flag = True
                                elif -0.80 < x_offset_2 < x_offset_d < x_offset_1:
                                    if side_sofa_paste >= 0:
                                        scale_flag = True
                            elif -0.05 < x_offset_1 < x_offset_d or -0.05 < x_offset_2 < x_offset_d:
                                scale_flag = True
                        elif object_role in ['side plant', 'side lamp'] and z_offset_2 > z_offset_d:
                            if -0.05 < x_offset_1 < x_offset_d or -0.05 < x_offset_2 < x_offset_d:
                                scale_flag = True
                        elif object_role in ['back table']:
                            scale_flag = True
                        # media
                        elif object_role in ['table'] and group_type in ['Media']:
                            if len(object_list) <= 1:
                                scale_flag = True
                            elif -0.15 < x_offset_1 < x_offset_d or -0.15 < x_offset_2 < x_offset_d:
                                scale_flag = True
                        # dining
                        elif object_role in ['table'] and group_type in ['Dining', 'Work', 'Rest']:
                            scale_flag = True
                        # cabinet
                        elif object_role in ['armoire', 'cabinet', 'tv', 'appliance']:
                            scale_flag = True
                        # bath
                        elif object_role in ['bath']:
                            scale_flag = True
                            if object_idx >= 1 and x_offset_1 < -0.50 or x_offset_2 < -0.50:
                                scale_flag = False
                        elif object_role in ['screen']:
                            scale_flag = True
                        # 缩放
                        if scale_flag:
                            fake_flag = 1
                            if object_id in fake_dict:
                                fake_scale_offset = fake_dict[object_id]
                            # 边桌
                            if object_role in ['side table', 'side plant', 'side lamp'] and -0.05 < x_offset_1 < x_offset_d and object_x_max < 0 - group_size_min[0] / 2 + x_offset_1:
                                fake_scale_offset = [1, 1, 1, 0 - x_offset_1, 0, 0, origin_position[0]]
                                zoom_dict[object_id] = fake_scale_offset
                            elif object_role in ['side table', 'side plant', 'side lamp'] and -0.05 < x_offset_2 < x_offset_d and object_x_min > 0 + group_size_min[0] / 2 - x_offset_2:
                                fake_scale_offset = [1, 1, 1, 0 + x_offset_2, 0, 0, origin_position[0]]
                                zoom_dict[object_id] = fake_scale_offset
                            # 横向
                            elif x_offset_1 <= x_offset_2 and x_offset_1 < 0:
                                if x_offset_2 >= 0:
                                    fake_scale_offset[0] = (object_width + x_offset_1 * 1) / object_width
                                    fake_scale_offset[3] = 0 - x_offset_1 * 0.5
                                else:
                                    fake_scale_offset[0] = (object_width + x_offset_1 + x_offset_2) / object_width
                                if object_role in ['side table', 'side plant', 'side lamp', 'side sofa']:
                                    fake_scale_offset[1] = fake_scale_offset[0]
                                    fake_scale_offset[2] = fake_scale_offset[0]
                            elif x_offset_2 <= x_offset_1 and x_offset_2 < 0:
                                if x_offset_1 >= 0:
                                    fake_scale_offset[0] = (object_width + x_offset_2 * 1) / object_width
                                    fake_scale_offset[3] = 0 + x_offset_2 * 0.5
                                else:
                                    fake_scale_offset[0] = (object_width + x_offset_1 + x_offset_2) / object_width
                                if object_role in ['side table', 'side plant', 'side lamp', 'side sofa']:
                                    fake_scale_offset[1] = fake_scale_offset[0]
                                    fake_scale_offset[2] = fake_scale_offset[0]
                            # 纵向
                            if z_offset_1 <= z_offset_2 and z_offset_1 < 0:
                                if z_offset_2 < -0.01:
                                    fake_scale_offset[2] = (object_depth + z_offset_1 * 2) / object_depth
                                else:
                                    fake_scale_offset[2] = (object_depth + z_offset_1 * 1) / object_depth
                                    fake_scale_offset[5] = -z_offset_1 / 2
                            elif z_offset_2 <= z_offset_1 and z_offset_2 < 0:
                                if z_offset_1 < -0.01:
                                    fake_scale_offset[2] = (object_depth + z_offset_2 * 2) / object_depth
                                else:
                                    fake_scale_offset[2] = (object_depth + z_offset_2 * 1) / object_depth
                                    fake_scale_offset[5] = z_offset_2 / 2
                            # 调整
                            if object_role not in ['screen']:
                                fake_dict[object_id] = fake_scale_offset
                        # 移动
                        elif object_role in ['sofa', 'bed']:
                            fake_flag = 1
                            if x_offset_1 <= x_offset_2 and x_offset_1 < 0:
                                if x_offset_2 <= 0:
                                    fake_scale_offset[3] = -x_offset_1 * 2
                                else:
                                    fake_scale_offset[3] = -x_offset_1 * 1
                            elif x_offset_2 <= x_offset_1 and x_offset_2 < 0:
                                if x_offset_1 <= 0:
                                    fake_scale_offset[3] = x_offset_2 * 2
                                else:
                                    fake_scale_offset[3] = x_offset_2
                        # 丢弃
                        else:
                            dump_list.append(object_one)
                            # 切换
                            if object_role in ['table'] and group_type in ['Media']:
                                if 'type' in object_media_new and 'TV - on top of others' in object_media_new['type']:
                                    replace_furniture_media(object_media_new, OBJECT_MEDIA_WALL, group_one)
                                elif 'size_rest' in group_one and group_one['size_rest'][0] > 0.01:
                                    replace_furniture_media(object_media_new, OBJECT_MEDIA_WALL, group_one)
                            continue
                    # 扩大调整
                    elif 0.00 <= x_offset_1 < 0.01 < x_offset_2 < max(0.10, object_width * 0.30) \
                            or 0.00 <= x_offset_2 < 0.01 < x_offset_1 < max(0.10, object_width * 0.30) \
                            or 0.01 < x_offset_1 <= x_offset_2 < max(0.10, object_width * 0.15) \
                            or 0.01 < x_offset_2 <= x_offset_1 < max(0.10, object_width * 0.15):
                        scale_flag = False
                        if object_role in ['armoire', 'cabinet'] and len(object_list) <= 10:
                            scale_flag = True
                        if object_role in ['armoire', 'cabinet'] and object_id in fake_dict:
                            scale_flag = True
                        if object_role in ['cabinet'] and 'Bathroom' in room_type:
                            scale_flag = False
                        # 缩放
                        if scale_flag:
                            fake_flag = 2
                            if 0 <= x_offset_2 < 0.01 < x_offset_1:
                                fake_scale_offset[0] = (object_width + x_offset_1) / object_width
                                fake_scale_offset[3] -= x_offset_1 / 2
                            elif 0 <= x_offset_1 < 0.01 < x_offset_2:
                                fake_scale_offset[0] = (object_width + x_offset_2) / object_width
                                fake_scale_offset[3] += x_offset_2 / 2
                            else:
                                fake_scale_offset[0] = (object_width + x_offset_1 + x_offset_2) / object_width
                                fake_scale_offset[3] -= x_offset_1 / 2
                                fake_scale_offset[3] += x_offset_2 / 2
                            if object_role not in ['screen']:
                                fake_dict[object_id] = fake_scale_offset
                                zoom_dict[object_id] = fake_scale_offset
                    # 丢弃边桌
                    if object_role in ['table'] and table_dump:
                        dump_list.append(object_one)
                        continue

                # 丢弃边椅
                if object_role == 'side sofa' and not object_main_type == object_seed_type:
                    if object_seed_type in SOFA_CORNER_TYPE_0:
                        dump_list.append(object_one)
                        continue
                # 丢弃配件
                if object_role == 'accessory' and (len(relate_id) > 0 or len(relate_role) > 0):
                    plat_find = {}
                    for plat_one in object_list:
                        if relate_role in ['rug']:
                            break
                        if not relate_id == plat_one['id']:
                            continue
                        if 'normal_position' in plat_one and 'normal_rotation' in plat_one:
                            plat_x = abs(plat_one['normal_position'][0] - origin_position[0])
                            plat_z = abs(plat_one['normal_position'][2] - origin_position[2])
                            plat_a = rot_to_ang(plat_one['normal_rotation'])
                            plat_s = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
                            if abs(plat_a - math.pi / 2) < 0.1 or abs(plat_a + math.pi / 2) < 0.1:
                                if plat_x <= plat_s[2] / 2 and plat_z <= plat_s[0] / 2:
                                    plat_find = plat_one
                                    break
                            else:
                                if plat_x <= plat_s[0] / 2 and plat_z <= plat_s[2] / 2:
                                    plat_find = plat_one
                                    break
                    if len(plat_find) > 0:
                        # 丢弃
                        if plat_find in dump_list:
                            continue
                        elif relate_id in fake_dict and relate_id not in zoom_dict:
                            continue
                        elif 'offset_position' in plat_find:
                            object_one['offset_position'] = plat_find['offset_position']
                    # 缩放判断
                    if relate_id in fake_dict:
                        fake_flag = 3

                # 拐角沙发
                sofa_type = ''
                if object_seed_type in SOFA_CORNER_TYPE_1:
                    sofa_type = object_seed_type
                elif object_seed_type in SOFA_CORNER_TYPE_2:
                    sofa_type = object_seed_type
                elif object_main_type in SOFA_CORNER_TYPE_1:
                    sofa_type = object_main_type
                # 调整地毯
                if object_role == 'rug':
                    # 更新
                    object_add = object_one.copy()
                    # 位置
                    if sofa_type == 'sofa/left corner sofa' and origin_position[0] < -0.1:
                        origin_position[0] *= -1
                    elif sofa_type == 'sofa/right corner sofa' and origin_position[0] > 0.1:
                        origin_position[0] *= -1
                    elif abs(group_x_min_rug) > abs(group_x_max_rug) + 0.1 and origin_position[0] > 0.1:
                        origin_position[0] *= -1
                        origin_angle *= -1
                    elif abs(group_x_max_rug) > abs(group_x_min_rug) + 0.1 and origin_position[0] < -0.1:
                        origin_position[0] *= -1
                        origin_angle *= -1
                    object_x_min = group_offset[0] + origin_position[0] - object_width / 2
                    object_x_max = group_offset[0] + origin_position[0] + object_width / 2
                    object_z_min = group_offset[2] + origin_position[2] - object_depth / 2
                    object_z_max = group_offset[2] + origin_position[2] + object_depth / 2
                    x_offset_1, x_offset_2 = object_x_min - group_x_min_rug, group_x_max_rug - object_x_max
                    z_offset_1, z_offset_2 = object_z_min - group_z_min_rug, group_z_max_rug - object_z_max
                    x_scale, z_scale, x_offset, z_offset = 1, 1, 0, 0
                    # 横向
                    if not layout_complete:
                        pass
                    elif x_offset_1 >= 0 and x_offset_2 >= 0:
                        pass
                    elif x_offset_1 + x_offset_2 >= 0:
                        if x_offset_1 < 0:
                            x_offset = -x_offset_1
                        if x_offset_2 < 0:
                            x_offset = x_offset_2
                    else:
                        if abs(origin_angle) < 0.1 or abs(origin_angle - math.pi) < 0.1:
                            x_scale = (group_x_max_rug - group_x_min_rug) / (object_x_max - object_x_min)
                        else:
                            z_scale = (group_x_max_rug - group_x_min_rug) / (object_x_max - object_x_min)
                        x_offset = (group_x_min_rug + group_x_max_rug) / 2 - origin_position[0] - group_offset[0]
                    # 纵向
                    if not layout_complete:
                        pass
                    elif z_offset_1 >= 0 and z_offset_2 >= 0:
                        pass
                    elif z_offset_1 + z_offset_2 >= 0:
                        if z_offset_1 < 0:
                            z_offset = -z_offset_1
                        if z_offset_2 < 0:
                            z_offset = z_offset_2
                    else:
                        if abs(origin_angle) < 0.1 or abs(origin_angle - math.pi) < 0.1:
                            z_scale = (group_z_max_rug - group_z_min_rug) / (object_z_max - object_z_min)
                        else:
                            x_scale = (group_z_max_rug - group_z_min_rug) / (object_z_max - object_z_min)
                        z_offset = (group_z_min_rug + group_z_max_rug) / 2 - origin_position[2] - group_offset[2]
                    # 尺寸
                    object_add['size'] = object_one['size'][:]
                    object_add['scale'] = object_one['scale'][:]
                    object_add['scale'][0] *= x_scale
                    object_add['scale'][2] *= z_scale
                    # 位置
                    tmp_x = group_offset[0] + origin_position[0] + x_offset + 0.00
                    tmp_z = group_offset[2] + origin_position[2] + z_offset + UNIT_DEPTH_FLOOR_FRAME
                    add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                    add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                    add_y = 0
                    furniture_position = [group_position[0] + add_x, group_position[1] + add_y, group_position[2] + add_z]
                    object_add['position'] = furniture_position
                    # 朝向
                    furniture_angle = group_angle + origin_angle
                    furniture_rotation = [0, math.sin(furniture_angle / 2), 0, math.cos(furniture_angle / 2)]
                    object_add['rotation'] = furniture_rotation
                    group_one['obj_list'].append(object_add)
                # 调整家具
                else:
                    # 更新
                    object_add = object_one.copy()
                    if object_media_old == object_one:
                        object_media_new = object_add
                    # 尺寸
                    object_add['size'] = object_one['size'][:]
                    object_add['scale'] = object_one['scale'][:]
                    # 缩放1 缩放2
                    if fake_flag == 1 or fake_flag == 2:
                        object_add['fake_size'] = 1
                        if object_id in fake_dict:
                            fake_scale_offset = fake_dict[object_id]
                            if fake_scale_offset[0] == fake_scale_offset[1] == fake_scale_offset[2] == 1:
                                object_add['fake_size'] = 0
                            elif abs(abs(origin_angle) - math.pi / 2) < 0.1:
                                object_add['scale'][0] *= fake_scale_offset[2]
                                object_add['scale'][1] *= fake_scale_offset[1]
                                object_add['scale'][2] *= fake_scale_offset[0]
                            else:
                                object_add['scale'][0] *= fake_scale_offset[0]
                                object_add['scale'][1] *= fake_scale_offset[1]
                                object_add['scale'][2] *= fake_scale_offset[2]
                    # 缩放3
                    elif fake_flag == 3:
                        relate_id = object_one['relate']
                        if relate_id in fake_dict:
                            fake_scale_offset = fake_dict[relate_id]
                            object_add['scale'][0] *= fake_scale_offset[0]
                            object_add['scale'][1] *= fake_scale_offset[1]
                            object_add['scale'][2] *= fake_scale_offset[2]
                        if relate_id in zoom_dict:
                            if 'normal_position' in object_add:
                                normal_position = object_add['normal_position']
                                normal_position[0] *= fake_scale_offset[0]
                                normal_position[1] *= fake_scale_offset[1]
                                normal_position[2] *= fake_scale_offset[2]

                    # 位置
                    if sofa_type == 'sofa/left corner sofa' and origin_position[0] < -0.1:
                        if object_role in ['table']:
                            mov_z = origin_position[2] - (object_depth * 0.5 + group_size_min[2] * 0.5)
                            if mov_z < -0.1:
                                origin_position[0] *= -1
                                table_swap = True
                        elif object_role in ['side sofa']:
                            if side_sofa_paste >= 1:
                                dump_list.append(object_one)
                                continue
                    elif sofa_type == 'sofa/right corner sofa' and origin_position[0] > 0.1:
                        if object_role in ['table']:
                            mov_z = origin_position[2] - (object_depth * 0.5 + group_size_min[2] * 0.5)
                            if mov_z < -0.1:
                                origin_position[0] *= -1
                                table_swap = True
                        elif object_role in ['side sofa']:
                            if side_sofa_paste <= -1:
                                dump_list.append(object_one)
                                continue
                    elif sofa_type in SOFA_CORNER_TYPE_2:
                        if object_role in ['table']:
                            origin_position[0] = 0
                    # 对调
                    if table_swap and relate_role in ['table']:
                        origin_position[0] *= -1
                    # 靠边
                    if object_role in ['shower', 'bath', 'screen']:
                        origin_position, origin_angle = compute_furniture_aside(region_direct, object_add, group_size,
                                                                                group_offset, group_neighbor_base)
                    # 计算
                    object_add['position'] = object_one['position'][:]
                    object_add['rotation'] = object_one['rotation'][:]
                    offset_position = [0, 0, 0]
                    if 'offset_position' in object_one:
                        offset_position = object_one['offset_position']
                    tmp_x = group_offset[0] + origin_position[0] + offset_position[0] + 0.00
                    tmp_y = group_offset[1] + origin_position[1] + offset_position[1] + 0.00
                    tmp_z = group_offset[2] + origin_position[2] + offset_position[2] + UNIT_DEPTH_FLOOR_FRAME
                    # 前移
                    if object_role in ['side table', 'side plant', 'side lamp', 'accessory'] and window_flag == 2:
                        new_z = -group_size[2] / 2 + object_depth / 200 + UNIT_DEPTH_CURTAIN
                        if tmp_z < new_z:
                            tmp_z = new_z
                    if fake_flag == 1 or fake_flag == 2:
                        if object_id in fake_dict:
                            fake_scale_offset = fake_dict[object_id]
                            if fake_scale_offset[6] * origin_position[0] >= 0:
                                tmp_x += fake_scale_offset[3]
                                tmp_z += fake_scale_offset[5]
                    elif fake_flag == 3:
                        relate_id = object_one['relate']
                        if relate_id in fake_dict:
                            fake_scale_offset = fake_dict[relate_id]
                            if fake_scale_offset[6] * origin_position[0] >= 0:
                                tmp_x = group_offset[0] + origin_position[0] + fake_scale_offset[3] * fake_scale_offset[0]
                                tmp_z = group_offset[2] + origin_position[2] + fake_scale_offset[5] * fake_scale_offset[2]
                    # 上移
                    if object_role in ['accessory'] and 'light' in object_type:
                        if tmp_y + object_height > 2.0:
                            tmp_y = room_height - ceil_height - object_height
                    # 位置
                    add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                    add_y = tmp_y
                    add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                    if object_add['role'] in ['side plant', 'side lamp'] and add_y < object_lift_bot < 0.1:
                        add_y = object_lift_bot
                    furniture_position = [group_position[0] + add_x, group_position[1] + add_y, group_position[2] + add_z]

                    object_add['position'] = furniture_position
                    object_add['normal_position'] = origin_position[:]
                    # 朝向
                    furniture_angle = group_angle + origin_angle
                    furniture_rotation = [0, math.sin(furniture_angle / 2), 0, math.cos(furniture_angle / 2)]
                    object_add['rotation'] = furniture_rotation
                    object_add['normal_rotation'] = [0, math.sin(origin_angle / 2), 0, math.cos(origin_angle / 2)]
                    # 添加
                    group_one['obj_list'].append(object_add)
                    pass

                # 添加家具
                stay_list.append(object_one)
            # 遍历配件
            if group_type in GROUP_RULE_FUNCTIONAL:
                for object_one in group_one['obj_list']:
                    object_role, object_plat = '', ''
                    if 'role' in object_one:
                        object_role = object_one['role']
                    if 'relate' in object_one:
                        object_plat = object_one['relate']
                    if object_role not in ['part', 'accessory']:
                        continue
                    if len(object_plat) <= 0:
                        continue
                    object_pos, relate_pos = object_one['position'], []
                    for plat_one in group_one['obj_list']:
                        if not plat_one['id'] == object_plat:
                            continue
                        plat_pos, plat_ang = plat_one['position'], rot_to_ang(plat_one['rotation'])
                        plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
                        if group_type in ['Armoire', 'Cabinet']:
                            plat_size = [group_size[i] for i in range(3)]
                        dis, ang = compute_furniture_length(plat_pos[0], plat_pos[2], object_pos[0], object_pos[2])
                        offset_x, offset_z = dis * math.sin(ang - plat_ang), dis * math.cos(ang - plat_ang)
                        if abs(offset_x) <= plat_size[0] / 2 + 0.1 and abs(offset_z) <= plat_size[2] / 2 + 0.1:
                            relate_pos = plat_pos[:]
                            break
                    object_one['relate_position'] = relate_pos

            # 保持家具
            keep_todo, keep_used = [], []
            if 'layout_keep' in layout_info:
                for keep_one in layout_info['layout_keep']:
                    if keep_one['group'] == group_type:
                        keep_todo.append(keep_one)
            if 'seed_position' in group_one and 'seed_rotation' in group_one:
                pass
            elif 'keep_position' in group_one and 'keep_rotation' in group_one:
                obj_todo = group_one['obj_list']
                for obj_temp in obj_todo:
                    # 种子查找
                    keep_wait, keep_best = [], {}
                    for keep_temp in keep_todo:
                        if keep_temp['group'] == group_type and keep_temp['role'] == obj_temp['role']:
                            keep_wait.append(keep_temp)
                    # 种子查找
                    obj_pos = obj_temp['position']
                    for keep_temp in keep_wait:
                        if keep_temp in keep_used:
                            continue
                        if len(keep_best) <= 0:
                            keep_best = keep_temp
                            continue
                        temp_pos = keep_temp['position']
                        best_pos = keep_best['position']
                        temp_dis = compute_furniture_length(temp_pos[0], temp_pos[2], obj_pos[0], obj_pos[2])
                        best_dis = compute_furniture_length(best_pos[0], best_pos[2], obj_pos[0], obj_pos[2])
                        if temp_dis < best_dis:
                            keep_best = keep_temp
                    if len(keep_best) > 0:
                        # 饰品
                        obj_move = [keep_best['position'][i] - obj_temp['position'][i] for i in range(3)]
                        for acce_temp in obj_todo:
                            if 'relate' in acce_temp and acce_temp['relate'] == obj_temp['id']:
                                acce_temp['position'] = [acce_temp['position'][i] + obj_move[i] for i in range(3)]
                        # 更新
                        obj_temp['position'] = keep_best['position'][:]
                        obj_temp['rotation'] = keep_best['rotation'][:]
                        keep_used.append(keep_best)
                for keep_new in keep_todo:
                    if keep_new in keep_used:
                        continue
                    if len(obj_todo) > 0:
                        obj_new = obj_todo[-1].copy()
                        obj_new['size'] = keep_new['size'][:]
                        obj_new['scale'] = keep_new['scale'][:]
                        obj_new['position'] = keep_new['position'][:]
                        obj_new['rotation'] = keep_new['rotation'][:]
                        obj_new['role'] = keep_new['role']
                        obj_new['relate'] = ''
                        obj_new['relate_position'] = []
                        obj_todo.append(obj_new)
            # 计算尺寸
            if len(stay_list) > 0:
                compute_furniture_scope(group_one, stay_list, room_type)
            # 交换家具
            if len(side_table_copy) <= 0 and group_type in ['Bed']:
                resolve_furniture_swap(group_one, group_side)

        # 遍历分组 装饰信息
        for object_list in [object_wall, object_ceil, object_floor]:
            for object_one in object_list:
                if 'relate_group' not in object_one:
                    continue
                if 'relate' in object_one and len(object_one['relate']) > 0:
                    if 'relate_position' in object_one and len(object_one['relate_position']) > 0:
                        continue
                object_size = [object_one['size'][i] * object_one['scale'][i] / 100 for i in range(3)]
                object_pos, object_ang = object_one['position'], rot_to_ang(object_one['rotation'])
                relate_id, relate_role, relate_group = '', '', object_one['relate_group']
                relate_pos, relate_dis, relate_shift, relate_move = [], 2, [], [0, 0, 0]
                for group_one in layout_one['group']:
                    if not group_one['type'] == relate_group:
                        continue
                    for relate_one in group_one['obj_list']:
                        relate_role = relate_one['role']
                        if relate_role not in ['sofa', 'bed', 'table', 'side table', 'cabinet', 'armoire']:
                            continue
                        relate_pos, relate_ang = relate_one['position'], rot_to_ang(relate_one['rotation'])
                        relate_size = [abs(relate_one['size'][i] * relate_one['scale'][i]) / 100 for i in range(3)]
                        dis, ang = compute_furniture_length(relate_pos[0], relate_pos[2], object_pos[0], object_pos[2])
                        offset_x, offset_z = dis * math.sin(ang - relate_ang), dis * math.cos(ang - relate_ang)
                        relate_dis_new = abs(offset_x)
                        if object_list == object_floor:
                            relate_dis_new = abs(offset_x) - relate_size[0] / 2 - object_size[0] / 2
                        # 邻接
                        if relate_dis_new <= 0.2:
                            relate_id, relate_pos, relate_dis = relate_one['id'], relate_pos[:], relate_dis_new
                            relate_shift = [offset_x, object_pos[1], offset_z]
                            if 'swap_move' in group_one:
                                relate_move = group_one['swap_move']
                            break
                        # 最近
                        elif relate_dis_new < relate_dis:
                            relate_id, relate_pos, relate_dis = relate_one['id'], relate_pos[:], relate_dis_new
                            relate_shift = [offset_x, object_pos[1], offset_z]
                            if 'swap_move' in group_one:
                                if object_list == object_ceil:
                                    relate_move = group_one['swap_move']
                                elif object_list == object_wall and abs(offset_z + relate_size[2] / 2) < 0.1:
                                    relate_move = group_one['swap_move']
                    if not relate_id == '' and relate_dis_new < 1.0:
                        break
                if not relate_id == '' and relate_dis_new < 1.0:
                    object_one['relate'] = relate_id
                    object_one['relate_role'] = relate_role
                    object_one['relate_position'] = relate_pos
                    object_one['normal_position'] = relate_shift[:]
                    object_one['position'][0] += relate_move[0]
                    object_one['position'][1] += relate_move[1]
                    object_one['position'][2] += relate_move[2]

        # 种子信息
        layout_one['target_seed'], layout_one['target_style'], layout_one['target_scope'] = [], [], []
        # 种子风格
        style_old, style_mode = '', ''
        if 'style' in data_info:
            style_old, style_mode = data_info['style'], 'room'
        # 种子家具
        if 'layout_seed' in room_layout_info:
            for object_idx, object_one in enumerate(room_layout_info['layout_seed']):
                object_id, object_type, object_style = object_one['id'], object_one['type'], object_one['style']
                entity_id = ''
                if 'entityId' in object_one:
                    entity_id = object_one['entityId']
                target_one = {
                    'id': object_id,
                    'type': object_type,
                    'entityId': entity_id
                }
                layout_one['target_seed'].append(target_one)
                if object_idx == 0 and not object_style == '':
                    style_old, style_mode = object_style, ''
        # 种子风格
        if len(layout_one['target_seed']) <= 0:
            style_mode = 'room'
        style_new, style_list, style_id_list = get_furniture_style_refer(style_old, style_mode)
        layout_one['target_style'] = style_id_list
        # 种子分配
        for group_one in layout_one['group']:
            group_type = group_one['type']
            if group_type not in GROUP_RULE_FUNCTIONAL:
                continue
            if 'obj_list' not in group_one:
                continue
            # 遍历家具
            for object_idx, object_one in enumerate(group_one['obj_list']):
                object_id, object_role = object_one['id'], object_one['role']
                seed_find, keep_find = False, False
                for seed_one in seed_list:
                    seed_id, seed_group, seed_role = seed_one['id'], seed_one['group'], seed_one['role']
                    if seed_group == group_type and seed_role == object_role:
                        seed_dict[object_id] = seed_one
                        seed_find = True
                        break
                if seed_find:
                    continue
                for seed_one in keep_list:
                    seed_id, seed_group, seed_role = seed_one['id'], seed_one['group'], seed_one['role']
                    if seed_group == group_type and seed_role == object_role:
                        keep_dict[object_id] = seed_one
                        keep_find = True
                        break
                    elif seed_role == object_role == 'side table':
                        keep_dict[object_id] = seed_one
                        keep_find = True
                        break
                if keep_find:
                    continue

        # 推荐家具 尺寸信息
        target_list_old = []
        for group_one in layout_one['group']:
            group_type = group_one['type']
            if 'obj_list' not in group_one:
                continue
            object_set = group_one['obj_list']
            # 遍历家具
            for object_idx, object_one in enumerate(object_set):
                object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
                object_rely, object_cate = '', ''
                if 'relate' in group_one:
                    object_rely = group_one['relate']
                # 查找
                find_idx = -1
                for target_idx, target_one in enumerate(target_list_old):
                    if target_one['id'] == object_id:
                        find_idx = target_idx
                        if target_one['size_cur'][0] < object_one['size_cur'][0]:
                            # 尺寸
                            if 'size_cur' in object_one:
                                object_size = object_one['size_cur']
                            else:
                                object_size = [abs(object_one['size'][i] * object_one['scale'][i]) for i in range(3)]
                            # 类目
                            cate_new = ''
                            cate_set_1, cate_set_2, cate_id_1, cate_id_2 = \
                                get_furniture_category_by_role(group_type, object_role, object_type, object_rely, room_type)
                            if len(cate_id_2) >= 1:
                                cate_new = cate_id_2[0]
                            elif len(cate_id_1) >= 1:
                                cate_new = cate_id_1[0]
                            else:
                                type_id, style_id, category_id = get_furniture_data_refer_id(object_id)
                                cate_new = category_id
                            # 更新
                            target_one['size_min'] = object_one['size_min'][:]
                            target_one['size_max'] = object_one['size_max'][:]
                            target_one['size_cur'] = object_one['size_cur'][:]
                            target_one['type'] = object_one['type']
                            target_one['role'] = object_one['role']
                            target_one['cate_id'] = cate_new
                        break
                # 更新
                if find_idx < 0:
                    # 尺寸
                    if 'size_cur' in object_one:
                        object_size = object_one['size_cur']
                    else:
                        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) for i in range(3)]
                    # 类目
                    cate_new = ''
                    if object_role in ['tv', 'electronics', 'screen', 'accessory', 'plants', '']:
                        continue
                    else:
                        cate_set_1, cate_set_2, cate_id_1, cate_id_2 = \
                            get_furniture_category_by_role(group_type, object_role, object_type, object_rely, room_type)
                        if len(cate_id_2) >= 1:
                            cate_new = cate_id_2[0]
                        elif len(cate_id_1) >= 1:
                            cate_new = cate_id_1[0]
                        else:
                            type_id, style_id, category_id = get_furniture_data_refer_id(object_id)
                            cate_new = category_id
                    # 添加
                    target_add = {
                        'id': object_id,
                        'type': object_type,
                        'role': object_role,
                        'size_min': object_one['size_min'][:],
                        'size_max': object_one['size_max'][:],
                        'size_cur': object_one['size_cur'][:],
                        'cate_id': cate_new,
                        'group': group_type
                    }
                    target_list_old.append(target_add)
        # 排序家具
        target_list_sub1, target_list_sub2, target_list_sub3 = [], [], []
        for target_one in target_list_old:
            target_id = target_one['id']
            if target_id in seed_dict:
                continue
            if target_id in keep_dict:
                keep_one = keep_dict[target_id]
                if 'role' in target_one and 'role' in keep_one:
                    if target_one['role'] == keep_one['role']:
                        continue
                else:
                    continue
            if 'fake_id' in target_one and target_one['fake_id'].startswith('link'):
                continue
            target_role = target_one['role']
            if target_role in ['sofa', 'bed', 'table', 'work', 'armoire']:
                target_list_sub1.append(target_one)
            elif target_role in ['', 'tv', 'rug', 'accessory']:
                target_list_sub3.append(target_one)
            else:
                target_list_sub2.append(target_one)
        target_list_new = []
        for target_one in target_list_sub1:
            target_list_new.append(target_one)
        for target_one in target_list_sub2:
            target_list_new.append(target_one)
        for target_one in target_list_sub3:
            target_list_new.append(target_one)
        layout_one['target_scope'] = target_list_new
        propose_one = {
            'id': data_info['id'],
            'type': data_info['type'],
            'area': data_info['area'],
            'target_seed': layout_one['target_seed'],
            'target_style': layout_one['target_style'],
            'target_scope': layout_one['target_scope']
        }
        propose_info.append(propose_one)
    # 返回信息
    return propose_info


# 调整家具位置
def house_rect_adjust(house_layout_info, house_propose_info, adjust_mode=0):
    layout_info, propose_info = house_layout_info, house_propose_info
    # 遍历房间
    for room_id, room_layout_info in layout_info.items():
        if room_id not in propose_info:
            continue
        room_propose_info = propose_info[room_id]
        room_rect_adjust(room_layout_info, room_propose_info, adjust_mode)


# 调整家具位置
def room_rect_adjust(room_layout_info, room_propose_info, adjust_mode=0):
    layout_info, propose_info = room_layout_info, room_propose_info
    if len(layout_info) <= 0:
        return
    room_type = room_layout_info['room_type']
    room_height, ceil_height = UNIT_HEIGHT_WALL, UNIT_HEIGHT_CEIL
    if 'room_height' in layout_info:
        room_height = layout_info['room_height']
    if 'ceil_height' in layout_info:
        ceil_height = layout_info['ceil_height']
    # 种子信息
    seed_dict = {}
    if 'layout_seed' in layout_info:
        for seed_one in layout_info['layout_seed']:
            seed_id = seed_one['id']
            entity_id = ''
            if 'entityId' in seed_one:
                entity_id = seed_one['entityId']
            if len(seed_id) > 0:
                seed_dict[seed_id] = seed_one
            if len(entity_id) > 0:
                seed_dict[entity_id] = seed_one
    if 'layout_keep' in layout_info:
        for seed_one in layout_info['layout_keep']:
            seed_id = seed_one['id']
            entity_id = ''
            if 'entityId' in seed_one:
                entity_id = seed_one['entityId']
            if len(seed_id) > 0:
                seed_dict[seed_id] = seed_one
            if len(entity_id) > 0:
                seed_dict[entity_id] = seed_one

    # 选品信息
    layout_scheme = layout_info['layout_scheme']
    for layout_idx, layout_one in enumerate(layout_scheme):
        # 调试打印
        if layout_info['room_type'] in ['LivingDiningRoom'] and layout_idx >= 0 and False:
            print('adjust room:', layout_info['room_type'], 'debug', layout_idx)
        # 硬装信息
        material_one = {}
        if 'material' in layout_one:
            material_one = layout_one['material']
        if 'self_transfer' in material_one and material_one['self_transfer']:
            if 'customized_ceiling' in material_one and len(material_one['customized_ceiling']) > 0:
                ceiling_one = material_one['customized_ceiling'][0]
                if 'size' in ceiling_one and len(ceiling_one['size']) >= 3:
                    if 'scale' in ceiling_one and len(ceiling_one['scale']) >= 3:
                        ceil_size = [abs(ceiling_one['size'][i] * ceiling_one['scale'][i]) / 100 for i in range(3)]
                        ceil_height = min(max(ceil_size[1], 0.05), 0.50)
        # 推荐方案
        target_furniture_scope = []
        if 0 <= layout_idx < len(room_propose_info):
            room_propose_one = room_propose_info[layout_idx]
            if 'target_scope' in room_propose_one:
                target_furniture_scope = room_propose_one['target_scope']
        # 替换方案
        target_furniture_list, target_furniture_size = [], {}
        if 0 <= layout_idx < len(propose_info):
            propose_one = propose_info[layout_idx]
            if 'target_furniture' in propose_one:
                target_furniture_list = propose_one['target_furniture']
            if 'target_furniture_size' in propose_one:
                target_furniture_size = propose_one['target_furniture_size']
        group_original = []
        layout_one['group_propose'] = []
        # 模板方案
        target_furniture_list.insert(0, {})
        # 调整方案
        replace_size = target_furniture_size
        for replace_idx, replace_dict in enumerate(target_furniture_list):
            if layout_info['room_type'] in ['MasterBedroom'] and layout_idx >= 0 and replace_idx >= 1 and False:
                print('replace room:', layout_info['room_type'], 'debug', layout_idx)
            group_list_src = layout_one['group']
            if adjust_mode == 1 and 'group_generated' in layout_one:
                group_list_src = layout_one['group_generated']
            # 更新方案
            group_list_add = group_rect_adjust(group_list_src, replace_dict, replace_size, seed_dict,
                                               room_type, room_height, ceil_height)
            # 碰撞检测
            group_rect_dodge(group_list_add)
            # 添加方案
            if replace_idx == 0:
                for group_one in group_list_add:
                    group_original.append(group_one)
            else:
                layout_one['group_propose'].append(group_list_add)
        # 模板方案
        if adjust_mode == 1 and 'group_generated' in layout_one:
            layout_one['group_generated'] = group_original
        else:
            layout_one['group'] = group_original


# 调整家具位置
def group_rect_adjust(group_list_src, replace_dict, replace_size, seed_dict,
                      room_type='', room_height=UNIT_HEIGHT_WALL, ceil_height=UNIT_HEIGHT_CEIL):
    group_list_add = []
    # 更新家具
    object_dict_new, relate_dict_new, corner_dict_new = {}, {}, {}
    for group_old in group_list_src:
        # 原有信息
        group_type, group_angle = group_old['type'], rot_to_ang(group_old['rotation'])
        group_width, group_depth = group_old['size'][0], group_old['size'][2]
        seed_list = []
        if 'seed_list' in group_old:
            for seed_id in group_old['seed_list']:
                seed_list.append(seed_id)
        if 'keep_list' in group_old:
            for seed_id in group_old['keep_list']:
                seed_list.append(seed_id)
        main_role = ''
        if group_type in GROUP_RULE_FUNCTIONAL:
            main_role = GROUP_RULE_FUNCTIONAL[group_type]['main']
            if group_type == 'Media':
                main_role = 'table'
            if group_type in ['Rest'] and len(group_old['obj_list']) == 1:
                obj_main = group_old['obj_list'][0]
                if 'role' in obj_main and len(obj_main['role']) > 0:
                    main_role = obj_main['role']
                pass
        vertical_flag, center_flag, corner_flag = 0, 0, 0
        if 'vertical' in group_old:
            vertical_flag = group_old['vertical']
        if 'center' in group_old:
            center_flag = group_old['center']
        region_direct, region_beside = 0, [1, 1]
        if 'region_direct' in group_old:
            region_direct = group_old['region_direct']
        if 'region_beside' in group_old:
            region_beside = group_old['region_beside']
        # 复制信息
        group_new = group_old.copy()
        group_new['obj_list'] = []

        # 替换处理
        for object_one in group_old['obj_list']:
            object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
            object_replace = False
            if object_id in replace_dict:
                object_replace = True
            if len(seed_list) > 0 and not object_replace:
                # 种子查找
                seed_wait, seed_best = [], {}
                if 'entityId' in object_one:
                    entity_id = object_one['entityId']
                    if entity_id in seed_dict:
                        seed_one = seed_dict[entity_id]
                        seed_group, seed_role = seed_one['group'], seed_one['role']
                        if seed_group == group_type and seed_role == object_role:
                            seed_wait.append(seed_one)
                if len(seed_wait) <= 0:
                    for seed_id in seed_list:
                        if seed_id in seed_dict:
                            seed_one = seed_dict[seed_id]
                            seed_group, seed_role = seed_one['group'], seed_one['role']
                            if seed_group == group_type and seed_role == object_role:
                                seed_wait.append(seed_one)
                # 种子查找
                obj_pos = object_one['position']
                for seed_temp in seed_wait:
                    if len(seed_best) <= 0:
                        seed_best = seed_temp
                        continue
                    temp_pos = seed_temp['position']
                    best_pos = seed_best['position']
                    temp_dis = compute_furniture_length(temp_pos[0], temp_pos[2], obj_pos[0], obj_pos[2])
                    best_dis = compute_furniture_length(best_pos[0], best_pos[2], obj_pos[0], obj_pos[2])
                    if temp_dis < best_dis:
                        seed_best = seed_temp
                if len(seed_best) > 0:
                    seed_size, seed_scale = seed_best['size'], seed_best['scale']
                    replace_id = seed_best['id']
                    replace_dict[object_id] = replace_id
                    replace_size[replace_id] = seed_size[:]
        # 缩放处理
        size_main, size_rest = [1, 1, 1], [0, 0, 0, 0]
        if 'size_rest' in group_old:
            size_rest = group_old['size_rest']
        for object_one in group_old['obj_list']:
            object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
            if object_role == main_role:
                size_main = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if object_role in ['accessory', '']:
                continue
            # 家具替换
            replace_id = object_id
            seed_size, seed_scale = object_one['size'], object_one['scale']
            if object_id in replace_dict:
                replace_id = replace_dict[object_id]
                if replace_id not in replace_size:
                    replace_id = object_id
                if replace_id in seed_dict:
                    seed_one = seed_dict[replace_id]
                    seed_size, seed_scale = seed_one['size'], seed_one['scale']
                else:
                    seed_scale = [1, 1, 1]
                seed_height = abs(seed_size[1] * seed_scale[1]) / 100
                if replace_id == object_id:
                    if replace_id in seed_dict:
                        seed_one = seed_dict[replace_id]
                        seed_one['scale'] = object_one['scale'][:]
                if seed_height > room_height - ceil_height:
                    seed_scale[1] = abs(room_height - ceil_height) / seed_height
                elif replace_id in seed_dict:
                    pass
                elif UNIT_HEIGHT_ARMOIRE_MID - 0.05 < seed_height < room_height - ceil_height - 0.05 \
                        and object_role in ['armoire', 'cabinet']:
                    seed_scale[1] = abs(room_height - ceil_height) / seed_height
            # 家具缩放
            if replace_id == object_id or replace_id == '':
                pass
            else:
                size_old = object_one['size'][:]
                size_max = [size_old[i] * 2.0 for i in range(3)]
                size_cur = [size_old[i] * 1.0 for i in range(3)]
                if 'size_max' in object_one:
                    size_max = object_one['size_max']
                if 'size_cur' in object_one:
                    size_cur = object_one['size_cur']
                type_new, style_new = object_one['type'], object_one['style']
                if replace_id in seed_dict:
                    seed_one = seed_dict[replace_id]
                    type_new, style_new, size_new = seed_one['type'], seed_one['style'], seed_one['size'][:]
                elif have_furniture_data(replace_id):
                    type_new, style_new, size_new = get_furniture_data(replace_id)
                elif 'size_cur' in object_one:
                    size_new = object_one['size_cur'][:]
                if replace_id in replace_size:
                    size_new = replace_size[replace_id]
                    # 推荐尺寸纠正
                    if size_new[0] < 0:
                        size_new[0] = object_one['size'][0]
                    if size_new[1] < 0:
                        size_new[1] = object_one['size'][1]
                    if size_new[2] < 0:
                        size_new[2] = object_one['size'][2]
                # 缩放纠正
                scale_new = [1, 1, 1]
                if replace_id in seed_dict:
                    scale_new = seed_scale[:]
                elif object_role == 'rug':
                    scale_new = [size_cur[0] / size_new[0], size_cur[1] / size_new[1],
                                 size_cur[2] / size_new[2]]
                elif group_type == 'Wall':
                    scale_new = [size_cur[0] / size_new[0], size_cur[1] / size_new[1],
                                 size_cur[2] / size_new[2]]
                    scale_min = min(scale_new[0], scale_new[1])
                    scale_new = [scale_min, scale_min, scale_min]
                # 选品信息
                object_new = object_one.copy()
                object_new['id'] = replace_id
                object_new['type'], object_new['style'], object_new['size'] = type_new, style_new, size_new[:]
                object_new['scale'] = scale_new[:]
                if replace_id not in object_dict_new:
                    object_dict_new[replace_id] = object_new
                elif not object_dict_new[replace_id]['role'] == object_role:
                    replace_id_new = replace_id + '_' + object_role
                    object_dict_new[replace_id_new] = object_new
                elif object_dict_new[replace_id]['scale'][0] > scale_new[0]:
                    object_dict_new[replace_id] = object_new

        # 偏移信息
        ratio_max_object, ratio_max_group, ratio_max_space = [0.1, 0.1, 0.1], [0.1, 0.1, 0.1], [0.1, 0.1, 0.1]
        offset_main_x, offset_main_z, offset_main_max = 0, 0, False
        for object_one in group_old['obj_list']:
            # 基本信息
            object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
            object_size_old = [abs(object_one['size'][i] * object_one['scale'][i] / 100) for i in range(3)]
            object_size_new = object_size_old[:]
            replace_id = object_id
            ratio_new_object, ratio_new_group, ratio_new_space = [1, 1, 1], [1, 1, 1], [1, 1, 1]
            if object_id == group_old['obj_main'] and object_role in ['lamp']:
                object_role = main_role
            group_size_old, group_size_max = group_old['size'][:], group_old['size'][:]
            if 'neighbor_base' in group_old:
                group_neighbor = group_old['neighbor_base'][:]
                group_size_max[0] += group_neighbor[1]
                group_size_max[0] += group_neighbor[3]
                group_size_max[2] += group_neighbor[0]
                group_size_max[2] += group_neighbor[2]

            # 替换信息
            if object_id in replace_dict:
                replace_id = replace_dict[object_id]
                if replace_id not in replace_size:
                    replace_id = object_id
            if replace_id in object_dict_new:
                object_new = object_dict_new[replace_id]
                if not object_role == object_dict_new[replace_id]['role']:
                    replace_id_new = replace_id + '_' + object_role
                    if replace_id_new in object_dict_new:
                        object_new = object_dict_new[replace_id_new]
                size_new, scale_new = object_new['size'], object_new['scale']
                object_size_new = [abs(size_new[i] * scale_new[i] / 100) for i in range(3)]
                ratio_new_object = [object_size_new[i] / object_size_old[i] for i in range(3)]
            if object_role == main_role and not object_role == '':
                ratio_new_group = [object_size_new[i] / group_size_old[i] for i in range(3)]
                ratio_new_space = [object_size_new[i] / group_size_max[i] for i in range(3)]

            # 家具偏移 主要家具
            if group_type in GROUP_RULE_FUNCTIONAL and object_role == main_role:
                # 家具比例
                for i in range(3):
                    ratio_max_object[i] = max(ratio_new_object[i], ratio_max_object[i])
                    ratio_max_group[i] = max(ratio_new_group[i], ratio_max_group[i])
                    ratio_max_space[i] = max(ratio_new_space[i], ratio_max_space[i])
                # 餐桌偏移
                if group_type in ['Dining']:
                    # 横向
                    if vertical_flag == 0 and ratio_max_object[0] > 1:
                        if region_direct >= 1:
                            offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                        elif region_direct <= -1:
                            offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                    elif vertical_flag == 1 and ratio_max_object[2] > 1:
                        if region_direct >= 1:
                            offset_main_z = size_main[2] * (1 - ratio_max_object[2]) / 2
                        elif region_direct <= -1:
                            offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                        elif region_beside[0] > 2 > region_beside[1]:
                            offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                        elif region_beside[1] > 2 > region_beside[0]:
                            offset_main_z = size_main[2] * (1 - ratio_max_object[2]) / 2
                    # 纵向
                    if vertical_flag == 0 and ratio_max_object[2] > 1:
                        offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                        if center_flag >= 1 and ratio_max_object[2] > 1.5:
                            offset_main_z = 0
                    elif vertical_flag == 1 and ratio_max_object[0] > 1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                    # 居中
                    if center_flag == 1 and region_direct == 0:
                        if vertical_flag == 0 and ratio_max_group[0] < 1:
                            offset_main_x = 0
                            offset_main_z = 0
                        elif vertical_flag == 1 and ratio_max_group[2] < 1:
                            offset_main_x = 0
                            offset_main_z = 0
                # 电视偏移
                elif group_type in ['Media']:
                    # 横向 靠右
                    if region_direct >= 1 and ratio_max_object[0] >= 1:
                        offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                    # 横向 靠左
                    elif region_direct <= -1 and ratio_max_object[0] >= 1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                    # 纵向
                    offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                # 书桌偏移
                elif group_type in ['Work', 'Rest']:
                    # 横向
                    if region_direct >= 1:
                        offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                        if ratio_max_group[0] >= max(1, ratio_max_object[0]):
                            offset_main_x = group_width * (1 - ratio_max_group[0]) / 2
                    elif region_direct <= -1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                        if ratio_max_group[0] >= max(1, ratio_max_object[0]):
                            offset_main_x = group_width * (ratio_max_group[0] - 1) / 2
                    # 纵向
                    if center_flag == 1:
                        offset_main_z = 0
                        if ratio_max_object[2] > 1:
                            offset_main_z = size_main[2] * (1 - ratio_max_object[2]) / 2
                    elif ratio_max_object[2] > 1:
                        offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                    else:
                        offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                # 柜体偏移
                elif group_type in ['Armoire', 'Cabinet', 'Appliance']:
                    # 横向
                    if region_direct >= 1:
                        offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                        if ratio_max_group[0] >= max(1, ratio_max_object[0]):
                            offset_main_x = group_width * (1 - ratio_max_group[0]) / 2
                    elif region_direct <= -1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                        if ratio_max_group[0] >= max(1, ratio_max_object[0]):
                            offset_main_x = group_width * (ratio_max_group[0] - 1) / 2
                    # 纵向
                    offset_main_z += size_main[2] * (ratio_max_object[2] - 1) / 2
                # 正对偏移
                else:
                    # 横向 靠右
                    if region_direct >= 1 and ratio_max_object[0] >= 1:
                        offset_main_x = size_main[0] * (1 - ratio_max_object[0]) / 2
                    # 横向 靠左
                    elif region_direct <= -1 and ratio_max_object[0] >= 1:
                        offset_main_x = size_main[0] * (ratio_max_object[0] - 1) / 2
                    # 纵向
                    offset_main_z = size_main[2] * (ratio_max_object[2] - 1) / 2
                # 过大偏移
                if group_type in ['Meeting', 'Bed', 'Dining']:
                    offset_max_x = group_old['size'][0] / 2 - object_size_new[0] / 2 - group_old['offset'][0]
                    offset_min_x = -group_old['size'][0] / 2 + object_size_new[0] / 2 - group_old['offset'][0]
                    offset_max_z = group_old['size'][2] / 2 - object_size_new[2] / 2 - group_old['offset'][2]
                    offset_min_z = -group_old['size'][2] / 2 + object_size_new[2] / 2 - group_old['offset'][2]
                    if group_type == 'Dining':
                        if offset_main_x > offset_max_x or offset_main_x < offset_min_x \
                                and ratio_max_group[0] <= 1:
                            # offset_main_x = -group_old['offset'][0]
                            offset_main_max = True
                        if offset_main_z > offset_max_z or offset_main_z < offset_min_z \
                                and ratio_max_group[2] <= 1:
                            offset_main_max = True
                    elif size_rest[1] + size_rest[3] >= 0.1:
                        if offset_main_x > offset_max_x > 0.1 or offset_main_x < offset_min_x < -0.1:
                            offset_main_x = -group_old['offset'][0]
                            offset_main_max = True
                        if offset_max_x <= 0.1 and offset_min_x >= -0.1:
                            offset_main_x = -group_old['offset'][0]
                            offset_main_max = True
                # 叠加偏移
                elif group_type in ['Armoire', 'Cabinet', 'Work', 'Rest']:
                    group_relate = ''
                    if 'relate' in group_old:
                        group_relate = group_old['relate']
                    if group_relate == object_id:
                        # 横向
                        if region_direct >= 1:
                            offset_main_x = size_main[0] * (1 - ratio_max_object[0]) * 1.5
                            if ratio_max_group[0] >= 1:
                                offset_main_x = group_width * (1 - ratio_max_group[0]) * 1.5
                        elif region_direct <= -1:
                            offset_main_x = size_main[0] * (ratio_max_object[0] - 1) * 1.5
                            if ratio_max_group[0] >= 1:
                                offset_main_x = group_width * (ratio_max_group[0] - 1) * 1.5
                # 卫浴偏移
                elif group_type in ['Bath']:
                    offset_main_x = 0
                # 周边变化
                if 'neighbor_more' in group_new:
                    neighbor_more = group_new['neighbor_more']
                    if offset_main_z * 2 > 0:
                        neighbor_more[2] = max(neighbor_more[2] - offset_main_z * 2, 0)
                    else:
                        neighbor_more[2] = min(neighbor_more[2] - offset_main_z * 2, 3)
                    if ratio_max_object[0] > 1.0:
                        neighbor_more[1] = max(neighbor_more[1] - abs(offset_main_x), 0)
                        neighbor_more[3] = max(neighbor_more[3] - abs(offset_main_x), 0)
            # 家具偏移 次要家具
            if group_type in ['Meeting'] and object_role == 'table' and not offset_main_max:
                if object_size_new[0] > size_main[0]:
                    ratio_new_main = [object_size_new[i] / size_main[i] for i in range(3)]
                    if ratio_new_main[0] > ratio_max_object[0]:
                        ratio_max_object[0] = ratio_new_main[0]
                break
            elif group_type in ['Dining'] and object_role == 'chair' and not offset_main_max:
                # 横向
                if region_direct >= 1 and ratio_new_object[0] > 1:
                    offset_main_x = size_main[0] * (1 - ratio_new_object[0]) / 2
                elif region_direct <= -1 and ratio_new_object[0] > 1:
                    offset_main_x = size_main[0] * (ratio_new_object[0] - 1) / 2
                break
            elif group_type in ['Rest'] and object_role == 'chair' and not offset_main_max:
                # 横向
                if region_direct >= 1 and ratio_new_object[0] > 1:
                    offset_main_x = size_main[0] * (1 - ratio_new_object[0]) / 2
                elif region_direct <= -1 and ratio_new_object[0] > 1:
                    offset_main_x = size_main[0] * (ratio_new_object[0] - 1) / 2
                break
            # 家具偏移 装饰物品
            if group_type in GROUP_RULE_FUNCTIONAL and object_role in ['accessory', '']:
                break
        # 空余信息
        width_rest = [0, 0, 0, 0]
        if 'size_rest' in group_old:
            width_rest = group_old['size_rest'][:]
        if 'neighbor_more' in group_old:
            group_neighbor = group_old['neighbor_more']
            width_rest[1] += group_neighbor[1]
            width_rest[3] += group_neighbor[3]
            if group_type in ['Dining', 'Work', 'Rest']:
                width_rest[0] += group_neighbor[0]
                width_rest[2] += group_neighbor[2]
        elif 'neighbor_base' in group_old:
            group_neighbor = group_old['neighbor_base']
            width_rest[1] += group_neighbor[1]
            width_rest[3] += group_neighbor[3]
            if group_type in ['Dining', 'Work', 'Rest']:
                width_rest[0] += group_neighbor[0]
                width_rest[2] += group_neighbor[2]
        else:
            group_neighbor = [1.0, 1.0, 1.0, 1.0]
            width_rest[1] += group_neighbor[1]
            width_rest[3] += group_neighbor[3]
            if group_type in ['Dining', 'Work', 'Rest']:
                width_rest[0] += group_neighbor[0]
                width_rest[2] += group_neighbor[2]
        # 水平空余
        if 'relate' in group_old and not group_old['relate'] == '':
            if 'neighbor_base' in group_old:
                group_neighbor = group_old['neighbor_base']
                if group_neighbor[1] > 0 and offset_main_x > 0:
                    width_rest[1] += offset_main_x
                    width_rest[3] = 0
                elif group_neighbor[3] > 0 and offset_main_x < 0:
                    width_rest[1] = 0
                    width_rest[3] -= offset_main_x
                else:
                    width_rest[1] = 0
                    width_rest[3] = 0
        elif region_direct == 0 and group_type in GROUP_RULE_FUNCTIONAL:
            if offset_main_x < 0:
                width_rest[1] += offset_main_x
                width_rest[3] -= offset_main_x
            else:
                width_rest[1] += offset_main_x
                width_rest[3] -= offset_main_x
            width_rest[1] += size_main[0] * (1 - ratio_max_object[0]) / 2
            width_rest[3] += size_main[0] * (1 - ratio_max_object[0]) / 2
        # 竖直空余
        if offset_main_z < 0:
            width_rest[0] += offset_main_z
            width_rest[2] -= offset_main_z
        else:
            width_rest[0] += offset_main_z
            width_rest[2] -= offset_main_z
        width_rest[0] += size_main[2] * (1 - ratio_max_object[2]) / 2
        width_rest[2] += size_main[2] * (1 - ratio_max_object[2]) / 2

        # 主要信息
        object_id_main = ''
        object_main_old = {}
        object_type_main_old, object_type_main_new = '', ''
        object_size_main_old, object_size_main_new, object_size_main = [1, 1, 1], [1, 1, 1], [1, 1, 1]
        object_position_main, object_rotation_main = [0, 0, 0], [0, 0, 0, 1]
        object_round_main = False
        object_dump_dict = {}
        # 更新处理
        object_list_old, object_seed_used = [], {}
        for object_idx, object_one in enumerate(group_old['obj_list']):
            if object_one['role'] == 'table' and group_type == 'Media':
                object_list_old.insert(0, object_one)
            else:
                object_list_old.append(object_one)
        for object_idx, object_one in enumerate(object_list_old):
            # 基本信息
            object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
            if have_furniture_data_key(object_id, 'category_id'):
                type_id, style_id, cate_id = get_furniture_data_refer_id(object_id, '', False)
                object_one['category'] = cate_id
            else:
                object_one['category'] = ''
            object_position = object_one['position']
            if object_role == main_role:
                object_main_old = object_one
            # 替换信息
            replace_id = object_id
            if object_id in replace_dict:
                replace_id = replace_dict[object_id]
            if replace_id == '':
                continue
            # 复制信息
            entity_id = ''
            if 'entityId' in object_one:
                entity_id = object_one['entityId']
            object_new = copy_object(object_one)
            object_new['entityId'] = entity_id
            object_turn = get_furniture_turn(replace_id)
            if abs(object_turn) > 0:
                object_new['turn'] = object_turn
            # 尺寸信息
            object_size_old = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            if min(abs(object_size_old[0]), abs(object_size_old[2])) < 0.001:
                continue
            object_size_new = object_size_old[:]
            object_xz_old = object_size_old[0] / object_size_old[2]
            if replace_id in object_dict_new:
                object_tmp = object_dict_new[replace_id]
                if not object_tmp['role'] == object_role:
                    replace_id_new = replace_id + '_' + object_role
                    if replace_id_new in object_dict_new:
                        object_tmp = object_dict_new[replace_id_new]
                object_new['id'] = object_tmp['id']
                object_new['type'] = object_tmp['type']
                object_new['style'] = object_tmp['style']
                object_new['size'] = object_tmp['size'][:]
                object_new['scale'] = object_tmp['scale'][:]
                if object_new['scale'][0] < 0.99 or object_new['scale'][2] < 0.99:
                    if object_new['role'] not in ['', 'rug', 'accessory']:
                        object_new['fake_size'] = 1
                elif 'fake_size' in object_new:
                    object_new['fake_size'] = 0
            if replace_id in seed_dict:
                seed_tmp = seed_dict[replace_id]
                seed_entity = ''
                if entity_id in seed_dict:
                    seed_tmp = seed_dict[entity_id]
                    if not seed_tmp['id'] == replace_id:
                        seed_tmp = seed_dict[replace_id]
                if 'entityId' in seed_tmp:
                    seed_entity = seed_tmp['entityId']
                object_new['type'] = seed_tmp['type']
                object_new['style'] = seed_tmp['style']
                object_new['size'] = seed_tmp['size'][:]
                object_new['scale'] = seed_tmp['scale'][:]
                object_new['entityId'] = seed_entity
            # 更新信息
            object_size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
            object_xz_new = object_size_new[0] / object_size_new[2]
            # 功能家具
            if group_type in GROUP_RULE_FUNCTIONAL:
                x2, z2 = object_one['position'][0], object_one['position'][2]
                flag_left, flag_back = 0, 0
                if len(object_main_old) > 0:
                    x1, z1 = object_main_old['position'][0], object_main_old['position'][2]
                    flag_left, flag_back = \
                        compute_furniture_locate(x1, z1, x2, z2, group_angle, group_width, group_depth, group_depth * 0.1)
                # 丢弃家具 主要
                if object_role in ['tv'] and size_main[1] * (ratio_max_object[1] - 1) > 0.2:
                    object_dump_dict[object_id] = 1
                    continue
                if object_role == main_role and replace_id in seed_dict:
                    ratio_max_limit_x, ratio_max_limit_z = 1.20, 1.20
                    if group_type in ['Bed']:
                        ratio_max_limit_x, ratio_max_limit_z = 1.40, 1.40
                    elif group_type in ['Media']:
                        ratio_max_limit_x, ratio_max_limit_z = 1.40, 5.00
                    elif group_type in ['Dining', 'Work']:
                        ratio_max_limit_x, ratio_max_limit_z = 1.40, 1.40
                    elif group_type in ['Armoire', 'Cabinet']:
                        ratio_max_limit_x, ratio_max_limit_z = 1.20, 1.40
                    if ratio_max_space[0] > ratio_max_limit_x or ratio_max_space[2] > ratio_max_limit_z:
                        object_dump_dict[object_id] = 1
                        object_id_main = object_id
                        offset_main_x, offset_main_z = 0, 0
                        ratio_max_object = [1, 1, 1]
                        continue
                    elif ratio_max_space[0] > 1.0 and object_size_new[0] > 3:
                        scale_rat = 1
                        if object_role in ['sofa', 'bed'] and object_size_new[0] > 5:
                            scale_rat = max(group_size_max[0], 3) / object_size_new[0]
                        elif object_role in ['table'] and object_size_new[0] > 4:
                            scale_rat = max(group_size_max[0], 3) / object_size_new[0]
                        object_new['scale'][0] *= scale_rat
                        object_new['scale'][1] *= scale_rat
                        object_new['scale'][2] *= scale_rat
                        object_size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                # 丢弃家具 次要
                if object_role in ['side table', 'side plant', 'side lamp']:
                    if replace_id not in seed_dict or replace_id in object_seed_used:
                        if flag_left >= 1 and width_rest[1] < object_size_new[0] - 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                        elif flag_left <= -1 and width_rest[3] < object_size_new[0] - 0.2:
                            object_dump_dict[object_id] = 1
                            continue
                        elif group_type in ['Bed'] and object_size_main[1] > UNIT_HEIGHT_SHELF_MIN:
                            object_dump_dict[object_id] = 1
                            continue
                elif object_role in ['side sofa']:
                    if replace_id in object_seed_used:
                        if object_size_new[0] > object_size_old[0]:
                            object_dump_dict[object_id] = 1
                            continue
                elif object_role in ['chair']:
                    # 丢弃椅子
                    if object_type_main_new in ['table/dining set', 'table/dinning set']:
                        object_dump_dict[object_id] = 1
                        continue
                    elif object_size_main_new[0] * object_size_main_new[2] >= 6 and max(ratio_max_object[0], ratio_max_object[2]) >= 1.5:
                        object_dump_dict[object_id] = 1
                        continue
                    elif object_size_main_new[0] * object_size_main_new[2] >= 4 and ratio_max_object[2] >= 1.5:
                        object_dump_dict[object_id] = 1
                        continue
                    # 丢弃左右
                    if flag_left >= 1 and flag_back == 0:
                        if width_rest[1] < object_size_new[2] / 2 and width_rest[1] < 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                        elif object_size_main[0] > object_size_main[2] * 1.5 and abs(offset_main_x) > 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                    elif flag_left <= -1 and flag_back == 0:
                        if width_rest[3] < object_size_new[2] / 2 and width_rest[3] < 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                        elif object_size_main[0] > object_size_main[2] * 1.5 and abs(offset_main_x) > 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                    # 丢弃前后
                    if flag_back >= 1:
                        if width_rest[0] < object_size_new[2] / 2 and width_rest[0] < 0.1:
                            object_dump_dict[object_id] = 1
                            continue
                    elif flag_back <= -1:
                        if width_rest[2] < object_size_new[2] / 2 and width_rest[2] < 0.1:
                            object_dump_dict[object_id] = 1
                            continue

                # 保持家具
                if 'keep_position' in group_old and replace_id in seed_dict:
                    tmp_x, tmp_y, tmp_z = 0, 0, 0
                # 主要家具
                elif object_role == main_role:
                    tmp_x, tmp_y, tmp_z = offset_main_x, 0, offset_main_z
                    if object_role == 'table' and group_type == 'Media':
                        object_rest = [0, 0, 0, 0]
                        if 'neighbor_base' in group_old:
                            object_rest = group_old['neighbor_base']
                        if ratio_max_group[0] > 1.01 and (region_direct <= -1 or region_beside[1] > 2 > region_beside[0]):
                            offset_pos, normal_pos = group_old['offset'], object_one['normal_position']
                            mov_x = 0 - group_size_old[0] / 2 - object_rest[1] - (offset_pos[0] + normal_pos[0] - object_size_new[0] / 2)
                            tmp_x = mov_x
                        elif ratio_max_group[0] > 1.01 and (region_direct >= 1 or region_beside[0] > 2 > region_beside[1]):
                            offset_pos, normal_pos = group_old['offset'], object_one['normal_position']
                            mov_x = 0 + group_size_old[0] / 2 + object_rest[3] - (offset_pos[0] + normal_pos[0] + object_size_new[0] / 2)
                            tmp_x = mov_x
                elif object_role == 'tv' and group_type == 'Media':
                    offset_side_x, offset_side_z = 0, (object_size_new[2] - object_size_old[2]) / 2
                    tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                # 地毯家具
                elif object_role == 'rug':
                    tmp_x, tmp_y, tmp_z = 0, 0, 0
                # 部件家具
                elif object_role in ['part'] and 'relate' in object_one:
                    relate_id_old = object_one['relate']
                    relate_id_new = ''
                    if relate_id_old in replace_dict:
                        relate_id_new = replace_dict[relate_id_old]
                        if relate_id_new == '':
                            continue
                    # 丢弃配件
                    if relate_id_old == object_id_main and not relate_id_old == relate_id_new:
                        continue
                # 配饰家具
                elif object_role in ['accessory'] and 'relate' in object_one and 'relate_position' in object_one:
                    relate_id_old, relate_position = object_one['relate'], object_one['relate_position']
                    # 丢弃配件
                    if relate_id_old in object_dump_dict:
                        continue
                    elif group_type in ['Dining'] and size_main[1] * (ratio_max_object[1] - 1) > 0.2:
                        continue
                    # 丢弃配件
                    relate_id_new = ''
                    if relate_id_old in replace_dict:
                        relate_id_new = replace_dict[relate_id_old]
                        if relate_id_new == '':
                            continue
                    # 丢弃配件
                    if relate_id_old == object_id_main and not relate_id_old == relate_id_new:
                        if corner_flag >= 1:
                            continue
                        if 'Bath' in room_type and group_type in ['Cabinet']:
                            continue
                    # 保留配件
                    if len(relate_position) > 2:
                        relate_key = relate_id_old + ('_%.2f_%.2f' % (relate_position[0], relate_position[2]))
                        if relate_key not in relate_dict_new:
                            relate_dict_new[relate_key] = {
                                'ratio': [1, 1, 1],
                                'offset': [0, 0, 0],
                                'group': {},
                                'relate_top': UNIT_HEIGHT_SHELF_MIN,
                                'relate_old': {},
                                'relate_new': {},
                                'object_top': [],
                                'object_side': []
                            }
                        if relate_id_new in object_dict_new and 'relate_top' in relate_dict_new[relate_key]:
                            plat_size = object_dict_new[relate_id_new]['size']
                            plat_scale = object_dict_new[relate_id_new]['scale']
                            plat_top = relate_dict_new[relate_key]['relate_top']
                            if plat_size[1] * plat_scale[1] / 100 >= plat_top:
                                continue
                        relate_dict_new[relate_key]['object_top'].append(object_new)
                        group_new['obj_list'].append(object_new)
                        continue
                # 次要家具
                else:
                    if object_role == 'table':
                        offset_side_x = 0
                        offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_main_x + offset_side_x, 0, offset_main_z * 2 + offset_side_z
                        if object_type_main_old in SOFA_CORNER_TYPE_0:
                            if object_type_main_new not in SOFA_CORNER_TYPE_0:
                                if offset_main_z > 0 - 0.2:
                                    tmp_z = offset_side_z + max(0.2, offset_main_z * 2)
                                else:
                                    tmp_z = offset_side_z
                        if corner_flag >= 1 and 'normal_position' in object_one:
                            normal_tmp_x = object_one['normal_position'][0]
                            normal_tmp_z = object_one['normal_position'][2]
                            normal_mov_x = 0.0
                            normal_mov_z = min(offset_main_z * 1.0, 0.3)
                            if object_type_main_new in ["sofa/left corner sofa"]:
                                if normal_tmp_z - (object_size_new[2] * 0.5 + object_size_main[2] * 0.5) < -0.1:
                                    if normal_tmp_x < 0:
                                        normal_mov_x = max(0 - normal_tmp_x * 2, 0 + 0.3)
                                    elif normal_tmp_x < 0 + 0.15:
                                        normal_mov_x = 0 + 0.3 - normal_tmp_x
                            elif object_type_main_new in ["sofa/right corner sofa"]:
                                if normal_tmp_z - (object_size_new[2] * 0.5 + object_size_main[2] * 0.5) < -0.1:
                                    if normal_tmp_x > 0:
                                        normal_mov_x = min(0 - normal_tmp_x * 2, 0 - 0.3)
                                    elif normal_tmp_x > 0 - 0.15:
                                        normal_mov_x = 0 - 0.3 - normal_tmp_x
                            else:
                                normal_mov_x = 0 - normal_tmp_x * 0.5
                            if object_type_main_old in SOFA_CORNER_TYPE_0:
                                if object_type_main_new not in SOFA_CORNER_TYPE_0:
                                    if offset_main_z > 0 - 0.2:
                                        normal_mov_z = max(0.2, offset_main_z * 2)
                            tmp_x = offset_main_x + normal_mov_x
                            tmp_z = offset_side_z + normal_mov_z
                        elif corner_flag <= 0 and 'normal_position' in object_one:
                            normal_tmp_z = object_one['normal_position'][2]
                            normal_mov_z = 0
                            if normal_tmp_z < (object_size_main_new[2] + object_size_new[2]) / 2 + 0.2:
                                normal_mov_z = 0.2
                            tmp_z += normal_mov_z
                    elif object_role == 'side table':
                        offset_side_x = 0
                        offset_side_x += offset_main_x
                        if flag_left >= 1:
                            offset_side_x += size_main[0] * (1 - ratio_max_object[0]) / 2
                            if object_size_new[0] > object_size_old[0]:
                                offset_side_x -= (object_size_new[0] - object_size_old[0]) / 2
                            if replace_id not in seed_dict or replace_id in object_seed_used:
                                if width_rest[1] < -offset_side_x + object_size_new[0] - 0.1:
                                    object_dump_dict[object_id] = 1
                                    continue
                        elif flag_left <= -1:
                            offset_side_x -= size_main[0] * (1 - ratio_max_object[0]) / 2
                            if object_size_new[0] > object_size_old[0]:
                                offset_side_x += (object_size_new[0] - object_size_old[0]) / 2
                            if replace_id not in seed_dict or replace_id in object_seed_used:
                                if width_rest[3] < offset_side_x + object_size_new[0] - 0.2:
                                    object_dump_dict[object_id] = 1
                                    continue
                        offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                    elif object_role == 'side sofa':
                        offset_side_x = 0
                        if flag_left >= 1:
                            offset_side_x -= (object_size_new[2] - object_size_old[2]) / 2
                        elif flag_left <= -1:
                            offset_side_x += (object_size_new[2] - object_size_old[2]) / 2
                        offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_main_x + offset_side_x, 0, offset_main_z * 2 + offset_side_z
                        if object_type_main_old in SOFA_CORNER_TYPE_0:
                            if object_type_main_new not in SOFA_CORNER_TYPE_0:
                                if offset_main_z > 0 - 0.2:
                                    tmp_z = max(0.2, offset_main_z * 2) + offset_side_z
                        if corner_flag >= 1 and 'normal_position' in object_one:
                            normal_tmp_x, normal_mov_x = object_one['normal_position'][0], 0.0
                            if object_type_main_new in ["sofa/left corner sofa"]:
                                if normal_tmp_x < 0 + 0.15:
                                    normal_mov_x = 0 + object_size_main[0] / 2 - normal_tmp_x
                            elif object_type_main_new in ["sofa/right corner sofa"]:
                                if normal_tmp_x > 0 - 0.15:
                                    normal_mov_x = 0 - object_size_main[0] / 2 - normal_tmp_x
                            tmp_x = offset_main_x + offset_side_x + normal_mov_x
                    elif object_role == 'chair':
                        offset_side_x = offset_main_x
                        offset_side_z = offset_main_z
                        if flag_left >= 1:
                            offset_side_x += (object_size_old[0] - object_size_new[0]) / 2
                            if ratio_max_object[0] > 1:
                                offset_side_x -= object_size_main_old[0] * (ratio_max_object[0] - 1) / 2
                        elif flag_left <= -1:
                            offset_side_x -= (object_size_old[0] - object_size_new[0]) / 2
                            if ratio_max_object[0] > 1:
                                offset_side_x += object_size_main_old[0] * (ratio_max_object[0] - 1) / 2
                        if flag_back >= 1:
                            if object_id_main in replace_dict and (not object_round_main) and \
                                    (not replace_dict[object_id_main] == object_id_main):
                                abs_z = abs(object_one['normal_position'][2])
                                fix_z = object_size_main_new[2] * 0.5 + object_size_new[2] * 0.5
                                min_z = 0 - object_size_main_new[2] * 0.5 - width_rest[2] + object_size_new[2] * 0.5
                                offset_side_z += (abs_z - max(fix_z, min_z))
                            elif ratio_max_object[2] > 1:
                                offset_side_z += (object_size_old[2] - object_size_new[2]) / 2
                                offset_side_z -= object_size_main_old[2] * (ratio_max_object[2] - 1)
                        elif flag_back <= -1:
                            if object_id_main in replace_dict and (not object_round_main) \
                                    and (not replace_dict[object_id_main] == object_id_main):
                                abs_z = abs(object_one['normal_position'][2])
                                fix_z = object_size_main_new[2] * 0.5 + object_size_new[2] * 0.5
                                max_z = 0 + object_size_main_new[2] * 0.5 + width_rest[2] - object_size_new[2] * 0.5
                                offset_side_z += (min(fix_z, max_z) - abs_z)
                            elif ratio_max_object[2] > 1:
                                offset_side_z -= (object_size_old[2] - object_size_new[2]) / 2
                                offset_side_z += object_size_main_old[2] * (ratio_max_object[2] - 1)
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                    elif object_role == 'bath':
                        offset_side_x, offset_side_z = 0, 0
                        object_angle_old = rot_to_ang(object_one['normal_rotation'])
                        if abs(object_angle_old - math.pi / 2) < 0.1 or abs(object_angle_old + math.pi / 2) < 0.1:
                            if region_direct >= 1:
                                offset_side_x -= (object_size_new[2] - object_size_old[2]) / 2
                            elif region_direct <= -1:
                                offset_side_x += (object_size_new[2] - object_size_old[2]) / 2
                            offset_side_z = (object_size_new[0] - object_size_old[0]) / 2
                        else:
                            if region_direct >= 1:
                                offset_side_x -= (object_size_new[0] - object_size_old[0]) / 2
                            elif region_direct <= -1:
                                offset_side_x += (object_size_new[0] - object_size_old[0]) / 2
                            offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                    elif object_role == 'screen':
                        offset_side_x, offset_side_z = 0, 0
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                    else:
                        offset_side_x, offset_side_z = 0, 0
                        if flag_left >= 1:
                            offset_side_x += size_main[0] * (1 - ratio_max_object[0]) / 2
                            offset_side_x += (object_size_old[0] - object_size_new[0]) / 2
                        elif flag_left <= -1:
                            offset_side_x -= size_main[0] * (1 - ratio_max_object[0]) / 2
                            offset_side_x -= (object_size_old[0] - object_size_new[0]) / 2
                        offset_side_z -= (object_size_old[2] - object_size_new[2]) / 2
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                # 位置信息
                add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                add_y = tmp_y
                add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                object_new['position'][0] += add_x
                object_new['position'][1] += add_y
                object_new['position'][2] += add_z
                if 'normal_position' in object_one:
                    object_new['normal_position'] = object_one['normal_position'][:]
                    object_new['normal_position'][0] += tmp_x
                    object_new['normal_position'][1] += tmp_y
                    object_new['normal_position'][2] += tmp_z
                if 'origin_position' in object_one:
                    object_new['origin_position'] = object_one['origin_position'][:]
                    object_new['origin_position'][0] += add_x
                    object_new['origin_position'][1] += add_y
                    object_new['origin_position'][2] += add_z
                # 位置检查
                if object_role in ['table', 'side sofa'] and group_type in ['Meeting'] and corner_flag >= 1:
                    ang_adjust = 0 - group_angle
                    pos_adjust = [object_new['position'][i] - object_position_main[i] for i in range(3)]
                    pos_z = pos_adjust[2] * math.cos(ang_adjust) - pos_adjust[0] * math.sin(ang_adjust)
                    pos_x = pos_adjust[2] * math.sin(ang_adjust) + pos_adjust[0] * math.cos(ang_adjust)
                    # 调整
                    if object_role == 'table':
                        tmp_x = pos_x
                        tmp_z = pos_z
                        add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
                        add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
                        object_new['position'][0] = object_position_main[0] + add_x
                        object_new['position'][2] = object_position_main[2] + add_z
                    # 删除
                    elif object_role == 'side sofa':
                        if offset_main_z > 0.4 and object_size_main[2] > 1.4:
                            continue
                # 角度信息
                if object_role in ['table'] and group_type in ['Meeting'] and 'normal_rotation' in object_one:
                    ang_nor = rot_to_ang(object_one['normal_rotation'])
                    if abs(ang_nor) < 0.1 and object_xz_old > 1.1 and object_xz_new < 0.9:
                        ang_new = rot_to_ang(object_new['rotation']) + math.pi / 2
                        object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                    elif abs(ang_nor) > 0.1 and object_xz_new > 0.9:
                        ang_nor = 0
                        ang_new = rot_to_ang(object_rotation_main) + ang_nor
                        object_new['normal_rotation'] = [0, math.sin(ang_nor / 2), 0, math.cos(ang_nor / 2)]
                        object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                        pass
                elif object_role in ['side sofa', 'side table'] and 'normal_position' in object_one:
                    pos_nor, ang_nor = object_one['normal_position'], rot_to_ang(object_new['normal_rotation'])
                    ang_fix = False
                    if pos_nor[0] < 0 - 0.3:
                        if object_role in ['side sofa']:
                            if abs(ang_to_ang(ang_nor + math.pi / 2)) <= math.pi / 4:
                                ang_nor += math.pi
                                ang_fix = True
                            elif abs(ang_to_ang(ang_nor - math.pi / 2)) >= math.pi / 4 and abs(object_xz_old - 1) < 0.2:
                                ang_nor = math.pi / 2
                                ang_fix = True
                        elif object_role in ['side table']:
                            if abs(ang_to_ang(ang_nor)) >= math.pi / 4 and abs(object_xz_old - 1) < 0.2:
                                ang_nor = 0
                                ang_fix = True
                    elif pos_nor[0] > 0 + 0.3:
                        if object_role in ['side sofa']:
                            if abs(ang_to_ang(ang_nor - math.pi / 2)) <= math.pi / 4:
                                ang_nor -= math.pi
                                ang_fix = True
                            elif abs(ang_to_ang(ang_nor + math.pi / 2)) >= math.pi / 4 and abs(object_xz_old - 1) < 0.2:
                                ang_nor = -math.pi / 2
                                ang_fix = True
                        elif object_role in ['side table']:
                            if abs(ang_to_ang(ang_nor)) >= math.pi / 4 and abs(object_xz_old - 1) < 0.2:
                                ang_nor = 0
                                ang_fix = True
                    if ang_fix:
                        ang_new = rot_to_ang(object_rotation_main) + ang_nor
                        object_new['normal_rotation'] = [0, math.sin(ang_nor / 2), 0, math.cos(ang_nor / 2)]
                        object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                elif object_role == 'bath':
                    if region_direct >= 1:
                        pass
                    elif region_direct <= -1:
                        pass
                # 平台信息
                relate_key = object_id + '_%.2f_%.2f' % (object_position[0], object_position[2])
                if object_role in GROUP_RULE_FUNCTIONAL[group_type]['plat']:
                    if relate_key not in relate_dict_new:
                        relate_dict_new[relate_key] = {
                            'ratio': [1, 1, 1],
                            'offset': [0, 0, 0],
                            'group': {},
                            'relate_top': UNIT_HEIGHT_SHELF_MIN,
                            'relate_old': {},
                            'relate_new': {},
                            'object_top': [],
                            'object_side': []
                        }
                if relate_key in relate_dict_new:
                    relate_info = relate_dict_new[relate_key]
                    relate_info['ratio'] = [object_size_new[i] / object_size_old[i] for i in range(3)]
                    relate_info['offset'] = [tmp_x, 0, tmp_z]
                    relate_info['group'] = group_new
                    relate_info['relate_top'] = UNIT_HEIGHT_SHELF_MIN
                    relate_info['relate_old'] = object_one
                    relate_info['relate_new'] = object_new
                    if object_role == 'table' and group_type in ['Media']:
                        if len(group_old['obj_list']) > 0:
                            object_tv = group_old['obj_list'][0]
                            bottom_tv = object_tv['position'][1] - 0.05
                            if object_tv['type'] in ['electronics/TV - on top of others']:
                                bottom_tv += 0.05
                            relate_info['relate_top'] = bottom_tv
                    elif object_role == 'table' and group_type in ['Work', 'Rest']:
                        relate_info['relate_top'] = UNIT_HEIGHT_TABLE_MAX
                # 添加信息
                group_new['obj_list'].append(object_new)
                if replace_id in seed_dict:
                    object_seed_used[replace_id] = 1
                # 错误纠正
                if object_new['type'] in ['table/dining table', 'table/dining table - square', 'table/table']:
                    find_chair = False
                    for object_chair in object_list_old:
                        if 'role' in object_chair and object_chair['role'] in ['chair']:
                            find_chair = True
                            break
                    if object_size_new[0] * 1.2 < object_size_new[2] and find_chair:
                        ang_new = rot_to_ang(object_new['rotation']) + math.pi / 2
                        object_new['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                # 主体信息
                if object_role == main_role:
                    object_id_main = object_id
                    object_type_main_old, object_type_main_new = object_type, object_new['type']
                    object_size_main_old, object_size_main_new = object_size_old[:], object_size_new[:]
                    object_size_main = object_size_new[:]
                    object_position_main = object_new['position'][:]
                    object_rotation_main = object_new['rotation'][:]
                    if group_type == 'Meeting' and group_old['obj_main'] in replace_dict:
                        if object_size_main[2] > object_size_main[0] * 0.6 and 2 <= object_size_main[0] < 3:
                            corner_flag = 1
                        elif object_size_main[2] >= 1.6:
                            corner_flag = 1
                        # 纠错信息
                        if corner_flag == 1:
                            if object_type not in SOFA_CORNER_TYPE_0:
                                corner_flag = 2
                        corner_dict_new[object_new['id']] = corner_flag
                    if abs(object_size_main_old[0] - object_size_main_old[2]) < abs(object_size_main_old[0]) * 0.1:
                        object_round_main = True
            # 装饰家具
            elif group_type in GROUP_RULE_DECORATIVE:
                # 关联关系
                relate_id_old, relate_id_new = '', ''
                relate_width, relate_height, relate_angle = 0, object_one['position'][1] - 0.1, 0
                normal_position, relate_position, relate_vertical, relate_offset = [0, 0, 0], [], 0, [0, 0, 0]
                object_width, object_height = object_size_new[0], object_size_new[1]
                object_angle = rot_to_ang(object_new['rotation'])
                if 'relate' in object_one:
                    relate_id_old = object_one['relate']
                if 'normal_position' in object_one:
                    normal_position = object_one['normal_position']
                if 'relate_position' in object_one:
                    relate_position = object_one['relate_position']
                # 参数计算
                if group_type in ['Wall', 'Ceiling', 'Floor']:
                    # 高度
                    if relate_id_old in replace_dict:
                        relate_id_new = replace_dict[relate_id_old]
                        if relate_id_new in replace_size:
                            relate_height = replace_size[relate_id_new][1] / 100
                    # 偏移
                    if len(relate_id_old) > 0 and len(relate_position) > 2:
                        relate_key = relate_id_old + '_%.2f_%.2f' % (relate_position[0], relate_position[2])
                        if relate_key in relate_dict_new:
                            relate_info = relate_dict_new[relate_key]
                            relate_plat, relate_group = relate_info['relate_new'], relate_info['group']
                            if len(relate_plat) > 0:
                                relate_width, relate_angle = 0, rot_to_ang(relate_plat['rotation'])
                                relate_vertical, relate_offset = 0, relate_info['offset']
                                if 'size' in relate_plat and 'scale' in relate_plat:
                                    relate_width = relate_plat['size'][0] * relate_plat['scale'][0] / 100
                                if 'vertical' in relate_group:
                                    relate_vertical = relate_group['vertical']
                # 墙面装饰
                if group_type == 'Wall':
                    # 高度
                    lift_max, lift_min = room_height - 0.2 - object_height, object_one['position'][1]
                    height_max = room_height - 0.2 - object_one['position'][1]
                    # 删除
                    if len(relate_position) > 2:
                        relate_key = relate_id_old + '_%.2f_%.2f' % (relate_position[0], relate_position[2])
                        relate_new = {}
                        if relate_key in relate_dict_new:
                            relate_new = relate_dict_new[relate_key]['relate_new']
                        if len(relate_new) > 0:
                            relate_id_new = relate_new['id']
                        if relate_id_new == relate_id_old:
                            lift_max = object_new['position'][1]
                        elif len(relate_new) > 0:
                            relate_height_new = abs(relate_new['size'][1] * relate_new['scale'][1] / 100)
                            if room_height - 0.2 - relate_height_new < object_size_new[1] * 0.8:
                                continue
                            else:
                                lift_min = max(lift_min, relate_height_new)
                                height_max = min(height_max, room_height - relate_height_new)
                    # 调整
                    if object_size_new[1] > height_max:
                        height_rat = height_max / object_size_new[1]
                        object_new['scale'][0] *= height_rat
                        object_new['scale'][1] *= height_rat
                    object_y = object_new['position'][1]
                    if object_y < lift_min:
                        object_y = lift_min
                    if object_y > lift_max:
                        object_y = lift_max
                    object_new['position'][1] = object_y
                    # 偏移
                    if len(relate_position) > 2:
                        if relate_vertical == 0:
                            tmp_x, tmp_y, tmp_z = relate_offset[0], 0, 0
                        else:
                            tmp_x, tmp_y, tmp_z = relate_offset[2], 0, 0
                        object_angle = rot_to_ang(object_new['rotation'])
                        add_x = tmp_z * math.sin(object_angle) + tmp_x * math.cos(object_angle)
                        add_y = tmp_y
                        add_z = tmp_z * math.cos(object_angle) - tmp_x * math.sin(object_angle)
                        object_new['position'][0] += add_x
                        object_new['position'][1] += add_y
                        object_new['position'][2] += add_z
                    # 添加
                    group_new['obj_list'].append(object_new)
                    continue
                # 顶面装饰
                elif group_type == 'Ceiling':
                    # 尺寸
                    if object_size_new[1] > object_size_old[1] and object_size_new[1] > room_height * 0.3:
                        height_ratio = room_height * 0.3 / object_size_new[1]
                        object_new['scale'][0] *= height_ratio
                        object_new['scale'][1] *= height_ratio
                        object_new['scale'][2] *= height_ratio
                        object_size_new = [abs(object_size_new[i] * height_ratio) for i in range(3)]
                    # 偏移
                    object_new['position'][1] += (object_size_old[1] - object_size_new[1])
                    if len(relate_position) > 2:
                        tmp_x, tmp_y, tmp_z = relate_offset[0], 0, relate_offset[2]
                        add_x = tmp_z * math.sin(relate_angle) + tmp_x * math.cos(relate_angle)
                        add_y = tmp_y
                        add_z = tmp_z * math.cos(relate_angle) - tmp_x * math.sin(relate_angle)
                        object_new['position'][0] += add_x
                        object_new['position'][1] += add_y
                        object_new['position'][2] += add_z
                    # 添加
                    group_new['obj_list'].append(object_new)
                    continue
                # 地面装饰
                elif group_type == 'Floor' and len(relate_position) > 2:
                    # 标志
                    offset_side_x, offset_side_z, offset_flag = 0, 0, False
                    if len(relate_position) > 2:
                        relate_key = relate_id_old + '_%.2f_%.2f' % (relate_position[0], relate_position[2])
                        relate_new = {}
                        if relate_key not in relate_dict_new:
                            relate_dict_new[relate_key] = {
                                'ratio': [],
                                'offset': [],
                                'group': {},
                                'relate_top': 1,
                                'relate_old': {},
                                'relate_new': {},
                                'object_top': [],
                                'object_side': []
                            }
                        else:
                            relate_new = relate_dict_new[relate_key]['relate_new']
                        # 删除
                        if len(relate_new) > 0:
                            relate_width_dlt = 0
                            if normal_position[0] <= 0 - 0.1:
                                relate_width_dlt = relate_group['neighbor_base'][1]
                            elif normal_position[0] <= 0 + 0.1:
                                relate_width_dlt = relate_group['neighbor_base'][3]
                            if relate_width_dlt < object_size_new[0]:
                                # 删除
                                if relate_width_dlt < 0.1:
                                    continue
                                elif relate_width_dlt < object_size_new[0] * 0.8:
                                    continue
                                # 缩放
                                scale_adjust = relate_width_dlt / object_size_new[0]
                                if object_type in ['electronics/air-conditioner - floor-based', 'lighting/floor lamp']:
                                    scale_adjust = max(scale_adjust, 0.8)
                                object_new['scale'] = [object_new['scale'][i] * scale_adjust for i in range(3)]
                                object_size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                        relate_dict_new[relate_key]['object_side'].append(object_new)
                        # 位置
                        offset_side_x, offset_side_z = 0, 0
                        if object_size_new[2] > object_size_old[2]:
                            offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        offset_flag = True
                    elif object_id in replace_dict:
                        # 位置信息
                        offset_side_x = 0
                        offset_side_z = (object_size_new[2] - object_size_old[2]) / 2
                        offset_flag = True
                    # 偏移
                    if offset_flag:
                        tmp_x, tmp_y, tmp_z = offset_side_x, 0, offset_side_z
                        add_x = tmp_z * math.sin(object_angle) + tmp_x * math.cos(object_angle)
                        add_y = tmp_y
                        add_z = tmp_z * math.cos(object_angle) - tmp_x * math.sin(object_angle)
                        object_new['position'][0] += add_x
                        object_new['position'][1] += add_y
                        object_new['position'][2] += add_z
                    # 尺寸
                    else:
                        scale_new = [object_one['size_cur'][i] / object_new['size'][i] for i in range(3)]
                        object_new['scale'] = scale_new
                    group_new['obj_list'].append(object_new)
                    continue
                # 窗户装饰
                elif group_type == 'Window':
                    scale_new = [object_size_old[i] * 100 / object_new['size'][i] for i in range(3)]
                    object_new['scale'] = scale_new
                # 其他装饰
                else:
                    scale_new = [object_one['size_cur'][i] / object_new['size'][i] for i in range(3)]
                    object_new['scale'] = scale_new
                scale_new = object_new['scale']
                if 'lamp' in object_new['type']:
                    scale_new_max = max(scale_new[0], scale_new[1], scale_new[2])
                    scale_new_min = min(scale_new[0], scale_new[1], scale_new[2])
                    if scale_new_max > 1.1 or scale_new_min < 0.9:
                        object_new['scale'] = [1, 1, 1]
                # 添加信息
                group_new['obj_list'].append(object_new)
                continue

        # 增加分组
        if object_id_main in object_dump_dict:
            continue
        group_list_add.append(group_new)

    # 更新装饰
    for relate_key, relate_info in relate_dict_new.items():
        if len(relate_info['group']) <= 0:
            continue
        plat_group = relate_info['group']
        plat_ratio = relate_info['ratio']
        plat_offset = relate_info['offset']
        plat_direct = 0
        if 'region_direct' in plat_group:
            plat_direct = plat_group['region_direct']
        plat_old, plat_new = relate_info['relate_old'], relate_info['relate_new']
        plat_size = [plat_old['size'][i] * plat_old['scale'][i] / 100 for i in range(3)]
        plat_size_new = [plat_size[i] * plat_ratio[i] for i in range(3)]
        plat_angle = rot_to_ang(plat_old['rotation'])
        # 顶端配件
        accessory_top_list, accessory_top_dict = relate_info['object_top'], {}
        plat_id_old, plat_id_new = plat_old['id'], plat_new['id']
        if plat_id_new == plat_id_old:
            accessory_list_new = accessory_top_list
        else:
            accessory_list_new, accessory_list_old = compute_accessory_keep(accessory_top_list)
            if 'obj_list' in plat_group:
                accessory_list_obj = plat_group['obj_list']
                for object_old in accessory_list_old:
                    accessory_list_obj.remove(object_old)
        plat_ratio_min = plat_ratio[0]
        if plat_ratio[0] > plat_ratio[2]:
            plat_ratio_min = plat_ratio[2]
        if plat_ratio_min > 1.0:
            plat_ratio_min = 1.0
        plat_ratio_min = (plat_ratio_min + 1) * 0.5
        for object_one in accessory_list_new:
            # 移除
            if plat_new['type'] in PACK_OBJECT_TYPE_0:
                plat_group['obj_list'].remove(object_one)
                continue
            # 缩放
            object_one['scale'][0] *= plat_ratio_min
            object_one['scale'][1] *= plat_ratio_min
            object_one['scale'][2] *= plat_ratio_min
            # 位移
            x1, z1 = plat_old['position'][0], plat_old['position'][2]
            x2, z2 = object_one['position'][0], object_one['position'][2]
            dis, ang = compute_furniture_length(x1, z1, x2, z2)
            offset_x, offset_z = dis * math.sin(ang - plat_angle), dis * math.cos(ang - plat_angle)
            ratio_x, ratio_z = min(plat_ratio[0], 1), min(plat_ratio[2], 1)
            ratio_offset_x, ratio_offset_z = offset_x * ratio_x, offset_z * ratio_z
            if plat_id_new in corner_dict_new:
                ratio_offset_x, ratio_offset_z = offset_x, offset_z
            tmp_x, tmp_z = ratio_offset_x, ratio_offset_z
            # 移除
            limit_x, limit_z = plat_size_new[0] * 0.4, plat_size_new[2] * 0.4
            if plat_id_new in corner_dict_new:
                limit_z = plat_size_new[2] * 0.1
            if (abs(tmp_x) > limit_x + 0.05 or abs(tmp_z) > limit_z + 0.05) and not plat_id_old == plat_id_new:
                plat_group['obj_list'].remove(object_one)
                continue
            # 更新
            add_x = tmp_z * math.sin(plat_angle) + tmp_x * math.cos(plat_angle)
            add_z = tmp_z * math.cos(plat_angle) - tmp_x * math.sin(plat_angle)
            object_one['position'][0] = plat_new['position'][0] + add_x
            object_one['position'][2] = plat_new['position'][2] + add_z
            if 'normal_position' in object_one and 'normal_position' in plat_new:
                object_one['normal_position'][0] = plat_new['normal_position'][0] + tmp_x
                object_one['normal_position'][2] = plat_new['normal_position'][2] + tmp_z
            if 'origin_position' in object_one and 'origin_position' in plat_new:
                object_one['origin_position'][0] = plat_new['origin_position'][0] + add_x
                object_one['origin_position'][2] = plat_new['origin_position'][2] + add_z
            if plat_old['role'] in ['table', 'side table', 'cabinet']:
                if 'pendant light' in object_one['type']:
                    object_y = object_one['position'][1]
                elif plat_old['id'] == plat_new['id'] and abs(plat_ratio[1] - 1.0) < 0.1:
                    object_y = object_one['position'][1]
                else:
                    object_y = plat_new['position'][1] + plat_new['size'][1] * plat_new['scale'][1] / 100
                object_one['position'][1] = object_y
                if 'normal_position' in object_one and 'normal_position' in plat_new:
                    object_one['normal_position'][1] = object_y
                if 'origin_position' in object_one and 'origin_position' in plat_new:
                    object_one['origin_position'][1] = object_y
            object_one['relate'] = plat_new['id']
            object_one['relate_role'] = plat_new['role']
        # 侧边配件
        accessory_side_list = relate_info['object_side']
        for object_one in accessory_side_list:
            x1, z1 = plat_old['position'][0], plat_old['position'][2]
            x2, z2 = object_one['position'][0], object_one['position'][2]
            flag_left, flag_back = compute_furniture_locate(x1, z1, x2, z2, plat_angle, plat_old['size'][0], plat_old['size'][2])
            offset_side_x, offset_side_z = plat_offset[0], 0
            if flag_left >= 1:
                if plat_direct >= 1:
                    offset_side_x += plat_size[0] * (1 - plat_ratio[0]) * 0.5
                elif plat_direct == 0:
                    offset_side_x += plat_size[0] * (1 - plat_ratio[0]) * 0.5
            elif flag_left <= -1:
                if plat_direct <= -1:
                    offset_side_x -= plat_size[0] * (1 - plat_ratio[0]) * 0.5
                elif plat_direct == 0:
                    offset_side_x -= plat_size[0] * (1 - plat_ratio[0]) * 0.5
            tmp_x, tmp_z = offset_side_x, offset_side_z
            add_x = tmp_z * math.sin(plat_angle) + tmp_x * math.cos(plat_angle)
            add_z = tmp_z * math.cos(plat_angle) - tmp_x * math.sin(plat_angle)
            object_one['position'][0] += add_x
            object_one['position'][2] += add_z
            if 'normal_position' in object_one and 'normal_position' in plat_new:
                object_one['normal_position'][0] = plat_new['normal_position'][0] + tmp_x
                object_one['normal_position'][2] = plat_new['normal_position'][2] + tmp_z
            if 'origin_position' in object_one and 'origin_position' in plat_new:
                object_one['origin_position'][0] = plat_new['origin_position'][0] + add_x
                object_one['origin_position'][2] = plat_new['origin_position'][2] + add_z
            if 'lamp' in object_one['type']:
                scale_new = object_one['scale']
                scale_new_max = max(scale_new[0], scale_new[1], scale_new[2])
                scale_new_min = min(scale_new[0], scale_new[1], scale_new[2])
                if scale_new_max > 1.1 or scale_new_min < 0.9:
                    object_one['scale'] = [1, 1, 1]
    # 更新参数
    for group_new in group_list_add:
        compute_group_param(group_new, keep_size=True)
    # 返回信息
    return group_list_add


# 避让家具位置
def group_rect_dodge(group_list_src):
    group_list_seed, group_list_main, group_list_rest, group_list_dump = [], [], [], []
    for group_one in group_list_src:
        if 'seed_list' in group_one and len(group_one['seed_list']) > 0:
            group_list_seed.append(group_one)
        elif 'keep_list' in group_one and len(group_one['keep_list']) > 0:
            group_list_seed.append(group_one)
        elif group_one['type'] in ['Meeting', 'Bed', 'Dining', 'Media']:
            group_list_main.append(group_one)
        elif group_one['type'] in ['Armoire', 'Cabinet', 'Appliance', 'Work', 'Rest']:
            group_list_rest.append(group_one)
    for group_old in group_list_seed:
        type_old, size_old = group_old['type'], group_old['size']
        pos_old, ang_old = group_old['position'], rot_to_ang(group_old['rotation'])
        for group_new in group_list_main:
            object_list = group_new['obj_list']
            for object_new in object_list:
                if object_new['role'] in ['tv', 'side_table', 'side sofa', 'chair']:
                    pass
                elif object_new['role'] in [ 'table'] and group_new['type'] in ['Bed', 'Media', 'Rest']:
                    pass
                else:
                    continue
                object_dump = False
                size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                pos_new, ang_new = object_new['position'], rot_to_ang(object_new['rotation'])
                dis_mov, ang_mov = xyz_to_ang(pos_old[0], pos_old[2], pos_new[0], pos_new[2])
                dis_x = dis_mov * math.sin(ang_mov - ang_old)
                dis_z = dis_mov * math.cos(ang_mov - ang_old)
                rat_x, rat_z = 0.5, 0.5
                if type_old in ['Media'] and size_old[2] >= 1.0:
                    rat_x, rat_z = 0.6, 0.6
                len_x, len_z = min(size_new[0], size_new[2]), min(size_new[0], size_new[2])
                if abs(ang_to_ang(ang_old - ang_new)) < 0.1 or \
                        abs(ang_to_ang(ang_old - ang_new - math.pi)) < 0.1:
                    len_x, len_z = size_new[0], size_new[2]
                elif abs(ang_to_ang(ang_old - ang_new - math.pi / 2)) < 0.1 or \
                        abs(ang_to_ang(ang_old - ang_new + math.pi / 2)) < 0.1:
                    len_x, len_z = size_new[2], size_new[0]
                if abs(dis_x) < size_old[0] / 2 + len_x * rat_x:
                    if abs(dis_z) < size_old[2] * 0.5 + len_z * 0.5 - 0.01:
                        if pos_new[1] <= pos_old[1] + size_old[1]:
                            object_dump = True
                if object_dump:
                    for object_idx in range(len(object_list) - 1, -1, -1):
                        object_old = object_list[object_idx]
                        if object_old['id'] == object_new['id']:
                            pos_dump = object_old['position']
                            if abs(pos_dump[0] - pos_new[0]) + abs(pos_dump[2] - pos_new[2]) <= 0.2:
                                object_list.pop(object_idx)
                        elif 'relate' in object_old and object_old['relate'] == object_new['id']:
                            pos_dump = object_old['relate_position']
                            if abs(pos_dump[0] - pos_new[0]) + abs(pos_dump[2] - pos_new[2]) <= 0.2:
                                object_list.pop(object_idx)
        for group_new in group_list_rest:
            size_new, pos_new, ang_new = group_new['size'], group_new['position'], rot_to_ang(group_new['rotation'])
            dis_mov, ang_mov = xyz_to_ang(pos_old[0], pos_old[2], pos_new[0], pos_new[2])
            dis_x = dis_mov * math.sin(ang_mov - ang_old)
            dis_z = dis_mov * math.cos(ang_mov - ang_old)
            rat_x, rat_z = 0.4, 0.2
            len_x, len_z = min(size_new[0], size_new[2]), min(size_new[0], size_new[2])
            if abs(ang_to_ang(ang_old - ang_new)) < 0.1 or abs(ang_to_ang(ang_old - ang_new - math.pi)) < 0.1:
                len_x, len_z = size_new[0], size_new[2]
            elif abs(ang_to_ang(ang_old - ang_new - math.pi / 2)) < 0.1 or abs(ang_to_ang(ang_old - ang_new + math.pi / 2)) < 0.1:
                len_x, len_z = size_new[2], size_new[0]
            if abs(dis_x) < size_old[0] * 0.5 + len_x * rat_x:
                if abs(dis_z) < size_old[2] * 0.5 + len_z * rat_z:
                    if pos_new[1] <= pos_old[1] + size_old[1]:
                        if group_new not in group_list_dump:
                            group_list_dump.append(group_new)
    for group_new in group_list_dump:
        if group_new in group_list_src:
            group_list_src.remove(group_new)


# 增加家具角色
def group_rect_append(group_old, seed_one):
    # 复制信息
    group_new = group_old
    return group_new


# 调整组合尺寸
def resolve_group_regulation(group_one, neighbor_fix=False):
    if 'regulation' in group_one:
        group_position, group_angle = group_one['position'], rot_to_ang(group_one['rotation'])
        group_regulate, group_neighbor = group_one['regulation'][:], [0, 0, 0, 0]
        if 'neighbor_best' in group_one:
            group_neighbor = group_one['neighbor_best']
        # 重置尺寸
        group_one['size'][0] += group_regulate[1]
        group_one['size'][0] += group_regulate[3]
        group_one['size'][2] += group_regulate[0]
        group_one['size'][2] += group_regulate[2]
        if neighbor_fix:
            group_one['size'][0] += group_neighbor[1]
            group_one['size'][0] += group_neighbor[3]
            group_one['size'][2] += group_neighbor[0]
            group_one['size'][2] += group_neighbor[2]
        group_one['size_min'][0] = min(group_one['size'][0], group_one['size_min'][0])
        group_one['size_min'][2] = min(group_one['size'][2], group_one['size_min'][2])
        # 重置位置
        tmp_x = (group_regulate[3] - group_regulate[1]) / 2
        tmp_z = (group_regulate[2] - group_regulate[0]) / 2
        if neighbor_fix:
            tmp_x += (group_neighbor[3] - group_neighbor[1]) / 2
            tmp_z += (group_neighbor[2] - group_neighbor[0]) / 2
        add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
        add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
        group_one['position'][0] += add_x
        group_one['position'][2] += add_z

        # 重置调整
        group_one['regulation'] = [0, 0, 0, 0]
        if neighbor_fix:
            group_one['neighbor_base'] = [0, 0, 0, 0]
            group_one['neighbor_more'] = [0, 0, 0, 0]
            group_one['neighbor_best'] = [0, 0, 0, 0]
            group_one['neighbor_zone'] = [0, 0, 0, 0]
        # 重置剩余
        size_rest = group_one['size_rest']
        size_rest[1] += group_regulate[1]
        size_rest[3] += group_regulate[3]
        size_rest[0] += group_regulate[0]
        size_rest[2] += group_regulate[2]
        # 重置偏移
        group_one['offset'][0] = (size_rest[1] - size_rest[3]) / 2
        group_one['offset'][2] = (size_rest[0] - size_rest[2]) / 2


# 调整组合碰撞
def resolve_group_impaction(group_list, decor_list, room_type=''):
    group_wear, group_dump = [], []
    # 避让处理
    for index_old, group_old in enumerate(group_list):
        if group_old in group_dump:
            continue
        angle_old = rot_to_ang(group_old['rotation'])
        stand_old = hor_or_ver(angle_old)
        if stand_old <= -1:
            continue
        # 参数
        pos_old, rot_old, size_old = group_old['position'][:], group_old['rotation'], group_old['size'][:]
        ang_old = rot_to_ang(rot_old)
        box_old = compute_furniture_rect(size_old, pos_old, rot_old)
        min_x_1 = min(box_old[0], box_old[2], box_old[4], box_old[6])
        max_x_1 = max(box_old[0], box_old[2], box_old[4], box_old[6])
        min_z_1 = min(box_old[1], box_old[3], box_old[5], box_old[7])
        max_z_1 = max(box_old[1], box_old[3], box_old[5], box_old[7])
        for index_new, group_new in enumerate(group_list):
            if group_new in group_dump:
                continue
            if index_new == index_old:
                continue
            angle_new = rot_to_ang(group_new['rotation'])
            stand_new = hor_or_ver(angle_new)
            if stand_new <= -1:
                continue
            pos_new, rot_new, size_new = group_new['position'][:], group_new['rotation'], group_new['size'][:]
            ang_new = rot_to_ang(rot_new)
            # 旋转
            if group_old['type'] in ['Meeting'] and group_new['type'] in ['Dining']:
                x1, z1, x2, z2 = pos_old[0], pos_old[2], pos_new[0], pos_new[2]
                tmp_x, tmp_z = x2 - x1, z2 - z1
                add_x = tmp_z * math.sin(-ang_old) + tmp_x * math.cos(-ang_old)
                add_z = tmp_z * math.cos(-ang_old) - tmp_x * math.sin(-ang_old)
                # 上下
                if abs(add_z) >= size_old[2] / 2 and abs(add_x) <= size_old[0] / 2:
                    if abs(add_z) <= (size_old[2] + size_new[2]) / 2 + 0.8:
                        if abs(ang_to_ang(ang_new - ang_old - math.pi / 2)) <= 0.1 or \
                                abs(ang_to_ang(ang_new - ang_old + math.pi / 2)) <= 0.1:
                            size_min = group_new['size_min'][:]
                            group_new['size'] = [size_new[2], size_new[1], size_new[0]]
                            group_new['size_min'] = [min(size_min[0], size_new[2]), size_min[1], min(size_min[2], size_new[0])]
                            size_new, size_min = group_new['size'][:], group_new['size_min'][:]
                            rest_x, rest_z = min(size_new[0] - size_min[0], 1), min(size_new[2] - size_min[2], 1)
                            group_new['size_rest'] = [rest_z / 2, rest_x / 2, rest_z / 2, rest_x / 2]
                            group_new['offset'] = [0, 0, 0]
                            ang_new = ang_old
                            rot_new = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                            group_new['rotation'] = rot_new
                # 左右
                elif abs(add_z) <= size_old[2] / 2 and abs(add_x) >= size_old[0] / 2:
                    if abs(add_x) <= (size_old[0] + size_new[0]) / 2 + 0.8:
                        if abs(ang_to_ang(ang_new - ang_old - 0)) <= 0.1 or \
                                abs(ang_to_ang(ang_new - ang_old - math.pi)) <= 0.1:
                            size_min = group_new['size_min'][:]
                            group_new['size'] = [size_new[2], size_new[1], size_new[0]]
                            group_new['size_min'] = [min(size_min[0], size_new[2]), size_min[1], min(size_min[2], size_new[0])]
                            size_new, size_min = group_new['size'][:], group_new['size_min'][:]
                            rest_x, rest_z = min(size_new[0] - size_min[0], 1), min(size_new[2] - size_min[2], 1)
                            group_new['size_rest'] = [rest_z / 2, rest_x / 2, rest_z / 2, rest_x / 2]
                            group_new['offset'] = [0, 0, 0]
                            ang_new = ang_old - math.pi / 2
                            rot_new = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                            group_new['rotation'] = rot_new

            box_new = compute_furniture_rect(size_new, pos_new, rot_new)
            min_x_2 = min(box_new[0], box_new[2], box_new[4], box_new[6])
            max_x_2 = max(box_new[0], box_new[2], box_new[4], box_new[6])
            min_z_2 = min(box_new[1], box_new[3], box_new[5], box_new[7])
            max_z_2 = max(box_new[1], box_new[3], box_new[5], box_new[7])

            # 避让
            if group_old['type'] in ['Meeting', 'Bed'] and group_new['type'] in ['Media', 'Dining']:
                pass
            # 远离
            elif min_x_2 >= max_x_1 - 0.001 or max_x_2 <= min_x_1 + 0.001 \
                    or min_z_2 >= max_z_1 - 0.001 or max_z_2 <= min_z_1 + 0.001:
                continue
            # 抛弃
            elif min_x_2 <= pos_old[0] <= max_x_2 and min_z_2 <= pos_old[2] <= max_z_2:
                group_dump.append(group_new)
                continue
            # 裁剪
            impact_1, impact_2 = [0, 0, 0, 0], [0, 0, 0, 0]
            # 上侧
            if pos_new[2] <= pos_old[2]:
                impact_1[0] = max_z_2 - min_z_1
                impact_1[2] = -(max_z_1 - min_z_1)
            # 下侧
            elif pos_new[2] > pos_old[2]:
                impact_1[2] = max_z_1 - min_z_2
                impact_1[0] = -(max_z_1 - min_z_1)
            # 左侧
            if pos_new[0] <= pos_old[0]:
                impact_1[1] = max_x_2 - min_x_1
                impact_1[3] = -(max_x_1 - min_x_1)
            # 右侧
            elif pos_new[0] > pos_old[0]:
                impact_1[3] = max_x_1 - min_x_2
                impact_1[1] = -(max_x_1 - min_x_1)

            # 裁剪
            if max(impact_1[0], impact_1[2]) / (max_z_1 - min_z_1) <= max(impact_1[1], impact_1[3]) / (max_x_1 - min_x_1):
                impact_d = max(impact_1[0], impact_1[2])
                if group_old['type'] in ['Meeting', 'Bed'] and group_new['type'] in ['Media', 'Dining']:
                    impact_pass, impact_rest = max(0.4 + impact_d, 0), 0.4
                    if group_old['type'] in ['Meeting'] and group_new['type'] in ['Media']:
                        impact_pass, impact_rest = max(0.8 + impact_d, 0), 0.4
                    elif group_old['type'] in ['Meeting'] and group_new['type'] in ['Dining']:
                        impact_pass, impact_rest = max(0.4 + impact_d, 0), 2.0
                        if impact_d >= min(3, (max_z_1 - min_z_1) * 0.5):
                            group_dump.append(group_new)
                            continue
                    if impact_pass <= 0:
                        continue
                    elif 0.4 <= impact_d <= 1.0:
                        impact_rest = 2.0
                        impact_main = min(max(max_z_1 - min_z_1 - impact_rest, 0), impact_pass)
                        impact_side = max(impact_pass - impact_main, 0)
                    elif group_new['type'] in ['Media']:
                        impact_rest = 0.4
                        impact_side = min(max(max_z_2 - min_z_2 - impact_rest, 0), impact_pass)
                        impact_main = max(impact_pass - impact_side, 0)
                    elif group_new['type'] in ['Dining']:
                        impact_rest = 2.0
                        impact_side = min(max(max_z_2 - min_z_2 - impact_rest, 0), impact_pass)
                        impact_main = max(impact_pass - impact_side, 0)
                    else:
                        impact_rest = 0.4
                        impact_side = min(max(max_z_2 - min_z_2 - impact_rest, 0), impact_pass)
                        impact_main = max(impact_pass - impact_side, 0)
                    if impact_1[0] > impact_1[2]:
                        impact_1, impact_2 = [impact_main, 0, 0, 0], [0, 0, impact_side, 0]
                    else:
                        impact_1, impact_2 = [0, 0, impact_main, 0], [impact_side, 0, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_old, impact_1)
                    resolve_bound_impaction(group_new, impact_2)
                elif group_old['type'] in ['Meeting'] and group_new['type'] in ['Rest']:
                    if impact_1[0] > impact_1[2]:
                        impact_1, impact_2 = [0, 0, 0, 0], [0, 0, impact_d, 0]
                    else:
                        impact_1, impact_2 = [0, 0, 0, 0], [impact_d, 0, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_new, impact_2)
                elif max_z_1 - min_z_1 > max_z_2 - min_z_2:
                    if impact_1[0] > impact_1[2]:
                        impact_1, impact_2 = [impact_d, 0, 0, 0], [0, 0, 0, 0]
                    else:
                        impact_1, impact_2 = [0, 0, impact_d, 0], [0, 0, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_old, impact_1)
                else:
                    if impact_1[0] > impact_1[2]:
                        impact_1, impact_2 = [0, 0, 0, 0], [0, 0, impact_d, 0]
                    else:
                        impact_1, impact_2 = [0, 0, 0, 0], [impact_d, 0, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_new, impact_2)
            else:
                impact_d = max(impact_1[1], impact_1[3])
                if group_old['type'] in ['Meeting', 'Bed'] and group_new['type'] in ['Media', 'Dining']:
                    impact_pass, impact_rest = max(0.4 + impact_d, 0), 0.4
                    if group_old['type'] in ['Meeting'] and group_new['type'] in ['Media']:
                        impact_pass, impact_rest = max(0.8 + impact_d, 0), 0.4
                    elif group_old['type'] in ['Meeting'] and group_new['type'] in ['Dining']:
                        impact_pass, impact_rest = max(0.4 + impact_d, 0), 2.0
                        if impact_d >= min(3, (max_x_1 - min_x_1) * 0.5):
                            group_dump.append(group_new)
                            continue
                    if impact_pass <= 0:
                        continue
                    if 0.4 <= impact_d <= 1.0:
                        impact_rest = 2.0
                        impact_main = min(max(max_x_1 - min_x_1 - impact_rest, 0), impact_pass)
                        impact_side = max(impact_pass - impact_main, 0)
                    elif group_new['type'] in ['Media']:
                        impact_rest = 0.4
                        impact_side = min(max(max_x_2 - min_x_2 - impact_rest, 0), impact_pass)
                        impact_main = max(impact_pass - impact_side, 0)
                    elif group_new['type'] in ['Dining']:
                        impact_rest = 2.0
                        impact_side = min(max(max_x_2 - min_x_2 - impact_rest, 0), impact_pass)
                        impact_main = max(impact_pass - impact_side, 0)
                    else:
                        impact_rest = 0.4
                        impact_side = min(max(max_x_2 - min_x_2 - impact_rest, 0), impact_pass)
                        impact_main = max(impact_pass - impact_side, 0)

                    if impact_1[1] > impact_1[3]:
                        impact_1, impact_2 = [0, impact_main, 0, 0], [0, 0, 0, impact_side]
                    else:
                        impact_1, impact_2 = [0, 0, 0, impact_main], [0, impact_side, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_old, impact_1)
                    resolve_bound_impaction(group_new, impact_2)
                elif group_old['type'] in ['Meeting'] and group_new['type'] in ['Rest']:
                    if impact_1[1] > impact_1[3]:
                        impact_1, impact_2 = [0, 0, 0, 0], [0, 0, 0, impact_d]
                    else:
                        impact_1, impact_2 = [0, 0, 0, 0], [0, impact_d, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_new, impact_2)
                elif max_x_1 - min_x_1 > max_x_2 - min_x_2:
                    if impact_1[1] > impact_1[3]:
                        impact_1, impact_2 = [0, impact_d, 0, 0], [0, 0, 0, 0]
                    else:
                        impact_1, impact_2 = [0, 0, 0, impact_d], [0, 0, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_old, impact_1)
                else:
                    if impact_1[1] > impact_1[3]:
                        impact_1, impact_2 = [0, 0, 0, 0], [0, 0, 0, impact_d]
                    else:
                        impact_1, impact_2 = [0, 0, 0, 0], [0, impact_d, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_new, impact_2)
        #
        for decor_idx, decor_new in enumerate(decor_list):
            pos_new, size_new = decor_new['position'][:], [abs(decor_new['size'][i] * decor_new['scale'][i]) / 100 for i in range(3)]
            box_new = compute_furniture_rect(size_new, decor_new['position'], decor_new['rotation'])
            min_x_2 = min(box_new[0], box_new[2], box_new[4], box_new[6])
            max_x_2 = max(box_new[0], box_new[2], box_new[4], box_new[6])
            min_z_2 = min(box_new[1], box_new[3], box_new[5], box_new[7])
            max_z_2 = max(box_new[1], box_new[3], box_new[5], box_new[7])
            # 远离
            if min_x_2 >= max_x_1 - 0.001 or max_x_2 <= min_x_1 + 0.001 \
                    or min_z_2 >= max_z_1 - 0.001 or max_z_2 <= min_z_1 + 0.001:
                continue
            # 抛弃
            if min_x_2 <= pos_old[0] <= max_x_2 and min_z_2 <= pos_old[2] <= max_z_2:
                group_dump.append(group_new)
                continue
            # 裁剪
            impact_1, impact_2 = [0, 0, 0, 0], [0, 0, 0, 0]
            # 上侧
            if pos_new[2] < pos_old[2]:
                impact_1[0] = max_z_2 - min_z_1
            # 下侧
            elif pos_new[2] > pos_old[2]:
                impact_1[2] = max_z_1 - min_z_2
            # 左侧
            if pos_new[0] < pos_old[0]:
                impact_1[1] = max_x_2 - min_x_1
            # 右侧
            elif pos_new[0] > pos_old[0]:
                impact_1[3] = max_x_1 - min_x_2

            # 裁剪
            if max(impact_1[0], impact_1[2]) / (max_z_1 - min_z_1) <= max(impact_1[1], impact_1[3]) / (max_x_1 - min_x_1):
                impact_d = max(impact_1[0], impact_1[2])
                if max_z_1 - min_z_1 > max_z_2 - min_z_2:
                    if impact_1[0] > impact_1[2]:
                        impact_1, impact_2 = [impact_d, 0, 0, 0], [0, 0, 0, 0]
                    else:
                        impact_1, impact_2 = [0, 0, impact_d, 0], [0, 0, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_old, impact_1)
            else:
                impact_d = max(impact_1[1], impact_1[3])
                if max_x_1 - min_x_1 > max_x_2 - min_x_2:
                    if impact_1[1] > impact_1[3]:
                        impact_1, impact_2 = [0, impact_d, 0, 0], [0, 0, 0, 0]
                    else:
                        impact_1, impact_2 = [0, 0, 0, impact_d], [0, 0, 0, 0]
                    # 调整
                    resolve_bound_impaction(group_old, impact_1)
    # 拥有处理
    for group_idx in range(len(group_list) - 1, -1, -1):
        group_one = group_list[group_idx]
        group_type, group_size = group_one['type'], group_one['size']
        if group_type in ['Armoire', 'Cabinet']:
            if group_size[0] >= 0.8:
                group_wear.append(group_one)
    # 抛弃处理
    for group_idx in range(len(group_list) - 1, -1, -1):
        group_one = group_list[group_idx]
        group_type, group_size = group_one['type'], group_one['size']
        if group_type in ['Armoire', 'Cabinet']:
            if group_size[0] <= 0.4 or group_size[2] < 0.1:
                group_dump.append(group_one)
            elif group_size[0] <= min(0.6, group_size[2]):
                group_dump.append(group_one)
            elif 0.2 < group_size[0] <= 0.6 and len(group_wear) > 0:
                group_one['type'] = 'Rest'
        elif group_type in ['Work', 'Rest']:
            if group_size[2] <= UNIT_WIDTH_DOOR + 0.01 and room_type in ['LivingRoom', 'LivingDiningRoom']:
                group_one['type'] = 'Cabinet'
            if group_size[0] <= 0.4 or group_size[2] < 0.1:
                group_dump.append(group_one)
    # 返回信息
    return group_dump


# 调整组合碰撞
def resolve_bound_impaction(group_one, impact_one):
    group_pos, group_ang = group_one['position'][:], rot_to_ang(group_one['rotation'])
    group_size, group_regulate = group_one['size'], [0, 0, 0, 0]
    if abs(ang_to_ang(group_ang - 0)) < 0.1:
        group_regulate = [-impact_one[0], -impact_one[1], -impact_one[2], -impact_one[3]]
    elif abs(ang_to_ang(group_ang - math.pi)) < 0.1:
        group_regulate = [-impact_one[2], -impact_one[3], -impact_one[0], -impact_one[1]]
    elif abs(ang_to_ang(group_ang + math.pi * 0.5)) < 0.1:
        group_regulate = [-impact_one[3], -impact_one[0], -impact_one[1], -impact_one[2]]
    elif abs(ang_to_ang(group_ang - math.pi * 0.5)) < 0.1:
        group_regulate = [-impact_one[1], -impact_one[2], -impact_one[3], -impact_one[0]]
    else:
        return
    # 重置尺寸
    group_one['size'][0] += group_regulate[1]
    group_one['size'][0] += group_regulate[3]
    group_one['size'][2] += group_regulate[0]
    group_one['size'][2] += group_regulate[2]
    group_one['size_min'][0] = min(group_one['size'][0], group_one['size_min'][0])
    group_one['size_min'][2] = min(group_one['size'][2], group_one['size_min'][2])
    # 重置位置
    tmp_x = (group_regulate[3] - group_regulate[1]) / 2
    tmp_z = (group_regulate[2] - group_regulate[0]) / 2
    add_x = tmp_z * math.sin(group_ang) + tmp_x * math.cos(group_ang)
    add_z = tmp_z * math.cos(group_ang) - tmp_x * math.sin(group_ang)
    group_one['position'][0] += add_x
    group_one['position'][2] += add_z


# 计算矩形顶点
def compute_furniture_bound(size, position, rotation, adjust=[0, 0, 0, 0]):
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
    return [x1, z1, x2, z2, x3, z3, x4, z4]


# 计算家具范围
def compute_furniture_scope(group_one, keep_list=[], room_type=''):
    group_type, group_size = group_one['type'], group_one['size']
    center_flag = 0
    if 'center' in group_one:
        center_flag = group_one['center']
    # 多家具功能区
    if group_type in ['Meeting', 'Bed', 'Media', 'Dining', 'Work', 'Rest', 'Bath', 'Toilet']:
        # 最小范围
        object_x_min, object_z_min, object_x_max, object_z_max = [100, 100, -100, -100]
        for object_one in keep_list:
            object_role = object_one['role']
            if object_role in ['rug', 'accessory']:
                continue
            origin_size, origin_scale = object_one['size'], object_one['scale']
            object_size = [origin_size[0] * origin_scale[0], origin_size[1] * origin_scale[1], origin_size[2] * origin_scale[2]]
            object_position, object_rotation = object_one['position'], object_one['rotation']
            if 'normal_position' in object_one:
                object_position = object_one['normal_position']
            if 'normal_rotation' in object_one:
                object_rotation = object_one['normal_rotation']
            object_size_norm = [abs(width_i / 100) for width_i in object_size]
            object_rect = compute_furniture_bound(object_size_norm, object_position, object_rotation)
            object_x_min = min(object_rect[0], object_rect[2], object_rect[4], object_rect[6], object_x_min)
            object_x_max = max(object_rect[0], object_rect[2], object_rect[4], object_rect[6], object_x_max)
            object_z_min = min(object_rect[1], object_rect[3], object_rect[5], object_rect[7], object_z_min)
            object_z_max = max(object_rect[1], object_rect[3], object_rect[5], object_rect[7], object_z_max)
        # 分组范围
        group_size, group_offset = group_one['size'], group_one['offset']
        group_x_min, group_x_max = -group_size[0] / 2 - group_offset[0], group_size[0] / 2 - group_offset[0]
        group_z_min, group_z_max = -group_size[2] / 2 - group_offset[2], group_size[2] / 2 - group_offset[2]
        # 计算范围
        scale_x, scale_z = 1, 1
        scale_x_1 = (object_x_min - group_x_min) / (object_x_max - object_x_min)
        scale_x_2 = (group_x_max - object_x_max) / (object_x_max - object_x_min)
        scale_z_1 = (object_z_min - group_z_min) / (object_z_max - object_z_min)
        scale_z_2 = (group_z_max - object_z_max) / (object_z_max - object_z_min)
        # 缩放范围
        if scale_x_1 < 0.01 < scale_x_2 and group_type in ['Dining', 'Work', 'Rest']:
            scale_x = 1 + scale_x_2
        elif scale_x_2 < 0.01 < scale_x_1 and group_type in ['Dining', 'Work', 'Rest']:
            scale_x = 1 + scale_x_1
        else:
            if scale_x_1 < scale_x_2:
                scale_x = 1 + scale_x_1
            else:
                scale_x = 1 + scale_x_2
        if scale_z_1 < 0.01 < scale_z_2:
            scale_z = 1 + scale_z_2
        elif scale_z_2 < 0.01 < scale_z_1:
            scale_z = 1 + scale_z_1
        else:
            if scale_z_1 < scale_z_2:
                scale_z = 1 + scale_z_1
            else:
                scale_z = 1 + scale_z_2
        if scale_z < 1.0:
            scale_z = 1.0
        for object_one in group_one['obj_list']:
            size_cur = [object_one['size'][i] * object_one['scale'][i] for i in range(3)]
            size_max = size_cur[:]
            size_min = [size_cur[i] * 0.8 * 0.8 for i in range(3)]
            # 调整
            if object_one['role'] in ['sofa', 'bed', 'table']:
                size_max[0] = size_cur[0] * scale_x * 1.2
                size_max[1] = size_cur[1] * 1.2
                size_max[2] = size_cur[2] * scale_z * 1.2
            elif object_one['role'] in ['shower']:
                size_max[0] = size_cur[0] * min(scale_x, 2)
                size_max[1] = size_cur[1] * 1.2
                size_max[2] = size_cur[2] * min(scale_z, 2)
            else:
                size_max[0] = size_cur[0] * min(scale_x, scale_z)
                size_max[1] = size_cur[1] * 1.2
                size_max[2] = size_cur[2] * min(scale_x, scale_z)
            if object_one['role'] == 'table':
                size_min[0] = size_cur[0] * 0.5
                size_min[2] = size_cur[2] * 0.5
                if center_flag >= 1:
                    size_max[0] *= 1.2
                    size_max[2] *= 1.2
            # 调整
            if size_max[0] < size_cur[0]:
                size_max[0] = size_cur[0]
            if size_max[1] < size_cur[1]:
                size_max[1] = size_cur[1]
            if size_max[2] < size_cur[2]:
                size_max[2] = size_cur[2]
            # 赋值
            object_one['size_max'] = size_max[:]
            object_one['size_min'] = size_min[:]
            object_one['size_cur'] = size_cur[:]
    # 单家具功能区
    elif group_type in GROUP_RULE_FUNCTIONAL:
        for object_one in group_one['obj_list']:
            size_cur = [object_one['size'][i] * object_one['scale'][i] for i in range(3)]
            size_max = [group_size[i] * 100 for i in range(3)]
            size_min = [size_cur[i] * 0.8 for i in range(3)]
            # 调整
            if size_max[1] < UNIT_HEIGHT_SHELF_MIN * 100:
                size_max[1] *= 1.1
            if size_max[2] < size_cur[2] * 1.5:
                size_max[2] = size_cur[2] * 1.5
            size_min[2] = size_cur[2] * 0.5
            if size_cur[0] > size_max[0]:
                size_cur[0] = size_max[0]
            if size_cur[2] > size_max[2]:
                size_cur[2] = size_max[2]
            if size_max[0] > size_cur[0]:
                size_cur[0] = size_max[0]
            # 调整
            if size_max[0] < size_cur[0]:
                size_max[0] = size_cur[0]
            if size_max[1] < size_cur[1]:
                size_max[1] = size_cur[1]
            if size_max[2] < size_cur[2]:
                size_max[2] = size_cur[2]
            # 赋值
            object_one['size_max'] = size_max[:]
            object_one['size_min'] = size_min[:]
            object_one['size_cur'] = size_cur[:]
    # 单配饰功能区
    elif group_type in GROUP_RULE_DECORATIVE:
        for object_idx, object_one in enumerate(group_one['obj_list']):
            size_cur = [object_one['size'][i] * object_one['scale'][i] for i in range(3)]
            size_max = size_cur[:]
            size_min = [size_cur[i] * 0.5 for i in range(3)]
            # 调整
            if group_type in ['Wall']:
                size_max = [size_cur[i] * 1.5 for i in range(3)]
            elif group_type in ['Ceiling']:
                size_max = [size_cur[i] * 2.0 for i in range(3)]
                if room_type in ['Balcony', 'Terrace', 'Lounge', 'LaundryRoom',
                                 'Hallway', 'Aisle', 'Corridor', 'Stairwell']:
                    size_max = [size_cur[i] * 1.5 for i in range(3)]
                if object_idx >= 1:
                    size_max = [size_cur[i] * 1.2 for i in range(3)]
                    size_max[1] = size_cur[1]
            elif group_type in ['Window']:
                size_max = [size_cur[i] * 2.0 for i in range(3)]
                size_min = size_cur[:]
                if 150 < size_min[0] < 200:
                    size_min[0] = 200
                if 150 < size_min[1] < 200:
                    size_min[1] = 200
                if 150 < size_max[0] < 200:
                    size_cur[0] = 200
                if 150 < size_max[1] < 200:
                    size_cur[1] = 200
            # 赋值
            object_one['size_max'] = size_max[:]
            object_one['size_min'] = size_min[:]
            object_one['size_cur'] = size_cur[:]


# 判断家具方位
def compute_furniture_locate(x1, z1, x2, z2, angle, width=1.0, depth=1.0, delta=0.1):
    # 左侧
    tmp_x, tmp_z = -width / 2, 0
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_left = x1 + add_x
    z1_left = z1 + add_z
    dis_left = (x1_left - x2) * (x1_left - x2) + (z1_left - z2) * (z1_left - z2)
    # 右侧
    tmp_x, tmp_z = width / 2, 0
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_right = x1 + add_x
    z1_right = z1 + add_z
    dis_right = (x1_right - x2) * (x1_right - x2) + (z1_right - z2) * (z1_right - z2)

    # 后侧
    tmp_x, tmp_z = 0, -depth / 2
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_back = x1 + add_x
    z1_back = z1 + add_z
    dis_back = (x1_back - x2) * (x1_back - x2) + (z1_back - z2) * (z1_back - z2)
    # 前侧
    tmp_x, tmp_z = 0, depth / 2
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_front = x1 + add_x
    z1_front = z1 + add_z
    dis_front = (x1_front - x2) * (x1_front - x2) + (z1_front - z2) * (z1_front - z2)

    # 返回
    flag_left, flag_back = 0, 0
    if dis_left < dis_right - delta:
        flag_left = 1
    elif dis_right < dis_left - delta:
        flag_left = -1
    if dis_back < dis_front - delta * 2:
        flag_back = 1
    elif dis_front < dis_back - delta * 2:
        flag_back = -1
    return flag_left, flag_back


# 计算家具距离
def compute_furniture_length(x1, y1, x2, y2):
    if abs(x2 - x1) < 0.001:
        if y2 >= y1:
            length = y2 - y1
            angle = 0
        else:
            length = y1 - y2
            angle = math.pi
    elif abs(y2 - y1) < 0.001:
        if x2 >= x1:
            length = x2 - x1
            angle = math.pi / 2
        else:
            length = x1 - x2
            angle = math.pi / 2 * 3
    else:
        length = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        angle = math.acos((y2 - y1) / length)
        if x2 - x1 <= -0.001:
            angle = math.pi * 2 - angle
    # 规范
    if angle > math.pi * 2:
        angle -= math.pi * 2
    elif angle < -math.pi * 2:
        angle += math.pi * 2
    # 规范
    if angle > math.pi:
        angle -= math.pi * 2
    elif angle < -math.pi:
        angle += math.pi * 2
    return length, angle


# 计算家具靠边
def compute_furniture_aside(region_dir, object_one, group_size, group_offset, group_neighbor):
    object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
    origin_size, origin_scale = object_one['size'], object_one['scale']
    object_size = [abs(origin_size[i] * origin_scale[i] / 100) for i in range(3)]
    origin_position, origin_rotation = object_one['position'][:], object_one['rotation']
    if 'normal_position' in object_one:
        origin_position = object_one['normal_position'][:]
    if 'normal_rotation' in object_one:
        origin_rotation = object_one['normal_rotation']
    origin_angle = rot_to_ang(origin_rotation)
    if object_role in ['bath'] and object_size[0] + object_size[2] < 1.0:
        object_role = 'shower'
    # 花洒
    if object_role in ['shower']:
        if group_offset[0] < -0.2 and abs(ang_to_ang(origin_angle - math.pi / 2)) <= 0.1:
            if region_dir == 1:
                origin_angle = 0 - math.pi / 2
                origin_position[0] = -group_offset[0] * 2
            elif region_dir == 0:
                origin_angle = 0
                origin_position[0] = -group_offset[0]
                origin_position[2] = -group_size[2] / 2 + object_size[2] / 2
        elif group_offset[0] > 0.2 and abs(ang_to_ang(origin_angle + math.pi / 2)) <= 0.1:
            if region_dir == -1:
                origin_angle = 0 + math.pi / 2
                origin_position[0] = -group_offset[0] * 2
            elif region_dir == 0:
                origin_angle = 0
                origin_position[0] = -group_offset[0]
                origin_position[2] = -group_size[2] / 2 + object_size[2] / 2
        elif abs(origin_position[0] + group_offset[0]) > min(group_size[0] / 4, 0.2) and group_size[0] < 1.5:
            origin_position[0] = -group_offset[0]
        elif abs(group_size[0] - group_size[2]) < 0.1 and group_size[0] < 1.5:
            origin_position[0] = -group_offset[0]
        elif min(group_size[0], group_size[2]) > 0.5 and max(group_size[0], group_size[2]) > 1.5:
            origin_position[0] = -group_offset[0]
    # 浴缸
    elif object_role in ['bath']:
        if region_dir >= 1 and abs(origin_angle - math.pi / 2) < 0.01:
            origin_angle *= -1
        elif region_dir <= -1 and abs(origin_angle + math.pi / 2) < 0.01:
            origin_angle *= -1
    # 浴门
    elif object_role in ['screen']:
        object_cate = get_furniture_cate(object_id)
        object_turn = 0
        # 更新
        if object_cate == '':
            if object_size[0] > object_size[2] * 5 > 0:
                object_cate = 'screen_I'
            elif object_size[0] > object_size[2] * 2 > 1.0:
                object_cate = 'screen_U'
            elif abs(ang_to_ang(origin_angle + math.pi * 0.50)) <= 0.1:
                object_cate = 'screen_L'
            elif abs(ang_to_ang(origin_angle - math.pi * 0.50)) <= 0.1:
                object_cate = 'screen_R'
            elif abs(ang_to_ang(origin_angle + math.pi * 0.25)) <= 0.1:
                object_cate = 'screen_U'
                object_turn = math.pi * 0.25
            elif abs(ang_to_ang(origin_angle - math.pi * 0.25)) <= 0.1:
                object_cate = 'screen_U'
                object_turn = math.pi * 0.25
            elif region_dir <= -1:
                object_cate = 'screen_L'
            elif region_dir >= 1:
                object_cate = 'screen_R'
            else:
                object_cate = 'screen_U'
        # 浴门替换
        if object_cate in ['screen_L', 'screen_R', 'screen_U', 'screen_V'] \
                and 0.5 < group_size[0] < group_size[2] > 1.5:
            object_new = copy_object_by_id(SCREEN_I_ID)
            object_cate = 'screen_I'
            object_one['id'] = object_new['id']
            object_one['type'], object_one['style'] = object_new['type'], object_new['style']
            object_one['size'], object_one['scale'] = object_new['size'][:], [1, 1, 1]
            origin_size, origin_scale = object_one['size'], object_one['scale']
            object_size = [abs(origin_size[i] * origin_scale[i] / 100) for i in range(3)]
        elif object_cate in ['screen_I', 'screen_U', 'screen_V'] and abs(group_size[0] - group_size[2]) < 0.4 \
                and 0.5 < min(group_size[0], group_size[2]) < max(group_size[0], group_size[2]) < 1.5:
            object_new = copy_object_by_id(SCREEN_L_ID)
            object_cate = 'screen_L'
            object_one['id'] = object_new['id']
            object_one['type'], object_one['style'] = object_new['type'], object_new['style']
            object_one['size'], object_one['scale'] = object_new['size'][:], [1, 1, 1]
            origin_size, origin_scale = object_one['size'], object_one['scale']
            object_size = [abs(origin_size[i] * origin_scale[i] / 100) for i in range(3)]

        # 浴门布局
        if region_dir == 0 and object_cate in ['screen_L', 'screen_R']:
            if len(group_offset) >= 3 and group_offset[0] > 0.1:
                region_dir = 1
            elif len(group_offset) >= 3 and group_offset[0] < -0.1:
                region_dir = -1
        if not region_dir == 0:
            if len(group_neighbor) >= 4 and group_neighbor[2] > 1 and group_size[0] > group_size[2] * 1.5:
                region_dir = 0
        # 靠左
        if region_dir <= -1:
            if 'I' in object_cate or object_size[0] > object_size[2] * 5 > 0:
                expand_scale_x = min((group_size[2] - 0.04) / (origin_size[0] / 100), 2.0)
                expand_scale_z = min(expand_scale_x, 1)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                object_width = origin_size[0] * expand_scale_x / 100
                object_depth = origin_size[2] * expand_scale_z / 100
                origin_position[0] = min(group_size[0] / 2 - 0.1, 1.0) - group_offset[0]
                origin_position[2] = -group_size[2] / 2 + object_width * 0.5 - group_offset[2]
                origin_angle = math.pi / 2
            elif 'L' in object_cate or 'U' in object_cate:
                expand_scale_x = min(max(group_size[0] / (origin_size[0] / 100), 0.5), 1.0)
                expand_scale_z = min(max(group_size[2] / (origin_size[2] / 100), 0.5), 1.0)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                object_width = origin_size[0] * expand_scale_x / 100
                object_depth = origin_size[2] * expand_scale_z / 100
                origin_position[0] = -group_size[0] / 2 + object_width * 0.5 - group_offset[0]
                origin_position[2] = -group_size[2] / 2 + max(object_depth * 0.5, 0.3) - group_offset[2]
                origin_angle = 0
                if 'U' in object_cate:
                    origin_position[0] = 0 - group_offset[0]
                    if object_turn > 0.1:
                        origin_position[2] = -group_size[2] / 2 + max(object_depth * 0.5, 0.8) - group_offset[2]
                        origin_angle += object_turn
            elif 'R' in object_cate:
                expand_scale_x = min(max(group_size[2] / (origin_size[0] / 100), 0.5), 1.0)
                expand_scale_z = min(max(group_size[0] / (origin_size[2] / 100), 0.5), 1.0)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                object_width = origin_size[0] * expand_scale_x / 100
                object_depth = origin_size[2] * expand_scale_z / 100
                origin_position[0] = -group_size[0] / 2 + object_depth * 0.5 - group_offset[0]
                origin_position[2] = -group_size[2] / 2 + max(object_width * 0.5, 0.3) - group_offset[2]
                origin_angle = math.pi * 0.5
            elif 'V' in object_cate:
                expand_scale_x = min(max(group_size[0] / (origin_size[0] / 100) * 1.2, 0.5), 1.2)
                expand_scale_z = min(max(group_size[2] / (origin_size[2] / 100) * 1.2, 0.5), 1.2)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                origin_position[0] = - group_offset[0]
                origin_position[2] = - group_offset[2]
                origin_angle = math.pi * 0.5 * 0.5
        # 靠右
        elif region_dir >= 1:
            if 'I' in object_cate or object_size[0] > object_size[2] * 5 > 0:
                expand_scale_x = min(group_size[2] / (origin_size[0] / 100), 2.0)
                expand_scale_z = min(expand_scale_x, 1)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                object_width = origin_size[0] * expand_scale_x / 100
                object_depth = origin_size[2] * expand_scale_z / 100
                origin_position[0] = -min(group_size[0] / 2 - 0.1, 1.0) - group_offset[0]
                origin_position[2] = -group_size[2] / 2 + object_width * 0.5 - group_offset[2]
                origin_angle = -math.pi / 2
            elif 'L' in object_cate:
                expand_scale_x = min(max(group_size[2] / (origin_size[0] / 100), 0.5), 1.0)
                expand_scale_z = min(max(group_size[0] / (origin_size[2] / 100), 0.5), 1.0)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                object_width = origin_size[0] * expand_scale_x / 100
                object_depth = origin_size[2] * expand_scale_z / 100
                origin_position[0] = group_size[0] / 2 - object_depth * 0.5 - group_offset[0]
                origin_position[2] = -group_size[2] / 2 + max(object_width * 0.5, 0.3) - group_offset[2]
                origin_angle = -math.pi * 0.5
            elif 'R' in object_cate or 'U' in object_cate:
                expand_scale_x = min(max(group_size[0] / (origin_size[0] / 100), 0.5), 1.0)
                expand_scale_z = min(max(group_size[2] / (origin_size[2] / 100), 0.5), 1.0)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                object_width = origin_size[0] * expand_scale_x / 100
                object_depth = origin_size[2] * expand_scale_z / 100
                origin_position[0] = group_size[0] / 2 - object_width * 0.5 - group_offset[0]
                origin_position[2] = -group_size[2] / 2 + max(object_depth * 0.5, 0.3) - group_offset[2]
                origin_angle = 0
                if 'U' in object_cate:
                    origin_position[0] = 0 - group_offset[0]
                    if object_turn > 0.1:
                        origin_position[2] = -group_size[2] / 2 + max(object_depth * 0.5, 0.8) - group_offset[2]
                        origin_angle -= object_turn
            elif 'V' in object_cate:
                expand_scale_x = min(max(group_size[0] / (origin_size[0] / 100) * 1.2, 0.5), 1.2)
                expand_scale_z = min(max(group_size[2] / (origin_size[2] / 100) * 1.2, 0.5), 1.2)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                origin_position[0] = - group_offset[0]
                origin_position[2] = - group_offset[2]
                origin_angle = -math.pi * 0.5 * 0.5
        # 居中
        else:
            if 'I' in object_cate or 'V' in object_cate or object_size[0] > object_size[2] * 5 > 0:
                expand_scale_x = min(max(group_size[0] / (origin_size[0] / 100), 0.5), 1.5)
                expand_scale_z = min(expand_scale_x, 1.2)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                origin_position[0] = 0 - group_offset[0]
                origin_position[2] = -group_size[2] / 2 + min(group_size[2], 1.8) - min(object_size[2] / 2, 0.1) - group_offset[2]
                origin_angle = 0
            elif 'L' in object_cate or 'R' in object_cate or 'U' in object_cate:
                expand_scale_x = min(max(group_size[0] / (origin_size[0] / 100), 0.5), 1.5)
                expand_scale_z = min(expand_scale_x, 1.2)
                object_one['scale'][0] = expand_scale_x
                object_one['scale'][2] = expand_scale_z
                object_width = origin_size[0] * expand_scale_x / 100
                object_depth = origin_size[2] * expand_scale_z / 100
                origin_position[0] = 0 - group_offset[0]
                origin_position[2] = -group_size[2] / 2 + max(object_depth * 0.5, 0.3) - group_offset[2]
                origin_angle = 0
    # 返回
    return origin_position, origin_angle


# 处理电视切换
def replace_furniture_media(object_one, object_new, group_one):
    if len(object_new) <= 0:
        object_new = copy_object_by_id(MEDIA_WALL_ID)
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    object_one['id'] = object_new['id']
    object_one['type'] = object_new['type']
    object_one['style'] = object_new['style']
    object_one['size'] = object_new['size'][:]
    object_one['scale'] = [abs(object_size[i] / object_one['size'][i]) * 100 for i in range(3)]
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    origin_position, origin_rotation = object_one['position'][:], object_one['rotation']
    if 'normal_position' in object_one:
        origin_position = object_one['normal_position'][:]
    if 'normal_rotation' in object_one:
        origin_rotation = object_one['normal_rotation']
    origin_angle = rot_to_ang(origin_rotation)
    offset_position = [0, 0, 0]
    if 'offset_position' in object_one:
        offset_position = object_one['offset_position']
    if 'TV - wall-attached' in object_one['type'] and origin_position[1] < 0.75:
        origin_position[1] = 0.75
    # 组合
    group_size, group_offset = group_one['size'], group_one['offset']
    group_position, group_rotation = group_one['position'], group_one['rotation']
    group_angle = rot_to_ang(group_rotation)
    # 位置
    origin_position[2] = -group_size[2] / 2 - group_offset[2] + object_size[2] / 2 + 0.001
    tmp_x = -group_offset[0] / 2 + origin_position[0] + offset_position[0]
    tmp_y = group_offset[1] + origin_position[1] + offset_position[1]
    tmp_z = group_offset[2] + origin_position[2] + offset_position[2]
    add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
    add_y = tmp_y
    add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
    furniture_position = [group_position[0] + add_x, group_position[1] + add_y, group_position[2] + add_z]
    object_one['position'] = furniture_position
    object_one['normal_position'] = origin_position[:]
    # 朝向
    furniture_angle = group_angle + origin_angle
    furniture_rotation = [0, math.sin(furniture_angle / 2), 0, math.cos(furniture_angle / 2)]
    object_one['rotation'] = furniture_rotation
    object_one['normal_rotation'] = [0, math.sin(origin_angle / 2), 0, math.cos(origin_angle / 2)]
    # 标志
    group_one['adjust'] = 1


# 计算家具复制
def resolve_furniture_copy(object_list, group_left, group_right, group_one={}, group_role=['side table']):
    group_main = {}
    left_list, right_list, face_list = [], [], []
    if 'side table' in group_role:
        group_role.append('side lamp')
        group_role.append('side plant')
    group_table, group_table_move = {}, 0
    for object_one in object_list:
        object_id, object_type, object_role = object_one['id'], object_one['type'], object_one['role']
        if 'obj_main' in group_one and group_one['obj_main'] == object_id:
            group_main = object_one
        if object_role in ['table'] and 'normal_position' in object_one:
            origin_position = object_one['normal_position']
            group_table_move = origin_position[0]
        if object_role in group_role and 'normal_position' in object_one:
            origin_position = object_one['normal_position']
            if origin_position[0] < 0:
                left_list.append(object_one)
            elif origin_position[0] > 0:
                right_list.append(object_one)
    if len(group_main) <= 0 and len(object_list) > 0:
        group_main = object_list[0]
    # 左拐右拐
    main_size = [abs(group_main['size'][i] * group_main['scale'][i]) / 100 for i in range(3)]
    left_flag, right_flag = False, False
    if 'type' in group_main:
        object_type = group_main['type']
        if 'left corner sofa' in object_type:
            left_flag = True
        elif 'right corner sofa' in object_type:
            right_flag = True
        elif 'type U sofa' in object_type:
            left_flag, right_flag = True, True
        elif 'type L sofa' in object_type:
            left_flag, right_flag = True, True
        elif 'sofa' in object_type and main_size[2] > 1.5:
            left_flag, right_flag = True, True
        elif 'bed' in object_type:
            left_flag, right_flag = True, True
    face_delta, face_shift = 0.02, 0.00
    if len(left_list) > 0 and len(right_list) <= 0:
        object_left = left_list[0]
        object_role = object_left['role']
        object_width = abs(object_left['size'][0] * object_left['scale'][0]) / 100
        object_depth = abs(object_left['size'][2] * object_left['scale'][2]) / 100
        if (group_right >= min(object_width, object_depth) - face_delta and not right_flag) or \
                (UNIT_WIDTH_DOOR > group_right > 0.3 > group_left and 'side sofa' in group_role) or \
                (group_right >= max(object_width, object_depth, group_left + 0.2) and 'side table' in group_role):
            if 'normal_position' in object_left:
                object_pos = object_left['normal_position']
                if object_role in ['side table']:
                    if object_pos[2] < abs(object_left['size'][2] * object_left['scale'][2] / 100):
                        face_list = left_list
                elif object_role in ['side sofa']:
                    if right_flag and group_right > group_left:
                        face_list = left_list
                        face_shift = object_pos[0] + min(max(object_width, object_depth), 1.0) / 2 + main_size[0] / 2
                    elif group_right - group_table_move > group_left:
                        face_list = left_list
                else:
                    face_list = left_list
    elif len(left_list) <= 0 and len(right_list) > 0:
        object_right = right_list[0]
        object_role = object_right['role']
        object_width = abs(object_right['size'][0] * object_right['scale'][0]) / 100
        object_depth = abs(object_right['size'][2] * object_right['scale'][2]) / 100
        if (group_left >= min(object_width, object_depth) - face_delta and not left_flag) or \
                (UNIT_WIDTH_DOOR > group_left > 0.3 > group_right and 'side sofa' in group_role) or \
                (group_left >= max(object_width, object_depth, group_right + 0.2) and 'side table' in group_role):
            if 'normal_position' in object_right:
                object_pos = object_right['normal_position']
                if object_role in ['side table']:
                    if object_pos[2] < abs(object_right['size'][2] * object_right['scale'][2] / 100):
                        face_list = right_list
                elif object_role in ['side sofa']:
                    if left_flag and group_left > group_right:
                        face_list = right_list
                        face_shift = object_pos[0] - min(max(object_width, object_depth), 1.0) / 2 - main_size[0] / 2
                    elif group_left + group_table_move > group_right:
                        face_list = right_list
                else:
                    face_list = right_list
    # 移动
    copy_list = []
    if len(left_list) > 0 and len(right_list) <= 0 and len(face_list) > 0 and right_flag and face_shift > 0.01:
        copy_list = compute_furniture_copy(face_list, object_list, group_one, group_main, face_shift / 2)
    elif len(left_list) <= 0 and len(right_list) > 0 and len(face_list) > 0 and left_flag and face_shift < -0.01:
        copy_list = compute_furniture_copy(face_list, object_list, group_one, group_main, face_shift / 2)
    # 复制
    else:
        copy_list = compute_furniture_copy(face_list, object_list, group_one, group_main, group_table_move)
    return copy_list, left_list, right_list


# 处理家具交换
def resolve_furniture_swap(group_one, group_side={}):
    group_type = group_one['type']
    if group_type not in ['Meeting', 'Bed']:
        return
    swap_flag, flag_left, flag_back = False, 0, 0
    neighbor_rest, neighbor_base, neighbor_more = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
    if 'size_rest' in group_one:
        neighbor_rest = group_one['size_rest'][:]
    if 'neighbor_base' in group_one:
        neighbor_base = group_one['neighbor_base'][:]
    if 'neighbor_more' in group_one:
        neighbor_more = group_one['neighbor_more'][:]
    if group_type in ['Bed']:
        if len(group_side) > 0:
            x1, z1 = group_one['position'][0], group_one['position'][2]
            x2, z2 = group_side['position'][0], group_side['position'][2]
            group_angle = rot_to_ang(group_one['rotation'])
            group_width, group_depth = group_one['size'][0], group_one['size'][2]
            flag_left, flag_back = compute_furniture_locate(x1, z1, x2, z2, group_angle, group_width, group_depth)
        if neighbor_rest[3] > neighbor_rest[1] + 0.1:
            if neighbor_base[1] < 0.4 and flag_left >= 1:
                swap_flag = True
            elif neighbor_base[3] > 0.4 > neighbor_base[1] * 2:
                swap_flag = True
        elif neighbor_rest[1] > neighbor_rest[3] + 0.1:
            if neighbor_base[3] < 0.4 and flag_left <= -1:
                swap_flag = True
            elif neighbor_base[1] > 0.4 > neighbor_base[3] * 2:
                swap_flag = True
    elif group_type in ['Meeting']:
        group_offset, region_middle = [0, 0, 0], 0.5
        if 'offset' in group_one:
            group_offset = group_one['offset']
        if 'region_middle' in group_one:
            region_middle = group_one['region_middle']
        if group_offset[0] > 0.0 + 0.1 and region_middle > 0.5 + 0.1:
            swap_flag = True
        if group_offset[0] < 0.0 - 0.1 and region_middle < 0.5 - 0.1:
            swap_flag = True
    #
    if swap_flag:
        group_one['offset'][0] *= -1
        group_one['size_rest'] = [neighbor_rest[0], neighbor_rest[3], neighbor_rest[2], neighbor_rest[1]]
        group_position, group_angle = group_one['position'], rot_to_ang(group_one['rotation'])
        group_offset, object_list = group_one['offset'], group_one['obj_list']
        for object_idx, object_one in enumerate(object_list):
            # 角色
            object_role = object_one['role']
            # 位置
            origin_position, origin_rotation = object_one['position'][:], object_one['rotation']
            if 'normal_position' in object_one:
                origin_position = object_one['normal_position'][:]
            if 'normal_rotation' in object_one:
                origin_rotation = object_one['normal_rotation']
            origin_angle = rot_to_ang(origin_rotation)
            offset_position = [0, 0, 0]
            if 'offset_position' in object_one:
                offset_position = object_one['offset_position']
            # 调换
            if object_role in ['rug']:
                continue
            else:
                origin_position[0] *= -1
                origin_angle *= -1
            # 位置
            tmp_x = group_offset[0] + origin_position[0] + offset_position[0]
            tmp_y = group_offset[1] + origin_position[1] + offset_position[1]
            tmp_z = group_offset[2] + origin_position[2] + offset_position[2]
            add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
            add_y = tmp_y
            add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
            furniture_position = [group_position[0] + add_x, group_position[1] + add_y, group_position[2] + add_z]
            if object_role in ['sofa', 'bed']:
                pos_old, pos_new = object_one['position'], furniture_position
                pos_dlt = [pos_new[0] - pos_old[0], pos_new[1] - pos_old[1], pos_new[2] - pos_old[2]]
                group_one['swap'] = 1
                group_one['swap_move'] = pos_dlt
            object_one['position'] = furniture_position
            object_one['normal_position'] = origin_position[:]
            # 朝向
            furniture_angle = group_angle + origin_angle
            furniture_rotation = [0, math.sin(furniture_angle / 2), 0, math.cos(furniture_angle / 2)]
            object_one['rotation'] = furniture_rotation
            object_one['normal_rotation'] = [0, math.sin(origin_angle / 2), 0, math.cos(origin_angle / 2)]


# 计算家具复制
def compute_furniture_copy(face_list, object_list, group_info, group_main, table_move=0):
    copy_list = []
    for object_face in face_list:
        object_type, object_role = '', ''
        if 'type' in object_face:
            object_type = object_face['type']
        if 'role' in object_face:
            object_role = object_face['role']
        if 'floor lamp' in object_type:
            continue

        # 复制对面
        object_copy = {}
        if len(object_face) > 0:
            object_copy = object_face.copy()
            object_copy['size'] = object_face['size'][:]
            object_copy['scale'] = object_face['scale'][:]
            object_copy['normal_position'] = object_face['normal_position'][:]
            object_copy['normal_rotation'] = object_face['normal_rotation'][:]
            object_copy['normal_position'][0] *= -1
            object_copy['normal_rotation'][1] *= -1
            if object_role in ['side sofa']:
                object_copy['normal_position'][0] += table_move * 2
            if 'relate_position' in object_face:
                object_copy['relate_position'] = object_face['relate_position'][:]
            if 'adjust_position' in object_face:
                object_copy['adjust_position'] = object_face['adjust_position'][:]
                object_copy['adjust_position'][0] *= -1
            object_copy['position'] = object_copy['normal_position'][:]
            object_copy['rotation'] = object_copy['normal_rotation'][:]
            # 调整位置
            if len(group_main) > 0 and 'origin_position' in group_main:
                group_position, group_angle = group_main['origin_position'], rot_to_ang(group_main['origin_rotation'])
                group_offset = [0, 0, 0]
                origin_position, origin_angle = object_copy['normal_position'], rot_to_ang(object_copy['normal_rotation'])
                tmp_x = group_offset[0] + origin_position[0]
                tmp_y = group_offset[1] + origin_position[1]
                tmp_z = group_offset[2] + origin_position[2]
            elif len(group_info) > 0:
                group_position, group_angle = group_info['position'], rot_to_ang(group_info['rotation'])
                group_offset = group_info['offset']
                origin_position, origin_angle = object_copy['normal_position'], rot_to_ang(object_copy['normal_rotation'])
                tmp_x = group_offset[0] + origin_position[0]
                tmp_y = group_offset[1] + origin_position[1]
                tmp_z = group_offset[2] + origin_position[2]
            add_x = tmp_z * math.sin(group_angle) + tmp_x * math.cos(group_angle)
            add_y = tmp_y
            add_z = tmp_z * math.cos(group_angle) - tmp_x * math.sin(group_angle)
            furniture_position = [group_position[0] + add_x, group_position[1] + add_y, group_position[2] + add_z]
            furniture_angle = group_angle + origin_angle
            furniture_rotation = [0, math.sin(furniture_angle / 2), 0, math.cos(furniture_angle / 2)]
            object_copy['origin_position'] = furniture_position
            object_copy['origin_rotation'] = furniture_rotation
            copy_list.append(object_copy)
        # 复制装饰
        if len(object_face) > 0 and len(object_copy) > 0:
            for object_one in object_list:
                if object_one['role'] == 'accessory' and object_one['relate'] == object_face['id']:
                    if 'relate_position' in object_one and len(object_one['relate_position']) >= 3:
                        relate_position = object_one['relate_position']
                        origin_position = object_face['position']
                        if 'origin_position' in object_face:
                            origin_position = object_face['origin_position']
                        if abs(relate_position[0] - origin_position[0]) >= 0.5:
                            continue
                        if abs(relate_position[2] - origin_position[2]) >= 0.5:
                            continue
                        object_copy = object_one.copy()
                        object_copy['size'] = object_one['size'][:]
                        object_copy['scale'] = object_one['scale'][:]
                        object_copy['position'] = object_one['position'][:]
                        object_copy['rotation'] = object_one['rotation'][:]
                        object_copy['normal_position'] = object_one['normal_position'][:]
                        object_copy['normal_rotation'] = object_one['normal_rotation'][:]
                        object_copy['normal_position'][0] *= -1
                        object_copy['normal_rotation'][1] *= -1
                        if object_role in ['side sofa']:
                            object_copy['normal_position'][0] += table_move * 2
                        object_copy['relate_position'] = object_copy['origin_position'][:]
                        if 'adjust_position' in object_one:
                            object_copy['adjust_position'] = object_one['adjust_position'][:]
                            object_copy['adjust_position'][0] *= -1
                    copy_list.append(object_copy)
    return copy_list


# 计算配饰保持
def compute_accessory_keep(accessory_list):
    accessory_keep, accessory_dump = [], []
    accessory_lamp = True
    if accessory_lamp:
        for accessory_one in accessory_list:
            if 'type' in accessory_one and 'lamp' in accessory_one['type']:
                accessory_keep.append(accessory_one)
            else:
                accessory_dump.append(accessory_one)
    else:
        accessory_dict = {}
        for accessory_one in accessory_list:
            accessory_y = str(round(accessory_one['position'][1] + 0.05, 1))
            if accessory_y not in accessory_dict:
                accessory_dict[accessory_y] = []
            accessory_dict[accessory_y].append(accessory_one)

        for accessory_key, accessory_val in accessory_dict.items():
            if len(accessory_val) > len(accessory_keep):
                for accessory_one in accessory_keep:
                    accessory_dump.append(accessory_one)
                accessory_keep = accessory_val
            else:
                for accessory_one in accessory_val:
                    accessory_dump.append(accessory_one)
    return accessory_keep, accessory_dump


# 计算组合参数
def compute_group_param(group_one, keep_size=False):
    group_type, object_list = group_one['type'], group_one['obj_list']
    if group_type not in GROUP_RULE_FUNCTIONAL:
        return
    if len(object_list) <= 0:
        return
    object_info_main, object_move_main = object_list[0], [0, 0, 0]
    object_pos_main = object_info_main['position']
    if 'normal_position' in object_info_main:
        object_move_main = object_info_main['normal_position'][:]
    for object_one in object_list:
        object_one['group'] = group_type
        if 'normal_position' in object_one:
            object_norm_pos = object_one['normal_position']
            object_norm_pos[0] -= object_move_main[0]
            object_norm_pos[2] -= object_move_main[2]
    size_old, offset_old = [0, 0, 0], [0, 0, 0]
    neighbor_base_old, neighbor_more_old = [0, 0, 0, 0], [0, 0, 0, 0]
    neighbor_best_old, neighbor_zone_old = [0, 0, 0, 0], [0, 0, 0, 0]
    if 'size' in group_one:
        size_old = group_one['size'][:]
    if 'offset' in group_one:
        offset_old = group_one['offset'][:]
    if 'neighbor_base' in group_one:
        neighbor_base_old = group_one['neighbor_base']
    if 'neighbor_more' in group_one:
        neighbor_more_old = group_one['neighbor_more']
    if 'neighbor_best' in group_one:
        neighbor_best_old = group_one['neighbor_best']
    if 'neighbor_zone' in group_one:
        neighbor_zone_old = group_one['neighbor_zone']
    # 矩形信息
    if keep_size:
        group_size, group_offset = group_one['size'][:], group_one['offset'][:]
    else:
        group_size, group_offset, furniture_rect = rect_group(group_one)
    # 主要家具 位置旋转
    group_rotation = group_one['rotation'][:]
    group_angle = rot_to_ang(group_rotation)
    offset = [-group_offset[0], -group_offset[1], -group_offset[2]]
    offset_x = offset[2] * math.sin(group_angle) + offset[0] * math.cos(group_angle)
    offset_y = group_offset[1]
    offset_z = offset[2] * math.cos(group_angle) - offset[0] * math.sin(group_angle)
    group_position = [object_pos_main[0] + offset_x,
                      object_pos_main[1] + offset_y,
                      object_pos_main[2] + offset_z]
    neighbor_base_new = [
        (0 - group_offset[2] - group_size[2] / 2) - (0 - offset_old[2] - size_old[2] / 2 - neighbor_base_old[0]),
        (0 - group_offset[0] - group_size[0] / 2) - (0 - offset_old[0] - size_old[0] / 2 - neighbor_base_old[1]),
        (0 - offset_old[2] + size_old[2] / 2 + neighbor_base_old[2]) - (0 - group_offset[2] + group_size[2] / 2),
        (0 - offset_old[0] + size_old[0] / 2 + neighbor_base_old[3]) - (0 - group_offset[0] + group_size[0] / 2)
    ]
    neighbor_more_new = [
        (0 - group_offset[2] - group_size[2] / 2) - (0 - offset_old[2] - size_old[2] / 2 - neighbor_more_old[0]),
        (0 - group_offset[0] - group_size[0] / 2) - (0 - offset_old[0] - size_old[0] / 2 - neighbor_more_old[1]),
        (0 - offset_old[2] + size_old[2] / 2 + neighbor_more_old[2]) - (0 - group_offset[2] + group_size[2] / 2),
        (0 - offset_old[0] + size_old[0] / 2 + neighbor_more_old[3]) - (0 - group_offset[0] + group_size[0] / 2)
    ]
    neighbor_best_new = [
        (0 - group_offset[2] - group_size[2] / 2) - (0 - offset_old[2] - size_old[2] / 2 - neighbor_best_old[0]),
        (0 - group_offset[0] - group_size[0] / 2) - (0 - offset_old[0] - size_old[0] / 2 - neighbor_best_old[1]),
        (0 - offset_old[2] + size_old[2] / 2 + neighbor_best_old[2]) - (0 - group_offset[2] + group_size[2] / 2),
        (0 - offset_old[0] + size_old[0] / 2 + neighbor_best_old[3]) - (0 - group_offset[0] + group_size[0] / 2)
    ]
    neighbor_zone_new = [
        (0 - group_offset[2] - group_size[2] / 2) - (0 - offset_old[2] - size_old[2] / 2 - neighbor_zone_old[0]),
        (0 - group_offset[0] - group_size[0] / 2) - (0 - offset_old[0] - size_old[0] / 2 - neighbor_zone_old[1]),
        (0 - offset_old[2] + size_old[2] / 2 + neighbor_zone_old[2]) - (0 - group_offset[2] + group_size[2] / 2),
        (0 - offset_old[0] + size_old[0] / 2 + neighbor_zone_old[3]) - (0 - group_offset[0] + group_size[0] / 2)
    ]
    # 尺寸信息
    object_one = group_one['obj_list'][0]
    object_id, object_type = object_one['id'], object_one['type']
    origin_size, origin_scale = object_one['size'], object_one['scale']
    object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
    # 剩余信息
    width_rest1 = group_offset[0] - object_size[0] / 2 + group_size[0] / 2
    width_rest2 = group_size[0] / 2 - group_offset[0] - object_size[0] / 2
    depth_rest1 = group_offset[2] - object_size[2] / 2 + group_size[2] / 2
    depth_rest2 = group_size[2] / 2 - group_offset[2] - object_size[2] / 2
    # 更新信息
    group_one['size'] = group_size
    group_one['offset'] = group_offset
    group_one['position'] = group_position
    group_one['rotation'] = group_rotation
    group_one['size_min'] = object_size
    group_one['size_rest'] = [depth_rest1, width_rest1, depth_rest2, width_rest2]
    group_one['obj_main'] = object_id
    group_one['obj_type'] = object_type
    if 'neighbor_base' in group_one:
        group_one['neighbor_base'] = neighbor_base_new
    if 'neighbor_more' in group_one:
        group_one['neighbor_more'] = neighbor_more_new
    if 'neighbor_best' in group_one:
        group_one['neighbor_best'] = neighbor_best_new
    if 'neighbor_zone' in group_one:
        group_one['neighbor_zone'] = neighbor_zone_new


# 功能测试
if __name__ == '__main__':
    # 目录
    image_dir = RECT_DIR_TEMP
    layout_path = os.path.join(image_dir, 'record_layout.json')
    propose_path = os.path.join(image_dir, 'record_propose_info.json')
    layout_info = json.load(open(layout_path, 'r'))
    propose_info = json.load(open(propose_path, 'r'))
    house_rect_adjust(layout_info, propose_info)
    pass
