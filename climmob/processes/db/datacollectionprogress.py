from ..db.project import getProjectData
from ..db.enumerator import searchEnumerator
from ...models import Assessment, Registry, Question, AssDetail
from climmob.models.repository import sql_execute

__all__ = ["getInformationFromProject","getInformationForMaps"]


def getInformationFromProject(request, user, projectid):

    sql = (
        "select farmername, clm_start, qst162"
        + " from "
        + user
        + "_"
        + projectid
        + ".REG_geninfo "
        + " order by qst162 +0"
    )
    mySession = request.dbsession
    # result = mySession.execute(sql)
    result = sql_execute(sql)

    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == projectid)
        .filter(Assessment.ass_status > 0)
        .order_by(Assessment.ass_days)
        .all()
    )

    packagesInformation = []
    for res in result:
        individualInformation = {}
        individualInformation["name"] = res[0]
        if res[1] :
            individualInformation["date"] = res[1].strftime("%d-%b")
        else:
            individualInformation["date"] = "The date is missing"
        individualInformation["package"] = res[2]
        packagesInformation.append(individualInformation)

    assessmentsInformation = []
    for assessment in assessments:
        assessmentDetails = {}
        assessmentDetails["name"] = assessment.ass_desc
        assessmentDetails["data"] = []
        sql = (
            "select qst163,clm_start"
            + " from "
            + user
            + "_"
            + projectid
            + ".ASS"
            + assessment.ass_cod
            + "_geninfo "
        )
        # mySession = request.dbsession
        # result = mySession.execute(sql)
        result = sql_execute(sql)

        for res in result:
            infoPacka = {}
            infoPacka["package"] = res[0]
            if res[1]:
                infoPacka["date"] = res[1].strftime("%d-%b")
            else:
                infoPacka["date"] = "The date is missing"
            assessmentDetails["data"].append(infoPacka)


        assessmentsInformation.append(assessmentDetails)

    return {
        "projectInfo": getProjectData(user, projectid, request),
        "packagesRegistryInfo": packagesInformation,
        "assessmentsDetails": assessmentsInformation,
    }


def getInformationForMaps(request, user, projectid):
    geoInformation = []
    colors = [
        "#1ab394",
        "#1c84c6",
        "#23c6c8",
        "#f8ac59",
        "#ed5565",
        "#a94442",
        "#3c763d",
        "#122b40",
        "#1ab394",
        "#1c84c6",
        "#23c6c8",
        "#f8ac59",
        "#ed5565",
        "#a94442",
        "#3c763d",
        "#122b40",
    ]

    registryHaveGeolocation = (
        request.dbsession.query(Question.question_code)
        .filter(Question.question_id == Registry.question_id)
        .filter(Registry.user_name == user)
        .filter(Registry.project_cod == projectid)
        .filter(Question.question_dtype == 4)
        .first()
    )

    if registryHaveGeolocation:
        geoInformationDict = {"Code": "registration", "Name": "Registration"}

        sql = (
            "select _submitted_by,"
            + registryHaveGeolocation[0]
            + " from "
            + user
            + "_"
            + projectid
            + ".REG_geninfo "
            + " order by qst162 +0"
        )
        # mySession = request.dbsession
        try:
            result = sql_execute(sql)
        except:
            result = sql_execute(sql.replace("_submitted_by","'Username is missing'"))

        geoInformationDict["fieldAgents"] = createListOfFieldAgents(
            request, user, result, colors
        )

        if len(geoInformationDict["fieldAgents"]) > 0:
            geoInformation.append(geoInformationDict)

    # else:
    #    print("No tiene gps")

    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == projectid)
        .filter(Assessment.ass_status > 0)
        .order_by(Assessment.ass_days)
        .all()
    )
    assessmentsInformation = []
    for assessment in assessments:
        assessmentHaveGeolocation = (
            request.dbsession.query(Question.question_code)
            .filter(Question.question_id == AssDetail.question_id)
            .filter(AssDetail.user_name == user)
            .filter(AssDetail.project_cod == projectid)
            .filter(AssDetail.ass_cod == assessment.ass_cod)
            .filter(Question.question_dtype == 4)
            .first()
        )

        if assessmentHaveGeolocation:
            geoInformationDict = {
                "Code": assessment.ass_cod,
                "Name": assessment.ass_desc,
            }

            sql = (
                "select _submitted_by,"
                + assessmentHaveGeolocation[0]
                + " from "
                + user
                + "_"
                + projectid
                + ".ASS"
                + assessment.ass_cod
                + "_geninfo "
            )
            # mySession = request.dbsession
            try:
                result = sql_execute(sql)
            except:
                result = sql_execute(sql.replace("_submitted_by", "'Username is missing'"))

            geoInformationDict["fieldAgents"] = createListOfFieldAgents(
                request, user, result, colors
            )

            if len(geoInformationDict["fieldAgents"]) > 0:
                geoInformation.append(geoInformationDict)
        # else:
        #    print("No tiene gps")

    return geoInformation


def createListOfFieldAgents(request, user, result, colors):
    listOfFieldAgents = []
    count = 0
    enumeratorByUser = searchEnumerator(user, request)
    for res in result:
        exits = False
        for index, element in enumerate(listOfFieldAgents):
            if listOfFieldAgents[index]["username"] == res[0]:
                listOfFieldAgents[index]["Points"].append(res[1])
                exits = True

        if not exits:
            dictOfFieldAgent = {}
            dictOfFieldAgent["username"] = res[0]
            enumerator = next(
                (item for item in enumeratorByUser if item["enum_id"] == res[0]), False
            )
            if enumerator:
                dictOfFieldAgent["Name"] = enumerator["enum_name"]
            else:
                dictOfFieldAgent["Name"] = "Other - "+res[0]

            dictOfFieldAgent["Color"] = colors[count]
            dictOfFieldAgent["Points"] = []
            dictOfFieldAgent["Points"].append(res[1])
            listOfFieldAgents.append(dictOfFieldAgent)
            count += 1

    return listOfFieldAgents
