from climmob.models import mapToSchema, MetadaFormLocationUnitOfAnalysis

__all__ = [
    "addMetadaFormLocationUnitOfAnalysis",
    "deleteMetadaFormLocationUnitOfAnalysisByMetadataForm",
]


def addMetadaFormLocationUnitOfAnalysis(data, request):
    mappedData = mapToSchema(MetadaFormLocationUnitOfAnalysis, data)
    newMetadaFormLocationUnitOfAnalysis = MetadaFormLocationUnitOfAnalysis(**mappedData)
    try:
        request.dbsession.add(newMetadaFormLocationUnitOfAnalysis)
        return True, ""
    except Exception as e:
        return False, str(e)


def deleteMetadaFormLocationUnitOfAnalysisByMetadataForm(request, metadataFormId):
    try:
        request.dbsession.query(MetadaFormLocationUnitOfAnalysis).filter(
            MetadaFormLocationUnitOfAnalysis.metadata_id == metadataFormId
        ).delete()
        return True, ""
    except Exception as e:
        return False, e
