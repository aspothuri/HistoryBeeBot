from pdf_reader import parse
# from tts import text_to_speech
from rapidfuzz import fuzz
from gtts import gTTS
import os

class Game:
    def __init__(self, file_path):
        self.qa = parse(file_path)
        self.scores = {}
        self.qNum = 1
        self.midQ = False

    def next_question(self):
        self.midQ = False
        self.qNum += 1

    def isCorrect(self, answer, threshold=55):
        correct_answer = self.qa['answers'][self.qNum-1].strip().lower()
        user_answer = answer.strip().lower()
        similarity = fuzz.ratio(user_answer, correct_answer)
        return similarity >= threshold
    
    def buzz(self, player, answer):
        print(self.qa['answers'][self.qNum-1].strip(), '|')
        if self.isCorrect(answer):
            self.scores[player] = self.scores.get(player, 0) + 10
            return True
        elif self.midQ:
            self.scores[player] = self.scores.get(player, 0) - 5
            return False

    # converts the text into an audio file and returns the file path of it
    def text_to_speech(self):
        file_path = f"audio_files/{self.qNum}.mp3"

        text = self.qa['questions'][self.qNum-1].strip().lower()

        if not os.path.exists(file_path):
            language = 'en'
            myobj = gTTS(text=text, lang=language, slow=False)
            myobj.save(file_path)

        return file_path

    # generate an audio file of the current tossup and return the file path
    def get_tossup(self):
        return self.text_to_speech()
