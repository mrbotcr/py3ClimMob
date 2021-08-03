from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)
from .celerytasks import create_CSV
import climmob.plugins as p
from ...processes import (
    registryHaveQuestionOfMultimediaType,
    assessmentHaveQuestionOfMultimediaType,
)


def create_datacsv(user, project, info, request, form, code):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, user, project, "datacsv")
    # We call the Celery task that will generate the output packages.pdf
    task = create_CSV.apply_async((path, info, project, form, code), queue="ClimMob")
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)
    nameOutput = form + "_data"
    if code != "":
        nameOutput += "_" + code

    registerProductInstance(
        user,
        project,
        "datacsv",
        nameOutput + "_" + project + ".csv",
        "text/csv",
        "create_data_" + form + "_" + code,
        task.id,
        request,
    )

    for plugin in p.PluginImplementations(p.IMultimedia):
        thereAreMultimedia = False
        if form == "Registration":
            thereAreMultimedia = registryHaveQuestionOfMultimediaType(
                request, user, project
            )

        if form == "Assessment":
            thereAreMultimedia = assessmentHaveQuestionOfMultimediaType(
                request, user, project, code
            )

        if thereAreMultimedia:
            plugin.start_multimedia_download(request, user, project, form, code)
