from pyramid.httpexceptions import HTTPForbidden

from climmob.utility.project import ProjectAccessType
from climmob.views.validators.BaseValidator import BaseValidator


class IsProjectOwnerValidator(BaseValidator):
    def run(self):
        access_type = self.view.context.access_type

        if access_type != ProjectAccessType.OWNER.value:
            raise HTTPForbidden(
                self._(
                    "The access assigned for this project does not allow you to publish data."
                )
            )
