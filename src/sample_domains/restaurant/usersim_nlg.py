from dialog_simulator import NLGTemplate, import_yaml


class UserSimNLGTemplate(NLGTemplate):

    def __init__(self):
        nlg_template = import_yaml("sample_domains/restaurant/nlg_usersim_rules.yaml")
        super(UserSimNLGTemplate, self).__init__(nlg_template)
