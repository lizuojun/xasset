import json

from Extract.extract_cache import get_house_data, get_house_sample

all_design_list = json.load(open("all_design_list.json", "r"))
#
#

all_jid = json.load(open("../material_jid_info.json", "r"))
out = {}
for design_data in all_design_list:
    design_id, design_url, scene_url = design_data

    _, house_data = get_house_data(design_id,
                                   design_url=design_url,
                                   scene_url=scene_url)
    print(design_id)
    sample_para, sample_data, sample_layout, sample_group = get_house_sample(design_id, reload=True)

    for room_d in sample_group:
        group_functional = sample_group[room_d]["group_functional"]
        group_decorative = sample_group[room_d]["group_decorative"]

        if len(group_functional) == 0:
            continue
        for g in group_decorative:
            if g["type"] == "Door":
                for obj in g["obj_list"]:
                    if obj["id"] not in out:
                        if "pocket" in obj:
                            out[obj["id"]] = obj
        print()

for i in out:
    if i not in all_jid:
        all_jid[i] = out[i]

with open("new_mat_jid.json", "w") as f:
    f.write(json.dumps(all_jid))

