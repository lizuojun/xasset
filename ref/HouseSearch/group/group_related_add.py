import json
import os

from Furniture.furniture import get_furniture_data

related_info = json.load(open(os.path.join(os.path.dirname(__file__), "new_save_related_info.json"), 'r'))


def get_sample_obj_info(jid):
    obj_type, obj_style_en, obj_size = get_furniture_data(jid)
    return {
        "id": jid,
        "type": obj_type,
        "style": obj_style_en,
        "size": obj_size,
        "scale": [
            1.0,
            1.0,
            1.0
        ],
        "position": [
            0.0,
            0.0,
            0.0,
        ],
        "rotation": [
            0,
            0,
            0,
            1
        ],
        "entityId": "",
        "categories": [
            "8dad7ea1-10bd-4d53-94a9-897a4c851e65"
        ],
        "category": "8dad7ea1-10bd-4d53-94a9-897a4c851e65",
        "role": "accessory",
        "count": 1,
        "relate": "",
        "relate_group": "",
        "relate_position": []
    }


def sample_group_add_related(group):
    new_add_obj_list = []
    if "obj_list" not in group:
        return

    for obj in group["obj_list"]:
        if obj["id"] in related_info:
            used_related_obj_list = related_info[obj["id"]]
            for related_obj in used_related_obj_list:
                obj_info = get_sample_obj_info(related_obj["id"])
                obj_info["normal_position"] = [related_obj["normal_position"][i] + obj["normal_position"][i] for i in range(3)]
                obj_info["scale"] = related_obj["scale"].copy()
                obj_info["normal_rotation"] = related_obj["normal_rotation"].copy()
                new_add_obj_list.append(obj_info)

    group["obj_list"] += new_add_obj_list
