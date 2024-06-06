from sqlalchemy.exc import IntegrityError
from climmob.models import (
    mapFromSchema,
    I18n,
    I18nUser,
    I18nQuestion,
    I18nQstoption,
    Question,
    mapToSchema,
)
from sqlalchemy import func

__all__ = [
    "getListOfLanguagesByUser",
    "getListOfUnusedLanguagesByUser",
    "addI18nUser",
    "modifyI18nUserDefaultLanguage",
    "deleteI18nUser",
    "query_languages",
    "languageExistInI18nUser",
]


def languageExistInI18nUser(language, userName, request):

    mappedData = mapFromSchema(
        request.dbsession.query(
            I18nUser,
        )
        .filter(I18nUser.user_name == userName)
        .filter(I18nUser.lang_code == language)
        .all()
    )

    if mappedData:
        return True

    return False


def getListOfLanguagesByUser(request, userName, questionId=None):
    print("Ingresa")
    if questionId:
        default = (
            request.dbsession.query(Question.question_lang)
            .filter(Question.question_id == questionId)
            .first()[0]
        )
    else:
        default = ""

    mappedData = mapFromSchema(
        request.dbsession.query(
            I18nUser,
            I18n,
            func.IF(default == I18nUser.lang_code, 1, 0).label("default"),
            (
                request.dbsession.query(func.count(Question.question_id))
                .filter(Question.user_name == userName)
                .filter(Question.question_lang == I18nUser.lang_code)
                .label("Question")
                + request.dbsession.query(func.count(I18nQuestion.lang_code))
                .filter(Question.user_name == userName)
                .filter(Question.question_id == I18nQuestion.question_id)
                .filter(I18nQuestion.lang_code == I18nUser.lang_code)
                .label("I18nQuestion")
                + request.dbsession.query(func.count(I18nQstoption.lang_code))
                .filter(Question.user_name == userName)
                .filter(Question.question_id == I18nQstoption.question_id)
                .filter(I18nQstoption.lang_code == I18nUser.lang_code)
                .label("I18nQstoption")
            ).label("used"),
        )
        .filter(I18nUser.lang_code == I18n.lang_code)
        .filter(I18nUser.user_name == userName)
        .order_by(I18nUser.lang_default.desc(), I18n.lang_name)
        .all()
    )
    return mappedData


def getListOfUnusedLanguagesByUser(request, userName):

    subquery = request.dbsession.query(I18nUser.lang_code).filter(
        I18nUser.user_name == userName
    )

    result = mapFromSchema(
        request.dbsession.query(I18n)
        .filter(I18n.lang_code.not_in(subquery))
        .order_by(I18n.lang_name)
        .all()
    )

    return result


def query_languages(request, userName, q, query_from, query_size):
    query = q.replace("*", "")

    subquery = request.dbsession.query(I18nUser.lang_code).filter(
        I18nUser.user_name == userName
    )

    total = (
        request.dbsession.query(I18n)
        .filter(I18n.lang_code.not_in(subquery))
        .filter(I18n.lang_name.ilike("%" + query + "%"))
        .order_by(I18n.lang_name)
        .all()
    )

    result = (
        request.dbsession.query(I18n)
        .filter(I18n.lang_code.not_in(subquery))
        .filter(I18n.lang_name.ilike("%" + query + "%"))
        .order_by(I18n.lang_name)
        .offset(query_from)
        .limit(query_size)
        .all()
    )

    return mapFromSchema(result), len(total)


def addI18nUser(data, request):
    mappedData = mapToSchema(I18nUser, data)
    newI18nUser = I18nUser(**mappedData)
    try:
        request.dbsession.add(newI18nUser)
        return True, ""
    except Exception as e:
        return False, str(e)


def modifyI18nUserDefaultLanguage(user, language, request):
    try:
        request.dbsession.query(I18nUser).filter(I18nUser.user_name == user).update(
            {"lang_default": 0}
        )

        request.dbsession.query(I18nUser).filter(I18nUser.user_name == user).filter(
            I18nUser.lang_code == language
        ).update({"lang_default": 1})
        return True, ""
    except Exception as e:
        return False, e


def deleteI18nUser(data, request):
    try:
        request.dbsession.query(I18nUser).filter(
            I18nUser.user_name == data["user_name"]
        ).filter(I18nUser.lang_code == data["lang_code"]).delete()
        return True, ""
    except IntegrityError as e:
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e
