class Answer:
    def __init__(self, value_id: str, text: str):
        self._answer_value = int(value_id)
        self._text = text
        self._frequency = 0
        self._expected_answer = False

    def make_expected_answer(self):
        self._expected_answer = True

    def get_answer_value(self):
        return self._answer_value

    def get_answer_text(self):
        return self._text

    def is_expected_answer(self):
        return self._expected_answer

    def increase_frequency(self):
        self._frequency += 1

    def get_frequency(self) -> int:
        return self._frequency

    def add_answer_frequency(self, given_answer):
        self._frequency += given_answer.get_frequency()

