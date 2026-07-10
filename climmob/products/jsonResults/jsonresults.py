from climmob.products.climmob_products import (
    registerProductInstance,
    createProductDirectory,
)
from climmob.products.jsonResults.celerytasks import create_report_json_results
from climmob.utility import get_settings


def create_json_results(
    userapikey,
    locale,
    user_in_session,
    userOwner,
    projectId,
    projectCod,
    cropname,
    destinations,
    request,
):
    settings = get_settings(request)

    path = createProductDirectory(request, userOwner, projectCod, "jsonresults")
    task = create_report_json_results.apply_async(
        args=(
            settings,
            userapikey,
            locale,
            user_in_session,
            userOwner,
            projectId,
            projectCod,
            cropname,
            path,
            destinations,
        ),
        queue="ClimMob",
    )
    registerProductInstance(
        projectId,
        "jsonresults",  # TODO: Este es el archivo
        "{}-{}.json".format(cropname, projectId),
        "application/json",
        "jsonresults",
        task.id,
        request,
        newTask=False,
    )
