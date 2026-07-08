import json
import os
import shutil as sh

import climmob.plugins as p
from climmob.config.celery_app import celeryApp
from climmob.models.repository import create_request
from climmob.plugins.utilities import climmobCeleryTask


@celeryApp.task(base=climmobCeleryTask)
def create_report_genesys_results(
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
):
    pathout = os.path.join(path, "outputs")
    if os.path.exists(pathout):
        sh.rmtree(pathout)
    os.makedirs(pathout)

    # TODO: copiar el jsonresults, que se asume que ya existe

    return ""
