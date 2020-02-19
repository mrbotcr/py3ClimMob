from .classes import privateView
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from ..processes import projectExists
from ..processes import (
    getProjectEnumerators,
    getUsableEnumerators,
    addEnumeratorToProject,
    getEnumeratorData,
    removeEnumeratorFromProject,
    seeProgress,
    getAssessmenstByProject,
)
from ..products.fieldagents.fieldagents import create_fieldagents_report
from climmob.products import stopTasksByProcess


class projectEnumerators_view(privateView):
    def processView(self):

        # self.needCSS("sweet")
        # self.needJS("sweet")
        # self.needJS("delete")
        projectid = self.request.matchdict["projectid"]

        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            return {
                "activeUser": self.user,
                "projectid": projectid,
                "enumerators": getProjectEnumerators(
                    self.user.login, projectid, self.request
                ),
                "assessments": getAssessmenstByProject(
                    self.user.login, projectid, self.request
                ),
                "workByUser": seeProgress(self.user.login, projectid, self.request),
            }


class addProjectEnumerators_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "POST":
                for key in self.request.params.keys():
                    if key.find("add") >= 0:
                        id = key.replace("add", "")
                        addEnumeratorToProject(
                            self.user.login, projectid, id, self.request
                        )
                stopTasksByProcess(
                    self.request, self.user.login, projectid, "create_fieldagents"
                )
                locale = self.request.locale_name
                create_fieldagents_report(
                    locale,
                    self.request,
                    self.user.login,
                    projectid,
                    getProjectEnumerators(self.user.login, projectid, self.request),
                )
                self.returnRawViewResult = True
                return HTTPFound(
                    location=self.request.route_url(
                        "prjenumerators", projectid=projectid
                    )
                )
            else:
                return {
                    "activeUser": self.user,
                    "projectid": projectid,
                    "enumerators": getUsableEnumerators(
                        self.user.login, projectid, self.request
                    ),
                }


class removeProjectEnumerators_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        enumeratorid = self.request.matchdict["enumeratorid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "POST":
                deleted, message = removeEnumeratorFromProject(
                    self.user.login, projectid, enumeratorid, self.request
                )
                if not deleted:
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    stopTasksByProcess(
                        self.request,
                        self.user.login,
                        projectid,
                        processName="create_fieldagents",
                    )
                    locale = self.request.locale_name
                    create_fieldagents_report(
                        locale,
                        self.request,
                        self.user.login,
                        projectid,
                        getProjectEnumerators(self.user.login, projectid, self.request),
                    )
                    self.returnRawViewResult = True
                    return {"status": 200}
                # return HTTPFound(location=self.request.route_url('prjenumerators', projectid=projectid))
            else:
                return {
                    "activeUser": self.user,
                    "projectid": projectid,
                    "enumerator": getEnumeratorData(
                        self.user.login, enumeratorid, self.request
                    ),
                }
