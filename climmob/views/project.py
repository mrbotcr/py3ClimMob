# -*- coding: utf-8 -*-

import datetime

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import climmob.plugins as p
from climmob.processes import (
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
    getProjectTemplates,
    getProjectAssessments,
    addEnumeratorToProject,
    addTechnologyProject,
    AddAliasTechnology,
    addTechAliasExtra,
    getAllRegistryGroups,
    addRegistryGroup,
    getQuestionsByGroupInRegistry,
    addRegistryQuestionToGroup,
    getAllAssessmentGroups,
    addProjectAssessmentClone,
    addAssessmentGroup,
    getQuestionsByGroupInAssessment,
    addAssessmentQuestionToGroup,
    getProjectEnumerators,
    searchTechnologiesInProject,
    AliasSearchTechnologyInProject,
    AliasExtraSearchTechnologyInProject,
    deleteRegistryByProjectId,
    deleteProjectAssessments,
    getUserProjects,
)
from climmob.views.classes import privateView


class getTemplatesByTypeOfProject_view(privateView):
    def processView(self):
        if self.request.method == "GET":
            typeId = self.request.matchdict["typeid"]
            templates = getProjectTemplates(self.request, typeId)
            self.returnRawViewResult = True

            return templates

        raise HTTPNotFound


class projectList_view(privateView):
    def processView(self):

        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "userProjects": getUserProjects(self.user.login, self.request),
            "sectionActive": "projectlist",
        }


class newProject_view(privateView):
    def processView(self):

        dataworking = {}
        newproject = False
        error_summary = {}
        dataworking["project_cod"] = ""
        dataworking["project_name"] = ""
        dataworking["project_abstract"] = ""
        dataworking["project_tags"] = ""
        dataworking["project_pi"] = self.user.fullName
        dataworking["project_piemail"] = self.user.email
        dataworking["project_numobs"] = 0
        dataworking["project_numcom"] = 3
        dataworking["project_regstatus"] = 0
        dataworking["project_localvariety"] = "on"
        dataworking["project_cnty"] = None
        dataworking["project_registration_and_analysis"] = 0
        dataworking["project_label_a"] = self._("Option A")
        dataworking["project_label_b"] = self._("Option B")
        dataworking["project_label_c"] = self._("Option C")
        dataworking["project_template"] = 0
        dataworking["usingTemplate"] = ""

        if self.request.method == "POST":
            if "btn_addNewProject" in self.request.POST:
                dataworking = self.getPostDict()

                continue_add = True
                message = ""
                for plugin in p.PluginImplementations(p.IProject):
                    if continue_add:
                        continue_add, message = plugin.before_adding_project(
                            self.request, self.user.login, dataworking
                        )
                if continue_add:
                    dataworking, error_summary, added = createProjectFunction(
                        dataworking, error_summary, self
                    )
                    if added:
                        for plugin in p.PluginImplementations(p.IProject):
                            plugin.after_adding_project(
                                self.request, self.user.login, dataworking
                            )
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
                else:
                    error_summary = {"plugin_error": message}

        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "indashboard": True,
            "dataworking": dataworking,
            "newproject": newproject,
            "countries": getCountryList(self.request),
            "error_summary": error_summary,
            "listOfTemplates": getProjectTemplates(
                self.request, dataworking["project_registration_and_analysis"]
            ),
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

    if "project_template" in dataworking.keys():
        if dataworking["project_template"] == "on":
            dataworking["project_template"] = 1
        else:
            dataworking["project_template"] = 0
    else:
        dataworking["project_template"] = 0

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

                        if "usingTemplate" in dataworking.keys():
                            if dataworking["usingTemplate"] != "":
                                listOfElementToInclude = ["registry"]

                                assessments = getProjectAssessments(
                                    dataworking["usingTemplate"], self.request
                                )
                                for assess in assessments:
                                    listOfElementToInclude.append(assess["ass_cod"])

                                newProjectId = getTheProjectIdForOwner(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    self.request,
                                )

                                functionCreateClone(
                                    self,
                                    dataworking["usingTemplate"],
                                    newProjectId,
                                    listOfElementToInclude,
                                )

                else:
                    error_summary = {
                        "exitsproject": self._("This project ID already exists.")
                    }
            else:
                error_summary = {
                    "repeatitem": self._(
                        "The names that the items will receive should be different."
                    )
                }
        else:
            error_summary = {"codempty": self._("The project ID can't be empty")}
    else:
        error_summary = {
            "observations": self._("The number of observations must be greater than 0.")
        }

    if int(dataworking["project_localvariety"]) == 1:
        dataworking["project_localvariety"] = "on"
    else:
        dataworking["project_localvariety"] = "off"

    return dataworking, error_summary, added


def functionCreateClone(self, projectId, newProjectId, structureToBeCloned):

    if "fieldagents" in structureToBeCloned:
        enumerators = getProjectEnumerators(
            projectId,
            self.request,
        )
        for participant in enumerators:
            for fieldAgent in enumerators[participant]:
                project_enumerator_data = {
                    "project_id": newProjectId,
                    "enum_user": fieldAgent["enum_id"],
                    "enum_id": participant,
                }
                continue_clone = True
                for plugin in p.PluginImplementations(p.ICloneProject):
                    if continue_clone:
                        continue_clone = plugin.before_cloning_enumerator(
                            self.request,
                            enumerators[participant],
                            project_enumerator_data,
                        )
                if continue_clone:
                    addEnumeratorToProject(self.request, project_enumerator_data)
                    for plugin in p.PluginImplementations(p.ICloneProject):
                        plugin.after_cloning_enumerator(
                            self.request,
                            enumerators[participant],
                            project_enumerator_data,
                        )

    if (
        "technologies" in structureToBeCloned
        or "technologyoptions" in structureToBeCloned
    ):
        techInfo = searchTechnologiesInProject(
            projectId,
            self.request,
        )
        for tech in techInfo:
            added, message = addTechnologyProject(
                newProjectId,
                tech["tech_id"],
                self.request,
            )

            if added:
                if "technologyoptions" in structureToBeCloned:

                    allAlias = AliasSearchTechnologyInProject(
                        tech["tech_id"],
                        projectId,
                        self.request,
                    )
                    for alias in allAlias:
                        data = {}
                        data["project_id"] = newProjectId
                        data["tech_id"] = tech["tech_id"]
                        data["alias_id"] = alias["alias_idTec"]
                        add, message = AddAliasTechnology(data, self.request)

                    allAliasExtra = AliasExtraSearchTechnologyInProject(
                        tech["tech_id"],
                        projectId,
                        self.request,
                    )
                    for alias in allAliasExtra:
                        data = {}
                        data["project_id"] = newProjectId
                        data["tech_id"] = tech["tech_id"]
                        data["alias_name"] = alias["alias_name"]
                        add, message = addTechAliasExtra(data, self.request)

    if "registry" in structureToBeCloned:
        groupsInRegistry = getAllRegistryGroups(
            projectId,
            self.request,
        )
        for group in groupsInRegistry:
            group["project_id"] = newProjectId
            addgroup, message = addRegistryGroup(group, self)

            if addgroup:
                questionsInRegistry = getQuestionsByGroupInRegistry(
                    projectId,
                    group["section_id"],
                    self.request,
                )
                for question in questionsInRegistry:
                    question["project_id"] = newProjectId
                    question["section_project_id"] = projectId
                    addq, message = addRegistryQuestionToGroup(question, self.request)

    assessments = getProjectAssessments(
        projectId,
        self.request,
    )
    for assessment in assessments:
        if assessment["ass_cod"] in structureToBeCloned:
            newAssessment = {}
            newAssessment["ass_desc"] = assessment["ass_desc"]
            newAssessment["ass_days"] = assessment["ass_days"]
            newAssessment["ass_final"] = assessment["ass_final"]
            newAssessment["project_id"] = newProjectId
            newAssessment["ass_status"] = 0
            added, msg = addProjectAssessmentClone(newAssessment, self.request)

            if added:
                newAssessment["ass_cod"] = msg
                data = {}
                data["project_id"] = projectId
                data["ass_cod"] = assessment["ass_cod"]
                groupsInAssessment = getAllAssessmentGroups(data, self.request)
                for group in groupsInAssessment:
                    group["project_id"] = newProjectId
                    group["ass_cod"] = newAssessment["ass_cod"]
                    addgroup, message = addAssessmentGroup(group, self)

                    if addgroup:
                        questionInAssessment = getQuestionsByGroupInAssessment(
                            projectId,
                            assessment["ass_cod"],
                            group["section_id"],
                            self.request,
                        )
                        for question in questionInAssessment:
                            question["project_id"] = newProjectId
                            question["ass_cod"] = newAssessment["ass_cod"]
                            question["section_project_id"] = newProjectId
                            question["section_assessment"] = newAssessment["ass_cod"]
                            (
                                addq,
                                message,
                            ) = addAssessmentQuestionToGroup(question, self.request)

    return ""


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

                if "project_template" in data.keys():
                    if data["project_template"] == "on":
                        data["project_template"] = 1
                    else:
                        data["project_template"] = 0
                else:
                    data["project_template"] = 0

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

                    continue_modify = True
                    message = ""
                    for plugin in p.PluginImplementations(p.IProject):
                        if continue_modify:
                            continue_modify, message = plugin.before_updating_project(
                                self.request, self.user.login, activeProjectId, data
                            )
                    if continue_modify:
                        modified, message = modifyProject(
                            activeProjectId, data, self.request
                        )
                        if not modified:
                            error_summary = {"dberror": message}
                        else:
                            for plugin in p.PluginImplementations(p.IProject):
                                plugin.after_updating_project(
                                    self.request, self.user.login, activeProjectId, data
                                )

                            if (
                                cdata["project_registration_and_analysis"] == 1
                                and data["project_registration_and_analysis"] == 0
                            ):
                                deleteRegistryByProjectId(activeProjectId, self.request)

                            if "usingTemplate" in data.keys():
                                if data["usingTemplate"] != "":
                                    deleteRegistryByProjectId(
                                        activeProjectId, self.request
                                    )
                                    deleteProjectAssessments(
                                        activeProjectId, self.request
                                    )

                                    listOfElementToInclude = ["registry"]

                                    assessments = getProjectAssessments(
                                        data["usingTemplate"], self.request
                                    )
                                    for assess in assessments:
                                        listOfElementToInclude.append(assess["ass_cod"])

                                    newProjectId = getTheProjectIdForOwner(
                                        self.user.login,
                                        data["project_cod"],
                                        self.request,
                                    )

                                    functionCreateClone(
                                        self,
                                        data["usingTemplate"],
                                        newProjectId,
                                        listOfElementToInclude,
                                    )

                            self.request.session.flash(
                                self._("The project was modified successfully")
                            )
                            self.returnRawViewResult = True
                            return HTTPFound(
                                location=self.request.route_url("dashboard")
                            )

                        if int(data["project_localvariety"]) == 1:
                            data["project_localvariety"] = "on"
                        else:
                            data["project_localvariety"] = "off"
                    else:
                        error_summary = {"dberror": message}
                else:
                    error_summary = {
                        "repeatitem": self._(
                            "The names that the items will receive should be different."
                        )
                    }
        context = {
            "activeProject": getActiveProject(self.user.login, self.request),
            "indashboard": True,
            "data": data,
            "newproject": newproject,
            "countries": getCountryList(self.request),
            "error_summary": error_summary,
            "listOfTemplates": getProjectTemplates(
                self.request, data["project_registration_and_analysis"]
            ),
        }
        for plugin in p.PluginImplementations(p.IProject):
            context = plugin.before_returning_project_context(self.request, context)
        return context


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
            continue_delete = True
            message = ""
            for plugin in p.PluginImplementations(p.IProject):
                if continue_delete:
                    continue_delete, message = plugin.before_deleting_project(
                        self.request, self.user.login, activeProjectId
                    )
            if continue_delete:
                deleted, message = deleteProject(activeProjectId, self.request)
                if not deleted:
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    for plugin in p.PluginImplementations(p.IProject):
                        if continue_delete:
                            plugin.after_deleting_project(
                                self.request, self.user.login, activeProjectId
                            )
                    self.returnRawViewResult = True
                    self.request.session.flash(
                        self._("The project was deleted successfully")
                    )
                    return {"status": 200}
            else:
                return {"status": 400, "error": message}

        return {
            "activeUser": self.user,
            "redirect": redirect,
            "data": data,
            "error_summary": error_summary,
        }
