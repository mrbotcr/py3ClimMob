import shutil as sh
from climmob.config.celery_app import celeryApp
import os
from climmob.config.celery_class import celeryTask
import xlsxwriter


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createPackages(path, projectid, packages, techs):

    if os.path.exists(path):
        sh.rmtree(path)

    os.makedirs(path)

    pathout = os.path.join(path, "outputs")
    os.makedirs(pathout)

    pathfinal = os.path.join(path, *["outputs", "packages_" + projectid + ".xlsx"])
    alphabet = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]

    book = xlsxwriter.Workbook(pathfinal)
    sheet1 = book.add_worksheet("packages")
    sheet1.set_column(0, 0, 15)
    sheet1.write("A1", "Package code")

    num_observations = packages[0]["project_numcom"]

    merge_format1 = book.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "#D8D8D8",
        }
    )

    merge_format2 = book.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "#FFFFFF",
        }
    )

    merge_format3 = book.add_format({"border": 1, "fg_color": "#D8D8D8"})

    merge_format4 = book.add_format({"border": 1, "fg_color": "#FFFFFF"})

    for x in range(0, num_observations):
        useFormat = None

        if x % 2 == 0:
            useFormat = merge_format1
        else:
            useFormat = merge_format2
        # VERIFICO QUE SEA UNO PORQUE DE SER ASI NO PUEDO HACER MERGE ENTRE COLUMNAS
        if len(techs) == 1:
            sheet1.write(0, x + 1, "Variety " + alphabet[x], useFormat)
            sheet1.write(1, x + 1, techs[0]["tech_name"], useFormat)
        else:
            number = (x * len(techs)) + 1
            start = alphabet[number]

            cont = 0
            for y in range(0, len(techs)):
                finish = alphabet[number + y]
                sheet1.write(finish + "2", techs[cont]["tech_name"], useFormat)
                cont = cont + 1

            sheet1.merge_range(
                start + "1:" + finish + "1", "Variety " + alphabet[x], useFormat
            )

    row = 2
    for package in packages:
        # print package
        cont = 1
        sheet1.write(row, 0, package["package_code"])
        x = 0
        for combination in package["combs"]:

            if x % 2 == 0:
                useFormat = merge_format3
            else:
                useFormat = merge_format4

            for tech in techs:
                for tec in combination["technologies"]:
                    if tec["tech_name"] == tech["tech_name"]:
                        sheet1.set_column(row, cont, len(tec["alias_name"]) * 1.5)
                        sheet1.write(row, cont, tec["alias_name"], useFormat)
                        cont = cont + 1

            x = x + 1

        row = row + 1

    book.close()

    return ""
