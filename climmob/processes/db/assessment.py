from sqlalchemy import func
from climmob.models.schema import mapFromSchema, mapToSchema
from climmob.models import (
    AssDetail,
    Asssection,
    Assessment,
    Project,
    Question,
    Qstoption,
    Regsection,
    Registry,
    userProject,
)
from climmob.processes.db.project import (
    addQuestionsToAssessment,
    numberOfCombinationsForTheProject,
    getProjectLocalVariety,
    getProjectData,
)
from climmob.processes.odk.generator import getRegisteredFarmers
import uuid, os
from subprocess import Popen, PIPE
import logging, shutil
from jinja2 import Environment
from climmob.processes.db.question import getQuestionOptions
from climmob.models.repository import sql_fetch_one

__all__ = [
    "availableAssessmentQuestions",
    "getAssessmentQuestions",
    "getAssessmentGroupInformation",
    "saveAssessmentOrder",
    "addAssessmentGroup",
    "modifyAssessmentGroup",
    "getAssessmentGroupData",
    "addAssessmentQuestionToGroup",
    "deleteAssessmentGroup",
    "getProjectAssessments",
    "addProjectAssessment",
    "modifyProjectAssessment",
    "getProjectAssessmentInfo",
    "deleteProjectAssessment",
    "isAssessmentOpen",
    "assessmentExists",
    "checkAssessments",
    "setAssessmentStatus",
    "setAssessmentIndividualStatus",
    "getAssesmentProgress",
    "projectAsessmentStatus",
    "haveTheBasicStructureAssessment",
    "exitsAssessmentGroup",
    "canDeleteTheAssessmentGroup",
    "canUseTheQuestionAssessment",
    "exitsQuestionInGroupAssessment",
    "deleteAssessmentQuestionFromGroup",
    "generateStructureForInterfaceForms",
    "getAssessmentGroup",
    "getAssessmentQuestionsApi",
    "there_is_final_assessment",
    "is_assessment_final",
    "get_usable_assessments",
    "getAnalysisControl",
    "getAllAssessmentGroups",
    "addProjectAssessmentClone",
    "getQuestionsByGroupInAssessment",
    "getTheGroupOfThePackageCodeAssessment",
    "formattingQuestions",
    "assessmentHaveQuestionOfMultimediaType",
    "deleteProjectAssessments",
]

log = logging.getLogger(__name__)


def deleteProjectAssessments(projectId, request):
    try:
        request.dbsession.query(Assessment).filter(
            Assessment.project_id == projectId
        ).delete()
        return True, ""
    except Exception as e:
        return False, e


def getTheGroupOfThePackageCodeAssessment(projectId, ass_cod, request):

    data = (
        request.dbsession.query(AssDetail.section_id)
        .filter(AssDetail.project_id == projectId)
        .filter(AssDetail.ass_cod == ass_cod)
        .filter(AssDetail.question_id == 163)
        .first()
    )
    return data[0]


def getQuestionsByGroupInAssessment(projectId, ass_cod, section_id, request):
    data = (
        request.dbsession.query(AssDetail)
        .filter(AssDetail.project_id == projectId)
        .filter(AssDetail.ass_cod == ass_cod)
        .filter(AssDetail.section_id == section_id)
        .order_by(AssDetail.question_order)
        .all()
    )
    return mapFromSchema(data)


def getAllAssessmentGroups(data, request):
    result = (
        request.dbsession.query(Asssection)
        .filter(Asssection.project_id == data["project_id"])
        .filter(Asssection.ass_cod == data["ass_cod"])
        .order_by(Asssection.section_id)
        .all()
    )
    return mapFromSchema(result)


def canDeleteTheAssessmentGroup(data, request):
    sql = (
        "select * from assdetail a, question q where a.project_id='"
        + data["project_id"]
        + "' and a.ass_cod = '"
        + data["ass_cod"]
        + "' and a.section_id = "
        + data["group_cod"]
        + " and a.question_id = q.question_id and q.question_reqinasses = 1;"
    )
    result = request.dbsession.execute(sql).fetchall()
    if not result:
        return True
    else:
        return False


def exitsAssessmentGroup(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Asssection)
        .filter(Asssection.project_id == data["project_id"])
        .filter(Asssection.section_id == data["group_cod"])
        .first()
    )

    if not result:
        return False
    else:
        return True


def projectAsessmentStatus(projectId, ass_cod, request):
    result = (
        request.dbsession.query(Assessment)
        .filter(
            Assessment.project_id == projectId,
            Assessment.ass_cod == ass_cod,
        )
        .first()
    )
    if result:
        if result.ass_status == 0:
            return True
        else:
            return False
    return False


def checkAssessments(projectId, assessment, request):
    _ = request.translate

    if not is_assessment_final(request, projectId, assessment):
        return True, {}

    localVariety = getProjectLocalVariety(projectId, request)
    errors = {}
    sql = (
        " SELECT assdetail.question_id "
        " FROM assdetail,question "
        " WHERE assdetail.question_id = question.question_id "
        " AND assdetail.project_id = '" + projectId + "' "
        " AND assdetail.ass_cod = '" + assessment + "' "
        " AND question.question_overall = 1"
    )

    data = request.dbsession.execute(sql).fetchone()
    if data is None:
        errors["NoOverAllChar"] = _(
            " 'Overrall ranking' question is not part of the final assessments. It is necessary to add this question from the ClimMob library to the assessment."
        )

    if localVariety == 1:
        sql = (
            " SELECT assdetail.question_id "
            " FROM assdetail,question "
            " WHERE assdetail.question_id = question.question_id "
            " AND assdetail.project_id = '" + projectId + "' "
            " AND assdetail.ass_cod = '" + assessment + "' "
            " AND question.question_overallperf = 1"
        )

        data = request.dbsession.execute(sql).fetchone()
        if data is None:
            errors["NoOverAllPerf"] = _(
                "'Comparison with current' question is not part of the final assessments. It is necessary to add this question from the ClimMob library to the assessment."
            )

    if errors:
        return False, errors
    else:
        return True, errors


def formattingQuestions(
    questions, request, projectLabels, onlyShowTheBasicQuestions=False
):
    _ = request.translate
    result = []
    for qst in questions:

        dct = dict(qst)
        options = []
        if dct["question_dtype"] == 5 or dct["question_dtype"] == 6:
            options = getQuestionOptions(dct["question_id"], request)
            dct["question_options"] = options

        if not onlyShowTheBasicQuestions:
            dct["isParentQuestion"] = 1
        result.append(dct)

        if not onlyShowTheBasicQuestions:
            if qst["question_quantitative"] == 0:
                isOther = False
                for option in options:
                    if option["value_isother"] == 1:
                        isOther = True

                if isOther:
                    newQuestion = dict(qst)
                    newQuestion["question_desc"] = newQuestion["question_desc"] + _(
                        " Other "
                    )
                    newQuestion["question_name"] = newQuestion["question_name"] + _(
                        " Other "
                    )
                    newQuestion["question_dtype"] = 1
                    newQuestion["question_requiredvalue"] = 0
                    newQuestion["isParentQuestion"] = 0

                    result.append(newQuestion)

        # We add the extra questions to the base dictionary but add the isParentQuestion flag, since this dictionary is used both in
        # the list of questions added to the project and to show the preview.
        # In the list you only have to see the single question, while in the preview you should see the questions by the number of packages.
        if not onlyShowTheBasicQuestions:
            if qst["question_quantitative"] == 1:
                for questionNumber in range(0, 3):
                    newQuestion = dict(qst)
                    descExtra = " - " + projectLabels[questionNumber]
                    newQuestion["question_desc"] = (
                        newQuestion["question_desc"] + descExtra
                    )
                    newQuestion["question_name"] = (
                        newQuestion["question_name"] + descExtra
                    )
                    options = []
                    if (
                        newQuestion["question_dtype"] == 5
                        or newQuestion["question_dtype"] == 6
                    ):
                        options = getQuestionOptions(
                            newQuestion["question_id"], request
                        )
                        newQuestion["question_options"] = options
                    newQuestion["isParentQuestion"] = 0
                    result.append(newQuestion)

                    isOther = False
                    for option in options:
                        if option["value_isother"] == 1:
                            isOther = True

                    if isOther:
                        newQuestion = dict(qst)
                        descExtra = " - " + projectLabels[questionNumber]
                        newQuestion["question_desc"] = (
                            newQuestion["question_desc"] + descExtra + _(" Other ")
                        )
                        newQuestion["question_name"] = (
                            newQuestion["question_name"] + descExtra + _(" Other ")
                        )
                        newQuestion["question_dtype"] = 1
                        newQuestion["question_requiredvalue"] = 0
                        newQuestion["isParentQuestion"] = 0
                        result.append(newQuestion)

    return result


def setAssessmentStatus(userOwner, projectCod, projectId, status, request):
    request.dbsession.query(Project).filter(Project.project_id == projectId).update(
        {"project_assstatus": status}
    )
    request.dbsession.query(Assessment).filter(
        Assessment.project_id == projectId
    ).update({"ass_status": status})

    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .all()
    )
    if status == 0:
        for assessment in assessments:
            try:
                path = os.path.join(
                    request.registry.settings["user.repository"],
                    *[userOwner, projectCod, "data", "ass", assessment.ass_cod]
                )
                shutil.rmtree(path)
            except:
                pass


def setAssessmentIndividualStatus(projectId, assessment, status, request):
    request.dbsession.query(Assessment).filter(
        Assessment.project_id == projectId
    ).filter(Assessment.ass_cod == assessment).update({"ass_status": status})


def there_is_final_assessment(request, projectId):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_final == 1)
        .count()
    )
    if res == 0:
        return False
    else:
        return True


def is_assessment_final(request, projectId, assessment):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessment)
        .filter(Assessment.ass_final == 1)
        .count()
    )
    if res == 0:
        return False
    else:
        return True


def get_usable_assessments(request, projectId):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_status == 0)
        .order_by(Assessment.ass_days.asc())
        .all()
    )
    res = mapFromSchema(res)
    return res


def getAnalysisControl(request, userSession, userName, projectId, projectCod):
    info = {}
    info["Characteristics"] = 0
    info["Performance"] = 0
    info["Explanatory"] = 0
    info["overralCharacteristic"] = ""
    info["overralPerformance"] = ""

    sql = (
        "SELECT count(question_dtype) as count, question_dtype FROM assessment,assdetail, question where "
        "assdetail.question_id = question.question_id "
        "and assessment.ass_cod = assdetail.ass_cod "
        "and (assessment.ass_status = 1 or assessment.ass_status = 2) "
        "and assdetail.project_id = assessment.project_id "
        "and assessment.project_id = '" + projectId + "' "
        "and question_overallperf = 0 "
        "and question_overall = 0 "
        "and question_dtype in (9,10,5) "
        "group by question_dtype"
    )

    data = request.dbsession.execute(sql).fetchall()
    for dat in data:
        if dat[1] == 9:
            info["Characteristics"] = dat[0]
        else:
            if dat[1] == 10:
                info["Performance"] = dat[0]
            else:
                if dat[1] == 5:
                    info["Explanatory"] = dat[0]

    sql = (
        "select ass_desc,question_dtype from assessment, assdetail, question where "
        "assdetail.question_id = question.question_id "
        "and assessment.ass_cod = assdetail.ass_cod "
        "and (assessment.ass_status = 1 or assessment.ass_status = 2) "
        "and assdetail.project_id = assessment.project_id "
        "and assdetail.project_id = '" + projectId + "' "
        "and (question_overallperf != 0 "
        "or question_overall != 0) "
    )

    data = request.dbsession.execute(sql).fetchall()
    for dat in data:
        if dat[1] == 9:
            info["overralCharacteristic"] = dat[0]
        else:
            if dat[1] == 10:
                info["overralPerformance"] = dat[0]

    return info


def getProjectAssessments(projectId, request):
    res = (
        request.dbsession.query(
            Assessment, func.count(AssDetail.question_id).label("totquestions")
        )
        .filter(Assessment.project_id == AssDetail.project_id)
        .filter(Assessment.ass_cod == AssDetail.ass_cod)
        .filter(Assessment.project_id == projectId)
        .group_by(
            Assessment.ass_cod,
            Assessment.ass_desc,
            Assessment.ass_days,
            Assessment.ass_status,
            Assessment.ass_final,
        )
        .order_by(Assessment.ass_days)
        .all()
    )
    result = mapFromSchema(res)

    return result


def isAssessmentOpen(projectId, assessmentId, request):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessmentId)
        .first()
    )
    if res is not None:
        if res.ass_status == 1:
            return True
        else:
            return False
    else:
        return False


def assessmentExists(projectId, assessmentId, request):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessmentId)
        .first()
    )
    if res is None:
        return False
    else:
        return True


def addProjectAssessment(data, request, _from=""):
    id = uuid.uuid4().hex[-12:]
    data["ass_cod"] = id
    mappedData = mapToSchema(Assessment, data)
    newAssessment = Assessment(**mappedData)
    try:
        request.dbsession.add(newAssessment)
        request.dbsession.flush()
        haveTheBasicStructureAssessment(
            data["userOwner"], data["project_id"], id, request
        )
        if _from == "":
            return True, ""
        else:
            return (
                True,
                getProjectAssessmentInfo(
                    data["project_id"],
                    newAssessment.ass_cod,
                    request,
                ),
            )
    except Exception as e:
        return False, e


def addProjectAssessmentClone(data, request):
    id = uuid.uuid4().hex[-12:]
    data["ass_cod"] = id
    mappedData = mapToSchema(Assessment, data)
    newAssessment = Assessment(**mappedData)
    try:
        request.dbsession.add(newAssessment)
        request.dbsession.flush()

        return True, data["ass_cod"]

    except Exception as e:
        return False, e


def getProjectAssessmentInfo(projectId, assessmentId, request):
    data = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessmentId)
        .first()
    )
    return mapFromSchema(data)


def modifyProjectAssessment(data, request):
    try:
        mappeData = mapToSchema(Assessment, data)
        request.dbsession.query(Assessment).filter(
            Assessment.project_id == data["project_id"]
        ).filter(Assessment.ass_cod == data["ass_cod"]).update(mappeData)
        return True, ""
    except Exception as e:
        return False, str(e)


def deleteProjectAssessment(userOwner, projectId, projectCod, assessment, request):
    try:
        request.dbsession.query(Assessment).filter(
            Assessment.project_id == projectId
        ).filter(Assessment.ass_cod == assessment).delete()
        dropFile = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "db", "ass", assessment, "drop.sql"]
        )
        # Drop the schema if the file exists
        if os.path.exists(dropFile):
            dropargs = []
            dropargs.append("mysql")
            dropargs.append("--defaults-file=" + request.registry.settings["mysql.cnf"])
            dropargs.append(userOwner + "_" + projectCod)

            with open(dropFile) as input_file:
                proc = Popen(dropargs, stdin=input_file, stderr=PIPE, stdout=PIPE)
                output, error = proc.communicate()
                output = output.decode("utf-8")
                error = error.decode("utf-8")
                if output != "" or error != "":
                    print("Error dropping database 1***")
                    msg = "Error dropping database \n"
                    msg = msg + "File: " + dropFile + "\n"
                    msg = msg + "Error: \n"
                    msg = msg + error + "\n"
                    msg = msg + "Output: \n"
                    msg = msg + output + "\n"
                    log.error(str(msg))

        return True, ""
    except Exception as e:
        return False, e


def availableAssessmentQuestions(projectId, assessment, request):
    projectCollaborators = (
        request.dbsession.query(userProject.user_name)
        .filter(userProject.project_id == projectId)
        .all()
    )

    stringForFilterQuestionByCollaborators = "question.user_name = 'bioversity'"
    if projectCollaborators:
        for user in projectCollaborators:
            stringForFilterQuestionByCollaborators += (
                " OR question.user_name='" + user[0] + "' "
            )

    sqlOverral = (
        "select question.question_id from assessment, assdetail, question where "
        "assdetail.question_id = question.question_id "
        "and assessment.ass_cod = assdetail.ass_cod "
        "and assdetail.project_id = '" + projectId + "' "
        "and (question_overallperf != 0 "
        "or question_overall != 0) "
    )

    sql = (
        "SELECT question.*, user.user_fullname, COALESCE(i18n_question.question_name, question.question_name) as question_name FROM user, question "
        " LEFT JOIN i18n_question ON question.question_id = i18n_question.question_id AND i18n_question.lang_code = '"
        + request.locale_name
        + "' "
        " WHERE (" + stringForFilterQuestionByCollaborators + ") AND "
        " question.question_reqinreg = 0 AND question.question_alwaysinreg = 0 AND question.question_visible = 1 AND question.question_id NOT IN (SELECT distinct question_id "
        " FROM assdetail WHERE project_id = '"
        + projectId
        + "' AND ass_cod = '"
        + assessment
        + "')"
        " AND question.question_id NOT IN (" + sqlOverral + ") AND"
        " question.user_name = user.user_name"
        " AND question.question_forms in (2,3)"
    )
    questions = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in questions:
        dct = dict(qst)
        ## Edited by Brandon
        if dct["question_dtype"] == 9:
            if (
                dct["question_posstm"] is not None
                and dct["question_negstm"] is not None
            ):
                result.append(dct)
        else:
            if dct["question_dtype"] == 10:
                if dct["question_perfstmt"] != None:
                    result.append(dct)
            else:
                if dct["question_dtype"] == 5 or dct["question_dtype"] == 6:
                    res = (
                        request.dbsession.query(Qstoption)
                        .filter(Qstoption.question_id == dct["question_id"])
                        .count()
                    )
                    if res > 0:
                        result.append(dct)
                else:
                    result.append(dct)
        ##

    return result


def canUseTheQuestionAssessment(user, projectId, assessmentId, question_id, request):
    sql = (
        "SELECT * FROM question WHERE question_id = "
        + question_id
        + " AND question_id IN (SELECT question_id FROM question WHERE (user_name = '"
        + user
        + "' OR user_name = 'bioversity') AND "
        "question.question_reqinreg = 0 AND question.question_alwaysinreg = 0 AND question_id NOT IN (SELECT distinct question_id "
        "FROM assdetail WHERE project_id = '"
        + projectId
        + "' AND ass_cod = '"
        + assessmentId
        + "'))"
    )

    result = request.dbsession.execute(sql).first()
    if result:
        return True
    else:
        return False


def exitsQuestionInGroupAssessment(data, request):
    result = (
        request.dbsession.query(AssDetail)
        .filter(AssDetail.project_id == data["project_id"])
        .filter(AssDetail.question_id == data["question_id"])
        .filter(AssDetail.section_id == data["group_cod"])
        .filter(AssDetail.ass_cod == data["ass_cod"])
        .first()
    )

    if result:
        return True
    else:
        return False


def deleteAssessmentQuestionFromGroup(data, request):
    try:
        request.dbsession.query(AssDetail).filter(
            AssDetail.project_id == data["project_id"]
        ).filter(AssDetail.question_id == data["question_id"]).filter(
            AssDetail.section_id == data["group_cod"]
        ).filter(
            AssDetail.ass_cod == data["ass_cod"]
        ).delete()
        return True, ""
    except Exception as e:
        return False, e


def haveTheBasicStructureAssessment(userOwner, projectId, assessmentId, request):
    hasSections = (
        request.dbsession.query(Asssection)
        .filter(Asssection.project_id == projectId)
        .filter(Asssection.ass_cod == assessmentId)
        .first()
    )
    if hasSections is None:
        addQuestionsToAssessment(userOwner, projectId, assessmentId, request)


def getAssessmentQuestions(
    userOwner,
    projectId,
    assessment,
    request,
    projectLabels,
    onlyShowTheBasicQuestions=False,
):
    hasSections = (
        request.dbsession.query(Asssection)
        .filter(Asssection.project_id == projectId)
        .filter(Asssection.ass_cod == assessment)
        .first()
    )
    if hasSections is None:
        addQuestionsToAssessment(userOwner, projectId, assessment, request)

    sql = (
        "SELECT asssection.section_id,asssection.section_name,asssection.section_content,asssection.section_order,asssection.section_private,"
        "question.question_id,COALESCE(i18n_question.question_desc,question.question_desc) as question_desc,COALESCE(i18n_question.question_name, question.question_name) as question_name,question.question_notes,question.question_dtype, "
        " COALESCE(i18n_question.question_posstm, question.question_posstm) as question_posstm, COALESCE(i18n_question.question_negstm ,question.question_negstm) as question_negstm, COALESCE(i18n_question.question_perfstmt, question.question_perfstmt) as question_perfstmt,IFNULL(assdetail.question_order,0) as question_order,"
        "question.question_reqinasses, question.question_tied, question.question_notobserved, question.question_requiredvalue, question.question_quantitative, question.user_name, (select user_fullname from user where user_name=question.user_name) as user_fullname FROM asssection LEFT JOIN assdetail ON assdetail.section_project_id = asssection.project_id "
        " AND assdetail.section_assessment = asssection.ass_cod AND assdetail.section_id = asssection.section_id "
        " LEFT JOIN i18n_question ON assdetail.question_id = i18n_question.question_id  AND i18n_question.lang_code = '"
        + request.locale_name
        + "'"
        " LEFT JOIN question ON assdetail.question_id = question.question_id WHERE "
        "asssection.project_id = '"
        + projectId
        + "' AND asssection.ass_cod = '"
        + assessment
        + "' ORDER BY section_order,question_order"
    )
    questions = request.dbsession.execute(sql).fetchall()

    result = formattingQuestions(
        questions,
        request,
        projectLabels,
        onlyShowTheBasicQuestions=onlyShowTheBasicQuestions,
    )

    return result


def getAssessmentGroupInformation(projectId, assessmentId, sectionId, request):
    data = (
        request.dbsession.query(Asssection)
        .filter(Asssection.project_id == projectId)
        .filter(Asssection.section_id == sectionId)
        .filter(Asssection.ass_cod == assessmentId)
        .first()
    )
    return mapFromSchema(data)


def saveAssessmentOrder(projectId, assessmentId, order, request):

    # Delete all questions in the assessment
    request.dbsession.query(AssDetail).filter(AssDetail.project_id == projectId).filter(
        AssDetail.ass_cod == assessmentId
    ).delete()
    # Update the group order
    pos = 0
    for item in order:
        if item["type"] == "group":
            pos = pos + 1
            request.dbsession.query(Asssection).filter(
                Asssection.project_id == projectId
            ).filter(Asssection.ass_cod == assessmentId).filter(
                Asssection.section_id == item["id"].replace("GRP", "")
            ).update(
                {"section_order": pos}
            )
    # Add question to the assessment
    pos = 0
    for item in order:
        if item["type"] == "group":
            if "children" in item.keys():
                for child in item["children"]:
                    pos = pos + 1
                    newQuestion = AssDetail(
                        ass_cod=assessmentId,
                        question_id=child["id"].replace("QST", ""),
                        section_assessment=assessmentId,
                        section_id=item["id"].replace("GRP", ""),
                        question_order=pos,
                        project_id=projectId,
                        section_project_id=projectId,
                    )
                    request.dbsession.add(newQuestion)
        if item["type"] == "question":
            newQuestion = AssDetail(
                ass_cod=assessmentId,
                question_id=item["id"],
                question_order=pos,
                project_id=projectId,
            )
            request.dbsession.add(newQuestion)
    request.dbsession.flush()
    return True, ""


def addAssessmentGroup(data, self, _from=""):
    result = (
        self.request.dbsession.query(func.count(Asssection.section_id).label("total"))
        .filter(Asssection.project_id == data["project_id"])
        .filter(Asssection.ass_cod == data["ass_cod"])
        .filter(Asssection.section_name == data["section_name"])
        .one()
    )
    if result.total <= 0:
        mappedData = mapToSchema(Asssection, data)
        max_id = (
            self.request.dbsession.query(
                func.ifnull(func.max(Asssection.section_id), 0).label("id_max")
            )
            .filter(Asssection.project_id == data["project_id"])
            .filter(Asssection.ass_cod == data["ass_cod"])
            .one()
        )
        max_order = (
            self.request.dbsession.query(
                func.ifnull(func.max(Asssection.section_order), 0).label("id_max")
            )
            .filter(Asssection.project_id == data["project_id"])
            .filter(Asssection.ass_cod == data["ass_cod"])
            .one()
        )
        if "section_id" not in data.keys():
            mappedData["section_id"] = max_id.id_max + 1
            mappedData["section_order"] = max_order.id_max + 1
        else:
            mappedData["section_id"] = data["section_id"]
            mappedData["section_order"] = data["section_order"]

        newGroup = Asssection(**mappedData)
        try:
            self.request.dbsession.add(newGroup)
            self.request.dbsession.flush()
            if _from == "":
                return True, ""
            else:
                data["group_cod"] = newGroup.section_id
                return True, getAssessmentGroupData(data, self)
        except Exception as e:
            return False, e
    else:
        return False, "repeated"


def modifyAssessmentGroup(data, self):
    result = (
        self.request.dbsession.query(func.count(Asssection.section_id).label("total"))
        .filter(Asssection.project_id == data["project_id"])
        .filter(Asssection.ass_cod == data["ass_cod"])
        .filter(Asssection.section_id != data["group_cod"])
        .filter(Asssection.section_name == data["section_name"])
        .one()
    )
    if result.total <= 0:
        try:
            mappedData = mapToSchema(Asssection, data)
            self.request.dbsession.query(Asssection).filter(
                Asssection.project_id == data["project_id"]
            ).filter(Asssection.ass_cod == data["ass_cod"]).filter(
                Asssection.section_id == data["group_cod"]
            ).update(
                mappedData
            )
            return True, ""
        except Exception as e:
            return False, e
    else:
        return False, "repeated"


def getAssessmentGroupData(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Asssection)
        .filter(Asssection.project_id == data["project_id"])
        .filter(Asssection.ass_cod == data["ass_cod"])
        .filter(Asssection.section_id == data["group_cod"])
        .one()
    )
    return mapFromSchema(result)


def addAssessmentQuestionToGroup(data, request):

    max_order = (
        request.dbsession.query(
            func.ifnull(func.max(AssDetail.question_order), 0).label("id_max")
        )
        .filter(AssDetail.project_id == data["project_id"])
        .filter(AssDetail.ass_cod == data["ass_cod"])
        .filter(AssDetail.section_id == data["section_id"])
        .one()
    )
    newQuestion = AssDetail(
        project_id=data["project_id"],
        ass_cod=data["ass_cod"],
        question_id=data["question_id"],
        section_project_id=data["project_id"],
        section_assessment=data["ass_cod"],
        section_id=data["section_id"],
        question_order=max_order.id_max + 1,
    )
    try:
        request.dbsession.add(newQuestion)
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def deleteAssessmentGroup(projectId, assId, sectionId, request):
    try:
        request.dbsession.query(Asssection).filter(
            Asssection.project_id == projectId
        ).filter(Asssection.ass_cod == assId).filter(
            Asssection.section_id == sectionId
        ).delete()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def getAssesmentProgress(userOwner, projectId, projectCod, assessment, request):
    result = {}
    perc = 0
    arstatus = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessment)
        .first()
    )
    if arstatus.ass_status == 0:
        result["asssubmissions"] = 0
    else:
        assessment = (
            request.dbsession.query(Assessment)
            .filter(Assessment.project_id == projectId)
            .filter(Assessment.ass_cod == assessment)
            .first()
        )

        sql = (
            "SELECT COUNT(*) as total FROM "
            + userOwner
            + "_"
            + projectCod
            + ".ASS"
            + assessment.ass_cod
            + "_geninfo"
        )
        try:
            res = sql_fetch_one(sql)
            totSubmissions = res["total"]
        except:
            totSubmissions = 0

        if totSubmissions > 0:
            sql = (
                "SELECT COUNT(*) as total FROM "
                + userOwner
                + "_"
                + projectCod
                + ".REG_geninfo"
            )
            try:
                res = sql_fetch_one(sql)
                submissions = res["total"]
            except:
                submissions = 0

            perc = (submissions * 100) / totSubmissions
            result = {
                "ass_cod": assessment.ass_cod,
                "ass_desc": assessment.ass_desc,
                "ass_status": assessment.ass_status,
                "asstotal": totSubmissions,
                "assperc": (submissions * 100) / totSubmissions,
                "submissions": submissions,
                "asssubmissions": arstatus.ass_status,
            }
        else:
            sql = (
                "SELECT COUNT(*) as total FROM "
                + userOwner
                + "_"
                + projectCod
                + ".REG_geninfo"
            )
            try:
                res = sql_fetch_one(sql)
                submissions = res["total"]
            except:
                submissions = 0

            perc = 0
            result = {
                "ass_cod": assessment.ass_cod,
                "ass_desc": assessment.ass_desc,
                "ass_status": assessment.ass_status,
                "asstotal": 0,
                "assperc": 0,
                "submissions": submissions,
                "asssubmissions": arstatus.ass_status,
            }

    return result, perc


def generateStructureForInterfaceForms(
    userOwner, projectId, projectCod, form, request, ass_cod=""
):
    _ = request.translate

    projectDetails = getProjectData(projectId, request)

    projectLabels = [
        projectDetails["project_label_a"],
        projectDetails["project_label_b"],
        projectDetails["project_label_c"],
    ]

    # print(projectLabels)

    data = []
    if form == "assessment":
        sections = mapFromSchema(
            request.dbsession.query(Asssection)
            .filter(Asssection.project_id == projectId)
            .filter(Asssection.ass_cod == ass_cod)
            .order_by(Asssection.section_order)
            .all()
        )
    else:
        sections = mapFromSchema(
            request.dbsession.query(Regsection)
            .filter(Regsection.project_id == projectId)
            .order_by(Regsection.section_order)
            .all()
        )
    numComb = numberOfCombinationsForTheProject(projectId, request)

    for section in sections:

        dataSection = {}
        dataSection["section_name"] = section["section_name"]
        dataSection["section_content"] = section["section_content"]
        dataSection["section_id"] = section["section_id"]
        dataSection["section_questions"] = []

        if form == "assessment":
            questions = mapFromSchema(
                request.dbsession.query(AssDetail)
                .filter(AssDetail.project_id == projectId)
                .filter(AssDetail.ass_cod == ass_cod)
                .filter(AssDetail.section_id == section["section_id"])
                .order_by(AssDetail.question_order)
                .all()
            )
        else:
            questions = mapFromSchema(
                request.dbsession.query(Registry)
                .filter(Registry.project_id == projectId)
                .filter(Registry.section_id == section["section_id"])
                .order_by(Registry.question_order)
                .all()
            )

        for question in questions:
            questionData = mapFromSchema(
                request.dbsession.query(Question)
                .filter(Question.question_id == question["question_id"])
                .first()
            )
            dataQuestion = {}
            if (
                questionData["question_dtype"] != 9
                and questionData["question_dtype"] != 10
            ):
                repeatQuestion = 1
                if questionData["question_quantitative"] == 1:
                    repeatQuestion = numComb

                for questionNumber in range(0, repeatQuestion):

                    nameExtra = ""
                    descExtra = ""
                    if questionData["question_quantitative"] == 1:
                        nameExtra = "_" + chr(65 + questionNumber).lower()
                        descExtra = " - " + projectLabels[questionNumber]

                    # create the question
                    dataQuestion = createQuestionForm(
                        questionData["question_id"],
                        questionData["question_desc"] + descExtra,
                        questionData["question_dtype"],
                        questionData["question_notes"],
                        questionData["question_unit"],
                        questionData["question_requiredvalue"],
                        questionData["question_code"] + nameExtra,
                        "grp_"
                        + str(section["section_id"])
                        + "/"
                        + questionData["question_code"]
                        + nameExtra,
                        questionData["question_dtype"],
                    )

                    if questionData["question_dtype"] == 8:
                        dataFarmer = getRegisteredFarmers(
                            userOwner, projectId, projectCod, request
                        )
                        for farmer in dataFarmer:
                            dataQuestion["question_options"].append(
                                createOption(
                                    farmer["farmer_name"],
                                    0,
                                    farmer["farmer_id"],
                                    0,
                                    farmer["farmer_id"],
                                    questionData["question_id"],
                                )
                            )

                    dataSection["section_questions"].append(dataQuestion)

                    if (
                        questionData["question_dtype"] == 5
                        or questionData["question_dtype"] == 6
                    ):
                        options = mapFromSchema(
                            request.dbsession.query(Qstoption)
                            .filter(Qstoption.question_id == question["question_id"])
                            .all()
                        )

                        for option in options:
                            dataQuestion["question_options"].append(option)
                            if option["value_isother"] == 1:
                                dataQuestion2 = createQuestionForm(
                                    questionData["question_id"],
                                    questionData["question_desc"]
                                    + descExtra
                                    + " "
                                    + _("Other"),
                                    1,
                                    "",
                                    "",
                                    0,
                                    questionData["question_code"] + nameExtra + "_oth",
                                    "grp_"
                                    + str(section["section_id"])
                                    + "/"
                                    + questionData["question_code"]
                                    + nameExtra
                                    + "_oth",
                                    questionData["question_dtype"],
                                )
                                dataSection["section_questions"].append(dataQuestion2)

            else:

                if questionData["question_dtype"] == 9:

                    optionsReq = []
                    for opt in range(0, numComb):
                        code = chr(65 + opt)
                        dataQuestionop = createOption(
                            projectLabels[opt],
                            0,
                            str(opt + 1),
                            0,
                            str(opt + 1),
                            questionData["question_id"],
                        )
                        optionsReq.append(dataQuestionop)

                    if questionData["question_tied"] == 1:
                        dataQuestionop = createOption(
                            "Tied",
                            0,
                            98,
                            0,
                            98,
                            questionData["question_id"],
                        )
                        optionsReq.append(dataQuestionop)

                    if questionData["question_notobserved"] == 1:
                        dataQuestionop = createOption(
                            "Not observed",
                            0,
                            99,
                            0,
                            99,
                            questionData["question_id"],
                        )
                        optionsReq.append(dataQuestionop)

                    if numComb == 2:
                        # the unique question
                        dataQuestion = createQuestionForm(
                            questionData["question_id"],
                            questionData["question_twoitems"],
                            5,
                            questionData["question_notes"],
                            questionData["question_unit"],
                            questionData["question_requiredvalue"],
                            questionData["question_code"],
                            "grp_"
                            + str(section["section_id"])
                            + "/char_"
                            + questionData["question_code"],
                            questionData["question_dtype"],
                        )
                        dataQuestion["question_options"] = optionsReq
                        dataSection["section_questions"].append(dataQuestion)

                    if numComb == 3:
                        # The possitive
                        dataQuestion = createQuestionForm(
                            questionData["question_id"],
                            questionData["question_posstm"],
                            5,
                            questionData["question_notes"],
                            questionData["question_unit"],
                            questionData["question_requiredvalue"],
                            questionData["question_code"],
                            "grp_"
                            + str(section["section_id"])
                            + "/char_"
                            + questionData["question_code"]
                            + "_pos",
                            questionData["question_dtype"],
                        )
                        dataQuestion["question_options"] = optionsReq
                        dataSection["section_questions"].append(dataQuestion)
                        # The negative
                        dataQuestion = createQuestionForm(
                            questionData["question_id"],
                            questionData["question_negstm"],
                            5,
                            questionData["question_notes"],
                            questionData["question_unit"],
                            questionData["question_requiredvalue"],
                            questionData["question_code"],
                            "grp_"
                            + str(section["section_id"])
                            + "/char_"
                            + questionData["question_code"]
                            + "_neg",
                            questionData["question_dtype"],
                        )
                        dataQuestion["question_options"] = optionsReq
                        dataSection["section_questions"].append(dataQuestion)

                    if numComb >= 4:

                        for opt in range(0, numComb):
                            renderedString = (
                                Environment()
                                .from_string(questionData["question_moreitems"])
                                .render(pos=opt + 1)
                            )
                            dataQuestion = createQuestionForm(
                                questionData["question_id"],
                                renderedString,
                                5,
                                questionData["question_notes"],
                                questionData["question_unit"],
                                questionData["question_requiredvalue"],
                                questionData["question_code"],
                                "grp_"
                                + str(section["section_id"])
                                + "/char_"
                                + questionData["question_code"]
                                + "_stmt_"
                                + str(opt + 1),
                                questionData["question_dtype"],
                            )
                            dataQuestion["question_options"] = optionsReq
                            dataSection["section_questions"].append(dataQuestion)

                if questionData["question_dtype"] == 10:
                    for opt in range(0, numComb):
                        code = chr(65 + opt)
                        renderedString = (
                            Environment()
                            .from_string(questionData["question_perfstmt"])
                            .render(option=projectLabels[opt])
                        )
                        # create the question
                        dataQuestion = createQuestionForm(
                            questionData["question_id"],
                            renderedString,
                            5,
                            questionData["question_notes"],
                            questionData["question_unit"],
                            questionData["question_requiredvalue"],
                            questionData["question_code"],
                            "grp_"
                            + str(section["section_id"])
                            + "/perf_"
                            + questionData["question_code"]
                            + "_"
                            + str(opt + 1),
                            questionData["question_dtype"],
                        )
                        # the best option
                        dataQuestionop = createOption(
                            _("Better"),
                            0,
                            1,
                            0,
                            1,
                            questionData["question_id"],
                        )
                        dataQuestion["question_options"].append(dataQuestionop)
                        # the worst option
                        dataQuestionop = createOption(
                            _("Worse"),
                            0,
                            2,
                            0,
                            2,
                            questionData["question_id"],
                        )
                        dataQuestion["question_options"].append(dataQuestionop)
                        # add to the section
                        dataSection["section_questions"].append(dataQuestion)

        data.append(dataSection)

    # Extra section for necessary questions in the json
    necessarySection = {}
    necessarySection["section_name"] = "Extra Field"
    necessarySection["section_content"] = _(
        "Have necessary questions for documentation."
    )
    necessarySection["section_id"] = "None"
    necessarySection["section_questions"] = []
    # Start survey
    dataQuestion = createQuestionForm(
        "-1",
        _("Start of survey"),
        15,
        _("Start of survey"),
        "",
        1,
        "__CLMQST1__",
        "clm_start",
        questionData["question_dtype"],
    )
    necessarySection["section_questions"].append(dataQuestion)
    # End survey
    dataQuestion = createQuestionForm(
        "-2",
        _("End of survey"),
        15,
        _("End of survey"),
        "",
        1,
        "__CLMQST2__",
        "clm_end",
        questionData["question_dtype"],
    )
    necessarySection["section_questions"].append(dataQuestion)
    data.append(necessarySection)

    return data


def createQuestionForm(
    question_id,
    question_desc,
    question_dtype,
    question_notes,
    question_unit,
    question_requiredvalue,
    question_code,
    question_datafield,
    question_dtype2,
):
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
    }
    ODKType = options[question_dtype]
    dataQuestion = {}
    dataQuestion["question_id"] = question_id
    dataQuestion["question_desc"] = question_desc
    dataQuestion["question_dtype"] = ODKType
    dataQuestion["question_dtype2"] = question_dtype2
    dataQuestion["question_notes"] = question_notes
    dataQuestion["question_unit"] = question_unit
    dataQuestion["question_requiredvalue"] = question_requiredvalue
    dataQuestion["question_code"] = question_code
    dataQuestion["question_datafield"] = question_datafield
    if ODKType == "select_one" or ODKType == "select_multiple":
        dataQuestion["question_options"] = []

    return dataQuestion


def createOption(
    value_desc, value_isother, value_code, value_isna, value_order, question_id
):
    dataQuestionop = {}
    dataQuestionop["value_desc"] = value_desc
    dataQuestionop["value_isother"] = value_isother
    dataQuestionop["value_code"] = value_code
    dataQuestionop["value_isna"] = value_isna
    dataQuestionop["value_order"] = value_order
    dataQuestionop["question_id"] = question_id

    return dataQuestionop


def getAssessmentGroup(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Asssection.section_id)
        .filter(Asssection.project_id == data["project_id"])
        .filter(Asssection.ass_cod == data["ass_cod"])
        .all()
    )
    res = []

    for re in result:
        res.append(int(re.section_id))

    return res


def getAssessmentQuestionsApi(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(AssDetail.question_id)
        .filter(AssDetail.project_id == data["project_id"])
        .filter(AssDetail.ass_cod == data["ass_cod"])
        .all()
    )
    res = []

    for re in result:
        res.append(int(re.question_id))

    return res


def assessmentHaveQuestionOfMultimediaType(request, projectId, ass_cod):

    result = (
        request.dbsession.query(func.count(AssDetail.question_id).label("count"))
        .filter(AssDetail.ass_cod == ass_cod)
        .filter(AssDetail.project_id == projectId)
        .filter(AssDetail.question_id == Question.question_id)
        .filter(Question.question_dtype.in_([16, 17, 18]))
        .one()
    )

    if result[0] > 0:
        return True
    else:
        return False
