from climmob.processes.db.project import get_project_by_id
from climmob.products.climmob_products import (
    registerProductInstance,
)
from climmob.products.genesysResults.celerytasks import create_genesys_results_task
from climmob.utility import get_settings


def create_genesys_results(
    project_id,
    request,
):
    settings = get_settings(request)

    request_attrs = {
        "settings": settings,
        "locale_name": request.locale_name,
        "user_in_session": request.user_in_session,
    }

    project = get_project_by_id(project_id, request)

    task = create_genesys_results_task.apply_async(
        args=(request_attrs, project),
        queue="ClimMob",
    )
    registerProductInstance(
        project_id,
        "genesys_results",
        "{}-{}.json".format(project["project_curated_cropname"], project_id),
        "application/json",
        "genesys_results",
        task.id,
        request,
        newTask=False,
    )
