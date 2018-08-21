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


from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pickle
from numpy import argmax


class NLGModel(NLG):

    def __init__(self):
        self.model = load_model("sample_domains/restaurant/models/nlg_model.h5")
        tokenizers = pickle.load(open("sample_domains/restaurant/models/tokenizers.pkl", "rb"))
        self.utterance_tokenizer = tokenizers["utterance_tokenizer"]
        self.utterance_length = tokenizers["utterance_length"]
        self.action_tokenizer = tokenizers["action_tokenizer"]
        self.action_length = tokenizers["action_length"]

    def create_tokenizer(data, char_level=False):
        tokenizer = Tokenizer(char_level=char_level)
        tokenizer.fit_on_texts(data)
        return tokenizer

    # max sentence length
    def max_length(data):
        return max(len(line.split()) for line in data)

    def encode_sequences(self, tokenizer, length, lines):
        X = tokenizer.texts_to_sequences(lines)
        X = pad_sequences(X, maxlen=length, padding='post')
        return X

    def word_for_id(self, integer, tokenizer):
        for word, index in tokenizer.word_index.items():
            if index == integer:
                return word
        return None

    def predict_sequence(self, model, tokenizer, source):
        prediction = model.predict(source, verbose=0)[0]
        integers = [argmax(vector) for vector in prediction]
        target = list()
        for i in integers:
            word = self.word_for_id(i, tokenizer)
            if word is None:
                break
            target.append(word)
        return ''.join(target)

    def get_utterance(self, action: 'DialogAction'):
        return self.predict_utterance(action.toString())

    def predict_utterance(self, action):
        encoded_action = self.encode_sequences(self.action_tokenizer,
                                               self.action_length,
                                               [action])
        pred = self.predict_sequence(self.model,
                                     self.utterance_tokenizer,
                                     encoded_action)
        return pred + "&"
