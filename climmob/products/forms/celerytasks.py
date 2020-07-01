import shutil as sh
from climmob.config.celery_app import celeryApp
import os
from climmob.config.celery_class import celeryTask
import gettext
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from ..qrpackages.celerytasks import create_qr

@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createDocumentForm(locale, user, path, projectid, formGroupsAndQuestions, form, code, packages):
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

    pathoutputhtml = os.path.join(path, "html")
    os.makedirs(pathoutputhtml)

    pathoutputpdf = os.path.join(path, "pdf")
    os.makedirs(pathoutputpdf)

    pathoutput = os.path.join(path, "outputs")
    os.makedirs(pathoutput)

    PATH2 = os.path.dirname(os.path.abspath(__file__))
    os.system(
        "cp -r '" + os.path.join(PATH2, "template", "css") + "' '" + pathoutputhtml + "'"
    )
    os.system(
        "cp -r '" + os.path.join(PATH2, "template", "img") + "' '" + pathoutputhtml + "'"
    )

    for package in packages:

        qr = create_qr(package,projectid,pathqr)

        env = Environment(autoescape=False, loader=FileSystemLoader(os.path.join(PATH, "templates", "snippets", "project")),trim_blocks=False)
        template = env.get_template("previewForm.jinja2")
        info= {"_": _,"data": formGroupsAndQuestions, "qr":qr}
        htmlOfPreview = template.render(info)



        data = {
            "tittle": _(form+" form for the project"),
            "projectid": projectid,
            "Instruction": _("Please complete this form"),
            "htmlOfPreview": htmlOfPreview
        }

        env = Environment(
            autoescape=False,
            loader=FileSystemLoader(os.path.join(PATH2, "template")),
            trim_blocks=False,
        )
        template = env.get_template("app.jinja2")
        render_temp = template.render(data)

        with open(
                pathoutputhtml + "/"+nameOutput+"_"+projectid+"_"+str(package["package_id"])+".html", "w"
        ) as f:  # saves tex_code to outpout file
            f.write(render_temp)

        html = HTML(filename=pathoutputhtml + "/"+nameOutput+"_"+projectid+"_"+str(package["package_id"])+".html")
        html.write_pdf(pathoutputpdf + "/"+nameOutput+"_"+projectid+"_"+str(package["package_id"])+".pdf")

    os.system("pdfjam " + pathoutputpdf + "/*.pdf --no-landscape  --outfile " + pathoutput+"/"+nameOutput+"_"+projectid+".pdf")

    #sh.rmtree(pathouttemp)

    return ""
