from climmob.config.celery_app import celeryApp
from climmob.plugins.utilities import climmobCeleryTask
import os
import shutil as sh
import json
from .exportToCsv import createCSV

@celeryApp.task(base=climmobCeleryTask)
def create_CSV(path, info, projectid):

    if os.path.exists(path):
        sh.rmtree(path)

    os.makedirs(path)

    pathout = os.path.join(path, "outputs")
    os.makedirs(pathout)

    pathInputFiles = os.path.join(path, "inputFile")
    os.makedirs(pathInputFiles)

    with open(pathInputFiles + "/info.json", "w") as outfile:
        jsonString = json.dumps(info, indent=4, ensure_ascii=False)
        outfile.write(jsonString)

    if os.path.exists(pathInputFiles + "/info.json"):
        try:
            createCSV(pathout + "/Information_of_the project_"+projectid+".csv", pathInputFiles + "/info.json")
        except Exception as e:
            print("We can't create the CSV." + str(e))

    sh.rmtree(pathInputFiles)
