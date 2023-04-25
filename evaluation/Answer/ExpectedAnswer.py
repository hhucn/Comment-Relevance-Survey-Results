class ExpectedAnswer:
    def __init__(self, question_id: str, answer: str):
        self._question_id = question_id
        self._answer = answer
        self._answer_value = self.parse_answer(answer)

    @staticmethod
    def parse_answer(answer):
        if answer == "Alice>Bob" \
                or answer == "Alice>Charlie" \
                or answer == "Alice>Daisy" \
                or answer == "Bob>Charlie" \
                or answer == "Bob>Daisy" \
                or answer == "Charlie>Daisy" \
                or answer == "Relevant"\
                or answer == "Alice":
            return 1
        elif answer == "Bob>Alice" \
                or answer == "Charlie>Alice" \
                or answer == "Daisy>Alice" \
                or answer == "Daisy>Bob" \
                or answer == "Charlie>Bob" \
                or answer == "Daisy>Charlie" \
                or answer == "Not Relevant"\
                or answer == "Bob":
            return 2
        elif answer == "Equally" or answer == "Cannot Assessed":
            return 3
        raise Exception("Given answer does not exist")

    def get_question_id(self):
        return self._question_id

    def get_answer_value(self):
        return self._answer_value
