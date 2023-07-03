import gettext
import os
import shutil as sh

from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage

from climmob.config.celery_app import celeryApp
from climmob.config.celery_class import celeryTask
from climmob.processes.db.i18n_general_phrases import getPhraseTranslationInLanguage
from climmob.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from climmob.models.meta import Base
import transaction


@celeryApp.task(bind=True, base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createDocumentForm(
    self,
    locale,
    user,
    path,
    projectid,
    dataPreviewInMultipleLanguages,
    form,
    code,
    packages,
    listOfLabels,
    settings,
):

    engine = get_engine(settings)
    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)
    dbsession = get_tm_session(session_factory, transaction.manager)

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
        if os.path.exists(pathqr):
            sh.rmtree(pathqr)

        os.makedirs(pathqr)

    pathoutput = os.path.join(path, "outputs")
    if not os.path.exists(pathoutput):
        os.makedirs(pathoutput)

    PATH2 = os.path.dirname(os.path.abspath(__file__))
    doc = DocxTemplate(PATH2 + "/template/word_template.docx")
    imgsOfQRs = []

    # if form == "Registration":
    #     for package in packages:
    #
    #         if self.is_aborted():
    #             sh.rmtree(pathqr)
    #             return ""
    #
    #         qr = create_qr(package, projectid, pathqr)
    #         imgsOfQRs.append(InlineImage(doc, qr, width=Mm(50)))

    if form == "Registration":
        tittle = _("Registration form for the project")
    else:
        tittle = _("Assessment form for the project")

    data = {
        "tittle": tittle,
        "projectid": projectid,
        "Instruction": _("Please complete this form"),
        "dataPreviewInMultipleLanguages": dataPreviewInMultipleLanguages,
        "imgsOfQRs": imgsOfQRs,
        "number_of_packages": 1,
        "logo": InlineImage(
            doc, os.path.join(PATH2, "template/prueba.png"), width=Mm(100)
        ),
        "_": _,
        "options": listOfLabels,
        "language": _("Language"),
        "Indication1": _("Write the package code you are delivering to the user."),
        "Indication2": _(
            "When you are going to fill out the form digitally, scan the corresponding package code from:  'List of packages with QR for the registration form', available in the download section."
        ),
        "Better": {},
        "Worse": {},
        "Tied": {},
        "NotObserved": {},
        "Latitude": {},
        "Longitude": {},
        "Altitude": {},
        "Accuracy": {},
        "Note": {},
        "Date": {},
        "Time": {},
    }

    for lang in dataPreviewInMultipleLanguages:

        data["Better"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None, 4, user, lang["lang_code"], returnSuggestion=True, dbsession=dbsession
        )["phrase_desc"]

        data["Worse"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None, 2, user, lang["lang_code"], returnSuggestion=True, dbsession=dbsession
        )["phrase_desc"]

        data["Tied"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None, 1, user, lang["lang_code"], returnSuggestion=True, dbsession=dbsession
        )["phrase_desc"]

        data["NotObserved"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None, 6, user, lang["lang_code"], returnSuggestion=True, dbsession=dbsession
        )["phrase_desc"]

        data["Latitude"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None,
            20,
            user,
            lang["lang_code"],
            returnSuggestion=True,
            dbsession=dbsession,
        )["phrase_desc"]

        data["Longitude"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None,
            21,
            user,
            lang["lang_code"],
            returnSuggestion=True,
            dbsession=dbsession,
        )["phrase_desc"]

        data["Altitude"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None,
            22,
            user,
            lang["lang_code"],
            returnSuggestion=True,
            dbsession=dbsession,
        )["phrase_desc"]

        data["Accuracy"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None,
            23,
            user,
            lang["lang_code"],
            returnSuggestion=True,
            dbsession=dbsession,
        )["phrase_desc"]

        data["Note"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None,
            25,
            user,
            lang["lang_code"],
            returnSuggestion=True,
            dbsession=dbsession,
        )["phrase_desc"]

        data["Date"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None,
            35,
            user,
            lang["lang_code"],
            returnSuggestion=True,
            dbsession=dbsession,
        )["phrase_desc"]

        data["Time"][lang["lang_code"]] = getPhraseTranslationInLanguage(
            None,
            37,
            user,
            lang["lang_code"],
            returnSuggestion=True,
            dbsession=dbsession,
        )["phrase_desc"]

    if self.is_aborted():
        return ""

    doc.render(data)

    if os.path.exists(pathoutput + "/" + nameOutput + "_" + projectid + ".docx"):
        os.remove(pathoutput + "/" + nameOutput + "_" + projectid + ".docx")

    doc.save(pathoutput + "/" + nameOutput + "_" + projectid + ".docx")

    if os.path.exists(pathqr):
        sh.rmtree(pathqr)

    return ""
