import climmob.plugins as p
from climmob.processes import (
    registryHaveQuestionOfMultimediaType,
    assessmentHaveQuestionOfMultimediaType,
)
from climmob.products.analysisdata.celerytasks import create_export
from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


def create_data_export(
    userOwner,
    projectId,
    projectCod,
    info,
    request,
    form,
    code,
    formatId,
    dataPrivacy=False,
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    formatExtra = ""
    if formatId == "xlsx":
        formatExtra = formatId + "_"

    if dataPrivacy:
        nameOutput = form + "_dataprivacy"
        productName = "dataprivacy" + formatId
        productCreate = "create_dataprivacy_" + formatExtra + form + "_" + code
    else:
        nameOutput = form + "_data"
        productName = "data" + formatId
        productCreate = "create_data_" + formatExtra + form + "_" + code

    if code != "":
        nameOutput += "_" + code

    path = createProductDirectory(request, userOwner, projectCod, productName)
    # We call the Celery task that will generate the output packages.pdf
    task = create_export.apply_async(
        (path, info, projectCod, formatId, nameOutput), queue="ClimMob"
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)

    if formatId == "csv":
        registerProductInstance(
            projectId,
            productName,
            nameOutput + "_" + projectCod + ".csv",
            "text/csv",
            productCreate,
            task.id,
            request,
        )

    if formatId == "xlsx":

        registerProductInstance(
            projectId,
            productName,
            nameOutput + "_" + projectCod + ".xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            productCreate,
            task.id,
            request,
        )

    for plugin in p.PluginImplementations(p.IMultimedia):
        thereAreMultimedia = False
        if form == "Registration":
            thereAreMultimedia = registryHaveQuestionOfMultimediaType(
                request, projectId
            )

        if form == "Assessment":
            thereAreMultimedia = assessmentHaveQuestionOfMultimediaType(
                request, projectId, code
            )

        if thereAreMultimedia:
            plugin.start_multimedia_download(
                request, userOwner, projectId, projectCod, form, code
            )
