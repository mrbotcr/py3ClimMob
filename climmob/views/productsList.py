from ..plugins.utilities import (
    climmobPublicView,
    climmobPrivateView,
    getProductDirectory,
    getProducts,
)
from ..products import product_found
import climmob.plugins.utilities as u
from ..processes import getActiveProject, getProductData
from pyramid.response import FileResponse
import os
import json


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
        "where edited.datetime_added = (select max(f.datetime_added) from products f where f.output_id = edited.output_id) and edited.user_name='"
        + user
        + "' and edited.project_cod='"
        + project
        + "'"
    )

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
