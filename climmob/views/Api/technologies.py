import json

from pyramid.response import Response

from climmob.processes import (
    get_user_techs,
    find_tech_in_library,
    add_technology,
    get_technology_by_user,
    get_technology_assigned,
    update_technology,
    delete_technology,
    get_technology_by_name,
)
from climmob.views.classes import apiView


class CreateTechnologyView(apiView):
    def process_view(self):

        if self.request.method == "POST":

            obligatory = ["tech_name"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                data_in_params = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        data_in_params = False

                if data_in_params:
                    dataworking["user_name"] = "bioversity"
                    exist_in_gen_library = find_tech_in_library(dataworking, self.request)
                    if exist_in_gen_library == False:
                        dataworking["user_name"] = self.user.login
                        exist_in_pers_library = find_tech_in_library(
                            dataworking, self.request
                        )
                        if exist_in_pers_library == False:
                            added, message = add_technology(dataworking, self.request)
                            if not added:
                                response = Response(status=401, body=message)
                                return response
                            else:
                                tech_data = get_technology_by_name(
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


class ReadTechnologiesView(apiView):
    def process_view(self):

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(
                    list(
                        [
                            *get_user_techs(self.user.login, self.request),
                            *get_user_techs("bioversity", self.request),
                        ]
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


class UpdateTechnologyView(apiView):
    def process_view(self):

        if self.request.method == "POST":

            obligatory = ["tech_id", "tech_name"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                data_in_params = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        data_in_params = False

                if data_in_params:
                    dataworking["user_name"] = "bioversity"
                    exist_in_gen_library = find_tech_in_library(dataworking, self.request)
                    if exist_in_gen_library == False:
                        dataworking["user_name"] = self.user.login
                        exist_in_pers_library = find_tech_in_library(
                            dataworking, self.request
                        )
                        if exist_in_pers_library == False:
                            if get_technology_by_user(dataworking, self.request):
                                if not get_technology_assigned(dataworking, self.request):
                                    update, message = update_technology(
                                        dataworking, self.request
                                    )
                                    if not update:
                                        response = Response(status=401, body=message)
                                        return response
                                    else:
                                        response = Response(
                                            status=200,
                                            body=self._(
                                                "The technology was modified successfully."
                                            ),
                                        )
                                        return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._(
                                            "You cannot update this technology because it has been assigned to a project."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "You do not have a technology with this ID."
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


class DeleteTechnologyViewAPI(apiView):
    def process_view(self):

        if self.request.method == "POST":

            obligatory = ["tech_id"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login
                if get_technology_by_user(dataworking, self.request):
                    if not get_technology_assigned(dataworking, self.request):
                        dlt, message = delete_technology(dataworking, self.request)
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
                                "You cannot delete this technology because it has been assigned to a project."
                            ),
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._("You do not have a technology with this ID."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
