from climmob.models import userProject, mapFromSchema

__all__ = ["getAllProjectsByUser", "get_owner_user_name_by_project_id"]

from climmob.utility.project import ProjectAccessType


def getAllProjectsByUser(user, request):
    mappedData = mapFromSchema(
        request.dbsession.query(userProject)
        .filter(userProject.user_name == user)
        .first()
    )
    return mappedData


def get_owner_user_name_by_project_id(project_id, request):
    mappedData = mapFromSchema(
        request.dbsession.query(userProject.user_name)
        .filter(userProject.project_id == project_id)
        .filter(userProject.access_type == ProjectAccessType.OWNER.value)
        .first()
    )
    return mappedData["user_name"]
