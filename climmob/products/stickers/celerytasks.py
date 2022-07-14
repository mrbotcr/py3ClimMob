import gettext
import os
import shutil as sh

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from climmob.config.celery_app import celeryApp
from climmob.config.celery_class import celeryTask
from climmob.products.qrpackages.celerytasks import create_qr

PATH = os.path.dirname(os.path.abspath(__file__))


@celeryApp.task(base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createStickerDocument(locale, user, path, projectid, packages):
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

    if os.path.exists(path):
        sh.rmtree(path)

    os.makedirs(path)

    pathoutput = os.path.join(path, "outputs")
    os.makedirs(pathoutput)

    pathouttemp = os.path.join(path, "temp")
    os.makedirs(pathouttemp)

    os.system(
        "cp -r '" + os.path.join(PATH, "template", "css") + "' '" + pathouttemp + "'"
    )
    os.system(
        "cp -r '" + os.path.join(PATH, "template", "img") + "' '" + pathouttemp + "'"
    )

    os.makedirs(os.path.join(pathouttemp + "/img/", "qr"))
    pathqr = os.path.join(pathouttemp + "/img/", "qr")

    for package in packages:

        qr = create_qr(package, projectid, pathqr)

    data = {
        "tittle": _("Stickers for packages"),
        "projectid": projectid,
        "packages": packages,
    }

    env = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(PATH, "template")),
        trim_blocks=False,
    )
    template = env.get_template("app.jinja2")
    render_temp = template.render(data)

    with open(
        pathouttemp + "/stickers_" + projectid + ".html", "w"
    ) as f:  # saves tex_code to outpout file
        f.write(render_temp)

    html = HTML(filename=pathouttemp + "/stickers_" + projectid + ".html")
    html.write_pdf(pathoutput + "/stickers_" + projectid + ".pdf")

    sh.rmtree(pathouttemp)
    return ""
