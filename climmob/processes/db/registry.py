from sqlalchemy import func
from climmob.models.schema import mapFromSchema, mapToSchema
from ...models import Regsection, Registry, Project, Question, Qstoption
from .project import addRegistryQuestionsToProject
from .assessment import setAssessmentStatus
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
    "generateStructureForInterface",
    "haveTheBasic",
    "getRegistryGroup",
    "getRegistryQuestionsApi",
    "generateStructureForValidateJsonOdk",
    "isRegistryClose",
    "getProjectNumobs",
]


def setRegistryStatus(user, project, status, request):
    request.dbsession.query(Project).filter(Project.user_name == user).filter(
        Project.project_cod == project
    ).update({"project_regstatus": status})
    if status == 0:
        setAssessmentStatus(user, project, status, request)
        try:
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[user, project, "data", "reg"]
            )
            shutil.rmtree(path)
        except:
            pass


def packageExist(XMLDataRoot, user, project, request):
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
            .filter(Project.user_name == user)
            .filter(Project.project_cod == project)
            .one()
        )
        if 1 <= incomingPackage <= prjData.project_numobs:
            return True
        else:
            return False
    else:
        return False


def isRegistryOpen(user, project, request):
    res = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    if res is not None:
        if res.project_regstatus == 1:
            return True
        else:
            return False
    else:
        return False


def getProjectNumobs(user, project, request):
    res = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .one()
    )
    return int(res.project_numobs)


def isRegistryClose(user, project, request):
    res = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    if res is not None:
        if res.project_regstatus == 2:
            return True
        else:
            return False
    else:
        return False


def availableRegistryQuestions(user, project, request):
    # sql = "SELECT * FROM question WHERE (user_name = '" + user + "' OR user_name = 'bioversity') AND " \
    #      "question.question_reqinasses = 0 AND question.question_alwaysinasse = 0 AND question_id NOT IN (SELECT distinct question_id FROM registry WHERE user_name = '" + user + "' AND project_cod = '" + project  + "')"

    sql = (
        "SELECT * FROM (select * from question where (question_dtype!=5 and question_dtype!=6 and question_dtype!= 9 and question_dtype != 10) UNION "
        "SELECT * FROM question WHERE (question_dtype=5 or question_dtype=6) AND question_id in (SELECT DISTINCT(question_id) FROM qstoption)) AS question "
        "WHERE (user_name = '" + user + "' OR user_name = 'bioversity') AND "
        "question_reqinasses = 0 AND "
        "question_alwaysinasse = 0 AND "
        "question_visible = 1 AND "
        "question_id NOT IN (SELECT distinct question_id FROM registry WHERE user_name = '"
        + user
        + "' AND project_cod = '"
        + project
        + "')"
    )

    questions = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in questions:
        dct = dict(qst)
        # for key, value in dct.items():
        #    if isinstance(value, str):
        #        dct[key] = value.decode("utf8")
        result.append(dct)

    return result


def canUseTheQuestion(user, project, question_id, request):
    sql = (
        "SELECT * FROM question WHERE question_id = "
        + question_id
        + " AND question_id IN (SELECT question_id from (SELECT * FROM (select * from question where (question_dtype!=5 and question_dtype!=6 and question_dtype!= 9 and question_dtype != 10) UNION "
        "SELECT * FROM question WHERE (question_dtype=5 or question_dtype=6) AND question_id in (SELECT DISTINCT(question_id) FROM qstoption)) AS question "
        "WHERE (user_name = '" + user + "' OR user_name = 'bioversity') AND "
        "question_reqinasses = 0 AND "
        "question_alwaysinasse = 0 AND "
        "question_id NOT IN (SELECT distinct question_id FROM registry WHERE user_name = '"
        + user
        + "' AND project_cod = '"
        + project
        + "')) as Preguntas)"
    )

    result = request.dbsession.execute(sql).first()
    if result:
        return True
    else:
        return False


def haveTheBasicStructure(user, project, request):
    hasSections = (
        request.dbsession.query(Regsection)
        .filter(Regsection.user_name == user)
        .filter(Regsection.project_cod == project)
        .first()
    )
    if hasSections is None:
        addRegistryQuestionsToProject(user, project, request)


def haveTheBasic(user, project, request):
    hasSections = (
        request.dbsession.query(Regsection)
        .filter(Regsection.user_name == user)
        .filter(Regsection.project_cod == project)
        .first()
    )
    if hasSections:
        return True
    else:
        return False


def generateStructureForValidateJsonOdk(user, project, request):
    result = (
        request.dbsession.query(
            Regsection.section_id,
            Question.question_code,
            Question.question_requiredvalue,
        )
        .filter(Regsection.user_name == user)
        .filter(Regsection.project_cod == project)
        .filter(Registry.user_name == user)
        .filter(Registry.project_cod == project)
        .filter(Regsection.section_id == Registry.section_id)
        .filter(Registry.question_id == Question.question_id)
        .all()
    )

    if result:
        return result
    else:
        return False


def generateStructureForInterface(user, project, request):

    data = []
    sections = mapFromSchema(
        request.dbsession.query(Regsection)
        .filter(Regsection.user_name == user)
        .filter(Regsection.project_cod == project)
        .order_by(Regsection.section_order)
        .all()
    )

    for section in sections:

        dataSection = {}
        dataSection["section_name"] = section["section_name"]
        dataSection["section_content"] = section["section_content"]
        dataSection["section_id"] = section["section_id"]
        dataSection["section_questions"] = []

        questions = mapFromSchema(
            request.dbsession.query(Registry)
            .filter(Registry.user_name == user)
            .filter(Registry.project_cod == project)
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
            dataQuestion["question_id"] = questionData["question_id"]
            dataQuestion["question_desc"] = questionData["question_desc"]
            dataQuestion["question_notes"] = questionData["question_notes"]
            dataQuestion["question_unit"] = questionData["question_unit"]
            dataQuestion["question_requiredvalue"] = questionData[
                "question_requiredvalue"
            ]
            dataQuestion["question_code"] = questionData["question_code"]
            dataQuestion["question_datafield"] = (
                "grp_"
                + str(section["section_id"])
                + "/"
                + dataQuestion["question_code"]
            )

            if questionData["question_dtype"] == 1:
                dataQuestion["question_dtype"] = "text"
            if questionData["question_dtype"] == 2:
                dataQuestion["question_dtype"] = "decimal"
            if questionData["question_dtype"] == 3:
                dataQuestion["question_dtype"] = "integer"
            if questionData["question_dtype"] == 4:
                dataQuestion["question_dtype"] = "geopoint"
            if questionData["question_dtype"] == 11:
                dataQuestion["question_dtype"] = "geotrace"
            if questionData["question_dtype"] == 12:
                dataQuestion["question_dtype"] = "geoshape"
            if questionData["question_dtype"] == 13:
                dataQuestion["question_dtype"] = "date"
            if questionData["question_dtype"] == 14:
                dataQuestion["question_dtype"] = "time"
            if questionData["question_dtype"] == 15:
                dataQuestion["question_dtype"] = "dateTime"
            if questionData["question_dtype"] == 16:
                dataQuestion["question_dtype"] = "image"
            if questionData["question_dtype"] == 17:
                dataQuestion["question_dtype"] = "audio"
            if questionData["question_dtype"] == 18:
                dataQuestion["question_dtype"] = "video"
            if questionData["question_dtype"] == 19:
                dataQuestion["question_dtype"] = "barcode"
            if questionData["question_dtype"] == 7:
                dataQuestion["question_dtype"] = "package"
            if questionData["question_dtype"] == 8:
                dataQuestion["question_dtype"] = "observer"

            if questionData["question_dtype"] == 5:
                dataQuestion["question_dtype"] = "Select one"

            if questionData["question_dtype"] == 6:
                dataQuestion["question_dtype"] = "Select Multiple"

            if (
                questionData["question_dtype"] == 5
                or questionData["question_dtype"] == 6
            ):
                options = mapFromSchema(
                    request.dbsession.query(Qstoption)
                    .filter(Qstoption.question_id == question["question_id"])
                    .all()
                )
                dataQuestion["question_options"] = []

                for option in options:
                    dataQuestion["question_options"].append(option)

            dataSection["section_questions"].append(dataQuestion)

        data.append(dataSection)

    # Extra section for necessary questions in the json
    necessarySection = {}
    necessarySection["section_name"] = "Extra Field"
    necessarySection["section_content"] = request.translate(
        "Have necessary questions for documentation."
    )
    necessarySection["section_id"] = "None"
    necessarySection["section_questions"] = [
        {
            "question_desc": request.translate("Start of survey"),
            "question_dtype": "datetime",
            "question_notes": request.translate("Start of survey"),
            "question_datafield": "clm_start",
            "question_requiredvalue": 1,
            "question_unit": "",
            "question_code": "__CLMQST1__",
            "question_id": -1,
        },
        {
            "question_desc": request.translate("End of survey"),
            "question_dtype": "datetime",
            "question_notes": request.translate("End of survey"),
            "question_datafield": "clm_end",
            "question_requiredvalue": 1,
            "question_unit": "",
            "question_code": "__CLMQST2__",
            "question_id": -2,
        },
    ]

    data.append(necessarySection)

    return data


def getRegistryQuestions(user, project, request):

    hasSections = (
        request.dbsession.query(Regsection)
        .filter(Regsection.user_name == user)
        .filter(Regsection.project_cod == project)
        .first()
    )
    if hasSections is None:
        addRegistryQuestionsToProject(user, project, request)

    sql = (
        "SELECT regsection.section_id,regsection.section_name,regsection.section_content,regsection.section_order,regsection.section_color,"
        "question.question_id,question.question_desc,question.question_notes,question.question_dtype,IFNULL(registry.question_order,0) as question_order,"
        "question.question_reqinreg FROM regsection LEFT JOIN registry ON registry.section_user = regsection.user_name AND registry.section_project = regsection.project_cod "
        " AND registry.section_id = regsection.section_id "
        " LEFT JOIN question ON registry.question_id = question.question_id WHERE "
        "regsection.user_name = '"
        + user
        + "' AND regsection.project_cod = '"
        + project
        + "' ORDER BY section_order,question_order"
    )
    questions = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in questions:
        dct = dict(qst)
        # for key, value in dct.items():
        #    if isinstance(value, str):
        #        dct[key] = value.decode("utf8")
        result.append(dct)

    return result


def getRegistryGroupInformation(user, project, section, request):
    data = (
        request.dbsession.query(Regsection)
        .filter(Regsection.user_name == user)
        .filter(Regsection.project_cod == project)
        .filter(Regsection.section_id == section)
        .first()
    )
    return mapFromSchema(data)


def saveRegistryOrder(user, project, order, request):
    # Delete all questions in the registry
    request.dbsession.query(Registry).filter(Registry.user_name == user).filter(
        Registry.project_cod == project
    ).delete()
    # Update the group order
    pos = 0
    for item in order:
        if item["type"] == "group":
            pos = pos + 1
            request.dbsession.query(Regsection).filter(
                Regsection.user_name == user
            ).filter(Regsection.project_cod == project).filter(
                Regsection.section_id == item["id"].replace("GRP", "")
            ).update(
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
                        user_name=user,
                        project_cod=project,
                        question_id=child["id"].replace("QST", ""),
                        section_user=user,
                        section_project=project,
                        section_id=item["id"].replace("GRP", ""),
                        question_order=pos,
                    )
                    request.dbsession.add(newQuestion)
        if item["type"] == "question":
            newQuestion = Registry(
                user_name=user,
                project_cod=project,
                question_id=item["id"],
                question_order=pos,
            )
            request.dbsession.add(newQuestion)
    request.dbsession.flush()
    return True, ""
    # except Exception, e:
    #     return False,str(e)


def addRegistryGroup(data, self, _from=""):
    result = (
        self.request.dbsession.query(func.count(Regsection.section_id).label("total"))
        .filter(Regsection.project_cod == data["project_cod"])
        .filter(Regsection.user_name == data["user_name"])
        .filter(Regsection.section_name == data["section_name"])
        .one()
    )
    if result.total <= 0:
        max_id = (
            self.request.dbsession.query(
                func.ifnull(func.max(Regsection.section_id), 0).label("id_max")
            )
            .filter(Regsection.project_cod == data["project_cod"])
            .one()
        )
        max_order = (
            self.request.dbsession.query(
                func.ifnull(func.max(Regsection.section_order), 0).label("id_max")
            )
            .filter(Regsection.user_name == data["user_name"])
            .filter(Regsection.project_cod == data["project_cod"])
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
        return False, self.request.translate("This section already exists")


def modifyRegistryGroup(data, self):
    result = (
        self.request.dbsession.query(func.count(Regsection.section_id).label("total"))
        .filter(Regsection.project_cod == data["project_cod"])
        .filter(Regsection.user_name == data["user_name"])
        .filter(Regsection.section_id != data["group_cod"])
        .filter(Regsection.section_name == data["section_name"])
        .one()
    )
    if result.total <= 0:
        try:
            mappedData = mapToSchema(Regsection, data)
            self.request.dbsession.query(Regsection).filter(
                Regsection.user_name == data["user_name"]
            ).filter(Regsection.project_cod == data["project_cod"]).filter(
                Regsection.section_id == data["group_cod"]
            ).update(
                mappedData
            )
            return True, ""
        except Exception as e:
            return False, e
    else:
        return False, self.request.translate("This section already exists")


def getRegistryGroupData(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Regsection)
        .filter(Regsection.user_name == data["user_name"])
        .filter(Regsection.project_cod == data["project_cod"])
        .filter(Regsection.section_id == data["group_cod"])
        .one()
    )
    mapedData = mapFromSchema(result)
    return mapedData


def exitsRegistryGroup(data, self):
    mySession = self.request.dbsession
    result = (
        mySession.query(Regsection)
        .filter(Regsection.user_name == data["user_name"])
        .filter(Regsection.project_cod == data["project_cod"])
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
        .filter(Regsection.user_name == data["user_name"])
        .filter(Regsection.project_cod == data["project_cod"])
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
        .filter(Registry.user_name == data["user_name"])
        .filter(Registry.project_cod == data["project_cod"])
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
        .filter(Registry.user_name == data["user_name"])
        .filter(Registry.project_cod == data["project_cod"])
        .filter(Registry.section_id == data["section_id"])
        .one()
    )
    newQuestion = Registry(
        user_name=data["user_name"],
        project_cod=data["project_cod"],
        question_id=data["question_id"],
        section_user=data["user_name"],
        section_project=data["project_cod"],
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
            Registry.user_name == data["user_name"]
        ).filter(Registry.project_cod == data["project_cod"]).filter(
            Registry.question_id == data["question_id"]
        ).filter(
            Registry.section_id == data["group_cod"]
        ).delete()
        return True, ""
    except Exception as e:
        return False, e


def exitsQuestionInGroup(data, request):
    result = (
        request.dbsession.query(Registry)
        .filter(Registry.user_name == data["user_name"])
        .filter(Registry.project_cod == data["project_cod"])
        .filter(Registry.question_id == data["question_id"])
        .filter(Registry.section_id == data["group_cod"])
        .first()
    )

    if result:
        return True
    else:
        return False


def deleteRegistryGroup(user, projectid, sectionid, request):
    try:
        request.dbsession.query(Regsection).filter(Regsection.user_name == user).filter(
            Regsection.project_cod == projectid
        ).filter(Regsection.section_id == sectionid).delete()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def canDeleteTheGroup(data, request):
    sql = (
        "select * from registry r, question q where r.user_name = '"
        + data["user_name"]
        + "' and r.project_cod='"
        + data["project_cod"]
        + "' and r.section_id = "
        + data["group_cod"]
        + " and r.question_id = q.question_id and q.question_reqinreg = 1;"
    )
    result = request.dbsession.execute(sql).fetchall()

    if not result:
        return True
    else:
        return False
