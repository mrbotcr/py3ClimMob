from ...models import Enumerator, mapToSchema, mapFromSchema, PrjEnumerator
from climmob.config.encdecdata import encodeData, decodeData

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


def isEnumeratorinProject(user, project, enumerator, request):
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
            .filter(PrjEnumerator.enum_id == enumerator)
            .filter(PrjEnumerator.user_name == user)
            .filter(PrjEnumerator.project_cod == project)
            .first()
        )
        if result:
            return True
        else:
            return False
        return True
    else:
        return False


def isEnumeratorAssigned(user, project, enumerator, request):
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
            .filter(PrjEnumerator.enum_id == enumerator)
            .filter(PrjEnumerator.user_name == user)
            .filter(PrjEnumerator.project_cod == project)
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
    return mapFromSchema(res)


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
    except Exception as e:
        #print(str(e))
        return False, e


def isEnumeratorPassword(user, enumerator, password, request):
    result = (
        request.dbsession.query(Enumerator.enum_password)
        .filter(Enumerator.user_name == user)
        .filter(Enumerator.enum_id == enumerator)
        .filter(Enumerator.enum_password == encodeData(password))
        .first()
    )
    if not result:
        return False
    else:
        return True
