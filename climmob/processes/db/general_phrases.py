from climmob.models import mapFromSchema, generalPhrases

__all__ = ["getListOfGeneralPhrases", "generalPhraseExistsWithID"]


def getListOfGeneralPhrases(request):
    mappedData = mapFromSchema(
        request.dbsession.query(generalPhrases).order_by(generalPhrases.phrase_id).all()
    )
    return mappedData


def generalPhraseExistsWithID(request, phraseId):
    mappedData = mapFromSchema(
        request.dbsession.query(generalPhrases)
        .filter(generalPhrases.phrase_id == phraseId)
        .first()
    )

    if mappedData:
        return True

    return False
