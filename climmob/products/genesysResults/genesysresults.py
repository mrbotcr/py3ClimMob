from climmob.products.climmob_products import (
    registerProductInstance,
    createProductDirectory,
)
from climmob.products.genesysResults.celerytasks import create_report_genesys_results
from climmob.utility import get_settings


def create_genesys_results(
    userOwner,
    projectId,
    projectCod,
    cropname,
    request,
):
    settings = get_settings(request)

    path = createProductDirectory(request, userOwner, projectCod, "genesys_results")
    task = create_report_genesys_results.apply_async(
        args=(
            settings,
            userOwner,
            projectId,
            projectCod,
            cropname,
            path,
        ),
        queue="ClimMob",
    )
    registerProductInstance(
        projectId,
        "genesys_results",  # TODO: Este es el archivo
        "{}-{}.json".format(cropname, projectId),
        "application/json",
        "genesys_results",
        task.id,
        request,
        newTask=False,
    )
