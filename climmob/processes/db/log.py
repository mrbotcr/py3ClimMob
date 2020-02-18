from ...models import Activitylog

__all__ = [
    'addToLog'
]

def addToLog(log_user,log_type,log_message,request):
    newLog = Activitylog(log_user=log_user,log_type=log_type,log_message=log_message)
    try:
        request.dbsession.add(newLog) #Add the new log to MySQL
        return True
    except:
        return False