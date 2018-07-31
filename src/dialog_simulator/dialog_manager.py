from dialog_simulator.dialog_helpers import DialogStatus, DialogGoal
import datetime, json, random, uuid, yaml


def print_action(action, turn, speaker):
    print("\t", turn, ": ", speaker, ": ", action.nl_utterance)
    print("\t\t  DialogAction: ", action.dialog_act, action.params)

class DialogManager(object):

    def __init__(self, user_sim, user_goal_type, agent, domain, max_turns=8, num_sim=1,
                 reward=1, first_speaker="random"):
        self.user_sim = user_sim
        self.user_goal_type = user_goal_type
        self.agent = agent
        self.domain = domain
        self.max_turns = max_turns
        self.current_turn = 0
        self.num_sim = num_sim
        self.reward = reward
        self.first_speaker = first_speaker
        self.dialog_history = []
        self.all_simulations = []
        self.starting_goals = None
        self.clean_dialogs = []

    # ------------------------------------- Dialog Evaluation ----------------------------------------#
    def _evaluate_dialog(self):
        for k, v in self.user_sim.goal.request_slots.items():
            if v == "UNK":
                return False
        return True

    # ------------------------------------- Goal Management ----------------------------------------#

    def set_starting_goals(self, starting_goals: dict):
        self.starting_goals = starting_goals

    def _generate_random_starting_goal(self):
        goal_params = random.choice(self.starting_goals)
        return DialogGoal(goal_params["inform_slots"], goal_params["request_slots"])

    def generate_goal(self, goal_type: str) -> 'DialogGoal':
        route = {"template": self._generate_random_starting_goal(),
                 "random": self._generate_random_goal()}
        if goal_type in route:
            return route.get(goal_type)
        elif goal_type == "mix":
            rand_gt = random.choice(list(route.keys()))
            return route.get(rand_gt)
        else:
            raise ValueError("Invalid goal type. Supported goal types: template, random.")

    def _get_rand_constraints(self, request_template: list):
        # 1. Generate inform slots
        inform_slots = self.domain.get_all_inform_slots()
        valid_inform_slots = list(set(inform_slots).difference(request_template))
        random.shuffle(valid_inform_slots)  # shuffle slots
        random_slots = valid_inform_slots[: random.randint(0, len(valid_inform_slots))]

        # 2. Populate inform slots with random constraints
        return {slot: self.domain.sample_inform_slot_value(slot) for slot in random_slots}

    def _generate_random_goal(self):
        # 1. Create request slots
        request_template = random.choice(self.domain.valid_user_goals)
        request_slots = {slot: "UNK" for slot in request_template}

        # 2. Generate random inform constraints
        inform_slots = self._get_rand_constraints(request_template)
        return DialogGoal(inform_slots, request_slots)

    # ------------------------------------- Turn Management ----------------------------------------#
    @staticmethod
    def _take_turn(prev_action: 'DialogAction', turn: int, speaker: 'Speaker') -> 'DialogAction':
        next_action = speaker.next(prev_action, turn)
        return next_action

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

        # Generate New Goal
        new_user_goal = self.generate_goal(self.user_goal_type)
        #print("User Goal: \n", new_user_goal)

        # Reset Speakers
        self.user_sim.reset(new_user_goal)
        self.agent.reset()

        # Reset conversation params
        self.current_turn = 0
        self.dialog_history = []
        self.clean_dialogs = []

    def write_history_json(self, path):
        now = datetime.datetime.now()
        file = "data_%d_%d_%d.json" % (now.year, now.month, now.day)
        try:
            with open(path + file, 'w') as outfile:
                json.dump( self.all_simulations, outfile, indent=4, sort_keys=True)
        except IOError:
            raise IOError("Error: Unable to write to file. ")
        return True

    def write_history_yaml(self, path) -> bool:
        now = datetime.datetime.now()
        file = "data_%d_%d_%d.yaml" % (now.year, now.month, now.day)
        try:
            with open( path + file, 'w') as outfile:
                yaml.dump(self.all_simulations, outfile, default_flow_style=False)
        except IOError:
            raise IOError("Error: Unable to write to file. ")
        return True

    def run_simulations(self, save_loc: str,
                        save_history: bool = True,
                        output: str = 'json',
                        print_dialog_flag: bool = False,
                        verbose_flag: bool = True) -> None:
        #print("Preparing to run simulations ... ")
        for i in range(self.num_sim):
            if verbose_flag:
                print("\tRunning simulation %i of %i" % (i+1, self.num_sim))
            self.run_simulation(print_dialog_flag, verbose_flag)
        #print("Successfully ran %i simulations." % self.num_sim)

        # write to file
        if save_history:
            if output == "json":
                write_status = self.write_history_json(save_loc)
            elif output == "yaml":
                write_status = self.write_history_yaml(save_loc)
            else:
                raise ValueError("Unsupported export type. Expecting json or yaml.")

            if write_status:
                print("Successfully wrote dialog histories to %s" % save_loc)

    def run_simulation(self, print_dialog_flag: bool = False, verbose: bool = True) -> None:

        self._initialize_new_round()            # 1. Reset agents

        # 2. Deterime who goes first
        if self.first_speaker == "random":
            flip = random.randint(0, 1)
        elif self.first_speaker == "usersim":
            flip = 0
        else:
            flip = 1

        user_goal = self.user_sim.goal          # 3. Stash user goal
        user_action, agent_action = None, None  # 4. Set agent actions

        # 5. Run Dialog simulation
        while self.current_turn < self.max_turns:
            if self.user_sim.dialog_status == DialogStatus.FINISHED or self.agent.dialog_status == DialogStatus.FINISHED:
                break

            if flip == 0:  # Assume User takes first action
                user_action = self._take_turn(agent_action, self.current_turn, self.user_sim)
                agent_action = self._take_turn(user_action, self.current_turn, self.agent)

                if print_dialog_flag:
                    print_action(user_action, self.current_turn, "usersim")
                    print_action(agent_action, self.current_turn, "agent")

                self._register_turn(user_action,
                                    agent_action,
                                    self.user_sim.goal.get_goal(),
                                    self.current_turn, "usersim")

            else:  # Assume Agent takes first action
                agent_action = self._take_turn(user_action, self.current_turn, self.agent)
                user_action = self._take_turn(agent_action, self.current_turn, self.user_sim)

                if print_dialog_flag:
                    print_action(agent_action, self.current_turn, "agent")
                    print_action(user_action, self.current_turn, "usersim")

                self._register_turn(user_action,
                                    agent_action,
                                    self.user_sim.goal.get_goal(),
                                    self.current_turn, "agent")
            self.current_turn += 1

        # 6. Evaluate goal
        dialog_result = "Success" if self._evaluate_dialog() else "Failed"
        if verbose:
            print("\tDialog Result: ", dialog_result)

        # 7. Register Simulation
        self._register_simulated_dialog(user_goal, self.current_turn)
