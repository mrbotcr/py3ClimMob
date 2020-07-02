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
                u"question_desc",
                u"question_dtype",
                u"question_notes",
                u"question_unit",
                u"question_alwaysinreg",
                u"question_alwaysinasse",
                u"question_requiredvalue",
                "user_name",
            ]
            obligatory = [
                u"question_code",
                u"question_desc",
                u"question_dtype",
                u"question_notes",
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
                                body=self._("Check the id of the question type."),
                            )
                            return response

                        dataworking["question_code"] = re.sub(
                            "[^A-Za-z0-9\-]+", "", dataworking["question_code"]
                        )
                        if not questionExists(
                            self.user.login, dataworking["question_code"], self.request
                        ):
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
                                        if str(dataworking["question_dtype"]) == "9":
                                            response = Response(
                                                status=200,
                                                body=self._(
                                                    "The question was successfully added. Configure the characteristic now."
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
                        [*UserQuestion(self.user.login, self.request), *UserQuestion("bioversity", self.request)]
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
                u"question_desc",
                u"question_dtype",
                u"question_notes",
                u"question_unit",
                u"question_alwaysinreg",
                u"question_alwaysinasse",
                u"question_requiredvalue",
                "user_name",
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
                                            "Check the id of the question type."
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
                                            "This question is already assigned to a form. You can not edit it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You can not edit it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this id."),
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
                                    "This question is already assigned to a form. You can not delete it."
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The question is from the ClimMob library. You can not delete it."
                                ),
                            )
                            return response
                else:
                    response = Response(
                        status=401,
                        body=self._("You do not have a question with this id."),
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
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
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
                                "This is not a question of select one or multiple selection."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._("You do not have a question with this id."),
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

                                    if "value_isother" not in dataworking.keys():
                                        dataworking["value_isother"] = 0

                                    if "value_isna" not in dataworking.keys():
                                        dataworking["value_isna"] = 0

                                    if not optionExists(
                                        dataworking["question_id"],
                                        dataworking["value_code"],
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
                                            response = Response(status=401, body=resp)
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._("Option already exists"),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This is not a question of select one or multiple selection."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question is already assigned to a form. You can not add it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You can not add it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this id."),
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
                u"value_isother",
                u"value_isna",
                "user_name",
            ]
            obligatory = [u"question_id", u"value_code", "user_name"]

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
                                            "This is not a question of select one or multiple selection."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question is already assigned to a form. You can not edit it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You can not edit it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this id."),
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
                                            "The option was successfully delete."
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
                                    "This is not a question of select one or multiple selection."
                                ),
                            )
                            return response
                    else:
                        if data["user_name"] == self.user.login:
                            response = Response(
                                status=401,
                                body=self._(
                                    "This question is already assigned to a form. You can not delete it."
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The question is from the ClimMob library. You can not delete it."
                                ),
                            )
                            return response
                else:
                    response = Response(
                        status=401,
                        body=self._("You do not have a question with this id."),
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
                                                "You successfully updated the characteristic."
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
                                            "This is not a question of type characteristic."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question is already assigned to a form. You can not edit it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You can not edit it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this id."),
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
                                                    "You successfully updated the performance statement."
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
                                                "The performance statement must have the wildcard {{option}}"
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This is not a question of type performance."
                                        ),
                                    )
                                    return response
                            else:
                                if data["user_name"] == self.user.login:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "This question is already assigned to a form. You can not edit it."
                                        ),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The question is from the ClimMob library. You can not edit it."
                                        ),
                                    )
                                    return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a question with this id."),
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
