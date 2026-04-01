# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2020-12-30
@Description: 房间方案绘制

"""

from ImportHouse.room_search import *


# 户型方案绘制
def search_update_draw(source_list=[], target_list=[], sample=True):
    if len(source_list) <= 0 and sample:
        source_list = get_source_list()
    if len(target_list) <= 0 and not sample:
        target_list = get_target_list()
    # 样板间
    for source_idx, source_key in enumerate(source_list):
        if source_idx == 0:
            print()
        if source_idx % 10 == 0:
            print('frame house source %04d' % source_idx)
        # 获取
        house_para, house_data = get_house_data(source_key)
        sample_para, sample_data, sample_layout, sample_group = get_house_sample(source_key)
        room_list = []
        if 'room' in house_data:
            room_list = house_data['room']
        for room_idx, room_one in enumerate(room_list):
            room_key, room_type, room_style, room_area, room_height = '', '', '', 0, 0
            if 'id' in room_one:
                room_key = room_one['id']
            if 'type' in room_one:
                room_type = room_one['type']
            if 'style' in room_one:
                room_style = room_one['style']
            if 'area' in room_one:
                room_area = room_one['area']
            if 'height' in room_one:
                room_height = room_one['height']
            if len(room_key) <= 0:
                continue
            if room_type in ROOM_TYPE_LEVEL_1 or room_type in ROOM_TYPE_LEVEL_2:
                pass
            else:
                continue
            room_layout = {}
            if room_key in sample_layout:
                room_layout = sample_layout[room_key]
            if len(room_layout) <= 0:
                continue
            # 解析
            room_data = copy.deepcopy(room_one)
            # 纠正
            correct_room_point(room_data)
            correct_room_link(room_data)
            frame_data = {
                'id': source_key + '_' + room_key, 'style': room_style, 'height': room_height,
                'room': [room_data]
            }
            frame_layout = {room_key: room_layout}
            # 绘制
            save_dir = DATA_DIR_IMPORT_SAMPLE
            save_key = '%s_%s' % (source_key, room_key)
            house_save(save_key, '', 0, 0,
                       frame_data, frame_layout, {},
                       save_key, save_dir, [SAVE_MODE_FRAME],
                       suffix_flag=False, sample_flag=True, upload_flag=False)
            # 上传
            save_file = save_key + '.png'
            save_path = os.path.join(save_dir, save_file)
            if os.path.exists(save_path):
                oss_upload_file('sample_image' + '/' + save_file, save_path, 'ihome-alg-layout')
    # 空户型
    for target_idx, target_key in enumerate(target_list):
        if target_idx == 0:
            print()
        if target_idx % 10 == 0:
            print('frame house target %04d' % target_idx)
        # 获取

        # 绘制

        # 上传

        pass
    return source_list, target_list


# 功能测试
if __name__ == '__main__':
    search_update_draw(['f738d550-6edb-4653-b580-4a04b6560a4e'])
    pass
