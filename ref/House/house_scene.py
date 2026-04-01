# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-11-10
@Description: 绘制户型、功能区域、家具数据

"""

import datetime
from House.data_oss import *
from House.house_data import *
from Extract.extract_parametric_mesh import extract_parametric_mesh_model


DATA_DIR_HOUSE = os.path.dirname(__file__) + '/temp/'
DATA_DIR_HOUSE_DATA = os.path.dirname(__file__) + '/temp/data/'
DATA_DIR_HOUSE_DESIGN = os.path.dirname(__file__) + '/temp/design/'
DATA_DIR_HOUSE_EMPTY = os.path.dirname(__file__) + '/temp/empty/'
DATA_DIR_HOUSE_SCHEME = os.path.dirname(__file__) + '/temp/scheme/'
if not os.path.exists(DATA_DIR_HOUSE):
    os.makedirs(DATA_DIR_HOUSE)
if not os.path.exists(DATA_DIR_HOUSE_DATA):
    os.makedirs(DATA_DIR_HOUSE_DATA)
if not os.path.exists(DATA_DIR_HOUSE_DESIGN):
    os.makedirs(DATA_DIR_HOUSE_DESIGN)
if not os.path.exists(DATA_DIR_HOUSE_EMPTY):
    os.makedirs(DATA_DIR_HOUSE_EMPTY)
if not os.path.exists(DATA_DIR_HOUSE_SCHEME):
    os.makedirs(DATA_DIR_HOUSE_SCHEME)

# OSS位置
DATA_OSS_DATABASE = 'ihome-alg-sample-data'
DATA_OSS_HOUSE_V1 = 'houseV1'


# 场景转换服务
SCENE_TRANSFER_UAT = 'https://1232801577699031.cn-zhangjiakou.fc.aliyuncs.com/2016-08-15/proxy/jr-prod-fc-dataservice/scenepost-api/'
SCENE_TRANSFER_PRE = 'https://1232801577699031.cn-zhangjiakou.fc.aliyuncs.com/2016-08-15/proxy/jr-prod-fc-dataservice/scenepost-api/'
SCENE_TRANSFER_PRO = 'https://1232801577699031.cn-zhangjiakou.fc.aliyuncs.com/2016-08-15/proxy/jr-prod-fc-dataservice/scenepost-api/'
# 设计转换服务 VIP
DESIGN_TRANSFER_UAT = 'http://100.88.245.100/getRoomsInfo'
DESIGN_TRANSFER_PRE = 'http://33.42.64.15:8888/getRoomsInfo'
DESIGN_TRANSFER_PRO = 'http://33.42.64.15:8888/getRoomsInfo'


# 数据地址
def house_scene_url(scene_id):
    # 服务地址
    server_env, server_url = '', SCENE_TRANSFER_UAT
    try:
        r = requests.get('http://jmenv.tbsite.net:8080/env', timeout=1)
        r.raise_for_status()
        server_env = r.text.strip()
    except Exception as e:
        print('get environment error:', e)
    if 'daily' in server_env:
        server_url = SCENE_TRANSFER_UAT
    elif 'pre' in server_env:
        server_url = SCENE_TRANSFER_PRE
    else:
        server_url = SCENE_TRANSFER_PRO
    # 场景文件
    scene_url = ''
    try:
        request_data = {
            'designId': scene_id,
            'imageIds': [],
            'aerialId': "",
            'includeTopicalCases': 0,
            'businessType': 2,
            'versionId': 'v123456'
        }
        response_info = requests.post(server_url, data=json.dumps(request_data))
        response_data = response_info.json()
        if 'data' in response_data:
            scene_url = response_data['data']
    except Exception as e:
        print('scene url error:', e)
    return scene_url


def get_refine_rooms(result):
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
    # 去掉不符合要求的房间 floor点的更新
    house_list = []
    for room_idx in range(len(house_input_json)):
        if house_input_json[room_idx]['area'] < 0.2:
            continue
        now_room_input = copy.deepcopy(house_input_json[room_idx])

        # 做两次、平滑、去掉共线点
        for _ in range(2):
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
                            if abs(ori_x - out_floor[0]) < 0.12:
                                ori_x = out_floor[0]
                        else:
                            if abs(ori_y - out_floor[1]) < 0.12:
                                ori_y = out_floor[1]
                    refined_pts.append([ori_x, ori_y])
                    out_floor.insert(0, ori_x)
                    out_floor.insert(1, ori_y)
            ori_x = out_floor[-2]
            ori_y = out_floor[-1]
            need_flag = False
            if abs(ori_x - out_floor[0]) < abs(ori_y - out_floor[1]):
                if abs(ori_x - out_floor[0]) > 0.001:
                    ori_x = out_floor[0]
                    need_flag = True
            else:
                if abs(ori_y - out_floor[1]) > 0.001:
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

            if abs(now_pt[0] - next_pt[0]) < 0.001 and abs(now_pt[0] - prev_pt[0]) < 0.001:
                refined_out_floor_pts[:2] = []
            elif abs(now_pt[1] - next_pt[1]) < 0.001 and abs(now_pt[1] - prev_pt[1]) < 0.001:
                refined_out_floor_pts[:2] = []

            refined_out_floor_pts += [refined_out_floor_pts[0], refined_out_floor_pts[1]]
            reorder_pts = []
            for i in range(len(refined_out_floor_pts) // 2):
                reorder_pts.insert(0, refined_out_floor_pts[2 * i])
                reorder_pts.insert(1, refined_out_floor_pts[2 * i + 1])
            now_room_input['floor'] = reorder_pts

        for window in now_room_input['window_info']:
            window['height'] = 0.6
        for window in now_room_input['baywindow_info']:
            window['height'] = 0.6
        check_anti(now_room_input)
        house_list.append(now_room_input)

    result['room'] = house_list
    return result


# 数据下载
def house_scene_path(scene_url, house_id='', house_id_pre='', house_dir=DATA_DIR_HOUSE_EMPTY):
    if not os.path.exists(house_dir):
        os.makedirs(house_dir)
    if len(scene_url) <= 0:
        print('scene trans error:', 'empty')
        return ''
    if os.path.exists(house_dir):
        if house_id == '':
            scene_id = scene_url.split('/')[-3]
        else:
            scene_id = house_id
        house_id = house_id_pre + scene_id
        des_path = os.path.join(house_dir, house_id + '.json')
        try:
            r = requests.get(scene_url)
            r.raise_for_status()
            with open(des_path, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            print('scene url error:', e)
            return ''
    # 整理场景
    json_path = des_path
    if os.path.exists(json_path):
        house_json = json.load(open(json_path, 'r', encoding='utf-8'))
        house_scene_clear_mesh(house_json)
        with open(json_path, "w") as f:
            json.dump(house_json, f, indent=4)
            f.close()
    return json_path


# 数据获取
def house_scene_fetch(scene_id):
    scene_url, scene_json = '', {}
    if len(scene_id) > 0:
        scene_url = house_scene_url(scene_id)
    if len(scene_url) > 0:
        try:
            r = requests.get(scene_url)
            scene_json = r.json()
            pass
        except Exception as e:
            print('scene trans error:', e)
    return scene_json


# 数据清理
def house_scene_clear_mesh(house_json, dump_type=['SlabSide', 'SlabTop', 'SlabBottom', 'LightBand']):
    # 丢弃面片
    mesh_dict_dump = {}
    mesh_list = house_json['mesh']
    mesh_count = len(mesh_list)
    for mesh_idx in range(mesh_count - 1, -1, -1):
        mesh_one = mesh_list[mesh_idx]
        mesh_uid, mesh_type, material_uid = mesh_one['uid'], mesh_one['type'], mesh_one['material']
        mesh_add = {
            'uid': mesh_uid,
            'type': mesh_type,
            'material': material_uid
        }
        if mesh_type in dump_type:
            mesh_dict_dump[mesh_uid] = mesh_add
    # 更新房间
    room_list = house_json['scene']['room']
    for room in room_list:
        children_list = room['children']
        children_count = len(children_list)
        for child_idx in range(children_count - 1, -1, -1):
            child_one = children_list[child_idx]
            child_ref = child_one['ref']
            if child_ref in mesh_dict_dump:
                children_list.pop(child_idx)


# 数据清理
def house_scene_clear_object(house_json, keep_type=[]):
    # 丢弃类型
    object_dict_dump = {}
    object_list = house_json['furniture']
    object_count = len(object_list)
    for object_idx in range(object_count - 1, -1, -1):
        object_one = object_list[object_idx]
        object_uid, object_jid, object_title = object_one['uid'], object_one['jid'], object_one['title']
        object_add = {
            'uid': object_uid,
            'jid': object_jid,
            'title': object_title
        }
        if object_title not in keep_type:
            object_dict_dump[object_uid] = object_add
    # 更新房间
    room_list = house_json['scene']['room']
    for room in room_list:
        children_list = room['children']
        children_count = len(children_list)
        for child_idx in range(children_count - 1, -1, -1):
            child_one = children_list[child_idx]
            child_ref = child_one['ref']
            if child_ref in object_dict_dump:
                children_list.pop(child_idx)
    pass


# 数据调整
def house_scene_switch_object(house_json, operate_dict):
    operate_json = {}
    # 记录物品
    object_list, object_dict = house_json['furniture'], {}
    object_count = len(object_list)
    for object_idx in range(object_count - 1, -1, -1):
        object_one = object_list[object_idx]
        object_uid, object_jid, object_title = object_one['uid'], object_one['jid'], object_one['title']
        object_dict[object_uid] = object_jid
    # 更新房间
    room_list = house_json['scene']['room']
    for room_one in room_list:
        room_key = room_one['instanceid']
        target_list, relate_list, remove_list, append_list = [], [], [], []
        children_remove, children_append, furniture_append = [], [], []
        if room_key in operate_dict:
            operate_one = operate_dict[room_key]
            if 'target' in operate_one:
                target_list = operate_one['target'][:]
            if 'relate' in operate_one:
                relate_list = operate_one['relate'][:]
            if 'remove' in operate_one:
                remove_list = operate_one['remove'][:]
            if 'append' in operate_one:
                append_list = operate_one['append'][:]
        else:
            continue
        if len(target_list) + len(relate_list) + len(remove_list) + len(append_list) <= 0:
            continue
        children_list = room_one['children']
        children_count = len(children_list)
        # 删除物品
        for child_idx in range(children_count - 1, -1, -1):
            child_one = children_list[child_idx]
            child_ref = child_one['ref']
            child_jid = ''
            if child_ref not in object_dict:
                continue
            child_jid = object_dict[child_ref]
            child_pos = child_one['pos']
            # 查找物品
            target_find, relate_find, remove_find = False, False, False
            for object_one in target_list:
                target_key, target_pos = object_one['id'], object_one['position']
                if child_jid == target_key:
                    if abs(child_pos[0] - target_pos[0]) + abs(child_pos[2] - target_pos[2]) < 0.1:
                        target_find = True
                        break
            for object_one in relate_list:
                target_key, target_pos = object_one['id'], object_one['position']
                if child_jid == target_key:
                    if abs(child_pos[0] - target_pos[0]) + abs(child_pos[2] - target_pos[2]) < 0.1:
                        target_find = True
                        break
            for object_one in remove_list:
                target_key, target_pos = object_one['id'], object_one['position']
                if child_jid == target_key:
                    if abs(child_pos[0] - target_pos[0]) + abs(child_pos[2] - target_pos[2]) < 0.1:
                        remove_find = True
                        break
            if target_find or relate_find or remove_find:
                children_list.pop(child_idx)
                children_remove.append({'ref': child_ref, 'jid': child_jid})
        # 增加物品
        for object_idx, object_one in enumerate(append_list):
            object_ref = '999%03d' % object_idx
            object_uid = '999%03d/model' % object_idx
            object_add = {
                'uid': object_uid, 'jid': object_one['id'], 'aid': [],
                'title': object_one['type'], 'type': 'standard'
            }
            child_add = {
                'ref': object_uid, 'instanceid': object_ref,
                'pos': object_one['position'], 'rot': object_one['rotation'],
                'scale': object_one['scale'],
            }
            object_list.append(object_add)
            children_list.append(child_add)
            furniture_append.append(object_add)
            children_append.append(child_add)
        # 操作记录
        operate_json[room_key] = {
            'children_remove': children_remove,
            'children_append': children_append,
            'furniture_append': furniture_append
        }
        pass
    # 返回信息
    return house_json, operate_json


# 数据转换
def house_scene_parse(scene_url, load_mesh=False, house_id='', load_parametric=False):
    # 方案信息
    house_data_info = {}
    # 原始场景
    house_scene_json = {}
    try:
        if os.path.exists(scene_url) and scene_url.endswith('.json'):
            house_scene_json = json.load(open(scene_url, 'r'))
        if len(house_scene_json) <= 0:
            response_info = requests.get(scene_url, timeout=3)
            house_scene_json = response_info.json()
    except requests.exceptions.RequestException:
        print('call scene json error:', 'time out')
    except Exception as e:
        print('call scene json error:', e)
    # 解析场景 TODO:
    # house_id = ''
    house_data = HouseData()
    house_data.load_json(house_scene_json, load_mesh)

    if len(house_id) == 0 and 'uid' in house_scene_json:
        house_id = house_scene_json['uid']
    # house_customized_data = extract_customized_ceiling(house_id, house_scene_json, upload=True)
    # house_feature_wall_data = extract_customized_feature_wall(house_id, house_scene_json, house_data, upload=True)

    house_parametric_mesh_model, _ = extract_parametric_mesh_model(house_id, house_scene_json,
                                                                   house_data=house_data.house_info,
                                                                   upload=load_parametric, view=False,
                                                                   specified_mesh_type=['CustomizedCeiling', 'CustomizedFeatureWall'])

    room_list = []
    if 'room' in house_data.house_info:
        room_list = house_data.house_info['room']
    for room in room_list:
        # if room['id'] in house_customized_data:
        #     for cs in house_customized_data[room['id']]:
        #         cs['room_area'] = room['area']
        #     room['material_info']['customized_ceiling'] = house_customized_data[room['id']]
        # if room['id'] in house_feature_wall_data:
        #     for cs in house_feature_wall_data[room['id']]:
        #         cs['room_area'] = room['area']
        #     if 'background' not in room['material_info']:
        #         room['material_info']['background'] = []
        #     room['material_info']['background'] += house_feature_wall_data[room['id']]

        if room['id'] in house_parametric_mesh_model:
            if 'decorate_info' not in room['material_info']:
                room['decorate_info'] = []
            room['decorate_info'] += house_parametric_mesh_model[room['id']]

    house_data_info = {'id': house_id, 'room': room_list}

    if 'scene' in house_data.house_info:
        house_data_info['scene'] = house_data.house_info['scene']
    # 返回信息
    house_data_info = get_refine_rooms(house_data_info)
    return house_data_info


# 数据转换
def house_design_trans(design_id, reload=False):
    # 缓存位置
    house_bucket = DATA_OSS_DATABASE
    house_subdir = DATA_OSS_HOUSE_V1
    # 缓存信息
    if not reload:
        house_id = design_id
        # 位置
        house_file = house_id + '.json'
        house_path = os.path.join(DATA_DIR_HOUSE_DATA, house_file)
        house_url = house_subdir + '/' + house_file
        house_data_old = {}
        # 下载
        if oss_exist_file(house_subdir + '/' + house_file, house_bucket):
            print('fetch house data', house_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'oss')
            oss_download_file(house_subdir + '/' + house_file, house_path, house_bucket)
            # 本地
            if os.path.exists(house_path):
                house_data_old = json.load(open(house_path, 'r'))
        if 'room' in house_data_old and len(house_data_old['room']) > 0:
            return house_data_old
    # 服务地址
    server_env, server_url = '', DESIGN_TRANSFER_UAT + '?designId=' + design_id
    try:
        r = requests.get('http://jmenv.tbsite.net:8080/env', timeout=1)
        r.raise_for_status()
        server_env = r.text.strip()
    except Exception as e:
        print('get environment error:', e)
    if 'daily' in server_env:
        server_url = DESIGN_TRANSFER_UAT + '?designId=' + design_id
    elif 'pre' in server_env:
        server_url = DESIGN_TRANSFER_PRE + '?designId=' + design_id
    else:
        server_url = DESIGN_TRANSFER_PRO + '?designId=' + design_id
    # 方案信息
    house_data_info = {}
    try:
        print('fetch house', design_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
        response_info = requests.get(server_url)
        if response_info:
            response_data = response_info.json()
            if 'url' in response_data:
                response_url = response_data['url']
                if len(response_url) > 0:
                    house_data_info = house_data_fetch(response_url)
                else:
                    print('fetch house error:', 'json empty')
                    return house_data_info
            elif 'data' in response_data and len(response_data['data']) > 0:
                response_json = json.loads(response_data['data'])
                house_data_info = response_json['data']
                if 'room' in house_data_info and len(house_data_info['room']) > 0:
                    print('fetch house', design_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
                else:
                    print('fetch house', design_id, datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), 'error')
                    house_data_info = {}
                    return house_data_info
            else:
                print('fetch house error:', 'data empty')
                return house_data_info
    except Exception as e:
        print('fetch house error:', e)
    # 校正坐标
    if 'room' in house_data_info:
        for room_one in house_data_info['room']:
            if 'coordinate' not in room_one:
                room_one['coordinate'] = 'xyz'
            if 'unit' not in room_one:
                room_one['unit'] = 'm'
    # 纠正门窗
    if 'room' in house_data_info:
        for room_one in house_data_info['room']:
            door_info, hole_info, window_info, baywindow_info = [], [], [], []
            if 'furniture_info' not in room_one:
                room_one['furniture_info'] = []
            if 'door_info' in room_one:
                door_info = room_one['door_info']
            if 'hole_info' in room_one:
                hole_info = room_one['hole_info']
            if 'window_info' in room_one:
                window_info = room_one['window_info']
            if 'baywindow_info' in room_one:
                baywindow_info = room_one['baywindow_info']
            for unit_list in [door_info, hole_info, window_info, baywindow_info]:
                for object_one in unit_list:
                    if 'id' not in object_one:
                        continue
                    object_id = object_one['id']
                    object_type, object_style = '', ''
                    object_size, object_scale = [1, 1, 1], [1, 1, 1]
                    object_pos, object_rot = [0, 0, 0], [0, 0, 0, 1]
                    object_entity = ''
                    if 'type' in object_one and 'style' in object_one:
                        object_type, object_style = object_one['type'], object_one['style']
                    if 'size' in object_one and 'scale' in object_one:
                        object_size, object_scale = object_one['size'][:], object_one['scale'][:]
                    if 'position' in object_one and 'rotation' in object_one:
                        object_pos, object_rot = object_one['position'][:], object_one['rotation'][:]
                    if 'entityId' in object_one:
                        object_entity = object_one['entityId']
                    object_new = {
                        'id': object_id,
                        'type': object_type, 'style': object_style,
                        'size': object_size, 'scale': object_scale,
                        'position': object_pos, 'rotation': object_rot,
                        'entityId': object_entity
                    }
                    room_one['furniture_info'].append(object_new)
    # 返回信息
    return house_data_info


# 数据获取
def house_data_fetch(data_url):
    house_data_info = {}
    if data_url == '':
        return house_data_info
    try:
        if os.path.exists(data_url) and data_url.endswith('.json'):
            house_data_info = json.load(open(data_url, 'r'))
            if 'room' in house_data_info and len(house_data_info['room']) > 0:
                pass
            else:
                house_data_info = {}
        if len(house_data_info) <= 0:
            response_info = requests.get(data_url, timeout=1)
            house_data_info = response_info.json()
    except requests.exceptions.RequestException:
        print('call design info error:', 'time out')
    except Exception as e:
        print('call design info error:', e)
    return house_data_info


# 功能测试
if __name__ == '__main__':
    scene_id = 'c7e9cc30-5664-48a7-acd5-6a81acafcfe9'
    scene_id = '6d9cfab6-3ac4-478b-883b-25553f32e770'
    house_data_info = house_design_trans(scene_id)
    print(house_data_info)
