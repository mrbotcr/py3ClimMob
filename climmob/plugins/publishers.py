from pyutilib.component.core import implements

from climmob.plugins import SingletonPlugin, IPublisher
from climmob.processes import get_project_by_id
from climmob.products.genesysResults import create_genesys_results_task
from climmob.products.jsonResults import create_report_json_results


class ClimMobPublisher(SingletonPlugin):
    implements(IPublisher)
    destination_name = "climmob"
    label = "ClimMob"
    disabled = True
    index = 0

    def get_destination_name(self):
        return self.destination_name

    def get_label(self):
        return self.label

    def publish(self, settings, request, path, project_id, crop_name):
        print(
            f"ClimmobPublisher: Publishing project {project_id} to {self.get_destination_name()} from {path}"
        )
        success, msg = create_report_json_results(
            None,
            "userOwner",
            project_id,
            "projectCod",
            crop_name,
            path,
        )
        return success, msg


class GenesysPublisher(SingletonPlugin):
    implements(IPublisher)
    destination_name = "genesys"
    label = "Genesys"
    disabled = False
    index = 3

    def get_destination_name(self):
        return self.destination_name

    def get_label(self):
        return self.label

    def publish(self, settings, request, path, project_id, crop_name):
        print(
            f"GenesysPublisher: Publishing project {project_id} to {self.get_destination_name()} from {path}"
        )
        request_attrs = {
            "settings": settings,
            "locale_name": request.locale_name,
            "user_in_session": request.user_in_session,
        }
        project = get_project_by_id(project_id, request)

        create_genesys_results_task(request_attrs, project)
        return True, ""
