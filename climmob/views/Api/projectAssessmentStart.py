import json
import os
import uuid
from xml.dom import minidom

from pyramid.response import Response

from climmob.processes import (
    projectExists,
    projectAsessmentStatus,
    getProjectProgress,
    checkAssessments,
    generateAssessmentFiles,
    assessmentExists,
    generateStructureForInterfaceForms,
    isAssessmentOpen,
    numberOfCombinationsForTheProject,
    setAssessmentIndividualStatus,
    getPackages,
    getJSONResult,
    getTheGroupOfThePackageCodeAssessment,
    getProjectData,
    getTheProjectIdForOwner,
    getAccessTypeForProject,
)
from climmob.processes.odk.api import storeJSONInMySQL
from climmob.products.forms.form import create_document_form
from climmob.views.classes import apiView
from climmob.views.registry import getDataFormPreview


class createProjectAssessment_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "ass_cod"]
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
                                    "The access assigned for this project does not allow you to do this action."
                                ),
                            )
                            return response
                        progress, pcompleted = getProjectProgress(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            activeProjectId,
                            self.request,
                        )
                        if progress["regsubmissions"] == 2:
                            if projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                if progress["assessment"] == True:
                                    checkPass, errors = checkAssessments(
                                        activeProjectId,
                                        dataworking["ass_cod"],
                                        self.request,
                                    )
                                    if checkPass:
                                        sectionOfThePackageCode = (
                                            getTheGroupOfThePackageCodeAssessment(
                                                activeProjectId,
                                                dataworking["ass_cod"],
                                                self.request,
                                            )
                                        )
                                        projectDetails = getProjectData(
                                            activeProjectId, self.request
                                        )
                                        listOfLabels = [
                                            projectDetails["project_label_a"],
                                            projectDetails["project_label_b"],
                                            projectDetails["project_label_c"],
                                        ]

                                        correct = generateAssessmentFiles(
                                            dataworking["user_owner"],
                                            activeProjectId,
                                            dataworking["project_cod"],
                                            dataworking["ass_cod"],
                                            self.request,
                                            sectionOfThePackageCode,
                                            listOfLabels,
                                        )
                                        if correct[0]["result"]:
                                            setAssessmentIndividualStatus(
                                                activeProjectId,
                                                dataworking["ass_cod"],
                                                1,
                                                self.request,
                                            )

                                            ncombs, packages = getPackages(
                                                dataworking["user_owner"],
                                                activeProjectId,
                                                self.request,
                                            )

                                            languages = projectDetails["languages"]
                                            if languages:
                                                for lang in languages:
                                                    (
                                                        data,
                                                        finalCloseQst,
                                                    ) = getDataFormPreview(
                                                        self,
                                                        dataworking["user_owner"],
                                                        activeProjectId,
                                                        assessmentid=dataworking[
                                                            "ass_cod"
                                                        ],
                                                        language=lang["lang_code"],
                                                    )

                                                    lang["Data"] = data

                                                dataPreviewInMultipleLanguages = (
                                                    languages
                                                )
                                            else:
                                                (
                                                    data,
                                                    finalCloseQst,
                                                ) = getDataFormPreview(
                                                    self,
                                                    dataworking["user_owner"],
                                                    activeProjectId,
                                                    assessmentid=dataworking["ass_cod"],
                                                )
                                                dataPreviewInMultipleLanguages = [
                                                    {
                                                        "lang_name": "Default",
                                                        "Data": data,
                                                    }
                                                ]

                                            create_document_form(
                                                self.request,
                                                self.request.locale_name,
                                                dataworking["user_owner"],
                                                activeProjectId,
                                                dataworking["project_cod"],
                                                "Assessment",
                                                dataworking["ass_cod"],
                                                dataPreviewInMultipleLanguages,
                                                packages,
                                                listOfLabels,
                                            )

                                            response = Response(
                                                status=200,
                                                body=self._("Data collection started."),
                                            )
                                            return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "There has been a problem in the creation of the basic structure of the project, this may be due to something wrong with the form. Contact the ClimMob team with the next message to get the solution to the problem"
                                                )
                                                + ": "
                                                + str(correct[0]["error"], "utf-8"),
                                            )
                                            return response

                                    else:
                                        response = Response(
                                            status=401,
                                            body=json.dumps({"errors": errors}),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You must have created the assessment forms."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("Data collection has already started."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You cannot add data collection moments. You alreaday started data collection."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not project with that code."),
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


class cancelAssessmentApi_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "ass_cod"]
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
                                    "The access assigned for this project does not allow you to cancel the assessment."
                                ),
                            )
                            return response

                        if not projectAsessmentStatus(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):

                            setAssessmentIndividualStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                0,
                                self.request,
                            )

                            response = Response(
                                status=200, body=self._("Cancel data collection")
                            )
                            return response

                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "Data collection has not started. You cannot cancel it."
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


class closeAssessmentApi_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "ass_cod"]
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
                                    "The access assigned for this project does not allow you to cancel the assessment."
                                ),
                            )
                            return response

                        if not projectAsessmentStatus(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if assessmentExists(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):

                                setAssessmentIndividualStatus(
                                    activeProjectId,
                                    dataworking["ass_cod"],
                                    2,
                                    self.request,
                                )
                                response = Response(
                                    status=200, body=self._("Data collection closed.")
                                )
                                return response

                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no data collection with that code."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "Data collection has not started. You cannot cancel it."
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


class readAssessmentStructure_view(apiView):
    def processView(self):
        if self.request.method == "GET":
            obligatory = ["project_cod", "user_owner", "ass_cod"]
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
                dataworking["section_private"] = None

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

                        if not projectAsessmentStatus(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if assessmentExists(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                response = Response(
                                    status=200,
                                    body=json.dumps(
                                        generateStructureForInterfaceForms(
                                            dataworking["user_owner"],
                                            activeProjectId,
                                            dataworking["project_cod"],
                                            "assessment",
                                            self.request,
                                            ass_cod=dataworking["ass_cod"],
                                        )
                                    ),
                                )
                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no data collection with that code."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("Data collection has not started."),
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


class pushJsonToAssessment_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "ass_cod", "json"]
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
                                    "The access assigned for this project does not allow you to push information."
                                ),
                            )
                            return response

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if not projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                if isAssessmentOpen(
                                    activeProjectId,
                                    dataworking["ass_cod"],
                                    self.request,
                                ):
                                    structure = generateStructureForInterfaceForms(
                                        dataworking["user_owner"],
                                        activeProjectId,
                                        dataworking["project_cod"],
                                        "assessment",
                                        self.request,
                                        ass_cod=dataworking["ass_cod"],
                                    )

                                    return ApiAssessmentPushProcess(
                                        self, structure, dataworking, activeProjectId
                                    )

                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "Data collection is closed. After you close data collection, no more data can be entered."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("Data collection has not started."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is no data collection with that code."
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


def ApiAssessmentPushProcess(self, structure, dataworking, activeProjectId):
    if structure:
        numComb = numberOfCombinationsForTheProject(
            activeProjectId,
            self.request,
        )
        obligatoryQuestions = []
        possibleQuestions = []
        searchQST163 = ""
        groupsForValidation = {}
        for section in structure:
            for question in section["section_questions"]:

                possibleQuestions.append(question["question_datafield"])

                if question["question_requiredvalue"] == 1:
                    obligatoryQuestions.append(question["question_datafield"])

                if question["question_dtype2"] == 9:
                    if question["question_code"] not in groupsForValidation.keys():
                        groupsForValidation[question["question_code"]] = []

                    groupsForValidation[question["question_code"]].append(
                        question["question_datafield"]
                    )

                if question["question_code"] == "QST163":
                    searchQST163 = question["question_datafield"]

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
                        if _json[searchQST163].isdigit():
                            # Validation for repeat response
                            for _group in groupsForValidation:
                                letter = []
                                for _var in groupsForValidation[_group]:

                                    if (
                                        (not _json[_var] in letter)
                                        or str(_json[_var]) == "98"
                                        or str(_json[_var]) == "99"
                                    ):
                                        letter.append(_json[_var])
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "You have repeated data in the next column: "
                                                + _var
                                                + ". Remember that the options can not be repeated."
                                            ),
                                        )
                                        return response

                            # I don't validate el identify of the farmer because the ODK return error if not exist
                            _json["clm_deviceimei"] = "API_" + str(self.apiKey)
                            uniqueId = str(uuid.uuid1())
                            path = os.path.join(
                                self.request.registry.settings["user.repository"],
                                *[
                                    dataworking["user_owner"],
                                    dataworking["project_cod"],
                                    "data",
                                    "ass",
                                    dataworking["ass_cod"],
                                    "json",
                                    uniqueId,
                                ]
                            )

                            if not os.path.exists(path):
                                os.makedirs(path)

                            pathfinal = os.path.join(path, uniqueId + ".json")

                            f = open(pathfinal, "w")
                            f.write(json.dumps(_json))
                            f.close()

                            storeJSONInMySQL(
                                self.user.login,
                                "ASS",
                                dataworking["user_owner"],
                                None,
                                dataworking["project_cod"],
                                dataworking["ass_cod"],
                                pathfinal,
                                self.request,
                                activeProjectId,
                            )

                            logFile = pathfinal.replace(".json", ".log")
                            if os.path.exists(logFile):
                                doc = minidom.parse(logFile)
                                errors = doc.getElementsByTagName("error")
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The data could not be saved. ERROR: "
                                        + errors[0].getAttribute("Error")
                                    ),
                                )
                                return response

                            response = Response(
                                status=200,
                                body=self._("Data registered."),
                            )
                            return response

                        else:
                            response = Response(
                                status=401,
                                body=self._("ERROR: The farmer code must be a number."),
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
                            "Error in the JSON sent by parameter. Check the obligatory Keys."
                        ),
                    )
                    return response
            else:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON sent by parameter. Check the permitted Keys."
                    ),
                )
                return response
        except:
            response = Response(
                status=401,
                body=self._("Error in the JSON sent by parameter."),
            )
            return response
    else:
        response = Response(
            status=401,
            body=self._("The data do not have structure."),
        )
        return response


class readAssessmentData_view(apiView):
    def processView(self):
        if self.request.method == "GET":
            obligatory = ["project_cod", "user_owner", "ass_cod"]
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
                dataworking["section_private"] = None

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

                        if not projectAsessmentStatus(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if assessmentExists(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                info = getJSONResult(
                                    dataworking["user_owner"],
                                    activeProjectId,
                                    dataworking["project_cod"],
                                    self.request,
                                    True,
                                    True,
                                    dataworking["ass_cod"],
                                )

                                newJson = {
                                    "structure": info["assessments"][0],
                                    "data": info["data"],
                                }

                                response = Response(
                                    status=200,
                                    body=json.dumps(newJson),
                                )
                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no data collection with that code."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("Data collection has not started."),
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


from climmob.views.Api.projectRegistryStart import functionForProcessAndValidateUpdate


class assessmentDataCleaning_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "ass_cod", "json"]
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
                                    "The access assigned for this project does not allow you to push information."
                                ),
                            )
                            return response

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if not projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                if isAssessmentOpen(
                                    activeProjectId,
                                    dataworking["ass_cod"],
                                    self.request,
                                ):
                                    structure = generateStructureForInterfaceForms(
                                        dataworking["user_owner"],
                                        activeProjectId,
                                        dataworking["project_cod"],
                                        "assessment",
                                        self.request,
                                        ass_cod=dataworking["ass_cod"],
                                    )

                                    return functionForProcessAndValidateUpdate(
                                        self,
                                        structure,
                                        dataworking,
                                        activeProjectId,
                                        dataworking["user_owner"],
                                        dataworking["project_cod"],
                                        "ass",
                                        code=dataworking["ass_cod"],
                                    )

                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "Data collection is closed. After you close data collection, no more data can be entered."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("Data collection has not started."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is no data collection with that code."
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
