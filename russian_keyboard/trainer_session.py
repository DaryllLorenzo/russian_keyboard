import random


class TrainingSession:
    def __init__(self, vocabulary, words_per_session=10):
        self.vocabulary = vocabulary[:]
        self.words_per_session = min(words_per_session, len(vocabulary))
        self.words_to_practice = []
        self.current_index = 0
        self.correct_count = 0
        self.mistakes = []

    def generate_session(self):
        self.words_to_practice = random.sample(self.vocabulary, self.words_per_session)
        self.current_index = 0
        self.correct_count = 0
        self.mistakes = []

    def current_word(self):
        if self.current_index < len(self.words_to_practice):
            return self.words_to_practice[self.current_index]
        return None

    def advance(self, was_correct):
        if was_correct:
            self.correct_count += 1
        else:
            current = self.current_word()
            if current:
                self.mistakes.append(current)
        self.current_index += 1
        return self.current_index >= len(self.words_to_practice)

    def get_progress(self):
        return (self.current_index, len(self.words_to_practice))

    def get_score(self):
        if self.words_per_session == 0:
            return 0
        return (self.correct_count / self.words_per_session) * 100
