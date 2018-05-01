from dialog_simulator import *
from pandas import DataFrame


class AgentGoal(DialogGoal):


    def update_goal(self, inform_slots):
        for k, v in inform_slots.items():
            if k in self.request_slots:
                self.request_slots[k] = v

    def __init__(self, inform_slots: dict, request_slots: dict):
        super(AgentGoal, self).__init__(inform_slots, request_slots)

class Agent(Speaker):

    def reset(self):
        pass

    def next(self, user_action, current_turn):
        pass

    def __init__(self, domain):
        super(Agent, self).__init__()
        self.domain = domain
        self.goal = None
        self.dialog_status = DialogStatus.NOT_STARTED
        self.current_turn = -1


class RestaurantAgent(Agent):

    def reset(self):
        self.current_turn = -1
        self.dialog_status = DialogStatus.NOT_STARTED
        self.goal = AgentGoal(inform_slots=dict(),
                              request_slots={"cuisine": "UNK",
                                             "area": "UNK",
                                             "pricerange": "UNK"})

    def next(self, user_action: DialogAction, current_turn: int) -> DialogAction:
        self.current_turn = current_turn

        if user_action is None and self.dialog_status == DialogStatus.NOT_STARTED:
            self.dialog_status = DialogStatus.NO_OUTCOME_YET
            return DialogAction(dialog_act="greetings")

        elif user_action.dialog_act == "request":
            self.dialog_status = DialogStatus.NO_OUTCOME_YET
            params = {}
            for k,v in user_action.params.items():
                if k in self.dialog_state["inform_slots"]:
                    params[k] = v
            return DialogAction(dialog_act="inform", params=params)

        elif user_action.dialog_act == "bye":
            self.dialog_status = DialogStatus.FINISHED
            return DialogAction(dialog_act="bye")

        else:
            if user_action.params is None:
                return self._request_user_pref()
            else:
                self.goal.update_goal(user_action.params)
                return self._request_user_pref()

    def _request_user_pref(self):
        # Find first unfilled slot and ask user about it
        for k,v in self.goal.get_request_slots().items():
            if v == "UNK":
                return DialogAction(dialog_act="request", params={k})

        # If agent knows all of user's preferences, make a suggestion
        return self._make_recommendation()

    def _update_dialog_state(self, user_action):
        for k,v in user_action["params"].items():
            if k in self.dialog_state["request_slots"]:
                self.dialog_state["request_slots"][k] = v
        return self._make_recommendation()

    def _make_recommendation(self):
        return DialogAction(dialog_act="inform", params={"name": 'aladin',
                                                         'phone': '933-333-2222',
                                                         'address':'324343'})

    def __str__(self):
        return "Restaurant Recommender v.1.0"

    def __init__(self, domain):
        super(RestaurantAgent, self).__init__(domain)
        self.dialog_status = DialogStatus.NOT_STARTED
        self.goal = AgentGoal(inform_slots=dict(),
                              request_slots={"cuisine": "UNK",
                                             "area": "UNK",
                                             "pricerange": "UNK"})
        self.kb = DataFrame(self.domain.domain_kb["kb"])
