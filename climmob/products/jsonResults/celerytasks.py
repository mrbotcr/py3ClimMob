import json
import os
import shutil as sh

import climmob.plugins as p
from climmob.config.celery_app import celeryApp
from climmob.plugins.utilities import climmobCeleryTask


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

    if os.path.exists(path):
        sh.rmtree(path)
    os.makedirs(path)
    pathout = os.path.join(path, "outputs")
    os.makedirs(pathout)

    file_path = os.path.join(pathout, "{}-{}.json".format(cropname, projectId))
    with open(file_path, "w") as outfile:
        json.dump(data, outfile, indent=4)

    p.load_all(settings)
    for plugin in p.PluginImplementations(p.IPublisher):
        if plugin.get_destination_name() in destinations:
            plugin.publish(settings, user_in_session, file_path, projectId, cropname)

    return ""
