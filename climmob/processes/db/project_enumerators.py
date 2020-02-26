from ...models import PrjEnumerator, Assessment
from climmob.models.schema import mapFromSchema
from ...models import Enumerator, PrjEnumerator
from sqlalchemy import or_
from climmob.config.encdecdata import decodeData

__all__ = [
    "getProjectEnumerators",
    "addEnumeratorToProject",
    "removeEnumeratorFromProject",
    "getUsableEnumerators",
    "seeProgress",
    "getAssessmenstByProject",
]


def getProjectEnumerators(user, project, request):
    """
    sql = "SELECT prjenumerator.enum_id,enumerator.enum_name,enumerator.enum_active " \
          "FROM prjenumerator,enumerator " \
          "WHERE prjenumerator.user_name = enumerator.user_name " \
          "AND prjenumerator.enum_id = enumerator.enum_id " \
          "AND prjenumerator.user_name = '" + user + "' " \
          "AND prjenumerator.project_cod = '" + project + "'"

    assessments = request.dbsession.execute(sql).fetchall()
    result = []
    for qst in assessments:
        dct = dict(qst)
        for key, value in dct.iteritems():
            if isinstance(value, str):
                dct[key] = value.decode("utf8")
        result.append(dct)
    return result
    """
    result = (
        request.dbsession.query(Enumerator)
        .filter(PrjEnumerator.user_name == Enumerator.user_name)
        .filter(PrjEnumerator.enum_id == Enumerator.enum_id)
        .filter(PrjEnumerator.user_name == user)
        .filter(PrjEnumerator.project_cod == project)
        .all()
    )
    res = mapFromSchema(result)
    result = []
    for enum in res:
        enum["enum_password"] = decodeData(request, enum["enum_password"]).decode(
            "utf-8"
        )
        result.append(enum)
    return result


def seeProgress(user, project, request):
    all = {}
    try:
        sql = (
            "SELECT _submitted_by as user_name, count(_submitted_by) as count FROM "
            + user
            + "_"
            + project
            + ".REG_geninfo group by _submitted_by"
        )

        counts = request.dbsession.execute(sql).fetchall()
        result = []

        for qst in counts:
            dct = dict(qst)
            for key, value in dct.items():
                if isinstance(value, str):
                    dct[key] = value
            result.append(dct)
        all["registry"] = result
    except:
        all["registry"] = {}

    try:
        assessments = getAssessmenstByProject(user, project, request)
        for assessment in assessments:

            sql = (
                "SELECT _submitted_by as user_name, count(_submitted_by) as count FROM "
                + user
                + "_"
                + project
                + ".ASS"
                + assessment["ass_cod"]
                + "_geninfo group by _submitted_by"
            )

            counts = request.dbsession.execute(sql).fetchall()
            result = []
            for qst in counts:
                dct = dict(qst)
                for key, value in dct.iteritems():
                    if isinstance(value, str):
                        dct[key] = value
                result.append(dct)

            all[assessment["ass_cod"]] = result
    except:
        print("Error en leer assessments")

    return all


def getAssessmenstByProject(user, project, request):
    res = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .filter(or_(Assessment.ass_status == 1, Assessment.ass_status == 2))
        .order_by(Assessment.ass_days.asc())
        .all()
    )
    res = mapFromSchema(res)
    return res


def addEnumeratorToProject(user, project, enumerator, request):
    newEnumerator = PrjEnumerator(
        user_name=user, project_cod=project, enum_user=user, enum_id=enumerator
    )
    try:
        request.dbsession.add(newEnumerator)
        return True, ""
    except Exception as e:
        return False, e


def removeEnumeratorFromProject(user, project, enumerator, request):
    try:
        request.dbsession.query(PrjEnumerator).filter(
            PrjEnumerator.user_name == user
        ).filter(PrjEnumerator.project_cod == project).filter(
            PrjEnumerator.enum_id == enumerator
        ).delete()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e


def getUsableEnumerators(user, project, request):
    sql = (
        "SELECT enum_id,enum_name FROM enumerator "
        "WHERE enum_active = 1 AND user_name = '" + user + "' "
        "AND enum_id NOT IN ("
        "SELECT distinct enum_id FROM prjenumerator "
        "WHERE user_name = '" + user + "' "
        "AND project_cod = '" + project + "')"
    )

    items = request.dbsession.execute(sql).fetchall()
    result = []
    for item in items:
        dct = dict(item)
        # for key, value in dct.items():
        #    if isinstance(value, str):
        #        dct[key] = value.decode("utf8")
        result.append(dct)
    return result
