from climmob.models import (
    ProjectMetadata,
    mapFromSchema,
    mapToSchema,
    CropTaxonomy,
)
from climmob.processes.db.technologies import getCropTaxonomyDetails

__all__ = ["getProjectMetadata", "addMetadata", "modifyMetadata"]


def getProjectMetadata(projectId, request):
    mappedData = mapFromSchema(
        request.dbsession.query(ProjectMetadata)
        .filter(ProjectMetadata.project_id == projectId)
        .first()
    )

    if mappedData:

        if mappedData["md_crops"]:

            mappedData["cropInfo"] = getCropTaxonomyDetails(
                mappedData["md_crops"], request
            )

    return mappedData


def addMetadata(data, request):

    mappedData = mapToSchema(ProjectMetadata, data)
    newProjectMetadata = ProjectMetadata(**mappedData)
    try:
        request.dbsession.add(newProjectMetadata)
        return True, ""
    except Exception as e:
        return False, str(e)


def modifyMetadata(projectId, data, request):
    mappedData = mapToSchema(ProjectMetadata, data)
    try:
        request.dbsession.query(ProjectMetadata).filter(
            ProjectMetadata.project_id == projectId
        ).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e
