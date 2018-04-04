


class DialogManager:


    def record_action(self, ):

    def start_simulation(self):
        pass

    def __init__(self, max_turns = 5, user_sim: UserSimulator, agent: Agent):
        self.user_sim = user_sim
        self.agent = agent
        self.max_turns = max_turns
        self.dialog_history = {}

