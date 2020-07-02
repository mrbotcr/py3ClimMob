from ..classes import apiView
from ...processes import (
    getUserTechs,
    findTechInLibrary,
    addTechnology,
    getTechnologyByUser,
    getTechnologyAssigned,
    updateTechnology,
    deleteTechnology,
    getTechnologyByName,
)

from pyramid.response import Response
import json
from heapq import merge


class createTechnology_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"tech_name"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    dataworking["user_name"] = "bioversity"
                    existInGenLibrary = findTechInLibrary(dataworking, self.request)
                    if existInGenLibrary == False:
                        dataworking["user_name"] = self.user.login
                        existInPersLibrary = findTechInLibrary(
                            dataworking, self.request
                        )
                        if existInPersLibrary == False:
                            added, message = addTechnology(dataworking, self.request)
                            if not added:
                                response = Response(status=401, body=message)
                                return response
                            else:
                                tech_data = getTechnologyByName(
                                    dataworking, self.request
                                )
                                # response = Response(status=200, body=self._("The technology was added successfully."))
                                response = Response(
                                    status=200, body=json.dumps(tech_data)
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "This technology already exists in your personal library."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "This technology already exists in the generic library."
                            ),
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


class readTechnologies_view(apiView):
    def processView(self):

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(
                    list(
                        [*getUserTechs(self.user.login, self.request),*getUserTechs("bioversity", self.request)]
                    )
                ),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response

"""list(

        getUserTechs(self.user.login, self.request),getUserTechs("bioversity", self.request)

)"""
def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

class updateTechnology_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"tech_id", u"tech_name"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    dataworking["user_name"] = "bioversity"
                    existInGenLibrary = findTechInLibrary(dataworking, self.request)
                    if existInGenLibrary == False:
                        dataworking["user_name"] = self.user.login
                        existInPersLibrary = findTechInLibrary(
                            dataworking, self.request
                        )
                        if existInPersLibrary == False:
                            if getTechnologyByUser(dataworking, self.request):
                                if not getTechnologyAssigned(dataworking, self.request):
                                    update, message = updateTechnology(
                                        dataworking, self.request
                                    )
                                    if not update:
                                        response = Response(status=401, body=message)
                                        return response
                                    else:
                                        response = Response(
                                            status=200,
                                            body=self._(
                                                "The technology was modify successfully."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You can not update this technology because it is assigned to a project."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You do not have a technology with this id."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "This technology already exists in your personal library."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "This technology already exists in the generic library."
                            ),
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


class deletetechnologyView_api(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"tech_id"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                if getTechnologyByUser(dataworking, self.request):
                    if not getTechnologyAssigned(dataworking, self.request):
                        dlt, message = deleteTechnology(dataworking, self.request)
                        if not dlt:
                            response = Response(status=401, body=message)
                            return response
                        else:
                            response = Response(
                                status=200,
                                body=self._("The technology was deleted successfully."),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You can not delete this technology because it is assigned to a project."
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
