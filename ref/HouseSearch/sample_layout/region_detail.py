from Extract.utils import rot_to_ang
from HouseSearch.sample_layout.region_math import compute_line_line_cos_angle, compute_line_line_project_length_and_dis
import math


def compute_group_near_line_idx(group_data, line_list, target_length=None, length_ratio=0.8):
    now_group_type = group_data["type"]
    half_size_x, half_size_y = group_data["size"][0] / 2., group_data["size"][2] / 2.
    left_top_pt = [group_data["position"][0] - half_size_x, group_data["position"][2] - half_size_y]
    right_bottom_pt = [group_data["position"][0] + half_size_x, group_data["position"][2] + half_size_y]

    left_bottom_pt = [left_top_pt[0], right_bottom_pt[1]]
    right_top_pt = [right_bottom_pt[0], left_top_pt[1]]

    key_point_list = [right_top_pt, left_top_pt, left_bottom_pt, right_bottom_pt, right_top_pt]

    out_line_idx = []
    for rect_line_idx in range(len(key_point_list) - 1):
        rect_line = [key_point_list[rect_line_idx], key_point_list[rect_line_idx + 1]]
        rect_line_length = math.sqrt((key_point_list[rect_line_idx][0] - key_point_list[rect_line_idx + 1][0]) ** 2 + \
                                     (key_point_list[rect_line_idx][1] - key_point_list[rect_line_idx + 1][1]) ** 2)

        for line_idx, line in enumerate(line_list):
            floor_line = [line["p1"], line["p2"]]
            line_length = math.sqrt((floor_line[0][0] - floor_line[1][0]) ** 2 + \
                                    (floor_line[0][1] - floor_line[1][1]) ** 2)

            if compute_line_line_cos_angle(rect_line, floor_line) > 0.7:
                length, dis, vec = compute_line_line_project_length_and_dis(rect_line, floor_line)
                if dis > 2.0 or length < rect_line_length * 0.5:
                    continue
                else:
                    if target_length:
                        if target_length > line_length * length_ratio:
                            continue

                    if line not in out_line_idx:
                        out_line_idx.append(line_idx)
    # 把没有unit的排前面
    out_list = []
    for idx in out_line_idx:
        if line_list[idx]["unit_depth"] > 0:
            out_list.append(idx)
        else:
            out_list.insert(0, idx)

    return out_list


def get_group_back_2d_middle_pos(group):
    # meeting sofa
    # bed bed
    for obj in group["obj_list"]:
        if obj["role"] in ["sofa", "bed"]:

            half_x = obj["size"][0] / 200.
            half_z = obj["size"][2] / 200.

            position_x = obj["position"][0]
            position_z = obj["position"][2]

            base_mid_top = [0, -half_z]

            ang = rot_to_ang(obj["rotation"])
            # cos_a * origin_x - sin_a * origin_z
            # cos_a * origin_z + sin_a * origin_x
            rot_base_mid_top = [-math.sin(-ang) * base_mid_top[1] + position_x,
                                math.cos(-ang) * base_mid_top[1] + position_z]

            return rot_base_mid_top
    return []
