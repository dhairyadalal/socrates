from dialog_simulator import *

kb_path = "sample_domains/restaurant/restaurants_kb.json"

kb = DomainKBsimple(type="tbl", kb_path=kb_path, kb_file_type="json")

params = {"cuisine": "indian", "area":"central"}

print(kb.get_suggestions(params))