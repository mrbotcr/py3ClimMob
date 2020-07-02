from ..classes import apiView
from ...processes import projectExists
from ...processes import (
    getProjectEnumerators,
    isEnumeratorAssigned,
    enumeratorExists,
    getUsableEnumerators,
    addEnumeratorToProject,
    getEnumeratorData,
    removeEnumeratorFromProject,
)

from pyramid.response import Response
import json


class addProjectEnumerator_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"enum_id"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if enumeratorExists(
                        self.user.login, dataworking["enum_id"], self.request
                    ):

                        if isEnumeratorAssigned(
                            self.user.login,
                            dataworking["project_cod"],
                            dataworking["enum_id"],
                            self.request,
                        ):
                            added, message = addEnumeratorToProject(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking["enum_id"],
                                self.request,
                            )
                            if not added:
                                response = Response(status=401, body=message)
                                return response
                            else:
                                response = Response(
                                    status=200,
                                    body=self._(
                                        "The enumerator has been added to the project."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The enumerator is inactive or is already assigned to the project."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "There is not enumerator with that identifier."
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
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class readProjectEnumerators_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    response = Response(
                        status=200,
                        body=json.dumps(
                            getProjectEnumerators(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )
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


class readPossibleProjectEnumerators_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    response = Response(
                        status=200,
                        body=json.dumps(
                            getUsableEnumerators(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )
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


class deleteProjectEnumerator_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"enum_id"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if enumeratorExists(
                        self.user.login, dataworking["enum_id"], self.request
                    ):
                        if not isEnumeratorAssigned(
                            self.user.login,
                            dataworking["project_cod"],
                            dataworking["enum_id"],
                            self.request,
                        ):
                            deleted, message = removeEnumeratorFromProject(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking["enum_id"],
                                self.request,
                            )

                            if deleted:
                                response = Response(
                                    status=200,
                                    body=self._(
                                        "The enumerator was removed from the project."
                                    ),
                                )
                                return response
                            else:
                                response = Response(status=401, body=message)
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The enumerator is inactive or is not assigned to the project."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "There is not enumerator with that identifier."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._("There is not a project with that code."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
