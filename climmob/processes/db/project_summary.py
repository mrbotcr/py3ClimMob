from sqlalchemy import func, or_

from climmob.models import (
    ProjectSummary,
    mapToSchema,
    mapFromSchema,
    userProject,
    Project,
)

__all__ = [
    "add_project_summary",
    "update_project_summary",
    "get_project_summary",
    "get_all_project_summary",
    "update_row_project_summary",
    "get_user_project_summary",
    "get_recent_project_summary",
    "get_project_id_row",
    "get_published_project_summary",
]


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
        request.dbsession.query(ProjectSummary).filter(
            ProjectSummary.project_id == project_id
        ).update(mapped_data)
        return True, ""
    except Exception as e:
        return False, e


def update_row_project_summary(data, project_id, request):
    mappedData = mapToSchema(ProjectSummary, data)
    try:
        request.dbsession.query(ProjectSummary).filter(
            ProjectSummary.project_id == project_id
        ).update(mappedData)
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

    res = mapFromSchema(request.dbsession.query(ProjectSummary).all())
    all_project = []
    for data in res:
        data["psm_json"]["admin_user_name"] = data["admin_user_name"]
        data["psm_json"]["admin_update_date"] = data["admin_update_date"]
        all_project.append(data["psm_json"])

    return all_project


def get_user_project_summary(request, user):

    projects = mapFromSchema(
        request.dbsession.query(ProjectSummary)
        .filter(userProject.user_name == user)
        .filter(Project.project_id == userProject.project_id)  ###revisar acá
        .filter(ProjectSummary.project_id == Project.project_id)
        .order_by(Project.project_creationdate.desc())
        .all()
    )

    user_projects = []
    for project in projects:
        project["psm_json"]["admin_user_name"] = project["admin_user_name"]
        project["psm_json"]["admin_update_date"] = project["admin_update_date"]
        user_projects.append(project["psm_json"])
    return user_projects


def get_recent_project_summary(request):
    projects = request.dbsession.query(ProjectSummary).filter(
        func.json_unquote(
            func.json_extract(ProjectSummary.psm_json, "$.project_checked")
        )
        == "0"
    )

    user_projects = []

    for row in projects.all():
        row.psm_json["admin_user_name"] = row.admin_user_name
        row.psm_json["admin_update_date"] = row.admin_update_date
        user_projects.append(row.psm_json)

    return user_projects


def get_published_project_summary(request):
    projects = (
        request.dbsession.query(ProjectSummary)
        .filter(
            func.json_unquote(
                func.json_extract(ProjectSummary.psm_json, "$.project_checked")
            )
            == "1"
        )
        .filter(
            func.json_unquote(
                func.json_extract(ProjectSummary.psm_json, "$.climmob_analytics")
            )
            == "1"
        )
    )

    user_projects = []

    for row in projects.all():
        row.psm_json["admin_user_name"] = row.admin_user_name
        row.psm_json["admin_update_date"] = row.admin_update_date
        user_projects.append(row.psm_json)

    return user_projects


def get_project_id_row(request, project_id):
    res = (
        request.dbsession.query(ProjectSummary.psm_json)
        .filter(ProjectSummary.project_id == project_id)
        .first()
    )

    return res
