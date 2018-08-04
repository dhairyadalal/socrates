from dialog_simulator import *
from dialog_agents import Agent
from copy import deepcopy


class MovieAgent(Agent):

    def __init__(self, domain):
        super(MovieAgent, self).__init__(domain)
        self.dialog_status = DialogStatus.NOT_STARTED
        self.goal = DialogGoal(inform_slots=dict(),
                               request_slots={"city": "UNK",
                                              "date": "UNK",
                                              "movie": "UNK",
                                              "theater": "UNK",
                                              "no_tickets": "UNK"}
                               )
        self.cc_details = {"credit_card": "UNK",
                            "ccv": "UNK",
                            "cc_zip":"UNK",
                            "cc_exp":"UNK"}
        self.params = None

        nlg_template = import_yaml("sample_domains/movies/nlg_agent_rules.yml")
        self.nlg = NLGTemplate(nlg_template=nlg_template)


    def reset(self):
        self.current_turn = -1
        self.dialog_status = DialogStatus.NOT_STARTED
        self.goal = DialogGoal(inform_slots=dict(),
                               request_slots={"city": "UNK",
                                              "date": "UNK",
                                              "movie": "UNK",
                                              "theater": "UNK",
                                              "no_tickets": "UNK"})

    def get_utterance(self, action: 'DialogAction') -> str:
        return self.nlg.get_utterance(action)

    def parse_utterance(self, utterance:str ) -> 'DialogAction':
        if self.nlu is not None:
            return self.nlu.parse_utterance(utterance)
        else:
            return None

    def next(self, user_action: 'DialogAction', current_turn: int) -> 'DialogAction':
        self.current_turn = current_turn

        if user_action is None and self.dialog_status == DialogStatus.NOT_STARTED or current_turn == -1:
            self.dialog_status = DialogStatus.NO_OUTCOME_YET
            action = DialogAction(dialog_act="greetings")
            action.update_utterance(self.get_utterance(action))
            return action

        elif user_action.dialog_act == "request":
            self.dialog_status = DialogStatus.NO_OUTCOME_YET

            # Check all keys exist in inform slots
            request_keys = list(user_action.params.keys())
            if all(k in self.goal.inform_slots.keys() for k in request_keys):
                params = {}
                for k, v in user_action.params.items():
                    if k in self.dialog_state["inform_slots"]:
                        params[k] = v
                action = DialogAction(dialog_act="inform", params=params)
                action.update_utterance(self.get_utterance(action))
                return action

            # Check KB for information
            else:
                # Pull out params with None.
                missing_params = {k:v for k,v in user_action.params.items()
                                       if v is None}
                lookup_params = {k:v for k,v in user_action.params.items()
                                       if v is not None}

                suggestions = self.domain.domain_kb.get_suggestions(lookup_params, 1)[0]

                if len(suggestions) == 0: # No suggestion returned
                    return DialogAction(dialog_act="inform", params={"unknown": None})
                else:
                    for param in missing_params:
                        missing_params[param] = suggestions[0][param]
                    action = DialogAction(dialog_act="inform", params=missing_params)
                    action.update_utterance(self.nlg.get_utterance(action))
                    return action

        elif user_action.dialog_act == "bye":
            self.dialog_status = DialogStatus.FINISHED
            action = DialogAction(dialog_act="bye")
            action.update_utterance(self.get_utterance(action))
            return action

        else:
            if user_action.params is None:
                return self._request_user_pref()
            elif any(k in {"cc_number", "cc_zip", "cc_exp"} for k in set(user_action.params.keys())):
                return self._purchase_tickets(user_action)
            else:
                self.goal.update_goal(user_action.params)
                return self._request_user_pref(user_action)

    def _request_user_pref(self, user_action: 'DialogAction'):
        # Find first unfilled slot and ask user about it
        for k, v in self.goal.request_slots.items():
            if v == "UNK":
                action = DialogAction(dialog_act="request", params={k: None})
                action.update_utterance(self.get_utterance(action))
                return action
        return self._reserve_tickets(user_action)

    def _purchase_tickets(self, user_action: 'DialogAction'=None):
        if user_action is None:
            action = DialogAction(dialog_act="request",
                                  params={"cc_number": None, "cc_zip": None, "cc_exp": None})
            action.update_utterance("Ready to purchase your tickets. Please provide your credit card, zip and expiration date. Respond with numbers in order and seperated by ';'. Eg. 444344444444;02133;02/2020 ")
            return action
        else:
            action = DialogAction(dialog_act="inform", params=self.params)
            action.update_utterance(self.get_utterance(action))
            return action

    def _reserve_tickets(self, user_action: 'DialogAction'=None):
        self.params = deepcopy(self.goal.request_slots)
        if self.params.get("no_tickets") is None:
            action = DialogAction("inform", params={"error": None})
            action.update_utterance(self.get_utterance(action))
            return action
        elif user_action is None:
            action = DialogAction("confirm", params=self.params)
            action.update_utterance(self.get_utterance(action))
            return action
        elif user_action.dialog_act == "affirm":
            return self._purchase_tickets(None)
        else:
            return self._purchase_tickets(None)

    def __str__(self):
        return "Movie Ticket Booker v1.0"
