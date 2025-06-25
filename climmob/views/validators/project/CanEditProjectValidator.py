from pyramid.httpexceptions import HTTPForbidden

from climmob.processes import getAccessTypeForProject
from climmob.views.validators.BaseValidator import BaseValidator


class CanEditProjectValidator(BaseValidator):
    def run(self):
        access_type = getAccessTypeForProject(
            self.view.user.login, self.view.context.active_project_id, self.view.request
        )

        if access_type == 4:
            raise HTTPForbidden(
                self._(
                    "The access assigned for this project does not allow you to clone assessments."
                )
            )
