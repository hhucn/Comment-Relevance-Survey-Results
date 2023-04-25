from typing import List, Union

import numpy as np
from scipy.stats import norm
from statsmodels.stats.proportion import proportion_confint

from evaluation.Answer.Answer import Answer
from evaluation.Answer.ExpectedAnswer import ExpectedAnswer


class Question:
    def __init__(self, question_id: str, text: str):
        self._question_id = question_id
        self._text = text
        self._answers = []

    def is_control_question(self):
        return self._question_id in {"v_392", "v_393", "v_394", "v_447", "v_448", "v_449"}

    def set_expected_answers(self, expected_answers: List[ExpectedAnswer]):
        for expected_answer in expected_answers:
            if expected_answer.get_question_id() == self._question_id:
                assert len([a for a in self.get_answers() if a.is_expected_answer()]) == 0, "Expected Answer already set!"
                [a.make_expected_answer() for a in self._answers
                 if expected_answer.get_answer_value() == a.get_answer_value()]

    def append_answer(self, answer: Answer):
        self._answers.append(answer)

    def aggregate_answers(self, given_answers: List[Answer]):
        for ga in given_answers:
            if self.is_new_answer(ga):
                self.append_answer(Answer(ga.get_answer_value(), ga.get_answer_text()))
            for a in self._answers:
                if ga.get_answer_text() == a.get_answer_text():
                    a.add_answer_frequency(ga)
                if ga.is_expected_answer() and ga.get_answer_text() == a.get_answer_text():
                    a.make_expected_answer()

    def is_new_answer(self, given_answer: Answer) -> bool:
        answers = [a.get_answer_value() for a in self.get_answers()]
        assert len(answers) <= 3, "Too many answers per question"
        return given_answer.get_answer_value() not in answers
    def get_expected_answer(self) -> Answer:
        return [a for a in self._answers if a.is_expected_answer()][0]

    def get_question_id(self) -> str:
        return self._question_id

    def get_question_text(self) -> str:
        return self._text

    def get_answers(self) -> List[Answer]:
        return self._answers

    def is_expected_answer(self, answer_value: int):
        return self.get_expected_answer().get_answer_value() == answer_value

    def add_given_answer(self, given_answer_value: int):
        for answer in self._answers:
            if answer.get_answer_value() == given_answer_value:
                answer.increase_frequency()

    def percentage_with_expected_answer(self):
        if self.number_of_answers() == 0:
            print(f"[WARN] {self.get_question_id()} has no answers")
            return 1
        return self.frequency_of_expected_answer() / self.number_of_answers()

    def number_of_answers(self):
        return sum(a.get_frequency() for a in self.get_answers())

    def frequency_of_expected_answer(self) -> int:
        assert len([a for a in self.get_answers() if a.is_expected_answer()]) == 1, "Should only be one expected answer"
        return next(a.get_frequency() for a in self.get_answers() if a.is_expected_answer())

    def p_value(self, n: Union[int, np.int64]):
        if len(self.get_answers()) == 0:
            return 1
        all_frequencies = sorted([a.get_frequency() for a in self.get_answers()])
        all_frequencies.remove(n)
        p = p_for_winner_proportion_difference(n, all_frequencies[-1], self.number_of_answers())
        return p




    def confidence_interval(self, n: float, niveau: float = 0.05) -> (float, float):
        """
        Return the confidence interval for n given answers

        Interpretation: If we did several surveys, the probability that n for those repetitions is not in this interval is niveau.

        Note the following relation to significance (but note it's not exact, b/c the assumptions are different: p = 0.5 vs. p=26/40
        statsmodels.stats.proportion.proportion_confint(26, 40, 0.05)
        (0.5021883054602991, 0.7978116945397009)
        stats.binom_test(26, 40, p=.5, alternative="greater")
        0.04034523387599622
        2*(1-stats.binom_test(20, 40, p=26/40, alternative="greater"))
        0.034561618646322234 <= α
        :return: confidence interval
        """
        return proportion_confint(n, self.number_of_answers(), niveau, "beta")

def p_for_winner_proportion_difference(n_winner: Union[int, np.int64], n_second: Union[int, np.int64],
                                       n: Union[int, np.int64]) -> float:
    assert n >= n_winner + n_second
    assert n > 5
    p_winner = n_winner / n
    p_second = n_second / n
    assert 0 <= p_winner <= 1
    assert 0 <= p_second <= 1
    delta = p_winner - p_second
    var = ((p_winner + p_second) - (p_winner - p_second) ** 2) / n
    z = delta / np.sqrt(var)
    p = 1 - norm.cdf(z)
    assert 0 <= p <= 1
    return p


