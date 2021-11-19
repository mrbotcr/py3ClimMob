from ...models import User, userProject
from ...models.schema import mapToSchema, mapFromSchema
from sqlalchemy import or_

__all__ = [
    "query_for_users",
    "add_project_collaborator",
    "get_collaborators_in_project",
    "remove_collaborator",
]


def query_for_users(request, q, query_from, query_size, projectId):
    query = q.replace("*", "")

    subquery = request.dbsession.query(userProject.user_name).filter(
        userProject.project_id == projectId
    )
    result = (
        request.dbsession.query(User)
        .filter(
            or_(
                User.user_name.ilike("%" + query + "%"),
                User.user_fullname.ilike("%" + query + "%"),
            )
        )
        .filter(User.user_name.notin_(subquery))
        .offset(query_from)
        .limit(query_size)
        .all()
    )

    result2 = (
        request.dbsession.query(User)
        .filter(User.user_name.ilike("%" + query + "%"))
        .filter(User.user_name.notin_(subquery))
        .all()
    )

    return mapFromSchema(result), len(result2)


def add_project_collaborator(request, data):

    try:
        mappedData = mapToSchema(userProject, data)
        newUserProject = userProject(**mappedData)
        try:
            request.dbsession.add(newUserProject)
            return True, ""
        except Exception as e:
            return False, str(e)

    except Exception as e:
        return False, str(e)


def get_collaborators_in_project(request, projectId):

    result = (
        request.dbsession.query(
            User.user_name,
            User.user_fullname,
            User.user_cnty,
            User.user_email,
            User.user_organization,
            userProject,
        )
        .filter(User.user_name == userProject.user_name)
        .filter(userProject.project_id == projectId)
        .order_by(userProject.access_type)
        .all()
    )

    if result:
        return mapFromSchema(result)
    else:
        return {}


def remove_collaborator(request, projectId, collaboratorId, self):
    try:
        result = (
            request.dbsession.query(userProject)
            .filter(userProject.project_id == projectId)
            .filter(userProject.user_name == collaboratorId)
            .filter(userProject.access_type != 1)
            .all()
        )
        if result:
            request.dbsession.query(userProject).filter(
                userProject.project_id == projectId
            ).filter(userProject.user_name == collaboratorId).filter(
                userProject.access_type != 1
            ).delete()
            return True, ""
        else:
            return False, self._("The project owner cannot be removed")
    except Exception as e:
        print(str(e))
        return False, e
