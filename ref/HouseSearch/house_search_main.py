import time
import numpy as np
from Extract.extract_cache import get_house_sample
from HouseSearch.group.armoire_group import generate_armoire_group
from HouseSearch.group_sample_search import house_room_zone_search_group_info
from HouseSearch.house_propose import check_room_type_same
from HouseSearch.house_search import house_search_sample_keys_list, get_sample_data_from_house_sample_keys, \
    house_search_sample_keys_list_with_seeds
from HouseSearch.house_seed import extract_input_seeds_info, \
    update_room_layout_material_seed, get_furniture_seeds_service_room_data

# import GroupBasedHouseSearch.merge_group as group_replace_module
from HouseSearch.house_style import get_furniture_list_target_style
from LayoutGroup.GroupBasedHouseSearch.merge_group import merge

group_role_not_recommend_map = {
    "LivingDiningRoom": ["Meeting", "Dining", "Cabinet", "Media", "Wall", "Ceiling", "Window"],
    "LivingRoom": ["Meeting", "Dining", "Cabinet", "Media", "Wall", "Ceiling", "Window"],
    "DiningRoom": ["Dining", "Cabinet", "Media", "Wall", "Ceiling", "Window"],
    "MasterBedroom": ["Bed", "Armoire", "Cabinet", "Media", "Wall", "Ceiling"],
    "Bedroom": ["Bed", "Armoire", "Cabinet", "Media", "Wall", "Ceiling"],
    "SecondBedroom": ["Bed", "Armoire", "Cabinet", "Media", "Wall", "Ceiling"],
    "ElderlyRoom": ["Bed", "Armoire", "Cabinet", "Media", "Wall", "Ceiling"],
    "KidsRoom": ["Bed", "Armoire", "Cabinet", "Media", "Wall", "Ceiling"]
}


def change_type(room_type):
    if room_type in ["LivingDiningRoom", "LivingRoom", "DiningRoom"]:
        return "LivingDiningRoom"
    if room_type in ["MasterBedroom", "Bedroom", "SecondBedroom"]:
        return "Bedroom"
    return room_type


def check_room_group_role(room_type, group, role):
    if group == "" or role == "":
        code = "LAYOUT_ALGO_SEED_ROLE_MAP_ERROR"
    elif room_type in group_role_not_recommend_map and group not in group_role_not_recommend_map[room_type]:
        code = "LAYOUT_ALGO_SEED_ROLE_NOT_RECOMMEND"
    else:
        code = ""

    return code


def check_room_seed(house_data, room_seed, seed_info):
    room_type_map = {}
    for room_data in house_data["room"]:
        room_type_map[room_data["id"]] = room_data["type"]

    return_map = {}
    for room_id in room_seed:
        if room_id in room_type_map:
            room_type = room_type_map[room_id]
        else:
            continue

        for jid in room_seed[room_id]:
            if jid in seed_info:
                group = seed_info[jid]["group"]
                role = seed_info[jid]["role"]
                return_map[jid] = check_room_group_role(room_type, group, role)

    return return_map


def extract_recommend_samples(seeds_info, house_data):
    out_sample_list = {}
    self_trans_list = {}
    room_type_table = {}
    for room in house_data["room"]:
        room_type_table[room["id"]] = room["type"]

    for room_id in seeds_info:
        now_room_type = room_type_table[room_id]
        if "self_transfer" in seeds_info[room_id]:
            for sample_idx, sample_id in enumerate(seeds_info[room_id]["self_transfer"]):
                if sample_idx not in out_sample_list:
                    out_sample_list[sample_idx] = {}
                    self_trans_list[sample_idx] = {}
                out_sample_list[sample_idx][room_id] = sample_id

                # 找到对应的房间/如果replace_info的room_id不在self_trans里面, 那随机返回一个
                if "_" not in sample_id:
                    _, _, sample_layout, sample_group = get_house_sample(sample_id)
                    for sample_room_id in sample_group:
                        if sample_room_id == room_id:
                            out_sample_list[sample_idx][room_id] = sample_id + "_" + sample_room_id

                    if "_" not in out_sample_list[sample_idx][room_id]:
                        for sample_room_id in sample_group:
                            if check_room_type_same(sample_group[sample_room_id]["room_type"], now_room_type):
                                if len(sample_group[sample_room_id]["group_functional"]) > 0:
                                    out_sample_list[sample_idx][room_id] = sample_id + "_" + sample_room_id

                self_trans_list[sample_idx][room_id] = True

        if "sample" in seeds_info[room_id]:
            for sample_idx, sample_id in enumerate(seeds_info[room_id]["sample"]):
                if "_" not in sample_id:
                    continue

                items = sample_id.split('_')
                source_house_id = items[0]
                source_room_id = ""
                self_t = False
                if len(items) > 1:
                    source_room_id = items[1]
                if len(items) > 2:
                    self_t = items[2]
                    self_t = "self" in self_t

                if sample_idx not in out_sample_list:
                    out_sample_list[sample_idx] = {}
                    self_trans_list[sample_idx] = {}

                out_sample_list[sample_idx][room_id] = source_house_id + "_" + source_room_id
                self_trans_list[sample_idx][room_id] = self_t

    return out_sample_list, self_trans_list


# 全屋方案检索主入口
def house_search_get_sample_info(house_data, seeds_info={}, seeds_note={}, sample_num=3, target_style='random',
                                 sample_seed_replace_flag=True):
    hard_replace_flag = False
    # target_style = 目前风格
    # target_style = 'random'
    # target_style = 'all'
    # 获取主材、软装种子
    furniture_room_seeds_info, furniture_seeds_note, material_seeds_info = extract_input_seeds_info(seeds_info,
                                                                                                    seeds_note,
                                                                                                    house_data)

    # 自迁移
    recommend_samples, self_trans = extract_recommend_samples(seeds_info, house_data)

    # 模型风格确认 现在只根据软装风格查找样板间
    if furniture_seeds_note:
        target_style = get_furniture_list_target_style(furniture_seeds_note)[0]
    elif material_seeds_info:
        target_style = get_furniture_list_target_style(seeds_note)[0]
    elif target_style == "seed":
        target_style = get_furniture_list_target_style(furniture_seeds_note)[0]

    # 保证可以放置在户型中的软装方案
    if furniture_room_seeds_info:
        house_sample_list = house_search_sample_keys_list_with_seeds(house_data, target_style=target_style,
                                                                     sample_num=sample_num,
                                                                     seeds=furniture_room_seeds_info,
                                                                     seeds_role_notes=furniture_seeds_note)
    else:
        if len(material_seeds_info):
            # 主材放我家匹配，选择主材rgb近似的样板间
            mat_sample_num = max(10, sample_num)
            house_sample_list = house_search_sample_keys_list(house_data, target_style='',
                                                              sample_num=mat_sample_num)
            house_sample_list_with_rgb = []
            for sample in house_sample_list:
                house_dis = 0
                if 'mat_vec' not in sample:
                    house_dis = 255 * 2.
                else:
                    for room_id, mat_info in material_seeds_info.items():
                        for k, mat_jid in mat_info.items():
                            if mat_jid[0] not in seeds_note:
                                continue
                            mat_vec = np.array(seeds_note[mat_jid[0]]['rgb'])
                            if room_id in sample['mat_vec']:
                                target_rgb = sample['mat_vec'][room_id][k]
                                if k in mat_vec and isinstance(mat_vec[0], list) and isinstance(target_rgb[k], list):
                                    house_dis += 255.
                                else:
                                    if len(mat_vec) < 3 and len(target_rgb) < 3:
                                        house_dis += 255
                                    else:
                                        house_dis += np.mean(np.abs(mat_vec[:3] - target_rgb[:3]))
                            else:
                                house_dis += 255.
                house_sample_list_with_rgb.append([sample, house_dis])
            house_sample_list_with_rgb.sort(key=lambda x: x[-1])
            house_sample_list = [i[0] for i in house_sample_list_with_rgb][:sample_num]
        else:
            house_sample_list = house_search_sample_keys_list(house_data, target_style=target_style,
                                                              sample_num=sample_num)
    # t方案替换
    if recommend_samples:
        for sample_idx, sample_one in enumerate(house_sample_list):
            if sample_idx >= len(recommend_samples):
                continue

            target_sample_keys = recommend_samples[sample_idx]
            for target_room_id in target_sample_keys:
                if target_room_id in sample_one["sample"]:
                    sample_one["sample"][target_room_id] = target_sample_keys[target_room_id]

    # 生成软装方案详细信息
    sample_info_list = []
    for sample_keys_info in house_sample_list:
        sample_info_list.append(get_sample_data_from_house_sample_keys(sample_keys_info))

    # 种子替换
    if material_seeds_info or furniture_room_seeds_info or self_trans:
        for sample_idx, sample_info in enumerate(sample_info_list):
            # 是否自迁移
            if sample_idx not in self_trans:
                now_tans = {}
            else:
                now_tans = self_trans[sample_idx]

            sample_info["info"]["seed_info"] = furniture_seeds_note
            sample_info["info"]["seed_flag"] = check_room_seed(house_data, furniture_room_seeds_info,
                                                               furniture_seeds_note)

            # 自迁移
            for base_room_id in seeds_info:
                if base_room_id not in sample_info['sample']:
                    continue
                if "material" in sample_info['sample'][base_room_id]['layout_scheme'][0]:
                    if base_room_id not in now_tans:
                        continue
                    sample_info['sample'][base_room_id]['layout_scheme'][0]["material"]["self_transfer"] = now_tans[base_room_id]

            # # 更新指定硬装种子
            for base_room_id in material_seeds_info:
                if base_room_id not in sample_info['sample']:
                    continue

                update_room_layout_material_seed(sample_info['sample'][base_room_id]['layout_scheme'][0]['material'],
                                                 material_seeds_info[base_room_id], seeds_note)

            # 软装替换微调
            if sample_seed_replace_flag:
                sample_seed_replace_process(sample_info, furniture_room_seeds_info, furniture_seeds_note)

    return sample_info_list


def sample_seed_replace_process(sample_info, furniture_seeds_info, furniture_seeds_note):
    for source_room_id in furniture_seeds_info:
        need_replace_seeds = furniture_seeds_info[source_room_id]
        if source_room_id not in sample_info['sample']:
            continue

        all_sample_groups = sample_info['sample'][source_room_id]['layout_scheme'][0]['group']

        for idx, group in enumerate(all_sample_groups):
            group_type = group["type"]

            seed_replace_dict = {}
            group_seed_info = {}
            # 查找当前房间对应功能区的种子家具
            for seed_jid in need_replace_seeds:
                if seed_jid not in furniture_seeds_note:
                    continue

                if furniture_seeds_note[seed_jid]["group"] == group_type:
                    seed_replace_dict[seed_jid] = ""

            if not seed_replace_dict:
                continue

            # 找种子家具对应的待替换家具jid
            for object_one in group['obj_list']:
                if object_one['role'] not in ['sofa', 'table', 'side table', 'cabinet', 'side table',
                                              'chair', 'bed', 'armoire']:
                    continue
                for seed in seed_replace_dict:
                    if len(seed_replace_dict[seed]) == 0 and \
                            object_one['role'] == furniture_seeds_note[seed]["role"]:
                        seed_replace_dict[seed] = object_one["id"]
                    group_seed_info[seed] = furniture_seeds_note[seed].copy()

            # 进行替换
            if group["type"] == "Armoire":
                all_sample_groups[idx] = generate_armoire_group(group, group_seed_info, seed_replace_dict)
            else:
                all_sample_groups[idx] = merge(group, group_seed_info, seed_replace_dict)


# 全屋方案检索region_info检索
def house_zone_search_get_sample_info(house_data, sample_num=3):
    return house_room_zone_search_group_info(house_data, sample_num)


if __name__ == '__main__':
    from ImportHouse.room_search import get_house_data

    _, house_data = get_house_data("9d74c6b1-3162-4844-91b4-abc8df358892")
    a = time.time()

    sample_list = house_search_get_sample_info(house_data, {}, sample_num=8, target_style="random")
    print()
