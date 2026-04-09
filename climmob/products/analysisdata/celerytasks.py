import os

import pandas as pd

from climmob.config.celery_app import celeryApp
from climmob.models.repository import create_request
from climmob.plugins.utilities import climmobCeleryTask
from climmob.processes import (
    getJSONResult,
    anonymize_project,
    set_project_anonymization_status,
)
from climmob.utility import AnonymizationStatus


@celeryApp.task(base=climmobCeleryTask)
def create_raw_data_file(
    request_attrs, project_id, file, result_params, start_anonymization=False
):
    print(f"PATH: {file['product_path']}")
    print(f"NAME_OUTPUT: {file['name']}")
    output_path = os.path.join(file["product_path"], "outputs")
    file_path = os.path.join(output_path, file["name"]) + f'.{file["type"]}'

    if os.path.exists(file_path):
        os.remove(file_path)

    with create_request(**request_attrs) as request:
        if start_anonymization:
            anonymization_status_id = AnonymizationStatus.IN_PROGRESS.value
            set_project_anonymization_status(
                project_id, anonymization_status_id, request
            )
            success, msg = anonymize_project(project_id, request)
            if success:
                anonymization_status_id = AnonymizationStatus.COMPLETED.value
                set_project_anonymization_status(
                    project_id, anonymization_status_id, request
                )
            else:
                # TODO: handle the error case
                pass
            pass

        result_params["request"] = request
        result = getJSONResult(**result_params)

    output_path = os.path.join(file["product_path"], "outputs")
    if not os.path.exists(file["product_path"]):
        os.makedirs(file["product_path"])
        os.makedirs(output_path)

    replace_options_with_labels(result)

    df = pd.DataFrame(result["data"])
    if file["type"] == "xlsx":
        df.to_excel(
            os.path.join(output_path, file["name"]) + f".{file['type']}",
            index=False,
        )
    elif file["type"] == "csv":
        df.to_csv(
            os.path.join(output_path, file["name"]) + f".{file['type']}",
            index=False,
        )


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
                    and row.get("ASS" + assessment["code"] + "_" + field["name"])
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
