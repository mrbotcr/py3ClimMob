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
    getListOfLanguagesByUser,
    addPrjLang,
    deleteAllPrjLang,
    getTotalNumberOfProjectsInClimMob,
    getProjectsByUserThatRequireSetup,
    getListOfProjectTypes,
    get_all_project_location,
    get_all_unit_of_analysis_by_location,
    get_all_objectives_by_location_and_unit_of_analysis,
    add_project_location_unit_objective,
    get_location_unit_of_analysis_by_combination,
    get_location_unit_of_analysis_objectives_by_combination,
    delete_all_project_location_unit_objective,
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
            "numberOfProjects": getTotalNumberOfProjectsInClimMob(self.request),
        }


class newProject_view(privateView):
    def processView(self):

        if self.request.registry.settings.get("projects.limit", "false") == "true":
            if getTotalNumberOfProjectsInClimMob(self.request) >= int(
                self.request.registry.settings.get("projects.quantity", 0)
            ):
                raise HTTPNotFound()

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
        dataworking["project_location"] = "-1"
        dataworking["project_unit_of_analysis"] = "-1"

        if self.request.method == "POST":
            if "btn_addNewProject" in self.request.POST:
                dataworking = self.getPostDict()

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
            "listOfLanguages": getListOfLanguagesByUser(self.request, self.user.login),
            "listOfLocations": get_all_project_location(self.request),
            "listOfUnitOfAnalysis": get_all_unit_of_analysis_by_location(
                self.request, dataworking["project_location"]
            ),
            "listOfObjectives": get_all_objectives_by_location_and_unit_of_analysis(
                self.request,
                dataworking["project_location"],
                dataworking["project_unit_of_analysis"],
            ),
        }


def createProjectFunction(dataworking, error_summary, self):
    added = False
    dataworking["user_name"] = self.user.login
    dataworking["project_regstatus"] = 0
    dataworking["project_lat"] = ""
    dataworking["project_lon"] = ""

    dataworking["project_localvariety"] = 1

    if "project_template" in dataworking.keys():
        if dataworking["project_template"] == "on":
            dataworking["project_template"] = 1
        else:
            dataworking["project_template"] = 0
    else:
        dataworking["project_template"] = 0

    if "project_type" in dataworking.keys() and dataworking["project_type"] == "on":
        dataworking["project_type"] = 2
    else:
        dataworking["project_type"] = 1

    continue_add = True

    for plugin in p.PluginImplementations(p.IProject):
        if continue_add:
            continue_add, message, dataworking = plugin.before_adding_project(
                self.request, self.user.login, dataworking
            )

            if not continue_add:
                error_summary = {"error": message}
                added = False

    if self.request.registry.settings.get("projects.limit", "false") == "true":
        if int(
            self.request.registry.settings.get("project.maximumnumberofobservations", 0)
        ) < int(dataworking["project_numobs"]):
            error_summary = {
                "projectslimits": self._(
                    "This project does not comply with the limitations on the number of participants per project."
                )
            }

            return dataworking, error_summary, added

    if continue_add:
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

                    location_unit_of_analysis = (
                        get_location_unit_of_analysis_by_combination(
                            self.request,
                            dataworking["project_location"],
                            dataworking["project_unit_of_analysis"],
                        )
                    )

                    dataworking[
                        "project_registration_and_analysis"
                    ] = location_unit_of_analysis["registration_and_analysis"]

                    if not exitsproject:
                        added, idormessage = addProject(dataworking, self.request)
                        if not added:
                            error_summary = {"dberror": idormessage}
                        else:
                            addToLog(
                                self.user.login,
                                "PRF",
                                "Created a new project",
                                datetime.datetime.now(),
                                self.request,
                            )

                            if isinstance(dataworking["project_objectives"], str):
                                dataworking["project_objectives"] = [
                                    dataworking["project_objectives"]
                                ]

                            for objective in dataworking["project_objectives"]:
                                luoao_id = get_location_unit_of_analysis_objectives_by_combination(
                                    self.request,
                                    location_unit_of_analysis["pluoa_id"],
                                    objective,
                                )[
                                    "pluoaobj_id"
                                ]

                                infoObj = {
                                    "project_id": idormessage,
                                    "pluoaobj_id": luoao_id,
                                }
                                add_project_location_unit_objective(
                                    infoObj, self.request
                                )

                            if "project_languages" in dataworking.keys():
                                if dataworking["project_languages"]:

                                    if isinstance(
                                        dataworking["project_languages"], str
                                    ):
                                        dataworking["project_languages"] = [
                                            dataworking["project_languages"]
                                        ]

                                    for index, lang in enumerate(
                                        dataworking["project_languages"]
                                    ):
                                        langInfo = {}
                                        if index == 0:
                                            langInfo["lang_default"] = 1

                                        langInfo["lang_code"] = lang
                                        langInfo["project_id"] = idormessage

                                        apl, aplmessage = addPrjLang(
                                            langInfo, self.request
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
                "observations": self._(
                    "The number of observations must be greater than 0."
                )
            }

    if int(dataworking["project_localvariety"]) == 1:
        dataworking["project_localvariety"] = "on"
    else:
        dataworking["project_localvariety"] = "off"

    if int(dataworking["project_type"]) == 2:
        dataworking["project_type"] = "on"
    else:
        dataworking["project_type"] = "off"

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
                    "enum_user": participant,
                    "enum_id": fieldAgent["enum_id"],
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

                if "project_type" in data.keys() and data["project_type"] == "on":
                    data["project_type"] = 2
                else:
                    data["project_type"] = 1

                data["project_regstatus"] = cdata["project_regstatus"]

                data["project_cod"] = activeProjectCod

                if (
                    self.request.registry.settings.get("projects.limit", "false")
                    == "true"
                ):
                    if int(
                        self.request.registry.settings.get(
                            "project.maximumnumberofobservations", 0
                        )
                    ) < int(data["project_numobs"]):
                        error_summary = {
                            "projectslimits": self._(
                                "This project does not comply with the limitations on the number of participants per project."
                            )
                        }

                if not error_summary:
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
                                (
                                    continue_modify,
                                    message,
                                    data,
                                ) = plugin.before_updating_project(
                                    self.request, self.user.login, activeProjectId, data
                                )
                        if continue_modify:

                            location_unit_of_analysis = (
                                get_location_unit_of_analysis_by_combination(
                                    self.request,
                                    data["project_location"],
                                    data["project_unit_of_analysis"],
                                )
                            )
                            data[
                                "project_registration_and_analysis"
                            ] = location_unit_of_analysis["registration_and_analysis"]

                            modified, message = modifyProject(
                                activeProjectId, data, self.request
                            )
                            if not modified:
                                error_summary = {"dberror": message}
                            else:

                                (
                                    deleted,
                                    message,
                                ) = delete_all_project_location_unit_objective(
                                    activeProjectId, self.request
                                )

                                if isinstance(data["project_objectives"], str):
                                    data["project_objectives"] = [
                                        data["project_objectives"]
                                    ]

                                for objective in data["project_objectives"]:
                                    luoao_id = get_location_unit_of_analysis_objectives_by_combination(
                                        self.request,
                                        location_unit_of_analysis["pluoa_id"],
                                        objective,
                                    )[
                                        "pluoaobj_id"
                                    ]

                                    infoObj = {
                                        "project_id": activeProjectId,
                                        "pluoaobj_id": luoao_id,
                                    }
                                    add_project_location_unit_objective(
                                        infoObj, self.request
                                    )

                                deleted, message = deleteAllPrjLang(
                                    activeProjectId, self.request
                                )

                                if "project_languages" in data.keys():
                                    if data["project_languages"]:

                                        if isinstance(data["project_languages"], str):
                                            data["project_languages"] = [
                                                data["project_languages"]
                                            ]

                                        for index, lang in enumerate(
                                            data["project_languages"]
                                        ):
                                            langInfo = {}
                                            if index == 0:
                                                langInfo["lang_default"] = 1

                                            langInfo["lang_code"] = lang
                                            langInfo["project_id"] = activeProjectId

                                            apl, aplmessage = addPrjLang(
                                                langInfo, self.request
                                            )

                                for plugin in p.PluginImplementations(p.IProject):
                                    plugin.after_updating_project(
                                        self.request,
                                        self.user.login,
                                        activeProjectId,
                                        data,
                                    )

                                if (
                                    cdata["project_registration_and_analysis"] == 1
                                    and data["project_registration_and_analysis"] == 0
                                ):
                                    deleteRegistryByProjectId(
                                        activeProjectId, self.request
                                    )

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
                                            listOfElementToInclude.append(
                                                assess["ass_cod"]
                                            )

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
            "listOfLanguages": getListOfLanguagesByUser(self.request, self.user.login),
            "listOfLocations": get_all_project_location(self.request),
            "listOfUnitOfAnalysis": get_all_unit_of_analysis_by_location(
                self.request, data["project_location"]
            ),
            "listOfObjectives": get_all_objectives_by_location_and_unit_of_analysis(
                self.request, data["project_location"], data["project_unit_of_analysis"]
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


class CurationOfProjects_view(privateView):
    def processView(self):
        error_summary = {}

        if self.request.method == "POST":

            if "btn_save_projects" in self.request.POST:
                formdata = self.getPostDict()
                listOfProject = {}

                for key in formdata.keys():
                    if key not in ["csrf_token", "btn_save_projects"]:

                        keyDetails = key.split("_")

                        if keyDetails[1] == "status":
                            value = 3
                        else:
                            value = formdata[key]

                        if keyDetails[-1] not in listOfProject.keys():
                            listOfProject[keyDetails[-1]] = {}

                        listOfProject[keyDetails[-1]][
                            key.replace("_" + keyDetails[-1], "")
                        ] = value

                for key in listOfProject.keys():
                    if (
                        all(listOfProject[key].values())
                        or listOfProject[key]["project_type"] == "2"
                    ):

                        listOfProject[key] = {
                            k: v for k, v in listOfProject[key].items() if v
                        }

                        updated, message = modifyProject(
                            key, listOfProject[key], self.request
                        )

                        if "project_objectives" in listOfProject[key].keys():
                            (
                                deleted,
                                message,
                            ) = delete_all_project_location_unit_objective(
                                key, self.request
                            )

                            if isinstance(
                                listOfProject[key]["project_objectives"], str
                            ):
                                listOfProject[key]["project_objectives"] = [
                                    listOfProject[key]["project_objectives"]
                                ]

                            for objective in listOfProject[key]["project_objectives"]:
                                location_unit_of_analysis = (
                                    get_location_unit_of_analysis_by_combination(
                                        self.request,
                                        listOfProject[key]["project_location"],
                                        listOfProject[key]["project_unit_of_analysis"],
                                    )
                                )

                                luoao_id = get_location_unit_of_analysis_objectives_by_combination(
                                    self.request,
                                    location_unit_of_analysis["pluoa_id"],
                                    objective,
                                )[
                                    "pluoaobj_id"
                                ]

                                infoObj = {
                                    "project_id": key,
                                    "pluoaobj_id": luoao_id,
                                }
                                add_project_location_unit_objective(
                                    infoObj, self.request
                                )

        completed, projects = getProjectsByUserThatRequireSetup(
            self.user.login, self.request
        )

        if completed:
            self.returnRawViewResult = True
            return HTTPFound(location=self.request.route_url("dashboard"))

        return {
            "listOfProjects": projects,
            "listOfProjectTypes": getListOfProjectTypes(self.request),
            "listOfLocations": get_all_project_location(self.request),
            "error_summary": error_summary,
        }


class GetUnitOfAnalysisByLocationView(privateView):
    def processView(self):
        self.returnRawViewResult = True
        if self.request.method == "GET":
            location_id = self.request.matchdict["locationid"]
            unit_of_analysis = get_all_unit_of_analysis_by_location(
                self.request, location_id
            )

            return unit_of_analysis

        return {}


class GetObjectivesByLocationAndUnitOfAnalysisView(privateView):
    def processView(self):
        self.returnRawViewResult = True
        if self.request.method == "GET":
            location_id = self.request.matchdict["locationid"]
            unit_of_analysis = self.request.matchdict["unitofanalysisid"]
            objectives = get_all_objectives_by_location_and_unit_of_analysis(
                self.request, location_id, unit_of_analysis
            )

            return objectives

        return {}
