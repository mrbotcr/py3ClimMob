import json

from pyramid.response import Response

from climmob.processes import (
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
    getProjectData,
    getTheProjectIdForOwner,
    getAccessTypeForProject,
    theUserBelongsToTheProject,
)
from climmob.views.classes import apiView


class readProjectRegistry_view(apiView):
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

                    projectDetails = getProjectData(activeProjectId, self.request)
                    projectLabels = [
                        projectDetails["project_label_a"],
                        projectDetails["project_label_b"],
                        projectDetails["project_label_c"],
                    ]
                    data = getRegistryQuestions(
                        dataworking["user_owner"],
                        activeProjectId,
                        self.request,
                        projectLabels,
                        onlyShowTheBasicQuestions=True,
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
                                "The access assigned for this project does not allow you to get this information."
                            ),
                        )
                        return response

                    pro = getProjectData(activeProjectId, self.request)
                    response = Response(
                        status=200,
                        body=json.dumps(
                            {
                                "Questions": availableRegistryQuestions(
                                    activeProjectId,
                                    self.request,
                                    pro["project_registration_and_analysis"],
                                ),
                                "QuestionsOptions": QuestionsOptions(
                                    self.user.login,
                                    dataworking["user_owner"],
                                    self.request,
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
            obligatory = [
                "project_cod",
                "user_owner",
                "section_name",
                "section_content",
            ]
            dataworking = json.loads(self.body)

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
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to add groups."
                                ),
                            )
                            return response

                        if projectRegStatus(activeProjectId, self.request):

                            haveTheBasicStructure(
                                dataworking["user_owner"],
                                activeProjectId,
                                self.request,
                            )

                            dataworking["project_id"] = activeProjectId
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
                                    "You cannot create groups. You started registration."
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


class updateRegistryGroup_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "group_cod",
                "section_name",
                "section_content",
            ]
            dataworking = json.loads(self.body)

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
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to update groups."
                                ),
                            )
                            return response

                        if projectRegStatus(activeProjectId, self.request):
                            dataworking["project_id"] = activeProjectId
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
                                    "You can not update groups. You started registration."
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


class deleteRegistryGroup_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "group_cod"]
            dataworking = json.loads(self.body)

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
                        accessType = getAccessTypeForProject(
                            self.user.login, activeProjectId, self.request
                        )

                        if accessType in [4]:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The access assigned for this project does not allow you to delete groups."
                                ),
                            )
                            return response

                        if projectRegStatus(activeProjectId, self.request):
                            dataworking["project_id"] = activeProjectId
                            exitsGroup = exitsRegistryGroup(dataworking, self)
                            if exitsGroup:
                                candelete = canDeleteTheGroup(dataworking, self.request)
                                if candelete:
                                    deleted, message = deleteRegistryGroup(
                                        activeProjectId,
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
                                            "You cannot delete this group because it contains questions required for the registration."
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
                                    "You cannot delete groups. You started registration."
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


class addQuestionToGroupRegistry_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "group_cod",
                "question_id",
                "question_user_name",
            ]
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
                                    "The access assigned for this project does not allow you to add questions."
                                ),
                            )
                            return response

                        if theUserBelongsToTheProject(
                            dataworking["question_user_name"],
                            activeProjectId,
                            self.request,
                        ):

                            if projectRegStatus(activeProjectId, self.request):
                                dataworking["project_id"] = activeProjectId
                                exitsGroup = exitsRegistryGroup(dataworking, self)
                                if exitsGroup:
                                    data, editable = getQuestionData(
                                        dataworking["question_user_name"],
                                        dataworking["question_id"],
                                        self.request,
                                    )
                                    if data:
                                        if canUseTheQuestion(
                                            dataworking["question_user_name"],
                                            dataworking["project_id"],
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
                                                        "The question was added to the project"
                                                    ),
                                                )
                                                return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "The question has already been assigned to the registration or cannot be used in this section."
                                                ),
                                            )
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "You do not have a question with this ID."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "There is not a group with that code."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You cannot add questions. You started registration."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You are trying to add a question from a user that does not belong to this project."
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


class deleteQuestionFromGroupRegistry_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "group_cod",
                "question_id",
                "question_user_name",
            ]
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
                                    "The access assigned for this project does not allow you to delete questions."
                                ),
                            )
                            return response

                        if projectRegStatus(activeProjectId, self.request):
                            dataworking["project_id"] = activeProjectId
                            exitsGroup = exitsRegistryGroup(dataworking, self)
                            if exitsGroup:
                                data, editable = getQuestionData(
                                    dataworking["question_user_name"],
                                    dataworking["question_id"],
                                    self.request,
                                )
                                if data:
                                    if data["question_reqinreg"] == 1:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "You can not delete this question because is required during registration."
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
                                                    "You do not have a question with this ID in this group."
                                                ),
                                            )
                                            return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You do not have a question with this ID."
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
                                    "You cannot delete questions. You started the registration."
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


class orderRegistryQuestions_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "order"]
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

                        dataworking["project_id"] = activeProjectId
                        if projectRegStatus(activeProjectId, self.request):
                            if haveTheBasic(
                                activeProjectId,
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
                                            questionsInProject = (
                                                getRegistryQuestionsApi(
                                                    dataworking, self
                                                )
                                            )
                                            if sorted(questionsInProject) == sorted(
                                                questions
                                            ):
                                                modified, error = saveRegistryOrder(
                                                    activeProjectId,
                                                    originalData,
                                                    self.request,
                                                )
                                                response = Response(
                                                    status=200,
                                                    body=self._(
                                                        "The order of the groups and questions has been changed."
                                                    ),
                                                )
                                                return response
                                            else:
                                                response = Response(
                                                    status=401,
                                                    body=self._(
                                                        "You are ordering questions that are not part of the form or you are forgetting to order some questions that belong to the form."
                                                    ),
                                                )
                                                return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "You are ordering groups that are not part of the form or you are forgetting to order some groups that belong to the form."
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
                                    body=self._("No group and questions to order."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You cannot order the groups and questions. You have started the registration."
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
