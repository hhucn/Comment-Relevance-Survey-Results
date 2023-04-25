from typing import List, Union

import numpy as np
from numpy import ndarray
from scipy.stats import fisher_exact, norm
from statsmodels.stats.proportion import proportion_confint

from evaluation.Answer.Answer import Answer
from evaluation.Question.Question import Question


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


class Hypothesis:
    def __init__(self, hypothesis_id: str):
        self._hypothesis_id = hypothesis_id
        self._questions = []

    def add_questions(self, given_questions: List[Question]):
        for gq in given_questions:
            if self.is_new_question(gq):
                self.add_question(Question(None, gq.get_question_text()))
            for q in self.get_questions():
                if q.get_question_text() == gq.get_question_text():
                    q.aggregate_answers(gq.get_answers())

    def add_question(self, given_question: Question) -> None:
        self._questions.append(given_question)

    def get_questions(self) -> List[Question]:
        return self._questions

    def is_new_question(self, given_question: Question) -> bool:
        return given_question.get_question_text() not in set([q.get_question_text() for q in self.get_questions()])

    def get_hypothesis_id(self):
        return self._hypothesis_id

    def print_stats(self):
        print(f"Hypothesis: {self._hypothesis_id}")
        print(
            f"Expected answer given by: {100 * self.percentage_with_expected_answer():.2f}% , good? "
            f"{self.expected_answer_significantly_given()} "
            f"p-value {self.max_p_value():.3f}"
            f"(std {self.expected_answer_std()}"
            f" significant deviation? {self.expected_answer_significantly_different()}")
        if self.expected_answer_significantly_given(0.01):
            print(f"Significance = 1%")
        elif self.expected_answer_significantly_given(0.05):
            print(f"Significance = 5%")
        elif self.expected_answer_significantly_given(0.1):
            print(f"Significance = 10%")

        print(f"Standard deviation within this group: {self.expected_answer_std():.4f} \n")

        for question in self.get_questions():
            print(f"Question: {question.get_question_text()}")
            print(f"Expected Answer given by: {100 * question.percentage_with_expected_answer():2f}%\n")

            for a in question.get_answers():
                print(f" {a.get_answer_text()} {'EXPECTED ANSWER' if a.is_expected_answer() else ''}")
                print(f"{100 * a.get_frequency() / question.number_of_answers():.0f}% " \
                      f"({a.get_frequency()}/{question.number_of_answers()}" \
                      f",({self.confidence_interval(a.get_frequency(), 0.05)[0]:.2f}," \
                      f"{self.confidence_interval(a.get_frequency(), 0.05)[1]:.2f})," \
                      f"p={question.p_value(a.get_frequency()):.3f})")
            print("\n")

    def percentage_with_expected_answer(self) -> ndarray:
        return np.nanmean([q.percentage_with_expected_answer() for q in self._questions])

    def expected_answer_significantly_given(self, niveau: float = 0.01):
        """
        Return True if the expected answer was given significantly more often than 50% (default 1 % niveau)
        """
        return self.max_p_value() < niveau

    def get_answers(self) -> List[Answer]:
        answers = []
        [answers.extend(q.get_answers()) for q in self.get_questions()]
        return answers

    def number_of_answers(self):
        return np.nansum([q.number_of_answers() for q in self.get_questions()])

    def expected_answer_std(self):
        return np.nanstd([q.percentage_with_expected_answer() for q in self.get_questions()])

    def expected_answer_significantly_different(self):
        """
        Performs a two-sided exact fisher test with every combination of two questions.
        :returns True if in any combination there is a significant (5 %) correlation of choosing the expected answer and the question asked
                          expected answer given    expected answer not given
        this questions              a                         b
        others questions            c                         d
        https://pythonhealthcare.org/2018/04/13/59-statistics-fishers-exact-test/
        """
        for question1 in self.get_questions():
            for question2 in self.get_questions():
                a = question1.get_expected_answer().get_frequency()
                b = question1.number_of_answers() - a
                c = question2.get_expected_answer().get_frequency()
                d = question2.number_of_answers() - c
                _, p_value = fisher_exact([[a, b], [c, d]])
                if p_value < .05:
                    return True
        return False

    def confidence_interval(self, n: float, niveau: float = 0.01) -> (float, float):
        """
        Return the confidence interval for n given answers
        """
        return proportion_confint(n, self.number_of_answers(), niveau, "beta")

    def p_value(self, n: Union[int, np.int64]) -> float:
        """
        :return: the probability of obtaining at least n answers, assuming that that answer is not the most frequently chosen one
        """
        if len(self.get_answers()) == 0:
            return 1
        all_frequencies = sorted([a.get_frequency() for a in self.get_answers()])
        all_frequencies.remove(n)
        return p_for_winner_proportion_difference(n, all_frequencies[-1], self.number_of_answers())

    def max_p_value(self):
        return np.nanmax([p.p_value(p.frequency_of_expected_answer())
                          for p in self.get_questions()])
