import shutil as sh
from climmob.config.celery_app import celeryApp
import os
from climmob.config.celery_class import celeryTask
import gettext
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from datetime import datetime


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createDataCollectionProgress(locale, user, path, project, informationAboutProject):
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

    pathoutput = os.path.join(path, "outputs")
    os.makedirs(pathoutput)

    PATH2 = os.path.dirname(os.path.abspath(__file__))
    doc = DocxTemplate(PATH2 + "/template/templateReport.docx")

    #print(informationAboutProject)
    data = {
        "date": datetime.today().strftime("%d-%m-%Y"),
        "dataworking": informationAboutProject,
        "logo": InlineImage(
            doc, os.path.join(PATH2, "template/prueba.png"), width=Mm(100)
        ),
        "_": _,
    }

    doc.render(data)
    doc.save(pathoutput + "/datacollectionprogress_" + project + ".docx")

    return ""


