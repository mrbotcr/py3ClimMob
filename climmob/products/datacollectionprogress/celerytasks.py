import shutil as sh
from climmob.config.celery_app import celeryApp
import os
from climmob.config.celery_class import celeryTask
import gettext
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from datetime import datetime
import folium
import subprocess
import glob


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createDataCollectionProgress(
    locale, user, path, project, informationAboutProject, geoInformation
):
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

    _("Alliance")
    _("Progress report on data collection")
    _("Maps of georeferenced points where the forms were applied by field agents.")
    _("Table to show if the information was collected and on what date.")
    _("Form map")
    _("Registry")

    pathoutput = os.path.join(path, "outputs")
    os.makedirs(pathoutput)

    PATH2 = os.path.dirname(os.path.abspath(__file__))
    doc = DocxTemplate(PATH2 + "/template/templateReport.docx")

    ## GEOINFORMATION - CREATING MAPS
    for form in geoInformation:
        m = folium.Map(prefer_canvas=True)

        for fieldAgent in form["fieldAgents"]:
            for point in fieldAgent["Points"]:
                if point:
                    folium.CircleMarker(
                        location=[point.split(" ")[0], point.split(" ")[1]],
                        radius=4,
                        popup=fieldAgent["Name"],
                        color=fieldAgent["Color"],
                        opacity=1,
                        fill=True,
                        fill_color=fieldAgent["Color"],
                        fill_opacity=1,
                    ).add_to(m)

        m.fit_bounds(m.get_bounds())
        saveMapPath = pathoutput + "/" + form["Code"] + ".html"
        m.save(saveMapPath)

        urlMap = "file://" + saveMapPath
        outfn = os.path.join(pathoutput, form["Code"] + ".png")
        # subprocess.check_call(
        #    [
        os.system(
            "xvfb-run cutycapt "
            + " --url={}".format(urlMap)
            + " --out={}".format(outfn)
            + " --delay={}".format(3000)
        )
        #    ]
        # )
        form["Image"] = InlineImage(doc, outfn, width=Mm(140))

    data = {
        "date": datetime.today().strftime("%d-%m-%Y"),
        "dataworking": informationAboutProject,
        "logo": InlineImage(
            doc, os.path.join(PATH2, "template/prueba.png"), width=Mm(100)
        ),
        "_": _,
        "geoInformation": geoInformation,
    }

    doc.render(data)
    doc.save(pathoutput + "/datacollectionprogress_" + project + ".docx")

    for html in glob.iglob(os.path.join(pathoutput, "*.html")):
        os.remove(html)

    for png in glob.iglob(os.path.join(pathoutput, "*.png")):
        os.remove(png)

    return ""
