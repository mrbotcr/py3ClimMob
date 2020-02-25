from ..classes import apiView

from ...processes import (
    projectExists,
    getRegistryQuestions,
    availableRegistryQuestions,
    QuestionsOptions,
    addRegistryGroup,
    modifyRegistryGroup,
    exitsRegistryGroup,
    canDeleteTheGroup,
    deleteRegistryGroup,
    projectRegStatus,
    getQuestionData,
    canUseTheQuestion,
    addRegistryQuestionToGroup,
    deleteRegistryQuestionFromGroup,
    exitsQuestionInGroup,
    haveTheBasicStructure,
    haveTheBasic,
    getRegistryGroup,
    getRegistryQuestionsApi,
    saveRegistryOrder,
)

from pyramid.response import Response
import json
import datetime


class readProjectRegistry_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    data = getRegistryQuestions(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    # The following is to help jinja2 to render the groups and questions
                    # This because the scope constraint makes it difficult to control
                    sectionID = -99
                    grpIndex = -1
                    for a in range(0, len(data)):
                        if data[a]["section_id"] != sectionID:
                            grpIndex = a
                            data[a]["createGRP"] = True
                            data[a]["grpCannotDelete"] = False
                            sectionID = data[a]["section_id"]
                            if a == 0:
                                data[a]["closeQst"] = False
                                data[a]["closeGrp"] = False
                            else:
                                if data[a - 1]["hasQuestions"]:
                                    data[a]["closeQst"] = True
                                    data[a]["closeGrp"] = True
                                else:
                                    data[a]["closeGrp"] = False
                                    data[a]["closeQst"] = False
                        else:
                            data[a]["createGRP"] = False
                            data[a]["closeQst"] = False
                            data[a]["closeGrp"] = False

                        if data[a]["question_id"] != None:
                            data[a]["hasQuestions"] = True
                            if data[a]["question_reqinreg"] == 1:
                                data[grpIndex]["grpCannotDelete"] = True
                        else:
                            data[a]["hasQuestions"] = False
                    finalCloseQst = data[len(data) - 1]["hasQuestions"]

                    response = Response(
                        status=200,
                        body=json.dumps({"data": data, "finalCloseQst": finalCloseQst}),
                    )
                    return response
                else:
                    response = Response(
                        status=401, body=self._("There is no a project with that code.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class readPossibleQuestionsForRegistryGroup_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    response = Response(
                        status=200,
                        body=json.dumps(
                            {
                                "Questions": availableRegistryQuestions(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    self.request,
                                ),
                                "QuestionsOptions": QuestionsOptions(
                                    self.user.login, self.request
                                ),
                            }
                        ),
                    )
                    return response
                else:
                    response = Response(
                        status=401, body=self._("There is no a project with that code.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class addRegistryGroup_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"section_name", u"section_content"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                dataworking["section_color"] = None

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

                            haveTheBasicStructure(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            )

                            addgroup, message = addRegistryGroup(
                                dataworking, self, "API"
                            )
                            if not addgroup:
                                response = Response(status=401, body=message)
                                return response
                            else:
                                response = Response(
                                    status=200, body=json.dumps(message)
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You can not create groups. You started the registry."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not a project with that code."),
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


class updateRegistryGroup_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [
                u"project_cod",
                u"group_cod",
                u"section_name",
                u"section_content",
            ]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                dataworking["section_color"] = None

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
                            exitsGroup = exitsRegistryGroup(dataworking, self)
                            if exitsGroup:
                                mdf, message = modifyRegistryGroup(dataworking, self)
                                if not mdf:
                                    response = Response(status=401, body=message)
                                    return response
                                else:
                                    response = Response(
                                        status=200,
                                        body=self._("Group updated successfully."),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("There is not a group with that code."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You can not update groups. You started the registry."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not a project with that code."),
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


class deleteRegistryGroup_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"group_cod"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                dataworking["section_color"] = None

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
                            exitsGroup = exitsRegistryGroup(dataworking, self)
                            if exitsGroup:
                                candelete = canDeleteTheGroup(dataworking, self.request)
                                if candelete:
                                    deleted, message = deleteRegistryGroup(
                                        self.user.login,
                                        dataworking["project_cod"],
                                        dataworking["group_cod"],
                                        self.request,
                                    )
                                    if not deleted:
                                        response = Response(status=401, body=message)
                                        return response
                                    else:
                                        response = Response(
                                            status=200,
                                            body=self._("Group deleted successfully."),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You can not delete this group because you have questions required for the registry."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("There is not a group with that code."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You can not delete groups. You started the registry."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not a project with that code."),
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


class addQuestionToGroupRegistry_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"group_cod", u"question_id"]
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
                            exitsGroup = exitsRegistryGroup(dataworking, self)
                            if exitsGroup:
                                data, editable = getQuestionData(
                                    self.user.login,
                                    dataworking["question_id"],
                                    self.request,
                                )
                                if data:
                                    if canUseTheQuestion(
                                        self.user.login,
                                        dataworking["project_cod"],
                                        dataworking["question_id"],
                                        self.request,
                                    ):
                                        dataworking["section_id"] = dataworking[
                                            "group_cod"
                                        ]
                                        addq, message = addRegistryQuestionToGroup(
                                            dataworking, self.request
                                        )
                                        if not addq:
                                            response = Response(
                                                status=401, body=message
                                            )
                                            return response
                                        else:
                                            response = Response(
                                                status=200,
                                                body=self._(
                                                    "The question was added to the record"
                                                ),
                                            )
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "The question is already assigned to registry or can not be used in this section."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You do not have a question with this id."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("There is not a group with that code."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You can not add questions. You started the registry."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not a project with that code."),
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


class deleteQuestionFromGroupRegistry_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"group_cod", u"question_id"]
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
                            exitsGroup = exitsRegistryGroup(dataworking, self)
                            if exitsGroup:
                                data, editable = getQuestionData(
                                    self.user.login,
                                    dataworking["question_id"],
                                    self.request,
                                )
                                if data:
                                    if data["question_reqinreg"] == 1:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "You can not delete this question because is required in the registry."
                                            ),
                                        )
                                        return response
                                    else:

                                        if exitsQuestionInGroup(
                                            dataworking, self.request
                                        ):
                                            (
                                                deleted,
                                                message,
                                            ) = deleteRegistryQuestionFromGroup(
                                                dataworking, self.request
                                            )
                                            if not deleted:
                                                response = Response(
                                                    status=401, body=message
                                                )
                                                return response
                                            else:
                                                response = Response(
                                                    status=200,
                                                    body=self._(
                                                        "Question deleted successfully."
                                                    ),
                                                )
                                                return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "You do not have a question with this id in this group."
                                                ),
                                            )
                                            return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You do not have a question with this id."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("There is not a group with that code."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You can not delete questions. You started the registry."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not a project with that code."),
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


class orderRegistryQuestions_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"order"]
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
                            if haveTheBasic(
                                self.user.login,
                                dataworking["project_cod"],
                                self.request,
                            ):
                                try:
                                    originalData = json.loads(dataworking["order"])

                                    groups = []
                                    questions = []
                                    questionWithoutGroup = False

                                    for item in originalData:
                                        if item["type"] == "question":
                                            questionWithoutGroup = True
                                        else:
                                            groups.append(
                                                int(item["id"].replace("GRP", ""))
                                            )
                                            if "children" in item.keys():
                                                for children in item["children"]:
                                                    questions.append(
                                                        int(
                                                            children["id"].replace(
                                                                "QST", ""
                                                            )
                                                        )
                                                    )

                                    if not questionWithoutGroup:
                                        groupsInProject = getRegistryGroup(
                                            dataworking, self
                                        )
                                        if sorted(groupsInProject) == sorted(groups):
                                            questionsInProject = getRegistryQuestionsApi(
                                                dataworking, self
                                            )
                                            if sorted(questionsInProject) == sorted(
                                                questions
                                            ):
                                                modified, error = saveRegistryOrder(
                                                    self.user.login,
                                                    dataworking["project_cod"],
                                                    originalData,
                                                    self.request,
                                                )
                                                response = Response(
                                                    status=200,
                                                    body=self._(
                                                        "The order of the groups and questions was changed."
                                                    ),
                                                )
                                                return response
                                            else:
                                                response = Response(
                                                    status=401,
                                                    body=self._(
                                                        "You are ordering questions that are not part of the form."
                                                    ),
                                                )
                                                return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "You are ordering groups that are not part of the form."
                                                ),
                                            )
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "Questions cannot be outside a group"
                                            ),
                                        )
                                        return response
                                except:
                                    response = Response(
                                        status=401,
                                        body=self._("Error in the JSON order."),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "No group and questions to order. You need to read the project registry."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You can not order the groups and questions. You started the registry."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not a project with that code."),
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
