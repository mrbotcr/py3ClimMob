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
    CropTaxonomy,
)
import shutil as sh
import pandas as pd
import numpy as np
import transaction
import datetime
import json
import os

from climmob.config.celery_app import celeryApp
from climmob.config.celery_class import celeryTask

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


def getTheTechOfTheProject(dbsession, projectId):

    crop = (
        dbsession.query(Technology)
        .filter(Prjtech.project_id == projectId)
        .filter(Technology.tech_id == Prjtech.tech_id)
        .first()
    )
    return mapFromSchema(crop)


def getTheCropOfTheProject(dbsession, projectId):

    crop = (
        dbsession.query(CropTaxonomy)
        .filter(Prjtech.project_id == projectId)
        .filter(Technology.tech_id == Prjtech.tech_id)
        .filter(Technology.croptaxonomy_code == CropTaxonomy.taxonomy_code)
        .first()
    )

    return mapFromSchema(crop)


def getNumberOfVarietiesInProject(projectId):

    sql = "SELECT count(*) as prjalias FROM prjalias where project_id='{}'".format(
        projectId
    )

    try:
        result = sql_execute(sql).one()
        if result:
            count = result[0]
            return count
        return 0
    except Exception as e:
        print("getNumberOfVarietiesInProject")
        print(str(e))
        return "0"


def getGender(projectId, user, projectCod, genderQuestions):

    numberOfMan = 0
    numberOfWoman = 0
    numberOfOther = 0
    resultGender = None

    try:
        # Search gender in the registry
        sqlRegistry = "SELECT r.question_id, q.question_code FROM registry r, question q where r.question_id in ({}) and r.project_id='{}' and r.question_id=q.question_id LIMIT 1".format(
            genderQuestions, projectId
        )

        result = sql_execute(sqlRegistry)
        qst_code = result.all()
        if qst_code:
            qst_code = qst_code[0][1]
            try:
                sqlGender = "SELECT {}_opts_des as optdesc, count(*) as quantity FROM {}_{}.REG_geninfo, {}_{}.REG_lkp{}_opts WHERE {} = {}_opts_cod GROUP BY {}_opts_des;".format(
                    qst_code,
                    user,
                    projectCod,
                    user,
                    projectCod,
                    qst_code,
                    qst_code,
                    qst_code,
                    qst_code,
                )
                resultGender = sql_execute(sqlGender).all()

            except Exception as e:
                print(
                    "Error en el query de registry gender project: {}".format(projectId)
                )
                print(str(e))
        else:
            sqlAssessment = "SELECT r.ass_cod, r.question_id, q.question_code FROM assdetail r, question q where r.question_id in ({}) and r.project_id='{}' and r.question_id=q.question_id LIMIT 1".format(
                genderQuestions, projectId
            )
            result = sql_execute(sqlAssessment)
            qst_code = result.all()
            if qst_code:
                ass_code = qst_code[0][0]
                qst_code = qst_code[0][2]
                try:
                    sqlGender = "SELECT {}_opts_des as optdesc, count(*) as quantity FROM {}_{}.ASS{}_geninfo, {}_{}.ASS{}_lkp{}_opts WHERE {} = {}_opts_cod GROUP BY {}_opts_des;".format(
                        qst_code,
                        user,
                        projectCod,
                        ass_code,
                        user,
                        projectCod,
                        ass_code,
                        qst_code,
                        qst_code,
                        qst_code,
                        qst_code,
                    )
                    resultGender = sql_execute(sqlGender).all()

                except Exception as e:
                    print(
                        "Error en el query de assessment gender project: {} assessment: {}".format(
                            projectId, ass_code
                        )
                    )
                    print(str(e))

        if resultGender:
            for val in resultGender:
                if val[0] in ["Woman", "Female", "Female ", "Femelle", "Mujer"]:
                    numberOfWoman = numberOfWoman + val[1]

                else:
                    if val[0] in ["Man", "Male", "Male ", "Mâle", "Hombre"]:
                        numberOfMan = numberOfMan + val[1]

                    else:
                        numberOfOther = numberOfOther + val[1]

    except Exception as e:
        print("getGender")
        print(str(e))

    return numberOfMan, numberOfWoman, numberOfOther


def getTheStartAndEndDateOfProject(projectId, user, projectCod, dbsession):

    startDates = []
    endDates = []

    sqlRegistry = "select Min(clm_start), max(clm_end) FROM {}_{}.REG_geninfo".format(
        user, projectCod
    )

    try:
        resultR = sql_execute(sqlRegistry).one()
        startDates.append(resultR[0])
        endDates.append(resultR[1])
    except Exception as e:
        print("getTheStartAndEndDateOfProject")
        print(e)
        pass

    assessments = (
        dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_status > 0)
        .order_by(Assessment.ass_days)
        .all()
    )

    for assessment in assessments:

        sqlAssessments = (
            "SELECT Min(clm_start), max(clm_end) FROM {}_{}.ASS{}_geninfo ".format(
                user, projectCod, assessment.ass_cod
            )
        )

        try:
            resultA = sql_execute(sqlAssessments).one()
            startDates.append(resultA[0])
            endDates.append(resultA[1])
        except Exception as e:
            print("getTheStartAndEndDateOfProject")
            print(str(e))
            pass

    startDates = [i for i in startDates if i is not None]
    endDates = [i for i in endDates if i is not None]
    try:
        return min(startDates), max(endDates)
    except:
        return "", ""


def numberOfRegisteredParticipants(user, projectCod):

    sql = "SELECT count(*) as count FROM " + user + "_" + projectCod + ".REG_geninfo "

    try:
        result = sql_execute(sql).one()
        if result:
            count = result[0]
            return count
        return "0"
    except Exception as e:
        print("numberOfRegisteredParticipants")
        print(str(e))
        return "0"


def numberOfRegisteredParticipantsByAssessment(projectId, user, projectCod, dbsession):

    assessments = mapFromSchema(
        dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .order_by(Assessment.ass_days)
        .all()
    )

    for assessment in assessments:

        sqlAssessments = "SELECT count(*) as count FROM {}_{}.ASS{}_geninfo ".format(
            user, projectCod, assessment["ass_cod"]
        )

        if assessment["ass_status"] == 0:
            assessment["ass_status"] = "Not yet started"
        else:
            if assessment["ass_status"] == 1:
                assessment["ass_status"] = "On going"
            else:
                assessment["ass_status"] = "Closed"

        try:
            result = sql_execute(sqlAssessments).one()
            if result:
                count = result[0]
                assessment["number_submissions"] = count
            else:
                assessment["number_submissions"] = 0
        except Exception as e:
            print("numberOfRegisteredParticipantsByAssessment")
            print(str(e))
            assessment["number_submissions"] = 0

    return assessments


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
            Project.project_abstract,
            Project.project_registration_and_analysis,
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
            Project.project_abstract,
            Project.project_registration_and_analysis,
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


def processForGetTheGenotypes(projectId):

    sql = (
        "SELECT "
        "project.project_id, "
        "project.project_pi as trial_pi, "
        "project.project_piemail as pi_email, "
        "(SELECT technology.tech_name FROM technology where technology.tech_id = prjalias.tech_id) as crop_name, "
        "("
        "	SELECT COALESCE((SELECT alias_name FROM techalias where tech_id=tech_used and alias_id=alias_used), alias_name) as genotype "
        ") as genotype "
        "FROM project, prjalias "
        "WHERE "
        "project.project_id = prjalias.project_id AND "
        "project.project_id='{}';"
    ).format(projectId)
    try:
        result = sql_execute(sql)
        return True, result
    except:
        return False, {}


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


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
        listOfGenotypes = []
        listOfDataCollectionMoments = []
        for project in getListOfProjects(dbsession):
            cantidad += 1
            print(cantidad)

            num = numberOfRegisteredParticipants(
                project["user_name"], project["project_cod"]
            )

            startDate, endDate = getTheStartAndEndDateOfProject(
                project["project_id"],
                project["user_name"],
                project["project_cod"],
                dbsession,
            )

            if startDate:
                startDate = startDate.strftime("%d-%m-%Y")
            if endDate:
                endDate = endDate.strftime("%d-%m-%Y")

            crop = getTheCropOfTheProject(dbsession, project["project_id"])
            tech = getTheTechOfTheProject(dbsession, project["project_id"])
            aliasNumber = getNumberOfVarietiesInProject(project["project_id"])
            genderMan, genderWoman, genderOther = getGender(
                project["project_id"],
                project["user_name"],
                project["project_cod"],
                settings["analytics.gender"],
            )

            if tech:
                tech = tech["tech_name"]
            else:
                tech = ""

            if crop:
                crop = crop["taxonomy_name"]

            else:
                crop = "No assigned"

            if project["project_registration_and_analysis"] == 0:
                project_type = "On-farm testing"
            else:
                project_type = "Consumer/Market testing"

            result = {
                "user_owner": project["user_name"],
                "project_id": project["project_id"],
                "project_cod": project["project_cod"],
                "projectTitle": project["project_name"],
                "projectDesc": project["project_abstract"],
                "project_pi": project["project_pi"],
                "project_piorganization": project["user_organization"],
                "project_piemail": project["project_piemail"],
                "project_date": project["project_creationdate"].strftime("%d-%m-%Y"),
                "project_country": project["cnty_name"],
                "project_type": project_type,
                "farmers_target": project["project_numobs"],
                "farmers_registered": num,
                "gender_man": genderMan,
                "gender_woman": genderWoman,
                "gender_other": genderOther,
                "gender_unreported": int(num) - genderMan - genderWoman - genderOther,
                "crop": crop,
                "technology": tech,
                "startDate": startDate,
                "endDate": endDate,
                "instance_name": settings.get("analytics.instancename", ""),
                "varieties_quantity": aliasNumber,
            }

            registry, infoOfCoordinates = getTheFirstGeoPointQuestionCodeInRegistry(
                project["project_id"],
                project["user_name"],
                project["project_cod"],
                dbsession,
            )
            LatitudeR = None
            LongitudeR = None
            if registry:

                LatitudeR, LongitudeR = processTheProjectCoordinates(infoOfCoordinates)

            result["LatitudeRegistry"] = LatitudeR
            result["LongitudeRegistry"] = LongitudeR

            LatitudeA = None
            LongitudeA = None

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
                LatitudeA, LongitudeA = processTheProjectCoordinates(infoOfCoordinates)

            result["LatitudeAssessment"] = LatitudeA
            result["LongitudeAssessment"] = LongitudeA

            listOfProjects.append(result)

            resultGeno, genotypes = processForGetTheGenotypes(project["project_id"])

            if resultGeno:
                for genotype in genotypes:

                    resultGenotypes = {
                        "project_id": genotype.project_id,
                        "trial_pi": genotype.trial_pi,
                        "pi_email": genotype.pi_email,
                        "country": project["cnty_name"],
                        "crop_name": genotype.crop_name,
                        "genotype": genotype.genotype,
                        "instance_name": settings.get("analytics.instancename", ""),
                    }
                    listOfGenotypes.append(resultGenotypes)

            infoDataCollectionMoments = numberOfRegisteredParticipantsByAssessment(
                project["project_id"],
                project["user_name"],
                project["project_cod"],
                dbsession,
            )

            if infoDataCollectionMoments:

                for dataCollectionMoment in infoDataCollectionMoments:

                    resultDataCollectionMoment = {
                        "project_id": project["project_id"],
                        "trial_pi": project["project_pi"],
                        "pi_email": project["project_piemail"],
                        "country": project["cnty_name"],
                        "code": dataCollectionMoment["ass_cod"],
                        "description": dataCollectionMoment["ass_desc"],
                        "status": dataCollectionMoment["ass_status"],
                        "number_submissions": dataCollectionMoment[
                            "number_submissions"
                        ],
                        "instance_name": settings.get("analytics.instancename", ""),
                    }
                    listOfDataCollectionMoments.append(resultDataCollectionMoment)

        projectsSummary = "projectsSummary"
        genotypesSummary = "genotypesSummary"
        dataCollectionMomentsSummary = "dataCollectionMomentsSummary"

        with open(
            os.path.join(
                jsonLocation,
                "{}_{}.json".format(
                    projectsSummary, settings.get("analytics.instancename", "")
                ),
            ),
            "w",
        ) as json_data:
            json.dump(listOfProjects, json_data, default=myconverter)

        df = pd.read_json(
            os.path.join(
                jsonLocation,
                "{}_{}.json".format(
                    projectsSummary, settings.get("analytics.instancename", "")
                ),
            )
        )
        df.to_excel(
            os.path.join(
                jsonLocation,
                "{}_{}.xlsx".format(
                    projectsSummary, settings.get("analytics.instancename", "")
                ),
            ),
            index=False,
        )

        with open(
            os.path.join(
                jsonLocation,
                "{}_{}.json".format(
                    genotypesSummary, settings.get("analytics.instancename", "")
                ),
            ),
            "w",
        ) as jsongeno_data:
            json.dump(listOfGenotypes, jsongeno_data, default=myconverter)

        df = pd.read_json(
            os.path.join(
                jsonLocation,
                "{}_{}.json".format(
                    genotypesSummary, settings.get("analytics.instancename", "")
                ),
            )
        )
        df.to_excel(
            os.path.join(
                jsonLocation,
                "{}_{}.xlsx".format(
                    genotypesSummary, settings.get("analytics.instancename", "")
                ),
            ),
            index=False,
        )

        with open(
            os.path.join(
                jsonLocation,
                "{}_{}.json".format(
                    dataCollectionMomentsSummary,
                    settings.get("analytics.instancename", ""),
                ),
            ),
            "w",
        ) as jsondatacollection_data:
            json.dump(
                listOfDataCollectionMoments,
                jsondatacollection_data,
                default=myconverter,
            )

        df = pd.read_json(
            os.path.join(
                jsonLocation,
                "{}_{}.json".format(
                    dataCollectionMomentsSummary,
                    settings.get("analytics.instancename", ""),
                ),
            )
        )
        df.to_excel(
            os.path.join(
                jsonLocation,
                "{}_{}.xlsx".format(
                    dataCollectionMomentsSummary,
                    settings.get("analytics.instancename", ""),
                ),
            ),
            index=False,
        )

        # except Exception as e:
        #    print(str(e))
        #    error = 1
    engine.dispose()

    if settings.get("analytics.active", "false") == "true":
        if settings.get("analytics.sqlalchemy.url", "") != settings.get(
            "sqlalchemy.url"
        ):
            engine = create_engine(
                settings.get("analytics.sqlalchemy.url", ""),
                poolclass=NullPool,
            )
            Session = sessionmaker(bind=engine)
            dbsession = Session()

            try:
                dbsession.execute(
                    "DELETE FROM {} WHERE instance_name='{}'".format(
                        "climmob_details", settings.get("analytics.instancename", "")
                    )
                )

                for project in listOfProjects:

                    columns = project.keys()
                    cols_comma_separated = ", ".join(columns)

                    binds_comma_separated = ""
                    for item in columns:
                        before = ", "
                        if binds_comma_separated == "":
                            before = ""

                        if project[item]:
                            binds_comma_separated += (
                                before + "'" + str(project[item]).replace("'", "") + "'"
                            )
                        else:
                            binds_comma_separated += before + "null"

                    sql = "INSERT INTO {} ({}) VALUES ({})".format(
                        "climmob_details",
                        cols_comma_separated,
                        binds_comma_separated,
                    )
                    try:
                        dbsession.execute(sql)
                    except Exception as e:
                        print(str(e))

            except Exception as e:
                print(str(e))

            dbsession.commit()
            dbsession.close()

    return ""
