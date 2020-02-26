from ..classes import apiView
from pyramid.response import Response
import json

from ...processes import (
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
)


class readProjectAssessments_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401, body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:

                    response = Response(
                        status=200,
                        body=json.dumps(
                            getProjectAssessments(
                                self.user.login,
                                dataworking["project_cod"],
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


class addNewAssessment_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [u"project_cod", u"ass_desc", u"ass_days", u"ass_final"]
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
                        #if projectAsessmentStatus(
                        #    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                        #):
                        if dataworking["ass_days"].isdigit():
                            added, msg = addProjectAssessment(
                                dataworking, self.request, "API"
                            )
                            if not added:
                                response = Response(status=401, body=msg)
                                return response
                            else:
                                response = Response(
                                    status=200, body=json.dumps(msg)
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The parameter ass_days must be a number."
                                ),
                            )
                            return response
                        #else:
                        #    response = Response(
                        #        status=401,
                        #        body=self._(
                        #            "You can not add assessments. You already started the data collection."
                        #        ),
                        #    )
                        #    return response
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


class updateProjectAssessment_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [u"project_cod", u"ass_cod", u"ass_desc", u"ass_days"]
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
                        #if projectAsessmentStatus(
                        #    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                        #):
                        if dataworking["ass_days"].isdigit():
                            if assessmentExists(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking["ass_cod"],
                                self.request,
                            ):
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
                                            "Assessment updated successfully."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is not a assessment with that code."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The parameter ass_days must be a number."
                                ),
                            )
                            return response
                        #else:
                        #    response = Response(
                        #        status=401,
                        #        body=self._(
                        #            "You can not update assessments. You already started the data collection."
                        #        ),
                        #    )
                        #    return response
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


class deleteProjectAssessment_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [u"project_cod", u"ass_cod"]
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
                        if assessmentExists(
                            self.user.login,
                            dataworking["project_cod"],
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                            ):
                                delete, msg = deleteProjectAssessment(
                                    self.user.login,
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
                                        body=self._("Assessment deleted successfully."),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You can not delete the assessment."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a assessment with that code."
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


# _________________________________________ASSESSMENTS GROUPS___________________________________________________#
class readProjectAssessmentStructure_view(apiView):
    def processView(self):
        if self.request.method == "GET":
            obligatory = [u"project_cod", u"ass_cod"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

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
                        if assessmentExists(
                            self.user.login,
                            dataworking["project_cod"],
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            data = getAssessmentQuestions(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking["ass_cod"],
                                self.request,
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
                                    "There is not a assessment with that code."
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class createAssessmentGroup_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                u"project_cod",
                u"ass_cod",
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

                        if assessmentExists(
                            self.user.login,
                            dataworking["project_cod"],
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                            ):
                                haveTheBasicStructureAssessment(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    dataworking["ass_cod"],
                                    self.request,
                                )

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
                                        "You can not update assessments. You already started the data collection."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a assessment with that code."
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


class updateAssessmentGroup_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                u"project_cod",
                u"ass_cod",
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

                        if assessmentExists(
                            self.user.login,
                            dataworking["project_cod"],
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                            ):
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
                                        "You can not update assessments. You already started the data collection."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a assessment with that code."
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


class deleteAssessmentGroup_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [u"project_cod", u"ass_cod", u"group_cod"]
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

                        if assessmentExists(
                            self.user.login,
                            dataworking["project_cod"],
                            dataworking["ass_cod"],
                            self.request,
                        ):
                            if projectAsessmentStatus(
                                    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                            ):
                                exitsGroup = exitsAssessmentGroup(dataworking, self)
                                if exitsGroup:
                                    candelete = canDeleteTheAssessmentGroup(
                                        dataworking, self.request
                                    )
                                    if candelete:
                                        deleted, message = deleteAssessmentGroup(
                                            self.user.login,
                                            dataworking["project_cod"],
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
                                        "You can not update assessments. You already started the data collection."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a assessment with that code."
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


# _________________________________________ASSESSMENTS GROUPS QUESTIONS___________________________________________________#


class readPossibleQuestionForAssessmentGroup_view(apiView):
    def processView(self):
        if self.request.method == "GET":
            obligatory = [u"project_cod", u"ass_cod"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

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
                        if assessmentExists(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking["ass_cod"],
                                self.request,
                        ):
                            if projectAsessmentStatus(
                                    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                            ):

                                response = Response(
                                    status=200,
                                    body=json.dumps(
                                        {
                                            "Questions": availableAssessmentQuestions(
                                                self.user.login,
                                                dataworking["project_cod"],
                                                dataworking["ass_cod"],
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
                                    status=401,
                                    body=self._(
                                        "You can not update assessments. You already started the data collection."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a assessment with that code."
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class addQuestionToGroupAssessment_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [u"project_cod", u"ass_cod", u"group_cod", u"question_id"]
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
                        if assessmentExists(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking["ass_cod"],
                                self.request,
                        ):
                            if projectAsessmentStatus(
                                    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                            ):
                                exitsGroup = exitsAssessmentGroup(dataworking, self)
                                if exitsGroup:
                                    data, editable = getQuestionData(
                                        self.user.login,
                                        dataworking["question_id"],
                                        self.request,
                                    )
                                    if data:
                                        if canUseTheQuestionAssessment(
                                            self.user.login,
                                            dataworking["project_cod"],
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
                                                        "The question was added to the assessment"
                                                    ),
                                                )
                                                return response
                                        else:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "The question is already assigned to assessment or can not be used in this section."
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
                                        body=self._(
                                            "There is not a group with that code."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You can not update assessments. You already started the data collection."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a assessment with that code."
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


class deleteQuestionFromGroupAssessment_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [u"project_cod", u"ass_cod", u"group_cod", u"question_id"]
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
                        if assessmentExists(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking["ass_cod"],
                                self.request,
                        ):
                            if projectAsessmentStatus(
                                    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
                            ):
                                exitsGroup = exitsAssessmentGroup(dataworking, self)
                                if exitsGroup:
                                    data, editable = getQuestionData(
                                        self.user.login,
                                        dataworking["question_id"],
                                        self.request,
                                    )
                                    if data:
                                        if data["question_reqinasses"] == 1:
                                            response = Response(
                                                status=401,
                                                body=self._(
                                                    "You can not delete this question because is required in the assessment."
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
                                        body=self._(
                                            "There is not a group with that code."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You can not update assessments. You already started the data collection."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a assessment with that code."
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


# _________________________________________ASSESSMENTS ORDER GROUPS___________________________________________________#
class orderAssessmentQuestions_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"ass_cod", u"order"]
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
                        if assessmentExists(
                                self.user.login,
                                dataworking["project_cod"],
                                dataworking["ass_cod"],
                                self.request,
                        ):
                            if projectAsessmentStatus(
                                    self.user.login, dataworking["project_cod"], dataworking["ass_cod"], self.request
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
                                        groupsInProject = getAssessmentGroup(
                                            dataworking, self
                                        )
                                        if sorted(groupsInProject) == sorted(groups):
                                            questionsInProject = getAssessmentQuestionsApi(
                                                dataworking, self
                                            )
                                            if sorted(questionsInProject) == sorted(
                                                questions
                                            ):
                                                modified, error = saveAssessmentOrder(
                                                    self.user.login,
                                                    dataworking["project_cod"],
                                                    dataworking["ass_cod"],
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
                                        "You can not update assessments. You already started the data collection."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a assessment with that code."
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
