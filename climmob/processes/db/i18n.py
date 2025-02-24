from climmob.models import mapFromSchema, I18n

__all__ = [
    "getListOfLanguages",
    "getListOfLanguagesInClimMob",
    "languageExistInI18n",
    "languageByLanguageCode",
]


def getListOfLanguages(request):
    mappedData = mapFromSchema(
        request.dbsession.query(I18n).order_by(I18n.lang_name).all()
    )
    return mappedData


def getListOfLanguagesInClimMob(request):
    mappedData = mapFromSchema(
        request.dbsession.query(I18n)
        .filter(I18n.lang_in_climmob == 1)
        .order_by(I18n.lang_name)
        .all()
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


def languageByLanguageCode(languageCode, request):

    mappedData = mapFromSchema(
        request.dbsession.query(
            I18n,
        )
        .filter(I18n.lang_code == languageCode)
        .first()
    )

    return mappedData
