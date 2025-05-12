import json

from pyramid.httpexceptions import HTTPBadRequest

from climmob.views.classes import privateView, apiView
from climmob.views.validators.BaseValidator import BaseValidator


class QuestionMinMaxValidator(BaseValidator):
    def __init__(self, view):
        super().__init__(view)
        self.question = {}
        if issubclass(self.view.__class__, privateView):
            self.question = self.view.getPostDict()

        elif issubclass(self.view.__class__, apiView):
            self.question = json.loads(self.view.body)

    def run(self):
        if not self.is_question_type_integer_or_decimal():
            if (
                "question_min" in self.question.keys()
                or "question_max" in self.question.keys()
            ):
                raise HTTPBadRequest(
                    "Non-numerical questions may not have min nor max set"
                )

        if self.question.get("question_min", "") == "":
            self.question["question_min"] = None
        if self.question.get("question_max", "") == "":
            self.question["question_max"] = None

        question_min, question_max = None, None

        if self.question["question_min"] is not None:
            try:
                question_min = float(self.question["question_min"])
            except ValueError:
                raise HTTPBadRequest("The minimum must be a number")

        if self.question["question_max"] is not None:
            try:
                question_max = float(self.question["question_max"])
            except ValueError:
                raise HTTPBadRequest("The maximum must be a number")

        if question_min is None or question_max is None:
            return

        if question_min >= question_max:
            raise HTTPBadRequest("The minimum must be less than the maximum")

    def is_question_type_integer_or_decimal(self):
        return (
            self.question.get("question_dtype") == "2"
            or self.question.get("question_dtype") == "3"
        )
