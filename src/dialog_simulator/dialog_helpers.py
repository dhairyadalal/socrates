from enum import Enum, auto
import json
import random
import re
import spacy
from nltk import word_tokenize


class DialogStatus(Enum):
    FINISHED = auto()
    NO_OUTCOME_YET = auto()
    NOT_STARTED = auto()

class DialogGoal(object):
    def get_goal(self):
        return {"inform_slots": self.inform_slots,
                "request_slots": self.request_slots}

    def update_goal(self, inform_slots):
        for k, v in inform_slots.items():
            if k in self.request_slots:
                self.request_slots[k] = v

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

    def __str__(self):
        return """inform slots: %s \nrequest slots: %s """ % (self.inform_slots, self.request_slots)

    def __init__(self, inform_slots: dict, request_slots: dict):
        self.inform_slots = inform_slots
        self.request_slots = request_slots


class DialogAction(object):
    """ Class to represent dialog actions that are generated by simulator and agent. """

    def __init__(self, dialog_act: str = None, params=dict(), nl_utterance: str = None):

        if not isinstance(params, dict):
            raise ValueError("Invalid param type. Expecting dict.")

        self.dialog_act = dialog_act
        self.params = params
        self.nl_utterance = nl_utterance

    def get_param_keys(self) -> str:
        """ Function returns param key concatenated and comma separated  """
        return ','.join(sorted(self.params.keys()))

    def update_utterance(self, utterance):
        self.nl_utterance = utterance

    def update_dialog_act(self, dialog_act):
        self.dialog_act = dialog_act

    def update_params(self, params):
        if isinstance(params, dict):
            self.params.update(params)
        else:
            raise ValueError("Invalid param type. Expected dict.")

    def params_empty(self)->bool:
        return bool(self.params)

    def __str__(self):
        action = {"dialog_act": self.dialog_act,
                  "params": self.params,
                  "nl_utterance": self.nl_utterance}
        return json.dumps(action, indent = 4)

class NLU(object):
    """ Base class for natural language understanding module. """

    def parse_utterance(self, utterance: str) -> 'DialogAction':
        pass

class NLUsimple(NLU):
    """ Simple NLU engine using NLP rules """

    def __init__(self, domain: 'Domain'):
        self.domain = domain
        self.ents = self._lookup_ents()
        self.QUESTION_POS_SEQUENCES = [["WP", "MD", "NN", "VB"],
                                       ["WR", "MD", "NN", "VB"],
                                       ["WP", "MD", "PR", "VB"],
                                       ["WR", "MD", "PR", "VB"],
                                       ["MD", "NN", "VB"],
                                       ["WR", "VB", "PR"],
                                       ["WR", "VB", "NN"],
                                       ["WP", "VB", "NN"],
                                       ["WP", "VB", "PR"]]
        self.nlp = spacy.load('en')

    def _simple_question_classifier(self, text: str) -> bool:
        # check if last token is '?'
        if text.strip()[-1] == '?':
            return True

        parsed_text = self.nlp(text)

        # chunk noun phrases into single token
        for noun_phrase in list(parsed_text.noun_chunks):
            noun_phrase.merge()

        # only care about the first two letters of the POS tag
        pos_tags = [token.tag_[0:2] for token in parsed_text]

        # check if first word lemma is be or do
        if parsed_text[0].lemma_ in ["be", "do"]:
            if pos_tags[1] in ["RB"]:  # ignore not case e.g. don't, isn't
                if pos_tags[2] in ["NN", "PR"]:
                    return True
            if pos_tags[1] in ["NN", "PR"]:
                return True

        if len(pos_tags) > 1:
            # check if first pos_tag is "MD" then "PR or NN" e.g. "Can recommender help"
            if pos_tags[0] == "MD" and pos_tags[1] in ["PR", "NN"]:
                return True
            # check if first pos_tag = "WP or WR" then "VB"--> "what does Recommender do"
            if pos_tags[0] in ["WP", "WR"] and pos_tags[1] == "VB":
                return True

        # check for pos patterns of interest
        for i in range(len(parsed_text)):
            for pattern in self.QUESTION_POS_SEQUENCES:
                if pattern == pos_tags[i: i + len(pattern)]:
                    return True

        return False

    def _intent_classifier(self, sent: str) -> str:

        # Confirm intent
        confirm_re = re.compile("you|you want|right\?")
        if confirm_re.match(sent.lower()):
            return "confirm"

        # Request intent
        if self._simple_question_classifier(sent):
            return "request"

        # Affirm intent regular expression
        affirm_re = re.compile("yes|yeah|yup|correct|right")
        if affirm_re.match(sent.lower()):
            return "affirm"

        # Negate intent
        negate_re = re.compile("no|nope|wrong|incorrect")
        if negate_re.match(sent.lower()):
            return "negate"

        # Greeting intent
        greetings_re = re.compile("hi|hello")
        if greetings_re.match(sent.lower()):
            return "greetings"

        # Bye intent
        bye_re = re.compile("bye|goodbye|thanks|thank you")
        if bye_re.match(sent.lower()):
            return "bye"

        # Assume inform intent
        return "inform"


    def _lookup_ents(self):
        ents = dict()

        # Request slots
        for slot in self.domain.request_slots:
            ents[slot] = "request_slot"

        # Inform slots
        for k,v in self.domain.inform_slot_values.items():
            ents.update({i: k for i in v})

        return ents

    def parse_utterance(self, utterance: str):
        intent = self._intent_classifier(utterance)

        params = dict()
        toks = word_tokenize(utterance.lower())
        for tok in toks:
            key = self.ents.get(tok)
            if key == "request_slot":
                params.update({tok: None})
            elif key is not None:
                params.update({key: tok})

        return DialogAction(dialog_act=intent, params=params)

class NLG(object):
    def get_utterance(self, dialog_action: DialogAction) -> str:
        pass

class NLGTemplate(NLG):

    def __init__(self, nlg_template: dict):
        self.model = nlg_template
        self.version = self.model.get("version")
        self.domain = self.model.get("domain")

        token_re = r"(?:^|\s)([$])(\w+)" if self.model.get("regex") is None else self.model.get("regex")
        self.re_nlg_pattern = re.compile(token_re)

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
    def get_utterance(self, dialog_action: DialogAction)->str:
        if "default" in dialog_action.params or not bool(dialog_action.params):
            default_exp = self.model["dialog_acts"][dialog_action.dialog_act]["default"]
            if len(default_exp) > 0:
                return random.choice(self.model["dialog_acts"][dialog_action.dialog_act]["default"])
            else:
                return default_exp
        else:
            # Generate natural language template
            param_keys = dialog_action.get_param_keys()
            nl_template = random.choice(self.model["dialog_acts"][dialog_action.dialog_act][param_keys])
            utterance = self._generate_utterance(nl_template, dialog_action)

        return utterance

    def get_model(self):
        return {"model": self.model, "type": self.type}

    def __str__(self):
        return "NLG v.%s, domain: %s" % (self.version, self.domain)


class Speaker(object):
    """ Base class for User Simulator and Dialog Agents """
    def next(self, previous_action: DialogAction, turn: int) -> DialogAction:
        pass

    def reset(self):
        pass

    def get_utterance(self, action: DialogAction) -> str:
        pass

    def parse_utterance(self, utterance: str) -> 'DialogAction':
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
