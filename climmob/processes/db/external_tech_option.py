__all__ = [
    "add_external_tech_option",
]

from sqlalchemy import exists

from climmob.models import mapToSchema
from climmob.models.climmobv4 import ExternalTechOption
from climmob.processes import removeAlias


def add_external_tech_option(tech_option, request):
    tech_exists = request.dbsession.query(
        exists().where(ExternalTechOption.id == tech_option["id"])
    ).scalar()
    if tech_exists:
        removeAlias(tech_option, request)
        return True, ""

    mapped_data = mapToSchema(ExternalTechOption, tech_option)
    new_project_summary = ExternalTechOption(**mapped_data)
    try:
        request.dbsession.add(new_project_summary)
        return True, ""
    except Exception as e:
        return False, str(e)
