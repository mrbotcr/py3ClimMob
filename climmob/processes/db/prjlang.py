from sqlalchemy.exc import IntegrityError
from climmob.models import Prjlang, mapToSchema, mapFromSchema, I18n

__all__ = [
    "getPrjLangInProject",
    "addPrjLang",
    "deletePrjLang",
    "deleteAllPrjLang",
    "getPrjLangDefaultInProject",
    "languageExistInTheProject",
]


def getPrjLangInProject(projectId, request):

    mappedData = mapFromSchema(
        request.dbsession.query(Prjlang, I18n)
        .filter(Prjlang.project_id == projectId)
        .filter(Prjlang.lang_code == I18n.lang_code)
        .order_by(Prjlang.lang_default.desc())
        .all()
    )

    return mappedData


def languageExistInTheProject(projectId, language, request):

    mappedData = mapFromSchema(
        request.dbsession.query(Prjlang)
        .filter(Prjlang.project_id == projectId)
        .filter(Prjlang.lang_code == language)
        .first()
    )

    if mappedData:
        return True
    else:
        return False


def getPrjLangDefaultInProject(projectId, request):

    mappedData = mapFromSchema(
        request.dbsession.query(Prjlang)
        .filter(Prjlang.project_id == projectId)
        .filter(Prjlang.lang_default == 1)
        .first()
    )

    return mappedData


def addPrjLang(data, request):
    mappedData = mapToSchema(Prjlang, data)
    newPrjLang = Prjlang(**mappedData)
    try:
        request.dbsession.add(newPrjLang)
        return True, ""
    except Exception as e:
        return False, str(e)


def deletePrjLang(data, request):
    try:
        request.dbsession.query(Prjlang).filter(
            Prjlang.project_id == data["project_id"]
        ).filter(Prjlang.lang_code == data["lang_code"]).delete()
        return True, ""
    except IntegrityError as e:
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e


def deleteAllPrjLang(projectId, request):
    try:
        request.dbsession.query(Prjlang).filter(
            Prjlang.project_id == projectId
        ).delete()
        request.dbsession.flush()
        return True, ""
    except IntegrityError as e:
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e
