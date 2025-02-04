from sqlalchemy import func, and_, or_
from climmob.models.climmobv4 import (
    Technology,
    Techalia,
    Prjtech,
    I18nTechnology,
    User,
    CropTaxonomy,
)
from climmob.models.schema import mapToSchema, mapFromSchema
from climmob.processes.db.techaliases import getTechsAlias

__all__ = [
    "getUserTechs",
    "findTechInLibrary",
    "addTechnology",
    "getTechnology",
    "updateTechnology",
    "deleteTechnology",
    "getTechnologyByUser",
    "getTechnologyAssigned",
    "technologyExist",
    "isTechnologyAssigned",
    "getTechnologyByName",
    "getUserTechById",
    "query_crops",
    "getTechnologiesByUserWithoutCropTaxonomy",
    "getCropTaxonomyDetails",
]


def getUserTechs(user, request):

    res = []
    result = mapFromSchema(
        request.dbsession.query(
            Technology,
            request.dbsession.query(func.count(Techalia.tech_id))
            .filter(Technology.tech_id == Techalia.tech_id)
            .label("quantity"),
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
        .filter(Technology.user_name == user)
        .filter(Technology.user_name == User.user_name)
        .order_by(Technology.tech_name)
        .all()
    )

    for technology in result:

        res3 = (
            request.dbsession.query(func.count(Prjtech.tech_id).label("found"))
            .filter(Prjtech.tech_id == technology["tech_id"])
            .one()
        )

        technology["tech_alias"] = getTechsAlias(technology["tech_id"], request)
        technology["found"] = res3.found
        res.append(technology)

    return res


def getUserTechById(tech_id, request):

    result = mapFromSchema(
        request.dbsession.query(
            Technology,
            request.dbsession.query(func.count(Techalia.tech_id))
            .filter(Technology.tech_id == Techalia.tech_id)
            .label("quantity"),
        )
        .filter(Technology.tech_id == tech_id)
        .one()
    )

    res3 = (
        request.dbsession.query(func.count(Prjtech.tech_id).label("found"))
        .filter(Prjtech.tech_id == tech_id)
        .one()
    )

    taxonomy_name = (
        request.dbsession.query(CropTaxonomy.taxonomy_name)
        .filter(CropTaxonomy.taxonomy_code == result["croptaxonomy_code"])
        .first()
    )

    result["taxonomy_name"] = taxonomy_name.taxonomy_name
    result["tech_alias"] = getTechsAlias(tech_id, request)
    result["found"] = res3.found

    return result


def findTechInLibrary(data, request, tech_id=None):
    if tech_id is None:
        result = (
            request.dbsession.query(Technology)
            .filter(
                Technology.user_name == data["user_name"],
                Technology.tech_name == data["tech_name"],
            )
            .all()
        )

        if not result:
            return False
        else:
            return True
    else:
        result = (
            request.dbsession.query(Technology)
            .filter(
                Technology.user_name == data["user_name"],
                Technology.tech_name == data["tech_name"],
                Technology.tech_id != tech_id,
            )
            .all()
        )

        if not result:
            return False
        else:
            return True


def addTechnology(data, request):
    mappeData = mapToSchema(Technology, data)
    newTech = Technology(**mappeData)
    try:
        request.dbsession.add(newTech)
        return True, ""

    except Exception as e:
        return False, e


def getTechnology(data, request):
    return mapFromSchema(
        request.dbsession.query(Technology)
        .filter(Technology.tech_id == data["tech_id"])
        .one()
    )


def technologyExist(techId, user, request):
    result = (
        request.dbsession.query(Technology)
        .filter(Technology.tech_id == techId)
        .filter(Technology.user_name == user)
        .first()
    )
    if result:
        return True
    else:
        result = (
            request.dbsession.query(Technology)
            .filter(Technology.tech_id == techId)
            .filter(Technology.user_name == "bioversity")
            .first()
        )
        if result:
            return True
        else:
            return False


def getTechnologyByName(data, request):
    return mapFromSchema(
        request.dbsession.query(Technology)
        .filter(
            Technology.user_name == data["user_name"],
            Technology.tech_name == data["tech_name"],
        )
        .one()
    )


def getTechnologyByUser(data, request):
    result = (
        request.dbsession.query(Technology)
        .filter(Technology.user_name == data["user_name"])
        .filter(Technology.tech_id == data["tech_id"])
        .all()
    )

    if not result:
        return False
    else:
        return True


def getTechnologyAssigned(data, request):
    result = (
        request.dbsession.query(func.count(Prjtech.tech_id).label("found"))
        .filter(Prjtech.tech_id == data["tech_id"])
        .one()
    )

    if result.found == 0:
        return False
    else:
        return True


def isTechnologyAssigned(data, request):
    result = (
        request.dbsession.query(func.count(Prjtech.tech_id).label("found"))
        .filter(Prjtech.tech_id == data["tech_id"])
        .filter(Prjtech.project_id == data["project_id"])
        .one()
    )

    if result.found == 0:
        return False
    else:
        return True


def updateTechnology(data, request):
    try:
        mappeData = mapToSchema(Technology, data)
        request.dbsession.query(Technology).filter(
            Technology.user_name == data["user_name"]
        ).filter(Technology.tech_id == data["tech_id"]).update(mappeData)
        return True, ""
    except Exception as e:
        return False, e


def deleteTechnology(data, request):
    try:
        request.dbsession.query(Technology).filter(
            Technology.user_name == data["user_name"]
        ).filter(Technology.tech_id == data["tech_id"]).delete()
        return True, ""

    except Exception as e:
        return False, e


def query_crops(request, q, query_from, query_size, lang_code="en"):
    query = q.replace("*", "")

    total = (
        request.dbsession.query(CropTaxonomy)
        .filter(CropTaxonomy.taxonomy_name.ilike("%" + query + "%"))
        .order_by(CropTaxonomy.taxonomy_name)
        .all()
    )

    result = (
        request.dbsession.query(CropTaxonomy)
        .filter(CropTaxonomy.taxonomy_name.ilike("%" + query + "%"))
        .order_by(CropTaxonomy.taxonomy_name)
        .offset(query_from)
        .limit(query_size)
        .all()
    )

    return mapFromSchema(result), len(total)


def getTechnologiesByUserWithoutCropTaxonomy(userId, request):

    result = (
        request.dbsession.query(Technology)
        .filter(Technology.user_name == userId)
        .filter(Technology.croptaxonomy_code == -1)
        .all()
    )

    if result:
        return False, result

    return True, result


def getCropTaxonomyDetails(cropTaxonomyId, request):

    cropTaxonomy = mapFromSchema(
        request.dbsession.query(CropTaxonomy)
        .filter(CropTaxonomy.taxonomy_code == cropTaxonomyId)
        .first()
    )

    return cropTaxonomy
