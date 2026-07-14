from climmob.plugins.utilities import getProductDirectory
from climmob.products.projectPublication.celerytasks import publish_project_task
from climmob.utility import get_settings


def publish_project(
    project_id,
    owner_username,
    cropname,
    destinations,
    request,
):
    settings = get_settings(request)
    product_directory = getProductDirectory(
        request, owner_username, project_id, "jsonresults"
    )
    task = publish_project_task.apply_async(
        args=(
            settings,
            request.locale_name,
            request.user_in_session,
            cropname,
            project_id,
            owner_username,
            destinations,
            product_directory,
        ),
        queue="ClimMob",
    )
