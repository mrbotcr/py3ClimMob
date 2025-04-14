from pyramid.httpexceptions import HTTPNotFound

from climmob.processes import projectExists
from climmob.views.validators.BaseValidator import BaseValidator


class ProjectExistsValidator(BaseValidator):
    def run(self):
        project_owner_username = self.view.request.matchdict["user"]
        project_cod = self.view.request.matchdict["project"]

        if not projectExists(
            self.view.user.login, project_owner_username, project_cod, self.view.request
        ):
            raise HTTPNotFound()
