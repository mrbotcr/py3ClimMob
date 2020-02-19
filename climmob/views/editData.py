import climmob.plugins.utilities as u
from .classes import privateView
from .editDataDB import getNamesEditByColums, fillDataTable, update_edited_data

# Edit by Brandon
from climmob.processes import projectExists
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import os
from ..products.datadesk.datadesk import create_data_desk
from climmob.processes import getQuestionsStructure

##########
import json


class downloadDataView(privateView):
    def processView(self):
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
            path = os.path.join(path, *paths)
            # print path

        dataXML = getNamesEditByColums(proId, path, code)
        if formId == "ass":
            # print "*********************************"
            dataOriginal = getQuestionsStructure(
                self.user.login, proId, code, self.request
            )
            for originalData in dataOriginal:
                for vars in originalData["vars"]:
                    for xmldata in dataXML:
                        if vars["name"].lower() == xmldata[0]:
                            # print vars["name"]
                            index = dataXML.index(xmldata)
                            dataXML[index].append(vars["validation"].lower())
                            # print dataXML[index]
                            # xmldata.append(vars["validation"].lower())

        columns = dataXML
        selected_contacts = []
        for column in columns:
            try:
                selected_contacts.append(
                    column[0]
                    + "$%*"
                    + column[1]
                    + "$%*"
                    + column[2]
                    + "$%*"
                    + column[3]
                    + "$%*"
                    + column[4]
                    + "$%*"
                    + column[5]
                )
            except:
                selected_contacts.append(
                    column[0]
                    + "$%*"
                    + column[1]
                    + "$%*"
                    + column[2]
                    + "$%*"
                    + column[3]
                    + "$%*"
                    + column[4]
                    + "$%*"
                )
        data = fillDataTable(self, proId, formId, selected_contacts, path, code)

        create_data_desk(self.request, self.user.login, proId, data, formId + code)

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
        u.getJSResource("productsListaes").need()
        u.getJSResource("uploadDatajq").need()

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
                                "error": self._("You have information with errors.")
                            }
                        else:
                            correct = True
                            print("Termina la edicion de datos.")
                else:
                    error_summary = {
                        "error": self._("This data does not belong to this form.")
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

            """
            #u.getJSResource('jquery').need()
            u.getJSResource('bootstrap').need()
            u.getJSResource('qlibrary').need()

            # edit by columns code
            u.getJSResource('icheck').need()
            u.getCSSResource('icheck').need()
            u.getJSResource('editDatajq').need()

            u.getCSSResource('select2').need()
            u.getJSResource('select2').need()
            """

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
            if formId == "ass":
                # print "*********************************"
                dataOriginal = getQuestionsStructure(
                    self.user.login, proId, code, self.request
                )
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
            else:
                newStructure = dataXML
                # print newStructure

            # Finish Brandon
            # print newStructure
            # return {'dataworking': dataworking, 'activeUser': self.user, 'getNamesEditByColums': getNamesEditByColums(proId,path, code), 'newStructure': newStructure}  # 'fill_table_n': fill_table_n(self,proId)
            return {
                "dataworking": dataworking,
                "activeUser": self.user,
                "formId": formId,
                "newStructure": newStructure,
            }
