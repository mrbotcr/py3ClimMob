import re

from pyramid.httpexceptions import HTTPNotFound
import validators
from climmob.config.encdecdata import encodeData, decodeData
from climmob.processes import (
    searchEnumerator,
    enumeratorExists,
    addEnumerator,
    deleteEnumerator,
    modifyEnumerator,
    getActiveProject,
    getEnumeratorData,
)
from climmob.views.classes import privateView
import climmob.plugins as p


class getEnumeratorDetails_view(privateView):
    def processView(self):
        if self.request.method == "GET":
            userOwner = self.request.matchdict["user"]
            enumId = self.request.matchdict["enumid"]
            enumerator = getEnumeratorData(userOwner, enumId, self.request)
            self.returnRawViewResult = True
            for plugin in p.PluginImplementations(p.IEnumerator):
                enumerator = plugin.before_returning_context(self.request, enumerator)
            return enumerator
        raise HTTPNotFound


class enumerators_view(privateView):
    def processView(self):
        dataworking = {}
        error_summary = {}
        modify = False

        nextPage = self.request.params.get("next")

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
                    if (
                        validators.email(dataworking["enum_email"])
                        and re.match(r"^[A-Za-z0-9._@-]+$", dataworking["enum_email"])
                        or dataworking["enum_email"] == ""
                    ):
                        continue_add = True
                        message = ""
                        for plugin in p.PluginImplementations(p.IEnumerator):
                            if continue_add:
                                continue_add, message = plugin.before_adding_enumerator(
                                    self.request, self.user.login, dataworking
                                )
                        if continue_add:
                            added, message = addEnumerator(
                                self.user.login, dataworking, self.request
                            )
                            if not added:
                                error_summary = {"dberror": message}
                            else:
                                for plugin in p.PluginImplementations(p.IEnumerator):
                                    plugin.after_adding_enumerator(
                                        self.request, self.user.login, dataworking
                                    )
                                dataworking = {}
                                self.request.session.flash(
                                    self._("The field agent was created successfully.")
                                )
                        else:
                            error_summary = {"dberror": message}
                    else:
                        error_summary = {
                            "invalid_email": self._("The email is invalid.")
                        }
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

                continue_update = True
                message = ""
                for plugin in p.PluginImplementations(p.IEnumerator):
                    if continue_update:
                        continue_update, message = plugin.before_updating_enumerator(
                            self.request, self.user.login, enumeratorid, dataworking
                        )
                if continue_update:
                    mdf, message = modifyEnumerator(
                        self.user.login, enumeratorid, dataworking, self.request
                    )
                    if not mdf:
                        error_summary = {"dberror": message}
                        dataworking["enum_password"] = decodeData(
                            self.request, dataworking["enum_password"]
                        ).decode("utf-8")

                    else:
                        for plugin in p.PluginImplementations(p.IEnumerator):
                            plugin.after_updating_enumerator(
                                self.request, self.user.login, enumeratorid, dataworking
                            )
                        dataworking = {}
                        self.request.session.flash(
                            self._("The field agent was modified successfully.")
                        )
                else:
                    error_summary = {"dberror": message}
                    dataworking["enum_password"] = decodeData(
                        self.request, dataworking["enum_password"]
                    ).decode("utf-8")

        return {
            "activeUser": self.user,
            "activeProject": getActiveProject(self.user.login, self.request),
            "searchEnumerator": searchEnumerator(self.user.login, self.request),
            "dataworking": dataworking,
            "error_summary": error_summary,
            "modify": modify,
            "nextPage": nextPage,
            "sectionActive": "fieldagents",
        }


class deleteEnumerator_view(privateView):
    def processView(self):
        enumeratorid = self.request.matchdict["enumeratorid"]

        if self.request.method == "POST":
            continue_delete = True
            message = ""
            for plugin in p.PluginImplementations(p.IEnumerator):
                if continue_delete:
                    continue_delete, message = plugin.before_deleting_enumerator(
                        self.request, self.user.login, enumeratorid
                    )
            if continue_delete:
                deleted, message = deleteEnumerator(
                    self.user.login, enumeratorid, self.request
                )
                if not deleted:
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    for plugin in p.PluginImplementations(p.IEnumerator):
                        plugin.after_deleting_enumerator(
                            self.request, self.user.login, enumeratorid
                        )
                    self.request.session.flash(
                        self._("The field agent was successfully removed")
                    )
                    self.returnRawViewResult = True
                    return {"status": 200}
            else:
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
