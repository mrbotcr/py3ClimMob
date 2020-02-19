from ..classes import apiView

from ...processes import projectExists, getProjectProgress, getProjectData

from pyramid.response import Response
import json
import datetime


class readProjectDetails_view(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            dataworking = json.loads(self.request.params["Body"])

            if sorted(obligatory) == sorted(dataworking.keys()):
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    projectDetails = getProjectData(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    progress, pcompleted = getProjectProgress(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    response = Response(
                        status=200,
                        body=json.dumps(
                            {
                                "project": projectDetails,
                                "progress": progress,
                                "pcompleted": pcompleted,
                            },
                            default=myconverter,
                        ),
                    )
                    return response
                else:
                    response = Response(
                        status=401, body=self._("There is no a project with that code.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response
