# -*- coding: utf-8 -*-

from .classes import privateView
from ..processes import (
    addQuestion,
    addOptionToQuestion,
    updateQuestion,
    deleteQuestion,
    UserQuestion,
    UserQuestionMoreBioversity,
    deleteAllOptionsForQuestion,
    QuestionsOptions,
    getQuestionData,
    getQuestionOptions,
    deleteOption,
    optionExists,
    getOptionData,
    updateOption,
    questionExists,
    categoryExists,
    addCategory,
    getCategories,
    updateCategory,
    deleteCategory,
    getCategoriesParents,
)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
import re
import json


class deleteQuestion_view(privateView):
    def processView(self):
        qid = self.request.matchdict["qid"]
        questionData, editable = getQuestionData(self.user.login, qid, self.request)
        if not questionData or not editable:
            return HTTPNotFound
        if self.request.method == "GET":
            if not questionData:
                raise HTTPNotFound()
        questionDesc = questionData["question_desc"]

        error_summary = {}
        formdata = {}
        redirect = False
        # if 'btn_delete_question' in self.request.POST:
        if self.request.method == "POST":
            formdata["question_id"] = qid
            dlt, message = deleteQuestion(formdata, self.request)

            if not dlt:
                error_summary = {"dberror": message}
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
            else:
                self.returnRawViewResult = True
                return {"status": 200}


class modifyQuestion_view(privateView):
    def processView(self):
        qid = self.request.matchdict["qid"]
        error_summary = {}
        redirect = False
        formdata, editable = getQuestionData(self.user.login, qid, self.request)
        if not formdata or not editable:
            raise HTTPNotFound()

        """if formdata["question_alwaysinreg"] == 1:
            formdata["question_alwaysinreg"] = "on"
        else:
            formdata["question_alwaysinreg"] = "off"

        if formdata["question_alwaysinasse"] == 1:
            formdata["question_alwaysinasse"] = "on"
        else:
            formdata["question_alwaysinasse"] = "off"
        """
        if formdata["question_requiredvalue"] == 1:
            formdata["question_requiredvalue"] = "on"
        else:
            formdata["question_requiredvalue"] = "off"

        if self.request.method == "POST":
            formdata = self.getPostDict()
            formdata["question_dtype"] = int(formdata["question_dtype"])
            formdata["user_name"] = self.user.login
            formdata["question_id"] = qid

            try:
                category = formdata["question_group"].split("[*$%&]")
                formdata["qstgroups_id"] = category[0]
                formdata["qstgroups_user"] = category[1]
            except:
                formdata["qstgroups_id"] = None
                formdata["qstgroups_user"] = None

            """if "question_alwaysinreg" in formdata.keys():
                formdata["question_alwaysinreg"] = 1
            else:
                formdata["question_alwaysinreg"] = 0

            if "question_alwaysinasse" in formdata.keys():
                formdata["question_alwaysinasse"] = 1
            else:
                formdata["question_alwaysinasse"] = 0
            """

            if "question_requiredvalue" in formdata.keys():
                formdata["question_requiredvalue"] = 1
            else:
                formdata["question_requiredvalue"] = 0

            if formdata["question_desc"] != "" and formdata["question_dtype"] != "":
                updated, idorerror = updateQuestion(formdata, self.request)
                if not updated:

                    if formdata["question_requiredvalue"] == 1:
                        formdata["question_requiredvalue"] = "on"
                    else:
                        formdata["question_requiredvalue"] = "off"

                    error_summary = {"dberror": idorerror}
                else:
                    self.request.session.flash(
                        self._("The question was successfully modified")
                    )
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "qlibrary", user_name=self.user.login
                        )
                    )
            else:
                """
                if formdata["question_alwaysinreg"] == 1:
                    formdata["question_alwaysinreg"] = "on"
                else:
                    formdata["question_alwaysinreg"] = "off"

                if formdata["question_alwaysinasse"] == 1:
                    formdata["question_alwaysinasse"] = "on"
                else:
                    formdata["question_alwaysinasse"] = "off"
                """
                if formdata["question_requiredvalue"] == 1:
                    formdata["question_requiredvalue"] = "on"
                else:
                    formdata["question_requiredvalue"] = "off"

                error_summary = {"questionempty": self._("Incomplete information.")}

        return {
            "activeUser": self.user,
            "error_summary": error_summary,
            "formdata": self.decodeDict(formdata),
            "redirect": redirect,
            "Categories": getCategories(self.user.login, self.request),
        }


class deleteQuestionValue_view(privateView):
    def processView(self):
        qid = self.request.matchdict["qid"]
        valueid = self.request.matchdict["valueid"]
        qdata, editable = getQuestionData(self.user.login, qid, self.request)
        if not qdata or not editable:
            raise HTTPNotFound()

        error_summary = {}
        formdata = {}
        if self.request.method == "GET":
            formdata = getOptionData(qid, valueid, self.request)
        if self.request.method == "POST":
            deleted, msg = deleteOption(qid, valueid, self.request)
            if deleted:
                self.returnRawViewResult = True
                return {"status": 200}
                # return HTTPFound(location=self.request.route_url('questionvalues', qid=qid))
            else:
                error_summary = {"dberror": msg}
                self.returnRawViewResult = True
                return {"status": 400, "error": msg}

        return {
            "activeUser": self.user,
            "qdata": qdata,
            "qid": qid,
            "formdata": formdata,
            "error_summary": error_summary,
        }


class modifyQuestionValue_view(privateView):
    def processView(self):
        qid = self.request.matchdict["qid"]
        valueid = self.request.matchdict["valueid"]
        qdata, editable = getQuestionData(self.user.login, qid, self.request)
        if not qdata or not editable:
            raise HTTPNotFound()

        error_summary = {}
        formdata = {}
        if self.request.method == "GET":
            formdata = getOptionData(qid, valueid, self.request)
        if self.request.method == "POST":
            formdata = self.getPostDict()
            formdata["question_id"] = qid
            formdata["value_code"] = valueid
            if "ckb_other" in formdata.keys():
                formdata["value_isother"] = 1
            else:
                formdata["value_isother"] = 0

            if "ckb_na" in formdata.keys():
                formdata["value_isna"] = 1
            else:
                formdata["value_isna"] = 0

            updated, resp = updateOption(formdata, self.request)
            if updated:
                self.returnRawViewResult = True
                return HTTPFound(
                    location=self.request.route_url("questionvalues", qid=qid)
                )
            else:
                error_summary = {"dberror": resp}

        if formdata["value_isna"] == 1:
            formdata["value_isna"] = "on"
        else:
            formdata["value_isna"] = "off"

        if formdata["value_isother"] == 1:
            formdata["value_isother"] = "on"
        else:
            formdata["value_isother"] = "off"

        return {
            "activeUser": self.user,
            "qdata": qdata,
            "qid": qid,
            "formdata": self.decodeDict(formdata),
            "error_summary": error_summary,
        }


class addQuestionValue_view(privateView):
    def processView(self):
        qid = self.request.matchdict["qid"]
        qdata, editable = getQuestionData(self.user.login, qid, self.request)
        if not qdata or not editable:
            raise HTTPNotFound()
        formdata = {}

        error_summary = {}
        if self.request.method == "GET":
            formdata["value_code"] = ""
            formdata["value_desc"] = ""
            formdata["value_isother"] = "off"
            formdata["value_isna"] = "off"
        if self.request.method == "POST":
            formdata = self.getPostDict()
            formdata["question_id"] = qid

            formdata["value_code"] = re.sub(
                "[^A-Za-z0-9\-]+", "", formdata["value_code"]
            )
            if formdata["value_code"] != "" and formdata["value_desc"] != "":

                if "ckb_other" in formdata.keys():
                    formdata["value_isother"] = 1
                else:
                    formdata["value_isother"] = 0

                if "ckb_na" in formdata.keys():
                    formdata["value_isna"] = 1
                else:
                    formdata["value_isna"] = 0
                if not optionExists(qid, formdata["value_code"], self.request):
                    addded, resp = addOptionToQuestion(formdata, self.request)
                    if addded:
                        self.returnRawViewResult = True
                        return HTTPFound(
                            location=self.request.route_url("questionvalues", qid=qid)
                        )
                    else:
                        error_summary = {"dberror": resp}
                else:
                    error_summary = {"dberror": self._("Option already exists")}
            else:
                error_summary = {"empty": self._("Both code and label cannot be empty")}

        if formdata["value_isna"] == 1:
            formdata["value_isna"] = "on"
        else:
            formdata["value_isna"] = "off"

        if formdata["value_isother"] == 1:
            formdata["value_isother"] = "on"
        else:
            formdata["value_isother"] = "off"

        return {
            "activeUser": self.user,
            "qdata": qdata,
            "qid": qid,
            "formdata": self.decodeDict(formdata),
            "error_summary": error_summary,
        }


class questionValues_view(privateView):
    def processView(self):
        qid = self.request.matchdict["qid"]
        qdata, editable = getQuestionData(self.user.login, qid, self.request)
        if qdata:
            if qdata["question_dtype"] == 5 or qdata["question_dtype"] == 6:
                qoptions = getQuestionOptions(qid, self.request)

                return {
                    "activeUser": self.user,
                    "qdata": qdata,
                    "qoptions": qoptions,
                    "qid": qid,
                    "editable": editable,
                }
            else:
                raise HTTPNotFound()
        else:
            raise HTTPNotFound()


class questionPerformance_view(privateView):
    def processView(self):
        qid = self.request.matchdict["qid"]
        qdata, editable = getQuestionData(self.user.login, qid, self.request)
        if not qdata:
            raise HTTPNotFound()
        if qdata["question_dtype"] == 10:
            error_summary = {}
            redirect = False
            withtoastr = False
            if "withtoastr" in self.request.params.keys():
                withtoastr = True
            if self.request.method == "GET":
                if qdata["question_perfstmt"] is None:
                    qdata["question_perfstmt"] = ""
                return {
                    "activeUser": self.user,
                    "qdata": qdata,
                    "qid": qid,
                    "error_summary": error_summary,
                    "redirect": redirect,
                    "withtoastr": withtoastr,
                    "editable": editable,
                }
            if self.request.method == "POST":
                if not editable:
                    raise HTTPNotFound()
                formdata = self.getPostDict()
                formdata["question_id"] = qid
                formdata["user_name"] = self.user.login
                perstmt = formdata["question_perfstmt"].replace(" ", "")
                if perstmt.find("{{option}}") >= 0:
                    modified, msg = updateQuestion(formdata, self.request)
                    if modified:
                        if withtoastr:
                            self.request.session.flash(
                                self._("The question was successfully added")
                            )
                        else:
                            self.request.session.flash(
                                self._(
                                    "You successfully updated the performance statement."
                                )
                            )
                        redirect = True
                    else:
                        error_summary = {"dberror": msg}
                else:
                    error_summary["stmterror"] = self._(
                        "The performance statement must have the wildcard {{option}}"
                    )
                return {
                    "activeUser": self.user,
                    "qdata": self.decodeDict(qdata),
                    "qid": qid,
                    "error_summary": error_summary,
                    "redirect": redirect,
                    "withtoastr": withtoastr,
                    "editable": editable,
                }
        else:
            raise HTTPNotFound()


class questionCharacteristics_view(privateView):
    def processView(self):
        qid = self.request.matchdict["qid"]
        qdata, editable = getQuestionData(self.user.login, qid, self.request)
        if not qdata:
            raise HTTPNotFound()
        if qdata["question_dtype"] == 9:
            error_summary = {}
            redirect = False
            withtoastr = False
            if "withtoastr" in self.request.params.keys():
                withtoastr = True
            if self.request.method == "GET":
                if qdata["question_posstm"] is None:
                    qdata["question_posstm"] = ""
                if qdata["question_negstm"] is None:
                    qdata["question_negstm"] = ""
                return {
                    "activeUser": self.user,
                    "qdata": qdata,
                    "qid": qid,
                    "error_summary": error_summary,
                    "redirect": redirect,
                    "withtoastr": withtoastr,
                    "editable": editable,
                }
            if self.request.method == "POST":
                if not editable:
                    raise HTTPNotFound()
                formdata = self.getPostDict()
                formdata["question_id"] = qid
                formdata["user_name"] = self.user.login

                modified, msg = updateQuestion(formdata, self.request)
                if modified:
                    if withtoastr:
                        self.request.session.flash(
                            self._("The question was successfully added")
                        )
                    else:
                        self.request.session.flash(
                            self._("You successfully updated the characteristic.")
                        )
                    redirect = True
                else:
                    error_summary = {"dberror": msg}
                qdata["question_posstm"] = formdata["question_posstm"]
                qdata["question_negstm"] = formdata["question_negstm"]

                return {
                    "activeUser": self.user,
                    "qdata": self.decodeDict(qdata),
                    "qid": qid,
                    "error_summary": error_summary,
                    "redirect": redirect,
                    "withtoastr": withtoastr,
                    "editable": editable,
                }
        else:
            raise HTTPNotFound()


class newQuestion_view(privateView):
    def processView(self):
        return {}


def actionsInquestion(self, formdata):

    if "question_id" in formdata.keys():
        deleteAllOptionsForQuestion(formdata["question_id"], self.request)

    if formdata["question_posstm"] == "" or formdata["question_posstm"] == "None":
        formdata["question_posstm"] = None

    if formdata["question_negstm"] == "" or formdata["question_negstm"] == "None":
        formdata["question_negstm"] = None

    if formdata["question_perfstmt"] == "" or formdata["question_perfstmt"] == "None":
        formdata["question_perfstmt"] = None

    formdata["question_dtype"] = int(formdata["question_dtype"])
    formdata["user_name"] = self.user.login
    formdata["question_code"] = re.sub("[^A-Za-z0-9\-]+", "", formdata["question_code"])

    try:
        category = formdata["question_group"].split("[*$%&]")
        formdata["qstgroups_id"] = category[0]
        formdata["qstgroups_user"] = category[1]
    except:
        formdata["qstgroups_id"] = None
        formdata["qstgroups_user"] = None

    if int(formdata["question_dtype"]) == 9 or int(formdata["question_dtype"]) == 10:
        formdata["question_alwaysinreg"] = 0

    if int(formdata["question_dtype"]) == 10:
        perstmt = formdata["question_perfstmt"].replace(" ", "")
        if perstmt.find("{{option}}") < 0:
            return {
                "result": "error",
                "error": self._(
                    "The performance statement must have the wildcard {{option}}"
                ),
            }

    if (
        formdata["question_code"] != ""
        and formdata["question_desc"] != ""
        and formdata["question_dtype"] != ""
    ):
        if not questionExists(self.user.login, formdata["question_code"], self.request):
            if formdata["action"] == "insert":
                add, idorerror = addQuestion(formdata, self.request)
                if not add:
                    return {"result": "error", "error": idorerror}
                else:

                    if (
                        int(formdata["question_dtype"]) == 5
                        or int(formdata["question_dtype"]) == 6
                    ):
                        optionValues = json.loads(formdata["optionsValues"])
                        cont = 1
                        for option in optionValues:
                            option["question_id"] = idorerror
                            option["value_code"] = cont
                            cont = cont + 1
                            addded, resp = addOptionToQuestion(option, self.request)
                            if not addded:
                                return {"result": "error", "error": resp}

                    return {
                        "result": "success",
                        "success": self._("The question was successfully added"),
                    }
        else:
            if formdata["action"] == "update":
                updated, idorerror = updateQuestion(formdata, self.request)
                if not updated:
                    return {"result": "error", "error": idorerror}
                else:

                    if (
                        int(formdata["question_dtype"]) == 5
                        or int(formdata["question_dtype"]) == 6
                    ):
                        optionValues = json.loads(formdata["optionsValues"])
                        cont = 1
                        for option in optionValues:
                            option["question_id"] = idorerror
                            option["value_code"] = cont
                            cont = cont + 1
                            addded, resp = addOptionToQuestion(option, self.request)
                            if not addded:
                                return {"result": "error", "error": resp}
                    return {
                        "result": "success",
                        "success": self._("The question was successfully modified"),
                    }
            else:
                return {
                    "result": "error",
                    "error": self._("There is another question with the same code."),
                }
    else:
        return {"result": "error", "error": self._("Incomplete information.")}


class questionsActions_view(privateView):
    def processView(self):

        if self.request.method == "POST":
            postdata = self.getPostDict()
            self.returnRawViewResult = True

            if postdata["action"] == "btn_add_question":
                del postdata["question_id"]
                postdata["action"] = "insert"

            if postdata["action"] == "btn_update_question":
                postdata["action"] = "update"

            return actionsInquestion(self, postdata)

        return {}


class qlibrary_view(privateView):
    def processView(self):

        user_name = self.request.matchdict["user_name"]

        regularDict = {
            "UserQuestion": UserQuestionMoreBioversity(user_name, self.request),
            "showing": user_name,
            # "QuestionsOptions": QuestionsOptions(self.user.login, self.request),
            # "ClimMobQuestionsOptions": QuestionsOptions("bioversity", self.request),
            "Categories": getCategoriesParents(self.user.login, self.request),
            # "editable": True,
            "allCategories": getCategories(user_name, self.request),
        }

        return regularDict


import uuid


class categories_view(privateView):
    def processView(self):
        error_summary = {}
        if self.request.method == "POST":
            postdata = self.getPostDict()
            if postdata["action"] == "new":
                postdata["qstgroups_id"] = str(uuid.uuid4())[-12:]
                if not categoryExists(
                    self.user.login, postdata["qstgroups_name"], self.request
                ):
                    added, message = addCategory(
                        self.user.login, postdata, self.request
                    )
                    if not added:
                        self.returnRawViewResult = True
                        return {
                            "result": "error",
                            "error": self._("Could not create category"),
                        }
                    else:
                        self.returnRawViewResult = True
                        return {
                            "result": "success",
                            "success": self._("The category was created successfully"),
                        }
                else:
                    self.returnRawViewResult = True
                    return {
                        "result": "error",
                        "error": self._("This category name already exists."),
                    }
            else:
                if postdata["action"] == "update":
                    if not categoryExists(
                        self.user.login, postdata["qstgroups_name"], self.request
                    ):
                        update, message = updateCategory(
                            self.user.login, postdata, self.request
                        )
                        if not update:
                            self.returnRawViewResult = True
                            return {
                                "result": "error",
                                "error": self._("Could not update the category"),
                            }
                        else:
                            self.returnRawViewResult = True
                            return {
                                "result": "success",
                                "success": self._(
                                    "The category was updated successfully"
                                ),
                            }
                    else:
                        self.returnRawViewResult = True
                        return {
                            "result": "error",
                            "error": self._("This category name already exists."),
                        }
                else:
                    if postdata["action"] == "delete":
                        deleted, message = deleteCategory(
                            self.user.login, postdata["qstgroups_id"], self.request
                        )
                        if not deleted:
                            self.returnRawViewResult = True
                            return {
                                "result": "error",
                                "error": self._("Could not delete the category"),
                            }
                        else:
                            self.returnRawViewResult = True
                            return {
                                "result": "success",
                                "success": self._(
                                    "The category was deleted successfully"
                                ),
                            }
        return {}
