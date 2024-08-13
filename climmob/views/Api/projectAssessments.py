import json

from pyramid.response import Response

from climmob.processes import (
    projectExists,
    getProjectAssessments,
    addProjectAssessment,
    projectAsessmentStatus,
    assessmentExists,
    modifyProjectAssessment,
    deleteProjectAssessment,
    getAssessmentQuestions,
    haveTheBasicStructureAssessment,
    addAssessmentGroup,
    exitsAssessmentGroup,
    modifyAssessmentGroup,
    canDeleteTheAssessmentGroup,
    deleteAssessmentGroup,
    availableAssessmentQuestions,
    QuestionsOptions,
    addAssessmentQuestionToGroup,
    getQuestionData,
    canUseTheQuestionAssessment,
    exitsQuestionInGroupAssessment,
    deleteAssessmentQuestionFromGroup,
    getAssessmentGroup,
    getAssessmentQuestionsApi,
    saveAssessmentOrder,
    getTheProjectIdForOwner,
    getAccessTypeForProject,
    theUserBelongsToTheProject,
    getProjectData,
)
from climmob.views.classes import apiView


class ReadProjectAssessmentsView(apiView):
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
                            getProjectAssessments(
                                activeProjectId,
                                self.request,
                            )
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


class AddNewAssessmentView(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "ass_desc",
                "ass_days",
                "ass_final",
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
                                    "The access assigned for this project does not allow you to add assessments."
                                ),
                            )
                            return response

                        if dataworking["ass_days"].isdigit():
                            dataworking["userOwner"] = dataworking["user_owner"]
                            dataworking["project_id"] = activeProjectId
                            added, msg = addProjectAssessment(
                                dataworking, self.request, "API"
                            )
                            if not added:
                                response = Response(status=401, body=msg)
                                return response
                            else:
                                response = Response(status=200, body=json.dumps(msg))
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("The parameter ass_days must be a number."),
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


class UpdateProjectAssessmentView(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "ass_cod",
                "ass_desc",
                "ass_days",
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
                                    "The access assigned for this project does not allow you to update assessments."
                                ),
                            )
                            return response

                        if dataworking["ass_days"].isdigit():
                            if assessmentExists(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                dataworking["project_id"] = activeProjectId
                                mdf, msg = modifyProjectAssessment(
                                    dataworking, self.request
                                )
                                if not mdf:
                                    response = Response(status=401, body=msg)
                                    return response
                                else:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "Data collection updated successfully."
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
                                body=self._("The parameter ass_days must be a number."),
                            )
                            return response
                        # else:
                        #    response = Response(
                        #        status=401,
                        #        body=self._(
                        #            "You cannot update data collection moments. You already started the data collection."
                        #        ),
                        #    )
                        #    return response
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


class DeleteProjectAssessmentView(apiView):
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
                                    "The access assigned for this project does not allow you to delete assessments."
                                ),
                            )
                            return response

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                delete, msg = deleteProjectAssessment(
                                    dataworking["user_owner"],
                                    activeProjectId,
                                    dataworking["project_cod"],
                                    dataworking["ass_cod"],
                                    self.request,
                                )
                                if not delete:
                                    response = Response(status=401, body=msg)
                                    return response
                                else:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "Data collection moment deleted succesfully."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You can not delete this group because you have questions required for the data collection moment."
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


# _________________________________________ASSESSMENTS GROUPS___________________________________________________#
class ReadProjectAssessmentStructureView(apiView):
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

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            projectDetails = getProjectData(
                                activeProjectId, self.request
                            )
                            projectLabels = [
                                projectDetails["project_label_a"],
                                projectDetails["project_label_b"],
                                projectDetails["project_label_c"],
                            ]
                            data = getAssessmentQuestions(
                                dataworking["user_owner"],
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                                projectLabels,
                                onlyShowTheBasicQuestions=True,
                            )
                            # The following is to help jinja2 to render the groups and questions
                            # This because the scope constraint makes it difficult to control
                            finalCloseQst = ""
                            if data:
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
                                        if data[a]["question_reqinasses"] == 1:
                                            data[grpIndex]["grpCannotDelete"] = True
                                    else:
                                        data[a]["hasQuestions"] = False
                                finalCloseQst = data[len(data) - 1]["hasQuestions"]

                                response = Response(status=200, body=json.dumps(data))
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class CreateAssessmentGroupView(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "ass_cod",
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
                                    "The access assigned for this project does not allow you to create groups."
                                ),
                            )
                            return response

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                haveTheBasicStructureAssessment(
                                    dataworking["user_owner"],
                                    activeProjectId,
                                    dataworking["ass_cod"],
                                    self.request,
                                )
                                dataworking["project_id"] = activeProjectId
                                addgroup, message = addAssessmentGroup(
                                    dataworking, self, "API"
                                )
                                if not addgroup:
                                    if message == "repeated":
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "There is already a group with this name."
                                            ),
                                        )
                                        return response
                                    else:
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
                                        "You cannot update data collection moments. You already started the data collection."
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


class UpdateAssessmentGroupView(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "ass_cod",
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

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                dataworking["project_id"] = activeProjectId
                                exitsGroup = exitsAssessmentGroup(dataworking, self)
                                if exitsGroup:
                                    mdf, message = modifyAssessmentGroup(
                                        dataworking, self
                                    )
                                    if not mdf:
                                        if message == "repeated":
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "There is already a group with this name."
                                                ),
                                            )
                                            return response
                                        else:
                                            response = Response(
                                                status=401, body=message
                                            )
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
                                        body=self._(
                                            "There is not a group with that code."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You cannot update data collection moments. You already started the data collection."
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


class DeleteAssessmentGroupView(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "ass_cod", "group_cod"]
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

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                dataworking["project_id"] = activeProjectId
                                exitsGroup = exitsAssessmentGroup(dataworking, self)
                                if exitsGroup:
                                    candelete = canDeleteTheAssessmentGroup(
                                        dataworking, self.request
                                    )
                                    if candelete:
                                        deleted, message = deleteAssessmentGroup(
                                            activeProjectId,
                                            dataworking["ass_cod"],
                                            dataworking["group_cod"],
                                            self.request,
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
                                                    "Group deleted successfully."
                                                ),
                                            )
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "You can not delete this group because you have questions required for the assessment."
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
                                        "You cannot update data collection moments. You already started the data collection."
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


# _________________________________________ASSESSMENTS GROUPS QUESTIONS___________________________________________________#


class ReadPossibleQuestionForAssessmentGroupView(apiView):
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

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):

                                response = Response(
                                    status=200,
                                    body=json.dumps(
                                        {
                                            "Questions": availableAssessmentQuestions(
                                                activeProjectId,
                                                dataworking["ass_cod"],
                                                self.request,
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
                                    status=401,
                                    body=self._(
                                        "You cannot update data collection moments. You already started the data collection."
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


class AddQuestionToGroupAssessmentView(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "ass_cod",
                "group_cod",
                "question_id",
                "question_user_name",
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
                                    "The access assigned for this project does not allow you to add question to groups."
                                ),
                            )
                            return response
                        if theUserBelongsToTheProject(
                            dataworking["question_user_name"],
                            activeProjectId,
                            self.request,
                        ):

                            if assessmentExists(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                if projectAsessmentStatus(
                                    activeProjectId,
                                    dataworking["ass_cod"],
                                    self.request,
                                ):
                                    dataworking["project_id"] = activeProjectId
                                    exitsGroup = exitsAssessmentGroup(dataworking, self)
                                    if exitsGroup:
                                        data, editable = getQuestionData(
                                            dataworking["question_user_name"],
                                            dataworking["question_id"],
                                            self.request,
                                        )
                                        if data:
                                            if canUseTheQuestionAssessment(
                                                dataworking["question_user_name"],
                                                activeProjectId,
                                                dataworking["ass_cod"],
                                                dataworking["question_id"],
                                                self.request,
                                            ):
                                                dataworking["section_id"] = dataworking[
                                                    "group_cod"
                                                ]
                                                (
                                                    addq,
                                                    message,
                                                ) = addAssessmentQuestionToGroup(
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
                                                            "The question was added to the data collection moment."
                                                        ),
                                                    )
                                                    return response
                                            else:
                                                response = Response(
                                                    status=401,
                                                    body=self._(
                                                        "The question is already assigned to the data collection moment or cannot be used in this section."
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
                                            "You cannot update data collection moments. You already started the data collection."
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


class DeleteQuestionFromGroupAssessmentView(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "ass_cod",
                "group_cod",
                "question_id",
                "question_user_name",
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
                                    "The access assigned for this project does not allow you to delete questions from a group."
                                ),
                            )
                            return response

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
                                self.request,
                            ):
                                dataworking["project_id"] = activeProjectId
                                exitsGroup = exitsAssessmentGroup(dataworking, self)
                                if exitsGroup:
                                    data, editable = getQuestionData(
                                        dataworking["question_user_name"],
                                        dataworking["question_id"],
                                        self.request,
                                    )
                                    if data:
                                        if data["question_reqinasses"] == 1:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "You can not delete this question because is required for this data collection moment."
                                                ),
                                            )
                                            return response
                                        else:
                                            if exitsQuestionInGroupAssessment(
                                                dataworking, self.request
                                            ):
                                                (
                                                    deleted,
                                                    message,
                                                ) = deleteAssessmentQuestionFromGroup(
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
                                        body=self._(
                                            "There is not a group with that code."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You cannot update data collection moments. You already started the data collection."
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


# _________________________________________ASSESSMENTS ORDER GROUPS___________________________________________________#
class orderAssessmentQuestions_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "ass_cod", "order"]
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
                                    "The access assigned for this project does not allow you to order the questions."
                                ),
                            )
                            return response

                        if assessmentExists(
                            activeProjectId,
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                activeProjectId,
                                dataworking["ass_cod"],
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
                                        dataworking["project_id"] = activeProjectId
                                        groupsInProject = getAssessmentGroup(
                                            dataworking, self
                                        )
                                        if sorted(groupsInProject) == sorted(groups):
                                            questionsInProject = (
                                                getAssessmentQuestionsApi(
                                                    dataworking, self
                                                )
                                            )
                                            if sorted(questionsInProject) == sorted(
                                                questions
                                            ):
                                                modified, error = saveAssessmentOrder(
                                                    activeProjectId,
                                                    dataworking["ass_cod"],
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
                                        "You cannot update data collection moments. You already started the data collection."
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
