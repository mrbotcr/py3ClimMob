import json
import os
import shutil as sh
from pathlib import Path

import climmob.plugins as p
from climmob.config.celery_app import celeryApp
from climmob.models.repository import create_request
from climmob.plugins.utilities import climmobCeleryTask


@celeryApp.task(base=climmobCeleryTask)
def create_report_json_results(
    userapikey,
    userOwner,
    projectId,
    projectCod,
    cropname,
    file_path,  # {user}/{project_cod}/products/jsonresults/outputs/{crop_name}-{project_id}.json
):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

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

    try:
        # TODO: run R script

        with open(file_path, "w") as outfile:
            print(f"WRITING INTO {file_path}")
            json.dump(data, outfile, indent=4)
    except Exception as e:
        return False, e

    return True, ""
