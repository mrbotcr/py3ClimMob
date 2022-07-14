from sqlalchemy import func, and_

from climmob.models.climmobv4 import Techalia, Prjalia, I18nTechalia
from climmob.models.schema import mapFromSchema, mapToSchema

__all__ = [
    "getTechsAlias",
    "findTechalias",
    "addTechAlias",
    "getAlias",
    "updateAlias",
    "removeAlias",
    "existAlias",
    "getAliasAssigned",
    "getAliasAssignedWithoutProjectCode",
]


def getTechsAlias(idtech, request):
    res = []
    result = mapFromSchema(
        request.dbsession.query(
            Techalia,
            request.dbsession.query(func.count(Prjalia.alias_id))
            .filter(Techalia.alias_id == Prjalia.alias_used)
            .label("quantity"),
            func.coalesce(I18nTechalia.alias_name, Techalia.alias_name).label(
                "tech_name"
            ),
        )
        .join(
            I18nTechalia,
            and_(
                Techalia.tech_id == I18nTechalia.tech_id,
                Techalia.alias_id == I18nTechalia.alias_id,
                I18nTechalia.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .filter(Techalia.tech_id == idtech)
        .order_by(Techalia.alias_name)
        .all()
    )

    return result


def findTechalias(data, request):
    if data["alias_id"] is None:
        result = (
            request.dbsession.query(Techalia)
            .filter(
                Techalia.tech_id == data["tech_id"],
                Techalia.alias_name == data["alias_name"],
            )
            .all()
        )
    else:
        result = (
            request.dbsession.query(Techalia)
            .filter(
                Techalia.tech_id == data["tech_id"],
                Techalia.alias_name == data["alias_name"],
                Techalia.alias_id != data["alias_id"],
            )
            .all()
        )
    if not result:
        return False
    else:
        return result


def addTechAlias(data, request, _from=""):
    max_id = request.dbsession.query(
        func.ifnull(func.max(Techalia.alias_id), 0).label("id_max")
    ).one()
    data["alias_id"] = max_id.id_max + 1
    mappedData = mapToSchema(Techalia, data)
    newTechalias = Techalia(**mappedData)
    try:
        request.dbsession.add(newTechalias)
        if _from == "":
            return True, ""
        else:
            return True, getAlias(data, request)

    except Exception as e:
        return False, e


def getAlias(data, request):
    return mapFromSchema(
        request.dbsession.query(Techalia)
        .filter(Techalia.alias_id == data["alias_id"])
        .filter(Techalia.tech_id == data["tech_id"])
        .one()
    )


def getAliasAssigned(data, projectId, request):
    result = (
        request.dbsession.query(func.count(Prjalia.alias_id).label("quantity"))
        .filter(Prjalia.project_id == projectId)
        .filter(Prjalia.alias_used == data["alias_id"])
        .filter(Prjalia.tech_used == data["tech_id"])
        .one()
    )

    if result.quantity == 0:
        return False
    else:
        return True


def getAliasAssignedWithoutProjectCode(data, request):
    result = (
        request.dbsession.query(func.count(Prjalia.alias_id).label("quantity"))
        .filter(Prjalia.alias_used == data["alias_id"])
        .filter(Prjalia.tech_used == data["tech_id"])
        .one()
    )

    if result.quantity == 0:
        return False
    else:
        return True


def existAlias(data, request):
    result = (
        request.dbsession.query(Techalia)
        .filter(Techalia.alias_id == data["alias_id"])
        .filter(Techalia.tech_id == data["tech_id"])
        .all()
    )

    if not result:
        return False
    else:
        return True


def updateAlias(data, request):
    try:
        mappedData = mapToSchema(Techalia, data)
        request.dbsession.query(Techalia).filter(
            Techalia.alias_id == data["alias_id"]
        ).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e


def removeAlias(data, request):
    try:
        request.dbsession.query(Techalia).filter(
            Techalia.alias_id == data["alias_id"]
        ).delete()
        return True, ""
    except Exception as e:
        return False, e
