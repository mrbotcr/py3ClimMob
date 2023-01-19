import argparse
import json
import os

import numpy as np
import transaction
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import tuple_

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
)
from climmob.models import get_engine, get_session_factory, get_tm_session
from climmob.models.meta import Base
from climmob.models.repository import sql_execute


def getProjectWithGeoPointInRegistry(dbsession):
    exclude = dbsession.query(Prjtech.project_id).filter(Prjtech.tech_id.in_([78, 76]))

    searchGeoPoint = (
        dbsession.query(Registry.project_id)
        .filter(Registry.question_id == Question.question_id)
        .filter(Question.question_dtype == 4)
    )

    result = (
        dbsession.query(
            Project.project_id,
            Project.project_cod,
            Project.project_name,
            Project.project_numobs,
            Project.project_pi,
            Project.project_piemail,
            Project.project_creationdate,
            User.user_fullname,
            User.user_organization,
            User.user_name,
        )
        .filter(userProject.project_id == Project.project_id)
        .filter(userProject.access_type == 1)
        .filter(userProject.user_name == User.user_name)
        .filter(Project.project_id.in_(searchGeoPoint))
        .filter(Project.project_regstatus > 0)
        .filter(Project.project_id.not_in(exclude))
        .all()
    )

    return mapFromSchema(result)


def getProjectWithGeoPointInAssessment(dbsession):
    exclude = dbsession.query(Prjtech.project_id).filter(Prjtech.tech_id.in_([78, 76]))

    searchGeoPointRegistry = (
        dbsession.query(Registry.project_id)
        .filter(Registry.question_id == Question.question_id)
        .filter(Question.question_dtype == 4)
    )

    searchGeoPointAssessment = (
        dbsession.query(AssDetail.project_id)
        .filter(AssDetail.question_id == Question.question_id)
        .filter(Question.question_dtype == 4)
    )

    searchAssessmentsOpen = (
        dbsession.query(Assessment.project_id)
        .filter(Assessment.ass_status > 0)
        .filter(Assessment.project_id.in_(searchGeoPointAssessment))
    )

    subquery = (
        dbsession.query(Project.project_cod, userProject.user_name)
        .filter(userProject.project_id == Project.project_id)
        .filter(userProject.access_type == 1)
        .filter(Project.project_id.in_(searchGeoPointRegistry))
        .filter(Project.project_regstatus > 0)
        .filter(Project.project_id.not_in(exclude))
        .all()
    )
    result = (
        dbsession.query(
            Project.project_id,
            Project.project_cod,
            Project.project_name,
            Project.project_numobs,
            Project.project_pi,
            Project.project_piemail,
            Project.project_creationdate,
            User.user_fullname,
            User.user_organization,
            User.user_name,
        )
        .filter(tuple_(Project.project_cod, userProject.user_name).notin_(subquery))
        .filter(userProject.project_id == Project.project_id)
        .filter(userProject.access_type == 1)
        .filter(userProject.user_name == User.user_name)
        .filter(Project.project_id.in_(searchAssessmentsOpen))
        .filter(Project.project_id.not_in(exclude))
        .all()
    )
    return mapFromSchema(result)


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


def processTheProject(
    project,
    infoInTheProject,
):
    listOfLatitude = []
    listOfLongitude = []
    minimunNumberOfPoints = 5
    # The minimum number of points allowed
    if infoInTheProject.rowcount > minimunNumberOfPoints:
        print("_____" + project["project_cod"])
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

            result = {
                "project_name": project["project_name"],
                "Latitude": averageLatitude,
                "Longitude": averageLongitude,
                "numberOfParticipantsCollected": infoInTheProject.rowcount,
                "project_numobs": project["project_numobs"],
                "project_pi": project["project_pi"],
                "project_piorganization": project["user_organization"],
                "project_piemail": project["project_piemail"],
                "project_date": project["project_creationdate"].strftime("%d-%m-%Y"),
            }

            return result

    return False


def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("ini_path", help="Path to ini file")
    args = parser.parse_args(raw_args)

    config_uri = args.ini_path

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, "climmob")
    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)
    error = 0
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        try:
            listOfProyects = []
            for project in getProjectWithGeoPointInRegistry(dbsession):
                info, infoInTheProject = getTheFirstGeoPointQuestionCodeInRegistry(
                    project["project_id"],
                    project["user_name"],
                    project["project_cod"],
                    dbsession,
                )
                if info:
                    result = processTheProject(project, infoInTheProject)
                    if result:
                        listOfProyects.append(result)

            for project in getProjectWithGeoPointInAssessment(dbsession):
                info, infoInTheProject = getTheFirstGeoPointQuestionCodeInAssessment(
                    project["project_id"],
                    project["user_name"],
                    project["project_cod"],
                    dbsession,
                )
                if info:
                    result = processTheProject(project, infoInTheProject)
                    if result:
                        listOfProyects.append(result)

            mapLocation = os.path.join(settings["user.repository"], "_map")
            if not os.path.exists(mapLocation):
                os.makedirs(mapLocation)

            with open(
                mapLocation + "/dataForProjectVisualization.json", "w"
            ) as json_data:
                json.dump(listOfProyects, json_data)

        except Exception as e:
            print(str(e))
            error = 1

    engine.dispose()
    return error
