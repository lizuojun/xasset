from Furniture.furniture import get_furniture_data_more

BATH_CABINET = {
        "64880d8a-9a44-4d0e-b704-e29903b718da": "浴室柜/主柜",
        "a76de286-1ce2-4c63-ae84-0201e1c68015": "浴室柜/边柜",
        "788625f2-f9c6-423b-a799-a49aa8412b18": "浴室柜/镜柜",
        "c36cc781-8d4f-496e-a10c-2a19d96317f3": "浴室柜/侧柜",
        "84fa847a-86d0-43ad-9ba1-d31fd3e58fb8": "浴室柜/高柜",
        "7b7d75de-673e-4888-b9f5-c314858a8d95": "浴室柜/地柜",
        "87de0e2d-8542-4f5d-bb37-5726dbee695b": "浴室柜",
        "bb477a34-dd3c-4f55-bdde-ce371d3c9bce": "浴室柜组合",
        "5e93a4a0-fbeb-442a-ae3a-442e004d9575": "浴室镜"
    }


def get_cabinet_group_detail_name(group_one):
    main_obj_jid = group_one['obj_main']

    # 检查浴室柜
    if group_one['obj_type'] in ["basin/floor-based single basin with cabinet"]:
        return "bath_cabinet"
    _, _, _, _, _, cate_id = get_furniture_data_more(main_obj_jid)
    if cate_id in BATH_CABINET:
        return "bath_cabinet"

    return ""
