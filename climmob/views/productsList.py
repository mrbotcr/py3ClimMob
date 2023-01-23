import os

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import FileResponse

import climmob.plugins as p
from climmob.plugins.utilities import (
    climmobPrivateView,
    getProductDirectory,
    getProducts,
)
from climmob.processes import (
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
from climmob.products import product_found
from climmob.products.analysisdata.analysisdata import create_datacsv
from climmob.products.dataxlsx.dataxlsx import create_XLSXToDownload
from climmob.products.colors.colors import create_colors_cards
from climmob.products.errorLogDocument.errorLogDocument import create_error_log_document
from climmob.products.fieldagents.fieldagents import create_fieldagents_report
from climmob.products.forms.form import create_document_form
from climmob.products.generalReport.generalReport import create_general_report
from climmob.products.packages.packages import create_packages_excell
from climmob.products.qrpackages.qrpackages import create_qr_packages
from climmob.views.classes import privateView
from climmob.views.projectHelp.projectHelp import getImportantInformation
from climmob.views.registry import getDataFormPreview


def getDataProduct(projectId, request):

    sql = (
        "select edited.celery_taskid,edited.project_id,edited.product_id, edited.datetime_added, edited.output_id,edited.state, edited.output_mimetype, edited.output_mimetype, edited.process_name "
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
        "where edited.datetime_added = (SELECT max(datetime_added) FROM products where project_id = '"
        + projectId
        + "' and product_id= edited.product_id and process_name= edited.process_name) and edited.project_id='"
        + projectId
        + "' order by field(edited.product_id,'fieldagents','packages','qrpackagewithtechnologies','qrpackage') desc, edited.datetime_added"
    )

    products = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in products:
        dct = dict(qst)
        result.append(dct)

    return result


class productsView(climmobPrivateView):
    def processView(self):

        hasActiveProject = False
        activeProjectData = getActiveProject(self.user.login, self.request)
        productsAvailable = []
        assessments = []

        if activeProjectData:

            products = getDataProduct(activeProjectData["project_id"], self.request)

            for product in products:
                if product_found(product["product_id"]):
                    contentType = product["output_mimetype"]
                    filename = product["output_id"]
                    path = getProductDirectory(
                        self.request,
                        activeProjectData["owner"]["user_name"],
                        activeProjectData["project_cod"],
                        product["product_id"],
                    )

                    if os.path.exists(path + "/outputs/" + filename):
                        product["exists"] = "correct"
                    else:
                        product["exists"] = "incorrect"

                    if product["product_id"] in [
                        "documentform",
                        "datacsv",
                        "errorlogdocument",
                        "multimediadownloads",
                        "uploaddata",
                        "dataxlsx",
                        "observationcards",
                        "climmobexplanationkit",
                    ]:
                        assessId = product["process_name"].split("_")[3]
                        if product["product_id"] == "dataxlsx":
                            assessId = product["process_name"].split("_")[4]

                        product["extraInformation"] = getProjectAssessmentInfo(
                            activeProjectData["project_id"],
                            assessId,
                            self.request,
                        )

                    productsAvailable.append(product)

            if activeProjectData["project_active"] == 1:
                hasActiveProject = True

            assessments = getProjectAssessments(
                activeProjectData["project_id"], self.request
            )

        return {
            "activeUser": self.user,
            "activeProject": activeProjectData,
            "hasActiveProject": hasActiveProject,
            "Products": productsAvailable,
            "assessments": assessments,
            "sectionActive": "productlist",
        }


class generateProductView(privateView):
    def processView(self):
        projectCod = self.request.matchdict["project"]
        productid = self.request.matchdict["productid"]
        processname = self.request.matchdict["processname"]

        activeProjectData = getActiveProject(self.user.login, self.request)

        if not activeProjectData:
            raise HTTPNotFound()

        listOfLabels = [
            activeProjectData["project_label_a"],
            activeProjectData["project_label_b"],
            activeProjectData["project_label_c"],
        ]

        if productid == "qrpackage":

            ncombs, packages = getPackages(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                self.request,
            )
            create_qr_packages(
                self.request,
                self.request.locale_name,
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                activeProjectData["project_cod"],
                ncombs,
                packages,
            )

        if productid == "qrpackageseditable":
            ncombs, packages = getPackages(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                self.request,
            )

            for plugin in p.PluginImplementations(p.IQRPackagesEditable):
                plugin.create_qr_packages_editable(
                    self.request,
                    self.request.locale_name,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    ncombs,
                    packages,
                )

        if productid == "qrpackagewithtechnologies":

            ncombs, packages = getPackages(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                self.request,
            )

            for plugin in p.PluginImplementations(p.IpackagesWithTechnologiesExtension):
                plugin.create_qr_packages_with_technologies(
                    self.request,
                    self.request.locale_name,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    ncombs,
                    packages,
                )

        if productid == "packages":
            ncombs, packages = getPackages(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                self.request,
            )
            create_packages_excell(
                self.request,
                self.request.locale_name,
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                activeProjectData["project_cod"],
                packages,
                getTech(activeProjectData["project_id"], self.request),
                listOfLabels,
            )

        if productid == "fieldagents":
            locale = self.request.locale_name
            create_fieldagents_report(
                locale,
                self.request,
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_cod"],
                activeProjectData["project_id"],
                getProjectEnumerators(activeProjectData["project_id"], self.request),
                activeProjectData,
            )

        if productid == "colors":
            ncombs, packages = getPackages(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                self.request,
            )
            numberOfCombinations = numberOfCombinationsForTheProject(
                activeProjectData["project_id"], self.request
            )

            if numberOfCombinations == 3:
                tech = searchTechnologiesInProject(
                    activeProjectData["project_id"], self.request
                )
                if len(tech) == 1:
                    if tech[0]["tech_id"] == 76 or tech[0]["tech_id"] == 78:
                        create_colors_cards(
                            self.request,
                            activeProjectData["owner"]["user_name"],
                            activeProjectData["project_id"],
                            activeProjectData["project_cod"],
                            packages,
                            listOfLabels,
                        )

        if productid == "datacsv":
            locale = self.request.locale_name
            infoProduct = processname.split("_")
            if infoProduct[2] == "Registration":
                info = getJSONResult(
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    self.request,
                    includeAssessment=False,
                )
            else:
                if infoProduct[2] == "Assessment":
                    info = getJSONResult(
                        activeProjectData["owner"]["user_name"],
                        activeProjectData["project_id"],
                        activeProjectData["project_cod"],
                        self.request,
                        assessmentCode=infoProduct[3],
                    )
                else:
                    info = getJSONResult(
                        activeProjectData["owner"]["user_name"],
                        activeProjectData["project_id"],
                        activeProjectData["project_cod"],
                        self.request,
                    )

            create_datacsv(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                activeProjectData["project_cod"],
                info,
                self.request,
                infoProduct[2],
                infoProduct[3],
            )

        if productid == "dataxlsx":
            infoProduct = processname.split("_")
            create_XLSXToDownload(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                activeProjectData["project_cod"],
                self.request,
                infoProduct[3],
                infoProduct[4],
            )

        if productid == "documentform":
            ncombs, packages = getPackages(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                self.request,
            )
            if processname == "create_from_Registration_":
                data, finalCloseQst = getDataFormPreview(
                    self,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                )
                create_document_form(
                    self.request,
                    self.request.locale_name,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    "Registration",
                    "",
                    data,
                    packages,
                    listOfLabels,
                )
            else:
                assessment_id = processname.split("_")[3]
                data, finalCloseQst = getDataFormPreview(
                    self,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    assessment_id,
                )
                create_document_form(
                    self.request,
                    self.request.locale_name,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    "Assessment",
                    assessment_id,
                    data,
                    packages,
                    listOfLabels,
                )

        if productid == "errorlogdocument":
            if processname == "create_errorlog_Registration_":
                data = generateStructureForInterfaceForms(
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    "registry",
                    self.request,
                )
                _errors = get_registry_logs(
                    self.request, activeProjectData["project_id"]
                )
                info = getJSONResult(
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    self.request,
                    includeRegistry=True,
                    includeAssessment=False,
                    assessmentCode="",
                )
                create_error_log_document(
                    self.request,
                    self.request.locale_name,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    "Registration",
                    "",
                    data,
                    _errors,
                    info,
                )
            else:
                assessment_id = processname.split("_")[3]
                data = generateStructureForInterfaceForms(
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    "assessment",
                    self.request,
                    ass_cod=assessment_id,
                )
                _errors = get_assessment_logs(
                    self.request, activeProjectData["project_id"], assessment_id
                )
                info = getJSONResult(
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    self.request,
                    includeRegistry=False,
                    includeAssessment=True,
                    assessmentCode=assessment_id,
                )
                create_error_log_document(
                    self.request,
                    self.request.locale_name,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    "Assessment",
                    assessment_id,
                    data,
                    _errors,
                    info,
                )

        if productid == "generalreport":
            dataworking = {}
            dataworking["project_username"] = activeProjectData["owner"]["user_name"]
            dataworking["project_cod"] = projectCod
            dataworking["project_id"] = activeProjectData["project_id"]
            dataworking["project_details"] = getProjectData(
                activeProjectData["project_id"], self.request
            )
            dataworking = getImportantInformation(dataworking, self.request)
            dataworking["project_fieldagents"] = getProjectEnumerators(
                activeProjectData["project_id"], self.request
            )
            dataRegistry, finalCloseQst = getDataFormPreview(
                self,
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                createAutoRegistry=False,
            )
            dataworking["project_registry"] = dataRegistry
            dataAssessments = getProjectAssessments(
                activeProjectData["project_id"], self.request
            )
            for assessment in dataAssessments:
                dataAssessmentsQuestions, finalCloseQst = getDataFormPreview(
                    self,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    assessment["ass_cod"],
                )
                assessment["Questions"] = dataAssessmentsQuestions
            dataworking["project_assessment"] = dataAssessments
            create_general_report(
                self.request,
                self.request.locale_name,
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                projectCod,
                dataworking,
            )

        if productid == "datacollectionprogress":
            geoInformation = getInformationForMaps(
                self.request,
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                projectCod,
            )
            for plugin in p.PluginImplementations(p.IDataColletionProgress):
                plugin.create_data_collection_progress(
                    self.request,
                    self.request.locale_name,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    getInformationFromProject(
                        self.request,
                        activeProjectData["owner"]["user_name"],
                        activeProjectData["project_id"],
                        activeProjectData["project_cod"],
                    ),
                    geoInformation,
                )

        if productid == "multimediadownloads":
            for plugin in p.PluginImplementations(p.IMultimedia):
                if processname == "create_multimedia_Registration_":
                    plugin.start_multimedia_download(
                        self.request,
                        activeProjectData["owner"]["user_name"],
                        activeProjectData["project_id"],
                        activeProjectData["project_cod"],
                        "Registration",
                        "",
                    )
                else:
                    assessment_id = processname.split("_")[3]
                    plugin.start_multimedia_download(
                        self.request,
                        activeProjectData["owner"]["user_name"],
                        activeProjectData["project_id"],
                        activeProjectData["project_cod"],
                        "Assessment",
                        assessment_id,
                    )

        if productid == "uploaddata":
            for plugin in p.PluginImplementations(p.IUpload):
                if processname == "create_uploaddata_Registration_":
                    plugin.create_Excel_template_for_upload_data(
                        self.request,
                        activeProjectData["owner"]["user_name"],
                        activeProjectData["project_id"],
                        activeProjectData["project_cod"],
                        "registry",
                    )
                else:
                    assessment_id = processname.split("_")[3]
                    plugin.create_Excel_template_for_upload_data(
                        self.request,
                        activeProjectData["owner"]["user_name"],
                        activeProjectData["project_id"],
                        activeProjectData["project_cod"],
                        "assessment",
                        assessment_id,
                    )

        if productid == "observationcards":
            locale = self.request.locale_name
            assessment_id = processname.split("_")[3]
            for plugin in p.PluginImplementations(p.IObservationCards):
                plugin.create_observation_cards(
                    self.request,
                    locale,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    assessment_id,
                    [],
                )

        if productid == "climmobexplanationkit":
            locale = self.request.locale_name
            assessment_id = processname.split("_")[3]

            ncombs, packages = getPackages(
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                self.request,
            )

            data, finalCloseQst = getDataFormPreview(
                self,
                activeProjectData["owner"]["user_name"],
                activeProjectData["project_id"],
                assessment_id,
            )

            for plugin in p.PluginImplementations(p.IExplanationKit):
                plugin.create_explanation_kit(
                    self.request,
                    locale,
                    activeProjectData["owner"]["user_name"],
                    activeProjectData["project_id"],
                    activeProjectData["project_cod"],
                    assessment_id,
                    data,
                    packages,
                    listOfLabels,
                )

        self.returnRawViewResult = True
        return HTTPFound(
            location=self.request.route_url(
                "productList", _query={"product1": processname}
            )
        )


class downloadView(climmobPrivateView):
    def processView(self):
        celery_taskid = self.request.matchdict["celery_taskid"]
        product_id = self.request.matchdict["product_id"]
        activeProjectData = getActiveProject(self.user.login, self.request)
        dataworking = getProductData(
            activeProjectData["project_id"],
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
                activeProjectData["owner"]["user_name"],
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
