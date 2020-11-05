import os
import climmob.products as p
from climmob.processes import addTask


def createProductDirectory(request, userID, projectID, product):
    try:
        if p.product_found(product):
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[userID, projectID, "products", product]
            )
            if not os.path.exists(path):
                os.makedirs(path)
                outputPath = os.path.join(path, "outputs")
                os.makedirs(outputPath)
                return path
            else:
                return getProductDirectory(request, userID, projectID, product)
        else:
            return None
    except:
        return None


def getProductDirectory(request, userID, projectID, product):
    try:
        if p.product_found(product):
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[userID, projectID, "products", product]
            )
            return path
        else:
            return None
    except:
        return None


def addProduct(name, description):
    result = {}
    result["name"] = name
    result["description"] = description
    result["metadata"] = {}
    # result["outputs"] = []
    return result


def addMetadataToProduct(product, key, value):
    try:
        product["metadata"][key] = value
        return True, product
    except:
        return False, product


# def addOutputToProduct(product,fileName,mimeType):
#     try:
#         found = False
#         for output in product["outputs"]:
#             if output["filename"] == fileName:
#                 found = True
#         if not found:
#             product["outputs"].append({'filename':fileName,'mimetype':mimeType})
#             return True,product
#         return False,product
#     except:
#         return False,product


def registerProductInstance(
    user, project, product, output, mimeType, processName, instanceID, request
):
    p.registerProductInstance(
        user, project, product, output, mimeType, processName, instanceID, request
    )


def getProducts():
    return p.getProducts()


def registerCeleryTask(taskID, request):
    addTask(taskID, request)


def register_products(config):

    products = []

    # QRPACKAGES
    qrProduct = addProduct("qrpackage", "QR generator for packages")
    addMetadataToProduct(qrProduct, "author", "Brandon Madriz")
    addMetadataToProduct(qrProduct, "version", "1.0")
    addMetadataToProduct(
        qrProduct,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(qrProduct)

    # PACKAGES
    packagesProduct = addProduct("packages", "Excell generator for packages")
    addMetadataToProduct(packagesProduct, "author", "Brandon Madriz")
    addMetadataToProduct(packagesProduct, "version", "1.0")
    addMetadataToProduct(
        packagesProduct,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(packagesProduct)

    # DATADESK
    dataProduct = addProduct("datadesk", "JSON generator for ClimMobDesk")
    addMetadataToProduct(dataProduct, "author", "Brandon Madriz")
    addMetadataToProduct(dataProduct, "version", "1.0")
    addMetadataToProduct(
        dataProduct,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(dataProduct)

    # CARDS
    cardsProduct = addProduct("cards", "Cards generator for rows")
    addMetadataToProduct(cardsProduct, "author", "Brandon Madriz")
    addMetadataToProduct(cardsProduct, "version", "1.0")
    addMetadataToProduct(
        cardsProduct,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(cardsProduct)

    # COLORS
    colorsProduct = addProduct("colors", "Cards generator for test with colors")
    addMetadataToProduct(colorsProduct, "author", "Brandon Madriz")
    addMetadataToProduct(colorsProduct, "version", "1.0")
    addMetadataToProduct(
        colorsProduct,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(colorsProduct)

    # REPORT
    analysysProduct = addProduct("reports", "Create reports and infosheets.")
    addMetadataToProduct(analysysProduct, "author", "Brandon Madriz")
    addMetadataToProduct(analysysProduct, "version", "1.0")
    addMetadataToProduct(
        analysysProduct,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(analysysProduct)

    # FIELD AGENTS
    fieldagents = addProduct("fieldagents", "Create report of field agents.")
    addMetadataToProduct(fieldagents, "author", "Brandon Madriz")
    addMetadataToProduct(fieldagents, "version", "1.0")
    addMetadataToProduct(
        fieldagents,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(fieldagents)

    # DATA CSV
    datacsv = addProduct("datacsv", "Information collected in the project.")
    addMetadataToProduct(datacsv, "author", "Brandon Madriz")
    addMetadataToProduct(datacsv, "version", "1.0")
    addMetadataToProduct(
        datacsv,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(datacsv)

    # FORM
    documentform = addProduct(
        "documentform", "Create a document pdf to collect information."
    )
    addMetadataToProduct(documentform, "author", "Brandon Madriz")
    addMetadataToProduct(documentform, "version", "1.0")
    addMetadataToProduct(
        documentform,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(documentform)

    # GENERAL REPORT
    generalreport = addProduct(
        "generalreport",
        "Create a document docx with the information in the project step by step.",
    )
    addMetadataToProduct(generalreport, "author", "Brandon Madriz")
    addMetadataToProduct(generalreport, "version", "1.0")
    addMetadataToProduct(
        generalreport,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(generalreport)

    # STICKERS
    stickersProduct = addProduct("stickers", "Stickers for packages")
    addMetadataToProduct(stickersProduct, "author", "Brandon Madriz")
    addMetadataToProduct(stickersProduct, "version", "1.0")
    addMetadataToProduct(
        stickersProduct,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(stickersProduct)

    # DATA COLLECTION PROGRESS

    datacollectionprogressProduct = addProduct(
        "datacollectionprogress",
        "Shows the information of the observers from whom the information has been collected",
    )
    addMetadataToProduct(datacollectionprogressProduct, "author", "Brandon Madriz")
    addMetadataToProduct(datacollectionprogressProduct, "version", "1.0")
    addMetadataToProduct(
        datacollectionprogressProduct,
        "Licence",
        "Copyright 2020, Alliance of Bioversity International and CIAT",
    )
    products.append(datacollectionprogressProduct)

    return products
