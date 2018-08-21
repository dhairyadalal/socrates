from dialog_simulator import NLU
import re

class NLUsimple(NLU):
    """ Simple NLU engine using NLP rules """

    def __init__(self, domain: 'Domain'):
        self.domain = domain
        self.ents = self._lookup_ents()
        self.QUESTION_POS_SEQUENCES = [["WP", "MD", "NN", "VB"],
                                       ["WR", "MD", "NN", "VB"],
                                       ["WP", "MD", "PR", "VB"],
                                       ["WR", "MD", "PR", "VB"],
                                       ["MD", "NN", "VB"],
                                       ["WR", "VB", "PR"],
                                       ["WR", "VB", "NN"],
                                       ["WP", "VB", "NN"],
                                       ["WP", "VB", "PR"]]
        self.nlp = spacy.load('en')

    def _simple_question_classifier(self, text: str) -> bool:
        # check if last token is '?'
        if text.strip()[-1] == '?':
            return True

        parsed_text = self.nlp(text)

        # chunk noun phrases into single token
        for noun_phrase in list(parsed_text.noun_chunks):
            noun_phrase.merge()

        # only care about the first two letters of the POS tag
        pos_tags = [token.tag_[0:2] for token in parsed_text]

        # check if first word lemma is be or do
        if parsed_text[0].lemma_ in ["be", "do"]:
            if pos_tags[1] in ["RB"]:  # ignore not case e.g. don't, isn't
                if pos_tags[2] in ["NN", "PR"]:
                    return True
            if pos_tags[1] in ["NN", "PR"]:
                return True

        if len(pos_tags) > 1:
            # check if first pos_tag is "MD" then "PR or NN" e.g. "Can recommender help"
            if pos_tags[0] == "MD" and pos_tags[1] in ["PR", "NN"]:
                return True
            # check if first pos_tag = "WP or WR" then "VB"--> "what does Recommender do"
            if pos_tags[0] in ["WP", "WR"] and pos_tags[1] == "VB":
                return True

        # check for pos patterns of interest
        for i in range(len(parsed_text)):
            for pattern in self.QUESTION_POS_SEQUENCES:
                if pattern == pos_tags[i: i + len(pattern)]:
                    return True

        return False

    def _intent_classifier(self, sent: str) -> str:

        # Confirm intent
        confirm_re = re.compile("you|you want|right\?")
        if confirm_re.match(sent.lower()):
            return "confirm"

        # Request intent
        if self._simple_question_classifier(sent):
            return "request"

        # Affirm intent regular expression
        affirm_re = re.compile("yes|yeah|yup|correct|right")
        if affirm_re.match(sent.lower()):
            return "affirm"

        # Negate intent
        negate_re = re.compile("no|nope|wrong|incorrect")
        if negate_re.match(sent.lower()):
            return "negate"

        # Greeting intent
        greetings_re = re.compile("hi|hello")
        if greetings_re.match(sent.lower()):
            return "greetings"

        # Bye intent
        bye_re = re.compile("bye|goodbye|thanks|thank you")
        if bye_re.match(sent.lower()):
            return "bye"

        # Assume inform intent
        return "inform"


    def _lookup_ents(self):
        ents = dict()

        # Request slots
        for slot in self.domain.request_slots:
            ents[slot] = "request_slot"

        # Inform slots
        for k,v in self.domain.inform_slot_values.items():
            ents.update({i: k for i in v})

        return ents

    def parse_utterance(self, utterance: str):
        intent = self._intent_classifier(utterance)

        params = dict()
        toks = word_tokenize(utterance.lower())
        for tok in toks:
            key = self.ents.get(tok)
            if key == "request_slot":
                params.update({tok: None})
            elif key is not None:
                params.update({key: tok})

        return DialogAction(dialog_act=intent, params=params)
