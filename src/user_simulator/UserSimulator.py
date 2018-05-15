import yaml
import random
from dialog_simulator import *


class UserGoal(DialogGoal):
    def update_goal(self, inform_slots):
        for k, v in inform_slots.items():
            if k in self.request_slots:
                self.request_slots[k] = v

    def __init__(self, inform_slots: dict, request_slots: dict):
        super(UserGoal, self).__init__(inform_slots, request_slots)


class UserSimulator(Speaker):

    # ------------------------------------- Goal Management ----------------------------------------#
    def generate_goal(self, goal_type: str):
        if goal_type == "template":
            goal = random.choice(self.starting_goals)
            self.goal = UserGoal(goal["inform_slots"], goal["request_slots"])
        elif goal_type == "random":
            self.goal = self._generate_random_goal()
        else:
            raise ValueError("Invalid goal type. Supported goal types: template, random.")

    def _get_rand_constraints(self, request_template: list):
        # 1. Generate inform slots
        inform_slots = self.domain.get_all_inform_slots()
        valid_inform_slots = list(set(inform_slots).difference(request_template))
        random.shuffle(valid_inform_slots)  # shuffle slots
        random_slots = valid_inform_slots[: random.randint(0, len(valid_inform_slots))]

        # 2. Populate inform slots with random constraints
        return {slot: self.domain.sample_inform_slot_value(slot) for slot in random_slots}

    def _generate_random_goal(self):
        # 1. Create request slots
        request_template = random.choice(self.valid_goals)
        request_slots = {slot: "UNK" for slot in request_template}

        # 2. Generate random inform constraints
        inform_slots = self._get_rand_constraints(request_template)
        return UserGoal(inform_slots, request_slots)

    def load_starting_goals(self, file_path: str, file_type: str):
        if file_type == "yaml":
            self.starting_goals = self._load_yaml(file_path)

    def get_goal(self):
        return self.goal.get_goal()

    def get_dialog_state(self):
        return self.dialog_status

    # ------------------------------------- Turn Management ----------------------------------------#
    def next(self, agent_action: DialogAction, current_turn: int):
        pass

    # ------------------------------------- Simulator Setup ----------------------------------------#
    def set_nlg_model(self, nlg_model):
        self.nlg = nlg_model

    def set_nlu_model(self, nlu_model):
        self.nlu = nlu_model

    @staticmethod
    def _load_yaml(file_path: str) -> dict:
        try:
            file = yaml.safe_load(open(file_path))
            return file
        except ImportError:
            raise ("Error: unable import %s." % file_path)

    def reset(self):
        self.dialog_status = DialogStatus.NOT_STARTED
        self.current_turn = -1
        self.generate_goal(self.goal_type)

    def __init__(self, domain, goal_type):
        super(UserSimulator, self).__init__()
        self.domain = domain
        self.valid_goals = domain.get_valid_user_goals()
        self.goal = None
        self.dialog_status = DialogStatus.NOT_STARTED
        self.current_turn = -1
        self.starting_goals = None
        self.goal_type = goal_type


class RuleSimulator(UserSimulator):

    # ------------------------  Route Response -----------------------------------------------------------------#
    def next(self, agent_action: DialogAction, current_turn: int) -> DialogAction:

        self.current_turn = current_turn

        if agent_action is None and self.dialog_status == DialogStatus.NOT_STARTED:
            self.dialog_status = DialogStatus.NO_OUTCOME_YET
            return self._respond_general(DialogAction(dialog_act="greetings"))
        elif self.current_turn == 1 and agent_action.dialog_act == "greetings":
            self.dialog_status = DialogStatus.NO_OUTCOME_YET
            return self._respond_random_inform()
        elif self.dialog_status == DialogStatus.FINISHED:
            return self._respond_general(DialogAction(dialog_act="bye"))
        else:
            return self.response_router[agent_action.dialog_act](agent_action)

    # ------------------------  Respond Methods -----------------------------------------------------------------#
    def _respond_general(self, action: DialogAction) -> DialogAction:
        action.update_utterance(self._action_to_nl(action))
        return action

    def _respond_request(self, agent_action: DialogAction) -> DialogAction:
        """ Respond to an agent's request for more information by informing them based on user preferences. """
        params = {}
        inform_slots = self.goal.get_inform_slots()

        # Loop over user's prefs in inform slots and update return action params
        for key in agent_action.params:
            if key in inform_slots:
                params[key] = inform_slots[key]
            else:
                params["no_pref"] = "UNK"
        ret_action = DialogAction(dialog_act="inform", params=params)
        ret_action.update_utterance(self._action_to_nl(ret_action))  # generate nl utterance
        return ret_action

    def _respond_confirm_multiple(self, agent_action: DialogAction) -> DialogAction:
        return DialogAction(dialog_act="inform", params={"unknown"})

    def _respond_confirm(self, agent_action: DialogAction) -> DialogAction:
        confirm_params = list(agent_action.params.items())
        inform_slots = self.goal.get_inform_slots()

        # Check if agent is asking to confirm single or multiple prefs
        if len(confirm_params) == 1:  # Single pref case
            if confirm_params[0][0] not in inform_slots:
                return self._respond_general(DialogAction(dialog_act="inform", params={"unknown"}))
            elif inform_slots[confirm_params[0][0]] == confirm_params[0][1]:
                utterance = self._action_to_nl(DialogAction(dialog_act="affirm"))
                return DialogAction(dialog_act="affirm", nl_utterance=utterance)
            else:
                utterance = self._action_to_nl(DialogAction(dialog_act="negate"))
                return DialogAction(dialog_act="negate", nl_utterance=utterance)

        # Multiple prefs confirm case
        else:
            self._respond_confirm_multiple(agent_action)

    def _respond_to_suggestion(self, agent_action: DialogAction) -> DialogAction:

        ret_action = DialogAction()

        # 1. Update goal with system suggestion and update dialog state
        self.goal.update_goal(agent_action.params)

        # Update dialog state base on new information
        self._update_dialog_status()

        # 2. Check dialog state. If not finished request follow-up.
        if self.dialog_status == DialogStatus.FINISHED:  # Case: Dialog is finished
            ret_action.update_dialog_act("bye")
            ret_action.update_utterance(self._action_to_nl(ret_action))
            return ret_action
        else:
            # Find first UNK slot and request more info.
            for k, v in self.goal.get_request_slots().items():
                if v == "UNK":
                    ret_action.update_dialog_act("request")
                    ret_action.update_params({k})
                    ret_action.update_utterance(self._action_to_nl(ret_action))
                    return ret_action

    def _respond_random_inform(self):
        inform_slots = self.goal.get_inform_slots()

        # Choose random inform preference
        rand_param = random.choice(list(inform_slots.keys()))
        params = dict()
        params[rand_param] = inform_slots[rand_param]

        # Generate action
        action = DialogAction(dialog_act="inform", params=params)
        action.update_utterance(self._action_to_nl(action))
        return action

    # ------------------------  Dialog Status Updates  ------------------------------------------------------------#
    def _update_dialog_status(self):
        # Check how many unknown slots remain.
        unk_slots = 0
        for i, v in self.goal.get_request_slots().items():
            if v == "UNK":
                unk_slots += 1

        # If greater than 0, ask more follow-up questions. Otherwise finish conversation.
        if unk_slots > 0:
            self.dialog_status = DialogStatus.NO_OUTCOME_YET
        else:
            self.dialog_status = DialogStatus.FINISHED

    # NLG
    def _action_to_nl(self, dialog_action: DialogAction)-> str:
        return self.nlg.get_utterance(dialog_action)

    def get_utterance(self, action: DialogAction) -> str:
        return self.nlg.get_utterance(action)

    def __str__(self):
        return "Restaurant Rules Simulator: v.1.0"

    def __init__(self, domain, goal_type):
        super(RuleSimulator, self).__init__(domain, goal_type)
        self.response_router = {"greetings": self._respond_general,
                                "inform": self._respond_to_suggestion,
                                "random_inform": self._respond_random_inform,
                                "request": self._respond_request,
                                "confirm": self._respond_confirm,
                                "bye": self._respond_general}

