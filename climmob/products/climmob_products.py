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
    projectId,
    product,
    output,
    mimeType,
    processName,
    instanceID,
    request,
    newTask=True,
):
    p.registerProductInstance(
        projectId,
        product,
        output,
        mimeType,
        processName,
        instanceID,
        request,
        newTask,
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
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(qrProduct)

    # PACKAGES
    packagesProduct = addProduct("packages", "Excell generator for packages")
    addMetadataToProduct(packagesProduct, "author", "Brandon Madriz")
    addMetadataToProduct(packagesProduct, "version", "1.0")
    addMetadataToProduct(
        packagesProduct,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(packagesProduct)

    # DATADESK
    dataProduct = addProduct("datadesk", "JSON generator for ClimMobDesk")
    addMetadataToProduct(dataProduct, "author", "Brandon Madriz")
    addMetadataToProduct(dataProduct, "version", "1.0")
    addMetadataToProduct(
        dataProduct,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(dataProduct)

    # CARDS
    cardsProduct = addProduct("cards", "Cards generator for rows")
    addMetadataToProduct(cardsProduct, "author", "Brandon Madriz")
    addMetadataToProduct(cardsProduct, "version", "1.0")
    addMetadataToProduct(
        cardsProduct,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(cardsProduct)

    # COLORS
    colorsProduct = addProduct("colors", "Cards generator for test with colors")
    addMetadataToProduct(colorsProduct, "author", "Brandon Madriz")
    addMetadataToProduct(colorsProduct, "version", "1.0")
    addMetadataToProduct(
        colorsProduct,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(colorsProduct)

    # REPORT
    analysysProduct = addProduct("reports", "Create reports.")
    addMetadataToProduct(analysysProduct, "author", "Brandon Madriz")
    addMetadataToProduct(analysysProduct, "version", "1.0")
    addMetadataToProduct(
        analysysProduct,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(analysysProduct)

    """
    This product was removed because the participant report is now a .zip file.
    
    infosheetsProduct = addProduct("infosheets", "Create infosheets.")
    addMetadataToProduct(infosheetsProduct, "author", "Brandon Madriz")
    addMetadataToProduct(infosheetsProduct, "version", "1.0")
    addMetadataToProduct(
        infosheetsProduct,
        "Licence",
        "Copyright 2021, MrBot Software Solutions",
    )
    products.append(infosheetsProduct)"""

    infosheetsZipProduct = addProduct(
        "infosheetszip", "Create a .zip file for participant reports."
    )
    addMetadataToProduct(infosheetsZipProduct, "author", "Brandon Madriz")
    addMetadataToProduct(infosheetsZipProduct, "version", "1.0")
    addMetadataToProduct(
        infosheetsZipProduct,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(infosheetsZipProduct)

    extraOutputsZipProduct = addProduct(
        "extraoutputszip", "Create a .zip file with the extra outputs of the report."
    )
    addMetadataToProduct(extraOutputsZipProduct, "author", "Brandon Madriz")
    addMetadataToProduct(extraOutputsZipProduct, "version", "1.0")
    addMetadataToProduct(
        extraOutputsZipProduct,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(extraOutputsZipProduct)

    # FIELD AGENTS
    fieldagents = addProduct("fieldagents", "Create report of field agents.")
    addMetadataToProduct(fieldagents, "author", "Brandon Madriz")
    addMetadataToProduct(fieldagents, "version", "1.0")
    addMetadataToProduct(
        fieldagents,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(fieldagents)

    # DATA CSV
    datacsv = addProduct("datacsv", "Information collected in the project.")
    addMetadataToProduct(datacsv, "author", "Brandon Madriz")
    addMetadataToProduct(datacsv, "version", "1.0")
    addMetadataToProduct(
        datacsv,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(datacsv)

    # DATA PRIVACY CSV
    dataprivacycsv = addProduct(
        "dataprivacycsv", "Information collected in the project."
    )
    addMetadataToProduct(dataprivacycsv, "author", "Brandon Madriz")
    addMetadataToProduct(dataprivacycsv, "version", "1.0")
    addMetadataToProduct(
        dataprivacycsv,
        "Licence",
        "Copyright 2024, MrBot Software Solutions",
    )
    products.append(dataprivacycsv)

    # FORM
    documentform = addProduct(
        "documentform", "Create a document pdf to collect information."
    )
    addMetadataToProduct(documentform, "author", "Brandon Madriz")
    addMetadataToProduct(documentform, "version", "1.0")
    addMetadataToProduct(
        documentform,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
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
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(generalreport)

    # STICKERS
    stickersProduct = addProduct("stickers", "Stickers for packages")
    addMetadataToProduct(stickersProduct, "author", "Brandon Madriz")
    addMetadataToProduct(stickersProduct, "version", "1.0")
    addMetadataToProduct(
        stickersProduct,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
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
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(datacollectionprogressProduct)

    # ERROR LOG DOCUMENT

    errorLogDocument = addProduct(
        "errorlogdocument", "Create a document xlsx with the error in the submission."
    )
    addMetadataToProduct(errorLogDocument, "author", "Brandon Madriz")
    addMetadataToProduct(errorLogDocument, "version", "1.0")
    addMetadataToProduct(
        errorLogDocument,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(errorLogDocument)

    # MULTIMEDIA

    multimediadownloads = addProduct(
        "multimediadownloads", "Multimedia content downloads."
    )
    addMetadataToProduct(multimediadownloads, "author", "Brandon Madriz")
    addMetadataToProduct(multimediadownloads, "version", "1.0")
    addMetadataToProduct(
        multimediadownloads,
        "Licence",
        "Copyright 2021, MrBot Software Solutions",
    )
    products.append(multimediadownloads)

    # RANDOMIZATION

    randomization = addProduct("randomization", "Randomization for tricot project.")
    addMetadataToProduct(randomization, "author", "Brandon Madriz")
    addMetadataToProduct(randomization, "version", "1.0")
    addMetadataToProduct(
        randomization,
        "Licence",
        "Copyright 2021, MrBot Software Solutions",
    )
    products.append(randomization)

    # UPLOAD DATA

    uploadData = addProduct(
        "uploaddata", "Upload information to ClimMob, via Excel and API."
    )
    addMetadataToProduct(uploadData, "author", "Brandon Madriz")
    addMetadataToProduct(uploadData, "version", "1.0")
    addMetadataToProduct(
        uploadData,
        "Licence",
        "Copyright 2021, MrBot Software Solutions",
    )
    products.append(uploadData)

    # PACKAGES WITH TECNOLOGIES

    packagesWithTechnologies = addProduct(
        "qrpackagewithtechnologies", "List of packages with QR - Showing technologies."
    )
    addMetadataToProduct(packagesWithTechnologies, "author", "Brandon Madriz")
    addMetadataToProduct(packagesWithTechnologies, "version", "1.0")
    addMetadataToProduct(
        packagesWithTechnologies,
        "Licence",
        "Copyright 2021, MrBot Software Solutions",
    )
    products.append(packagesWithTechnologies)

    # DATA XLSX
    dataxlsx = addProduct(
        "dataxlsx", "Information collected in the project in XLSX format."
    )
    addMetadataToProduct(dataxlsx, "author", "Brandon Madriz")
    addMetadataToProduct(dataxlsx, "version", "1.0")
    addMetadataToProduct(
        dataxlsx,
        "Licence",
        "Copyright 2022, MrBot Software Solutions",
    )
    products.append(dataxlsx)

    # DATA PRIVACY XLSX
    dataprivacyxlsx = addProduct(
        "dataprivacyxlsx",
        "Information collected in the project in XLSX format with data privacy.",
    )
    addMetadataToProduct(dataprivacyxlsx, "author", "Brandon Madriz")
    addMetadataToProduct(dataprivacyxlsx, "version", "1.0")
    addMetadataToProduct(
        dataprivacyxlsx,
        "Licence",
        "Copyright 2024, MrBot Software Solutions",
    )
    products.append(dataprivacyxlsx)

    # INPUT FILES
    datajson = addProduct(
        "datajson", "data.json file used as input for report generation."
    )
    addMetadataToProduct(datajson, "author", "Brandon Madriz")
    addMetadataToProduct(datajson, "version", "1.0")
    addMetadataToProduct(
        datajson,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(datajson)

    infojson = addProduct(
        "infojson", "info.json file used as input for report generation."
    )
    addMetadataToProduct(infojson, "author", "Brandon Madriz")
    addMetadataToProduct(infojson, "version", "1.0")
    addMetadataToProduct(
        infojson,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(infojson)

    projectssummary = addProduct(
        "projectssummary", "Summary of all projects registered in ClimMob."
    )
    addMetadataToProduct(projectssummary, "author", "Brandon Madriz")
    addMetadataToProduct(projectssummary, "version", "1.0")
    addMetadataToProduct(
        projectssummary,
        "Licence",
        "Copyright 2023, MrBot Software Solutions",
    )
    products.append(projectssummary)

    return products
