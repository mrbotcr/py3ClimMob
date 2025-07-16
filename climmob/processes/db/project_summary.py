from climmob.models import ProjectSummary, mapToSchema, mapFromSchema, userProject, Project

__all__ = [
    "add_project_summary",
    "update_project_summary",
    "get_project_summary",
    "get_all_project_summary",
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
    try:
        request.dbsession.query(ProjectSummary).filter(
            ProjectSummary.project_id == project_id
        ).update({
            ProjectSummary.psm_json: data
        })
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

    res = mapFromSchema(request.dbsession.query(ProjectSummary.psm_json).all())
    all_project = []
    for data in res:
        all_project.append(data["psm_json"])

    return all_project

def get_user_project_summary(request, user):

    projects = mapFromSchema(
        request.dbsession.query(ProjectSummary)
        .filter(userProject.user_name == user)
        .filter(Project.project_id == userProject.project_id) ###revisar acá
        .filter(ProjectSummary.project_id == Project.project_id)
        .order_by(userProject.project_dashboard.desc())
        .order_by(Project.project_creationdate.desc())
        .all()
    )

    user_projects = []
    for project in projects:
        user_projects.append(project["psm_json"])
    return user_projects



