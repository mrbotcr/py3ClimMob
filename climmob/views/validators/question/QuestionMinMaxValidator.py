import json

from pyramid.httpexceptions import HTTPBadRequest

from climmob.utility import is_type_numerical
from climmob.views.classes import privateView, apiView
from climmob.views.validators.BaseValidator import BaseValidator


class QuestionMinMaxValidator(BaseValidator):
    def __init__(self, view):
        super().__init__(view)
        self.question = {}

        self.extract_question()

        self.min, self.max = None, None

        self.question_dtype = None

    def extract_question(self):
        if issubclass(self.view.__class__, privateView):
            self.question = self.view.getPostDict()

        elif issubclass(self.view.__class__, apiView):
            self.question = json.loads(self.view.body)

        else:
            raise TypeError

    def run(self):
        self.set_min_max()
        if self.min == "":
            self.min = None
        if self.max == "":
            self.max = None

        self.set_question_dtype()

        if not is_type_numerical(self.question_dtype):
            if self.min is not None or self.max is not None:
                raise HTTPBadRequest(
                    self._("Non-numerical questions may not have min nor max set")
                )
        if self.min is not None:
            self.min = self.float_parse(self.min, "question_min")

        if self.max is not None:
            self.max = self.float_parse(self.max, "question_max")

        if self.min is None or self.max is None:
            return

        if self.min >= self.max:
            raise HTTPBadRequest(self._("The minimum must be less than the maximum"))

    def set_min_max(self):
        self.min = self.question.get("question_min")
        self.max = self.question.get("question_max")

    def set_question_dtype(self):
        self.question_dtype = self.question.get("question_dtype")
