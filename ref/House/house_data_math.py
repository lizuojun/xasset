# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-12-05
@Description:

"""

import math


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
    if abs(rot_1 - 1) < 0.0001 or abs(rot_1 + 1) < 0.0001:
        ang = math.pi
    elif abs(rot_3 - 1) < 0.0001 or abs(rot_3 + 1) < 0.0001:
        ang = 0
    else:
        if rot_1 > 0 and rot_3 > 0:
            ang = math.asin(rot_1) * 2
        elif rot_1 < 0 and rot_3 > 0:
            ang = math.asin(rot_1) * 2
        elif rot_1 > 0 and rot_3 < 0:
            ang = math.acos(rot_3) * 2
        elif rot_1 < 0 and rot_3 < 0:
            ang = (math.pi + math.pi - math.acos(rot_3)) * 2
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


def normalize_angle(angle_old):
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


def straight_angle(angle):
    if abs(abs(angle) - math.pi * 0.5) < 0.05 or abs(abs(angle) - math.pi * 1.5) < 0.05:
        return 0
    elif abs(angle) < 0.05 or abs(abs(angle) - math.pi) < 0.05 or abs(abs(angle) - math.pi * 2) < 0.05:
        return 1
    return -1


def compute_length(x1, y1, x2, y2):
    return round((((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5), 3)


def compute_length_angle(x1, y1, x2, y2):
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


def compute_bound(size, position, rotation, adjust=[0, 0, 0, 0]):
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


def compute_coincide_line(x1, y1, x2, y2, x3, y3, x4, y4, margin_min=0.1):
    line_width, line_angle = compute_length_angle(x1, y1, x2, y2)
    x_p, y_p, x_q, y_q = x3, y3, x4, y4
    unit_width, unit_angle = compute_length_angle(x_p, y_p, x_q, y_q)
    if unit_width < margin_min:
        return False, x_p, y_p, x_q, y_q
    # 靠墙吸附
    if straight_angle(line_angle) == 0:
        if not straight_angle(unit_angle) == 0:
            return False, x_p, y_p, x_q, y_q
        if abs(y_p - y1) < margin_min and abs(y_q - y1) < margin_min:
            x_min, x_max = min(x1, x2), max(x1, x2)
            if x_min < (x_p + x_q) / 2 < x_max:
                pass
            else:
                return False, x_p, y_p, x_q, y_q
        else:
            return False, x_p, y_p, x_q, y_q
    elif straight_angle(line_angle) == 1:
        if not straight_angle(unit_angle) == 1:
            return False, x_p, y_p, x_q, y_q
        if abs(x_p - x1) < margin_min and abs(x_q - x1) < margin_min:
            y_min, y_max = min(y1, y2), max(y1, y2)
            if y_min < (y_p + y_q) / 2 < y_max:
                pass
            else:
                return False, x_p, y_p, x_q, y_q
        else:
            return False, x_p, y_p, x_q, y_q
    else:
        r_p_x = (x_p - x1) / (x2 - x1)
        r_p_y = (y_p - y1) / (y2 - y1)
        r_q_x = (x_q - x1) / (x2 - x1)
        r_q_y = (y_q - y1) / (y2 - y1)
        if abs(r_p_x - r_p_y) > 0.01 or abs(r_q_x - r_q_y) > 0.01:
            return False, x_p, y_p, x_q, y_q
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        if x_min < (x_p + x_q) / 2 < x_max and y_min < (y_p + y_q) / 2 < y_max:
            pass
        else:
            return False, x_p, y_p, x_q, y_q
    unit_width, unit_angle = compute_length_angle(x_p, y_p, x_q, y_q)
    if unit_width < margin_min:
        return False, x_p, y_p, x_q, y_q
    return True, x_p, y_p, x_q, y_q


def compute_coincide_list(unit_one, line_set):
    line_len = int(len(line_set) / 2)
    edge_len = int(len(unit_one) / 2)
    for i in range(line_len):
        x1 = line_set[(2 * i + 0) % len(line_set)]
        y1 = line_set[(2 * i + 1) % len(line_set)]
        x2 = line_set[(2 * i + 2) % len(line_set)]
        y2 = line_set[(2 * i + 3) % len(line_set)]
        for j in range(edge_len):
            x_p = unit_one[(2 * j + 0) % len(unit_one)]
            y_p = unit_one[(2 * j + 1) % len(unit_one)]
            x_q = unit_one[(2 * j + 2) % len(unit_one)]
            y_q = unit_one[(2 * j + 3) % len(unit_one)]
            coincide, x_p, y_p, x_q, y_q = compute_coincide_line(x1, y1, x2, y2, x_p, y_p, x_q, y_q)
            if coincide:
                # unit_one[(2 * j + 0) % len(unit_one)] = x_p
                # unit_one[(2 * j + 1) % len(unit_one)] = y_p
                # unit_one[(2 * j + 2) % len(unit_one)] = x_q
                # unit_one[(2 * j + 3) % len(unit_one)] = y_q
                return True
    return False


def compute_coincide_unit(unit_old, unit_new, margin_min=0.5):
    position_old, position_new = [], []
    if len(unit_old) >= 8:
        position_old = [(unit_old[0] + unit_old[2] + unit_old[4] + unit_old[6]) / 4,
                        (unit_old[1] + unit_old[3] + unit_old[5] + unit_old[7]) / 4]
    elif len(unit_old) >= 2:
        position_old = [unit_old[0], unit_old[1]]
    if len(unit_new) >= 8:
        position_new = [(unit_new[0] + unit_new[2] + unit_new[4] + unit_new[6]) / 4,
                        (unit_new[1] + unit_new[3] + unit_new[5] + unit_new[7]) / 4]
    elif len(unit_old) >= 2:
        position_new = [unit_new[0], unit_new[1]]
    if len(position_old) < 2 or len(position_new) < 2:
        return False
    length = compute_length(position_old[0], position_old[1], position_new[0], position_new[1])
    if length < margin_min:
        return True
    return False