from sqlalchemy.exc import IntegrityError
from climmob.models import (
    mapFromSchema,
    I18n,
    I18nQuestion,
    I18nQstoption,
    Question,
    mapToSchema,
)
from climmob.models.schema import getDictionaryOfModel
from climmob.processes.db.i18n_user import getListOfLanguagesByUser

__all__ = [
    "getQuestionTranslation",
    "getTranslationByLanguage",
    "addI18nQuestion",
    "modifyI18nQuestion",
    "getAllTranslationsOfQuestion",
    "deleteI18nQuestion",
    "getFieldTranslationByLanguage",
]


def getQuestionTranslation(request, questionId, langCode):
    mappedData = mapFromSchema(
        request.dbsession.query(I18nQuestion)
        .filter(I18nQuestion.question_id == questionId)
        .filter(I18nQuestion.lang_code == langCode)
        .first()
    )
    if not mappedData:

        mappedData = mapFromSchema(
            request.dbsession.query(Question)
            .filter(Question.question_id == questionId)
            .filter(Question.question_lang == langCode)
            .first()
        )
        if not mappedData:
            mappedData = getDictionaryOfModel(I18nQuestion)

    mappedData["question_options"] = mapFromSchema(
        request.dbsession.query(I18nQstoption)
        .filter(I18nQstoption.question_id == questionId)
        .filter(I18nQstoption.lang_code == langCode)
        .all()
    )

    return mappedData


def getAllTranslationsOfQuestion(request, userName, questionId):

    languages = getListOfLanguagesByUser(request, userName, questionId)

    for lang in languages:
        lang["translations"] = getQuestionTranslation(
            request, questionId, lang["lang_code"]
        )

    return languages


def getTranslationByLanguage(request, questionId, langCode):

    return mapFromSchema(
        request.dbsession.query(I18nQuestion)
        .filter(I18nQuestion.question_id == questionId)
        .filter(I18nQuestion.lang_code == langCode)
        .first()
    )


def getFieldTranslationByLanguage(request, questionId, langCode, field):

    sql = (
        "SELECT COALESCE(i.{},q.{}) as {} "
        "FROM question q "
        " LEFT JOIN i18n_question i "
        " ON        q.question_id = i.question_id "
        " AND       i.lang_code = '{}' "
        " WHERE q.question_id = {} "
    ).format(field, field, field, langCode, questionId)

    result = request.dbsession.execute(sql).fetchall()

    if result:

        return True, result[0][field]

    return False, ""


def addI18nQuestion(data, request):
    mappedData = mapToSchema(I18nQuestion, data)
    newI18nQuestion = I18nQuestion(**mappedData)
    try:
        request.dbsession.add(newI18nQuestion)
        return True, data["question_id"]
    except Exception as e:
        return False, str(e)


def modifyI18nQuestion(questionId, data, request):
    mappedData = mapToSchema(I18nQuestion, data)
    try:
        request.dbsession.query(I18nQuestion).filter(
            I18nQuestion.question_id == questionId
        ).filter(I18nQuestion.lang_code == data["lang_code"]).update(mappedData)
        return True, data["question_id"]
    except Exception as e:
        return False, e


def deleteI18nQuestion(data, request):
    try:
        request.dbsession.query(I18nQuestion).filter(
            I18nQuestion.question_id == data["question_id"]
        ).filter(I18nQuestion.lang_code == data["lang_code"]).delete()
        return True, ""
    except IntegrityError as e:
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e
