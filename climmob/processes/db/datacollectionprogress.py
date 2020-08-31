from ..db.project import getProjectData
from ...models import Assessment

__all__ = [
    "getInformationFromProject",
]

def getInformationFromProject(request, user ,projectid):

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
    result = mySession.execute(sql)

    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == projectid)
        .filter(Assessment.ass_status > 0)
        .all()
    )

    packagesInformation = []
    for res in result:
        individualInformation = {}
        individualInformation["name"] = res[0]
        individualInformation["date"] = str(res[1]).split(" ")[0]
        individualInformation["package"] = res[2]
        packagesInformation.append(individualInformation)

    assessmentsInformation = []
    for assessment in assessments:
        assessmentDetails = {}
        assessmentDetails["name"] = assessment.ass_desc
        assessmentDetails["data"] = []
        sql = (
                "select qst163"
                + " from "
                + user
                + "_"
                + projectid
                + ".ASS"+assessment.ass_cod+"_geninfo "
        )
        mySession = request.dbsession
        result = mySession.execute(sql)

        for res in result:
            assessmentDetails["data"].append(res[0])

        assessmentsInformation.append(assessmentDetails)



    return { "projectInfo": getProjectData(user,projectid,request), "packagesRegistryInfo": packagesInformation, "assessmentsDetails": assessmentsInformation }