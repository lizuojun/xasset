import os
import json
from tqdm import tqdm


def get_child_jid(dict_data, jid_list):
    if 'id' in dict_data:
        jid_list.append(dict_data['id'])
    if 'children' in dict_data:
        for child in dict_data['children']:
            jid_list = get_child_jid(child, jid_list)
    return jid_list


data = json.load(open(os.path.join(os.path.dirname(__file__), './material_category_id.json')))
supported_cate_list = []
supported_cate_list = get_child_jid(data, supported_cate_list)
supported_jid_list = []
with open(os.path.join(os.path.dirname(__file__), '/Users/liqing.zhc/code/ihome-layout/LayoutDecoration/sample_room/calcifer_model_support_mobile_scene_1621410616703.txt')) as f:
    org_data = f.readlines()
    for line in tqdm(org_data):
        line = line.strip('\n')
        jid, prop = line.split('\t')
        flag = True
        prop_res = ''
        for i, c in enumerate(prop[1:-1]):
            if c == '"':
                if flag:
                    flag = False
                    continue
                else:
                    prop_res += c
                    flag = True
            elif c == '\\' and prop[i+2] != '"':
                continue
            else:
                prop_res += c
        # prop_res = prop_res.replace('\\"', '')
        # prop_res = prop_res.replace('\\', '')
        try:
            prop = json.loads(prop_res)
        except Exception as e:

            ind = prop.find('category_id')
            if ind < 0:
                print(jid, prop)
                print('-------------------------------')
                continue
            start = ind + len('category_id')
            break_flag = False
            for c in prop[ind + len('category_id'):]:
                if c in ['"', ':']:
                    start += 1
                else:
                    break_flag = True
                    break
            if not break_flag:
                print(jid, prop)
                print('-------------------------------')
                continue
            end = start
            break_flag = False
            for c in prop[start:]:

                if c == '"':
                    break_flag = True
                    break
                end += 1
            if not break_flag:
                print(jid, prop)
                print('-------------------------------')
                continue

            cid = prop[start:end]

            # supported
            ind = prop.find('support_mobile_scene')
            if ind < 0:
                print(jid, prop)
                print('-------------------------------')
                continue
            start = ind + len('support_mobile_scene')
            break_flag = False
            for c in prop[ind + len('support_mobile_scene'):]:
                if c in ['"', ':']:
                    start += 1
                else:
                    break_flag = True
                    break
            if not break_flag:
                print(jid, prop)
                print('-------------------------------')
                continue
            end = start
            break_flag = False
            for c in prop[start:]:

                if c == '"':
                    break_flag = True
                    break
                end += 1
            if not break_flag:
                print(jid, prop)
                print('-------------------------------')
                continue
            supported = prop[start:end]

            prop = {
                'support_mobile_scene': supported,
                'category_id': cid
            }
        if prop['support_mobile_scene'] == 'true' and 'category_id' in prop and 'support_mobile_scene' in prop \
                and prop['category_id'] in supported_cate_list:
            supported_jid_list.append(jid)

supported_jid_list = list(set(supported_jid_list))
print(len(supported_jid_list))
with open(os.path.join(os.path.dirname(__file__), 'hs_support_list.txt'), 'w') as f:
    json.dump(supported_jid_list, f)