from pyramid.httpexceptions import HTTPFound, HTTPNotFound
import paginate
from climmob.processes import (
    getUserTechs,
    findTechInLibrary,
    addTechnology,
    getTechnology,
    updateTechnology,
    deleteTechnology,
    getUserTechById,
    getActiveProject,
    getTechnologyByName,
    query_crops,
)
from climmob.views.classes import privateView, publicView
from climmob.views.techaliases import newalias_view, modifyalias_view


class getUserTechnologyDetails_view(privateView):
    def processView(self):

        if self.request.method == "GET":
            userOwner = self.request.matchdict["user"]
            techId = self.request.matchdict["technologyid"]
            technology = getUserTechById(techId, self.request)
            self.returnRawViewResult = True

            return technology

        raise HTTPNotFound


class getUserTechnologyAliasDetails_view(privateView):
    def processView(self):

        if self.request.method == "GET":
            userOwner = self.request.matchdict["user"]
            techId = self.request.matchdict["technologyid"]
            aliasId = self.request.matchdict["aliasid"]
            technology = getUserTechById(techId, self.request)
            self.returnRawViewResult = True

            for alias in technology["tech_alias"]:
                if alias["alias_id"] == int(aliasId):
                    return alias

        raise HTTPNotFound


class technologies_view(privateView):
    def processView(self):
        dataworking = {}
        error_summary = {}
        error_summary_add = {}
        error_summary_options = {}
        action = ""
        techSee = {}
        # alias = {}

        nextPage = self.request.params.get("next")

        if self.request.method == "POST":
            if "btn_add_technology" in self.request.POST:
                dict_return = newtechnology_view.processView(self)
                dataworking = dict_return["formdata"]
                error_summary_add = dict_return["error_summary"]
                if not error_summary_add:
                    tech = getTechnologyByName(dataworking, self.request)
                    techSee = getUserTechById(tech["tech_id"], self.request)
                if not dict_return["redirect"]:
                    action = "addTechnology"

            if "btn_modify_technology" in self.request.POST:
                dataworking = self.getPostDict()
                self.request.matchdict["technologyid"] = dataworking["tech_id"]
                dict_return = modifytechnology_view.processView(self)
                dataworking = dict_return["formdata"]
                error_summary = dict_return["error_summary"]
                techSee = getUserTechById(dataworking["tech_id"], self.request)
                if not dict_return["redirect"]:
                    action = "modifyTechnology"

            if "btn_add_alias" in self.request.POST:
                dataworking = self.getPostDict()
                self.request.matchdict["technologyid"] = dataworking["tech_id"]
                dict_return = newalias_view.processView(self)
                dataworking["alias_name_insert"] = dict_return["formdata"]["alias_name"]
                error_summary_options = dict_return["error_summary"]
                techSee = getUserTechById(dataworking["tech_id"], self.request)

            if "btn_modify_alias" in self.request.POST:

                dataworking = self.getPostDict()
                self.request.matchdict["technologyid"] = dataworking["tech_id"]
                self.request.matchdict["aliasid"] = dataworking["alias_id"]
                dict_return = modifyalias_view.processView(self)
                error_summary_options = dict_return["error_summary"]
                techSee = getUserTechById(dataworking["tech_id"], self.request)

            if (
                "btn_add_technology" not in self.request.POST
                and "btn_modify_technology" not in self.request.POST
                and "btn_add_alias" not in self.request.POST
                and "btn_modify_alias" not in self.request.POST
            ):
                dataworking = self.getPostDict()
                techSee = getUserTechById(dataworking["tech_id"], self.request)

        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "dataworking": dataworking,
            "error_summary_add": error_summary_add,
            "error_summary": error_summary,
            "error_summary_options": error_summary_options,
            "UserTechs": getUserTechs(self.user.login, self.request),
            "ClimMobTechs": getUserTechs("bioversity", self.request),
            "action": action,
            "techSee": techSee,
            "nextPage": nextPage,
            "sectionActive": "technologies",
            # "alias": alias
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
                            if "croptaxonomy_code" in formdata.keys():
                                formdata["croptaxonomy_code"] = formdata[
                                    "croptaxonomy_code"
                                ].replace("'", "")
                            added, message = addTechnology(formdata, self.request)
                            if not added:
                                error_summary = {"dberror": message}
                            else:
                                self.request.session.flash(
                                    self._("The technology was created successfully")
                                )
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
                    existInGenLibrary = findTechInLibrary(
                        formdata, self.request, formdata["tech_id"]
                    )
                    if existInGenLibrary == False:

                        formdata["user_name"] = self.user.login
                        existInPersLibrary = findTechInLibrary(
                            formdata, self.request, formdata["tech_id"]
                        )
                        if existInPersLibrary == False:
                            formdata["user_name"] = self.user.login

                            if "croptaxonomy_code" in formdata.keys():
                                formdata["croptaxonomy_code"] = formdata[
                                    "croptaxonomy_code"
                                ].replace("'", "")

                            update, message = updateTechnology(formdata, self.request)
                            if not update:
                                error_summary = {"dberror": message}
                            else:
                                self.request.session.flash(
                                    self._("The technology was successfully edited")
                                )
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
                self.request.session.flash(
                    self._("The technology was successfully removed")
                )
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


class APICropsView(publicView):
    def processView(self):
        q = self.request.params.get("q", "")
        current_page = self.request.params.get("page")

        if q == "":
            q = None

        if current_page is None:
            current_page = 1

        query_size = 10
        if q is not None:
            q = q.lower()
            query_result, total = query_crops(self.request, q, 0, query_size, "en")
            if total > 0:
                collection = list(range(total))
                page = paginate.Page(collection, current_page, 10)
                query_result, total = query_crops(
                    self.request, q, page.first_item - 1, query_size, "en"
                )
                select2_result = []
                for result in query_result:
                    select2_result.append(
                        {
                            "id": "{}".format(result["taxonomy_code"]),
                            "text": result["crop_name"],
                        }
                    )
                with_pagination = False
                if page.page_count > 1:
                    with_pagination = True

                if not with_pagination:
                    return {"total": total, "results": select2_result}
                else:
                    return {
                        "total": total,
                        "results": select2_result,
                        "pagination": {"more": True},
                    }
            else:
                return {"total": 0, "results": []}
        else:
            return {"total": 0, "results": []}
