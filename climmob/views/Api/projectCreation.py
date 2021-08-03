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
    existsCountryByCode,
    getCountryList,
)
from ..cloneProjects.cloneProjects import functionCreateClone

from pyramid.response import Response
import json
import datetime
import re


class readListOfCountries_view(apiView):
    def processView(self):

        if self.request.method == "GET":

            response = Response(
                status=200, body=json.dumps(getCountryList(self.request)),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


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
                u"project_cnty",
                u"project_registration_and_analysis",
            ]

            possibles = [
                u"project_cod",
                u"project_name",
                u"project_abstract",
                u"project_tags",
                u"project_pi",
                u"project_piemail",
                u"project_numobs",
                u"project_cnty",
                u"project_registration_and_analysis",
                u"project_clone",
            ]

            dataworking = json.loads(self.body)

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

                    dataworking["user_name"] = self.user.login
                    dataworking["project_localvariety"] = 1
                    dataworking["project_regstatus"] = 0
                    dataworking["project_numcom"] = 3

                    dataInParams = True
                    for key in dataworking.keys():
                        if dataworking[key] == "":
                            dataInParams = False

                    if dataInParams:

                        if "project_clone" in dataworking.keys():
                            print("Desea clonar un proyecto")
                            exitsproject = projectInDatabase(
                                self.user.login,
                                dataworking["project_clone"],
                                self.request,
                            )
                            if not exitsproject:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The project to be cloned does not exist."
                                    ),
                                )
                                return response

                        dataworking["project_lat"] = ""
                        dataworking["project_lon"] = ""
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
                                        if str(
                                            dataworking[
                                                "project_registration_and_analysis"
                                            ]
                                        ) not in ["0", "1",]:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "The possible values in the parameter 'project_registration_and_analysis' are: ['0':' Registration is done first, followed by one or more data collection moments (with different forms)','1':'Requires registering participants and immediately asking questions to analyze the information']"
                                                ),
                                            )
                                            return response

                                        if str(
                                            dataworking["project_localvariety"]
                                        ) not in ["0", "1",]:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "The possible values in the parameter 'project_localvariety' are: ['0':'No','1':'Yes']"
                                                ),
                                            )
                                            return response

                                        if not existsCountryByCode(
                                            self.request, dataworking["project_cnty"]
                                        ):
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "The country assigned to the project does not exist in the ClimMob list."
                                                ),
                                            )
                                            return response

                                        added, message = addProject(
                                            dataworking, self.request
                                        )

                                        if added:
                                            dataworking[
                                                "slt_project_cod"
                                            ] = dataworking["project_clone"]
                                            if "project_clone" in dataworking.keys():

                                                ok = functionCreateClone(
                                                    self, dataworking
                                                )

                                                response = Response(
                                                    status=200,
                                                    body=self._(
                                                        "Project successfully cloned."
                                                    ),
                                                )
                                                return response

                                        if not added:
                                            response = Response(
                                                status=401, body=message
                                            )
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
                                    "For the project code only letters and numbers are allowed. The project code must start with a letter."
                                ),
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
                        body=self._(
                            "You are trying to use a parameter that is not allowed.."
                        ),
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
                u"project_cnty",
                u"project_registration_and_analysis",
                u"user_name",
                u"project_numcom",
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
                        dataworking["project_lat"] = ""
                        dataworking["project_lon"] = ""
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

                            if (
                                "project_registration_and_analysis"
                                in dataworking.keys()
                            ):
                                if str(
                                    dataworking["project_registration_and_analysis"]
                                ) not in ["0", "1",]:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The possible values in the parameter 'project_registration_and_analysis' are: ['0':' Registration is done first, followed by one or more data collection moments (with different forms)','1':'Requires registering participants and immediately asking questions to analyze the information']"
                                        ),
                                    )
                                    return response

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

                            if not existsCountryByCode(
                                self.request, dataworking["project_cnty"]
                            ):
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The country assigned to the project does not exist in the ClimMob list."
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
