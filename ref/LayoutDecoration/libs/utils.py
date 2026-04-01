import math
import numpy as np
from LayoutDecoration.Base.math_util import xyz_to_ang, ang_to_ang, rot_to_ang
from LayoutDecoration.Base.math_util import is_coincident_line, compute_furniture_rely_soft, compute_room_line, compute_furniture_rect
from Furniture.furniture_group import GROUP_RULE_FUNCTIONAL


def correct_room_move(room_layout, object_one):
    # 物品信息
    plat_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    plat_pos, plat_rot, plat_ang = object_one['position'], object_one['rotation'], rot_to_ang(object_one['rotation'])
    plat_fix_y = 0.05
    # 避让信息
    plat_mov_x = 0
    plat_mov_z = min(plat_size[0], plat_size[2], 0.5)
    plat_add_x = plat_mov_z * math.sin(plat_ang) + plat_mov_x * math.cos(plat_ang)
    plat_add_z = plat_mov_z * math.cos(plat_ang) - plat_mov_x * math.sin(plat_ang)
    # 分组信息
    if 'layout_scheme' in room_layout:
        scheme_list = room_layout['layout_scheme']
    else:
        scheme_list = [{'group': room_layout}]

    for scheme_idx, scheme_one in enumerate(scheme_list):
        group_list, group_todo, object_todo = [], [], []
        if 'group' in scheme_one:
            group_list = scheme_one['group']
        # 避让检测
        for group_idx, group_one in enumerate(group_list):
            group_type = group_one['type']
            # 组合检测
            if group_type in GROUP_RULE_FUNCTIONAL:
                group_rect = compute_furniture_rect(group_one['size'], group_one['position'], group_one['rotation'])
                group_rect = np.reshape(group_rect, [-1]).tolist()
                point_0 = [(group_rect[0] + group_rect[2]) / 2, 0, (group_rect[1] + group_rect[3]) / 2]
                point_1 = [group_rect[0], 0, group_rect[1]]
                point_2 = [group_rect[2], 0, group_rect[3]]
                for obj_pos in [point_0, point_1, point_2]:
                    plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
                    plat_on = False
                    # 垂直距离
                    if abs(plat_dis[1]) >= plat_size[1] + plat_fix_y:
                        plat_on = False
                        continue
                    # 水平距离
                    ang = 0 - rot_to_ang(plat_rot)
                    dis_x = plat_dis[2] * math.sin(ang) + plat_dis[0] * math.cos(ang)
                    dis_z = plat_dis[2] * math.cos(ang) - plat_dis[0] * math.sin(ang)
                    if abs(dis_z) >= plat_size[2] / 2 + 0.02:
                        plat_on = False
                        continue
                    if abs(dis_x) >= plat_size[0] / 2 - 0.05:
                        if abs(dis_x) <= plat_size[0] / 2 + 0.05:
                            wait_on = True
                            break
                        plat_on = False
                        continue
                    # 符合要求
                    plat_on = True
                    group_todo.append(group_one)
                    break
            # 物品检测
            elif group_type in ['Wall', 'Floor']:
                obj_set = []
                if 'obj_list' in group_one:
                    obj_set = group_one['obj_list']
                for obj_idx, obj_one in enumerate(obj_set):
                    obj_pos = obj_one['position']
                    plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
                    plat_on = False
                    # 垂直距离
                    if abs(plat_dis[1]) >= plat_size[1] + plat_fix_y:
                        plat_on = False
                        continue
                    # 水平距离
                    ang = 0 - rot_to_ang(plat_rot)
                    dis_x = plat_dis[2] * math.sin(ang) + plat_dis[0] * math.cos(ang)
                    dis_z = plat_dis[2] * math.cos(ang) - plat_dis[0] * math.sin(ang)
                    if abs(dis_z) >= plat_size[2] / 2 + 0.02:
                        plat_on = False
                        continue
                    if abs(dis_x) >= plat_size[0] / 2 - 0.05:
                        if abs(dis_x) <= plat_size[0] / 2 + 0.05:
                            wait_on = True
                            break
                        plat_on = False
                        continue
                    # 符合要求
                    plat_on = True
                    object_todo.append(obj_one)
        # 避让处理
        for group_idx, group_one in enumerate(group_todo):
            # 组合避让
            group_pos = group_one['position']
            group_pos[0] += plat_add_x
            group_pos[2] += plat_add_z
            # 物品避让
            object_list = group_one['obj_list']
            for object_idx, obj in enumerate(object_list):
                object_pos = obj['position']
                object_pos[0] += plat_add_x
                object_pos[2] += plat_add_z
                obj['correct_move'] = True
        for object_idx, obj in enumerate(object_todo):
            object_pos = obj['position']
            object_pos[0] += plat_add_x
            object_pos[2] += plat_add_z
            obj['correct_move'] = True


def correct_house_move(house_layout, object_one, room_id=''):
    room_layout = {}
    if len(room_id) > 0:
        for room_key, room_val in house_layout.items():
            if room_id == room_key:
                room_layout = room_val
                break
    if len(room_layout) <= 0:
        for room_key, room_val in house_layout.items():
            if 'floor' not in room_val:
                continue
            line_ori = compute_room_line(room_val)
            line_idx, edge_idx = compute_furniture_rely_soft(object_one, line_ori)
            if 0 <= line_idx < len(line_ori) and 0 <= edge_idx < 4:
                room_layout = room_val
                break
    if len(room_layout) > 0:
        correct_room_move(room_layout, object_one)

