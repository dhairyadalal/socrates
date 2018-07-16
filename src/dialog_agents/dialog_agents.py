from dialog_simulator import *

class Agent(Speaker):

    def __init__(self, domain):
        super(Agent, self).__init__()
        self.domain = domain
        self.goal = None
        self.dialog_status = DialogStatus.NOT_STARTED
        self.current_turn = -1
