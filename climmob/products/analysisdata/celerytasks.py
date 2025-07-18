import os

import pandas as pd

from climmob.config.celery_app import celeryApp
from climmob.plugins.utilities import climmobCeleryTask
from climmob.products.analysisdata.exportToCsv import createCSV


@celeryApp.task(base=climmobCeleryTask)
def create_raw_data_file(path, info, name_output, file_type):

    path_out = os.path.join(path, "outputs")
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(path_out)

    # TODO replace labels

    df = pd.DataFrame(info)
    if file_type == "xlsx":
        df.to_excel(os.path.join(path_out, name_output) + f".{file_type}", index=False)
    elif file_type == "csv":
        df.to_csv(os.path.join(path_out, name_output) + f".{file_type}", index=False)


    # if os.path.exists(path):
    #    sh.rmtree(path)

    # nameOutput = form + "_data"
    # if code != "":
    #     nameOutput += "_" + code
    #
    # pathout = os.path.join(path, "outputs")
    # if not os.path.exists(path):
    #     os.makedirs(path)
    #     os.makedirs(pathout)
    #
    # if os.path.exists(pathout + "/" + nameOutput + "_" + projectCod + ".csv"):
    #     os.remove(pathout + "/" + nameOutput + "_" + projectCod + ".csv")
    #
    # pathInputFiles = os.path.join(path, "inputFile")
    # os.makedirs(pathInputFiles)
    #
    # with open(pathInputFiles + "/info.json", "w") as outfile:
    #     jsonString = json.dumps(info, indent=4, ensure_ascii=False)
    #     outfile.write(jsonString)
    #
    # if os.path.exists(pathInputFiles + "/info.json"):
    #     try:
    #         createCSV(
    #             pathout + "/" + nameOutput + "_" + projectCod + ".csv",
    #             pathInputFiles + "/info.json",
    #         )
    #     except Exception as e:
    #         print("We can't create the CSV." + str(e))
    #
    # sh.rmtree(pathInputFiles)
