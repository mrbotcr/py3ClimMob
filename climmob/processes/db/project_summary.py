from climmob.models import (
    ProjectSummary,
    mapToSchema,
    mapFromSchema
)

__all__ = [
    "add_project_summary",
    "update_project_summary",
    "get_project_summary",
    "get_all_project_summary"
]

import sys
def add_project_summary(data, request):
    mapped_data = mapToSchema(ProjectSummary, data)
    new_project_summary = ProjectSummary(**mapped_data)
    try:
        request.dbsession.add(new_project_summary)
    except Exception as e:
        return False, str(e)

def update_project_summary(data, project_id, request):

    mapped_data = mapToSchema(ProjectSummary, data)
    try:
        request.dbsession.query(ProjectSummary).filter(ProjectSummary.project_id == project_id).update(mapped_data)
        return True, ""
    except Exception as e:
        return False, e

def get_project_summary(project_id, request):

    res = mapFromSchema(
        request.dbsession.query(ProjectSummary)
        .filter(ProjectSummary.project_id == project_id)
        .first()
    )

    return res

def get_all_project_summary(request):

    res = mapFromSchema(
        request.dbsession.query(ProjectSummary.psm_json)
        .all()
    )
    all_project = []
    for data in res:
        all_project.append(data["psm_json"])

    return all_project
