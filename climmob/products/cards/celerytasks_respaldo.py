import shutil as sh
from climmob.config.celery_app import celeryApp
import os
import uuid
from jinja2 import Environment, FileSystemLoader
from climmob.config.celery_class import celeryTask


#PATH = os.path.abspath('climmob/products/cards')
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(autoescape=False,loader=FileSystemLoader(os.path.join(PATH, 'templates')),trim_blocks=False)


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def create_index_html(svg, qrid,projectname, projectpi, package, projectpiemail, projectpinumber, projectcreationdate, letter):

    context = {
        'qrid': qrid,
        'bioversity': os.path.join(PATH,"images/bioversity.png"),
        'projectname': projectname,
        'projectpi':projectpi,
        'package':package,
        'projectpiemail':projectpiemail,
        'projectpinumber': projectpinumber,
        'projectcreationdate': projectcreationdate,
        'letter': letter
    }

    with open(svg, 'w') as f:

        html = render_template('templateCard.xml', context)
        f.write(html.encode('utf-8'))

@celeryApp.task(base=celeryTask,soft_time_limit=7200, time_limit=7200)
def createCards(path,projectid, packages):

    if os.path.exists(path):
        sh.rmtree(path)


    os.makedirs(path)

    pathout = os.path.join(path,"outputs")
    os.makedirs(pathout)

    pathfinal = os.path.join(path, *["outputs","cards.pdf"])


    pathqrs = os.path.join(path[0:-6], *["qrpackage","packages"])
    pathqr = os.path.join(pathqrs, "qr")

    path = os.path.join(path,"cards")

    os.makedirs(path)
    os.makedirs(os.path.join(path,"svg"))
    os.makedirs(os.path.join(path,"png"))
    os.makedirs(os.path.join(path,"pdf"))

    pathsvg = os.path.join(path,"svg")
    pathpng = os.path.join(path,"png")
    pathpdfini = os.path.join(path,"pdf")
    uuidVal = uuid.uuid4()
    pathpdf = os.path.join(pathpdfini,str(uuidVal))

    os.mkdir(pathpdf)
    alphabet =["A","B","C","D","E","F","G","H","I","J","K"]
    allPNGpaths = ""
    contador = 1
    veces = 0
    for package in packages:

        cont = 0

        for x in range(0, int(package["project_numcom"])):

            svg = pathsvg + "/" + str(package["package_id"])+"_"+alphabet[x]+ ".svg"
            qr = pathqr + "/" + str(package["package_id"]) + ".png"
            create_index_html(svg,qr, package["project_name"],str(package["project_pi"]), "Package "+str(package["package_id"]),str(package["project_piemail"]),"",str(package["project_creationdate"])[0:10], alphabet[x])

            png = pathpng + "/" + str(package["package_id"])+"_"+alphabet[x]+ ".png"
            os.system("svg2png " + svg + " -o " + png + " -w 748 -h 244")
            allPNGpaths += png + " "

            if contador == 296:
                veces = veces + 1
                os.system("pdfjam " + allPNGpaths + "  --no-landscape --nup 2x8 --frame true --outfile " + pathpdf + "/" + str(veces) + ".pdf")
                os.system("pdfcrop --margin '0 20 0 20' " + pathpdf + "/" + str(veces) + ".pdf " + pathpdf + "/" + str(veces) + ".pdf")
                allPNGpaths = ""
                contador = 0
            contador = contador + 1


    if allPNGpaths != "":
        veces = veces + 1
        os.system("pdfjam " + allPNGpaths + "  --no-landscape --nup 2x8 --frame true --outfile " + pathpdf + "/" + str(veces) + ".pdf")
        os.system("pdfcrop --margin '0 20 0 20' " + pathpdf + "/" + str(veces) + ".pdf " + pathpdf + "/" + str(veces) + ".pdf")

    os.system("pdfjam " + pathpdf + "/*.pdf --no-landscape  --outfile " + pathfinal)

    import shutil
    shutil.rmtree(path)
    shutil.rmtree(pathqrs)

    return ""