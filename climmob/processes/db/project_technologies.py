from ...models import (
    Prjtech,
    Technology,
    Prjalia,
    Techalia,
    Project,
    I18nTechnology,
    I18nTechalia,
    userProject,
    User,
)
from ...models.schema import mapToSchema, mapFromSchema
from sqlalchemy import func, or_, and_

__all__ = [
    "searchTechnologies",
    "searchTechnologiesInProject",
    "addTechnologyProject",
    "deleteTechnologyProject",
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
]


def searchTechnologies(projectId, request):
    res = []

    userCollaborators = request.dbsession.query(userProject.user_name).filter(
        userProject.project_id == projectId
    )

    subquery = request.dbsession.query(Prjtech.tech_id).filter(
        Prjtech.project_id == projectId
    )
    result = (
        request.dbsession.query(
            Technology,
            request.dbsession.query(func.count(Techalia.tech_id))
            .filter(Techalia.tech_id == Technology.tech_id)
            .label("quantityAlias"),
            func.coalesce(I18nTechnology.tech_name, Technology.tech_name).label(
                "tech_name"
            ),
            User.user_fullname,
        )
        .join(
            I18nTechnology,
            and_(
                Technology.tech_id == I18nTechnology.tech_id,
                I18nTechnology.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .filter(
            or_(
                Technology.user_name.in_(userCollaborators),
                Technology.user_name == "Bioversity",
            )
        )
        .filter(Technology.tech_id.notin_(subquery))
        .filter(Technology.user_name == User.user_name)
        .order_by(Technology.tech_name)
        .all()
    )
    for technology in result:
        res.append(
            {
                "tech_id": technology[0].tech_id,
                "tech_name": technology[2],
                "user_name": technology[0].user_name,
                "quantity": 0,
                "quantityAlias": technology.quantityAlias,
                "user_fullname": technology[3],
            }
        )

    return res


def searchTechnologiesInProject(projectId, request):

    result = (
        request.dbsession.query(
            func.coalesce(I18nTechnology.tech_name, Technology.tech_name).label(
                "tech_name"
            ),
            Technology.user_name,
            Prjtech,
            request.dbsession.query(func.count(Prjalia.alias_id))
            .filter(Prjalia.tech_id == Prjtech.tech_id)
            .filter(Prjalia.project_id == projectId)
            .label("quantity"),
            request.dbsession.query(func.count(Techalia.tech_id))
            .filter(Techalia.tech_id == Prjtech.tech_id)
            .label("quantityAlias"),
            User.user_fullname,
        )
        .join(
            I18nTechnology,
            and_(
                Prjtech.tech_id == I18nTechnology.tech_id,
                I18nTechnology.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .filter(Prjtech.tech_id == Technology.tech_id)
        .filter(Prjtech.project_id == projectId)
        .filter(Technology.user_name == User.user_name)
        .order_by(Technology.tech_name)
        .all()
    )

    res = []
    for technology in result:
        res.append(
            {
                "tech_name": technology.tech_name,
                "user_name": technology.user_name,
                "project_id": technology[2].project_id,
                "tech_id": technology[2].tech_id,
                "quantity": technology.quantity,
                "quantityAlias": technology.quantityAlias,
                "user_fullname": technology[5],
            }
        )

    return res


def changeTheStateOfCreateComb(projectId, request):
    request.dbsession.query(Project).filter(Project.project_id == projectId).update(
        {"project_createcomb": 1}
    )


def addTechnologyProject(projectId, techId, request):

    newTechnologyProject = Prjtech(project_id=projectId, tech_id=techId)
    try:
        request.dbsession.add(newTechnologyProject)

        request.dbsession.query(Project).filter(Project.project_id == projectId).update(
            {"project_createcomb": 1}
        )

        return True, ""

    except Exception as e:
        print(str(e))
        return False, e


def deleteTechnologyProject(projectId, techId, request):
    try:
        request.dbsession.query(Prjtech).filter(Prjtech.tech_id == techId).filter(
            Prjtech.project_id == projectId
        ).delete()

        request.dbsession.query(Project).filter(Project.project_id == projectId).update(
            {"project_createcomb": 1}
        )

        return True, ""

    except Exception as e:
        print(str(e))
        return False, e


# -----------------------------------------Alises-------------------------------------------------------


def AliasSearchTechnology(technologyId, projectId, request):
    res = []
    subquery = (
        request.dbsession.query(Prjalia.alias_used)
        .filter(Prjalia.project_id == projectId)
        .filter(Prjalia.tech_id == technologyId)
        .filter(Prjalia.alias_name == "")
    )
    result = (
        request.dbsession.query(
            Technology,
            Techalia,
            func.coalesce(I18nTechalia.alias_name, Techalia.alias_name).label(
                "alias_name"
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
        .filter(Techalia.tech_id == Technology.tech_id)
        .filter(Technology.tech_id == technologyId)
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
                "alias_name": technology[2],
            }
        )

    return res


def AliasSearchTechnologyInProject(technologyId, projectId, request):
    res = []
    result = (
        request.dbsession.query(
            Prjalia,
            Techalia,
            func.coalesce(I18nTechalia.alias_name, Techalia.alias_name).label(
                "alias_name"
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
        .filter(Prjalia.project_id == projectId)
        .filter(Prjalia.tech_id == technologyId)
        .filter(Prjalia.alias_used == Techalia.alias_id)
        .filter(Prjalia.tech_used == Techalia.tech_id)
    )
    for technology in result:
        res.append(
            {
                "project_id": technology[0].project_id,
                "tech_idPrj": technology[0].tech_id,
                "alias_id": technology[0].alias_id,
                "alias_namePrj": technology[0].alias_name,
                "tech_used": technology[0].tech_used,
                "alias_used": technology[0].alias_used,
                "tech_idTec": technology[1].tech_id,
                "alias_idTec": technology[1].alias_id,
                "alias_name": technology[2],
            }
        )

    return res


def AliasExtraSearchTechnologyInProject(technologyId, projectId, request):
    res = []
    result = (
        request.dbsession.query(Prjalia)
        .filter(Prjalia.project_id == projectId)
        .filter(Prjalia.tech_id == technologyId)
        .filter(Prjalia.alias_name != "")
    )

    for alias in result:
        res.append(
            {
                "project_id": alias.project_id,
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
        project_id=data["project_id"],
        tech_id=data["tech_id"],
        tech_used=data["tech_id"],
        alias_used=data["alias_id"],
        alias_id=max_id.id_max + 1,
        alias_name="",
    )

    try:
        request.dbsession.add(newAliasTechnology)
        request.dbsession.flush()
        request.dbsession.query(Project).filter().filter(
            Project.project_id == data["project_id"]
        ).update({"project_createcomb": 1})

        return (
            True,
            mapFromSchema(
                request.dbsession.query(Prjalia)
                .filter(Prjalia.tech_id == data["tech_id"])
                .filter(Prjalia.project_id == data["project_id"])
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
            Project.project_id == data["project_id"]
        ).update({"project_createcomb": 1})

        return (
            True,
            mapFromSchema(
                request.dbsession.query(Prjalia)
                .filter(Prjalia.tech_id == data["tech_id"])
                .filter(Prjalia.project_id == data["project_id"])
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
        .filter(Prjalia.tech_id == data["tech_id"])
        .filter(Prjalia.project_id == data["project_id"])
        .filter(Prjalia.alias_id == data["alias_id"])
        .all()
    )
    if result:
        return True
    else:
        return False


def deleteAliasTechnology(projectId, techId, aliasId, request):
    try:
        request.dbsession.query(Prjalia).filter(Prjalia.tech_id == techId).filter(
            Prjalia.project_id == projectId
        ).filter(Prjalia.alias_id == aliasId).delete()
        request.dbsession.query(Project).filter(Project.project_id == projectId).update(
            {"project_createcomb": 1}
        )

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
            .filter(Prjalia.project_id == data["project_id"])
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


def numberOfCombinationsForTheProject(projectId, request):
    number = (
        request.dbsession.query(Project.project_numcom.label("numcom"))
        .filter(Project.project_id == projectId)
        .one()
    )

    if not number:
        return False
    else:
        return number.numcom


def numberOfAliasesInTechnology(projectId, technologyId, request):
    number = (
        request.dbsession.query(func.count(Prjalia.project_id).label("count"))
        .filter(Prjalia.project_id == projectId)
        .filter(Prjalia.tech_id == technologyId)
        .one()
    )

    if not number:
        return False
    else:
        return number.count
