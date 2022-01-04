from climmob.views.classes import apiView
from climmob.processes import (
    projectExists,
    projectRegStatus,
    createCombinations,
    getCombinations,
    getCombinationStatus,
    setCombinationStatus,
    getProjectProgress,
    projectCreateCombinations,
    getPackages,
    projectCreatePackages,
    setRegistryStatus,
    generateStructureForInterfaceForms,
    isRegistryClose,
    getProjectNumobs,
    getJSONResult,
    getTheProjectIdForOwner,
    getAccessTypeForProject,
    getProjectData,
    setCombinationQuantityAvailable,
    updateCreatePackages,
    deleteProjectPackages,
)
from climmob.products.randomization.randomization import create_randomization
from climmob.views.project_combinations import createSettings
from climmob.products import stopTasksByProcess
from climmob.processes.odk.api import storeJSONInMySQL
from climmob.views.project_combinations import startTheRegistry
from pyramid.response import Response
from xml.dom import minidom
import json
import datetime
import os
import uuid


class readProjectCombinations_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod", u"user_owner"]
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
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )

                        progress, pcompleted = getProjectProgress(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            activeProjectId,
                            self.request,
                        )
                        if (
                            progress["enumerators"] == True
                            and progress["technology"] == True
                            and progress["techalias"] == True
                            and progress["registry"] == True
                        ):

                            createCombinations(
                                dataworking["user_owner"],
                                activeProjectId,
                                dataworking["project_cod"],
                                self.request,
                            )
                            techs, ncombs, combs, = getCombinations(
                                activeProjectId, self.request,
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
                                            "quantity_available": combs[pos2 - 1][
                                                "quantity_available"
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
                                    "quantity_available": combs[pos2 - 1][
                                        "quantity_available"
                                    ],
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
            obligatory = [u"project_cod", u"user_owner", u"ncomb", u"status"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to set usable combinations."
                                ),
                            )
                            return response

                        if projectRegStatus(activeProjectId, self.request):
                            progress, pcompleted = getProjectProgress(
                                dataworking["user_owner"],
                                dataworking["project_cod"],
                                activeProjectId,
                                self.request,
                            )
                            if (
                                progress["enumerators"] == True
                                and progress["technology"] == True
                                and progress["techalias"] == True
                                and progress["registry"] == True
                            ):
                                if not projectCreateCombinations(
                                    activeProjectId, self.request,
                                ):
                                    exits, status = getCombinationStatus(
                                        activeProjectId,
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
                                                    activeProjectId,
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


class setAvailabilityCombination_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"user_owner", u"ncomb", u"availability"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to set usable combinations."
                                ),
                            )
                            return response

                        if projectRegStatus(activeProjectId, self.request):
                            progress, pcompleted = getProjectProgress(
                                dataworking["user_owner"],
                                dataworking["project_cod"],
                                activeProjectId,
                                self.request,
                            )
                            if (
                                progress["enumerators"] == True
                                and progress["technology"] == True
                                and progress["techalias"] == True
                                and progress["registry"] == True
                            ):
                                if not projectCreateCombinations(
                                    activeProjectId, self.request,
                                ):
                                    exits, status = getCombinationStatus(
                                        activeProjectId,
                                        dataworking["ncomb"],
                                        self.request,
                                    )
                                    if exits:
                                        if dataworking["availability"].isnumeric():

                                            setCombinationQuantityAvailable(
                                                activeProjectId,
                                                dataworking["ncomb"],
                                                dataworking["availability"],
                                                self.request,
                                            )

                                            response = Response(
                                                status=200,
                                                body=self._(
                                                    "The availability of the combination was changed."
                                                ),
                                            )
                                            return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "The number of items available in the combination must be an integer."
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
            obligatory = [u"project_cod", u"user_owner"]
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
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to create packages."
                                ),
                            )
                            return response

                        progress, pcompleted = getProjectProgress(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            activeProjectId,
                            self.request,
                        )
                        if (
                            progress["enumerators"] == True
                            and progress["technology"] == True
                            and progress["techalias"] == True
                            and progress["registry"] == True
                        ):
                            if not projectCreateCombinations(
                                activeProjectId, self.request,
                            ):
                                prjData = getProjectData(activeProjectId, self.request)
                                # Only create the packages if its needed
                                if prjData["project_createpkgs"] == 1:

                                    up = updateCreatePackages(
                                        activeProjectId, 2, self.request
                                    )

                                    dl = deleteProjectPackages(
                                        activeProjectId, self.request
                                    )

                                    settings = createSettings(self.request)
                                    create_randomization(
                                        self.request,
                                        self.request.locale_name,
                                        dataworking["user_owner"],
                                        activeProjectId,
                                        dataworking["project_cod"],
                                        settings,
                                    )

                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "ClimMob has started the package creation process, please check back in a moment to verify that the process has been completed."
                                        ),
                                    )
                                    return response

                                if prjData["project_createpkgs"] == 2:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "ClimMob is still generating the packages, please try this request again in a moment."
                                        ),
                                    )
                                    return response

                                if prjData["project_createpkgs"] == 3:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "There was a problem with the creation of the packages please check the available quantity of each combination."
                                        ),
                                    )
                                    return response

                                if prjData["project_createpkgs"] == 0:
                                    ncombs, packages = getPackages(
                                        dataworking["user_owner"],
                                        activeProjectId,
                                        self.request,
                                    )

                                    response = Response(
                                        status=200,
                                        body=json.dumps(
                                            {
                                                "packages": packages,
                                                "combinations": ncombs,
                                            },
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
            obligatory = [u"project_cod", u"user_owner"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to create the registry."
                                ),
                            )
                            return response

                        if projectRegStatus(activeProjectId, self.request):
                            progress, pcompleted = getProjectProgress(
                                dataworking["user_owner"],
                                dataworking["project_cod"],
                                activeProjectId,
                                self.request,
                            )
                            if (
                                progress["enumerators"] == True
                                and progress["technology"] == True
                                and progress["techalias"] == True
                                and progress["registry"] == True
                            ):
                                if not projectCreateCombinations(
                                    activeProjectId, self.request,
                                ):
                                    if not projectCreatePackages(
                                        activeProjectId, self.request,
                                    ):
                                        projectDetails = getProjectData(
                                            activeProjectId, self.request
                                        )

                                        startIsOk, error = startTheRegistry(
                                            self,
                                            dataworking["user_owner"],
                                            activeProjectId,
                                            dataworking["project_cod"],
                                            [
                                                projectDetails["project_label_a"],
                                                projectDetails["project_label_b"],
                                                projectDetails["project_label_c"],
                                            ],
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
            obligatory = [u"project_cod", u"user_owner"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to cancel the registry."
                                ),
                            )
                            return response

                        if not projectRegStatus(activeProjectId, self.request):
                            setRegistryStatus(
                                dataworking["user_owner"],
                                dataworking["project_cod"],
                                activeProjectId,
                                0,
                                self.request,
                            )
                            stopTasksByProcess(
                                self.request, activeProjectId,
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
            obligatory = [u"project_cod", u"user_owner"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to finish the registry."
                                ),
                            )
                            return response

                        if not projectRegStatus(activeProjectId, self.request):

                            progress, pcompleted = getProjectProgress(
                                dataworking["user_owner"],
                                dataworking["project_cod"],
                                activeProjectId,
                                self.request,
                            )
                            if progress["regtotal"] > 0:
                                setRegistryStatus(
                                    dataworking["user_owner"],
                                    dataworking["project_cod"],
                                    activeProjectId,
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
            obligatory = [u"project_cod", u"user_owner"]
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
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )

                        if not projectRegStatus(activeProjectId, self.request):
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    generateStructureForInterfaceForms(
                                        dataworking["user_owner"],
                                        activeProjectId,
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
            obligatory = [u"project_cod", u"user_owner", u"json"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to push information to the project."
                                ),
                            )
                            return response

                        if not projectRegStatus(activeProjectId, self.request):
                            if not isRegistryClose(activeProjectId, self.request,):
                                structure = generateStructureForInterfaceForms(
                                    dataworking["user_owner"],
                                    activeProjectId,
                                    dataworking["project_cod"],
                                    "registry",
                                    self.request,
                                )

                                return ApiRegistrationPushProcess(self, structure, dataworking, activeProjectId)
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


def ApiRegistrationPushProcess(self, structure, dataworking, activeProjectId):
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
                                activeProjectId,
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
                                        dataworking[
                                            "user_owner"
                                        ],
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
                                    self.user.login,
                                    "REG",
                                    dataworking[
                                        "user_owner"
                                    ],
                                    None,
                                    dataworking[
                                        "project_cod"
                                    ],
                                    None,
                                    pathfinal,
                                    self.request,
                                    activeProjectId,
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

class readRegistryData_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod", u"user_owner"]
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
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )

                        if not projectRegStatus(activeProjectId, self.request):
                            info = getJSONResult(
                                dataworking["user_owner"],
                                activeProjectId,
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
