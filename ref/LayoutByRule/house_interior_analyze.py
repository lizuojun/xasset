# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2021-04-15
@Description: 全屋布局分析

"""

from House.house_sample import *
from LayoutByRule.house_calculator import *

# 房间类型
ROOM_TYPE_FOR_REST_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library']
ROOM_TYPE_FOR_REST_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
ROOM_TYPE_FOR_REST_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom',
                        'Balcony', 'Terrace', 'Lounge', 'LaundryRoom',
                        'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                        'StorageRoom', 'CloakRoom', 'EquipmentRoom']
ROOM_TYPE_FOR_REST_4 = ['Hallway', 'Aisle', 'Corridor', 'Stairwell',
                        'StorageRoom', 'CloakRoom', 'EquipmentRoom']

# 功能区域主次
GROUP_TYPE_MAIN = ['Meeting', 'Dining', 'Bed', 'Media', 'Bath', 'Toilet']
GROUP_TYPE_REST = ['Work', 'Rest', 'Armoire', 'Cabinet', 'Appliance']


# 全屋分析
def house_rect_analyze(data_info, layout_info={}, sample_id=''):
    # 矩形信息
    group_info, region_info = {}, {}

    # 提取方案
    if len(layout_info) <= 0:
        correct_house_data(data_info)
        data_info, layout_info, group_info = extract_house_layout_by_info(data_info)
    if len(layout_info) <= 0:
        return layout_info, group_info, region_info

    # 房间信息
    room_dict, door_mode = {}, 0
    if 'room' not in data_info:
        return layout_info, group_info, region_info
    room_list = data_info['room']
    for room_info in room_list:
        room_dict[room_info['id']] = room_info['type']
    # 房门信息 入户门 厨房门 厕所门
    door_main, door_cook, door_bath = {}, {}, {}
    door_pt_main, door_pt_cook, door_pt_bath = [], [], []
    for room_info in room_list:
        door_list = []
        if 'door_info' in room_info and len(room_info['door_info']) > 0:
            for door_one in room_info['door_info']:
                door_list.append(door_one)
        if 'hole_info' in room_info and len(room_info['hole_info']) > 0:
            for door_one in room_info['hole_info']:
                door_list.append(door_one)
        # 入户门
        if len(door_main) <= 0:
            for door_one in door_list:
                door_to_id = door_one['to']
                if door_to_id == '':
                    if len(door_list) >= 2 or len(door_list) >= len(room_list):
                        door_main = door_one
                        break
        # 厨房门
        if room_info['type'] == 'Kitchen' or 'Kitchen' in room_info['id'] or 'kitchen' in room_info['id']:
            for door_one in door_list:
                door_to_type = ''
                if len(door_to_type) <= 0 and 'link' in door_one:
                    door_to_type = door_one['link']
                if len(door_cook) <= 0:
                    door_cook = door_one
                elif door_to_type not in ['Balcony', 'Terrace']:
                    door_cook = door_one
        # 厕所门
        if room_info['type'] == 'Bathroom' or 'Bathroom' in room_info['id'] or 'bathroom' in room_info['id']:
            for door_one in door_list:
                door_to_type = ''
                if len(door_to_type) <= 0 and 'link' in door_one:
                    door_to_type = door_one['link']
                if len(door_bath) <= 0:
                    door_bath = door_one
                elif door_to_type not in ['Balcony', 'Terrace']:
                    door_bath = door_one
    if 'pts' in door_main:
        door_pts = door_main['pts']
        if len(door_pts) >= 8:
            door_pt_main = [(door_pts[0] + door_pts[2] + door_pts[4] + door_pts[6]) / 4,
                            (door_pts[1] + door_pts[3] + door_pts[5] + door_pts[7]) / 4]
        elif len(door_pts) >= 2:
            door_pt_main = [door_pts[0], door_pts[1]]
    if 'pts' in door_cook:
        door_pts = door_cook['pts']
        if len(door_pts) >= 8:
            door_pt_cook = [(door_pts[0] + door_pts[2] + door_pts[4] + door_pts[6]) / 4,
                            (door_pts[1] + door_pts[3] + door_pts[5] + door_pts[7]) / 4]
        elif len(door_pts) >= 2:
            door_pt_cook = [door_pts[0], door_pts[1]]
    if 'pts' in door_bath:
        door_pts = door_bath['pts']
        if len(door_pts) >= 8:
            door_pt_bath = [(door_pts[0] + door_pts[2] + door_pts[4] + door_pts[6]) / 4,
                            (door_pts[1] + door_pts[3] + door_pts[5] + door_pts[7]) / 4]
        elif len(door_pts) >= 2:
            door_pt_bath = [door_pts[0], door_pts[1]]
    # 遍历房间
    for room_info in room_list:
        # 房间信息
        room_id = room_info['id']
        if room_id not in layout_info:
            continue
        layout_one = layout_info[room_id]
        room_type = layout_one['room_type']
        room_area = layout_one['room_area']
        region_info[room_id] = {
            'room_type': room_info['type'],
            'room_area': room_info['area'],
            'room_rect': []
        }
        # 启动信息
        seed_list, keep_list, mesh_list = [], [], []
        if 'layout_seed' in layout_one:
            seed_list = layout_one['layout_seed']
        if 'layout_keep' in layout_one:
            keep_list = layout_one['layout_keep']
        if 'layout_mesh' in layout_one:
            mesh_list = layout_one['layout_mesh']
        # 方案信息
        sample_list, scheme_list = [], []
        if 'layout_sample' in layout_info[room_id]:
            sample_list = layout_one['layout_sample']
        if 'layout_scheme' in layout_info[room_id]:
            scheme_list = layout_one['layout_scheme']
        # 布局方案
        room_rect_list, room_scheme_list = room_rect_analyze_detail(room_info, sample_list, scheme_list,
                                                                    room_type, room_area, room_dict, door_mode,
                                                                    door_pt_main, door_pt_cook, door_pt_bath)
        # 遍历方案
        layout_one['layout_scheme'] = []
        for scheme_idx, scheme_one in enumerate(room_scheme_list):
            rect_one = {}
            if len(room_rect_list) > 0:
                rect_one = room_rect_list[scheme_idx]
            # 调整得分
            scheme_score = scheme_one['score']
            if scheme_score < 0:
                group_set = []
                if 'group' in scheme_one:
                    group_set = scheme_one['group']
                for group_one in group_set:
                    group_type = group_one['type']
                    width_plus = group_one['size'][0] + group_one['size'][2]
                    if group_type in ['Meeting', 'Dining', 'Bed', 'Armoire']:
                        if 'regulation' in group_one:
                            width_plus += group_one['regulation'][0]
                            width_plus += group_one['regulation'][1]
                            width_plus += group_one['regulation'][2]
                            width_plus += group_one['regulation'][3]
                        scheme_score += width_plus * 1
                    else:
                        scheme_score += 1
                scheme_one['score'] = scheme_score
            # 添加布局
            if sample_id == '':
                layout_info[room_id]['layout_scheme'].append(scheme_one)
                region_info[room_id]['room_rect'].append(rect_one)
            else:
                layout_info[room_id]['layout_scheme'].append(scheme_one)
                region_info[room_id]['room_rect'].append(rect_one)
    # 返回信息
    return layout_info, group_info, region_info


# 单屋分析
def room_rect_analyze(data_info, layout_info={}, sample_id=''):
    # 矩形信息
    group_info, region_info = {}, {}
    if len(layout_info) <= 0:
        layout_info, group_info = extract_room_layout_by_info(data_info)
    # 房间信息
    room_type, room_area, room_dict, door_mode = layout_info['room_type'], layout_info['room_area'], {}, 1
    region_info = {
        'room_type': room_type,
        'room_area': room_area,
        'room_rect': []
    }
    door_list, hole_list = [], []
    if 'door_info' in data_info:
        door_list = data_info['door_info']
    if 'hole_info' in data_info:
        hole_list = data_info['hole_info']
    for door_one in door_list:
        to_room = door_one['to']
        to_type = to_room.split('-')[0]
        room_dict[to_room] = to_type
    for door_one in hole_list:
        to_room = door_one['to']
        to_type = to_room.split('-')[0]
        room_dict[to_room] = to_type
    # 启动信息
    seed_list, keep_list, mesh_list = [], [], []
    if 'layout_seed' in layout_info:
        seed_list = layout_info['layout_seed']
    if 'layout_keep' in layout_info:
        keep_list = layout_info['layout_keep']
    if 'layout_mesh' in layout_info:
        mesh_list = layout_info['layout_mesh']
    # 方案信息
    sample_list, scheme_list = [], []
    if 'layout_sample' in layout_info:
        sample_list = layout_info['layout_sample']
    if 'layout_scheme' in layout_info:
        scheme_list = layout_info['layout_scheme']
    # 布局方案
    room_rect_list, room_scheme_list = room_rect_analyze_detail(data_info, sample_list, scheme_list,
                                                                room_type, room_area, room_dict, door_mode)
    # 遍历方案
    layout_info['layout_scheme'] = []
    for scheme_idx, scheme_one in enumerate(room_scheme_list):
        if len(scheme_one['group']) <= 0:
            continue
        rect_one = {}
        if len(room_rect_list) > 0:
            rect_one = room_rect_list[scheme_idx]
        # 调整得分
        scheme_score = scheme_one['score']
        if scheme_score < 0:
            for group_one in scheme_one['group']:
                group_type = group_one['type']
                width_plus = group_one['size'][0] + group_one['size'][2]
                if group_type in ['Meeting', 'Dining', 'Bed', 'Armoire']:
                    if 'regulation' in group_one:
                        width_plus += group_one['regulation'][0]
                        width_plus += group_one['regulation'][1]
                        width_plus += group_one['regulation'][2]
                        width_plus += group_one['regulation'][3]
                    scheme_score += width_plus * 1
                else:
                    scheme_score += 1
            scheme_one['score'] = scheme_score
        # 添加布局
        if sample_id == '':
            layout_info['layout_scheme'].append(scheme_one)
            region_info['room_rect'].append(rect_one)
        else:
            find_idx = -1
            for old_idx, old_scheme in enumerate(layout_info['layout_scheme']):
                if old_scheme['score'] < scheme_score:
                    find_idx = old_idx
                    break
            if find_idx >= 0:
                layout_info['layout_scheme'].insert(find_idx, scheme_one)
                region_info['room_rect'].insert(find_idx, rect_one)
            else:
                layout_info['layout_scheme'].append(scheme_one)
                region_info['room_rect'].append(rect_one)
    # 组合信息
    group_info = {
        'room_type': '',
        'room_style': '',
        'room_area': 0,
        'room_height': UNIT_HEIGHT_WALL,
        'group_functional': [],
        'group_decorative': []
    }
    if 'room_type' in layout_info:
        group_info['room_type'] = layout_info['room_type']
    if 'room_style' in layout_info:
        group_info['room_style'] = layout_info['room_style']
    if 'room_area' in layout_info:
        group_info['room_area'] = layout_info['room_area']
    if 'room_height' in layout_info:
        group_info['room_height'] = layout_info['room_height']
    group_list, group_func, group_deco = [], [], []
    if len(room_scheme_list) > 0:
        scheme_one = room_scheme_list[0]
        if 'group' in scheme_one:
            group_list = scheme_one['group']
    for group_one in group_list:
        group_type = ''
        if 'type' in group_one:
            group_type = group_one['type']
        if group_type in GROUP_RULE_FUNCTIONAL:
            group_func.append(group_one)
        elif group_type in GROUP_RULE_DECORATIVE:
            group_deco.append(group_one)
    group_info['group_functional'] = group_func
    group_info['group_decorative'] = group_deco

    # 返回信息
    return layout_info, group_info, region_info


# 单屋分析
def room_rect_analyze_detail(room_info, sample_list, scheme_list, room_type='', room_area=10, room_dict={},
                             door_mode=1, door_pt_main=[], door_pt_cook=[], door_pt_bath=[]):
    # 房间信息
    room_key = ''
    if 'id' in room_info:
        room_key = room_info['id']
    if room_type == '':
        room_type = room_info['type']
    if room_area < 0:
        room_area = 10
    room_height = UNIT_HEIGHT_WALL
    if 'height' in room_info and abs(room_info['height'] - UNIT_HEIGHT_WALL) < 1.0:
        room_height = room_info['height']
    if 'ceiling' in room_info:
        ceil_height = room_info['ceiling']
        if ceil_height < 0 or ceil_height > 0.2:
            ceil_height = 0
        room_height -= ceil_height
    room_link = []
    if 'link' in room_info:
        room_link = room_info
    room_info['line_unit'] = []

    # 分析调试
    if '18037' in room_key and False:
        print('analyze room:', room_info['id'], 'debug')

    # 房间类型
    room_major = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']
    room_minor = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
    room_other = ['Bathroom', 'MasterBathroom', 'SecondBathroom', 'Kitchen', 'Balcony', 'Terrace', 'StorageRoom', 'CloakRoom', 'EquipmentRoom']
    room_aisle = ['Hallway', 'Aisle', 'Corridor', 'Stairwell', 'Courtyard', 'Garage']
    # 房门信息
    door_list = []
    if 'door_info' in room_info and len(room_info['door_info']) > 0:
        for unit_one in room_info['door_info']:
            door_list.append(unit_one)
    if 'hole_info' in room_info and len(room_info['hole_info']) > 0:
        for unit_one in room_info['hole_info']:
            door_list.append(unit_one)
    # 进门出门
    door_entry, main_entry, main_to_type = {}, False, ''
    for unit_idx, unit_one in enumerate(door_list):
        door_to_id, door_to_type = unit_one['to'], ''
        if len(door_to_type) <= 0 and 'link' in unit_one:
            door_to_type = unit_one['link']
        if door_to_id == '':
            if room_type in room_minor and (door_to_type in room_major or door_to_type in room_aisle):
                pass
            else:
                door_entry, main_entry = unit_one, True
            if room_type in room_minor:
                pass
            else:
                break
        if room_type in room_major and door_to_type in room_aisle:
            door_entry = unit_one
        elif room_type in room_major:
            if len(door_entry) <= 0:
                door_entry = unit_one
            elif 'to' in door_entry and door_entry['to'] == '':
                continue
            elif 'link' in door_entry:
                entry_link = door_entry['link']
                if entry_link == '':
                    continue
                elif entry_link in room_aisle:
                    continue
                elif door_to_type in room_major and entry_link not in room_major:
                    door_entry = unit_one
        elif room_type in room_minor and door_to_type in room_major:
            door_entry = unit_one
        elif room_type in room_minor and door_to_type not in room_other and len(door_entry) <= 0:
            door_entry = unit_one
        elif room_type in room_minor and door_to_type in room_aisle \
                and 'link' in door_entry and door_entry['link'] in room_other:
            door_entry = unit_one
        elif room_type in room_other and door_to_type not in room_other:
            if door_to_type in ['none', 'OtherRoom'] and len(door_entry) > 0:
                pass
            else:
                door_entry = unit_one
        elif room_type not in room_major and len(door_entry) <= 0:
            door_entry = unit_one
    # 异常处理
    door_entry_more, door_entry_rest = [], []
    for unit_one in door_list:
        door_to_id = unit_one['to']
        if door_to_id == '' and 'pts' in unit_one and len(unit_one['pts']) >= 2:
            door_entry_more.append(unit_one)
        else:
            door_entry_rest.append(unit_one)
    if room_type in room_minor and 'link' in door_entry and (door_entry['link'] in room_major or door_entry['link'] in room_aisle):
        pass
    elif len(door_entry_more) == 1:
        door_entry, door_aside = door_entry_more[0], 10
    elif len(door_entry_more) >= 2 and len(door_entry_rest) > 0:
        door_entry, door_dis_min = door_entry_more[0], 10
        for unit_idx, unit_one in enumerate(door_entry_more):
            if unit_idx >= 4:
                break
            unit_pts_one, unit_dis_one = unit_one['pts'], 10
            for unit_new in door_entry_rest:
                if 'pts' in unit_new and len(unit_new['pts']) >= 2:
                    unit_pts_new = unit_new['pts']
                    unit_dis_new = abs(unit_pts_one[0] - unit_pts_new[0]) + abs(unit_pts_one[1] - unit_pts_new[1])
                    if unit_dis_new < unit_dis_one:
                        unit_dis_one = unit_dis_new
            if unit_dis_one < door_dis_min:
                door_entry = unit_one
    # 进门位置
    door_pt_entry = []
    if 'pts' in door_entry:
        unit_pts = door_entry['pts']
        if len(unit_pts) >= 8:
            door_pt_entry = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                             (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
        elif len(unit_pts) >= 2:
            door_pt_entry = [unit_pts[0], unit_pts[1]]
    if len(door_pt_entry) <= 0:
        door_pt_entry = door_pt_main[:]
    elif len(door_pt_main) <= 0 and main_entry:
        door_pt_main = door_pt_entry[:]

    # 厨房厕所
    door_cook, door_bath, door_open = {}, {}, {}
    door_pt_cook, door_pt_bath, door_pt_open = [], [], []
    for unit_one in door_list:
        door_width = UNIT_WIDTH_DOOR
        if 'pts' in unit_one:
            unit_pts = unit_one['pts']
            unit_dis_1 = abs(unit_pts[2] - unit_pts[0]) + abs(unit_pts[3] - unit_pts[1])
            unit_dis_2 = abs(unit_pts[4] - unit_pts[2]) + abs(unit_pts[5] - unit_pts[3])
            door_width = max(unit_dis_1, unit_dis_2)
            pass
        door_to_id = unit_one['to']
        if door_to_id == '':
            continue
        door_to_type = ''
        if len(door_to_type) <= 0 and 'link' in unit_one:
            door_to_type = unit_one['link']
        if door_to_type == '':
            continue
        elif door_to_type in ['Kitchen']:
            door_cook = unit_one
        elif door_to_type in ['Bathroom', 'MasterBathroom', 'SecondBathroom']:
            door_bath = unit_one
        elif door_to_type in ['Balcony', 'Terrace'] and door_width > UNIT_WIDTH_HOLE:
            door_open = unit_one
    if 'pts' in door_cook:
        unit_pts = door_cook['pts']
        door_pt_cook = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                        (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
    if 'pts' in door_bath:
        unit_pts = door_bath['pts']
        door_pt_bath = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                        (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
    if 'pts' in door_open:
        unit_pts = door_open['pts']
        door_pt_open = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                        (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
    room_info['door_link'] = door_pt_entry
    room_info['door_cook'] = door_pt_cook
    room_info['door_bath'] = door_pt_bath

    # 户型分析
    line_list, line_ori = room_line(room_info, [], [], [], [], room_type, room_area, door_pt_main)
    room_info['line_unit'] = line_list
    # 布局处理
    room_rect_list, room_scheme_list = [], []
    if len(scheme_list) <= 0:
        for sample_one in sample_list:
            sample_new = sample_one.copy()
            sample_new['score'] = -1
            for group_one in sample_new['group']:
                group_one['obj_list'] = []
            scheme_list.append(sample_new)
    # 遍历方案
    for scheme_idx, scheme_one in enumerate(scheme_list):
        # 分类组合
        group_main, group_rest, group_deco, group_ready = [], [], [], []
        group_sample = scheme_one['group']
        for group_one in group_sample:
            group_type = group_one['type']
            if group_type == 'Bed' and room_type == 'Library':
                room_type = 'Bedroom'
                break
        if 'source_room_flag' in scheme_one and 'type' in scheme_one and not room_type == scheme_one['type']:
            room_type = scheme_one['type']
        # 功能组合
        group_work, group_sofa = {}, {}
        for group_one in group_sample:
            group_type, group_size = group_one['type'], group_one['size']
            if group_type in GROUP_TYPE_MAIN:
                if room_type in ['Library']:
                    group_rest.append(group_one)
                else:
                    group_main.append(group_one)
            elif group_type in ['Work'] and room_type in ['Library']:
                group_main.append(group_one)
            elif group_type in ['Rest'] and room_type in ['Balcony', 'Terrace']:
                group_main.append(group_one)
            elif group_type in GROUP_RULE_FUNCTIONAL:
                group_rest.append(group_one)
                if group_type in ['Work']:
                    group_work = group_one
                if 'obj_type' in group_one and 'sofa' in group_one['obj_type']:
                    group_sofa = group_one
            elif group_type in GROUP_RULE_DECORATIVE:
                group_deco.append(group_one)
        if len(group_main) <= 0 and len(group_work) > 0:
            room_type = 'Library'
            group_main.append(group_work)
            if group_work in group_rest:
                group_rest.remove(group_work)
        if len(group_main) <= 0 and len(group_sofa) > 0:
            group_main.append(group_sofa)
            if group_sofa in group_rest:
                group_rest.remove(group_sofa)
            pass
        # 矩形信息
        room_rect_add = {}

        # 更新布局
        for group_one in group_main:
            group_ready.append(group_one)
        for group_one in group_rest:
            group_ready.append(group_one)

        # 功能组合
        if room_area >= 0:
            # 更新矩形
            type_fine, unit_fine, height_fine, back_fine = compute_group_unit(group_ready, [], [])
            room_rect_new = room_rect(room_info, type_fine, unit_fine, height_fine, back_fine, room_type, room_area, door_pt_main)
            room_rect_add = room_rect_new[0]
            rect_list = room_rect_add['rect']
            line_list = room_rect_add['line']
            # 更新布局
            rect_used = {}
            room_rect_update_ready(rect_list, line_list, rect_used, group_main, neighbor_find=False, room_area=room_area)

            # 更新矩形
            type_fine, unit_fine, height_fine, back_fine = compute_group_unit(group_ready, [], [])
            room_rect_new = room_rect(room_info, type_fine, unit_fine, height_fine, back_fine, room_type, room_area, door_pt_main)
            room_rect_add = room_rect_new[0]
            rect_list = room_rect_add['rect']
            line_list = room_rect_add['line']
            room_rect_list.append(room_rect_add)
            # 更新布局
            rect_used = {}
            room_rect_update_ready(rect_list, line_list, rect_used, group_ready, neighbor_find=True, room_area=room_area)

        # 装饰组合
        if room_area >= 0:
            for group_one in group_deco:
                group_ready.append(group_one)

        # 增加组合
        scheme_one['group'] = []
        for group_one in group_ready:
            scheme_one['group'].append(group_one)
        room_scheme_list.append(scheme_one)
        # 增加区域
        if 'line' in room_rect_add:
            scheme_one['line_unit'] = room_rect_add['line']
    # 返回信息
    return room_rect_list, room_scheme_list


# 布局更新
def room_rect_update_ready(rect_list, line_list, rect_used, group_todo, neighbor_find=False, room_area=10):
    group_result, group_center, group_center_face = [], [], []
    if len(group_todo) <= 0:
        return group_result, group_center
    group_main_list, group_face_list, group_rest_list = [], [], []
    for group_one in group_todo:
        group_type = group_one['type']
        if group_type in ['Meeting', 'Bed']:
            group_main_list.append(group_one)
        elif group_type in ['Media']:
            group_face_list.append(group_one)
        elif group_type in ['Work', 'Rest', 'Armoire', 'Cabinet', 'Appliance']:
            group_rest_list.append(group_one)
    if len(group_face_list) <= 0 and len(group_rest_list) > 0:
        group_face_list = group_rest_list
    # 遍历组合
    for group_one in group_todo:
        # 分组信息
        group_type, group_size = group_one['type'], group_one['size']
        group_pos, group_ang = group_one['position'], rot_to_ang(group_one['rotation'])
        group_width, group_depth = group_size[0], group_size[2]
        group_x, group_y = group_pos[0], group_pos[2]
        group_regulate = [0, 0, 0, 0]
        if 'regulation' in group_one:
            group_regulate = group_one['regulation'][:]
            group_width = group_size[0] + group_regulate[1] + group_regulate[3]
            group_depth = group_size[2] + group_regulate[0] + group_regulate[2]
        # 对面组合
        group_face, group_todo_list = {}, []
        if group_type in ['Meeting', 'Bed']:
            group_todo_list = group_face_list
        elif group_type in ['Media']:
            group_todo_list = group_main_list
        for group_new in group_todo_list:
            group_pos_old, group_ang_old = group_pos, group_ang
            group_pos_new, group_ang_new = group_new['position'], rot_to_ang(group_new['rotation'])
            dlt_x, dlt_z = group_pos_new[0] - group_pos_old[0], group_pos_new[2] - group_pos_old[2]
            tmp_x = dlt_z * math.sin(-group_ang_old) + dlt_x * math.cos(-group_ang_old)
            tmp_z = dlt_z * math.cos(-group_ang_old) - dlt_x * math.sin(-group_ang_old)
            if abs(ang_to_ang(group_ang_old + math.pi - group_ang_new)) < 0.1:
                if abs(tmp_x) > 0.5 and abs(tmp_x) > group_new['size'][0] / 2:
                    continue
                if abs(tmp_x) < 2 and abs(tmp_z) < 6:
                    group_face = group_new
                    break
        # 邻居信息
        neighbor_base, neighbor_more = [0, 0, 0, 0], [0, 0, 0, 0]
        neighbor_best, neighbor_zone = [1, 1, 1, 1], [1, 1, 1, 1]
        group_one['neighbor_base'] = neighbor_base
        group_one['neighbor_more'] = neighbor_more
        group_one['neighbor_best'] = neighbor_best
        group_one['neighbor_zone'] = neighbor_zone
        # 特殊信息
        vertical_flag, window_flag, center_flag, switch_flag, region_direct = 0, 0, 0, 0, 0
        back_p1, back_p2, back_depth, back_front, back_angle = [], [], 0, group_depth, 0
        if 'back_depth' in group_one:
            back_depth = group_one['back_depth']
        if group_type in ['Meeting', 'Dining', 'Work']:
            center_flag = 1
        # 矩形查找
        rect_best = {}
        for rect_idx, rect_one in enumerate(rect_list):
            # 初步判断
            if not rect_one['type'] == UNIT_TYPE_GROUP:
                continue
            if rect_idx in rect_used:
                continue
            # 矩形距离
            rect_width, rect_depth, rect_height = rect_one['width'], rect_one['depth'], rect_one['height']
            rect_angle = rect_one['angle']
            if abs(normalize_line_angle(rect_angle - group_ang)) < 0.01:
                if rect_depth < group_depth * 0.5 or rect_depth > group_depth * 2 + 1.0:
                    continue
            elif abs(normalize_line_angle(rect_angle - group_ang - math.pi)) < 0.01:
                if rect_depth < group_depth * 0.5 or rect_depth > group_depth * 2 + 1.0:
                    continue
            else:
                if rect_depth < group_width * 0.5:
                    continue
            rect_x, rect_y = rect_one['center'][0], rect_one['center'][1]
            rect_d_x, rect_d_y = abs(group_x - rect_x), abs(group_y - rect_y)
            rect_flag = False
            if determine_line_angle(rect_angle) == determine_line_angle(group_ang) == 0:
                if rect_d_x < rect_depth * 0.5 and rect_d_y < rect_width * 0.5:
                    rect_flag = True
            elif determine_line_angle(rect_angle) == determine_line_angle(group_ang) == 1:
                if rect_d_x < rect_width * 0.5 and rect_d_y < rect_depth * 0.5:
                    rect_flag = True
            else:
                if determine_line_angle(rect_angle) == 0:
                    if rect_d_x < rect_depth * 0.3 and rect_d_y < rect_width * 0.3:
                        rect_flag = True
                elif determine_line_angle(rect_angle) == 1:
                    if rect_d_x < rect_width * 0.3 and rect_d_y < rect_depth * 0.3:
                        rect_flag = True
                else:
                    if rect_d_x + rect_d_y < min(rect_width, rect_depth) * 0.4:
                        rect_flag = True
            if rect_flag:
                # 判断参数
                index_best = rect_idx
                if determine_line_angle(group_ang) == determine_line_angle(rect_angle):
                    angle_suit = 0
                    width_best = group_one['size'][0]
                    if 'regulation' in group_one:
                        width_best += group_one['regulation'][1]
                        width_best += group_one['regulation'][3]
                    if width_best > rect_width:
                        width_best = rect_width
                    depth_best = group_one['size'][2]
                    space_best = rect_width - width_best
                else:
                    angle_suit = 1
                    width_best = group_one['size'][2]
                    depth_best = group_one['size'][0]
                    space_best = rect_width - width_best
                line_idx_old = rect_one['index']
                line_one_old = line_list[line_idx_old]
                unit_edge = line_one_old['unit_edge']
                unit_flag = line_one_old['unit_flag']
                if unit_edge in [1, 3] and unit_flag >= 1:
                    vertical_flag = 1
                if group_type in ['Meeting'] and unit_edge in [1, 3] and unit_flag >= 1:
                    pass
                elif group_type in ['Dining'] and unit_edge in [2] and unit_flag >= 1:
                    center_flag = 0
                    ang_new = ang_to_ang(group_ang + math.pi)
                    group_regulate_new = [group_regulate[2], group_regulate[3], group_regulate[0], group_regulate[1]]
                    group_one['rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                    group_one['regulation'] = group_regulate_new
                    group_one['region_beside'] = [line_one_old['score_pre'], line_one_old['score_post']]
                    unit_edge = 0
                else:
                    center_flag = 0
                # 邻居信息
                if neighbor_find:
                    width_cur, width_pre_max, width_post_max = line_one_old['width'], 0, 0
                    edge_idx, rely_idx, rely_rat, rely_face, rely_back = compute_group_rely(group_one, [line_one_old], 2.0)
                    edge_idx, rely_idx = unit_edge, line_idx_old
                    # 两侧扩展
                    if unit_edge >= 0 and unit_flag >= 1:
                        line_idx = line_idx_old
                        line_one = line_one_old
                        line_idx_pre = (line_idx - 1 + len(line_list)) % len(line_list)
                        line_idx_post = (line_idx + 1 + len(line_list)) % len(line_list)
                        line_idx_pre2 = (line_idx - 2 + len(line_list)) % len(line_list)
                        line_idx_post2 = (line_idx + 2 + len(line_list)) % len(line_list)
                        line_pre, line_post = line_list[line_idx_pre], line_list[line_idx_post]
                        line_pre2, line_post2 = line_list[line_idx_pre2], line_list[line_idx_post2]
                        width_pre, width_post, width_pre_more, width_post_more = 0, 0, 0, 0
                        depth_pre, depth_post = line_one['depth_pre'], line_one['depth_post']
                        depth_pre_more, depth_post_more = line_one['depth_pre_more'], line_one['depth_post_more']
                        # 前序信息
                        if line_one['score_pre'] == 1:
                            unit_fine = [UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]
                            if group_type in ['Dining', 'Work', 'Rest']:
                                unit_fine = [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                            if line_pre['type'] in unit_fine:
                                depth_pre = line_one['depth_pre']
                                if line_pre['type'] in [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL] or depth_pre > rect_depth:
                                    width_pre = line_pre['width']
                                    width_pre_more = line_pre['width']
                                if line_pre['score_pre'] == 1 and line_pre2['type'] in unit_fine:
                                    width_pre_more += min(line_pre2['width'], UNIT_WIDTH_DODGE)
                                elif line_pre['score_pre'] == 2:
                                    width_pre_more += min(line_pre2['depth'], UNIT_WIDTH_DODGE)
                            elif line_pre['type'] in [UNIT_TYPE_SIDE] and line_pre['width'] > UNIT_DEPTH_CURTAIN + 0.01:
                                depth_pre = line_one['depth_pre']
                                if depth_pre > rect_depth - 0.25:
                                    width_pre = line_pre['width']
                                    width_pre_more = line_pre['width']
                            elif line_pre['type'] in [UNIT_TYPE_DOOR] and line_pre['height'] >= UNIT_HEIGHT_WALL - 0.1:
                                side_width = min(line_pre['width'] * 1.0, 1.0)
                                group_width_new = group_size[0] + group_regulate[1] + group_regulate[3]
                                if group_type in ['Dining']:
                                    if unit_edge in [0, 2] and line_one['width'] >= group_width_new - 0.01:
                                        width_pre_more = side_width
                                    elif unit_edge in [1, 3] and line_one['width'] >= group_depth:
                                        width_pre_more = side_width
                                else:
                                    if unit_edge in [0, 2] and line_one['width'] >= group_width_new - 0.01:
                                        width_pre_more = side_width
                                    elif unit_edge in [1, 3] and line_one['width'] >= group_depth:
                                        width_pre_more = side_width
                            if line_pre['score_pre'] == 2 and line_pre['type'] in unit_fine:
                                width_pre += MIN_GROUP_PASS
                                width_pre_more += UNIT_WIDTH_DODGE
                            if line_pre['score_pre'] == 1 and line_pre['type'] in [UNIT_TYPE_WALL]:
                                if line_pre['width'] < 1:
                                    line_idx_pre_pre = (line_idx - 2 + len(line_list)) % len(line_list)
                                    line_pre_pre = line_list[line_idx_pre_pre]
                                    if line_pre_pre['type'] in [UNIT_TYPE_DOOR] or line_pre_pre['score_pre'] == 2:
                                        width_pre_more += UNIT_WIDTH_DODGE
                        elif line_one['score_pre'] == 2:
                            if unit_edge == 0 and line_one['width'] > group_width or group_regulate[3] >= 0:
                                width_pre = MIN_GROUP_PASS
                                width_pre_more = UNIT_WIDTH_DODGE
                            elif unit_edge == 2 and line_one['width'] > group_width or group_regulate[1] >= 0:
                                width_pre = MIN_GROUP_PASS
                                width_pre_more = UNIT_WIDTH_DODGE
                        if width_pre < 0.01 and rely_rat[0] > 0.01:
                            width_pre += width_cur * (rely_rat[0] - 0)
                            width_pre_more += width_cur * (rely_rat[0] - 0)
                        # 后序信息
                        if line_one['score_post'] == 1:
                            unit_fine = [UNIT_TYPE_WINDOW, UNIT_TYPE_AISLE, UNIT_TYPE_WALL]
                            if group_type in ['Dining', 'Work', 'Rest']:
                                unit_fine = [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL]
                            if line_post['type'] in unit_fine:
                                depth_post = line_one['depth_post']
                                if line_post['type'] in [UNIT_TYPE_WINDOW, UNIT_TYPE_WALL] or depth_post > rect_depth:
                                    width_post = line_post['width']
                                    width_post_more = line_post['width']
                                    if line_post['score_post'] == 1 and line_post2['type'] in unit_fine:
                                        width_post_more += min(line_post2['width'], UNIT_WIDTH_DODGE)
                                    elif line_post['score_post'] == 2:
                                        width_post_more += min(line_post2['depth'], UNIT_WIDTH_DODGE)
                            elif line_post['type'] in [UNIT_TYPE_SIDE] and line_post['width'] > UNIT_DEPTH_CURTAIN + 0.01:
                                depth_post = line_one['depth_post']
                                if depth_post > rect_depth - 0.1:
                                    width_post = line_post['width']
                                    width_post_more = line_post['width']
                            elif line_post['type'] in [UNIT_TYPE_DOOR] and line_post['height'] >= UNIT_HEIGHT_WALL - 0.1:
                                side_width = min(line_post['width'] * 1.0, 1.0)
                                group_width_new = group_size[0] + group_regulate[1] + group_regulate[3]
                                if group_type in ['Dining']:
                                    if unit_edge in [0, 2] and line_one['width'] >= group_width_new - 0.01:
                                        width_post_more = side_width
                                    elif unit_edge in [1, 3] and line_one['width'] >= group_depth:
                                        width_post_more = side_width
                                else:
                                    if unit_edge in [0, 2] and line_one['width'] >= group_width_new - 0.01:
                                        width_post_more = side_width
                                    elif unit_edge in [1, 3] and line_one['width'] >= group_depth:
                                        width_post_more = side_width
                            if line_post['score_post'] == 2 and line_post['type'] in unit_fine:
                                width_post += MIN_GROUP_PASS
                                width_post_more += UNIT_WIDTH_DODGE
                            if line_post['score_post'] == 1 and line_post['type'] in [UNIT_TYPE_WALL]:
                                if line_post['width'] < 1:
                                    line_idx_post_post = (line_idx + 2 + len(line_list)) % len(line_list)
                                    line_post_post = line_list[line_idx_post_post]
                                    if line_post_post['type'] in [UNIT_TYPE_DOOR] or line_post_post['score_post'] == 2:
                                        width_post_more += UNIT_WIDTH_DODGE
                        elif line_one['score_post'] == 2:
                            if unit_edge == 0 and line_one['width'] > group_width or group_regulate[1] >= 0:
                                width_post = MIN_GROUP_PASS
                                width_post_more = UNIT_WIDTH_DODGE / 2
                            elif unit_edge == 2 and line_one['width'] > group_width or group_regulate[3] >= 0:
                                width_post = MIN_GROUP_PASS
                                width_post_more = UNIT_WIDTH_DODGE / 2
                        if width_post < 0.01 and rely_rat[1] < 0.99:
                            width_post += width_cur * (1 - rely_rat[1])
                            width_post_more += width_cur * (1 - rely_rat[1])
                        #
                        if width_pre_max < width_pre:
                            width_pre_max = width_pre
                        if width_post_max < width_post:
                            width_post_max = width_post
                        # 邻居信息
                        if unit_edge == 0 and unit_flag >= 1:
                            if width_pre > 0 or width_pre_more > 0:
                                neighbor_base[3] = width_pre
                                neighbor_more[3] = width_pre_more
                            if width_post > 0 or width_post_more > 0:
                                neighbor_base[1] = width_post
                                neighbor_more[1] = width_post_more
                        elif unit_edge == 2 and unit_flag >= 1:
                            if width_pre > 0 or width_pre_more > 0:
                                neighbor_base[1] = width_pre
                                neighbor_more[1] = width_pre_more
                            if width_post > 0 or width_post_more > 0:
                                neighbor_base[3] = width_post
                                neighbor_more[3] = width_post_more
                        elif unit_edge == 1 and unit_flag >= 1:
                            if width_pre > 0 or width_pre_more > 0:
                                neighbor_base[0] = width_pre
                                neighbor_more[0] = width_pre_more
                            if width_post > 0 or width_post_more > 0:
                                neighbor_base[2] = width_post
                                neighbor_more[2] = width_post_more
                            if min(depth_pre, depth_post) - rely_back > group_width:
                                neighbor_base[3] = min(depth_pre, depth_post) - rely_back - group_width
                            if min(depth_pre_more, depth_post_more) - rely_back > group_width:
                                neighbor_more[3] = min(depth_pre_more, depth_post_more) - rely_back - group_width
                        elif unit_edge == 3 and unit_flag >= 1:
                            if width_pre > 0 or width_pre_more > 0:
                                neighbor_base[2] = width_pre
                                neighbor_more[2] = width_pre_more
                            if width_post > 0 or width_post_more > 0:
                                neighbor_base[0] = width_post
                                neighbor_more[0] = width_post_more
                            if min(depth_pre, depth_post) - rely_back > group_width:
                                neighbor_base[1] = min(depth_pre, depth_post) - rely_back - group_width
                            if min(depth_pre_more, depth_post_more) - rely_back > group_width:
                                neighbor_more[1] = min(depth_pre_more, depth_post_more) - rely_back - group_width
                    # 进深扩展
                    if len(group_face) > 0:
                        face_size, face_pos, face_adjust = group_face['size'], group_face['position'], [0, 0, 0, 0]
                        if 'regulation' in group_face:
                            face_adjust = group_face['regulation']
                        tmp_x, tmp_z = face_pos[0] - group_pos[0], face_pos[2] - group_pos[2]
                        add_x = tmp_z * math.sin(-group_ang) + tmp_x * math.cos(-group_ang)
                        add_z = tmp_z * math.cos(-group_ang) - tmp_x * math.sin(-group_ang)
                        depth_min = add_z + group_size[2] / 2 - face_size[2] / 2 - face_adjust[2]
                        if abs(add_x) <= group_size[0] / 2:
                            depth_add = depth_min - (group_size[2] + group_regulate[2])
                            depth_add = min(depth_add * 0.80, depth_add - 0.10)
                            if len(neighbor_base) >= 4:
                                neighbor_base[2] = min(depth_add, 3.0)
                            if len(neighbor_more) >= 4:
                                neighbor_more[2] = min(depth_add, 3.0)
                    elif unit_edge >= 0 and unit_flag >= 1:
                        rect_depth = group_size[2] + group_regulate[0] + group_regulate[2] + rely_back
                        if unit_edge in [1, 3]:
                            rect_depth = group_size[0] + group_regulate[1] + group_regulate[3] + rely_back
                        if 0 <= edge_idx < 4 and 0 <= rely_idx < len(line_list):
                            # 扩展边界
                            line_one_old, depth_max, depth_add = line_list[rely_idx], rely_face, 0
                            if depth_max > min(depth_pre_more, depth_post_more) > rect_depth:
                                depth_add = (min(depth_pre_more, depth_post_more) - rect_depth) - UNIT_DEPTH_DODGE * 0.5
                            elif depth_max * 0.50 > rect_depth:
                                depth_add = depth_max * 0.50 - rect_depth
                                if depth_add < MIN_GROUP_PASS:
                                    depth_add = depth_max * 0.60 - rect_depth
                                    depth_add = min(depth_add, MID_GROUP_PASS * 1.0)
                                else:
                                    depth_add = min(depth_add, MID_GROUP_PASS * 2.0)
                            elif depth_max * 0.75 > rect_depth:
                                depth_add = depth_max * 0.75 - rect_depth
                                depth_add = min(depth_add, MID_GROUP_PASS * 1.0)
                            elif depth_max * 1.00 > rect_depth:
                                depth_add = depth_max - rect_depth - 0.5
                            if group_type in ['Armoire', 'Cabinet']:
                                depth_add = depth_max - rect_depth
                            # 调整边界
                            if len(neighbor_more) >= 4:
                                neighbor_more[unit_edge] = max(neighbor_more[unit_edge], rely_back - UNIT_DEPTH_CURTAIN)
                                if unit_edge == 0:
                                    neighbor_more[2] = min(depth_add, MID_GROUP_PASS * 3.0)
                                elif unit_edge == 1:
                                    neighbor_more[3] = min(depth_add, MID_GROUP_PASS * 3.0)
                                elif unit_edge == 2:
                                    neighbor_more[0] = min(depth_add, MID_GROUP_PASS * 3.0)
                                elif unit_edge == 3:
                                    neighbor_more[1] = min(depth_add, MID_GROUP_PASS * 3.0)
                    # 区域扩展
                    room_rect_update_region(group_one, line_list, edge_idx, rely_idx, rely_rat, rely_back)
                    # 特殊信息
                    if unit_edge in [1, 3] and unit_flag >= 1:
                        vertical_flag = 1
                    if rect_height > group_one['size'][1] + 0.1:
                        window_flag = 1
                    if group_type in ['Meeting'] and unit_edge in [1, 3] and unit_flag >= 1:
                        pass
                    else:
                        center_flag = 0
                    if width_pre_max > MIN_GROUP_PASS and width_post_max > MIN_GROUP_PASS:
                        region_direct = 0
                    elif width_pre_max < width_post_max:
                        region_direct = 1
                    elif width_pre_max > width_post_max:
                        region_direct = -1
                    group_one['vertical'] = vertical_flag
                    group_one['window'] = window_flag
                    group_one['center'] = center_flag
                    group_one['region_direct'] = region_direct
                    # 背景信息
                    if unit_flag >= 1:
                        # 背景范围
                        back_p1, back_p2 = rect_one['p1'][:], rect_one['p2'][:]
                        if len(neighbor_base) >= 4:
                            d1, d2 = 0, 0
                            if unit_edge == 0:
                                d1, d2 = neighbor_base[3], neighbor_base[1]
                            elif unit_edge == 2:
                                d1, d2 = neighbor_base[1], neighbor_base[3]
                            elif unit_edge == 1:
                                d1, d2 = neighbor_base[0], neighbor_base[2]
                            elif unit_edge == 3:
                                d1, d2 = neighbor_base[2], neighbor_base[0]
                            x1, z1, x2, z2 = back_p1[0], back_p1[1], back_p2[0], back_p2[1]
                            dis, ang = compute_dis_ang(x1, z1, x2, z2)
                            if d1 > 0 and d2 > 0 and dis > 0:
                                dd = min(d1, d2)
                                x1_new = x1 + (x1 - x2) * dd / dis
                                z1_new = z1 + (z1 - z2) * dd / dis
                                back_p1 = [x1_new, z1_new]
                                x2_new = x2 + (x2 - x1) * dd / dis
                                z2_new = z2 + (z2 - z1) * dd / dis
                                back_p2 = [x2_new, z2_new]
                        # 背景厚度
                        back_depth = 0.00
                        if 'back_depth' in rect_one:
                            back_depth = rect_one['back_depth']
                        elif group_regulate[0] + group_regulate[2] >= 0.05 and unit_edge == 0:
                            back_depth = group_regulate[0] + group_regulate[2]
                        # 进深距离
                        back_front = group_depth
                        if unit_edge in [1, 3]:
                            back_front = group_width
                        elif 'region_extent' in group_one:
                            back_front = group_one['region_extent']
                        # 背景朝向
                        back_angle = rect_one['angle']
                # 参数信息
                param_best = {
                    'index': index_best,
                    'angle': angle_suit,
                    'width': width_best,
                    'depth': depth_best,
                    'width_rest': space_best,
                    'group': []
                }
                param_add = param_best.copy()
                param_add['group'].append(group_one)
                # 参数添加
                if index_best not in rect_used:
                    rect_used[index_best] = []
                rect_used[index_best].append(param_add)
                rect_best = rect_one
                break
        # 矩形范围
        if len(rect_best) <= 0:
            edge_idx, rely_idx, rely_rat, rely_face, rely_back = compute_group_rely(group_one, line_list, 2.0)
            unit_edge = edge_idx
            # 进深扩展
            if len(group_face) > 0:
                # 对面信息
                face_size, face_pos, face_adjust = group_face['size'], group_face['position'], [0, 0, 0, 0]
                if 'regulation' in group_face:
                    face_adjust = group_face['regulation']
                tmp_x, tmp_z = face_pos[0] - group_pos[0], face_pos[2] - group_pos[2]
                add_x = tmp_z * math.sin(-group_ang) + tmp_x * math.cos(-group_ang)
                add_z = tmp_z * math.cos(-group_ang) - tmp_x * math.sin(-group_ang)
                depth_min = add_z + group_size[2] / 2 - face_size[2] / 2 - face_adjust[2]
                if abs(add_x) <= group_size[0] / 2:
                    depth_add = depth_min - (group_size[2] + group_regulate[2])
                    depth_add = min(depth_add * 0.80, depth_add - 0.10)
                    if len(neighbor_base) >= 4:
                        neighbor_base[2] = min(depth_add, 3.0)
                    if len(neighbor_more) >= 4:
                        neighbor_more[2] = min(depth_add, 3.0)
                # 周边信息
                neighbor_face = [0, 0, 0, 0]
                if 'neighbor_base' in group_face:
                    face_size, face_side = group_face['size'], group_face['neighbor_base']
                    face_rest = [0, 0, 0, 0]
                    if 'regulation' in group_face:
                        face_rest = group_face['regulation']
                    face_width = face_size[0] + face_rest[1] + face_rest[3] + min(face_side[1], face_side[3]) * 2
                    neighbor_face[1] = (face_width - group_size[0]) / 2
                    neighbor_face[3] = (face_width - group_size[0]) / 2
                    if face_side[1] >= face_side[3]:
                        neighbor_face[1] += (face_side[1] - face_side[3])
                    else:
                        neighbor_face[3] += (face_side[3] - face_side[1])
                neighbor_base[1] = max(neighbor_more[1], neighbor_face[3])
                neighbor_base[3] = max(neighbor_more[3], neighbor_face[1])
                # 周边信息
                neighbor_face = [0, 0, 0, 0]
                if 'neighbor_more' in group_face:
                    face_size, face_side = group_face['size'], group_face['neighbor_more']
                    face_rest = [0, 0, 0, 0]
                    if 'regulation' in group_face:
                        face_rest = group_face['regulation']
                    face_width = face_size[0] + face_rest[1] + face_rest[3] + min(face_side[1], face_side[3]) * 2
                    neighbor_face[1] = (face_width - group_size[0]) / 2
                    neighbor_face[3] = (face_width - group_size[0]) / 2
                    if face_side[1] >= face_side[3]:
                        neighbor_face[1] += (face_side[1] - face_side[3])
                    else:
                        neighbor_face[3] += (face_side[3] - face_side[1])
                neighbor_more[1] = max(neighbor_more[1], neighbor_face[3])
                neighbor_more[3] = max(neighbor_more[3], neighbor_face[1])
            elif group_type in ['Dining']:
                rect_depth = group_size[2] + group_regulate[0] + group_regulate[2] + rely_back
                if unit_edge in [1, 3]:
                    rect_depth = group_size[0] + group_regulate[1] + group_regulate[3] + rely_back
                if 0 <= edge_idx < 4 and 0 <= rely_idx < len(line_list):
                    # 扩展边界
                    line_one_old, depth_max, depth_add = line_list[rely_idx], rely_face, 0
                    if depth_max * 0.50 > rect_depth:
                        depth_add = depth_max * 0.50 - rect_depth
                        if depth_add < MIN_GROUP_PASS:
                            depth_add = depth_max * 0.60 - rect_depth
                            depth_add = min(depth_add, MID_GROUP_PASS * 1.0)
                        else:
                            depth_add = min(depth_add, MID_GROUP_PASS * 2.0)
                    elif depth_max * 0.75 > rect_depth:
                        depth_add = depth_max * 0.75 - rect_depth
                        depth_add = min(depth_add, MID_GROUP_PASS * 1.0)
                    elif depth_max * 1.00 > rect_depth:
                        depth_add = depth_max - rect_depth - 0.5
                    if group_type in ['Armoire', 'Cabinet']:
                        depth_add = depth_max - rect_depth
                    # 调整边界
                    if len(neighbor_more) >= 4:
                        # 扩展边界
                        line_idx_pre = (rely_idx - 1 + len(line_list)) % len(line_list)
                        line_idx_post = (rely_idx + 1 + len(line_list)) % len(line_list)
                        line_idx_pre2 = (rely_idx - 2 + len(line_list)) % len(line_list)
                        line_idx_post2 = (rely_idx + 2 + len(line_list)) % len(line_list)
                        line_pre, line_post = line_list[line_idx_pre], line_list[line_idx_post]
                        line_pre2, line_post2 = line_list[line_idx_pre2], line_list[line_idx_post2]
                        stop_pre, stop_pre2, stop_post, stop_post2 = False, False, False, False
                        if line_pre['type'] in [UNIT_TYPE_GROUP] and line_pre['depth'] > 1:
                            stop_pre = True
                        if line_pre2['type'] in [UNIT_TYPE_GROUP] and line_pre2['depth'] > 1:
                            stop_pre2 = True
                        if line_post['type'] in [UNIT_TYPE_GROUP] and line_post['depth'] > 1:
                            stop_post = True
                        if line_post2['type'] in [UNIT_TYPE_GROUP] and line_post2['depth'] > 1:
                            stop_post2 = True
                        rat_pre, rat_post, width_old = 0, 1, line_one_old['width']
                        if width_old > 5 and rely_rat[0] > 0.5:
                            rat_pre = 0.5
                        elif width_old > 5 and rely_rat[1] < 0.5:
                            rat_post = 0.5
                        else:
                            if line_one_old['score_pre'] == 1 and not stop_pre:
                                dis_pre = line_pre['width']
                                if line_pre['score_pre'] == 1 and not stop_pre2:
                                    dis_pre = line_pre['width'] + line_pre2['width']
                                rat_pre = 0 - dis_pre / width_old
                            if line_one_old['score_post'] == 1 and not stop_post:
                                dis_post = line_post['width']
                                if line_post['score_post'] == 1 and not stop_post2:
                                    dis_post = line_post['width'] + line_post2['width']
                                rat_post = 1 + dis_post / width_old
                        # 调整边界
                        neighbor_more[unit_edge] = max(neighbor_more[unit_edge], rely_back - 0.4)
                        if unit_edge == 0:
                            neighbor_more[2] = min(depth_add, MID_GROUP_PASS * 3.0)
                            if group_regulate[unit_edge] + rely_back < 0.5:
                                neighbor_more[1] = max(neighbor_more[1], width_old * (rat_post - rely_rat[1]) - 0.4)
                                neighbor_more[3] = max(neighbor_more[3], width_old * (rely_rat[0] - rat_pre) - 0.4)
                        elif unit_edge == 1:
                            neighbor_more[3] = min(depth_add, MID_GROUP_PASS * 3.0)
                            if group_regulate[unit_edge] + rely_back < 0.5:
                                neighbor_more[0] = max(neighbor_more[0], width_old * (rely_rat[0] - rat_pre) - 0.4)
                                neighbor_more[2] = max(neighbor_more[2], width_old * (rat_post - rely_rat[1]) - 0.4)
                        elif unit_edge == 2:
                            neighbor_more[0] = min(depth_add, MID_GROUP_PASS * 3.0)
                            if group_regulate[unit_edge] + rely_back < 0.5:
                                neighbor_more[1] = max(neighbor_more[1], width_old * (rely_rat[0] - rat_pre) - 0.4)
                                neighbor_more[3] = max(neighbor_more[3], width_old * (rat_post - rely_rat[1]) - 0.4)
                        elif unit_edge == 3:
                            neighbor_more[1] = min(depth_add, MID_GROUP_PASS * 3.0)
                            if group_regulate[unit_edge] + rely_back < 0.5:
                                neighbor_more[2] = max(neighbor_more[2], width_old * (rely_rat[0] - rat_pre) - 0.4)
                                neighbor_more[0] = max(neighbor_more[0], width_old * (rat_post - rely_rat[1]) - 0.4)
                else:
                    neighbor_more[0] = max(1.0, neighbor_more[0])
                    neighbor_more[1] = max(1.0, neighbor_more[1])
                    neighbor_more[2] = max(1.0, neighbor_more[2])
                    neighbor_more[3] = max(1.0, neighbor_more[3])
            # 区域扩展
            room_rect_update_region(group_one, line_list, edge_idx, rely_idx, rely_rat, rely_back)
        # 调整信息 邻居信息
        group_one['neighbor_base'] = neighbor_base
        group_one['neighbor_more'] = neighbor_more
        # 调整信息 特殊信息
        group_one['center'] = center_flag
        group_one['vertical'] = vertical_flag
        if 'switch' not in group_one:
            group_one['switch'] = switch_flag
        if 'region_direct' not in group_one:
            group_one['region_direct'] = region_direct
        # 调整信息 背景信息
        group_one['back_p1'] = back_p1
        group_one['back_p2'] = back_p2
        group_one['back_depth'] = back_depth
        group_one['back_front'] = back_front
        group_one['back_angle'] = back_angle
        # 添加布局
        group_result.append(group_one)
    # 返回信息
    return group_result, group_center


# 布局避让
def room_rect_update_dodge(rect_list, line_list, rect_used, group_todo, room_type='', room_area=10, door_pt_entry=[]):
    # 排序矩形
    rect_sort = []
    rect_sort_1, rect_sort_2, rect_sort_3 = [], [], []
    for rect_idx, param_list in rect_used.items():
        # 初步判断
        if not len(param_list) == 1:
            continue
        if not len(param_list[0]['group']) == 1:
            continue
        group_rect = param_list[0]['group'][0]
        group_type = group_rect['type']
        if group_type in GROUP_PAIR_FUNCTIONAL:
            rect_sort_1.insert(0, rect_idx)
        elif group_type in ['Media']:
            rect_sort_1.append(rect_idx)
        elif 'seed_list' in group_rect and len(group_rect['seed_list']) > 0:
            rect_sort_1.append(rect_idx)
        elif group_type in ['Armoire', 'Cabinet']:
            if group_rect['size'][1] > UNIT_HEIGHT_ARMOIRE_MIN and group_rect['size'][0] > UNIT_WIDTH_ARMOIRE_MIN:
                rect_sort_2.append(rect_idx)
            else:
                rect_sort_3.append(rect_idx)
        elif group_type in ['Work']:
            rect_sort_3.insert(0, rect_idx)
        else:
            rect_sort_3.append(rect_idx)
    for rect_set in [rect_sort_1, rect_sort_2, rect_sort_3]:
        for rect_idx in rect_set:
            rect_sort.append(rect_idx)

    # 遍历矩形
    for rect_idx in rect_sort:
        param_list = rect_used[rect_idx]
        # 初步判断
        if not len(param_list) == 1:
            continue
        if not len(param_list[0]['group']) == 1:
            continue
        rect_one = rect_list[rect_idx]
        line_idx = rect_one['index']
        line_one = line_list[line_idx]
        rect_ang = normalize_line_angle(rect_one['angle'])
        group_old = param_list[0]['group'][0]
        type_old, size_old, seed_old = group_old['type'], group_old['size'], []
        position_old, angle_old = group_old['position'], rot_to_ang(group_old['rotation'])
        if 'seed_list' in group_old:
            seed_old = group_old['seed_list']
        dump_old_1, dump_old_2 = 0, 0
        if 'size_rest' in group_old:
            dump_old_1 += group_old['size_rest'][1]
            dump_old_2 += group_old['size_rest'][3]
        if 'regulation' in group_old:
            if group_old['regulation'][1] < 0:
                dump_old_1 += group_old['regulation'][1]
            if group_old['regulation'][3] < 0:
                dump_old_2 += group_old['regulation'][3]

        # 避碰范围
        adjust_flag = 1
        x_min_1, z_min_1, x_max_1, z_max_1 = compute_group_scope(group_old, adjust_flag)
        # 扩展范围
        expand_x_min = min(rect_one['expand'][0], x_min_1)
        expand_z_min = min(rect_one['expand'][1], z_min_1)
        expand_x_max = max(rect_one['expand'][2], x_max_1)
        expand_z_max = max(rect_one['expand'][3], z_max_1)
        # 记录范围
        x_min_old, z_min_old, x_max_old, z_max_old = x_min_1, z_min_1, x_max_1, z_max_1
        x_dodge_direct, x_dodge_delete, z_dodge_direct, z_dodge_delete = 0, 0, 0, 0

        # 碰撞检测
        group_dump_list = []
        for group_idx, group_new in enumerate(group_todo):
            # 组合信息
            type_new, size_new, seed_new, center_new = group_new['type'], [], [], 0
            position_new, angle_new = group_new['position'], rot_to_ang(group_new['rotation'])
            if 'size' in group_new:
                size_new = group_new['size']
            if 'seed_list' in group_new:
                seed_new = group_new['seed_list']
            if 'center' in group_new:
                center_new = group_new['center']
            if 'regulation' not in group_new:
                group_new['regulation'] = [0, 0, 0, 0]
            # 组合判断1
            if type_new == type_old:
                if abs(position_old[0] - position_new[0]) < 0.01 and abs(position_old[2] - position_new[2]) < 0.01:
                    continue
            # 组合判断2
            elif type_new in GROUP_TYPE_MAIN:
                continue
            elif type_new in ['Work'] and room_type in ['Library'] and center_new >= 1:
                x_min_2, z_min_2, x_max_2, z_max_2 = compute_group_scope(group_new)
                if x_min_2 > x_max_1 or x_max_2 < x_min_1 or z_min_2 > z_max_1 or z_max_2 < z_min_1:
                    continue
                if determine_line_angle(rect_ang) == 0:
                    if x_min_1 < x_min_2 < x_max_1:
                        x_dlt = x_max_1 - x_min_2
                        if abs(x_dlt) < MID_GROUP_PASS * 2:
                            group_new['position'][0] += x_dlt
                    elif x_min_1 < x_max_2 < x_max_1:
                        x_dlt = x_min_1 - x_max_2
                        if abs(x_dlt) < MID_GROUP_PASS * 2:
                            group_new['position'][0] += x_dlt
                elif determine_line_angle(rect_ang) == 1:
                    if z_min_1 < z_min_2 < z_max_1:
                        z_dlt = z_max_1 - z_min_2
                        if abs(z_dlt) < MID_GROUP_PASS * 2:
                            group_new['position'][2] += z_dlt
                    elif z_min_1 < z_max_2 < z_max_1:
                        z_dlt = z_min_1 - z_max_2
                        if abs(z_dlt) < MID_GROUP_PASS * 2:
                            group_new['position'][2] += z_dlt
                continue
            elif type_new in ['Work'] and room_type in ['Library']:
                continue
            elif type_new in ['Rest'] and room_type in ['Balcony', 'Terrace']:
                continue
            elif type_new in ['Cabinet'] and max(size_new[0], size_new[2]) < 0.5:
                continue
            elif type_old in GROUP_TYPE_MAIN and hor_or_ver(angle_old) <= -1:
                # 平行
                if abs(ang_to_ang(angle_new - angle_old - 0)) < 0.01 \
                        or abs(ang_to_ang(angle_new - angle_old - math.pi)) < 0.01:
                    dlt_x, dlt_z = position_new[0] - position_old[0], position_new[2] - position_old[2]
                    tmp_x = dlt_z * math.sin(-math.pi / 2 - angle_old) + dlt_x * math.cos(-math.pi / 2 - angle_old)
                    tmp_z = dlt_z * math.cos(-math.pi / 2 - angle_old) - dlt_x * math.sin(-math.pi / 2 - angle_old)
                    if abs(tmp_x) > (size_old[0] + size_new[0]) / 2:
                        continue
                    elif abs(tmp_z) > (size_old[2] + size_new[2]) / 2:
                        continue
                # 垂直
                elif abs(ang_to_ang(angle_new - angle_old - math.pi / 2)) < 0.01 \
                        or abs(ang_to_ang(angle_new - angle_old + math.pi / 2)) < 0.01:
                    dlt_x, dlt_z = position_new[0] - position_old[0], position_new[2] - position_old[2]
                    tmp_x = dlt_z * math.sin(-math.pi / 2 - angle_old) + dlt_x * math.cos(-math.pi / 2 - angle_old)
                    tmp_z = dlt_z * math.cos(-math.pi / 2 - angle_old) - dlt_x * math.sin(-math.pi / 2 - angle_old)
                    if abs(tmp_x) > (size_old[0] + size_new[2]) / 2:
                        continue
                    elif abs(tmp_z) > (size_old[2] + size_new[0]) / 2:
                        continue
            # 组合判断3
            if type_old in GROUP_PAIR_FUNCTIONAL:
                if type_new in GROUP_PAIR_FUNCTIONAL[type_old]:
                    continue
            if type_old not in GROUP_TYPE_MAIN and len(seed_old) <= 0 and len(seed_new) > 0:
                continue

            # 避碰范围
            if type_old in ['Bed', 'Media'] and type_new in GROUP_TYPE_REST:
                x_min_2, z_min_2, x_max_2, z_max_2 = compute_group_scope(group_new)
            elif type_old in ['Work', 'Rest'] and type_new in GROUP_TYPE_REST:
                x_min_2, z_min_2, x_max_2, z_max_2 = compute_group_scope(group_new)
            elif type_old in ['Bath', 'Toilet'] and type_new in GROUP_TYPE_REST:
                x_min_2, z_min_2, x_max_2, z_max_2 = compute_group_scope(group_new)
            elif type_old in ['Cabinet'] and type_new in ['Cabinet'] and room_type in ROOM_TYPE_FOR_REST_4:
                x_min_2, z_min_2, x_max_2, z_max_2 = compute_group_scope(group_new)
            else:
                x_min_2, z_min_2, x_max_2, z_max_2 = compute_group_scope(group_new)
            # 通行空间
            group_pass = 0
            if type_old in ['Bed', 'Media'] and type_new in GROUP_TYPE_REST:
                if type_old in ['Media'] and type_new in ['Rest']:
                    group_pass = MIN_GROUP_PASS * 0.0
                elif type_new in ['Work']:
                    group_pass = MIN_GROUP_PASS * 1.0
                elif type_new in ['Cabinet'] and max(size_new[0], size_new[2]) < 0.6:
                    group_pass = MIN_GROUP_PASS * 0.0
                elif room_type in ['KidsRoom']:
                    group_pass = MIN_GROUP_PASS * 1.0
                else:
                    group_pass = MIN_GROUP_PASS * 2.0
                if 'obj_type' in group_old and group_old['obj_type'] == 'bed/bed set':
                    group_pass = 0
            elif type_old in ['Dining'] and type_new in GROUP_TYPE_REST:
                if abs(normalize_line_angle(angle_old - angle_new)) <= 0.1:
                    group_pass = 0
                elif abs(normalize_line_angle(angle_old - angle_new - math.pi)) <= 0.1:
                    group_pass = 0
            elif type_old in ['Work'] and type_new in GROUP_TYPE_REST:
                if room_type not in ['Library']:
                    group_pass = 0
                if type_new in ['Rest']:
                    group_pass = 0
            elif type_old in ['Bath', 'Toilet'] and type_new in ['Appliance']:
                group_pass = 0
            elif type_old in ['Toilet'] and type_new in GROUP_TYPE_REST:
                group_pass = 0
            elif type_old in GROUP_TYPE_REST and type_new in GROUP_TYPE_REST:
                group_pass = 0
            dump_pass = 0
            if type_old in ['Bed'] and type_new in ['Armoire', 'Cabinet']:
                if abs(angle_old - angle_new) > 0.1:
                    dump_pass = dump_old_1 + dump_old_2 - 0.01
                if dump_pass > MIN_GROUP_PASS:
                    group_pass = min(MIN_GROUP_PASS * 1.0, group_pass)
            face_pass = group_pass
            if type_old in ['Bed'] and type_new in ['Armoire', 'Cabinet']:
                face_pass = min(group_pass, 0.2)
            elif type_old in ['Dining'] and type_new in ['Armoire', 'Cabinet']:
                face_pass = 0
            # 竖墙避碰
            if determine_line_angle(rect_ang) == 0:
                if determine_line_angle(angle_new) == 0:
                    group_pass = 0.0
                if x_min_2 >= x_max_1 + face_pass or x_max_2 <= x_min_1 - face_pass:
                    continue
                if abs(ang_to_ang(angle_new - angle_old - math.pi)) < 0.1 and room_area <= 15:
                    if type_new in ['Armoire', 'Cabinet']:
                        if x_min_2 >= x_max_1 or x_max_2 <= x_min_1:
                            continue
                        regulation_new = group_new['regulation']
                        if x_max_2 - 0.2 <= x_min_1 <= x_max_2 and size_new[2] > 0.2 and regulation_new[2] >= -0.1:
                            regulation_new[2] -= (x_max_2 - x_min_1 + 0.1)
                            continue
                        if x_min_2 + 0.2 >= x_max_1 >= x_min_2 and size_new[2] > 0.2 and regulation_new[2] >= -0.1:
                            regulation_new[2] -= (x_max_1 - x_min_2 + 0.1)
                            continue

                result, p1, p2, p_min, p_max, p_direct, p_delete = compute_group_dodge(z_min_1, z_max_1, expand_z_min, expand_z_max, z_min_2, z_max_2, group_pass, dump_pass)
                # 避碰失败
                if result <= -1:
                    keep_flag = False
                    if 'seed_list' in group_new and len(group_new['seed_list']) > 0:
                        keep_flag = True
                    elif type_old in ['Bed'] and type_new in ['Work'] and room_type in ROOM_TYPE_FOR_REST_2:
                        if abs(normalize_line_angle(angle_old - angle_new - math.pi)) <= 0.1:
                            dump_new = 0
                            if x_min_2 >= x_max_1 - MIN_GROUP_PASS:
                                dump_new = x_min_2 - x_max_1
                            elif x_max_2 <= x_min_1 + MIN_GROUP_PASS:
                                dump_new = x_min_1 - x_max_2
                            if dump_new < 0 and 'regulation' in group_new:
                                dump_old = group_new['regulation'][2]
                                group_new['regulation'][2] = min(dump_new, dump_old)
                                keep_flag = True
                        elif abs(normalize_line_angle(angle_old - angle_new - math.pi / 2)) <= 0.1 or \
                                abs(normalize_line_angle(angle_old - angle_new + math.pi / 2)) <= 0.1:
                            dump_new = 0
                            if z_min_2 >= z_max_1 - MIN_GROUP_PASS and abs(normalize_line_angle(angle_new - math.pi)) <= 0.1:
                                dump_new = z_min_2 - z_max_1
                            elif z_max_2 <= z_min_1 + MIN_GROUP_PASS and abs(normalize_line_angle(angle_new - 0)) <= 0.1:
                                dump_new = z_min_1 - z_max_2
                            if dump_new < 0:
                                dump_old = group_new['regulation'][2]
                                group_new['regulation'][2] = min(dump_new, dump_old)
                                keep_flag = True
                    if not keep_flag:
                        group_dump_list.insert(0, group_idx)
                        continue
                elif p_direct * z_dodge_direct <= -1:
                    group_dump_list.insert(0, group_idx)
                    continue
                # 避碰合适
                z_min_1, z_max_1, expand_z_min, expand_z_max = p1, p2, p_min, p_max
                if p_delete > z_dodge_delete:
                    z_dodge_direct = p_direct
                    z_dodge_delete = p_delete
            # 横墙避碰
            elif determine_line_angle(rect_ang) == 1:
                if determine_line_angle(angle_new) == 1:
                    group_pass = 0.0
                if z_min_2 >= z_max_1 + face_pass or z_max_2 <= z_min_1 - face_pass:
                    continue
                if abs(ang_to_ang(angle_new - angle_old - math.pi)) < 0.1 and room_area <= 15:
                    if type_new in ['Armoire', 'Cabinet']:
                        if z_min_2 >= z_max_1 or z_max_2 <= z_min_1:
                            continue
                        regulation_new = group_new['regulation']
                        if z_max_2 - 0.2 <= z_min_1 <= z_max_2 and size_new[2] > 0.2 and regulation_new[2] >= -0.1:
                            regulation_new[2] -= (z_max_2 - z_min_1 + 0.1)
                            continue
                        if z_min_2 + 0.2 >= z_max_1 >= z_min_2 and size_new[2] > 0.2 and regulation_new[2] >= -0.1:
                            regulation_new[2] -= (z_max_1 - z_min_2 + 0.1)
                            continue

                result, p1, p2, p_min, p_max, p_direct, p_delete = compute_group_dodge(x_min_1, x_max_1, expand_x_min, expand_x_max, x_min_2, x_max_2, group_pass, dump_pass)
                # 避碰失败
                if result <= -1:
                    keep_flag = False
                    if 'seed_list' in group_new and len(group_new['seed_list']) > 0:
                        keep_flag = True
                    elif type_old in ['Bed'] and type_new in ['Work'] and room_type in ROOM_TYPE_FOR_REST_2:
                        if abs(normalize_line_angle(angle_old - angle_new - math.pi)) <= 0.1:
                            dump_new = 0
                            if z_min_2 >= z_max_1 - MIN_GROUP_PASS:
                                dump_new = z_min_2 - z_max_1
                            elif z_max_2 <= z_min_1 + MIN_GROUP_PASS:
                                dump_new = z_min_1 - z_max_2
                            if dump_new < 0:
                                dump_old = group_new['regulation'][2]
                                group_new['regulation'][2] = min(dump_new, dump_old)
                                keep_flag = True
                        elif abs(normalize_line_angle(angle_old - angle_new - math.pi / 2)) <= 0.1 or \
                                abs(normalize_line_angle(angle_old - angle_new + math.pi / 2)) <= 0.1:
                            dump_new = 0
                            if x_min_2 >= x_max_1 - MIN_GROUP_PASS and abs(normalize_line_angle(angle_new + math.pi / 2)) <= 0.1:
                                dump_new = x_min_2 - x_max_1
                            elif x_max_2 <= x_min_1 + MIN_GROUP_PASS and abs(normalize_line_angle(angle_new - math.pi / 2)) <= 0.1:
                                dump_new = x_min_1 - x_max_2
                            if dump_new < 0:
                                dump_old = group_new['regulation'][2]
                                group_new['regulation'][2] = min(dump_new, dump_old)
                                keep_flag = True
                    if not keep_flag:
                        group_dump_list.insert(0, group_idx)
                        continue
                elif p_direct * x_dodge_direct <= -1:
                    group_dump_list.insert(0, group_idx)
                    continue
                # 避碰合适
                x_min_1, x_max_1, expand_x_min, expand_x_max = p1, p2, p_min, p_max
                if p_delete > x_dodge_delete:
                    x_dodge_direct = p_direct
                    x_dodge_delete = p_delete
            # 斜墙避碰
            else:
                if x_min_2 + 0.01 >= x_max_1 or x_max_2 - 0.01 <= x_min_1:
                    continue
                if z_min_2 + 0.01 >= z_max_1 or z_max_2 - 0.01 <= z_min_1:
                    continue
                group_dump_list.insert(0, group_idx)
                continue

        # 碰撞修复
        rect_p1, rect_p2 = rect_one['p1'], rect_one['p2']
        x_dlt = x_min_1 - x_min_old
        if abs(x_dlt) < abs(x_max_1 - x_max_old):
            x_dlt = x_max_1 - x_max_old
        if 0 < abs(x_dlt) < 0.05:
            x_dlt = 0
        z_dlt = z_min_1 - z_min_old
        if abs(z_dlt) < abs(z_max_1 - z_max_old):
            z_dlt = z_max_1 - z_max_old
        if 0 < abs(z_dlt) < 0.05:
            z_dlt = 0
        #
        if z_min_1 < expand_z_min:
            if z_dodge_direct * (rect_p2[1] - rect_p1[1]) > 0:
                z_dlt_max = dump_old_1 + (z_min_old - expand_z_min)
                z_dlt = max(0 - z_dlt_max, z_dlt)
            else:
                z_dlt_max = dump_old_2 + (z_min_old - expand_z_min)
                z_dlt = max(0 - z_dlt_max, z_dlt)
        elif z_max_1 > expand_z_max:
            if z_dodge_direct * (rect_p2[1] - rect_p1[1]) > 0:
                z_dlt_max = dump_old_1 + (expand_z_max - z_max_old)
                z_dlt = min(0 + z_dlt_max, z_dlt)
            else:
                z_dlt_max = dump_old_2 + (expand_z_max - z_max_old)
                z_dlt = min(0 + z_dlt_max, z_dlt)
        group_old['position'][0] += x_dlt
        group_old['position'][2] += z_dlt
        rect_one['expand'] = [expand_x_min, expand_z_min, expand_x_max, expand_z_max]
        group_old['expand'] = [expand_x_min, expand_z_min, expand_x_max, expand_z_max]

        # 裁剪修复
        if type_old in GROUP_PAIR_FUNCTIONAL:
            rect_p1, rect_p2 = rect_one['p1'], rect_one['p2']
            dump_all, dump_dir = 0, 0
            if x_dodge_delete > 0:
                dump_all = x_dodge_delete
                if x_dodge_direct * (rect_p2[0] - rect_p1[0]) > 0:
                    dump_dir = -1
                else:
                    dump_dir = 1
            elif z_dodge_delete > 0:
                dump_all = z_dodge_delete
                if z_dodge_direct * (rect_p2[1] - rect_p1[1]) > 0:
                    dump_dir = -1
                else:
                    dump_dir = 1
            if dump_dir <= -1 and dump_all > 0:
                if dump_old_1 > dump_all:
                    group_old['regulation'][1] -= dump_old_1
                else:
                    group_old['regulation'][1] -= dump_old_1
                    group_old['regulation'][3] -= (dump_all - dump_old_1)
            elif dump_dir >= 1 and dump_all > 0:
                if dump_old_2 > dump_all:
                    group_old['regulation'][3] -= dump_old_2
                else:
                    group_old['regulation'][3] -= dump_old_2
                    group_old['regulation'][1] -= (dump_all - dump_old_2)

        # 正对修复
        pair_dict = {'Media': ['Bed']}
        for group_idx, group_new in enumerate(group_todo):
            if type_old not in pair_dict:
                break
            if group_new['type'] not in pair_dict[type_old]:
                continue
            x_old, z_old = group_old['position'][0], group_old['position'][2]
            x_new, z_new = group_new['position'][0], group_new['position'][2]
            x_dlt_old, z_dlt_old = 0, 0
            x_dlt_new, z_dlt_new = 0, 0
            offset = [0, 0, 0]
            if 'offset' in group_new:
                offset = group_new['offset']
            if determine_line_angle(rect_ang) == 0:
                if group_new['type'] in ['Bed']:
                    if abs(ang_to_ang(rect_ang - math.pi / 2)) < 0.1:
                        z_new += offset[0]
                    elif abs(ang_to_ang(rect_ang + math.pi / 2)) < 0.1:
                        z_new -= offset[0]
                # 调整自己
                if z_new - z_old > 0.05:
                    x_min_old, z_min_old, x_max_old, z_max_old = compute_group_scope(group_old)
                    z_dlt_old = z_new - z_old
                    if z_dlt_old > expand_z_max - z_max_old:
                        z_dlt_old = max(expand_z_max - z_max_old, 0)
                elif z_new - z_old < -0.05:
                    x_min_old, z_min_old, x_max_old, z_max_old = compute_group_scope(group_old)
                    z_dlt_old = z_new - z_old
                    if z_dlt_old < expand_z_min - z_min_old:
                        z_dlt_old = min(expand_z_min - z_min_old, 0)
            elif determine_line_angle(rect_ang) == 1:
                if group_new['type'] in ['Bed']:
                    if abs(ang_to_ang(rect_ang - 0)) < 0.1:
                        z_new -= offset[0]
                    elif abs(ang_to_ang(rect_ang + math.pi)) < 0.1:
                        z_new += offset[0]
                # 调整自己
                if x_new - x_old > 0.05:
                    x_min_old, z_min_old, x_max_old, z_max_old = compute_group_scope(group_old)
                    x_dlt_old = x_new - x_old
                    if x_dlt_old > expand_x_max - x_max_old:
                        x_dlt_old = max(expand_x_max - x_max_old, 0)
                elif x_new - x_old < -0.05:
                    x_min_old, z_min_old, x_max_old, z_max_old = compute_group_scope(group_old)
                    x_dlt_old = x_new - x_old
                    if x_dlt_old < expand_x_min - x_min_old:
                        x_dlt_old = min(expand_x_min - x_min_old, 0)
            group_old['position'][0] += x_dlt_old
            group_old['position'][2] += z_dlt_old
            group_new['position'][0] += x_dlt_new
            group_new['position'][2] += z_dlt_new
            break

        # 舍弃处理
        for group_dump_idx in group_dump_list:
            group1 = group_todo[group_dump_idx]
            type1 = group1['type']
            pos1 = group1['position']
            if type1 in ['Meeting', 'Dining', 'Bed']:
                continue
            group_todo.pop(group_dump_idx)
            for param_rect_idx, param_used_list in rect_used.items():
                for param_used_idx, param_used_one in enumerate(param_used_list):
                    group_used_list = param_used_one['group']
                    for group_used_idx, group_used_one in enumerate(group_used_list):
                        group2 = group_used_one
                        type2 = group2['type']
                        pos2 = group2['position']
                        if type1 == type2 and abs(pos1[0] - pos2[0]) < 0.01 and abs(pos1[2] - pos2[2]) < 0.01:
                            group_used_list.pop(group_used_idx)
                            break
                    if len(group_used_list) <= 0:
                        param_used_list.pop(param_used_idx)
                        break
                if len(param_used_list) <= 0:
                    break

    # 舍弃处理
    rect_sort = list(rect_used.keys())
    for rect_idx in rect_sort:
        param_list = rect_used[rect_idx]
        if len(param_list) <= 0:
            rect_used.pop(rect_idx)


# 布局避让
def room_rect_center_dodge(group_todo, group_new):
    if len(group_new) <= 0:
        return
    group_size_new = group_new['size']
    group_pos_new = group_new['position']
    group_rot_new = group_new['rotation']
    group_ang_new = rot_to_ang(group_rot_new)
    for group_idx in range(len(group_todo) - 1, -1, -1):
        group_old = group_todo[group_idx]
        if group_old == group_new:
            continue
        if group_old['type'] in GROUP_TYPE_MAIN:
            continue
        group_pass_old = [0, 0, 0]
        if group_old['type'] in ['Cabinet']:
            group_pass_old[2] = 0.1
        elif group_old['type'] in ['Armoire', 'Appliance']:
            group_pass_old[2] = 0.4
        group_size_old = group_old['size']
        group_pos_old = group_old['position']
        group_rot_old = group_old['rotation']
        group_ang_old = rot_to_ang(group_rot_old)
        tmp_x = group_pos_new[0] - group_pos_old[0]
        tmp_z = group_pos_new[2] - group_pos_old[2]
        distance_new_x = tmp_z * math.sin(-group_ang_new) + tmp_x * math.cos(-group_ang_new)
        distance_new_z = tmp_z * math.cos(-group_ang_new) - tmp_x * math.sin(-group_ang_new)
        if abs(ang_to_ang(group_ang_old - group_ang_new) + math.pi / 2) <= 0.01 or \
                abs(ang_to_ang(group_ang_old - group_ang_new) - math.pi / 2) <= 0.01:
            distance_min_x = abs(group_size_new[0] / 2 + group_size_old[2] / 2 + group_pass_old[2])
            distance_min_z = abs(group_size_new[2] / 2 + group_size_old[0] / 2 + group_pass_old[0])
        else:
            distance_min_x = abs(group_size_new[0] / 2 + group_size_old[0] / 2 + group_pass_old[0])
            distance_min_z = abs(group_size_new[2] / 2 + group_size_old[2] / 2 + group_pass_old[2])
        if abs(distance_new_x) < distance_min_x - 0.1 and abs(distance_new_z) < distance_min_z - 0.1:
            group_todo.pop(group_idx)
        elif group_old['type'] in ['Rest'] and group_new['type'] in ['Work']:
            group_pass = 0.1
            if distance_min_x - 0.1 < abs(distance_new_x) < distance_min_x + group_pass:
                tmp_x, tmp_z = 0, 0
                if distance_new_x >= 0:
                    tmp_x = distance_min_x + group_pass - distance_new_x
                else:
                    tmp_x = -(distance_min_x + group_pass) - distance_new_x
                add_x = tmp_z * math.sin(group_ang_new) + tmp_x * math.cos(group_ang_new)
                add_z = tmp_z * math.cos(group_ang_new) - tmp_x * math.sin(group_ang_new)
                group_pos_new[0] += add_x
                group_pos_new[2] += add_z
            elif distance_min_z - 0.1 < abs(distance_new_z) < distance_min_z + group_pass:
                tmp_x, tmp_z = 0, 0
                if distance_new_z >= 0:
                    tmp_z = distance_min_z + group_pass - distance_new_z
                else:
                    tmp_z = -(distance_min_z + group_pass) - distance_new_z
                add_x = tmp_z * math.sin(group_ang_new) + tmp_x * math.cos(group_ang_new)
                add_z = tmp_z * math.cos(group_ang_new) - tmp_x * math.sin(group_ang_new)
                group_pos_new[0] += add_x
                group_pos_new[2] += add_z


# 计算区域
def room_rect_update_region(group_one, line_list, edge_idx, rely_idx, rely_rat, rely_back):
    # 组合信息
    group_type, group_size = group_one['type'], group_one['size']
    group_regulate, group_neighbor = [0, 0, 0, 0], [0, 0, 0, 0]
    if 'regulation' in group_one:
        group_regulate = group_one['regulation']
    if 'neighbor_base' in group_one:
        group_neighbor = group_one['neighbor_base']
    neighbor_best, neighbor_zone = group_neighbor[:], group_neighbor[:]
    if rely_idx < 0 or edge_idx < 0:
        group_one['neighbor_best'] = neighbor_best
        group_one['neighbor_zone'] = neighbor_zone
        return
    if len(rely_rat) <= 0:
        rely_rat = [0, 1]
    group_width = group_size[0] + group_regulate[1] + group_regulate[3]
    group_depth = group_size[2] + group_regulate[0] + group_regulate[2]
    depth_best = group_depth
    if edge_idx in [0, 2]:
        depth_best = group_depth
    else:
        depth_best = group_width
    # 两侧进深
    line_one = line_list[rely_idx]
    depth_ext = line_one['depth_ext']
    if group_type in ['Dining', 'Work', 'Bath']:
        depth_ext = line_one['depth_all']
    elif rely_rat[0] > 0.1 or rely_rat[1] < 0.9:
        depth_ext = line_one['depth_all']
    depth_max = 0
    depth_pre, depth_post = line_one['depth_pre'], line_one['depth_post']
    depth_pre_more, depth_post_more = line_one['depth_pre_more'], line_one['depth_post_more']
    for depth_one in depth_ext:
        if depth_one[1] - depth_one[0] > 0.1 and depth_one[2] > 5:
            if depth_max > 5:
                depth_max = min(depth_max, depth_one[2])
            else:
                depth_max = depth_one[2]
        elif depth_one[0] < 0.5 < depth_one[1] and depth_one[2] > depth_max:
            depth_max = depth_one[2]
    if depth_max < min(depth_pre_more, depth_post_more):
        depth_max = max(depth_pre_more, depth_post_more)
    # 两侧宽度
    width_pre, width_post, width_pre_more, width_post_more = 0, 0, 0, 0
    ratio_pre, ratio_post, ratio_pre_more, ratio_post_more = rely_rat[0], rely_rat[1], rely_rat[0], rely_rat[1]
    for depth_idx, depth_one in enumerate(depth_ext):
        depth_good = False
        if abs(depth_one[2] - depth_max) < 0.1:
            depth_good = True
        elif depth_one[2] > max(depth_max + 0.1, 3):
            depth_good = True
        elif depth_one[2] > depth_max + 0.1 and group_type in ['Bath']:
            depth_good = True
        elif depth_one[2] > min(depth_max + 0.1, 2) and group_type in ['Media']:
            if depth_one[1] < 0.2 or depth_one[0] > 0.8:
                depth_good = True
        elif depth_one[2] > depth_best and group_type in ['Dining']:
            if depth_one[1] < rely_rat[1] + 0.1:
                depth_good = True
        if depth_good:
            if depth_one[0] <= ratio_pre:
                ratio_pre = depth_one[0]
                ratio_pre_more = ratio_pre
                if depth_idx == 0 and depth_one[0] > 0:
                    ratio_pre = 0
                    ratio_pre_more = 0
            if depth_one[1] >= ratio_post:
                ratio_post = depth_one[1]
                ratio_post_more = ratio_post
                if depth_idx == len(depth_ext) - 1 and depth_one[1] < 1:
                    ratio_post = 1
                    ratio_post_more = 1
    # 前序
    if ratio_pre <= 0 + 0.01:
        ratio_pre_old = ratio_pre
        #
        line_new, line_idx = line_one, rely_idx
        for side_idx in range(5):
            if not line_new['score_pre'] == 1:
                if side_idx == 0 and line_new['score_pre'] == 2 and rely_rat[0] <= 0 - 0.1 and group_type in ['Dining']:
                    ratio_pre = min(0 - MID_GROUP_PASS / line_one['width'], ratio_pre)
                break
            line_idx = (line_idx - 1 + len(line_list)) % len(line_list)
            line_new = line_list[line_idx]
            type_new, width_new = line_new['type'], line_new['width']
            if type_new in [UNIT_TYPE_GROUP]:
                line_idx_2 = (line_idx - 1 + len(line_list)) % len(line_list)
                line_new_2 = line_list[line_idx_2]
                type_new_2, width_new_2 = line_new_2['type'], line_new_2['width']
                if type_new_2 in [UNIT_TYPE_GROUP] and line_new['unit_edge'] in [1, 3] and group_type not in ['Work', 'Rest']:
                    ratio_add = -MIN_GROUP_PASS / line_one['width']
                    ratio_pre -= ratio_add
                break
            if type_new in [UNIT_TYPE_DOOR]:
                if width_new >= UNIT_WIDTH_HOLE and edge_idx in [1, 3]:
                    ratio_add = MID_GROUP_PASS / line_one['width']
                    ratio_pre -= ratio_add
                break
            if type_new in [UNIT_TYPE_SIDE]:
                if width_new > UNIT_DEPTH_CURTAIN + 0.01:
                    ratio_add = -MIN_GROUP_PASS / line_one['width']
                    ratio_pre -= ratio_add
                break
            if type_new in [UNIT_TYPE_WINDOW]:
                if edge_idx == 1:
                    break
                elif group_width > max(width_new * 2, 2) or line_one['height'] < UNIT_HEIGHT_WALL - 0.01:
                    ratio_add = -MIN_GROUP_PASS / line_one['width']
                    ratio_pre -= ratio_add
                    break
            if type_new in [UNIT_TYPE_AISLE]:
                break
            depth_ext = line_new['depth_ext']
            if group_type in ['Dining', 'Work', 'Bath']:
                depth_ext = line_new['depth_all']
            elif group_type in ['Bed'] and group_width > 2:
                depth_ext = line_new['depth_all']
            if len(depth_ext) <= 0:
                break
            depth_one = depth_ext[-1]
            if depth_max - 0.1 < depth_one[2] < depth_max + 0.1:
                if line_new['score_pre'] == 1:
                    line_idx_2 = (line_idx - 1 + len(line_list)) % len(line_list)
                    line_new_2 = line_list[line_idx_2]
                    type_new_2, width_new_2 = line_new_2['type'], line_new_2['width']
                    if type_new_2 in [UNIT_TYPE_GROUP] and depth_one[1] - depth_one[0] > 0.99:
                        ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                        if ratio_add > MIN_GROUP_PASS / line_one['width'] and group_type in ['Toilet']:
                            break
                        if ratio_add > 0 and group_type in ['Toilet'] and edge_idx in [1, 3]:
                            break
                        ratio_pre -= ratio_add
                        ratio_pre = (ratio_pre_old + ratio_pre) / 2
                        break
                    if type_new_2 in [UNIT_TYPE_AISLE] and line_new_2['depth'] <= 0:
                        ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                        ratio_pre -= ratio_add
                        ratio_pre = (ratio_pre_old + ratio_pre) / 2
                        break
                    if width_new_2 > 1 and group_type in ['Bed'] and group_width > 2:
                        ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                        ratio_pre -= ratio_add
                        break
                ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                if (rely_rat[0] - (ratio_pre - ratio_add)) * line_one['width'] > max(group_width, group_depth, 1):
                    if group_type in ['Media'] and edge_idx == 0:
                        ratio_pre -= ratio_add
                    elif group_type in ['Armoire', 'Cabinet'] and edge_idx == 0:
                        ratio_pre -= ratio_add
                    break
                else:
                    if ratio_add > MIN_GROUP_PASS / line_one['width'] and group_type in ['Meeting'] and edge_idx == 1:
                        break
                    if ratio_add > MIN_GROUP_PASS / line_one['width'] and group_type in ['Media'] and \
                            line_new['depth_pre'] < min(group_width, group_depth):
                        break
                    if ratio_add > MID_GROUP_PASS / line_one['width'] and group_type in ['Work', 'Rest']:
                        break
                    if ratio_add > MIN_GROUP_PASS / line_one['width'] and group_type in ['Toilet']:
                        break
                    ratio_pre -= ratio_add
                    if group_type in ['Bed'] and group_width > 2 and width_new > 1:
                        ratio_pre = (ratio_pre_old + ratio_pre) / 2
                        break
            if depth_one[0] > 0 + 0.01:
                break
        #
        line_new, line_idx = line_one, rely_idx
        for side_idx in range(5):
            if not line_new['score_pre'] == 1:
                break
            line_idx = (line_idx - 1 + len(line_list)) % len(line_list)
            line_new = line_list[line_idx]
            type_new, width_new = line_new['type'], line_new['width']
            if type_new in [UNIT_TYPE_GROUP]:
                if line_one['unit_group'] in ['Bath', 'Toilet']:
                    pass
                elif line_new['unit_group'] == line_one['unit_group']:
                    pass
                else:
                    break
            depth_ext = line_new['depth_ext']
            if len(depth_ext) <= 0:
                break
            depth_one = depth_ext[-1]
            if depth_max - 0.1 < depth_one[2] < depth_max + 0.1:
                if type_new in [UNIT_TYPE_DOOR] and depth_one[2] > 2:
                    break
                if line_new['score_pre'] == 1:
                    line_idx_2 = (line_idx - 1 + len(line_list)) % len(line_list)
                    line_new_2 = line_list[line_idx_2]
                    type_new_2 = line_new_2['type']
                    if type_new_2 in [UNIT_TYPE_GROUP] and depth_one[1] - depth_one[0] > 0.99:
                        if line_one['unit_group'] in ['Bath', 'Toilet']:
                            pass
                        elif line_new_2['unit_group'] == line_one['unit_group']:
                            pass
                        else:
                            ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                            ratio_pre_more -= ratio_add
                            ratio_pre_more = (ratio_pre_old + ratio_pre_more) / 2
                            break
                ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                ratio_pre_more -= ratio_add
            if depth_one[0] > 0 + 0.01:
                break
    # 后序
    if ratio_post >= 1 - 0.01:
        ratio_post_old = ratio_post
        #
        line_new, line_idx = line_one, rely_idx
        for side_idx in range(5):
            if not line_new['score_post'] == 1:
                if side_idx == 0 and line_new['score_post'] == 2 and rely_rat[1] >= 1 + 0.1 and group_type in ['Dining']:
                    ratio_post = max(1 + MID_GROUP_PASS / line_one['width'], ratio_post)
                break
            line_idx = (line_idx + 1 + len(line_list)) % len(line_list)
            line_new = line_list[line_idx]
            type_new, width_new = line_new['type'], line_new['width']
            if type_new in [UNIT_TYPE_GROUP]:
                line_idx_2 = (line_idx + 1 + len(line_list)) % len(line_list)
                line_new_2 = line_list[line_idx_2]
                type_new_2, width_new_2 = line_new_2['type'], line_new_2['width']
                if type_new_2 in [UNIT_TYPE_GROUP] and line_new['unit_edge'] in [1, 3] and group_type not in ['Work', 'Rest']:
                    ratio_add = -MIN_GROUP_PASS / line_one['width']
                    ratio_post += ratio_add
                if type_new_2 in [UNIT_TYPE_AISLE] and line_new['depth'] <= 0:
                    ratio_add = -MIN_GROUP_PASS / line_one['width']
                    ratio_post += ratio_add
                break
            if type_new in [UNIT_TYPE_DOOR]:
                if width_new >= UNIT_WIDTH_HOLE and edge_idx in [1, 3]:
                    ratio_add = MID_GROUP_PASS / line_one['width']
                    ratio_post += ratio_add
                break
            if type_new in [UNIT_TYPE_SIDE]:
                if width_new > UNIT_DEPTH_CURTAIN + 0.01:
                    ratio_add = -MIN_GROUP_PASS / line_one['width']
                    ratio_post += ratio_add
                break
            if type_new in [UNIT_TYPE_WINDOW]:
                if edge_idx == 3:
                    break
                elif group_width > max(width_new * 2, 2) or line_one['height'] < UNIT_HEIGHT_WALL - 0.01:
                    ratio_add = -MIN_GROUP_PASS / line_one['width']
                    ratio_post += ratio_add
                    break
            if type_new in [UNIT_TYPE_AISLE]:
                break
            depth_ext = line_new['depth_ext']
            if group_type in ['Dining', 'Work', 'Bath']:
                depth_ext = line_new['depth_all']
            elif group_type in ['Bed'] and group_width > 2:
                depth_ext = line_new['depth_all']
            if len(depth_ext) <= 0:
                break
            depth_one = depth_ext[0]
            if depth_max - 0.1 < depth_one[2] < depth_max + 0.1:
                if line_new['score_post'] == 1:
                    line_idx_2 = (line_idx + 1 + len(line_list)) % len(line_list)
                    line_new_2 = line_list[line_idx_2]
                    type_new_2, width_new_2 = line_new_2['type'], line_new_2['width']
                    if type_new_2 in [UNIT_TYPE_GROUP] and depth_one[1] - depth_one[0] > 0.99:
                        ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                        if ratio_add > MIN_GROUP_PASS / line_one['width'] and group_type in ['Toilet']:
                            break
                        if ratio_add > 0 and group_type in ['Toilet'] and edge_idx in [1, 3]:
                            break
                        ratio_post += ratio_add
                        ratio_post = (ratio_post_old + ratio_post) / 2
                        break
                    if type_new_2 in [UNIT_TYPE_AISLE] and line_new_2['depth'] <= 0:
                        ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                        ratio_post += ratio_add
                        ratio_post = (ratio_post_old + ratio_post) / 2
                        break
                    if width_new_2 > 1 and group_type in ['Bed'] and group_width > 2:
                        ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                        ratio_post += ratio_add
                        ratio_post = (ratio_post_old + ratio_post) / 2
                        break
                ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                if ((ratio_post + ratio_add) - rely_rat[1]) * line_one['width'] > max(group_width, group_depth, 1):
                    if group_type in ['Media'] and edge_idx == 0:
                        ratio_post += ratio_add
                    elif group_type in ['Armoire', 'Cabinet'] and edge_idx == 0:
                        ratio_post += ratio_add
                    break
                else:
                    if ratio_add > MIN_GROUP_PASS / line_one['width'] and group_type in ['Meeting'] and edge_idx == 3:
                        break
                    if ratio_add > MIN_GROUP_PASS / line_one['width'] and group_type in ['Media'] and \
                            line_new['depth_post'] < min(group_width, group_depth):
                        break
                    if ratio_add > MID_GROUP_PASS / line_one['width'] and group_type in ['Work', 'Rest']:
                        break
                    if ratio_add > MIN_GROUP_PASS / line_one['width'] and group_type in ['Toilet']:
                        break
                    ratio_post += ratio_add
                    if group_type in ['Bed'] and group_width > 2 and width_new > 1:
                        ratio_post = (ratio_post_old + ratio_post) / 2
                        break
            if depth_one[1] < 1 - 0.01:
                break
        #
        line_new, line_idx = line_one, rely_idx
        for side_idx in range(5):
            if not line_new['score_post'] == 1:
                break
            line_idx = (line_idx + 1 + len(line_list)) % len(line_list)
            line_new = line_list[line_idx]
            type_new, width_new = line_new['type'], line_new['width']
            if type_new in [UNIT_TYPE_GROUP]:
                if line_one['unit_group'] in ['Bath', 'Toilet']:
                    pass
                elif line_new['unit_group'] == line_one['unit_group']:
                    pass
                else:
                    break
            depth_ext = line_new['depth_ext']
            if len(depth_ext) <= 0:
                break
            depth_one = depth_ext[0]
            if depth_max - 0.1 < depth_one[2] < depth_max + 0.1:
                if type_new in [UNIT_TYPE_DOOR] and depth_one[2] > 2:
                    break
                if line_new['score_post'] == 1:
                    line_idx_2 = (line_idx + 1 + len(line_list)) % len(line_list)
                    line_new_2 = line_list[line_idx_2]
                    type_new_2 = line_new_2['type']
                    if type_new_2 in [UNIT_TYPE_GROUP] and depth_one[1] - depth_one[0] > 0.99:
                        if line_one['unit_group'] in ['Bath', 'Toilet']:
                            pass
                        elif line_new_2['unit_group'] == line_one['unit_group']:
                            pass
                        else:
                            ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                            ratio_post_more += ratio_add
                            ratio_post_more = (ratio_post_old + ratio_post_more) / 2
                            break
                ratio_add = line_new['width'] * (depth_one[1] - depth_one[0]) / line_one['width']
                ratio_post_more += ratio_add
            if depth_one[1] < 1 - 0.01:
                break
    # 计算
    if abs(ratio_pre - ratio_post) > 0.01:
        width_cur = line_one['width']
        width_pre = width_cur * (rely_rat[0] - ratio_pre)
        width_post = width_cur * (ratio_post - rely_rat[1])
        if width_pre > 1.5 > width_post > 0.5:
            width_pre = width_post
        elif width_post > 1.5 > width_pre > 0.5:
            width_post = width_pre
        elif width_pre > 1.0 > width_post > 0.1:
            width_pre = width_post
        elif width_post > 1.0 > width_pre > 0.1:
            width_post = width_pre
        width_pre_more = width_cur * (rely_rat[0] - ratio_pre_more)
        width_post_more = width_cur * (ratio_post_more - rely_rat[1])
    # 最佳
    if edge_idx in [0, 2]:
        depth_best = group_depth + rely_back
    else:
        depth_best = group_width + rely_back
    if min(depth_pre, depth_post) * 0.5 >= max(depth_best - 0.01, 0.8) and group_type in ['Media', 'Work', 'Rest']:
        depth_best = min(depth_pre, depth_post) * 0.5
        if group_type in ['Media']:
            depth_best = min(depth_best, 0.6)
        else:
            depth_best = min(depth_best, 1.0)
    elif min(depth_pre, depth_post) >= max(depth_best - 0.01, 0.8) and \
            group_type in ['Media', 'Armoire', 'Cabinet', 'Appliance', 'Toilet'] and edge_idx in [0, 2]:
        pass
    elif depth_best + 0.01 >= min(depth_pre, depth_post) >= min(depth_best * 0.8, 1.0) and \
            group_type in ['Media', 'Work', 'Rest',  'Bath', 'Toilet']:
        depth_best = min(depth_pre, depth_post)
    elif depth_best + 0.01 >= max(depth_pre, depth_post) >= min(depth_best * 0.8, 1.0) and \
            group_type in ['Media', 'Work', 'Rest', 'Bath', 'Toilet']:
        depth_best = max(depth_pre, depth_post)
    elif min(depth_pre, depth_post) >= depth_best - 0.01 and abs(min(depth_pre, depth_post) - UNIT_DEPTH_ASIDE * 1) > 0.01:
        if min(depth_pre, depth_post) >= max(depth_best - 0.01, 0.8) and \
                group_type in ['Media', 'Armoire', 'Cabinet', 'Appliance', 'Toilet'] and edge_idx in [0, 2]:
            pass
        elif min(depth_pre, depth_post) >= max(depth_best - 0.01, 0.8) and \
                group_type in ['Bath', 'Toilet'] and edge_idx in [1, 3]:
            pass
        elif min(depth_pre, depth_post) - MID_GROUP_PASS > depth_best and \
                group_type in ['Media', 'Armoire', 'Cabinet', 'Appliance', 'Toilet'] and edge_idx in [0, 2]:
            depth_best = min(depth_pre, depth_post) - MID_GROUP_PASS
        else:
            depth_best = min(depth_pre, depth_post)
    elif depth_best < max(depth_pre, depth_post) <= min(depth_pre_more, depth_post_more) + 0.01:
        if max(depth_pre, depth_post) >= max(depth_best - 0.01, 0.8) and \
                group_type in ['Media', 'Armoire', 'Cabinet', 'Appliance', 'Toilet'] and edge_idx in [0, 2]:
            pass
        elif max(depth_pre, depth_post) >= max(depth_best - 0.01, 0.8) and \
                group_type in ['Bath', 'Toilet'] and edge_idx in [1, 3]:
            pass
        else:
            depth_best = max(depth_pre, depth_post)
    elif depth_best < max(depth_pre, depth_post) <= max(depth_pre_more, depth_post_more) + 0.01 and edge_idx in [1, 3]:
        if max(depth_pre, depth_post) > min(depth_pre_more, depth_post_more) > min(depth_best, 2.0):
            depth_best = min(depth_pre_more, depth_post_more)
        elif max(depth_pre, depth_post) < min(depth_best * 2, 2.0):
            depth_best = max(depth_pre, depth_post)
        elif max(depth_pre, depth_post) < min(depth_best * 2, 5.0) and group_type in ['Meeting']:
            depth_best = max(depth_pre, depth_post)
    elif min(depth_pre_more, depth_post_more) > depth_best - 0.01 and \
            abs(min(depth_pre_more, depth_post_more) - UNIT_DEPTH_ASIDE * 1) > 0.01:
        if min(depth_pre_more, depth_post_more) < min(depth_best * 2, 2.0):
            depth_best = min(depth_pre_more, depth_post_more)
    elif max(depth_pre_more, depth_post_more) > depth_best - 0.01 and group_type in ['Dining', 'Work', 'Rest']:
        if max(depth_pre_more, depth_post_more) < min(depth_best * 2, 2.0):
            depth_best = max(depth_pre_more, depth_post_more)
    # 范围
    depth_back = rely_back
    if abs(rely_back) < 0.1:
        depth_back = rely_back
    elif abs(rely_back - UNIT_DEPTH_CURTAIN) < 0.001:
        depth_back = 0
    elif 0 < rely_back < UNIT_DEPTH_CURTAIN + 0.001:
        rely_back = UNIT_DEPTH_CURTAIN
        depth_back = 0
    elif rely_back > UNIT_DEPTH_CURTAIN + 0.001 and 'center' in group_one and group_one['center'] >= 1:
        depth_back = 0
        if rely_back > UNIT_DEPTH_ASIDE:
            depth_back = UNIT_DEPTH_ASIDE
        if line_one['type'] in [UNIT_TYPE_DOOR] and line_one['width'] < group_width:
            depth_back = 0
    elif line_one['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW] and line_one['width'] > UNIT_WIDTH_HOLE:
        depth_back = max(rely_back - UNIT_DEPTH_CURTAIN, 0)
    elif line_one['type'] in [UNIT_TYPE_GROUP] and line_one['height'] > UNIT_HEIGHT_WALL - 0.01:
        depth_back = max(rely_back - UNIT_DEPTH_CURTAIN, 0)
    if group_type in ['Armoire', 'Cabinet'] and depth_max > 5:
        depth_max *= 0.5
    if edge_idx == 0:
        #
        neighbor_best[0] = depth_back
        neighbor_best[2] = depth_best - group_depth - rely_back
        neighbor_best[1] = width_post
        neighbor_best[3] = width_pre
        #
        neighbor_zone[0] = depth_back
        neighbor_zone[2] = depth_max - group_depth - rely_back
        neighbor_zone[1] = width_post_more
        neighbor_zone[3] = width_pre_more
    elif edge_idx == 1:
        #
        neighbor_best[0] = width_pre
        neighbor_best[2] = width_post
        neighbor_best[1] = depth_back
        neighbor_best[3] = depth_best - group_width - rely_back
        #
        neighbor_zone[0] = width_pre_more
        neighbor_zone[2] = width_post_more
        neighbor_zone[1] = depth_back
        neighbor_zone[3] = depth_max - group_width - rely_back
    elif edge_idx == 2:
        #
        neighbor_best[0] = depth_best - group_depth - rely_back
        neighbor_best[2] = depth_back
        neighbor_best[1] = width_pre
        neighbor_best[3] = width_post
        #
        neighbor_zone[0] = depth_max - group_depth - rely_back
        neighbor_zone[2] = depth_back
        neighbor_zone[1] = width_pre_more
        neighbor_zone[3] = width_post_more
    elif edge_idx == 3:
        #
        neighbor_best[0] = width_post
        neighbor_best[2] = width_pre
        neighbor_best[1] = depth_best - group_width - rely_back
        neighbor_best[3] = depth_back
        #
        neighbor_zone[0] = width_post_more
        neighbor_zone[2] = width_pre_more
        neighbor_zone[1] = depth_best - group_width - rely_back
        neighbor_zone[3] = depth_back
    if group_type in ['Meeting', 'Bed']:
        if 'neighbor_base' in group_one and neighbor_best[2] < 0.01:
            neighbor_base = group_one['neighbor_base']
            neighbor_best[2] = max(neighbor_best[2], neighbor_base[2] * 0.5)
        if 'neighbor_more' in group_one and neighbor_best[2] > 0.01:
            neighbor_more = group_one['neighbor_more']
            neighbor_best[2] = min(neighbor_best[2], neighbor_more[2] * 1.0)
    if group_type in ['Dining']:
        if 'neighbor_base' in group_one and neighbor_best[2] < 0.01:
            neighbor_base = group_one['neighbor_base']
            neighbor_best[2] = max(neighbor_best[2], neighbor_base[2] * 0.5)
        if 'neighbor_more' in group_one and neighbor_best[2] > 0.01:
            neighbor_more = group_one['neighbor_more']
            neighbor_best[2] = min(neighbor_best[2], neighbor_more[2] * 1.0)
    group_one['neighbor_best'] = neighbor_best
    group_one['neighbor_zone'] = neighbor_zone
