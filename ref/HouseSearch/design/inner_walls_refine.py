"""
    为house_data 更新内墙信息
    默认为0.12 的内墙宽度(包括断头墙)
"""
import copy
import math

import numpy as np

from HouseSearch.util import update_unit_pts, check_on_line, fix_line_intersection, is_coincident_line,\
    compute_poly_area, get_single_wall_fix_line_intersection


# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use("TkAgg")


def update_inner_wall_offset(room_info, offset=0.06):
    floor_pts = []
    origin_room_floor = room_info['floor']
    for pts_idx in range(len(origin_room_floor) // 2):
        floor_pts.append([origin_room_floor[2 * pts_idx], origin_room_floor[2 * pts_idx + 1]])

    new_floor_pts = copy.deepcopy(floor_pts[:-1])
    old_floor_pts = copy.deepcopy(floor_pts[:-1])
    # 遍历每条边，更新上面的门窗墙
    new_door_info_list = copy.deepcopy(room_info['door_info'])
    new_window_info_list = copy.deepcopy(room_info['window_info'])
    new_hole_info_list = copy.deepcopy(room_info['hole_info'])

    offset_list = None
    for start_idx in range(0, len(old_floor_pts)):
        a_pt = old_floor_pts[start_idx]
        b_pt = old_floor_pts[(start_idx + 1) % len(old_floor_pts)]

        start_p = old_floor_pts[start_idx]
        end_p = old_floor_pts[(start_idx + 1) % len(old_floor_pts)]

        line_norm = [start_p[1] - end_p[1], end_p[0] - start_p[0]]
        norm = math.sqrt(line_norm[0] ** 2 + line_norm[1] ** 2)
        if norm > 0.01:
            offset_list = [line_norm[0] / norm * offset, line_norm[1] / norm * offset]

        new_pt_a = [old_floor_pts[start_idx][0] + offset_list[0],
                    old_floor_pts[start_idx][1] + offset_list[1]]

        new_pt_b = [old_floor_pts[(start_idx + 1) % len(old_floor_pts)][0] + offset_list[0],
                    old_floor_pts[(start_idx + 1) % len(old_floor_pts)][1] + offset_list[1]]

        if 'material_info' in room_info and 'wall' in room_info['material_info']:
            for wall in room_info['material_info']['wall']:
                if 'wall' in wall and 'offset' not in wall:
                    wall_line = wall['wall']
                    flag, remained, removed = is_coincident_line(wall_line, [a_pt, b_pt])
                    if flag:
                        wall['wall'] = (np.array(wall_line) + offset_list).tolist()
                        wall['offset'] = True

            fix_line_intersection([new_pt_a, new_pt_b], new_floor_pts, start_idx)

        for unit_idx, unit_info in enumerate(room_info['door_info']):
            near_pts = unit_info['main_pts']
            if check_on_line(near_pts[0], [a_pt, b_pt]) and check_on_line(near_pts[0], [a_pt, b_pt]):
                update_unit_pts(new_door_info_list[unit_idx]['pts'], near_pts, offset_list)

        for unit_idx, unit_info in enumerate(room_info['window_info']):
            near_pts = unit_info['main_pts']
            if check_on_line(near_pts[0], [a_pt, b_pt]) and check_on_line(near_pts[0], [a_pt, b_pt]):
                update_unit_pts(new_window_info_list[unit_idx]['pts'], near_pts, offset_list)

        for unit_idx, unit_info in enumerate(room_info['hole_info']):
            near_pts = unit_info['main_pts']
            if check_on_line(near_pts[0], [a_pt, b_pt]) and check_on_line(near_pts[0], [a_pt, b_pt]):
                update_unit_pts(new_hole_info_list[unit_idx]['pts'], near_pts, offset_list)

    # 更新断墙
    if "add_single_walls" in room_info and len(room_info['add_single_walls']) > 0:
        add_wall_info = []
        for single_node_wall_list in room_info['add_single_walls']:
            start_idx = single_node_wall_list[0]["start_wall_idx"]
            start_type = single_node_wall_list[0]["start_wall_type"]
            start_p = new_floor_pts[start_idx]
            end_p = new_floor_pts[(start_idx + 1) % len(new_floor_pts)]

            base_line = [end_p[0] - start_p[0], end_p[1] - start_p[1]]
            norm = math.sqrt(base_line[0] ** 2 + base_line[1] ** 2)
            if norm < 0.01:
                continue

            base_line = [base_line[0] / norm, base_line[1] / norm]

            # 提取点集
            single_wall_floor_pts = []
            for wall in single_node_wall_list:
                wall_from = wall["from"]
                wall_to = wall["to"]

                if len(single_wall_floor_pts) == 0:
                    single_wall_floor_pts.append(wall_from)
                    single_wall_floor_pts.append(wall_to)
                else:
                    single_wall_floor_pts.append(wall_to)

            forward_floor_list = [[i[0], i[1]] for i in single_wall_floor_pts]
            backward_floor_list = [[i[0], i[1]] for i in single_wall_floor_pts]

            for w_idx in range(len(single_wall_floor_pts) - 1):
                wall_from = single_wall_floor_pts[w_idx]
                wall_to = single_wall_floor_pts[w_idx + 1]

                temp_line = [wall_to[0] - wall_from[0], wall_to[1] - wall_from[1]]
                norm = math.sqrt(temp_line[0] ** 2 + temp_line[1] ** 2)
                if norm < 0.01:
                    break

                temp_line = [temp_line[0] / norm, temp_line[1] / norm]

                temp_line_normal = [-temp_line[1], temp_line[0]]

                offset_list = [temp_line_normal[0] * offset, temp_line_normal[1] * offset]

                new_back_pt_a = [single_wall_floor_pts[w_idx][0] + offset_list[0],
                                 single_wall_floor_pts[w_idx][1] + offset_list[1]]

                new_back_pt_b = [single_wall_floor_pts[(w_idx + 1) % len(old_floor_pts)][0] + offset_list[0],
                                 single_wall_floor_pts[(w_idx + 1) % len(old_floor_pts)][1] + offset_list[1]]

                fix_line_intersection([new_back_pt_a, new_back_pt_b], backward_floor_list, w_idx, circle=False)

                new_forward_pt_a = [single_wall_floor_pts[w_idx][0] - offset_list[0],
                                    single_wall_floor_pts[w_idx][1] - offset_list[1]]

                new_forward_pt_b = [single_wall_floor_pts[(w_idx + 1) % len(old_floor_pts)][0] - offset_list[0],
                                    single_wall_floor_pts[(w_idx + 1) % len(old_floor_pts)][1] - offset_list[1]]

                fix_line_intersection([new_forward_pt_a, new_forward_pt_b], forward_floor_list, w_idx, circle=False)

                if w_idx == 0:
                    backward_floor_list[w_idx][0] += offset_list[0]
                    backward_floor_list[w_idx][1] += offset_list[1]
                    forward_floor_list[w_idx][0] -= offset_list[0]
                    forward_floor_list[w_idx][1] -= offset_list[1]

            if start_type == "line":
                forward_start_pt_fixed = get_single_wall_fix_line_intersection([forward_floor_list[0], forward_floor_list[1]], new_floor_pts, start_idx, start_idx+1)
            else:
                forward_start_pt_fixed = get_single_wall_fix_line_intersection([forward_floor_list[0], forward_floor_list[1]], new_floor_pts, start_idx, start_idx-1)

            backward_start_pt_fixed = get_single_wall_fix_line_intersection([backward_floor_list[0], backward_floor_list[1]], new_floor_pts, start_idx, start_idx+1)

            # 修正交点
            if forward_start_pt_fixed:
                forward_floor_list[0] = forward_start_pt_fixed
            if backward_start_pt_fixed:
                backward_floor_list[0] = backward_start_pt_fixed

            backward_floor_list.reverse()
            add_wall_info.append((start_idx, forward_floor_list + backward_floor_list, start_type))

        add_wall_info = sorted(add_wall_info, key=lambda x: x[0], reverse=True)
        for item_data in add_wall_info:
            start_idx, l, start_type = item_data
            if start_type == "pt":
                new_floor_pts[start_idx: start_idx + 1] = l
            else:
                new_floor_pts[start_idx: start_idx + 1] = [new_floor_pts[start_idx]] + l

    room_info['floor'] = []
    for pts in new_floor_pts:
        room_info['floor'] += pts
    room_info['floor'] += [new_floor_pts[0][0], new_floor_pts[0][1]]
    room_info['door_info'] = new_door_info_list
    room_info['window_info'] = new_window_info_list
    room_info['hole_info'] = new_hole_info_list

    return room_info


def room_inner_walls_refine(house_data):
    for room_idx in range(len(house_data['room'])):
        house_data['room'][room_idx] = update_inner_wall_offset(house_data['room'][room_idx], offset=0.06)

    # 更新面积
    # 计算面积
    for room_idx in range(len(house_data['room']) - 1, -1, -1):
        house_data['room'][room_idx]['area'] = compute_poly_area(house_data['room'][room_idx]['floor'])
        if house_data['room'][room_idx]['area'] < 0.1:
            house_data['room'].pop(room_idx)

    return house_data
