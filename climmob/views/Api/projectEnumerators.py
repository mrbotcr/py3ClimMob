from ..classes import apiView
from ...processes import projectExists
from ...processes import (
    getProjectEnumerators,
    isEnumeratorAssigned,
    enumeratorExists,
    getUsableEnumerators,
    addEnumeratorToProject,
    getTheProjectIdForOwner,
    removeEnumeratorFromProject,
    getAccessTypeForProject,
    theUserBelongsToTheProject,
    getProjectData
)
from ...products.fieldagents.fieldagents import create_fieldagents_report
from climmob.products import stopTasksByProcess
from pyramid.response import Response
import json


class addProjectEnumerator_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"user_owner", u"enum_id", u"enum_user_name"]
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

                    if accessType == 4:
                        response = Response(
                            status=401,
                            body=self._(
                                "The access assigned for this project does not allow you to add field agents."
                            ),
                        )
                        return response

                    if theUserBelongsToTheProject(
                        dataworking["enum_user_name"], activeProjectId, self.request
                    ):
                        if enumeratorExists(
                            dataworking["enum_user_name"],
                            dataworking["enum_id"],
                            self.request,
                        ):

                            if isEnumeratorAssigned(
                                dataworking["enum_user_name"],
                                activeProjectId,
                                dataworking["enum_id"],
                                self.request,
                            ):
                                added, message = addEnumeratorToProject(
                                    activeProjectId,
                                    dataworking["enum_id"],
                                    dataworking["enum_user_name"],
                                    self.request,
                                )
                                if not added:
                                    response = Response(status=401, body=message)
                                    return response
                                else:
                                    # EDITED FOR CREATE THE REPORT
                                    stopTasksByProcess(
                                        self.request,
                                        activeProjectId,
                                        "create_fieldagents",
                                    )
                                    locale = self.request.locale_name
                                    create_fieldagents_report(
                                        locale,
                                        self.request,
                                        dataworking["user_owner"],
                                        dataworking["project_cod"],
                                        activeProjectId,
                                        getProjectEnumerators(
                                            activeProjectId, self.request,
                                        ),
                                        getProjectData(activeProjectId, self.request)
                                    )
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "The field agent has been added to the project."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The field agent is inactive or is already assigned to the project."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not enumerator with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You are trying to add a field agent from a user that does not belong to this project."
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
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class readProjectEnumerators_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod", u"user_owner"]
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
                            getProjectEnumerators(activeProjectId, self.request,)
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


class readPossibleProjectEnumerators_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod", u"user_owner"]
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
                                "The access assigned for this project does not allow you to make modifications."
                            ),
                        )
                        return response

                    response = Response(
                        status=200,
                        body=json.dumps(
                            getUsableEnumerators(activeProjectId, self.request,)
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


class deleteProjectEnumerator_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"user_owner", u"enum_id", u"enum_user_name"]
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

                    if accessType == 4:
                        response = Response(
                            status=401,
                            body=self._(
                                "The access assigned for this project does not allow you to delete field agents."
                            ),
                        )
                        return response

                    if enumeratorExists(
                        dataworking["enum_user_name"],
                        dataworking["enum_id"],
                        self.request,
                    ):
                        if not isEnumeratorAssigned(
                            dataworking["enum_user_name"],
                            activeProjectId,
                            dataworking["enum_id"],
                            self.request,
                        ):
                            deleted, message = removeEnumeratorFromProject(
                                activeProjectId, dataworking["enum_id"], self.request,
                            )

                            if deleted:
                                # EDITED FOR CREATE THE REPORT
                                stopTasksByProcess(
                                    self.request, activeProjectId, "create_fieldagents",
                                )
                                locale = self.request.locale_name
                                create_fieldagents_report(
                                    locale,
                                    self.request,
                                    dataworking["user_owner"],
                                    dataworking["project_cod"],
                                    activeProjectId,
                                    getProjectEnumerators(
                                        activeProjectId, self.request,
                                    ),
                                    getProjectData(self.request)
                                )
                                response = Response(
                                    status=200,
                                    body=self._(
                                        "The field agent was removed from the project."
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
                                    "The field agent is inactive or is not assigned to the project."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "There is not enumerator with that identifier."
                            ),
                        )
                        return response

                else:
                    response = Response(
                        status=401, body=self._("There is no project with that code."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
