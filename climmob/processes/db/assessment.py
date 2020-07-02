from sqlalchemy import func
from climmob.models.schema import mapFromSchema, mapToSchema
from ...models import AssDetail, Asssection, Assessment, Project, Question, Qstoption
from .project import (
    addQuestionsToAssessment,
    numberOfCombinationsForTheProject,
    getProjectLocalVariety,
)
from ..odk.generator import getRegisteredFarmers
import uuid, os
from subprocess import Popen, PIPE
import logging, shutil
from jinja2 import Environment

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
    "generateStructureForInterfaceAssessment",
    "generateStructureForValidateJsonOdkAssessment",
    "getAssessmentGroup",
    "getAssessmentQuestionsApi",
    "there_is_final_assessment",
    "is_assessment_final",
    "get_usable_assessments",
    "AsessmentStatus",
    "getAnalysisControl",
]

log = logging.getLogger(__name__)


def canDeleteTheAssessmentGroup(data, request):
    sql = (
        "select * from assdetail a, question q where a.user_name = '"
        + data["user_name"]
        + "' and a.project_cod='"
        + data["project_cod"]
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
        .filter(Asssection.user_name == data["user_name"])
        .filter(Asssection.project_cod == data["project_cod"])
        .filter(Asssection.section_id == data["group_cod"])
        .first()
    )

    if not result:
        return False
    else:
        return True


def projectAsessmentStatus(user, project, ass_cod, request):
    result = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user, Assessment.project_cod == project, Assessment.ass_cod == ass_cod)
        .first()
    )
    if result:
        if result.ass_status == 0:
            return True
        else:
            return False
    return False


def AsessmentStatus(user, project, assessment, request):
    result = (
        request.dbsession.query(Assessment)
        .filter(
            Assessment.user_name == user,
            Assessment.project_cod == project,
            Assessment.ass_cod == assessment,
        )
        .first()
    )
    if result.ass_status == 0:
        return True
    else:
        return False


def checkAssessments(user, project, assessment, request):
    if not is_assessment_final(request, user, project, assessment):
        return True, []

    localVariety = getProjectLocalVariety(user, project, request)
    errors = []
    sql = (
        "SELECT assdetail.question_id "
        "FROM assdetail,question "
        "WHERE assdetail.question_id = question.question_id "
        "AND assdetail.user_name = '" + user + "' "
        "AND assdetail.project_cod = '" + project + "' "
        "AND assdetail.ass_cod = '" + assessment + "' "
        "AND question.question_overall = 1"
    )
    data = request.dbsession.execute(sql).fetchone()
    if data is None:
        errors.append(
            {
                "error": "NoOverAllChar",
                "message": request.translate(
                    "An overall characteristic question is not part of the final assessments. You need to add this type of question to the assessment."
                ),
            }
        )

    if localVariety == 1:
        sql = (
            "SELECT assdetail.question_id "
            "FROM assdetail,question "
            "WHERE assdetail.question_id = question.question_id "
            "AND assdetail.user_name = '" + user + "' "
            "AND assdetail.project_cod = '" + project + "' "
            "AND assdetail.ass_cod = '" + assessment + "' "
            "AND question.question_overallperf = 1"
        )
        data = request.dbsession.execute(sql).fetchone()
        if data is None:
            errors.append(
                {
                    "error": "NoOverAllPerf",
                    "message": request.translate(
                        "An overall performance question is not part of the final assessments. You need to add this type of question to the assessment."
                    ),
                }
            )

    # sql = "SELECT assdetail.question_id " \
    #       "FROM assdetail,question " \
    #       "WHERE assdetail.question_id = question.question_id " \
    #       "AND assdetail.user_name = '" + user + "' " \
    #       "AND assdetail.project_cod = '" + project + "' " \
    #       "AND assdetail.ass_cod = '" + assessment + "' " \
    #       "AND question.question_dtype = 4"
    # data = request.dbsession.execute(sql).fetchone()
    # if data is None:
    #     errors.append({'error': "NoGeoLocation",'message': request.translate("A geolocation question is not part of the assessments. You need to add this type of question to the FIRST assessment.")})

    if errors:
        return False, errors
    else:
        return True, errors


def setAssessmentStatus(user, project, status, request):
    request.dbsession.query(Project).filter(Project.user_name == user).filter(
        Project.project_cod == project
    ).update({"project_assstatus": status})
    request.dbsession.query(Assessment).filter(Assessment.user_name == user).filter(
        Assessment.project_cod == project
    ).update({"ass_status": status})

    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .all()
    )
    if status == 0:
        for assessment in assessments:
            try:
                path = os.path.join(
                    request.registry.settings["user.repository"],
                    *[user, project, "data", "ass", assessment.ass_cod]
                )
                shutil.rmtree(path)
            except:
                pass


def setAssessmentIndividualStatus(user, project, assessment, status, request):
    request.dbsession.query(Assessment).filter(Assessment.user_name == user).filter(
        Assessment.project_cod == project
    ).filter(Assessment.ass_cod == assessment).update({"ass_status": status})


def there_is_final_assessment(request, user, project):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .filter(Assessment.ass_final == 1)
        .count()
    )
    if res == 0:
        return False
    else:
        return True


def is_assessment_final(request, user, project, assessment):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .filter(Assessment.ass_cod == assessment)
        .filter(Assessment.ass_final == 1)
        .count()
    )
    if res == 0:
        return False
    else:
        return True


def get_usable_assessments(request, user, project):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .filter(Assessment.ass_status == 0)
        .order_by(Assessment.ass_days.asc())
        .all()
    )
    res = mapFromSchema(res)
    return res


def getAnalysisControl(request, user, project):
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
        "and assdetail.user_name = '" + user + "' "
        "and assessment.project_cod = '" + project + "' "
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
        "and assdetail.user_name = '" + user + "' "
        "and assdetail.project_cod = '" + project + "' "
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


def getProjectAssessments(user, project, request):
    # print "****************************88"
    # print user
    # print project
    # print "****************************88"
    sql = (
        "SELECT assessment.ass_cod,assessment.ass_desc,assessment.ass_days,assessment.ass_status,assessment.ass_final,COUNT(assdetail.question_id) as totquestions "
        "FROM assessment LEFT JOIN assdetail "
        "ON assessment.user_name = assdetail.user_name "
        "AND assessment.project_cod = assdetail.project_cod "
        "AND assessment.ass_cod = assdetail.ass_cod "
        "WHERE assessment.user_name = '" + user + "' "
        "AND assessment.project_cod = '" + project + "' "
        "GROUP BY assessment.ass_cod,assessment.ass_desc,assessment.ass_days,assessment.ass_status,assessment.ass_final ORDER BY assessment.ass_days"
    )
    assessments = request.dbsession.execute(sql).fetchall()
    result = []
    for qst in assessments:
        dct = dict(qst)
        # for key, value in dct.iteritems():
        #    if isinstance(value, str):
        #        dct[key] = value.decode("utf8")
        result.append(dct)
    return result


def isAssessmentOpen(user, project, assessment, request):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .filter(Assessment.ass_cod == assessment)
        .first()
    )
    if res is not None:
        if res.ass_status == 1:
            return True
        else:
            return False
    else:
        return False


def assessmentExists(user, project, assessment, request):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .filter(Assessment.ass_cod == assessment)
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
            data["user_name"], data["project_cod"], id, request
        )
        if _from == "":
            return True, ""
        else:
            return (
                True,
                getProjectAssessmentInfo(
                    data["user_name"],
                    data["project_cod"],
                    newAssessment.ass_cod,
                    request,
                ),
            )
    except Exception as e:
        return False, e


def getProjectAssessmentInfo(user, project, assessment, request):
    data = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .filter(Assessment.ass_cod == assessment)
        .first()
    )
    return mapFromSchema(data)


def modifyProjectAssessment(data, request):
    try:
        mappeData = mapToSchema(Assessment, data)
        request.dbsession.query(Assessment).filter(
            Assessment.user_name == data["user_name"]
        ).filter(Assessment.project_cod == data["project_cod"]).filter(
            Assessment.ass_cod == data["ass_cod"]
        ).update(
            mappeData
        )
        return True, ""
    except Exception as e:
        return False, str(e)


def deleteProjectAssessment(user, project, assessment, request):
    try:
        request.dbsession.query(Assessment).filter(Assessment.user_name == user).filter(
            Assessment.project_cod == project
        ).filter(Assessment.ass_cod == assessment).delete()

        dropFile = os.path.join(
            request.registry.settings["user.repository"],
            *[user, project, "db", "ass", assessment, "drop.sql"]
        )
        # Drop the schema if the file exists
        if os.path.exists(dropFile):
            dropargs = []
            dropargs.append("mysql")
            dropargs.append("--defaults-file=" + request.registry.settings["mysql.cnf"])
            dropargs.append(user + "_" + project)

            with open(dropFile) as input_file:
                proc = Popen(dropargs, stdin=input_file, stderr=PIPE, stdout=PIPE)
                output, error = proc.communicate()
                if output != "" or error != "":
                    print("Error dropping database 1***")
                    msg = "Error dropping database \n"
                    msg = msg + "File: " + dropFile + "\n"
                    msg = msg + "Error: \n"
                    msg = msg + error + "\n"
                    msg = msg + "Output: \n"
                    msg = msg + output + "\n"
                    log.error(msg)

        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def availableAssessmentQuestions(user, project, assessment, request):

    sqlOverral = (
        "select question.question_id from assessment, assdetail, question where "
        "assdetail.question_id = question.question_id "
        "and assessment.ass_cod = assdetail.ass_cod "
        "and assdetail.user_name = '" + user + "' "
        "and assdetail.project_cod = '" + project + "' "
        "and (question_overallperf != 0 "
        "or question_overall != 0) "
    )

    sql = (
        "SELECT * FROM question WHERE (user_name = '"
        + user
        + "' OR user_name = 'bioversity') AND "
        "question.question_reqinreg = 0 AND question.question_alwaysinreg = 0 AND question.question_visible = 1 AND question_id NOT IN (SELECT distinct question_id "
        "FROM assdetail WHERE user_name = '"
        + user
        + "' AND project_cod = '"
        + project
        + "' AND ass_cod = '"
        + assessment
        + "')"
        "AND question_id NOT IN (" + sqlOverral + ")"
    )
    questions = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in questions:
        dct = dict(qst)
        # for key, value in dct.iteritems():
        #    if isinstance(value, str):
        #        dct[key] = value.decode("utf8")
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


def canUseTheQuestionAssessment(user, project, assessment, question_id, request):
    sql = (
        "SELECT * FROM question WHERE question_id = "
        + question_id
        + " AND question_id IN (SELECT question_id FROM question WHERE (user_name = '"
        + user
        + "' OR user_name = 'bioversity') AND "
        "question.question_reqinreg = 0 AND question.question_alwaysinreg = 0 AND question_id NOT IN (SELECT distinct question_id "
        "FROM assdetail WHERE user_name = '"
        + user
        + "' AND project_cod = '"
        + project
        + "' AND ass_cod = '"
        + assessment
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
        .filter(AssDetail.user_name == data["user_name"])
        .filter(AssDetail.project_cod == data["project_cod"])
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
            AssDetail.user_name == data["user_name"]
        ).filter(AssDetail.project_cod == data["project_cod"]).filter(
            AssDetail.question_id == data["question_id"]
        ).filter(
            AssDetail.section_id == data["group_cod"]
        ).filter(
            AssDetail.ass_cod == data["ass_cod"]
        ).delete()
        return True, ""
    except Exception as e:
        return False, e


def haveTheBasicStructureAssessment(user, project, assessment, request):
    hasSections = (
        request.dbsession.query(Asssection)
        .filter(Asssection.user_name == user)
        .filter(Asssection.project_cod == project)
        .filter(Asssection.ass_cod == assessment)
        .first()
    )
    if hasSections is None:
        addQuestionsToAssessment(user, project, assessment, request)


def getAssessmentQuestions(user, project, assessment, request):
    hasSections = (
        request.dbsession.query(Asssection)
        .filter(Asssection.user_name == user)
        .filter(Asssection.project_cod == project)
        .filter(Asssection.ass_cod == assessment)
        .first()
    )
    if hasSections is None:
        addQuestionsToAssessment(user, project, assessment, request)

    sql = (
        "SELECT asssection.section_id,asssection.section_name,asssection.section_content,asssection.section_order,asssection.section_color,"
        "question.question_id,question.question_desc,question.question_notes,question.question_dtype,IFNULL(assdetail.question_order,0) as question_order,"
        "question.question_reqinasses FROM asssection LEFT JOIN assdetail ON assdetail.section_user = asssection.user_name AND assdetail.section_project = asssection.project_cod "
        " AND assdetail.section_assessment = asssection.ass_cod AND assdetail.section_id = asssection.section_id "
        " LEFT JOIN question ON assdetail.question_id = question.question_id WHERE "
        "asssection.user_name = '"
        + user
        + "' AND asssection.project_cod = '"
        + project
        + "' AND asssection.ass_cod = '"
        + assessment
        + "' ORDER BY section_order,question_order"
    )
    questions = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in questions:
        dct = dict(qst)
        # for key, value in dct.iteritems():
        #    if isinstance(value, str):
        #        dct[key] = value.decode("utf8")
        result.append(dct)

    return result


def getAssessmentGroupInformation(user, project, assessment, section, request):
    data = (
        request.dbsession.query(Asssection)
        .filter(Asssection.user_name == user)
        .filter(Asssection.project_cod == project)
        .filter(Asssection.section_id == section)
        .filter(Asssection.ass_cod == assessment)
        .first()
    )
    return mapFromSchema(data)


def saveAssessmentOrder(user, project, assessment, order, request):

    # Delete all questions in the assessment
    request.dbsession.query(AssDetail).filter(AssDetail.user_name == user).filter(
        AssDetail.project_cod == project
    ).filter(AssDetail.ass_cod == assessment).delete()
    # Update the group order
    pos = 0
    for item in order:
        if item["type"] == "group":
            pos = pos + 1
            request.dbsession.query(Asssection).filter(
                Asssection.user_name == user
            ).filter(Asssection.project_cod == project).filter(
                Asssection.ass_cod == assessment
            ).filter(
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
                        user_name=user,
                        project_cod=project,
                        ass_cod=assessment,
                        question_id=child["id"].replace("QST", ""),
                        section_user=user,
                        section_project=project,
                        section_assessment=assessment,
                        section_id=item["id"].replace("GRP", ""),
                        question_order=pos,
                    )
                    request.dbsession.add(newQuestion)
        if item["type"] == "question":
            newQuestion = AssDetail(
                user_name=user,
                project_cod=project,
                ass_cod=assessment,
                question_id=item["id"],
                question_order=pos,
            )
            request.dbsession.add(newQuestion)
    request.dbsession.flush()
    return True, ""


def addAssessmentGroup(data, self, _from=""):
    result = (
        self.request.dbsession.query(func.count(Asssection.section_id).label("total"))
        .filter(Asssection.project_cod == data["project_cod"])
        .filter(Asssection.ass_cod == data["ass_cod"])
        .filter(Asssection.user_name == data["user_name"])
        .filter(Asssection.section_name == data["section_name"])
        .one()
    )
    if result.total <= 0:
        mappedData = mapToSchema(Asssection, data)
        max_id = (
            self.request.dbsession.query(
                func.ifnull(func.max(Asssection.section_id), 0).label("id_max")
            )
            .filter(Asssection.project_cod == data["project_cod"])
            .filter(Asssection.user_name == data["user_name"])
            .filter(Asssection.ass_cod == data["ass_cod"])
            .one()
        )
        max_order = (
            self.request.dbsession.query(
                func.ifnull(func.max(Asssection.section_order), 0).label("id_max")
            )
            .filter(Asssection.user_name == data["user_name"])
            .filter(Asssection.project_cod == data["project_cod"])
            .filter(Asssection.ass_cod == data["ass_cod"])
            .one()
        )
        mappedData["section_id"] = max_id.id_max + 1
        mappedData["section_order"] = max_order.id_max + 1
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
        .filter(Asssection.project_cod == data["project_cod"])
        .filter(Asssection.user_name == data["user_name"])
        .filter(Asssection.ass_cod == data["ass_cod"])
        .filter(Asssection.section_id != data["group_cod"])
        .filter(Asssection.section_name == data["section_name"])
        .one()
    )
    if result.total <= 0:
        try:
            mappedData = mapToSchema(Asssection, data)
            self.request.dbsession.query(Asssection).filter(
                Asssection.user_name == data["user_name"]
            ).filter(Asssection.project_cod == data["project_cod"]).filter(
                Asssection.ass_cod == data["ass_cod"]
            ).filter(
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
        .filter(Asssection.user_name == data["user_name"])
        .filter(Asssection.project_cod == data["project_cod"])
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
        .filter(AssDetail.user_name == data["user_name"])
        .filter(AssDetail.project_cod == data["project_cod"])
        .filter(AssDetail.ass_cod == data["ass_cod"])
        .filter(AssDetail.section_id == data["section_id"])
        .one()
    )
    newQuestion = AssDetail(
        user_name=data["user_name"],
        project_cod=data["project_cod"],
        ass_cod=data["ass_cod"],
        question_id=data["question_id"],
        section_user=data["user_name"],
        section_project=data["project_cod"],
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


def deleteAssessmentGroup(user, projectid, assid, sectionid, request):
    try:
        request.dbsession.query(Asssection).filter(Asssection.user_name == user).filter(
            Asssection.project_cod == projectid
        ).filter(Asssection.ass_cod == assid).filter(
            Asssection.section_id == sectionid
        ).delete()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def getAssesmentProgress(user, project, assessment, request):
    result = {}
    perc = 0
    arstatus = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .filter(Assessment.ass_cod == assessment)
        .first()
    )
    if arstatus.ass_status == 0:
        result["asssubmissions"] = 0
    else:
        assessment = (
            request.dbsession.query(Assessment)
            .filter(Assessment.user_name == user)
            .filter(Assessment.project_cod == project)
            .filter(Assessment.ass_cod == assessment)
            .first()
        )

        sql = (
            "SELECT COUNT(*) as total FROM "
            + user
            + "_"
            + project
            + ".ASS"
            + assessment.ass_cod
            + "_geninfo"
        )
        try:
            res = request.repsession.execute(sql).fetchone()
            totSubmissions = res["total"]
        except:
            totSubmissions = 0

        if totSubmissions > 0:
            sql = (
                "SELECT COUNT(*) as total FROM " + user + "_" + project + ".REG_geninfo"
            )
            try:
                res = request.repsession.execute(sql).fetchone()
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
                "SELECT COUNT(*) as total FROM " + user + "_" + project + ".REG_geninfo"
            )
            try:
                res = request.repsession.execute(sql).fetchone()
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


def generateStructureForInterfaceAssessment(user, project, ass_cod, request):

    data = []
    sections = mapFromSchema(
        request.dbsession.query(Asssection)
        .filter(Asssection.user_name == user)
        .filter(Asssection.project_cod == project)
        .filter(Asssection.ass_cod == ass_cod)
        .order_by(Asssection.section_order)
        .all()
    )
    numComb = numberOfCombinationsForTheProject(user, project, request)

    for section in sections:

        dataSection = {}
        dataSection["section_name"] = section["section_name"]
        dataSection["section_content"] = section["section_content"]
        dataSection["section_id"] = section["section_id"]
        dataSection["section_questions"] = []

        questions = mapFromSchema(
            request.dbsession.query(AssDetail)
            .filter(AssDetail.user_name == user)
            .filter(AssDetail.project_cod == project)
            .filter(AssDetail.ass_cod == ass_cod)
            .filter(AssDetail.section_id == section["section_id"])
            .order_by(AssDetail.question_order)
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
                # create the question
                dataQuestion = createQuestionAss(
                    questionData["question_id"],
                    questionData["question_desc"],
                    questionData["question_dtype"],
                    questionData["question_notes"],
                    questionData["question_unit"],
                    questionData["question_requiredvalue"],
                    questionData["question_code"],
                    "grp_"
                    + str(section["section_id"])
                    + "/"
                    + questionData["question_code"],
                )

                if questionData["question_dtype"] == 8:
                    dataFarmer = getRegisteredFarmers(user, project, request)
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

                dataSection["section_questions"].append(dataQuestion)
            else:

                if questionData["question_dtype"] == 9:

                    optionsReq = []
                    for opt in range(0, numComb):
                        code = chr(65 + opt)
                        dataQuestionop = createOption(
                            "Option " + code,
                            0,
                            str(opt + 1),
                            0,
                            str(opt + 1),
                            questionData["question_id"],
                        )
                        optionsReq.append(dataQuestionop)

                    if numComb == 2:
                        # the unique question
                        dataQuestion = createQuestionAss(
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
                        )
                        dataQuestion["question_options"] = optionsReq
                        dataSection["section_questions"].append(dataQuestion)

                    if numComb == 3:
                        # The possitive
                        dataQuestion = createQuestionAss(
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
                        )
                        dataQuestion["question_options"] = optionsReq
                        dataSection["section_questions"].append(dataQuestion)
                        # The negative
                        dataQuestion = createQuestionAss(
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
                            dataQuestion = createQuestionAss(
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
                            )
                            dataQuestion["question_options"] = optionsReq
                            dataSection["section_questions"].append(dataQuestion)

                if questionData["question_dtype"] == 10:
                    for opt in range(0, numComb):
                        code = chr(65 + opt)
                        renderedString = (
                            Environment()
                            .from_string(questionData["question_perfstmt"])
                            .render(option=code)
                        )
                        # create the question
                        dataQuestion = createQuestionAss(
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
                        )
                        # the best option
                        dataQuestionop = createOption(
                            request.translate("Better"),
                            0,
                            1,
                            0,
                            1,
                            questionData["question_id"],
                        )
                        dataQuestion["question_options"].append(dataQuestionop)
                        # the worst option
                        dataQuestionop = createOption(
                            request.translate("Worst"),
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
    necessarySection["section_content"] = request.translate(
        "Have necessary questions for documentation."
    )
    necessarySection["section_id"] = "None"
    necessarySection["section_questions"] = []
    # Start survey
    dataQuestion = createQuestionAss(
        "-1",
        request.translate("Start of survey"),
        15,
        request.translate("Start of survey"),
        "",
        1,
        "__CLMQST1__",
        "clm_start",
    )
    necessarySection["section_questions"].append(dataQuestion)
    # End survey
    dataQuestion = createQuestionAss(
        "-2",
        request.translate("End of survey"),
        15,
        request.translate("End of survey"),
        "",
        1,
        "__CLMQST2__",
        "clm_end",
    )
    necessarySection["section_questions"].append(dataQuestion)
    data.append(necessarySection)

    return data


def createQuestionAss(
    question_id,
    question_desc,
    question_dtype,
    question_notes,
    question_unit,
    question_requiredvalue,
    question_code,
    question_datafield,
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
    }
    ODKType = options[question_dtype]
    dataQuestion = {}
    dataQuestion["question_id"] = question_id
    dataQuestion["question_desc"] = question_desc
    dataQuestion["question_dtype"] = ODKType
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


def generateStructureForValidateJsonOdkAssessment(user, project, assessment, request):
    result = (
        request.dbsession.query(
            Asssection.section_id,
            Question.question_code,
            Question.question_dtype,
            Question.question_requiredvalue,
        )
        .filter(Asssection.user_name == user)
        .filter(Asssection.project_cod == project)
        .filter(Asssection.user_name == user)
        .filter(Asssection.ass_cod == assessment)
        .filter(AssDetail.project_cod == project)
        .filter(AssDetail.ass_cod == assessment)
        .filter(Asssection.section_id == AssDetail.section_id)
        .filter(AssDetail.question_id == Question.question_id)
        .all()
    )

    if result:
        return result
    else:
        return False


def getAssessmentGroup(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Asssection.section_id)
        .filter(Asssection.user_name == data["user_name"])
        .filter(Asssection.project_cod == data["project_cod"])
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
        .filter(AssDetail.user_name == data["user_name"])
        .filter(AssDetail.project_cod == data["project_cod"])
        .filter(AssDetail.ass_cod == data["ass_cod"])
        .all()
    )
    res = []

    for re in result:
        res.append(int(re.question_id))

    return res
