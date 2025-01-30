from climmob.models import MetadataForm, mapToSchema, mapFromSchema
from climmob.processes.db.project_metadata_form import getProjectMetadataForm
from climmob.processes.db.metadata_form_location_unit_of_analysis import (
    getAllMetadaFormLocationUnitOfAnalysisByMetadataForm,
)

__all__ = [
    "addMetadataForm",
    "getAllMetadata",
    "getMetadataForm",
    "getMetadataForProject",
    "deleteMetadataForm",
    "modifyMetadataForm",
]


def addMetadataForm(data, request):
    mappedData = mapToSchema(MetadataForm, data)
    newMetadataForm = MetadataForm(**mappedData)
    try:
        request.dbsession.add(newMetadataForm)
        return True, ""
    except Exception as e:
        return False, str(e)


def getAllMetadata(request):
    _query = (
        request.dbsession.query(
            MetadataForm.metadata_id,
            MetadataForm.metadata_name,
            MetadataForm.metadata_active,
        )
        .order_by(MetadataForm.metadata_name)
        .all()
    )
    result = mapFromSchema(_query)

    for metadata in result:

        metadata["InfoDetails"] = getAllMetadaFormLocationUnitOfAnalysisByMetadataForm(
            request, metadata["metadata_id"]
        )

    return result


def getMetadataForm(request, metadataFormId):
    resultQuery = (
        request.dbsession.query(MetadataForm)
        .filter(MetadataForm.metadata_id == metadataFormId)
        .first()
    )
    result = mapFromSchema(resultQuery)

    result["InfoDetails"] = getAllMetadaFormLocationUnitOfAnalysisByMetadataForm(
        request, result["metadata_id"]
    )

    return result


"""
    ADAPATAR LOS FILTROS POR LOS NECESARIOS
"""


def getMetadataForProject(request, projectId):

    result = mapFromSchema(
        request.dbsession.query(MetadataForm.metadata_id, MetadataForm.metadata_name)
        .filter(MetadataForm.metadata_active == 1)
        .order_by(MetadataForm.metadata_name)
        .all()
    )
    for info in result:

        info["result"] = getProjectMetadataForm(request, projectId, info["metadata_id"])

    return result


def modifyMetadataForm(request, metadataId, data):
    try:
        mappedData = mapToSchema(MetadataForm, data)
        request.dbsession.query(MetadataForm).filter(
            MetadataForm.metadata_id == metadataId
        ).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e


def deleteMetadataForm(request, metadataFormId):
    try:
        request.dbsession.query(MetadataForm).filter(
            MetadataForm.metadata_id == metadataFormId
        ).delete()
        return True, ""
    except Exception as e:
        return False, e
