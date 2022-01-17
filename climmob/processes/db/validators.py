from climmob.models import User, Project, Prjtech, userProject

__all__ = [
    "userExists",
    "emailExists",
    "otherUserHasEmail",
    "projectExists",
    "projectTechnologyExists",
    "projectInDatabase",
    "projectRegStatus",
    "getTheProjectIdForOwner",
    "getAccessTypeForProject",
    "theUserBelongsToTheProject",
]


def userExists(user, request):
    res = False
    result = request.dbsession.query(User).filter_by(user_name=user).first()
    if not result is None:
        res = True
    return res


def emailExists(email, request):
    res = False
    result = request.dbsession.query(User).filter_by(user_email=email).first()
    # print(result)
    if not result is None:
        res = True
    return res


def otherUserHasEmail(user, email, request):
    res = False
    result = (
        request.dbsession.query(User)
        .filter(User.user_name != user)
        .filter_by(user_email=email)
        .first()
    )
    if not result is None:
        res = True
    return res


def getTheProjectIdForOwner(userOwner, projectCod, request):
    projectId = (
        request.dbsession.query(userProject.project_id)
        .filter(userProject.project_id == Project.project_id)
        .filter(userProject.user_name == userOwner)
        .filter(Project.project_cod == projectCod)
        .filter(userProject.access_type == 1)
        .first()
    )
    if projectId:
        return projectId[0]


def getAccessTypeForProject(user, projectId, request):

    result = (
        request.dbsession.query(userProject.access_type)
        .filter(userProject.user_name == user)
        .filter(userProject.project_id == projectId)
        .first()
    )
    if result:
        return result[0]
    else:
        return None


def theUserBelongsToTheProject(user, projectId, request):

    if user == "bioversity":
        return True

    result = (
        request.dbsession.query(userProject)
        .filter(userProject.user_name == user)
        .filter(userProject.project_id == projectId)
        .all()
    )
    if result:
        return True

    return False


def projectExists(user, userOwner, projectCod, request):
    ownerConfirmation = (
        request.dbsession.query(userProject, Project)
        .filter(userProject.project_id == Project.project_id)
        .filter(userProject.user_name == userOwner)
        .filter(Project.project_cod == projectCod)
        .filter(userProject.access_type == 1)
        .first()
    )
    if ownerConfirmation:
        result = (
            request.dbsession.query(userProject, Project)
            .filter(userProject.project_id == Project.project_id)
            .filter(
                userProject.user_name == user,
                userProject.project_id == ownerConfirmation[0].project_id,
            )
            .first()
        )

        if not result:
            return False
        else:
            if result.Project.project_active == 1:
                return True
            else:
                return False
    else:
        return False


def projectRegStatus(projectId, request):
    result = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if result.project_regstatus == 0:
        return True
    else:
        return False


def projectInDatabase(userName, projectCod, request):
    result = (
        request.dbsession.query(userProject)
        .filter(userProject.user_name == userName)
        .filter(userProject.project_id == Project.project_id)
        .filter(Project.project_cod == projectCod)
        .first()
    )
    if not result:
        return False
    else:
        return True


def projectTechnologyExists(projectId, technologyid, request):
    result = (
        request.dbsession.query(Prjtech)
        .filter(Prjtech.tech_id == technologyid)
        .filter(Prjtech.project_id == projectId)
        .first()
    )
    if not result:
        return False
    else:
        return True
