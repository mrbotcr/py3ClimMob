import datetime
import json
import re

from pyramid.response import Response

from climmob.processes import (
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
    getTheProjectIdForOwner,
    getAccessTypeForProject,
    theUserBelongsToTheProject,
    add_project_collaborator,
    getUserInfo,
    remove_collaborator,
    get_collaborators_in_project,
    getProjectIsTemplate,
    getProjectAssessments,
    deleteRegistryByProjectId,
    deleteProjectAssessments,
    getProjectTemplates,
    addPrjLang,
    languageExistInI18nUser,
    get_all_project_location,
    get_location_by_id,
    get_all_unit_of_analysis_by_location,
    get_unit_of_analysis_by_id,
    get_location_unit_of_analysis_by_combination,
    get_all_objectives_by_location_and_unit_of_analysis,
    get_location_unit_of_analysis_objectives_by_combination,
    add_project_location_unit_objective,
    delete_all_project_location_unit_objective,
)
from climmob.views.classes import apiView
from climmob.views.project import functionCreateClone


class ReadListOfTemplatesView(apiView):
    def processView(self):
        if self.request.method == "GET":

            obligatory = ["project_type"]

            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:

                    response = Response(
                        status=200,
                        body=json.dumps(
                            getProjectTemplates(
                                self.request, dataworking["project_type"]
                            )
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class ReadListOfCountriesView(apiView):
    def processView(self):

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(getCountryList(self.request)),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class ReadListOfLocationsView(apiView):
    def processView(self):

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(
                    get_all_project_location(self.request, method_from_schema="API")
                ),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class ReadListOfUnitOfAnalysisView(apiView):
    def processView(self):

        if self.request.method == "GET":

            obligatory = ["plocation_id"]

            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:

                    if get_location_by_id(self.request, dataworking["plocation_id"]):

                        response = Response(
                            status=200,
                            body=json.dumps(
                                get_all_unit_of_analysis_by_location(
                                    self.request,
                                    dataworking["plocation_id"],
                                    method_from_schema="API",
                                )
                            ),
                        )
                        return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("The experimental site does not exist."),
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
                    body=self._("Error in the JSON. Parameter plocation_id required."),
                )
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class ReadListOfObjectivesView(apiView):
    def processView(self):

        if self.request.method == "GET":

            obligatory = ["plocation_id", "puoa_id"]

            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:

                    if get_location_by_id(self.request, dataworking["plocation_id"]):

                        if get_unit_of_analysis_by_id(
                            self.request, dataworking["puoa_id"]
                        ):

                            if get_location_unit_of_analysis_by_combination(
                                self.request,
                                dataworking["plocation_id"],
                                dataworking["puoa_id"],
                            ):

                                response = Response(
                                    status=200,
                                    body=json.dumps(
                                        get_all_objectives_by_location_and_unit_of_analysis(
                                            self.request,
                                            dataworking["plocation_id"],
                                            dataworking["puoa_id"],
                                            method_from_schema="API",
                                        )
                                    ),
                                )
                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "This experiment side with this unit of analysis has no defined relationship."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("The unit of analysis does not exist."),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("The experimental site does not exist."),
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
                        "Error in the JSON. Parameter plocation_id and puoa_id required."
                    ),
                )
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class CreateProjectView(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                "project_cod",
                "project_name",
                "project_abstract",
                "project_tags",
                "project_pi",
                "project_piemail",
                "project_affiliation",
                "project_type",
                "project_location",
                "project_unit_of_analysis",
                "project_objectives",
                "project_numobs",
                "project_cnty",
                "project_label_a",
                "project_label_b",
                "project_label_c",
            ]

            possibles = [
                "user_owner",
                "project_cod",
                "project_name",
                "project_abstract",
                "project_tags",
                "project_pi",
                "project_piemail",
                "project_affiliation",
                "project_type",
                "project_location",
                "project_unit_of_analysis",
                "project_objectives",
                "project_numobs",
                "project_cnty",
                "project_clone",
                "project_label_a",
                "project_label_b",
                "project_label_c",
                "project_template",
                "project_languages",
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

                    if not "project_languages" in dataworking.keys():
                        dataworking["project_languages"] = ["en"]
                    else:

                        if type(dataworking["project_languages"]) != list:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The parameter project_languages must be a list."
                                ),
                            )
                            return response

                    dataworking["user_name"] = self.user.login
                    dataworking["project_localvariety"] = 1
                    dataworking["project_regstatus"] = 0
                    dataworking["project_numcom"] = 3

                    dataInParams = True
                    for key in dataworking.keys():
                        if dataworking[key] == "":
                            dataInParams = False

                    if (
                        dataInParams
                        and dataworking["project_languages"]
                        and dataworking["project_objectives"]
                    ):

                        for lang in dataworking["project_languages"]:
                            if not languageExistInI18nUser(
                                lang,
                                self.user.login,
                                self.request,
                            ):
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You are trying to add a language to the project that is not part of the list of languages to be used."
                                    ),
                                )
                                return response

                        if (
                            "project_clone" in dataworking.keys()
                            and "project_template" in dataworking.keys()
                        ):
                            response = Response(
                                status=401,
                                body=self._(
                                    "You cannot create a clone and use a template at the same time."
                                ),
                            )
                            return response

                        try:
                            dataworking["project_type"] = int(
                                dataworking["project_type"]
                            )

                            if dataworking["project_type"] not in [1, 2]:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The parameter project_type must be [1: Real. 2: Training - This project was only used to explain the use of the ClimMob platform and was created as an example]."
                                    ),
                                )
                                return response

                        except:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The parameter project_type must be a number."
                                ),
                            )
                            return response

                        if not get_location_by_id(
                            self.request, dataworking["project_location"]
                        ):
                            response = Response(
                                status=401,
                                body=self._("The project_location does not exist."),
                            )
                            return response

                        if not get_unit_of_analysis_by_id(
                            self.request, dataworking["project_unit_of_analysis"]
                        ):
                            response = Response(
                                status=401,
                                body=self._(
                                    "The project_unit_of_analysis does not exist."
                                ),
                            )
                            return response

                        location_unit_of_analysis = (
                            get_location_unit_of_analysis_by_combination(
                                self.request,
                                dataworking["project_location"],
                                dataworking["project_unit_of_analysis"],
                            )
                        )

                        if not location_unit_of_analysis:
                            response = Response(
                                status=401,
                                body=self._(
                                    "This project_location with this project_unit_of_analysis has no defined relationship."
                                ),
                            )
                            return response

                        dataworking[
                            "project_registration_and_analysis"
                        ] = location_unit_of_analysis["registration_and_analysis"]

                        if not isinstance(dataworking["project_objectives"], list):
                            response = Response(
                                status=401,
                                body=self._(
                                    "project_objectives should be in list format."
                                ),
                            )
                            return response
                        else:
                            for obj in dataworking["project_objectives"]:

                                if not get_location_unit_of_analysis_objectives_by_combination(
                                    self.request,
                                    location_unit_of_analysis["pluoa_id"],
                                    obj,
                                ):
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The objective {} does not correspond to the experiment site and the unit of analysis indicated.".format(
                                                obj
                                            )
                                        ),
                                    )
                                    return response

                        if "project_template" in dataworking.keys():
                            existsTemplate = getProjectIsTemplate(
                                self.request, dataworking["project_template"]
                            )
                            if existsTemplate:
                                if str(
                                    dataworking["project_registration_and_analysis"]
                                ) == str(
                                    existsTemplate["project_registration_and_analysis"]
                                ):
                                    dataworking["usingTemplate"] = dataworking[
                                        "project_template"
                                    ]
                                    dataworking["project_template"] = 0
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You are trying to use a template that does not correspond to the type of project you are creating."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no template with this identifier."
                                    ),
                                )
                                return response

                        if "project_clone" in dataworking.keys():
                            existsproject = projectInDatabase(
                                self.user.login,
                                dataworking["project_clone"],
                                self.request,
                            )
                            if not existsproject:
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
                                            dataworking["project_localvariety"]
                                        ) not in [
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

                                        if (
                                            dataworking["project_label_a"]
                                            != dataworking["project_label_b"]
                                            and dataworking["project_label_a"]
                                            != dataworking["project_label_c"]
                                            and dataworking["project_label_b"]
                                            != dataworking["project_label_c"]
                                        ):

                                            added, idormessage = addProject(
                                                dataworking, self.request
                                            )

                                            if added:

                                                for objective in dataworking[
                                                    "project_objectives"
                                                ]:
                                                    luoao_id = get_location_unit_of_analysis_objectives_by_combination(
                                                        self.request,
                                                        location_unit_of_analysis[
                                                            "pluoa_id"
                                                        ],
                                                        objective,
                                                    )[
                                                        "pluoaobj_id"
                                                    ]

                                                    infoObj = {
                                                        "project_id": idormessage,
                                                        "pluoaobj_id": luoao_id,
                                                    }
                                                    add_project_location_unit_objective(
                                                        infoObj, self.request
                                                    )

                                                if (
                                                    "project_languages"
                                                    in dataworking.keys()
                                                ):
                                                    if dataworking["project_languages"]:

                                                        for index, lang in enumerate(
                                                            dataworking[
                                                                "project_languages"
                                                            ]
                                                        ):
                                                            langInfo = {}
                                                            if index == 1:
                                                                langInfo[
                                                                    "lang_default"
                                                                ] = 1

                                                            langInfo["lang_code"] = lang
                                                            langInfo[
                                                                "project_id"
                                                            ] = idormessage

                                                            (
                                                                apl,
                                                                aplmessage,
                                                            ) = addPrjLang(
                                                                langInfo, self.request
                                                            )

                                                if (
                                                    "project_clone"
                                                    in dataworking.keys()
                                                ):
                                                    dataworking[
                                                        "slt_project_cod"
                                                    ] = dataworking["project_clone"]

                                                    projectId = getTheProjectIdForOwner(
                                                        self.user.login,
                                                        dataworking["project_clone"],
                                                        self.request,
                                                    )

                                                    listOfElementToInclude = [
                                                        "registry",
                                                        "fieldagents",
                                                        "technologies",
                                                        "technologyoptions",
                                                    ]

                                                    assessments = getProjectAssessments(
                                                        projectId,
                                                        self.request,
                                                    )
                                                    for assess in assessments:
                                                        listOfElementToInclude.append(
                                                            assess["ass_cod"]
                                                        )

                                                    ok = functionCreateClone(
                                                        self,
                                                        projectId,
                                                        idormessage,
                                                        listOfElementToInclude,
                                                    )

                                                    response = Response(
                                                        status=200,
                                                        body=self._(
                                                            "Project successfully cloned."
                                                        ),
                                                    )
                                                    return response

                                                if (
                                                    "usingTemplate"
                                                    in dataworking.keys()
                                                ):
                                                    listOfElementToInclude = [
                                                        "registry"
                                                    ]

                                                    assessments = getProjectAssessments(
                                                        dataworking["usingTemplate"],
                                                        self.request,
                                                    )
                                                    for assess in assessments:
                                                        listOfElementToInclude.append(
                                                            assess["ass_cod"]
                                                        )

                                                    newProjectId = (
                                                        getTheProjectIdForOwner(
                                                            self.user.login,
                                                            dataworking["project_cod"],
                                                            self.request,
                                                        )
                                                    )

                                                    functionCreateClone(
                                                        self,
                                                        dataworking["usingTemplate"],
                                                        newProjectId,
                                                        listOfElementToInclude,
                                                    )

                                            if not added:
                                                response = Response(
                                                    status=401, body=idormessage
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
                                                    "The names that the items will receive should be different."
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
                                        body=self._("This project ID already exists."),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The project ID must start with a letter."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "For the project ID only letters and numbers are allowed. The project ID must start with a letter."
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
                            "You are trying to use a parameter that is not allowed."
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


class ReadProjectsView(apiView):
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
                "user_owner",
                "project_cod",
                "project_name",
                "project_abstract",
                "project_tags",
                "project_pi",
                "project_piemail",
                "project_numobs",
                "project_cnty",
                "user_name",
                "project_numcom",
                "project_label_a",
                "project_label_b",
                "project_label_c",
                "project_template",
                "project_affiliation",
                "project_type",
                "project_location",
                "project_unit_of_analysis",
                "project_objectives",
            ]
            obligatory = ["project_cod", "user_owner"]

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

                            if accessType == 4:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The access assigned for this project does not allow you to make modifications."
                                    ),
                                )
                                return response

                            cdata = getProjectData(activeProjectId, self.request)

                            if "project_location" in dataworking.keys():
                                if (
                                    not "project_unit_of_analysis" in dataworking.keys()
                                    or not "project_objectives" in dataworking.keys()
                                ):
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "To modify project_location, the parameters: 'project_unit_of_analysis', 'project_objectives' are required."
                                        ),
                                    )
                                    return response

                                if not get_location_by_id(
                                    self.request, dataworking["project_location"]
                                ):
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The project_location does not exist."
                                        ),
                                    )
                                    return response

                            if "project_unit_of_analysis" in dataworking.keys():

                                if not "project_objectives" in dataworking.keys():
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "To modify project_unit_of_analysis, the parameter: 'project_objectives' is required."
                                        ),
                                    )
                                    return response

                                if not get_unit_of_analysis_by_id(
                                    self.request,
                                    dataworking["project_unit_of_analysis"],
                                ):
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The project_unit_of_analysis does not exist."
                                        ),
                                    )
                                    return response

                            location_unit_of_analysis = None
                            if "project_objectives" in dataworking.keys():

                                if not "project_location" in dataworking.keys():
                                    dataworking["project_location"] = cdata[
                                        "project_location"
                                    ]

                                if not "project_unit_of_analysis" in dataworking.keys():
                                    dataworking["project_unit_of_analysis"] = cdata[
                                        "project_unit_of_analysis"
                                    ]

                                location_unit_of_analysis = (
                                    get_location_unit_of_analysis_by_combination(
                                        self.request,
                                        dataworking["project_location"],
                                        dataworking["project_unit_of_analysis"],
                                    )
                                )

                                if not location_unit_of_analysis:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This project_location with this project_unit_of_analysis has no defined relationship."
                                        ),
                                    )
                                    return response

                                dataworking[
                                    "project_registration_and_analysis"
                                ] = location_unit_of_analysis[
                                    "registration_and_analysis"
                                ]

                                if not isinstance(
                                    dataworking["project_objectives"], list
                                ):
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "project_objectives should be in list format."
                                        ),
                                    )
                                    return response
                                else:
                                    for obj in dataworking["project_objectives"]:

                                        if not get_location_unit_of_analysis_objectives_by_combination(
                                            self.request,
                                            location_unit_of_analysis["pluoa_id"],
                                            obj,
                                        ):
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "The objective {} does not correspond to the experiment site and the unit of analysis indicated.".format(
                                                        obj
                                                    )
                                                ),
                                            )
                                            return response

                            if "project_template" in dataworking.keys():
                                existsTemplate = getProjectIsTemplate(
                                    self.request, dataworking["project_template"]
                                )
                                if existsTemplate:
                                    if (
                                        "project_registration_and_analysis"
                                        in dataworking.keys()
                                    ):
                                        if str(
                                            dataworking[
                                                "project_registration_and_analysis"
                                            ]
                                        ) == str(
                                            existsTemplate[
                                                "project_registration_and_analysis"
                                            ]
                                        ):
                                            dataworking["usingTemplate"] = dataworking[
                                                "project_template"
                                            ]
                                            dataworking["project_template"] = 0
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "You are trying to use a template that does not correspond to the type of project you are creating."
                                                ),
                                            )
                                            return response
                                    else:
                                        if str(
                                            cdata["project_registration_and_analysis"]
                                        ) == str(
                                            existsTemplate[
                                                "project_registration_and_analysis"
                                            ]
                                        ):
                                            dataworking["usingTemplate"] = dataworking[
                                                "project_template"
                                            ]
                                            dataworking["project_template"] = 0
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "You are trying to use a template that does not correspond to the type of project you are creating."
                                                ),
                                            )
                                            return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "There is no template with this identifier."
                                        ),
                                    )
                                    return response

                            if "project_type" in dataworking.keys():
                                try:
                                    dataworking["project_type"] = int(
                                        dataworking["project_type"]
                                    )

                                    if dataworking["project_type"] not in [1, 2]:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "The parameter project_type must be [1: Real. 2: Training - This project was only used to explain the use of the ClimMob platform and was created as an example]."
                                            ),
                                        )
                                        return response

                                except:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The parameter project_type must be a number."
                                        ),
                                    )
                                    return response

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
                                        activeProjectId,
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

                            if "project_cnty" in dataworking.keys():
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
                            if not "project_label_a" in dataworking.keys():
                                dataworking["project_label_a"] = cdata[
                                    "project_label_a"
                                ]

                            if not "project_label_b" in dataworking.keys():
                                dataworking["project_label_b"] = cdata[
                                    "project_label_b"
                                ]

                            if not "project_label_c" in dataworking.keys():
                                dataworking["project_label_c"] = cdata[
                                    "project_label_c"
                                ]

                            if (
                                dataworking["project_label_a"]
                                != dataworking["project_label_b"]
                                and dataworking["project_label_a"]
                                != dataworking["project_label_c"]
                                and dataworking["project_label_b"]
                                != dataworking["project_label_c"]
                            ):

                                modified, message = modifyProject(
                                    activeProjectId,
                                    dataworking,
                                    self.request,
                                )

                                if modified:

                                    if "project_objectives" in dataworking.keys():
                                        (
                                            deleted,
                                            message,
                                        ) = delete_all_project_location_unit_objective(
                                            activeProjectId, self.request
                                        )

                                        for objective in dataworking[
                                            "project_objectives"
                                        ]:
                                            luoao_id = get_location_unit_of_analysis_objectives_by_combination(
                                                self.request,
                                                location_unit_of_analysis["pluoa_id"],
                                                objective,
                                            )[
                                                "pluoaobj_id"
                                            ]

                                            infoObj = {
                                                "project_id": activeProjectId,
                                                "pluoaobj_id": luoao_id,
                                            }
                                            add_project_location_unit_objective(
                                                infoObj, self.request
                                            )

                                    if (
                                        str(cdata["project_registration_and_analysis"])
                                        == "1"
                                        and str(
                                            dataworking[
                                                "project_registration_and_analysis"
                                            ]
                                        )
                                        == "0"
                                    ):
                                        deleteRegistryByProjectId(
                                            activeProjectId, self.request
                                        )

                                    if "usingTemplate" in dataworking.keys():
                                        deleteRegistryByProjectId(
                                            activeProjectId, self.request
                                        )
                                        deleteProjectAssessments(
                                            activeProjectId, self.request
                                        )

                                        listOfElementToInclude = ["registry"]

                                        assessments = getProjectAssessments(
                                            dataworking["usingTemplate"], self.request
                                        )
                                        for assess in assessments:
                                            listOfElementToInclude.append(
                                                assess["ass_cod"]
                                            )

                                        newProjectId = getTheProjectIdForOwner(
                                            self.user.login,
                                            dataworking["project_cod"],
                                            self.request,
                                        )

                                        functionCreateClone(
                                            self,
                                            dataworking["usingTemplate"],
                                            newProjectId,
                                            listOfElementToInclude,
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
                                    body=self._(
                                        "The names that the items will receive should be different."
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


class DeleteProjectViewApi(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = ["project_cod", "user_owner"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                if not projectExists(
                    self.user.login,
                    dataworking["user_owner"],
                    dataworking["project_cod"],
                    self.request,
                ):
                    response = Response(
                        status=401, body=self._("This project does not exist.")
                    )
                    return response

                activeProjectId = getTheProjectIdForOwner(
                    dataworking["user_owner"], dataworking["project_cod"], self.request
                )
                accessType = getAccessTypeForProject(
                    self.user.login, activeProjectId, self.request
                )

                if accessType in [4]:
                    response = Response(
                        status=401,
                        body=self._(
                            "The access assigned for this project does not allow you to delete the project."
                        ),
                    )
                    return response

                deleted, message = deleteProject(activeProjectId, self.request)
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


class ReadCollaboratorsView(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "GET":

            obligatory = ["project_cod", "user_owner"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                if not projectExists(
                    self.user.login,
                    dataworking["user_owner"],
                    dataworking["project_cod"],
                    self.request,
                ):
                    response = Response(
                        status=401, body=self._("This project does not exist.")
                    )
                    return response

                activeProjectId = getTheProjectIdForOwner(
                    dataworking["user_owner"], dataworking["project_cod"], self.request
                )

                response = Response(
                    status=200,
                    body=json.dumps(
                        get_collaborators_in_project(self.request, activeProjectId),
                        default=myconverter,
                    ),
                )
                return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class AddCollaboratorView(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                "project_cod",
                "user_owner",
                "user_collaborator",
                "access_type",
            ]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                if not projectExists(
                    self.user.login,
                    dataworking["user_owner"],
                    dataworking["project_cod"],
                    self.request,
                ):
                    response = Response(
                        status=401, body=self._("This project does not exist.")
                    )
                    return response

                activeProjectId = getTheProjectIdForOwner(
                    dataworking["user_owner"], dataworking["project_cod"], self.request
                )
                accessType = getAccessTypeForProject(
                    self.user.login, activeProjectId, self.request
                )

                if accessType in [4]:
                    response = Response(
                        status=401,
                        body=self._(
                            "The access assigned for this project does not allow you to add collaborators to the project."
                        ),
                    )
                    return response

                if getUserInfo(self.request, dataworking["user_collaborator"]):

                    if not theUserBelongsToTheProject(
                        dataworking["user_collaborator"],
                        activeProjectId,
                        self.request,
                    ):
                        if dataworking["access_type"] in [2, 3, 4, "2", "3", "4"]:

                            dataworking["access_type"] = int(dataworking["access_type"])
                            dataworking["project_id"] = activeProjectId
                            dataworking["user_name"] = dataworking["user_collaborator"]
                            dataworking["project_dashboard"] = 0
                            added, message = add_project_collaborator(
                                self.request, dataworking
                            )

                            if added:
                                response = Response(
                                    status=200,
                                    body=self._("Collaborator added successfully."),
                                )
                                return response

                            else:
                                response = Response(status=401, body=message)
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The types of access for collaborators are as follows: 2=Admin, 3=Editor, 4=Member."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "The collaborator you want to add already belongs to the project."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._(
                            "The user you want to add as a collaborator does not exist."
                        ),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class DeleteCollaboratorView(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = ["project_cod", "user_owner", "user_collaborator"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                if not projectExists(
                    self.user.login,
                    dataworking["user_owner"],
                    dataworking["project_cod"],
                    self.request,
                ):
                    response = Response(
                        status=401, body=self._("This project does not exist.")
                    )
                    return response

                activeProjectId = getTheProjectIdForOwner(
                    dataworking["user_owner"], dataworking["project_cod"], self.request
                )
                accessType = getAccessTypeForProject(
                    self.user.login, activeProjectId, self.request
                )

                if accessType in [4]:
                    response = Response(
                        status=401,
                        body=self._(
                            "The access assigned for this project does not allow you to delete collaborators from the project."
                        ),
                    )
                    return response

                if getUserInfo(self.request, dataworking["user_collaborator"]):

                    if theUserBelongsToTheProject(
                        dataworking["user_collaborator"],
                        activeProjectId,
                        self.request,
                    ):
                        if (
                            dataworking["user_owner"]
                            != dataworking["user_collaborator"]
                        ):

                            remove, message = remove_collaborator(
                                self.request,
                                activeProjectId,
                                dataworking["user_collaborator"],
                                self,
                            )

                            if remove:
                                response = Response(
                                    status=200,
                                    body=self._(
                                        "The collaborator has been successfully removed."
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
                                    "The user who owns the project cannot be deleted."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You are trying to delete a collaborator that does not belong to this project."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._(
                            "The user you want to delete as a collaborator does not exist."
                        ),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
