from typing import List, Tuple

import numpy as np
import pandas as pd

from evaluation.Answer.Answer import Answer
from evaluation.Answer.ExpectedAnswer import ExpectedAnswer
from evaluation.Hypothesis.Hypothesis import Hypothesis
from evaluation.Hypothesis.HypothesisPage import HypothesisPage
from evaluation.Question.Question import Question
from evaluation.User.User import User


def parse_code_book(lines: List[str]) -> List[Question]:
    def parse_question(lines: List[str], current_line: int) -> Tuple[Question, int]:
        text = lines[current_line].split(" (q")[0].strip()
        current_line += 1
        question_id = lines[current_line].split("\t")[0]
        current_line += 1
        question = Question(question_id, text)
        while "\t" in lines[current_line]:
            question_id = lines[current_line].split("\t")[2]
            question_text = lines[current_line].split("\t")[3].strip()
            question.append_answer(Answer(question_id, question_text))
            current_line += 1

        return question, current_line

    current_line = 0
    while "H1" not in lines[current_line]:
        current_line += 1

    hypotheses_pages = []
    cn_id = None

    while current_line < len(lines):
        if "Seite" in lines[current_line]:
            hypothesis_id = lines[current_line].split(":")[1].strip()
            hypothesis_text = lines[current_line].split("(")[0].strip()
            pgid = lines[current_line].split("PGID")[1].split(")")[0].strip()
            hypotheses_pages.append(HypothesisPage(hypothesis_id, hypothesis_text, pgid))
        if "Typ 111" in lines[current_line]:
            question, current_line = parse_question(lines, current_line)
            hypotheses_pages[-1].add_questions(question)
        current_line += 1

    return hypotheses_pages


def parse_users(answers_frame: pd.DataFrame) -> List[User]:
    return [User(series.to_dict()) for _idx, series in answers_frame.iterrows()]


def create_expected_answers(expected_answer_tuples: List[List[List[str] | str]]) -> List[ExpectedAnswer]:
    expected_answers = []
    for expected_answer_tuples in expected_answer_tuples:
        answer_ids = expected_answer_tuples[0]
        expected_answer = expected_answer_tuples[1]
        [expected_answers.append(ExpectedAnswer(answer_id, expected_answer)) for answer_id in answer_ids]
    return expected_answers


def set_expected_answers(hypotheses_pages: List[HypothesisPage], expected_answer: List[ExpectedAnswer]):
    [h.set_expected_answers(expected_answer) for h in hypotheses_pages]


def get_control_questions(hypotheses_pages: List[HypothesisPage], user: User) -> List[Question]:
    control_questions = []
    for hypothesis_page in hypotheses_pages:
        for q in hypothesis_page.get_questions():
            if q.is_control_question() and user.get_answer_value(q.get_question_id()) is not None:
                control_questions.append(q)
    return control_questions


def filter_reliable_users(hypotheses_pages: List[HypothesisPage], users: List[User]) -> List[User]:
    reliable_users = []
    for user in users:
        control_questions = get_control_questions(hypotheses_pages, user)
        correct_questions = 0
        for question in control_questions:
            if question.is_expected_answer(user.get_answer_value(question.get_question_id())):
                correct_questions += 1
        if correct_questions > np.floor(len(control_questions) / 2):
            reliable_users.append(user)
        else:
            print(f"user with code {user.get_code()} unreliable, got {correct_questions} of {len(control_questions)} "
                  f"control questions right")
    print(f"{len(reliable_users)} of {len(users)} users reliable")
    return reliable_users


def add_answer_frequencies(hypothesis_pages: List[HypothesisPage], reliable_users: List[User]):
    for user in reliable_users:
        for page in hypothesis_pages:
            for question in page.get_questions():
                question.add_given_answer(user.get_answer_value(question.get_question_id()))


def create_hypotheses(hypotheses_pages: List[HypothesisPage]) -> dict[str, Hypothesis]:
    hypotheses = {}
    for page in hypotheses_pages:
        if page.get_hypothesis_pgid() != 6189726 and page.get_hypothesis_pgid() != 6249046:
            if hypotheses.get(page.get_hypothesis_id()) is None:
                hypotheses[page.get_hypothesis_id()] = Hypothesis(page.get_hypothesis_id())
            hypotheses.get(page.get_hypothesis_id()).add_questions(page.get_questions())
            if page.is_neutral_topic():
                hypotheses.get(page.get_hypothesis_id()).add_neutral_questions(page.get_questions())
            else:
                hypotheses.get(page.get_hypothesis_id()).add_controversial_questions(page.get_questions())
    return hypotheses


def print_gender(question: Question) -> None:
    if question.get_question_id() == "v_1":
        for answer in question.get_answers():
            if answer.get_answer_value() == 1:
                print(f"Male: {answer.get_frequency()}")
            elif answer.get_answer_value() == 2:
                print(f"Female: {answer.get_frequency()}")
            elif answer.get_answer_value() == 3:
                print(f"Diverse: {answer.get_frequency()}")
            elif answer.get_answer_value() == 4:
                print(f"Different: {answer.get_frequency()}")
            elif answer.get_answer_value() == 5:
                print(f"Not Specified: {answer.get_frequency()}")


def print_age(question: Question) -> None:
    if question.get_question_id() == "v_2":
        for answer in question.get_answers():
            if answer.get_answer_value() == 1:
                print(f"<20: {answer.get_frequency()}")
            elif answer.get_answer_value() == 2:
                print(f"20-29: {answer.get_frequency()}")
            elif answer.get_answer_value() == 3:
                print(f"30-39: {answer.get_frequency()}")
            elif answer.get_answer_value() == 4:
                print(f"40-49: {answer.get_frequency()}")
            elif answer.get_answer_value() == 5:
                print(f"50-59: {answer.get_frequency()}")
            elif answer.get_answer_value() == 6:
                print(f"60-69: {answer.get_frequency()}")
            elif answer.get_answer_value == 7:
                print(f">69: {answer.get_frequency()}")


def print_education(question: Question) -> None:
    if question.get_question_id() == "v_3":
        for answer in question.get_answers():
            if answer.get_answer_value() == 1:
                print(f"No degree: {answer.get_frequency()}")
            elif answer.get_answer_value() == 2:
                print(f"High-School: {answer.get_frequency()}")
            elif answer.get_answer_value() == 3:
                print(f"College Degree: {answer.get_frequency()}")
            elif answer.get_answer_value() == 4:
                print(f"Graduate Degree: {answer.get_frequency()}")
            elif answer.get_answer_value() == 5:
                print(f"Not Specified: {answer.get_frequency()}")


def print_demographic(hypotheses_pages: List[HypothesisPage], type: str) -> None:
    for page in hypotheses_pages:
        if page.get_hypothesis_pgid() == 6189726:
            for question in page.get_questions():
                if type == "gender":
                    print_gender(question)
                elif type == "age":
                    print_age(question)
                elif type == "education":
                    print_education(question)


def calc_average_expected_answer_neutral_topic(hypotheses: dict[Hypothesis]) -> float:
    percentage = []
    for hypotheses_key in hypotheses.keys():
        for question in hypotheses[hypotheses_key].get_neutral_questions():
            percentage.append(question.percentage_with_expected_answer())

    return sum(percentage) / len(percentage)


def calc_average_expected_answer_controversial_topic(hypotheses: dict[Hypothesis]) -> float:
    percentage = []
    for hypotheses_key in hypotheses.keys():
        for question in hypotheses[hypotheses_key].get_controversial_questions():
            percentage.append(question.percentage_with_expected_answer())

    return sum(percentage) / len(percentage)
