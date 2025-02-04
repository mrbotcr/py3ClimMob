import json
import os

from jinja2 import Environment, FileSystemLoader
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

import climmob.plugins as p
from climmob.processes import (
    projectExists,
    addRegistryGroup,
    deleteRegistryGroup,
    modifyRegistryGroup,
    getRegistryQuestions,
    saveRegistryOrder,
    getRegistryGroupInformation,
    availableRegistryQuestions,
    setRegistryStatus,
    getProjectProgress,
    clean_registry_error_logs,
    getCategoriesFromUserCollaborators,
    getAssessmentQuestions,
    getActiveProject,
    getTheProjectIdForOwner,
    getProjectLabels,
    getPrjLangDefaultInProject,
    languageExistInTheProject,
    modifyProjectMainLanguage,
    projectRegStatus,
)
from climmob.products import stopTasksByProcess
from climmob.views.classes import privateView
from climmob.views.question import getDictForPreview
from climmob.products.forms.form import create_document_form


class DeleteRegistrySectionView(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        groupid = self.request.matchdict["groupid"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )

        data = getRegistryGroupInformation(activeProjectId, groupid, self.request)
        if self.request.method == "POST":
            deleted, message = deleteRegistryGroup(
                activeProjectId, groupid, self.request
            )
            if not deleted:
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
            else:
                self.returnRawViewResult = True
                return {"status": 200}

        return {
            "activeUser": self.user,
            "data": data,
            "groupid": groupid,
        }


def actionsInSections(self, postdata):

    if postdata["action"] == "insert":
        addgroup, message = addRegistryGroup(postdata, self)
        if not addgroup:
            if message == "repeated":
                return {
                    "result": "error",
                    "error": self._("There is already a group with this name."),
                }
            else:
                return {"result": "error", "error": message}
        else:
            return {
                "result": "success",
                "success": self._("The section was successfully added"),
            }
    else:
        if postdata["action"] == "update":
            mdf, message = modifyRegistryGroup(postdata, self)
            if not mdf:
                if message == "repeated":
                    return {
                        "result": "error",
                        "error": self._("There is already a group with this name."),
                    }
                else:
                    return {"result": "error", "error": message}
            else:
                return {
                    "result": "success",
                    "success": self._("The section was successfully updated"),
                }


class RegistrySectionActionsView(privateView):
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

        if self.request.method == "POST":
            postdata = self.getPostDict()
            postdata["project_id"] = activeProjectId
            self.returnRawViewResult = True

            if postdata["action"] == "btnNewSection":
                del postdata["group_cod"]
                postdata["action"] = "insert"

            if postdata["action"] == "btnUpdateSection":
                postdata["action"] = "update"

            return actionsInSections(self, postdata)


class CancelRegistryView(privateView):
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
        if self.request.method == "POST":
            if "cancelRegistry" in self.request.params.keys():
                setRegistryStatus(
                    activeProjectUser,
                    activeProjectCod,
                    activeProjectId,
                    0,
                    self.request,
                )
                clean_registry_error_logs(self.request, activeProjectId)

                stopTasksByProcess(self.request, activeProjectId)

                for plugin in p.PluginImplementations(p.IForm):
                    plugin.after_deleting_form(
                        self.request,
                        activeProjectUser,
                        activeProjectId,
                        activeProjectCod,
                        "registry",
                        "",
                    )

                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("dashboard"))

        return {
            "activeUser": self.user,
            "redirect": redirect,
            "activeProject": getActiveProject(self.user.login, self.request),
        }


class CloseRegistryView(privateView):
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

        progress, pcompleted = getProjectProgress(
            activeProjectUser, activeProjectCod, activeProjectId, self.request
        )
        if self.request.method == "POST":
            if "closeRegistry" in self.request.params.keys():
                setRegistryStatus(
                    activeProjectUser,
                    activeProjectCod,
                    activeProjectId,
                    2,
                    self.request,
                )
                for plugin in p.PluginImplementations(p.IForm):
                    plugin.after_deleting_form(
                        self.request,
                        activeProjectUser,
                        activeProjectId,
                        activeProjectCod,
                        "registry",
                        "",
                    )

                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("dashboard"))

        return {
            "activeUser": self.user,
            "redirect": redirect,
            "progress": progress,
            "activeProject": getActiveProject(self.user.login, self.request),
        }


class RegistryView(privateView):
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

        if "language" in self.request.params.keys():
            langActive = self.request.params["language"]

            if not languageExistInTheProject(activeProjectId, langActive, self.request):
                raise HTTPNotFound()

        else:
            langActive = getPrjLangDefaultInProject(activeProjectId, self.request)
            if langActive:
                langActive = langActive["lang_code"]
            else:
                langActive = self.request.locale_name

        if "btn_download_doc" in self.request.POST:

            projectDetails = getActiveProject(self.user.login, self.request)

            listOfLabels = [
                projectDetails["project_label_a"],
                projectDetails["project_label_b"],
                projectDetails["project_label_c"],
            ]

            createDocumentForm(
                projectDetails["languages"],
                self,
                activeProjectUser,
                activeProjectId,
                self.request.locale_name,
                activeProjectCod,
                listOfLabels,
            )

            self.returnRawViewResult = True
            return HTTPFound(
                location=self.request.route_url(
                    "productList", _query={"product1": "create_from_Registration_"}
                )
            )

        data, finalCloseQst = getDataFormPreview(
            self, activeProjectUser, activeProjectId, langActive
        )

        activeProjectData = getActiveProject(self.user.login, self.request)

        dictreturn = {
            "activeUser": self.user,
            "data": data,
            "finalCloseQst": finalCloseQst,
            "activeProject": activeProjectData,
            "UserQuestion": availableRegistryQuestions(
                activeProjectId,
                self.request,
                activeProjectData["project_registration_and_analysis"],
                language=langActive,
            ),
            "Categories": getCategoriesFromUserCollaborators(
                activeProjectId, self.request
            ),
            "languageActive": langActive,
        }

        dictreturn.update(
            getDictForPreview(self.request, activeProjectUser, langActive)
        )

        return dictreturn


class RegistryFormCreationView(privateView):
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

            if "language" in self.request.params.keys():
                langActive = self.request.params["language"]
            else:
                langActive = getPrjLangDefaultInProject(activeProjectId, self.request)
                if langActive:
                    langActive = langActive["lang_code"]
                else:
                    langActive = self.request.locale_name

            if self.request.method == "POST":
                # if "saveorder" in self.request.POST:
                newOrder = json.loads(self.request.POST.get("neworder", "{}"))
                questionWithoutGroup = False
                for item in newOrder:
                    if item["type"] == "question":
                        questionWithoutGroup = True

                if not questionWithoutGroup:
                    modified, error = saveRegistryOrder(
                        activeProjectId, newOrder, self.request
                    )
                else:
                    error_summary["questionWithoutGroup"] = self._(
                        "Questions cannot be outside a group"
                    )

                PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                env = Environment(
                    autoescape=False,
                    loader=FileSystemLoader(
                        os.path.join(PATH, "templates", "snippets", "project")
                    ),
                    trim_blocks=False,
                )
                template = env.get_template("previewForm.jinja2")

                data, finalCloseQst = getDataFormPreview(
                    self, activeProjectUser, activeProjectId, langActive
                )

                info = {
                    "img1": self.request.url_for_static("landing/odk.png"),
                    "img2": self.request.url_for_static("landing/odk2.png"),
                    "img3": self.request.url_for_static("landing/odk3.png"),
                    "data": data,
                    "isOneProject": "True",
                    "activeProject": getActiveProject(self.user.login, self.request),
                    "_": self._,
                    "showPhone": True,
                }

                info.update(
                    getDictForPreview(self.request, activeProjectUser, langActive)
                )
                render_temp = template.render(info)

                self.returnRawViewResult = True
                return render_temp
        self.returnRawViewResult = True
        return ""


def getDataFormPreview(
    self,
    userOwner,
    projectId,
    language="default",
    assessmentid=None,
    createAutoRegistry=True,
):
    projectLabels = getProjectLabels(projectId, self.request)

    if not assessmentid:
        data = getRegistryQuestions(
            userOwner,
            projectId,
            self.request,
            projectLabels,
            language=language,
            createAutoRegistry=createAutoRegistry,
        )
    else:
        data = getAssessmentQuestions(
            userOwner,
            projectId,
            assessmentid,
            self.request,
            projectLabels,
            language=language,
        )
    # The following is to help jinja2 to render the groups and questions
    # This because the scope constraint makes it difficult to control
    sectionID = -99
    grpIndex = -1
    finalCloseQst = 0
    for a in range(0, len(data)):
        if data[a]["section_id"] != sectionID:
            grpIndex = a
            data[a]["createGRP"] = True
            data[a]["grpCannotDelete"] = False
            sectionID = data[a]["section_id"]
            if a == 0:
                data[a]["closeQst"] = False
                data[a]["closeGrp"] = False
            else:
                if data[a - 1]["hasQuestions"]:
                    data[a]["closeQst"] = True
                    data[a]["closeGrp"] = True
                else:
                    data[a]["closeGrp"] = False
                    data[a]["closeQst"] = False
        else:
            data[a]["createGRP"] = False
            data[a]["closeQst"] = False
            data[a]["closeGrp"] = False

        if data[a]["question_id"] != None:
            data[a]["hasQuestions"] = True
            if "question_reqinreg" in data[a].keys():
                if data[a]["question_reqinreg"] == 1:
                    data[grpIndex]["grpCannotDelete"] = True

            if "question_reqinasses" in data[a].keys():
                if data[a]["question_reqinasses"] == 1:
                    data[grpIndex]["grpCannotDelete"] = True
        else:
            data[a]["hasQuestions"] = False

    if data:
        finalCloseQst = data[len(data) - 1]["hasQuestions"]

    return data, finalCloseQst


class GetRegistrySectionView(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        section = self.request.matchdict["section"]
        self.returnRawViewResult = True

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )
            if self.request.method == "GET":

                section = getRegistryGroupInformation(
                    activeProjectId, section, self.request
                )

                return section

        return {}


def createDocumentForm(
    languages, self, userOwner, projectId, locale, projectCod, listOfLabelsForPackages
):
    if languages:
        for lang in languages:
            data, finalCloseQst = getDataFormPreview(
                self, userOwner, projectId, language=lang["lang_code"]
            )

            lang["Data"] = data

        dataPreviewInMultipleLanguages = languages
    else:
        data, finalCloseQst = getDataFormPreview(
            self, userOwner, projectId, language=locale
        )
        dataPreviewInMultipleLanguages = [
            {"lang_code": locale, "lang_name": "Default", "Data": data}
        ]

    create_document_form(
        self.request,
        locale,
        userOwner,
        projectId,
        projectCod,
        "Registration",
        "",
        dataPreviewInMultipleLanguages,
        listOfLabelsForPackages,
    )


class ChangeProjectMainLanguage_view(privateView):
    def processView(self):

        self.returnRawViewResult = True
        if self.request.method == "POST":

            postdata = self.getPostDict()
            activeProjectUser = postdata["user"]
            activeProjectCod = postdata["project"]
            main_language = postdata["main_language"]

            if not projectExists(
                self.user.login, activeProjectUser, activeProjectCod, self.request
            ):
                raise HTTPNotFound()
            else:
                activeProjectId = getTheProjectIdForOwner(
                    activeProjectUser, activeProjectCod, self.request
                )

                if projectRegStatus(activeProjectId, self.request):

                    edited, message = modifyProjectMainLanguage(
                        self.request, activeProjectId, main_language
                    )

                    if edited:

                        return {
                            "result": "success",
                            "message": self._("Main language successfully updated"),
                        }

        return {
            "result": "error",
            "message": self._("There was an error updating the main language"),
        }
