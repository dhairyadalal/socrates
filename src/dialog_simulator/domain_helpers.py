import pickle
import random
import yaml


class Domain:

    # Functions to update Domain
    def add_request_slots(self, request_slots: list)->None:
        if request_slots is not None:
            self.request_slots.extend(request_slots)
        else:
            self.request_slots = request_slots

    def add_inform_slots(self, new_inform_slots: list)->None:

        if self.inform_slots is not None:
            for item in new_inform_slots:
                self.inform_slots.update(item)
        else:
            self.inform_slots = new_inform_slots

    def add_domain_kb(self, domain_kb):
        self.domain_kb = domain_kb

    # Functions to retrieve Domain values
    def sample_inform_slot(self) -> str:
        return random.choice(self.inform_slots)

    def sample_inform_slot_value(self, inform_slot: str) -> str:
        return random.choice(self.inform_slot_values[inform_slot])

    def sample_request_slot(self):
        return random.choice(self.request_slots)

    def get_all_inform_slots(self) -> list:
        return self.inform_slots

    def get_all_request_slots(self) -> list:
        return self.request_slots

    def get_all_inform_slot_values(self) -> dict:
        return self.inform_slot_values

    def get_valid_user_goals(self) -> list:
        return self.valid_user_goals

    def __init__(self, domain_name, version_number=None, dialog_acts=None, request_slots=None,
                 inform_slots=None, valid_user_goals=None, inform_slot_values=None, domain_kb=None):
        self.domain_name = domain_name
        self.version = version_number
        self.dialog_acts = dialog_acts
        self.request_slots = request_slots
        self.inform_slots = inform_slots
        self.valid_user_goals = valid_user_goals
        self.inform_slot_values = inform_slot_values
        self.domain_kb = domain_kb

    def __str__(self):
        return "Domain: %s | Version: %s " % (self.domain_name, self.version)


class DomainManager:

    # Manage Domains
    def add_domain(self, domain: Domain)->None:
        if domain is None:
            raise ValueError("Error: Invalid domain object. Domain is NoneType.")
        elif domain.domain_name in self.domains:
            raise ValueError("Error: %s already exists in domain list. Call remove_domain before adding new domain"
                             % domain)
        else:
            self.domains[domain.domain_name] = domain
            self.domain_names.append(domain.domain_name)

    def update_domain(self, domain: Domain) -> None:
        print("updating domain",  domain.domain_name)
        self.domains[domain.domain_name] = domain

    def get_domain(self, domain_name:str)->Domain:
        return self.domains[domain_name]

    def remove_domain(self, domain: Domain)->None:
        self.domain_names.remove(domain.domain_name)
        self.domains.pop(domain, None)

    def save_domains(self, path: str)->str:
        if path[-1] != '/':
            path += '/'
        pickle.dump(self, open(path + self.default_name, 'wb'))
        return "Saved domains to: " + path + self.default_name

    # Load Domains
    def load_domains(self, path: str)->None:
        if path[-1] != '/':
            path += '/'
        tmp = pickle.load(open(path + self.default_name, "rb"))
        self.domain_names = tmp.domain_names
        self.domains = tmp.domains

    # Import Domains
    def _load_yaml(self, file_path: str)->dict:
        try:
            file = yaml.safe_load(open(file_path))
            return file
        except ImportError:
            raise("Error: unable import %s." % file_path)

    def import_domain(self, file_path: str, file_type: str)->None:
        if file_type == "yaml":
            file = self._load_yaml(file_path)
            if file is not None:
                domain = Domain(domain_name = file["domain_name"],
                                version_number = file["version"],
                                dialog_acts = file["dialog_acts"],
                                request_slots = file["request_slots"],
                                inform_slots = file["inform_slots"],
                                valid_user_goals = file["valid_user_goals"],
                                inform_slot_values = file["inform_slot_values"],
                                domain_kb = None)
                self.add_domain(domain)
                print("Successfully imported %s domain. Use get_domain('%s') to access domain object."
                      % (file["domain_name"], file["domain_name"]))
            else:
                raise ValueError("Error: Load_yaml failed, NoneType returned.")

    def __init__(self):
        self.domain_names = []
        self.domains = {}
        self.default_name = "domains.pkl"

    def __str__(self):
        return "Current domains: " + str(self.domain_names)








