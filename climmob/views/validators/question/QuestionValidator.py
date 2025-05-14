import json

from climmob.views.classes import privateView, apiView
from climmob.views.validators.BaseValidator import BaseValidator


class QuestionValidator(BaseValidator):
    def __init__(self, view):
        super().__init__(view)
        self.question = {}
        if issubclass(self.view.__class__, privateView):
            self.question = self.view.getPostDict()

        elif issubclass(self.view.__class__, apiView):
            self.question = json.loads(self.view.body)
