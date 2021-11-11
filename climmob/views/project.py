# -*- coding: utf-8 -*-

from .classes import privateView
from ..processes import (
    projectInDatabase,
    addProject,
    getProjectData,
    modifyProject,
    projectExists,
    deleteProject,
    changeTheStateOfCreateComb,
    getCountryList,
    getTheProjectIdForOwner,
    addToLog,
    getActiveProject,
)
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import datetime


class newProject_view(privateView):
    def processView(self):

        dataworking = {}
        newproject = False
        error_summary = {}
        dataworking["project_cod"] = ""
        dataworking["project_name"] = ""
        dataworking["project_abstract"] = ""
        dataworking["project_tags"] = ""
        dataworking["project_pi"] = ""
        dataworking["project_piemail"] = ""
        dataworking["project_numobs"] = 0
        dataworking["project_numcom"] = 3
        dataworking["project_regstatus"] = 0
        dataworking["project_localvariety"] = "on"
        dataworking["project_cnty"] = None
        dataworking["project_registration_and_analysis"] = 0
        dataworking["project_label_a"] = self._("Option A")
        dataworking["project_label_b"] = self._("Option B")
        dataworking["project_label_c"] = self._("Option C")

        if self.request.method == "POST":
            if "btn_addNewProject" in self.request.POST:

                dataworking = self.getPostDict()

                dataworking, error_summary, added = createProjectFunction(
                    dataworking, error_summary, self
                )
                if added:
                    self.request.session.flash(
                        self._("The project was created successfully")
                    )
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "dashboard",
                            _query={
                                "user": self.user.login,
                                "project": dataworking["project_cod"],
                            },
                        )
                    )

        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "indashboard": True,
            "dataworking": dataworking,
            "newproject": newproject,
            "countries": getCountryList(self.request),
            "error_summary": error_summary,
        }


def createProjectFunction(dataworking, error_summary, self):
    added = False
    dataworking["user_name"] = self.user.login
    dataworking["project_regstatus"] = 0
    dataworking["project_lat"] = ""
    dataworking["project_lon"] = ""

    dataworking["project_registration_and_analysis"] = int(
        dataworking["project_registration_and_analysis"]
    )

    dataworking["project_localvariety"] = 1

    if int(dataworking["project_numobs"]) > 0:
        if dataworking["project_cod"] != "":
            if (
                dataworking["project_label_a"] != dataworking["project_label_b"]
                and dataworking["project_label_a"] != dataworking["project_label_c"]
                and dataworking["project_label_b"] != dataworking["project_label_c"]
            ):
                exitsproject = projectInDatabase(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if not exitsproject:
                    added, message = addProject(dataworking, self.request)
                    if not added:
                        error_summary = {"dberror": message}
                    else:
                        addToLog(
                            self.user.login,
                            "PRF",
                            "Created a new project",
                            datetime.datetime.now(),
                            self.request,
                        )

                else:
                    error_summary = {
                        "exitsproject": self._(
                            "A project already exists with this code."
                        )
                    }
            else:
                error_summary = {
                    "repeatitem": self._(
                        "The names that the items will receive should be different."
                    )
                }
        else:
            error_summary = {"codempty": self._("The project code can't be empty")}
    else:
        error_summary = {
            "observations": self._("The number of observations must be greater than 0.")
        }

    if int(dataworking["project_localvariety"]) == 1:
        dataworking["project_localvariety"] = "on"
    else:
        dataworking["project_localvariety"] = "off"

    return dataworking, error_summary, added


class modifyProject_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )

        newproject = False
        error_summary = {}
        data = getProjectData(activeProjectId, self.request)

        if int(data["project_localvariety"]) == 1:
            data["project_localvariety"] = "on"
        else:
            data["project_localvariety"] = "off"

        if self.request.method == "POST":
            if "btn_addNewProject" in self.request.POST:
                # get the field value

                cdata = getProjectData(activeProjectId, self.request)
                data = self.getPostDict()

                data["project_regstatus"] = cdata["project_regstatus"]

                data["project_cod"] = activeProjectCod

                data["project_registration_and_analysis"] = int(
                    data["project_registration_and_analysis"]
                )

                if (
                    data["project_label_a"] != data["project_label_b"]
                    and data["project_label_a"] != data["project_label_c"]
                    and data["project_label_b"] != data["project_label_c"]
                ):

                    if cdata["project_regstatus"] != 0:
                        data["project_numobs"] = cdata["project_numobs"]
                        data["project_numcom"] = cdata["project_numcom"]



                    data["project_localvariety"] = 1

                    isNecessarygenerateCombinations = False
                    if int(data["project_numobs"]) != int(cdata["project_numobs"]):
                        isNecessarygenerateCombinations = True

                    if int(data["project_numcom"]) != int(cdata["project_numcom"]):
                        isNecessarygenerateCombinations = True

                    if isNecessarygenerateCombinations:
                        changeTheStateOfCreateComb(activeProjectId, self.request)

                    modified, message = modifyProject(activeProjectId, data, self.request)
                    if not modified:
                        error_summary = {"dberror": message}
                    else:
                        self.request.session.flash(
                            self._("The project was modified successfully")
                        )
                        self.returnRawViewResult = True
                        return HTTPFound(location=self.request.route_url("dashboard"))

                    if int(data["project_localvariety"]) == 1:
                        data["project_localvariety"] = "on"
                    else:
                        data["project_localvariety"] = "off"
                else:
                    error_summary = {"repeatitem": self._(
                        "The names that the items will receive should be different."
                    )}
        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "indashboard": True,
            "data": data,
            "newproject": newproject,
            "countries": getCountryList(self.request),
            "error_summary": error_summary,
        }


class deleteProject_view(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )
        redirect = False
        error_summary = {}
        data = getProjectData(activeProjectId, self.request)
        if self.request.method == "POST":
            deleted, message = deleteProject(activeProjectId, self.request)
            if not deleted:
                error_summary = {"dberror": message}
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
            else:
                self.returnRawViewResult = True
                self.request.session.flash(
                    self._("The project was deleted successfully")
                )
                return {"status": 200}

        return {
            "activeUser": self.user,
            "redirect": redirect,
            "data": data,
            "error_summary": error_summary,
        }
