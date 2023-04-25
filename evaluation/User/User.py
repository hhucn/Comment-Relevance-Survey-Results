from typing import Optional

import numpy as np


class User:
    def __init__(self, user_answers: dict):
        self.user_answers = user_answers

    def get_answer_value(self, question_id) -> Optional[int]:
        answer = self.user_answers[question_id]
        if np.isnan(answer) or answer == 0:
            return None
        return int(answer)

    def get_code(self) -> int:
        return self.user_answers["c_0001"]
