import json
import csv


def getRealData(lkptables, rtable, rfield, value, isMultiSelect):
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


def createCSV(outputPath, inputFile):
    myFile = open(outputPath, "w")
    with myFile:
        writer = csv.writer(myFile)

        with open(inputFile) as json_file:
            data = json.load(json_file)
            # SACO LAS COLUMNAS DEL REGISTRY
            columns = []
            for field in data["registry"]["fields"]:
                columns.append(field["desc"].replace(",", ""))

            # SACO LAS COLUMNAS DE LOS ASSESSMENTS
            for assessment in data["assessments"]:
                for field in assessment["fields"]:
                    columns.append(field["desc"].replace(",", ""))

            # ESCRIBO LAS COLUMNAS
            writer.writerow(columns)

            # EMPIEZO A SACAR LOS DATOS
            for row in data["data"]:
                fieldsDataRow = []
                # DATOS DEL REGISTRO
                for field in data["registry"]["fields"]:
                    # print(field)
                    if field["rtable"] != None and row["REG_" + field["name"]] != None:
                        result = getRealData(
                            data["registry"]["lkptables"],
                            field["rtable"],
                            field["rfield"],
                            row["REG_" + field["name"]],
                            field["isMultiSelect"],
                        )
                        fieldsDataRow.append(str(result).replace(",", ""))
                    else:
                        fieldsDataRow.append(
                            str(row["REG_" + field["name"]]).replace(",", "")
                        )

                for assessment in data["assessments"]:
                    for field in assessment["fields"]:
                        if (
                            field["rtable"] != None
                            and row["ASS" + assessment["code"] + "_" + field["name"]]
                            != None
                        ):
                            result = getRealData(
                                assessment["lkptables"],
                                field["rtable"],
                                field["rfield"],
                                row["ASS" + assessment["code"] + "_" + field["name"]],
                                field["isMultiSelect"],
                            )
                            fieldsDataRow.append(str(result).replace(",", ""))
                        else:
                            fieldsDataRow.append(
                                str(
                                    row[
                                        "ASS" + assessment["code"] + "_" + field["name"]
                                    ]
                                ).replace(",", "")
                            )

                writer.writerow(fieldsDataRow)
