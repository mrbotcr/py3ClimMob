from pyramid.httpexceptions import HTTPBadRequest

from climmob.processes import getQuestionData
from climmob.utility import is_type_numerical
from climmob.views.validators.question.QuestionValidator import QuestionValidator


class QuestionUpdateMinMaxValidator(QuestionValidator):
    def run(self):
        current_question = self.get_question_data()

        self.check_question_type(current_question)

        question_min = self.question.get(
            "question_min", current_question["question_min"]
        )
        question_max = self.question.get(
            "question_max", current_question["question_max"]
        )

        if question_min == "":
            question_min = None

        if question_max == "":
            question_max = None

        if question_min is not None:
            try:
                question_min = float(question_min)
            except ValueError:
                raise HTTPBadRequest("The minimum must be a number")

        if question_max is not None:
            try:
                question_max = float(question_max)
            except ValueError:
                raise HTTPBadRequest("The maximum must be a number")

        if question_min is None or question_max is None:
            return

        if question_min >= question_max:
            raise HTTPBadRequest("The minimum must be less than the maximum")

    def check_question_type(self, current_question):
        q_type = self.question.get(
            "question_dtype", str(current_question["question_dtype"])
        )
        if not is_type_numerical(q_type):
            if (
                "question_min" in self.question.keys()
                or "question_max" in self.question.keys()
            ):
                raise HTTPBadRequest(
                    "Non-numerical questions may not have min nor max set"
                )

    def get_question_data(self):
        current_question, _ = getQuestionData(
            self.view.user.login, self.question.get("question_id"), self.view.request
        )
        return current_question
