from climmob.products.climmob_products import (
    registerProductInstance,
    createProductDirectory,
)

from climmob.products.jsonResults.celerytasks import create_report_json_results


def create_json_results(
    userapikey,
    locale,
    userOwner,
    projectId,
    projectCod,
    cropname,
    request,
):

    path = createProductDirectory(request, userOwner, projectCod, "jsonresults")
    task = create_report_json_results.apply_async(
        args=(
            userapikey,
            locale,
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
        "jsonresults",
        "{}-{}.json".format(cropname, projectId),
        "application/json",
        "jsonresults",
        task.id,
        request,
        newTask=False,
    )
