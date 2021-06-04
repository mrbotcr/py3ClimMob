import shutil as sh
from climmob.config.celery_app import celeryApp
import os
from climmob.config.celery_class import celeryTask
import gettext
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from datetime import datetime


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createGeneralReport(locale, user, path, project, projectDetails):
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
    doc = DocxTemplate(PATH2 + "/template/generalGeneralTemplate.docx")

    _("Assigned field agents")
    _("Selected technologies")
    _("Pending step")
    _("Combinations included in the project")
    _("Section")

    data = {
        "date": datetime.today().strftime("%d-%m-%Y"),
        "dataworking": projectDetails,
        "logo": InlineImage(
            doc, os.path.join(PATH2, "template/prueba.png"), width=Mm(100)
        ),
        "_": _,
    }

    doc.render(data)
    doc.save(pathoutput + "/" + user + "_" + project + "_general_report.docx")

    return ""


"""def createDocumentForm(locale, user, path, projectid, formGroupsAndQuestions, form, code, packages):
    if os.path.exists(path):
        sh.rmtree(path)

    nameOutput = form + "_form"
    if code != "":
        nameOutput += "_" + code

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
    pathqr = os.path.join(path, "qr")
    os.makedirs(pathqr)

    pathoutput = os.path.join(path, "outputs")
    os.makedirs(pathoutput)

    PATH2 = os.path.dirname(os.path.abspath(__file__))
    doc = DocxTemplate(PATH2+"/template/word_template.docx")
    imgsOfQRs = []
    for package in packages:

        qr = create_qr(package,projectid,pathqr)
        imgsOfQRs.append(InlineImage(doc, qr, width=Mm(50)))

    data = {
        "tittle": _(form + " form for the project"),
        "projectid": projectid,
        "Instruction": _("Please complete this form"),
        "data": formGroupsAndQuestions,
        "imgsOfQRs": imgsOfQRs,
        "number_of_packages": len(packages),
        "logo": InlineImage(doc,os.path.join(PATH2, "template/prueba.png"), width=Mm(100)),
        "_": _
    }

    doc.render(data)
    doc.save(pathoutput+"/"+nameOutput+"_"+projectid+".docx")

    sh.rmtree(pathqr)

    return ""
"""
