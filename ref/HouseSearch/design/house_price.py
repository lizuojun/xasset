import json
import math
import random
import time

import numpy as np

from layout_sample import parse_design_data

ROOM_TYPE_HUMAN_PRICE = {
    "bedrooms": {
        "price_level_1": {
            "p_floor": {"price": 55.0, "method": "area"},
            "p_wall": {"price": 25.0, "method": "line"},
            "p_ceiling": {"price": 25.0, "method": "area"},
            "p_background_wall": {"price": 0.0, "method": "room"}
        },
        "price_level_2": {
            "p_floor": {"price": 90.0, "method": "area"},
            "p_wall": {"price": 70.0, "method": "line"},
            "p_ceiling": {"price": 70.0, "method": "area"},
            "p_background_wall": {"price": 0.0, "method": "room"}
        },
        "price_level_3": {
            "p_floor": {"price": 90.0, "method": "area"},
            "p_wall": {"price": 75.0, "method": "line"},
            "p_ceiling": {"price": 200.0, "method": "area"},
            "p_background_wall": {"price": 3500.0, "method": "room"}
        }
    },
    "livingRooms": {
        "price_level_1": {
            "p_floor": {"price": 55.0, "method": "area"},
            "p_wall": {"price": 25.0, "method": "line"},
            "p_ceiling": {"price": 25.0, "method": "area"},
            "p_background_wall": {"price": 0.0, "method": "room"}
        },
        "price_level_2": {
            "p_floor": {"price": 85.0, "method": "area"},
            "p_wall": {"price": 70.0, "method": "line"},
            "p_ceiling": {"price": 90.0, "method": "area"},
            "p_background_wall": {"price": 0.0, "method": "room"}
        },
        "price_level_3": {
            "p_floor": {"price": 100.0, "method": "area"},
            "p_wall": {"price": 75.0, "method": "line"},
            "p_ceiling": {"price": 200.0, "method": "area"},
            "p_background_wall": {"price": 3500.0, "method": "room"}
        }
    },
    "kitchens": {
        "price_level_1": {
            "p_floor": {"price": 55.0, "method": "area"},
            "p_wall": {"price": 60.0, "method": "line"},
            "p_baoliguan": {"price": 400.0, "method": "room"}
        },
        "price_level_2": {
            "p_floor": {"price": 55.0, "method": "area"},
            "p_wall": {"price": 60.0, "method": "line"},
            "p_baoliguan": {"price": 400.0, "method": "room"}
        },
        "price_level_3": {
            "p_floor": {"price": 55.0, "method": "area"},
            "p_wall": {"price": 60.0, "method": "line"},
            "p_baoliguan": {"price": 400.0, "method": "room"}
        }
    },
    "bathrooms": {
        "price_level_1": {
            "p_floor": {"price": 120.0, "method": "area"},
            "p_wall": {"price": 140.0, "method": "line"},
            "p_baoliguan": {"price": 400.0, "method": "room"}
        },
        "price_level_2": {
            "p_floor": {"price": 120.0, "method": "area"},
            "p_wall": {"price": 140.0, "method": "line"},
            "p_baoliguan": {"price": 400.0, "method": "room"}
        },
        "price_level_3": {
            "p_floor": {"price": 120.0, "method": "area"},
            "p_wall": {"price": 140.0, "method": "line"},
            "p_baoliguan": {"price": 400.0, "method": "room"}
        }
    },
    "balconies": {
        "price_level_1": {
            "p_wall": {"price": 25.0, "method": "line"},
            "p_floor": {"price": 55.0, "method": "area"},
            "p_ceiling": {"price": 25.0, "method": "area"}
        },
        "price_level_2": {
            "p_wall": {"price": 70.0, "method": "line"},
            "p_floor": {"price": 95.0, "method": "area"},
            "p_ceiling": {"price": 55.0, "method": "area"}
        },
        "price_level_3": {
            "p_wall": {"price": 70.0, "method": "line"},
            "p_floor": {"price": 95.0, "method": "area"},
            "p_ceiling": {"price": 55.0, "method": "area"}
        }
    },
    "others": {
        "price_level_1": {
            "p_rubbish": {"price": 500.0, "method": "house"},
            "p_moving": {"price": 1000.0, "method": "house"},
            "p_protecting": {"price": 1000.0, "method": "house"},
            "p_electric": {"price": 2500.0, "method": "house"},
            "p_water": {"price": 2500.0, "method": "house"},
            "p_others": {"price": 500.0, "method": "house"}
        },
        "price_level_2": {
            "p_rubbish": {"price": 500.0, "method": "house"},
            "p_moving": {"price": 1000.0, "method": "house"},
            "p_protecting": {"price": 1000.0, "method": "house"},
            "p_electric": {"price": 2500.0, "method": "house"},
            "p_water": {"price": 2500.0, "method": "house"},
            "p_others": {"price": 500.0, "method": "house"}
        },
        "price_level_3": {
            "p_rubbish": {"price": 500.0, "method": "house"},
            "p_moving": {"price": 1000.0, "method": "house"},
            "p_protecting": {"price": 1000.0, "method": "house"},
            "p_electric": {"price": 2500.0, "method": "house"},
            "p_water": {"price": 2500.0, "method": "house"},
            "p_others": {"price": 500.0, "method": "house"}
        }
    }
}

ROOM_TYPE_MATERIAL_PRICE = {
    "bedrooms": {
        "price_level_1": {
            "m_floor_board": {"price": 100.0, "method": "area"},
            "m_wood_door": {"price": 1000.0, "method": "room"},
            "m_painting": {"price": 4 * 10.0, "method": "line"},
            "m_door_stone": {"price": 50.0, "method": "room"}},
        "price_level_2": {
            "m_floor_board": {"price": 200.0, "method": "area"},
            "m_wood_door": {"price": 2000.0, "method": "room"},
            "m_painting": {"price": 4 * 20.0, "method": "line"},
            "m_door_stone": {"price": 70.0, "method": "room"}},
        "price_level_3": {
            "m_floor_board": {"price": 350.0, "method": "area"},
            "m_wood_door": {"price": 3000.0, "method": "room"},
            "m_painting": {"price": 4 * 30.0, "method": "line"},
            "m_door_stone": {"price": 100.0, "method": "room"}},
    },
    "livingRooms": {
        "price_level_1": {
            "m_floor_brick": {"price": 100.0, "method": "area"},
            "m_painting": {"price": 4 * 10.0, "method": "line"},
            "m_baseboard": {"price": 50.0, "method": "line"}
        },
        "price_level_2": {
            "m_floor_brick": {"price": 150.0, "method": "area"},
            "m_painting": {"price": 4 * 20.0, "method": "line"},
            "m_baseboard": {"price": 70.0, "method": "line"}
        },
        "price_level_3": {
            "m_floor_brick": {"price": 350.0, "method": "area"},
            "m_painting": {"price": 4 * 55.0, "method": "line"},
            "m_baseboard": {"price": 100.0, "method": "line"}
        }
    },
    "kitchens": {
        "price_level_1": {
            "m_floor_brick": {"price": 100.0, "method": "area"},
            "m_wall_brick": {"price": 50.0, "method": "line"},
            "m_wood_door": {"price": 1000.0, "method": "room"},
            "m_cupboard": {"price": 7000.0, "method": "house"},
            "m_ceiling": {"price": 100.0, "method": "area"},
            "m_cook_2": {"price": 3000, "method": "room"},
            "m_light": {"price": 150.0, "method": "room"}
        },
        "price_level_2": {
            "m_floor_brick": {"price": 150.0, "method": "area"},
            "m_wall_brick": {"price": 100.0, "method": "line"},
            "m_wood_door": {"price": 2000.0, "method": "room"},
            "m_cupboard": {"price": 13000.0, "method": "house"},
            "m_ceiling": {"price": 150.0, "method": "area"},
            "m_cook_2": {"price": 4500, "method": "room"},
            "m_light": {"price": 200.0, "method": "room"}
        },
        "price_level_3": {
            "m_floor_brick": {"price": 350.0, "method": "area"},
            "m_wall_brick": {"price": 150.0, "method": "line"},
            "m_wood_door": {"price": 3000.0, "method": "room"},
            "m_cupboard": {"price": 20000.0, "method": "house"},
            "m_ceiling": {"price": 180.0, "method": "area"},
            "m_cook_2": {"price": 8000, "method": "room"},
            "m_light": {"price": 300.0, "method": "room"}
        }
    },
    "bathrooms": {
        "price_level_1": {
            "m_floor_brick": {"price": 100.0, "method": "area"},
            "m_wall_brick": {"price": 50.0, "method": "line"},
            "m_toi": {"price": 900.0, "method": "room"},
            "m_clean": {"price": 700.0, "method": "room"},
            "m_bath_cabinet": {"price": 2000.0, "method": "room"},
            "m_ceiling": {"price": 120.0, "method": "area"},
            "m_door": {"price": 1000.0, "method": "room"},
            "m_light_heater": {"price": 1000.0, "method": "room"}
        },
        "price_level_2": {
            "m_floor_brick": {"price": 150.0, "method": "area"},
            "m_wall_brick": {"price": 100.0, "method": "line"},
            "m_toi": {"price": 2000.0, "method": "room"},
            "m_clean": {"price": 1000.0, "method": "room"},
            "m_bath_cabinet": {"price": 3000.0, "method": "room"},
            "m_ceiling": {"price": 150.0, "method": "area"},
            "m_door": {"price": 1200.0, "method": "room"},
            "m_light_heater": {"price": 1200.0, "method": "room"}
        },
        "price_level_3": {
            "m_floor_brick": {"price": 350.0, "method": "area"},
            "m_wall_brick": {"price": 150.0, "method": "line"},
            "m_toi": {"price": 5000.0, "method": "room"},
            "m_clean": {"price": 2000.0, "method": "room"},
            "m_bath_cabinet": {"price": 5000.0, "method": "room"},
            "m_ceiling": {"price": 190.0, "method": "area"},
            "m_door": {"price": 1600.0, "method": "room"},
            "m_light_heater": {"price": 1500.0, "method": "room"}
        }
    },
    "balconies": {
        "price_level_1": {
            "m_painting": {"price": 10.0, "method": "line"},
            "m_floor_brick": {"price": 100.0, "method": "area"},
            "m_switch": {"price": 500, "method": "room"}
        },
        "price_level_2": {
            "m_painting": {"price": 20.0, "method": "line"},
            "m_floor_brick": {"price": 150.0, "method": "area"},
            "m_switch": {"price": 1500, "method": "room"}
        },
        "price_level_3": {
            "m_painting": {"price": 30.0, "method": "line"},
            "m_floor_brick": {"price": 350.0, "method": "area"},
            "m_switch": {"price": 2000, "method": "room"}
        }
    },
}

ROOM_TYPE_FURNISHING_PRICE = {
    "bedrooms": {
        "price_level_1": {
            "f_bed_armoire": {"price": 2000.0, "method": "room"},
            "f_bed_stand": {"price": 300.0, "method": "room"},
            "f_dress_table": {"price": 1000.0, "method": "room"},
            "f_storage": {"price": 800.0, "method": "room"},
            "f_bed": {"price": 2000.0, "method": "room"},
            "f_curtain": {"price": 600.0, "method": "room"},
            "f_air_conditioner": {"price": 1500.0, "method": "room"},
            "f_light": {"price": 100, "method": "room"}
        },
        "price_level_2": {
            "f_bed_armoire": {"price": 4000.0, "method": "room"},
            "f_bed_stand": {"price": 1000.0, "method": "room"},
            "f_dress_table": {"price": 2000.0, "method": "room"},
            "f_storage": {"price": 1000.0, "method": "room"},
            "f_bed": {"price": 5000.0, "method": "room"},
            "f_curtain": {"price": 800.0, "method": "room"},
            "f_air_conditioner": {"price": 3000.0, "method": "room"},
            "f_light": {"price": 300, "method": "room"}
        },
        "price_level_3": {
            "f_bed_armoire": {"price": 8000.0, "method": "room"},
            "f_bed_stand": {"price": 2000.0, "method": "room"},
            "f_dress_table": {"price": 5000.0, "method": "room"},
            "f_storage": {"price": 3000.0, "method": "room"},
            "f_bed": {"price": 10000.0, "method": "room"},
            "f_curtain": {"price": 2000.0, "method": "room"},
            "f_air_conditioner": {"price": 5000.0, "method": "room"},
            "f_light": {"price": 500, "method": "room"}
        }
    },
    "livingRooms": {
        "price_level_1": {
            "f_sofa": {"price": 3000.0, "method": "room"},
            "f_coffee_table": {"price": 500.0, "method": "room"},
            "f_curtain": {"price": 600.0, "method": "room"},
            "f_media_unit": {"price": 500.0, "method": "room"},
            "f_shoes_cabinet": {"price": 300.0, "method": "room"},
            "f_air_conditioner": {"price": 1500.0, "method": "room"},
            "f_tv": {"price": 1500.0, "method": "house"},
            "f_light": {"price": 500.0, "method": "room"},

            "f_air": {"price": 0.0, "method": "house"},
            "f_rug_and_accs": {"price": 0.0, "method": "room"}
        },
        "price_level_2": {
            "f_sofa": {"price": 5000.0, "method": "room"},
            "f_coffee_table": {"price": 1000.0, "method": "room"},
            "f_curtain": {"price": 1200.0, "method": "room"},
            "f_media_unit": {"price": 1000.0, "method": "room"},
            "f_shoes_cabinet": {"price": 600.0, "method": "room"},
            "f_air_conditioner": {"price": 3000.0, "method": "room"},
            "f_tv": {"price": 3000.0, "method": "house"},
            "f_light": {"price": 1000.0, "method": "room"},

            "f_air": {"price": 10000.0, "method": "house"},
            "f_rug_and_accs": {"price": 2000.0, "method": "house"}
        },
        "price_level_3": {
            "f_sofa": {"price": 8000.0, "method": "room"},
            "f_coffee_table": {"price": 8000.0, "method": "room"},
            "f_curtain": {"price": 2000.0, "method": "room"},
            "f_media_unit": {"price": 2000.0, "method": "room"},
            "f_shoes_cabinet": {"price": 1000.0, "method": "room"},
            "f_air_conditioner": {"price": 5000.0, "method": "room"},
            "f_tv": {"price": 8000.0, "method": "house"},
            "f_light": {"price": 1500.0, "method": "room"},

            "f_air": {"price": 20000.0, "method": "house"},
            "f_rug_and_accs": {"price": 5000.0, "method": "house"}},
    },
    "diningRooms": {
        "price_level_1": {"f_dining": {"price": 1500.0, "method": "room"}},
        "price_level_2": {"f_dining": {"price": 3000.0, "method": "room"}},
        "price_level_3": {"f_dining": {"price": 5000.0, "method": "room"}},
    },
    "kitchens": {
        "price_level_1": {"f_fridge": {"price": 2000.0, "method": "house"},
                          "f_bowl_washer": {"price": 0.0, "method": "house"}},
        "price_level_2": {"f_fridge": {"price": 3000.0, "method": "house"},
                          "f_bowl_washer": {"price": 2000.0, "method": "house"}},
        "price_level_3": {"f_fridge": {"price": 5000.0, "method": "house"},
                          "f_bowl_washer": {"price": 4000.0, "method": "house"}},
    },
    "bathrooms": {
        "price_level_1": {"f_heater": {"price": 1000.0, "method": "room"}},
        "price_level_2": {"f_heater": {"price": 1500.0, "method": "room"}},
        "price_level_3": {"f_heater": {"price": 3000.0, "method": "room"}},
    },
    "balconies": {
        "price_level_1": {"f_clothes_washer": {"price": 1500.0, "method": "house"},
                          "f_clothes_hanger": {"price": 300.0, "method": "house"}},
        "price_level_2": {"f_clothes_washer": {"price": 2000.0, "method": "house"},
                          "f_clothes_hanger": {"price": 500.0, "method": "house"}},
        "price_level_3": {"f_clothes_washer": {"price": 5000.0, "method": "house"},
                          "f_clothes_hanger": {"price": 600.0, "method": "house"}},
    },
}


def get_door_length(pts):
    l1 = (pts[0] - pts[2]) ** 2 + (pts[1] - pts[3]) ** 2
    l2 = (pts[0] - pts[6]) ** 2 + (pts[1] - pts[7]) ** 2
    if l2 > l1:
        r = math.sqrt(l2)
    else:
        r = math.sqrt(l1)
    # print(r)
    return r


def get_room_line_area(floor, door_list, hole_list, window_list):
    line = 0.0
    for i in range(len(floor) // 2 - 1):
        start_p = [floor[2 * i + 0], floor[2 * i + 1]]
        end_p = [floor[2 * i + 2], floor[2 * i + 3]]
        # 修改地面周长 x 2.8
        line += 2.8 * math.sqrt((start_p[0] - end_p[0]) ** 2 + (start_p[1] - end_p[1]) ** 2)

    # for door in door_list:
    #     line -= 2.0 * get_door_length(door['pts'])
    #
    # for door in hole_list:
    #     line -= 2.0 * get_door_length(door['pts'])
    #
    # for window in window_list:
    #     line -= 1.4 * get_door_length(window['pts'])

    return line


def method_compute(room_type, item_name, price_item, area_single, area_wall_line_single, house_single):
    price_single = price_item['price']
    method = price_item['method']
    if method == "room":
        price = price_single * 1.0
    elif method == "area":
        price = price_single * area_single
    elif method == "line":
        price = price_single * area_wall_line_single
    elif method == "house":
        key = room_type + "_" + item_name
        if key not in house_single:
            price = price_single
            house_single.append(key)
        else:
            price = 0.0
    else:
        price = 0.0

    # print("\t%s 价格 %.2f" % (item_name, price))
    # print(round(price, 1))
    return round(price, 1)


def construct_house_without_floorplan(area, room_nums=None):
    maxRoomLength = [9, 5, 5, 5, 5]
    # // 不同房间类型的面积占比
    areaParam = [0.42, 0.36, 0.08, 0.07, 0.07]
    # // magic number
    varParam = [3.0, 0.5, 1.0, 1.0, 1.0]

    # // 得房率
    usedAreaRatio = 0.8
    if room_nums is None:
        room_nums = adviceCode(area)
    bs, ls, ks, bath, bals = detailRooms(area, usedAreaRatio, varParam, areaParam, room_nums)

    house_data = {'room': []}

    for i, a in enumerate(ls):
        side = np.sqrt(a)
        room_type = 'LivingDiningRoom'
        room_info = {
            'id': room_type + '_%d' % i,
            'type': room_type,
            'area': a,
            'floor': [0, 0., side, 0., side, side, 0, side],
            'door_info': [],
            'hole_info': [],
            'window_info': []
        }
        house_data['room'].append(room_info)
    for i, a in enumerate(bs):
        side = np.sqrt(a)
        room_type = 'MasterBedroom'
        room_info = {
            'id': room_type + '_%d' % i,
            'type': room_type,
            'area': a,
            'floor': [0, 0., side, 0., side, side, 0, side],
            'door_info': [],
            'hole_info': [],
            'window_info': []
        }
        house_data['room'].append(room_info)
    for i, a in enumerate(ks):
        side = np.sqrt(a)
        room_type = 'Kitchen'
        room_info = {
            'id': room_type + '_%d' % i,
            'type': room_type,
            'area': a,
            'floor': [0, 0., side, 0., side, side, 0, side],
            'door_info': [],
            'hole_info': [],
            'window_info': []
        }
        house_data['room'].append(room_info)
    for i, a in enumerate(bath):
        side = np.sqrt(a)
        room_type = 'Bathroom'
        room_info = {
            'id': room_type + '_%d' % i,
            'type': room_type,
            'area': a,
            'floor': [0, 0., side, 0., side, side, 0, side],
            'door_info': [],
            'hole_info': [],
            'window_info': []
        }
        house_data['room'].append(room_info)
    for i, a in enumerate(bals):
        side = np.sqrt(a)
        room_type = 'Balcony'
        room_info = {
            'id': room_type + '_%d' % i,
            'type': room_type,
            'area': a,
            'floor': [0, 0., side, 0., side, side, 0, side],
            'door_info': [],
            'hole_info': [],
            'window_info': []
        }
        house_data['room'].append(room_info)

    return house_data


def resetAreaRatio(nowCode, targetCode, areaParam):
    newArea = []
    for i in range(len(nowCode)):
        if targetCode[i] < 1e-3:
            newArea.append(0.)
        else:
            newArea.append(nowCode[i] / targetCode[i] * areaParam[i])
    allLength = arraySum(newArea)
    for i in range(len(nowCode)):
        newArea[i] = newArea[i] / allLength
    return newArea


def adviceCode(area):
    if (area < 10):
        code =[1, 0, 0, 0, 0]
    elif (area < 30):
        code =[1, 0, 1, 1, 0]
    elif (area < 55):
        code =[1, 1, 1, 1, 0]

    elif (area < 75):
        code =[1, 1, 1, 1, 1]

    elif (area < 99):
        code =[2, 1, 1, 1, 1]

    elif (area < 121):
        code =[3, 2, 1, 1, 1]

    elif (area < 140):
        code =[3, 2, 1, 2, 1]

    elif (area < 160):
        code =[4, 2, 1, 2, 2]

    elif (area < 201):
        code =[5, 2, 2, 3, 3]
    else:
        code = [5, 2, 2, 3, 3]

    return code

def arraySum(arr):
    return np.sum(arr)


def arrayMean(arr):
    return np.sum(arr) / len(arr)

def arrayVar(arr):
    m = arrayMean(arr)
    return np.sum((np.array(arr) -m) ** 2) / len(arr)


def detailRooms(area, usedAreaRatio, varParam, areaParam, nowCode):
    areaUsed = area * usedAreaRatio
    # bestCode = adviceCode(area)
    bestCode = nowCode.copy()

    bedroomCode = []
    livingCode = []
    kitchenCode = []
    bathCode = []
    balconyCode = []
    # // 固定初始面积
    areaParam_rep = []
    for i in range(len(nowCode)):
        if nowCode[i] < 0.5:
            areaParam_rep.append(0)
        else:
            areaParam_rep.append(areaParam[i])
    sum = np.sum(areaParam_rep)
    if sum < 1e-8:
        areaParam_rep = [0] * len(nowCode)
    else:
        areaParam_rep = np.array(areaParam_rep) / sum

    np.random.seed(int(areaParam_rep[0] * areaUsed))
    room_ratio = np.random.rand(nowCode[0]) / 5. + 1.
    if nowCode[0] > 0:
        room_ratio /= np.sum(room_ratio)
    for i in range(nowCode[0]):
        bedroomCode.append(areaParam_rep[0] * areaUsed * room_ratio[i])

    np.random.seed(int(areaParam_rep[1] * areaUsed))
    room_ratio = np.random.rand(nowCode[1]) / 5. + 1.
    if nowCode[1] > 0:
        room_ratio /= np.sum(room_ratio)
    for i in range(nowCode[1]):
        livingCode.append(areaParam_rep[1] * areaUsed * room_ratio[i])

    np.random.seed(int(areaParam_rep[2] * areaUsed))
    room_ratio = np.random.rand(nowCode[2]) / 5. + 1.
    if nowCode[2] > 0:
        room_ratio /= np.sum(room_ratio)
    for i in range(nowCode[2]):
        kitchenCode.append(areaParam_rep[2] * areaUsed * room_ratio[i])

    np.random.seed(int(areaParam_rep[3] * areaUsed))
    room_ratio = np.random.rand(nowCode[3]) / 5. + 1.
    if nowCode[3] > 0:
        room_ratio /= np.sum(room_ratio)
    for i in range(nowCode[3]):
        bathCode.append(areaParam_rep[3] * areaUsed * room_ratio[i])

    np.random.seed(int(areaParam_rep[4] * areaUsed))
    room_ratio = np.random.rand(nowCode[4]) / 5. + 1.
    if nowCode[4] > 0:
        room_ratio /= np.sum(room_ratio)
    for i in range(nowCode[4]):
        balconyCode.append(areaParam_rep[4] * areaUsed * room_ratio[i])

    # # // 如果用户手工调整
    # # 根据输入的code
    # # 需要重新计算面积分布
    # # // bestCode的面积分配是固定的areaParam
    #
    # targetAreaRatio = resetAreaRatio(nowCode, bestCode, areaParam)
    # l = 0
    # # // 优化目标: 每个房间类型的面积总和 符合areaParam占比
    # # // 目标 同房间类型的房间面积总和接近targetArea, 每个房间的面积接近平均值
    # for iter in range(3):
    #     bedTargetArea = targetAreaRatio[0] * areaUsed
    #     l = max(len(bedroomCode) - 1, 0)
    #
    #     for i in range(len(bedroomCode)):
    #         bedroomCode[i] = round(((bedTargetArea+bedroomCode[i]-arraySum(bedroomCode)) + varParam[0] / (l+1) * arrayMean(bedroomCode)) / (1 + varParam[0] / (l+1)), 2)
    #     livingTargetArea = targetAreaRatio[1] * areaUsed
    #     l =max(len(livingCode) - 1, 0)
    #     for i in range(len(livingCode)):
    #         livingCode[i] = round(((livingTargetArea+livingCode[i]-arraySum(livingCode)) + varParam[1] / (l+1) * arrayMean(livingCode)) / (1 + varParam[1] / (l+1)), 2)
    #
    #     kitchenTargetArea = targetAreaRatio[2] * areaUsed
    #     l = max(len(kitchenCode) - 1, 0)
    #     for i in range(len(kitchenCode)):
    #         kitchenCode[i] = round(((kitchenTargetArea+kitchenCode[i]-arraySum(kitchenCode)) + varParam[2] / (l+1) * arrayMean(kitchenCode)) / (1 + varParam[2] / (l+1)), 2)
    #
    #     bathTargetArea = targetAreaRatio[3] * areaUsed
    #     l = max(len(bathCode) - 1, 0)
    #     for i in range(len(bathCode)):
    #         bathCode[i] = round(((bathTargetArea+bathCode[i]-arraySum(bathCode)) + varParam[3] / (l+1) * arrayMean(bathCode)) / (1 + varParam[3] / (l+1)), 2)
    #
    #     balconyTargetArea = targetAreaRatio[4] * areaUsed
    #     l = max(len(balconyCode) - 1, 0)
    #     for i in range(len(balconyCode)):
    #         balconyCode[i] = round(((balconyTargetArea+balconyCode[i]-arraySum(balconyCode)) + varParam[4] / (l+1) * arrayMean(balconyCode)) / (1 + varParam[4] / (l+1)), 2)

    return bedroomCode, livingCode, kitchenCode, bathCode, balconyCode


def get_house_price_info(house_data):
    house_total_price = {"price_level_1": 0.0, "price_level_2": 0.0, "price_level_3": 0.0}
    addition_human_price = ROOM_TYPE_HUMAN_PRICE['others']
    house_single = 1.0

    price_info = {
        "price_level_1": {"person": {}, "material": {}, "furniture": {}},
        "price_level_2": {"person": {}, "material": {}, "furniture": {}},
        "price_level_3": {"person": {}, "material": {}, "furniture": {}}
    }

    for price_level in price_info:
        for room_type in ROOM_TYPE_HUMAN_PRICE:
            price_info[price_level]['person'][room_type] = {}
            for item in ROOM_TYPE_HUMAN_PRICE[room_type]['price_level_1']:
                price_info[price_level]['person'][room_type][item] = 0.0

        for room_type in ROOM_TYPE_MATERIAL_PRICE:
            price_info[price_level]['material'][room_type] = {}
            for item in ROOM_TYPE_MATERIAL_PRICE[room_type]['price_level_1']:
                price_info[price_level]['material'][room_type][item] = 0.0

        for room_type in ROOM_TYPE_FURNISHING_PRICE:
            price_info[price_level]['furniture'][room_type] = {}
            for item in ROOM_TYPE_FURNISHING_PRICE[room_type]['price_level_1']:
                price_info[price_level]['furniture'][room_type][item] = 0.0

    areas = {}
    for price_level in price_info:
        house_single = []
        house_area = {
            "bedrooms": [],
            "livingRooms": [],
            "kitchens": [],
            "bathrooms": [],
            "balconies": []
        }
        for room_data in house_data['room']:
            room_type = room_data['type']

            area_single = room_data['area']
            text_area = str(round(area_single, 2))
            area_wall_line_single = get_room_line_area(room_data['floor'], room_data['door_info'],
                                                       room_data['hole_info'], room_data['window_info'])

            # person成本 human
            if room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
                house_area['livingRooms'].append(area_single)
                # print("客厅 %s person" % text_area)
                price_items = ROOM_TYPE_HUMAN_PRICE['livingRooms'][price_level]
                for item_name in price_items:
                    price_info[price_level]['person']['livingRooms'][item_name] += method_compute("livingRooms",
                                                                                                  item_name,
                                                                                                  price_items[
                                                                                                      item_name],
                                                                                                  area_single,
                                                                                                  area_wall_line_single,
                                                                                                  house_single)

            elif room_type in ['Bedroom', 'MasterBedroom', 'SecondBedroom', 'KidsRoom', 'ElderRoom']:
                price_items = ROOM_TYPE_HUMAN_PRICE['bedrooms'][price_level]
                house_area['bedrooms'].append(area_single)
                # print("卧室 %s person" % text_area)
                for item_name in price_items:
                    price_info[price_level]['person']['bedrooms'][item_name] += method_compute("bedrooms", item_name,
                                                                                               price_items[item_name],
                                                                                               area_single,
                                                                                               area_wall_line_single,
                                                                                               house_single)

            elif room_type in ['Kitchen']:
                house_area['kitchens'].append(area_single)
                price_items = ROOM_TYPE_HUMAN_PRICE['kitchens'][price_level]
                # print("厨房 %s person" % text_area)
                for item_name in price_items:
                    price_info[price_level]['person']['kitchens'][item_name] += method_compute("kitchens", item_name,
                                                                                               price_items[item_name],
                                                                                               area_single,
                                                                                               area_wall_line_single,
                                                                                               house_single)

            elif room_type in ['Bathroom', 'MasterBathroom', 'SecondBathroom']:
                house_area['bathrooms'].append(area_single)
                price_items = ROOM_TYPE_HUMAN_PRICE['bathrooms'][price_level]
                # print("卫生间 %s person" % text_area)
                for item_name in price_items:
                    price_info[price_level]['person']['bathrooms'][item_name] += method_compute("bathrooms", item_name,
                                                                                                price_items[item_name],
                                                                                                area_single,
                                                                                                area_wall_line_single,
                                                                                                house_single)

            elif room_type in ['Balcony']:
                house_area['balconies'].append(area_single)
                price_items = ROOM_TYPE_HUMAN_PRICE['balconies'][price_level]
                # print("阳台 %s person" % text_area)
                # floor
                for item_name in price_items:
                    price_info[price_level]['person']['balconies'][item_name] += method_compute("balconies", item_name,
                                                                                                price_items[item_name],
                                                                                                area_single,
                                                                                                area_wall_line_single,
                                                                                                house_single)

            # material成本 material
            if room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
                price_items = ROOM_TYPE_MATERIAL_PRICE['livingRooms'][price_level]
                # print("客厅 %s material" % text_area)
                for item_name in price_items:
                    price_info[price_level]['material']['livingRooms'][item_name] += method_compute("livingRooms",
                                                                                                    item_name,
                                                                                                    price_items[
                                                                                                        item_name],
                                                                                                    area_single,
                                                                                                    area_wall_line_single,
                                                                                                    house_single)

            elif room_type in ['Bedroom', 'MasterBedroom', 'SecondBedroom', 'KidsRoom', 'ElderRoom']:
                price_items = ROOM_TYPE_MATERIAL_PRICE['bedrooms'][price_level]
                # print("卧室 %s material" % text_area)
                for item_name in price_items:
                    price_info[price_level]['material']['bedrooms'][item_name] += method_compute("bedrooms", item_name,
                                                                                                 price_items[item_name],
                                                                                                 area_single,
                                                                                                 area_wall_line_single,
                                                                                                 house_single)

            elif room_type in ['Kitchen']:
                price_items = ROOM_TYPE_MATERIAL_PRICE['kitchens'][price_level]
                # print("厨房 %s material" % text_area)
                for item_name in price_items:
                    price_info[price_level]['material']['kitchens'][item_name] += method_compute("kitchens", item_name,
                                                                                                 price_items[item_name],
                                                                                                 area_single,
                                                                                                 area_wall_line_single,
                                                                                                 house_single)

            elif room_type in ['Bathroom', 'MasterBathroom', 'SecondBathroom']:
                price_items = ROOM_TYPE_MATERIAL_PRICE['bathrooms'][price_level]
                # print("卫生间 %s material" % text_area)
                for item_name in price_items:
                    price_info[price_level]['material']['bathrooms'][item_name] += method_compute("bathrooms",
                                                                                                  item_name,
                                                                                                  price_items[
                                                                                                      item_name],
                                                                                                  area_single,
                                                                                                  area_wall_line_single,
                                                                                                  house_single)

            elif room_type in ['Balcony']:
                price_items = ROOM_TYPE_MATERIAL_PRICE['balconies'][price_level]
                # print("阳台 %s material" % text_area)
                for item_name in price_items:
                    price_info[price_level]['material']['balconies'][item_name] += method_compute("balconies",
                                                                                                  item_name,
                                                                                                  price_items[
                                                                                                      item_name],
                                                                                                  area_single,
                                                                                                  area_wall_line_single,
                                                                                                  house_single)

            # 家具/电器成本 furnishing
            if room_type in ['LivingDiningRoom', 'LivingRoom']:
                price_items = ROOM_TYPE_FURNISHING_PRICE['livingRooms'][price_level]

                # print("客厅 %s 家具/电器" % text_area)
                for item_name in price_items:
                    price_info[price_level]['furniture']['livingRooms'][item_name] += method_compute("livingRooms",
                                                                                                     item_name,
                                                                                                     price_items[
                                                                                                         item_name],
                                                                                                     area_single,
                                                                                                     area_wall_line_single,
                                                                                                     house_single)

                price_items = ROOM_TYPE_FURNISHING_PRICE['diningRooms'][price_level]
                # print("\t餐厅 家具/电器 价格")
                for item_name in price_items:
                    price_info[price_level]['furniture']['diningRooms'][item_name] += method_compute("diningRooms",
                                                                                                     item_name,
                                                                                                     price_items[
                                                                                                         item_name],
                                                                                                     area_single,
                                                                                                     area_wall_line_single,
                                                                                                     house_single)

            elif room_type in ['DiningRoom']:
                price_items = ROOM_TYPE_FURNISHING_PRICE['diningRooms'][price_level]
                # print("餐厅 %s 家具/电器 价格" % text_area)
                for item_name in price_items:
                    price_info[price_level]['furniture']['diningRooms'][item_name] += method_compute("diningRooms",
                                                                                                     item_name,
                                                                                                     price_items[
                                                                                                         item_name],
                                                                                                     area_single,
                                                                                                     area_wall_line_single,
                                                                                                     house_single)

            elif room_type in ['Bedroom', 'MasterBedroom', 'SecondBedroom', 'KidsRoom', 'ElderRoom']:
                price_items = ROOM_TYPE_FURNISHING_PRICE['bedrooms'][price_level]
                # print("卧室 %s 家具/电器 价格" % text_area)
                for item_name in price_items:
                    price_info[price_level]['furniture']['bedrooms'][item_name] += method_compute("bedrooms",
                                                                                                  item_name,
                                                                                                  price_items[
                                                                                                      item_name],
                                                                                                  area_single,
                                                                                                  area_wall_line_single,
                                                                                                  house_single)

            elif room_type in ['Kitchen']:
                price_items = ROOM_TYPE_FURNISHING_PRICE['kitchens'][price_level]
                # print("厨房 %s 家具/电器 价格")
                for item_name in price_items:
                    price_info[price_level]['furniture']['kitchens'][item_name] += method_compute("kitchens",
                                                                                                  item_name,
                                                                                                  price_items[
                                                                                                      item_name],
                                                                                                  area_single,
                                                                                                  area_wall_line_single,
                                                                                                  house_single)

            elif room_type in ['Bathroom', 'MasterBathroom', 'SecondBathroom']:
                price_items = ROOM_TYPE_FURNISHING_PRICE['bathrooms'][price_level]
                # 均按房间个数处理
                # print("卫生间 %s 家具/电器 价格" % text_area)
                for item_name in price_items:
                    price_info[price_level]['furniture']['bathrooms'][item_name] += method_compute("bathrooms",
                                                                                                   item_name,
                                                                                                   price_items[
                                                                                                       item_name],
                                                                                                   area_single,
                                                                                                   area_wall_line_single,
                                                                                                   house_single)

            elif room_type in ['Balcony']:
                price_items = ROOM_TYPE_FURNISHING_PRICE['balconies'][price_level]
                # print("阳台 %s 家具/电器 价格" % text_area)
                for item_name in price_items:
                    price_info[price_level]['furniture']['balconies'][item_name] += method_compute("balconies",
                                                                                                   item_name,
                                                                                                   price_items[
                                                                                                       item_name],
                                                                                                   area_single,
                                                                                                   area_wall_line_single,
                                                                                                   house_single)
        areas = house_area
        # 计算总价
        price_total = 0.0
        for price_type in price_info[price_level]:
            if price_type == 'total':
                continue
            price_type_total = 0.0
            for rooms_type in price_info[price_level][price_type]:
                room_type_price = 0.0
                for item in price_info[price_level][price_type][rooms_type]:
                    price_info[price_level][price_type][rooms_type][item] = round(
                        price_info[price_level][price_type][rooms_type][item], 1)
                    price_type_total += round(price_info[price_level][price_type][rooms_type][item], 1)
                    room_type_price += round(price_info[price_level][price_type][rooms_type][item], 1)

                price_info[price_level][price_type][rooms_type]['total'] = round(room_type_price, 1)

            price_info[price_level][price_type]['total'] = round(price_type_total, 1)

            price_total += round(price_type_total, 1)

        price_info[price_level]['total'] = round(price_total, 1)
        house_total_price[price_level] += round(price_total, 1)

    # # 额外person费用
    for price_level in house_total_price:
        addition_price = 0.0
        for item_name in addition_human_price[price_level]:
            if item_name == 'total':
                continue
            price_info[price_level]['person']['others'][item_name] = round(addition_human_price[price_level][item_name][
                                                                               "price"], 1)
            addition_price += round(addition_human_price[price_level][item_name]["price"], 1)
        price_info[price_level]['person']['others']["total"] = round(addition_price, 1)
        price_info[price_level]['person']['total'] += round(addition_price, 1)
        price_info[price_level]['total'] += round(addition_price, 1)
    price_info['area'] = areas
    house_data['price_info'] = price_info

    # print(price_info)
    # house_data['price_info_total'] = {'house_total_price': house_total_price}
    return house_data


if __name__ == '__main__':
    # from House.house_sample import *
    #
    # a = time.time()
    # design_json_url = ""
    #
    # _, house_data = parse_design_data("", design_json_url)
    # correct_house_data(house_data)
    # house_info = get_house_price_info(house_data)
    #
    # with open("test_house_data.json", "w") as f:
    #     f.write(json.dumps(house_info, indent=4))
    # print(time.time() - a)
    house_data = construct_house_without_floorplan(1., room_nums=[3,1,1,1,1])
    price = get_house_price_info(house_data)['price_info']
    # price.pop('area')
    print(house_data)
