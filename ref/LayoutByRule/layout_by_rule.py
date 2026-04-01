# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-08-13
@Description: 规则化布局算法

"""

from LayoutByRule.house_interior_layout import *
from LayoutByRule.house_interior_scope import *
from LayoutByRule.house_interior_refine import *
from LayoutByRule.house_interior_view import *

# 临时数据目录
DATA_DIR_RULE = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(DATA_DIR_RULE):
    os.makedirs(DATA_DIR_RULE)


def layout_by_rule(data_info, layout_info, sample_id=''):
    region_info = house_rect_layout(data_info, layout_info, sample_id)
    propose_info = house_rect_scope(data_info, layout_info)
    return region_info, propose_info


def layout_by_rule_house_refer(data_info, layout_info, sample_id=''):
    region_info = house_rect_layout(data_info, layout_info, sample_id)
    group_type_main = GROUP_TYPE_MAIN[:]
    group_type_main.append('Work')
    for room_key, room_val in layout_info.items():
        if 'layout_scheme' in room_val:
            for scheme_one in room_val['layout_scheme']:
                if 'group' not in scheme_one:
                    continue
                room_type = ''
                if 'type' in scheme_one:
                    room_type = scheme_one['type']
                # 扩张处理
                group_list, group_todo, decor_todo = scheme_one['group'], [], []
                for group_one in group_list:
                    group_type, neighbor_fix = group_one['type'], False
                    if group_type in GROUP_RULE_FUNCTIONAL:
                        if group_type in ['Meeting', 'Media', 'Bed', 'Dining',
                                          'Armoire', 'Cabinet',
                                          'Work', 'Rest', 'Bath', 'Toilet']:
                            neighbor_fix = True
                        resolve_group_regulation(group_one, neighbor_fix)
                        group_todo.append(group_one)
                    elif group_type in ['Window']:
                        object_list = group_one['obj_list']
                        for object_one in object_list:
                            object_type = object_one['type']
                            if 'curtain' in object_type:
                                decor_todo.append(object_one)
                # 避让处理
                group_dump = resolve_group_impaction(group_todo, decor_todo, room_type)
                for group_one in group_dump:
                    if group_one in group_list:
                        group_list.remove(group_one)
    propose_info = {}
    return region_info, propose_info, group_type_main


def layout_by_rule_room(data_info, layout_info, sample_id=''):
    region_info = room_rect_layout(data_info, layout_info, sample_id)
    propose_info = room_rect_scope(data_info, layout_info)
    return region_info, propose_info


def layout_by_rule_room_refer(data_info, layout_info, sample_id=''):
    region_info = room_rect_layout(data_info, layout_info, sample_id)
    if 'layout_scheme' in layout_info:
        for scheme_one in layout_info['layout_scheme']:
            if 'group' not in scheme_one:
                continue
            group_list, group_todo, decor_todo = scheme_one['group'], [], []
            for group_one in group_list:
                group_type, neighbor_fix = group_one['type'], False
                if group_type in GROUP_RULE_FUNCTIONAL:
                    if group_type in ['Meeting', 'Media', 'Bed', 'Dining',
                                      'Armoire', 'Cabinet',
                                      'Work', 'Rest', 'Bath', 'Toilet']:
                        neighbor_fix = True
                    resolve_group_regulation(group_one, neighbor_fix)
                    group_todo.append(group_one)
                elif group_type in ['Window']:
                    object_list = group_one['obj_list']
                    for object_one in object_list:
                        object_type = object_one['type']
                        if 'curtain' in object_type:
                            decor_todo.append(object_one)
            group_dump = resolve_group_impaction(group_todo, decor_todo)
            for group_one in group_dump:
                if group_one in group_list:
                    group_list.remove(group_one)
    propose_info = []
    return region_info, propose_info


def layout_by_rule_group(data_info, layout_info, sample_id=''):
    region_info = room_rect_layout(data_info, layout_info, sample_id)
    if 'layout_scheme' in layout_info:
        for layout_one in layout_info['layout_scheme']:
            if 'group' not in layout_one:
                continue
            for group_one in layout_one['group']:
                if group_one['type'] in GROUP_TYPE_MAIN:
                    group_one['regulation'] = [0, 0, 0, 0]
    propose_info = {}
    return region_info, propose_info


def replace_by_rule(data_info, layout_info):
    region_info = house_rect_replace(data_info, layout_info)
    propose_info = house_rect_scope(data_info, layout_info)
    return region_info, propose_info


def replace_by_rule_room(data_info, layout_info):
    region_info = room_rect_replace(data_info, layout_info)
    propose_info = room_rect_scope(data_info, layout_info)
    return region_info, propose_info


# 功能测试
if __name__ == '__main__':
    # 导入
    from House.house import *
    from House.house_sample import *

    # 单批
    house_id = '355ab8b3-1609-4346-8202-1546938d57f2'
    data_info, layout_info, group_dict = extract_house_layout(house_id)
    layout_by_rule(data_info, layout_info)
