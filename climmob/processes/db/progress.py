from sqlalchemy import func
from climmob.models.schema import mapFromSchema, mapToSchema
from ...models import Project, Assessment
from .project import (
    addQuestionsToAssessment,
    numberOfCombinationsForTheProject,
    getProjectLocalVariety,
)
from ..odk.generator import getRegisteredFarmers
import uuid, os
from subprocess import Popen, PIPE
import logging, shutil
from jinja2 import Environment

__all__ = ["getProjectEncrypted", "getRegistryInformation", "AssessmentsInformation"]

log = logging.getLogger(__name__)


def getProjectEncrypted(request, encrypted):
    # sql ="SELECT * FROM project where MD5(concat(user_name,'#$%&',project_cod)) = '"+encrypted+"'"
    # result = request.dbsession.execute(sql).fetchall()
    result = (
        request.dbsession.query(Project)
        .filter(
            func.md5(func.concat(Project.user_name, "#$%&", Project.project_cod))
            == encrypted
        )
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
        res = request.repsession.execute(sql).fetchone()
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
        .filter(Assessment.user_name == info["user_name"])
        .filter(Assessment.project_cod == info["project_cod"])
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
            res = request.repsession.execute(sql).fetchone()
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
