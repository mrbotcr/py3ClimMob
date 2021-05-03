from .classes import privateView
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import json
from ..processes import QuestionsOptions, projectExists, getCategories
from ..processes import (
    addAssessmentGroup,
    addAssessmentQuestionToGroup,
    deleteAssessmentGroup,
    modifyAssessmentGroup,
    getAssessmentGroupData,
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
    getCategoriesParents,
    setAssessmentIndividualStatus,
    getAssesmentProgress,
    there_is_final_assessment,
    getTheGroupOfThePackageCodeAssessment,
    clean_assessments_error_logs,
    getPackages,
)
from ..products.forms.form import create_document_form
from jinja2 import Environment, FileSystemLoader
from .registry import getDataFormPreview
from pyramid.response import FileResponse
import mimetypes, os

import pprint


class modifyAssessmentSection_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        groupid = self.request.matchdict["groupid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            error_summary = {}
            data = {}
            data["project_cod"] = projectid
            data["ass_cod"] = assessmentid
            data["group_cod"] = groupid
            data["user_name"] = self.user.login

            if self.request.method == "POST":
                if "btn_modify_group" in self.request.POST:
                    tdata = self.getPostDict()
                    data["section_name"] = tdata["section_name"]
                    data["section_content"] = tdata["section_content"]

                    if data["section_name"] != "":
                        if data["section_content"] != "":

                            mdf, message = modifyAssessmentGroup(data, self)
                            if not mdf:
                                if message == "repeated":
                                    error_summary = {
                                        "repeated": self._(
                                            "There is already a group with this name."
                                        )
                                    }
                                else:
                                    error_summary = {"dberror": message}
                            else:
                                self.returnRawViewResult = True
                                return HTTPFound(
                                    location=self.request.route_url(
                                        "assessmentdetail",
                                        projectid=projectid,
                                        assessmentid=assessmentid,
                                    )
                                )
                        else:
                            error_summary = {
                                "sectiondescription": self._(
                                    "The description of the group cannot be empty."
                                )
                            }
                    else:
                        error_summary = {
                            "sectionname": self._(
                                "The name of the group cannot be empty."
                            )
                        }
            else:
                groupData = getAssessmentGroupData(data, self)
                data["section_name"] = groupData["section_name"]
                data["section_content"] = groupData["section_content"]
            return {
                "activeUser": self.user,
                "projectid": projectid,
                "assessmentid": assessmentid,
                "data": data,
                "error_summary": error_summary,
                "assinfo": getProjectAssessmentInfo(
                    self.user.login, projectid, assessmentid, self.request
                ),
            }


class deleteAssessmentSection_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        groupid = self.request.matchdict["groupid"]
        assessmentid = self.request.matchdict["assessmentid"]
        error_summary = {}
        data = projectExists(self.user.login, projectid, self.request)

        if not data:
            raise HTTPNotFound()
        else:
            data = getAssessmentGroupInformation(
                self.user.login, projectid, assessmentid, groupid, self.request
            )
            if self.request.method == "POST":
                deleted, message = deleteAssessmentGroup(
                    self.user.login, projectid, assessmentid, groupid, self.request
                )
                if not deleted:
                    error_summary = {"dberror": message}
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    self.returnRawViewResult = True
                    return {"status": 200}
                    # return HTTPFound(location=self.request.route_url('assessmentdetail',projectid=projectid,assessmentid=assessmentid))

        return {
            "activeUser": self.user,
            "projectid": projectid,
            "assessmentid": assessmentid,
            "data": data,
            "error_summary": error_summary,
            "groupid": groupid,
        }


class newAssessmentSection_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        error_summary = {}
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            data = {}
            data["user_name"] = self.user.login
            data["project_cod"] = projectid
            data["ass_cod"] = assessmentid
            if self.request.method == "POST":
                if "btn_add_group" in self.request.POST:
                    tdata = self.getPostDict()
                    data["section_name"] = tdata["section_name"]
                    data["section_content"] = tdata["section_content"]
                    data["section_private"] = None
                    if data["section_name"] != "":
                        if data["section_content"] != "":
                            addgroup, message = addAssessmentGroup(data, self)

                            if not addgroup:
                                if message == "repeated":
                                    error_summary = {
                                        "repeated": self._(
                                            "There is already a group with this name."
                                        )
                                    }
                                else:
                                    error_summary = {"dberror": message}
                            else:
                                self.returnRawViewResult = True
                                return HTTPFound(
                                    location=self.request.route_url(
                                        "assessmentdetail",
                                        projectid=projectid,
                                        assessmentid=assessmentid,
                                    )
                                )
                        else:
                            error_summary = {
                                "sectiondescription": self._(
                                    "The description of the group can not be empty."
                                )
                            }
                    else:
                        error_summary = {
                            "sectionname": self._(
                                "The name of the group can not be empty."
                            )
                        }

            return {
                "activeUser": self.user,
                "projectid": projectid,
                "assessmentid": assessmentid,
                "data": self.decodeDict(data),
                "error_summary": error_summary,
                "assinfo": getProjectAssessmentInfo(
                    self.user.login, projectid, assessmentid, self.request
                ),
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
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "POST":
                postdata = self.getPostDict()
                postdata["user_name"] = self.user.login
                postdata["project_cod"] = projectid
                postdata["ass_cod"] = assessmentid
                self.returnRawViewResult = True

                if postdata["action"] == "btnNewSection":
                    del postdata["group_cod"]
                    postdata["action"] = "insert"

                if postdata["action"] == "btnUpdateSection":
                    postdata["action"] = "update"

                return actionsInSections(self, postdata)
        return {}


class newAssessmentQuestion_view(privateView):
    def processView(self):

        projectid = self.request.matchdict["projectid"]
        groupid = self.request.matchdict["groupid"]
        assessmentid = self.request.matchdict["assessmentid"]

        data = {}
        data["project_cod"] = projectid
        data["ass_cod"] = assessmentid
        data["group_cod"] = groupid
        data["section_id"] = groupid
        data["user_name"] = self.user.login

        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "POST":
                if "btn_add_question_to_group" in self.request.POST:
                    postdata = self.getPostDict()
                    error = False
                    for key in postdata.keys():
                        if key.find("CHK") >= 0:
                            qid = key.replace("CHK", "")
                            data["question_id"] = qid
                            addq, message = addAssessmentQuestionToGroup(
                                data, self.request
                            )
                            if not addq:
                                error = True
                    if not error:
                        self.returnRawViewResult = True
                        return HTTPFound(
                            location=self.request.route_url(
                                "assessmentdetail",
                                projectid=projectid,
                                assessmentid=assessmentid,
                            )
                        )

            # print availableAssessmentQuestions(self.user.login,projectid,assessmentid,self.request)
            return {
                "activeUser": self.user,
                "UserQuestion": availableAssessmentQuestions(
                    self.user.login, projectid, assessmentid, self.request
                ),
                "QuestionsOptions": QuestionsOptions(self.user.login, self.request),
                "projectid": projectid,
                "assessmentid": assessmentid,
                "assinfo": getProjectAssessmentInfo(
                    self.user.login, projectid, assessmentid, self.request
                ),
                "groupInfo": getAssessmentGroupData(data, self),
                "Categories": getCategories(self.user.login, self.request),
            }


class assessmenthead_view(privateView):
    def processView(self):

        projectid = self.request.matchdict["projectid"]
        data = {}
        error_summary = {}

        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:

            if self.request.method == "POST":
                data = self.getPostDict()
                if "btn_add_ass" in self.request.POST:
                    data["project_cod"] = projectid
                    data["user_name"] = self.user.login
                    if data.get("ass_final", "off") == "on":
                        data["ass_final"] = 1
                    else:
                        data["ass_final"] = 0
                    added, msg = addProjectAssessment(data, self.request)
                    if data["ass_final"] == 1:
                        data["ass_final"] = "on"
                    else:
                        data["ass_final"] = "off"
                    if not added:
                        error_summary["addAssessment"] = msg
                    else:
                        data = {}
                else:
                    if "btn_modify_ass" in self.request.POST:
                        data["project_cod"] = projectid
                        data["user_name"] = self.user.login
                        if data.get("ass_final", "off") == "on":
                            data["ass_final"] = 1
                        else:
                            data["ass_final"] = 0
                        error, msg = modifyProjectAssessment(data, self.request)
                        if data["ass_final"] == 1:
                            data["ass_final"] = "on"
                        else:
                            data["ass_final"] = "off"
                        if not error:
                            error_summary["modifyAssessment"] = msg
                        else:
                            data = {}

            new_available = not there_is_final_assessment(
                self.request, self.user.login, projectid
            )

            return {
                "new_available": new_available,
                "activeUser": self.user,
                "projectid": projectid,
                "assessments": getProjectAssessments(
                    self.user.login, projectid, self.request
                ),
                "data": data,
                "error_summary": error_summary,
            }


"""
class newassessmenthead_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            data = {}
            error_summary = {}
            if self.request.method == "POST":
                data = self.getPostDict()
                data["project_cod"] = projectid
                data["user_name"] = self.user.login
                if data.get("ass_final", "off") == "on":
                    data["ass_final"] = 1
                else:
                    data["ass_final"] = 0
                added, msg = addProjectAssessment(data, self.request)
                if data["ass_final"] == 1:
                    data["ass_final"] = "on"
                else:
                    data["ass_final"] = "off"
                if not added:
                    error_summary["addAssessment"] = msg
                else:
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "assessment", projectid=projectid
                        )
                    )
            new_available = not there_is_final_assessment(
                self.request, self.user.login, projectid
            )
            return {
                "new_available": new_available,
                "activeUser": self.user,
                "projectid": projectid,
                "data": data,
                "error_summary": error_summary,
            }
"""

"""
class modifyassessmenthead_view(privateView):
    def processView(self):
        # self.needCSS('switch')
        # self.needJS('switch')
        # self.needJS('assessment_form')
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            data = getProjectAssessmentInfo(
                self.user.login, projectid, assessmentid, self.request
            )
            if data["ass_final"] == 1:
                data["ass_final"] = "on"
            else:
                data["ass_final"] = "off"
            error_summary = {}
            if self.request.method == "POST":
                data = self.getPostDict()
                data["project_cod"] = projectid
                data["ass_cod"] = assessmentid
                data["user_name"] = self.user.login
                if data.get("ass_final", "off") == "on":
                    data["ass_final"] = 1
                else:
                    data["ass_final"] = 0
                error, msg = modifyProjectAssessment(data, self.request)
                if data["ass_final"] == 1:
                    data["ass_final"] = "on"
                else:
                    data["ass_final"] = "off"
                if not error:
                    error_summary["modifyAssessment"] = msg
                else:
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "assessment", projectid=projectid
                        )
                    )
            new_available = is_assessment_final(
                self.request, self.user.login, projectid, assessmentid
            )
            if not new_available:
                new_available = not there_is_final_assessment(
                    self.request, self.user.login, projectid
                )
            return {
                "new_available": new_available,
                "activeUser": self.user,
                "projectid": projectid,
                "data": data,
                "error_summary": error_summary,
            }
"""


class deleteassessmenthead_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            data = getProjectAssessmentInfo(
                self.user.login, projectid, assessmentid, self.request
            )
            error_summary = {}
            if self.request.method == "POST":
                error, msg = deleteProjectAssessment(
                    self.user.login, projectid, assessmentid, self.request
                )
                if not error:
                    error_summary["deleteAssessment"] = msg
                    self.returnRawViewResult = True
                    return {"status": 400, "error": msg}
                else:
                    self.returnRawViewResult = True
                    return {"status": 200}
                    # return HTTPFound(location=self.request.route_url('assessment', projectid=projectid))
            return {
                "activeUser": self.user,
                "projectid": projectid,
                "data": data,
                "error_summary": error_summary,
            }


class assessment_view(privateView):
    def processView(self):

        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        error_summary = {}

        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:

            data, finalCloseQst = getDataFormPreview(self, projectid, assessmentid)

            return {
                "activeUser": self.user,
                "data": data,
                "finalCloseQst": finalCloseQst,
                "error_summary": error_summary,
                "projectid": projectid,
                "assessmentid": assessmentid,
                "assinfo": getProjectAssessmentInfo(
                    self.user.login, projectid, assessmentid, self.request
                ),
                "UserQuestion": availableAssessmentQuestions(
                    self.user.login, projectid, assessmentid, self.request
                ),
                "Categories": getCategoriesParents(self.user.login, self.request),
            }


class assessmentFormCreation_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        error_summary = {}

        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "POST":
                newOrder = d = json.loads(self.request.POST.get("neworder", "{}"))
                questionWithoutGroup = False
                for item in newOrder:
                    if item["type"] == "question":
                        questionWithoutGroup = True

                if not questionWithoutGroup:
                    modified, error = saveAssessmentOrder(
                        self.user.login,
                        projectid,
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

                data, finalCloseQst = getDataFormPreview(self, projectid, assessmentid)
                info = {
                    "img1": self.request.url_for_static("landing/odk.png"),
                    "img2": self.request.url_for_static("landing/odk2.png"),
                    "img3": self.request.url_for_static("landing/odk3.png"),
                    "data": data,
                    "_": self._,
                    "showPhone": True,
                }
                render_temp = template.render(info)

                self.returnRawViewResult = True
                return render_temp
        self.returnRawViewResult = True
        return ""


class startAssessments_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        onlyError = False
        error_summary = {}
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "GET":
                # Edited by brandon - > this URL is only for POST
                """redirect = False
                usable_assessments = get_usable_assessments(
                    self.request, self.user.login, projectid
                )
                return {
                    "assessments": usable_assessments,
                    "activeUser": self.user,
                    "projectid": projectid,
                    "error_summary": [],
                    "checkPass": True,
                    "redirect": redirect,
                }"""
                raise HTTPNotFound()

            if self.request.method == "POST":
                data = self.getPostDict()
                assessment_id = data["assessment_id"]
                redirect = False
                print("checkAssessments")
                checkPass, error_summary = checkAssessments(
                    self.user.login, projectid, assessment_id, self.request
                )
                if checkPass:
                    print("generateAssessmentFiles")
                    sectionOfThePackageCode = getTheGroupOfThePackageCodeAssessment(
                        self.user.login, projectid, assessment_id, self.request
                    )
                    correct = generateAssessmentFiles(
                        self.user.login,
                        projectid,
                        assessment_id,
                        self.request,
                        sectionOfThePackageCode,
                    )

                    # Edited by Brandon
                    if correct[0]["result"]:
                        print("setAssessmentIndividualStatus")
                        setAssessmentIndividualStatus(
                            self.user.login, projectid, assessment_id, 1, self.request
                        )
                        # setAssessmentStatus(self.user.login,projectid,1,self.request)
                        # WORKING HERE FOR CREATE THE ASSESSMENT DOCUMENT
                        print("getPackages")
                        ncombs, packages = getPackages(
                            self.user.login, projectid, self.request
                        )
                        print("getDataFormPreview")
                        data, finalCloseQst = getDataFormPreview(
                            self, projectid, assessment_id
                        )
                        print("create_document_form")
                        create_document_form(
                            self.request,
                            "en",
                            self.user.login,
                            projectid,
                            "Assessment",
                            assessment_id,
                            data,
                            packages,
                        )
                        print("Returning")
                        self.returnRawViewResult = True
                        return HTTPFound(location=self.request.route_url("dashboard"))
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
                    "projectid": projectid,
                    "error_summary": error_summary,
                    "checkPass": checkPass,
                    "redirect": redirect,
                    "onlyError": onlyError,
                }


# class cancelAssessment_view(privateView):
#     def processView(self):
#         projectid = self.request.matchdict['projectid']
#         if not projectExists(self.user.login, projectid, self.request):
#             raise HTTPNotFound()
#         redirect = False
#         if self.request.method == 'POST':
#             if 'cancelAssessments' in self.request.params.keys():
#                 setAssessmentStatus(self.user.login, projectid, 0, self.request)
#                 redirect = True
#
#         return {'activeUser': self.user, 'redirect': redirect}


class closeAssessment_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        redirect = False
        progress, pcompleted = getAssesmentProgress(
            self.user.login, projectid, assessmentid, self.request
        )
        assessmentData = getProjectAssessmentInfo(
            self.user.login, projectid, assessmentid, self.request
        )
        if self.request.method == "POST":
            if "closeAssessment" in self.request.params.keys():
                setAssessmentIndividualStatus(
                    self.user.login, projectid, assessmentid, 2, self.request
                )
                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("dashboard"))

        return {
            "activeUser": self.user,
            "redirect": redirect,
            "progress": progress,
            "assessmentData": assessmentData,
        }


class CancelAssessmentView(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        redirect = False
        progress, pcompleted = getAssesmentProgress(
            self.user.login, projectid, assessmentid, self.request
        )
        assessmentData = getProjectAssessmentInfo(
            self.user.login, projectid, assessmentid, self.request
        )
        if self.request.method == "POST":
            if "closeAssessment" in self.request.params.keys():
                setAssessmentIndividualStatus(
                    self.user.login, projectid, assessmentid, 0, self.request
                )
                clean_assessments_error_logs(
                    self.request, projectid, self.user.login, assessmentid
                )
                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("dashboard"))

        return {
            "activeUser": self.user,
            "redirect": redirect,
            "progress": progress,
            "assessmentData": assessmentData,
        }
