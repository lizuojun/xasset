# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-01-18
@Description: 解析户型数据细节，包括房间的轮廓、门、窗、门洞、飘窗等信息

"""

from scipy.spatial import ConvexHull

from House.point_align import *
from House.point_clock import *
from House.house_data_math import *


class FloorData(object):
    def __init__(self):
        self.floor_list = []
        self.floor_list_clockwise = []
        self.mesh_type = 'Floor'
        self.MAX_GRADIENT_VALUE = 1e5

    def load_data(self, mesh_list):
        self.floor_list = []
        if len(mesh_list) == 0:
            return False
        room_line_list = []
        grid_face_list = []
        for mesh_one in mesh_list:
            mesh_xyz = mesh_one['xyz']
            mesh_faces = mesh_one['faces']
            mesh_xz_ori = []
            for i in range(len(mesh_xyz) // 3):
                mesh_xz_ori.append([round(float(mesh_xyz[3 * i + 0]), 3), round(float(mesh_xyz[3 * i + 2]), 3)])
            if len(mesh_xz_ori) == 0:
                return False
            mesh_xz_new = []
            for index in mesh_faces:
                mesh_xz_new.append(mesh_xz_ori[index])
            if not len(mesh_xz_new) == len(mesh_xz_ori):
                return False
            for j in range(len(mesh_xz_new) // 3):
                p1 = mesh_xz_new[3 * j + 0]
                p2 = mesh_xz_new[3 * j + 1]
                p3 = mesh_xz_new[3 * j + 2]
                grid_face_list.append([[p1, p2], [p1, p3], [p2, p3]])
        # room line
        for face_one in grid_face_list:
            for line_one in face_one:
                line_rev = [line_one[1], line_one[0]]
                if line_one in room_line_list:
                    room_line_list.remove(line_one)
                elif line_rev in room_line_list:
                    room_line_list.remove(line_rev)
                else:
                    room_line_list.append(line_one)
        if len(room_line_list) == 0:
            return False
        # find segment
        if not self.find_area_clockwise(room_line_list):
            return False
        # merge line
        try:
            floor_list_ori = self.merge_line_direction()
            for floor_idx, floor_one in enumerate(floor_list_ori):
                if len(self.floor_list) >= 2:
                    # same dump
                    x_old, y_old = self.floor_list[-2], self.floor_list[-1]
                    x_cur, y_cur = floor_one[0][0], floor_one[0][1]
                    if abs(x_cur - x_old) + abs(y_cur - y_old) < 0.02:
                        continue
                    # line dump
                    if floor_idx + 1 < len(floor_list_ori):
                        floor_new = floor_list_ori[floor_idx + 1]
                        x_new, y_new = floor_new[0][0], floor_new[0][1]
                        len_old, ang_old = compute_length_angle(x_old, y_old, x_cur, y_cur)
                        len_new, ang_new = compute_length_angle(x_cur, y_cur, x_new, y_new)
                        if len_new < 0.01:
                            continue
                        if abs(ang_old - ang_new) < 0.01:
                            continue
                self.floor_list.append(floor_one[0][0])
                self.floor_list.append(floor_one[0][1])
            if len(floor_list_ori) > 0:
                self.floor_list.append(floor_list_ori[0][0][0])
                self.floor_list.append(floor_list_ori[0][0][1])
        except Exception as e:
            print(e)
            return False
        return True

    def find_area_clockwise(self, room_line_list):
        self.floor_list_clockwise = []
        line_x_list = []
        line_z_list = []
        for line_one in room_line_list:
            line_x_list.append(line_one[0][0])
            line_x_list.append(line_one[1][0])
            line_z_list.append(line_one[0][1])
            line_z_list.append(line_one[1][1])
        #
        max_line_z_value = max(line_z_list)
        max_line_z_count = line_z_list.count(max_line_z_value)
        if max_line_z_count == 2:
            max_z_index = line_z_list.index(max_line_z_value)
            apog_z_axis = [line_x_list[max_z_index], line_z_list[max_z_index]]
            line_z_axis = []
            line_z_delta, line_z_count = 0, 0
            for line_one in room_line_list:
                if line_one[0] == apog_z_axis or line_one[1] == apog_z_axis:
                    if not line_one[0][0] == line_one[1][0]:
                        if line_z_delta < abs(line_one[0][0] - line_one[1][0]):
                            line_z_delta = abs(line_one[0][0] - line_one[1][0])
                            line_z_axis = line_one
                    line_z_count += 1
                    if line_z_count >= 2:
                        break
            if len(line_z_axis) == 0:
                return False
            # line start
            if line_z_axis[0][0] > line_z_axis[1][0]:
                line_clockwise_start = [line_z_axis[1], line_z_axis[0]]
            else:
                line_clockwise_start = line_z_axis
            self.floor_list_clockwise.append(line_clockwise_start)
            # line next
            while len(room_line_list) > 0:
                line_clockwise_start_rev = [line_clockwise_start[1], line_clockwise_start[0]]
                if line_clockwise_start in room_line_list:
                    room_line_list.remove(line_clockwise_start)
                elif line_clockwise_start_rev in room_line_list:
                    room_line_list.remove(line_clockwise_start_rev)
                line_clockwise_next = self.find_line_connect(room_line_list, line_clockwise_start)
                if len(line_clockwise_next) == 0:
                    break
                self.floor_list_clockwise.append(line_clockwise_next)
                if line_clockwise_next in room_line_list:
                    room_line_list.remove(line_clockwise_next)
                line_clockwise_start = line_clockwise_next
        else:
            apog_z_index = []
            for index, value in enumerate(line_z_list):
                if value == max_line_z_value:
                    apog_z_index.append(index)
            corr_x_value = []
            for index in apog_z_index:
                corr_x_value.append(line_x_list[index])
            corr_x_value_array = np.array(corr_x_value)
            apog_z_index_array = np.array(apog_z_index)
            apog_z_index_sorted = apog_z_index_array[np.argsort(corr_x_value_array)]
            #
            corr_xz_value_array = []
            for index in apog_z_index_sorted:
                corr_xz_value_array.append([line_x_list[index], line_z_list[index]])
            apog_xz_value_array = []
            for xz_one in corr_xz_value_array:
                if xz_one not in apog_xz_value_array:
                    apog_xz_value_array.append(xz_one)
            if len(apog_xz_value_array) < 2:
                return False
            # line start
            line_clockwise_start = [apog_xz_value_array[0], apog_xz_value_array[1]]
            self.floor_list_clockwise.append(line_clockwise_start)
            # line next
            while len(room_line_list) > 0:
                line_clockwise_start_rev = [line_clockwise_start[1], line_clockwise_start[0]]
                if line_clockwise_start in room_line_list:
                    room_line_list.remove(line_clockwise_start)
                elif line_clockwise_start_rev in room_line_list:
                    room_line_list.remove(line_clockwise_start_rev)
                line_clockwise_next = self.find_line_connect(room_line_list, line_clockwise_start)
                if len(line_clockwise_next) == 0:
                    break
                self.floor_list_clockwise.append(line_clockwise_next)
                if line_clockwise_next in room_line_list:
                    room_line_list.remove(line_clockwise_next)
                line_clockwise_start = line_clockwise_next
        return True

    def find_line_connect(self, line_list, line_start):
        line_next = []
        if len(line_list) == 0:
            return line_next
        line_next_all = []
        for line_one in line_list:
            # 后续情况1
            if line_one[0] == line_start[1]:
                line_next = line_one
                line_next_all.append(line_next)
            elif line_one[1] == line_start[1]:
                line_next = [line_one[1], line_one[0]]
                line_next_all.append(line_next)
            # 后续情况2
            else:
                start_x0, start_x1 = line_start[0][0], line_start[1][0]
                start_y0, start_y1 = line_start[0][1], line_start[1][1]
                if line_one[0][0] == start_x0 and line_one[0][0] == start_x1:
                    if min(start_y0, start_y1) < line_one[0][1] < max(start_y0, start_y1):
                        line_next_new = [line_one[0], line_one[1]]
                        line_next_all.append(line_next_new)
                elif line_one[0][1] == start_y0 and line_one[0][1] == start_y1:
                    if min(start_x0, start_x1) < line_one[0][0] < max(start_x0, start_x1):
                        line_next_new = [line_one[0], line_one[1]]
                        line_next_all.append(line_next_new)
                elif line_one[1][0] == start_x0 and line_one[1][0] == start_x1:
                    if min(start_y0, start_y1) < line_one[1][1] < max(start_y0, start_y1):
                        line_next_new = [line_one[1], line_one[0]]
                        line_next_all.append(line_next_new)
                elif line_one[1][1] == start_y0 and line_one[1][1] == start_y1:
                    if min(start_x0, start_x1) < line_one[1][0] < max(start_x0, start_x1):
                        line_next_new = [line_one[1], line_one[0]]
                        line_next_all.append(line_next_new)
        # 后续线段 单选
        if len(line_next_all) == 1:
            line_next = line_next_all[0]
        # 后续线段 多选
        elif len(line_next_all) > 1 and len(line_next) > 0:
            x1, y1, x2, y2 = line_start[0][0], line_start[0][1], line_start[1][0], line_start[1][1]
            start_length, start_angle = compute_length_angle(x1, y1, x2, y2)
            x1, y1, x2, y2 = line_next[0][0], line_next[0][1], line_next[1][0], line_next[1][1]
            next_length, next_angle = compute_length_angle(x1, y1, x2, y2)
            delta_angle = normalize_angle(next_angle - start_angle)
            for line_next_idx in range(len(line_next_all) - 1):
                line_next_one = line_next_all[line_next_idx]
                x1, y1, x2, y2 = line_next_one[0][0], line_next_one[0][1], line_next_one[1][0], line_next_one[1][1]
                next_length_new, next_angle_new = compute_length_angle(x1, y1, x2, y2)
                delta_angle_new = normalize_angle(next_angle_new - start_angle)
                if next_length_new < 1.0:
                    continue
                if abs(abs(delta_angle_new) - math.pi) < 0.1:
                    continue
                if -0.1 < delta_angle_new < delta_angle - math.pi / 4:
                    line_next = line_next_one
                    break
                if -math.pi / 2 - 0.1 < delta_angle_new < delta_angle - math.pi / 4 and not line_next_one[0] == line_start[1]:
                    line_next = line_next_one
                    line_start[1][0] = line_next[0][0]
                    line_start[1][1] = line_next[0][1]
        # 后续线段 调整
        return line_next

    def merge_line_direction(self):
        floor_list = []
        # gradient
        line_gradient_list = []
        for line_one in self.floor_list_clockwise:
            if float(line_one[1][0] - line_one[0][0]) == 0:
                gradient = self.MAX_GRADIENT_VALUE
            else:
                temp = round(float(line_one[1][1] - line_one[0][1]) / float(line_one[1][0] - line_one[0][0]), 3)
                gradient = abs(temp)
            line_gradient_list.append(gradient)
        # gradient sliced
        gradient_sliced = []
        gradient_tmp = []
        for index, gradient in enumerate(line_gradient_list):
            if index == 0:
                gradient_tmp.append(gradient)
            if gradient not in gradient_tmp:
                gradient_sliced.append(index)
                gradient_tmp = [gradient]
        # floor list
        if len(gradient_sliced) <= 0:
            return floor_list
        floor_list.append([self.floor_list_clockwise[0][0], self.floor_list_clockwise[gradient_sliced[0] - 1][1]])
        for i, _slice in enumerate(gradient_sliced):
            if i <= 0:
                continue
            floor_list.append([self.floor_list_clockwise[gradient_sliced[i - 1]][0],
                               self.floor_list_clockwise[gradient_sliced[i] - 1][1]
                               ])
        floor_list.append([self.floor_list_clockwise[gradient_sliced[-1]][0],
                           self.floor_list_clockwise[len(self.floor_list_clockwise) - 1][1]
                           ])
        return floor_list


class DoorData(object):
    def __init__(self):
        self.door_list = []
        self.mesh_type = 'Door'

    def load_data(self, mesh_list, floor_list):
        self.door_list = []
        if len(mesh_list) <= 0:
            return False
        rect_list = []
        # mesh
        for mesh_one in mesh_list:
            mesh_xyz = mesh_one['xyz']
            x_list, y_list, z_list, xz_list = [], [], [], []
            # xz list
            for i in range(len(mesh_xyz) // 3):
                x_list.append(round(float(mesh_xyz[3 * i + 0]), 3))
                y_list.append(round(float(mesh_xyz[3 * i + 1]), 3))
                z_list.append(round(float(mesh_xyz[3 * i + 2]), 3))
                xz = [round(float(mesh_xyz[3 * i + 0]), 3), round(float(mesh_xyz[3 * i + 2]), 3)]
                xz_list.append(xz)
            # pt list
            y_set = set(y_list)
            if len(y_set) >= 2:
                continue
            if len(rect_list) <= 0:
                rect_list.append(xz_list)
            else:
                is_found = False
                for rect_one in rect_list:
                    for pt in xz_list:
                        if pt in rect_one:
                            is_found = True
                    if is_found:
                        break
                if not is_found:
                    rect_list.append(xz_list)
        # bottom list
        for rect_one in rect_list:
            # xz bottom
            if len(rect_one) > 4:
                pt_array = np.array(rect_one)
                try:
                    hull = ConvexHull(pt_array)
                    index = hull.vertices
                except Exception as e:
                    index = [0, 1, -3, -2]
                bottom_list = [rect_one[index[0]][0], rect_one[index[0]][1], rect_one[index[1]][0], rect_one[index[1]][1],
                               rect_one[index[2]][0], rect_one[index[2]][1], rect_one[index[3]][0], rect_one[index[3]][1]]
            else:
                bottom_list = [rect_one[0][0], rect_one[0][1], rect_one[1][0], rect_one[1][1],
                               rect_one[2][0], rect_one[2][1], rect_one[3][0], rect_one[3][1]]
            # xz align
            bottom_list_new = compute_point_align(bottom_list, floor_list)
            if len(bottom_list_new) > 0:
                self.door_list.append(bottom_list_new)
        # clockwise
        self.door_list = generate_point_clockwise(self.door_list)
        return True

    def load_object(self, object_list, floor_list):
        for object_one in object_list:
            # 排除
            object_pos = object_one['position']
            object_rot = object_one['rotation']
            object_has = False
            for unit_pts in self.door_list:
                unit_pos = []
                if len(unit_pts) >= 8:
                    unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                                (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                elif len(unit_pts) >= 2:
                    unit_pos = [unit_pts[0], unit_pts[1]]
                if len(unit_pos) >= 2:
                    x1, y1 = unit_pos[0], unit_pos[1]
                    x2, y2 = object_pos[0], object_pos[2]
                    if compute_length(x1, y1, x2, y2) <= 0.5:
                        object_has = True
                        break
            if object_has:
                continue
            # 计算
            object_size = [object_one['size'][i] * object_one['scale'][i] / 100 for i in range(3)]
            bottom_list = compute_bound(object_size, object_pos, object_rot)
            bottom_line = compute_coincide_list(bottom_list, floor_list)
            if bottom_line:
                self.door_list.append(bottom_list)


class HoleData(object):
    def __init__(self):
        self.hole_list = []
        self.mesh_type = 'Hole'
        self.THRESHOLD = 0.5

    def load_data(self, mesh_list, floor_list):
        self.hole_list = []
        if len(mesh_list) <= 0:
            return False
        rect_list = []
        # mesh
        for mesh_one in mesh_list:
            mesh_xyz = mesh_one['xyz']
            x_list, y_list, z_list, xz_list, bottom_list = [], [], [], [], []
            # y_sum
            y_sum = 0
            for i in range(len(mesh_xyz) // 3):
                y_sum += float(mesh_xyz[3 * i + 1])
            if y_sum > self.THRESHOLD:
                continue
            # xz list
            for i in range(len(mesh_xyz) // 3):
                x_list.append(round(float(mesh_xyz[3 * i + 0]), 3))
                y_list.append(round(float(mesh_xyz[3 * i + 1]), 3))
                z_list.append(round(float(mesh_xyz[3 * i + 2]), 3))
                xz = [round(float(mesh_xyz[3 * i + 0]), 3), round(float(mesh_xyz[3 * i + 2]), 3)]
                xz_list.append(xz)
            # pt list
            y_set = set(y_list)
            if len(y_set) >= 2:
                continue
            if len(rect_list) <= 0:
                rect_list.append(xz_list)
            else:
                is_found = False
                for rect_one in rect_list:
                    for pt in xz_list:
                        if pt in rect_one:
                            is_found = True
                    if is_found:
                        break
                if not is_found:
                    rect_list.append(xz_list)
            # # bottom list
            # for i in range(len(x_list)):
            #     bottom_list.append(x_list[i])
            #     bottom_list.append(z_list[i])
            # x_set, z_set = set(x_list), set(z_list)
            # if len(x_set) == 1 and len(z_set) == 1:
            #     x_list, z_list, bottom_list = [], [], []
            #     for i in range(len(mesh_xyz) // 3):
            #         x_list.append(round(float(mesh_xyz[3 * i + 0]), 2))
            #         z_list.append(round(float(mesh_xyz[3 * i + 2]), 2))
            #         bottom_list.append(round(float(mesh_xyz[3 * i + 0]), 2))
            #         bottom_list.append(round(float(mesh_xyz[3 * i + 2]), 2))
            # if len(bottom_list) <= 0:
            #     return False
            # # xz align
            # bottom_list_new = compute_point_align(bottom_list, floor_list)
            # self.hole_list.append(bottom_list_new)
            pass
        # bottom list
        for rect_one in rect_list:
            # xz bottom
            if len(rect_one) > 4:
                pt_array = np.array(rect_one)
                try:
                    hull = ConvexHull(pt_array)
                    index = hull.vertices
                except Exception as e:
                    index = [0, 1, -3, -2]
                bottom_list = [rect_one[index[0]][0], rect_one[index[0]][1], rect_one[index[1]][0], rect_one[index[1]][1],
                               rect_one[index[2]][0], rect_one[index[2]][1], rect_one[index[3]][0], rect_one[index[3]][1]]
            else:
                bottom_list = [rect_one[0][0], rect_one[0][1], rect_one[1][0], rect_one[1][1],
                               rect_one[2][0], rect_one[2][1], rect_one[3][0], rect_one[3][1]]
            # xz align
            bottom_list_new = compute_point_align(bottom_list, floor_list)
            self.hole_list.append(bottom_list_new)
        # clockwise
        self.hole_list = generate_point_clockwise(self.hole_list)
        return True

    def load_object(self, object_list, floor_list):
        for object_one in object_list:
            # 排除
            object_pos = object_one['position']
            object_rot = object_one['rotation']
            object_has = False
            for unit_pts in self.hole_list:
                unit_pos = []
                if len(unit_pts) >= 8:
                    unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                                (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                elif len(unit_pts) >= 2:
                    unit_pos = [unit_pts[0], unit_pts[1]]
                if len(unit_pos) >= 2:
                    x1, y1 = unit_pos[0], unit_pos[1]
                    x2, y2 = object_pos[0], object_pos[2]
                    if compute_length(x1, y1, x2, y2) <= 0.5:
                        object_has = True
                        break
            if object_has:
                continue
            # 计算
            object_size = [object_one['size'][i] * object_one['scale'][i] / 100 for i in range(3)]
            bottom_list = compute_bound(object_size, object_pos, object_rot)
            bottom_line = compute_coincide_list(bottom_list, floor_list)
            if bottom_line:
                self.hole_list.append(bottom_list)


class WindowData(object):
    def __init__(self):
        self.window_list = []
        self.window_list_height = []
        self.mesh_type = 'Window'

    def load_data(self, mesh_list, floor_list):
        self.window_list = []
        self.window_list_height = []
        if len(mesh_list) <= 0:
            return False
        for mesh_one in mesh_list:
            mesh_xyz = mesh_one['xyz']
            mesh_faces = mesh_one['faces']
            x_list, y_list, z_list = [], [], []
            for i in range(len(mesh_xyz) // 3):
                x_list.append(round(float(mesh_xyz[3 * i + 0]), 3))
                y_list.append(round(float(mesh_xyz[3 * i + 1]), 3))
                z_list.append(round(float(mesh_xyz[3 * i + 2]), 3))
            if min(y_list) >= 1.5:
                continue
            # max min
            max_x, min_x, max_z, min_z = max(x_list), min(x_list), max(z_list), min(z_list)
            x_set, z_set = set(x_list), set(z_list)
            # orthogonal
            if len(x_set) == 2 and len(z_set) == 2:
                coordinates = [max_x, max_z, max_x, min_z, min_x, min_z, min_x, max_z]
                coordinates_new = compute_point_align(coordinates, floor_list)
                self.window_list.append(coordinates_new)
                self.window_list_height.append(min(y_list))
            elif len(x_set) == 4 and len(z_set) == 2:
                coordinates = [max_x, max_z, max_x, min_z, min_x, min_z, min_x, max_z]
                coordinates_new = compute_point_align(coordinates, floor_list)
                self.window_list.append(coordinates_new)
                self.window_list_height.append(min(y_list))
            elif len(x_set) == 2 and len(z_set) == 4:
                coordinates = [max_x, max_z, max_x, min_z, min_x, min_z, min_x, max_z]
                coordinates_new = compute_point_align(coordinates, floor_list)
                self.window_list.append(coordinates_new)
                self.window_list_height.append(min(y_list))
            elif len(x_set) == 4 and len(z_set) == 4:
                x_set_new = heapq.nlargest(4, x_set)
                index_0 = x_list.index(x_set_new[0])
                index_1 = x_list.index(x_set_new[1])
                index_2 = x_list.index(x_set_new[2])
                index_3 = x_list.index(x_set_new[3])
                coordinates = [x_list[index_0], z_list[index_0],
                               x_list[index_1], z_list[index_1],
                               x_list[index_3], z_list[index_3],
                               x_list[index_2], z_list[index_2]]
                coordinates_new = compute_point_align(coordinates, floor_list)
                self.window_list.append(coordinates_new)
                self.window_list_height.append(min(y_list))
            else:
                continue
        self.window_list = generate_point_clockwise(self.window_list)
        return True

    def load_object(self, object_list, floor_list):
        for object_one in object_list:
            # 排除
            object_pos = object_one['position']
            object_rot = object_one['rotation']
            object_has = False
            for unit_pts in self.window_list:
                unit_pos = []
                if len(unit_pts) >= 8:
                    unit_pos = [(unit_pts[0] + unit_pts[2] + unit_pts[4] + unit_pts[6]) / 4,
                                (unit_pts[1] + unit_pts[3] + unit_pts[5] + unit_pts[7]) / 4]
                elif len(unit_pts) >= 2:
                    unit_pos = [unit_pts[0], unit_pts[1]]
                if len(unit_pos) >= 2:
                    x1, y1 = unit_pos[0], unit_pos[1]
                    x2, y2 = object_pos[0], object_pos[2]
                    if compute_length(x1, y1, x2, y2) <= 0.5:
                        object_has = True
                        break
            if object_has:
                continue
            # 计算
            object_size = [object_one['size'][i] * object_one['scale'][i] / 100 for i in range(3)]
            bottom_list = compute_bound(object_size, object_pos, object_rot)
            bottom_line = compute_coincide_list(bottom_list, floor_list)
            if bottom_line:
                window_height = 2.4 - object_size[1]
                if window_height < 0:
                    window_height = 0
                self.window_list.append(bottom_list)
                self.window_list_height.append(window_height)


class BaywindowData(object):
    def __init__(self):
        self.baywindow_list = []
        self.baywindow_list_height = []
        self.point_clockwise = []
        self.mesh_type = 'Baywindow'

    def load_data(self, mesh_list, floor_list):
        self.baywindow_list = []
        self.baywindow_list_height = []
        if len(mesh_list) <= 0:
            return False
        x_list = []
        y_list = []
        z_list = []
        for mesh_one in mesh_list:
            mesh_xyz = mesh_one['xyz']
            mesh_faces = mesh_one['faces']
            for i in range(len(mesh_xyz) // 3):
                x_list.append(round(float(mesh_xyz[3 * i + 0]), 3))
                y_list.append(round(float(mesh_xyz[3 * i + 1]), 3))
                z_list.append(round(float(mesh_xyz[3 * i + 2]), 3))
        # TODO: baywindow data
        return True


# 默认门
DEFAULT_DOOR_DICT = {
    "923ebf68-e6c9-4a48-a23a-52b15806532c": {
        "style": "Contemporary",
        "type": "door/entry/single swing door",
        "size": [
            79.80000305175781,
            201.39999389648438,
            11.674099922180176
        ],
        "type_id": "85534f68-a899-4662-927d-20efefc9cb6f",
        "style_id": "19b9974d-363d-47df-81b5-81893d48a813"
    },
    "edb0357d-8414-4094-8db1-5c6a3a406c3d": {
        "style": "Contemporary",
        "type": "door/single swing door",
        "size": [
            80.5,
            210.0,
            16.44409942626953
        ],
        "type_id": "2a7d8c37-31a8-4c46-b7d1-f980681c1c1c",
        "style_id": "19b9974d-363d-47df-81b5-81893d48a813"
    },
    "cc16b9fe-102b-4bcb-9414-deafd6613b79": {
        "style": "Contemporary",
        "type": "door/single swing door",
        "size": [
            75.87039947509766,
            201.93800354003906,
            18.156099319458008
        ],
        "type_id": "2a7d8c37-31a8-4c46-b7d1-f980681c1c1c",
        "style_id": "19b9974d-363d-47df-81b5-81893d48a813"
    }
}
# 默认洞
DEFAULT_HOLE_DICT = {

}
# 默认窗
DEFAULT_WINDOW_DICT = {

}