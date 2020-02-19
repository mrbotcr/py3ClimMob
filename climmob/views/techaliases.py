from .classes import privateView
from pyramid.httpexceptions import HTTPFound

from ..processes import (
    getTechsAlias,
    findTechalias,
    addTechAlias,
    getAlias,
    updateAlias,
    removeAlias,
    getTechnology,
)


class alias_view(privateView):
    def processView(self):
        # self.needJS('alias')
        # self.needJS('datatables')
        # self.needCSS('datatables')

        # self.needCSS("sweet")
        # self.needJS("sweet")
        # self.needJS("delete")

        formdata = {}
        formdata["tech_id"] = self.request.matchdict["technologyid"]
        data = getTechnology(formdata, self.request)
        formdata["user_name"] = data["user_name"]
        return {
            "activeUser": self.user,
            "formdata": formdata,
            "Alias": getTechsAlias(formdata["tech_id"], self.request),
            "tech": data,
        }


class newalias_view(privateView):
    def processView(self):
        formdata = {}
        error_summary = {}
        formdata["tech_id"] = self.request.matchdict["technologyid"]

        if self.request.method == "POST":
            if "btn_add_alias" in self.request.POST:

                formdata = self.getPostDict()
                formdata["tech_id"] = self.request.matchdict["technologyid"]
                formdata["alias_id"] = None
                if formdata["alias_name"] != "":
                    badalias = ""
                    textarea = formdata["alias_name"].replace("\r", "")
                    addd = []
                    for alias in textarea.split("\n"):

                        if alias.strip() != "":
                            formdata["alias_name"] = alias
                            existAlias = findTechalias(formdata, self.request)
                            if alias not in addd:
                                if existAlias == False:

                                    added, message = addTechAlias(
                                        formdata, self.request
                                    )
                                    if not added:
                                        error_summary = {"dberror": message}
                                        badalias += alias + "\n"
                                    else:
                                        addd.append(alias)
                                else:
                                    badalias += alias + "\n"

                    if badalias == "":
                        self.returnRawViewResult = True
                        return HTTPFound(
                            location=self.request.route_url(
                                "useralias", technologyid=formdata["tech_id"]
                            )
                        )
                    else:
                        formdata["alias_name"] = badalias
                        error_summary = {
                            "exists": self._(
                                "This alias already exists in the technology"
                            )
                        }
                else:
                    error_summary = {
                        "nameempty": self._("The name of the alias cannot be empy")
                    }

        data = getTechnology(formdata, self.request)
        return {
            "activeUser": self.user,
            "formdata": self.decodeDict(formdata),
            "error_summary": error_summary,
            "tech": data,
        }


class deletealias_view(privateView):
    def processView(self):
        formdata = {}
        error_summary = {}
        formdata["tech_id"] = self.request.matchdict["technologyid"]
        formdata["alias_id"] = self.request.matchdict["aliasid"]
        data = getAlias(formdata, self.request)
        formdata["alias_name"] = data["alias_name"]

        if self.request.method == "POST":
            # if 'btn_delete_alias' in self.request.POST:
            formdata["alias_id"] = self.request.matchdict["aliasid"]
            removed, message = removeAlias(formdata, self.request)
            if not removed:
                error_summary = {"dberror": message}
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
            else:
                self.returnRawViewResult = True
                return {"status": 200}
            # else:
            #    return HTTPFound(location=self.request.route_url('useralias', technologyid=formdata["tech_id"]))

        return {
            "activeUser": self.user,
            "formdata": formdata,
            "error_summary": error_summary,
        }


class modifyalias_view(privateView):
    def processView(self):
        formdata = {}
        error_summary = {}
        formdata["tech_id"] = self.request.matchdict["technologyid"]
        formdata["alias_id"] = self.request.matchdict["aliasid"]
        data = getAlias(formdata, self.request)
        formdata["alias_name"] = data["alias_name"]

        if self.request.method == "POST":
            if "btn_modify_alias" in self.request.POST:

                formdata = self.getPostDict()
                formdata["tech_id"] = self.request.matchdict["technologyid"]
                formdata["alias_id"] = self.request.matchdict["aliasid"]

                if formdata["alias_name"] != "":

                    existAlias = findTechalias(formdata, self.request)
                    if existAlias == False:

                        update, message = updateAlias(formdata, self.request)
                        if not update:
                            error_summary = {"dberror": message}
                        else:
                            self.returnRawViewResult = True
                            return HTTPFound(
                                location=self.request.route_url(
                                    "useralias", technologyid=formdata["tech_id"]
                                )
                            )
                    else:
                        error_summary = {
                            "exists": self._(
                                "This alias already exists in the technology"
                            )
                        }
                else:
                    error_summary = {
                        "nameempty": self._("The name of the alias cannot be empy")
                    }

        data2 = getTechnology(formdata, self.request)
        return {
            "activeUser": self.user,
            "formdata": self.decodeDict(formdata),
            "error_summary": error_summary,
            "tech": data2,
        }
