from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.processes import (
    projectExists,
    getProjectEnumerators,
    getUsableEnumerators,
    addEnumeratorToProject,
    removeEnumeratorFromProject,
    thereIsAnEqualEnumIdInTheProject,
    getActiveProject,
    getTheProjectIdForOwner,
)
from climmob.products import stopTasksByProcess
from climmob.products.fieldagents.fieldagents import create_fieldagents_report
from climmob.views.classes import privateView
import climmob.plugins as p


class projectEnumerators_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        error_summary = {}

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )
            activeProject = getActiveProject(self.user.login, self.request)

            if activeProject["project_template"] == 1:

                self.returnRawViewResult = True
                return HTTPFound(
                    location=self.request.route_url(
                        "dashboard",
                        _query={
                            "user": activeProjectUser,
                            "project": activeProjectCod,
                        },
                    )
                )

            if self.request.method == "POST":
                error_summary = addProjectEnumerators_view.processView(self)
            return {
                "activeUser": self.user,
                "activeProject": activeProject,
                "enumeratorsInProject": getProjectEnumerators(
                    activeProjectId, self.request
                ),
                "enumerators": getUsableEnumerators(activeProjectId, self.request),
                "error_summary": error_summary,
            }


class addProjectEnumerators_view(privateView):
    def processView(self):

        error_summary = {}
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if self.request.method == "POST":
                itsNecessaryCreateTheProduct = False
                errorCount = 1
                for key in self.request.params.keys():
                    if key.find("add") >= 0:
                        enumData = key.replace("add", "").split("[___]")

                        alreadyExists = thereIsAnEqualEnumIdInTheProject(
                            enumData[0], activeProjectId, self.request
                        )
                        if not alreadyExists:
                            project_enumerator_data = {
                                "project_id": activeProjectId,
                                "enum_user": enumData[1],
                                "enum_id": enumData[0],
                            }
                            continue_adding = True
                            message = ""
                            for plugin in p.PluginImplementations(p.IProjectEnumerator):
                                if continue_adding:
                                    (
                                        continue_clone,
                                        message,
                                    ) = plugin.before_adding_enumerator_to_project(
                                        self.request, project_enumerator_data
                                    )
                            if continue_adding:
                                added, message = addEnumeratorToProject(
                                    self.request, project_enumerator_data
                                )
                                if added:
                                    for plugin in p.PluginImplementations(
                                        p.IProjectEnumerator
                                    ):
                                        plugin.after_adding_enumerator_to_project(
                                            self.request, project_enumerator_data
                                        )
                                    itsNecessaryCreateTheProduct = True
                            else:
                                error_summary["error" + str(errorCount)] = message
                                errorCount += 1
                        else:
                            error_summary["error" + str(errorCount)] = self._(
                                "The user {} cannot be added because there is another user with the same username"
                            ).format(str(enumData[0]))
                            errorCount += 1

                if itsNecessaryCreateTheProduct:
                    stopTasksByProcess(
                        self.request, activeProjectId, "create_fieldagents"
                    )
                    locale = self.request.locale_name
                    create_fieldagents_report(
                        locale,
                        self.request,
                        activeProjectUser,
                        activeProjectCod,
                        activeProjectId,
                        getProjectEnumerators(activeProjectId, self.request),
                        getActiveProject(self.user.login, self.request),
                    )

        return error_summary


class removeProjectEnumerators_view(privateView):
    def processView(self):

        enumeratorid = self.request.matchdict["enumeratorid"]
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if self.request.method == "POST":
                deleted, message = removeEnumeratorFromProject(
                    activeProjectId, enumeratorid, self.request
                )
                if not deleted:
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    stopTasksByProcess(
                        self.request,
                        activeProjectId,
                        processName="create_fieldagents",
                    )
                    locale = self.request.locale_name
                    create_fieldagents_report(
                        locale,
                        self.request,
                        activeProjectUser,
                        activeProjectCod,
                        activeProjectId,
                        getProjectEnumerators(activeProjectId, self.request),
                        getActiveProject(self.user.login, self.request),
                    )
                    self.returnRawViewResult = True
                    return {"status": 200}
            else:
                return {}
