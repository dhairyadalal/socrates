from dialog_simulator import *

domain_config = "sample_domains/movies/movie_domain.yaml"
domain_kb_file_path = "sample_domains/movies/moviekb.csv"

starting_goal_path = "sample_domains/movies/sample_starting_goals.yml"
usersim_nlg_path = "sample_domains/movies/nlg_usersim_rules.yml"
agent_nlg_path = "sample_domains/movies/nlg_agent_rules.yml"

# domain
dc = import_domain_yaml(domain_config)
kb = DomainKBtable("table", domain_kb_file_path, "csv")
dc.add_domain_kb(kb)

# NLG
nlg_dict = import_yaml(usersim_nlg_path)
unlg = NLG("dict", nlg_dict)


sg = import_yaml(starting_goal_path)
import random

gc = random.choice(sg)
goal = DialogGoal( gc["inform_slots"], gc["request_slots"] )

from sample_domains import MovieUserSim, MovieAgent

usersim = MovieUserSim(dc)
usersim.set_nlg(unlg)
usersim.reset(goal)

print(goal.inform_slots)
action = DialogAction("request", params={ "theater":None })
print(usersim.next(action, -1))


nlg_dict = import_yaml(agent_nlg_path)
anlg = NLG("dict", nlg_dict)

action= DialogAction("request", params={"movie":None, "theater":None, "genre":"horror"})
agent = MovieAgent(dc)
agent.set_nlg(anlg)

print(agent.next(action, 1))