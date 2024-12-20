from climmob.models import MetadataForm, mapToSchema, mapFromSchemaWithRelationships
from climmob.processes.db.project_metadata_form import getProjectMetadataForm

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
    _query = request.dbsession.query(MetadataForm).order_by(MetadataForm.metadata_name).all()
    result = mapFromSchemaWithRelationships(_query)
    return result


def getMetadataForm(request, metadataFormId):
    resultQuery = (
        request.dbsession.query(MetadataForm)
        .filter(MetadataForm.metadata_id == metadataFormId)
        .first()
    )
    result = mapFromSchemaWithRelationships(resultQuery)

    return result


"""
    ADAPATAR LOS FILTROS POR LOS NECESARIOS
"""


def getMetadataForProject(request, projectId):

    result = mapFromSchemaWithRelationships(
        request.dbsession.query(MetadataForm)
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
