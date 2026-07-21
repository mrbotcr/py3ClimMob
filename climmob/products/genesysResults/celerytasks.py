import os
import shutil
from pathlib import Path

from climmob.config.celery_app import celeryApp
from climmob.models.repository import create_request
from climmob.plugins.utilities import climmobCeleryTask
from climmob.products.climmob_products import (
    createProductDirectory,
    getProductDirectory,
)


@celeryApp.task(base=climmobCeleryTask)
def create_genesys_results_task(request_attrs, project):
    with create_request(**request_attrs) as request:
        path = getProductDirectory(
            request,
            project["owner"]["user_name"],
            project["project_cod"],
            "jsonresults",
        )
        formatted = "{}-{}.json".format(
            project["project_curated_cropname"], project["project_id"]
        )
        jsonresults_path = os.path.join(path, "outputs", formatted)

        path = createProductDirectory(
            request,
            project["owner"]["user_name"],
            project["project_cod"],
            "genesys_results",
        )
        formatted = "{}-{}.json".format(
            project["project_curated_cropname"], project["project_id"]
        )
        genesys_path = os.path.join(path, "outputs", formatted)

    Path(genesys_path).parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(jsonresults_path, genesys_path)

    return ""
