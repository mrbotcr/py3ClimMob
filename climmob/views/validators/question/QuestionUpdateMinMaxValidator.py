from climmob.processes import getQuestionData
from climmob.views.validators.question.QuestionMinMaxValidator import (
    QuestionMinMaxValidator,
)


class QuestionUpdateMinMaxValidator(QuestionMinMaxValidator):
    def __init__(self, view):
        super().__init__(view)
        self.old_question = self.get_question_data()

    def get_question_data(self):
        current_question, _ = getQuestionData(
            self.view.user.login, self.question.get("question_id"), self.view.request
        )
        return current_question

    def set_min_max(self):
        super().set_min_max()
        if self.min is None:
            self.min = self.old_question["question_min"]
        if self.max is None:
            self.max = self.old_question["question_max"]

    def set_question_dtype(self):
        super().set_question_dtype()
        if self.question_dtype is None:
            self.question_dtype = self.old_question["question_dtype"]
