# TODO Move file to validators/project
import json

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from climmob.processes import projectExists
from climmob.views.classes import privateView, apiView
from climmob.views.validators.BaseValidator import BaseValidator


class ProjectExistsValidator(BaseValidator):
    def __init__(self, view):
        super().__init__(view)
        self.project_owner_username = None
        self.project_cod = None
        self.extract()
        self.is_project_close()

    def extract(self):

        if issubclass(self.view.__class__, privateView):
            self.project_owner_username = self.view.request.user
            self.project_cod = self.view.request.project

        elif issubclass(self.view.__class__, apiView):
            body = json.loads(self.view.body)
            self.project_owner_username = body["user_owner"]
            self.project_cod = body["project_cod"]

        else:
            raise TypeError

    def run(self):

        if not projectExists(
            self.view.user.login,
            self.project_owner_username,
            self.project_cod,
            self.view.request,
        ):
            raise HTTPNotFound(self._("There is no a project with that code."))

    def is_project_close(self):
        if (self.view.request.method == "POST" or self.view.request.method == "PUT" or
                self.view.request.method == "DELETE"):
            if self.view.classResult["project_status"] == 3:
                self.view.request.method = "GET"
                raise HTTPForbidden("The project is closed. It is not allowed to make changes.")