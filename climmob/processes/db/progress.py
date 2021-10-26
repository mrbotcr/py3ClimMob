from sqlalchemy import func
from climmob.models.schema import mapFromSchema
from ...models import Project, Assessment, userProject
from climmob.models.repository import sql_fetch_one
import logging

__all__ = ["getProjectEncrypted", "getRegistryInformation", "AssessmentsInformation"]

log = logging.getLogger(__name__)


def getProjectEncrypted(request, encrypted):

    result = (
        request.dbsession.query(Project, userProject)
        .filter(
            func.md5(func.concat(userProject.user_name, "#$%&", userProject.project_id))
            == encrypted
        )
        .filter(userProject.project_id == Project.project_id)
        .filter(userProject.access_type == 1)
        .first()
    )
    if result:

        return True, mapFromSchema(result)
    else:
        return False, ""


def getRegistryInformation(request, info):

    submissions = 0
    sql = (
        "SELECT COUNT(*) as total FROM "
        + info["user_name"]
        + "_"
        + info["project_cod"]
        + ".REG_geninfo"
    )
    try:
        res = sql_fetch_one(sql)
        submissions = res["total"]

    except:
        submissions = 0

    pending = info["project_numobs"] - submissions

    dic = {"Delivered": submissions, "Pending": pending}

    return dic


def AssessmentsInformation(request, info, registered):
    assessmentArray = []
    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == info["project_id"])
        .order_by(Assessment.ass_days)
        .all()
    )
    for assessment in assessments:
        submissions = 0

        sql = (
            "SELECT COUNT(*) as total FROM "
            + info["user_name"]
            + "_"
            + info["project_cod"]
            + ".ASS"
            + assessment.ass_cod
            + "_geninfo"
        )
        try:
            res = sql_fetch_one(sql)
            submissions = res["total"]
        except:
            submissions = 0

        pending = registered - submissions
        dic = {
            "Delivered": submissions,
            "Pending": pending,
            "Name": assessment.ass_desc,
            "Status": assessment.ass_status,
            "Id": "ass_" + str(assessment.ass_cod),
        }

        assessmentArray.append(dic)

    return assessmentArray
