import datetime
import json
import os
import uuid
from xml.dom import minidom

from pyramid.response import Response

from climmob.processes import (
    thereIsAnEqualEnumIdInTheProject,
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
    update_project_status,
)
from climmob.views.Api.projectRegistryStart import functionForProcessAndValidateUpdate
from climmob.processes.odk.api import storeJSONInMySQL, review_multimedia_content
from climmob.products.forms.form import create_document_form
from climmob.views.classes import apiView
from climmob.views.registry import getDataFormPreview
from climmob.views.validators import TextField
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator
from climmob.views.validators.project import (
    ProjectOpenValidator,
)


class CreateProjectAssessmentView(apiView):
    valid_fields = (
        TextField("project_cod"),
        TextField("user_owner"),
        TextField("ass_cod"),
    )
    validators = (
        ProjectExistsValidator,
        ProjectOpenValidator,
    )

    def post(self):
        dataworking = json.loads(self.body)
        dataworking["user_name"] = self.user.login
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
                        sectionOfThePackageCode = getTheGroupOfThePackageCodeAssessment(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        )
                        projectDetails = getProjectData(activeProjectId, self.request)
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
                                    (data, finalCloseQst,) = getDataFormPreview(
                                        self,
                                        dataworking["user_owner"],
                                        activeProjectId,
                                        assessmentid=dataworking["ass_cod"],
                                        language=lang["lang_code"],
                                    )

                                    lang["Data"] = data

                                dataPreviewInMultipleLanguages = languages
                            else:
                                (data, finalCloseQst,) = getDataFormPreview(
                                    self,
                                    dataworking["user_owner"],
                                    activeProjectId,
                                    assessmentid=dataworking["ass_cod"],
                                    language="en",
                                )
                                dataPreviewInMultipleLanguages = [
                                    {
                                        "lang_code": self.request.locale_name,
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
                                listOfLabels,
                            )

                            update_project_status(activeProjectId, 2, self.request)

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
                                + (
                                    correct[0]["error"].decode("utf-8")
                                    if isinstance(correct[0]["error"], bytes)
                                    else correct[0]["error"]
                                ),
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
                        body=self._("You must have created the assessment forms."),
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
                    "You cannot add data collection moments. You already started data collection."
                ),
            )
            return response


class CancelAssessmentApiView(apiView):
    valid_fields = (
        TextField("project_cod"),
        TextField("user_owner"),
        TextField("ass_cod"),
    )
    validators = (
        ProjectExistsValidator,
        ProjectOpenValidator,
    )

    def post(self):
        dataworking = json.loads(self.body)
        dataworking["user_name"] = self.user.login
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

        if isAssessmentOpen(
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

            response = Response(status=200, body=self._("Cancel data collection"))
            return response

        else:
            response = Response(
                status=401,
                body=self._("Data collection has not started. You cannot cancel it."),
            )
            return response


class CloseAssessmentApiView(apiView):
    valid_fields = (
        TextField("project_cod"),
        TextField("user_owner"),
        TextField("ass_cod"),
    )
    validators = (
        ProjectExistsValidator,
        ProjectOpenValidator,
    )

    def post(self):

        dataworking = json.loads(self.body)
        dataworking["user_name"] = self.user.login
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
                response = Response(status=200, body=self._("Data collection closed."))
                return response

            else:
                response = Response(
                    status=401,
                    body=self._("There is no data collection with that code."),
                )
                return response
        else:
            response = Response(
                status=401,
                body=self._("Data collection has not started. You cannot cancel it."),
            )
            return response


class ReadAssessmentStructureView(apiView):
    valid_fields = (
        TextField("project_cod"),
        TextField("user_owner"),
        TextField("ass_cod"),
    )
    validators = (ProjectExistsValidator,)

    def get(self):
        dataworking = json.loads(self.body)
        dataworking["user_name"] = self.user.login
        dataworking["section_private"] = None
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
                    body=self._("There is no data collection with that code."),
                )
                return response
        else:
            response = Response(
                status=401,
                body=self._("Data collection has not started."),
            )
            return response


class PushJsonToAssessmentView(apiView):
    valid_fields = (
        TextField("project_cod"),
        TextField("user_owner"),
        TextField("ass_cod"),
        TextField("json"),
    )
    validators = (
        ProjectExistsValidator,
        ProjectOpenValidator,
    )

    def post(self):
        dataworking = json.loads(self.body)
        dataworking["user_name"] = self.user.login
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
                body=self._("There is no data collection with that code."),
            )
            return response


def ApiAssessmentPushProcess(self, structure, dataworking, activeProjectId):
    if structure:
        numComb = numberOfCombinationsForTheProject(
            activeProjectId,
            self.request,
        )
        obligatoryQuestions = []
        possibleQuestions = ["clm_start", "clm_end", "_submitted_date", "_submitted_by"]
        searchQST163 = ""
        groupsForValidation = {}
        media_questions = []
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

                if question["question_dtype"] in ["video", "audio", "image"]:
                    media_questions.append(
                        {
                            "type": question["question_dtype"],
                            "datafield": question["question_datafield"],
                        }
                    )

        try:
            _json = json.loads(dataworking["json"])
            _json["_submitted_date"] = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            permitedKeys = True
            for key in _json.keys():
                if key not in possibleQuestions:
                    # print(key)
                    permitedKeys = False

            if permitedKeys:
                obligatoryKeys = True
                for key in obligatoryQuestions:
                    if key not in _json.keys():
                        obligatoryKeys = False

                if obligatoryKeys:

                    dataInParams = True
                    paramsWithoutData = []
                    for key in obligatoryQuestions:
                        if _json[key].strip(" ") == "":
                            dataInParams = False
                            paramsWithoutData.append(key)

                    if dataInParams:

                        if "_submitted_by" in _json.keys():
                            if not thereIsAnEqualEnumIdInTheProject(
                                _json["_submitted_by"], activeProjectId, self.request
                            ):
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no field agent with that ID assigned to the project. Please check the key: _submitted_by"
                                    ),
                                )
                                return response

                        if not "clm_start" in _json.keys() or _json["clm_start"] == "":
                            _json["clm_start"] = datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )

                        if not "clm_end" in _json.keys() or _json["clm_end"] == "":
                            _json["clm_end"] = datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )

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

                            media_result, error_message = review_multimedia_content(
                                media_questions, _json, self
                            )
                            if not media_result:
                                response = Response(
                                    status=401,
                                    body=error_message,
                                )
                                return response

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
                            pathxml = os.path.join(
                                self.request.registry.settings["user.repository"],
                                *[
                                    dataworking["user_owner"],
                                    dataworking["project_cod"],
                                    "data",
                                    "ass",
                                    dataworking["ass_cod"],
                                    "xml",
                                    uniqueId,
                                ]
                            )

                            if not os.path.exists(path):
                                os.makedirs(path)
                                if media_questions:
                                    os.makedirs(pathxml)
                                    infoFile = os.path.join(
                                        pathxml, str(uniqueId) + ".info"
                                    )
                                    file = open(infoFile, "w")
                                    file.write(uniqueId + " API")
                                    file.close()

                            for file in self.request.POST.getall("media"):
                                filename = file.filename.lower()
                                full_path = os.path.join(pathxml, filename)
                                # print(full_path)

                                with open(full_path, "wb") as f:
                                    f.write(file.file.read())

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
                                "Error in the JSON. Not all parameters have data. Check the columns: {}.".format(
                                    str(", ".join(map(str, paramsWithoutData)))
                                )
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._(
                            "Error in the JSON sent by parameter. Check the obligatory Keys: {}.".format(
                                str(", ".join(map(str, obligatoryQuestions)))
                            )
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
        except Exception as e:
            response = Response(
                status=401,
                body=self._("Error in the JSON sent by parameter." + str(e)),
            )
            return response
    else:
        response = Response(
            status=401,
            body=self._("The data do not have structure."),
        )
        return response


class ReadAssessmentDataView(apiView):
    valid_fields = (
        TextField("project_cod"),
        TextField("user_owner"),
        TextField("ass_cod"),
    )
    validators = (ProjectExistsValidator,)

    def get(self):
        dataworking = json.loads(self.body)
        dataworking["user_name"] = self.user.login
        dataworking["section_private"] = None
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
                    body=self._("There is no data collection with that code."),
                )
                return response
        else:
            response = Response(
                status=401,
                body=self._("Data collection has not started."),
            )
            return response


class AssessmentDataCleaningView(apiView):
    valid_fields = (
        TextField("project_cod"),
        TextField("user_owner"),
        TextField("ass_cod"),
        TextField("json"),
    )
    validators = (
        ProjectExistsValidator,
        ProjectOpenValidator,
    )

    def post(self):
        dataworking = json.loads(self.body)
        dataworking["user_name"] = self.user.login
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
                body=self._("There is no data collection with that code."),
            )
            return response
