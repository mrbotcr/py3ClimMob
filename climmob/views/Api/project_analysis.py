from climmob.views.classes import apiView
from climmob.processes import (
    projectExists,
    getJSONResult,
    getQuestionsByType,
    getProjectProgress,
    getProjectData,
    getTheProjectIdForOwner,
    getAccessTypeForProject,
)
from climmob.views.project_analysis import processToGenerateTheReport
from pyramid.response import Response
import json


class readDataOfProjectView_api(apiView):
    def processView(self):

        if self.request.method == "GET":

            obligatory = ["project_cod", "user_owner"]
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

                    response = Response(
                        status=200,
                        body=json.dumps(
                            getJSONResult(
                                dataworking["user_owner"],
                                activeProjectId,
                                dataworking["project_cod"],
                                self.request,
                            )
                        ),
                    )
                    return response
                else:
                    response = Response(
                        status=401, body=self._("This project does not exist.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class readVariablesForAnalysisView_api(apiView):
    def processView(self):

        if self.request.method == "GET":

            obligatory = ["project_cod", "user_owner"]
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
                                "The access assigned for this project does not allow you to create an analysis."
                            ),
                        )
                        return response

                    infoProject = getProjectData(activeProjectId, self.request)
                    progress, pcompleted = getProjectProgress(
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        activeProjectId,
                        self.request,
                    )

                    total_ass_records = 0
                    for assessment in progress["assessments"]:
                        if (
                            assessment["ass_status"] == 1
                            or assessment["ass_status"] == 2
                        ):
                            total_ass_records = (
                                total_ass_records + assessment["asstotal"]
                            )

                    if (
                        infoProject["project_registration_and_analysis"] == 1
                        and progress["regtotal"] >= 5
                    ) or (total_ass_records > 0):

                        dataForAnalysis, assessmentsList = getQuestionsByType(
                            activeProjectId, self.request
                        )

                        response = Response(
                            status=200,
                            body=json.dumps(
                                {
                                    "dataForAnalysis": dataForAnalysis,
                                    "assessmentsList": assessmentsList,
                                }
                            ),
                        )
                        return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You don't have the amount of information needed to do a ClimMob analysis."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401, body=self._("This project does not exist.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class generateAnalysisByApiView_api(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                "project_cod",
                "user_owner",
                "variables_to_analyze",
                "infosheets",
            ]
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
                                "The access assigned for this project does not allow you to create an analysis."
                            ),
                        )
                        return response

                    infoProject = getProjectData(activeProjectId, self.request)
                    progress, pcompleted = getProjectProgress(
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        activeProjectId,
                        self.request,
                    )

                    total_ass_records = 0
                    for assessment in progress["assessments"]:
                        if (
                            assessment["ass_status"] == 1
                            or assessment["ass_status"] == 2
                        ):
                            total_ass_records = (
                                total_ass_records + assessment["asstotal"]
                            )

                    if (
                        infoProject["project_registration_and_analysis"] == 1
                        and progress["regtotal"] >= 5
                    ) or (total_ass_records > 0):

                        try:
                            variables = dataworking["variables_to_analyze"]
                            if type(variables) == list:
                                dataForAnalysis, assessmentsList = getQuestionsByType(
                                    activeProjectId, self.request
                                )
                                listOfAllowedVariables = []
                                for _key in dataForAnalysis:
                                    for _variable in dataForAnalysis[_key]:
                                        listOfAllowedVariables.append(
                                            _variable["codeForAnalysis"]
                                        )

                                errorInVariables = False
                                for variable in variables:
                                    if variable not in listOfAllowedVariables:
                                        errorInVariables = True

                                if not errorInVariables:

                                    if dataworking["variables_to_analyze"]:
                                        if str(dataworking["infosheets"]) == "1":
                                            infosheet = "TRUE"
                                        else:
                                            infosheet = "FALSE"

                                        dataworking["project_id"] = activeProjectId
                                        dataworking["owner"] = {}
                                        dataworking["owner"]["user_name"] = dataworking[
                                            "user_owner"
                                        ]
                                        pro = processToGenerateTheReport(
                                            dataworking,
                                            self.request,
                                            variables,
                                            infosheet,
                                            "",
                                        )

                                        response = Response(
                                            status=200,
                                            body=self._(
                                                "The analysis is being generated, it is a process that requires time to be processed, as soon as it is ready you will be able to see it in the download list."
                                            ),
                                        )
                                        return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "The variable_to_analyze parameter must contain data."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "One of the variables you sent for analysis does not exist."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The variable_to_analyze parameter must be a list."
                                    ),
                                )
                                return response
                        except Exception as e:
                            print(e)
                            response = Response(
                                status=401,
                                body=self._(
                                    "Problem with the data sent in the parameter: variables_to_analyze"
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You don't have the amount of information needed to do a ClimMob analysis."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401, body=self._("This project does not exist.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
