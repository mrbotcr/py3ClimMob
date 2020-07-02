from ...models import Country, Sector, User
from ...config.encdecdata import decodeData
import arrow

__all__ = [
    "getCountryList",
    "getSectorList",
    "getUserLog",
    "getUserStats",
    "getUserPassword",
]


def getCountryList(request):
    countries = []
    results = request.dbsession.query(Country).order_by(Country.cnty_name).all()
    for result in results:
        try:
            # name = unicode(result.cnty_name.decode('cp1252').encode('utf-8'))
            # name = str(result.cnty_name.decode('cp1252').encode('utf-8'),"utf-8")
            name = str(result.cnty_name)
            countries.append({"code": result.cnty_cod, "name": name})
        except:
            countries.append({"code": result.cnty_cod, "name": "Unknown"})
    return countries


def getSectorList(request):
    sectors = []
    results = request.dbsession.query(Sector).all()
    for result in results:
        sectors.append({"code": str(result.sector_cod), "name": result.sector_name})

    return sectors


def getUserLog(user, request, limit=True):
    sql = (
        "SELECT DATE_FORMAT(DATE(log_datetime), '%W %D of %M, %Y') as log_date,TIME(log_datetime) as log_time,log_type,log_message,log_datetime as date1,log_datetime as date2 FROM activitylog WHERE log_user = '"
        + user
        + "' ORDER BY date1 DESC,date2 ASC,log_id desc"
    )
    if limit:
        sql = sql + " LIMIT 20"

    activities = request.dbsession.execute(sql)
    items = []
    count = 1
    for activity in activities:
        if count % 2 == 0:
            alt = False
        else:
            alt = True
        count = count + 1
        if activity[2] == "PRF":
            color = "navy-bg"
            icon = "fa-user"
            desType = "Profile"
        else:
            if activity[2] == "PRJ":
                color = "blue-bg"
                icon = "fa-briefcase"
                desType = "Project"
            else:
                if activity[2] == "ANA":
                    color = "lazur-bg"
                    icon = "fa-flask"
                    desType = "Analysis"
                else:
                    if activity[2] == "API":
                        color = "yellow-bg"
                        icon = "fa-bolt"
                        desType = "API"
                    else:
                        color = "gray-bg"
                        icon = "fa-cogs"
                        desType = "Other"

        items.append(
            {
                "date": activity[0],
                "time": activity[1],
                "type": desType,
                "message": activity[3],
                "alt": alt,
                "icon": icon,
                "color": color,
            }
        )
    return items


def getUserStats(user, request):
    sql = "SELECT count(project_cod) FROM project WHERE user_name = '" + user + "'"
    projects = request.dbsession.execute(sql).first()

    sql = (
        "SELECT max(project_creationdate) FROM project WHERE user_name = '" + user + "'"
    )

    lastProject = request.dbsession.execute(sql).first()
    if lastProject[0] is None:
        lastProject = request.translate("Does not have projects yet")
    else:
        ar = arrow.get(lastProject[0])
        lastProject = ar.format("dddd Do of MMMM, YYYY")

    return {
        "totprojects": projects[0],
        "lastproject": lastProject,
        "totregistry": 0,
        "totassessment": 0,
    }


def getUserPassword(user, request):
    res = ""
    result = request.dbsession.query(User).filter_by(user_name=user).first()
    if not result is None:
        res = decodeData(request, result.user_password)
    return res
