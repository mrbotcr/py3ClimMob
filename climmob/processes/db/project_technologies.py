from ...models import Prjtech, Technology, Prjalia, Techalia, Project
from ...models.schema import mapToSchema, mapFromSchema
from sqlalchemy import func, or_

__all__ = [
    "searchTechnologies",
    "searchTechnologiesInProject",
    "addTechnologyProject",
    "deleteTechnologyProject",
    "numberOfTechnologies",
    "AliasSearchTechnology",
    "AliasSearchTechnologyInProject",
    "AliasExtraSearchTechnologyInProject",
    "AddAliasTechnology",
    "addTechAliasExtra",
    "deleteAliasTechnology",
    "findAssignedAlias",
    "findTechAlias",
    "numberOfCombinationsForTheProject",
    "numberOfAliasesInTechnology",
    "changeTheStateOfCreateComb",
    "getAliasExtra",
]


def searchTechnologies(user, projectid, request):
    res = []

    subquery = (
        request.dbsession.query(Prjtech.tech_id)
        .filter(Prjtech.project_cod == projectid)
        .filter(Prjtech.user_name == user)
    )
    result = (
        request.dbsession.query(
            Technology,
            request.dbsession.query(func.count(Techalia.tech_id))
            .filter(Techalia.tech_id == Technology.tech_id)
            .label("quantityAlias"),
        )
        .filter(or_(Technology.user_name == user, Technology.user_name == "bioversity"))
        .filter(Technology.tech_id.notin_(subquery))
        .order_by(Technology.tech_name)
        .all()
    )
    for technology in result:
        res.append(
            {
                "tech_id": technology[0].tech_id,
                "tech_name": technology[0].tech_name,
                "user_name": technology[0].user_name,
                "quantity": 0,
                "quantityAlias": technology.quantityAlias,
            }
        )

    return res


def searchTechnologiesInProject(user, project_id, request):

    result = (
        request.dbsession.query(
            Technology.tech_name,
            Prjtech,
            request.dbsession.query(func.count(Prjalia.alias_id))
            .filter(Prjalia.tech_id == Prjtech.tech_id)
            .filter(Prjalia.project_cod == project_id)
            .filter(Prjalia.user_name == user)
            .label("quantity"),
            request.dbsession.query(func.count(Techalia.tech_id))
            .filter(Techalia.tech_id == Prjtech.tech_id)
            .label("quantityAlias"),
        )
        .filter(Prjtech.tech_id == Technology.tech_id)
        .filter(Prjtech.user_name == user)
        .filter(Prjtech.project_cod == project_id)
        .order_by(Technology.tech_name)
        .all()
    )

    res = []
    for technology in result:
        res.append(
            {
                "tech_name": technology.tech_name,
                "user_name": technology[1].user_name,
                "project_cod": technology[1].project_cod,
                "tech_id": technology[1].tech_id,
                "quantity": technology.quantity,
                "quantityAlias": technology.quantityAlias,
            }
        )

    return res


def changeTheStateOfCreateComb(user, projectid, request):
    request.dbsession.query(Project).filter(Project.user_name == user).filter(
        Project.project_cod == projectid
    ).update({"project_createcomb": 1})


def addTechnologyProject(user, projectid, tech_id, request):

    newTechnologyProject = Prjtech(
        user_name=user, project_cod=projectid, tech_id=tech_id
    )
    try:
        request.dbsession.add(newTechnologyProject)

        request.dbsession.query(Project).filter(Project.user_name == user).filter(
            Project.project_cod == projectid
        ).update({"project_createcomb": 1})

        return True, ""

    except Exception as e:
        print(str(e))
        return False, e


def deleteTechnologyProject(user, projectid, tech_id, request):
    try:
        request.dbsession.query(Prjtech).filter(Prjtech.user_name == user).filter(
            Prjtech.tech_id == tech_id
        ).filter(Prjtech.project_cod == projectid).delete()

        request.dbsession.query(Project).filter(Project.user_name == user).filter(
            Project.project_cod == projectid
        ).update({"project_createcomb": 1})

        return True, ""

    except Exception as e:
        print(str(e))
        return False, e


def numberOfTechnologies(user, projectid, request):
    result = (
        request.dbsession.query(func.count(Prjtech.project_cod).label("number"))
        .filter(Prjtech.user_name == user)
        .filter(Prjtech.project_cod == projectid)
        .one()
    )

    return result.number


# -----------------------------------------Alises-------------------------------------------------------


def AliasSearchTechnology(technology, user, projectid, request):
    res = []
    subquery = (
        request.dbsession.query(Prjalia.alias_used)
        .filter(Prjalia.user_name == user)
        .filter(Prjalia.project_cod == projectid)
        .filter(Prjalia.tech_id == technology)
        .filter(Prjalia.alias_name == "")
    )
    result = (
        request.dbsession.query(Technology, Techalia)
        .filter(Techalia.tech_id == Technology.tech_id)
        .filter(Technology.tech_id == technology)
        .filter(Techalia.alias_id.notin_(subquery))
        .all()
    )
    for technology in result:
        res.append(
            {
                "tech_id": technology[0].tech_id,
                "tech_name": technology[0].tech_name,
                "user_name": technology[0].user_name,
                "tech_idAlias": technology[1].tech_id,
                "alias_id": technology[1].alias_id,
                "alias_name": technology[1].alias_name,
            }
        )

    return res


def AliasSearchTechnologyInProject(technology, user, projectid, request):
    res = []
    result = (
        request.dbsession.query(Prjalia, Techalia)
        .filter(Prjalia.user_name == user)
        .filter(Prjalia.project_cod == projectid)
        .filter(Prjalia.tech_id == technology)
        .filter(Prjalia.alias_used == Techalia.alias_id)
        .filter(Prjalia.tech_used == Techalia.tech_id)
    )
    for technology in result:
        res.append(
            {
                "user_name": technology[0].user_name,
                "project_cod": technology[0].project_cod,
                "tech_idPrj": technology[0].tech_id,
                "alias_id": technology[0].alias_id,
                "alias_namePrj": technology[0].alias_name,
                "tech_used": technology[0].tech_used,
                "alias_used": technology[0].alias_used,
                "tech_idTec": technology[1].tech_id,
                "alias_idTec": technology[1].alias_id,
                "alias_name": technology[1].alias_name,
            }
        )

    return res


def AliasExtraSearchTechnologyInProject(technology, user, projectid, request):
    res = []
    result = (
        request.dbsession.query(Prjalia)
        .filter(Prjalia.user_name == user)
        .filter(Prjalia.project_cod == projectid)
        .filter(Prjalia.tech_id == technology)
        .filter(Prjalia.alias_name != "")
    )

    for alias in result:
        res.append(
            {
                "user_name": alias.user_name,
                "project_cod": alias.project_cod,
                "tech_id": alias.tech_id,
                "alias_id": alias.alias_id,
                "alias_name": alias.alias_name,
                "tech_used": alias.tech_used,
                "alias_used": alias.alias_used,
            }
        )

    return res


def AddAliasTechnology(data, request):
    max_id = request.dbsession.query(
        func.ifnull(func.max(Prjalia.alias_id), 0).label("id_max")
    ).one()
    newAliasTechnology = Prjalia(
        user_name=data["user_name"],
        project_cod=data["project_cod"],
        tech_id=data["tech_id"],
        tech_used=data["tech_id"],
        alias_used=data["alias_id"],
        alias_id=max_id.id_max + 1,
        alias_name="",
    )

    try:
        request.dbsession.add(newAliasTechnology)
        request.dbsession.flush()
        request.dbsession.query(Project).filter(
            Project.user_name == data["user_name"]
        ).filter(Project.project_cod == data["project_cod"]).update(
            {"project_createcomb": 1}
        )

        return (
            True,
            mapFromSchema(
                request.dbsession.query(Prjalia)
                .filter(Prjalia.user_name == data["user_name"])
                .filter(Prjalia.tech_id == data["tech_id"])
                .filter(Prjalia.project_cod == data["project_cod"])
                .filter(Prjalia.alias_id == newAliasTechnology.alias_id)
                .one()
            ),
        )

    except Exception as e:
        print(str(e))
        return False, e


def addTechAliasExtra(data, request):
    max_id = request.dbsession.query(
        func.ifnull(func.max(Prjalia.alias_id), 0).label("id_max")
    ).one()
    mappedData = mapToSchema(Prjalia, data)
    mappedData["alias_id"] = max_id.id_max + 1
    newAliasTechnology = Prjalia(**mappedData)
    try:
        # print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        # print mappedData
        # print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        request.dbsession.add(newAliasTechnology)
        request.dbsession.flush()
        request.dbsession.query(Project).filter(
            Project.user_name == data["user_name"]
        ).filter(Project.project_cod == data["project_cod"]).update(
            {"project_createcomb": 1}
        )

        return (
            True,
            mapFromSchema(
                request.dbsession.query(Prjalia)
                .filter(Prjalia.user_name == data["user_name"])
                .filter(Prjalia.tech_id == data["tech_id"])
                .filter(Prjalia.project_cod == data["project_cod"])
                .filter(Prjalia.alias_id == newAliasTechnology.alias_id)
                .one()
            ),
        )

    except Exception as e:
        print(str(e))
        return False, e


def findAssignedAlias(data, request):
    result = (
        request.dbsession.query(Prjalia)
        .filter(Prjalia.user_name == data["user_name"])
        .filter(Prjalia.tech_id == data["tech_id"])
        .filter(Prjalia.project_cod == data["project_cod"])
        .filter(Prjalia.alias_id == data["alias_id"])
        .all()
    )
    if result:
        return True
    else:
        return False


def deleteAliasTechnology(user, projectid, techid, aliasid, request):
    try:
        request.dbsession.query(Prjalia).filter(Prjalia.user_name == user).filter(
            Prjalia.tech_id == techid
        ).filter(Prjalia.project_cod == projectid).filter(
            Prjalia.alias_id == aliasid
        ).delete()
        request.dbsession.query(Project).filter(Project.user_name == user).filter(
            Project.project_cod == projectid
        ).update({"project_createcomb": 1})

        return True, ""

    except Exception as e:
        print(str(e))
        return False, e


def findTechAlias(data, request):
    result = (
        request.dbsession.query(Techalia)
        .filter(
            Techalia.tech_id == data["tech_id"],
            Techalia.alias_name == data["alias_name"],
        )
        .all()
    )
    if not result:
        result = (
            request.dbsession.query(Prjalia)
            .filter(Prjalia.user_name == data["user_name"])
            .filter(Prjalia.project_cod == data["project_cod"])
            .filter(Prjalia.tech_id == data["tech_id"])
            .filter(Prjalia.alias_name == data["alias_name"])
            .all()
        )
        if not result:
            return False
        else:
            return result
    else:
        return result


def numberOfCombinationsForTheProject(user, projectid, request):
    number = (
        request.dbsession.query(Project.project_numcom.label("numcom"))
        .filter(Project.user_name == user)
        .filter(Project.project_cod == projectid)
        .one()
    )

    if not number:
        return False
    else:
        return number.numcom


def numberOfAliasesInTechnology(user, projectid, technologyid, request):
    number = (
        request.dbsession.query(func.count(Prjalia.user_name).label("count"))
        .filter(Prjalia.user_name == user)
        .filter(Prjalia.project_cod == projectid)
        .filter(Prjalia.tech_id == technologyid)
        .one()
    )

    if not number:
        return False
    else:
        return number.count


def getAliasExtra(technology, user, projectid, aliasid, request):
    alias = (
        request.dbsession.query(Prjalia)
        .filter(Prjalia.user_name == user)
        .filter(Prjalia.project_cod == projectid)
        .filter(Prjalia.tech_id == technology)
        .filter(Prjalia.alias_id == aliasid)
        .one()
    )
    return alias
