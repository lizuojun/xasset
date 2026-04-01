# -*- coding: utf-8 -*-

from ImportHouse.room_search import *
from Extract.group_material import house_data_group_wall
from Extract.group_win_door import house_data_group_win_door
from Extract.group_feature_wall import house_data_group_feature_wall
from Extract.get_house_data_universal import get_house_data_univ


# 获取单屋方案 TODO:
def search_sample_room(house_id, room_id, room_style='', room_color='', sample_num=1):
    # 查找区域

    # 查找房间
    room_info, room_data = get_room_data(house_id, room_id)
    # 更新样板

    # 返回样板
    pass


# 获取种子方案 TODO:
def search_sample_seed():
    pass


# 方案解析: 扩展支持硬装定制以及自由造型
def extract_sample_house(house_id, design_url='', scene_url='', reload=True):
    try:
        house_para, house_data = get_house_data_univ(house_id, design_url, scene_url, reload=reload, use_service=False)
        sample_para, house_data, sample_layout, sample_group = get_house_sample(house_id, reload=reload)
        if reload:
            house_data = house_data_group_win_door(house_id, house_data, sample_layout, upload=False)
            house_data = house_data_group_wall(house_id, house_data, sample_layout, False)
            house_data = house_data_group_feature_wall(house_id, house_data, sample_layout, True)
    except Exception as e:
        print(e)
        return {}, {}, {}, {}
    # 返回
    return sample_para, house_data, sample_layout, sample_group


# 功能测试
if __name__ == '__main__':
    # 清空缓存
    search_clear_temp()
    # search_fetch_temp()
    pass

    # 户型数据
    target_house_set = [
        '42fb6a2c-168f-45f2-af47-5089d63a8e48'
    ]
    target_house_set = []
    for target_house in target_house_set:
        house_para, house_data = get_house_data_univ(target_house, '', '', reload=True)
    pass

    # 方案数据
    sample_house_set = [
        '019f41a0-49c5-4cfe-a7d1-025c2e1430c8'
    ]
    for sample_house in sample_house_set:
        sample_para, sample_data, sample_layout, sample_group = extract_sample_house(sample_house, reload=True)
    pass

    # 数据保存
    # save_room_sample()
    # save_furniture_data()
    pass
