

def get_default_wall_info():
    return {'normal_height': 2.8, 'door_height': 2.0, 'window_top': 2.0, 'window_height':0.6}


def get_default_baseboard_info():
    return {}


def get_default_door_info():
    return {'type':'Door', 'door_height': 2.0}


def get_default_window_info():
    return {'type':'Window', 'window_top': 2.0, 'window_height':0.6}


style_en = {
    "victorian": "欧式/古典",
    "european": "欧式",
    "classic": "简欧/新古典",
    "neo-classical": "简欧/新古典",
    "neoclassical": "简欧/新古典",
    "asian antique": "明清古典",
    "vintage": "复古怀旧",
    "antique": "古董",
    "swedish": "北欧",
    "nordic": "北欧",
    "north-europe": "北欧",
    "midcentury": "中世纪",
    "modern": "包豪斯",
    "mediterranean": "地中海",
    "tuscan": "托斯卡纳",
    "bohemian chic": "波西米亚",
    "chinese": "中式",
    "chinese modern": "新中式",
    "japan": "日式",
    "japanese": "日式",
    "korea": "韩式",
    "korean modern": "韩式",
    "asan": "东南亚",
    "asian": "东南亚",
    "islamic": "伊斯兰",
    "country": "美式乡村",
    "us": "美式乡村",
    "contemporary": "现代",
    "industrial": "工业风",
    "urban": "都市风",
    "retro": "年代风",
    "beach": "海滩风",
    "tropical": "热带风",
    "coastal": "沿海",
    "cottage": "小屋",
    "rural": "田园",
    "garden": "花园",
    "cold color": "冷色调",
    "warm color": "暖色调",
    "rustic": "粗朴",
    "traditional": "传统",
    "light luxury": "轻奢",
    "minimal": "极简",
    "minimalist": "极简主义",
    "eclectic": "混搭/折衷主义",
    "mashup": "混搭/折衷主义",
    "funky": "放客风格",
    "transitional": "过渡风格",
    "shabby chic": "新怀旧风格",
    "eco friendly/green design": "环保设计",
    "recycled": "可回收",
    "other": "其他"
}
need_style = ["Victorian", "Classic", "European", "Vintage", "Swedish", "Chinese Modern", "Contemporary", "Country", "Mediterranean"]
style_dict = {
    "Victorian": "european",
    "European": "european",
    "Classic": "european",
    "Neo-classical": "european",
    "Neoclassical": "european",
    "Asian antique": "chinese",
    "Vintage": "european",
    "Antique": "european",
    "Swedish": "nordic",
    "Nordic": "nordic",
    "North-europe": "nordic",
    "Midcentury": "european",
    "Modern": "modern",
    "Mediterranean": "european",
    "Tuscan": "european",
    "Bohemian chic": "european",
    "Chinese": "chinese",
    "Chinese Modern": "chinese",
    "Japan": "nordic",
    "Japanese": "nordic",
    "Korea": "nordic",
    "Korean modern": "nordic",
    "Asan": "chinese",
    "Asian": "chinese",
    "Islamic": "european",
    "Country": "european",
    "Us": "european",
    "Contemporary": "modern",
    "Industrial": "modern",
    "Urban": "modern",
    "Retro": "modern",
    "Beach": "modern",
    "Tropical": "modern",
    "Coastal": "modern",
    "Cottage": "modern",
    "Rural": "european",
    "Garden": "european",
    "Cold color": "modern",
    "Warm color": "modern",
    "Rustic": "modern",
    "Traditional": "european",
    "Light luxury": "modern",
    "Minimal": "modern",
    "Minimalist": "modern",
    "Eclectic": "modern",
    "Mashup": "modern",
    "Funky": "modern",
    "Transitional": "modern",
    "Shabby chic": "modern",
    "Eco friendly/green design": "modern",
    "Recycled": "modern",
    "Other": "modern"
}


def change_jr_to_recon_style(jr_style):
    if jr_style in style_dict:
        return style_dict[jr_style]
    else:
        return 'modern'


class RoomBuildDict:
    def __init__(self):
        self.ROOM_BUILD_TYPE_DICT = {
            'LivingDiningRoom': 'LivingDiningRoom',
            'LivingRoom': 'LivingDiningRoom',
            'DiningRoom': 'LivingDiningRoom',
            'MasterBedroom': 'MasterBedroom',
            'SecondBedroom': 'MasterBedroom',
            'Bedroom': 'MasterBedroom',
            'KidsRoom': 'KidsRoom',
            'ElderlyRoom': 'MasterBedroom',
            'NannyRoom': 'MasterBedroom',
            'Library': 'Library',

            'Kitchen': 'Kitchen',
            'MasterBathroom': 'Bathroom',
            'SecondBathroom': 'Bathroom',
            'Bathroom': 'Bathroom',
            'Balcony': 'Balcony',
            'Terrace': 'Balcony',
            'Lounge': 'Library',

            'Hallway': 'LivingDiningRoom',
            'Aisle': 'LivingDiningRoom',
            'Corridor': 'LivingDiningRoom',
            'Stairwell': 'LivingDiningRoom',
            'StairWell': 'LivingDiningRoom',

            # 'LaundryRoom': 'Other',
            # 'StorageRoom': 'Other',
            # 'CloakRoom': 'Other',
            # 'EquipmentRoom': 'Other',
            # 'Auditorium': 'Other',
            # 'OtherRoom': 'Other',
            # 'undefined': 'Other',
            # 'none': 'Other',
            # '': 'Other',
            'LaundryRoom': 'MasterBedroom',
            'StorageRoom': 'MasterBedroom',
            'CloakRoom': 'MasterBedroom',
            'EquipmentRoom': 'MasterBedroom',
            'Auditorium': 'MasterBedroom',
            'OtherRoom': 'MasterBedroom',
            'undefined': 'MasterBedroom',
            'none': 'MasterBedroom',
            '': 'MasterBedroom',
            'Other': 'MasterBedroom',

            'Courtyard': '',
            'Garage': ''
        }

    def __getitem__(self, item):
        if item in self.ROOM_BUILD_TYPE_DICT:
            return self.ROOM_BUILD_TYPE_DICT[item]
        else:
            return ''


ROOM_BUILD_TYPE = RoomBuildDict()


def is_hallway(room_type):
    return room_type in ['Hallway', 'Aisle', 'Corridor', 'Stairwell']

PRIME_GENERAL_WALL_ROOM_TYPES = ['MasterBedroom', 'SecondBedroom', 'Bedroom', 'KidsRoom', 'ElderlyRoom', 'NannyRoom', 'Library']