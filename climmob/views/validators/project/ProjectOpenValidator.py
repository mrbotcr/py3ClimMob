from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPForbidden
import json
from climmob.processes import get_project_status, getTheProjectIdForOwner
from climmob.utility.project import ProjectStatus
from climmob.views.classes import privateView, apiView
from climmob.views.validators.BaseValidator import BaseValidator


class ProjectOpenValidator(BaseValidator):
    def __init__(self, view):
        super().__init__(view)
        self.request = None

    def run(self):
        if issubclass(self.view.__class__, privateView):
            if (
                self.view.request.method in {"POST", "PUT", "DELETE"}
            ) and self.view.classResult[
                "project_status"
            ] == ProjectStatus.FINALIZED.value:
                current_view = self.view.__class__.__name__
                post_data = self.view.getPostDict()
                for view_class, button in self.routes_of_exceptions():
                    if current_view == view_class:
                        for key, value in post_data.items():
                            if key == button and value == "":
                                return
                self.view.request.method = "GET"
                raise HTTPForbidden(
                    self._("The project is closed. It is not allowed to make changes.")
                )
        elif issubclass(self.view.__class__, apiView):
            if self.view.request.method in {"POST", "PUT", "DELETE"}:
                body = json.loads(self.view.request.POST.get("Body"))
                project_cod = body["project_cod"]
                user_owner = self.view.user.login  ##(it comes from apikey)
                project_id = getTheProjectIdForOwner(
                    user_owner, project_cod, self.view.request
                )
                project_status = get_project_status(project_id, self.view.request)
                if project_status == ProjectStatus.FINALIZED.value:
                    raise HTTPForbidden(
                        self._(
                            "The project is closed. It is not allowed to make changes."
                        )
                    )

    """this function excepts some routes with the method and the button of trigger, to allow show all the info of the project"""
    """exceptions form : (View, button)"""

    def routes_of_exceptions(self):
        return [
            ("ProjectTechnologiesView", "btn_show_technology_alias"),
            ("EditDataView", "btn_EditData"),
        ]
