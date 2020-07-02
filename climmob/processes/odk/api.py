from lxml import etree
import os, glob, shutil
import json
from pyramid.response import FileResponse
import mimetypes
from pyramid.httpexceptions import HTTPNotFound
from hashlib import md5
from uuid import uuid4
from ...models import Project, storageErrors, Assessment
from ...processes import (
    isRegistryOpen,
    isAssessmentOpen,
    assessmentExists,
    projectExists,
    packageExist
)
from ..db.json import addJsonLog
from pyramid.response import Response
from subprocess import check_call, CalledProcessError, Popen, PIPE
import logging
import climmob.plugins as p
import datetime
import io

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
        for key, value in file.iteritems():
            atag = etree.Element(key)
            atag.text = value
            xformTag.append(atag)
        root.append(xformTag)
    return etree.tostring(root, encoding="utf-8")


def getFormList(userid, enumerator, request):
    prjList = []

    sql = (
        "SELECT prjenumerator.project_cod,project.project_regstatus,project.project_assstatus FROM "
        "prjenumerator,enumerator,project WHERE "
        "prjenumerator.enum_user = enumerator.user_name AND "
        "prjenumerator.enum_id = enumerator.enum_id AND "
        "prjenumerator.user_name = project.user_name AND "
        "prjenumerator.project_cod = project.project_cod AND "
        "enumerator.enum_active = 1 AND "
        "(project.project_regstatus != 0) AND "
        "enumerator.user_name = '" + userid + "' AND "
        "enumerator.enum_id = '" + enumerator + "'"
    )
    # print(sql)
    projects = request.dbsession.execute(sql).fetchall()

    for project in projects:
        # print("yep!1")
        if project.project_regstatus == 1:
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[userid, project.project_cod, "odk", "reg", "*.json"]
            )
            files = glob.glob(path)
            if files:
                with io.open(files[0], encoding="utf8") as data_file:
                    data = json.load(data_file)
                    data["downloadUrl"] = request.route_url(
                        "odkxmlform", userid=userid, projectid=project.project_cod
                    )
                    data["manifestUrl"] = request.route_url(
                        "odkmanifest", userid=userid, projectid=project.project_cod
                    )
                prjList.append(data)

        assessments = (
            request.dbsession.query(Assessment)
            .filter(Assessment.user_name == userid)
            .filter(Assessment.project_cod == project.project_cod)
            .filter(Assessment.ass_status == 1)
            .all()
        )
        for assessment in assessments:
            # print("yep!2")
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[
                    userid,
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
                        userid=userid,
                        projectid=project.project_cod,
                        assessmentid=assessment.ass_cod,
                    )
                    data["manifestUrl"] = request.route_url(
                        "odkmanifestass",
                        userid=userid,
                        projectid=project.project_cod,
                        assessmentid=assessment.ass_cod,
                    )
                    prjList.append(data)

    return generateFormList(prjList)


def getManifest(userid, projectid, request):
    prjdat = (
        request.dbsession.query(Project)
        .filter(Project.user_name == userid)
        .filter(Project.project_cod == projectid)
        .first()
    )
    if prjdat.project_regstatus == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "odk", "reg", "media", "*.*"]
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
                        userid=userid,
                        projectid=projectid,
                        fileid=fileName,
                    ),
                }
            )
        return generateManifest(fileArray)
    else:
        return generateManifest([])


def getAssessmentManifest(userid, projectid, assessmentid, request):
    prjdat = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == userid)
        .filter(Assessment.project_cod == projectid)
        .filter(Assessment.ass_cod == assessmentid)
        .first()
    )
    if prjdat.ass_status == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "odk", "ass", assessmentid, "media", "*.*"]
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
                        userid=userid,
                        projectid=projectid,
                        assessmentid=assessmentid,
                        fileid=fileName,
                    ),
                }
            )
        return generateManifest(fileArray)
    else:
        return generateManifest([])


def getXMLForm(userid, projectid, request):
    prjdat = (
        request.dbsession.query(Project)
        .filter(Project.user_name == userid)
        .filter(Project.project_cod == projectid)
        .first()
    )
    if prjdat.project_regstatus == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "odk", "reg", "*.xml"]
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


def getAssessmentXMLForm(userid, projectid, assessmentid, request):
    prjdat = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == userid)
        .filter(Assessment.project_cod == projectid)
        .filter(Assessment.ass_cod == assessmentid)
        .first()
    )
    if prjdat.ass_status == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "odk", "ass", assessmentid, "*.xml"]
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


def getMediaFile(userid, projectid, fileid, request):
    prjdat = (
        request.dbsession.query(Project)
        .filter(Project.user_name == userid)
        .filter(Project.project_cod == projectid)
        .first()
    )
    if prjdat.project_regstatus == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "odk", "reg", "media", fileid]
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


def getAssessmentMediaFile(userid, projectid, assessmentid, fileid, request):
    prjdat = (
        request.dbsession.query(Assessment)
        .filter(Assessment.user_name == userid)
        .filter(Assessment.project_cod == projectid)
        .filter(Assessment.ass_cod == assessmentid)
        .first()
    )
    if prjdat.ass_status == 1:
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "odk", "ass", assessmentid, "media", fileid]
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


def storeJSONInMySQL(type, userid, userEnum, projectid, assessmentid, JSONFile, request):
    schema = userid + "_" + projectid
    if type == "REG":
        manifestFile = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "db", "reg", "manifest.xml"]
        )
        jsFile = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "db", "reg", "custom.js"]
        )

    else:
        manifestFile = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectid, "db", "ass", assessmentid, "manifest.xml"]
        )
        jsFile = ""

    #print(JSONFile)
    importedFile = os.path.splitext(JSONFile)[0] + ".imp"
    #print(importedFile)
    importedFile = '/'.join(JSONFile.split('/')[:-2])+"/myimportedFile.imp"

    logFile = os.path.splitext(JSONFile)[0] + ".log"
    jsonPath = os.path.dirname(JSONFile)
    mapPath = os.path.join(jsonPath, *["maps"])
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
        """storeError(
            fileuid,
            type,
            userid,
            projectid,
            assessmentid,
            p.returncode,
            stdout,
            " ".join(args),
            request,
        )"""
        
        if userEnum != None:
            addJsonLog(request,type,userid, userEnum,projectid,assessmentid,fileuid, JSONFile, logFile)


    return True


def convertXMLToJSON(
    userid,
    userEnum,
    XMLFile,
    JSONFile,
    projectID,
    submissionType,
    assessmentID,
    request,
):
    if submissionType == "REG":
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectID, "odk", "reg", "*.xml"]
        )
    if submissionType == "ASS":
        path = os.path.join(
            request.registry.settings["user.repository"],
            *[userid, projectID, "odk", "ass", assessmentID, "*.xml"]
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
            for plugin in p.PluginImplementations(p.ISubmissionStorage):
                data = plugin.before_save_in_json(request, userid, projectID, data)
            with open(JSONFile, "w") as outfile:
                data["_submitted_by"] = userEnum
                data["_submitted_date"] = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                jsonString = json.dumps(data, indent=4, ensure_ascii=False)
                outfile.write(jsonString)
            # Now we store the data in MySQL
            storeJSONInMySQL(
                submissionType, userid, userEnum,projectID, assessmentID, JSONFile, request
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
                if user == userInRequest:
                    if projectExists(user, project, request):
                        if isRegistryOpen(user, project, request):
                            if packageExist(root, user, project, request):
                                return True, 201, project, "REG", None
                            else:
                                return False, 404, None, None, None
                        else:
                            return False, 403, None, None, None
                    else:
                        return False, 404, None, None, None
                else:
                    return False, 403, None, None, None
            if xFormIDParts[0] == "ASS":
                user = xFormIDParts[1]
                project = xFormIDParts[2]
                assessment = xFormIDParts[3]
                if user == userInRequest:
                    if projectExists(user, project, request):
                        if isAssessmentOpen(user, project, assessment, request):
                            if assessmentExists(user, project, assessment, request):
                                return True, 201, project, "ASS", assessment
                            else:
                                return False, 404, None, None, None
                        else:
                            return False, 403, None, None, None
                    else:
                        return False, 404, None, None, None
                else:
                    return False, 403, None, None, None
        else:
            return False, 404, None, None, None
    else:
        return False, 404, None, None, None


def storeSubmission(userid, userEnum, request):
    # try:
    acceptSubmission = False
    projectID = None
    submissionType = None
    assessmentID = None
    error = 404
    for key in request.POST.keys():
        filename = request.POST[key].filename
        if filename.upper().find(".XML") >= 0:
            input_file = request.POST[key].file
            input_file.seek(0)
            (
                acceptSubmission,
                error,
                projectID,
                submissionType,
                assessmentID,
            ) = checkSubmission(userid, input_file, request)
    if acceptSubmission:
        iniqueID = uuid4()
        if submissionType == "REG":
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[userid, projectID, "data", "reg", "xml", str(iniqueID)]
            )
            if not os.path.exists(path):
                os.makedirs(path)
                os.makedirs(
                    os.path.join(
                        request.registry.settings["user.repository"],
                        *[userid, projectID, "data", "reg", "json", str(iniqueID)]
                    )
                )

        else:
            path = os.path.join(
                request.registry.settings["user.repository"],
                *[userid, projectID, "data", "ass", assessmentID, "xml", str(iniqueID)]
            )
            if not os.path.exists(path):
                os.makedirs(path)
                os.makedirs(
                    os.path.join(
                        request.registry.settings["user.repository"],
                        *[
                            userid,
                            projectID,
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
            print(key)
            filename = request.POST[key].filename
            input_file = request.POST[key].file
            file_path = os.path.join(path, filename)
            if file_path.upper().find(".XML") >= 0:
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
                userEnum,
                XMLFile,
                JSONFile,
                projectID,
                submissionType,
                assessmentID,
                request,
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
