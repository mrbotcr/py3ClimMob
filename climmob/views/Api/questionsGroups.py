from ..classes import apiView
from ...processes import (
    getCategoryById,
    categoryExistsWithDifferentId,
    categoryExistsByUserAndId,
    getCategoriesParents,
    categoryExists,
    theCategoryHaveQuestions,
    addCategory,
    updateCategory,
    deleteCategory,
)

import json
from pyramid.response import Response
import uuid


class createGroupOfQuestion_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = ["qstgroups_name", "user_name"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

            obligatoryKeys = True

            for key in obligatory:
                if key not in dataworking.keys():
                    obligatoryKeys = False

            if obligatoryKeys:

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    dataworking["qstgroups_id"] = str(uuid.uuid4())[-12:]
                    if not categoryExists(
                        self.user.login, dataworking["qstgroups_name"], self.request
                    ):
                        added, message = addCategory(
                            self.user.login, dataworking, self.request
                        )
                        if not added:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There was a problem with the creation of the category."
                                ),
                            )
                            return response
                        else:
                            response = Response(
                                status=200,
                                body=json.dumps(
                                    getCategoryById(
                                        dataworking["qstgroups_id"], self.request
                                    )
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is already a category with this name."),
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
                    body=self._("It is not complying with the obligatory keys."),
                )
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class updateGroupOfQuestion_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = ["qstgroups_name", "qstgroups_id", "user_name"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

            obligatoryKeys = True

            for key in obligatory:
                if key not in dataworking.keys():
                    obligatoryKeys = False

            if obligatoryKeys:

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    if categoryExistsByUserAndId(
                        self.user.login, dataworking["qstgroups_id"], self.request
                    ):
                        if not categoryExistsWithDifferentId(
                            self.user.login,
                            dataworking["qstgroups_name"],
                            dataworking["qstgroups_id"],
                            self.request,
                        ):
                            update, message = updateCategory(
                                self.user.login, dataworking, self.request
                            )
                            if not update:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There was a problem updating the category."
                                    ),
                                )
                                return response
                            else:
                                response = Response(
                                    status=200,
                                    body=json.dumps(
                                        getCategoryById(
                                            dataworking["qstgroups_id"], self.request
                                        )
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is already a category with this name."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You cannot edit this category because it does not belong to your personal library."
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
                    body=self._("It is not complying with the obligatory keys."),
                )
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class deleteGroupOfQuestion_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = ["qstgroups_id", "user_name"]

            dataworking = json.loads(self.body)
            dataworking["user_name"] = self.user.login

            obligatoryKeys = True

            for key in obligatory:
                if key not in dataworking.keys():
                    obligatoryKeys = False

            if obligatoryKeys:

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    if categoryExistsByUserAndId(
                        self.user.login, dataworking["qstgroups_id"], self.request
                    ):
                        if not theCategoryHaveQuestions(
                            self.user.login, dataworking["qstgroups_id"], self.request
                        ):
                            delete, message = deleteCategory(
                                self.user.login,
                                dataworking["qstgroups_id"],
                                self.request,
                            )
                            if not delete:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There was a problem removing the category."
                                    ),
                                )
                                return response
                            else:
                                response = Response(
                                    status=200,
                                    body=self._("The category was removed."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "This category cannot be removed because it has questions."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._(
                                "You cannot delete this category because it does not belong to your personal library."
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
                    body=self._("It is not complying with the obligatory keys."),
                )
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class readGroupsOfQuestions_view(apiView):
    def processView(self):

        if self.request.method == "GET":

            groups = getCategoriesParents(self.user.login, self.request)
            listOfGroups = []
            for group in groups:
                listOfGroups.append(
                    {
                        "user_name": group[0],
                        "qstgroups_id": group[1],
                        "qstgroups_name": group[2],
                        "numberOfQuestions": group[3],
                    }
                )

            response = Response(status=200, body=json.dumps(listOfGroups),)
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response
