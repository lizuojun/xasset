from Furniture.furniture_group_replace import pre_group_rect_adjust, get_furniture_group, rot_to_ang
from HouseSearch.group.group_related_add import sample_group_add_related
from HouseSearch.group_sample_build_info import update_group_rug_obj
import json
import math
import os

from HouseSearch.sample_refine.group_build import bed_group_build

art_size_json = json.load(open(os.path.join(os.path.dirname(__file__), "../source/art_size_refined.json")))


def get_default_tv(group_info, best_group_size):
    half_z = group_info["size"][2] / 2. - 3 / 200.

    tv = {
                        "id": "0c5efde1-79b5-4c77-bf81-efa976963813",
                        "type": "electronics/TV - wall-attached",
                        "style": "Contemporary",
                        "size": [
                            129.988,
                            75.77028,
                            3.1459,
                        ],
                        "scale": [
                            1,
                            1,
                            1
                        ],
                        "position": [
                            0.,0.,0.
                        ],
                        "rotation": [
                            0.,0.,0.,1.
                        ],
                        "entityId": "42552",
                        "relate": "wall",
                        "relate_role": "wall",
                        "group": "Media",
                        "role": "tv",
                        "count": 1,
                        "relate_position": [],
                        "adjust_position": [
                            0,
                            0,
                            0
                        ],
                        "origin_position": [
                            0,
                            0,
                            0
                        ],
                        "origin_rotation": [
                            0,
                            0,
                            0
                        ],
                        "normal_position": [
                            -0.0,
                            0.9,
                            -half_z
                        ],
                        "normal_rotation": [
                            0,
                            0.0,
                            0,
                            1.0
                        ]
                    }
    group_info["obj_list"].append(tv)


def advisor_sample_refine(layout_room_sample, seed_dict, best_group_info=None):
    if "layout_sample" not in layout_room_sample:
        return

    if len(layout_room_sample["layout_sample"]) == 0:
        return

    if "group" not in layout_room_sample["layout_sample"][0]:
        return

    rug_list = []
    for jid in seed_dict:
        if seed_dict[jid]["group"] == "Meeting" and seed_dict[jid]["role"] == "rug":
            rug_list.append(jid)
        elif seed_dict[jid]["group"] == "Bed" and seed_dict[jid]["role"] == "rug":
            rug_list.append(jid)

    group_sample_info = {}
    for jid in seed_dict:
        group_name = seed_dict[jid]["group"]
        group_role = seed_dict[jid]["role"]
        if group_name not in group_sample_info:
            group_sample_info[group_name] = {}
        if group_role not in group_sample_info[group_name]:
            group_sample_info[group_name][group_role] = []
        group_sample_info[group_name][group_role].append(jid)

    best_group_size = {}
    best_group_data = {}
    if best_group_info:
        for target_group in best_group_info:
            if target_group["type"] == "Bed":
                best_group_size["Bed"] = target_group["size"]
                best_group_data["Bed"] = target_group

            elif target_group["type"] == "Media":
                best_group_size["Media"] = target_group["size"]
                best_group_data["Media"] = target_group

            elif target_group["type"] == "Armoire":
                best_group_size["Armoire"] = target_group["size"]
                best_group_data["Armoire"] = target_group

            elif target_group["type"] == "Meeting":
                best_group_size["Meeting"] = target_group["size"]
                best_group_data["Meeting"] = target_group

            elif target_group["type"] == "Cabinet" and target_group["zone"] == "Hallway":
                best_group_size["Cabinet_Hallway"] = target_group["size"]
                best_group_data["Cabinet_Hallway"] = target_group

            elif target_group["type"] == "Cabinet" and target_group["zone"] == "DiningRoom":
                best_group_size["Cabinet_DiningRoom"] = target_group["size"]
                best_group_data["Cabinet_DiningRoom"] = target_group

    # 软装处理
    for group_info_idx in range(len(layout_room_sample["layout_sample"][0]["group"]) - 1, -1, -1):
        group_info = layout_room_sample["layout_sample"][0]["group"][group_info_idx]
        group_type = group_info["type"]
        if group_type == "Bed":
            if "Bed" in group_sample_info and "Bed" in best_group_size:
                bed_jid = None
                side_table_jid = None
                if "bed" in group_sample_info["Bed"]:
                    bed_jid = group_sample_info["Bed"]["bed"][0]
                if "side table" in group_sample_info["Bed"]:
                    side_table_jid = group_sample_info["Bed"]["side table"][0]

                if bed_jid and side_table_jid:
                    bed_group_build(group_info, best_group_size["Bed"], seed_dict)

            # for obj_idx in range(len(group_info["obj_list"]) - 1, -1, -1):
            #     if group_info["obj_list"][obj_idx]['role'] not in ["side table", "bed"]:
            #         group_info["obj_list"].pop(obj_idx)

            if len(rug_list) > 0:
                update_group_rug_obj(group_info, [{"id": rug_list[0]}])

        elif group_type == "Meeting":
            group_sample_info_meeting = group_sample_info["Meeting"] if "Meeting" in group_sample_info else {}

            side_sofa_default = None
            for obj_idx in range(len(group_info["obj_list"]) - 1, -1, -1):
                if group_info["obj_list"][obj_idx]['role'] == "side sofa":
                    side_sofa_default = group_info["obj_list"][obj_idx]
                    group_info["obj_list"].pop(obj_idx)

                if group_info["obj_list"][obj_idx]['role'] in ["accessory", "light"]:
                    group_info["obj_list"].pop(obj_idx)

            if side_sofa_default:
                if "side sofa" in group_sample_info_meeting and len(group_sample_info_meeting["side sofa"]) > 0:
                    group_info["obj_list"].append(side_sofa_default)

            for obj_idx in range(len(group_info["obj_list"]) - 1, -1, -1):
                if group_info["obj_list"][obj_idx]['role'] == "table":
                    obj_info = group_info["obj_list"][obj_idx]
                    obj_info["normal_rotation"] = [0, 0, 0, 1.0]
                elif group_info["obj_list"][obj_idx]['role'] == "rug":
                    obj_info = group_info["obj_list"][obj_idx]
                    obj_info["normal_rotation"] = [0, 0, 0, 1.0]
                elif group_info["obj_list"][obj_idx]['role'] == "side table":
                    if "side table" not in group_sample_info_meeting or len(
                            group_sample_info_meeting["side table"]) == 0:
                        group_info["obj_list"].pop(obj_idx)

            if len(rug_list) > 0:
                update_group_rug_obj(group_info, [{"id": rug_list[0]}])

        elif group_type == "Wall":
            # 挂画处理
            for obj_idx in range(len(group_info["obj_list"]) - 1, -1, -1):
                if group_info["obj_list"][obj_idx]['role'] == "art":
                    art_jid = group_info["obj_list"][obj_idx]["id"]

                    if art_jid in art_size_json:
                        new_type = art_size_json[art_jid]
                    else:
                        continue

                    if new_type == "double":
                        new_size = [127 * 1.2, 88 * 1.0, 0]
                    elif new_type == "multi":
                        new_size = [150 * 1.2, 78 * 1.2, 0]
                    else:
                        continue

                    new_scale = [new_size[i] / group_info["obj_list"][obj_idx]["size"][i] for i in range(2)]
                    new_scale += [1.0]
                    group_info["obj_list"][obj_idx]["scale"] = new_scale

        elif group_type == "Armoire":
            key = 'Armoire'
            if key in best_group_size:
                target_size = best_group_size[key]
                group_info["size"][0] = target_size[0]
                group_info["size"][2] = target_size[2]

                for obj in group_info["obj_list"]:
                    if obj["role"] == "armoire":
                        obj["scale"][0] = group_info["size"][0] / (obj["size"][0]/100.)
                        obj["scale"][2] = group_info["size"][2] / (obj["size"][2]/100.)

        elif group_type == "Cabinet":
            if "zone" in group_info:
                key = 'Cabinet_' + group_info['zone']
                if key in best_group_size:
                    target_size = best_group_size[key]
                    group_info["size"][0] = target_size[0]
                    group_info["size"][2] = target_size[2]

                    for obj in group_info["obj_list"]:
                        if obj["role"] == "cabinet":
                            obj["scale"][0] = group_info["size"][0] / (obj["size"][0]/100.)
                            obj["scale"][2] = group_info["size"][2] / (obj["size"][2]/100.)

    # 考虑 床/沙发/餐桌/梳妆台/
    replace_pair = {}
    replace_size = {}

    for group_info in layout_room_sample["layout_sample"][0]["group"]:
        group_type = group_info["type"]
        if group_type in group_sample_info:
            for obj in group_info["obj_list"]:
                if obj["role"] in group_sample_info[group_type]:

                    target_seed_list = group_sample_info[group_type][obj["role"]]
                    if len(target_seed_list) > 0 and group_type in ["Bed", "Meeting", "Dining", "Work", "Rest",
                                                                    "Media"]:
                        replace_pair[obj["id"]] = target_seed_list[0]
                        replace_size[target_seed_list[0]] = seed_dict[target_seed_list[0]]["size"].copy()
                obj["size_max"] = [obj["size"][i] * obj["scale"][i] * 1.5 for i in range(3)]
                obj["size_cur"] = [obj["size"][i] * obj["scale"][i] for i in range(3)]
        else:
            for obj in group_info["obj_list"]:
                obj["size_max"] = [obj["size"][i] * obj["scale"][i] * 1.5 for i in range(3)]
                obj["size_cur"] = [obj["size"][i] * obj["scale"][i] for i in range(3)]

    # Work
    for group_info in layout_room_sample["layout_sample"][0]["group"]:
        group_type = group_info["type"]
        if group_type == "Work":
            # group_info["size"] = group_info["size_min"].copy()
            # group_info["size_rest"] = [0, 0, 0, 0]
            group_info["neighbor_base"] = [2.0, 2.0, 2.0, 2.0]

    layout_room_sample["layout_sample"][0]["group"] = pre_group_rect_adjust(
        layout_room_sample["layout_sample"][0]["group"],
        replace_pair, replace_size, {})

    # 修复media
    for group_info_idx in range(len(layout_room_sample["layout_sample"][0]["group"]) - 1, -1, -1):
        group_info = layout_room_sample["layout_sample"][0]["group"][group_info_idx]
        group_type = group_info["type"]
        if group_type == "Media":
            group_sample_info_media = group_sample_info["Media"] if "Media" in group_sample_info else {}
            used_back_wall_media = False
            if "table" not in group_sample_info_media or len(group_sample_info_media["table"]) == 0:
                continue
            for jid in group_sample_info_media["table"]:
                if jid in seed_dict and seed_dict[jid]["size"][1] > 150 and seed_dict[jid]["size"][0] > 220:
                    used_back_wall_media = True
                    new_size_scale = 265 / seed_dict[jid]["size"][1]
                    for i in group_info["obj_list"]:
                        if i["role"] == "table":
                            i["scale"][0] *= new_size_scale
                            i["scale"][1] = new_size_scale
                    group_info["size"][0] *= new_size_scale
                    group_info["size"][1] = 2.65
                    group_info["size_min"][0] *= new_size_scale
                    group_info["size_min"][1] = 2.65

                if "Media" in best_group_size and used_back_wall_media:
                    best_width = best_group_size["Media"][0]
                    new_size_scale_w = best_width / (seed_dict[jid]["size"][0]/100.)

                    for i in group_info["obj_list"]:
                        if i["role"] == "table":
                            i["scale"][0] = new_size_scale_w
                    group_info["size"][0] = seed_dict[jid]["size"][0]/100. * new_size_scale_w
                    group_info["size_min"][0] = seed_dict[jid]["size"][0]/100. * new_size_scale_w

            tv_flag = False
            for obj in group_info["obj_list"]:
                if obj["role"] == "tv":
                    tv_flag = True
                    if obj["normal_position"][1] > 1.5:
                        obj["normal_position"][1] = 1.5

            if not used_back_wall_media and not tv_flag:
                get_default_tv(group_info, best_group_size)

    # 修复Dining
    for group_info_idx in range(len(layout_room_sample["layout_sample"][0]["group"]) - 1, -1, -1):
        group_info = layout_room_sample["layout_sample"][0]["group"][group_info_idx]
        group_type = group_info["type"]
        if group_type == "Dining":
            for obj in group_info["obj_list"]:
                if obj["role"] == "chair":
                    obj_rot = rot_to_ang(obj["normal_rotation"])
                    cos_ang = math.cos(obj_rot)
                    sin_ang = math.sin(obj_rot)
                    rot_dir = [-sin_ang, cos_ang]

                    obj["normal_position"][0] += rot_dir[0] * 0.05
                    obj["normal_position"][2] += rot_dir[1] * 0.05
            group_info["size"][2] -= 0.1

    # 配饰更新
    for group in layout_room_sample["layout_sample"][0]["group"]:
        sample_group_add_related(group)


def advisor_scheme_refine(layout_scheme, seed_dict):
    group_sample_info = {}
    for jid in seed_dict:
        group_name = seed_dict[jid]["group"]
        group_role = seed_dict[jid]["role"]
        if group_name not in group_sample_info:
            group_sample_info[group_name] = {}
        if group_role not in group_sample_info[group_name]:
            group_sample_info[group_name][group_role] = []
        group_sample_info[group_name][group_role].append(jid)

    # 更新窗帘、work区
    for scheme in layout_scheme["layout_scheme"]:
        for group in scheme['group']:
            group_type = group["type"]
            if group_type == "Window":
                for obj in group["obj_list"]:
                    if obj["size"][0] > 210:
                        obj["scale"][1] += 0.05

            # elif group_type == "Ceiling":
            #     group["position"][1] += 0.10
            #     for obj in group["obj_list"]:
            #         obj["position"][1] += 0.15

            elif group_type == "Work":
                chair = None
                group_rot = rot_to_ang(group["rotation"])
                cos_ang = math.cos(group_rot)
                sin_ang = math.sin(group_rot)
                dir = [0, 1]
                rot_dir = [dir[0] * cos_ang - dir[1] * sin_ang, dir[1] * cos_ang + dir[0] * sin_ang]
                for obj in group["obj_list"]:
                    if obj["role"] == "chair":
                        chair = obj

                if not chair:
                    target_group = get_furniture_group(scheme["source_house"], scheme["source_room"], "Work")
                    for target_obj in target_group["obj_list"]:
                        if target_obj["role"] == "chair":
                            new_obj = target_obj.copy()
                            new_obj["position"][0] = group["position"][0] + rot_dir[0] * new_obj["normal_position"][0]
                            new_obj["position"][2] = group["position"][2] + rot_dir[1] * new_obj["normal_position"][
                                2] * 0.9
                            new_obj["rotation"] = group["rotation"].copy()
                            group["obj_list"].append(new_obj)

            elif group_type == "Media":
                group_sample_info_media = group_sample_info["Media"] if "Media" in group_sample_info else {}
                if "table" not in group_sample_info_media or len(group_sample_info_media["table"]) == 0:
                    continue
                else:
                    used_back_wall_media = False
                    for jid in group_sample_info_media["table"]:
                        if jid in seed_dict and seed_dict[jid]["size"][1] > 150 and seed_dict[jid]["size"][0] > 230:
                            used_back_wall_media = True

                    if used_back_wall_media:
                        for obj_idx in range(len(group["obj_list"]) - 1, -1, -1):
                            obj_info = group["obj_list"][obj_idx]
                            if obj_info['role'] == "tv":
                                group["obj_list"].pop(obj_idx)

        for group_idx in range(len(scheme['group'])-1, -1, -1):
            if scheme['group'][group_idx]["type"] == "Appliance":
                scheme['group'].pop(group_idx)
