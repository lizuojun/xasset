from ImportHouse.room_search import *
from LayoutDecoration.recon_main import house_recon_pipeline


def layout_group_extract_once(design_id):
    design_id = design_id.rstrip()
    print('group house:', design_id)
    try:
        # house_data = house_design_trans(design_id)
        house_para, house_data = get_house_data(design_id)
        if 'room' in house_data and len(house_data['room']) > 0:
            pass
        else:
            house_id_new, house_data_new, house_feature_new = get_house_data_feature(design_id, True)
            house_data = house_data_new
        house_data_info, house_layout_info, house_group_info = group_house(house_data)
        return house_data_info, house_layout_info
    except Exception as e:
        print('layout group error.')
        print(e)


if __name__ == '__main__':
    design_id = '123b2f26-665b-41f0-afe4-4196d3d9fdd0'
    design_id = '026c0291-be67-4072-94b6-c960e404b33c'
    # design_id = '870c6e14-5d7f-42ff-9060-1a6ebd25a109'
    # design_id = '9043756c-8230-4e73-8a31-de94982ab69a'
    house_data, layout_info = layout_group_extract_once(design_id)

    build_mode = {
        'mesh': False,
        'customized_ceiling': False,
        'win_door': False,
        'mat': False,
        'floor_line': False,
        'bg_wall': False,
        'kitchen': False,
        'light': True,
        'debug': True
    }
    house_info, scene = house_recon_pipeline(house_data, layout_info, style='Modern', build_mode=build_mode)

    # 生成scene json
    house_scene = scene.write_scene_json()
