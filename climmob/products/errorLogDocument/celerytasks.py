import shutil as sh
from climmob.config.celery_app import celeryApp
import os
from climmob.config.celery_class import celeryTask
import gettext
import xlsxwriter
import json


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createErrorLogDocument(user, path, project, form, code, structure, listOfErrors):
    if not os.path.exists(path):
        os.makedirs(path)

    nameOutput = form + "_form"
    if code != "":
        nameOutput += "_" + code

    pathoutput = os.path.join(path, "outputs")
    if not os.path.exists(pathoutput):
        os.makedirs(pathoutput)

    workbook = xlsxwriter.Workbook(
        pathoutput + "/" + nameOutput + "_" + project + ".xlsx"
    )
    worksheet = workbook.add_worksheet("Errors")
    col = 2
    worksheet.write(0, 0, "Field agent")
    worksheet.write(0, 1, "Error")
    for section in structure:
        for question in section["section_questions"]:
            worksheet.write(0, col, question["question_desc"])
            col += 1

    row = 1
    for errorFile in listOfErrors:

        if os.path.exists(errorFile["json_file"]):
            with open(errorFile["json_file"], "r") as json_file:
                new_json = json.load(json_file)

                col = 2
                worksheet.write(row, 0, errorFile["enum_name"])
                worksheet.write(row, 1, errorFile["detail"])
                for section in structure:
                    for question in section["section_questions"]:
                        if question["question_dtype"] == "select_one":
                            for option in question["question_options"]:
                                if str(option["value_code"]) == str(
                                    new_json[question["question_datafield"]]
                                ):
                                    worksheet.write(row, col, option["value_desc"])
                        else:
                            if question["question_dtype"] == "select_multiple":
                                allOptionSelected = ""
                                selectedValues = [
                                    str(x)
                                    for x in new_json[
                                        question["question_datafield"]
                                    ].split(" ")
                                ]
                                for option in question["question_options"]:
                                    if str(option["value_code"]) in selectedValues:
                                        if allOptionSelected == "":
                                            allOptionSelected = option["value_desc"]
                                        else:
                                            allOptionSelected += (
                                                "\n" + option["value_desc"]
                                            )

                                worksheet.write(row, col, allOptionSelected)

                            else:
                                worksheet.write(
                                    row, col, new_json[question["question_datafield"]]
                                )
                        col += 1
                row += 1

    workbook.close()

    return ""
