from climmob.models import (
    ProjectMetadataForm,
    MetadataForm,
    mapToSchema,
    mapFromSchemaWithRelationships,
)

__all__ = [
    "addProjectMetadataForm",
    "getProjectMetadataForm",
    "modifyProjectMetadataForm",
    "knowIfTheProjectMetadataIsComplete",
]


def addProjectMetadataForm(data, request):
    mappedData = mapToSchema(ProjectMetadataForm, data)
    newProjectMetadataForm = ProjectMetadataForm(**mappedData)
    try:
        request.dbsession.add(newProjectMetadataForm)
        return True, ""
    except Exception as e:
        return False, str(e)


def getProjectMetadataForm(request, projectId, metadataFormId):
    result = mapFromSchemaWithRelationships(
        request.dbsession.query(ProjectMetadataForm)
        .filter(ProjectMetadataForm.project_id == projectId)
        .filter(ProjectMetadataForm.metadata_id == metadataFormId)
        .first()
    )
    return result


def modifyProjectMetadataForm(request, projectId, metadataFormId, data):
    try:
        mappedData = mapToSchema(ProjectMetadataForm, data)
        request.dbsession.query(ProjectMetadataForm).filter(
            ProjectMetadataForm.project_id == projectId
        ).filter(ProjectMetadataForm.metadata_id == metadataFormId).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e


def knowIfTheProjectMetadataIsComplete(request, projectId):
    result = mapFromSchemaWithRelationships(request.dbsession.query(MetadataForm).all())
    quantityRequired = len(result)
    quantityCompleted = 0
    for metadata in result:
        for project in metadata["project_metadata_form"]:
            if project["project_id"] == projectId:
                quantityCompleted = quantityCompleted + 1

    return quantityRequired, quantityCompleted
