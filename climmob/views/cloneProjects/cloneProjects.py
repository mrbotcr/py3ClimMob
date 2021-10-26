from ..classes import privateView
from ...processes import (
    getUserProjects,
    getProjectEnumerators,
    searchTechnologiesInProject,
    getProjectData,
    getProjectAssessments,
    getCountryList,
    AliasSearchTechnologyInProject,
    addEnumeratorToProject,
    addTechnologyProject,
    AddAliasTechnology,
    AliasExtraSearchTechnologyInProject,
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
    projectExists,
    getActiveProject,
    getTheProjectIdForOwner,
)
from ..project import createProjectFunction
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from ..registry import getDataFormPreview


class cloneProjects_view(privateView):
    def processView(self):

        dataworking = {}
        showForm = False
        error_summary = {}
        projectCod = ""
        userOwner = ""
        projectId = ""

        if not "stage" in self.request.params.keys():
            stage = 1
        else:
            try:
                stage = int(self.request.params["stage"])
            except:
                stage = 1

        if stage < 1 or stage > 4:
            raise HTTPNotFound()

        try:
            projectCod = self.request.params["project"]
            userOwner = self.request.params["user"]

            if not projectExists(self.user.login, userOwner, projectCod, self.request):
                raise HTTPNotFound()

            projectId = getTheProjectIdForOwner(userOwner, projectCod, self.request)
        except:
            if stage != 1:
                raise HTTPNotFound()

        if stage == 1:
            if self.request.method == "POST":
                dataworking = self.getPostDict()
                self.returnRawViewResult = True
                data = dataworking["slt_project_by_owner"].split("___")
                return HTTPFound(
                    location=self.request.route_url(
                        "cloneProject",
                        _query={"stage": 2, "project": data[1], "user": data[0]},
                    )
                )
            else:
                dataworking["slt_project_by_owner"] = ""

                if projectCod != "":
                    dataworking["slt_project_by_owner"] = userOwner + "___" + projectCod

                return {
                    "activeProject": getActiveProject(self.user.login, self.request),
                    "dataworking": dataworking,
                    "projects": getUserProjects(self.user.login, self.request),
                    "stage": stage,
                }

        if stage == 2:
            dataworking["slt_project_by_owner"] = userOwner + "___" + projectCod

            dataworking["projectBeingCloned"] = getAllInformationForProject(
                self, userOwner, projectId
            )

            return {
                "activeProject": getActiveProject(self.user.login, self.request),
                "dataworking": dataworking,
                "projects": getUserProjects(self.user.login, self.request),
                "stage": stage,
            }

        if stage == 3:

            dataworking["slt_project_by_owner"] = userOwner + "___" + projectCod

            if self.request.method == "POST":
                dataworking = self.getPostDict()

                if "btn_addNewProject" in self.request.POST:

                    dataworking, error_summary, added = createProjectFunction(
                        dataworking, error_summary, self
                    )
                    if added:

                        newProjectId = getTheProjectIdForOwner(
                            self.user.login, dataworking["project_cod"], self.request
                        )

                        ok = functionCreateClone(
                            self,
                            projectId,
                            newProjectId,
                            dataworking["structureToBeCloned"].split(","),
                        )

                        if not error_summary:
                            #     stage = 4
                            self.returnRawViewResult = True
                            return HTTPFound(
                                location=self.request.route_url(
                                    "cloneProject",
                                    _query={
                                        "stage": 4,
                                        "project": projectCod,
                                        "user": userOwner,
                                        "cloned": dataworking["project_cod"],
                                    },
                                )
                            )

            if not error_summary:
                dataworking["project_numobs"] = 0
                dataworking["project_numcom"] = 3
                dataworking["project_regstatus"] = 0
                dataworking["project_registration_and_analysis"] = 0

            return {
                "activeProject": getActiveProject(self.user.login, self.request),
                "dataworking": dataworking,
                "projects": getUserProjects(self.user.login, self.request),
                "countries": getCountryList(self.request),
                "assessments": getProjectAssessments(projectId, self.request),
                "showForm": showForm,
                "error_summary": error_summary,
                "stage": stage,
            }

        if stage == 4:
            dataworking["slt_project_by_owner"] = userOwner + "___" + projectCod

            try:
                cloned = self.request.params["cloned"]
                dataworking["project_cod"] = cloned
                dataworking["userInSetion"] = self.user.login
                if not projectExists(
                    self.user.login, self.user.login, cloned, self.request
                ):
                    raise HTTPNotFound()
            except:
                raise HTTPNotFound()

            dataworking["clonedProject"] = getAllInformationForProject(
                self, userOwner, projectId
            )

            newProjectId = getTheProjectIdForOwner(
                self.user.login, cloned, self.request
            )

            dataworking["projectBeingCloned"] = getAllInformationForProject(
                self, self.user.login, newProjectId
            )

            return {
                "activeProject": getActiveProject(self.user.login, self.request),
                "dataworking": dataworking,
                "stage": 4,
            }


def functionCreateClone(self, projectId, newProjectId, structureToBeCloned):

    if "fieldagents" in structureToBeCloned:
        enumerators = getProjectEnumerators(projectId, self.request,)
        for participant in enumerators:
            for fieldAgent in enumerators[participant]:
                addEnumeratorToProject(
                    newProjectId, fieldAgent["enum_id"], participant, self.request
                )

    if (
        "technologies" in structureToBeCloned
        or "technologyoptions" in structureToBeCloned
    ):
        techInfo = searchTechnologiesInProject(projectId, self.request,)
        for tech in techInfo:
            added, message = addTechnologyProject(
                newProjectId, tech["tech_id"], self.request,
            )

            if added:
                if "technologyoptions" in structureToBeCloned:

                    allAlias = AliasSearchTechnologyInProject(
                        tech["tech_id"], projectId, self.request,
                    )
                    for alias in allAlias:
                        data = {}
                        data["project_id"] = newProjectId
                        data["tech_id"] = tech["tech_id"]
                        data["alias_id"] = alias["alias_idTec"]
                        add, message = AddAliasTechnology(data, self.request)

                    allAliasExtra = AliasExtraSearchTechnologyInProject(
                        tech["tech_id"], projectId, self.request,
                    )
                    for alias in allAliasExtra:
                        data = {}
                        data["project_id"] = newProjectId
                        data["tech_id"] = tech["tech_id"]
                        data["alias_name"] = alias["alias_name"]
                        add, message = addTechAliasExtra(data, self.request)

    if "registry" in structureToBeCloned:
        groupsInRegistry = getAllRegistryGroups(projectId, self.request,)
        for group in groupsInRegistry:
            group["project_id"] = newProjectId
            addgroup, message = addRegistryGroup(group, self)

            if addgroup:
                questionsInRegistry = getQuestionsByGroupInRegistry(
                    projectId, group["section_id"], self.request,
                )
                for question in questionsInRegistry:
                    question["project_id"] = newProjectId
                    question["section_project_id"] = projectId
                    addq, message = addRegistryQuestionToGroup(question, self.request)

    assessments = getProjectAssessments(projectId, self.request,)
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
                            (addq, message,) = addAssessmentQuestionToGroup(
                                question, self.request
                            )

    return ""


def getAllInformationForProject(self, userOwner, projectId):

    dataworking = getProjectData(projectId, self.request)

    dataworking["project_registration_and_analysis"] = dataworking[
        "project_registration_and_analysis"
    ]

    dataworking["project_fieldagents"] = getProjectEnumerators(projectId, self.request)

    techInfo = searchTechnologiesInProject(projectId, self.request)
    for tech in techInfo:
        tech["alias"] = AliasSearchTechnologyInProject(
            tech["tech_id"], projectId, self.request,
        )
        tech["aliasExtra"] = AliasExtraSearchTechnologyInProject(
            tech["tech_id"], projectId, self.request
        )
    dataworking["project_techs"] = techInfo

    dataRegistry, finalCloseQst = getDataFormPreview(
        self, userOwner, projectId, createAutoRegistry=False
    )

    dataworking["project_registry"] = dataRegistry
    dataAssessments = getProjectAssessments(projectId, self.request)
    for assessment in dataAssessments:
        dataAssessmentsQuestions, finalCloseQst = getDataFormPreview(
            self, userOwner, projectId, assessment["ass_cod"]
        )
        assessment["Questions"] = dataAssessmentsQuestions
    dataworking["project_assessment"] = dataAssessments

    return dataworking
