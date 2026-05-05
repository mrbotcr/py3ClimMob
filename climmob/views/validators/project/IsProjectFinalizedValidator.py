from pyramid.httpexceptions import HTTPNotFound

from climmob.processes import get_project_status
from climmob.utility.project import ProjectStatus
from climmob.views.validators.BaseValidator import BaseValidator


class IsProjectFinalizedValidator(BaseValidator):
    def run(self):
        active_project_id = self.view.context.active_project_id

        status = get_project_status(active_project_id, self.view.request)

        if status != ProjectStatus.FINALIZED:
            raise HTTPNotFound(
                self._("Project must be finalized in order to publish it")
            )
