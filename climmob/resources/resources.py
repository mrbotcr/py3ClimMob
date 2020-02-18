"""
from fanstatic import Library, Resource, get_library_registry
import os

__all__ = [
    'addLibrary', 'addJSResource',
    'addCSSResource', 'getJSResource', 'getCSSResource',
    'getLibraryList', 'getCSSResourceList', 'getJSResourceList'
]

_LIBRARIES = []
_CSSRESOURCES = []
_JSRESOURCES = []

def library_found(name):
    for library in _LIBRARIES:
        if library["name"] == name:
            return True
    return False

def library_index(name):
    for pos in range(0,len(_LIBRARIES)):
        if _LIBRARIES[pos]["name"] == name:
            return pos
    return -1

def library_path_exits(path):
    return os.path.exists(path)

def library_path_found(path):
    for library in _LIBRARIES:
        if os.path.normpath(library["path"]) == os.path.normpath(path):
            return True
    return False

def addLibrary(name,path):
    if not library_found(name):
        if library_path_exits(path):
            if not library_path_found(path):
                _LIBRARIES.append({'name': name,'path': path,'library': Library(name, path)})
                registry = get_library_registry()
                registry.add(_LIBRARIES[len(_LIBRARIES)-1]["library"])
            else:
                raise Exception("Path {} already in use".format(path))
        else:
            raise Exception("Path {} does not exist".format(path))
    else:
        raise Exception("Library name {} is already in use".format(name))

def resourceExists(resourceID,resourceType='JS'):
    if resourceType == 'JS':
        for resource in _JSRESOURCES:
            if resource["resourceID"] == resourceID:
                return True
    if resourceType == 'CSS':
        for resource in _CSSRESOURCES:
            if resource["resourceID"] == resourceID:
                return True
    return False

def resourceIndex(resourceID,resourceType='JS'):
    if resourceType == 'JS':
        for index in range(0,len(_JSRESOURCES)) :
            if _JSRESOURCES[index]["resourceID"] == resourceID:
                return index
    if resourceType == 'CSS':
        for index in range(0, len(_CSSRESOURCES)):
            if _CSSRESOURCES[index]["resourceID"] == resourceID:
                return index
    return -1

def addResource(libraryName,resourceID,resourceFile,resourceType='JS',depends='CHAIN',bottomSafe=False):
    index = library_index(libraryName)
    if index >= 0:
        libraryPath = _LIBRARIES[index]["path"]
        pathToResource = os.path.join(libraryPath, resourceFile)
        if os.path.exists(pathToResource):
            if not resourceExists(resourceID,resourceType):
                if resourceType == 'JS':
                    if len(_JSRESOURCES) == 0:
                        _JSRESOURCES.append({'resourceID':resourceID,'file':resourceFile,'resource':Resource(_LIBRARIES[index]["library"],resourceFile,bottom=bottomSafe),'library':libraryName,'depends':None})
                    else:
                        if depends == 'CHAIN':
                            _JSRESOURCES.append({'resourceID': resourceID,'file':resourceFile,
                                                 'resource': Resource(_LIBRARIES[index]["library"], resourceFile,
                                                                      depends=[_JSRESOURCES[len(_JSRESOURCES) - 1][
                                                                          "resource"]], bottom=bottomSafe),'library':libraryName,'depends':_JSRESOURCES[len(_JSRESOURCES) - 1][
                                                                          "resourceID"]})
                        else:
                            if depends is None:
                                _JSRESOURCES.append({'resourceID': resourceID,'file':resourceFile,
                                                 'resource': Resource(_LIBRARIES[index]["library"], resourceFile, bottom=bottomSafe),'library':libraryName,'depends':None})
                            else:
                                depIndex = resourceIndex(depends)
                                if depIndex >= 0:
                                    _JSRESOURCES.append({'resourceID': resourceID,'file':resourceFile,
                                                         'resource': Resource(_LIBRARIES[index]["library"], resourceFile,
                                                                              depends=[_JSRESOURCES[depIndex]["resource"]], bottom=bottomSafe),'library':libraryName,'depends':depends})
                                else:
                                    raise Exception("Dependency resource {} does not exists".format(depends))
                if resourceType == 'CSS':
                    if len(_CSSRESOURCES) == 0:
                        _CSSRESOURCES.append({'resourceID':resourceID,'file':resourceFile,'resource':Resource(_LIBRARIES[index]["library"],resourceFile),'library':libraryName,'depends':None})
                    else:
                        if depends == 'CHAIN':
                            _CSSRESOURCES.append({'resourceID': resourceID,'file':resourceFile,
                                                  'resource': Resource(_LIBRARIES[index]["library"], resourceFile,
                                                                       depends=[_CSSRESOURCES[len(_CSSRESOURCES) - 1][
                                                                           "resource"]]),'library':libraryName,'depends':_CSSRESOURCES[len(_CSSRESOURCES) - 1][
                                                                           "resourceID"]})
                        else:
                            if depends is None:
                                _CSSRESOURCES.append({'resourceID': resourceID,'file':resourceFile,
                                                      'resource': Resource(_LIBRARIES[index]["library"], resourceFile),'library':libraryName,'depends':None})
                            else:
                                depIndex = resourceIndex(depends,'CSS')
                                if depIndex >= 0:
                                    _CSSRESOURCES.append({'resourceID': resourceID,'file':resourceFile,
                                                          'resource': Resource(_LIBRARIES[index]["library"],
                                                                               resourceFile,
                                                                               depends=[
                                                                               _CSSRESOURCES[depIndex]["resource"]]),'library':libraryName,'depends':depends})
                                else:
                                    raise Exception("Dependency resource {} does not exists".format(depends))
            else:
                raise Exception("Resource id {} already in list".format(resourceID))
        else:
            raise Exception("Resource file {} does not exists".format(resourceFile))
    else:
        raise Exception("Library name {} does not exists".format(libraryName))

def addJSResource(libraryName,resourceID,resourceFile,depends='CHAIN',bottomSafe=False):
    addResource(libraryName,resourceID,resourceFile,'JS',depends,bottomSafe)

def addCSSResource(libraryName,resourceID,resourceFile,depends='CHAIN'):
    addResource(libraryName,resourceID,resourceFile,'CSS',depends)

def getJSResource(resourceID):
    index = resourceIndex(resourceID)
    if index >= 0:
        return _JSRESOURCES[index]["resource"]
    else:
        raise Exception("JS Resource {} does not exists".format(resourceID))

def getCSSResource(resourceID):
    index = resourceIndex(resourceID,'CSS')
    if index >= 0:
        return _CSSRESOURCES[index]["resource"]
    else:
        raise Exception("CSS Resource {} does not exists".format(resourceID))

def getLibraryList():
    result = []
    for library in _LIBRARIES:
        result.append({'name': library["name"],'path': library["path"]})
    return result

def getCSSResourceList():
    result = []
    for resource in _CSSRESOURCES:
        result.append({'resourceID':resource["resourceID"],'file':resource["file"],'library':resource["library"],'depends':resource["depends"]})
    return result

def getJSResourceList():
    result = []
    for resource in _JSRESOURCES:
        result.append({'resourceID':resource["resourceID"],'file':resource["file"],'library':resource["library"],'depends':resource["depends"]})
    return result

"""

"""
    Provides the declaration and injection of resources into Jinja2.

    :copyright: (c) 2018 by QLands Technology Consultants.
    :license: AGPL, see LICENSE.txt for more details.
"""

import os
from lxml import etree

__all__ = ["add_library", "add_js_resource", "add_css_resource", "need"]

_LIBRARIES = []


def library_found(name):
    for library in _LIBRARIES:
        if library["name"] == name:
            return True
    return False


def get_library_index(name):
    for pos in range(0, len(_LIBRARIES)):
        if _LIBRARIES[pos]["name"] == name:
            return pos
    return -1


def library_path_exits(path):
    return os.path.exists(path)


def library_path_found(path):
    for library in _LIBRARIES:
        if os.path.normpath(library["path"]) == os.path.normpath(path):
            return True
    return False


def add_library(name, path, config):
    if not library_found(name):
        if library_path_exits(path):
            if not library_path_found(path):
                _LIBRARIES.append(
                    {
                        "name": name,
                        "path": path,
                        "library": etree.Element("root"),
                        "CSSResources": [],
                        "JSResources": [],
                    }
                )
                config.add_static_view(name, path, cache_max_age=3600)
            else:
                raise Exception("Path {} already in use".format(path))
        else:
            raise Exception("Path {} not found".format(path))
    else:
        raise Exception("Library name {} is already in use".format(name))


def resource_exists(library_index, resource_id, resource_type="JS"):
    if resource_type == "JS":
        for resource in _LIBRARIES[library_index]["JSResources"]:
            if resource["resourceID"] == resource_id:
                return True
    if resource_type == "CSS":
        for resource in _LIBRARIES[library_index]["CSSResources"]:
            if resource["resourceID"] == resource_id:
                return True
    return False


def get_resource_index(library_index, resource, resource_type="JS"):
    if resource_type == "JS":
        for index in range(0, len(_LIBRARIES[library_index]["JSResources"])):
            if (
                _LIBRARIES[library_index]["JSResources"][index]["resourceID"]
                == resource
            ):
                return index
    if resource_type == "CSS":
        for index in range(0, len(_LIBRARIES[library_index]["CSSResources"])):
            if (
                _LIBRARIES[library_index]["CSSResources"][index]["resourceID"]
                == resource
            ):
                return index
    return -1


def add_resource_to_library(
    library_index, resource_type, resource_id, resource_file, depends=None
):
    if depends is None:
        resource = etree.Element(resource_type)
        resource.set("resourceID", resource_id)
        resource.set("resourceFile", resource_file)
        _LIBRARIES[library_index]["library"].append(resource)
    else:
        to_resource = _LIBRARIES[library_index]["library"].findall(
            ".//" + resource_type + "[@resourceID='" + depends + "']"
        )
        if to_resource:
            resource = etree.Element(resource_type)
            resource.set("resourceID", resource_id)
            resource.set("resourceFile", resource_file)
            to_resource[0].append(resource)
        else:
            raise Exception("Dependency resource {} does not exists".format(depends))
    if resource_type == "JS":
        _LIBRARIES[library_index]["JSResources"].append(
            {"libraryIndex": library_index, "resourceID": resource_id}
        )
    else:
        _LIBRARIES[library_index]["CSSResources"].append(
            {"libraryIndex": library_index, "resourceID": resource_id}
        )


def add_resource(
    library_name, resource_id, resource_file, resource_type="JS", depends="CHAIN"
):
    index = get_library_index(library_name)
    if index >= 0:
        library_path = _LIBRARIES[index]["path"]
        path_to_resource = os.path.join(library_path, resource_file)
        if os.path.exists(path_to_resource):
            if not resource_exists(index, resource_id, resource_type):
                if resource_type == "JS":
                    if len(_LIBRARIES[index]["JSResources"]) == 0:
                        add_resource_to_library(
                            index, resource_type, resource_id, resource_file
                        )
                    else:
                        if depends == "CHAIN":
                            add_resource_to_library(
                                index,
                                resource_type,
                                resource_id,
                                resource_file,
                                _LIBRARIES[index]["JSResources"][
                                    len(_LIBRARIES[index]["JSResources"]) - 1
                                ]["resourceID"],
                            )
                        else:
                            if depends is None:
                                add_resource_to_library(
                                    index, resource_type, resource_id, resource_file
                                )
                            else:
                                dep_index = get_resource_index(index, depends)
                                if dep_index >= 0:
                                    add_resource_to_library(
                                        index,
                                        resource_type,
                                        resource_id,
                                        resource_file,
                                        _LIBRARIES[index]["JSResources"][dep_index][
                                            "resourceID"
                                        ],
                                    )
                                else:
                                    raise Exception(
                                        "Dependency resource {} does not exists".format(
                                            depends
                                        )
                                    )
                else:
                    if len(_LIBRARIES[index]["CSSResources"]) == 0:
                        add_resource_to_library(
                            index, resource_type, resource_id, resource_file
                        )
                    else:
                        if depends == "CHAIN":
                            add_resource_to_library(
                                index,
                                resource_type,
                                resource_id,
                                resource_file,
                                _LIBRARIES[index]["CSSResources"][
                                    len(_LIBRARIES[index]["CSSResources"]) - 1
                                ]["resourceID"],
                            )
                        else:
                            if depends is None:
                                add_resource_to_library(
                                    index, resource_type, resource_id, resource_file
                                )
                            else:
                                dep_index = get_resource_index(index, depends, "CSS")
                                if dep_index >= 0:
                                    add_resource_to_library(
                                        index,
                                        resource_type,
                                        resource_id,
                                        resource_file,
                                        _LIBRARIES[index]["CSSResources"][dep_index][
                                            "resourceID"
                                        ],
                                    )
                                else:
                                    raise Exception(
                                        "Dependency resource {} does not exists".format(
                                            depends
                                        )
                                    )
            else:
                raise Exception("Resource id {} already in list".format(resource_id))
        else:
            raise Exception("Resource file {} does not exists".format(resource_file))
    else:
        raise Exception("Library name {} does not exists".format(library_name))


def add_js_resource(library_name, resource_id, resource_file, depends="CHAIN"):
    add_resource(library_name, resource_id, resource_file, "JS", depends)


def add_css_resource(library_name, resource_id, resource_file, depends="CHAIN"):
    add_resource(library_name, resource_id, resource_file, "CSS", depends)


def need(library_name, resource_id, resource_type):
    ancestors = []
    index = get_library_index(library_name)
    if index >= 0:
        resource = _LIBRARIES[index]["library"].findall(
            ".//" + resource_type + "[@resourceID='" + resource_id + "']"
        )
        if resource:
            library_path = _LIBRARIES[index]["name"]
            for ancestor in resource[0].iterancestors():
                if ancestor.tag != "root":
                    ancestor_id = ancestor.get("resourceID")
                    ancestor_file = ancestor.get("resourceFile")
                    file_path = os.path.join(library_path, ancestor_file)
                    ancestors.insert(
                        0, {"resourceID": ancestor_id, "filePath": file_path}
                    )
            ancestors.append(
                {
                    "resourceID": resource_id,
                    "filePath": os.path.join(
                        library_path, resource[0].get("resourceFile")
                    ),
                }
            )
    return ancestors