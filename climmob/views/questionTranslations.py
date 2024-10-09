from climmob.views.classes import privateView, publicView
from pyramid.httpexceptions import HTTPNotFound
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
    # getListOfUnusedLanguagesByUser,
    query_languages,
    updateQuestion,
    deleteI18nQuestion,
    deleteAllI18nQstoption,
)
import paginate


class QuestionTranslationsView(privateView):
    def processView(self):
        userOwner = self.request.matchdict["user"]
        questionId = self.request.matchdict["questionid"]
        nextPage = self.request.params.get("next")

        if self.request.method == "POST":

            if userOwner != self.user.login:
                raise HTTPNotFound

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
            "nextPage": nextPage,
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


class APILanguagesView(publicView):
    def processView(self):

        userName = self.request.matchdict["user"]

        q = self.request.params.get("q", "")
        current_page = self.request.params.get("page")

        if q == "":
            q = None

        if current_page is None:
            current_page = 1

        query_size = 10
        if q is not None:
            q = q.lower()
            query_result, total = query_languages(
                self.request, userName, q, 0, query_size
            )
            if total > 0:
                collection = list(range(total))
                page = paginate.Page(collection, current_page, 10)
                query_result, total = query_languages(
                    self.request,
                    userName,
                    q,
                    page.first_item - 1,
                    query_size,
                )
                select2_result = []
                for result in query_result:
                    select2_result.append(
                        {
                            "id": "{}".format(result["lang_code"]),
                            "text": result["lang_name"],
                        }
                    )
                with_pagination = False
                if page.page_count > 1:
                    with_pagination = True

                if not with_pagination:
                    return {"total": total, "results": select2_result}
                else:
                    return {
                        "total": total,
                        "results": select2_result,
                        "pagination": {"more": True},
                    }
            else:
                return {"total": 0, "results": []}
        else:
            return {"total": 0, "results": []}


class ChangeDefaultQuestionLanguageView(privateView):
    def processView(self):
        userOwner = self.request.matchdict["user"]
        questionId = self.request.matchdict["questionid"]
        message = ""
        self.returnRawViewResult = True

        if self.request.method == "POST":

            if userOwner != self.user.login:
                return {
                    "status": 400,
                    "error": self._(
                        "You cannot change the main language of this question."
                    ),
                }

            postdata = self.getPostDict()

            formdata = {}
            formdata["user_name"] = userOwner
            formdata["question_id"] = questionId
            formdata["question_lang"] = postdata["lang_code"]
            formdata["lang_code"] = postdata["lang_code"]
            updt, message = updateQuestion(formdata, self.request)
            if updt:
                dlt, meesage = deleteI18nQuestion(formdata, self.request)
                if dlt:
                    opt, message = deleteAllI18nQstoption(formdata, self.request)
                    if opt:
                        return {"status": 200}

        return {"status": 400, "error": message}
