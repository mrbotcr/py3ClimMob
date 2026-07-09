import json
import os
import shutil as sh

import climmob.plugins as p
from climmob.config.celery_app import celeryApp
from climmob.models.repository import create_request
from climmob.plugins.utilities import climmobCeleryTask

# TODO: Este se TIENE que ejecutar al hacer le request
@celeryApp.task(base=climmobCeleryTask)
def create_report_json_results(
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
    data = {
        "agricultural_record": {
            "farm": {
                "farm_id": projectId,
                "name": "Finca El Progreso",
                "location": {
                    "country": "Costa Rica",
                    "province": "Alajuela",
                    "district": "San Carlos",
                    "coordinates": {"latitude": 10.3269, "longitude": -84.4278},
                },
            },
        }
    }

    # TODO: run R script

    if os.path.exists(path):
        sh.rmtree(path)
    os.makedirs(path)
    pathout = os.path.join(path, "outputs")
    os.makedirs(pathout)

    file_path = os.path.join(pathout, "{}-{}.json".format(cropname, projectId))
    with open(file_path, "w") as outfile:
        json.dump(data, outfile, indent=4)

    with create_request(settings, locale, user_in_session) as request:
        p.load_all(settings)
        for plugin in p.PluginImplementations(p.IPublisher):
            if plugin.get_destination_name() in destinations:
                plugin.publish(settings, request, file_path, projectId, cropname)

    return ""
