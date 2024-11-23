from climmob.models import (
    ProjectMetadataForm,
    mapToSchema,
    mapFromSchemaWithRelationships,
)

__all__ = [
    "addProjectMetadataForm",
    "getProjectMetadataForm",
    "modifyProjectMetadataForm",
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
