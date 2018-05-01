from enum import Enum, auto
import random
import re


class DialogStatus(Enum):
    FINISHED = auto()
    NO_OUTCOME_YET = auto()
    NOT_STARTED = auto()

class DialogGoal(object):
    def get_goal(self):
        return {"inform_slots": self.inform_slots,
                 "request_slots": self.request_slots}

    def update_goal(self, inform_slots):
        pass

    def update_goal_slot(self, slot_type: str, key: str, val: str):
        if slot_type == "inform":
            self.inform_slots[key] = val
        elif slot_type == "request":
            self.request_slots[key] = val
        else:
            raise ValueError("Invalid slot type. Supported slot types: request, inform.")

    def get_inform_slots(self):
        return self.inform_slots

    def get_request_slots(self):
        return self.request_slots

    def __init__(self, inform_slots: dict, request_slots: dict):
        self.inform_slots = inform_slots
        self.request_slots = request_slots


class DialogAction(object):
    """ Class to represent dialog actions that are generated by simulator and agent. """

    def get_param_keys(self):
        """ Function returns param key concatenated and comma separated  """
        if isinstance(self.params, set):
            return ','.join(sorted(self.params))
        else:
            return ','.join(sorted(self.params.keys()))

    def update_utterance(self, utterance):
        self.nl_utterance = utterance

    def update_dialog_act(self, dialog_act):
        self.dialog_act = dialog_act

    def update_params(self, params):
        if isinstance(params, dict) or isinstance(params, set):
            self.params = params
        else:
            raise ValueError("Invalid param type. Supported types: dict, set.")

    def __init__(self, dialog_act: str = None, params=None, nl_utterance: str = None):
        self.dialog_act = dialog_act
        self.params = params
        self.nl_utterance = nl_utterance


class NLU(object):
    """ Base class for natural language understanding module. """
    def __init__(self):
        pass

class NLG(object):
    """ Base class for natural language generation module. """
    # ---------------------------- Generate Utterance using Dictionary Lookup ----------------------------------- #
    def _generate_utterance(self, nl_template: str, dialog_action: DialogAction):
        slots = self.re_nlg_pattern.findall(nl_template)
        for tup in slots:
            replace_val = dialog_action.params[tup[1].lower()]
            nl_template = nl_template.replace(''.join(tup), replace_val)
        return nl_template

    # ----------------------------- Generate Utterance using Model ---------------------------------------------- #
    def _model_generate_utterance(self, dialog_action: DialogAction):
        """ Method will be overridden with local implementation. """

        return None

    # --------------------------------- Class Public Methods ---------------------------------------------------- #
    def get_utterance(self, dialog_action: DialogAction):

        if self.type == "dict":
            if dialog_action.params is None:
                return random.choice(self.model["dialog_acts"][dialog_action.dialog_act])
            else:
                # Generate natural language template
                param_keys = dialog_action.get_param_keys()
                nl_template = random.choice(self.model["dialog_acts"][dialog_action.dialog_act][param_keys])
                utterance = self._generate_utterance(nl_template, dialog_action)
        else:
            utterance = self._model_generate_utterance(dialog_action)

        return utterance

    def get_model(self):
        return {"model": self.model, "type": self.type}

    def __init__(self, type:str, model:object, model_name: str = None):
        if type in ["dict", "model"]:
            self.type = type
        else:
            raise ValueError("Invalid model type. Supported types: dict, model.")
        self.model = model
        self.model_name = model_name
        self.re_nlg_pattern = re.compile(r"(?:^|\s)([$])(\w+)")


class Speaker(object):
    """ Base class for User Simulator and Dialog Agents """
    def next(self, previous_action: object, turn: int):
        pass

    def reset(self):
        pass

    def get_nlu(self):
        return self.nlu

    def get_nlg(self):
        return self.nlg

    def set_nlg(self, nlg: NLG):
        self.nlg = nlg

    def set_nlu(self, nlu: NLU):
        self.nlu = nlu

    def get_dialog_status(self):
        return self.dialog_status

    def __init__(self):
        self.nlu = None
        self.nlg = None
        self.dialog_status = DialogStatus.NOT_STARTED
