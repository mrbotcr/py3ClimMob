from ...models import Activitylog, mapFromSchema

__all__ = ["addToLog", "getLastActivityLogByUser"]


def addToLog(log_user, log_type, log_message, log_datetime, request):
    newLog = Activitylog(
        log_user=log_user,
        log_type=log_type,
        log_message=log_message,
        log_datetime=log_datetime,
    )
    try:
        request.dbsession.add(newLog)  # Add the new log to MySQL
        return True
    except:
        return False


def getLastActivityLogByUser(log_user, request):
    result = (
        request.dbsession.query(Activitylog)
        .filter(Activitylog.log_user == log_user)
        .order_by(Activitylog.log_datetime.desc())
        .first()
    )

    if result:
        return mapFromSchema(result)
    else:
        return None
