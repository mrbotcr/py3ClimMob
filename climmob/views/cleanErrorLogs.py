from .classes import privateView
from climmob.processes import projectExists
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from ..processes import (
    get_registry_logs,
    get_registry_log_by_log,
    get_assessment_logs,
    get_assessment_log_by_log,
    getProjectData,
    update_registry_status_log,
    update_assessment_status_log,
    isAssessmentOpen,
)
import os
from .editDataDB import getNamesEditByColums, fillDataTable
from climmob.processes import getQuestionsStructure
import json
import xml.etree.ElementTree as ET
from ..processes.odk.api import storeJSONInMySQL
import transaction
from zope.sqlalchemy import mark_changed
from climmob.models.repository import sql_execute


class cleanErrorLogs_view(privateView):
    def processView(self):
        proId = self.request.matchdict["projectid"]
        formId = self.request.matchdict["formid"]
        proData = getProjectData(self.user.login, proId, self.request)
        try:
            codeId = self.request.matchdict["codeid"]

            if not isAssessmentOpen(self.user.login, proId, codeId, self.request):
                raise HTTPNotFound()
        except:
            codeId = ""
            if int(proData["project_regstatus"]) == 2:
                raise HTTPNotFound()

        try:
            logId = self.request.matchdict["logid"]
        except:
            logId = ""

        if not projectExists(self.user.login, proId, self.request):
            raise HTTPNotFound()
        else:

            # GET
            if logId != "":

                if codeId == "":
                    exits, log = get_registry_log_by_log(
                        self.request, self.user.login, proId, logId
                    )

                else:
                    exits, log = get_assessment_log_by_log(
                        self.request, self.user.login, proId, codeId, logId
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
                                            formId, self, proId, "qst162", new_json
                                        )
                                        new_json[key] = dataworking["newqst"].split(
                                            "-"
                                        )[1]

                                        if "txt_oldvalue" not in dataworking.keys():
                                            dataworking["txt_oldvalue"] = -999

                                        with open(log, "w") as json_file:
                                            json.dump(new_json, json_file)

                                        if str(dataworking["txt_oldvalue"]) == str(
                                            dataworking["newqst"].split("-")[1]
                                        ):

                                            query = (
                                                "Delete from "
                                                + self.user.login
                                                + "_"
                                                + proId
                                                + ".REG_geninfo where qst162='"
                                                + dataworking["newqst"].split("-")[1]
                                                + "'"
                                            )
                                            # mySession = self.request.dbsession
                                            # transaction.begin()
                                            # mySession.execute(query)
                                            # mark_changed(mySession)
                                            # transaction.commit()
                                            sql_execute(query)

                                        storeJSONInMySQL(
                                            "REG",
                                            self.user.login,
                                            new_json["_submitted_by"],
                                            proId,
                                            codeId,
                                            log,
                                            self.request,
                                        )

                                        update_registry_status_log(
                                            self.request,
                                            self.user.login,
                                            proId,
                                            logId,
                                            2,
                                        )

                                        self.returnRawViewResult = True
                                        return HTTPFound(
                                            location=self.request.route_url(
                                                "CleanErrorLogs",
                                                projectid=proId,
                                                formid=formId,
                                            )
                                        )
                                    else:
                                        key = get_key_form_manifest(
                                            formId, self, proId, "qst163", new_json
                                        )
                                        new_json[key] = dataworking["newqst2"]

                                        if "txt_oldvalue" not in dataworking.keys():
                                            dataworking["txt_oldvalue"] = -999

                                        with open(log, "w") as json_file:
                                            json.dump(new_json, json_file)

                                        if str(dataworking["txt_oldvalue"]) == str(
                                            dataworking["newqst2"]
                                        ):
                                            query = (
                                                "Delete from "
                                                + self.user.login
                                                + "_"
                                                + proId
                                                + ".ASS"
                                                + codeId
                                                + "_geninfo where qst163='"
                                                + dataworking["newqst2"]
                                                + "'"
                                            )
                                            # mySession = self.request.dbsession
                                            # transaction.begin()
                                            # mySession.execute(query)
                                            # mark_changed(mySession)
                                            # transaction.commit()
                                            sql_execute(query)

                                        storeJSONInMySQL(
                                            "ASS",
                                            self.user.login,
                                            new_json["_submitted_by"],
                                            proId,
                                            codeId,
                                            log,
                                            self.request,
                                        )

                                        update_assessment_status_log(
                                            self.request,
                                            self.user.login,
                                            proId,
                                            codeId,
                                            logId,
                                            2,
                                        )

                                        self.returnRawViewResult = True
                                        return HTTPFound(
                                            location=self.request.route_url(
                                                "CleanErrorLogsAssessment",
                                                projectid=proId,
                                                formid=formId,
                                                codeid=codeId,
                                            )
                                        )

                                if "discard" in dataworking.keys():
                                    if formId == "registry":
                                        update_registry_status_log(
                                            self.request,
                                            self.user.login,
                                            proId,
                                            logId,
                                            3,
                                        )

                                        self.returnRawViewResult = True
                                        return HTTPFound(
                                            location=self.request.route_url(
                                                "CleanErrorLogs",
                                                projectid=proId,
                                                formid=formId,
                                            )
                                        )
                                    else:
                                        update_assessment_status_log(
                                            self.request,
                                            self.user.login,
                                            proId,
                                            codeId,
                                            logId,
                                            3,
                                        )

                                        self.returnRawViewResult = True
                                        return HTTPFound(
                                            location=self.request.route_url(
                                                "CleanErrorLogsAssessment",
                                                projectid=proId,
                                                formid=formId,
                                                codeid=codeId,
                                            )
                                        )

                            else:
                                new_json = convertJsonLog(formId, self, proId, new_json)

                if formId == "registry":
                    query = (
                        "select qst162 from "
                        + self.user.login
                        + "_"
                        + proId
                        + ".REG_geninfo;"
                    )
                    # mySession = self.request.dbsession
                    # result = mySession.execute(query)
                    result = sql_execute(query)
                    array = [int(new_json["qst162"])]
                    # array = []
                    for y in range(1, proData["project_numobs"] + 1):
                        array.append(y)

                    for x in result:
                        array.remove(int(x[0]))

                    structure, data = getStructureAndData(
                        formId, self, proId, codeId, str(new_json["qst162"])
                    )
                    return {
                        "Logs": get_registry_logs(self.request, self.user.login, proId),
                        "proId": proId,
                        "codeid": codeId,
                        "formId": formId,
                        "logId": logId,
                        "Structure": structure,
                        "Data": json.loads(data),
                        "New": new_json,
                        "PosibleValues": array,
                    }
                else:
                    # Edited by Brandon
                    path = os.path.join(
                        self.request.registry.settings["user.repository"],
                        *[self.user.login, proId]
                    )
                    paths = ["db", "ass", codeId, "create.xml"]
                    path = os.path.join(path, *paths)

                    rtable = ""
                    columns = []
                    tree = ET.parse(path)
                    for i, x in enumerate(tree.find("tables/table")):
                        if "odktype" in x.attrib:
                            if x.attrib["name"] == "qst163":
                                rtable = x.attrib["rtable"]

                    for i, x in enumerate(tree.find("lkptables")):
                        if x.attrib["name"] == rtable:
                            for s, y in enumerate(x):
                                columns.append(y.attrib["name"])
                    ###

                    queryR = (
                        "select qst163 from "
                        + self.user.login
                        + "_"
                        + proId
                        + ".ASS"
                        + codeId
                        + "_geninfo;"
                    )
                    # mySession = self.request.dbsession
                    # resultR = mySession.execute(queryR)
                    resultR = sql_execute(queryR)

                    array = []
                    for x in resultR:
                        if int(x[0]) != int(new_json["qst163"]):
                            array.append(int(x[0]))

                    # Edited by Brandon
                    _filters = ""
                    if array:
                        _filters = (
                            "where "
                            + columns[0]
                            + " not in("
                            + ",".join(map(str, array))
                            + ");"
                        )

                    """query = (
                        "select qst163_cod, qst163_des from "
                        + self.user.login
                        + "_"
                        + proId
                        + ".ASS"
                        + codeId
                        + "_lkpqst163 "
                        + _filters
                    )"""
                    query = (
                        "select "
                        + columns[0]
                        + ", "
                        + columns[1]
                        + " from "
                        + self.user.login
                        + "_"
                        + proId
                        + "."
                        + rtable
                        + " "
                        + _filters
                    )
                    # end edited

                    mySession = self.request.dbsession
                    result = mySession.execute(query)
                    array = []

                    for x in result:
                        array.append([x[0], x[1]])

                    structure, data = getStructureAndData(
                        formId, self, proId, codeId, str(new_json["qst163"])
                    )
                    return {
                        "Logs": get_assessment_logs(
                            self.request, self.user.login, proId, codeId
                        ),
                        "proId": proId,
                        "codeid": codeId,
                        "formId": formId,
                        "logId": logId,
                        "Structure": structure,
                        "Data": json.loads(data),
                        "New": new_json,
                        "PosibleValues": array,
                    }
            else:
                if formId == "registry":
                    _info = get_registry_logs(self.request, self.user.login, proId)
                    if not _info:
                        self.returnRawViewResult = True
                        return HTTPFound(location=self.request.route_url("dashboard"))
                    return {
                        "Logs": _info,
                        "proId": proId,
                        "codeid": codeId,
                        "formId": formId,
                        "logId": logId,
                    }
                else:
                    _info = get_assessment_logs(
                        self.request, self.user.login, proId, codeId
                    )
                    if not _info:
                        self.returnRawViewResult = True
                        return HTTPFound(location=self.request.route_url("dashboard"))
                    return {
                        "Logs": _info,
                        "proId": proId,
                        "codeid": codeId,
                        "formId": formId,
                        "logId": logId,
                    }


def getStructureAndData(formId, self, proId, code, filter):
    if formId == "registry":
        formId = "reg"
    else:
        if formId == "assessment":
            formId = "ass"
        else:
            raise HTTPNotFound()

    # Add by Brandon

    path = os.path.join(
        self.request.registry.settings["user.repository"], *[self.user.login, proId]
    )
    if code == "":
        paths = ["db", formId, "create.xml"]
    else:
        paths = ["db", formId, code, "create.xml"]

    path = os.path.join(path, *paths)

    dataXML = getNamesEditByColums(proId, path, code)
    selected_contacts = []
    newStructure = []
    if formId == "ass":
        # print "*********************************"
        dataOriginal = getQuestionsStructure(self.user.login, proId, code, self.request)

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

    fill = fillDataTable(self, proId, formId, selected_contacts, path, code, where)

    return newStructure, fill


def convertJsonLog(formId, self, proId, newjson):
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
        self.request.registry.settings["user.repository"], *[self.user.login, proId]
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


def get_key_form_manifest(formId, self, proId, search, newjson):
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
        self.request.registry.settings["user.repository"], *[self.user.login, proId]
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
