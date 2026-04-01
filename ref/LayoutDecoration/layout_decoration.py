"""
@Author:
@Date:
@Description:

"""
import json
from LayoutDecoration.recon_main import house_recon_pipeline

# 功能测试
if __name__ == '__main__':
    input_json = json.load(open('/Users/liqing.zhc/code/HardDecorate/LayoutDecoration/test.json', 'r'))
    # 组装house_data 兼容room_data 构建mesh
    if 'house_data' not in input_json:
        if 'room_data' not in input_json:
            # return {}, {}
            house_data = {}
            exit(0)
        else:
            house_data = {'id': '', 'room': [input_json['room_data']]}
    else:
        house_data = input_json['house_data']
    # 风格提取
    if 'style' in input_json:
        jr_style = input_json['style']
    else:
        jr_style = ''

    # 组装全屋软装 兼容单屋
    if 'house_layout' in input_json:
        house_layout = input_json['house_layout']
    else:
        if 'room_layout' in input_json and input_json['room_layout']:
            house_layout = {input_json['room_layout']['type'] + '-0': input_json['room_layout']}
        else:
            house_layout = ''

    # 商品信息
    sell_info = {}
    if 'sell_info' in input_json:
        sell_info = input_json['sell_info']

    house, scene = house_recon_pipeline(house_data, house_layout, jr_style, {}, sell_info)
    scene_data = scene.write_scene_json()
    json.dump(scene_data, open('./scene.json', 'w'))
    house.get_scene_info()
