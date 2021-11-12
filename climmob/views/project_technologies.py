from .classes import privateView
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from ..processes import (
    projectExists,
    projectTechnologyExists,
    searchTechnologies,
    searchTechnologiesInProject,
    addTechnologyProject,
    deleteTechnologyProject,
    AliasSearchTechnology,
    AliasSearchTechnologyInProject,
    AliasExtraSearchTechnologyInProject,
    AddAliasTechnology,
    deleteAliasTechnology,
    addTechAliasExtra,
    findTechAlias,
    numberOfCombinationsForTheProject,
    isTechnologyAssigned,
    numberOfAliasesInTechnology,
    getTechnology,
    getActiveProject,
    getTheProjectIdForOwner,
    getProjectData
)


class projectTecnologies_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        alias = {}
        tech_id = ""
        dataworking = {}
        error_summary = {}
        dataworking["alias_name"] = ""
        techSee = {}

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            prjData = getProjectData(activeProjectId, self.request)
            # Only create the packages if its needed
            if prjData["project_createpkgs"] == 2:
                self.returnRawViewResult = True

                return HTTPFound(
                    location=self.request.route_url("dashboard")
                )

            if self.request.method == "POST":
                if "btn_save_technologies" in self.request.POST:
                    postdata = self.getPostDict()

                    if postdata["txt_technologies_included"] != "":

                        part = postdata["txt_technologies_included"][:-1].split(",")

                        for element in part:
                            attr = element.split("_")
                            if attr[2] == "new":
                                addTechnologyProject(
                                    activeProjectId, attr[1], self.request,
                                )
                    if postdata["txt_technologies_excluded"] != "":

                        part = postdata["txt_technologies_excluded"][:-1].split(",")

                        for element in part:
                            attr = element.split("_")
                            if attr[2] == "exists":
                                deleteTechnologyProject(
                                    activeProjectId, attr[1], self.request,
                                )

                if "btn_show_technology_alias" in self.request.POST:
                    postdata = self.getPostDict()
                    tech_id = postdata["tech_id"]
                    self.request.matchdict["tech_id"] = postdata["tech_id"]
                    alias = prjTechAliases_view.processView(self)
                    techSee = getTechnology(postdata, self.request)

                if "btn_show_technology_alias_in_library" in self.request.POST:
                    postdata = self.getPostDict()
                    tech_id = postdata["tech_id"]
                    alias = {
                        "AliasTechnology": AliasSearchTechnology(
                            tech_id, activeProjectId, self.request
                        )
                    }
                    techSee = getTechnology(postdata, self.request)

                if "btn_save_technologies_alias" in self.request.POST:
                    postdata = self.getPostDict()
                    tech_id = postdata["tech_id"]
                    dataworking["project_id"] = activeProjectId
                    dataworking["tech_id"] = tech_id
                    dataworking["user_name"] = self.user.login
                    if not isTechnologyAssigned(dataworking, self.request):
                        added, message = addTechnologyProject(
                            activeProjectId, dataworking["tech_id"], self.request,
                        )
                    self.request.matchdict["tech_id"] = postdata["tech_id"]
                    alias = prjTechAliases_view.processView(self)
                    techSee = getTechnology(postdata, self.request)

                if "btn_add_alias" in self.request.POST:
                    postdata = self.getPostDict()
                    tech_id = postdata["tech_id"]
                    dataworking["project_id"] = activeProjectId
                    dataworking["tech_id"] = tech_id
                    dataworking["user_name"] = self.user.login
                    if not isTechnologyAssigned(dataworking, self.request):
                        added, message = addTechnologyProject(
                            activeProjectId, dataworking["tech_id"], self.request,
                        )

                    self.request.matchdict["tech_id"] = postdata["tech_id"]
                    result = prjTechAliasAdd_view.processView(self)
                    dataworking = result["dataworking"]
                    error_summary = result["error_summary"]
                    if result["redirect"]:
                        dataworking["alias_name"] = ""
                    alias = prjTechAliases_view.processView(self)
                    techSee = getTechnology(postdata, self.request)

            return {
                "activeUser": self.user,
                "activeProject": getActiveProject(self.user.login, self.request),
                "tech_id": tech_id,
                "TechnologiesUser": searchTechnologies(activeProjectId, self.request),
                "TechnologiesInProject": searchTechnologiesInProject(
                    activeProjectId, self.request
                ),
                "project_numcom": numberOfCombinationsForTheProject(
                    activeProjectId, self.request
                ),
                "alias": alias,
                "dataworking": dataworking,
                "error_summary": error_summary,
                "techSee": techSee,
            }


class prjTechAliases_view(privateView):
    def processView(self):

        error_summary = {}
        dataworking = {}
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        technologyid = self.request.matchdict["tech_id"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if self.request.method == "POST":
                if "btn_save_technologies_alias" in self.request.POST:
                    postdata = self.getPostDict()
                    if postdata["txt_technologies_included"] != "":

                        part = postdata["txt_technologies_included"][:-1].split(",")

                        for element in part:
                            attr = element.split("_")
                            if attr[2] == "new":
                                dataworking["project_id"] = activeProjectId
                                dataworking["tech_id"] = technologyid
                                dataworking["alias_id"] = attr[1]

                                add, message = AddAliasTechnology(
                                    dataworking, self.request
                                )
                                if not add:
                                    error_summary = {"dberror": message}

                    if postdata["txt_technologies_excluded"] != "":
                        part = postdata["txt_technologies_excluded"][:-1].split(",")
                        for element in part:
                            attr = element.split("_")
                            delete, message = deleteAliasTechnology(
                                activeProjectId, technologyid, attr[1], self.request,
                            )
                            if not delete:
                                error_summary = {"dberror": message}

                    if (
                        numberOfAliasesInTechnology(
                            activeProjectId, technologyid, self.request
                        )
                        == 0
                    ):
                        deleteTechnologyProject(
                            activeProjectId, technologyid, self.request
                        )

            return {
                "activeUser": self.user,
                "dataworking": dataworking,
                "error_summary": error_summary,
                "AliasTechnology": AliasSearchTechnology(
                    technologyid, activeProjectId, self.request
                ),
                "AliasTechnologyInProject": AliasSearchTechnologyInProject(
                    technologyid, activeProjectId, self.request
                ),
                "AliasExtraTechnologyInProject": AliasExtraSearchTechnologyInProject(
                    technologyid, activeProjectId, self.request
                ),
                "activeProject": getActiveProject(self.user.login, self.request),
                "techid": technologyid,
                "project_numcom": numberOfCombinationsForTheProject(
                    activeProjectId, self.request
                ),
                "count": numberOfAliasesInTechnology(
                    activeProjectId, technologyid, self.request
                ),
            }


class prjTechAliasAdd_view(privateView):
    def processView(self):
        error_summary = {}
        dataworking = {}
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        technologyid = self.request.matchdict["tech_id"]
        redirect = False

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )

        if not projectTechnologyExists(activeProjectId, technologyid, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "POST":
                if "btn_add_alias" in self.request.POST:
                    tdata = self.getPostDict()
                    alias_name = tdata["txt_add_alias"]
                    if alias_name != "":
                        # add the object
                        dataworking["user_name"] = self.user.login
                        dataworking["project_id"] = activeProjectId
                        dataworking["tech_id"] = technologyid
                        dataworking["alias_name"] = alias_name
                        # verify that there is no
                        existAlias = findTechAlias(dataworking, self.request)
                        if existAlias == False:
                            # add the alias
                            added, message = addTechAliasExtra(
                                dataworking, self.request
                            )
                            if not added:
                                # capture the error
                                error_summary = {"dberror": message}
                            else:
                                redirect = True
                        else:
                            # error
                            error_summary = {
                                "exists": self._(
                                    "This technology option already exists in the technology"
                                )
                            }
                    else:
                        # error
                        error_summary = {
                            "nameempty": self._(
                                "The name of the technology option cannot be empy"
                            )
                        }
        return {
            "activeUser": self.user,
            "error_summary": error_summary,
            "dataworking": self.decodeDict(dataworking),
            "tech_id": technologyid,
            "redirect": redirect,
        }
