import uuid
import datetime
from climmob.config.encdecdata import encodeData
from climmob.models import (
    User,
    mapToSchema,
    mapFromSchema,
    mapFromSchemaWithRelationships,
)
from climmob.models.repository import sql_execute

__all__ = [
    "addUser",
    "updateProfile",
    "changeUserPassword",
    "getUserCount",
    "getUserInfo",
    "update_last_login",
    "getAllUserAdmin",
]


def getUserCount(request):
    numUsers = request.dbsession.query(User).count()
    return numUsers


def addUser(userData, request):
    userData2 = userData.copy()
    userData2["user_apikey"] = str(uuid.uuid4())
    userData2["user_about"] = ""
    userData2["user_password"] = encodeData(request, userData["user_password"])
    userData2["user_joindate"] = datetime.datetime.now()

    mappedData = mapToSchema(User, userData2)
    newUser = User(**mappedData)
    try:
        request.dbsession.add(newUser)  # Add the ne user to MySQL
        return True, ""
    except Exception as e:
        return False, str(e)


def updateProfile(user, data, request):
    try:
        mappedData = mapToSchema(User, data)
        request.dbsession.query(User).filter_by(user_name=user).update(mappedData)
        return True, ""
    except Exception as e:
        return False, str(e)


def changeUserPassword(user, password, request):
    try:
        request.dbsession.query(User).filter_by(user_name=user).update(
            {"user_password": encodeData(request, password)}
        )
        return True
    except:
        return False


def getUserInfo(request, user_name):
    result = request.dbsession.query(User).filter(User.user_name == user_name).first()
    return mapFromSchema(result)


def update_last_login(request, user):

    string_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "UPDATE user set user_last_login = '{}' WHERE user_name = '{}';".format(
        string_date, user
    )

    sql_execute(sql)


def getAllUserAdmin(request):
    result = mapFromSchemaWithRelationships(
        request.dbsession.query(User).filter(User.user_admin == 1).all()
    )

    return result
