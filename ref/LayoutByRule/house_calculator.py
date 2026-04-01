# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-08-20
@Description: 全屋矩形布局计算

"""

import os
from LayoutByRule.house_analysis import *


# 临时数据目录
RECT_DIR_TEMP = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(RECT_DIR_TEMP):
    os.makedirs(RECT_DIR_TEMP)


MIN_GROUP_PASS = 0.2
MID_GROUP_PASS = 0.8
MAX_GROUP_PASS = 3.0


# 计算两点距离角度
def compute_dis_ang(x1, y1, x2, y2):
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


# 计算墙体承载区域
def compute_suit_ratio(line_list, line_idx, group_width, group_depth, line_ratio=[0, 1],
                       merge_type=[], max_pass=-1, min_pass=-1, mid_pass=0, line_used={}):
    line_one = line_list[line_idx]
    line_width = line_one['width']
    suit_width, suit_depth, suit_depth_min = line_width, UNIT_DEPTH_GROUP_MAX * 2, UNIT_DEPTH_GROUP_MAX * 2
    suit_ratio = line_ratio[:]
    suit_ratio_best = [(suit_ratio[1] + suit_ratio[0]) / 2, (suit_ratio[1] + suit_ratio[0]) / 2]
    suit_depth_best = 0
    group_depth_max = min(group_depth + 1.5, group_depth * 1.5)
    # 本身区域
    if min_pass <= -1:
        min_pass = MIN_GROUP_PASS
    if max_pass <= -1:
        max_pass = MAX_GROUP_PASS
    ratio_0, ratio_1 = line_ratio[0], line_ratio[1]
    depth_all = []
    if 'depth_all' in line_one and len(line_one['depth_all']) > 0:
        depth_all = line_one['depth_all']
    if len(depth_all) > 0:
        width_best, width_last, depth_last = 0, 0, 0
        for depth_one in depth_all:
            # 起止比例
            ratio_pre, ratio_post = depth_one[0], depth_one[1]
            if ratio_pre >= ratio_1:
                continue
            if ratio_post <= ratio_0:
                continue
            if ratio_pre < ratio_0:
                ratio_pre = ratio_0
            if ratio_post > ratio_1:
                ratio_post = ratio_1
            # 深度判断
            width_now = line_width * (ratio_post - ratio_pre)
            depth_now = depth_one[2]
            if depth_now < group_depth + min_pass:
                if ratio_pre <= ratio_0:
                    ratio_0 = ratio_post
                if ratio_post >= ratio_1:
                    ratio_1 = ratio_pre
                if ratio_pre > ratio_0 and ratio_post < ratio_1:
                    if ratio_pre - ratio_0 >= ratio_1 - ratio_post:
                        ratio_1 = ratio_pre
                        break
                    else:
                        ratio_0 = ratio_post
                        continue
            elif depth_now < group_depth + max_pass:
                if depth_now > group_depth + mid_pass:
                    if width_now > width_best or depth_last == 0:
                        if depth_now <= suit_depth_best and width_now < width_best + 0.5 and \
                                len(suit_ratio_best) >= 2 and ratio_pre >= suit_ratio_best[1] - 0.1:
                            suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                            suit_depth_best = depth_now
                        else:
                            if depth_now > group_depth_max and suit_depth_best > group_depth_max and \
                                    ratio_pre <= suit_ratio_best[1] + 0.01:
                                if depth_now < suit_depth_best - 1 and width_now > width_best * 2:
                                    suit_ratio_best = [ratio_pre, ratio_post]
                                    suit_depth_best = depth_now
                                elif depth_now > suit_depth_best + 2 and width_now > width_best * 2:
                                    suit_ratio_best = [ratio_pre, ratio_post]
                                    suit_depth_best = depth_now
                                else:
                                    suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                                    suit_depth_best = min(suit_depth_best, depth_now)
                            elif suit_depth_best - 0.4 < depth_now < suit_depth_best:
                                suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                                suit_depth_best = depth_now
                            else:
                                suit_ratio_best = [ratio_pre, ratio_post]
                                suit_depth_best = depth_now
                        suit_depth = min(depth_now, suit_depth)
                        width_best = max(width_now, line_width * (suit_ratio_best[1] - suit_ratio_best[0]))
                        width_last = width_now
                        depth_last = depth_now
                    elif depth_now > suit_depth_best:
                        if abs(depth_now - UNIT_DEPTH_ASIDE - suit_depth_best) < 0.01:
                            suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                            suit_depth_best = depth_now
                        elif depth_now < suit_depth_best + UNIT_DEPTH_ASIDE * 0.5:
                            if width_now > width_best * 2:
                                suit_ratio_best = [ratio_pre, ratio_post]
                                suit_depth_best = depth_now
                            elif len(suit_ratio_best) >= 2 and ratio_pre >= suit_ratio_best[1] - 0.1 and width_now < width_last:
                                suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                                suit_depth_best = min(suit_depth_best, depth_now)
                                suit_depth = min(suit_depth, depth_now)
                        elif depth_now > group_depth_max + 2 and suit_depth_best > group_depth_max:
                            suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                            suit_depth_best = depth_now
                    elif group_depth_max < depth_now < suit_depth_best and suit_depth_best > group_depth * 1.5:
                        if abs(depth_now + UNIT_DEPTH_ASIDE - suit_depth_best) < 0.01:
                            suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                            suit_depth_best = depth_now
                        elif depth_now > suit_depth_best - UNIT_DEPTH_ASIDE * 0.5:
                            suit_ratio_post = suit_ratio_best[1]
                            suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                            suit_depth_best = depth_now
                            if suit_ratio_post > 0.6 and suit_ratio_best[1] > 0.8:
                                break
                        elif width_now > width_best * 2:
                            suit_ratio_best = [ratio_pre, ratio_post]
                            suit_depth_best = depth_now
                        width_last = width_now
                        depth_last = depth_now
                    elif depth_now < suit_depth:
                        suit_depth = depth_now
                elif depth_now < suit_depth:
                    suit_depth = depth_now
                    if suit_depth_best <= 0.1 < suit_depth:
                        suit_ratio_best = [ratio_pre, ratio_post]
                        suit_depth_best = depth_now
                    width_last = width_now
                    depth_last = depth_now
                if depth_now < suit_depth_min:
                    suit_depth_min = depth_now
            else:
                if depth_last == 0 and width_now > width_best:
                    width_best = width_now
                    suit_ratio_best = [ratio_pre, ratio_post]
                    suit_depth_best = depth_now
        suit_width = line_width * (ratio_1 - ratio_0)
    suit_ratio = [ratio_0, ratio_1]
    if abs(suit_ratio_best[1] - suit_ratio_best[0]) < 0.001:
        suit_ratio_best = [(ratio_0 + ratio_1) / 2, (ratio_0 + ratio_1) / 2]
    # 返回信息
    if len(merge_type) <= 0:
        if suit_width < 0:
            suit_depth, suit_depth_min = min(group_depth, suit_depth), min(group_depth, suit_depth_min)
        return suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best
    suit_width_old = suit_width
    ratio_best_pre = suit_ratio_best[0]
    ratio_best_post = suit_ratio_best[1]

    # 当前信息
    type_cur, width_cure = line_one['type'], line_one['width']

    # 前段融合
    score_pre = line_one['score_pre']
    index_pre = (line_idx - 1 + len(line_list)) % len(line_list)
    line_pre = line_list[index_pre]
    type_pre, width_pre, depth_pre, count_pre = line_pre['type'], line_pre['width'], line_pre['depth'], 0
    merge_flag = 0
    while score_pre <= 2 and type_pre in merge_type and ratio_0 == 0:
        ratio_best_new = 1
        # 阳角判断
        if merge_flag == 0:
            merge_flag = 1
        if score_pre == 2 and line_width > MIN_GROUP_PASS * 2:
            if line_pre['width'] < 0.01:
                index_temp = (index_pre - 1 + len(line_list)) % len(line_list)
                if index_temp in line_used:
                    break
                # 阳角融合
                score_pre = line_pre['score_pre']
                index_pre = (index_pre - 1 + len(line_list)) % len(line_list)
                line_pre = line_list[index_pre]
                type_pre = line_pre['type']
                width_pre = line_pre['width']
                if score_pre == 4:
                    score_pre = 1
                    merge_flag = 2
                    continue
                else:
                    break
            else:
                break
        if score_pre == 1 and index_pre in line_used and type_cur not in [UNIT_TYPE_WALL]:
            break
        count_pre += 1
        depth_ext = line_pre['depth_ext']
        if line_one['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
            depth_ext = line_pre['depth_all']
        if len(depth_ext) > 0:
            for depth_one in depth_ext[::-1]:
                if type_pre in [UNIT_TYPE_DOOR] and width_pre > UNIT_WIDTH_DOOR:
                    ratio_0 = 0
                    ratio_best_new = 0
                    index_pre2 = (index_pre - 1 + len(line_list)) % len(line_list)
                    line_pre2 = line_list[index_pre2]
                    if line_pre['score_post'] == 1 and line_pre2['type'] in [UNIT_TYPE_WALL]:
                        ratio_0 = 0 - line_pre2['width'] / width_pre
                    break
                if depth_one[2] < group_depth:
                    ratio_0 = depth_one[1]
                    break
                if abs(depth_one[2] - suit_depth) < 0.01 and abs(1 - depth_one[1]) < 0.01:
                    ratio_best_new = depth_one[0]
        else:
            ratio_0 = 1
        if 1 - ratio_0 >= 0.01:
            # 更新适应比例
            width_add = width_pre * (1 - ratio_0)
            if width_add >= suit_width_old and merge_flag == 1 and \
                    type_pre not in [UNIT_TYPE_DOOR] and type_cur not in [UNIT_TYPE_DOOR]:
                if width_add > group_width:
                    return suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best
            suit_width += width_add
            suit_ratio[0] -= width_add / line_width
            # 更新最佳比例
            if abs(ratio_best_pre - 0) <= 0.01:
                ratio_best_pre = ratio_best_new
                width_best_add = width_pre * (1 - ratio_best_new)
                suit_ratio_best[0] -= width_best_add / line_width
            # 更新前段信息
            if not line_pre['type'] == type_pre:
                break
            score_pre = line_pre['score_pre']
            index_pre = (index_pre - 1 + len(line_list)) % len(line_list)
            line_pre = line_list[index_pre]
            type_pre = line_pre['type']
            width_pre = line_pre['width']
        else:
            break
        merge_flag = 0
    # 后段融合
    score_post = line_one['score_post']
    index_post = (line_idx + 1 + len(line_list)) % len(line_list)
    line_post = line_list[index_post]
    type_post, width_post, depth_post, count_post = line_post['type'], line_post['width'], line_post['depth'], 0
    merge_flag = 0
    while score_post <= 2 and type_post in merge_type and ratio_1 == 1:
        ratio_best_new = 0
        # 阳角判断
        if merge_flag == 0:
            merge_flag = 1
        if score_post == 2 and line_width > MIN_GROUP_PASS * 2:
            if line_post['width'] < 0.01:
                index_temp = (index_post + 1 + len(line_list)) % len(line_list)
                if index_temp in line_used:
                    break
                # 阳角融合
                score_post = line_post['score_post']
                index_post = (index_post + 1 + len(line_list)) % len(line_list)
                line_post = line_list[index_post]
                type_post = line_post['type']
                width_post = line_post['width']
                if score_post == 4:
                    score_post = 1
                    merge_flag = 2
                    continue
                else:
                    break
            else:
                break
        if score_post == 1 and index_post in line_used and type_cur not in [UNIT_TYPE_WALL]:
            break
        count_post += 1
        depth_ext = line_post['depth_ext']
        if line_one['type'] in [UNIT_TYPE_DOOR, UNIT_TYPE_WINDOW]:
            depth_ext = line_post['depth_all']
        if len(depth_ext) > 0:
            for depth_one in depth_ext:
                if type_post in [UNIT_TYPE_DOOR] and width_post > UNIT_WIDTH_DOOR:
                    ratio_1 = 1
                    ratio_best_new = 1
                    index_post2 = (index_post + 1 + len(line_list)) % len(line_list)
                    line_post2 = line_list[index_post2]
                    if line_post['score_post'] == 1 and line_post2['type'] in [UNIT_TYPE_WALL]:
                        ratio_1 = 1 + line_post2['width'] / width_post
                    break
                if depth_one[2] < group_depth:
                    ratio_1 = depth_one[0]
                    break
                if abs(depth_one[2] - suit_depth) < 0.01 and abs(depth_one[0] - 0) < 0.01:
                    ratio_best_new = depth_one[1]
        else:
            ratio_1 = 0
        if ratio_1 - 0 >= 0.01:
            # 更新适应比例
            width_add = width_post * (ratio_1 - 0)
            if width_add > suit_width_old and merge_flag == 1 and \
                    type_post not in [UNIT_TYPE_DOOR] and type_cur not in [UNIT_TYPE_DOOR]:
                if width_add > group_width:
                    return suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best
            suit_width += width_add
            suit_ratio[1] += width_add / line_width
            # 更新最佳比例
            if abs(1 - ratio_best_post) <= 0.01:
                ratio_best_post = ratio_best_new
                width_best_add = width_post * (ratio_best_new - 0)
                suit_ratio_best[1] += width_best_add / line_width
            # 更新后段信息
            if not line_post['type'] == type_post:
                break
            score_post = line_post['score_post']
            index_post = (index_post + 1 + len(line_list)) % len(line_list)
            line_post = line_list[index_post]
            type_post = line_post['type']
            width_post = line_post['width']
        else:
            break
        merge_flag = 0
    # 返回信息
    if suit_width < 0:
        suit_depth, suit_depth_min = min(group_depth, suit_depth), min(group_depth, suit_depth_min)
    return suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best


# 计算墙体区域差集
def compute_diff_ratio(ratio_1, ratio_2):
    if ratio_2[1] <= ratio_1[0] or ratio_2[0] >= ratio_1[1]:
        ratio_result = [ratio_1[0], ratio_1[1]]
    elif ratio_2[0] <= ratio_1[0] and ratio_2[1] >= ratio_1[1]:
        ratio_result = [0, 0]
    elif ratio_2[0] <= ratio_1[0] < ratio_2[1]:
        ratio_result = [ratio_2[1], ratio_1[1]]
    elif ratio_2[0] < ratio_1[1] <= ratio_2[1]:
        ratio_result = [ratio_1[0], ratio_2[0]]
    elif ratio_1[0] < ratio_2[0] and ratio_2[1] < ratio_1[1]:
        ratio_result = [ratio_1[0], ratio_2[0]]
        if ratio_1[1] - ratio_2[1] > ratio_2[0] - ratio_1[0]:
            ratio_result = [ratio_2[1], ratio_1[1]]
    return ratio_result


# 计算墙体对面区域
def compute_pair_ratio(line_old, ratio_old, line_new):
    # 对面平行
    angle_old = line_old['angle']
    stand_old = determine_line_angle(angle_old)
    angle_new = line_new['angle']
    stand_new = determine_line_angle(angle_new)
    # 排除垂直
    if not stand_new == stand_old:
        return 0, 0, [], [], []
    # 排除阳角
    if abs(angle_new - angle_old) < 1:
        return 0, 0, [], [], []
    p1_old, p2_old, p1_new, p2_new = line_old['p1'], line_old['p2'], line_new['p1'], line_new['p2']

    # 更新两点
    if stand_old == 0:
        if (p2_new[0] - p1_new[0]) * (p1_old[1] - p2_new[1]) > 0:
            return 0, 0, [], [], []
    elif stand_new == 1:
        if (p2_new[1] - p1_new[1]) * (p1_old[0] - p2_new[0]) < 0:
            return 0, 0, [], [], []
    # 对面比例
    if stand_new == 0:
        ratio_face = [(p2_new[0] - p1_old[0]) / (p2_old[0] - p1_old[0]),
                      (p1_new[0] - p1_old[0]) / (p2_old[0] - p1_old[0])]
        depth_new = abs(p1_new[1] - p1_old[1])
    elif stand_new == 1:
        ratio_face = [(p2_new[1] - p1_old[1]) / (p2_old[1] - p1_old[1]),
                      (p1_new[1] - p1_old[1]) / (p2_old[1] - p1_old[1])]
        depth_new = abs(p1_new[0] - p1_old[0])
    elif abs(ang_to_ang(angle_new - angle_old - math.pi)) < 0.1:
        width_old = line_old['width']
        dlt_x, dlt_z = p1_new[0] - p1_old[0], p1_new[1] - p1_old[1]
        x_1 = dlt_z * math.sin(-math.pi / 2 - angle_old) + dlt_x * math.cos(-math.pi / 2 - angle_old)
        z_1 = dlt_z * math.cos(-math.pi / 2 - angle_old) - dlt_x * math.sin(-math.pi / 2 - angle_old)
        dlt_x, dlt_z = p2_new[0] - p1_old[0], p2_new[1] - p1_old[1]
        x_2 = dlt_z * math.sin(-math.pi / 2 - angle_old) + dlt_x * math.cos(-math.pi / 2 - angle_old)
        z_2 = dlt_z * math.cos(-math.pi / 2 - angle_old) - dlt_x * math.sin(-math.pi / 2 - angle_old)
        if min(z_1, z_2) > 1:
            ratio_face = [-x_2 / width_old, -x_1 / width_old]
            depth_new = min(z_1, z_2)
        else:
            return 0, 0, [], [], []
    else:
        return 0, 0, [], [], []
    if ratio_face[1] <= ratio_old[0] or ratio_face[0] >= ratio_old[1]:
        return 0, 0, [], [], []
    if abs(ratio_face[0] - ratio_face[1]) < 0.001:
        return 0, 0, [], [], []
    # 对边参数
    ratio_min, ratio_max = ratio_face[0], ratio_face[1]
    ratio_new = [(ratio_max - ratio_face[1]) / (ratio_face[0] - ratio_face[1]),
                 (ratio_min - ratio_face[1]) / (ratio_face[0] - ratio_face[1])]
    width_new = line_new['width'] * (ratio_new[1] - ratio_new[0])
    # 原边参数
    ratio_pair = ratio_face[:]
    if ratio_pair[0] < ratio_old[0]:
        ratio_pair[0] = ratio_old[0]
    if ratio_pair[1] > ratio_old[1]:
        ratio_pair[1] = ratio_old[1]
    ratio_min = ratio_pair[0]
    ratio_max = ratio_pair[1]
    ratio_best = [(ratio_max - ratio_face[1]) / (ratio_face[0] - ratio_face[1]),
                  (ratio_min - ratio_face[1]) / (ratio_face[0] - ratio_face[1])]
    return width_new, depth_new, ratio_new, ratio_best, ratio_pair


# 计算墙体区域冲突
def compute_line_impact(line_1, ratio_1, width_1, depth_1, line_2, ratio_2, width_2, depth_2, ratio_2_best=[]):
    # 角度判断
    angle1 = line_1['angle']
    angle2 = line_2['angle']
    if line_1 == line_2:
        ratio_1_new = ratio_1[:]
        ratio_2_new = ratio_2[:]
        if len(ratio_2_best) >= 2:
            if ratio_2_best[0] - 0 <= 1 - ratio_2_best[1]:
                ratio_2_new[1] = min(ratio_2_best[0] + width_2 / line_2['width'], ratio_2[1])
            else:
                ratio_2_new[0] = max(ratio_2_best[1] - width_2 / line_2['width'], ratio_2[0])
        else:
            ratio_2_new[1] = min(ratio_2[0] + width_2 / line_2['width'], ratio_2[1])
        if ratio_1_new[1] <= ratio_2_new[0] or ratio_1_new[0] >= ratio_2_new[1]:
            return True, False, ratio_1_new, ratio_2_new, 0, depth_1
        elif ratio_1_new[0] <= ratio_2_new[0] <= ratio_1_new[1]:
            ratio_1_new[1] = min(ratio_1_new[1], ratio_2_new[0])
            if line_1['width'] * (ratio_1_new[1] - ratio_1_new[0]) >= width_1 * 0.8:
                return True, True, ratio_1_new, ratio_2_new, 0, depth_1
            else:
                return False, False, ratio_1_new, ratio_2_new, 0, depth_1
        elif ratio_1_new[0] <= ratio_2_new[1] <= ratio_1_new[1]:
            ratio_1_new[0] = max(ratio_1_new[0], ratio_2_new[1])
            if line_1['width'] * (ratio_1_new[1] - ratio_1_new[0]) >= width_1 * 0.8:
                return True, True, ratio_1_new, ratio_2_new, 0, depth_1
            else:
                return False, False, ratio_1_new, ratio_2_new, 0, depth_1
        else:
            return False, False, ratio_1_new, ratio_2_new, 0, depth_1
    elif abs(angle1 - angle2) <= 0.01 and line_1['width'] >= width_1:
        return True, False, ratio_1, ratio_2, 0, 0
    else:
        pass
    width_1_max = line_1['width'] * (ratio_1[1] - ratio_1[0])
    if width_1 > width_1_max:
        width_1 = width_1_max
    width_2_max = line_2['width'] * (ratio_2[1] - ratio_2[0])
    if width_2 > width_2_max:
        width_2 = width_2_max

    # 线段1
    p1, p2 = line_1['p1'], line_1['p2']
    x_delta1 = depth_1 * math.sin(angle1 + math.pi / 2)
    y_delta1 = depth_1 * math.cos(angle1 + math.pi / 2)
    rect_ratio_1 = [[ratio_1[0], ratio_1[0] + width_1 / line_1['width']],
                    [ratio_1[1] - width_1 / line_1['width'], ratio_1[1]]]
    # 矩形1-1
    r1 = rect_ratio_1[0][0]
    r2 = rect_ratio_1[0][1]
    a1 = [p1[0] * (1 - r1) + p2[0] * r1, p1[1] * (1 - r1) + p2[1] * r1]
    a2 = [p1[0] * (1 - r2) + p2[0] * r2, p1[1] * (1 - r2) + p2[1] * r2]
    a3 = [a2[0] + x_delta1, a2[1] + y_delta1]
    a4 = [a1[0] + x_delta1, a1[1] + y_delta1]
    # 矩形1-2
    r1 = rect_ratio_1[1][0]
    r2 = rect_ratio_1[1][1]
    b1 = [p1[0] * (1 - r1) + p2[0] * r1, p1[1] * (1 - r1) + p2[1] * r1]
    b2 = [p1[0] * (1 - r2) + p2[0] * r2, p1[1] * (1 - r2) + p2[1] * r2]
    b3 = [b2[0] + x_delta1, b2[1] + y_delta1]
    b4 = [b1[0] + x_delta1, b1[1] + y_delta1]

    # 线段2
    p1, p2 = line_2['p1'], line_2['p2']
    x_delta2 = depth_2 * math.sin(angle2 + math.pi / 2)
    y_delta2 = depth_2 * math.cos(angle2 + math.pi / 2)
    rect_ratio_2 = [[ratio_2[0], ratio_2[0] + width_2 / line_2['width']],
                    [ratio_2[1] - width_2 / line_2['width'], ratio_2[1]]]
    # 矩形2-1
    r1 = rect_ratio_2[0][0]
    r2 = rect_ratio_2[0][1]
    c1 = [p1[0] * (1 - r1) + p2[0] * r1, p1[1] * (1 - r1) + p2[1] * r1]
    c2 = [p1[0] * (1 - r2) + p2[0] * r2, p1[1] * (1 - r2) + p2[1] * r2]
    c3 = [c2[0] + x_delta2, c2[1] + y_delta2]
    c4 = [c1[0] + x_delta2, c1[1] + y_delta2]
    # 矩形2-2
    r1 = rect_ratio_2[1][0]
    r2 = rect_ratio_2[1][1]
    d1 = [p1[0] * (1 - r1) + p2[0] * r1, p1[1] * (1 - r1) + p2[1] * r1]
    d2 = [p1[0] * (1 - r2) + p2[0] * r2, p1[1] * (1 - r2) + p2[1] * r2]
    d3 = [d2[0] + x_delta2, d2[1] + y_delta2]
    d4 = [d1[0] + x_delta2, d1[1] + y_delta2]

    # 矩形碰撞
    rect_list_1 = [[a1, a2, a3, a4], [b1, b2, b3, b4]]
    rect_list_2 = [[c1, c2, c3, c4], [d1, d2, d3, d4]]
    x_min_1_all, x_max_1_all = min(a1[0], a3[0], b1[0], b3[0]), max(a1[0], a3[0], b1[0], b3[0])
    y_min_1_all, y_max_1_all = min(a1[1], a3[1], b1[1], b3[1]), max(a1[1], a3[1], b1[1], b3[1])

    suit_once, impact_once = False, False
    suit_ratio1, suit_ratio2 = [], []
    suit_ratio2_list = []
    suit_distance, suit_distance_x, suit_distance_y = 0, 0, 0
    suit_depth = 0
    for index_one, rect_one in enumerate(rect_list_1):
        x_min_1 = min(rect_one[0][0], rect_one[1][0], rect_one[2][0], rect_one[3][0])
        y_min_1 = min(rect_one[0][1], rect_one[1][1], rect_one[2][1], rect_one[3][1])
        x_max_1 = max(rect_one[0][0], rect_one[1][0], rect_one[2][0], rect_one[3][0])
        y_max_1 = max(rect_one[0][1], rect_one[1][1], rect_one[2][1], rect_one[3][1])
        x_center_1 = (x_min_1 + x_max_1) / 2
        y_center_1 = (y_min_1 + y_max_1) / 2
        for index_two, rect_two in enumerate(rect_list_2):
            x_min_2 = min(rect_two[0][0], rect_two[1][0], rect_two[2][0], rect_two[3][0])
            y_min_2 = min(rect_two[0][1], rect_two[1][1], rect_two[2][1], rect_two[3][1])
            x_max_2 = max(rect_two[0][0], rect_two[1][0], rect_two[2][0], rect_two[3][0])
            y_max_2 = max(rect_two[0][1], rect_two[1][1], rect_two[2][1], rect_two[3][1])
            x_center_2 = (x_min_2 + x_max_2) / 2
            y_center_2 = (y_min_2 + y_max_2) / 2
            if x_min_2 - 0.01 >= x_max_1 or x_max_2 + 0.01 <= x_min_1 \
                    or y_min_2 - 0.01 >= y_max_1 or y_max_2 + 0.01 <= y_min_1:
                suit_once = True
                temp_distance_x = abs(x_center_1 - x_center_2)
                temp_distance_y = abs(y_center_1 - y_center_2)
                if temp_distance_x + temp_distance_y > suit_distance_x + suit_distance_y:
                    suit_distance_x = temp_distance_x
                    suit_distance_y = temp_distance_y
                    suit_ratio1 = rect_ratio_1[index_one][:]
                    suit_ratio2 = rect_ratio_2[index_two][:]
                    # 水平
                    if determine_line_angle(line_1['angle']) == 0:
                        if y_min_2 + 0.01 >= y_max_1 or y_max_2 - 0.01 <= y_min_1:
                            suit_ratio1 = ratio_1[:]
                        else:
                            x_add = min(x_min_2, x_max_1_all) - x_max_1
                            if x_add < x_min_1 - max(x_max_2, x_min_1_all):
                                x_add = x_min_1 - max(x_max_2, x_min_1_all)
                            if index_one == 0:
                                suit_ratio1[1] += x_add / line_1['width']
                            else:
                                suit_ratio1[0] -= x_add / line_1['width']
                    # 竖直
                    elif determine_line_angle(line_1['angle']) == 1:
                        if x_min_2 + 0.01 >= x_max_1 or x_max_2 - 0.01 <= x_min_1:
                            suit_ratio1 = ratio_1[:]
                        else:
                            y_add = min(y_min_2, y_max_1_all) - y_max_1
                            if y_add < y_min_1 - max(y_max_2, y_min_1_all):
                                y_add = y_min_1 - max(y_max_2, y_min_1_all)
                            if index_one == 0:
                                suit_ratio1[1] += y_add / line_1['width']
                            else:
                                suit_ratio1[0] -= y_add / line_1['width']
                    plus_depth = UNIT_DEPTH_DODGE * 4.0
                    if x_min_2 - 0.01 >= x_max_1:
                        suit_distance = x_min_2 - x_max_1
                        if abs(ang_to_ang(angle1 - 0)) < 0.1 or abs(ang_to_ang(angle1 - math.pi)) < 0.1:
                            plus_depth = min(plus_depth, suit_distance)
                    elif x_max_2 + 0.01 <= x_min_1:
                        suit_distance = x_min_1 - x_max_2
                        if abs(ang_to_ang(angle1 - 0)) < 0.1 or abs(ang_to_ang(angle1 - math.pi)) < 0.1:
                            plus_depth = min(plus_depth, suit_distance)
                    elif y_min_2 - 0.01 >= y_max_1:
                        suit_distance = y_min_2 - y_max_1
                        if abs(ang_to_ang(angle1 - math.pi / 2)) < 0.1 or abs(ang_to_ang(angle1 + math.pi / 2)) < 0.1:
                            plus_depth = min(plus_depth, suit_distance)
                    elif y_max_2 + 0.01 <= y_min_1:
                        suit_distance = y_min_1 - y_max_2
                        if abs(ang_to_ang(angle1 - math.pi / 2)) < 0.1 or abs(ang_to_ang(angle1 + math.pi / 2)) < 0.1:
                            plus_depth = min(plus_depth, suit_distance)
                    # 深度
                    suit_depth = depth_1 + plus_depth
                    if suit_distance < 0.05:
                        suit_distance = 0
                    if index_two <= 0:
                        suit_ratio2[1] += suit_distance / line_2['width']
                        if suit_ratio2[1] >= ratio_2[1]:
                            suit_ratio2[1] = ratio_2[1]
                        suit_ratio2_list.append(suit_ratio2)
                    elif index_two >= 1:
                        suit_ratio2[0] -= suit_distance / line_2['width']
                        if suit_ratio2[0] <= ratio_2[0]:
                            suit_ratio2[0] = ratio_2[0]
                        suit_ratio2_list.append(suit_ratio2)
                else:
                    suit_ratio2 = rect_ratio_2[index_two][:]
                    suit_ratio2_list.append(suit_ratio2)
            else:
                impact_once = True
    if 'depth_all' in line_1 and len(suit_ratio1) >= 2:
        for depth_one in line_1['depth_all']:
            if depth_one[0] <= suit_ratio1[0] <= depth_one[1] - 0.1:
                if suit_depth > depth_one[2]:
                    suit_depth = depth_one[2]
            if depth_one[0] + 0.1 <= suit_ratio1[1] <= depth_one[1]:
                if suit_depth > depth_one[2]:
                    suit_depth = depth_one[2]
    if len(suit_ratio2_list) >= 4:
        pass
    elif len(suit_ratio2_list) >= 2:
        if suit_ratio2_list[0][1] >= suit_ratio2_list[1][0] - 0.05:
            suit_ratio2 = [suit_ratio2_list[0][0], suit_ratio2_list[1][1]]
    return suit_once, impact_once, suit_ratio1, suit_ratio2, suit_distance, suit_depth


# 计算墙体到点距离
def compute_line_distance(line, ratio, point, depth=0, mode=2):
    if len(point) < 2:
        return 10, 10, 10
    p1 = line['p1'][:]
    p2 = line['p2'][:]
    ratio_po = (ratio[0] + ratio[1]) / 2
    if depth > 0.01:
        angle = line['angle'] + math.pi / 2
        x_delta = depth * math.sin(angle)
        y_delta = depth * math.cos(angle)
        p1[0] += x_delta
        p2[0] += x_delta
        p1[1] += y_delta
        p2[1] += y_delta
    p1_suit = [p1[0] * (1 - ratio[0]) + p2[0] * ratio[0], p1[1] * (1 - ratio[0]) + p2[1] * ratio[0]]
    p2_suit = [p1[0] * (1 - ratio[1]) + p2[0] * ratio[1], p1[1] * (1 - ratio[1]) + p2[1] * ratio[1]]
    p3_suit = [p1[0] * (1 - ratio_po) + p2[0] * ratio_po, p1[1] * (1 - ratio_po) + p2[1] * ratio_po]
    if mode == 1:
        distance_p1 = abs(p1_suit[0] - point[0]) + abs(p1_suit[1] - point[1])
        distance_p2 = abs(p2_suit[0] - point[0]) + abs(p2_suit[1] - point[1])
        distance_p3 = abs(p3_suit[0] - point[0]) + abs(p3_suit[1] - point[1])
    else:
        distance_p1 = math.sqrt((p1_suit[0] - point[0]) * (p1_suit[0] - point[0]) +
                                (p1_suit[1] - point[1]) * (p1_suit[1] - point[1]))
        distance_p2 = math.sqrt((p2_suit[0] - point[0]) * (p2_suit[0] - point[0]) +
                                (p2_suit[1] - point[1]) * (p2_suit[1] - point[1]))
        distance_p3 = math.sqrt((p3_suit[0] - point[0]) * (p3_suit[0] - point[0]) +
                                (p3_suit[1] - point[1]) * (p3_suit[1] - point[1]))
    return distance_p1, distance_p2, distance_p3


# 计算墙体到点关系
def compute_point_inner(p1, p2, point):
    p1_suit, p2_suit = p1[:], p2[:]
    distance_p1 = abs(p1_suit[0] - point[0]) + abs(p1_suit[1] - point[1])
    distance_p2 = abs(p2_suit[0] - point[0]) + abs(p2_suit[1] - point[1])
    length_cur, angle_cur = compute_dis_ang(p1[0], p1[1], p2[0], p2[1])
    if distance_p1 <= distance_p2:
        length_side, angle_side = compute_dis_ang(point[0], point[1], p1[0], p1[1])
        side_order = -1
    else:
        length_side, angle_side = compute_dis_ang(p2[0], p2[1], point[0], point[1])
        side_order = 1
    angle_inner = normalize_line_angle(angle_cur + math.pi * 0.5 * side_order)
    angle_outer = normalize_line_angle(angle_cur - math.pi * 0.5 * side_order)
    inner_suit = -1
    # 平行
    if abs(ang_to_ang(angle_cur - angle_side)) < 0.4:
        inner_suit = 0
    # 阴角
    elif abs(ang_to_ang(angle_inner - angle_side)) < 0.4:
        inner_suit = 1
    # 阳角
    elif abs(ang_to_ang(angle_outer - angle_side)) < 0.4:
        inner_suit = -1
    # 其他
    else:
        angle_dlt = (angle_side - angle_cur) * side_order
        angle_dlt = ang_to_ang(angle_dlt)
        # 锐角
        if math.pi / 2 < angle_dlt <= math.pi:
            inner_suit = 0.5
        # 钝角
        elif 0 < angle_dlt <= math.pi / 2:
            inner_suit = -0.5
    return inner_suit


# 计算墙体到点距离
def compute_point_distance(p1, p2, ratio, point, mode=2):
    if len(point) < 2:
        return 10, 10, 10
    ratio_po = (ratio[0] + ratio[1]) / 2
    p1_suit = [p1[0] * (1 - ratio[0]) + p2[0] * ratio[0], p1[1] * (1 - ratio[0]) + p2[1] * ratio[0]]
    p2_suit = [p1[0] * (1 - ratio[1]) + p2[0] * ratio[1], p1[1] * (1 - ratio[1]) + p2[1] * ratio[1]]
    p3_suit = [p1[0] * (1 - ratio_po) + p2[0] * ratio_po, p1[1] * (1 - ratio_po) + p2[1] * ratio_po]
    if mode == 1:
        distance_p1 = abs(p1_suit[0] - point[0]) + abs(p1_suit[1] - point[1])
        distance_p2 = abs(p2_suit[0] - point[0]) + abs(p2_suit[1] - point[1])
        distance_p3 = abs(p3_suit[0] - point[0]) + abs(p3_suit[1] - point[1])
    else:
        distance_p1 = math.sqrt((p1_suit[0] - point[0]) * (p1_suit[0] - point[0]) +
                                (p1_suit[1] - point[1]) * (p1_suit[1] - point[1]))
        distance_p2 = math.sqrt((p2_suit[0] - point[0]) * (p2_suit[0] - point[0]) +
                                (p2_suit[1] - point[1]) * (p2_suit[1] - point[1]))
        distance_p3 = math.sqrt((p3_suit[0] - point[0]) * (p3_suit[0] - point[0]) +
                                (p3_suit[1] - point[1]) * (p3_suit[1] - point[1]))
    return distance_p1, distance_p2, distance_p3


# 计算分组矩形顶点
def compute_group_bound(size, position, rotation, adjust=[0, 0, 0, 0], direct=0):
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


# 计算分组矩形范围
def compute_group_scope(group_one, adjust_flag=0):
    # 原有范围
    type_one = group_one['type']
    adjust_one = [0, 0, 0, 0]
    if 'regulation' in group_one:
        adjust_one = group_one['regulation'][:]
        if adjust_flag >= 1:
            if adjust_one[0] > 0:
                adjust_one[0] = 0
            if adjust_one[1] > 0:
                adjust_one[1] = 0
            if adjust_one[2] > 0:
                adjust_one[2] = 0
            if adjust_one[3] > 0:
                adjust_one[3] = 0
    # 调整范围
    adjust_new = [0, 0, 0, 0]
    if adjust_flag >= 1:
        if type_one in ['Work'] and group_one['size'][2] - group_one['size_min'][2] <= 0.5:
            adjust_new = [0, 0, 0.2, 0]
        elif type_one in ['Toilet']:
            adjust_new = [0, 0, 0.2, 0]
        elif type_one in ['Armoire']:
            adjust_new = [0, 0, 0.2, 0]
        elif type_one in ['Cabinet']:
            adjust_new = [0, 0, 0.2, 0]
        elif type_one in ['Appliance']:
            adjust_new = [0, 0, 0.2, 0]
    adjust_one[0] += adjust_new[0]
    adjust_one[1] += adjust_new[1]
    adjust_one[2] += adjust_new[2]
    adjust_one[3] += adjust_new[3]
    # 避碰范围
    unit_1 = compute_group_bound(group_one['size'], group_one['position'], group_one['rotation'], adjust_one)
    rect_1 = [
        [unit_1[0], unit_1[1]],
        [unit_1[2], unit_1[3]],
        [unit_1[4], unit_1[5]],
        [unit_1[6], unit_1[7]]
    ]
    x_min_1 = min(rect_1[0][0], rect_1[1][0], rect_1[2][0], rect_1[3][0])
    x_max_1 = max(rect_1[0][0], rect_1[1][0], rect_1[2][0], rect_1[3][0])
    y_min_1 = min(rect_1[0][1], rect_1[1][1], rect_1[2][1], rect_1[3][1])
    y_max_1 = max(rect_1[0][1], rect_1[1][1], rect_1[2][1], rect_1[3][1])
    return x_min_1, y_min_1, x_max_1, y_max_1


# 计算分组组件信息
def compute_group_unit(group_list, mesh_list=[], deco_list=[], deco_mode=0):
    type_fine, unit_fine, height_fine, back_fine = [], [], [], []
    # 软装组件
    for group_one in group_list:
        # 类型
        group_type = group_one['type']
        type_fine.append(group_one['type'])
        # 轮廓
        unit_adjust = [0, 0, 0, 0]
        if 'regulation' in group_one:
            unit_adjust = group_one['regulation'][:]
            unit_adjust[2] = min(unit_adjust[2], 1.0)
        unit_one = compute_group_bound(group_one['size'], group_one['position'], group_one['rotation'], unit_adjust)
        unit_one.append(unit_one[0])
        unit_one.append(unit_one[1])
        unit_fine.append(unit_one)
        # 高度
        height_fine.append(group_one['size'][1])
    # 硬装组件
    for mesh_one in mesh_list:
        mesh_role = ''
        if 'role' in mesh_one:
            mesh_role = mesh_one['role']
        unit_adjust = [0, 0, 0, 0]
        unit_pos, unit_rot = mesh_one['position'][:], mesh_one['rotation'][:]
        unit_size = [abs(mesh_one['size'][i] * mesh_one['scale'][i]) / 100 for i in range(3)]
        # 尺寸纠正
        if unit_size[0] < 0.5 and unit_size[2] > 1:
            unit_size_rev = [unit_size[2], unit_size[1], unit_size[0]]
            unit_ang_rev = ang_to_ang(rot_to_ang(unit_rot) + math.pi / 2)
            unit_rot_rev = [0, math.sin(unit_ang_rev / 2), 0, math.cos(unit_ang_rev / 2)]
            unit_size, unit_rot = unit_size_rev, unit_rot_rev
            if unit_size[0] > unit_size[2] * 5:
                mesh_role = 'Background'
        # 角色分配
        if mesh_role.lower() in ['cabinet']:
            # 类型
            type_fine.append('Mesh')
            # 轮廓
            unit_one = compute_group_bound(unit_size, unit_pos, unit_rot, unit_adjust)
            unit_one.append(unit_one[0])
            unit_one.append(unit_one[1])
            unit_fine.append(unit_one)
            height_fine.append(unit_size[1])
        elif mesh_role.lower() in ['background', 'curtain', 'window']:
            # 轮廓
            unit_one = compute_group_bound(unit_size, unit_pos, unit_rot, unit_adjust)
            back_fine.append(unit_one)
    # 装饰组件
    for deco_one in deco_list:
        if 'type' in deco_one and deco_one['type'] == 3:
            deco_type = 'curtain'
            if deco_mode >= 1:
                deco_width, deco_height = 0, 0
                if 'width' in deco_one:
                    deco_width = deco_one['width']
                if 'height' in deco_one:
                    deco_height = deco_one['height']
                if deco_width <= 3 and deco_height <= UNIT_HEIGHT_WALL - 0.2:
                    continue
        if 'p1' in deco_one and 'p2' in deco_one and 'p3' in deco_one and 'p4' in deco_one:
            p1, p2, p3, p4 = deco_one['p1'], deco_one['p2'], deco_one['p3'], deco_one['p4']
            unit_one = [p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1]]
            back_fine.append(unit_one)
    # 返回信息
    return type_fine, unit_fine, height_fine, back_fine


# 计算墙体避让区域
def compute_group_dodge(p_1, p_2, p_min, p_max, q_1, q_2, delta=0.3, dump=0):
    p_direct = 0
    p_delete = 0
    # 下移 或 右移
    if q_1 <= p_1:
        p_direct = 1
        if q_2 + delta <= p_1 + 0.001:
            if p_min < q_2 + delta:
                p_min = q_2 + delta
            return 0, p_1, p_2, p_min, p_max, p_direct, p_delete
        if q_2 + delta - p_1 <= p_max - p_2:
            if p_min < q_2 + delta:
                p_min = q_2 + delta
            p_move = q_2 + delta - p_1
            p_1 += p_move
            p_2 += p_move
            if p_min > p_1:
                p_min = p_1
        elif q_2 - p_1 <= p_max - p_2:
            if p_min < q_2 + p_max - p_2:
                p_min = q_2 + p_max - p_2
            p_move = p_max - p_2
            p_1 += p_move
            p_2 += p_move
            if p_min > p_1:
                p_min = p_1
        # 裁剪处理
        elif q_2 + delta - p_1 <= p_max - p_2 + dump:
            if p_min < q_2 + delta:
                p_min = q_2 + delta
            p_move = q_2 + delta - p_1
            p_1 += p_move
            p_2 += p_move
            p_delete = dump
            if p_delete > p_move:
                p_delete = p_move
        elif q_2 - p_1 <= p_max - p_2 + dump:
            if p_min < q_2:
                p_min = q_2
            p_move = p_max - p_2 + dump
            p_1 += p_move
            p_2 += p_move
            p_delete = dump
        else:
            p_move = p_max - p_2
            p_1 += p_move
            p_2 += p_move
            if p_min > p_1:
                p_min = p_1
            return -1, p_1, p_2, p_min, p_max, p_direct, p_delete
    # 上移 或 左移
    elif q_2 >= p_2:
        p_direct = -1
        if q_1 - delta >= p_2 - 0.001:
            if p_max > q_1 - delta:
                p_max = q_1 - delta
            return 0, p_1, p_2, p_min, p_max, p_direct, p_delete
        if p_2 - (q_1 - delta) <= p_1 - p_min:
            if p_max > q_1 - delta:
                p_max = q_1 - delta
            p_move = p_2 - (q_1 - delta)
            p_1 -= p_move
            p_2 -= p_move
            if p_max < p_2:
                p_max = p_2
        elif p_2 - q_1 <= p_1 - p_min:
            if p_max > p_2 - (p_1 - p_min):
                p_max = p_2 - (p_1 - p_min)
            p_move = p_1 - p_min
            p_1 -= p_move
            p_2 -= p_move
            if p_max < p_2:
                p_max = p_2
        # 裁剪处理
        elif p_2 - (q_1 - delta) <= p_1 - p_min + dump:
            if p_max > q_1 - delta:
                p_max = q_1 - delta
            p_move = p_2 - (q_1 - delta)
            p_1 -= p_move
            p_2 -= p_move
            p_delete = dump
            if p_delete > p_move:
                p_delete = p_move
        elif p_2 - q_1 <= p_1 - p_min + dump:
            if p_max > q_1:
                p_max = q_1
            p_move = p_1 - p_min + dump
            p_1 -= p_move
            p_2 -= p_move
            p_delete = dump
        else:
            p_move = p_1 - p_min
            p_1 -= p_move
            p_2 -= p_move
            if p_max < p_2:
                p_max = p_2
            return -1, p_1, p_2, p_min, p_max, p_direct, p_delete
    # 放弃
    else:
        return -1, p_1, p_2, p_min, p_max, p_direct, p_delete
    return 0, p_1, p_2, p_min, p_max, p_direct, p_delete


# 数据解析：计算角度
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


# 数据解析：规范角度
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