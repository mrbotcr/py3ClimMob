"""
These series of functions help plugin developers 
to manipulate the host behaviour without the trouble if dealing with it
These code is licensed under BSD
"""

import inspect
import os

import climmob.products as p
import climmob.resources as r
from climmob.config.celery_class import celeryTask
from climmob.processes import addTask
from climmob.views.classes import publicView, privateView

__all__ = [
    "addTemplatesDirectory",
    "addStaticView",
    "addJSResource",
    "addCSSResource",
    "addLibrary",
    "addRoute",
    "getJSResource",
    "getCSSResource",
    "climmobPublicView",
    "climmobPrivateView",
    "addFieldToUserSchema",
    "addFieldToProjectSchema",
    "addFieldToQuestionSchema",
    "addProduct",
    "addMetadataToProduct",
    "addOutputToProduct",
    "registerProductInstance",
    "climmobCeleryTask",
    "registerCeleryTask",
]


class climmobPublicView(publicView):
    """
    A view class for plugins which require a public (not login required) view.
    """


class climmobPrivateView(privateView):
    """
    A view class for plugins which require a private (login required) view.
    """


class climmobCeleryTask(celeryTask):
    """
    A view class for plugins which require a private (login required) view.
    """


def __returnCurrentPath():
    """

    This code is based on CKAN
    :Copyright (C) 2007 Open Knowledge Foundation
    :license: AGPL V3, see LICENSE for more details.

    """
    frame, filename, line_number, function_name, lines, index = inspect.getouterframes(
        inspect.currentframe()
    )[2]
    return os.path.dirname(filename)


def addTemplatesDirectory(config, relative_path, prepend=True):
    callerPath = __returnCurrentPath()
    templates_path = os.path.join(callerPath, relative_path)
    if os.path.exists(templates_path):
        config.add_jinja2_search_path(searchpath=templates_path, prepend=prepend)
        if prepend == True:
            config.registry.settings["templatesPaths"].insert(0, templates_path)
        else:
            config.registry.settings["templatesPaths"].append(templates_path)
    else:
        raise Exception("Templates path {} does not exists".format(relative_path))


def addStaticView(config, viewName, relative_path, cache_max_age=3600):
    callerPath = __returnCurrentPath()
    static_path = os.path.join(callerPath, relative_path)
    if os.path.exists(static_path):
        introspector = config.introspector
        if introspector.get("static views", viewName, None) is None:
            config.add_static_view(viewName, static_path, cache_max_age=cache_max_age)
    else:
        raise Exception("Static path {} does not exists".format(relative_path))


def addJSResource(libraryName, resourceID, resourceFile, depends, bottomSafe=False):
    return {
        "libraryname": libraryName,
        "id": resourceID,
        "file": resourceFile,
        "depends": depends,
        "bottomsafe": bottomSafe,
    }


def addCSSResource(libraryName, resourceID, resourceFile, depends):
    return {
        "libraryname": libraryName,
        "id": resourceID,
        "file": resourceFile,
        "depends": depends,
    }


def addLibrary(name, path):
    callerPath = __returnCurrentPath()
    library_path = os.path.join(callerPath, path)
    if os.path.exists(library_path):
        return {"name": name, "path": library_path}
    else:
        raise Exception("Library path {} does not exists".format(path))


def addRoute(name, path, view, renderer):
    return {"name": name, "path": path, "view": view, "renderer": renderer}


def getJSResource(resourceID):
    return r.getJSResource(resourceID)


def getCSSResource(resourceID):
    return r.getCSSResource(resourceID)


def addFieldToUserSchema(fieldName, fieldDesc):
    return {"schema": "user", "fieldname": fieldName, "fielddesc": fieldDesc}


def addFieldToProjectSchema(fieldName, fieldDesc):
    return {"schema": "project", "fieldname": fieldName, "fielddesc": fieldDesc}


def addFieldToAssessmentSchema(fieldName, fieldDesc):
    return {"schema": "assessment", "fieldname": fieldName, "fielddesc": fieldDesc}


def addFieldToQuestionSchema(fieldName, fieldDesc):
    return {"schema": "question", "fieldname": fieldName, "fielddesc": fieldDesc}


def addFieldToEnumertorSchema(fieldName, fieldDesc):
    return {"schema": "enumerator", "fieldname": fieldName, "fielddesc": fieldDesc}


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
    result["outputs"] = []
    return result


def addMetadataToProduct(product, key, value):
    try:
        product["metadata"][key] = value
        return True, product
    except:
        return False, product


def addOutputToProduct(product, fileName, mimeType):
    try:
        found = False
        for output in product["outputs"]:
            if output["filename"] == fileName:
                found = True
        if not found:
            product["outputs"].append({"filename": fileName, "mimetype": mimeType})
            return True, product
        return False, product
    except:
        return False, product


def registerProductInstance(user, project, product, output, instanceID, request):
    p.registerProductInstance(user, project, product, output, instanceID, request)


def getProducts():
    return p.getProducts()


def registerCeleryTask(taskID, request):
    addTask(taskID, request)
