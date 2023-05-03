from climmob.models import mapFromSchema, I18n

__all__ = ["getListOfLanguages"]


def getListOfLanguages(request):
    mappedData = mapFromSchema(
        request.dbsession.query(I18n).order_by(I18n.lang_name).all()
    )
    return mappedData
