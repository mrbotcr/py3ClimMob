from pyramid.httpexceptions import HTTPForbidden

from climmob.views.classes import privateView
from climmob.views.validators.BaseValidator import BaseValidator
from climmob.processes import get_user_access_type_in_project
from climmob.utility.project import ProjectAccessType


class ActionOnlyForProjectOwnerValidator(BaseValidator):
    def __init__(self, view):
        super().__init__(view)
        self.project_id = None
        self.extract()

    def extract(self):
        if issubclass(self.view.__class__, privateView):
            self.project_id = self.view.context.active_project_id
        else:
            raise TypeError

    def run(self):
        valid, access_type = get_user_access_type_in_project(
            self.project_id, self.view.user.login, self.view.request
        )

        if not valid or access_type not in [ProjectAccessType.OWNER.value]:
            raise HTTPForbidden("This action is forbidden")
