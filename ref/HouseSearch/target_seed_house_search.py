import time, json, os
from collections import Counter

from Extract.extract_cache import get_room_data, get_house_data, oss_upload_json, save_furniture_data, \
    get_furniture_data_more, add_furniture_type, add_furniture_data, correct_house_data
from House.house_scene_build import house_build_house
from HouseSearch.house_propose import compute_role_vector_sim
from HouseSearch.house_search import compute_room_role_vector, get_sample_data_from_house_sample_keys
from HouseSearch.house_search_main import house_search_get_sample_info, check_room_seed, sample_seed_replace_process
from HouseSearch.house_seed import extract_input_seeds_info
from HouseSearch.house_style import change_base_style, get_furniture_list_target_style
from HouseSearch.util import get_http_data_from_url
from layout import layout_room_by_sample
from layout_sample_analyze import view_house, layout_sample_camera

target_house_room = {
    "LivingRoom": [
        "7a9571e6-0b7d-41bb-a585-6b4319bf6385_LivingDiningRoom-1250",  # 22 origin_1
        # "2b97206e-8767-4beb-89c7-721fd333f138_LivingRoom-1590",  # 29 origin_2
        "30f1dafd-b408-4ae4-8004-ba41d0f2b7a5_LivingRoom-2098",  # origin_3
        "5d12f045-8829-44ec-840f-ed645f837be3_LivingRoom-2169",  # 37 origin_4
        "6ba46ef8-3fea-4d0c-8383-08024338e0c5_LivingRoom-2506",  # 40 origin_5
        "2b52b376-8ffe-43ab-bcc5-ed8d0e402da9_LivingRoom-17995",  # 45 origin_6
        "9febe749-9f93-4bc6-9db4-aed04d4e713e_LivingDiningRoom-1938"  # 54
    ],
    "Bedroom": [
        "6ba46ef8-3fea-4d0c-8383-08024338e0c5_Bedroom-8430",  # 11
        "2b52b376-8ffe-43ab-bcc5-ed8d0e402da9_Bedroom-23558",  # 17
        "dd9ef9d2-5135-4a67-a2d7-89ec57672bad_MasterBedroom-1196",  # 19
        "dd9ef9d2-5135-4a67-a2d7-89ec57672bad_Bedroom-16220"  # 28
    ]
}

origin_base_id_change = {
    "7a9571e6-0b7d-41bb-a585-6b4319bf6385_LivingDiningRoom-1250": "origin_1",
    "30f1dafd-b408-4ae4-8004-ba41d0f2b7a5_LivingRoom-2098": "origin_3",
    "2b97206e-8767-4beb-89c7-721fd333f138_LivingRoom-1590": "origin_2",
    "5d12f045-8829-44ec-840f-ed645f837be3_LivingRoom-2169": "origin_4",
    "6ba46ef8-3fea-4d0c-8383-08024338e0c5_LivingRoom-2506": "origin_5",
    "2b52b376-8ffe-43ab-bcc5-ed8d0e402da9_LivingRoom-17995": "origin_6",
    "9febe749-9f93-4bc6-9db4-aed04d4e713e_LivingDiningRoom-1938": "origin_7"
}

source_living_base_scheme = json.load(
    open(os.path.join(os.path.dirname(__file__), "source/living_dict.json"), 'r'))["base"]


def extract_target_house_room():
    from Demo.test_local import get_design_json_daily

    for i in target_house_room["LivingRoom"]:
        design_url = get_design_json_daily(i)

        _, house_data = get_house_data(i, design_url)

        for room_data in house_data["room"]:
            if room_data["type"] in ["LivingDiningRoom", "LivingRoom"]:
                pass


# dd9ef9d2-5135-4a67-a2d7-89ec57672bad
def get_house_info(house_id, room_id):
    room_para, room_data = get_room_data(house_id, room_id)
    return {"id": "test_id", "room": [room_data]}


def house_search_base_target(house_id, room_id, house_data, replace_more, sample_num=1, set_scheme=None):
    room_key = house_id + "_" + room_id
    if room_key in origin_base_id_change:
        # raise Exception("wrong source room_data!, %s" % room_key)
        source_key = origin_base_id_change[room_key]
    else:
        source_key = "origin_5"

    furniture_room_seeds_info, furniture_seeds_note, material_seeds_info = extract_input_seeds_info(replace_more,
                                                                                                    {},
                                                                                                    house_data)

    target_style_list = get_furniture_list_target_style(furniture_seeds_note)

    room_data_info = {}
    for room in house_data["room"]:
        room_data_info[room["id"]] = {"area": room["area"], "type": room["type"]}

    role_vector = {}
    if replace_more and room_id in replace_more:
        seeds_list = []
        for jid in replace_more[room_id]["soft"]:
            if jid not in furniture_seeds_note:
                continue

            seeds_list.append(
                {"jid": jid, "group": furniture_seeds_note[jid]["group"], "role": furniture_seeds_note[jid]["role"]})

        role_vector = compute_room_role_vector(seeds_list, room_data_info[room_id]["type"])

    num_seeds = len(list(furniture_seeds_note.keys()))
    all_list = []
    for item in source_living_base_scheme:
        if item["style_type"] not in target_style_list:
            continue

        if item["source_id"] != source_key:
            continue
        score = compute_role_vector_sim(role_vector, item["roles_vec"])
        all_list.append((item["key"], score))

    if len(all_list) > 0 or set_scheme is not None:
        need_keys = sorted(all_list, key=lambda x: x[1])
        house_sample_list = []
        now_area = room_data_info[room_id]["area"]
        if now_area > 35.:
            ratio = 1.0
        else:
            ratio = 0.7

        for i in range(len(need_keys[:sample_num])):
            if need_keys[i][1] > ratio * num_seeds:
                continue

            house_sample_list.append({"sample": {room_id: need_keys[i][0]}})

        # TODO: 在这里换成我找的方案。前面的key是户型中的room_id，后面是找到的方案的key
        if set_scheme is not None:
            house_sample_list = []
            house_sample_list.append({"sample": {room_id: set_scheme}})

        sample_info_list = []
        for sample_keys_info in house_sample_list:
            sample_info_list.append(get_sample_data_from_house_sample_keys(sample_keys_info))

        if material_seeds_info or furniture_room_seeds_info:
            for sample_idx, sample_info in enumerate(sample_info_list):
                sample_seed_replace_process(sample_info, furniture_room_seeds_info, furniture_seeds_note)

                sample_info["info"]["seed_info"] = furniture_seeds_note
                sample_info["info"]["seed_flag"] = check_room_seed(house_data, furniture_room_seeds_info,
                                                                   furniture_seeds_note)

        return sample_info_list
    else:
        return []


def house_layout_build(room_info, room_id, sample_data_info):
    seed_in_flag = False
    house_layout = {}

    if room_id in sample_data_info['sample']:
        if "seed_info" not in sample_data_info['info']:
            replace_soft = []
            replace_note = {}
        else:
            replace_soft = list(sample_data_info['info']["seed_info"].keys())
            replace_note = sample_data_info['info']["seed_info"]

        room_data_add, room_layout_add, room_propose_add, room_region_add = \
            layout_room_by_sample(room_info, sample_data_info['sample'][room_id], replace_soft,
                                  replace_note, refine_mode=0)

        house_layout[room_id] = room_layout_add

        group_list = []
        if 'layout_scheme' in room_layout_add:
            scheme_set = room_layout_add['layout_scheme']
            if len(scheme_set) > 0 and 'group' in scheme_set[0]:
                group_list = scheme_set[0]['group']

        replace_used = []
        for replace_key in replace_soft:
            replace_use = False
            for group_one in group_list:
                object_list = group_one['obj_list']
                for object_one in object_list:
                    if object_one['id'] == replace_key:
                        replace_use = True
                        break
                if replace_use:
                    break
            if replace_use:
                replace_used.append(replace_key)
        if len(replace_used) == len(replace_soft):
            seed_in_flag = True

    return house_layout, seed_in_flag


# def check_sofa_L_type(jid, new_data):
#     url = "http://calcifer-api.alibaba-inc.com/api/v1/models/" + jid + "/algorithm?keys=l_sofa_shape_type"
#     data = get_http_data_from_url(url)
#     if data:
#         if jid in data and "l_sofa_shape_type" in data[jid]:
#             if data[jid]["l_sofa_shape_type"] == "右":
#                 add_furniture_type(jid, "sofa/right corner sofa")
#                 new_data["type"] = "sofa/right corner sofa"
#                 # add_furniture_data(jid, new_data)
#             elif data[jid]["l_sofa_shape_type"] == "左":
#                 new_data["type"] = "sofa/left corner sofa"
#                 add_furniture_type(jid, "sofa/left corner sofa")
#                 # add_furniture_data(jid, new_data)


def house_search_from_seed(furniture_list=[], room_type="Bedroom", recon_scene=False, set_scheme=None, sample_num=1):
    if "-" in room_type:
        room_type, _ = room_type.split('-')
    if room_type in ["Bedroom", "MasterBedroom", "SecondBedroom", "KidsRoom"]:
        need_target_room_list = target_house_room["Bedroom"]
    else:
        need_target_room_list = target_house_room["LivingRoom"]

    seeds_have_in_flag = False
    used_key = ""
    scheme_key = []

    replace_more = {}
    house_info = {}
    house_layout = {}

    # 种子处理 L 沙发处理
    # for seed_id in furniture_list:
    #     obj_type, obj_style_en, obj_size, obj_type_id, obj_style_id, obj_category_id = get_furniture_data_more(seed_id)
    #     new_data = {
    #         "type": obj_type,
    #         "style": obj_style_en,
    #         "size": obj_size,
    #         "size_obj": obj_size,
    #         "category_id": obj_category_id,
    #         "type_id": obj_type_id,
    #         "style_id": obj_style_id
    #     }
    #     if "sofa" in obj_type and obj_size[0] > 2.0:
    #         check_sofa_L_type(seed_id, new_data)

    # TODO: 把need_target_room_list换成我找到的户型
    if set_scheme is not None:
        need_target_room_list = [set_scheme]

    for room_key in need_target_room_list:
        house_id, room_id = room_key.split('_')
        used_key = house_id

        house_info = get_house_info(house_id, room_id)
        replace_more = {room_id: {"soft": furniture_list, "sample": []}}
        house_sample_info = house_search_base_target(house_id, room_id, house_info, replace_more, sample_num=sample_num,
                                                     set_scheme=set_scheme)
        if not house_sample_info:
            continue

        for sample_data in house_sample_info:
            now_scheme_key = sample_data["info"]["sample"][room_id]

            room_info = house_info["room"][0]
            house_layout = {}

            house_layout, seed_in_flag = house_layout_build(room_info, room_id, sample_data)

            if seed_in_flag:
                seeds_have_in_flag = True
                scheme_house, scheme_room = now_scheme_key.split('_')
                if now_scheme_key not in replace_more[room_id]["sample"]:
                    replace_more[room_id]["sample"].append(now_scheme_key + "_self")
                scheme_key.append(now_scheme_key)

        if seeds_have_in_flag:
            break

    # 走样板间正常检索 直接挑大户型
    if not seeds_have_in_flag and False:
        for room_key in need_target_room_list[-4:]:
            house_id, room_id = room_key.split('_')
            used_key = house_id

            house_info = get_house_info(house_id, room_id)
            correct_house_data(house_info)
            replace_more = {room_id: {"soft": furniture_list, "sample": []}}
            house_sample_info = house_search_get_sample_info(house_info, seeds_info=replace_more, target_style="seed")
            if not house_sample_info:
                continue

            for sample_data in house_sample_info:
                now_scheme_key = sample_data["info"]["sample"][room_id]
                room_info = house_info["room"][0]
                house_layout, seed_in_flag = house_layout_build(room_info, room_id, sample_data)

                if seed_in_flag:
                    seeds_have_in_flag = True
                    scheme_house, scheme_room = now_scheme_key.split('_')
                    if now_scheme_key not in replace_more[room_id]["sample"]:
                        replace_more[room_id]["sample"].append(now_scheme_key)
                    scheme_key.append(now_scheme_key)

            if seeds_have_in_flag:
                break

    # 重建户型
    if recon_scene and seeds_have_in_flag:
        house_mode = {
            'mesh': True,
            'customized_ceiling': True,
            'win_door': True,
            'mat': True,
            'floor_line': True,
            'bg_wall': True,
            'kitchen': True,
            'light': True,
            'debug': False,
            'white_list': False
        }
        house_scene, house_outdoor = house_build_house(house_info, house_layout, '',
                                                       house_mode)
        data_time = time.strftime("%Y-%m-%d") + "/"
        name_time = str(int(time.time() * 1000))

        scene_name = furniture_list[0] + "_" + used_key + "_" + name_time + ".json"
        oss_upload_json("demo_scene/" + data_time + scene_name, house_scene, "ihome-alg-layout")

        scene_url = "https://ihome-alg-layout.oss-cn-hangzhou.aliyuncs.com/demo_scene/" + data_time + scene_name

        house_info, house_layout, camera_info, wander_info = view_house(house_info, house_layout, view_mode=1)
        house_info["layout"] = house_layout
        house_camera_list = layout_sample_camera(house_info)

        return True, used_key, scene_url, house_camera_list

    if seeds_have_in_flag:
        return True, used_key, replace_more
    else:
        return False, "9febe749-9f93-4bc6-9db4-aed04d4e713e", replace_more


def get_room_id():
    from Demo.test_local import get_design_json_daily

    # for i in target_house_room["LivingRoom"]:
    #     design_url = get_design_json_daily(i)
    #
    #     _, house_data = get_house_data(i, design_url)
    #     for room_data in house_data["room"]:
    #         if room_data["type"] in ["LivingDiningRoom", "LivingRoom"]:
    #             print(i + '_' + room_data["id"])
    #             break

    for j in target_house_room["Bedroom"]:
        design_url = get_design_json_daily(j)

        _, house_data = get_house_data(j, design_url, reload=True)
        for room_data in house_data["room"]:
            if room_data["type"] in ["Bedroom", "MasterBedroom"]:
                print(j + '_' + room_data["id"], room_data["area"])


def check_furniture_turn():
    pass


def check_sofa_l_type():
    pass


if __name__ == '__main__':
    a = time.time()
    jid_list = [
        "721230a2-d34d-4ef0-8460-7508eed3e32c",
        "87153468-49a7-4478-a13e-05cf397789bf",

        "7c90729d-056a-4633-9c32-c862c06bfd77",  # 茶几
        "763c8359-2c11-4df3-80e8-d8af62604774",
        "d539aa2c-3af1-4c6e-bc90-a9e612635e3f",
        "8fbc1f92-7bd5-4420-8e81-5e72a30542e6",
        "3c4bf560-0f03-4424-8010-aa9ffc7526a8",
        "73582afb-79af-4e20-9e24-4c6a9803408e",
        "e376d3bd-0af5-4a3a-948e-0e19b07186c5",
        "4b2938bc-c990-4474-a348-12dfdd8d38e1",
        "03e02f1c-3319-47bd-b656-0547856cad65",

        "13cb99c0-b67a-42a9-8b61-878ffb97d068",  # 桌
        "c715d6d7-6b93-4ad3-b51e-73869dd30035",
        "82e9d768-74cb-4da8-8b97-50f45f3f4d2a",
        "6abeab62-1cb6-4edf-a248-e11fcbb22f2a",
        "8ffddc7b-684c-4dcd-89a5-22e394eabb26",
        "f752d7fd-a371-42c1-839a-99d460f78484",
        "e3e6e8e2-4741-4f88-a53d-f208ccb9783b",
        "043c7029-4e43-4b17-a6e8-dc233d29a63e",

        "c9fde3b4-72ab-4894-aaa6-e400e2c0c799",  # 电视柜
        "25e7ec1b-ed5a-4ddf-85c3-eb9f326ccacb",
        "e2430c07-70e0-4682-8f5d-b69b177cd66f",
        "cf94cf5f-756e-4584-bccc-1dfe78b7d8cb",
        "7d4fdb60-5f6e-4673-ae81-41b8060ce90e",
        "034a4131-ff19-4209-b4bd-2237f303c910",
        "903cd37a-b144-4263-b419-c3893c6736c8",
        "2ad484c7-a2d6-4963-b3f3-dc864af559d9",
        "d5d2bc1a-9ca8-4498-b1b6-e9b9559a461f",
        "20d2ed7d-1bd1-4906-9a82-c617283edb3c",

        "797dd860-1f9b-409b-9495-9ed9747a484d",  # 单人沙发
        "76cb80ec-f698-4cb4-90af-0756f7bc61f5",
        "c86e3e3a-a602-4d55-abc8-96b96acc8b6e",
        "5391442d-e1e8-4296-ab60-fbb817c0b5ab",
        "a8f59973-1ceb-4e45-9f3c-8d818535d307"]

    all_test = ["5640d5a3-b4ee-4c83-a35b-f5c4e59c0c9a",  # 沙发
                "c7553bdd-f2cb-4927-96f1-ad93054987cd",
                "bf89493a-47c9-402a-910e-8853e63ec50a",
                "eefb47a0-f61a-4665-a6ce-5e6508ef1073",

                "1acc9527-7bb3-40dd-bdc8-36edff7beee8",
                "727e1be9-a486-4403-96d7-eefd0624278c",
                "5cf00b14-42e5-4ef9-9a37-93d79edb4dcf",
                "3a699665-1dbb-42ad-a779-93159335948f",
                "36242f9a-aac7-44d4-9d06-5a77158df119",

                "3c4bf560-0f03-4424-8010-aa9ffc7526a8",
                "73582afb-79af-4e20-9e24-4c6a9803408e",
                "e376d3bd-0af5-4a3a-948e-0e19b07186c5",
                "c9fde3b4-72ab-4894-aaa6-e400e2c0c799",
                "26e022d4-9d90-43b6-86ec-00788d5e5bb6",
                "5097fdd4-ca70-4570-8772-bdbd3b4d5ab6",
                "7b05e806-e153-4376-9dd6-1af3206ed821",

                "7d4fdb60-5f6e-4673-ae81-41b8060ce90e",
                "034a4131-ff19-4209-b4bd-2237f303c910",
                "903cd37a-b144-4263-b419-c3893c6736c8",

                "c315b65c-6f5d-42e1-b113-87942131c250",  # 单人沙发
                "834993fb-1095-4002-b4d4-d36ccfde5df2",  #
                "d19cb47f-4073-4acd-8585-cf988e8d05a1"
                ]

    all_test_multi_seeds = [
        [
            False, '',
            '["84a5a72d-7ec0-489b-80cf-16276d68289e", "e7e42c4b-4202-458b-8e56-e8aa8d1892c6", "4cbbd4c5-ddbc-4c5c-bddc-4dffe2c17308", "3181dd62-48ce-4e4f-ad9f-474ed7fb7355", "d3b2bb10-8827-49cc-99c3-ce01b4890f28"]'
        ],
        [False, '',
         '["c713903a-e254-41be-ac87-5edb9bc45b95", "58a5fdc5-719a-4639-b8de-824d0a0db50b", "35f32bda-3403-4c1d-aef3-d4748ef08358", "86a2eda4-9dd9-47dd-99be-17a7291dff65", "e116425c-5825-4c25-bbe7-b695dbba8d8d"]'],
        [False, '',
         '["1fe38f83-7542-4d2f-b1c9-85b3c94fac0f", "bde6be09-6478-46ac-8df0-d9454ebfbe78", "6253a5c7-f12d-4d0d-9b50-46819ce25104", "fdd47fb6-aed5-4c92-9d77-fe06a7012f9e"]'],
        [False, '',
         '["f8d3e231-3870-4a60-8fd1-fe528336c349", "af28d581-223f-42e3-9fa4-fa7b2de216c5", "78fa6e6b-df04-4981-be57-bed79cf126ef", "e2f9e1a5-b2dd-446a-a4d1-ce079a420b26"]'],
        [False, '',
         '["0fc81f42-9fb3-43f3-8175-82555ddac9d9", "77bdd4c5-ca46-4da8-aceb-deba60177927", "ebe67abc-d230-4ecb-9340-b92acd14852d", "542c7cfc-af62-482f-b37a-b8254c1df25b", "c594d5ed-30f0-4014-9228-e1f68a1e80b7"]'],
        [False, '',
         '["ed0b13fb-0f0b-4c1b-9a0f-0248b7cf9068", "93543930-98a7-4a95-a53a-62cc05bca831", "322d0306-06f5-475f-a18d-ef794c59dac2", "45b3c800-13f9-4215-95d6-c026d19ca977", "c3c00ddf-8d68-4089-b055-b6756e8e6531"]'],
        [False, '',
         '["cf1e82dc-2fac-4b2b-a504-837e5be5105e", "03b5f323-0cbf-44fa-a1fd-27e27a94fcd3", "2c11cad5-5cfd-4dab-b196-c92ba2858669", "94f3d8db-12d2-4f60-9f31-1e6c57e6092f"]'],
        [False, '',
         '["7bab43e2-d652-483a-b174-1c703ae53ded", "d4ec8711-ec9d-4bc8-bc58-eec13b9fcefc", "0b4a9524-cc89-4b0f-b472-2fe4d00f26a0", "d31cee62-049d-47ce-9f60-74f59f88e1e5"]'],
        [False, '',
         '["d8081aac-5cce-4378-b333-f81e35bff213", "1f587064-95b3-4ea4-8970-47c3fa9495f3", "5e6cedca-d7c0-439b-a91e-5cccdb82e7b5", "8765dada-3b27-474a-b34f-7777b51859a1", "c0db516a-3ed0-4593-a682-8384e0451599"]'],
        [False, '',
         '["1f8765f3-5f91-4d7a-9db4-bb65bce7adef", "f7842767-6786-4f19-9c4f-f92ce2f7ef62", "673cef4f-0d4b-4911-8d06-548b20a8742f", "a7969e51-cce1-4ee9-9674-db379a165896", "c904cb65-0741-4428-98dc-537833fcbcc1"]'],
        [False, '',
         '["123b1213-2228-4b6f-b202-e5510d95686c", "9696ee53-7763-4f93-870f-d243552a0fd7", "b7dd6d62-0e38-45a5-a622-4bc1cc7218df", "db133f85-6052-4507-be7d-7f528919a5d2", "8f154b37-3cac-4149-873c-d34d3b808905"]'],
        [False, '',
         '["26fac82c-652b-4610-8463-18fcde09fcc6", "ecc43cb0-3435-4624-a088-64fa77dd8080", "425d2597-dd59-418d-8a9c-644f34dcbbbd", "9f1be662-f56c-4367-a887-b47fd58069cf"]'],
        [False, '',
         '["4303e3cd-b3b3-4e1a-96d6-7a81c0b6d81b", "5f30cdbe-cd23-4043-a69b-1c090e3af95c", "b3e636fe-ed70-4adb-a3d5-860848d0a94a", "50b0cc3a-1b21-4140-8e29-ea749a21fd66", "424fa828-d2ee-419b-905d-f756bf04a0c7"]'],
        [False, '',
         '["3e4ac5e8-275b-491e-bf82-9ff4495a0dce", "60f4922a-43fb-4df8-accf-aee487207c4d", "2182beb5-b608-4751-b6bf-1de220378bfb", "6e5386c3-37e8-4082-b7fc-78b8cb2c3947", "85e6cba4-617c-40a1-bff1-8495567fe3c2"]'],
        [False, '',
         '["cee26cc5-0bc6-482c-8077-29d0ac322f17", "0940caaa-071a-4902-88b1-d7d365152141", "09a572f2-9966-4cd6-881d-e0f6b8d06587", "c49562dd-9b34-4249-b744-9b09ec7a25e2", "2afba0ba-64d0-4b9b-b825-5831074f81bd"]'],
        [False, '',
         '["c8187c41-5751-4115-a593-bff33dc7853b", "028c6220-c830-46cf-9727-a1a26d06d296", "0549ebbd-f715-4e92-95b4-1ed7590dc628", "9ad42484-43e6-4c44-8f3e-d01879c49611", "23b0c53e-489d-4e9c-8ef9-1be53ee4b8e4"]'],
        [False, '',
         '["f6f357fb-927f-4106-b8c8-5aca04dc278f", "c5249617-49ef-43f4-ac36-ba67208ff9e8", "b70b4098-873f-4044-9a7d-feb1614ad6b8", "975acc64-ce6a-4656-891c-168a9ad0c9cd", "71c733b1-0abb-4819-8efc-c094f376dfd1"]'],
        [False, '',
         '["05bab646-3a1f-4c56-8693-32e6108272f3", "b21460ba-893b-445d-9866-9cf080e83fb2", "f3fdf3de-f4e4-4dd1-bfab-282546625cb9", "d42482db-47fa-48d2-973b-231ae0ed7c83", "60b784da-5d02-48dd-8a2f-ef37a6742dad"]'],
        [False, '',
         '["19ac44e2-7c7a-48b6-923f-1cae474ecf72", "86dbff23-6810-415b-8dea-bea485488e57", "6c4dd289-8884-4c36-b99f-10d689d6f5a6", "bc67d05d-cc0f-41a9-a7d2-4421faa3b183", "49c12e7f-5387-45fc-ace0-79843d9d099a"]'],
        [False, '',
         '["ebaa0dd5-1bab-440b-adfc-73754e86e8b5", "4f4c8b3b-ad71-4400-aa9c-04a4246b89f2", "157b00b7-bece-459f-a631-34ba7c2ba0cb", "413b648a-f8de-4abf-81ea-84a704a2c38a"]'],
        [False, '',
         '["156637b6-900e-445a-b29e-b63ea298d87e", "2c3bc40e-865f-411a-a670-0efeb617ec93", "81ee3d71-3b27-470e-8f4c-304105c39d46", "aed596cf-898b-4b0a-bbf0-7354887f2ffb", "9122640b-016e-48ee-9404-fb7d5752e5d5"]'],
        [False, '',
         '["9f518457-e3bc-4e8c-96b7-1e852e6b6d93", "e0aa9a5f-b092-4369-96eb-38682c3d33e3", "8f6d7858-0d6a-4da8-bb10-e830bdd2814c", "46c6859f-ccfc-41d8-90b5-1c230848f9ff", "03c309cc-d94b-4b1c-b411-73dfae873a04"]'],
        [False, '',
         '["935c353a-1e1c-4b2c-9d95-af117b8c8e62", "cdda2fd3-2c4d-4fe4-b692-4f1c2bfe496c", "0b4d9843-9cd1-45de-89fa-669fd5522815", "f2d032cc-e635-488d-8eb6-916a269a1609", "a0fa9a3b-73db-4fad-8276-72331657f22e"]'],
        [False, '',
         '["3a75436b-79d7-4e74-b43e-5cc43e7cb7b5", "980d274c-aae6-4a7e-9e61-f0343af9d111", "99fc9535-138c-4df6-a8e1-12824f5d3419", "6ca9409f-ac81-4d24-b995-726b3c8fd29c", "5280cf83-84f0-4377-aeec-be7b9c284d81"]'],
        [False, '',
         '["252ae9a6-2f22-43fc-82e4-cb94d0fd7e64", "cc5a990d-e4de-4292-a6e4-0e24ccfaedb3", "4e08e709-41da-4225-a447-417bfcb756f1", "1125bcb9-c22e-4f92-a00a-56b87d97e9f8", "79901c8f-f16d-4c1a-ac58-784482db697c"]'],
        [False, '',
         '["43fd1ea2-bb4c-4980-8409-855aa7be3033", "ca5c123a-b06c-4299-ae85-2c49da1a1b41", "d0e11984-12ff-4c46-9417-517037c5b2a3", "48ac66ca-cdf5-4b87-9d9c-c7ba1766d0cf", "7b09c123-a2a6-479b-b755-1041a1e3160b"]'],
        [False, '',
         '["6469791b-3218-4cd3-a54a-116b887fad59", "28cf97f9-4d24-4956-8648-f75f47fff29d", "3c6d38d2-2d9f-406c-b87f-f2e0385ec8b1", "5d95424d-66d8-4250-80af-6363a44d4aa0", "6f89df9f-c499-4af8-b201-7dcb6af5b22f"]'],
        [False, '',
         '["e1e4ce21-8150-4b05-a9b5-a1f9eb571c71", "aa539eee-1bc8-498c-9421-fef8c6905e28", "9396fe86-6b11-4ec4-ba4f-c6e751237b06", "ad615473-1e22-4fc6-935f-a6b80a91d519", "cc10b031-91f7-4fed-9b39-2c646e18dfa2"]'],
        [False, '',
         '["098e7b47-f5a8-45ef-8a28-d5899c06eb4a", "23edce31-51dc-4dc3-9f48-ce1d3de9769a", "25ffce5e-cfea-4288-8d68-d4206c4a1eb2", "7c52e70a-1e39-48a9-bd80-871d54672601", "d1716f52-65c9-4650-86dc-9cd1f118e1ab"]']]
    # all_data = json.load(open("./temp/out_multi_seeds.json", "r"))

    # 只输出没有放置成功的
    # out = []
    # for item in jid_list:
    #     # furniture_list = json.loads(item[-1])
    #     furniture_list = [item]
    #     flag, key, scene = house_search_from_seed(furniture_list, "LivingRoom")
    #     if not flag:
    #         out.append([flag, key, scene])
    #
    #     print(flag, key, scene)
    #
    # print(out)
    # print(time.time() - a)
    # # save_furniture_data()

    test = ["b5ce9bc6-27d8-4205-8074-1e6b1f3467b6", "8017cfa4-628a-4714-b09c-20b7b9854777",
            "9d1cb881-636e-43e2-9daa-1c833c3443a2"]
    flag, key, scene, _ = house_search_from_seed(test, "LivingRoom", recon_scene=True)

    print(flag)
    print(key)
    print(scene)
