import os
import json
import copy
bed_size_json_path = os.path.join(os.path.dirname(__file__), "../source/bed_size_refined.json")
bed_size_json = json.load(open(bed_size_json_path))


def bed_group_build(origin_group, target_group_size, seed_info):
    input_bed_info = {}
    input_side_table_info = {}
    for jid in seed_info:
        obj = seed_info[jid]
        if obj["role"] == "bed":
            input_bed_info = obj.copy()
            if jid in bed_size_json:
                input_bed_info["collider_width"] = input_bed_info["size"][0] + bed_size_json[jid]
            else:
                if input_bed_info["size"][0] > 2.20:
                    input_bed_info["collider_width"] -= 0.20
                else:
                    input_bed_info["collider_width"] = input_bed_info["size"][0]
            input_bed_info["width_scale"] = 1.0

        elif obj["role"] == "side table":
            input_side_table_info = obj.copy()
            if input_side_table_info["size"][0] > 0.55:
                input_side_table_info["width_scale"] = input_side_table_info["size"][0] / 0.55
                input_side_table_info["collider_width"] = 0.55
            else:
                input_side_table_info["width_scale"] = 1.0
                input_side_table_info["collider_width"] = input_side_table_info["size"][0]
            input_side_table_info["num_layout"] = 2

    if not input_bed_info or not input_side_table_info:
        return

    target_group_width = target_group_size[0]
    full_type_layout_size = input_side_table_info["scaled_width_refined"] * 2 + input_bed_info["scaled_width_refined"]
    if target_group_width < full_type_layout_size:
        # 改成单柜
        if target_group_width < 0.45 * 2 + 1.80:
            input_side_table_info["num_layout"] = 1

        input_side_table_info["width_scale"] = input_side_table_info["size"][0] / 0.5
        input_side_table_info["collider_width"] = 0.5

        input_bed_info["width_scale"] = 1.8 / input_bed_info["collider_width"]
        input_bed_info["collider_width"] = 1.8

    # 拼接功能区
    bed_info = {
        "id": input_bed_info["id"],
        "type": input_bed_info["type"],
        "style": input_bed_info["style"],
        "size": input_bed_info["size"].copy(),
        "scale": [input_bed_info["width_scale"], 1, 1],
        "position": [0, 0, 0],
        "rotation": [0, -0.0, 0, 1.0],
        "entityId": "17523",
        "categories": ["41ac92b5-5f88-46d0-a59a-e1ed31739154"],
        "category": "41ac92b5-5f88-46d0-a59a-e1ed31739154",
        "relate": "wall",
        "group": "Bed",
        "role": "bed",
        "count": 1,
        "adjust_position": [0, 0, 0],
        "normal_position": [0.0, 0, 0.0],
        "normal_rotation": [0, 0.0, 0, 1.0]
    }

    side_info = {
        "id": input_side_table_info["id"],
        "type": input_side_table_info["type"],
        "style": input_side_table_info["style"],
        "size": input_side_table_info["size"].copy(),
        "scale": [input_side_table_info["width_scale"], 1, 1],
        "position": [0, 0, 0],
        "rotation": [0, -0.0, 0, 1.0],
        "entityId": "17524",
        "categories": ["89404b8a-5bb6-42cf-95fa-73c9bfba4c97"],
        "category": "89404b8a-5bb6-42cf-95fa-73c9bfba4c97",
        "relate": "wall",
        "group": "Bed",
        "role": "side table",
        "count": 1,
        "adjust_position": [0, 0, 0],
        "normal_position": [bed_info["collider_width"]/2.0+0.05, 0.0, -bed_info["size"][2]/2.0],
        "normal_rotation": [0, 0.0, 0, 1.0]
    }
    obj_list = []
    obj_list.append(bed_info)
    obj_list.append(side_info)
    if input_side_table_info["num_layout"] == 2:
        another_side = copy.deepcopy(side_info)
        another_side["normal_position"] = [-bed_info["collider_width"]/2.0-0.05, 0.0, -bed_info["size"][2]/2.0],

    origin_group["obj_list"] = obj_list
    origin_group["obj_main"] = bed_info["id"]
    origin_group["size"] = [bed_info["collider_width"]+0.1+input_side_table_info["num_layout"]*input_side_table_info["collider_width"],
                            1.5,
                            bed_info["size"][2]]
    origin_group["offset"] = [0.0, 0.0, 0.0]
    origin_group["position"] = [0.0, 0.0, 0.0]
    origin_group["rotation"] = [0.0, 0.0, 0.0, 1.0]
    origin_group["size_min"] = origin_group["size"].copy()
    origin_group["size_rest"] = origin_group["size"].copy()

    return origin_group


def check_info():
    pass
