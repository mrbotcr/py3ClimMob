from ...models import User, Project, Prjtech

__all__ = [
    "userExists",
    "emailExists",
    "otherUserHasEmail",
    "projectExists",
    "projectTechnologyExists",
    "projectInDatabase",
    "projectRegStatus",
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
    #print(result)
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


def projectExists(user, project, request):
    result = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user, Project.project_cod == project)
        .first()
    )
    if not result:
        return False
    else:
        if result.project_active == 1:
            return True
        else:
            return False


def projectRegStatus(user, project, request):
    result = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user, Project.project_cod == project)
        .first()
    )
    if result.project_regstatus == 0:
        return True
    else:
        return False


def projectInDatabase(user, project, request):
    result = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user, Project.project_cod == project)
        .first()
    )
    if not result:
        return False
    else:
        return True


def projectTechnologyExists(user, projectid, technologyid, request):
    result = (
        request.dbsession.query(Prjtech)
        .filter(Prjtech.tech_id == technologyid)
        .filter(Prjtech.project_cod == projectid)
        .filter(Prjtech.user_name == user)
        .first()
    )
    if not result:
        return False
    else:
        return True
