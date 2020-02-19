from .classes import privateView
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import json, os
from ..processes import QuestionsOptions, projectExists, getCategories
from ..processes import (
    addRegistryGroup,
    addRegistryQuestionToGroup,
    deleteRegistryGroup,
    modifyRegistryGroup,
    getRegistryGroupData,
    getRegistryQuestions,
    saveRegistryOrder,
    getRegistryGroupInformation,
    availableRegistryQuestions,
    generateRegistryPreview,
    setRegistryStatus,
    getProjectProgress,
)
from climmob.products import stopTasksByProcess
from pyramid.response import FileResponse
import mimetypes


class modifyRegistrySection_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        groupid = self.request.matchdict["groupid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            error_summary = {}
            data = {}
            data["project_cod"] = projectid
            data["group_cod"] = groupid
            data["user_name"] = self.user.login

            if self.request.method == "POST":
                if "btn_modify_group" in self.request.POST:
                    tdata = self.getPostDict()
                    data["section_name"] = tdata["section_name"]
                    data["section_content"] = tdata["section_content"]

                    if data["section_name"] != "":
                        if data["section_content"] != "":

                            mdf, message = modifyRegistryGroup(data, self)
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
                                        "registry", projectid=projectid
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
                groupData = getRegistryGroupData(data, self)
                data["section_name"] = groupData["section_name"]
                data["section_content"] = groupData["section_content"]
            return {
                "activeUser": self.user,
                "projectid": projectid,
                "data": self.decodeDict(data),
                "error_summary": error_summary,
            }


class deleteRegistrySection_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        groupid = self.request.matchdict["groupid"]
        error_summary = {}
        data = projectExists(self.user.login, projectid, self.request)

        if not data:
            raise HTTPNotFound()
        else:
            data = getRegistryGroupInformation(
                self.user.login, projectid, groupid, self.request
            )
            if self.request.method == "POST":
                deleted, message = deleteRegistryGroup(
                    self.user.login, projectid, groupid, self.request
                )
                if not deleted:
                    error_summary = {"dberror": message}
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    self.returnRawViewResult = True
                    return {"status": 200}
                    # return HTTPFound(location=self.request.route_url('registry',projectid=projectid))

        return {
            "activeUser": self.user,
            "projectid": projectid,
            "data": data,
            "error_summary": error_summary,
            "groupid": groupid,
        }


class newRegistrySection_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        error_summary = {}
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            data = {}
            data["user_name"] = self.user.login
            data["project_cod"] = projectid
            if self.request.method == "POST":
                if "btn_add_group" in self.request.POST:
                    tdata = self.getPostDict()
                    data["section_name"] = tdata["section_name"]
                    data["section_content"] = tdata["section_content"]
                    data["section_color"] = None
                    if data["section_name"] != "":
                        if data["section_content"] != "":
                            addgroup, message = addRegistryGroup(data, self)

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
                                        "registry", projectid=projectid
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
                                "The name of the group can not be empty."
                            )
                        }

            return {
                "activeUser": self.user,
                "projectid": projectid,
                "data": self.decodeDict(data),
                "error_summary": error_summary,
            }


class newRegistryQuestion_view(privateView):
    def processView(self):
        # self.needJS("newregistryquestion")
        # self.needCSS("datatables")
        # self.needJS("shuffle")
        # self.needCSS("shuffle")

        projectid = self.request.matchdict["projectid"]
        groupid = self.request.matchdict["groupid"]

        data = {}
        data["project_cod"] = projectid
        data["section_id"] = groupid
        data["group_cod"] = groupid
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
                            addq, message = addRegistryQuestionToGroup(
                                data, self.request
                            )
                            if not addq:
                                error = True
                    if not error:
                        self.returnRawViewResult = True
                        return HTTPFound(
                            location=self.request.route_url(
                                "registry", projectid=projectid
                            )
                        )

            return {
                "activeUser": self.user,
                "UserQuestion": availableRegistryQuestions(
                    self.user.login, projectid, self.request
                ),
                "QuestionsOptions": QuestionsOptions(self.user.login, self.request),
                "projectid": projectid,
                "groupInfo": getRegistryGroupData(data, self),
                "Categories": getCategories(self.user.login, self.request),
            }


class registryEnketo_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        fileid = self.request.matchdict["file"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
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
                response.content_disposition = 'attachment; filename="' + fileName + '"'
                return response
            else:
                raise HTTPNotFound()


class registryPreview_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
            generated, file = generateRegistryPreview(
                self.user.login, projectid, self.request
            )
            if generated:
                file = os.path.basename(file)
                pathToXML = self.request.route_url(
                    "registryenketo", projectid=projectid, file=file
                )
            else:
                pathToXML = ""
        return {"activeUser": self.user, "pathToXML": pathToXML, "projectid": projectid}


class cancelRegistry_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        redirect = False
        if self.request.method == "POST":
            if "cancelRegistry" in self.request.params.keys():
                setRegistryStatus(self.user.login, projectid, 0, self.request)
                redirect = True

                stopTasksByProcess(self.request, self.user.login, projectid)

        return {"activeUser": self.user, "redirect": redirect}


class closeRegistry_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        redirect = False
        progress, pcompleted = getProjectProgress(
            self.user.login, projectid, self.request
        )
        if self.request.method == "POST":
            if "closeRegistry" in self.request.params.keys():
                setRegistryStatus(self.user.login, projectid, 2, self.request)
                redirect = True

        return {"activeUser": self.user, "redirect": redirect, "progress": progress}


class registry_view(privateView):
    def processView(self):

        # self.needJS("registry")
        # self.needCSS("nestable")
        # self.needCSS("sweet")
        # self.needJS("sweet")
        # self.needJS("delete")

        projectid = self.request.matchdict["projectid"]
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
                        modified, error = saveRegistryOrder(
                            self.user.login, projectid, newOrder, self.request
                        )
                    else:
                        error_summary["questionWithoutGroup"] = self._(
                            "Questions cannot be outside a group"
                        )

            data = getRegistryQuestions(self.user.login, projectid, self.request)
            # The following is to help jinja2 to render the groups and questions
            # This because the scope constraint makes it difficult to control
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
                    if data[a]["question_reqinreg"] == 1:
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
            }
            # return {'finalCloseQst':finalCloseQst,'found':False,'activeUser':self.user,'Project':projectid, 'error_summary':error_summary,'saveordergroup':saveordergroup,'saveorderquestions':saveorderquestions, 'UserGroups':UserGroups(self.user.login,projectid,self), 'Prj_UserQuestion':Prj_UserQuestion(self.user.login, projectid,self), 'accordion_open':accordion_open, 'data':data, 'archive':projectid.replace(" ", "_")+"_"+self._("registry")+".xml"}
