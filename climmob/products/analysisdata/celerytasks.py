import os

import pandas as pd

from climmob.config.celery_app import celeryApp
from climmob.plugins.utilities import climmobCeleryTask


@celeryApp.task(base=climmobCeleryTask)
def create_raw_data_file(path, info, name_output, file_type):

    path_out = os.path.join(path, "outputs")
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(path_out)

    replace_options_with_labels(info)

    df = pd.DataFrame(info["data"])
    if file_type == "xlsx":
        df.to_excel(os.path.join(path_out, name_output) + f".{file_type}", index=False)
    elif file_type == "csv":
        df.to_csv(os.path.join(path_out, name_output) + f".{file_type}", index=False)


def replace_options_with_labels(data):
    for row in data["data"]:
        for field in data["registry"]["fields"]:
            if field["rtable"] is not None and row["REG_" + field["name"]] is not None:
                result = get_option_label(
                    data["registry"]["lkptables"],
                    field["rtable"],
                    field["rfield"],
                    row["REG_" + field["name"]],
                    field["isMultiSelect"],
                )
                row["REG_" + field["name"]] = result

        for assessment in data["assessments"]:
            for field in assessment["fields"]:
                if (
                    field["rtable"] is not None
                    and row["ASS" + assessment["code"] + "_" + field["name"]]
                    is not None
                ):
                    result = get_option_label(
                        assessment["lkptables"],
                        field["rtable"],
                        field["rfield"],
                        row["ASS" + assessment["code"] + "_" + field["name"]],
                        field["isMultiSelect"],
                    )
                    row["ASS" + assessment["code"] + "_" + field["name"]] = result


def get_option_label(lkptables, rtable, rfield, value, isMultiSelect):
    res = None
    for lkp in lkptables:
        if lkp["name"] == rtable:
            for data in lkp["values"]:
                if isMultiSelect == "true":
                    for valueSplit in value.split(" "):
                        if str(data[rfield]) == str(valueSplit):
                            if res == None:
                                res = data[rfield[:-3] + "des"]
                            else:
                                res += " - " + data[rfield[:-3] + "des"]
                else:
                    if data[rfield] == value:
                        res = data[rfield[:-3] + "des"]
                        break

    return res
