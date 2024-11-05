import json
import os
import xml.etree.ElementTree as ET

from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.models.repository import sql_execute, execute_two_sqls
from climmob.processes import (
    get_registry_logs,
    get_registry_log_by_log,
    get_assessment_logs,
    get_assessment_log_by_log,
    getProjectData,
    update_registry_status_log,
    update_assessment_status_log,
    isAssessmentOpen,
    getTheProjectIdForOwner,
    getActiveProject,
    getQuestionsStructure,
)
from climmob.processes import projectExists
from climmob.processes.odk.api import storeJSONInMySQL
from climmob.views.classes import privateView
from climmob.views.editDataDB import getNamesEditByColums, fillDataTable


class CleanErrorLogsView(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        pass

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )
        formId = self.request.matchdict["formid"]
        proData = getProjectData(activeProjectId, self.request)
        try:
            codeId = self.request.matchdict["codeid"]

            if not isAssessmentOpen(activeProjectId, codeId, self.request):
                raise HTTPNotFound()
        except:
            codeId = ""
            if int(proData["project_regstatus"]) == 2:
                raise HTTPNotFound()

        try:
            logId = self.request.matchdict["logid"]
        except:
            logId = ""

        # GET
        if logId != "":

            if codeId == "":
                exits, log = get_registry_log_by_log(
                    self.request, activeProjectId, logId
                )

            else:
                exits, log = get_assessment_log_by_log(
                    self.request, activeProjectId, codeId, logId
                )

            if exits:
                if os.path.exists(log):

                    with open(log, "r") as json_file:
                        new_json = json.load(json_file)

                        # POST
                        if self.request.method == "POST":
                            dataworking = self.getPostDict()
                            if "submit" in dataworking.keys():
                                if formId == "registry":
                                    key = get_key_form_manifest(
                                        formId,
                                        self,
                                        activeProjectUser,
                                        activeProjectCod,
                                        "qst162",
                                        new_json,
                                    )
                                    new_json[key] = dataworking["newqst"].split("-")[1]
        #
        #                             if "txt_oldvalue" not in dataworking.keys():
        #                                 dataworking["txt_oldvalue"] = -999
        #
        #                             with open(log, "w") as json_file:
        #                                 json.dump(new_json, json_file)
        #
        #                             if str(dataworking["txt_oldvalue"]) == str(
        #                                 dataworking["newqst"].split("-")[1]
        #                             ):
        #
        #                                 query = (
        #                                     "Delete from "
        #                                     + activeProjectUser
        #                                     + "_"
        #                                     + activeProjectCod
        #                                     + ".REG_geninfo where qst162='"
        #                                     + dataworking["newqst"].split("-")[1]
        #                                     + "'"
        #                                 )
        #                                 execute_two_sqls(
        #                                     "SET @odktools_current_user = '"
        #                                     + self.user.login
        #                                     + "';",
        #                                     query,
        #                                 )
        #
        #                             storeJSONInMySQL(
        #                                 self.user.login,
        #                                 "REG",
        #                                 activeProjectUser,
        #                                 new_json["_submitted_by"],
        #                                 activeProjectCod,
        #                                 codeId,
        #                                 log,
        #                                 self.request,
        #                                 activeProjectId,
        #                             )
        #
        #                             update_registry_status_log(
        #                                 self.request,
        #                                 activeProjectId,
        #                                 logId,
        #                                 2,
        #                             )
        #
        #                             self.returnRawViewResult = True
        #                             return HTTPFound(
        #                                 location=self.request.route_url(
        #                                     "CleanErrorLogs",
        #                                     user=activeProjectUser,
        #                                     project=activeProjectCod,
        #                                     formid=formId,
        #                                 )
        #                             )
        #                         else:
        #                             key = get_key_form_manifest(
        #                                 formId,
        #                                 self,
        #                                 activeProjectUser,
        #                                 activeProjectCod,
        #                                 "qst163",
        #                                 new_json,
        #                             )
        #                             new_json[key] = dataworking["newqst2"]
        #
        #                             if "txt_oldvalue" not in dataworking.keys():
        #                                 dataworking["txt_oldvalue"] = -999
        #
        #                             with open(log, "w") as json_file:
        #                                 json.dump(new_json, json_file)
        #
        #                             if str(dataworking["txt_oldvalue"]) == str(
        #                                 dataworking["newqst2"]
        #                             ):
        #                                 query = (
        #                                     "Delete from "
        #                                     + activeProjectUser
        #                                     + "_"
        #                                     + activeProjectCod
        #                                     + ".ASS"
        #                                     + codeId
        #                                     + "_geninfo where qst163='"
        #                                     + dataworking["newqst2"]
        #                                     + "'"
        #                                 )
        #                                 execute_two_sqls(
        #                                     "SET @odktools_current_user = '"
        #                                     + self.user.login
        #                                     + "'; ",
        #                                     query,
        #                                 )
        #
        #                             storeJSONInMySQL(
        #                                 self.user.login,
        #                                 "ASS",
        #                                 activeProjectUser,
        #                                 new_json["_submitted_by"],
        #                                 activeProjectCod,
        #                                 codeId,
        #                                 log,
        #                                 self.request,
        #                                 activeProjectId,
        #                             )
        #
        #                             update_assessment_status_log(
        #                                 self.request,
        #                                 activeProjectId,
        #                                 codeId,
        #                                 logId,
        #                                 2,
        #                             )
        #
        #                             self.returnRawViewResult = True
        #                             return HTTPFound(
        #                                 location=self.request.route_url(
        #                                     "CleanErrorLogsAssessment",
        #                                     user=activeProjectUser,
        #                                     project=activeProjectCod,
        #                                     formid=formId,
        #                                     codeid=codeId,
        #                                 )
        #                             )
        #
        #                     if "discard" in dataworking.keys():
        #                         if formId == "registry":
        #                             update_registry_status_log(
        #                                 self.request,
        #                                 activeProjectId,
        #                                 logId,
        #                                 3,
        #                             )
        #
        #                             self.returnRawViewResult = True
        #                             return HTTPFound(
        #                                 location=self.request.route_url(
        #                                     "CleanErrorLogs",
        #                                     user=activeProjectUser,
        #                                     project=activeProjectCod,
        #                                     formid=formId,
        #                                 )
        #                             )
        #                         else:
        #                             update_assessment_status_log(
        #                                 self.request,
        #                                 activeProjectId,
        #                                 codeId,
        #                                 logId,
        #                                 3,
        #                             )
        #
        #                             self.returnRawViewResult = True
        #                             return HTTPFound(
        #                                 location=self.request.route_url(
        #                                     "CleanErrorLogsAssessment",
        #                                     user=activeProjectUser,
        #                                     project=activeProjectCod,
        #                                     formid=formId,
        #                                     codeid=codeId,
        #                                 )
        #                             )
        #
        #                     if "deleteboth" in dataworking.keys():
        #
        #                         if formId == "registry":
        #
        #                             if str(dataworking["txt_oldvalue"]) == str(
        #                                 dataworking["newqst"].split("-")[1]
        #                             ):
        #                                 query = (
        #                                     "Delete from "
        #                                     + activeProjectUser
        #                                     + "_"
        #                                     + activeProjectCod
        #                                     + ".REG_geninfo where qst162='"
        #                                     + dataworking["newqst"].split("-")[1]
        #                                     + "'"
        #                                 )
        #                                 execute_two_sqls(
        #                                     "SET @odktools_current_user = '"
        #                                     + self.user.login
        #                                     + "'; ",
        #                                     query,
        #                                 )
        #
        #                             update_registry_status_log(
        #                                 self.request,
        #                                 activeProjectId,
        #                                 logId,
        #                                 3,
        #                             )
        #
        #                             self.returnRawViewResult = True
        #                             return HTTPFound(
        #                                 location=self.request.route_url(
        #                                     "CleanErrorLogs",
        #                                     user=activeProjectUser,
        #                                     project=activeProjectCod,
        #                                     formid=formId,
        #                                 )
        #                             )
        #                         else:
        #
        #                             if str(dataworking["txt_oldvalue"]) == str(
        #                                 dataworking["newqst2"]
        #                             ):
        #                                 query = (
        #                                     "Delete from "
        #                                     + activeProjectUser
        #                                     + "_"
        #                                     + activeProjectCod
        #                                     + ".ASS"
        #                                     + codeId
        #                                     + "_geninfo where qst163='"
        #                                     + dataworking["newqst2"]
        #                                     + "'"
        #                                 )
        #                                 execute_two_sqls(
        #                                     "SET @odktools_current_user = '"
        #                                     + self.user.login
        #                                     + "'; ",
        #                                     query,
        #                                 )
        #
        #                             update_assessment_status_log(
        #                                 self.request,
        #                                 activeProjectId,
        #                                 codeId,
        #                                 logId,
        #                                 3,
        #                             )
        #
        #                             self.returnRawViewResult = True
        #                             return HTTPFound(
        #                                 location=self.request.route_url(
        #                                     "CleanErrorLogsAssessment",
        #                                     user=activeProjectUser,
        #                                     project=activeProjectCod,
        #                                     formid=formId,
        #                                     codeid=codeId,
        #                                 )
        #                             )
        #
        #                 else:
        #                     new_json = convertJsonLog(
        #                         formId,
        #                         self,
        #                         activeProjectUser,
        #                         activeProjectCod,
        #                         new_json,
        #                     )
        #
        #     if formId == "registry":
        #         query = (
        #             "select qst162 from "
        #             + activeProjectUser
        #             + "_"
        #             + activeProjectCod
        #             + ".REG_geninfo;"
        #         )
        #         result = sql_execute(query)
        #         array = [int(new_json["qst162"])]
        #         # array = []
        #         for y in range(1, proData["project_numobs"] + 1):
        #             array.append(y)
        #
        #         for x in result:
        #             array.remove(int(x[0]))
        #
        #         structure, data = getStructureAndData(
        #             formId,
        #             self,
        #             activeProjectUser,
        #             activeProjectId,
        #             activeProjectCod,
        #             codeId,
        #             str(new_json["qst162"]),
        #         )
        #
        #         return {
        #             "Logs": get_registry_logs(self.request, activeProjectId),
        #             "activeProject": getActiveProject(self.user.login, self.request),
        #             "codeid": codeId,
        #             "formId": formId,
        #             "logId": logId,
        #             "Structure": structure,
        #             "Data": json.loads(data),
        #             "New": new_json,
        #             "PosibleValues": array,
        #         }
        #     else:
        #         # Edited by Brandon
        #         path = os.path.join(
        #             self.request.registry.settings["user.repository"],
        #             *[activeProjectUser, activeProjectCod]
        #         )
        #         paths = ["db", "ass", codeId, "create.xml"]
        #         path = os.path.join(path, *paths)
        #
        #         rtable = ""
        #         columns = []
        #         tree = ET.parse(path)
        #         for i, x in enumerate(tree.find("tables/table")):
        #             if "odktype" in x.attrib:
        #                 if x.attrib["name"] == "qst163":
        #                     rtable = x.attrib["rtable"]
        #
        #         for i, x in enumerate(tree.find("lkptables")):
        #             if x.attrib["name"] == rtable:
        #                 for s, y in enumerate(x):
        #                     columns.append(y.attrib["name"])
        #         ###
        #
        #         queryR = (
        #             "select qst163 from "
        #             + activeProjectUser
        #             + "_"
        #             + activeProjectCod
        #             + ".ASS"
        #             + codeId
        #             + "_geninfo;"
        #         )
        #         resultR = sql_execute(queryR)
        #
        #         array = []
        #         for x in resultR:
        #             if int(x[0]) != int(new_json["qst163"]):
        #                 array.append(int(x[0]))
        #
        #         # Edited by Brandon
        #         _filters = ""
        #         if array:
        #             _filters = (
        #                 "where "
        #                 + columns[0]
        #                 + " not in("
        #                 + ",".join(map(str, array))
        #                 + ");"
        #             )
        #
        #         query = (
        #             "select "
        #             + columns[0]
        #             + ", "
        #             + columns[1]
        #             + " from "
        #             + activeProjectUser
        #             + "_"
        #             + activeProjectCod
        #             + "."
        #             + rtable
        #             + " "
        #             + _filters
        #         )
        #         # end edited
        #
        #         result = sql_execute(query)
        #
        #         array = []
        #
        #         for x in result:
        #             array.append([x[0], x[1]])
        #
        #         structure, data = getStructureAndData(
        #             formId,
        #             self,
        #             activeProjectUser,
        #             activeProjectId,
        #             activeProjectCod,
        #             codeId,
        #             str(new_json["qst163"]),
        #         )
        #         return {
        #             "Logs": get_assessment_logs(self.request, activeProjectId, codeId),
        #             "activeProject": getActiveProject(self.user.login, self.request),
        #             "codeid": codeId,
        #             "formId": formId,
        #             "logId": logId,
        #             "Structure": structure,
        #             "Data": json.loads(data),
        #             "New": new_json,
        #             "PosibleValues": array,
        #         }
        # else:
        #     if formId == "registry":
        #         _info = get_registry_logs(self.request, activeProjectId)
        #         if not _info:
        #             self.returnRawViewResult = True
        #             return HTTPFound(location=self.request.route_url("dashboard"))
        #         return {
        #             "Logs": _info,
        #             "activeProject": getActiveProject(self.user.login, self.request),
        #             "codeid": codeId,
        #             "formId": formId,
        #             "logId": logId,
        #         }
        #     else:
        #         _info = get_assessment_logs(self.request, activeProjectId, codeId)
        #         if not _info:
        #             self.returnRawViewResult = True
        #             return HTTPFound(location=self.request.route_url("dashboard"))
        #         return {
        #             "Logs": _info,
        #             "activeProject": getActiveProject(self.user.login, self.request),
        #             "codeid": codeId,
        #             "formId": formId,
        #             "logId": logId,
        #         }


def getStructureAndData(formId, self, userOwner, projectId, projectCod, code, filter):
    if formId == "registry":
        formId = "reg"
    else:
        if formId == "assessment":
            formId = "ass"
        else:
            raise HTTPNotFound()

    # Add by Brandon

    path = os.path.join(
        self.request.registry.settings["user.repository"], *[userOwner, projectCod]
    )
    if code == "":
        paths = ["db", formId, "create.xml"]
    else:
        paths = ["db", formId, code, "create.xml"]

    path = os.path.join(path, *paths)

    dataXML = getNamesEditByColums(path)
    selected_contacts = []
    newStructure = []
    if formId == "ass":
        # print "*********************************"
        dataOriginal = getQuestionsStructure(projectId, code, self.request)

        for originalData in dataOriginal:
            questInfo = {}
            questInfo["name"] = originalData["name"]
            questInfo["id"] = originalData["id"]
            questInfo["vars"] = []
            for vars in originalData["vars"]:

                for xmldata in dataXML:
                    if vars["name"].lower() == xmldata[0]:
                        xmldata.append(vars["validation"].lower())
                        questInfo["vars"].append(xmldata)
            newStructure.append(questInfo)

        aux_newStructure = []
        for quest in newStructure:
            for col in quest["vars"]:

                selected_contacts.append(
                    col[0]
                    + "$%*"
                    + col[1]
                    + "$%*"
                    + col[2]
                    + "$%*"
                    + col[3]
                    + "$%*"
                    + col[4]
                    + "$%*"
                )
            aux_newStructure.append(quest["vars"])

        newStructure = aux_newStructure
        where = "where qst163 = " + filter
    else:
        newStructure = dataXML
        newStructure.append(["qst162", "Package code", "string", "", ""])
        where = "where qst162 = " + filter

        for col in newStructure:
            selected_contacts.append(
                col[0]
                + "$%*"
                + col[1]
                + "$%*"
                + col[2]
                + "$%*"
                + col[3]
                + "$%*"
                + col[4]
                + "$%*"
            )

    fill = fillDataTable(
        self,
        userOwner,
        projectId,
        projectCod,
        formId,
        selected_contacts,
        path,
        code,
        where,
    )

    return newStructure, fill


def convertJsonLog(formId, self, userOwner, projectCod, newjson):
    if formId == "registry":
        formId = "reg"
        code = ""
    else:
        if formId == "assessment":
            formId = "ass"
            code = self.request.matchdict["codeid"]
        else:
            raise HTTPNotFound()

    path = os.path.join(
        self.request.registry.settings["user.repository"], *[userOwner, projectCod]
    )
    if code == "":
        paths = ["db", formId, "manifest.xml"]
    else:
        paths = ["db", formId, code, "manifest.xml"]

    path = os.path.join(path, *paths)

    tree = ET.parse(path)

    convertjson = {}
    for i, x in enumerate(tree.find("table")):
        row = []
        if x.attrib["xmlcode"] in newjson.keys():
            if x.attrib["mysqlcode"] != "qst162":
                convertjson[x.attrib["mysqlcode"]] = newjson[x.attrib["xmlcode"]]
            else:
                convertjson[x.attrib["mysqlcode"]] = newjson[x.attrib["xmlcode"]].split(
                    "-"
                )[1]

    return convertjson


def get_key_form_manifest(formId, self, userOwner, projectCod, search, newjson):

    if formId == "registry":
        formId = "reg"
        code = ""
    else:
        if formId == "assessment":
            formId = "ass"
            code = self.request.matchdict["codeid"]
        else:
            raise HTTPNotFound()

    path = os.path.join(
        self.request.registry.settings["user.repository"], *[userOwner, projectCod]
    )
    if code == "":
        paths = ["db", formId, "manifest.xml"]
    else:
        paths = ["db", formId, code, "manifest.xml"]

    path = os.path.join(path, *paths)

    tree = ET.parse(path)

    for i, x in enumerate(tree.find("table")):
        if x.attrib["mysqlcode"] == search:
            return x.attrib["xmlcode"]
