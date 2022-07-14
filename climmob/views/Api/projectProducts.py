import datetime
import json

from pyramid.response import FileResponse
from pyramid.response import Response

from climmob.plugins.utilities import getProductDirectory
from climmob.processes import projectExists, getProductData, getTheProjectIdForOwner
from climmob.products import product_found
from climmob.views.classes import apiView
from climmob.views.productsList import getDataProduct


class readProducts_view(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "GET":
            obligatory = ["project_cod", "user_owner"]
            try:
                dataworking = json.loads(self.body)
            except:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON, It does not have the 'body' parameter."
                    ),
                )
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )

                        products = getDataProduct(activeProjectId, self.request)

                        response = Response(
                            status=200, body=json.dumps(products, default=myconverter)
                        )
                        return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not project with that code."),
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
            obligatory = [
                "project_cod",
                "user_owner",
                "celery_taskid",
                "product_id",
            ]
            try:
                dataworking = json.loads(self.body)
            except:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON, It does not have the 'body' parameter."
                    ),
                )
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )

                        # Here start the code for the download
                        productData = getProductData(
                            activeProjectId,
                            dataworking["celery_taskid"],
                            dataworking["product_id"],
                            self.request,
                        )

                        if productData:
                            product_id = productData["product_id"]

                            if product_found(product_id):
                                contentType = productData["output_mimetype"]
                                filename = productData["output_id"]
                                path = getProductDirectory(
                                    self.request,
                                    dataworking["user_owner"],
                                    dataworking["project_cod"],
                                    product_id,
                                )
                                response = FileResponse(
                                    path + "/outputs/" + filename,
                                    request=self.request,
                                    content_type=contentType,
                                )
                                response.content_disposition = (
                                    'attachment; filename="' + filename + '"'
                                )

                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no product with that product_id."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is no product with that celery_taskid or product_id."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
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
