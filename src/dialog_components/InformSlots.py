class InformSlots:
    """
    InformSlots contains the contstraints the define a user's goal. These constraints will communicated by the user agent when interacting with a dialog system. There are two types of inform slots: required and optional.

    E.g.: For a user wanting to buy food, the contraints may be { cuisine=Indian, price = cheap }


    Attributes
        ----------
        required_slots: dict
            The required constraints that must be satisfied to achieve a user's goal.

        optional_slots: dict
            Any additional preferences to bound the user goal that are not required to fulfill the user's goal. These preferences can be configured as bonuses values to a reward function or ignored.

        Methods
        -------
        add_constraint(self, key, val, required)
            Add/update constratint to internal dictionary.

        print_constraints(type="all")
            Print the contraints stored in the required_slots and optional_slots.
    """

    def __init__(self):
        self.required_slots = {}
        self.optional_slots = {}

    def add_constraint(self, key, val, required):
        """ Add/update inform constraints. "required" is a boolean and used to indicate if the contraint gets added to required_slots or optional_slots.
        """

        if(required == True):
            self.required_slots[key] = val
        else:
            self.optional_slots[key] = val;

    def print_constraints(self, type="all"):
        """ Print slots. If type is specified will print appropriate slots.
        type: all, required, optional 
        """
        if type == "all":
            print("required slots:", request_slots)
        elif type == "optional":
            print("optional slots:", optional_slots)
        else:
            print("required slots:", request_slots)
