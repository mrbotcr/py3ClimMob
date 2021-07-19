import shutil as sh
from climmob.config.celery_app import celeryApp
import os
from climmob.config.celery_class import celeryTask
import gettext
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from ..qrpackages.celerytasks import create_qr


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createDocumentForm(
    locale, user, path, projectid, formGroupsAndQuestions, form, code, packages,
):

    # NO SE BORRA EL PATH PORQUE PUEDE TENER VARIOS ARCHIVOS
    # if os.path.exists(path):
    #    sh.rmtree(path)
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

    pathqr = os.path.join(path, "qr")
    if form == "Registration":
        pathqr = os.path.join(path, "qr")

        if os.path.exists(pathqr):
            sh.rmtree(pathqr)

        os.makedirs(pathqr)

    pathoutput = os.path.join(path, "outputs")
    if not os.path.exists(pathoutput):
        os.makedirs(pathoutput)

    PATH2 = os.path.dirname(os.path.abspath(__file__))
    doc = DocxTemplate(PATH2 + "/template/word_template.docx")
    imgsOfQRs = []
    if form == "Registration":
        for package in packages:

            qr = create_qr(package, projectid, pathqr)
            imgsOfQRs.append(InlineImage(doc, qr, width=Mm(50)))

    data = {
        "tittle": _(form + " form for the project"),
        "projectid": projectid,
        "Instruction": _("Please complete this form"),
        "data": formGroupsAndQuestions,
        "imgsOfQRs": imgsOfQRs,
        "number_of_packages": len(packages),
        "logo": InlineImage(
            doc, os.path.join(PATH2, "template/prueba.png"), width=Mm(100)
        ),
        "_": _,
    }

    doc.render(data)

    if os.path.exists(pathoutput + "/" + nameOutput + "_" + projectid + ".docx"):
        print("Lo elimina")
        os.remove(pathoutput + "/" + nameOutput + "_" + projectid + ".docx")

    doc.save(pathoutput + "/" + nameOutput + "_" + projectid + ".docx")

    if os.path.exists(pathqr):
        sh.rmtree(pathqr)

    return ""
