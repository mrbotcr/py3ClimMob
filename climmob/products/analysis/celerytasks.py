from climmob.config.celery_app import celeryApp
from climmob.plugins.utilities import climmobCeleryTask
import os
import shutil as sh
import json
from jinja2 import Environment, FileSystemLoader
from zipfile import ZipFile
from os.path import basename
from .exportToCsv import createCSV
import gettext

PATH = os.path.dirname(os.path.abspath(__file__))


@celeryApp.task(base=climmobCeleryTask)
def createReports(locale, path, user, projectid, data, info, infosheet):

    if os.path.exists(path):
        sh.rmtree(path)

    os.makedirs(path)

    pathout = os.path.join(path, "outputs")
    os.makedirs(pathout)

    pathouttemp = os.path.join(path, "outputs", "r_result")
    os.makedirs(pathouttemp)

    pathInputFiles = os.path.join(path, "inputFile")
    os.makedirs(pathInputFiles)

    with open(pathInputFiles + "/data.json", "w") as outfile:
        jsonString = json.dumps(data, indent=4, ensure_ascii=False)
        outfile.write(jsonString)

    with open(pathInputFiles + "/info.json", "w") as outfile:
        jsonString = json.dumps(info, indent=4, ensure_ascii=False)
        outfile.write(jsonString)

    if os.path.exists(pathInputFiles + "/info.json"):
        try:
            createCSV(pathouttemp + "/Report_data.csv", pathInputFiles + "/info.json")
        except Exception as e:
            print("We can't create the CSV." + str(e))

    parts = __file__.split("/products/")
    this_file_path = parts[0] + "/locale"
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

    pathScript = "/home/ubuntu/new_r_code/ClimMob-analysis"

    os.system(
        "Rscript "
        + pathScript +"/ClimMob.R"
        + " "
        + pathInputFiles + "/data.json"
        + " "
        + pathInputFiles+ "/info.json"
        + " "
        + pathouttemp
        + " TRUE "
        + " "+locale+" "
        + " docx "
        + " " + _("participant")
        + " " + _("item")
        + " "+pathScript
    )

    report = pathouttemp + "/" + projectid + "_report.docx"
    reportInfo = pathouttemp + "/" + projectid + "_infosheets.docx"
    reportData = pathouttemp + "/Report_data.csv"
    file_paths = []

    if os.path.exists(report):
        file_paths.append(report)

    if os.path.exists(reportInfo):
        file_paths.append(reportInfo)

    if os.path.exists(reportData):
        file_paths.append(reportData)

    with ZipFile(pathout + "/reports_" + projectid + ".zip", "w") as zipReport:
        # writing each file one by one
        for file in file_paths:
            zipReport.write(file, basename(file))

    # createTheDocuments(
    #     locale,
    #     path,
    #     pathout,
    #     pathInputFiles,
    #     pathouttemp,
    #     "Report",
    #     pathouttemp + "/result.json",
    #     infosheet,
    #     projectid,
    # )

    #sh.rmtree(pathouttemp)
    #sh.rmtree(pathInputFiles)

    return ""


def createTheDocuments(
    locale,
    path,
    output_dir,
    pathInputFiles,
    output_dirtemp,
    output_fname,
    result_json,
    infosheet,
    projectid,
):
    # output_dir = "/home/acoto/Dropbox/Bioversity/climmob/repLAtex/repLAtex/report/temp/"  # temp files path
    # output_fname = "REPORTE"  # final files name
    pathTempFoReport = os.path.join(path, "report")
    os.makedirs(pathTempFoReport)

    tmp_tex = pathTempFoReport + "/rep.tex"  # latex auxiliar file
    # result_json = "/home/acoto/Downloads/climmoboutput/result.json"  # R results

    with open(result_json) as handle:
        data_pre = json.loads(handle.read())
    # general report
    data_general = {"vars": [], "objs": [], "carac": [], "logos": []}

    parts = __file__.split("/products/")
    this_file_path = parts[0] + "/locale"
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

    if not os.path.isfile(
        parts[0] + "/products/analysis/report/report_" + locale + ".tex"
    ) or not os.path.isfile(
        parts[0] + "/products/analysis/report/infosheets_" + locale + ".tex"
    ):
        locale = "en"

    data_general["vars"] = [
        {
            "var": _("Number of observers"),
            "val": data_pre[data_pre["Characteristics"][0]]["nobs"][0],
        },
        {"var": _("Number of aspects to evaluate"), "val": len(data_pre["Items"])},
        {"var": _("Total number of types"), "val": len(data_pre["Characteristics"])},
    ]
    for i in data_pre["Items"]:
        data_general["objs"].append(
            {"techId": i["techName"], "aliasId": i["aliasName"]}
        )
    count = 0
    for i in data_pre["Characteristics"]:
        count += 1
        result = []
        for c in data_pre[i]["coeff"]:
            result.append(
                {
                    "obj": c["Item"],
                    "est": c["estimate"],
                    "errEsr": c["SE"],
                    "errCuaStd": c["quasiSE"],
                    "cuaVrnz": c["quasiVar"],
                }
            )

        estR_plot = []
        for er in data_pre[i]["treenode"]:
            estR_plot.append(convertImg(data_pre[i]["treenode"][er]))

        data_general["carac"].append(
            {
                "caracId": count,
                "name": i,
                "varE": convertImg(data_pre[i]["tree"]),
                "estR_plot": estR_plot,
                "results": result,
            }
        )
    data_general["logos"] = [
        os.path.join(PATH, "report/prueba.jpg"),
        os.path.join(PATH, "report/logos.jpg"),
    ]
    # infosheets reports
    if infosheet == "TRUE":
        data_by_user = {"users": []}
        info = data_pre["Infosheets"]
        for u in info:
            uname = info[u]["header"]["aliasName"]
            family = "NA"
            div2 = "NA"
            div1 = "NA"
            var_by_user = []
            carac_by_user = []
            positions = []

            for vv in zip(
                info[u]["table1"]["Item"], info[u]["table1"]["Name"]
            ):  # vars by user
                var_by_user.append({"var": vv[0].replace("_", "\_"), "name": vv[1]})
            for cc in info[u]["table2"]:
                carac = cc["Characteristic"]
                posi = []
                count_pos = len(cc.keys()) - 1

                for pos_index in range(count_pos):
                    posi.append(cc["Position" + str(pos_index + 1)])

                carac_by_user.append({"carac": carac, "pos": posi})
            for pp in info[u]["table3"]:
                positions.append(
                    {"pos": "Position " + pp["Position"], "var": pp["Item"]}
                )

            data_by_user["users"].append(
                {
                    "uname": uname,
                    "family": family,
                    "div2": div2,
                    "div1": div1,
                    "var_by_user": var_by_user,
                    "carac_by_user": carac_by_user,
                    "positions": positions,
                }
            )

    # install pandoc

    makeReports(
        data_general, output_dirtemp, output_fname, "report_" + locale + ".tex", tmp_tex
    )  # gen general report
    if infosheet == "TRUE":
        makeReports(
            data_by_user,
            output_dirtemp,
            output_fname + "_INFOS",
            "infosheets_" + locale + ".tex",
            tmp_tex,
        )  # gen info sheets

    report = output_dirtemp + "/" + output_fname + ".pdf"
    reportInfo = output_dirtemp + "/" + output_fname + "_INFOS.pdf"
    reportData = output_dirtemp + "/" + output_fname + "_data.csv"
    file_paths = []

    if os.path.exists(report):
        file_paths.append(report)

    if os.path.exists(reportInfo):
        file_paths.append(reportInfo)

    if os.path.exists(reportData):
        file_paths.append(reportData)

    with ZipFile(output_dir + "/reports_" + projectid + ".zip", "w") as zipReport:
        # writing each file one by one
        for file in file_paths:
            zipReport.write(file, basename(file))


def convertImg(file):
    ext = "png"
    f2 = file.replace(file[-3:], ext)
    # sudo apt install librsvg2-bin
    cmd = "rsvg-convert -a -f png %s > %s" % (file, f2)
    os.system(cmd)

    os.system("convert " + f2 + " -trim " + f2)

    return f2


def makeReports(data, output_dir, output_fname, template, input_latex_file):
    # PATH = os.path.dirname(os.path.abspath(__file__))

    env = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(PATH, "report")),
        trim_blocks=False,
    )
    template = env.get_template(template)
    render_temp = template.render(data)

    with open(input_latex_file, "w") as f:  # saves tex_code to outpout file
        f.write(render_temp.encode("utf-8"))

    cmd = (
        "pdflatex -synctex=1 -interaction=nonstopmode --jobname %s -output-directory %s %s"
        % (
            output_fname,
            output_dir,
            input_latex_file.replace(" ", "\ ").replace("(", "\(").replace(")", "\)"),
        )
    )

    # print cmd
    os.system(cmd)
