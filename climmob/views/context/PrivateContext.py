from functools import cached_property

from climmob.processes import getTheProjectIdForOwner
from climmob.views.context.BaseContext import BaseContext


class PrivateContext(BaseContext):
    @cached_property
    def active_project_id(self):
        active_project_user = self.request.user
        active_project_cod = self.request.project
        active_project_id = getTheProjectIdForOwner(
            active_project_user, active_project_cod, self.request
        )
        return active_project_id
