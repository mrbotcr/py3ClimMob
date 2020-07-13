from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from .classes import privateView
import re
from climmob.config.encdecdata import encodeData, decodeData
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
        dataworking = {}
        error_summary = {}
        modify =False

        if self.request.method == "POST":
            dataworking = self.getPostDict()
            if "btn_add_enumerator" in self.request.POST:
                modify =False
                dataworking["enum_id"] = re.sub("[^A-Za-z0-9\-]+", "", dataworking["enum_id"])
                if not enumeratorExists(
                    self.user.login, dataworking["enum_id"], self.request
                ):
                    added, message = addEnumerator(
                        self.user.login, dataworking, self.request
                    )
                    if not added:
                        error_summary = {"dberror": message}
                    else:
                        dataworking ={}
                        self.request.session.flash(
                            self._(
                                "The field agent was created successfully."
                            )
                        )
                else:
                    error_summary = {
                        "exists": self._(
                            "This field agent username already exists."
                        )
                    }

            if "btn_modify_enumerator" in self.request.POST:
                modify = True
                enumeratorid = dataworking["enum_id"]
                dataworking["enum_password"] = encodeData(self.request, dataworking["enum_password"])
                if "ckb_modify_status" in dataworking.keys():
                    if dataworking["ckb_modify_status"] == "on":
                        dataworking["enum_active"] = 1
                    else:
                        dataworking["enum_active"] = 0
                    dataworking.pop("ckb_modify_status")
                else:
                    dataworking["enum_active"] = 0

                mdf, message = modifyEnumerator(
                    self.user.login, enumeratorid, dataworking, self.request
                )

                if not mdf:
                    error_summary = {"dberror": message}
                    dataworking["enum_password"] = decodeData(self.request, dataworking["enum_password"]).decode(
                        "utf-8"
                    )

                else:
                    dataworking = {}
                    self.request.session.flash(
                        self._("The field agent was modified successfully.")
                    )

        return {
            "activeUser": self.user,
            "searchEnumerator": searchEnumerator(self.user.login, self.request),
            "dataworking": dataworking,
            "error_summary": error_summary,
            "modify" :modify
        }


"""class addEnumerator_view(privateView):
    def processView(self):
        error_summary = {}
        newEnumerator = False
        if self.request.method == "POST":
            postdata = self.getPostDict()
            postdata["enum_id"] = re.sub("[^A-Za-z0-9\-]+", "", postdata["enum_id"])
            if not enumeratorExists(
                self.user.login, postdata["enum_id"], self.request
            ):
                added, message = addEnumerator(
                    self.user.login, postdata, self.request
                )
                if not added:
                    error_summary = {"dberror": message}
                else:
                    self.request.session.flash(
                        self._(
                            "The field agent was created successfully."
                        )
                    )
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "enumerators"
                        )
                    )
            else:
                error_summary = {
                    "exists": self._(
                        "This field agent name already exists."
                    )
                }

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
"""
"""
class modifyEnumerator_view(privateView):
    def processView(self):

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

                postdata["enum_password"] = encodeData(self.request, postdata["enum_password"])
                if "ckb_modify_status" in postdata.keys():
                    if postdata["ckb_modify_status"] == "on":
                        postdata["enum_active"] = 1
                    else:
                        postdata["enum_active"] = 0
                    postdata.pop("ckb_modify_status")
                else:
                    postdata["enum_active"] = 0
                    
                mdf, message = modifyEnumerator(
                    self.user.login, enumeratorid, postdata, self.request
                )
                
                if not mdf:
                    error_summary = {"dberror": message}
                    postdata["enum_password"] = decodeData(self.request, postdata["enum_password"]).decode(
                        "utf-8"
                    )

                else:
                    self.request.session.flash(
                        self._("The field agent was modified successfully.")
                    )
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "enumerators"
                        )
                    )

                return {
                    "activeUser": self.user,
                    "dataworking": self.decodeDict(postdata),
                    "error_summary": error_summary,
                    "enumeratorModified": enumeratorModified,
                }
"""

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
