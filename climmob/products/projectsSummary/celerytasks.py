from climmob.models import get_engine, get_session_factory, get_tm_session
from climmob.models.repository import sql_execute
from climmob.models.meta import Base
from climmob.models import (
    Project,
    mapFromSchema,
    Registry,
    Question,
    AssDetail,
    Assessment,
    User,
    Prjtech,
    userProject,
    Country,
    Technology,
)
import shutil as sh
import pandas as pd
import numpy as np
import transaction
import json
import os

from climmob.config.celery_app import celeryApp
from climmob.config.celery_class import celeryTask


def numberOfRegisteredParticipants(user, projectCod):

    sql = "SELECT count(*) as count FROM " + user + "_" + projectCod + ".REG_geninfo "

    try:
        print(sql)
        result = sql_execute(sql)
        print(result)
        count = result.one()[0]
        return count
    except Exception as e:
        print(str(e))
        return "-"


def getTheFirstGeoPointQuestionCodeInRegistry(projectId, user, projectCod, dbsession):
    registryHaveGeolocation = (
        dbsession.query(Question.question_code)
        .filter(Question.question_id == Registry.question_id)
        .filter(Registry.project_id == projectId)
        .filter(Question.question_dtype == 4)
        .first()
    )

    if registryHaveGeolocation:
        sql = (
            "SELECT SUBSTRING_INDEX("
            + registryHaveGeolocation[0]
            + ", ' ', 1) AS Latitude, SUBSTRING_INDEX(SUBSTRING_INDEX("
            + registryHaveGeolocation[0]
            + ", ' ', 2), ' ', -1) AS Longitude FROM "
            + user
            + "_"
            + projectCod
            + ".REG_geninfo "
        )

        try:
            result = sql_execute(sql)
            return True, result
        except:
            return False, {}

    return False, {}


def getTheFirstGeoPointQuestionCodeInAssessment(projectId, user, projectCod, dbsession):
    assessments = (
        dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_status > 0)
        .order_by(Assessment.ass_days)
        .all()
    )

    for assessment in assessments:

        assessmentHaveGeolocation = (
            dbsession.query(Question.question_code)
            .filter(Question.question_id == AssDetail.question_id)
            .filter(AssDetail.project_id == projectId)
            .filter(AssDetail.ass_cod == assessment.ass_cod)
            .filter(Question.question_dtype == 4)
            .first()
        )

        if assessmentHaveGeolocation:
            sql = (
                "SELECT SUBSTRING_INDEX("
                + assessmentHaveGeolocation[0]
                + ", ' ', 1) AS Latitude, SUBSTRING_INDEX(SUBSTRING_INDEX("
                + assessmentHaveGeolocation[0]
                + ", ' ', 2), ' ', -1) AS Longitude FROM "
                + user
                + "_"
                + projectCod
                + ".ASS"
                + assessment.ass_cod
                + "_geninfo "
            )

            try:
                result = sql_execute(sql)
                return True, result
            except:
                return False, {}

    return False, {}


def calculationOfFinalCoordinates(listOfLatitude, listOfLongitude):
    # calculation of the percentil 25 and 75 for latitude
    perc25latitude = np.percentile(listOfLatitude, 25)
    perc75latitude = np.percentile(listOfLatitude, 75)
    # calculation of the percentil 25 and 75 for longitude
    perc25longitude = np.percentile(listOfLongitude, 25)
    perc75longitude = np.percentile(listOfLongitude, 75)
    # calculation of the average for latitude and longitude
    averageLatitude = (perc25latitude + perc75latitude) / 2
    averageLongitude = (perc25longitude + perc75longitude) / 2
    # return the coordinates obtained
    return averageLatitude, averageLongitude


def processTheProjectCoordinates(
    infoInTheProject,
):
    listOfLatitude = []
    listOfLongitude = []
    minimunNumberOfPoints = 5
    # The minimum number of points allowed
    if infoInTheProject.rowcount > minimunNumberOfPoints:
        # Iterates each point and adds it to a list in case it is not null
        for res in infoInTheProject:
            if res[0] and res[0] != "null":
                try:
                    listOfLatitude.append(float(res[0]))
                    listOfLongitude.append(float(res[1]))
                except:
                    print("Some values are incorrect")
        # if the valid points are more than 5
        if len(listOfLatitude) > minimunNumberOfPoints:
            averageLatitude, averageLongitude = calculationOfFinalCoordinates(
                listOfLatitude, listOfLongitude
            )

            return averageLatitude, averageLongitude

    return False, False


def getListOfProjects(dbsession):

    # check the technologies to exclude Colors for example

    exclude = dbsession.query(Prjtech.project_id).filter(Prjtech.tech_id.in_([78, 76]))

    projectsWithCountry = (
        dbsession.query(
            Project.project_id,
            Project.project_cod,
            Project.project_name,
            Project.project_numobs,
            Project.project_pi,
            Project.project_piemail,
            Project.project_creationdate,
            User.user_organization,
            userProject.user_name,
            Country.cnty_name,
        )
        .filter(Project.project_id == userProject.project_id)
        .filter(Project.project_cnty == Country.cnty_cod)
        .filter(userProject.access_type == 1)
        .filter(User.user_name == userProject.user_name)
        .filter(Project.project_active == 1)
        .filter(Project.project_id.not_in(exclude))
        .all()
    )

    projectsWithoutCountry = (
        dbsession.query(
            Project.project_id,
            Project.project_cod,
            Project.project_name,
            Project.project_numobs,
            Project.project_pi,
            Project.project_piemail,
            Project.project_creationdate,
            User.user_organization,
            userProject.user_name,
            Project.project_cnty.label("cnty_name"),
        )
        .filter(Project.project_id == userProject.project_id)
        .filter(Project.project_cnty.is_(None))
        .filter(userProject.access_type == 1)
        .filter(User.user_name == userProject.user_name)
        .filter(Project.project_active == 1)
        .filter(Project.project_id.not_in(exclude))
        .all()
    )

    return projectsWithCountry + projectsWithoutCountry


def getTheCropOfTheProject(dbsession, projectId):

    crop = (
        dbsession.query(Technology)
        .filter(Prjtech.project_id == projectId)
        .filter(Technology.tech_id == Prjtech.tech_id)
        .first()
    )

    return mapFromSchema(crop)


@celeryApp.task(bind=True, base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createProjectsSummary(self, settings, otro):
    jsonLocation = os.path.join(settings["user.repository"], "_report")
    if os.path.exists(jsonLocation):
        sh.rmtree(jsonLocation)

    os.makedirs(jsonLocation)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        # try:
        cantidad = 0
        listOfProjects = []
        for project in getListOfProjects(dbsession):
            cantidad += 1
            print(cantidad)

            num = numberOfRegisteredParticipants(
                project["user_name"], project["project_cod"]
            )

            crop = {}

            if crop:
                crop = crop["tech_name"]
            else:
                crop = "No crop assigned"

            result = {
                "user_owner": project["user_name"],
                "project_id": project["project_id"],
                "project_cod": project["project_cod"],
                "project_name": project["project_name"],
                "project_pi": project["project_pi"],
                "project_piorganization": project["user_organization"],
                "project_piemail": project["project_piemail"],
                "project_date": project["project_creationdate"].strftime("%d-%m-%Y"),
                "project_country": project["cnty_name"],
                "project_numobs": project["project_numobs"],
                "NumberOfRegisteredParticipants": num,
                "crop": crop,
            }

            registry, infoOfCoordinates = getTheFirstGeoPointQuestionCodeInRegistry(
                project["project_id"],
                project["user_name"],
                project["project_cod"],
                dbsession,
            )
            Latitude = None
            Longitude = None
            if registry:

                Latitude, Longitude = processTheProjectCoordinates(infoOfCoordinates)

            else:

                (
                    assessment,
                    infoOfCoordinates,
                ) = getTheFirstGeoPointQuestionCodeInAssessment(
                    project["project_id"],
                    project["user_name"],
                    project["project_cod"],
                    dbsession,
                )

                if assessment:
                    Latitude, Longitude = processTheProjectCoordinates(
                        infoOfCoordinates
                    )

            if Latitude:
                result["Latitude"] = Latitude
                result["Longitude"] = Longitude

            listOfProjects.append(result)

        with open(os.path.join(jsonLocation, "projectsSummary.json"), "w") as json_data:
            json.dump(listOfProjects, json_data)

        df = pd.read_json(os.path.join(jsonLocation, "projectsSummary.json"))
        df.to_excel(os.path.join(jsonLocation, "projectsSummary.xlsx"), index=False)

        # except Exception as e:
        #    print(str(e))
        #    error = 1
    engine.dispose()

    return ""
