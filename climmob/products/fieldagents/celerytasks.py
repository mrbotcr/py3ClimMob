from climmob.config.celery_app import celeryApp
from climmob.config.celery_class import celeryTask
from jinja2 import Environment, FileSystemLoader
import os
import shutil as sh
import json
import zlib
import base64
import qrcode
import gettext
from weasyprint import HTML

PATH = os.path.dirname(os.path.abspath(__file__))
# pip install "weasyprint<43"


@celeryApp.task(bind=True, base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createFieldAgentsReport(
    self, locale, url, userOwner, path, projectCod, fieldagents, project
):
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

    for userParticipant in fieldagents:
        for fieldagent in fieldagents[userParticipant]:

            if self.is_aborted():
                sh.rmtree(path)
                return ""

            odk_settings = {
                "admin": {"change_server": True, "change_form_metadata": False},
                "general": {
                    "change_server": True,
                    "navigation": "buttons",
                    "server_url": url
                    + "/user/"
                    + userOwner
                    + "/project/"
                    + projectCod
                    + "/collaborator/"
                    + fieldagent["user_name"],
                    "username": fieldagent["enum_id"],
                    "password": fieldagent["enum_password"],
                },
                "project": {
                    "name": project["project_name"],
                    "icon": "🌱",
                    "color": "#ffffff",
                },
            }

            qr_json = json.dumps(odk_settings).encode()
            zip_json = zlib.compress(qr_json)
            serialization = base64.b64encode(zip_json)
            serialization = serialization.decode()
            serialization = serialization.replace("\n", "")
            img = qrcode.make(serialization)

            qr_file = os.path.join(
                pathouttemp + "/img",
                *[
                    str(fieldagent["enum_id"])
                    + "_"
                    + str(fieldagent["user_name"])
                    + ".png"
                ]
            )
            img.save(qr_file)

            if self.is_aborted():
                sh.rmtree(path)
                return ""

    data = {
        "tittle": _("List of field agents for the project"),
        "projectid": projectCod,
        "Name": _("Name"),
        "Username": _("Username"),
        "Password": _("Password"),
        "QR": _("QR"),
        "fieldagents": fieldagents,
        "URLInstruction1": _(
            "To manually configure the ODK Collect server, use the URL of the user to which it belongs and use the corresponding field agent user and password."
        ),
        "URL": url,
        "Instruction3": _("Server"),
        "Instruction4": _("User-owned field agents"),
    }

    env = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(PATH, "template")),
        trim_blocks=False,
    )
    template = env.get_template("app.jinja2")

    if self.is_aborted():
        sh.rmtree(path)
        return ""

    render_temp = template.render(data)

    with open(
        pathouttemp + "/fieldagents_" + projectCod + ".html", "w"
    ) as f:  # saves tex_code to outpout file
        f.write(render_temp)

    if self.is_aborted():
        sh.rmtree(path)
        return ""

    html = HTML(filename=pathouttemp + "/fieldagents_" + projectCod + ".html")
    html.write_pdf(pathoutput + "/fieldagents_" + projectCod + ".pdf")

    sh.rmtree(pathouttemp)
    return ""
