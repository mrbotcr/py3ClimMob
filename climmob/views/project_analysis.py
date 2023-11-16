from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from climmob.processes import (
    getActiveProject,
    getQuestionsByType,
    getJSONResult,
    getCombinationsData,
    getProjectProgress,
    projectExists,
    getTheProjectIdForOwner,
    getProjectMetadata,
    getProjectData,
    get_collaborators_in_project,
    addMetadata,
    modifyMetadata,
)
from climmob.products.analysis.analysis import create_analysis
from climmob.products.analysisdata.analysisdata import create_datacsv
from climmob.views.classes import privateView


class metadata_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        error_summary = {}

        dataworking = {}

        activeProject = getActiveProject(self.user.login, self.request)

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            projectInfo = getProjectData(activeProjectId, self.request)

            if self.request.method == "POST":
                if "btn_save_metadata" in self.request.POST:

                    dataworking = self.getPostDict()

                    if activeProject["access_type"] in [4]:
                        raise HTTPNotFound()

                    if not getProjectMetadata(activeProjectId, self.request):

                        dataworking["project_id"] = activeProjectId
                        added, message = addMetadata(dataworking, self.request)
                        if added:

                            self.request.session.flash(
                                self._("The metadata was successfully saved")
                            )
                            self.returnRawViewResult = True
                            return HTTPFound(
                                location=self.request.route_url(
                                    "Metadata",
                                    user=activeProjectUser,
                                    project=activeProjectCod,
                                )
                            )
                        else:
                            self.request.session.flash(
                                self._("Error|Error saving metadata {}".format(message))
                            )
                    else:

                        updated, message = modifyMetadata(
                            activeProjectId, dataworking, self.request
                        )

                        if updated:

                            self.request.session.flash(
                                self._("The metadata was successfully saved")
                            )
                            self.returnRawViewResult = True
                            return HTTPFound(
                                location=self.request.route_url(
                                    "Metadata",
                                    user=activeProjectUser,
                                    project=activeProjectCod,
                                )
                            )
                        else:
                            self.request.session.flash(
                                self._("Error|Error saving metadata {}".format(message))
                            )

            info = getProjectMetadata(activeProjectId, self.request)

            if not dataworking:
                if info:
                    dataworking = info
                else:
                    dataworking["md_coordinator"] = projectInfo["project_pi"]
                    dataworking["md_year"] = projectInfo["project_creationdate"].year
                    dataworking["md_tricot_project"] = projectInfo["project_name"]

                    collaborators = get_collaborators_in_project(
                        self.request, activeProjectId
                    )

                    collaboratorsString = ""
                    for collaborator in collaborators:
                        if collaboratorsString == "":
                            collaboratorsString += "{} ( {} )".format(
                                collaborator["user_fullname"],
                                collaborator["user_email"],
                            )
                        else:
                            collaboratorsString += "\n{} ( {} )".format(
                                collaborator["user_fullname"],
                                collaborator["user_email"],
                            )

                    dataworking["md_collaborators"] = collaboratorsString

                    varieties = getCombinationsData(activeProjectId, self.request)

                    varietiesString = ""
                    for variety in varieties:
                        for element in variety["elements"]:
                            if varietiesString == "":
                                varietiesString += element["alias_name"]
                            else:
                                varietiesString += "\n{}".format(element["alias_name"])

                    dataworking["md_varieties"] = varietiesString

        return {"activeProject": activeProject, "dataworking": dataworking}


class analysisDataView(privateView):
    def processView(self):
        error_summary = {}
        hasActiveProject = False
        infosheet = False
        activeProjectData = getActiveProject(self.user.login, self.request)

        progress, pcompleted = getProjectProgress(
            activeProjectData["owner"]["user_name"],
            activeProjectData["project_cod"],
            activeProjectData["project_id"],
            self.request,
        )

        total_ass_records = 0
        for assessment in progress["assessments"]:
            if assessment["ass_status"] == 1 or assessment["ass_status"] == 2:
                total_ass_records = total_ass_records + assessment["asstotal"]

        if total_ass_records > 5 or (
            activeProjectData["project_registration_and_analysis"] == 1
            and progress["regtotal"] >= 5
        ):

            if self.request.method == "POST":
                if "btn_createAnalysis" in self.request.POST:
                    dataworking = self.getPostDict()

                    if dataworking["txt_included_in_analysis"] != "":
                        part = dataworking["txt_included_in_analysis"][:-1].split(",")

                        variablesSplit = ""
                        if "txt_splits" in dataworking:
                            if dataworking["txt_splits"][0:4] == "true":
                                variablesSplit = dataworking["txt_splits"][5:-1]

                        combinationRerence = -1
                        if "txt_reference" in dataworking:
                            combinationRerence = dataworking["txt_reference"].replace(
                                "reference_", ""
                            )

                        infosheet = dataworking["txt_infosheets"].upper()
                        dataworking["project_id"] = activeProjectData["project_id"]
                        pro = processToGenerateTheReport(
                            activeProjectData,
                            self.request,
                            part,
                            infosheet,
                            variablesSplit,
                            combinationRerence,
                        )

                    self.returnRawViewResult = True
                    if infosheet == "TRUE":
                        return HTTPFound(
                            location=self.request.route_url(
                                "productList",
                                _query={
                                    "product1": "reports",
                                    "product2": "infosheetszip",
                                    "product3": "extraoutputszip",
                                },
                            )
                        )
                    else:
                        return HTTPFound(
                            location=self.request.route_url(
                                "productList",
                                _query={
                                    "product1": "reports",
                                    "product2": "extraoutputszip",
                                },
                            )
                        )

            dataForAnalysis, assessmentsList = getQuestionsByType(
                activeProjectData["project_id"], self.request
            )

            return {
                "activeProject": getActiveProject(self.user.login, self.request),
                "activeUser": self.user,
                "dataForAnalysis": dataForAnalysis,
                "assessmentsList": assessmentsList,
                "correct": False,
                "combinations": getCombinationsData(
                    activeProjectData["project_id"], self.request
                ),
            }
        else:
            raise HTTPNotFound()


def processToGenerateTheReport(
    activeProjectData, request, variables, infosheet, variablesSplit, combinationRerence
):

    data, _assessment = getQuestionsByType(activeProjectData["project_id"], request)

    dict = {}
    for element in variables:
        attr = element.split("_")
        for _section in data:
            if _section not in dict:
                dict[_section] = []
            for _info in data[_section]:
                if _info["id"] == int(attr[3]):

                    if attr[1] == "REG" and _info["code"] is None:
                        dict[_section].append(
                            data[_section][data[_section].index(_info)]
                        )

                    if attr[1] == "ASS":
                        if _info["code"] is not None:
                            if _info["code"]["ass_cod"] == attr[2]:
                                dict[_section].append(
                                    data[_section][data[_section].index(_info)]
                                )

    locale = request.locale_name
    info = getJSONResult(
        activeProjectData["owner"]["user_name"],
        activeProjectData["project_id"],
        activeProjectData["project_cod"],
        request,
    )

    create_analysis(
        locale,
        activeProjectData["owner"]["user_name"],
        activeProjectData["project_id"],
        activeProjectData["project_cod"],
        dict,
        info,
        infosheet,
        request,
        request.registry.settings["r.analysis.script"],
        variablesSplit,
        combinationRerence,
    )

    create_datacsv(
        activeProjectData["owner"]["user_name"],
        activeProjectData["project_id"],
        activeProjectData["project_cod"],
        info,
        request,
        "Report",
        "",
    )

    return True
