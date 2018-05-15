from dialog_simulator import *
from dialog_simulator.dialog_helpers import DialogStatus
import random
import uuid
import yaml

def print_action(action, turn, speaker):
    print(turn,': ', speaker, "->", action.dialog_act, action.params)
    print(speaker, ": ", action.nl_utterance)

class DialogManager:

    @ staticmethod
    def _take_turn(action, turn, speaker):

        # Cold start case: action is None
        if action is None:
            action = speaker.next(action, turn)
            action.nl_utterance = speaker.get_utterance(action)
            return action

        # Otherwise follow conversation parse flow
        else:
            # 1. Parse previous utterance using speaker's NLU
            parsed_action = speaker.parse_utterance(action.nl_utterance)

            # 2. Check if nlu returned an action. If not, pass action action.
            if parsed_action is not None:
                action = speaker.next(parsed_action, turn)
            else:
                action = speaker.next(action, turn)

            action.nl_utterance = speaker.get_utterance(action)
            return action

    def _evaluate_dialog(self):
        for k, v in self.user_sim.goal.request_slots.items():
            if v == "UNK":
                return False
        return True

    def _register_turn(self, user_action, agent_action, user_goal, turn, first_speaker):
        if first_speaker == "usersim":
            conv_round = {"turn": turn,
                          "user_goal": user_goal,
                          "first_speaker": {
                              "speaker": "usersim",
                              "dialog_act": user_action.dialog_act,
                              "dialog_slots": user_action.params,
                              "nl_utterance": user_action.nl_utterance
                          },
                          "second_speaker": {
                              "speaker": "agent",
                              "dialog_act": agent_action.dialog_act,
                              "dialog_slots": agent_action.params,
                              "nl_utterance": agent_action.nl_utterance}
                          }
        else:
            conv_round = {"turn": turn,
                          "user_goal": user_goal,
                          "first_speaker": {
                              "speaker": "agent",
                              "dialog_act": agent_action.dialog_act,
                              "dialog_slots": agent_action.params,
                              "nl_utterance": agent_action.nl_utterance
                          },
                          "second_speaker": {
                              "speaker": "usersim",
                              "dialog_act": user_action.dialog_act,
                              "dialog_slots": user_action.params,
                              "nl_utterance": user_action.nl_utterance}
                          }

        # Update Dialog History
        self.dialog_history.append(conv_round)

    def _register_simulated_dialog(self, starting_user_goal, turns_taken):
        # 1. Evaluate dialog
        dialog_grade = "Success" if self._evaluate_dialog() else "Failed"

        # 2. Evaluate if agent suggestion matches user preferences
        goal_grade = "Success"

        # 2. register dialog in all_dialogs
        self.all_simulations.append({"dialog_id": str(uuid.uuid4()),
                                     "dialog_grade": dialog_grade,
                                     "goal_grade": goal_grade,
                                     "reward": 0,
                                     "starting_user_goal": starting_user_goal.get_goal(),
                                     "turns_taken": turns_taken,
                                     "turn_history": self.dialog_history})

    def _initialize_new_round(self):
        self.user_sim.reset()
        self.agent.reset()
        self.current_turn = 0
        self.dialog_history = []

    def run_simulations(self):
        print("Preparing to run simulations ... ")
        for i in range(self.num_sim):
            print("\tRunning simulation %i of %i" % (i+1, self.num_sim))
            self.run_simulation()

        # write to file
        with open('data/simulated_dialogs/data.yml', 'w') as outfile:
            yaml.dump(self.all_simulations, outfile, default_flow_style=False)

    def run_simulation(self):

        self._initialize_new_round()            # 1. Reset agents
        flip = random.randint(0, 1)             # 2. Flip coin to see who goes first.
        user_goal = self.user_sim.goal          # 3. Stash user goal
        user_action, agent_action = None, None  # 4. Set agent actions

        # 5. Run Dialog simulation
        while self.current_turn < self.max_turns:
            if self.user_sim.dialog_status == DialogStatus.FINISHED or self.agent.dialog_status == DialogStatus.FINISHED:
                break

            if flip == 0:  # Assume User takes first action
                user_action = self._take_turn(agent_action, self.current_turn, self.user_sim)
                agent_action = self._take_turn(user_action, self.current_turn, self.agent)
                self._register_turn(user_action, agent_action, self.user_sim.goal.get_goal(),
                                    self.current_turn, "usersim")
            else:  # Assume Agent takes first action
                agent_action = self._take_turn(user_action, self.current_turn, self.agent)
                user_action = self._take_turn(agent_action, self.current_turn, self.user_sim)
                self._register_turn(user_action, agent_action, self.user_sim.goal.get_goal(),
                                    self.current_turn, "agent")
            self.current_turn += 1

        # 6. Evaluate goal
        dialog_result = "Success" if self._evaluate_dialog() else "Failed"
        print("\tDialog Result: ", dialog_result)

        # 7. Register Simulation
        self._register_simulated_dialog(user_goal, self.current_turn)

    def __init__(self, user_sim, agent, domain, max_turns=8, num_sim=1, reward=1, first_speaker="random"):
        self.user_sim = user_sim
        self.agent = agent
        self.domain = domain
        self.max_turns = max_turns
        self.current_turn = 0
        self.num_sim = num_sim
        self.reward = reward
        self.first_speaker = first_speaker
        self.dialog_history = []
        self.all_simulations = []


