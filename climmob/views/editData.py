import climmob.plugins.utilities as u
from .classes import privateView
from .editDataDB import getNamesEditByColums, fillDataTable, update_edited_data

# Edit by Brandon
from climmob.processes import projectExists, getJSONResult
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import os
from ..products.datadesk.datadesk import create_data_desk
from ..products.analysisdata.analysisdata import create_datacsv
from ..products.errorLogDocument.errorLogDocument import create_error_log_document
from climmob.processes import (
    getQuestionsStructure,
    generateStructureForInterfaceForms,
    get_registry_logs,
    get_assessment_logs,
)

##########
import json


class downloadDataView(privateView):
    def processView(self):
        proId = self.request.matchdict["projectid"]
        formId = self.request.matchdict["formid"]
        includeRegistry = True
        includeAssessment = True
        code = ""

        if not projectExists(self.user.login, proId, self.request):
            raise HTTPNotFound()
        else:

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
            self.user.login,
            proId,
            self.request,
            includeRegistry,
            includeAssessment,
            code,
        )

        create_datacsv(self.user.login, proId, info, self.request, formId, code)

        url = self.request.route_url("productList")
        self.returnRawViewResult = True
        return HTTPFound(location=url)


class downloadErroLogDocument_view(privateView):
    def processView(self):
        proId = self.request.matchdict["projectid"]
        formId = self.request.matchdict["formid"]
        code = ""
        data = {}
        _errors = []
        includeRegistry = True
        includeAssessment = True
        if not projectExists(self.user.login, proId, self.request):
            raise HTTPNotFound()
        else:

            if formId == "registry":
                formId = "Registration"
                includeAssessment = False
                data = generateStructureForInterfaceForms(
                    self.user.login, proId, "registry", self.request
                )
                _errors = get_registry_logs(self.request, self.user.login, proId)

                info = getJSONResult(
                    self.user.login,
                    proId,
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
                        self.user.login, proId, "assessment", self.request, ass_cod=code
                    )
                    _errors = get_assessment_logs(
                        self.request, self.user.login, proId, code
                    )
                    includeRegistry = False
                    info = getJSONResult(
                        self.user.login,
                        proId,
                        self.request,
                        includeRegistry,
                        includeAssessment,
                        code,
                    )

                else:
                    raise HTTPNotFound()

        create_error_log_document(
            self.request, self.request.locale_name,self.user.login, proId, formId, code, data, _errors, info
        )

        url = self.request.route_url("productList")
        self.returnRawViewResult = True
        return HTTPFound(location=url)


class uploadDataView(privateView):
    def processView(self):
        error_summary = {}
        proId = self.request.matchdict["projectid"]
        formId = self.request.matchdict["formid"]
        code = ""
        # print proId
        # print formId
        # u.getJSResource("productsListaes").need()
        # u.getJSResource("uploadDatajq").need()

        if not projectExists(self.user.login, proId, self.request):
            raise HTTPNotFound()
        else:
            if self.request.method == "GET":

                return {
                    "activeUser": self.user,
                    "error_summary": error_summary,
                    "correct": False,
                }
            else:

                dataworking = self.getPostDict()
                _json = json.loads(dataworking["dataUpload"])

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
                    *[self.user.login, proId]
                )
                if code == "":
                    paths = ["db", formId, "create.xml"]
                else:
                    paths = ["db", formId, code, "create.xml"]

                path = os.path.join(path, *paths)

                correct = False
                if (
                    _json["projectMeta"][0]["code"] == code
                    and _json["projectMeta"][0]["project_code"] == proId
                    and _json["projectMeta"][0]["form"] == formId
                    and _json["projectMeta"][0]["user"] == self.user.login
                ):
                    json_data = self.request.POST.getall("dataNeccessaryUpload")
                    if json_data[0] != "":
                        output = update_edited_data(
                            self, proId, formId, json_data, path, code
                        )
                        if output == 0:
                            error_summary = {
                                "error": self._(
                                    "The information you provided has errors."
                                )
                            }
                        else:
                            correct = True
                            print("Termina la edicion de datos.")
                else:
                    error_summary = {
                        "error": self._("These data do not belong to this form.")
                    }

                return {
                    "activeUser": self.user,
                    "error_summary": error_summary,
                    "correct": correct,
                }

        return ""


class editDataView(privateView):
    def processView(self):

        # Edit by Brandon
        # proId = 'prueba_qrs'  # the name of project or database in edit module, www is the test database
        proId = self.request.matchdict["projectid"]
        formId = self.request.matchdict["formid"]
        code = ""
        # print proId
        # print formId
        if not projectExists(self.user.login, proId, self.request):
            raise HTTPNotFound()
        else:

            if formId == "registry":
                formId = "reg"
            else:
                if formId == "assessment":
                    formId = "ass"
                    code = self.request.matchdict["codeid"]
                else:
                    raise HTTPNotFound()

            # Add by Brandon
            path = os.path.join(
                self.request.registry.settings["user.repository"],
                *[self.user.login, proId]
            )
            if code == "":
                paths = ["db", formId, "create.xml"]
            else:
                paths = ["db", formId, code, "create.xml"]
            # print "*************************************************"
            path = os.path.join(path, *paths)
            # files = glob(path + '/*.xml')
            # path = files[0]
            # print path
            # print "*************************************************"
            #########

            ####

            dataworking = {}  #
            dataworking["error"] = ""
            dataworking["data"] = False

            if "btn_EditData" in self.request.POST:
                selected_contacts = self.request.POST.getall("q_reg")
                print(selected_contacts)
                if (
                    len(selected_contacts) == 0
                ):  # if non selected columns in check options

                    dataworking["error"] = "byC"
                    dataworking["msg"] = True
                else:  # if the user select more than 1 columns
                    """
                    u.getJSResource('gridl').need()
                    u.getJSResource('jqgrid').need()
                    u.getJSResource('sweet').need()

                    u.getCSSResource('jqgrid').need()
                    #u.getCSSResource('jquery').need()
                    u.getCSSResource('sweet').need()
                    """

                    # print selected_contacts
                    dataworking["data"] = True
                    dataworking["fill"] = fillDataTable(
                        self, proId, formId, selected_contacts, path, code
                    )
                    dataworking["error"] = ""

                    # print dataworking['fill']

            else:
                if "json_data" in self.request.POST:
                    json_data = self.request.POST.getall("json_data")
                    dataworking["error"] = "byC"
                    dataworking["data"] = False
                    dataworking["msg"] = False
                    # u.getJSResource('sweet').need()
                    # u.getCSSResource('sweet').need()
                    if json_data[0] != "":
                        dataworking["msg_flag"] = update_edited_data(
                            self, proId, formId, json_data, path, code
                        )

            # Added by Brandon
            dataXML = getNamesEditByColums(proId, path, code)
            # print(dataXML)
            # if formId == "ass":
            #    # print "*********************************"
            dataOriginal = getQuestionsStructure(
                self.user.login, proId, code, self.request
            )
            newStructure = []
            for originalData in dataOriginal:
                questInfo = {}
                questInfo["name"] = originalData["name"]
                questInfo["id"] = originalData["id"]
                questInfo["vars"] = []
                # print(originalData)
                for vars in originalData["vars"]:
                    # print(vars["name"].lower())
                    for xmldata in dataXML:
                        if vars["name"].lower() == xmldata[0]:
                            xmldata.append(vars["validation"].lower())
                            questInfo["vars"].append(xmldata)

                # print(questInfo)
                newStructure.append(questInfo)
            # else:
            #    newStructure = dataXML
            #    # print newStructure

            # Finish Brandon
            # print newStructure
            # return {'dataworking': dataworking, 'activeUser': self.user, 'getNamesEditByColums': getNamesEditByColums(proId,path, code), 'newStructure': newStructure}  # 'fill_table_n': fill_table_n(self,proId)
            return {
                "dataworking": dataworking,
                "activeUser": self.user,
                "formId": formId,
                "newStructure": newStructure,
            }
