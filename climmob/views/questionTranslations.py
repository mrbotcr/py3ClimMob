from climmob.views.classes import privateView
from climmob.processes import (
    userQuestionDetailsById,
    getListOfLanguagesByUser,
    getTranslationByLanguage,
    addI18nQuestion,
    modifyI18nQuestion,
    deleteI18nQuestion,
    getAllTranslationsOfQuestion,
    getTranslationQuestionOptionByLanguage,
    addI18nQstoption,
    modifyI18nQstoption,
    deleteI18nQstoption,
)


class questionTranslations_view(privateView):
    def processView(self):
        userOwner = self.request.matchdict["user"]
        questionId = self.request.matchdict["questionid"]

        if self.request.method == "POST":
            postdata = self.getPostDict()

            languages = getListOfLanguagesByUser(self.request, userOwner, questionId)

            for lang in languages:
                info = {}
                info["question_id"] = questionId
                info["lang_code"] = lang["lang_code"]
                info["user_name"] = self.user.login
                if lang["default"] != 1:
                    # print(lang["lang_code"])
                    for key in postdata.keys():
                        try:
                            keyS = key.split("_")
                            if keyS[2] == lang["lang_code"]:
                                info[keyS[0] + "_" + keyS[1]] = postdata[key]
                        except:
                            va = ""

                    result = actionInTheTranslationOfQuestion(self, info)

                    questionOptions = []
                    for key in postdata.keys():
                        info = {}
                        info["question_id"] = questionId
                        info["lang_code"] = lang["lang_code"]
                        try:
                            keyS = key.split("_")
                            if keyS[3] == lang["lang_code"]:
                                info["value_code"] = keyS[2]
                                info["value_desc"] = postdata[key]
                                questionOptions.append(info)
                        except:
                            va = ""

                    result = actionInTheTranslationOfQuestionOptions(
                        self, questionOptions
                    )

        question = userQuestionDetailsById(userOwner, questionId, self.request)

        return {
            "questionDetails": question,
            "translations": getAllTranslationsOfQuestion(
                self.request, userOwner, questionId
            ),
        }


def actionInTheTranslationOfQuestion(self, formdata):

    isThereTranslationInThisLanguage = getTranslationByLanguage(
        self.request, formdata["question_id"], formdata["lang_code"]
    )

    if (
        formdata.get("question_desc", "") != ""
        or formdata.get("question_notes", "") != ""
        or formdata.get("question_unit", "") != ""
        or formdata.get("question_posstm", "") != ""
        or formdata.get("question_nrgstm", "") != ""
        or formdata.get("question_perfstmt", "") != ""
        or formdata.get("question_name", "") != ""
    ):
        if isThereTranslationInThisLanguage:
            # print("Ya existe la traducción")
            # print("Es update")
            updated, idorerror = modifyI18nQuestion(
                formdata["question_id"], formdata, self.request
            )

            if not updated:
                return {"result": "error", "error": idorerror}
            else:
                self.request.session.flash(
                    self._("The translate was successfully modified")
                )

                return {
                    "question_id": formdata["question_id"],
                    "user_name": formdata["user_name"],
                    "result": "success",
                    "success": self._("The translate was successfully modified"),
                }

        else:
            # print("No existe la traducción")
            # print("Es insert")

            add, idorerror = addI18nQuestion(formdata, self.request)

            if not add:
                return {"result": "error", "error": idorerror}
            else:
                self.request.session.flash(
                    self._("The question was successfully translated")
                )

                return {
                    "question_id": formdata["question_id"],
                    "user_name": formdata["user_name"],
                    "result": "success",
                    "success": self._("The question was successfully translated"),
                }
    else:
        if isThereTranslationInThisLanguage:

            deleted, message = deleteI18nQuestion(formdata, self.request)


def actionInTheTranslationOfQuestionOptions(self, formdata):

    for option in formdata:

        isThereTranslation = getTranslationQuestionOptionByLanguage(
            self.request,
            option["question_id"],
            option["lang_code"],
            option["value_code"],
        )
        if option.get("value_desc", "") != "":
            if isThereTranslation:
                updated, idorerror = modifyI18nQstoption(option, self.request)
            else:
                add, idorerror = addI18nQstoption(option, self.request)
        else:
            if isThereTranslation:
                deleted, message = deleteI18nQstoption(option, self.request)
    return {}
