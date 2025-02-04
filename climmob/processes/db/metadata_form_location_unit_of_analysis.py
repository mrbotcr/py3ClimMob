from climmob.models import mapToSchema, MetadaFormLocationUnitOfAnalysis, mapFromSchema
from climmob.processes.db.location_unit_of_analysis import (
    get_location_unit_of_analysis_by_pluoa_id,
)

__all__ = [
    "addMetadaFormLocationUnitOfAnalysis",
    "deleteMetadaFormLocationUnitOfAnalysisByMetadataForm",
    "getAllMetadaFormLocationUnitOfAnalysisByMetadataForm",
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


def getAllMetadaFormLocationUnitOfAnalysisByMetadataForm(request, metadataFormId):

    result = mapFromSchema(
        request.dbsession.query(MetadaFormLocationUnitOfAnalysis)
        .filter(MetadaFormLocationUnitOfAnalysis.metadata_id == metadataFormId)
        .all()
    )

    for info in result:
        info["InfoDetails"] = get_location_unit_of_analysis_by_pluoa_id(
            request, info["pluoa_id"]
        )

    return result
