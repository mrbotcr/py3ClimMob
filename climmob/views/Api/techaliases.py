from ..classes import apiView
from pyramid.httpexceptions import HTTPFound
from ...processes import getTechnologyByUser
from ...processes import (
    getTechsAlias,
    findTechalias,
    addTechAlias,
    updateAlias,
    removeAlias,
    existAlias,
    getAliasAssigned,
)

import json
from pyramid.response import Response


class createAlias_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"tech_id", u"alias_name"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    dataworking["user_name"] = self.user.login
                    dataworking["alias_id"] = None
                    if getTechnologyByUser(dataworking, self.request):

                        existAlias = findTechalias(dataworking, self.request)
                        if existAlias == False:
                            added, message = addTechAlias(
                                dataworking, self.request, "API"
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
                            body=self._("You do not have a technology with this id."),
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


class readAlias_view(apiView):
    def processView(self):
        if self.request.method == "GET":
            obligatory = [u"tech_id"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    dataworking["user_name"] = self.user.login
                    if getTechnologyByUser(dataworking, self.request):

                        response = Response(
                            status=200,
                            body=json.dumps(
                                getTechsAlias(dataworking["tech_id"], self.request)
                            ),
                        )
                        return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("You do not have a technology with this id."),
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


class updateAlias_view(apiView):
    def processView(self):
        if self.request.method == "POST":

            obligatory = [u"tech_id", u"alias_id", u"alias_name"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    dataworking["user_name"] = self.user.login
                    if getTechnologyByUser(dataworking, self.request):
                        if existAlias(dataworking, self.request):
                            existAlias2 = findTechalias(dataworking, self.request)
                            if existAlias2 == False:
                                if not getAliasAssigned(dataworking, self.request):
                                    update, message = updateAlias(
                                        dataworking, self.request
                                    )
                                    if not update:
                                        response = Response(status=401, body=message)
                                        return response
                                    else:
                                        response = Response(
                                            status=200,
                                            body=self._(
                                                "The alias was update successfully."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You can not update this alias because it is assigned to a project."
                                        ),
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
                                body=self._("You do not have a alias with this id."),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("You do not have a technology with this id."),
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


class deleteAliasView_api(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"tech_id", u"alias_id"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    dataworking["user_name"] = self.user.login
                    if getTechnologyByUser(dataworking, self.request):
                        if existAlias(dataworking, self.request):
                            if not getAliasAssigned(dataworking, self.request):
                                removed, message = removeAlias(
                                    dataworking, self.request
                                )
                                if not removed:
                                    response = Response(status=401, body=message)
                                    return response
                                else:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "The alias was delete successfully."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You can not delete this alias because it is assigned to a project."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("You do not have a alias with this id."),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("You do not have a technology with this id."),
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
