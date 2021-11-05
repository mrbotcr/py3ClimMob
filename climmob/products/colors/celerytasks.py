import shutil
from climmob.config.celery_app import celeryApp
import base64
import os
import bz2

import uuid
from jinja2 import Environment, FileSystemLoader
from climmob.config.celery_class import celeryTask

PATH = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, "templates")),
    trim_blocks=False,
)
from ..qrpackages.celerytasks import create_qr


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def create_index_html(
    svg, packageid, letterA, letterB, letterC, qr, labelA, labelB, labelC
):

    context = {
        "climmob": os.path.join(PATH, "images/icon.png"),
        "packageid": packageid,
        "letterA": letterA,
        "letterB": letterB,
        "letterC": letterC,
        "bioversity": qr,
        "labelA": labelA,
        "labelB": labelB,
        "labelC": labelC,
    }

    with open(svg, "w") as f:

        html = render_template("templateColors.xml", context)
        f.write(html)


@celeryApp.task(bind=True, base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createColors(self, path, projectid, packages, listOfLabels):
    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)
    pathout = os.path.join(path, "outputs")
    os.makedirs(pathout)
    # Added by Carlos
    pathfinal = os.path.join(path, *["outputs", "colors_" + projectid + ".pdf"])

    path = os.path.join(path, "colors")

    os.makedirs(path)
    os.makedirs(os.path.join(path, "qr"))
    os.makedirs(os.path.join(path, "svg"))
    os.makedirs(os.path.join(path, "png"))
    os.makedirs(os.path.join(path, "pdf"))

    pathqr = os.path.join(path, "qr")
    pathsvg = os.path.join(path, "svg")
    pathpng = os.path.join(path, "png")
    pathpdf = os.path.join(path, "pdf")
    uuidVal = uuid.uuid4()
    pathpdf = os.path.join(pathpdf, str(uuidVal))

    os.mkdir(pathpdf)

    allPNGpaths = ""
    contador = 1
    veces = 0
    for package in packages:

        if self.is_aborted():
            shutil.rmtree(path)
            return ""

        qr = create_qr(package, projectid, pathqr, all=False)

        _tec = 0
        _one = ""
        _two = ""
        _three = ""
        for combination in package["combs"]:

            for tec in combination["technologies"]:
                if _tec == 0:
                    _one = tec["alias_name"]
                else:
                    if _tec == 1:
                        _two = tec["alias_name"]
                    else:
                        _three = tec["alias_name"]

                _tec = _tec + 1

        # COLORS
        colors = {
            "White": "ffffff",
            "Blue": "0003D9",
            "Yellow": "FFC40D",
            "Black": "000000",
            "Red": "d91d21",
            "Blanco": "ffffff",
            "Azul": "0003D9",
            "Amarillo": "FFC40D",
            "Negro": "000000",
            "Rojo": "d91d21",
        }
        # SVG
        svg = pathsvg + "/" + str(package["package_id"]) + ".svg"
        create_index_html(
            svg,
            str(package["package_id"]),
            colors[_one],
            colors[_two],
            colors[_three],
            qr,
            listOfLabels[0],
            listOfLabels[1],
            listOfLabels[2],
        )
        # PDF
        # Changed by Carlos
        png = pathpng + "/" + str(package["package_id"]) + ".png"
        # Changed by Carlos
        os.system("svg2png " + svg + " -o " + png + " -w 406 -h 209")
        # Multi PDFs to One PDF
        # png+= str(tec["package_id"])+".png"

        # Changed by Carlos
        allPNGpaths += png + " "

        if contador == 296:
            veces = veces + 1
            os.system(
                "pdfjam "
                + allPNGpaths
                + "  --no-landscape --nup 2x5 --frame false --outfile "
                + pathpdf
                + "/"
                + str(veces)
                + ".pdf"
            )
            os.system(
                "pdfcrop --margin '0 20 0 20' "
                + pathpdf
                + "/"
                + str(veces)
                + ".pdf "
                + pathpdf
                + "/"
                + str(veces)
                + ".pdf"
            )
            allPNGpaths = ""
            contador = 0
        contador = contador + 1

    if self.is_aborted():
        shutil.rmtree(path)
        return ""

    if allPNGpaths != "":
        veces = veces + 1
        os.system(
            "pdfjam "
            + allPNGpaths
            + "  --no-landscape --nup 2x5 --frame false --outfile "
            + pathpdf
            + "/"
            + str(veces)
            + ".pdf"
        )
        os.system(
            "pdfcrop --margin '0 20 0 20' "
            + pathpdf
            + "/"
            + str(veces)
            + ".pdf "
            + pathpdf
            + "/"
            + str(veces)
            + ".pdf"
        )

    if self.is_aborted():
        shutil.rmtree(path)
        return ""

    # Changed by Carlos
    os.system("pdfjam " + pathpdf + "/*.pdf --no-landscape  --outfile " + pathfinal)

    # import shutil
    shutil.rmtree(path)

    return ""
