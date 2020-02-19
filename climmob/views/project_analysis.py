from .classes import privateView
from ..processes import getActiveProject, getQuestionsByType, getJSONResult
from ..products.analysis.analysis import create_analysis
from pyramid.httpexceptions import HTTPFound
import climmob.plugins.utilities as u
import climmob.plugins as p
import json


class analysisDataView(privateView):
    def processView(self):
        error_summary = {}
        # self.needJS("icheck")
        # self.needCSS("icheck")
        # self.needCSS('switch')
        # self.needJS("switch")
        # self.needJS("analysisData")

        hasActiveProject = False
        activeProjectData = getActiveProject(self.user.login, self.request)

        if self.request.method == "POST":
            if "btn_createAnalysis" in self.request.POST:
                dataworking = self.getPostDict()

                use = []
                if dataworking["txt_included_in_analysis"] != "":
                    part = dataworking["txt_included_in_analysis"][:-1].split(",")

                    for element in part:
                        attr = element.split("_")
                        use.append(int(attr[1]))

                data = getQuestionsByType(
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

                infosheet = dataworking["txt_infosheets"].upper()
                # print json.dumps(dict)
                locale = self.request.locale_name
                create_analysis(
                    locale,
                    self.user.login,
                    activeProjectData["project_cod"],
                    dict,
                    getJSONResult(
                        self.user.login, activeProjectData["project_cod"], self.request
                    ),
                    infosheet,
                    self.request,
                )
                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("productList"))

        return {
            "activeUser": self.user,
            "dataForAnalysis": getQuestionsByType(
                self.user.login, activeProjectData["project_cod"], self.request
            ),
            "correct": False,
        }
