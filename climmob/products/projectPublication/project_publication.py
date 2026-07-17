import os

from climmob.plugins.utilities import getProductDirectory
from climmob.products.projectPublication.celerytasks import publish_project_task
from climmob.utility import get_settings


def publish_project(
    project_id,
    project_cod,
    owner_username,
    cropname,
    destinations,
    request,
    notify=True,
):
    settings = get_settings(request)
    product_directory = getProductDirectory(
        request, owner_username, project_cod, "jsonresults"
    )
    formatted = "{}-{}.json".format(cropname, project_id)
    file_path = os.path.join(product_directory, "outputs", formatted)
    publish_project_task.apply_async(
        args=(
            settings,
            request.locale_name,
            request.user_in_session,
            cropname,
            project_id,
            owner_username,
            destinations,
            file_path,
            notify,
        ),
        queue="ClimMob",
    )
