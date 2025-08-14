import json
import re
from datetime import datetime

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
    "get_sensitive_questions_anonymity_by_project_id",
    "anonymize_questions",
    "remove_anonymized_values_by_form_id",
]

from climmob.models.climmobv4 import AnonymizationParameter
from climmob.models.repository import sql_execute
from climmob.utility import (
    get_question_by_field_name,
    QuestionAnonymity,
    QuestionType,
    add_noise_to_gps_coordinates,
)

log = logging.getLogger(__name__)


def get_anonymization_params(question_id, request):
    result = mapFromSchema(
        request.dbsession.query(AnonymizationParameter)
        .filter(AnonymizationParameter.question_id == question_id)
        .all()
    )
    return result


def get_anonymization_params_as_dict(question_id, request):
    params = get_anonymization_params(question_id, request)
    result = {}
    for param in params:
        result[param["name"]] = param["value"]
    return result


def save_anonymization_params(question_id, data, request):
    delete_existing_anonymization_params(question_id, request)

    params = []
    for key in data.keys():
        pattern = r"anonym_param_([a-z_]+)"
        match = re.match(pattern, key)
        if match:
            params.append({"name": match.group(1), "value": data[key]})

    for param in params:
        new_param = AnonymizationParameter(**param)
        new_param.question_id = question_id
        request.dbsession.add(new_param)
        request.dbsession.flush()


def delete_existing_anonymization_params(question_id, request):
    try:
        request.dbsession.query(AnonymizationParameter).filter(
            AnonymizationParameter.question_id == question_id
        ).delete()
        return True, ""
    except Exception as e:
        return False, str(e)


def addQuestion(data, request):
    _ = request.translate
    mappeData = mapToSchema(Question, data)
    newQuestion = Question(**mappeData)
    save_point = request.tm.savepoint()
    try:
        request.dbsession.add(newQuestion)
        request.dbsession.flush()
        save_anonymization_params(newQuestion.question_id, data, request)
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
        save_anonymization_params(data["question_id"], data, request)
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

    if data["question_sensitive"]:
        params = (
            request.dbsession.query(
                AnonymizationParameter.name, AnonymizationParameter.value
            )
            .filter(AnonymizationParameter.question_id == data["question_id"])
            .all()
        )
        data.update(params)

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


def get_sensitive_questions_anonymity_by_project_id(project_id, request):
    """
    Retrieve all sensitive questions of a project by its id. Includes the registry and all the assessments.
    """
    query = (
        request.dbsession.query(
            Question.question_id,
            Question.question_dtype,
            Question.question_code,
            Question.question_anonymity,
        )
        .join(Registry, Registry.question_id == Question.question_id)
        .filter(Registry.project_id == project_id)
        .filter(Question.question_sensitive == 1)
        .union(
            request.dbsession.query(
                Question.question_id,
                Question.question_dtype,
                Question.question_code,
                Question.question_anonymity,
            )
            .join(AssDetail, AssDetail.question_id == Question.question_id)
            .filter(AssDetail.project_id == project_id)
            .filter(Question.question_sensitive == 1)
        )
    )
    return query.all()


def anonymize_questions(request, form, form_id, project_id, schema):
    questions = get_sensitive_questions_anonymity_by_project_id(project_id, request)

    registry_id = (
        form.get("grp_validation/clc_after", form["grp_1/QST162"])
        if form_id == "-"
        else form["grp_1/QST163"]
    )

    pattern = r"grp_\d+/(.+)"
    to_anonymize = []

    for key in form.keys():
        match = re.fullmatch(pattern, key)
        if not match:
            continue
        question = get_question_by_field_name(match.group(1), questions)
        if question and question.question_anonymity != QuestionAnonymity.REMOVE.value:
            to_anonymize.append(
                {"field_name": match.group(1), "value": form[key], "question": question}
            )

    if not to_anonymize:
        return True

    anonymized_values = []

    for field in to_anonymize:
        params = get_anonymization_params_as_dict(
            field["question"].question_id, request
        )
        if field["question"].question_anonymity == QuestionAnonymity.PSEUDONYM.value:
            field["value"] = params["pseudonym"].replace("{}", registry_id)
        elif field["question"].question_anonymity == QuestionAnonymity.RANGE.value:
            parser = (
                int
                if field["question"].question_dtype == QuestionType.INTEGER.value
                else float
            )
            field["value"] = parser(field["value"])
            params["lower_bound"] = parser(params["lower_bound"])
            params["upper_bound"] = parser(params["upper_bound"])
            params["interval"] = parser(params["interval"])

            if field["value"] < params["lower_bound"]:
                field["value"] = f'<{params["lower_bound"]}'
            elif field["value"] > params["upper_bound"]:
                field["value"] = f'>{params["upper_bound"]}'
            else:
                i = params["lower_bound"]
                while i < params["upper_bound"]:
                    if i <= field["value"] < (i + params["interval"]):
                        field["value"] = f'{i}-{i + params["interval"]}'
                    i += params["interval"]
        elif field["question"].question_anonymity == QuestionAnonymity.MONTH_YEAR.value:
            dt = datetime.fromisoformat(field["value"])
            field["value"] = dt.strftime("%Y-%m")
        elif field["question"].question_anonymity == QuestionAnonymity.NOISE.value:
            geo_point = field["value"].split()
            geo_point[0], geo_point[1] = add_noise_to_gps_coordinates(
                float(geo_point[0]), float(geo_point[1]), 3000
            )
            if geo_point[0] == "Error" or geo_point[1] == "Error":
                return False, "Could not anonymize GeoPoint"
            field["value"] = " ".join(geo_point)
        value = (
            f"("
            f"'{form_id}', "
            f"'{registry_id}', "
            f"'{field['field_name']}', "
            f"'{field['value']}'"
            f")"
        )
        anonymized_values.append(value)

    sql = f"INSERT INTO {schema}.anonymized VALUES {', '.join(anonymized_values)}"
    try:
        sql_execute(sql)
        return True, ""
    except Exception as e:
        match = re.search(rf"Duplicate entry '({form_id})-(\d+)-(.+?)'", str(e))
        if match:
            form_name = "registry" if form_id == "-" else f"assessment '{form_id}'"
            msg = f"Duplicate entry for package '{match.group(2)}' in {form_name}"
            return False, msg
        return False, ""


def remove_anonymized_values_by_form_id(schema, form_id):
    sql = f"DELETE FROM {schema}.anonymized where form_id='{form_id}'"
    sql_execute(sql)
