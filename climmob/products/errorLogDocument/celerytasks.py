import gettext
import json
import os

import pandas as pd

from climmob.config.celery_app import celeryApp
from climmob.config.celery_class import celeryTask
from climmob.products.analysisdata.exportToCsv import getRealData


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createErrorLogDocument(
    locale, user, path, project, form, code, structure, listOfErrors, info
):
    if not os.path.exists(path):
        os.makedirs(path)

    PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    this_file_path = PATH + "/locale"
    try:
        es = gettext.translation(
            "climmob", localedir=this_file_path, languages=[locale]
        )
        es.install()
        _ = es.gettext
    except:
        locale = "en"
        es = gettext.translation(
            "climmob", localedir=this_file_path, languages=[locale]
        )
        es.install()
        _ = es.gettext

    nameOutput = form + "_form"
    if code != "":
        nameOutput += "_" + code

    pathoutput = os.path.join(path, "outputs")
    if not os.path.exists(pathoutput):
        os.makedirs(pathoutput)

    _columns = [_("Field agent"), _("Error")]

    _rows = []
    _used = []

    listOfBadQuestions = [
        "surveyid",
        "originid",
        "cal_qst163",
        "_xform_id_string",
        "_submitted_by",
        "_submitted_date",
        "_geopoint",
        "_longitude",
        "_latitude",
        "_elevation",
        "_precision",
        "clm_deviceimei",
        "instancename",
        "clc_after",
        "clc_before",
    ]

    firstPart = "REG_"
    qst = "qst162"
    fields = info["registry"]["fields"]
    lkps = info["registry"]["lkptables"]
    if code != "":
        firstPart = "ASS" + code + "_"
        qst = "qst163"
        fields = info["assessments"][0]["fields"]
        lkps = info["assessments"][0]["lkptables"]

    for field in fields:
        if field["name"] not in listOfBadQuestions:
            _columns.append(field["desc"])

    for errorFile in listOfErrors:
        _dataInRow = []
        if os.path.exists(errorFile["json_file"]):
            with open(errorFile["json_file"], "r") as json_file:
                new_json = json.load(json_file)

                _dataInRow.append(errorFile["enum_id"])
                _dataInRow.append(errorFile["detail"])
                for field in fields:
                    if field["name"] not in listOfBadQuestions:
                        value = getTheValueForField(field, new_json, structure)
                        if field["name"] == "qst163":
                            value = int(value.split(":")[1].split("-")[0])
                            _used.append(int(value))

                        if field["name"] == "qst162":
                            value = int(value.split("-")[1])
                            _used.append(int(value))

                        if field["name"] == "rowuuid":
                            value = errorFile["log_id"]

                        _dataInRow.append(value)

        _rows.append(_dataInRow)

    primaryKey = -1
    for row in info["data"]:
        cont = 1
        if row[firstPart + qst]:
            if int(row[firstPart + qst]) in _used:
                _dataInRow = []
                if firstPart + "_submitted_by" in row.keys():
                    _dataInRow.append(row[firstPart + "_submitted_by"])
                else:
                    _dataInRow.append("")

                _dataInRow.append(
                    "Duplicate entry '"
                    + str(row[firstPart + qst])
                    + "' for key '"
                    + firstPart
                    + "geninfo.PRIMARY'"
                )

                for field in fields:
                    if field["name"] not in listOfBadQuestions:
                        cont += 1

                        if field["key"] == "true" and primaryKey == -1:
                            primaryKey = cont

                        if (
                            field["rtable"] != None
                            and row[firstPart + field["name"]] != None
                            and field["name"] != "qst163"
                        ):
                            result = getRealData(
                                lkps,
                                field["rtable"],
                                field["rfield"],
                                row[firstPart + field["name"]],
                                field["isMultiSelect"],
                            )
                            _dataInRow.append(str(result).replace(",", ""))
                        else:
                            if field["name"] == "qst163" or field["name"] == "qst162":
                                _dataInRow.append(int(row[firstPart + field["name"]]))

                            else:
                                _dataInRow.append(
                                    str(row[firstPart + field["name"]]).replace(",", "")
                                )

                _rows.append(_dataInRow)

    df = pd.DataFrame(_rows, columns=_columns).sort_values(by=[_columns[primaryKey]])
    df.to_excel(pathoutput + "/" + nameOutput + "_" + project + ".xlsx", index=False)

    return ""


def getTheValueForField(field, new_json, structure):
    value = ""
    for section in structure:
        for question in section["section_questions"]:

            splited = question["question_datafield"].split("/")
            if len(splited) >= 2:
                if field["name"] == splited[1].lower():
                    try:
                        value = new_json[question["question_datafield"]]
                    except:
                        value = "None"

                    if value != "None":
                        if question["question_dtype"] == "select_one":
                            for option in question["question_options"]:
                                if str(option["value_code"]) == str(value):
                                    return option["value_desc"]
                        else:
                            if question["question_dtype"] == "select_multiple":
                                allOptionSelected = ""
                                selectedValues = [str(x) for x in value.split(" ")]
                                for option in question["question_options"]:
                                    if str(option["value_code"]) in selectedValues:
                                        if allOptionSelected == "":
                                            allOptionSelected = option["value_desc"]
                                        else:
                                            allOptionSelected += (
                                                "\n" + option["value_desc"]
                                            )
                                return allOptionSelected
            else:
                if field["name"] == question["question_code"]:
                    return new_json[question["question_datafield"]]

                if (
                    field["name"] == "clm_start"
                    and question["question_code"] == "__CLMQST1__"
                ) or (
                    field["name"] == "clm_end"
                    and question["question_code"] == "__CLMQST2__"
                ):
                    return new_json[question["question_datafield"]]

    return value
