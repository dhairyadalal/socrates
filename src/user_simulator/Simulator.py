import yaml
import random
import re


class UserSimulator(object):

    def generate_user_goal(self):
        print("Generating User Goal")
        if self.goal_type == "template":
            print(self.starting_goals)
            self.user_goal = random.choice(self.starting_goals)
        else:
            self.user_goal = self._generate_random_user_goal()
        return self.user_goal

    def _get_rand_constraints(self, request_template: list) ->dict:
        # 1. Generate inform slots
        inform_slots = self.domain.get_all_inform_slots()
        valid_inform_slots = list(set(inform_slots).difference(request_template))
        random.shuffle(valid_inform_slots)  # shuffle slots
        random_slots = valid_inform_slots[: random.randint(0, len(valid_inform_slots))]

        # 2. Populate inform slots with random contraints
        return {slot:self.domain.sample_inform_slot_value(slot) for slot in random_slots}

    def _generate_random_user_goal(self) -> None:
        user_goal = {"inform_slots": {}, "request_slots": {}}

        # 1. Create request slots
        request_template = random.choice(self.valid_goals)
        user_goal["request_slots"] = {slot: "UNK" for slot in request_template}

        # 2. Generate random inform contraints
        user_goal["inform_slots"] = self._get_rand_constraints(request_template)
        return user_goal

    def load_starting_goals(self, file_path, file_type):
        if file_type == "yaml":
            self.starting_goals = self._load_yaml(file_path)

    def next(self, agent_action, current_turn):
        pass

    def set_nlg_model(self, nlg_model):
        self.nlg_model = nlg_model

    def set_nlu_model(self, nlu_model):
        self.nlu_model = nlu_model

    @staticmethod
    def _load_yaml(file_path: str) -> dict:
        try:
            file = yaml.safe_load(open(file_path))
            return file
        except ImportError:
            raise ("Error: unable import %s." % file_path)

    def __init__(self, domain, goal_type: str):

        self.domain = domain
        self.goal_type = goal_type
        self.valid_goals = domain.get_valid_user_goals()


class RuleSimulator(UserSimulator):


    @staticmethod
    def _extract_aa_vals(self, agent_action):
        split = agent_action.split('(')
        dialog_act = split[0]
        params = split[1].split(')')[0]
        return dialog_act, params

    def _respond_request(self):
        pass

    def _respond_general(self, **kwargs):
        pass

    def _respond_confirm(self, **kwargs):
        pass

    def _generate_utterance(self, nl_template, dialog_act, param_vals):
        slots = self.re_nlg_pattern.findall(nl_template)
        for tup in slots:
            replace_val = param_vals[tup[1].lower()]
            nl_template = nl_template.replace(''.join(tup), replace_val)
        return nl_template

    def action_to_nl(self, dialog_act:str, params:dict = None)-> str:
        if params is None:
            return random.choice(self.nlg_model["dialog_acts"][dialog_act])
        else:
            nl_template = random.choice(self.nlg_model["dialog_acts"][dialog_act][params["param_key"]])
            return self._generate_utterance(nl_template, dialog_act, params["param_vals"])

    # def next(self, agent_action, current_turn):
    #     dialog_act, params = self._extract_aa_vals(agent_action)
    #     if current_turn == -1:
    #         self._respond_general(dialog_act="greetings")
    #     else:
    #         self.response_router(dialog_act=dialog_act, params=params)

    def __init__(self, domain, goal_type: str):
        super(RuleSimulator, self).__init__(domain, goal_type)
        self.re_nlg_pattern = re.compile(r"(?:^|\s)([$])(\w+)")

        self.response_router = { "greetings": self._respond_general,
                                  "request": self._respond_request,
                                  "confirm": self._respond_confirm,
                                  "bye": self._respond_general }

