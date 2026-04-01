# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-10
@Description: 家具打组

"""

import math
from Furniture.furniture import *
from Furniture.furniture_refer import *
from Furniture.furniture_group_comp import *

# 家具组合
FURNITURE_GROUP_DICT = {}
FURNITURE_GROUP_FINE = {}

# 功能区域规则
GROUP_RULE_FUNCTIONAL = {
    'Meeting': {
        'room': ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library', 'Balcony', 'Terrace'],
        'list':
            {
                'sofa': ['sofa/ multi seat sofa', 'sofa/double seat sofa', 'sofa/single seat sofa',
                         'sofa/left corner sofa', 'sofa/right corner sofa', 'sofa/type L sofa', 'sofa/type U sofa',
                         'sofa/lounge chair',
                         'sofa/sofa set', 'sofa/sofa bed'
                         ],
                'table': ['table/coffee table - rectangular', 'table/coffee table - irregular shape',
                          'table/coffee table - round'],
                'side sofa': ['sofa/single seat sofa', 'sofa/double seat sofa',
                              'sofa/lounge chair', 'sofa/ottoman', 'sofa/corner',
                              'chair/armchair', 'chair/chair'
                              ],
                'side table': ['table/side table', 'table/night table', 'storage unit/dresser'],
                'rug': ['rug/rug'],
                'accessory': ['accessory/accessory - on top of others', 'accessory/pillow',
                              'plants/plants - on top of others',
                              'lighting/desk lamp', 'lighting/pendant light', 'lighting/wall lamp',
                              'appliance/appliance - on top of others',
                              'mirror/floor-based mirror',
                              '300 - on top of others']
            },
        'main': 'sofa',
        'plat': ['table', 'side table', 'sofa', 'side sofa'],
        'range': {
            'table': [[-1.50, 1.50], [-0.10, 0.10], [0.00, 2.00]],
            'side sofa': [[-2.50, 2.50], [-0.10, 0.10], [0.00, 2.50]],
            'side table': [[-2.50, 2.50], [-0.10, 0.10], [-2.00, 2.00]],
            'rug': [[-1.00, 1.00], [-0.10, 0.10], [-1.00, 2.00]]
        },
        'size': {
            'sofa': [[0.80, 8.00], [0.00, 5.00], [0.40, 5.00]],
            'table': [[0.40, 5.00], [0.00, 1.50], [0.40, 5.00]],
            'side sofa': [[0.00, 3.00], [0.00, 1.50], [0.00, 2.00]],
            'side table': [[0.00, 1.00], [0.00, 1.50], [0.00, 1.00]]
        },
        'count': {
            'table': [0, 2],
            'side table': [0, 4],
            'rug': [0, 1]
        },
        'alias': '会客',
        'sequence': ['sofa', 'table', 'side sofa', 'side table', 'rug', 'accessory'],
    },
    'Dining': {
        'room': ['LivingDiningRoom', 'LivingRoom', 'DiningRoom'],
        'list':
            {
                'table': ['table/dining table', 'table/dining table - round', 'table/dining table - square',
                          'table/table', 'table/dining set', 'table/dinning set'],
                'chair': ['chair/chair', 'chair/armchair', 'chair/bar chair',
                          'sofa/ottoman', 'sofa/ multi seat sofa'],
                'accessory': ['accessory/accessory - on top of others', 'accessory/kitchen decoration-horizontal',
                              'plants/plants - on top of others',
                              'appliance/appliance - on top of others',
                              '300 - on top of others']
            },
        'main': 'table',
        'main_style': 'chair',
        'plat': ['table'],
        'range': {
            'chair': [[-3.00, 3.00], [-0.10, 0.10], [-2.00, 2.00]],
        },
        'size': {
            'table': [[0.40, 5.00], [0.50, 5.00], [0.40, 5.00]],
        },
        'count': {
            'table': [1, 1]
        },
        'alias': '就餐',
        'sequence': ['table', 'chair', 'accessory'],
    },
    'Bed': {
        'room': ['MasterBedroom', 'SecondBedroom', 'Bedroom',
                 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                 'Library', 'OtherRoom'],
        'list':
            {
                'bed': ['bed/king-size bed', 'bed/queen-size bed', 'bed/single bed', 'bed/crib',
                        'bed/bed set'],
                'side table': ['table/night table', 'table/side table',
                               'table/coffee table - rectangular',
                               'cabinet/floor-based cabinet', 'storage unit/floor-based storage unit'],
                'table': ['sofa/ottoman', 'sofa/single seat sofa', 'sofa/lounge chair'],
                'rug': ['rug/rug'],
                'accessory': ['accessory/accessory - on top of others', 'accessory/bedding', 'accessory/pillow',
                              'plants/plants - on top of others',
                              'lighting/desk lamp', 'lighting/pendant light', 'lighting/wall lamp',
                              'mirror/floor-based mirror', 'cabinet/floor-based cabinet',
                              '300 - on top of others']
            },
        'main': 'bed',
        'plat': ['bed', 'side table', 'table'],
        'range': {
            'table': [[-1.00, 1.00], [-0.10, 0.10], [0.00, 2.00]],
            'side table': [[-2.50, 2.50], [-0.10, 0.10], [-2.00, 1.00]],
            'rug': [[-1.00, 1.00], [-0.10, 0.10], [-1.00, 2.00]]
        },
        'size': {
            'table': [[0.00, 3.00], [0.00, 1.00], [0.00, 1.50]],
            'side table': [[0.00, 1.00], [0.00, 1.30], [0.00, 1.00]]
        },
        'count': {
            'side table': [0, 2],
            'table': [0, 1],
            'rug': [0, 1]
        },
        'alias': '睡眠',
        'sequence': ['bed', 'side table', 'table', 'rug', 'accessory'],
    },
    'Media': {
        'room': ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                 'MasterBedroom', 'SecondBedroom', 'Bedroom',
                 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                 'Library'],
        'list':
            {
                'tv': ['electronics/TV - wall-attached', 'electronics/TV - on top of others'],
                'table': ['media unit/floor-based media unit', 'media unit/wall-attached media unit',
                          'cabinet/floor-based cabinet', 'cabinet/hutch&buffet', 'cabinet/wall-attached cabinet',
                          'storage unit/floor-based storage unit', 'storage unit/dresser',
                          'build element/background wall'],
                'side table': ['table/side table', 'table/night table',
                               'cabinet/floor-based cabinet', 'cabinet/hutch&buffet',
                               'shelf/book shelf', 'shelf/decorative shelf'],
                'accessory': ['accessory/accessory - on top of others', 'accessory/accessory - floor-based',
                              'plants/plants - on top of others',
                              'appliance/appliance - on top of others', 'appliance/appliance - floor-based',
                              'art/art - wall-attached', 'recreation/musical instrument',
                              '300 - on top of others']
            },
        'main': 'tv',
        'main_style': 'table',
        'plat': ['table', 'side table'],
        'range': {
            'table': [[-1.00, 1.00], [-0.10, 0.10], [-0.50, 0.50]],
            'side table': [[-2.00, 2.00], [-0.10, 0.10], [-0.50, 0.50]]
        },
        'size': {
            'table': [[0.60, 5.00], [0.00, 3.00], [0.00, 1.00]],
            'side table': [[0.00, 1.00], [0.00, 3.00], [0.00, 1.00]]
        },
        'count': {
            'tv': [1, 1],
            'side table': [0, 2],
        },
        'alias': '视听',
        'sequence': ['tv', 'table', 'side table', 'accessory'],
    },
    'Armoire': {
        'room': ['MasterBedroom', 'SecondBedroom', 'Bedroom',
                 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                 'Library'],
        'list':
            {
                'armoire': ['storage unit/armoire', 'storage unit/armoire - L shaped',
                            'wardrobe/base wardrobe', 'wardrobe/top wardrobe'],
                'accessory': ['accessory/accessory - on top of others', 'accessory/clothes',
                              'accessory/accessory - floor-based', '300 - on top of others']
            },
        'main': 'armoire',
        'plat': ['armoire'],
        'range': {},
        'size': {
            'armoire': [[0.20, 5.00], [0.70, 5.00], [0.20, 5.00]]
        },
        'alias': '衣柜',
        'sequence': ['armoire', 'accessory'],
    },
    'Cabinet': {
        'room': ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                 'MasterBedroom', 'SecondBedroom', 'Bedroom',
                 'KidsRoom', 'ElderlyRoom', 'NannyRoom', 'Library',
                 'Bathroom', 'MasterBathroom', 'SecondBathroom',
                 'Balcony', 'Terrace', 'Lounge', 'LaundryRoom',
                 'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                 'StorageRoom', 'CloakRoom', 'EquipmentRoom', 'Auditorium', 'OtherRoom'
                 ],
        'list':
            {
                'cabinet': ['cabinet/floor-based cabinet', 'cabinet/bookcase - L shaped', 'cabinet/hutch&buffet',
                            'cabinet/wall-attached cabinet',
                            'basin/single basin - on top of others',
                            'basin/floor-based single basin with cabinet',
                            'basin/floor-based double basin with cabinet',
                            'storage unit/dresser', 'storage unit/floor-based storage unit',
                            'wardrobe/base wardrobe',
                            'shelf/book shelf', 'shelf/decorative shelf',
                            'kitchen cabinet/base cabinet', 'kitchen cabinet/wall cabinet',
                            'customized content/customized platform',
                            'customized content/customized personalized model',
                            'customized content/customized furniture', 'customized content/customized fixed furniture'
                            ],
                'accessory': ['accessory/accessory - on top of others', 'accessory/clothes',
                              'accessory/accessory - floor-based', 'accessory/kitchen decoration-horizontal',
                              'plants/plants - on top of others',
                              'lighting/desk lamp', 'recreation/musical instrument', 'electronics/computer',
                              'appliance/appliance - on top of others', 'appliance/range & cooktop',
                              'art/art - wall-attached', 'mirror/wall-attached mirror',
                              'attachment/taps', 'sink/drop-in single kitchen sink',
                              '300 - on top of others']
            },
        'main': 'cabinet',
        'plat': ['cabinet'],
        'range': {},
        'size': {
            'cabinet': [[0.20, 5.00], [0.20, 5.00], [0.20, 1.50]]
        },
        'alias': '储物',
        'sequence': ['cabinet', 'accessory'],
    },
    'Appliance': {
        'room': ['LivingDiningRoom', 'LivingRoom', 'DiningRoom',
                 'Kitchen',
                 'Bathroom', 'MasterBathroom', 'SecondBathroom',
                 'Balcony', 'Terrace', 'Lounge', 'LaundryRoom'
                 ],
        'list':
            {
                'appliance': ['appliance/washer', 'appliance/refrigerator',
                              'electronics/air-conditioner - floor-based'],
                'accessory': ['accessory/accessory - on top of others', 'accessory/kitchen decoration-horizontal',
                              'plants/plants - on top of others', 'shelf/decorative shelf']
            },
        'main': 'appliance',
        'plat': ['appliance'],
        'range': {},
        'alias': '电器',
        'sequence': ['appliance', 'accessory'],
    },
    'Work': {
        'room': ['MasterBedroom', 'SecondBedroom', 'Bedroom',
                 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                 'Library', 'Balcony', 'Terrace', 'OtherRoom'],
        'list':
            {
                'table': ['table/table', 'table/console table', 'table/dresser', 'recreation/musical instrument'],
                'chair': ['chair/chair', 'chair/armchair', 'chair/bar chair', 'stool/stool',
                          'sofa/single seat sofa', 'sofa/ottoman'],
                'rug': ['rug/rug'],
                'accessory': ['accessory/accessory - on top of others', 'plants/plants - on top of others',
                              'lighting/desk lamp', 'electronics/computer', 'table/side table',
                              'art/art - wall-attached', 'mirror/wall-attached mirror',
                              'accessory/accessory - floor-based', '300 - on top of others']
            },
        'main': 'table',
        'plat': ['table'],
        'range': {
            'chair': [[-1.00, 1.00], [-0.10, 0.10], [-2.00, 2.00]],
            'rug': [[-1.00, 1.00], [-0.10, 0.10], [-1.00, 1.00]]
        },
        'size': {
            'table': [[0.40, 5.00], [0.40, 5.00], [0.30, 5.00]]
        },
        'count': {
            'chair': [0, 3]
        },
        'alias': '办公',
        'sequence': ['table', 'chair', 'rug', 'accessory'],
    },
    'Rest': {
        'room': ['Library', 'Balcony', 'Terrace',
                 'MasterBedroom', 'SecondBedroom', 'Bedroom',
                 'KidsRoom', 'ElderlyRoom', 'NannyRoom',
                 'Hallway', 'Aisle', 'Corridor',
                 'LaundryRoom', 'Auditorium'],
        'list':
            {
                'table': ['table/coffee table - rectangular', 'table/coffee table - round',
                          'table/coffee table - irregular shape', 'coffee table - round',
                          'table/side table', 'table/night table', 'table/console table', 'table/dresser',
                          'outdoor furniture/outdoor furniture - floor-based', 'outdoor furniture/playground equipment',
                          'lighting/floor lamp', 'stool/stool'],
                'chair': ['chair/chair', 'chair/armchair', 'chair/bar chair', 'stool/stool',
                          'sofa/single seat sofa', 'sofa/lounge chair', 'sofa/ottoman', 'sofa/corner',
                          'outdoor furniture/outdoor furniture - floor-based'],
                'rug': ['rug/rug'],
                'accessory': ['accessory/accessory - on top of others', 'plants/plants - on top of others',
                              'art/art - wall-attached', 'mirror/wall-attached mirror',
                              'accessory/accessory - floor-based', '300 - on top of others']
            },
        'main': 'table',
        'main_style': 'table',
        'plat': ['table'],
        'range': {
            'chair': [[-2.00, 2.00], [-0.10, 0.10], [-2.00, 2.00]],
            'rug': [[-1.00, 1.00], [-0.10, 0.10], [-1.00, 1.00]]
        },
        'size': {
            'table': [[0.30, 5.00], [0.20, 2.00], [0.30, 1.50]],
            'table/side table': [[1.20, 5.00], [0.20, 2.00], [1.20, 1.50]],
            'table/night table': [[1.20, 5.00], [0.20, 2.00], [1.20, 1.50]],
            'chair': [[0.20, 2.00], [0.20, 2.00], [0.20, 2.00]],
        },
        'count': {
            'table': [1, 1]
        },
        'alias': '休闲',
        'sequence': ['table', 'chair', 'rug', 'accessory'],
    },
    'Bath': {
        'room': ['Bathroom', 'MasterBathroom', 'SecondBathroom', 'MasterBedroom', 'SecondBedroom', 'Bedroom'],
        'list':
            {
                'shower': ['shower/wall-attached shower head'],
                'bath': ['bath/freestanding bath'],
                'screen': ['shower/shower screen', 'shower/floor based shower room'],
                'accessory': ['accessory/accessory - on top of others', 'plants/plants - on top of others',
                              'accessory/bathroom accessory - on top of others',
                              'accessory/kitchen decoration-horizontal',
                              'electronics/computer', 'attachment']
            },
        'main': 'shower',
        'main_style': 'shower',
        'plat': ['shower', 'bath'],
        'range': {
            'bath': [[-1.00, 1.00], [-0.10, 0.10], [-1.00, 1.00]],
            'screen': [[-1.50, 1.50], [-0.10, 0.10], [-1.50, 1.50]]
        },
        'count': {
            'bath': [0, 1]
        },
        'alias': '卫浴',
        'sequence': ['shower', 'bath', 'screen', 'accessory']
    },
    'Toilet': {
        'room': ['Bathroom', 'MasterBathroom', 'SecondBathroom', 'MasterBedroom', 'SecondBedroom', 'Bedroom'],
        'list':
            {
                'toilet': ['toilet/floor-based toilet', 'toilet/wall-attached toilet'],
                'accessory': ['accessory/accessory - on top of others', 'plants/plants - on top of others',
                              'accessory/kitchen decoration-horizontal']
            },
        'main': 'toilet',
        'main_style': 'toilet',
        'plat': ['toilet'],
        'range': {},
        'count': {
            'toilet': [1, 1]
        },
        'size': {
            'toilet': [[0.20, 2.00], [0.20, 2.00], [0.20, 2.00]]
        },
        'alias': '马桶',
        'sequence': ['toilet', 'accessory']
    }
}
# 装饰区域规则
GROUP_RULE_DECORATIVE = {
    'Wall': ['art/art - wall-attached', 'mirror/wall-attached mirror', 'accessory/accessory - wall-attached',
             'accessory/clock - wall-attached', 'accessory/bathroom accessory - wall-attached', 'attachment/taps',
             'lighting/wall lamp', 'appliance/appliance - wall-attached', 'toilet/wall-attached toilet',
             'cabinet/wall-attached cabinet', 'storage unit/wall-attached storage unit', 'cabinet/floor-based cabinet',
             'shelf/decorative shelf'],
    'Ceiling': ['lighting/ceiling light', 'lighting/pendant light', 'lighting/chandelier',
                'lighting/track-mounted spotlight- ceiling-attached'],
    'Floor': ['plants/plants - floor-based', 'plants/plants - on top of others', 'art/art - wall-attached',
              'cabinet/floor-based cabinet', 'storage unit/floor-based storage unit', 'shelf/decorative shelf',
              'table/side table', 'sofa/ottoman', 'lighting/floor lamp', 'electronics/air-conditioner - floor-based',
              'accessory/accessory - on top of others', 'accessory/accessory - floor-based', 'accessory/clothes',
              'accessory/bathroom accessory - floor-based', 'accessory/kitchen decoration-horizontal',
              'recreation/musical instrument', 'rug/rug'],
    'Door': ['door/single swing door', 'door/double sliding door', 'door/triple sliding door',
             'door/entry/single swing door',
             'door/entry/double swing door - asymmetrical', 'door/entry/double swing door - symmetrical',
             'barn door/barn door'],
    'Window': ['window/window', 'window/bay window', 'window/floor-based window',
               'parametric corner window', 'param window/bay window',
               'curtain/curtain', 'curtain/single curtain', 'accessory/simulated curtain'],
    'Background': ['build element/background wall', 'build element/column'],
    'Customize': []
}
# 功能区域成对
GROUP_PAIR_FUNCTIONAL = {
    'Meeting': ['Media'],
    'Bed': ['Media']
}
# 装饰区域平台
GROUP_PLAT_WALL = ['appliance/appliance - wall-attached',
                   'cabinet/wall-attached cabinet', 'storage unit/wall-attached storage unit',
                   'cabinet/floor-based cabinet']
# 功能角色名称
GROUP_ROLE_NAME = {
    'Meeting sofa': '沙发', 'Meeting table': '茶几', 'Meeting side sofa': '边椅', 'Meeting side table': '边几', 'Meeting rug': '地毯',
    'Dining table': '餐桌', 'Dining chair': '餐椅', 'Dining cabinet': '餐边柜',
    'Bed bed': '床', 'Bed table': '床前几', 'Bed side table': '床头柜', 'Bed rug': '地毯',
    'Media table': '电视柜', 'Media tv': '电视',
    'Library Work table': '办公桌', 'Library Work table': '办公椅', 'Library Work rug': '地毯',
    'Bedroom Work table': '梳妆桌', 'Bedroom Work table': '梳妆椅', 'Bedroom Work rug': '地毯',
    'Rest table': '休闲桌', 'Rest chair': '休闲椅',
    'Hallway cabinet': '玄关柜',
    'CloakRoom cabinet': '衣柜', 'CloakRoom armoire': '衣柜',
}

# 组合家具
GROUP_FURNITURE_LIST = {}
for group_name, group_rule in GROUP_RULE_FUNCTIONAL.items():
    for obj_role, obj_list in group_rule['list'].items():
        for obj_type in obj_list:
            GROUP_FURNITURE_LIST[obj_type] = 1
for group_name, group_rule in GROUP_RULE_DECORATIVE.items():
    for obj_type in group_rule:
        GROUP_FURNITURE_LIST[obj_type] = 1
# 启动家具
GROUP_SEED_LIST = ['sofa/ multi seat sofa', 'sofa/double seat sofa',
                   'sofa/right corner sofa', 'sofa/left corner sofa', 'sofa/type L sofa', 'sofa/type U sofa',
                   'sofa/lounge chair',
                   'sofa/sofa set',
                   'table/dining table', 'table/dining table - round', 'table/dining table - square',
                   'table/dining set', 'table/dinning set',
                   'table/coffee table - round', 'table/coffee table - rectangular',
                   'table/table', 'table/console table', 'table/side table',
                   'bed/king-size bed', 'bed/queen-size bed', 'bed/single bed', 'bed/crib',
                   'bed/bed set',
                   'media unit/floor-based media unit', 'media unit/wall-attached media unit',
                   'storage unit/armoire', 'storage unit/armoire - L shaped',
                   'storage unit/dresser', 'storage unit/floor-based storage unit',
                   'cabinet/floor-based cabinet', 'cabinet/bookcase - L shaped', 'cabinet/hutch&buffet',
                   'shelf/book shelf',
                   'shower/wall-attached shower head', 'toilet/floor-based toilet', 'toilet/wall-attached toilet',
                   'basin/floor-based single basin with cabinet'
                   ]
GROUP_MESH_DICT = {
    'background': [
        'build element/background wall',
        'customized content/customized feature wall', 'customized feature wall', 'CustomizedFeatureWall',
        'extrusion customized background wall'
    ],
    'ceiling': [
        'build element/ceiling molding', 'build element/gypsum ceiling',
        'build element/kitchen ceiling', 'build element/3d kitchen ceiling',
        'customized content/customized ceiling', 'customized content/smart customized ceiling',
        'extrusion customized ceiling model', 'CustomizedCeiling'
    ],
    'cabinet': [
        'customized content/customized platform', 'customized content/customized personalized model',
        'customized content/customized furniture', 'customized content/customized fixed furniture',
        'kitchen cabinet/base cabinet', 'kitchen cabinet/wall cabinet',
        'kitchen cabinet/cbnt door', 'sink/drop-in single kitchen sink', 'appliance/range & cooktop',
        'build element/column - DIY - square', 'build element/column - DIY - round',
        'build element/beam', 'build element/column', 'obstacle/flue - square'
    ]
}
GROUP_MESH_LIST = []
GROUP_MESH_SOFT = ['wardrobe/base wardrobe', 'appliance/range & cooktop', 'sink/drop-in single kitchen sink']
for mesh_role, type_list in GROUP_MESH_DICT.items():
    for type_one in type_list:
        GROUP_MESH_LIST.append(type_one)

# 拐角沙发
SOFA_CORNER_TYPE_0 = ['sofa/left corner sofa', 'sofa/right corner sofa',
                      'sofa/type L sofa', 'sofa/type U sofa', 'sofa/sofa set']
SOFA_CORNER_TYPE_1 = ['sofa/left corner sofa', 'sofa/right corner sofa']
SOFA_CORNER_TYPE_2 = ['sofa/type L sofa', 'sofa/type U sofa', 'sofa/sofa set']
# 特定餐桌
TABLE_ROUND_TYPE_0 = ['table/dining table - round']
# 组合家具
PACK_OBJECT_TYPE_0 = ['sofa/sofa set', 'table/dining set', 'table/dinning set', 'bed/bed set']
# 装饰物品
DECO_OBJECT_TYPE_0 = ['accessory/accessory - on top of others', 'plants/plants - on top of others',
                      'accessory/accessory - wall-attached', 'art/art - wall-attached',
                      'accessory/kitchen decoration-horizontal', '']
LAST_OBJECT_TYPE_0 = ['lighting/ceiling light', 'lighting/chandelier',
                      'door/single swing door', 'door/double sliding door', 'door/single swing door',
                      'door/entry/single swing door', 'door/entry/double swing door - asymmetrical',
                      'window/window', 'window/floor-based window', 'curtain/curtain',
                      'build element/column']
LINK_OBJECT_DICT_0 = {
    'sofa': {
        'depth': 2.0,
        'type': ''
    }
}
RELY_OBJECT_DICT_0 = {
    'accessory/pillow': ['sofa/single seat sofa', 'sofa/double seat sofa', 'sofa/ multi seat sofa'],
    'electronics/TV - on top of others': ['media unit/floor-based media unit'],
    'electronics/TV - wall-attached': ['media unit/floor-based media unit'],
    'sink/drop-in single kitchen sink': ['cabinet/floor-based cabinet'],
    'appliance/range & cooktop': ['cabinet/floor-based cabinet']
}
# 忽略物品
DUMP_OBJECT_TYPE_0 = ['lighting/downlight', 'lighting/single spotlight - ceiling-attached',
                      'build element/air-conditioning vent', 'build element/ceiling decoration', 'build element/jiaohua',
                      'appliance/bathroom heater with light', 'appliance/room heater',
                      'electric/switch - single switch', 'electric/switch - tandem switch',
                      'electric/switch - triple switch', 'electric/switch - waterproof switch',
                      'electric/socket weak - telephone jack+network', 'electric/socket weak - tv cable',
                      'electric/socket strong - five-hole socket',
                      'electric/socket strong - five-hole socket (with switch )',
                      'water/water supply', 'water/cold water', 'water/hot water',
                      '']
DUMP_OBJECT_DICT_0 = {
    'c6dbfb0c-2499-4e42-83d2-dea6e403aaed': 1,
    'bad82d21-887d-4a79-a801-e9133bedae34': 1,
    '08ba345f-e2ff-4eb0-83b2-0437890c7a39': 1  # 窗帘渲染错误
}
# 特定物品
TABLE_CLOTH_ID = '57a71438-ebf3-4f72-8820-f8b686ae75c8'
CHAIR_CLOTH_ID = '1832bc28-0979-401d-a25e-7a49b854694a'
MEDIA_PLAT_ID = '73b9f552-7f5c-406d-a62d-7627482383cc'
MEDIA_WALL_ID = 'e5e6d90f-58c5-4293-8dc0-0a701af93bd5'
SCREEN_I_ID = '004aca6b-d74e-485a-9c99-4b55762ab080'
SCREEN_L_ID = '00e154da-8a16-41b4-a9ba-de7c1874245a'
SCREEN_R_ID = '114b34e5-0984-432e-a052-96fabb7deb75'
SCREEN_U_ID = '302fd336-6222-426e-8b6f-2d962d8cc9ad'
SCREEN_V_ID = '116a426e-f14b-4ca3-9588-75632b4bdbed'
# 家具尺寸
UNIT_WIDTH_DOOR = 0.85
UNIT_WIDTH_SOFA_SINGLE = 1.50
UNIT_WIDTH_SHELF_MIN1 = 0.40
UNIT_WIDTH_SHELF_MIN2 = 0.50
UNIT_DEPTH_SHELF_MIN = 0.20
UNIT_HEIGHT_SHELF_MIN = 1.50
UNIT_HEIGHT_TABLE_MAX = 1.00
UNIT_HEIGHT_CLOTH_MAX = 0.01
UNIT_HEIGHT_OBJECT = 2.80

# 房间级别
ROOM_TYPE_LEVEL_1 = ['LivingDiningRoom', 'LivingRoom', 'DiningRoom', 'Library']
ROOM_TYPE_LEVEL_2 = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom']
ROOM_TYPE_LEVEL_3 = ['MasterBathroom', 'SecondBathroom', 'Bathroom',
                     'Balcony', 'Terrace', 'Lounge', 'LaundryRoom',
                     'Hallway', 'Aisle', 'Corridor', 'Stairwell',
                     'StorageRoom', 'CloakRoom', 'EquipmentRoom']
ROOM_TYPE_LEVEL_4 = ['Hallway', 'Aisle', 'Corridor', 'Stairwell',
                     'StorageRoom', 'CloakRoom', 'EquipmentRoom']
# 组合关联
GROUP_TYPE_RELATE = ['Meeting', 'Bed', 'Media', 'Dining', 'Work', 'Rest', 'Cabinet', 'Bath', 'Toilet']
# 角色更新
GROUP_ROLE_UPDATE = {
    '8e9c139b-c76a-4e29-bc73-95ed3e99d39e': ['Meeting', 'table'],
    '8f976494-047a-4010-85d0-7ff90f706b37': ['Cabinet', 'car']
}


# 数据解析：加载组合数据
def load_furniture_group(reload=False):
    # 默认组合
    global FURNITURE_GROUP_DICT
    if len(FURNITURE_GROUP_DICT) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_group_dict.json')
        FURNITURE_GROUP_DICT = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_GROUP_DICT = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    # 补充组合
    global FURNITURE_GROUP_FINE
    if len(FURNITURE_GROUP_FINE) <= 0 or reload:
        json_path = os.path.join(os.path.dirname(__file__), 'furniture_group_fine.json')
        FURNITURE_GROUP_FINE = {}
        if os.path.exists(json_path):
            try:
                FURNITURE_GROUP_FINE = json.load(open(json_path, 'r'))
            except Exception as e:
                print(e)
    return FURNITURE_GROUP_DICT


# 数据解析：保存打组数据
def save_furniture_group():
    # 默认组合
    global FURNITURE_GROUP_DICT
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_group_dict.json')
    with open(json_path, 'w') as f:
        json.dump(FURNITURE_GROUP_DICT, f, indent=4)
        f.close()
    # 打印信息
    print('save furniture group success')


# 数据解析：保存打组数据
def save_furniture_group_fine():
    # 补充组合
    global FURNITURE_GROUP_FINE
    json_path = os.path.join(os.path.dirname(__file__), 'furniture_group_fine.json')
    with open(json_path, 'w') as f:
        json.dump(FURNITURE_GROUP_FINE, f, indent=4)
        f.close()
    # 打印信息
    print('save furniture group fine success')


# 数据解析：清空打组数据
def clear_furniture_group():
    # 默认组合
    global FURNITURE_GROUP_DICT
    FURNITURE_GROUP_DICT.clear()
    # 打印信息
    print('clear furniture group success')
    save_furniture_group()


# 数据解析：清空打组数据
def clear_furniture_group_fine():
    # 补充组合
    global FURNITURE_GROUP_FINE
    FURNITURE_GROUP_FINE.clear()
    # 打印信息
    print('clear furniture group fine success')
    save_furniture_group_fine()


# 数据解析：增加打组数据
def add_furniture_group(house_id, room_id, group_info, fine_flag=False):
    if 'obj_list' not in group_info:
        return
    # 加载组合
    global FURNITURE_GROUP_DICT
    global FURNITURE_GROUP_FINE
    load_furniture_group()

    # 判断分类
    group_dict = {}
    if fine_flag:
        group_dict = FURNITURE_GROUP_FINE
    else:
        group_dict = FURNITURE_GROUP_DICT

    # 添加房间
    if house_id not in group_dict:
        group_dict[house_id] = {}
    if room_id not in group_dict[house_id]:
        group_dict[house_id][room_id] = []
    # 添加组合
    type_new, size_new, main_new = group_info['type'], group_info['size'], group_info['obj_main']
    find_idx = -1
    for group_idx, group_one in enumerate(group_dict[house_id][room_id]):
        type_old = group_one['type']
        size_old = group_one['size']
        main_old = group_one['obj_main']
        if type_new == type_old and main_new == main_old:
            if abs(size_new[0] - size_old[0]) < 0.01 and abs(size_new[2] - size_old[2]) < 0.01:
                find_idx = group_idx
                break
            elif type_new in ['Meeting', 'Dining', 'Media', 'Bed']:
                find_idx = group_idx
                break
    group_copy = group_info.copy()
    group_copy['obj_list'] = []
    for obj_one in group_info['obj_list']:
        group_copy['obj_list'].append(obj_one)
    if find_idx <= -1:
        group_dict[house_id][room_id].append(group_copy)
    else:
        group_dict[house_id][room_id][find_idx] = group_copy


# 数据解析：增加打组数据
def add_furniture_group_list(house_id, room_id, group_list, fine_flag=False):
    if len(group_list) <= 0:
        return
    # 加载组合
    global FURNITURE_GROUP_DICT
    global FURNITURE_GROUP_FINE
    load_furniture_group()

    # 判断分类
    group_dict = {}
    if fine_flag:
        group_dict = FURNITURE_GROUP_FINE
    else:
        group_dict = FURNITURE_GROUP_DICT
    # 添加房间
    if house_id not in group_dict:
        group_dict[house_id] = {}
    if room_id not in group_dict[house_id]:
        group_dict[house_id][room_id] = []
    # 更新分组
    group_dict[house_id][room_id] = group_list


# 数据解析：删除打组数据
def del_furniture_group(house_id, room_id, fine_flag=False):
    # 加载组合
    global FURNITURE_GROUP_DICT
    global FURNITURE_GROUP_FINE
    load_furniture_group()
    # 判断分类
    group_dict = {}
    if fine_flag:
        group_dict = FURNITURE_GROUP_FINE
    else:
        group_dict = FURNITURE_GROUP_DICT
    # 添加房间
    if house_id not in group_dict:
        return
    if room_id == '':
        group_dict[house_id] = {}
    if room_id not in group_dict[house_id]:
        return
    group_dict[house_id][room_id] = []


# 数据解析：获取打组数据
def get_furniture_group(house_id, room_id, group_type, group_main='', group_size=[], room_type='',
                        fine_flag=False):
    if house_id == '':
        return {}
    global FURNITURE_GROUP_DICT
    global FURNITURE_GROUP_FINE
    load_furniture_group()
    # 判断分类
    group_dict = {}
    if fine_flag:
        group_dict = FURNITURE_GROUP_FINE
    else:
        group_dict = FURNITURE_GROUP_DICT
    # 查找组合
    group_best = {}

    # 默认门窗
    door_list_back, window_list_back = [], []
    if group_type in ['Door']:
        door_list_back = get_furniture_list_by_rand('door')
    elif group_type in ['Window']:
        window_list_back = get_furniture_list_by_rand('window') + get_furniture_list_by_rand('curtain')
    if house_id not in group_dict:
        if group_type in ['Door']:
            group_best = {
                'type': group_type, 'style': 'Contemporary', 'code': 0, 'size': [1, 1, 1], 'obj_main': '',
                'obj_type': '', 'obj_list': door_list_back, 'mat_list': []
            }
        elif group_type in ['Window']:
            group_best = {
                'type': group_type, 'style': 'Contemporary', 'code': 0, 'size': [1, 1, 1], 'obj_main': '',
                'obj_type': '', 'obj_list': window_list_back, 'mat_list': []
            }
        return group_best

    # 全屋门窗
    door_list_side, window_list_side = [], []
    object_list_new, object_list_old = [], []
    if group_type in ['Door']:
        object_list_old = door_list_side
    elif group_type in ['Window']:
        object_list_old = window_list_side
    if group_type in ['Door', 'Window']:
        for room_name, group_list in group_dict[house_id].items():
            if room_name == room_id:
                continue
            if 'Bathroom' in room_id or 'Bathroom' in room_type:
                if 'Bathroom' not in room_name:
                    continue
            for group_one in group_list:
                if group_one['type'] == group_type:
                    object_list_new = group_one['obj_list']
                    break
            for object_new in object_list_new:
                if 'relate' in object_new and len(object_new['relate']) > 0:
                    continue
                size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                size_find = False
                for object_old in object_list_old:
                    if 'relate' in object_old and len(object_old['relate']) > 0:
                        continue
                    size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
                    if object_new['id'] == object_old['id'] and abs(size_new[0] - size_old[0]) < 0.3:
                        size_find = True
                        break
                    elif object_new['type'] == object_old['type'] and abs(size_new[0] - size_old[0]) < size_old[0] / 3:
                        size_find = True
                        break
                if not size_find:
                    object_list_old.append(object_new)
                    if 'fake_id' in object_new and object_new['fake_id'].startswith('link'):
                        origin_position = object_new['position']
                        for object_add in object_list_new:
                            if 'relate' in object_add and object_add['relate'] == object_new['id']:
                                if 'relate_position' in object_add and len(object_add['relate_position']) >= 3:
                                    relate_position = object_add['relate_position']
                                    offset_x = relate_position[0] - origin_position[0]
                                    offset_z = relate_position[2] - origin_position[2]
                                    if abs(offset_x) <= 0.1 and abs(offset_z) <= 0.1:
                                        object_list_old.append(object_add)
                    break

    # 查找组合
    door_list_best, window_list_best, curtain_link = [], [], {}
    if room_id in group_dict[house_id]:
        group_best = {}
        # group list
        group_list = group_dict[house_id][room_id]
        for group_one in group_list:
            if group_one['type'] == group_type:
                if group_one['type'] in GROUP_RULE_DECORATIVE:
                    group_best = copy_group(group_one)
                    break
                elif group_one['obj_main'] == group_main or group_main == '':
                    group_best = copy_group(group_one)
                    if len(group_size) <= 2:
                        return group_best
                    else:
                        group_diff = [abs(group_one['size'][i] - group_size[i]) for i in range(3)]
                        if max(group_diff[0], group_diff[2]) < 0.01:
                            return group_best
        if len(group_best) <= 0:
            for group_one in group_list:
                if group_one['type'] == group_type:
                    group_best = group_one
        # group wait
        group_wait = []
        if room_type in ['LivingDiningRoom']:
            for room_key, room_val in group_dict[house_id].items():
                if room_key == room_id:
                    continue
                elif 'LivingRoom' in room_key or 'DiningRoom' in room_key:
                    group_wait = room_val
                    break
        for group_one in group_wait:
            if group_one['type'] == group_type:
                if group_one['type'] in GROUP_RULE_DECORATIVE:
                    group_find = copy_group(group_one)
                    if 'obj_list' in group_best and 'obj_list' in group_find:
                        obj_list_old = group_best['obj_list']
                        obj_list_new = group_find['obj_list']
                        for obj_add in obj_list_new:
                            obj_list_old.append(obj_add)
                    break

        # group best
        if len(group_best) > 0:
            object_list_new, object_list_old = [], []
            if group_type in ['Door']:
                object_list_new = group_best['obj_list']
                object_list_old = door_list_best
            elif group_type in ['Window']:
                object_list_new = group_best['obj_list']
                object_list_old = window_list_best
            for object_new in object_list_new:
                if 'relate' in object_new and len(object_new['relate']) > 0:
                    continue
                object_key = object_new['id']
                if object_key in DUMP_OBJECT_DICT_0:
                    continue
                size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
                size_find = False
                for object_old in object_list_old:
                    if 'relate' in object_old and len(object_old['relate']) > 0:
                        continue
                    size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
                    if object_new['id'] == object_old['id'] and abs(size_new[0] - size_old[0]) < 0.3:
                        size_find = True
                        break
                    elif object_new['type'] == object_old['type'] and abs(size_new[0] - size_old[0]) < size_old[0] / 3:
                        size_find = True
                        break
                if not size_find:
                    object_list_old.append(object_new)
                    if 'fake_id' in object_new and object_new['fake_id'].startswith('link'):
                        origin_position = object_new['position']
                        for object_add in object_list_new:
                            if 'relate' in object_add and object_add['relate'] == object_new['id']:
                                if 'relate_position' in object_add and len(object_add['relate_position']) >= 3:
                                    relate_position = object_add['relate_position']
                                    offset_x = relate_position[0] - origin_position[0]
                                    offset_z = relate_position[2] - origin_position[2]
                                    if abs(offset_x) <= 0.1 and abs(offset_z) <= 0.1:
                                        object_list_old.append(object_add)

    # 补充门窗
    object_list_set, object_list_old = [], []
    if group_type in ['Door']:
        object_list_set = [door_list_side, door_list_back]
        object_list_old = door_list_best
    elif group_type in ['Window']:
        object_list_set = [window_list_side, window_list_back]
        object_list_old = window_list_best
    for object_list_new in object_list_set:
        for object_new in object_list_new:
            if 'relate' in object_new and len(object_new['relate']) > 0:
                continue
            size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
            size_find = False
            for object_old in object_list_old:
                if 'relate' in object_old and len(object_old['relate']) > 0:
                    continue
                size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
                if object_new['id'] == object_old['id'] and abs(size_new[0] - size_old[0]) < 0.3:
                    size_find = True
                    break
                elif object_new['type'] == object_old['type'] and 2.0 < size_old[0] < size_new[0] < 3.0:
                    size_find = True
                    break
                elif object_new['type'] == object_old['type'] and abs(size_new[0] - size_old[0]) < size_old[0] / 3:
                    size_find = True
                    break
                elif object_new['type'] == object_old['type'] and 'fake_id' in object_old and object_old['fake_id'].startswith('link'):
                    if size_new[0] > size_old[0] > 2 and abs(size_new[1] - size_old[1]) < 0.4:
                        size_find = True
                        break
            if not size_find:
                object_list_old.append(object_new)
                if 'fake_id' in object_new and object_new['fake_id'].startswith('link'):
                    origin_position = object_new['position']
                    for object_add in object_list_new:
                        if 'relate' in object_add and object_add['relate'] == object_new['id']:
                            if 'relate_position' in object_add and len(object_add['relate_position']) >= 3:
                                relate_position = object_add['relate_position']
                                offset_x = relate_position[0] - origin_position[0]
                                offset_z = relate_position[2] - origin_position[2]
                                if abs(offset_x) <= 0.1 and abs(offset_z) <= 0.1:
                                    object_list_old.append(object_add)
    if group_type in ['Door', 'Window'] and 'obj_list' in group_best:
        group_best['obj_list'] = object_list_old

    # 返回信息
    if len(group_best) <= 0:
        if group_type in GROUP_RULE_FUNCTIONAL:
            for room_id, group_list in FURNITURE_GROUP_DICT[house_id].items():
                for group_one in group_list:
                    if group_one['type'] == group_type:
                        if group_one['obj_main'] == group_main or group_main == '':
                            group_best = group_one
                            if len(group_size) <= 0:
                                return group_best
                            elif abs(group_one['size'][0] - group_size[0]) < 0.01:
                                return group_best
                if len(group_best) <= 0:
                    for group_one in group_list:
                        if group_one['type'] == group_type:
                            group_best = copy_group(group_one)
        elif group_type in GROUP_RULE_DECORATIVE:
            group_best = {
                'type': group_type, 'style': 'Contemporary', 'code': 0, 'size': [1, 1, 1], 'obj_main': '',
                'obj_type': '', 'obj_list': object_list_old, 'mat_list': []
            }
    return group_best


# 数据解析：获取打组数据
def get_furniture_group_list(house_id, room_id, type_list=[], fine_flag=False):
    group_list_new = []
    global FURNITURE_GROUP_DICT
    global FURNITURE_GROUP_FINE
    load_furniture_group()
    # 判断分类
    group_dict = {}
    if fine_flag:
        group_dict = FURNITURE_GROUP_FINE
    else:
        group_dict = FURNITURE_GROUP_DICT
    # 查找组合
    if house_id not in group_dict:
        return group_list_new
    if room_id not in group_dict[house_id]:
        return group_list_new
    group_list_old = group_dict[house_id][room_id]
    for group_one in group_list_old:
        if len(type_list) <= 0 or group_one['type'] in type_list:
            group_list_new.append(group_one)
    return group_list_new


# 数据解析：获取打组配饰
def get_furniture_group_deco(room_type, room_style, group_type, plat_role,
                             plat_id='', plat_type='', plat_style='', plat_height=1,
                             pack_num=3, pack_old=[], fine_flag=False):
    pack_list = []
    if pack_num <= 0:
        pack_num = 1
    # 组合信息
    group_todo, style_list = [], []
    if not room_style == '':
        style_list = get_furniture_style_refer_en(room_style)
    elif not plat_style == '':
        style_list = get_furniture_style_refer_en(plat_style, '')
    # 遍历方案
    global FURNITURE_GROUP_DICT
    global FURNITURE_GROUP_FINE
    load_furniture_group()
    # 判断分类
    if fine_flag:
        group_wait = [FURNITURE_GROUP_DICT, FURNITURE_GROUP_FINE]
    else:
        group_wait = [FURNITURE_GROUP_DICT]
    # 类型纠正
    plat_cate_id, plat_cate = '', ''
    if plat_role in ['table', 'cabinet'] and not plat_id == '':
        object_category_new, object_group_new, object_role_new = compute_furniture_cate_by_id(plat_id, plat_type, plat_cate_id)
        if not object_category_new == '':
            plat_cate = object_category_new.split('/')[0]
    # 查找组合
    group_todo_1, group_todo_2, group_todo_3 = [], [], []
    for group_dict in group_wait:
        for house_id, room_dict in group_dict.items():
            for room_id, group_list in room_dict.items():
                # 房间类型
                if group_type in ['Media'] and 'Living' not in room_id and 'Bed' not in room_id:
                    continue
                elif 'Living' in room_type and 'Living' not in room_id and 'Dining' not in room_id:
                    continue
                elif 'Dining' in room_type and 'Living' not in room_id and 'Dining' not in room_id:
                    continue
                elif 'Bath' in room_type and 'Bath' not in room_id:
                    continue
                elif 'Bed' in room_type and 'Bed' not in room_id:
                    continue
                # 房间硬装
                group_wall, group_ceil, group_floor = {}, {}, {}
                for group_one in group_list:
                    if group_one['type'] == 'Wall':
                        group_wall = group_one
                    elif group_one['type'] == 'Ceiling':
                        group_ceil = group_one
                    elif group_one['type'] == 'Floor':
                        group_floor = group_one
                # 遍历组合
                for group_one in group_list:
                    # 组合排除
                    if len(group_type) > 0 and not group_one['type'] == group_type:
                        continue
                    group_add = group_one
                    if 'wall' in plat_role:
                        group_add = group_wall
                    elif 'ceil' in plat_role:
                        group_add = group_ceil
                    elif 'floor' in plat_role:
                        group_add = group_floor
                    if len(group_add) <= 0:
                        continue
                    group_code, group_size, group_style = 0, [1, 1, 1], ''
                    if 'code' in group_one:
                        group_code = group_one['code']
                    if 'size' in group_one:
                        group_size = group_one['size']
                    if 'style' in group_one:
                        group_style = group_one['style']
                    if group_code % 10 <= 0:
                        continue
                    # 平台数据
                    object_main, object_type, object_style, height_main = '', '', group_style, 1
                    object_count, plants_count = 0, 0
                    for object_one in group_one['obj_list']:
                        if 'role' in object_one and object_one['role'] == plat_role:
                            object_main = object_one['id']
                            object_type, object_style = object_one['type'], object_one['style']
                            height_main = abs(object_one['size'][1] * object_one['scale'][1]) / 100
                        if 'relate_role' in object_one and object_one['relate_role'] == plat_role:
                            object_count += 1
                            if 'plants' in object_one['type']:
                                plants_count += 1
                    if object_count <= 0:
                        continue
                    if object_count <= 1 and plat_role in ['sofa', 'table', 'cabinet', 'armoire']:
                        continue
                    # 房间匹配
                    if room_type == 'KidsRoom' and room_type in room_id:
                        if object_count >= 2:
                            group_todo_1.append(group_one)
                        else:
                            group_todo_3.append(group_one)
                    # 类型匹配
                    elif plat_cate in ['书桌', '梳妆台', '餐边柜', '浴室柜', '鞋柜']:
                        object_cate_id, object_cate = '', ''
                        object_category_new, object_group_new, object_role_new = compute_furniture_cate_by_id(object_main, object_type, object_cate_id)
                        object_cate = object_category_new
                        if plat_cate in object_cate:
                            if plat_cate in ['书桌']:
                                good_count = 0
                                for object_one in group_one['obj_list']:
                                    if object_main == object_one['id']:
                                        continue
                                    object_cate = get_furniture_cate(object_one['id'])
                                    if object_cate in ['电脑']:
                                        good_count += 1
                                        break
                                if good_count >= 1:
                                    group_todo_1.append(group_one)
                                else:
                                    group_todo_2.append(group_one)
                            elif plat_cate in ['梳妆台']:
                                good_count = 0
                                for object_one in group_one['obj_list']:
                                    if object_main == object_one['id']:
                                        continue
                                    object_cate = get_furniture_cate(object_one['id'])
                                    if object_cate in ['化妆品组合']:
                                        good_count += 1
                                        break
                                if good_count >= 1:
                                    group_todo_1.append(group_one)
                                else:
                                    group_todo_2.append(group_one)
                            elif plat_cate in ['餐边柜']:
                                if 'DiningRoom' in room_id and object_count >= 3:
                                    group_todo_1.append(group_one)
                                elif object_count >= 3:
                                    group_todo_2.append(group_one)
                                else:
                                    group_todo_3.append(group_one)
                            elif plat_cate in ['浴室柜']:
                                if 'Bathroom' in room_id:
                                    group_todo_1.append(group_one)
                                else:
                                    group_todo_2.append(group_one)
                            else:
                                group_todo_1.append(group_one)
                        else:
                            if object_count >= 4:
                                group_todo_2.append(group_one)
                            else:
                                group_todo_3.append(group_one)
                    # 房间匹配
                    elif room_type == 'DiningRoom' and room_type in room_id:
                        if object_count >= 4:
                            group_todo_1.append(group_one)
                        else:
                            group_todo_2.append(group_one)
                    elif room_type == 'Library' and room_type in room_id:
                        if object_count >= 4:
                            group_todo_1.append(group_one)
                        else:
                            group_todo_3.append(group_one)
                    # 风格匹配
                    elif object_style in style_list:
                        if group_type in ['Meeting']:
                            if object_count >= 3:
                                group_todo_1.append(group_one)
                            else:
                                group_todo_2.append(group_one)
                        elif group_type in ['Dining']:
                            if object_count in [5, 7]:
                                group_todo_1.append(group_one)
                            else:
                                group_todo_2.append(group_one)
                        elif group_type in ['Cabinet']:
                            if object_count >= 4:
                                if group_size[1] < UNIT_HEIGHT_SHELF_MIN and plat_height < UNIT_HEIGHT_SHELF_MIN:
                                    group_todo_2.append(group_one)
                                elif group_size[1] < UNIT_HEIGHT_SHELF_MIN and plat_height < UNIT_HEIGHT_SHELF_MIN:
                                    group_todo_2.append(group_one)
                                else:
                                    group_todo_3.append(group_one)
                            else:
                                group_todo_3.append(group_one)
                        else:
                            if object_count >= 4:
                                group_todo_1.append(group_one)
                            else:
                                group_todo_2.append(group_one)
                    # 数量优先
                    elif object_style in ['', 'Other']:
                        if group_type in ['Dining', 'Cabinet']:
                            if object_count >= 4:
                                group_todo_2.append(group_one)
                            else:
                                group_todo_3.append(group_one)
                        else:
                            group_todo_3.append(group_one)
                    else:
                        if 'Bed' in room_type and 'Bed' in room_id:
                            group_todo_2.append(group_one)
                        else:
                            group_todo_3.append(group_add)
                # 统计组合
                if len(group_todo_1) >= pack_num * 2 or len(group_todo_1) + len(group_todo_2) >= pack_num * 4:
                    break
            # 判断
            if len(group_todo_1) >= pack_num * 2 or len(group_todo_1) + len(group_todo_2) >= pack_num * 4:
                break
        # 判断
        if len(group_todo_1) >= pack_num * 2 or len(group_todo_1) + len(group_todo_2) >= pack_num * 4:
            break
    # 遍历组合
    global GROUP_RULE_FUNCTIONAL
    pack_dict = {}
    if len(pack_old) > 0:
        pack_one = pack_old
        pack_key = '%d_%s' % (len(pack_one), pack_one[0]['id'])
        if pack_key not in pack_dict:
            pack_dict[pack_key] = 1
    # 遍历
    pack_same = []
    for group_todo in [group_todo_1, group_todo_2, group_todo_3]:
        pack_todo = []
        # 遍历
        for group_one in group_todo:
            pack_one = []
            # 关联平台
            relate_role = plat_role
            if plat_role in ['wall', 'ceil', 'floor'] and group_type in GROUP_RULE_FUNCTIONAL:
                relate_role = GROUP_RULE_FUNCTIONAL[group_type]['main']
            # 遍历物品
            same_flag, plat_new = False, {}
            for object_one in group_one['obj_list']:
                if 'id' in object_one and object_one['id'] == plat_id and not plat_id == '':
                    same_flag = True
                if 'relate_role' in object_one and object_one['relate_role'] == relate_role:
                    object_new = copy_object(object_one)
                    # 关联位置
                    if plat_role in ['wall', 'ceil', 'floor']:
                        object_new['relate_position'] = [0, 0, 0]
                        pack_one.append(object_new)
                    elif plat_role in ['sofa', 'side sofa'] and 'pillow' not in object_one['type']:
                        continue
                    # 关联位置
                    else:
                        if len(plat_new) <= 0:
                            for plat_one in group_one['obj_list']:
                                if plat_one['role'] == plat_role:
                                    if plat_role in ['side table']:
                                        pos1, pos2 = object_new['normal_position'], plat_one['normal_position']
                                        if abs(pos1[0] - pos2[0]) + abs(pos1[2] - pos2[2]) < 0.5:
                                            plat_new = plat_one
                                            break
                                    else:
                                        plat_new = plat_one
                                        break
                        if len(plat_new) > 0:
                            pos1, pos2 = object_new['normal_position'], plat_new['normal_position']
                            if plat_role in ['side table']:
                                if abs(pos1[0] - pos2[0]) + abs(pos1[2] - pos2[2]) < 0.5:
                                    object_new['relate_shifting'] = [pos1[i] - pos2[i] for i in range(3)]
                                    pack_one.append(object_new)
                            else:
                                object_new['relate_shifting'] = [pos1[i] - pos2[i] for i in range(3)]
                                pack_one.append(object_new)
            # 对称物品
            if plat_role in ['side table'] and False:
                table_left, table_right, table_copy = [], [], []
                for object_one in pack_one:
                    if object_one['normal_position'][0] < 0:
                        table_left.append(object_one)
                    else:
                        table_right.append(object_one)
                if len(table_left) > 0 and len(table_right) <= 0:
                    table_copy = table_left
                elif len(table_left) <= 0 and len(table_right) > 0:
                    table_copy = table_right
                if len(table_copy) > 0:
                    for object_one in table_copy:
                        object_new = copy_object(object_one)
                        object_new['normal_position'][0] *= -1
                        object_new['normal_rotation'][1] *= -1
                        object_new['relate_shifting'][0] *= -1
                        pack_one.append(object_new)
            # 添加物品
            if len(pack_one) <= 0:
                continue
            pack_key = '%d_%s' % (len(pack_one), pack_one[0]['id'])
            if pack_key not in pack_dict:
                pack_dict[pack_key] = 1
            else:
                pack_dict[pack_key] += 1
                continue
            if len(pack_list) >= 1 and len(pack_one) <= 1 and plat_role in ['table', 'cabinet', 'armoire']:
                continue
            # 匹配
            if same_flag and len(pack_one) >= len(pack_same):
                pack_same = pack_one
                continue
            # 排序
            find_idx = -1
            for pack_idx, pack_old in enumerate(pack_todo):
                if len(pack_old) < len(pack_one):
                    find_idx = pack_idx
                    break
            if 0 <= find_idx < len(pack_todo):
                pack_todo.insert(find_idx, pack_one)
            else:
                pack_todo.append(pack_one)
            # 判断
            if len(pack_todo) >= min(pack_num * 2, pack_num + 2):
                break
        # 判断
        if len(pack_same) > 0:
            pack_list.append(pack_same)
        for pack_one in pack_todo:
            pack_list.append(pack_one)
            if len(pack_list) >= min(pack_num * 2, pack_num + 5):
                break
        if len(pack_list) >= min(pack_num * 2, pack_num + 5):
            break
    # 乱序
    pack_fine, pack_best = [], []
    for pack_idx, pack_one in enumerate(pack_list):
        if pack_idx == 0:
            pack_best = pack_one
        if pack_idx >= pack_num + 2:
            break
        pack_fine.append(pack_one)
    random.shuffle(pack_fine)
    if len(pack_fine) > pack_num:
        pack_fine = pack_fine[0:pack_num + 0]
    # 最佳
    find_best = False
    for pack_idx, pack_one in enumerate(pack_fine):
        if len(pack_one) >= len(pack_best):
            find_best = True
            break
    if not find_best and plat_role in ['side table'] and len(pack_fine) > 0:
        pack_fine[-1] = pack_best
    # 返回信息
    return pack_fine


# 数据解析：增加打组配饰 桌布 电视 盖毯 浴帘
def add_furniture_group_deco(group_one):
    group_type = ''
    if 'type' in group_one:
        group_type = group_one['type']
    # 添加桌布
    if group_type in ['Dining']:
        # 平台家具
        object_list, object_main, object_lift = group_one['obj_list'], {}, 0
        for object_idx, object_one in enumerate(object_list):
            if object_one['role'] in ['table']:
                object_main = object_one
                break
        if len(object_main) <= 0:
            return
        # 补充装饰
        cloth_id = TABLE_CLOTH_ID
        cloth_list = get_furniture_list_id('桌布')
        object_new = copy_object_by_id(cloth_id)
        object_new['role'] = 'cloth'
        object_size = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
        object_new['size_max'] = [object_size[0] * 120, object_size[1] * 100, object_size[2] * 120]
        object_new['size_dir'] = [0, 0, 0]
        # 平台信息
        main_size = [abs(object_main['size'][i] * object_main['scale'][i]) / 100 for i in range(3)]
        plat_size = main_size[:]
        plat_center = [0, plat_size[1], 0]
        plat_dict = get_furniture_plat_detail(object_main['id'], '', 'bot')
        if len(plat_dict) > 0:
            plat_scale = object_main['scale']
            plat_find, size_best = False, 0
            for plat_key, plat_val in plat_dict.items():
                for info_one in plat_val:
                    deco_one = [info_one[i] / 100 for i in range(len(info_one))]
                    deco_one[0] *= plat_scale[0]
                    deco_one[1] *= plat_scale[1]
                    deco_one[2] *= plat_scale[2]
                    deco_one[3] *= plat_scale[0]
                    deco_one[4] *= plat_scale[1]
                    deco_one[5] *= plat_scale[2]
                    deco_one[6] *= plat_scale[1]
                    size_one = (deco_one[3] - deco_one[0]) + (deco_one[5] - deco_one[2])
                    if deco_one[1] > 0.5 and size_one > 0.5 and size_one > size_best:
                        plat_find = True
                        size_best = size_one
                        plat_size = [deco_one[3] - deco_one[0], deco_one[1], deco_one[5] - deco_one[2]]
                        plat_center = [(deco_one[0] + deco_one[3]) / 2, deco_one[1], (deco_one[2] + deco_one[5]) / 2]
                        if abs(plat_size[0] - plat_size[2]) < 0.1 and abs(plat_size[0] - main_size[0]) < 0.4:
                            plat_size = main_size[:]
        # 平台高度
        object_lift = plat_size[1]
        # 替换物品
        top_old, top_new, top_dlt = 1000, 1000 + 100, object_size[1]
        if 'top_id' in object_main:
            top_old = object_main['top_id']
            top_new = top_old + 100
        object_find = False
        for object_idx, object_one in enumerate(object_list):
            if object_one['role'] in ['table']:
                pass
            elif object_one['role'] in ['cloth'] or object_one['type'] in ['accessory/simulated cloth']:
                object_find = True
                object_list[object_idx] = object_new
            elif 'top_of' in object_one and object_one['top_of'] >= top_old:
                if object_one['top_of'] == top_old:
                    object_one['top_of'] = top_new
                object_one['position'][1] += top_dlt
                object_one['normal_position'][1] += top_dlt
                object_one['origin_position'][1] += top_dlt
                if 'relate_shifting' in object_one:
                    object_lift = object_one['relate_shifting'][1]
                    object_one['relate_shifting'][1] += top_dlt
        if not object_find:
            object_list.insert(1, object_new)
        # 位置
        object_new['position'] = object_main['position'][:]
        object_new['rotation'] = object_main['rotation'][:]
        object_new['normal_position'] = plat_center[:]
        object_new['normal_rotation'] = [0, 0, 0, 1]
        object_new['origin_position'] = object_main['origin_position'][:]
        object_new['origin_rotation'] = object_main['origin_rotation'][:]
        # 修复
        object_new['position'][1] = object_main['position'][1] + object_lift
        object_new['origin_position'][1] = object_main['origin_position'][1] + object_lift
        # 依附
        object_new['relate'] = object_main['id']
        object_new['relate_position'] = object_main['origin_position'][:]
        object_new['relate_shifting'] = plat_center[:]
        # 叠加
        object_new['top_id'] = top_new
        object_new['top_of'] = top_old
        # 尺寸
        if len(object_main) > 0:
            deco_rest = min(plat_size[1] * 1.0, 1.5)
            if abs(plat_size[0] - main_size[0]) <= 0.1 and abs(plat_size[2] - main_size[2]) <= 0.1:
                deco_rest = min(plat_size[1] * 0.8, 0.8)
            ratio_x, ratio_z = (plat_size[0] + deco_rest) / object_size[0], (plat_size[2] + deco_rest) / object_size[2]
            if 0.8 < ratio_x < 1:
                ratio_x = 1
            if 0.8 < ratio_z < 1:
                ratio_z = 1
            object_scale = object_new['scale']
            object_scale[0] *= ratio_x
            object_scale[2] *= ratio_z
    # 添加盖毯
    elif group_type in ['Meeting', 'Rest']:
        # 平台家具
        object_list, object_main, object_lift = group_one['obj_list'], {}, 0
        for object_idx, object_one in enumerate(object_list):
            if object_one['role'] in ['sofa', 'chair']:
                object_main = object_one
                break
        if len(object_main) <= 0:
            return
        # 补充装饰
        cloth_id = CHAIR_CLOTH_ID
        cloth_list = get_furniture_list_id('盖毯')
        if len(cloth_list) > 0:
            object_idx = random.randint(0, 99)
            cloth_id = cloth_list[object_idx % len(cloth_list)]
        object_new = copy_object_by_id(cloth_id)
        object_new['role'] = 'cloth'
        object_size = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
        object_new['size_max'] = [object_size[0] * 150, 200, object_size[2] * 150]
        object_new['size_dir'] = [0, 0, 0]
        object_width, object_depth = object_size[0], object_size[2]
        if object_size[2] > object_size[0] * 1.5:
            object_width, object_depth = object_size[2], object_size[0]
        # 平台信息
        main_size = [abs(object_main['size'][i] * object_main['scale'][i]) / 100 for i in range(3)]
        if main_size[0] < UNIT_WIDTH_SOFA_SINGLE * 0.8:
            return
        plat_side = False
        plat_size = main_size[:]
        plat_center = [0, plat_size[1], 0]
        # 查找平面
        plat_dict = get_furniture_plat_detail(object_main['id'], '', 'bot')
        if len(plat_dict) > 0:
            plat_scale = object_main['scale']
            size_best = 0
            for plat_key, plat_val in plat_dict.items():
                for info_one in plat_val:
                    deco_one = [info_one[i] / 100 for i in range(len(info_one))]
                    deco_one[0] *= plat_scale[0]
                    deco_one[1] *= plat_scale[1]
                    deco_one[2] *= plat_scale[2]
                    deco_one[3] *= plat_scale[0]
                    deco_one[4] *= plat_scale[1]
                    deco_one[5] *= plat_scale[2]
                    deco_one[6] *= plat_scale[1]
                    size_one = (deco_one[3] - deco_one[0]) + (deco_one[5] - deco_one[2])
                    size_add = 0
                    if deco_one[2] > -main_size[2] / 2 + 0.6:
                        size_add = 100
                        plat_side = True
                    if size_one + size_add > size_best:
                        size_best = size_one + size_add
                        plat_size = [deco_one[3] - deco_one[0], deco_one[1], deco_one[5] - deco_one[2]]
                        plat_center = [(deco_one[0] + deco_one[3]) / 2, deco_one[1],
                                       (deco_one[2] + deco_one[5]) / 2]
                        if abs(plat_size[0] - plat_size[2]) < 0.1 and abs(plat_size[0] - main_size[0]) < 0.4:
                            plat_size = main_size[:]
        # 平台高度
        object_lift = main_size[1] + 0.10
        object_shift = [plat_center[0], object_lift, plat_center[2]]
        object_shift[2] = max(plat_center[2] - plat_size[2] / 2 - 0.2, -main_size[2] / 2 + 0.1) + object_width / 2
        if plat_side and plat_center[0] > 0:
            object_shift[0] = min(plat_center[0] + plat_size[0] / 2 + 0.2, main_size[0] / 2 - 0.1) - object_width / 2
            random_ang = random.randint(0, 5) / 4 * math.pi / 4 - math.pi / 8
            normal_ang = -math.pi + random_ang
            if object_size[2] > object_size[0] * 1.5:
                normal_ang = -math.pi / 2 + random_ang
            if object_shift[2] > 0.5:
                object_shift[2] *= 0.5
        elif plat_side and plat_center[0] < 0:
            object_shift[0] = max(plat_center[0] - plat_size[0] / 2 - 0.2, -main_size[0] / 2 + 0.1) + object_width / 2
            random_ang = random.randint(0, 5) / 4 * math.pi / 4 - math.pi / 8
            normal_ang = 0 + random_ang
            if object_size[2] > object_size[0] * 1.5:
                normal_ang = math.pi / 2 + random_ang
            if object_shift[2] > 0.5:
                object_shift[2] *= 0.5
        elif plat_center[0] < -0.2:
            object_shift[0] = min(-plat_center[0] + plat_size[0] / 2 + 0.2, main_size[0] / 2 - 0.1) - object_depth / 2
            random_ang = random.randint(0, 5) / 4 * math.pi / 4 - math.pi / 8
            normal_ang = -math.pi / 2 + random_ang
            if object_size[2] > object_size[0] * 1.5:
                normal_ang = 0 + random_ang
        elif plat_center[0] > 0.2:
            object_shift[0] = max(-plat_center[0] - plat_size[0] / 2 - 0.2, -main_size[0] / 2 + 0.1) + object_depth / 2
            random_ang = random.randint(0, 5) / 4 * math.pi / 4 - math.pi / 8
            normal_ang = -math.pi / 2 + random_ang
            if object_size[2] > object_size[0] * 1.5:
                normal_ang = 0 + random_ang
        elif random.randint(0, 100) % 2 == 0:
            object_shift[0] = main_size[0] / 2 - 0.1 - object_depth / 2
            random_ang = random.randint(0, 5) / 4 * math.pi / 4 - math.pi / 8
            normal_ang = -math.pi / 2 + random_ang
            if object_size[2] > object_size[0] * 1.5:
                normal_ang = 0 + random_ang
        else:
            object_shift[0] = -main_size[0] / 2 + 0.1 + object_depth / 2
            random_ang = random.randint(0, 5) / 4 * math.pi / 4 - math.pi / 8
            normal_ang = -math.pi / 2 + random_ang
            if object_size[2] > object_size[0] * 1.5:
                normal_ang = 0 + random_ang
        plat_pos = object_main['position']
        plat_ang = rot_to_ang(object_main['rotation'])
        # 替换物品
        top_old, top_new, top_dlt = 1000, 1000 + 100, object_size[1]
        if 'top_id' in object_main:
            top_old = object_main['top_id']
            top_new = top_old + 100
        object_find = False
        for object_idx, object_one in enumerate(object_list):
            if object_one['role'] in ['sofa']:
                pass
            elif object_one['role'] in ['cloth'] or object_one['type'] in ['accessory/simulated cloth']:
                object_find = True
                object_list[object_idx] = object_new
        if not object_find:
            object_list.insert(1, object_new)
        # 位置
        object_new['position'] = object_main['position'][:]
        object_new['rotation'] = object_main['rotation'][:]
        object_new['normal_position'] = object_shift[:]
        object_new['normal_rotation'] = [0, math.sin(normal_ang / 2), 0, math.cos(normal_ang / 2)]
        object_new['origin_position'] = object_main['origin_position'][:]
        object_new['origin_rotation'] = object_main['origin_rotation'][:]
        # 修复
        tmp_x, tmp_y, tmp_z = object_shift[0], object_shift[1], object_shift[2]
        add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
        add_y = tmp_y
        add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
        object_pos = [plat_pos[0] + add_x, plat_pos[1] + add_y, plat_pos[2] + add_z]
        object_ang = plat_ang + normal_ang
        object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
        object_new['position'] = object_pos[:]
        object_new['rotation'] = object_rot[:]
        # 依附
        object_new['relate'] = object_main['id']
        object_new['relate_position'] = object_main['origin_position'][:]
        object_new['relate_shifting'] = object_shift[:]
        # 叠加
        object_new['top_id'] = top_new
        object_new['top_of'] = top_old
    # 添加电视
    elif group_type in ['Media']:
        # 平台家具
        object_list, object_main, object_lift = group_one['obj_list'], {}, 0
        for object_idx, object_one in enumerate(object_list):
            if object_one['role'] in ['table']:
                object_main = object_one
                break
        if len(object_main) <= 0:
            return
        # 补充装饰
        wall_flag, media_plat, media_wall = False, MEDIA_PLAT_ID, MEDIA_WALL_ID
        media_list = get_furniture_list_id('电视')
        if len(media_list) > 0:
            media_plat = media_list[len(object_list) % len(media_list)]
        object_new = copy_object_by_id(media_plat)
        object_new['role'] = 'tv'
        object_size = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
        object_new['size_max'] = [object_size[0] * 100, object_size[1] * 100, object_size[2] * 100]
        object_new['size_dir'] = [0, 0, 0]
        # 平台信息
        main_size = [abs(object_main['size'][i] * object_main['scale'][i]) / 100 for i in range(3)]
        plat_size = main_size[:]
        plat_center = [0, plat_size[1], 0]
        plat_dict = get_furniture_plat_detail(object_main['id'], '', 'bot')
        if len(plat_dict) > 0:
            plat_scale = object_main['scale']
            plat_find, size_best = False, 0
            for plat_key, plat_val in plat_dict.items():
                for info_one in plat_val:
                    deco_one = [info_one[i] / 100 for i in range(len(info_one))]
                    deco_one[0] *= plat_scale[0]
                    deco_one[1] *= plat_scale[1]
                    deco_one[2] *= plat_scale[2]
                    deco_one[3] *= plat_scale[0]
                    deco_one[4] *= plat_scale[1]
                    deco_one[5] *= plat_scale[2]
                    deco_one[6] *= plat_scale[1]
                    size_one = (deco_one[3] - deco_one[0]) * (deco_one[5] - deco_one[2])
                    if deco_one[1] + size_one + deco_one[0] / 10 > size_best and 0.2 < deco_one[1] < 1.5:
                        size_best = deco_one[1] + size_one + deco_one[0] / 10
                        plat_size = [deco_one[3] - deco_one[0], deco_one[1], deco_one[5] - deco_one[2]]
                        plat_center = [(deco_one[0] + deco_one[3]) / 2, deco_one[1], (deco_one[2] + deco_one[5]) / 2]
        else:
            return
        # 电视切换
        if plat_size[0] < 0.8 or plat_size[2] < 0.4:
            return
        if plat_size[0] < main_size[0] * 0.8 and abs(plat_center[0]) > 0.2:
            wall_flag = True
        elif plat_size[0] < 1.2:
            wall_flag = True
        for object_one in object_list:
            if object_one['role'] in ['tv']:
                if object_one['type'] in ['electronics/TV - wall-attached']:
                    wall_flag = True
                    media_wall = object_one['id']
                break
        if wall_flag:
            object_new = copy_object_by_id(media_wall)
            object_new['role'] = 'tv'
            object_size = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
            object_new['size_max'] = [object_size[0] * 120, object_size[1] * 120, object_size[2] * 120]
            object_new['size_dir'] = [0, 0, 0]
            if main_size[1] < UNIT_HEIGHT_SHELF_MIN:
                plat_size = [main_size[0], plat_size[1], main_size[2]]
                plat_center = [0, plat_size[1], 0]
        elif object_size[0] > max(plat_size[0] - 0.40, 1.2):
            ratio_new = max(plat_size[0] - 0.40, 1.2) / object_size[0]
            scale_new = object_new['scale']
            scale_new[0] *= ratio_new
            scale_new[1] *= ratio_new
            scale_new[2] *= ratio_new
            object_size = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
            object_new['size_max'] = [object_size[0] * 100, object_size[1] * 100, object_size[2] * 100]
            object_new['size_dir'] = [0, 0, 0]
        # 平台高度
        object_lift = plat_size[1]
        if object_new['type'] in ['electronics/TV - wall-attached']:
            object_lift = min(plat_size[1] + 0.4, 1.5)
        elif object_new['type'] in ['electronics/TV - on top of others']:
            object_lift = min(plat_size[1], 1.0)
        # 靠墙距离
        wall_space = 0.05
        if wall_flag:
            wall_space = 0.00
        object_shift = [plat_center[0], object_lift, plat_center[2] - plat_size[2] / 2 + object_size[2] / 2 + wall_space]
        plat_pos = object_main['position']
        plat_ang = rot_to_ang(object_main['rotation'])
        # 替换物品
        top_old, top_new = 1000, 1000 + 100
        if 'top_id' in object_main:
            top_old = object_main['top_id']
            top_new = top_old + 100
        object_find = False
        for object_idx, object_one in enumerate(object_list):
            if object_one['role'] in ['table']:
                pass
            elif object_one['role'] in ['tv']:
                object_find = True
                object_list[object_idx] = object_new
        if not object_find:
            object_list.insert(1, object_new)
        # 尺寸
        width_min = min(main_size[0] / 2, 2.0)
        if object_size[0] < width_min:
            object_ratio = width_min / object_size[0]
            object_scale = object_new['scale']
            object_scale[0] *= object_ratio
            object_scale[1] *= object_ratio
        # 位置
        object_new['position'] = object_main['position'][:]
        object_new['rotation'] = object_main['rotation'][:]
        object_new['normal_position'] = object_shift[:]
        object_new['normal_rotation'] = [0, 0, 0, 1]
        object_new['origin_position'] = object_main['position'][:]
        object_new['origin_rotation'] = object_main['rotation'][:]
        # 修复
        normal_ang = 0
        tmp_x, tmp_y, tmp_z = object_shift[0], object_shift[1], object_shift[2]
        add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
        add_y = tmp_y
        add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
        object_pos = [plat_pos[0] + add_x, plat_pos[1] + add_y, plat_pos[2] + add_z]
        object_ang = plat_ang + normal_ang
        object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
        object_new['position'] = object_pos[:]
        object_new['rotation'] = object_rot[:]
        # 依附
        object_new['relate'] = object_main['id']
        object_new['relate_position'] = object_main['position'][:]
        object_new['relate_shifting'] = object_shift[:]
        # 叠加
        object_new['top_id'] = top_new
        object_new['top_of'] = top_old
        # 检查
        object_todo = []
        for object_idx, object_one in enumerate(object_list):
            if object_one['role'] in ['table', 'tv']:
                continue
            if 'relate_shifting' not in object_one:
                continue
            shift_old = object_one['relate_shifting']
            if abs(shift_old[1] - plat_center[1]) > 0.01:
                break
            object_todo.append(object_idx)
        # 避让
        object_dump, object_hide = [], []
        object_add_1, object_add_2 = [], []
        object_x_min, object_x_max = object_shift[0] - object_size[0] / 2, object_shift[0] + object_size[0] / 2
        plat_x_min, plat_x_max = plat_center[0] - plat_size[0] / 2, plat_center[0] + plat_size[0] / 2
        cate_main = ['花卉', '工艺品', '书籍', '相框']
        random.shuffle(cate_main)
        for object_idx in object_todo:
            object_one = object_list[object_idx]
            if object_one['role'] in ['table', 'tv']:
                continue
            size_old = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            shift_old = object_one['relate_shifting']
            if object_idx == object_todo[0]:
                object_one['size_max'] = [size_old[0] * 100, size_old[1] * 100, size_old[2] * 100]
                object_x_max = max(object_x_max, shift_old[0] + size_old[0] / 2)
                object_add_1 = compute_accessory_side(object_x_max, plat_x_max, object_one,
                                                      plat_pos, plat_ang, cate_main[0:2])
            if object_idx == object_todo[-1]:
                object_one['size_max'] = [size_old[0] * 100, size_old[1] * 100, size_old[2] * 100]
                object_x_min = min(object_x_min, shift_old[0] - size_old[0] / 2)
                object_add_2 = compute_accessory_side(object_x_min, plat_x_min, object_one,
                                                      plat_pos, plat_ang, cate_main[2:4])
            if shift_old[1] + size_old[1] <= object_shift[1] + 0.05:
                continue
            elif shift_old[0] + size_old[0] / 2 < object_shift[0] - object_size[0] / 2:
                continue
            elif shift_old[0] - size_old[0] / 2 > object_shift[0] + object_size[0] / 2:
                continue
            else:
                object_dump.append(object_idx)
                continue
        # 隐藏
        object_hide = []
        object_dump.sort(reverse=True)
        for object_idx in object_dump:
            object_one = object_list[object_idx]
            object_hide.append(object_one)
            object_list.pop(object_idx)
        # 增加
        object_idx_1 = 2
        if len(object_todo) > 0:
            object_idx_1 = object_todo[0]
        for object_one in object_add_1:
            object_list.insert(object_idx_1, object_one)
        for object_one in object_add_2:
            object_list.insert(object_idx_1, object_one)
        group_one['obj_hide'] = object_hide
    # 添加浴帘
    elif group_type in ['Bath']:
        pass


# 数据解析：解析提取打组家具
def extract_furniture_group(furniture_todo, decorate_todo=[], room_type='', room_mirror=0, check_mode=1, print_flag=False):
    # 打组规则
    global GROUP_RULE_FUNCTIONAL

    # 清理物品
    furniture_list, furniture_last = [], []
    for furniture_idx in range(len(furniture_todo) - 1, -1, -1):
        furniture_val = furniture_todo[furniture_idx]
        furniture_key, furniture_type = furniture_val['id'], furniture_val['type']
        if furniture_key in DUMP_OBJECT_DICT_0:
            continue
        elif furniture_type in DUMP_OBJECT_TYPE_0:
            continue
        elif furniture_type in LAST_OBJECT_TYPE_0:
            furniture_last.append(furniture_val)
        else:
            furniture_list.append(furniture_val)
        if 'style' in furniture_val:
            furniture_style = furniture_val['style']
            furniture_val['style'] = get_furniture_style_en(furniture_style)

    # 打印信息
    if 'Library' in room_type and False:
        print('group room:', room_type, 'debug', '------debug------')

    # 软装造型
    sofa_list, face_list = [], []
    rely_dict, soft_mesh = {}, {}
    for furniture_idx in range(len(furniture_list) - 1, -1, -1):
        if len(decorate_todo) <= 0:
            break
        obj_one = furniture_list[furniture_idx]
        obj_size = [abs(obj_one['size'][i] * obj_one['scale'][i]) / 100 for i in range(3)]
        rely_key = obj_one['type']
        if 'sofa' in rely_key and obj_size[0] > 1.0:
            sofa_list.append(obj_one)
        elif 'TV' in rely_key:
            face_list.append(obj_one)
        if rely_key not in RELY_OBJECT_DICT_0:
            continue
        if rely_key not in rely_dict:
            rely_dict[rely_key] = [obj_one]
        else:
            rely_dict[rely_key].append(obj_one)
    for furniture_idx in range(len(decorate_todo) - 1, -1, -1):
        obj_one = decorate_todo[furniture_idx]
        obj_type = obj_one['type']
        obj_pos, obj_ang = obj_one['position'], rot_to_ang(obj_one['rotation'])
        obj_size = [abs(obj_one['size'][i] * obj_one['scale'][i]) / 100 for i in range(3)]
        if obj_pos[1] > 2.0 or obj_type in ['customized content/smart customized ceiling']:
            continue
        if obj_pos[1] > 0.2 and obj_size[2] < 0.2:
            if obj_type in ['build element/background wall'] and obj_pos[1] < 0.5:
                pass
            elif obj_type in ['build element/background wall'] and (obj_size[0] > 3.0 and obj_size[2] < 0.1):
                pass
            else:
                obj_one['type'] = '300 - on top of others'
                obj_one['style'] = ''
                furniture_list.append(obj_one)
            continue
        if obj_size[1] < 0.1:
            continue
        if obj_size[2] < 0.1:
            continue
        rely_find = False
        for rely_key, rely_set in rely_dict.items():
            rely_find, rely_size = False, [0.5, 0.5, 0.1]
            for rely_one in rely_set:
                rely_pos = rely_one['position']
                pos_old_x = rely_pos[0] - obj_pos[0]
                pos_old_z = rely_pos[2] - obj_pos[2]
                pos_new_x = pos_old_z * math.sin(-obj_ang) + pos_old_x * math.cos(-obj_ang)
                pos_new_z = pos_old_z * math.cos(-obj_ang) - pos_old_x * math.sin(-obj_ang)
                if abs(pos_new_x) < obj_size[0] / 2 - 0.1 and abs(pos_new_z) < obj_size[2] / 2:
                    rely_find = True
                    rely_size = [abs(rely_one['size'][i] * rely_one['scale'][i]) / 100 for i in range(3)]
                    break
            if rely_find:
                break
        if rely_find:
            plat_set = RELY_OBJECT_DICT_0[rely_key]
            plat_idx = min(int(obj_size[0] / rely_size[0]), len(plat_set) - 1) % len(plat_set)
            obj_one['type'] = plat_set[plat_idx]
            obj_one['style'] = ''
            furniture_list.append(obj_one)
        elif obj_pos[1] <= 0.1:
            obj_one['type'] = 'cabinet/floor-based cabinet'
            obj_one['style'] = ''
            furniture_list.append(obj_one)
        elif obj_pos[1] < 2.0 and obj_type not in ['build element/background wall', 'CustomizedCeiling']:
            obj_one['type'] = '300 - on top of others'
            obj_one['style'] = ''
            furniture_list.append(obj_one)
    if len(face_list) == 1 and len(sofa_list) >= 2:
        rely_one = face_list[0]
        rely_pos = rely_one['position']
        for obj_one in sofa_list:
            obj_pos, obj_ang = obj_one['position'], rot_to_ang(obj_one['rotation'])
            obj_size = [abs(obj_one['size'][i] * obj_one['scale'][i]) / 100 for i in range(3)]
            pos_old_x = rely_pos[0] - obj_pos[0]
            pos_old_z = rely_pos[2] - obj_pos[2]
            pos_new_x = pos_old_z * math.sin(-obj_ang) + pos_old_x * math.cos(-obj_ang)
            pos_new_z = pos_old_z * math.cos(-obj_ang) - pos_old_x * math.sin(-obj_ang)
            if abs(pos_new_x) < obj_size[0] / 2 - 0.1 and abs(pos_new_z) < obj_size[2] / 2:
                furniture_list.remove(obj_one)
                break
    # 级联物品
    link_dict = {}
    for furniture_idx in range(len(furniture_list) - 1, -1, -1):
        obj_one = furniture_list[furniture_idx]
        link_key = obj_one['type'].split('/')[0]
        if link_key not in LINK_OBJECT_DICT_0:
            continue
        link_info = LINK_OBJECT_DICT_0[link_key]
        # 级联信息
        obj_size = [abs(obj_one['size'][i] * obj_one['scale'][i]) / 100 for i in range(3)]
        if obj_size[2] > link_info['depth']:
            continue
        obj_pos, obj_ang = obj_one['position'], rot_to_ang(obj_one['rotation'])
        int_pos, int_ang = 0, 0
        if abs(obj_ang) < 0.1 or abs(obj_ang - math.pi) < 0.1 or abs(obj_ang + math.pi) < 0.1:
            int_pos, int_ang = int(obj_pos[2] * 10), 0
        elif abs(obj_ang - math.pi / 2) < 0.1 or abs(obj_ang + math.pi / 2) < 0.1:
            int_pos, int_ang = int(obj_pos[0] * 10), 90
        else:
            int_pos, int_ang = 0, int(obj_ang * 180 / math.pi / 10) * 10
        same_key = '%s_%d_%d_%d' % (link_key, int(obj_size[2] * 10 + 0.5) * 10, int_pos, int_ang)
        if same_key not in link_dict:
            link_dict[same_key] = [obj_one]
        else:
            obj_set = link_dict[same_key]
            find_idx = -1
            for old_idx, old_one in enumerate(obj_set):
                pos_1, pos_2 = obj_one['position'], old_one['position']
                if pos_1[0] + pos_1[2] < pos_2[0] + pos_2[2]:
                    find_idx = old_idx
                    break
            if find_idx <= -1:
                obj_set.append(obj_one)
            else:
                obj_set.insert(find_idx, obj_one)
    # 级联生成
    attach_todo, attach_dump, attach_diff, attach_near = [], [], 0, 5
    for obj_key, obj_val in link_dict.items():
        if len(obj_val) <= 1:
            continue
        # 最大
        obj_max, size_max, pos_max, ang_max = {}, [], [], 0
        for obj_old in obj_val:
            size_old = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
            if len(obj_max) <= 0:
                obj_max = obj_old
                size_max = size_old
            elif size_old[0] + size_old[2] > size_max[0] + size_max[2]:
                obj_max = obj_old
                size_max = size_old
        if len(obj_max) > 0 and len(size_max) > 0:
            pos_max = obj_max['position']
            ang_max = rot_to_ang(obj_max['rotation'])
        # 偏移
        obj_set = []
        min_x, min_y, min_z = 100, 100, 100
        max_x, max_y, max_z = -100, -100, -100
        min_dlt, max_dlt = 0.25, 0.50
        for obj_old in obj_val:
            size_old = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
            pos_one = obj_old['position']
            ang_one = rot_to_ang(obj_old['rotation'])
            if obj_old == obj_max:
                obj_set.append(obj_old)
            elif len(pos_max) > 0:
                pos_dlt_x = abs(pos_one[0] - pos_max[0])
                pos_dlt_y = abs(pos_one[1] - pos_max[1])
                pos_dlt_z = abs(pos_one[2] - pos_max[2])
                if min(size_max[0], size_old[0]) >= 2.5 and max(pos_dlt_x, pos_dlt_z) <= attach_near:
                    if min(pos_dlt_x, pos_dlt_z) < min_dlt:
                        obj_set.append(obj_old)
                    elif max(pos_dlt_x, pos_dlt_z) <= max_dlt:
                        obj_set.append(obj_old)
                elif size_old[0] < 2.5 and max(pos_dlt_x, pos_dlt_z) <= attach_near:
                    if min(pos_dlt_x, pos_dlt_z) < min_dlt:
                        obj_set.append(obj_old)
                    elif max(pos_dlt_x, pos_dlt_z) <= max_dlt:
                        obj_set.append(obj_old)
                else:
                    continue
            pos_old_x = pos_one[0] - pos_max[0]
            pos_old_y = pos_one[1]
            pos_old_z = pos_one[2] - pos_max[2]
            pos_new_x = pos_old_z * math.sin(-ang_max) + pos_old_x * math.cos(-ang_max)
            pos_new_z = pos_old_z * math.cos(-ang_max) - pos_old_x * math.sin(-ang_max)
            pos_new_x_1, pos_new_x_2 = pos_new_x - size_old[0] / 2, pos_new_x + size_old[0] / 2
            pos_new_z_1, pos_new_z_2 = pos_new_z - size_old[2] / 2, pos_new_z + size_old[2] / 2
            min_x = min(pos_new_x_1, pos_new_x_2, min_x)
            max_x = max(pos_new_x_1, pos_new_x_2, max_x)
            min_z = min(pos_new_z_1, pos_new_z_2, min_z)
            max_z = max(pos_new_z_1, pos_new_z_2, max_z)
            min_y = min(pos_old_y, min_y)
            max_y = max(pos_old_y + size_old[1], max_y)
        if len(obj_set) <= 1 or len(obj_max) <= 0:
            continue
        # 生成
        obj_new = copy_object(obj_max)
        attach_diff += 1
        obj_size_new = [(max_x - min_x) * 100, abs(obj_max['size'][1] * obj_max['scale'][1]), (max_z - min_z) * 100]
        obj_scale_new = [1, 1, 1]
        tmp_x, tmp_z = (max_x + min_x) / 2, (max_z + min_z) / 2
        add_x = tmp_z * math.sin(ang_max) + tmp_x * math.cos(ang_max)
        add_z = tmp_z * math.cos(ang_max) - tmp_x * math.sin(ang_max)
        obj_pos_new = [pos_max[0] + add_x, pos_max[1], pos_max[2] + add_z]
        obj_rot_new = [0, math.sin(ang_max / 2), 0, math.cos(ang_max / 2)]
        obj_new['size'] = obj_size_new
        obj_new['scale'] = obj_scale_new
        obj_new['position'] = obj_pos_new
        obj_new['rotation'] = obj_rot_new
        fake_id = 'link_%d_' % attach_diff + obj_max['id']
        obj_new['fake_id'] = fake_id
        for obj_old in obj_set:
            obj_old['group'] = ''
            obj_old['role'] = 'part'
            obj_old['relate'] = fake_id
            obj_old['relate_role'] = obj_key.split('_')[0]
            obj_old['relate_position'] = obj_pos_new[:]
            obj_old['relate_rotation'] = obj_rot_new[:]
        attach_todo.append(obj_new)
        # 添加
        link_key = obj_new['type'].split('/')[0]
        if link_key in ['sofa']:
            obj_new['type'] = 'sofa/ multi seat sofa'
        furniture_list.append(obj_new)
        pass

    # 家具计数
    furniture_count = len(furniture_list)

    # 功能区域 主要家具
    group_list_functional = extract_furniture_major(furniture_list, room_type, check_mode)

    # 功能区域 配套家具
    furniture_used, furniture_todo, main_cnt, face_cnt = [], [], 0, 0
    group_main = {}
    if len(group_list_functional) > 0:
        group_one, group_type = group_list_functional[0], ''
        if group_one['type'] in ['Meeting', 'Bed']:
            group_main = group_one
    for group_idx in range(len(group_list_functional) - 1, -1, -1):
        group_one = group_list_functional[group_idx]
        group_type, group_same = '', []
        if 'type' in group_one:
            group_type = group_one['type']
        if group_type in ['Meeting', 'Bed']:
            group_main = group_one
            main_cnt += 1
        elif group_type in ['Media']:
            face_cnt += 1
        elif group_type in ['Dining', 'Work', 'Rest']:
            for group_old in group_list_functional:
                if group_old == group_one:
                    continue
                elif group_old['type'] in ['Dining', 'Work', 'Rest']:
                    group_same.append(group_old)
                elif group_old['type'] in ['Cabinet'] and group_old['size'][0] > 1.0 and group_old['size'][1] < 1.2:
                    if group_old['size'][2] > 0.5:
                        group_same.append(group_old)
        elif group_type in ['Toilet']:
            continue
        group_fix = extract_furniture_minor(group_one, furniture_list, furniture_used, furniture_todo, group_main, group_same)
        if group_fix <= -1:
            group_list_functional.pop(group_idx)
        elif group_type in ['Dining', 'Work', 'Rest']:
            group_size = group_one['size']
            object_list, object_main, object_seat = group_one['obj_list'], {}, []
            for object_idx, object_one in enumerate(object_list):
                object_role = object_one['role']
                if object_role in ['table']:
                    object_main = object_one
                elif object_role in ['chair']:
                    object_seat.append(object_one)
            if len(object_seat) <= 0 and group_one['size'][2] * 2 < group_one['size'][0]:
                if 'relate_role' in object_one and object_one['relate_role'] in ['wall']:
                    group_one['type'] = 'Cabinet'
                    object_main['role'] = 'cabinet'

    # 功能区域 纠正家具
    group_todo = []
    if len(furniture_todo) > 0:
        furniture_new = furniture_todo[0]
        furniture_pos = furniture_new['position']
        furniture_size = [abs(furniture_new['size'][i] * furniture_new['scale'][i]) / 100 for i in range(3)]
        furniture_role = furniture_new['role']
        if furniture_role in ['table'] and furniture_pos[1] < 0.1 \
                and furniture_size[0] + furniture_size[2] > 1.0 and furniture_size[2] > 0.1:
            group_new = {
                'type': 'Rest',
                'style': furniture_new['style'],
                'code': 0,
                'size': furniture_size[:],
                'scale': [1, 1, 1],
                'offset': [0, 0, 0],
                'position': [furniture_new['position'][0], 0, furniture_new['position'][2]],
                'rotation': furniture_new['rotation'][:],
                'obj_main': '',
                'obj_type': '',
                'obj_list': [furniture_new]
            }
            extract_furniture_minor(group_new, furniture_list, furniture_used, furniture_todo)
            furniture_count = 0
            for furniture_one in group_new['obj_list']:
                if furniture_one['role'] not in ['rug', 'accessory', '']:
                    furniture_count += 1
            if furniture_size[0] + furniture_size[2] > 1.50 and furniture_size[1] > 0.50 and furniture_count >= 4:
                group_new['type'] = 'Dining'
            elif furniture_size[1] > 1.50 and furniture_size[2] > 0.10 and furniture_count <= 1:
                group_new['type'] = 'Cabinet'
                furniture_new['role'] = 'cabinet'
            elif furniture_size[0] > 0.50 and furniture_size[0] > furniture_size[2] * 2 and furniture_count <= 1:
                group_new['type'] = 'Cabinet'
                furniture_new['role'] = 'cabinet'
            group_todo.append(group_new)

    furniture_media, furniture_table, furniture_chair, furniture_bath = [], [], [], []
    for furniture_index in range(len(furniture_list) - 1, -1, -1):
        furniture_info = furniture_list[furniture_index]
        furniture_type = furniture_info['type']
        furniture_size = [abs(furniture_info['size'][i] * furniture_info['scale'][i]) / 100 for i in range(3)]
        if furniture_type.startswith('media') and face_cnt < main_cnt:
            if furniture_size[0] + furniture_size[2] > 0.5:
                furniture_info['group'] = 'Media'
                furniture_info['role'] = 'table'
                furniture_pos = furniture_info['position']
                if furniture_pos[1] > 0.1:
                    furniture_pos[1] = 0
                furniture_media.append(furniture_info)
                furniture_list.pop(furniture_index)
        elif furniture_type.startswith('table'):
            if max(furniture_size[0], furniture_size[2]) > 0.4:
                furniture_info['role'] = 'table'
                furniture_pos = furniture_info['position']
                if furniture_pos[1] > 0.1:
                    furniture_pos[1] = 0
                furniture_table.append(furniture_info)
                furniture_list.pop(furniture_index)
        elif furniture_type in ['sofa/double seat sofa', 'sofa/single seat sofa',
                                'sofa/lounge chair', 'sofa/ottoman', 'chair/armchair']:
            if furniture_size[0] + furniture_size[2] > 1.0 and min(furniture_size[0], furniture_size[2]) > 0.3:
                furniture_info['group'] = 'Rest'
                furniture_info['role'] = 'table'
                furniture_pos = furniture_info['position']
                if furniture_pos[1] > 0.1:
                    furniture_pos[1] = 0
                furniture_chair.append(furniture_info)
        elif furniture_type.startswith('bath'):
            if furniture_size[0] + furniture_size[2] > 1.0 and furniture_size[1] > 0.2:
                furniture_info['role'] = 'bath'
                furniture_pos = furniture_info['position']
                furniture_bath.append(furniture_info)
                furniture_list.pop(furniture_index)
    for furniture_todo in [furniture_media, furniture_table, furniture_chair, furniture_bath]:
        if len(furniture_todo) <= 0:
            continue
        for furniture_new in furniture_todo:
            furniture_pos = furniture_new['position']
            furniture_size = [abs(furniture_new['size'][i] * furniture_new['scale'][i]) / 100 for i in range(3)]
            furniture_type, furniture_role = furniture_new['type'], furniture_new['role']
            group_new = {
                'type': 'Rest',
                'style': furniture_new['style'],
                'code': 0,
                'size': furniture_size[:],
                'scale': [1, 1, 1],
                'offset': [0, 0, 0],
                'position': [furniture_new['position'][0], 0, furniture_new['position'][2]],
                'rotation': furniture_new['rotation'][:],
                'obj_main': '',
                'obj_type': '',
                'obj_list': [furniture_new]
            }
            if 'media unit' in furniture_type:
                group_new['type'] = 'Media'
            elif 'bath' in furniture_role:
                group_new['type'] = 'Bath'
            elif furniture_size[0] > 1.0 and furniture_size[2] > 0.5:
                group_new['type'] = 'Work'
            elif furniture_size[0] > 0.8 and furniture_size[2] < 0.4:
                group_new['type'] = 'Cabinet'
                furniture_new['role'] = 'table'
            elif furniture_pos[1] > 0.1 or furniture_size[0] + furniture_size[2] < 1.0:
                continue
            extract_furniture_minor(group_new, furniture_list, furniture_used, furniture_todo)
            furniture_count = 0
            for furniture_one in group_new['obj_list']:
                if furniture_one['role'] not in ['rug', 'accessory', '']:
                    furniture_count += 1
                if furniture_one in furniture_chair:
                    furniture_chair.remove(furniture_one)
            if furniture_count <= 1 and 'chair' in furniture_type:
                if room_type in ROOM_TYPE_LEVEL_2 or room_type in ['DiningRoom', 'Library']:
                    continue
            group_todo.append(group_new)
    for group_new in group_todo:
        group_list_functional.append(group_new)
    # 功能区域 纠正家具
    group_meet, group_rest = {}, {}
    group_same, group_dump = [], []
    for group_new in group_list_functional:
        if group_new['type'] in ['Meeting']:
            sofa_wait, meet_table = [], False
            obj_list = group_new['obj_list']
            for object_one in obj_list:
                size_old = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                if object_one['role'] in ['sofa', 'side sofa']:
                    if size_old[2] < 0.5:
                        continue
                    sofa_wait.append(object_one)
                if object_one['role'] in ['table']:
                    meet_table = True
            if len(sofa_wait) >= 2:
                main_sofa = sofa_wait[0]
                main_size = abs(main_sofa['size'][0] * main_sofa['scale'][0]) / 100
                for sofa_old in sofa_wait:
                    x1, z1, ang = sofa_old['position'][0], sofa_old['position'][2], rot_to_ang(sofa_old['rotation'])
                    sofa_size = abs(sofa_old['size'][0] * sofa_old['scale'][0]) / 100
                    sofa_side_1, sofa_side_2 = [], []
                    for sofa_new in sofa_wait:
                        if sofa_new == sofa_old:
                            continue
                        x2, z2 = sofa_new['position'][0], sofa_new['position'][2]
                        flag_left, flag_back = xyz_to_loc(x1, z1, x2, z2, ang, 1.0, 1.0, 0.5)
                        if flag_left <= -1 and flag_back <= -1:
                            sofa_side_1.append(sofa_new)
                        elif flag_left >= 1 and flag_back <= -1:
                            sofa_side_2.append(sofa_new)
                    side_size = 0
                    if len(sofa_side_1) >= 1 and len(sofa_side_2) >= 1:
                        side_size = 1
                    if sofa_size >= 1.5 and sofa_size + side_size > main_size:
                        main_sofa['role'] = 'side sofa'
                        main_sofa = sofa_old
                        main_size = sofa_size + side_size
                        main_sofa['role'] = 'sofa'
                if not main_sofa == sofa_wait[0]:
                    for object_idx, object_one in enumerate(group_new['obj_list']):
                        if object_one == main_sofa:
                            group_new['obj_list'].pop(object_idx)
                            break
                    group_new['obj_list'].insert(0, main_sofa)
                    group_new['position'] = main_sofa['position'][:]
                    group_new['rotation'] = main_sofa['rotation'][:]
            if not meet_table:
                group_meet = group_new
        elif group_new['type'] in ['Dining']:
            group_same.append(group_new)
        elif group_new['type'] in ['Rest']:
            chair_one, table_one, lamp_one = {}, {}, {}
            obj_list = group_new['obj_list']
            for object_one in obj_list:
                if object_one['role'] in ['chair']:
                    chair_one = object_one
                if object_one['role'] in ['table']:
                    table_one = object_one
                    if 'type' in table_one and 'coffee table' in table_one['type']:
                        group_rest = group_new
                if object_one['role'] in ['lamp']:
                    lamp_one = object_one
            if len(chair_one) > 0 and len(table_one) > 0:
                table_size = [abs(table_one['size'][i] * table_one['scale'][i]) / 100 for i in range(3)]
                if abs(table_size[0] - table_size[2]) < min(table_size[0], table_size[2], 1.00) * 0.05:
                    # 位置朝向
                    table_pos = table_one['position']
                    table_ang = rot_to_ang(table_one['rotation'])
                    chair_pos = chair_one['position']
                    chair_ang = rot_to_ang(chair_one['rotation'])
                    # 规范数据
                    pos_old_x = chair_pos[0] - table_pos[0]
                    pos_old_z = chair_pos[2] - table_pos[2]
                    pos_new_x = pos_old_z * math.sin(-table_ang) + pos_old_x * math.cos(-table_ang)
                    pos_new_z = pos_old_z * math.cos(-table_ang) - pos_old_x * math.sin(-table_ang)
                    if abs(pos_new_z) > abs(pos_new_x) * 1.5 or abs(pos_new_z) > table_size[2]:
                        table_ang_1 = table_ang - math.pi / 2
                        table_ang_2 = table_ang + math.pi / 2
                        delta_ang_1 = ang_to_ang(chair_ang - table_ang_1)
                        delta_ang_2 = ang_to_ang(chair_ang - table_ang_2)
                        if abs(delta_ang_1) <= abs(delta_ang_2):
                            table_rot = [0, math.sin(table_ang_1 / 2), 0, math.cos(table_ang_1 / 2)]
                            table_one['rotation'] = table_rot[:]
                            group_new['rotation'] = table_rot[:]
                        else:
                            table_rot = [0, math.sin(table_ang_2 / 2), 0, math.cos(table_ang_2 / 2)]
                            table_one['rotation'] = table_rot[:]
                            group_new['rotation'] = table_rot[:]
            elif len(chair_one) <= 0 and len(table_one) > 0:
                table_size = [abs(table_one['size'][i] * table_one['scale'][i]) / 100 for i in range(3)]
                if table_size[0] > 1 and table_size[1] > 1 and table_size[2] < 0.5:
                    group_new['type'] = 'Cabinet'
                    table_one['role'] = 'cabinet'
                elif room_type in ['LivingRoom', 'LivingDiningRoom'] and furniture_count > 1:
                    group_dump.append(group_new)
            elif len(obj_list) <= 1 and len(lamp_one) > 0:
                group_dump.append(group_new)
                furniture_list.append(lamp_one)

    # 功能区域 纠正组合
    if len(group_meet) > 0 and len(group_rest) > 0:
        # 沙发
        pos_meet, ang_meet = group_meet['position'][:], rot_to_ang(group_meet['rotation'])
        size_meet = group_meet['size'][:]
        # 茶几
        pos_rest, ang_rest = group_rest['position'][:], rot_to_ang(group_rest['rotation'])
        size_rest = group_rest['size'][:]
        # 平移
        pos_old_x = pos_rest[0] - pos_meet[0]
        pos_old_y = pos_rest[1] - pos_meet[1]
        pos_old_z = pos_rest[2] - pos_meet[2]
        pos_new_x = pos_old_z * math.sin(-ang_meet) + pos_old_x * math.cos(-ang_meet)
        pos_new_y = pos_old_y
        pos_new_z = pos_old_z * math.cos(-ang_meet) - pos_old_x * math.sin(-ang_meet)
        pos_max_z = size_meet[2] / 2 + size_rest[2] / 2 + 0.6
        if abs(pos_new_x) < 1.0 and pos_new_z > 1.0:
            tmp_x, tmp_z = pos_new_x, pos_new_z
            if abs(tmp_x) > 0.5:
                tmp_x = 0
            tmp_z = min(pos_new_z, pos_max_z)
            add_x = tmp_z * math.sin(ang_meet) + tmp_x * math.cos(ang_meet)
            add_z = tmp_z * math.cos(ang_meet) - tmp_x * math.sin(ang_meet)
            dlt_x = pos_meet[0] + add_x - pos_rest[0]
            dlt_z = pos_meet[2] + add_z - pos_rest[2]
            if 'obj_list' in group_meet and 'obj_list' in group_rest:
                obj_list_keep = group_meet['obj_list']
                obj_list_dump = group_rest['obj_list']
                if len(obj_list_dump) >= 2:
                    for obj_idx in range(len(obj_list_keep) - 1, -1, -1):
                        obj_new = obj_list_keep[obj_idx]
                        if 'role' in obj_new and obj_new['role'] in ['side sofa']:
                            obj_list_keep.pop(obj_idx)
                for obj_idx in range(len(obj_list_dump) - 1, -1, -1):
                    obj_new = obj_list_dump[obj_idx]
                    # 位置
                    obj_pos = obj_new['position']
                    obj_pos[0] += dlt_x
                    obj_pos[2] += dlt_z
                    # 角色
                    if 'role' in obj_new and obj_new['role'] in ['sofa', 'chair']:
                        obj_new['role'] = 'side sofa'
                    # 增加
                    obj_list_keep.insert(1, obj_new)
            for group_idx in range(len(group_list_functional) - 1, -1, -1):
                group_one = group_list_functional[group_idx]
                if group_one == group_rest:
                    group_list_functional.pop(group_idx)
                    break
        pass
    if len(group_same) > 1:
        group_max, chair_cnt = {}, 0
        for group_new in group_same:
            chair_set, chair_cnt = group_new['obj_list'], 0
            for chair_one in chair_set:
                if 'role' in chair_one and chair_one['role'] in ['chair']:
                    chair_cnt += 1
            group_new['chair_cnt'] = chair_cnt
        for group_new in group_same:
            if len(group_max) <= 0:
                group_max = group_new
            elif group_new['chair_cnt'] > group_max['chair_cnt']:
                group_max = group_new
        for group_new in group_same:
            chair_cnt, chair_max = group_new['chair_cnt'], group_max['chair_cnt']
            if chair_cnt <= 0 < chair_max:
                group_dump.append(group_new)
            if chair_cnt <= 1 < chair_max:
                group_new['type'] = 'Rest'
                for object_one in group_new['obj_list']:
                    object_one['group'] = 'Rest'
            if chair_cnt <= chair_max - 2:
                group_new['type'] = 'Rest'
                for object_one in group_new['obj_list']:
                    object_one['group'] = 'Rest'
            if chair_cnt < chair_max:
                group_list_functional.remove(group_new)
                group_list_functional.append(group_new)
    for group_new in group_dump:
        group_list_functional.remove(group_new)
    # 功能区域 纠正组合
    group_work, group_rest = {}, {}
    for group_new in group_list_functional:
        if group_new['type'] in ['Work']:
            group_work = group_new
        if group_new['type'] in ['Rest']:
            group_rest = group_new
    if len(group_work) <= 0 and len(group_rest) > 0 and room_type in ['Library']:
        object_list = group_rest['obj_list']
        if len(object_list) >= 2:
            group_type = 'Work'
            group_rest['type'] = group_type
            for object_one in object_list:
                object_one['group'] = group_type

    # 功能区域 规范家具
    for group_one in group_list_functional:
        extract_furniture_align(group_one, room_type, room_mirror, check_mode)

    # 装饰区域 装饰家具
    for furniture_one in furniture_last:
        furniture_list.append(furniture_one)
    group_list_decorative = extract_furniture_decor(furniture_list, room_type)
    for group_one in group_list_decorative:
        if group_one['type'] not in ['Wall', 'Ceiling', 'Floor', 'Background']:
            continue
        if len(group_one['obj_list']) <= 0:
            continue
        # 关联信息
        extract_furniture_relate(group_one, group_list_functional, room_type, room_mirror)

    # 功能区域 单独家具
    if len(group_list_functional) <= 1 and len(furniture_list) == 1 and furniture_count == 1:
        furniture_info = furniture_list[0]
        # 信息
        object_new = furniture_info
        object_id = object_new['id']
        object_type, object_style = object_new['type'], object_new['style']
        origin_size, origin_scale = object_new['size'], object_new['scale']
        object_cate = ''
        # 角色
        object_size_now = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        object_group, object_role = compute_furniture_role(object_type, object_size_now, room_type, object_id, object_cate)
        if object_group == '':
            if 'sofa' in object_type:
                object_group, object_role = 'Meeting', 'sofa'
            elif 'coffee table' in object_type:
                object_group, object_role = 'Meeting', 'table'
            elif 'dining table' in object_type:
                object_group, object_role = 'Dining', 'table'
            elif 'appliance' in object_type:
                object_group, object_role = 'Appliance', 'appliance'
            elif 'cabinet' in object_type:
                object_group, object_role = 'Cabinet', 'cabinet'
                if origin_size[0] > 100 and origin_size[1] < 40 and origin_size[2] < 40:
                    object_group, object_role = 'Media', 'table'
            elif 'side table' in object_type or 'side table' in object_type:
                object_group, object_role = 'Rest', 'table'
            elif 'table' in object_type and object_size_now[2] > 0.5:
                if object_size_now[1] > 0.6:
                    object_group, object_role = 'Work', 'table'
                else:
                    object_group, object_role = 'Meeting', 'table'
            elif 0.1 < min(object_size_now[0], object_size_now[2]) < max(object_size_now[0], object_size_now[2]) < 5:
                object_group, object_role = 'Cabinet', 'cabinet'
        if object_role in ['rug', 'accessory', '']:
            object_group = ''
        elif object_role in ['side table'] and object_group not in ['Meeting', 'Bed']:
            object_group, object_role = 'Rest', 'table'
        elif object_role in ['side table'] and max(object_size_now[0], object_size_now[2]) > 0.9:
            object_group, object_role = 'Rest', 'table'
        elif object_role in ['side sofa'] and object_group in ['Meeting']:
            object_group, object_role = 'Rest', 'chair'
        # 组合
        if not object_group == '':
            # 家具
            object_new['group'] = object_group
            object_new['role'] = object_role
            object_new['count'] = 1
            object_new['relate'] = ''
            object_new['relate_position'] = []
            object_new['adjust_position'] = [0, 0, 0]
            object_new['origin_position'] = object_new['position'][:]
            object_new['origin_rotation'] = object_new['rotation'][:]
            object_new['normal_position'] = [0, 0, 0]
            object_new['normal_rotation'] = [0, 0, 0, 1]
            # 组合
            group_one = {
                'type': object_group,
                'style': furniture_info['style'],
                'code': 0,
                'size': object_size_now[:],
                'scale': [1, 1, 1],
                'offset': [0, 0, 0],
                'position': [furniture_info['position'][0], 0, furniture_info['position'][2]],
                'rotation': furniture_info['rotation'][:],
                'size_min': object_size_now[:],
                'size_rest': [0, 0, 0, 0],
                'relate': '',
                'relate_position': [],
                'obj_main': '',
                'obj_type': '',
                'obj_list': [furniture_info]
            }
            group_list_functional.append(group_one)
            # 规范
            extract_furniture_align(group_one, room_type, room_mirror, check_mode)

    # 功能区域 整理组合
    for group_one in group_list_functional:
        group_type, object_list = group_one['type'], group_one['obj_list']
        if group_type not in GROUP_RULE_FUNCTIONAL:
            continue
        if len(object_list) <= 0:
            continue
        object_info_main = object_list[0]
        object_role_side = []
        for object_one in object_list:
            object_one['group'] = group_type
            if object_one['role'] in ['side table']:
                object_role_side.append(object_one['role'])
        # 矩形信息
        group_size, group_offset, furniture_rect = rect_group(group_one)
        # 主要家具 位置旋转
        group_rotation = group_one['rotation'][:]
        group_angle = rot_to_ang(group_rotation)
        offset = [-group_offset[0], -group_offset[1], -group_offset[2]]
        offset_x = offset[2] * math.sin(group_angle) + offset[0] * math.cos(group_angle)
        offset_y = group_offset[1]
        offset_z = offset[2] * math.cos(group_angle) - offset[0] * math.sin(group_angle)
        group_position = [group_one['position'][0] + offset_x,
                          group_one['position'][1] + offset_y,
                          group_one['position'][2] + offset_z]
        # 尺寸信息
        object_one = group_one['obj_list'][0]
        object_id, object_type = object_one['id'], object_one['type']
        origin_size, origin_scale = object_one['size'], object_one['scale']
        object_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        # 剩余信息
        width_rest1 = group_offset[0] - object_size[0] / 2 + group_size[0] / 2
        width_rest2 = group_size[0] / 2 - group_offset[0] - object_size[0] / 2
        depth_rest1 = group_offset[2] - object_size[2] / 2 + group_size[2] / 2
        depth_rest2 = group_size[2] / 2 - group_offset[2] - object_size[2] / 2
        if group_type in ['Media'] and 'side table' in object_role_side:
            width_rest_max = max(width_rest1, width_rest2)
            width_rest1 = max(width_rest1, width_rest_max)
            width_rest2 = max(width_rest2, width_rest_max)
        # 更新信息
        group_one['size'] = group_size
        group_one['offset'] = group_offset
        group_one['position'] = group_position
        group_one['rotation'] = group_rotation
        group_one['size_min'] = object_size
        group_one['size_rest'] = [depth_rest1, width_rest1, depth_rest2, width_rest2]
        group_one['obj_main'] = object_id
        group_one['obj_type'] = object_type

    # 功能区域 打印组合
    for group_one in group_list_functional:
        if not print_flag:
            break
        print('\t\tgroup extract:', group_one['type'], group_one['style'], group_one['code'],
              len(group_one['obj_list']), [obj_info['type'] for obj_info in group_one['obj_list']])

    # 返回打组
    return group_list_functional, group_list_decorative


# 数据解析：解析提取主要家具
def extract_furniture_major(furniture_list, room_type, check_mode=1):
    # 打组信息
    group_list_delay, group_list_final = [], []
    if len(furniture_list) <= 0:
        return group_list_final

    # 级联家具
    part_list, sofa_list, chair_list, bed_list, screen_list = [], [], [], [], []
    for furniture_idx in range(len(furniture_list) - 1, -1, -1):
        furniture_one = furniture_list[furniture_idx]
        furniture_type = furniture_one['type']
        if 'role' in furniture_one and furniture_one['role'] in ['part']:
            part_list.append(furniture_one)
            furniture_list.pop(furniture_idx)
        if 'sofa' in furniture_type:
            sofa_list.append(furniture_one)
        elif 'chair' in furniture_type:
            chair_list.append(furniture_one)
        elif 'bed' in furniture_type:
            bed_list.append(furniture_one)
    # 电视位置
    table_media,  table_media_pos = {}, []
    for furniture_idx in range(len(furniture_list) - 1, -1, -1):
        furniture_one = furniture_list[furniture_idx]
        furniture_id = furniture_one['id']
        furniture_type, furniture_pos = furniture_one['type'], furniture_one['position']
        if furniture_type in ['media unit/floor-based media unit']:
            table_media = furniture_one
        if len(table_media_pos) <= 0 and 'media unit' in furniture_type:
            table_media_pos = furniture_pos
        if 'TV' in furniture_type:
            table_media_pos = furniture_pos
    # 遍历家具
    for furniture_idx in range(len(furniture_list) - 1, -1, -1):
        furniture_one = furniture_list[furniture_idx]
        furniture_id = furniture_one['id']
        furniture_type, furniture_pos = furniture_one['type'], furniture_one['position']
        origin_size, origin_scale = furniture_one['size'], furniture_one['scale']
        furniture_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        furniture_cate_id = ''
        if 'category' in furniture_one:
            furniture_cate_id = furniture_one['category']
        if furniture_type in DECO_OBJECT_TYPE_0:
            if furniture_size[0] < 1 and furniture_size[1] < 1 and furniture_size[2] < 1:
                continue
        if furniture_size[0] <= 0 or furniture_size[2] <= 0:
            furniture_list.pop(furniture_idx)
            continue
        # sofa
        if furniture_type in ['bed/single bed'] and room_type in ['LivingDiningRoom', 'LivingRoom']:
            if furniture_size[0] > 1.5 > furniture_size[2]:
                furniture_type = 'sofa/ multi seat sofa'
        # table
        if furniture_type in ['table/dining table - square', 'table/dining table - round'] and room_type in ['Balcony', 'Terrace', 'Library']:
            furniture_type = 'table/table'
        elif furniture_type in ['table/side table'] and room_type in ['Balcony', 'Terrace', 'Library']:
            furniture_type = 'coffee table - round'
        elif furniture_type in ['outdoor furniture/outdoor furniture - floor-based'] and room_type in ['Balcony', 'Terrace', 'Library']:
            if furniture_size[0] > UNIT_WIDTH_SOFA_SINGLE and 0.2 < furniture_size[1] <= UNIT_HEIGHT_TABLE_MAX:
                furniture_type = 'sofa/double seat sofa'
        # table
        elif furniture_type in ['200 - on the floor'] and furniture_pos[1] < 0.1 and room_type in ['Library']:
            if furniture_size[1] <= UNIT_HEIGHT_SHELF_MIN and furniture_size[0] + furniture_size[2] < 4:
                furniture_type = 'table/table'
        elif furniture_type in ['accessory/accessory - floor-based'] and furniture_pos[1] < 0.1 and min(furniture_size[0], furniture_size[1], furniture_size[2]) > 0.4:
            if furniture_size[1] <= UNIT_HEIGHT_SHELF_MIN:
                furniture_type = 'table/side table'
        # cabinet
        if furniture_type in ['storage unit/wall-attached storage unit'] and furniture_pos[1] < 0.1:
            furniture_type = 'storage unit/floor-based storage unit'

        # 调试打印
        if 0 < furniture_pos[0] < 3 and 0 < furniture_pos[2] < 5 and furniture_size[0] > 0.8 and furniture_size[2] < 0.8 and False:
            print()
        # 打组查找
        suit_type, suit_role = '', ''
        for rule_type, rule_info in GROUP_RULE_FUNCTIONAL.items():
            if furniture_type.startswith('bed') and furniture_size[0] > 0.5:
                if furniture_size[2] > 1.5 and rule_type in ['Meeting']:
                    continue
            elif len(room_type) > 0 and room_type not in rule_info['room']:
                continue
            suit_role = rule_info['main']
            if suit_role not in rule_info['list']:
                continue
            suit_type_list = rule_info['list'][suit_role]
            if furniture_type in suit_type_list:
                suit_type = rule_type
                # 尺寸检查
                size_right = True
                if 'size' in rule_info and suit_role in rule_info['size']:
                    size_rule = rule_info['size'][suit_role]
                    if not len(size_rule) == len(furniture_size):
                        continue
                    for size_idx, [size_min, size_max] in enumerate(size_rule):
                        if furniture_size[size_idx] < size_min or furniture_size[size_idx] > size_max:
                            size_right = False
                            break
                if size_right:
                    break
                elif suit_type in ['Rest', 'Cabinet'] and furniture_size[2] < 0.1:
                    screen_list.append(furniture_one)
                    suit_type = ''
                    continue
                elif suit_type in ['Rest'] and room_type in ['Balcony', 'Terrace', 'Library']:
                    break
                else:
                    suit_type = ''
                    continue
        # 打组纠错
        if suit_type == '':
            if furniture_type == 'accessory/accessory - on top of others':
                if furniture_size[0] > 1.20 and furniture_size[1] > 1.00 and furniture_size[2] > 1.00:
                    suit_type, suit_role = 'Work', 'table'
            elif furniture_type == 'accessory/bathroom accessory - floor-based':
                if furniture_size[0] > 0.80 and furniture_size[1] > 0.40 and furniture_size[2] > 0.40:
                    suit_type, suit_role = 'Cabinet', 'cabinet'
            elif 'table/console table' in furniture_type:
                suit_type, suit_role = 'Rest', 'table'
            elif 'table/side table' in furniture_type and furniture_size[0] + furniture_size[2] > 0.6:
                suit_type, suit_role = 'Rest', 'table'
            elif ('storage unit' in furniture_type or 'wardrobe' in furniture_type) and furniture_pos[1] < 0.1:
                suit_type, suit_role = 'Cabinet', 'cabinet'
            elif 'outdoor furniture' in furniture_type:
                suit_type, suit_role = 'Rest', 'table'
                if min(furniture_size[0], furniture_size[2]) < 0.5 and max(furniture_size[0], furniture_size[2]) > 1.0:
                    suit_type, suit_role = 'Cabinet', 'cabinet'
                if furniture_id in GROUP_ROLE_UPDATE:
                    update_role = GROUP_ROLE_UPDATE[furniture_id]
                    if len(update_role) >= 2:
                        suit_type, suit_role = update_role[0], update_role[1]
            elif 'stair' in furniture_type:
                suit_type, suit_role = 'Cabinet', 'stairwell'
        if suit_type == '':
            continue
        # 打组纠错
        if suit_type in ['Bed'] and suit_role in ['bed']:
            origin_scale = furniture_one['scale']
            if abs(origin_scale[0]) > 0.8 and abs(origin_scale[0]) - abs(origin_scale[2]) > 0.2:
                origin_scale[2] = origin_scale[0]
            elif abs(origin_scale[2]) > 0.8 and abs(origin_scale[2]) - abs(origin_scale[0]) > 0.3:
                origin_scale[0] = origin_scale[2]
            furniture_one['scale'] = origin_scale
        # 打组纠错
        elif suit_type in ['Meeting'] and suit_role in ['sofa']:
            if furniture_size[0] < 2 and room_type in ['DiningRoom', 'Library']:
                continue
        elif suit_type in ['Media'] and suit_role in ['tv']:
            if 'position' in furniture_one:
                furniture_pos = furniture_one['position']
                if furniture_pos[1] < 0 or furniture_pos[1] > 3:
                    continue
        elif suit_type in ['Dining'] and suit_role in ['table']:
            if 'dining' not in furniture_type:
                object_category_new, object_group_new, object_role_new = compute_furniture_cate_by_id(furniture_id, furniture_type, furniture_cate_id)
                if not object_group_new == '':
                    suit_type, suit_role = object_group_new, object_role_new
                    if suit_type in ['Dining'] and len(furniture_list) <= 1:
                        suit_type, suit_role = 'Rest', 'table'
                    elif suit_type in ['Work'] and len(furniture_list) <= 1:
                        suit_type, suit_role = 'Work', 'table'
                elif len(furniture_list) <= 1:
                    suit_type, suit_role = 'Rest', 'table'
        if suit_type in ['Work'] and suit_role in ['table']:
            if min(furniture_size[0], furniture_size[2]) > 2.0:
                continue
        if suit_type in ['Rest'] and suit_role in ['table']:
            if 'outdoor furniture' in furniture_type and furniture_size[1] > 0.6:
                if min(furniture_size[0], furniture_size[2]) > 0.4 and max(furniture_size[0], furniture_size[2]) > 0.6:
                    continue
            elif 'lighting/floor lamp' in furniture_type:
                suit_role = 'lamp'
        if suit_type in ['Armoire'] and suit_role in ['armoire']:
            pass
        if suit_type in ['Cabinet'] and suit_role in ['cabinet']:
            if furniture_size[0] < UNIT_WIDTH_SHELF_MIN1 and furniture_size[2] < UNIT_DEPTH_SHELF_MIN:
                continue
        if suit_type in ['Appliance'] and suit_role in ['appliance']:
            if furniture_size[0] < UNIT_WIDTH_SHELF_MIN2 and furniture_size[2] < UNIT_WIDTH_SHELF_MIN2:
                continue
        furniture_one['group'], furniture_one['role'] = suit_type, suit_role
        furniture_one['count'] = 1
        if 'relate' not in furniture_one:
            furniture_one['relate'] = ''
        furniture_one['relate_position'] = []

        # 打组检查 家具替换
        group_have = False
        group_list_old = group_list_final
        if suit_type in ['Meeting', 'Dining', 'Bed']:
            for group_old in group_list_old:
                if not group_old['type'] == suit_type:
                    continue
                group_have = True
                furniture_old = group_old['obj_list'][0]
                pos_old, pos_new = furniture_old['position'], furniture_one['position']
                pos_dlt = [abs(pos_new[i] - pos_old[i]) for i in range(3)]
                size_old = [abs(furniture_old['size'][i] * furniture_old['scale'][i]) / 100 for i in range(3)]
                size_new = [abs(furniture_one['size'][i] * furniture_one['scale'][i]) / 100 for i in range(3)]
                # 增加主家具
                if size_new[0] < min(size_old[0], 2.5) and furniture_type in ['sofa/ottoman', 'sofa/single seat sofa', 'sofa/lounge chair']:
                    furniture_one['role'] = ''
                    group_have = True
                    break
                elif (pos_dlt[0] + pos_dlt[2] >= 10 or pos_dlt[0] > 4 or pos_dlt[2] > 4) and size_old[0] > 1 and size_new[0] > 1:
                    group_have = False
                else:
                    # 保持主家具
                    size_dlt_old = compute_furniture_well(furniture_old, sofa_list, suit_type, suit_role, table_media_pos)
                    size_dlt_new = compute_furniture_well(furniture_one, sofa_list, suit_type, suit_role, table_media_pos)
                    if size_new[0] + size_dlt_new <= size_old[0] + size_dlt_old:
                        if suit_type in ['Dining']:
                            if size_new[2] <= size_new[0] / 2 and size_new[1] > 0.5:
                                suit_type, suit_role = 'Cabinet', 'cabinet'
                                furniture_one['role'] = suit_role
                                group_have = False
                            elif size_new[2] > size_new[0] / 2 and size_new[1] < 0.5:
                                suit_type, suit_role = 'Rest', 'table'
                                furniture_one['role'] = suit_role
                                group_have = False
                            else:
                                group_have = True
                        else:
                            furniture_one['role'] = ''
                            group_have = True
                        break
                    # 替换主家具
                    else:
                        # 更新分组
                        group_old['size'] = furniture_size[:]
                        group_old['style'] = furniture_one['style']
                        group_old['position'] = [furniture_one['position'][0], 0, furniture_one['position'][2]]
                        group_old['rotation'] = furniture_one['rotation'][:]
                        group_old['obj_list'] = [furniture_one]
                        # 更新家具
                        furniture_add = copy_object(furniture_old)
                        furniture_list[furniture_idx] = furniture_add
                        furniture_one = furniture_add
                        furniture_id = furniture_one['id']
                        furniture_type, furniture_pos = furniture_one['type'], furniture_one['position']
                        origin_size, origin_scale = furniture_one['size'], furniture_one['scale']
                        furniture_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
                        if suit_type in ['Dining']:
                            if size_old[2] <= size_old[0] / 2 and size_old[1] > 0.5:
                                suit_type, suit_role = 'Cabinet', 'cabinet'
                                furniture_one['role'] = suit_role
                                group_have = False
                            elif size_old[2] > size_old[0] / 2 and size_old[1] < 0.5:
                                suit_type, suit_role = 'Rest', 'table'
                                furniture_one['role'] = suit_role
                                group_have = False
                            else:
                                group_have = True
                        else:
                            furniture_one['role'] = ''
                            group_have = True
                        break
        if group_have and suit_type in ['Meeting', 'Bed']:
            continue
        # 打组检查 位置错误
        if suit_type in ['Work', 'Cabinet']:
            pos_one = furniture_one['position']
            if pos_one[1] >= 0.5:
                if furniture_size[1] > 0.2 and ('Bath' in room_type or 'basin' in furniture_type):
                    pass
                else:
                    furniture_one['group'], furniture_one['role'] = '', ''
                    continue
            elif pos_one[1] >= 0.2:
                if furniture_size[1] > 0.2 and ('Bath' in room_type or 'basin' in furniture_type):
                    pass
                elif furniture_size[1] > 0.5 and 'Hallway' in room_type:
                    pass
                elif furniture_size[1] < 1:
                    furniture_one['group'], furniture_one['role'] = '', ''
                    continue

        # 打组添加
        group_one = {
            'type': suit_type,
            'style': furniture_one['style'],
            'code': 0,
            'size': furniture_size[:],
            'scale': [1, 1, 1],
            'offset': [0, 0, 0],
            'position': [furniture_one['position'][0], 0, furniture_one['position'][2]],
            'rotation': furniture_one['rotation'][:],
            'size_min': furniture_size[:],
            'size_rest': [0, 0, 0, 0],
            'relate': '',
            'relate_position': [],
            'obj_main': '',
            'obj_type': '',
            'obj_list': [furniture_one]
        }
        if suit_type in ['Cabinet'] and furniture_size[1] <= UNIT_HEIGHT_SHELF_MIN:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Cabinet'] and max(furniture_size[0], furniture_size[2]) <= 0.5:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Armoire', 'Appliance'] and furniture_size[1] <= UNIT_HEIGHT_SHELF_MIN:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Cabinet', 'Armoire', 'Appliance'] and 'Bathroom' in room_type:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Cabinet'] and room_type in ROOM_TYPE_LEVEL_1:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Cabinet'] and room_type in ROOM_TYPE_LEVEL_2 and furniture_id.endswith('.json'):
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Cabinet'] and room_type in ROOM_TYPE_LEVEL_2 and furniture_size[2] < 0.25:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Work', 'Rest'] and suit_role in ['table', 'lamp'] and \
                room_type in ['Library', 'Balcony', 'Terrace']:
            if len(bed_list) > 0:
                group_list_delay.append(group_one)
                furniture_list.pop(furniture_idx)
            elif suit_role in ['lamp']:
                group_list_delay.append(group_one)
                furniture_list.pop(furniture_idx)
            else:
                group_list_final.append(group_one)
                furniture_list.pop(furniture_idx)
        elif suit_type in ['Work', 'Rest'] and suit_role in ['table'] and \
                room_type in ROOM_TYPE_LEVEL_1 and len(furniture_list) > 1:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Work', 'Rest'] and suit_role in ['table'] and \
                room_type in ROOM_TYPE_LEVEL_2:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Rest'] and suit_role in ['chair']:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Bath'] and 'Bathroom' in room_type:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        elif suit_type in ['Media'] and suit_role in ['table']:
            group_list_delay.append(group_one)
            furniture_list.pop(furniture_idx)
        else:
            if suit_type in ['Meeting', 'Bed']:
                group_list_final.insert(0, group_one)
            else:
                group_list_final.append(group_one)
            furniture_list.pop(furniture_idx)

    # 组合纠正
    if 'DiningRoom' in room_type:
        have_food = False
        for group_old in group_list_final:
            if group_old['type'] in ['Dining']:
                have_food = True
        for group_idx in range(len(group_list_delay) - 1, -1, -1):
            group_one = group_list_delay[group_idx]
            object_role = ''
            if 'obj_list' in group_one and len(group_one['obj_list']) >= 1:
                object_main = group_one['obj_list'][0]
                if 'role' in object_main:
                    object_role = object_main['role']
            if group_one['type'] in ['Work', 'Rest'] and object_role in ['table']:
                size_new = group_one['size']
                if len(furniture_list) <= 1:
                    pass
                elif size_new[0] + size_new[1] > 1.5 and not have_food:
                    group_one['type'] = 'Dining'
                    group_list_final.append(group_one)
                    group_list_delay.pop(group_idx)
                    break
    elif 'Bathroom' in room_type:
        # 洗浴间纠正
        have_bath = False
        for group_idx, group_one in enumerate(group_list_delay):
            group_type, group_size = group_one['type'], group_one['size']
            if group_type in ['Bath']:
                have_bath = True
                break
        if not have_bath:
            for group_idx, group_one in enumerate(group_list_delay):
                group_type, group_size = group_one['type'], group_one['size']
                if group_type in ['Cabinet'] and \
                        max(group_size[0], group_size[2]) > 1.50 and min(group_size[0], group_size[2]) > 0.75:
                    group_one['type'] = 'Bath'
                    object_list = group_one['obj_list']
                    if len(object_list) >= 1:
                        object_list[0]['role'] = 'bath'
                    have_bath = True
                    break
        if not have_bath:
            for furniture_idx in range(len(furniture_list) - 1, -1, -1):
                furniture_one = furniture_list[furniture_idx]
                furniture_type = furniture_one['type']
                if furniture_type.startswith('bath'):
                    suit_type, suit_role = 'Bath', 'bath'
                    furniture_one['role'] = suit_role
                    furniture_one['count'] = 1
                    furniture_one['relate'] = ''
                    furniture_one['relate_position'] = []
                    group_one = {
                        'type': suit_type,
                        'style': furniture_one['style'],
                        'code': 0,
                        'size': [0, 0, 0],
                        'scale': [1, 1, 1],
                        'offset': [0, 0, 0],
                        'position': [furniture_one['position'][0], 0, furniture_one['position'][2]],
                        'rotation': furniture_one['rotation'][:],
                        'size_min': [0, 0, 0],
                        'size_rest': [0, 0, 0, 0],
                        'relate': '',
                        'relate_position': [],
                        'obj_main': '',
                        'obj_type': '',
                        'obj_list': [furniture_one]
                    }
                    group_list_delay.append(group_one)
                    furniture_list.pop(furniture_idx)
        # 洗衣柜纠正
        group_app = {}
        for group_idx, group_one in enumerate(group_list_delay):
            if group_one['type'] in ['Appliance']:
                group_app = group_one
                break
        for group_idx in range(len(group_list_delay) - 1, -1, -1):
            if len(group_app) <= 0:
                break
            group_one = group_list_delay[group_idx]
            if group_one['type'] not in ['Cabinet']:
                continue
            pos_old = group_app['position']
            pos_new = group_one['position']
            size_new = group_one['size']
            dis_x, dis_z = abs(pos_old[0] - pos_new[0]), abs(pos_old[2] - pos_new[2])
            if max(dis_x, dis_z) < max(size_new[0], size_new[2]) * 0.5:
                if min(dis_x, dis_z) < min(size_new[0], size_new[2]) * 0.5:
                    # 融合
                    object_old, object_new = {}, {}
                    if 'obj_list' in group_app and len(group_app['obj_list']) > 0:
                        object_old = group_app['obj_list'][0]
                    if 'obj_list' in group_one and len(group_one['obj_list']) > 0:
                        object_new = group_one['obj_list'][0]
                    if len(object_old) > 0 and len(object_new) > 0:
                        group_app['size'] = group_one['size'][:]
                        group_app['position'] = group_one['position'][:]
                        group_app['rotation'] = group_one['rotation'][:]
                        group_app['obj_list'].insert(0, object_new)
                    # 删除
                    group_list_delay.pop(group_idx)
                    break
    # 组合分类
    group_meeting, group_media, group_work, group_bath, group_toilet = {}, {}, {}, {}, {}
    for group_old in group_list_final:
        if group_old['type'] in ['Meeting']:
            group_meeting = group_old
        elif group_old['type'] in ['Media']:
            group_media = group_old
        elif group_old['type'] in ['Work']:
            group_work = group_old
        elif group_old['type'] in ['Bath']:
            group_bath = group_old
        elif group_old['type'] in ['Toilet']:
            group_toilet = group_old
    for group_old in group_list_delay:
        if group_old['type'] in ['Work']:
            group_work = group_old
    if len(group_media) <= 0 and len(table_media) > 0 and table_media in furniture_list:
        table_one = table_media
        table_one['group'], table_one['role'] = 'Media', 'table'
        table_size = [abs(table_one['size'][i] * table_one['scale'][i]) / 100 for i in range(3)]
        table_fine = True
        if table_size[2] > 0.5 and 'position' in group_meeting and 'position' in table_media:
            pos_1, pos_2 = group_meeting['position'],  table_media['position']
            dlt_x = min(abs(pos_1[0] - pos_2[0]), abs(pos_1[2] - pos_2[2]))
            dlt_z = max(abs(pos_1[0] - pos_2[0]), abs(pos_1[2] - pos_2[2]))
            sofa_size = group_meeting['size']
            if dlt_x < 0.4 and dlt_z < sofa_size[2] / 2 + table_size[2] / 2 + 0.2:
                table_fine = False
        if table_fine:
            group_one = {
                'type': 'Media',
                'style': table_one['style'],
                'code': 0,
                'size': table_size[:],
                'scale': [1, 1, 1],
                'offset': [0, 0, 0],
                'position': [table_one['position'][0], 0, table_one['position'][2]],
                'rotation': table_one['rotation'][:],
                'size_min': table_size[:],
                'size_rest': [0, 0, 0, 0],
                'relate': '',
                'relate_position': [],
                'obj_main': '',
                'obj_type': '',
                'obj_list': [table_one]
            }
            group_list_final.append(group_one)
            furniture_list.remove(table_one)
            if room_type in ['Library']:
                group_one['type'] = 'Work'
                table_one['group'] = 'Work'
                if len(group_work) <= 0:
                    group_work = group_one
            else:
                group_media = group_one
    if len(group_work) <= 0 and len(sofa_list) + len(chair_list) > 0 and room_type in ['Library']:
        chair_list_old = sofa_list + chair_list
        for group_idx, group_one in enumerate(group_list_delay):
            group_type = group_one['type']
            if group_type not in ['Media', 'Cabinet', 'Armoire']:
                continue
            position_right = True
            object_one = group_one['obj_list'][0]
            size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            pos_one, rot_one = object_one['position'], object_one['rotation']
            ang_one = rot_to_ang(rot_one)
            for object_old in chair_list_old:
                pos_old, rot_old = object_old['position'], object_old['rotation']
                size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
                dis_dlt, ang_dlt = xyz_to_ang(pos_one[0], pos_one[2], pos_old[0], pos_old[2])
                if abs(dis_dlt * math.sin(ang_dlt - ang_one)) < size_one[0] * 0.5 and \
                        abs(dis_dlt * math.cos(ang_dlt - ang_one)) < size_one[2] * 0.5 + size_old[2] * 0.5 + 0.2:
                    position_right = False
                    break
            if not position_right:
                group_one['type'] = 'Work'
                object_one['group'] = 'Work'
                object_one['role'] = 'table'
                break
    if len(group_bath) > 0 or len(group_toilet) > 0:
        for screen_one in screen_list:
            screen_one['type'] = 'shower/shower screen'

    # 遍历组合
    for group_idx, group_one in enumerate(group_list_delay):
        # 位置判断
        position_right = True
        object_one = group_one['obj_list'][0]
        type_one = object_one['type']
        size_one = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        pos_one, rot_one = object_one['position'], object_one['rotation']
        ang_one = rot_to_ang(rot_one)

        group_type, group_face, group_back = group_one['type'], '', ''
        group_near, group_near_x, group_near_z = {}, 0, 0
        for group_old in group_list_final:
            if group_old['type'] in ['Meeting', 'Bed', 'Media', 'Work', 'Rest']:
                pass
            elif group_old['type'] in ['Dining'] and group_one['type'] in ['Rest']:
                pass
            else:
                continue
            object_old = group_old['obj_list'][0]
            type_old = object_old['type']
            size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
            pos_old, rot_old = object_old['position'], object_old['rotation']
            ang_old = rot_to_ang(rot_old)
            ang_adjust = 0 - ang_old
            pos_x_old, pos_z_old = pos_one[0] - pos_old[0], pos_one[2] - pos_old[2]
            pos_x_new = pos_z_old * math.sin(ang_adjust) + pos_x_old * math.cos(ang_adjust)
            pos_z_new = pos_z_old * math.cos(ang_adjust) - pos_x_old * math.sin(ang_adjust)
            if group_old['type'] in ['Meeting']:
                x_limit = size_old[0] / 2 + min(size_one[0] + 0.05, size_one[2] + 0.05, 1.5)
                z_limit = size_old[2] / 2 + min(size_one[0] + 0.05, size_one[2] + 0.05, 1.5)
                if 'sofa' in type_one:
                    z_limit = size_old[2] / 2 + max(size_one[0] + 0.05, size_one[2] + 0.05, 1.5)
                if group_one['type'] in ['Cabinet', 'Rest'] and size_one[1] < 1.5:
                    x_limit = size_old[0] / 2 + min(max(size_one[0] / 2 + 0.20, size_one[2] / 2 + 0.20), 1.5)
                    if max(size_one[0], size_one[2]) < 0.75:
                        x_limit = size_old[0] / 2 + min(max(size_one[0] / 2 + 0.50, size_one[2] / 2 + 0.50), 1.5)
                elif group_one['type'] in ['Cabinet'] and size_one[1] > 1.5:
                    x_limit = size_old[0] / 2
            elif group_old['type'] in ['Bed']:
                x_limit = size_old[0] / 2 + max(min(size_one[0] / 2, size_one[2] / 2), 0.4) + 0.2
                z_limit = size_old[2] / 2 + 0.2
                if group_one['type'] in ['Work'] and pos_z_new < 0.0:
                    if ('single bed' in type_old and size_old[0] < 1.5) and max(size_one[0], size_one[2]) > 0.6:
                        continue
                    elif size_one[0] > 0.6 and size_one[1] > 1.0 and type_one in ['table/table']:
                        continue
                elif group_one['type'] in ['Work', 'Rest'] and pos_z_new > 0.2 and abs(pos_x_new) > size_old[0] / 2:
                    continue
            elif group_old['type'] in ['Media']:
                width_max = size_old[0]
                if len(table_media) > 0:
                    width_max = abs(table_media['size'][0] * table_media['scale'][0]) / 100
                x_limit = max(size_old[0] / 2, width_max / 2) + max(size_one[0] / 2, size_one[2] / 2, 0.5) + 0.2
                z_limit = max(size_old[2] / 2, size_one[2] / 2) + 0.2
            elif group_old['type'] in ['Dining'] and group_one['type'] in ['Rest']:
                x_limit = size_old[0] / 2 + size_one[2] / 2
                z_limit = size_old[2] / 2 + max(min(size_one[0], size_one[2]), max(size_one[0], size_one[2]) * 0.5)
            elif group_old['type'] in ['Work', 'Rest']:
                x_limit = size_old[0] / 2 + size_one[0] / 2 + 0.1
                z_limit = size_old[2] / 2 + size_one[2] + 0.1
                if abs(abs(ang_to_ang(ang_old - ang_one)) - math.pi / 2) < 0.1:
                    x_limit = size_old[0] / 2 + size_one[2] / 2 + 0.1
                    z_limit = size_old[2] / 2
                if 'lamp' in type_one:
                    x_limit += 0.2
                    z_limit += 0.2
            else:
                continue
            # 床前桌椅
            if group_old['type'] in ['Bed'] and group_one['type'] in ['Rest'] and abs(pos_x_new) < size_old[0] / 4:
                if size_old[2] / 2 - size_one[2] < pos_z_new < size_old[2] / 2 + size_one[2]:
                    position_right = False
                    break
            elif group_old['type'] in ['Bed'] and group_one['type'] in ['Rest'] and abs(pos_x_new) < size_old[0] / 2 + 0.2:
                # 角度判定
                if size_old[2] / 2 - size_one[2] < pos_z_new < size_old[2] / 2 + size_one[2] + 0.2 and 'sofa' in type_one:
                    ang_new = ang_to_ang(rot_to_ang(rot_one) + ang_adjust)
                    if math.pi / 2 < ang_new < math.pi or -math.pi < ang_new < -math.pi / 2:
                        position_right = False
                        break
            # 床后桌椅
            elif group_old['type'] in ['Bed'] and group_one['type'] in ['Cabinet']:
                rely_role = ''
                if 'relate_role' in object_one:
                    rely_role = object_one['relate_role']
                if pos_z_new < 0 - size_old[2] / 2 + 0.2:
                    if size_one[2] < 0.4 or rely_role in ['wall', 'rug']:
                        if abs(pos_x_new) < size_old[0] / 2 + 0.5:
                            position_right = False
                            break
                        elif size_one[1] > UNIT_HEIGHT_OBJECT:
                            position_right = False
                            break
                    elif 0.5 < size_one[1] < UNIT_HEIGHT_SHELF_MIN and rely_role in ['']:
                        if abs(pos_x_new) < 0.5:
                            group_one['type'], object_one['role'] = 'Work', 'table'
                            group_one['relate'], group_one['relate_role'] = 'bed', 'bed'
                            continue
            elif group_old['type'] in ['Meeting'] and group_one['type'] in ['Work', 'Rest', 'Cabinet'] and abs(pos_x_new) < size_old[0] / 4:
                if -size_old[2] / 2 - size_one[2] / 2 - 0.1 < pos_z_new < -size_old[2] / 2 - size_one[2] / 2 + 0.1:
                    group_one['type'], object_one['role'] = 'Cabinet', 'cabinet'
                    group_one['relate'], group_one['relate_role'] = 'sofa', 'sofa'
                    continue
                elif -size_old[2] / 2 - size_one[2] < pos_z_new < -size_old[2] / 2 + size_one[2]:
                    if size_one[0] > size_one[2]:
                        group_one['type'], object_one['role'] = 'Cabinet', 'cabinet'
                        continue
                    else:
                        position_right = False
                        break
            # 通用判断
            if abs(pos_x_new) < size_old[0] * 0.25 and 0 < pos_z_new and size_one[1] < 1.0 and \
                    group_old['type'] in ['Meeting', 'Bed']:
                group_face = object_old['role']
            elif abs(pos_x_new) < size_old[0] * 0.75 and pos_z_new < 0 - size_old[2] / 2 and \
                    group_old['type'] in ['Meeting', 'Bed']:
                group_back = object_old['role']
            elif abs(pos_x_new) < x_limit and abs(pos_z_new) < z_limit:
                type_main = type_one.split('/')[0]
                if group_old['type'] in ['Bed'] and type_main in ['storage unit', 'wardrobe']:
                    continue
                else:
                    position_right = False
                    group_near, group_near_x, group_near_z = group_old, pos_x_new, pos_z_new
                    break
        # 位置处理
        object_old = group_one['obj_list'][0]
        if 'group' in object_old and object_old['group'] in ['Media'] and len(group_media) <= 0:
            if object_old['role'] in ['table', 'cabinet']:
                group_one['type'] = 'Media'
                object_one['group'] = 'Media'
                object_one['role'] = 'table'
                group_list_final.append(group_one)
        elif len(group_face) > 0 and len(group_back) <= 0 and position_right:
            group_one['direct'] = group_face
            chair_cnt = 0
            for chair_idx, chair_one in enumerate(chair_list):
                if 'position' in chair_one:
                    position_tmp = chair_one['position']
                    position_dlt = [pos_one[i] - position_tmp[i] for i in range(3)]
                    if max(abs(position_dlt[0]), abs(position_dlt[2])) < 1.0:
                        chair_cnt += 1
            if chair_cnt > 0:
                group_one['type'] = 'Work'
                object_one['group'], object_one['role'] = 'Work', 'table'
                group_list_final.append(group_one)
            elif len(group_media) <= 0 and object_one['role'] in ['table', 'cabinet']:
                if room_type not in ['KidsRoom']:
                    group_one['type'] = 'Media'
                    object_one['group'], object_one['role'] = 'Media', 'table'
                else:
                    group_list_final.append(group_one)
        elif group_type in ['Cabinet'] and 'Bathroom' in room_type and size_one[0] < 0.4:
            object_old['group'], object_old['role'] = '', ''
            furniture_list.append(object_old)
        elif not position_right:
            object_old['group'], object_old['role'] = '', ''
            furniture_list.append(object_old)
            if len(group_near) > 0 and group_near['type'] in ['Media'] and abs(group_near_x) > 0.4:
                object_old['group'], object_old['role'] = 'Media', 'side table'
        else:
            group_list_final.append(group_one)
    # 增加部件
    for group_idx, group_one in enumerate(group_list_final):
        if len(part_list) <= 0:
            break
        obj_set = group_one['obj_list']
        obj_key = obj_set[0]['id']
        for part_idx in range(len(part_list) - 1, -1, -1):
            part_one = part_list[part_idx]
            plat_key = part_one['relate']
            if plat_key == obj_key:
                part_one['group'] = group_one['type']
                obj_set.append(part_one)
                part_list.pop(part_idx)

    # 返回信息
    return group_list_final


# 数据解析：解析提取配套家具
def extract_furniture_minor(group_one, furniture_list, furniture_used, furniture_todo, group_main={}, group_same=[]):
    group_type = group_one['type']
    group_rule = GROUP_RULE_FUNCTIONAL[group_type]
    count_dict = {group_rule['main']: 1}
    # 主要家具
    obj_main = group_one['obj_list'][0]
    obj_main_type, obj_main_role = obj_main['type'], obj_main['role']
    obj_main_size = [abs(obj_main['size'][i] * obj_main['scale'][i]) / 100 for i in range(3)]
    obj_main_pos, obj_main_ang = obj_main['position'], rot_to_ang(obj_main['rotation'])
    obj_main_corner = 0
    if 'left' in obj_main_type:
        obj_main_corner = -1
    elif 'right' in obj_main_type:
        obj_main_corner = 1

    plat_list = []
    if group_rule['main'] in group_rule['plat'] or obj_main_role in group_rule['plat']:
        plat_list.append(obj_main)
    if obj_main['id'] in furniture_used:
        return -1

    # 配套家具
    furniture_range = [-obj_main_size[2] / 2, -obj_main_size[0] / 2, obj_main_size[2] / 2, obj_main_size[0] / 2]
    table_main, table_wait, chair_dict, chair_near = {}, [], {}, []
    table_side, table_rely, table_move, chair_move = [], [], [], []
    table_hor, table_ver = [], []
    for furniture_index in range(len(furniture_list) - 1, -1, -1):
        furniture_info = furniture_list[furniture_index]
        furniture_id = furniture_info['id']
        furniture_type = furniture_info['type']
        origin_size, origin_scale = furniture_info['size'], furniture_info['scale']
        furniture_size = [abs(origin_size[i] * origin_scale[i]) / 100 for i in range(3)]
        if furniture_type in ['accessory/accessory - on top of others', 'plants/plants - on top of others',
                              'accessory/accessory - wall-attached']:
            if furniture_size[0] < 1 and furniture_size[1] < 1 and furniture_size[2] < 1:
                continue
        furniture_pos = furniture_info['position']
        furniture_rot = furniture_info['rotation']
        furniture_ang = rot_to_ang(furniture_rot)
        furniture_group, furniture_role = '', ''
        for value_key, value_one in group_rule['list'].items():
            if furniture_role in ['side table'] and furniture_group == group_type:
                break
            if value_key in ['side table'] and furniture_type.startswith('cabinet'):
                if 0.2 < min(furniture_size[0], furniture_size[2]) < 1.2 and furniture_size[1] < 1.2:
                    furniture_role = value_key
                    break
            if value_key in ['side sofa'] and furniture_type.startswith('sofa'):
                furniture_role = value_key
                break
            if furniture_type in value_one:
                furniture_role = value_key
                if furniture_role == group_rule['main']:
                    furniture_role = ''
                    continue
                else:
                    break
        if furniture_role in ['sofa', 'bed', 'cabinet', 'armoire', 'appliance']:
            continue
        if furniture_role in ['chair'] and 0.001 < abs(furniture_pos[1]) < 0.3:
            furniture_pos[1] = 0
        if furniture_role == '' and 'media unit' in furniture_type and group_type in ['Meeting']:
            if min(furniture_size[0], furniture_size[2]) > 1.8:
                pass
            elif furniture_size[0] > 0.5 and furniture_size[1] < 0.8 and furniture_size[2] > 0.5:
                furniture_role = 'table'
        if furniture_role == '' and 'table' in furniture_type and group_type in ['Bed']:
            if furniture_size[0] < 1.0 and furniture_size[1] < 1.5 and furniture_size[2] < 1.0:
                furniture_role = 'side table'
        if furniture_role == '' and furniture_id in GROUP_ROLE_UPDATE:
            update_role = GROUP_ROLE_UPDATE[furniture_id]
            if len(update_role) >= 2:
                furniture_group, furniture_role = update_role[0], update_role[1]
        if furniture_role in ['', 'accessory']:
            continue

        # 距离计算
        distance_old = [furniture_pos[0] - group_one['position'][0],
                        furniture_pos[1] - group_one['position'][1],
                        furniture_pos[2] - group_one['position'][2]]
        distance_old_x, distance_old_z = distance_old[0], distance_old[2]
        distance_new_x = distance_old_z * math.sin(-obj_main_ang) + distance_old_x * math.cos(-obj_main_ang)
        distance_new_z = distance_old_z * math.cos(-obj_main_ang) - distance_old_x * math.sin(-obj_main_ang)
        distance_new = [distance_new_x, distance_old[1], distance_new_z]

        # 距离判断
        range_rule_dict, range_right = {}, True
        if 'range' in group_rule:
            range_rule_dict = group_rule['range']
        if abs(distance_new_x) < obj_main_size[0] / 3 and distance_new_z > min(obj_main_size[2] / 2, 0.5):
            if furniture_role in ['side table']:
                furniture_role = 'table'
        elif abs(distance_new_x) > obj_main_size[0] / 2 and distance_new_z < max(obj_main_size[2] / 2, 0.2):
            if furniture_role in ['table']:
                if distance_new_z < 0:
                    furniture_role = 'side table'
                elif distance_new_x < 2.0 and group_type in ['Media']:
                    furniture_role = 'side table'
                else:
                    continue
        if furniture_role in range_rule_dict:
            # 距离规则
            range_rule = range_rule_dict[furniture_role]
            # 距离遍历
            range_right = True
            for range_idx, [range_min, range_max] in enumerate(range_rule):
                if group_type in ['Meeting'] and furniture_role in ['side sofa']:
                    range_x = obj_main_size[0] / 2 + furniture_size[2] / 2 + min(1.0, furniture_size[2])
                    if range_idx == 0:
                        range_min, range_max = 0 - range_x, 0 + range_x
                    elif range_idx == 2:
                        range_max = min(max(obj_main_size[2] * 2, 2.5), range_max)
                elif group_type in ['Meeting'] and furniture_role in ['side table']:
                    range_x = obj_main_size[0] / 2 + furniture_size[0] / 2 + min(0.5, furniture_size[0])
                    if range_idx == 0 and distance_new_z < obj_main_size[0] / 2:
                        range_min, range_max = 0 - range_x, 0 + range_x
                elif group_type in ['Media'] and furniture_role in ['side table']:
                    range_x = max(obj_main_size[0] / 2 + furniture_size[0] / 2 + 0.4, 2.0)
                    range_z = obj_main_size[2] / 2 + 0.2
                    if range_idx == 0:
                        range_min, range_max = 0 - range_x, 0 + range_x
                    elif range_idx == 2:
                        range_min, range_max = 0 - range_z, 0 + range_z
                elif group_type in ['Dining'] and furniture_role in ['chair']:
                    range_x = obj_main_size[0] / 2 + furniture_size[2] / 2 + min(0.5, furniture_size[2] / 2, obj_main_size[0] / 2)
                    range_z = obj_main_size[2] / 2 + furniture_size[2] / 2 + min(0.5, furniture_size[2] / 1, obj_main_size[2] / 2)
                    if range_idx == 0:
                        range_min, range_max = 0 - range_x, 0 + range_x
                    elif range_idx == 2:
                        range_min, range_max = 0 - range_z, 0 + range_z
                elif group_type in ['Work'] and furniture_role in ['chair']:
                    if 'type' in group_main and group_main['type'] in ['Bed'] and 'sofa' in furniture_type:
                        range_max = 1.0
                elif group_type in ['Rest'] and furniture_role in ['chair']:
                    range_x = obj_main_size[0] / 2 + furniture_size[2] / 2 + min(0.5, furniture_size[2] / 1, obj_main_size[0] / 1)
                    range_z = obj_main_size[2] / 2 + furniture_size[2] / 2 + min(0.5, furniture_size[2] / 1, obj_main_size[2] / 1)
                    if range_idx == 0:
                        range_min, range_max = 0 - range_x, 0 + range_x
                    elif range_idx == 2:
                        range_min, range_max = 0 - range_z, 0 + range_z
                elif group_type in ['Work'] and furniture_role in ['rug']:
                    range_x = obj_main_size[0] / 2
                    if range_idx == 0:
                        range_min, range_max = 0 - range_x, 0 + range_x
                if distance_new[range_idx] < range_min or distance_new[range_idx] > range_max:
                    range_right = False
                    break
            # 距离过近
            if group_type in ['Meeting'] and furniture_role in ['side sofa']:
                if abs(distance_new_x) <= min(obj_main_size[0] / 2, 1.0) and abs(distance_new_z) < min(obj_main_size[2] / 2, 0.5):
                    range_right = False
            elif group_type in ['Bed'] and furniture_role in ['side table']:
                if distance_new_x > 0 and distance_new_x + furniture_size[0] / 2 < 0 + obj_main_size[0] / 2:
                    range_right = False
                if distance_new_x < 0 and distance_new_x - furniture_size[0] / 2 > 0 - obj_main_size[0] / 2:
                    range_right = False
            # 距离过后
            if group_type in ['Meeting'] and furniture_role in ['table'] and not range_right:
                if obj_main_size[0] / 2 + 0 < abs(distance_new_x) < obj_main_size[0] / 2 + 1:
                    if -obj_main_size[2] / 2 < distance_new_z < 0:
                        furniture_role = 'side table'
                        range_right = True

        # 距离错误
        if not range_right:
            continue

        # 类似判断
        same_right = True
        for same_one in group_same:
            same_pos = same_one['position']
            same_dlt = [furniture_pos[0] - same_pos[0], furniture_pos[1] - same_pos[1], furniture_pos[2] - same_pos[2]]
            # 类似距离
            same_add_old, same_add_new = 0, 0
            if 'lamp' in obj_main_type:
                same_add_old = 1.0
            obj_same_type = ''
            if 'type' in same_one['obj_list'][0]:
                obj_same_type = same_one['obj_list'][0]['type']
            if 'lamp' in obj_same_type:
                same_add_new = 1.0
            # 距离比较
            if abs(same_dlt[0]) + abs(same_dlt[2]) + same_add_new < abs(distance_new_x) + abs(distance_new_z) + same_add_old:
                same_right = False
                if min(abs(same_dlt[0]), abs(same_dlt[2])) < 0.5 and max(abs(same_dlt[0]), abs(same_dlt[2])) < 1.0:
                    pass
                break
        if not same_right:
            continue

        # 尺寸判断
        size_rule_dict, size_right = {}, True
        if 'size' in group_rule:
            size_rule_dict = group_rule['size']
        if furniture_role in size_rule_dict:
            # 尺寸规则
            size_rule = size_rule_dict[furniture_role]
            # 尺寸遍历
            size_right = True
            for size_idx, [size_min, size_max] in enumerate(size_rule):
                if furniture_size[size_idx] < size_min or furniture_size[size_idx] > size_max:
                    size_right = False
                    break
            if not size_right and group_type in ['Meeting'] and furniture_role in ['table']:
                furniture_role = 'side table'
                # 尺寸规则
                size_rule = size_rule_dict[furniture_role]
                # 尺寸遍历
                if len(size_rule) >= 3:
                    size_right = True
                    for size_idx, [size_min, size_max] in enumerate(size_rule):
                        if furniture_size[size_idx] < size_min or furniture_size[size_idx] > size_max:
                            size_right = False
                            break
                # 距离规则
                range_rule = range_rule_dict[furniture_role]
                if len(range_rule) >= 3:
                    if distance_new_z < 0:
                        size_right = False
        # 尺寸错误
        if not size_right:
            continue

        # 角度判断
        angle_judge, angle_right = False, True
        if group_type in ['Meeting'] and furniture_role in ['table', 'side sofa', 'side table']:
            if furniture_role in ['side table']:
                if 'keep' in furniture_info and furniture_info['keep'] >= 1:
                    pass
                elif distance_new_z > obj_main_size[2] / 2 + furniture_size[2] / 2 and distance_new_z > 1:
                    table_rely = [furniture_info]
                    table_move = [distance_new_x, distance_new_z]
                table_side.append(furniture_info)
            elif furniture_role in ['side sofa']:
                if distance_new_z > obj_main_size[2] / 2 + furniture_size[2] / 2 and distance_new_z > 2:
                    if obj_main_type in SOFA_CORNER_TYPE_2:
                        continue
                    if distance_new_x < 0 and obj_main_corner <= -1:
                        continue
                    if distance_new_x > 0 and obj_main_corner >= 1:
                        continue
                chair_move.append([distance_new_x, distance_new_z])
            if distance_new_z < -obj_main_size[2] / 2 - furniture_size[2] / 2:
                if furniture_role in ['table']:
                    furniture_info['role'] = furniture_role
                    furniture_todo.append(furniture_info)
                continue
            else:
                if furniture_role in ['table']:
                    angle_judge = True
                    angle_delta_min = math.pi * 0.25
            # 位置纠正
            if furniture_pos[1] > 1:
                furniture_pos[1] = 0
        elif group_type in ['Work'] and furniture_role in ['chair']:
            angle_judge = True
            angle_delta_min = math.pi * 0.50
        if angle_judge:
            # 角度1
            angle1, angle2 = obj_main_ang, rot_to_ang(furniture_info['rotation'])
            # 连线角度
            x1, z1, x2, z2 = obj_main_pos[0], obj_main_pos[2], furniture_pos[0], furniture_pos[2]
            if abs(z1 - z2) <= 0.001:
                if x2 >= x1:
                    angle12 = math.pi * 0.5
                else:
                    angle12 = -math.pi * 0.5
            else:
                angle12 = math.atan((x2 - x1) / (z2 - z1))
                if z2 < z1:
                    angle12 += math.pi
            angle_delta_old = abs(angle1 - angle12)
            angle_delta_new = abs(angle_delta_old - round(angle_delta_old * 0.5 / math.pi) * math.pi * 2)
            if angle_delta_new > angle_delta_min + 0.1:
                angle_right = False
            # 角度校正
            if angle_right:
                if group_type == 'Meeting' and furniture_role == 'table':
                    width_x = abs(furniture_info['size'][0])
                    width_z = abs(furniture_info['size'][2])
                    if abs(angle1 - angle2) > 0.1 and width_x > width_z * 1.5:
                        furniture_info['rotation'] = [0, math.sin(angle1 / 2), 0, math.cos(angle1 / 2)]
            else:
                if group_type == 'Meeting' and furniture_role == 'table':
                    furniture_role = 'side table'
                elif group_type == 'Work' and furniture_role == 'chair':
                    angle1 += math.pi
                    group_one['rotation'] = [0, math.sin(angle1 / 2), 0, math.cos(angle1 / 2)]
                    obj_main['rotation'] = [0, math.sin(angle1 / 2), 0, math.cos(angle1 / 2)]
        # 重复判断
        if group_type in ['Meeting'] and furniture_role in ['side sofa']:
            if furniture_info['id'] == obj_main['id']:
                if furniture_size[0] < obj_main_size[0] / 2 and origin_scale[0] < 0.8:
                    furniture_list.pop(furniture_index)
                    continue
        elif group_type in ['Work'] and furniture_role in ['chair']:
            if len(chair_near) >= 2:
                if abs(chair_near[1]) < abs(distance_new_z) and abs(chair_near[0]) * 5.0 < abs(distance_new_x):
                    continue
        # 平台信息
        if furniture_role in group_rule['plat']:
            plat_list.append(furniture_info)
        # 风格信息
        if 'main_style' in group_rule and furniture_role == group_rule['main_style']:
            group_one['style'] = furniture_info['style']
        # 关联信息
        furniture_info['role'] = furniture_role
        furniture_info['relate'] = ''
        furniture_info['relate_position'] = []
        # 添加家具
        group_one['obj_list'].append(furniture_info)
        # 占用家具
        furniture_used.append(furniture_info['id'])
        furniture_list.pop(furniture_index)
        if furniture_info in furniture_todo:
            furniture_todo.remove(furniture_info)

        # 家具计数
        if furniture_role not in count_dict:
            count_dict[furniture_role] = 1
        else:
            count_dict[furniture_role] += 1

        # 桌椅计数
        if furniture_role == 'table':
            table_main = furniture_info
        elif furniture_role == 'side table' and abs(distance_new_x) < obj_main_size[0] / 4 and distance_new_z > 0:
            if abs(distance_new_x) < max(obj_main_size[0] / 4, 1.0) and distance_new_z < max(obj_main_size[2] / 2, 1.0):
                furniture_info['role'] = 'table'
            else:
                table_wait.append(furniture_info)
        elif furniture_role == 'chair':
            if furniture_info['id'] not in chair_dict:
                chair_dict[furniture_info['id']] = [[distance_new_x, distance_new_z]]
            else:
                chair_dict[furniture_info['id']].append([distance_new_x, distance_new_z])
            if len(chair_near) <= 0:
                chair_near = [distance_new_x, distance_new_z]
            elif abs(chair_near[0]) + abs(chair_near[1]) > abs(distance_new_x) + abs(distance_new_z):
                chair_near = [distance_new_x, distance_new_z]
        if furniture_role in ['table', 'side table']:
            if abs(ang_to_ang(furniture_ang - math.pi / 2)) < 0.1 or abs(ang_to_ang(furniture_ang + math.pi / 2)) < 0.1:
                table_hor.append(furniture_info)
            elif abs(ang_to_ang(furniture_ang)) < 0.1 or abs(ang_to_ang(furniture_ang - math.pi * 1)) < 0.1:
                table_ver.append(furniture_info)
        # 组合方向
        if furniture_role in ['bath'] and len(furniture_rot) >= 4:
            group_one['rotation'] = furniture_rot[:]
        elif furniture_role in ['table'] and len(furniture_rot) >= 4:
            if obj_main_role in ['tv']:
                if abs(ang_to_ang(obj_main_ang - furniture_ang)) < 0.1:
                    pass
                else:
                    obj_turn = (obj_main_ang - furniture_ang) * 2 / math.pi
                    obj_main['turn'] = obj_turn
                    obj_main['turn_fix'] = 1
                    add_furniture_turn(obj_main['id'], obj_turn)
                    obj_main['rotation'] = furniture_rot[:]
                    group_one['rotation'] = furniture_rot[:]
    # 方向纠正
    if len(table_ver) >= 2:
        if 0.1 < abs(ang_to_ang(obj_main_ang)) < math.pi / 4:
            obj_main_ang = 0
            obj_main['rotation'] = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
            group_one['rotation'] = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
        elif 0.1 < abs(ang_to_ang(obj_main_ang - math.pi)) < math.pi / 4:
            obj_main_ang = math.pi
            obj_main['rotation'] = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
            group_one['rotation'] = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
    elif len(table_hor) >= 2:
        if 0.1 < abs(ang_to_ang(obj_main_ang - math.pi / 2)) < math.pi / 4:
            obj_main_ang = math.pi / 2
            obj_main['rotation'] = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
            group_one['rotation'] = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
        elif 0.1 < abs(ang_to_ang(obj_main_ang + math.pi / 2)) < math.pi / 4:
            obj_main_ang = -math.pi / 2
            obj_main['rotation'] = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
            group_one['rotation'] = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]

    # 椅子判断
    if len(chair_dict) >= 2:
        object_set = group_one['obj_list']
        # 删除
        for object_idx in range(len(object_set) - 1, -1, -1):
            object_one = object_set[object_idx]
            if object_one['id'] in chair_dict:
                chair_set = chair_dict[object_one['id']]
                if len(chair_set) <= 0:
                    continue
                other_set = []
                if len(chair_set) <= 1:
                    for chair_key, chair_val in chair_dict.items():
                        if not chair_key == object_one['id']:
                            if len(chair_val) > len(other_set):
                                other_set = chair_val
                    dump_flag = False
                    if len(other_set) >= 4:
                        front_flag, back_flag = False, False
                        for other_pos in other_set:
                            if len(other_pos) >= 2 and other_pos[1] > 0.1:
                                front_flag = True
                            elif len(other_pos) >= 2 and other_pos[1] < -0.1:
                                back_flag = True
                        if front_flag and back_flag:
                            dump_flag = True
                    if dump_flag:
                        furniture_list.append(object_one)
                        object_set.pop(object_idx)
        # 角度
        chair_side1_cnt, chair_side2_cnt = 0, 0
        if group_type in ['Work', 'Rest']:
            if obj_main_role in ['table', 'lamp'] and abs(obj_main_size[0] - obj_main_size[2]) < 0.2:
                for chair_key, chair_set in chair_dict.items():
                    if len(chair_set) <= 0:
                        continue
                    if chair_set[0][0] < 0:
                        chair_side1_cnt += 1
                    if chair_set[0][0] > 0:
                        chair_side2_cnt += 1
                if chair_side1_cnt == len(chair_dict):
                    obj_main_ang += math.pi / 2
                    obj_main_rot = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
                    obj_main['rotation'] = obj_main_rot[:]
                    group_one['rotation'] = obj_main_rot[:]
                elif chair_side2_cnt == len(chair_dict):
                    obj_main_ang += math.pi / 2
                    obj_main_rot = [0, math.sin(obj_main_ang / 2), 0, math.cos(obj_main_ang / 2)]
                    obj_main['rotation'] = obj_main_rot[:]
                    group_one['rotation'] = obj_main_rot[:]

    # 茶几判断
    if len(table_main) <= 0 and len(table_wait) > 0:
        table_wait[0]['role'] = 'table'
    # 边桌判断
    if len(table_move) >= 2 and len(table_rely) > 0 and len(chair_move) > 0:
        table_fix, table_one = False, table_rely[0]
        new_x, new_z = table_move[0], table_move[1]
        for chair_idx, chair_mov in enumerate(chair_move):
            old_x, old_z = chair_mov[0], chair_mov[1]
            if old_x - 0.4 < new_x < old_x + 0.4 and new_z < old_z + 1.0:
                table_fix = True
                break
        object_set = group_one['obj_list']
        if table_fix:
            table_one['relate_role'] = 'side sofa'
        elif table_one in object_set:
            object_set.remove(table_one)

    # 数量判断
    count_rule_dict, count_right = {}, True
    if 'count' in group_rule:
        count_rule_dict = group_rule['count']
    for count_role, [count_min, count_max] in count_rule_dict.items():
        count_cur = 0
        if count_role in count_dict:
            count_cur = count_dict[count_role]
        if count_cur > count_max and count_role in ['side table']:
            tmp_x, tmp_z = 0, -obj_main_size[2] / 2
            add_x = tmp_z * math.sin(obj_main_ang) + tmp_x * math.cos(obj_main_ang)
            add_z = tmp_z * math.cos(obj_main_ang) - tmp_x * math.sin(obj_main_ang)
            new_x, new_z = obj_main_pos[0] + add_x, obj_main_pos[2] + add_z
            width_max = 0
            for obj_idx in range(len(group_one['obj_list']) - 1, -1, -1):
                obj_one = group_one['obj_list'][obj_idx]
                obj_pos = obj_one['position']
                if obj_one['role'] == count_role:
                    width_new = abs(obj_pos[0] - new_x) + abs(obj_pos[2] - new_z)
                    if width_new > width_max:
                        width_max = width_new
            for obj_idx in range(len(group_one['obj_list']) - 1, -1, -1):
                obj_one = group_one['obj_list'][obj_idx]
                obj_pos = obj_one['position']
                if obj_one['role'] == count_role:
                    width_new = abs(obj_pos[0] - new_x) + abs(obj_pos[2] - new_z)
                    if width_new >= width_max - 0.1:
                        group_one['obj_list'].pop(obj_idx)
                        if obj_one in plat_list:
                            plat_list.remove(obj_one)
                        obj_one['role'] = 'table'
                        furniture_todo.append(obj_one)
                        count_cur -= 1
                        if count_cur <= count_max:
                            break
        if count_cur > count_max:
            object_list, object_todo, object_dump = group_one['obj_list'], [], []
            for new_idx, new_one in enumerate(object_list):
                if not new_one['role'] == count_role:
                    continue
                new_width = abs(new_one['size'][0] * new_one['scale'][0]) / 100
                new_found = -1
                for old_idx, old_one in enumerate(object_todo):
                    old_width = abs(old_one['size'][0] * old_one['scale'][0]) / 100
                    if new_width > old_width:
                        new_found = old_idx
                        break
                if 0 <= new_found < len(object_todo):
                    object_todo.insert(new_found, new_one)
                else:
                    object_todo.append(new_one)
            if len(object_todo) > count_max:
                object_dump = object_todo[count_max:len(object_todo)]
                object_count = len(object_list)
                for object_idx in range(object_count - 1, -1, -1):
                    object_one = object_list[object_idx]
                    if object_one in object_dump:
                        object_list.pop(object_idx)
                        if object_one in plat_list:
                            plat_list.remove(object_one)
                        count_cur -= 1
        if count_cur < count_min:
            return -1

    # 配件判断
    if group_type in ['Media'] and len(group_one['obj_list']) >= 2:
        for object_one in group_one['obj_list']:
            if object_one['role'] in ['table']:
                obj_main = object_one
                obj_main_type, obj_main_role = obj_main['type'], obj_main['role']
                obj_main_size = [abs(obj_main['size'][i] * obj_main['scale'][i]) / 100 for i in range(3)]
                obj_main_pos, obj_main_ang = obj_main['position'], rot_to_ang(obj_main['rotation'])
    furniture_wait = []
    for furniture_index in range(len(furniture_list) - 1, -1, -1):
        furniture_info = furniture_list[furniture_index]
        furniture_type = furniture_info['type']
        furniture_size = [abs(furniture_info['size'][i] * furniture_info['scale'][i]) / 100 for i in range(3)]
        furniture_role = ''
        for value_key, value_one in group_rule['list'].items():
            if value_key == group_rule['main']:
                continue
            if furniture_type in value_one:
                furniture_role = value_key
                break
        if furniture_role in ['accessory'] or 'floor lamp' in furniture_type:
            pass
        elif furniture_role in ['side table']:
            if 0.2 < min(furniture_size[0], furniture_size[2]) < 1.2 and furniture_size[1] < 1.2:
                pass
            else:
                continue
        else:
            continue
        # 计算距离
        obj_pos = furniture_info['position']
        # 判断距离
        plat_on, wait_on = False, False
        plat_id, plat_one, plat_role, plat_size = '', {}, '', []
        plat_dlt_x, plat_dlt_z, plat_fix_y = 0, 0, 0.05

        # 遍历平台
        for plat_idx in range(len(plat_list) - 1, -1, -1):
            if 'floor lamp' in furniture_type:
                break
            plat_one = plat_list[plat_idx]
            plat_pos, plat_rot, plat_ang = plat_one['position'], plat_one['rotation'], rot_to_ang(plat_one['rotation'])
            plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
            plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
            if group_type in ['Media'] and plat_size[1] < 1.00:
                if 'role' in plat_one and plat_one['role'] in ['table']:
                    plat_fix_y = 1.00
            if furniture_type in ['lighting/pendant light', 'lighting/wall lamp']:
                if 'role' in plat_one and plat_one['role'] in ['side table']:
                    plat_fix_y = 1.00
                else:
                    plat_on = False
                    continue
            # 垂直距离
            if abs(plat_dis[1]) >= plat_size[1] + plat_fix_y:
                plat_on = False
                continue
            # 水平距离
            ang = 0 - plat_ang
            dis_x = plat_dis[2] * math.sin(ang) + plat_dis[0] * math.cos(ang)
            dis_z = plat_dis[2] * math.cos(ang) - plat_dis[0] * math.sin(ang)
            dlt_x, dlt_z = 0 - 0.05, 0 + 0.02
            if furniture_type in ['lighting/pendant light', 'lighting/wall lamp']:
                dlt_x, dlt_z = 0 - 0.05, 0 + 0.20
            if abs(dis_z) >= plat_size[2] / 2 + dlt_z:
                plat_on = False
                continue
            if abs(dis_x) >= plat_size[0] / 2 + dlt_x:
                if abs(dis_x) <= plat_size[0] / 2 + 0.05:
                    wait_on = True
                    break
                plat_on = False
                continue
            # 符合要求
            plat_on = True
            plat_id, plat_role, plat_size = plat_one['id'], plat_one['role'], plat_size
            plat_dlt_x, plat_dlt_z = dis_x, dis_z
            break
        if wait_on:
            furniture_wait.append(furniture_info)
            furniture_list.pop(furniture_index)
            continue

        # 判断落地
        if obj_pos[1] > 0.2:
            pass
        elif group_type in ['Meeting', 'Bed', 'Media', 'Work'] and not plat_on:
            distance_old = [obj_pos[0] - obj_main_pos[0], obj_pos[1] - obj_main_pos[1], obj_pos[2] - obj_main_pos[2]]
            distance_old_x, distance_old_z = distance_old[0], distance_old[2]
            distance_new_x = distance_old_z * math.sin(-obj_main_ang) + distance_old_x * math.cos(-obj_main_ang)
            distance_new_z = distance_old_z * math.cos(-obj_main_ang) - distance_old_x * math.sin(-obj_main_ang)
            size_max = max(furniture_size[0], furniture_size[2]) / 2
            if abs(distance_new_z) < obj_main_size[2] / 2 + 0.2:
                if 'floor lamp' in furniture_type and obj_pos[1] <= 0.05 and \
                        abs(distance_new_x) < obj_main_size[0] / 2 + size_max + 0.6:
                    plat_on = True
                    plat_id, plat_one, plat_role = '', obj_main, 'rug'
                    furniture_role = 'side lamp'
                elif 'plants' in furniture_type and obj_pos[1] <= 0.05 and \
                        abs(distance_new_x) < obj_main_size[0] / 2 + size_max + 0.4:
                    if group_type in ['Meeting', 'Bed'] and distance_new_z > 0:
                        pass
                    elif group_type in ['Bed'] and abs(distance_new_x) > obj_main_size[0] / 2 + size_max + 0.2:
                        pass
                    else:
                        plat_on = True
                        plat_id, plat_one, plat_role = '', obj_main, 'rug'
                        furniture_role = 'side plant'
                elif ('cabinet' in furniture_type or furniture_size[0] > 1.0) and \
                        abs(distance_new_x) < obj_main_size[0] / 2 + 0.2 and obj_pos[1] < 0.1:
                    plat_on = True
                    plat_id, plat_one, plat_role = '', obj_main, 'rug'
                    furniture_role = 'back table'
                    if obj_pos[1] > plat_size[1] and obj_pos[1] + furniture_size[1] > UNIT_HEIGHT_OBJECT:
                        obj_pos[1] = max(UNIT_HEIGHT_OBJECT - furniture_size[1], 0)
            elif -obj_main_size[2] / 2 < distance_new_z < obj_main_size[2] / 2 + 0.5:
                if abs(distance_new_x) < obj_main_size[0] / 2 + size_max:
                    plat_on = True
                    plat_id, plat_one, plat_role = '', obj_main, 'rug'
                    furniture_role = 'accessory'
        elif group_type in ['Work', 'Rest'] and min(furniture_size[0], furniture_size[1]) >= UNIT_HEIGHT_SHELF_MIN:
            if furniture_size[2] < 0.1 and 'relate_role' in group_one and group_one['relate_role'] in ['bed']:
                continue
        # 判断无效
        if not plat_on:
            continue
        if plat_role in ['sofa', 'side sofa']:
            if 'pillow' in furniture_type or 'cloth' in furniture_type:
                pass
            else:
                continue
        if plat_role in ['bed']:
            if 'pillow' in furniture_type or 'cloth' in furniture_type:
                pass
            elif 'lamp' in furniture_type or 'plant' in furniture_type:
                continue
        # 关联信息
        furniture_info['scale'] = [abs(furniture_info['scale'][i]) for i in range(3)]
        furniture_info['group'] = group_type
        furniture_info['role'] = furniture_role
        furniture_info['count'] = 1
        furniture_info['relate'] = plat_id
        furniture_info['relate_role'] = plat_role
        furniture_info['relate_group'] = group_type
        furniture_info['relate_object'] = plat_one
        furniture_info['relate_position'] = plat_one['position'][:]
        # 添加家具
        group_one['obj_list'].append(furniture_info)
        if furniture_role in ['side lamp']:
            plat_list.append(furniture_info)
        # 占用家具
        furniture_used.append(furniture_info['id'])
        furniture_list.pop(furniture_index)
        # 家具计数
        if furniture_role not in count_dict:
            count_dict[furniture_role] = 1
        else:
            count_dict[furniture_role] += 1
    # 配件判断
    if len(furniture_wait) > 0 and len(group_one['obj_list']) == 1 and group_type in ['Dining', 'Work', 'Rest']:
        furniture_info = furniture_wait[0]
        furniture_role = 'accessory'
        obj_pos = furniture_info['position']
        plat_one = group_one['obj_list'][0]
        plat_role = plat_one['role']
        plat_pos, plat_rot, plat_ang = plat_one['position'], plat_one['rotation'], rot_to_ang(plat_one['rotation'])
        plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
        dis_x = plat_dis[2] * math.sin(-plat_ang) + plat_dis[0] * math.cos(-plat_ang)
        dis_z = plat_dis[2] * math.cos(-plat_ang) - plat_dis[0] * math.sin(-plat_ang)
        dis_x = 0
        add_x = dis_z * math.sin(plat_ang) + dis_x * math.cos(plat_ang)
        add_z = dis_z * math.cos(plat_ang) - dis_x * math.sin(plat_ang)
        furniture_info['position'][0] = plat_pos[0] + add_x
        furniture_info['position'][2] = plat_pos[2] + add_z
        # 关联信息
        furniture_info['scale'] = [abs(furniture_info['scale'][i]) for i in range(3)]
        furniture_info['group'] = group_type
        furniture_info['role'] = furniture_role
        furniture_info['relate'] = plat_id
        furniture_info['relate_role'] = plat_role
        furniture_info['relate_group'] = group_type
        furniture_info['relate_object'] = plat_one
        furniture_info['relate_position'] = plat_one['position'][:]
        # 添加家具
        group_one['obj_list'].append(furniture_info)
        # 占用家具
        furniture_used.append(furniture_info['id'])

    # 返回信息
    return 0


# 数据解析：解析规范打组家具
def extract_furniture_align(group_one, room_type='', room_mirror=0, check_mode=1):
    # 家具分组
    group_type = group_one['type']
    if group_type not in GROUP_RULE_FUNCTIONAL:
        return
    pos_adjust = [0 - group_one['position'][0], 0 - group_one['position'][1], 0 - group_one['position'][2]]
    ang_adjust = 0 - rot_to_ang(group_one['rotation'])
    # 家具信息
    obj_list = group_one['obj_list']
    obj_main = obj_list[0]
    id_main, type_main, role_main = obj_main['id'], obj_main['type'], obj_main['role']
    size_main = [abs(obj_main['size'][i] * obj_main['scale'][i]) / 100 for i in range(3)]
    lift_main = obj_main['position'][1]
    if group_type in ['Cabinet', 'Armoire'] and lift_main > 0.05 and size_main[1] > 1.50:
        pos_adjust[1] = 0 - lift_main
    # 家具计数
    obj_count = 0
    for obj_one in obj_list:
        if obj_one['role'] in ['rug', 'accessory', '']:
            continue
        obj_count += 1

    # 规范区域 纠正错误
    chair_back, chair_front, chair_copy = [], [], []
    table_left, table_right, table_copy = [], [], []
    table_move = False
    table_main = {}
    for obj_one in obj_list:
        # 记录位置
        origin_position = obj_one['position'][:]
        origin_rotation = obj_one['rotation'][:]
        normal_position = [0, 0, 0]
        normal_rotation = [0, 0, 0, 1]
        obj_one['adjust_position'] = [0, 0, 0]
        obj_one['origin_position'] = origin_position[:]
        obj_one['origin_rotation'] = origin_rotation[:]
        obj_one['normal_position'] = normal_position[:]
        obj_one['normal_rotation'] = normal_rotation[:]

        # 规范位置
        pos_old_x = origin_position[0] + pos_adjust[0]
        pos_old_y = origin_position[1] + pos_adjust[1]
        pos_old_z = origin_position[2] + pos_adjust[2]
        pos_new_x = pos_old_z * math.sin(ang_adjust) + pos_old_x * math.cos(ang_adjust)
        pos_new_y = pos_old_y
        pos_new_z = pos_old_z * math.cos(ang_adjust) - pos_old_x * math.sin(ang_adjust)
        # 规范朝向
        ang_old = rot_to_ang(origin_rotation)
        ang_new = ang_to_ang(ang_old + ang_adjust)
        # 更新信息
        normal_position = [pos_new_x, pos_new_y, pos_new_z]
        normal_rotation = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
        # 镜像处理
        if room_mirror == 1 and type_main in SOFA_CORNER_TYPE_0:
            normal_position = [-pos_new_x, pos_new_y, pos_new_z]
        # 纠错处理
        obj_self, obj_role = obj_one, obj_one['role']
        size_self = [abs(obj_self['size'][i] * obj_self['scale'][i]) / 100 for i in range(3)]
        if group_type in ['Meeting'] and obj_role in ['table']:
            # 中间桌子
            table_main = obj_one
            # 角度规范
            if obj_one['type'] == 'table/coffee table - round':
                ang_new = 0
                normal_rotation = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
        elif group_type in ['Meeting'] and obj_role in ['side table', 'side plant']:
            if (abs(ang_to_ang(ang_new)) < 0.1 or abs(ang_to_ang(ang_new - math.pi)) < 0.1) and check_mode >= 1:
                min_x = -size_main[0] / 2 - size_self[0] / 2
                max_x = size_main[0] / 2 + size_self[0] / 2
                if 0 > pos_new_x > min_x:
                    pos_new_x = min_x
                elif 0 < pos_new_x < max_x:
                    pos_new_x = max_x
                if abs(pos_new_x - normal_position[0]) > 0.01:
                    obj_one['adjust_position'] = [0, 0, 0]
                    obj_one['adjust_position'][0] = pos_new_x - normal_position[0]
                    table_move = True
                if pos_new_z < 0 - size_main[2] / 2 + size_self[2] / 2 - 0.05:
                    pos_new_z = 0 - size_main[2] / 2 + size_self[2] / 2
                    obj_one['adjust_position'] = [0, 0, 0]
                    obj_one['adjust_position'][2] = pos_new_z - normal_position[2]
                    table_move = True
                normal_position[0] = pos_new_x
                normal_position[2] = pos_new_z
        elif group_type in ['Meeting'] and obj_role in ['side sofa']:
            # 拐角对调
            ratio_swap = 1
            if type_main == 'sofa/left corner sofa' and pos_new_z < 0.5 * size_main[2] + 0.5 * size_self[2]:
                if pos_new_x * ratio_swap < -0.05 * size_main[0]:
                    if check_mode >= 1:
                        normal_position[0] *= -1
                        normal_rotation = [0, math.sin(-ang_new / 2), 0, math.cos(-ang_new / 2)]
            elif type_main == 'sofa/right corner sofa' and pos_new_z < 0.5 * size_main[2] + 0.5 * size_self[2]:
                if pos_new_x * ratio_swap > 0.05 * size_main[0]:
                    if check_mode >= 1:
                        normal_position[0] *= -1
                        normal_rotation = [0, math.sin(-ang_new / 2), 0, math.cos(-ang_new / 2)]
        elif group_type in ['Bed'] and obj_role in ['side table']:
            if abs(ang_new) > 0.1:
                ang_new = 0
                normal_rotation = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
            if abs(ang_new) < 0.1 and check_mode >= 1:
                min_x = -size_main[0] / 2 - size_self[0] / 2
                max_x = size_main[0] / 2 + size_self[0] / 2
                if check_mode >= 2:
                    if min_x < pos_new_x < 0 or pos_new_x < 0:
                        if abs(size_main[0]) < 2.5:
                            pos_new_x = min_x
                    elif 0 < pos_new_x < max_x or pos_new_x > 0:
                        if abs(size_main[0]) < 2.5:
                            pos_new_x = max_x
                cur_z = -size_main[2] / 2 + size_self[2] / 2
                if pos_new_z < cur_z or cur_z + 0.1 < pos_new_z < cur_z + 1.0:
                    pos_new_z = cur_z
                if abs(pos_new_x - normal_position[0]) > 0.01 or abs(pos_new_z - normal_position[2]) > 0.01:
                    obj_one['adjust_position'] = [0, 0, 0]
                    obj_one['adjust_position'][0] = pos_new_x - normal_position[0]
                    obj_one['adjust_position'][2] = pos_new_z - normal_position[2]
                    table_move = True
                normal_position[0] = pos_new_x
                normal_position[2] = pos_new_z
                # 对称纠错
                if abs(pos_new_z - cur_z) < 1.0:
                    if pos_new_x < 0:
                        table_left.append(obj_one)
                    elif pos_new_x > 0:
                        table_right.append(obj_one)
                else:
                    table_copy.append(obj_one)
        elif group_type in ['Meeting', 'Bed'] and obj_role in ['rug']:
            if ang_to_ang(ang_new) < 0.1 or ang_to_ang(ang_new - math.pi) < 0.1:
                if pos_new_z - size_self[2] / 2 < -size_main[2] / 2:
                    pos_new_z = max(-pos_new_z, size_self[2] / 2 - size_main[2] / 2)
                    normal_position[2] = pos_new_z
            elif ang_to_ang(ang_new + math.pi / 2) < 0.1 or ang_to_ang(ang_new - math.pi / 2) < 0.1:
                if pos_new_z - size_self[0] / 2 < -size_main[2] / 2:
                    pos_new_z = max(-pos_new_z, size_self[0] / 2 - size_main[2] / 2)
                    normal_position[2] = pos_new_z
            pass
        elif group_type in ['Media'] and obj_role in ['table']:
            if obj_main['type'] == 'electronics/TV - wall-attached':
                pos_z_0 = obj_main['size'][2] * obj_main['scale'][2] / 100
                pos_z_1 = obj_one['size'][2] * obj_one['scale'][2] / 100
                pos_new_z = -pos_z_0 / 2 + pos_z_1 / 2
                normal_position[2] = pos_new_z
                if len(obj_list) <= 2 and size_self[2] <= UNIT_HEIGHT_TABLE_MAX:
                    normal_position[0] = 0
        elif group_type in ['Media'] and obj_role in ['side table', 'side plant']:
            if (abs(ang_to_ang(ang_new)) < 0.1 or abs(ang_to_ang(ang_new - math.pi)) < 0.1) and check_mode >= 1:
                min_x = -size_main[0] / 2 - size_self[0] / 2
                max_x = size_main[0] / 2 + size_self[0] / 2
                if 0 > pos_new_x > min_x:
                    pos_new_x = min_x
                elif 0 < pos_new_x < max_x:
                    pos_new_x = max_x
                if abs(pos_new_x - normal_position[0]) > 0.01:
                    obj_one['adjust_position'] = [0, 0, 0]
                    obj_one['adjust_position'][0] = pos_new_x - normal_position[0]
                    table_move = True
                if pos_new_z < 0 - size_main[2] / 2 + size_self[2] / 2 - 0.05:
                    pos_new_z = 0 - size_main[2] / 2 + size_self[2] / 2
                    obj_one['adjust_position'] = [0, 0, 0]
                    obj_one['adjust_position'][2] = pos_new_z - normal_position[2]
                    table_move = True
                normal_position[0] = pos_new_x
                normal_position[2] = pos_new_z
        elif group_type in ['Dining'] and obj_role in ['chair']:
            flag_left, flag_back = xyz_to_loc(0, 0, pos_new_x, pos_new_z, 0, size_main[0], size_main[2], 0.4)
            if flag_back >= 1:
                chair_back.append(obj_one)
            elif flag_back <= -1:
                chair_front.append(obj_one)
            if flag_back >= 1:
                if size_self[0] > 1 and abs(pos_new_x) <= 0.4 and 0 - size_main[2] / 2 - 0.1 < pos_new_z < 0:
                    normal_position[2] = 0 - size_main[2] / 2 - size_self[2] / 2
            elif flag_back <= -1:
                if size_self[0] > 1 and abs(pos_new_x) <= 0.4 and 0 + size_main[2] / 2 + 0.1 > pos_new_z > 0:
                    normal_position[2] = 0 + size_main[2] / 2 + size_self[2] / 2
        elif group_type in ['Rest'] and obj_role in ['chair']:
            if abs(ang_new) > math.pi / 2 and check_mode >= 1 and obj_count <= 2:
                ang_new = math.pi - ang_new
                normal_rotation = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
        elif group_type in ['Bath'] and obj_role in ['screen']:
            if normal_position[2] <= -0.1 and size_self[2] < 0.2 < size_self[0]:
                # 分组
                if len(obj_main) > 0:
                    ang_main = rot_to_ang(obj_main['rotation'])
                    rot_main = [0, math.sin(-ang_main / 2), 0, math.cos(-ang_main / 2)]
                    obj_main['rotation'] = rot_main[:]
                    obj_main['origin_rotation'] = rot_main[:]
                    group_one['rotation'] = rot_main[:]
                # 自身
                normal_position[0] *= -1
                normal_position[2] *= -1
                normal_rotation = [0, math.sin(-ang_new / 2), 0, math.cos(-ang_new / 2)]
        # 配件纠错
        if 'relate_object' in obj_one:
            if table_move and obj_one['type'] not in ['lighting/pendant light', 'lighting/wall lamp']:
                obj_plat = obj_one['relate_object']
                obj_move = [0, 0, 0]
                if 'adjust_position' in obj_plat:
                    obj_move = obj_plat['adjust_position']
                for i in range(3):
                    normal_position[i] += obj_move[i]
            obj_one.pop('relate_object')

        # 原始位置
        obj_one['origin_position'] = origin_position[:]
        obj_one['origin_rotation'] = origin_rotation[:]
        # 规范位置
        obj_one['normal_position'] = normal_position[:]
        obj_one['normal_rotation'] = normal_rotation[:]
        # 更新位置
        obj_one['position'] = normal_position[:]
        obj_one['rotation'] = normal_rotation[:]

        # 边桌纠错
        table_face = False
        pos_new_x, pos_new_z = 0, 0
        if len(table_left) >= 1 and len(table_right) <= 0 and check_mode >= 2 and len(table_copy) == 1:
            table_face = True
            pos_new_x, pos_new_z = -table_left[0]['normal_position'][0], table_left[0]['normal_position'][2]
        if len(table_left) <= 0 and len(table_right) >= 1 and check_mode >= 2 and len(table_copy) == 1:
            table_face = True
            pos_new_x, pos_new_z = -table_right[0]['normal_position'][0], table_right[0]['normal_position'][2]
        if table_face:
            obj_old = table_copy[0]
            # 更新偏移
            pos_old_x, pos_old_z = obj_old['normal_position'][0], obj_old['normal_position'][2]
            adjust_position = [0, 0, 0]
            if 'adjust_position' in obj_old:
                adjust_position = obj_old['adjust_position']
            adjust_position[0] += (pos_new_x - pos_old_x)
            adjust_position[2] += (pos_new_z - pos_old_z)
            obj_old['adjust_position'] = adjust_position
            table_move = True
            # 更新位置
            normal_position = [pos_new_x, obj_old['normal_position'][1], pos_new_z]
            obj_old['normal_position'] = normal_position[:]
            obj_old['normal_rotation'] = normal_rotation[:]
            obj_old['position'] = normal_position[:]
            obj_old['rotation'] = normal_rotation[:]

    # 功能区域 补齐家具
    if len(chair_back) >= 2 and len(chair_front) <= 0 and check_mode >= 2:
        chair_copy = chair_back
    elif len(chair_back) <= 0 and len(chair_front) >= 2 and check_mode >= 2:
        chair_copy = chair_front
    elif len(chair_back) >= 2 and len(chair_front) == 1 and check_mode >= 2:
        chair_keep = chair_front[0]
        chair_size = [abs(chair_keep['size'][i] * chair_keep['scale'][i]) / 100 for i in range(3)]
        chair_copy = []
        for chair_one in chair_back:
            width_dlt = abs(chair_one['normal_position'][0] - chair_keep['normal_position'][0])
            if width_dlt > chair_size[0] * 0.75:
                chair_copy.append(chair_one)
    elif len(chair_back) == 1 and len(chair_front) >= 2 and check_mode >= 2:
        chair_keep = chair_back[0]
        chair_size = [abs(chair_keep['size'][i] * chair_keep['scale'][i]) / 100 for i in range(3)]
        chair_copy = []
        for chair_one in chair_front:
            width_dlt = abs(chair_one['normal_position'][0] - chair_keep['normal_position'][0])
            if width_dlt > chair_size[0] * 0.75:
                chair_copy.append(chair_one)
    for obj_one in chair_copy:
        object_new = copy_object(obj_one)
        object_new['position'][2] = -obj_one['position'][2]
        object_ang = rot_to_ang(obj_one['rotation']) + math.pi
        object_new['rotation'] = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
        object_new['normal_position'] = object_new['position'][:]
        object_new['normal_rotation'] = object_new['rotation'][:]
        if len(obj_list) >= 2:
            obj_list.insert(1, object_new)
        else:
            obj_list.append(object_new)

    # 功能区域 纠正家具
    obj_list = group_one['obj_list']
    if group_type == 'Meeting' and len(table_main) <= 0:
        for obj_one in obj_list:
            if obj_one['role'] in ['side sofa']:
                obj_pos, obj_rot = obj_one['normal_position'], obj_one['normal_rotation']
                obj_size = [abs(obj_one['size'][i] * obj_one['scale'][i]) / 100 for i in range(3)]
                if max(-size_main[0] / 2, -1) < obj_pos[0] < min(size_main[0] / 2, 1) and obj_pos[2] > 0.5:
                    if obj_size[0] + obj_size[2] > 1 and obj_size[1] < 1 and len(table_main) <= 0:
                        obj_one['role'] = 'table'
                        table_main = obj_one
                        continue
                elif obj_pos[2] < -size_main[2] / 2 + obj_size[2]:
                    if obj_size[0] < 1 and obj_size[2] < 1 and obj_size[1] < 1:
                        obj_one['role'] = 'side table'
                        table_main = obj_one
                        continue
    # 功能区域 碰撞家具
    if group_type == 'Meeting' and len(table_main) > 0:
        mid_pos, mid_rot = table_main['normal_position'], table_main['normal_rotation']
        mid_ang = rot_to_ang(mid_rot)
        mid_size = [abs(table_main['size'][i] * table_main['scale'][i]) / 100 for i in range(3)]
        mid_width, mid_depth = mid_size[0], mid_size[2]
        if abs(mid_ang - math.pi / 2) < 0.01 or abs(mid_ang + math.pi / 2) < 0.01:
            mid_width, mid_depth = mid_size[2], mid_size[0]
        for obj_idx in range(len(obj_list) - 1, -1, -1):
            obj_one = obj_list[obj_idx]
            if obj_one['role'] in ['side sofa']:
                obj_pos, obj_rot = obj_one['normal_position'], obj_one['normal_rotation']
                obj_ang = rot_to_ang(obj_rot)
                obj_size = [abs(obj_one['size'][i] * obj_one['scale'][i]) / 100 for i in range(3)]
                obj_width, obj_depth = obj_size[2], obj_size[0]
                if abs(obj_ang) < 0.01 or abs(obj_ang - math.pi) < 0.01 or abs(obj_ang + math.pi) < 0.01:
                    obj_width, obj_depth = obj_size[0], obj_size[2]
                # 距离判断
                obj_dis = [obj_pos[0] - mid_pos[0], obj_pos[1] - mid_pos[1], obj_pos[2] - mid_pos[2]]
                dis_x, dis_z = obj_dis[0], obj_dis[2]
                min_x, min_z = (mid_width + obj_width) / 2, (mid_depth + obj_depth) / 2
                if abs(dis_x) < min_x - 0.1 and abs(dis_z) < min_z - 0.1:
                    group_one['obj_list'].pop(obj_idx)
                    break
    # 功能区域 靠墙家具
    if group_type == 'Bath' and len(obj_list) > 1:
        shift_pos = 0
        for obj_one in obj_list:
            if obj_one['role'] == 'screen':
                obj_size = [obj_one['size'][i] * obj_one['scale'][i] / 100 for i in range(3)]
                obj_position = obj_one['normal_position']
                if abs(obj_position[0]) > 0.2 and obj_position[2] - obj_size[0] / 2 < -size_main[2] / 2:
                    shift_new = obj_size[0] / 2 - obj_position[2] - size_main[2] / 2
                    if shift_pos < shift_new < 0.2:
                        shift_pos = shift_new
        for obj_one in obj_list:
            if obj_one['role'] == 'screen':
                obj_one['normal_position'][2] += shift_pos

    # 计算编码
    group_type = group_one['type']
    group_rule = GROUP_RULE_FUNCTIONAL[group_type]
    role_list = group_rule['sequence']
    role_count = [0] * len(role_list)
    lamp_count = 0
    for obj_one in group_one['obj_list']:
        role_one = obj_one['role']
        if role_one in role_list:
            role_count[role_list.index(role_one)] += 1
        elif role_one in ['lamp']:
            lamp_count += 1
    if group_type in ['Rest'] and role_count[0] == 0 and lamp_count > 0:
        role_count[0] = lamp_count
    group_code = 0
    for count_one in role_count:
        if count_one >= 10:
            count_one = 9
        group_code *= 10
        group_code += count_one
    group_one['code'] = group_code
    if len(group_one['obj_list']) > 0:
        group_one['obj_main'] = group_one['obj_list'][0]['id']
        group_one['obj_type'] = group_one['obj_list'][0]['type']


# 数据解析：解析提取装饰打组
def extract_furniture_decor(furniture_list, room_type=''):
    # 打组信息
    group_list_final = []
    group_wall, group_ceil, group_floor, group_window, group_background = {}, {}, {}, {}, {}
    for rule_type in GROUP_RULE_DECORATIVE.keys():
        group_one = {
            'type': rule_type,
            'style': '',
            'code': 1,
            'size': [1, 1, 1],
            'obj_main': '',
            'obj_type': '',
            'obj_list': [],
            'mat_list': []
        }
        group_list_final.append(group_one)
        if group_one['type'] == 'Wall':
            group_wall = group_one
        elif group_one['type'] == 'Ceiling':
            group_ceil = group_one
        elif group_one['type'] == 'Floor':
            group_floor = group_one
        elif group_one['type'] == 'Window':
            group_window = group_one
        elif group_one['type'] == 'Background':
            group_background = group_one
    # 依附信息
    attach_todo = []
    # 遍历家具
    for furniture_idx in range(len(furniture_list) - 1, -1, -1):
        furniture_one = furniture_list[furniture_idx]
        furniture_type = furniture_one['type']
        furniture_size = [abs(furniture_one['size'][i] * furniture_one['scale'][i]) / 100 for i in range(3)]
        furniture_pos = furniture_one['position']
        # 打组查找
        suit_type = ''
        for rule_type, rule_info in GROUP_RULE_DECORATIVE.items():
            if furniture_type in rule_info:
                suit_type = rule_type
                break
        # 打组纠错
        if suit_type == '':
            if furniture_type in ['shelf/book shelf', 'customized content/customized platform']:
                if furniture_size[2] < 0.1 and furniture_size[0] > 0.8 and furniture_pos[1] <= 0.2:
                    suit_type = 'Background'
        if suit_type == '':
            continue
        # 位置判断
        if suit_type in ['Wall']:
            if furniture_pos[1] <= 0.20:
                if furniture_size[1] >= 5:
                    continue
                elif 'cabinet' in furniture_type:
                    suit_type = 'Floor'
                else:
                    suit_type = 'Floor'
        elif suit_type in ['Floor']:
            if furniture_pos[1] >= 0.15:
                if furniture_type in ['accessory/accessory - on top of others']:
                    if furniture_size[1] > UNIT_HEIGHT_SHELF_MIN and furniture_pos[1] < 0.8:
                        suit_type = 'Floor'
                    else:
                        attach_todo.append(furniture_one)
                        continue
                elif furniture_type in ['plants/plants - on top of others']:
                    attach_todo.append(furniture_one)
                    continue
                else:
                    continue
        elif suit_type in ['Window']:
            if 'curtain' in furniture_type:
                pass
        # 打组添加
        group_find = False
        for group_one in group_list_final:
            if group_one['type'] == suit_type:
                group_find = True
                break
        if not group_find:
            # 打组信息
            group_one = {
                'type': suit_type,
                'style': '',
                'code': 1,
                'size': [0, 0, 0],
                'obj_list': []
            }
            group_list_final.append(group_one)
        # 物品判断
        obj_exist, obj_style = False, False
        for obj_old in group_one['obj_list']:
            if obj_old['id'] == furniture_one['id'] and suit_type in ['Ceiling'] and furniture_size[1] <= 0.1:
                obj_old['count'] += 1
                obj_exist = True
                break
            size_old = obj_old['size']
            size_new = furniture_one['size']
            size_score_old = abs(size_old[0]) + abs(size_old[1]) + abs(size_old[2])
            size_score_new = abs(size_new[0]) + abs(size_new[1]) + abs(size_new[2])
            if size_score_new > size_score_old:
                obj_style = True
        # 角色判断
        furniture_role = furniture_type
        furniture_type_split = furniture_type.split('/')
        if len(furniture_type_split) > 1:
            furniture_role = furniture_type_split[0]
        else:
            furniture_type_split = furniture_type.split(' ')
            if len(furniture_type_split) > 1:
                furniture_role = furniture_type_split[-1]
        if 'door' in furniture_role:
            furniture_role = 'door'
        elif 'window' in furniture_role:
            furniture_role = 'window'
        # 信息更新
        furniture_one['scale'] = [abs(furniture_one['scale'][i]) for i in range(3)]
        furniture_one['group'] = suit_type
        furniture_one['role'] = furniture_role
        furniture_one['count'] = 1
        furniture_one['relate'] = ''
        furniture_one['relate_group'] = ''
        furniture_one['relate_position'] = []
        if not obj_exist:
            group_one['code'] += 1
            if furniture_type in GROUP_PLAT_WALL:
                group_one['obj_list'].insert(0, furniture_one)
            else:
                group_one['obj_list'].append(furniture_one)
            furniture_list.pop(furniture_idx)
        if obj_style:
            group_one['style'] = furniture_one['style']

    # 依附信息
    attach_wall, attach_rest = [], []
    if 'obj_list' in group_wall:
        attach_wall = group_wall['obj_list']
    for obj_idx, obj_old in enumerate(attach_wall):
        obj_pos = obj_old['position']
        obj_size = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
        if obj_old['type'] in GROUP_PLAT_WALL:
            continue
        for plat_one in group_wall['obj_list']:
            plat_pos, plat_rot = plat_one['position'], plat_one['rotation']
            plat_ang = rot_to_ang(plat_one['rotation'])
            plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
            if plat_one['type'] in GROUP_PLAT_WALL:
                plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
                # 垂直距离
                if plat_dis[1] >= plat_size[1] + 0.05 or plat_dis[1] < -obj_size[1] - 0.05:
                    continue
                # 水平距离
                ang = -plat_ang
                dis_x = plat_dis[2] * math.sin(ang) + plat_dis[0] * math.cos(ang)
                dis_z = plat_dis[2] * math.cos(ang) - plat_dis[0] * math.sin(ang)
                if abs(dis_x) >= plat_size[0] / 2:
                    continue
                if abs(dis_z) >= plat_size[2] / 2:
                    continue
                # 相关处理
                furniture_one = obj_old
                furniture_one['scale'] = [abs(furniture_one['scale'][i]) for i in range(3)]
                furniture_one['relate'] = plat_one['id']
                furniture_one['relate_group'] = ''
                furniture_one['relate_position'] = plat_one['position'][:]
                furniture_one['relate_rotation'] = plat_one['rotation'][:]
                break
    for obj_idx, obj_old in enumerate(attach_todo):
        obj_type, obj_pos = obj_old['type'], obj_old['position']
        obj_size = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
        for plat_one in group_wall['obj_list']:
            plat_pos, plat_rot, plat_ang = plat_one['position'], plat_one['rotation'], rot_to_ang(plat_one['rotation'])
            plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
            if plat_one['type'] in GROUP_PLAT_WALL:
                plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
                # 垂直距离
                if plat_dis[1] >= plat_size[1] + 0.05 or plat_dis[1] < -obj_size[1] / 2 - 0.05:
                    continue
                # 水平距离
                ang = -plat_ang
                dis_x = plat_dis[2] * math.sin(ang) + plat_dis[0] * math.cos(ang)
                dis_z = plat_dis[2] * math.cos(ang) - plat_dis[0] * math.sin(ang)
                if abs(dis_x) >= plat_size[0] / 2:
                    continue
                if abs(dis_z) >= plat_size[2] / 2:
                    continue
                # 相关处理
                furniture_one = obj_old
                furniture_one['scale'] = [abs(furniture_one['scale'][i]) for i in range(3)]
                furniture_one['role'] = obj_old['type'].split('/')[0]
                furniture_one['count'] = 1
                furniture_one['relate'] = plat_one['id']
                furniture_one['relate_group'] = ''
                furniture_one['relate_position'] = plat_one['position'][:]
                furniture_one['relate_rotation'] = plat_one['rotation'][:]
                group_wall['code'] += 1
                group_wall['obj_list'].append(furniture_one)
                break
        for plat_one in group_floor['obj_list']:
            plat_pos, plat_rot, plat_ang = plat_one['position'], plat_one['rotation'], rot_to_ang(plat_one['rotation'])
            plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
            if plat_pos[1] < 0.1:
                plat_dis = [obj_pos[0] - plat_pos[0], obj_pos[1] - plat_pos[1], obj_pos[2] - plat_pos[2]]
                # 垂直距离
                if plat_dis[1] >= plat_size[1] + 0.05 or plat_dis[1] < -obj_size[1] / 2 - 0.05:
                    continue
                # 水平距离
                ang = -plat_ang
                dis_x = plat_dis[2] * math.sin(ang) + plat_dis[0] * math.cos(ang)
                dis_z = plat_dis[2] * math.cos(ang) - plat_dis[0] * math.sin(ang)
                if abs(dis_x) >= plat_size[0] / 2:
                    continue
                if abs(dis_z) >= plat_size[2] / 2:
                    continue
                # 相关处理
                furniture_one = obj_old
                furniture_one['scale'] = [abs(furniture_one['scale'][i]) for i in range(3)]
                furniture_one['role'] = obj_old['type'].split('/')[0]
                furniture_one['count'] = 1
                furniture_one['relate'] = plat_one['id']
                furniture_one['relate_group'] = ''
                furniture_one['relate_position'] = plat_one['position'][:]
                furniture_one['relate_rotation'] = plat_one['rotation'][:]
                group_floor['code'] += 1
                group_floor['obj_list'].append(furniture_one)
                break
        if 'relate' in obj_old and obj_old['relate'] == '':
            attach_rest.append(obj_old)
    for obj_idx, obj_old in enumerate(attach_rest):
        if len(attach_rest) >= 5 and room_type in ['Library']:
            break
        elif len(attach_rest) >= 3:
            break
        obj_type, obj_pos = obj_old['type'], obj_old['position']
        if obj_type in ['plants/plants - on top of others']:
            obj_size = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
            if obj_pos[1] > 1.0 and obj_size[2] < 0.1:
                group_wall['obj_list'].append(obj_old)
            elif min(obj_size[0], obj_size[1], obj_size[2]) > 0.1:
                obj_pos[1] = 0.0
                group_floor['obj_list'].append(obj_old)
        elif obj_type in ['accessory/accessory - on top of others']:
            obj_size = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
            if obj_pos[1] > 1.0 and obj_size[2] < 0.1:
                group_wall['obj_list'].append(obj_old)
            elif min(obj_size[0], obj_size[1], obj_size[2]) > 0.1:
                obj_pos[1] = 0.0
                group_floor['obj_list'].append(obj_old)

    # 组合挂画 TODO:
    art_list, art_dict = [], {}
    if 'obj_list' in group_wall:
        object_list = group_wall['obj_list']
        for obj_idx, obj_old in enumerate(object_list):
            if 'lamp' in obj_old['type'] or 'cabinet' in obj_old['type']:
                continue
            else:
                art_list.append(obj_old)
    for obj_idx, obj_old in enumerate(art_list):
        obj_pos, obj_ang = obj_old['position'], rot_to_ang(obj_old['rotation'])
        int_pos, int_ang = 0, 0
        if abs(obj_ang) < 0.1 or abs(obj_ang - math.pi) < 0.1 or abs(obj_ang + math.pi) < 0.1:
            int_pos, int_ang = int(obj_pos[2] * 100), 0
        elif abs(obj_ang - math.pi / 2) < 0.1 or abs(obj_ang + math.pi / 2) < 0.1:
            int_pos, int_ang = int(obj_pos[0] * 100), 90
        else:
            int_pos, int_ang = 0, int(obj_ang * 180 / math.pi / 10) * 10
        obj_key = '%d_%d' % (int_pos, int_ang)
        for old_key, old_val in art_dict.items():
            old_ang = int(old_key.split('_')[0])
            old_pos = int(old_key.split('_')[-1])
            if abs(old_ang - int_ang) <= 10 and abs(old_pos - int_pos) <= 20:
                obj_key = old_key
                break
        if obj_key not in art_dict:
            art_dict[obj_key] = [obj_old]
        else:
            art_dict[obj_key].append(obj_old)
    # 组合灯饰
    light_list, light_dict = [], {}
    if 'obj_list' in group_ceil:
        object_list = group_ceil['obj_list']
        for obj_idx, obj_old in enumerate(object_list):
            if 'lighting' in obj_old['type']:
                light_list.append(obj_old)
    for obj_idx, obj_old in enumerate(light_list):
        obj_pos, obj_ang = obj_old['position'], rot_to_ang(obj_old['rotation'])
        obj_size = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
        obj_rat = obj_size[0] / obj_size[2]
        int_height = int(obj_size[1] * 100)
        int_pos_x, int_pos_z = int(obj_pos[0] * 100), int(obj_pos[2] * 100)
        obj_key = '%d_%d_%d' % (int_pos_x, int_pos_z, int_height)
        for old_key, old_val in light_dict.items():
            old_pos_x = int(old_key.split('_')[0])
            old_pos_z = int(old_key.split('_')[1])
            old_height = int(old_key.split('_')[-1])
            old_one = old_val[0]
            old_size = [abs(old_one['size'][i] * old_one['scale'][i]) / 100 for i in range(3)]
            old_rat = old_size[0] / old_size[2]
            dis_x, dis_z, dis_h = int_pos_x - old_pos_x, int_pos_z - old_pos_z, int_height - old_height
            if obj_rat > old_rat * 2.0 or obj_rat < old_rat * 0.5:
                pass
            elif max(abs(dis_x), abs(dis_z)) <= 100:
                if max(abs(dis_x), abs(dis_z)) > 50 and 'Bathroom' in room_type:
                    pass
                else:
                    obj_key = old_key
                    break
            elif max(abs(dis_x), abs(dis_z)) <= 200:
                if obj_size[0] > obj_size[2] * 10 or obj_size[2] > obj_size[0] * 10:
                    pass
                elif min(abs(dis_x), abs(dis_z)) < 50 and abs(dis_h) < 20:
                    obj_key = old_key
                    break
            elif obj_size[0] > max(obj_size[2] * 10, 1.0) and abs(obj_size[0] - old_size[0]) < 0.1:
                if max(abs(dis_x), abs(dis_z)) <= 300 and min(abs(dis_x), abs(dis_z)) < 30 and abs(dis_h) < 20:
                    obj_key = old_key
                    break
        if obj_key not in light_dict:
            light_dict[obj_key] = [obj_old]
        else:
            light_dict[obj_key].append(obj_old)

    # 组合绿植
    plant_list, plant_dict = [], {}
    if room_type in ['Balcony', 'Terrace', 'Lounge', 'Hallway', 'Aisle', 'Corridor', 'Stairwell']:
        if 'obj_list' in group_floor:
            object_list = group_floor['obj_list']
            for obj_idx, obj_old in enumerate(object_list):
                if 'type' in obj_old and 'plants' in obj_old['type']:
                    plant_list.append(obj_old)
    for obj_idx, obj_old in enumerate(plant_list):
        obj_pos, obj_ang = obj_old['position'], rot_to_ang(obj_old['rotation'])
        int_pos_x, int_pos_z = int(obj_pos[0] * 100), int(obj_pos[2] * 100)
        obj_key = '%d_%d' % (int_pos_x, int_pos_z)
        for old_key, old_val in plant_dict.items():
            old_pos_x = int(old_key.split('_')[0])
            old_pos_z = int(old_key.split('_')[-1])
            dis_x, dis_z = int_pos_x - old_pos_x, int_pos_z - old_pos_z
            if abs(dis_x) <= 100 and abs(dis_z) <= 100:
                obj_key = old_key
                break
        if obj_key not in plant_dict:
            plant_dict[obj_key] = [obj_old]
        else:
            plant_dict[obj_key].append(obj_old)
    # 组合平台
    table_list, table_dict = [], {}
    if room_type in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
        if 'obj_list' in group_floor:
            object_list = group_floor['obj_list']
            for obj_idx, obj_old in enumerate(object_list):
                object_size = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
                if 'type' in obj_old and 'sofa' in obj_old['type'] and object_size[1] < 1.0:
                    table_list.append(obj_old)
    for obj_idx, obj_old in enumerate(table_list):
        obj_pos, obj_ang = obj_old['position'], rot_to_ang(obj_old['rotation'])
        int_pos_x, int_pos_z = int(obj_pos[0] * 100), int(obj_pos[2] * 100)
        obj_key = '%d_%d' % (int_pos_x, int_pos_z)
        for old_key, old_val in table_dict.items():
            old_pos_x = int(old_key.split('_')[0])
            old_pos_z = int(old_key.split('_')[-1])
            if abs(int_pos_x - old_pos_x) <= 100 and abs(int_pos_z - old_pos_z) <= 100:
                obj_key = old_key
                break
        if obj_key not in table_dict:
            table_dict[obj_key] = [obj_old]
        else:
            table_dict[obj_key].append(obj_old)

    # 组合窗帘
    window_list, curtain_list, curtain_dict = [], [], {}
    if 'obj_list' in group_window:
        object_list = group_window['obj_list']
        for obj_idx, obj_old in enumerate(object_list):
            if 'curtain' in obj_old['type']:
                curtain_list.append(obj_old)
            else:
                window_list.append(obj_old)
    for obj_idx, obj_old in enumerate(curtain_list):
        obj_pos, obj_ang = obj_old['position'], rot_to_ang(obj_old['rotation'])
        int_pos, int_ang = 0, 0
        if abs(obj_ang) < 0.1 or abs(obj_ang - math.pi) < 0.1 or abs(obj_ang + math.pi) < 0.1:
            int_pos, int_ang = int(obj_pos[2] * 100), 0
        elif abs(obj_ang - math.pi / 2) < 0.1 or abs(obj_ang + math.pi / 2) < 0.1:
            int_pos, int_ang = int(obj_pos[0] * 100), 90
        else:
            int_pos, int_ang = 0, int(obj_ang * 180 / math.pi / 10) * 10
        obj_key = '%d_%d' % (int_pos, int_ang)
        for old_key, old_val in curtain_dict.items():
            old_ang = int(old_key.split('_')[0])
            old_pos = int(old_key.split('_')[-1])
            if abs(old_ang - int_ang) <= 10 and abs(old_pos - int_pos) <= 20:
                obj_key = old_key
                break
        if obj_key not in curtain_dict:
            curtain_dict[obj_key] = [obj_old]
        else:
            curtain_list = curtain_dict[obj_key]
            find_idx = -1
            for curtain_idx, curtain_one in enumerate(curtain_list):
                pos_1, pos_2 = obj_old['position'], curtain_one['position']
                if pos_1[0] + pos_1[2] < pos_2[0] + pos_2[2]:
                    find_idx = curtain_idx
                    break
            if find_idx <= -1:
                curtain_list.append(obj_old)
            else:
                curtain_list.insert(find_idx, obj_old)
            curtain_dict[obj_key] = curtain_list
    curtain_side = {}
    for obj_key, obj_set in curtain_dict.items():
        if len(obj_set) < 2:
            continue
        obj_1, obj_2, obj_3, obj_4 = obj_set[0], obj_set[1], obj_set[-2], obj_set[-1]
        if obj_1['id'] == obj_3['id'] and not obj_4['id'] == obj_3['id']:
            if abs(abs(obj_4['size'][0] * obj_4['scale'][0]) - abs(obj_3['size'][0] * obj_3['scale'][0])) > 0.1:
                curtain_side[obj_key + '_right'] = [obj_4]
                obj_set.remove(obj_4)
        elif obj_4['id'] == obj_2['id'] and not obj_1['id'] == obj_2['id']:
            if abs(abs(obj_1['size'][0] * obj_1['scale'][0]) - abs(obj_2['size'][0] * obj_2['scale'][0])) > 0.1:
                curtain_side[obj_key + '_left'] = [obj_1]
                obj_set.remove(obj_1)
        elif abs(obj_1['position'][1] - obj_3['position'][1]) <= 0.1 and abs(obj_4['position'][1] - obj_3['position'][1]) >= 0.2:
            curtain_side[obj_key + '_right'] = [obj_4]
            obj_set.remove(obj_4)
        elif abs(obj_4['position'][1] - obj_2['position'][1]) <= 0.1 and abs(obj_1['position'][1] - obj_2['position'][1]) >= 0.2:
            curtain_side[obj_key + '_left'] = [obj_1]
            obj_set.remove(obj_1)
    for obj_key, obj_set in curtain_side.items():
        curtain_dict[obj_key] = obj_set
    # 组合背景
    background_list, background_dict = [], {}
    if 'obj_list' in group_background:
        object_list = group_background['obj_list']
        for obj_idx, obj_old in enumerate(object_list):
            background_list.append(obj_old)
    for obj_idx, obj_old in enumerate(background_list):
        obj_pos, obj_ang = obj_old['position'], rot_to_ang(obj_old['rotation'])
        int_pos, int_ang = 0, 0
        if abs(obj_ang) < 0.1 or abs(obj_ang - math.pi) < 0.1 or abs(obj_ang + math.pi) < 0.1:
            int_pos, int_ang = int(obj_pos[2] * 100), 0
        elif abs(obj_ang - math.pi / 2) < 0.1 or abs(obj_ang + math.pi / 2) < 0.1:
            int_pos, int_ang = int(obj_pos[0] * 100), 90
        else:
            int_pos, int_ang = 0, int(obj_ang * 180 / math.pi / 10) * 10
        obj_key = '%d_%d' % (int_pos, int_ang)
        for old_key, old_val in background_dict.items():
            old_ang = int(old_key.split('_')[0])
            old_pos = int(old_key.split('_')[-1])
            if abs(old_ang - int_ang) <= 10 and abs(old_pos - int_pos) <= 20:
                obj_key = old_key
                break
        if obj_key not in background_dict:
            background_dict[obj_key] = [obj_old]
        else:
            background_dict[obj_key].append(obj_old)

    # 级联检查
    for link_dict in [light_dict, plant_dict, table_dict, curtain_dict, background_dict]:
        # 级联分组
        link_group, link_role = {}, ''
        if link_dict == light_dict:
            link_group, link_role = group_ceil, 'ceiling'
        elif link_dict == plant_dict:
            link_group, link_role = group_floor, 'floor'
        elif link_dict == table_dict:
            link_group, link_role = group_floor, 'floor'
        elif link_dict == curtain_dict:
            link_group, link_role = group_window, 'curtain'
        elif link_dict == background_dict:
            link_group, link_role = group_background, 'background'
        # 级联生成
        attach_todo, attach_dump, attach_diff, attach_near = [], [], 0, 5
        for obj_key, obj_val in link_dict.items():
            if len(obj_val) <= 1:
                continue
            # 最大
            obj_max, size_max, pos_max, ang_max = {}, [], [], 0
            for obj_old in obj_val:
                size_old = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
                if len(obj_max) <= 0:
                    obj_max = obj_old
                    size_max = size_old
                elif size_old[0] + size_old[2] > size_max[0] + size_max[2]:
                    obj_max = obj_old
                    size_max = size_old
            if len(obj_max) > 0 and len(size_max) > 0:
                pos_max = obj_max['position']
                ang_max = rot_to_ang(obj_max['rotation'])
            # 校正
            if link_dict == curtain_dict:
                if size_max[1] > UNIT_HEIGHT_OBJECT:
                    size_max[1] = UNIT_HEIGHT_OBJECT
                for obj_old in obj_val:
                    size_old = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
                    size_rat = 1
                    if size_old[1] > size_max[1] or 0.8 < abs(size_old[1] / size_max[1]) < 1.2:
                        size_rat = size_max[1] / size_old[1]
                    obj_old['scale'][1] *= size_rat
                if room_type in ['Balcony', 'Terrace']:
                    attach_near = 10
            # 偏移
            obj_set = []
            min_x, min_y, min_z = 100, 100, 100
            max_x, max_y, max_z = -100, -100, -100
            min_dlt, max_dlt = 0.25, 0.50
            if link_dict == light_dict:
                min_dlt, max_dlt = 0.50, 1.00
            for obj_old in obj_val:
                size_old = [abs(obj_old['size'][i] * obj_old['scale'][i]) / 100 for i in range(3)]
                pos_one = obj_old['position']
                ang_one = rot_to_ang(obj_old['rotation'])
                if obj_old == obj_max:
                    obj_set.append(obj_old)
                elif len(pos_max) > 0:
                    pos_dlt_x = abs(pos_one[0] - pos_max[0])
                    pos_dlt_y = abs(pos_one[1] - pos_max[1])
                    pos_dlt_z = abs(pos_one[2] - pos_max[2])
                    if min(size_max[0], size_old[0]) >= 2.5 and max(pos_dlt_x, pos_dlt_z) <= attach_near:
                        if min(pos_dlt_x, pos_dlt_z) < min_dlt:
                            obj_set.append(obj_old)
                        elif max(pos_dlt_x, pos_dlt_z) <= max_dlt:
                            obj_set.append(obj_old)
                    elif size_old[0] < 2.5 and max(pos_dlt_x, pos_dlt_z) <= attach_near:
                        if min(pos_dlt_x, pos_dlt_z) < min_dlt:
                            obj_set.append(obj_old)
                        elif max(pos_dlt_x, pos_dlt_z) <= max_dlt:
                            obj_set.append(obj_old)
                    else:
                        continue
                pos_old_x = pos_one[0] - pos_max[0]
                pos_old_y = pos_one[1]
                pos_old_z = pos_one[2] - pos_max[2]
                pos_new_x = pos_old_z * math.sin(-ang_max) + pos_old_x * math.cos(-ang_max)
                pos_new_z = pos_old_z * math.cos(-ang_max) - pos_old_x * math.sin(-ang_max)
                pos_new_x_1, pos_new_x_2 = pos_new_x - size_old[0] / 2, pos_new_x + size_old[0] / 2
                pos_new_z_1, pos_new_z_2 = pos_new_z - size_old[2] / 2, pos_new_z + size_old[2] / 2
                min_x = min(pos_new_x_1, pos_new_x_2, min_x)
                max_x = max(pos_new_x_1, pos_new_x_2, max_x)
                min_z = min(pos_new_z_1, pos_new_z_2, min_z)
                max_z = max(pos_new_z_1, pos_new_z_2, max_z)
                min_y = min(pos_old_y, min_y)
                max_y = max(pos_old_y + size_old[1], max_y)
            if len(obj_set) <= 1 or len(obj_max) <= 0:
                continue
            # 生成
            obj_new = copy_object(obj_max)
            attach_diff += 1
            obj_size_new = [(max_x - min_x) * 100, abs(obj_max['size'][1] * obj_max['scale'][1]), (max_z - min_z) * 100]
            obj_scale_new = [1, 1, 1]
            tmp_x, tmp_z = (max_x + min_x) / 2, (max_z + min_z) / 2
            add_x = tmp_z * math.sin(ang_max) + tmp_x * math.cos(ang_max)
            add_z = tmp_z * math.cos(ang_max) - tmp_x * math.sin(ang_max)
            obj_pos_new = [pos_max[0] + add_x, pos_max[1], pos_max[2] + add_z]
            obj_rot_new = [0, math.sin(ang_max / 2), 0, math.cos(ang_max / 2)]
            obj_new['size'] = obj_size_new
            obj_new['scale'] = obj_scale_new
            obj_new['position'] = obj_pos_new
            obj_new['rotation'] = obj_rot_new
            fake_id = 'link_%d_' % attach_diff + obj_max['id']
            obj_new['fake_id'] = fake_id
            for obj_old in obj_set:
                obj_old['relate'] = fake_id
                obj_old['relate_role'] = link_role
                obj_old['relate_position'] = obj_pos_new[:]
                obj_old['relate_rotation'] = obj_rot_new[:]
            attach_todo.append(obj_new)
        # 级联添加
        if 'obj_list' in link_group:
            for obj_idx, obj_add in enumerate(attach_todo):
                link_group['obj_list'].insert(0, obj_add)
    # 返回信息
    return group_list_final


# 数据解析：解析提取相关家具
def extract_furniture_relate(group_one, group_list, room_type='', room_mirror=0):
    if len(group_list) <= 0:
        return
    group_type = group_one['type']
    object_list = group_one['obj_list']
    # 家具相关
    lamp_left, lamp_right, lamp_group = [], [], ''
    for object_idx, object_one in enumerate(object_list):
        if group_type not in ['Wall', 'Ceiling', 'Floor', 'Background']:
            break
        if 'relate' in object_one and not object_one['relate'] == '':
            continue
        if 'count' in object_one and object_one['count'] > 1:
            continue
        object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
        object_pos = object_one['position']
        object_rot = object_one['rotation']
        object_ang = rot_to_ang(object_rot)
        for group_old in group_list:
            if group_old['type'] not in GROUP_TYPE_RELATE:
                continue
            if group_old['type'] in ['Bath'] and group_type in ['Ceiling']:
                continue
            if group_old['type'] in ['Toilet'] and group_type in ['Ceiling']:
                continue
            if group_old['type'] in ['Cabinet', 'Appliance'] and group_type in ['Ceiling']:
                continue
            if group_type in ['Wall']:
                relate_for_x, relate_for_z = 0.0, 0.5
                relate_min_x, relate_min_z = 1.5, 0.1
            elif group_type in ['Ceiling']:
                relate_for_x, relate_for_z = 0.0, 0.0
                relate_min_x, relate_min_z = 1.0, 1.0
            elif group_type in ['Floor']:
                relate_for_x, relate_for_z = 0.5, 0.5
                relate_min_x, relate_min_z = 1.0, 1.0
            elif group_type in ['Background']:
                relate_for_x, relate_for_z = 0.0, 0.5
                relate_min_x, relate_min_z = 0.5, 0.1
            else:
                continue
            # 主要信息
            main_info = group_old['obj_list'][0]
            main_type, main_role = main_info['type'], main_info['role']
            main_size = [abs(main_info['size'][i] * main_info['scale'][i]) / 100 for i in range(3)]
            main_pos, main_rot = main_info['origin_position'], main_info['origin_rotation']
            main_ang = rot_to_ang(main_rot)
            # 纠正信息
            pos_adjust = [0 - main_pos[0], 0 - main_pos[1], 0 - main_pos[2]]
            ang_adjust = 0 - main_ang
            # 纠正位置
            pos_old_x = object_pos[0] + pos_adjust[0]
            pos_old_z = object_pos[2] + pos_adjust[2]
            pos_new_x = pos_old_z * math.sin(ang_adjust) + pos_old_x * math.cos(ang_adjust)
            pos_new_y = object_pos[1]
            pos_new_z = pos_old_z * math.cos(ang_adjust) - pos_old_x * math.sin(ang_adjust)
            # 纠正朝向
            ang_new = ang_to_ang(object_ang + ang_adjust)
            # 相关角度
            if group_old['type'] in ['Meeting']:
                if group_type in ['Wall']:
                    relate_min_x, relate_min_z = 1.0, 0.5
                    if object_one['type'] in ['art/art - wall-attached']:
                        relate_min_x, relate_min_z = 0.5, 0.5
                    if abs(ang_new) > 0.1:
                        continue
                elif group_type in ['Ceiling']:
                    if relate_min_z < main_size[2] / 2:
                        relate_min_z = main_size[2] / 2
                elif group_type in ['Floor']:
                    rest_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
                    if abs(ang_new - math.pi / 2) <= 0.01 or abs(ang_new + math.pi / 2) <= 0.01:
                        rest_half = rest_size[0] / 2
                    else:
                        rest_half = rest_size[2] / 2
                    if pos_new_z < -main_size[2] / 2 + rest_half - 0.02:
                        continue
            elif group_old['type'] in ['Bed']:
                if group_type in ['Wall']:
                    relate_min_x, relate_min_z = 1.0, 0.2
                    if object_one['type'] in ['art/art - wall-attached']:
                        relate_min_x, relate_min_z = 0.5, 0.2
                    if abs(ang_new + math.pi / 2) < 0.1 or abs(ang_new - math.pi / 2) < 0.1:
                        relate_for_x, relate_for_z = 0.5, 0.0
                        relate_min_x, relate_min_z = 0.2, 1.5
            elif group_old['type'] in ['Media']:
                if group_type in ['Wall']:
                    relate_min_x, relate_min_z = 2.0, 0.5
                elif group_type in ['Ceiling']:
                    if relate_min_z > main_size[2] / 2 + 0.1:
                        relate_min_z = main_size[2] / 2 + 0.1
            elif group_old['type'] in ['Dining']:
                if group_type in ['Wall']:
                    if abs(ang_new + math.pi / 2) < 0.1 or abs(ang_new - math.pi / 2) < 0.1:
                        relate_for_x, relate_for_z = 0.5, 0.0
                        relate_min_x, relate_min_z = 0.1, 1.5
                    else:
                        relate_for_x, relate_for_z = 0.0, 0.5
                        relate_min_x, relate_min_z = 0.5, 1.5
                elif group_type in ['Ceiling']:
                    if relate_min_x > main_size[0] / 2:
                        relate_min_x = main_size[0] / 2
                    if relate_min_z > main_size[2] / 2:
                        relate_min_z = main_size[2] / 2
            elif group_old['type'] in ['Armoire', 'Cabinet', 'Rest']:
                if group_type in ['Wall']:
                    relate_min_x, relate_min_z = 0.3, 0.3
                    if abs(ang_new) > 0.1:
                        continue
            # 相关距离
            if abs(pos_new_x) <= main_size[0] * 0.5:
                relate_dlt_x = abs(pos_new_x + 0 * main_size[0])
            elif pos_new_x <= 0:
                relate_dlt_x = abs(pos_new_x + relate_for_x * main_size[0])
            else:
                relate_dlt_x = abs(pos_new_x - relate_for_x * main_size[0])
            if pos_new_z <= 0:
                relate_dlt_z = abs(pos_new_z + relate_for_z * main_size[2])
                if group_type in ['Wall']:
                    relate_dlt_z = abs(pos_new_z + relate_for_z * main_size[2] - 0.5 * object_size[2])
            else:
                relate_dlt_z = abs(pos_new_z - relate_for_z * main_size[2])
                if group_type in ['Wall']:
                    relate_dlt_z = abs(pos_new_z - relate_for_z * main_size[2] + 0.5 * object_size[2])
            # 相关尺寸
            relate_size = True
            if group_type in ['Wall'] and main_role in ['sofa', 'bed']:
                if object_size[2] > 0.4 and object_size[0] + object_size[1] > 1.0:
                    relate_size = False
            # 相关装饰
            if relate_dlt_x < relate_min_x and relate_dlt_z < relate_min_z and relate_size:
                # 相关家具
                object_one['relate'] = main_info['id']
                object_one['relate_role'] = main_role
                object_one['relate_group'] = group_old['type']
                object_one['relate_position'] = main_pos[:]
                # 位置朝向
                object_one['origin_position'] = object_pos[:]
                object_one['origin_rotation'] = object_rot[:]
                object_one['normal_position'] = [pos_new_x, pos_new_y, pos_new_z]
                object_one['normal_rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]
                # 镜像处理
                if room_mirror == 1 and main_type in SOFA_CORNER_TYPE_0:
                    object_one['normal_position'] = [-pos_new_x, pos_new_y, pos_new_z]
                # 对称壁灯
                if 'wall lamp' in object_one['type']:
                    if pos_new_x < 0:
                        lamp_left.append(object_one)
                        lamp_group = group_old['type']
                    elif pos_new_x > 0:
                        lamp_right.append(object_one)
                        lamp_group = group_old['type']
                break
    # 壁灯纠错
    lamp_good = True
    if len(lamp_left) >= 1 and len(lamp_right) <= 0 and lamp_group in ['Meeting', 'Bed', 'Media']:
        lamp_good = False
    elif len(lamp_left) <= 0 and len(lamp_right) >= 1 and lamp_group in ['Meeting', 'Bed', 'Media']:
        lamp_good = False
    if not lamp_good:
        for object_one in lamp_left:
            object_one['relate'] = ''
            object_one['relate_role'] = ''
            object_one['relate_group'] = ''
            object_one['relate_position'] = []
        for object_one in lamp_right:
            object_one['relate'] = ''
            object_one['relate_role'] = ''
            object_one['relate_group'] = ''
            object_one['relate_position'] = []
    # 装饰相关
    wall_wait, floor_wait = [], []
    for object_idx, object_one in enumerate(group_one['obj_list']):
        if 'count' in object_one and object_one['count'] > 1:
            continue
        if 'relate' in object_one and not object_one['relate'] == '':
            continue
        if group_type in ['Wall']:
            wall_wait.append(object_one)
        elif group_type in ['Floor']:
            floor_wait.append(object_one)
    for object_old in wall_wait:
        if 'relate' in object_old and not object_old['relate'] == '':
            continue
        size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
        pos_old, rot_old = object_old['position'], object_old['rotation']
        ang_old = rot_to_ang(object_old['rotation'])
        for object_new in wall_wait:
            if object_old == object_new:
                continue
            if 'relate' in object_new and not object_new['relate'] == '':
                continue
            size_new = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
            pos_new, rot_new = object_new['position'], object_new['rotation']
            ang_new = rot_to_ang(object_new['rotation'])
            # 位置判断
            main_one, object_one = {}, {}
            pos_dlt = [(pos_old[i] - pos_new[i]) for i in range(3)]
            if max(abs(pos_dlt[0]), abs(pos_dlt[2])) < size_new[0] and pos_dlt[1] > 0:
                main_one, main_size = object_new, size_new
                main_pos, main_rot, main_ang = pos_new, rot_new, ang_new
                object_one = object_old
                object_pos, object_rot, object_ang = pos_old, rot_old, ang_old
            elif max(abs(pos_dlt[0]), abs(pos_dlt[2])) < size_old[0] and pos_dlt[1] < 0:
                main_one, main_size = object_old, size_old
                main_pos, main_rot, main_ang = pos_old, rot_old, ang_old
                object_one = object_new
                object_pos, object_rot, object_ang = pos_new, rot_new, ang_new
            else:
                continue
            if len(main_one) > 0 and len(object_one) > 0:
                # 纠正信息
                pos_adjust = [0 - main_pos[0], 0 - main_pos[1], 0 - main_pos[2]]
                ang_adjust = 0 - main_ang
                # 纠正位置
                pos_old_x = object_pos[0] + pos_adjust[0]
                pos_old_z = object_pos[2] + pos_adjust[2]
                pos_new_x = pos_old_z * math.sin(ang_adjust) + pos_old_x * math.cos(ang_adjust)
                pos_new_y = object_pos[1]
                pos_new_z = pos_old_z * math.cos(ang_adjust) - pos_old_x * math.sin(ang_adjust)
                # 纠正朝向
                ang_new = ang_to_ang(object_ang + ang_adjust)
                if abs(pos_new_x) < main_size[0] / 2 and abs(pos_new_z) < main_size[2] / 2:
                    object_one['relate'] = main_one['id']
                    object_one['relate_position'] = main_pos[:]
                    object_one['relate_rotation'] = main_rot[:]
                    object_one['relate_role'] = ''
                    object_one['relate_group'] = ''
                    # 位置朝向
                    object_one['origin_position'] = object_pos[:]
                    object_one['origin_rotation'] = object_rot[:]
                    object_one['normal_position'] = [pos_new_x, pos_new_y, pos_new_z]
                    object_one['normal_rotation'] = [0, math.sin(ang_new / 2), 0, math.cos(ang_new / 2)]


# 数据解析：检查更新组合参数
def extract_furniture_update(group_one):
    pass


# 数据解析：解析提取摆放参数
def extract_furniture_locate(plat_one, plat_size=[], group_one={}):
    plat_type = plat_one['type']
    if len(plat_size) < 3:
        plat_size = [abs(plat_one['size'][i] * plat_one['scale'][i]) / 100 for i in range(3)]
    # 餐桌角度
    table_main, table_type, table_size, chair_list, chair_angle = '', '', [], [], 0
    if len(group_one) > 0 and group_one['type'] == 'Dining':
        # 桌椅
        if 'obj_main' in group_one:
            table_main = group_one['obj_main']
        if 'obj_type' in group_one:
            table_type = group_one['obj_type']
        object_list = group_one['obj_list']
        for object_one in object_list:
            if 'role' in object_one and object_one['role'] == 'table':
                table_type = object_one['type']
                table_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
            elif 'role' in object_one and object_one['role'] == 'chair':
                chair_list.append(object_one)
        # 角度
        if len(chair_list) >= 4:
            # 解算
            dis_list, ang_list = [], []
            obj_list_0, obj_list_1, obj_list_2, obj_list_3 = [], [], [], []
            for object_one in chair_list:
                if 'normal_position' not in object_one:
                    continue
                object_pos = object_one['normal_position']
                object_dis, object_ang = xyz_to_ang(0, 0, object_pos[0], object_pos[2])
                dis_list.append(object_dis)
                ang_list.append(object_ang)
                x, z = object_pos[0], object_pos[2]
                if abs(x) < table_size[0] / 2 and abs(z) > table_size[2] / 2:
                    if z < 0:
                        obj_list_0.append(x)
                    else:
                        obj_list_2.append(x)
                elif abs(x) > table_size[0] / 2 and abs(z) < table_size[2] / 2:
                    if x < 0:
                        obj_list_1.append(z)
                    else:
                        obj_list_3.append(z)
            # 圆形
            if len(ang_list) >= 4:
                ang_list.sort()
                ang_list_dlt = [ang_to_ang(ang_list[i] - ang_list[i - 1]) for i in range(len(ang_list))]
                ang_min, ang_max = min(ang_list_dlt), max(ang_list_dlt)
                if abs(ang_max - ang_min) < math.pi / 5:
                    chair_angle = ang_list[0]
    # 摆放信息
    locate_param = []
    if len(locate_param) <= 0 and len(plat_size) >= 3:
        circle_flag = False
        if abs(plat_size[0] - plat_size[2]) < 0.05:
            circle_flag = True
        # 圆形
        if circle_flag:
            chair_count = 4
            if 2.0 < min(plat_size[0], plat_size[2]) < 2.5:
                chair_count = 6
            elif 2.5 <= min(plat_size[0], plat_size[2]):
                chair_count = 8
            locate_param = [chair_angle, chair_count]
        # 矩形
        else:
            if plat_size[0] > min(plat_size[2] + 0.5, plat_size[2] * 1.5):
                locate_param = [plat_size[0] - 0.6, 2, 0, 0]
                if plat_size[0] > 2:
                    locate_param = [plat_size[0] - 0.6, 3, 0, 0]
            elif plat_size[2] > min(plat_size[0] + 0.5, plat_size[0] * 1.5):
                locate_param = [0, 0, plat_size[2] - 0.6, 2]
                if plat_size[2] > 2:
                    locate_param = [0, 0, plat_size[2] - 0.6, 3]
            else:
                locate_param = [0, 1, 0, 1]
    # 返回信息
    return locate_param


# 数据拷贝
def copy_object(object_one):
    object_new = object_one.copy()
    object_new['size'] = object_one['size'][:]
    object_new['scale'] = object_one['scale'][:]
    object_new['position'] = object_one['position'][:]
    object_new['rotation'] = object_one['rotation'][:]
    if 'origin_position' in object_one:
        object_new['origin_position'] = object_one['origin_position'][:]
    if 'origin_rotation' in object_one:
        object_new['origin_rotation'] = object_one['origin_rotation'][:]
    if 'normal_position' in object_one:
        object_new['normal_position'] = object_one['normal_position'][:]
    if 'normal_rotation' in object_one:
        object_new['normal_rotation'] = object_one['normal_rotation'][:]
    if 'relate_position' in object_one:
        object_new['relate_position'] = object_one['relate_position'][:]
    if 'relate_shifting' in object_one:
        object_new['relate_shifting'] = object_one['relate_shifting'][:]
    return object_new


# 数据拷贝
def copy_object_by_id(object_id):
    object_type, object_style, object_size = get_furniture_data(object_id)
    object_new = {'id': object_id, 'type': object_type, 'style': object_style,
                  'size': object_size[:], 'scale': [1, 1, 1], 'position': [0, 0, 0], 'rotation': [0, 0, 0, 1],
                  'role': '', 'count': 1, 'relate': '', 'relate_position': []}
    return object_new


# 数据拷贝
def copy_group(group_one):
    group_new = group_one.copy()
    if 'size' in group_one:
        group_new['size'] = group_one['size'][:]
    if 'scale' in group_one:
        group_new['scale'] = group_one['scale'][:]
    if 'offset' in group_one:
        group_new['offset'] = group_one['offset'][:]
    if 'position' in group_one:
        group_new['position'] = group_one['position'][:]
    if 'rotation' in group_one:
        group_new['rotation'] = group_one['rotation'][:]
    group_new['obj_list'] = []
    if 'obj_list' in group_one:
        for object_one in group_one['obj_list']:
            object_add = copy_object(object_one)
            group_new['obj_list'].append(object_add)
    group_new['obj_hide'] = []
    if 'obj_hide' in group_one:
        for object_one in group_one['obj_hide']:
            object_add = copy_object(object_one)
            group_new['obj_hide'].append(object_add)
    if 'size_min' in group_one:
        group_new['size_min'] = group_one['size_min'][:]
    if 'size_rest' in group_one:
        group_new['size_rest'] = group_one['size_rest'][:]
    if 'regulation' in group_one:
        group_new['regulation'] = group_one['regulation'][:]
    if 'seed_list' in group_one:
        group_new['seed_list'] = group_one['seed_list'][:]
    return group_new


# 数据计算：打组矩形
def rect_group(group_data):
    # 矩形结果
    furniture_rect = []
    furniture_list = group_data['obj_list']
    # 组合参数
    group_type = ''
    if 'type' in group_data:
        group_type = group_data['type']
    # 计算参数
    min_x, min_y, min_z = 100, 0, 100
    max_x, max_y, max_z = -100, 0, -100
    # 遍历家具
    for furniture_idx, furniture_one in enumerate(furniture_list):
        # 家具角色
        furniture_key, furniture_role = furniture_one['id'], ''
        if 'role' in furniture_one:
            furniture_role = furniture_one['role']
        if furniture_role in ['accessory']:
            continue
        # 家具位置
        width_x = furniture_one['size'][0] * abs(furniture_one['scale'][0]) / 100
        width_y = furniture_one['size'][1] * abs(furniture_one['scale'][1]) / 100
        width_z = furniture_one['size'][2] * abs(furniture_one['scale'][2]) / 100
        [center_x, center_y, center_z] = furniture_one['position']
        angle = rot_to_ang(furniture_one['rotation'])
        if 'normal_position' in furniture_one:
            # 坐标调整
            [center_x, center_y, center_z] = furniture_one['normal_position']
        if 'normal_rotation' in furniture_one:
            angle = rot_to_ang(furniture_one['normal_rotation'])
        if furniture_idx == 0 or furniture_role in ['tv']:
            y1 = center_y
            y2 = center_y + width_y
            if y1 < min_y:
                min_y = y1
            if y2 > max_y:
                max_y = y2
        # 计算矩形
        tmp_x = -width_x / 2
        tmp_z = -width_z / 2
        add_x1 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
        add_z1 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
        tmp_x = width_x / 2
        tmp_z = -width_z / 2
        add_x2 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
        add_z2 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
        tmp_x = width_x / 2
        tmp_z = width_z / 2
        add_x3 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
        add_z3 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
        tmp_x = -width_x / 2
        tmp_z = width_z / 2
        add_x4 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
        add_z4 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
        x_list = [center_x + add_x1, center_x + add_x2, center_x + add_x3, center_x + add_x4]
        z_list = [center_z + add_z1, center_z + add_z2, center_z + add_z3, center_z + add_z4]
        [x1, x2, x3, x4] = x_list
        [z1, z2, z3, z4] = z_list
        if len(furniture_list) > 1 and furniture_role in ['rug', 'side lamp', 'side plant']:
            continue
        else:
            x_list.sort()
            z_list.sort()
            if x_list[0] < min_x:
                min_x = x_list[0]
            if x_list[3] > max_x:
                max_x = x_list[3]
            if z_list[0] < min_z:
                if group_type in ['Meeting'] and furniture_role in ['side plant']:
                    pass
                else:
                    min_z = z_list[0]
            if z_list[3] > max_z:
                max_z = z_list[3]
        # 添加矩形
        rect_one = {
            'id': furniture_one['id'],
            'position': [center_x, center_y, center_z],
            'size': [width_x, width_y, width_z],
            'angle': angle,
            'point': [x1, z1, x2, z2, x3, z3, x4, z4]
        }
        furniture_rect.append(rect_one)
    group_data['size'] = [max_x - min_x, max_y - min_y, max_z - min_z]
    group_data['offset'] = [-(max_x + min_x) / 2, 0, -(max_z + min_z) / 2]
    # 返回信息
    return group_data['size'], group_data['offset'], furniture_rect


# 数据计算
def list_room_by_group(group_type):
    room_list = []
    if group_type in GROUP_RULE_FUNCTIONAL:
        group_rule = GROUP_RULE_FUNCTIONAL[group_type]
        if 'room' in group_rule:
            room_list = group_rule['room']
    return room_list


# 数据计算：家具角色
def compute_furniture_role(object_type, object_size=[], room_type='', object_id='', object_cate_id=''):
    group_name, object_role = '', ''
    # 角色判断
    wait_list = []
    for group_key, group_rule in GROUP_RULE_FUNCTIONAL.items():
        if room_type not in ['', 'none', 'undefined']:
            if group_key in ['Meeting'] and 'sofa' in object_type and object_size[0] > 2.5 and object_size[2] > 0.5:
                pass
            elif room_type not in group_rule['room']:
                continue
        for object_role, obj_list in group_rule['list'].items():
            if object_role in ['accessory', '']:
                continue
            if object_type in obj_list:
                size_good, size_scale = True, 1.0
                # 角色尺寸
                if 'size' in group_rule and object_role in group_rule['size']:
                    size_rule = group_rule['size'][object_role][:]
                    if group_key in ['Media'] and 'media unit' in object_type:
                        size_rule[0][-1] *= 3
                        size_rule[2][-1] *= 3
                    if len(object_size) == len(size_rule) == 3:
                        for i in range(3):
                            if len(size_rule[i]) >= 1:
                                if object_size[i] < size_rule[i][0] or object_size[i] * size_scale > size_rule[i][-1]:
                                    size_good = False
                                    break
                # 品类尺寸
                if 'size' in group_rule and object_type in group_rule['size']:
                    size_rule = group_rule['size'][object_type]
                    if len(object_size) == len(size_rule) == 3:
                        for i in range(3):
                            if len(size_rule[i]) >= 1:
                                if object_size[i] < size_rule[i][0] or object_size[i] * size_scale > size_rule[i][-1]:
                                    size_good = False
                                    break
                # 正确尺寸
                if size_good:
                    wait_list.append([group_key, object_role])
    if len(wait_list) > 1:
        group_name, object_role = wait_list[0][0], wait_list[0][1]
        if group_name in ['Meeting'] and object_role in ['sofa']:
            if max(object_size[0], object_size[2]) < 1.2:
                group_name, object_role = 'Meeting', 'side sofa'
        elif group_name in ['Meeting'] and object_role in ['side table']:
            if min(object_size[0], object_size[2]) > 0.6 and object_size[1] > 0.4:
                group_name, object_role = 'Meeting', 'table'
        elif group_name in ['Dining'] and object_role in ['table']:
            if object_size[1] > UNIT_HEIGHT_TABLE_MAX and len(object_id) > 0:
                object_category_new, object_group_new, object_role_new = \
                    compute_furniture_cate_by_id(object_id, object_type, object_cate_id)
                if object_group_new in ['Work']:
                    group_name, object_role = 'Cabinet', 'cabinet'
        elif group_name in ['Media'] and 'media unit' not in object_type:
            group_name, object_role = 'Cabinet', 'cabinet'
        elif group_name in ['Bed'] and object_role in ['table']:
            if object_size[2] > object_size[0] * 0.8:
                group_name, object_role = wait_list[-1][0], wait_list[-1][1]
        if len(object_id) > 0:
            object_category_new, object_group_new, object_role_new = \
                compute_furniture_cate_by_id(object_id, object_type, object_cate_id)
            if not object_group_new == '':
                group_name, object_role = object_group_new, object_role_new
            elif object_type in ['chair/chair', 'chair/armchair', 'chair/bar chair']:
                if len(object_size) >= 3 and object_size[0] < 0.8:
                    if room_type in ['LivingDiningRoom', 'DiningRoom']:
                        group_name, object_role = 'Dining', 'chair'
                    elif room_type in ['Library', 'MasterBedroom', 'SecondBedroom', 'Bedroom']:
                        group_name, object_role = 'Work', 'chair'
            elif wait_list[-1][0] in ['Cabinet']:
                group_name, object_role = 'Cabinet', 'cabinet'
    elif len(wait_list) == 1:
        group_name, object_role = wait_list[0][0], wait_list[0][1]
        if group_name in ['Meeting'] and object_role in ['table']:
            pass
        elif group_name in ['Dining'] and object_role in ['table']:
            if object_size[1] > UNIT_HEIGHT_TABLE_MAX and len(object_id) > 0:
                object_category_new, object_group_new, object_role_new = \
                    compute_furniture_cate_by_id(object_id, object_type, object_cate_id)
                if object_group_new in ['Work']:
                    group_name, object_role = 'Cabinet', 'cabinet'
        elif group_name in ['Bed'] and object_role in ['table']:
            if object_size[2] > object_size[0] * 0.8:
                group_name, object_role = 'Rest', 'chair'
        elif group_name in ['Media'] and 'media unit' not in object_type:
            group_name, object_role = 'Cabinet', 'cabinet'
        elif group_name in ['Bed'] and object_role in ['bed']:
            if room_type in ["LivingRoom", "LivingDiningRoom"]:
                group_name, object_role = 'Meeting', 'sofa'
    elif 'cabinet' in object_type:
        group_name, object_role = 'Cabinet', 'cabinet'
    else:
        group_name, object_role = '', ''

    # 角色纠错 根据部分category 其次根据jid配置数据指定角色
    if len(object_cate_id) == 0:
        object_cate_id = get_furniture_data_more(object_id)[-1]
    group_role_fix = get_furniture_role_by_cate_id(object_cate_id)

    # 优先用jid指定角色 其次是category 最后是上面策略分析的结果
    group_role_fix_jid = get_furniture_role_by_jid(object_id)
    if len(group_role_fix_jid) >= 2:
        group_name, object_role = group_role_fix_jid[0], group_role_fix_jid[1]
    elif len(group_role_fix) >= 2:
        group_name, object_role = group_role_fix[0], group_role_fix[1]

    # 角色兜底
    if group_name == '':
        if len(room_type) > 0:
            object_type_main = object_type.split('/')[0]
            if object_type_main in ['table']:
                if min(object_size[0], object_size[2]) * 4 < max(object_size[0], object_size[2]):
                    if object_size[1] < 0.75:
                        group_name, object_role = 'Media', 'table'
                    else:
                        group_name, object_role = 'Cabinet', 'cabinet'
                elif max(object_size[0], object_size[2]) < 0.5:
                    group_name, object_role = 'Meeting', 'side table'
                    if 'Bedroom' in room_type:
                        group_name, object_role = 'Bed', 'side table'
                elif 'coffee table' in object_type:
                    group_name, object_role = 'Meeting', 'table'
                    if object_size[1] > 1.0:
                        group_name, object_role = 'Cabinet', 'cabinet'
                else:
                    group_name, object_role = 'Meeting', 'table'
                return group_name, object_role
            elif object_type_main in ['sofa']:
                if object_size[0] >= 3:
                    group_name, object_role = 'Meeting', 'sofa'
                else:
                    group_name, object_role = 'Meeting', 'side sofa'
                return group_name, object_role
            elif object_type_main in ['chair']:
                if object_size[0] >= 3:
                    group_name, object_role = 'Meeting', 'sofa'
                else:
                    group_name, object_role = 'Rest', 'chair'
                return group_name, object_role
            elif object_type_main in ['bed']:
                if object_size[0] >= 3:
                    group_name, object_role = 'Bed', 'bed'
                else:
                    group_name, object_role = 'Rest', 'chair'
                return group_name, object_role
            elif object_type_main in ['media unit', 'storage unit', 'cabinet', 'shelf']:
                group_name, object_role = 'Cabinet', 'cabinet'
                return group_name, object_role
    else:
        return group_name, object_role

    # 装饰区域
    for group_key, obj_list in GROUP_RULE_DECORATIVE.items():
        if object_type in obj_list:
            object_role = object_type.split('/')[0]
            group_name, object_role = group_key, object_role
            return group_name, object_role
    return '', ''


# 数据计算：硬装角色
def compute_decorate_role(object_type):
    group_name, object_role = '', ''
    for group_name, group_rule in GROUP_RULE_DECORATIVE.items():
        if object_type in group_rule:
            object_role = object_type.split('/')[0]
            return group_name, object_role
    return '', ''


# 数据计算：硬装角色
def compute_decorate_mesh(object_type, object_size=[1, 1, 1]):
    for mesh_role, mesh_list in GROUP_MESH_DICT.items():
        if object_type in mesh_list:
            if mesh_role == 'background':
                if 20 < object_size[2] < object_size[0] < 200:
                    return 'cabinet'
                if 20 < object_size[0] < object_size[2] < 200:
                    return 'cabinet'
            return mesh_role
    return ''


# 数据计算：家具角色
def compute_furniture_cate_by_id(object_id, object_type='', object_cate_id=''):
    if len(object_cate_id) > 0:
        type_id, style_id, category_id = '', '', object_cate_id
    else:
        type_id, style_id, category_id = get_furniture_data_refer_id(object_id, '', False)
    object_category_new, object_group_new, object_role_new = '', '', ''
    if not category_id == '':
        object_category_new, object_group_new, object_role_new = get_furniture_role_by_category(category_id)
        if object_group_new == '' and object_type in ['table/table']:
            object_group_new, object_role_new = 'Work', 'table'
    return object_category_new, object_group_new, object_role_new


# 数据计算：家具角色
def compute_furniture_cate_by_cate(object_cate_id, object_type=''):
    object_category_new, object_group_new, object_role_new = '', '', ''
    if not object_cate_id == '':
        object_category_new, object_group_new, object_role_new = get_furniture_role_by_category(object_cate_id)
        if object_group_new == '' and object_type in ['table/table']:
            object_group_new, object_role_new = 'Work', 'table'
    return object_category_new, object_group_new, object_role_new


# 数据计算：家具类似
def compute_furniture_like(object_group, object_role, object_limit=10):
    like_list = []
    global FURNITURE_GROUP_DICT
    load_furniture_group()
    for group_room in FURNITURE_GROUP_DICT.values():
        if len(like_list) >= object_limit:
            break
        for group_list in group_room.values():
            if len(like_list) >= object_limit:
                break
            for group_one in group_list:
                if len(like_list) >= object_limit:
                    break
                if not object_group == '' and not object_group == group_one['type']:
                    continue
                for object_one in group_one['obj_list']:
                    if len(like_list) >= object_limit:
                        break
                    if not object_role == '' and not object_role == object_one['role']:
                        continue
                    like_list.append(object_one['id'])
    return like_list


# 数据计算：家具矩形
def compute_furniture_rect(size, position, rotation, adjust=[0, 0, 0, 0], direct=0):
    # 角度
    ang = rot_to_ang(rotation)
    angle = ang
    # 尺寸
    width_x, width_y, width_z = size[0], size[1], size[2]
    center_x, center_y, center_z = position[0], position[1], position[2]
    # 矩形
    tmp_x = (width_x / 2 + adjust[3])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x1 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z1 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = -(width_x / 2 + adjust[1])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x2 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z2 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = -(width_x / 2 + adjust[1])
    tmp_z = (width_z / 2 + adjust[2])
    add_x3 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z3 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = (width_x / 2 + adjust[3])
    tmp_z = (width_z / 2 + adjust[2])
    add_x4 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z4 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    [x1, x2, x3, x4] = [center_x + add_x1, center_x + add_x2, center_x + add_x3, center_x + add_x4]
    [z1, z2, z3, z4] = [center_z + add_z1, center_z + add_z2, center_z + add_z3, center_z + add_z4]
    if direct >= 1:
        return [x2, z2, x3, z3, x4, z4, x1, z1]
    return [x1, z1, x2, z2, x3, z3, x4, z4]


# 数据计算：家具区域
def compute_furniture_pixel(object_one, camera_one, view_width=800, view_height=800):
    # 物品
    size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    if 'item' in object_one:
        item_one = object_one['item']
        size = [abs(item_one['size'][i] * item_one['scale'][i]) / 100 for i in range(3)]
    position, angle = object_one['position'], rot_to_ang(object_one['rotation'])
    adjust = [0, 0, 0, 0]

    # 尺寸
    width_x, width_y, width_z = size[0], size[1], size[2]
    center_x, center_y, center_z = position[0], position[1], position[2]
    # 轮廓
    tmp_x = (width_x / 2 + adjust[3])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x1 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z1 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = -(width_x / 2 + adjust[1])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x2 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z2 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = -(width_x / 2 + adjust[1])
    tmp_z = (width_z / 2 + adjust[2])
    add_x3 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z3 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    tmp_x = (width_x / 2 + adjust[3])
    tmp_z = (width_z / 2 + adjust[2])
    add_x4 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z4 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    [x1, x2, x3, x4] = [center_x + add_x1, center_x + add_x2, center_x + add_x3, center_x + add_x4]
    [z1, z2, z3, z4] = [center_z + add_z1, center_z + add_z2, center_z + add_z3, center_z + add_z4]
    # 顶点
    bot_y, top_y = center_y, center_y + width_y
    p1, p2, p3, p4 = [x1, bot_y, z1], [x2, bot_y, z2], [x3, bot_y, z3], [x4, bot_y, z4]
    p5, p6, p7, p8 = [x1, top_y, z1], [x2, top_y, z2], [x3, top_y, z3], [x4, top_y, z4]
    point_set = [p1, p2, p3, p4, p5, p6, p7, p8]

    # 投影 TODO:
    o1, o2, fov = camera_one['pos'], camera_one['target'], camera_one['fov']


    aspect_ratio = camera_one["aspect"]  # width / height
    fov = camera_one["fov"] / 180.0*math.pi
    near, far = camera_one["near"], camera_one["far"]

    camera_position = camera_one["pos"]
    camera_target = camera_one["target"]

    t = math.tan(fov/2) * abs(near)
    r = t * aspect_ratio
    l = -r
    b = -t
    n = abs(near)
    f = abs(far)

    g_hat = np.array([u-v for u, v in zip(camera_target, camera_position)])
    g_norm = np.sqrt(np.sum(g_hat**2))
    g_hat /= g_norm
    e = np.array(camera_position)

    # t_hat = np.array(camera_one["up"])
    t_hat = np.cross(np.cross(g_hat, np.array(camera_one["up"])), g_hat)
    t_norm = np.sqrt(np.sum(t_hat**2))
    t_hat /= t_norm

    g_cross_t = np.cross(g_hat, t_hat)
    R_view = np.concatenate([g_cross_t.reshape(1, -1),
                             t_hat.reshape(1, -1),
                             -1*g_hat.reshape(1, -1),
                             np.zeros((1, 3))], axis=0)

    R_view = np.concatenate([R_view, np.array([0, 0, 0, 1]).reshape(-1, 1)], axis=-1)
    T_view = np.concatenate([np.concatenate([np.eye(3), -1*e.reshape(-1, 1)], axis=-1),
              np.array([0., 0., 0., 1.]).reshape(1, -1)], axis=0)

    point_num = len(point_set)
    point_set = np.concatenate([np.array(point_set), np.ones((point_num, 1))], axis=-1)
    point_set = point_set.transpose()

    # view/camera transformation
    camera_coo = R_view.dot(T_view).dot(point_set)

    scale = np.array([
        [2./(r-l), 0., 0., 0.],
        [0., 2./(t-b), 0., 0.],
        [0., 0., 2./(f-n), 0.],
        [0., 0., 0., 1.],
    ])
    move = np.array([
        [1., 0., 0., 0.],
        [0., 1., 0., 0.],
        [0., 0., 0., -0.5*(n+f)],  # 如果near和far都是正数的话，这里应该去掉负号？
        [0., 0., 0., 1.]
    ])

    M_ortho = scale.dot(move)
    M_persp_to_ortho = np.array([
        [n, 0., 0., 0.],
        [0., n, 0., 0.],
        [0., 0., n+f, -n*f],
        [0., 0., 1., 0.]
    ])

    coo = M_ortho.dot(M_persp_to_ortho.dot(camera_coo))

    M_viewport = np.array([
        [-view_width/2., 0., 0., view_width/2.],
        [0., view_height/2., 0., view_height/2.],
        [0., 0., 1., 0.],
        [0., 0., 0., 1.]
    ])

    # 变换到图像坐标系
    final_coo = M_viewport.dot(coo)
    final_coo = final_coo.transpose()
    norm = final_coo[:, -1]
    final_coo /= norm.reshape(-1, 1)
    final_coo = final_coo[:, :-1]

    x_min = np.min(final_coo[:, 0])
    x_max = np.max(final_coo[:, 0])
    y_min = np.min(final_coo[:, 1])
    y_max = np.max(final_coo[:, 1])

    return [x_min, y_min, x_max, y_max]


# 数据计算：家具靠背
def compute_furniture_back(size, position, rotation, extent):
    # 角度
    ang = rot_to_ang(rotation)
    angle = ang
    # 尺寸
    width_x, width_z = size[0], size[2]
    adjust = [0, 0, 0, 0]
    # 中心
    center_x, center_z = position[0], position[2]
    # 矩形
    tmp_x = -(width_x / 2 + adjust[3])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x1 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z1 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)

    tmp_x = (width_x / 2 + adjust[1])
    tmp_z = -(width_z / 2 + adjust[0])
    add_x2 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z2 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)

    tmp_x = (width_x / 2 + adjust[1])
    tmp_z = -(width_z / 2 + adjust[2]) - extent
    add_x3 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z3 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)

    tmp_x = -(width_x / 2 + adjust[3])
    tmp_z = -(width_z / 2 + adjust[2]) - extent
    add_x4 = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z4 = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)

    # 返回
    [x1, x2, x3, x4] = [center_x + add_x1, center_x + add_x2, center_x + add_x3, center_x + add_x4]
    [z1, z2, z3, z4] = [center_z + add_z1, center_z + add_z2, center_z + add_z3, center_z + add_z4]
    return [x1, z1, x2, z2, x3, z3, x4, z4]


# 数据计算：家具靠墙
def compute_furniture_rely(object_one, line_list, rely_dlt=0.1):
    # 家具矩形
    object_pos, object_rot = object_one['position'], object_one['rotation']
    object_type = object_one['type']
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    object_unit = compute_furniture_rect(object_size, object_pos, object_rot)
    # 靠墙判断
    if object_type.startswith('sofa'):
        rely_dlt = 0.45
    elif object_type.startswith('bed'):
        rely_dlt = 0.30
    unit_one = object_unit
    edge_len, edge_idx = int(len(unit_one) / 2), -1
    rely_dis, rely_idx, rely_rat = 0, -1, []
    for j in range(edge_len):
        x_p = unit_one[(2 * j + 0) % len(unit_one)]
        y_p = unit_one[(2 * j + 1) % len(unit_one)]
        x_q = unit_one[(2 * j + 2) % len(unit_one)]
        y_q = unit_one[(2 * j + 3) % len(unit_one)]
        x_r = unit_one[(2 * j + 4) % len(unit_one)]
        y_r = unit_one[(2 * j + 5) % len(unit_one)]
        # 宽度深度
        unit_width, unit_angle = xyz_to_ang(x_p, y_p, x_q, y_q)
        if j <= 1:
            unit_depth = math.sqrt((x_r - x_q) * (x_r - x_q) + (y_r - y_q) * (y_r - y_q))
        else:
            x_o = unit_one[2 * j - 2]
            y_o = unit_one[2 * j - 1]
            unit_depth = math.sqrt((x_o - x_p) * (x_o - x_p) + (y_o - y_p) * (y_o - y_p))
        if unit_width < unit_depth / 2 or unit_width < 0.2:
            continue
        unit_idx, unit_dis, unit_rat = -1, 0, []
        for line_idx, line_one in enumerate(line_list):
            # 重合方向
            x1, y1, x2, y2 = line_one['p1'][0], line_one['p1'][1], line_one['p2'][0], line_one['p2'][1]
            line_width, line_angle = line_one['width'], line_one['angle']
            if abs(ang_to_ang(line_angle - unit_angle)) > 0.1:
                continue
            if abs(y1 - y2) < 0.1 and abs(x1 - x2) < 0.1:
                continue
            elif abs(y1 - y2) < 0.1:
                if abs(y1 - y_p) > rely_dlt:
                    continue
            elif abs(x1 - x2) < 0.1:
                if abs(x1 - x_p) > rely_dlt:
                    continue
            else:
                r_p_x = (x_p - x1) / (x2 - x1)
                r_p_y = (y_p - y1) / (y2 - y1)
                r_q_x = (x_q - x1) / (x2 - x1)
                r_q_y = (y_q - y1) / (y2 - y1)
                if abs(r_p_x - r_p_y) > 0.01 or abs(r_q_x - r_q_y) > 0.01:
                    continue
            # 重合比例
            if abs(x2 - x1) >= 0.00001:
                r_p = (x_p - x1) / (x2 - x1)
                r_q = (x_q - x1) / (x2 - x1)
            elif abs(y2 - y1) >= 0.00001:
                r_p = (y_p - y1) / (y2 - y1)
                r_q = (y_q - y1) / (y2 - y1)
            else:
                continue
            if r_p <= 0 and r_q <= 0:
                continue
            if r_p >= 1 and r_q >= 1:
                continue
            if abs(r_p - r_q) < 0.001:
                continue
            r1 = max(0, min(r_p, r_q))
            r2 = min(1, max(r_p, r_q))
            if line_width * (r2 - r1) < 0.1:
                continue
            unit_idx, unit_dis = line_idx, line_width * (r2 - r1)
            unit_rat = [min(r_p, r_q), max(r_p, r_q)]
            break
        if 0 <= unit_idx < len(line_list):
            if unit_dis > rely_dis:
                edge_idx, rely_dis, rely_idx, rely_rat = j, unit_dis, unit_idx, unit_rat
            if unit_dis > unit_width * 0.9 and unit_width > unit_depth:
                break
    return edge_idx, rely_idx, rely_rat


# 数据计算：家具加成
def compute_furniture_well(object_one, object_link, suit_type, suit_role, face_pos=[]):
    object_well = 0
    object_type = object_one['type']
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    object_pos = object_one['position']
    if suit_type in ['Meeting'] and suit_role in ['sofa']:
        if 'relate_role' in object_one and object_one['relate_role'] in ['wall'] and object_size[0] >= 1.0:
            object_well += 1
        if object_size[0] < object_size[2] * 1.2 and object_size[0] < 2:
            object_well -= 1
        # 同类判断
        pos_adjust = [0 - object_pos[0], 0 - object_pos[1], 0 - object_pos[2]]
        ang_adjust = 0 - rot_to_ang(object_one['rotation'])
        for object_old in object_link:
            size_old = [abs(object_old['size'][i] * object_old['scale'][i]) / 100 for i in range(3)]
            if object_old == object_one:
                continue
            elif 'sofa' not in object_old['type']:
                continue
            elif size_old[2] <= 0.5:
                continue
            elif 'relate' in object_one and len(object_one['relate']) > 0:
                continue
            pos_old_x = object_old['position'][0] + pos_adjust[0]
            pos_old_z = object_old['position'][2] + pos_adjust[2]
            pos_new_x = pos_old_z * math.sin(ang_adjust) + pos_old_x * math.cos(ang_adjust)
            pos_new_z = pos_old_z * math.cos(ang_adjust) - pos_old_x * math.sin(ang_adjust)
            if abs(pos_new_x) < min(abs(object_size[0]) / 2, 0.3) and pos_new_z > 1:
                object_well -= 1
        # 对面判断
        if len(face_pos) >= 3:
            pos_old_x = face_pos[0] + pos_adjust[0]
            pos_old_z = face_pos[2] + pos_adjust[2]
            pos_new_x = pos_old_z * math.sin(ang_adjust) + pos_old_x * math.cos(ang_adjust)
            pos_new_z = pos_old_z * math.cos(ang_adjust) - pos_old_x * math.sin(ang_adjust)
            if abs(pos_new_x) <= 0.1 and 1 < pos_new_z < 5:
                object_well += 2
            elif abs(pos_new_x) <= 0.5 and 1 < pos_new_z < 10:
                object_well += 1
    elif suit_type in ['Dining'] and suit_role in ['table']:
        if 'dining' in object_type:
            object_well = 1
        if 'relate_role' in object_one and object_one['relate_role'] in ['wall']:
            object_well = 1
    return object_well


# 数据计算：配饰补充
def compute_accessory_side(x1, x2, object_old, plat_pos, plat_ang, cate_main=[], cate_side=[]):
    # 配饰品类
    if len(cate_main) <= 0:
        cate_main = ['花卉', '工艺品', '书籍', '相框']
    if len(cate_side) <= 0:
        cate_side = ['配饰']
    # 配饰补充
    object_set = []
    object_rand = random.randint(0, 100)
    for add_idx in range(2):
        if len(object_old) <= 0:
            break
        if len(plat_pos) <= 0:
            break
        if abs(x1 - x2) < 0.1:
            break
        if add_idx <= 0 and abs(x1 - x2) >= 0.2:
            cate_one = cate_main[add_idx % len(cate_main)]
        else:
            cate_one = cate_side[add_idx % len(cate_side)]
        object_rand += 1
        object_list = get_furniture_list_id(cate_one)
        object_id = object_list[object_rand % len(object_list)]
        object_new = copy_object(object_old)
        # 基本信息
        object_type, object_style, origin_size = get_furniture_data(object_id)
        object_new['id'] = object_id
        object_new['type'], object_new['style'] = object_type, object_style
        object_new['size'], object_new['scale'] = origin_size[:], [1, 1, 1]
        object_size = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
        width_max = abs(x1 - x2)
        if object_size[0] > width_max:
            ratio_new = width_max / object_size[0]
            scale_new = object_new['scale']
            scale_new[0] *= ratio_new
            scale_new[1] *= ratio_new
            scale_new[2] *= ratio_new
            object_size = [abs(object_new['size'][i] * object_new['scale'][i]) / 100 for i in range(3)]
        # 位置信息
        shift_max = max(object_size[0], width_max / 2)
        object_shift = object_new['relate_shifting']
        object_shift[0] = x1 + shift_max / width_max * 0.5 * (x2 - x1)
        tmp_x, tmp_y, tmp_z = object_shift[0], object_shift[1], object_shift[2]
        add_x = tmp_z * math.sin(plat_ang) + tmp_x * math.cos(plat_ang)
        add_y = tmp_y
        add_z = tmp_z * math.cos(plat_ang) - tmp_x * math.sin(plat_ang)
        object_pos = [plat_pos[0] + add_x, plat_pos[1] + add_y, plat_pos[2] + add_z]
        object_ang = plat_ang + 0
        object_rot = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
        object_new['position'] = object_pos[:]
        object_new['rotation'] = object_rot[:]
        object_new['origin_position'] = object_pos[:]
        object_new['origin_rotation'] = object_rot[:]
        object_new['normal_position'][0] = tmp_x
        # 尺寸信息
        object_new['size_max'] = [object_size[0] * 100, object_size[1] * 100, object_size[2] * 100]
        object_new['size_max'][0] = shift_max * 100
        object_new['size_dir'] = [0, 0, 0]
        # 叠加信息
        object_new['top_id'] += 100
        # 更新范围
        x1_new = x1 + (shift_max + 0.05) / width_max * 1.0 * (x2 - x1)
        x1 = x1_new
        object_set.append(object_new)
    return object_set


# 数据计算：硬装区域
def compute_decorate_rect(group_one):
    group_type = group_one['type']
    front_rect, back_rect = [], []
    back_p1, back_p2, back_depth, back_front, back_angle = [], [], 0, 0, 0
    if 'back_p1' in group_one and 'back_p2' in group_one:
        back_p1, back_p2 = group_one['back_p1'], group_one['back_p2']
    if 'back_depth' in group_one:
        back_depth = group_one['back_depth']
    if 'back_front' in group_one:
        back_front = group_one['back_front']
    if 'back_angle' in group_one:
        back_angle = group_one['back_angle']
    if len(back_p1) >= 2 and len(back_p2) >= 2 and back_front > 0:
        tmp_x, tmp_z = 0, back_front
        p1, p2 = back_p1[:], back_p2[:]
        add_x = tmp_z * math.sin(back_angle) + tmp_x * math.cos(back_angle)
        add_z = tmp_z * math.cos(back_angle) - tmp_x * math.sin(back_angle)
        p3 = [p2[0] + add_x, p2[1] + add_z]
        p4 = [p1[0] + add_x, p1[1] + add_z]
        front_rect = [p1, p2, p3, p4]
    else:
        unit_one = compute_furniture_rect(group_one['size'], group_one['position'], group_one['rotation'])
        if len(unit_one) >= 8:
            front_rect = [[unit_one[0], unit_one[1]], [unit_one[2], unit_one[3]],
                          [unit_one[4], unit_one[5]], [unit_one[6], unit_one[7]]]
    if len(back_p1) >= 2 and len(back_p2) >= 2:
        if back_depth <= 0:
            back_depth = 0.05
        tmp_x, tmp_z = 0, back_depth
        p1, p2 = back_p1[:], back_p2[:]
        add_x = tmp_z * math.sin(back_angle) + tmp_x * math.cos(back_angle)
        add_z = tmp_z * math.cos(back_angle) - tmp_x * math.sin(back_angle)
        p3 = [p2[0] + add_x, p2[1] + add_z]
        p4 = [p1[0] + add_x, p1[1] + add_z]
        back_rect = [p1, p2, p3, p4]
    return front_rect, back_rect


# 数据计算：硬装拆分
def compute_decorate_part(object_one, object_role=''):
    # 位置
    object_pos = object_one['position']
    object_ang = rot_to_ang(object_one['rotation'])
    # 尺寸
    object_size = [abs(object_one['size'][i] * object_one['scale'][i]) / 100 for i in range(3)]
    width_old, depth_old = object_size[0], object_size[2]
    width_new, depth_new = object_size[0], 0.5
    if object_role in ['background']:
        depth_new = 0.1
    if depth_old < 1.0:
        return [object_one]

    # 原有硬装
    tmp_x, tmp_z = 0, depth_old / 2 - depth_new / 2
    angle = -object_ang
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    pos_1 = [object_pos[0] + add_x, object_pos[1], object_pos[2] + add_z]
    rot_1 = [0, math.sin(object_ang / 2), 0, math.cos(object_ang / 2)]
    size_1 = [width_new * 100, object_size[1] * 100, depth_new * 100]
    scale_1 = [1, 1, 1]
    object_1 = copy_object(object_one)
    object_1['size'], object_1['scale'] = size_1, scale_1
    object_1['position'], object_1['rotation'] = pos_1, rot_1
    if 'entityId' in object_one:
        object_1['entityId'] = ''
    # 对面硬装
    tmp_x, tmp_z = 0, depth_old / 2 - depth_new / 2
    angle = object_ang
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    pos_2 = [object_pos[0] + add_x, object_pos[1], object_pos[2] + add_z]
    rot_2 = [0, math.sin(-object_ang / 2), 0, math.cos(-object_ang / 2)]
    size_2 = [width_new * 100, object_size[1] * 100, depth_new * 100]
    scale_2 = [1, 1, 1]
    object_2 = copy_object(object_one)
    object_2['size'], object_2['scale'] = size_2, scale_2
    object_2['position'], object_2['rotation'] = pos_2, rot_2
    if 'entityId' in object_one:
        object_2['entityId'] = ''
    # 返回信息
    object_list = [object_1, object_2]
    return object_list


# 数据计算：组合靠墙
def compute_group_rely(group_one, line_list, rely_dlt=0.2):
    # 家具矩形
    object_pos, object_rot = group_one['position'], group_one['rotation']
    object_type = group_one['type']
    object_size = [abs(group_one['size'][i]) for i in range(3)]
    object_rect = [0, 0, 0, 0]
    if 'regulation' in group_one:
        object_rect = group_one['regulation']
    object_unit = compute_furniture_rect(object_size, object_pos, object_rot, object_rect)
    # 靠墙判断
    unit_one = object_unit
    edge_len, edge_idx = int(len(unit_one) / 2), -1
    rely_len, rely_idx, rely_rat, rely_face, rely_back = 0, -1, [0, 1], object_size[2], 0
    for j in range(edge_len):
        x_p = unit_one[(2 * j + 0) % len(unit_one)]
        y_p = unit_one[(2 * j + 1) % len(unit_one)]
        x_q = unit_one[(2 * j + 2) % len(unit_one)]
        y_q = unit_one[(2 * j + 3) % len(unit_one)]
        x_r = unit_one[(2 * j + 4) % len(unit_one)]
        y_r = unit_one[(2 * j + 5) % len(unit_one)]
        # 宽度深度
        unit_width, unit_angle = xyz_to_ang(x_p, y_p, x_q, y_q)
        if j <= 1:
            unit_depth = math.sqrt((x_r - x_q) * (x_r - x_q) + (y_r - y_q) * (y_r - y_q))
        else:
            x_o = unit_one[2 * j - 2]
            y_o = unit_one[2 * j - 1]
            unit_depth = math.sqrt((x_o - x_p) * (x_o - x_p) + (y_o - y_p) * (y_o - y_p))
        if unit_width < unit_depth / 2 and object_type not in ['Bath']:
            continue
        if unit_width < 0.2:
            continue
        unit_idx, unit_dis, unit_rat, unit_face, unit_back = -1, 0, [], unit_depth, 0
        for line_idx, line_one in enumerate(line_list):
            # 重合方向
            x1, y1, x2, y2 = line_one['p1'][0], line_one['p1'][1], line_one['p2'][0], line_one['p2'][1]
            line_width, line_angle = line_one['width'], line_one['angle']
            if abs(ang_to_ang(line_angle - unit_angle)) > 0.1:
                continue
            if abs(y1 - y2) < 0.1 and abs(x1 - x2) < 0.1:
                continue
            elif abs(y1 - y2) < 0.1:
                unit_back = abs(y1 - y_p)
                if unit_back > rely_dlt:
                    continue
                if abs(unit_back) < 0.001:
                    unit_back, y_p = 0, y1
            elif abs(x1 - x2) < 0.1:
                unit_back = abs(x1 - x_p)
                if unit_back > rely_dlt:
                    continue
                if abs(unit_back) < 0.001:
                    unit_back, x_p = 0, x1
            else:
                r_p_x = (x_p - x1) / (x2 - x1)
                r_p_y = (y_p - y1) / (y2 - y1)
                r_q_x = (x_q - x1) / (x2 - x1)
                r_q_y = (y_q - y1) / (y2 - y1)
                if abs(r_p_x - r_p_y) > 0.01 or abs(r_q_x - r_q_y) > 0.01:
                    continue

            # 重合比例
            if abs(x2 - x1) >= 0.00001:
                r_p = (x_p - x1) / (x2 - x1)
                r_q = (x_q - x1) / (x2 - x1)
            elif abs(y2 - y1) >= 0.00001:
                r_p = (y_p - y1) / (y2 - y1)
                r_q = (y_q - y1) / (y2 - y1)
            else:
                continue
            if r_p <= 0 and r_q <= 0:
                continue
            if r_p >= 1 and r_q >= 1:
                continue
            if abs(r_p - r_q) < 0.001:
                continue
            r1 = max(0, min(r_p, r_q))
            r2 = min(1, max(r_p, r_q))
            if line_width * (r2 - r1) < 0.1:
                continue
            unit_idx, unit_dis = line_idx, line_width * (r2 - r1)
            unit_rat = [min(r_p, r_q), max(r_p, r_q)]
            if 'depth_all' in line_one:
                depth_all = line_one['depth_all']
                depth_rat = 0
                for depth_one in depth_all:
                    if depth_one[1] <= unit_rat[0] or depth_one[0] >= unit_rat[1]:
                        continue
                    else:
                        if depth_rat < 0.1:
                            unit_face = depth_one[2]
                            depth_rat = depth_one[1] - depth_one[0]
                        elif depth_rat < depth_one[1] - depth_one[0]:
                            unit_face = depth_one[2]
                            depth_rat = depth_one[1] - depth_one[0]
                        if depth_rat > (unit_rat[1] - unit_rat[0]) * 0.5:
                            break
            if 0 <= unit_idx < len(line_list):
                if unit_dis <= rely_len * 0.5 and j == edge_idx:
                    pass
                elif unit_dis >= max(rely_len * 2.0, 0.5) and j == edge_idx:
                    edge_idx, rely_len, rely_idx, rely_rat = j, unit_dis, unit_idx, unit_rat
                    rely_face, rely_back = unit_face, unit_back
                elif unit_dis * unit_face > rely_len * rely_face and unit_back < max(rely_back + 0.5, rely_back * 1.5):
                    edge_idx, rely_len, rely_idx, rely_rat = j, unit_dis, unit_idx, unit_rat
                    rely_face, rely_back = unit_face, unit_back
                elif edge_idx < 0:
                    edge_idx, rely_len, rely_idx, rely_rat = j, unit_dis, unit_idx, unit_rat
                    rely_face, rely_back = unit_face, unit_back
                if unit_dis > unit_width * 0.9 and unit_width > unit_depth:
                    break
    return edge_idx, rely_idx, rely_rat, rely_face, rely_back


# 判断方位
def xyz_to_loc(x1, z1, x2, z2, angle, width=1.0, depth=1.0, delta=0.1):
    # 左侧
    tmp_x, tmp_z = -width / 2, 0
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_left = x1 + add_x
    z1_left = z1 + add_z
    dis_left = (x1_left - x2) * (x1_left - x2) + (z1_left - z2) * (z1_left - z2)
    # 右侧
    tmp_x, tmp_z = width / 2, 0
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_right = x1 + add_x
    z1_right = z1 + add_z
    dis_right = (x1_right - x2) * (x1_right - x2) + (z1_right - z2) * (z1_right - z2)

    # 后侧
    tmp_x, tmp_z = 0, -depth / 2
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_back = x1 + add_x
    z1_back = z1 + add_z
    dis_back = (x1_back - x2) * (x1_back - x2) + (z1_back - z2) * (z1_back - z2)
    # 前侧
    tmp_x, tmp_z = 0, depth / 2
    add_x = tmp_z * math.sin(angle) + tmp_x * math.cos(angle)
    add_z = tmp_z * math.cos(angle) - tmp_x * math.sin(angle)
    x1_front = x1 + add_x
    z1_front = z1 + add_z
    dis_front = (x1_front - x2) * (x1_front - x2) + (z1_front - z2) * (z1_front - z2)

    # 返回
    flag_left, flag_back = 0, 0
    if dis_left < dis_right - delta:
        flag_left = 1
    elif dis_right < dis_left - delta:
        flag_left = -1
    if dis_back < dis_front - delta:
        flag_back = 1
    elif dis_front < dis_back - delta:
        flag_back = -1
    return flag_left, flag_back


# 计算角度
def xyz_to_ang(x1, y1, x2, y2):
    if abs(x2 - x1) < 0.001:
        if y2 >= y1:
            length = y2 - y1
            angle = 0
        else:
            length = y1 - y2
            angle = math.pi
    elif abs(y2 - y1) < 0.001:
        if x2 >= x1:
            length = x2 - x1
            angle = math.pi / 2
        else:
            length = x1 - x2
            angle = math.pi / 2 * 3
    else:
        length = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        angle = math.acos((y2 - y1) / length)
        if x2 - x1 <= -0.001:
            angle = math.pi * 2 - angle
    # 规范
    if angle > math.pi * 2:
        angle -= math.pi * 2
    elif angle < -math.pi * 2:
        angle += math.pi * 2
    # 规范
    if angle > math.pi:
        angle -= math.pi * 2
    elif angle < -math.pi:
        angle += math.pi * 2
    return length, angle


def ang_to_rot(ang):
    return [0, math.sin(ang / 2), 0, math.cos(ang / 2)]


# 转化角度
def rot_to_ang(rot):
    rot_1 = rot[1]
    rot_3 = rot[3]
    if rot_1 > 1:
        rot_1 = 1
    elif rot_1 < -1:
        rot_1 = -1
    if rot_3 > 1:
        rot_3 = 1
    elif rot_3 < -1:
        rot_3 = -1
    # 计算
    ang = 0
    if abs(rot_1 - 1) < 0.0001 or abs(rot_1 + 1) < 0.0001:
        ang = math.pi
    elif abs(rot_3 - 1) < 0.0001 or abs(rot_3 + 1) < 0.0001:
        ang = 0
    else:
        if rot_1 >= 0 and rot_3 >= 0:
            ang = math.asin(rot_1) * 2
        elif rot_1 <= 0 and rot_3 >= 0:
            ang = math.asin(rot_1) * 2
        elif rot_1 >= 0 and rot_3 <= 0:
            ang = math.acos(rot_3) * 2
        elif rot_1 <= 0 and rot_3 <= 0:
            ang = -math.acos(rot_3) * 2
    # 规范
    if ang > math.pi * 2:
        ang -= math.pi * 2
    elif ang < -math.pi * 2:
        ang += math.pi * 2
    # 规范
    if ang > math.pi:
        ang -= math.pi * 2
    elif ang < -math.pi:
        ang += math.pi * 2
    # 返回
    return ang


# 规范角度
def ang_to_ang(angle_old):
    angle_new = angle_old
    # 计算
    if abs(angle_new - 2 * math.pi) <= 0.01:
        angle_new = 0
    elif abs(angle_new + 2 * math.pi) <= 0.01:
        angle_new = 0
    elif abs(angle_new - math.pi) <= 0.01:
        angle_new = math.pi
    elif abs(angle_new + math.pi) <= 0.01:
        angle_new = math.pi
    else:
        # 规范
        if angle_new > 2 * math.pi:
            angle_new -= 2 * math.pi
        elif angle_new < -2 * math.pi:
            angle_new += 2 * math.pi
        # 规范
        if angle_new <= -math.pi:
            angle_new += 2 * math.pi
        if angle_new > math.pi:
            angle_new -= 2 * math.pi
    # 返回
    return angle_new


# 水平角度
def hor_or_ver(angle_old):
    angle_new = ang_to_ang(angle_old)
    if abs(angle_new - math.pi * 0.5) < 0.05 or abs(angle_new + math.pi * 0.5) < 0.05:
        return 0
    elif abs(angle_new) < 0.05 or abs(angle_new - math.pi) < 0.05 or abs(angle_new + math.pi) < 0.05:
        return 1
    return -1


# 数据加载
load_furniture_group()

# 功能测试
if __name__ == '__main__':
    pass
