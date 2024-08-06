import climmob.plugins as p
from climmob.processes import (
    registryHaveQuestionOfMultimediaType,
    assessmentHaveQuestionOfMultimediaType,
)
from climmob.products.analysisdata.celerytasks import create_CSV
from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


def create_datacsv(
    userOwner, projectId, projectCod, info, request, form, code, dataPrivacy=False
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    if dataPrivacy:
        nameOutput = form + "_dataprivacy"
        productName = "dataprivacycsv"
        productCreate = "create_dataprivacy_" + form + "_" + code
    else:
        nameOutput = form + "_data"
        productName = "datacsv"
        productCreate = "create_data_" + form + "_" + code

    if code != "":
        nameOutput += "_" + code

    path = createProductDirectory(request, userOwner, projectCod, productName)
    # We call the Celery task that will generate the output packages.pdf
    task = create_CSV.apply_async(
        (path, info, projectCod, form, code, nameOutput), queue="ClimMob"
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)

    registerProductInstance(
        projectId,
        productName,
        nameOutput + "_" + projectCod + ".csv",
        "text/csv",
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
