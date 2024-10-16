import json

from pyramid.response import Response

from climmob.processes import (
    searchEnumerator,
    enumeratorExists,
    addEnumerator,
    deleteEnumerator,
    isEnumeratorPassword,
    modifyEnumerator,
    modifyEnumeratorPassword,
)
from climmob.views.classes import apiView


class CreateEnumeratorView(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                "enum_id",
                "enum_name",
                "enum_password",
                "enum_password_re",
            ]

            possibles = [
                "enum_id",
                "enum_name",
                "enum_password",
                "enum_password_re",
                "enum_telephone",
            ]

            dataworking = json.loads(self.body)

            permitedKeys = True
            for key in dataworking.keys():
                if key not in possibles:
                    permitedKeys = False

            obligatoryKeys = True

            for key in obligatory:
                if key not in dataworking.keys():
                    obligatoryKeys = False

            if obligatoryKeys:
                if permitedKeys:

                    dataInParams = True
                    for key in dataworking.keys():
                        if dataworking[key] == "":
                            dataInParams = False

                    if dataInParams:
                        if (
                            dataworking["enum_password"]
                            == dataworking["enum_password_re"]
                        ):
                            dataworking.pop("enum_password_re")
                            if not enumeratorExists(
                                self.user.login, dataworking["enum_id"], self.request
                            ):
                                added, message = addEnumerator(
                                    self.user.login, dataworking, self.request
                                )
                                if not added:
                                    response = Response(status=401, body=message)
                                    return response
                                else:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "The field agent was created successfully."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "This field agent name already exists."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The password and its retype are not the same."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401, body=self._("Not all parameters have data.")
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._(
                            "You are trying to use a parameter that is not allowed.."
                        ),
                    )
                    return response
            else:
                response = Response(
                    status=401,
                    body=self._("It is not complying with the obligatory keys."),
                )
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class ReadEnumeratorsView(apiView):
    def processView(self):

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(searchEnumerator(self.user.login, self.request)),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class UpdateEnumeratorView(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                "enum_id",
            ]

            possibles = [
                "enum_id",
                "enum_name",
                "enum_password",
                "enum_password_re",
                "enum_telephone",
                "enum_active",
            ]

            dataworking = json.loads(self.body)

            permitedKeys = True
            for key in dataworking.keys():
                if key not in possibles:
                    permitedKeys = False

            obligatoryKeys = True

            for key in obligatory:
                if key not in dataworking.keys():
                    obligatoryKeys = False

            if obligatoryKeys:
                if permitedKeys:

                    dataInParams = True
                    for key in dataworking.keys():
                        if dataworking[key] == "":
                            dataInParams = False

                    if dataInParams:
                        if enumeratorExists(
                            self.user.login, dataworking["enum_id"], self.request
                        ):
                            mdf, message = modifyEnumerator(
                                self.user.login,
                                dataworking["enum_id"],
                                dataworking,
                                self.request,
                            )
                            if not mdf:
                                response = Response(status=401, body=message)
                                return response
                            else:
                                response = Response(
                                    status=200,
                                    body=self._(
                                        "The field agent was modified successfully."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is no field agent with that identifier."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401, body=self._("Not all parameters have data.")
                        )
                        return response
                else:
                    response = Response(
                        status=401,
                        body=self._(
                            "You are trying to use a parameter that is not allowed.."
                        ),
                    )
                    return response
            else:
                response = Response(
                    status=401,
                    body=self._("It is not complying with the obligatory keys."),
                )
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class UpdatePasswordEnumeratorView(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                "enum_id",
                "enum_password",
                "enum_password_new",
                "enum_password_new_re",
            ]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    if enumeratorExists(
                        self.user.login, dataworking["enum_id"], self.request
                    ):
                        if isEnumeratorPassword(
                            self.user.login,
                            dataworking["enum_id"],
                            dataworking["enum_password"],
                            self.request,
                        ):
                            if (
                                dataworking["enum_password_new"]
                                == dataworking["enum_password_new_re"]
                            ):
                                mdf, message = modifyEnumeratorPassword(
                                    self.user.login,
                                    dataworking["enum_id"],
                                    dataworking["enum_password_new"],
                                    self.request,
                                )
                                if not mdf:
                                    response = Response(status=401, body=message)
                                    return response
                                else:
                                    response = Response(
                                        status=200,
                                        body=self._(
                                            "The password was modified successfully."
                                        ),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The new password and the retype are not the same."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("The current password is incorrect."),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "There is no field agent with that identifier."
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


class ApiDeleteEnumeratorView(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = ["enum_id"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                if not enumeratorExists(
                    self.user.login, dataworking["enum_id"], self.request
                ):
                    response = Response(
                        status=401, body=self._("This field agent does not exist.")
                    )
                    return response

                deleted, message = deleteEnumerator(
                    self.user.login, dataworking["enum_id"], self.request
                )
                if not deleted:
                    response = Response(status=401, body=message)
                    return response
                else:
                    response = Response(
                        status=200,
                        body=self._("The field agent was deleted successfully."),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
