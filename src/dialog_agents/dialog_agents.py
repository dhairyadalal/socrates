from dialog_simulator import *

class Agent(Speaker):

    def __init__(self, domain):
        super(Agent, self).__init__()
        self.domain = domain
        self.goal = None
        self.dialog_status = DialogStatus.NOT_STARTED
        self.current_turn = -1


class RestaurantAgent(Agent):

    def __init__(self, domain):
        super(RestaurantAgent, self).__init__(domain)
        self.dialog_status = DialogStatus.NOT_STARTED
        self.goal = DialogGoal(inform_slots=dict(),
                               request_slots={"cuisine": "UNK",
                                              "area": "UNK",
                                              "pricerange": "UNK"})
        self.kb = None

    def reset(self):
        self.current_turn = -1
        self.dialog_status = DialogStatus.NOT_STARTED
        self.goal = DialogGoal(inform_slots=dict(),
                              request_slots={"cuisine": "UNK",
                                             "area": "UNK",
                                             "pricerange": "UNK"})

    def get_utterance(self, action: DialogAction) -> str:
        return self.nlg.get_utterance(action)

    def parse_utterance(self, utterance: str) -> 'DialogAction':
        if self.nlu is not None:
            return self.nlu.parse_utterance(utterance)
        else:
            return None

    def next(self, user_action: DialogAction, current_turn: int) -> 'DialogAction':
        self.current_turn = current_turn

        if user_action is None and self.dialog_status == DialogStatus.NOT_STARTED:
            self.dialog_status = DialogStatus.NO_OUTCOME_YET
            action = DialogAction(dialog_act="greetings")
            action.update_utterance(self.get_utterance(action))
            return action

        elif user_action.dialog_act == "request":
            self.dialog_status = DialogStatus.NO_OUTCOME_YET
            params = {}
            for k,v in user_action.params.items():
                if k in self.dialog_state["inform_slots"]:
                    params[k] = v
            action = DialogAction(dialog_act="inform", params=params)
            action.update_utterance(self.get_utterance(action))
            return action

        elif user_action.dialog_act == "bye":
            self.dialog_status = DialogStatus.FINISHED
            action = DialogAction(dialog_act="bye")
            action.update_utterance(self.get_utterance(action))
            return action

        else:
            if user_action.params is None:
                return self._request_user_pref()
            else:
                self.goal.update_goal(user_action.params)
                return self._request_user_pref()

    def _request_user_pref(self):
        # Find first unfilled slot and ask user about it
        for k,v in self.goal.request_slots.items():
            if v == "UNK":
                action = DialogAction(dialog_act="request", params={k: None})
                action.update_utterance(self.get_utterance(action))
                return action

        # If agent knows all of user's preferences, make a suggestion
        return self._make_recommendation()

    def _update_dialog_state(self, user_action):
        for k,v in user_action["params"].items():
            if k in self.dialog_state["request_slots"]:
                self.dialog_state["request_slots"][k] = v
        return self._make_recommendation()

    def _make_recommendation(self):
        params = self.goal.request_slots
        suggestions = self.domain.domain_kb.get_suggestions(params, 1)

        if len(suggestions) == 0:
            action = DialogAction(dialog_act="inform",
                                  params={"name": 'aladin',
                                          'phone': '933-333-2222',
                                          'address':'324343'})
            action.update_utterance(self.get_utterance(action))

        else:
            suggestion = suggestions[0][0]
            recommend_params = {"name", "phone", "address"}
            params = dict()
            for rp in recommend_params:
                params.update({rp:suggestion.get(rp)})
            action = DialogAction(dialog_act="inform",
                                  params=params)
            action.update_utterance(self.get_utterance(action))


        return action

    def __str__(self):
        return "Restaurant Recommender v.1.0"