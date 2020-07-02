from ..classes import apiView
from ...processes import projectExists
from ...processes import (
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
)

from pyramid.response import Response
import json


class addProjectTechnology_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"tech_id"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if projectRegStatus(
                        self.user.login, dataworking["project_cod"], self.request
                    ):
                        if technologyExist(dataworking, self.request):

                            if not isTechnologyAssigned(dataworking, self.request):
                                added, message = addTechnologyProject(
                                    self.user.login,
                                    dataworking["project_cod"],
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
                                            "The technology has been added to the project."
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
                                    "There is not technology with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You can not add more technologies. You started the registry."
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
                            searchTechnologiesInProject(
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


class readPossibleProjectTechnologies_view(apiView):
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
                            searchTechnologies(
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


class deleteProjectTechnology_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"tech_id"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if projectRegStatus(
                        self.user.login, dataworking["project_cod"], self.request
                    ):
                        if technologyExist(dataworking, self.request):
                            if isTechnologyAssigned(dataworking, self.request):
                                deleted, message = deleteTechnologyProject(
                                    self.user.login,
                                    dataworking["project_cod"],
                                    dataworking["tech_id"],
                                    self.request,
                                )
                                if deleted:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "The technology was removed from the project."
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
                                    "There is not technology with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You can not delete technologies. You started the registry."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


# ___________________________________________________________ALIAS_______________________________________________________#


class addProjectTechnologyAlias_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [u"project_cod", u"tech_id", u"alias_id"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if projectRegStatus(
                        self.user.login, dataworking["project_cod"], self.request
                    ):
                        if technologyExist(dataworking, self.request):
                            if isTechnologyAssigned(dataworking, self.request):
                                if existAlias(dataworking, self.request):
                                    if not getAliasAssigned(dataworking, self.request):
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
                                                "The alias is assigned to the project."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "There is not alias with that identifier for this technology."
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
                                    "There is not technology with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You can not add Alias to technologies. You started the registry."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class addProjectTechnologyAliasExtra_view(apiView):
    def processView(self):
        if self.request.method == "POST":
            obligatory = [u"project_cod", u"tech_id", u"alias_name"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if projectRegStatus(
                        self.user.login, dataworking["project_cod"], self.request
                    ):
                        if technologyExist(dataworking, self.request):
                            if isTechnologyAssigned(dataworking, self.request):
                                if not findTechAlias(dataworking, self.request):
                                    added, message = addTechAliasExtra(
                                        dataworking, self.request
                                    )
                                    if not added:
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
                                            "This alias already exists in the technology."
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
                                    "There is not technology with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You can not add Alias to technologies. You started the registry."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class readProjectTechnologiesAlias_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod", u"tech_id"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if technologyExist(dataworking, self.request):
                        if isTechnologyAssigned(dataworking, self.request):
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    AliasSearchTechnologyInProject(
                                        dataworking["tech_id"],
                                        self.user.login,
                                        dataworking["project_cod"],
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
                            body=self._(
                                "There is not technology with that identifier."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class readProjectTechnologiesAliasExtra_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod", u"tech_id"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if technologyExist(dataworking, self.request):
                        if isTechnologyAssigned(dataworking, self.request):
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    AliasExtraSearchTechnologyInProject(
                                        dataworking["tech_id"],
                                        self.user.login,
                                        dataworking["project_cod"],
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
                            body=self._(
                                "There is not technology with that identifier."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class readPossibleProjectTechnologiesAlias_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod", u"tech_id"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,
                                    body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if technologyExist(dataworking, self.request):
                        if isTechnologyAssigned(dataworking, self.request):
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    AliasSearchTechnology(
                                        dataworking["tech_id"],
                                        self.user.login,
                                        dataworking["project_cod"],
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
                            body=self._(
                                "There is not technology with that identifier."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class deleteProjectTechnologyAlias_view(apiView):
    def processView(self):

        if self.request.method == "POST":
            obligatory = [u"project_cod", u"tech_id", u"alias_id"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                exitsproject = projectExists(
                    self.user.login, dataworking["project_cod"], self.request
                )
                if exitsproject:
                    if projectRegStatus(
                        self.user.login, dataworking["project_cod"], self.request
                    ):
                        if technologyExist(dataworking, self.request):
                            if isTechnologyAssigned(dataworking, self.request):
                                if findAssignedAlias(dataworking, self.request):
                                    delete, message = deleteAliasTechnology(
                                        self.user.login,
                                        dataworking["project_cod"],
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
                                                "The alias has been delete to the project."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "There is not alias with that identifier for this technology."
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
                                    "There is not technology with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You can not delete Alias to technologies. You started the registry."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
