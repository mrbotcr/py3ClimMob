from .classes import privateView
from ..processes import (
    getActiveProject,
    getQuestionsByType,
    getJSONResult,
    getCombinationsData,
    getProjectProgress,
)
from ..products.analysis.analysis import create_analysis
from ..products.analysisdata.analysisdata import create_datacsv
from pyramid.httpexceptions import HTTPFound, HTTPNotFound


class analysisDataView(privateView):
    def processView(self):
        error_summary = {}
        hasActiveProject = False
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
                    variablesSplit = ""

                    if dataworking["txt_included_in_analysis"] != "":
                        part = dataworking["txt_included_in_analysis"][:-1].split(",")
                        if dataworking["txt_splits"][0:4] == "true":
                            variablesSplit = dataworking["txt_splits"][5:-1]

                        infosheet = dataworking["txt_infosheets"].upper()
                        dataworking["project_id"] = activeProjectData["project_id"]
                        pro = processToGenerateTheReport(
                            activeProjectData,
                            self.request,
                            part,
                            infosheet,
                            variablesSplit,
                        )

                    self.returnRawViewResult = True
                    return HTTPFound(location=self.request.route_url("productList"))

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
    activeProjectData, request, variables, infosheet, variablesSplit
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
