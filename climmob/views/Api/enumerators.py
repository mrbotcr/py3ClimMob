from ..classes import apiView
from ...processes import (
    searchEnumerator,
    enumeratorExists,
    addEnumerator,
    deleteEnumerator,
    isEnumeratorPassword,
    modifyEnumerator,
    getEnumeratorData,
    modifyEnumeratorPassword,
)

from pyramid.response import Response
import json


class createEnumerator_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                u"enum_id",
                u"enum_name",
                u"enum_password",
                u"enum_password_re",
            ]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    if dataworking["enum_password"] == dataworking["enum_password_re"]:
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
                                        "The enumerator was created successfully."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._("This enumerator name already exists."),
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
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class readEnumerators_view(apiView):
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


class updateEnumerator_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"enum_id", u"enum_name", u"enum_active"]
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
                                    "The enumerator was modified successfully."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no enumerator with that identifier."),
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


class updatePasswordEnumerator_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                u"enum_id",
                u"enum_password",
                u"enum_password_new",
                u"enum_password_new_re",
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
                            body=self._("There is no enumerator with that identifier."),
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


class apiDeleteEnumerator_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [u"enum_id"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):

                if not enumeratorExists(
                    self.user.login, dataworking["enum_id"], self.request
                ):
                    response = Response(
                        status=401, body=self._("This enumerator does not exist.")
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
                        body=self._("The enumerator was deleted successfully"),
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response
