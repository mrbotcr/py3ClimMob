from climmob.processes import getTheProjectIdForOwner
from climmob.views.context.BaseContext import BaseContext


class PrivateContext(BaseContext):
    def __init__(self, request):
        super().__init__(request)
        self._active_project_id = None

    @property
    def active_project_id(self):
        if not self._active_project_id:
            active_project_user = self.request.matchdict["user"]
            active_project_cod = self.request.matchdict["project"]
            self._active_project_id = getTheProjectIdForOwner(
                active_project_user, active_project_cod, self.request
            )
        return self._active_project_id
