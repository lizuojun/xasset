import requests
import threadpool
import json

name_list = [i for i in range(10)]
pool = threadpool.ThreadPool(10)
IGARPH_ITEM_INFO = 'https://tui.alibaba-inc.com/recommend?appid=21150&model_jid='
IGARPH_SIMILAR_ITEMS = 'https://tui.alibaba-inc.com/recommend?appid=23187&model_jid='


def get_item_info_from_igraph(jid, out_table, igraph):
    url = igraph + jid
    try:
        r = requests.get(url, timeout=1)
        r.raise_for_status()
        out = json.loads(r.content.decode('gbk'))
        out = out['result']
        out_table[jid] = out
        # print('get_item_info_from_igraph ok!', jid)
    except:
        out_table[jid] = []
        print('get_item_info_from_igraph error!')


def get_model_attributes(jid_list):
    multi_thread_input_list = []
    multi_thread_output_table = {}

    # 并行化访问igraph！
    for jid in jid_list:
        dict_vars = [jid, multi_thread_output_table, IGARPH_ITEM_INFO]
        multi_thread_input_list += [(dict_vars, None)]
    pool_requests = threadpool.makeRequests(get_item_info_from_igraph, multi_thread_input_list)
    [pool.putRequest(req) for req in pool_requests]
    pool.wait()
    for k, v in multi_thread_output_table.items():
        if len(v) == 0:
            multi_thread_output_table[k] = {}
        else:
            multi_thread_output_table[k] = v[0]
    return multi_thread_output_table


def get_similar_model_list(jid_list):
    multi_thread_input_list = []
    multi_thread_output_table = {}

    # 并行化访问igraph！
    for jid in jid_list:
        dict_vars = [jid, multi_thread_output_table, IGARPH_SIMILAR_ITEMS]
        multi_thread_input_list += [(dict_vars, None)]
    pool_requests = threadpool.makeRequests(get_item_info_from_igraph, multi_thread_input_list)
    [pool.putRequest(req) for req in pool_requests]
    pool.wait()
    for k, v in multi_thread_output_table.items():
        if len(v) == 0:
            multi_thread_output_table[k] = {}
        else:
            multi_thread_output_table[k] = v[0]
    return multi_thread_output_table


if __name__ == '__main__':
    jid_list = [
        "15db50c6-e38a-483e-b7ed-d9df172de548", "16336834-3f05-46aa-851d-4d169fc68d24",
        "18e65913-e399-4f30-965f-c14de1e27082", "1bf7ffe8-bbde-4758-8b8a-9b939b332da9",
        "201bf206-da23-422a-a46c-573383a482f4", "208bffe1-3a74-4f27-9a75-88b13d90a410",
        "23f16681-07f9-4128-9544-40051d8bf3fb", "246e5c84-b259-4c2b-abd8-ec9b105ccc85",
        "278d4982-9f76-49db-b508-65c84cef5162", "2a8b24ae-0331-4453-847b-72fb5518bfad",
        "2bf2fafb-15ea-47fe-9953-167f5e7a7191", "2db27eb4-cf15-46ba-8b76-5ae2b697ef76",
        "3044c69b-7f04-4954-965d-d2ed42b25157", "30e8aca4-91a2-41f4-9997-67d323fb6cba",
        "35b200df-d975-4e87-8b07-cb27cbf6ab60", "37e2493a-6884-442f-960d-cc1505e25565",
        "3ba46682-4453-4fcd-9ae4-92bd9553c274", "3cc8a861-7f00-466a-82c8-7945d5b1aaef",
        "40d875c9-5470-4b48-8f0e-afc102dd8daf", "4327dffc-3201-4dd5-88f9-2d3ab028d4d6",
        "43f27098-cd6e-41eb-bc79-adda5c3f9227", "47140497-0923-4ba5-8d57-4c006b891849",
        "47dbd630-9785-41a9-a998-00c297e0f205", "49f7ed9a-ed85-4c0b-9877-896c9326770e",
        "4a1ae2ba-aefc-44cc-b5e6-b1decd779100", "4d6e729c-30de-48f1-9b3e-522861b38be0",
        "563159db-0a16-49f4-8a77-9190080cbd45", "5c4ec4ee-f1de-4557-98a7-81f473da99fa",
        "5edf86e2-e9ad-4299-afab-f5437fe9c821", "6023fc79-51ee-460c-93c4-3ac58ea33c4a"

    ]
    res = get_model_attributes(jid_list)
    res = get_similar_model_list(jid_list)
    print('')
