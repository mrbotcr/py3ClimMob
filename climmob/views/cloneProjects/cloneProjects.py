from ..classes import privateView
from ...models import Prjcombination
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
)
from ..project import createProjectFunction
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import datetime
from ..registry import getDataFormPreview


class cloneProjects_view(privateView):
    def processView(self):
        dataworking = {}
        showForm = False
        error_summary = {}
        step = 1

        if self.request.method == "POST":

            dataworking = self.getPostDict()

            if "btn_addNewProject" in self.request.POST:

                dataworking, error_summary, added = createProjectFunction(
                    dataworking, error_summary, self
                )
                if added:
                    enumerators = getProjectEnumerators(
                        self.user.login, dataworking["slt_project_cod"], self.request
                    )
                    for enumerator in enumerators:
                        addEnumeratorToProject(
                            self.user.login,
                            dataworking["project_cod"],
                            enumerator["enum_id"],
                            self.request,
                        )

                    techInfo = searchTechnologiesInProject(
                        self.user.login, dataworking["slt_project_cod"], self.request
                    )
                    for tech in techInfo:
                        added, message = addTechnologyProject(
                            self.user.login,
                            dataworking["project_cod"],
                            tech["tech_id"],
                            self.request,
                        )

                        if added:
                            allAlias = AliasSearchTechnologyInProject(
                                tech["tech_id"],
                                self.user.login,
                                dataworking["slt_project_cod"],
                                self.request,
                            )
                            for alias in allAlias:
                                data = {}
                                data["user_name"] = self.user.login
                                data["project_cod"] = dataworking["project_cod"]
                                data["tech_id"] = tech["tech_id"]
                                data["alias_id"] = alias["alias_idTec"]
                                add, message = AddAliasTechnology(data, self.request)

                            allAliasExtra = AliasExtraSearchTechnologyInProject(
                                tech["tech_id"],
                                self.user.login,
                                dataworking["slt_project_cod"],
                                self.request,
                            )
                            for alias in allAliasExtra:
                                data = {}
                                data["user_name"] = self.user.login
                                data["project_cod"] = dataworking["project_cod"]
                                data["tech_id"] = tech["tech_id"]
                                data["alias_name"] = alias["alias_name"]
                                add, message = addTechAliasExtra(data, self.request)
                    groupsInRegistry = getAllRegistryGroups(
                        self.user.login, dataworking["slt_project_cod"], self.request
                    )
                    for group in groupsInRegistry:
                        group["project_cod"] = dataworking["project_cod"]
                        addgroup, message = addRegistryGroup(group, self)

                        if addgroup:
                            questionsInRegistry = getQuestionsByGroupInRegistry(
                                self.user.login,
                                dataworking["slt_project_cod"],
                                group["section_id"],
                                self.request,
                            )
                            for question in questionsInRegistry:
                                question["project_cod"] = dataworking["project_cod"]
                                question["section_project"] = dataworking["project_cod"]
                                addq, message = addRegistryQuestionToGroup(
                                    question, self.request
                                )

                    assessments = getProjectAssessments(
                        self.user.login, dataworking["slt_project_cod"], self.request
                    )
                    for assessment in assessments:
                        newAssessment = {}
                        newAssessment["ass_desc"] = assessment["ass_desc"]
                        newAssessment["ass_days"] = assessment["ass_days"]
                        newAssessment["ass_final"] = assessment["ass_final"]
                        newAssessment["user_name"] = self.user.login
                        newAssessment["project_cod"] = dataworking["project_cod"]
                        newAssessment["ass_status"] = 0
                        added, msg = addProjectAssessmentClone(
                            newAssessment, self.request
                        )

                        if added:
                            newAssessment["ass_cod"] = msg
                            data = {}
                            data["user_name"] = self.user.login
                            data["project_cod"] = dataworking["slt_project_cod"]
                            data["ass_cod"] = assessment["ass_cod"]
                            groupsInAssessment = getAllAssessmentGroups(
                                data, self.request
                            )
                            for group in groupsInAssessment:
                                group["project_cod"] = dataworking["project_cod"]
                                group["ass_cod"] = newAssessment["ass_cod"]
                                addgroup, message = addAssessmentGroup(group, self)

                                if addgroup:
                                    questionInAssessment = getQuestionsByGroupInAssessment(
                                        self.user.login,
                                        dataworking["slt_project_cod"],
                                        assessment["ass_cod"],
                                        group["section_id"],
                                        self.request,
                                    )
                                    for question in questionInAssessment:
                                        question["project_cod"] = dataworking[
                                            "project_cod"
                                        ]
                                        question["ass_cod"] = newAssessment["ass_cod"]
                                        question["section_project"] = dataworking[
                                            "project_cod"
                                        ]
                                        question["section_assessment"] = newAssessment[
                                            "ass_cod"
                                        ]
                                        addq, message = addAssessmentQuestionToGroup(
                                            question, self.request
                                        )

                    dataworking["clonedProject"] = getAllInformationForProject(
                        self, dataworking["project_cod"]
                    )
                    dataworking["projectBeingCloned"] = getAllInformationForProject(
                        self, dataworking["slt_project_cod"]
                    )
                    step = 2
                    dataworking["slt_project_cod"] = ""

            if ("btn_view_project" in self.request.POST) or error_summary:

                if not error_summary:
                    dataworking["project_numobs"] = 0
                    dataworking["project_numcom"] = 3
                    dataworking["project_regstatus"] = 0
                    dataworking["project_registration_and_analysis"] = 0

                dataworking["projectBeingCloned"] = getAllInformationForProject(
                    self, dataworking["slt_project_cod"]
                )
                showForm = True

        return {
            "activeUser": self.user,
            "dataworking": dataworking,
            "projects": getUserProjects(self.user.login, self.request),
            "countries": getCountryList(self.request),
            "showForm": showForm,
            "error_summary": error_summary,
            "step": step,
        }


def getAllInformationForProject(self, project_cod):

    dataworking = getProjectData(self.user.login, project_cod, self.request)
    dataworking["project_registration_and_analysis"] = dataworking[
        "project_registration_and_analysis"
    ]

    dataworking["project_fieldagents"] = getProjectEnumerators(
        self.user.login, project_cod, self.request
    )

    techInfo = searchTechnologiesInProject(self.user.login, project_cod, self.request)
    for tech in techInfo:
        tech["alias"] = AliasSearchTechnologyInProject(
            tech["tech_id"], self.user.login, project_cod, self.request,
        )
        tech["aliasExtra"] = AliasExtraSearchTechnologyInProject(
            tech["tech_id"], self.user.login, project_cod, self.request
        )
    dataworking["project_techs"] = techInfo

    dataRegistry, finalCloseQst = getDataFormPreview(
        self, project_cod, createAutoRegistry=False
    )

    dataworking["project_registry"] = dataRegistry
    dataAssessments = getProjectAssessments(self.user.login, project_cod, self.request)
    for assessment in dataAssessments:
        dataAssessmentsQuestions, finalCloseQst = getDataFormPreview(
            self, project_cod, assessment["ass_cod"]
        )
        assessment["Questions"] = dataAssessmentsQuestions
    dataworking["project_assessment"] = dataAssessments

    return dataworking
