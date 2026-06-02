from pyramid.httpexceptions import HTTPForbidden

from climmob.views.validators.BaseValidator import BaseValidator


class HasAccessToProjectValidator(BaseValidator):
    def run(self):
        access_type = self.view.context.access_type

        if access_type is None:
            raise HTTPForbidden(
                self._(
                    "The access assigned for this project does not allow you to get the collected data."
                )
            )
