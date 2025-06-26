import json

from pyramid.httpexceptions import HTTPNotFound

from climmob.processes import assessmentExists
from climmob.views.classes import privateView, apiView
from climmob.views.validators.BaseValidator import BaseValidator


class AssessmentExistsValidator(BaseValidator):
    def __init__(self, view):
        super().__init__(view)
        self.ass_cod = None
        self.extract()

    def extract(self):
        if issubclass(self.view.__class__, privateView):
            self.ass_cod = self.view.request.assessmentid

        elif issubclass(self.view.__class__, apiView):
            body = json.loads(self.view.body)
            self.ass_cod = body["ass_cod"]

        else:
            raise TypeError

    def run(self):
        if not assessmentExists(
            self.view.context.active_project_id,
            self.ass_cod,
            self.view.request,
        ):
            raise HTTPNotFound(self._("There is no data collection with that code."))
