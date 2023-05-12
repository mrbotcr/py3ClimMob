from sqlalchemy.exc import IntegrityError
from climmob.models import mapFromSchema, I18nQstoption, mapToSchema

__all__ = [
    "getTranslationQuestionOptionByLanguage",
    "getFieldTranslationQuestionOptionByLanguage",
    "addI18nQstoption",
    "modifyI18nQstoption",
    "deleteI18nQstoption",
    "deleteAllI18nQstoption",
]


def getTranslationQuestionOptionByLanguage(request, questionId, langCode, valueCode):

    return mapFromSchema(
        request.dbsession.query(I18nQstoption)
        .filter(I18nQstoption.question_id == questionId)
        .filter(I18nQstoption.lang_code == langCode)
        .filter(I18nQstoption.value_code == valueCode)
        .first()
    )


def getFieldTranslationQuestionOptionByLanguage(
    request, questionId, langCode, valueCode
):

    sql = (
        "SELECT COALESCE(i.{},q.{}) as {} "
        "FROM qstoption q "
        " LEFT JOIN i18n_qstoption i "
        " ON        q.question_id = i.question_id "
        " AND  q.value_code = i.value_code "
        " AND       i.lang_code = '{}' "
        " WHERE q.question_id = {} "
        " AND q.value_code = {}"
    ).format("value_desc", "value_desc", "value_desc", langCode, questionId, valueCode)
    result = request.dbsession.execute(sql).fetchall()
    if result:

        return True, result[0]["value_desc"]

    return False, ""


def addI18nQstoption(data, request):
    mappedData = mapToSchema(I18nQstoption, data)
    newI18nQstoption = I18nQstoption(**mappedData)
    try:
        request.dbsession.add(newI18nQstoption)
        return True, data["question_id"]
    except Exception as e:
        return False, str(e)


def modifyI18nQstoption(data, request):
    mappedData = mapToSchema(I18nQstoption, data)
    try:
        request.dbsession.query(I18nQstoption).filter(
            I18nQstoption.question_id == data["question_id"]
        ).filter(I18nQstoption.lang_code == data["lang_code"]).filter(
            I18nQstoption.value_code == data["value_code"]
        ).update(
            mappedData
        )
        return True, data["question_id"]
    except Exception as e:
        return False, e


def deleteI18nQstoption(data, request):
    try:
        request.dbsession.query(I18nQstoption).filter(
            I18nQstoption.question_id == data["question_id"]
        ).filter(I18nQstoption.lang_code == data["lang_code"]).filter(
            I18nQstoption.value_code == data["value_code"]
        ).filter(
            I18nQstoption.lang_code == data["lang_code"]
        ).delete()
        return True, ""
    except IntegrityError as e:
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e


def deleteAllI18nQstoption(data, request):
    try:
        request.dbsession.query(I18nQstoption).filter(
            I18nQstoption.question_id == data["question_id"]
        ).filter(I18nQstoption.lang_code == data["lang_code"]).delete()
        return True, ""
    except IntegrityError as e:
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e
