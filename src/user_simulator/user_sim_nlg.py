class DialogTemplates:

    def __init__(self):
        self.dialog_acts =[]
        self.dialog_templates = {}

    def add_dialog_act(self, dialog_act:str)->None:
        self.dialog_acts.append(dialog_act)
        if dialog_act not in self.dialog_templates.keys():
            self.dialog_templates[dialog_act] = {}

    def add_dialog_tempate(self, dialog_act: str, key: str, template: str)->None:
        self.dialog_acts[dialog_act][key] = template

