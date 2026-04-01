import math
import copy
import random

import oss2
import json
import time
import numpy as np
import matplotlib.pyplot as plt
import requests
from shapely.geometry.polygon import Polygon


def gen_random_str(num):
    return ''.join(random.sample('zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHQFEDCBA0123456789', num))


def check_on_line(pt, line):
    p1, p2 = line
    if np.linalg.norm(np.array(p1) - np.array(p2)) < 1e-3:
        if np.linalg.norm(np.array(p1) - np.array(pt)) < 1e-3:
            return True
        else:
            return False
    pf = pt
    cross = (p2[0] - p1[0]) * (pf[0] - p1[0]) + (p2[1] - p1[1]) * (pf[1] - p1[1])
    if cross < 0:
        return False
    d2 = (p2[0] - p1[0]) * (p2[0] - p1[0]) + (p2[1] - p1[1]) * (p2[1] - p1[1])
    if cross > d2:
        return False
    r = cross / d2
    px = p1[0] + (p2[0] - p1[0]) * r
    py = p1[1] + (p2[1] - p1[1]) * r
    return ((pf[0] - px) * (pf[0] - px) + (py - pf[1]) * (py - pf[1])) <= 0.01


def check_anti(room_info):
    out_pts = []
    floor_pts = room_info['floor']
    for i in range(len(floor_pts) // 2 - 1):
        out_pts.append([floor_pts[2 * i], floor_pts[2 * i + 1]])
    convex_p_idx = np.argmax(np.array(out_pts), axis=0)[0]
    convex_prev_idx = (convex_p_idx - 1) % len(out_pts)
    convex_next_idx = (convex_p_idx + 1) % len(out_pts)
    x1 = out_pts[convex_prev_idx][0]
    y1 = out_pts[convex_prev_idx][1]
    x2 = out_pts[convex_p_idx][0]
    y2 = out_pts[convex_p_idx][1]
    x3 = out_pts[convex_next_idx][0]
    y3 = out_pts[convex_next_idx][1]
    if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) < 0:
        return room_info
    else:
        new_out_pts = []
        out_pts.reverse()
        for i in out_pts:
            new_out_pts.append(i[0])
            new_out_pts.append(i[1])
        new_out_pts.append(new_out_pts[0])
        new_out_pts.append(new_out_pts[1])
        room_info['floor'] = new_out_pts
        return room_info


def get_http_data_from_url(src_url, timeout=1):
    try:
        r = requests.get(src_url, timeout=timeout)
        r.raise_for_status()
    except Exception as e:
        print('http request error:', e)
        return ''
    return json.loads(r.content.decode('utf-8'))


ACCESS_ID = ''
ACCESS_SECRET = ''
ACCESS_ENDPOINT = 'http://oss-cn-hangzhou.aliyuncs.com'

ROOM_CVT_TABLE = {
    'LivingDiningRoom': 'LivingDiningRoom',
    'LivingRoom': 'LivingDiningRoom',
    'DiningRoom': 'LivingDiningRoom',

    'MasterBedroom': 'MasterBedroom',
    'SecondBedroom': 'MasterBedroom',
    'Bedroom': 'MasterBedroom',
    'KidsRoom': 'MasterBedroom',
    'ElderlyRoom': 'MasterBedroom',
    'NannyRoom': 'MasterBedroom',

    'Kitchen': 'Kitchen',

    'MasterBathroom': 'Bathroom',
    'SecondBathroom': 'Bathroom',
    'Bathroom': 'Bathroom',

    'Library': 'Library',
    'Lounge': 'Library',
    'Balcony': 'Balcony',
    'Terrace': 'Balcony',
    'Hallway': 'LivingDiningRoom',
    'Aisle': 'LivingDiningRoom',
    'Corridor': 'LivingDiningRoom',
    'Stairwell': 'LivingDiningRoom',

    'StorageRoom': 'Other',
    'CloakRoom': 'Other',
    'EquipmentRoom': 'Other',
    'LaundryRoom': 'Other',
    'Auditorium': 'Other',
    'Other': 'Other',
    'Courtyard': '',
    'Garage': '',
    'OtherRoom': 'Other',
    'none': 'Other',
    '': '',
    'undefined': 'Other'
}


def compute_dis(input_p, p_list):
    if len(p_list) == 0:
        return 100
    for p in p_list:
        dis = (input_p[0] - p[0]) ** 2 + (input_p[1] - p[1]) ** 2
        if dis < 1e-5:
            return 0.
        else:
            continue
    return 100.


def compute_p_dis(input_p, target_p):
    dis = (input_p[0] - target_p[0]) ** 2 + (input_p[1] - target_p[1]) ** 2
    return math.sqrt(dis)


def oss_upload_json(object_name, json_object, bucket_name='', access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    bucket.put_object(object_name, json.dumps(json_object))


def oss_upload_byte(object_name, json_file_txt, bucket_name='', access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    bucket.put_object(object_name, json_file_txt)


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


def combine_living_rooms(result):
    house_input_json = result['room']
    living_list = []
    for room in house_input_json:
        if room['type'] in ['LivingDiningRoom', 'LivingRoom', 'Hallway', 'Aisle']:
            living_list.append([room['area'], room])

    need_del = []
    if len(living_list) > 1:
        base_room = sorted(living_list, key=lambda x: x[0], reverse=True)[0][1]

        for room in living_list:
            if room[1]['id'] == base_room['id']:
                continue
            target_room = room[1]

            done = False
            for base_i in range(0, len(base_room['floor']) // 2 - 1, 1):
                if done:
                    break
                for target_i in range(0, len(target_room['floor']) // 2 - 1, 1):
                    line_start = [base_room['floor'][2 * base_i + 0], base_room['floor'][2 * base_i + 1]]
                    line_end = [base_room['floor'][2 * base_i + 2], base_room['floor'][2 * base_i + 3]]
                    pt_1 = [target_room['floor'][2 * target_i + 0], target_room['floor'][2 * target_i + 1]]
                    pt_2 = [target_room['floor'][2 * target_i + 2], target_room['floor'][2 * target_i + 3]]

                    if pt_in_line(pt_1, [line_start, line_end]) and pt_in_line(pt_2, [line_start, line_end]):
                        new_pts = []
                        if compute_p_dis(line_start, pt_1) < compute_p_dis(line_start, pt_2):
                            near_idx = target_i
                        else:
                            near_idx = target_i + 1

                        new_floor = target_room['floor'][:-2]
                        for i in range(len(new_floor) // 2):
                            temp_pts_idx = (near_idx + i) % (len(target_room['floor']) // 2 - 1)
                            new_pts.append(new_floor[2 * temp_pts_idx + 0])
                            new_pts.append(new_floor[2 * temp_pts_idx + 1])

                        base_room['floor'][base_i * 2 + 2:base_i * 2 + 2] = new_pts
                        base_room['door_info'] += target_room['door_info']
                        base_room['window_info'] += target_room['window_info']
                        base_room['type'] = "LivingDiningRoom"
                        done = True
                        break
            if done:
                need_del.append(target_room['id'])

    for i in range(len(house_input_json) - 1, -1, -1):
        if house_input_json[i]['id'] in need_del:
            house_input_json.pop(i)


# 户型图识别后处理
def layout_refine_rooms(result):
    house_input_json = result['room']

    all_room_area = []
    for i in range(len(house_input_json)):
        all_room_area.append([house_input_json[i]['area'], i])

    # 规范化所有id与type名称
    id_change_table = {}
    room_index = 0
    for room in house_input_json:
        room_index += 1
        now_room = room['id']
        now_type, _ = now_room.split('-')
        if now_room in id_change_table:
            room['id'] = id_change_table[now_room]
        else:
            if room['type'] == 'kitchen':
                room['type'] = 'Kitchen'
            if room['type'] == 'library':
                room['type'] = 'Library'
            if room['type'] == 'balcony':
                room['type'] = 'Balcony'
            if room['type'] in ['bedRoom', 'bedroom']:
                room['type'] = 'MasterBedroom'
                if room['area'] < 7.:
                    room['type'] = 'Library'
            if room['type'] in ['livingRoom', 'living_room']:
                # room['type'] = 'LivingRoom'
                room['type'] = 'LivingDiningRoom'
            if room['type'] == 'bathroom':
                room['type'] = 'Bathroom'
            # other改完书房
            if room['type'] == 'other':
                room['type'] = 'MasterBedroom'
            if room['type'] == 'restroom':
                room['type'] = 'Bathroom'
            room['id'] = room['type'] + '-' + str(room_index)
            id_change_table[now_room] = room['id']

    # 更新门窗信息
    for room in house_input_json:
        if 'door_info' in room:
            for door in room['door_info']:
                if door['to'] in id_change_table:
                    door['to'] = id_change_table[door['to']]
        else:
            room['door_info'] = []

        if 'window_info' in room:
            for window in room['window_info']:
                if window['to'] in id_change_table:
                    window['to'] = id_change_table[window['to']]
        else:
            room['window_info'] = []

        if 'baywindow_info' in room and len(room['baywindow_info'][0]['pts']) > 0:
            for baywindow in room['baywindow_info']:
                if baywindow['to'] in id_change_table:
                    baywindow['to'] = id_change_table[baywindow['to']]
        else:
            room['baywindow_info'] = []

        if 'hole_info' in room:
            for hole in room['hole_info']:
                if hole['to'] in id_change_table:
                    hole['to'] = id_change_table[hole['to']]
        else:
            room['hole_info'] = []

    # 去掉不符合要求的房间 floor点的更新
    house_list = []
    for idx in range(len(all_room_area)):
        room_idx = all_room_area[idx][1]
        # if house_input_json[room_idx]['area'] < 1.5:
        #     continue
        # if house_input_json[room_idx]['area'] < 5.0 and house_input_json[room_idx]['type'] == 'Library':
        #     continue
        now_room_input = copy.deepcopy(house_input_json[room_idx])
        # if not now_room_input['type'] in ['MasterBedroom', 'LivingDiningRoom', 'DiningRoom', 'LivingRoom', 'Balcony',
        #                                   'Kitchen', 'Bathroom', 'Library']:
        #     continue
        house_list.append(now_room_input)

    return {'room': house_list, 'id': ''}


# 户型图识别 对输出结果的优化并上传结果(包括点去重、去掉共边点，房间类型纠错，内点建墙)
# 户型图识别 对输出结果的优化并上传结果(包括点去重、去掉共边点，房间类型纠错，内点建墙)
def get_refine_rooms(result):
    if "room" not in result:
        return

    house_input_json = result['room']

    for room in house_input_json:
        if 'door_info' in room:
            pass
        else:
            room['door_info'] = []

        if 'window_info' in room:
            pass
        else:
            room['window_info'] = []

        if 'baywindow_info' in room:
            pass
        else:
            room['baywindow_info'] = []

        if 'hole_info' in room:
            pass
        else:
            room['hole_info'] = []

    # 去掉不符合要求的房间 floor点的更新
    house_list = []
    for room_idx in range(len(house_input_json)):
        if house_input_json[room_idx]['area'] < 0.2:
            continue
        now_room_input = copy.deepcopy(house_input_json[room_idx])

        # 做两次、平滑、去掉共线点
        for _ in range(3):
            origin_floor = now_room_input['floor']

            refined_pts = []
            out_floor = []

            for i in range(0, len(origin_floor) // 2, 1):
                ori_x = origin_floor[2 * i]
                ori_y = origin_floor[2 * i + 1]
                if compute_dis([ori_x, ori_y], refined_pts) < 1e-5:
                    continue
                else:
                    if len(out_floor) > 0:
                        if abs(ori_x - out_floor[0]) < abs(ori_y - out_floor[1]):
                            if abs(ori_x - out_floor[0]) < 0.121:
                                ori_x = out_floor[0]
                        else:
                            if abs(ori_y - out_floor[1]) < 0.121:
                                ori_y = out_floor[1]
                    refined_pts.append([ori_x, ori_y])
                    out_floor.insert(0, ori_x)
                    out_floor.insert(1, ori_y)
            ori_x = out_floor[-2]
            ori_y = out_floor[-1]
            need_flag = False
            if abs(ori_x - out_floor[0]) < abs(ori_y - out_floor[1]):
                if 0.001 < abs(ori_x - out_floor[0]) < 0.13:
                    ori_x = out_floor[0]
                    need_flag = True
            else:
                if 0.001 < abs(ori_y - out_floor[1]) < 0.1:
                    ori_y = out_floor[1]
                    need_flag = True

            if need_flag:
                out_floor.append(ori_x)
                out_floor.append(ori_y)
            out_floor.append(out_floor[0])
            out_floor.append(out_floor[1])
            refined_out_floor_pts = [out_floor[0], out_floor[1]]

            for i in range(1, len(out_floor) // 2 - 1):
                now_pt = out_floor[2 * i:2 * i + 2]
                next_pt = out_floor[2 * i + 2:2 * i + 4]
                prev_base_idx = (2 * i - 2) % len(out_floor)
                prev_pt = out_floor[prev_base_idx:prev_base_idx + 2]
                if abs(now_pt[0] - next_pt[0]) < 0.001 and abs(now_pt[0] - prev_pt[0]) < 0.001:
                    continue
                if abs(now_pt[1] - next_pt[1]) < 0.001 and abs(now_pt[1] - prev_pt[1]) < 0.001:
                    continue
                refined_out_floor_pts += now_pt

            now_pt = refined_out_floor_pts[0:2]
            next_pt = refined_out_floor_pts[2:4]
            prev_pt = refined_out_floor_pts[-2:]

            if len(refined_out_floor_pts) < 6:
                continue

            if abs(now_pt[0] - next_pt[0]) < 0.00001 and abs(now_pt[0] - prev_pt[0]) < 0.00001:
                refined_out_floor_pts[:2] = []
            elif abs(now_pt[1] - next_pt[1]) < 0.00001 and abs(now_pt[1] - prev_pt[1]) < 0.00001:
                refined_out_floor_pts[:2] = []

            refined_out_floor_pts += [refined_out_floor_pts[0], refined_out_floor_pts[1]]
            reorder_pts = []
            for i in range(len(refined_out_floor_pts) // 2):
                reorder_pts.insert(0, refined_out_floor_pts[2 * i])
                reorder_pts.insert(1, refined_out_floor_pts[2 * i + 1])
            now_room_input['floor'] = reorder_pts

        for window in now_room_input['window_info']:
            if "height" not in window:
                window['height'] = 0.6
        for window in now_room_input['baywindow_info']:
            if "height" not in window:
                window['height'] = 0.6

        check_anti(now_room_input)
        house_list.append(now_room_input)

    result['room'] = house_list
    return result


def update_unit_pts(unit_pts, near_pts, offset_list):
    unit_pts[0] = near_pts[0][0] + offset_list[0]
    unit_pts[1] = near_pts[0][1] + offset_list[1]

    unit_pts[2] = near_pts[1][0] + offset_list[0]
    unit_pts[3] = near_pts[1][1] + offset_list[1]

    unit_pts[4] = near_pts[1][0] - offset_list[0]
    unit_pts[5] = near_pts[1][1] - offset_list[1]

    unit_pts[6] = near_pts[0][0] - offset_list[0]
    unit_pts[7] = near_pts[0][1] - offset_list[1]


def find_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    a = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(a) < 0.01:
        return []

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
            (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
            (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    return [px, py]


def get_single_wall_fix_line_intersection(input_line, base_line_list, start_idx, next_idx):
    if next_idx > start_idx:
        start_p = base_line_list[start_idx]
        end_p = base_line_list[(next_idx) % len(base_line_list)]
    else:
        end_p = base_line_list[start_idx]
        start_p = base_line_list[(next_idx) % len(base_line_list)]

    in_line_start = input_line[0]
    in_line_end = input_line[1]

    new_pt = find_intersection(in_line_start[0], in_line_start[1], in_line_end[0], in_line_end[1],
                               start_p[0], start_p[1], end_p[0], end_p[1])
    if len(new_pt) > 0:
        s = [(in_line_start[i]-new_pt[i])**2 for i in range(len(in_line_start))]
        if sum(s) < 0.1:
            return new_pt
    return None


def fix_line_intersection(input_line, base_line_list, start_idx, circle=True):
    start_p = base_line_list[start_idx]
    end_p = base_line_list[(start_idx + 1) % len(base_line_list)]
    end_next_p = base_line_list[(start_idx + 2) % len(base_line_list)]
    prev_p = base_line_list[(start_idx - 1) % len(base_line_list)]

    in_line_start = input_line[0]
    in_line_end = input_line[1]

    if circle or start_idx > 0:

        new_pt = find_intersection(in_line_start[0], in_line_start[1], in_line_end[0], in_line_end[1],
                                   prev_p[0], prev_p[1], start_p[0], start_p[1])
        if len(new_pt) > 0:
            base_line_list[start_idx] = new_pt
        else:
            base_line_list[start_idx] = input_line[0]

    if circle or start_idx + 2 <= len(base_line_list):
        new_pt = find_intersection(in_line_start[0], in_line_start[1], in_line_end[0], in_line_end[1], end_p[0],
                                   end_p[1], end_next_p[0], end_next_p[1])
        if len(new_pt) > 0:
            base_line_list[(start_idx + 1) % len(base_line_list)] = new_pt
        else:
            base_line_list[(start_idx + 1) % len(base_line_list)] = input_line[1]


def is_coincident_line(base_line, rect_line):
    base_line = [[round(base_line[0][0], 3), round(base_line[0][1], 3)],
                 [round(base_line[1][0], 3), round(base_line[1][1], 3)]]
    rect_line = [[round(rect_line[0][0], 3), round(rect_line[0][1], 3)],
                 [round(rect_line[1][0], 3), round(rect_line[1][1], 3)]]
    base_vec = np.array(base_line[1]) - base_line[0]
    rect_vec = np.array(rect_line[1]) - rect_line[0]
    if np.linalg.norm(rect_vec) < 1e-3:
        return False, [base_line], []
    if np.linalg.norm(base_vec) < 1e-3:
        return False, [], []
    cross_vec_1 = np.array(rect_line[1]) - base_line[0]
    cross_vec_2 = np.array(rect_line[1]) - base_line[1]
    cross_vec = cross_vec_1 if np.linalg.norm(cross_vec_1) > np.linalg.norm(cross_vec_2) else cross_vec_2
    if abs(np.cross(rect_vec, base_vec)) / np.linalg.norm(base_vec) / np.linalg.norm(rect_vec) < 1e-3 and \
            abs(np.cross(cross_vec, base_vec)) / np.linalg.norm(base_vec) < 1e-2:
        if np.dot(base_vec, rect_vec) < 0:
            rect_line = np.array([rect_line[1], rect_line[0]])
        base_vec_length = np.linalg.norm(base_vec)
        rect_start_vec = np.array(rect_line[0]) - base_line[0]
        start_project_length = np.dot(rect_start_vec, base_vec) / base_vec_length / base_vec_length

        rect_end_vec = np.array(rect_line[1]) - base_line[0]
        end_project_length = np.dot(rect_end_vec, base_vec) / base_vec_length / base_vec_length

        if (start_project_length <= 1e-3 and end_project_length <= 1e-3) or (start_project_length > 1. - 1e-3 and end_project_length > 1. - 1e-3):
            return False, [base_line], []
        elif start_project_length <= 1e-3 < end_project_length < 1. - 1e-3:
            # fix by lizuojun 2020.05.31
            val_1 = end_project_length * base_vec + np.array(base_line[0])
            val_2 = end_project_length * base_vec + np.array(base_line[0])
            # rm_edge = [base_line[0], end_project_length * base_vec + np.array(base_line[0])]
            # remained_edge = [[end_project_length * base_vec + np.array(base_line[0]), base_line[1]]]
            rm_edge = [base_line[0], val_1.tolist()]
            remained_edge = [[val_2.tolist(), base_line[1]]]
            return True, remained_edge, rm_edge
        elif 1e-3 < start_project_length < 1. - 1e-3 <= end_project_length:
            # fix by lizuojun 2020.05.31
            val_1 = start_project_length * base_vec + np.array(base_line[0])
            val_2 = start_project_length * base_vec + np.array(base_line[0])
            # rm_edge = [start_project_length * base_vec + np.array(base_line[0]), base_line[1]]
            # remained_edge = [[base_line[0], start_project_length * base_vec + np.array(base_line[0])]]
            rm_edge = [val_1.tolist(), base_line[1]]
            remained_edge = [[base_line[0], val_2.tolist()]]
            return True, remained_edge, rm_edge
        elif start_project_length <= 1e-3 and end_project_length >= 1.0 - 1e-3:
            return True, [], base_line
        else:
            # fix by lizuojun 2020.05.31
            val_1 = start_project_length * base_vec + np.array(base_line[0])
            val_2 = end_project_length * base_vec + np.array(base_line[0])
            val_3 = start_project_length * base_vec + np.array(base_line[0])
            val_4 = end_project_length * base_vec + np.array(base_line[0])
            return True, [[base_line[0], val_1.tolist()], [val_2.tolist(), base_line[1]]], [val_3.tolist(), val_4.tolist()]
            # return True, [[base_line[0], start_project_length * base_vec + np.array(base_line[0])],
            #               [end_project_length * base_vec + np.array(base_line[0]), base_line[1]]], \
            #        [start_project_length * base_vec + np.array(base_line[0]),
            #         end_project_length * base_vec + np.array(base_line[0])]
    else:
        return False, [base_line], []


def update_offset(room_info, offset=0.12):
    # 去掉共线点

    floor_pts = []
    origin_room_floor = room_info['floor']
    for pts_idx in range(len(origin_room_floor) // 2):
        floor_pts.append([origin_room_floor[2 * pts_idx], origin_room_floor[2 * pts_idx + 1]])

    convex_floor_pts = convex_p_find(floor_pts[:-1])

    new_floor_pts = copy.deepcopy(floor_pts[:-1])
    old_floor_pts = copy.deepcopy(floor_pts[:-1])
    # 遍历每条边，更新上面的门窗墙
    new_door_info_list = copy.deepcopy(room_info['door_info'])
    new_window_info_list = copy.deepcopy(room_info['window_info'])
    new_hole_info_list = copy.deepcopy(room_info['hole_info'])

    for start_idx in range(0, len(old_floor_pts)):
        a_pt = old_floor_pts[start_idx]
        b_pt = old_floor_pts[(start_idx + 1) % len(old_floor_pts)]

        start_p = old_floor_pts[start_idx]
        end_p = old_floor_pts[(start_idx + 1) % len(old_floor_pts)]
        prev_p = old_floor_pts[(start_idx - 1) % len(old_floor_pts)]

        normal = compute_line_face_normal(start_p, end_p, prev_p, convex_floor_pts[start_idx])
        offset_list = [normal[0] * offset, normal[1] * offset]

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

    room_info['floor'] = []
    for pts in new_floor_pts:
        room_info['floor'] += pts
    room_info['floor'] += [new_floor_pts[0][0], new_floor_pts[0][1]]
    room_info['door_info'] = new_door_info_list
    room_info['window_info'] = new_window_info_list
    room_info['hole_info'] = new_hole_info_list

    return room_info


def find_pt_in_line(pts, line):
    pts = np.array(pts).reshape(-1, 2)
    # 水平线
    if abs(line[0][0] - line[1][0]) < abs(line[0][1] - line[1][1]):
        if abs(line[0][0] - line[1][0]) > 0.01:
            return []
        mid_p = 0.25 * (pts[0][1] + pts[1][1] + pts[2][1] + pts[3][1])
        mid_p_base = 0.25 * (pts[0][0] + pts[1][0] + pts[2][0] + pts[3][0])
        line_base = line[0][0]
        l = 0.5 * max(abs(pts[0][1] - pts[1][1]), abs(pts[1][1] - pts[2][1]))
        out_p = [[line[0][0], mid_p - l * 0.95], [line[0][0], mid_p + l * 0.95]]
        max_p = max(line[0][1], line[1][1])
        min_p = min(line[0][1], line[1][1])
        if line[0][1] > line[1][1]:
            out_p.reverse()
    else:
        if abs(line[0][1] - line[1][1]) > 0.01:
            return []
        mid_p = 0.25 * (pts[0][0] + pts[1][0] + pts[2][0] + pts[3][0])
        mid_p_base = 0.25 * (pts[0][1] + pts[1][1] + pts[2][1] + pts[3][1])
        line_base = line[1][1]
        l = 0.5 * max(abs(pts[0][0] - pts[1][0]), abs(pts[1][0] - pts[2][0]))
        out_p = [[mid_p - l * 0.95, line[1][1]], [mid_p + l * 0.95, line[1][1]]]
        max_p = max(line[0][0], line[1][0])
        min_p = min(line[0][0], line[1][0])
        if line[0][0] > line[1][0]:
            out_p.reverse()
    if abs(mid_p_base - line_base) > 0.2:
        return []
    if (mid_p - l) < min_p or (mid_p + l) > max_p:
        return []
    return out_p


def pt_in_line(pt, line):
    if abs(line[0][0] - line[1][0]) < 0.01:
        if abs(line[0][0] - pt[0]) < 0.01 and min(line[0][1], line[1][1]) <= pt[1] <= max(line[0][1], line[1][1]):
            return True
    elif abs(line[0][1] - line[1][1]) < 0.01:
        if abs(line[0][1] - pt[1]) < 0.01 and min(line[0][0], line[1][0]) <= pt[0] <= max(line[0][0], line[1][0]):
            return True
    else:
        r_p_x = (pt[0] - line[0][0]) / (line[1][0] - line[0][0])
        r_p_y = (pt[1] - line[0][1]) / (line[1][1] - line[0][1])
        r_q_x = (pt[0] - line[0][0]) / (line[1][0] - line[0][0])
        r_q_y = (pt[1] - line[0][1]) / (line[1][1] - line[0][1])
        if abs(r_p_x - r_p_y) > 0.01 or abs(r_q_x - r_q_y) > 0.01:
            return True
    return False


def in_poly(p, a, b, c, axis):
    pa = [p[0] - a[0], p[1] - a[1], p[2] - a[2]]
    pb = [p[0] - b[0], p[1] - b[1], p[2] - b[2]]
    pc = [p[0] - c[0], p[1] - c[1], p[2] - c[2]]

    t1 = np.cross(pa, pb)
    t2 = np.cross(pb, pc)
    t3 = np.cross(pc, pa)

    is_in = (t1[axis] >= 0 and t2[axis] >= 0 and t3[axis] >= 0) or (t1[axis] <= 0 and t2[axis] <= 0 and t3[axis] <= 0)
    return is_in


# 计算多边形每个点的凹凸性, 最低点为凸顶点
def convex_p_find(floor_pts, axis=1, r=1., yz_flip=False):
    if len(floor_pts[0]) == 2:
        if yz_flip:
            temp_p = [[i[0], i[1], 0.] for i in floor_pts]
        else:
            temp_p = [[i[0], 0., i[1]] for i in floor_pts]
    else:
        temp_p = copy.deepcopy(floor_pts)
    convex_p_idx = []
    num_p = len(temp_p)
    for p in range(num_p):
        one = np.array(temp_p[p]) - np.array(temp_p[(p - 1) % num_p])
        two = np.array(temp_p[(p + 1) % num_p]) - np.array(temp_p[p])
        crossRes = np.cross(one, two)
        if crossRes[axis] * r >= 0:
            convex_p_idx.append(0)
        else:
            convex_p_idx.append(1)
    return convex_p_idx


# 计算多边形每条边朝向多边形内部的法向量, 给出当前点与前后点, 以及当前的凹凸性
# 当前点与后一点为边 计算该边向内的向量
def compute_line_face_normal(p, next, prev, convex_flag):
    n = 1.
    if not convex_flag:
        n = -1.
    p = np.array(p)
    prev = np.array(prev)
    next = np.array(next)
    normal_dir = n * (p - prev)

    line_normal = next - p
    line_normal = [-line_normal[1], line_normal[0]]

    norm = np.sqrt(line_normal[0] * line_normal[0] + line_normal[1] * line_normal[1])
    if norm < 0.001:
        return [0, 0]

    if normal_dir[0] * line_normal[0] + normal_dir[1] * line_normal[1] > 0:
        line_normal = [-line_normal[0], -line_normal[1]]
    line_normal = [-line_normal[0] / norm, -line_normal[1] / norm]
    return line_normal


def compute_poly_area(p_list):
    def compute_two_p(p0, p1, p2):
        return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])

    area = 0.
    num_p = len(p_list) // 2
    for p_idx in range(1, num_p):
        p_now = p_idx
        p_next = (p_idx + 1) % num_p
        area += (compute_two_p([p_list[0], p_list[1]],
                                  [p_list[2 * p_now], p_list[2 * p_now + 1]],
                                  [p_list[2 * p_next], p_list[2 * p_next + 1]]))
    return abs(area) * 0.5


def compute_poly_list_area(p_list):
    def compute_two_p(p0, p1, p2):
        return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])

    area = 0.
    num_p = len(p_list)
    for p_idx in range(num_p):
        p_now = p_idx
        p_next = (p_idx + 1) % num_p
        area += (compute_two_p([p_list[0][0], p_list[0][1]],
                                  [p_list[p_now][0], p_list[p_now][1]],
                                  [p_list[p_next][0], p_list[p_next][1]]))
    return abs(area) * 0.5


if __name__ == '__main__':
    import time

    all_test = {
        'room': [
            {'floor': [-3.911927, 2.940641, -3.911927, 1.717651, -2.639059, 1.717651, -2.579059, 1.777651, -3.851927,
                       3.000641, -3.911927, 2.940641, -3.911927, 2.940641]}
        ]
    }

    p_list = [-1.911927, 3.940641, -3.911927, 1.717651, -2.639059, 1.717651, -2.579059, 1.777651, -3.851927,
     3.000641, -3.911927, 1.940641, -3.911927, 2.940641]

    a = time.time()
    p = Polygon([[p_list[2 * i], p_list[2 * i + 1]] for i in range(len(p_list) // 2)])
    print(time.time() - a)

    a = time.time()
    compute_poly_area(p_list)
    print(time.time() - a)
