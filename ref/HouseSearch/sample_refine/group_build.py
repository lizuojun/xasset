import os
import json
import copy

bed_size_json_path = os.path.join(os.path.dirname(__file__), "../source/bed_size_refined.json")
bed_size_json = json.load(open(bed_size_json_path))


def bed_group_build(origin_group, target_group_size, seed_info):
    input_bed_info = {}
    input_side_table_info = {}
    input_side_table_light_info = {}
    for jid in seed_info:
        obj = seed_info[jid]
        if obj["role"] == "bed":
            input_bed_info = obj.copy()
            if jid in bed_size_json:
                input_bed_info["collider_width"] = input_bed_info["size"][0] / 100. + bed_size_json[jid][0]
            else:
                if input_bed_info["size"][0] / 100. > 2.20:
                    input_bed_info["collider_width"] = input_bed_info["size"][0] / 100.
                else:
                    input_bed_info["collider_width"] = input_bed_info["size"][0] / 100.
            input_bed_info["width_scale"] = 1.0

        elif obj["role"] == "side table":
            input_side_table_info = obj.copy()
            if input_side_table_info["size"][0] > 0.55:
                input_side_table_info["width_scale"] = input_side_table_info["size"][0] / 100. / 0.55
                input_side_table_info["collider_width"] = 0.55
            else:
                input_side_table_info["width_scale"] = 1.0
                input_side_table_info["collider_width"] = input_side_table_info["size"][0] / 100.
            input_side_table_info["num_layout"] = 2

        elif obj["role"] == "side table lighting":
            input_side_table_light_info = obj.copy()


    if not input_bed_info or not input_side_table_info:
        return

    target_group_width = target_group_size[0]
    full_type_layout_size = input_side_table_info["collider_width"] * 2 + input_bed_info["collider_width"]
    if target_group_width < full_type_layout_size:
        # 改成单柜
        if target_group_width < 0.50 * 2 + 1.80 - 0.2:
            input_side_table_info["num_layout"] = 1

        input_side_table_info["width_scale"] = 0.50 / (input_side_table_info["size"][0] / 100.)
        input_side_table_info["collider_width"] = 0.50

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
        "normal_position": [
            input_side_table_info["collider_width"] / 2. + input_bed_info["collider_width"] / 2.0 + 0.05, 0.0,
            input_side_table_info["collider_width"] / 2. - bed_info["size"][2] / 100.0 / 2.0],
        "normal_rotation": [0, 0.0, 0, 1.0]
    }

    if input_side_table_light_info:
        side_table_light = {
            "id": input_side_table_light_info["id"],
            "type": input_side_table_light_info["type"],
            "style": input_side_table_light_info["style"],
            "size": input_side_table_light_info["size"].copy(),
            "scale": [1, 1, 1],
            "position": [0, 0, 0],
            "rotation": [0, -0.0, 0, 1.0],
            "entityId": "17524",
            "categories": ["89404b8a-5bb6-42cf-95fa-73c9bfba4c97"],
            "category": "89404b8a-5bb6-42cf-95fa-73c9bfba4c97",
            "relate": "wall",
            "group": "Bed",
            "role": "side table lighting",
            "count": 1,
            "adjust_position": [0, 0, 0],
            "normal_position": [
                side_info["normal_position"][0], 2.7 - input_side_table_light_info["size"][1]/100.,
                side_info["normal_position"][2]],
            "normal_rotation": [0, 0.0, 0, 1.0]
        }
    else:
        side_table_light = {}

    obj_list = []
    obj_list.append(bed_info)
    obj_list.append(side_info)
    if side_table_light:
        obj_list.append(side_table_light)

    if input_side_table_info["num_layout"] == 2:
        another_side = copy.deepcopy(side_info)
        another_side["normal_position"] = [
            -input_side_table_info["collider_width"] / 2. - input_bed_info["collider_width"] / 2.0 - 0.05, 0.0,
            input_side_table_info["collider_width"] / 2. - bed_info["size"][
                2] / 100.0 / 2.0]
        obj_list.append(another_side)

        if side_table_light:
            another_side_table_light = copy.deepcopy(side_table_light)
            another_side_table_light["normal_position"] = [
                another_side["normal_position"][0], 2.7 - another_side_table_light["size"][1]/100.,
                another_side["normal_position"][2]]
            obj_list.append(another_side_table_light)

    origin_group["obj_list"] = obj_list
    origin_group["obj_main"] = bed_info["id"]
    origin_group["size"] = [
        input_bed_info["collider_width"] + 0.1 + input_side_table_info["num_layout"] * input_side_table_info[
            "collider_width"],
        1.5,
        bed_info["size"][2] / 100.]
    origin_group["offset"] = [0.0, 0.0, 0.0]
    origin_group["position"] = [0.0, 0.0, 0.0]
    origin_group["rotation"] = [0.0, 0.0, 0.0, 1.0]
    origin_group["size_min"] = origin_group["size"].copy()
    origin_group["size_rest"] = [0.0, 0.0, 0.0, 0.0]

    return origin_group


def check_info():
    pass
