import spacy


class InstructionParser:
    """
    Parses natural language navigation instructions.

    Extracts:
    - actions (verbs)
    - landmarks (nouns)
    - directions
    - colors
    - counts
    - modifiers (near, around, toward)
    """

    def __init__(self):

        try:
            self.nlp = spacy.load("en_core_web_sm")

        except:

            # fallback if model not installed
            from spacy.cli import download

            download("en_core_web_sm")

            self.nlp = spacy.load("en_core_web_sm")

        # navigation directions
        self.direction_words = {
            "left", "right", "forward", "back",
            "north", "south", "east", "west",
            "up", "down"
        }

        # object color words
        self.color_words = {
            "red", "blue", "green", "black",
            "white", "yellow", "orange",
            "brown", "gray"
        }

        # spatial modifiers
        self.modifiers = {
            "near", "around", "toward", "towards",
            "beside", "behind", "infront", "ahead"
        }

    # -----------------------------------------------------

    def parse(self, instruction: str):

        doc = self.nlp(instruction.lower())

        actions = []
        landmarks = []
        directions = []
        colors = []
        modifiers = []
        counts = []

        # detect noun phrases (multi-word objects)
        for chunk in doc.noun_chunks:

            phrase = chunk.text.strip()

            if phrase not in landmarks:
                landmarks.append(phrase)

        for token in doc:

            # verbs → actions
            if token.pos_ == "VERB":
                actions.append(token.text)

            # nouns → landmarks / objects
            if token.pos_ == "NOUN" and token.text not in {"it", "them", "this", "that"}:
                landmarks.append(token.text)

            # direction words
            if token.text in self.direction_words or token.lemma_ in self.direction_words:
                directions.append(token.text)

            # colors
            if token.text in self.color_words:
                colors.append(token.text)

            # modifiers
            if token.text in self.modifiers:
                modifiers.append(token.text)

            # numbers (for actions like circle 3 times)
            if token.like_num:
                try:
                    counts.append(int(token.text))

                except:
                    counts.append(token.text)

        # remove duplicates
        actions = list(set(actions))
        landmarks = list(set(landmarks))
        directions = list(set(directions))
        colors = list(set(colors))
        modifiers = list(set(modifiers))

        # -----------------------------------------
        # YOLO LABEL NORMALIZATION
        # -----------------------------------------
        normalized_landmarks = []

        for l in landmarks:

            l = l.lower()

            # HUMAN NORMALIZATION
            if l in ["human", "people", "man", "woman"]:
                normalized_landmarks.append("person")

            # VEHICLE NORMALIZATION
            elif l in ["vehicle", "van", "truck", "bus"]:
                normalized_landmarks.append("car")

            else:
                normalized_landmarks.append(l)

        landmarks = list(set(normalized_landmarks))
        

        return {
            "instruction": instruction,
            "actions": actions,
            "landmarks": landmarks,
            "directions": directions,
            "colors": colors,
            "modifiers": modifiers,
            "counts": counts
        }


# -----------------------------------------------------

if __name__ == "__main__":

    parser = InstructionParser()

    example = "go near the red car and circle around it three times"

    result = parser.parse(example)

    print("\nParsed Instruction\n")
    print(result)