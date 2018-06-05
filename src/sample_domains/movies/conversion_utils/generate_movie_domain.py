""" Script was used to convert TC-Bot data into socrates format """

import pandas
import json
import re


# Generate movie kb csv
with open("../tc_bot_movie_data/moviekb_dict.json", "r") as file:
    j = file.read()
data = json.loads(j)

tbl = []
for k, v in data.items():
    tbl.append(v)

pandas.DataFrame(tbl).to_csv("../moviekb.csv")

# generate agent and user nlg rules from nl_pairs.json
with open("../tc_bot_movie_data/nl_pairs.json", "r") as file:
    nl_pairs = json.loads(file.read())
    file.close()

r = re.compile(r"(?:^|\s)([$])(\w+)([$])")

agent_nlg = {'domain': 'movie', 'version': 1.0, 'regex': "(?:^|\s)([$])(\w+)([$])",
             'dialog_acts': {}}
usersim_nlg = {'domain': 'movie', 'version': 1.0, 'regex': "(?:^|\s)([$])(\w+)([$])",
               'dialog_acts': {}}

for k, v in nl_pairs["dia_acts"].items():
    usr = dict()
    agt = dict()

    # handle requests seperately
    for i in v:
        if len(i["inform_slots"]) == 0:
            usr.update({'default': i["nl"]["usr"]})
            agt.update({'default': i["nl"]["agt"]})
        else:
            ik = ','.join(sorted(i["inform_slots"]))
            usr.update({ik: i["nl"]["usr"]})
            agt.update({ik: i["nl"]["agt"]})

        if len(i["request_slots"]) > 0:
            ik = ','.join(sorted(i["inform_slots"]))
            usr.update({ik: i["nl"]["usr"]})
            agt.update({ik: i["nl"]["agt"]})

    # Update nlg respectively w/ extracted templates
    agent_nlg.get('dialog_acts').update({k: agt})
    usersim_nlg.get('dialog_acts').update({k: usr})

with open("../nlg_agent_rules.json", "w") as file:
    json.dump(agent_nlg, file, indent=4)

with open("../nlg_usersim_rules.json", "w") as file:
    json.dump(usersim_nlg, file, indent=4)

# Import starting goals
with open("../tc_bot_movie_data/user_first_goals.json", "r") as file:
    first_goals = json.loads(file.read())
    file.close()

discard = [ item.pop('diaact') for item in first_goals ]

with open("../ssample_staring_goals.json", "w") as file:
    json.dump(first_goals, file, indent=4)
