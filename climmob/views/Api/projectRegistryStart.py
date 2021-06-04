from ..classes import apiView

from ...processes import (
    projectExists,
    projectRegStatus,
    createCombinations,
    getCombinations,
    projectHasCombinations,
    getCombinationStatus,
    setCombinationStatus,
    getProjectProgress,
    projectCreateCombinations,
    create_packages_with_r,
    getPackages,
    projectCreatePackages,
    setRegistryStatus,
    generateStructureForInterfaceForms,
    generateStructureForValidateJsonOdk,
    isRegistryClose,
    getProjectNumobs,
    getJSONResult,
)

from climmob.products import stopTasksByProcess
from ...processes.odk.api import storeJSONInMySQL

from ..project_combinations import startTheRegistry

from pyramid.response import Response
from xml.dom import minidom
import json
import datetime
import os
import uuid
import climmob.plugins as p

class readProjectCombinations_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.body)
            except:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON, It does not have the 'body' parameter."
                    ),
                )
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        # if projectRegStatus(self.user.login, dataworking['project_cod'], self.request):
                        progress, pcompleted = getProjectProgress(
                            self.user.login, dataworking["project_cod"], self.request
                        )
                        if (
                            progress["enumerators"] == True
                            and progress["technology"] == True
                            and progress["techalias"] == True
                            and progress["registry"] == True
                        ):

                            createCombinations(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )
                            techs, ncombs, combs, = getCombinations(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )

                            pos = 1
                            elements = []
                            combArray = []
                            pos2 = 0
                            for comb in combs:
                                if pos <= len(techs):
                                    elements.append(
                                        {
                                            "alias_id": comb["alias_id"],
                                            "alias_name": comb["alias_name"],
                                        }
                                    )
                                    pos += 1
                                else:
                                    combArray.append(
                                        {
                                            "ncomb": comb["comb_code"] - 1,
                                            "comb_usable": combs[pos2 - 1][
                                                "comb_usable"
                                            ],
                                            "elements": list(elements),
                                        }
                                    )
                                    elements = []
                                    elements.append(
                                        {
                                            "alias_id": comb["alias_id"],
                                            "alias_name": comb["alias_name"],
                                        }
                                    )
                                    pos = 2
                                pos2 += 1
                            combArray.append(
                                {
                                    "ncomb": ncombs,
                                    "comb_usable": combs[pos2 - 1]["comb_usable"],
                                    "elements": list(elements),
                                }
                            )

                            response = Response(
                                status=200,
                                body=json.dumps(
                                    {"techs": techs, "combinations": combArray}
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You must have the field agents, technologies, technology options and created the registration form to read the combinations."
                                ),
                            )
                            return response
                        # else:
                        #    response = Response(status=401, body=self._("The registry is already started."))
                        #    return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class setUsableCombinations_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"ncomb", u"status"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        if projectRegStatus(
                            self.user.login, dataworking["project_cod"], self.request
                        ):
                            progress, pcompleted = getProjectProgress(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )
                            if (
                                progress["enumerators"] == True
                                and progress["technology"] == True
                                and progress["techalias"] == True
                                and progress["registry"] == True
                            ):
                                if not projectCreateCombinations(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    self.request,
                                ):
                                    exits, status = getCombinationStatus(
                                        self.user.login,
                                        dataworking["project_cod"],
                                        dataworking["ncomb"],
                                        self.request,
                                    )
                                    if exits:
                                        if (
                                            str(dataworking["status"]) == "0"
                                            or str(dataworking["status"]) == "1"
                                        ):
                                            if str(dataworking["status"]) != str(
                                                status
                                            ):
                                                setCombinationStatus(
                                                    self.user.login,
                                                    dataworking["project_cod"],
                                                    dataworking["ncomb"],
                                                    dataworking["status"],
                                                    self.request,
                                                )

                                                response = Response(
                                                    status=200,
                                                    body=self._(
                                                        "The state of the combination was changed."
                                                    ),
                                                )
                                                return response
                                            else:
                                                response = Response(
                                                    status=401,
                                                    body=self._(
                                                        "The state is the same."
                                                    ),
                                                )
                                                return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "The value of the status is 0 [unusable] or 1 [usable]."
                                                ),
                                            )
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "You do not have a combination with this ID."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The combinations have not been created."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You must have the field agents, technology options and registration form ready."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("Registration has already started."),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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


class createPackages_view(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.body)
            except:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON, It does not have the 'body' parameter."
                    ),
                )
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        progress, pcompleted = getProjectProgress(
                            self.user.login, dataworking["project_cod"], self.request
                        )
                        if (
                            progress["enumerators"] == True
                            and progress["technology"] == True
                            and progress["techalias"] == True
                            and progress["registry"] == True
                        ):
                            if not projectCreateCombinations(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            ):
                                create_packages_with_r(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    self.request,
                                )
                                ncombs, packages = getPackages(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    self.request,
                                )

                                response = Response(
                                    status=200,
                                    body=json.dumps(
                                        {"packages": packages, "combinations": ncombs},
                                        default=myconverter,
                                    ),
                                )
                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "This project has not created the combinations. You need to create the combinations first."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You must have the field agents, technology options and registration form ready."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class createProjectRegistry_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        if projectRegStatus(
                            self.user.login, dataworking["project_cod"], self.request
                        ):
                            progress, pcompleted = getProjectProgress(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )
                            if (
                                progress["enumerators"] == True
                                and progress["technology"] == True
                                and progress["techalias"] == True
                                and progress["registry"] == True
                            ):
                                if not projectCreateCombinations(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    self.request,
                                ):
                                    if not projectCreatePackages(
                                        self.user.login,
                                        dataworking["project_cod"],
                                        self.request,
                                    ):

                                        startIsOk, error = startTheRegistry(
                                            self, dataworking["project_cod"]
                                        )
                                        if startIsOk:
                                            response = Response(
                                                status=200,
                                                body=self._("Registration started."),
                                            )
                                            return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "There has been a problem in the creation of the basic structure of the project, this may be due to something wrong with the form. Contact the ClimMob team with the next message to get the solution to the problem"
                                                )
                                                + ": "
                                                + error,
                                            )
                                            return response

                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "Packages have not available yet. You need to do the randomization first."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This project has not created the combinations. You need to create the combinations first."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You must have the field agents, technology options and registration form ready."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("Registration has already started."),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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


class cancelRegistryApi_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        if not projectRegStatus(
                            self.user.login, dataworking["project_cod"], self.request
                        ):
                            setRegistryStatus(
                                self.user.login,
                                dataworking["project_cod"],
                                0,
                                self.request,
                            )
                            stopTasksByProcess(
                                self.request,
                                self.user.login,
                                dataworking["project_cod"],
                            )

                            response = Response(
                                status=200, body=self._("Cancel registration.")
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The registration has not started. You cannot cancel it."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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


class closeRegistryApi_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        if not projectRegStatus(
                            self.user.login, dataworking["project_cod"], self.request
                        ):

                            progress, pcompleted = getProjectProgress(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )
                            if progress["regtotal"] > 0:
                                setRegistryStatus(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    2,
                                    self.request,
                                )
                                response = Response(
                                    status=200, body=self._("Closed registration.")
                                )
                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You cannot close the registration because you do not have data."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The registration has not started. You cannot cancel it."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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


class readRegistryStructure_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.body)
            except:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON, It does not have the 'body' parameter."
                    ),
                )
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        if not projectRegStatus(
                            self.user.login, dataworking["project_cod"], self.request
                        ):
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    generateStructureForInterfaceForms(
                                        self.user.login,
                                        dataworking["project_cod"],
                                        "registry",
                                        self.request,
                                    )
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401, body=self._("Registration has not started.")
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class pushJsonToRegistry_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"json"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        if not projectRegStatus(
                            self.user.login, dataworking["project_cod"], self.request
                        ):
                            if not isRegistryClose(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            ):
                                structure = generateStructureForInterfaceForms(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    "registry",
                                    self.request,
                                )
                                if structure:
                                    obligatoryQuestions = [u"clm_start", u"clm_end"]
                                    possibleQuestions = [u"clm_start", u"clm_end"]
                                    searchQST162 = ""
                                    for section in structure:
                                        for question in section["section_questions"]:

                                            possibleQuestions.append(
                                                question["question_datafield"]
                                            )

                                            if question["question_code"] == "QST162":
                                                searchQST162 = question[
                                                    "question_datafield"
                                                ]

                                            if question["question_requiredvalue"] == 1:
                                                obligatoryQuestions.append(
                                                    question["question_datafield"]
                                                )

                                    try:
                                        _json = json.loads(dataworking["json"])

                                        permitedKeys = True
                                        for key in _json.keys():
                                            if key not in possibleQuestions:
                                                permitedKeys = False

                                        if permitedKeys:
                                            obligatoryKeys = True
                                            for key in obligatoryQuestions:
                                                if key not in _json.keys():
                                                    obligatoryKeys = False

                                            if obligatoryKeys:

                                                dataInParams = True
                                                for key in obligatoryQuestions:
                                                    if _json[key].strip(" ") == "":
                                                        dataInParams = False

                                                if dataInParams:

                                                    if _json[searchQST162].isdigit():
                                                        if int(
                                                            _json[searchQST162]
                                                        ) <= getProjectNumobs(
                                                            self.user.login,
                                                            dataworking["project_cod"],
                                                            self.request,
                                                        ):
                                                            _json["clm_deviceimei"] = (
                                                                "API_"
                                                                + str(self.apiKey)
                                                            )

                                                            uniqueId = str(uuid.uuid1())
                                                            path = os.path.join(
                                                                self.request.registry.settings[
                                                                    "user.repository"
                                                                ],
                                                                *[
                                                                    self.user.login,
                                                                    dataworking[
                                                                        "project_cod"
                                                                    ],
                                                                    "data",
                                                                    "reg",
                                                                    "json",
                                                                    uniqueId,
                                                                ]
                                                            )

                                                            if not os.path.exists(path):
                                                                os.makedirs(path)

                                                            pathfinal = os.path.join(
                                                                path, uniqueId + ".json"
                                                            )

                                                            f = open(pathfinal, "w")
                                                            f.write(json.dumps(_json))
                                                            f.close()
                                                            storeJSONInMySQL(
                                                                "REG",
                                                                self.user.login,
                                                                None,
                                                                dataworking[
                                                                    "project_cod"
                                                                ],
                                                                None,
                                                                pathfinal,
                                                                self.request,
                                                            )

                                                            logFile = pathfinal.replace(
                                                                ".json", ".log"
                                                            )
                                                            if os.path.exists(logFile):
                                                                doc = minidom.parse(
                                                                    logFile
                                                                )
                                                                errors = doc.getElementsByTagName(
                                                                    "error"
                                                                )
                                                                response = Response(
                                                                    status=401,
                                                                    body=self._(
                                                                        "The data could not be registered. ERROR: "
                                                                        + errors[
                                                                            0
                                                                        ].getAttribute(
                                                                            "Error"
                                                                        )
                                                                    ),
                                                                )
                                                                return response

                                                            print("****************Estoy acá********")
                                                            for plugin in p.PluginImplementations(p.ISubmissionStorage):
                                                                plugin.report_data_entry_to_a_project(self.request,
                                                                                                      self.user.login,
                                                                                                      "xxxx",
                                                                                                      "API user")

                                                            print("****************Estoy acá y salí********")
                                                            response = Response(
                                                                status=200,
                                                                body=self._(
                                                                    "Data registered."
                                                                ),
                                                            )
                                                            return response
                                                        else:
                                                            response = Response(
                                                                status=401,
                                                                body=self._(
                                                                    "ERROR: You do not have a package code with this ID."
                                                                ),
                                                            )
                                                            return response
                                                    else:
                                                        response = Response(
                                                            status=401,
                                                            body=self._(
                                                                "ERROR: The package code must be a number."
                                                            ),
                                                        )
                                                        return response
                                                else:
                                                    response = Response(
                                                        status=401,
                                                        body=self._(
                                                            "Error in the JSON. Not all parameters have data."
                                                        ),
                                                    )
                                                    return response
                                            else:
                                                response = Response(
                                                    status=401,
                                                    body=self._(
                                                        "Error in the JSON sent by parameter. Check the obligatory Keys: "
                                                        + str(obligatoryQuestions)
                                                    ),
                                                )
                                                return response
                                        else:
                                            # getWrongKeys(possibleQuestions,_json)
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "Error in the JSON sent by parameter. Check the permited Keys: "
                                                    + str(possibleQuestions)
                                                ),
                                            )
                                            return response
                                    except Exception as e:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "Error in the JSON sent by parameter. "
                                                + str(e)
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This project do not have structure."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "Registration has closed. No more participants can be registered."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401, body=self._("Registration has not started.")
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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


class readRegistryData_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.body)
            except:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON, It does not have the 'body' parameter."
                    ),
                )
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        if not projectRegStatus(
                            self.user.login, dataworking["project_cod"], self.request
                        ):
                            info = getJSONResult(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                                True,
                                False,
                                "",
                            )

                            newJson = {
                                "structure": info["registry"],
                                "data": info["data"],
                            }

                            response = Response(status=200, body=json.dumps(newJson),)
                            return response
                        else:
                            response = Response(
                                status=401, body=self._("Registration has not started.")
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response
