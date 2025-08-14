from pyramid.httpexceptions import HTTPForbidden

from climmob.views.classes import privateView, apiView
from climmob.views.validators.BaseValidator import BaseValidator


class ProjectOpenValidator(BaseValidator):

    def run(self):
        if issubclass(self.view.__class__, privateView) or issubclass(self.view.__class__, apiView):
            if (self.view.request.method == "POST" or self.view.request.method == "PUT" or
                    self.view.request.method == "DELETE"):
                if self.view.classResult["project_status"] == 3:
                    self.view.request.method = "GET"
                    raise HTTPForbidden("The project is closed. It is not allowed to make changes.")
