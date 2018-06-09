import pickle
import random
import pandas as pd
from .utils import *

class Domain:

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

    def __str__(self):
        return "Domain: %s | Version: %s " % (self.domain_name, self.version)


class DomainManager:

    def __init__(self):
        self.domain_names = []
        self.domains = {}
        self.default_name = "domains.pkl"

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

    def __str__(self):
        return "Current domains: " + str(self.domain_names)


class DomainKB(object):

    def __init__(self, type: str):
        self.type = type
        self.kb = None

    def get_suggestions(self, params: dict, num_results: int) -> list:
        pass

    def validate_suggestion(self, suggestion: dict, user_params: dict) -> float:
        pass

    def get_item(self, params):
        pass


class DomainKBtable(DomainKB):

    def __init__(self, type: str, kb_path: str, kb_file_type: str):
        super(DomainKBtable, self).__init__(type)
        self.tbl = self._load_kb(kb_path, kb_file_type)

    def _load_kb(self, kb_path, kb_file_type) -> 'pandas.DataFrame':
        if kb_file_type == "json":
            return pd.read_json(kb_path)
        if kb_file_type == "csv":
            return pd.read_csv(kb_path)

    def get_suggestions(self, params: dict, num_results: int) -> list:

        # 1. Check if exact match exists
        results = self._extact_match(params)

        if len(results) == 0:
            results = self._or_match(params)
            results = self.rank_results(results, params)

            return results[:num_results]

        else:
            return [(json.loads(row.to_json()), 1.0) for _, row in results.iterrows()][:num_results]

    def validate_suggestion(self, suggestion: dict, user_params: dict) -> float:
        return 0

    def get_item(self, params) -> dict:
        return {}

    def _extact_match(self, params: dict) -> 'pandas.DataFrame':
        query = [str(key) + "=='" + str(val) + "'" for key, val in params.items()]
        query = '&'.join(query)
        return self.tbl.query(query)

    def _or_match(self, params: dict) -> 'pandas.DataFrame':
        query = [str(key) + "=='" + str(val) + "'" for key, val in params.items()]
        query = '|'.join(query)
        return self.tbl.query(query)

    @staticmethod
    def _sim_score(set1: set, set2: set) -> float:
        return len(set1.intersection(set2)) / len(set2)

    def rank_results(self, results: 'pandas.DataFrame', params: dict) -> list:

        param_val_set = set(params.values())
        param_key_list = list(params.keys())
        result_list = []

        for _, row in results.iterrows():
            row_vals_set = set(row[param_key_list].values)
            result_list.append((json.loads(row.to_json()),
                                self._sim_score(row_vals_set, param_val_set)))

        return sorted(result_list, key=lambda tup: tup[1], reverse=True)


# Public method for Domain digestion
def import_domain_yaml(file_path: str) -> Domain:
    try:
        file = import_yaml(file_path)
        if file is None:
            raise ImportError("File was empty. Unable to load domain.")

        domain = Domain(domain_name=file["domain_name"],
                        version_number=file["version"],
                        dialog_acts=file["dialog_acts"],
                        request_slots=file["request_slots"],
                        inform_slots=file["inform_slots"],
                        valid_user_goals=file["valid_user_goals"],
                        inform_slot_values=file["inform_slot_values"],
                        domain_kb=None)
        return domain
    except Exception:
        raise ImportError("Error: Failed to load %s." % file_path)
