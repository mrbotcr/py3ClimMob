from pyramid.httpexceptions import HTTPForbidden

from climmob.utility.project import ProjectAdmin
from climmob.views.validators.BaseValidator import BaseValidator


class SectionOnlyForAdminValidator(BaseValidator):
    def run(self):

        if ProjectAdmin.YES.value != self.view.user.admin:
            raise HTTPForbidden(
                self._(
                    "The permissions you have in ClimMob do not allow you to access this section."
                )
            )


class SectionOnlyForAdminJsonValidator(BaseValidator):
    def run(self):

        if ProjectAdmin.YES.value != self.view.user.admin:

            return {
                "message": self._(
                    "The permissions you have in ClimMob do not allow you to access this section."
                ),
                "status": 403,
            }
