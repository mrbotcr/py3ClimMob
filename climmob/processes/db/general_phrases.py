from climmob.models import mapFromSchema, generalPhrases

__all__ = ["getListOfGeneralPhrases", "generalPhraseExistsWithID", "generalPhraseByID"]


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


def generalPhraseByID(request, phraseId, dbsession=None):

    if request and not dbsession:
        _DBsession_ = request.dbsession
    if dbsession and not request:
        _DBsession_ = dbsession

    mappedData = mapFromSchema(
        _DBsession_.query(generalPhrases)
        .filter(generalPhrases.phrase_id == phraseId)
        .first()
    )
    return mappedData
