import json

from Extract.extract_cache import get_house_data, get_house_sample


_, house_data = get_house_data("489c410c-f01c-431a-b4f3-30368d066fea",
                               design_url="https://jr-prod-cms-assets.oss-cn-beijing.aliyuncs.com/design/2021-11-03/json/87b45b4f-4bc0-47c8-b2a8-657a130f025b.json",
                               scene_url="https://jr-prod-cms-assets.oss-cn-beijing.aliyuncs.com/Asset/489c410c-f01c-431a-b4f3-30368d066fea/v1635927588/scene.json")

sample_para, sample_data, sample_layout, sample_group = get_house_sample("489c410c-f01c-431a-b4f3-30368d066fea", reload=True)


# print()


def check_normal_p(obj, furniture_list):
    out_obj = []
    p = [obj["position"][0], obj["position"][2]]
    half_size = [obj["size"][0] * obj["scale"][0] / 200. * 1.05, obj["size"][2]*obj["scale"][2] / 200.* 1.05]

    if abs(obj["rotation"][1]) > 0.5 and abs(obj["rotation"][1]) < 0.8:
        half_size = [half_size[1], half_size[0]]

    main_aabb = [[p[0] - half_size[0], p[1] - half_size[1]], [p[0] + half_size[0], p[1] + half_size[1]]]

    for target_obj in furniture_list:
        if target_obj["id"] == obj["id"]:
            continue

        now_p = [target_obj["position"][0], target_obj["position"][2]]
        now_half_size = [target_obj["size"][0]*target_obj["scale"][0] / 200., target_obj["size"][2]*target_obj["scale"][2] / 200.]
        if abs(target_obj["rotation"][1]) > 0.5 and abs(target_obj["rotation"][1]) < 0.8:
            now_half_size = [now_half_size[1], now_half_size[0]]
        now_aabb = [[now_p[0] - now_half_size[0], now_p[1] - now_half_size[1]],
                    [now_p[0] + now_half_size[0], now_p[1] + now_half_size[1]]]
        if main_aabb[0][0] < now_aabb[0][0] and now_aabb[1][0] < main_aabb[1][0] and main_aabb[0][1] < now_aabb[0][
            1] and now_aabb[1][1] < main_aabb[1][1]:
            out_obj.append(target_obj)
    return out_obj


temp = {
    "id": "",
    "related_list": [
        {
            "id": "",
            "normal_pos": "",
            "normal_rotation": "",
            "scale": ""
        }
    ]
}

out_all_obj = {}


def get_related_info(obj, target_obj):
    normal_p = [target_obj["position"][0] - obj["position"][0], target_obj["position"][1] - obj["position"][1],
                target_obj["position"][2] - obj["position"][2]]
    return {
        "id": target_obj["id"],
        "normal_position": normal_p,
        "normal_rotation": target_obj["rotation"].copy(),
        "scale": target_obj["scale"].copy()
    }


for room in sample_data["room"]:
    furniture_list = room["furniture_info"]
    for obj in furniture_list:
        if obj["id"] != "929bf844-ab25-4eb6-a630-845c6a76480b":
            continue
        if obj["size"][0] > 0.5:
            main_pos = obj["position"]
            out_obj_list = check_normal_p(obj, furniture_list)
            if out_obj_list:
                related_list = []
                for target_obj in out_obj_list:
                    related_list.append(get_related_info(obj, target_obj))
                if len(related_list) > 0:
                    out_all_obj[obj["id"]] = related_list

# with open("save_related_info.json", "w") as f:
#     f.write(json.dumps(out_all_obj))
