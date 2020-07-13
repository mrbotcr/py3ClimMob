from pyramid.httpexceptions import HTTPFound
from .classes import privateView

from ..processes import (
    getUserTechs,
    findTechInLibrary,
    addTechnology,
    getTechnology,
    updateTechnology,
    deleteTechnology,
    getUserTechById
)

from .techaliases import newalias_view, modifyalias_view


class technologies_view(privateView):
    def processView(self):
        dataworking = {}
        error_summary = {}
        error_summary_options = {}
        action = ""
        techSee ={}
        #alias = {}

        if self.request.method == "POST":
            if "btn_add_technology" in self.request.POST:
                dict_return = newtechnology_view.processView(self)
                dataworking = dict_return["formdata"]
                error_summary =dict_return["error_summary"]
                if not dict_return["redirect"]:
                    action = "addTechnology"

            if "btn_modify_technology" in self.request.POST:
                dataworking= self.getPostDict()
                self.request.matchdict["technologyid"] = dataworking["tech_id"]
                dict_return = modifytechnology_view.processView(self)
                dataworking = dict_return["formdata"]
                error_summary =dict_return["error_summary"]
                techSee = getUserTechById(dataworking["tech_id"], self.request)
                if not dict_return["redirect"]:
                    action = "modifyTechnology"

            if "btn_add_alias" in self.request.POST:
                dataworking = self.getPostDict()
                self.request.matchdict["technologyid"] = dataworking["tech_id"]
                dict_return = newalias_view.processView(self)
                dataworking["alias_name_insert"] = dict_return["formdata"]["alias_name"]
                error_summary_options = dict_return["error_summary"]
                techSee = getUserTechById(dataworking["tech_id"],self.request)

            if "btn_modify_alias" in self.request.POST:

                dataworking = self.getPostDict()
                self.request.matchdict["technologyid"] = dataworking["tech_id"]
                self.request.matchdict["aliasid"] = dataworking["alias_id"]
                dict_return = modifyalias_view.processView(self)
                error_summary_options = dict_return["error_summary"]
                techSee = getUserTechById(dataworking["tech_id"], self.request)

            if "btn_add_technology" not in self.request.POST and "btn_modify_technology" not in self.request.POST and "btn_add_alias" not in self.request.POST and "btn_modify_alias" not in self.request.POST:
                dataworking = self.getPostDict()
                techSee = getUserTechById(dataworking["tech_id"], self.request)


        return {
            "activeUser": self.user,
            "dataworking": dataworking,
            "error_summary": error_summary,
            "error_summary_options": error_summary_options,
            "UserTechs": getUserTechs(self.user.login, self.request),
            "ClimMobTechs": getUserTechs("bioversity", self.request),
            "action": action,
            "techSee": techSee
            #"alias": alias
        }

class newtechnology_view(privateView):
    def processView(self):
        error_summary = {}
        formdata = {}
        redirect = False
        formdata["tech_name"] = ""
        if self.request.method == "POST":
            if "btn_add_technology" in self.request.POST:
                formdata = self.getPostDict()
                del formdata["tech_id"]
                formdata["user_name"] = self.user.login
                if formdata["tech_name"] != "":

                    formdata["user_name"] = "bioversity"
                    existInGenLibrary = findTechInLibrary(formdata, self.request)
                    if existInGenLibrary == False:

                        formdata["user_name"] = self.user.login
                        existInPersLibrary = findTechInLibrary(formdata, self.request)
                        if existInPersLibrary == False:
                            formdata["user_name"] = self.user.login
                            added, message = addTechnology(formdata, self.request)
                            if not added:
                                error_summary = {"dberror": message}
                            else:
                                redirect = True
                        else:
                            error_summary = {
                                "exists": self._(
                                    "This technology already exists in your personal library"
                                )
                            }
                    else:
                        error_summary = {
                            "exists": self._(
                                "This technology already exists in the generic library"
                            )
                        }
                else:
                    error_summary = {
                        "nameempty": self._("You need to set values for the name")
                    }

        if redirect:
            self.request.session.flash(self._("The technology was added successfully"))

        return {
            "activeUser": self.user,
            "error_summary": error_summary,
            "redirect": redirect,
            "formdata": self.decodeDict(formdata),
        }


class modifytechnology_view(privateView):
    def processView(self):
        formdata = {}
        formdata["tech_id"] = self.request.matchdict["technologyid"]
        data = getTechnology(formdata, self.request)
        if self.request.method == "GET":
            if not bool(data):
                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("usertechnologies"))

        error_summary = {}
        redirect = False

        formdata["tech_name"] = data["tech_name"]

        if self.request.method == "POST":
            if "btn_modify_technology" in self.request.POST:

                formdata = self.getPostDict()
                formdata["user_name"] = self.user.login
                formdata["tech_id"] = self.request.matchdict["technologyid"]

                if formdata["tech_name"] != "":

                    formdata["user_name"] = "bioversity"
                    existInGenLibrary = findTechInLibrary(formdata, self.request)
                    if existInGenLibrary == False:

                        formdata["user_name"] = self.user.login
                        existInPersLibrary = findTechInLibrary(formdata, self.request)
                        if existInPersLibrary == False:
                            formdata["user_name"] = self.user.login
                            update, message = updateTechnology(formdata, self.request)
                            if not update:
                                error_summary = {"dberror": message}
                            else:
                                redirect = True
                        else:
                            error_summary = {
                                "exists": self._(
                                    "This technology already exists in your personal library"
                                )
                            }
                    else:
                        error_summary = {
                            "exists": self._(
                                "This technology already exists in the generic library"
                            )
                        }
                else:
                    error_summary = {
                        "nameempty": self._("You need to set values for the name")
                    }

        if redirect:
            self.request.session.flash(
                self._("The technology was modified successfully")
            )

        return {
            "activeUser": self.user,
            "error_summary": error_summary,
            "redirect": redirect,
            "formdata": self.decodeDict(formdata),
        }


class deletetechnology_view(privateView):
    def processView(self):
        formdata = {}
        formdata["user_name"] = self.user.login
        formdata["tech_id"] = self.request.matchdict["technologyid"]
        data = getTechnology(formdata, self.request)

        if self.request.method == "GET":
            if data is None:
                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("usertechnologies"))

        formdata["tech_name"] = data["tech_name"]
        error_summary = {}
        redirect = False

        if self.request.method == "POST":

            dlt, message = deleteTechnology(formdata, self.request)

            if not dlt:
                error_summary = {"dberror": message}
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
            else:
                self.returnRawViewResult = True
                return {"status": 200}

        if redirect:
            self.request.session.flash(
                self._("The technology was deleted successfully")
            )

        return {
            "activeUser": self.user,
            "error_summary": error_summary,
            "redirect": redirect,
            "formdata": formdata,
        }
