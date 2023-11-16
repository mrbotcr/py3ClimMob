from climmob.models import (
    ProjectMetadata,
    mapFromSchema,
    mapToSchema,
    I18nCropTaxonomy,
    CropTaxonomy,
)

__all__ = ["getProjectMetadata", "addMetadata", "modifyMetadata"]


def getProjectMetadata(projectId, request, langcode="en"):
    mappedData = mapFromSchema(
        request.dbsession.query(ProjectMetadata)
        .filter(ProjectMetadata.project_id == projectId)
        .first()
    )

    if mappedData:

        if mappedData["md_crops"]:

            mappedData["cropInfo"] = mapFromSchema(
                request.dbsession.query(CropTaxonomy, I18nCropTaxonomy)
                .filter(I18nCropTaxonomy.taxonomy_code == mappedData["md_crops"])
                .filter(I18nCropTaxonomy.lang_code == langcode)
                .filter(CropTaxonomy.taxonomy_code == I18nCropTaxonomy.taxonomy_code)
                .first()
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
