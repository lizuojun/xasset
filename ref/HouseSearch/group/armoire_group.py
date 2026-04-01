def generate_armoire_group(group, group_seed_info, seed_replace_dict):
    armoire_data = None
    for key in group_seed_info:
        if group_seed_info[key]["group"] == "Armoire":
            armoire_data = group_seed_info[key]
    if armoire_data:
        group["size"] = [i/100. for i in armoire_data["size"]]
        group["size"][1] = 2.65
        group["size_min"][1] = group["size"][1]
        group["obj_main"] = armoire_data["id"]
        group["obj_type"] = armoire_data["type"]
        for obj in group["obj_list"]:
            if obj["role"] == "armoire":
                obj["id"] = armoire_data["id"]
                obj["type"] = armoire_data["type"]
                obj["style"] = armoire_data["style"]
                obj["size"] = armoire_data["size"].copy()
                if obj["size"][1] > 265:
                    obj["scale"][1] = 265 / float(obj["size"][1])

    return group

