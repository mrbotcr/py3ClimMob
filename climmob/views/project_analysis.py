from .classes import privateView
from ..processes import getActiveProject, getQuestionsByType, getJSONResult
from ..products.analysis.analysis import create_analysis
from ..products.analysisdata.analysisdata import create_datacsv
from pyramid.httpexceptions import HTTPFound


class analysisDataView(privateView):
    def processView(self):
        error_summary = {}
        hasActiveProject = False
        activeProjectData = getActiveProject(self.user.login, self.request)

        if self.request.method == "POST":
            if "btn_createAnalysis" in self.request.POST:
                dataworking = self.getPostDict()

                if dataworking["txt_included_in_analysis"] != "":
                    part = dataworking["txt_included_in_analysis"][:-1].split(",")
                    infosheet = dataworking["txt_infosheets"].upper()
                    dataworking["project_id"] = activeProjectData["project_id"]
                    pro = processToGenerateTheReport(
                        activeProjectData, self.request, part, infosheet
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
        }


def processToGenerateTheReport(activeProjectData, request, variables, infosheet):

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
