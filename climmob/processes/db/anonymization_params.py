__all__ = ["save_anonymization_params", "get_anonymization_params_as_dict"]

import re

from climmob.models import mapFromSchema
from climmob.models.climmobv4 import AnonymizationParameter


def get_anonymization_params(question_id, request):
    result = mapFromSchema(
        request.dbsession.query(AnonymizationParameter)
        .filter(AnonymizationParameter.question_id == question_id)
        .all()
    )
    return result


def get_anonymization_params_as_dict(question_id, request):
    params = get_anonymization_params(question_id, request)
    result = {}
    for param in params:
        result[param["name"]] = param["value"]
    return result


def save_anonymization_params(question_id, data, request):
    delete_existing_anonymization_params(question_id, request)

    params = []
    for key in data.keys():
        pattern = r"anonym_param_([a-z_]+)"
        match = re.match(pattern, key)
        if match:
            params.append({"name": match.group(1), "value": data[key]})

    for param in params:
        new_param = AnonymizationParameter(**param)
        new_param.question_id = question_id
        request.dbsession.add(new_param)
        request.dbsession.flush()


def delete_existing_anonymization_params(question_id, request):
    try:
        request.dbsession.query(AnonymizationParameter).filter(
            AnonymizationParameter.question_id == question_id
        ).delete()
        return True, ""
    except Exception as e:
        return False, str(e)
