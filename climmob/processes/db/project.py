import datetime
import glob
import os
import uuid

from ago import human
from sqlalchemy import func

from climmob.models import (
    Project,
    mapToSchema,
    mapFromSchema,
    PrjEnumerator,
    Prjtech,
    Regsection,
    Registry,
    Question,
    AssDetail,
    Asssection,
    Assessment,
    Products,
    Prjalia,
    RegistryJsonLog,
    AssessmentJsonLog,
    userProject,
    Country,
)
from climmob.models.repository import sql_fetch_all, sql_fetch_one
from climmob.processes.db.enumerator import countEnumeratorsOfAllCollaborators
from climmob.processes.db.project_technologies import numberOfCombinationsForTheProject
from climmob.processes.db.question import getQuestionOptions
from climmob.processes.db.prjlang import getPrjLangInProject
from climmob.processes.db.project_metadata_form import (
    knowIfTheProjectMetadataIsComplete,
)
from climmob.processes.db.project_location_unit_objective import (
    get_project_objectives_by_project_id,
)
import climmob.plugins as p

__all__ = [
    "getTotalNumberOfProjectsInClimMob",
    "addProject",
    "getProjectData",
    "getProjectLabels",
    "getActiveProject",
    "getProjectProgress",
    "setActiveProject",
    "addRegistryQuestionsToProject",
    "addQuestionsToAssessment",
    "getUserProjects",
    "getRegisteredFarmers",
    "modifyProject",
    "deleteProject",
    "getProductData",
    "getProjectCount",
    "getProjectLocalVariety",
    "getMD5Project",
    "getProjectTemplates",
    "getProjectIsTemplate",
    "getProjectUserAndOwner",
    "getProjectFullDetailsById",
    "getProjectsByUserThatRequireSetup",
]


def getTotalNumberOfProjectsInClimMob(request):

    res = request.dbsession.query(Project).count()

    return res


def getProjectTemplates(request, registrationAndAnalysis):

    listOfTemplates = mapFromSchema(
        request.dbsession.query(Project.project_id, Project.project_name)
        .filter(Project.project_template == 1)
        .filter(Project.project_active == 1)
        .filter(Project.project_registration_and_analysis == registrationAndAnalysis)
        .all()
    )

    return listOfTemplates


def getProjectIsTemplate(request, projectId):

    res = mapFromSchema(
        request.dbsession.query(Project)
        .filter(Project.project_id == projectId)
        .filter(Project.project_template == 1)
        .filter(Project.project_active == 1)
        .first()
    )

    return res


def getProjectCount(request):
    numProj = request.dbsession.query(Project).count()
    return numProj


def addQuestionsToAssessment(userOwner, projectId, assessment, request):
    _ = request.translate

    data = {}
    data["ass_cod"] = assessment
    data["section_id"] = 1
    data["section_name"] = _("Farmer selection")
    data["section_content"] = _("List of farmers included in the registration form")
    data["section_order"] = 1
    data["section_private"] = 1
    data["project_id"] = projectId
    newAsssection = Asssection(**data)
    request.dbsession.add(newAsssection)
    data = {}
    data["ass_cod"] = assessment
    data["question_id"] = 163
    data["section_assessment"] = assessment
    data["section_id"] = 1
    data["question_order"] = 1
    data["project_id"] = projectId
    data["section_project_id"] = projectId
    newAssQuestion = AssDetail(**data)
    request.dbsession.add(newAssQuestion)
    data = {}
    data["ass_cod"] = assessment
    data["section_id"] = 2
    data["section_name"] = _("Main section")
    data["section_content"] = _("General data")
    data["section_order"] = 2
    data["section_private"] = 0
    data["project_id"] = projectId
    newAsssection = Asssection(**data)
    try:
        request.dbsession.add(newAsssection)
        questions = (
            request.dbsession.query(Question)
            .filter(Question.user_name == "bioversity")
            .filter(Question.question_reqinasses == 1)
            .filter(Question.question_visible == 1)
            .filter(Question.question_code != "QST163")
            .all()
        )
        order = 1
        good = True
        errMsg = ""
        for question in questions:

            addQuestion = True
            if question.question_dtype == 5 or question.question_dtype == 6:
                res = getQuestionOptions(question.question_id, request)
                if not res:
                    addQuestion = False

            if addQuestion:
                data = {}
                data["ass_cod"] = assessment
                data["question_id"] = question.question_id
                data["section_assessment"] = assessment
                data["section_id"] = 2
                data["question_order"] = order
                data["project_id"] = projectId
                data["section_project_id"] = projectId
                order = order + 1
                newAssQuestion = AssDetail(**data)
                try:
                    request.dbsession.add(newAssQuestion)
                except Exception as e:
                    good = False
                    errMsg = str(e)
        if good:
            questions = (
                request.dbsession.query(Question)
                .filter(Question.user_name == userOwner)
                .filter(Question.question_alwaysinasse == 1)
                .filter(Question.question_visible == 1)
                .all()
            )
            for question in questions:

                addQuestion = True
                if question.question_dtype == 5 or question.question_dtype == 6:
                    res = getQuestionOptions(question.question_id, request)
                    if not res:
                        addQuestion = False

                if addQuestion:
                    data = {}
                    data["ass_cod"] = assessment
                    data["question_id"] = question.question_id
                    data["section_assessment"] = assessment
                    data["section_id"] = 2
                    data["question_order"] = order
                    data["project_id"] = projectId
                    data["section_project_id"] = projectId
                    order = order + 1
                    newAssQuestion = AssDetail(**data)
                    try:
                        ## Edited by Brandon
                        if question.question_dtype == 9:
                            if (
                                question.question_posstm is not None
                                and question.question_negstm is not None
                            ):
                                request.dbsession.add(newAssQuestion)
                        else:
                            if question.question_dtype == 10:
                                if question.question_perfstmt != None:
                                    request.dbsession.add(newAssQuestion)
                            else:
                                request.dbsession.add(newAssQuestion)
                    except Exception as e:
                        good = False
                        errMsg = str(e)
        if good:
            request.dbsession.flush()
        return good, errMsg
    except Exception as e:
        return False, str(e)


def addRegistryQuestionsToProject(userOwner, projectId, request):
    _ = request.translate
    data = {}
    data["section_id"] = 1
    data["section_name"] = _("Main section")
    data["section_content"] = _("General data")
    data["section_order"] = 1
    data["section_private"] = 0
    data["project_id"] = projectId
    newRegsection = Regsection(**data)
    try:
        request.dbsession.add(newRegsection)
        questions = (
            request.dbsession.query(Question)
            .filter(Question.user_name == "bioversity")
            .filter(Question.question_reqinreg == 1)
            .filter(Question.question_visible == 1)
            .all()
        )
        order = 1
        good = True
        errMsg = ""
        for question in questions:

            addQuestion = True
            if question.question_dtype == 5 or question.question_dtype == 6:
                res = getQuestionOptions(question.question_id, request)
                if not res:
                    addQuestion = False

            if addQuestion:
                data = {}
                data["question_id"] = question.question_id
                data["section_id"] = 1
                data["question_order"] = order
                data["project_id"] = projectId
                data["section_project_id"] = projectId
                order = order + 1
                newRegQuestion = Registry(**data)
                try:
                    request.dbsession.add(newRegQuestion)
                except Exception as e:
                    good = False
                    errMsg = str(e)
        if good:
            questions = (
                request.dbsession.query(Question)
                .filter(Question.user_name == userOwner)
                .filter(Question.question_alwaysinreg == 1)
                .filter(Question.question_reqinreg == 0)
                .filter(Question.question_visible == 1)
                .all()
            )
            for question in questions:

                addQuestion = True
                if question.question_dtype == 5 or question.question_dtype == 6:
                    res = getQuestionOptions(question.question_id, request)
                    if not res:
                        addQuestion = False

                if addQuestion:
                    data = {}
                    data["question_id"] = question.question_id
                    data["section_id"] = 1
                    data["question_order"] = order
                    data["project_id"] = projectId
                    data["section_project_id"] = projectId

                    order = order + 1
                    newRegQuestion = Registry(**data)
                    try:
                        request.dbsession.add(newRegQuestion)
                    except Exception as e:
                        good = False
                        errMsg = str(e)
        if good:
            request.dbsession.flush()
        return good, errMsg
    except Exception as e:
        return False, str(e)


def addProject(data, request):
    data["project_active"] = 1
    data["project_public"] = 0
    data["project_creationdate"] = datetime.datetime.now()

    project_id = str(uuid.uuid4())[-12:]
    data["project_id"] = project_id
    newUserProject = userProject(
        project_id=project_id,
        user_name=data["user_name"],
        access_type=1,
        project_dashboard=1,
    )
    try:
        mappedData = mapToSchema(Project, data)
        newProject = Project(**mappedData)
        try:
            request.dbsession.add(newProject)
            request.dbsession.add(newUserProject)
            return True, data["project_id"]
        except Exception as e:
            return False, str(e)

    except Exception as e:
        return False, str(e)


def modifyProject(projectId, data, request):
    mappedData = mapToSchema(Project, data)
    try:
        request.dbsession.query(Project).filter(Project.project_id == projectId).update(
            mappedData
        )
        request.dbsession.flush()
        return True, ""
    except Exception as e:
        return False, str(e)


def deleteProject(projectId, request):
    try:
        request.dbsession.query(Project).filter(Project.project_id == projectId).update(
            {"project_active": 0}
        )
        return True, ""
    except Exception as e:
        return False, str(e)


def getProjectData(projectId, request):
    mappedData = mapFromSchema(
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if mappedData:
        mappedData["languages"] = getPrjLangInProject(projectId, request)
        mappedData["objectives"] = get_project_objectives_by_project_id(
            request, projectId
        )

    return mappedData


def getProjectLabels(projectId, request):
    mappedData = mapFromSchema(
        request.dbsession.query(
            Project.project_label_a, Project.project_label_b, Project.project_label_c
        )
        .filter(Project.project_id == projectId)
        .first()
    )
    return [
        mappedData["project_label_a"],
        mappedData["project_label_b"],
        mappedData["project_label_c"],
    ]


def getProjectLocalVariety(projectId, request):
    result = (
        request.dbsession.query(Project.project_localvariety)
        .filter(Project.project_id == projectId)
        .first()
    )
    return result.project_localvariety


def setActiveProject(userName, projectId, request):
    request.dbsession.query(userProject).filter(
        userProject.user_name == userName
    ).update({userProject.project_dashboard: 0})
    request.dbsession.query(userProject).filter(
        userProject.user_name == userName
    ).filter(userProject.project_id == projectId).update(
        {userProject.project_dashboard: 1}
    )
    request.dbsession.flush()


def getActiveProject(userName, request):
    activeProject = mapFromSchema(
        request.dbsession.query(userProject, Project)
        .filter(userProject.project_id == Project.project_id)
        .filter(userProject.user_name == userName)
        .filter(Project.project_active == 1)
        .filter(userProject.project_dashboard == 1)
        .first()
    )
    if not activeProject:
        project = mapFromSchema(
            request.dbsession.query(Project, userProject)
            .filter(Project.project_id == userProject.project_id)
            .filter(userProject.user_name == userName)
            .filter(Project.project_active == 1)
            .order_by(Project.project_creationdate.desc())
            .first()
        )
        if project:
            setActiveProject(userName, project["project_id"], request)
            activeProject = mapFromSchema(
                request.dbsession.query(Project, userProject)
                .filter(userProject.project_id == Project.project_id)
                .filter(userProject.user_name == userName)
                .filter(Project.project_active == 1)
                .filter(userProject.project_dashboard == 1)
                .first()
            )

    if activeProject:

        activeProject = extraDetailsForProject(activeProject, request)

    return activeProject


def extraDetailsForProject(activeProject, request):
    activeProject["owner"] = mapFromSchema(
        request.dbsession.query(userProject)
        .filter(userProject.project_id == activeProject["project_id"])
        .filter(userProject.access_type == 1)
        .one()
    )

    activeProject["languages"] = getPrjLangInProject(
        activeProject["project_id"], request
    )

    for plugin in p.PluginImplementations(p.IProjectTechnologyOptions):
        activeProject = plugin.get_extra_information_for_data_exchange(
            request, activeProject
        )

    return activeProject


def getProjectFullDetailsById(userName, projectId, request):

    activeProject = mapFromSchema(
        request.dbsession.query(userProject, Project)
        .filter(userProject.project_id == Project.project_id)
        .filter(userProject.user_name == userName)
        .filter(Project.project_id == projectId)
        .first()
    )

    if activeProject:

        activeProject = extraDetailsForProject(activeProject, request)

    return activeProject


def getMD5Project(userName, projectId, projectCod, request):

    result = (
        request.dbsession.query(
            func.md5(func.concat(userProject.user_name, "#$%&", userProject.project_id))
        )
        .filter(userProject.project_id == Project.project_id)
        .filter(Project.project_cod == projectCod)
        .filter(userProject.user_name == userName)
        .filter(userProject.project_id == projectId)
        .first()
    )
    return result[0]


def getUserProjects(user, request):

    projects = (
        request.dbsession.query(Project, userProject)
        .filter(Project.project_id == userProject.project_id)
        .filter(userProject.user_name == user)
        .filter(Project.project_active == 1)
        .order_by(userProject.project_dashboard.desc())
        .order_by(Project.project_creationdate.desc())
        .all()
    )
    mappedData = mapFromSchema(projects)
    for project in mappedData:
        project["owner"] = mapFromSchema(
            request.dbsession.query(userProject)
            .filter(userProject.project_id == project["project_id"])
            .filter(userProject.access_type == 1)
            .one()
        )
        project["project_assstatus"] = (
            request.dbsession.query(
                func.ifnull(func.max(Assessment.ass_status), 0).label(
                    "project_assstatus"
                )
            )
            .filter(Assessment.project_id == project["project_id"])
            .one()
        )[0]

        # project["progress"], project["perc"] = getProjectProgress(
        #     project["user_name"], project["project_cod"], project["project_id"], request
        # )
    return mappedData


def getRegisteredFarmers(userOwner, projectId, projectCod, request):
    res = []
    qstfarmer = (
        request.dbsession.query(Question).filter(Question.question_fname == 1).first()
    )
    qstregkey = (
        request.dbsession.query(Question).filter(Question.question_regkey == 1).first()
    )
    qstdistrict = (
        request.dbsession.query(Question)
        .filter(Question.question_id == Registry.question_id)
        .filter(Registry.project_id == projectId)
        .filter(Question.question_district == 1)
        .first()
    )
    qstvillage = (
        request.dbsession.query(Question)
        .filter(Question.question_id == Registry.question_id)
        .filter(Registry.project_id == projectId)
        .filter(Question.question_village == 1)
        .first()
    )
    qstfather = (
        request.dbsession.query(Question)
        .filter(Question.question_id == Registry.question_id)
        .filter(Registry.project_id == projectId)
        .filter(Question.question_father == 1)
        .first()
    )
    if qstfarmer is not None and qstregkey is not None:
        parts = []
        parts.append("'P:'")
        parts.append(qstregkey.question_code)
        parts.append("'-'")
        parts.append(qstfarmer.question_code)
        if qstdistrict is not None:
            parts.append("'-'")
            parts.append("IFNULL(" + qstdistrict.question_code + ",'')")
        if qstvillage is not None:
            parts.append("'-'")
            parts.append("IFNULL(" + qstvillage.question_code + ",'')")
        if qstfather is not None:
            parts.append("'-'")
            parts.append("IFNULL(" + qstfather.question_code + ",'')")
        sql = (
            "SELECT "
            + qstregkey.question_code
            + " as farmer_id,CONCAT("
            + ",".join(parts)
            + ") as farmer_name FROM "
            + userOwner
            + "_"
            + projectCod
            + ".REG_geninfo order by CAST("
            + qstregkey.question_code
            + " AS unsigned)"
        )
        # print("*****************44")
        # print(sql)
        # print("*****************44")
        try:
            farmers = sql_fetch_all(sql)
            for farmer in farmers:
                res.append(
                    {"farmer_id": farmer.farmer_id, "farmer_name": farmer.farmer_name}
                )
        except:
            return []
    return res


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def getLastRegistrySubmissionDate(userName, projectCode, request):
    _ = request.translate
    path = os.path.join(
        request.registry.settings["user.repository"],
        *[userName, projectCode, "data", "reg", "*"]
    )
    files = glob.glob(path)
    if files:
        files.sort(key=os.path.getmtime)
        return human(modification_date(files[0]), precision=1)
    else:
        return _("Without submissions")


def getLastAssessmentSubmissionDate(userName, projectCode, assessment, request):
    _ = request.translate
    path = os.path.join(
        request.registry.settings["user.repository"],
        *[userName, projectCode, "data", "ass", assessment, "*"]
    )
    files = glob.glob(path)
    if files:
        files.sort(key=os.path.getmtime)
        return human(modification_date(files[0]), precision=1)
    else:
        return _("Without submissions")


def getProjectProgress(userName, projectCode, project, request):
    _ = request.translate
    result = {}
    perc = 4
    result["enumerators_by_user"] = countEnumeratorsOfAllCollaborators(project, request)
    # Project Profile
    perc = perc + 16

    numberOfFieldAgents = (
        request.dbsession.query(PrjEnumerator)
        .filter(PrjEnumerator.project_id == project)
        .count()
    )
    if numberOfFieldAgents > 0:
        result["enumerators"] = True
        result["numberOfFieldAgents"] = numberOfFieldAgents
        perc = perc + 16
    else:
        result["enumerators"] = False
        result["numberOfFieldAgents"] = 0

    if (
        request.dbsession.query(Prjtech).filter(Prjtech.project_id == project).first()
        is not None
    ):
        result["technology"] = True
        perc = perc + 8

        data = (
            request.dbsession.query(
                Prjtech.tech_id,
                request.dbsession.query(func.count(Prjalia.alias_id))
                .filter(Prjalia.project_id == project)
                .filter(Prjalia.tech_id == Prjtech.tech_id)
                .label("count"),
            )
            .filter(Prjtech.project_id == project)
            .all()
        )
        total = 1
        for info in data:
            total = info[1] * total
        necessary = numberOfCombinationsForTheProject(project, request)
        result["techalias"] = False
        result["numberOfCombinations"] = total

        if total <= 50:
            if total >= necessary:
                perc = perc + 8
                result["techalias"] = True

    else:
        result["technology"] = False
        result["techalias"] = False
        result["numberOfCombinations"] = 0

    # Check On-farm testing or Market testing
    formType = (
        request.dbsession.query(Project.project_registration_and_analysis)
        .filter(Project.project_id == project)
        .first()
    )
    formType = formType[0]
    # If the registry has not only required climmob questions

    if (
        request.dbsession.query(Regsection)
        .filter(Regsection.project_id == project)
        .first()
        is not None
    ):
        result["registry"] = True
        numberOfQuestionsInRegistry = (
            request.dbsession.query(Registry)
            .filter(Registry.project_id == project)
            .count()
        )
        result["numberOfQuestionsInRegistry"] = numberOfQuestionsInRegistry
        if formType == 0:
            perc = perc + 16
        else:
            perc = perc + 32
    else:
        result["registry"] = False
        result["numberOfQuestionsInRegistry"] = 0

    if (
        request.dbsession.query(Asssection)
        .filter(Asssection.project_id == project)
        .first()
        is not None
    ):
        result["assessment"] = True
        if formType == 0:
            perc = perc + 16
    else:
        result["assessment"] = False

    # Check the status of registry and assessment
    arstatus = (
        request.dbsession.query(Project).filter(Project.project_id == project).first()
    )
    if arstatus.project_regstatus == 0:
        result["regsubmissions"] = 0
        result["regtotal"] = 0
        result["regperc"] = 0
        result["project_numobs"] = 0
        result["lastreg"] = _("Not yet started")
    else:
        totSubmissions = arstatus.project_numobs
        result["project_numobs"] = totSubmissions
        sql = (
            "SELECT COUNT(*) as total FROM "
            + userName
            + "_"
            + projectCode
            + ".REG_geninfo"
        )
        try:
            # res = request.repsession.execute(sql).fetchone()
            res = sql_fetch_one(sql)
            submissions = res["total"]
        except:
            submissions = 0

        errorsCount = (
            request.dbsession.query(RegistryJsonLog)
            .filter(RegistryJsonLog.project_id == project)
            .filter(RegistryJsonLog.status == 1)
            .count()
        )

        result["lastreg"] = getLastRegistrySubmissionDate(
            userName, projectCode, request
        )
        result["regtotal"] = submissions
        result["regerrors"] = errorsCount
        result["regperc"] = (submissions * 100) / totSubmissions
        if arstatus.project_regstatus == 1:
            result["regsubmissions"] = 1
        else:
            result["regsubmissions"] = 2

    result["asssubmissions"] = 1
    assessmentArray = []
    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == project)
        .order_by(Assessment.ass_days)
        .all()
    )
    for assessment in assessments:
        assessment = mapFromSchema(assessment)
        if "enketo_url" not in assessment.keys():
            assessment["enketo_url"] = ""

        if "ass_rhomis" not in assessment.keys():
            assessment["ass_rhomis"] = ""

        sql = (
            "SELECT COUNT(*) as total FROM "
            + userName
            + "_"
            + projectCode
            + ".ASS"
            + assessment["ass_cod"]
            + "_geninfo"
        )
        try:
            # res = request.repsession.execute(sql).fetchone()
            res = sql_fetch_one(sql)
            totSubmissions = res["total"]
        except:
            totSubmissions = 0

        if totSubmissions > 0:
            sql = (
                "SELECT COUNT(*) as total FROM "
                + userName
                + "_"
                + projectCode
                + ".REG_geninfo"
            )
            try:
                # res = request.repsession.execute(sql).fetchone()
                res = sql_fetch_one(sql)
                submissions = res["total"]
            except:
                submissions = 0

            lastAss = getLastAssessmentSubmissionDate(
                userName, projectCode, assessment["ass_cod"], request
            )

            errorsCount = (
                request.dbsession.query(AssessmentJsonLog)
                .filter(AssessmentJsonLog.project_id == project)
                .filter(AssessmentJsonLog.ass_cod == assessment["ass_cod"])
                .filter(AssessmentJsonLog.status == 1)
                .count()
            )

            assessmentArray.append(
                {
                    "ass_cod": assessment["ass_cod"],
                    "ass_desc": assessment["ass_desc"],
                    "ass_status": assessment["ass_status"],
                    "asstotal": totSubmissions,
                    "assperc": (totSubmissions * 100) / submissions,
                    "submissions": submissions,
                    "errors": errorsCount,
                    "lastass": lastAss,
                    "enketo_url": assessment["enketo_url"],
                    "ass_rhomis": assessment["ass_rhomis"],
                }
            )
        else:
            sql = (
                "SELECT COUNT(*) as total FROM "
                + userName
                + "_"
                + projectCode
                + ".REG_geninfo"
            )
            try:
                res = sql_fetch_one(sql)
                submissions = res["total"]
            except:
                submissions = 0

            assessmentArray.append(
                {
                    "ass_cod": assessment["ass_cod"],
                    "ass_desc": assessment["ass_desc"],
                    "ass_status": assessment["ass_status"],
                    "asstotal": 0,
                    "assperc": 0,
                    "submissions": submissions,
                    "errors": 0,
                    "lastass": _("Without submissions"),
                    "enketo_url": assessment["enketo_url"],
                    "ass_rhomis": assessment["ass_rhomis"],
                }
            )
    result["assessments"] = assessmentArray

    """
    METADATA
    """

    quantityRequired, quantityCompleted = knowIfTheProjectMetadataIsComplete(
        request, project
    )

    if quantityRequired == quantityCompleted:
        result["metadata"] = True
        perc = perc + 16
    else:
        perc = perc + int((16 / quantityRequired) * quantityCompleted)
        result["metadata"] = False

    return result, perc


def getProductData(projectId, celerytaskId, productId, request):
    mappedData = mapFromSchema(
        request.dbsession.query(Products)
        .filter(Products.project_id == projectId)
        .filter(Products.celery_taskid == celerytaskId)
        .filter(Products.product_id == productId)
        .first()
    )
    return mappedData


def getProjectUserAndOwner(projectId, request):

    mappedData = mapFromSchema(
        request.dbsession.query(userProject, Project.project_cod)
        .filter(userProject.project_id == projectId)
        .filter(userProject.access_type == 1)
        .filter(userProject.project_id == Project.project_id)
        .first()
    )

    return mappedData


def getProjectsByUserThatRequireSetup(userOwner, request):

    res = mapFromSchema(
        request.dbsession.query(Project, Country)
        .filter(Project.project_id == userProject.project_id)
        .filter(userProject.access_type == 1)
        .filter(userProject.user_name == userOwner)
        .filter(Project.project_cnty == Country.cnty_cod)
        .filter(Project.project_type == 0)
        .all()
    )

    if res:

        return False, res

    return True, res
