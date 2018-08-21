import yaml
import random
from dialog_simulator import *


class UserSimulator(Speaker):

    def __init__(self, domain: 'Domain') -> None:
        super(UserSimulator, self).__init__()
        self.domain = domain
        self.valid_goals = domain.get_valid_user_goals()
        self.goal = None
        self.dialog_status = DialogStatus.NOT_STARTED
        self.current_turn = -1
        self.starting_goals = None

    # ------------------------------------- Goal Management ----------------------------------------#
    def get_goal(self) -> 'DialogGoal':
        return self.goal.get_goal()

    def get_dialog_state(self) ->' DialogStatus':
        return self.dialog_status

    # ------------------------------------- Base Methods ----------------------------------------#
    def next(self, agent_action: 'DialogAction',
             current_turn: int) -> 'DialogAction':
        pass

    def get_utterance(self, action: 'DialogAction') -> str:
        return self.nlg.get_utterance(action)

    def parse_utterance(self, utterance: str) -> 'DialogAction':
        return self.nlu.parse_utterance(utterance)

    # ------------------------------------- Simulator Setup ----------------------------------------#
    def set_nlg_model(self, nlg_model):
        self.nlg = nlg_model

    def set_nlu_model(self, nlu_model):
        self.nlu = nlu_model

    def reset(self, user_goal: 'DialogGoal'):
        self.dialog_status = DialogStatus.NOT_STARTED
        self.current_turn = -1
        self.goal = user_goal


