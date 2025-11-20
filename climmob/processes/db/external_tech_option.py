__all__ = [
    "add_external_tech_option",
]

from climmob.models import mapToSchema
from climmob.models.climmobv4 import ExternalTechOption


def add_external_tech_option(tech_option, request):
    mapped_data = mapToSchema(ExternalTechOption, tech_option)
    new_project_summary = ExternalTechOption(**mapped_data)
    try:
        request.dbsession.add(new_project_summary)
        return True, ""
    except Exception as e:
        return False, str(e)
