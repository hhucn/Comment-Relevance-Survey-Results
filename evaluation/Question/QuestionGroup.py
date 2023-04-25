from typing import List, Union

import numpy as np
from scipy.stats import stats
from statsmodels.stats.proportion import proportion_confint

from evaluation.Answer.Answer import Answer
from evaluation.Question.Question import Question


class QuestionGroup:
    # cn_id: str
    # group_ident: str
    # questions: List[Question]
    # answers: List[Answer]

    def __init__(self, questions: List[Question]):
        for q in questions:
            assert q._text_ident_part() == questions[0]._text_ident_part(), f"{q.cn_id}/{questions[0].cn_id}: {q.text} and {questions[0].text} should match to form a group"
            assert q.cn_id[:-1] == questions[0].cn_id[:-1], f"{q.cn_id}/{questions[0].cn_id[:-1]}: IDs should have the same prefix to form a group"
            assert len(q.answers) == len(questions[0].answers), f"{q.cn_id}/{questions[0].cn_id[:-1]}: number of answers differs"
        if len(questions) == 1:
            self.cn_id = questions[0].cn_id
        else:
            self.cn_id = questions[0].cn_id[:-1]
        self.group_ident = questions[0].group_ident()
        # note special cases Pc2, D8f where order of answers is changed
        self.answers = []
        discard_answers = False
        for q in questions:
            for a_idx, a in enumerate(q.answers):
                if len(self.answers) <= a_idx:
                    self.answers.append(Answer(None, a.text))
                    self.answers[a_idx].expected = a.expected
                self.answers[a_idx].selection_frequency += a.selection_frequency
                if self.answers[a_idx].text != a.text:
                    print(f"No matching texts in answers for {self.group_ident}: {self.answers[a_idx].text} / {a.text}")
                    discard_answers = True
                if self.answers[a_idx].expected != a.expected:
                    print(f"No matching expected answers for {self.group_ident}: {self.answers[a_idx].text} / {a.text}")
                    discard_answers = True
        if discard_answers:
            self.answers = []

        self.questions = questions

    def number_of_answers(self) -> np.int64:
        return np.nansum([q.number_of_answers() for q in self.questions])

    def percentage_with_expected_answer(self) -> float:
        return np.nanmean([q.percentage_with_expected_answer() for q in self.questions])

    def frequency_of_expected_answer(self) -> np.int64:
        return np.sum([q.frequency_of_expected_answer() for q in self.questions])

    def p_value(self, n: Union[int, np.int64]) -> float:
        """
        :return: the probability of obtaining at least n answers, assuming that that answer is not the most frequently chosen one
        """
        if len(self.answers) == 0:
            return 1
        all_frequencies = sorted([a.selection_frequency for a in self.answers])
        all_frequencies.remove(n)
        return Question.p_for_winner_proportion_difference(n, all_frequencies[-1], self.number_of_answers())

    def n_answers_are_significant(self, n: Union[int, np.int64], niveau: float = 0.01) -> np.bool_:
        """
        :return: True if n answers are significantly the most chosen answer option (default 1 % niveau)
        """
        return self.p_value(n) < niveau

    def confidence_interval(self, n: float, niveau: float = 0.01) -> (float, float):
        """
        Return the confidence interval for n given answers
        """
        return proportion_confint(n, self.number_of_answers(), niveau, "beta")

    def answer_confidence_interval_not_overlapping_and_best(self, answer: Answer, niveau: float = 0.01) -> float:
        """
        Returns true if the lower bound of th confidence interval for the given answer is not included (and larger) than
        evey confidence interval for every other answer
        :return:
        """
        lbound = self.confidence_interval(answer.selection_frequency, niveau)[0]
        return sum(self.confidence_interval(a.selection_frequency, niveau)[1] >= lbound for a in set(self.answers) - {answer}) == 0

    def expected_answer_significantly_given(self, niveau: float = 0.01) -> np.bool_:
        """
        :return: True if the expected answer was given significantly more often than 50 % (default 1 % niveau)
        """
        return self.n_answers_are_significant(self.frequency_of_expected_answer(), niveau)

    def expected_answer_std(self) -> float:
        return np.nanstd([q.percentage_with_expected_answer() for q in self.questions])

    def expected_answer_significantly_different(self) -> bool:
        """
        Performs a two-sided exact fisher test with every combination of two questions.
        :returns True if in any combination there is a significant (5 %) correlation of choosing the expected answer and the question asked.

                          expected answer given    expected answer not given
        this questions              a                         b
        others questions            c                         d

        https://pythonhealthcare.org/2018/04/13/59-statistics-fishers-exact-test/
        """
        for question1 in self.questions:
            for question2 in self.questions:
                a = question1.expected_answer().selection_frequency
                b = question1.number_of_answers() - a
                c = question2.expected_answer().selection_frequency
                d = question2.number_of_answers() - c
                _, p_value = stats.fisher_exact([[a, b], [c, d]])
                if p_value < .05:
                    return True
        return False

    def print_stats(self):
        print(f"QG {self.group_ident}")
        print(self.questions[0].scenario)
        print(f"  {self.percentage_with_expected_answer()}, good? {self.expected_answer_significantly_given()} (std {self.expected_answer_std()}, significant deviation? {self.expected_answer_significantly_different()})")
        for question in self.questions:
            print(f"  Q {question.cn_id}")
            print(f"    {question.percentage_with_expected_answer()}")

