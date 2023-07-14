import json
import os

from jinja2 import Environment, FileSystemLoader
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

import climmob.plugins as p
from climmob.processes import (
    projectExists,
    addAssessmentGroup,
    deleteAssessmentGroup,
    modifyAssessmentGroup,
    saveAssessmentOrder,
    getAssessmentGroupInformation,
    availableAssessmentQuestions,
    getProjectAssessments,
    addProjectAssessment,
    getProjectAssessmentInfo,
    modifyProjectAssessment,
    deleteProjectAssessment,
    checkAssessments,
    generateAssessmentFiles,
    getCategoriesFromUserCollaborators,
    setAssessmentIndividualStatus,
    getAssesmentProgress,
    there_is_final_assessment,
    getTheGroupOfThePackageCodeAssessment,
    clean_assessments_error_logs,
    getPackages,
    getTheProjectIdForOwner,
    getActiveProject,
    getPrjLangDefaultInProject,
    languageExistInTheProject,
    getPhraseTranslationInLanguage,
)
from climmob.products.forms.form import create_document_form
from climmob.views.classes import privateView
from climmob.views.registry import getDataFormPreview
from climmob.views.question import getDictForPreview


class deleteAssessmentSection_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        groupid = self.request.matchdict["groupid"]
        assessmentid = self.request.matchdict["assessmentid"]
        error_summary = {}

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            data = getAssessmentGroupInformation(
                activeProjectId, assessmentid, groupid, self.request
            )
            if self.request.method == "POST":
                deleted, message = deleteAssessmentGroup(
                    activeProjectId, assessmentid, groupid, self.request
                )
                if not deleted:
                    error_summary = {"dberror": message}
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    self.returnRawViewResult = True
                    return {"status": 200}

        return {
            "activeUser": self.user,
            "assessmentid": assessmentid,
            "data": data,
            "error_summary": error_summary,
            "groupid": groupid,
        }


def actionsInSections(self, postdata):

    if postdata["action"] == "insert":
        addgroup, message = addAssessmentGroup(postdata, self)
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
            mdf, message = modifyAssessmentGroup(postdata, self)
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


class assessmentSectionActions_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        assessmentid = self.request.matchdict["assessmentid"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if self.request.method == "POST":
                postdata = self.getPostDict()
                postdata["project_id"] = activeProjectId
                postdata["ass_cod"] = assessmentid
                self.returnRawViewResult = True

                if postdata["action"] == "btnNewSection":
                    del postdata["group_cod"]
                    postdata["action"] = "insert"

                if postdata["action"] == "btnUpdateSection":
                    postdata["action"] = "update"

                return actionsInSections(self, postdata)
        return {}


class getAssessmentDetails_view(privateView):
    def processView(self):
        if self.request.method == "GET":
            activeProjectUser = self.request.matchdict["user"]
            activeProjectCod = self.request.matchdict["project"]
            assessmentid = self.request.matchdict["assessmentid"]

            if not projectExists(
                self.user.login, activeProjectUser, activeProjectCod, self.request
            ):
                raise HTTPNotFound()
            else:
                activeProjectId = getTheProjectIdForOwner(
                    activeProjectUser, activeProjectCod, self.request
                )

                assessment = getProjectAssessmentInfo(
                    activeProjectId, assessmentid, self.request
                )
                self.returnRawViewResult = True

                return assessment

        raise HTTPNotFound()


class assessmenthead_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        data = {}
        error_summary = {}

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if self.request.method == "POST":
                data = self.getPostDict()
                if "btn_add_ass" in self.request.POST:
                    data["project_id"] = activeProjectId
                    data["userOwner"] = activeProjectUser
                    if data.get("ass_final", "off") == "on":
                        data["ass_final"] = 1
                    else:
                        data["ass_final"] = 0

                    for plugin in p.PluginImplementations(p.ICheckBox):
                        data = plugin.before_process_checkbox_data(data, "ass_rhomis")

                    added, msg = addProjectAssessment(data, self.request)
                    if data["ass_final"] == 1:
                        data["ass_final"] = "on"
                    else:
                        data["ass_final"] = "off"

                    for plugin in p.PluginImplementations(p.ICheckBox):
                        data = plugin.after_process_checkbox_data(data, "ass_rhomis")

                    if not added:
                        error_summary["addAssessment"] = msg
                    else:
                        data = {}
                else:
                    if "btn_modify_ass" in self.request.POST:
                        data["project_id"] = activeProjectId
                        data["userOwner"] = activeProjectUser
                        if data.get("ass_final", "off") == "on":
                            data["ass_final"] = 1
                        else:
                            data["ass_final"] = 0

                        for plugin in p.PluginImplementations(p.ICheckBox):
                            data = plugin.before_process_checkbox_data(
                                data, "ass_rhomis"
                            )

                        # for plugin in p.PluginImplementations(p.IRhomis):
                        #     data = plugin.before_process_modify(
                        #         activeProjectUser, activeProjectCod, data, self.request
                        #     )

                        error, msg = modifyProjectAssessment(data, self.request)
                        if data["ass_final"] == 1:
                            data["ass_final"] = "on"
                        else:
                            data["ass_final"] = "off"

                        for plugin in p.PluginImplementations(p.ICheckBox):
                            data = plugin.after_process_checkbox_data(
                                data, "ass_rhomis"
                            )

                        if not error:
                            error_summary["modifyAssessment"] = msg
                        else:
                            data = {}

            new_available = not there_is_final_assessment(self.request, activeProjectId)

            return {
                "new_available": new_available,
                "activeProject": getActiveProject(self.user.login, self.request),
                "assessments": getProjectAssessments(activeProjectId, self.request),
                "data": data,
                "error_summary": error_summary,
            }


class deleteassessmenthead_view(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        assessmentid = self.request.matchdict["assessmentid"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            data = getProjectAssessmentInfo(activeProjectId, assessmentid, self.request)

            error_summary = {}
            if self.request.method == "POST":
                error, msg = deleteProjectAssessment(
                    activeProjectUser,
                    activeProjectId,
                    activeProjectId,
                    assessmentid,
                    self.request,
                )

                if not error:
                    error_summary["deleteAssessment"] = msg
                    self.returnRawViewResult = True
                    return {"status": 400, "error": msg}
                else:
                    self.returnRawViewResult = True
                    return {"status": 200}
            return {
                "data": data,
                "error_summary": error_summary,
            }


class assessment_view(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        assessmentid = self.request.matchdict["assessmentid"]
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

                if not languageExistInTheProject(
                    activeProjectId, langActive, self.request
                ):
                    raise HTTPNotFound()

            else:
                langActive = getPrjLangDefaultInProject(activeProjectId, self.request)
                if langActive:
                    langActive = langActive["lang_code"]
                else:
                    langActive = self.request.locale_name

            data, finalCloseQst = getDataFormPreview(
                self, activeProjectUser, activeProjectId, langActive, assessmentid
            )

            dictreturn = {
                "activeUser": self.user,
                "data": data,
                "finalCloseQst": finalCloseQst,
                "error_summary": error_summary,
                "activeProject": getActiveProject(self.user.login, self.request),
                "assessmentid": assessmentid,
                "assinfo": getProjectAssessmentInfo(
                    activeProjectId, assessmentid, self.request
                ),
                "UserQuestion": availableAssessmentQuestions(
                    activeProjectId, assessmentid, self.request, language=langActive
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


class assessmentFormCreation_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        assessmentid = self.request.matchdict["assessmentid"]
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
                newOrder = d = json.loads(self.request.POST.get("neworder", "{}"))
                questionWithoutGroup = False
                for item in newOrder:
                    if item["type"] == "question":
                        questionWithoutGroup = True

                if not questionWithoutGroup:
                    modified, error = saveAssessmentOrder(
                        activeProjectId,
                        assessmentid,
                        newOrder,
                        self.request,
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
                    self, activeProjectUser, activeProjectId, langActive, assessmentid
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


class startAssessments_view(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        onlyError = False
        checkPass = False
        error_summary = {}
        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if self.request.method == "GET":
                # this URL is only for POST
                raise HTTPNotFound()

            if self.request.method == "POST":
                data = self.getPostDict()
                assessment_id = data["assessment_id"]
                redirect = False
                print("checkAssessments")

                isExternal = False
                assessInfo = getProjectAssessmentInfo(
                    activeProjectId, assessment_id, self.request
                )
                # for plugin in p.PluginImplementations(p.IRhomis):
                #     if "ass_rhomis" in assessInfo.keys():
                #         if assessInfo["ass_rhomis"] == 1:
                #             isExternal = True
                #             for plugin in p.PluginImplementations(p.IRhomis):
                #                 (
                #                     checkPass,
                #                     error_summary,
                #                 ) = plugin.start_external_data_collection_form(
                #                     self.request,
                #                     activeProjectUser,
                #                     activeProjectId,
                #                     activeProjectCod,
                #                     assessment_id,
                #                 )
                #
                #                 if checkPass:
                #                     self.returnRawViewResult = True
                #                     return HTTPFound(
                #                         location=self.request.route_url("dashboard")
                #                     )

                if not isExternal:

                    checkPass, error_summary = checkAssessments(
                        activeProjectId, assessment_id, self.request
                    )
                    if checkPass:
                        print("generateAssessmentFiles")
                        sectionOfThePackageCode = getTheGroupOfThePackageCodeAssessment(
                            activeProjectId, assessment_id, self.request
                        )

                        projectDetails = getActiveProject(self.user.login, self.request)
                        languages = projectDetails["languages"]
                        listOfLabels = [
                            projectDetails["project_label_a"],
                            projectDetails["project_label_b"],
                            projectDetails["project_label_c"],
                        ]

                        correct = generateAssessmentFiles(
                            activeProjectUser,
                            activeProjectId,
                            activeProjectCod,
                            assessment_id,
                            self.request,
                            sectionOfThePackageCode,
                            listOfLabels,
                        )

                        # Edited by Brandon
                        if correct[0]["result"]:
                            print("setAssessmentIndividualStatus")
                            setAssessmentIndividualStatus(
                                activeProjectId, assessment_id, 1, self.request
                            )

                            print("getPackages")
                            ncombs, packages = getPackages(
                                activeProjectUser, activeProjectId, self.request
                            )
                            print("getDataFormPreview")
                            if languages:
                                for lang in languages:
                                    data, finalCloseQst = getDataFormPreview(
                                        self,
                                        activeProjectUser,
                                        activeProjectId,
                                        assessmentid=assessment_id,
                                        language=lang["lang_code"],
                                    )

                                    lang["Data"] = data

                                dataPreviewInMultipleLanguages = languages
                            else:
                                data, finalCloseQst = getDataFormPreview(
                                    self,
                                    activeProjectUser,
                                    activeProjectId,
                                    assessmentid=assessment_id,
                                    language=self.request.locale_name,
                                )
                                dataPreviewInMultipleLanguages = [
                                    {
                                        "lang_code": self.request.locale_name,
                                        "lang_name": "Default",
                                        "Data": data,
                                    }
                                ]

                            print("create_document_form")
                            create_document_form(
                                self.request,
                                self.request.locale_name,
                                activeProjectUser,
                                activeProjectId,
                                activeProjectCod,
                                "Assessment",
                                assessment_id,
                                dataPreviewInMultipleLanguages,
                                packages,
                                listOfLabels,
                            )
                            print("Returning")

                            for plugin in p.PluginImplementations(p.IForm):
                                plugin.after_adding_form(
                                    self.request,
                                    activeProjectUser,
                                    activeProjectId,
                                    activeProjectCod,
                                    "assessment",
                                    assessment_id,
                                )

                            for plugin in p.PluginImplementations(p.IUpload):
                                plugin.create_Excel_template_for_upload_data(
                                    self.request,
                                    activeProjectUser,
                                    activeProjectId,
                                    activeProjectCod,
                                    "assessment",
                                    assessment_id,
                                )

                            self.returnRawViewResult = True
                            return HTTPFound(
                                location=self.request.route_url("dashboard")
                            )
                        else:
                            onlyError = True
                            error_summary = {
                                "error": self._(
                                    "There has been a problem in the creation of the basic structure of the project, this may be due to something wrong with the form."
                                ),
                                "contact": self._(
                                    "Contact the ClimMob team with the next message to get the solution to the problem:"
                                ),
                                "copie": str(correct[0]["error"], "utf-8"),
                            }

                return {
                    "activeUser": self.user,
                    "activeProject": getActiveProject(self.user.login, self.request),
                    "error_summary": error_summary,
                    "checkPass": checkPass,
                    "redirect": redirect,
                    "onlyError": onlyError,
                }


class closeAssessment_view(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        assessmentid = self.request.matchdict["assessmentid"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )

        redirect = False
        progress, pcompleted = getAssesmentProgress(
            activeProjectUser,
            activeProjectId,
            activeProjectCod,
            assessmentid,
            self.request,
        )
        assessmentData = getProjectAssessmentInfo(
            activeProjectId, assessmentid, self.request
        )
        if self.request.method == "POST":
            if "closeAssessment" in self.request.params.keys():
                setAssessmentIndividualStatus(
                    activeProjectId, assessmentid, 2, self.request
                )

                for plugin in p.PluginImplementations(p.IForm):
                    plugin.after_deleting_form(
                        self.request,
                        activeProjectUser,
                        activeProjectId,
                        activeProjectCod,
                        "assessment",
                        assessmentid,
                    )

                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("dashboard"))

        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "activeUser": self.user,
            "redirect": redirect,
            "progress": progress,
            "assessmentData": assessmentData,
        }


class CancelAssessmentView(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        assessmentid = self.request.matchdict["assessmentid"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )

        redirect = False
        progress, pcompleted = getAssesmentProgress(
            activeProjectUser,
            activeProjectId,
            activeProjectCod,
            assessmentid,
            self.request,
        )
        assessmentData = getProjectAssessmentInfo(
            activeProjectId, assessmentid, self.request
        )
        if self.request.method == "POST":
            if "closeAssessment" in self.request.params.keys():
                setAssessmentIndividualStatus(
                    activeProjectId, assessmentid, 0, self.request
                )
                clean_assessments_error_logs(
                    self.request, activeProjectId, assessmentid
                )

                for plugin in p.PluginImplementations(p.IForm):
                    plugin.after_deleting_form(
                        self.request,
                        activeProjectUser,
                        activeProjectId,
                        activeProjectCod,
                        "assessment",
                        assessmentid,
                    )

                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("dashboard"))

        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "activeUser": self.user,
            "redirect": redirect,
            "progress": progress,
            "assessmentData": assessmentData,
        }


class getAssessmentSection_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        assessmentid = self.request.matchdict["assessmentid"]
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
                section = getAssessmentGroupInformation(
                    activeProjectId, assessmentid, section, self.request
                )
                return section
        return {}
