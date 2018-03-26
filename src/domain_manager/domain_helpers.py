import pickle
import random


class DialogTemplates:

    def __init__(self):
        self.dialog_acts =[]
        self.dialog_templates = {}

    def add_dialog_act(self, dialog_act:str)->None:
        self.dialog_acts.append(dialog_act)
        if dialog_act not in self.dialog_templates.keys():
            self.dialog_templates[dialog_act] = {}

    def add_dialog_tempate(self, dialog_act: str, key: str, template: str)->None:
        self.dialog_acts[dialog_act][key] = template


class Domain:

    def add_request_slots(self, request_slots: list)->None:
        if request_slots is not None:
            self.request_slots.extend(request_slots)
        else:
            self.request_slots = request_slots

    def add_inform_slots(self, new_inform_slots: list)->None:

        if self.inform_slots is not None:
            for item in new_inform_slot:
                self.inform_slots.update(item)
        else:
            self.inform_slots = new_inform_slots

    def add_dialog_acts(self, dialog_acts: list)->None:
        self.dialog_acts = dialog_acts

    def add_dialog_act(self, dialog_act:str)->None:
        self.dialog_acts.append(dialog_act)

    def add_domain_kb(self, domain_kb):
        self.domain_kb = domain_kb

    def __init__(self, domain_name, dialog_acts=None, request_slots=None, inform_slots=None, domain_kb=None):
        self.domain_name = domain_name
        self.dialog_acts = dialog_acts
        self.request_slots = request_slots
        self.inform_slots = inform_slots
        self.domain_kb = domain_kb



    def sample_inform_slot(self, inform_slot):
        return random.choice(self.inform_slots[inform_slot])

    def sample_request_slot(self):
        return random.choice(self.request_slots)

class DomainManager:

    def __init__(self):
        self.domain_names =[]
        self.domains = {}
        self.dialog_templates = {}
        self.default_path = "../data/domains.pkl"

    def add_domain(self, domain: Domain)->None:
        if domain is None:
            raise ValueError("Error: Invalid domain object. Domain is NoneType.")
        elif domain.domain_name in self.domains:
            raise ValueError("Error: %s already exists in domain list. Call remove_domain before adding new domain"
                             % domain)
        else:
            self.domains[domain.domain_name] = domain
            self.domain_names.append(domain.domain_name)

    def get_domain(self, domain_name:str)->Domain:
        return self.domains[domain_name]

    def remove_domain(self, domain: Domain)->None:
        self.domain_names.remove(domain.domain_name)
        self.domains.pop(domain, None)

    def save_domains(self, path=None)->str:
        if path is None:
            path = self.default_path
        pickle.dump(self, open(path, 'wb'))
        return path

    def load_domains(self)->None:
        tmp = pickle.load(open(self.default_path, "rb"))
        self.domain_names = tmp.domain_names
        self.domains = tmp.domains
        self.dialog_templates = tmp.dialog_templates

    def add_dialog_templates(self, domain_name:str, dialog_templates: DialogTemplates) -> None:
        self.dialog_templates[domain_name] = dialog_templates

    def __str__(self):
        return "Current domains: " + str(self.domain_names)








