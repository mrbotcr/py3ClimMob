import json

from pyramid.response import Response

from climmob.processes import (
    projectExists,
    searchTechnologiesInProject,
    searchTechnologies,
    technologyExist,
    isTechnologyAssigned,
    addTechnologyProject,
    deleteTechnologyProject,
    AliasSearchTechnology,
    AliasSearchTechnologyInProject,
    AliasExtraSearchTechnologyInProject,
    existAlias,
    getAliasAssigned,
    AddAliasTechnology,
    deleteAliasTechnology,
    findAssignedAlias,
    findTechAlias,
    addTechAliasExtra,
    projectRegStatus,
    getTheProjectIdForOwner,
    getAccessTypeForProject,
    theUserBelongsToTheProject,
)
from climmob.views.classes import apiView


class addProjectTechnology_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "tech_id", "tech_user_name"]
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
                                "The access assigned for this project does not allow you to add technologies."
                            ),
                        )
                        return response
                    if theUserBelongsToTheProject(
                        dataworking["tech_user_name"], activeProjectId, self.request
                    ):

                        if projectRegStatus(activeProjectId, self.request):
                            if technologyExist(
                                dataworking["tech_id"],
                                dataworking["tech_user_name"],
                                self.request,
                            ):
                                dataworking["project_id"] = activeProjectId
                                if not isTechnologyAssigned(dataworking, self.request):
                                    added, message = addTechnologyProject(
                                        activeProjectId,
                                        dataworking["tech_id"],
                                        self.request,
                                    )
                                    if not added:
                                        response = Response(status=401, body=message)
                                        return response
                                    else:
                                        response = Response(
                                            status=200,
                                            body=self._(
                                                "The technology was added correctly."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The technology is already assigned to the project."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no technology with that identifier."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You cannot add more technologies. You started the registry."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You are trying to add a tech from a user that does not belong to this project."
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


class readProjectTechnologies_view(apiView):
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
                            searchTechnologiesInProject(
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


class readPossibleProjectTechnologies_view(apiView):
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

                    response = Response(
                        status=200,
                        body=json.dumps(
                            searchTechnologies(
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


class deleteProjectTechnology_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = ["project_cod", "user_owner", "tech_id", "tech_user_name"]
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
                                "The access assigned for this project does not allow you to delete technologies."
                            ),
                        )
                        return response

                    if projectRegStatus(activeProjectId, self.request):
                        if technologyExist(
                            dataworking["tech_id"],
                            dataworking["tech_user_name"],
                            self.request,
                        ):
                            dataworking["project_id"] = activeProjectId
                            if isTechnologyAssigned(dataworking, self.request):
                                deleted, message = deleteTechnologyProject(
                                    activeProjectId,
                                    dataworking["tech_id"],
                                    self.request,
                                )
                                if deleted:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "The technology has been removed from the project."
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
                                        "The technology is not assigned to the project."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is no technology with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You cannot delete technologies. You have started registration."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


# ___________________________________________________________ALIAS_______________________________________________________#


class addProjectTechnologyAlias_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "tech_id",
                "tech_user_name",
                "alias_id",
            ]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
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
                                "The access assigned for this project does not allow you to add technology options."
                            ),
                        )
                        return response

                    if theUserBelongsToTheProject(
                        dataworking["tech_user_name"], activeProjectId, self.request
                    ):

                        if projectRegStatus(activeProjectId, self.request):
                            if technologyExist(
                                dataworking["tech_id"],
                                dataworking["tech_user_name"],
                                self.request,
                            ):
                                dataworking["project_id"] = activeProjectId
                                if isTechnologyAssigned(dataworking, self.request):
                                    if existAlias(dataworking, self.request):
                                        if not getAliasAssigned(
                                            dataworking, activeProjectId, self.request
                                        ):
                                            add, message = AddAliasTechnology(
                                                dataworking, self.request
                                            )
                                            if not add:
                                                response = Response(
                                                    status=401, body=message
                                                )
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
                                                    "The technology option has not been assigned to the project."
                                                ),
                                            )
                                            return response
                                    else:
                                        response = Response(
                                            status=401,
                                            body=self._(
                                                "There is no technology option with that identifier for this technology."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The technology is not assigned to the project."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no technology with that identifier."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You can not add an technology option for technologies. You have already started registration."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You are trying to add a technology alias from a user that does not belong to this project."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class addProjectTechnologyAliasExtra_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "tech_id",
                "tech_user_name",
                "alias_name",
            ]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
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
                                "The access assigned for this project does not allow you to add technology options."
                            ),
                        )
                        return response

                    if theUserBelongsToTheProject(
                        dataworking["tech_user_name"], activeProjectId, self.request
                    ):

                        if projectRegStatus(activeProjectId, self.request):
                            if technologyExist(
                                dataworking["tech_id"],
                                dataworking["tech_user_name"],
                                self.request,
                            ):
                                dataworking["project_id"] = activeProjectId
                                if isTechnologyAssigned(dataworking, self.request):
                                    if not findTechAlias(dataworking, self.request):
                                        added, message = addTechAliasExtra(
                                            dataworking, self.request
                                        )
                                        if not added:
                                            response = Response(
                                                status=401, body=message
                                            )
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
                                                "This technology option already exists for the technology."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "The technology is not assigned to the project."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no technology with that identifier."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "You can not add technology option for technologies. You have already started registration."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You are trying to add a technology alias extra from a user that does not belong to this project."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class readProjectTechnologiesAlias_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = ["project_cod", "user_owner", "tech_id", "tech_user_name"]
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

                    if technologyExist(
                        dataworking["tech_id"],
                        dataworking["tech_user_name"],
                        self.request,
                    ):
                        dataworking["project_id"] = activeProjectId
                        if isTechnologyAssigned(dataworking, self.request):
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    AliasSearchTechnologyInProject(
                                        dataworking["tech_id"],
                                        activeProjectId,
                                        self.request,
                                    )
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The technology is not assigned to the project."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no technology with that identifier."),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._("There is no project with that code."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class readProjectTechnologiesAliasExtra_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = ["project_cod", "user_owner", "tech_id", "tech_user_name"]
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

                    if technologyExist(
                        dataworking["tech_id"],
                        dataworking["tech_user_name"],
                        self.request,
                    ):
                        dataworking["project_id"] = activeProjectId
                        if isTechnologyAssigned(dataworking, self.request):
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    AliasExtraSearchTechnologyInProject(
                                        dataworking["tech_id"],
                                        activeProjectId,
                                        self.request,
                                    )
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The technology is not assigned to the project."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no technology with that identifier."),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._("There is no project with that code."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class readPossibleProjectTechnologiesAlias_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = ["project_cod", "user_owner", "tech_id", "tech_user_name"]
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

                    if technologyExist(
                        dataworking["tech_id"],
                        dataworking["tech_user_name"],
                        self.request,
                    ):
                        dataworking["project_id"] = activeProjectId
                        if isTechnologyAssigned(dataworking, self.request):
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    AliasSearchTechnology(
                                        dataworking["tech_id"],
                                        activeProjectId,
                                        self.request,
                                    )
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The technology is not assigned to the project."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no technology with that identifier."),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._("There is no project with that code."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class deleteProjectTechnologyAlias_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [
                "project_cod",
                "user_owner",
                "tech_id",
                "tech_user_name",
                "alias_id",
            ]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
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
                                "The access assigned for this project does not allow you to delete technology options."
                            ),
                        )
                        return response

                    if projectRegStatus(activeProjectId, self.request):
                        if technologyExist(
                            dataworking["tech_id"],
                            dataworking["tech_user_name"],
                            self.request,
                        ):
                            dataworking["project_id"] = activeProjectId
                            if isTechnologyAssigned(dataworking, self.request):
                                if findAssignedAlias(dataworking, self.request):
                                    delete, message = deleteAliasTechnology(
                                        activeProjectId,
                                        dataworking["tech_id"],
                                        dataworking["alias_id"],
                                        self.request,
                                    )
                                    if not delete:
                                        response = Response(status=401, body=message)
                                        return response
                                    else:
                                        response = Response(
                                            status=200,
                                            body=self._(
                                                "The technology option has been deleted in the project."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "There is no technology option with that identifier for this technology."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The technology is not assigned to the project."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is no technology with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You can not delete the technology option for technologies. You started registration."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
