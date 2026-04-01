from Furniture.furniture import add_furniture_data


#


def refine_living_seeds_note(seed_info):
    pass


def refine_bedroom_seeds_note(seed_info):
    pass
    # for jid in seed_info:
    #     role_info = seed_info[jid]
    #     role = role_info["role"]
    #     group = role_info["group"]
    #     if role == "side table" and group == "Media":
    #         role_info["role"] = "cabinet"
    #         role_info["group"] = "Cabinet"
    #         role_info["type"] = "wardrobe/base wardrobe"
    #         for i in range(3):
    #             if role_info["size"][i] < 21:
    #                 role_info["size"][i] = 21
    #
    #         new_obj_info = {"id": role_info["id"], "style": role_info["style"], "type": "wardrobe/base wardrobe",
    #                         "size": role_info["size"]}
    #         add_furniture_data(role_info["id"], new_obj_info)


def refine_seeds_note(seed_info, room_type="LivingRoom"):
    if room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
        refine_living_seeds_note(seed_info)
    else:
        refine_bedroom_seeds_note(seed_info)
