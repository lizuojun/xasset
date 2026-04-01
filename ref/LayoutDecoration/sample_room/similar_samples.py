import json
import os
import time
from ..net_utils.igraph_request import get_similar_model_list, get_model_attributes


class SimilarHard:
    def __init__(self):
        t = time.strftime('%Y-%m-%d')
        if os.path.exists(os.path.join(os.path.dirname(__file__), 'online_hard_lib.json')):
            self.ONLINE_HARD_LIBS = json.load(open(os.path.join(os.path.dirname(__file__), 'online_hard_lib.json'), 'rb'),
                                              encoding='utf-8')
        else:
            self.ONLINE_HARD_LIBS = {}
        if os.path.exists(os.path.join(os.path.dirname(__file__), 'hard_similar_dict.json')):
            self.HARD_SIMILAR_DICT = json.load(open(os.path.join(os.path.dirname(__file__), 'hard_similar_dict.json'), 'rb'),
                                              encoding='utf-8')
        else:
            self.HARD_SIMILAR_DICT = {}
        self.need_update = False
        if 'time' in self.HARD_SIMILAR_DICT:
            if self.HARD_SIMILAR_DICT['time'] != t:
                self.need_update = True
        else:
            self.HARD_SIMILAR_DICT['time'] = t

    def get_similar_hard_item(self, jid_list):
        res_jid_dict = {}
        remained_jid_list = []
        if not self.need_update:
            for jid in jid_list:
                if jid in self.HARD_SIMILAR_DICT:
                    if len(self.HARD_SIMILAR_DICT[jid]) == 0:
                        remained_jid_list.append(jid)
                        continue
                    else:
                        black_list = self.HARD_SIMILAR_DICT[jid]['black_list']
                        similar_list = self.HARD_SIMILAR_DICT[jid]['local_similarity'].split(',')  #zncz_similarity
                        similar_list = [i for i in similar_list if len(i) != 0 and i not in black_list]
                        if len(similar_list) == 0:
                            similar_list = self.HARD_SIMILAR_DICT[jid]['local_similarity'].split(',')
                            similar_list = [i for i in similar_list if len(i) != 0 and i not in black_list]
                            if len(similar_list) == 0:
                                similar_list = self.HARD_SIMILAR_DICT[jid]['global_similarity'].split(',')
                                similar_list = [i for i in similar_list if len(i) != 0 and i not in black_list]
                                if len(similar_list) == 0:
                                    similar_list = []
                    res_jid_dict[jid] = similar_list
                else:
                    remained_jid_list.append(jid)
        else:
            self.need_update = False
            remained_jid_list = jid_list.copy()
        igraph_res = get_similar_model_list(remained_jid_list)
        for k, v in igraph_res.items():
            if len(v) == 0:
                similar_list = []
            else:
                v['black_list'] = []
                self.HARD_SIMILAR_DICT[k] = v
                similar_list = v['local_similarity'].split(',') #  zncz_similarity
                similar_list = [i for i in similar_list if len(i) != 0]
                if len(similar_list) == 0:
                    similar_list = v['local_similarity'].split(',')
                    similar_list = [i for i in similar_list if len(i) != 0]
                    if len(similar_list) == 0:
                        similar_list = v['global_similarity'].split(',')
                        similar_list = [i for i in similar_list if len(i) != 0]
                        if len(similar_list) == 0:
                            similar_list = []
            res_jid_dict[k] = similar_list
        if len([i for i in igraph_res if len(i) != 0]) > 0:
            with open(os.path.join(os.path.dirname(__file__), 'hard_similar_dict.json'), 'w') as f:
                json.dump(self.HARD_SIMILAR_DICT, f, indent='  ')
        return res_jid_dict

    def get_jid_attribute(self, jid_list):

        res_jid_dict = {}
        remained_jid_list = []
        for jid in jid_list:
            if jid in self.ONLINE_HARD_LIBS:
                res_jid_dict[jid] = self.ONLINE_HARD_LIBS[jid]
            else:
                remained_jid_list.append(jid)

        igraph_res = get_model_attributes(remained_jid_list)
        for k, v in igraph_res.items():
            self.ONLINE_HARD_LIBS[k] = v
            res_jid_dict[k] = v
        if len(remained_jid_list) > 0:
            with open(os.path.join(os.path.dirname(__file__), 'online_hard_lib.json'), 'w') as f:
                json.dump(self.ONLINE_HARD_LIBS, f, indent='  ')
        return res_jid_dict

    def get_material(self, jid, hard_type, attr):
        model_size = attr['model_size']
        model_size = model_size.split('&')
        model_size = [float(i[2:]) for i in model_size]
        image_url = attr['image_url']
        formated_mat = {
            'code': 1,
            "texture": image_url,
            "jid": jid,
            "uv_ratio": [100. / model_size[0], 0, 100. / model_size[1], 0],
            "color": [255, 255, 255, 255] if 'color' not in attr or isinstance(attr['color'], str) else attr['color'],
            'type': hard_type
        }
        return formated_mat

    def get_door(self, jid, attr):
        model_size = attr['model_size']
        model_size = model_size.split('&')
        model_size = [float(i[2:]) for i in model_size]
        ret_door = {'jid': jid,
                    'size': [model_size[0] / 100., model_size[2] / 100., model_size[1] / 100.]}

        return ret_door



