# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2019-01-18
@Description:

"""

import math
import heapq
import numpy as np


def compute_length(x1, y1, x2, y2):
    return round((((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5), 3)


def compute_collinear(x1, y1, x2, y2, x3, y3, epsilon=0.1):
    # same line
    sum1 = x1 * y2 - y1 * x2
    sum2 = x2 * y3 - y2 * x3
    sum3 = x3 * y1 - y3 * x1
    sum_line = sum1 + sum2 + sum3
    # middle line
    mid_flag = False
    if min(x1, x2) - epsilon <= x3 <= max(x1, x2) + epsilon and min(y1, y2) - epsilon <= y3 <= max(y1, y2) + epsilon:
        mid_flag = True
    if abs(sum_line) <= 1e-2 and mid_flag:
        return 1, abs(sum_line)
    else:
        return 0, 0


def compute_point_inner(point_list):
    index_list = [0, 0, 0, 0]
    minimum_two_number = heapq.nlargest(2, point_list)
    index_0 = point_list.index(minimum_two_number[0])
    index_1 = point_list.index(minimum_two_number[1])
    index_list[index_0] = 1
    index_list[index_1] = 1
    return index_list


def compute_point_align(point_list, floor_list):
    aligned_points = []
    two_inner_points_list = []
    is_found_point_on_floor = False
    for i in range(len(floor_list) // 2 - 1):
        flag_collinear_list = []
        sum_number_list = []
        x1, y1, x2, y2 = floor_list[2 * i + 0], floor_list[2 * i + 1], floor_list[2 * i + 2], floor_list[2 * i + 3]
        for j in range(len(point_list) // 2):
            x3, y3 = point_list[2*j+0], point_list[2*j+1]
            is_collinear, sum_number = compute_collinear(x1, y1, x2, y2, x3, y3)
            flag_collinear_list.append(is_collinear)
            sum_number_list.append(sum_number)
        if flag_collinear_list.count(1) == 4:
            flag_collinear_list = compute_point_inner(sum_number_list)
        elif len(flag_collinear_list) == 4 and flag_collinear_list.count(1) == 2:
            is_found_point_on_floor = True
            idx_is_found_sort = np.argsort(~(np.array(flag_collinear_list)))
            for k in range(len(idx_is_found_sort) - 2):
                point_new1 = point_list[2 * idx_is_found_sort[k]]
                point_new2 = point_list[2 * idx_is_found_sort[k] + 1]
                two_inner_points_list.append([point_new1, point_new2])
                aligned_points.append(point_new1)
                aligned_points.append(point_new2)
        elif len(flag_collinear_list) >= 4 and flag_collinear_list.count(1) >= 2:
            is_found_point_on_floor = True
            idx_is_found_sort = np.argsort(~(np.array(flag_collinear_list)))
            for k in range(len(idx_is_found_sort) - 3):
                point_new1 = point_list[2 * idx_is_found_sort[k]]
                point_new2 = point_list[2 * idx_is_found_sort[k] + 1]
                if [point_new1, point_new2] in two_inner_points_list:
                    continue
                two_inner_points_list.append([point_new1, point_new2])
                aligned_points.append(point_new1)
                aligned_points.append(point_new2)
        if is_found_point_on_floor:
            object_line = [floor_list[2*i+0], floor_list[2*i+1], floor_list[2*i+2], floor_list[2*i+3]]
            break

    if len(two_inner_points_list) <= 1:
        return []
    distance_two_inner_points = compute_length(two_inner_points_list[0][0], two_inner_points_list[0][1],
                                               two_inner_points_list[1][0], two_inner_points_list[1][1])
    two_outer_points_list = []
    for j in range(len(point_list) // 2):
        outer_point = [point_list[2*j+0], point_list[2*j+1]]
        if outer_point != two_inner_points_list[0] and outer_point != two_inner_points_list[1] and \
                outer_point not in two_outer_points_list:
            two_outer_points_list.append(outer_point)

    # sort
    distance_outer_points_list = []
    base_inner_point = [two_inner_points_list[0][0], two_inner_points_list[0][1]]
    # distance
    for outer_point in two_outer_points_list:
        distance_outer_points_list.append(compute_length(base_inner_point[0], base_inner_point[1],
                                                         outer_point[0], outer_point[1]))
    #
    for i, dis_outer_point in enumerate(distance_outer_points_list):
        if dis_outer_point > distance_two_inner_points:
            aligned_points.append(two_outer_points_list[i][0])
            aligned_points.append(two_outer_points_list[i][1])
    #
    for i, dis_outer_point in enumerate(distance_outer_points_list):
        if dis_outer_point <= distance_two_inner_points:
            aligned_points.append(two_outer_points_list[i][0])
            aligned_points.append(two_outer_points_list[i][1])
    return aligned_points

