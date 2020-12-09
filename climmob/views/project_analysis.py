from .classes import privateView
from ..processes import getActiveProject, getQuestionsByType, getJSONResult
from ..products.analysis.analysis import create_analysis
from ..products.analysisdata.analysisdata import create_datacsv
from pyramid.httpexceptions import HTTPFound
import climmob.plugins.utilities as u
import climmob.plugins as p
import json


class analysisDataView(privateView):
    def processView(self):
        error_summary = {}
        hasActiveProject = False
        activeProjectData = getActiveProject(self.user.login, self.request)

        if self.request.method == "POST":
            if "btn_createAnalysis" in self.request.POST:
                dataworking = self.getPostDict()

                dict = {}
                if dataworking["txt_included_in_analysis"] != "":
                    part = dataworking["txt_included_in_analysis"][:-1].split(",")

                    data, _assessment = getQuestionsByType(
                        self.user.login, activeProjectData["project_cod"], self.request
                    )

                    for element in part:
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

                                    if attr[1]=="ASS":
                                        if _info["code"] is not None:
                                            if _info["code"]["ass_cod"] == attr[2]:
                                                dict[_section].append(
                                                    data[_section][data[_section].index(_info)]
                                                )

                    #for element in part:
                    #    attr = element.split("_")
                    #    use.append(int(attr[2]))

                """use = []
                if dataworking["txt_included_in_analysis"] != "":
                    part = dataworking["txt_included_in_analysis"][:-1].split(",")

                    for element in part:
                        attr = element.split("_")
                        use.append(int(attr[1]))

                data, _assessment = getQuestionsByType(
                    self.user.login, activeProjectData["project_cod"], self.request
                )
                dict = {}

                for _section in data:
                    dict[_section] = []
                    for _info in data[_section]:
                        if _info["id"] in use:
                            dict[_section].append(
                                data[_section][data[_section].index(_info)]
                            )
                """
                infosheet = dataworking["txt_infosheets"].upper()
                # print json.dumps(dict)
                locale = self.request.locale_name
                info = getJSONResult(
                    self.user.login, activeProjectData["project_cod"], self.request
                )

                create_analysis(
                    locale,
                    self.user.login,
                    activeProjectData["project_cod"],
                    dict,
                    info,
                    infosheet,
                    self.request,
                    self.request.registry.settings["r.analysis.script"],
                )

                create_datacsv(
                    self.user.login,
                    activeProjectData["project_cod"],
                    info,
                    self.request,
                    "Report",
                    "",
                )

                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("productList"))

        dataForAnalysis, assessmentsList = getQuestionsByType(
            self.user.login, activeProjectData["project_cod"], self.request
        )

        return {
            "activeUser": self.user,
            "dataForAnalysis": dataForAnalysis,
            "assessmentsList": assessmentsList,
            "correct": False,
        }
