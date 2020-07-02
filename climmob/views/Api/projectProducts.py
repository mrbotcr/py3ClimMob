from ...plugins.utilities import getProductDirectory
from ..classes import apiView
from ...processes import projectExists, getProductData
from ..productsList import getDataProduct
from ...products import product_found
from pyramid.response import Response
import json
import datetime
from pyramid.response import FileResponse


class readProducts_view(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "GET":
            obligatory = [u"project_cod"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        products = getDataProduct(
                            self.user.login, dataworking["project_cod"], self.request
                        )

                        # for index in range(0,len(products)):
                        #    if products[index]["state"] == "Success":
                        #        products[index]["Url"] = self.request.route_url('download',product_id=products[index]["celery_taskid"])

                        response = Response(
                            status=200, body=json.dumps(products, default=myconverter)
                        )
                        return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not a project with that code."),
                        )
                        return response
                else:
                    response = Response(
                        status=401, body=self._("Not all parameters have data.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class downloadApi_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [u"project_cod", u"celery_taskid"]
            try:
                dataworking = json.loads(self.request.params["Body"])
            except:
                response = Response(status=401,body=self._("Error in the JSON, It does not have the 'body' parameter."))
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login, dataworking["project_cod"], self.request
                    )
                    if exitsproject:
                        # Here start the code for the download
                        productData = getProductData(
                            self.user.login,
                            dataworking["project_cod"],
                            dataworking["celery_taskid"],
                            self.request,
                        )
                        if productData:
                            product_id = productData["product_id"]

                            if product_found(product_id):
                                contentType = productData["output_mimetype"]
                                filename = productData["output_id"]
                                path = getProductDirectory(
                                    self.request,
                                    self.user.login,
                                    dataworking["project_cod"],
                                    product_id,
                                )
                                response = FileResponse(
                                    path + "/outputs/" + filename,
                                    request=self.request,
                                    content_type=contentType.encode("utf-8"),
                                )
                                response.content_disposition = (
                                    'attachment; filename="' + filename + '"'
                                )

                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is not a product with that celery_taskid."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is not a product with that celery_taskid."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not a project with that code."),
                        )
                        return response
                else:
                    response = Response(
                        status=401, body=self._("Not all parameters have data.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response
