from ..classes import apiView
from ...processes import (
    projectInDatabase,
    addProject,
    projectExists,
    deleteProject,
    getUserProjects,
    getProjectData,
    modifyProject,
    changeTheStateOfCreateComb,
)

from pyramid.response import Response
import json
import datetime
import re


class createProject_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                u"project_cod",
                u"project_name",
                u"project_abstract",
                u"project_tags",
                u"project_pi",
                u"project_piemail",
                u"project_numobs",
                "project_numcom",
                u"project_lat",
                u"project_lon",
                u"project_localvariety",
                "user_name",
                "project_regstatus",
            ]
            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login
            dataworking["project_regstatus"] = 0
            dataworking["project_numcom"] = 3

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    if re.search("^[A-Za-z0-9]*$", dataworking["project_cod"]):
                        if dataworking["project_cod"][0].isdigit() == False:
                            exitsproject = projectInDatabase(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )
                            if not exitsproject:

                                try:
                                    dataworking["project_numobs"] = int(
                                        dataworking["project_numobs"]
                                    )
                                except:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The parameter project_numobs must be a number."
                                        ),
                                    )
                                    return response

                                if (
                                    dataworking["project_numobs"] > 0
                                    and dataworking["project_numcom"] > 0
                                ):
                                    if str(dataworking["project_localvariety"]) not in [
                                        "0",
                                        "1",
                                    ]:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "The possible values in the parameter 'project_localvariety' are: ['0':'No','1':'Yes']"
                                            ),
                                        )
                                        return response

                                    added, message = addProject(
                                        dataworking, self.request
                                    )
                                    if not added:
                                        response = Response(status=401, body=message)
                                        return response
                                    else:
                                        response = Response(
                                            status=200,
                                            body=self._(
                                                "Project created successfully."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The number of combinations and observations must be greater than 0."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "A project already exists with this code."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The project code must start with a letter."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "For the project code only letters and numbers are allowed and the project code must start with a letter."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401, body=self._("Not all parameters have data.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response

        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class readProjects_view(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(
                    getUserProjects(self.user.login, self.request), default=myconverter
                ),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class updateProject_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            possibles = [
                u"project_cod",
                u"project_name",
                u"project_abstract",
                u"project_tags",
                u"project_pi",
                u"project_piemail",
                u"project_numobs",
                u"project_numcom",
                u"project_lat",
                u"project_lon",
                u"project_localvariety",
                "user_name",
                "project_regstatus",
            ]
            obligatory = [u"project_cod"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login
            dataworking["project_numcom"] = 3

            permitedKeys = True
            for key in dataworking.keys():
                if key not in possibles:
                    permitedKeys = False

            obligatoryKeys = True

            for key in obligatory:
                if key not in dataworking.keys():
                    obligatoryKeys = False

            if obligatoryKeys:
                if permitedKeys:

                    dataInParams = True
                    for key in dataworking.keys():
                        if dataworking[key] == "":
                            dataInParams = False

                    if dataInParams:
                        exitsproject = projectInDatabase(
                            self.user.login, dataworking["project_cod"], self.request
                        )
                        if exitsproject:
                            cdata = getProjectData(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )
                            if cdata["project_regstatus"] != 0:
                                dataworking["project_numobs"] = cdata["project_numobs"]
                                dataworking["project_numcom"] = cdata["project_numcom"]

                            if "project_numobs" in dataworking.keys():
                                isNecessarygenerateCombinations = False
                                if int(dataworking["project_numobs"]) != int(
                                    cdata["project_numobs"]
                                ):
                                    isNecessarygenerateCombinations = True

                                if int(dataworking["project_numcom"]) != int(
                                    cdata["project_numcom"]
                                ):
                                    isNecessarygenerateCombinations = True

                                if isNecessarygenerateCombinations:
                                    changeTheStateOfCreateComb(
                                        self.user.login,
                                        dataworking["project_cod"],
                                        self.request,
                                    )

                            if "project_localvariety" in dataworking.keys():
                                if str(dataworking["project_localvariety"]) not in [
                                    "0",
                                    "1",
                                ]:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The possible values in the parameter 'project_localvariety' are: ['0':'No','1':'Yes']"
                                        ),
                                    )
                                    return response

                            modified, message = modifyProject(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking,
                                self.request,
                            )
                            if not modified:
                                response = Response(status=401, body=message)
                                return response
                            else:
                                response = Response(
                                    status=200,
                                    body=self._(
                                        "The project was modified successfully."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("There is no a project with that code."),
                            )
                            return response
                    else:
                        response = Response(
                            status=401, body=self._("Not all parameters have data.")
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._("Error in the parameters that you want to modify."),
                    )
                    return response
            else:
                response = Response(
                    status=401,
                    body=self._("It is not complying with the obligatory keys."),
                )
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class deleteProject_view_api(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"project_cod"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                projectid = dataworking["project_cod"]
                if not projectExists(self.user.login, projectid, self.request):
                    response = Response(
                        status=401, body=self._("This project does not exist.")
                    )
                    return response

                deleted, message = deleteProject(
                    self.user.login, projectid, self.request
                )
                if not deleted:
                    response = Response(status=401, body=message)
                    return response
                else:
                    response = Response(
                        status=200, body=self._("The project was deleted successfully")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
