from collections import Counter

STYLE_DICT = {"Chinese": ["Chinese", "Chinese Modern", "新中式", "明清古典", "中式"],
              "Modern": ["Modern", "Minimalist", "Minimal", "极简主义",
                         "Contemporary", "极简", "现代"],
              "European": ["European", 'Victorian', "European", "Classic", "Vintage", "复古怀旧", "简欧/新古典", "欧式/古典"],
              "Country": ["Country", "美式乡村", "美式"],
              "Nordic": ["北欧", "Swedish", "Nordic"],
              "Luxury": ["Light Luxury", "轻奢", "Luxury"],
              "Japanese": ["日式", "Japanese", "Japan"]}


def change_base_style(style):
    for i in STYLE_DICT:
        if style in STYLE_DICT[i]:
            return i
    return "Modern"


def get_furniture_list_target_style(furniture_seeds_note):
    style = []
    for seed_id in furniture_seeds_note:
        seed = furniture_seeds_note[seed_id]
        style.append(change_base_style(seed["style"]))
    if len(style) == 0:
        return ["Modern", "Luxury"]
    c = Counter(style)
    max_style = c.most_common(1)[0]
    if max_style[1] == 1:
        return [max_style[0]]
    else:
        return [max_style[0]]


def get_check_styles(input_style):
    if input_style in ["all", "random", ""]:
        return {"Luxury": [], "Modern": [], "Nordic": [], "Japanese": []}
    else:
        base_style = change_base_style(input_style)
        return {base_style: []}


# 设计家style转换
def spec_style_change(input_style):
    style_keys = [("country", "田园"),

                  ("ASAN", "东南亚"),

                  ("other", "其他"),

                  ("Nordic", "Nordic"),

                  ("Japan", "Japanese"),

                  ("european", "欧式"),

                  ("mediterranean", "地中海"),

                  ("chinese", "中式"),

                  ("modern", "Modern"),

                  ("Mashup", "混搭"),

                  ("neoclassical", "新古典"),

                  ("US", "美式"),

                  ("Korea", "韩式"),

                  ("ModernAmerican", "简美"),

                  ("NeoChinese", "新中式"),

                  ("EntryLuxury", "Luxury"),

                  ("emptyStyle", "无")]
    for key in style_keys:
        if key[0] == input_style:
            return key[1]
    return "现代"