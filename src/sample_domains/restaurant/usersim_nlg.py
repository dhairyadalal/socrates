from dialog_simulator import NLGTemplate, NLG, import_yaml
import subprocess
import os

class UserSimNLGmodel(NLG):

    def get_utterance(self, action: 'DialogAction') -> str:


        # 1. covert action to txt file
        with open("action.txt", "w") as file:
            file.write(action.toString()+"\n")
            file.close()

        # 2. Call Opennmt to get a prediction
        run_string = "python ../other_materials/libraries/OpenNMT-py/translate.py -model ../other_materials/libraries/nlg_model/model_step_100000.pt -src action.txt -output pred.txt -replace_unk"
        FNULL = open(os.devnull, 'w')
        args = run_string.split()
        subprocess.call(args, shell=False, stdout=FNULL)

        # 3. Open up prediction
        utterance = ""
        with open("pred.txt", "r") as file:
            utterance = file.read()
            file.close()

        # 3. Clean up temp files
      #  clean_up = ["os.devnull", "action.txt", "pred.txt"]
      #  for file in clean_up:
      #      if os.path.exists(file):
      #          os.remove(file)

        return utterance

class UserSimNLGTemplate(NLGTemplate):

    def __init__(self):
        nlg_template = import_yaml("sample_domains/restaurant/nlg_usersim_rules.yaml")
        super(UserSimNLGTemplate, self).__init__(nlg_template)
