# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2019-01-18
@Description:

"""

import math


def compute_angle(p0, p1, p2):
    a = math.pow(p1[0]-p0[0], 2) + math.pow(p1[1]-p0[1], 2)
    b = math.pow(p1[0]-p2[0], 2) + math.pow(p1[1]-p2[1], 2)
    c = math.pow(p2[0]-p0[0], 2) + math.pow(p2[1]-p0[1], 2)
    if a*b == 0:
        return 0
    else:
        return math.acos((a+b-c)/math.sqrt(4*a*b))


def compute_clockwise(point_list):
    point_edge = 0
    point_numb = len(point_list) // 2
    for i in range(point_numb - 1):
        point_edge += round((point_list[2 * i + 2] - point_list[2 * i + 0]) * (point_list[2 * i + 3] + point_list[2 * i + 1]), 3)
    point_edge += round((point_list[0] - point_list[-2]) * (point_list[1] + point_list[-1]), 3)
    if point_edge >= 0:
        return True
    else:
        return False


def generate_point_clockwise(point_list):
    point_list_clockwise = []
    if len(point_list) == 0:
        return []
    #
    for point in point_list:
        point_list_temp = []
        if len(point) <= 0:
            continue
        if compute_clockwise(point):
            angle1 = compute_angle([point[0], point[1]], [point[2], point[3]], [point[4], point[5]])
            angle2 = compute_angle([point[0], point[1]], [point[2], point[3]], [point[6], point[7]])
            if angle1 > angle2:
                point_idx = [0, 1, 2, 3, 4, 5, 6, 7]
                for idx in point_idx:
                    point_list_temp.append(point[idx])
                point_list_clockwise.append(point_list_temp)
            else:
                point_idx = [0, 1, 2, 3, 6, 7, 4, 5]
                for idx in point_idx:
                    point_list_temp.append(point[idx])
                point_list_clockwise.append(point_list_temp)
        else:
            angle1 = compute_angle([point[2], point[3]], [point[0], point[1]], [point[4], point[5]])
            angle2 = compute_angle([point[2], point[3]], [point[0], point[1]], [point[6], point[7]])
            if angle1 > angle2:
                point_idx = [2, 3, 0, 1, 4, 5, 6, 7]
                for idx in point_idx:
                    point_list_temp.append(point[idx])
                point_list_clockwise.append(point_list_temp)
            else:
                point_idx = [2, 3, 0, 1, 6, 7, 4, 5]
                for idx in point_idx:
                    point_list_temp.append(point[idx])
                point_list_clockwise.append(point_list_temp)
    return point_list_clockwise

