STYLE_DICT = {"Chinese": ["Chinese", "Chinese Modern", "新中式", "明清古典", "中式"],
              "Modern": ["Modern", "Minimalist", "Minimal", "极简主义",
                         "Contemporary", "极简", "现代"],
              "European": ["European", 'Victorian', "European", "Classic", "Vintage", "复古怀旧", "简欧/新古典", "欧式/古典"],
              "Country": ["Country", "美式乡村", "美式"],
              "Nordic": ["北欧", "Swedish", "Nordic"],
              "Luxury": ["Light Luxury", "轻奢", "Luxury"],
              "Japanese": ["日式", "Japanese"]}


# 离线解析使用，映射基本风格大类，其他小众 不明的风格归为other
def check_base_style(style):
    for key in STYLE_DICT:
        if style in STYLE_DICT[key]:
            return key

    return "Other"


# 输入风格映射，映射到四个基本风格上
def get_target_style(style):
    if len(style) == 0:
        return ""

    for key in STYLE_DICT:
        if style in STYLE_DICT[key]:
            return key

    return "Modern"
