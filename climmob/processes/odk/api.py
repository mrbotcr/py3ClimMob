from lxml import etree
import os, glob, shutil
import json
from pyramid.response import FileResponse
import mimetypes
from pyramid.httpexceptions import HTTPNotFound
from hashlib import md5
from uuid import uuid4
from climmob.models import Project, storageErrors, Assessment
from climmob.processes import (
    isRegistryOpen,
    isAssessmentOpen,
    assessmentExists,
    projectExists,
    packageExist,
    getTheProjectIdForOwner,
)
from climmob.processes.db.json import addJsonLog
from subprocess import check_call, CalledProcessError, Popen, PIPE
import logging
import datetime
import io
import shutil as sh

log = logging.getLogger(__name__)

__all__ = [
    "generateFormList",
    "generateManifest",
    "getFormList",
    "getManifest",
    "getXMLForm",
    "getMediaFile",
    "storeSubmission",
    "getAssessmentXMLForm",
    "getAssessmentManifest",
    "getAssessmentMediaFile",
]


def generateFormList(projectArray):
    root = etree.Element("xforms", xmlns="http://openrosa.org/xforms/xformsList")
    for project in projectArray:
        xformTag = etree.Element("xform")
        for key, value in project.items():
            atag = etree.Element(key)
            # print "**************************55"
            # print value
            # print "**************************55"
            atag.text = value
            xformTag.append(atag)
        root.append(xformTag)
    return etree.tostring(root, encoding="utf-8")


def generateManifest(mediaFileArray):
    root = etree.Element("manifest", xmlns="http://openrosa.org/xforms/xformsManifest")
    for file in mediaFileArray:
        xformTag = etree.Element("mediaFile")
        for key, value in file.items():
            atag = etree.Element(key)
            atag.text = value
            xformTag.append(atag)
        root.append(xformTag)
    return etree.tostring(root, encoding="utf-8")


def getFormList(userid, enumerator, request, userOwner=None, projectCod=None):
    prjList = []

    sql = (
        "SELECT user_project.user_name,project.project_id,project.project_cod,project.project_regstatus,project.project_assstatus FROM "
        "prjenumerator,enumerator,project, user_project WHERE "
        "user_project.project_id = prjenumerator.project_id AND "
        "user_project.access_type = 1 AND "
        "prjenumerator.enum_user = enumerator.user_name AND "
        "prjenumerator.enum_id = enumerator.enum_id AND "
        "prjenumerator.project_id = project.project_id AND "
        "enumerator.enum_active = 1 AND "
        "(project.project_regstatus != 0) AND "
        "enumerator.user_name = '" + userid + "' AND "
        "enumerator.enum_id = '" + enumerator + "'"
    )

    if projectCod != None:
        sql = (
            sql
            + " AND project.project_cod='"
            + projectCod
            + "' and user_project.user_name='"
            + userOwner
            + "'"
        )

    projects = request.dbsession.execute(sql).fetchall()

    for project in projects:
        # print("yep!1")
        if project.project_regstatus == 1:
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[project.user_name, project.project_cod, "odk", "reg", "*.json"]
            )
            files = glob.glob(path)
            if files:
                with io.open(files[0], encoding="utf8") as data_file:
                    data = json.load(data_file)
                    data["downloadUrl"] = request.route_url(
                        "odkxmlform",
                        user=userid,
                        userowner=project.user_name,
                        project=project.project_cod,
                    )
                    data["manifestUrl"] = request.route_url(
                        "odkmanifest",
                        user=userid,
                        userowner=project.user_name,
                        project=project.project_cod,
                    )
                prjList.append(data)

        assessments = (
            request.dbsession.query(Assessment)
            .filter(Assessment.project_id == project.project_id)
            .filter(Assessment.ass_status == 1)
            .all()
        )
        for assessment in assessments:
            # print("yep!2")
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[
                    project.user_name,
                    project.project_cod,
                    "odk",
                    "ass",
                    assessment.ass_cod,
                    "*.json",
                ]
            )
            files = glob.glob(path)
            if files:
                with open(files[0]) as data_file:
                    data = json.load(data_file, encoding="utf8")
                    data["downloadUrl"] = request.route_url(
                        "odkxmlformass",
                        user=userid,
                        userowner=project.user_name,
                        project=project.project_cod,
                        assessmentid=assessment.ass_cod,
                    )
                    data["manifestUrl"] = request.route_url(
                        "odkmanifestass",
                        user=userid,
                        userowner=project.user_name,
                        project=project.project_cod,
                        assessmentid=assessment.ass_cod,
                    )
                    prjList.append(data)

    return generateFormList(prjList)


def getManifest(user, userOwner, projectId, projectCod, request):
    prjdat = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if prjdat.project_regstatus == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "odk", "reg", "media", "*.*"]
        )

    files = glob.glob(path)
    if files:
        fileArray = []
        for file in files:
            fileName = os.path.basename(file)
            fileArray.append(
                {
                    "filename": fileName,
                    "hash": "md5:" + md5(open(file, "rb").read()).hexdigest(),
                    "downloadUrl": request.route_url(
                        "odkmediafile",
                        user=user,
                        userowner=userOwner,
                        project=projectCod,
                        fileid=fileName,
                    ),
                }
            )
        return generateManifest(fileArray)
    else:
        return generateManifest([])


def getAssessmentManifest(
    user, userOwner, projectId, projectCod, assessmentid, request
):
    prjdat = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessmentid)
        .first()
    )
    if prjdat.ass_status == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "odk", "ass", assessmentid, "media", "*.*"]
        )
    else:
        raise HTTPNotFound()

    files = glob.glob(path)
    if files:
        fileArray = []
        for file in files:
            fileName = os.path.basename(file)
            fileArray.append(
                {
                    "filename": fileName,
                    "hash": "md5:" + md5(open(file, "rb").read()).hexdigest(),
                    "downloadUrl": request.route_url(
                        "odkmediafileass",
                        user=user,
                        userowner=userOwner,
                        project=projectCod,
                        assessmentid=assessmentid,
                        fileid=fileName,
                    ),
                }
            )
        return generateManifest(fileArray)
    else:
        return generateManifest([])


def getXMLForm(userOwner, projectId, projectCod, request):
    prjdat = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if prjdat.project_regstatus == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "odk", "reg", "*.xml"]
        )

    files = glob.glob(path)
    if files:
        content_type, content_enc = mimetypes.guess_type(files[0])
        fileName = os.path.basename(files[0])
        response = FileResponse(files[0], request=request, content_type=content_type)
        response.content_disposition = 'attachment; filename="' + fileName + '"'
        return response
    else:
        raise HTTPNotFound()


def getAssessmentXMLForm(userOwner, projectId, projectCod, assessmentid, request):
    prjdat = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessmentid)
        .first()
    )
    if prjdat.ass_status == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "odk", "ass", assessmentid, "*.xml"]
        )
    else:
        raise HTTPNotFound()
    files = glob.glob(path)
    if files:
        content_type, content_enc = mimetypes.guess_type(files[0])
        fileName = os.path.basename(files[0])
        response = FileResponse(files[0], request=request, content_type=content_type)
        response.content_disposition = 'attachment; filename="' + fileName + '"'
        return response
    else:
        raise HTTPNotFound()


def getMediaFile(userOwner, projectId, projectCod, fileid, request):
    prjdat = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if prjdat.project_regstatus == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "odk", "reg", "media", fileid]
        )
    else:
        raise HTTPNotFound()
    if os.path.isfile(path):
        content_type, content_enc = mimetypes.guess_type(path)
        fileName = os.path.basename(path)
        response = FileResponse(path, request=request, content_type=content_type)
        response.content_disposition = 'attachment; filename="' + fileName + '"'
        return response
    else:
        raise HTTPNotFound()


def getAssessmentMediaFile(
    userOwner, projectId, projectCod, assessmentid, fileid, request
):
    prjdat = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessmentid)
        .first()
    )
    if prjdat.ass_status == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "odk", "ass", assessmentid, "media", fileid]
        )
    else:
        raise HTTPNotFound()
    if os.path.isfile(path):
        content_type, content_enc = mimetypes.guess_type(path)
        fileName = os.path.basename(path)
        response = FileResponse(path, request=request, content_type=content_type)
        response.content_disposition = 'attachment; filename="' + fileName + '"'
        return response
    else:
        raise HTTPNotFound()


def storeError(
    fileid, type, userid, projectid, assessmentid, errorNumber, error, command, request
):
    if errorNumber == 2:
        try:
            terror = error.strip("\r")
            terror = terror.strip("\n")
            terror = terror.strip("\t")
            t1 = terror.split("&")
            t2 = t1[1].split("@")
            sqlErrorNumber = t1[0]
            sqlErrorDesc = t2[0]
            sqlTable = t2[1]
        except:
            sqlErrorNumber = "UNK"
            sqlErrorDesc = "UNK"
            sqlTable = "UNK"
    else:
        sqlErrorNumber = "NonSQL " + str(errorNumber)
        sqlErrorDesc = error
        sqlTable = None

    sqlErrorDesc = sqlErrorDesc.strip("\r")
    sqlErrorDesc = sqlErrorDesc.strip("\t")

    newError = storageErrors(
        fileuid=fileid,
        user_name=userid,
        project_cod=projectid,
        assessment_id=assessmentid,
        submission_type=type,
        command_executed=command,
        error_cod=sqlErrorNumber,
        error_des=sqlErrorDesc,
        error_table=sqlTable,
        error_datetime=datetime.datetime.now(),
    )
    try:
        request.dbsession.add(newError)
        return True, ""
    except Exception as e:
        return False, str(e)


def storeJSONInMySQL(
    userid,
    type,
    userOwner,
    userEnum,
    projectCod,
    assessmentid,
    JSONFile,
    request,
    projectId,
):
    schema = userOwner + "_" + projectCod
    if type == "REG":
        manifestFile = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "db", "reg", "manifest.xml"]
        )
        jsFile = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "db", "reg", "custom.js"]
        )

    else:
        manifestFile = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "db", "ass", assessmentid, "manifest.xml"]
        )
        jsFile = ""

    # print(JSONFile)
    importedFile = os.path.splitext(JSONFile)[0] + ".imp"
    # print(importedFile)
    importedFile = "/".join(JSONFile.split("/")[:-2]) + "/myimportedFile.sqlite"

    logFile = os.path.splitext(JSONFile)[0] + ".log"
    jsonPath = os.path.dirname(JSONFile)
    mapPath = os.path.join(jsonPath, *["maps"])
    if not os.path.exists(mapPath):
        os.makedirs(mapPath)

    host = request.registry.settings["odktools.mysql.host"]
    port = request.registry.settings["odktools.mysql.port"]
    user = request.registry.settings["odktools.mysql.user"]
    password = request.registry.settings["odktools.mysql.password"]
    JSONtoMySQL = os.path.join(
        request.registry.settings["odktools.path"], *["JSONToMySQL", "jsontomysql"]
    )

    args = []
    args.append(JSONtoMySQL)
    args.append("-H " + host)
    args.append("-P " + port)
    args.append("-u " + user)
    args.append("-p " + password)
    args.append("-s " + schema)
    args.append("-m " + manifestFile)
    args.append("-j " + JSONFile)
    args.append("-i " + importedFile)
    args.append("-o " + logFile)
    args.append("-M " + mapPath)
    args.append("-w")
    if type == "REG":
        args.append("-J " + jsFile)

    p = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        base = os.path.basename(JSONFile)
        fileuid = os.path.splitext(base)[0]
        print("*********************666")
        print(" ".join(args))
        print("*********************666")

        if userEnum != None:
            addJsonLog(
                request,
                type,
                userid,
                userEnum,
                assessmentid,
                fileuid,
                JSONFile,
                logFile,
                projectId,
            )

    return True


def convertXMLToJSON(
    userid,
    userOwner,
    userEnum,
    XMLFile,
    JSONFile,
    projectCod,
    submissionType,
    assessmentID,
    request,
    projectId,
):
    if submissionType == "REG":
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "odk", "reg", "*.xml"]
        )
    if submissionType == "ASS":
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userOwner, projectCod, "odk", "ass", assessmentID, "*.xml"]
        )

    files = glob.glob(path)
    if files:
        XMLtoJSON = os.path.join(
            request.registry.settings["odktools.path"], *["XMLtoJSON", "xmltojson"]
        )
        args = []
        args.append(XMLtoJSON)
        args.append("-i " + XMLFile)
        args.append("-o " + JSONFile)
        args.append("-x " + files[0])
        try:
            check_call(args)
            # Now that we have the data in JSON format we check if any connected plugins
            # may change the JSON data
            with open(JSONFile) as data_file:
                data = json.load(data_file)
            # for plugin in p.PluginImplementations(p.ISubmissionStorage):
            #    data = plugin.before_save_in_json(request, userid, projectID, data)
            with open(JSONFile, "w") as outfile:
                data["_submitted_by"] = userEnum
                data["_submitted_date"] = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                jsonString = json.dumps(data, indent=4, ensure_ascii=False)
                outfile.write(jsonString)
            # Now we store the data in MySQL
            storeJSONInMySQL(
                userid,
                submissionType,
                userOwner,
                userEnum,
                projectCod,
                assessmentID,
                JSONFile,
                request,
                projectId,
            )
        except CalledProcessError as e:
            print("1")
            msg = "Error creating database files \n"
            msg = msg + "Commang: " + " ".join(args) + "\n"
            msg = msg + "Error: \n"
            msg = msg + str(e)
            print(msg)
            return False
    else:
        print("Unable to find XML Form File for submission")
        return False

    return True


def checkSubmission(userInRequest, file, request):
    tree = etree.parse(file)
    root = tree.getroot()
    XFormID = root.get("id")
    if XFormID is not None:
        xFormIDParts = XFormID.split("_")
        if xFormIDParts[0] == "REG" or xFormIDParts[0] == "ASS":
            if xFormIDParts[0] == "REG":
                user = xFormIDParts[1]
                project = xFormIDParts[2]
                if projectExists(userInRequest, user, project, request):
                    projectId = getTheProjectIdForOwner(user, project, request)
                    if isRegistryOpen(projectId, request):
                        if packageExist(root, projectId, request):
                            return True, 201, project, "REG", None, user, projectId
                        else:
                            return False, 404, None, None, None, None, None
                    else:
                        return False, 403, None, None, None, None, None
                else:
                    return False, 404, None, None, None, None, None

            if xFormIDParts[0] == "ASS":
                user = xFormIDParts[1]
                project = xFormIDParts[2]
                assessment = xFormIDParts[3]
                if projectExists(userInRequest, user, project, request):

                    projectId = getTheProjectIdForOwner(user, project, request)

                    if isAssessmentOpen(projectId, assessment, request):
                        if assessmentExists(projectId, assessment, request):
                            return (
                                True,
                                201,
                                project,
                                "ASS",
                                assessment,
                                user,
                                projectId,
                            )
                        else:
                            return False, 404, None, None, None, None, None
                    else:
                        return False, 403, None, None, None, None, None
                else:
                    return False, 404, None, None, None, None, None
        else:
            return False, 404, None, None, None, None, None
    else:
        return False, 404, None, None, None, None, None


def storeSubmission(userid, userEnum, request):
    # try:
    acceptSubmission = False
    projectCod = None
    submissionType = None
    assessmentID = None
    userOwner = None
    projectId = None
    error = 404
    for key in request.POST.keys():
        filename = request.POST[key].filename
        if filename.upper().find(".XML") >= 0 or filename == "xml_submission_file":
            input_file = request.POST[key].file

            # Change by Brandon
            iniqueIDTemp = uuid4()

            pathTemp = os.path.join(
                request.registry.settings["user.repository"],
                *[userid, "data", "xml", str(iniqueIDTemp)]
            )

            os.makedirs(pathTemp)

            filePath = os.path.join(pathTemp, filename)
            tempFilePath = filePath + "~"

            input_file.seek(0)

            with open(tempFilePath, "wb") as output_file:
                shutil.copyfileobj(input_file, output_file)

            final = open(filePath, "w")
            args = ["tidy", "-xml", tempFilePath]
            p = Popen(args, stdout=final, stderr=PIPE)
            stdout, stderr = p.communicate()
            final.close()
            if p.returncode != 0:
                return False, 500
            # End changes by Brandon

            (
                acceptSubmission,
                error,
                projectCod,
                submissionType,
                assessmentID,
                userOwner,
                projectId,
            ) = checkSubmission(userid, filePath, request)

            sh.rmtree(pathTemp)

    if acceptSubmission:
        iniqueID = uuid4()
        if submissionType == "REG":
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[userOwner, projectCod, "data", "reg", "xml", str(iniqueID)]
            )
            if not os.path.exists(path):
                os.makedirs(path)
                os.makedirs(
                    os.path.join(
                        request.registry.settings["user.repository"],
                        *[userOwner, projectCod, "data", "reg", "json", str(iniqueID)]
                    )
                )

        else:
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[
                    userOwner,
                    projectCod,
                    "data",
                    "ass",
                    assessmentID,
                    "xml",
                    str(iniqueID),
                ]
            )
            if not os.path.exists(path):
                os.makedirs(path)
                os.makedirs(
                    os.path.join(
                        request.registry.settings["user.repository"],
                        *[
                            userOwner,
                            projectCod,
                            "data",
                            "ass",
                            assessmentID,
                            "json",
                            str(iniqueID),
                        ]
                    )
                )

        XMLFile = ""
        for key in request.POST.keys():
            filename = request.POST[key].filename
            input_file = request.POST[key].file
            file_path = os.path.join(path, filename)
            if file_path.upper().find(".XML") >= 0 or filename == "xml_submission_file":
                XMLFile = file_path
            temp_file_path = file_path + "~"

            input_file.seek(0)
            with open(temp_file_path, "wb") as output_file:
                shutil.copyfileobj(input_file, output_file)
            # Now that we know the file has been fully saved to disk move it into place.
            os.rename(temp_file_path, file_path)
        if XMLFile != "":
            XMLFilePath = os.path.dirname(XMLFile)
            newFile = os.path.join(XMLFilePath, str(iniqueID) + ".xml")
            # Write the original name in info for reference
            infoFile = os.path.join(XMLFilePath, str(iniqueID) + ".info")
            file = open(infoFile, "w")
            file.write(filename)
            file.close()
            # Rename the file
            os.rename(XMLFile, newFile)
            XMLFile = newFile
            JSONFile = XMLFile.replace("xml", "json")
            convertXMLToJSON(
                userid,
                userOwner,
                userEnum,
                XMLFile,
                JSONFile,
                projectCod,
                submissionType,
                assessmentID,
                request,
                projectId,
            )
            return True, 201
        else:
            return False, 500
    else:
        print("***********************7771")
        print("No accepted")
        print("***********************7771")
        return False, error
    # except:
    #     return False,500
