import json

from climmob.models import MetadataForm, mapToSchema, mapFromSchema
from climmob.processes.db.project_metadata_form import getProjectMetadataForm
from climmob.processes.db.registry import isRegistryClose
from climmob.processes.db.metadata_form_location_unit_of_analysis import (
    getAllMetadaFormLocationUnitOfAnalysisByMetadataForm,
)

__all__ = [
    "addMetadataForm",
    "getAllMetadata",
    "getMetadataForm",
    "getMetadataForProject",
    "deleteMetadataForm",
    "modifyMetadataForm",
]


def addMetadataForm(data, request):
    mappedData = mapToSchema(MetadataForm, data)
    newMetadataForm = MetadataForm(**mappedData)
    try:
        request.dbsession.add(newMetadataForm)
        return True, ""
    except Exception as e:
        return False, str(e)


def getAllMetadata(request):
    _query = (
        request.dbsession.query(
            MetadataForm.metadata_id,
            MetadataForm.metadata_name,
            MetadataForm.metadata_active,
        )
        .order_by(MetadataForm.metadata_name)
        .all()
    )
    result = mapFromSchema(_query)

    for metadata in result:

        metadata["InfoDetails"] = getAllMetadaFormLocationUnitOfAnalysisByMetadataForm(
            request, metadata["metadata_id"]
        )

    return result


def getMetadataForm(request, metadataFormId):
    resultQuery = (
        request.dbsession.query(MetadataForm)
        .filter(MetadataForm.metadata_id == metadataFormId)
        .first()
    )
    result = mapFromSchema(resultQuery)

    result["InfoDetails"] = getAllMetadaFormLocationUnitOfAnalysisByMetadataForm(
        request, result["metadata_id"]
    )

    return result


"""
    ADAPATAR LOS FILTROS POR LOS NECESARIOS
"""


def getMetadataForProject(request, projectId):
    form_allow = [0]
    if isRegistryClose(projectId, request):
        form_allow.append(1)

    result = mapFromSchema(
        request.dbsession.query(MetadataForm.metadata_id, MetadataForm.metadata_name)
        .filter(MetadataForm.metadata_active == 1)
        .filter(MetadataForm.metadata_for_technology_options.in_(form_allow))
        .order_by(MetadataForm.metadata_name)
        .all()
    )
    for info in result:

        info["result"] = getProjectMetadataForm(request, projectId, info["metadata_id"])

        if info["result"]:

            empty_form = getMetadataForm(request, info["metadata_id"])
            required_keys = []
            list_of_missing_keys = []

            if "metadata_json" in empty_form:
                try:
                    json_form = json.loads(empty_form["metadata_json"])
                    if "children" in json_form:
                        required_keys = look_for_required_key(json_form["children"])
                except json.JSONDecodeError as e:
                    return "_(Error parsing JSON)"

            data = info["result"]["pmf_json"].get("data", {})

            for key in required_keys:
                if not find_key_recursively(data, key):
                    list_of_missing_keys.append(key)

            info["state_of_form"] = (
                "1" if not list_of_missing_keys else list_of_missing_keys
            )

        else:
            info["state_of_form"] = "0"  # empty form

    return result


def look_for_required_key(children):
    name_of_required_keys = []
    for child in children:
        if not isinstance(child, dict):
            continue

        if "children" in child and isinstance(child["children"], list):
            name_of_required_keys.extend(look_for_required_key(child["children"]))
        bind = child.get("bind", {})
        if bind.get("required") == "yes":
            name = child.get("name")
            if name:
                name_of_required_keys.append(name)

    return name_of_required_keys


def find_key_recursively(data, key_name):
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key_name and v not in [None, "", [], {}]:
                return True
            if isinstance(v, (dict, list)):
                if find_key_recursively(v, key_name):
                    return True
    elif isinstance(data, list):
        for item in data:
            if find_key_recursively(item, key_name):
                return True
    return False


def modifyMetadataForm(request, metadataId, data):
    try:
        mappedData = mapToSchema(MetadataForm, data)
        request.dbsession.query(MetadataForm).filter(
            MetadataForm.metadata_id == metadataId
        ).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e


def deleteMetadataForm(request, metadataFormId):
    try:
        request.dbsession.query(MetadataForm).filter(
            MetadataForm.metadata_id == metadataFormId
        ).delete()
        return True, ""
    except Exception as e:
        return False, e
