from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.processes import (
    getUserProjects,
    getProjectEnumerators,
    searchTechnologiesInProject,
    getProjectData,
    getProjectAssessments,
    getCountryList,
    AliasSearchTechnologyInProject,
    AliasExtraSearchTechnologyInProject,
    projectExists,
    getActiveProject,
    getTheProjectIdForOwner,
)
from climmob.views.classes import privateView
from climmob.views.project import createProjectFunction, functionCreateClone
from climmob.views.registry import getDataFormPreview


class cloneProjects_view(privateView):
    def processView(self):

        dataworking = {}
        dataworking["structureToBeCloned"] = ""
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
            dataworking["project_label_a"] = self._("Option A")
            dataworking["project_label_b"] = self._("Option B")
            dataworking["project_label_c"] = self._("Option C")
            dataworking["project_pi"] = self.user.fullName
            dataworking["project_piemail"] = self.user.email

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


def getAllInformationForProject(self, userOwner, projectId):

    dataworking = getProjectData(projectId, self.request)

    dataworking["project_registration_and_analysis"] = dataworking[
        "project_registration_and_analysis"
    ]

    dataworking["project_fieldagents"] = getProjectEnumerators(projectId, self.request)

    techInfo = searchTechnologiesInProject(projectId, self.request)
    for tech in techInfo:
        tech["alias"] = AliasSearchTechnologyInProject(
            tech["tech_id"],
            projectId,
            self.request,
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
