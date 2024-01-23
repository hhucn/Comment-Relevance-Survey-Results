from typing import List

from evaluation.Answer.ExpectedAnswer import ExpectedAnswer
from evaluation.Question.Question import Question


class HypothesisPage:
    # hypothesis_id: e.g. H1
    # hypothesis_text: e.g. "H1: Chia Seeds Pro"
    # questions: List[Questions]
    # pgid: PageId e.g. 6197635
    def __init__(self, hypothesis_id: str, hypothesis_text: str, pgid: str):
        self._hypothesis_id = hypothesis_id
        self._pgid = int(pgid)
        self._hypothesis_text = hypothesis_text
        self._questions: List[Question] = []

    def add_questions(self, question: Question):
        self._questions.append(question)

    def set_expected_answers(self, expected_answers: List[ExpectedAnswer]):
        [q.set_expected_answers(expected_answers) for q in self.get_questions()]

    def get_questions(self):
        return self._questions

    def get_hypothesis_id(self):
        return self._hypothesis_id

    def get_hypothesis_pgid(self) -> int:
        return self._pgid

    def is_neutral_topic(self):
        if "Solar" in self._hypothesis_text or "Football" in self._hypothesis_text:
            return False
        return True

