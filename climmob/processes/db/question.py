import json

from sqlalchemy import func, or_, and_

from climmob.models import (
    Question,
    Registry,
    mapToSchema,
    mapFromSchema,
    Qstoption,
    AssDetail,
    I18nQuestion,
    I18nQstoption,
    I18n,
)
from sqlalchemy.exc import DatabaseError
import logging

__all__ = [
    "addQuestion",
    "addOptionToQuestion",
    "updateQuestion",
    "deleteAllOptionsForQuestion",
    "deleteQuestion",
    "UserQuestion",
    "QuestionsOptions",
    "getQuestionData",
    "getQuestionOptions",
    "getQuestionOptionsByQuestionCode",
    "deleteOption",
    "optionExists",
    "getOptionData",
    "updateOption",
    "questionExists",
    "UserQuestionMoreBioversity",
    "optionExistsWithName",
    "opcionNAinQuestion",
    "opcionOtherInQuestion",
    "userQuestionDetailsById",
    "getDefaultQuestionLanguage",
    "getQuestionOwner",
    "knowIfUserHasCreatedTranslations",
]

log = logging.getLogger(__name__)


def addQuestion(data, request):
    _ = request.translate
    mappeData = mapToSchema(Question, data)
    newQuestion = Question(**mappeData)
    save_point = request.tm.savepoint()
    try:
        request.dbsession.add(newQuestion)
        request.dbsession.flush()
        return True, newQuestion.question_id
    except DatabaseError as e:
        save_point.rollback()
        log.error("Error creating the question.")
        return False, _("Error creating the question. The question is very long")
    except Exception as e:
        save_point.rollback()
        log.error("Error {} while creating a question".format(str(e)))
        return False, str(e)


def getQuestionOwner(request, questionId):

    result = mapFromSchema(
        request.dbsession.query(Question.user_name)
        .filter(Question.question_id == questionId)
        .first()
    )
    if result:

        return result["user_name"]

    return ""


def questionExists(user, code, request):
    inlocal = (
        request.dbsession.query(Question)
        .filter(Question.user_name == user)
        .filter(Question.question_code == code)
        .first()
    )
    inglobal = (
        request.dbsession.query(Question)
        .filter(Question.user_name == "bioversity")
        .filter(Question.question_code == code)
        .first()
    )
    if inlocal is not None or inglobal is not None:
        return True
    return False


def addOptionToQuestion(data, request):
    mappeData = mapToSchema(Qstoption, data)
    max_id = request.dbsession.query(
        func.ifnull(func.max(Qstoption.value_order), 0).label("id_max")
    ).one()
    mappeData["value_order"] = max_id.id_max + 1
    newQstoption = Qstoption(**mappeData)
    try:
        request.dbsession.add(newQstoption)
        request.dbsession.flush()
        return True, ""
    except Exception as e:
        return False, str(e)


def updateOption(data, request):
    try:
        mappeData = mapToSchema(Qstoption, data)
        request.dbsession.query(Qstoption).filter(
            Qstoption.question_id == data["question_id"]
        ).filter(Qstoption.value_code == data["value_code"]).update(mappeData)
        return True, ""
    except Exception as e:
        return False, str(e)


def updateQuestion(data, request):
    _ = request.translate
    try:
        mappeData = mapToSchema(Question, data)
        request.dbsession.query(Question).filter(
            Question.user_name == data["user_name"]
        ).filter(Question.question_id == data["question_id"]).update(mappeData)
        return True, data["question_id"]
    except DatabaseError as e:
        log.error("Error creating the question. The question is very long")
        return False, _("Error creating the question. The question is very long")
    except Exception as e:
        return False, str(e)


def deleteOption(id_question, value, request):
    try:
        request.dbsession.query(Qstoption).filter(
            Qstoption.question_id == id_question
        ).filter(Qstoption.value_code == value).delete()
        return True, ""
    except Exception as e:
        return False, str(e)


def deleteAllOptionsForQuestion(id_question, request):
    try:
        request.dbsession.query(I18nQstoption).filter(
            I18nQstoption.question_id == id_question
        ).delete()
        request.dbsession.query(Qstoption).filter(
            Qstoption.question_id == id_question
        ).delete()
        return True, ""
    except Exception as e:
        return False, str(e)


def deleteQuestion(data, request):
    try:
        request.dbsession.query(I18nQstoption).filter(
            I18nQstoption.question_id == data["question_id"]
        ).delete()
        request.dbsession.query(I18nQuestion).filter(
            I18nQuestion.question_id == data["question_id"]
        ).delete()
        request.dbsession.query(Question).filter(
            Question.question_id == data["question_id"]
        ).delete()
        return True, ""
    except Exception as e:
        return False, str(e)


def UserQuestion(user, request):

    mappedData = mapFromSchema(
        request.dbsession.query(Question)
        .filter(Question.user_name == user)
        .filter(Question.question_visible == 1)
        .all()
    )
    result = []
    for data in mappedData:
        registry = (
            request.dbsession.query(func.count(Registry.question_id).label("found"))
            .filter(Registry.question_id == data["question_id"])
            .one()
        )
        assessment = (
            request.dbsession.query(func.count(AssDetail.question_id).label("found"))
            .filter(AssDetail.question_id == data["question_id"])
            .one()
        )
        data["assigned"] = assessment.found + registry.found
        if data["question_dtype"] == 5 or data["question_dtype"] == 6:
            options = getQuestionOptions(data["question_id"], request)
            data["num_options"] = len(options)
        result.append(data)
    return result


def UserQuestionMoreBioversity(user, request):

    query = (
        request.dbsession.query(
            Question,
            func.coalesce(I18nQuestion.question_desc, Question.question_desc).label(
                "question_desc"
            ),
            func.coalesce(I18nQuestion.question_name, Question.question_name).label(
                "question_name"
            ),
            func.coalesce(I18nQuestion.question_posstm, Question.question_posstm).label(
                "question_posstm"
            ),
            func.coalesce(I18nQuestion.question_negstm, Question.question_negstm).label(
                "question_negstm"
            ),
            func.coalesce(
                I18nQuestion.question_perfstmt, Question.question_perfstmt
            ).label("question_perfstmt"),
        )
        .join(
            I18nQuestion,
            and_(
                Question.question_id == I18nQuestion.question_id,
                I18nQuestion.lang_code == Question.question_lang,
            ),
            isouter=True,
        )
        .filter(or_(Question.user_name == user, Question.user_name == "bioversity"))
        .order_by(Question.user_name, Question.question_dtype)
    )

    if user != "bioversity":
        query = query.filter(Question.question_visible == 1)

    mappedData = mapFromSchema(query.all())

    result = []
    for data in mappedData:
        registry = (
            request.dbsession.query(func.count(Registry.question_id).label("found"))
            .filter(Registry.question_id == data["question_id"])
            .one()
        )
        assessment = (
            request.dbsession.query(func.count(AssDetail.question_id).label("found"))
            .filter(AssDetail.question_id == data["question_id"])
            .one()
        )
        data["assigned"] = assessment.found + registry.found
        if data["question_dtype"] == 5 or data["question_dtype"] == 6:
            options = getQuestionOptions(data["question_id"], request)
            data["num_options"] = len(options)
            data["question_options"] = json.dumps(options)

        result.append(data)
    return result


def userQuestionDetailsById(userOwner, questionId, request, language="default"):

    if language == "default":
        language = getDefaultQuestionLanguage(request, questionId)["question_lang"]

    data = mapFromSchema(
        request.dbsession.query(
            Question,
            func.coalesce(I18nQuestion.question_desc, Question.question_desc).label(
                "question_desc"
            ),
            func.coalesce(I18nQuestion.question_name, Question.question_name).label(
                "question_name"
            ),
            func.coalesce(I18nQuestion.question_posstm, Question.question_posstm).label(
                "question_posstm"
            ),
            func.coalesce(I18nQuestion.question_negstm, Question.question_negstm).label(
                "question_negstm"
            ),
            func.coalesce(
                I18nQuestion.question_perfstmt, Question.question_perfstmt
            ).label("question_perfstmt"),
        )
        .join(
            I18nQuestion,
            and_(
                Question.question_id == I18nQuestion.question_id,
                I18nQuestion.lang_code == language,
            ),
            isouter=True,
        )
        .filter(Question.user_name == userOwner)
        .filter(Question.question_id == questionId)
        .order_by(Question.user_name, Question.question_dtype)
        .one()
    )

    registry = (
        request.dbsession.query(func.count(Registry.question_id).label("found"))
        .filter(Registry.question_id == data["question_id"])
        .one()
    )
    assessment = (
        request.dbsession.query(func.count(AssDetail.question_id).label("found"))
        .filter(AssDetail.question_id == data["question_id"])
        .one()
    )

    if data and data["question_lang"]:
        i18n = mapFromSchema(
            request.dbsession.query(I18n)
            .filter(I18n.lang_code == data["question_lang"])
            .first()
        )
        data["lang_name"] = i18n["lang_name"]

    data["isIndividual"] = 1
    data["assigned"] = assessment.found + registry.found
    if data["question_dtype"] == 5 or data["question_dtype"] == 6:
        options = getQuestionOptions(data["question_id"], request, language=language)
        data["num_options"] = len(options)
        data["question_options"] = options

    return data


def QuestionsOptions(user, userOwner, request):
    subquery = (
        request.dbsession.query(Question.question_id)
        .filter(or_(Question.user_name == user, Question.user_name == userOwner))
        .filter(Question.question_dtype.in_([5, 6]))
    )
    result = mapFromSchema(
        request.dbsession.query(Qstoption)
        .filter(Qstoption.question_id.in_(subquery))
        .all()
    )
    return result


def getQuestionData(userOwner, questionId, request):
    questionData = mapFromSchema(
        request.dbsession.query(Question)
        .filter(Question.user_name == userOwner, Question.question_id == questionId)
        .first()
    )
    if questionData:
        registry = (
            request.dbsession.query(func.count(Registry.question_id).label("found"))
            .filter(Registry.question_id == questionId)
            .one()
        )
        assessment = (
            request.dbsession.query(func.count(AssDetail.question_id).label("found"))
            .filter(AssDetail.question_id == questionId)
            .one()
        )
        total = assessment.found + registry.found
        questionData["assigned"] = total

        if total == 0:
            editable = True
        else:
            editable = False
    else:
        questionData = mapFromSchema(
            request.dbsession.query(Question)
            .filter(
                Question.user_name == "bioversity", Question.question_id == questionId
            )
            .first()
        )
        editable = False
    return questionData, editable


def getOptionData(question, value, request):
    questionData = mapFromSchema(
        request.dbsession.query(Qstoption)
        .filter(Qstoption.question_id == question)
        .filter(Qstoption.value_code == value)
        .first()
    )
    return questionData


def getQuestionOptions(question, request, language="default"):

    if language == "default":
        language = getDefaultQuestionLanguage(request, question)["question_lang"]

    return mapFromSchema(
        request.dbsession.query(
            Qstoption,
            func.coalesce(I18nQstoption.value_desc, Qstoption.value_desc).label(
                "value_desc"
            ),
        )
        .join(
            I18nQstoption,
            and_(
                Qstoption.question_id == I18nQstoption.question_id,
                Qstoption.value_code == I18nQstoption.value_code,
                I18nQstoption.lang_code == language,
            ),
            isouter=True,
        )
        .filter(Qstoption.question_id == question)
        .order_by(Qstoption.value_order)
        .all()
    )


def getQuestionOptionsByQuestionCode(question_code, projectId, form, request):
    print("_______________")
    print(
        "ESTE ESTA COMPLICADO PORQUE DIFERENTES USUARIOS PUEDEN TENER EL MISMO QUESTION_CODE"
    )
    print("_______________")
    print(question_code)
    print(form)
    print(projectId)
    if form == "reg":

        return mapFromSchema(
            request.dbsession.query(Qstoption)
            .filter(Question.question_code == question_code)
            .filter(Qstoption.question_id == Question.question_id)
            .filter(Question.question_id == Registry.question_id)
            .filter(Registry.project_id == projectId)
            .order_by(Qstoption.value_order)
            .all()
        )


def optionExists(question, option, request):
    res = (
        request.dbsession.query(Qstoption)
        .filter(Qstoption.question_id == question)
        .filter(Qstoption.value_code == option)
        .first()
    )
    if res is None:
        return False
    return True


def optionExistsWithName(question, option, request):
    res = (
        request.dbsession.query(Qstoption)
        .filter(Qstoption.question_id == question)
        .filter(Qstoption.value_desc == option)
        .first()
    )
    if res is None:
        return False
    return True


def opcionNAinQuestion(question, request):
    res = (
        request.dbsession.query(Qstoption)
        .filter(Qstoption.question_id == question)
        .filter(Qstoption.value_isna == 1)
        .all()
    )
    if res:
        return True
    return False


def opcionOtherInQuestion(question, request):
    res = (
        request.dbsession.query(Qstoption)
        .filter(Qstoption.question_id == question)
        .filter(Qstoption.value_isother == 1)
        .all()
    )
    if res:
        return True
    return False


def getDefaultQuestionLanguage(request, questionId):

    return mapFromSchema(
        request.dbsession.query(Question.question_lang)
        .filter(Question.question_id == questionId)
        .first()
    )


def knowIfUserHasCreatedTranslations(request, userId):

    userQuestionsId = request.dbsession.query(Question.question_id).filter(
        Question.user_name == userId
    )

    translations = (
        request.dbsession.query(I18nQuestion)
        .filter(I18nQuestion.question_id.in_(userQuestionsId))
        .all()
    )

    if translations:

        return True

    return False
