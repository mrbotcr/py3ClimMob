from climmob.products.climmob_products import (
    registerProductInstance,
    createProductDirectory,
)
from climmob.products.jsonResults.celerytasks import create_report_json_results
from climmob.utility import get_settings


def create_json_results(
    userapikey,
    userOwner,
    projectId,
    projectCod,
    cropname,
    request,
):
    path = createProductDirectory(request, userOwner, projectCod, "jsonresults")

    formatted = "{}-{}.json".format(cropname, projectId)
    file_path = os.path.join(path, "outputs", formatted)

    task = create_report_json_results.apply_async(
        args=(
            userapikey,
            userOwner,
            projectId,
            projectCod,
            cropname,
            file_path,
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
