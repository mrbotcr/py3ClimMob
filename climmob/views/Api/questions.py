from ..classes import apiView
from pyramid.httpexceptions import HTTPFound
from ...processes import (
    addQuestion,
    addOptionToQuestion,
    updateQuestion,
    deleteQuestion,
    UserQuestion,
    QuestionsOptions,
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
)

import json
from heapq import merge
from pyramid.response import Response
import re


class createQuestion_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            possibles = [
                u"question_code",
                u"question_name",
                u"question_desc",
                u"question_dtype",
                u"question_notes",
                u"qstgroups_id",
                u"question_unit",
                u"question_alwaysinreg",
                u"question_alwaysinasse",
                u"question_requiredvalue",
                "user_name",
            ]
            obligatory = [
                u"question_code",
                u"question_name",
                u"question_desc",
                u"question_dtype",
                u"qstgroups_id",
                u"question_requiredvalue",
            ]
            zeroOrTwo = [
                "question_alwaysinreg",
                "question_alwaysinasse",
                "question_requiredvalue",
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
                        if "question_alwaysinreg" not in dataworking.keys():
                            dataworking["question_alwaysinreg"] = 0

                        if "question_alwaysinasse" not in dataworking.keys():
                            dataworking["question_alwaysinasse"] = 0

                        if "question_requiredvalue" not in dataworking.keys():
                            dataworking["question_requiredvalue"] = 0

                        if "question_unit" not in dataworking.keys():
                            dataworking["question_unit"] = ""

                        for data in zeroOrTwo:
                            if str(dataworking[data]) not in ["0", "1"]:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The possible values in the parameters: 'question_alwaysinreg','question_alwaysinasse','question_requiredvalue' is 1 or 0."
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
                                            # response = Response(status=200, body=self._("The question was successfully added. Add new values now."))
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
                                                # response = Response(status=200,body=self._("The question was successfully added. Configure the performance statement now."))
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
                                        # response = Response(status=200, body=self._("The question was successfully added."))
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


class readQuestions_view(apiView):
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


class updateQuestion_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            possibles = [
                u"question_id",
                u"question_name",
                u"question_desc",
                u"question_dtype",
                u"question_notes",
                u"question_unit",
                u"question_alwaysinreg",
                u"question_alwaysinasse",
                u"question_requiredvalue",
                u"qstgroups_id",
                u"user_name",
            ]
            obligatory = [u"question_id"]
            zeroOrTwo = [
                "question_alwaysinreg",
                "question_alwaysinasse",
                "question_requiredvalue",
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

                                if "question_unit" not in dataworking.keys():
                                    dataworking["question_unit"] = data["question_unit"]

                                for data2 in zeroOrTwo:
                                    if str(dataworking[data2]) not in ["0", "1"]:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "The possible values in the parameters: 'question_alwaysinreg','question_alwaysinasse','question_requiredvalue' is 1 or 0."
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


class deleteQuestion_viewApi(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"question_id"]
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


class readQuestionValues_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"question_id", "user_name"]

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


class addQuestionValue_viewApi(apiView):
    def processView(self):

        if self.request.method == "POST":
            possibles = [
                u"question_id",
                u"value_code",
                u"value_desc",
                u"value_isother",
                u"value_isna",
                "user_name",
            ]
            obligatory = [u"question_id", u"value_code", u"value_desc", "user_name"]

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


class updateQuestionValue_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            possibles = [
                u"question_id",
                u"value_code",
                u"value_desc",
                "user_name",
            ]
            obligatory = [u"question_id", u"value_code", u"value_desc", "user_name"]

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


class deleteQuestionValue_viewApi(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"question_id", u"value_code", "user_name"]

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


class updateQuestionCharacteristics_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            possibles = [
                u"question_id",
                u"question_twoitems",
                u"question_posstm",
                u"question_negstm",
                u"question_moreitems",
                "user_name",
            ]
            obligatory = [
                u"question_id",
                u"question_posstm",
                u"question_negstm",
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


class updateQuestionPerformance_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            possibles = [u"question_id", u"question_perfstmt", "user_name"]
            obligatory = [u"question_id", u"question_perfstmt", "user_name"]

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
