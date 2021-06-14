import shutil as sh
from climmob.config.celery_app import celeryApp
import os
from climmob.config.celery_class import celeryTask
import csv
import gettext


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createPackages(locale, path, projectid, packages, techs):

    if os.path.exists(path):
        sh.rmtree(path)

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

    os.makedirs(path)

    pathout = os.path.join(path, "outputs")
    os.makedirs(pathout)

    pathfinal = os.path.join(path, *["outputs", "packages_" + projectid + ".csv"])
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

    num_observations = packages[0]["project_numcom"]

    firstRow = [_("Package code")]
    SecondRow = [""]
    allRows = []

    with open(pathfinal, "w") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=",")

        for x in range(0, num_observations):
            if len(techs) == 1:
                firstRow.append(_("Option ") + alphabet[x])
                SecondRow.append(techs[0]["tech_name"])
            else:
                cont = 0
                for y in range(0, len(techs)):
                    firstRow.append(_("Option ") + alphabet[x])
                    SecondRow.append(techs[cont]["tech_name"])
                    cont = cont + 1

        filewriter.writerow(firstRow)
        filewriter.writerow(SecondRow)

        for package in packages:
            simpleRow = [package["package_code"]]

            for combination in package["combs"]:
                for tech in techs:
                    for tec in combination["technologies"]:
                        if tec["tech_name"] == tech["tech_name"]:
                            simpleRow.append(tec["alias_name"])

            allRows.append(simpleRow)

        filewriter.writerows(allRows)

    return ""
