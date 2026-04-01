from HouseSearch.group.group_detail import get_cabinet_group_detail_name
from HouseSearch.house_propose import check_sample_group
from ImportHouse.room_search import get_house_sample_layout, extract_house_layout_by_info, add_furniture_group_list, \
    get_house_data


# 解析入口
# 布局模板解析 样板间
def house_search_parse_sample_key(sample_key=''):
    sample_data, design_key, house_key, room_key = {}, '', '', ''
    if len(sample_key) > 0:
        sample_key_set = sample_key.split('_')
        design_key = sample_key_set[0]
        if len(sample_key_set) >= 2:
            house_key = sample_key_set[0]
            room_key = sample_key_set[-1]
        else:
            house_key = sample_key_set[0]
            room_key = ""
    sample_data, sample_layout, sample_group, sample_scene = {}, {}, {}, {}
    # 获取信息
    if len(house_key) > 0:
        sample_layout_old = get_house_sample_layout(house_key)
        # 布局
        if room_key in sample_layout_old:
            sample_layout[room_key] = sample_layout_old[room_key]
        else:
            sample_layout = sample_layout_old
        # 添加
        for room_key, room_val in sample_layout.items():
            scheme_one = {}
            room_type = room_val['room_type']
            if 'layout_scheme' in room_val and len(room_val['layout_scheme']) > 0:
                scheme_one = room_val['layout_scheme'][0]
            group_set_new = []

            if 'group' in scheme_one:
                group_set_old = scheme_one['group']
                all_meetings = []
                max_code = 0
                max_meeting = None
                for group_old_idx in range(len(group_set_old)-1, -1, -1):
                    now_group = group_set_old[group_old_idx]

                    if "obj_type" in now_group and "table/table" in now_group["obj_type"] and now_group["type"] == "Cabinet":
                        now_group["type"] = "Work"
                        for obj_idx in range(len(now_group["obj_list"])-1, -1, -1):
                            if now_group["obj_list"][obj_idx]['role'] == 'cabinet':
                                now_group["obj_list"][obj_idx]['role'] = 'table'

                    if now_group["type"] == "Floor":
                        for obj_idx in range(len(now_group["obj_list"])-1, -1, -1):
                            if now_group["obj_list"][obj_idx]['role'] == 'electronics':
                                now_group["obj_list"].pop(obj_idx)

                    if now_group['type'] == 'Appliance':
                        group_set_old.pop(group_old_idx)

                    # 打组后处理
                    if room_type not in ["Bathroom", "MasterBathroom"]:
                        if now_group['type'] == 'Cabinet':
                            name = get_cabinet_group_detail_name(now_group)
                            if name == "bath_cabinet":
                                group_set_old.pop(group_old_idx)
                                continue

                    check_sample_group(now_group)

                # if max_meeting:
                #    group_set_old.insert(0, max_meeting)

    # 解析信息s
    if len(sample_layout) <= 0:
        house_para, house_data = get_house_data(house_key)
        if 'room' in house_data:
            sample_data = house_data.copy()
            sample_data['id'] = house_key
            sample_data['room'] = []
            for room_one in house_data['room']:
                if len(room_key) <= 0:
                    sample_data['room'].append(room_one)
                elif 'id' in room_one and room_one['id'] == room_key:
                    sample_data['room'].append(room_one)
                    break
            sample_data, sample_layout, sample_group, sample_scene = house_search_parse_sample_data(sample_data)
    # 返回信息
    return sample_data, sample_layout, sample_group, sample_scene


# 布局模板解析
def house_search_parse_sample_data(sample_json):
    sample_data, sample_layout, sample_group, sample_scene = {'id': '', 'room': []}, {}, {}, {}
    if len(sample_json) > 0:
        sample_data, sample_layout, sample_group = extract_house_layout_by_info(sample_json, check_mode=1)
    if len(sample_layout) <= 0:
        sample_data = {}

    return sample_data, sample_layout, sample_group, sample_scene
