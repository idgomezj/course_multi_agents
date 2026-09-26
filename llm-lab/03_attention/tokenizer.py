from config import TRAINING_FILE


class CharacterTokenizer:

    def __init__(self):

        with open(
            TRAINING_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()


        self.characters = sorted(
            list(set(text))
        )


        self.vocab_size = len(
            self.characters
        )


        self.stoi = {

            character: index

            for index, character
            in enumerate(
                self.characters
            )
        }


        self.itos = {

            index: character

            for index, character
            in enumerate(
                self.characters
            )
        }


    def encode(self, text):

        return [

            self.stoi[
                character
            ]

            for character
            in text
        ]


    def decode(self, tokens):

        return "".join(

            self.itos[token]

            for token
            in tokens
        )