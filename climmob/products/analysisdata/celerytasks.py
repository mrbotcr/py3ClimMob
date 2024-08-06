import json
import os
import shutil as sh

from climmob.config.celery_app import celeryApp
from climmob.plugins.utilities import climmobCeleryTask
from climmob.products.analysisdata.exportToCsv import createCSV


@celeryApp.task(base=climmobCeleryTask)
def create_CSV(path, info, projectCod, form, code, nameOutput):

    # if os.path.exists(path):
    #    sh.rmtree(path)

    pathout = os.path.join(path, "outputs")
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(pathout)

    if os.path.exists(pathout + "/" + nameOutput + "_" + projectCod + ".csv"):
        os.remove(pathout + "/" + nameOutput + "_" + projectCod + ".csv")

    pathInputFiles = os.path.join(path, "inputFile")
    os.makedirs(pathInputFiles)

    with open(pathInputFiles + "/info.json", "w") as outfile:
        jsonString = json.dumps(info, indent=4, ensure_ascii=False)
        outfile.write(jsonString)

    if os.path.exists(pathInputFiles + "/info.json"):
        try:
            createCSV(
                pathout + "/" + nameOutput + "_" + projectCod + ".csv",
                pathInputFiles + "/info.json",
            )
        except Exception as e:
            print("We can't create the CSV." + str(e))

    sh.rmtree(pathInputFiles)
