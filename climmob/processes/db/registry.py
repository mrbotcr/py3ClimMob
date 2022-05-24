from sqlalchemy import func
from climmob.models.schema import mapFromSchema, mapToSchema
from climmob.models import Regsection, Registry, Project, Question, userProject
from climmob.processes import addRegistryQuestionsToProject
from climmob.processes.db.assessment import setAssessmentStatus, formattingQuestions
import os, shutil

__all__ = [
    "availableRegistryQuestions",
    "getRegistryQuestions",
    "getRegistryGroupInformation",
    "saveRegistryOrder",
    "addRegistryGroup",
    "modifyRegistryGroup",
    "getRegistryGroupData",
    "addRegistryQuestionToGroup",
    "deleteRegistryGroup",
    "setRegistryStatus",
    "isRegistryOpen",
    "packageExist",
    "exitsRegistryGroup",
    "canDeleteTheGroup",
    "canUseTheQuestion",
    "deleteRegistryQuestionFromGroup",
    "exitsQuestionInGroup",
    "haveTheBasicStructure",
    "haveTheBasic",
    "getRegistryGroup",
    "getRegistryQuestionsApi",
    "isRegistryClose",
    "getProjectNumobs",
    "getAllRegistryGroups",
    "getQuestionsByGroupInRegistry",
    "getTheGroupOfThePackageCode",
    "registryHaveQuestionOfMultimediaType",
    "deleteRegistryByProjectId",
]


def deleteRegistryByProjectId(projectId, request):
    try:
        request.dbsession.query(Regsection).filter(
            Regsection.project_id == projectId
        ).delete()
        return True, ""
    except Exception as e:
        return False, e


def getTheGroupOfThePackageCode(projectId, request):

    data = (
        request.dbsession.query(Registry.section_id)
        .filter(Registry.project_id == projectId)
        .filter(Registry.question_id == 162)
        .first()
    )
    return data[0]


def setRegistryStatus(userOwner, projectCod, projectId, status, request):
    request.dbsession.query(Project).filter(Project.project_id == projectId).update(
        {"project_regstatus": status}
    )
    if status == 0:
        setAssessmentStatus(userOwner, projectCod, projectId, status, request)
        try:
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[userOwner, projectCod, "data", "reg"]
            )
            shutil.rmtree(path)
        except:
            pass


def packageExist(XMLDataRoot, projectId, request):
    qstPackage = (
        request.dbsession.query(Question).filter(Question.question_regkey == 1).first()
    )
    questionCode = qstPackage.question_code
    eincomingPackage = XMLDataRoot.findall(".//" + questionCode.upper())
    if eincomingPackage:
        try:
            incomingPackage = eincomingPackage[0].text
            temp1 = incomingPackage.split("~")
            if len(temp1) == 2:
                temp2 = temp1[0].split("-")
                incomingPackage = int(temp2[1])
            else:
                incomingPackage = int(eincomingPackage[0].text)
        except:
            incomingPackage = -999
        prjData = (
            request.dbsession.query(Project)
            .filter(Project.project_id == projectId)
            .one()
        )
        if 1 <= incomingPackage <= prjData.project_numobs:
            return True
        else:
            return False
    else:
        return False


def isRegistryOpen(projectId, request):
    res = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if res is not None:
        if res.project_regstatus == 1:
            return True
        else:
            return False
    else:
        return False


def getProjectNumobs(projectId, request):
    res = request.dbsession.query(Project).filter(Project.project_id == projectId).one()
    return int(res.project_numobs)


def isRegistryClose(projectId, request):
    res = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if res is not None:
        if res.project_regstatus == 2:
            return True
        else:
            return False
    else:
        return False


def availableRegistryQuestions(projectId, request, registration_and_analysis):
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

    if registration_and_analysis == 1:
        startWith = "SELECT question.*, user.user_fullname, COALESCE(i18n_question.question_name, question.question_name) as question_name FROM user, (select * from question where (question_dtype!=5 and question_dtype!=6) UNION "
    else:
        startWith = "SELECT question.*, user.user_fullname, COALESCE(i18n_question.question_name, question.question_name) as question_name FROM user, (select * from question where (question_dtype!=5 and question_dtype!=6 and question_dtype!= 9 and question_dtype != 10) UNION "
    sql = (
        startWith
        + "SELECT * FROM question WHERE (question_dtype=5 or question_dtype=6) AND question_id in (SELECT DISTINCT(question_id) FROM qstoption)) AS question "
        "LEFT JOIN i18n_question ON question.question_id = i18n_question.question_id AND       i18n_question.lang_code = '"
        + request.locale_name
        + "'"
        " WHERE (" + stringForFilterQuestionByCollaborators + ") AND "
        "question_reqinasses = 0 AND "
        "question_alwaysinasse = 0 AND "
        "question_visible = 1 AND "
        "question.question_id NOT IN (SELECT distinct question_id FROM registry WHERE project_id = '"
        + projectId
        + "') AND"
        " question.user_name = user.user_name"
    )

    if registration_and_analysis == 0:
        sql = sql + " AND question.question_forms in (1,3)"

    questions = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in questions:
        dct = dict(qst)

        result.append(dct)

    return result


def canUseTheQuestion(userOwner, projectId, questionId, request):
    sql = (
        "SELECT * FROM question WHERE question_id = "
        + questionId
        + " AND question_id IN (SELECT question_id from (SELECT * FROM (select * from question where (question_dtype!=5 and question_dtype!=6 and question_dtype!= 9 and question_dtype != 10) UNION "
        "SELECT * FROM question WHERE (question_dtype=5 or question_dtype=6) AND question_id in (SELECT DISTINCT(question_id) FROM qstoption)) AS question "
        "WHERE (user_name = '" + userOwner + "' OR user_name = 'bioversity') AND "
        "question_reqinasses = 0 AND "
        "question_alwaysinasse = 0 AND "
        "question_id NOT IN (SELECT distinct question_id FROM registry WHERE project_id = '"
        + projectId
        + "')) as Preguntas)"
    )
    result = request.dbsession.execute(sql).first()
    if result:
        return True
    else:
        return False


def haveTheBasicStructure(userOwner, projectId, request):
    hasSections = (
        request.dbsession.query(Regsection)
        .filter(Regsection.project_id == projectId)
        .first()
    )
    if hasSections is None:
        addRegistryQuestionsToProject(userOwner, projectId, request)


def haveTheBasic(projectId, request):
    hasSections = (
        request.dbsession.query(Regsection)
        .filter(Regsection.project_id == projectId)
        .first()
    )
    if hasSections:
        return True
    else:
        return False


def getRegistryQuestions(
    userOwner,
    projectId,
    request,
    projectLabels,
    createAutoRegistry=True,
    onlyShowTheBasicQuestions=False,
):

    hasSections = (
        request.dbsession.query(Regsection)
        .filter(Regsection.project_id == projectId)
        .first()
    )
    if hasSections is None:
        if createAutoRegistry:
            addRegistryQuestionsToProject(userOwner, projectId, request)
        else:
            return []

    sql = (
        " SELECT regsection.section_id,regsection.section_name,regsection.section_content,regsection.section_order,regsection.section_private,"
        " question.question_id,COALESCE(i18n_question.question_desc,question.question_desc) as question_desc, COALESCE(i18n_question.question_name, question.question_name) as question_name,question.question_notes,question.question_dtype, "
        " COALESCE(i18n_question.question_posstm, question.question_posstm) as question_posstm, COALESCE(i18n_question.question_negstm ,question.question_negstm) as question_negstm, COALESCE(i18n_question.question_perfstmt, question.question_perfstmt) as question_perfstmt,IFNULL(registry.question_order,0) as question_order,"
        " question.question_reqinreg,question.question_tied, question.question_notobserved, question.question_requiredvalue, question.question_quantitative, question.user_name, (select user_fullname from user where user_name=question.user_name) as user_fullname FROM regsection "
        " LEFT JOIN registry ON  registry.section_project_id = regsection.project_id AND registry.section_id = regsection.section_id "
        " LEFT JOIN i18n_question ON registry.question_id = i18n_question.question_id  AND i18n_question.lang_code = '"
        + request.locale_name
        + "'"
        " LEFT JOIN question ON registry.question_id = question.question_id WHERE "
        " regsection.project_id = '"
        + projectId
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


def getRegistryGroupInformation(projectId, section, request):
    data = (
        request.dbsession.query(Regsection)
        .filter(Regsection.project_id == projectId)
        .filter(Regsection.section_id == section)
        .first()
    )
    return mapFromSchema(data)


def getAllRegistryGroups(projectId, request):
    data = (
        request.dbsession.query(Regsection)
        .filter(Regsection.project_id == projectId)
        .order_by(Regsection.section_id)
        .all()
    )
    return mapFromSchema(data)


def getQuestionsByGroupInRegistry(projectId, section_id, request):

    data = (
        request.dbsession.query(Registry)
        .filter(Registry.project_id == projectId)
        .filter(Registry.section_id == section_id)
        .order_by(Registry.question_order)
        .all()
    )
    return mapFromSchema(data)


def saveRegistryOrder(projectId, order, request):
    # Delete all questions in the registry
    request.dbsession.query(Registry).filter(Registry.project_id == projectId).delete()
    # Update the group order
    pos = 0
    for item in order:
        if item["type"] == "group":
            pos = pos + 1
            request.dbsession.query(Regsection).filter(
                Regsection.project_id == projectId
            ).filter(Regsection.section_id == item["id"].replace("GRP", "")).update(
                {"section_order": pos}
            )
    # Add question to the registry
    pos = 0
    for item in order:
        if item["type"] == "group":
            if "children" in item.keys():
                for child in item["children"]:
                    pos = pos + 1
                    newQuestion = Registry(
                        question_id=child["id"].replace("QST", ""),
                        section_id=item["id"].replace("GRP", ""),
                        question_order=pos,
                        project_id=projectId,
                        section_project_id=projectId,
                    )
                    request.dbsession.add(newQuestion)
        if item["type"] == "question":
            newQuestion = Registry(
                project_id=projectId,
                question_id=item["id"],
                question_order=pos,
            )
            request.dbsession.add(newQuestion)
    request.dbsession.flush()
    return True, ""


def addRegistryGroup(data, self, _from=""):
    _ = self.request.translate
    result = (
        self.request.dbsession.query(func.count(Regsection.section_id).label("total"))
        .filter(Regsection.project_id == data["project_id"])
        .filter(Regsection.section_name == data["section_name"])
        .one()
    )
    if result.total <= 0:
        max_id = (
            self.request.dbsession.query(
                func.ifnull(func.max(Regsection.section_id), 0).label("id_max")
            )
            .filter(Regsection.project_id == data["project_id"])
            .one()
        )
        max_order = (
            self.request.dbsession.query(
                func.ifnull(func.max(Regsection.section_order), 0).label("id_max")
            )
            .filter(Regsection.project_id == data["project_id"])
            .one()
        )
        mappedData = mapToSchema(Regsection, data)
        mappedData["section_id"] = max_id.id_max + 1
        mappedData["section_order"] = max_order.id_max + 1
        newGroup = Regsection(**mappedData)
        try:
            self.request.dbsession.add(newGroup)
            self.request.dbsession.flush()
            if _from == "":
                return True, ""
            else:
                data["group_cod"] = newGroup.section_id
                return True, getRegistryGroupData(data, self)
        except Exception as e:
            return False, e
    else:
        return False, _("This section already exists")


def modifyRegistryGroup(data, self):
    _ = self.request.translate

    result = (
        self.request.dbsession.query(func.count(Regsection.section_id).label("total"))
        .filter(Regsection.project_id == data["project_id"])
        .filter(Regsection.section_id != data["group_cod"])
        .filter(Regsection.section_name == data["section_name"])
        .one()
    )
    if result.total <= 0:
        try:
            mappedData = mapToSchema(Regsection, data)
            self.request.dbsession.query(Regsection).filter(
                Regsection.project_id == data["project_id"]
            ).filter(Regsection.section_id == data["group_cod"]).update(mappedData)
            return True, ""
        except Exception as e:
            return False, e
    else:
        return False, _("This section already exists")


def getRegistryGroupData(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Regsection)
        .filter(Regsection.project_id == data["project_id"])
        .filter(Regsection.section_id == data["group_cod"])
        .one()
    )
    mapedData = mapFromSchema(result)
    return mapedData


def exitsRegistryGroup(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Regsection)
        .filter(Regsection.project_id == data["project_id"])
        .filter(Regsection.section_id == data["group_cod"])
        .first()
    )

    if not result:
        return False
    else:
        return True


def getRegistryGroup(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Regsection.section_id)
        .filter(Regsection.project_id == data["project_id"])
        .all()
    )
    res = []

    for re in result:
        res.append(int(re.section_id))

    return res


def getRegistryQuestionsApi(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Registry.question_id)
        .filter(Registry.project_id == data["project_id"])
        .all()
    )
    res = []

    for re in result:
        res.append(int(re.question_id))

    return res


def addRegistryQuestionToGroup(data, request):
    max_order = (
        request.dbsession.query(
            func.ifnull(func.max(Registry.question_order), 0).label("id_max")
        )
        .filter(Registry.project_id == data["project_id"])
        .filter(Registry.section_id == data["section_id"])
        .one()
    )
    newQuestion = Registry(
        project_id=data["project_id"],
        question_id=data["question_id"],
        section_project_id=data["project_id"],
        section_id=data["section_id"],
        question_order=max_order.id_max + 1,
    )
    try:
        request.dbsession.add(newQuestion)
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def deleteRegistryQuestionFromGroup(data, request):
    try:
        request.dbsession.query(Registry).filter(
            Registry.project_id == data["project_id"]
        ).filter(Registry.question_id == data["question_id"]).filter(
            Registry.section_id == data["group_cod"]
        ).delete()
        return True, ""
    except Exception as e:
        return False, e


def exitsQuestionInGroup(data, request):
    result = (
        request.dbsession.query(Registry)
        .filter(Registry.project_id == data["project_id"])
        .filter(Registry.question_id == data["question_id"])
        .filter(Registry.section_id == data["group_cod"])
        .first()
    )

    if result:
        return True
    else:
        return False


def deleteRegistryGroup(projectId, sectionId, request):
    try:
        request.dbsession.query(Regsection).filter(
            Regsection.project_id == projectId
        ).filter(Regsection.section_id == sectionId).delete()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def canDeleteTheGroup(data, request):
    sql = (
        "select * from registry r, question q where r.project_id='"
        + data["project_id"]
        + "' and r.section_id = "
        + data["group_cod"]
        + " and r.question_id = q.question_id and q.question_reqinreg = 1;"
    )
    result = request.dbsession.execute(sql).fetchall()

    if not result:
        return True
    else:
        return False


def registryHaveQuestionOfMultimediaType(request, projectId):

    result = (
        request.dbsession.query(func.count(Registry.question_id).label("count"))
        .filter(Registry.project_id == projectId)
        .filter(Registry.question_id == Question.question_id)
        .filter(Question.question_dtype.in_([16, 17, 18]))
        .one()
    )

    if result[0] > 0:
        return True
    else:
        return False
