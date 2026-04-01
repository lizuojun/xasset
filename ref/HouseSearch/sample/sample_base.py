from functools import singledispatch


class SerializationBase:
    def to_json(self, obj):
        if isinstance(obj, SerializationBase):
            now = obj.build_json()
        elif isinstance(obj, SerializationList):
            now = obj.build_json()
        elif type(obj).__name__ in ["int", "float", "str", "bool", "NoneType"]:
            now = obj
        elif type(obj).__name__ == "list":
            now = [self.fast_json_copy(sub_obj) for sub_obj in obj]
        elif type(obj).__name__ == "dict":
            now = {}
            for sub_key, value in obj.items():
                now[sub_key] = self.fast_json_copy(value)
        else:
            raise TypeError("SerializationBase not support type %s in obj" % type(obj).__name__)

        return now

    # 自身class 数据转成json
    def build_json(self):
        dump_json = {}
        for key in vars(self):
            value = getattr(self, key)
            dump_json[key] = self.to_json(value)

        return dump_json

    # class 数据转 json 数据
    def parse_class_to_json(self, class_name):
        pass

    # json 数据转 class 数据
    @classmethod
    def parse_json(cls, obj):
        if type(obj).__name__ not in ["dict", "list"]:
            return obj
        if type(obj).__name__ == "dict":
            s = SerializationBase()
            for key in obj:
                setattr(s, key, SerializationBase.parse_json(obj[key]))
            return s
        else:
            s = SerializationList()
            out_list = []
            for sub_obj in obj:
                out_list.append(SerializationBase.parse_json(sub_obj))
            setattr(s, "_array", out_list)
            return s

    # json 数据转 class 数据
    def parse_json_class(self, obj):
        pass

    @staticmethod
    def get_default_value(obj, key, default):
        if key in obj:
            return obj[key]
        return default

    def fast_json_copy(self, d):
        output = d.copy()
        for key, value in output.items():
            output[key] = self.fast_json_copy(value) if isinstance(value, dict) else value
        return output

    def get_item(self, item_key, default=None):
        if item_key in self.__dict__:
            return self.__dict__[item_key]
        return default


class SerializationList(SerializationBase):
    def __init__(self):
        super(SerializationBase)
        self._array = []

    def build_json(self):
        return [self.to_json(data) for data in self._array]


if __name__ == '__main__':
    import time
    import copy

    start_t = time.time()
    test_json = {
        "Balcony-5325": {
            "room_type": "Balcony",
            "room_style": "Contemporary",
            "room_area": 6.73666400000001,
            "room_height": 2.8,
            "layout_scheme": [
                {
                    "code": 10200,
                    "score": 80,
                    "type": "Balcony",
                    "style": "Contemporary",
                    "area": 6.73666400000001,
                    "material": {
                        "id": "Balcony-5325",
                        "type": "Balcony",
                        "floor": [
                            {
                                "jid": "d455f25f-c369-4325-a63e-1ab46b518f22",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/d455f25f-c369-4325-a63e-1ab46b518f22/wallfloor_mini.jpg",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.3,
                                    0.07
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "27207",
                                "area": 5.929456
                            }
                        ],
                        "wall": [
                            {
                                "jid": "361d057d-0728-4e1c-9482-055a2c2e2dbc",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/361d057d-0728-4e1c-9482-055a2c2e2dbc/wallfloor_mini.jpg",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.9,
                                    0.9
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "25788",
                                "area": 11.766000000000002,
                                "wall": [
                                    [
                                        -3.204002,
                                        5.4735000000000005
                                    ],
                                    [
                                        1.053998,
                                        5.4735000000000005
                                    ]
                                ],
                                "offset": True,
                                "alias": "361d057d-0728-4e1c-9482-055a2c2e2dbc"
                            }
                        ],
                        "win_pocket": [],
                        "door_pocket": [],
                        "customized_ceiling": [],
                        "win": [
                            {
                                "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                "type": "window/floor-based window",
                                "style": "Contemporary",
                                "size": [
                                    272.919,
                                    216.796,
                                    12.0
                                ],
                                "scale": [
                                    0.531474,
                                    1,
                                    1
                                ],
                                "position": [
                                    -3.204002,
                                    0.2,
                                    4.627494
                                ],
                                "rotation": [
                                    0,
                                    -0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "12326",
                                "categories": [
                                    "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                ],
                                "pocket": {
                                    "jid": "",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                    "color": [
                                        255,
                                        255,
                                        255
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        2.729192,
                                        0.001
                                    ],
                                    "seam": False,
                                    "material_id": "12406",
                                    "area": -1
                                },
                                "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                "unit_to_room": "",
                                "unit_to_type": "",
                                "role": "window",
                                "count": 1,
                                "relate": "",
                                "relate_group": "",
                                "relate_position": []
                            }
                        ],
                        "door": {
                            "LivingDiningRoom": [
                                {
                                    "id": "1dbb3f82-5c6f-41ef-900e-9a436b252cde",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        203.555,
                                        172.29,
                                        18.1747
                                    ],
                                    "scale": [
                                        1.143337,
                                        1.218875,
                                        1
                                    ],
                                    "position": [
                                        -0.950672,
                                        0,
                                        3.7855
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17894",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "LivingDiningRoom-5376",
                                    "unit_to_type": "LivingDiningRoom",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ]
                        },
                        "background": []
                    },
                    "decorate": {},
                    "painting": {},
                    "group": [
                        {
                            "type": "Rest",
                            "code": 1100,
                            "size": [
                                1.3097204895019534,
                                0.6641660308837891,
                                0.8665219879150391
                            ],
                            "offset": [
                                -0.22432725524902355,
                                0,
                                -0.0
                            ],
                            "position": [
                                -2.1539177447509767,
                                0,
                                4.444688
                            ],
                            "rotation": [
                                0,
                                -0.0,
                                0,
                                1.0
                            ],
                            "size_min": [
                                0.8610659790039062,
                                0.6641660308837891,
                                0.8665219879150391
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.0,
                                0.4486545104980471
                            ],
                            "obj_main": "c315b65c-6f5d-42e1-b113-87942131c250",
                            "obj_type": "sofa/single seat sofa",
                            "obj_list": [
                                {
                                    "id": "c315b65c-6f5d-42e1-b113-87942131c250",
                                    "type": "sofa/single seat sofa",
                                    "style": "Contemporary",
                                    "size": [
                                        86.10659790039062,
                                        66.4166030883789,
                                        86.6521987915039
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -2.378245,
                                        0,
                                        4.444688
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17523",
                                    "categories": [
                                        "182f769f-981f-4a8e-9aef-7efe9917cf19"
                                    ],
                                    "category": "182f769f-981f-4a8e-9aef-7efe9917cf19",
                                    "relate": "wall",
                                    "group": "Rest",
                                    "role": "table",
                                    "count": 1,
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -2.378245,
                                        0,
                                        4.444688
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                },
                                {
                                    "id": "71103010-5fb5-4a51-8d49-484717252988",
                                    "type": "sofa/ottoman",
                                    "style": "Other",
                                    "size": [
                                        41.0361,
                                        46.0891,
                                        39.4851
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.704238,
                                        0,
                                        4.616203
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17525",
                                    "categories": [
                                        "5b4dc4ea-d84e-4b21-8cec-f2d090c61275"
                                    ],
                                    "category": "5b4dc4ea-d84e-4b21-8cec-f2d090c61275",
                                    "group": "Rest",
                                    "role": "chair",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.704238,
                                        0,
                                        4.616203
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        0.6740070000000002,
                                        0,
                                        0.17151499999999942
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "neighbor_more": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "switch": 0,
                            "region_direct": 0,
                            "region_center": [],
                            "back_p1": [],
                            "back_p2": [],
                            "back_depth": 0,
                            "back_front": 0.8665219879150391,
                            "back_angle": 0
                        },
                        {
                            "type": "Wall",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Ceiling",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Floor",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "5f62f363-85d8-48bb-8e95-d77951df040c",
                                    "type": "plants/plants - on top of others",
                                    "style": "Other",
                                    "size": [
                                        28.1437,
                                        55.3952,
                                        20.9205
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        0.793279,
                                        0,
                                        5.308897
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17527",
                                    "categories": [
                                        "c352426b-2cfd-4855-a75a-50014e437832"
                                    ],
                                    "category": "c352426b-2cfd-4855-a75a-50014e437832",
                                    "role": "plants",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                },
                                {
                                    "id": "5f62f363-85d8-48bb-8e95-d77951df040c",
                                    "type": "plants/plants - on top of others",
                                    "style": "Other",
                                    "size": [
                                        28.1437,
                                        55.3952,
                                        20.9205
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -2.73558,
                                        0,
                                        5.308897
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17528",
                                    "categories": [
                                        "c352426b-2cfd-4855-a75a-50014e437832"
                                    ],
                                    "category": "c352426b-2cfd-4855-a75a-50014e437832",
                                    "role": "plants",
                                    "count": 1,
                                    "relate": "c315b65c-6f5d-42e1-b113-87942131c250",
                                    "relate_group": "Rest",
                                    "relate_position": [
                                        -2.378245,
                                        0,
                                        4.444688
                                    ],
                                    "relate_role": "table",
                                    "origin_position": [
                                        -2.73558,
                                        0,
                                        5.308897
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        -0.35733499999999996,
                                        0,
                                        0.8642089999999998
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Door",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "1dbb3f82-5c6f-41ef-900e-9a436b252cde",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        203.555,
                                        172.29,
                                        18.1747
                                    ],
                                    "scale": [
                                        1.143337,
                                        1.218875,
                                        1
                                    ],
                                    "position": [
                                        -0.950672,
                                        0,
                                        3.7855
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17894",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "LivingDiningRoom-5376",
                                    "unit_to_type": "LivingDiningRoom",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Window",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                    "type": "window/floor-based window",
                                    "style": "Contemporary",
                                    "size": [
                                        272.919,
                                        216.796,
                                        12.0
                                    ],
                                    "scale": [
                                        0.531474,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -3.204002,
                                        0.2,
                                        4.627494
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "12326",
                                    "categories": [
                                        "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            2.729192,
                                            0.001
                                        ],
                                        "seam": False,
                                        "material_id": "12406",
                                        "area": -1
                                    },
                                    "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                    "unit_to_room": "",
                                    "unit_to_type": "",
                                    "role": "window",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Background",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Customize",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        }
                    ],
                    "group_area": 1.1349016021762908,
                    "source_house": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4",
                    "source_room": "Balcony-5325",
                    "source_room_area": 6.73666400000001,
                    "line_unit": [
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.731,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    1.6280000000000028
                                ]
                            ],
                            "height": 0,
                            "angle": -1.5707963267948966,
                            "p1": [
                                0.994,
                                3.845
                            ],
                            "p2": [
                                0.263,
                                3.845
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.6,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 2,
                            "width": 3.072,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 0.664,
                            "angle": -1.5707963267948966,
                            "p1": [
                                0.263,
                                3.845
                            ],
                            "p2": [
                                -2.809,
                                3.845
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 1.037,
                            "unit_margin": 0.17,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": 5,
                            "width": 0.335,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    1.6280000000000028
                                ]
                            ],
                            "height": 0,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -2.809,
                                3.845
                            ],
                            "p2": [
                                -3.144,
                                3.845
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 4,
                            "score": 8,
                            "width": 1.628,
                            "depth": 0.335,
                            "depth_all": [
                                [
                                    0.0,
                                    1.0,
                                    4.138
                                ]
                            ],
                            "height": 0.6,
                            "angle": 0,
                            "p1": [
                                -3.144,
                                3.845
                            ],
                            "p2": [
                                -3.144,
                                5.474
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.335,
                            "depth_post": 0.23,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0.0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                -3.144,
                                5.353
                            ],
                            "width_original": 1.45,
                            "p1_original": [
                                -3.144,
                                3.902
                            ]
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0.6,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -3.144,
                                5.474
                            ],
                            "p2": [
                                -2.914,
                                5.474
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 3.908,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    0.20480092118730808,
                                    1.6280000000000028
                                ],
                                [
                                    0.20480092118730808,
                                    0.7998766632548618,
                                    1.6280000000000023
                                ],
                                [
                                    0.7998766632548618,
                                    1.0,
                                    1.6280000000000028
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -2.914,
                                5.474
                            ],
                            "p2": [
                                0.994,
                                5.474
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 8,
                            "width": 1.628,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0.0,
                                    1.0,
                                    4.138
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                0.994,
                                5.474
                            ],
                            "p2": [
                                0.994,
                                3.845
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.6,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        }
                    ]
                }
            ],
            "layout_mesh": []
        },
        "LivingDiningRoom-5376": {
            "room_type": "LivingDiningRoom",
            "room_style": "Chinese Modern",
            "room_area": 39.9504450656,
            "room_height": 2.8,
            "layout_scheme": [
                {
                    "code": 31309,
                    "score": 80,
                    "type": "LivingDiningRoom",
                    "style": "Chinese Modern",
                    "area": 39.9504450656,
                    "material": {
                        "id": "LivingDiningRoom-5376",
                        "type": "LivingDiningRoom",
                        "floor": [
                            {
                                "jid": "f97913fe-2685-4115-a52b-a5728c8f445d",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/f97913fe-2685-4115-a52b-a5728c8f445d/wallfloor_mini.jpg",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.9,
                                    0.9
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "17538",
                                "area": 37.928134393551986
                            }
                        ],
                        "wall": [
                            {
                                "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                                "texture_url": "",
                                "color": [
                                    248,
                                    249,
                                    251
                                ],
                                "colorMode": "color",
                                "size": [
                                    1,
                                    1
                                ],
                                "seam": False,
                                "material_id": "76",
                                "area": 22.111073461245663,
                                "wall": [
                                    [
                                        1.054,
                                        0.53
                                    ],
                                    [
                                        5.233,
                                        0.53
                                    ]
                                ],
                                "offset": True,
                                "alias": "c53afd8f-6b30-4d1b-8454-0138ff5d7147"
                            }
                        ],
                        "win_pocket": [],
                        "door_pocket": [],
                        "ceiling": [
                            {
                                "id": "db593061-992e-4fa9-b4f4-f4db7cc0ef25",
                                "type": "build element/ceiling molding",
                                "style": "\u5317\u6b27",
                                "size": [
                                    357.5,
                                    30.0,
                                    325.745
                                ],
                                "scale": [
                                    0.824692,
                                    1,
                                    0.824509
                                ],
                                "position": [
                                    -1.045104,
                                    2.5,
                                    1.741363
                                ],
                                "rotation": [
                                    0,
                                    0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "19475",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "db593061-992e-4fa9-b4f4-f4db7cc0ef25",
                                "type": "build element/ceiling molding",
                                "style": "\u5317\u6b27",
                                "size": [
                                    357.5,
                                    30.0,
                                    325.745
                                ],
                                "scale": [
                                    0.824692,
                                    1,
                                    0.824509
                                ],
                                "position": [
                                    -1.045104,
                                    2.5,
                                    1.741363
                                ],
                                "rotation": [
                                    0,
                                    0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "19475",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "20c2771c-3a17-4abf-856b-8edbdf1e2f7f",
                                "type": "build element/gypsum ceiling",
                                "style": "\u5176\u4ed6",
                                "size": [
                                    224.67600000000002,
                                    13.8576,
                                    224.73700000000002
                                ],
                                "scale": [
                                    1.195404,
                                    1,
                                    1.10538
                                ],
                                "position": [
                                    -0.309105,
                                    2.661424,
                                    -2.384401
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "19481",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "20c2771c-3a17-4abf-856b-8edbdf1e2f7f",
                                "type": "build element/gypsum ceiling",
                                "style": "\u5176\u4ed6",
                                "size": [
                                    224.67600000000002,
                                    13.8576,
                                    224.73700000000002
                                ],
                                "scale": [
                                    1.195404,
                                    1,
                                    1.10538
                                ],
                                "position": [
                                    -0.309105,
                                    2.661424,
                                    -2.384401
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "19481",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "db593061-992e-4fa9-b4f4-f4db7cc0ef25",
                                "type": "build element/ceiling molding",
                                "style": "\u5317\u6b27",
                                "size": [
                                    357.5,
                                    30.0,
                                    325.745
                                ],
                                "scale": [
                                    0.824692,
                                    1,
                                    0.824509
                                ],
                                "position": [
                                    -1.045104,
                                    2.5,
                                    1.741363
                                ],
                                "rotation": [
                                    0,
                                    0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "19475",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "db593061-992e-4fa9-b4f4-f4db7cc0ef25",
                                "type": "build element/ceiling molding",
                                "style": "\u5317\u6b27",
                                "size": [
                                    357.5,
                                    30.0,
                                    325.745
                                ],
                                "scale": [
                                    0.824692,
                                    1,
                                    0.824509
                                ],
                                "position": [
                                    -1.045104,
                                    2.5,
                                    1.741363
                                ],
                                "rotation": [
                                    0,
                                    0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "19475",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "20c2771c-3a17-4abf-856b-8edbdf1e2f7f",
                                "type": "build element/gypsum ceiling",
                                "style": "\u5176\u4ed6",
                                "size": [
                                    224.67600000000002,
                                    13.8576,
                                    224.73700000000002
                                ],
                                "scale": [
                                    1.195404,
                                    1,
                                    1.10538
                                ],
                                "position": [
                                    -0.309105,
                                    2.661424,
                                    -2.384401
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "19481",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "20c2771c-3a17-4abf-856b-8edbdf1e2f7f",
                                "type": "build element/gypsum ceiling",
                                "style": "\u5176\u4ed6",
                                "size": [
                                    224.67600000000002,
                                    13.8576,
                                    224.73700000000002
                                ],
                                "scale": [
                                    1.195404,
                                    1,
                                    1.10538
                                ],
                                "position": [
                                    -0.309105,
                                    2.661424,
                                    -2.384401
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "19481",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            }
                        ],
                        "win": [],
                        "door": {
                            "Balcony": [
                                {
                                    "id": "1dbb3f82-5c6f-41ef-900e-9a436b252cde",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        203.555,
                                        172.29,
                                        18.1747
                                    ],
                                    "scale": [
                                        1.143337,
                                        1.218875,
                                        1
                                    ],
                                    "position": [
                                        -0.950672,
                                        0,
                                        3.7855
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17894",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "Balcony-5325",
                                    "unit_to_type": "Balcony",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                },
                                {
                                    "id": "1dbb3f82-5c6f-41ef-900e-9a436b252cde",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        203.555,
                                        172.29,
                                        18.1747
                                    ],
                                    "scale": [
                                        0.761797,
                                        1.218875,
                                        1
                                    ],
                                    "position": [
                                        -0.161892,
                                        0,
                                        -4.1965
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17960",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "Balcony-5439",
                                    "unit_to_type": "Balcony",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "entry": [
                                {
                                    "id": "3ad620eb-bb89-4e86-92b1-df46fd0a0029",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        1.074346,
                                        0.966714,
                                        1
                                    ],
                                    "position": [
                                        5.232998,
                                        0,
                                        -0.297224
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "18430",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "unit_to_room": "",
                                    "unit_to_type": "entry",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "Library": [
                                {
                                    "id": "f6818cb3-eb0d-4255-8dd6-c0e50f9084e0",
                                    "type": "door/entry/single swing door",
                                    "style": "Swedish",
                                    "size": [
                                        160.191,
                                        240.07999999999998,
                                        12.5
                                    ],
                                    "scale": [
                                        0.456641,
                                        0.899392,
                                        1
                                    ],
                                    "position": [
                                        4.000758,
                                        0,
                                        -1.7165
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "18092",
                                    "categories": [
                                        "69d013d3-354d-44af-bdfd-22a1181a8001"
                                    ],
                                    "category": "69d013d3-354d-44af-bdfd-22a1181a8001",
                                    "unit_to_room": "Library-5490",
                                    "unit_to_type": "Library",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "Kitchen": [
                                {
                                    "id": "1e8a476f-6902-4f3c-ad90-da73bede3334",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        280.891,
                                        188.26200000000003,
                                        12.5
                                    ],
                                    "scale": [
                                        0.293642,
                                        1.115467,
                                        1
                                    ],
                                    "position": [
                                        1.261002,
                                        0,
                                        -3.058504
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "18673",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "Kitchen-5469",
                                    "unit_to_type": "Kitchen",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "Bathroom": [
                                {
                                    "id": "32cd827e-3d58-428d-84ba-39c7ae518118",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.41528,
                                        1.016769,
                                        1
                                    ],
                                    "position": [
                                        -3.087704,
                                        0,
                                        -2.5075
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "19009",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/32cd827e-3d58-428d-84ba-39c7ae518118/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            1.274739,
                                            2.053975
                                        ],
                                        "seam": False,
                                        "material_id": "19076",
                                        "area": -1
                                    },
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "unit_to_room": "Bathroom-5454",
                                    "unit_to_type": "Bathroom",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "KidsRoom": [
                                {
                                    "id": "3ad620eb-bb89-4e86-92b1-df46fd0a0029",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.704455,
                                        1.051246,
                                        1
                                    ],
                                    "position": [
                                        -3.502943,
                                        0,
                                        -1.945372
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7034626523170564,
                                        0,
                                        0.7107322258031166
                                    ],
                                    "entityId": "18739",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "unit_to_room": "KidsRoom-5403",
                                    "unit_to_type": "KidsRoom",
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "SecondBedroom": [
                                {
                                    "id": "32cd827e-3d58-428d-84ba-39c7ae518118",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.631927,
                                        1.051246,
                                        1
                                    ],
                                    "position": [
                                        -3.481661,
                                        0,
                                        -0.0155
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "19080",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/32cd827e-3d58-428d-84ba-39c7ae518118/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            1.274739,
                                            2.053975
                                        ],
                                        "seam": False,
                                        "material_id": "19147",
                                        "area": -1
                                    },
                                    "unit_to_room": "SecondBedroom-5523",
                                    "unit_to_type": "SecondBedroom",
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ]
                        },
                        "background": []
                    },
                    "decorate": {},
                    "painting": {},
                    "group": [
                        {
                            "type": "Meeting",
                            "code": 112214,
                            "size": [
                                3.745438429599762,
                                0.9005970001220703,
                                2.2145559528808603
                            ],
                            "offset": [
                                0.03474579801750177,
                                0,
                                -0.6150099863281255
                            ],
                            "position": [
                                -1.7307240136718747,
                                0,
                                1.571854798017502
                            ],
                            "rotation": [
                                0,
                                0.7071067811865475,
                                0,
                                0.7071067811865476
                            ],
                            "size_min": [
                                2.37177001953125,
                                0.9005970001220703,
                                0.9845359802246094
                            ],
                            "size_rest": [
                                0.0,
                                0.7215800030517578,
                                1.230019972656251,
                                0.6520884070167541
                            ],
                            "obj_main": "28185ab5-70dd-40ba-bdc4-11fadab3b597",
                            "obj_type": "sofa/ multi seat sofa",
                            "obj_list": [
                                {
                                    "id": "28185ab5-70dd-40ba-bdc4-11fadab3b597",
                                    "type": "sofa/ multi seat sofa",
                                    "style": "Chinese Modern",
                                    "size": [
                                        237.177001953125,
                                        90.05970001220703,
                                        98.45359802246094
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -2.345734,
                                        0,
                                        1.537109
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24847",
                                    "categories": [
                                        "d2a64592-caa7-4ab1-877e-561323315774"
                                    ],
                                    "category": "d2a64592-caa7-4ab1-877e-561323315774",
                                    "relate": "wall",
                                    "group": "Meeting",
                                    "role": "sofa",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -2.345734,
                                        0,
                                        1.537109
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                },
                                {
                                    "id": "bd1951e3-0a39-4c33-bf8d-b7618c59fd38",
                                    "type": "rug/rug",
                                    "style": "Swedish",
                                    "size": [
                                        340.1090087890625,
                                        0.9301319718360901,
                                        239.9720001220703
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.638142,
                                        0,
                                        1.462197
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17494",
                                    "categories": [
                                        "cabb5091-b54f-4fe9-b990-a7ac1b1b2803"
                                    ],
                                    "category": "cabb5091-b54f-4fe9-b990-a7ac1b1b2803",
                                    "role": "rug",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.638142,
                                        0,
                                        1.462197
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.07491200000000028,
                                        0,
                                        0.7075920104980468
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ],
                                    "group": "Meeting"
                                },
                                {
                                    "id": "bfcc6663-f67a-499d-b5f6-ad7b9d075fb1",
                                    "type": "sofa/single seat sofa",
                                    "style": "Classic",
                                    "size": [
                                        129.20799255371094,
                                        68.88529968261719,
                                        116.03700256347656
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.269486,
                                        0,
                                        2.864389
                                    ],
                                    "rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "entityId": "17492",
                                    "categories": [
                                        "c2dcb449-4729-4cfe-9e38-1fc1453211a5"
                                    ],
                                    "category": "c2dcb449-4729-4cfe-9e38-1fc1453211a5",
                                    "relate": "",
                                    "group": "Meeting",
                                    "role": "side sofa",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.269486,
                                        0,
                                        2.864389
                                    ],
                                    "origin_rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "normal_position": [
                                        -1.3272799999999998,
                                        0,
                                        1.0762480000000008
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.7071067811865476,
                                        0,
                                        0.7071067811865475
                                    ]
                                },
                                {
                                    "id": "e0a6d319-ee75-4fff-a745-c35e837c8133",
                                    "type": "sofa/single seat sofa",
                                    "style": "Contemporary",
                                    "size": [
                                        93.71269989013672,
                                        52.59120178222656,
                                        82.74240112304688
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.159821,
                                        0,
                                        0.385171
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17493",
                                    "categories": [
                                        "182f769f-981f-4a8e-9aef-7efe9917cf19"
                                    ],
                                    "category": "182f769f-981f-4a8e-9aef-7efe9917cf19",
                                    "group": "Meeting",
                                    "role": "side sofa",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.159821,
                                        0,
                                        0.385171
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        1.1519380000000006,
                                        0,
                                        1.185913
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ]
                                },
                                {
                                    "id": "fd7ed7fe-7b9d-432a-9ae0-221d9dbd88b8",
                                    "type": "table/night table",
                                    "style": "Contemporary",
                                    "size": [
                                        45.0,
                                        46.0,
                                        46.41960144042969
                                    ],
                                    "scale": [
                                        1.1111,
                                        1.1111,
                                        1.11111
                                    ],
                                    "position": [
                                        -2.282782,
                                        0,
                                        -0.042978
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17495",
                                    "categories": [
                                        "5ad47fd2-b143-4af2-9961-e88a57b4a337"
                                    ],
                                    "category": "5ad47fd2-b143-4af2-9961-e88a57b4a337",
                                    "group": "Meeting",
                                    "role": "side table",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -2.282782,
                                        0,
                                        -0.042978
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        1.580087,
                                        0,
                                        0.06295199999999967
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ]
                                },
                                {
                                    "id": "888ffe40-ad39-4bee-8c4c-ed03c3369533",
                                    "type": "table/coffee table - rectangular",
                                    "style": "Contemporary",
                                    "size": [
                                        115.7979965209961,
                                        29.58639907836914,
                                        82.75080108642578
                                    ],
                                    "scale": [
                                        1,
                                        1.000122,
                                        1
                                    ],
                                    "position": [
                                        -1.166906,
                                        0,
                                        1.554002
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17497",
                                    "categories": [
                                        "9eaee326-16c4-4244-87d5-38e7b57a4e38"
                                    ],
                                    "category": "9eaee326-16c4-4244-87d5-38e7b57a4e38",
                                    "group": "Meeting",
                                    "role": "table",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.166906,
                                        0,
                                        1.554002
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        -0.016892999999999714,
                                        0,
                                        1.1788280000000002
                                    ],
                                    "normal_rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ]
                                },
                                {
                                    "id": "fd7ed7fe-7b9d-432a-9ae0-221d9dbd88b8",
                                    "type": "table/night table",
                                    "style": "Contemporary",
                                    "size": [
                                        45.0,
                                        46.0,
                                        46.41960144042969
                                    ],
                                    "scale": [
                                        1.1111,
                                        1.1111,
                                        1.11111
                                    ],
                                    "position": [
                                        -2.484725,
                                        0,
                                        3.143221
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17501",
                                    "categories": [
                                        "5ad47fd2-b143-4af2-9961-e88a57b4a337"
                                    ],
                                    "category": "5ad47fd2-b143-4af2-9961-e88a57b4a337",
                                    "group": "Meeting",
                                    "role": "side table",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -2.484725,
                                        0,
                                        3.143221
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        -1.606112,
                                        0,
                                        -0.13899099999999942
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ]
                                },
                                {
                                    "id": "588c5563-4107-4a0f-810f-ef7ad22ba249",
                                    "type": "lighting/desk lamp",
                                    "style": "Contemporary",
                                    "size": [
                                        40.73910140991211,
                                        53.42559814453125,
                                        39.39360046386719
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -2.237328,
                                        0.511109,
                                        -0.049637
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17496",
                                    "categories": [
                                        "28bf7153-4059-4ff2-aeb0-5b4f35b7133a"
                                    ],
                                    "category": "28bf7153-4059-4ff2-aeb0-5b4f35b7133a",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "fd7ed7fe-7b9d-432a-9ae0-221d9dbd88b8",
                                    "relate_role": "side table",
                                    "relate_group": "Meeting",
                                    "relate_position": [
                                        -2.282782,
                                        0,
                                        -0.042978
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -2.237328,
                                        0.511109,
                                        -0.049637
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        1.586746,
                                        0.511109,
                                        0.10840599999999956
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Meeting"
                                },
                                {
                                    "id": "31a9b812-9c28-4c3d-b49d-d805170ac59a",
                                    "type": "300 - on top of others",
                                    "style": "Other",
                                    "size": [
                                        51.11470031738281,
                                        34.53850173950195,
                                        25.81369972229004
                                    ],
                                    "scale": [
                                        0.877961,
                                        0.877987,
                                        0.877874
                                    ],
                                    "position": [
                                        -1.12395,
                                        0.2028,
                                        1.335227
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17498",
                                    "categories": [
                                        "f118f5f8-38f9-49d0-87be-16c35e96bb6c"
                                    ],
                                    "category": "f118f5f8-38f9-49d0-87be-16c35e96bb6c",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "888ffe40-ad39-4bee-8c4c-ed03c3369533",
                                    "relate_role": "table",
                                    "relate_group": "Meeting",
                                    "relate_position": [
                                        -1.166906,
                                        0,
                                        1.554002
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.12395,
                                        0.2028,
                                        1.335227
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        0.20188200000000045,
                                        0.2028,
                                        1.2217840000000002
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Meeting"
                                },
                                {
                                    "id": "909c8022-3017-4c09-8616-33c4e4c18cdb",
                                    "type": "300 - on top of others",
                                    "style": "Other",
                                    "size": [
                                        35.0,
                                        18.54800033569336,
                                        35.0
                                    ],
                                    "scale": [
                                        1,
                                        1.000108,
                                        1
                                    ],
                                    "position": [
                                        -1.112352,
                                        0.2959,
                                        1.749527
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17499",
                                    "categories": [
                                        "b66bcce5-a1e4-482d-a3f7-f0241a0d26a7"
                                    ],
                                    "category": "b66bcce5-a1e4-482d-a3f7-f0241a0d26a7",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "888ffe40-ad39-4bee-8c4c-ed03c3369533",
                                    "relate_role": "table",
                                    "relate_group": "Meeting",
                                    "relate_position": [
                                        -1.166906,
                                        0,
                                        1.554002
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.112352,
                                        0.2959,
                                        1.749527
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        -0.21241799999999963,
                                        0.2959,
                                        1.2333820000000002
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Meeting"
                                },
                                {
                                    "id": "588c5563-4107-4a0f-810f-ef7ad22ba249",
                                    "type": "lighting/desk lamp",
                                    "style": "Contemporary",
                                    "size": [
                                        40.73910140991211,
                                        53.42559814453125,
                                        39.39360046386719
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -2.404342,
                                        0.511109,
                                        3.13823
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17502",
                                    "categories": [
                                        "28bf7153-4059-4ff2-aeb0-5b4f35b7133a"
                                    ],
                                    "category": "28bf7153-4059-4ff2-aeb0-5b4f35b7133a",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "fd7ed7fe-7b9d-432a-9ae0-221d9dbd88b8",
                                    "relate_role": "side table",
                                    "relate_group": "Meeting",
                                    "relate_position": [
                                        -2.484725,
                                        0,
                                        3.143221
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -2.404342,
                                        0.511109,
                                        3.13823
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        -1.601121,
                                        0.511109,
                                        -0.05860799999999954
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Meeting"
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0.05999800988769466,
                                0,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0.281,
                                0,
                                0
                            ],
                            "neighbor_more": [
                                0,
                                0.281,
                                0.5,
                                0
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "switch": 0,
                            "region_direct": 1,
                            "region_center": [],
                            "back_p1": [
                                -2.898,
                                -0.076
                            ],
                            "back_p2": [
                                -2.898,
                                3.445
                            ],
                            "back_depth": 0.0,
                            "back_front": 2.2145559528808603,
                            "back_angle": 1.5707963267948966,
                            "expand": [
                                -2.898,
                                -0.3008644167823793,
                                -0.6234440471191398,
                                3.725
                            ]
                        },
                        {
                            "type": "Media",
                            "code": 1000,
                            "size": [
                                1.3143800354003907,
                                1.4555180310058593,
                                0.06550039768218995
                            ],
                            "offset": [
                                -0.0,
                                0,
                                -0.0
                            ],
                            "position": [
                                0.901248,
                                0,
                                1.832774
                            ],
                            "rotation": [
                                0,
                                -0.7071067811865475,
                                0,
                                0.7071067811865476
                            ],
                            "size_min": [
                                1.3143800354003907,
                                0.6860130310058594,
                                0.06550039768218995
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.0,
                                0.0
                            ],
                            "obj_main": "91e6da58-461f-483a-a0d0-114cefccea89",
                            "obj_type": "electronics/TV - wall-attached",
                            "obj_list": [
                                {
                                    "id": "91e6da58-461f-483a-a0d0-114cefccea89",
                                    "type": "electronics/TV - wall-attached",
                                    "style": "Chinese Modern",
                                    "size": [
                                        131.43800354003906,
                                        68.60130310058594,
                                        6.550039768218994
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        0.901248,
                                        0.769505,
                                        1.832774
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24848",
                                    "categories": [
                                        "438a813a-502e-4376-893d-eac6523e1ca7"
                                    ],
                                    "category": "438a813a-502e-4376-893d-eac6523e1ca7",
                                    "relate": "wall",
                                    "group": "Media",
                                    "role": "tv",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        0.901248,
                                        0.769505,
                                        1.832774
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0.769505,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "neighbor_more": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "switch": 0,
                            "region_direct": 0,
                            "region_center": [],
                            "back_p1": [],
                            "back_p2": [],
                            "back_depth": 0,
                            "back_front": 0.06550039768218995,
                            "back_angle": 0
                        },
                        {
                            "type": "Dining",
                            "code": 145,
                            "size": [
                                1.8486590072631837,
                                0.7253939819335937,
                                1.4785000610351562
                            ],
                            "offset": [
                                -0.003450000000000064,
                                0,
                                -0.0
                            ],
                            "position": [
                                -0.8106099999999999,
                                0,
                                -2.455646
                            ],
                            "rotation": [
                                0,
                                -0.0,
                                0,
                                1.0
                            ],
                            "size_min": [
                                0.8582990264892578,
                                0.7253939819335937,
                                1.4785000610351562
                            ],
                            "size_rest": [
                                0.0,
                                0.49172999038696286,
                                0.0,
                                0.498629990386963
                            ],
                            "obj_main": "29390fb0-db51-45de-ab1d-d382327aa05d",
                            "obj_type": "table/dining table - square",
                            "obj_list": [
                                {
                                    "id": "29390fb0-db51-45de-ab1d-d382327aa05d",
                                    "type": "table/dining table - square",
                                    "style": "Chinese Modern",
                                    "size": [
                                        85.82990264892578,
                                        72.53939819335938,
                                        147.85000610351562
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -0.81406,
                                        0,
                                        -2.455646
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "24836",
                                    "categories": [
                                        "9161c9e8-49e8-48bd-9ee8-0c75dd267413"
                                    ],
                                    "category": "9161c9e8-49e8-48bd-9ee8-0c75dd267413",
                                    "group": "Dining",
                                    "role": "table",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -0.81406,
                                        0,
                                        -2.455646
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                },
                                {
                                    "id": "4a102505-62b9-4126-82fe-44d517b952ad",
                                    "type": "chair/chair",
                                    "style": "Chinese Modern",
                                    "size": [
                                        40.94929885864258,
                                        95.35690307617188,
                                        51.39590072631836
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -0.14566,
                                        0,
                                        -2.786846
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24837",
                                    "categories": [
                                        "30c7fefc-a32e-48e1-9458-dfab61595dc7"
                                    ],
                                    "category": "30c7fefc-a32e-48e1-9458-dfab61595dc7",
                                    "group": "Dining",
                                    "role": "chair",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -0.14566,
                                        0,
                                        -2.786846
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.6684,
                                        0,
                                        -0.33119999999999994
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ]
                                },
                                {
                                    "id": "4a102505-62b9-4126-82fe-44d517b952ad",
                                    "type": "chair/chair",
                                    "style": "Chinese Modern",
                                    "size": [
                                        40.94929885864258,
                                        95.35690307617188,
                                        51.39590072631836
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -0.14326,
                                        0,
                                        -2.153646
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24838",
                                    "categories": [
                                        "30c7fefc-a32e-48e1-9458-dfab61595dc7"
                                    ],
                                    "category": "30c7fefc-a32e-48e1-9458-dfab61595dc7",
                                    "group": "Dining",
                                    "role": "chair",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -0.14326,
                                        0,
                                        -2.153646
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.6708000000000001,
                                        0,
                                        0.30200000000000005
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ]
                                },
                                {
                                    "id": "4a102505-62b9-4126-82fe-44d517b952ad",
                                    "type": "chair/chair",
                                    "style": "Chinese Modern",
                                    "size": [
                                        40.94929885864258,
                                        95.35690307617188,
                                        51.39590072631836
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.46926,
                                        0,
                                        -2.788046
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24839",
                                    "categories": [
                                        "30c7fefc-a32e-48e1-9458-dfab61595dc7"
                                    ],
                                    "category": "30c7fefc-a32e-48e1-9458-dfab61595dc7",
                                    "group": "Dining",
                                    "role": "chair",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.46926,
                                        0,
                                        -2.788046
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        -0.6552,
                                        0,
                                        -0.3323999999999998
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ]
                                },
                                {
                                    "id": "4a102505-62b9-4126-82fe-44d517b952ad",
                                    "type": "chair/chair",
                                    "style": "Chinese Modern",
                                    "size": [
                                        40.94929885864258,
                                        95.35690307617188,
                                        51.39590072631836
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.47796,
                                        0,
                                        -2.135746
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24840",
                                    "categories": [
                                        "30c7fefc-a32e-48e1-9458-dfab61595dc7"
                                    ],
                                    "category": "30c7fefc-a32e-48e1-9458-dfab61595dc7",
                                    "group": "Dining",
                                    "role": "chair",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.47796,
                                        0,
                                        -2.135746
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        -0.6638999999999999,
                                        0,
                                        0.3199000000000001
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ]
                                },
                                {
                                    "id": "554fc4b7-829b-4419-9185-5ec8300de856",
                                    "type": "plants/plants - on top of others",
                                    "style": "Other",
                                    "size": [
                                        17.06839942932129,
                                        45.35860061645508,
                                        21.595199584960938
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -0.78616,
                                        0.7254,
                                        -2.418146
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24841",
                                    "categories": [
                                        "f168f93c-351e-4224-aa36-b08441933739"
                                    ],
                                    "category": "f168f93c-351e-4224-aa36-b08441933739",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "29390fb0-db51-45de-ab1d-d382327aa05d",
                                    "relate_role": "table",
                                    "relate_group": "Dining",
                                    "relate_position": [
                                        -0.81406,
                                        0,
                                        -2.455646
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -0.78616,
                                        0.7254,
                                        -2.418146
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.027900000000000036,
                                        0.7254,
                                        0.03750000000000009
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Dining"
                                },
                                {
                                    "id": "a3bcc47b-9d8b-44ec-b624-aa5e5b86efee",
                                    "type": "accessory/kitchen decoration-horizontal",
                                    "style": "Other",
                                    "size": [
                                        33.838199615478516,
                                        5.21619987487793,
                                        19.52039909362793
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.09166,
                                        0.7254,
                                        -2.781046
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24842",
                                    "categories": [
                                        "642b2c31-4dc9-4880-9308-d225a7f876ca"
                                    ],
                                    "category": "642b2c31-4dc9-4880-9308-d225a7f876ca",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "29390fb0-db51-45de-ab1d-d382327aa05d",
                                    "relate_role": "table",
                                    "relate_group": "Dining",
                                    "relate_position": [
                                        -0.81406,
                                        0,
                                        -2.455646
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.09166,
                                        0.7254,
                                        -2.781046
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        -0.27760000000000007,
                                        0.7254,
                                        -0.3253999999999997
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Dining"
                                },
                                {
                                    "id": "a3bcc47b-9d8b-44ec-b624-aa5e5b86efee",
                                    "type": "accessory/kitchen decoration-horizontal",
                                    "style": "Other",
                                    "size": [
                                        33.838199615478516,
                                        5.21619987487793,
                                        19.52039909362793
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.08886,
                                        0.7254,
                                        -2.133046
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24843",
                                    "categories": [
                                        "642b2c31-4dc9-4880-9308-d225a7f876ca"
                                    ],
                                    "category": "642b2c31-4dc9-4880-9308-d225a7f876ca",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "29390fb0-db51-45de-ab1d-d382327aa05d",
                                    "relate_role": "table",
                                    "relate_group": "Dining",
                                    "relate_position": [
                                        -0.81406,
                                        0,
                                        -2.455646
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.08886,
                                        0.7254,
                                        -2.133046
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        -0.27479999999999993,
                                        0.7254,
                                        0.3226
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Dining"
                                },
                                {
                                    "id": "a3bcc47b-9d8b-44ec-b624-aa5e5b86efee",
                                    "type": "accessory/kitchen decoration-horizontal",
                                    "style": "Other",
                                    "size": [
                                        33.838199615478516,
                                        5.21619987487793,
                                        19.52039909362793
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -0.52436,
                                        0.7254,
                                        -2.781946
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24844",
                                    "categories": [
                                        "642b2c31-4dc9-4880-9308-d225a7f876ca"
                                    ],
                                    "category": "642b2c31-4dc9-4880-9308-d225a7f876ca",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "29390fb0-db51-45de-ab1d-d382327aa05d",
                                    "relate_role": "table",
                                    "relate_group": "Dining",
                                    "relate_position": [
                                        -0.81406,
                                        0,
                                        -2.455646
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -0.52436,
                                        0.7254,
                                        -2.781946
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.28969999999999996,
                                        0.7254,
                                        -0.3262999999999998
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Dining"
                                },
                                {
                                    "id": "a3bcc47b-9d8b-44ec-b624-aa5e5b86efee",
                                    "type": "accessory/kitchen decoration-horizontal",
                                    "style": "Other",
                                    "size": [
                                        33.838199615478516,
                                        5.21619987487793,
                                        19.52039909362793
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -0.52396,
                                        0.7254,
                                        -2.154046
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24845",
                                    "categories": [
                                        "642b2c31-4dc9-4880-9308-d225a7f876ca"
                                    ],
                                    "category": "642b2c31-4dc9-4880-9308-d225a7f876ca",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "29390fb0-db51-45de-ab1d-d382327aa05d",
                                    "relate_role": "table",
                                    "relate_group": "Dining",
                                    "relate_position": [
                                        -0.81406,
                                        0,
                                        -2.455646
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -0.52396,
                                        0.7254,
                                        -2.154046
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.2901,
                                        0.7254,
                                        0.3016000000000001
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865477
                                    ],
                                    "group": "Dining"
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "neighbor_more": [
                                0.4,
                                0.4,
                                0.4,
                                0.4
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 1,
                            "switch": 0,
                            "region_direct": 0,
                            "region_center": [],
                            "back_p1": [],
                            "back_p2": [],
                            "back_depth": 0,
                            "back_front": 1.4785000610351562,
                            "back_angle": 0
                        },
                        {
                            "type": "Wall",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "6bb7851d-3fb4-46c5-b51b-e513a55139ef",
                                    "type": "art/art - wall-attached",
                                    "style": "Chinese Modern",
                                    "size": [
                                        216.78199768066406,
                                        79.01609802246094,
                                        4.680019855499268
                                    ],
                                    "scale": [
                                        1.014844,
                                        1.107103,
                                        0.854701
                                    ],
                                    "position": [
                                        -2.818002,
                                        1.161454,
                                        1.754701
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17491",
                                    "categories": [
                                        "85278e9e-3e38-4070-a0a3-6a798ae51b7a"
                                    ],
                                    "category": "85278e9e-3e38-4070-a0a3-6a798ae51b7a",
                                    "role": "art",
                                    "count": 1,
                                    "relate": "28185ab5-70dd-40ba-bdc4-11fadab3b597",
                                    "relate_group": "Meeting",
                                    "relate_position": [
                                        -2.345734,
                                        0,
                                        1.537109
                                    ],
                                    "relate_role": "sofa",
                                    "origin_position": [
                                        -2.818002,
                                        1.161454,
                                        1.754701
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        -0.21759200000000015,
                                        1.161454,
                                        -0.47226799999999963
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Ceiling",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Floor",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Door",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "3ad620eb-bb89-4e86-92b1-df46fd0a0029",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        1.074346,
                                        0.966714,
                                        1
                                    ],
                                    "position": [
                                        5.232998,
                                        0,
                                        -0.297224
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "18430",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "unit_to_room": "",
                                    "unit_to_type": "",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                },
                                {
                                    "id": "f6818cb3-eb0d-4255-8dd6-c0e50f9084e0",
                                    "type": "door/entry/single swing door",
                                    "style": "Swedish",
                                    "size": [
                                        160.191,
                                        240.07999999999998,
                                        12.5
                                    ],
                                    "scale": [
                                        0.456641,
                                        0.899392,
                                        1
                                    ],
                                    "position": [
                                        4.000758,
                                        0,
                                        -1.7165
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "18092",
                                    "categories": [
                                        "69d013d3-354d-44af-bdfd-22a1181a8001"
                                    ],
                                    "category": "69d013d3-354d-44af-bdfd-22a1181a8001",
                                    "unit_to_room": "Library-5490",
                                    "unit_to_type": "Library",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                },
                                {
                                    "id": "1e8a476f-6902-4f3c-ad90-da73bede3334",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        280.891,
                                        188.26200000000003,
                                        12.5
                                    ],
                                    "scale": [
                                        0.293642,
                                        1.115467,
                                        1
                                    ],
                                    "position": [
                                        1.261002,
                                        0,
                                        -3.058504
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "18673",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "Kitchen-5469",
                                    "unit_to_type": "Kitchen",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                },
                                {
                                    "id": "1dbb3f82-5c6f-41ef-900e-9a436b252cde",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        203.555,
                                        172.29,
                                        18.1747
                                    ],
                                    "scale": [
                                        0.761797,
                                        1.218875,
                                        1
                                    ],
                                    "position": [
                                        -0.161892,
                                        0,
                                        -4.1965
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17960",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "Balcony-5439",
                                    "unit_to_type": "Balcony",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                },
                                {
                                    "id": "32cd827e-3d58-428d-84ba-39c7ae518118",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.41528,
                                        1.016769,
                                        1
                                    ],
                                    "position": [
                                        -3.087704,
                                        0,
                                        -2.5075
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "19009",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/32cd827e-3d58-428d-84ba-39c7ae518118/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            1.274739,
                                            2.053975
                                        ],
                                        "seam": False,
                                        "material_id": "19076",
                                        "area": -1
                                    },
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "unit_to_room": "Bathroom-5454",
                                    "unit_to_type": "Bathroom",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                },
                                {
                                    "id": "3ad620eb-bb89-4e86-92b1-df46fd0a0029",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.704455,
                                        1.051246,
                                        1
                                    ],
                                    "position": [
                                        -3.502943,
                                        0,
                                        -1.945372
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7034626523170564,
                                        0,
                                        0.7107322258031166
                                    ],
                                    "entityId": "18739",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "unit_to_room": "KidsRoom-5403",
                                    "unit_to_type": "KidsRoom",
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                },
                                {
                                    "id": "32cd827e-3d58-428d-84ba-39c7ae518118",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.631927,
                                        1.051246,
                                        1
                                    ],
                                    "position": [
                                        -3.481661,
                                        0,
                                        -0.0155
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "19080",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/32cd827e-3d58-428d-84ba-39c7ae518118/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            1.274739,
                                            2.053975
                                        ],
                                        "seam": False,
                                        "material_id": "19147",
                                        "area": -1
                                    },
                                    "unit_to_room": "SecondBedroom-5523",
                                    "unit_to_type": "SecondBedroom",
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Window",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Background",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Customize",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        }
                    ],
                    "group_area": 11.113817840514958,
                    "source_house": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4",
                    "source_room": "LivingDiningRoom-5376",
                    "source_room_area": 39.9504450656,
                    "line_unit": [
                        {
                            "type": 1,
                            "score": 3,
                            "width": 3.52,
                            "depth": 2.2745559528808603,
                            "depth_all": [
                                [
                                    0.0,
                                    0.172,
                                    7.221004341860217
                                ],
                                [
                                    0.172,
                                    1,
                                    3.8919999999999995
                                ]
                            ],
                            "height": 0.901,
                            "angle": 0,
                            "p1": [
                                -2.898,
                                -0.076
                            ],
                            "p2": [
                                -2.898,
                                3.445
                            ],
                            "score_pre": 2,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 2.2745559528808603,
                            "unit_index": 0,
                            "unit_depth": 2.275,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.281,
                            "depth": 2.2745559528808603,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    3.8919999999999995
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -2.898,
                                3.445
                            ],
                            "p2": [
                                -2.898,
                                3.725
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 2.2745559528808603,
                            "depth_post": 3.161,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 5,
                            "width": 3.161,
                            "depth": 0.28,
                            "depth_all": [
                                [
                                    0,
                                    0.005,
                                    5.747999999999999
                                ],
                                [
                                    0.005,
                                    0.324,
                                    6.173
                                ],
                                [
                                    0.324,
                                    0.613,
                                    7.861999999999999
                                ],
                                [
                                    0.613,
                                    1,
                                    7.437
                                ]
                            ],
                            "height": 0.901,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -2.898,
                                3.725
                            ],
                            "p2": [
                                0.263,
                                3.725
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.281,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 4.025,
                            "unit_margin": 0.28,
                            "unit_edge": 1,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p1_original": [
                                -2.838,
                                3.725
                            ],
                            "width_original": 3.101
                        },
                        {
                            "type": 3,
                            "score": 2,
                            "width": 0.33,
                            "depth": 0.28,
                            "depth_all": [],
                            "height": 0.901,
                            "angle": 1.5707963267948966,
                            "p1": [
                                0.263,
                                3.725
                            ],
                            "p2": [
                                0.593,
                                3.725
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.28,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.40099999999999997,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    0.05024688279301738,
                                    7.437
                                ],
                                [
                                    0.05024688279301738,
                                    1.0,
                                    7.861999999999999
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                0.593,
                                3.725
                            ],
                            "p2": [
                                0.994,
                                3.725
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 1.236,
                            "depth": 0.40099999999999997,
                            "depth_all": [
                                [
                                    -0.0,
                                    1,
                                    3.8919999999999995
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                0.994,
                                3.725
                            ],
                            "p2": [
                                0.994,
                                2.49
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.40099999999999997,
                            "depth_post": 0.2,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 2,
                            "width": 1.314,
                            "depth": 0.06550039768218996,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    3.8919999999999995
                                ]
                            ],
                            "height": 1.456,
                            "angle": 3.141592653589793,
                            "p1": [
                                0.994,
                                2.49
                            ],
                            "p2": [
                                0.994,
                                1.176
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 1,
                            "unit_depth": 0.066,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.646,
                            "depth": 0.2,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    3.8919999999999995
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                0.994,
                                1.176
                            ],
                            "p2": [
                                0.994,
                                0.53
                            ],
                            "score_pre": 1,
                            "score_post": 2,
                            "depth_pre": 0.2,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 2.616,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0.0,
                                    0.07987385321100919,
                                    3.1755970248982544
                                ],
                                [
                                    0.07987385321100919,
                                    1,
                                    2.1860000000000004
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                0.994,
                                0.53
                            ],
                            "p2": [
                                3.6100000000000003,
                                0.53
                            ],
                            "score_pre": 2,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": 5,
                            "width": 1.5630000000000002,
                            "depth": 0.85,
                            "depth_all": [],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                3.6100000000000003,
                                0.53
                            ],
                            "p2": [
                                5.173,
                                0.53
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 1.5630000000000002,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 5,
                            "width": 1.5630000000000002,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 3.141592653589793,
                            "p1": [
                                5.173,
                                0.53
                            ],
                            "p2": [
                                5.173,
                                -1.033
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 1.5630000000000002,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p1_original": [
                                5.173,
                                0.439
                            ],
                            "width_original": 1.473
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.623,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    0.318,
                                    8.621718000000001
                                ],
                                [
                                    0.318,
                                    1.0,
                                    0.8064911078450017
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                5.173,
                                -1.033
                            ],
                            "p2": [
                                5.173,
                                -1.657
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.756,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    2.1860000000000004
                                ]
                            ],
                            "height": 0,
                            "angle": -1.5707963267948966,
                            "p1": [
                                5.173,
                                -1.657
                            ],
                            "p2": [
                                4.417,
                                -1.657
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.6,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 2,
                            "width": 0.831,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": -1.5707963267948966,
                            "p1": [
                                4.417,
                                -1.657
                            ],
                            "p2": [
                                3.585,
                                -1.657
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 1,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "Library-5490",
                            "unit_to_type": "Library"
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 2.384,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    2.1860000000000004
                                ]
                            ],
                            "height": 0,
                            "angle": -1.5707963267948966,
                            "p1": [
                                3.585,
                                -1.657
                            ],
                            "p2": [
                                1.201,
                                -1.657
                            ],
                            "score_pre": 1,
                            "score_post": 2,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.947,
                            "depth": 0.6613436019511616,
                            "depth_all": [
                                [
                                    0.0,
                                    0.521,
                                    4.218947846983317
                                ],
                                [
                                    0.521,
                                    0.843,
                                    4.023435517999999
                                ],
                                [
                                    0.843,
                                    1,
                                    3.0349999999999997
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                1.201,
                                -1.65
                            ],
                            "p2": [
                                1.201,
                                -2.596
                            ],
                            "score_pre": 2,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 2,
                            "width": 0.925,
                            "depth": 0.6613436019511616,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 3.141592653589793,
                            "p1": [
                                1.201,
                                -2.596
                            ],
                            "p2": [
                                1.201,
                                -3.521
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 2,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "Kitchen-5469",
                            "unit_to_type": "Kitchen"
                        },
                        {
                            "type": 6,
                            "score": 2,
                            "width": 0.386,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    3.0349999999999997
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                1.201,
                                -3.521
                            ],
                            "p2": [
                                1.201,
                                -3.906373376623377
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                1.201,
                                -3.906373376623377
                            ],
                            "p2": [
                                1.201,
                                -4.136
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0,
                            "depth_post": 0,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 8,
                            "width": 3.0360000000000005,
                            "depth": 0.386,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": -1.5707963267948966,
                            "p1": [
                                1.201,
                                -4.136
                            ],
                            "p2": [
                                -1.834,
                                -4.136
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.23,
                            "depth_post": 0.23,
                            "unit_index": 3,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "Balcony-5439",
                            "unit_to_type": "Balcony",
                            "p2_original": [
                                -0.987,
                                -4.136
                            ],
                            "width_original": 1.651,
                            "p1_original": [
                                0.663,
                                -4.136
                            ]
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 2.8,
                            "angle": 0,
                            "p1": [
                                -1.834,
                                -4.137
                            ],
                            "p2": [
                                -1.834,
                                -3.9069999999999996
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 2,
                            "width": 0.712,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    0.6123511235955056,
                                    3.0349999999999997
                                ],
                                [
                                    0.6123511235955056,
                                    1.0,
                                    2.6100026092143453
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -1.834,
                                -3.9069999999999996
                            ],
                            "p2": [
                                -1.834,
                                -3.195
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 1.9486590072631838,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 3,
                            "width": 0.747,
                            "depth": 1.9486590072631838,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    2.6100026092143453
                                ]
                            ],
                            "height": 0.725,
                            "angle": 0,
                            "p1": [
                                -1.834,
                                -3.195
                            ],
                            "p2": [
                                -1.834,
                                -2.448
                            ],
                            "score_pre": 1,
                            "score_post": 2,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 2,
                            "unit_depth": 1.949,
                            "unit_margin": 0.1,
                            "unit_edge": 1,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.938,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0.0,
                                    0.299,
                                    5.748
                                ],
                                [
                                    0.299,
                                    1,
                                    6.173
                                ]
                            ],
                            "height": 0,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -1.834,
                                -2.448
                            ],
                            "p2": [
                                -2.772,
                                -2.448
                            ],
                            "score_pre": 2,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 5,
                            "width": 0.677,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -2.772,
                                -2.448
                            ],
                            "p2": [
                                -3.449,
                                -2.448
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 1.002,
                            "unit_index": 4,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "Bathroom-5454",
                            "unit_to_type": "Bathroom",
                            "p2_original": [
                                -3.403,
                                -2.448
                            ],
                            "width_original": 0.631
                        },
                        {
                            "type": 2,
                            "score": 5,
                            "width": 1.002,
                            "depth": 0.677,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 0,
                            "p1": [
                                -3.449,
                                -2.448
                            ],
                            "p2": [
                                -3.449,
                                -1.445
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.677,
                            "depth_post": 0.85,
                            "unit_index": 5,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "KidsRoom-5403",
                            "unit_to_type": "KidsRoom"
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.948,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    0.226,
                                    7.0837291078449995
                                ],
                                [
                                    0.226,
                                    0.487,
                                    8.621718000000001
                                ],
                                [
                                    0.487,
                                    1.0,
                                    7.771722341860217
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -3.449,
                                -1.445
                            ],
                            "p2": [
                                -3.449,
                                -0.498
                            ],
                            "score_pre": 1,
                            "score_post": 2,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 5,
                            "score": 6,
                            "width": 0.497,
                            "depth": 0.422,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    -0.427884
                                ]
                            ],
                            "height": 0,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -3.449,
                                -0.498
                            ],
                            "p2": [
                                -3.945,
                                -0.498
                            ],
                            "score_pre": 2,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.422,
                            "unit_index": 0,
                            "unit_depth": 0.422,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": 8,
                            "width": 0.422,
                            "depth": 0.497,
                            "depth_all": [
                                [
                                    0.0,
                                    1.0,
                                    0.059999830575000246
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -3.945,
                                -0.498
                            ],
                            "p2": [
                                -3.945,
                                -0.076
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.497,
                            "depth_post": 1.047,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 6,
                            "width": 1.047,
                            "depth": 0.422,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -3.945,
                                -0.076
                            ],
                            "p2": [
                                -2.898,
                                -0.076
                            ],
                            "score_pre": 4,
                            "score_post": 2,
                            "depth_pre": 0.422,
                            "depth_post": 0.85,
                            "unit_index": 6,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "SecondBedroom-5523",
                            "unit_to_type": "SecondBedroom",
                            "p2_original": [
                                -3.028,
                                -0.076
                            ],
                            "width_original": 0.907,
                            "p1_original": [
                                -3.935,
                                -0.076
                            ]
                        }
                    ]
                }
            ],
            "layout_mesh": [
                {
                    "id": "db593061-992e-4fa9-b4f4-f4db7cc0ef25",
                    "type": "build element/ceiling molding",
                    "style": "\u5317\u6b27",
                    "size": [
                        357.5,
                        30.0,
                        325.745
                    ],
                    "scale": [
                        0.824692,
                        1,
                        0.824509
                    ],
                    "position": [
                        -1.045104,
                        2.5,
                        1.741363
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "19475",
                    "categories": [
                        "91e376e7-ebdb-43cc-a230-827a367cf18e"
                    ],
                    "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                    "role": "ceiling"
                },
                {
                    "id": "20c2771c-3a17-4abf-856b-8edbdf1e2f7f",
                    "type": "build element/gypsum ceiling",
                    "style": "\u5176\u4ed6",
                    "size": [
                        224.67600000000002,
                        13.8576,
                        224.73700000000002
                    ],
                    "scale": [
                        1.195404,
                        1,
                        1.10538
                    ],
                    "position": [
                        -0.309105,
                        2.661424,
                        -2.384401
                    ],
                    "rotation": [
                        0,
                        1.0,
                        0,
                        6.123233995736766e-17
                    ],
                    "entityId": "19481",
                    "categories": [
                        "91e376e7-ebdb-43cc-a230-827a367cf18e"
                    ],
                    "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                    "role": "ceiling"
                }
            ]
        },
        "KidsRoom-5403": {
            "room_type": "KidsRoom",
            "room_style": "Swedish",
            "room_area": 11.498968100451997,
            "room_height": 2.8,
            "layout_scheme": [
                {
                    "code": 20200,
                    "score": 80,
                    "type": "KidsRoom",
                    "style": "Swedish",
                    "area": 11.498968100451997,
                    "material": {
                        "id": "KidsRoom-5403",
                        "type": "KidsRoom",
                        "floor": [
                            {
                                "jid": "f2dfc41c-cf44-417f-a439-e3f455e6827d",
                                "texture_url": "",
                                "color": None,
                                "colorMode": "color",
                                "size": [
                                    1,
                                    1
                                ],
                                "seam": False,
                                "material_id": "24675",
                                "area": 10.857054312014501
                            }
                        ],
                        "wall": [
                            {
                                "jid": "0e9773b3-48e3-4813-8c3b-743c8f949f5a",
                                "texture_url": "",
                                "color": None,
                                "colorMode": "color",
                                "size": [
                                    1,
                                    1
                                ],
                                "seam": False,
                                "material_id": "24736",
                                "area": 14.845846549454864,
                                "wall": [
                                    [
                                        -6.306002,
                                        -4.4275
                                    ],
                                    [
                                        -6.306002,
                                        -0.557616
                                    ]
                                ],
                                "offset": True,
                                "alias": "0e9773b3-48e3-4813-8c3b-743c8f949f5a"
                            },
                            {
                                "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                                "texture_url": "",
                                "color": [
                                    248,
                                    249,
                                    251
                                ],
                                "colorMode": "color",
                                "size": [
                                    1,
                                    1
                                ],
                                "seam": False,
                                "material_id": "14149",
                                "area": 0.013724000000000292,
                                "wall": [
                                    [
                                        -3.494998,
                                        -2.4475
                                    ],
                                    [
                                        -3.508722,
                                        -2.4475
                                    ]
                                ],
                                "offset": True,
                                "alias": "c53afd8f-6b30-4d1b-8454-0138ff5d7147"
                            }
                        ],
                        "win_pocket": [],
                        "door_pocket": [],
                        "customized_ceiling": [
                            {
                                "type": "CustomizedCeiling",
                                "size": [
                                    2.6310100000000003,
                                    0.00032999999999994145,
                                    4.39189
                                ],
                                "valid": False,
                                "bounds": [
                                    [
                                        -6.246,
                                        -3.61499
                                    ],
                                    [
                                        -5.0695,
                                        -0.67762
                                    ],
                                    [
                                        2.79967,
                                        2.8
                                    ]
                                ],
                                "coords": [
                                    [
                                        [
                                            -6.246,
                                            -4.3075
                                        ],
                                        [
                                            -6.246,
                                            -0.67762
                                        ],
                                        [
                                            -3.61499,
                                            -0.67762
                                        ],
                                        [
                                            -3.615,
                                            -1.17204
                                        ],
                                        [
                                            -3.62872,
                                            -2.50681
                                        ],
                                        [
                                            -3.615,
                                            -2.50688
                                        ],
                                        [
                                            -3.615,
                                            -5.0695
                                        ],
                                        [
                                            -5.342,
                                            -5.0695
                                        ],
                                        [
                                            -5.34199,
                                            -4.3075
                                        ],
                                        [
                                            -6.246,
                                            -4.3075
                                        ]
                                    ]
                                ],
                                "obj": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4_19564.json",
                                "room_area": 10.8376
                            }
                        ],
                        "ceiling": [
                            {
                                "id": "2ad9ec18-d6cb-4890-b646-5f18b3a33998",
                                "type": "build element/ceiling molding",
                                "style": "\u7f8e\u5f0f\u4e61\u6751",
                                "size": [
                                    434.0,
                                    31.543,
                                    339.0
                                ],
                                "scale": [
                                    0.626489,
                                    1,
                                    0.508372
                                ],
                                "position": [
                                    -4.934311,
                                    2.48457,
                                    -2.487098
                                ],
                                "rotation": [
                                    0,
                                    -0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "19614",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "2ad9ec18-d6cb-4890-b646-5f18b3a33998",
                                "type": "build element/ceiling molding",
                                "style": "\u7f8e\u5f0f\u4e61\u6751",
                                "size": [
                                    434.0,
                                    31.543,
                                    339.0
                                ],
                                "scale": [
                                    0.626489,
                                    1,
                                    0.508372
                                ],
                                "position": [
                                    -4.934311,
                                    2.48457,
                                    -2.487098
                                ],
                                "rotation": [
                                    0,
                                    -0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "19614",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "2ad9ec18-d6cb-4890-b646-5f18b3a33998",
                                "type": "build element/ceiling molding",
                                "style": "\u7f8e\u5f0f\u4e61\u6751",
                                "size": [
                                    434.0,
                                    31.543,
                                    339.0
                                ],
                                "scale": [
                                    0.626489,
                                    1,
                                    0.508372
                                ],
                                "position": [
                                    -4.934311,
                                    2.48457,
                                    -2.487098
                                ],
                                "rotation": [
                                    0,
                                    -0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "19614",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "2ad9ec18-d6cb-4890-b646-5f18b3a33998",
                                "type": "build element/ceiling molding",
                                "style": "\u7f8e\u5f0f\u4e61\u6751",
                                "size": [
                                    434.0,
                                    31.543,
                                    339.0
                                ],
                                "scale": [
                                    0.626489,
                                    1,
                                    0.508372
                                ],
                                "position": [
                                    -4.934311,
                                    2.48457,
                                    -2.487098
                                ],
                                "rotation": [
                                    0,
                                    -0.7071067811865475,
                                    0,
                                    0.7071067811865476
                                ],
                                "entityId": "19614",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            }
                        ],
                        "win": [
                            {
                                "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                "type": "window/floor-based window",
                                "style": "Contemporary",
                                "size": [
                                    272.919,
                                    216.796,
                                    12.0
                                ],
                                "scale": [
                                    0.594247,
                                    1,
                                    1
                                ],
                                "position": [
                                    -4.515186,
                                    0.2,
                                    -5.1095
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "12508",
                                "categories": [
                                    "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                ],
                                "pocket": {
                                    "jid": "",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                    "color": [
                                        255,
                                        255,
                                        255
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        2.729192,
                                        0.001
                                    ],
                                    "seam": False,
                                    "material_id": "12588",
                                    "area": -1
                                },
                                "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                "unit_to_room": "",
                                "unit_to_type": "",
                                "role": "window",
                                "count": 1,
                                "relate": "",
                                "relate_group": "",
                                "relate_position": []
                            }
                        ],
                        "door": {
                            "LivingDiningRoom": [
                                {
                                    "id": "3ad620eb-bb89-4e86-92b1-df46fd0a0029",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.704455,
                                        1.051246,
                                        1
                                    ],
                                    "position": [
                                        -3.502943,
                                        0,
                                        -1.945372
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7034626523170564,
                                        0,
                                        0.7107322258031166
                                    ],
                                    "entityId": "18739",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "unit_to_room": "LivingDiningRoom-5376",
                                    "unit_to_type": "LivingDiningRoom",
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ]
                        },
                        "background": []
                    },
                    "decorate": {},
                    "painting": {},
                    "group": [
                        {
                            "type": "Bed",
                            "code": 10000,
                            "size": [
                                1.7371299999999998,
                                1.1307800000000001,
                                2.2709
                            ],
                            "offset": [
                                -0.0,
                                0,
                                -0.0
                            ],
                            "position": [
                                -5.110552,
                                0,
                                -3.23569
                            ],
                            "rotation": [
                                0,
                                0.7071067811865475,
                                0,
                                0.7071067811865476
                            ],
                            "size_min": [
                                1.7371299999999998,
                                1.1307800000000001,
                                2.2709
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.0,
                                0.0
                            ],
                            "obj_main": "bbd7d862-6db2-4c54-94f7-9f7192c5b2e7",
                            "obj_type": "bed/single bed",
                            "obj_list": [
                                {
                                    "id": "bbd7d862-6db2-4c54-94f7-9f7192c5b2e7",
                                    "type": "bed/single bed",
                                    "style": "Swedish",
                                    "size": [
                                        173.713,
                                        113.078,
                                        227.09
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -5.110552,
                                        0,
                                        -3.23569
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "23868",
                                    "categories": [
                                        "8f58f84c-1424-4aaf-aef5-62ae1da722ab"
                                    ],
                                    "category": "8f58f84c-1424-4aaf-aef5-62ae1da722ab",
                                    "relate": "wall",
                                    "group": "Bed",
                                    "role": "bed",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -5.110552,
                                        0,
                                        -3.23569
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0.059997999999999996,
                                0,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0.7999999999999998,
                                0,
                                0.263
                            ],
                            "neighbor_more": [
                                0,
                                0.7999999999999998,
                                0.2,
                                0.263
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "switch": 0,
                            "region_direct": 0,
                            "region_center": [],
                            "back_p1": [
                                -6.306,
                                -4.367
                            ],
                            "back_p2": [
                                -6.306,
                                -2.104
                            ],
                            "back_depth": 0.0,
                            "back_front": 2.2709,
                            "back_angle": 1.5707963267948966,
                            "expand": [
                                -6.306,
                                -4.367,
                                -3.9751,
                                -1.56770796460177
                            ]
                        },
                        {
                            "type": "Cabinet",
                            "code": 10,
                            "size": [
                                1.716269989013672,
                                2.0223100280761717,
                                0.56
                            ],
                            "offset": [
                                -0.0,
                                0,
                                -0.0
                            ],
                            "position": [
                                -5.387867,
                                0,
                                -0.957616
                            ],
                            "rotation": [
                                0,
                                1.0,
                                0,
                                6.123233995736766e-17
                            ],
                            "size_min": [
                                1.716269989013672,
                                2.0223100280761717,
                                0.56
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.0,
                                0.0
                            ],
                            "obj_main": "b8b40baa-1c68-45d8-ad98-94d001ecb15e",
                            "obj_type": "storage unit/floor-based storage unit",
                            "obj_list": [
                                {
                                    "id": "b8b40baa-1c68-45d8-ad98-94d001ecb15e",
                                    "type": "storage unit/floor-based storage unit",
                                    "style": "Contemporary",
                                    "size": [
                                        171.6269989013672,
                                        202.2310028076172,
                                        56.0
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -5.387867,
                                        0,
                                        -0.957616
                                    ],
                                    "rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "entityId": "23869",
                                    "categories": [
                                        "41115241-95b4-4805-8c82-b1651990407b"
                                    ],
                                    "category": "41115241-95b4-4805-8c82-b1651990407b",
                                    "relate": "wall",
                                    "group": "Cabinet",
                                    "role": "cabinet",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -5.387867,
                                        0,
                                        -0.957616
                                    ],
                                    "origin_rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "normal_position": [
                                        -0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0.059615999999999836,
                                0,
                                0,
                                0.059998005493164364
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "region_direct": 1,
                            "neighbor_base": [
                                0,
                                0.975,
                                0,
                                0
                            ],
                            "neighbor_more": [
                                0,
                                0.975,
                                0,
                                0
                            ],
                            "switch": 0,
                            "region_center": [],
                            "back_p1": [
                                -6.306,
                                -0.618
                            ],
                            "back_p2": [
                                -4.53,
                                -0.618
                            ],
                            "back_depth": 0.0,
                            "back_front": 0.56,
                            "back_angle": 3.141592653589793
                        },
                        {
                            "type": "Wall",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Ceiling",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Floor",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Door",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Window",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                    "type": "window/floor-based window",
                                    "style": "Contemporary",
                                    "size": [
                                        272.919,
                                        216.796,
                                        12.0
                                    ],
                                    "scale": [
                                        0.594247,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -4.515186,
                                        0.2,
                                        -5.1095
                                    ],
                                    "rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "entityId": "12508",
                                    "categories": [
                                        "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            2.729192,
                                            0.001
                                        ],
                                        "seam": False,
                                        "material_id": "12588",
                                        "area": -1
                                    },
                                    "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                    "unit_to_room": "",
                                    "unit_to_type": "",
                                    "role": "window",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Background",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Customize",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        }
                    ],
                    "group_area": 4.9059597108476565,
                    "source_house": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4",
                    "source_room": "KidsRoom-5403",
                    "source_room_area": 11.498968100451997,
                    "line_unit": [
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.263,
                            "depth": 0.964,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    2.751004000000001
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -6.306,
                                -4.367
                            ],
                            "p2": [
                                -6.306,
                                -4.104
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.964,
                            "depth_post": 2.3309,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 2,
                            "width": 1.737,
                            "depth": 2.3309,
                            "depth_all": [
                                [
                                    0,
                                    0.984,
                                    2.751004000000001
                                ],
                                [
                                    0.984,
                                    1,
                                    2.3180618469833174
                                ]
                            ],
                            "height": 1.131,
                            "angle": 0,
                            "p1": [
                                -6.306,
                                -4.104
                            ],
                            "p2": [
                                -6.306,
                                -2.367
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 2.331,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 2,
                            "width": 0.7999999999999998,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    2.3180618469833174
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -6.306,
                                -2.367
                            ],
                            "p2": [
                                -6.306,
                                -1.56770796460177
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 2.3309,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": 2,
                            "width": 0.33,
                            "depth": 0.2,
                            "depth_all": [],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -6.306,
                                -1.56770796460177
                            ],
                            "p2": [
                                -6.306,
                                -1.238
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.2,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 5,
                            "width": 0.6200000000000001,
                            "depth": 0.06,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    2.751004000000001
                                ]
                            ],
                            "height": 2.022,
                            "angle": 0,
                            "p1": [
                                -6.306,
                                -1.238
                            ],
                            "p2": [
                                -6.306,
                                -0.618
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 1.776,
                            "unit_index": 1,
                            "unit_depth": 1.776,
                            "unit_margin": 0.06,
                            "unit_edge": 3,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                -6.306,
                                -0.678
                            ],
                            "width_original": 0.56
                        },
                        {
                            "type": 1,
                            "score": 5,
                            "width": 1.776,
                            "depth": 0.6200000000000001,
                            "depth_all": [
                                [
                                    0,
                                    0.527,
                                    3.7498840000000007
                                ],
                                [
                                    0.527,
                                    1,
                                    4.431883999999998
                                ]
                            ],
                            "height": 2.022,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -6.306,
                                -0.618
                            ],
                            "p2": [
                                -4.53,
                                -0.618
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.6200000000000001,
                            "depth_post": 0.85,
                            "unit_index": 1,
                            "unit_depth": 0.62,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p1_original": [
                                -6.246,
                                -0.618
                            ],
                            "width_original": 1.716
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.975,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    0.128,
                                    4.431883999999998
                                ],
                                [
                                    0.128,
                                    1.0,
                                    0.8777677573840064
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -4.53,
                                -0.618
                            ],
                            "p2": [
                                -3.555,
                                -0.618
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.6200000000000001,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.828,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    2.751004000000001
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                -3.555,
                                -0.618
                            ],
                            "p2": [
                                -3.555,
                                -1.445
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.6,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 2,
                            "width": 1.0,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 3.141592653589793,
                            "p1": [
                                -3.555,
                                -1.445
                            ],
                            "p2": [
                                -3.555,
                                -2.445
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "LivingDiningRoom-5376",
                            "unit_to_type": "LivingDiningRoom"
                        },
                        {
                            "type": 6,
                            "score": 2,
                            "width": 2.374,
                            "depth": 0.4201040000000007,
                            "depth_all": [
                                [
                                    0.0,
                                    0.8094995787700083,
                                    2.751004000000001
                                ],
                                [
                                    0.8094995787700083,
                                    1,
                                    1.7869999999999981
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                -3.555,
                                -2.445
                            ],
                            "p2": [
                                -3.555,
                                -4.819000000000001
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                -3.555,
                                -4.819000000000001
                            ],
                            "p2": [
                                -3.555,
                                -5.049
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0,
                            "depth_post": 0,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 4,
                            "score": 8,
                            "width": 1.774,
                            "depth": 0.45200000000000007,
                            "depth_all": [
                                [
                                    0.0,
                                    0.4792378804960541,
                                    2.654139757384004
                                ],
                                [
                                    0.4792378804960541,
                                    1.0,
                                    4.431883999999998
                                ]
                            ],
                            "height": 0.6,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -3.569,
                                -5.049
                            ],
                            "p2": [
                                -5.342,
                                -5.049
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.23,
                            "depth_post": 0.23,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0.0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p1_original": [
                                -3.704,
                                -5.049
                            ],
                            "width_original": 1.638
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0.6,
                            "angle": 0,
                            "p1": [
                                -5.342,
                                -5.05
                            ],
                            "p2": [
                                -5.342,
                                -4.82
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.45200000000000007,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    1.7869999999999981
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -5.342,
                                -4.82
                            ],
                            "p2": [
                                -5.342,
                                -4.368
                            ],
                            "score_pre": 1,
                            "score_post": 2,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 6,
                            "width": 0.964,
                            "depth": 0.26,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    3.7498840000000007
                                ]
                            ],
                            "height": 1.131,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -5.342,
                                -4.368
                            ],
                            "p2": [
                                -6.306,
                                -4.368
                            ],
                            "score_pre": 2,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.263,
                            "unit_index": 0,
                            "unit_depth": 1.997,
                            "unit_margin": 0.26,
                            "unit_edge": 3,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                -6.246,
                                -4.368
                            ],
                            "width_original": 0.904
                        }
                    ]
                }
            ],
            "layout_mesh": [
                {
                    "id": "2ad9ec18-d6cb-4890-b646-5f18b3a33998",
                    "type": "build element/ceiling molding",
                    "style": "\u7f8e\u5f0f\u4e61\u6751",
                    "size": [
                        434.0,
                        31.543,
                        339.0
                    ],
                    "scale": [
                        0.626489,
                        1,
                        0.508372
                    ],
                    "position": [
                        -4.934311,
                        2.48457,
                        -2.487098
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "19614",
                    "categories": [
                        "91e376e7-ebdb-43cc-a230-827a367cf18e"
                    ],
                    "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                    "role": "ceiling"
                }
            ]
        },
        "Balcony-5439": {
            "room_type": "Balcony",
            "room_style": "Swedish",
            "room_area": 3.742371909090907,
            "room_height": 2.8,
            "layout_scheme": [
                {
                    "code": 10100,
                    "score": 80,
                    "type": "Balcony",
                    "style": "Swedish",
                    "area": 3.742371909090907,
                    "material": {
                        "id": "Balcony-5439",
                        "type": "Balcony",
                        "floor": [
                            {
                                "jid": "d5874b67-6e51-42f1-8fa2-c305cf1fd155",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/d5874b67-6e51-42f1-8fa2-c305cf1fd155/wallfloor_mini.jpg",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.8,
                                    0.53
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "20174",
                                "area": 3.556641
                            }
                        ],
                        "wall": [
                            {
                                "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                                "texture_url": "",
                                "color": [
                                    248,
                                    249,
                                    251
                                ],
                                "colorMode": "color",
                                "size": [
                                    1,
                                    1
                                ],
                                "seam": False,
                                "material_id": "892",
                                "area": 9.104000000000003,
                                "wall": [
                                    [
                                        -1.871998,
                                        -5.4735000000000005
                                    ],
                                    [
                                        1.321002,
                                        -5.4735000000000005
                                    ]
                                ],
                                "offset": True,
                                "alias": "c53afd8f-6b30-4d1b-8454-0138ff5d7147"
                            }
                        ],
                        "win_pocket": [],
                        "door_pocket": [],
                        "win": [
                            {
                                "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                "type": "window/floor-based window",
                                "style": "Contemporary",
                                "size": [
                                    272.919,
                                    216.796,
                                    12.0
                                ],
                                "scale": [
                                    0.942983,
                                    1,
                                    1
                                ],
                                "position": [
                                    -0.182739,
                                    0.2,
                                    -5.5335
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "12419",
                                "categories": [
                                    "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                ],
                                "pocket": {
                                    "jid": "",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                    "color": [
                                        255,
                                        255,
                                        255
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        2.729192,
                                        0.001
                                    ],
                                    "seam": False,
                                    "material_id": "12499",
                                    "area": -1
                                },
                                "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                "unit_to_room": "",
                                "unit_to_type": "",
                                "role": "window",
                                "count": 1,
                                "relate": "",
                                "relate_group": "",
                                "relate_position": []
                            }
                        ],
                        "door": {
                            "LivingDiningRoom": [
                                {
                                    "id": "1dbb3f82-5c6f-41ef-900e-9a436b252cde",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        203.555,
                                        172.29,
                                        18.1747
                                    ],
                                    "scale": [
                                        0.761797,
                                        1.218875,
                                        1
                                    ],
                                    "position": [
                                        -0.161892,
                                        0,
                                        -4.1965
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17960",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "LivingDiningRoom-5376",
                                    "unit_to_type": "LivingDiningRoom",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ]
                        },
                        "background": []
                    },
                    "decorate": {},
                    "painting": {},
                    "group": [
                        {
                            "type": "Appliance",
                            "code": 10,
                            "size": [
                                0.6,
                                0.8600709999999999,
                                0.587731
                            ],
                            "offset": [
                                -0.0,
                                0,
                                -0.0
                            ],
                            "position": [
                                -1.538133,
                                0,
                                -4.745319
                            ],
                            "rotation": [
                                0,
                                0.7071067811865475,
                                0,
                                0.7071067811865476
                            ],
                            "size_min": [
                                0.6,
                                0.8600709999999999,
                                0.587731
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.0,
                                0.0
                            ],
                            "obj_main": "b9878eac-818d-4950-b56c-7678bb4ec355",
                            "obj_type": "appliance/washer",
                            "obj_list": [
                                {
                                    "id": "b9878eac-818d-4950-b56c-7678bb4ec355",
                                    "type": "appliance/washer",
                                    "style": "Swedish",
                                    "size": [
                                        60.0,
                                        86.0071,
                                        58.7731
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -1.538133,
                                        0,
                                        -4.745319
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17519",
                                    "categories": [
                                        "f8e77f0a-068d-457f-9783-121ebb3ec821"
                                    ],
                                    "category": "f8e77f0a-068d-457f-9783-121ebb3ec821",
                                    "role": "appliance",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -1.538133,
                                        0,
                                        -4.745319
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ],
                                    "group": "Appliance"
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "region_direct": 0,
                            "regulation": [
                                0,
                                0,
                                0.020267499999999827,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0.387,
                                0,
                                0.428
                            ],
                            "neighbor_more": [
                                0,
                                1.037,
                                0,
                                0.428
                            ],
                            "switch": 0,
                            "region_center": [],
                            "back_p1": [
                                -1.812,
                                -5.432
                            ],
                            "back_p2": [
                                -1.812,
                                -4.058
                            ],
                            "back_depth": 0.0,
                            "back_front": 0.587731,
                            "back_angle": 1.5707963267948966
                        },
                        {
                            "type": "Wall",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Ceiling",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Floor",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "link_0_10defb41-8d60-4df3-a772-e9763d6dbf60",
                                    "type": "plants/plants - on top of others",
                                    "style": "Swedish",
                                    "size": [
                                        137.6481,
                                        95.0468,
                                        53.6898
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        0.08141900000000002,
                                        0,
                                        -5.225051
                                    ],
                                    "rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17520",
                                    "categories": [
                                        "7126c163-836c-4fcd-be09-e612a06a2649"
                                    ],
                                    "category": "7126c163-836c-4fcd-be09-e612a06a2649",
                                    "role": "plants",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": [],
                                    "relate_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                },
                                {
                                    "id": "10defb41-8d60-4df3-a772-e9763d6dbf60",
                                    "type": "plants/plants - on top of others",
                                    "style": "Swedish",
                                    "size": [
                                        49.5603,
                                        95.0468,
                                        53.6898
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -0.35902,
                                        0,
                                        -5.225051
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17520",
                                    "categories": [
                                        "7126c163-836c-4fcd-be09-e612a06a2649"
                                    ],
                                    "category": "7126c163-836c-4fcd-be09-e612a06a2649",
                                    "role": "plants",
                                    "count": 1,
                                    "relate": "link_0_10defb41-8d60-4df3-a772-e9763d6dbf60",
                                    "relate_group": "",
                                    "relate_position": [
                                        0.08141900000000002,
                                        0,
                                        -5.225051
                                    ],
                                    "relate_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                },
                                {
                                    "id": "10defb41-8d60-4df3-a772-e9763d6dbf60",
                                    "type": "plants/plants - on top of others",
                                    "style": "Swedish",
                                    "size": [
                                        49.5603,
                                        95.0468,
                                        53.6898
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        0.521858,
                                        0,
                                        -5.225051
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17521",
                                    "categories": [
                                        "7126c163-836c-4fcd-be09-e612a06a2649"
                                    ],
                                    "category": "7126c163-836c-4fcd-be09-e612a06a2649",
                                    "role": "plants",
                                    "count": 1,
                                    "relate": "link_0_10defb41-8d60-4df3-a772-e9763d6dbf60",
                                    "relate_group": "",
                                    "relate_position": [
                                        0.08141900000000002,
                                        0,
                                        -5.225051
                                    ],
                                    "relate_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Door",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Window",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                    "type": "window/floor-based window",
                                    "style": "Contemporary",
                                    "size": [
                                        272.919,
                                        216.796,
                                        12.0
                                    ],
                                    "scale": [
                                        0.942983,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -0.182739,
                                        0.2,
                                        -5.5335
                                    ],
                                    "rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "entityId": "12419",
                                    "categories": [
                                        "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            2.729192,
                                            0.001
                                        ],
                                        "seam": False,
                                        "material_id": "12499",
                                        "area": -1
                                    },
                                    "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                    "unit_to_room": "",
                                    "unit_to_type": "",
                                    "role": "window",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Background",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Customize",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        }
                    ],
                    "group_area": 0.35263859999999997,
                    "source_house": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4",
                    "source_room": "Balcony-5439",
                    "source_room_area": 3.742371909090907,
                    "line_unit": [
                        {
                            "type": 3,
                            "score": 5,
                            "width": 0.428,
                            "depth": 0.587731,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    3.0729999999999995
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -1.812,
                                -5.474
                            ],
                            "p2": [
                                -1.812,
                                -5.045
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.6,
                            "depth_post": 0.587731,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 2,
                            "width": 0.6,
                            "depth": 0.587731,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    3.0729999999999995
                                ]
                            ],
                            "height": 0.86,
                            "angle": 0,
                            "p1": [
                                -1.812,
                                -5.045
                            ],
                            "p2": [
                                -1.812,
                                -4.445
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 3.073,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.588,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.187,
                            "depth": 0.587731,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    3.0729999999999995
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -1.812,
                                -4.445
                            ],
                            "p2": [
                                -1.812,
                                -4.258
                            ],
                            "score_pre": 1,
                            "score_post": 2,
                            "depth_pre": 0.587731,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.20099999999999998,
                            "depth": 0.85,
                            "depth_all": [],
                            "height": 0,
                            "angle": -2.7901478595862867,
                            "p1": [
                                -1.812,
                                -4.258
                            ],
                            "p2": [
                                -1.881252100840336,
                                -4.446331932773109
                            ],
                            "score_pre": 2,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.037,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0,
                            "angle": -2.7901478595862867,
                            "p1": [
                                -1.881252100840336,
                                -4.446331932773109
                            ],
                            "p2": [
                                -1.894,
                                -4.481
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0,
                            "depth_post": 0,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 3,
                            "width": 0.037,
                            "depth": 0.06,
                            "depth_all": [],
                            "height": 0.86,
                            "angle": 0.2606023917473526,
                            "p1": [
                                -1.894,
                                -4.481
                            ],
                            "p2": [
                                -1.884,
                                -4.445
                            ],
                            "score_pre": 2,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.648,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.195,
                            "depth": 0.2,
                            "depth_all": [],
                            "height": 0,
                            "angle": 0.2606023917473526,
                            "p1": [
                                -1.884,
                                -4.445
                            ],
                            "p2": [
                                -1.834,
                                -4.257
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.2,
                            "depth_post": 0.59,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 5,
                            "width": 0.59,
                            "depth": 0.19,
                            "depth_all": [
                                [
                                    0.037,
                                    1,
                                    1.2169999999999996
                                ]
                            ],
                            "height": 0.86,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -1.834,
                                -4.257
                            ],
                            "p2": [
                                -1.244,
                                -4.257
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.2,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.79,
                            "unit_margin": 0.19,
                            "unit_edge": 1,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 2,
                            "width": 0.257,
                            "depth": 0.2,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    1.2169999999999996
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -1.244,
                                -4.257
                            ],
                            "p2": [
                                -0.987,
                                -4.257
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.2,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 2,
                            "width": 1.651,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -0.987,
                                -4.257
                            ],
                            "p2": [
                                0.663,
                                -4.257
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "LivingDiningRoom-5376",
                            "unit_to_type": "LivingDiningRoom"
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.598,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    1.2169999999999996
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                0.663,
                                -4.257
                            ],
                            "p2": [
                                1.261,
                                -4.257
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.9870000000000001,
                            "depth": 0.598,
                            "depth_all": [
                                [
                                    0.0012330293819655524,
                                    1,
                                    3.0729999999999995
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                1.261,
                                -4.257
                            ],
                            "p2": [
                                1.261,
                                -5.244
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.598,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                1.261,
                                -5.244
                            ],
                            "p2": [
                                1.261,
                                -5.474
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0,
                            "depth_post": 0,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 4,
                            "score": 8,
                            "width": 3.073,
                            "depth": 0.428,
                            "depth_all": [
                                [
                                    0.0,
                                    1.0,
                                    1.2169999999999996
                                ]
                            ],
                            "height": 0.6,
                            "angle": -1.5707963267948966,
                            "p1": [
                                1.261,
                                -5.474
                            ],
                            "p2": [
                                -1.812,
                                -5.474
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.23,
                            "depth_post": 0.428,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0.0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                -1.47,
                                -5.474
                            ],
                            "width_original": 2.574,
                            "p1_original": [
                                1.104,
                                -5.474
                            ]
                        }
                    ]
                }
            ],
            "layout_mesh": []
        },
        "Bathroom-5454": {
            "room_type": "Bathroom",
            "room_style": "Swedish",
            "room_area": 2.745773999999998,
            "room_height": 2.8,
            "layout_scheme": [
                {
                    "code": 20200,
                    "score": 80,
                    "type": "Bathroom",
                    "style": "Swedish",
                    "area": 2.745773999999998,
                    "material": {
                        "id": "Bathroom-5454",
                        "type": "Bathroom",
                        "floor": [
                            {
                                "jid": "fd93d5e2-aff7-4d34-bc5c-cc9c053220f3",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/fd93d5e2-aff7-4d34-bc5c-cc9c053220f3/wallfloor_mini.jpg",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.9,
                                    0.9
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "20143",
                                "area": 2.402166
                            }
                        ],
                        "wall": [
                            {
                                "jid": "44d6fc60-53d8-444e-a5e2-ab1fa58876a9",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/44d6fc60-53d8-444e-a5e2-ab1fa58876a9/wallfloor_mini.jpg",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.6,
                                    0.6
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "20787",
                                "area": 7.1499999999999995,
                                "wall": [
                                    [
                                        -3.4349979999999998,
                                        -4.4815
                                    ],
                                    [
                                        -3.4349979999999998,
                                        -2.5075
                                    ]
                                ],
                                "offset": True,
                                "alias": "44d6fc60-53d8-444e-a5e2-ab1fa58876a9"
                            }
                        ],
                        "win_pocket": [],
                        "door_pocket": [],
                        "customized_ceiling": [],
                        "win": [
                            {
                                "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                "type": "window/floor-based window",
                                "style": "Contemporary",
                                "size": [
                                    272.919,
                                    216.796,
                                    12.0
                                ],
                                "scale": [
                                    0.309678,
                                    1,
                                    1
                                ],
                                "position": [
                                    -2.672564,
                                    0.2,
                                    -4.4815
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "12239",
                                "categories": [
                                    "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                ],
                                "pocket": {
                                    "jid": "",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                    "color": [
                                        255,
                                        255,
                                        255
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        2.729192,
                                        0.001
                                    ],
                                    "seam": False,
                                    "material_id": "12319",
                                    "area": -1
                                },
                                "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                "unit_to_room": "",
                                "unit_to_type": "",
                                "role": "window",
                                "count": 1,
                                "relate": "",
                                "relate_group": "",
                                "relate_position": []
                            }
                        ],
                        "door": {
                            "LivingDiningRoom": [
                                {
                                    "id": "32cd827e-3d58-428d-84ba-39c7ae518118",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.41528,
                                        1.016769,
                                        1
                                    ],
                                    "position": [
                                        -3.087704,
                                        0,
                                        -2.5075
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "19009",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/32cd827e-3d58-428d-84ba-39c7ae518118/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            1.274739,
                                            2.053975
                                        ],
                                        "seam": False,
                                        "material_id": "19076",
                                        "area": -1
                                    },
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "unit_to_room": "LivingDiningRoom-5376",
                                    "unit_to_type": "LivingDiningRoom",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ]
                        },
                        "background": []
                    },
                    "decorate": {},
                    "painting": {},
                    "group": [
                        {
                            "type": "Toilet",
                            "code": 10,
                            "size": [
                                0.334264,
                                0.773639,
                                0.516423
                            ],
                            "offset": [
                                -0.0,
                                0,
                                -0.0
                            ],
                            "position": [
                                -3.116786,
                                0,
                                -3.495578
                            ],
                            "rotation": [
                                0,
                                0.7071067811865475,
                                0,
                                0.7071067811865476
                            ],
                            "size_min": [
                                0.334264,
                                0.773639,
                                0.516423
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.0,
                                0.0
                            ],
                            "obj_main": "73f1868e-5821-4d46-836a-d956319a71d7",
                            "obj_type": "toilet/floor-based toilet",
                            "obj_list": [
                                {
                                    "id": "73f1868e-5821-4d46-836a-d956319a71d7",
                                    "type": "toilet/floor-based toilet",
                                    "style": "Swedish",
                                    "size": [
                                        33.4264,
                                        77.3639,
                                        51.6423
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -3.116786,
                                        0,
                                        -3.495578
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17516",
                                    "categories": [
                                        "087cf1ce-df43-478f-842e-fe3199822ac6"
                                    ],
                                    "group": "Toilet",
                                    "role": "toilet",
                                    "category": "087cf1ce-df43-478f-842e-fe3199822ac6",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -3.116786,
                                        0,
                                        -3.495578
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0.06000250000000029,
                                0,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0.761,
                                0,
                                0.759
                            ],
                            "neighbor_more": [
                                0,
                                0.761,
                                0,
                                0.759
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "switch": 0,
                            "region_direct": 0,
                            "region_center": [],
                            "back_p1": [
                                -3.435,
                                -4.422
                            ],
                            "back_p2": [
                                -3.435,
                                -2.569
                            ],
                            "back_depth": 0.0,
                            "back_front": 0.516423,
                            "back_angle": 1.5707963267948966,
                            "expand": [
                                -3.435,
                                -4.421,
                                -2.6585745,
                                -3.328
                            ]
                        },
                        {
                            "type": "Bath",
                            "code": 100,
                            "size": [
                                0.7756399999999999,
                                0.8581019999999999,
                                0.7756399999999999
                            ],
                            "offset": [
                                -0.0,
                                0,
                                -0.0
                            ],
                            "position": [
                                -2.423818,
                                0,
                                -3.97368
                            ],
                            "rotation": [
                                0,
                                -0.7071067811865475,
                                0,
                                0.7071067811865476
                            ],
                            "size_min": [
                                0.7756399999999999,
                                0.8581019999999999,
                                0.7756399999999999
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.0,
                                0.0
                            ],
                            "obj_main": "89b997b0-062b-4afd-b627-928d82017855",
                            "obj_type": "bath/freestanding bath",
                            "obj_list": [
                                {
                                    "id": "89b997b0-062b-4afd-b627-928d82017855",
                                    "type": "bath/freestanding bath",
                                    "style": "Swedish",
                                    "size": [
                                        77.564,
                                        85.8102,
                                        77.564
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -2.423818,
                                        0,
                                        -3.97368
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17514",
                                    "categories": [
                                        "49d4a12a-dade-4ea1-bb97-68139ccac840"
                                    ],
                                    "group": "Bath",
                                    "role": "bath",
                                    "category": "49d4a12a-dade-4ea1-bb97-68139ccac840",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -2.423818,
                                        0,
                                        -3.97368
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0.0819979999999999,
                                0,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0,
                                0,
                                1.018
                            ],
                            "neighbor_more": [
                                0,
                                0,
                                0,
                                1.018
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "switch": 0,
                            "region_direct": -1,
                            "region_center": [],
                            "back_p1": [
                                -1.954,
                                -3.586
                            ],
                            "back_p2": [
                                -1.954,
                                -4.361
                            ],
                            "back_depth": 0.0,
                            "back_front": 0.7756399999999999,
                            "back_angle": -1.5707963267948966,
                            "expand": [
                                -2.811638,
                                -4.3614999999999995,
                                -1.954,
                                -2.568
                            ]
                        },
                        {
                            "type": "Wall",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Ceiling",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Floor",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Door",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Window",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                    "type": "window/floor-based window",
                                    "style": "Contemporary",
                                    "size": [
                                        272.919,
                                        216.796,
                                        12.0
                                    ],
                                    "scale": [
                                        0.309678,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -2.672564,
                                        0.2,
                                        -4.4815
                                    ],
                                    "rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "entityId": "12239",
                                    "categories": [
                                        "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            2.729192,
                                            0.001
                                        ],
                                        "seam": False,
                                        "material_id": "12319",
                                        "area": -1
                                    },
                                    "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                    "unit_to_room": "",
                                    "unit_to_type": "",
                                    "role": "window",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Background",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Customize",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        }
                    ],
                    "group_area": 0.7742390272719999,
                    "source_house": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4",
                    "source_room": "Bathroom-5454",
                    "source_room_area": 2.745773999999998,
                    "line_unit": [
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.759,
                            "depth": 0.34,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    1.4809999999999999
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -3.435,
                                -4.421
                            ],
                            "p2": [
                                -3.435,
                                -3.663
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.34,
                            "depth_post": 0.5764230000000001,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 2,
                            "width": 0.334,
                            "depth": 0.5764230000000001,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    1.4809999999999999
                                ]
                            ],
                            "height": 0.774,
                            "angle": 0,
                            "p1": [
                                -3.435,
                                -3.663
                            ],
                            "p2": [
                                -3.435,
                                -3.328
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.576,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": 5,
                            "width": 0.761,
                            "depth": 0.5764230000000001,
                            "depth_all": [
                                [
                                    0,
                                    0.303,
                                    1.4809999999999999
                                ],
                                [
                                    0.303,
                                    1.0,
                                    0.08202351800000063
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -3.435,
                                -3.328
                            ],
                            "p2": [
                                -3.435,
                                -2.568
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.5764230000000001,
                            "depth_post": 0.663,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 5,
                            "width": 0.663,
                            "depth": 0.761,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -3.435,
                                -2.568
                            ],
                            "p2": [
                                -2.772,
                                -2.568
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.761,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "LivingDiningRoom-5376",
                            "unit_to_type": "LivingDiningRoom"
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.818,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    1.8539999999999996
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -2.772,
                                -2.568
                            ],
                            "p2": [
                                -1.954,
                                -2.568
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 1.018,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    -0.0,
                                    0.521,
                                    0.8684355179999992
                                ],
                                [
                                    0.521,
                                    1,
                                    1.4809999999999999
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                -1.954,
                                -2.568
                            ],
                            "p2": [
                                -1.954,
                                -3.586
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.6,
                            "depth_post": 0.8556399999999996,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 2,
                            "width": 0.776,
                            "depth": 0.8556399999999996,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    1.4809999999999999
                                ]
                            ],
                            "height": 0.858,
                            "angle": 3.141592653589793,
                            "p1": [
                                -1.954,
                                -3.586
                            ],
                            "p2": [
                                -1.954,
                                -4.361
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.858,
                            "unit_index": 1,
                            "unit_depth": 0.856,
                            "unit_margin": 0.08,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.06,
                            "depth": 0.858,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    1.4809999999999999
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                -1.954,
                                -4.361
                            ],
                            "p2": [
                                -1.954,
                                -4.421
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0,
                            "depth_post": 0,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 5,
                            "width": 0.858,
                            "depth": 0.06,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    1.8539999999999996
                                ]
                            ],
                            "height": 2.8,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -1.954,
                                -4.421
                            ],
                            "p2": [
                                -2.812,
                                -4.421
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.2,
                            "depth_post": 0.85,
                            "unit_index": 1,
                            "unit_depth": 0.836,
                            "unit_margin": 0.06,
                            "unit_edge": 1,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p1_original": [
                                -2.036,
                                -4.421
                            ],
                            "width_original": 0.776
                        },
                        {
                            "type": 4,
                            "score": 2,
                            "width": 0.284,
                            "depth": 0.2,
                            "depth_all": [
                                [
                                    0,
                                    0.038,
                                    1.8539999999999996
                                ],
                                [
                                    0.038,
                                    1,
                                    1.429
                                ]
                            ],
                            "height": 0.6,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -2.812,
                                -4.421
                            ],
                            "p2": [
                                -3.095,
                                -4.421
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.2,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.34,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    1.429
                                ]
                            ],
                            "height": 0,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -3.095,
                                -4.421
                            ],
                            "p2": [
                                -3.435,
                                -4.421
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        }
                    ]
                }
            ],
            "layout_mesh": []
        },
        "Kitchen-5469": {
            "room_type": "Kitchen",
            "room_style": "Swedish",
            "room_area": 4.823946000000003,
            "room_height": 2.8,
            "layout_scheme": [
                {
                    "code": 10100,
                    "score": 80,
                    "type": "Kitchen",
                    "style": "Swedish",
                    "area": 4.823946000000003,
                    "material": {
                        "id": "Kitchen-5469",
                        "type": "Kitchen",
                        "floor": [
                            {
                                "jid": "152212f8-bf59-4b84-8b4b-96591f6382bc",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/152212f8-bf59-4b84-8b4b-96591f6382bc/wallfloor_mini.png",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.6,
                                    0.6
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "24865",
                                "area": 4.560939
                            }
                        ],
                        "wall": [
                            {
                                "jid": "eabb6b37-d2c1-4f3c-8e4f-68c0f4a177bb",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/eabb6b37-d2c1-4f3c-8e4f-68c0f4a177bb/wallfloor_mini.png",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.6,
                                    1.2
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "25087",
                                "area": 9.222999999999999,
                                "wall": [
                                    [
                                        1.321002,
                                        -4.1965
                                    ],
                                    [
                                        1.321002,
                                        -1.7095
                                    ]
                                ],
                                "offset": True,
                                "alias": "eabb6b37-d2c1-4f3c-8e4f-68c0f4a177bb"
                            },
                            {
                                "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                                "texture_url": "",
                                "color": [
                                    248,
                                    249,
                                    251
                                ],
                                "colorMode": "color",
                                "size": [
                                    1,
                                    1
                                ],
                                "seam": False,
                                "material_id": "2729",
                                "area": 0.07399999999999984,
                                "wall": [
                                    [
                                        1.321002,
                                        -4.136500000000001
                                    ],
                                    [
                                        1.261002,
                                        -4.136500000000001
                                    ]
                                ],
                                "offset": True,
                                "alias": "c53afd8f-6b30-4d1b-8454-0138ff5d7147"
                            }
                        ],
                        "win_pocket": [],
                        "door_pocket": [],
                        "win": [
                            {
                                "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                "type": "window/floor-based window",
                                "style": "Contemporary",
                                "size": [
                                    272.919,
                                    216.796,
                                    12.0
                                ],
                                "scale": [
                                    0.285964,
                                    1,
                                    1
                                ],
                                "position": [
                                    2.107214,
                                    0.2,
                                    -4.1965
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "12597",
                                "categories": [
                                    "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                ],
                                "pocket": {
                                    "jid": "",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                    "color": [
                                        255,
                                        255,
                                        255
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        2.729192,
                                        0.001
                                    ],
                                    "seam": False,
                                    "material_id": "12677",
                                    "area": -1
                                },
                                "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                "unit_to_room": "",
                                "unit_to_type": "",
                                "role": "window",
                                "count": 1,
                                "relate": "",
                                "relate_group": "",
                                "relate_position": []
                            }
                        ],
                        "door": {
                            "LivingDiningRoom": [
                                {
                                    "id": "1e8a476f-6902-4f3c-ad90-da73bede3334",
                                    "type": "door/double sliding door",
                                    "style": "Swedish",
                                    "size": [
                                        280.891,
                                        188.26200000000003,
                                        12.5
                                    ],
                                    "scale": [
                                        0.293642,
                                        1.115467,
                                        1
                                    ],
                                    "position": [
                                        1.261002,
                                        0,
                                        -3.058504
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "18673",
                                    "categories": [
                                        "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000"
                                    ],
                                    "category": "2bc73bd5-2f0a-467c-a8ec-4ff285b3a000",
                                    "unit_to_room": "LivingDiningRoom-5376",
                                    "unit_to_type": "LivingDiningRoom",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ]
                        },
                        "background": []
                    },
                    "decorate": {},
                    "painting": {},
                    "group": [
                        {
                            "type": "Wall",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Ceiling",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Floor",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Door",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Window",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                    "type": "window/floor-based window",
                                    "style": "Contemporary",
                                    "size": [
                                        272.919,
                                        216.796,
                                        12.0
                                    ],
                                    "scale": [
                                        0.285964,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        2.107214,
                                        0.2,
                                        -4.1965
                                    ],
                                    "rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "entityId": "12597",
                                    "categories": [
                                        "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            2.729192,
                                            0.001
                                        ],
                                        "seam": False,
                                        "material_id": "12677",
                                        "area": -1
                                    },
                                    "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                    "unit_to_room": "",
                                    "unit_to_type": "",
                                    "role": "window",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Background",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Customize",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        }
                    ],
                    "group_area": 0.5949597066,
                    "source_house": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4",
                    "source_room": "Kitchen-5469",
                    "source_room_area": 4.823946000000003,
                    "line_unit": [
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0.6,
                            "angle": 0,
                            "p1": [
                                1.321,
                                -4.137
                            ],
                            "p2": [
                                1.321,
                                -3.9069999999999996
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 2,
                            "width": 0.386,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    2.0379999999999994
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                1.321,
                                -3.9069999999999996
                            ],
                            "p2": [
                                1.321,
                                -3.521
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 2,
                            "width": 0.925,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 0,
                            "p1": [
                                1.321,
                                -3.521
                            ],
                            "p2": [
                                1.321,
                                -2.596
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "LivingDiningRoom-5376",
                            "unit_to_type": "LivingDiningRoom"
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 0.827,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    2.0379999999999994
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                1.321,
                                -2.596
                            ],
                            "p2": [
                                1.321,
                                -1.769
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 8,
                            "width": 2.038,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0.0,
                                    0.405,
                                    0.8765970248982542
                                ],
                                [
                                    0.405,
                                    1.0,
                                    2.3670000000000018
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                1.321,
                                -1.77
                            ],
                            "p2": [
                                3.359,
                                -1.77
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.6,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 2.137,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    -0.0,
                                    0.40982218062704723,
                                    2.0379999999999994
                                ],
                                [
                                    0.40982218062704723,
                                    0.7963841834347215,
                                    1.6130026092143448
                                ],
                                [
                                    0.7963841834347215,
                                    1,
                                    2.0379999999999994
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                3.359,
                                -1.77
                            ],
                            "p2": [
                                3.359,
                                -3.9069999999999996
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.6,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                3.359,
                                -3.9069999999999996
                            ],
                            "p2": [
                                3.359,
                                -4.137
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0,
                            "depth_post": 0,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 4,
                            "score": 8,
                            "width": 2.0380000000000003,
                            "depth": 0.386,
                            "depth_all": [
                                [
                                    0.0,
                                    0.5955740922473013,
                                    2.3670000000000018
                                ],
                                [
                                    0.5955740922473013,
                                    1.0,
                                    0.6655890248982557
                                ]
                            ],
                            "height": 0.6,
                            "angle": -1.5707963267948966,
                            "p1": [
                                3.359,
                                -4.137
                            ],
                            "p2": [
                                1.321,
                                -4.137
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.23,
                            "depth_post": 0.23,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                1.717,
                                -4.137
                            ],
                            "width_original": 0.78,
                            "p1_original": [
                                2.497,
                                -4.137
                            ]
                        }
                    ]
                }
            ],
            "layout_mesh": []
        },
        "Library-5490": {
            "room_type": "Library",
            "room_style": "Chinese Modern",
            "room_area": 9.944694000000002,
            "room_height": 2.8,
            "layout_scheme": [
                {
                    "code": 10201,
                    "score": 80,
                    "type": "Library",
                    "style": "Chinese Modern",
                    "area": 9.944694000000002,
                    "material": {
                        "id": "Library-5490",
                        "type": "Library",
                        "floor": [
                            {
                                "jid": "5262f3a8-6c27-4545-ba19-1f0ef3094539",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/5262f3a8-6c27-4545-ba19-1f0ef3094539/wallfloor.png",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.3,
                                    0.6
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "20332",
                                "area": 9.360054
                            }
                        ],
                        "wall": [
                            {
                                "jid": "acd31a0a-da3f-48f3-bbd9-6e5469a69da3",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/acd31a0a-da3f-48f3-bbd9-6e5469a69da3/wallfloor_mini.png",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.8,
                                    0.8
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "22178",
                                "area": 13.171,
                                "wall": [
                                    [
                                        6.306002,
                                        -5.3555
                                    ],
                                    [
                                        6.306002,
                                        -1.7165
                                    ]
                                ],
                                "offset": True,
                                "alias": "acd31a0a-da3f-48f3-bbd9-6e5469a69da3"
                            },
                            {
                                "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                                "texture_url": "",
                                "color": [
                                    248,
                                    249,
                                    251
                                ],
                                "colorMode": "color",
                                "size": [
                                    1,
                                    1
                                ],
                                "seam": False,
                                "material_id": "3937",
                                "area": 0.003000000000001002,
                                "wall": [
                                    [
                                        3.420002,
                                        -4.1965
                                    ],
                                    [
                                        3.419002,
                                        -4.1965
                                    ]
                                ],
                                "alias": "c53afd8f-6b30-4d1b-8454-0138ff5d7147"
                            }
                        ],
                        "win_pocket": [],
                        "door_pocket": [],
                        "ceiling": [
                            {
                                "id": "2d2f91f5-22d6-4891-9d22-68ef3e995be8",
                                "type": "build element/ceiling molding",
                                "style": "\u73b0\u4ee3",
                                "size": [
                                    337.0,
                                    22.1789,
                                    368.0
                                ],
                                "scale": [
                                    0.53636,
                                    1,
                                    0.695797
                                ],
                                "position": [
                                    4.893768,
                                    2.578211,
                                    -3.505234
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "19535",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "2d2f91f5-22d6-4891-9d22-68ef3e995be8",
                                "type": "build element/ceiling molding",
                                "style": "\u73b0\u4ee3",
                                "size": [
                                    337.0,
                                    22.1789,
                                    368.0
                                ],
                                "scale": [
                                    0.53636,
                                    1,
                                    0.695797
                                ],
                                "position": [
                                    4.893768,
                                    2.578211,
                                    -3.505234
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "19535",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "2d2f91f5-22d6-4891-9d22-68ef3e995be8",
                                "type": "build element/ceiling molding",
                                "style": "\u73b0\u4ee3",
                                "size": [
                                    337.0,
                                    22.1789,
                                    368.0
                                ],
                                "scale": [
                                    0.53636,
                                    1,
                                    0.695797
                                ],
                                "position": [
                                    4.893768,
                                    2.578211,
                                    -3.505234
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "19535",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "2d2f91f5-22d6-4891-9d22-68ef3e995be8",
                                "type": "build element/ceiling molding",
                                "style": "\u73b0\u4ee3",
                                "size": [
                                    337.0,
                                    22.1789,
                                    368.0
                                ],
                                "scale": [
                                    0.53636,
                                    1,
                                    0.695797
                                ],
                                "position": [
                                    4.893768,
                                    2.578211,
                                    -3.505234
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "19535",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            }
                        ],
                        "win": [
                            {
                                "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                "type": "window/floor-based window",
                                "style": "Contemporary",
                                "size": [
                                    272.919,
                                    216.796,
                                    12.0
                                ],
                                "scale": [
                                    0.797306,
                                    1,
                                    1
                                ],
                                "position": [
                                    5.038002,
                                    0.2,
                                    -5.3555
                                ],
                                "rotation": [
                                    0,
                                    1.0,
                                    0,
                                    6.123233995736766e-17
                                ],
                                "entityId": "12684",
                                "categories": [
                                    "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                ],
                                "pocket": {
                                    "jid": "",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                    "color": [
                                        255,
                                        255,
                                        255
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        2.729192,
                                        0.001
                                    ],
                                    "seam": False,
                                    "material_id": "12764",
                                    "area": -1
                                },
                                "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                "unit_to_room": "",
                                "unit_to_type": "",
                                "role": "window",
                                "count": 1,
                                "relate": "",
                                "relate_group": "",
                                "relate_position": []
                            }
                        ],
                        "door": {
                            "LivingDiningRoom": [
                                {
                                    "id": "f6818cb3-eb0d-4255-8dd6-c0e50f9084e0",
                                    "type": "door/entry/single swing door",
                                    "style": "Swedish",
                                    "size": [
                                        160.191,
                                        240.07999999999998,
                                        12.5
                                    ],
                                    "scale": [
                                        0.456641,
                                        0.899392,
                                        1
                                    ],
                                    "position": [
                                        4.000758,
                                        0,
                                        -1.7165
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "18092",
                                    "categories": [
                                        "69d013d3-354d-44af-bdfd-22a1181a8001"
                                    ],
                                    "category": "69d013d3-354d-44af-bdfd-22a1181a8001",
                                    "unit_to_room": "LivingDiningRoom-5376",
                                    "unit_to_type": "LivingDiningRoom",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ]
                        },
                        "background": []
                    },
                    "decorate": {},
                    "painting": {},
                    "group": [
                        {
                            "type": "Work",
                            "code": 1101,
                            "size": [
                                1.8847399999999999,
                                0.918732,
                                1.3189100000000005
                            ],
                            "offset": [
                                -0.0,
                                0,
                                -0.20625500000000022
                            ],
                            "position": [
                                5.5865469999999995,
                                0,
                                -4.29313
                            ],
                            "rotation": [
                                0,
                                -0.7071067811865475,
                                0,
                                0.7071067811865476
                            ],
                            "size_min": [
                                1.8847399999999999,
                                0.918732,
                                0.9064
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.41251000000000043,
                                0.0
                            ],
                            "obj_main": "fcfbc8b2-1c5f-4722-bd51-01db2cc0bb4a",
                            "obj_type": "table/table",
                            "obj_list": [
                                {
                                    "id": "fcfbc8b2-1c5f-4722-bd51-01db2cc0bb4a",
                                    "type": "table/table",
                                    "style": "Chinese Modern",
                                    "size": [
                                        188.474,
                                        91.8732,
                                        90.64
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        5.792802,
                                        0,
                                        -4.29313
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "27520",
                                    "categories": [
                                        "5c76d84c-aa8c-4bb8-88fc-cbf8da81be71"
                                    ],
                                    "category": "5c76d84c-aa8c-4bb8-88fc-cbf8da81be71",
                                    "relate": "wall",
                                    "group": "Work",
                                    "role": "table",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        5.792802,
                                        0,
                                        -4.29313
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                },
                                {
                                    "id": "fdd81a82-935c-4d9c-9a57-b8cb9ef2aa07",
                                    "type": "chair/chair",
                                    "style": "Swedish",
                                    "size": [
                                        75.4238,
                                        79.6142,
                                        92.9958
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        5.392071,
                                        0,
                                        -4.535242
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17368",
                                    "categories": [
                                        "f2c08afc-68c8-42a7-b62c-1b648f87edba"
                                    ],
                                    "category": "f2c08afc-68c8-42a7-b62c-1b648f87edba",
                                    "group": "Work",
                                    "role": "chair",
                                    "count": 1,
                                    "relate": "",
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        5.392071,
                                        0,
                                        -4.535242
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        -0.24211200000000066,
                                        0,
                                        0.40073100000000034
                                    ],
                                    "normal_rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ]
                                },
                                {
                                    "id": "eb992c56-6d74-46ec-a7a3-164c7057da4a",
                                    "type": "electronics/computer",
                                    "style": "Contemporary",
                                    "size": [
                                        30.0127,
                                        21.3651,
                                        22.6413
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        6.043692,
                                        0.598905,
                                        -4.102153
                                    ],
                                    "rotation": [
                                        0,
                                        -0.8502021762828798,
                                        0,
                                        0.5264563224464638
                                    ],
                                    "entityId": "17367",
                                    "categories": [
                                        "506f8b56-81a8-4017-9982-2c597c3bff8a"
                                    ],
                                    "category": "506f8b56-81a8-4017-9982-2c597c3bff8a",
                                    "group": "Work",
                                    "role": "accessory",
                                    "count": 1,
                                    "relate": "fcfbc8b2-1c5f-4722-bd51-01db2cc0bb4a",
                                    "relate_role": "table",
                                    "relate_group": "Work",
                                    "relate_position": [
                                        5.792802,
                                        0,
                                        -4.29313
                                    ],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        6.043692,
                                        0.598905,
                                        -4.102153
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.8502021762828798,
                                        0,
                                        0.5264563224464638
                                    ],
                                    "normal_position": [
                                        0.19097699999999937,
                                        0.598905,
                                        -0.25089
                                    ],
                                    "normal_rotation": [
                                        0,
                                        -0.22892288862875873,
                                        0,
                                        0.9734445598296109
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0.05999800000000033,
                                0.059500000000000774,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0,
                                0,
                                1.574
                            ],
                            "neighbor_more": [
                                0,
                                0,
                                0.5,
                                1.574
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "switch": 0,
                            "region_direct": -1,
                            "region_center": [],
                            "back_p1": [
                                6.306,
                                -3.351
                            ],
                            "back_p2": [
                                6.306,
                                -5.295
                            ],
                            "back_depth": 0.0,
                            "back_front": 1.3189100000000005,
                            "back_angle": -1.5707963267948966,
                            "expand": [
                                4.727091999999999,
                                -5.295,
                                6.306,
                                -1.776
                            ]
                        },
                        {
                            "type": "Wall",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Ceiling",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Floor",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "24713296-7907-4994-89b6-f072535d993b",
                                    "type": "recreation/musical instrument",
                                    "style": "Contemporary",
                                    "size": [
                                        138.422,
                                        107.836,
                                        74.7084
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        5.87246,
                                        0,
                                        -2.46861
                                    ],
                                    "rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17365",
                                    "categories": [
                                        "cbe71e44-7998-4598-b8a4-784cdb0aee4d"
                                    ],
                                    "category": "cbe71e44-7998-4598-b8a4-784cdb0aee4d",
                                    "role": "recreation",
                                    "count": 1,
                                    "relate": "fcfbc8b2-1c5f-4722-bd51-01db2cc0bb4a",
                                    "relate_group": "Work",
                                    "relate_position": [
                                        5.792802,
                                        0,
                                        -4.29313
                                    ],
                                    "relate_role": "table",
                                    "origin_position": [
                                        5.87246,
                                        0,
                                        -2.46861
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        1.8245199999999997,
                                        0,
                                        -0.07965799999999972
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Door",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Window",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                    "type": "window/floor-based window",
                                    "style": "Contemporary",
                                    "size": [
                                        272.919,
                                        216.796,
                                        12.0
                                    ],
                                    "scale": [
                                        0.797306,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        5.038002,
                                        0.2,
                                        -5.3555
                                    ],
                                    "rotation": [
                                        0,
                                        1.0,
                                        0,
                                        6.123233995736766e-17
                                    ],
                                    "entityId": "12684",
                                    "categories": [
                                        "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            2.729192,
                                            0.001
                                        ],
                                        "seam": False,
                                        "material_id": "12764",
                                        "area": -1
                                    },
                                    "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                    "unit_to_room": "",
                                    "unit_to_type": "",
                                    "role": "window",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Background",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Customize",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        }
                    ],
                    "group_area": 2.485802433400001,
                    "source_house": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4",
                    "source_room": "Library-5490",
                    "source_room_area": 9.944694000000002,
                    "line_unit": [
                        {
                            "type": 6,
                            "score": 5,
                            "width": 1.574,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0.0,
                                    0.27,
                                    1.9394951078450013
                                ],
                                [
                                    0.27,
                                    1,
                                    2.8260000000000023
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                6.306,
                                -1.776
                            ],
                            "p2": [
                                6.306,
                                -3.351
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.6,
                            "depth_post": 1.3789100000000007,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 5,
                            "width": 1.945,
                            "depth": 1.3789100000000007,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    2.8260000000000023
                                ]
                            ],
                            "height": 0.919,
                            "angle": 3.141592653589793,
                            "p1": [
                                6.306,
                                -3.351
                            ],
                            "p2": [
                                6.306,
                                -5.295
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 1.379,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                6.306,
                                -5.236
                            ],
                            "width_original": 1.885
                        },
                        {
                            "type": 4,
                            "score": 8,
                            "width": 2.826,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0.0,
                                    0.6864111818825194,
                                    3.5189999999999984
                                ],
                                [
                                    0.6864111818825194,
                                    1.0,
                                    3.093999999999999
                                ]
                            ],
                            "height": 0.6,
                            "angle": -1.5707963267948966,
                            "p1": [
                                6.306,
                                -5.295
                            ],
                            "p2": [
                                3.48,
                                -5.295
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 1.945,
                            "depth_post": 0.23,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0.0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                3.95,
                                -5.295
                            ],
                            "width_original": 0.977,
                            "p1_original": [
                                6.246,
                                -5.295
                            ]
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0.6,
                            "angle": 0,
                            "p1": [
                                3.48,
                                -5.296
                            ],
                            "p2": [
                                3.48,
                                -5.066
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 2,
                            "width": 2.439,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    2.8260000000000023
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                3.48,
                                -5.066
                            ],
                            "p2": [
                                3.48,
                                -2.627
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        { \
                            "type": 3,
                            "score": 5,
                            "width": 0.85,
                            "depth": 0.85,
                            "depth_all": [],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                3.48,
                                -2.627
                            ],
                            "p2": [
                                3.48,
                                -1.777
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.9359999999999999,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 5,
                            "width": 0.9359999999999999,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": 1.5707963267948966,
                            "p1": [
                                3.48,
                                -1.777
                            ],
                            "p2": [
                                4.417,
                                -1.777
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "LivingDiningRoom-5376",
                            "unit_to_type": "LivingDiningRoom",
                            "p1_original": [
                                3.585,
                                -1.777
                            ],
                            "width_original": 0.831
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 1.889,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    3.5189999999999984
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966, \
                            "p1": [
                                4.417,
                                -1.777
                            ],
                            "p2": [
                                6.306,
                                -1.777
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        }
                    ]
                }
            ],
            "layout_mesh": [
                {
                    "id": "2d2f91f5-22d6-4891-9d22-68ef3e995be8",
                    "type": "build element/ceiling molding",
                    "style": "\u73b0\u4ee3",
                    "size": [
                        337.0,
                        22.1789,
                        368.0
                    ],
                    "scale": [
                        0.53636,
                        1,
                        0.695797
                    ],
                    "position": [
                        4.893768,
                        2.578211,
                        -3.505234
                    ],
                    "rotation": [
                        0,
                        1.0,
                        0,
                        6.123233995736766e-17
                    ],
                    "entityId": "19535",
                    "categories": [
                        "91e376e7-ebdb-43cc-a230-827a367cf18e"
                    ],
                    "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                    "role": "ceiling"
                }
            ]
        },
        "SecondBedroom-5523": {
            "room_type": "SecondBedroom",
            "room_style": "Contemporary",
            "room_area": 14.837229563112,
            "room_height": 2.8,
            "layout_scheme": [
                {
                    "code": 20400,
                    "score": 80,
                    "type": "SecondBedroom",
                    "style": "Contemporary",
                    "area": 14.837229563112,
                    "material": {
                        "id": "SecondBedroom-5523",
                        "type": "SecondBedroom",
                        "floor": [
                            {
                                "jid": "858b121d-997d-48a5-9b18-c0e846b9a2af",
                                "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/858b121d-997d-48a5-9b18-c0e846b9a2af/wallfloor.png",
                                "color": [
                                    255,
                                    255,
                                    255
                                ],
                                "colorMode": "texture",
                                "size": [
                                    0.3,
                                    0.6
                                ],
                                "seam": {
                                    "jid": "16807240-b36e-4777-aca4-03ea45f7bf9c",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/16807240-b36e-4777-aca4-03ea45f7bf9c/wallfloor.png",
                                    "color": [
                                        104,
                                        104,
                                        102
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        1,
                                        1
                                    ]
                                },
                                "material_id": "19157",
                                "area": 13.815557563112002
                            }
                        ],
                        "wall": [
                            {
                                "jid": "9cb801b9-6b25-4c44-8f34-15def8286954",
                                "texture_url": "",
                                "color": None,
                                "colorMode": "color",
                                "size": [
                                    4.148148,
                                    2.8
                                ],
                                "seam": False,
                                "material_id": "24818",
                                "area": 15.618231999999999,
                                "wall": [
                                    [
                                        -6.306002,
                                        -0.557616
                                    ],
                                    [
                                        -6.306002,
                                        3.7775
                                    ]
                                ],
                                "offset": True,
                                "alias": "9cb801b9-6b25-4c44-8f34-15def8286954"
                            }
                        ],
                        "win_pocket": [],
                        "door_pocket": [],
                        "customized_ceiling": [],
                        "ceiling": [
                            {
                                "id": "66f5b2a1-92fc-4dfe-a81b-cc5d20e38be7",
                                "type": "build element/ceiling molding",
                                "style": "\u65b0\u4e2d\u5f0f",
                                "size": [
                                    254.99999999999997,
                                    29.7313,
                                    319.0
                                ],
                                "scale": [
                                    0.978842,
                                    1,
                                    0.875027
                                ],
                                "position": [
                                    -4.619254,
                                    2.502687,
                                    1.695688
                                ],
                                "rotation": [
                                    0,
                                    0.0,
                                    0,
                                    1.0
                                ],
                                "entityId": "19732",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "66f5b2a1-92fc-4dfe-a81b-cc5d20e38be7",
                                "type": "build element/ceiling molding",
                                "style": "\u65b0\u4e2d\u5f0f",
                                "size": [
                                    254.99999999999997,
                                    29.7313,
                                    319.0
                                ],
                                "scale": [
                                    0.978842,
                                    1,
                                    0.875027
                                ],
                                "position": [
                                    -4.619254,
                                    2.502687,
                                    1.695688
                                ],
                                "rotation": [
                                    0,
                                    0.0,
                                    0,
                                    1.0
                                ],
                                "entityId": "19732",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "66f5b2a1-92fc-4dfe-a81b-cc5d20e38be7",
                                "type": "build element/ceiling molding",
                                "style": "\u65b0\u4e2d\u5f0f",
                                "size": [
                                    254.99999999999997,
                                    29.7313,
                                    319.0
                                ],
                                "scale": [
                                    0.978842,
                                    1,
                                    0.875027
                                ],
                                "position": [
                                    -4.619254,
                                    2.502687,
                                    1.695688
                                ],
                                "rotation": [
                                    0,
                                    0.0,
                                    0,
                                    1.0
                                ],
                                "entityId": "19732",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            },
                            {
                                "id": "66f5b2a1-92fc-4dfe-a81b-cc5d20e38be7",
                                "type": "build element/ceiling molding",
                                "style": "\u65b0\u4e2d\u5f0f",
                                "size": [
                                    254.99999999999997,
                                    29.7313,
                                    319.0
                                ],
                                "scale": [
                                    0.978842,
                                    1,
                                    0.875027
                                ],
                                "position": [
                                    -4.619254,
                                    2.502687,
                                    1.695688
                                ],
                                "rotation": [
                                    0,
                                    0.0,
                                    0,
                                    1.0
                                ],
                                "entityId": "19732",
                                "categories": [
                                    "91e376e7-ebdb-43cc-a230-827a367cf18e"
                                ],
                                "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                                "role": "ceiling"
                            }
                        ],
                        "win": [
                            {
                                "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                "type": "window/floor-based window",
                                "style": "Contemporary",
                                "size": [
                                    272.919,
                                    216.796,
                                    12.0
                                ],
                                "scale": [
                                    0.604011,
                                    1,
                                    1
                                ],
                                "position": [
                                    -4.623687,
                                    0.2,
                                    4.4735
                                ],
                                "rotation": [
                                    0,
                                    -0.0,
                                    0,
                                    1.0
                                ],
                                "entityId": "12152",
                                "categories": [
                                    "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                ],
                                "pocket": {
                                    "jid": "",
                                    "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                    "color": [
                                        255,
                                        255,
                                        255
                                    ],
                                    "colorMode": "texture",
                                    "size": [
                                        2.729192,
                                        0.001
                                    ],
                                    "seam": False,
                                    "material_id": "12232",
                                    "area": -1
                                },
                                "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                "unit_to_room": "",
                                "unit_to_type": "",
                                "role": "window",
                                "count": 1,
                                "relate": "",
                                "relate_group": "",
                                "relate_position": []
                            }
                        ],
                        "door": {
                            "LivingDiningRoom": [
                                {
                                    "id": "32cd827e-3d58-428d-84ba-39c7ae518118",
                                    "type": "door/entry/double swing door - asymmetrical",
                                    "style": "Swedish",
                                    "size": [
                                        127.755,
                                        205.39999999999998,
                                        24.0
                                    ],
                                    "scale": [
                                        0.631927,
                                        1.051246,
                                        1
                                    ],
                                    "position": [
                                        -3.481661,
                                        0,
                                        -0.0155
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "19080",
                                    "categories": [
                                        "e9eadbdd-03c9-46c3-b947-f13c4e32e908"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/32cd827e-3d58-428d-84ba-39c7ae518118/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            1.274739,
                                            2.053975
                                        ],
                                        "seam": False,
                                        "material_id": "19147",
                                        "area": -1
                                    },
                                    "unit_to_room": "LivingDiningRoom-5376",
                                    "unit_to_type": "LivingDiningRoom",
                                    "category": "e9eadbdd-03c9-46c3-b947-f13c4e32e908",
                                    "role": "door",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ]
                        },
                        "background": []
                    },
                    "decorate": {},
                    "painting": {},
                    "group": [
                        {
                            "type": "Bed",
                            "code": 12000,
                            "size": [
                                3.2660254914758333,
                                0.96,
                                2.10439
                            ],
                            "offset": [
                                -0.021084741139524854,
                                0,
                                -0.0
                            ],
                            "position": [
                                -5.193807,
                                0,
                                2.084987254262083
                            ],
                            "rotation": [
                                0,
                                0.7071067811865475,
                                0,
                                0.7071067811865476
                            ],
                            "size_min": [
                                2.23924,
                                0.96,
                                2.10439
                            ],
                            "size_rest": [
                                0.0,
                                0.49230800459839186,
                                0.0,
                                0.5344774868774416
                            ],
                            "obj_main": "b529e255-88f1-4b14-9801-8ff8b2672d78",
                            "obj_type": "bed/king-size bed",
                            "obj_list": [
                                {
                                    "id": "b529e255-88f1-4b14-9801-8ff8b2672d78",
                                    "type": "bed/king-size bed",
                                    "style": "Contemporary",
                                    "size": [
                                        223.924,
                                        96.0,
                                        210.439
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -5.193807,
                                        0,
                                        2.049885
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "24835",

             "categories": [
                                        "41ac92b5-5f88-46d0-a59a-e1ed31739154"
                                    ],
                                    "category": "41ac92b5-5f88-46d0-a59a-e1ed31739154",
                                    "relate": "wall",
                                    "group": "Bed",
                                    "role": "bed",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -5.193807,
                                        0,
                                        2.049885
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                },
                                {
                                    "id": "b6f3b0ec-6e65-452d-87cc-33a861cf2edd",
                                    "type": "table/night table",
                                    "style": "Chinese Modern",
                                    "size": [
                                        68.53949737548828,
                                        120.13500213623047,
                                        52.09320068359375
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -5.985536,
                                        0,
                                        0.738485
                                    ],
                                    "rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "entityId": "17509",
                                    "categories": [
                                        "89404b8a-5bb6-42cf-95fa-73c9bfba4c97"
                                    ],
                                    "category": "89404b8a-5bb6-42cf-95fa-73c9bfba4c97",
                                    "relate": "",
                                    "group": "Bed",
                                    "role": "side table",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -5.985536,
                                        0,
                                        0.738485
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7071067811865475,
                                        0,
                                        0.7071067811865476
                                    ],
                                    "normal_position": [
                                        1.3114000000000001,
                                        0,
                                        -0.7917289965820312
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                },
                                {
                                    "id": "b6f3b0ec-6e65-452d-87cc-33a861cf2edd",
                                    "type": "table/night table",
                                    "style": "Chinese Modern",
                                    "size": [
                                        68.53949737548828,
                                        120.13500213623047,
                                        52.09320068359375
                                    ],
                                    "scale": [
                                        1,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -5.969157,
                                        0,
                                        3.309571
                                    ],
                                    "rotation": [
                                        0,
                                        0.7202683699094771,
                                        0,
                                        0.6936955206053623
                                    ],
                                    "entityId": "17508",
                                    "categories": [
                                        "89404b8a-5bb6-42cf-95fa-73c9bfba4c97"
                                    ],
                                    "category": "89404b8a-5bb6-42cf-95fa-73c9bfba4c97",
                                    "relate": "",
                                    "group": "Bed",
                                    "role": "side table",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -5.969157,
                                        0,
                                        3.309571
                                    ],
                                    "origin_rotation": [
                                        0,
                                        0.7202683699094771,
                                        0,
                                        0.6936955206053623
                                    ],
                                    "normal_position": [
                                        -1.259686,
                                        0,
                                        -0.7753500000000001
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.018789841938387904,
                                        0,
                                        0.999823455335956
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0.059997999999999996,
                                0,
                                0,
                                0
                            ],
                            "neighbor_base": [
                                0,
                                0,
                                0,
                                0.299
                            ],
                            "neighbor_more": [
                                0,
                                0,
                                0.23721887293124966,
                                0.299
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "switch": 0,
                            "region_direct": -1,
                            "region_center": [],
                            "back_p1": [
                                -6.306,
                                0.452
                            ],
                            "back_p2": [
                                -6.306,
                                3.718
                            ],
                            "back_depth": 0.0,
                            "back_front": 2.10439,
                            "back_angle": 1.5707963267948966,
                            "expand": [
                                -6.306,
                                0.39578751312255833,
                                -4.14161,
                                3.718
                            ]
                        },
                        {
                            "type": "Armoire",
                            "code": 10,
                            "size": [
                                2.1509214389199998,
                                2.07336,
                                0.590119
                            ],
                            "offset": [
                                -0.0,
                                0,
                                -0.0
                            ],
                            "position": [
                                -5.170542,
                                0,
                                -0.142556
                            ],
                            "rotation": [
                                0,
                                -0.0,
                                0,
                                1.0
                            ],
                            "size_min": [
                                2.1509214389199998,
                                2.07336,
                                0.590119
                            ],
                            "size_rest": [
                                0.0,
                                0.0,
                                0.0,
                                0.0
                            ],
                            "obj_main": "252a1568-be96-4451-9247-9d51cf7731e4",
                            "obj_type": "storage unit/armoire - L shaped",
                            "obj_list": [
                                {
                                    "id": "252a1568-be96-4451-9247-9d51cf7731e4",
                                    "type": "storage unit/armoire - L shaped",
                                    "style": "Contemporary",
                                    "size": [
                                        145.076,
                                        207.336,
                                        59.0119
                                    ],
                                    "scale": [
                                        1.482617,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -5.170542,
                                        0,
                                        -0.142556
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "17510",
                                    "categories": [
                                        "2dd2368f-a3eb-43c2-8a6b-d585cd19d9a6"
                                    ],
                                    "category": "2dd2368f-a3eb-43c2-8a6b-d585cd19d9a6",
                                    "relate": "wall",
                                    "group": "Armoire",
                                    "role": "armoire",
                                    "count": 1,
                                    "relate_position": [],
                                    "adjust_position": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "origin_position": [
                                        -5.170542,
                                        0,
                                        -0.142556
                                    ],
                                    "origin_rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "normal_position": [
                                        0.0,
                                        0,
                                        0.0
                                    ],
                                    "normal_rotation": [
                                        0,
                                        0.0,
                                        0,
                                        1.0
                                    ]
                                }
                            ],
                            "relate": "",
                            "relate_position": [],
                            "regulation": [
                                0.06038449999999984,
                                0.05999728053999975,
                                0,
                                0.03008128053999992
                            ],
                            "vertical": 0,
                            "window": 0,
                            "center": 0,
                            "region_direct": 0,
                            "neighbor_base": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "neighbor_more": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "switch": 0,
                            "region_center": [],
                            "back_p1": [
                                -4.065,
                                -0.498
                            ],
                            "back_p2": [
                                -6.306,
                                -0.498
                            ],
                            "back_depth": 0.0,
                            "back_front": 0.590119,
                            "back_angle": 0.0
                        },
                        {
                            "type": "Wall",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Ceiling",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Floor",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Door",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Window",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [
                                {
                                    "id": "83107d57-1e01-43e6-abf7-686a9b01435e",
                                    "type": "window/floor-based window",
                                    "style": "Contemporary",
                                    "size": [
                                        272.919,
                                        216.796,
                                        12.0
                                    ],
                                    "scale": [
                                        0.604011,
                                        1,
                                        1
                                    ],
                                    "position": [
                                        -4.623687,
                                        0.2,
                                        4.4735
                                    ],
                                    "rotation": [
                                        0,
                                        -0.0,
                                        0,
                                        1.0
                                    ],
                                    "entityId": "12152",
                                    "categories": [
                                        "5656c60a-b26c-4bf8-905a-c9da68d6dacf"
                                    ],
                                    "pocket": {
                                        "jid": "",
                                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/83107d57-1e01-43e6-abf7-686a9b01435e/pocket_tex.jpg",
                                        "color": [
                                            255,
                                            255,
                                            255
                                        ],
                                        "colorMode": "texture",
                                        "size": [
                                            2.729192,
                                            0.001
                                        ],
                                        "seam": False,
                                        "material_id": "12232",
                                        "area": -1
                                    },
                                    "category": "5656c60a-b26c-4bf8-905a-c9da68d6dacf",
                                    "unit_to_room": "",
                                    "unit_to_type": "",
                                    "role": "window",
                                    "count": 1,
                                    "relate": "",
                                    "relate_group": "",
                                    "relate_position": []
                                }
                            ],
                            "mat_list": []
                        },
                        {
                            "type": "Background",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [ \
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        },
                        {
                            "type": "Customize",
                            "size": [
                                0,
                                0,
                                0
                            ],
                            "offset": [
                                0,
                                0,
                                0
                            ],
                            "position": [
                                0,
                                0,
                                0
                            ],
                            "rotation": [
                                0,
                                0,
                                0,
                                1
                            ],
                            "obj_main": "",
                            "obj_list": [],
                            "mat_list": []
                        }
                    ],
                    "group_area": 8.14229099262086,
                    "source_house": "0007aee4-a8fa-4c64-bfcb-81fa4541d4b4",
                    "source_room": "SecondBedroom-5523",
                    "source_room_area": 14.837229563112,
                    "line_unit": [
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.46599999999999997,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0.016429184549356223,
                                    1,
                                    2.2179999999999973
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -5.482,
                                3.718
                            ],
                            "p2": [
                                -5.482,
                                4.183330459770115
                            ],
                            "score_pre": 2,
                            "score_post": 1,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -5.482,
                                4.183330459770115
                            ],
                            "p2": [
                                -5.482,
                                4.413
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0,
                            "depth_post": 0,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 4,
                            "score": 8,
                            "width": 2.2169999999999996,
                            "depth": 0.45799999999999996,
                            "depth_all": [
                                [
                                    0.0,
                                    0.6385638249887237,
                                    4.911116
                                ],
                                [
                                    0.6385638249887237, \
                                    0.7203319801533605,
                                    4.369
                                ],
                                [
                                    0.7203319801533605,
                                    1.0,
                                    3.944
                                ]
                            ],
                            "height": 0.6,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -5.482,
                                4.413
                            ],
                            "p2": [
                                -3.264,
                                4.413
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.23,
                            "depth_post": 0.23,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                -3.739,
                                4.413
                            ],
                            "width_original": 1.648,
                            "p1_original": [ \
                                -5.388,
                                4.413
                            ]
                        },
                        {
                            "type": 3,
                            "score": -1,
                            "width": 0.23,
                            "depth": 0,
                            "depth_all": [],
                            "height": 0.6,
                            "angle": 3.141592653589793,
                            "p1": [
                                -3.264,
                                4.413
                            ],
                            "p2": [
                                -3.264,
                                4.183334302325582
                            ],
                            "score_pre": 0,
                            "score_post": 0,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 3,
                            "width": 0.45799999999999996,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    2.2179999999999973
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                -3.264,
                                4.183334302325582
                            ],
                            "p2": [
                                -3.264,
                                3.726
                            ],
                            "score_pre": 1,
                            "score_post": 2,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 6,
                            "width": 0.246,
                            "depth": 0.6,
                            "depth_all": [
                                [
                                    0.0,
                                    1.0, \
                                    3.256000000000005
                                ]
                            ],
                            "height": 0,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -3.264,
                                3.726
                            ],
                            "p2": [
                                -3.018,
                                3.726
                            ],
                            "score_pre": 2,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.6,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 6,
                            "score": 5,
                            "width": 2.831,
                            "depth": 0.246,
                            "depth_all": [
                                [
                                    0.0026004945249028613,
                                    1,
                                    3.2879999999999994
                                ]
                            ],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                -3.018,
                                3.725
                            ],
                            "p2": [
                                -3.018,
                                0.8940000000000001
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 0.246,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 3,
                            "score": 5,
                            "width": 0.85,
                            "depth": 0.85,
                            "depth_all": [],
                            "height": 0,
                            "angle": 3.141592653589793,
                            "p1": [
                                -3.018,
                                0.8940000000000001
                            ],
                            "p2": [
                                -3.018,
                                0.044
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 1.0470000000000002,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 2,
                            "score": 6,
                            "width": 1.0470000000000002,
                            "depth": 0.85,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    0.85
                                ]
                            ],
                            "height": 2.8,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -3.018,
                                0.044
                            ],
                            "p2": [
                                -4.065,
                                0.044
                            ],
                            "score_pre": 4,
                            "score_post": 2,
                            "depth_pre": 0.85,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 0.12,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "LivingDiningRoom-5376",
                            "unit_to_type": "LivingDiningRoom",
                            "p2_original": [
                                -3.935,
                                0.044
                            ],
                            "width_original": 0.917
                        },
                        {
                            "type": 1,
                            "score": 6,
                            "width": 0.542,
                            "depth": 0.03,
                            "depth_all": [
                                [
                                    0.0,
                                    1,
                                    2.2406819999999987
                                ]
                            ],
                            "height": 2.073,
                            "angle": 3.141592653589793,
                            "p1": [
                                -4.065,
                                0.044
                            ],
                            "p2": [
                                -4.065,
                                -0.498
                            ],
                            "score_pre": 2,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 2.241,
                            "unit_index": 1,
                            "unit_depth": 2.181,
                            "unit_margin": 0.03,
                            "unit_edge": 3,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                -4.065,
                                -0.438
                            ],
                            "width_original": 0.482
                        },
                        {
                            "type": 1,
                            "score": 8,
                            "width": 2.241,
                            "depth": 0.6501189999999999,
                            "depth_all": [
                                [
                                    0.0,
                                    0.65,
                                    4.911116
                                ],
                                [
                                    0.65,
                                    1,
                                    4.215116000000006
                                ]
                            ],
                            "height": 2.073,
                            "angle": -1.5707963267948966,
                            "p1": [
                                -4.065,
                                -0.498
                            ],
                            "p2": [
                                -6.306,
                                -0.498
                            ],
                            "score_pre": 4,
                            "score_post": 4,
                            "depth_pre": 0.542,
                            "depth_post": 0.6499999999999999,
                            "unit_index": 1,
                            "unit_depth": 0.65,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p2_original": [
                                -6.246,
                                -0.498
                            ],
                            "width_original": 2.181
                        },
                        {
                            "type": 1,
                            "score": 5,
                            "width": 0.6499999999999999,
                            "depth": 0.06,
                            "depth_all": [
                                [
                                    0,
                                    0.817,
                                    2.2406819999999987
                                ],
                                [
                                    0.817,
                                    1,
                                    2.4206818305749995
                                ]
                            ],
                            "height": 2.073,
                            "angle": 0,
                            "p1": [
                                -6.306,
                                -0.498
                            ],
                            "p2": [
                                -6.306,
                                0.153
                            ],
                            "score_pre": 4,
                            "score_post": 1,
                            "depth_pre": 2.241,
                            "depth_post": 0.85,
                            "unit_index": 1,
                            "unit_depth": 2.211,
                            "unit_margin": 0.06,
                            "unit_edge": 1,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p1_original": [
                                -6.306,
                                -0.438
                            ],
                            "width_original": 0.59
                        },
                        {
                            "type": 3,
                            "score": 2,
                            "width": 0.299,
                            "depth": 0.2,
                            "depth_all": [
                                [
                                    0,
                                    1,
                                    2.4206818305749995
                                ]
                            ],
                            "height": 0,
                            "angle": 0,
                            "p1": [
                                -6.306,
                                0.153
                            ],
                            "p2": [
                                -6.306,
                                0.452
                            ],
                            "score_pre": 1,
                            "score_post": 1,
                            "depth_pre": 0.2,
                            "depth_post": 2.1643899999999996,
                            "unit_index": 0,
                            "unit_depth": 0,
                            "unit_margin": 0,
                            "unit_edge": 0,
                            "unit_flag": 0,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 5,
                            "width": 3.266,
                            "depth": 2.1643899999999996,
                            "depth_all": [
                                [
                                    0,
                                    0.122,
                                    2.4206818305749995
                                ],
                                [
                                    0.122,
                                    1.0,
                                    3.2879999999999994
                                ]
                            ],
                            "height": 0.96,
                            "angle": 0,
                            "p1": [
                                -6.306,
                                0.452
                            ],
                            "p2": [
                                -6.306,
                                3.718
                            ],
                            "score_pre": 1,
                            "score_post": 4,
                            "depth_pre": 0.85,
                            "depth_post": 0.8240000000000001,
                            "unit_index": 0,
                            "unit_depth": 2.164,
                            "unit_margin": 0.06,
                            "unit_edge": 0,
                            "unit_flag": 1,
                            "unit_to_room": "",
                            "unit_to_type": ""
                        },
                        {
                            "type": 1,
                            "score": 6,
                            "width": 0.8240000000000001,
                            "depth": 0,
                            "depth_all": [
                                [
                                    0,
                                    1.0,
                                    4.215116000000006
                                ]
                            ],
                            "height": 0.96,
                            "angle": 1.5707963267948966,
                            "p1": [
                                -6.306,
                                3.718
                            ],
                            "p2": [
                                -5.482,
                                3.718
                            ],
                            "score_pre": 4,
                            "score_post": 2,
                            "depth_pre": 3.266,
                            "depth_post": 0.85,
                            "unit_index": 0,
                            "unit_depth": 3.266,
                            "unit_margin": 0,
                            "unit_edge": 1,
                            "unit_flag": -1,
                            "unit_to_room": "",
                            "unit_to_type": "",
                            "p1_original": [
                                -6.246,
                                3.718
                            ],
                            "width_original": 0.764
                        }
                    ]
                }
            ],
            "layout_mesh": [
                {
                    "id": "66f5b2a1-92fc-4dfe-a81b-cc5d20e38be7",
                    "type": "build element/ceiling molding",
                    "style": "\u65b0\u4e2d\u5f0f",
                    "size": [
                        254.99999999999997,
                        29.7313,
                        319.0
                    ],
                    "scale": [
                        0.978842,
                        1,
                        0.875027
                    ],
                    "position": [
                        -4.619254,
                        2.502687,
                        1.695688
                    ],
                    "rotation": [
                        0,
                        0.0,
                        0,
                        1.0
                    ],
                    "entityId": "19732",
                    "categories": [
                        "91e376e7-ebdb-43cc-a230-827a367cf18e"
                    ],
                    "category": "91e376e7-ebdb-43cc-a230-827a367cf18e",
                    "role": "ceiling"
                }
            ]
        }
    }
    # new_a = copy.deepcopy(test_json)
    # new_a = d.to_json(test_json)
    # print(time.time() - start_t)
    a = SerializationBase.parse_json(test_json)
    print(time.time() - start_t)
    start_t = time.time()
    j = a.build_json()
    print(time.time() - start_t)
    print(type(True))


