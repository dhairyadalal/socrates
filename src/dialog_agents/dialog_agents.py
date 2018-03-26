from dialog_components import InformSlots


class Agent:

    def __init__(self, informslots ):

        self.informslots = informslots

    def state_to_action(self, state, available_actions):
         return { "act_slot_response" : None,
                  "act_slot_value_response": None  }

    def set_nlg_model(self, nlg_model):
        self.nlg_model = nlg_model