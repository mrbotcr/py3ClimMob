from climmob.views.classes import apiView
from climmob.processes import (
    getListOfLanguagesByUser,
    getListOfUnusedLanguagesByUser,
    languageExistInI18nUser,
    languageExistInI18n,
    addI18nUser,
    deleteI18nUser,
    getAllTranslationsOfPhrasesByLanguage,
    generalPhraseExistsWithID,
    savePhraseTranslation,
)
import datetime
import json
import re

from pyramid.response import Response


class readListOfLanguages_view(apiView):
    def processView(self):

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(
                    getListOfLanguagesByUser(self.request, self.user.login)
                ),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class addLanguageForUse_view(apiView):
    def processView(self):

        if self.request.method == "POST":

            obligatory = [
                "lang_code",
            ]

            possibles = [
                "lang_code",
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

                        if not languageExistInI18nUser(
                            dataworking["lang_code"], self.user.login, self.request
                        ):

                            if languageExistInI18n(
                                dataworking["lang_code"], self.request
                            ):
                                dataworking["user_name"] = self.user.login
                                added, error = addI18nUser(dataworking, self.request)

                                if added:
                                    response = Response(
                                        status=200,
                                        body=self._("Language added successfully."),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._("The language could not be added."),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "The language does not exist in the list of languages available for use in ClimMob."
                                    ),
                                )
                                return response

                        else:
                            response = Response(
                                status=401,
                                body=self._("This language has already been added."),
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


class deleteLanguage_view(apiView):
    def processView(self):
        if self.request.method == "POST":

            obligatory = [
                "lang_code",
            ]

            possibles = [
                "lang_code",
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

                        if languageExistInI18nUser(
                            dataworking["lang_code"], self.user.login, self.request
                        ):

                            dataworking["user_name"] = self.user.login
                            deleted, error = deleteI18nUser(dataworking, self.request)

                            if deleted:
                                response = Response(
                                    status=200,
                                    body=self._("Language successfully deleted."),
                                )
                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("The language could not be removed."),
                                )
                                return response

                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The language could not be removed because it is not included in their languages of use."
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


class readListOfUnusedLanguages_view(apiView):
    def processView(self):

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(
                    getListOfUnusedLanguagesByUser(self.request, self.user.login)
                ),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class readAllGeneralPhrases_view(apiView):
    def processView(self):

        if self.request.method == "GET":

            obligatory = ["user_name", "lang_code"]

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
            dataworking["user_name"] = self.user.login

            if sorted(obligatory) == sorted(dataworking.keys()):

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:

                    if not languageExistInI18nUser(
                        dataworking["lang_code"],
                        self.user.login,
                        self.request,
                    ):
                        response = Response(
                            status=401,
                            body=self._(
                                "The language does not belong to your list of languages to be used."
                            ),
                        )
                        return response

                    response = Response(
                        status=200,
                        body=json.dumps(
                            getAllTranslationsOfPhrasesByLanguage(
                                self.request, self.user.login, dataworking["lang_code"]
                            )
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
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class changeGeneralPhrases_view(apiView):
    def processView(self):
        if self.request.method == "POST":

            obligatory = ["lang_code", "phrase_id", "phrase_desc"]

            possibles = ["lang_code", "phrase_id", "phrase_desc"]

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
                        if key not in ["phrase_desc"]:
                            if dataworking[key] == "":
                                dataInParams = False

                    if dataInParams:

                        if languageExistInI18nUser(
                            dataworking["lang_code"], self.user.login, self.request
                        ):

                            if generalPhraseExistsWithID(
                                self.request, dataworking["phrase_id"]
                            ):

                                good, message = savePhraseTranslation(
                                    self.request,
                                    dataworking["phrase_id"],
                                    dataworking["phrase_desc"],
                                    self.user.login,
                                    dataworking["lang_code"],
                                )

                                if good:
                                    response = Response(
                                        status=200,
                                        body=self._("Phrase successfully saved."),
                                    )
                                    return response
                                else:
                                    response = Response(
                                        status=401,
                                        body=self._("Error when modifying the phrase."),
                                    )
                                    return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._("There is no phrase with this ID."),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "The language could not be used because it is not included in their languages of use."
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
