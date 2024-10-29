import json
import re

from pyramid.response import Response

from climmob.processes import (
    addQuestion,
    addOptionToQuestion,
    updateQuestion,
    deleteQuestion,
    UserQuestion,
    getQuestionData,
    getQuestionOptions,
    deleteOption,
    optionExists,
    getOptionData,
    updateOption,
    questionExists,
    categoryExistsById,
    optionExistsWithName,
    opcionNAinQuestion,
    opcionOtherInQuestion,
    languageExistInI18nUser,
    getAllTranslationsOfQuestion,
)
from climmob.views.classes import apiView
from climmob.views.questionTranslations import (
    actionInTheTranslationOfQuestion,
    actionInTheTranslationOfQuestionOptions,
)


class CreateQuestionView(apiView):
    def processView(self):

        if self.request.method == "POST":

            possibles = [
                "question_code",
                "question_name",
                "question_desc",
                "question_dtype",
                "question_notes",
                "qstgroups_id",
                "question_unit",
                "question_alwaysinreg",
                "question_alwaysinasse",
                "question_requiredvalue",
                "question_tied",
                "question_notobserved",
                "question_quantitative",
                "question_lang",
                "user_name",
            ]
            obligatory = [
                "question_code",
                "question_name",
                "question_desc",
                "question_dtype",
                "qstgroups_id",
                "question_requiredvalue",
                "question_lang",
            ]
            zeroOrTwo = [
                "question_alwaysinreg",
                "question_alwaysinasse",
                "question_requiredvalue",
                "question_tied",
                "question_notobserved",
                "question_quantitative",
            ]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

            permitedKeys = True
            for key in dataworking.keys():
                if key not in possibles:
                    print(key)
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

                        if not languageExistInI18nUser(
                            dataworking["question_lang"], self.user.login, self.request
                        ):
                            response = Response(
                                status=401,
                                body=self._(
                                    "The language does not belong to your list of languages to be used.."
                                ),
                            )
                            return response

                        if "question_alwaysinreg" not in dataworking.keys():
                            dataworking["question_alwaysinreg"] = 0

                        if "question_alwaysinasse" not in dataworking.keys():
                            dataworking["question_alwaysinasse"] = 0

                        if "question_requiredvalue" not in dataworking.keys():
                            dataworking["question_requiredvalue"] = 0

                        if "question_unit" not in dataworking.keys():
                            dataworking["question_unit"] = ""

                        if "question_tied" not in dataworking.keys():
                            dataworking["question_tied"] = 0

                        if "question_notobserved" not in dataworking.keys():
                            dataworking["question_notobserved"] = 0

                        if "question_quantitative" not in dataworking.keys():
                            dataworking["question_quantitative"] = 0

                        for data in zeroOrTwo:
                            if str(dataworking[data]) not in ["0", "1"]:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The possible values in the parameters: 'question_alwaysinreg','question_alwaysinasse','question_requiredvalue', 'question_quantitative' is 1 or 0."
                                    ),
                                )
                                return response

                        if str(dataworking["question_dtype"]) not in [
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                            "6",
                            "9",
                            "10",
                            "11",
                            "12",
                            "13",
                            "14",
                            "15",
                            "16",
                            "17",
                            "18",
                            "19",
                        ]:
                            response = Response(
                                status=401,
                                body=self._("Check the ID of the question type."),
                            )
                            return response

                        dataworking["question_code"] = re.sub(
                            "[^A-Za-z0-9\-]+", "", dataworking["question_code"]
                        )
                        if not questionExists(
                            self.user.login, dataworking["question_code"], self.request
                        ):
                            categoryExists = categoryExistsById(
                                self.user.login,
                                dataworking["qstgroups_id"],
                                self.request,
                            )
                            if categoryExists:
                                dataworking["qstgroups_user"] = categoryExists[
                                    "user_name"
                                ]

                                if (
                                    str(dataworking["question_dtype"]) == "9"
                                    or str(dataworking["question_dtype"]) == "10"
                                ):
                                    dataworking["question_quantitative"] = 0

                                if str(dataworking["question_dtype"]) != "9":
                                    dataworking["question_tied"] = 0
                                    dataworking["question_notobserved"] = 0

                                add, idorerror = addQuestion(dataworking, self.request)
                                if not add:
                                    response = Response(status=401, body=idorerror)
                                    return response
                                else:

                                    if (
                                        str(dataworking["question_dtype"]) == "5"
                                        or str(dataworking["question_dtype"]) == "6"
                                        or str(dataworking["question_dtype"]) == "9"
                                        or str(dataworking["question_dtype"]) == "10"
                                    ):
                                        if (
                                            str(dataworking["question_dtype"]) == "5"
                                            or str(dataworking["question_dtype"]) == "6"
                                        ):
                                            response = Response(
                                                status=200,
                                                body=json.dumps(
                                                    getQuestionData(
                                                        dataworking["user_name"],
                                                        idorerror,
                                                        self.request,
                                                    )
                                                ),
                                            )
                                            return response
                                        else:
                                            if (
                                                str(dataworking["question_dtype"])
                                                == "9"
                                            ):
                                                response = Response(
                                                    status=200,
                                                    body=self._(
                                                        "The question was successfully added. Configure the ranking of options now."
                                                    ),
                                                )
                                                return response
                                            else:
                                                response = Response(
                                                    status=200,
                                                    body=json.dumps(
                                                        getQuestionData(
                                                            dataworking["user_name"],
                                                            idorerror,
                                                            self.request,
                                                        )
                                                    ),
                                                )
                                                return response
                                    else:
                                        response = Response(
                                            status=200,
                                            body=json.dumps(
                                                getQuestionData(
                                                    dataworking["user_name"],
                                                    idorerror,
                                                    self.request,
                                                )
                                            ),
                                        )
                                        return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no category with this identifier."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is another question with the same code."
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
                        body=self._("Error in the parameters that you want to add."),
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


class ReadQuestionsView(apiView):
    def processView(self):

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(
                    list(
                        [
                            *UserQuestion(self.user.login, self.request),
                            *UserQuestion("bioversity", self.request),
                        ]
                    )
                ),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class UpdateQuestionView(apiView):
    def processView(self):

        if self.request.method == "POST":

            possibles = [
                "question_id",
                "question_name",
                "question_desc",
                "question_dtype",
                "question_notes",
                "question_unit",
                "question_alwaysinreg",
                "question_alwaysinasse",
                "question_requiredvalue",
                "question_tied",
                "question_notobserved",
                "question_quantitative",
                "qstgroups_id",
                "question_lang",
                "user_name",
            ]
            obligatory = ["question_id"]
            zeroOrTwo = [
                "question_alwaysinreg",
                "question_alwaysinasse",
                "question_requiredvalue",
                "question_tied",
                "question_notobserved",
                "question_quantitative",
            ]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

            permitedKeys = True
            for key in dataworking.keys():
                if key not in possibles:
                    print(key)
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
                        data, editable = getQuestionData(
                            self.user.login, dataworking["question_id"], self.request
                        )
                        if data:
                            if editable:

                                if "question_lang" in dataworking.keys():

                                    if not languageExistInI18nUser(
                                        dataworking["question_lang"],
                                        self.user.login,
                                        self.request,
                                    ):
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "The language does not belong to your list of languages to be used.."
                                            ),
                                        )
                                        return response

                                if "question_alwaysinreg" not in dataworking.keys():
                                    dataworking["question_alwaysinreg"] = data[
                                        "question_alwaysinreg"
                                    ]

                                if "question_alwaysinasse" not in dataworking.keys():
                                    dataworking["question_alwaysinasse"] = data[
                                        "question_alwaysinasse"
                                    ]

                                if "question_requiredvalue" not in dataworking.keys():
                                    dataworking["question_requiredvalue"] = data[
                                        "question_requiredvalue"
                                    ]

                                if "question_tied" not in dataworking.keys():
                                    dataworking["question_tied"] = data["question_tied"]

                                if "question_notobserved" not in dataworking.keys():
                                    dataworking["question_notobserved"] = data[
                                        "question_notobserved"
                                    ]

                                if "question_quantitative" not in dataworking.keys():
                                    dataworking["question_quantitative"] = data[
                                        "question_quantitative"
                                    ]

                                if "question_unit" not in dataworking.keys():
                                    dataworking["question_unit"] = data["question_unit"]

                                for data2 in zeroOrTwo:
                                    if str(dataworking[data2]) not in ["0", "1"]:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "The possible values in the parameters: 'question_alwaysinreg','question_alwaysinasse','question_requiredvalue', 'question_quantitative' is 1 or 0."
                                            ),
                                        )
                                        return response

                                if "qstgroups_id" in dataworking.keys():
                                    categoryExists = categoryExistsById(
                                        self.user.login,
                                        dataworking["qstgroups_id"],
                                        self.request,
                                    )
                                    if categoryExists:
                                        dataworking["qstgroups_user"] = categoryExists[
                                            "user_name"
                                        ]
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "There is a problem with the question category you want to assign."
                                            ),
                                        )
                                        return response

                                if "question_dtype" in dataworking.keys():
                                    if str(dataworking["question_dtype"]) not in [
                                        "1",
                                        "2",
                                        "3",
                                        "4",
                                        "5",
                                        "6",
                                        "9",
                                        "10",
                                        "11",
                                        "12",
                                        "13",
                                        "14",
                                        "15",
                                        "16",
                                        "17",
                                        "18",
                                        "19",
                                    ]:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "Check the ID of the question type."
                                            ),
                                        )
                                        return response
                                if "question_dtype" in dataworking.keys():
                                    if (
                                        str(dataworking["question_dtype"]) == "9"
                                        or str(dataworking["question_dtype"]) == "10"
                                    ):
                                        dataworking["question_quantitative"] = 0

                                    if str(dataworking["question_dtype"]) != "9":
                                        dataworking["question_tied"] = 0
                                        dataworking["question_notobserved"] = 0

                                else:
                                    if (
                                        str(data["question_dtype"]) == "9"
                                        or str(data["question_dtype"]) == "10"
                                    ):
                                        dataworking["question_quantitative"] = 0

                                    if str(data["question_dtype"]) != "9":
                                        dataworking["question_tied"] = 0
                                        dataworking["question_notobserved"] = 0

                                updated, idorerror = updateQuestion(
                                    dataworking, self.request
                                )
                                if not updated:
                                    response = Response(status=401, body=idorerror)
                                    return response
                                else:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "The question was successfully modified."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question has already been assigned to a form. You cannot edit it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You cannot edit it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this ID."),
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
                        body=self._("Error in the parameters that you want to add."),
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


class DeleteQuestionViewApi(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = ["question_id"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                data, editable = getQuestionData(
                    self.user.login, dataworking["question_id"], self.request
                )
                if data:
                    if editable:
                        dlt, message = deleteQuestion(dataworking, self.request)

                        if not dlt:
                            response = Response(status=401, body=message)
                            return response
                        else:
                            response = Response(
                                status=200,
                                body=self._("The question was deleted successfully."),
                            )
                            return response
                    else:
                        if data["user_name"] == self.user.login:
                            response = Response(
                                status=401,
                                body=self._(
                                    "This question has already been assigned to a form. You cannot delete it."
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The question is from the ClimMob library. You cannot delete it."
                                ),
                            )
                            return response
                else:
                    response = Response(
                        status=401,
                        body=self._("You do not have a question with this ID."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class ReadQuestionValuesView(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = ["question_id", "user_name"]

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
            dataworking["user_name"] = self.user.login

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking, editable = getQuestionData(
                    self.user.login, dataworking["question_id"], self.request
                )
                if dataworking:
                    if (
                        dataworking["question_dtype"] == 5
                        or dataworking["question_dtype"] == 6
                    ):
                        qoptions = getQuestionOptions(
                            dataworking["question_id"], self.request
                        )

                        response = Response(status=200, body=json.dumps(qoptions))
                        return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "This is not a question of type Select one or Multiple selection."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._("You do not have a question with this ID."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class AddQuestionValueViewApi(apiView):
    def processView(self):

        if self.request.method == "POST":
            possibles = [
                "question_id",
                "value_code",
                "value_desc",
                "value_isother",
                "value_isna",
                "user_name",
            ]
            obligatory = ["question_id", "value_code", "value_desc", "user_name"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

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

                        data, editable = getQuestionData(
                            self.user.login, dataworking["question_id"], self.request
                        )
                        if data:
                            if editable:
                                if (
                                    data["question_dtype"] == 5
                                    or data["question_dtype"] == 6
                                ):
                                    if (
                                        "value_isother" in dataworking.keys()
                                        and "value_isna" in dataworking.keys()
                                    ):
                                        if (
                                            int(dataworking["value_isother"]) == 1
                                            and int(dataworking["value_isna"]) == 1
                                        ):
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "An option cannot be 'Other' and 'Not applicable'."
                                                ),
                                            )
                                            return response

                                    if opcionOtherInQuestion(
                                        dataworking["question_id"], self.request
                                    ):
                                        if "value_isother" in dataworking.keys():
                                            if int(dataworking["value_isother"]) == 1:
                                                response = Response(
                                                    status=401,
                                                    body=self._(
                                                        "There is already an 'Other' option."
                                                    ),
                                                )
                                                return response

                                    if opcionNAinQuestion(
                                        dataworking["question_id"], self.request
                                    ):
                                        if "value_isna" in dataworking.keys():
                                            if int(dataworking["value_isna"]) == 1:
                                                response = Response(
                                                    status=401,
                                                    body=self._(
                                                        "There is already an 'Not applicable' option."
                                                    ),
                                                )
                                                return response

                                    if "value_isother" not in dataworking.keys():
                                        dataworking["value_isother"] = 0

                                    if "value_isna" not in dataworking.keys():
                                        dataworking["value_isna"] = 0

                                    if not optionExists(
                                        dataworking["question_id"],
                                        dataworking["value_code"],
                                        self.request,
                                    ):
                                        if not optionExistsWithName(
                                            dataworking["question_id"],
                                            dataworking["value_desc"],
                                            self.request,
                                        ):
                                            addded, resp = addOptionToQuestion(
                                                dataworking, self.request
                                            )
                                            if addded:
                                                response = Response(
                                                    status=200,
                                                    body=self._(
                                                        "The option was successfully added."
                                                    ),
                                                )
                                                return response
                                            else:
                                                response = Response(
                                                    status=401, body=resp
                                                )
                                                return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "There is already an option with that description."
                                                ),
                                            )
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "There is already an option with that code."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This is not a question of type Select one or Multiple selection."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question has already been assigned to a form. You cannot add it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You cannot add it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this ID."),
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
                        body=self._("Error in the parameters that you want to add."),
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


class UpdateQuestionValueView(apiView):
    def processView(self):

        if self.request.method == "POST":
            possibles = [
                "question_id",
                "value_code",
                "value_desc",
                "user_name",
            ]
            obligatory = ["question_id", "value_code", "value_desc", "user_name"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

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

                        data, editable = getQuestionData(
                            self.user.login, dataworking["question_id"], self.request
                        )
                        if data:
                            if editable:
                                if (
                                    data["question_dtype"] == 5
                                    or data["question_dtype"] == 6
                                ):
                                    if optionExists(
                                        dataworking["question_id"],
                                        dataworking["value_code"],
                                        self.request,
                                    ):
                                        formdata = getOptionData(
                                            dataworking["question_id"],
                                            dataworking["value_code"],
                                            self.request,
                                        )
                                        if "value_isother" not in dataworking.keys():
                                            dataworking["value_isother"] = formdata[
                                                "value_isother"
                                            ]

                                        if "value_isna" not in dataworking.keys():
                                            dataworking["value_isna"] = formdata[
                                                "value_isna"
                                            ]

                                        updated, resp = updateOption(
                                            dataworking, self.request
                                        )
                                        if updated:
                                            response = Response(
                                                status=200,
                                                body=self._(
                                                    "The option was successfully update."
                                                ),
                                            )
                                            return response
                                        else:
                                            response = Response(status=401, body=resp)
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "Does not have an option with this value_code"
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This is not a question of type Select one or Multiple selection."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question has already been assigned to a form. You cannot edit it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You cannot edit it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this ID."),
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
                        body=self._("Error in the parameters that you want to add."),
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


class DeleteQuestionValueViewApi(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = ["question_id", "value_code", "user_name"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

            if sorted(obligatory) == sorted(dataworking.keys()):

                data, editable = getQuestionData(
                    self.user.login, dataworking["question_id"], self.request
                )
                if data:
                    if editable:
                        if data["question_dtype"] == 5 or data["question_dtype"] == 6:
                            exits = optionExists(
                                dataworking["question_id"],
                                dataworking["value_code"],
                                self.request,
                            )
                            if exits:
                                deleted, msg = deleteOption(
                                    dataworking["question_id"],
                                    dataworking["value_code"],
                                    self.request,
                                )
                                if deleted:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "The option was successfully deleted."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(status=401, body=msg)
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "Does not have an option with this value_code"
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "This is not a question of type Select one or Multiple selection."
                                ),
                            )
                            return response
                    else:
                        if data["user_name"] == self.user.login:
                            response = Response(
                                status=401,
                                body=self._(
                                    "This question has already been assigned to a form. You cannot delete it."
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The question is from the ClimMob library. You cannot delete it."
                                ),
                            )
                            return response
                else:
                    response = Response(
                        status=401,
                        body=self._("You do not have a question with this ID."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


"""class readQuestionPerformance_view(apiView):
    def processView(self):

        print ""

class readQuestionCharacteristic_view(apiView):
    def processView(self):

        print ""
"""


class UpdateQuestionCharacteristicsView(apiView):
    def processView(self):

        if self.request.method == "POST":
            possibles = [
                "question_id",
                "question_twoitems",
                "question_posstm",
                "question_negstm",
                "question_moreitems",
                "user_name",
            ]
            obligatory = [
                "question_id",
                "question_posstm",
                "question_negstm",
                "user_name",
            ]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

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

                        data, editable = getQuestionData(
                            self.user.login, dataworking["question_id"], self.request
                        )
                        if data:
                            if editable:
                                if data["question_dtype"] == 9:
                                    modified, msg = updateQuestion(
                                        dataworking, self.request
                                    )
                                    if modified:
                                        response = Response(
                                            status=200,
                                            body=self._(
                                                "You successfully updated the ranking of options."
                                            ),
                                        )
                                        return response
                                    else:
                                        response = Response(status=401, body=msg)
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This is not a question of type ranking of options."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question has already been assigned to a form. You cannot edit it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You cannot edit it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this ID."),
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
                        body=self._("Error in the parameters that you want to add."),
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


class UpdateQuestionPerformanceView(apiView):
    def processView(self):

        if self.request.method == "POST":
            possibles = ["question_id", "question_perfstmt", "user_name"]
            obligatory = ["question_id", "question_perfstmt", "user_name"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

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

                        data, editable = getQuestionData(
                            self.user.login, dataworking["question_id"], self.request
                        )
                        if data:
                            if editable:
                                if data["question_dtype"] == 10:
                                    perstmt = dataworking["question_perfstmt"].replace(
                                        " ", ""
                                    )
                                    if perstmt.find("{{option}}") >= 0:
                                        modified, msg = updateQuestion(
                                            dataworking, self.request
                                        )
                                        if modified:
                                            response = Response(
                                                status=200,
                                                body=self._(
                                                    "You successfully updated the comparison with check."
                                                ),
                                            )
                                            return response
                                        else:
                                            response = Response(status=401, body=msg)
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "The comparison with check must have the wildcard {{option}}"
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This is not a question of type comparison with check."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question has already been assigned to a form. You cannot edit it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You cannot edit it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this ID."),
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
                        body=self._("Error in the parameters that you want to add."),
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


class MultiLanguageQuestionView(apiView):
    def processView(self):

        if self.request.method == "POST":

            possibles = ["question_id", "question_name", "lang_code", "user_name"]
            obligatory = ["question_id", "question_name", "lang_code", "user_name"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

            if not "question_id" in dataworking.keys():
                response = Response(
                    status=401,
                    body=self._("The question_id parameter is required."),
                )
                return response

            data, editable = getQuestionData(
                self.user.login, dataworking["question_id"], self.request
            )

            if data:

                if not data["question_lang"]:
                    response = Response(
                        status=401,
                        body=self._(
                            "It is not possible to translate a question without first assigning a language to it."
                        ),
                    )
                    return response

                if data["user_name"] != self.user.login:
                    response = Response(
                        status=401,
                        body=self._(
                            "The question is from the ClimMob library. You cannot edit it."
                        ),
                    )
                    return response

                if data["question_lang"] == dataworking["lang_code"]:
                    response = Response(
                        status=401,
                        body=self._(
                            "The question cannot be translated into the same language that has been defined as the main language."
                        ),
                    )
                    return response

                if "question_perfstmt" in dataworking.keys():
                    if dataworking["question_perfstmt"].find("{{option}}") == -1:
                        response = Response(
                            status=401,
                            body=self._(
                                "The parameter question_perfstmt must contain the value: {{option}} in the text."
                            ),
                        )
                        return response

                if data["question_dtype"] not in [9, 10]:
                    possibles.append("question_desc")
                    obligatory.append("question_desc")

                if data["question_dtype"] in [2, 3, 8]:
                    possibles.append("question_unit")
                    obligatory.append("question_unit")

                if data["question_dtype"] in [9]:
                    possibles.append("question_posstm")
                    obligatory.append("question_posstm")
                    possibles.append("question_negstm")
                    obligatory.append("question_negstm")

                if data["question_dtype"] in [10]:
                    possibles.append("question_perfstmt")
                    obligatory.append("question_perfstmt")

                if data["question_dtype"] in [5, 6]:

                    options = getQuestionOptions(
                        dataworking["question_id"], self.request
                    )

                    for op in options:
                        possibles.append("option_{}".format(op["value_code"]))
                        obligatory.append("option_{}".format(op["value_code"]))

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

                            if not languageExistInI18nUser(
                                dataworking["lang_code"],
                                self.user.login,
                                self.request,
                            ):
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The language does not belong to your list of languages to be used."
                                    ),
                                )
                                return response

                            result = actionInTheTranslationOfQuestion(self, dataworking)

                            questionOptions = []
                            for key in dataworking.keys():
                                keyS = key.split("_")
                                if keyS[0] == "option":
                                    info = {}
                                    info["question_id"] = dataworking["question_id"]
                                    info["lang_code"] = dataworking["lang_code"]
                                    try:
                                        info["value_code"] = keyS[1]
                                        info["value_desc"] = dataworking[key]
                                        questionOptions.append(info)
                                    except:
                                        va = ""
                            if questionOptions:
                                actionInTheTranslationOfQuestionOptions(
                                    self, questionOptions
                                )

                            if result["result"] == "success":
                                response = Response(status=200, body=result["success"])
                                return response
                            else:
                                response = Response(status=401, body=result["error"])
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
                                "Error in the parameters that you want to add."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._(
                            "It is not complying with the obligatory keys: {}".format(
                                ", ".join(obligatory)
                            )
                        ),
                    )
                    return response
            else:
                response = Response(
                    status=401,
                    body=self._("You do not have a question with this ID."),
                )
                return response

        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class ReadMultiLanguagesFromQuestionView(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = ["question_id", "user_name"]

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
            dataworking["user_name"] = self.user.login

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking, editable = getQuestionData(
                    dataworking["user_name"], dataworking["question_id"], self.request
                )
                if dataworking:

                    if not dataworking["question_lang"]:
                        response = Response(
                            status=401,
                            body=self._(
                                "This question does not have a main language configured, so it does not have translations."
                            ),
                        )
                        return response

                    translations = getAllTranslationsOfQuestion(
                        self.request,
                        dataworking["user_name"],
                        dataworking["question_id"],
                    )

                    dataworking["translations"] = translations

                    response = Response(status=200, body=json.dumps(dataworking))
                    return response

                else:
                    response = Response(
                        status=401,
                        body=self._("You do not have a question with this ID."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response
