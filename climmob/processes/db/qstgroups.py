from ...models import mapToSchema, mapFromSchema
from ...models.climmobv4 import Question_group, Question, userProject
from sqlalchemy import or_

__all__ = [
    "categoryExists",
    "categoryExistsByUserAndId",
    "categoryExistsWithDifferentId",
    "theCategoryHaveQuestions",
    "addCategory",
    "getCategories",
    "updateCategory",
    "deleteCategory",
    "getCategoriesParents",
    "getCategoryById",
    "categoryExistsById",
    "getCategoriesFromUserCollaborators",
]


def categoryExists(user, name, request):
    result = (
        request.dbsession.query(Question_group)
        .filter(
            or_(
                Question_group.user_name == user,
                Question_group.user_name == "bioversity",
            )
        )
        .filter(Question_group.qstgroups_name == name)
        .first()
    )

    if result:
        return True
    else:
        return False


def categoryExistsWithDifferentId(user, name, id, request):
    result = (
        request.dbsession.query(Question_group)
        .filter(
            or_(
                Question_group.user_name == user,
                Question_group.user_name == "bioversity",
            )
        )
        .filter(Question_group.qstgroups_name == name)
        .filter(Question_group.qstgroups_id != id)
        .first()
    )

    if result:
        return True
    else:
        return False


def categoryExistsById(user, id, request):
    result = (
        request.dbsession.query(Question_group)
        .filter(
            or_(
                Question_group.user_name == user,
                Question_group.user_name == "bioversity",
            )
        )
        .filter(Question_group.qstgroups_id == id)
        .first()
    )

    if result:
        return mapFromSchema(result)
    else:
        return False


def categoryExistsByUserAndId(user, id, request):
    result = (
        request.dbsession.query(Question_group)
        .filter(Question_group.user_name == user)
        .filter(Question_group.qstgroups_id == id)
        .first()
    )

    if result:
        return True
    else:
        return False


def theCategoryHaveQuestions(user, id, request):
    result = (
        request.dbsession.query(Question)
        .filter(Question.qstgroups_id == id)
        .filter(Question.qstgroups_user == user)
        .all()
    )

    if result:
        return True
    else:
        return False


def addCategory(user, data, request):
    data["user_name"] = user
    mappedData = mapToSchema(Question_group, data)
    newCategory = Question_group(**mappedData)
    try:
        request.dbsession.add(newCategory)
        return True, ""
    except Exception as e:
        return False, str(e)


def getCategories(user, request):
    sql = (
        "select qstgroups.user_name,qstgroups.qstgroups_id, qstgroups_name,(select count(question.question_id)from question where question.qstgroups_id = qstgroups.qstgroups_id "
        "and question.qstgroups_user = qstgroups.user_name) as count "
        "from qstgroups where (qstgroups.user_name = '"
        + user
        + "' or qstgroups.user_name = 'bioversity')"
    )
    data = request.dbsession.execute(sql).fetchall()

    return data


def getCategoriesParents(userRegular, userOwner, request):

    sql = (
        "SELECT "
        "qstgroups.user_name, qstgroups.qstgroups_id, COALESCE(i.qstgroups_name, qstgroups.qstgroups_name) as qstgroups_name, "
        "(select count(question.question_id)from question where question.qstgroups_id = qstgroups.qstgroups_id and question.qstgroups_user = qstgroups.user_name) as count "
        "FROM qstgroups "
        "LEFT JOIN i18n_qstgroups i "
        "ON        qstgroups.user_name = i.user_name "
        "AND		  qstgroups.qstgroups_id = i.qstgroups_id "
        "AND       i.lang_code = '" + request.locale_name + "' "
        "WHERE "
        "(qstgroups.user_name = '"
        + userRegular
        + "' OR qstgroups.user_name = 'bioversity' OR qstgroups.user_name ='"
        + userOwner
        + "') "
        "and qstgroups.qstgroups_id not in (select distinct(group_id) from qstsubgroups where parent_username='bioversity')"
    )

    data = request.dbsession.execute(sql).fetchall()

    return data


def getCategoriesFromUserCollaborators(projectId, request):

    projectCollaborators = (
        request.dbsession.query(userProject.user_name)
        .filter(userProject.project_id == projectId)
        .all()
    )

    stringForFilterCategoriesByCollaborators = "qstgroups.user_name = 'bioversity'"
    if projectCollaborators:
        for user in projectCollaborators:
            stringForFilterCategoriesByCollaborators += (
                " OR qstgroups.user_name='" + user[0] + "' "
            )

    sql = (
        " SELECT "
        " qstgroups.user_name, qstgroups.qstgroups_id, COALESCE(i.qstgroups_name, qstgroups.qstgroups_name) as qstgroups_name, "
        " (select count(question.question_id)from question where question.qstgroups_id = qstgroups.qstgroups_id and question.qstgroups_user = qstgroups.user_name) as count "
        " FROM qstgroups "
        " LEFT JOIN i18n_qstgroups i "
        " ON        qstgroups.user_name = i.user_name "
        " AND		  qstgroups.qstgroups_id = i.qstgroups_id "
        " AND       i.lang_code = '" + request.locale_name + "' "
        " WHERE "
        " (" + stringForFilterCategoriesByCollaborators + " ) "
        " AND qstgroups.qstgroups_id not in (select distinct(group_id) from qstsubgroups where parent_username='bioversity')"
    )

    data = request.dbsession.execute(sql).fetchall()

    return data


def getCategoryById(qstgroups_id, request):
    res = (
        request.dbsession.query(Question_group)
        .filter(Question_group.qstgroups_id == qstgroups_id)
        .all()
    )
    result = mapFromSchema(res)

    return result


def updateCategory(user, data, request):
    mappedData = mapToSchema(Question_group, data)
    try:
        request.dbsession.query(Question_group).filter(
            Question_group.user_name == user
        ).filter(Question_group.qstgroups_id == data["qstgroups_id"]).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e


def deleteCategory(user, id, request):
    try:
        request.dbsession.query(Question_group).filter(
            Question_group.user_name == user
        ).filter(Question_group.qstgroups_id == id).delete()
        return True, ""
    except Exception as e:
        print(str(e))
        return False, e
