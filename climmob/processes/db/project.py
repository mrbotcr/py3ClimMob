from ...models import (
    Project,
    mapToSchema,
    mapFromSchema,
    PrjEnumerator,
    Prjtech,
    Regsection,
    Registry,
    Question,
    Qstoption,
    AssDetail,
    Asssection,
    Assessment,
    Products,
    Prjalia,
)
from ..db.question import getQuestionOptions
import datetime, os, glob
from sqlalchemy import func
from .project_technologies import numberOfCombinationsForTheProject
from ago import human

__all__ = [
    "addProject",
    "getProjectData",
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
]


def getProjectCount(request):
    numProj = request.dbsession.query(Project).count()
    return numProj


def addQuestionsToAssessment(user, project, assessment, request):
    data = {}
    data["user_name"] = user
    data["project_cod"] = project
    data["ass_cod"] = assessment
    data["section_id"] = 1
    data["section_name"] = request.translate("Main section")
    data["section_content"] = request.translate("General data")
    data["section_order"] = 1
    data["section_color"] = ""
    newAsssection = Asssection(**data)
    try:
        request.dbsession.add(newAsssection)
        questions = (
            request.dbsession.query(Question)
            .filter(Question.user_name == "bioversity")
            .filter(Question.question_reqinasses == 1)
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
                data["user_name"] = user
                data["project_cod"] = project
                data["ass_cod"] = assessment
                data["question_id"] = question.question_id
                data["section_user"] = user
                data["section_project"] = project
                data["section_assessment"] = assessment
                data["section_id"] = 1
                data["question_order"] = order
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
                .filter(Question.user_name == user)
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
                    data["user_name"] = user
                    data["project_cod"] = project
                    data["ass_cod"] = assessment
                    data["question_id"] = question.question_id
                    data["section_user"] = user
                    data["section_project"] = project
                    data["section_assessment"] = assessment
                    data["section_id"] = 1
                    data["question_order"] = order
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
                        ##
                        # request.dbsession.add(newAssQuestion)
                    except Exception as e:
                        good = False
                        errMsg = str(e)
        if good:
            request.dbsession.flush()
        return good, errMsg
    except Exception as e:
        return False, str(e)


def addRegistryQuestionsToProject(user, project, request):
    data = {}
    data["user_name"] = user
    data["project_cod"] = project
    data["section_id"] = 1
    data["section_name"] = request.translate("Main section")
    data["section_content"] = request.translate("General data")
    data["section_order"] = 1
    data["section_color"] = ""
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
                data["user_name"] = user
                data["project_cod"] = project
                data["question_id"] = question.question_id
                data["section_user"] = user
                data["section_project"] = project
                data["section_id"] = 1
                data["question_order"] = order
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
                .filter(Question.user_name == user)
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
                    data["user_name"] = user
                    data["project_cod"] = project
                    data["question_id"] = question.question_id
                    data["section_user"] = user
                    data["section_project"] = project
                    data["section_id"] = 1
                    data["question_order"] = order
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
    mappedData = mapToSchema(Project, data)
    newProject = Project(**mappedData)
    try:
        request.dbsession.add(newProject)
        return True, ""
    except Exception as e:
        return False, str(e)


def modifyProject(user, project, data, request):
    mappedData = mapToSchema(Project, data)
    try:
        request.dbsession.query(Project).filter(Project.user_name == user).filter(
            Project.project_cod == project
        ).update(mappedData)
        return True, ""
    except Exception as e:
        return False, str(e)


def deleteProject(user, project, request):
    try:
        request.dbsession.query(Project).filter(Project.user_name == user).filter(
            Project.project_cod == project
        ).update({"project_active": 0})
        return True, ""
    except Exception as e:
        return False, str(e)


def getProjectData(user, project, request):
    mappedData = mapFromSchema(
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    return mappedData


def getProjectLocalVariety(user, project, request):
    result = (
        request.dbsession.query(Project.project_localvariety)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    return result.project_localvariety


def setActiveProject(user, project, request):
    request.dbsession.query(Project).filter(Project.user_name == user).update(
        {Project.project_dashboard: 0}
    )
    request.dbsession.query(Project).filter(Project.user_name == user).filter(
        Project.project_cod == project
    ).update({Project.project_dashboard: 1})
    request.dbsession.flush()


def getActiveProject(user, request):
    activeProject = mapFromSchema(
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_active == 1)
        .filter(Project.project_dashboard == 1)
        .first()
    )
    if not activeProject:
        project = (
            request.dbsession.query(Project)
            .filter(Project.user_name == user)
            .filter(Project.project_active == 1)
            .order_by(Project.project_creationdate.desc())
            .first()
        )
        if project is not None:
            setActiveProject(user, project.project_cod, request)
            activeProject = mapFromSchema(
                request.dbsession.query(Project)
                .filter(Project.user_name == user)
                .filter(Project.project_active == 1)
                .filter(Project.project_dashboard == 1)
                .first()
            )
            return activeProject
        else:
            return activeProject

    return activeProject


def getMD5Project(user, project, request):

    result = (
        request.dbsession.query(
            func.md5(func.concat(Project.user_name, "#$%&", Project.project_cod))
        )
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    return result[0]


def getUserProjects(user, request):
    projects = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_active == 1)
        .order_by(Project.project_dashboard.desc())
        .order_by(Project.project_creationdate.desc())
        .all()
    )
    mappedData = mapFromSchema(projects)
    for project in mappedData:
        project["progress"], project["perc"] = getProjectProgress(
            user, project["project_cod"], request
        )
    return mappedData


def getRegisteredFarmers(user, project, request):
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
        .filter(Registry.user_name == user)
        .filter(Registry.project_cod == project)
        .filter(Question.question_district == 1)
        .first()
    )
    qstvillage = (
        request.dbsession.query(Question)
        .filter(Question.question_id == Registry.question_id)
        .filter(Registry.user_name == user)
        .filter(Registry.project_cod == project)
        .filter(Question.question_village == 1)
        .first()
    )
    qstfather = (
        request.dbsession.query(Question)
        .filter(Question.question_id == Registry.question_id)
        .filter(Registry.user_name == user)
        .filter(Registry.project_cod == project)
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
            + user
            + "_"
            + project
            + ".REG_geninfo"
        )
        print("*****************44")
        print(sql)
        print("*****************44")
        try:
            farmers = request.repsession.execute(sql).fetchall()
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


def getLastRegistrySubmissionDate(user, project, request):
    path = os.path.join(
        request.registry.settings["user.repository"],
        *[user, project, "data", "reg", "*"]
    )
    files = glob.glob(path)
    if files:
        files.sort(key=os.path.getmtime)
        return human(modification_date(files[0]), precision=1)
    else:
        return request.translate("Without submissions")


def getLastAssessmentSubmissionDate(user, project, assessment, request):
    path = os.path.join(
        request.registry.settings["user.repository"],
        *[user, project, "data", "ass", assessment]
    )
    files = glob.glob(path)
    if files:
        files.sort(key=os.path.getmtime)
        return human(modification_date(files[0]), precision=1)
    else:
        return request.translate("Without submissions")


def getProjectProgress(user, project, request):
    result = {}
    perc = 0
    if (
        request.dbsession.query(PrjEnumerator)
        .filter(PrjEnumerator.user_name == user)
        .filter(PrjEnumerator.project_cod == project)
        .first()
        is not None
    ):
        result["enumerators"] = True
        perc = perc + 20
    else:
        result["enumerators"] = False

    if (
        request.dbsession.query(Prjtech)
        .filter(Prjtech.user_name == user)
        .filter(Prjtech.project_cod == project)
        .first()
        is not None
    ):
        result["technology"] = True
        perc = perc + 20
        # If a technology does not have aliases
        # Edit by Brandon
        """
        sql = "SELECT tech_id FROM prjtech WHERE user_name = '" + user + "' AND project_cod = '" + project + "' and " \
              "tech_id NOT IN (SELECT distinct tech_id FROM prjalias WHERE user_name = '" + user + "' AND project_cod = '" + project + "')"
        techaliases = request.dbsession.execute(sql).fetchone()
        if techaliases is not None:
            result["techalias"] = False
        else:
            perc = perc + 20
            result["techalias"] = True
        """
        # Pruebas de lo que quiero hacer
        # data = request.dbsession.query(Prjtech.tech_id,func.count(Prjalia.alias_id)).filter(Prjtech.user_name == user).filter(Prjtech.project_cod == project).filter(Prjtech.tech_id == Prjalia.tech_id).group_by(Prjtech.tech_id).all()
        data = (
            request.dbsession.query(
                Prjtech.tech_id,
                request.dbsession.query(func.count(Prjalia.alias_id))
                .filter(Prjalia.user_name == user)
                .filter(Prjalia.project_cod == project)
                .filter(Prjalia.tech_id == Prjtech.tech_id)
                .label("count"),
            )
            .filter(Prjtech.user_name == user)
            .filter(Prjtech.project_cod == project)
            .all()
        )
        total = 1
        for info in data:
            total = info[1] * total

        # print total

        necessary = numberOfCombinationsForTheProject(user, project, request)
        result["techalias"] = False

        if total >= necessary:
            perc = perc + 20
            result["techalias"] = True

        # The edition ends
    else:
        result["technology"] = False
        result["techalias"] = False

    # If the registry has not only required climmob questions

    if (
        request.dbsession.query(Regsection)
        .filter(Regsection.user_name == user)
        .filter(Regsection.project_cod == project)
        .first()
        is not None
    ):
        result["registry"] = True
        perc = perc + 20
    else:
        result["registry"] = False

    if (
        request.dbsession.query(Asssection)
        .filter(Asssection.user_name == user)
        .filter(Asssection.project_cod == project)
        .first()
        is not None
    ):
        result["assessment"] = True
        perc = perc + 20
    else:
        result["assessment"] = False

    # Check the status of registry and assessment
    arstatus = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    if arstatus.project_regstatus == 0:
        result["regsubmissions"] = 0
        result["regtotal"] = 0
        result["regperc"] = 0
        result["project_numobs"] = 0
        result["lastreg"] = request.translate("Not yet started")
    else:
        totSubmissions = arstatus.project_numobs
        result["project_numobs"] = totSubmissions
        sql = "SELECT COUNT(*) as total FROM " + user + "_" + project + ".REG_geninfo"
        try:
            res = request.repsession.execute(sql).fetchone()
            submissions = res["total"]
        except:
            submissions = 0

        result["lastreg"] = getLastRegistrySubmissionDate(user, project, request)
        result["regtotal"] = submissions
        result["regperc"] = (submissions * 100) / totSubmissions
        if arstatus.project_regstatus == 1:
            result["regsubmissions"] = 1
        else:
            result["regsubmissions"] = 2

    result["asssubmissions"] = 1
    assessmentArray = []
    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == user)
        .filter(Assessment.project_cod == project)
        .all()
    )
    for assessment in assessments:
        sql = (
            "SELECT COUNT(*) as total FROM "
            + user
            + "_"
            + project
            + ".ASS"
            + assessment.ass_cod
            + "_geninfo"
        )
        try:
            res = request.repsession.execute(sql).fetchone()
            totSubmissions = res["total"]
        except:
            totSubmissions = 0

        if totSubmissions > 0:
            sql = (
                "SELECT COUNT(*) as total FROM " + user + "_" + project + ".REG_geninfo"
            )
            try:
                res = request.repsession.execute(sql).fetchone()
                submissions = res["total"]
            except:
                submissions = 0

            lastAss = getLastAssessmentSubmissionDate(
                user, project, assessment.ass_cod, request
            )
            assessmentArray.append(
                {
                    "ass_cod": assessment.ass_cod,
                    "ass_desc": assessment.ass_desc,
                    "ass_status": assessment.ass_status,
                    "asstotal": totSubmissions,
                    "assperc": (totSubmissions * 100) / submissions,
                    "submissions": submissions,
                    "lastass": lastAss,
                }
            )
        else:
            sql = (
                "SELECT COUNT(*) as total FROM " + user + "_" + project + ".REG_geninfo"
            )
            try:
                res = request.repsession.execute(sql).fetchone()
                submissions = res["total"]
            except:
                submissions = 0

            assessmentArray.append(
                {
                    "ass_cod": assessment.ass_cod,
                    "ass_desc": assessment.ass_desc,
                    "ass_status": assessment.ass_status,
                    "asstotal": 0,
                    "assperc": 0,
                    "submissions": submissions,
                    "lastass": request.translate("Without submissions"),
                }
            )
    result["assessments"] = assessmentArray

    return result, perc


def getProductData(user, project, celery_taskid, request):
    mappedData = mapFromSchema(
        request.dbsession.query(Products)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .filter(Products.celery_taskid == celery_taskid)
        .first()
    )
    return mappedData
