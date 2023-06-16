from climmob.models import mapFromSchema, I18n

__all__ = ["getListOfLanguages", "languageExistInI18n"]


def getListOfLanguages(request):
    mappedData = mapFromSchema(
        request.dbsession.query(I18n).order_by(I18n.lang_name).all()
    )
    return mappedData


def languageExistInI18n(language, request):

    mappedData = mapFromSchema(
        request.dbsession.query(
            I18n,
        )
        .filter(I18n.lang_code == language)
        .all()
    )

    if mappedData:
        return True

    return False
