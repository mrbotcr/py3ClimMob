from ..classes import apiView
from ...processes import projectExists, getJSONResult
from pyramid.response import Response
import json

class readDataOfProjectView_api(apiView):
    def processView(self):

        if self.request.method == "GET":

            if "Body" in self.request.params:

                obligatory = [u'project_cod']
                dataworking = json.loads(self.request.params['Body'])

                if sorted(obligatory) == sorted(dataworking.keys()):

                    projectid = dataworking['project_cod']
                    if projectExists(self.user.login, projectid, self.request):

                        response = Response(status=200, body=json.dumps(getJSONResult(self.user.login,dataworking["project_cod"],self.request)))
                        return response
                    else:
                        response = Response(status=401, body=self._("This project does not exist."))
                        return response
                else:
                    response = Response(status=401, body=self._("Error in the JSON."))
                    return response
            else:
                response = Response(status=401, body=self._("Error. You do not have the parameter: Body."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response