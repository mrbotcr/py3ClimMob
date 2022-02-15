from climmob.models import (
    Enumerator,
    mapToSchema,
    mapFromSchema,
    PrjEnumerator,
    userProject,
)
from climmob.config.encdecdata import encodeData, decodeData
from sqlalchemy.exc import IntegrityError

__all__ = [
    "searchEnumerator",
    "enumeratorExists",
    "addEnumerator",
    "modifyEnumerator",
    "deleteEnumerator",
    "isEnumeratorPassword",
    "getEnumeratorData",
    "modifyEnumeratorPassword",
    "isEnumeratorActive",
    "getEnumeratorPassword",
    "isEnumeratorinProject",
    "isEnumeratorAssigned",
    "countEnumerators",
    "getEnumeratorByProject",
    "countEnumeratorsOfAllCollaborators",
]


def searchEnumerator(user, request):
    result = (
        request.dbsession.query(Enumerator).filter(Enumerator.user_name == user).all()
    )
    res = mapFromSchema(result)
    result = []
    for enum in res:
        enum["enum_password"] = decodeData(request, enum["enum_password"]).decode(
            "utf-8"
        )
        result.append(enum)
    return result


def countEnumerators(user, request):
    result = (
        request.dbsession.query(Enumerator).filter(Enumerator.user_name == user).count()
    )
    return result


def countEnumeratorsOfAllCollaborators(projectId, request):

    projectCollaborators = request.dbsession.query(userProject.user_name).filter(
        userProject.project_id == projectId
    )

    result = (
        request.dbsession.query(Enumerator)
        .filter(Enumerator.user_name.in_(projectCollaborators))
        .count()
    )

    return result


def enumeratorExists(user, id, request):
    result = (
        request.dbsession.query(Enumerator)
        .filter(Enumerator.user_name == user)
        .filter(Enumerator.enum_id == id)
        .first()
    )
    if result:
        return True
    else:
        return False


def getEnumeratorPassword(user, enumerator, request):
    result = (
        request.dbsession.query(Enumerator)
        .filter(Enumerator.enum_id == enumerator)
        .filter(Enumerator.user_name == user)
        .first()
    )
    return decodeData(request, result.enum_password)


def isEnumeratorActive(user, enumerator, request):
    result = (
        request.dbsession.query(Enumerator)
        .filter(Enumerator.enum_id == enumerator)
        .filter(Enumerator.user_name == user)
        .filter(Enumerator.enum_active == 1)
        .first()
    )
    if result:
        return True
    else:
        return False


def isEnumeratorinProject(projectId, enumeratorId, request):
    result = (
        request.dbsession.query(Enumerator)
        .filter(Enumerator.enum_id == enumeratorId)
        .filter(Enumerator.enum_active == 1)
        .first()
    )
    if result:
        result = (
            request.dbsession.query(PrjEnumerator)
            .filter(PrjEnumerator.enum_id == enumeratorId)
            .filter(PrjEnumerator.project_id == projectId)
            .first()
        )
        if result:
            return True
        else:
            return False
    else:
        return False


def isEnumeratorAssigned(user, projectId, enumerator, request):
    result = (
        request.dbsession.query(Enumerator)
        .filter(Enumerator.enum_id == enumerator)
        .filter(Enumerator.user_name == user)
        .filter(Enumerator.enum_active == 1)
        .first()
    )
    if result:
        result = (
            request.dbsession.query(PrjEnumerator)
            .filter(PrjEnumerator.enum_user == user)
            .filter(PrjEnumerator.enum_id == enumerator)
            .filter(PrjEnumerator.project_id == projectId)
            .first()
        )
        if not result:
            return True
        else:
            return False
    else:
        return False


def getEnumeratorData(user, id, request):
    res = (
        request.dbsession.query(Enumerator)
        .filter(Enumerator.user_name == user)
        .filter(Enumerator.enum_id == id)
        .first()
    )
    result = mapFromSchema(res)
    if result:
        result["enum_password"] = decodeData(request, result["enum_password"]).decode(
            "utf-8"
        )
    return result


def getEnumeratorByProject(projectId, id, request):
    res = (
        request.dbsession.query(Enumerator)
        .filter(PrjEnumerator.project_id == projectId)
        .filter(Enumerator.user_name == PrjEnumerator.enum_user)
        .filter(Enumerator.enum_id == id)
        .first()
    )
    result = mapFromSchema(res)

    return result


def addEnumerator(user, data, request):
    data["enum_active"] = 1
    data["enum_password"] = encodeData(request, data["enum_password"])
    data["user_name"] = user
    mappedData = mapToSchema(Enumerator, data)
    newProjectEnumerator = Enumerator(**mappedData)
    try:
        request.dbsession.add(newProjectEnumerator)
        return True, ""
    except Exception as e:
        return False, str(e)


def modifyEnumerator(user, id, data, request):
    mappedData = mapToSchema(Enumerator, data)
    try:
        request.dbsession.query(Enumerator).filter(Enumerator.user_name == user).filter(
            Enumerator.enum_id == id
        ).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e


def modifyEnumeratorPassword(user, id, password, request):
    try:
        request.dbsession.query(Enumerator).filter(Enumerator.user_name == user).filter(
            Enumerator.enum_id == id
        ).update({"enum_password": encodeData(request, password)})
        return True, ""
    except Exception as e:
        return False, e


def deleteEnumerator(user, enumerator, request):
    try:
        request.dbsession.query(Enumerator).filter(Enumerator.user_name == user).filter(
            Enumerator.enum_id == enumerator
        ).delete()
        return True, ""
    except IntegrityError as e:
        print("capturado")
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e


def isEnumeratorPassword(user, enumerator, password, request):
    result = (
        request.dbsession.query(Enumerator.enum_password)
        .filter(Enumerator.user_name == user)
        .filter(Enumerator.enum_id == enumerator)
        .filter(Enumerator.enum_password == encodeData(request, password))
        .first()
    )
    if not result:
        return False
    else:
        return True
