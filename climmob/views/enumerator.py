from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from .classes import privateView
import re

from ..processes import (
    searchEnumerator,
    enumeratorExists,
    addEnumerator,
    deleteEnumerator,
    isEnumeratorPassword,
    modifyEnumerator,
    getEnumeratorData,
    modifyEnumeratorPassword,
)


class enumerators_view(privateView):
    def processView(self):
        # self.needJS("enulibrary")

        # self.needCSS("sweet")
        # self.needJS("sweet")
        # self.needJS("delete")

        return {
            "activeUser": self.user,
            "searchEnumerator": searchEnumerator(self.user.login, self.request),
        }


class addEnumerator_view(privateView):
    def processView(self):
        error_summary = {}
        newEnumerator = False
        if self.request.method == "POST":
            postdata = self.getPostDict()
            postdata["enum_id"] = re.sub("[^A-Za-z0-9\-]+", "", postdata["enum_id"])
            if postdata["enum_id"] != "":
                if postdata["enum_name"] != "":
                    if postdata["enum_password"] != "":
                        if postdata["enum_password"] == postdata["enum_password_re"]:
                            postdata.pop("enum_password_re")
                            if not enumeratorExists(
                                self.user.login, postdata["enum_id"], self.request
                            ):
                                added, message = addEnumerator(
                                    self.user.login, postdata, self.request
                                )
                                if not added:
                                    error_summary = {"dberror": message}
                                else:
                                    newEnumerator = True
                                    self.request.session.flash(
                                        self._(
                                            "The enumerator was created successfully"
                                        )
                                    )
                            else:
                                error_summary = {
                                    "exists": self._(
                                        "This enumerator name already exists."
                                    )
                                }
                        else:
                            error_summary = {
                                "passworerror": self._(
                                    "The password and its retype are not the same"
                                )
                            }
                    else:
                        error_summary = {
                            "passwordempty": self._(
                                "The password of the enumerator cannot be empty."
                            )
                        }
                else:
                    error_summary = {
                        "nameempty": self._(
                            "The name of the enumerator cannot be empty."
                        )
                    }
            else:
                error_summary = {"userempty": self._("The user name cannot be empty.")}
            return {
                "activeUser": self.user,
                "dataworking": self.decodeDict(postdata),
                "error_summary": error_summary,
                "newEnumerator": newEnumerator,
            }
        else:
            return {
                "activeUser": self.user,
                "dataworking": {},
                "error_summary": error_summary,
                "newEnumerator": newEnumerator,
            }


class modifyEnumerator_view(privateView):
    def processView(self):
        # self.needCSS("bootstrap")
        # self.needCSS("switch")
        # self.needCSS("icheck")

        # self.needJS("jquery")
        # self.needJS("bootstrap")
        # self.needJS("switch")
        # self.needJS("enumerators")

        error_summary = {}
        enumeratorid = self.request.matchdict["enumeratorid"]
        enumeratorModified = False

        if self.request.method == "GET":
            dataworking = getEnumeratorData(self.user.login, enumeratorid, self.request)
            if not dataworking:
                raise HTTPNotFound
            return {
                "activeUser": self.user,
                "dataworking": dataworking,
                "error_summary": error_summary,
                "enumeratorModified": enumeratorModified,
            }
        else:
            if "btn_modify_enumerator" in self.request.POST:
                postdata = self.getPostDict()

                # Remove the password from the data
                if "enum_password" in postdata.keys():
                    postdata.pop("enum_password")

                # Remove the new password from the data
                if "enum_password_new" in postdata.keys():
                    postdata.pop("enum_password_new")

                # Remove the new password from the data
                if "enum_password_new_re" in postdata.keys():
                    postdata.pop("enum_password_new_re")

                if "ckb_modify_status" in postdata.keys():
                    if postdata["ckb_modify_status"] == "on":
                        postdata["enum_active"] = 1
                    else:
                        postdata["enum_active"] = 0
                    postdata.pop("ckb_modify_status")
                else:
                    postdata["enum_active"] = 0
                if postdata["enum_name"] != "":
                    mdf, message = modifyEnumerator(
                        self.user.login, enumeratorid, postdata, self.request
                    )
                    if not mdf:
                        error_summary = {"dberror": message}
                    else:
                        enumeratorModified = True
                        self.request.session.flash(
                            self._("The enumerator was modified successfully")
                        )
                else:
                    error_summary = {
                        "nameempty": self._(
                            "The name of the enumerator cannot be empty."
                        )
                    }

                return {
                    "activeUser": self.user,
                    "dataworking": self.decodeDict(postdata),
                    "error_summary": error_summary,
                    "enumeratorModified": enumeratorModified,
                }

            if "btn_change_password" in self.request.POST:
                postdata = self.getPostDict()
                # if isEnumeratorPassword(self.user.login,enumeratorid,postdata["enum_password"],self.request):
                if postdata["enum_password_new"] != "":
                    if (
                        postdata["enum_password_new"]
                        == postdata["enum_password_new_re"]
                    ):
                        mdf, message = modifyEnumeratorPassword(
                            self.user.login,
                            enumeratorid,
                            postdata["enum_password_new"],
                            self.request,
                        )
                        if mdf:
                            enumeratorModified = True
                            self.request.session.flash(
                                self._("The password was modified successfully")
                            )
                        else:
                            error_summary = {"dberror": message}
                    else:
                        error_summary = {
                            "IncorrectPassword": self._(
                                "The new password and the retype are not the same"
                            )
                        }
                else:
                    error_summary = {
                        "IncorrectPassword": self._("The new password cannot be empty")
                    }
                # else:
                #    error_summary = {'IncorrectPassword': self._("The current password is incorrect.")}

                return {
                    "activeUser": self.user,
                    "dataworking": getEnumeratorData(
                        self.user.login, enumeratorid, self.request
                    ),
                    "error_summary": error_summary,
                    "enumeratorModified": enumeratorModified,
                }


class deleteEnumerator_view(privateView):
    def processView(self):
        enumeratorid = self.request.matchdict["enumeratorid"]
        error_summary = {}
        dataworking = getEnumeratorData(self.user.login, enumeratorid, self.request)
        enumeratorDeleted = False

        if self.request.method == "POST":
            deleted, message = deleteEnumerator(
                self.user.login, enumeratorid, self.request
            )
            if not deleted:
                error_summary = {"dberror": message}
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
            else:
                self.returnRawViewResult = True
                return {"status": 200}

                # enumeratorDeleted = True
                # self.request.session.flash('The enumerator was deleted successfully')
        # return {'activeUser': self.user, 'error_summary': error_summary, 'dataworking':dataworking,'enumeratorDeleted':enumeratorDeleted}
