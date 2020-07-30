from .classes import privateView, publicView
from ..processes import (
    getActiveProject,
    getProjectProgress,
    projectExists,
    setActiveProject,
    getUserProjects,
    get_usable_assessments,
    getAnalysisControl,
    getProjectEncrypted,
    getUserInfo,
    getRegistryInformation,
    getMD5Project,
    AssessmentsInformation,
    seeProgress,
    counterChat
)
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from .assessment import startAssessments_view


class dashboard_view(privateView):
    def processView(self):

        if "project" in self.request.params.keys():

            activeProject = self.request.params["project"]
            if not projectExists(self.user.login, activeProject, self.request):
                raise HTTPNotFound()
            else:

                session = self.request.session
                session["activeProject"] = activeProject
                setActiveProject(self.user.login, activeProject, self.request)
                activeProjectData = getActiveProject(self.user.login, self.request)

                progress, pcompleted = getProjectProgress(
                    self.user.login, activeProject, self.request
                )
                hasActiveProject = True
                showAnalysis = False
                progress["usableAssessments"] = get_usable_assessments(
                    self.request, self.user.login, activeProject
                )
                progress["analysisControl"] = getAnalysisControl(
                    self.request, self.user.login, activeProject
                )
                total_ass_records = 0
                all_ass_closed = True
                for assessment in progress["assessments"]:
                    if assessment["ass_status"] == 1 or assessment["ass_status"] == 2:
                        if assessment["ass_status"] == 1:
                            all_ass_closed = False
                        showAnalysis = True
                        total_ass_records = total_ass_records + assessment["asstotal"]
                    else:
                        all_ass_closed = False

                return {
                    "activeUser": self.user,
                    "activeProject": activeProjectData,
                    "hasActiveProject": hasActiveProject,
                    "progress": progress,
                    "pcompleted": pcompleted,
                    "userProjects": getUserProjects(self.user.login, self.request),
                    "showAnalysis": showAnalysis,
                    "total_ass_records": total_ass_records,
                    "allassclosed": all_ass_closed,
                    "encrypted": getMD5Project(
                        self.user.login, activeProjectData["project_cod"], self.request
                    ),
                    "fieldagents":seeProgress(self.user.login,activeProjectData["project_cod"],self.request),
                    "usable_assessments": get_usable_assessments(
                        self.request, self.user.login, activeProjectData["project_cod"]
                    )
                }
        else:
            activeProjectData = getActiveProject(self.user.login, self.request)
            if activeProjectData:
                self.returnRawViewResult = True
                return HTTPFound(
                    location=self.request.route_url(
                        "dashboard",
                        _query={"project": activeProjectData["project_cod"]},
                    )
                )
            else:
                return {
                    "activeUser": self.user,
                    "activeProject": activeProjectData,
                    "hasActiveProject": False,
                    "progress": {},
                    "pcompleted": 0,
                    "allassclosed": False,
                }


class projectInformation_view(publicView):
    def processView(self):
        encrypted = self.request.matchdict["id"]
        exists, info = getProjectEncrypted(self.request, encrypted)
        registry = getRegistryInformation(self.request, info)
        assessments = AssessmentsInformation(self.request, info, registry["Delivered"])

        if exists:
            return {
                "Exist": exists,
                "Project": info,
                "User": getUserInfo(self.request, info["user_name"]),
                "Registry": registry,
                "Assessments": assessments,
            }
        else:
            raise HTTPNotFound()
