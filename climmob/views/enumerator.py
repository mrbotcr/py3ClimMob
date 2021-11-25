from climmob.views.classes import privateView
import re
from climmob.config.encdecdata import encodeData, decodeData
from climmob.processes import (
    searchEnumerator,
    enumeratorExists,
    addEnumerator,
    deleteEnumerator,
    modifyEnumerator,
    getActiveProject,
)


class enumerators_view(privateView):
    def processView(self):
        dataworking = {}
        error_summary = {}
        modify = False

        if self.request.method == "POST":
            dataworking = self.getPostDict()
            if "btn_add_enumerator" in self.request.POST:
                modify = False
                dataworking["enum_id"] = re.sub(
                    "[^A-Za-z0-9\-]+", "", dataworking["enum_id"]
                )
                if not enumeratorExists(
                    self.user.login, dataworking["enum_id"], self.request
                ):
                    added, message = addEnumerator(
                        self.user.login, dataworking, self.request
                    )
                    if not added:
                        error_summary = {"dberror": message}
                    else:
                        dataworking = {}
                        self.request.session.flash(
                            self._("The field agent was created successfully.")
                        )
                else:
                    error_summary = {
                        "exists": self._("This field agent username already exists.")
                    }

            if "btn_modify_enumerator" in self.request.POST:
                modify = True
                enumeratorid = dataworking["enum_id"]
                dataworking["enum_password"] = encodeData(
                    self.request, dataworking["enum_password"]
                )
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
                    dataworking["enum_password"] = decodeData(
                        self.request, dataworking["enum_password"]
                    ).decode("utf-8")

                else:
                    dataworking = {}
                    self.request.session.flash(
                        self._("The field agent was modified successfully.")
                    )

        return {
            "activeUser": self.user,
            "activeProject": getActiveProject(self.user.login, self.request),
            "searchEnumerator": searchEnumerator(self.user.login, self.request),
            "dataworking": dataworking,
            "error_summary": error_summary,
            "modify": modify,
        }


class deleteEnumerator_view(privateView):
    def processView(self):
        enumeratorid = self.request.matchdict["enumeratorid"]

        if self.request.method == "POST":
            deleted, message = deleteEnumerator(
                self.user.login, enumeratorid, self.request
            )
            if not deleted:
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
            else:
                self.returnRawViewResult = True
                return {"status": 200}
