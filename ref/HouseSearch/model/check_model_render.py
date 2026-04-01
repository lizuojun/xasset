import json

all_need_jids = open("temp/all_jids_new.txt").read().split()

all_check_jids = open("temp/temp_rd_model_check_jid_support_1612516157092.txt").readlines()
all_checked_json = {}
for i in all_check_jids:
    if len(i) > 10:
        jid, checked = i.split(',')
        if "true" in checked:
            all_checked_json[jid] = True
        else:
            all_checked_json[jid] = False

out_need_jids = []
cannot_change_jids = []
for need_jid in all_need_jids:
    if need_jid in all_checked_json:
        out_need_jids.append(need_jid)
    else:
        cannot_change_jids.append(need_jid)

with open("temp/need_new.txt", "w") as f:
    for i in out_need_jids:
        f.write(i + "\n")
