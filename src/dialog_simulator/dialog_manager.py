from dialog_simulator import *
import random
import uuid


class DialogManager:

    def setup_usersim(domain, goaltype, starting_goals_path, nlg=None, nlu=None):
        usersim = RuleSimulator(domain)
        usersim.set_nlg(nlg)
        usersim.set_nlu(nlu)
        usersim.load_starting_goals(starting_goals_path, "yaml")
        usersim.generate_goal(goaltype)

        return usersim

    def setup_agent(domain, nlg=None, nlu=None):
        agent = RestaurantAgent(domain)
        agent.set_nlu(nlu)
        agent.set_nlg(nlg)
        return agent

    def __init__(self, user_sim, agent, domain, max_turns=8):
        self.user_sim = user_sim
        self.agent = agent
        self.domain = domain
        self.max_turns = max_turns
        self.simulations = []
