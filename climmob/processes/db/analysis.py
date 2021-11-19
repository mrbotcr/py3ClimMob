from climmob.models.schema import mapFromSchema, mapToSchema
from climmob.models import (
    AssDetail,
    Asssection,
    Assessment,
    Question,
    Regsection,
    Registry,
    I18nQuestion,
)
from .question import opcionOtherInQuestion
from climmob.processes.db.project import (
    numberOfCombinationsForTheProject,
    getProjectLabels,
)
from sqlalchemy import or_, func, and_
from jinja2 import Environment

__all__ = ["getQuestionsByType", "getQuestionsStructure"]


def getQuestionsByType(projectId, request):
    data = []

    dic = {}
    _assessments = []
    dic["Characteristics"] = []
    dic["Performance"] = []
    dic["Explanatory"] = []
    dic["Quantitative"] = []
    dic["linearRegression"] = []

    projectLabels = getProjectLabels(projectId, request)

    numComb = numberOfCombinationsForTheProject(projectId, request)

    sections = mapFromSchema(
        request.dbsession.query(Regsection)
        .filter(Regsection.project_id == projectId)
        .all()
    )
    for section in sections:

        questions = mapFromSchema(
            request.dbsession.query(Registry)
            .filter(Registry.project_id == projectId)
            .filter(Registry.section_id == section["section_id"])
            .all()
        )
        for question in questions:
            questionData = mapFromSchema(
                request.dbsession.query(
                    Question,
                    func.coalesce(
                        I18nQuestion.question_name, Question.question_name
                    ).label("question_name"),
                    func.coalesce(
                        I18nQuestion.question_desc, Question.question_desc
                    ).label("question_desc"),
                    func.coalesce(
                        I18nQuestion.question_posstm, Question.question_posstm
                    ).label("question_posstm"),
                    func.coalesce(
                        I18nQuestion.question_negstm, Question.question_negstm
                    ).label("question_negstm"),
                    func.coalesce(
                        I18nQuestion.question_perfstmt, Question.question_perfstmt
                    ).label("question_perfstmt"),
                )
                .join(
                    I18nQuestion,
                    and_(
                        Question.question_id == I18nQuestion.question_id,
                        I18nQuestion.lang_code == request.locale_name,
                    ),
                    isouter=True,
                )
                .filter(Question.question_id == question["question_id"])
                .first()
            )

            dictName, dictQues = addQuestionToDictionary(
                projectLabels, questionData, numComb
            )

            if dictName != "":
                dic[dictName].append(dictQues)

    # ASSESSMENTS
    assessments = mapFromSchema(
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(or_(Assessment.ass_status == 1, Assessment.ass_status == 2))
        .order_by(Assessment.ass_days)
        .all()
    )
    for assessment in assessments:
        _assessments.append(assessment)
        sections = mapFromSchema(
            request.dbsession.query(Asssection)
            .filter(Asssection.project_id == projectId)
            .filter(Asssection.ass_cod == assessment["ass_cod"])
            .order_by(Asssection.section_order)
            .all()
        )

        for section in sections:

            questions = mapFromSchema(
                request.dbsession.query(AssDetail)
                .filter(AssDetail.project_id == projectId)
                .filter(AssDetail.ass_cod == assessment["ass_cod"])
                .filter(AssDetail.section_id == section["section_id"])
                .order_by(AssDetail.question_order)
                .all()
            )
            for question in questions:

                questionData = mapFromSchema(
                    request.dbsession.query(
                        Question,
                        func.coalesce(
                            I18nQuestion.question_name, Question.question_name
                        ).label("question_name"),
                        func.coalesce(
                            I18nQuestion.question_desc, Question.question_desc
                        ).label("question_desc"),
                        func.coalesce(
                            I18nQuestion.question_posstm, Question.question_posstm
                        ).label("question_posstm"),
                        func.coalesce(
                            I18nQuestion.question_negstm, Question.question_negstm
                        ).label("question_negstm"),
                        func.coalesce(
                            I18nQuestion.question_perfstmt, Question.question_perfstmt
                        ).label("question_perfstmt"),
                    )
                    .join(
                        I18nQuestion,
                        and_(
                            Question.question_id == I18nQuestion.question_id,
                            I18nQuestion.lang_code == request.locale_name,
                        ),
                        isouter=True,
                    )
                    .filter(Question.question_id == question["question_id"])
                    .first()
                )

                dictName, dictQues = addQuestionToDictionary(
                    projectLabels, questionData, numComb, assessment
                )

                if dictName != "":
                    dic[dictName].append(dictQues)

    return dic, _assessments


def addQuestionToDictionary(projectLabels, questionData, numComb, assessment=None):

    questInfo = {}

    if assessment:
        code = "ASS" + assessment["ass_cod"]
        code2 = "ASS"
        extracode = assessment["ass_cod"]
    else:
        code = "REG"
        code2 = "REG"
        extracode = ""

    if questionData["question_quantitative"] == 1:

        if questionData["question_dtype"] not in [2, 3, 4, 5, 6]:
            return "", ""

        questInfo["name"] = questionData["question_name"]
        questInfo["codeQst"] = questionData["question_code"]
        questInfo["id"] = questionData["question_id"]
        questInfo["dtype"] = questionData["question_dtype"]
        questInfo["vars"] = []
        questInfo["code"] = assessment
        questInfo["questionAsked"] = []
        if questionData["question_dtype"] in [2, 3]:
            questInfo["type"] = "linearregression"
        else:
            questInfo["type"] = "quantitative"
        options = {
            1: "text",
            2: "decimal",
            3: "integer",
            4: "geopoint",
            5: "select_one",
            6: "select_multiple",
            7: "barcode",
            8: "select_one",
            9: "select_one",
            10: "select_one",
            11: "geotrace",
            12: "geoshape",
            13: "date",
            14: "time",
            15: "dateTime",
            16: "image",
            17: "audio",
            18: "video",
            19: "barcode",
            20: "start",
            21: "end",
            22: "today",
            23: "deviceid",
            24: "subscriberid",
            25: "simserial",
            26: "phonenumber",
            27: "text",
            28: "calculate",
            29: "note",
        }

        questInfo["class"] = options[questionData["question_dtype"]]

        for questionNumber in range(0, numComb):
            nameExtra = "_" + chr(65 + questionNumber).lower()
            descExtra = " - " + projectLabels[questionNumber]
            questInfo["vars"].append(
                code + "_" + questionData["question_code"] + nameExtra
            )
            questInfo["questionAsked"].append(questionData["question_desc"] + descExtra)

        questInfo["codeForAnalysis"] = (
            questInfo["type"]
            + "_"
            + code2
            + "_"
            + extracode
            + "_"
            + str(questInfo["id"])
            + "_add"
        )

        if questionData["question_dtype"] in [2, 3]:
            return "linearRegression", questInfo
        else:
            return "Quantitative", questInfo

    else:
        if questionData["question_dtype"] in [2, 3, 4, 5, 6]:
            questInfo["name"] = questionData["question_name"]
            questInfo["codeQst"] = questionData["question_code"]
            questInfo["questionAsked"] = questionData["question_desc"]
            questInfo["id"] = questionData["question_id"]
            questInfo["dtype"] = questionData["question_dtype"]
            questInfo["vars"] = code + "_" + questionData["question_code"].lower()
            questInfo["code"] = assessment
            questInfo["type"] = "explanatory"
            questInfo["codeForAnalysis"] = (
                questInfo["type"]
                + "_"
                + code2
                + "_"
                + extracode
                + "_"
                + str(questInfo["id"])
                + "_add"
            )
            return "Explanatory", questInfo

        if questionData["question_dtype"] == 9 or questionData["question_dtype"] == 10:

            questInfo["name"] = questionData["question_name"]
            questInfo["codeQst"] = questionData["question_code"]
            questInfo["id"] = questionData["question_id"]
            questInfo["vars"] = []
            questInfo["code"] = assessment
            questInfo["questionAsked"] = []

            if questionData["question_dtype"] == 9:
                questInfo["type"] = "characteristic"

                if numComb == 2:
                    varsData = {}
                    varsData["name"] = (
                        code + "_char_" + questionData["question_code"].lower()
                    )
                    questInfo["vars"].append(varsData)
                    questInfo["questionAsked"].append(questionData["question_twoitems"])

                if numComb == 3:
                    varsData = {}
                    # The possitive
                    varsData["name"] = (
                        code + "_char_" + questionData["question_code"].lower() + "_pos"
                    )
                    questInfo["vars"].append(varsData)
                    questInfo["questionAsked"].append(questionData["question_posstm"])

                    varsData = {}
                    # The negative
                    varsData["name"] = (
                        code + "_char_" + questionData["question_code"].lower() + "_neg"
                    )
                    questInfo["vars"].append(varsData)
                    questInfo["questionAsked"].append(questionData["question_negstm"])

                if numComb >= 4:
                    for opt in range(0, numComb):
                        varsData = {}
                        varsData["name"] = (
                            code
                            + "_char_"
                            + questionData["question_code"].lower()
                            + "_stmt_"
                            + str(opt + 1)
                        )
                        questInfo["vars"].append(varsData)
                        codeOption = chr(65 + opt)
                        renderedString = (
                            Environment()
                            .from_string(questionData["question_perfstmt"])
                            .render(option=codeOption)
                        )
                        questInfo["questionAsked"].append(renderedString)

                questInfo["codeForAnalysis"] = (
                    questInfo["type"]
                    + "_"
                    + code2
                    + "_"
                    + extracode
                    + "_"
                    + str(questInfo["id"])
                    + "_add"
                )
                return "Characteristics", questInfo

            if questionData["question_dtype"] == 10:
                questInfo["type"] = "performance"
                for opt in range(0, numComb):
                    varsData = {}
                    varsData["name"] = (
                        code
                        + "_perf_"
                        + questionData["question_code"].lower()
                        + "_"
                        + str(opt + 1)
                    )
                    questInfo["vars"].append(varsData)
                    codeOption = chr(65 + opt)
                    renderedString = (
                        Environment()
                        .from_string(questionData["question_perfstmt"])
                        .render(option=codeOption)
                    )
                    questInfo["questionAsked"].append(renderedString)

                questInfo["codeForAnalysis"] = (
                    questInfo["type"]
                    + "_"
                    + code2
                    + "_"
                    + extracode
                    + "_"
                    + str(questInfo["id"])
                    + "_add"
                )
                return "Performance", questInfo

    return "", ""


def getQuestionsStructure(projectId, ass_cod, request):
    data = []

    dic = []
    if ass_cod == "":
        sections = mapFromSchema(
            request.dbsession.query(Regsection)
            .filter(Regsection.project_id == projectId)
            .order_by(Regsection.section_order)
            .all()
        )
    else:
        sections = mapFromSchema(
            request.dbsession.query(Asssection)
            .filter(Asssection.project_id == projectId)
            .filter(Asssection.ass_cod == ass_cod)
            .order_by(Asssection.section_order)
            .all()
        )
    numComb = numberOfCombinationsForTheProject(projectId, request)

    for section in sections:
        if ass_cod == "":
            questions = mapFromSchema(
                request.dbsession.query(Registry)
                .filter(Registry.project_id == projectId)
                .filter(Registry.section_id == section["section_id"])
                .order_by(Registry.question_order)
                .all()
            )
        else:
            questions = mapFromSchema(
                request.dbsession.query(AssDetail)
                .filter(AssDetail.project_id == projectId)
                .filter(AssDetail.ass_cod == ass_cod)
                .filter(AssDetail.section_id == section["section_id"])
                .order_by(AssDetail.question_order)
                .all()
            )
        for question in questions:

            questionData = mapFromSchema(
                request.dbsession.query(
                    Question,
                    func.coalesce(
                        I18nQuestion.question_name, Question.question_name
                    ).label("question_name"),
                )
                .join(
                    I18nQuestion,
                    and_(
                        Question.question_id == I18nQuestion.question_id,
                        I18nQuestion.lang_code == request.locale_name,
                    ),
                    isouter=True,
                )
                .filter(Question.question_id == question["question_id"])
                .first()
            )

            questInfo = {}
            questInfo["name"] = questionData["question_name"]
            questInfo["id"] = questionData["question_id"]
            questInfo["vars"] = []

            if (
                questionData["question_dtype"] == 9
                or questionData["question_dtype"] == 10
            ):

                if questionData["question_dtype"] == 9:

                    if numComb == 2:
                        varsData = {}
                        varsData["name"] = "char_" + questionData["question_code"]
                        varsData["validation"] = ""
                        questInfo["vars"].append(varsData)

                    if numComb == 3:
                        varsData = {}
                        # The possitive
                        varsData["name"] = (
                            "char_" + questionData["question_code"] + "_pos"
                        )
                        varsData["validation"] = (
                            "char_" + questionData["question_code"] + "_neg"
                        )
                        questInfo["vars"].append(varsData)

                        varsData = {}
                        # The negative
                        varsData["name"] = (
                            "char_" + questionData["question_code"] + "_neg"
                        )
                        varsData["validation"] = (
                            "char_" + questionData["question_code"] + "_pos"
                        )
                        questInfo["vars"].append(varsData)

                    if numComb >= 4:
                        for opt in range(0, numComb):
                            # --------------#
                            validationString = ""
                            for optval in range(0, numComb):

                                if str(opt + 1) != str(optval + 1):
                                    validationString += (
                                        "char_"
                                        + questionData["question_code"]
                                        + "_stmt_"
                                        + str(optval + 1)
                                        + "*****"
                                    )
                            # --------------#
                            varsData = {}
                            varsData["name"] = (
                                "char_"
                                + questionData["question_code"]
                                + "_stmt_"
                                + str(opt + 1)
                            )
                            varsData["validation"] = validationString[
                                : len(validationString) - 5
                            ]
                            questInfo["vars"].append(varsData)

                    dic.append(questInfo)

                if questionData["question_dtype"] == 10:
                    for opt in range(0, numComb):
                        varsData = {}
                        varsData["name"] = (
                            "perf_" + questionData["question_code"] + "_" + str(opt + 1)
                        )
                        varsData["validation"] = ""
                        questInfo["vars"].append(varsData)

                    dic.append(questInfo)
            else:

                repeatQuestion = 1
                if questionData["question_quantitative"] == 1:
                    repeatQuestion = numComb

                for questionNumber in range(0, repeatQuestion):
                    nameExtra = ""
                    if questionData["question_quantitative"] == 1:
                        nameExtra = "_" + chr(65 + questionNumber).lower()

                    questInfo["vars"].append(
                        {
                            "name": questionData["question_code"] + nameExtra,
                            "validation": "",
                        }
                    )

                    if (
                        questionData["question_dtype"] == 5
                        or questionData["question_dtype"] == 6
                    ):
                        if opcionOtherInQuestion(questionData["question_id"], request):
                            questInfo["vars"].append(
                                {
                                    "name": questionData["question_code"]
                                    + nameExtra
                                    + "_oth",
                                    "validation": "",
                                }
                            )

                dic.append(questInfo)

    return dic
