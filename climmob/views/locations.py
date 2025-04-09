import re

from cherrypy.lib.sessions import Session
from pattern.graph import redirect
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import validators
from pyramid.view import view_config

from climmob.processes import (
    getActiveProject,
)

from climmob.processes.db.project_location import (
    get_all_project_location,
    deleteLocationdb,
    add_Location_DB,
    editLocation,
    get_location_by_name
)

from climmob.views.classes import privateView

class crud_view(privateView):
    def processView(self):
        dataworking = {}
        error_summary = {}
        success_message = None
        error_message = None
        exist = None
        modify = False
        reportUpload = []
        nextPage = self.request.params.get("next")
        if self.request.method == "POST":
            dataworking = self.getPostDict()
            if "btn_add_location" in self.request.POST:
                modify = False
                exist = get_location_by_name(self.request, dataworking["plocation_name"])
                if not exist:
                    dataworking = add_Location_DB(dataworking, self.request)
                    success_message = "Location created successfully"
                else:
                    error_message = "There is already a record with that name, it was not created"

            if "btn_edit_location" in self.request.POST:
                modify = False
                exist = get_location_by_name(self.request, dataworking["edit_plocation_name"])
                if not exist:
                    locationid = dataworking["edit_plocation_id"]
                    dataworking = editLocation(
                        dataworking, locationid, self.request
                    )
                    success_message = "Location edited successfully"
                else:
                    error_message = "There is already a record with that name, it was not modified."
        return {
            "activeUser": self.user,
            "activeProject": getActiveProject(self.user.login, self.request),
            "searchAllProyectLocation": get_all_project_location(self.request),
            "nextPage": nextPage,
            "modify": modify,
            "reportUpload": reportUpload,
            "error_summary": error_summary,
            "error_message": error_message,
            "dataworking": dataworking,
            'success_message': success_message
        }

class deleteLocation_view(privateView):
    def processView(self):
        locationid = self.request.matchdict["locationid"]
        if self.request.method == "POST":
            deleted= deleteLocationdb(locationid, self.request)
            if not deleted:
                self.returnRawViewResult = True

                return {"status": 400}
            else:
                self.request.session.flash(
                    self._("The location was successfully removed")
                )
                self.returnRawViewResult = True
                return {"status": 200}
        else:
            self.returnRawViewResult = True
            return {"status": 400 }
