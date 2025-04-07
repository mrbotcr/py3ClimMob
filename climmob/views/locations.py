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
import climmob.plugins as p


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
        print(self.getPostDict())
        if self.request.method == "POST":
            dataworking = self.getPostDict()
            if "btn_add_location" in self.request.POST:
                modify = False
                exist = get_location_by_name(self.request, dataworking["plocation_name"])
                if not exist:
                    dataworking, error_summary = functionForAddLocations(
                        self, dataworking, error_summary
                    )
                    success_message = "Location created successfully"
                else:

                    error_message = "There is already a record with that name, it was not created"

            if "btn_edit_location" in self.request.POST:
                modify = False
                exist = get_location_by_name(self.request, dataworking["edit_plocation_name"])
                if not exist:
                    locationid = dataworking["edit_plocation_id"]
                    dataworking, error_summary = editLocation(
                        dataworking, locationid, error_summary, self.request
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


def functionForAddLocations(self, dataworking, error_summary, showMessage=True):
    added, message = add_Location_DB(dataworking, self.request)
    if not added:
        error_summary = {"error": message}
    else:
        dataworking = {}
        if showMessage:
            self.request.session.flash(self._("The location was created successfully."))
    return dataworking, error_summary


class deleteLocation_view(privateView):
    def processView(self):
        locationid = self.request.matchdict["locationid"]

        if self.request.method == "POST":
            continue_delete = True
            message = ""

            if continue_delete:
                deleted, message = deleteLocationdb(locationid, self.request)
                if not deleted:
                    self.returnRawViewResult = True

                    return {"status": 400, "error": message}
                else:
                    self.request.session.flash(
                        self._("The location was successfully removed")
                    )
                    self.returnRawViewResult = True
                    return {"status": 200}
            else:
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
