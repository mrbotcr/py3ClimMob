from climmob.models import mapFromSchema, generalPhrases

__all__ = ["getListOfGeneralPhrases"]


def getListOfGeneralPhrases(request):
    mappedData = mapFromSchema(
        request.dbsession.query(generalPhrases).order_by(generalPhrases.phrase_id).all()
    )
    return mappedData
