import os

from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.processes import (
    getQuestionsStructure,
    generateStructureForInterfaceForms,
    get_registry_logs,
    get_assessment_logs,
    getTheProjectIdForOwner,
    getActiveProject,
    projectExists,
    getJSONResult,
)
from climmob.products.analysisdata.analysisdata import create_datacsv
from climmob.products.dataxlsx.dataxlsx import create_XLSXToDownload
from climmob.products.errorLogDocument.errorLogDocument import create_error_log_document
from climmob.views.classes import privateView
from climmob.views.editDataDB import (
    getNamesEditByColums,
    fillDataTable,
    update_edited_data,
)


class downloadDataView(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        formId = self.request.matchdict["formid"]
        formatId = self.request.matchdict["formatid"]
        includeRegistry = True
        includeAssessment = True
        code = ""
        formatExtra = ""

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if formId == "registry":
                formId = "Registration"
                includeAssessment = False
            else:
                if formId == "assessment":
                    formId = "Assessment"
                    includeAssessment = True
                    code = self.request.matchdict["codeid"]
                else:
                    raise HTTPNotFound()

        info = getJSONResult(
            activeProjectUser,
            activeProjectId,
            activeProjectCod,
            self.request,
            includeRegistry,
            includeAssessment,
            code,
        )

        if formatId not in ["csv", "xlsx"]:
            raise HTTPNotFound()

        if formatId == "csv":
            create_datacsv(
                activeProjectUser,
                activeProjectId,
                activeProjectCod,
                info,
                self.request,
                formId,
                code,
            )

        if formatId == "xlsx":
            formatExtra = formatId + "_"
            create_XLSXToDownload(
                activeProjectUser,
                activeProjectId,
                activeProjectCod,
                self.request,
                formId,
                code,
            )

        url = self.request.route_url(
            "productList",
            _query={"product1": "create_data_" + formatExtra + formId + "_" + code},
        )
        self.returnRawViewResult = True
        return HTTPFound(location=url)


class downloadErroLogDocument_view(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        formId = self.request.matchdict["formid"]
        code = ""
        data = {}
        _errors = []
        includeRegistry = True
        includeAssessment = True

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if formId == "registry":
                formId = "Registration"
                includeAssessment = False
                data = generateStructureForInterfaceForms(
                    activeProjectUser,
                    activeProjectId,
                    activeProjectCod,
                    "registry",
                    self.request,
                )
                _errors = get_registry_logs(self.request, activeProjectId)

                info = getJSONResult(
                    activeProjectUser,
                    activeProjectId,
                    activeProjectCod,
                    self.request,
                    includeRegistry,
                    includeAssessment,
                    code,
                )
            else:
                if formId == "assessment":
                    formId = "Assessment"
                    code = self.request.matchdict["codeid"]
                    data = generateStructureForInterfaceForms(
                        activeProjectUser,
                        activeProjectId,
                        activeProjectCod,
                        "assessment",
                        self.request,
                        ass_cod=code,
                    )
                    _errors = get_assessment_logs(self.request, activeProjectId, code)
                    includeRegistry = False
                    info = getJSONResult(
                        activeProjectUser,
                        activeProjectId,
                        activeProjectCod,
                        self.request,
                        includeRegistry,
                        includeAssessment,
                        code,
                    )

                else:
                    raise HTTPNotFound()

        create_error_log_document(
            self.request,
            self.request.locale_name,
            activeProjectUser,
            activeProjectId,
            activeProjectCod,
            formId,
            code,
            data,
            _errors,
            info,
        )

        url = self.request.route_url(
            "productList", _query={"product1": "create_errorlog_" + formId + "_" + code}
        )
        self.returnRawViewResult = True
        return HTTPFound(location=url)


class editDataView(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        formId = self.request.matchdict["formid"]
        code = ""

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if formId == "registry":
                formId = "reg"
            else:
                if formId == "assessment":
                    formId = "ass"
                    code = self.request.matchdict["codeid"]
                else:
                    raise HTTPNotFound()

            path = os.path.join(
                self.request.registry.settings["user.repository"],
                *[activeProjectUser, activeProjectCod]
            )
            if code == "":
                paths = ["db", formId, "create.xml"]
            else:
                paths = ["db", formId, code, "create.xml"]

            path = os.path.join(path, *paths)

            dataworking = {}  #
            dataworking["error"] = ""
            dataworking["data"] = False

            if "btn_EditData" in self.request.POST:
                selected_contacts = self.request.POST.getall("q_reg")
                if (
                    len(selected_contacts) == 0
                ):  # if non selected columns in check options

                    dataworking["error"] = "byC"
                    dataworking["msg"] = True
                else:

                    dataworking["data"] = True
                    dataworking["fill"] = fillDataTable(
                        self,
                        activeProjectUser,
                        activeProjectId,
                        activeProjectCod,
                        formId,
                        selected_contacts,
                        path,
                        code,
                    )
                    dataworking["error"] = ""

            else:
                if "json_data" in self.request.POST:
                    json_data = self.request.POST.getall("json_data")
                    dataworking["error"] = "byC"
                    dataworking["data"] = False
                    dataworking["msg"] = False

                    if json_data[0] != "":
                        dataworking["msg_flag"] = update_edited_data(
                            activeProjectUser,
                            activeProjectCod,
                            formId,
                            json_data,
                            path,
                            code,
                        )

            dataXML = getNamesEditByColums(path)

            dataOriginal = getQuestionsStructure(activeProjectId, code, self.request)
            newStructure = []
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

            return {
                "activeProject": getActiveProject(self.user.login, self.request),
                "dataworking": dataworking,
                "activeUser": self.user,
                "formId": formId,
                "newStructure": newStructure,
            }
