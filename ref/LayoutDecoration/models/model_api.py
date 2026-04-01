import os
import json
import requests

MODEL_ATTR_URL = 'https://api.shejijia.com/fpmw/api/rest/v2.0/product/%s?t=ezhome'
MODEL_ATTR_BUFFER = os.path.join(os.path.dirname(__file__), './model_attrs.json')
if os.path.exists(MODEL_ATTR_BUFFER):
    model_attrs = json.load(open(MODEL_ATTR_BUFFER))
else:
    model_attrs = {}
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'}


def get_model_attr(jid):
    if jid in model_attrs:
        data = model_attrs[jid]
    else:
        url = MODEL_ATTR_URL % jid
        try:
            # print(url)
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            if res.ok:
                data = json.loads(res.content)
                model_attrs[jid] = data
                json.dump(model_attrs, open(MODEL_ATTR_BUFFER, 'w'), ensure_ascii=False)
            else:
                data = {}
        except Exception as e:
            print(e)
            data = {}
    return data


def get_attr_calcifer_id(jid):
    attrs = get_model_attr(jid)
    for attr in attrs['item']['attributes']:
        if 'id' in attr and attr['id'] == 'attr-calcifer-id':
            if 'free' in attr and len(attr['free']) > 0:
                return attr['free'][0]
    return None


if __name__ == '__main__':
    jid = '2ab283b6-c838-48ef-bd72-22933afde3b7'
    attr = get_model_attr(jid)
    print(attr)
