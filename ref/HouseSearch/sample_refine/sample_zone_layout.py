import math
import copy

# 功能区域摆放
from Extract.utils import compute_furniture_rect, xyz_to_ang, ang_to_ang, rot_to_ang
from LayoutByRule.house_analysis import room_line

MIN_GROUP_PASS = 0.2
MID_GROUP_PASS = 0.8
MAX_GROUP_PASS = 3.0

UNIT_WIDTH_GROUP = 1.5
UNIT_DEPTH_GROUP = 1.0
UNIT_WIDTH_GROUP_MAX = 5.0
UNIT_WIDTH_GROUP_MIN = 0.4
UNIT_DEPTH_GROUP_MAX = 4.0
UNIT_DEPTH_GROUP_MIN = 0.2
UNIT_DEPTH_GROUP_MID = 0.6

UNIT_TYPE_NONE = 0
UNIT_TYPE_GROUP = 1
UNIT_TYPE_DOOR = 2
UNIT_TYPE_SIDE = 3
UNIT_TYPE_WINDOW = 4
UNIT_TYPE_AISLE = 5
UNIT_TYPE_WALL = 6

UNIT_WIDTH_DOOR = 0.85
UNIT_WIDTH_HOLE = 1.50
UNIT_WIDTH_AISLE = 2.0
UNIT_WIDTH_DOOR_FRAME = 0.05


def room_rect_layout_zone(line_list, zone_list, group_list, room_data=None):
    # 组合检查
    group_result = []
    zone_group_map = []

    # 区域参数
    for zone_idx, zone_one in enumerate(zone_list):
        edge_idx, line_idx, unit_rat = compute_zone_rely(zone_one, line_list)
        if len(unit_rat) >= 2:
            if abs(unit_rat[0] - 0) < 0.01:
                unit_rat[0] = 0
            elif abs(unit_rat[1] - 1) < 0.05:
                unit_rat[1] = 1
        zone_one['edge_idx'], zone_one['line_idx'], zone_one['unit_rat'] = edge_idx, line_idx, unit_rat

    # 组合布局 区域与sample进行对应
    line_used, line_face, zone_used = {}, {}, {}
    for group_idx, group_one in enumerate(group_list):
        # 组合信息
        group_type, group_size = group_one['type'], group_one['size']

        if 'zone' in group_one:
            group_room_type = group_one['zone']
        else:
            group_room_type = ''

        group_width, group_height, group_depth = group_size[0], group_size[1], group_size[2]
        # 最佳参数
        param_best = {
            'index': -1,
            'score': -100,
            'vertical': 0,
            'width': 0,
            'depth': 0,
            'depth_suit': 0,
            'width_rest': 0,
            'depth_rest': 0,
            'ratio': [0, 1],
            'ratio_best': [0, 1],
            'group': []
        }
        # 区域查找
        for zone_idx, zone_one in enumerate(zone_list):
            if zone_idx in zone_used:
                continue
            zone_room_type, zone_type, zone_size = zone_one['zone'], zone_one['type'], zone_one['size']
            edge_idx, line_idx, unit_rat = zone_one['edge_idx'], zone_one['line_idx'], zone_one['unit_rat']
            if group_type == zone_type:
                if group_type == "Cabinet" and group_room_type != zone_room_type:
                    continue

                zone_used[zone_idx] = 1
                suit_width, suit_depth = zone_size[0], zone_size[2]
                suit_ratio, suit_ratio_best = [0, 1], [0, 1]
                # 侧面
                if edge_idx in [1, 3]:
                    # group_one = spin_exist_group(group_one)
                    group_type, group_size = group_one['type'], group_one['size']
                    group_width, group_height, group_depth = group_size[0], group_size[1], group_size[2]
                # 靠墙
                if edge_idx in [0, 1, 2, 3]:
                    line_one = line_list[line_idx]
                    line_width = line_one['width']
                    max_pass, min_pass, mid_pass = 2.0, MIN_GROUP_PASS, 0
                    suit_width, suit_depth, suit_depth_min, suit_ratio, suit_ratio_best = \
                        compute_suit_ratio(line_list, line_idx, group_width, group_depth,
                                           unit_rat, [], max_pass, min_pass, mid_pass, line_used)

                    if len(unit_rat) > 0:
                        suit_ratio[0], suit_ratio[1] = min(unit_rat[0], suit_ratio[0]), min(unit_rat[1], suit_ratio[1])
                        suit_width = line_width * (suit_ratio[1] - suit_ratio[0])
                        suit_depth = max(suit_depth, zone_size[2])
                        suit_ratio_best = unit_rat[:]
                        if line_width * (unit_rat[1] - unit_rat[0]) > group_width:
                            suit_ratio_best = unit_rat[:]
                # 悬空 TODO: 扩展比例
                else:
                    suit_ratio = [0, 1]
                # 参数
                param_best['index'] = line_idx
                param_best['score'] = 10
                param_best['vertical'] = 0
                param_best['width'] = group_width
                param_best['depth'] = group_depth
                param_best['depth_suit'] = suit_depth
                param_best['width_rest'] = suit_width - group_width
                param_best['depth_rest'] = suit_depth - group_depth
                param_best['ratio'] = suit_ratio[:]
                param_best['ratio_best'] = suit_ratio_best[:]
                param_best['zone'] = zone_one

                if line_idx > 0:
                    param_best['width'] = line_list[line_idx]["width"]

                break

        # 参数判断
        index_best = int(param_best['index'])
        if 'zone' not in param_best:
            continue
        # 参数信息
        param_add = param_best.copy()
        param_add['ratio'] = param_best['ratio'][:]
        param_add['ratio_best'] = param_best['ratio_best'][:]
        param_add['zone'] = param_best['zone'].copy()
        group_add = group_one
        param_add['group'].append(group_add)
        if index_best not in line_used:
            line_used[index_best] = []
        line_used[index_best].append(param_add)

    # 计算精细 布局位置/朝向/尺寸/根据align位置调整 全屋调整
    group_result = []
    for line_idx in line_used.keys():
        # 遍历参数
        param_list = line_used[line_idx]
        for param_idx, param_one in enumerate(param_list):
            # 布局信息
            group_ratio = param_one['ratio']
            line_width = param_one["width"]
            group_width_rest, group_depth_rest = param_one['width_rest'], param_one['depth_rest']
            ratio_pre, ratio_post, ratio_dir = group_ratio[0], group_ratio[1], 0

            # 查找功能区
            group_width = param_one["group"][0]["size"][0]

            # 区域信息
            if 'zone' in param_one:
                zone_one = param_one['zone']
                zone_type, zone_size = zone_one['type'], zone_one['size']
                zone_pos, zone_rot, zone_ang = zone_one['position'], zone_one['rotation'], rot_to_ang(
                    zone_one['rotation'])
                edge_idx, line_idx, unit_rat = zone_one['edge_idx'], zone_one['line_idx'], zone_one['unit_rat']

            else:
                continue

            # 限制比例
            if ratio_pre <= group_ratio[0]:
                ratio_pre = group_ratio[0]
            if ratio_post >= group_ratio[1]:
                ratio_post = group_ratio[1]

            # 靠窗判断
            window_flag, door_flag = 0, 0
            # 旋转判断
            vertical_flag = param_one['vertical']
            # 悬空判断
            type_swap, index_swap, width_swap, depth_swap, angle_swap, ratio_swap = 0, line_idx, 0, 0, 0, []

            # 遍历组合
            group_cnt = 1
            for group_idx in range(group_cnt):
                # 组合信息
                group_one = param_one['group'][group_idx]
                group_size, group_size_min = group_one['size'], group_one['size_min']
                group_width, group_height, group_depth = group_size[0], group_size[1], group_size[2]
                group_width_min, group_depth_min = group_size_min[0], group_size_min[2]
                group_width_well, group_depth_max = group_width, group_depth

                group_one['position'] = [zone_pos[0], group_one['position'][1], zone_pos[2]]
                group_one['rotation'] = [0, math.sin(zone_ang / 2), 0, math.cos(zone_ang / 2)]
                group_one['regulation'] = [0.0, 0.0, 0.0, 0.0]

                # 特别信息
                group_one['vertical'] = vertical_flag
                group_one['window'] = window_flag
                # group_one['center'] = center_flag
                # 区域信息
                group_one['region_direct'] = ratio_dir
                group_one['region_middle'] = (ratio_pre + ratio_post) / 2
                group_one['region_center'] = []
                group_one['region_extent'] = group_depth
                # group_one['region_extent'] = region_depth
                # 新增组合
                group_result.append(group_one)

            # 更新参数
            param_one['ratio'] = [ratio_pre, ratio_post]
            # param_one['width_rest'] = width_rest_new
            # param_one['depth_rest'] = depth_rest_new

    # 返回信息
    return group_result


# 数据计算：区域靠墙
def compute_zone_rely(zone_one, line_list):
    object_type, object_size = zone_one['type'], [abs(zone_one['size'][i]) for i in range(3)]
    object_pos, object_rot = zone_one['position'], zone_one['rotation']
    # 家具矩形
    if 'unit' in zone_one:
        object_unit = zone_one['unit']
    else:
        object_unit = compute_furniture_rect(object_size, object_pos, object_rot)
        zone_one['unit'] = object_unit
    # 靠墙判断
    rely_dlt = 0.40
    if object_type.startswith('Meeting') or object_type.startswith('sofa'):
        rely_dlt = 0.45
    elif object_type.startswith('Bed') or object_type.startswith('bed'):
        rely_dlt = 0.40
    elif object_type.startswith('Cabinet') or object_type.startswith('cabinet'):
        rely_dlt = 0.40

    unit_one = object_unit
    edge_len, edge_idx = int(len(unit_one) / 2), -1
    rely_dis, rely_idx, rely_rat = 0, -1, []
    for j in range(edge_len):
        x_p = unit_one[(2 * j + 0) % len(unit_one)]
        y_p = unit_one[(2 * j + 1) % len(unit_one)]
        x_q = unit_one[(2 * j + 2) % len(unit_one)]
        y_q = unit_one[(2 * j + 3) % len(unit_one)]
        x_r = unit_one[(2 * j + 4) % len(unit_one)]
        y_r = unit_one[(2 * j + 5) % len(unit_one)]
        # 宽度深度
        unit_width, unit_angle = xyz_to_ang(x_p, y_p, x_q, y_q)
        if j <= 1:
            unit_depth = math.sqrt((x_r - x_q) * (x_r - x_q) + (y_r - y_q) * (y_r - y_q))
        else:
            x_o = unit_one[2 * j - 2]
            y_o = unit_one[2 * j - 1]
            unit_depth = math.sqrt((x_o - x_p) * (x_o - x_p) + (y_o - y_p) * (y_o - y_p))
        # if unit_width < unit_depth / 2 or unit_width < 0.2:
        #     continue
        unit_dis, unit_idx, unit_rat = 0, -1, []

        max_unit_dis, max_unit_idx = -1000, -1
        for line_idx, line_one in enumerate(line_list):
            # 重合方向
            x1, y1, x2, y2 = line_one['p1'][0], line_one['p1'][1], line_one['p2'][0], line_one['p2'][1]
            line_width, line_angle = line_one['width'], line_one['angle']
            if abs(ang_to_ang(line_angle - unit_angle)) > 0.1:
                continue
            if abs(y1 - y2) < 0.1 and abs(x1 - x2) < 0.1:
                continue
            elif abs(y1 - y2) < 0.1:
                if abs(y1 - y_p) > rely_dlt * 1.0:
                    continue
                elif abs(y1 - y_p) > rely_dlt * 0.5 and j > 0:
                    continue
            elif abs(x1 - x2) < 0.1:
                if abs(x1 - x_p) > rely_dlt * 1.0:
                    continue
                elif abs(x1 - x_p) > rely_dlt * 0.5 and j > 0:
                    continue
            else:
                r_p_x = (x_p - x1) / (x2 - x1)
                r_p_y = (y_p - y1) / (y2 - y1)
                r_q_x = (x_q - x1) / (x2 - x1)
                r_q_y = (y_q - y1) / (y2 - y1)
                if abs(r_p_x - r_p_y) > 0.01 or abs(r_q_x - r_q_y) > 0.01:
                    continue
            # 重合比例
            if abs(x2 - x1) >= 0.00001:
                r_p = (x_p - x1) / (x2 - x1)
                r_q = (x_q - x1) / (x2 - x1)
            elif abs(y2 - y1) >= 0.00001:
                r_p = (y_p - y1) / (y2 - y1)
                r_q = (y_q - y1) / (y2 - y1)
            else:
                continue
            if r_p <= 0 and r_q <= 0:
                continue
            if r_p >= 1 and r_q >= 1:
                continue
            if abs(r_p - r_q) < 0.001:
                continue
            r1 = max(0, min(r_p, r_q))
            r2 = min(1, max(r_p, r_q))
            if line_width * (r2 - r1) < 0.1:
                continue

            temp_dis = line_width * (r2 - r1)
            if temp_dis > max_unit_dis:
                max_unit_dis = unit_dis
                unit_idx, unit_dis = line_idx, line_width * (r2 - r1)
                unit_rat = [min(r_p, r_q), max(r_p, r_q)]

        if 0 <= unit_idx < len(line_list):
            if unit_dis > rely_dis:
                edge_idx, rely_dis, rely_idx, rely_rat = j, unit_dis, unit_idx, unit_rat
            if unit_dis > unit_width * 0.9 and unit_width > unit_depth:
                break
    return edge_idx, rely_idx, rely_rat


# 计算墙体承载区域
def compute_suit_ratio(line_list, line_idx, group_width, group_depth, line_ratio=[0, 1],
                       merge_type=[], max_pass=-1, min_pass=-1, mid_pass=0, line_used={}):
    line_one = line_list[line_idx]
    line_width = line_one['width']
    suit_width, suit_depth, suit_depth_min = line_width, UNIT_DEPTH_GROUP_MAX * 2, UNIT_DEPTH_GROUP_MAX * 1
    suit_ratio = line_ratio[:]
    suit_ratio_best = [(suit_ratio[1] + suit_ratio[0]) / 2, (suit_ratio[1] + suit_ratio[0]) / 2]
    suit_depth_best = 0
    # 本身区域
    if min_pass <= -1:
        min_pass = MIN_GROUP_PASS
    if max_pass <= -1:
        max_pass = MAX_GROUP_PASS
    ratio_0, ratio_1 = line_ratio[0], line_ratio[1]
    depth_all = line_one['depth_all']
    if len(depth_all) > 0:
        width_last, depth_last = 0, 0
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
                    if width_now > width_last or depth_last == 0:
                        width_last = width_now
                        depth_last = depth_now
                        suit_depth = depth_now
                        suit_ratio_best = [ratio_pre, ratio_post]
                        suit_depth_best = depth_now
                    elif depth_now > suit_depth_best or depth_now > min(group_depth + 3, group_depth * 2):
                        if len(suit_ratio_best) >= 2 and ratio_pre >= suit_ratio_best[1] - 0.1:
                            suit_ratio_best[1] = max(suit_ratio_best[1], ratio_post)
                elif depth_now < suit_depth:
                    suit_depth = depth_now
                if depth_now < suit_depth_min:
                    suit_depth_min = depth_now
            else:
                if depth_last == 0 and width_now > width_last:
                    width_last = width_now
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

    # 前段融合
    score_pre = line_one['score_pre']
    index_pre = (line_idx - 1 + len(line_list)) % len(line_list)
    line_pre = line_list[index_pre]
    type_pre, width_pre, count_pre = line_pre['type'], line_pre['width'], 0
    merge_flag = 0
    while score_pre <= 2 and type_pre in merge_type and ratio_0 == 0:
        ratio_best_new = 1
        # 阳角判断
        if merge_flag == 0:
            merge_flag = 1
        if score_pre == 2 and line_width > MIN_GROUP_PASS * 2:
            if line_pre['width'] < MIN_GROUP_PASS:
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
        count_pre += 1
        if len(line_pre['depth_all']) > 0:
            for depth_one in line_pre['depth_all'][::-1]:
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
            if width_add >= suit_width_old and merge_flag == 1 and type_pre not in [UNIT_TYPE_DOOR]:
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
    type_post, width_post, count_post = line_post['type'], line_post['width'], 0
    merge_flag = 0
    while score_post <= 2 and type_post in merge_type and ratio_1 == 1:
        ratio_best_new = 0
        # 阳角判断
        if merge_flag == 0:
            merge_flag = 1
        if score_post == 2 and line_width > MIN_GROUP_PASS * 2:
            if line_post['width'] < MIN_GROUP_PASS:
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
        count_post += 1
        if len(line_post['depth_all']) > 0:
            for depth_one in line_post['depth_all']:
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
            if width_add > suit_width_old and merge_flag == 1 and type_post not in [UNIT_TYPE_DOOR]:
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


# 拷贝组合
def copy_exist_group(group_one):
    group_add = group_one.copy()
    group_add['size'] = group_one['size'][:]
    group_add['offset'] = group_one['offset'][:]
    group_add['position'] = group_one['position'][:]
    group_add['rotation'] = group_one['rotation'][:]
    if 'size_min' in group_one:
        group_add['size_min'] = group_one['size_min'][:]
    if 'size_rest' in group_one:
        group_add['size_rest'] = group_one['size_rest'][:]
    if 'regulation' in group_one:
        group_add['regulation'] = group_one['regulation'][:]
    if 'seed_list' in group_one:
        group_add['seed_list'] = group_one['seed_list'][:]

    return group_add


def room_rect_zone_scope(room_data, room_layout, group_result, zone_scope_rule=None):
    # 位置归一化
    for group in group_result:
        group_pos = group["position"]

        group_size = group["size"]
        group_type = group["type"]

        target_ang = rot_to_ang(group["rotation"])

        for obj in group["obj_list"]:
            obj_source_ang = rot_to_ang(obj["normal_rotation"])
            ang_final = obj_source_ang + target_ang

            cos_a = math.cos(target_ang)
            sin_a = math.sin(target_ang)

            origin_x = obj["normal_position"][0]
            origin_z = obj["normal_position"][2]

            obj["position"][0] = cos_a * origin_x - sin_a * origin_z + group_pos[0]
            obj["position"][2] = cos_a * origin_z + sin_a * origin_x + group_pos[2]
            obj["position"][1] += group_pos[1]

            obj["rotation"] = [0., math.sin(ang_final / 2.), 0.0, math.cos(ang_final / 2.)]

        # fake resize
        if group_type in ["Cabinet", "Armoire"]:
            group_size = group["size"]
            if group_size[1] > 2.0 and group_size[0] > 1.5:
                group_size[1] = 2.65
            for obj in group["obj_list"]:
                if obj["role"] in ["cabinet", "armoire"]:
                    obj["scale"] = [group_size[i]/(obj["size"][i]/100.) for i in range(3)]

    room_layout["layout_scheme"][0]["group"] = group_result


def room_rect_zone_deco(room_data, room_layout, group_result):
    # 窗: 窗帘
    # 顶: 顶灯
    # 墙: 挂画
    # 台面配饰
    pass


def uniform_group_sample_list(group_list):
    for g in group_list:
        ang = rot_to_ang(g["rotation"])
        if abs(ang - 0.) > 0.1:
            g["rotation"] = [0., 0., 0., 1.]
            for obj in g["obj_list"]:
                obj_source_ang = rot_to_ang(obj["normal_rotation"])
                ang_final = obj_source_ang - ang

                cos_a = math.cos(- ang)
                sin_a = math.sin(- ang)

                origin_x = obj["normal_position"][0]
                origin_z = obj["normal_position"][2]

                obj["normal_position"][0] = cos_a * origin_x - sin_a * origin_z
                obj["normal_position"][2] = cos_a * origin_z + sin_a * origin_x

                obj["normal_rotation"] = [0., math.sin(ang_final / 2.), 0.0, math.cos(ang_final / 2.)]


def split_group_sample_list(group_list_input):
    group_main_list = []
    group_deco_list = []
    for group in group_list_input:
        if group["type"] in ["Ceiling", "Window", "Wall", "Door", "Floor", "Background", "Customize"]:
            group_deco_list.append(group)
        else:
            group_main_list.append(group)
    return group_main_list, group_deco_list


def room_sample_layout_zone(room_data, room_layout):
    line_list, line_ori = room_line(room_data, [], [], [], [], room_data["type"], room_data["area"])
    if "region_info" in room_data:
        zone_list = room_data["region_info"]
        room_layout["layout_scheme"] = copy.deepcopy(room_layout["layout_sample"])
        group_list = copy.deepcopy(room_layout["layout_scheme"][0]["group"])
        group_main_list, group_deco_list = split_group_sample_list(group_list)

        group_main = room_rect_layout_zone(line_list, zone_list, group_main_list)

        # 区域内恢复
        room_rect_zone_scope(room_data, room_layout, group_main)

        # 配饰布局
        room_rect_zone_deco(room_data, room_layout, group_deco_list)

    return room_data, room_layout



