from ...models import  mapToSchema,mapFromSchema
from ...models.climmobv4 import Question_group
from sqlalchemy import or_
__all__ = [
    'categoryExists','addCategory','getCategories','updateCategory','deleteCategory'
]



def categoryExists(user,name,request):
    result = request.dbsession.query(Question_group).filter(or_(Question_group.user_name == user, Question_group.user_name == 'bioversity') ).filter(Question_group.qstgroups_name == name).first()

    if result:
        return True
    else:
        return False

def addCategory(user,data,request):
    data["user_name"] = user
    mappedData = mapToSchema(Question_group, data)
    newCategory = Question_group(**mappedData)
    try:
        request.dbsession.add(newCategory)
        return True, ""
    except Exception as e:
        return False, str(e)

def getCategories(user, request):
    sql =   "select qstgroups.user_name,qstgroups.qstgroups_id, qstgroups_name,(select count(question.question_id)from question where question.qstgroups_id = qstgroups.qstgroups_id " \
            "and question.qstgroups_user = qstgroups.user_name) as count " \
            "from qstgroups where (qstgroups.user_name = '" + user +"' or qstgroups.user_name = 'bioversity')"
    data = request.dbsession.execute(sql).fetchall()

    return data

def updateCategory(user, data,request):
    mappedData = mapToSchema(Question_group, data)
    try:
        request.dbsession.query(Question_group).filter(Question_group.user_name == user).filter(Question_group.qstgroups_id == data["qstgroups_id"]).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e

def deleteCategory(user, id, request):
    try:
        request.dbsession.query(Question_group).filter(Question_group.user_name == user).filter(Question_group.qstgroups_id == id).delete()
        return True,""
    except Exception as e:
        print (str(e))
        return False, e