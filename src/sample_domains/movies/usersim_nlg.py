from dialog_simulator import NLGTemplate, NLG, import_yaml


class UserSimNLGTemplate(NLGTemplate):

    def __init__(self):
        nlg_template = import_yaml("sample_domains/movies/nlg_usersim_rules.yml")
        super(UserSimNLGTemplate, self).__init__(nlg_template)
