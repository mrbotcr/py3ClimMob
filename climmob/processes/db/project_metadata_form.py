from climmob.models import (
    ProjectMetadataForm,
    MetadataForm,
    mapToSchema,
    mapFromSchema,
)
from sqlalchemy import func

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
    result = mapFromSchema(
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
    quantityRequired = mapFromSchema(
        request.dbsession.query(
            func.count(MetadataForm.metadata_id).label("quantity_required")
        ).one()
    )
    quantityCompleted = mapFromSchema(
        request.dbsession.query(
            func.count(ProjectMetadataForm.project_id).label("quantity_completed")
        )
        .filter(ProjectMetadataForm.project_id == projectId)
        .one()
    )
    return (
        quantityRequired["quantity_required"],
        quantityCompleted["quantity_completed"],
    )
