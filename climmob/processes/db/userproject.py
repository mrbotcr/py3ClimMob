from climmob.models import userProject, mapFromSchema

__all__ = ["getAllProjectsByUser"]


def getAllProjectsByUser(user, request):
    mappedData = mapFromSchema(
        request.dbsession.query(userProject)
        .filter(userProject.user_name == user)
        .first()
    )
    return mappedData
