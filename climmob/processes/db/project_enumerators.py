from sqlalchemy import or_, tuple_

from climmob.config.encdecdata import decodeData
from climmob.models import userProject, Assessment, User, Enumerator, PrjEnumerator
from climmob.models.repository import sql_fetch_all
from climmob.models.schema import mapFromSchema
from climmob.processes import getEnumeratorByProject

__all__ = [
    "getProjectEnumerators",
    "addEnumeratorToProject",
    "removeEnumeratorFromProject",
    "getUsableEnumerators",
    "seeProgress",
    "getAssessmenstByProject",
    "thereIsAnEqualEnumIdInTheProject",
]


def getProjectEnumerators(projectId, request):

    result = (
        request.dbsession.query(Enumerator, User.user_fullname)
        .filter(PrjEnumerator.enum_user == Enumerator.user_name)
        .filter(PrjEnumerator.enum_id == Enumerator.enum_id)
        .filter(PrjEnumerator.project_id == projectId)
        .filter(PrjEnumerator.enum_user == User.user_name)
        .all()
    )
    res = mapFromSchema(result)
    newFormat = {}
    for enum in res:
        enum["enum_password"] = decodeData(request, enum["enum_password"]).decode(
            "utf-8"
        )

        if enum["user_name"] not in newFormat.keys():
            newFormat[enum["user_name"]] = []
            newFormat[enum["user_name"]].append(enum)
        else:
            newFormat[enum["user_name"]].append(enum)

    return newFormat


def seeProgress(userOwner, projectId, projectCod, request):
    all = {}
    try:
        sql = (
            "SELECT _submitted_by as user_name, count(*) as count FROM "
            + userOwner
            + "_"
            + projectCod
            + ".REG_geninfo group by _submitted_by"
        )

        counts = sql_fetch_all(sql)
        result = []

        for qst in counts:
            _user = getEnumeratorByProject(projectId, qst[0], request)
            if _user:
                result.append({"User": _user["enum_name"], "Count": qst[1]})
            else:
                enco = False
                for i, ex in enumerate(result, start=0):

                    if ex["User"] == "Other":
                        enco = True
                        result[i]["Count"] = result[i]["Count"] + qst[1]
                if enco == False:
                    result.append({"User": "Other", "Count": qst[1]})

        all["registry"] = result
    except:
        all["registry"] = {}

    try:
        ass = []
        assessments = getAssessmenstByProject(projectId, request)
        for assessment in assessments:

            sql = (
                "SELECT _submitted_by as user_name, count(*) as count FROM "
                + userOwner
                + "_"
                + projectCod
                + ".ASS"
                + assessment["ass_cod"]
                + "_geninfo group by _submitted_by"
            )

            # counts = request.dbsession.execute(sql).fetchall()
            counts = sql_fetch_all(sql)
            result = []
            for qst in counts:
                _user = getEnumeratorByProject(projectId, qst[0], request)
                if _user:
                    result.append({"User": _user["enum_name"], "Count": qst[1]})
                else:
                    enco = False
                    for i, ex in enumerate(result, start=0):

                        if ex["User"] == "Other":
                            enco = True
                            result[i]["Count"] = result[i]["Count"] + qst[1]
                    if enco == False:
                        result.append({"User": "Other", "Count": qst[1]})

            ass.append({"Name": assessment["ass_cod"], "Values": result})

        all["Assessments"] = ass
    except:
        return all

    return all


def getAssessmenstByProject(projectId, request):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(or_(Assessment.ass_status == 1, Assessment.ass_status == 2))
        .order_by(Assessment.ass_days.asc())
        .all()
    )
    res = mapFromSchema(res)
    return res


def thereIsAnEqualEnumIdInTheProject(enumId, projectId, request):
    res = (
        request.dbsession.query(PrjEnumerator)
        .filter(PrjEnumerator.project_id == projectId)
        .filter(PrjEnumerator.enum_id == enumId)
        .first()
    )
    if res:
        return True

    return False


def addEnumeratorToProject(projectId, enumeratorId, userOwner, request):
    newEnumerator = PrjEnumerator(
        project_id=projectId, enum_user=userOwner, enum_id=enumeratorId
    )
    try:
        request.dbsession.add(newEnumerator)
        return True, ""
    except Exception as e:
        return False, e


def removeEnumeratorFromProject(projectId, enumerator, request):
    try:
        request.dbsession.query(PrjEnumerator).filter(
            PrjEnumerator.project_id == projectId
        ).filter(PrjEnumerator.enum_id == enumerator).delete()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def getUsableEnumerators(projectId, request):

    # get the user that are collaborators in the project
    projectCollaborators = request.dbsession.query(userProject.user_name).filter(
        userProject.project_id == projectId
    )

    exclude = (
        request.dbsession.query(PrjEnumerator.enum_id, PrjEnumerator.enum_user)
        .distinct()
        .filter(PrjEnumerator.project_id == projectId)
    )

    result = (
        request.dbsession.query(
            Enumerator.user_name,
            Enumerator.enum_id,
            Enumerator.enum_name,
            User.user_fullname,
        )
        .filter(Enumerator.enum_active == 1)
        .filter(Enumerator.user_name.in_(projectCollaborators))
        .filter(User.user_name == Enumerator.user_name)
        .filter(tuple_(Enumerator.enum_id, Enumerator.user_name).notin_(exclude))
        .all()
    )

    return mapFromSchema(result)
