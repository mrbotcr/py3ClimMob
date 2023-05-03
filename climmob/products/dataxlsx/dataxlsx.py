import climmob.plugins as p
from climmob.processes import (
    registryHaveQuestionOfMultimediaType,
    assessmentHaveQuestionOfMultimediaType,
)
from climmob.products.dataxlsx.celerytasks import create_XLSX
from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


def create_XLSXToDownload(userOwner, projectId, projectCod, request, form, code):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    settings = {}
    for key, value in request.registry.settings.items():
        if isinstance(value, str):
            settings[key] = value

    path = createProductDirectory(request, userOwner, projectCod, "dataxlsx")
    # We call the Celery task that will generate the output packages.pdf
    nameOutput = form + "_data"
    if code != "":
        nameOutput += "_" + code

    task = create_XLSX.apply_async(
        (
            settings,
            path,
            userOwner,
            projectCod,
            projectId,
            form,
            code,
            nameOutput + "_" + projectCod + ".xlsx",
        ),
        queue="ClimMob",
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)

    registerProductInstance(
        projectId,
        "dataxlsx",
        nameOutput + "_" + projectCod + ".xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "create_data_xlsx_" + form + "_" + code,
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
