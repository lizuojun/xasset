import json
import math
import os

from House.house_save import group_save, get_furniture_data
from layout_group import layout_group_generate, layout_group_decorate, layout_group_param

need_deco_table_keys = ["side_table", "table", "media_table", "bed_media"]

all_used_jid = []
all_files = os.listdir("temp")
for i in all_files:
    if "json" in i and "used" not in i:
        design_id = i.split('_')[0]
        all_used_jid.append(design_id)


def group_save_visual(group_scheme, jid, save_path="./temp/new_data"):
    obj_type, obj_style_en, obj_size = get_furniture_data(jid)
    data = {
        "meta": {
            "version": "0.1",
            "origin": "Floorplan web editor",
            "magic": "171bd2f43d70",
            "unit": "cm"
        },
        "boundingBox": {
            "xLen": obj_size[0],
            "yLen": obj_size[2],
            "zLen": obj_size[1]
        },
        "Products": [
            {"id": jid,
             "position": {
                 "x": 0.0,
                 "y": 0.0,
                 "z": 0
             },
             "rotation": 0.0,
             "scale": {
                 "XScale": 1,
                 "YScale": 1,
                 "ZScale": 1
             },
             "size": [
                 obj_size[0],
                 obj_size[2],
                 obj_size[1]
             ], "role": ""}
        ]
    }
    for scheme in group_scheme:
        for obj in scheme:
            _, _, o_size = get_furniture_data(obj["id"])
            one_item = {"id": obj["id"],
                        "position": {
                            "x": obj["position"][0] * 100.,
                            "y": obj["position"][1] * 100.,
                            "z": obj["position"][2] * 100.
                        },
                        "rotation": obj["rotation"][1],
                        "scale": {
                            "XScale": obj["scale"][0],
                            "YScale": obj["scale"][1],
                            "ZScale": obj["scale"][2]
                        },
                        "size": [
                            o_size[0],
                            o_size[2],
                            o_size[1],
                        ],"role":""}
            data["Products"].append(one_item)

    with open(save_path+"/"+jid+"_group.json", "w") as f:
        f.write(json.dumps(data))


def extract_table_info():
    all_table = json.load(open("../source/table.json"))
    for room_style in all_table["form_options"]:
        all_furnish = all_table["form_options"][room_style]["furnishing"]
        for item in all_furnish["items"]:
            for sub_items in item["items"]:
                key = sub_items["key"]
                for model in sub_items["model_list"]:
                    jid = model["id"]
                    if jid in all_used_jid:
                        continue

                    obj_type, obj_style_en, obj_size = get_furniture_data(jid)
                    obj_size[2], obj_size[1] = obj_size[1], obj_size[2]
                    if key in need_deco_table_keys:
                        if "Bedroom" in room_style:
                            data = {
                                "plat_id": jid,
                                "layout_number": 1,
                                "room_id": "Bedroom-516",
                                "propose_number": 1,
                                "layout_mode": 20,
                                "room_data": {
                                    "id": "Bedroom-516",
                                    "type": "Bedroom",
                                    "style": "country",
                                    "area": 23.422513628412,
                                    "furniture_info": [
                                        {
                                            "id": jid,
                                            "type": obj_type,
                                            "style": "北欧",
                                            "size": obj_size,
                                            "scale": [1, 1, 1],
                                            "position": [0, 0, 0],
                                            "rotation": [0, 0, 0]
                                        }
                                    ]
                                }
                            }
                        else:
                            data = {
                                "plat_id": jid,
                                "layout_number": 1,
                                "room_id": "LivingDiningRoom-516",
                                "propose_number": 1,
                                "layout_mode": 20,
                                "room_data": {
                                    "id": "LivingDiningRoom-516",
                                    "type": "LivingDiningRoom",
                                    "style": "country",
                                    "area": 23.422513628412,
                                    "furniture_info": [
                                        {
                                            "id": jid,
                                            "type": obj_type,
                                            "style": "北欧",
                                            "size": obj_size,
                                            "scale": [1, 1, 1],
                                            "position": [0, 0, 0],
                                            "rotation": [0, 0, 0]
                                        }
                                    ]
                                }
                            }
                        return_data = layout_group_param(data)
                        group_save_visual(return_data["group_scheme"], jid)


def extract_temp_data_to_related_add():
    add_all_map = {}
    for jid in all_used_jid:
        p = json.load(open("./temp/"+jid+"_group.json"))["Products"]
        if len(p) > 0:
            main_data = p[0]
            main_p = [main_data["position"]["x"]/100., main_data["position"]["z"]/100., main_data["position"]["y"]/100.]
            out_add_list = []
            for obj in p[1:]:
                now_p = [obj["position"]["x"] / 100. - main_p[0], obj["position"]["z"] / 100. - main_p[1],
                          obj["position"]["y"] / 100. - main_p[2]]
                rotation = [0, math.sin(obj["rotation"] / 2.), 0, math.cos(obj["rotation"] / 2.)]
                scale = [obj["scale"]["XScale"], obj["scale"]["ZScale"], obj["scale"]["YScale"]]

                out_add_list.append({
                    "id": obj["id"],
                    "normal_position": now_p,
                    "normal_rotation": rotation,
                    "scale": scale
                })
            if len(out_add_list) > 0:
                add_all_map[main_data["id"]] = out_add_list
    return add_all_map


if __name__ == '__main__':
    import json
    add_all_map = extract_temp_data_to_related_add()
    with open("save_related_info_new.json", "w") as f:
        f.write(json.dumps(add_all_map))
