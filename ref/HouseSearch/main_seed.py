from Furniture.furniture import get_furniture_data
from HouseSearch.seed.role import get_furniture_roles_info


# 请求硬装搭配生成v1.0 找主家具
def get_room_main_furniture_seeds(furniture_seeds_info):
    furniture_main_seeds_info = {}
    for source_room_id in furniture_seeds_info:
        room_type = source_room_id.split('-')[0]

        if source_room_id in furniture_seeds_info:
            furniture_seeds_role_list = get_furniture_roles_info(furniture_seeds_info[source_room_id], room_type)
            if len(list(furniture_seeds_role_list.keys())) == 1:
                for jid in furniture_seeds_role_list:
                    furniture_main_seeds_info[source_room_id] = furniture_seeds_role_list[jid]
            else:
                for jid in furniture_seeds_role_list:
                    if "main" in furniture_seeds_role_list[jid] and furniture_seeds_role_list[jid]['main']:
                        furniture_main_seeds_info[source_room_id] = furniture_seeds_role_list[jid]
                        break

            # 没有种子家具、使用原种子家具
            # if source_room_id not in furniture_main_seeds_info:
            #     for group in sample_info['sample'][source_room_id]['layout_scheme'][0]['group']:
            #         if room_type in ["LivingDiningRoom", "LivingRoom"]:
            #             if group['type'] == "Meeting":
            #                 furniture_main_seeds_info[source_room_id] = group['obj_main']
            #         elif room_type in ["Bedroom", "MasterBedroom", "SecondBedroom"]:
            #             if group['type'] == "Bed":
            #                 furniture_main_seeds_info[source_room_id] = group['obj_main']

    return furniture_main_seeds_info


# 单group输入
def get_group_main_furniture_seeds(obj_list):
    for object_one in obj_list:
        object_id = object_one['id']
        if object_one['role'] == "bed":
            return object_id
        elif object_one['role'] == "sofa":
            return object_id

    return ""


def check_need_hard_type(room_material, need_hard_type_list):
    out_info = {}
    for floor_mat in room_material['floor']:
        obj_type, obj_style_en, obj_size = get_furniture_data(floor_mat['jid'])
        if obj_type in need_hard_type_list and len(need_hard_type_list[obj_type]["replace_id"]) == 0:
            need_hard_type_list[obj_type] = {"replace_id": floor_mat['jid'], "contentType": obj_type}

    for wall_mat in room_material['wall']:
        obj_type, obj_style_en, obj_size = get_furniture_data(wall_mat['jid'])
        if obj_type in need_hard_type_list and len(need_hard_type_list[obj_type]["replace_id"]) == 0:
            need_hard_type_list[obj_type] = {"replace_id": wall_mat['jid'], "contentType": obj_type}




