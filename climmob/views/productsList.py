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
    getJSONResult
)
from .registry import getDataFormPreview

from ..products.qrpackages.qrpackages import create_qr_packages
from ..products.packages.packages import create_packages_excell
from ..products.colors.colors import create_colors_cards
from ..products.fieldagents.fieldagents import create_fieldagents_report
from ..products.analysisdata.analysisdata import create_datacsv
from ..products.forms.form import create_document_form

def getDataProduct(user, project, request):

    sql = (
        "select edited.celery_taskid,edited.user_name,edited.project_cod,edited.product_id, edited.datetime_added, edited.output_id,edited.state, edited.output_mimetype "
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
        "where edited.datetime_added = (SELECT max(datetime_added) FROM products where project_cod = '"+project+"' and user_name='"+user+"' and product_id= edited.product_id) and edited.user_name='"
        + user
        + "' and edited.project_cod='"
        + project
        + "' order by field(edited.product_id,'fieldagents','packages','qrpackage') desc, edited.datetime_added"
    )

    #print(sql)

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
        # for key, value in dct.items():
        #    if isinstance(value, str):
        #        dct[key] = value.decode("utf8")
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

            if activeProjectData["project_active"] == 1:
                hasActiveProject = True
                # u.getJSResource("productsListaes").need()
                # u.getJSResource("productsList").need()
                # u.getJSResource("concurrent").need()
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

        if productid == "qrpackage":

            ncombs, packages = getPackages(self.user.login, projectid, self.request)
            create_qr_packages(self.request, self.user.login, projectid, ncombs, packages)

        if productid == "packages":
            ncombs, packages = getPackages(self.user.login, projectid, self.request)
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
                tech = searchTechnologiesInProject(self.user.login, projectid, self.request)
                if len(tech) == 1:
                    if tech[0]["tech_name"] == "Colores" or tech[0]["tech_name"] == "Colors":
                        create_colors_cards(self.request, self.user.login, projectid, packages)

        if productid == "datacsv":
            locale = self.request.locale_name
            info = getJSONResult(
                self.user.login, projectid, self.request
            )

            create_datacsv(self.user.login, projectid, info, self.request)

        if productid == "documentform":
            #POR AHORA ESTARÍA SOLO FUNCIONANDO CON EL FORMULARIO DE REGISTRO DEBE DE SER EDITADO
            ncombs, packages = getPackages(self.user.login, projectid, self.request)
            data, finalCloseQst = getDataFormPreview(self, projectid)
            create_document_form(self.request, "en", self.user.login, projectid, "Registration", "", data, packages)

        self.returnRawViewResult = True
        return HTTPFound(
            location=self.request.route_url(
                "productList"
            )
        )


class downloadJsonView(climmobPrivateView):
    def processView(self):

        celery_taskid = self.request.matchdict["product_id"]
        activeProjectData = getActiveProject(self.user.login, self.request)
        dataworking = getProductData(
            self.user.login,
            activeProjectData["project_cod"],
            celery_taskid,
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
        celery_taskid = self.request.matchdict["product_id"]
        activeProjectData = getActiveProject(self.user.login, self.request)
        dataworking = getProductData(
            self.user.login,
            activeProjectData["project_cod"],
            celery_taskid,
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

            # response = FileResponse(path+'/outputs/'+filename,request=self.request,content_type=contentType)
            # headers = response.headers
            # headers['Content-Type'] = contentType
            # headers['Accept-Ranges'] = 'bite'
            # headers['Content-Disposition'] = 'attachment;filename=' + os.path.basename(path+'/outputs/'+filename)
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
