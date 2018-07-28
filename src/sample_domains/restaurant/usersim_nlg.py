from dialog_simulator import NLG, DialogAction


class TemplateNLG(NLG):

    def __init__(self, template_file: s):
        pass

    def _generate_utterance(self, nl_template: str,
                            dialog_action: DialogAction):
        slots = self.re_nlg_pattern.findall(nl_template)
        for tup in slots:
            replace_val = dialog_action.params[tup[1].lower()]
            nl_template = nl_template.replace(''.join(tup), replace_val)
        return nl_template

    # ------------- Generate Utterance using Model ---------------------- #
    def _model_generate_utterance(self, dialog_action: DialogAction):
        """ Method will be overridden with local implementation. """
        return None

    # ------------- Class Public Methods -------------------------------- #
    def get_utterance(self, dialog_action: DialogAction) -> str:
        if self.type == "dict":
            if "default" in dialog_action.params or not bool(
                    dialog_action.params):
                default_exp = \
                self.model["dialog_acts"][dialog_action.dialog_act]["default"]
                if len(default_exp) > 0:
                    return random.choice(
                        self.model["dialog_acts"][dialog_action.dialog_act][
                            "default"])
                else:
                    return default_exp
            else:
                # Generate natural language template
                param_keys = dialog_action.get_param_keys()
                nl_template = random.choice(
                    self.model["dialog_acts"][dialog_action.dialog_act][
                        param_keys])
                utterance = self._generate_utterance(nl_template, dialog_action)
        else:
            utterance = self._model_generate_utterance(dialog_action)

        return utterance

    def get_model(self):
        return {"model": self.model, "type": self.type}

    def __str__(self):
        return "NLG v.%s, domain: %s" % (self.version, self.domain)


