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
    getAssessmentQuestions,
    saveAssessmentOrder,
    getAssessmentGroupInformation,
    availableAssessmentQuestions,
    generateAssessmentPreview,
    getProjectAssessments,
    addProjectAssessment,
    getProjectAssessmentInfo,
    modifyProjectAssessment,
    deleteProjectAssessment,
    checkAssessments,
    generateAssessmentFiles,
    setAssessmentStatus,
    getProjectProgress,
    setAssessmentIndividualStatus,
    getAssesmentProgress,
    there_is_final_assessment,
    is_assessment_final,
    get_usable_assessments,
)

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
                                    "The description of the group can not be empty."
                                )
                            }
                    else:
                        error_summary = {
                            "sectionname": self._(
                                "The name of the group can not be empty."
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
                    data["section_color"] = None
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


class newAssessmentQuestion_view(privateView):
    def processView(self):
        # self.needJS("newregistryquestion")
        # self.needCSS("datatables")
        # self.needJS("shuffle")
        # self.needCSS("shuffle")

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


class assessmentEnketo_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        fileid = self.request.matchdict["file"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            data = getProjectAssessmentInfo(
                self.user.login, projectid, assessmentid, self.request
            )
            if data:
                path = os.path.join(
                    self.request.registry.settings["user.repository"],
                    *[self.user.login, projectid, "tmp", fileid]
                )

                if os.path.isfile(path):
                    content_type, content_enc = mimetypes.guess_type(path)
                    fileName = os.path.basename(path)
                    response = FileResponse(
                        path, request=self.request, content_type=content_type
                    )
                    response.content_disposition = (
                        'attachment; filename="' + fileName + '"'
                    )
                    return response
                else:
                    raise HTTPNotFound()
            else:
                raise HTTPNotFound()


class assessmentPreview_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]

        generated, file = generateAssessmentPreview(
            self.user.login, projectid, assessmentid, self.request
        )
        if generated:
            file = os.path.basename(file)
            pathToXML = self.request.route_url(
                "assessmentenketo",
                projectid=projectid,
                assessmentid=assessmentid,
                file=file,
            )
        else:
            pathToXML = ""

        return {
            "activeUser": self.user,
            "pathToXML": pathToXML,
            "projectid": projectid,
            "assessmentid": assessmentid,
        }


class assessmenthead_view(privateView):
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
                "assessments": getProjectAssessments(
                    self.user.login, projectid, self.request
                ),
            }


class newassessmenthead_view(privateView):
    def processView(self):
        # self.needCSS('switch')
        # self.needJS('switch')
        # self.needJS('assessment_form')
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

        # self.needJS("registry")
        # self.needCSS("nestable")
        # self.needCSS("sweet")
        # self.needJS("sweet")
        # self.needJS("delete")

        projectid = self.request.matchdict["projectid"]
        assessmentid = self.request.matchdict["assessmentid"]
        error_summary = {}

        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "POST":
                if "saveorder" in self.request.POST:
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

            data = getAssessmentQuestions(
                self.user.login, projectid, assessmentid, self.request
            )
            # The following is to help jinja2 to render the groups and questions
            # This because the scope constraint makes it difficult to control
            finalCloseQst = ""
            if data:
                sectionID = -99
                grpIndex = -1
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
                        if data[a]["question_reqinasses"] == 1:
                            data[grpIndex]["grpCannotDelete"] = True
                    else:
                        data[a]["hasQuestions"] = False
                finalCloseQst = data[len(data) - 1]["hasQuestions"]

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
            }


class startAssessments_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "GET":
                redirect = False
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
                }
            if self.request.method == "POST":
                data = self.getPostDict()
                assessment_id = data["assessment_id"]
                redirect = False
                checkPass, errors = checkAssessments(
                    self.user.login, projectid, assessment_id, self.request
                )
                if checkPass:
                    generateAssessmentFiles(
                        self.user.login, projectid, assessment_id, self.request
                    )
                    setAssessmentIndividualStatus(
                        self.user.login, projectid, assessment_id, 1, self.request
                    )
                    # setAssessmentStatus(self.user.login,projectid,1,self.request)
                    redirect = True
                return {
                    "activeUser": self.user,
                    "projectid": projectid,
                    "error_summary": errors,
                    "checkPass": checkPass,
                    "redirect": redirect,
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
                redirect = True

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
                redirect = True

        return {
            "activeUser": self.user,
            "redirect": redirect,
            "progress": progress,
            "assessmentData": assessmentData,
        }
