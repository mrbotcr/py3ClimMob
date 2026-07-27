from pyramid.httpexceptions import HTTPNotFound

from climmob.processes import is_publication_allowed
from climmob.views.validators.BaseValidator import BaseValidator


class ProjectPublicationAllowedValidator(BaseValidator):
    def run(self):
        project_id = self.view.context.active_project_id

        allowed = is_publication_allowed(project_id, self.view.request)

        if not allowed:
            raise HTTPNotFound(
                self._(
                    "The access assigned for this project does not allow you to get the collected data."
                )
            )
