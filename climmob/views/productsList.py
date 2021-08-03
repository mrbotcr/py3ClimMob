from ..plugins.utilities import (
    climmobPublicView,
    climmobPrivateView,
    getProductDirectory,
    getProducts,
)
from .classes import privateView
from ..products import product_found
import climmob.plugins.utilities as u
from pyramid.response import FileResponse
import os
import json

from pyramid.httpexceptions import HTTPFound

from ..processes import (
    getActiveProject,
    getProductData,
    getPackages,
    getTech,
    getProjectEnumerators,
    numberOfCombinationsForTheProject,
    searchTechnologiesInProject,
    getJSONResult,
    getProjectData,
    getProjectAssessments,
    getInformationFromProject,
    getInformationForMaps,
    getProjectAssessmentInfo,
    generateStructureForInterfaceForms,
    get_registry_logs,
    get_assessment_logs,
)
from .projectHelp.projectHelp import getImportantInformation
from .registry import getDataFormPreview

from ..products.qrpackages.qrpackages import create_qr_packages
from ..products.packages.packages import create_packages_excell
from ..products.colors.colors import create_colors_cards
from ..products.fieldagents.fieldagents import create_fieldagents_report
from ..products.analysisdata.analysisdata import create_datacsv
from ..products.forms.form import create_document_form
from ..products.generalReport.generalReport import create_general_report
from ..products.stickers.stickers import create_stickers_document
from ..products.datacollectionprogress.dataCollectionProgress import (
    create_data_collection_progress,
)
from ..products.errorLogDocument.errorLogDocument import create_error_log_document
import climmob.plugins as p


def getDataProduct(user, project, request):

    sql = (
        "select edited.celery_taskid,edited.user_name,edited.project_cod,edited.product_id, edited.datetime_added, edited.output_id,edited.state, edited.output_mimetype, edited.output_mimetype, edited.process_name "
        "from "
        "("
        "SELECT *,'Success' as state  FROM products p where p.celery_taskid in (select taskid from finishedtasks where taskerror = 0) "
        "UNION "
        "SELECT *,'Fail.' as state  FROM products p where p.celery_taskid in (select taskid from finishedtasks where taskerror = 1) "
        "UNION "
        "SELECT *,'Pending...' as state  FROM products p where p.celery_taskid not in (select taskid from finishedtasks) and datediff(sysdate(),datetime_added)<2 "
        "UNION "
        "SELECT *,'Fail.' as state  FROM products p where p.celery_taskid not in (select taskid from finishedtasks) and datediff(sysdate(),datetime_added)>=2 "
        ") "
        "as edited "
        "where edited.datetime_added = (SELECT max(datetime_added) FROM products where project_cod = '"
        + project
        + "' and user_name='"
        + user
        + "' and product_id= edited.product_id and process_name= edited.process_name) and edited.user_name='"
        + user
        + "' and edited.project_cod='"
        + project
        + "' order by field(edited.product_id,'fieldagents','packages','qrpackage') desc, edited.datetime_added"
    )

    # print(sql)

    """sql = "select edited.celery_taskid,edited.user_name,edited.project_cod,edited.product_id, edited.datetime_added, edited.output_id, edited.state " \
          "from " \
          "(" \
          "SELECT *,'Success' as state  FROM products p where p.celery_taskid in (select taskid from finishedtasks where taskerror = 0) " \
          "UNION " \
          "SELECT *,'Fail.' as state  FROM products p where p.celery_taskid in (select taskid from finishedtasks where taskerror = 1) " \
          "UNION " \
          "SELECT *,'Pending...' as state  FROM products p where p.celery_taskid not in (select taskid from finishedtasks) and datediff(sysdate(),datetime_added)<2 " \
          "UNION " \
          "SELECT *,'Fail.' as state  FROM products p where p.celery_taskid not in (select taskid from finishedtasks) and datediff(sysdate(),datetime_added)>=2 " \
          ") " \
          "as edited " \
          "where edited.datetime_added = (select max(p.datetime_added) from products p where p.product_id =edited.product_id) and edited.user_name='"+user+"' and edited.project_cod='"+project+"'"
    """

    """sql = "SELECT *,'Success' as state  FROM products p where p.celery_taskid in (select taskid from finishedtasks where taskerror = 0) " \
          "UNION " \
          "SELECT *,'Fail.' as state  FROM products p where p.celery_taskid in (select taskid from finishedtasks where taskerror = 1) " \
          "UNION " \
          "SELECT *,'Pending...' as state  FROM products p where p.celery_taskid not in (select taskid from finishedtasks) and datediff(sysdate(),datetime_added)<2 " \
          "UNION " \
          "SELECT *,'Fail.' as state  FROM products p where p.celery_taskid not in (select taskid from finishedtasks) and datediff(sysdate(),datetime_added)>=2 "
    """
    questions = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in questions:
        dct = dict(qst)
        result.append(dct)

    return result


class productsView(climmobPrivateView):
    def processView(self):

        hasActiveProject = False
        activeProjectData = getActiveProject(self.user.login, self.request)
        if activeProjectData:
            products = getDataProduct(
                self.user.login, activeProjectData["project_cod"], self.request
            )

            for product in products:

                if product_found(product["product_id"]):
                    contentType = product["output_mimetype"]
                    filename = product["output_id"]
                    path = getProductDirectory(
                        self.request,
                        self.user.login,
                        activeProjectData["project_cod"],
                        product["product_id"],
                    )

                    if os.path.exists(path + "/outputs/" + filename):
                        product["exists"] = "correct"
                    else:
                        product["exists"] = "incorrect"

                    if (
                        product["product_id"] == "documentform"
                        or product["product_id"] == "datacsv"
                        or product["product_id"] == "errorlogdocument"
                        or product["product_id"] == "multimediadownloads"
                    ):
                        product["extraInformation"] = getProjectAssessmentInfo(
                            self.user.login,
                            activeProjectData["project_cod"],
                            product["process_name"].split("_")[3],
                            self.request,
                        )

            if activeProjectData["project_active"] == 1:
                hasActiveProject = True
        else:
            products = []

        return {
            "activeUser": self.user,
            "activeProject": activeProjectData,
            "hasActiveProject": hasActiveProject,
            "Products": products,
        }


class generateProductView(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        productid = self.request.matchdict["productid"]
        processname = self.request.matchdict["processname"]

        if productid == "qrpackage":

            ncombs, packages = getPackages(self.user.login, projectid, self.request)
            create_qr_packages(
                self.request,
                self.request.locale_name,
                self.user.login,
                projectid,
                ncombs,
                packages,
            )

        if productid == "packages":
            ncombs, packages = getPackages(
                self.request.locale_name, self.user.login, projectid, self.request
            )
            create_packages_excell(
                self.request,
                self.user.login,
                projectid,
                packages,
                getTech(self.user.login, projectid, self.request),
            )

        if productid == "fieldagents":
            locale = self.request.locale_name
            create_fieldagents_report(
                locale,
                self.request,
                self.user.login,
                projectid,
                getProjectEnumerators(self.user.login, projectid, self.request),
            )

        if productid == "colors":
            ncombs, packages = getPackages(self.user.login, projectid, self.request)
            numberOfCombinations = numberOfCombinationsForTheProject(
                self.user.login, projectid, self.request
            )

            if numberOfCombinations == 3:
                tech = searchTechnologiesInProject(
                    self.user.login, projectid, self.request
                )
                if len(tech) == 1:
                    if (
                        tech[0]["tech_name"] == "Colores"
                        or tech[0]["tech_name"] == "Colors"
                    ):
                        create_colors_cards(
                            self.request, self.user.login, projectid, packages
                        )

        if productid == "datacsv":
            locale = self.request.locale_name
            infoProduct = processname.split("_")
            if infoProduct[2] == "Registration":
                info = getJSONResult(
                    self.user.login, projectid, self.request, includeAssessment=False
                )
            else:
                if infoProduct[2] == "Assessment":
                    info = getJSONResult(
                        self.user.login,
                        projectid,
                        self.request,
                        assessmentCode=infoProduct[3],
                    )
                else:
                    info = getJSONResult(self.user.login, projectid, self.request,)

            create_datacsv(
                self.user.login,
                projectid,
                info,
                self.request,
                infoProduct[2],
                infoProduct[3],
            )

        if productid == "documentform":
            ncombs, packages = getPackages(self.user.login, projectid, self.request)
            if processname == "create_from_Registration_":
                data, finalCloseQst = getDataFormPreview(self, projectid)
                create_document_form(
                    self.request,
                    self.request.locale_name,
                    self.user.login,
                    projectid,
                    "Registration",
                    "",
                    data,
                    packages,
                )
            else:
                assessment_id = processname.split("_")[3]
                data, finalCloseQst = getDataFormPreview(self, projectid, assessment_id)
                create_document_form(
                    self.request,
                    self.request.locale_name,
                    self.user.login,
                    projectid,
                    "Assessment",
                    assessment_id,
                    data,
                    packages,
                )

        if productid == "errorlogdocument":
            if processname == "create_errorlog_Registration_":
                data = generateStructureForInterfaceForms(
                    self.user.login, projectid, "registry", self.request
                )
                _errors = get_registry_logs(self.request, self.user.login, projectid)
                info = getJSONResult(
                    self.user.login,
                    projectid,
                    self.request,
                    includeRegistry=True,
                    includeAssessment=False,
                    assessmentCode="",
                )
                create_error_log_document(
                    self.request,
                    self.request.locale_name,
                    self.user.login,
                    projectid,
                    "Registration",
                    "",
                    data,
                    _errors,
                    info,
                )
            else:
                assessment_id = processname.split("_")[3]
                data = generateStructureForInterfaceForms(
                    self.user.login,
                    projectid,
                    "assessment",
                    self.request,
                    ass_cod=assessment_id,
                )
                _errors = get_assessment_logs(
                    self.request, self.user.login, projectid, assessment_id
                )
                info = getJSONResult(
                    self.user.login,
                    projectid,
                    self.request,
                    includeRegistry=False,
                    includeAssessment=True,
                    assessmentCode=assessment_id,
                )
                create_error_log_document(
                    self.request,
                    self.request.locale_name,
                    self.user.login,
                    projectid,
                    "Assessment",
                    assessment_id,
                    data,
                    _errors,
                    info,
                )

        if productid == "generalreport":
            dataworking = {}
            dataworking["project_username"] = self.user.login
            dataworking["project_cod"] = projectid
            dataworking["project_details"] = getProjectData(
                self.user.login, projectid, self.request
            )
            dataworking = getImportantInformation(dataworking, self.request)
            dataworking["project_fieldagents"] = getProjectEnumerators(
                self.user.login, projectid, self.request
            )
            dataRegistry, finalCloseQst = getDataFormPreview(
                self, projectid, createAutoRegistry=False
            )
            dataworking["project_registry"] = dataRegistry
            dataAssessments = getProjectAssessments(
                self.user.login, projectid, self.request
            )
            for assessment in dataAssessments:
                dataAssessmentsQuestions, finalCloseQst = getDataFormPreview(
                    self, projectid, assessment["ass_cod"]
                )
                assessment["Questions"] = dataAssessmentsQuestions
            dataworking["project_assessment"] = dataAssessments
            create_general_report(
                self.request,
                self.request.locale_name,
                self.user.login,
                projectid,
                dataworking,
            )

        if productid == "stickers":
            locale = self.request.locale_name
            ncombs, packages = getPackages(self.user.login, projectid, self.request)

            create_stickers_document(
                locale, self.request, self.user.login, projectid, packages
            )

        if productid == "datacollectionprogress":
            geoInformation = getInformationForMaps(
                self.request, self.user.login, projectid
            )
            create_data_collection_progress(
                self.request,
                self.request.locale_name,
                self.user.login,
                projectid,
                getInformationFromProject(self.request, self.user.login, projectid),
                geoInformation,
            )

        if productid == "multimediadownloads":
            for plugin in p.PluginImplementations(p.IMultimedia):
                if processname == "create_multimedia_Registration_":
                    plugin.start_multimedia_download(
                        self.request, self.user.login, projectid, "Registration", ""
                    )
                else:
                    assessment_id = processname.split("_")[3]
                    plugin.start_multimedia_download(
                        self.request,
                        self.user.login,
                        projectid,
                        "Assessment",
                        assessment_id,
                    )

        self.returnRawViewResult = True
        return HTTPFound(location=self.request.route_url("productList"))


class downloadJsonView(climmobPrivateView):
    def processView(self):
        celery_taskid = self.request.matchdict["celery_taskid"]
        product_id = self.request.matchdict["product_id"]
        activeProjectData = getActiveProject(self.user.login, self.request)
        dataworking = getProductData(
            self.user.login,
            activeProjectData["project_cod"],
            celery_taskid,
            product_id,
            self.request,
        )
        product_id = dataworking["product_id"]

        if product_found(product_id):
            contentType = dataworking["output_mimetype"]
            filename = dataworking["output_id"]
            path = getProductDirectory(
                self.request,
                self.user.login,
                activeProjectData["project_cod"],
                product_id,
            )

            data = ""
            with open(path + "/outputs/" + filename) as f:
                data = json.load(f)

            self.returnRawViewResult = True
            return data


class downloadView(climmobPrivateView):
    def processView(self):
        celery_taskid = self.request.matchdict["celery_taskid"]
        product_id = self.request.matchdict["product_id"]
        activeProjectData = getActiveProject(self.user.login, self.request)
        dataworking = getProductData(
            self.user.login,
            activeProjectData["project_cod"],
            celery_taskid,
            product_id,
            self.request,
        )
        product_id = dataworking["product_id"]

        if product_found(product_id):
            contentType = dataworking["output_mimetype"]
            filename = dataworking["output_id"]
            path = getProductDirectory(
                self.request,
                self.user.login,
                activeProjectData["project_cod"],
                product_id,
            )
            response = FileResponse(
                path + "/outputs/" + filename,
                request=self.request,
                content_type=contentType,
            )
            response.content_disposition = 'attachment; filename="' + filename + '"'
            self.returnRawViewResult = True
            return response

        else:
            self.returnRawViewResult = True
            return False

    def contentType_found(self, product_id):
        # product_id = 'qrpackage'
        products = getProducts()
        for product in products:
            if product["name"] == product_id:
                return product["outputs"][0]["mimetype"]

        return False

    def filename_found(self, product_id):
        # product_id = 'qrpackage'
        products = getProducts()
        for product in products:
            if product["name"] == product_id:
                return product["outputs"][0]["filename"]

        return False


class dataView(climmobPrivateView):
    def processView(self):
        activeProjectData = getActiveProject(self.user.login, self.request)
        products = getDataProduct(
            self.user.login, activeProjectData["project_cod"], self.request
        )
        return {"Products": products}
