from dialog_simulator import *
domain_config = "sample_domains/movies/movie_domain.yaml"
domain_kb_file_path = "sample_domains/movies/moviekb.csv"

starting_goal_path = "sample_domains/movies/sample_starting_goals.json"
usersim_nlg_path = "sample_domains/movies/nlg_usersim_rules.json"
agent_nlg_path = "sample_domains/movies/nlg_agent_rules.json"

# domain
dc = import_yaml(domain_config)
kb = DomainKBtable("table", domain_kb_file_path, "csv")

# NLG
nlg_dict = import_json(usersim_nlg_path)
unlg = NLG("dict", nlg_dict)

nlg_dict = import_json(agent_nlg_path)
anlg = NLG("dict", nlg_dict)

sg = import_json(starting_goal_path)
import random
print(random.choice(sg))