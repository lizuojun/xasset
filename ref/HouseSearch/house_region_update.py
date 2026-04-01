import math

from Extract.extract_cache import GROUP_TYPE_MAIN, GROUP_TYPE_REST, get_house_data, get_house_sample, rot_to_ang
from HouseSearch.put_home_sample_search import refine_region_info
from ImportHouse.room_search import search_advice_house


def template_update_house_data_region(house_id, house_data):
    # 使用house_id对应的方案区域
    sample_para, sample_data, sample_layout, sample_group = get_house_sample(house_id)
    for room_data in house_data["room"]:
        room_id = room_data["id"]
        region_info = []
        for target_room_id in sample_layout:
            if target_room_id == room_id and sample_layout[target_room_id]["layout_scheme"]:

                for group in sample_layout[target_room_id]["layout_scheme"][0]["group"]:
                    if group["type"] in ["Meeting", "Dining", "Media", "Bed", "Armoire", "Work", "Cabinet", "Bath",
                                         "Rest"]:
                        one_region = {
                            "type": group["type"],
                            "size": group["size"][:],
                            "scale": [1., 1., 1.],
                            "position": group["position"][:],
                            "rotation": group["rotation"][:],
                            "zone": ""
                        }
                        if "table/table" in group["obj_type"] and group["type"] == "Cabinet":
                            one_region["type"] = "Work"

                        if "zone" in group:
                            one_region["zone"] = group["zone"]
                        if "scale" in group:
                            one_region["scale"] = group["scale"]
                        region_info.append(one_region)
        refine_region_info(room_data, region_info)
        if region_info:
            room_data["region_info"] = region_info


def cnn_update_house_data_region(house_id, house_data):
    # 使用网络结果
    from LayoutByCNN.layout_by_cnn_main import house_layout_sample_by_CNN
    house_layout_sample_by_CNN(house_data)
    return house_data


def advice_update_house_data_region(house_id, house_data):
    # 使用预布局
    for room_data in house_data["room"]:
        if "region_info" in room_data:
            room_data["region_info"] = []

    _, sample_layout, house_propose_info = search_advice_house(house_data)
    for room_data in house_data["room"]:
        room_id = room_data["id"]

        if room_data["type"] not in ["LivingDiningRoom", "LivingRoom", "DiningRoom", "Bedroom", "SecondBedroom",
                                     "MasterBedroom"]:
            continue
        region_info = []

        for target_room_id in sample_layout:
            if target_room_id == room_id and sample_layout[target_room_id]["layout_scheme"]:

                for group in sample_layout[target_room_id]["layout_scheme"][0]["group"]:
                    if group["type"] in ["Meeting", "Dining", "Media", "Bed", "Armoire", "Work", "Cabinet", "Bath",
                                         "Rest"]:
                        group_size = group["size"]
                        size_w_d = 0
                        size_h_d = 0

                        # if group["type"] in ["Meeting", "Dining", "Media", "Work", "Cabinet",
                        #                      "Rest"]:
                        #     size_w_d -= 0.2
                        #
                        # if group["type"] in ["Meeting", "Dining", "Work", "Rest"]:
                        #     size_w_d -= 0.2
                        #     size_h_d -= 0.2

                        group_size[0] += size_w_d
                        group_size[2] += size_h_d

                        zone_ang = rot_to_ang(group["rotation"])

                        if group["type"] in ["Meeting", "Work", "Rest"]:
                            group["position"][0] += math.sin(zone_ang) * size_h_d/2.
                            group["position"][2] += math.cos(zone_ang) * size_h_d/2.

                        if 'regulation' in group:
                            group_regulate = group['regulation'][:]
                        else:
                            group_regulate = [0.0, 0.0, 0.0, 0.0]
                        if 'neighbor_best' in group:
                            group_neighbor = group['neighbor_best'][:]
                        else:
                            group_neighbor = [0.0, 0.0, 0.0, 0.0]

                        # 调整尺寸
                        one_region = {
                            "type": group["type"],
                            "size": group["size"][:],
                            "scale": [1., 1., 1.],
                            "position": group["position"][:],
                            "rotation": group["rotation"][:],
                            "zone": ""
                        }
                        if "table/table" in group["obj_type"] and group["type"] == "Cabinet":
                            one_region["type"] = "Work"

                        if "zone" in group:
                            one_region["zone"] = group["zone"]
                        if "scale" in group:
                            one_region["scale"] = group["scale"]
                        region_info.append(one_region)
        refine_region_info(room_data, region_info)
        if region_info:
            room_data["region_info"] = region_info
