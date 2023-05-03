import os
import shutil as sh
import uuid
from climmob.config.celery_app import celeryApp
from climmob.plugins.utilities import climmobCeleryTask
from subprocess import Popen, PIPE
from climmob.models import get_engine
import pandas as pd
import multiprocessing


@celeryApp.task(base=climmobCeleryTask)
def create_XLSX(
    settings,
    path,
    userOwner,
    projectCod,
    projectId,
    form,
    code,
    finalName,
    sensitive=False,
):

    num_workers = (
        multiprocessing.cpu_count() - int(settings.get("server:threads", "1")) - 1
    )

    if num_workers <= 0:
        num_workers = 1

    pathout = os.path.join(path, "outputs")
    if not os.path.exists(pathout):
        os.makedirs(pathout)

    pathOfTheUser = os.path.join(settings["user.repository"], *[userOwner, projectCod])

    UuidForTempDirectory = str(uuid.uuid4())

    pathtmp = os.path.join(path, "tmp_" + UuidForTempDirectory)
    if not os.path.exists(pathtmp):
        os.makedirs(pathtmp)

    pathtmpout = os.path.join(path, "tmp_out_" + UuidForTempDirectory)
    if not os.path.exists(pathtmpout):
        os.makedirs(pathtmpout)

    listOfRequiredInformation = []
    listOfGeneratedXLSX = []

    listOfRequiredInformation.append({"form": "Registration", "code": ""})

    if form == "Report":
        try:
            engine = get_engine(settings)
            sql = "SELECT * FROM assessment WHERE project_id='{}' AND ass_status > 0 ORDER BY ass_days".format(
                projectId
            )
            listOfAssessments = engine.execute(sql).fetchall()

            for assessment in listOfAssessments:
                listOfRequiredInformation.append(
                    {"form": "Assessment", "code": assessment[0]}
                )
            engine.dispose()
        except Exception as e:
            print("Error in the query for get the assessments")
    else:
        if form == "Assessment":
            listOfRequiredInformation.append({"form": form, "code": code})

    for requiredInformation in listOfRequiredInformation:

        nameOutput = requiredInformation["form"] + "_data"
        if requiredInformation["code"] != "":
            nameOutput += "_" + requiredInformation["code"]

        xlsx_file = os.path.join(pathtmpout, *[nameOutput + "_" + projectCod + ".xlsx"])

        if requiredInformation["code"] != "":
            pathOfTheForm = os.path.join(
                pathOfTheUser, *["db", "ass", requiredInformation["code"]]
            )
            mainTable = "ASS" + requiredInformation["code"] + "_geninfo"
        else:
            pathOfTheForm = os.path.join(pathOfTheUser, *["db", "reg"])
            mainTable = "REG_geninfo"

        create_xml = os.path.join(pathOfTheForm, *["create.xml"])

        mysql_user = settings["odktools.mysql.user"]
        mysql_password = settings["odktools.mysql.password"]
        mysql_host = settings["odktools.mysql.host"]
        mysql_port = settings["odktools.mysql.port"]
        odk_tools_dir = settings["odktools.path"]

        paths = ["utilities", "MySQLToXLSX", "mysqltoxlsx"]
        mysql_to_xlsx = os.path.join(odk_tools_dir, *paths)

        args = [
            mysql_to_xlsx,
            "-H " + mysql_host,
            "-P " + mysql_port,
            "-u " + mysql_user,
            "-p '{}'".format(mysql_password),
            "-s " + userOwner + "_" + projectCod,
            "-x " + create_xml,
            "-o " + xlsx_file,
            "-T " + pathtmp,
            "-w {}".format(num_workers),
            "-r {}".format(3),
        ]
        if sensitive:
            args.append("-c")

        commandToExec = " ".join(map(str, args))

        # p = Popen(args, stdout=PIPE, stderr=PIPE, shell=True)
        p = Popen(commandToExec, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            # os.system("mv " + xlsx_file + " " + pathout)
            listOfGeneratedXLSX.append(xlsx_file)
        else:
            print(
                "MySQLToXLSX Error: "
                + stderr.decode()
                + "-"
                + stdout.decode()
                + ". Args: "
                + " ".join(args)
            )
            error = stdout.decode() + stderr.decode()
            if error.find("Worksheet name is already in use") >= 0:
                print(
                    "A worksheet name has been repeated. Excel only allow 30 characters in the worksheet name. "
                    "You can fix this by editing the dictionary and change the description of the tables "
                    "to a maximum of "
                    "30 characters."
                )
            else:
                print(
                    "Unknown error while creating the XLSX. Sorry about this. "
                    "Please report this error as an issue on https://github.com/BioversityCostaRica/py3climmob"
                )

    if len(listOfGeneratedXLSX) > 0:
        mergeXLSXForms(listOfGeneratedXLSX, pathout, finalName)

    sh.rmtree(pathtmpout)
    if os.path.exists(pathtmp):
        sh.rmtree(pathtmp)


def mergeXLSXForms(listOfGeneratedXLSX, pathout, finalName):

    merged_inner = pd.DataFrame()

    for index, XLSX in enumerate(listOfGeneratedXLSX):

        if index == 0:
            registryDF = pd.read_excel(
                XLSX,
                sheet_name=0,
            )
            registryDF = registryDF.add_suffix("_reg")

            merged_inner = registryDF
        else:

            assessmentDF = pd.read_excel(
                XLSX,
                sheet_name=0,
            )
            assessmentDF = assessmentDF.add_suffix("_ass_" + str(index))
            if not assessmentDF.empty:
                merged_inner = pd.merge(
                    left=merged_inner,
                    right=assessmentDF,
                    left_on="qst162_reg",
                    right_on="qst163_ass_" + str(index),
                    how="left",
                )

    merged_inner.to_excel(finalName, sheet_name="Sheet1", index=False)

    os.system("mv " + finalName + " " + pathout)
