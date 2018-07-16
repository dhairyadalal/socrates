from user_simulator import UserSimulator
from dialog_simulator import DialogAction, DialogGoal, DialogStatus
import random

class RestaurantUserSim(UserSimulator):

    def __init__(self, domain: 'Domain') -> None:

        super(RestaurantUserSim, self).__init__(domain)
        self.response_router = {"greetings": self._respond_general,
                                "inform": self._respond_to_suggestion,
                                "random_inform": self._respond_random_inform,
                                "request": self._respond_request,
                                "confirm": self._respond_confirm,
                                "bye": self._respond_general}
        self.current_turn = -1

    # ------------------------  Route Response -----------------------------------------------------------------#

    def next(self, agent_action: 'DialogAction', current_turn: int) -> 'DialogAction':
        """
        The next function produces the user simulators next response to the dialog agent.
        It takes in a dialog action representing the agent's last utterance and  current turn. Next use the
        response router to appropiate select and generate the next response.
        """
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
    def _respond_general(self, action: 'DialogAction') -> 'DialogAction':
        """
        This method funnels dialog action that are not inform or request directly to nlg module to generate a response.
        General responses don't require any special logic from the user simulator.
        """

        action.update_utterance(self.get_utterance(action))
        return action

    def _respond_request(self, agent_action: DialogAction) -> 'DialogAction':
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
        ret_action.update_utterance(self.get_utterance(ret_action))  # generate nl utterance
        return ret_action

    def _respond_confirm_multiple(self, agent_action: 'DialogAction') -> 'DialogAction':
        """ Placeholder for handling multipele request from agent. User responds they don't know. """
        return DialogAction(dialog_act="inform", params={"unknown": None})

    def _respond_confirm(self, agent_action: DialogAction) -> 'DialogAction':
        """
        Method resolves the confirm dialog act, where the agent is asking the user to validate their preferences.
        Compare the prefence key/values sent in the params of the dialog action to usersim's own prefs in the goal obj.
        Return a affirm or negate dialog action.
        """

        confirm_params = list(agent_action.params.items())
        inform_slots = self.goal.get_inform_slots()

        # Check if agent is asking to confirm single or multiple prefs
        if len(confirm_params) == 1:  # Single pref case
            if confirm_params[0][0] not in inform_slots:
                return self._respond_general(DialogAction(dialog_act="inform", params={"unknown": None}))
            elif inform_slots[confirm_params[0][0]] == confirm_params[0][1]:
                utterance = self.get_utterance(DialogAction(dialog_act="affirm"))
                return DialogAction(dialog_act="affirm", nl_utterance=utterance)
            else:
                utterance = self.get_utterance(DialogAction(dialog_act="negate"))
                return DialogAction(dialog_act="negate", nl_utterance=utterance)

        # Multiple prefs confirm case
        else:
            self._respond_confirm_multiple(agent_action)

    def _respond_to_suggestion(self, agent_action: DialogAction) -> 'DialogAction':
        """
        Respond to agent's suggestion and update user's goal to reflect new suggestion information.
        If agent has provided partial information, usersim will ask for more information based on the request slots
        in its goal object that are set to "UNK".
        """

        ret_action = DialogAction()

        # 1. Update goal with system suggestion and update dialog state
        self.goal.update_goal(agent_action.params)

        # Update dialog state base on new information
        self._update_dialog_status()

        # 2. Check dialog state. If not finished request follow-up.
        if self.dialog_status == DialogStatus.FINISHED:  # Case: Dialog is finished
            ret_action.update_dialog_act("bye")
            ret_action.update_utterance(self.get_utterance(ret_action))
            return ret_action
        else:
            # Find first UNK slot and request more info.
            for k, v in self.goal.get_request_slots().items():
                if v == "UNK":
                    ret_action.update_dialog_act("request")
                    ret_action.update_params({k:None})
                    ret_action.update_utterance(self.get_utterance(ret_action))
                    return ret_action

    def _respond_random_inform(self) -> DialogAction:
        """
        User is speaking first. Will randomly choose its prefrences and inform the agent.
        """
        inform_slots = self.goal.get_inform_slots()

        # Choose random inform preference
        rand_param = random.choice(list(inform_slots.keys()))
        params = dict()
        params[rand_param] = inform_slots[rand_param]

        # Generate action
        action = DialogAction(dialog_act="inform", params=params)
        action.update_utterance(self.get_utterance(action))
        return action

    # ------------------------  Dialog Status Updates  ------------------------------------------------------------#
    def _update_dialog_status(self):
        """
        Internal state tracking. Check internal goal status and update dialog status accordingly.
        """

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

    def __str__(self):
        return "Restaurant Rules Simulator: v.1.0"

