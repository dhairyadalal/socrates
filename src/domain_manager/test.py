from domain_helpers import DomainManager, Domain
import json

# 1. Create domain manager
domain_manager = DomainManager()

# 2. Specify dialog acts
dialog_acts = ["inform", "request", "affirm", "negate", "greetings", "bye"]

# Get inform and request slots

dat = json.load(open("../../sample_data/Restaurant_Domain/ontology_dstc2.json", "rb"))
print(dat.keys())


#rest_domain = Domain(name = "restaurant_search", )

